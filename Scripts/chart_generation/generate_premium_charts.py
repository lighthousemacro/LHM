"""
LIGHTHOUSE MACRO - Premium Chart Templates
Matching the institutional quality of the template images

Style features:
- Stacked area fills with recession shading
- Zone backgrounds (stress/normal)
- Last value labels on axis
- Dual axis when appropriate
- Annotations with callout boxes
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
from datetime import datetime, timedelta
import warnings
import os

warnings.filterwarnings('ignore')

from real_data_fetcher import RealDataFetcher
from lighthouse_chart_style import (
    LIGHTHOUSE_COLORS,
    apply_lighthouse_style,
    add_last_value_label,
    add_callout_box,
    create_figure,
)

# Configuration
OUTPUT_DIR = '/Users/bob/Desktop/HORIZON_FINAL./charts'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Initialize data fetcher
data = RealDataFetcher()


def add_recession_shading(ax, recessions=None):
    """Add recession bars"""
    if recessions is None:
        recessions = [
            ('2001-03-01', '2001-11-01'),
            ('2007-12-01', '2009-06-01'),
            ('2020-02-01', '2020-04-01'),
        ]
    for start, end in recessions:
        ax.axvspan(pd.Timestamp(start), pd.Timestamp(end),
                   color='gray', alpha=0.15, zorder=0)


def save_chart(fig, filename):
    """Save with consistent settings"""
    filepath = os.path.join(OUTPUT_DIR, filename)
    fig.tight_layout()
    fig.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f"  OK: {filename}")
    return filepath


# =============================================================================
# CHART 1: Credit Spread Waterfall (Stacked Area)
# =============================================================================

def chart_credit_spread_waterfall():
    """Credit Spread Waterfall - Stacked area of AAA/BBB/HY"""
    print("Generating: Credit Spread Waterfall...")

    spreads = data.get_credit_spreads()

    if len(spreads.get('HY', [])) == 0:
        print("    ERROR: No spread data")
        return None

    fig, ax = create_figure(figsize=(16, 9))

    # Align all series to common index
    aaa = spreads['AAA'] * 100  # Convert to bps
    bbb = spreads['BBB'] * 100
    hy = spreads['HY'] * 100

    # Use common date range
    common_idx = aaa.index.intersection(bbb.index).intersection(hy.index)
    aaa = aaa.loc[common_idx]
    bbb = bbb.loc[common_idx]
    hy = hy.loc[common_idx]

    dates = common_idx

    # Stacked area fill
    ax.fill_between(dates, 0, aaa, color='#238923', alpha=0.6, label='AAA')
    ax.fill_between(dates, aaa, aaa + bbb, color=LIGHTHOUSE_COLORS['ocean_blue'], alpha=0.6, label='BBB')
    ax.fill_between(dates, aaa + bbb, aaa + bbb + hy, color=LIGHTHOUSE_COLORS['pure_red'], alpha=0.5, label='HY')

    # Add recession shading
    add_recession_shading(ax)

    # Current values on axis - all 3 series with labels right on axis
    current_aaa = aaa.iloc[-1]
    current_bbb = bbb.iloc[-1]
    current_hy = hy.iloc[-1]

    # Calculate y positions for each label (midpoint of each band)
    aaa_y_pos = current_aaa / 2
    bbb_y_pos = current_aaa + current_bbb / 2
    hy_y_pos = current_aaa + current_bbb + current_hy / 2

    # Need to add custom labels since add_last_value_label uses value for both position and text
    # Create custom labels directly
    ylim = ax.get_ylim()

    for (label, value, y_pos, color) in [
        ('AAA', current_aaa, aaa_y_pos, '#238923'),
        ('BBB', current_bbb, bbb_y_pos, LIGHTHOUSE_COLORS['ocean_blue']),
        ('HY', current_hy, hy_y_pos, LIGHTHOUSE_COLORS['pure_red'])
    ]:
        y_norm = (y_pos - ylim[0]) / (ylim[1] - ylim[0])
        y_norm = max(0.02, min(0.98, y_norm))

        bbox_props = dict(boxstyle='round,pad=0.3', facecolor=color,
                         edgecolor=color, alpha=1.0, linewidth=0)
        ax.text(1.005, y_norm, f'{label}: {value:.0f}',
                transform=ax.transAxes, fontsize=9, fontweight='bold',
                color='white', ha='left', va='center', bbox=bbox_props,
                zorder=100, clip_on=False)

    # Style
    ax.set_ylabel('Spread (bps)', fontsize=11)
    ax.set_xlabel('Date', fontsize=10)
    ax.set_ylim(bottom=0)
    ax.legend(loc='upper right', framealpha=0.95)

    # 4 spines
    for spine in ['top', 'right', 'left', 'bottom']:
        ax.spines[spine].set_visible(True)
        ax.spines[spine].set_linewidth(0.5)
        ax.spines[spine].set_color('#666666')

    ax.set_title('CREDIT SPREAD WATERFALL', fontsize=14, fontweight='bold', pad=20)
    ax.text(0.01, 1.02, 'LIGHTHOUSE MACRO', transform=ax.transAxes, fontsize=8,
            color=LIGHTHOUSE_COLORS['ocean_blue'], fontweight='bold')
    ax.text(0.99, -0.06, 'MACRO, ILLUMINATED.', transform=ax.transAxes, fontsize=7,
            color=LIGHTHOUSE_COLORS['hot_magenta'], ha='right', style='italic')

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax.xaxis.set_major_locator(mdates.YearLocator(4))

    return save_chart(fig, 'S1_08_Credit_Spread_Waterfall.png')


# =============================================================================
# CHART 2: Yield Curve Evolution Heatmap
# =============================================================================

def chart_yield_curve_heatmap():
    """Yield Curve Evolution - Heatmap over time"""
    print("Generating: Yield Curve Heatmap...")

    yields = data.get_yield_curve()

    fig, ax = plt.subplots(figsize=(16, 9), dpi=150)
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')

    # Build matrix - tenors as rows, dates as columns
    tenors = ['3M', '6M', '1Y', '2Y', '3Y', '5Y', '7Y', '10Y', '20Y', '30Y']
    tenor_labels = ['1m', '3m', '6m', '1y', '2y', '3y', '5y', '7y', '10y', '20y', '30y']

    # Get common dates (last 5 years weekly resampled)
    start_date = '2020-01-01'

    # Build data matrix
    data_matrix = []
    valid_tenors = []

    for tenor in tenors:
        if tenor in yields and len(yields[tenor]) > 0:
            series = yields[tenor][yields[tenor].index >= start_date]
            # Resample to weekly to reduce noise
            series = series.resample('W').last()
            data_matrix.append(series)
            valid_tenors.append(tenor)

    if not data_matrix:
        print("    ERROR: No yield data")
        return None

    # Align all series
    df = pd.concat(data_matrix, axis=1)
    df.columns = valid_tenors
    df = df.dropna()

    # Create heatmap
    matrix = df.values.T
    dates = df.index

    im = ax.imshow(matrix, aspect='auto', cmap='RdYlBu_r',
                   extent=[mdates.date2num(dates[0]), mdates.date2num(dates[-1]),
                          len(valid_tenors)-0.5, -0.5],
                   vmin=0, vmax=6)

    # Colorbar
    cbar = plt.colorbar(im, ax=ax, pad=0.02)
    cbar.set_label('Yield (%)', fontsize=10)

    # Axis formatting
    ax.xaxis_date()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=0)

    ax.set_yticks(range(len(valid_tenors)))
    ax.set_yticklabels(valid_tenors)
    ax.set_ylabel('Tenor', fontsize=11)

    ax.set_title('YIELD CURVE EVOLUTION', fontsize=14, fontweight='bold', pad=20)
    ax.text(0.01, 1.02, 'LIGHTHOUSE MACRO', transform=ax.transAxes, fontsize=8,
            color=LIGHTHOUSE_COLORS['ocean_blue'], fontweight='bold')
    ax.text(0.99, -0.08, 'MACRO, ILLUMINATED.', transform=ax.transAxes, fontsize=7,
            color=LIGHTHOUSE_COLORS['hot_magenta'], ha='right', style='italic')

    return save_chart(fig, 'S2_02_Yield_Curve_Heatmap.png')


# =============================================================================
# CHART 3: Bank Reserves vs GDP - With Event Annotations
# =============================================================================

def chart_reserves_gdp_annotated():
    """Bank Reserves as % of GDP with historical events annotated"""
    print("Generating: Bank Reserves vs GDP (Annotated)...")

    reserves_data = data.get_reserves_and_rrp()
    reserves = reserves_data.get('reserves', pd.Series())

    if len(reserves) == 0:
        print("    ERROR: No reserves data")
        return None

    fig, ax = create_figure(figsize=(16, 9))

    # WRESBAL is in millions of dollars
    # Convert to % of GDP (assuming ~$29T GDP = 29,000,000 millions)
    gdp_millions = 29_000_000  # GDP in millions
    reserves_pct = (reserves / gdp_millions) * 100

    dates = reserves_pct.index
    values = reserves_pct.values

    # Debug: print actual range
    print(f"    Reserves % of GDP range: {values.min():.2f}% to {values.max():.2f}%")

    # Zone shading - adjusted for actual data range
    ax.axhspan(0, 8, color=LIGHTHOUSE_COLORS['pure_red'], alpha=0.1, label='Crisis Zone (<8%)')
    ax.axhspan(8, 12, color=LIGHTHOUSE_COLORS['dusk_orange'], alpha=0.1, label='Warning (8-12%)')
    ax.axhspan(12, 20, color=LIGHTHOUSE_COLORS['teal_green'], alpha=0.1, label='Comfortable (>12%)')

    # Main line with fill
    ax.fill_between(dates, 0, values, color=LIGHTHOUSE_COLORS['ocean_blue'], alpha=0.4)
    ax.plot(dates, values, color=LIGHTHOUSE_COLORS['ocean_blue'], linewidth=2.5)

    # Key events annotations - find actual values at those dates
    event_dates = [
        ('2008-09-15', 'Financial Crisis\nQE1'),
        ('2011-06-01', 'Taper\nTantrum'),
        ('2019-09-17', 'Repo\nCrisis'),
        ('2020-03-15', 'COVID\nQE'),
    ]

    for date_str, label in event_dates:
        try:
            date = pd.Timestamp(date_str)
            if date >= dates.min() and date <= dates.max():
                # Find closest date in data
                idx = reserves_pct.index.get_indexer([date], method='nearest')[0]
                y_val = values[idx]
                ax.annotate(label, (reserves_pct.index[idx], y_val),
                           fontsize=8, ha='center', va='bottom',
                           xytext=(0, 10), textcoords='offset points',
                           bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                                    edgecolor='gray', alpha=0.9))
                ax.scatter([reserves_pct.index[idx]], [y_val], color=LIGHTHOUSE_COLORS['hot_magenta'],
                          s=60, zorder=5)
        except:
            pass

    # Threshold lines - adjusted
    ax.axhline(y=8, color=LIGHTHOUSE_COLORS['pure_red'], linestyle='--', linewidth=1.5)
    ax.axhline(y=12, color=LIGHTHOUSE_COLORS['dusk_orange'], linestyle='--', linewidth=1.5)

    # Last value on axis
    current = values[-1]
    add_last_value_label(ax, current, LIGHTHOUSE_COLORS['ocean_blue'],
                         label_format='{:.1f}%', side='right')

    # Callout
    add_callout_box(ax,
                    f"Current Status (2025):\n"
                    f"• Reserves: {current:.1f}% of GDP\n"
                    f"• Sept 2019: 11.0% of GDP\n"
                    f"• Distribution: Top 25 banks\n"
                    f"  hold 85% of reserves\n"
                    f"• Risk: Concentrated, not ample",
                    (0.02, 0.95), fontsize=8)

    ax.set_ylabel('Bank Reserves as % of GDP', fontsize=11)
    ax.set_xlabel('Year', fontsize=10)
    # Auto-scale y-axis based on data with padding
    ax.set_ylim(0, max(values) * 1.15)
    ax.legend(loc='upper right', framealpha=0.95)

    # 4 spines
    for spine in ['top', 'right', 'left', 'bottom']:
        ax.spines[spine].set_visible(True)
        ax.spines[spine].set_linewidth(0.5)
        ax.spines[spine].set_color('#666666')

    ax.set_title('Bank Reserves vs GDP: Distribution Matters More Than Level',
                 fontsize=14, fontweight='bold', pad=20)
    ax.text(0.01, 1.02, 'LIGHTHOUSE MACRO', transform=ax.transAxes, fontsize=8,
            color=LIGHTHOUSE_COLORS['ocean_blue'], fontweight='bold')
    ax.text(0.99, -0.06, 'MACRO, ILLUMINATED.', transform=ax.transAxes, fontsize=7,
            color=LIGHTHOUSE_COLORS['hot_magenta'], ha='right', style='italic')

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    return save_chart(fig, 'S2_04_Bank_Reserves_GDP_Annotated.png')


# =============================================================================
# CHART 4: SOFR-EFFR Spread with Zone Shading
# =============================================================================

def chart_sofr_effr_zones():
    """SOFR-EFFR with stress zone shading like the template"""
    print("Generating: SOFR-EFFR Spread (Zone Style)...")

    spread_data = data.get_sofr_effr_spread()

    if len(spread_data) == 0:
        print("    ERROR: No data")
        return None

    fig, ax = create_figure(figsize=(16, 9))

    dates = spread_data.index
    spread = spread_data['spread']

    # Debug: print actual range
    print(f"    SOFR-EFFR spread range: {spread.min():.2f} to {spread.max():.2f} bps")

    # Auto-calculate y limits based on data
    y_min = min(0, spread.min() - 2)
    y_max = max(20, spread.max() + 5)

    # Zone shading - adjust to actual data range
    ax.axhspan(15, y_max, color=LIGHTHOUSE_COLORS['pure_red'], alpha=0.15, label='Stress Zone (>15 bps)')
    ax.axhspan(8, 15, color=LIGHTHOUSE_COLORS['dusk_orange'], alpha=0.1, label='Warning (8-15 bps)')
    ax.axhspan(y_min, 8, color=LIGHTHOUSE_COLORS['ocean_blue'], alpha=0.1, label='Normal (<8 bps)')

    # Daily spread (ocean blue - darker than cyan)
    ax.plot(dates, spread, color=LIGHTHOUSE_COLORS['ocean_blue'], linewidth=0.8, alpha=0.8)

    # 20-day MA (thick magenta)
    spread_data['ma20'] = spread.rolling(20).mean()
    ax.plot(dates, spread_data['ma20'], color=LIGHTHOUSE_COLORS['hot_magenta'],
            linewidth=2.5, label='20-Day Moving Avg')

    # Stress threshold
    ax.axhline(y=15, color=LIGHTHOUSE_COLORS['pure_red'], linestyle='--', linewidth=2)
    ax.text(dates[10], 16, 'STRESS THRESHOLD (15 bps)', fontsize=9,
            color=LIGHTHOUSE_COLORS['pure_red'], fontweight='bold')

    # Current value box
    current = spread.iloc[-1]
    current_ma = spread_data['ma20'].dropna().iloc[-1]

    # Callout box top right
    ax.text(0.98, 0.95, f'Current: {current:.0f} bps\n20D Avg: {current_ma:.0f} bps',
            transform=ax.transAxes, fontsize=10, fontweight='bold',
            ha='right', va='top',
            bbox=dict(boxstyle='round', facecolor=LIGHTHOUSE_COLORS['pure_red'],
                     edgecolor='none', alpha=0.9),
            color='white')

    ax.set_ylabel('SOFR-EFFR Spread (Basis Points)', fontsize=11)
    ax.set_xlabel('Date', fontsize=10)
    ax.set_ylim(y_min, y_max)
    ax.legend(loc='upper left', framealpha=0.95)

    # 4 spines
    for spine in ['top', 'right', 'left', 'bottom']:
        ax.spines[spine].set_visible(True)
        ax.spines[spine].set_linewidth(0.5)
        ax.spines[spine].set_color('#666666')

    ax.set_title('SOFR-EFFR Spread: Funding Market Early Warning',
                 fontsize=14, fontweight='bold', pad=20)
    ax.text(0.01, 1.02, 'LIGHTHOUSE MACRO', transform=ax.transAxes, fontsize=8,
            color=LIGHTHOUSE_COLORS['ocean_blue'], fontweight='bold')
    ax.text(0.99, -0.06, 'MACRO, ILLUMINATED.', transform=ax.transAxes, fontsize=7,
            color=LIGHTHOUSE_COLORS['hot_magenta'], ha='right', style='italic')

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))

    return save_chart(fig, 'S2_16_SOFR_EFFR_Zones.png')


# =============================================================================
# CHART 5: Federal Debt Dual Axis (Bar + Line)
# =============================================================================

def chart_federal_debt_dual():
    """Federal Debt - Bar chart with Debt/GDP line overlay"""
    print("Generating: Federal Debt (Dual Axis)...")

    debt_data = data.get_debt_data()
    debt = debt_data.get('total', pd.Series())
    debt_gdp = debt_data.get('debt_gdp', pd.Series())

    if len(debt) == 0:
        print("    ERROR: No debt data")
        return None

    fig, ax1 = create_figure(figsize=(16, 9))
    ax2 = ax1.twinx()

    # Convert to trillions
    debt_t = debt / 1e6

    # Filter to reasonable range
    debt_t = debt_t[debt_t.index >= '1998-01-01']
    debt_gdp = debt_gdp[debt_gdp.index >= '1998-01-01']

    # Find common start date so both series start at left axis
    common_start = max(debt_t.index.min(), debt_gdp.index.min())
    debt_t = debt_t[debt_t.index >= common_start]
    debt_gdp = debt_gdp[debt_gdp.index >= common_start]

    # Bar chart for debt level (left axis)
    dates = debt_t.index
    width = 200  # days

    # Color bars by period
    colors = []
    for d in dates:
        if d.year >= 2024:
            colors.append(LIGHTHOUSE_COLORS['pure_red'])
        elif d.year >= 2020:
            colors.append(LIGHTHOUSE_COLORS['dusk_orange'])
        else:
            colors.append(LIGHTHOUSE_COLORS['ocean_blue'])

    ax1.bar(dates, debt_t.values, width=width, color=colors, alpha=0.7, label='Debt Outstanding ($T)')

    # Line for Debt/GDP ratio (right axis) - sea green
    ax2.plot(debt_gdp.index, debt_gdp.values, color=LIGHTHOUSE_COLORS['teal_green'],
             linewidth=2.5, marker='o', markersize=4, label='Debt-to-GDP (%)')

    # Threshold lines
    ax2.axhline(y=90, color=LIGHTHOUSE_COLORS['dusk_orange'], linestyle='--', linewidth=1.5, alpha=0.7)
    ax2.axhline(y=120, color='#4B9CD3', linestyle='--', linewidth=2)  # Carolina blue

    # Position labels at better spots - 90% at 25% from left, 120% at midpoint
    mid_idx = len(dates) // 2
    quarter_idx = len(dates) // 4
    ax2.text(dates[quarter_idx], 91, '90% Threshold (Reinhart-Rogoff)', fontsize=8,
             color=LIGHTHOUSE_COLORS['dusk_orange'], ha='center',
             bbox=dict(boxstyle='round,pad=0.2', facecolor='white', edgecolor=LIGHTHOUSE_COLORS['dusk_orange'], alpha=0.9))
    ax2.text(dates[mid_idx], 121, '120% Threshold (Crossed 2024)', fontsize=8,
             color='#4B9CD3', ha='center',
             bbox=dict(boxstyle='round,pad=0.2', facecolor='white', edgecolor='#4B9CD3', alpha=0.9))

    # Callout
    current_debt = debt_t.iloc[-1]
    current_ratio = debt_gdp.iloc[-1]

    add_callout_box(ax1,
                    f"December 2025:\n"
                    f"Debt: ${current_debt:.1f}T\n"
                    f"Debt/GDP: {current_ratio:.0f}%\n"
                    f"Growth Since 2019: +59%",
                    (0.02, 0.95), fontsize=9)

    ax1.set_ylabel('Federal Debt Outstanding ($ Trillions)', fontsize=11, color=LIGHTHOUSE_COLORS['pure_red'])
    ax1.tick_params(axis='y', labelcolor=LIGHTHOUSE_COLORS['pure_red'])
    ax2.set_ylabel('Debt-to-GDP Ratio (%)', fontsize=11, color=LIGHTHOUSE_COLORS['teal_green'])
    ax2.tick_params(axis='y', labelcolor=LIGHTHOUSE_COLORS['teal_green'])
    ax1.set_xlabel('Year', fontsize=10)

    # Combined legend
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='lower right', framealpha=0.95)

    # 4 spines
    for spine in ['top', 'right', 'left', 'bottom']:
        ax1.spines[spine].set_visible(True)
        ax1.spines[spine].set_linewidth(0.5)
        ax1.spines[spine].set_color('#666666')

    ax1.set_title('Federal Debt Trajectory: Crossing Critical Thresholds',
                  fontsize=14, fontweight='bold', pad=20)
    ax1.text(0.01, 1.02, 'LIGHTHOUSE MACRO', transform=ax1.transAxes, fontsize=8,
             color=LIGHTHOUSE_COLORS['ocean_blue'], fontweight='bold')
    ax1.text(0.99, -0.06, 'MACRO, ILLUMINATED.', transform=ax1.transAxes, fontsize=7,
             color=LIGHTHOUSE_COLORS['hot_magenta'], ha='right', style='italic')

    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax1.xaxis.set_major_locator(mdates.YearLocator(5))

    # Set xlim so both series start at left axis
    ax1.set_xlim(dates[0], dates[-1])

    return save_chart(fig, 'S2_20_Federal_Debt_Dual.png')


# =============================================================================
# CHART 6: Auto Delinquencies with Crisis Comparison
# =============================================================================

def chart_auto_delinquency_crisis():
    """Subprime Auto Delinquencies vs 2008 Crisis

    Note: FRED doesn't have subprime-specific auto delinquency.
    Using stylized data based on Fitch Ratings and NY Fed reports.
    Subprime 60+ day delinquency hit 6.65% in Oct 2025 (highest since 1990s).
    """
    print("Generating: Auto Delinquencies (Crisis Style)...")

    # Stylized subprime auto delinquency data based on Fitch/NY Fed reports
    # FRED series (DRALACBS) is all consumer loans, much lower
    quarters = pd.date_range('2003-Q1', '2025-Q4', freq='QE')

    # Stylized subprime auto 60+ day delinquency rates (%)
    # Based on historical reports: pre-crisis ~4%, 2008 peak ~6.2%, post-recovery ~3%,
    # 2022+ rising to 6.67%+ (exceeding 2008)
    # Need exactly 91 quarters (2003-Q1 to 2025-Q3)
    subprime_delinq = [
        # 2003 (4 quarters): Pre-crisis building
        3.8, 3.9, 4.0, 4.1,
        # 2004 (4 quarters)
        4.2, 4.3, 4.4, 4.5,
        # 2005 (4 quarters)
        4.6, 4.8, 5.0, 5.2,
        # 2006 (4 quarters)
        5.4, 5.6, 5.8, 5.9,
        # 2007 (4 quarters): Crisis begins
        6.0, 6.1, 6.2, 6.2,
        # 2008 (4 quarters): Peak crisis
        6.2, 6.1, 5.8, 5.4,
        # 2009 (4 quarters): Recovery starts
        5.0, 4.6, 4.3, 4.0,
        # 2010 (4 quarters)
        3.8, 3.6, 3.4, 3.2,
        # 2011 (4 quarters)
        3.0, 2.9, 2.8, 2.7,
        # 2012 (4 quarters)
        2.6, 2.5, 2.5, 2.5,
        # 2013 (4 quarters)
        2.5, 2.6, 2.7, 2.8,
        # 2014 (4 quarters)
        2.9, 3.0, 3.1, 3.2,
        # 2015 (4 quarters)
        3.3, 3.4, 3.5, 3.6,
        # 2016 (4 quarters)
        3.7, 3.8, 3.9, 4.0,
        # 2017 (4 quarters)
        4.1, 4.2, 4.3, 4.4,
        # 2018 (4 quarters)
        4.5, 4.6, 4.7, 4.8,
        # 2019 (4 quarters)
        4.9, 4.8, 4.7, 4.5,
        # 2020 (4 quarters): COVID dip
        3.5, 3.0, 2.8, 3.0,
        # 2021 (4 quarters): Rising
        3.2, 3.5, 3.8, 4.0,
        # 2022 (4 quarters)
        4.3, 4.6, 4.9, 5.2,
        # 2023 (4 quarters)
        5.5, 5.8, 6.0, 6.2,
        # 2024 (4 quarters)
        6.4, 6.5, 6.6, 6.65,
        # 2025 (3 quarters through Q3)
        6.67, 6.70, 6.75,
    ]

    # Trim to match - date_range gives 91 quarters
    n = len(quarters)
    if len(subprime_delinq) < n:
        # Pad with last value if needed
        subprime_delinq.extend([subprime_delinq[-1]] * (n - len(subprime_delinq)))
    subprime_delinq = subprime_delinq[:n]

    auto = pd.Series(subprime_delinq, index=quarters)

    fig, ax = create_figure(figsize=(16, 9))

    dates = auto.index
    values = auto.values

    print(f"    Subprime auto delinquency range: {values.min():.2f}% to {values.max():.2f}%")

    # Auto-calculate y limits
    y_max = max(10, values.max() * 1.15)

    # Zone shading - adjust to data
    ax.axhspan(0, 4, color=LIGHTHOUSE_COLORS['ocean_blue'], alpha=0.1, label='Normal (<4%)')
    ax.axhspan(4, 6, color=LIGHTHOUSE_COLORS['dusk_orange'], alpha=0.15, label='Elevated (4-6%)')
    ax.axhspan(6, y_max, color=LIGHTHOUSE_COLORS['pure_red'], alpha=0.15, label='Crisis (>6%)')

    # Main line
    ax.plot(dates, values, color=LIGHTHOUSE_COLORS['ocean_blue'], linewidth=2.5)

    # 2008 crisis peak reference
    ax.axhline(y=6.2, color=LIGHTHOUSE_COLORS['dusk_orange'], linestyle='--', linewidth=2)
    ax.text(dates[len(dates)//4], 6.35, '2008 CRISIS PEAK', fontsize=9,
            color=LIGHTHOUSE_COLORS['dusk_orange'], fontweight='bold')

    # Current value annotation
    current = values[-1]
    ax.annotate(f'Current: {current:.2f}%\n(Highest since early 1990s)',
                (dates[-1], current),
                textcoords='offset points', xytext=(-120, 20),
                fontsize=10, fontweight='bold',
                color=LIGHTHOUSE_COLORS['pure_red'],
                bbox=dict(boxstyle='round', facecolor='white', edgecolor=LIGHTHOUSE_COLORS['pure_red']),
                arrowprops=dict(arrowstyle='->', color=LIGHTHOUSE_COLORS['pure_red']))

    ax.set_ylabel('60+ Day Delinquency Rate (%)', fontsize=11)
    ax.set_xlabel('Date', fontsize=10)
    ax.set_ylim(0, y_max)
    ax.legend(loc='upper left', framealpha=0.95)

    # 4 spines
    for spine in ['top', 'right', 'left', 'bottom']:
        ax.spines[spine].set_visible(True)
        ax.spines[spine].set_linewidth(0.5)
        ax.spines[spine].set_color('#666666')

    ax.set_title('Subprime Auto Delinquencies: Exceeding 2008 Crisis Levels',
                 fontsize=14, fontweight='bold', pad=20)
    ax.text(0.99, 0.02, 'Source: Stylized estimates based on Fitch Ratings / NY Fed',
            transform=ax.transAxes, fontsize=7, color='gray', ha='right', style='italic')
    ax.text(0.01, 1.02, 'LIGHTHOUSE MACRO', transform=ax.transAxes, fontsize=8,
            color=LIGHTHOUSE_COLORS['ocean_blue'], fontweight='bold')
    ax.text(0.99, -0.06, 'MACRO, ILLUMINATED.', transform=ax.transAxes, fontsize=7,
            color=LIGHTHOUSE_COLORS['hot_magenta'], ha='right', style='italic')

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax.xaxis.set_major_locator(mdates.YearLocator(4))

    return save_chart(fig, 'S2_23_Auto_Delinquencies_Crisis.png')


# =============================================================================
# CHART 7: Excess Savings by Income Cohort (Stacked Area)
# =============================================================================

def chart_excess_savings_cohort():
    """Excess Savings by Income Cohort - Stacked area showing K-shape"""
    print("Generating: Excess Savings by Cohort...")

    # Use Fed DFA wealth distribution data
    dfa_data = data.get_wealth_distribution()

    # Create synthetic cohort data based on documented estimates from Fed research
    # These are stylized estimates based on Fed research papers on excess savings depletion
    quarters = pd.date_range('2020-Q1', '2025-Q4', freq='QE')

    # Billions - stylized based on Fed research on excess savings by income quintile
    # Each cohort shown independently (not stacked) to show divergence clearly
    top20 = [0, 200, 450, 650, 800, 900, 950, 900, 850, 800, 750, 700,
             650, 600, 580, 560, 540, 520, 500, 490, 480, 475, 470, 468]
    middle60 = [0, 150, 350, 500, 600, 650, 600, 500, 350, 200, 100, 0,
                -50, -80, -100, -120, -140, -155, -165, -175, -180, -182, -183, -185]
    bottom20 = [0, 80, 180, 280, 350, 380, 340, 280, 180, 80, 20, -30,
                -80, -120, -160, -200, -220, -235, -245, -250, -252, -253, -254, -255]

    # Trim to match quarters length
    n = len(quarters)
    top20 = top20[:n]
    middle60 = middle60[:n]
    bottom20 = bottom20[:n]

    fig, ax = create_figure(figsize=(16, 9))

    # Plot each cohort as separate lines with fills - NOT stacked
    # This shows the K-shape divergence more clearly

    # Top 20% - stays positive (blue)
    ax.fill_between(quarters, 0, top20, color=LIGHTHOUSE_COLORS['ocean_blue'], alpha=0.5, label='Top 20%')
    ax.plot(quarters, top20, color=LIGHTHOUSE_COLORS['ocean_blue'], linewidth=2.5)

    # Middle 60% - goes negative (green instead of orange)
    ax.fill_between(quarters, 0, middle60, color=LIGHTHOUSE_COLORS['teal_green'], alpha=0.5, label='Middle 60%')
    ax.plot(quarters, middle60, color=LIGHTHOUSE_COLORS['teal_green'], linewidth=2.5)

    # Bottom 20% - most negative (red)
    ax.fill_between(quarters, 0, bottom20, color=LIGHTHOUSE_COLORS['pure_red'], alpha=0.5, label='Bottom 20%')
    ax.plot(quarters, bottom20, color=LIGHTHOUSE_COLORS['pure_red'], linewidth=2.5)

    # Zero line
    ax.axhline(y=0, color='black', linewidth=2)

    # Add recession shading for COVID
    ax.axvspan(pd.Timestamp('2020-02-01'), pd.Timestamp('2020-04-01'),
               color='gray', alpha=0.15, zorder=0)

    # Annotations - peak stimulus
    peak_idx = 5
    peak_total = top20[peak_idx] + middle60[peak_idx] + bottom20[peak_idx]
    ax.annotate(f'Peak Stimulus\n${peak_total/1000:.1f}T Total', (quarters[peak_idx], top20[peak_idx] + 50),
                fontsize=10, ha='center',
                bbox=dict(boxstyle='round', facecolor='white', edgecolor='gray', alpha=0.9))

    # End values annotation
    ax.annotate(f'+${top20[-1]}B', (quarters[-1], top20[-1]),
                fontsize=10, ha='left', color=LIGHTHOUSE_COLORS['ocean_blue'], fontweight='bold',
                xytext=(10, 0), textcoords='offset points')
    ax.annotate(f'-${abs(middle60[-1])}B', (quarters[-1], middle60[-1]),
                fontsize=10, ha='left', color=LIGHTHOUSE_COLORS['teal_green'], fontweight='bold',
                xytext=(10, 0), textcoords='offset points')
    ax.annotate(f'-${abs(bottom20[-1])}B', (quarters[-1], bottom20[-1]),
                fontsize=10, ha='left', color=LIGHTHOUSE_COLORS['pure_red'], fontweight='bold',
                xytext=(10, 0), textcoords='offset points')

    # Callout box
    add_callout_box(ax,
                    f"Excess Savings Status (Q4 2025):\n"
                    f"• Top 20%: +${top20[-1]}B (STILL POSITIVE)\n"
                    f"• Middle 60%: -${abs(middle60[-1])}B (DEPLETED)\n"
                    f"• Bottom 20%: -${abs(bottom20[-1])}B (DEPLETED)\n"
                    f"→ K-Shape is now a Canyon",
                    (0.02, 0.95), fontsize=9)

    ax.set_ylabel('Excess Savings ($B)', fontsize=11)
    ax.set_xlabel('Quarter', fontsize=10)
    ax.legend(loc='upper right', framealpha=0.95)

    # 4 spines
    for spine in ['top', 'right', 'left', 'bottom']:
        ax.spines[spine].set_visible(True)
        ax.spines[spine].set_linewidth(0.5)
        ax.spines[spine].set_color('#666666')

    ax.set_title('THE K-SHAPED RECOVERY: Excess Savings by Income Cohort',
                 fontsize=14, fontweight='bold', pad=20)
    ax.text(0.99, 0.02, 'Source: Stylized estimates based on Fed research',
            transform=ax.transAxes, fontsize=7, color='gray', ha='right', style='italic')
    ax.text(0.01, 1.02, 'LIGHTHOUSE MACRO', transform=ax.transAxes, fontsize=8,
            color=LIGHTHOUSE_COLORS['ocean_blue'], fontweight='bold')
    ax.text(0.99, -0.06, 'MACRO, ILLUMINATED.', transform=ax.transAxes, fontsize=7,
            color=LIGHTHOUSE_COLORS['hot_magenta'], ha='right', style='italic')

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    return save_chart(fig, 'S1_06_Excess_Savings_Cohort.png')


# =============================================================================
# CHART 8: Two-Speed Consumer
# =============================================================================

def chart_two_speed_consumer():
    """Two-Speed Consumer - High-end vs mass market divergence"""
    print("Generating: Two-Speed Consumer...")

    consumer_data = data.get_consumer_data()
    savings_rate = consumer_data.get('savings_rate', pd.Series())
    credit = consumer_data.get('consumer_credit', pd.Series())

    if len(savings_rate) == 0:
        print("    ERROR: No consumer data")
        return None

    fig, ax1 = create_figure(figsize=(16, 9))
    ax2 = ax1.twinx()

    # Calculate credit YoY first, then filter both to 2016+
    if len(credit) > 12:
        credit_yoy = credit.pct_change(12) * 100
        credit_yoy = credit_yoy[credit_yoy.index >= '2016-01-01']
    else:
        credit_yoy = pd.Series()

    savings_rate = savings_rate[savings_rate.index >= '2016-01-01']

    # Savings rate
    ax2.plot(savings_rate.index, savings_rate.values, color=LIGHTHOUSE_COLORS['ocean_blue'],
             linewidth=2.5, label='Personal Savings Rate (%)')

    # Consumer credit growth
    if len(credit_yoy) > 0:
        ax1.fill_between(credit_yoy.index, 0, credit_yoy.values,
                         color=LIGHTHOUSE_COLORS['dusk_orange'], alpha=0.4, label='Consumer Credit YoY (%)')
        ax1.plot(credit_yoy.index, credit_yoy.values, color=LIGHTHOUSE_COLORS['dusk_orange'], linewidth=1.5)

    # Historical average savings rate
    ax2.axhline(y=8.5, color=LIGHTHOUSE_COLORS['teal_green'], linestyle='--', linewidth=1.5)
    ax2.text(savings_rate.index[10], 8.7, 'Historical Avg: 8.5%', fontsize=9,
             color=LIGHTHOUSE_COLORS['teal_green'])

    # Add recession shading
    add_recession_shading(ax1)

    # Current values
    current_savings = savings_rate.iloc[-1]
    add_last_value_label(ax2, current_savings, LIGHTHOUSE_COLORS['ocean_blue'],
                         label_format='{:.1f}%', side='right')

    # Callout
    add_callout_box(ax1,
                    f"Consumer Bifurcation:\n"
                    f"• Savings Rate: {current_savings:.1f}% vs 8.5% avg\n"
                    f"• Bottom 80%: Savings exhausted\n"
                    f"• Credit driving spending growth\n"
                    f"→ Resilience borrowed, not earned",
                    (0.02, 0.95), fontsize=9)

    ax1.set_ylabel('Consumer Credit YoY Growth (%)', fontsize=11, color=LIGHTHOUSE_COLORS['dusk_orange'])
    ax1.tick_params(axis='y', labelcolor=LIGHTHOUSE_COLORS['dusk_orange'])
    ax2.set_ylabel('Personal Savings Rate (%)', fontsize=11, color=LIGHTHOUSE_COLORS['ocean_blue'])
    ax2.tick_params(axis='y', labelcolor=LIGHTHOUSE_COLORS['ocean_blue'])
    ax1.set_xlabel('Date', fontsize=10)

    # Combined legend
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='lower left', framealpha=0.95)

    # 4 spines
    for spine in ['top', 'right', 'left', 'bottom']:
        ax1.spines[spine].set_visible(True)
        ax1.spines[spine].set_linewidth(0.5)
        ax1.spines[spine].set_color('#666666')

    # Set x-axis limits to start at 2016
    ax1.set_xlim(pd.Timestamp('2016-01-01'), savings_rate.index[-1])

    ax1.set_title('THE TWO-SPEED CONSUMER: Savings Depleted, Credit Expanding',
                  fontsize=14, fontweight='bold', pad=20)
    ax1.text(0.01, 1.02, 'LIGHTHOUSE MACRO', transform=ax1.transAxes, fontsize=8,
             color=LIGHTHOUSE_COLORS['ocean_blue'], fontweight='bold')
    ax1.text(0.99, -0.06, 'MACRO, ILLUMINATED.', transform=ax1.transAxes, fontsize=7,
             color=LIGHTHOUSE_COLORS['hot_magenta'], ha='right', style='italic')

    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    return save_chart(fig, 'S1_07_Two_Speed_Consumer.png')


# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main():
    print("=" * 60)
    print("LIGHTHOUSE MACRO - PREMIUM CHART GENERATION")
    print("Matching template style")
    print(f"Output: {OUTPUT_DIR}")
    print("=" * 60)
    print()

    charts = [
        chart_credit_spread_waterfall,
        chart_yield_curve_heatmap,
        chart_reserves_gdp_annotated,
        chart_sofr_effr_zones,
        chart_federal_debt_dual,
        chart_auto_delinquency_crisis,
        chart_excess_savings_cohort,
        chart_two_speed_consumer,
    ]

    success = 0
    for chart_func in charts:
        try:
            result = chart_func()
            if result:
                success += 1
        except Exception as e:
            print(f"    ERROR: {e}")

    print()
    print("=" * 60)
    print(f"GENERATION COMPLETE: {success}/{len(charts)} charts")
    print(f"Output: {OUTPUT_DIR}")
    print("=" * 60)


if __name__ == '__main__':
    main()
