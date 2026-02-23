#!/usr/bin/env python3
"""
Generate Charts for Educational Series: Post 1 - Labor (V8)
============================================================
VERSION 8: Generates BOTH white and dark theme versions.

Charts:
  1. Quits Rate vs Inverted Unemployment Rate (dual axis)
  2. Temporary Help Services YoY % Change
  3. Hires Rate vs Layoffs Rate (dual axis)
  4. State Unemployment Diffusion Index
  5. Job-Hopper Wage Premium
  6. Multiple Flow Indicators Indexed to Cycle Peak
  7. Unemployment Rate with Recession Shading
  8. Labor Fragility Index (LFI)
  9. Transmission Chain (schematic)

Usage:
    python generate_labor_educational_charts_v8.py
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter

# ============================================
# PATHS & CONFIG
# ============================================
BASE_PATH = '/Users/bob/LHM'
DATA_PATH = f'{BASE_PATH}/Data/data/curated/labor/labor_panel_m.parquet'
ATLANTA_FED_PATH = f'{BASE_PATH}/Data/data/raw/labor/atlanta_fed_wages.parquet'

COLORS = {
    'ocean_blue': '#2389BB',
    'dusk_orange': '#FF6723',
    'hot_magenta': '#FF2389',
    'teal_green': '#00BB89',
    'neutral_gray': '#898989',
    'lime_green': '#238923',
    'pure_red': '#892323',
    'sky': '#00BFFF',
}

RECESSIONS = [
    ('2001-03-01', '2001-11-01'),
    ('2007-12-01', '2009-06-01'),
    ('2020-02-01', '2020-04-01'),
]

# ============================================
# THEME CONFIG (set before generating)
# ============================================
THEME = {}  # populated by set_theme()
OUTPUT_DIR = ''


def set_theme(mode='white'):
    """Configure theme colors. Call before generating charts."""
    global THEME, OUTPUT_DIR
    if mode == 'dark':
        THEME = {
            'bg': '#1B2A49',
            'fg': '#e6edf3',
            'muted': '#8b949e',
            'spine': '#2a4060',
            'zero_line': '#e6edf3',
            'recession': '#ffffff',
            'recession_alpha': 0.08,
            'box_bg': '#1B2A49',
            'box_edge': COLORS['sky'],
            'callout_text': '#e6edf3',
            'brand_color': COLORS['sky'],
            'brand2_color': COLORS['hot_magenta'],
            'primary': COLORS['sky'],
            'secondary': COLORS['dusk_orange'],
            'fill_alpha': 0.25,
            'legend_bg': '#1e3350',
            'legend_fg': '#e6edf3',
            'mode': 'dark',
        }
        OUTPUT_DIR = f'{BASE_PATH}/Content/Educational_Series/dark'
    else:
        THEME = {
            'bg': '#ffffff',
            'fg': '#1a1a1a',
            'muted': '#555555',
            'spine': '#666666',
            'zero_line': '#000000',
            'recession': 'gray',
            'recession_alpha': 0.15,
            'box_bg': '#ffffff',
            'box_edge': COLORS['ocean_blue'],
            'callout_text': '#555555',
            'brand_color': COLORS['ocean_blue'],
            'brand2_color': COLORS['hot_magenta'],
            'primary': COLORS['ocean_blue'],
            'secondary': COLORS['dusk_orange'],
            'fill_alpha': 0.15,
            'legend_bg': '#ffffff',
            'legend_fg': '#1a1a1a',
            'mode': 'white',
        }
        OUTPUT_DIR = f'{BASE_PATH}/Content/Educational_Series/white'
    os.makedirs(OUTPUT_DIR, exist_ok=True)


# ============================================
# LOAD DATA
# ============================================
print("Loading data...")
df = pd.read_parquet(DATA_PATH)
df.index = pd.to_datetime(df.index)

try:
    atl_fed = pd.read_parquet(ATLANTA_FED_PATH)
    atl_fed.index = pd.to_datetime(atl_fed.index)
except Exception:
    atl_fed = None

print(f"Loaded: {len(df)} rows, {df.index.min().date()} to {df.index.max().date()}")

# ============================================
# HELPERS
# ============================================


def add_branding(ax, source='BLS'):
    """Add watermarks and source line.
    Top-left: LIGHTHOUSE MACRO
    Bottom-right: MACRO, ILLUMINATED.
    Bottom-left: Lighthouse Macro | Data Source; mm.dd.yyyy
    """
    from datetime import datetime
    date_str = datetime.now().strftime('%m.%d.%Y')
    # Top-left watermark
    ax.text(0.01, 1.02, 'LIGHTHOUSE MACRO', transform=ax.transAxes,
            fontsize=8, color=THEME['brand_color'], ha='left', va='bottom',
            fontweight='bold', alpha=0.6)
    # Bottom-right watermark
    ax.text(0.99, -0.08, 'MACRO, ILLUMINATED.', transform=ax.transAxes,
            fontsize=8, color=THEME['brand_color'], ha='right', fontweight='bold',
            alpha=0.6)
    # Bottom-left source
    ax.text(0.01, -0.08, f'Lighthouse Macro | {source}; {date_str}',
            transform=ax.transAxes, fontsize=7, color=THEME['muted'],
            ha='left', style='italic')


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


def add_recessions(ax, start_date=None):
    for s, e in RECESSIONS:
        ts, te = pd.Timestamp(s), pd.Timestamp(e)
        if start_date and te < pd.Timestamp(start_date):
            continue
        ax.axvspan(ts, te, color=THEME['recession'],
                   alpha=THEME['recession_alpha'], zorder=0)


def set_xlim_to_data(ax, idx):
    padding_left = pd.Timedelta(days=30)
    padding_right = pd.Timedelta(days=360)
    ax.set_xlim(idx.min() - padding_left, idx.max() + padding_right)


def annotate_current(ax, x, y, fmt='{:.1f}%', color=None):
    if color is None:
        color = THEME['brand2_color'] if THEME['mode'] == 'white' else COLORS['sky']
    fsize = 11 if THEME['mode'] == 'dark' else 10
    ax.annotate(fmt.format(y), xy=(x, y),
                xytext=(10, 10), textcoords='offset points',
                fontsize=fsize, fontweight='bold', color=color,
                bbox=dict(boxstyle='round', facecolor=THEME['box_bg'],
                          edgecolor=color, alpha=0.95))


def save_fig(fig, filename):
    filepath = os.path.join(OUTPUT_DIR, filename)
    fig.tight_layout()
    fig.savefig(filepath, dpi=200, bbox_inches='tight', facecolor=THEME['bg'])
    plt.close(fig)
    print(f"  Saved: {filename}")
    return filepath


def new_fig(figsize=(14, 8)):
    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_facecolor(THEME['bg'])
    ax.set_facecolor(THEME['bg'])
    return fig, ax


def legend_style():
    return dict(
        framealpha=0.95,
        facecolor=THEME['legend_bg'],
        edgecolor=THEME['spine'],
        labelcolor=THEME['legend_fg'],
    )


# ============================================
# CHART 1: Quits Rate vs Inverted Unemployment Rate
# ============================================
def chart_1_quits_vs_unemployment():
    """Dual-axis: Quits (RHS, inverted) vs Unemployment (LHS)."""
    print("\nChart 1: Quits vs Unemployment (Dual Axis)...")

    subset = df[['JOLTS_Quits_Rate', 'Unemployment_Rate']].dropna()
    subset = subset[subset.index >= '2001-01-01']

    fig, ax1 = new_fig()

    c1 = COLORS['dusk_orange']
    ax1.plot(subset.index, subset['Unemployment_Rate'],
             color=c1, linewidth=2.5, label='Unemployment Rate')
    ax1.fill_between(subset.index, subset['Unemployment_Rate'],
                     alpha=THEME['fill_alpha'], color=c1)
    ax1.set_ylabel('Unemployment Rate (%)', color=c1, fontsize=12, fontweight='bold')
    ax1.tick_params(axis='y', labelcolor=c1, labelsize=10)
    ax1.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.0f}%'))
    ax1.set_ylim(2, 16)

    ax2 = ax1.twinx()
    c2 = THEME['primary']
    ax2.plot(subset.index, subset['JOLTS_Quits_Rate'],
             color=c2, linewidth=2.5, label='Quits Rate')
    ax2.set_ylabel('Quits Rate (%) \u2014 INVERTED', color=c2, fontsize=12, fontweight='bold')
    ax2.tick_params(axis='y', labelcolor=c2, labelsize=10)
    ax2.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.1f}%'))
    ax2.set_ylim(1.0, 3.5)
    ax2.invert_yaxis()

    ax2.axhline(y=2.0, color=COLORS['pure_red'], linestyle='--', linewidth=2, alpha=0.8)
    ax2.text(subset.index[5], 1.95, 'Pre-Recessionary (2.0%)',
             fontsize=9, color=COLORS['pure_red'], fontweight='bold')

    add_recessions(ax1)
    style_ax(ax1, right_primary=False)
    ax1.grid(False)
    ax2.grid(False)
    for spine in ax2.spines.values():
        spine.set_color(THEME['spine'])
    set_xlim_to_data(ax1, subset.index)

    # Callout with current values
    last_q = subset['JOLTS_Quits_Rate'].iloc[-1]
    last_u = subset['Unemployment_Rate'].iloc[-1]
    ax2.text(0.98, 0.03,
             f'Quits: {last_q:.1f}% (down from 3.0% peak)\n'
             f'Unemployment: {last_u:.1f}%\n\n'
             f'\u2191 Quits axis inverted',
             transform=ax2.transAxes, fontsize=8, ha='right', va='bottom',
             color=c2, style='italic',
             bbox=dict(boxstyle='round', facecolor=THEME['box_bg'],
                       alpha=0.9, edgecolor=c2))

    ax1.set_title('Quits Rate (Leading) vs Unemployment Rate (Lagging)',
                  fontsize=14, fontweight='bold', pad=20, color=THEME['fg'])

    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', **legend_style())

    add_branding(ax1, source='BLS JOLTS')
    return save_fig(fig, 'chart_1_quits_vs_unemployment.png')


# ============================================
# CHART 2: Temp Help YoY
# ============================================
def chart_2_temp_help():
    """Temp Help YoY with prominent zero line and recession shading."""
    print("\nChart 2: Temp Help YoY...")

    if 'Emp_Temp_Help' not in df.columns:
        print("  SKIP: Emp_Temp_Help not found")
        return None

    temp_yoy = df['Emp_Temp_Help'].pct_change(12, fill_method=None) * 100
    temp_yoy = temp_yoy.dropna()
    temp_yoy = temp_yoy[temp_yoy.index >= '2002-01-01']

    fig, ax = new_fig()

    pos_color = COLORS['lime_green'] if THEME['mode'] == 'dark' else COLORS['teal_green']
    colors_bar = [pos_color if x >= 0 else COLORS['pure_red'] for x in temp_yoy]
    ax.bar(temp_yoy.index, temp_yoy, color=colors_bar, alpha=0.7, width=25)

    ax.axhline(y=0, color=THEME['zero_line'], linewidth=2, zorder=5)

    thresh_color = THEME['primary'] if THEME['mode'] == 'dark' else COLORS['pure_red']
    ax.axhline(y=-3, color=thresh_color, linestyle='--', linewidth=1.5, alpha=0.7)
    ax.text(temp_yoy.index[3], -4.5, 'Recession Signal (-3%)',
            fontsize=9, color=thresh_color, fontweight='bold')

    ymin, ymax = temp_yoy.min() - 5, temp_yoy.max() + 5
    ax.axhspan(ymin, 0, color=COLORS['pure_red'], alpha=0.03, zorder=0)

    add_recessions(ax, '2002-01-01')

    # Yellow vertical lines: last zero-crossing before each recession
    recession_starts = [pd.Timestamp('2001-03-01'), pd.Timestamp('2007-12-01'),
                        pd.Timestamp('2020-02-01')]
    sign_change = (temp_yoy.shift(1) >= 0) & (temp_yoy < 0)
    transitions = temp_yoy[sign_change].index
    for rs in recession_starts:
        prior = transitions[transitions < rs]
        if len(prior) > 0:
            ax.axvline(x=prior[-1], color='#FFD700', linewidth=2, alpha=0.7, zorder=4)
    # Current cycle (no recession yet but contraction ongoing)
    post_2020 = transitions[transitions > pd.Timestamp('2022-01-01')]
    if len(post_2020) > 0:
        ax.axvline(x=post_2020[0], color='#FFD700', linewidth=2, alpha=0.7, zorder=4)

    current_val = temp_yoy.iloc[-1]
    annotate_current(ax, temp_yoy.index[-1], current_val, color=THEME['primary'])

    ax.text(0.5, 0.97,
            f'Current: {current_val:.1f}% YoY\n'
            f'Contraction sustained for 38+ months\n'
            f'Yellow lines: last negative before recession\n'
            f'Red dashed: -3% threshold',
            transform=ax.transAxes, fontsize=9, va='top', ha='center',
            color=THEME['callout_text'], fontweight='bold',
            bbox=dict(boxstyle='round', facecolor=THEME['box_bg'], alpha=0.9,
                      edgecolor=THEME['primary']))

    ax.set_ylabel('YoY Change (%)', fontsize=11)
    ax.set_ylim(ymin, ymax)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.0f}%'))
    ax.set_title('Temp Help Employment YoY Change\nFirst Hired, First Fired',
                 fontsize=14, fontweight='bold', pad=15)
    style_ax(ax)
    add_branding(ax, source='BLS CES')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    set_xlim_to_data(ax, temp_yoy.index)

    return save_fig(fig, 'chart_2_temp_help_yoy.png')


# ============================================
# CHART 3: Hires Rate vs Layoffs Rate
# ============================================
def chart_3_hires_vs_layoffs():
    """Dual-axis: Hires Rate vs Layoffs Rate. Shows the freeze."""
    print("\nChart 3: Hires vs Layoffs...")

    cols = ['JOLTS_Hires_Rate', 'JOLTS_Layoffs_Rate']
    if not all(c in df.columns for c in cols):
        print("  SKIP: missing columns")
        return None

    subset = df[cols].dropna()
    subset = subset[subset.index >= '2001-01-01']

    fig, ax = new_fig()

    # Layoffs on left axis (secondary)
    c_layoffs = COLORS['dusk_orange']
    ax.plot(subset.index, subset['JOLTS_Layoffs_Rate'],
            color=c_layoffs, linewidth=2.5, label='Layoffs Rate')
    ax.set_ylabel('Layoffs Rate (%)', color=c_layoffs, fontsize=12, fontweight='bold')
    ax.tick_params(axis='y', labelcolor=c_layoffs)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.1f}%'))

    # Hires on right axis (primary)
    ax2 = ax.twinx()
    c_hires = THEME['primary']
    ax2.plot(subset.index, subset['JOLTS_Hires_Rate'],
             color=c_hires, linewidth=2.5, label='Hires Rate')
    ax2.fill_between(subset.index, subset['JOLTS_Hires_Rate'],
                     alpha=THEME['fill_alpha'], color=c_hires)
    ax2.set_ylabel('Hires Rate (%)', color=c_hires, fontsize=12, fontweight='bold')
    ax2.tick_params(axis='y', labelcolor=c_hires)
    ax2.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.1f}%'))

    add_recessions(ax)
    style_ax(ax, right_primary=False)
    ax.grid(False)
    ax2.grid(False)
    for spine in ax2.spines.values():
        spine.set_color(THEME['spine'])
    set_xlim_to_data(ax, subset.index)

    # End-of-line labels
    last = subset.iloc[-1]
    annotate_current(ax2, subset.index[-1], last['JOLTS_Hires_Rate'],
                     fmt='{:.1f}%', color=c_hires)
    annotate_current(ax, subset.index[-1], last['JOLTS_Layoffs_Rate'],
                     fmt='{:.1f}%', color=c_layoffs)

    # Callout
    callout_color = THEME['primary'] if THEME['mode'] == 'dark' else COLORS['hot_magenta']
    ax.text(0.5, 0.95,
            'Hiring freeze without firing wave\n'
            f'Hires: {last["JOLTS_Hires_Rate"]:.1f}% (down from 4.5% peak)\n'
            f'Layoffs: {last["JOLTS_Layoffs_Rate"]:.1f}% (historically low)',
            transform=ax.transAxes, fontsize=9, ha='center', va='top',
            fontweight='bold', color=callout_color,
            bbox=dict(boxstyle='round', facecolor=THEME['box_bg'],
                      edgecolor=callout_color, alpha=0.95))

    ax.set_title('Hires Rate vs Layoffs Rate',
                 fontsize=14, fontweight='bold', pad=20)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    lines1, labels1 = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax.legend(lines1 + lines2, labels1 + labels2, loc='upper left', **legend_style())

    add_branding(ax, source='BLS JOLTS')
    return save_fig(fig, 'chart_3_hires_vs_layoffs.png')


# ============================================
# CHART 4: State Diffusion
# ============================================
def chart_4_state_diffusion():
    """% of states with rising unemployment (YoY)."""
    print("\nChart 4: State Diffusion...")

    state_cols = [c for c in df.columns
                  if c.startswith('Unemp_Rate_') and len(c) == len('Unemp_Rate_XX')
                  and c[-2:].isalpha() and c[-2:].isupper()]
    print(f"  Found {len(state_cols)} state columns")

    if len(state_cols) < 40:
        print("  SKIP: not enough state columns")
        return None

    state_data = df[state_cols].dropna(how='all')
    state_yoy = state_data.diff(12)

    rising_count = (state_yoy > 0).sum(axis=1)
    valid_count = state_yoy.notna().sum(axis=1)
    diffusion = (rising_count / valid_count * 100).replace([np.inf, -np.inf], np.nan)
    diffusion = diffusion.dropna()
    diffusion = diffusion[diffusion.index >= '2005-01-01']

    print(f"  Range: {diffusion.min():.1f}% to {diffusion.max():.1f}%")
    print(f"  Current: {diffusion.iloc[-1]:.1f}%")

    fig, ax = new_fig()

    ax.plot(diffusion.index, diffusion, color=THEME['primary'], linewidth=2.5)
    ax.fill_between(diffusion.index, diffusion, alpha=THEME['fill_alpha'],
                    color=THEME['primary'])

    ax.axhline(y=50, color=COLORS['dusk_orange'], linestyle='--', linewidth=2,
               label='50%: Broad-Based')
    ax.axhline(y=70, color=COLORS['pure_red'], linestyle='--', linewidth=1.5,
               label='70%: Pervasive')

    add_recessions(ax, '2005-01-01')

    annotate_current(ax, diffusion.index[-1], diffusion.iloc[-1], fmt='{:.0f}%')

    ax.set_ylabel('% of States with Rising Unemployment (YoY)', fontsize=11)
    ax.set_ylim(0, 110)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.0f}%'))
    ax.set_title('State Unemployment Diffusion Index\nHow Widespread Is the Weakness?',
                 fontsize=14, fontweight='bold', pad=15)
    ax.axhline(y=100, color=THEME['muted'], linestyle='-', linewidth=1, alpha=0.5)
    ax.legend(loc='upper left', **legend_style())
    style_ax(ax)
    add_branding(ax, source='BLS LAUS')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    set_xlim_to_data(ax, diffusion.index)

    return save_fig(fig, 'chart_4_state_diffusion.png')


# ============================================
# CHART 5: Job-Hopper Premium
# ============================================
def chart_5_job_hopper():
    """Job-Hopper Premium (Switchers - Stayers wage growth)."""
    print("\nChart 5: Job-Hopper Premium...")

    premium = df.get('AtlFed_Job_Hopper_Premium')
    if premium is None and atl_fed is not None:
        premium = atl_fed.get('AtlFed_Job_Hopper_Premium')
    if premium is None:
        print("  SKIP: no premium data")
        return None

    premium = premium.dropna()
    premium = premium[premium.index >= '2000-01-01']

    fig, ax = new_fig()

    ax.plot(premium.index, premium, color=THEME['primary'], linewidth=2.5)
    ax.fill_between(premium.index, premium, alpha=THEME['fill_alpha'],
                    color=THEME['primary'])

    ax.axhline(y=0.5, color=COLORS['dusk_orange'], linestyle='--', linewidth=1.5,
               label='Late-Cycle Threshold (0.5 ppts)')
    ax.axhline(y=0, color=THEME['zero_line'], linewidth=1, alpha=0.5)

    ax.axhspan(premium.min() - 0.5, 0.5, color=COLORS['pure_red'], alpha=0.03, zorder=0)

    add_recessions(ax)

    annotate_current(ax, premium.index[-1], premium.iloc[-1], fmt='{:.1f} ppts')

    ax.set_ylabel('Premium (ppts)', fontsize=11)
    ax.set_ylim(-1.5, 3.5)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.1f}'))
    ax.set_title('Job-Hopper Premium: Switcher vs Stayer Wage Growth\n'
                 'The Grass Is No Longer Greener',
                 fontsize=14, fontweight='bold', pad=15)
    ax.legend(loc='upper left', **legend_style())
    style_ax(ax)
    add_branding(ax, source='Atlanta Fed Wage Growth Tracker')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    set_xlim_to_data(ax, premium.index)

    return save_fig(fig, 'chart_5_job_hopper_premium.png')


# ============================================
# CHART 6: Flow Indicators Indexed to Cycle Peak
# ============================================
def chart_6_flow_indexed():
    """Multiple flow indicators indexed to their cycle peak = 100."""
    print("\nChart 6: Flow Indicators Indexed to Cycle Peak...")

    series = {}

    quits = df['JOLTS_Quits_Rate'].dropna()
    if len(quits) > 0:
        series['Quits Rate'] = ((quits / quits.max()) * 100,
                                THEME['primary'])

    hires = df.get('JOLTS_Hires_Rate')
    if hires is not None:
        hires = hires.dropna()
        series['Hires Rate'] = ((hires / hires.max()) * 100,
                                COLORS['dusk_orange'])

    temp = df.get('Emp_Temp_Help')
    if temp is not None:
        temp = temp.dropna()
        series['Temp Help'] = ((temp / temp.max()) * 100,
                               COLORS['teal_green'] if THEME['mode'] == 'white' else COLORS['lime_green'])

    if not series:
        print("  SKIP: no data")
        return None

    start = pd.Timestamp('2019-01-01')

    fig, ax = new_fig()

    for name, (data, color) in series.items():
        plot_data = data[data.index >= start]
        ax.plot(plot_data.index, plot_data, color=color, linewidth=2.5, label=name)
        # End-of-line value label
        last_val = plot_data.iloc[-1]
        ax.text(plot_data.index[-1] + pd.Timedelta(days=10), last_val,
                f'{last_val:.0f}', fontsize=10, fontweight='bold',
                color=color, va='center')

    ax.axhline(y=100, color=THEME['muted'], linewidth=1, linestyle='--', alpha=0.5)

    # Callout
    ax.text(0.5, 0.05,
            'All three flow indicators have\n'
            'declined materially from cycle peaks',
            transform=ax.transAxes, fontsize=9, ha='center', va='bottom',
            color=THEME['callout_text'],
            bbox=dict(boxstyle='round', facecolor=THEME['box_bg'],
                      edgecolor=THEME['spine'], alpha=0.9))

    add_recessions(ax, '2019-01-01')
    style_ax(ax)
    set_xlim_to_data(ax, df[df.index >= start].index)
    # Extend right margin for labels
    xmin, xmax = ax.get_xlim()
    ax.set_xlim(xmin, xmax + 60)

    ax.set_ylabel('Index (Peak = 100)', fontsize=11)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.0f}'))
    ax.set_title('Flow Indicators Indexed to Cycle Peak (Peak = 100)',
                 fontsize=14, fontweight='bold', pad=15)
    ax.legend(loc='upper right', **legend_style())
    add_branding(ax, source='BLS, JOLTS')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    return save_fig(fig, 'chart_6_flow_indexed.png')


# ============================================
# CHART 7: Unemployment Rate with Recession Shading
# ============================================
def chart_7_unemployment():
    """Simple unemployment rate time series with recession bars."""
    print("\nChart 7: Unemployment Rate...")

    unemp = df['Unemployment_Rate'].dropna()
    unemp = unemp[unemp.index >= '2000-01-01']

    fig, ax = new_fig()

    ax.plot(unemp.index, unemp, color=THEME['primary'], linewidth=2.5)
    ax.fill_between(unemp.index, unemp, alpha=THEME['fill_alpha'],
                    color=THEME['primary'])

    add_recessions(ax)

    # Callout box
    current = unemp.iloc[-1]
    callout_color = THEME['primary']
    ax.text(0.5, 0.95,
            f'Current: {current:.1f}%\n\n'
            f'Headline looks fine.\n'
            f'Flows tell a different story.\n\n'
            f'Gray bars = recessions',
            transform=ax.transAxes, fontsize=9, ha='center', va='top',
            color=callout_color,
            bbox=dict(boxstyle='round', facecolor=THEME['box_bg'],
                      edgecolor=callout_color, alpha=0.95))

    annotate_current(ax, unemp.index[-1], current)

    ax.set_ylabel('Rate (%)', fontsize=11)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.0f}%'))
    ax.set_title('Unemployment Rate',
                 fontsize=14, fontweight='bold', pad=15)
    style_ax(ax)
    add_branding(ax, source='BLS CPS')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    set_xlim_to_data(ax, unemp.index)

    return save_fig(fig, 'chart_7_unemployment_rate.png')


# ============================================
# CHART 8: Labor Fragility Index (LFI)
# ============================================
def chart_8_lfi():
    """Labor Fragility Index composite.

    Canonical formula from master context:
        LFI = 0.35*z(LongTermUnemp%) + 0.35*z(-Quits) + 0.30*z(-Hires/Quits)
    All components oriented so HIGHER = MORE FRAGILE.
    Uses 36-month rolling z-scores to capture regime shifts.
    """
    print("\nChart 8: LFI...")

    lt_share_raw = df.get('Unemp_27_Weeks_Plus')
    unemp_total = df.get('Unemp_Total_Level')
    quits = df.get('JOLTS_Quits_Rate')

    if lt_share_raw is None or unemp_total is None or quits is None:
        print("  SKIP: missing core columns")
        return None

    lt_share = lt_share_raw / unemp_total * 100

    def z(s, w=36):
        return (s - s.rolling(w, min_periods=12).mean()) / s.rolling(w, min_periods=12).std()

    z_lt = z(lt_share)
    z_neg_quits = z(-quits)

    if 'JOLTS_Hires_Level' in df.columns and 'JOLTS_Quits_Level' in df.columns:
        hq_ratio = df['JOLTS_Hires_Level'] / df['JOLTS_Quits_Level']
        z_neg_hq = z(-hq_ratio)
        lfi = 0.35 * z_lt + 0.35 * z_neg_quits + 0.30 * z_neg_hq
    else:
        lfi = 0.50 * z_lt + 0.50 * z_neg_quits

    lfi = lfi.dropna()
    lfi = lfi[lfi.index >= '2005-01-01']
    print(f"  LFI current: {lfi.iloc[-1]:.3f}")

    fig, ax = new_fig()

    ax.plot(lfi.index, lfi, color=THEME['primary'], linewidth=2.5)

    ax.fill_between(lfi.index, lfi, where=(lfi > 0) & (lfi <= 0.5),
                    color=COLORS['teal_green'], alpha=0.15)
    ax.fill_between(lfi.index, lfi, where=(lfi > 0.5) & (lfi <= 1.0),
                    color=COLORS['dusk_orange'], alpha=0.25)
    ax.fill_between(lfi.index, lfi, where=(lfi > 1.0),
                    color=COLORS['pure_red'], alpha=0.3)

    ax.axhline(y=0.5, color=COLORS['dusk_orange'], linestyle='--', linewidth=1.5,
               label='Elevated (+0.5)')
    ax.axhline(y=1.0, color=COLORS['pure_red'], linestyle='--', linewidth=1.5,
               label='Pre-Recessionary (+1.0)')
    ax.axhline(y=0, color=THEME['zero_line'], linewidth=0.5, alpha=0.3)

    add_recessions(ax, '2005-01-01')

    annotate_current(ax, lfi.index[-1], lfi.iloc[-1], fmt='{:.2f}')

    ax.set_ylabel('LFI (Z-Score Composite)', fontsize=11)
    ax.set_title('Labor Fragility Index (LFI)\nSynthesizing Flow Indicators into a Single Signal',
                 fontsize=14, fontweight='bold', pad=15)
    ax.legend(loc='upper left', **legend_style())
    style_ax(ax)
    add_branding(ax, source='BLS, JOLTS')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    set_xlim_to_data(ax, lfi.index)

    return save_fig(fig, 'chart_8_lfi.png')


# ============================================
# CHART 9: Transmission Chain (Schematic)
# ============================================
def chart_9_transmission():
    """Visual schematic of the labor transmission chain."""
    print("\nChart 9: Transmission Chain...")

    fig, ax = plt.subplots(figsize=(7, 3.2))
    fig.patch.set_facecolor(THEME['bg'])
    ax.set_facecolor(THEME['bg'])
    ax.set_xlim(0, 7)
    ax.set_ylim(0, 4.0)
    ax.axis('off')

    box_edge = THEME['box_edge']
    box_fill = THEME['box_bg']
    sub_color = THEME['muted']
    arrow_color = COLORS['dusk_orange']

    bw = 0.95  # box width
    bh = 1.05  # box height
    gap = 1.3  # center-to-center spacing

    chain = [
        (0.75,          1.7, 'LABOR',    'Employment\nHours, Wages'),
        (0.75 + gap,    1.7, 'INCOME',   'Disposable\nIncome'),
        (0.75 + gap*2,  1.7, 'SPENDING', 'Consumption\n(68% GDP)'),
        (0.75 + gap*3,  1.7, 'CREDIT',   'Revenue\nDebt Service'),
        (0.75 + gap*4,  1.7, 'HOUSING',  'Wealth\nMortgage'),
    ]

    for x, y, title, sub in chain:
        rect = plt.Rectangle((x - bw/2, y - bh/2), bw, bh, linewidth=2,
                              edgecolor=box_edge, facecolor=box_fill, zorder=3)
        ax.add_patch(rect)
        ax.text(x, y + 0.12, title, fontsize=9, fontweight='bold',
                color=box_edge, ha='center', va='center')
        ax.text(x, y - 0.22, sub, fontsize=5.5, color=sub_color,
                ha='center', va='center')

    for i in range(len(chain) - 1):
        ax.annotate('', xy=(chain[i + 1][0] - bw/2, chain[i + 1][1]),
                    xytext=(chain[i][0] + bw/2, chain[i][1]),
                    arrowprops=dict(arrowstyle='->', color=arrow_color,
                                    lw=2.5, connectionstyle='arc3,rad=0'))

    lag_labels = ['1-3 mo', '1-2 mo', '1-3 mo', '2-3 mo']
    for i, label in enumerate(lag_labels):
        mid_x = (chain[i][0] + chain[i + 1][0]) / 2
        ax.text(mid_x, chain[i][1] + 0.75, label, fontsize=6,
                ha='center', color=arrow_color, fontweight='bold')

    ax.text(3.5, 3.6, 'The Labor Transmission Chain', fontsize=12,
            fontweight='bold', ha='center', color=box_edge)
    ax.text(3.5, 3.15, 'Change the labor picture, and everything downstream changes with it.',
            fontsize=8, ha='center', style='italic', color=sub_color)

    # Top-left watermark
    ax.text(0.15, 3.85, 'LIGHTHOUSE MACRO', fontsize=6,
            color=THEME['brand_color'], ha='left', fontweight='bold', alpha=0.6)
    # Bottom-right watermark
    ax.text(6.8, 0.15, 'MACRO, ILLUMINATED.', fontsize=6,
            color=THEME['brand_color'], ha='right', fontweight='bold', alpha=0.6)
    # Bottom-left source
    from datetime import datetime
    date_str = datetime.now().strftime('%m.%d.%Y')
    ax.text(0.15, 0.15, f'Lighthouse Macro; {date_str}', fontsize=5,
            color=THEME['muted'], ha='left', style='italic')

    return save_fig(fig, 'chart_9_transmission_chain.png')


# ============================================
# CHART 10: Hours Worked vs Employment YoY
# ============================================
def chart_10_hours_vs_employment():
    """Dual-axis: Aggregate Hours YoY vs Employment YoY. Hours lead."""
    print("\nChart 10: Hours Worked vs Employment...")

    hours = df.get('Aggregate_Weekly_Hours_Index')
    emp = df.get('Nonfarm_Payrolls')

    if hours is None or emp is None:
        print("  SKIP: missing columns")
        return None

    hours_yoy = hours.pct_change(12, fill_method=None) * 100
    emp_yoy = emp.pct_change(12, fill_method=None) * 100

    combined = pd.DataFrame({'hours': hours_yoy, 'emp': emp_yoy}).dropna()
    combined = combined[combined.index >= '2001-01-01']

    fig, ax1 = new_fig()

    # Employment YoY (LHS, secondary)
    c_emp = COLORS['dusk_orange']
    ax1.plot(combined.index, combined['emp'],
             color=c_emp, linewidth=2.5, label='Employment YoY (%)')
    ax1.set_ylabel('Employment YoY (%)', color=c_emp, fontsize=12, fontweight='bold')
    ax1.tick_params(axis='y', labelcolor=c_emp, labelsize=10)
    ax1.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.0f}%'))

    # Hours YoY (RHS, primary)
    ax2 = ax1.twinx()
    c_hours = THEME['primary']
    ax2.plot(combined.index, combined['hours'],
             color=c_hours, linewidth=2.5, label='Hours YoY (%)')
    ax2.set_ylabel('Hours YoY (%)', color=c_hours, fontsize=12, fontweight='bold')
    ax2.tick_params(axis='y', labelcolor=c_hours, labelsize=10)
    ax2.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.0f}%'))

    # Zero lines
    ax1.axhline(y=0, color=THEME['zero_line'], linewidth=0.5, alpha=0.3)

    add_recessions(ax1)
    style_ax(ax1, right_primary=False)
    ax1.grid(False)
    ax2.grid(False)
    for spine in ax2.spines.values():
        spine.set_color(THEME['spine'])
    set_xlim_to_data(ax1, combined.index)

    # End-of-line labels
    last_h = combined['hours'].iloc[-1]
    last_e = combined['emp'].iloc[-1]
    annotate_current(ax2, combined.index[-1], last_h,
                     fmt='{:.1f}%', color=c_hours)
    annotate_current(ax1, combined.index[-1], last_e,
                     fmt='{:.1f}%', color=c_emp)

    ax1.set_title('Hours Worked vs Employment (YoY)\nHours Get Cut Before Headcount',
                  fontsize=14, fontweight='bold', pad=20)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', **legend_style())

    add_branding(ax1, source='BLS CES')
    return save_fig(fig, 'chart_10_hours_vs_employment.png')


# ============================================
# MAIN
# ============================================
def generate_all():
    charts = []
    charts.append(chart_1_quits_vs_unemployment())
    charts.append(chart_2_temp_help())
    charts.append(chart_3_hires_vs_layoffs())
    charts.append(chart_4_state_diffusion())
    charts.append(chart_5_job_hopper())
    charts.append(chart_6_flow_indexed())
    charts.append(chart_7_unemployment())
    charts.append(chart_8_lfi())
    charts.append(chart_9_transmission())
    charts.append(chart_10_hours_vs_employment())
    return [c for c in charts if c]


def main():
    for mode in ['white', 'dark']:
        print(f"\n{'=' * 60}")
        print(f"GENERATING {mode.upper()} THEME")
        print(f"{'=' * 60}")
        set_theme(mode)
        charts = generate_all()
        print(f"\n  {len(charts)} charts saved to {OUTPUT_DIR}")

    print(f"\n{'=' * 60}")
    print("COMPLETE: Both themes generated.")
    print("=" * 60)


if __name__ == "__main__":
    main()
