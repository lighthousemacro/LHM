#!/usr/bin/env python3
"""
Generate Charts for Educational Series: Post 6 - Business (Pillar 6)
=====================================================================
Generates BOTH white and dark theme versions.
Matches format from Consumer: THE SPENDING ENGINE charts.

Usage:
    python business_edu_charts.py --chart 1
    python business_edu_charts.py --chart 1 --theme dark
    python business_edu_charts.py --all
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
OUTPUT_BASE = f'{BASE_PATH}/Outputs/Educational_Charts/Business_Post_6'
DB_PATH = f'{BASE_PATH}/Data/databases/Lighthouse_Master.db'

fred = Fred()

# Simple cache to avoid refetching same data across themes
_DATA_CACHE = {}

COLORS = {
    'ocean': '#0089D1',
    'dusk': '#FF6723',
    'sky': '#33CCFF',
    'venus': '#FF2389',
    'sea': '#00BB99',
    'doldrums': '#D3D6D9',
    'starboard': '#00FF00',
    'port': '#FF0000',
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
            'spine': '#cccccc',
            'zero_line': '#333333',
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


def fetch_db(series_id, start='2000-01-01'):
    """Fetch a series from the master DB (for TradingView and other non-FRED data)."""
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


def fetch_db_level(series_id, start='1950-01-01'):
    """Fetch DB series as-is (already a rate/level/index)."""
    df = fetch_db(series_id, start=start)
    if df.empty:
        return pd.Series(dtype=float)
    return df['value'].dropna()


def yoy_pct(df, col='value'):
    """Compute YoY % change from index level."""
    return df[col].pct_change(12, fill_method=None) * 100


def fetch_fred_yoy(series_id, start='1949-01-01', trim=None):
    """Fetch FRED series, compute YoY%, drop NaN, trim to start date."""
    df = fetch_fred(series_id, start=start)
    df['yoy'] = yoy_pct(df)
    if trim:
        df = df.loc[trim:]
    return df['yoy'].dropna()


def fetch_fred_level(series_id, start='1950-01-01'):
    """Fetch FRED series as-is (already a rate/level, not an index)."""
    df = fetch_fred(series_id, start=start)
    return df['value'].dropna()


def fetch_quarterly_yoy(series_id, start='1949-01-01', trim=None):
    """Fetch quarterly FRED series, compute YoY (4-period), forward-fill to monthly."""
    df = fetch_fred(series_id, start=start)
    df['yoy'] = df['value'].pct_change(4, fill_method=None) * 100
    monthly = df['yoy'].resample('MS').ffill()
    if trim:
        monthly = monthly.loc[trim:]
    return monthly.dropna()


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
    # Dark theme: Ocean fill at 20% to pop against chart bg
    # White theme: keep chart bg
    if THEME['mode'] == 'dark':
        box_fc = '#0089D1'
        box_alpha = 1.0
    else:
        box_fc = THEME['bg']
        box_alpha = 0.9
    txt_color = '#ffffff' if THEME['mode'] == 'dark' else THEME['fg']
    ax.text(x, y, text, transform=ax.transAxes,
            fontsize=10, color=txt_color, ha='center', va='top',
            style='italic',
            bbox=dict(boxstyle='round,pad=0.5',
                      facecolor=box_fc, edgecolor='#33CCFF',
                      linewidth=2.0,
                      alpha=box_alpha))


def brand_fig(fig, title, subtitle=None, source=None, data_date=None):
    """Apply TT deck branding at figure level.

    Args:
        data_date: Latest observation date (str or pd.Timestamp). Shown as 'Data thru MM.DD.YYYY'.
    """
    fig.patch.set_facecolor(THEME['bg'])

    OCEAN = '#0089D1'
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
    fig.savefig(filepath, dpi=200, bbox_inches='tight', pad_inches=0.10,
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
# CHART 1: ISM Manufacturing PMI (The Headline) [Figure 1]
# ============================================
def chart_01():
    """ISM Manufacturing PMI with expansion/contraction threshold."""
    print('\nChart 1: ISM Manufacturing PMI...')

    pmi = fetch_db_level('TV_USISMMP', start='1950-01-01')

    fig, ax = new_fig()

    # Color the line by regime, interpolating exact crossing points at 50
    from matplotlib.collections import LineCollection
    threshold = 50
    x_vals = mdates.date2num(pmi.index)
    y_vals = pmi.values
    new_segments = []
    new_colors = []
    for i in range(len(x_vals) - 1):
        x0, y0 = x_vals[i], y_vals[i]
        x1, y1 = x_vals[i + 1], y_vals[i + 1]
        # Check if segment crosses the threshold
        if (y0 - threshold) * (y1 - threshold) < 0:
            # Interpolate the crossing point
            t = (threshold - y0) / (y1 - y0)
            x_cross = x0 + t * (x1 - x0)
            # First half
            new_segments.append([[x0, y0], [x_cross, threshold]])
            new_colors.append(COLORS['sea'] if y0 >= threshold else COLORS['venus'])
            # Second half
            new_segments.append([[x_cross, threshold], [x1, y1]])
            new_colors.append(COLORS['sea'] if y1 >= threshold else COLORS['venus'])
        else:
            new_segments.append([[x0, y0], [x1, y1]])
            new_colors.append(COLORS['sea'] if y0 >= threshold else COLORS['venus'])
    lc = LineCollection(new_segments, colors=new_colors, linewidths=2.5)
    ax.add_collection(lc)
    ax.autoscale()

    # Invisible plots for legend entries
    ax.plot([], [], color=COLORS['sea'], linewidth=2.5, label='Expansion (>50)')
    ax.plot([], [], color=COLORS['venus'], linewidth=2.5, label='Contraction (<50)')

    # Threshold line
    ax.axhline(50, color=COLORS['doldrums'], linewidth=1.5, linestyle='--', alpha=0.8)

    style_ax(ax, right_primary=True)
    ax.tick_params(axis='both', which='both', length=0)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.0f}'))
    set_xlim_to_data(ax, pmi.index)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    add_last_value_label(ax, pmi, color=COLORS['sea'] if pmi.iloc[-1] >= 50 else COLORS['venus'],
                         fmt='{:.1f}', side='right')
    add_recessions(ax)
    ax.legend(loc='upper left', **legend_style())

    pmi_last = pmi.iloc[-1]
    regime = "expansion" if pmi_last > 50 else "contraction"
    add_annotation_box(ax,
        f"ISM Manufacturing at {pmi_last:.1f} ({regime}).\n"
        f"Below 50 = contraction. Below 45 = deep recession signal.",
        x=0.63, y=0.92)

    brand_fig(fig, 'ISM Manufacturing PMI',
              subtitle='The earliest read on goods economy health',
              source='ISM via TradingView', data_date=pmi.index[-1])

    return save_fig(fig, 'chart_01_ism_manufacturing.png')


# ============================================
# CHART 2: ISM Manufacturing vs Services (The Bifurcation) [Figure 2]
# ============================================
def chart_02():
    """ISM Manufacturing vs Services PMI: the late-cycle divergence."""
    print('\nChart 2: ISM Manufacturing vs Services PMI...')

    mfg = fetch_db_level('TV_USISMMP')
    svc = fetch_db_level('TV_USBCOI')
    # Start from youngest series
    common_start = max(mfg.index[0], svc.index[0])
    mfg = mfg[mfg.index >= common_start]
    svc = svc[svc.index >= common_start]

    # Two-panel layout: top 65%, bottom 35%
    fig, (ax_top, ax_bot) = plt.subplots(2, 1, figsize=(14, 8),
        gridspec_kw={'height_ratios': [65, 35], 'hspace': 0.0})
    fig.patch.set_facecolor(THEME['bg'])
    ax_top.set_facecolor(THEME['bg'])
    ax_bot.set_facecolor(THEME['bg'])
    fig.subplots_adjust(top=0.88, bottom=0.08, left=0.06, right=0.94)

    # === TOP PANEL: Both PMI lines ===
    c1 = THEME['primary']
    c2 = THEME['secondary']
    ax_top.plot(mfg.index, mfg, color=c1, linewidth=2.5,
                label=f'ISM Manufacturing ({mfg.iloc[-1]:.1f})')
    ax_top.plot(svc.index, svc, color=c2, linewidth=2.5,
                label=f'ISM Services ({svc.iloc[-1]:.1f})')
    ax_top.axhline(50, color=COLORS['doldrums'], linewidth=1.0, linestyle='--', alpha=0.7)

    style_ax(ax_top, right_primary=True)
    ax_top.spines['bottom'].set_linewidth(4.0)  # Panel divider
    ax_top.tick_params(axis='both', which='both', length=0)
    ax_top.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.0f}'))
    set_xlim_to_data(ax_top, mfg.index)
    ax_top.set_xticklabels([])  # Hide x labels on top panel
    add_last_value_label(ax_top, mfg, color=c1, fmt='{:.1f}', side='right')
    add_last_value_label(ax_top, svc, color=c2, fmt='{:.1f}', side='right')
    add_recessions(ax_top)
    ax_top.legend(loc='upper right', **legend_style())

    spread_last_val = mfg.iloc[-1] - svc.iloc[-1]  # just for annotation
    add_annotation_box(ax_top,
        f"Manufacturing leads down by 6-9 months. Services follows.\n"
        f"Gap narrows as cycles mature.",
        x=0.58, y=0.12)

    # === BOTTOM PANEL: Services - Manufacturing spread ===
    combined = pd.DataFrame({'mfg': mfg, 'svc': svc}).dropna()
    spread = combined['svc'] - combined['mfg']
    c_spread = COLORS['sea']

    ax_bot.fill_between(spread.index, 0, spread, where=(spread >= 0),
                        color=c_spread, alpha=0.20)
    ax_bot.fill_between(spread.index, 0, spread, where=(spread < 0),
                        color=COLORS['venus'], alpha=0.20)
    ax_bot.plot(spread.index, spread, color=c_spread, linewidth=1.8,
                label=f'Spread: Svc \u2212 Mfg ({spread.iloc[-1]:+.1f})')
    ax_bot.axhline(0, color=COLORS['doldrums'], linewidth=1.0, linestyle='--', alpha=0.7)

    style_ax(ax_bot, right_primary=True)
    ax_bot.spines['top'].set_linewidth(4.0)  # Panel divider
    ax_bot.tick_params(axis='both', which='both', length=0)
    ax_bot.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:+.0f}'))
    set_xlim_to_data(ax_bot, spread.index)
    ax_bot.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    add_last_value_label(ax_bot, spread, color=c_spread, fmt='{:+.1f}', side='right')
    add_recessions(ax_bot)
    ax_bot.legend(loc='upper right', **legend_style())

    brand_fig(fig, 'ISM Manufacturing vs Services PMI',
              subtitle='The Late-Cycle Bifurcation: manufacturing leads, services follows',
              source='ISM via TradingView', data_date=mfg.index[-1])

    return save_fig(fig, 'chart_02_ism_bifurcation.png')


# ============================================
# CHART 3: ISM Manufacturing Subcomponents [Figure 3]
# ============================================
def chart_03():
    """ISM Manufacturing key subcomponents: New Orders, Employment, Prices."""
    print('\nChart 3: ISM Manufacturing Subcomponents...')

    new_orders = fetch_db_level('TV_USMNO')
    employment = fetch_db_level('TV_USMEMP')
    prices = fetch_db_level('TV_USMPR')
    # Start chart when all 3 series have data
    common_start = max(new_orders.index[0], employment.index[0], prices.index[0])
    new_orders = new_orders[new_orders.index >= common_start]
    employment = employment[employment.index >= common_start]
    prices = prices[prices.index >= common_start]

    fig, ax = new_fig()

    ax.plot(new_orders.index, new_orders, color=THEME['primary'], linewidth=2.5,
            label=f'New Orders ({new_orders.iloc[-1]:.1f})')
    ax.plot(employment.index, employment, color=THEME['secondary'], linewidth=2.5,
            label=f'Employment ({employment.iloc[-1]:.1f})')
    ax.plot(prices.index, prices, color=COLORS['sea'], linewidth=2.0,
            label=f'Prices Paid ({prices.iloc[-1]:.1f})')

    ax.axhline(50, color=COLORS['doldrums'], linewidth=1.0, linestyle='--', alpha=0.7)

    style_ax(ax, right_primary=True)
    ax.tick_params(axis='both', which='both', length=0)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.0f}'))
    set_xlim_to_data(ax, new_orders.index)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    add_last_value_label(ax, new_orders, color=THEME['primary'], fmt='{:.1f}', side='right')
    add_last_value_label(ax, employment, color=THEME['secondary'], fmt='{:.1f}', side='right')
    add_last_value_label(ax, prices, color=COLORS['sea'], fmt='{:.1f}', side='right')
    add_recessions(ax)
    ax.legend(loc='upper center', bbox_to_anchor=(0.50, 1.0), **legend_style())

    no_last = new_orders.iloc[-1]
    emp_last = employment.iloc[-1]
    add_annotation_box(ax,
        f"New Orders lead PMI by 1-2 months. Employment lags.\n"
        f"Orders {no_last:.1f}, Employment {emp_last:.1f}. "
        f"{'Employment contracting.' if emp_last < 50 else 'Employment expanding.'}",
        x=0.52, y=0.15)

    brand_fig(fig, 'ISM Manufacturing Subcomponents',
              subtitle='New Orders lead. Employment confirms. Prices signal inflation.',
              source='ISM via TradingView', data_date=new_orders.index[-1])

    return save_fig(fig, 'chart_03_ism_subcomponents.png')


# ============================================
# CHART 4: Core Capital Goods Orders vs Shipments (The Forward Commitment) [Figure 4]
# ============================================
def chart_04():
    """Core Capital Goods Orders (Nondefense ex-Aircraft) YoY: the purest capex signal."""
    print('\nChart 4: Core Capital Goods Orders YoY...')

    orders = fetch_fred_yoy('ANDENO')
    shipments = fetch_fred_yoy('ANXAVS')

    fig, ax = new_fig()

    ax.plot(orders.index, orders, color=THEME['primary'], linewidth=2.5,
            label=f'Core Capex Orders YoY ({orders.iloc[-1]:.1f}%)')
    ax.plot(shipments.index, shipments, color=THEME['secondary'], linewidth=2.0,
            label=f'Core Capex Shipments YoY ({shipments.iloc[-1]:.1f}%)')

    ax.fill_between(orders.index, 0, orders,
                    where=(orders < 0),
                    color=COLORS['venus'], alpha=0.10, label='Orders contracting')
    ax.axhline(0, color=COLORS['doldrums'], linewidth=0.8, alpha=0.5, linestyle='--')

    style_single_ax(ax)
    set_xlim_to_data(ax, orders.index)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    add_last_value_label(ax, orders, color=THEME['primary'], side='right')
    add_last_value_label(ax, shipments, color=THEME['secondary'], side='right')
    add_recessions(ax)
    ax.legend(loc='upper left', **legend_style())

    orders_last = orders.iloc[-1]
    ships_last = shipments.iloc[-1]
    spread = orders_last - ships_last
    add_annotation_box(ax,
        f"Orders {orders_last:+.1f}% vs Shipments {ships_last:+.1f}%.\n"
        f"Spread: {spread:+.1f}pp. Negative = backlog shrinking.",
        x=0.80, y=0.94)

    brand_fig(fig, 'Core Capital Goods: Orders vs Shipments',
              subtitle='The Forward Commitment: CEOs voting with their checkbooks',
              source='Census via FRED', data_date=orders.index[-1])

    return save_fig(fig, 'chart_04_core_capex_orders.png')


# ============================================
# CHART 5: Bookings/Billings Ratio [Figure 5]
# ============================================
def chart_05():
    """Bookings/Billings ratio (Orders / Shipments): demand vs supply balance."""
    print('\nChart 5: Bookings/Billings Ratio...')

    orders_df = fetch_fred('ANDENO')
    ships_df = fetch_fred('ANXAVS')

    ratio = (orders_df['value'] / ships_df['value']).dropna()
    ratio_3m = ratio.rolling(3, min_periods=1).mean()
    ratio_6m = ratio.rolling(6, min_periods=1).mean()

    fig, ax = new_fig()

    ax.plot(ratio.index, ratio, color=THEME['primary'], linewidth=0.8, alpha=0.2)
    ax.plot(ratio_3m.index, ratio_3m, color=THEME['primary'], linewidth=2.0,
            label=f'3-Month Avg ({ratio_3m.iloc[-1]:.2f}x)')
    ax.plot(ratio_6m.index, ratio_6m, color=COLORS['sea'], linewidth=2.5,
            label=f'6-Month Avg ({ratio_6m.iloc[-1]:.2f}x)')

    ax.axhline(1.0, color=COLORS['doldrums'], linewidth=1.0, linestyle='--', alpha=0.7,
               label='Equilibrium (1.0x)')
    ax.axhline(0.95, color=COLORS['venus'], linewidth=1.0, linestyle='-', alpha=0.7,
               label='Demand < Supply (<0.95x)')

    ax.fill_between(ratio_6m.index, 0.95, ratio_6m,
                    where=(ratio_6m < 0.95),
                    color=COLORS['venus'], alpha=0.10)

    style_ax(ax, right_primary=True)
    ax.tick_params(axis='both', which='both', length=0)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.2f}x'))
    set_xlim_to_data(ax, ratio_3m.index)
    # Cap y-axis top based on 3MMA max + padding
    y_top = ratio_3m.max() * 1.05
    ax.set_ylim(top=y_top)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    add_last_value_label(ax, ratio_3m, color=THEME['primary'],
                         fmt='{:.2f}x', side='right')
    add_last_value_label(ax, ratio_6m, color=COLORS['sea'],
                         fmt='{:.2f}x', side='right')
    add_recessions(ax)
    ax.legend(loc='upper left', **legend_style())

    last_val = ratio_6m.iloc[-1]
    status = "shrinking" if last_val < 1.0 else "growing"
    add_annotation_box(ax,
        f"Ratio at {last_val:.2f}x. Backlog {status}.\n"
        f"Below 0.95x = demand weaker than supply. Orders drying up.",
        x=0.78, y=0.98)

    brand_fig(fig, 'Core Capital Goods: Bookings/Billings Ratio',
              subtitle='When orders lag shipments, the backlog is dying',
              source='Census via FRED', data_date=ratio_3m.index[-1])

    return save_fig(fig, 'chart_05_bookings_billings.png')


# ============================================
# CHART 6: Durable Goods Orders [Figure 6]
# ============================================
def chart_06():
    """Durable Goods: Total vs Ex-Transportation YoY."""
    print('\nChart 6: Durable Goods Orders...')

    total = fetch_fred_yoy('DGORDER')
    ex_transport = fetch_fred_yoy('ADXTNO')

    fig, ax = new_fig()

    ax.plot(total.index, total, color=THEME['primary'], linewidth=2.5,
            label=f'Total Durables YoY ({total.iloc[-1]:.1f}%)')
    ax.plot(ex_transport.index, ex_transport, color=THEME['secondary'], linewidth=2.5,
            label=f'Ex-Transportation YoY ({ex_transport.iloc[-1]:.1f}%)')

    ax.axhline(0, color=COLORS['doldrums'], linewidth=0.8, alpha=0.5, linestyle='--')

    style_single_ax(ax)
    set_xlim_to_data(ax, total.index)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    add_last_value_label(ax, total, color=THEME['primary'], side='right')
    add_last_value_label(ax, ex_transport, color=THEME['secondary'], side='right')
    add_recessions(ax)
    ax.legend(loc='upper left', **legend_style())

    total_last = total.iloc[-1]
    ext_last = ex_transport.iloc[-1]
    add_annotation_box(ax,
        f"Total durables: {total_last:+.1f}% YoY. Ex-transport: {ext_last:+.1f}%.\n"
        f"Ex-transport strips Boeing volatility. The cleaner trend signal.",
        x=0.52, y=0.92)

    brand_fig(fig, 'Durable Goods Orders: Total vs Ex-Transportation',
              subtitle='Stripping Boeing noise reveals the underlying trend',
              source='Census via FRED', data_date=total.index[-1])

    return save_fig(fig, 'chart_06_durable_goods.png')


# ============================================
# CHART 7: Business Inventories & I/S Ratio [Figure 7]
# ============================================
def chart_07():
    """Business Inventories YoY and Inventory/Sales Ratio: the mistake detector."""
    print('\nChart 7: Inventories & I/S Ratio...')

    inv_yoy = fetch_fred_yoy('BUSINV')
    is_ratio = fetch_fred_level('ISRATIO')

    fig, ax1 = new_fig()
    ax2 = ax1.twinx()
    c1, c2 = THEME['secondary'], THEME['primary']

    ax1.plot(inv_yoy.index, inv_yoy, color=c1, linewidth=2.5,
             label=f'Business Inventories YoY ({inv_yoy.iloc[-1]:.1f}%)')

    # Center ratio around its historical average so it aligns with 0% on LHS
    is_mean = is_ratio.mean()
    is_centered = is_ratio - is_mean
    ax2.plot(is_centered.index, is_centered, color=c2, linewidth=2.5,
             label=f'Inventory/Sales Ratio ({is_ratio.iloc[-1]:.2f})')

    ax1.axhline(0, color=COLORS['doldrums'], linewidth=0.8, alpha=0.5, linestyle='--')
    # 1.40 threshold centered: 1.40 - mean
    ax2.axhline(1.40 - is_mean, color=COLORS['venus'], linewidth=1.0, linestyle='-', alpha=0.75)

    style_dual_ax(ax1, ax2, c1, c2)
    ax1.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.0f}%'))
    # Format RHS ticks back to actual ratio values
    ax2.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{(x + is_mean):.2f}'))
    align_yaxis_zero(ax1, ax2)
    set_xlim_to_data(ax1, inv_yoy.index)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    add_last_value_label(ax1, inv_yoy, color=c1, side='left')
    # Custom pill showing original ratio value at the centered position
    last_centered = float(is_centered.iloc[-1])
    pill = dict(boxstyle='round,pad=0.3', facecolor=c2, edgecolor=c2, alpha=0.95)
    ax2.annotate(f'{is_ratio.iloc[-1]:.2f}', xy=(1.0, last_centered),
                 xycoords=('axes fraction', 'data'),
                 fontsize=9, fontweight='bold', color='white',
                 ha='left', va='center', xytext=(6, 0),
                 textcoords='offset points', bbox=pill)
    # Label 1.40 threshold on RHS axis
    threshold_centered = 1.40 - is_mean
    pill_thresh = dict(boxstyle='round,pad=0.3', facecolor=COLORS['venus'], edgecolor=COLORS['venus'], alpha=0.75)
    ax2.annotate('Thr: 1.40', xy=(1.0, threshold_centered),
                 xycoords=('axes fraction', 'data'),
                 fontsize=9, fontweight='bold', color='white',
                 ha='left', va='center', xytext=(6, 0),
                 textcoords='offset points', bbox=pill_thresh)
    add_recessions(ax1)

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', **legend_style())

    is_last = is_ratio.iloc[-1]
    status = "elevated" if is_last > 1.38 else "balanced"
    add_annotation_box(ax1,
        f"I/S ratio at {is_last:.2f} ({status}). Threshold: 1.40.\n"
        f"When inventories build faster than sales, production cuts follow.",
        x=0.52, y=0.92)

    brand_fig(fig, 'Business Inventories & Inventory/Sales Ratio',
              subtitle='The Mistake Detector: overstock signals liquidation ahead',
              source='Census via FRED', data_date=is_ratio.index[-1])

    return save_fig(fig, 'chart_07_inventories.png')


# ============================================
# CHART 8: Regional Fed Manufacturing Surveys (5-Survey) [Figure 8]
# ============================================
def chart_08():
    """Regional Fed Surveys: Empire, Philly, Dallas, Richmond, KC composite view."""
    print('\nChart 8: Regional Fed Manufacturing Surveys (5-Survey)...')

    # FRED sources
    empire = fetch_fred_level('GACDISA066MSFRBNY')
    philly = fetch_fred_level('GACDFSA066MSFRBPHI')
    dallas = fetch_fred_level('BACTSAMFRBDAL')
    # TradingView sources
    richmond = fetch_db_level('TV_USRFMI')
    kc = fetch_db_level('TV_USKFMI')

    fig, ax = new_fig()

    ax.plot(empire.index, empire, color=THEME['primary'], linewidth=1.5, alpha=0.7,
            label=f'Empire ({empire.iloc[-1]:.0f})')
    ax.plot(philly.index, philly, color=THEME['secondary'], linewidth=1.5, alpha=0.7,
            label=f'Philly ({philly.iloc[-1]:.0f})')
    ax.plot(dallas.index, dallas, color=THEME['tertiary'], linewidth=1.5, alpha=0.7,
            label=f'Dallas ({dallas.iloc[-1]:.0f})')
    ax.plot(richmond.index, richmond, color=THEME['quaternary'], linewidth=1.5, alpha=0.7,
            label=f'Richmond ({richmond.iloc[-1]:.0f})')
    ax.plot(kc.index, kc, color=COLORS['venus'], linewidth=1.5, alpha=0.7,
            label=f'KC ({kc.iloc[-1]:.0f})')

    # 5-survey average
    combined = pd.DataFrame({
        'empire': empire, 'philly': philly, 'dallas': dallas,
        'richmond': richmond, 'kc': kc
    }).dropna()
    avg = combined.mean(axis=1)
    ax.plot(avg.index, avg, color=THEME['fg'], linewidth=3.5, alpha=0.9,
            label=f'5-Survey Avg ({avg.iloc[-1]:.1f})')

    ax.axhline(0, color=COLORS['doldrums'], linewidth=1.5, linestyle='--', alpha=0.7)
    ax.axhspan(ax.get_ylim()[0], 0, color=COLORS['venus'], alpha=0.03)

    style_ax(ax, right_primary=True)
    ax.tick_params(axis='both', which='both', length=0)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.0f}'))
    set_xlim_to_data(ax, avg.index)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    # Custom pill for avg line - need dark text on light pill (and vice versa)
    last_avg = float(avg.iloc[-1])
    pill_fg = dict(boxstyle='round,pad=0.3', facecolor=THEME['fg'], edgecolor=THEME['fg'], alpha=0.95)
    ax.annotate(f'{last_avg:.1f}', xy=(1.0, last_avg),
                xycoords=('axes fraction', 'data'),
                fontsize=9, fontweight='bold', color=THEME['bg'],
                ha='left', va='center', xytext=(6, 0),
                textcoords='offset points', bbox=pill_fg)
    add_recessions(ax, start_date='2005-01-01')
    ax.legend(loc='upper left', **legend_style(), fontsize=8, ncol=2)

    avg_last = avg.iloc[-1]
    signal = "contraction" if avg_last < 0 else "expansion"
    add_annotation_box(ax,
        f"5-survey average at {avg_last:.1f} ({signal}).\n"
        f"Regional surveys preview ISM by 2-3 weeks. Below zero = manufacturing shrinking.",
        x=0.45, y=0.08)

    brand_fig(fig, 'Regional Fed Manufacturing Surveys',
              subtitle='ISM Preview: five districts tell one story',
              source='NY Fed, Philly Fed, Dallas Fed, Richmond Fed, KC Fed',
              data_date=avg.index[-1])

    return save_fig(fig, 'chart_08_regional_fed.png')


# ============================================
# CHART 9: Industrial Production & Capacity Utilization [Figure 9]
# ============================================
def chart_09():
    """Industrial Production YoY and Manufacturing Capacity Utilization."""
    print('\nChart 9: Industrial Production & Capacity Utilization...')

    ip_yoy = fetch_fred_yoy('INDPRO')
    cap_util = fetch_fred_level('MCUMFN')
    # Start when both series have data
    common_start = max(ip_yoy.index[0], cap_util.index[0])
    ip_yoy = ip_yoy[ip_yoy.index >= common_start]
    cap_util = cap_util[cap_util.index >= common_start]

    fig, ax1 = new_fig()
    ax2 = ax1.twinx()
    c1, c2 = THEME['secondary'], THEME['primary']

    ax1.plot(ip_yoy.index, ip_yoy, color=c1, linewidth=2.5,
             label=f'Industrial Production YoY ({ip_yoy.iloc[-1]:.1f}%)')

    # Center capacity util on its historical mean so it aligns with 0% on LHS
    cu_mean = cap_util.mean()
    cu_centered = cap_util - cu_mean
    ax2.plot(cu_centered.index, cu_centered, color=c2, linewidth=2.5,
             label=f'Mfg Capacity Util. ({cap_util.iloc[-1]:.1f}%)')

    ax1.axhline(0, color=COLORS['doldrums'], linewidth=0.8, alpha=0.5, linestyle='--')
    ax2.axhline(78 - cu_mean, color=COLORS['venus'], linewidth=1.0, linestyle='-', alpha=0.75)

    style_dual_ax(ax1, ax2, c1, c2)
    ax1.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.0f}%'))
    # Format RHS ticks back to actual capacity util values
    ax2.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{(x + cu_mean):.0f}%'))
    align_yaxis_zero(ax1, ax2)
    set_xlim_to_data(ax1, ip_yoy.index)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    add_last_value_label(ax1, ip_yoy, color=c1, side='left')
    # Custom pill showing original cap util value at centered position
    last_centered = float(cu_centered.iloc[-1])
    pill_cu = dict(boxstyle='round,pad=0.3', facecolor=c2, edgecolor=c2, alpha=0.95)
    ax2.annotate(f'{cap_util.iloc[-1]:.1f}%', xy=(1.0, last_centered),
                 xycoords=('axes fraction', 'data'),
                 fontsize=9, fontweight='bold', color='white',
                 ha='left', va='center', xytext=(6, 0),
                 textcoords='offset points', bbox=pill_cu)
    # 78% threshold label
    thresh_centered = 78 - cu_mean
    pill_thresh = dict(boxstyle='round,pad=0.3', facecolor=COLORS['venus'], edgecolor=COLORS['venus'], alpha=0.75)
    ax2.annotate('Thr: 78%', xy=(1.0, thresh_centered),
                 xycoords=('axes fraction', 'data'),
                 fontsize=9, fontweight='bold', color='white',
                 ha='left', va='center', xytext=(6, 0),
                 textcoords='offset points', bbox=pill_thresh)
    add_recessions(ax1)

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    leg_style = legend_style()
    leg_style['framealpha'] = 1.0
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', bbox_to_anchor=(0.1, 1.0), **leg_style)

    ip_last = ip_yoy.iloc[-1]
    cu_last = cap_util.iloc[-1]
    slack = "building" if cu_last < 78 else "tight"
    add_annotation_box(ax1,
        f"IP growth: {ip_last:+.1f}% YoY. Capacity util: {cu_last:.1f}% (slack {slack}).\n"
        f"Below 78% = slack in system. Pricing power falls, disinflation follows.",
        x=0.62, y=0.96)

    brand_fig(fig, 'Industrial Production & Manufacturing Capacity Utilization',
              subtitle='Production output meets the capacity constraint',
              source='Federal Reserve via FRED', data_date=ip_yoy.index[-1])

    return save_fig(fig, 'chart_09_ip_capacity.png')


# ============================================
# CHART 10: Corporate Profits YoY [Figure 10]
# ============================================
def chart_10():
    """Corporate Profits (before tax, no IVA/CCAdj) YoY: the bottom line."""
    print('\nChart 10: Corporate Profits YoY...')

    profits = fetch_quarterly_yoy('A464RC1Q027SBEA')

    fig, ax = new_fig()

    ax.plot(profits.index, profits, color=THEME['primary'], linewidth=2.5,
            label=f'Corporate Profits YoY ({profits.iloc[-1]:.1f}%)')

    ax.fill_between(profits.index, 0, profits,
                    where=(profits < 0),
                    color=COLORS['venus'], alpha=0.12, label='Earnings recession')

    ax.axhline(0, color=COLORS['doldrums'], linewidth=0.8, alpha=0.5, linestyle='--')

    style_single_ax(ax)
    set_xlim_to_data(ax, profits.index)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    add_last_value_label(ax, profits, color=THEME['primary'], side='right')
    add_recessions(ax)
    ax.legend(loc='upper left', **legend_style())

    p_last = profits.iloc[-1]
    status = "growing" if p_last > 0 else "contracting"
    add_annotation_box(ax,
        f"Corporate profits {status} at {p_last:+.1f}% YoY.\n"
        f"Margin compression precedes layoffs by 2-4 quarters.",
        x=0.52, y=0.92)

    brand_fig(fig, 'Corporate Profits: Year-Over-Year Growth',
              subtitle='The Bottom Line: profits peak before the economy does',
              source='BEA via FRED', data_date=profits.index[-1])

    return save_fig(fig, 'chart_10_corporate_profits.png')


# ============================================
# CHART 11: Unit Labor Costs vs Productivity [Figure 11]
# ============================================
def chart_11():
    """Unit Labor Costs YoY vs Nonfarm Productivity YoY: the margin squeeze."""
    print('\nChart 11: Unit Labor Costs vs Productivity...')

    ulc = fetch_quarterly_yoy('ULCNFB')
    prod = fetch_quarterly_yoy('OPHNFB')

    fig, ax = new_fig()

    ax.plot(ulc.index, ulc, color=THEME['primary'], linewidth=2.5,
            label=f'Unit Labor Costs YoY ({ulc.iloc[-1]:.1f}%)')
    ax.plot(prod.index, prod, color=THEME['secondary'], linewidth=2.5,
            label=f'Productivity YoY ({prod.iloc[-1]:.1f}%)')

    common = pd.DataFrame({'ulc': ulc, 'prod': prod}).dropna()
    ax.fill_between(common.index, common['ulc'], common['prod'],
                    where=(common['ulc'] > common['prod']),
                    color=COLORS['venus'], alpha=0.12, label='ULC > Productivity (margin pressure)')

    ax.axhline(0, color=COLORS['doldrums'], linewidth=0.8, alpha=0.5, linestyle='--')

    style_single_ax(ax)
    set_xlim_to_data(ax, ulc.index)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    add_last_value_label(ax, ulc, color=THEME['primary'], side='right')
    add_last_value_label(ax, prod, color=THEME['secondary'], side='right')
    add_recessions(ax)
    ax.legend(loc='upper left', **legend_style())

    ulc_last = ulc.iloc[-1]
    prod_last = prod.iloc[-1]
    gap = ulc_last - prod_last
    pressure = "Margins under pressure" if gap > 0 else "Margins expanding"
    add_annotation_box(ax,
        f"ULC {ulc_last:+.1f}% vs Productivity {prod_last:+.1f}%. Gap: {gap:+.1f}pp.\n"
        f"{pressure}. When labor costs outrun productivity, layoffs follow.",
        x=0.52, y=0.92)

    brand_fig(fig, 'Unit Labor Costs vs Nonfarm Productivity',
              subtitle='The Margin Squeeze: labor costs eating into profits',
              source='BLS via FRED', data_date=ulc.index[-1])

    return save_fig(fig, 'chart_11_ulc_vs_productivity.png')


# ============================================
# CHART 12: Business Loans & Delinquency [Figure 12]
# ============================================
def chart_12():
    """C&I Loan Growth YoY and Business Loan Delinquency Rate."""
    print('\nChart 12: Business Loans & Delinquency...')

    loans_yoy = fetch_fred_yoy('BUSLOANS')
    delinq = fetch_fred_level('DRBLACBS')

    fig, ax1 = new_fig()
    ax2 = ax1.twinx()
    c1, c2 = THEME['primary'], THEME['secondary']

    ax1.plot(loans_yoy.index, loans_yoy, color=c1, linewidth=2.5,
             label=f'C&I Loan Growth YoY ({loans_yoy.iloc[-1]:.1f}%)')
    ax2.plot(delinq.index, delinq, color=c2, linewidth=2.5,
             label=f'Business Delinquency Rate ({delinq.iloc[-1]:.1f}%)')

    ax1.axhline(0, color=COLORS['doldrums'], linewidth=0.8, alpha=0.5, linestyle='--')

    style_dual_ax(ax1, ax2, c1, c2)
    ax1.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.1f}%'))
    ax2.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.1f}%'))
    set_xlim_to_data(ax1, loans_yoy.index)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    add_last_value_label(ax1, loans_yoy, color=c1, side='left')
    add_last_value_label(ax2, delinq, color=c2, side='right')
    add_recessions(ax1)

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', **legend_style())

    loans_last = loans_yoy.iloc[-1]
    delinq_last = delinq.iloc[-1]
    add_annotation_box(ax1,
        f"Loan growth: {loans_last:+.1f}% YoY. Delinquency: {delinq_last:.1f}%.\n"
        f"When growth declines and delinquency rises, the credit cycle turns.",
        x=0.52, y=0.92)

    brand_fig(fig, 'Business Loan Growth & Delinquency Rate',
              subtitle='The Credit Channel: banks tighten as stress builds',
              source='Federal Reserve via FRED', data_date=loans_yoy.index[-1])

    return save_fig(fig, 'chart_12_business_credit.png')


# ============================================
# CHART 13: Leading Economic Index [Figure 13]
# ============================================
def chart_13():
    """Conference Board Leading Economic Index: the composite crystal ball."""
    print('\nChart 13: Leading Economic Index...')

    lei = fetch_db_level('TV_USLEI', start='1960-01-01')
    # Compute YoY % change
    lei_yoy = lei.pct_change(12) * 100

    fig, ax = new_fig()

    ax.plot(lei_yoy.index, lei_yoy, color=THEME['primary'], linewidth=2.5,
            label=f'LEI YoY% ({lei_yoy.iloc[-1]:.1f}%)')

    ax.fill_between(lei_yoy.index, 0, lei_yoy,
                    where=(lei_yoy < 0),
                    color=COLORS['venus'], alpha=0.10, label='LEI declining (recession warning)')

    ax.axhline(0, color=COLORS['doldrums'], linewidth=1.0, linestyle='--', alpha=0.7)
    # Recession warning threshold
    ax.axhline(-4.0, color=COLORS['venus'], linewidth=1.0, linestyle='-', alpha=0.5)

    style_single_ax(ax)
    set_xlim_to_data(ax, lei_yoy.dropna().index)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    add_last_value_label(ax, lei_yoy.dropna(), color=THEME['primary'], side='right')
    add_recessions(ax)
    ax.legend(loc='upper left', **legend_style())

    lei_last = lei_yoy.iloc[-1]
    add_annotation_box(ax,
        f"LEI {lei_last:+.1f}% YoY. Below -4% for 6+ months = recession.\n"
        f"Composite of 10 leading indicators: the economy's crystal ball.",
        x=0.52, y=0.92)

    brand_fig(fig, 'Conference Board Leading Economic Index',
              subtitle='10 indicators, one signal: where the economy is heading',
              source='Conference Board via TradingView',
              data_date=lei_yoy.dropna().index[-1])

    return save_fig(fig, 'chart_13_leading_index.png')


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
    13: chart_13,
}


def main():
    parser = argparse.ArgumentParser(description='Generate Business educational charts')
    parser.add_argument('--chart', type=int, help='Chart number to generate (1-13)')
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
