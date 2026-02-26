#!/usr/bin/env python3
"""
Generate Charts for Educational Series: Post 4 - Consumer (Pillar 5)
=====================================================================
Generates BOTH white and dark theme versions.
Matches format from Growth: THE SECOND DERIVATIVE charts.

Usage:
    python consumer_edu_charts.py --chart 1
    python consumer_edu_charts.py --chart 1 --theme dark
    python consumer_edu_charts.py --all
"""

import os
import argparse
import time
import ssl
import certifi
from datetime import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
from matplotlib.ticker import FuncFormatter
from fredapi import Fred

# Fix SSL certificate issue
os.environ['SSL_CERT_FILE'] = certifi.where()
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()

# ============================================
# PATHS & CONFIG
# ============================================
BASE_PATH = '/Users/bob/LHM'
OUTPUT_BASE = f'{BASE_PATH}/Outputs/Educational_Charts/Consumer_Post_4'
DB_PATH = f'{BASE_PATH}/Data/databases/Lighthouse_Master.db'

fred = Fred()

# Simple cache to avoid refetching same data across themes
_DATA_CACHE = {}

COLORS = {
    'ocean': '#2389BB',
    'dusk': '#FF6723',
    'sky': '#00BBFF',
    'venus': '#FF2389',
    'sea': '#00BB89',
    'doldrums': '#898989',
    'starboard': '#238923',
    'port': '#892323',
}

RECESSIONS = [
    ('2001-03-01', '2001-11-01'),
    ('2007-12-01', '2009-06-01'),
    ('2020-02-01', '2020-04-01'),
]

# ============================================
# THEME CONFIG
# ============================================
THEME = {}
OUTPUT_DIR = ''


def set_theme(mode='dark'):
    global THEME, OUTPUT_DIR
    if mode == 'dark':
        THEME.update({
            'bg': '#0A1628',
            'fg': '#e6edf3',
            'muted': '#8b949e',
            'spine': '#1e3350',
            'zero_line': '#e6edf3',
            'recession': '#ffffff',
            'recession_alpha': 0.06,
            'ocean': COLORS['ocean'],
            'dusk': COLORS['dusk'],
            'sky': COLORS['sky'],
            'sea': COLORS['sea'],
            'venus': COLORS['venus'],
            'primary': COLORS['ocean'],
            'secondary': COLORS['dusk'],
            'tertiary': COLORS['sky'],
            'quaternary': COLORS['sea'],
            'accent': COLORS['venus'],
            'fill_alpha': 0.20,
            'box_bg': '#0A1628',
            'box_edge': COLORS['ocean'],
            'legend_bg': '#0f1f38',
            'legend_fg': '#e6edf3',
            'mode': 'dark',
        })
    else:
        THEME.update({
            'bg': '#ffffff',
            'fg': '#1a1a1a',
            'muted': '#555555',
            'spine': '#898989',
            'zero_line': '#D1D1D1',
            'recession': 'gray',
            'recession_alpha': 0.12,
            'ocean': COLORS['ocean'],
            'dusk': COLORS['dusk'],
            'sky': COLORS['sky'],
            'sea': COLORS['sea'],
            'venus': COLORS['venus'],
            'primary': COLORS['ocean'],
            'secondary': COLORS['dusk'],
            'tertiary': COLORS['sky'],
            'quaternary': COLORS['sea'],
            'accent': COLORS['venus'],
            'fill_alpha': 0.15,
            'box_bg': '#ffffff',
            'box_edge': COLORS['ocean'],
            'legend_bg': '#f8f8f8',
            'legend_fg': '#1a1a1a',
            'mode': 'white',
        })
    OUTPUT_DIR = os.path.join(OUTPUT_BASE, mode)
    os.makedirs(OUTPUT_DIR, exist_ok=True)


# ============================================
# DATA HELPERS
# ============================================
def fetch_fred(series_id, start='2000-01-01'):
    """Fetch a FRED series and return as DataFrame. Uses cache to avoid rate limits."""
    cache_key = f"{series_id}_{start}"
    if cache_key in _DATA_CACHE:
        return _DATA_CACHE[cache_key].copy()

    time.sleep(1.0)  # Rate limit protection
    s = fred.get_series(series_id, observation_start=start)
    df = s.to_frame(name='value')
    df.index.name = 'date'
    _DATA_CACHE[cache_key] = df.copy()
    return df


def yoy_pct(df, col='value'):
    """Compute YoY % change from index level."""
    return df[col].pct_change(12, fill_method=None) * 100


def fetch_fred_yoy(series_id, start='1999-01-01', trim='2000-01-01'):
    """Fetch FRED series, compute YoY%, drop NaN, trim to start date."""
    df = fetch_fred(series_id, start=start)
    df['yoy'] = yoy_pct(df)
    if trim:
        df = df.loc[trim:]
    return df['yoy'].dropna()


def fetch_fred_level(series_id, start='2000-01-01'):
    """Fetch FRED series as-is (already a rate/level, not an index)."""
    df = fetch_fred(series_id, start=start)
    return df['value'].dropna()


def fetch_quarterly_yoy(series_id, start='1999-01-01', trim='2000-01-01'):
    """Fetch quarterly FRED series, compute YoY (4-period), forward-fill to monthly."""
    df = fetch_fred(series_id, start=start)
    df['yoy'] = df['value'].pct_change(4, fill_method=None) * 100
    monthly = df['yoy'].resample('MS').ffill()
    if trim:
        monthly = monthly.loc[trim:]
    return monthly.dropna()


def fetch_quarterly_level(series_id, start='2000-01-01'):
    """Fetch quarterly FRED series as level, forward-fill to monthly."""
    df = fetch_fred(series_id, start=start)
    monthly = df['value'].resample('MS').ffill()
    return monthly.dropna()


def rolling_zscore(series, window=60):
    """Compute rolling z-score over a given window (months)."""
    mu = series.rolling(window, min_periods=24).mean()
    sigma = series.rolling(window, min_periods=24).std()
    return (series - mu) / sigma


def target_zscore(series, target=0.0, scale=1.0):
    """Z-score relative to a fixed target level."""
    return (series - target) / scale


# ============================================
# CHART STYLING HELPERS
# ============================================
def new_fig(figsize=(14, 8)):
    """Create figure with theme background."""
    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_facecolor(THEME['bg'])
    ax.set_facecolor(THEME['bg'])
    fig.subplots_adjust(top=0.88, bottom=0.08, left=0.06, right=0.94)
    return fig, ax


def style_dual_ax(ax1, ax2, c1, c2):
    """Apply full styling to a dual-axis chart."""
    style_ax(ax1, right_primary=False)
    ax1.grid(False)
    ax2.grid(False)
    for spine in ax2.spines.values():
        spine.set_color(THEME['spine'])
        spine.set_linewidth(0.5)
    ax1.tick_params(axis='both', which='both', length=0)
    ax1.tick_params(axis='y', labelcolor=c1, labelsize=10)
    ax1.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.1f}%'))
    ax2.tick_params(axis='both', which='both', length=0)
    ax2.tick_params(axis='y', labelcolor=c2, labelsize=10)
    ax2.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.1f}%'))
    ax1.yaxis.set_tick_params(which='both', right=False)
    ax2.yaxis.set_tick_params(which='both', left=False)


def style_single_ax(ax):
    """Apply full styling to a single-axis chart."""
    style_ax(ax, right_primary=True)
    ax.tick_params(axis='both', which='both', length=0)
    ax.tick_params(axis='y', labelcolor=THEME['fg'], labelsize=10)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.1f}%'))


def add_annotation_box(ax, text, x=0.52, y=0.92):
    """Add takeaway annotation box in dead space."""
    ax.text(x, y, text, transform=ax.transAxes,
            fontsize=10, color=THEME['fg'], ha='center', va='top',
            style='italic',
            bbox=dict(boxstyle='round,pad=0.5',
                      facecolor=THEME['bg'], edgecolor='#2389BB',
                      alpha=0.9))


def style_ax(ax, right_primary=True):
    """Style axes: all 4 spines at 0.5pt, grid off."""
    ax.grid(False)
    for spine in ['top', 'right', 'left', 'bottom']:
        ax.spines[spine].set_visible(True)
        ax.spines[spine].set_linewidth(0.5)
        ax.spines[spine].set_color(THEME['spine'])
    ax.tick_params(colors=THEME['fg'], labelsize=10)
    ax.xaxis.label.set_color(THEME['fg'])
    ax.yaxis.label.set_color(THEME['fg'])
    ax.title.set_color(THEME['fg'])
    if right_primary:
        ax.yaxis.tick_right()
        ax.yaxis.set_label_position('right')


def brand_fig(fig, title, subtitle=None, source=None):
    """Apply TT deck branding at figure level."""
    fig.patch.set_facecolor(THEME['bg'])

    OCEAN = '#2389BB'
    DUSK = '#FF6723'

    fig.text(0.03, 0.98, 'LIGHTHOUSE MACRO', fontsize=13,
             color=OCEAN, fontweight='bold', va='top')
    fig.text(0.97, 0.98, datetime.now().strftime('%B %d, %Y'),
             fontsize=11, color=THEME['muted'], ha='right', va='top')

    bar = fig.add_axes([0.03, 0.955, 0.94, 0.004])
    bar.axhspan(0, 1, 0, 0.67, color=OCEAN)
    bar.axhspan(0, 1, 0.67, 1.0, color=DUSK)
    bar.set_xlim(0, 1); bar.set_ylim(0, 1); bar.axis('off')

    bbar = fig.add_axes([0.03, 0.035, 0.94, 0.004])
    bbar.axhspan(0, 1, 0, 0.67, color=OCEAN)
    bbar.axhspan(0, 1, 0.67, 1.0, color=DUSK)
    bbar.set_xlim(0, 1); bbar.set_ylim(0, 1); bbar.axis('off')

    fig.text(0.97, 0.025, 'MACRO, ILLUMINATED.', fontsize=13,
             color=OCEAN, ha='right', va='top', style='italic', fontweight='bold')

    if source:
        date_str = datetime.now().strftime('%m.%d.%Y')
        fig.text(0.03, 0.022, f'Lighthouse Macro | {source}; {date_str}',
                 fontsize=9, color=THEME['muted'], ha='left', va='top', style='italic')

    fig.suptitle(title, fontsize=15, fontweight='bold', y=0.945,
                 color=THEME['fg'])
    if subtitle:
        fig.text(0.5, 0.895, subtitle, fontsize=14, ha='center',
                 color=OCEAN, style='italic')


def add_last_value_label(ax, y_data, color, fmt='{:.1f}%', side='right', fontsize=9, pad=0.3):
    """Add colored pill with bold white text on the axis edge."""
    if len(y_data) == 0:
        return
    last_y = float(y_data.iloc[-1]) if hasattr(y_data, 'iloc') else float(y_data[-1])
    label = fmt.format(last_y)
    pill = dict(boxstyle=f'round,pad={pad}', facecolor=color, edgecolor=color, alpha=0.95)
    if side == 'right':
        ax.annotate(label, xy=(1.0, last_y), xycoords=('axes fraction', 'data'),
                    fontsize=fontsize, fontweight='bold', color='white',
                    ha='left', va='center',
                    xytext=(6, 0), textcoords='offset points',
                    bbox=pill)
    else:
        ax.annotate(label, xy=(0.0, last_y), xycoords=('axes fraction', 'data'),
                    fontsize=fontsize, fontweight='bold', color='white',
                    ha='right', va='center',
                    xytext=(-6, 0), textcoords='offset points',
                    bbox=pill)


def add_recessions(ax, start_date=None):
    """Add recession shading."""
    for s, e in RECESSIONS:
        ts, te = pd.Timestamp(s), pd.Timestamp(e)
        if start_date and te < pd.Timestamp(start_date):
            continue
        ax.axvspan(ts, te, color=THEME['recession'],
                   alpha=THEME['recession_alpha'], zorder=0)


def set_xlim_to_data(ax, idx):
    """Set x limits with padding."""
    padding_left = pd.Timedelta(days=30)
    padding_right = pd.Timedelta(days=180)
    ax.set_xlim(idx.min() - padding_left, idx.max() + padding_right)


def legend_style():
    """Legend styling dict."""
    return dict(
        framealpha=0.95,
        facecolor=THEME['legend_bg'],
        edgecolor=THEME['spine'],
        labelcolor=THEME['legend_fg'],
    )


def save_fig(fig, filename):
    """Save figure to output directory."""
    border_color = COLORS['ocean']
    border_width = 4.0
    fig.patches.append(plt.Rectangle(
        (0, 0), 1, 1, transform=fig.transFigure,
        fill=False, edgecolor=border_color, linewidth=border_width,
        zorder=100, clip_on=False
    ))

    filepath = os.path.join(OUTPUT_DIR, filename)
    fig.savefig(filepath, dpi=200, bbox_inches='tight', pad_inches=0.025,
                facecolor=THEME['bg'], edgecolor='none')
    plt.close(fig)
    print(f'  Saved: {filepath}')
    return filepath


# ============================================
# CHART 1: Real DPI vs Real PCE (Income-Spending Gap) [Article Figure 1]
# ============================================
def chart_01():
    """Real DPI YoY vs Real PCE YoY: the income-spending gap."""
    print('\nChart 1: Real DPI vs Real PCE (Income vs Spending)...')

    dpi = fetch_fred_yoy('DSPIC96')
    pce = fetch_fred_yoy('PCEC96')

    # Trim to 2008+ to align with when Real PCE data is meaningful
    dpi = dpi.loc['2008-01-01':]
    pce = pce.loc['2008-01-01':]

    fig, ax = new_fig()

    ax.plot(dpi.index, dpi, color=THEME['primary'], linewidth=2.5,
            label=f'Real DPI YoY ({dpi.iloc[-1]:.1f}%)')
    ax.plot(pce.index, pce, color=THEME['secondary'], linewidth=2.5,
            label=f'Real PCE YoY ({pce.iloc[-1]:.1f}%)')

    # Shade the gap when spending exceeds income (unsustainable)
    common = pd.DataFrame({'dpi': dpi, 'pce': pce}).dropna()
    ax.fill_between(common.index, common['dpi'], common['pce'],
                    where=(common['pce'] > common['dpi']),
                    color=COLORS['dusk'], alpha=0.15, label='Spending > Income (unsustainable)')

    ax.axhline(0, color=COLORS['doldrums'], linewidth=0.8, alpha=0.5, linestyle='--')

    style_single_ax(ax)
    set_xlim_to_data(ax, dpi.index)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    add_last_value_label(ax, dpi, color=THEME['primary'], side='right')
    add_last_value_label(ax, pce, color=THEME['secondary'], side='right')
    add_recessions(ax)
    ax.legend(loc='upper left', **legend_style())

    dpi_last = dpi.iloc[-1]
    pce_last = pce.iloc[-1]
    gap = dpi_last - pce_last
    add_annotation_box(ax,
        f"Income-Spending Gap: {gap:+.1f}pp.\nWhen spending exceeds income, credit fills the gap.",
        x=0.52, y=0.92)

    brand_fig(fig, 'Real Disposable Income vs Real Consumer Spending',
              subtitle='Income vs Credit: Which is driving spending?',
              source='BEA via FRED')

    return save_fig(fig, 'chart_01_income_vs_spending.png')


# ============================================
# CHART 2: Real PCE Components (Goods vs Services vs Durables) [Article Figure 2]
# ============================================
def chart_02():
    """Real PCE Components: Durables, Nondurables, Services YoY."""
    print('\nChart 2: Real PCE Components...')

    # Real PCE total (monthly)
    pce_total = fetch_fred_yoy('PCEC96')
    # Real components (quarterly, use quarterly YoY with pct_change(4))
    durables = fetch_quarterly_yoy('PCDGCC96')
    nondurables = fetch_quarterly_yoy('PCNDGC96')
    services = fetch_quarterly_yoy('PCESVC96')

    # Start x-axis when quarterly series begin so all lines start together
    quarterly_start = max(durables.index.min(), nondurables.index.min(), services.index.min())
    pce_total = pce_total.loc[quarterly_start:]

    fig, ax = new_fig()

    ax.plot(pce_total.index, pce_total, color=THEME['primary'], linewidth=2.5,
            label=f'Real PCE Total ({pce_total.iloc[-1]:.1f}%)')
    ax.plot(durables.index, durables, color=THEME['secondary'], linewidth=2.0,
            label=f'Durables ({durables.iloc[-1]:.1f}%)', alpha=0.9)
    ax.plot(services.index, services, color=THEME['accent'], linewidth=2.0,
            label=f'Services ({services.iloc[-1]:.1f}%)', alpha=0.9)
    ax.plot(nondurables.index, nondurables, color=THEME['quaternary'], linewidth=1.5,
            label=f'Nondurables ({nondurables.iloc[-1]:.1f}%)', alpha=0.7)

    ax.axhline(0, color=COLORS['doldrums'], linewidth=0.8, alpha=0.5, linestyle='--')

    style_single_ax(ax)
    set_xlim_to_data(ax, pce_total.index)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    add_last_value_label(ax, pce_total, color=THEME['primary'], side='right')
    add_recessions(ax)
    ax.legend(loc='upper left', **legend_style())

    dur_last = durables.iloc[-1]
    svc_last = services.iloc[-1]
    add_annotation_box(ax,
        f"Durables at {dur_last:.1f}% YoY, Services at {svc_last:.1f}%.\nDurables turn first at cycle inflections.",
        x=0.52, y=0.92)

    brand_fig(fig, 'Personal Consumption Expenditures: Component Breakdown',
              subtitle='Durables lead the cycle, Services lag',
              source='BEA via FRED')

    return save_fig(fig, 'chart_02_pce_components.png')


# ============================================
# CHART 3: Durables Leading Services (Cyclical Canary) [Article Figure 3]
# ============================================
def chart_03():
    """Durables vs Services PCE YoY: durables lead at cycle turns."""
    print('\nChart 3: Durables Leading Services...')

    durables = fetch_quarterly_yoy('PCDGCC96')
    services = fetch_quarterly_yoy('PCESVC96')

    fig, ax1 = new_fig()
    ax2 = ax1.twinx()
    c_primary, c_secondary = THEME['primary'], THEME['secondary']

    # Services on LHS, Durables on RHS (durables more volatile)
    ax1.plot(services.index, services, color=c_secondary, linewidth=2.5,
             label=f'Services YoY ({services.iloc[-1]:.1f}%)')
    ax2.plot(durables.index, durables, color=c_primary, linewidth=2.5,
             label=f'Durables YoY ({durables.iloc[-1]:.1f}%)')

    ax1.axhline(0, color=COLORS['doldrums'], linewidth=0.8, alpha=0.5, linestyle='--')

    # Align both y-axes at zero
    def align_yaxis_zero(a1, a2):
        y1_min, y1_max = a1.get_ylim()
        y2_min, y2_max = a2.get_ylim()
        # Calculate ratios of negative to positive range
        r1 = abs(y1_min) / max(abs(y1_max), 1e-6)
        r2 = abs(y2_min) / max(abs(y2_max), 1e-6)
        # Use the larger ratio for both
        r = max(r1, r2)
        a1.set_ylim(bottom=-r * abs(y1_max), top=y1_max)
        a2.set_ylim(bottom=-r * abs(y2_max), top=y2_max)
    align_yaxis_zero(ax1, ax2)

    style_dual_ax(ax1, ax2, c_secondary, c_primary)
    set_xlim_to_data(ax1, durables.index)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    add_last_value_label(ax1, services, color=c_secondary, side='left')
    add_last_value_label(ax2, durables, color=c_primary, side='right')

    add_recessions(ax1)

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', **legend_style())

    dur_last = durables.iloc[-1]
    svc_last = services.iloc[-1]
    add_annotation_box(ax1,
        f"Durables ({dur_last:.1f}%) turn before Services ({svc_last:.1f}%).\nThe cyclical canary in the consumer coal mine.",
        x=0.52, y=0.98)

    brand_fig(fig, 'Durable Goods vs Services Spending',
              subtitle='Durables turn first at cycle inflections',
              source='BEA via FRED')

    return save_fig(fig, 'chart_03_durables_vs_services.png')


# ============================================
# CHART 4: Personal Saving Rate [Article Figure 4]
# ============================================
def chart_04():
    """Personal Saving Rate with threshold bands."""
    print('\nChart 4: Personal Saving Rate...')

    saving = fetch_fred_level('PSAVERT', start='2000-01-01')

    fig, ax = new_fig()
    c1 = THEME['primary']

    ax.plot(saving.index, saving, color=c1, linewidth=2.5,
            label=f'Saving Rate ({saving.iloc[-1]:.1f}%)')

    # Threshold lines
    ax.axhline(7.5, color=THEME['muted'], linewidth=1.0, linestyle='--', alpha=0.6)
    ax.axhline(5.5, color=COLORS['dusk'], linewidth=1.2, linestyle='--', alpha=0.7)
    ax.axhline(3.5, color=COLORS['venus'], linewidth=1.2, linestyle='--', alpha=0.7)

    # Threshold labels on left
    ax.text(saving.index[5], 7.7, 'Pre-pandemic normal (7.5%)',
            fontsize=8, color=THEME['muted'], va='bottom', alpha=0.7)
    ax.text(saving.index[5], 5.7, 'Stretched (5.5%)',
            fontsize=8, color=COLORS['dusk'], va='bottom', alpha=0.8)
    ax.text(saving.index[5], 3.7, 'Stressed (3.5%)',
            fontsize=8, color=COLORS['venus'], va='bottom', alpha=0.8)

    # Shade below 5.5% as warning zone
    ax.fill_between(saving.index, saving, 5.5,
                    where=(saving < 5.5), color=COLORS['dusk'], alpha=0.15)

    style_single_ax(ax)
    set_xlim_to_data(ax, saving.index)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    # Cap y-axis to avoid COVID spike dominating
    y_max = min(saving.max(), 35)
    ax.set_ylim(-1, y_max + 2)

    add_last_value_label(ax, saving, color=c1, side='right')
    add_recessions(ax)
    ax.legend(loc='upper left', **legend_style())

    sav_last = saving.iloc[-1]
    add_annotation_box(ax,
        f"Saving rate at {sav_last:.1f}%. Pre-pandemic normal: 7.5%.\nExcess savings depleted by Q1 2024 per SF Fed.",
        x=0.35, y=0.92)

    brand_fig(fig, 'Personal Saving Rate',
              subtitle='The fuel tank is running low',
              source='BEA via FRED')

    return save_fig(fig, 'chart_04_saving_rate.png')


# ============================================
# CHART 5: Consumer Credit Growth (Revolving vs Nonrevolving) [Article Figure 5]
# ============================================
def chart_05():
    """Consumer Credit Growth: Revolving vs Nonrevolving YoY."""
    print('\nChart 5: Consumer Credit Growth...')

    revolving = fetch_fred_yoy('REVOLSL')
    nonrevolving = fetch_fred_yoy('NONREVSL')

    fig, ax1 = new_fig()
    ax2 = ax1.twinx()
    c_rev, c_nonrev = THEME['primary'], THEME['secondary']

    # Revolving (Ocean) on LHS, Nonrevolving (Dusk) on RHS
    ax1.plot(revolving.index, revolving, color=c_rev, linewidth=2.5,
            label=f'Revolving (Credit Cards) ({revolving.iloc[-1]:.1f}%)')
    ax2.plot(nonrevolving.index, nonrevolving, color=c_nonrev, linewidth=2.0,
            label=f'Nonrevolving (Auto, Student) ({nonrevolving.iloc[-1]:.1f}%)')

    ax1.axhline(0, color=COLORS['doldrums'], linewidth=0.8, alpha=0.5, linestyle='--')

    # Align both y-axes at zero
    def align_yaxis_zero(a1, a2):
        y1_min, y1_max = a1.get_ylim()
        y2_min, y2_max = a2.get_ylim()
        r1 = abs(y1_min) / max(abs(y1_max), 1e-6)
        r2 = abs(y2_min) / max(abs(y2_max), 1e-6)
        r = max(r1, r2)
        a1.set_ylim(bottom=-r * abs(y1_max), top=y1_max)
        a2.set_ylim(bottom=-r * abs(y2_max), top=y2_max)
    align_yaxis_zero(ax1, ax2)

    style_dual_ax(ax1, ax2, c_rev, c_nonrev)
    set_xlim_to_data(ax1, revolving.index)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    add_last_value_label(ax1, revolving, color=c_rev, side='left')
    add_last_value_label(ax2, nonrevolving, color=c_nonrev, side='right')
    add_recessions(ax1)

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', **legend_style())

    rev_last = revolving.iloc[-1]
    add_annotation_box(ax1,
        f"Revolving credit growing {rev_last:.1f}% YoY.\nCredit substituting for depleted savings.",
        x=0.52, y=0.12)

    brand_fig(fig, 'Consumer Credit Growth: Revolving vs Nonrevolving',
              subtitle='Credit cards fill the gap when savings run dry',
              source='Federal Reserve G.19 via FRED')

    return save_fig(fig, 'chart_05_consumer_credit.png')


# ============================================
# CHART 6: Credit Card Delinquencies [Article Figure 6]
# ============================================
def chart_06():
    """Credit Card Delinquency Rate with threshold bands."""
    print('\nChart 6: Credit Card Delinquencies...')

    # DRCCLACBS is quarterly
    dq = fetch_fred_level('DRCCLACBS', start='2000-01-01')

    fig, ax = new_fig()
    c1 = THEME['primary']  # Ocean for the data line

    ax.plot(dq.index, dq, color=c1, linewidth=2.5, marker='o', markersize=3,
            label=f'CC Delinquency Rate ({dq.iloc[-1]:.1f}%)')

    # Threshold bands
    ax.axhline(2.5, color=THEME['quaternary'], linewidth=1.0, linestyle='--', alpha=0.6)
    ax.axhline(3.5, color=COLORS['dusk'], linewidth=1.2, linestyle='--', alpha=0.7)
    ax.axhline(5.0, color=COLORS['venus'], linewidth=1.2, linestyle='--', alpha=0.7)

    # Labels
    ax.text(dq.index[2], 2.6, 'Healthy (<2.5%)',
            fontsize=8, color=THEME['quaternary'], va='bottom', alpha=0.8)
    ax.text(dq.index[2], 3.6, 'Stressed (3.5%)',
            fontsize=8, color=COLORS['dusk'], va='bottom', alpha=0.8)
    ax.text(dq.index[2], 5.1, 'Crisis (5.0%)',
            fontsize=8, color=COLORS['venus'], va='bottom', alpha=0.8)

    # Shade above 2.5% as warning
    ax.fill_between(dq.index, dq, 2.5,
                    where=(dq > 2.5), color=COLORS['dusk'], alpha=0.15)

    style_single_ax(ax)
    set_xlim_to_data(ax, dq.index)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    add_last_value_label(ax, dq, color=c1, side='right')
    add_recessions(ax)
    ax.legend(loc='upper left', **legend_style())

    dq_last = dq.iloc[-1]
    add_annotation_box(ax,
        f"CC delinquency at {dq_last:.1f}%. Peaked ~3.2% Q2 2024.\nNY Fed Q4 2025: aggregate delinquency re-accelerating.",
        x=0.62, y=0.92)

    brand_fig(fig, 'Credit Card Delinquency Rate',
              subtitle='When savings run out, credit stress builds',
              source='Federal Reserve via FRED')

    return save_fig(fig, 'chart_06_cc_delinquency.png')


# ============================================
# CHART 7: UMich Consumer Sentiment [Article Figure 7]
# ============================================
def chart_07():
    """UMich Consumer Sentiment with threshold bands."""
    print('\nChart 7: UMich Consumer Sentiment...')

    umich = fetch_fred_level('UMCSENT', start='2000-01-01')

    fig, ax = new_fig()
    c1 = THEME['primary']

    ax.plot(umich.index, umich, color=c1, linewidth=2.5,
            label=f'UMich Sentiment ({umich.iloc[-1]:.0f})')

    # Threshold lines
    ax.axhline(65, color=COLORS['venus'], linewidth=1.2, linestyle='--', alpha=0.7)
    ax.axhline(80, color=COLORS['dusk'], linewidth=1.2, linestyle='--', alpha=0.7)
    ax.axhline(100, color=THEME['muted'], linewidth=1.0, linestyle='--', alpha=0.5)

    # Labels
    ax.text(umich.index[2], 66, 'Recessionary (<65)',
            fontsize=8, color=COLORS['venus'], va='bottom', alpha=0.8)
    ax.text(umich.index[2], 81, 'Weak (65-80)',
            fontsize=8, color=COLORS['dusk'], va='bottom', alpha=0.8)
    ax.text(umich.index[2], 101, 'Normal (>100)',
            fontsize=8, color=THEME['muted'], va='bottom', alpha=0.6)

    # Shade below 80 as warning
    ax.fill_between(umich.index, umich, 80,
                    where=(umich < 80), color=COLORS['dusk'], alpha=0.12)

    style_single_ax(ax)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.0f}'))
    set_xlim_to_data(ax, umich.index)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    add_last_value_label(ax, umich, color=c1, fmt='{:.0f}', side='right')
    add_recessions(ax)
    ax.legend(loc='upper left', **legend_style())

    u_last = umich.iloc[-1]
    add_annotation_box(ax,
        f"Sentiment at {u_last:.0f}.\nSustained readings below 65 historically\nprecede or coincide with recessions.",
        x=0.55, y=0.98)

    brand_fig(fig, 'University of Michigan Consumer Sentiment',
              subtitle='Confidence leads spending by 1-3 months',
              source='UMich via FRED')

    return save_fig(fig, 'chart_07_umich_sentiment.png')


# ============================================
# CHART 8: Aggregate Weekly Payrolls (Emp x Hours x Wages) YoY [Article Figure 8]
# ============================================
def chart_08():
    """Aggregate Weekly Payrolls: Emp x Hours x AHE, YoY."""
    print('\nChart 8: Aggregate Payrolls...')

    emp = fetch_fred('USPRIV', start='1999-01-01')
    hours = fetch_fred('AWHAETP', start='1999-01-01')
    ahe = fetch_fred('CES0500000003', start='1999-01-01')

    # Compute aggregate payroll index
    agg = pd.DataFrame({
        'emp': emp['value'],
        'hours': hours['value'],
        'ahe': ahe['value'],
    }).dropna()
    agg['payroll'] = agg['emp'] * agg['hours'] * agg['ahe']
    agg['yoy'] = agg['payroll'].pct_change(12) * 100
    agg = agg.loc['2000-01-01':].dropna()

    # Also compute real payroll (deflate by CPI)
    cpi = fetch_fred('CPIAUCSL', start='1999-01-01')
    # Resample to monthly + ffill to handle any missing observations (e.g. Oct 2025)
    cpi_monthly = cpi['value'].resample('MS').last().ffill()
    cpi_yoy = cpi_monthly.pct_change(12) * 100
    cpi_yoy = cpi_yoy.loc['2000-01-01':].dropna()

    # Align dates
    common = pd.DataFrame({'nominal': agg['yoy'], 'cpi': cpi_yoy}).dropna()
    common['real'] = common['nominal'] - common['cpi']

    fig, ax = new_fig()

    ax.plot(common.index, common['nominal'], color=THEME['primary'], linewidth=2.5,
            label=f'Nominal Payrolls YoY ({common["nominal"].iloc[-1]:.1f}%)')
    ax.plot(common.index, common['real'], color=THEME['secondary'], linewidth=2.0,
            label=f'Real Payrolls YoY ({common["real"].iloc[-1]:.1f}%)', alpha=0.9)

    ax.axhline(0, color=COLORS['doldrums'], linewidth=0.8, alpha=0.5, linestyle='--')
    ax.axhline(3, color=COLORS['venus'], linewidth=1.0, alpha=0.6, linestyle='--')
    ax.text(common.index[5], 3.2, 'Nominal stagnation (3%)',
            fontsize=8, color=COLORS['venus'], va='bottom', alpha=0.8)

    style_single_ax(ax)
    set_xlim_to_data(ax, common.index)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    add_last_value_label(ax, common['nominal'], color=THEME['primary'], side='right')
    add_last_value_label(ax, common['real'], color=THEME['secondary'], side='left')
    add_recessions(ax)
    ax.legend(loc='upper left', **legend_style())

    nom_last = common['nominal'].iloc[-1]
    real_last = common['real'].iloc[-1]
    add_annotation_box(ax,
        f"Aggregate payrolls: {nom_last:.1f}% nominal, {real_last:.1f}% real.\nEmployment x Hours x Wages = total income.",
        x=0.55, y=0.98)

    brand_fig(fig, 'Aggregate Weekly Payrolls (Employment x Hours x Wages)',
              subtitle='The paycheck reality behind consumer spending',
              source='BLS via FRED')

    return save_fig(fig, 'chart_08_aggregate_payrolls.png')


# ============================================
# CHART 9: Household Debt Service Ratio [Article Figure 9]
# ============================================
def chart_09():
    """Household Debt Service Ratio with threshold bands."""
    print('\nChart 9: Debt Service Ratio...')

    # TDSP is quarterly
    dsr = fetch_fred_level('TDSP', start='2000-01-01')

    fig, ax = new_fig()
    c1 = THEME['primary']

    ax.plot(dsr.index, dsr, color=c1, linewidth=2.5, marker='o', markersize=2,
            label=f'Debt Service Ratio ({dsr.iloc[-1]:.1f}%)')

    # Threshold bands
    ax.axhline(10, color=COLORS['dusk'], linewidth=1.2, linestyle='--', alpha=0.7)
    ax.axhline(13, color=COLORS['venus'], linewidth=1.2, linestyle='--', alpha=0.7)

    ax.text(dsr.index[2], 10.15, 'Stretched (10%)',
            fontsize=8, color=COLORS['dusk'], va='bottom', alpha=0.8)
    ax.text(dsr.index[2], 13.15, 'Stressed (13%)',
            fontsize=8, color=COLORS['venus'], va='bottom', alpha=0.8)

    style_single_ax(ax)
    set_xlim_to_data(ax, dsr.index)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    add_last_value_label(ax, dsr, color=c1, side='right')
    add_recessions(ax)
    ax.legend(loc='upper left', **legend_style())

    dsr_last = dsr.iloc[-1]
    add_annotation_box(ax,
        f"DSR at {dsr_last:.1f}% of disposable income.\nRising rates push payments higher even\nwithout new borrowing.",
        x=0.55, y=0.92)

    brand_fig(fig, 'Household Debt Service Ratio',
              subtitle='Payment burden as share of disposable income',
              source='Federal Reserve via FRED')

    return save_fig(fig, 'chart_09_debt_service_ratio.png')


# ============================================
# CHART 10: Household Net Worth / DPI Ratio [Article Figure 10]
# ============================================
def chart_10():
    """Household Net Worth to Disposable Income ratio."""
    print('\nChart 10: Household Net Worth / DPI...')

    # Both quarterly
    nw = fetch_fred('BOGZ1FL192090005Q', start='2000-01-01')
    dpi_q = fetch_fred('DPI', start='2000-01-01')

    # Align quarterly data
    nw_q = nw['value'].resample('QS').last().dropna()
    dpi_q_resampled = dpi_q['value'].resample('QS').last().dropna()

    # BOGZ1FL192090005Q is in millions, DPI is in billions (SAAR)
    # Convert NW from millions to billions, then ratio = NW / DPI
    # Result is a multiple (e.g., 7.5x meaning net worth = 7.5x annual income)
    common = pd.DataFrame({'nw': nw_q / 1000, 'dpi': dpi_q_resampled}).dropna()
    common['ratio'] = (common['nw'] / common['dpi'])

    # Override latest value with Fed Z.1 January 2026 direct release ($181.6T NW)
    # FRED lags the primary release; Z.1 shows 7.9x vs FRED's 7.5x
    if common.index[-1] >= pd.Timestamp('2025-07-01'):
        common.loc[common.index[-1], 'ratio'] = 7.9

    fig, ax = new_fig()
    c1 = THEME['primary']

    ax.plot(common.index, common['ratio'], color=c1, linewidth=2.5, marker='o', markersize=2,
            label=f'Net Worth / DPI ({common["ratio"].iloc[-1]:.1f}x)')

    # Historical average
    avg = common['ratio'].mean()
    ax.axhline(avg, color=THEME['muted'], linewidth=1.0, linestyle='--', alpha=0.5)
    ax.text(common.index[2], avg + 0.05, f'Average ({avg:.1f}x)',
            fontsize=8, color=THEME['muted'], va='bottom', alpha=0.6)

    style_single_ax(ax)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.1f}x'))
    set_xlim_to_data(ax, common.index)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    add_last_value_label(ax, common['ratio'], color=c1, fmt='{:.1f}x', side='right')
    add_recessions(ax)
    ax.legend(loc='upper left', **legend_style())

    ratio_last = common['ratio'].iloc[-1]
    add_annotation_box(ax,
        f"NW/DPI at {ratio_last:.1f}x.\nAggregate looks strong, but top 10% hold ~68%\nof wealth. Bottom 50% have negative net worth.",
        x=0.52, y=0.98)

    brand_fig(fig, 'Household Net Worth to Disposable Income',
              subtitle='Aggregate wealth masks distributional reality',
              source='Federal Reserve Z.1 via FRED')

    return save_fig(fig, 'chart_10_net_worth_dpi.png')


# ============================================
# CHART 11: Consumer Composite Index (CCI) [Article Figure 11]
# ============================================
def chart_11():
    """Consumer Composite Index with regime bands."""
    print('\nChart 11: Consumer Composite Index (CCI)...')

    # Fetch components (7 total, matching Pillar 5 doc)
    pce = fetch_fred_yoy('PCEC96')                          # Real PCE YoY
    saving = fetch_fred_level('PSAVERT', start='1999-01-01')  # Saving Rate
    cc_dq = fetch_quarterly_level('DRCCLACBS', start='1999-01-01')  # CC Delinquency (quarterly, ffill)
    umich = fetch_fred_level('UMCSENT', start='1999-01-01')  # UMich (proxy for CB Expectations)
    dpi = fetch_fred_yoy('DSPIC96')                          # Real DPI YoY
    dsr = fetch_quarterly_level('TDSP', start='1999-01-01')   # Debt Service Ratio (quarterly, ffill)
    rsxfs = fetch_fred_yoy('RSXFS')                          # Retail Sales Control Group YoY (card spending proxy)

    # Build DataFrame aligned on common dates
    start_date = '2002-01-01'
    cci_df = pd.DataFrame({
        'pce': pce,
        'saving': saving,
        'cc_dq': cc_dq,
        'umich': umich,
        'dpi': dpi,
        'dsr': dsr,
        'rsxfs': rsxfs,
    })
    cci_df = cci_df.loc[start_date:].dropna()

    # Z-scores relative to expansion norms
    z_pce = target_zscore(cci_df['pce'], target=2.5, scale=2.0)
    z_saving = target_zscore(cci_df['saving'], target=7.0, scale=3.0)
    z_cc_dq = target_zscore(cci_df['cc_dq'], target=3.0, scale=1.5) * -1   # Inverted
    z_umich = target_zscore(cci_df['umich'], target=85.0, scale=15.0)
    z_dpi = target_zscore(cci_df['dpi'], target=2.5, scale=2.0)
    z_dsr = target_zscore(cci_df['dsr'], target=10.0, scale=2.0) * -1       # Inverted
    z_rsxfs = target_zscore(cci_df['rsxfs'], target=3.0, scale=3.0)

    # CCI formula: 7 components, weights validated via backtest (cci_backtest.py)
    # PCE & Saving anchor the composite (highest forward PCE correlation)
    # RSXFS (retail control) is 3rd most predictive, replaces dropped card spending
    # CC_DQ & UMich downweighted (low empirical predictive power)
    # Weights: PCE 0.25, Saving 0.20, RSXFS 0.15, DPI 0.10, DSR 0.10, CC_DQ 0.10, UMich 0.10
    cci = (0.25 * z_pce + 0.20 * z_saving + 0.15 * z_rsxfs
           + 0.10 * z_dpi + 0.10 * z_dsr + 0.10 * z_cc_dq + 0.10 * z_umich)
    cci = cci.dropna()

    fig, ax = new_fig()
    c1 = THEME['primary']

    # Regime bands
    ax.axhspan(1.0, 2.5, color=COLORS['starboard'], alpha=0.15)   # Consumer Boom
    ax.axhspan(0.5, 1.0, color=COLORS['sea'], alpha=0.15)         # Healthy
    ax.axhspan(-0.5, 0.5, color=COLORS['doldrums'], alpha=0.10)   # Neutral/Fatigued
    ax.axhspan(-1.0, -0.5, color=COLORS['dusk'], alpha=0.15)      # Stressed
    ax.axhspan(-2.5, -1.0, color=COLORS['port'], alpha=0.20)      # Crisis

    ax.plot(cci.index, cci, color=c1, linewidth=2.5, label=f'CCI ({cci.iloc[-1]:.2f})')
    ax.axhline(0, color=THEME['muted'], linewidth=0.8, alpha=0.5, linestyle='--')

    style_single_ax(ax)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.1f}'))
    ax.tick_params(axis='both', which='both', length=0)
    set_xlim_to_data(ax, cci.index)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    add_last_value_label(ax, cci, color=c1, fmt='{:.2f}', side='right')

    # Regime labels on left
    ax.text(0.14, 1.5, 'BOOM', transform=ax.get_yaxis_transform(),
            fontsize=9, color=COLORS['starboard'], va='center', ha='left', fontweight='bold', alpha=0.8)
    ax.text(0.14, 0.75, 'HEALTHY', transform=ax.get_yaxis_transform(),
            fontsize=9, color=COLORS['sea'], va='center', ha='left', fontweight='bold', alpha=0.8)
    ax.text(0.14, 0.0, 'NEUTRAL', transform=ax.get_yaxis_transform(),
            fontsize=9, color=THEME['muted'], va='center', ha='left', fontweight='bold', alpha=0.6)
    ax.text(0.14, -0.75, 'STRESSED', transform=ax.get_yaxis_transform(),
            fontsize=9, color=COLORS['dusk'], va='center', ha='left', fontweight='bold', alpha=0.8)
    ax.text(0.14, -1.5, 'CRISIS', transform=ax.get_yaxis_transform(),
            fontsize=9, color=COLORS['port'], va='center', ha='left', fontweight='bold', alpha=0.8)

    add_recessions(ax, start_date=start_date)
    ax.legend(loc='upper left', **legend_style())

    cci_last = cci.iloc[-1]
    if cci_last > 1.0: regime = "Consumer Boom"
    elif cci_last > 0.5: regime = "Healthy"
    elif cci_last > -0.5: regime = "Neutral/Fatigued"
    elif cci_last > -1.0: regime = "Stressed"
    else: regime = "Crisis"

    add_annotation_box(ax,
        f"CCI at {cci_last:.2f}: {regime} regime.\nPCE, savings, credit, confidence, income, debt service.",
        x=0.35, y=0.92)

    brand_fig(fig, 'Consumer Composite Index (CCI)',
              subtitle='Synthesizing consumer health into one regime indicator',
              source='FRED, BEA, Federal Reserve, UMich')

    return save_fig(fig, 'chart_11_cci_composite.png')


# ============================================
# MAIN
# ============================================
CHART_MAP = {
    1: chart_01,
    2: chart_02,
    3: chart_03,
    4: chart_04,
    5: chart_05,
    6: chart_06,
    7: chart_07,
    8: chart_08,
    9: chart_09,
    10: chart_10,
    11: chart_11,
}


def main():
    parser = argparse.ArgumentParser(description='Generate Consumer educational charts')
    parser.add_argument('--chart', type=int, help='Chart number to generate (1-11)')
    parser.add_argument('--theme', default='both', choices=['dark', 'white', 'both'],
                        help='Theme to generate')
    parser.add_argument('--all', action='store_true', help='Generate all charts')
    args = parser.parse_args()

    if args.all:
        charts_to_gen = sorted(CHART_MAP.keys())
    elif args.chart:
        charts_to_gen = [args.chart]
    else:
        charts_to_gen = [1]

    themes_to_gen = ['dark', 'white'] if args.theme == 'both' else [args.theme]

    for mode in themes_to_gen:
        set_theme(mode)
        print(f'\n=== Generating {mode.upper()} theme ===')
        for chart_num in charts_to_gen:
            if chart_num not in CHART_MAP:
                print(f'Chart {chart_num} not implemented yet.')
                continue
            try:
                CHART_MAP[chart_num]()
            except Exception as e:
                print(f'  Error generating chart {chart_num}: {e}')
                import traceback
                traceback.print_exc()

    print('\nDone.')


if __name__ == '__main__':
    main()
