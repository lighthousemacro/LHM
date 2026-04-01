#!/usr/bin/env python3
"""
Generate Charts for Educational Series: Post 10 - Plumbing (Pillar 10)
======================================================================
11 charts covering: Reserves vs LCLOR, RRP rise and fall, EFFR-IORB spread,
SOFR-IORB spread, SOFR-EFFR spread, Fed balance sheet composition,
TGA balance, MMF assets, OFR FSI funding, CP spreads, net liquidity.

Generates BOTH white and dark theme versions.

Usage:
    python plumbing_edu_charts.py --chart 1
    python plumbing_edu_charts.py --chart 1 --theme dark
    python plumbing_edu_charts.py --all
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
OUTPUT_BASE = f'{BASE_PATH}/Outputs/Educational_Charts/Plumbing_Post_10'
DB_PATH = f'{BASE_PATH}/Data/databases/Lighthouse_Master.db'
ICON_PATH = f'{BASE_PATH}/Brand/icon_transparent_128.png'

fred = Fred()

# Simple cache to avoid refetching same data across themes
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


def set_theme(mode='white'):
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
    """Fetch a FRED series and return as DataFrame. Uses cache."""
    cache_key = f"{series_id}_{start}"
    if cache_key in _DATA_CACHE:
        return _DATA_CACHE[cache_key].copy()

    time.sleep(1.0)
    s = fred.get_series(series_id, observation_start=start)
    df = s.to_frame(name='value')
    df.index.name = 'date'
    _DATA_CACHE[cache_key] = df.copy()
    return df


def fetch_db(series_id, start='1950-01-01'):
    """Fetch a series from the master DB (immutable read-only)."""
    cache_key = f"db_{series_id}_{start}"
    if cache_key in _DATA_CACHE:
        return _DATA_CACHE[cache_key].copy()

    conn = sqlite3.connect(
        f'file:///{DB_PATH}?mode=ro&immutable=1', uri=True
    )
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


def fetch_horizon(columns, start='1950-01-01'):
    """Fetch columns from horizon_dataset (immutable read-only)."""
    cache_key = f"hz_{'_'.join(columns)}_{start}"
    if cache_key in _DATA_CACHE:
        return _DATA_CACHE[cache_key].copy()

    conn = sqlite3.connect(
        f'file:///{DB_PATH}?mode=ro&immutable=1', uri=True
    )
    cols_str = ', '.join([f'"{c}"' for c in columns])
    df = pd.read_sql(
        f'SELECT date, {cols_str} FROM horizon_dataset WHERE date >= ? ORDER BY date',
        conn, params=(start,)
    )
    conn.close()

    if df.empty:
        return pd.DataFrame()

    df['date'] = pd.to_datetime(df['date'])
    df = df.set_index('date')
    for c in columns:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    _DATA_CACHE[cache_key] = df.copy()
    return df


def smart_fetch(series_id, fred_id=None, start='1950-01-01'):
    """Try DB first, fall back to FRED."""
    s = fetch_db_level(series_id, start=start)
    if len(s) > 10:
        return s
    fid = fred_id or series_id
    print(f'  DB miss for {series_id}, fetching from FRED as {fid}...')
    return fetch_fred_level(fid, start=start)


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


def add_annotation_box(ax, text, x=0.50, y=0.95):
    """Add takeaway annotation box."""
    box_fc = '#2389BB'
    txt_color = '#ffffff'
    ax.text(x, y, text, transform=ax.transAxes,
            fontsize=11, fontweight='bold', color=txt_color, ha='center', va='top',
            style='italic',
            bbox=dict(boxstyle='round,pad=0.5',
                      facecolor=box_fc, edgecolor='#23BBFF',
                      linewidth=2.0, alpha=1.0))


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
        edgecolor='#23BBFF' if THEME['mode'] == 'dark' else THEME['spine'],
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
# CHART 1: Reserves vs LCLOR
# ============================================
def chart_01():
    """Reserves vs LCLOR estimate."""
    print('\nChart 1: Reserves vs LCLOR...')

    reserves = smart_fetch('WRESBAL', start='2014-01-01')
    # WRESBAL is in millions, convert to trillions
    reserves = reserves / 1e6

    fig, ax = new_fig()

    ax.plot(reserves.index, reserves, color=THEME['primary'], linewidth=2.5,
            label=f'Bank Reserves (${reserves.iloc[-1]:.2f}T)', zorder=5)

    # LCLOR band: $3.0T to $3.25T
    ax.axhspan(3.0, 3.25, color=COLORS['port'], alpha=0.15, zorder=0,
               label='LCLOR Est. $3.0\u20133.25T (Sep 2024 FOMC)')

    # Annotation for the LCLOR band
    add_annotation_box(ax, 'Sep 2024 Fed minutes: reserves approaching\n'
                       '"lowest comfortable level" ($3.0\u20133.25T)',
                       x=0.70, y=0.25)

    style_single_ax(ax, fmt='${:.1f}T')
    set_xlim_to_data(ax, reserves.index)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    add_last_value_label(ax, reserves, color=THEME['primary'], fmt='${:.2f}T', side='right')
    add_recessions(ax, start_date='2014-01-01')
    ax.legend(loc='upper left', fontsize=10, **legend_style())

    brand_fig(fig, 'The Buffer Is Thinner Than You Think',
              subtitle='Figure 1: Bank Reserves vs. LCLOR Estimate',
              source='Federal Reserve H.4.1', data_date=reserves.index[-1])
    save_fig(fig, 'P10_01_reserves_vs_lclor.png')


# ============================================
# CHART 2: RRP Rise and Fall
# ============================================
def chart_02():
    """RRP usage: the spent buffer."""
    print('\nChart 2: RRP Rise and Fall...')

    rrp = smart_fetch('RRPONTSYD', start='2013-01-01')
    # RRPONTSYD is in billions
    rrp_t = rrp / 1000  # Convert to trillions

    fig, ax = new_fig()

    ax.fill_between(rrp_t.index, 0, rrp_t, color=THEME['primary'], alpha=0.5, zorder=2)
    ax.plot(rrp_t.index, rrp_t, color=THEME['primary'], linewidth=1.5, zorder=3)

    # $200B threshold line (0.2T)
    ax.axhline(0.2, color=COLORS['venus'], linestyle='--', linewidth=1.5, alpha=0.8, zorder=4)
    ax.text(rrp_t.index[len(rrp_t)//5 + int(len(rrp_t)*0.15)], 0.25, 'Buffer Exhausted ($200B)',
            fontsize=10, color=COLORS['venus'], fontweight='bold')

    # Key date annotations
    annotations = [
        ('2021-06-01', 'ON RRP\nramps up', 0.6),
        ('2022-12-01', 'Peak:\n~$2.5T', 2.7),
        ('2025-10-15', 'Oct 2025\nSOFR spike', 0.3),
        ('2026-01-15', 'RRP = $0', 0.15),
    ]
    for date_str, label, y_pos in annotations:
        dt = pd.Timestamp(date_str)
        if dt <= rrp_t.index[-1]:
            ax.annotate(label, xy=(dt, y_pos),
                        fontsize=9, fontweight='bold', color=THEME['fg'],
                        ha='center', va='bottom',
                        bbox=dict(boxstyle='round,pad=0.3', facecolor=THEME['bg'],
                                  edgecolor=THEME['spine'], alpha=0.9))

    style_single_ax(ax, fmt='${:.1f}T')
    set_xlim_to_data(ax, rrp_t.index)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax.set_ylim(bottom=-0.05)
    add_last_value_label(ax, rrp_t, color=THEME['primary'], fmt='${:.2f}T', side='right')
    add_recessions(ax, start_date='2013-01-01')

    brand_fig(fig, 'The Spent Buffer: $2.5 Trillion, Gone',
              subtitle='Figure 2: ON RRP Facility Usage',
              source='NY Fed', data_date=rrp_t.index[-1])
    save_fig(fig, 'P10_02_rrp_rise_and_fall.png')


# ============================================
# CHART 3: EFFR-IORB Spread
# ============================================
def chart_03():
    """EFFR minus IORB spread."""
    print('\nChart 3: EFFR-IORB Spread...')

    effr = smart_fetch('EFFR', start='2014-01-01')
    iorb = smart_fetch('IORB', start='2014-01-01')
    # IORB only starts Jul 2021; before that use IOER
    ioer = smart_fetch('IOER', start='2014-01-01')

    # Combine IOER and IORB
    rate_on_reserves = pd.concat([ioer[ioer.index < '2021-07-29'], iorb[iorb.index >= '2021-07-29']])
    rate_on_reserves = rate_on_reserves.sort_index()

    # Align on common dates
    common = effr.index.intersection(rate_on_reserves.index)
    spread = (effr.loc[common] - rate_on_reserves.loc[common]) * 100  # Convert to bps

    fig, ax = new_fig()

    ax.plot(spread.index, spread, color=THEME['primary'], linewidth=2.0,
            label='EFFR \u2212 IORB (bps)')

    # Zero line
    ax.axhline(0, color=COLORS['fog'], linestyle='--', linewidth=1.0, zorder=1)

    # +8 bps threshold
    ax.axhline(8, color=COLORS['venus'], linestyle='-', linewidth=1.5, zorder=4)
    ax.text(spread.index[len(spread)//3 + int(len(spread)*0.25)], 9.5, 'Acute Stress (+8 bps)',
            fontsize=10, color=COLORS['venus'], fontweight='bold')

    style_single_ax(ax, fmt='{:.0f}')
    set_xlim_to_data(ax, spread.index)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    add_last_value_label(ax, spread, color=THEME['primary'], fmt='{:.1f}', side='right')
    add_recessions(ax, start_date='2014-01-01')
    ax.legend(loc='upper left', fontsize=10, **legend_style())

    brand_fig(fig, 'The Canary in the Funding Mine',
              subtitle='Figure 3: EFFR \u2212 IORB Spread',
              source='Federal Reserve', data_date=spread.index[-1])
    save_fig(fig, 'P10_03_effr_iorb_spread.png')


# ============================================
# CHART 4: SOFR-IORB Spread
# ============================================
def chart_04():
    """SOFR minus IORB spread."""
    print('\nChart 4: SOFR-IORB Spread...')

    sofr = smart_fetch('SOFR', start='2018-04-01')
    iorb = smart_fetch('IORB', start='2018-04-01')
    ioer = smart_fetch('IOER', start='2018-04-01')

    # Combine IOER and IORB
    rate_on_reserves = pd.concat([ioer[ioer.index < '2021-07-29'], iorb[iorb.index >= '2021-07-29']])
    rate_on_reserves = rate_on_reserves.sort_index()

    common = sofr.index.intersection(rate_on_reserves.index)
    spread = (sofr.loc[common] - rate_on_reserves.loc[common]) * 100  # bps

    fig, ax = new_fig()

    ax.plot(spread.index, spread, color=THEME['secondary'], linewidth=2.0,
            label='SOFR \u2212 IORB (bps)')

    # Zero line
    ax.axhline(0, color=COLORS['fog'], linestyle='--', linewidth=1.0, zorder=1)

    # +8 bps threshold
    ax.axhline(8, color=COLORS['venus'], linestyle='-', linewidth=1.5, zorder=4)
    ax.text(spread.index[len(spread)//10 + int(len(spread)*0.25)], 10, 'Stress Threshold (+8 bps)',
            fontsize=10, color=COLORS['venus'], fontweight='bold')

    # Annotate Sep 2019 spike if visible
    sep2019 = spread.loc['2019-09-15':'2019-09-20']
    if len(sep2019) > 0:
        peak_date = sep2019.idxmax()
        peak_val = sep2019.max()
        ax.annotate(f'Sep 17, 2019\nSOFR spike\n({peak_val:.0f} bps)',
                    xy=(peak_date, peak_val),
                    xytext=(peak_date + pd.Timedelta(days=120), peak_val * 0.7),
                    fontsize=9, fontweight='bold', color=THEME['fg'],
                    arrowprops=dict(arrowstyle='->', color=THEME['fg'], lw=1.5),
                    bbox=dict(boxstyle='round,pad=0.3', facecolor=THEME['bg'],
                              edgecolor=THEME['spine'], alpha=0.9))

    style_single_ax(ax, fmt='{:.0f}')
    set_xlim_to_data(ax, spread.index)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    add_last_value_label(ax, spread, color=THEME['secondary'], fmt='{:.1f}', side='right')
    add_recessions(ax, start_date='2018-04-01')
    ax.legend(loc='upper left', fontsize=10, **legend_style())

    brand_fig(fig, 'September 2019 Started Here',
              subtitle='Figure 4: SOFR \u2212 IORB Spread',
              source='NY Fed, Federal Reserve', data_date=spread.index[-1])
    save_fig(fig, 'P10_04_sofr_iorb_spread.png')


# ============================================
# CHART 4B: SOFR-EFFR Spread (Dealer Capacity)
# ============================================
def chart_04b():
    """SOFR minus EFFR spread: dealer balance sheet barometer."""
    print('\nChart 4B: SOFR-EFFR Spread...')

    sofr = smart_fetch('SOFR', start='2018-04-01')
    effr = smart_fetch('EFFR', start='2018-04-01')

    common = sofr.index.intersection(effr.index)
    spread = (sofr.loc[common] - effr.loc[common]) * 100  # bps

    fig, ax = new_fig()

    ax.plot(spread.index, spread, color=THEME['tertiary'], linewidth=2.0,
            label='SOFR \u2212 EFFR (bps)')

    # Zero line
    ax.axhline(0, color=COLORS['fog'], linestyle='--', linewidth=1.0, zorder=1)

    # Shade regimes
    ax.fill_between(spread.index, 0, spread,
                    where=(spread > 0),
                    color=COLORS['port'], alpha=0.10, zorder=0,
                    label='Balance sheet constrained (SOFR > EFFR)')
    ax.fill_between(spread.index, 0, spread,
                    where=(spread < 0),
                    color=COLORS['starboard'], alpha=0.10, zorder=0,
                    label='Cash abundant (SOFR < EFFR)')

    style_single_ax(ax, fmt='{:.0f}')
    set_xlim_to_data(ax, spread.index)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    add_last_value_label(ax, spread, color=THEME['tertiary'], fmt='{:.1f}', side='right')
    add_recessions(ax, start_date='2018-04-01')
    ax.legend(loc='upper left', fontsize=9, **legend_style())

    add_annotation_box(ax, 'When secured (SOFR) costs more than unsecured (EFFR),\n'
                       'dealer balance sheet capacity is the binding constraint.',
                       x=0.50, y=0.20)

    brand_fig(fig, 'When Secured Costs More Than Unsecured',
              subtitle='Figure 5: SOFR \u2212 EFFR Spread (Dealer Capacity Barometer)',
              source='NY Fed, Federal Reserve', data_date=spread.index[-1])
    save_fig(fig, 'P10_04b_sofr_effr_spread.png')


# ============================================
# CHART 5: Fed Balance Sheet Composition
# ============================================
def chart_05():
    """Fed balance sheet: QT's quiet drain."""
    print('\nChart 5: Fed Balance Sheet Composition...')

    walcl = smart_fetch('WALCL', start='2008-01-01')
    treast = smart_fetch('TREAST', start='2008-01-01')
    mbs = smart_fetch('WSHOMCB', start='2008-01-01')

    # All in millions, convert to trillions
    walcl_t = walcl / 1e6
    treast_t = treast / 1e6
    mbs_t = mbs / 1e6

    # Align indices
    common = walcl_t.index.intersection(treast_t.index).intersection(mbs_t.index)
    walcl_t = walcl_t.loc[common]
    treast_t = treast_t.loc[common]
    mbs_t = mbs_t.loc[common]
    other_t = walcl_t - treast_t - mbs_t
    other_t = other_t.clip(lower=0)

    fig, ax = new_fig()

    ax.fill_between(common, 0, treast_t, color=THEME['primary'], alpha=0.7,
                    label=f'Treasuries (${treast_t.iloc[-1]:.2f}T)', zorder=2)
    ax.fill_between(common, treast_t, treast_t + mbs_t, color=THEME['secondary'], alpha=0.7,
                    label=f'MBS (${mbs_t.iloc[-1]:.2f}T)', zorder=2)
    ax.fill_between(common, treast_t + mbs_t, treast_t + mbs_t + other_t,
                    color=THEME['tertiary'], alpha=0.5,
                    label=f'Other (${other_t.iloc[-1]:.2f}T)', zorder=2)

    # Total line
    ax.plot(common, walcl_t, color=THEME['fg'], linewidth=1.5, linestyle='--',
            label=f'Total (${walcl_t.iloc[-1]:.2f}T)', zorder=5, alpha=0.6)

    # QE/QT regime annotations
    regimes = [
        ('2008-11-01', 'QE1', 1.5),
        ('2010-11-01', 'QE2', 3.0),
        ('2012-09-01', 'QE3', 3.5),
        ('2017-10-01', 'QT1', 4.0),
        ('2020-03-15', 'COVID\nQE', 5.5),
        ('2022-06-01', 'QT2', 8.5),
    ]
    for date_str, label, y_pos in regimes:
        dt = pd.Timestamp(date_str)
        if dt <= common[-1]:
            ax.axvline(dt, color=THEME['muted'], linestyle=':', linewidth=0.8, alpha=0.5)
            ax.text(dt, y_pos, f' {label}', fontsize=9, fontweight='bold',
                    color=THEME['muted'], va='bottom', ha='left')

    style_single_ax(ax, fmt='${:.0f}T')
    set_xlim_to_data(ax, common)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax.set_ylim(bottom=0)
    add_last_value_label(ax, walcl_t, color=THEME['primary'], fmt='${:.1f}T', side='right')
    add_recessions(ax, start_date='2008-01-01')
    ax.legend(loc='upper left', fontsize=9, **legend_style())

    brand_fig(fig, "QT's Quiet Drain",
              subtitle='Figure 6: Fed Balance Sheet Composition',
              source='Federal Reserve H.4.1', data_date=common[-1])
    save_fig(fig, 'P10_05_fed_balance_sheet.png')


# ============================================
# CHART 6: TGA Balance
# ============================================
def chart_06():
    """Treasury General Account balance."""
    print('\nChart 6: TGA Balance...')

    tga = smart_fetch('WTREGEN', start='2015-01-01')
    # WTREGEN is in millions, convert to billions
    tga_b = tga / 1e3

    fig, ax = new_fig()

    ax.plot(tga_b.index, tga_b, color=THEME['primary'], linewidth=2.0,
            label=f'TGA Balance (${tga_b.iloc[-1]:.0f}B)')

    # Normal operating level reference
    ax.axhline(750, color=COLORS['fog'], linestyle='--', linewidth=1.0, zorder=1)
    ax.text(tga_b.index[len(tga_b)//3 - int(len(tga_b)*0.20)], 780, 'Typical Operating Level (~$750B)',
            fontsize=9, color=COLORS['doldrums'])

    # Debt ceiling annotations
    dc_events = [
        ('2019-03-01', '2019 Debt\nCeiling', 0.75),
        ('2021-08-01', '2021 Debt\nCeiling', 0.85),
        ('2023-01-15', '2023 Debt Ceiling\n(Drawdown)', 0.80),
        ('2023-06-15', 'Post-Ceiling\nRebuilds TGA', 0.70),
    ]
    for date_str, label, y_frac in dc_events:
        dt = pd.Timestamp(date_str)
        if dt <= tga_b.index[-1]:
            y_pos = ax.get_ylim()[1] * y_frac
            ax.annotate(label, xy=(dt, tga_b.asof(dt)),
                        xytext=(dt + pd.Timedelta(days=30), y_pos),
                        fontsize=8, fontweight='bold', color=THEME['fg'],
                        arrowprops=dict(arrowstyle='->', color=THEME['muted'], lw=1.0),
                        bbox=dict(boxstyle='round,pad=0.3', facecolor=THEME['bg'],
                                  edgecolor=THEME['spine'], alpha=0.9))

    style_single_ax(ax, fmt='${:.0f}B')
    set_xlim_to_data(ax, tga_b.index)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax.set_ylim(bottom=0)
    add_last_value_label(ax, tga_b, color=THEME['primary'], fmt='${:.0f}B', side='right')
    add_recessions(ax, start_date='2015-01-01')
    ax.legend(loc='upper left', fontsize=10, **legend_style())

    brand_fig(fig, "The Treasury's Checking Account",
              subtitle='Figure 7: Treasury General Account (TGA)',
              source='Federal Reserve', data_date=tga_b.index[-1])
    save_fig(fig, 'P10_06_tga_balance.png')


# ============================================
# CHART 7: Money Market Fund Assets
# ============================================
def chart_07():
    """Money Market Fund assets: where the RRP cash went."""
    print('\nChart 7: Money Market Fund Assets...')

    # Try OFR monthly data first, then quarterly FRED
    mmf = fetch_db_level('OFR_MMF-MMF_TOT-M', start='2010-01-01')
    source_label = 'OFR'
    if len(mmf) < 10:
        mmf = smart_fetch('MMMFFAQ027S', start='2000-01-01')
        source_label = 'Federal Reserve'

    # OFR data is in raw dollars; FRED quarterly is in millions
    if source_label == 'OFR':
        mmf_t = mmf / 1e12  # raw dollars to trillions
    else:
        mmf_t = mmf / 1e6  # millions to trillions

    fig, ax = new_fig()

    ax.fill_between(mmf_t.index, 0, mmf_t, color=THEME['primary'], alpha=0.4, zorder=2)
    ax.plot(mmf_t.index, mmf_t, color=THEME['primary'], linewidth=2.0, zorder=3,
            label=f'MMF Total Assets (${mmf_t.iloc[-1]:.2f}T)')

    add_annotation_box(ax, 'RRP drained to zero: $2.5T in cash migrated\n'
                       'from the Fed into money market funds and T-bills.',
                       x=0.40, y=0.95)

    style_single_ax(ax, fmt='${:.1f}T')
    set_xlim_to_data(ax, mmf_t.index)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax.set_ylim(bottom=0)
    add_last_value_label(ax, mmf_t, color=THEME['primary'], fmt='${:.2f}T', side='right')
    add_recessions(ax, start_date='2010-01-01')
    ax.legend(loc='upper left', fontsize=10, **legend_style())

    brand_fig(fig, 'Where the Money Went: RRP to Money Markets',
              subtitle='Figure 8: Money Market Fund Total Assets',
              source=source_label, data_date=mmf_t.index[-1])
    save_fig(fig, 'P10_07_mmf_assets.png')


# ============================================
# CHART 8: OFR FSI Funding Component
# ============================================
def chart_08():
    """OFR Financial Stress Index: Funding component."""
    print('\nChart 8: OFR FSI Funding...')

    hz = fetch_horizon(['OFR_FSI_Funding'], start='2000-01-01')
    if hz.empty:
        print('  WARNING: OFR_FSI_Funding not in horizon, trying observations...')
        fsi_fund = fetch_db_level('OFR_FSI_Funding', start='2000-01-01')
    else:
        fsi_fund = hz['OFR_FSI_Funding'].dropna()

    if len(fsi_fund) == 0:
        print('  SKIP: No OFR FSI Funding data available.')
        return

    fig, ax = new_fig()

    ax.plot(fsi_fund.index, fsi_fund, color=THEME['primary'], linewidth=2.0,
            label=f'OFR FSI Funding ({fsi_fund.iloc[-1]:.2f})')

    # Zero line
    ax.axhline(0, color=COLORS['fog'], linestyle='--', linewidth=1.0, zorder=1)

    # Regime shading
    ax.fill_between(fsi_fund.index, 1.0, fsi_fund,
                    where=(fsi_fund > 1.0),
                    color=COLORS['port'], alpha=0.08, zorder=0,
                    label='Stress (> +1.0)')
    ax.fill_between(fsi_fund.index, -1.0, fsi_fund,
                    where=(fsi_fund < -1.0),
                    color=COLORS['starboard'], alpha=0.08, zorder=0,
                    label='Calm (< \u22121.0)')

    # Threshold lines
    ax.axhline(1.0, color=COLORS['port'], linestyle=':', linewidth=1.0, alpha=0.5)
    ax.axhline(-1.0, color=COLORS['starboard'], linestyle=':', linewidth=1.0, alpha=0.5)

    style_single_ax(ax, fmt='{:.1f}')
    set_xlim_to_data(ax, fsi_fund.index)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    add_last_value_label(ax, fsi_fund, color=THEME['primary'], fmt='{:.2f}', side='right')
    add_recessions(ax, start_date='2000-01-01')
    ax.legend(loc='upper left', fontsize=9, **legend_style())

    brand_fig(fig, "Third-Party Validation: Funding Stress Is Quiet... For Now",
              subtitle='Figure 9: OFR Financial Stress Index (Funding Component)',
              source='OFR', data_date=fsi_fund.index[-1])
    save_fig(fig, 'P10_08_ofr_fsi_funding.png')


# ============================================
# CHART 9: Commercial Paper Spreads
# ============================================
def chart_09():
    """Commercial paper spreads: unsecured funding signal."""
    print('\nChart 9: Commercial Paper Spreads...')

    cp = smart_fetch('DCPF3M', start='2010-01-01')
    effr = smart_fetch('EFFR', start='2010-01-01')

    # Align on common dates
    common = cp.index.intersection(effr.index)
    spread = (cp.loc[common] - effr.loc[common]) * 100  # bps

    fig, ax = new_fig()

    ax.plot(spread.index, spread, color=THEME['secondary'], linewidth=2.0,
            label='3M Fin. CP \u2212 EFFR (bps)')

    # Zero line
    ax.axhline(0, color=COLORS['fog'], linestyle='--', linewidth=1.0, zorder=1)

    # 20-day moving average for smoothing
    spread_ma = spread.rolling(20, min_periods=5).mean()
    ax.plot(spread_ma.index, spread_ma, color=THEME['primary'], linewidth=1.5,
            alpha=0.7, label='20-day MA')

    style_single_ax(ax, fmt='{:.0f}')
    set_xlim_to_data(ax, spread.index)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    add_last_value_label(ax, spread, color=THEME['secondary'], fmt='{:.1f}', side='right')
    add_recessions(ax, start_date='2010-01-01')
    ax.legend(loc='upper left', fontsize=10, **legend_style())

    brand_fig(fig, 'Unsecured Funding: The Next Signal',
              subtitle='Figure 10: 3-Month Financial Commercial Paper Spread vs EFFR',
              source='Federal Reserve', data_date=spread.index[-1])
    save_fig(fig, 'P10_09_cp_spreads.png')


# ============================================
# CHART 10: Net Liquidity vs S&P 500
# ============================================
def chart_10():
    """Net liquidity proxy vs S&P 500."""
    print('\nChart 10: Net Liquidity vs S&P 500...')

    # Get components from horizon_dataset
    hz = fetch_horizon(['Fed_Balance_Sheet', 'Treasury_General_Account', 'RRP_Usage'],
                       start='2018-01-01')

    if hz.empty:
        walcl = smart_fetch('WALCL', start='2018-01-01')
        tga = smart_fetch('WTREGEN', start='2018-01-01')
        rrp = smart_fetch('RRPONTSYD', start='2018-01-01')
        # Align
        common = walcl.index.intersection(tga.index).intersection(rrp.index)
        net_liq = (walcl.loc[common] - tga.loc[common] - rrp.loc[common]) / 1e6  # to trillions
    else:
        hz = hz.dropna(subset=['Fed_Balance_Sheet'])
        # Horizon dataset: Fed_Balance_Sheet is in millions, TGA and RRP in millions
        net_liq = (hz['Fed_Balance_Sheet'] - hz['Treasury_General_Account'].fillna(0) - hz['RRP_Usage'].fillna(0)) / 1e6

    # SPX from observations
    spx = fetch_db_level('SPX_Close', start='2018-01-01')
    if len(spx) < 10:
        spx = smart_fetch('SP500', start='2018-01-01')

    fig, ax1 = new_fig()
    ax2 = ax1.twinx()

    c1 = THEME['primary']
    c2 = THEME['secondary']

    ax1.plot(net_liq.index, net_liq, color=c1, linewidth=2.0,
             label='Net Liquidity ($T)')
    ax2.plot(spx.index, spx, color=c2, linewidth=2.0,
             label='S&P 500')

    style_dual_ax(ax1, ax2, c1, c2)
    ax1.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'${x:.1f}T'))
    ax2.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:,.0f}'))

    # Set x-limits
    all_dates = net_liq.index.union(spx.index)
    set_xlim_to_data(ax1, all_dates)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax1.tick_params(axis='x', labelcolor=THEME['fg'])

    add_last_value_label(ax1, net_liq, color=c1, fmt='${:.2f}T', side='left')
    add_last_value_label(ax2, spx, color=c2, fmt='{:,.0f}', side='right')

    add_recessions(ax1, start_date='2018-01-01')

    # Combined legend
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=10, **legend_style())

    data_date = max(net_liq.index[-1], spx.index[-1]) if len(spx) > 0 else net_liq.index[-1]
    brand_fig(fig, 'The Net Liquidity Equation',
              subtitle='Figure 11: Net Liquidity (Fed BS \u2212 TGA \u2212 RRP) vs S&P 500',
              source='Federal Reserve, Yahoo Finance', data_date=data_date)
    save_fig(fig, 'P10_10_net_liquidity.png')


# ============================================
# CHART 11: SOFR Volume (Repo Market Scale)
# ============================================
def chart_11():
    """SOFR transaction volume: the scale of the repo market."""
    print('\nChart 11: SOFR Volume...')

    vol = smart_fetch('SOFRVOL', start='2018-04-01')

    if len(vol) < 10:
        print('  SKIP: Insufficient SOFR Volume data.')
        return

    # Already in billions
    vol_t = vol / 1000  # Convert to trillions

    fig, ax = new_fig()

    # Light bars for daily, thick MA line for trend
    ax.fill_between(vol_t.index, 0, vol_t, color=THEME['primary'], alpha=0.25, zorder=2)
    vol_ma = vol_t.rolling(20, min_periods=5).mean()
    ax.plot(vol_ma.index, vol_ma, color=THEME['primary'], linewidth=2.5,
            label=f'SOFR Volume 20d MA (${vol_ma.iloc[-1]:.2f}T)', zorder=5)

    # Annotate key milestones
    annotations = [
        ('2020-03-15', 'COVID\nLiquidity\nCrisis', 0.85),
        ('2022-06-01', 'QT\nBegins', 0.80),
        ('2025-12-01', 'QT\nEnds', 0.75),
    ]
    for date_str, label, y_frac in annotations:
        dt = pd.Timestamp(date_str)
        if dt <= vol_t.index[-1]:
            y_pos = ax.get_ylim()[1] * y_frac if ax.get_ylim()[1] > 0 else vol_t.max() * y_frac
            ax.axvline(dt, color=THEME['muted'], linestyle=':', linewidth=0.8, alpha=0.5)
            ax.text(dt + pd.Timedelta(days=15), y_pos, label,
                    fontsize=9, fontweight='bold', color=THEME['muted'], va='top')

    add_annotation_box(ax, 'Repo market has more than tripled since 2018.\n'
                       'More volume = more intermediation demand on constrained dealer balance sheets.',
                       x=0.35, y=0.30)

    style_single_ax(ax, fmt='${:.1f}T')
    set_xlim_to_data(ax, vol_t.index)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax.set_ylim(bottom=0)
    add_last_value_label(ax, vol_t, color=THEME['primary'], fmt='${:.2f}T', side='right')
    add_recessions(ax, start_date='2018-04-01')
    ax.legend(loc='upper left', fontsize=10, **legend_style())

    brand_fig(fig, 'The Plumbing Got Bigger. The Plumbers Didn\'t.',
              subtitle='Figure 12: SOFR Transaction Volume (Daily Repo Market Activity)',
              source='NY Fed', data_date=vol_t.index[-1])
    save_fig(fig, 'P10_12_sofr_volume.png')


# ============================================
# MAIN
# ============================================
CHART_MAP = {
    1: chart_01,
    2: chart_02,
    3: chart_03,
    4: chart_04,
    '4b': chart_04b,
    5: chart_05,
    6: chart_06,
    7: chart_07,
    8: chart_08,
    9: chart_09,
    10: chart_10,
    11: chart_11,
}


def main():
    parser = argparse.ArgumentParser(description='Generate Pillar 10 (Plumbing) educational charts')
    parser.add_argument('--chart', type=str, default=None,
                        help='Chart number to generate (1-11, or "4b")')
    parser.add_argument('--theme', type=str, default='white', choices=['white', 'dark', 'both'],
                        help='Theme to generate')
    parser.add_argument('--all', action='store_true',
                        help='Generate all charts')
    args = parser.parse_args()

    themes = ['white', 'dark'] if args.theme == 'both' else [args.theme]

    for theme in themes:
        print(f'\n{"="*60}')
        print(f'  GENERATING {theme.upper()} THEME CHARTS')
        print(f'{"="*60}')
        set_theme(theme)

        if args.all or args.chart is None:
            for key in [1, 2, 3, 4, '4b', 5, 6, 7, 8, 9, 10, 11]:
                try:
                    CHART_MAP[key]()
                except Exception as e:
                    print(f'  ERROR on chart {key}: {e}')
                    import traceback
                    traceback.print_exc()
        else:
            chart_key = args.chart
            try:
                chart_key = int(chart_key)
            except ValueError:
                pass
            if chart_key in CHART_MAP:
                CHART_MAP[chart_key]()
            else:
                print(f'Unknown chart: {chart_key}')

    # Copy white theme outputs to the Pillar_10 directory for Substack
    white_dir = os.path.join(OUTPUT_BASE, 'white')
    pub_dir = os.path.join(BASE_PATH, 'Outputs', 'Charts', 'Pillar_10')
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
