#!/usr/bin/env python3
"""
Generate Charts for Educational Series: Post 2 - Prices
========================================================
Generates BOTH white and dark theme versions.
Matches format from Labor: THE SOURCE CODE charts.

Usage:
    python prices_edu_charts.py --chart 1
    python prices_edu_charts.py --chart 1 --theme dark
    python prices_edu_charts.py --all
"""

import os
import argparse
from datetime import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
import matplotlib.image as mpimg
from matplotlib.ticker import FuncFormatter
from fredapi import Fred

# ============================================
# PATHS & CONFIG
# ============================================
BASE_PATH = '/Users/bob/LHM'
OUTPUT_BASE = f'{BASE_PATH}/Outputs/Educational_Charts/Prices_Post_2'
DB_PATH = f'{BASE_PATH}/Data/databases/Lighthouse_Master.db'
ICON_PATH = f'{BASE_PATH}/Brand/icon_transparent_128.png'

fred = Fred()

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
            'brand_color': COLORS['sky'],
            'brand2_color': COLORS['dusk'],
            'primary': COLORS['sky'],
            'secondary': COLORS['dusk'],
            'tertiary': COLORS['sea'],
            'accent': COLORS['venus'],
            'fill_alpha': 0.20,
            'box_bg': '#0A1628',
            'box_edge': COLORS['sky'],
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
            'brand_color': COLORS['ocean'],
            'brand2_color': COLORS['dusk'],
            'primary': COLORS['ocean'],
            'secondary': COLORS['dusk'],
            'tertiary': COLORS['sea'],
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
    """Fetch a FRED series and return as DataFrame."""
    s = fred.get_series(series_id, observation_start=start)
    df = s.to_frame(name='value')
    df.index.name = 'date'
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


def target_zscore(series, target=2.0, scale=1.0):
    """Z-score relative to a fixed target level.
    Returns how far above/below the target, normalized by scale.
    scale controls sensitivity: smaller = more sensitive."""
    return (series - target) / scale


# ============================================
# CHART STYLING HELPERS (matching labor format)
# ============================================
def new_fig(figsize=(14, 8)):
    """Create figure with theme background. Reserves space for TT deck branding."""
    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_facecolor(THEME['bg'])
    ax.set_facecolor(THEME['bg'])
    # Reserve margins: top for brand/title/subtitle, bottom for accent bar/source
    # Extra right/left margin so end-of-line pills have room outside spines
    fig.subplots_adjust(top=0.88, bottom=0.08, left=0.06, right=0.94)
    return fig, ax


def style_dual_ax(ax1, ax2, c1, c2):
    """Apply full styling to a dual-axis chart: spines, tick colors, no tick marks, formatters."""
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
    """Apply full styling to a single-axis chart: spines, ticks on RHS, no tick marks."""
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

    # Top-left watermark
    fig.text(0.035, 0.98, 'LIGHTHOUSE MACRO', fontsize=13,
             color=OCEAN, fontweight='bold', va='top')

    # Date top-right
    fig.text(0.97, 0.98, datetime.now().strftime('%B %d, %Y'),
             fontsize=11, color=THEME['muted'], ha='right', va='top')

    # Top accent bar: ocean 2/3, dusk 1/3
    bar = fig.add_axes([0.03, 0.955, 0.94, 0.004])
    bar.axhspan(0, 1, 0, 0.67, color=OCEAN)
    bar.axhspan(0, 1, 0.67, 1.0, color=DUSK)
    bar.set_xlim(0, 1); bar.set_ylim(0, 1); bar.axis('off')

    # Bottom accent bar: mirror of top
    bbar = fig.add_axes([0.03, 0.035, 0.94, 0.004])
    bbar.axhspan(0, 1, 0, 0.67, color=OCEAN)
    bbar.axhspan(0, 1, 0.67, 1.0, color=DUSK)
    bbar.set_xlim(0, 1); bbar.set_ylim(0, 1); bbar.axis('off')

    # Bottom-right watermark
    fig.text(0.97, 0.025, 'MACRO, ILLUMINATED.', fontsize=13,
             color=OCEAN, ha='right', va='top', style='italic', fontweight='bold')

    # Source line bottom-left
    if source:
        date_str = datetime.now().strftime('%m.%d.%Y')
        fig.text(0.03, 0.022, f'Lighthouse Macro | {source}; {date_str}',
                 fontsize=9, color=THEME['muted'], ha='left', va='top', style='italic')

    # Title and subtitle
    fig.suptitle(title, fontsize=15, fontweight='bold', y=0.945,
                 color=THEME['fg'])
    if subtitle:
        fig.text(0.5, 0.895, subtitle, fontsize=14, ha='center',
                 color=OCEAN, style='italic')


def add_last_value_label(ax, y_data, color, fmt='{:.1f}%', side='right', fontsize=9, pad=0.3):
    """Add colored pill with bold white text on the axis edge.
    side='right' places on RHS spine, side='left' places on LHS spine.
    """
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
    """Set x limits. Extra right padding so lines end well before the right spine."""
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
    # Add outer border at absolute figure edge (Ocean for white, Sky for dark)
    border_color = THEME['primary']
    fig.patches.append(plt.Rectangle(
        (0, 0), 1, 1, transform=fig.transFigure,
        fill=False, edgecolor=border_color, linewidth=1.5,
        zorder=100, clip_on=False
    ))

    filepath = os.path.join(OUTPUT_DIR, filename)
    fig.savefig(filepath, dpi=200, bbox_inches='tight', pad_inches=0.15,
                facecolor=THEME['bg'], edgecolor='none')
    plt.close(fig)
    print(f'  Saved: {filepath}')
    return filepath


# ============================================
# CHART 1: Goods vs Services CPI YoY
# ============================================
def chart_01():
    """The Great Divergence: Core Goods vs Core Services CPI YoY (dual axis, same scale)."""
    print('\nChart 1: Goods vs Services CPI YoY...')

    # Fetch SA index levels from FRED
    goods = fetch_fred('CUSR0000SACL1E', start='1999-01-01')
    services = fetch_fred('CUSR0000SASLE', start='1999-01-01')

    goods['yoy'] = yoy_pct(goods)
    services['yoy'] = yoy_pct(services)

    # Trim to 2000+
    goods = goods.loc['2000-01-01':]
    services = services.loc['2000-01-01':]

    fig, ax1 = new_fig()
    ax2 = ax1.twinx()

    c_primary = THEME['primary']    # RHS = blue
    c_secondary = THEME['secondary']  # LHS = orange

    # Drop NaN before plotting so line doesn't break at gaps
    g_plot = goods['yoy'].dropna()
    s_plot = services['yoy'].dropna()

    # Goods on LHS (secondary/orange), Services on RHS (primary/blue)
    ax1.plot(g_plot.index, g_plot, color=c_secondary, linewidth=2.5,
             label=f'Core Goods CPI ({g_plot.iloc[-1]:.1f}%)')
    ax2.plot(s_plot.index, s_plot, color=c_primary, linewidth=2.5,
             label=f'Core Services CPI ({s_plot.iloc[-1]:.1f}%)')

    # Zero line and 2% target
    ax1.axhline(0, color=COLORS['doldrums'], linewidth=0.8, alpha=0.5, linestyle='--')
    ax1.axhline(2.0, color=COLORS['venus'], linewidth=0.8, alpha=0.5, linestyle='--')

    # Same scale, aligned at zero
    g_data = goods['yoy'].dropna()
    s_data = services['yoy'].dropna()
    all_min = min(g_data.min(), s_data.min())
    all_max = max(g_data.max(), s_data.max())
    pad = (all_max - all_min) * 0.08
    y_lo, y_hi = all_min - pad, all_max + pad

    ax1.set_ylim(y_lo, y_hi)
    ax2.set_ylim(y_lo, y_hi)

    # Style axes
    style_ax(ax1, right_primary=False)
    ax1.grid(False)
    ax2.grid(False)
    for spine in ax2.spines.values():
        spine.set_color(THEME['spine'])
        spine.set_linewidth(0.5)

    # Kill ALL tick marks on both axes (major + minor, both sides)
    ax1.tick_params(axis='both', which='both', length=0)
    ax1.tick_params(axis='y', labelcolor=c_secondary, labelsize=10)
    ax1.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.0f}%'))

    ax2.tick_params(axis='both', which='both', length=0)
    ax2.tick_params(axis='y', labelcolor=c_primary, labelsize=10)
    ax2.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.0f}%'))

    # Also kill any secondary tick marks ax1 might draw on right via twinx
    ax1.yaxis.set_tick_params(which='both', right=False)
    ax2.yaxis.set_tick_params(which='both', left=False)

    set_xlim_to_data(ax1, goods.index)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    # Last value labels: goods on LHS (orange), services on RHS (blue)
    add_last_value_label(ax1, g_data, color=c_secondary, side='left')
    add_last_value_label(ax2, s_data, color=c_primary, side='right')

    # Recession shading
    add_recessions(ax1)

    # Combined legend
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', **legend_style())

    # Label the 2% target line
    ax1.text(0.02, 2.15, '2% Target', fontsize=8, color=COLORS['venus'],
             alpha=0.7, style='italic', transform=ax1.get_yaxis_transform())

    # Annotation box — dynamic takeaway
    g_last = g_data.iloc[-1]
    s_last = s_data.iloc[-1]
    spread = s_last - g_last
    takeaway = f"Goods-services spread: {spread:.1f} ppts.\nThe last mile is a services problem."
    ax1.text(0.52, 0.92, takeaway, transform=ax1.transAxes,
             fontsize=10, color=THEME['fg'], ha='center', va='top',
             style='italic',
             bbox=dict(boxstyle='round,pad=0.5',
                       facecolor=THEME['bg'], edgecolor='#2389BB',
                       alpha=0.9))

    # TT deck branding at figure level
    g_sub = "deflating" if g_data.iloc[-1] < 0 else "subdued" if g_data.iloc[-1] < 2 else "rising"
    brand_fig(fig, 'The Great Divergence: Core Goods vs Core Services',
              subtitle=f'Goods {g_sub} while services remain sticky',
              source='BLS CPI')

    return save_fig(fig, 'chart_01_goods_vs_services.png')


# ============================================
# CHART 2: Headline CPI vs Core PCE YoY
# ============================================
def chart_02():
    """Headline CPI vs Core PCE: The Gap That Matters."""
    print('\nChart 2: Headline CPI vs Core PCE...')

    cpi = fetch_fred_yoy('CPIAUCSL')
    pce = fetch_fred_yoy('PCEPILFE')

    fig, ax1 = new_fig()
    ax2 = ax1.twinx()
    c_primary, c_secondary = THEME['primary'], THEME['secondary']

    # CPI on LHS (secondary/orange), Core PCE on RHS (primary/blue)
    ax1.plot(cpi.index, cpi, color=c_secondary, linewidth=2.5, label=f'Headline CPI YoY ({cpi.iloc[-1]:.1f}%)')
    ax2.plot(pce.index, pce, color=c_primary, linewidth=2.5, label=f'Core PCE YoY ({pce.iloc[-1]:.1f}%)')

    ax1.axhline(2.0, color=COLORS['venus'], linewidth=0.8, alpha=0.5, linestyle='--')
    ax1.axhline(0, color=COLORS['doldrums'], linewidth=0.8, alpha=0.5, linestyle='--')

    # Label the 2% target line
    ax1.text(0.02, 2.15, '2% Target', fontsize=8, color=COLORS['venus'],
             alpha=0.7, style='italic', transform=ax1.get_yaxis_transform())

    # Same scale
    all_min = min(cpi.min(), pce.min())
    all_max = max(cpi.max(), pce.max())
    pad = (all_max - all_min) * 0.08
    ax1.set_ylim(all_min - pad, all_max + pad)
    ax2.set_ylim(all_min - pad, all_max + pad)

    style_dual_ax(ax1, ax2, c_secondary, c_primary)
    set_xlim_to_data(ax1, cpi.index)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    add_last_value_label(ax1, cpi, color=c_secondary, side='left')
    add_last_value_label(ax2, pce, color=c_primary, side='right')

    add_recessions(ax1)

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', **legend_style())

    pce_last = pce.iloc[-1]
    pce_above = ((pce_last / 2.0) - 1) * 100
    add_annotation_box(ax1,
        f"The Fed targets Core PCE, not headline CPI.\nAt {pce_last:.1f}%, we're {pce_above:.0f}% above the 2% goal.",
        x=0.50, y=0.92)

    brand_fig(fig, 'Headline CPI vs Core PCE: The Gap That Matters',
              subtitle='The number the Fed actually watches',
              source='BLS, BEA')

    return save_fig(fig, 'chart_02_headline_vs_core.png')


# ============================================
# CHART 3: The Shelter Lag Trap
# ============================================
def chart_03():
    """Shelter CPI, Rent CPI, OER YoY — the mechanical lag."""
    print('\nChart 3: Shelter Lag Trap...')

    shelter = fetch_fred_yoy('CUSR0000SAH1')
    rent = fetch_fred_yoy('CUSR0000SEHA')
    oer = fetch_fred_yoy('CUSR0000SEHC')

    fig, ax = new_fig()
    c1, c2, c3 = THEME['primary'], THEME['secondary'], THEME['tertiary']

    ax.plot(shelter.index, shelter, color=c1, linewidth=2.5, label=f'Shelter CPI ({shelter.iloc[-1]:.1f}%)')
    ax.plot(rent.index, rent, color=c2, linewidth=2.5, label=f'Rent of Primary Residence ({rent.iloc[-1]:.1f}%)')
    ax.plot(oer.index, oer, color=c3, linewidth=2.5, label=f"Owners' Equivalent Rent ({oer.iloc[-1]:.1f}%)")

    ax.axhline(0, color=COLORS['doldrums'], linewidth=0.8, alpha=0.5, linestyle='--')
    ax.axhline(2.0, color=COLORS['venus'], linewidth=0.8, alpha=0.5, linestyle='--')
    ax.text(0.02, 2.15, '2% Target', fontsize=8, color=COLORS['venus'],
            alpha=0.7, style='italic', transform=ax.get_yaxis_transform())

    style_single_ax(ax)
    ax.tick_params(axis='both', which='both', length=0)
    set_xlim_to_data(ax, shelter.index)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    add_last_value_label(ax, shelter, color=c1, side='right', fontsize=7, pad=0.2)
    add_last_value_label(ax, rent, color=c2, side='right', fontsize=7, pad=0.2)
    add_last_value_label(ax, oer, color=c3, side='right', fontsize=7, pad=0.2)

    add_recessions(ax)
    ax.legend(loc='upper left', **legend_style())

    add_annotation_box(ax,
        f"Shelter = 34% of CPI weight.\nThe lag is mechanical, the decline is baked in.",
        x=0.50, y=0.92)

    brand_fig(fig, 'The Shelter Lag Trap',
              subtitle='Market rents lead CPI shelter by 12-18 months',
              source='BLS CPI')

    return save_fig(fig, 'chart_03_shelter_lag.png')


# ============================================
# CHART 4: Sticky vs Flexible CPI
# ============================================
def chart_04():
    """Atlanta Fed Sticky vs Flexible CPI — shifted 12 months to show lead relationship."""
    print('\nChart 4: Sticky vs Flexible CPI (shifted 12mo)...')

    # These are 12M trimmed-mean annualized rates from Atlanta Fed
    sticky = fetch_fred_level('CORESTICKM159SFRBATL', start='1999-01-01')
    flexible = fetch_fred_level('COREFLEXCPIM159SFRBATL', start='1999-01-01')

    # Trim to 2000+
    sticky = sticky.loc['2000-01-01':]
    flexible = flexible.loc['2000-01-01':]

    # Shift sticky backward 12 months to show flexible's lead visually
    sticky_plot = sticky.copy()
    sticky_plot.index = sticky_plot.index - pd.DateOffset(months=12)
    sticky_label = f'Sticky CPI (shifted -12mo, {sticky.iloc[-1]:.1f}%)'
    flexible_plot = flexible
    flex_label = f'Flexible CPI ({flexible.iloc[-1]:.1f}%)'

    fig, ax1 = new_fig()
    ax2 = ax1.twinx()
    c_primary, c_secondary = THEME['primary'], THEME['secondary']

    # Flexible on LHS (secondary/orange), Sticky on RHS (primary/blue) — sticky is the story
    ax1.plot(flexible_plot.index, flexible_plot, color=c_secondary, linewidth=2.5, label=flex_label)
    ax2.plot(sticky_plot.index, sticky_plot, color=c_primary, linewidth=2.5, label=sticky_label)

    ax1.axhline(0, color=THEME['muted'], linewidth=0.8, alpha=0.5, linestyle='--')

    # Data-driven ranges
    f_pad = (flexible_plot.max() - flexible_plot.min()) * 0.08
    s_pad = (sticky_plot.max() - sticky_plot.min()) * 0.08
    ax1.set_ylim(flexible_plot.min() - f_pad, flexible_plot.max() + f_pad)
    ax2.set_ylim(sticky_plot.min() - s_pad, sticky_plot.max() + s_pad)

    style_dual_ax(ax1, ax2, c_secondary, c_primary)
    set_xlim_to_data(ax1, flexible_plot.index)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    add_last_value_label(ax1, flexible_plot, color=c_secondary, side='left')
    add_last_value_label(ax2, sticky_plot, color=c_primary, side='right')

    add_recessions(ax1)

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', **legend_style())

    add_annotation_box(ax1,
        f"Flexible inflation normalized.\nSticky at {sticky.iloc[-1]:.1f}% is {sticky.iloc[-1]/2:.1f}x the target.",
        x=0.50, y=0.92)

    brand_fig(fig, 'Sticky vs Flexible: The Persistence Problem',
              subtitle='Flexible leads Sticky by ~12 months',
              source='Atlanta Fed')

    return save_fig(fig, 'chart_04_sticky_vs_flexible.png')


# ============================================
# CHART 5: PPI Leads CPI
# ============================================
def chart_05():
    """PPI Final Demand vs CPI YoY — the pipeline signal."""
    print('\nChart 5: PPI vs CPI...')

    ppi = fetch_fred_yoy('PPIFIS')
    cpi = fetch_fred_yoy('CPIAUCSL')

    fig, ax1 = new_fig()
    ax2 = ax1.twinx()
    c_primary, c_secondary = THEME['primary'], THEME['secondary']

    # CPI on LHS (secondary/orange), PPI on RHS (primary/blue) — PPI is the leading signal
    ax1.plot(cpi.index, cpi, color=c_secondary, linewidth=2.5, label=f'CPI YoY ({cpi.iloc[-1]:.1f}%)')
    ax2.plot(ppi.index, ppi, color=c_primary, linewidth=2.5, label=f'PPI Final Demand YoY ({ppi.iloc[-1]:.1f}%)')

    ax1.axhline(0, color=COLORS['doldrums'], linewidth=0.8, alpha=0.5, linestyle='--')
    ax1.axhline(2.0, color=COLORS['venus'], linewidth=0.8, alpha=0.5, linestyle='--')
    ax1.text(0.02, 2.15, '2% Target', fontsize=8, color=COLORS['venus'],
             alpha=0.7, style='italic', transform=ax1.get_yaxis_transform())

    # Same scale
    all_min = min(ppi.min(), cpi.min())
    all_max = max(ppi.max(), cpi.max())
    pad = (all_max - all_min) * 0.08
    ax1.set_ylim(all_min - pad, all_max + pad)
    ax2.set_ylim(all_min - pad, all_max + pad)

    style_dual_ax(ax1, ax2, c_secondary, c_primary)
    set_xlim_to_data(ax1, ppi.index)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    add_last_value_label(ax1, cpi, color=c_secondary, side='left')
    add_last_value_label(ax2, ppi, color=c_primary, side='right')

    add_recessions(ax1)

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', **legend_style())

    ppi_last, cpi_last = ppi.iloc[-1], cpi.iloc[-1]
    ppi_vs = "below" if ppi_last < cpi_last else "above"
    add_annotation_box(ax1,
        f"PPI ({ppi_last:.1f}%) {ppi_vs} CPI ({cpi_last:.1f}%) = {'dis' if ppi_last < cpi_last else ''}inflationary\npressure in the pipeline. Pass-through takes 3-6 months.",
        x=0.50, y=0.92)

    brand_fig(fig, 'The Pipeline: PPI Leads CPI',
              subtitle='Producer prices signal what consumer prices do next',
              source='BLS PPI, CPI')

    return save_fig(fig, 'chart_05_ppi_leads_cpi.png')


# ============================================
# CHART 6: Inflation Expectations
# ============================================
def chart_06():
    """5Y5Y Forward vs UMich 1Y — anchoring test."""
    print('\nChart 6: Inflation Expectations...')

    fwd_raw = fetch_fred_level('T5YIFR', start='2003-01-01')
    fwd = fwd_raw.rolling(20, min_periods=5).mean().dropna()  # Smooth daily noise
    umich = fetch_fred_level('MICH', start='2003-01-01')

    fig, ax1 = new_fig()
    ax2 = ax1.twinx()
    c_primary, c_secondary = THEME['primary'], THEME['secondary']

    # Smooth UMich with 3-month MA to reduce noise
    umich_smooth = umich.rolling(3, min_periods=1).mean()

    # UMich on LHS (secondary/orange), 5Y5Y on RHS (primary/blue) — 5Y5Y is the anchoring signal
    ax1.plot(umich_smooth.index, umich_smooth, color=c_secondary, linewidth=2.5, label=f'UMich 1Y Expectations, 3mMA ({umich_smooth.iloc[-1]:.1f}%)')
    ax2.plot(fwd.index, fwd, color=c_primary, linewidth=2.5, label=f'5Y5Y Forward ({fwd.iloc[-1]:.1f}%)')

    # 2% target line and 3% danger zone on RHS scale (5Y5Y)
    ax2.axhline(2.0, color=COLORS['venus'], linewidth=0.8, alpha=0.5, linestyle='--')
    ax2.axhline(3.0, color=COLORS['sea'], linewidth=0.8, alpha=0.5, linestyle='--')
    ax2.text(1.01, 2.05, '2% Target', fontsize=8, color=COLORS['venus'],
             alpha=0.7, style='italic', transform=ax2.get_yaxis_transform(), ha='left')
    ax2.text(1.01, 3.05, '3% Danger', fontsize=8, color=COLORS['sea'],
             alpha=0.7, style='italic', transform=ax2.get_yaxis_transform(), ha='left')

    # Independent scales — these series have very different ranges
    style_dual_ax(ax1, ax2, c_secondary, c_primary)
    set_xlim_to_data(ax1, fwd.index)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    add_last_value_label(ax1, umich_smooth, color=c_secondary, side='left')
    add_last_value_label(ax2, fwd, color=c_primary, side='right')

    add_recessions(ax1, start_date='2003-01-01')

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', **legend_style())

    add_annotation_box(ax1,
        f"5Y5Y at {fwd.iloc[-1]:.2f}%: {'drifting, not de-anchored' if fwd.iloc[-1] < 3.0 else 'de-anchoring risk'}.\nIf this breaks 3%, all bets are off.",
        x=0.50, y=0.12)

    brand_fig(fig, 'Inflation Expectations: Are They Anchored?',
              subtitle='The line between controlled and uncontrolled inflation',
              source='FRED, UMich')

    return save_fig(fig, 'chart_06_expectations.png')


# ============================================
# CHART 7: Trimmed Mean vs Core PCE
# ============================================
def chart_07():
    """Dallas Fed Trimmed Mean PCE vs Core PCE — signal beneath noise."""
    print('\nChart 7: Trimmed Mean vs Core PCE...')

    trimmed = fetch_fred_level('PCETRIM12M159SFRBDAL', start='2000-01-01')
    core_pce = fetch_fred_yoy('PCEPILFE')

    fig, ax1 = new_fig()
    ax2 = ax1.twinx()
    c_primary, c_secondary = THEME['primary'], THEME['secondary']

    # Core PCE on LHS (secondary/orange), Trimmed Mean on RHS (primary/blue)
    ax1.plot(core_pce.index, core_pce, color=c_secondary, linewidth=2.5, label=f'Core PCE YoY ({core_pce.iloc[-1]:.1f}%)')
    ax2.plot(trimmed.index, trimmed, color=c_primary, linewidth=2.5, label=f'Trimmed Mean PCE 12M ({trimmed.iloc[-1]:.1f}%)')

    ax1.axhline(2.0, color=COLORS['venus'], linewidth=0.8, alpha=0.5, linestyle='--')
    ax1.axhline(0, color=COLORS['doldrums'], linewidth=0.8, alpha=0.5, linestyle='--')
    ax1.text(0.02, 2.15, '2% Target', fontsize=8, color=COLORS['venus'],
             alpha=0.7, style='italic', transform=ax1.get_yaxis_transform())

    # Same scale
    all_min = min(trimmed.min(), core_pce.min())
    all_max = max(trimmed.max(), core_pce.max())
    pad = (all_max - all_min) * 0.08
    ax1.set_ylim(all_min - pad, all_max + pad)
    ax2.set_ylim(all_min - pad, all_max + pad)

    style_dual_ax(ax1, ax2, c_secondary, c_primary)
    set_xlim_to_data(ax1, trimmed.index)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    add_last_value_label(ax1, core_pce, color=c_secondary, side='left')
    add_last_value_label(ax2, trimmed, color=c_primary, side='right')

    add_recessions(ax1)

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', **legend_style())

    add_annotation_box(ax1,
        f"Trimmed mean strips the noise.\nAt {trimmed.iloc[-1]:.1f}%, the stickiness is broad-based.",
        x=0.45, y=0.92)

    brand_fig(fig, 'Trimmed Mean vs Core: The Signal Beneath the Noise',
              subtitle='Dallas Fed trimmed mean confirms persistent inflation',
              source='Dallas Fed, BEA')

    return save_fig(fig, 'chart_07_trimmed_mean.png')


# ============================================
# CHART 8: Wages vs Prices (ECI vs Core PCE)
# ============================================
def chart_08():
    """ECI Total Compensation vs Core PCE — wage-price spiral check."""
    print('\nChart 8: ECI vs Core PCE...')

    eci = fetch_quarterly_as_monthly('ECIALLCIV')
    core_pce = fetch_fred_yoy('PCEPILFE')

    fig, ax1 = new_fig()
    ax2 = ax1.twinx()
    c_primary, c_secondary = THEME['primary'], THEME['secondary']

    # Core PCE on LHS (secondary/orange), ECI on RHS (primary/blue) — wages are the story
    ax1.plot(core_pce.index, core_pce, color=c_secondary, linewidth=2.5, label=f'Core PCE YoY ({core_pce.iloc[-1]:.1f}%)')
    ax2.plot(eci.index, eci, color=c_primary, linewidth=2.5, label=f'ECI Total Compensation YoY ({eci.iloc[-1]:.1f}%)')

    ax1.axhline(2.0, color=COLORS['venus'], linewidth=0.8, alpha=0.5, linestyle='--')
    ax1.axhline(0, color=COLORS['doldrums'], linewidth=0.8, alpha=0.5, linestyle='--')
    ax1.text(0.02, 2.15, '2% Target', fontsize=8, color=COLORS['venus'],
             alpha=0.7, style='italic', transform=ax1.get_yaxis_transform())

    # Same scale
    all_min = min(eci.min(), core_pce.min())
    all_max = max(eci.max(), core_pce.max())
    pad = (all_max - all_min) * 0.08
    ax1.set_ylim(all_min - pad, all_max + pad)
    ax2.set_ylim(all_min - pad, all_max + pad)

    style_dual_ax(ax1, ax2, c_secondary, c_primary)
    set_xlim_to_data(ax1, eci.index)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    add_last_value_label(ax1, core_pce, color=c_secondary, side='left')
    add_last_value_label(ax2, eci, color=c_primary, side='right')

    add_recessions(ax1)

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', **legend_style())

    eci_last, pce_last = eci.iloc[-1], core_pce.iloc[-1]
    spiral_status = "No wage-price spiral." if eci_last > pce_last else "Wages falling behind prices."
    add_annotation_box(ax1,
        f"{spiral_status} ECI at {eci_last:.1f}% vs Core PCE\nat {pce_last:.1f}%. Equilibrium, not resolution.",
        x=0.50, y=0.92)

    brand_fig(fig, 'Wages vs Prices: The Spiral Check',
              subtitle='ECI compensation growth vs core inflation',
              source='BLS ECI, BEA')

    return save_fig(fig, 'chart_08_wages_vs_prices.png')


# ============================================
# CHART 9: Dollar Channel — Goods Deflation
# ============================================
def _chart_09_core(shifted=False):
    """Dollar vs Goods CPI — shared logic for shifted/unshifted."""

    dollar = fetch_fred_level('DTWEXBGS', start='1999-01-01')
    goods = fetch_fred_yoy('CUSR0000SACL1E')

    # Resample daily dollar to monthly, then compute YoY, then 3mMA
    dollar_monthly = dollar.resample('MS').mean()
    dollar_yoy_raw = dollar_monthly.pct_change(12) * 100
    dollar_yoy = dollar_yoy_raw.rolling(3, min_periods=1).mean()
    dollar_yoy = dollar_yoy.dropna()
    dollar_yoy = dollar_yoy.loc['2000-01-01':]

    inv_dollar_plot = -dollar_yoy

    if shifted:
        # Shift goods backward 18 months to show dollar's lead
        goods_plot = goods.copy()
        goods_plot.index = goods_plot.index - pd.DateOffset(months=18)
        goods_label = f'Core Goods CPI YoY (shifted -18mo, {goods.iloc[-1]:.1f}%)'
        subtitle = 'Dollar leads goods inflation by ~18 months'
        filename = 'chart_09_dollar_goods.png'
    else:
        goods_plot = goods
        goods_label = f'Core Goods CPI YoY ({goods.iloc[-1]:.1f}%)'
        subtitle = 'Trade-weighted dollar (inverted) vs core goods CPI'
        filename = 'chart_09_dollar_goods.png'

    fig, ax1 = new_fig()
    ax2 = ax1.twinx()
    c_primary, c_secondary = THEME['primary'], THEME['secondary']

    # Dollar (inverted) on LHS (secondary/orange), Goods CPI on RHS (primary/blue)
    ax1.plot(dollar_yoy.index, inv_dollar_plot, color=c_secondary, linewidth=2.5,
             label=f'Dollar YoY % (inverted, {inv_dollar_plot.iloc[-1]:.1f}%)')
    ax2.plot(goods_plot.index, goods_plot, color=c_primary, linewidth=2.5,
             label=goods_label)

    ax1.axhline(0, color=THEME['muted'], linewidth=0.8, alpha=0.5, linestyle='--')

    # Scale axes so visual amplitudes align: ~3:1 ratio dollar-to-goods
    ax1.set_ylim(-15, 10)
    ax2.set_ylim(-5, 14)

    style_dual_ax(ax1, ax2, c_secondary, c_primary)
    set_xlim_to_data(ax1, inv_dollar_plot.index)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    add_last_value_label(ax1, inv_dollar_plot, color=c_secondary, side='left')
    add_last_value_label(ax2, goods_plot, color=c_primary, side='right')

    add_recessions(ax1)

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', **legend_style())

    dollar_dir = "Strong" if dollar_yoy.iloc[-1] > 0 else "Weak"
    goods_dir = "deflation" if goods.iloc[-1] < 0 else "inflation"
    add_annotation_box(ax1,
        f"{dollar_dir} dollar ({dollar_yoy.iloc[-1]:.1f}% YoY) \u2192 goods {goods_dir}.\nThe 9-18 month lag is mechanical.",
        x=0.50, y=0.92)

    goods_title_word = "Deflation" if goods.iloc[-1] < 0 else "Disinflation"
    brand_fig(fig, f'The Dollar Channel: Goods {goods_title_word} Explained',
              subtitle=subtitle,
              source='FRED, BLS')

    return save_fig(fig, filename)


def chart_09():
    """Chart 9: shifted only."""
    print('\nChart 9: Dollar vs Goods CPI (shifted)...')
    return _chart_09_core(shifted=True)


# ============================================
# CHART 10: PCI Composite with Regime Bands
# ============================================
def chart_10():
    """Prices Composite Index (PCI) with regime bands."""
    print('\nChart 10: PCI Composite...')

    # Fetch components
    core_pce_idx = fetch_fred('PCEPILFE', start='1995-01-01')
    core_pce_idx['yoy'] = yoy_pct(core_pce_idx)
    # 3M annualized
    core_pce_idx['mom'] = core_pce_idx['value'].pct_change(1, fill_method=None)
    core_pce_idx['ann3m'] = (((1 + core_pce_idx['mom']).rolling(3).apply(
        lambda x: x.prod(), raw=True)) ** 4 - 1) * 100

    shelter = fetch_fred('CUSR0000SAH1', start='1995-01-01')
    shelter['yoy'] = yoy_pct(shelter)

    sticky = fetch_fred_level('CORESTICKM159SFRBATL', start='1995-01-01')

    fwd5y5y = fetch_fred_level('T5YIFR', start='2003-01-01')

    goods = fetch_fred('CUSR0000SACL1E', start='1995-01-01')
    goods['yoy'] = yoy_pct(goods)

    # Services ex-shelter proxy: use supercore
    # CUSR0000SASLE (services) minus shelter contribution approximation
    # Simpler: use core services as proxy since we don't have clean ex-shelter
    services = fetch_fred('CUSR0000SASLE', start='1995-01-01')
    services['yoy'] = yoy_pct(services)

    # Align all to common date range
    start_date = '2004-01-01'  # 5Y5Y starts 2003, need buffer for z-scores

    # Build DataFrame
    pci_df = pd.DataFrame({
        'core_pce_3m': core_pce_idx['ann3m'],
        'services_yoy': services['yoy'],
        'shelter_yoy': shelter['yoy'],
        'sticky': sticky,
        'fwd5y5y': fwd5y5y,
        'goods_yoy': goods['yoy'],
    })
    pci_df = pci_df.loc[start_date:].dropna()

    # Target-based z-scores: measure distance from Fed-consistent targets
    # Scale calibrated so 1.0 = meaningfully above target
    # Core PCE 3m ann: target 2%, scale 1.5 (volatile, wider band)
    # Services YoY: target 2.5% (Fed-consistent), scale 1.5
    # Shelter YoY: target 2.5% (Fed-consistent), scale 1.5
    # Sticky CPI: target 2.5% (Fed-consistent), scale 1.0
    # 5Y5Y fwd: target 2.25% (anchored expectations), scale 0.3 (small moves matter)
    # Goods YoY: target 0% (goods should be flat/deflating), scale 1.5
    z_core = target_zscore(pci_df['core_pce_3m'], target=2.0, scale=1.5)
    z_svc = target_zscore(pci_df['services_yoy'], target=2.5, scale=1.5)
    z_shelter = target_zscore(pci_df['shelter_yoy'], target=2.5, scale=1.5)
    z_sticky = target_zscore(pci_df['sticky'], target=2.5, scale=1.0)
    z_fwd = target_zscore(pci_df['fwd5y5y'], target=2.25, scale=0.3)
    z_goods = target_zscore(pci_df['goods_yoy'], target=0.0, scale=1.5)

    # PCI formula: positive = inflationary, negative = deflationary
    # Goods inverted: positive goods inflation is inflationary
    pci = (0.30 * z_core + 0.20 * z_svc + 0.15 * z_shelter
           + 0.15 * z_sticky + 0.10 * z_fwd + 0.10 * z_goods)
    pci = pci.dropna()

    fig, ax = new_fig()
    c1 = THEME['primary']

    # Regime bands — bright and visible
    ax.axhspan(1.5, 3.0, color=COLORS['port'], alpha=0.25)     # Crisis
    ax.axhspan(1.0, 1.5, color=COLORS['dusk'], alpha=0.20)     # High
    ax.axhspan(0.5, 1.0, color=COLORS['dusk'], alpha=0.12)     # Elevated
    ax.axhspan(-0.5, 0.5, color=COLORS['sea'], alpha=0.12)     # On target
    ax.axhspan(-3.0, -0.5, color=COLORS['sky'], alpha=0.12)    # Deflationary

    ax.plot(pci.index, pci, color=c1, linewidth=2.5, label=f'PCI ({pci.iloc[-1]:.2f})')
    ax.axhline(0, color=THEME['muted'], linewidth=0.8, alpha=0.5, linestyle='--')

    style_single_ax(ax)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.1f}'))
    ax.tick_params(axis='both', which='both', length=0)
    set_xlim_to_data(ax, pci.index)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    add_last_value_label(ax, pci, color=c1, fmt='{:.2f}', side='right')

    # Regime labels inside data area, right-aligned
    ax.text(0.98, 1.75, 'CRISIS', transform=ax.get_yaxis_transform(),
            fontsize=9, color=COLORS['port'], va='center', ha='right', fontweight='bold', alpha=0.8)
    ax.text(0.98, 1.25, 'HIGH', transform=ax.get_yaxis_transform(),
            fontsize=9, color=COLORS['dusk'], va='center', ha='right', fontweight='bold', alpha=0.8)
    ax.text(0.98, 0.75, 'ELEVATED', transform=ax.get_yaxis_transform(),
            fontsize=9, color=COLORS['dusk'], va='center', ha='right', fontweight='bold', alpha=0.6)
    ax.text(0.99, 0.25, 'TARGET', transform=ax.get_yaxis_transform(),
            fontsize=9, color=COLORS['sea'], va='center', ha='right', fontweight='bold', alpha=0.8)
    ax.text(0.98, -1.0, 'DEFLATIONARY', transform=ax.get_yaxis_transform(),
            fontsize=9, color=COLORS['sky'], va='center', ha='right', fontweight='bold', alpha=0.8)

    ax.legend(loc='upper left', **legend_style())

    pci_last = pci.iloc[-1]
    if pci_last > 1.5: regime = "Crisis"
    elif pci_last > 1.0: regime = "High"
    elif pci_last > 0.5: regime = "Elevated"
    elif pci_last > -0.5: regime = "On Target"
    else: regime = "Deflationary"
    if regime == "On Target":
        regime_note = "Policy flexibility restored."
    elif regime == "Elevated":
        regime_note = "Fed can't ease aggressively."
    elif regime == "High":
        regime_note = "No cuts possible."
    elif regime == "Crisis":
        regime_note = "Inflation emergency."
    else:
        regime_note = "Easing urgently needed."
    add_annotation_box(ax,
        f"PCI at {pci_last:.2f}: {regime} regime.\n{regime_note}",
        x=0.35, y=0.92)

    brand_fig(fig, 'Prices Composite Index (PCI)',
              subtitle='Synthesizing all inflation signals into one regime indicator',
              source='FRED, BLS, BEA, Atlanta Fed')

    return save_fig(fig, 'chart_10_pci_composite.png')


# ============================================
# TABLE IMAGES (for Substack)
# ============================================
def _render_table(col_headers, rows, title, subtitle, filename, col_widths=None):
    """Render a branded table as a PNG image."""
    OCEAN = '#2389BB'
    DUSK = '#FF6723'

    n_cols = len(col_headers)
    n_rows = len(rows)

    fig_w = 10
    fig_h = 3.2 + n_rows * 0.45
    fig = plt.figure(figsize=(fig_w, fig_h), facecolor=THEME['bg'])

    # Scale table position based on content height
    table_top = 0.68 if n_rows <= 3 else 0.72
    ax = fig.add_axes([0.05, 0.10, 0.90, table_top - 0.10])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, n_rows + 1)
    ax.axis('off')

    if col_widths is None:
        col_widths = [1.0 / n_cols] * n_cols
    col_x = [sum(col_widths[:i]) for i in range(n_cols)]

    # Header row
    header_y = n_rows + 0.5
    ax.axhspan(header_y - 0.4, header_y + 0.4, xmin=0, xmax=1,
               facecolor=OCEAN, alpha=0.9, zorder=0)
    for j, header in enumerate(col_headers):
        ax.text(col_x[j] + col_widths[j] / 2, header_y, header,
                ha='center', va='center', fontsize=11, fontweight='bold',
                color='white', zorder=1)

    # Data rows
    for i, row in enumerate(rows):
        y = n_rows - i - 0.5
        # Alternating row background
        if i % 2 == 1:
            ax.axhspan(y - 0.4, y + 0.4, xmin=0, xmax=1,
                       facecolor=THEME['spine'], alpha=0.3, zorder=0)
        for j, cell in enumerate(row):
            ax.text(col_x[j] + col_widths[j] / 2, y, cell,
                    ha='center', va='center', fontsize=10,
                    color=THEME['fg'], zorder=1)

    # Grid lines
    for i in range(n_rows + 2):
        y = i - 0.1
        ax.axhline(y, color=THEME['spine'], linewidth=0.5, alpha=0.5)

    # Custom branding for tables (no accent bars crossing title)
    OCEAN = '#2389BB'
    DUSK = '#FF6723'
    fig.patch.set_facecolor(THEME['bg'])

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

    fig.text(0.035, 0.98, 'LIGHTHOUSE MACRO', fontsize=11,
             color=OCEAN, fontweight='bold', va='top')
    fig.text(0.97, 0.98, datetime.now().strftime('%B %d, %Y'),
             fontsize=9, color=THEME['muted'], ha='right', va='top')

    # Title and subtitle with clear spacing
    fig.text(0.5, 0.93, title, fontsize=14, fontweight='bold',
             ha='center', va='top', color=THEME['fg'])
    if subtitle:
        fig.text(0.5, 0.88, subtitle, fontsize=11, ha='center',
                 va='top', color=OCEAN, style='italic')

    # Bottom accent bar only
    bbar = fig.add_axes([0.03, 0.035, 0.94, 0.004])
    bbar.axhspan(0, 1, 0, 0.67, color=OCEAN)
    bbar.axhspan(0, 1, 0.67, 1.0, color=DUSK)
    bbar.set_xlim(0, 1); bbar.set_ylim(0, 1); bbar.axis('off')

    fig.text(0.97, 0.025, 'MACRO, ILLUMINATED.', fontsize=11,
             color=OCEAN, ha='right', va='top', style='italic', fontweight='bold')
    date_str = datetime.now().strftime('%m.%d.%Y')
    fig.text(0.03, 0.022, f'Lighthouse Macro; {date_str}',
             fontsize=8, color=THEME['muted'], ha='left', va='top', style='italic')

    return save_fig(fig, filename)


def table_shelter_lag():
    """Generate shelter lag table as branded PNG."""
    print('\nTable: Shelter Lag...')
    headers = ['Market Rent Peak/Trough', 'CPI Shelter Peak/Trough', 'Lag']
    rows = [
        ['Feb 2022 (+16.0% peak)', 'Mar 2023 (+8.2% peak)', '13 months'],
        ['Jun 2020 (-1.2% trough)', 'Jun 2021 (+1.9% trough)', '12 months'],
        ['Jan 2019 (+3.2% local peak)', 'Feb 2020 (+3.8% local peak)', '13 months'],
    ]
    return _render_table(headers, rows,
                         'Shelter Lag: Market Rents Lead CPI by ~13 Months',
                         'Every turning point since 2015 confirms the mechanical lag',
                         'table_shelter_lag.png',
                         col_widths=[0.40, 0.40, 0.20])


def table_pci_regime():
    """Generate PCI regime bands table as branded PNG."""
    print('\nTable: PCI Regime Bands...')
    headers = ['PCI Range', 'Regime', 'Interpretation']
    rows = [
        ['> +1.5', 'Crisis', 'Inflation emergency, Fed forced to act'],
        ['+1.0 to +1.5', 'High', 'Aggressive restraint, no cuts possible'],
        ['+0.5 to +1.0', 'Elevated', "Fed can't ease aggressively"],
        ['-0.5 to +0.5', 'On Target', 'Policy flexibility restored'],
        ['< -0.5', 'Deflationary', 'Easing urgently needed'],
    ]
    return _render_table(headers, rows,
                         'PCI Regime Bands',
                         'Mapping the inflation environment to Fed flexibility',
                         'table_pci_regime.png',
                         col_widths=[0.20, 0.20, 0.60])


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
    11: table_shelter_lag,
    12: table_pci_regime,
}


def main():
    parser = argparse.ArgumentParser(description='Generate Prices educational charts')
    parser.add_argument('--chart', type=int, help='Chart number to generate (1-18)')
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
        for chart_num in charts_to_gen:
            if chart_num not in CHART_MAP:
                print(f'Chart {chart_num} not implemented yet.')
                continue
            CHART_MAP[chart_num]()

    print('\nDone.')


if __name__ == '__main__':
    main()
