#!/usr/bin/env python3
"""
Generate Charts for Educational Series: Post 8 - Government (Pillar 8)
=====================================================================
9 charts covering: deficit/GDP, term premium, 10Y decomposition,
interest expense (% revenue and nominal), debt-to-GDP, fiscal impulse,
GCI-Gov composite, and foreign holdings share.

Generates BOTH white and dark theme versions.

Usage:
    python government_edu_charts.py --chart 1
    python government_edu_charts.py --chart 1 --theme dark
    python government_edu_charts.py --all
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
OUTPUT_BASE = f'{BASE_PATH}/Outputs/Educational_Charts/Government_Post_8'
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
# CHART 1: Federal Deficit (% of GDP) [Figure 1]
# ============================================
def chart_01():
    """Federal Surplus/Deficit as % of GDP, long history with recession shading."""
    print('\nChart 1: Federal Deficit (% of GDP)...')

    deficit = fetch_fred_level('FYFSGDA188S', start='1950-01-01')

    fig, ax = new_fig()

    ax.plot(deficit.index, deficit, color=THEME['primary'], linewidth=2.5,
            label=f'Federal Deficit/GDP ({deficit.iloc[-1]:.1f}%)')

    # Fill deficit area (negative values)
    ax.fill_between(deficit.index, 0, deficit,
                    where=(deficit < 0),
                    color=COLORS['port'], alpha=0.15)
    # Fill surplus area
    ax.fill_between(deficit.index, 0, deficit,
                    where=(deficit > 0),
                    color=COLORS['starboard'], alpha=0.15)

    # Zero line
    ax.axhline(0, color=THEME['zero_line'], linewidth=0.8, linestyle='--', alpha=0.5)

    # Historical norm reference (-3%)
    ax.axhline(-3, color=COLORS['doldrums'], linewidth=1.0, linestyle=':',
               alpha=0.6)
    ax.text(deficit.index[2], -3.5, 'Historical norm (~3% deficit)',
            fontsize=9, color=COLORS['doldrums'], style='italic')

    style_single_ax(ax)
    set_xlim_to_data(ax, deficit.index)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    add_last_value_label(ax, deficit, color=THEME['primary'], side='right')
    add_recessions(ax, start_date='1950-01-01')
    ax.legend(loc='lower left', **legend_style())

    add_annotation_box(ax,
        f"Running {abs(deficit.iloc[-1]):.0f}% of GDP deficits\n"
        f"outside of recession.\n"
        f"This is structural, not cyclical.",
        x=0.50, y=0.18)

    brand_fig(fig, 'Federal Surplus/Deficit as % of GDP',
              subtitle='Structural deficits at full employment',
              source='Office of Management and Budget via FRED',
              data_date=deficit.index[-1])

    return save_fig(fig, 'chart_01_deficit_gdp.png')


# ============================================
# CHART 2: ACM 10-Year Term Premium [Figure 2]
# ============================================
def chart_02():
    """10-Year Term Premium (ACM Model), long history."""
    print('\nChart 2: ACM 10-Year Term Premium...')

    tp = fetch_fred_level('THREEFYTP10', start='1961-01-01')

    fig, ax = new_fig()

    ax.plot(tp.index, tp, color=THEME['primary'], linewidth=2.0,
            label=f'10Y Term Premium ACM ({tp.iloc[-1]:.2f}%)')

    # Fill positive (normal) vs negative (suppressed)
    ax.fill_between(tp.index, 0, tp,
                    where=(tp > 0),
                    color=COLORS['ocean'], alpha=THEME['fill_alpha'])
    ax.fill_between(tp.index, 0, tp,
                    where=(tp < 0),
                    color=COLORS['venus'], alpha=0.10)

    # Zero line
    ax.axhline(0, color=THEME['zero_line'], linewidth=0.8, linestyle='--', alpha=0.5)

    # Target level (1.5%)
    ax.axhline(1.5, color=COLORS['venus'], linewidth=1.5, linestyle='-',
               alpha=0.8)
    ax.text(tp.index[-1] - pd.Timedelta(days=3000), 1.65,
            'LHM Target: ~150 bps',
            fontsize=9, color=COLORS['venus'], fontweight='bold')

    style_single_ax(ax)
    set_xlim_to_data(ax, tp.index)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    add_last_value_label(ax, tp, color=THEME['primary'], fmt='{:.2f}%', side='right')
    add_recessions(ax, start_date='1961-01-01')
    ax.legend(loc='upper right', **legend_style())

    add_annotation_box(ax,
        "Term premium is the 'honest signal.'\n"
        "Post-QE suppression is normalizing.\n"
        "Still below what structural deficits demand.",
        x=0.50, y=0.93)

    brand_fig(fig, 'ACM 10-Year Term Premium',
              subtitle='The honest signal of fiscal sustainability',
              source='NY Fed / Adrian, Crump & Moench via FRED',
              data_date=tp.index[-1])

    return save_fig(fig, 'chart_02_term_premium.png')


# ============================================
# CHART 3: 10Y Yield Decomposition [Figure 3]
# ============================================
def chart_03():
    """10Y Yield = Expected Short Rate + Term Premium decomposition."""
    print('\nChart 3: 10Y Yield Decomposition...')

    tp = fetch_fred_level('THREEFYTP10', start='1990-01-01')
    y10 = fetch_fred_level('DGS10', start='1990-01-01')

    # Align dates
    idx = tp.index.intersection(y10.index)
    tp = tp.loc[idx]
    y10 = y10.loc[idx]
    expected = y10 - tp

    fig, ax1 = new_fig()
    ax2 = ax1.twinx()
    c1, c2 = THEME['secondary'], THEME['primary']

    ax1.plot(expected.index, expected, color=c1, linewidth=2.0,
             label=f'Expected Short Rate ({expected.iloc[-1]:.2f}%)')
    ax2.plot(tp.index, tp, color=c2, linewidth=2.5,
             label=f'Term Premium ({tp.iloc[-1]:.2f}%)')

    # Reference: actual 10Y
    ax2.plot(y10.index, y10, color=COLORS['doldrums'], linewidth=1.0,
             linestyle=':', alpha=0.5, label=f'10Y Yield ({y10.iloc[-1]:.2f}%)')

    # Zero line on TP axis
    ax2.axhline(0, color=THEME['zero_line'], linewidth=0.8, linestyle='--', alpha=0.3)

    style_dual_ax(ax1, ax2, c1, c2)
    ax1.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.1f}%'))
    ax2.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.1f}%'))
    set_xlim_to_data(ax1, tp.index)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    add_last_value_label(ax1, expected, color=c1, fmt='{:.2f}%', side='left')
    add_last_value_label(ax2, tp, color=c2, fmt='{:.2f}%', side='right')
    add_recessions(ax1, start_date='1990-01-01')

    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax1.legend(h1 + h2, l1 + l2, loc='upper left', **legend_style())

    add_annotation_box(ax1,
        "A 4.5% yield driven by rate expectations\n"
        "is different from 4.5% driven by term premium.\n"
        "The composition shift is the story.",
        x=0.52, y=0.92)

    brand_fig(fig, '10-Year Yield Decomposition',
              subtitle='Expected rate vs. term premium: what is driving yields?',
              source='NY Fed ACM Model, Federal Reserve via FRED',
              data_date=tp.index[-1])

    return save_fig(fig, 'chart_03_yield_decomposition.png')


# ============================================
# CHART 4: Federal Interest Expense (% of Revenue) [Figure 4]
# ============================================
def chart_04():
    """Federal interest payments as % of federal receipts."""
    print('\nChart 4: Federal Interest Expense (% of Revenue)...')

    # Quarterly BEA data: interest payments and receipts
    interest = fetch_fred_level('A091RC1Q027SBEA', start='1950-01-01')
    receipts = fetch_fred_level('FGRECPT', start='1950-01-01')

    # Align
    idx = interest.index.intersection(receipts.index)
    interest = interest.loc[idx]
    receipts = receipts.loc[idx]
    ratio = (interest / receipts) * 100

    fig, ax = new_fig()

    ax.plot(ratio.index, ratio, color=THEME['primary'], linewidth=2.5,
            label=f'Interest / Revenue ({ratio.iloc[-1]:.1f}%)')
    ax.fill_between(ratio.index, 0, ratio,
                    color=COLORS['ocean'], alpha=THEME['fill_alpha'])

    style_single_ax(ax)
    set_xlim_to_data(ax, ratio.index)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    add_last_value_label(ax, ratio, color=THEME['primary'], side='right')
    add_recessions(ax, start_date='1950-01-01')
    ax.legend(loc='upper left', **legend_style())

    add_annotation_box(ax,
        "Interest as a share of revenue is rising\n"
        "back toward early-1990s peaks.\n"
        "The compounding trap is real.",
        x=0.52, y=0.25)

    brand_fig(fig, 'Federal Interest Expense as % of Revenue',
              subtitle='The compounding trap: higher rates on a larger debt stock',
              source='BEA via FRED',
              data_date=ratio.index[-1])

    return save_fig(fig, 'chart_04_interest_pct_revenue.png')


# ============================================
# CHART 5: Federal Interest Expense (Nominal, $B Annual) [Figure 5]
# ============================================
def chart_05():
    """Federal interest outlays in nominal dollars (annual)."""
    print('\nChart 5: Federal Interest Expense (Nominal)...')

    # Use annual series for clean long history
    interest = fetch_fred_level('FYOINT', start='1950-01-01')

    fig, ax = new_fig()

    ax.plot(interest.index, interest / 1e3, color=THEME['primary'], linewidth=2.5,
            label=f'Interest on Debt (${interest.iloc[-1]/1e3:.0f}B)')
    ax.fill_between(interest.index, 0, interest / 1e3,
                    color=COLORS['ocean'], alpha=THEME['fill_alpha'])

    style_single_ax(ax, fmt='${:.0f}B')
    set_xlim_to_data(ax, interest.index)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    add_last_value_label(ax, interest / 1e3, color=THEME['primary'],
                         fmt='${:.0f}B', side='right')
    add_recessions(ax, start_date='1950-01-01')
    ax.legend(loc='upper left', **legend_style())

    add_annotation_box(ax,
        "Interest payments have surpassed\n"
        "defense spending. Approaching $1T annually.\n"
        "This is the doom loop in action.",
        x=0.35, y=0.92)

    brand_fig(fig, 'Federal Government Interest Outlays',
              subtitle='Now larger than defense spending',
              source='Office of Management and Budget via FRED',
              data_date=interest.index[-1])

    return save_fig(fig, 'chart_05_interest_nominal.png')


# ============================================
# CHART 6: Debt-to-GDP Ratio [Figure 6]
# ============================================
def chart_06():
    """Gross Federal Debt as % of GDP, full history including WWII context."""
    print('\nChart 6: Debt-to-GDP Ratio...')

    debt_gdp = fetch_fred_level('GFDEGDQ188S', start='1966-01-01')

    fig, ax = new_fig()

    ax.plot(debt_gdp.index, debt_gdp, color=THEME['primary'], linewidth=2.5,
            label=f'Debt / GDP ({debt_gdp.iloc[-1]:.0f}%)')
    ax.fill_between(debt_gdp.index, 0, debt_gdp,
                    color=COLORS['ocean'], alpha=THEME['fill_alpha'])

    # 100% reference line
    ax.axhline(100, color=COLORS['venus'], linewidth=1.5, linestyle='-',
               alpha=0.7)
    ax.text(debt_gdp.index[5], 103, '100% of GDP',
            fontsize=9, color=COLORS['venus'], fontweight='bold')

    style_single_ax(ax, fmt='{:.0f}%')
    set_xlim_to_data(ax, debt_gdp.index)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    add_last_value_label(ax, debt_gdp, color=THEME['primary'],
                         fmt='{:.0f}%', side='right')
    add_recessions(ax, start_date='1966-01-01')
    ax.legend(loc='upper left', **legend_style())

    add_annotation_box(ax,
        f"Debt-to-GDP at {debt_gdp.iloc[-1]:.0f}%.\n"
        f"Highest since WWII, but trajectory\n"
        f"is the real concern: 120%+ by 2030.",
        x=0.52, y=0.93)

    brand_fig(fig, 'Federal Debt as % of GDP',
              subtitle='The level matters less than the trajectory',
              source='Federal Reserve via FRED',
              data_date=debt_gdp.index[-1])

    return save_fig(fig, 'chart_06_debt_to_gdp.png')


# ============================================
# CHART 7: Fiscal Impulse (YoY Change in Deficit) [Figure 7]
# ============================================
def chart_07():
    """Fiscal impulse: YoY change in trailing 12-month deficit."""
    print('\nChart 7: Fiscal Impulse...')

    # Monthly Treasury Statement deficit (cumulative 12M rolling)
    # MTSDS133FMS is in millions, convert to billions
    monthly_def = fetch_fred_level('MTSDS133FMS', start='1980-01-01') / 1000.0

    # Trailing 12-month rolling sum
    rolling_12m = monthly_def.rolling(12).sum()
    # YoY change in the 12M rolling deficit
    impulse = rolling_12m.diff(12)
    impulse = impulse.dropna()

    fig, ax = new_fig()

    # Bar chart: positive = stimulative (green), negative = drag (red)
    pos = impulse.clip(lower=0)
    neg = impulse.clip(upper=0)

    ax.fill_between(impulse.index, 0, pos,
                    color=COLORS['starboard'], alpha=0.5, label='Fiscal stimulus')
    ax.fill_between(impulse.index, 0, neg,
                    color=COLORS['port'], alpha=0.5, label='Fiscal drag')
    ax.plot(impulse.index, impulse, color=THEME['primary'], linewidth=1.5, alpha=0.7)

    # Zero line
    ax.axhline(0, color=THEME['zero_line'], linewidth=0.8, linestyle='--', alpha=0.5)

    style_single_ax(ax, fmt='${:.0f}B')
    set_xlim_to_data(ax, impulse.index)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    add_last_value_label(ax, impulse, color=THEME['primary'],
                         fmt='${:.0f}B', side='right')
    add_recessions(ax, start_date='1981-01-01')
    ax.legend(loc='upper left', **legend_style())

    add_annotation_box(ax,
        "Positive = government adding to demand.\n"
        "Negative = fiscal drag on growth.\n"
        "Spending cuts are contractionary by definition.",
        x=0.52, y=0.92)

    brand_fig(fig, 'Fiscal Impulse: Year-Over-Year Change in Deficit',
              subtitle='The second derivative of government spending',
              source='Monthly Treasury Statement via FRED',
              data_date=impulse.index[-1])

    return save_fig(fig, 'chart_07_fiscal_impulse.png')


# ============================================
# CHART 8: GCI-Gov Composite [Figure 8]
# ============================================
def chart_08():
    """GCI-Gov composite index from lighthouse_indices."""
    print('\nChart 8: GCI-Gov Composite...')

    # Try DB first
    gcigov = fetch_db_level('GCI_Gov', start='1990-01-01')

    if len(gcigov) == 0:
        # Fallback: try lighthouse_indices table
        try:
            conn = sqlite3.connect(DB_PATH)
            df = pd.read_sql(
                "SELECT date, value FROM lighthouse_indices "
                "WHERE index_id = 'GCI_Gov' AND date >= '1990-01-01' ORDER BY date",
                conn
            )
            conn.close()
            df['date'] = pd.to_datetime(df['date'])
            df = df.set_index('date')
            gcigov = df['value'].dropna()
        except Exception as e:
            print(f'  Warning: Could not load GCI_Gov: {e}')
            print('  Skipping chart 8.')
            return None

    if len(gcigov) == 0:
        print('  No GCI_Gov data available. Skipping.')
        return None

    fig, ax = new_fig()

    ax.plot(gcigov.index, gcigov, color=THEME['primary'], linewidth=2.0,
            label=f'GCI-Gov ({gcigov.iloc[-1]:.2f})')

    # Regime bands
    ax.axhspan(1.0, gcigov.max() + 0.5, color=COLORS['port'], alpha=0.08)
    ax.axhspan(0.5, 1.0, color=COLORS['dusk'], alpha=0.08)
    ax.axhspan(-0.5, 0.5, color=COLORS['doldrums'], alpha=0.05)
    ax.axhspan(gcigov.min() - 0.5, -0.5, color=COLORS['starboard'], alpha=0.08)

    # Regime labels
    ax.text(gcigov.index[-1] + pd.Timedelta(days=30), 1.25, 'High Stress',
            fontsize=8, color=COLORS['port'], va='center')
    ax.text(gcigov.index[-1] + pd.Timedelta(days=30), 0.75, 'Elevated',
            fontsize=8, color=COLORS['dusk'], va='center')
    ax.text(gcigov.index[-1] + pd.Timedelta(days=30), 0.0, 'Normal',
            fontsize=8, color=COLORS['doldrums'], va='center')
    ax.text(gcigov.index[-1] + pd.Timedelta(days=30), -0.75, 'Fiscal Health',
            fontsize=8, color=COLORS['starboard'], va='center')

    # Zero line
    ax.axhline(0, color=THEME['zero_line'], linewidth=0.8, linestyle='--', alpha=0.3)

    style_single_ax(ax, fmt='{:.1f}')
    set_xlim_to_data(ax, gcigov.index)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    add_last_value_label(ax, gcigov, color=THEME['primary'],
                         fmt='{:.2f}', side='right')
    add_recessions(ax, start_date='1990-01-01')
    ax.legend(loc='upper left', **legend_style())

    add_annotation_box(ax,
        f"GCI-Gov at {gcigov.iloc[-1]:.2f}.\n"
        "Positive = fiscal stress rising.\n"
        "Synthesizes deficit, debt, interest, term premium.",
        x=0.35, y=0.93)

    brand_fig(fig, 'Government Conditions Index (GCI-Gov)',
              subtitle='Pillar 8 Composite: fiscal stress in a single number',
              source='Lighthouse Macro Proprietary',
              data_date=gcigov.index[-1])

    return save_fig(fig, 'chart_08_gci_gov.png')


# ============================================
# CHART 9: Foreign Holdings Share [Figure 9]
# ============================================
def chart_09():
    """Federal debt held by foreign investors as share of total."""
    print('\nChart 9: Foreign Holdings Share...')

    foreign = fetch_fred_level('FDHBFIN', start='1970-01-01')  # Billions
    total = fetch_fred_level('GFDEBTN', start='1970-01-01')    # Millions

    # Convert total to billions to match foreign
    total = total / 1000.0

    # Align
    idx = foreign.index.intersection(total.index)
    foreign = foreign.loc[idx]
    total = total.loc[idx]
    share = (foreign / total) * 100

    fig, ax = new_fig()

    ax.plot(share.index, share, color=THEME['primary'], linewidth=2.5,
            label=f'Foreign Share of Debt ({share.iloc[-1]:.1f}%)')
    ax.fill_between(share.index, 0, share,
                    color=COLORS['ocean'], alpha=THEME['fill_alpha'])

    style_single_ax(ax)
    set_xlim_to_data(ax, share.index)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    add_last_value_label(ax, share, color=THEME['primary'], side='right')
    add_recessions(ax, start_date='1970-01-01')
    ax.legend(loc='upper left', **legend_style())

    add_annotation_box(ax,
        "Foreign demand for Treasuries peaked\n"
        "around 2014 and has been declining.\n"
        "The marginal buyer is now price-sensitive.",
        x=0.40, y=0.92)

    brand_fig(fig, 'Foreign Holdings as Share of Federal Debt',
              subtitle='The marginal buyer has changed',
              source='Federal Reserve via FRED',
              data_date=share.index[-1])

    return save_fig(fig, 'chart_09_foreign_holdings.png')


# ============================================
# CHART 10: Receipts vs. Outlays (The Structural Gap) [Figure 10]
# ============================================
def chart_10():
    """Federal receipts vs. outlays showing the structural divergence."""
    print('\nChart 10: Receipts vs. Outlays...')

    # Monthly Treasury Statement: receipts and outlays in millions -> billions
    receipts = fetch_fred_level('MTSR133FMS', start='1980-01-01') / 1000.0
    outlays = fetch_fred_level('MTSO133FMS', start='1980-01-01') / 1000.0

    # Trailing 12-month rolling sums for smoothing
    r12 = receipts.rolling(12).sum().dropna()
    o12 = outlays.rolling(12).sum().dropna()

    # Align
    idx = r12.index.intersection(o12.index)
    r12 = r12.loc[idx]
    o12 = o12.loc[idx]

    fig, ax = new_fig()

    ax.plot(r12.index, r12, color=COLORS['starboard'], linewidth=2.5,
            label=f'Receipts 12M (${r12.iloc[-1]:,.0f}B)')
    ax.plot(o12.index, o12, color=COLORS['port'], linewidth=2.5,
            label=f'Outlays 12M (${o12.iloc[-1]:,.0f}B)')

    # Fill the gap
    ax.fill_between(o12.index, r12, o12,
                    where=(o12 > r12),
                    color=COLORS['port'], alpha=0.12,
                    label='Deficit')
    ax.fill_between(o12.index, r12, o12,
                    where=(r12 >= o12),
                    color=COLORS['starboard'], alpha=0.12,
                    label='Surplus')

    style_single_ax(ax, fmt='${:,.0f}B')
    set_xlim_to_data(ax, r12.index)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    add_last_value_label(ax, r12, color=COLORS['starboard'],
                         fmt='${:,.0f}B', side='right')
    add_last_value_label(ax, o12, color=COLORS['port'],
                         fmt='${:,.0f}B', side='right')
    add_recessions(ax, start_date='1981-01-01')
    ax.legend(loc='upper left', **legend_style())

    gap = o12.iloc[-1] - r12.iloc[-1]
    add_annotation_box(ax,
        f"The gap: ${gap:,.0f}B in annual deficit.\n"
        f"Outlays growing faster than receipts.\n"
        f"The scissors are opening, not closing.",
        x=0.40, y=0.45)

    brand_fig(fig, 'Federal Receipts vs. Outlays (Trailing 12 Months)',
              subtitle='The structural gap: spending outpaces revenue',
              source='Monthly Treasury Statement via FRED',
              data_date=r12.index[-1])

    return save_fig(fig, 'chart_10_receipts_vs_outlays.png')


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
    parser = argparse.ArgumentParser(description='Generate Government educational charts')
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
