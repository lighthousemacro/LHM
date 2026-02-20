#!/usr/bin/env python3
"""
Generate Charts for Educational Series: Post 7 - Trade (Pillar 7)
=====================================================================
Generates BOTH white and dark theme versions.
Matches format from Business/Consumer/Housing charts.

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
    box_fc = '#0089D1'
    box_alpha = 1.0
    txt_color = '#ffffff'
    ax.text(x, y, text, transform=ax.transAxes,
            fontsize=10, color=txt_color, ha='center', va='top',
            style='italic',
            bbox=dict(boxstyle='round,pad=0.5',
                      facecolor=box_fc, edgecolor='#33CCFF',
                      linewidth=2.0,
                      alpha=box_alpha))


def brand_fig(fig, title, subtitle=None, source=None, data_date=None):
    """Apply LHM branding at figure level."""
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
        edgecolor='#33CCFF' if THEME['mode'] == 'dark' else THEME['spine'],
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
        x=0.70, y=0.92)

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
        x=0.52, y=0.15)

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
        x=0.52, y=0.15)

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
    ax.legend(loc='upper left', **legend_style())

    add_annotation_box(ax,
        "Exports contracting while imports decelerate.\n"
        "The strong dollar + retaliatory tariffs double hit.",
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
        x=0.30, y=0.92)

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
    imp_xpet = fetch_fred_yoy('IRFPPF', trim='2000-01-01')
    imp_cons = fetch_fred_yoy('IRFPCF', trim='2000-01-01')
    imp_ind = fetch_fred_yoy('IRFPIF', trim='2000-01-01')

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
        x=0.52, y=0.15)

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
        "Below 100 = we pay more for imports than we\n"
        "earn on exports. Tariffs push this lower.",
        x=0.52, y=0.15)

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
        "Currently elevated but below 2019 peaks.",
        x=0.25, y=0.92)

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

    ca_total = fetch_quarterly_level('IEABC', start='1999-01-01')
    ca_goods = fetch_quarterly_level('IEABCG', start='1999-01-01')
    ca_services = fetch_quarterly_level('IEABCS', start='1999-01-01')
    ca_income = fetch_quarterly_level('IEABCPI', start='1999-01-01')

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
    add_recessions(ax, start_date='1999-01-01')
    ax.legend(loc='lower left', **legend_style())

    add_annotation_box(ax,
        "Goods deficit dominates, but services surplus\n"
        "and primary income partially offset.",
        x=0.52, y=0.92)

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
    parser = argparse.ArgumentParser(description='Generate Trade educational charts')
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
