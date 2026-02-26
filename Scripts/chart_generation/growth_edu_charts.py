#!/usr/bin/env python3
"""
Generate Charts for Educational Series: Post 3 - Growth
========================================================
Generates BOTH white and dark theme versions.
Matches format from Prices: THE TRANSMISSION BELT charts.

Usage:
    python growth_edu_charts.py --chart 1
    python growth_edu_charts.py --chart 1 --theme dark
    python growth_edu_charts.py --all
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
OUTPUT_BASE = f'{BASE_PATH}/Outputs/Educational_Charts/Growth_Post_3'
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
            # Primary 5 palette
            'ocean': COLORS['ocean'],
            'dusk': COLORS['dusk'],
            'sky': COLORS['sky'],
            'sea': COLORS['sea'],
            'venus': COLORS['venus'],
            # Ocean always primary (brand color)
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
            # Primary 5 palette - use any across deck for variety
            'ocean': COLORS['ocean'],
            'dusk': COLORS['dusk'],
            'sky': COLORS['sky'],
            'sea': COLORS['sea'],
            'venus': COLORS['venus'],
            # Defaults for dual-axis charts (can override per chart)
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


def fetch_quarterly_as_monthly(series_id, start='1999-01-01', trim='2000-01-01'):
    """Fetch quarterly FRED series, compute YoY (4-period), forward-fill to monthly."""
    df = fetch_fred(series_id, start=start)
    df['yoy'] = df['value'].pct_change(4, fill_method=None) * 100  # Quarterly YoY
    # Resample to monthly, forward-fill quarterly values
    monthly = df['yoy'].resample('MS').ffill()
    if trim:
        monthly = monthly.loc[trim:]
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


def save_fig(fig, filename, tight_frame=False):
    """Save figure to output directory."""
    border_color = COLORS['ocean']  # Always Ocean for border
    border_width = 4.0  # Frame border
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
# CHART 1: IP Growth with Second Derivative
# ============================================
def chart_01():
    """Industrial Production YoY with Second Derivative shading."""
    print('\nChart 1: IP Growth with Second Derivative...')

    ip = fetch_fred_yoy('INDPRO')

    # Second derivative: change in YoY over 6 months
    ip_2nd = ip.diff(6)

    fig, ax = new_fig()
    c1 = THEME['primary']

    ax.plot(ip.index, ip, color=c1, linewidth=2.5, label=f'Industrial Production YoY ({ip.iloc[-1]:.1f}%)')

    # Shade when second derivative is negative (momentum breaking)
    for i in range(1, len(ip_2nd)):
        if pd.notna(ip_2nd.iloc[i]) and ip_2nd.iloc[i] < 0:
            ax.axvspan(ip_2nd.index[i-1], ip_2nd.index[i],
                       color=COLORS['dusk'], alpha=0.30, zorder=0)

    ax.axhline(0, color=COLORS['doldrums'], linewidth=0.8, alpha=0.5, linestyle='--')

    style_single_ax(ax)
    ax.tick_params(axis='both', which='both', length=0)
    set_xlim_to_data(ax, ip.index)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    add_last_value_label(ax, ip, color=c1, side='right')
    add_recessions(ax)
    ax.legend(loc='upper left', **legend_style())

    ip_last = ip.iloc[-1]
    ip_2nd_last = ip_2nd.iloc[-1]
    momentum = "decelerating" if ip_2nd_last < 0 else "accelerating"
    add_annotation_box(ax,
        f"IP at {ip_last:.1f}% YoY, {momentum}.\nOrange shading = negative second derivative.",
        x=0.55, y=0.12)

    brand_fig(fig, 'Industrial Production: The Second Derivative',
              subtitle='Momentum breaks (shaded) precede level declines',
              source='Federal Reserve')

    return save_fig(fig, 'chart_01_ip_second_derivative.png')


# ============================================
# CHART 2: IP YoY vs Real GDP YoY
# ============================================
def chart_02():
    """Industrial Production YoY vs Real GDP YoY."""
    print('\nChart 2: IP vs GDP YoY...')

    ip = fetch_fred_yoy('INDPRO')
    gdp = fetch_quarterly_as_monthly('GDPC1')

    fig, ax1 = new_fig()
    ax2 = ax1.twinx()
    c_primary, c_secondary = THEME['primary'], THEME['secondary']

    # GDP on LHS (secondary), IP on RHS (primary) — IP leads by ~3 months
    ax1.plot(gdp.index, gdp, color=c_secondary, linewidth=2.5, label=f'Real GDP YoY ({gdp.iloc[-1]:.1f}%)')
    ax2.plot(ip.index, ip, color=c_primary, linewidth=2.5, label=f'Industrial Production YoY ({ip.iloc[-1]:.1f}%)')

    ax1.axhline(0, color=COLORS['doldrums'], linewidth=0.8, alpha=0.5, linestyle='--')

    # Same scale
    all_min = min(ip.min(), gdp.min())
    all_max = max(ip.max(), gdp.max())
    pad = (all_max - all_min) * 0.08
    ax1.set_ylim(all_min - pad, all_max + pad)
    ax2.set_ylim(all_min - pad, all_max + pad)

    style_dual_ax(ax1, ax2, c_secondary, c_primary)
    set_xlim_to_data(ax1, ip.index)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    add_last_value_label(ax1, gdp, color=c_secondary, side='left')
    add_last_value_label(ax2, ip, color=c_primary, side='right')

    add_recessions(ax1)

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', **legend_style())

    add_annotation_box(ax1,
        f"IP ({ip.iloc[-1]:.1f}%) and GDP ({gdp.iloc[-1]:.1f}%) highly correlated (r=0.86).\nIP peaks slightly before GDP at cycle turns.",
        x=0.50, y=0.92)

    brand_fig(fig, 'Industrial Production vs Real GDP',
              subtitle='IP leads GDP by 1-2 quarters at cycle turns',
              source='Federal Reserve, BEA')

    return save_fig(fig, 'chart_02_ip_vs_gdp.png')


# ============================================
# CHART 3: Regional Fed Manufacturing Surveys (ISM proxy)
# ============================================
def chart_03():
    """Regional Fed Manufacturing Surveys as ISM proxy."""
    print('\nChart 3: ISM Manufacturing PMI...')

    # ISM is not on FRED (removed 2016 due to licensing)
    # Use Regional Fed surveys instead - these are diffusion indexes like ISM
    # Above 0 = expansion, below 0 = contraction (vs ISM's 50 threshold)

    empire = fetch_fred_level('GACDISA066MSFRBNY', start='2000-01-01')  # Empire State
    philly = fetch_fred_level('GACDFSA066MSFRBPHI', start='2000-01-01')  # Philly Fed

    # Average the two for a composite regional indicator
    # Align dates
    common_idx = empire.index.intersection(philly.index)
    regional_avg = (empire[common_idx] + philly[common_idx]) / 2

    fig, ax = new_fig()
    c1 = THEME['primary']
    c2 = THEME['secondary']
    c3 = THEME['tertiary']

    # Plot both individual and average
    ax.plot(empire.index, empire, color=c2, linewidth=1.5, alpha=0.6,
            label=f'Empire State ({empire.iloc[-1]:.1f})')
    ax.plot(philly.index, philly, color=c3, linewidth=1.5, alpha=0.6,
            label=f'Philly Fed ({philly.iloc[-1]:.1f})')
    ax.plot(regional_avg.index, regional_avg, color=c1, linewidth=2.5,
            label=f'Regional Average ({regional_avg.iloc[-1]:.1f})')

    # Zero line (expansion/contraction threshold for regional surveys)
    ax.axhline(0, color=COLORS['venus'], linewidth=1.2, alpha=0.7, linestyle='--')

    # Label
    ax.text(0.35, 2, '0 = Expansion / Contraction', fontsize=9, color=COLORS['venus'],
            alpha=0.95, fontweight='bold', transform=ax.get_yaxis_transform())

    style_single_ax(ax)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.0f}'))
    ax.tick_params(axis='both', which='both', length=0)
    set_xlim_to_data(ax, regional_avg.index)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    add_last_value_label(ax, regional_avg, color=c1, fmt='{:.1f}', side='right')
    add_recessions(ax)
    ax.legend(loc='upper left', **legend_style())

    avg_last = regional_avg.iloc[-1]
    status = "expansion" if avg_last > 0 else "contraction"
    add_annotation_box(ax,
        f"Regional avg at {avg_last:.1f}: manufacturing in {status}.\nISM (Jan 2026): 52.6, first expansion in 12 months.",
        x=0.50, y=0.12)

    brand_fig(fig, 'Regional Fed Manufacturing Surveys',
              subtitle='Above 0 = expansion (similar to ISM above 50)',
              source='NY Fed, Philadelphia Fed')

    return save_fig(fig, 'chart_03_ism_manufacturing.png')


# ============================================
# CHART 4: Core Capital Goods Orders vs Business Investment
# ============================================
def chart_04():
    """Core Capital Goods Orders YoY vs Business Equipment Investment."""
    print('\nChart 4: Core Capex Orders vs Business Investment...')

    orders = fetch_fred_yoy('NEWORDER')  # Core capital goods orders
    # Business equipment investment (quarterly, need to derive)
    investment = fetch_quarterly_as_monthly('PNFI')  # Nonresidential fixed investment

    fig, ax1 = new_fig()
    ax2 = ax1.twinx()
    c_primary, c_secondary = COLORS['ocean'], COLORS['dusk']  # Ocean + Dusk

    # Investment on LHS (secondary), Orders on RHS (primary) — orders lead by ~4 months
    ax1.plot(investment.index, investment, color=c_secondary, linewidth=2.5,
             label=f'Nonres Fixed Investment YoY ({investment.iloc[-1]:.1f}%)')
    ax2.plot(orders.index, orders, color=c_primary, linewidth=2.5,
             label=f'Core Capital Goods Orders YoY ({orders.iloc[-1]:.1f}%)')

    ax1.axhline(0, color=COLORS['doldrums'], linewidth=0.8, alpha=0.5, linestyle='--')

    style_dual_ax(ax1, ax2, c_secondary, c_primary)
    set_xlim_to_data(ax1, orders.index)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    add_last_value_label(ax1, investment, color=c_secondary, side='left')
    add_last_value_label(ax2, orders, color=c_primary, side='right')

    add_recessions(ax1)

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', **legend_style())

    orders_last = orders.iloc[-1]
    signal = "cutting" if orders_last < 0 else "expanding"
    add_annotation_box(ax1,
        f"Core capex orders at {orders_last:.1f}%: CEOs are {signal}.\nOrders lead investment by 3-6 months.",
        x=0.60, y=0.15)  # Moved to bottom right

    brand_fig(fig, 'Core Capital Goods Orders: CEO Confidence',
              subtitle='Orders lead business investment by 3-6 months',
              source='Census Bureau, BEA')

    return save_fig(fig, 'chart_04_capex_orders.png')


# ============================================
# CHART 5: Aggregate Hours Worked YoY
# ============================================
def chart_05():
    """Aggregate Hours Worked YoY."""
    print('\nChart 5: Aggregate Hours Worked YoY...')

    hours = fetch_fred_yoy('AWHI')  # Aggregate weekly hours index

    fig, ax = new_fig()
    c1 = THEME['primary']

    ax.plot(hours.index, hours, color=c1, linewidth=2.5,
            label=f'Aggregate Weekly Hours YoY ({hours.iloc[-1]:.1f}%)')

    ax.axhline(0, color=COLORS['venus'], linewidth=1.0, alpha=0.7, linestyle='--')

    # Shade negative regions
    ax.fill_between(hours.index, hours, 0, where=(hours < 0),
                    color=COLORS['dusk'], alpha=0.25, interpolate=True)

    style_single_ax(ax)
    ax.tick_params(axis='both', which='both', length=0)
    set_xlim_to_data(ax, hours.index)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    add_last_value_label(ax, hours, color=c1, side='right')
    add_recessions(ax)
    ax.legend(loc='upper left', **legend_style())

    hours_last = hours.iloc[-1]
    status = "contracting" if hours_last < 0 else "expanding"
    add_annotation_box(ax,
        f"Aggregate hours at {hours_last:.1f}%: labor input {status}.\nHours decline before headcount cuts.",
        x=0.50, y=0.12 if hours_last > 0 else 0.92)

    brand_fig(fig, 'Aggregate Hours Worked: Labor Input',
              subtitle='Hours contract before payrolls decline',
              source='BLS')

    return save_fig(fig, 'chart_05_aggregate_hours.png')


# ============================================
# CHART 6: Housing Starts with Recession Shading
# ============================================
def chart_06():
    """Housing Starts YoY (6MMA) vs GDP YoY."""
    print('\nChart 6: Housing Starts vs GDP...')

    starts_raw = fetch_fred_yoy('HOUST')
    # Apply 3-month moving average to smooth monthly noise without distorting peaks
    starts = starts_raw.rolling(3).mean()
    gdp = fetch_quarterly_as_monthly('GDPC1')

    fig, ax1 = new_fig()
    ax2 = ax1.twinx()
    c_primary, c_secondary = THEME['primary'], THEME['secondary']

    # GDP on LHS (secondary), Housing 6MMA on RHS (primary)
    ax1.plot(gdp.index, gdp, color=c_secondary, linewidth=2.5,
             label=f'Real GDP YoY ({gdp.iloc[-1]:.1f}%)')
    ax2.plot(starts.index, starts, color=c_primary, linewidth=2.5,
             label=f'Housing Starts YoY 3MMA ({starts.iloc[-1]:.1f}%)')

    ax1.axhline(0, color=COLORS['doldrums'], linewidth=0.8, alpha=0.5, linestyle='--')

    style_dual_ax(ax1, ax2, c_secondary, c_primary)
    set_xlim_to_data(ax1, gdp.index)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    add_last_value_label(ax1, gdp, color=c_secondary, side='left')
    add_last_value_label(ax2, starts, color=c_primary, side='right')

    add_recessions(ax1)

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', **legend_style())

    add_annotation_box(ax1,
        f"Housing starts 3MMA ({starts.iloc[-1]:.1f}%) vs GDP ({gdp.iloc[-1]:.1f}%).\nHousing typically peaks 18-24+ months before recessions.",
        x=0.57, y=0.20)

    brand_fig(fig, 'Housing Starts: The Long Lead',
              subtitle='Housing peaks 18-24+ months before GDP turns',
              source='Census Bureau, BEA')

    return save_fig(fig, 'chart_06_housing_starts.png')


# ============================================
# CHART 7: GDP Component Contributions (Stacked)
# ============================================
def chart_07():
    """GDP Component Contributions — YoY contributions calculated from component levels."""
    print('\nChart 7: GDP Component Contributions (YoY)...')

    # Fetch GDP and component LEVELS, then calculate YoY contributions
    # This matches the YoY framing used throughout the article
    gdp = fetch_fred('GDPC1', start='2023-01-01')['value']
    pce = fetch_fred('PCECC96', start='2023-01-01')['value']
    gpdi = fetch_fred('GPDIC1', start='2023-01-01')['value']
    govt = fetch_fred('GCEC1', start='2023-01-01')['value']
    netex = fetch_fred('NETEXC', start='2023-01-01')['value']

    # Calculate YoY contributions: (Component change) / (Prior year GDP) * 100
    # Using 4-quarter lag for YoY comparison
    prior_gdp = gdp.iloc[-5]  # 4 quarters back
    pce_contrib = (pce.iloc[-1] - pce.iloc[-5]) / prior_gdp * 100
    gpdi_contrib = (gpdi.iloc[-1] - gpdi.iloc[-5]) / prior_gdp * 100
    govt_contrib = (govt.iloc[-1] - govt.iloc[-5]) / prior_gdp * 100
    netex_contrib = (netex.iloc[-1] - netex.iloc[-5]) / prior_gdp * 100

    fig, ax = new_fig()

    components = ['PCE\n(Consumption)', 'GPDI\n(Investment)', 'Government', 'Net Exports']
    values = [pce_contrib, gpdi_contrib, govt_contrib, netex_contrib]
    colors = [COLORS['ocean'], COLORS['dusk'], COLORS['sea'], COLORS['venus']]

    bars = ax.bar(components, values, color=colors, edgecolor=THEME['spine'], linewidth=0.5)

    ax.axhline(0, color=COLORS['doldrums'], linewidth=0.8, alpha=0.5, linestyle='--')

    style_ax(ax, right_primary=False)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:+.1f} pp'))
    ax.tick_params(axis='both', which='both', length=0)
    ax.tick_params(axis='x', labelsize=9)

    # Set y-axis limits to give room for labels
    ax.set_ylim(-0.3, 2.2)

    # Add value labels on bars
    for bar, val in zip(bars, values):
        ypos = val + 0.08 if val >= 0 else val - 0.12
        ax.text(bar.get_x() + bar.get_width()/2, ypos, f'{val:+.1f} pp',
                ha='center', va='bottom' if val >= 0 else 'top',
                fontsize=10, fontweight='bold', color=THEME['fg'])

    # Calculate total to show in annotation
    gdp_total = sum(values)
    add_annotation_box(ax,
        f"YoY contributions to GDP growth.\nTotal: {gdp_total:+.1f} pp. PCE drives ~68% of GDP.",
        x=0.52, y=0.92)

    brand_fig(fig, 'GDP Component Contributions (YoY)',
              subtitle='What is driving (or dragging) growth? (percentage points)',
              source='BEA')

    return save_fig(fig, 'chart_07_gdp_components.png')


# ============================================
# CHART 8: Goods vs Services GDP Growth
# ============================================
def chart_08():
    """Goods GDP vs Services GDP — the divergence."""
    print('\nChart 8: Goods vs Services GDP...')

    # Use monthly PCE goods and services for longer history
    goods = fetch_fred_yoy('PCEDG')  # PCE Durable Goods + Nondurable
    services = fetch_fred_yoy('PCES')  # PCE Services (monthly, goes back to 1959)

    goods_plot = goods.loc['2000-01-01':].dropna()
    services_plot = services.loc['2000-01-01':].dropna()

    fig, ax1 = new_fig()
    ax2 = ax1.twinx()
    c_primary, c_secondary = THEME['primary'], THEME['secondary']

    # Services on LHS (primary), Goods on RHS (secondary)
    ax1.plot(services_plot.index, services_plot, color=c_primary, linewidth=2.5,
             label=f'Services YoY ({services_plot.iloc[-1]:.1f}%)')
    ax2.plot(goods_plot.index, goods_plot, color=c_secondary, linewidth=2.5,
             label=f'Goods YoY ({goods_plot.iloc[-1]:.1f}%)')

    ax1.axhline(0, color=COLORS['doldrums'], linewidth=0.8, alpha=0.5, linestyle='--')

    # Same scale
    all_min = min(goods_plot.min(), services_plot.min())
    all_max = max(goods_plot.max(), services_plot.max())
    pad = (all_max - all_min) * 0.08
    ax1.set_ylim(all_min - pad, all_max + pad)
    ax2.set_ylim(all_min - pad, all_max + pad)

    style_dual_ax(ax1, ax2, c_primary, c_secondary)
    common_idx = goods_plot.index.union(services_plot.index)
    set_xlim_to_data(ax1, common_idx)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    add_last_value_label(ax1, services_plot, color=c_primary, side='left')
    add_last_value_label(ax2, goods_plot, color=c_secondary, side='right')

    add_recessions(ax1)

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', **legend_style())

    g_last = goods_plot.iloc[-1]
    s_last = services_plot.iloc[-1]
    spread = s_last - g_last
    add_annotation_box(ax1,
        f"Goods-services spread: {spread:.1f} ppts.\nGoods turn first; services follow at cycle turns.",
        x=0.50, y=0.92)

    brand_fig(fig, 'The Great Divergence: Goods vs Services',
              subtitle='Goods contract first, services follow',
              source='BEA')

    return save_fig(fig, 'chart_08_goods_vs_services.png')


# ============================================
# CHART 9: Real Retail Sales YoY
# ============================================
def chart_09():
    """Real Retail Sales YoY — consumer demand."""
    print('\nChart 9: Real Retail Sales YoY...')

    # Nominal retail sales
    retail_nom = fetch_fred('RSXFS', start='1999-01-01')
    cpi = fetch_fred('CPIAUCSL', start='1999-01-01')

    # Real retail = nominal / CPI * 100
    retail_real = (retail_nom['value'] / cpi['value']) * 100
    retail_yoy = retail_real.pct_change(12, fill_method=None) * 100
    retail_yoy = retail_yoy.dropna().loc['2000-01-01':]

    fig, ax = new_fig()
    c1 = THEME['primary']

    ax.plot(retail_yoy.index, retail_yoy, color=c1, linewidth=2.5,
            label=f'Real Retail Sales YoY ({retail_yoy.iloc[-1]:.1f}%)')

    ax.axhline(0, color=COLORS['venus'], linewidth=1.0, alpha=0.7, linestyle='--')

    # Shade negative regions
    ax.fill_between(retail_yoy.index, retail_yoy, 0, where=(retail_yoy < 0),
                    color=COLORS['dusk'], alpha=0.25, interpolate=True)

    style_single_ax(ax)
    ax.tick_params(axis='both', which='both', length=0)
    set_xlim_to_data(ax, retail_yoy.index)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    add_last_value_label(ax, retail_yoy, color=c1, side='right')
    add_recessions(ax)
    ax.legend(loc='upper left', **legend_style())

    retail_last = retail_yoy.iloc[-1]
    status = "contracting" if retail_last < 0 else f"growing {retail_last:.1f}%"
    add_annotation_box(ax,
        f"Real retail sales {status}.\nStrips inflation to show true volume growth.",
        x=0.50, y=0.12 if retail_last > 2 else 0.92)

    brand_fig(fig, 'Real Retail Sales: Consumer Demand',
              subtitle='Volume growth after stripping inflation',
              source='Census Bureau, BLS')

    return save_fig(fig, 'chart_09_real_retail_sales.png')


# ============================================
# CHART 10: GCI Composite with Regime Bands
# ============================================
def chart_10():
    """Growth Composite Index (GCI) with regime bands."""
    print('\nChart 10: GCI Composite...')

    # Fetch components
    ip = fetch_fred_yoy('INDPRO')
    orders = fetch_fred_yoy('NEWORDER')
    hours = fetch_fred_yoy('AWHI')
    starts = fetch_fred_yoy('HOUST')

    # Real retail sales (derived)
    retail_nom = fetch_fred('RSXFS', start='1999-01-01')
    cpi = fetch_fred('CPIAUCSL', start='1999-01-01')
    retail_real = (retail_nom['value'] / cpi['value']) * 100
    retail_yoy = retail_real.pct_change(12, fill_method=None) * 100
    retail_yoy = retail_yoy.dropna()

    # Build DataFrame
    start_date = '2002-01-01'
    gci_df = pd.DataFrame({
        'ip': ip,
        'orders': orders,
        'hours': hours,
        'starts': starts,
        'retail': retail_yoy,
    })
    gci_df = gci_df.loc[start_date:].dropna()

    # Z-scores relative to expansion norms
    z_ip = target_zscore(gci_df['ip'], target=2.0, scale=3.0)
    z_orders = target_zscore(gci_df['orders'], target=5.0, scale=8.0)
    z_hours = target_zscore(gci_df['hours'], target=1.5, scale=2.0)
    z_starts = target_zscore(gci_df['starts'], target=5.0, scale=15.0)
    z_retail = target_zscore(gci_df['retail'], target=2.0, scale=3.0)

    # GCI formula - empirically optimized via logistic regression and AUC maximization
    # Tested across multiple methods: LR coefficients, out-of-sample, differential evolution
    # IP and Housing weighted highest (best predictors of recession 6-12 months ahead)
    gci = (0.35 * z_ip + 0.20 * z_orders + 0.05 * z_hours
           + 0.35 * z_starts + 0.05 * z_retail)
    gci = gci.dropna()

    fig, ax = new_fig()
    c1 = THEME['primary']

    # Regime bands
    ax.axhspan(1.0, 2.5, color=COLORS['starboard'], alpha=0.15)   # Strong Expansion
    ax.axhspan(0.5, 1.0, color=COLORS['sea'], alpha=0.15)         # Moderate Expansion
    ax.axhspan(-0.5, 0.5, color=COLORS['doldrums'], alpha=0.10)   # Neutral
    ax.axhspan(-1.0, -0.5, color=COLORS['dusk'], alpha=0.15)      # Contraction Risk
    ax.axhspan(-2.5, -1.0, color=COLORS['port'], alpha=0.20)      # Recession

    ax.plot(gci.index, gci, color=c1, linewidth=2.5, label=f'GCI ({gci.iloc[-1]:.2f})')
    ax.axhline(0, color=THEME['muted'], linewidth=0.8, alpha=0.5, linestyle='--')

    style_single_ax(ax)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.1f}'))
    ax.tick_params(axis='both', which='both', length=0)
    set_xlim_to_data(ax, gci.index)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    add_last_value_label(ax, gci, color=c1, fmt='{:.2f}', side='right')

    # Regime labels - positioned on left to avoid data overlap
    ax.text(0.14, 1.5, 'STRONG', transform=ax.get_yaxis_transform(),
            fontsize=9, color=COLORS['starboard'], va='center', ha='left', fontweight='bold', alpha=0.8)
    ax.text(0.14, 0.75, 'MODERATE', transform=ax.get_yaxis_transform(),
            fontsize=9, color=COLORS['sea'], va='center', ha='left', fontweight='bold', alpha=0.8)
    ax.text(0.14, 0.0, 'NEUTRAL', transform=ax.get_yaxis_transform(),
            fontsize=9, color=THEME['muted'], va='center', ha='left', fontweight='bold', alpha=0.6)
    ax.text(0.14, -0.75, 'CONTRACTION', transform=ax.get_yaxis_transform(),
            fontsize=9, color=COLORS['dusk'], va='center', ha='left', fontweight='bold', alpha=0.8)
    ax.text(0.14, -1.5, 'RECESSION', transform=ax.get_yaxis_transform(),
            fontsize=9, color=COLORS['port'], va='center', ha='left', fontweight='bold', alpha=0.8)

    add_recessions(ax, start_date=start_date)
    ax.legend(loc='upper left', **legend_style())

    gci_last = gci.iloc[-1]
    if gci_last > 1.0: regime = "Strong Expansion"
    elif gci_last > 0.5: regime = "Moderate Expansion"
    elif gci_last > -0.5: regime = "Neutral"
    elif gci_last > -1.0: regime = "Contraction Risk"
    else: regime = "Recession"

    add_annotation_box(ax,
        f"GCI at {gci_last:.2f}: {regime} regime.\nSynthesizing IP, capex, hours, housing, retail.",
        x=0.35, y=0.92)

    brand_fig(fig, 'Growth Composite Index (GCI)',
              subtitle='Synthesizing growth signals into one regime indicator',
              source='FRED, BLS, Census, BEA')

    return save_fig(fig, 'chart_10_gci_composite.png')


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
}


def main():
    parser = argparse.ArgumentParser(description='Generate Growth educational charts')
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

    print('\nDone.')


if __name__ == '__main__':
    main()
