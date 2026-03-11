#!/usr/bin/env python3
"""
Generate Charts for Educational Series: Post 9 - Financial Conditions (Pillar 9)
================================================================================
12 charts covering: HY OAS percentile distribution, spread mispricing gap,
yield curve dis-inversion clock, NFCI decomposition, SLOOS vs loan growth,
transmission gap, complacency gap, delinquencies vs spreads, default risk
premium regime, Credit-Labor Gap (CLG), financial cascade infographic, and
FCI regime map with component tug-of-war.

Generates BOTH white and dark theme versions.

Usage:
    python financial_edu_charts.py --chart 1
    python financial_edu_charts.py --chart 1 --theme dark
    python financial_edu_charts.py --all
"""

import os
import argparse
import time
import ssl
import certifi
import sqlite3
from datetime import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
from matplotlib.ticker import FuncFormatter
from fredapi import Fred

# Fix SSL certificate issue
os.environ['SSL_CERT_FILE'] = certifi.where()
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()

# ============================================
# PATHS & CONFIG
# ============================================
BASE_PATH = '/Users/bob/LHM'
OUTPUT_BASE = f'{BASE_PATH}/Outputs/Educational_Charts/Financial_Post_9'
DB_PATH = f'{BASE_PATH}/Data/databases/Lighthouse_Master.db'
ICON_PATH = f'{BASE_PATH}/Brand/icon_transparent_128.png'

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
    'fog': '#D1D1D1',
}

RECESSIONS = [
    ('1953-07-01', '1954-05-01'),
    ('1957-08-01', '1958-04-01'),
    ('1960-04-01', '1961-02-01'),
    ('1969-12-01', '1970-11-01'),
    ('1973-11-01', '1975-03-01'),
    ('1980-01-01', '1980-07-01'),
    ('1981-07-01', '1982-11-01'),
    ('1990-07-01', '1991-03-01'),
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
def fetch_fred(series_id, start='1950-01-01'):
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


def fetch_db(series_id, start='1950-01-01'):
    """Fetch a series from the master DB."""
    cache_key = f"db_{series_id}_{start}"
    if cache_key in _DATA_CACHE:
        return _DATA_CACHE[cache_key].copy()

    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql(
        "SELECT date, value FROM observations WHERE series_id = ? AND date >= ? ORDER BY date",
        conn, params=(series_id, start)
    )
    conn.close()

    if df.empty:
        return pd.DataFrame(columns=['value'])

    df['date'] = pd.to_datetime(df['date'])
    df = df.set_index('date')
    _DATA_CACHE[cache_key] = df.copy()
    return df


def fetch_fred_level(series_id, start='1950-01-01'):
    """Fetch FRED series as-is (already a rate/level)."""
    df = fetch_fred(series_id, start=start)
    return df['value'].dropna()


def fetch_db_level(series_id, start='1950-01-01'):
    """Fetch DB series as-is."""
    df = fetch_db(series_id, start=start)
    if df.empty:
        return pd.Series(dtype=float)
    return df['value'].dropna()


def fetch_db_index(index_id, start='1950-01-01'):
    """Fetch a series from lighthouse_indices table."""
    cache_key = f"dbidx_{index_id}_{start}"
    if cache_key in _DATA_CACHE:
        return _DATA_CACHE[cache_key].copy()

    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql(
        "SELECT date, value FROM lighthouse_indices "
        "WHERE index_id = ? AND date >= ? ORDER BY date",
        conn, params=(index_id, start)
    )
    conn.close()

    if df.empty:
        return pd.Series(dtype=float)

    df['date'] = pd.to_datetime(df['date'])
    df = df.set_index('date')
    s = df['value'].dropna()
    _DATA_CACHE[cache_key] = s.copy()
    return s


def fetch_quarterly_level(series_id, start='1950-01-01'):
    """Fetch quarterly FRED series as level, forward-fill to monthly."""
    df = fetch_fred(series_id, start=start)
    monthly = df['value'].resample('MS').ffill()
    return monthly.dropna()


def rolling_zscore(series, window=60):
    """Compute rolling z-score over a given window (months)."""
    mu = series.rolling(window, min_periods=24).mean()
    sigma = series.rolling(window, min_periods=24).std()
    return (series - mu) / sigma


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


def new_fig_panels(nrows=2, height_ratios=None, figsize=(14, 10)):
    """Create multi-panel figure with theme background."""
    if height_ratios is None:
        height_ratios = [3, 1]
    fig, axes = plt.subplots(nrows, 1, figsize=figsize,
                             gridspec_kw={'height_ratios': height_ratios,
                                          'hspace': 0.25})
    fig.patch.set_facecolor(THEME['bg'])
    for ax in axes:
        ax.set_facecolor(THEME['bg'])
    fig.subplots_adjust(top=0.88, bottom=0.08, left=0.06, right=0.94)
    return fig, axes


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
    ax2.tick_params(axis='both', which='both', length=0)
    ax2.tick_params(axis='y', labelcolor=c2, labelsize=10)
    ax1.yaxis.set_tick_params(which='both', right=False)
    ax2.yaxis.set_tick_params(which='both', left=False)


def style_single_ax(ax, fmt='{:.1f}%'):
    """Apply full styling to a single-axis chart."""
    style_ax(ax, right_primary=True)
    ax.tick_params(axis='both', which='both', length=0)
    ax.tick_params(axis='y', labelcolor=THEME['fg'], labelsize=10)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: fmt.format(x)))


def add_annotation_box(ax, text, x=0.50, y=0.15):
    """Add takeaway annotation box at specified position.

    Default is bottom-center which avoids data on most time series charts.
    Each chart caller should pass x,y explicitly based on where the dead space is.
    """
    box_fc = '#2389BB'
    txt_color = '#ffffff'
    ax.text(x, y, text, transform=ax.transAxes,
            fontsize=11, fontweight='bold', color=txt_color, ha='center', va='top',
            style='italic',
            bbox=dict(boxstyle='round,pad=0.5',
                      facecolor=box_fc, edgecolor='#00BBFF',
                      linewidth=2.0,
                      alpha=1.0))


def brand_fig(fig, title, subtitle=None, source=None, data_date=None):
    """Apply LHM branding at figure level."""
    fig.patch.set_facecolor(THEME['bg'])

    OCEAN = '#2389BB'
    DUSK = '#FF6723'

    fig.text(0.035, 0.98, 'LIGHTHOUSE MACRO', fontsize=13,
             color=OCEAN, fontweight='bold', va='top')
    fig.text(0.97, 0.98, datetime.now().strftime('%B %d, %Y'),
             fontsize=11, color=THEME['muted'], ha='right', va='top')

    bar = fig.add_axes([0.03, 0.955, 0.94, 0.004])
    bar.axhspan(0, 1, 0, 0.67, color=OCEAN)
    bar.axhspan(0, 1, 0.67, 1.0, color=DUSK)
    bar.set_xlim(0, 1); bar.set_ylim(0, 1); bar.axis('off')

    # Lighthouse icon
    if os.path.exists(ICON_PATH):
        icon_img = mpimg.imread(ICON_PATH)
        icon_w = 0.018
        icon_aspect = icon_img.shape[0] / icon_img.shape[1]
        fig_aspect = fig.get_figwidth() / fig.get_figheight()
        icon_h = icon_w * icon_aspect * fig_aspect
        icon_ax = fig.add_axes([0.012, 0.985 - icon_h, icon_w, icon_h])
        icon_ax.imshow(icon_img, aspect='equal')
        icon_ax.axis('off')

    bbar = fig.add_axes([0.03, 0.035, 0.94, 0.004])
    bbar.axhspan(0, 1, 0, 0.67, color=OCEAN)
    bbar.axhspan(0, 1, 0.67, 1.0, color=DUSK)
    bbar.set_xlim(0, 1); bbar.set_ylim(0, 1); bbar.axis('off')

    fig.text(0.97, 0.025, 'MACRO, ILLUMINATED.', fontsize=13,
             color=OCEAN, ha='right', va='top', style='italic', fontweight='bold')

    if source:
        pull_str = datetime.now().strftime('%m.%d.%Y')
        if data_date is not None:
            if isinstance(data_date, str):
                data_date = pd.Timestamp(data_date)
            data_str = data_date.strftime('%m.%d.%Y')
            fig.text(0.03, 0.022,
                     f'Lighthouse Macro | {source} | Data thru {data_str} | Pulled {pull_str}',
                     fontsize=9, color=THEME['muted'], ha='left', va='top', style='italic')
        else:
            fig.text(0.03, 0.022, f'Lighthouse Macro | {source}; {pull_str}',
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
        edgecolor='#00BBFF' if THEME['mode'] == 'dark' else THEME['spine'],
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


def align_yaxis_zero(a1, a2):
    """Align both y-axes at zero for dual-axis charts."""
    y1_min, y1_max = a1.get_ylim()
    y2_min, y2_max = a2.get_ylim()
    r1 = abs(y1_min) / max(abs(y1_max), 1e-6)
    r2 = abs(y2_min) / max(abs(y2_max), 1e-6)
    r = max(r1, r2)
    a1.set_ylim(bottom=-r * abs(y1_max), top=y1_max)
    a2.set_ylim(bottom=-r * abs(y2_max), top=y2_max)


# ============================================
# CHART 1: HY OAS Percentile Distribution [Figure 1]
# ============================================
def chart_01():
    """High-Yield Credit Spreads with 20-year rolling percentile bands."""
    print('\nChart 1: HY OAS Percentile Distribution...')

    hy = fetch_db_level('BAMLH0A0HYM2', start='1997-01-01')
    if len(hy) == 0:
        hy = fetch_fred_level('BAMLH0A0HYM2', start='1997-01-01')

    # BAMLH0A0HYM2 is in percentage points (e.g., 3.50 = 350 bps). Multiply by 100 for bps.
    hy_bps = hy * 100

    # 20-year rolling window (~5040 trading days)
    win = 5040
    p10 = hy_bps.rolling(win, min_periods=1000).quantile(0.10)
    p25 = hy_bps.rolling(win, min_periods=1000).quantile(0.25)
    p75 = hy_bps.rolling(win, min_periods=1000).quantile(0.75)
    p90 = hy_bps.rolling(win, min_periods=1000).quantile(0.90)

    # Current percentile
    last_val = hy_bps.iloc[-1]
    pctile = (hy_bps < last_val).sum() / len(hy_bps) * 100

    fig, ax = new_fig()

    # Percentile bands
    ax.fill_between(hy_bps.index, p10, p25, color=COLORS['port'], alpha=0.15,
                    label='10th-25th percentile')
    ax.fill_between(hy_bps.index, p25, p75, color=COLORS['fog'], alpha=0.10,
                    label='25th-75th percentile')
    ax.fill_between(hy_bps.index, p75, p90, color=COLORS['port'], alpha=0.15,
                    label='75th-90th percentile')

    # Main line on top
    ax.plot(hy_bps.index, hy_bps, color=THEME['primary'], linewidth=2.0,
            label=f'HY OAS ({last_val:.0f} bps)', zorder=5)

    style_single_ax(ax, fmt='{:.0f}')
    set_xlim_to_data(ax, hy_bps.index)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    add_last_value_label(ax, hy_bps, color=THEME['primary'], fmt='{:.0f}', side='right')
    add_recessions(ax, start_date='1997-01-01')
    ax.legend(loc='upper right', fontsize=9, **legend_style())

    add_annotation_box(ax,
        f"Current: {last_val:.0f} bps ({pctile:.0f}th percentile)\n"
        f"20-year rolling distribution context.\n"
        f"Percentile tells you where we stand in history.",
        x=0.82, y=0.45)

    brand_fig(fig, 'High-Yield Credit Spreads',
              subtitle='ICE BofA HY OAS | Percentile Distribution (20-Year Rolling)',
              source='ICE BofA via FRED',
              data_date=hy_bps.index[-1])

    return save_fig(fig, 'chart_01_hy_oas_percentile.png')


# ============================================
# CHART 2: Spread Mispricing Gap [Figure 2]
# ============================================
def chart_02():
    """HY OAS vs All-Loan Delinquency Rate (12-month forward) showing mispricing."""
    print('\nChart 2: Spread Mispricing Gap...')

    hy = fetch_db_level('BAMLH0A0HYM2', start='1997-01-01')
    if len(hy) == 0:
        hy = fetch_fred_level('BAMLH0A0HYM2', start='1997-01-01')
    hy_bps = hy * 100

    # All-loan delinquency rate
    delinq = fetch_db_level('DRALACBS', start='1991-01-01')
    if len(delinq) == 0:
        delinq = fetch_fred_level('DRALACBS', start='1991-01-01')

    # Shift delinquency data BACK 12 months (so it aligns with when spreads "should" have priced it)
    delinq_fwd = delinq.copy()
    delinq_fwd.index = delinq_fwd.index - pd.DateOffset(months=12)

    # Filter to common date range starting 1997
    start = '1997-01-01'
    hy_bps = hy_bps[hy_bps.index >= start]
    delinq_fwd = delinq_fwd[delinq_fwd.index >= start]

    fig, ax1 = new_fig()
    ax2 = ax1.twinx()
    c1, c2 = THEME['primary'], THEME['secondary']

    ax1.plot(hy_bps.index, hy_bps, color=c1, linewidth=2.5,
             label=f'HY OAS ({hy_bps.iloc[-1]:.0f} bps)')
    ax2.plot(delinq_fwd.index, delinq_fwd, color=c2, linewidth=2.0,
             label=f'All-Loan Delinq. 12M Fwd ({delinq_fwd.iloc[-1]:.2f}%)')

    style_dual_ax(ax1, ax2, c1, c2)
    ax1.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.0f}'))
    ax2.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.1f}%'))
    set_xlim_to_data(ax1, hy_bps.index)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    add_last_value_label(ax1, hy_bps, color=c1, fmt='{:.0f}', side='left')
    add_last_value_label(ax2, delinq_fwd, color=c2, fmt='{:.2f}%', side='right')
    add_recessions(ax1, start_date='1997-01-01')

    # Annotate mispricing episodes
    ax1.annotate('2006-07:\nSpreads tight,\ndelinquencies rising',
                 xy=(pd.Timestamp('2007-01-01'), 300), fontsize=8,
                 color=COLORS['venus'], fontweight='bold',
                 ha='center', va='bottom',
                 arrowprops=dict(arrowstyle='->', color=COLORS['venus'], lw=1.5),
                 xytext=(pd.Timestamp('2005-01-01'), 700))
    ax1.annotate('2018-19:\nLate-cycle\ncomplacency',
                 xy=(pd.Timestamp('2018-10-01'), 400), fontsize=8,
                 color=COLORS['venus'], fontweight='bold',
                 ha='center', va='bottom',
                 arrowprops=dict(arrowstyle='->', color=COLORS['venus'], lw=1.5),
                 xytext=(pd.Timestamp('2016-06-01'), 800))

    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax1.legend(h1 + h2, l1 + l2, loc='upper right', fontsize=9, **legend_style())

    brand_fig(fig, 'The Spread Mispricing Gap',
              subtitle='HY OAS vs. All-Loan Delinquency Rate (12-Month Forward)',
              source='ICE BofA, Federal Reserve via FRED',
              data_date=hy_bps.index[-1])

    return save_fig(fig, 'chart_02_spread_mispricing.png')


# ============================================
# CHART 3: Yield Curve Dis-Inversion Clock [Figure 3]
# ============================================
def chart_03():
    """10Y-2Y spread with annotated dis-inversion to recession lags."""
    print('\nChart 3: Yield Curve Dis-Inversion Clock...')

    curve = fetch_db_level('T10Y2Y', start='1976-01-01')
    if len(curve) == 0:
        curve = fetch_fred_level('T10Y2Y', start='1976-01-01')

    fig, ax = new_fig()

    ax.plot(curve.index, curve, color=THEME['primary'], linewidth=1.8, label='10Y-2Y Spread')

    # Zero line
    ax.axhline(0, color=COLORS['fog'], linewidth=1.2, linestyle='--', alpha=0.7)

    # Fill: green above 0, red below 0
    ax.fill_between(curve.index, 0, curve,
                    where=(curve >= 0),
                    color=COLORS['starboard'], alpha=0.08)
    ax.fill_between(curve.index, 0, curve,
                    where=(curve < 0),
                    color=COLORS['port'], alpha=0.12)

    style_single_ax(ax, fmt='{:.1f}%')
    set_xlim_to_data(ax, curve.index)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("'%y"))
    add_last_value_label(ax, curve, color=THEME['primary'], fmt='{:.2f}%', side='right')
    add_recessions(ax, start_date='1976-01-01')

    # Annotated dis-inversion episodes with arrows to recession starts
    annotations = [
        ('1989-06', '1990-07', '13 months'),
        ('1998-06', '2001-03', '33 months\n(long lag)'),
        ('2007-06', '2007-12', '6 months'),
        ('2019-08', '2020-02', '6 months'),
    ]

    arrow_color = COLORS['venus']
    for i, (disinv, rec_start, label) in enumerate(annotations):
        disinv_dt = pd.Timestamp(disinv)
        rec_dt = pd.Timestamp(rec_start)
        # Place annotation above the zero line
        y_offset = 1.5 + (i % 2) * 0.8
        ax.annotate(f'{disinv[:7]} dis-inv.\n{chr(8594)} {rec_start[:7]} rec.\n({label})',
                    xy=(disinv_dt, 0), fontsize=7,
                    color=arrow_color, fontweight='bold',
                    ha='center', va='bottom',
                    arrowprops=dict(arrowstyle='->', color=arrow_color, lw=1.2),
                    xytext=(disinv_dt, y_offset))

    # Current dis-inversion
    ax.annotate('2024-09 dis-inv.\nClock running...',
                xy=(pd.Timestamp('2024-09-01'), 0), fontsize=8,
                color=COLORS['venus'], fontweight='bold',
                ha='center', va='bottom',
                arrowprops=dict(arrowstyle='->', color=COLORS['venus'], lw=1.5),
                xytext=(pd.Timestamp('2024-09-01'), 1.8))

    ax.legend(loc='lower left', fontsize=9, **legend_style())

    brand_fig(fig, 'The Yield Curve Dis-Inversion Clock',
              subtitle='10Y-2Y Spread | Every Dis-Inversion Has Been Followed by Recession',
              source='US Treasury via FRED',
              data_date=curve.index[-1])

    return save_fig(fig, 'chart_03_disinversion_clock.png')


# ============================================
# CHART 4: NFCI Subcomponent Decomposition [Figure 4]
# ============================================
def chart_04():
    """NFCI and subindices: Credit, Leverage, Risk."""
    print('\nChart 4: NFCI Decomposition...')

    nfci = fetch_db_level('NFCI', start='2000-01-01')
    credit = fetch_db_level('NFCICREDIT', start='2000-01-01')
    leverage = fetch_db_level('NFCILEVERAGE', start='2000-01-01')
    risk = fetch_db_level('NFCIRISK', start='2000-01-01')

    # Fallbacks
    if len(nfci) == 0:
        nfci = fetch_fred_level('NFCI', start='2000-01-01')
    if len(credit) == 0:
        credit = fetch_fred_level('NFCICREDIT', start='2000-01-01')
    if len(leverage) == 0:
        leverage = fetch_fred_level('NFCILEVERAGE', start='2000-01-01')
    if len(risk) == 0:
        risk = fetch_fred_level('NFCIRISK', start='2000-01-01')

    fig, ax = new_fig()

    ax.plot(nfci.index, nfci, color=THEME['primary'], linewidth=3.0,
            label=f'NFCI Composite ({nfci.iloc[-1]:.2f})', zorder=5)
    ax.plot(credit.index, credit, color=THEME['secondary'], linewidth=1.5,
            alpha=0.8, label=f'Credit ({credit.iloc[-1]:.2f})')
    ax.plot(leverage.index, leverage, color=THEME['tertiary'], linewidth=1.5,
            alpha=0.8, label=f'Leverage ({leverage.iloc[-1]:.2f})')
    ax.plot(risk.index, risk, color=THEME['quaternary'], linewidth=1.5,
            alpha=0.8, label=f'Risk ({risk.iloc[-1]:.2f})')

    # Zero line (average tightness)
    ax.axhline(0, color=COLORS['fog'], linewidth=1.0, linestyle='--', alpha=0.7)
    ax.text(nfci.index[5], 0.05, 'Average Tightness',
            fontsize=9, color=COLORS['doldrums'], style='italic')

    style_single_ax(ax, fmt='{:.2f}')
    set_xlim_to_data(ax, nfci.index)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    add_last_value_label(ax, nfci, color=THEME['primary'], fmt='{:.2f}', side='right')
    add_recessions(ax, start_date='2000-01-01')
    ax.legend(loc='upper right', fontsize=9, **legend_style())

    add_annotation_box(ax,
        "The headline hides the war.\n"
        "Subcomponents can diverge sharply.\n"
        "Credit subindex leads the composite.",
        x=0.55, y=0.12)

    brand_fig(fig, 'Financial Conditions: The Headline Hides the War',
              subtitle='NFCI Composite vs. Risk, Credit, and Leverage Subindices',
              source='Chicago Fed via FRED',
              data_date=nfci.index[-1])

    return save_fig(fig, 'chart_04_nfci_decomposition.png')


# ============================================
# CHART 5: SLOOS Leads Loan Growth [Figure 5]
# ============================================
def chart_05():
    """SLOOS C&I tightening (inverted) vs C&I loan growth YoY."""
    print('\nChart 5: SLOOS Leads Loan Growth...')

    sloos = fetch_db_level('DRTSCILM', start='1990-01-01')
    busloans = fetch_db_level('BUSLOANS', start='1988-01-01')
    if len(sloos) == 0:
        sloos = fetch_fred_level('DRTSCILM', start='1990-01-01')
    if len(busloans) == 0:
        busloans = fetch_fred_level('BUSLOANS', start='1988-01-01')

    # Invert SLOOS so tightening points DOWN
    sloos_inv = sloos * -1

    # Compute YoY% for BUSLOANS (weekly data ~ 52 periods, or monthly ~ 12)
    # Detect frequency
    if len(busloans) > 100:
        median_gap = busloans.index.to_series().diff().median().days
        if median_gap < 10:
            # Weekly
            busloans_yoy = busloans.pct_change(52) * 100
        else:
            # Monthly
            busloans_yoy = busloans.pct_change(12) * 100
    else:
        busloans_yoy = busloans.pct_change(12) * 100

    busloans_yoy = busloans_yoy.dropna()
    busloans_yoy = busloans_yoy[busloans_yoy.index >= '1990-01-01']

    fig, ax1 = new_fig()
    ax2 = ax1.twinx()
    c1, c2 = THEME['secondary'], THEME['primary']

    ax1.plot(sloos_inv.index, sloos_inv, color=c1, linewidth=2.0,
             label=f'SLOOS C&I Tightening (Inv.) ({sloos_inv.iloc[-1]:.1f}%)')
    ax2.plot(busloans_yoy.index, busloans_yoy, color=c2, linewidth=2.5,
             label=f'C&I Loan Growth YoY ({busloans_yoy.iloc[-1]:.1f}%)')

    # Zero lines
    ax1.axhline(0, color=COLORS['fog'], linewidth=0.8, linestyle='--', alpha=0.5)
    ax2.axhline(0, color=COLORS['fog'], linewidth=0.6, linestyle=':', alpha=0.3)

    style_dual_ax(ax1, ax2, c1, c2)
    ax1.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.0f}%'))
    ax2.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.0f}%'))
    set_xlim_to_data(ax1, sloos_inv.index)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    add_last_value_label(ax1, sloos_inv, color=c1, fmt='{:.1f}%', side='left')
    add_last_value_label(ax2, busloans_yoy, color=c2, fmt='{:.1f}%', side='right')
    add_recessions(ax1, start_date='1990-01-01')

    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax1.legend(h1 + h2, l1 + l2, loc='lower left', fontsize=9, **legend_style())

    add_annotation_box(ax1,
        "When banks tighten (SLOOS drops inverted),\n"
        "loan growth follows 2-4 quarters later.\n"
        "SLOOS is the pipeline. Loans are the flow.",
        x=0.82, y=0.12)

    brand_fig(fig, 'The Credit Pipeline: When Banks Tighten, Loan Growth Follows',
              subtitle='SLOOS C&I Tightening (Inverted, Leading) vs. C&I Loan Growth YoY',
              source='Federal Reserve SLOOS, H.8 via FRED',
              data_date=sloos_inv.index[-1])

    return save_fig(fig, 'chart_05_sloos_ci_loans.png')


# ============================================
# CHART 6: Transmission Gap (Real Rates vs HY Spreads) [Figure 6]
# ============================================
def chart_06():
    """Real rates vs HY OAS inverted, showing transmission failure."""
    print('\nChart 6: Transmission Gap...')

    # Use 10Y TIPS yield as real rate proxy (cleanest approach)
    real_rate = fetch_db_level('DFII10', start='2000-01-01')
    if len(real_rate) == 0:
        real_rate = fetch_fred_level('DFII10', start='2000-01-01')

    hy = fetch_db_level('BAMLH0A0HYM2', start='2000-01-01')
    if len(hy) == 0:
        hy = fetch_fred_level('BAMLH0A0HYM2', start='2000-01-01')

    # Invert HY OAS: tight spreads = high on chart = "loose"
    hy_inv = hy * -100  # Convert to bps and invert

    fig, ax1 = new_fig()
    ax2 = ax1.twinx()
    c1, c2 = THEME['primary'], THEME['secondary']

    ax1.plot(real_rate.index, real_rate, color=c1, linewidth=2.5,
             label=f'10Y Real Rate ({real_rate.iloc[-1]:.2f}%)')
    ax2.plot(hy_inv.index, hy_inv, color=c2, linewidth=2.0,
             label=f'HY OAS Inverted ({hy_inv.iloc[-1]:.0f} bps inv.)')

    # Zero line on real rate axis
    ax1.axhline(0, color=COLORS['fog'], linewidth=0.8, linestyle='--', alpha=0.5)

    style_dual_ax(ax1, ax2, c1, c2)
    ax1.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.1f}%'))
    ax2.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.0f}'))
    set_xlim_to_data(ax1, real_rate.index)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    add_last_value_label(ax1, real_rate, color=c1, fmt='{:.2f}%', side='left')
    add_last_value_label(ax2, hy_inv, color=c2, fmt='{:.0f}', side='right')
    add_recessions(ax1, start_date='2000-01-01')

    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax1.legend(h1 + h2, l1 + l2, loc='upper right', fontsize=9, **legend_style())

    add_annotation_box(ax1,
        "When these diverge, policy is not transmitting.\n"
        "Real rates restrictive + spreads tight =\n"
        "the market is overriding the Fed.",
        x=0.50, y=0.12)

    brand_fig(fig, 'The Transmission Gap',
              subtitle='Real Rates (Restrictive) vs. HY Spreads (Inverted, Loose)',
              source='FRED, ICE BofA',
              data_date=real_rate.index[-1])

    return save_fig(fig, 'chart_06_transmission_gap.png')


# ============================================
# CHART 7: Complacency Gap (VIX Inverted vs LFI) [Figure 7]
# ============================================
def chart_07():
    """VIX inverted vs Labor Fragility Index, showing complacency."""
    print('\nChart 7: Complacency Gap...')

    vix = fetch_db_level('VIXCLS', start='2000-01-01')
    if len(vix) == 0:
        vix = fetch_fred_level('VIXCLS', start='2000-01-01')

    # Smooth VIX with 63-day (3-month) MA before inverting
    vix = vix.rolling(63, min_periods=10).mean()
    # Invert VIX: low VIX = high on chart = complacency
    vix_inv = vix * -1

    # Fetch LFI from lighthouse_indices (already 63-day smoothed in compute_indices)
    # Additional 63-day chart smoothing to match VIX smoothing
    lfi = fetch_db_index('LFI', start='2000-01-01')
    if len(lfi) > 0:
        lfi = lfi.rolling(63, min_periods=10).mean()

    if len(lfi) == 0:
        print('  No LFI data available. Attempting manual construction...')
        # If LFI not in indices, skip gracefully
        print('  Skipping chart 7 (no LFI data).')
        return None

    fig, ax1 = new_fig()
    ax2 = ax1.twinx()
    c1, c2 = THEME['primary'], THEME['secondary']

    ax1.plot(vix_inv.index, vix_inv, color=c1, linewidth=2.0,
             label=f'VIX Inverted ({vix_inv.iloc[-1]:.1f})')
    ax2.plot(lfi.index, lfi, color=c2, linewidth=2.5,
             label=f'LFI ({lfi.iloc[-1]:.2f})')

    # Zero line on LFI axis
    ax2.axhline(0, color=COLORS['fog'], linewidth=0.8, linestyle='--', alpha=0.5)

    # LFI threshold
    ax2.axhline(0.5, color=COLORS['venus'], linewidth=1.0, linestyle=':', alpha=0.6)

    style_dual_ax(ax1, ax2, c1, c2)
    ax1.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.0f}'))
    ax2.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.2f}'))
    set_xlim_to_data(ax1, vix_inv.index)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    add_last_value_label(ax1, vix_inv, color=c1, fmt='{:.1f}', side='left')
    add_last_value_label(ax2, lfi, color=c2, fmt='{:.2f}', side='right')
    add_recessions(ax1, start_date='2000-01-01')

    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax1.legend(h1 + h2, l1 + l2, loc='upper right', fontsize=9, **legend_style())

    add_annotation_box(ax1,
        "Gap = priced risk minus actual fragility.\n"
        "When VIX is low and LFI is rising,\n"
        "the market is mispricing labor stress.",
        x=0.50, y=0.12)

    brand_fig(fig, 'The Complacency Gap',
              subtitle='VIX (Inverted) vs. Labor Fragility Index',
              source='CBOE, Lighthouse Macro Proprietary',
              data_date=vix_inv.index[-1])

    return save_fig(fig, 'chart_07_complacency_gap.png')


# ============================================
# CHART 8: Banks See It, Spreads Don't [Figure 8]
# ============================================
def chart_08():
    """Credit card delinquency rate vs HY OAS inverted."""
    print('\nChart 8: Banks See It, Spreads Don\'t...')

    delinq = fetch_db_level('DRCCLACBS', start='1991-01-01')
    hy = fetch_db_level('BAMLH0A0HYM2', start='1991-01-01')
    if len(delinq) == 0:
        delinq = fetch_fred_level('DRCCLACBS', start='1991-01-01')
    if len(hy) == 0:
        hy = fetch_fred_level('BAMLH0A0HYM2', start='1991-01-01')

    # Invert HY OAS: tight spreads = high on chart = complacent
    hy_inv = hy * -100  # bps inverted

    fig, ax1 = new_fig()
    ax2 = ax1.twinx()
    c1, c2 = THEME['primary'], THEME['secondary']

    ax1.plot(delinq.index, delinq, color=c1, linewidth=2.5,
             label=f'CC Delinquency Rate ({delinq.iloc[-1]:.2f}%)')
    ax2.plot(hy_inv.index, hy_inv, color=c2, linewidth=2.0,
             label=f'HY OAS Inverted ({hy_inv.iloc[-1]:.0f} bps inv.)')

    style_dual_ax(ax1, ax2, c1, c2)
    ax1.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.1f}%'))
    ax2.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.0f}'))
    set_xlim_to_data(ax1, delinq.index)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    add_last_value_label(ax1, delinq, color=c1, fmt='{:.2f}%', side='left')
    add_last_value_label(ax2, hy_inv, color=c2, fmt='{:.0f}', side='right')
    add_recessions(ax1, start_date='1991-01-01')

    # Annotate 2006-07 divergence
    ax1.annotate('2006-07: Banks see it.\nSpreads don\'t.',
                 xy=(pd.Timestamp('2007-01-01'), 4.5), fontsize=9,
                 color=COLORS['venus'], fontweight='bold',
                 ha='center', va='bottom',
                 arrowprops=dict(arrowstyle='->', color=COLORS['venus'], lw=1.5),
                 xytext=(pd.Timestamp('2004-06-01'), 5.8))

    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax1.legend(h1 + h2, l1 + l2, loc='upper right', fontsize=9, **legend_style())

    brand_fig(fig, 'Banks See It. Spreads Don\'t.',
              subtitle='Credit Card Delinquency Rate vs. HY OAS (Inverted)',
              source='Federal Reserve, ICE BofA via FRED',
              data_date=delinq.index[-1])

    return save_fig(fig, 'chart_08_delinq_vs_spreads.png')


# ============================================
# CHART 9: Default Risk Premium with Regime Bands [Figure 9]
# ============================================
def chart_09():
    """Baa-10Y spread with regime bands and historical annotations."""
    print('\nChart 9: Default Risk Premium with Regime Bands...')

    baa10y = fetch_db_level('BAA10Y', start='1986-01-01')
    if len(baa10y) == 0:
        baa10y = fetch_fred_level('BAA10Y', start='1986-01-01')

    # BAA10Y is in percentage points. Convert to bps for display.
    baa10y_bps = baa10y * 100

    fig, ax = new_fig()

    # Regime bands (in bps)
    y_min = 0
    y_max = max(baa10y_bps.max() * 1.05, 700)

    ax.axhspan(0, 150, color=COLORS['starboard'], alpha=0.08)
    ax.axhspan(150, 250, alpha=0)  # Normal = no fill
    ax.axhspan(250, 400, color=COLORS['dusk'], alpha=0.08)
    ax.axhspan(400, y_max, color=COLORS['port'], alpha=0.10)

    # Regime labels on right edge
    label_x = baa10y_bps.index[-1] + pd.Timedelta(days=60)
    ax.text(label_x, 75, 'Complacent', fontsize=8, color=COLORS['starboard'], va='center')
    ax.text(label_x, 200, 'Normal', fontsize=8, color=COLORS['doldrums'], va='center')
    ax.text(label_x, 325, 'Elevated', fontsize=8, color=COLORS['dusk'], va='center')
    ax.text(label_x, 450, 'Stressed', fontsize=8, color=COLORS['port'], va='center')

    # Main line on top
    ax.plot(baa10y_bps.index, baa10y_bps, color=THEME['primary'], linewidth=2.0,
            label=f'Baa-10Y Spread ({baa10y_bps.iloc[-1]:.0f} bps)', zorder=5)

    # Annotate key moments
    annotations_list = [
        (pd.Timestamp('2000-11-01'), 'Dot-com peak'),
        (pd.Timestamp('2007-01-01'), 'Pre-crisis low'),
        (pd.Timestamp('2008-12-01'), '2008-09 crisis'),
        (pd.Timestamp('2020-03-15'), 'COVID spike'),
    ]
    for dt, lbl in annotations_list:
        # Find closest data point
        closest = baa10y_bps.index[baa10y_bps.index.get_indexer([dt], method='nearest')[0]]
        val = baa10y_bps.loc[closest]
        offset_y = 80 if val < 400 else -80
        ax.annotate(lbl, xy=(closest, val), fontsize=7,
                    color=COLORS['venus'], fontweight='bold',
                    ha='center', va='bottom' if offset_y > 0 else 'top',
                    arrowprops=dict(arrowstyle='->', color=COLORS['venus'], lw=1.0),
                    xytext=(closest, val + offset_y))

    style_single_ax(ax, fmt='{:.0f}')
    ax.set_ylim(y_min, y_max)
    set_xlim_to_data(ax, baa10y_bps.index)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    add_last_value_label(ax, baa10y_bps, color=THEME['primary'], fmt='{:.0f}', side='right')
    add_recessions(ax, start_date='1986-01-01')
    ax.legend(loc='upper right', fontsize=9, **legend_style())

    brand_fig(fig, 'The Default Risk Premium',
              subtitle='Baa Corporate Spread vs. 10-Year Treasury | Regime Context',
              source="Moody's, US Treasury via FRED",
              data_date=baa10y_bps.index[-1])

    return save_fig(fig, 'chart_09_erp_regime.png')


# ============================================
# CHART 10: Credit-Labor Gap (CLG) [Figure 10]
# ============================================
def chart_10():
    """Credit-Labor Gap: z(HY OAS) - z(LFI). Proprietary composite."""
    print('\nChart 10: Credit-Labor Gap (CLG)...')

    clg = fetch_db_index('CLG', start='2000-01-01')

    if len(clg) == 0:
        print('  No CLG data available. Skipping.')
        return None

    # Heavy smoothing: 6-month MA to get a clean signal line
    clg = clg.rolling(126, min_periods=30).mean()

    fig, ax = new_fig()

    ax.plot(clg.index, clg, color=THEME['primary'], linewidth=2.0,
            label=f'CLG ({clg.iloc[-1]:.2f})')

    # Fill: starboard above 0, port below 0 (light fill)
    ax.fill_between(clg.index, 0, clg,
                    where=(clg >= 0),
                    color=COLORS['starboard'], alpha=0.10)
    ax.fill_between(clg.index, 0, clg,
                    where=(clg < 0),
                    color=COLORS['port'], alpha=0.10)

    # Zero line
    ax.axhline(0, color=COLORS['fog'], linewidth=1.0, linestyle='--', alpha=0.7)

    # Threshold lines
    ax.axhline(-1.0, color=COLORS['venus'], linewidth=1.5, linestyle='--', alpha=0.8)
    ax.text(clg.index[min(10, len(clg) - 1)], -1.15,
            'Credit Ignoring Labor (-1.0)',
            fontsize=9, color=COLORS['venus'], fontweight='bold')
    ax.axhline(1.0, color=COLORS['sea'], linewidth=1.5, linestyle='--', alpha=0.8)
    ax.text(clg.index[min(10, len(clg) - 1)], 1.10,
            'Credit Too Wide (+1.0)',
            fontsize=9, color=COLORS['sea'], fontweight='bold')

    # No scatter dots - they add noise on smoothed data

    style_single_ax(ax, fmt='{:.1f}')
    set_xlim_to_data(ax, clg.index)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    add_last_value_label(ax, clg, color=THEME['primary'], fmt='{:.2f}', side='right')
    add_recessions(ax, start_date='2000-01-01')
    ax.legend(loc='upper right', fontsize=9, **legend_style())

    add_annotation_box(ax,
        "CLG = z(HY OAS) minus z(LFI).\n"
        "Below -1.0: credit markets are too tight\n"
        "for what the labor market is signaling.",
        x=0.82, y=0.88)

    brand_fig(fig, 'The Credit-Labor Gap (CLG)',
              subtitle='z(HY OAS) minus z(LFI) | When Credit Ignores What Labor Is Saying',
              source='Lighthouse Macro Proprietary',
              data_date=clg.index[-1])

    return save_fig(fig, 'chart_10_credit_labor_gap.png')


# ============================================
# CHART 11: Financial Cascade "You Are Here" [Figure 11]
# ============================================
def chart_11():
    """Infographic: 8-step financial cascade with current status."""
    print('\nChart 11: Financial Cascade "You Are Here"...')

    # Static infographic data
    steps = [
        {'num': 1, 'label': 'Yield Curve Inverts', 'threshold': '< 0 bps',
         'reading': 'July 2022', 'done': True},
        {'num': 2, 'label': 'Curve Dis-Inverts', 'threshold': '> 0 bps',
         'reading': 'Sept 2024', 'done': True},
        {'num': 3, 'label': 'SLOOS Tightens', 'threshold': '> +20%',
         'reading': 'Peak 50.8% (Q3 2023)', 'done': True},
        {'num': 4, 'label': 'Loan Growth Decelerates', 'threshold': '< +3%',
         'reading': '+2.9% YoY (improving)', 'done': True},
        {'num': 5, 'label': 'Spreads Widen', 'threshold': '> 400 bps',
         'reading': '319 bps', 'done': False},
        {'num': 6, 'label': 'VIX Spikes', 'threshold': '> 25',
         'reading': '29.5 (Mar 6)', 'done': True},
        {'num': 7, 'label': 'Defaults Rise', 'threshold': '> 4%',
         'reading': '~2.5%', 'done': False},
        {'num': 8, 'label': 'Recession Begins', 'threshold': 'NBER call',
         'reading': 'Not yet', 'done': False},
    ]

    fig, ax = new_fig(figsize=(14, 9))
    ax.set_xlim(0, 10)
    ax.set_ylim(-0.5, len(steps) + 0.5)
    ax.axis('off')
    for spine in ax.spines.values():
        spine.set_visible(False)

    # "YOU ARE HERE" position: between step 4 and 5
    you_are_here_y = len(steps) - 4.5  # Between index 3 and 4 from top

    bar_height = 0.7
    bar_left = 1.0
    bar_width = 7.5

    for i, step in enumerate(steps):
        y = len(steps) - 1 - i  # Top to bottom

        # Color based on status
        if step['done']:
            box_color = COLORS['sea']
            text_color = '#ffffff'
            status_mark = '\u2713'  # checkmark
        elif step['num'] == 5:
            # "Next" step
            box_color = COLORS['venus']
            text_color = '#ffffff'
            status_mark = '\u2190 NEXT'
        else:
            box_color = COLORS['fog']
            text_color = THEME['fg']
            status_mark = '\u2717'  # X mark

        # Draw rounded box
        rect = FancyBboxPatch(
            (bar_left, y - bar_height / 2), bar_width, bar_height,
            boxstyle='round,pad=0.1',
            facecolor=box_color, edgecolor=THEME['spine'],
            linewidth=1.0, alpha=0.9
        )
        ax.add_patch(rect)

        # Step number circle
        circle = plt.Circle((bar_left + 0.4, y), 0.25,
                             color=THEME['bg'], ec=text_color, lw=1.5, zorder=5)
        ax.add_patch(circle)
        ax.text(bar_left + 0.4, y, str(step['num']),
                fontsize=12, fontweight='bold', color=text_color,
                ha='center', va='center', zorder=6)

        # Step label
        ax.text(bar_left + 1.0, y + 0.08, step['label'],
                fontsize=12, fontweight='bold', color=text_color,
                ha='left', va='center')

        # Threshold and reading
        ax.text(bar_left + 1.0, y - 0.18,
                f"Trigger: {step['threshold']}  |  Reading: {step['reading']}",
                fontsize=9, color=text_color, alpha=0.85,
                ha='left', va='center')

        # Status mark on right
        ax.text(bar_left + bar_width - 0.3, y, status_mark,
                fontsize=14 if step['num'] != 5 else 11,
                fontweight='bold', color=text_color,
                ha='center', va='center')

    # "YOU ARE HERE" arrow between steps 4 and 5
    arrow_y = you_are_here_y
    ax.annotate('YOU ARE HERE',
                xy=(bar_left - 0.1, arrow_y),
                fontsize=14, fontweight='bold', color=COLORS['venus'],
                ha='right', va='center',
                arrowprops=dict(arrowstyle='->', color=COLORS['venus'],
                                lw=3.0, connectionstyle='arc3,rad=0'))

    # Connecting line between steps
    for i in range(len(steps) - 1):
        y_top = len(steps) - 1 - i - bar_height / 2
        y_bot = len(steps) - 2 - i + bar_height / 2
        ax.plot([bar_left + bar_width / 2, bar_left + bar_width / 2],
                [y_bot, y_top],
                color=COLORS['doldrums'], linewidth=1.5, linestyle=':', alpha=0.5)

    brand_fig(fig, 'The Financial Cascade: You Are Here',
              subtitle='Eight Steps of Financial Stress | Five Complete, Three Pending',
              source='Lighthouse Macro')

    return save_fig(fig, 'chart_11_financial_cascade.png')


# ============================================
# CHART 12: FCI Regime Map with Component Tug-of-War [Figure 12]
# ============================================
def chart_12():
    """Two-panel: FCI regime map (top) and component tug-of-war bars (bottom)."""
    print('\nChart 12: FCI Regime Map with Component Tug-of-War...')

    fci = fetch_db_index('FCI', start='1975-01-01')

    if len(fci) == 0:
        print('  No FCI data available. Skipping.')
        return None

    fig, (ax_top, ax_bot) = new_fig_panels(nrows=2, height_ratios=[3, 1], figsize=(14, 11))

    # ---- TOP PANEL: FCI time series with regime bands ----
    y_max = max(fci.max() + 0.5, 2.0)
    y_min = min(fci.min() - 0.5, -2.0)

    # Regime bands
    ax_top.axhspan(1.0, y_max, color=COLORS['starboard'], alpha=0.10)
    ax_top.axhspan(0.5, 1.0, color=COLORS['sea'], alpha=0.08)
    ax_top.axhspan(-0.5, 0.5, alpha=0)  # Neutral = no fill
    ax_top.axhspan(-1.0, -0.5, color=COLORS['dusk'], alpha=0.08)
    ax_top.axhspan(y_min, -1.0, color=COLORS['port'], alpha=0.10)

    ax_top.plot(fci.index, fci, color=THEME['primary'], linewidth=2.0,
                label=f'FCI ({fci.iloc[-1]:.2f})', zorder=5)

    # Regime labels on right edge
    label_x = fci.index[-1] + pd.Timedelta(days=60)
    ax_top.text(label_x, 1.25, 'Very Loose', fontsize=8,
                color=COLORS['starboard'], va='center')
    ax_top.text(label_x, 0.75, 'Loose', fontsize=8,
                color=COLORS['sea'], va='center')
    ax_top.text(label_x, 0.0, 'Neutral', fontsize=8,
                color=COLORS['doldrums'], va='center')
    ax_top.text(label_x, -0.75, 'Tight', fontsize=8,
                color=COLORS['dusk'], va='center')
    ax_top.text(label_x, -1.25, 'Crisis', fontsize=8,
                color=COLORS['port'], va='center')

    # Zero line
    ax_top.axhline(0, color=COLORS['fog'], linewidth=1.0, linestyle='--', alpha=0.7)

    style_single_ax(ax_top, fmt='{:.1f}')
    ax_top.set_ylim(y_min, y_max)
    set_xlim_to_data(ax_top, fci.index)
    ax_top.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    add_last_value_label(ax_top, fci, color=THEME['primary'], fmt='{:.2f}', side='right')
    add_recessions(ax_top, start_date='1975-01-01')
    ax_top.legend(loc='upper left', fontsize=9, **legend_style())

    # ---- BOTTOM PANEL: Component tug-of-war (horizontal bars) ----
    # These are illustrative current readings based on latest available data
    # Attempt to fetch latest component data for directional read
    components = {}

    # Try to get latest values for each component
    hy_latest = fetch_db_level('BAMLH0A0HYM2', start='2025-01-01')
    nfci_latest = fetch_db_level('NFCI', start='2025-01-01')
    curve_latest = fetch_db_level('T10Y2Y', start='2025-01-01')
    real_rate_latest = fetch_db_level('DFII10', start='2025-01-01')
    busloans_latest = fetch_db_level('BUSLOANS', start='2024-01-01')
    vix_latest = fetch_db_level('VIXCLS', start='2025-01-01')
    lci_latest = fetch_db_index('LCI', start='2025-01-01')
    sloos_latest = fetch_db_level('DRTSCILM', start='2024-01-01')

    # Compute directional contributions (positive = pulling loose, negative = tight)
    # Use z-score-like heuristic relative to historical norms
    def _direction(series, invert=False, tight_label='Tight', loose_label='Loose'):
        """Return a rough directional score and label."""
        if len(series) == 0:
            return 0.0
        val = float(series.iloc[-1])
        if invert:
            val = -val
        return val

    # Component contribution estimates (rough directional)
    comp_labels = ['HY OAS', 'NFCI', 'Yield Curve', 'Real Rate',
                   'C&I Growth', 'VIX', 'LCI', 'SLOOS']
    comp_values = []

    # HY OAS: tight spreads = loose conditions (negative for tight = positive for loose)
    if len(hy_latest) > 0:
        # Below 300 bps = loose
        comp_values.append(max(-1, min(1, (3.5 - hy_latest.iloc[-1]) / 2.0)))
    else:
        comp_values.append(0.3)

    # NFCI: negative = loose conditions
    if len(nfci_latest) > 0:
        comp_values.append(max(-1, min(1, -nfci_latest.iloc[-1] * 2)))
    else:
        comp_values.append(0.2)

    # Yield Curve: positive = loose
    if len(curve_latest) > 0:
        comp_values.append(max(-1, min(1, curve_latest.iloc[-1] / 1.5)))
    else:
        comp_values.append(0.1)

    # Real Rate: high = tight (invert)
    if len(real_rate_latest) > 0:
        comp_values.append(max(-1, min(1, -real_rate_latest.iloc[-1] / 3.0)))
    else:
        comp_values.append(-0.5)

    # C&I Growth: positive = loose
    if len(busloans_latest) > 60:
        median_gap = busloans_latest.index.to_series().diff().median().days
        periods = 52 if median_gap < 10 else 12
        bl_yoy = busloans_latest.pct_change(periods).iloc[-1] * 100
        comp_values.append(max(-1, min(1, bl_yoy / 10.0)))
    else:
        comp_values.append(0.0)

    # VIX: low = loose
    if len(vix_latest) > 0:
        comp_values.append(max(-1, min(1, (20 - vix_latest.iloc[-1]) / 15.0)))
    else:
        comp_values.append(0.3)

    # LCI: positive = loose (ample liquidity)
    if len(lci_latest) > 0:
        comp_values.append(max(-1, min(1, lci_latest.iloc[-1])))
    else:
        comp_values.append(0.0)

    # SLOOS: high tightening = tight (invert)
    if len(sloos_latest) > 0:
        comp_values.append(max(-1, min(1, -sloos_latest.iloc[-1] / 50.0)))
    else:
        comp_values.append(-0.3)

    comp_values = np.array(comp_values)

    # Bar colors: positive (loose) = Sea, negative (tight) = Dusk/Port
    bar_colors = [COLORS['sea'] if v >= 0 else COLORS['dusk'] for v in comp_values]

    y_pos = np.arange(len(comp_labels))
    ax_bot.barh(y_pos, comp_values, height=0.6, color=bar_colors, alpha=0.85,
                edgecolor=THEME['spine'], linewidth=0.5)

    # Labels
    ax_bot.set_yticks(y_pos)
    ax_bot.set_yticklabels(comp_labels, fontsize=10, color=THEME['fg'])

    # Zero line
    ax_bot.axvline(0, color=COLORS['fog'], linewidth=1.0, linestyle='-', alpha=0.7)

    # Axis labels
    ax_bot.text(-1.05, -0.8, '\u2190 Pulling TIGHT', fontsize=9,
                color=COLORS['dusk'], ha='left', transform=ax_bot.get_yaxis_transform())
    ax_bot.text(1.05, -0.8, 'Pulling LOOSE \u2192', fontsize=9,
                color=COLORS['sea'], ha='right', transform=ax_bot.get_yaxis_transform())

    style_ax(ax_bot, right_primary=False)
    ax_bot.tick_params(axis='both', which='both', length=0)
    ax_bot.set_xlim(-1.1, 1.1)
    ax_bot.xaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.1f}'))
    ax_bot.tick_params(axis='x', labelsize=9, colors=THEME['muted'])

    # Title for bottom panel
    ax_bot.set_title('Component Tug-of-War (Current)', fontsize=11,
                     color=THEME['fg'], fontweight='bold', pad=8)

    brand_fig(fig, 'Financial Conditions Index (FCI): Regime Map',
              subtitle='Composite with Component Tug-of-War',
              source='Lighthouse Macro Proprietary',
              data_date=fci.index[-1])

    return save_fig(fig, 'chart_12_fci_regime_map.png')


# ============================================
# CHART MAP & MAIN
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
    12: chart_12,
}


def main():
    parser = argparse.ArgumentParser(description='Generate Financial Conditions educational charts')
    parser.add_argument('--chart', type=int, help='Chart number to generate (1-12)')
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
