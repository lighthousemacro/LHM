#!/usr/bin/env python3
"""
TOKEN TERMINAL RESEARCH CHARTS
===============================
~20 standalone Token Terminal charts + ~5 TT x Macro overlay charts.
Lighthouse Macro branded, institutional quality.

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
from pathlib import Path
from datetime import datetime, timedelta

from lighthouse_chart_style import (
    LIGHTHOUSE_COLORS as C,
    hex_to_rgba
)

DB = Path('/Users/bob/LHM/Data/databases/Lighthouse_Master.db')

conn = sqlite3.connect(DB)

# =========================================================================
# THEME SYSTEM
# =========================================================================

THEME = {}  # populated by set_theme()
OUT = None

def set_theme(mode='white'):
    """Configure theme. Call before generating charts."""
    global THEME, OUT
    if mode == 'dark':
        THEME = {
            'bg': '#0A1628',
            'fg': '#e6edf3',
            'muted': '#8b949e',
            'spine': '#2a4060',
            'brand_color': '#00BBFF',
            'brand2_color': C['dusk_orange'],
            'primary': '#00BBFF',
            'subtitle': '#7a8a9e',
            'text_strong': '#e6edf3',
            'text_label': '#c0cad8',
            'bar_edge': '#3a5575',
            'zero_line': '#4a6080',
            'legend_bg': '#1e3350',
            'legend_fg': '#e6edf3',
            'fill_alpha': 0.25,
            'table_header_bg': '#0d1f3c',
            'table_row_green': '#1a3328',
            'table_row_blue': '#1a2a40',
            'table_row_yellow': '#2a2a1a',
            'table_row_red': '#2a1a1a',
            'table_row_white': '#1B2A49',
            'table_verdict_green': '#1a3328',
            'table_verdict_blue': '#1a2a40',
            'table_verdict_gray': '#222e3e',
            'table_verdict_red': '#2a1a1a',
            'mode': 'dark',
        }
        OUT = Path('/Users/bob/LHM/Outputs/token_terminal_deck/dark')
    else:
        THEME = {
            'bg': '#ffffff',
            'fg': '#1a1a1a',
            'muted': '#555555',
            'spine': '#999999',
            'brand_color': C['ocean_blue'],
            'brand2_color': C['dusk_orange'],
            'primary': C['ocean_blue'],
            'subtitle': '#888888',
            'text_strong': '#333333',
            'text_label': '#333333',
            'bar_edge': '#333333',
            'zero_line': '#D1D1D1',
            'legend_bg': '#ffffff',
            'legend_fg': '#1a1a1a',
            'fill_alpha': 0.15,
            'table_header_bg': C['ocean_blue'],
            'table_row_green': '#E8F5E9',
            'table_row_blue': '#E3F2FD',
            'table_row_yellow': '#FFF8E1',
            'table_row_red': '#FFEBEE',
            'table_row_white': 'white',
            'table_verdict_green': '#E8F5E9',
            'table_verdict_blue': '#E3F2FD',
            'table_verdict_gray': '#F5F5F5',
            'table_verdict_red': '#FFEBEE',
            'mode': 'white',
        }
        OUT = Path('/Users/bob/LHM/Outputs/token_terminal_deck')
    OUT.mkdir(parents=True, exist_ok=True)

# Default to white
set_theme('white')

# =========================================================================
# PALETTE & HELPERS
# =========================================================================

PALETTE_WHITE = [C['ocean_blue'], C['dusk_orange'], C['hot_magenta'],
                 '#8B5CF6', '#00D4FF', '#F59E0B',
                 '#10B981', '#EF4444', '#6366F1', C['teal_green']]

PALETTE_DARK = ['#00BBFF', '#FF6723', '#FF2389', '#A78BFA',
                '#FBBF24', '#34D399', '#00BB89', '#F87171',
                '#818CF8', '#FB923C']

def get_palette():
    return PALETTE_DARK if THEME['mode'] == 'dark' else PALETTE_WHITE

# Semantic colors: use bright variants on dark backgrounds
def clr(name):
    """Get theme-appropriate semantic color."""
    dark_map = {
        'green': '#34D399',
        'blue': '#00BBFF',
        'orange': '#FF6723',
        'red': '#FF4455',
        'cyan': '#00BBFF',
        'magenta': '#FF2389',
        'teal': '#34D399',
    }
    white_map = {
        'green': C['teal_green'],
        'blue': C['ocean_blue'],
        'orange': C['dusk_orange'],
        'red': C['pure_red'],
        'cyan': '#00BBFF',
        'magenta': C['dusk_orange'],
        'teal': C['teal_green'],
    }
    m = dark_map if THEME['mode'] == 'dark' else white_map
    return m.get(name, THEME['fg'])

SECTOR_COLORS_WHITE = {
    'DeFi - DEX': C['ocean_blue'],
    'DeFi - Lending': C['teal_green'],
    'DeFi - Derivatives': C['hot_magenta'],
    'Layer 1 (Settlement)': C['dusk_orange'],
    'Layer 2 (Scaling)': C['electric_cyan'],
    'Liquid Staking': '#8B5CF6',
    'Infrastructure': '#F59E0B',
    'Uncategorized': C['neutral_gray'],
}

SECTOR_COLORS_DARK = {
    'DeFi - DEX': '#00BBFF',
    'DeFi - Lending': '#00DDAA',
    'DeFi - Derivatives': '#FF2389',
    'Layer 1 (Settlement)': '#FF6723',
    'Layer 2 (Scaling)': '#00BBFF',
    'Liquid Staking': '#A78BFA',
    'Infrastructure': '#FBBF24',
    'Uncategorized': '#6a7a8a',
}

def get_sector_colors():
    return SECTOR_COLORS_DARK if THEME['mode'] == 'dark' else SECTOR_COLORS_WHITE


def brand_ax(ax, title, subtitle=None):
    """Apply LHM branding to a single axis."""
    ax.set_facecolor(THEME['bg'])
    ax.set_title(title, fontsize=13, fontweight='bold', pad=14, loc='left',
                 color=THEME['fg'])
    if subtitle:
        # Place subtitle just below the title, right-aligned
        ax.text(1.0, 1.005, subtitle, transform=ax.transAxes,
                fontsize=8, ha='right', va='bottom', color='#2389BB', style='italic')
    for spine in ax.spines.values():
        spine.set_linewidth(0.5)
        spine.set_color(THEME['spine'])
    ax.tick_params(colors=THEME['fg'], labelsize=9)
    ax.xaxis.label.set_color(THEME['fg'])
    ax.yaxis.label.set_color(THEME['fg'])
    ax.grid(False)


def style_twin_ax(ax2, color):
    """Style a twinx axis: tick colors match series, spines themed."""
    ax2.tick_params(axis='y', colors=color, labelsize=9)
    ax2.yaxis.label.set_color(color)
    ax2.tick_params(axis='x', colors=THEME['fg'], labelsize=9)
    for spine in ax2.spines.values():
        spine.set_linewidth(0.5)
        spine.set_color(THEME['spine'])
    ax2.grid(False)


def add_last_value_label(ax, x_data, y_data, color, fmt='{:.1f}', side='right'):
    """Add bold last-value label on the y-axis in series color."""
    if len(x_data) == 0 or len(y_data) == 0:
        return
    last_y = float(y_data.iloc[-1]) if hasattr(y_data, 'iloc') else float(y_data[-1])
    label = fmt.format(last_y)
    if side == 'right':
        ax.annotate(label, xy=(1.0, last_y), xycoords=('axes fraction', 'data'),
                    fontsize=9, fontweight='bold', color=color,
                    ha='left', va='center',
                    xytext=(6, 0), textcoords='offset points')


def brand_fig(fig, title, subtitle=None, source=None):
    """Apply LHM branding at figure level."""
    fig.patch.set_facecolor(THEME['bg'])

    OCEAN = '#2389BB'
    DUSK = '#FF6723'

    # Top-left watermark — Ocean Blue, bold
    fig.text(0.03, 0.98, 'LIGHTHOUSE MACRO', fontsize=11,
             color=OCEAN, fontweight='bold', va='top')

    # Date top-right
    fig.text(0.97, 0.98, datetime.now().strftime('%B %d, %Y'),
             fontsize=9, color=THEME['subtitle'], ha='right', va='top')

    # Top accent bar — Ocean Blue + Dusk Orange (brand standard)
    bar = fig.add_axes([0.03, 0.955, 0.94, 0.004])
    bar.axhspan(0, 1, 0, 0.67, color=OCEAN)
    bar.axhspan(0, 1, 0.67, 1.0, color=DUSK)
    bar.set_xlim(0, 1); bar.set_ylim(0, 1); bar.axis('off')

    # Bottom accent bar — mirror of top
    bbar = fig.add_axes([0.03, 0.035, 0.94, 0.004])
    bbar.axhspan(0, 1, 0, 0.67, color=OCEAN)
    bbar.axhspan(0, 1, 0.67, 1.0, color=DUSK)
    bbar.set_xlim(0, 1); bbar.set_ylim(0, 1); bbar.axis('off')

    # Bottom-right watermark — below the bottom accent bar, fully visible
    fig.text(0.97, 0.015, 'MACRO, ILLUMINATED.', fontsize=11,
             color=OCEAN, ha='right', va='top', style='italic', fontweight='bold')

    # Source line
    if source:
        date_str = datetime.now().strftime('%m.%d.%Y')
        fig.text(0.03, 0.015, f'Lighthouse Macro | {source}; {date_str}',
                 fontsize=7, color=THEME['muted'], ha='left', va='top', style='italic')

    fig.suptitle(title, fontsize=15, fontweight='bold', y=0.95,
                 color=THEME['fg'])
    if subtitle:
        fig.text(0.5, 0.925, subtitle, fontsize=9, ha='center',
                 color=OCEAN, style='italic')


def save(fig, name):
    """Save chart and close."""
    fig.savefig(OUT / name, dpi=200, bbox_inches='tight', pad_inches=0.15,
                facecolor=THEME['bg'], edgecolor='none')
    plt.close(fig)
    print(f'  Saved: {name}')


# =========================================================================
# DATA LOADERS
# =========================================================================

def get_scores():
    df = pd.read_sql("""
        SELECT cs.*, cm.name as meta_name, cm.sector as meta_sector
        FROM crypto_scores cs
        LEFT JOIN crypto_meta cm ON cs.project_id = cm.project_id
        WHERE cs.date = (SELECT MAX(date) FROM crypto_scores)
        ORDER BY cs.overall_score DESC
    """, conn)
    df['display_name'] = df['name'].fillna(df['meta_name']).fillna(df['project_id'])
    # Use meta_sector for grouping if sector column from scores is messy
    df['sector_clean'] = df['sector'].fillna(df['meta_sector']).fillna('Uncategorized')
    return df


def get_metric_ts(metric_id, project_ids=None, days=180):
    cutoff = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    q = "SELECT project_id, date, value FROM crypto_metrics WHERE metric_id=? AND date>=?"
    params = [metric_id, cutoff]
    if project_ids:
        placeholders = ','.join(['?'] * len(project_ids))
        q += f" AND project_id IN ({placeholders})"
        params.extend(project_ids)
    q += " ORDER BY date"
    df = pd.read_sql(q, conn, params=params)
    df['date'] = pd.to_datetime(df['date'])
    return df


def get_macro_ts(series_id, days=730):
    cutoff = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    df = pd.read_sql(
        "SELECT date, value FROM observations WHERE series_id=? AND date>=? ORDER BY date",
        conn, params=[series_id, cutoff]
    )
    df['date'] = pd.to_datetime(df['date'])
    return df


# =========================================================================
# TOKEN TERMINAL STANDALONE CHARTS (1-20)
# =========================================================================

def chart_01_scoring_matrix():
    """Horizontal bar scoring matrix, top 15 protocols."""
    scores = get_scores()
    df = scores[scores['overall_score'] > 0].head(15)

    fig, ax = plt.subplots(figsize=(10, 8), facecolor=THEME['bg'])

    protocols = df['display_name'].tolist()
    fin = df['financial_score'].fillna(0).values
    use = df['usage_score'].fillna(0).values
    val = df['valuation_score'].fillna(0).values
    total = df['overall_score'].fillna(0).values

    y = np.arange(len(protocols))
    bh = 0.25

    ax.barh(y + bh, fin, bh, label='Financial', color=C['teal_green'] if THEME['mode'] == 'white' else '#00BB89', alpha=0.9)
    ax.barh(y, val, bh, label='Valuation', color=clr('orange'), alpha=0.9)
    ax.barh(y - bh, use, bh, label='Usage', color=clr('blue'), alpha=0.9)

    for i, t in enumerate(total):
        ax.text(max(fin[i], use[i], val[i]) + 2, y[i], f'{t:.0f}',
                va='center', fontsize=9, fontweight='bold', color=THEME['text_strong'])

    # Verdict dots
    for i, row in enumerate(df.itertuples()):
        v = str(row.verdict) if row.verdict else ''
        if 'TIER 1' in v: c = clr('green')
        elif 'TIER 2' in v: c = clr('blue')
        elif 'NEUTRAL' in v: c = C['neutral_gray']
        else: c = clr('red')
        ax.plot(-3, y[i], 'o', color=c, markersize=7, clip_on=False)

    ax.set_yticks(y)
    ax.set_yticklabels(protocols, fontsize=9)
    ax.invert_yaxis()
    ax.set_xlim(-5, 110)
    ax.legend(loc='lower right', fontsize=8, framealpha=0.95, facecolor=THEME['legend_bg'],
                edgecolor=THEME['spine'], labelcolor=THEME['legend_fg'])
    brand_ax(ax, 'LHM Protocol Scoring Matrix', '24-Point System | Financial + Usage + Valuation')
    brand_fig(fig, '', source='Token Terminal, LHM Scoring Engine')
    fig.suptitle('')  # Title on ax instead
    save(fig, '01_scoring_matrix.png')


def chart_02_valuation_map():
    """Revenue vs P/F scatter, bubble = FDV, color = verdict."""
    scores = get_scores()
    vdf = scores[(scores['ann_revenue'] > 0) & (scores['pf_ratio'] > 0) & (scores['pf_ratio'] < 10000)].copy()

    fig, ax = plt.subplots(figsize=(10, 8), facecolor=THEME['bg'])

    colors = []
    for v in vdf['verdict']:
        v = str(v)
        if 'TIER 1' in v: colors.append(clr('green'))
        elif 'TIER 2' in v: colors.append(clr('blue'))
        elif 'NEUTRAL' in v: colors.append(C['neutral_gray'])
        else: colors.append(clr('red'))

    sizes = np.clip(vdf['fdv'].fillna(1e8) / 1e8, 40, 500)
    ax.scatter(vdf['ann_revenue'] / 1e6, vdf['pf_ratio'],
               c=colors, s=sizes, alpha=0.7, edgecolors=THEME['bar_edge'], linewidth=0.5)

    for _, row in vdf.iterrows():
        if row['ann_revenue'] > 3e6 or row['pf_ratio'] < 5 or row['overall_score'] >= 70:
            ax.annotate(row['display_name'], (row['ann_revenue'] / 1e6, row['pf_ratio']),
                        fontsize=7.5, ha='left', va='bottom', color=THEME['text_label'],
                        xytext=(5, 5), textcoords='offset points')

    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel('Annualized Revenue ($M)', fontsize=10)
    ax.set_ylabel('P/F Ratio (FDV / Fees)', fontsize=10)
    ax.axhline(y=10, color=clr('orange'), linestyle='--', alpha=0.3)
    ax.axvline(x=10, color=clr('orange'), linestyle='--', alpha=0.3)
    ax.text(0.95, 0.05, 'VALUE ZONE\nHigh Rev + Low P/F', fontsize=9,
            color=clr('green'), alpha=0.5, fontweight='bold',
            ha='right', va='bottom', transform=ax.transAxes)

    legend_els = [
        Line2D([0], [0], marker='o', color='w', markerfacecolor=clr('green'), markersize=9, label='Tier 1'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor=clr('blue'), markersize=9, label='Tier 2'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor=C['neutral_gray'], markersize=9, label='Neutral'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor=clr('red'), markersize=9, label='Avoid'),
    ]
    ax.legend(handles=legend_els, loc='upper left', fontsize=8, framealpha=0.95, facecolor=THEME['legend_bg'],
                edgecolor=THEME['spine'], labelcolor=THEME['legend_fg'])
    brand_ax(ax, 'Protocol Valuation Map', 'Revenue vs P/F | Bubble = FDV | Color = Verdict')
    brand_fig(fig, '', source='Token Terminal, LHM Analysis')
    fig.suptitle('')
    save(fig, '02_valuation_map.png')


def chart_03_revenue_trends():
    """Revenue time series, top 6 protocols."""
    scores = get_scores()
    names = dict(zip(scores['project_id'], scores['display_name']))
    top6 = scores.head(6)['project_id'].tolist()
    rev_df = get_metric_ts('revenue', top6, days=180)

    fig, ax = plt.subplots(figsize=(10, 6), facecolor=THEME['bg'])
    for i, pid in enumerate(top6):
        sub = rev_df[rev_df['project_id'] == pid].copy()
        if sub.empty: continue
        sub = sub[['date', 'value']].set_index('date').resample('W').mean().reset_index()
        c = get_palette()[i % len(get_palette())]
        ax.plot(sub['date'], sub['value'] / 1e6, color=c,
                linewidth=1.8, label=names.get(pid, pid), alpha=0.85)
        add_last_value_label(ax, sub['date'], sub['value'] / 1e6, c, fmt='${:.1f}M')

    ax.set_ylabel('Weekly Revenue ($M)', fontsize=10)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:.1f}M'))
    ax.legend(loc='upper left', fontsize=8, ncol=2, framealpha=0.95, facecolor=THEME['legend_bg'],
                edgecolor=THEME['spine'], labelcolor=THEME['legend_fg'])
    brand_ax(ax, 'Revenue Trends (6M)', 'Token Terminal | Weekly Avg | Top 6 by LHM Score')
    brand_fig(fig, '', source='Token Terminal')
    fig.suptitle('')
    save(fig, '03_revenue_trends.png')


def chart_04_dau_trends():
    """DAU time series, top 6 protocols."""
    scores = get_scores()
    names = dict(zip(scores['project_id'], scores['display_name']))
    top6 = scores.head(6)['project_id'].tolist()
    dau_df = get_metric_ts('user_dau', top6, days=180)

    fig, ax = plt.subplots(figsize=(10, 6), facecolor=THEME['bg'])
    for i, pid in enumerate(top6):
        sub = dau_df[dau_df['project_id'] == pid].copy()
        if sub.empty: continue
        sub = sub[['date', 'value']].set_index('date').resample('W').mean().reset_index()
        c = get_palette()[i % len(get_palette())]
        ax.plot(sub['date'], sub['value'] / 1e3, color=c,
                linewidth=1.8, label=names.get(pid, pid), alpha=0.85)
        add_last_value_label(ax, sub['date'], sub['value'] / 1e3, c, fmt='{:.0f}K')

    ax.set_ylabel('Daily Active Users (K)', fontsize=10)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:.0f}K'))
    ax.legend(loc='upper left', fontsize=8, ncol=2, framealpha=0.95, facecolor=THEME['legend_bg'],
                edgecolor=THEME['spine'], labelcolor=THEME['legend_fg'])
    brand_ax(ax, 'DAU Trends (6M)', 'Token Terminal | Weekly Avg | Top 6 by LHM Score')
    brand_fig(fig, '', source='Token Terminal')
    fig.suptitle('')
    save(fig, '04_dau_trends.png')


def chart_05_sector_health():
    """Sector health horizontal bars."""
    scores = get_scores()
    sectors = scores.groupby('sector_clean').agg({
        'overall_score': 'mean',
        'ann_revenue': 'sum',
        'project_id': 'count'
    }).rename(columns={'project_id': 'count'}).sort_values('overall_score', ascending=True)

    # Filter out sectors with only 1 protocol
    sectors = sectors[sectors['count'] >= 1]

    fig, ax = plt.subplots(figsize=(10, 6), facecolor=THEME['bg'])
    sy = np.arange(len(sectors))
    scolors = [clr('green') if s >= 70 else clr('blue') if s >= 55
               else clr('orange') if s >= 40 else clr('red')
               for s in sectors['overall_score']]

    ax.barh(sy, sectors['overall_score'], color=scolors, alpha=0.85,
            edgecolor=THEME['bar_edge'], linewidth=0.5)
    for i, (score, count, rev) in enumerate(zip(
            sectors['overall_score'], sectors['count'], sectors['ann_revenue'])):
        ax.text(score + 1, sy[i], f'{score:.0f}  ({count}p, ${rev/1e6:.0f}M rev)',
                va='center', fontsize=8, color=THEME['text_strong'])

    ax.set_yticks(sy)
    ax.set_yticklabels([s.replace('_', ' ').title() for s in sectors.index], fontsize=9)
    ax.set_xlim(0, 100)
    ax.axvline(55, color=clr('orange'), linestyle='--', alpha=0.3)
    ax.axvline(70, color=clr('green'), linestyle='--', alpha=0.3)
    brand_ax(ax, 'Sector Health', 'Avg LHM Score | (protocols, total annualized revenue)')
    brand_fig(fig, '', source='Token Terminal, LHM Scoring Engine')
    fig.suptitle('')
    save(fig, '05_sector_health.png')


def chart_06_tvl_rankings():
    """TVL bar chart, top 15."""
    scores = get_scores()
    tvl_df = scores[scores['tvl'] > 0].nlargest(15, 'tvl').sort_values('tvl', ascending=True)

    fig, ax = plt.subplots(figsize=(10, 7), facecolor=THEME['bg'])
    y = np.arange(len(tvl_df))
    colors = [get_sector_colors().get(row['sector_clean'], THEME['muted']) for _, row in tvl_df.iterrows()]

    ax.barh(y, tvl_df['tvl'] / 1e9, color=colors, alpha=0.85, edgecolor=THEME['bar_edge'], linewidth=0.5)
    for i, (_, row) in enumerate(tvl_df.iterrows()):
        ax.text(row['tvl'] / 1e9 + 0.3, y[i], f'${row["tvl"]/1e9:.1f}B',
                va='center', fontsize=8, fontweight='bold', color=THEME['text_strong'])

    ax.set_yticks(y)
    ax.set_yticklabels(tvl_df['display_name'], fontsize=9)
    ax.set_xlabel('Total Value Locked ($B)', fontsize=10)
    brand_ax(ax, 'TVL Rankings', 'Token Terminal | Top 15 by TVL')
    brand_fig(fig, '', source='Token Terminal')
    fig.suptitle('')
    save(fig, '06_tvl_rankings.png')


def chart_07_subsidy_score():
    """
    SUBSIDY SCORE CHART (FIXED).
    Computes subsidy_score = token_incentives / revenue from metrics table.
    """
    scores = get_scores()
    names = dict(zip(scores['project_id'], scores['display_name']))

    # Get token_incentives and revenue for all protocols (latest 30 days avg)
    rev_df = get_metric_ts('revenue', days=30)
    inc_df = get_metric_ts('token_incentives', days=30)

    if rev_df.empty and inc_df.empty:
        print('  [07] SKIP: No revenue or incentives data')
        return

    # Average daily values per protocol
    rev_avg = rev_df.groupby('project_id')['value'].mean().rename('avg_rev')
    inc_avg = inc_df.groupby('project_id')['value'].mean().rename('avg_inc')

    # Merge
    combined = pd.concat([rev_avg, inc_avg], axis=1).fillna(0)
    combined = combined[combined['avg_rev'] > 0]  # Need revenue to compute ratio
    combined['subsidy_score'] = combined['avg_inc'] / combined['avg_rev']
    combined = combined.replace([np.inf, -np.inf], np.nan).dropna(subset=['subsidy_score'])
    combined['display_name'] = combined.index.map(lambda x: names.get(x, x))

    # Split into reasonable (<5) and extreme (>5) for visualization
    reasonable = combined[combined['subsidy_score'] <= 5].sort_values('subsidy_score', ascending=True)
    extreme = combined[combined['subsidy_score'] > 5].sort_values('subsidy_score', ascending=True)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 8), facecolor=THEME['bg'],
                                     gridspec_kw={'width_ratios': [3, 1], 'wspace': 0.3})

    # Left: Reasonable subsidy scores
    if not reasonable.empty:
        y = np.arange(len(reasonable))
        colors = []
        for s in reasonable['subsidy_score']:
            if s < 0.5: colors.append(clr('green'))
            elif s < 1.0: colors.append(clr('blue'))
            elif s < 2.0: colors.append(clr('orange'))
            else: colors.append(clr('red'))

        ax1.barh(y, reasonable['subsidy_score'], color=colors, alpha=0.85,
                 edgecolor=THEME['bar_edge'], linewidth=0.5)
        for i, (_, row) in enumerate(reasonable.iterrows()):
            ax1.text(row['subsidy_score'] + 0.05, y[i], f'{row["subsidy_score"]:.2f}x',
                     va='center', fontsize=8, fontweight='bold', color=THEME['text_strong'])
        ax1.set_yticks(y)
        ax1.set_yticklabels(reasonable['display_name'], fontsize=8)
        ax1.axvline(0.5, color=clr('green'), linestyle='--', alpha=0.5, linewidth=1)
        ax1.axvline(2.0, color=clr('red'), linestyle='--', alpha=0.5, linewidth=1)
        ax1.text(0.48, 0.97, 'Organic (<0.5)', fontsize=7, color=clr('green'),
                 transform=ax1.transAxes, ha='right', va='top')
        ax1.text(0.95, 0.97, 'Ponzi (>2.0)', fontsize=7, color=clr('red'),
                 transform=ax1.transAxes, ha='right', va='top')

    brand_ax(ax1, 'Reasonable (<5x)', '')

    # Right: Extreme subsidy scores
    if not extreme.empty:
        y2 = np.arange(len(extreme))
        ax2.barh(y2, extreme['subsidy_score'], color=clr('red'), alpha=0.7,
                 edgecolor=THEME['bar_edge'], linewidth=0.5)
        for i, (_, row) in enumerate(extreme.iterrows()):
            ax2.text(row['subsidy_score'] + 1, y2[i], f'{row["subsidy_score"]:.0f}x',
                     va='center', fontsize=8, fontweight='bold', color=clr('red'))
        ax2.set_yticks(y2)
        ax2.set_yticklabels(extreme['display_name'], fontsize=8)
        brand_ax(ax2, 'Extreme (>5x)', '')
    else:
        ax2.text(0.5, 0.5, 'No extreme\nsubsidies', transform=ax2.transAxes,
                 ha='center', va='center', fontsize=10, color=THEME['spine'])
        ax2.axis('off')

    fig.subplots_adjust(top=0.84)
    brand_fig(fig, 'Subsidy Score Analysis', source='Token Terminal')
    fig.text(0.5, 0.90, 'Token Incentives per $1 of Revenue | <0.5 = Organic | >2.0 = Unsustainable',
             fontsize=9, ha='center', color='#2389BB', style='italic')
    save(fig, '07_subsidy_score.png')


def chart_08_fee_revenue_waterfall():
    """Fees vs Revenue for top protocols (shows take rate)."""
    scores = get_scores()
    df = scores[(scores['ann_fees'] > 0) & (scores['ann_revenue'] > 0)].nlargest(12, 'ann_fees')

    fig, ax = plt.subplots(figsize=(12, 6), facecolor=THEME['bg'])
    x = np.arange(len(df))
    w = 0.35

    ax.bar(x - w/2, df['ann_fees'] / 1e6, w, label='Fees', color=clr('blue'), alpha=0.85)
    ax.bar(x + w/2, df['ann_revenue'] / 1e6, w, label='Revenue', color=clr('orange'), alpha=0.85)

    # Take rate label
    for i, (_, row) in enumerate(df.iterrows()):
        if row['ann_fees'] > 0:
            take_rate = row['ann_revenue'] / row['ann_fees'] * 100
            ax.text(x[i], max(row['ann_fees'], row['ann_revenue']) / 1e6 + 5,
                    f'{take_rate:.0f}%', ha='center', fontsize=7, color=THEME['muted'])

    ax.set_xticks(x)
    ax.set_xticklabels(df['display_name'], fontsize=8, rotation=45, ha='right')
    ax.set_ylabel('Annualized ($M)', fontsize=10)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:.0f}M'))
    ax.legend(fontsize=9, framealpha=0.95, facecolor=THEME['legend_bg'],
                edgecolor=THEME['spine'], labelcolor=THEME['legend_fg'])
    brand_ax(ax, 'Fees vs Revenue (Take Rate)', 'Top 12 by Fees | % = Revenue/Fees')
    fig.subplots_adjust(bottom=0.2)
    brand_fig(fig, '', source='Token Terminal')
    fig.suptitle('')
    save(fig, '08_fee_revenue_waterfall.png')


def chart_09_pe_ratio_spectrum():
    """P/E ratio bar chart showing valuation spectrum."""
    scores = get_scores()
    df = scores[(scores['pf_ratio'] > 0) & (scores['pf_ratio'] < 5000)].copy()
    df = df.sort_values('pf_ratio', ascending=True).head(20)

    fig, ax = plt.subplots(figsize=(10, 8), facecolor=THEME['bg'])
    y = np.arange(len(df))
    colors = []
    for pf in df['pf_ratio']:
        if pf < 20: colors.append(clr('green'))
        elif pf < 50: colors.append(clr('blue'))
        elif pf < 100: colors.append(clr('orange'))
        else: colors.append(clr('red'))

    ax.barh(y, df['pf_ratio'], color=colors, alpha=0.85, edgecolor=THEME['bar_edge'], linewidth=0.5)
    for i, (_, row) in enumerate(df.iterrows()):
        ax.text(row['pf_ratio'] + 1, y[i], f'{row["pf_ratio"]:.1f}x',
                va='center', fontsize=8, color=THEME['text_strong'])

    ax.set_yticks(y)
    ax.set_yticklabels(df['display_name'], fontsize=9)
    ax.axvline(20, color=clr('green'), linestyle='--', alpha=0.4, label='Value (<20x)')
    ax.axvline(100, color=clr('red'), linestyle='--', alpha=0.4, label='Expensive (>100x)')
    ax.legend(fontsize=8, loc='lower right')
    brand_ax(ax, 'P/F Valuation Spectrum', 'FDV / Annualized Fees | Lower = Cheaper')
    brand_fig(fig, '', source='Token Terminal')
    fig.suptitle('')
    save(fig, '09_pf_ratio_spectrum.png')


def chart_10_float_ratio():
    """Float ratio (circulating / FDV)."""
    scores = get_scores()
    df = scores[(scores['float_ratio'] > 0) & (scores['float_ratio'] <= 1)].copy()
    df = df.sort_values('float_ratio', ascending=True).head(20)

    fig, ax = plt.subplots(figsize=(10, 8), facecolor=THEME['bg'])
    y = np.arange(len(df))
    colors = []
    for f in df['float_ratio']:
        if f < 0.2: colors.append(clr('red'))
        elif f < 0.5: colors.append(clr('orange'))
        else: colors.append(clr('green'))

    ax.barh(y, df['float_ratio'] * 100, color=colors, alpha=0.85, edgecolor=THEME['bar_edge'], linewidth=0.5)
    for i, (_, row) in enumerate(df.iterrows()):
        ax.text(row['float_ratio'] * 100 + 1, y[i], f'{row["float_ratio"]:.0%}',
                va='center', fontsize=8, color=THEME['text_strong'])

    ax.set_yticks(y)
    ax.set_yticklabels(df['display_name'], fontsize=9)
    ax.axvline(20, color=clr('red'), linestyle='--', alpha=0.4, label='Predatory (<20%)')
    ax.axvline(50, color=clr('green'), linestyle='--', alpha=0.4, label='Healthy (>50%)')
    ax.set_xlabel('Float Ratio (%)', fontsize=10)
    ax.legend(fontsize=8, loc='lower right')
    brand_ax(ax, 'Float Ratio (Unlock Risk)', 'Circulating / Total Supply | Lower = More Dilution Ahead')
    brand_fig(fig, '', source='Token Terminal')
    fig.suptitle('')
    save(fig, '10_float_ratio.png')


def chart_11_tvl_trends():
    """TVL time series for top 6."""
    scores = get_scores()
    names = dict(zip(scores['project_id'], scores['display_name']))
    top6_tvl = scores[scores['tvl'] > 0].nlargest(6, 'tvl')['project_id'].tolist()
    tvl_df = get_metric_ts('tvl', top6_tvl, days=180)

    fig, ax = plt.subplots(figsize=(10, 6), facecolor=THEME['bg'])
    for i, pid in enumerate(top6_tvl):
        sub = tvl_df[tvl_df['project_id'] == pid].copy()
        if sub.empty: continue
        sub = sub[['date', 'value']].set_index('date').resample('W').mean().reset_index()
        c = get_palette()[i % len(get_palette())]
        ax.plot(sub['date'], sub['value'] / 1e9, color=c,
                linewidth=1.8, label=names.get(pid, pid), alpha=0.85)
        add_last_value_label(ax, sub['date'], sub['value'] / 1e9, c, fmt='${:.1f}B')

    ax.set_ylabel('TVL ($B)', fontsize=10)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:.1f}B'))
    ax.legend(loc='upper left', fontsize=8, ncol=2, framealpha=0.95, facecolor=THEME['legend_bg'],
                edgecolor=THEME['spine'], labelcolor=THEME['legend_fg'])
    brand_ax(ax, 'TVL Trends (6M)', 'Token Terminal | Weekly Avg | Top 6 by TVL')
    brand_fig(fig, '', source='Token Terminal')
    fig.suptitle('')
    save(fig, '11_tvl_trends.png')


def chart_12_fee_trends():
    """Fee time series, top 6 protocols."""
    scores = get_scores()
    names = dict(zip(scores['project_id'], scores['display_name']))
    top6 = scores[scores['ann_fees'] > 0].nlargest(6, 'ann_fees')['project_id'].tolist()
    fee_df = get_metric_ts('fees', top6, days=180)

    fig, ax = plt.subplots(figsize=(10, 6), facecolor=THEME['bg'])
    for i, pid in enumerate(top6):
        sub = fee_df[fee_df['project_id'] == pid].copy()
        if sub.empty: continue
        sub = sub[['date', 'value']].set_index('date').resample('W').mean().reset_index()
        c = get_palette()[i % len(get_palette())]
        ax.plot(sub['date'], sub['value'] / 1e6, color=c,
                linewidth=1.8, label=names.get(pid, pid), alpha=0.85)
        add_last_value_label(ax, sub['date'], sub['value'] / 1e6, c, fmt='${:.1f}M')

    ax.set_ylabel('Weekly Fees ($M)', fontsize=10)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:.1f}M'))
    ax.legend(loc='upper left', fontsize=8, ncol=2, framealpha=0.95, facecolor=THEME['legend_bg'],
                edgecolor=THEME['spine'], labelcolor=THEME['legend_fg'])
    brand_ax(ax, 'Fee Trends (6M)', 'Token Terminal | Weekly Avg | Top 6 by Fees')
    brand_fig(fig, '', source='Token Terminal')
    fig.suptitle('')
    save(fig, '12_fee_trends.png')


def chart_13_dau_rankings():
    """Static DAU bar chart rankings."""
    scores = get_scores()
    df = scores[scores['dau'] > 0].nlargest(15, 'dau').sort_values('dau', ascending=True)

    fig, ax = plt.subplots(figsize=(10, 7), facecolor=THEME['bg'])
    y = np.arange(len(df))
    colors = [get_sector_colors().get(row['sector_clean'], THEME['muted']) for _, row in df.iterrows()]

    ax.barh(y, df['dau'] / 1e3, color=colors, alpha=0.85, edgecolor=THEME['bar_edge'], linewidth=0.5)
    for i, (_, row) in enumerate(df.iterrows()):
        ax.text(row['dau'] / 1e3 + 5, y[i], f'{row["dau"]/1e3:.0f}K',
                va='center', fontsize=8, fontweight='bold', color=THEME['text_strong'])

    ax.set_yticks(y)
    ax.set_yticklabels(df['display_name'], fontsize=9)
    ax.set_xlabel('Daily Active Users (K)', fontsize=10)
    brand_ax(ax, 'DAU Rankings', 'Token Terminal | Latest Snapshot')
    brand_fig(fig, '', source='Token Terminal')
    fig.suptitle('')
    save(fig, '13_dau_rankings.png')


def chart_14_verdict_breakdown():
    """Pie/donut chart of verdict distribution."""
    scores = get_scores()

    # Simplify verdicts
    def bucket(v):
        v = str(v)
        if 'TIER 1' in v: return 'Tier 1 (Accumulate)'
        if 'TIER 2' in v: return 'Tier 2 (Hold)'
        if 'NEUTRAL' in v: return 'Neutral (Watch)'
        if 'CAUTION' in v: return 'Caution'
        if 'AVOID' in v: return 'Avoid'
        return 'Other'

    scores['bucket'] = scores['verdict'].apply(bucket)
    counts = scores['bucket'].value_counts()

    fig, ax = plt.subplots(figsize=(8, 8), facecolor=THEME['bg'])
    color_map = {
        'Tier 1 (Accumulate)': clr('green'),
        'Tier 2 (Hold)': clr('blue'),
        'Neutral (Watch)': C['neutral_gray'],
        'Caution': clr('orange'),
        'Avoid': clr('red'),
        'Other': '#666',
    }
    colors = [color_map.get(b, '#666') for b in counts.index]

    wedges, texts, autotexts = ax.pie(counts, labels=counts.index, colors=colors,
                                       autopct='%1.0f%%', pctdistance=0.75,
                                       startangle=90, textprops={'fontsize': 9, 'color': THEME['fg']})
    for t in autotexts:
        t.set_fontweight('bold')
        t.set_color(THEME['fg'])

    # Donut
    centre_circle = plt.Circle((0, 0), 0.55, fc=THEME['bg'])
    ax.add_artist(centre_circle)
    ax.text(0, 0, f'{len(scores)}\nProtocols', ha='center', va='center',
            fontsize=14, fontweight='bold', color=THEME['text_strong'])

    brand_ax(ax, '', '')
    brand_fig(fig, 'LHM Verdict Distribution', f'{len(scores)} Protocols Analyzed',
              source='Token Terminal, LHM Scoring Engine')
    save(fig, '14_verdict_distribution.png')


def chart_15_token_incentives_trends():
    """Token incentives time series."""
    scores = get_scores()
    names = dict(zip(scores['project_id'], scores['display_name']))
    # Get protocols with actual incentives
    has_incentives = scores[scores['subsidy_score'].notna() & (scores['subsidy_score'] > 0)].head(6)
    pids = has_incentives['project_id'].tolist()
    if not pids:
        print('  [15] SKIP: No protocols with incentives data')
        return

    inc_df = get_metric_ts('token_incentives', pids, days=180)
    if inc_df.empty:
        print('  [15] SKIP: No incentives time series data')
        return

    fig, ax = plt.subplots(figsize=(10, 6), facecolor=THEME['bg'])
    for i, pid in enumerate(pids):
        sub = inc_df[inc_df['project_id'] == pid].copy()
        if sub.empty: continue
        sub = sub[sub['value'] > 0]
        if sub.empty: continue
        sub = sub[['date', 'value']].set_index('date').resample('W').mean().reset_index()
        c = get_palette()[i % len(get_palette())]
        ax.plot(sub['date'], sub['value'] / 1e6, color=c,
                linewidth=1.8, label=names.get(pid, pid), alpha=0.85)
        add_last_value_label(ax, sub['date'], sub['value'] / 1e6, c, fmt='${:.1f}M')

    ax.set_ylabel('Token Incentives ($M/wk)', fontsize=10)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:.1f}M'))
    ax.legend(loc='upper left', fontsize=8, ncol=2, framealpha=0.95, facecolor=THEME['legend_bg'],
                edgecolor=THEME['spine'], labelcolor=THEME['legend_fg'])
    brand_ax(ax, 'Token Incentive Spending (6M)', 'Protocols paying most for user acquisition')
    brand_fig(fig, '', source='Token Terminal')
    fig.suptitle('')
    save(fig, '15_token_incentives.png')


def chart_16_earnings_heatmap():
    """Protocol earnings (revenue - incentives) heatmap style."""
    scores = get_scores()
    df = scores[scores['ann_revenue'] > 0].head(20).copy()

    # Compute earnings = revenue - incentives (using subsidy_score)
    df['ann_incentives'] = df['subsidy_score'].fillna(0) * df['ann_revenue']
    df['net_earnings'] = df['ann_revenue'] - df['ann_incentives']

    fig, ax = plt.subplots(figsize=(10, 7), facecolor=THEME['bg'])
    df = df.sort_values('net_earnings', ascending=True)
    y = np.arange(len(df))

    colors = [clr('green') if e > 0 else clr('red') for e in df['net_earnings']]
    ax.barh(y, df['net_earnings'] / 1e6, color=colors, alpha=0.85, edgecolor=THEME['bar_edge'], linewidth=0.5)

    for i, (_, row) in enumerate(df.iterrows()):
        val = row['net_earnings'] / 1e6
        offset = 1 if val >= 0 else -1
        ax.text(val + offset, y[i], f'${val:.1f}M',
                va='center', fontsize=7.5, fontweight='bold',
                ha='left' if val >= 0 else 'right', color=THEME['text_strong'])

    ax.set_yticks(y)
    ax.set_yticklabels(df['display_name'], fontsize=8)
    ax.axvline(0, color=THEME['text_strong'], linewidth=0.8)
    ax.set_xlabel('Net Earnings ($M ann.)', fontsize=10)
    brand_ax(ax, 'Protocol Net Earnings', 'Revenue - Token Incentives | Green = Profitable')
    brand_fig(fig, '', source='Token Terminal, LHM Analysis')
    fig.suptitle('')
    save(fig, '16_net_earnings.png')


def chart_17_price_trends():
    """Token price trends for top 6."""
    scores = get_scores()
    names = dict(zip(scores['project_id'], scores['display_name']))
    top6 = scores.head(6)['project_id'].tolist()
    price_df = get_metric_ts('price', top6, days=180)

    fig, ax = plt.subplots(figsize=(10, 6), facecolor=THEME['bg'])
    for i, pid in enumerate(top6):
        sub = price_df[price_df['project_id'] == pid].copy()
        if sub.empty: continue
        # Normalize to 100 at start
        sub = sub.sort_values('date')
        base = sub['value'].iloc[0]
        if base > 0:
            sub['norm'] = sub['value'] / base * 100
            c = get_palette()[i % len(get_palette())]
            ax.plot(sub['date'], sub['norm'], color=c,
                    linewidth=1.8, label=names.get(pid, pid), alpha=0.85)
            add_last_value_label(ax, sub['date'], sub['norm'], c, fmt='{:.0f}')

    ax.axhline(100, color=THEME['spine'], linestyle='--', linewidth=0.5)
    ax.set_ylabel('Indexed Price (100 = 6M ago)', fontsize=10)
    ax.legend(loc='upper left', fontsize=8, ncol=2, framealpha=0.95, facecolor=THEME['legend_bg'],
                edgecolor=THEME['spine'], labelcolor=THEME['legend_fg'])
    brand_ax(ax, 'Price Performance (6M, Indexed)', 'Top 6 by LHM Score | Rebased to 100')
    brand_fig(fig, '', source='Token Terminal')
    fig.suptitle('')
    save(fig, '17_price_performance.png')


def chart_18_developer_activity():
    """Developer count rankings."""
    scores = get_scores()
    df = scores[scores['active_developers'] > 0].nlargest(15, 'active_developers').sort_values('active_developers', ascending=True)

    if df.empty:
        print('  [18] SKIP: No developer data')
        return

    fig, ax = plt.subplots(figsize=(10, 7), facecolor=THEME['bg'])
    y = np.arange(len(df))
    colors = [get_sector_colors().get(row['sector_clean'], THEME['muted']) for _, row in df.iterrows()]

    ax.barh(y, df['active_developers'], color=colors, alpha=0.85, edgecolor=THEME['bar_edge'], linewidth=0.5)
    for i, (_, row) in enumerate(df.iterrows()):
        ax.text(row['active_developers'] + 0.5, y[i], f'{int(row["active_developers"])}',
                va='center', fontsize=8, fontweight='bold', color=THEME['text_strong'])

    ax.set_yticks(y)
    ax.set_yticklabels(df['display_name'], fontsize=9)
    ax.set_xlabel('Active Developers', fontsize=10)
    brand_ax(ax, 'Developer Activity Rankings', 'Token Terminal | Monthly Active Developers')
    brand_fig(fig, '', source='Token Terminal')
    fig.suptitle('')
    save(fig, '18_developer_activity.png')


def chart_19_market_cap_vs_revenue():
    """Market cap vs revenue scatter, log scale."""
    scores = get_scores()
    df = scores[(scores['market_cap'] > 0) & (scores['ann_revenue'] > 0)].copy()

    fig, ax = plt.subplots(figsize=(10, 8), facecolor=THEME['bg'])
    colors = [get_sector_colors().get(row['sector_clean'], THEME['muted']) for _, row in df.iterrows()]

    ax.scatter(df['ann_revenue'] / 1e6, df['market_cap'] / 1e9,
               c=colors, s=80, alpha=0.7, edgecolors=THEME['bar_edge'], linewidth=0.5)

    for _, row in df.iterrows():
        if row['ann_revenue'] > 5e6 or row['market_cap'] > 2e9:
            ax.annotate(row['display_name'],
                        (row['ann_revenue'] / 1e6, row['market_cap'] / 1e9),
                        fontsize=7, xytext=(5, 5), textcoords='offset points',
                        color=THEME['text_label'])

    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel('Annualized Revenue ($M)', fontsize=10)
    ax.set_ylabel('Market Cap ($B)', fontsize=10)

    # Unique sector legend
    seen = set()
    legend_els = []
    for _, row in df.iterrows():
        s = row['sector_clean']
        if s not in seen:
            seen.add(s)
            legend_els.append(Line2D([0], [0], marker='o', color='w',
                                     markerfacecolor=get_sector_colors().get(s, THEME['muted']),
                                     markersize=8, label=s))
    ax.legend(handles=legend_els, fontsize=7, loc='upper left', framealpha=0.95, facecolor=THEME['legend_bg'],
                edgecolor=THEME['spine'], labelcolor=THEME['legend_fg'])
    brand_ax(ax, 'Market Cap vs Revenue', 'Log Scale | Colored by Sector')
    brand_fig(fig, '', source='Token Terminal')
    fig.suptitle('')
    save(fig, '19_mcap_vs_revenue.png')


def chart_20_scoring_radar():
    """Score comparison table (styled)."""
    scores = get_scores()
    df = scores.head(15)[['display_name', 'financial_score', 'usage_score',
                           'valuation_score', 'overall_score', 'verdict']].copy()

    fig, ax = plt.subplots(figsize=(12, 6), facecolor=THEME['bg'])
    ax.axis('off')

    # Prepare table data
    table_data = []
    cell_colors = []
    for _, row in df.iterrows():
        def score_color(s):
            if s >= 80: return THEME['table_row_green']
            elif s >= 60: return THEME['table_row_blue']
            elif s >= 40: return THEME['table_row_yellow']
            else: return THEME['table_row_red']

        v = str(row['verdict'])
        if 'TIER 1' in v: vc = THEME['table_verdict_green']
        elif 'TIER 2' in v: vc = THEME['table_verdict_blue']
        elif 'NEUTRAL' in v: vc = THEME['table_verdict_gray']
        else: vc = THEME['table_verdict_red']

        table_data.append([
            row['display_name'],
            f'{row["financial_score"]:.0f}',
            f'{row["usage_score"]:.0f}',
            f'{row["valuation_score"]:.0f}',
            f'{row["overall_score"]:.0f}',
            v[:15]
        ])
        cell_colors.append([
            THEME['table_row_white'],
            score_color(row['financial_score']),
            score_color(row['usage_score']),
            score_color(row['valuation_score']),
            score_color(row['overall_score']),
            vc
        ])

    table = ax.table(cellText=table_data,
                      colLabels=['Protocol', 'Financial', 'Usage', 'Valuation', 'Overall', 'Verdict'],
                      cellColours=cell_colors,
                      loc='center', cellLoc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 1.6)

    # Style all cells
    for (row, col), cell in table.get_celld().items():
        if row == 0:
            cell.set_text_props(fontweight='bold', color='white')
            cell.set_facecolor(THEME['table_header_bg'])
        else:
            cell.set_text_props(color=THEME['fg'])
        cell.set_edgecolor(THEME['spine'])

    brand_fig(fig, 'Protocol Score Card', 'Top 15 by Overall Score | LHM 24-Point System',
              source='Token Terminal, LHM Scoring Engine')
    save(fig, '20_score_card.png')


# =========================================================================
# TT x MACRO OVERLAY CHARTS (21-25)
# =========================================================================

def chart_21_crypto_rev_vs_rrp():
    """Total crypto protocol revenue vs Fed RRP."""
    all_rev = get_metric_ts('revenue', days=365)
    if all_rev.empty:
        print('  [21] SKIP: No revenue data')
        return

    agg_rev = all_rev.groupby('date')['value'].sum().reset_index()
    agg_rev = agg_rev.set_index('date').resample('W').mean().reset_index()

    rrp = get_macro_ts('RRPONTSYD', 365)

    fig, ax = plt.subplots(figsize=(12, 6), facecolor=THEME['bg'])
    ax.bar(agg_rev['date'], agg_rev['value'] / 1e6, width=5,
           color=clr('orange'), alpha=0.6, label='Total Protocol Revenue ($M/wk)')
    ax.set_ylabel('Weekly Revenue ($M)', fontsize=10, color=clr('orange'))
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:.0f}M'))

    ax2 = ax.twinx()
    if not rrp.empty:
        ax2.plot(rrp['date'], rrp['value'], color=clr('blue'),
                 linewidth=2.5, label='RRP ($B)', alpha=0.8)
        ax2.set_ylabel('RRP ($B)', fontsize=10, color=clr('blue'))
        ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:.0f}B'))
        style_twin_ax(ax2, clr('blue'))
        add_last_value_label(ax2, rrp['date'], rrp['value'], clr('blue'), fmt='${:.0f}B')

    # Last value label for bars (LHS)
    if not agg_rev.empty:
        add_last_value_label(ax, agg_rev['date'], agg_rev['value'] / 1e6, clr('orange'), fmt='${:.1f}M', side='left')

    ax.legend(loc='upper left', fontsize=8, framealpha=0.95, facecolor=THEME['legend_bg'],
                edgecolor=THEME['spine'], labelcolor=THEME['legend_fg'])
    if not rrp.empty:
        ax2.legend(loc='upper right', fontsize=8, framealpha=0.95, facecolor=THEME['legend_bg'],
                edgecolor=THEME['spine'], labelcolor=THEME['legend_fg'])
    brand_ax(ax, 'Crypto Revenue vs Fed Liquidity', 'Total Protocol Rev (bars) vs Reverse Repo (line) | 1Y')
    brand_fig(fig, '', source='Token Terminal, FRED (NY Fed)')
    fig.suptitle('')
    save(fig, '21_crypto_rev_vs_rrp.png')


def chart_22_crypto_dau_vs_nfci():
    """Total crypto DAU vs financial conditions (NFCI)."""
    all_dau = get_metric_ts('user_dau', days=365)
    if all_dau.empty:
        print('  [22] SKIP: No DAU data')
        return

    agg_dau = all_dau.groupby('date')['value'].sum().reset_index()
    agg_dau = agg_dau.set_index('date').resample('W').mean().reset_index()

    nfci = get_macro_ts('NFCI', 365)

    fig, ax = plt.subplots(figsize=(12, 6), facecolor=THEME['bg'])
    ax.plot(agg_dau['date'], agg_dau['value'] / 1e6, color=clr('orange'),
            linewidth=2, label='Total Crypto DAU (M)', alpha=0.85)
    ax.fill_between(agg_dau['date'], agg_dau['value'] / 1e6, alpha=0.15, color=clr('orange'))
    ax.set_ylabel('Total DAU (M)', fontsize=10, color=clr('orange'))

    ax2 = ax.twinx()
    if not nfci.empty:
        ax2.plot(nfci['date'], nfci['value'], color=clr('blue'),
                 linewidth=2, label='NFCI', alpha=0.8)
        ax2.axhline(0, color=THEME['spine'], linewidth=0.5)
        ax2.set_ylabel('NFCI (Neg = Loose)', fontsize=10, color=clr('blue'))
        ax2.invert_yaxis()  # Invert so loose conditions (neg) show at top
        style_twin_ax(ax2, clr('blue'))
        add_last_value_label(ax2, nfci['date'], nfci['value'], clr('blue'), fmt='{:.2f}')

    # Last value for DAU (LHS)
    if not agg_dau.empty:
        add_last_value_label(ax, agg_dau['date'], agg_dau['value'] / 1e6, clr('orange'), fmt='{:.1f}M', side='left')

    ax.legend(loc='upper left', fontsize=8, framealpha=0.95, facecolor=THEME['legend_bg'],
                edgecolor=THEME['spine'], labelcolor=THEME['legend_fg'])
    if not nfci.empty:
        ax2.legend(loc='upper right', fontsize=8, framealpha=0.95, facecolor=THEME['legend_bg'],
                edgecolor=THEME['spine'], labelcolor=THEME['legend_fg'])
    brand_ax(ax, 'Crypto Adoption vs Financial Conditions',
             'Aggregate DAU vs NFCI (inverted) | Loose conditions = crypto growth')
    brand_fig(fig, '', source='Token Terminal, FRED (Chicago Fed)')
    fig.suptitle('')
    save(fig, '22_dau_vs_nfci.png')


def chart_23_crypto_fees_vs_hy_spreads():
    """Total crypto fees vs HY credit spreads."""
    all_fees = get_metric_ts('fees', days=365)
    if all_fees.empty:
        print('  [23] SKIP: No fees data')
        return

    agg_fees = all_fees.groupby('date')['value'].sum().reset_index()
    agg_fees = agg_fees.set_index('date').resample('W').mean().reset_index()

    hy = get_macro_ts('BAMLH0A0HYM2', 365)

    fig, ax = plt.subplots(figsize=(12, 6), facecolor=THEME['bg'])
    ax.plot(agg_fees['date'], agg_fees['value'] / 1e6, color=clr('magenta'),
            linewidth=2, label='Total Crypto Fees ($M/wk)', alpha=0.85)
    ax.fill_between(agg_fees['date'], agg_fees['value'] / 1e6, alpha=0.15, color=clr('magenta'))
    ax.set_ylabel('Weekly Fees ($M)', fontsize=10, color=clr('magenta'))
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:.0f}M'))

    ax2 = ax.twinx()
    if not hy.empty:
        ax2.fill_between(hy['date'], hy['value'] * 100, alpha=0.15, color=clr('orange'))
        ax2.plot(hy['date'], hy['value'] * 100, color=clr('orange'),
                 linewidth=2, label='HY OAS (bps)', alpha=0.8)
        ax2.set_ylabel('HY Spread (bps)', fontsize=10, color=clr('orange'))
        ax2.invert_yaxis()  # Tight spreads (bullish) at top
        style_twin_ax(ax2, clr('orange'))
        add_last_value_label(ax2, hy['date'], hy['value'] * 100, clr('orange'), fmt='{:.0f} bps')

    # Last value for fees (LHS)
    if not agg_fees.empty:
        add_last_value_label(ax, agg_fees['date'], agg_fees['value'] / 1e6, clr('magenta'), fmt='${:.1f}M', side='left')

    ax.legend(loc='upper left', fontsize=8, framealpha=0.95, facecolor=THEME['legend_bg'],
                edgecolor=THEME['spine'], labelcolor=THEME['legend_fg'])
    if not hy.empty:
        ax2.legend(loc='upper right', fontsize=8, framealpha=0.95, facecolor=THEME['legend_bg'],
                edgecolor=THEME['spine'], labelcolor=THEME['legend_fg'])
    brand_ax(ax, 'Crypto Fees vs Credit Spreads',
             'Tight spreads + rising fees = risk-on regime')
    brand_fig(fig, '', source='Token Terminal, FRED (BofA ICE)')
    fig.suptitle('')
    save(fig, '23_fees_vs_hy_spreads.png')


def chart_24_defi_tvl_vs_vix():
    """DeFi TVL trends vs VIX."""
    tvl_df = get_metric_ts('tvl', days=365)
    if tvl_df.empty:
        print('  [24] SKIP: No TVL data')
        return

    agg_tvl = tvl_df.groupby('date')['value'].sum().reset_index()
    agg_tvl = agg_tvl.set_index('date').resample('W').mean().reset_index()

    vix = get_macro_ts('VIXCLS', 365)

    fig, ax = plt.subplots(figsize=(12, 6), facecolor=THEME['bg'])
    ax.plot(agg_tvl['date'], agg_tvl['value'] / 1e9, color=clr('green'),
            linewidth=2.5, label='Total DeFi TVL ($B)', alpha=0.85)
    ax.fill_between(agg_tvl['date'], agg_tvl['value'] / 1e9, alpha=0.15, color=clr('green'))
    ax.set_ylabel('DeFi TVL ($B)', fontsize=10, color=clr('green'))
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:.0f}B'))

    ax2 = ax.twinx()
    if not vix.empty:
        ax2.fill_between(vix['date'], vix['value'], alpha=0.15, color=clr('magenta'))
        ax2.plot(vix['date'], vix['value'], color=clr('magenta'),
                 linewidth=1.5, label='VIX', alpha=0.7)
        ax2.axhline(20, color=clr('orange'), linestyle='--', alpha=0.3)
        ax2.set_ylabel('VIX', fontsize=10, color=clr('magenta'))
        ax2.invert_yaxis()  # Low VIX (bullish) at top
        style_twin_ax(ax2, clr('magenta'))
        add_last_value_label(ax2, vix['date'], vix['value'], clr('magenta'), fmt='{:.1f}')

    # Last value for TVL (LHS)
    if not agg_tvl.empty:
        add_last_value_label(ax, agg_tvl['date'], agg_tvl['value'] / 1e9, clr('green'), fmt='${:.1f}B', side='left')

    ax.legend(loc='upper left', fontsize=8, framealpha=0.95, facecolor=THEME['legend_bg'],
                edgecolor=THEME['spine'], labelcolor=THEME['legend_fg'])
    if not vix.empty:
        ax2.legend(loc='upper right', fontsize=8, framealpha=0.95, facecolor=THEME['legend_bg'],
                edgecolor=THEME['spine'], labelcolor=THEME['legend_fg'])
    brand_ax(ax, 'DeFi TVL vs Volatility',
             'TVL grows when vol compresses | VIX inverted')
    brand_fig(fig, '', source='Token Terminal, FRED (CBOE)')
    fig.suptitle('')
    save(fig, '24_tvl_vs_vix.png')


def chart_25_crypto_rev_vs_yield_curve():
    """Total crypto revenue vs yield curve steepness."""
    all_rev = get_metric_ts('revenue', days=365)
    if all_rev.empty:
        print('  [25] SKIP: No revenue data')
        return

    agg_rev = all_rev.groupby('date')['value'].sum().reset_index()
    agg_rev = agg_rev.set_index('date').resample('W').mean().reset_index()

    t10y2y = get_macro_ts('T10Y2Y', 365)

    fig, ax = plt.subplots(figsize=(12, 6), facecolor=THEME['bg'])
    ax.bar(agg_rev['date'], agg_rev['value'] / 1e6, width=5,
           color=clr('orange'), alpha=0.6, label='Total Protocol Revenue ($M/wk)')
    ax.set_ylabel('Weekly Revenue ($M)', fontsize=10, color=clr('orange'))
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:.0f}M'))

    ax2 = ax.twinx()
    if not t10y2y.empty:
        pos = t10y2y['value'] >= 0
        neg = t10y2y['value'] < 0
        ax2.fill_between(t10y2y['date'], t10y2y['value'],
                         where=pos, alpha=0.15, color=clr('blue'))
        ax2.fill_between(t10y2y['date'], t10y2y['value'],
                         where=neg, alpha=0.15, color=clr('red'))
        ax2.plot(t10y2y['date'], t10y2y['value'], color=clr('blue'),
                 linewidth=2, label='10Y-2Y Spread (%)', alpha=0.8)
        ax2.axhline(0, color=THEME['spine'], linewidth=0.5)
        ax2.set_ylabel('Yield Curve (10Y-2Y %)', fontsize=10, color=clr('blue'))
        style_twin_ax(ax2, clr('blue'))
        add_last_value_label(ax2, t10y2y['date'], t10y2y['value'], clr('blue'), fmt='{:.2f}%')

    # Last value for revenue bars (LHS axis)
    if not agg_rev.empty:
        add_last_value_label(ax, agg_rev['date'], agg_rev['value'] / 1e6, clr('orange'), fmt='${:.1f}M', side='left')

    ax.legend(loc='upper left', fontsize=8, framealpha=0.95, facecolor=THEME['legend_bg'],
                edgecolor=THEME['spine'], labelcolor=THEME['legend_fg'])
    if not t10y2y.empty:
        ax2.legend(loc='upper right', fontsize=8, framealpha=0.95, facecolor=THEME['legend_bg'],
                edgecolor=THEME['spine'], labelcolor=THEME['legend_fg'])
    brand_ax(ax, 'Crypto Revenue vs Yield Curve',
             'Steepening curve + rising revenue = macro expansion signal')
    brand_fig(fig, '', source='Token Terminal, FRED (US Treasury)')
    fig.suptitle('')
    save(fig, '25_rev_vs_yield_curve.png')


# =========================================================================
# RUN ALL
# =========================================================================

def run_all_charts():
    """Generate all 25 charts."""
    print('TOKEN TERMINAL STANDALONE:')
    chart_01_scoring_matrix()
    chart_02_valuation_map()
    chart_03_revenue_trends()
    chart_04_dau_trends()
    chart_05_sector_health()
    chart_06_tvl_rankings()
    chart_07_subsidy_score()
    chart_08_fee_revenue_waterfall()
    chart_09_pe_ratio_spectrum()
    chart_10_float_ratio()
    chart_11_tvl_trends()
    chart_12_fee_trends()
    chart_13_dau_rankings()
    chart_14_verdict_breakdown()
    chart_15_token_incentives_trends()
    chart_16_earnings_heatmap()
    chart_17_price_trends()
    chart_18_developer_activity()
    chart_19_market_cap_vs_revenue()
    chart_20_scoring_radar()

    print()
    print('TT x MACRO OVERLAYS:')
    chart_21_crypto_rev_vs_rrp()
    chart_22_crypto_dau_vs_nfci()
    chart_23_crypto_fees_vs_hy_spreads()
    chart_24_defi_tvl_vs_vix()
    chart_25_crypto_rev_vs_yield_curve()


if __name__ == '__main__':
    modes = ['white']
    if '--dark' in sys.argv:
        modes = ['dark']
    elif '--both' in sys.argv:
        modes = ['white', 'dark']

    for mode in modes:
        set_theme(mode)
        print(f'\nLIGHTHOUSE MACRO x TOKEN TERMINAL — {mode.upper()} Theme')
        print('=' * 55)
        print(f'Date: {datetime.now().strftime("%Y-%m-%d %H:%M")}')
        print(f'Output: {OUT}')
        print()
        run_all_charts()
        print()
        print(f'Done ({mode}). 25 charts saved to {OUT}/')

    conn.close()
    print(f'\nOpen: open {OUT}')
