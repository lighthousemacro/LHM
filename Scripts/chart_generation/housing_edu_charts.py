#!/usr/bin/env python3
"""
Generate Charts for Educational Series: Post 5 - Housing (Pillar 4)
====================================================================
Generates BOTH white and dark theme versions.
Comprehensive housing dashboard: 21+ charts covering demand, supply,
prices, affordability, credit, shelter inflation, and construction costs.

Usage:
    python housing_edu_charts.py --chart 1
    python housing_edu_charts.py --chart 1 --theme dark
    python housing_edu_charts.py --all
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
OUTPUT_BASE = f'{BASE_PATH}/Outputs/Educational_Charts/Housing_Post_5'
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


def fetch_quarterly_level(series_id, start='2000-01-01'):
    """Fetch quarterly FRED series as level, forward-fill to monthly."""
    df = fetch_fred(series_id, start=start)
    monthly = df['value'].resample('MS').ffill()
    return monthly.dropna()


def fetch_weekly_to_monthly(series_id, start='2000-01-01'):
    """Fetch weekly FRED series, resample to monthly average."""
    df = fetch_fred(series_id, start=start)
    monthly = df['value'].resample('MS').mean()
    return monthly.dropna()


def rolling_zscore(series, window=60):
    """Compute rolling z-score over a given window (months)."""
    mu = series.rolling(window, min_periods=24).mean()
    sigma = series.rolling(window, min_periods=24).std()
    return (series - mu) / sigma


def fetch_db(series_id, start='2000-01-01'):
    """Fetch a series from the master DB (for Zillow and other non-FRED data)."""
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


def fetch_db_yoy(series_id, start='1999-01-01', trim='2000-01-01'):
    """Fetch DB series, compute YoY%, trim."""
    df = fetch_db(series_id, start=start)
    if df.empty:
        return pd.Series(dtype=float)
    df['yoy'] = df['value'].pct_change(12, fill_method=None) * 100
    if trim:
        df = df.loc[trim:]
    return df['yoy'].dropna()


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


def style_single_ax(ax):
    """Apply full styling to a single-axis chart."""
    style_ax(ax, right_primary=True)
    ax.tick_params(axis='both', which='both', length=0)
    ax.tick_params(axis='y', labelcolor=THEME['fg'], labelsize=10)


def add_annotation_box(ax, text, x=0.52, y=0.92):
    """Add takeaway annotation box in dead space."""
    ax.text(x, y, text, transform=ax.transAxes,
            fontsize=10, color=THEME['fg'], ha='center', va='top',
            style='italic',
            bbox=dict(boxstyle='round,pad=0.5',
                      facecolor=THEME['bg'], edgecolor='#2389BB',
                      alpha=0.9))


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


def add_last_value_label(ax, y_data, color, fmt='{:.1f}', side='right', fontsize=9, pad=0.3):
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


# ============================================
# A. DEMAND CHARTS (1-5)
# ============================================
def chart_01():
    """New Home Sales vs 30Y Mortgage Rate (dual axis, inverted RHS)."""
    print('\nChart 1: New Home Sales vs Mortgage Rate...')

    # NOTE: EXHOSLUSM495S (Existing Home Sales) was restructured on FRED in 2025
    # and only has ~13 months of history. Using HSN1F (New Home Sales) instead
    # which has full history and shows the same rate-sensitivity story.
    sales = fetch_fred_level('HSN1F', start='2018-01-01')
    rate = fetch_weekly_to_monthly('MORTGAGE30US', start='2018-01-01')

    fig, ax1 = new_fig()
    ax2 = ax1.twinx()

    c1, c2 = THEME['primary'], THEME['secondary']
    ax1.plot(sales.index, sales, color=c1, linewidth=2.5,
             label=f'New Home Sales SAAR ({sales.iloc[-1]:,.0f}K)')
    ax2.plot(rate.index, rate, color=c2, linewidth=2.5,
             label=f'30Y Mortgage Rate ({rate.iloc[-1]:.2f}%)')

    # Invert right axis so rising rates go down (visually correlated)
    ax2.invert_yaxis()

    style_dual_ax(ax1, ax2, c1, c2)
    ax1.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:,.0f}K'))
    ax2.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.1f}%'))
    set_xlim_to_data(ax1, sales.index)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    add_last_value_label(ax1, sales, color=c1, fmt='{:,.0f}K', side='left')
    add_last_value_label(ax2, rate, color=c2, fmt='{:.2f}%', side='right')
    add_recessions(ax1, start_date='2018-01-01')
    ax1.legend(loc='upper left', **legend_style())
    ax2.legend(loc='upper right', **legend_style())

    add_annotation_box(ax1, 'Sales cratered as rates doubled.\nBuilders adapted with rate buydowns.', x=0.78, y=0.65)

    brand_fig(fig, 'New Home Sales vs. 30-Year Mortgage Rate',
              subtitle='Inverted Rate Axis | 2018-Present',
              source='Census Bureau, Freddie Mac via FRED')
    save_fig(fig, 'chart_01_sales_vs_rate.png')


def chart_02():
    """Regional Home Prices YoY% via Case-Shiller city indices."""
    print('\nChart 2: Regional Home Prices YoY% (Case-Shiller)...')

    # NOTE: NAR regional median price series (HOSMEDUS*) were restructured on FRED
    # in 2025 and only have ~13 months of history. Using Case-Shiller city indices
    # as regional proxies instead (full history).
    regions = {
        'New York': ('NYXRSA', THEME['primary']),
        'Chicago': ('CHXRSA', THEME['quaternary']),
        'Atlanta': ('ATXRSA', THEME['secondary']),
        'San Francisco': ('SFXRSA', THEME['tertiary']),
    }

    fig, ax = new_fig()

    for name, (sid, color) in regions.items():
        try:
            data = fetch_fred_yoy(sid, start='2018-01-01', trim='2019-01-01')
            if len(data) > 0:
                ax.plot(data.index, data, color=color, linewidth=2.0,
                        label=f'{name} ({data.iloc[-1]:.1f}%)')
        except Exception as e:
            print(f'  Warning: Could not fetch {sid}: {e}')

    ax.axhline(0, color=COLORS['doldrums'], linewidth=0.8, alpha=0.5, linestyle='--')

    style_single_ax(ax)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.0f}%'))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    add_recessions(ax, start_date='2019-01-01')
    ax.legend(loc='upper left', **legend_style())

    add_annotation_box(ax, 'Sun Belt cooled sharply. Northeast resilient.', x=0.72, y=0.85)

    brand_fig(fig, 'Regional Home Prices: Case-Shiller City Indices',
              subtitle='Year-over-Year % Change',
              source='S&P CoreLogic Case-Shiller via FRED')
    save_fig(fig, 'chart_02_regional_prices_yoy.png')


def chart_03():
    """New Home Sales (SAAR) long history — builder market share proxy."""
    print('\nChart 3: New Home Sales Level (Builder Market Share)...')

    # NOTE: EXHOSLUSM495S (existing home sales) only has 13 months on FRED
    # after NAR restructured. Can't compute new/total ratio with long history.
    # Showing new home sales level instead — the recovery from 2022 lows
    # while existing sales remain frozen tells the builder market share story.
    new = fetch_fred_level('HSN1F', start='2005-01-01')

    fig, ax = new_fig()

    ax.fill_between(new.index, 0, new, color=THEME['primary'], alpha=THEME['fill_alpha'])
    ax.plot(new.index, new, color=THEME['primary'], linewidth=2.5,
            label=f'New Home Sales SAAR ({new.iloc[-1]:,.0f}K)')

    # Pre-pandemic average
    hist_avg = new.loc['2015-01-01':'2019-12-31'].mean()
    ax.axhline(hist_avg, color=COLORS['doldrums'], linewidth=1.0, linestyle='--',
               label=f'2015-2019 Average ({hist_avg:,.0f}K)')

    style_single_ax(ax)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:,.0f}K'))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    set_xlim_to_data(ax, new.index)
    add_recessions(ax, start_date='2005-01-01')
    add_last_value_label(ax, new, color=THEME['primary'], fmt='{:,.0f}K')
    ax.legend(loc='upper left', **legend_style())

    add_annotation_box(ax, 'Builders recovered via rate buydowns\nwhile resale market stays frozen.', x=0.45, y=0.93)

    brand_fig(fig, 'New Home Sales: Builders Filling the Void',
              subtitle='Seasonally Adjusted Annual Rate (Thousands) | 2005-Present',
              source='Census Bureau via FRED')
    save_fig(fig, 'chart_03_new_pct_of_total.png')


def chart_04():
    """Mortgage Rate vs Mortgage Debt Service as % of DPI (dual axis)."""
    print('\nChart 4: Mortgage Rate vs Debt Service Burden...')

    # NOTE: FIXHAI (NAR Affordability Index) was restructured on FRED in 2025
    # and only has ~13 months of history. Using MDSP (Mortgage Debt Service
    # Payments as % of Disposable Income) instead — quarterly, back to 2005.
    rate = fetch_weekly_to_monthly('MORTGAGE30US', start='2005-01-01')
    mdsp = fetch_fred_level('MDSP', start='2005-01-01')

    fig, ax1 = new_fig()
    ax2 = ax1.twinx()

    c1, c2 = THEME['primary'], THEME['secondary']
    ax1.plot(mdsp.index, mdsp, color=c1, linewidth=2.5,
             label=f'Mortgage Debt Service / DPI ({mdsp.iloc[-1]:.1f}%)')
    ax2.plot(rate.index, rate, color=c2, linewidth=2.5,
             label=f'30Y Mortgage Rate ({rate.iloc[-1]:.1f}%)')

    style_dual_ax(ax1, ax2, c1, c2)
    ax1.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.1f}%'))
    ax2.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.1f}%'))
    set_xlim_to_data(ax1, rate.index)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    add_last_value_label(ax1, mdsp, color=c1, fmt='{:.1f}%', side='left')
    add_last_value_label(ax2, rate, color=c2, fmt='{:.1f}%', side='right')
    add_recessions(ax1, start_date='2005-01-01')
    ax1.legend(loc='upper left', **legend_style())
    ax2.legend(loc='upper right', **legend_style())

    add_annotation_box(ax1, 'Rates doubled but debt service stayed\nbelow 2007 peak. Lock-in effect at work.', x=0.55, y=0.80)

    brand_fig(fig, 'Mortgage Rate vs. Debt Service Burden',
              subtitle='Mortgage Payments as % of Disposable Income | 2005-Present',
              source='Freddie Mac, Federal Reserve via FRED')
    save_fig(fig, 'chart_04_rate_vs_affordability.png')


def chart_05():
    """Monthly Payment Comparison bar chart (static)."""
    print('\nChart 5: Monthly Payment Comparison...')

    # Median home price ~$397K, 20% down = $317,600 loan
    loan = 317600
    rates = [3.0, 4.5, 5.5, 6.1, 7.0]
    labels = ['3.0%\n(Pre-pandemic)', '4.5%\n(Thaw target)', '5.5%\n(Unlock level)',
              '6.1%\n(Current)', '7.0%\n(2023 peak)']

    payments = []
    for r in rates:
        monthly_r = r / 100 / 12
        n = 360
        pmt = loan * (monthly_r * (1 + monthly_r)**n) / ((1 + monthly_r)**n - 1)
        payments.append(pmt)

    fig, ax = new_fig()

    bar_colors = [THEME['quaternary'], THEME['tertiary'], THEME['primary'],
                  THEME['secondary'], THEME['accent']]
    bars = ax.bar(range(len(rates)), payments, color=bar_colors, width=0.6, edgecolor='none')

    # Add value labels on bars
    for bar_obj, pmt in zip(bars, payments):
        ax.text(bar_obj.get_x() + bar_obj.get_width()/2, bar_obj.get_height() + 30,
                f'${pmt:,.0f}', ha='center', va='bottom', fontsize=12,
                fontweight='bold', color=THEME['fg'])

    ax.set_xticks(range(len(rates)))
    ax.set_xticklabels(labels, fontsize=10, color=THEME['fg'])

    style_ax(ax, right_primary=True)
    ax.tick_params(axis='both', which='both', length=0)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'${x:,.0f}'))
    ax.set_ylim(0, max(payments) * 1.15)

    add_annotation_box(ax, f'44% payment increase from 3% to 6.1%.\n$317,600 loan (median home, 20% down).', x=0.3, y=0.88)

    brand_fig(fig, 'Monthly Mortgage Payment by Rate',
              subtitle='Median Home ($397K) | 20% Down | 30-Year Fixed',
              source='Lighthouse Macro calculations')
    save_fig(fig, 'chart_05_payment_comparison.png')


# ============================================
# B. SUPPLY CHARTS (6-9)
# ============================================
def chart_06():
    """Housing Starts: Total, Single-Family, Multi-Family."""
    print('\nChart 6: Housing Starts (Total, SF, MF)...')

    total = fetch_fred_level('HOUST', start='2015-01-01')
    sf = fetch_fred_level('HOUST1F', start='2015-01-01')

    # MF derived
    combined = pd.DataFrame({'total': total, 'sf': sf}).dropna()
    mf = combined['total'] - combined['sf']

    fig, ax = new_fig()

    ax.plot(combined.index, combined['total'], color=THEME['tertiary'], linewidth=1.5,
            label=f'Total ({combined["total"].iloc[-1]:.0f}K)', linestyle='--')
    ax.plot(combined.index, combined['sf'], color=THEME['primary'], linewidth=2.5,
            label=f'Single-Family ({combined["sf"].iloc[-1]:.0f}K)')
    ax.plot(mf.index, mf, color=THEME['secondary'], linewidth=2.5,
            label=f'Multi-Family ({mf.iloc[-1]:.0f}K)')

    style_single_ax(ax)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:,.0f}K'))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    set_xlim_to_data(ax, combined.index)
    add_recessions(ax, start_date='2015-01-01')
    ax.legend(loc='upper left', **legend_style())

    add_annotation_box(ax, 'SF drives the cycle.\nMF a fraction of total.', x=0.87, y=0.93)

    brand_fig(fig, 'Housing Starts: Single-Family vs. Multi-Family',
              subtitle='Thousands of Units, SAAR',
              source='Census via FRED')
    save_fig(fig, 'chart_06_housing_starts.png')


def chart_07():
    """Regional Housing Starts."""
    print('\nChart 7: Regional Housing Starts...')

    regions = {
        'South': ('HOUSTS', THEME['primary']),
        'West': ('HOUSTW', THEME['secondary']),
        'Midwest': ('HOUSTMW', THEME['quaternary']),
        'Northeast': ('HOUSTNE', THEME['tertiary']),
    }

    fig, ax = new_fig()

    for name, (sid, color) in regions.items():
        data = fetch_fred_level(sid, start='2015-01-01')
        ax.plot(data.index, data, color=color, linewidth=2.0,
                label=f'{name} ({data.iloc[-1]:.0f}K)')

    style_single_ax(ax)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:,.0f}K'))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    add_recessions(ax, start_date='2015-01-01')
    ax.legend(loc='upper left', **legend_style())

    add_annotation_box(ax, 'South = 50%+ of all construction.\nRegional divergence matters.', x=0.7, y=0.55)

    brand_fig(fig, 'Housing Starts by Region',
              subtitle='Thousands of Units, SAAR',
              source='Census via FRED')
    save_fig(fig, 'chart_07_regional_starts.png')


def chart_08():
    """Building Permits vs Housing Starts (pipeline signal)."""
    print('\nChart 8: Permits vs Starts...')

    permits = fetch_fred_level('PERMIT', start='2015-01-01')
    starts = fetch_fred_level('HOUST', start='2015-01-01')

    fig, ax = new_fig()

    ax.plot(permits.index, permits, color=THEME['primary'], linewidth=2.5,
            label=f'Permits ({permits.iloc[-1]:.0f}K)')
    ax.plot(starts.index, starts, color=THEME['secondary'], linewidth=2.5,
            label=f'Starts ({starts.iloc[-1]:.0f}K)')

    combined = pd.DataFrame({'permits': permits, 'starts': starts}).dropna()

    style_single_ax(ax)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:,.0f}K'))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    set_xlim_to_data(ax, combined.index)
    add_recessions(ax, start_date='2015-01-01')
    add_last_value_label(ax, permits, color=THEME['primary'], fmt='{:,.0f}K')
    add_last_value_label(ax, starts, color=THEME['secondary'], fmt='{:,.0f}K')
    ax.legend(loc='upper left', **legend_style())
    add_annotation_box(ax, "Permits lead starts by 1-2 months.\nGap = future supply pipeline.", x=0.85, y=0.90)

    brand_fig(fig, 'Building Permits vs. Housing Starts',
              subtitle='The Construction Pipeline',
              source='Census via FRED')
    save_fig(fig, 'chart_08_permits_vs_starts.png')


def chart_09():
    """Units Under Construction vs Completions."""
    print('\nChart 9: Under Construction vs Completions...')

    under = fetch_fred_level('UNDCONTSA', start='2015-01-01')
    comp = fetch_fred_level('COMPUTSA', start='2015-01-01')

    fig, ax = new_fig()

    ax.plot(under.index, under, color=THEME['primary'], linewidth=2.5,
            label=f'Under Construction ({under.iloc[-1]:.0f}K)')
    ax.plot(comp.index, comp, color=THEME['secondary'], linewidth=2.5,
            label=f'Completions ({comp.iloc[-1]:.0f}K)')

    style_single_ax(ax)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:,.0f}K'))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    set_xlim_to_data(ax, under.index)
    add_recessions(ax, start_date='2015-01-01')
    add_last_value_label(ax, under, color=THEME['primary'], fmt='{:,.0f}K')
    add_last_value_label(ax, comp, color=THEME['secondary'], fmt='{:,.0f}K')
    ax.legend(loc='upper left', **legend_style())

    add_annotation_box(ax, 'Under construction peaked mid-2023.\nCompletions catching up.', x=0.8, y=0.40)

    brand_fig(fig, 'Housing Units Under Construction vs. Completions',
              subtitle='Thousands of Units, SAAR',
              source='Census via FRED')
    save_fig(fig, 'chart_09_under_construction_vs_completions.png')


# ============================================
# C. PRICES (10-12)
# ============================================
def chart_10():
    """Case-Shiller National vs 20-City YoY%."""
    print('\nChart 10: Case-Shiller National vs 20-City YoY%...')

    national = fetch_fred_yoy('CSUSHPINSA', start='2014-01-01', trim='2015-01-01')
    city20 = fetch_fred_yoy('SPCS20RSA', start='2014-01-01', trim='2015-01-01')

    fig, ax = new_fig()

    ax.plot(national.index, national, color=THEME['primary'], linewidth=2.5,
            label=f'National ({national.iloc[-1]:.1f}%)')
    ax.plot(city20.index, city20, color=THEME['secondary'], linewidth=2.5,
            label=f'20-City Composite ({city20.iloc[-1]:.1f}%)')

    ax.axhline(0, color=COLORS['doldrums'], linewidth=0.8, alpha=0.5, linestyle='--')

    style_single_ax(ax)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.0f}%'))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    set_xlim_to_data(ax, national.index)
    add_recessions(ax, start_date='2015-01-01')
    add_last_value_label(ax, national, color=THEME['primary'], fmt='{:.1f}%')
    add_last_value_label(ax, city20, color=THEME['secondary'], fmt='{:.1f}%')
    ax.legend(loc='upper left', **legend_style())
    add_annotation_box(ax, 'Low single-digit appreciation.\nTight supply supporting prices.', x=0.78, y=0.88)

    brand_fig(fig, 'Case-Shiller Home Price Index',
              subtitle='National vs. 20-City Composite | Year-over-Year %',
              source='S&P/Cotality via FRED')
    save_fig(fig, 'chart_10_case_shiller_yoy.png')


def chart_11():
    """Case-Shiller vs FHFA HPI YoY%."""
    print('\nChart 11: Case-Shiller vs FHFA HPI YoY%...')

    cs = fetch_fred_yoy('CSUSHPINSA', start='2004-01-01', trim='2005-01-01')

    # FHFA is quarterly, need to compute YoY on quarterly then ffill
    fhfa_raw = fetch_fred('USSTHPI', start='2004-01-01')
    fhfa_raw['yoy'] = fhfa_raw['value'].pct_change(4, fill_method=None) * 100
    fhfa = fhfa_raw['yoy'].resample('MS').ffill().dropna()
    fhfa = fhfa.loc['2005-01-01':]

    fig, ax = new_fig()

    ax.plot(cs.index, cs, color=THEME['primary'], linewidth=2.5,
            label=f'Case-Shiller National ({cs.iloc[-1]:.1f}%)')
    ax.plot(fhfa.index, fhfa, color=THEME['secondary'], linewidth=2.5,
            label=f'FHFA HPI ({fhfa.iloc[-1]:.1f}%)')

    ax.axhline(0, color=COLORS['doldrums'], linewidth=0.8, alpha=0.5, linestyle='--')

    style_single_ax(ax)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.0f}%'))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    set_xlim_to_data(ax, cs.index)
    add_recessions(ax, start_date='2005-01-01')
    ax.legend(loc='upper left', **legend_style())

    add_annotation_box(ax, 'FHFA broader coverage (conforming loans).\nCase-Shiller: repeat-sales methodology.', x=0.3, y=0.15)

    brand_fig(fig, 'Case-Shiller vs. FHFA House Price Index',
              subtitle='Year-over-Year % Change | Two Measurement Approaches',
              source='S&P/Cotality, FHFA via FRED')
    save_fig(fig, 'chart_11_cs_vs_fhfa.png')


def chart_12():
    """Real vs Nominal HPI YoY%."""
    print('\nChart 12: Real vs Nominal HPI YoY%...')

    cs = fetch_fred_yoy('CSUSHPINSA', start='2004-01-01', trim='2005-01-01')
    cpi = fetch_fred_yoy('CPIAUCSL', start='2004-01-01', trim='2005-01-01')

    combined = pd.DataFrame({'nominal': cs, 'cpi': cpi}).dropna()
    combined['real'] = combined['nominal'] - combined['cpi']

    fig, ax = new_fig()

    ax.plot(combined.index, combined['nominal'], color=THEME['primary'], linewidth=2.5,
            label=f'Nominal HPI YoY ({combined["nominal"].iloc[-1]:.1f}%)')
    ax.plot(combined.index, combined['real'], color=THEME['secondary'], linewidth=2.5,
            label=f'Real HPI YoY ({combined["real"].iloc[-1]:.1f}%)')

    ax.axhline(0, color=COLORS['doldrums'], linewidth=0.8, alpha=0.5, linestyle='--')

    # Shade periods of negative real appreciation
    ax.fill_between(combined.index, 0, combined['real'],
                    where=(combined['real'] < 0),
                    color=THEME['secondary'], alpha=0.15, label='Real depreciation')

    style_single_ax(ax)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.0f}%'))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    set_xlim_to_data(ax, combined.index)
    add_recessions(ax, start_date='2005-01-01')
    add_last_value_label(ax, combined['nominal'], color=THEME['primary'], fmt='{:.1f}%')
    add_last_value_label(ax, combined['real'], color=THEME['secondary'], fmt='{:.1f}%')
    ax.legend(loc='upper left', **legend_style())

    add_annotation_box(ax, 'Real flat-to-negative = affordability\nimproving without a crash.', x=0.7, y=0.15)

    brand_fig(fig, 'Nominal vs. Real Home Price Appreciation',
              subtitle='Case-Shiller YoY% Minus CPI YoY%',
              source='S&P/Cotality, BLS via FRED')
    save_fig(fig, 'chart_12_real_vs_nominal_hpi.png')


# ============================================
# D. AFFORDABILITY (13-14)
# ============================================
def chart_13():
    """Mortgage Rate + 10Y Treasury + Spread."""
    print('\nChart 13: Mortgage Rate, 10Y, and Spread...')

    mort = fetch_weekly_to_monthly('MORTGAGE30US', start='2015-01-01')
    tsy = fetch_fred('DGS10', start='2015-01-01')
    # DGS10 is daily, resample to monthly
    tsy_m = tsy['value'].resample('MS').mean().dropna()

    combined = pd.DataFrame({'mortgage': mort, 'treasury': tsy_m}).dropna()
    combined['spread'] = combined['mortgage'] - combined['treasury']

    fig, ax1 = new_fig()
    ax2 = ax1.twinx()

    c1, c2, c3 = THEME['primary'], THEME['tertiary'], THEME['secondary']
    ax1.plot(combined.index, combined['mortgage'], color=c1, linewidth=2.5,
             label=f'30Y Mortgage ({combined["mortgage"].iloc[-1]:.2f}%)')
    ax1.plot(combined.index, combined['treasury'], color=c2, linewidth=2.0,
             label=f'10Y Treasury ({combined["treasury"].iloc[-1]:.2f}%)')
    ax2.plot(combined.index, combined['spread'], color=c3, linewidth=2.0, linestyle='--',
             label=f'Spread ({combined["spread"].iloc[-1]:.0f} bps)')

    # Convert spread axis to bps
    ax2.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x*100:.0f}'))

    # Historical average spread ~170 bps
    ax2.axhline(1.70, color=COLORS['doldrums'], linewidth=1.0, linestyle=':',
                alpha=0.7)

    style_dual_ax(ax1, ax2, c1, c3)
    ax1.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.1f}%'))
    set_xlim_to_data(ax1, combined.index)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    add_last_value_label(ax1, combined['mortgage'], color=c1, fmt='{:.2f}%', side='left')
    add_last_value_label(ax2, combined['spread'] * 100, color=c3, fmt='{:.0f}bps', side='right')
    add_recessions(ax1, start_date='2015-01-01')
    ax1.legend(loc='upper left', **legend_style())
    ax2.legend(loc='lower right', **legend_style())

    brand_fig(fig, 'Mortgage Rate, 10-Year Treasury, and Spread',
              subtitle='Spread Wider Than Normal = MBS Market Impaired',
              source='Freddie Mac, Treasury via FRED')
    save_fig(fig, 'chart_13_rate_treasury_spread.png')


def chart_14():
    """New Home Sales and Months' Supply (dual axis)."""
    print('\nChart 14: New Home Sales and Months Supply...')

    sales = fetch_fred_level('HSN1F', start='2010-01-01')
    supply = fetch_fred_level('MSACSR', start='2010-01-01')

    fig, ax1 = new_fig()
    ax2 = ax1.twinx()

    c1, c2 = THEME['primary'], THEME['secondary']
    ax1.plot(sales.index, sales, color=c1, linewidth=2.5,
             label=f'New Home Sales ({sales.iloc[-1]:.0f}K)')
    ax2.plot(supply.index, supply, color=c2, linewidth=2.5,
             label=f'Months Supply ({supply.iloc[-1]:.1f})')

    # Balanced supply range
    ax2.axhspan(5.0, 7.0, alpha=0.08, color=COLORS['sea'], label='Balanced range (5-7 mo)')

    style_dual_ax(ax1, ax2, c1, c2)
    ax1.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:,.0f}K'))
    ax2.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.1f}'))
    set_xlim_to_data(ax1, sales.index)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    add_last_value_label(ax1, sales, color=c1, fmt='{:.0f}K', side='left')
    add_last_value_label(ax2, supply, color=c2, fmt='{:.1f} mo', side='right')
    add_recessions(ax1, start_date='2010-01-01')
    ax1.legend(loc='upper left', **legend_style())
    ax2.legend(loc='upper right', **legend_style())

    brand_fig(fig, 'New Home Sales and Months\' Supply',
              subtitle='Sales SAAR vs. Inventory-to-Sales Ratio',
              source='Census via FRED')
    save_fig(fig, 'chart_14_new_sales_months_supply.png')


# ============================================
# E. CREDIT (15-17)
# ============================================
def chart_15():
    """Mortgage Delinquency Rate 30+ Days (long history)."""
    print('\nChart 15: Mortgage Delinquency Rate...')

    dq = fetch_quarterly_level('DRSFRMACBS', start='2003-01-01')

    fig, ax = new_fig()

    ax.plot(dq.index, dq, color=THEME['secondary'], linewidth=2.5,
            label=f'30+ Day Delinquency ({dq.iloc[-1]:.2f}%)')
    ax.fill_between(dq.index, 0, dq, color=THEME['secondary'], alpha=THEME['fill_alpha'])

    # Stress thresholds
    ax.axhline(3.5, color=COLORS['venus'], linewidth=1.0, linestyle='--',
               alpha=0.7, label='Stressed threshold (3.5%)')

    style_single_ax(ax)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.1f}%'))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    set_xlim_to_data(ax, dq.index)
    add_recessions(ax, start_date='2003-01-01')
    add_last_value_label(ax, dq, color=THEME['secondary'], fmt='{:.2f}%')
    ax.legend(loc='upper right', **legend_style())

    add_annotation_box(ax, 'Not 2008. Credit channel is not engaged.\nBorrower profiles historically strong.', x=0.65, y=0.75)

    brand_fig(fig, 'Mortgage Delinquency Rate (30+ Days)',
              subtitle='Single-Family Residential | All Commercial Banks',
              source='Federal Reserve via FRED')
    save_fig(fig, 'chart_15_mortgage_delinquency.png')


def chart_16():
    """Homeowner vs Rental Vacancy Rate."""
    print('\nChart 16: Homeowner vs Rental Vacancy Rate...')

    ho_vac = fetch_quarterly_level('RHVRUSQ156N', start='2000-01-01')
    rent_vac = fetch_quarterly_level('RRVRUSQ156N', start='2000-01-01')

    fig, ax1 = new_fig()
    ax2 = ax1.twinx()

    c1, c2 = THEME['primary'], THEME['secondary']
    ax1.plot(ho_vac.index, ho_vac, color=c1, linewidth=2.5,
             label=f'Homeowner Vacancy ({ho_vac.iloc[-1]:.1f}%)')
    ax2.plot(rent_vac.index, rent_vac, color=c2, linewidth=2.5,
             label=f'Rental Vacancy ({rent_vac.iloc[-1]:.1f}%)')

    style_dual_ax(ax1, ax2, c1, c2)
    ax1.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.1f}%'))
    ax2.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.1f}%'))
    set_xlim_to_data(ax1, ho_vac.index)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    add_last_value_label(ax1, ho_vac, color=c1, fmt='{:.1f}%', side='left')
    add_last_value_label(ax2, rent_vac, color=c2, fmt='{:.1f}%', side='right')
    add_recessions(ax1)
    ax1.legend(loc='upper left', **legend_style())
    ax2.legend(loc='upper right', **legend_style())

    brand_fig(fig, 'Homeowner vs. Rental Vacancy Rate',
              subtitle='Ownership Market Tight | Rental Market Loosening',
              source='Census via FRED')
    save_fig(fig, 'chart_16_vacancy_rates.png')


def chart_17():
    """Homeownership Rate."""
    print('\nChart 17: Homeownership Rate...')

    rate = fetch_quarterly_level('RHORUSQ156N', start='1995-01-01')

    fig, ax = new_fig()

    ax.plot(rate.index, rate, color=THEME['primary'], linewidth=2.5,
            label=f'Homeownership Rate ({rate.iloc[-1]:.1f}%)')
    ax.fill_between(rate.index, rate.min() - 1, rate, color=THEME['primary'],
                    alpha=THEME['fill_alpha'])

    # Long-run average
    avg = rate.mean()
    ax.axhline(avg, color=COLORS['doldrums'], linewidth=1.0, linestyle='--',
               label=f'Long-run Average ({avg:.1f}%)')

    style_single_ax(ax)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.1f}%'))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    set_xlim_to_data(ax, rate.index)
    add_recessions(ax)
    add_last_value_label(ax, rate, color=THEME['primary'], fmt='{:.1f}%')
    ax.legend(loc='lower left', **legend_style())

    brand_fig(fig, 'U.S. Homeownership Rate',
              subtitle='Quarterly | Census Housing Vacancy Survey',
              source='Census via FRED')
    save_fig(fig, 'chart_17_homeownership_rate.png')


# ============================================
# F. SHELTER INFLATION (18-19)
# ============================================
def chart_18():
    """CPI Shelter YoY% vs CPI Rent vs OER."""
    print('\nChart 18: CPI Shelter Components YoY%...')

    shelter = fetch_fred_yoy('CUSR0000SAH1', start='2014-01-01', trim='2015-01-01')
    rent = fetch_fred_yoy('CUSR0000SEHA', start='2014-01-01', trim='2015-01-01')
    oer = fetch_fred_yoy('CUSR0000SEHC', start='2014-01-01', trim='2015-01-01')

    fig, ax = new_fig()

    ax.plot(shelter.index, shelter, color=THEME['primary'], linewidth=2.5,
            label=f'Shelter ({shelter.iloc[-1]:.1f}%)')
    ax.plot(rent.index, rent, color=THEME['secondary'], linewidth=2.0,
            label=f'Rent of Primary Residence ({rent.iloc[-1]:.1f}%)')
    ax.plot(oer.index, oer, color=THEME['tertiary'], linewidth=2.0,
            label=f'Owners\' Equivalent Rent ({oer.iloc[-1]:.1f}%)')

    # Fed 2% proxy for shelter
    ax.axhline(2.0, color=COLORS['venus'], linewidth=1.0, linestyle='-',
               alpha=0.7, label='2% Target Proxy')

    ax.axhline(0, color=COLORS['doldrums'], linewidth=0.8, alpha=0.5, linestyle='--')

    style_single_ax(ax)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.0f}%'))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    set_xlim_to_data(ax, shelter.index)
    add_recessions(ax, start_date='2015-01-01')
    add_last_value_label(ax, shelter, color=THEME['primary'], fmt='{:.1f}%')
    ax.legend(loc='upper left', **legend_style())

    add_annotation_box(ax, 'Shelter = 34% of CPI, 18% of Core PCE.\nMarket rents lead by 12-18 months.', x=0.5, y=0.45)

    brand_fig(fig, 'CPI Shelter Inflation Components',
              subtitle='Year-over-Year % | Shelter, Rent, and OER',
              source='BLS via FRED')
    save_fig(fig, 'chart_18_shelter_inflation.png')


def chart_19():
    """Median Home Price: National and New."""
    print('\nChart 19: Median Home Prices...')

    existing = fetch_fred_level('HOSMEDUSM052N', start='2010-01-01')
    new_price = fetch_fred_level('MSPNHSUS', start='2010-01-01')

    fig, ax = new_fig()

    ax.plot(existing.index, existing / 1000, color=THEME['primary'], linewidth=2.5,
            label=f'Existing Home ({existing.iloc[-1]/1000:.0f}K)')
    ax.plot(new_price.index, new_price / 1000, color=THEME['secondary'], linewidth=2.5,
            label=f'New Home ({new_price.iloc[-1]/1000:.0f}K)')

    style_single_ax(ax)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'${x:,.0f}K'))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    set_xlim_to_data(ax, existing.index)
    add_recessions(ax, start_date='2010-01-01')
    add_last_value_label(ax, existing / 1000, color=THEME['primary'], fmt='${:.0f}K')
    add_last_value_label(ax, new_price / 1000, color=THEME['secondary'], fmt='${:.0f}K')
    ax.legend(loc='upper left', **legend_style())

    add_annotation_box(ax, 'New home premium narrowing.\nBuilders cutting to sustain volume.', x=0.35, y=0.55)

    brand_fig(fig, 'Median Home Prices: Existing vs. New',
              subtitle='National | Dollars',
              source='NAR, Census via FRED')
    save_fig(fig, 'chart_19_median_prices.png')


# ============================================
# G. CONSTRUCTION COSTS (20)
# ============================================
def chart_20():
    """Tariff Cost Impact bar chart (static data)."""
    print('\nChart 20: Tariff Cost Impact...')

    materials = ['Lumber', 'Steel', 'Fixtures & Cabinets',
                 'Copper', 'Aluminum', 'Appliances']
    costs = [6500, 4000, 3000, 2250, 1500, 1250]
    total = sum(costs)

    fig, ax = new_fig()
    fig.subplots_adjust(left=0.17)

    # Horizontal bar chart, sorted by cost
    y_pos = range(len(materials))
    bars = ax.barh(y_pos, costs, color=THEME['primary'], height=0.6, edgecolor='none')

    # Add total bar
    ax.barh(len(materials), total, color=COLORS['venus'], height=0.6, edgecolor='none')

    # Labels
    all_labels = materials + ['TOTAL']
    ax.set_yticks(range(len(all_labels)))
    ax.set_yticklabels(all_labels, fontsize=11, color=THEME['fg'])

    # Value labels
    for i, (cost, label) in enumerate(zip(costs + [total], all_labels)):
        ax.text(cost + 200, i, f'${cost:,}', va='center', fontsize=11,
                fontweight='bold', color=THEME['fg'])

    style_ax(ax, right_primary=False)
    ax.tick_params(axis='both', which='both', length=0)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, p: f'${x:,.0f}'))
    ax.invert_yaxis()
    ax.set_xlim(0, total * 1.25)

    add_annotation_box(ax, f'Total: ~${total:,} per unit\n~4-5% of median new home price.', x=0.75, y=0.85)

    brand_fig(fig, 'Estimated Tariff Impact on New Home Construction',
              subtitle='Cost Per Unit by Material Category',
              source='NAHB estimates')
    save_fig(fig, 'chart_20_tariff_impact.png')


# ============================================
# H. COMPOSITE (21)
# ============================================
def chart_21():
    """Housing Composite Index with regime bands (simplified HCI)."""
    print('\nChart 21: Housing Composite Index...')

    # Components (all z-scored)
    sales = fetch_fred_yoy('EXHOSLUSM495S', start='2003-01-01', trim='2005-01-01')
    starts = fetch_fred_yoy('HOUST', start='2003-01-01', trim='2005-01-01')
    prices = fetch_fred_yoy('CSUSHPINSA', start='2003-01-01', trim='2005-01-01')
    mort = fetch_weekly_to_monthly('MORTGAGE30US', start='2003-01-01')
    dq = fetch_quarterly_level('DRSFRMACBS', start='2003-01-01')

    # Compute rolling z-scores
    z_sales = rolling_zscore(sales)
    z_starts = rolling_zscore(starts)
    z_prices = rolling_zscore(prices)
    # Invert mortgage rate (higher = worse)
    z_mort = -rolling_zscore(mort.loc['2005-01-01':])
    # Invert delinquency (higher = worse)
    z_dq = -rolling_zscore(dq.loc['2005-01-01':])

    # Combine (equal weight simplified)
    hci = pd.DataFrame({
        'sales': z_sales, 'starts': z_starts, 'prices': z_prices,
        'mort': z_mort, 'dq': z_dq
    }).mean(axis=1).dropna()

    fig, ax = new_fig()

    # Regime bands
    ax.axhspan(1.0, 2.5, alpha=0.08, color=COLORS['starboard'])  # Boom
    ax.axhspan(0.5, 1.0, alpha=0.05, color=COLORS['sea'])  # Expansion
    ax.axhspan(-0.5, 0.5, alpha=0.05, color=COLORS['doldrums'])  # Neutral
    ax.axhspan(-1.0, -0.5, alpha=0.05, color=COLORS['dusk'])  # Contraction
    ax.axhspan(-2.5, -1.0, alpha=0.08, color=COLORS['port'])  # Crisis

    # Regime labels
    ax.text(0.02, 0.95, 'BOOM', transform=ax.transAxes, fontsize=8,
            color=COLORS['starboard'], alpha=0.6, va='top')
    ax.text(0.02, 0.72, 'EXPANSION', transform=ax.transAxes, fontsize=8,
            color=COLORS['sea'], alpha=0.6, va='top')
    ax.text(0.02, 0.50, 'NEUTRAL', transform=ax.transAxes, fontsize=8,
            color=COLORS['doldrums'], alpha=0.6, va='center')
    ax.text(0.02, 0.28, 'CONTRACTION', transform=ax.transAxes, fontsize=8,
            color=COLORS['dusk'], alpha=0.6, va='bottom')
    ax.text(0.02, 0.05, 'CRISIS', transform=ax.transAxes, fontsize=8,
            color=COLORS['port'], alpha=0.6, va='bottom')

    ax.plot(hci.index, hci, color=THEME['primary'], linewidth=2.5,
            label=f'HCI Simplified ({hci.iloc[-1]:.2f})')
    ax.axhline(0, color=COLORS['doldrums'], linewidth=0.8, alpha=0.5, linestyle='--')

    style_single_ax(ax)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.1f}'))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    set_xlim_to_data(ax, hci.index)
    add_recessions(ax, start_date='2005-01-01')
    add_last_value_label(ax, hci, color=THEME['primary'], fmt='{:.2f}')
    ax.legend(loc='lower left', **legend_style())

    brand_fig(fig, 'Housing Composite Index (Simplified HCI)',
              subtitle='Equal-Weighted Z-Score Composite | Regime Bands',
              source='Lighthouse Macro calculations')
    save_fig(fig, 'chart_21_housing_composite.png')


# ============================================
# I. ZILLOW DATA (Charts 22-24)
# ============================================
def chart_22():
    """Zillow ZORI YoY% vs CPI Shelter YoY% (leading indicator relationship)."""
    print('\nChart 22: Zillow ZORI vs CPI Shelter (Lead/Lag)...')

    # ZORI from DB
    zori_yoy = fetch_db_yoy('ZILLOW_ZORI_NATIONAL', start='2014-01-01', trim='2016-01-01')

    # CPI Shelter YoY from FRED
    shelter_yoy = fetch_fred_yoy('CUSR0000SAH1', start='2014-01-01', trim='2016-01-01')

    fig, ax = new_fig()
    ax2 = ax.twinx()

    ax2.plot(zori_yoy.index, zori_yoy, color=THEME['primary'], linewidth=2.5,
             label=f'Zillow ZORI YoY% ({zori_yoy.iloc[-1]:.1f}%)')
    ax.plot(shelter_yoy.index, shelter_yoy, color=THEME['secondary'], linewidth=2.5,
            label=f'CPI Shelter YoY% ({shelter_yoy.iloc[-1]:.1f}%)')

    c1, c2 = THEME['secondary'], THEME['primary']
    style_dual_ax(ax, ax2, c1, c2)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.1f}%'))
    ax2.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.1f}%'))
    common_start = max(zori_yoy.index.min(), shelter_yoy.index.min())
    common_end = max(zori_yoy.index.max(), shelter_yoy.index.max())
    set_xlim_to_data(ax, pd.date_range(common_start, common_end))
    align_yaxis_zero(ax, ax2)

    add_last_value_label(ax2, zori_yoy, color=THEME['primary'], fmt='{:.1f}%')
    add_last_value_label(ax, shelter_yoy, color=THEME['secondary'], fmt='{:.1f}%', side='left')

    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h2 + h1, l2 + l1, loc='upper left', **legend_style())

    add_annotation_box(ax, 'ZORI leads CPI Shelter by 12-18 months.\nMarket rents peaked 2022, shelter CPI peaked 2024.', x=0.22, y=0.70)

    brand_fig(fig, 'Zillow ZORI vs CPI Shelter Inflation',
              subtitle='Market Rents Lead Official Shelter CPI by 12-18 Months',
              source='Zillow, BLS via FRED')
    save_fig(fig, 'chart_22_zori_vs_shelter.png')


def chart_23():
    """Zillow ZHVI YoY% vs Case-Shiller National YoY%."""
    print('\nChart 23: Zillow ZHVI vs Case-Shiller (Lead/Lag)...')

    zhvi_yoy = fetch_db_yoy('ZILLOW_ZHVI_NATIONAL', start='1999-01-01', trim='2001-01-01')
    cs_yoy = fetch_fred_yoy('CSUSHPINSA', start='1999-01-01', trim='2001-01-01')

    fig, ax = new_fig()

    ax.plot(zhvi_yoy.index, zhvi_yoy, color=THEME['primary'], linewidth=2.5,
            label=f'Zillow ZHVI YoY% ({zhvi_yoy.iloc[-1]:.1f}%)')
    ax.plot(cs_yoy.index, cs_yoy, color=THEME['secondary'], linewidth=2.5,
            label=f'Case-Shiller National YoY% ({cs_yoy.iloc[-1]:.1f}%)')

    ax.axhline(0, color=COLORS['doldrums'], linewidth=0.8, alpha=0.5, linestyle='--')

    style_single_ax(ax)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.0f}%'))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    common_start = max(zhvi_yoy.index.min(), cs_yoy.index.min())
    common_end = max(zhvi_yoy.index.max(), cs_yoy.index.max())
    set_xlim_to_data(ax, pd.date_range(common_start, common_end))
    add_recessions(ax, start_date=str(common_start.date()))

    add_last_value_label(ax, zhvi_yoy, color=THEME['primary'], fmt='{:.1f}%')
    ax.legend(loc='upper left', **legend_style())

    add_annotation_box(ax, 'ZHVI leads Case-Shiller by 1-2 months.\nBroader coverage (all homes vs repeat sales).', x=0.55, y=0.90)

    brand_fig(fig, 'Zillow ZHVI vs Case-Shiller National',
              subtitle='Home Price Indices Year-over-Year',
              source='Zillow, S&P/Case-Shiller via FRED')
    save_fig(fig, 'chart_23_zhvi_vs_case_shiller.png')


def chart_24():
    """Regional Existing Home Sales (NE, MW, S, W)."""
    print('\nChart 24: Regional Existing Home Sales...')

    # NOTE: Regional existing home sales series (EXHOSLUS*) were added to FRED
    # in 2025 and only have ~13 months of history. Set start accordingly.
    regions = {
        'Northeast': fetch_fred_level('EXHOSLUSNEM495S', start='2024-01-01'),
        'Midwest': fetch_fred_level('EXHOSLUSMWM495S', start='2024-01-01'),
        'South': fetch_fred_level('EXHOSLUSSOM495S', start='2024-01-01'),
        'West': fetch_fred_level('EXHOSLUSWTM495S', start='2024-01-01'),
    }
    colors_map = [THEME['primary'], THEME['secondary'], THEME['tertiary'], THEME['quaternary']]

    fig, ax = new_fig()

    for (name, data), color in zip(regions.items(), colors_map):
        # Convert to thousands for readability
        data_k = data / 1e3
        ax.plot(data_k.index, data_k, color=color, linewidth=2.5,
                label=f'{name} ({data_k.iloc[-1]:,.0f}K)')

    style_single_ax(ax)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:,.0f}K'))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b\n%Y'))
    # Use South (largest) for x limits
    set_xlim_to_data(ax, regions['South'].index)
    ax.legend(loc='upper right', **legend_style())

    brand_fig(fig, 'Existing Home Sales by Region',
              subtitle='Seasonally Adjusted Annual Rate (SAAR) | 2025-2026',
              source='NAR via FRED')
    save_fig(fig, 'chart_24_regional_existing_sales.png')


# ============================================
# J. ARTICLE-SPECIFIC CHARTS (Charts 25-26)
# ============================================
def chart_25():
    """New Home Inventory and Months' Supply (for article Figure 8)."""
    print('\nChart 25: New Home Inventory + Months Supply...')

    # NOTE: Existing home inventory (HOSINVUSM495N) only has 13 months on FRED.
    # Using new home inventory (MNMFS) and months supply (MSACSR) instead —
    # full history back to 2005. Tells the supply glut/deficit story clearly.
    inv = fetch_fred_level('MNMFS', start='2005-01-01')   # New homes for sale (thousands)
    ms = fetch_fred_level('MSACSR', start='2005-01-01')    # Months supply

    fig, ax1 = new_fig()
    ax2 = ax1.twinx()

    c1, c2 = THEME['primary'], THEME['secondary']

    ax1.plot(inv.index, inv, color=c1, linewidth=2.5,
             label=f'New Homes For Sale ({inv.iloc[-1]:,.0f}K)')

    # Line for months supply
    ax2.plot(ms.index, ms, color=c2, linewidth=2.5,
             label=f'Months Supply ({ms.iloc[-1]:.1f})')

    # Balanced market reference
    ax2.axhline(6.0, color=COLORS['doldrums'], linewidth=1.0, linestyle='--', alpha=0.5,
                label='6 mo = Balanced Market')

    style_dual_ax(ax1, ax2, c1, c2)
    ax1.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:,.0f}K'))
    ax2.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.0f} mo'))
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    set_xlim_to_data(ax1, inv.index)
    add_recessions(ax1, start_date='2005-01-01')

    add_last_value_label(ax1, inv, color=c1, fmt='{:,.0f}K', side='left')
    add_last_value_label(ax2, ms, color=c2, fmt='{:.1f} mo')

    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax1.legend(h1 + h2, l1 + l2, loc='upper right', **legend_style())

    add_annotation_box(ax1, 'Inventory elevated vs 2020 lows\nbut months supply rising on weak demand.', x=0.45, y=0.93)

    brand_fig(fig, 'New Home Inventory and Months\' Supply',
              subtitle='Homes For Sale (Thousands) vs. Months at Current Sales Pace',
              source='Census Bureau via FRED')
    save_fig(fig, 'chart_25_inventory_months_supply.png')


def chart_26():
    """ZORI YoY% and Rental Vacancy Rate (for article Figure 11)."""
    print('\nChart 26: ZORI YoY + Rental Vacancy...')

    zori_yoy = fetch_db_yoy('ZILLOW_ZORI_NATIONAL', start='2016-01-01', trim='2017-01-01')
    vacancy = fetch_quarterly_level('RRVRUSQ156N', start='2017-01-01')

    fig, ax1 = new_fig()
    ax2 = ax1.twinx()

    c1, c2 = THEME['secondary'], THEME['primary']

    ax1.plot(zori_yoy.index, zori_yoy, color=c1, linewidth=2.5,
             label=f'ZORI YoY% ({zori_yoy.iloc[-1]:.1f}%)')
    ax2.plot(vacancy.index, vacancy, color=c2, linewidth=2.5,
             label=f'Rental Vacancy Rate ({vacancy.iloc[-1]:.1f}%)')

    # Invert ZORI axis so falling rent growth goes up (visually correlated with rising vacancy)
    ax1.invert_yaxis()

    ax1.axhline(0, color=COLORS['doldrums'], linewidth=0.8, alpha=0.5, linestyle='--')

    style_dual_ax(ax1, ax2, c1, c2)
    ax1.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.0f}%'))
    ax2.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.1f}%'))
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    common_start = max(zori_yoy.index.min(), vacancy.index.min())
    common_end = max(zori_yoy.index.max(), vacancy.index.max())
    set_xlim_to_data(ax1, pd.date_range(common_start, common_end))

    add_last_value_label(ax1, zori_yoy, color=c1, fmt='{:.1f}%', side='left')
    add_last_value_label(ax2, vacancy, color=c2, fmt='{:.1f}%')

    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax1.legend(h1 + h2, l1 + l2, loc='upper right', **legend_style())

    add_annotation_box(ax1, 'MF completion wave pushing vacancy higher.\nRent growth normalized from 15%+ to <2%.', x=0.60, y=0.92)

    brand_fig(fig, 'Zillow ZORI YoY% and Rental Vacancy Rate',
              subtitle='Rent Growth Normalizing as Multifamily Supply Delivers',
              source='Zillow, Census via FRED')
    save_fig(fig, 'chart_26_zori_vacancy.png')


# ============================================
# K. TRADINGVIEW DATA CHARTS (27-30)
# ============================================
def chart_27():
    """Existing Home Sales (SAAR) vs 30Y Mortgage Rate (dual axis, inverted RHS)."""
    print('\nChart 27: Existing Home Sales vs Mortgage Rate...')

    # Full existing home sales history from TradingView (697 months back to 1968)
    # FRED's EXHOSLUSM495S only has ~13 months after NAR restructured.
    sales_raw = fetch_db('TV_USEHS', start='2015-01-01')
    if sales_raw.empty:
        print('  WARNING: TV_USEHS not in DB. Run TradingView fetcher first.')
        return
    sales = sales_raw['value'].dropna() / 1e6  # Convert to millions
    rate = fetch_weekly_to_monthly('MORTGAGE30US', start='2015-01-01')

    fig, ax1 = new_fig()
    ax2 = ax1.twinx()

    c1, c2 = THEME['primary'], THEME['secondary']
    ax1.plot(sales.index, sales, color=c1, linewidth=2.5,
             label=f'Existing Home Sales ({sales.iloc[-1]:.2f}M)')
    ax2.plot(rate.index, rate, color=c2, linewidth=2.5,
             label=f'30Y Mortgage Rate ({rate.iloc[-1]:.2f}%)')

    # Invert right axis so rising rates go down
    ax2.invert_yaxis()

    # Reference lines for key levels
    ax1.axhline(4.5, color=COLORS['sea'], linewidth=1.0, linestyle='--', alpha=0.5,
                label='Thaw threshold (4.5M)')

    style_dual_ax(ax1, ax2, c1, c2)
    ax1.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.1f}M'))
    ax2.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.1f}%'))
    set_xlim_to_data(ax1, sales.index)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    add_last_value_label(ax1, sales, color=c1, fmt='{:.2f}M', side='left')
    add_last_value_label(ax2, rate, color=c2, fmt='{:.2f}%', side='right')
    add_recessions(ax1, start_date='2015-01-01')
    ax1.legend(loc='upper left', **legend_style())
    ax2.legend(loc='upper right', **legend_style())

    add_annotation_box(ax1, 'Sales collapsed from 6.5M to 3.9M.\nFrozen in 3.8-4.3M band since mid-2023.', x=0.80, y=0.80)

    brand_fig(fig, 'Existing Home Sales vs. 30-Year Mortgage Rate',
              subtitle='Inverted Rate Axis | The Frozen Market',
              source='NAR via TradingView, Freddie Mac via FRED')
    save_fig(fig, 'chart_27_existing_sales_vs_rate.png')


def chart_28():
    """NAHB Housing Market Index (from TradingView)."""
    print('\nChart 28: NAHB Housing Market Index...')

    nahb = fetch_db('TV_USHMI', start='2005-01-01')
    if nahb.empty:
        print('  WARNING: TV_USHMI not in DB. Run TradingView fetcher first.')
        return

    nahb_series = nahb['value'].dropna()

    fig, ax = new_fig()

    import numpy as np
    import matplotlib.collections as mcoll
    # Single line, blue above 50, orange below 50
    points = np.array([mdates.date2num(nahb_series.index), nahb_series.values]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    # Color each segment by midpoint value
    midpoints = (nahb_series.values[:-1] + nahb_series.values[1:]) / 2
    colors = [THEME['primary'] if m >= 50 else THEME['secondary'] for m in midpoints]
    lc = mcoll.LineCollection(segments, colors=colors, linewidths=2.5, zorder=3)
    ax.add_collection(lc)
    # Dummy for legend
    ax.plot([], [], color=THEME['primary'], linewidth=2.5,
            label=f'NAHB HMI ({nahb_series.iloc[-1]:.0f})')
    ax.fill_between(nahb_series.index, 50, nahb_series,
                    where=(nahb_series >= 50),
                    color=THEME['primary'], alpha=THEME['fill_alpha'],
                    interpolate=True)
    ax.fill_between(nahb_series.index, 50, nahb_series,
                    where=(nahb_series < 50),
                    color=THEME['secondary'], alpha=THEME['fill_alpha'],
                    interpolate=True)

    # 50 = breakeven
    ax.axhline(50, color=COLORS['doldrums'], linewidth=1.5, linestyle='--',
               label='Breakeven (50)')

    style_single_ax(ax)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.0f}'))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    set_xlim_to_data(ax, nahb_series.index)
    add_recessions(ax, start_date='2005-01-01')
    pill_color = THEME['primary'] if nahb_series.iloc[-1] >= 50 else THEME['secondary']
    add_last_value_label(ax, nahb_series, color=pill_color, fmt='{:.0f}')
    ax.legend(loc='upper left', **legend_style())

    add_annotation_box(ax, '21 months below 50.\nBuilders buying volume with margin.', x=0.18, y=0.88)

    brand_fig(fig, 'NAHB Housing Market Index',
              subtitle='Builder Sentiment | Above 50 = Expansion',
              source='NAHB via TradingView')
    save_fig(fig, 'chart_28_nahb_hmi.png')


def chart_29():
    """MBA Purchase Application Index (from TradingView)."""
    print('\nChart 29: MBA Purchase Application Index...')

    mba = fetch_db('TV_USPIND', start='2010-01-01')
    if mba.empty:
        print('  WARNING: TV_USPIND not in DB. Run TradingView fetcher first.')
        return

    mba_series = mba['value'].dropna()
    # Smooth with 3-month MA for readability (weekly data stored as monthly)
    mba_smooth = mba_series.rolling(3, min_periods=1).mean()

    fig, ax = new_fig()

    ax.plot(mba_smooth.index, mba_smooth, color=THEME['primary'], linewidth=2.5,
            label=f'MBA Purchase Index 3m MA ({mba_smooth.iloc[-1]:.0f})')
    ax.plot(mba_series.index, mba_series, color=THEME['primary'], linewidth=0.8,
            alpha=0.3)

    # Pre-pandemic average (2017-2019)
    pre_pandemic = mba_series.loc['2017-01-01':'2019-12-31'].mean()
    ax.axhline(pre_pandemic, color=COLORS['doldrums'], linewidth=1.0, linestyle='--',
               label=f'2017-2019 Avg ({pre_pandemic:.0f})')

    style_single_ax(ax)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:,.0f}'))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    set_xlim_to_data(ax, mba_smooth.index)
    add_recessions(ax, start_date='2010-01-01')
    add_last_value_label(ax, mba_smooth, color=THEME['primary'], fmt='{:,.0f}')
    ax.legend(loc='upper left', **legend_style())

    add_annotation_box(ax, 'Highest-frequency demand signal.\nLeads sales by 4-8 weeks.', x=0.78, y=0.88)

    brand_fig(fig, 'MBA Purchase Application Index',
              subtitle='Mortgage Demand | 3-Month Moving Average',
              source='Mortgage Bankers Association via TradingView')
    save_fig(fig, 'chart_29_mba_purchase.png')


def chart_30():
    """Pending Home Sales YoY% (from TradingView)."""
    print('\nChart 30: Pending Home Sales YoY%...')

    phs = fetch_db('TV_USPHSIYY', start='2010-01-01')
    if phs.empty:
        print('  WARNING: TV_USPHSIYY not in DB. Run TradingView fetcher first.')
        return

    phs_series = phs['value'].dropna()

    fig, ax = new_fig()

    ax.plot(phs_series.index, phs_series, color=THEME['primary'], linewidth=2.5,
            label=f'Pending Home Sales YoY% ({phs_series.iloc[-1]:.1f}%)')
    ax.fill_between(phs_series.index, 0, phs_series,
                    where=(phs_series >= 0),
                    color=THEME['primary'], alpha=THEME['fill_alpha'])
    ax.fill_between(phs_series.index, 0, phs_series,
                    where=(phs_series < 0),
                    color=THEME['secondary'], alpha=THEME['fill_alpha'])

    ax.axhline(0, color=COLORS['doldrums'], linewidth=1.0, linestyle='--')

    style_single_ax(ax)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.0f}%'))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    set_xlim_to_data(ax, phs_series.index)
    add_recessions(ax, start_date='2010-01-01')
    add_last_value_label(ax, phs_series, color=THEME['primary'], fmt='{:.1f}%')
    ax.legend(loc='upper left', **legend_style())

    add_annotation_box(ax, 'Pending sales = signed contracts.\nLeads closings by 1-2 months.', x=0.78, y=0.15)

    brand_fig(fig, 'Pending Home Sales',
              subtitle='Year-over-Year % Change',
              source='NAR via TradingView')
    save_fig(fig, 'chart_30_pending_home_sales.png')


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
    parser = argparse.ArgumentParser(description='Generate Housing educational charts')
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
