#!/usr/bin/env python3
"""
Generate Charts for Educational Series: Post 7 - Trade (Pillar 7)
=====================================================================
30 charts covering: trade balance, import/export prices, dollar dynamics,
bilateral trade, current account, supply chains, tariffs, energy trade,
domestic distribution, inventories, and terms of trade.

Generates BOTH white and dark theme versions.
Build 2-3x more charts than needed (~10-12) for article selection.

Usage:
    python trade_edu_charts.py --chart 1
    python trade_edu_charts.py --chart 1 --theme dark
    python trade_edu_charts.py --all
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
OUTPUT_BASE = f'{BASE_PATH}/Outputs/Educational_Charts/Trade_Post_7'
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

    # Lighthouse icon (top-left, next to text)
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
# CHART 1: U.S. Trade Balance (Goods & Services) [Figure 1]
# ============================================
def chart_01():
    """Trade Balance: Goods & Services, long history with recession shading."""
    print('\nChart 1: U.S. Trade Balance...')

    bal = fetch_fred_level('BOPGSTB', start='1992-01-01')

    fig, ax = new_fig()

    ax.plot(bal.index, bal, color=THEME['primary'], linewidth=2.5,
            label=f'Trade Balance G&S (${bal.iloc[-1]:.0f}B)')

    # Fill negative area
    ax.fill_between(bal.index, 0, bal,
                    where=(bal < 0),
                    color=COLORS['venus'], alpha=0.10)

    ax.axhline(0, color=COLORS['doldrums'], linewidth=0.8, linestyle='--', alpha=0.5)

    style_single_ax(ax, fmt='${:.0f}B')
    set_xlim_to_data(ax, bal.index)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    add_last_value_label(ax, bal, color=THEME['primary'], fmt='${:.0f}B', side='right')
    add_recessions(ax, start_date='1992-01-01')
    ax.legend(loc='lower left', **legend_style())

    add_annotation_box(ax,
        f"Trade deficit at ${bal.iloc[-1]:.0f}B.\n"
        f"Narrowing from peak, but driven by\n"
        f"demand destruction, not competitiveness.",
        x=0.675, y=0.15)

    brand_fig(fig, 'U.S. Trade Balance: Goods & Services',
              subtitle='The persistent deficit tells half the story',
              source='Census Bureau via FRED',
              data_date=bal.index[-1])

    return save_fig(fig, 'chart_01_trade_balance.png')


# ============================================
# CHART 2: Import Prices vs CPI Goods (The Pipeline) [Figure 2]
# ============================================
def chart_02():
    """Import Prices YoY vs CPI Goods YoY: the inflation transmission pipeline."""
    print('\nChart 2: Import Prices vs CPI Goods...')

    imp = fetch_fred_yoy('IR', trim='2000-01-01')
    # CPI Goods: Core Commodities Less Food & Energy
    cpi_goods = fetch_fred_yoy('CUSR0000SACL1E', trim='2000-01-01')

    # Align
    idx = imp.index.intersection(cpi_goods.index)
    imp = imp.loc[idx]
    cpi_goods = cpi_goods.loc[idx]

    fig, ax1 = new_fig()
    ax2 = ax1.twinx()
    c1, c2 = THEME['secondary'], THEME['primary']

    ax1.plot(imp.index, imp, color=c1, linewidth=2.5,
             label=f'Import Prices YoY ({imp.iloc[-1]:.1f}%)')
    ax2.plot(cpi_goods.index, cpi_goods, color=c2, linewidth=2.5,
             label=f'CPI Core Goods YoY ({cpi_goods.iloc[-1]:.1f}%)')

    ax1.axhline(0, color=COLORS['doldrums'], linewidth=0.8, linestyle='--', alpha=0.5)

    style_dual_ax(ax1, ax2, c1, c2)
    ax1.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.0f}%'))
    ax2.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.1f}%'))
    set_xlim_to_data(ax1, imp.index)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    align_yaxis_zero(ax1, ax2)

    add_last_value_label(ax1, imp, color=c1, side='left')
    add_last_value_label(ax2, cpi_goods, color=c2, side='right')
    add_recessions(ax1, start_date='2000-01-01')

    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax1.legend(h1 + h2, l1 + l2, loc='upper left', **legend_style())

    add_annotation_box(ax1,
        "Import prices lead CPI goods by 3-6 months.\n"
        "Tariff pass-through is the pipeline right now.",
        x=0.545, y=0.92)

    brand_fig(fig, 'The Inflation Pipeline: Import Prices → CPI Goods',
              subtitle='What you pay at the border shows up at the register',
              source='BLS via FRED',
              data_date=imp.index[-1])

    return save_fig(fig, 'chart_02_import_prices_cpi_goods.png')


# ============================================
# CHART 3: Trade-Weighted Dollar (Broad, DM, EM) [Figure 3]
# ============================================
def chart_03():
    """Dollar strength: Broad, Advanced, and Emerging Market indices."""
    print('\nChart 3: Trade-Weighted Dollar Indices...')

    broad = fetch_fred_level('DTWEXBGS', start='2006-01-01')
    dm = fetch_fred_level('DTWEXAFEGS', start='2006-01-01')
    em = fetch_fred_level('DTWEXEMEGS', start='2006-01-01')

    fig, ax = new_fig()

    ax.plot(broad.index, broad, color=THEME['primary'], linewidth=2.5,
            label=f'Broad ({broad.iloc[-1]:.1f})')
    ax.plot(dm.index, dm, color=THEME['secondary'], linewidth=2.0,
            label=f'Advanced Economies ({dm.iloc[-1]:.1f})')
    ax.plot(em.index, em, color=THEME['tertiary'], linewidth=2.0,
            label=f'Emerging Markets ({em.iloc[-1]:.1f})')

    style_single_ax(ax, fmt='{:.0f}')
    set_xlim_to_data(ax, broad.index)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    add_last_value_label(ax, broad, color=THEME['primary'], fmt='{:.1f}', side='right')
    add_last_value_label(ax, dm, color=THEME['secondary'], fmt='{:.1f}', side='right')
    add_last_value_label(ax, em, color=THEME['tertiary'], fmt='{:.1f}', side='right')
    add_recessions(ax, start_date='2006-01-01')
    ax.legend(loc='upper left', **legend_style())

    add_annotation_box(ax,
        "Strong dollar = cheap imports, expensive exports.\n"
        "EM currencies under disproportionate stress.",
        x=0.50, y=0.95)

    brand_fig(fig, 'Trade-Weighted Dollar: The Competitiveness Gauge',
              subtitle='Broad, Advanced Economies, and Emerging Markets',
              source='Federal Reserve via FRED',
              data_date=broad.index[-1])

    return save_fig(fig, 'chart_03_dollar_indices.png')


# ============================================
# CHART 4: Exports & Imports YoY Growth [Figure 4]
# ============================================
def chart_04():
    """Exports and Imports YoY growth rates, showing volume dynamics."""
    print('\nChart 4: Exports & Imports YoY...')

    exp_yoy = fetch_fred_yoy('BOPTEXP', trim='2000-01-01')
    imp_yoy = fetch_fred_yoy('BOPTIMP', trim='2000-01-01')

    # Align
    idx = exp_yoy.index.intersection(imp_yoy.index)
    exp_yoy = exp_yoy.loc[idx]
    imp_yoy = imp_yoy.loc[idx]

    fig, ax = new_fig()

    ax.plot(exp_yoy.index, exp_yoy, color=THEME['primary'], linewidth=2.5,
            label=f'Exports YoY ({exp_yoy.iloc[-1]:.1f}%)')
    ax.plot(imp_yoy.index, imp_yoy, color=THEME['secondary'], linewidth=2.5,
            label=f'Imports YoY ({imp_yoy.iloc[-1]:.1f}%)')

    ax.axhline(0, color=COLORS['doldrums'], linewidth=0.8, linestyle='--', alpha=0.5)

    # Shade negative export growth
    ax.fill_between(exp_yoy.index, 0, exp_yoy,
                    where=(exp_yoy < 0),
                    color=COLORS['venus'], alpha=0.08)

    style_single_ax(ax)
    set_xlim_to_data(ax, exp_yoy.index)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    add_last_value_label(ax, exp_yoy, color=THEME['primary'], side='right')
    add_last_value_label(ax, imp_yoy, color=THEME['secondary'], side='right')
    add_recessions(ax, start_date='2000-01-01')

    # Add recession shading to legend
    from matplotlib.patches import Patch
    handles, labels = ax.get_legend_handles_labels()
    handles.append(Patch(facecolor=THEME['recession'], alpha=THEME['recession_alpha'],
                         label='NBER Recession'))
    ax.legend(handles=handles, loc='upper left', **legend_style())

    add_annotation_box(ax,
        "Exports rebounding while imports contract.\n"
        "Divergence signals shifting demand dynamics.",
        x=0.52, y=0.92)

    brand_fig(fig, 'U.S. Exports & Imports: Year-Over-Year Growth',
              subtitle='When both decelerate, global demand is weakening',
              source='Census Bureau via FRED',
              data_date=exp_yoy.index[-1])

    return save_fig(fig, 'chart_04_exports_imports_yoy.png')


# ============================================
# CHART 5: China Bilateral Trade (Decoupling) [Figure 5]
# ============================================
def chart_05():
    """U.S.-China bilateral trade: exports to vs imports from China."""
    print('\nChart 5: China Bilateral Trade...')

    exp_china = fetch_fred_level('EXPCH', start='2000-01-01')
    imp_china = fetch_fred_level('IMPCH', start='2000-01-01')

    fig, ax = new_fig()

    ax.plot(imp_china.index, imp_china, color=THEME['secondary'], linewidth=2.5,
            label=f'Imports from China (${imp_china.iloc[-1]/1000:.1f}B)')
    ax.plot(exp_china.index, exp_china, color=THEME['primary'], linewidth=2.5,
            label=f'Exports to China (${exp_china.iloc[-1]/1000:.1f}B)')

    # Fill the gap between imports and exports (the deficit)
    idx = imp_china.index.intersection(exp_china.index)
    ax.fill_between(idx, exp_china.loc[idx], imp_china.loc[idx],
                    alpha=0.12, color=COLORS['venus'],
                    label='Bilateral Deficit')

    style_single_ax(ax, fmt='${:.0f}M')
    set_xlim_to_data(ax, imp_china.index)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    add_last_value_label(ax, imp_china, color=THEME['secondary'],
                         fmt='${:.0f}M', side='right')
    add_last_value_label(ax, exp_china, color=THEME['primary'],
                         fmt='${:.0f}M', side='right')
    add_recessions(ax, start_date='2000-01-01')
    ax.legend(loc='upper left', **legend_style())

    add_annotation_box(ax,
        "China imports peaked 2018 and are falling.\n"
        "Decoupling is real: 22% → 13% import share.",
        x=0.40, y=0.92)

    brand_fig(fig, 'U.S.-China Trade: The Decoupling',
              subtitle='Import share falling, but the deficit shifted, not eliminated',
              source='Census Bureau via FRED',
              data_date=imp_china.index[-1])

    return save_fig(fig, 'chart_05_china_bilateral.png')


# ============================================
# CHART 6: Import Price Components (Pipeline Detail) [Figure 6]
# ============================================
def chart_06():
    """Import price breakdown: All, ex-Petroleum, Consumer Goods, Industrial Supplies."""
    print('\nChart 6: Import Price Components...')

    imp_all = fetch_fred_yoy('IR', trim='2000-01-01')
    imp_xpet = fetch_fred_yoy('IREXPET', trim='2000-01-01')
    imp_cons = fetch_fred_yoy('IR4', trim='2000-01-01')
    imp_ind = fetch_fred_yoy('IR1', trim='2000-01-01')

    fig, ax = new_fig()

    ax.plot(imp_all.index, imp_all, color=THEME['primary'], linewidth=2.5,
            label=f'All Imports ({imp_all.iloc[-1]:.1f}%)')
    ax.plot(imp_xpet.index, imp_xpet, color=THEME['secondary'], linewidth=2.0,
            label=f'Ex-Petroleum ({imp_xpet.iloc[-1]:.1f}%)')
    ax.plot(imp_cons.index, imp_cons, color=THEME['tertiary'], linewidth=2.0,
            label=f'Consumer Goods ({imp_cons.iloc[-1]:.1f}%)')
    ax.plot(imp_ind.index, imp_ind, color=THEME['quaternary'], linewidth=1.8,
            label=f'Industrial Supplies ({imp_ind.iloc[-1]:.1f}%)')

    ax.axhline(0, color=COLORS['doldrums'], linewidth=0.8, linestyle='--', alpha=0.5)

    style_single_ax(ax)
    set_xlim_to_data(ax, imp_all.index)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    add_last_value_label(ax, imp_all, color=THEME['primary'], side='right')
    add_recessions(ax, start_date='2000-01-01')
    ax.legend(loc='upper left', ncol=2, **legend_style())

    add_annotation_box(ax,
        "Ex-petroleum strips oil noise.\n"
        "Consumer goods prices tell you what hits wallets.",
        x=0.57, y=0.92)

    brand_fig(fig, 'Import Price Decomposition',
              subtitle='Where the tariff pressure is actually landing',
              source='BLS via FRED',
              data_date=imp_all.index[-1])

    return save_fig(fig, 'chart_06_import_price_components.png')


# ============================================
# CHART 7: Terms of Trade (Export/Import Price Ratio) [Figure 7]
# ============================================
def chart_07():
    """Terms of Trade: Export Price Index / Import Price Index."""
    print('\nChart 7: Terms of Trade...')

    exp_px = fetch_fred_level('IQ', start='1990-01-01')
    imp_px = fetch_fred_level('IR', start='1990-01-01')

    idx = exp_px.index.intersection(imp_px.index)
    exp_px = exp_px.loc[idx]
    imp_px = imp_px.loc[idx]

    tot = (exp_px / imp_px) * 100  # Index, 100 = neutral

    fig, ax = new_fig()

    ax.plot(tot.index, tot, color=THEME['primary'], linewidth=2.5,
            label=f'Terms of Trade ({tot.iloc[-1]:.1f})')

    ax.axhline(100, color=COLORS['doldrums'], linewidth=0.8, linestyle='--', alpha=0.5)

    # Fill above/below 100
    ax.fill_between(tot.index, 100, tot,
                    where=(tot > 100),
                    color=COLORS['sea'], alpha=0.12, label='Favorable')
    ax.fill_between(tot.index, 100, tot,
                    where=(tot < 100),
                    color=COLORS['venus'], alpha=0.12, label='Deteriorating')

    style_single_ax(ax, fmt='{:.0f}')
    set_xlim_to_data(ax, tot.index)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    add_last_value_label(ax, tot, color=THEME['primary'], fmt='{:.1f}', side='right')
    add_recessions(ax, start_date='1990-01-01')
    ax.legend(loc='upper left', **legend_style())

    add_annotation_box(ax,
        "Above 100 = export prices outpacing imports.\n"
        "Energy independence and services exports driving favorable terms.",
        x=0.52, y=0.92)

    brand_fig(fig, 'Terms of Trade: Competitiveness Barometer',
              subtitle='Export prices relative to import prices (100 = neutral)',
              source='BLS via FRED',
              data_date=tot.index[-1])

    return save_fig(fig, 'chart_07_terms_of_trade.png')


# ============================================
# CHART 8: Trade Policy Uncertainty (EPUTRADE) [Figure 8]
# ============================================
def chart_08():
    """Trade Policy Uncertainty Index with tariff regime annotations."""
    print('\nChart 8: Trade Policy Uncertainty...')

    tpu = fetch_fred_level('EPUTRADE', start='1985-01-01')

    fig, ax = new_fig()

    ax.plot(tpu.index, tpu, color=THEME['primary'], linewidth=2.5,
            label=f'Trade Policy Uncertainty ({tpu.iloc[-1]:.0f})')

    # Fill elevated zones
    ax.fill_between(tpu.index, 0, tpu,
                    where=(tpu > 200),
                    color=COLORS['venus'], alpha=0.12)

    # Key event annotations
    events = [
        ('1993-11-01', 'NAFTA\nDebate', 0.05),
        ('2001-12-01', 'China\nWTO', 0.05),
        ('2018-03-01', 'Steel/Aluminum\nTariffs', 0.05),
        ('2019-08-01', 'Trade War\nEscalation', 0.05),
        ('2025-01-01', '2025 Tariff\nRegime', 0.05),
    ]
    for date_str, label, offset in events:
        dt = pd.Timestamp(date_str)
        if dt >= tpu.index.min():
            y_val = tpu.loc[tpu.index >= dt].iloc[0] if len(tpu.loc[tpu.index >= dt]) > 0 else 0
            ax.annotate(label, xy=(dt, y_val),
                        xytext=(0, 25), textcoords='offset points',
                        fontsize=8, color=THEME['fg'], ha='center',
                        arrowprops=dict(arrowstyle='->', color=THEME['muted'], lw=0.8))

    style_single_ax(ax, fmt='{:.0f}')
    set_xlim_to_data(ax, tpu.index)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    add_last_value_label(ax, tpu, color=THEME['primary'], fmt='{:.0f}', side='right')
    add_recessions(ax, start_date='1985-01-01')
    ax.legend(loc='upper left', **legend_style())

    add_annotation_box(ax,
        "Trade policy uncertainty leads capex by 3-6 months.\n"
        "At record highs, eclipsing 2019 trade war peaks.",
        x=0.55, y=0.80)

    brand_fig(fig, 'Trade Policy Uncertainty Index',
              subtitle='When businesses cannot plan, they do not invest',
              source='PolicyUncertainty.com via FRED',
              data_date=tpu.index[-1])

    return save_fig(fig, 'chart_08_trade_policy_uncertainty.png')


# ============================================
# CHART 9: Current Account Balance (Structural) [Figure 9]
# ============================================
def chart_09():
    """Current Account Balance: Goods, Services, Primary Income decomposition."""
    print('\nChart 9: Current Account Balance...')

    ca_total = fetch_quarterly_level('IEABC', start='1990-01-01')
    ca_goods = fetch_quarterly_level('IEABCG', start='1990-01-01')
    ca_services = fetch_quarterly_level('IEABCS', start='1990-01-01')
    ca_income = fetch_quarterly_level('IEABCPI', start='1990-01-01')

    fig, ax = new_fig()

    ax.plot(ca_total.index, ca_total / 1000, color=THEME['primary'], linewidth=2.5,
            label=f'Current Account (${ca_total.iloc[-1]/1000:.0f}B)')
    ax.plot(ca_goods.index, ca_goods / 1000, color=THEME['secondary'], linewidth=2.0,
            label=f'Goods (${ca_goods.iloc[-1]/1000:.0f}B)')
    ax.plot(ca_services.index, ca_services / 1000, color=THEME['tertiary'], linewidth=2.0,
            label=f'Services (${ca_services.iloc[-1]/1000:.0f}B)')
    ax.plot(ca_income.index, ca_income / 1000, color=THEME['quaternary'], linewidth=2.0,
            label=f'Primary Income (${ca_income.iloc[-1]/1000:.0f}B)')

    ax.axhline(0, color=COLORS['doldrums'], linewidth=0.8, linestyle='--', alpha=0.5)

    style_single_ax(ax, fmt='${:.0f}B')
    set_xlim_to_data(ax, ca_total.index)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    add_last_value_label(ax, ca_total / 1000, color=THEME['primary'],
                         fmt='${:.0f}B', side='right')
    add_recessions(ax, start_date='1990-01-01')
    ax.legend(loc='lower left', **legend_style())

    add_annotation_box(ax,
        "Goods deficit dominates, but services surplus\n"
        "and primary income partially offset.",
        x=0.55, y=0.15)

    brand_fig(fig, 'Current Account Decomposition',
              subtitle='The financial mirror of every trade deficit',
              source='BEA via FRED',
              data_date=ca_total.index[-1])

    return save_fig(fig, 'chart_09_current_account.png')


# ============================================
# CHART 10: Inventory-to-Sales Ratios [Figure 10]
# ============================================
def chart_10():
    """Inventory-to-Sales: Total, Wholesale, Retail, Manufacturers."""
    print('\nChart 10: Inventory-to-Sales Ratios...')

    total = fetch_fred_level('ISRATIO', start='1992-01-01')
    wholesale = fetch_fred_level('WHLSLRIRSA', start='1992-01-01')
    retail = fetch_fred_level('RETAILIRSA', start='1992-01-01')
    mfg = fetch_fred_level('MNFCTRIRSA', start='1992-01-01')

    fig, ax = new_fig()

    ax.plot(total.index, total, color=THEME['primary'], linewidth=2.5,
            label=f'Total Business ({total.iloc[-1]:.2f})')
    ax.plot(wholesale.index, wholesale, color=THEME['secondary'], linewidth=2.0,
            label=f'Wholesale ({wholesale.iloc[-1]:.2f})')
    ax.plot(retail.index, retail, color=THEME['tertiary'], linewidth=2.0,
            label=f'Retail ({retail.iloc[-1]:.2f})')
    ax.plot(mfg.index, mfg, color=THEME['quaternary'], linewidth=2.0,
            label=f'Manufacturers ({mfg.iloc[-1]:.2f})')

    style_single_ax(ax, fmt='{:.2f}')
    set_xlim_to_data(ax, total.index)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    add_last_value_label(ax, total, color=THEME['primary'],
                         fmt='{:.2f}', side='right')
    add_recessions(ax, start_date='1992-01-01')
    ax.legend(loc='upper left', **legend_style())

    add_annotation_box(ax,
        "Wholesale I/S rising = importers front-loading\n"
        "ahead of tariff escalation. Watch for reversal.",
        x=0.52, y=0.15)

    brand_fig(fig, 'Inventory-to-Sales Ratios',
              subtitle='Where trade flows meet domestic demand',
              source='Census Bureau via FRED',
              data_date=total.index[-1])

    return save_fig(fig, 'chart_10_inventory_sales.png')


# ============================================
# CHART 11: Goods vs Services Trade Balance [Figure 11]
# ============================================
def chart_11():
    """Goods vs Services trade balance: the structural split."""
    print('\nChart 11: Goods vs Services Balance...')

    goods = fetch_fred_level('BOPGTB', start='1992-01-01')
    services = fetch_fred_level('BOPSTB', start='1992-01-01')

    fig, ax = new_fig()

    ax.plot(goods.index, goods / 1000, color=THEME['secondary'], linewidth=2.5,
            label=f'Goods Balance (${goods.iloc[-1]/1000:.0f}B)')
    ax.plot(services.index, services / 1000, color=THEME['primary'], linewidth=2.5,
            label=f'Services Balance (${services.iloc[-1]/1000:.0f}B)')

    ax.axhline(0, color=COLORS['doldrums'], linewidth=0.8, linestyle='--', alpha=0.5)

    ax.fill_between(goods.index, 0, goods / 1000,
                    where=(goods < 0),
                    color=COLORS['venus'], alpha=0.08)
    ax.fill_between(services.index, 0, services / 1000,
                    where=(services > 0),
                    color=COLORS['sea'], alpha=0.08)

    style_single_ax(ax, fmt='${:.0f}B')
    set_xlim_to_data(ax, goods.index)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    add_last_value_label(ax, goods / 1000, color=THEME['secondary'],
                         fmt='${:.0f}B', side='right')
    add_last_value_label(ax, services / 1000, color=THEME['primary'],
                         fmt='${:.0f}B', side='right')
    add_recessions(ax, start_date='1992-01-01')
    ax.legend(loc='lower left', **legend_style())

    add_annotation_box(ax,
        "Services surplus (~$22B/mo) partially offsets\n"
        "the goods deficit (~$100B/mo). Tech, finance, IP.",
        x=0.70, y=0.92)

    brand_fig(fig, 'Goods vs Services Trade Balance',
              subtitle='The structural split that defines U.S. trade',
              source='Census Bureau via FRED',
              data_date=goods.index[-1])

    return save_fig(fig, 'chart_11_goods_vs_services.png')


# ============================================
# CHART 12: Dollar Z-RoC (63-Day Rate of Change) [Figure 12]
# ============================================
def chart_12():
    """Dollar 63-day rate of change with regime bands."""
    print('\nChart 12: Dollar Z-RoC...')

    broad = fetch_fred_level('DTWEXBGS', start='2006-01-01')
    # Resample to daily then compute 63-day RoC
    daily = broad.resample('D').ffill()
    roc_63 = daily.pct_change(63) * 100
    # Z-score
    mu = roc_63.rolling(252, min_periods=126).mean()
    sigma = roc_63.rolling(252, min_periods=126).std()
    z_roc = ((roc_63 - mu) / sigma).dropna()

    fig, ax = new_fig()

    # Color-segment the line using LineCollection
    from matplotlib.collections import LineCollection
    x_vals = mdates.date2num(z_roc.index)
    y_vals = z_roc.values
    segments = []
    colors_list = []
    for i in range(len(x_vals) - 1):
        segments.append([[x_vals[i], y_vals[i]], [x_vals[i+1], y_vals[i+1]]])
        if y_vals[i] > 1.5:
            colors_list.append(COLORS['venus'])
        elif y_vals[i] < -1.5:
            colors_list.append(COLORS['sky'])
        else:
            colors_list.append(COLORS['ocean'])
    lc = LineCollection(segments, colors=colors_list, linewidths=2.0)
    ax.add_collection(lc)
    ax.autoscale()

    # Regime bands
    ax.axhspan(1.5, ax.get_ylim()[1], color=COLORS['venus'], alpha=0.06)
    ax.axhspan(ax.get_ylim()[0], -1.5, color=COLORS['sky'], alpha=0.06)
    ax.axhline(1.5, color=COLORS['venus'], linewidth=0.8, linestyle='--', alpha=0.5)
    ax.axhline(-1.5, color=COLORS['sky'], linewidth=0.8, linestyle='--', alpha=0.5)
    ax.axhline(0, color=COLORS['doldrums'], linewidth=0.8, linestyle='--', alpha=0.3)

    # Legend entries
    ax.plot([], [], color=COLORS['venus'], linewidth=2, label='USD Strength Extreme (>+1.5)')
    ax.plot([], [], color=COLORS['ocean'], linewidth=2, label='Neutral')
    ax.plot([], [], color=COLORS['sky'], linewidth=2, label='USD Weakness Extreme (<-1.5)')

    style_single_ax(ax, fmt='{:.1f}')
    set_xlim_to_data(ax, z_roc.index)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    add_last_value_label(ax, z_roc, color=COLORS['ocean'], fmt='{:.2f}', side='right')
    add_recessions(ax, start_date='2006-01-01')
    ax.legend(loc='upper left', **legend_style())

    add_annotation_box(ax,
        "Dollar Z-RoC: momentum of the dollar.\n"
        "At extremes (>1.5 or <-1.5), reversals are probable.",
        x=0.52, y=0.955)

    brand_fig(fig, 'Dollar Z-RoC: The Momentum Signal',
              subtitle='63-day rate of change, z-scored for regime detection',
              source='Federal Reserve via FRED',
              data_date=z_roc.index[-1])

    return save_fig(fig, 'chart_12_dollar_zroc.png')


# ============================================
# CHART 13: Import Prices ex-Petro vs Core PCE (Lagged Pipeline) [Figure 13]
# ============================================
def chart_13():
    """Import Prices ex-Petroleum (lagged 4 months) vs Core PCE YoY."""
    print('\nChart 13: Import Prices ex-Petro vs Core PCE...')

    imp_xpet = fetch_fred_yoy('IREXPET', trim='2000-01-01')
    core_pce = fetch_fred_yoy('PCEPILFE', trim='2000-01-01')

    # Lag import prices by 4 months (shift forward for alignment)
    imp_lagged = imp_xpet.shift(4)

    idx = imp_lagged.dropna().index.intersection(core_pce.index)
    imp_lagged = imp_lagged.loc[idx]
    core_pce = core_pce.loc[idx]

    fig, ax1 = new_fig()
    ax2 = ax1.twinx()
    c1, c2 = THEME['secondary'], THEME['primary']

    ax1.plot(imp_lagged.index, imp_lagged, color=c1, linewidth=2.5,
             label=f'Import Prices ex-Petro YoY, 4M Lag ({imp_lagged.iloc[-1]:.1f}%)')
    ax2.plot(core_pce.index, core_pce, color=c2, linewidth=2.5,
             label=f'Core PCE YoY ({core_pce.iloc[-1]:.1f}%)')

    ax1.axhline(0, color=COLORS['doldrums'], linewidth=0.8, linestyle='--', alpha=0.5)

    style_dual_ax(ax1, ax2, c1, c2)
    ax1.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.0f}%'))
    ax2.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.1f}%'))
    set_xlim_to_data(ax1, imp_lagged.index)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    align_yaxis_zero(ax1, ax2)

    add_last_value_label(ax1, imp_lagged, color=c1, side='left')
    add_last_value_label(ax2, core_pce, color=c2, side='right')
    add_recessions(ax1, start_date='2000-01-01')

    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax1.legend(h1 + h2, l1 + l2, loc='upper left', **legend_style())

    add_annotation_box(ax1,
        "Import prices ex-petro lead core PCE by ~4 months.\n"
        "The tariff pipeline is building pressure.",
        x=0.55, y=0.93)

    brand_fig(fig, 'The Tariff Pipeline: Import Prices → Core PCE',
              subtitle='Import prices ex-petroleum (4-month lag) vs Core PCE',
              source='BLS, BEA via FRED',
              data_date=core_pce.index[-1])

    return save_fig(fig, 'chart_13_import_prices_core_pce.png')


# ============================================
# CHART 14: Broad Dollar vs Export Volume YoY (Inverse Relationship) [Figure 14]
# ============================================
def chart_14():
    """Dollar strength (inverted) vs Real Export growth."""
    print('\nChart 14: Dollar vs Exports...')

    dollar_yoy = fetch_fred_yoy('DTWEXBGS', trim='2008-01-01')
    exp_yoy = fetch_quarterly_yoy('EXPGSC1', trim='2008-01-01')

    idx = dollar_yoy.index.intersection(exp_yoy.index)
    dollar_yoy = dollar_yoy.loc[idx]
    exp_yoy = exp_yoy.loc[idx]

    fig, ax1 = new_fig()
    ax2 = ax1.twinx()
    c1, c2 = THEME['secondary'], THEME['primary']

    ax1.plot(dollar_yoy.index, -dollar_yoy, color=c1, linewidth=2.5,
             label=f'Broad Dollar YoY (INVERTED, {-dollar_yoy.iloc[-1]:.1f}%)')
    ax2.plot(exp_yoy.index, exp_yoy, color=c2, linewidth=2.5,
             label=f'Real Exports YoY ({exp_yoy.iloc[-1]:.1f}%)')

    ax1.axhline(0, color=COLORS['doldrums'], linewidth=0.8, linestyle='--', alpha=0.5)

    style_dual_ax(ax1, ax2, c1, c2)
    ax1.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.0f}%'))
    ax2.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.0f}%'))
    set_xlim_to_data(ax1, dollar_yoy.index)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    align_yaxis_zero(ax1, ax2)

    add_last_value_label(ax1, -dollar_yoy, color=c1, side='left')
    add_last_value_label(ax2, exp_yoy, color=c2, side='right')
    add_recessions(ax1, start_date='2008-01-01')

    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax1.legend(h1 + h2, l1 + l2, loc='upper left', **legend_style())

    add_annotation_box(ax1,
        "Strong dollar = weak exports. The relationship\n"
        "is tight with a 3-6 month transmission lag.",
        x=0.52, y=0.15)

    brand_fig(fig, 'The Dollar-Export Trade-Off',
              subtitle='Dollar strength (inverted) vs real export growth',
              source='Federal Reserve, BEA via FRED',
              data_date=dollar_yoy.index[-1])

    return save_fig(fig, 'chart_14_dollar_vs_exports.png')


# ============================================
# CHART 15: Japan Bilateral Trade [Figure 15]
# ============================================
def chart_15():
    """U.S.-Japan bilateral trade."""
    print('\nChart 15: Japan Bilateral Trade...')

    exp_jp = fetch_fred_level('EXPJP', start='2000-01-01')
    imp_jp = fetch_fred_level('IMPJP', start='2000-01-01')

    fig, ax = new_fig()

    ax.plot(imp_jp.index, imp_jp, color=THEME['secondary'], linewidth=2.5,
            label=f'Imports from Japan (${imp_jp.iloc[-1]/1000:.1f}B)')
    ax.plot(exp_jp.index, exp_jp, color=THEME['primary'], linewidth=2.5,
            label=f'Exports to Japan (${exp_jp.iloc[-1]/1000:.1f}B)')

    idx = imp_jp.index.intersection(exp_jp.index)
    ax.fill_between(idx, exp_jp.loc[idx], imp_jp.loc[idx],
                    alpha=0.12, color=COLORS['venus'],
                    label='Bilateral Deficit')

    style_single_ax(ax, fmt='${:.0f}M')
    set_xlim_to_data(ax, imp_jp.index)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    add_last_value_label(ax, imp_jp, color=THEME['secondary'],
                         fmt='${:.0f}M', side='right')
    add_last_value_label(ax, exp_jp, color=THEME['primary'],
                         fmt='${:.0f}M', side='right')
    add_recessions(ax, start_date='2000-01-01')
    ax.legend(loc='upper left', **legend_style())

    add_annotation_box(ax,
        "Japan deficit narrowing as yen weakens.\n"
        "Autos and semiconductors dominate imports.",
        x=0.30, y=0.92)

    brand_fig(fig, 'U.S.-Japan Trade',
              subtitle='Key bilateral for autos, semiconductors, and the yen carry trade',
              source='Census Bureau via FRED',
              data_date=imp_jp.index[-1])

    return save_fig(fig, 'chart_15_japan_bilateral.png')


# ============================================
# CHART 16: BIS Real Effective Exchange Rate (Competitiveness) [Figure 16]
# ============================================
def chart_16():
    """BIS REER vs long-run average: dollar valuation."""
    print('\nChart 16: BIS Real Effective Exchange Rate...')

    reer = fetch_fred_level('RBUSBIS', start='1994-01-01')

    fig, ax = new_fig()

    ax.plot(reer.index, reer, color=THEME['primary'], linewidth=2.5,
            label=f'BIS REER ({reer.iloc[-1]:.1f})')

    # 10-year rolling average
    avg_10y = reer.rolling(120, min_periods=60).mean()
    ax.plot(avg_10y.index, avg_10y, color=THEME['secondary'], linewidth=1.5,
            linestyle='--', label=f'10Y Average ({avg_10y.iloc[-1]:.1f})')

    # Fill above/below average
    idx = avg_10y.dropna().index
    ax.fill_between(idx, avg_10y.loc[idx], reer.loc[idx],
                    where=(reer.loc[idx] > avg_10y.loc[idx]),
                    color=COLORS['venus'], alpha=0.10, label='Overvalued')
    ax.fill_between(idx, avg_10y.loc[idx], reer.loc[idx],
                    where=(reer.loc[idx] < avg_10y.loc[idx]),
                    color=COLORS['sea'], alpha=0.10, label='Undervalued')

    style_single_ax(ax, fmt='{:.0f}')
    set_xlim_to_data(ax, reer.index)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    add_last_value_label(ax, reer, color=THEME['primary'], fmt='{:.1f}', side='right')
    add_recessions(ax, start_date='1994-01-01')
    ax.legend(loc='lower left', **legend_style())

    dev_pct = (reer.iloc[-1] / avg_10y.iloc[-1] - 1) * 100
    add_annotation_box(ax,
        f"BIS REER {dev_pct:+.0f}% vs 10Y average.\n"
        "Inflation-adjusted: the gold standard for\n"
        "competitiveness analysis.",
        x=0.30, y=0.92)

    brand_fig(fig, 'BIS Real Effective Exchange Rate',
              subtitle='Dollar valuation adjusted for inflation differentials',
              source='Bank for International Settlements via FRED',
              data_date=reer.index[-1])

    return save_fig(fig, 'chart_16_bis_reer.png')


# ============================================
# CHART 17: Export vs Import Price Divergence (Terms of Trade Momentum) [Figure 17]
# ============================================
def chart_17():
    """Export Price YoY minus Import Price YoY: the margin signal."""
    print('\nChart 17: Export-Import Price Spread...')

    exp_yoy = fetch_fred_yoy('IQ', trim='1995-01-01')
    imp_yoy = fetch_fred_yoy('IR', trim='1995-01-01')

    idx = exp_yoy.index.intersection(imp_yoy.index)
    exp_yoy = exp_yoy.loc[idx]
    imp_yoy = imp_yoy.loc[idx]
    spread = exp_yoy - imp_yoy

    fig, ax = new_fig()

    # Color-segment: green above 0, red below 0
    from matplotlib.collections import LineCollection
    x_vals = mdates.date2num(spread.index)
    y_vals = spread.values
    segs = []
    seg_colors = []
    for i in range(len(x_vals) - 1):
        segs.append([[x_vals[i], y_vals[i]], [x_vals[i+1], y_vals[i+1]]])
        seg_colors.append(COLORS['sea'] if y_vals[i] >= 0 else COLORS['venus'])
    lc = LineCollection(segs, colors=seg_colors, linewidths=2.5)
    ax.add_collection(lc)
    ax.autoscale()

    ax.fill_between(spread.index, 0, spread,
                    where=(spread > 0),
                    color=COLORS['sea'], alpha=0.10)
    ax.fill_between(spread.index, 0, spread,
                    where=(spread < 0),
                    color=COLORS['venus'], alpha=0.10)

    ax.axhline(0, color=COLORS['doldrums'], linewidth=1.0, linestyle='--', alpha=0.5)

    ax.plot([], [], color=COLORS['sea'], linewidth=2.5, label='Favorable (exports outpacing)')
    ax.plot([], [], color=COLORS['venus'], linewidth=2.5, label='Deteriorating (imports outpacing)')

    style_single_ax(ax, fmt='{:.1f} ppt')
    set_xlim_to_data(ax, spread.index)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    add_last_value_label(ax, spread,
                         color=COLORS['sea'] if spread.iloc[-1] >= 0 else COLORS['venus'],
                         fmt='{:.1f} ppt', side='right')
    add_recessions(ax, start_date='1995-01-01')
    ax.legend(loc='upper left', **legend_style())

    add_annotation_box(ax,
        "Negative = import costs rising faster than\n"
        "export prices. Margin compression for U.S. firms.",
        x=0.52, y=0.15)

    brand_fig(fig, 'Export-Import Price Spread',
              subtitle='The margin signal: who is absorbing the cost pressure?',
              source='BLS via FRED',
              data_date=spread.index[-1])

    return save_fig(fig, 'chart_17_export_import_spread.png')


# ============================================
# CHART 18: Freight/Logistics Indicators [Figure 18]
# ============================================
def chart_18():
    """Domestic freight: TSI, Cass, Truck Tonnage, Rail Intermodal."""
    print('\nChart 18: Freight/Logistics Indicators...')

    tsi = fetch_fred_yoy('TSIFRGHT', trim='2005-01-01')
    cass = fetch_fred_yoy('FRGSHPUSM649NCIS', trim='2005-01-01')
    truck = fetch_fred_yoy('TRUCKD11', trim='2005-01-01')
    rail = fetch_fred_yoy('RAILFRTINTERMODALD11', trim='2005-01-01')

    fig, ax = new_fig()

    ax.plot(tsi.index, tsi, color=THEME['primary'], linewidth=2.5,
            label=f'TSI Freight ({tsi.iloc[-1]:.1f}%)')
    ax.plot(cass.index, cass, color=THEME['secondary'], linewidth=2.0,
            label=f'Cass Freight ({cass.iloc[-1]:.1f}%)')
    ax.plot(truck.index, truck, color=THEME['tertiary'], linewidth=2.0,
            label=f'Truck Tonnage ({truck.iloc[-1]:.1f}%)')
    ax.plot(rail.index, rail, color=THEME['quaternary'], linewidth=2.0,
            label=f'Rail Intermodal ({rail.iloc[-1]:.1f}%)')

    ax.axhline(0, color=COLORS['doldrums'], linewidth=0.8, linestyle='--', alpha=0.5)

    style_single_ax(ax)
    set_xlim_to_data(ax, tsi.index)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    add_recessions(ax, start_date='2005-01-01')
    ax.legend(loc='upper left', ncol=2, **legend_style())

    add_annotation_box(ax,
        "Freight volumes are the physical heartbeat of trade.\n"
        "When all four decline, goods recession is underway.",
        x=0.52, y=0.15)

    brand_fig(fig, 'Domestic Freight: The Physical Trade Signal',
              subtitle='Year-over-year growth across transport modes',
              source='BTS, Cass, ATA, AAR via FRED',
              data_date=tsi.index[-1])

    return save_fig(fig, 'chart_18_freight_logistics.png')


# ============================================
# CHART 19: Real vs Nominal Retail Sales (Inflation Erosion) [Figure 19]
# ============================================
def chart_19():
    """Real vs Nominal Retail Sales YoY: the inflation tax on spending."""
    print('\nChart 19: Real vs Nominal Retail Sales...')

    nominal = fetch_fred_yoy('RSAFS', trim='2000-01-01')
    real = fetch_fred_yoy('RRSFS', trim='2000-01-01')

    idx = nominal.index.intersection(real.index)
    nominal = nominal.loc[idx]
    real = real.loc[idx]

    fig, ax = new_fig()

    ax.plot(nominal.index, nominal, color=THEME['secondary'], linewidth=2.5,
            label=f'Nominal Retail Sales YoY ({nominal.iloc[-1]:.1f}%)')
    ax.plot(real.index, real, color=THEME['primary'], linewidth=2.5,
            label=f'Real Retail Sales YoY ({real.iloc[-1]:.1f}%)')

    # Fill the gap (inflation tax)
    ax.fill_between(idx, real, nominal,
                    where=(nominal > real),
                    color=COLORS['venus'], alpha=0.10, label='Inflation Tax')

    ax.axhline(0, color=COLORS['doldrums'], linewidth=0.8, linestyle='--', alpha=0.5)

    style_single_ax(ax)
    set_xlim_to_data(ax, nominal.index)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    add_last_value_label(ax, nominal, color=THEME['secondary'], side='right')
    add_last_value_label(ax, real, color=THEME['primary'], side='right')
    add_recessions(ax, start_date='2000-01-01')
    ax.legend(loc='upper left', **legend_style())

    spread = nominal.iloc[-1] - real.iloc[-1]
    add_annotation_box(ax,
        f"Gap of {spread:.1f} ppts = inflation eating\n"
        "into real purchasing power. Tariffs widen this.",
        x=0.52, y=0.15)

    brand_fig(fig, 'Real vs Nominal Retail Sales',
              subtitle='The inflation tax on consumer spending',
              source='Census Bureau via FRED',
              data_date=nominal.index[-1])

    return save_fig(fig, 'chart_19_real_vs_nominal_retail.png')


# ============================================
# CHART 20: DM vs EM Dollar Indices YoY [Figure 20]
# ============================================
def chart_20():
    """Dollar strength: DM vs EM divergence."""
    print('\nChart 20: DM vs EM Dollar YoY...')

    dm_yoy = fetch_fred_yoy('DTWEXAFEGS', trim='2008-01-01')
    em_yoy = fetch_fred_yoy('DTWEXEMEGS', trim='2008-01-01')

    idx = dm_yoy.index.intersection(em_yoy.index)
    dm_yoy = dm_yoy.loc[idx]
    em_yoy = em_yoy.loc[idx]

    fig, ax = new_fig()

    ax.plot(dm_yoy.index, dm_yoy, color=THEME['primary'], linewidth=2.5,
            label=f'vs DM YoY ({dm_yoy.iloc[-1]:.1f}%)')
    ax.plot(em_yoy.index, em_yoy, color=THEME['secondary'], linewidth=2.5,
            label=f'vs EM YoY ({em_yoy.iloc[-1]:.1f}%)')

    ax.axhline(0, color=COLORS['doldrums'], linewidth=0.8, linestyle='--', alpha=0.5)

    # Shade when EM diverges from DM
    spread = em_yoy - dm_yoy
    ax.fill_between(idx, dm_yoy, em_yoy,
                    where=(em_yoy > dm_yoy),
                    color=COLORS['venus'], alpha=0.08, label='EM disproportionate stress')

    style_single_ax(ax)
    set_xlim_to_data(ax, dm_yoy.index)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    add_last_value_label(ax, dm_yoy, color=THEME['primary'], side='right')
    add_last_value_label(ax, em_yoy, color=THEME['secondary'], side='right')
    add_recessions(ax, start_date='2008-01-01')
    ax.legend(loc='upper left', **legend_style())

    add_annotation_box(ax,
        "When EM line > DM line, emerging markets are\n"
        "under disproportionate dollar pressure.",
        x=0.52, y=0.15)

    brand_fig(fig, 'Dollar Strength: DM vs EM',
              subtitle='Who is bearing the brunt of dollar strength?',
              source='Federal Reserve via FRED',
              data_date=dm_yoy.index[-1])

    return save_fig(fig, 'chart_20_dm_vs_em_dollar.png')


# ============================================
# CHART 21: Net Exports GDP Contribution [Figure 21]
# ============================================
def chart_21():
    """Net Exports (real) as GDP component."""
    print('\nChart 21: Net Exports GDP Contribution...')

    netexp = fetch_quarterly_level('NETEXC', start='1990-01-01')

    fig, ax = new_fig()

    ax.plot(netexp.index, netexp, color=THEME['primary'], linewidth=2.5,
            label=f'Real Net Exports (${netexp.iloc[-1]:.0f}B)')

    ax.axhline(0, color=COLORS['doldrums'], linewidth=0.8, linestyle='--', alpha=0.5)

    ax.fill_between(netexp.index, 0, netexp,
                    where=(netexp < 0),
                    color=COLORS['venus'], alpha=0.10)

    style_single_ax(ax, fmt='${:.0f}B')
    set_xlim_to_data(ax, netexp.index)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    add_last_value_label(ax, netexp, color=THEME['primary'],
                         fmt='${:.0f}B', side='right')
    add_recessions(ax, start_date='1990-01-01')
    ax.legend(loc='lower left', **legend_style())

    add_annotation_box(ax,
        "Net exports are a persistent GDP drag.\n"
        "Narrowing = GDP add, but quality matters.",
        x=0.685, y=0.20)

    brand_fig(fig, 'Real Net Exports: The GDP Drag',
              subtitle='Trade as a GDP component (chained 2017 dollars)',
              source='BEA via FRED',
              data_date=netexp.index[-1])

    return save_fig(fig, 'chart_21_net_exports_gdp.png')


# ============================================
# CHART 22: Trade Balance Long History (50+ Years) [Figure 22]
# ============================================
def chart_22():
    """Trade balance: the 50-year structural deterioration."""
    print('\nChart 22: Trade Balance Long History...')

    bal = fetch_fred_level('BOPGSTB', start='1970-01-01')

    fig, ax = new_fig()

    ax.plot(bal.index, bal, color=THEME['primary'], linewidth=2.5,
            label=f'Trade Balance G&S (${bal.iloc[-1]:.0f}B)')

    ax.fill_between(bal.index, 0, bal,
                    where=(bal < 0),
                    color=COLORS['venus'], alpha=0.08)
    ax.fill_between(bal.index, 0, bal,
                    where=(bal > 0),
                    color=COLORS['sea'], alpha=0.08)

    ax.axhline(0, color=COLORS['doldrums'], linewidth=0.8, linestyle='--', alpha=0.5)

    # Key event annotations
    events = [
        ('1971-08-01', 'Nixon\nShock'),
        ('1985-09-01', 'Plaza\nAccord'),
        ('1994-01-01', 'NAFTA'),
        ('2001-12-01', 'China\nWTO'),
        ('2018-07-01', 'Trade\nWar'),
    ]
    for date_str, label in events:
        dt = pd.Timestamp(date_str)
        if dt >= bal.index.min():
            closest_idx = bal.index[bal.index.searchsorted(dt)]
            y_val = bal.loc[closest_idx]
            ax.annotate(label, xy=(dt, y_val),
                        xytext=(0, 30), textcoords='offset points',
                        fontsize=8, color=THEME['fg'], ha='center',
                        arrowprops=dict(arrowstyle='->', color=THEME['muted'], lw=0.8))

    style_single_ax(ax, fmt='${:.0f}B')
    set_xlim_to_data(ax, bal.index)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    add_last_value_label(ax, bal, color=THEME['primary'], fmt='${:.0f}B', side='right')
    add_recessions(ax, start_date='1970-01-01')
    ax.legend(loc='lower left', **legend_style())

    add_annotation_box(ax,
        "50+ years of structural deficit.\n"
        "Each trade regime shift is visible.",
        x=0.70, y=0.50)

    brand_fig(fig, 'U.S. Trade Balance: The Long View',
              subtitle='From surplus to structural deficit since 1971',
              source='Census Bureau via FRED',
              data_date=bal.index[-1])

    return save_fig(fig, 'chart_22_trade_balance_long.png')


# ============================================
# CHART 23: Oil Production & Exports (Energy Trade) [Figure 23]
# ============================================
def chart_23():
    """U.S. crude oil production and exports from TradingView."""
    print('\nChart 23: Oil Production & Exports...')

    production = fetch_db_level('TV_USCOP', start='2000-01-01')
    exports = fetch_db_level('TV_USOE', start='2000-01-01')

    fig, ax1 = new_fig()
    ax2 = ax1.twinx()
    c1, c2 = THEME['primary'], THEME['secondary']

    ax1.plot(production.index, production, color=c1, linewidth=2.5,
             label=f'Crude Production ({production.iloc[-1]:.0f}K b/d)')
    ax2.plot(exports.index, exports, color=c2, linewidth=2.5,
             label=f'Oil Exports ({exports.iloc[-1]:.0f}K b/d)')

    style_dual_ax(ax1, ax2, c1, c2)
    ax1.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.0f}'))
    ax2.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.0f}'))
    set_xlim_to_data(ax1, production.index)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    add_last_value_label(ax1, production, color=c1, fmt='{:.0f}K', side='left')
    add_last_value_label(ax2, exports, color=c2, fmt='{:.0f}K', side='right')
    add_recessions(ax1, start_date='2000-01-01')

    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax1.legend(h1 + h2, l1 + l2, loc='upper left', **legend_style())

    add_annotation_box(ax1,
        "Structural shift: from net importer to\n"
        "near-net exporter. Deficit is now goods, not oil.",
        x=0.52, y=0.15)

    brand_fig(fig, 'U.S. Energy Trade: Production & Exports',
              subtitle='The structural shift from importer to exporter',
              source='EIA via TradingView',
              data_date=production.index[-1])

    return save_fig(fig, 'chart_23_oil_production_exports.png')


# ============================================
# CHART 24: TIC Net Long-Term Flows (Capital Flows) [Figure 24]
# ============================================
def chart_24():
    """TIC Net Long-Term Flows: who is buying U.S. assets."""
    print('\nChart 24: TIC Net Long-Term Flows...')

    tic = fetch_db_level('TV_USTICNLF', start='2000-01-01')

    fig, ax = new_fig()

    # 3-month moving average for smoothing
    tic_3m = tic.rolling(3, min_periods=1).mean()

    ax.bar(tic.index, tic / 1000, width=25, color=[COLORS['sea'] if v > 0 else COLORS['venus'] for v in tic],
           alpha=0.4, label='Monthly')
    ax.plot(tic_3m.index, tic_3m / 1000, color=THEME['primary'], linewidth=2.5,
            label=f'3M Avg (${tic_3m.iloc[-1]/1000:.1f}B)')

    ax.axhline(0, color=COLORS['doldrums'], linewidth=0.8, linestyle='--', alpha=0.5)

    style_single_ax(ax, fmt='${:.0f}B')
    set_xlim_to_data(ax, tic.index)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    add_last_value_label(ax, tic_3m / 1000, color=THEME['primary'],
                         fmt='${:.1f}B', side='right')
    add_recessions(ax, start_date='2000-01-01')
    ax.legend(loc='upper left', **legend_style())

    add_annotation_box(ax,
        "Negative TIC = foreigners SELLING U.S. assets.\n"
        "Watch Japan and China: both slowly reducing.",
        x=0.52, y=0.92)

    brand_fig(fig, 'TIC Net Long-Term Flows',
              subtitle='The financial mirror: are foreigners still buying?',
              source='Treasury Department via TradingView',
              data_date=tic.index[-1])

    return save_fig(fig, 'chart_24_tic_flows.png')


# ============================================
# CHART 25: Import-Sensitive Retail Categories [Figure 25]
# ============================================
def chart_25():
    """Import-sensitive retail: electronics, clothing, furniture YoY."""
    print('\nChart 25: Import-Sensitive Retail Categories...')

    electronics = fetch_fred_yoy('RSEAS', trim='2005-01-01')
    clothing = fetch_fred_yoy('RSCCAS', trim='2005-01-01')
    furniture = fetch_fred_yoy('MRTSSM442USN', trim='2005-01-01')

    fig, ax = new_fig()

    ax.plot(electronics.index, electronics, color=THEME['primary'], linewidth=2.5,
            label=f'Electronics ({electronics.iloc[-1]:.1f}%)')
    ax.plot(clothing.index, clothing, color=THEME['secondary'], linewidth=2.0,
            label=f'Clothing ({clothing.iloc[-1]:.1f}%)')
    ax.plot(furniture.index, furniture, color=THEME['tertiary'], linewidth=2.0,
            label=f'Furniture ({furniture.iloc[-1]:.1f}%)')

    ax.axhline(0, color=COLORS['doldrums'], linewidth=0.8, linestyle='--', alpha=0.5)

    style_single_ax(ax)
    set_xlim_to_data(ax, electronics.index)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    add_recessions(ax, start_date='2005-01-01')
    ax.legend(loc='upper left', **legend_style())

    add_annotation_box(ax,
        "These categories are tariff canaries.\n"
        "Rising prices + falling volumes = pass-through.",
        x=0.52, y=0.92)

    brand_fig(fig, 'Import-Sensitive Retail Categories',
              subtitle='Where tariff pass-through shows up first',
              source='Census Bureau via FRED',
              data_date=electronics.index[-1])

    return save_fig(fig, 'chart_25_import_sensitive_retail.png')


# ============================================
# CHART 26: E-Commerce Share of Retail [Figure 26]
# ============================================
def chart_26():
    """E-commerce as % of total retail sales: structural distribution shift."""
    print('\nChart 26: E-Commerce Share...')

    ecom_pct = fetch_quarterly_level('ECOMPCTSA', start='2000-01-01')

    fig, ax = new_fig()

    ax.plot(ecom_pct.index, ecom_pct, color=THEME['primary'], linewidth=2.5,
            label=f'E-Commerce Share ({ecom_pct.iloc[-1]:.1f}%)')

    ax.fill_between(ecom_pct.index, 0, ecom_pct,
                    color=COLORS['ocean'], alpha=0.10)

    style_single_ax(ax)
    set_xlim_to_data(ax, ecom_pct.index)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    add_last_value_label(ax, ecom_pct, color=THEME['primary'], side='right')
    add_recessions(ax, start_date='2000-01-01')
    ax.legend(loc='upper left', **legend_style())

    add_annotation_box(ax,
        "E-commerce bypasses some tariff pass-through\n"
        "via competitive pressure. Structural channel shift.",
        x=0.52, y=0.50)

    brand_fig(fig, 'E-Commerce Share of Retail Sales',
              subtitle='The structural shift in how imports reach consumers',
              source='Census Bureau via FRED',
              data_date=ecom_pct.index[-1])

    return save_fig(fig, 'chart_26_ecommerce_share.png')


# ============================================
# CHART 27: Foreign Holdings of Treasuries [Figure 27]
# ============================================
def chart_27():
    """Foreign holdings of U.S. Treasuries: the deficit financing machine."""
    print('\nChart 27: Foreign Treasury Holdings...')

    fh = fetch_fred_level('FDHBFIN', start='2000-01-01')

    fig, ax = new_fig()

    ax.plot(fh.index, fh / 1000, color=THEME['primary'], linewidth=2.5,
            label=f'Foreign Holdings (${fh.iloc[-1]/1000:.1f}T)')

    ax.fill_between(fh.index, 0, fh / 1000,
                    color=COLORS['ocean'], alpha=0.08)

    style_single_ax(ax, fmt='${:.1f}T')
    set_xlim_to_data(ax, fh.index)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    add_last_value_label(ax, fh / 1000, color=THEME['primary'],
                         fmt='${:.1f}T', side='right')
    add_recessions(ax, start_date='2000-01-01')
    ax.legend(loc='upper left', **legend_style())

    add_annotation_box(ax,
        "Foreign Treasury holdings = trade deficit\n"
        "recycled into U.S. debt markets. When this\n"
        "slows, term premium must rise.",
        x=0.52, y=0.50)

    brand_fig(fig, 'Foreign Holdings of U.S. Treasuries',
              subtitle='The capital account mirror of every trade deficit',
              source='Treasury Department via FRED',
              data_date=fh.index[-1])

    return save_fig(fig, 'chart_27_foreign_treasury_holdings.png')


# ============================================
# CHART 28: WTI Crude vs Import Prices (Energy Channel) [Figure 28]
# ============================================
def chart_28():
    """WTI crude oil vs all import prices: separating oil from tariffs."""
    print('\nChart 28: WTI vs Import Prices...')

    wti_yoy = fetch_fred_yoy('DCOILWTICO', trim='2000-01-01')
    imp_yoy = fetch_fred_yoy('IR', trim='2000-01-01')
    imp_xpet_yoy = fetch_fred_yoy('IREXPET', trim='2000-01-01')

    # Resample WTI to monthly for alignment
    wti_monthly = wti_yoy.resample('MS').last()

    idx = wti_monthly.dropna().index.intersection(imp_yoy.index).intersection(imp_xpet_yoy.index)
    wti_monthly = wti_monthly.loc[idx]
    imp_yoy_a = imp_yoy.loc[idx]
    imp_xpet_a = imp_xpet_yoy.loc[idx]

    fig, ax1 = new_fig()
    ax2 = ax1.twinx()
    c1, c2 = THEME['secondary'], THEME['primary']

    ax1.plot(wti_monthly.index, wti_monthly, color=c1, linewidth=2.0, alpha=0.7,
             label=f'WTI YoY ({wti_monthly.iloc[-1]:.0f}%)')
    ax2.plot(imp_yoy_a.index, imp_yoy_a, color=c2, linewidth=2.5,
             label=f'Import Prices All YoY ({imp_yoy_a.iloc[-1]:.1f}%)')
    ax2.plot(imp_xpet_a.index, imp_xpet_a, color=COLORS['sea'], linewidth=2.0,
             linestyle='--', label=f'Import Prices Ex-Petro ({imp_xpet_a.iloc[-1]:.1f}%)')

    ax1.axhline(0, color=COLORS['doldrums'], linewidth=0.8, linestyle='--', alpha=0.5)

    style_dual_ax(ax1, ax2, c1, c2)
    ax1.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.0f}%'))
    ax2.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.0f}%'))
    set_xlim_to_data(ax1, wti_monthly.index)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    add_last_value_label(ax1, wti_monthly, color=c1, fmt='{:.0f}%', side='left')
    add_last_value_label(ax2, imp_xpet_a, color=COLORS['sea'], side='right')
    add_recessions(ax1, start_date='2000-01-01')

    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax1.legend(h1 + h2, l1 + l2, loc='upper left', **legend_style())

    add_annotation_box(ax1,
        "When All imports spike but ex-petro is flat = oil.\n"
        "When ex-petro spikes independently = tariffs.",
        x=0.52, y=0.15)

    brand_fig(fig, 'Separating Oil from Tariffs',
              subtitle='WTI crude vs import prices (all and ex-petroleum)',
              source='BLS, EIA via FRED',
              data_date=imp_yoy_a.index[-1])

    return save_fig(fig, 'chart_28_wti_vs_import_prices.png')


# ============================================
# CHART 29: USD/CNY and USD/MXN (Nearshoring Signal) [Figure 29]
# ============================================
def chart_29():
    """Key bilateral exchange rates: CNY and MXN."""
    print('\nChart 29: USD/CNY and USD/MXN...')

    cny = fetch_fred_level('DEXCHUS', start='2006-01-01')
    mxn = fetch_fred_level('DEXMXUS', start='2006-01-01')

    fig, ax1 = new_fig()
    ax2 = ax1.twinx()
    c1, c2 = THEME['primary'], THEME['secondary']

    ax1.plot(cny.index, cny, color=c1, linewidth=2.5,
             label=f'USD/CNY ({cny.iloc[-1]:.2f})')
    ax2.plot(mxn.index, mxn, color=c2, linewidth=2.5,
             label=f'USD/MXN ({mxn.iloc[-1]:.2f})')

    style_dual_ax(ax1, ax2, c1, c2)
    ax1.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.1f}'))
    ax2.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.0f}'))
    set_xlim_to_data(ax1, cny.index)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    add_last_value_label(ax1, cny, color=c1, fmt='{:.2f}', side='left')
    add_last_value_label(ax2, mxn, color=c2, fmt='{:.1f}', side='right')
    add_recessions(ax1, start_date='2006-01-01')

    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax1.legend(h1 + h2, l1 + l2, loc='upper left', **legend_style())

    add_annotation_box(ax1,
        "Both rising = dollar strength vs trade partners.\n"
        "CNY managed float; MXN = nearshoring signal.",
        x=0.52, y=0.50)

    brand_fig(fig, 'Key Bilateral Rates: CNY & MXN',
              subtitle='The currencies that matter most for U.S. trade',
              source='Federal Reserve via FRED',
              data_date=cny.index[-1])

    return save_fig(fig, 'chart_29_cny_mxn.png')


# ============================================
# CHART 30: Import Price All vs Dollar YoY (Inverse Relationship) [Figure 30]
# ============================================
def chart_30():
    """Import prices vs Dollar (inverted): dollar drives import costs."""
    print('\nChart 30: Import Prices vs Dollar...')

    imp_yoy = fetch_fred_yoy('IR', trim='2000-01-01')
    dollar_yoy = fetch_fred_yoy('DTWEXBGS', trim='2000-01-01')

    idx = imp_yoy.index.intersection(dollar_yoy.index)
    imp_yoy = imp_yoy.loc[idx]
    dollar_yoy = dollar_yoy.loc[idx]

    fig, ax1 = new_fig()
    ax2 = ax1.twinx()
    c1, c2 = THEME['secondary'], THEME['primary']

    ax1.plot(dollar_yoy.index, -dollar_yoy, color=c1, linewidth=2.5,
             label=f'Broad Dollar YoY (INVERTED, {-dollar_yoy.iloc[-1]:.1f}%)')
    ax2.plot(imp_yoy.index, imp_yoy, color=c2, linewidth=2.5,
             label=f'Import Prices All YoY ({imp_yoy.iloc[-1]:.1f}%)')

    ax1.axhline(0, color=COLORS['doldrums'], linewidth=0.8, linestyle='--', alpha=0.5)

    style_dual_ax(ax1, ax2, c1, c2)
    ax1.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.0f}%'))
    ax2.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.0f}%'))
    set_xlim_to_data(ax1, dollar_yoy.index)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    align_yaxis_zero(ax1, ax2)

    add_last_value_label(ax1, -dollar_yoy, color=c1, side='left')
    add_last_value_label(ax2, imp_yoy, color=c2, side='right')
    add_recessions(ax1, start_date='2000-01-01')

    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax1.legend(h1 + h2, l1 + l2, loc='upper left', **legend_style())

    add_annotation_box(ax1,
        "Dollar weakness = import prices rise.\n"
        "When both diverge: tariffs or supply shocks.",
        x=0.52, y=0.15)

    brand_fig(fig, 'Dollar → Import Prices: The Transmission',
              subtitle='Dollar strength (inverted) vs import price inflation',
              source='Federal Reserve, BLS via FRED',
              data_date=imp_yoy.index[-1])

    return save_fig(fig, 'chart_30_dollar_vs_import_prices.png')


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
    14: chart_14,
    15: chart_15,
    16: chart_16,
    17: chart_17,
    18: chart_18,
    19: chart_19,
    20: chart_20,
    21: chart_21,
    22: chart_22,
    23: chart_23,
    24: chart_24,
    25: chart_25,
    26: chart_26,
    27: chart_27,
    28: chart_28,
    29: chart_29,
    30: chart_30,
}


def main():
    parser = argparse.ArgumentParser(description='Generate Trade educational charts')
    parser.add_argument('--chart', type=int, help='Chart number to generate (1-30)')
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
