#!/usr/bin/env python3
"""
Generate Charts for Positioning Update #2 (February 22, 2026)
==============================================================
The Tariff Regime Breaks. The Defensive Thesis Doesn't.

Generates BOTH dark and white theme versions.
11 charts matching the positioning update narrative.

Usage:
    python positioning_update_2_charts.py --all
    python positioning_update_2_charts.py --chart 1
    python positioning_update_2_charts.py --chart 1 --theme dark
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
from matplotlib.collections import LineCollection
from fredapi import Fred

# Fix SSL certificate issue
os.environ['SSL_CERT_FILE'] = certifi.where()
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()

# ============================================
# PATHS & CONFIG
# ============================================
BASE_PATH = '/Users/bob/LHM'
OUTPUT_BASE = f'{BASE_PATH}/Outputs/Deliverables/Positioning_Update_2_2026-02-22'
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


def fetch_fred_level(series_id, start='1950-01-01'):
    """Fetch FRED series as-is (rate/level)."""
    df = fetch_fred(series_id, start=start)
    return df['value'].dropna()


def fetch_db(series_id, start='2000-01-01'):
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


def fetch_db_level(series_id, start='1950-01-01'):
    """Fetch DB series as-is."""
    df = fetch_db(series_id, start=start)
    if df.empty:
        return pd.Series(dtype=float)
    return df['value'].dropna()


def fetch_index(index_id, start='2000-01-01'):
    """Fetch a pre-computed composite index from lighthouse_indices."""
    cache_key = f"idx_{index_id}_{start}"
    if cache_key in _DATA_CACHE:
        return _DATA_CACHE[cache_key].copy()
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql(
        "SELECT date, value, status FROM lighthouse_indices WHERE index_id = ? AND date >= ? ORDER BY date",
        conn, params=(index_id, start)
    )
    conn.close()
    if df.empty:
        return pd.DataFrame(columns=['value', 'status'])
    df['date'] = pd.to_datetime(df['date'])
    df = df.set_index('date')
    _DATA_CACHE[cache_key] = df.copy()
    return df


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
    """Add takeaway annotation box."""
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
# CHART 1: Pillar Dashboard (Diagnostic Dozen Readings)
# ============================================
def chart_01():
    """Diagnostic Dozen: horizontal bar chart showing all pillar readings and regimes."""
    print('\nChart 1: Pillar Dashboard...')

    # Fetch latest reading for each pillar
    pillar_ids = ['LPI', 'PCI', 'GCI', 'HCI', 'CCI', 'BCI', 'TCI', 'GCI_Gov', 'FCI', 'LCI']
    pillar_labels = [
        '1. Labor (LPI)',
        '2. Prices (PCI)',
        '3. Growth (GCI)',
        '4. Housing (HCI)',
        '5. Consumer (CCI)',
        '6. Business (BCI)',
        '7. Trade (TCI)',
        '8. Government (GCI-Gov)',
        '9. Financial (FCI)',
        '10. Plumbing (LCI)',
    ]

    values = []
    statuses = []
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    for pid in pillar_ids:
        cur.execute('SELECT value, status FROM lighthouse_indices WHERE index_id=? ORDER BY date DESC LIMIT 1', (pid,))
        row = cur.fetchone()
        if row:
            values.append(row[0])
            statuses.append(row[1] or '')
        else:
            values.append(0.0)
            statuses.append('N/A')

    # Also get derived composites
    derived_ids = ['LFI', 'CLG', 'MRI']
    derived_labels = ['LFI (Labor Fragility)', 'CLG (Credit-Labor Gap)', 'MRI (Master Risk Index)']
    derived_values = []
    derived_statuses = []
    for did in derived_ids:
        cur.execute('SELECT value, status FROM lighthouse_indices WHERE index_id=? ORDER BY date DESC LIMIT 1', (did,))
        row = cur.fetchone()
        if row:
            derived_values.append(row[0])
            derived_statuses.append(row[1] or '')
        else:
            derived_values.append(0.0)
            derived_statuses.append('N/A')
    conn.close()

    # Combine all
    all_labels = pillar_labels + ['', ''] + derived_labels  # empty strings for spacing
    all_values = values + [0, 0] + derived_values
    all_statuses = statuses + ['', ''] + derived_statuses

    # Filter out spacers for plotting
    plot_labels = pillar_labels + derived_labels
    plot_values = values + derived_values
    plot_statuses = statuses + derived_statuses

    fig, ax = plt.subplots(figsize=(14, 10))
    fig.patch.set_facecolor(THEME['bg'])
    ax.set_facecolor(THEME['bg'])
    fig.subplots_adjust(top=0.88, bottom=0.06, left=0.28, right=0.88)

    y_pos = np.arange(len(plot_labels))[::-1]  # Reverse so Pillar 1 is at top

    # Color bars by value: green for positive/healthy, red for negative/stressed
    bar_colors = []
    for v, status in zip(plot_values, plot_statuses):
        s_upper = status.upper()
        if s_upper in ('HEALTHY', 'EXPANSION', 'AMPLE', 'ON TARGET', 'NEUTRAL', 'TREND', 'MID-CYCLE', 'NORMAL'):
            bar_colors.append(COLORS['sea'])
        elif s_upper in ('ELEVATED', 'TIGHT', 'SLOWING', 'FROZEN', 'HEADWIND', 'MISPRICED'):
            bar_colors.append(COLORS['dusk'])
        elif s_upper in ('HIGH', 'SCARCE', 'STRESS', 'CRITICAL', 'CRISIS'):
            bar_colors.append(COLORS['venus'])
        else:
            bar_colors.append(COLORS['ocean'])

    bars = ax.barh(y_pos, plot_values, color=bar_colors, height=0.6, alpha=0.85, zorder=3)

    # Add value + status labels (always to the right of the bar end)
    for i, (v, s) in enumerate(zip(plot_values, plot_statuses)):
        # Place label to the right of bar for positive, to the right of zero for negative
        x_pos = max(v, 0) + 0.05
        ax.text(x_pos, y_pos[i], f'{v:+.2f}  {s}',
                va='center', ha='left', fontsize=10, fontweight='bold',
                color=THEME['fg'])

    # Zero line
    ax.axvline(0, color=THEME['fg'], linewidth=0.8, alpha=0.5)

    # Threshold markers
    ax.axvline(-0.5, color=COLORS['doldrums'], linewidth=0.8, linestyle=':', alpha=0.4)
    ax.axvline(0.5, color=COLORS['doldrums'], linewidth=0.8, linestyle=':', alpha=0.4)

    # Separator line between pillars and derived
    sep_y = y_pos[len(pillar_labels) - 1] - 0.5
    ax.axhline(sep_y, color=THEME['spine'], linewidth=1.5, linestyle='-', alpha=0.5)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(plot_labels, fontsize=11, color=THEME['fg'])
    ax.set_xlabel('Z-Score', fontsize=11, color=THEME['fg'])

    style_ax(ax, right_primary=False)
    ax.tick_params(axis='both', which='both', length=0)
    ax.tick_params(axis='y', labelcolor=THEME['fg'], labelsize=11)
    ax.tick_params(axis='x', labelcolor=THEME['fg'], labelsize=10)

    brand_fig(fig, 'The Diagnostic Dozen: Pillar Readings',
              subtitle='12 Macro Pillars + Derived Composites (Latest)',
              source='Lighthouse Macro Composite Indices')

    return save_fig(fig, 'chart_01_pillar_dashboard.png')


# ============================================
# CHART 2: JOLTS Quits Rate
# ============================================
def chart_02():
    """JOLTS Quits Rate: sitting on the pre-recessionary threshold."""
    print('\nChart 2: JOLTS Quits Rate...')

    quits = fetch_db_level('JTSQUR', start='2001-01-01')

    fig, ax = new_fig()

    ax.plot(quits.index, quits, color=THEME['primary'], linewidth=2.5,
            label=f'JOLTS Quits Rate ({quits.iloc[-1]:.1f}%)')

    # Pre-recessionary threshold at 2.0%
    ax.axhline(2.0, color=COLORS['venus'], linewidth=1.5, linestyle='-', alpha=0.8,
               label='Pre-Recessionary Threshold (2.0%)')

    # Shade below threshold
    ax.fill_between(quits.index, 2.0, quits,
                    where=(quits <= 2.0),
                    color=COLORS['venus'], alpha=0.10)

    style_single_ax(ax)
    set_xlim_to_data(ax, quits.index)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    add_last_value_label(ax, quits, color=THEME['primary'], side='right')
    add_recessions(ax, start_date='2001-01-01')
    ax.legend(loc='upper left', **legend_style())

    q_last = quits.iloc[-1]
    add_annotation_box(ax,
        f"Quits at {q_last:.1f}%. The line is 2.0%.\n"
        f"Below 2.0% = workers afraid to leave. Pre-recessionary confirmed.",
        x=0.68, y=0.92)

    brand_fig(fig, 'JOLTS Quits Rate',
              subtitle='The Truth Serum: workers vote with their feet',
              source='BLS via FRED (JTSQUR)', data_date=quits.index[-1])

    return save_fig(fig, 'chart_02_quits_rate.png')


# ============================================
# CHART 3: JOLTS Openings Rate
# ============================================
def chart_03():
    """JOLTS Openings Rate: collapse to 2020 lows."""
    print('\nChart 3: JOLTS Openings Rate...')

    # BLS_JTS000000000000000JOR = JOLTS Job Openings Rate
    openings = fetch_db_level('BLS_JTS000000000000000JOR', start='2001-01-01')

    fig, ax = new_fig()

    ax.plot(openings.index, openings, color=THEME['primary'], linewidth=2.5,
            label=f'JOLTS Openings Rate ({openings.iloc[-1]:.1f}%)')
    ax.fill_between(openings.index, openings, alpha=THEME['fill_alpha'],
                    color=THEME['primary'])

    style_single_ax(ax)
    set_xlim_to_data(ax, openings.index)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    add_last_value_label(ax, openings, color=THEME['primary'], side='right')
    add_recessions(ax, start_date='2001-01-01')
    ax.legend(loc='upper left', **legend_style())

    o_last = openings.iloc[-1]
    add_annotation_box(ax,
        f"Openings rate at {o_last:.1f}%, lowest since 2020.\n"
        f"Professional services, retail, and finance leading lower.",
        x=0.68, y=0.92)

    brand_fig(fig, 'JOLTS Job Openings Rate',
              subtitle='Demand for labor is collapsing',
              source='BLS (JOLTS)', data_date=openings.index[-1])

    return save_fig(fig, 'chart_03_jolts_openings.png')


# ============================================
# CHART 4: Labor Fragility Index (LFI)
# ============================================
def chart_04():
    """Labor Fragility Index: structural weakness building."""
    print('\nChart 4: Labor Fragility Index...')

    lfi_df = fetch_index('LFI', start='2001-01-01')
    lfi_raw = lfi_df['value'].dropna()
    lfi_spot = lfi_raw.iloc[-1]  # Latest raw reading
    # Apply 3-month MA to smooth daily noise
    lfi = lfi_raw.rolling(63, min_periods=20).mean()
    lfi = lfi.dropna()

    fig, ax = new_fig()

    # Faint raw series for context
    ax.plot(lfi_raw.index, lfi_raw, color=THEME['primary'], linewidth=0.4, alpha=0.25)
    ax.plot(lfi.index, lfi, color=THEME['primary'], linewidth=2.5,
            label=f'LFI 3M MA ({lfi.iloc[-1]:.2f})')
    ax.fill_between(lfi.index, lfi, alpha=THEME['fill_alpha'] * 0.5,
                    color=THEME['primary'])

    # Mark latest spot reading
    ax.scatter([lfi_raw.index[-1]], [lfi_spot], color=COLORS['venus'],
               s=60, zorder=5, label=f'Spot: {lfi_spot:.2f}')

    # +0.5 elevated threshold
    ax.axhline(0.5, color=COLORS['dusk'], linewidth=1.5, linestyle='-', alpha=0.8,
               label='Elevated Fragility (+0.5)')
    # +1.0 high risk
    ax.axhline(1.0, color=COLORS['venus'], linewidth=1.5, linestyle='--', alpha=0.7,
               label='High Fragility (+1.0)')
    # Zero
    ax.axhline(0, color=COLORS['doldrums'], linewidth=0.8, linestyle='--', alpha=0.5)

    # Shade above elevated
    ax.fill_between(lfi.index, 0.5, lfi,
                    where=(lfi >= 0.5),
                    color=COLORS['dusk'], alpha=0.08)

    style_ax(ax, right_primary=True)
    ax.tick_params(axis='both', which='both', length=0)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.1f}'))
    set_xlim_to_data(ax, lfi.index)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    add_last_value_label(ax, lfi, color=THEME['primary'], fmt='{:.2f}', side='right')
    add_recessions(ax, start_date='2001-01-01')
    ax.legend(loc='upper left', **legend_style())

    lfi_ma = lfi.iloc[-1]
    add_annotation_box(ax,
        f"LFI spot: {lfi_spot:+.2f} (3M MA: {lfi_ma:+.2f}).\n"
        f"Spot spiked above +0.5 elevated threshold in mid-January.\n"
        f"Long-term unemployment building, quits decelerating.",
        x=0.62, y=0.92)

    brand_fig(fig, 'Labor Fragility Index (LFI)',
              subtitle='Structural weakness before headline unemployment catches up',
              source='Lighthouse Macro Composite (BLS JOLTS + CPS)',
              data_date=lfi.index[-1])

    return save_fig(fig, 'chart_04_lfi.png')


# ============================================
# CHART 5: HY OAS (Credit Still in Denial)
# ============================================
def chart_05():
    """HY OAS: credit complacency deepens."""
    print('\nChart 5: HY OAS...')

    hy_oas = fetch_db_level('BAMLH0A0HYM2', start='1997-01-01')
    # Convert to bps (series is in percentage points, multiply by 100)
    hy_oas_bps = hy_oas * 100

    fig, ax = new_fig()

    ax.plot(hy_oas_bps.index, hy_oas_bps, color=THEME['primary'], linewidth=2.0,
            label=f'HY OAS ({hy_oas_bps.iloc[-1]:.0f} bps)')
    ax.fill_between(hy_oas_bps.index, hy_oas_bps, alpha=THEME['fill_alpha'] * 0.5,
                    color=THEME['primary'])

    # 300 bps complacent threshold
    ax.axhline(300, color=COLORS['dusk'], linewidth=1.5, linestyle='-', alpha=0.8,
               label='Complacent Threshold (300 bps)')

    # Shade below complacent
    ax.fill_between(hy_oas_bps.index, 300, hy_oas_bps,
                    where=(hy_oas_bps < 300),
                    color=COLORS['dusk'], alpha=0.08)

    style_ax(ax, right_primary=True)
    ax.tick_params(axis='both', which='both', length=0)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.0f}'))
    set_xlim_to_data(ax, hy_oas_bps.index)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    add_last_value_label(ax, hy_oas_bps, color=THEME['primary'], fmt='{:.0f} bps', side='right')
    add_recessions(ax, start_date='1997-01-01')
    ax.legend(loc='upper left', **legend_style())

    oas_last = hy_oas_bps.iloc[-1]
    add_annotation_box(ax,
        f"HY OAS at {oas_last:.0f} bps. Below 300 = complacent.\n"
        f"Credit pricing a different economy than labor is reporting.",
        x=0.62, y=0.92)

    brand_fig(fig, 'High Yield OAS: Credit Spreads',
              subtitle='Credit Still in Denial',
              source='ICE BofA via FRED (BAMLH0A0HYM2)',
              data_date=hy_oas_bps.index[-1])

    return save_fig(fig, 'chart_05_hy_oas.png')


# ============================================
# CHART 6: Credit-Labor Gap (CLG)
# ============================================
def chart_06():
    """Credit-Labor Gap: deeply negative, credit ignoring fundamentals."""
    print('\nChart 6: Credit-Labor Gap...')

    clg_df = fetch_index('CLG', start='2000-01-01')
    clg_raw = clg_df['value'].dropna()
    clg_spot = clg_raw.iloc[-1]  # Latest raw reading
    # Apply 3-month MA to smooth daily noise
    clg = clg_raw.rolling(63, min_periods=20).mean().dropna()

    fig, ax = new_fig()

    # Color the line by regime
    x_vals = mdates.date2num(clg.index)
    y_vals = clg.values
    threshold = -1.0
    segments = []
    seg_colors = []
    for i in range(len(x_vals) - 1):
        x0, y0 = x_vals[i], y_vals[i]
        x1, y1 = x_vals[i + 1], y_vals[i + 1]
        if (y0 - threshold) * (y1 - threshold) < 0:
            t = (threshold - y0) / (y1 - y0)
            x_cross = x0 + t * (x1 - x0)
            segments.append([[x0, y0], [x_cross, threshold]])
            seg_colors.append(COLORS['sea'] if y0 >= threshold else COLORS['venus'])
            segments.append([[x_cross, threshold], [x1, y1]])
            seg_colors.append(COLORS['sea'] if y1 >= threshold else COLORS['venus'])
        else:
            segments.append([[x0, y0], [x1, y1]])
            seg_colors.append(COLORS['sea'] if y0 >= threshold else COLORS['venus'])
    lc = LineCollection(segments, colors=seg_colors, linewidths=2.5)
    ax.add_collection(lc)
    ax.autoscale()

    # Legend entries
    ax.plot([], [], color=COLORS['sea'], linewidth=2.5, label='CLG > -1.0 (normal)')
    ax.plot([], [], color=COLORS['venus'], linewidth=2.5, label='CLG < -1.0 (credit ignoring labor)')

    # Thresholds
    ax.axhline(-1.0, color=COLORS['venus'], linewidth=1.5, linestyle='-', alpha=0.7,
               label='Credit Ignoring Fundamentals (-1.0)')
    ax.axhline(0, color=COLORS['doldrums'], linewidth=0.8, linestyle='--', alpha=0.5)

    style_ax(ax, right_primary=True)
    ax.tick_params(axis='both', which='both', length=0)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.1f}'))
    set_xlim_to_data(ax, clg.index)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    add_last_value_label(ax, clg, color=COLORS['venus'] if clg.iloc[-1] < -1.0 else COLORS['sea'],
                         fmt='{:.2f}', side='right')
    # Mark latest spot reading
    ax.scatter([clg_raw.index[-1]], [clg_spot], color=COLORS['venus'],
               s=60, zorder=5)
    add_recessions(ax, start_date='2000-01-01')
    ax.legend(loc='upper left', **legend_style())

    clg_ma = clg.iloc[-1]
    add_annotation_box(ax,
        f"CLG spot: {clg_spot:.2f}, 3M MA: {clg_ma:.2f}.\n"
        f"Spot deeply below -1.0. Credit ignoring labor fundamentals.",
        x=0.62, y=0.15)

    brand_fig(fig, 'Credit-Labor Gap (CLG)',
              subtitle='z(HY OAS) minus z(LFI): when credit ignores labor, it ends badly',
              source='Lighthouse Macro Composite',
              data_date=clg.index[-1])

    return save_fig(fig, 'chart_06_clg.png')


# ============================================
# CHART 7: VIX
# ============================================
def chart_07():
    """VIX: from complacency to recalibration."""
    print('\nChart 7: VIX...')

    vix = fetch_db_level('VIXCLS', start='2020-01-01')

    fig, ax = new_fig()

    ax.plot(vix.index, vix, color=THEME['primary'], linewidth=2.0,
            label=f'VIX ({vix.iloc[-1]:.1f})')
    ax.fill_between(vix.index, vix, alpha=THEME['fill_alpha'] * 0.5,
                    color=THEME['primary'])

    # 50-day MA
    vix_50d = vix.rolling(50, min_periods=20).mean()
    ax.plot(vix_50d.index, vix_50d, color=THEME['secondary'], linewidth=1.5,
            linestyle='--', alpha=0.8, label=f'50d MA ({vix_50d.iloc[-1]:.1f})')

    # Reference levels
    ax.axhline(20, color=COLORS['doldrums'], linewidth=0.8, linestyle=':', alpha=0.5)
    ax.axhline(30, color=COLORS['dusk'], linewidth=0.8, linestyle=':', alpha=0.5)

    style_ax(ax, right_primary=True)
    ax.tick_params(axis='both', which='both', length=0)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.0f}'))
    set_xlim_to_data(ax, vix.index)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))

    add_last_value_label(ax, vix, color=THEME['primary'], fmt='{:.1f}', side='right')
    ax.legend(loc='upper left', **legend_style())

    vix_last = vix.iloc[-1]
    add_annotation_box(ax,
        f"VIX at {vix_last:.1f}. Dropped from ~21 on SCOTUS ruling.\n"
        f"Not cheap, but no longer pricing full tariff uncertainty.\n"
        f"Don't add new vol here. Monetize existing hedges.",
        x=0.62, y=0.92)

    brand_fig(fig, 'CBOE Volatility Index (VIX)',
              subtitle='From Complacency to Recalibration',
              source='CBOE via FRED (VIXCLS)',
              data_date=vix.index[-1])

    return save_fig(fig, 'chart_07_vix.png')


# ============================================
# CHART 8: SOFR vs EFFR (The One Switch)
# ============================================
def chart_08():
    """SOFR vs EFFR spread: The One Switch. Defensive vs Disorderly."""
    print('\nChart 8: SOFR vs EFFR...')

    # EFFR from DB (good data)
    effr = fetch_db_level('NYFED_EFFR', start='2019-01-01')

    # SOFR from FRED API (DB data is corrupted)
    sofr_raw = fetch_fred_level('SOFR', start='2019-01-01')
    # Align to percent (SOFR is in %)
    sofr = sofr_raw

    # Two-panel: top = rates, bottom = spread
    fig, (ax_top, ax_bot) = plt.subplots(2, 1, figsize=(14, 8),
        gridspec_kw={'height_ratios': [65, 35], 'hspace': 0.0})
    fig.patch.set_facecolor(THEME['bg'])
    ax_top.set_facecolor(THEME['bg'])
    ax_bot.set_facecolor(THEME['bg'])
    fig.subplots_adjust(top=0.88, bottom=0.08, left=0.06, right=0.94)

    c1 = THEME['primary']
    c2 = THEME['secondary']

    # === TOP PANEL: Both rates ===
    ax_top.plot(sofr.index, sofr, color=c1, linewidth=2.0,
                label=f'SOFR ({sofr.iloc[-1]:.2f}%)')
    ax_top.plot(effr.index, effr, color=c2, linewidth=2.0,
                label=f'EFFR ({effr.iloc[-1]:.2f}%)')

    style_ax(ax_top, right_primary=True)
    ax_top.spines['bottom'].set_linewidth(4.0)
    ax_top.tick_params(axis='both', which='both', length=0)
    ax_top.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.1f}%'))
    set_xlim_to_data(ax_top, sofr.index)
    ax_top.set_xticklabels([])
    add_last_value_label(ax_top, sofr, color=c1, fmt='{:.2f}%', side='right')
    add_last_value_label(ax_top, effr, color=c2, fmt='{:.2f}%', side='right')
    ax_top.legend(loc='upper left', **legend_style())

    # === BOTTOM PANEL: Spread in bps ===
    # Align dates
    combined = pd.DataFrame({'sofr': sofr, 'effr': effr}).dropna()
    spread = (combined['sofr'] - combined['effr']) * 100  # Convert to bps

    # Color by regime
    c_normal = COLORS['sea']
    c_stress = COLORS['venus']
    ax_bot.fill_between(spread.index, 0, spread, where=(spread < 15),
                        color=c_normal, alpha=0.15)
    ax_bot.fill_between(spread.index, 0, spread, where=(spread >= 15),
                        color=c_stress, alpha=0.15)
    ax_bot.plot(spread.index, spread, color=THEME['fg'], linewidth=1.5,
                label=f'SOFR-EFFR Spread ({spread.iloc[-1]:.0f} bps)')

    # Distress threshold
    ax_bot.axhline(15, color=COLORS['venus'], linewidth=1.5, linestyle='-', alpha=0.7,
                   label='Distress Threshold (15 bps)')
    ax_bot.axhline(0, color=COLORS['doldrums'], linewidth=0.8, linestyle='--', alpha=0.5)

    style_ax(ax_bot, right_primary=True)
    ax_bot.spines['top'].set_linewidth(4.0)
    ax_bot.tick_params(axis='both', which='both', length=0)
    ax_bot.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.0f}'))
    set_xlim_to_data(ax_bot, spread.index)
    ax_bot.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))

    # Custom spread pill
    last_spread = float(spread.iloc[-1])
    pill_color = c_normal if last_spread < 15 else c_stress
    pill = dict(boxstyle='round,pad=0.3', facecolor=pill_color, edgecolor=pill_color, alpha=0.95)
    ax_bot.annotate(f'{last_spread:.0f} bps', xy=(1.0, last_spread),
                    xycoords=('axes fraction', 'data'),
                    fontsize=9, fontweight='bold', color='white',
                    ha='left', va='center', xytext=(6, 0),
                    textcoords='offset points', bbox=pill)
    ax_bot.legend(loc='upper left', **legend_style())

    add_annotation_box(ax_top,
        f"Spread at ~{last_spread:.0f} bps. Below 15 = Defensive (not Disorderly).\n"
        f"The One Switch: when this breaks 15, everything changes.",
        x=0.62, y=0.35)

    brand_fig(fig, 'SOFR vs EFFR: The One Switch',
              subtitle='Defensive vs Disorderly: the plumbing signal that matters most',
              source='NY Fed, Federal Reserve',
              data_date=spread.index[-1])

    return save_fig(fig, 'chart_08_sofr_effr.png')


# ============================================
# CHART 9: Liquidity Cushion Index (LCI)
# ============================================
def chart_09():
    """Liquidity Cushion Index: approaching scarce regime."""
    print('\nChart 9: Liquidity Cushion Index...')

    lci_df = fetch_index('LCI', start='2010-01-01')
    lci_raw = lci_df['value'].dropna()
    lci_spot = lci_raw.iloc[-1]
    # Apply 3-month MA to smooth daily noise
    lci = lci_raw.rolling(63, min_periods=20).mean().dropna()

    fig, ax = new_fig()

    # Faint raw for context
    ax.plot(lci_raw.index, lci_raw, color=THEME['primary'], linewidth=0.4, alpha=0.25)
    ax.plot(lci.index, lci, color=THEME['primary'], linewidth=2.5,
            label=f'LCI 3M MA ({lci.iloc[-1]:.2f})')
    ax.fill_between(lci.index, lci, alpha=THEME['fill_alpha'] * 0.5,
                    color=THEME['primary'])
    # Mark latest spot reading
    ax.scatter([lci_raw.index[-1]], [lci_spot], color=COLORS['dusk'],
               s=60, zorder=5, label=f'Spot: {lci_spot:.2f}')

    # Regime thresholds
    ax.axhline(0.5, color=COLORS['sea'], linewidth=1.2, linestyle='-', alpha=0.6,
               label='Ample (+0.5)')
    ax.axhline(0, color=COLORS['doldrums'], linewidth=0.8, linestyle='--', alpha=0.5)
    ax.axhline(-0.5, color=COLORS['dusk'], linewidth=1.5, linestyle='-', alpha=0.8,
               label='Scarce Regime (-0.5)')
    ax.axhline(-1.0, color=COLORS['venus'], linewidth=1.5, linestyle='--', alpha=0.7,
               label='Stress (-1.0)')

    # Zone shading
    ax.axhspan(-0.5, -3.0, color=COLORS['dusk'], alpha=0.04)

    style_ax(ax, right_primary=True)
    ax.tick_params(axis='both', which='both', length=0)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.1f}'))
    set_xlim_to_data(ax, lci.index)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    add_last_value_label(ax, lci, color=THEME['primary'], fmt='{:.2f}', side='right')
    ax.legend(loc='upper left', **legend_style(), fontsize=9)

    lci_ma = lci.iloc[-1]
    add_annotation_box(ax,
        f"LCI spot: {lci_spot:.2f}, 3M MA: {lci_ma:.2f}.\n"
        f"Approaching -0.5 scarce regime. RRP exhausted.",
        x=0.62, y=0.92)

    brand_fig(fig, 'Liquidity Cushion Index (LCI)',
              subtitle='System shock absorption: approaching scarce',
              source='Lighthouse Macro Composite (Fed, OFR, NY Fed)',
              data_date=lci.index[-1])

    return save_fig(fig, 'chart_09_lci.png')


# ============================================
# CHART 10: Yield Curve + Term Premium (Steepener)
# ============================================
def chart_10():
    """10Y-2Y curve with steepener thesis building."""
    print('\nChart 10: Yield Curve...')

    t10y2y_raw = fetch_db_level('T10Y2Y', start='2000-01-01')
    t10y2y = t10y2y_raw * 100  # Convert pct pts to bps
    dgs10 = fetch_db_level('DGS10', start='2000-01-01')
    dgs2 = fetch_db_level('DGS2', start='2000-01-01')

    fig, ax1 = new_fig()
    ax2 = ax1.twinx()
    c1 = THEME['secondary']  # Spread on LHS
    c2 = THEME['primary']    # 10Y on RHS

    # LHS: 10Y-2Y Spread (in bps)
    ax1.plot(t10y2y.index, t10y2y, color=c1, linewidth=2.5,
             label=f'10Y-2Y Spread ({t10y2y.iloc[-1]:.0f} bps)')
    ax1.fill_between(t10y2y.index, 0, t10y2y,
                     where=(t10y2y >= 0),
                     color=COLORS['sea'], alpha=0.06)
    ax1.fill_between(t10y2y.index, 0, t10y2y,
                     where=(t10y2y < 0),
                     color=COLORS['venus'], alpha=0.06)

    # RHS: 10Y yield
    ax2.plot(dgs10.index, dgs10, color=c2, linewidth=2.0,
             label=f'10Y Yield ({dgs10.iloc[-1]:.2f}%)')

    ax1.axhline(0, color=COLORS['doldrums'], linewidth=1.0, linestyle='--', alpha=0.5)

    style_dual_ax(ax1, ax2, c1, c2)
    ax1.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.0f} bps'))
    ax2.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.1f}%'))
    set_xlim_to_data(ax1, t10y2y.index)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    add_last_value_label(ax1, t10y2y, color=c1, fmt='{:.0f} bps', side='left')
    add_last_value_label(ax2, dgs10, color=c2, fmt='{:.2f}%', side='right')
    add_recessions(ax1, start_date='2000-01-01')

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', **legend_style())

    spread_last = t10y2y.iloc[-1]
    y10_last = dgs10.iloc[-1]
    add_annotation_box(ax1,
        f"10Y at {y10_last:.2f}%, curve at +{spread_last:.0f} bps.\n"
        f"Term premium building. Steepener thesis accelerates above 4.60%.",
        x=0.62, y=0.92)

    brand_fig(fig, '10Y-2Y Yield Curve + 10Y Treasury',
              subtitle='The Steepener Building: term premium returns',
              source='Federal Reserve via FRED',
              data_date=t10y2y.index[-1])

    return save_fig(fig, 'chart_10_yield_curve.png')


# ============================================
# CHART 11: Macro Risk Index (MRI)
# ============================================
def chart_11():
    """MRI: master composite regime classification."""
    print('\nChart 11: Macro Risk Index...')

    mri_df = fetch_index('MRI', start='2000-01-01')
    mri_raw = mri_df['value'].dropna()
    mri_spot = mri_raw.iloc[-1]
    # Apply 3-month MA to smooth daily noise
    mri = mri_raw.rolling(63, min_periods=20).mean().dropna()

    fig, ax = new_fig()

    # Faint raw for context
    ax.plot(mri_raw.index, mri_raw, color=THEME['primary'], linewidth=0.4, alpha=0.25)
    ax.plot(mri.index, mri, color=THEME['primary'], linewidth=2.5,
            label=f'MRI 3M MA ({mri.iloc[-1]:.2f})')
    # Mark latest spot
    ax.scatter([mri_raw.index[-1]], [mri_spot], color=COLORS['dusk'],
               s=60, zorder=5, label=f'Spot: {mri_spot:.2f}')

    # Regime zone shading
    ax.axhspan(-3.0, -0.5, color=COLORS['sea'], alpha=0.05, label='Low Risk')
    ax.axhspan(-0.5, 0.5, color=COLORS['doldrums'], alpha=0.04, label='Neutral')
    ax.axhspan(0.5, 1.0, color=COLORS['dusk'], alpha=0.05, label='Elevated')
    ax.axhspan(1.0, 1.5, color=COLORS['venus'], alpha=0.05, label='High Risk')
    ax.axhspan(1.5, 3.0, color=COLORS['port'], alpha=0.05, label='Crisis')

    # Key thresholds
    ax.axhline(0.5, color=COLORS['dusk'], linewidth=1.0, linestyle='-', alpha=0.5)
    ax.axhline(1.0, color=COLORS['venus'], linewidth=1.0, linestyle='-', alpha=0.5)
    ax.axhline(-0.5, color=COLORS['sea'], linewidth=1.0, linestyle='-', alpha=0.5)
    ax.axhline(0, color=COLORS['doldrums'], linewidth=0.8, linestyle='--', alpha=0.5)

    style_ax(ax, right_primary=True)
    ax.tick_params(axis='both', which='both', length=0)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.1f}'))
    set_xlim_to_data(ax, mri.index)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    add_last_value_label(ax, mri, color=THEME['primary'], fmt='{:.2f}', side='right')
    add_recessions(ax, start_date='2000-01-01')

    # Simplified legend (too many entries from zone shading)
    ax.legend(loc='upper left', **legend_style(), fontsize=8, ncol=2)

    mri_last = mri.iloc[-1]
    if mri_last < -0.5:
        regime = "Low Risk"
    elif mri_last < 0.5:
        regime = "Neutral"
    elif mri_last < 1.0:
        regime = "Elevated"
    elif mri_last < 1.5:
        regime = "High Risk"
    else:
        regime = "Crisis"

    add_annotation_box(ax,
        f"MRI spot: {mri_spot:+.2f}, 3M MA: {mri_last:+.2f} ({regime}).\n"
        f"Ticking down as tariff pressure releases.\n"
        f"Defensive posture holds. Labor is the binding constraint.",
        x=0.62, y=0.15)

    brand_fig(fig, 'Macro Risk Index (MRI)',
              subtitle='Master Composite: 12 pillars, one number',
              source='Lighthouse Macro Composite',
              data_date=mri.index[-1])

    return save_fig(fig, 'chart_11_mri.png')


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
}


def main():
    parser = argparse.ArgumentParser(description='Generate Positioning Update #2 charts')
    parser.add_argument('--chart', type=int, help='Chart number to generate (1-11)')
    parser.add_argument('--theme', default='both', choices=['dark', 'white', 'both'],
                        help='Theme to generate')
    parser.add_argument('--all', action='store_true', help='Generate all charts')
    args = parser.parse_args()

    if args.all:
        charts_to_gen = sorted(CHART_MAP.keys())
    elif args.chart:
        charts_to_gen = [args.chart]
    else:
        charts_to_gen = sorted(CHART_MAP.keys())

    themes_to_gen = ['dark', 'white'] if args.theme == 'both' else [args.theme]

    for mode in themes_to_gen:
        set_theme(mode)
        print(f'\n=== Generating {mode.upper()} theme ===')
        for chart_num in charts_to_gen:
            if chart_num not in CHART_MAP:
                print(f'Chart {chart_num} not implemented.')
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
