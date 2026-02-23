#!/usr/bin/env python3
"""
Generate Charts for Educational Series: Post 1 - Labor
=======================================================
Creates 7 branded charts for the first educational post on labor markets.

Charts:
1. Quits Rate vs. Unemployment Rate (Dual Axis) - shows quits leading
2. Job-Hopper Premium Time Series - collapse from 5+ ppts to ~0
3. Youth vs. Prime-Age Unemployment - youth as canary
4. Temp Help Employment YoY% - recession signal
5. State Unemployment Diffusion - heat map of rising states
6. Labor Fragility Index (LFI) - composite indicator
7. Transmission Chain Schematic - Labor → Consumer → Credit → Housing

Usage:
    python generate_labor_educational_charts.py
"""

import os
import sys
from datetime import datetime

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter

# Add utilities path
sys.path.insert(0, '/Users/bob/LHM/Scripts/utilities')
try:
    from lighthouse_chart_style import (
        LIGHTHOUSE_COLORS, LIGHTHOUSE_FILLS_HEX,
        create_figure, apply_lighthouse_style,
        add_threshold_line, add_zone_shading,
        format_axis_percent, setup_date_axis,
        save_chart, add_last_value_label, add_series_with_label
    )
except ImportError:
    # Fallback colors
    LIGHTHOUSE_COLORS = {
        'ocean_blue': '#2389BB',
        'dusk_orange': '#FF6723',
        'electric_cyan': '#00FFFF',
        'hot_magenta': '#FF2389',
        'teal_green': '#00BB89',
        'neutral_gray': '#898989',
        'lime_green': '#238923',
        'pure_red': '#892323'
    }

# ============================================
# PATHS & CONFIG
# ============================================
BASE_PATH = '/Users/bob/LHM'
DATA_PATH = f'{BASE_PATH}/Data/data/curated/labor/labor_panel_m.parquet'
ATLANTA_FED_PATH = f'{BASE_PATH}/Data/data/raw/labor/atlanta_fed_wages.parquet'
OUTPUT_DIR = f'{BASE_PATH}/Outputs/Educational_Charts/Labor_Post_1'

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ============================================
# LOAD DATA
# ============================================
print("Loading data...")
df = pd.read_parquet(DATA_PATH)
df.index = pd.to_datetime(df.index)

# Load Atlanta Fed data
try:
    atl_fed = pd.read_parquet(ATLANTA_FED_PATH)
    atl_fed.index = pd.to_datetime(atl_fed.index)
    print(f"Loaded Atlanta Fed data: {len(atl_fed)} rows")
except Exception as e:
    print(f"Warning: Could not load Atlanta Fed data: {e}")
    atl_fed = None

print(f"Loaded labor panel: {len(df)} rows, {len(df.columns)} columns")
print(f"Date range: {df.index.min()} to {df.index.max()}")

# ============================================
# HELPER FUNCTIONS
# ============================================

def apply_lhm_style(ax, title, subtitle=None, primary_side='right'):
    """Apply Lighthouse Macro styling to axes."""
    ax.grid(False)

    # All 4 spines visible
    for spine in ['top', 'right', 'left', 'bottom']:
        ax.spines[spine].set_visible(True)
        ax.spines[spine].set_linewidth(0.5)
        ax.spines[spine].set_color('#666666')

    # Title
    ax.set_title(title, fontsize=14, fontweight='bold', loc='center', pad=20)

    if subtitle:
        ax.text(0.5, 1.02, subtitle, transform=ax.transAxes,
                fontsize=10, ha='center', style='italic', color='#666666')

    # Branding
    ax.text(0.01, 1.06, 'LIGHTHOUSE MACRO',
            transform=ax.transAxes, fontsize=8,
            color=LIGHTHOUSE_COLORS['ocean_blue'], fontweight='bold')
    ax.text(0.99, -0.08, 'MACRO, ILLUMINATED.',
            transform=ax.transAxes, fontsize=7,
            color=LIGHTHOUSE_COLORS['hot_magenta'],
            ha='right', style='italic')

    return ax


def add_recession_bars(ax, start_date='2000-01-01'):
    """Add recession shading."""
    recessions = [
        ('2001-03-01', '2001-11-01'),  # Dot-com
        ('2007-12-01', '2009-06-01'),  # GFC
        ('2020-02-01', '2020-04-01'),  # COVID
    ]
    for start, end in recessions:
        if pd.Timestamp(start) >= pd.Timestamp(start_date):
            ax.axvspan(pd.Timestamp(start), pd.Timestamp(end),
                      color='gray', alpha=0.15, zorder=0)


def save_fig(fig, filename):
    """Save figure with standard settings."""
    filepath = os.path.join(OUTPUT_DIR, filename)
    fig.tight_layout()
    fig.savefig(filepath, dpi=200, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close(fig)
    print(f"  Saved: {filename}")
    return filepath


# ============================================
# CHART 1: Quits Rate vs. Unemployment Rate
# ============================================
def chart_1_quits_vs_unemployment():
    """
    Dual axis chart showing quits rate leading unemployment.
    Key insight: Quits collapse 6-9 months before unemployment rises.
    """
    print("\nChart 1: Quits Rate vs Unemployment Rate...")

    # Data subset - since 2000
    subset = df[['JOLTS_Quits_Rate', 'Unemployment_Rate']].dropna()

    fig, ax1 = plt.subplots(figsize=(12, 7))
    fig.patch.set_facecolor('white')
    ax1.set_facecolor('white')

    # Left axis: Unemployment Rate (lagging)
    color_unemp = LIGHTHOUSE_COLORS['neutral_gray']
    ax1.plot(subset.index, subset['Unemployment_Rate'],
             color=color_unemp, linewidth=1.5, label='Unemployment Rate (Lagging)')
    ax1.set_ylabel('Unemployment Rate (%)', color=color_unemp)
    ax1.tick_params(axis='y', labelcolor=color_unemp)
    ax1.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.1f}%'))

    # Right axis: Quits Rate (leading)
    ax2 = ax1.twinx()
    color_quits = LIGHTHOUSE_COLORS['ocean_blue']
    ax2.plot(subset.index, subset['JOLTS_Quits_Rate'],
             color=color_quits, linewidth=2.5, label='Quits Rate (Leading)')
    ax2.fill_between(subset.index, subset['JOLTS_Quits_Rate'],
                     alpha=0.2, color=color_quits)
    ax2.set_ylabel('Quits Rate (%)', color=color_quits, fontweight='bold')
    ax2.tick_params(axis='y', labelcolor=color_quits)
    ax2.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.1f}%'))

    # Threshold line at 2.0%
    ax2.axhline(y=2.0, color=LIGHTHOUSE_COLORS['pure_red'], linestyle='--',
                linewidth=1.5, alpha=0.8)
    ax2.text(subset.index[-1], 2.05, ' Pre-Recessionary Threshold (2.0%)',
             fontsize=8, color=LIGHTHOUSE_COLORS['pure_red'], va='bottom')

    # Add recession shading
    add_recession_bars(ax1)

    # Current value annotation
    current_quits = subset['JOLTS_Quits_Rate'].iloc[-1]
    ax2.annotate(f'Current: {current_quits:.1f}%',
                xy=(subset.index[-1], current_quits),
                xytext=(20, 20), textcoords='offset points',
                fontsize=9, fontweight='bold',
                color=LIGHTHOUSE_COLORS['hot_magenta'],
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                         edgecolor=LIGHTHOUSE_COLORS['hot_magenta']))

    # Styling
    for spine in ['top', 'right', 'left', 'bottom']:
        ax1.spines[spine].set_visible(True)
        ax1.spines[spine].set_linewidth(0.5)
        ax1.spines[spine].set_color('#666666')

    ax1.grid(False)
    ax2.grid(False)

    # Title and branding
    ax1.set_title('Quits Rate vs. Unemployment Rate\nQuits Lead by 6-9 Months',
                  fontsize=14, fontweight='bold', pad=20)
    ax1.text(0.01, 1.08, 'LIGHTHOUSE MACRO',
             transform=ax1.transAxes, fontsize=8,
             color=LIGHTHOUSE_COLORS['ocean_blue'], fontweight='bold')
    ax1.text(0.99, -0.10, 'MACRO, ILLUMINATED.',
             transform=ax1.transAxes, fontsize=7,
             color=LIGHTHOUSE_COLORS['hot_magenta'],
             ha='right', style='italic')

    # Combined legend
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left',
               framealpha=0.95, edgecolor='#666666')

    # Format x-axis
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    return save_fig(fig, 'chart_1_quits_vs_unemployment.png')


# ============================================
# CHART 2: Job-Hopper Premium Time Series
# ============================================
def chart_2_job_hopper_premium():
    """
    Time series showing collapse of job-hopper premium.
    Key insight: Premium collapsed from 5+ ppts to near zero.
    """
    print("\nChart 2: Job-Hopper Premium...")

    # Use Atlanta Fed data
    if 'AtlFed_Job_Hopper_Premium' in df.columns:
        subset = df[['AtlFed_Job_Hopper_Premium']].dropna()
        premium = subset['AtlFed_Job_Hopper_Premium']
    elif atl_fed is not None and 'job_hopper_premium' in atl_fed.columns:
        premium = atl_fed['job_hopper_premium'].dropna()
    else:
        print("  Warning: Job hopper premium data not found")
        return None

    # Filter to post-2010
    premium = premium[premium.index >= '2010-01-01']

    fig, ax = plt.subplots(figsize=(12, 7))
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')

    # Main line
    color = LIGHTHOUSE_COLORS['ocean_blue']
    ax.plot(premium.index, premium, color=color, linewidth=2.5, label='Job-Hopper Premium')
    ax.fill_between(premium.index, premium, alpha=0.2, color=color)

    # Threshold lines
    ax.axhline(y=0.5, color=LIGHTHOUSE_COLORS['dusk_orange'], linestyle='--',
               linewidth=1.5, alpha=0.8)
    ax.text(premium.index[0], 0.6, 'Late-Cycle Threshold (0.5 ppts)',
            fontsize=8, color=LIGHTHOUSE_COLORS['dusk_orange'])

    ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)

    # Zone shading
    ax.axhspan(-1, 0.5, color=LIGHTHOUSE_COLORS['pure_red'], alpha=0.08, label='Late-Cycle Zone')
    ax.axhspan(1.5, 6, color=LIGHTHOUSE_COLORS['lime_green'], alpha=0.08, label='Healthy Zone')

    # Annotations for key periods
    # 2022 peak
    peak_date = premium.idxmax()
    peak_val = premium.max()
    ax.annotate(f'Peak: {peak_val:.1f} ppts\n({peak_date.strftime("%b %Y")})',
                xy=(peak_date, peak_val), xytext=(-60, 20),
                textcoords='offset points', fontsize=9,
                bbox=dict(boxstyle='round', facecolor='white', edgecolor='gray'))

    # Current value
    current_val = premium.iloc[-1]
    current_date = premium.index[-1]
    ax.annotate(f'Current: {current_val:.1f} ppts',
                xy=(current_date, current_val), xytext=(10, 30),
                textcoords='offset points', fontsize=9, fontweight='bold',
                color=LIGHTHOUSE_COLORS['hot_magenta'],
                bbox=dict(boxstyle='round', facecolor='white',
                         edgecolor=LIGHTHOUSE_COLORS['hot_magenta']))

    # Styling
    ax.set_ylabel('Premium (Percentage Points)', fontsize=10)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.1f} ppts'))

    apply_lhm_style(ax, 'Job-Hopper Premium: Switchers vs. Stayers Wage Growth',
                    subtitle='"The grass is no longer greener"')

    ax.legend(loc='upper right', framealpha=0.95)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    return save_fig(fig, 'chart_2_job_hopper_premium.png')


# ============================================
# CHART 3: Youth vs. Prime-Age Unemployment
# ============================================
def chart_3_youth_vs_prime_age():
    """
    Youth unemployment as leading indicator.
    Key insight: Youth leads prime-age by 3-4 months with 2x amplitude.
    """
    print("\nChart 3: Youth vs Prime-Age Unemployment...")

    subset = df[['Unemp_Rate_16_24', 'Unemp_Rate_25_54', 'Unemployment_Rate']].dropna()

    fig, ax = plt.subplots(figsize=(12, 7))
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')

    # Plot series
    ax.plot(subset.index, subset['Unemp_Rate_16_24'],
            color=LIGHTHOUSE_COLORS['ocean_blue'], linewidth=2.5,
            label='Youth (16-24) - Leading')
    ax.plot(subset.index, subset['Unemp_Rate_25_54'],
            color=LIGHTHOUSE_COLORS['dusk_orange'], linewidth=2,
            label='Prime-Age (25-54) - Lagging')
    ax.plot(subset.index, subset['Unemployment_Rate'],
            color=LIGHTHOUSE_COLORS['neutral_gray'], linewidth=1.5,
            linestyle='--', label='Overall')

    # Add recession shading
    add_recession_bars(ax)

    # Threshold zones
    ax.axhspan(11, 20, color=LIGHTHOUSE_COLORS['pure_red'], alpha=0.05)
    ax.text(subset.index[10], 11.5, 'Youth Stress Zone (>11%)',
            fontsize=8, color=LIGHTHOUSE_COLORS['pure_red'], alpha=0.7)

    # Current values
    current_youth = subset['Unemp_Rate_16_24'].iloc[-1]
    current_prime = subset['Unemp_Rate_25_54'].iloc[-1]

    ax.annotate(f'Youth: {current_youth:.1f}%',
                xy=(subset.index[-1], current_youth),
                xytext=(10, 10), textcoords='offset points',
                fontsize=9, fontweight='bold',
                color=LIGHTHOUSE_COLORS['ocean_blue'])
    ax.annotate(f'Prime: {current_prime:.1f}%',
                xy=(subset.index[-1], current_prime),
                xytext=(10, -15), textcoords='offset points',
                fontsize=9, fontweight='bold',
                color=LIGHTHOUSE_COLORS['dusk_orange'])

    # Styling
    ax.set_ylabel('Unemployment Rate (%)', fontsize=10)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.1f}%'))
    ax.set_ylim(0, max(subset['Unemp_Rate_16_24'].max() * 1.1, 20))

    apply_lhm_style(ax, 'Youth vs. Prime-Age Unemployment\nYouth as the Canary')

    ax.legend(loc='upper left', framealpha=0.95)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    return save_fig(fig, 'chart_3_youth_vs_prime_age.png')


# ============================================
# CHART 4: Temp Help Employment YoY%
# ============================================
def chart_4_temp_help():
    """
    Temp help as leading indicator.
    Key insight: Below -3% YoY = recession signal.
    """
    print("\nChart 4: Temp Help Employment YoY%...")

    if 'Emp_Temp_Help' not in df.columns:
        print("  Warning: Temp help data not found")
        return None

    temp_help = df['Emp_Temp_Help'].dropna()
    temp_help_yoy = temp_help.pct_change(12) * 100  # YoY %
    temp_help_yoy = temp_help_yoy.dropna()

    fig, ax = plt.subplots(figsize=(12, 7))
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')

    # Bar chart with color coding
    colors = [LIGHTHOUSE_COLORS['ocean_blue'] if x >= 0
              else (LIGHTHOUSE_COLORS['pure_red'] if x < -3
                    else LIGHTHOUSE_COLORS['dusk_orange'])
              for x in temp_help_yoy]

    ax.bar(temp_help_yoy.index, temp_help_yoy, color=colors, alpha=0.7, width=25)

    # Threshold lines
    ax.axhline(y=0, color='black', linewidth=0.5)
    ax.axhline(y=-3, color=LIGHTHOUSE_COLORS['pure_red'], linestyle='--',
               linewidth=2, alpha=0.8)
    ax.text(temp_help_yoy.index[5], -2.5, 'Recession Signal (-3%)',
            fontsize=9, color=LIGHTHOUSE_COLORS['pure_red'], fontweight='bold')

    # Add recession shading
    add_recession_bars(ax)

    # Current value annotation
    current_val = temp_help_yoy.iloc[-1]
    ax.annotate(f'Current: {current_val:.1f}%',
                xy=(temp_help_yoy.index[-1], current_val),
                xytext=(10, 30 if current_val < 0 else -30),
                textcoords='offset points',
                fontsize=10, fontweight='bold',
                color=LIGHTHOUSE_COLORS['hot_magenta'],
                bbox=dict(boxstyle='round', facecolor='white',
                         edgecolor=LIGHTHOUSE_COLORS['hot_magenta']))

    # Styling
    ax.set_ylabel('Year-over-Year Change (%)', fontsize=10)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.0f}%'))

    apply_lhm_style(ax, 'Temp Help Employment: YoY Change\n"First Hired, First Fired"')

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    return save_fig(fig, 'chart_4_temp_help_yoy.png')


# ============================================
# CHART 5: State Unemployment Diffusion
# ============================================
def chart_5_state_diffusion():
    """
    Percentage of states with rising unemployment.
    Key insight: >50% = broad-based weakness.
    """
    print("\nChart 5: State Unemployment Diffusion...")

    # Get all state unemployment columns
    state_cols = [c for c in df.columns if c.startswith('Unemp_Rate_')
                  and len(c) == len('Unemp_Rate_XX')]

    if len(state_cols) < 40:
        print(f"  Warning: Only found {len(state_cols)} state columns")
        return None

    states_df = df[state_cols].dropna(how='all')

    # Calculate 3-month change for each state
    states_3m_change = states_df.diff(3)

    # Calculate diffusion: % of states with rising unemployment
    diffusion = (states_3m_change > 0).sum(axis=1) / len(state_cols) * 100
    diffusion = diffusion.dropna()

    # Filter to recent years
    diffusion = diffusion[diffusion.index >= '2005-01-01']

    fig, ax = plt.subplots(figsize=(12, 7))
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')

    # Main line
    ax.plot(diffusion.index, diffusion, color=LIGHTHOUSE_COLORS['ocean_blue'],
            linewidth=2.5, label='% of States with Rising Unemployment (3M)')
    ax.fill_between(diffusion.index, diffusion, alpha=0.2,
                   color=LIGHTHOUSE_COLORS['ocean_blue'])

    # Threshold zones
    ax.axhspan(50, 100, color=LIGHTHOUSE_COLORS['pure_red'], alpha=0.08)
    ax.axhline(y=50, color=LIGHTHOUSE_COLORS['dusk_orange'], linestyle='--',
               linewidth=2, alpha=0.8)
    ax.text(diffusion.index[5], 52, 'Broad-Based Weakness (>50%)',
            fontsize=9, color=LIGHTHOUSE_COLORS['dusk_orange'], fontweight='bold')

    ax.axhline(y=70, color=LIGHTHOUSE_COLORS['pure_red'], linestyle='--',
               linewidth=1.5, alpha=0.8)
    ax.text(diffusion.index[5], 72, 'Pervasive Weakness (>70%)',
            fontsize=9, color=LIGHTHOUSE_COLORS['pure_red'])

    # Add recession shading
    add_recession_bars(ax, '2005-01-01')

    # Current value
    current_val = diffusion.iloc[-1]
    ax.annotate(f'Current: {current_val:.0f}%',
                xy=(diffusion.index[-1], current_val),
                xytext=(10, 20), textcoords='offset points',
                fontsize=10, fontweight='bold',
                color=LIGHTHOUSE_COLORS['hot_magenta'],
                bbox=dict(boxstyle='round', facecolor='white',
                         edgecolor=LIGHTHOUSE_COLORS['hot_magenta']))

    # Styling
    ax.set_ylabel('% of States', fontsize=10)
    ax.set_ylim(0, 100)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.0f}%'))

    apply_lhm_style(ax, 'State Unemployment Diffusion Index\n"Weakness is Spreading"')

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    return save_fig(fig, 'chart_5_state_diffusion.png')


# ============================================
# CHART 6: Labor Fragility Index (LFI)
# ============================================
def chart_6_labor_fragility_index():
    """
    Composite LFI indicator.
    Formula: 0.30*LT_Unemp + 0.25*(-Quits) + 0.20*(-Hires/Quits) + 0.15*(-TempHelp) + 0.10*(-JobHopper)
    """
    print("\nChart 6: Labor Fragility Index...")

    # Calculate LFI components
    # For now, use simplified version with available data

    # 1. Long-term unemployed share
    if 'Unemp_27_Weeks_Plus' in df.columns and 'Unemp_Total_Level' in df.columns:
        lt_unemp_share = df['Unemp_27_Weeks_Plus'] / df['Unemp_Total_Level'] * 100
    else:
        lt_unemp_share = pd.Series(index=df.index, dtype=float)

    # 2. Quits rate (inverted)
    quits = df['JOLTS_Quits_Rate'] if 'JOLTS_Quits_Rate' in df.columns else pd.Series(index=df.index, dtype=float)

    # 3. Temp help YoY (inverted)
    if 'Emp_Temp_Help' in df.columns:
        temp_help_yoy = df['Emp_Temp_Help'].pct_change(12) * 100
    else:
        temp_help_yoy = pd.Series(index=df.index, dtype=float)

    # 4. Job-hopper premium (inverted)
    job_hopper = df['AtlFed_Job_Hopper_Premium'] if 'AtlFed_Job_Hopper_Premium' in df.columns else pd.Series(index=df.index, dtype=float)

    # Calculate z-scores (rolling 36-month)
    def rolling_zscore(series, window=36):
        mean = series.rolling(window, min_periods=12).mean()
        std = series.rolling(window, min_periods=12).std()
        return (series - mean) / std

    # Combine into LFI
    z_lt_unemp = rolling_zscore(lt_unemp_share)
    z_quits = -rolling_zscore(quits)  # Inverted
    z_temp = -rolling_zscore(temp_help_yoy)  # Inverted
    z_hopper = -rolling_zscore(job_hopper)  # Inverted

    # Weighted average (simplified weights)
    lfi = (0.35 * z_lt_unemp.fillna(0) +
           0.35 * z_quits.fillna(0) +
           0.20 * z_temp.fillna(0) +
           0.10 * z_hopper.fillna(0))

    lfi = lfi.dropna()
    lfi = lfi[lfi.index >= '2005-01-01']

    fig, ax = plt.subplots(figsize=(12, 7))
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')

    # Main line
    ax.plot(lfi.index, lfi, color=LIGHTHOUSE_COLORS['ocean_blue'],
            linewidth=2.5, label='Labor Fragility Index (LFI)')
    ax.fill_between(lfi.index, lfi, where=(lfi > 0.5),
                   color=LIGHTHOUSE_COLORS['dusk_orange'], alpha=0.3)
    ax.fill_between(lfi.index, lfi, where=(lfi > 1.0),
                   color=LIGHTHOUSE_COLORS['pure_red'], alpha=0.3)

    # Threshold zones
    ax.axhspan(0.5, 1.0, color=LIGHTHOUSE_COLORS['dusk_orange'], alpha=0.1, label='Elevated')
    ax.axhspan(1.0, 3.0, color=LIGHTHOUSE_COLORS['pure_red'], alpha=0.1, label='High/Critical')
    ax.axhline(y=0.5, color=LIGHTHOUSE_COLORS['dusk_orange'], linestyle='--', linewidth=1.5)
    ax.axhline(y=1.0, color=LIGHTHOUSE_COLORS['pure_red'], linestyle='--', linewidth=1.5)
    ax.axhline(y=0, color='black', linewidth=0.5)

    # Labels
    ax.text(lfi.index[5], 0.55, 'Elevated (0.5-1.0)', fontsize=8,
            color=LIGHTHOUSE_COLORS['dusk_orange'])
    ax.text(lfi.index[5], 1.05, 'High Risk (>1.0)', fontsize=8,
            color=LIGHTHOUSE_COLORS['pure_red'])

    # Add recession shading
    add_recession_bars(ax, '2005-01-01')

    # Current value
    current_val = lfi.iloc[-1]
    ax.annotate(f'Current LFI: {current_val:.2f}',
                xy=(lfi.index[-1], current_val),
                xytext=(10, 20), textcoords='offset points',
                fontsize=10, fontweight='bold',
                color=LIGHTHOUSE_COLORS['hot_magenta'],
                bbox=dict(boxstyle='round', facecolor='white',
                         edgecolor=LIGHTHOUSE_COLORS['hot_magenta']))

    # Styling
    ax.set_ylabel('LFI (Z-Score Composite)', fontsize=10)

    apply_lhm_style(ax, 'Labor Fragility Index (LFI)\nComposite Leading Indicator')

    ax.legend(loc='upper left', framealpha=0.95)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    return save_fig(fig, 'chart_6_labor_fragility_index.png')


# ============================================
# CHART 7: Transmission Chain Schematic
# ============================================
def chart_7_transmission_chain():
    """
    Schematic showing Labor → Consumer → Credit → Housing cascade.
    """
    print("\nChart 7: Transmission Chain Schematic...")

    fig, ax = plt.subplots(figsize=(14, 8))
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 8)
    ax.axis('off')

    # Colors
    box_color = LIGHTHOUSE_COLORS['ocean_blue']
    arrow_color = LIGHTHOUSE_COLORS['dusk_orange']

    # Box positions
    boxes = [
        (1, 4, 'LABOR', '1-3 mo lag'),
        (4.5, 4, 'CONSUMER', '68% of GDP'),
        (8, 4, 'CREDIT', '3-6 mo lag'),
        (11.5, 4, 'HOUSING', '6-9 mo lag'),
    ]

    # Draw boxes
    for x, y, title, subtitle in boxes:
        rect = plt.Rectangle((x-0.8, y-0.8), 2.2, 1.6, linewidth=2,
                             edgecolor=box_color, facecolor='white', zorder=3)
        ax.add_patch(rect)
        ax.text(x+0.3, y+0.1, title, fontsize=12, fontweight='bold',
               color=box_color, ha='center', va='center')
        ax.text(x+0.3, y-0.4, subtitle, fontsize=9, color='gray',
               ha='center', va='center', style='italic')

    # Draw arrows
    for i in range(len(boxes)-1):
        x1, y1 = boxes[i][0] + 1.4, boxes[i][1]
        x2, y2 = boxes[i+1][0] - 0.8, boxes[i+1][1]
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                   arrowprops=dict(arrowstyle='->', color=arrow_color, lw=2))

    # Add explanatory text
    explanations = [
        (2.75, 2.5, 'Employment × Hours × Wages\n= Income'),
        (6.25, 2.5, 'Income → Spending\n→ Corporate Revenue'),
        (9.75, 2.5, 'Income Loss →\nDebt Service Strain'),
        (2.75, 5.5, 'Quits, Hires, Claims\n(Leading Indicators)'),
        (9.75, 5.5, 'Delinquencies Rise\n→ Spreads Widen'),
    ]

    for x, y, text in explanations:
        ax.text(x, y, text, fontsize=9, color='#555555',
               ha='center', va='center',
               bbox=dict(boxstyle='round', facecolor='#f0f0f0',
                        edgecolor='#cccccc', alpha=0.8))

    # Title
    ax.text(7, 7.3, 'The Labor Transmission Chain', fontsize=16,
            fontweight='bold', ha='center', color=LIGHTHOUSE_COLORS['ocean_blue'])
    ax.text(7, 6.8, '"Get the labor call right, and you\'ve triangulated 70% of the macro outlook"',
            fontsize=10, ha='center', style='italic', color='#666666')

    # Branding
    ax.text(0.5, 0.5, 'LIGHTHOUSE MACRO', fontsize=8,
            color=LIGHTHOUSE_COLORS['ocean_blue'], fontweight='bold')
    ax.text(13.5, 0.5, 'MACRO, ILLUMINATED.', fontsize=7,
            color=LIGHTHOUSE_COLORS['hot_magenta'], ha='right', style='italic')

    return save_fig(fig, 'chart_7_transmission_chain.png')


# ============================================
# MAIN EXECUTION
# ============================================
def main():
    """Generate all charts for educational post."""
    print("="*60)
    print("GENERATING EDUCATIONAL CHARTS: LABOR POST 1")
    print("="*60)
    print(f"Output directory: {OUTPUT_DIR}")

    charts_generated = []

    # Generate each chart
    result = chart_1_quits_vs_unemployment()
    if result: charts_generated.append(result)

    result = chart_2_job_hopper_premium()
    if result: charts_generated.append(result)

    result = chart_3_youth_vs_prime_age()
    if result: charts_generated.append(result)

    result = chart_4_temp_help()
    if result: charts_generated.append(result)

    result = chart_5_state_diffusion()
    if result: charts_generated.append(result)

    result = chart_6_labor_fragility_index()
    if result: charts_generated.append(result)

    result = chart_7_transmission_chain()
    if result: charts_generated.append(result)

    print("\n" + "="*60)
    print(f"COMPLETE: {len(charts_generated)} charts generated")
    print("="*60)
    for path in charts_generated:
        print(f"  {os.path.basename(path)}")
    print("="*60)

    return charts_generated


if __name__ == "__main__":
    main()
