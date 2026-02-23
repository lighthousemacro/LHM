#!/usr/bin/env python3
"""
TOKEN TERMINAL x LIGHTHOUSE MACRO - Dashboard
==============================================
Single-page institutional dashboard combining Token Terminal
protocol fundamentals with Lighthouse Macro liquidity overlay.

Output: /Users/bob/LHM/Outputs/token_terminal_deck/
"""

import sys
sys.path.insert(0, '/Users/bob/LHM/Scripts/utilities')

import sqlite3
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.gridspec as gridspec
from matplotlib.patches import FancyBboxPatch, Rectangle
from matplotlib.lines import Line2D
from matplotlib.offsetbox import AnchoredText
from pathlib import Path
from datetime import datetime, timedelta
try:
    from adjustText import adjust_text
    HAS_ADJUST = True
except ImportError:
    HAS_ADJUST = False

from lighthouse_chart_style import (
    LIGHTHOUSE_COLORS as C,
    hex_to_rgba
)

DB = Path('/Users/bob/LHM/Data/databases/Lighthouse_Master.db')
OUT = Path('/Users/bob/LHM/Outputs/token_terminal_deck')
OUT.mkdir(parents=True, exist_ok=True)

conn = sqlite3.connect(DB)

# =========================================================================
# DISTINCT PALETTE - No adjacent teal/cyan confusion
# Ocean, Dusk, Venus, then supplementary distinct colors
# =========================================================================
CHART_PALETTE = [
    C['ocean_blue'],     # #2389BB
    C['dusk_orange'],    # #FF6723
    C['hot_magenta'],    # #FF2389 (Venus)
    '#8B5CF6',           # Purple
    C['electric_cyan'],  # #00FFFF
    '#F59E0B',           # Amber
]

# Bar chart palette: must be visually distinct even adjacent
BAR_TRIO = [C['ocean_blue'], C['dusk_orange'], C['hot_magenta']]


def style_spines(ax):
    """Clean thin spines on all 4 sides."""
    for spine in ax.spines.values():
        spine.set_linewidth(0.5)
        spine.set_color('#999')
    ax.grid(False)


def panel_title(ax, title, subtitle=None):
    """Set panel title with subtitle below, no overlap."""
    ax.set_title(title, fontsize=13, fontweight='bold', pad=18 if subtitle else 10)
    if subtitle:
        ax.text(0.5, 1.02, subtitle, transform=ax.transAxes,
                fontsize=8, ha='center', color='#888', style='italic')


def fig_branding(fig, header_line2):
    """Add LHM branding to figure."""
    fig.text(0.03, 0.975, 'LIGHTHOUSE MACRO', fontsize=14,
             color=C['ocean_blue'], fontweight='bold')
    fig.text(0.03, 0.96, f'{header_line2} | {datetime.now().strftime("%B %d, %Y")}',
             fontsize=10, color='#666', style='italic')
    fig.text(0.97, 0.008, 'MACRO, ILLUMINATED.', fontsize=8,
             color=C['hot_magenta'], ha='right', style='italic')
    # Accent bar
    bar = fig.add_axes([0.03, 0.945, 0.94, 0.004])
    bar.axhspan(0, 1, 0, 0.67, color=C['ocean_blue'])
    bar.axhspan(0, 1, 0.67, 1.0, color=C['dusk_orange'])
    bar.set_xlim(0, 1)
    bar.set_ylim(0, 1)
    bar.axis('off')


# =========================================================================
# DATA HELPERS
# =========================================================================

def get_scores():
    """Get latest protocol scores with proper names."""
    df = pd.read_sql("""
        SELECT cs.*, cm.name as meta_name
        FROM crypto_scores cs
        LEFT JOIN crypto_meta cm ON cs.project_id = cm.project_id
        WHERE cs.date = (SELECT MAX(date) FROM crypto_scores)
        ORDER BY cs.overall_score DESC
    """, conn)
    df['display_name'] = df['name'].fillna(df['meta_name']).fillna(df['project_id'])
    return df


def get_metric_ts(metric_id, project_ids=None, days=180):
    """Get time series for a metric."""
    cutoff = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    q = "SELECT project_id, date, value FROM crypto_metrics WHERE metric_id=? AND date>=?"
    params = [metric_id, cutoff]
    if project_ids:
        placeholders = ','.join(['?'] * len(project_ids))
        q += f" AND project_id IN ({placeholders})"
        params.extend(project_ids)
    q += " ORDER BY date"
    return pd.read_sql(q, conn, params=params)


def get_macro_ts(series_id, days=730):
    """Get macro time series from observations."""
    cutoff = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    df = pd.read_sql(
        "SELECT date, value FROM observations WHERE series_id=? AND date>=? ORDER BY date",
        conn, params=[series_id, cutoff]
    )
    df['date'] = pd.to_datetime(df['date'])
    return df


def get_names():
    """Get display names for all protocols."""
    scores = get_scores()
    return dict(zip(scores['project_id'], scores['display_name']))


# =========================================================================
# DASHBOARD 1: Protocol Fundamentals
# =========================================================================

def dashboard_protocol_fundamentals():
    scores = get_scores()
    names = get_names()

    fig = plt.figure(figsize=(22, 28), facecolor='white')
    gs = gridspec.GridSpec(3, 2, hspace=0.38, wspace=0.28,
                           left=0.07, right=0.95, top=0.93, bottom=0.03)

    # ------------------------------------------------------------------
    # PANEL 1: Scoring Matrix (top-left)
    # ------------------------------------------------------------------
    ax1 = fig.add_subplot(gs[0, 0])
    df = scores[scores['overall_score'] > 0].head(15).copy()

    protocols = df['display_name'].tolist()
    fin = df['financial_score'].fillna(0).tolist()
    use = df['usage_score'].fillna(0).tolist()
    val = df['valuation_score'].fillna(0).tolist()
    total = df['overall_score'].fillna(0).tolist()

    y = np.arange(len(protocols))
    bh = 0.25

    # Ocean, Dusk, Venus - all distinct
    ax1.barh(y + bh, fin, bh, label='Financial', color=C['ocean_blue'], alpha=0.9)
    ax1.barh(y, use, bh, label='Usage', color=C['dusk_orange'], alpha=0.9)
    ax1.barh(y - bh, val, bh, label='Valuation', color=C['hot_magenta'], alpha=0.9)

    for i, t in enumerate(total):
        ax1.text(max(fin[i], use[i], val[i]) + 2, y[i], f'{t:.0f}',
                 va='center', fontsize=9, fontweight='bold', color='#222')

    # Tier color dots
    for i, row in enumerate(df.itertuples()):
        v = str(row.verdict) if row.verdict else ''
        if 'TIER 1' in v:
            c = '#00AA00'
        elif 'TIER 2' in v:
            c = C['ocean_blue']
        elif 'NEUTRAL' in v:
            c = '#999999'
        else:
            c = C['pure_red']
        ax1.plot(-2, y[i], 'o', color=c, markersize=7, clip_on=False)

    ax1.set_yticks(y)
    ax1.set_yticklabels(protocols, fontsize=9)
    ax1.invert_yaxis()
    ax1.set_xlim(-4, 108)
    ax1.legend(loc='lower right', fontsize=8, framealpha=0.9)
    panel_title(ax1, 'LHM Protocol Scoring Matrix',
                '24-Point System | Financial + Usage + Valuation')
    style_spines(ax1)

    # ------------------------------------------------------------------
    # PANEL 2: Valuation Map (top-right)
    # ------------------------------------------------------------------
    ax2 = fig.add_subplot(gs[0, 1])
    vdf = scores[(scores['ann_revenue'] > 0) & (scores['pf_ratio'] > 0) & (scores['pf_ratio'] < 10000)].copy()

    colors = []
    for v in vdf['verdict']:
        v = str(v)
        if 'TIER 1' in v:
            colors.append('#00AA00')
        elif 'TIER 2' in v:
            colors.append(C['ocean_blue'])
        elif 'NEUTRAL' in v:
            colors.append('#999999')
        else:
            colors.append(C['pure_red'])

    sizes = np.clip(vdf['fdv'].fillna(1e8) / 1e8, 40, 500)

    ax2.scatter(vdf['ann_revenue'] / 1e6, vdf['pf_ratio'],
                c=colors, s=sizes, alpha=0.7, edgecolors='#333', linewidth=0.5)

    # Labels - annotate with offsets to avoid bubble overlap
    for _, row in vdf.iterrows():
        if row['ann_revenue'] > 2e6 or row['pf_ratio'] < 5 or row['overall_score'] >= 70:
            ax2.annotate(row['display_name'],
                         xy=(row['ann_revenue'] / 1e6, row['pf_ratio']),
                         fontsize=7, color='#333',
                         xytext=(6, 6), textcoords='offset points',
                         bbox=dict(boxstyle='round,pad=0.15', fc='white', ec='none', alpha=0.7))

    ax2.set_xscale('log')
    ax2.set_yscale('log')
    ax2.set_xlabel('Annualized Revenue ($M)', fontsize=10)
    ax2.set_ylabel('P/F Ratio (FDV / Fees)', fontsize=10)
    ax2.axhline(y=10, color=C['dusk_orange'], linestyle='--', alpha=0.3, linewidth=1)
    ax2.axvline(x=10, color=C['dusk_orange'], linestyle='--', alpha=0.3, linewidth=1)

    ax2.text(0.95, 0.03, 'VALUE ZONE', fontsize=9,
             color='#00AA00', alpha=0.5, fontweight='bold',
             ha='right', va='bottom', transform=ax2.transAxes)

    legend_els = [
        Line2D([0], [0], marker='o', color='w', markerfacecolor='#00AA00', markersize=9, label='Tier 1'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor=C['ocean_blue'], markersize=9, label='Tier 2'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='#999999', markersize=9, label='Neutral'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor=C['pure_red'], markersize=9, label='Avoid'),
    ]
    ax2.legend(handles=legend_els, loc='upper left', fontsize=8, framealpha=0.9)
    panel_title(ax2, 'Protocol Valuation Map',
                'Revenue vs P/F | Bubble Size = FDV | Color = LHM Verdict')
    style_spines(ax2)

    # ------------------------------------------------------------------
    # PANEL 3: Revenue Trends (mid-left)
    # ------------------------------------------------------------------
    ax3 = fig.add_subplot(gs[1, 0])
    top6 = scores.head(6)['project_id'].tolist()
    rev_df = get_metric_ts('revenue', top6, days=180)
    rev_df['date'] = pd.to_datetime(rev_df['date'])

    for i, pid in enumerate(top6):
        sub = rev_df[rev_df['project_id'] == pid].copy()
        if sub.empty:
            continue
        sub = sub[['date', 'value']].set_index('date').resample('W').mean().reset_index()
        label = names.get(pid, pid)
        ax3.plot(sub['date'], sub['value'] / 1e6, color=CHART_PALETTE[i],
                 linewidth=2, label=label, alpha=0.9)

    ax3.set_ylabel('Weekly Revenue ($M)', fontsize=10)
    ax3.legend(loc='upper right', fontsize=8, ncol=2, framealpha=0.9)
    ax3.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:.1f}M'))
    panel_title(ax3, 'Revenue Trends (6M)',
                'Token Terminal | Weekly Avg | Top 6 by LHM Score')
    style_spines(ax3)

    # ------------------------------------------------------------------
    # PANEL 4: DAU Trends (mid-right)
    # ------------------------------------------------------------------
    ax4 = fig.add_subplot(gs[1, 1])
    dau_df = get_metric_ts('user_dau', top6, days=180)
    dau_df['date'] = pd.to_datetime(dau_df['date'])

    for i, pid in enumerate(top6):
        sub = dau_df[dau_df['project_id'] == pid].copy()
        if sub.empty:
            continue
        sub = sub[['date', 'value']].set_index('date').resample('W').mean().reset_index()
        label = names.get(pid, pid)
        ax4.plot(sub['date'], sub['value'] / 1e3, color=CHART_PALETTE[i],
                 linewidth=2, label=label, alpha=0.9)

    ax4.set_ylabel('Daily Active Users (K)', fontsize=10)
    ax4.legend(loc='upper right', fontsize=8, ncol=2, framealpha=0.9)
    ax4.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:.0f}K'))
    panel_title(ax4, 'DAU Trends (6M)',
                'Token Terminal | Weekly Avg | Top 6 by LHM Score')
    style_spines(ax4)

    # ------------------------------------------------------------------
    # PANEL 5: Sector Health (bottom-left)
    # ------------------------------------------------------------------
    ax5 = fig.add_subplot(gs[2, 0])
    sectors = scores.groupby('sector').agg({
        'overall_score': 'mean',
        'financial_score': 'mean',
        'usage_score': 'mean',
        'valuation_score': 'mean',
        'ann_revenue': 'sum',
        'project_id': 'count'
    }).rename(columns={'project_id': 'count'}).sort_values('overall_score', ascending=True)

    sy = np.arange(len(sectors))
    # Use distinct colors: green, ocean, dusk, red - no teal/cyan
    scolors = ['#00AA00' if s >= 70 else C['ocean_blue'] if s >= 55
               else C['dusk_orange'] if s >= 40 else C['pure_red']
               for s in sectors['overall_score']]

    ax5.barh(sy, sectors['overall_score'], color=scolors, alpha=0.85,
             edgecolor='#444', linewidth=0.5)

    for i, (score, count, rev) in enumerate(zip(
            sectors['overall_score'], sectors['count'], sectors['ann_revenue'])):
        ax5.text(score + 1.5, sy[i], f'{score:.0f}  ({count}p, ${rev/1e6:.0f}M)',
                 va='center', fontsize=8, color='#333')

    ax5.set_yticks(sy)
    ax5.set_yticklabels([s.replace('_', ' ').title() if s else 'Other'
                         for s in sectors.index], fontsize=9)
    ax5.set_xlim(0, 105)
    ax5.axvline(55, color=C['dusk_orange'], linestyle='--', alpha=0.25, linewidth=1)
    ax5.axvline(70, color='#00AA00', linestyle='--', alpha=0.25, linewidth=1)
    panel_title(ax5, 'Sector Health',
                'Avg LHM Score | (protocols, ann. revenue)')
    style_spines(ax5)

    # ------------------------------------------------------------------
    # PANEL 6: Key Stats Table (bottom-right)
    # ------------------------------------------------------------------
    ax6 = fig.add_subplot(gs[2, 1])
    ax6.axis('off')

    tier1 = scores[scores['verdict'].str.contains('TIER 1', na=False)]
    tier2 = scores[scores['verdict'].str.contains('TIER 2', na=False)]
    avoid = scores[scores['verdict'].str.contains('AVOID', na=False)]

    total_rev = scores['ann_revenue'].sum()
    total_fees = scores['ann_fees'].sum()
    avg_pf = scores.loc[scores['pf_ratio'] > 0, 'pf_ratio'].median()
    total_dau = scores['dau'].sum()
    total_tvl = scores['tvl'].sum()

    rrp_val = get_macro_ts('RRPONTSYD', 7)
    rrp_latest = f"${rrp_val['value'].iloc[-1]:.1f}B" if not rrp_val.empty else "N/A"
    nfci_val = get_macro_ts('NFCI', 7)
    nfci_latest = f"{nfci_val['value'].iloc[-1]:.2f}" if not nfci_val.empty else "N/A"
    hy_val = get_macro_ts('BAMLH0A0HYM2', 7)
    hy_latest = f"{hy_val['value'].iloc[-1]*100:.0f}bps" if not hy_val.empty else "N/A"
    vix_val = get_macro_ts('VIXCLS', 7)
    vix_latest = f"{vix_val['value'].iloc[-1]:.1f}" if not vix_val.empty else "N/A"

    stats_data = [
        ('header', 'PROTOCOL UNIVERSE'),
        ('row', 'Protocols Covered', f'{len(scores)}'),
        ('row', 'Tier 1 (Accumulate)', f'{len(tier1)}'),
        ('row', 'Tier 2 (Hold)', f'{len(tier2)}'),
        ('row', 'Avoid / Caution', f'{len(avoid)}'),
        ('spacer', None),
        ('header', 'AGGREGATE FUNDAMENTALS'),
        ('row', 'Total Ann. Revenue', f'${total_rev/1e6:.0f}M'),
        ('row', 'Total Ann. Fees', f'${total_fees/1e6:.0f}M'),
        ('row', 'Median P/F Ratio', f'{avg_pf:.1f}x'),
        ('row', 'Total DAU', f'{total_dau/1e3:.0f}K'),
        ('row', 'Total TVL', f'${total_tvl/1e9:.1f}B'),
        ('spacer', None),
        ('header', 'MACRO CONTEXT'),
        ('row', 'Reverse Repo (RRP)', rrp_latest),
        ('row', 'NFCI', nfci_latest),
        ('row', 'HY OAS (Credit)', hy_latest),
        ('row', 'VIX', vix_latest),
    ]

    y_pos = 0.92
    for item in stats_data:
        if item[0] == 'header':
            ax6.text(0.05, y_pos, item[1], transform=ax6.transAxes,
                     fontsize=11, fontweight='bold', color=C['ocean_blue'])
            y_pos -= 0.008
            ax6.plot([0.05, 0.95], [y_pos, y_pos], color=C['ocean_blue'],
                     linewidth=0.8, alpha=0.4, transform=ax6.transAxes, clip_on=False)
        elif item[0] == 'spacer':
            pass
        else:
            ax6.text(0.08, y_pos, item[1], transform=ax6.transAxes,
                     fontsize=10, color='#333')
            ax6.text(0.92, y_pos, item[2], transform=ax6.transAxes,
                     fontsize=10, fontweight='bold', color='#111', ha='right')
        y_pos -= 0.048

    panel_title(ax6, 'Dashboard Summary')

    # ------------------------------------------------------------------
    # FIGURE BRANDING
    # ------------------------------------------------------------------
    fig_branding(fig, 'Token Terminal Integration')

    fig.savefig(OUT / 'dashboard_protocol_fundamentals.png', dpi=150,
                bbox_inches='tight', facecolor='white', edgecolor=C['ocean_blue'])
    plt.close()
    print('  [1] Protocol fundamentals dashboard')


# =========================================================================
# DASHBOARD 2: Macro Liquidity + Crypto Overlay
# =========================================================================

def dashboard_macro_overlay():
    fig = plt.figure(figsize=(22, 28), facecolor='white')
    gs = gridspec.GridSpec(3, 2, hspace=0.38, wspace=0.28,
                           left=0.07, right=0.95, top=0.93, bottom=0.03)

    # ------------------------------------------------------------------
    # PANEL 1: RRP
    # ------------------------------------------------------------------
    ax1 = fig.add_subplot(gs[0, 0])
    rrp = get_macro_ts('RRPONTSYD', 730)
    if not rrp.empty:
        ax1.fill_between(rrp['date'], rrp['value'], alpha=0.25, color=C['ocean_blue'])
        ax1.plot(rrp['date'], rrp['value'], color=C['ocean_blue'], linewidth=1.5)
        ax1.axhline(200, color=C['pure_red'], linestyle='--', alpha=0.4, linewidth=1)
        # Latest value - positioned clearly
        latest = rrp.iloc[-1]
        ax1.annotate(f'${latest["value"]:.1f}B',
                     xy=(latest['date'], latest['value']),
                     fontsize=11, fontweight='bold', color=C['ocean_blue'],
                     xytext=(-80, 40), textcoords='offset points',
                     arrowprops=dict(arrowstyle='->', color=C['ocean_blue'], lw=1.5),
                     bbox=dict(boxstyle='round,pad=0.3', fc='white', ec=C['ocean_blue'], alpha=0.9))
        # Threshold label in clear area
        ax1.text(0.03, 0.08, 'Buffer Exhausted (<$200B)',
                 fontsize=9, color=C['pure_red'], transform=ax1.transAxes, alpha=0.7)
    ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:,.0f}B'))
    panel_title(ax1, 'Reverse Repo Facility ($B)', 'Fed Liquidity Buffer | Effectively Zero')
    style_spines(ax1)

    # ------------------------------------------------------------------
    # PANEL 2: NFCI
    # ------------------------------------------------------------------
    ax2 = fig.add_subplot(gs[0, 1])
    nfci = get_macro_ts('NFCI', 730)
    if not nfci.empty:
        pos_mask = nfci['value'] >= 0
        neg_mask = nfci['value'] < 0
        ax2.fill_between(nfci['date'], nfci['value'], where=pos_mask,
                         alpha=0.25, color=C['pure_red'])
        ax2.fill_between(nfci['date'], nfci['value'], where=neg_mask,
                         alpha=0.25, color='#00AA00')
        ax2.plot(nfci['date'], nfci['value'], color=C['ocean_blue'], linewidth=1.5)
        ax2.axhline(0, color='#333', linewidth=0.8)
        latest = nfci.iloc[-1]
        ax2.annotate(f'{latest["value"]:.2f}',
                     xy=(latest['date'], latest['value']),
                     fontsize=11, fontweight='bold', color=C['ocean_blue'],
                     xytext=(-80, -40), textcoords='offset points',
                     arrowprops=dict(arrowstyle='->', color=C['ocean_blue'], lw=1.5),
                     bbox=dict(boxstyle='round,pad=0.3', fc='white', ec=C['ocean_blue'], alpha=0.9))
    panel_title(ax2, 'Financial Conditions (NFCI)', 'Negative = Loose | Positive = Tight')
    style_spines(ax2)

    # ------------------------------------------------------------------
    # PANEL 3: HY OAS
    # ------------------------------------------------------------------
    ax3 = fig.add_subplot(gs[1, 0])
    hy = get_macro_ts('BAMLH0A0HYM2', 730)
    if not hy.empty:
        ax3.fill_between(hy['date'], hy['value'] * 100, alpha=0.2, color=C['dusk_orange'])
        ax3.plot(hy['date'], hy['value'] * 100, color=C['dusk_orange'], linewidth=1.5)
        ax3.axhline(300, color=C['pure_red'], linestyle='--', alpha=0.4, linewidth=1)
        ax3.text(0.03, 0.92, 'Complacency (<300bps)',
                 fontsize=9, color=C['pure_red'], transform=ax3.transAxes, alpha=0.7)
        latest = hy.iloc[-1]
        ax3.annotate(f'{latest["value"]*100:.0f}bps',
                     xy=(latest['date'], latest['value'] * 100),
                     fontsize=11, fontweight='bold', color=C['dusk_orange'],
                     xytext=(-80, 30), textcoords='offset points',
                     arrowprops=dict(arrowstyle='->', color=C['dusk_orange'], lw=1.5),
                     bbox=dict(boxstyle='round,pad=0.3', fc='white', ec=C['dusk_orange'], alpha=0.9))
    ax3.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:.0f}'))
    ax3.set_ylabel('Spread (bps)', fontsize=10)
    panel_title(ax3, 'HY Credit Spreads (OAS)', 'Risk Appetite Proxy | Tight = Complacent')
    style_spines(ax3)

    # ------------------------------------------------------------------
    # PANEL 4: VIX
    # ------------------------------------------------------------------
    ax4 = fig.add_subplot(gs[1, 1])
    vix = get_macro_ts('VIXCLS', 730)
    if not vix.empty:
        ax4.fill_between(vix['date'], vix['value'], alpha=0.2, color=C['hot_magenta'])
        ax4.plot(vix['date'], vix['value'], color=C['hot_magenta'], linewidth=1.5)
        ax4.axhline(20, color=C['dusk_orange'], linestyle='--', alpha=0.4, linewidth=1)
        ax4.axhline(30, color=C['pure_red'], linestyle='--', alpha=0.4, linewidth=1)
        latest = vix.iloc[-1]
        ax4.annotate(f'{latest["value"]:.1f}',
                     xy=(latest['date'], latest['value']),
                     fontsize=11, fontweight='bold', color=C['hot_magenta'],
                     xytext=(-80, 30), textcoords='offset points',
                     arrowprops=dict(arrowstyle='->', color=C['hot_magenta'], lw=1.5),
                     bbox=dict(boxstyle='round,pad=0.3', fc='white', ec=C['hot_magenta'], alpha=0.9))
    panel_title(ax4, 'VIX (Implied Volatility)', 'Fear Gauge | >20 Caution | >30 Stress')
    style_spines(ax4)

    # ------------------------------------------------------------------
    # PANEL 5: Yield Curve
    # ------------------------------------------------------------------
    ax5 = fig.add_subplot(gs[2, 0])
    t10y2y = get_macro_ts('T10Y2Y', 730)
    t10y3m = get_macro_ts('T10Y3M', 730)

    if not t10y2y.empty:
        ax5.fill_between(t10y2y['date'], t10y2y['value'],
                         where=t10y2y['value'] < 0, alpha=0.2, color=C['pure_red'])
        ax5.fill_between(t10y2y['date'], t10y2y['value'],
                         where=t10y2y['value'] >= 0, alpha=0.12, color='#00AA00')
        ax5.plot(t10y2y['date'], t10y2y['value'], color=C['ocean_blue'],
                 linewidth=1.8, label='10Y-2Y')
    if not t10y3m.empty:
        ax5.plot(t10y3m['date'], t10y3m['value'], color=C['dusk_orange'],
                 linewidth=1.8, label='10Y-3M')
    ax5.axhline(0, color='#333', linewidth=0.8)
    ax5.legend(loc='lower right', fontsize=9, framealpha=0.9)
    ax5.set_ylabel('Spread (%)', fontsize=10)
    panel_title(ax5, 'Yield Curve', 'Inversion = Recession Signal | Steepening = Normalization')
    style_spines(ax5)

    # ------------------------------------------------------------------
    # PANEL 6: Crypto Revenue vs RRP Overlay
    # ------------------------------------------------------------------
    ax6 = fig.add_subplot(gs[2, 1])

    all_rev = get_metric_ts('revenue', days=365)
    if not all_rev.empty:
        all_rev['date'] = pd.to_datetime(all_rev['date'])
        agg_rev = all_rev.groupby('date')['value'].sum().reset_index()
        agg_rev = agg_rev.set_index('date').resample('W').mean().reset_index()

        # Dusk orange bars (not teal)
        ax6.bar(agg_rev['date'], agg_rev['value'] / 1e6, width=5,
                color=C['dusk_orange'], alpha=0.55, label='Protocol Revenue ($M/wk)')
        ax6.set_ylabel('Weekly Revenue ($M)', fontsize=10, color=C['dusk_orange'])
        ax6.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:.0f}M'))

        # RRP overlay on right axis - ocean blue line
        ax6r = ax6.twinx()
        rrp_1y = get_macro_ts('RRPONTSYD', 365)
        if not rrp_1y.empty:
            ax6r.plot(rrp_1y['date'], rrp_1y['value'], color=C['ocean_blue'],
                      linewidth=2.5, label='RRP ($B)', alpha=0.9)
            ax6r.set_ylabel('RRP ($B)', fontsize=10, color=C['ocean_blue'])
            ax6r.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:.0f}B'))
            ax6r.spines['right'].set_color(C['ocean_blue'])
            ax6r.spines['right'].set_linewidth(1.2)

        # Combined legend
        lines1, labels1 = ax6.get_legend_handles_labels()
        lines2, labels2 = ax6r.get_legend_handles_labels() if not rrp_1y.empty else ([], [])
        ax6.legend(lines1 + lines2, labels1 + labels2,
                   loc='upper right', fontsize=8, framealpha=0.9)

    panel_title(ax6, 'Crypto Revenue vs Liquidity',
                'Protocol Rev (bars) vs Fed RRP (line) | 1Y')
    style_spines(ax6)

    # ------------------------------------------------------------------
    # FIGURE BRANDING
    # ------------------------------------------------------------------
    fig_branding(fig, 'Macro Liquidity Context')

    fig.savefig(OUT / 'dashboard_macro_liquidity.png', dpi=150,
                bbox_inches='tight', facecolor='white', edgecolor=C['ocean_blue'])
    plt.close()
    print('  [2] Macro liquidity dashboard')


# =========================================================================
# RUN ALL
# =========================================================================
if __name__ == '__main__':
    print('LIGHTHOUSE MACRO x TOKEN TERMINAL - Dashboards')
    print('=' * 50)
    print(f'Date: {datetime.now().strftime("%Y-%m-%d %H:%M")}')
    print(f'Output: {OUT}')
    print()

    dashboard_protocol_fundamentals()
    dashboard_macro_overlay()

    conn.close()

    print()
    print(f'Done. 2 dashboards saved to {OUT}/')
    print(f'Open: open {OUT}')
