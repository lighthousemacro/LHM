#!/usr/bin/env python3
"""
Generate Charts for Educational Series: Post 12 - Sentiment (Pillar 12)
======================================================================
10 charts covering: AAII Bull-Bear, NAAIM Exposure, II Bull-Bear,
Put/Call Ratio, VIX vs 50d MA, VIX Term Structure, ETF Flows,
MMF Assets, SPI Composite, SSD Divergence.

Usage:
    python sentiment_edu_charts.py --chart 1
    python sentiment_edu_charts.py --all
"""

import os
import argparse
import sqlite3
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
from matplotlib.ticker import FuncFormatter

# ============================================
# PATHS & CONFIG
# ============================================
BASE_PATH = '/Users/bob/LHM'
OUTPUT_BASE = f'{BASE_PATH}/Outputs/Educational_Charts/Sentiment_Post_12'
DB_PATH = f'{BASE_PATH}/Data/databases/Lighthouse_Master.db'
ICON_PATH = f'{BASE_PATH}/Brand/icon_transparent_128.png'

_DATA_CACHE = {}

COLORS = {
    'ocean': '#2389BB',
    'dusk': '#FF6723',
    'sky': '#23BBFF',
    'venus': '#FF2389',
    'sea': '#00BB89',
    'doldrums': '#898989',
    'starboard': '#238923',
    'port': '#892323',
    'fog': '#D1D1D1',
}

RECESSIONS = [
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


def set_theme(mode='white'):
    global THEME, OUTPUT_DIR
    if mode == 'dark':
        THEME.update({
            'bg': '#0A1628', 'fg': '#e6edf3', 'muted': '#8b949e',
            'spine': '#1e3350', 'zero_line': '#e6edf3',
            'recession': '#ffffff', 'recession_alpha': 0.06,
            'primary': COLORS['ocean'], 'secondary': COLORS['dusk'],
            'tertiary': COLORS['sky'], 'quaternary': COLORS['sea'],
            'fill_alpha': 0.20,
            'legend_bg': '#0f1f38', 'legend_fg': '#e6edf3',
            'mode': 'dark',
        })
    else:
        THEME.update({
            'bg': '#ffffff', 'fg': '#1a1a1a', 'muted': '#555555',
            'spine': '#898989', 'zero_line': '#D1D1D1',
            'recession': 'gray', 'recession_alpha': 0.12,
            'primary': COLORS['ocean'], 'secondary': COLORS['dusk'],
            'tertiary': COLORS['sky'], 'quaternary': COLORS['sea'],
            'fill_alpha': 0.15,
            'legend_bg': '#f8f8f8', 'legend_fg': '#1a1a1a',
            'mode': 'white',
        })
    OUTPUT_DIR = os.path.join(OUTPUT_BASE, mode)
    os.makedirs(OUTPUT_DIR, exist_ok=True)


# ============================================
# DATA HELPERS
# ============================================
def fetch_db_level(series_id, start='1950-01-01'):
    cache_key = f"db_{series_id}_{start}"
    if cache_key in _DATA_CACHE:
        return _DATA_CACHE[cache_key].copy()
    conn = sqlite3.connect(f'file:///{DB_PATH}?mode=ro&immutable=1', uri=True)
    df = pd.read_sql(
        "SELECT date, value FROM observations WHERE series_id = ? AND date >= ? ORDER BY date",
        conn, params=(series_id, start))
    conn.close()
    if df.empty:
        return pd.Series(dtype=float)
    df['date'] = pd.to_datetime(df['date'])
    df = df.set_index('date')
    s = df['value'].dropna()
    _DATA_CACHE[cache_key] = s.copy()
    return s


def fetch_db_index(index_id, start='1950-01-01'):
    cache_key = f"dbidx_{index_id}_{start}"
    if cache_key in _DATA_CACHE:
        return _DATA_CACHE[cache_key].copy()
    conn = sqlite3.connect(f'file:///{DB_PATH}?mode=ro&immutable=1', uri=True)
    df = pd.read_sql(
        "SELECT date, value FROM lighthouse_indices "
        "WHERE index_id = ? AND date >= ? ORDER BY date",
        conn, params=(index_id, start))
    conn.close()
    if df.empty:
        return pd.Series(dtype=float)
    df['date'] = pd.to_datetime(df['date'])
    df = df.set_index('date')
    s = df['value'].dropna()
    _DATA_CACHE[cache_key] = s.copy()
    return s


def fetch_yf(ticker, start='2000-01-01'):
    cache_key = f"yf_{ticker}_{start}"
    if cache_key in _DATA_CACHE:
        return _DATA_CACHE[cache_key].copy()
    try:
        import yfinance as yf
        t = yf.Ticker(ticker)
        hist = t.history(start=start, auto_adjust=True)
        if not hist.empty:
            s = hist['Close'].dropna()
            s.index = s.index.tz_localize(None)
            _DATA_CACHE[cache_key] = s.copy()
            return s
    except Exception as e:
        print(f'  yfinance fetch failed for {ticker}: {e}')
    return pd.Series(dtype=float)


# ============================================
# CHART STYLING HELPERS (same as pillar 11)
# ============================================
def new_fig(figsize=(14, 8)):
    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_facecolor(THEME['bg'])
    ax.set_facecolor(THEME['bg'])
    fig.subplots_adjust(top=0.88, bottom=0.08, left=0.06, right=0.94)
    return fig, ax


def style_ax(ax, right_primary=True):
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


def style_single_ax(ax, fmt='{:.1f}'):
    style_ax(ax, right_primary=True)
    ax.tick_params(axis='both', which='both', length=0)
    ax.tick_params(axis='y', labelcolor=THEME['fg'], labelsize=10)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: fmt.format(x)))


def brand_fig(fig, title, subtitle=None, source=None, data_date=None):
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
    fig.suptitle(title, fontsize=15, fontweight='bold', y=0.945, color=THEME['fg'])
    if subtitle:
        fig.text(0.5, 0.895, subtitle, fontsize=14, ha='center',
                 color=OCEAN, style='italic')


def add_last_value_label(ax, y_data, color, fmt='{:.1f}', side='right', fontsize=9, pad=0.3):
    if len(y_data) == 0:
        return
    last_y = float(y_data.iloc[-1]) if hasattr(y_data, 'iloc') else float(y_data[-1])
    label = fmt.format(last_y)
    pill = dict(boxstyle=f'round,pad={pad}', facecolor=color, edgecolor=color, alpha=0.95)
    if side == 'right':
        ax.annotate(label, xy=(1.0, last_y), xycoords=('axes fraction', 'data'),
                    fontsize=fontsize, fontweight='bold', color='white',
                    ha='left', va='center', xytext=(6, 0), textcoords='offset points',
                    bbox=pill)
    else:
        ax.annotate(label, xy=(0.0, last_y), xycoords=('axes fraction', 'data'),
                    fontsize=fontsize, fontweight='bold', color='white',
                    ha='right', va='center', xytext=(-6, 0), textcoords='offset points',
                    bbox=pill)


def add_recessions(ax, start_date=None):
    for s, e in RECESSIONS:
        ts, te = pd.Timestamp(s), pd.Timestamp(e)
        if start_date and te < pd.Timestamp(start_date):
            continue
        ax.axvspan(ts, te, color=THEME['recession'],
                   alpha=THEME['recession_alpha'], zorder=0)


def set_xlim_to_data(ax, *indices):
    start = max(idx.min() for idx in indices)
    end = max(idx.max() for idx in indices)
    padding_left = pd.Timedelta(days=30)
    padding_right = pd.Timedelta(days=180)
    ax.set_xlim(start - padding_left, end + padding_right)


def legend_style():
    return dict(
        framealpha=0.95,
        facecolor=THEME['legend_bg'],
        edgecolor='#23BBFF' if THEME['mode'] == 'dark' else THEME['spine'],
        labelcolor=THEME['legend_fg'],
    )


def save_fig(fig, filename):
    border_color = COLORS['ocean']
    border_width = 4.0
    fig.patches.append(plt.Rectangle(
        (0, 0), 1, 1, transform=fig.transFigure,
        fill=False, edgecolor=border_color, linewidth=border_width,
        zorder=100, clip_on=False))
    filepath = os.path.join(OUTPUT_DIR, filename)
    fig.savefig(filepath, dpi=200, bbox_inches='tight', pad_inches=0.025,
                facecolor=THEME['bg'], edgecolor='none')
    plt.close(fig)
    print(f'  Saved: {filepath}')
    return filepath


# ============================================
# CHART 1: AAII Bull-Bear Spread
# ============================================
def chart_01():
    """AAII Bull-Bear Spread."""
    print('\nChart 1: AAII Bull-Bear Spread...')

    spread = fetch_db_level('AAII_Bull_Bear_Spread', start='1987-01-01') * 100

    fig, ax = new_fig()
    ax.plot(spread.index, spread, color=THEME['primary'], linewidth=1.5, zorder=5)

    # Zero line
    ax.axhline(0, color=COLORS['fog'], linestyle='--', linewidth=1.0, zorder=2)

    # Thresholds
    ax.axhline(30, color=COLORS['venus'], linestyle='--', linewidth=1.5, alpha=0.8, zorder=3)
    ax.axhline(-20, color=COLORS['sea'], linestyle='--', linewidth=1.5, alpha=0.8, zorder=3)

    # Labels
    ax.text(spread.index[-1] + pd.Timedelta(days=10), 33, 'Euphoria', fontsize=8,
            color=COLORS['venus'], fontweight='bold', va='bottom')
    ax.text(spread.index[-1] + pd.Timedelta(days=10), -23, 'Capitulation', fontsize=8,
            color=COLORS['sea'], fontweight='bold', va='top')

    # Fill extremes
    ax.fill_between(spread.index, 30, spread, where=spread > 30,
                    color=COLORS['venus'], alpha=0.08, zorder=1, interpolate=True)
    ax.fill_between(spread.index, -20, spread, where=spread < -20,
                    color=COLORS['sea'], alpha=0.08, zorder=1, interpolate=True)

    style_single_ax(ax, fmt='{:.0f}%')
    set_xlim_to_data(ax, spread.index)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    add_last_value_label(ax, spread, color=THEME['primary'], fmt='{:.1f}%', side='right')
    add_recessions(ax)

    brand_fig(fig, 'AAII Bull-Bear Spread: The Retail Truth Serum',
              subtitle='Figure 1: Weekly Bull-Bear Spread Since 1987',
              source='AAII', data_date=spread.index[-1])
    save_fig(fig, 'pillar_12_fig_01.png')


# ============================================
# CHART 2: AAII Components (Bulls, Bears, Neutral)
# ============================================
def chart_02():
    """AAII Components stacked area."""
    print('\nChart 2: AAII Components...')

    bulls = fetch_db_level('AAII_Bullish', start='2020-01-01') * 100
    bears = fetch_db_level('AAII_Bearish', start='2020-01-01') * 100
    neutral = fetch_db_level('AAII_Neutral', start='2020-01-01') * 100

    # Align
    df = pd.DataFrame({'Bulls': bulls, 'Bears': bears, 'Neutral': neutral}).dropna()

    fig, ax = new_fig()

    ax.fill_between(df.index, 0, df['Bears'], color=COLORS['port'], alpha=0.6,
                    label='Bears', zorder=3)
    ax.fill_between(df.index, df['Bears'], df['Bears'] + df['Neutral'],
                    color=COLORS['doldrums'], alpha=0.3, label='Neutral', zorder=2)
    ax.fill_between(df.index, df['Bears'] + df['Neutral'],
                    df['Bears'] + df['Neutral'] + df['Bulls'],
                    color=COLORS['starboard'], alpha=0.6, label='Bulls', zorder=3)

    ax.set_ylim(0, 100)
    style_single_ax(ax, fmt='{:.0f}%')
    set_xlim_to_data(ax, df.index)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    ax.legend(loc='upper right', fontsize=10, **legend_style())

    brand_fig(fig, 'AAII Sentiment Components: The Crowd\'s Composition',
              subtitle='Figure 2: Bullish, Bearish, and Neutral Readings',
              source='AAII', data_date=df.index[-1])
    save_fig(fig, 'pillar_12_fig_02.png')


# ============================================
# CHART 3: VIX with 50-Day MA
# ============================================
def chart_03():
    """VIX vs 50-Day MA."""
    print('\nChart 3: VIX vs 50d MA...')

    vix = fetch_db_level('VIXCLS', start='2019-01-01')
    if len(vix) < 100 or vix.index[-1] < pd.Timestamp('2026-03-01'):
        print('  VIX stale, fetching from yfinance...')
        vix_yf = fetch_yf('^VIX', start='2019-01-01')
        if len(vix_yf) > 100:
            vix = vix_yf

    vix_50d = vix.rolling(50).mean()

    # Plot from 2021
    plot_start = '2021-01-01'
    vix_p = vix[vix.index >= plot_start]
    vix_50d_p = vix_50d[vix_50d.index >= plot_start]

    fig, ax = new_fig()

    ax.plot(vix_p.index, vix_p, color=THEME['primary'], linewidth=2.0,
            label='VIX', zorder=5)
    ax.plot(vix_50d_p.index, vix_50d_p, color=COLORS['dusk'], linewidth=1.5,
            linestyle='--', label='50-Day MA', zorder=4)

    # Shade when VIX > 30% above 50d MA
    vix_ratio = vix_p / vix_50d_p
    spike = vix_ratio > 1.30
    ax.fill_between(vix_p.index, vix_p, vix_50d_p,
                    where=spike.reindex(vix_p.index, fill_value=False),
                    color=COLORS['venus'], alpha=0.12, zorder=1, interpolate=True,
                    label='Fear Spike (>30% above MA)')

    style_single_ax(ax, fmt='{:.0f}')
    set_xlim_to_data(ax, vix_p.index)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    add_last_value_label(ax, vix_p, color=THEME['primary'], fmt='{:.1f}', side='right')
    add_last_value_label(ax, vix_50d_p, color=COLORS['dusk'], fmt='{:.1f}',
                         side='right', fontsize=8)
    ax.legend(loc='upper left', fontsize=10, **legend_style())
    add_recessions(ax, start_date=plot_start)

    brand_fig(fig, 'VIX vs. 50-Day Moving Average: Fear in Context',
              subtitle='Figure 3: The Deviation from Recent Norms Matters More Than the Level',
              source='CBOE', data_date=vix_p.index[-1])
    save_fig(fig, 'pillar_12_fig_03.png')


# ============================================
# CHART 4: VIX Term Structure (VIX/VIX3M Ratio)
# ============================================
def chart_04():
    """VIX Term Structure."""
    print('\nChart 4: VIX Term Structure...')

    vix = fetch_yf('^VIX', start='2021-01-01')
    vix3m = fetch_yf('^VIX3M', start='2021-01-01')

    if len(vix) < 50 or len(vix3m) < 50:
        print('  Cannot fetch VIX/VIX3M from yfinance, skipping chart 4')
        return

    ratio = (vix / vix3m).dropna()

    fig, ax = new_fig()

    ax.plot(ratio.index, ratio, color=THEME['primary'], linewidth=2.0, zorder=5)

    # Backwardation threshold
    ax.axhline(1.0, color=COLORS['fog'], linestyle='--', linewidth=1.0, zorder=2)
    ax.text(ratio.index[-1] + pd.Timedelta(days=10), 1.02, 'Backwardation', fontsize=8,
            color=COLORS['venus'], fontweight='bold', va='bottom')

    # Shade above 1.0
    ax.fill_between(ratio.index, 1.0, ratio, where=ratio > 1.0,
                    color=COLORS['venus'], alpha=0.12, zorder=1, interpolate=True)

    style_single_ax(ax, fmt='{:.2f}')
    set_xlim_to_data(ax, ratio.index)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    add_last_value_label(ax, ratio, color=THEME['primary'], fmt='{:.2f}', side='right')

    brand_fig(fig, 'VIX Term Structure: Stress Detection',
              subtitle='Figure 4: VIX / VIX3M Ratio. Above 1.0 = Backwardation = Acute Stress',
              source='CBOE', data_date=ratio.index[-1])
    save_fig(fig, 'pillar_12_fig_04.png')


# ============================================
# CHART 5: AAII Bears % with SPX overlay
# ============================================
def chart_05():
    """AAII Bears % with S&P 500 overlay."""
    print('\nChart 5: AAII Bears vs SPX...')

    bears = fetch_db_level('AAII_Bearish', start='2020-01-01') * 100
    spx = fetch_db_level('SPX_Close', start='2020-01-01')

    fig, ax1 = new_fig()
    ax2 = ax1.twinx()

    # SPX on left
    ax1.plot(spx.index, spx, color=COLORS['dusk'], linewidth=1.5, label='S&P 500', zorder=4)
    # Bears on right (inverted feel: high bears = contrarian bullish)
    ax2.plot(bears.index, bears, color=THEME['primary'], linewidth=2.0,
             label='AAII Bears %', zorder=5)

    # Threshold
    ax2.axhline(50, color=COLORS['sea'], linestyle='--', linewidth=1.5, alpha=0.8, zorder=3)
    ax2.text(bears.index[-1] + pd.Timedelta(days=10), 52, 'Extreme\nFear', fontsize=8,
             color=COLORS['sea'], fontweight='bold', va='bottom')

    style_dual_ax(ax1, ax2, COLORS['dusk'], THEME['primary'])
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    set_xlim_to_data(ax1, spx.index, bears.index)

    add_last_value_label(ax1, spx, color=COLORS['dusk'], fmt='{:,.0f}', side='left')
    add_last_value_label(ax2, bears, color=THEME['primary'], fmt='{:.0f}%', side='right')

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left',
               fontsize=10, **legend_style())

    brand_fig(fig, 'AAII Bears vs. S&P 500: Fear Creates Opportunity',
              subtitle='Figure 5: Extreme Bearish Readings Have Preceded Rallies',
              source='AAII, S&P 500', data_date=max(bears.index[-1], spx.index[-1]))
    save_fig(fig, 'pillar_12_fig_05.png')


# ============================================
# CHART 6: VIX % Above 50d MA (z-scored deviation)
# ============================================
def chart_06():
    """VIX deviation from 50d MA."""
    print('\nChart 6: VIX % Above 50d MA...')

    vix_dev = fetch_db_level('VIX_vs_50d_pct', start='2021-01-01')
    if len(vix_dev) < 50:
        # Compute from VIX
        vix = fetch_yf('^VIX', start='2019-01-01')
        vix_50d = vix.rolling(50).mean()
        vix_dev = ((vix / vix_50d) - 1) * 100
        vix_dev = vix_dev[vix_dev.index >= '2021-01-01'].dropna()

    fig, ax = new_fig()

    ax.plot(vix_dev.index, vix_dev, color=THEME['primary'], linewidth=2.0, zorder=5)

    # Zero line
    ax.axhline(0, color=COLORS['fog'], linestyle='--', linewidth=1.0, zorder=2)

    # Thresholds
    ax.axhline(30, color=COLORS['venus'], linestyle='--', linewidth=1.5, alpha=0.8, zorder=3)
    ax.axhline(-20, color=COLORS['sea'], linestyle='--', linewidth=1.5, alpha=0.8, zorder=3)

    ax.text(vix_dev.index[-1] + pd.Timedelta(days=10), 33, 'Fear Spike', fontsize=8,
            color=COLORS['venus'], fontweight='bold', va='bottom')
    ax.text(vix_dev.index[-1] + pd.Timedelta(days=10), -23, 'Complacent', fontsize=8,
            color=COLORS['sea'], fontweight='bold', va='top')

    # Fill extremes
    ax.fill_between(vix_dev.index, 30, vix_dev, where=vix_dev > 30,
                    color=COLORS['venus'], alpha=0.08, zorder=1, interpolate=True)
    ax.fill_between(vix_dev.index, -20, vix_dev, where=vix_dev < -20,
                    color=COLORS['sea'], alpha=0.08, zorder=1, interpolate=True)

    style_single_ax(ax, fmt='{:.0f}%')
    set_xlim_to_data(ax, vix_dev.index)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    add_last_value_label(ax, vix_dev, color=THEME['primary'], fmt='{:.0f}%', side='right')

    brand_fig(fig, 'VIX Deviation from 50-Day MA: Regime Detection',
              subtitle='Figure 6: % Above/Below 50-Day Moving Average',
              source='CBOE, Lighthouse Macro calculations', data_date=vix_dev.index[-1])
    save_fig(fig, 'pillar_12_fig_06.png')


# ============================================
# CHART 7: Money Market Fund Assets
# ============================================
def chart_07():
    """Money Market Fund Assets."""
    print('\nChart 7: MMF Assets...')

    mmf = fetch_db_level('MMMFTAQ027S', start='2000-01-01')
    # Convert to trillions
    mmf_t = mmf / 1000

    # YoY change
    mmf_yoy = mmf.pct_change(4) * 100  # quarterly data, 4 periods = 1 year

    fig, ax1 = new_fig()
    ax2 = ax1.twinx()

    ax1.plot(mmf_t.index, mmf_t, color=COLORS['dusk'], linewidth=2.0,
             label='MMF Assets ($T)', zorder=5)
    ax2.plot(mmf_yoy.index, mmf_yoy, color=THEME['primary'], linewidth=2.0,
             label='YoY % Change', zorder=4)
    ax2.axhline(0, color=COLORS['fog'], linestyle='--', linewidth=0.8, zorder=2)

    style_dual_ax(ax1, ax2, COLORS['dusk'], THEME['primary'])
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    set_xlim_to_data(ax1, mmf_t.index)

    add_last_value_label(ax1, mmf_t, color=COLORS['dusk'], fmt='${:.1f}T', side='left')
    mmf_yoy_clean = mmf_yoy.dropna()
    if len(mmf_yoy_clean) > 0:
        add_last_value_label(ax2, mmf_yoy_clean, color=THEME['primary'],
                             fmt='{:.1f}%', side='right')

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left',
               fontsize=10, **legend_style())
    add_recessions(ax1)

    brand_fig(fig, 'Money Market Fund Assets: The Cash Mountain',
              subtitle='Figure 7: Record Cash Levels = Fear + Future Buying Power',
              source='ICI, Federal Reserve', data_date=mmf_t.index[-1])
    save_fig(fig, 'pillar_12_fig_07.png')


# ============================================
# CHART 8: SPI Composite
# ============================================
def chart_08():
    """SPI Composite with S&P 500 overlay."""
    print('\nChart 8: SPI Composite...')

    spi = fetch_db_index('SPI', start='2000-01-01')
    spx = fetch_db_level('SPX_Close', start='2000-01-01')

    # Smooth SPI with 10-day MA for readability
    spi_smooth = spi.rolling(10, min_periods=5).mean().dropna()

    fig, ax1 = new_fig()
    ax2 = ax1.twinx()

    # SPX on left
    ax1.plot(spx.index, spx, color=COLORS['dusk'], linewidth=1.5, label='S&P 500', zorder=4)

    # SPI on right
    ax2.plot(spi_smooth.index, spi_smooth, color=THEME['primary'], linewidth=2.0,
             label='SPI (10d MA)', zorder=5)

    # SPI thresholds
    ax2.axhline(1.5, color=COLORS['sea'], linestyle='--', linewidth=1.0, alpha=0.6, zorder=3)
    ax2.axhline(-1.0, color=COLORS['venus'], linestyle='--', linewidth=1.0, alpha=0.6, zorder=3)

    # Shade extremes
    ax2.fill_between(spi_smooth.index, 1.5,
                     np.maximum(spi_smooth.values, 1.5),
                     where=spi_smooth > 1.5,
                     color=COLORS['sea'], alpha=0.10, zorder=1, interpolate=True)
    ax2.fill_between(spi_smooth.index, -1.0,
                     np.minimum(spi_smooth.values, -1.0),
                     where=spi_smooth < -1.0,
                     color=COLORS['venus'], alpha=0.10, zorder=1, interpolate=True)

    # Labels
    ax2.text(spi_smooth.index[-1] + pd.Timedelta(days=10), 1.6, 'Extreme Fear\n(Contrarian Buy)',
             fontsize=7, color=COLORS['sea'], fontweight='bold', va='bottom')
    ax2.text(spi_smooth.index[-1] + pd.Timedelta(days=10), -1.1, 'Euphoria\n(Contrarian Sell)',
             fontsize=7, color=COLORS['venus'], fontweight='bold', va='top')

    style_dual_ax(ax1, ax2, COLORS['dusk'], THEME['primary'])
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    set_xlim_to_data(ax1, spx.index, spi_smooth.index)

    add_last_value_label(ax1, spx, color=COLORS['dusk'], fmt='{:,.0f}', side='left')
    add_last_value_label(ax2, spi_smooth, color=THEME['primary'], fmt='{:.2f}', side='right')

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left',
               fontsize=10, **legend_style())
    add_recessions(ax1)

    brand_fig(fig, 'Sentiment & Positioning Index: The Contrarian Signal',
              subtitle='Figure 8: SPI Composite vs S&P 500',
              source='AAII, CBOE, Lighthouse Macro calculations',
              data_date=spi_smooth.index[-1])
    save_fig(fig, 'pillar_12_fig_08.png')


# ============================================
# CHART 9: SPI Zoomed (recent 3 years)
# ============================================
def chart_09():
    """SPI Composite zoomed recent period."""
    print('\nChart 9: SPI Zoomed...')

    spi = fetch_db_index('SPI', start='2023-01-01')
    spi_smooth = spi.rolling(10, min_periods=5).mean().dropna()

    fig, ax = new_fig()

    # Raw as faint
    ax.plot(spi.index, spi, color=THEME['primary'], linewidth=0.5, alpha=0.2, zorder=3)
    # Smoothed
    ax.plot(spi_smooth.index, spi_smooth, color=THEME['primary'], linewidth=2.5,
            label='SPI (10d MA)', zorder=5)

    # Zero and thresholds
    ax.axhline(0, color=COLORS['fog'], linestyle='--', linewidth=1.0, zorder=2)
    ax.axhline(1.5, color=COLORS['sea'], linestyle='--', linewidth=1.5, alpha=0.8, zorder=3)
    ax.axhline(1.0, color=COLORS['sea'], linestyle=':', linewidth=1.0, alpha=0.5, zorder=3)
    ax.axhline(-0.5, color=COLORS['venus'], linestyle=':', linewidth=1.0, alpha=0.5, zorder=3)
    ax.axhline(-1.0, color=COLORS['venus'], linestyle='--', linewidth=1.5, alpha=0.8, zorder=3)

    # Labels
    ax.text(spi_smooth.index[-1] + pd.Timedelta(days=10), 1.6, 'Extreme Fear', fontsize=8,
            color=COLORS['sea'], fontweight='bold', va='bottom')
    ax.text(spi_smooth.index[-1] + pd.Timedelta(days=10), -1.1, 'Euphoria', fontsize=8,
            color=COLORS['venus'], fontweight='bold', va='top')

    # Shade
    ax.fill_between(spi_smooth.index, 1.5, spi_smooth, where=spi_smooth > 1.5,
                    color=COLORS['sea'], alpha=0.10, zorder=1, interpolate=True)
    ax.fill_between(spi_smooth.index, -1.0, spi_smooth, where=spi_smooth < -1.0,
                    color=COLORS['venus'], alpha=0.10, zorder=1, interpolate=True)

    style_single_ax(ax, fmt='{:.1f}')
    set_xlim_to_data(ax, spi_smooth.index)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    add_last_value_label(ax, spi_smooth, color=THEME['primary'], fmt='{:.2f}', side='right')
    ax.legend(loc='upper left', fontsize=10, **legend_style())

    brand_fig(fig, 'SPI: Recent Sentiment Regimes',
              subtitle='Figure 9: Sentiment & Positioning Index (Zoomed)',
              source='AAII, CBOE, Lighthouse Macro calculations',
              data_date=spi_smooth.index[-1])
    save_fig(fig, 'pillar_12_fig_09.png')


# ============================================
# CHART 10: SSD (Sentiment-Structure Divergence)
# ============================================
def chart_10():
    """Sentiment-Structure Divergence with SPX overlay."""
    print('\nChart 10: SSD...')

    ssd = fetch_db_index('SSD', start='2000-01-01')
    spx = fetch_db_level('SPX_Close', start='2000-01-01')

    # Smooth
    ssd_smooth = ssd.rolling(10, min_periods=5).mean().dropna()

    fig, ax1 = new_fig()
    ax2 = ax1.twinx()

    # SPX on left
    ax1.plot(spx.index, spx, color=COLORS['dusk'], linewidth=1.5, label='S&P 500', zorder=4)

    # SSD on right
    ax2.plot(ssd_smooth.index, ssd_smooth, color=THEME['primary'], linewidth=2.0,
             label='SSD (10d MA)', zorder=5)

    # Thresholds
    ax2.axhline(1.5, color=COLORS['sea'], linestyle='--', linewidth=1.0, alpha=0.6, zorder=3)
    ax2.axhline(-1.5, color=COLORS['venus'], linestyle='--', linewidth=1.0, alpha=0.6, zorder=3)
    ax2.axhline(0, color=COLORS['fog'], linestyle='--', linewidth=0.8, zorder=2)

    # Shade extremes
    ax2.fill_between(ssd_smooth.index, 1.5,
                     np.maximum(ssd_smooth.values, 1.5),
                     where=ssd_smooth > 1.5,
                     color=COLORS['sea'], alpha=0.10, zorder=1, interpolate=True)
    ax2.fill_between(ssd_smooth.index, -1.5,
                     np.minimum(ssd_smooth.values, -1.5),
                     where=ssd_smooth < -1.5,
                     color=COLORS['venus'], alpha=0.10, zorder=1, interpolate=True)

    # Labels
    ax2.text(ssd_smooth.index[-1] + pd.Timedelta(days=10), 1.6, 'Capitulation\nLow', fontsize=7,
             color=COLORS['sea'], fontweight='bold', va='bottom')
    ax2.text(ssd_smooth.index[-1] + pd.Timedelta(days=10), -1.6, 'Blow-Off\nTop Risk', fontsize=7,
             color=COLORS['venus'], fontweight='bold', va='top')

    style_dual_ax(ax1, ax2, COLORS['dusk'], THEME['primary'])
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    set_xlim_to_data(ax1, spx.index, ssd_smooth.index)

    add_last_value_label(ax1, spx, color=COLORS['dusk'], fmt='{:,.0f}', side='left')
    add_last_value_label(ax2, ssd_smooth, color=THEME['primary'], fmt='{:.2f}', side='right')

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left',
               fontsize=10, **legend_style())
    add_recessions(ax1)

    brand_fig(fig, 'Sentiment-Structure Divergence: When Fear Meets Structure',
              subtitle='Figure 10: SSD vs S&P 500. Extremes Mark Turning Points.',
              source='Lighthouse Macro calculations',
              data_date=ssd_smooth.index[-1])
    save_fig(fig, 'pillar_12_fig_10.png')


# ============================================
# CHART MAP & MAIN
# ============================================
CHART_MAP = {
    1: chart_01, 2: chart_02, 3: chart_03, 4: chart_04, 5: chart_05,
    6: chart_06, 7: chart_07, 8: chart_08, 9: chart_09, 10: chart_10,
}


def main():
    parser = argparse.ArgumentParser(description='Generate Pillar 12 (Sentiment) educational charts')
    parser.add_argument('--chart', type=str, default=None, help='Chart number (1-10)')
    parser.add_argument('--theme', type=str, default='white', choices=['white', 'dark', 'both'])
    parser.add_argument('--all', action='store_true')
    args = parser.parse_args()

    themes = ['white', 'dark'] if args.theme == 'both' else [args.theme]

    for theme in themes:
        print(f'\n{"="*60}')
        print(f'  GENERATING {theme.upper()} THEME CHARTS')
        print(f'{"="*60}')
        set_theme(theme)

        if args.all or args.chart is None:
            for key in range(1, 11):
                try:
                    CHART_MAP[key]()
                except Exception as e:
                    print(f'  ERROR on chart {key}: {e}')
                    import traceback
                    traceback.print_exc()
        else:
            chart_key = int(args.chart)
            if chart_key in CHART_MAP:
                CHART_MAP[chart_key]()
            else:
                print(f'Unknown chart: {chart_key}')

    # Copy white theme outputs
    white_dir = os.path.join(OUTPUT_BASE, 'white')
    pub_dir = os.path.join(BASE_PATH, 'Outputs', 'Charts', 'Pillar_12')
    os.makedirs(pub_dir, exist_ok=True)
    if os.path.exists(white_dir):
        import shutil
        for f in os.listdir(white_dir):
            if f.endswith('.png'):
                shutil.copy2(os.path.join(white_dir, f), os.path.join(pub_dir, f))
                print(f'  Copied to publish dir: {f}')

    print(f'\nDone! Charts saved to:')
    print(f'  {OUTPUT_BASE}/')
    print(f'  {pub_dir}/')


if __name__ == '__main__':
    main()
