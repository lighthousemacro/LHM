#!/usr/bin/env python3
"""
Generate Charts for Educational Series: Post 9 - Financial Conditions (Pillar 9)
================================================================================
10 charts covering: HY OAS spreads, HY vs IG spreads, Credit-Labor Gap (CLG),
NFCI decomposition, SLOOS lending standards, bank credit growth, credit card
stress, Baa-10Y default risk premium, VIX vs VVIX, and FCI composite.

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


def add_annotation_box(ax, text, x=0.52, y=0.92):
    """Add takeaway annotation box in dead space."""
    box_fc = '#2389BB'
    box_alpha = 1.0
    txt_color = '#ffffff'
    ax.text(x, y, text, transform=ax.transAxes,
            fontsize=11, fontweight='bold', color=txt_color, ha='center', va='top',
            style='italic',
            bbox=dict(boxstyle='round,pad=0.5',
                      facecolor=box_fc, edgecolor='#00BBFF',
                      linewidth=2.0,
                      alpha=box_alpha))


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
# CHART 1: HY OAS Spread (Full History) [Figure 1]
# ============================================
def chart_01():
    """High-Yield Credit Spreads, full history with threshold lines."""
    print('\nChart 1: HY OAS Spread (Full History)...')

    hy = fetch_db_level('BAMLH0A0HYM2', start='1997-01-01')
    if len(hy) == 0:
        hy = fetch_fred_level('BAMLH0A0HYM2', start='1997-01-01')

    # Compute percentile for annotation
    last_val = hy.iloc[-1]
    pctile = (hy < last_val).sum() / len(hy) * 100

    fig, ax = new_fig()

    ax.plot(hy.index, hy, color=THEME['primary'], linewidth=2.0,
            label=f'HY OAS ({last_val:.0f} bps)')

    # Threshold reference lines
    ax.axhline(300, color=COLORS['venus'], linewidth=1.5, linestyle='--', alpha=0.8)
    ax.text(hy.index[10], 320, 'Complacent (300 bps)',
            fontsize=9, color=COLORS['venus'], style='italic')

    ax.axhline(450, color=COLORS['fog'], linewidth=1.2, linestyle='--', alpha=0.7)
    ax.text(hy.index[10], 470, 'Elevated (450 bps)',
            fontsize=9, color=COLORS['doldrums'], style='italic')

    ax.axhline(650, color=COLORS['port'], linewidth=1.5, linestyle='--', alpha=0.8)
    ax.text(hy.index[10], 670, 'Crisis (650 bps)',
            fontsize=9, color=COLORS['port'], style='italic')

    style_single_ax(ax, fmt='{:.0f}')
    set_xlim_to_data(ax, hy.index)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    add_last_value_label(ax, hy, color=THEME['primary'], fmt='{:.0f}', side='right')
    add_recessions(ax, start_date='1997-01-01')
    ax.legend(loc='upper right', **legend_style())

    add_annotation_box(ax,
        f"{last_val:.0f} bps: {pctile:.0f}th percentile since 1997.\n"
        f"Below 300 = market pricing perfection.\n"
        f"Spreads compress until they don't.",
        x=0.52, y=0.92)

    brand_fig(fig, 'High-Yield Credit Spreads',
              subtitle="ICE BofA HY OAS | The Market's Real-Time Verdict on Risk",
              source='ICE BofA via FRED',
              data_date=hy.index[-1])

    return save_fig(fig, 'chart_01_hy_oas.png')


# ============================================
# CHART 2: HY OAS vs IG OAS (Dual Axis) [Figure 2]
# ============================================
def chart_02():
    """Credit Spreads: High-Yield vs Investment-Grade, dual axis."""
    print('\nChart 2: HY OAS vs IG OAS...')

    hy = fetch_db_level('BAMLH0A0HYM2', start='1997-01-01')
    ig = fetch_db_level('BAMLC0A0CM', start='1997-01-01')
    if len(hy) == 0:
        hy = fetch_fred_level('BAMLH0A0HYM2', start='1997-01-01')
    if len(ig) == 0:
        ig = fetch_fred_level('BAMLC0A0CM', start='1997-01-01')

    # Align
    idx = hy.index.intersection(ig.index)
    hy = hy.loc[idx]
    ig = ig.loc[idx]

    # Compute HY/IG ratio for annotation
    ratio = hy / ig
    last_ratio = ratio.iloc[-1]

    fig, ax1 = new_fig()
    ax2 = ax1.twinx()
    c1, c2 = THEME['secondary'], THEME['primary']

    ax1.plot(ig.index, ig, color=c1, linewidth=2.0,
             label=f'IG OAS ({ig.iloc[-1]:.0f} bps)')
    ax2.plot(hy.index, hy, color=c2, linewidth=2.5,
             label=f'HY OAS ({hy.iloc[-1]:.0f} bps)')

    style_dual_ax(ax1, ax2, c1, c2)
    ax1.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.0f}'))
    ax2.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.0f}'))
    set_xlim_to_data(ax1, hy.index)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    add_last_value_label(ax1, ig, color=c1, fmt='{:.0f}', side='left')
    add_last_value_label(ax2, hy, color=c2, fmt='{:.0f}', side='right')
    add_recessions(ax1, start_date='1997-01-01')

    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax1.legend(h1 + h2, l1 + l2, loc='upper right', **legend_style())

    add_annotation_box(ax1,
        f"HY/IG ratio: {last_ratio:.1f}x.\n"
        f"When this ratio compresses, the market\n"
        f"is underpricing credit differentiation.",
        x=0.52, y=0.92)

    brand_fig(fig, 'Credit Spreads: High-Yield vs Investment-Grade',
              subtitle='When the Gap Narrows, Risk Is Underpriced',
              source='ICE BofA via FRED',
              data_date=hy.index[-1])

    return save_fig(fig, 'chart_02_hy_vs_ig.png')


# ============================================
# CHART 3: Credit-Labor Gap (CLG) [Figure 3]
# ============================================
def chart_03():
    """Credit-Labor Gap: z(HY OAS) - z(LFI). Proprietary composite."""
    print('\nChart 3: Credit-Labor Gap (CLG)...')

    clg = fetch_db_index('CLG', start='2000-01-01')

    if len(clg) == 0:
        print('  No CLG data available. Skipping.')
        return None

    fig, ax = new_fig()

    ax.plot(clg.index, clg, color=THEME['primary'], linewidth=2.0,
            label=f'CLG ({clg.iloc[-1]:.2f})')

    # Fill: green above 0 (credit pricing risk appropriately), red below 0 (credit ignoring labor)
    ax.fill_between(clg.index, 0, clg,
                    where=(clg >= 0),
                    color=COLORS['starboard'], alpha=0.20)
    ax.fill_between(clg.index, 0, clg,
                    where=(clg < 0),
                    color=COLORS['port'], alpha=0.20)

    # Zero line
    ax.axhline(0, color=THEME['zero_line'], linewidth=0.8, linestyle='--', alpha=0.5)

    # -1.0 threshold
    ax.axhline(-1.0, color=COLORS['venus'], linewidth=1.5, linestyle='--', alpha=0.8)
    ax.text(clg.index[10], -1.15, 'Credit Ignoring Labor (-1.0)',
            fontsize=9, color=COLORS['venus'], fontweight='bold')

    style_single_ax(ax, fmt='{:.1f}')
    set_xlim_to_data(ax, clg.index)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    add_last_value_label(ax, clg, color=THEME['primary'], fmt='{:.2f}', side='right')
    add_recessions(ax, start_date='2000-01-01')
    ax.legend(loc='upper right', **legend_style())

    add_annotation_box(ax,
        "CLG = z(HY OAS) minus z(LFI).\n"
        "Below -1.0: credit markets are too tight\n"
        "for what the labor market is signaling.",
        x=0.52, y=0.92)

    brand_fig(fig, 'The Credit-Labor Gap (CLG)',
              subtitle='z(HY OAS) minus z(LFI) | When Credit Ignores What Labor Is Saying',
              source='Lighthouse Macro Proprietary',
              data_date=clg.index[-1])

    return save_fig(fig, 'chart_03_clg.png')


# ============================================
# CHART 4: Chicago Fed NFCI Decomposition [Figure 4]
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

    ax.plot(nfci.index, nfci, color=THEME['primary'], linewidth=2.5,
            label=f'NFCI Composite ({nfci.iloc[-1]:.2f})')
    ax.plot(credit.index, credit, color=THEME['secondary'], linewidth=1.5,
            alpha=0.8, label=f'Credit ({credit.iloc[-1]:.2f})')
    ax.plot(leverage.index, leverage, color=THEME['tertiary'], linewidth=1.5,
            alpha=0.8, label=f'Leverage ({leverage.iloc[-1]:.2f})')
    ax.plot(risk.index, risk, color=THEME['quaternary'], linewidth=1.5,
            alpha=0.8, label=f'Risk ({risk.iloc[-1]:.2f})')

    # Zero line (average tightness)
    ax.axhline(0, color=THEME['zero_line'], linewidth=0.8, linestyle='--', alpha=0.5)
    ax.text(nfci.index[5], 0.05, 'Avg Tightness (0)',
            fontsize=9, color=COLORS['doldrums'], style='italic')

    style_single_ax(ax, fmt='{:.2f}')
    set_xlim_to_data(ax, nfci.index)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    add_last_value_label(ax, nfci, color=THEME['primary'], fmt='{:.2f}', side='right')
    add_recessions(ax, start_date='2000-01-01')
    ax.legend(loc='upper right', **legend_style())

    add_annotation_box(ax,
        "Positive = tighter than average.\n"
        "Negative = looser than average.\n"
        "Credit subindex leads the composite.",
        x=0.35, y=0.92)

    brand_fig(fig, 'Financial Conditions: NFCI Decomposition',
              subtitle='Credit, Leverage, and Risk Subindices',
              source='Chicago Fed via FRED',
              data_date=nfci.index[-1])

    return save_fig(fig, 'chart_04_nfci.png')


# ============================================
# CHART 5: SLOOS Lending Standards (C&I) [Figure 5]
# ============================================
def chart_05():
    """Bank lending standards: C&I loans from Senior Loan Officer Survey."""
    print('\nChart 5: SLOOS Lending Standards...')

    ci_all = fetch_db_level('DRTSCILM', start='1990-01-01')
    ci_small = fetch_db_level('DRTSCIS', start='1990-01-01')
    if len(ci_all) == 0:
        ci_all = fetch_fred_level('DRTSCILM', start='1990-01-01')
    if len(ci_small) == 0:
        ci_small = fetch_fred_level('DRTSCIS', start='1990-01-01')

    fig, ax = new_fig()

    ax.plot(ci_all.index, ci_all, color=THEME['primary'], linewidth=2.5,
            label=f'C&I All Firms ({ci_all.iloc[-1]:.1f}%)')
    ax.plot(ci_small.index, ci_small, color=THEME['secondary'], linewidth=2.0,
            label=f'C&I Small Firms ({ci_small.iloc[-1]:.1f}%)')

    # Zero line
    ax.axhline(0, color=THEME['zero_line'], linewidth=0.8, linestyle='--', alpha=0.5)

    # Fill: red above 0 (tightening), green below 0 (easing)
    ax.fill_between(ci_all.index, 0, ci_all,
                    where=(ci_all > 0),
                    color=COLORS['port'], alpha=0.12)
    ax.fill_between(ci_all.index, 0, ci_all,
                    where=(ci_all <= 0),
                    color=COLORS['starboard'], alpha=0.12)

    # Tightening threshold annotations
    ax.axhline(20, color=COLORS['doldrums'], linewidth=1.0, linestyle=':', alpha=0.5)
    ax.axhline(40, color=COLORS['venus'], linewidth=1.0, linestyle=':', alpha=0.5)

    style_single_ax(ax)
    set_xlim_to_data(ax, ci_all.index)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    add_last_value_label(ax, ci_all, color=THEME['primary'], side='right')
    add_recessions(ax, start_date='1990-01-01')
    ax.legend(loc='upper right', **legend_style())

    add_annotation_box(ax,
        "Net % tightening standards.\n"
        ">20%: significant tightening.\n"
        ">40%: credit crunch territory.",
        x=0.52, y=0.18)

    brand_fig(fig, 'Bank Lending Standards: C&I Loans',
              subtitle='Senior Loan Officer Survey | When Banks Say No',
              source='Federal Reserve SLOOS',
              data_date=ci_all.index[-1])

    return save_fig(fig, 'chart_05_sloos.png')


# ============================================
# CHART 6: Bank Credit Growth (YoY%) [Figure 6]
# ============================================
def chart_06():
    """Total bank credit and C&I loans, year-over-year % change."""
    print('\nChart 6: Bank Credit Growth...')

    totbk = fetch_db_level('TOTBKCR', start='1974-01-01')
    busloans = fetch_db_level('BUSLOANS', start='1974-01-01')
    if len(totbk) == 0:
        totbk = fetch_fred_level('TOTBKCR', start='1974-01-01')
    if len(busloans) == 0:
        busloans = fetch_fred_level('BUSLOANS', start='1974-01-01')

    # Compute YoY %
    totbk_yoy = totbk.pct_change(52) * 100  # Weekly data, ~52 weeks
    busloans_yoy = busloans.pct_change(52) * 100
    totbk_yoy = totbk_yoy.dropna()
    busloans_yoy = busloans_yoy.dropna()

    # Filter to start at 1975 for clean display
    totbk_yoy = totbk_yoy[totbk_yoy.index >= '1975-01-01']
    busloans_yoy = busloans_yoy[busloans_yoy.index >= '1975-01-01']

    fig, ax1 = new_fig()
    ax2 = ax1.twinx()
    c1, c2 = THEME['secondary'], THEME['primary']

    ax1.plot(busloans_yoy.index, busloans_yoy, color=c1, linewidth=2.0,
             label=f'C&I Loans YoY ({busloans_yoy.iloc[-1]:.1f}%)')
    ax2.plot(totbk_yoy.index, totbk_yoy, color=c2, linewidth=2.5,
             label=f'Total Bank Credit YoY ({totbk_yoy.iloc[-1]:.1f}%)')

    # Zero line
    ax2.axhline(0, color=THEME['zero_line'], linewidth=0.8, linestyle='--', alpha=0.5)

    style_dual_ax(ax1, ax2, c1, c2)
    ax1.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.0f}%'))
    ax2.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.0f}%'))
    align_yaxis_zero(ax1, ax2)
    set_xlim_to_data(ax1, totbk_yoy.index)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    add_last_value_label(ax1, busloans_yoy, color=c1, fmt='{:.1f}%', side='left')
    add_last_value_label(ax2, totbk_yoy, color=c2, fmt='{:.1f}%', side='right')
    add_recessions(ax1, start_date='1975-01-01')

    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax1.legend(h1 + h2, l1 + l2, loc='upper right', **legend_style())

    brand_fig(fig, 'Bank Credit Growth',
              subtitle='Total Bank Credit and C&I Loans | Year-over-Year Change',
              source='Federal Reserve H.8 via FRED',
              data_date=totbk_yoy.index[-1])

    return save_fig(fig, 'chart_06_bank_credit.png')


# ============================================
# CHART 7: Credit Card Stress [Figure 7]
# ============================================
def chart_07():
    """Credit card delinquencies and charge-offs."""
    print('\nChart 7: Credit Card Stress...')

    chargeoff = fetch_db_level('CORCCACBS', start='1985-01-01')
    delinq = fetch_db_level('DRCCLACBS', start='1985-01-01')
    if len(chargeoff) == 0:
        chargeoff = fetch_fred_level('CORCCACBS', start='1985-01-01')
    if len(delinq) == 0:
        delinq = fetch_fred_level('DRCCLACBS', start='1985-01-01')

    fig, ax1 = new_fig()
    ax2 = ax1.twinx()
    c1, c2 = THEME['secondary'], THEME['primary']

    ax1.plot(delinq.index, delinq, color=c1, linewidth=2.0,
             label=f'Delinquency Rate ({delinq.iloc[-1]:.2f}%)')
    ax2.plot(chargeoff.index, chargeoff, color=c2, linewidth=2.5,
             label=f'Charge-Off Rate ({chargeoff.iloc[-1]:.2f}%)')

    style_dual_ax(ax1, ax2, c1, c2)
    ax1.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.1f}%'))
    ax2.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.1f}%'))
    set_xlim_to_data(ax1, delinq.index)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    add_last_value_label(ax1, delinq, color=c1, fmt='{:.2f}%', side='left')
    add_last_value_label(ax2, chargeoff, color=c2, fmt='{:.2f}%', side='right')
    add_recessions(ax1, start_date='1985-01-01')

    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax1.legend(h1 + h2, l1 + l2, loc='upper right', **legend_style())

    add_annotation_box(ax1,
        "Delinquencies lead charge-offs by\n"
        "1-2 quarters. Rising delinquencies\n"
        "signal deteriorating consumer credit.",
        x=0.52, y=0.92)

    brand_fig(fig, 'Credit Card Stress: Delinquencies and Charge-Offs',
              subtitle='When Delinquencies Lead, Charge-Offs Follow',
              source='Federal Reserve via FRED',
              data_date=chargeoff.index[-1])

    return save_fig(fig, 'chart_07_cc_stress.png')


# ============================================
# CHART 8: Baa-10Y Spread (Default Risk Premium) [Figure 8]
# ============================================
def chart_08():
    """Baa corporate spread vs 10-Year Treasury."""
    print('\nChart 8: Baa-10Y Spread...')

    baa10y = fetch_db_level('BAA10Y', start='1986-01-01')
    if len(baa10y) == 0:
        baa10y = fetch_fred_level('BAA10Y', start='1986-01-01')

    # Convert to bps for display (series is in percentage points)
    baa10y_bps = baa10y * 100

    fig, ax = new_fig()

    ax.plot(baa10y.index, baa10y_bps, color=THEME['primary'], linewidth=2.0,
            label=f'Baa-10Y Spread ({baa10y_bps.iloc[-1]:.0f} bps)')

    # Threshold lines
    ax.axhline(200, color=COLORS['fog'], linewidth=1.2, linestyle='--', alpha=0.7)
    ax.text(baa10y.index[10], 210, 'Normal (200 bps)',
            fontsize=9, color=COLORS['doldrums'], style='italic')

    ax.axhline(350, color=COLORS['venus'], linewidth=1.5, linestyle='--', alpha=0.8)
    ax.text(baa10y.index[10], 360, 'Elevated (350 bps)',
            fontsize=9, color=COLORS['venus'], style='italic')

    ax.axhline(500, color=COLORS['port'], linewidth=1.5, linestyle='--', alpha=0.8)
    ax.text(baa10y.index[10], 510, 'Crisis (500 bps)',
            fontsize=9, color=COLORS['port'], style='italic')

    style_single_ax(ax, fmt='{:.0f}')
    set_xlim_to_data(ax, baa10y.index)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    add_last_value_label(ax, baa10y_bps, color=THEME['primary'], fmt='{:.0f}', side='right')
    add_recessions(ax, start_date='1986-01-01')
    ax.legend(loc='upper right', **legend_style())

    add_annotation_box(ax,
        "The Baa-10Y spread captures default\n"
        "risk expectations for IG corporates.\n"
        "Spikes precede earnings deterioration.",
        x=0.52, y=0.92)

    brand_fig(fig, 'The Default Risk Premium',
              subtitle='Baa Corporate Spread vs 10-Year Treasury',
              source='Moody\'s/Treasury via FRED',
              data_date=baa10y.index[-1])

    return save_fig(fig, 'chart_08_baa10y.png')


# ============================================
# CHART 9: VIX vs VVIX [Figure 9]
# ============================================
def chart_09():
    """Volatility and the Volatility of Volatility."""
    print('\nChart 9: VIX vs VVIX...')

    vix = fetch_db_level('VIXCLS', start='2007-12-01')
    vvix = fetch_db_level('VXVCLS', start='2007-12-01')
    if len(vix) == 0:
        vix = fetch_fred_level('VIXCLS', start='2007-12-01')
    if len(vvix) == 0:
        vvix = fetch_fred_level('VXVCLS', start='2007-12-01')

    fig, ax1 = new_fig()
    ax2 = ax1.twinx()
    c1, c2 = THEME['secondary'], THEME['primary']

    ax1.plot(vvix.index, vvix, color=c1, linewidth=1.8,
             label=f'VVIX ({vvix.iloc[-1]:.1f})')
    ax2.plot(vix.index, vix, color=c2, linewidth=2.5,
             label=f'VIX ({vix.iloc[-1]:.1f})')

    style_dual_ax(ax1, ax2, c1, c2)
    ax1.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.0f}'))
    ax2.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.0f}'))
    set_xlim_to_data(ax1, vix.index)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    add_last_value_label(ax1, vvix, color=c1, fmt='{:.1f}', side='left')
    add_last_value_label(ax2, vix, color=c2, fmt='{:.1f}', side='right')
    add_recessions(ax1, start_date='2007-12-01')

    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax1.legend(h1 + h2, l1 + l2, loc='upper right', **legend_style())

    add_annotation_box(ax1,
        "When VIX is low but VVIX is rising,\n"
        "the market is mispricing tail risk.\n"
        "VVIX divergences are early warnings.",
        x=0.52, y=0.92)

    brand_fig(fig, 'Volatility and the Volatility of Volatility',
              subtitle='VIX vs VVIX | When Vol Is Mispriced, VVIX Warns First',
              source='CBOE via FRED',
              data_date=vix.index[-1])

    return save_fig(fig, 'chart_09_vix_vvix.png')


# ============================================
# CHART 10: FCI Composite (Proprietary) [Figure 10]
# ============================================
def chart_10():
    """Financial Conditions Index, proprietary composite with regime bands."""
    print('\nChart 10: FCI Composite...')

    fci = fetch_db_index('FCI', start='1975-01-01')

    if len(fci) == 0:
        print('  No FCI data available. Skipping.')
        return None

    fig, ax = new_fig()

    ax.plot(fci.index, fci, color=THEME['primary'], linewidth=2.0,
            label=f'FCI ({fci.iloc[-1]:.2f})')

    # Regime bands
    y_max = max(fci.max() + 0.5, 2.0)
    y_min = min(fci.min() - 0.5, -2.0)

    ax.axhspan(1.0, y_max, color=COLORS['starboard'], alpha=0.08)
    ax.axhspan(0.5, 1.0, color=COLORS['starboard'], alpha=0.04)
    ax.axhspan(-0.5, 0.5, color=COLORS['doldrums'], alpha=0.03)
    ax.axhspan(-1.0, -0.5, color=COLORS['port'], alpha=0.04)
    ax.axhspan(y_min, -1.0, color=COLORS['port'], alpha=0.08)

    # Regime labels on right edge
    ax.text(fci.index[-1] + pd.Timedelta(days=30), 1.25, 'Very Loose',
            fontsize=8, color=COLORS['starboard'], va='center')
    ax.text(fci.index[-1] + pd.Timedelta(days=30), 0.75, 'Loose',
            fontsize=8, color=COLORS['starboard'], va='center')
    ax.text(fci.index[-1] + pd.Timedelta(days=30), 0.0, 'Neutral',
            fontsize=8, color=COLORS['doldrums'], va='center')
    ax.text(fci.index[-1] + pd.Timedelta(days=30), -0.75, 'Tight',
            fontsize=8, color=COLORS['port'], va='center')
    ax.text(fci.index[-1] + pd.Timedelta(days=30), -1.25, 'Crisis',
            fontsize=8, color=COLORS['port'], va='center')

    # Zero line
    ax.axhline(0, color=THEME['zero_line'], linewidth=0.8, linestyle='--', alpha=0.5)

    style_single_ax(ax, fmt='{:.1f}')
    set_xlim_to_data(ax, fci.index)
    ax.set_ylim(y_min, y_max)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    add_last_value_label(ax, fci, color=THEME['primary'], fmt='{:.2f}', side='right')
    add_recessions(ax, start_date='1975-01-01')
    ax.legend(loc='upper left', **legend_style())

    add_annotation_box(ax,
        f"FCI at {fci.iloc[-1]:.2f}.\n"
        "Synthesizes spreads, curve, lending,\n"
        "and liquidity into a single number.",
        x=0.52, y=0.92)

    brand_fig(fig, 'Financial Conditions Index (FCI)',
              subtitle='Lighthouse Macro Proprietary | Synthesizing Spreads, Curve, Lending, and Liquidity',
              source='Lighthouse Macro Proprietary',
              data_date=fci.index[-1])

    return save_fig(fig, 'chart_10_fci.png')


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
}


def main():
    parser = argparse.ArgumentParser(description='Generate Financial Conditions educational charts')
    parser.add_argument('--chart', type=int, help='Chart number to generate (1-10)')
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
