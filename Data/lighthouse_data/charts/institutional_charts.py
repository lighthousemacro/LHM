"""
INSTITUTIONAL GRADE CHARTS
Lighthouse Macro - January 2026

Every chart here uses REAL DATA ONLY. No fallbacks to simulated data.
If data is unavailable, the chart fails loudly rather than silently fabricating.

Principles:
1. Raw data with visible noise - no undisclosed smoothing
2. If smoothed, MUST be labeled (e.g., "3-mo MA")
3. Event markers where data should show them
4. Source attribution with series IDs
5. Honest annotations - no manufactured talking points

Charts that required rebuilding:
- Consumer Bifurcation (Savings Rate)
- Foreign Treasury Holdings (TIC data)
- Subprime Auto Delinquencies
- Wealth Distribution
- Excess Savings
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
import requests
from datetime import datetime
from pathlib import Path

# FRED API
FRED_API_KEY = os.environ.get('FRED_API_KEY')

# Lighthouse colors
COLORS = {
    'ocean_blue': '#2389BB',
    'dusk_orange': '#FF6723',
    'electric_cyan': '#03DDFF',
    'hot_magenta': '#FF00F0',
    'sea_teal': '#289389',
    'silvs_gray': '#D1D1D1',
    'up_green': '#008000',
    'down_red': '#FF3333',
    'neutral': '#666666',
}

OUTPUT_DIR = Path('/Users/bob/LHM/data/charts/institutional')


def fetch_fred_raw(series_id: str, start_date: str = '2000-01-01') -> pd.Series:
    """
    Fetch raw FRED data - NO smoothing, NO interpolation.
    FAILS LOUDLY if data unavailable - never returns fake data.
    """
    if not FRED_API_KEY:
        raise ValueError("FRED_API_KEY environment variable required")

    url = 'https://api.stlouisfed.org/fred/series/observations'
    params = {
        'series_id': series_id,
        'api_key': FRED_API_KEY,
        'file_type': 'json',
        'observation_start': start_date,
    }

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()

    if 'observations' not in data or len(data['observations']) == 0:
        raise ValueError(f"No data returned for {series_id}")

    df = pd.DataFrame(data['observations'])
    df = df[df['value'] != '.']
    df['date'] = pd.to_datetime(df['date'])
    df['value'] = pd.to_numeric(df['value'])

    series = df.set_index('date')['value']
    series.name = series_id

    return series


def add_branding(fig, ax, source_text):
    """Standard LHM branding."""
    fig.text(0.01, 0.99, 'LIGHTHOUSE MACRO', fontsize=10, fontweight='bold',
             color=COLORS['ocean_blue'], ha='left', va='top')
    fig.text(0.99, 0.01, 'MACRO, ILLUMINATED.', fontsize=8, style='italic',
             color=COLORS['ocean_blue'], ha='right', va='bottom', alpha=0.7)
    fig.text(0.01, 0.01, source_text,
             fontsize=7, color=COLORS['neutral'], ha='left', va='bottom', style='italic')

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(False)


def add_recession_shading(ax, start_year='2000'):
    """Add NBER recession shading."""
    recessions = [
        ('2001-03-01', '2001-11-01'),
        ('2007-12-01', '2009-06-01'),
        ('2020-02-01', '2020-04-01'),
    ]
    for start, end in recessions:
        if pd.Timestamp(start).year >= int(start_year[:4]):
            ax.axvspan(pd.Timestamp(start), pd.Timestamp(end),
                       alpha=0.1, color='gray', zorder=0)


# =============================================================================
# CHART 1: Foreign Treasury Holdings (TIC Data)
# =============================================================================

def generate_foreign_holdings_chart():
    """
    Foreign Official Treasury Holdings - REAL TIC DATA

    FRED Series:
    - FDHBFIN: Foreign Holdings of Treasury Securities (Total)
    - There's no Japan/China breakdown in FRED - we use total foreign holdings

    If you need country breakdown, that requires Treasury TIC website scraping
    or Bloomberg terminal data.
    """
    print("\nGenerating Foreign Holdings chart (REAL DATA)...")

    # Fetch real data
    foreign_holdings = fetch_fred_raw('FDHBFIN', '2000-01-01')  # $M
    foreign_holdings = foreign_holdings / 1000  # Convert to $B

    # Also get Fed holdings for context
    try:
        fed_holdings = fetch_fred_raw('TREAST', '2000-01-01')  # Fed Treasury holdings, $M
        fed_holdings = fed_holdings / 1000  # $B
    except:
        fed_holdings = None

    fig, ax = plt.subplots(figsize=(12, 8))

    # Plot foreign holdings
    ax.plot(foreign_holdings.index, foreign_holdings.values,
            linewidth=1.5, color=COLORS['ocean_blue'],
            label='Foreign Holdings (Total)')

    # Add markers for each data point to show it's real monthly data
    ax.scatter(foreign_holdings.index[::12], foreign_holdings.values[::12],
               s=20, color=COLORS['ocean_blue'], zorder=5, alpha=0.7)

    if fed_holdings is not None:
        ax.plot(fed_holdings.index, fed_holdings.values,
                linewidth=1.5, color=COLORS['dusk_orange'],
                label='Fed Holdings')

    # Current value annotation
    current_val = foreign_holdings.iloc[-1]
    current_date = foreign_holdings.index[-1]
    peak_val = foreign_holdings.max()
    peak_date = foreign_holdings.idxmax()

    ax.annotate(
        f'Current: ${current_val:,.0f}B\n({current_date.strftime("%b %Y")})\n'
        f'Peak: ${peak_val:,.0f}B ({peak_date.strftime("%b %Y")})',
        xy=(current_date, current_val),
        xytext=(-120, 30), textcoords='offset points',
        fontsize=9, fontweight='bold',
        color='white',
        bbox=dict(boxstyle='round,pad=0.4', facecolor=COLORS['ocean_blue'],
                  edgecolor='none', alpha=0.9),
        arrowprops=dict(arrowstyle='->', color=COLORS['ocean_blue'], lw=1.5))

    add_recession_shading(ax)

    ax.set_title('Foreign Holdings of U.S. Treasuries', fontsize=14, fontweight='bold', pad=20)
    ax.set_ylabel('Holdings ($B)', fontweight='bold')
    ax.legend(loc='upper left', frameon=True, facecolor='white')

    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    add_branding(fig, ax, 'Source: FRED (FDHBFIN, TREAST) | Raw monthly data')

    plt.tight_layout()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / 'chart_foreign_holdings.png'
    fig.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close(fig)

    print(f"  Saved: {output_path}")
    return output_path


# =============================================================================
# CHART 2: Auto Loan Delinquencies (Real FRED Data)
# =============================================================================

def generate_auto_delinquency_chart():
    """
    Auto Loan Delinquencies - REAL FRED DATA

    FRED Series:
    - DRALACBS: Delinquency Rate on Consumer Loans, All Commercial Banks
    - Note: Subprime-specific data requires NY Fed Consumer Credit Panel (not in FRED)

    This shows ALL auto delinquencies, not just subprime.
    If chart says "subprime" but uses this data, that's misleading.
    """
    print("\nGenerating Auto Delinquency chart (REAL DATA)...")

    # Try auto-specific first, fall back to consumer loans
    try:
        # This is the closest FRED has to auto delinquency
        delinq = fetch_fred_raw('DRALACBS', '2000-01-01')
        series_name = 'Consumer Loan Delinquency (All Banks)'
        series_id = 'DRALACBS'
    except:
        # Broader consumer loan delinquency
        delinq = fetch_fred_raw('DRCLACBS', '2000-01-01')
        series_name = 'Consumer Loan Delinquency Rate'
        series_id = 'DRCLACBS'

    fig, ax = plt.subplots(figsize=(12, 8))

    # Plot raw quarterly data with markers
    ax.plot(delinq.index, delinq.values,
            linewidth=1.5, color=COLORS['ocean_blue'],
            marker='o', markersize=3, alpha=0.8)

    # Historical context lines
    pre_gfc_avg = delinq[delinq.index < '2007-01-01'].mean()
    gfc_peak = delinq['2008-01-01':'2010-12-31'].max()

    ax.axhline(pre_gfc_avg, color=COLORS['silvs_gray'], linestyle='--',
               linewidth=1, alpha=0.7)
    ax.text(delinq.index.min(), pre_gfc_avg + 0.1,
            f'Pre-GFC avg: {pre_gfc_avg:.2f}%', fontsize=8, color=COLORS['neutral'])

    ax.axhline(gfc_peak, color=COLORS['down_red'], linestyle='--',
               linewidth=1, alpha=0.5)
    ax.text(delinq.index.min(), gfc_peak + 0.1,
            f'GFC peak: {gfc_peak:.2f}%', fontsize=8, color=COLORS['down_red'])

    # Current value
    current_val = delinq.iloc[-1]
    current_date = delinq.index[-1]

    ax.annotate(
        f'Current: {current_val:.2f}%\n({current_date.strftime("%b %Y")})',
        xy=(current_date, current_val),
        xytext=(-80, 30), textcoords='offset points',
        fontsize=10, fontweight='bold',
        color='white',
        bbox=dict(boxstyle='round,pad=0.4', facecolor=COLORS['ocean_blue'],
                  edgecolor='none', alpha=0.9),
        arrowprops=dict(arrowstyle='->', color=COLORS['ocean_blue'], lw=1.5))

    add_recession_shading(ax)

    ax.set_title(f'{series_name}', fontsize=14, fontweight='bold', pad=20)
    ax.set_ylabel('Delinquency Rate (%)', fontweight='bold')

    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    add_branding(fig, ax, f'Source: FRED ({series_id}) | Raw quarterly data')

    plt.tight_layout()

    output_path = OUTPUT_DIR / 'chart_auto_delinquency.png'
    fig.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close(fig)

    print(f"  Saved: {output_path}")
    return output_path


# =============================================================================
# CHART 3: Credit Card Delinquency (Real FRED Data)
# =============================================================================

def generate_cc_delinquency_chart():
    """
    Credit Card Delinquency - REAL FRED DATA

    FRED Series:
    - DRCCLACBS: Delinquency Rate on Credit Card Loans
    """
    print("\nGenerating Credit Card Delinquency chart (REAL DATA)...")

    cc_delinq = fetch_fred_raw('DRCCLACBS', '2000-01-01')

    fig, ax = plt.subplots(figsize=(12, 8))

    # Raw quarterly data with markers
    ax.plot(cc_delinq.index, cc_delinq.values,
            linewidth=1.5, color=COLORS['dusk_orange'],
            marker='o', markersize=3, alpha=0.8)

    # Historical context
    pre_gfc_avg = cc_delinq[cc_delinq.index < '2007-01-01'].mean()
    gfc_peak = cc_delinq['2008-01-01':'2011-12-31'].max()
    covid_low = cc_delinq['2020-01-01':'2021-12-31'].min()

    ax.axhline(pre_gfc_avg, color=COLORS['silvs_gray'], linestyle='--', linewidth=1)
    ax.text(cc_delinq.index[5], pre_gfc_avg - 0.2,
            f'Pre-GFC avg: {pre_gfc_avg:.2f}%', fontsize=8, color=COLORS['neutral'])

    # Current value
    current_val = cc_delinq.iloc[-1]
    current_date = cc_delinq.index[-1]

    ax.annotate(
        f'Current: {current_val:.2f}%\n({current_date.strftime("%b %Y")})\n'
        f'GFC Peak: {gfc_peak:.2f}%\n'
        f'COVID Low: {covid_low:.2f}%',
        xy=(current_date, current_val),
        xytext=(-120, -60), textcoords='offset points',
        fontsize=9, fontweight='bold',
        color='white',
        bbox=dict(boxstyle='round,pad=0.4', facecolor=COLORS['dusk_orange'],
                  edgecolor='none', alpha=0.9),
        arrowprops=dict(arrowstyle='->', color=COLORS['dusk_orange'], lw=1.5))

    add_recession_shading(ax)

    ax.set_title('Credit Card Delinquency Rate', fontsize=14, fontweight='bold', pad=20)
    ax.set_ylabel('Delinquency Rate (%)', fontweight='bold')

    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    add_branding(fig, ax, 'Source: FRED (DRCCLACBS) | Raw quarterly data')

    plt.tight_layout()

    output_path = OUTPUT_DIR / 'chart_cc_delinquency.png'
    fig.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close(fig)

    print(f"  Saved: {output_path}")
    return output_path


# =============================================================================
# CHART 4: Wealth Distribution (Real Fed DFA Data)
# =============================================================================

def generate_wealth_distribution_chart():
    """
    Wealth Distribution by Percentile - REAL FED DFA DATA

    FRED Series (Distributional Financial Accounts):
    - WFRBST01134: Share of Total Net Worth Held by the Top 1%
    - WFRBSB50215: Share of Total Net Worth Held by the Bottom 50%
    - WFRBSN40080: Share of Total Net Worth Held by the 50th to 90th Percentiles
    """
    print("\nGenerating Wealth Distribution chart (REAL DATA)...")

    top1 = fetch_fred_raw('WFRBST01134', '1990-01-01')
    bottom50 = fetch_fred_raw('WFRBSB50215', '1990-01-01')
    middle = fetch_fred_raw('WFRBSN40080', '1990-01-01')

    fig, ax = plt.subplots(figsize=(12, 8))

    # Plot each series
    ax.plot(top1.index, top1.values, linewidth=2, color=COLORS['hot_magenta'],
            marker='o', markersize=3, label='Top 1%')
    ax.plot(middle.index, middle.values, linewidth=2, color=COLORS['ocean_blue'],
            marker='s', markersize=3, label='50th-90th Percentile')
    ax.plot(bottom50.index, bottom50.values, linewidth=2, color=COLORS['down_red'],
            marker='^', markersize=3, label='Bottom 50%')

    # Current values
    ax.annotate(f'Top 1%: {top1.iloc[-1]:.1f}%',
                xy=(top1.index[-1], top1.iloc[-1]),
                xytext=(10, 0), textcoords='offset points',
                fontsize=9, fontweight='bold', color=COLORS['hot_magenta'])

    ax.annotate(f'Bottom 50%: {bottom50.iloc[-1]:.1f}%',
                xy=(bottom50.index[-1], bottom50.iloc[-1]),
                xytext=(10, 0), textcoords='offset points',
                fontsize=9, fontweight='bold', color=COLORS['down_red'])

    add_recession_shading(ax, '1990')

    ax.set_title('U.S. Wealth Distribution by Percentile', fontsize=14, fontweight='bold', pad=20)
    ax.set_ylabel('Share of Total Net Worth (%)', fontweight='bold')
    ax.legend(loc='center left', frameon=True, facecolor='white')

    ax.xaxis.set_major_locator(mdates.YearLocator(5))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    add_branding(fig, ax, 'Source: FRED/Fed DFA (WFRBST01134, WFRBSB50215, WFRBSN40080) | Quarterly')

    plt.tight_layout()

    output_path = OUTPUT_DIR / 'chart_wealth_distribution.png'
    fig.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close(fig)

    print(f"  Saved: {output_path}")
    return output_path


# =============================================================================
# CHART 5: Excess Savings (Calculated from Real Data)
# =============================================================================

def generate_excess_savings_chart():
    """
    Excess Savings - CALCULATED FROM REAL FRED DATA

    Method: Compare actual savings to pre-COVID trend
    - PSAVE: Personal Savings ($B, SAAR)
    - Calculate cumulative deviation from Jan 2020 trend

    This is a DERIVED metric but from REAL inputs.
    """
    print("\nGenerating Excess Savings chart (REAL DATA)...")

    # Personal savings (billions, seasonally adjusted annual rate)
    savings = fetch_fred_raw('PSAVE', '2015-01-01')

    # Calculate pre-COVID trend (2015-2019)
    pre_covid = savings[savings.index < '2020-01-01']
    trend_growth = (pre_covid.iloc[-1] / pre_covid.iloc[0]) ** (1 / len(pre_covid)) - 1

    # Project trend forward
    trend_start = pre_covid.iloc[-1]
    trend_dates = savings[savings.index >= '2020-01-01'].index
    trend_values = [trend_start * (1 + trend_growth) ** i for i in range(len(trend_dates))]
    trend = pd.Series(trend_values, index=trend_dates)

    # Excess = cumulative difference (convert SAAR to monthly, then cumsum)
    post_covid = savings[savings.index >= '2020-01-01']
    monthly_actual = post_covid / 12  # Convert SAAR to monthly
    monthly_trend = trend / 12
    excess_flow = monthly_actual - monthly_trend
    excess_stock = excess_flow.cumsum()

    fig, ax = plt.subplots(figsize=(12, 8))

    # Plot excess savings stock
    ax.fill_between(excess_stock.index, 0, excess_stock.values,
                    where=excess_stock.values > 0, alpha=0.4, color=COLORS['up_green'],
                    label='Excess Savings')
    ax.fill_between(excess_stock.index, 0, excess_stock.values,
                    where=excess_stock.values <= 0, alpha=0.4, color=COLORS['down_red'],
                    label='Below Trend')

    ax.plot(excess_stock.index, excess_stock.values,
            linewidth=2, color=COLORS['ocean_blue'])

    ax.axhline(0, color='black', linewidth=0.5)

    # Peak and current
    peak_val = excess_stock.max()
    peak_date = excess_stock.idxmax()
    current_val = excess_stock.iloc[-1]
    current_date = excess_stock.index[-1]

    ax.annotate(f'Peak: ${peak_val/1000:.1f}T\n({peak_date.strftime("%b %Y")})',
                xy=(peak_date, peak_val),
                xytext=(30, -30), textcoords='offset points',
                fontsize=9, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.9))

    ax.annotate(f'Current: ${current_val/1000:.2f}T\n({current_date.strftime("%b %Y")})',
                xy=(current_date, current_val),
                xytext=(-100, 30), textcoords='offset points',
                fontsize=10, fontweight='bold',
                color='white',
                bbox=dict(boxstyle='round,pad=0.4', facecolor=COLORS['ocean_blue'],
                          edgecolor='none', alpha=0.9),
                arrowprops=dict(arrowstyle='->', color=COLORS['ocean_blue'], lw=1.5))

    ax.set_title('Cumulative Excess Savings vs Pre-COVID Trend',
                 fontsize=14, fontweight='bold', pad=20)
    ax.set_ylabel('Cumulative Excess ($B)', fontweight='bold')
    ax.legend(loc='upper right', frameon=True)

    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    add_branding(fig, ax,
                 'Source: FRED (PSAVE) | Excess = cumulative deviation from 2015-2019 trend')

    plt.tight_layout()

    output_path = OUTPUT_DIR / 'chart_excess_savings.png'
    fig.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close(fig)

    print(f"  Saved: {output_path}")
    return output_path


# =============================================================================
# CHART 6: CRE Delinquencies (Real FRED Data)
# =============================================================================

def generate_cre_delinquency_chart():
    """
    Commercial Real Estate Delinquencies - REAL FRED DATA

    FRED Series:
    - DRSFRMACBS: Delinquency Rate on All Loans, All Commercial Banks (proxy)
    - For CRE-specific, need CMBS data from Trepp/Bloomberg
    """
    print("\nGenerating CRE Delinquency chart (REAL DATA)...")

    # Commercial real estate loans delinquency
    try:
        cre_delinq = fetch_fred_raw('DRCRELACBS', '2000-01-01')
        series_name = 'CRE Loan Delinquency'
        series_id = 'DRCRELACBS'
    except:
        # Fallback to broader commercial loans
        cre_delinq = fetch_fred_raw('DRBLACBS', '2000-01-01')
        series_name = 'Business Loan Delinquency'
        series_id = 'DRBLACBS'

    fig, ax = plt.subplots(figsize=(12, 8))

    ax.plot(cre_delinq.index, cre_delinq.values,
            linewidth=1.5, color=COLORS['dusk_orange'],
            marker='o', markersize=3, alpha=0.8)

    # GFC context
    gfc_peak = cre_delinq['2008-01-01':'2012-12-31'].max()
    ax.axhline(gfc_peak, color=COLORS['down_red'], linestyle='--',
               linewidth=1, alpha=0.5)
    ax.text(cre_delinq.index[5], gfc_peak + 0.2,
            f'GFC peak: {gfc_peak:.2f}%', fontsize=8, color=COLORS['down_red'])

    current_val = cre_delinq.iloc[-1]
    current_date = cre_delinq.index[-1]

    ax.annotate(
        f'Current: {current_val:.2f}%\n({current_date.strftime("%b %Y")})',
        xy=(current_date, current_val),
        xytext=(-80, 30), textcoords='offset points',
        fontsize=10, fontweight='bold',
        color='white',
        bbox=dict(boxstyle='round,pad=0.4', facecolor=COLORS['dusk_orange'],
                  edgecolor='none', alpha=0.9),
        arrowprops=dict(arrowstyle='->', color=COLORS['dusk_orange'], lw=1.5))

    add_recession_shading(ax)

    ax.set_title(f'{series_name} Rate', fontsize=14, fontweight='bold', pad=20)
    ax.set_ylabel('Delinquency Rate (%)', fontweight='bold')

    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    add_branding(fig, ax, f'Source: FRED ({series_id}) | Raw quarterly data')

    plt.tight_layout()

    output_path = OUTPUT_DIR / 'chart_cre_delinquency.png'
    fig.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close(fig)

    print(f"  Saved: {output_path}")
    return output_path


# =============================================================================
# MASTER GENERATION FUNCTION
# =============================================================================

def generate_all_institutional_charts():
    """Generate all institutionally credible charts."""
    print("=" * 60)
    print("GENERATING INSTITUTIONAL GRADE CHARTS")
    print("All data is REAL - no fabrication, no undisclosed smoothing")
    print("=" * 60)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    results = {}

    charts = [
        ('Foreign Holdings', generate_foreign_holdings_chart),
        ('Auto Delinquency', generate_auto_delinquency_chart),
        ('CC Delinquency', generate_cc_delinquency_chart),
        ('Wealth Distribution', generate_wealth_distribution_chart),
        ('Excess Savings', generate_excess_savings_chart),
        ('CRE Delinquency', generate_cre_delinquency_chart),
    ]

    for name, func in charts:
        try:
            path = func()
            results[name] = 'SUCCESS'
        except Exception as e:
            print(f"  ERROR generating {name}: {e}")
            results[name] = f'FAILED: {e}'

    print("\n" + "=" * 60)
    print("GENERATION COMPLETE")
    print("=" * 60)
    for name, status in results.items():
        print(f"  {name}: {status}")

    return results


if __name__ == "__main__":
    generate_all_institutional_charts()
