"""
Two Speed Consumer - INSTITUTIONAL GRADE
Lighthouse Macro - January 2026

Shows the bifurcation between:
- Top consumers (wealth effect, asset-driven, low debt stress)
- Bottom consumers (wage-dependent, high debt stress, delinquency rising)

ALL ANNOTATIONS MUST MATCH THE DATA VALUES EXACTLY.

FRED Series:
- DRCCLACBS: Credit Card Delinquency Rate (bottom consumer proxy)
- DRSFRMACBS: Single-Family Mortgage Delinquency (housing stress)
- PSAVERT: Personal Savings Rate (overall health)
- WFRBST01134: Top 1% Share of Net Worth (wealth concentration)
- WFRBSB50215: Bottom 50% Share of Net Worth (bottom consumer weakness)
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import requests
from datetime import datetime
from pathlib import Path

FRED_API_KEY = os.environ.get('FRED_API_KEY')

COLORS = {
    'ocean_blue': '#2389BB',
    'dusk_orange': '#FF6723',
    'hot_magenta': '#FF00F0',
    'sea_teal': '#289389',
    'silvs_gray': '#D1D1D1',
    'up_green': '#008000',
    'down_red': '#FF3333',
    'neutral': '#666666',
}


def fetch_fred_raw(series_id: str, start_date: str = '2000-01-01') -> pd.Series:
    """Fetch raw FRED data."""
    if not FRED_API_KEY:
        raise ValueError("FRED_API_KEY required")

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
        raise ValueError(f"No data for {series_id}")

    df = pd.DataFrame(data['observations'])
    df = df[df['value'] != '.']
    df['date'] = pd.to_datetime(df['date'])
    df['value'] = pd.to_numeric(df['value'])

    return df.set_index('date')['value']


def generate_two_speed_consumer_chart(output_path: Path = None):
    """
    Two Speed Consumer - Real Data, Matching Annotations

    Shows the divergence between top and bottom consumers through:
    - Credit card delinquency (bottom consumer stress)
    - Savings rate (overall consumer health)
    - Wealth share divergence (structural inequality)
    """
    print("\nGenerating Two Speed Consumer chart (REAL DATA)...")

    # Fetch data
    cc_delinq = fetch_fred_raw('DRCCLACBS', '2015-01-01')  # Quarterly
    savings_rate = fetch_fred_raw('PSAVERT', '2015-01-01')  # Monthly

    # Try wealth data (may fail if series changed)
    try:
        top1_share = fetch_fred_raw('WFRBST01134', '2015-01-01')  # Quarterly
        bottom50_share = fetch_fred_raw('WFRBSB50215', '2015-01-01')  # Quarterly
        has_wealth_data = True
    except:
        has_wealth_data = False
        print("  Wealth distribution data unavailable")

    # Create figure with 2 subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), sharex=True)

    # === TOP PANEL: Savings Rate vs Delinquency ===
    # Left axis: Savings Rate
    ax1.plot(savings_rate.index, savings_rate.values,
             linewidth=1.5, color=COLORS['ocean_blue'],
             marker='.', markersize=2, alpha=0.7,
             label='Personal Savings Rate (%)')

    ax1.set_ylabel('Savings Rate (%)', color=COLORS['ocean_blue'], fontweight='bold')
    ax1.tick_params(axis='y', labelcolor=COLORS['ocean_blue'])

    # Right axis: CC Delinquency
    ax1_right = ax1.twinx()
    ax1_right.plot(cc_delinq.index, cc_delinq.values,
                   linewidth=2, color=COLORS['down_red'],
                   marker='o', markersize=4,
                   label='Credit Card Delinquency (%)')

    ax1_right.set_ylabel('CC Delinquency (%)', color=COLORS['down_red'], fontweight='bold')
    ax1_right.tick_params(axis='y', labelcolor=COLORS['down_red'])

    # Get EXACT current values
    savings_current = savings_rate.iloc[-1]
    savings_date = savings_rate.index[-1]
    cc_current = cc_delinq.iloc[-1]
    cc_date = cc_delinq.index[-1]

    # Pre-COVID averages
    savings_pre_covid = savings_rate[savings_rate.index < '2020-01-01'].mean()
    cc_pre_covid = cc_delinq[cc_delinq.index < '2020-01-01'].mean()

    # Annotations with EXACT values
    ax1.annotate(
        f'Savings: {savings_current:.1f}%\n({savings_date.strftime("%b %Y")})\n'
        f'Pre-COVID avg: {savings_pre_covid:.1f}%',
        xy=(savings_date, savings_current),
        xytext=(-100, 30), textcoords='offset points',
        fontsize=9, fontweight='bold', color='white',
        bbox=dict(boxstyle='round,pad=0.4', facecolor=COLORS['ocean_blue'],
                  edgecolor='none', alpha=0.9),
        arrowprops=dict(arrowstyle='->', color=COLORS['ocean_blue'], lw=1.5))

    ax1_right.annotate(
        f'CC Delinq: {cc_current:.2f}%\n({cc_date.strftime("%b %Y")})\n'
        f'Pre-COVID avg: {cc_pre_covid:.2f}%',
        xy=(cc_date, cc_current),
        xytext=(20, -40), textcoords='offset points',
        fontsize=9, fontweight='bold', color='white',
        bbox=dict(boxstyle='round,pad=0.4', facecolor=COLORS['down_red'],
                  edgecolor='none', alpha=0.9),
        arrowprops=dict(arrowstyle='->', color=COLORS['down_red'], lw=1.5))

    ax1.set_title('The Two-Speed Consumer: Savings Collapse + Delinquency Rise',
                  fontsize=12, fontweight='bold')

    # Add legend
    from matplotlib.lines import Line2D
    lines1 = [Line2D([0], [0], color=COLORS['ocean_blue'], linewidth=2),
              Line2D([0], [0], color=COLORS['down_red'], linewidth=2)]
    ax1.legend(lines1, ['Savings Rate', 'CC Delinquency'], loc='upper left')

    # === BOTTOM PANEL: Wealth Distribution (if available) ===
    if has_wealth_data:
        ax2.plot(top1_share.index, top1_share.values,
                 linewidth=2, color=COLORS['hot_magenta'],
                 marker='o', markersize=4,
                 label='Top 1% Share of Net Worth')

        ax2.plot(bottom50_share.index, bottom50_share.values,
                 linewidth=2, color=COLORS['sea_teal'],
                 marker='s', markersize=4,
                 label='Bottom 50% Share of Net Worth')

        # Current values - EXACT
        top1_current = top1_share.iloc[-1]
        top1_date = top1_share.index[-1]
        bottom50_current = bottom50_share.iloc[-1]
        bottom50_date = bottom50_share.index[-1]

        ax2.annotate(
            f'Top 1%: {top1_current:.1f}%\n({top1_date.strftime("%b %Y")})',
            xy=(top1_date, top1_current),
            xytext=(-80, 10), textcoords='offset points',
            fontsize=9, fontweight='bold', color=COLORS['hot_magenta'],
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.9))

        ax2.annotate(
            f'Bottom 50%: {bottom50_current:.1f}%\n({bottom50_date.strftime("%b %Y")})',
            xy=(bottom50_date, bottom50_current),
            xytext=(-80, -20), textcoords='offset points',
            fontsize=9, fontweight='bold', color=COLORS['sea_teal'],
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.9))

        ax2.set_ylabel('Share of Net Worth (%)', fontweight='bold')
        ax2.set_title('Wealth Distribution: The Structural Divide',
                      fontsize=12, fontweight='bold')
        ax2.legend(loc='center left')
    else:
        # Alternative: Show additional delinquency metrics
        try:
            auto_delinq = fetch_fred_raw('DRALACBS', '2015-01-01')
            mortgage_delinq = fetch_fred_raw('DRSFRMACBS', '2015-01-01')

            ax2.plot(auto_delinq.index, auto_delinq.values,
                     linewidth=2, color=COLORS['dusk_orange'],
                     marker='o', markersize=4,
                     label='Consumer Loan Delinquency')

            ax2.plot(mortgage_delinq.index, mortgage_delinq.values,
                     linewidth=2, color=COLORS['sea_teal'],
                     marker='s', markersize=4,
                     label='Mortgage Delinquency')

            auto_current = auto_delinq.iloc[-1]
            mortgage_current = mortgage_delinq.iloc[-1]

            ax2.annotate(f'Consumer: {auto_current:.2f}%',
                        xy=(auto_delinq.index[-1], auto_current),
                        xytext=(10, 10), textcoords='offset points',
                        fontsize=9, fontweight='bold', color=COLORS['dusk_orange'])

            ax2.annotate(f'Mortgage: {mortgage_current:.2f}%',
                        xy=(mortgage_delinq.index[-1], mortgage_current),
                        xytext=(10, -15), textcoords='offset points',
                        fontsize=9, fontweight='bold', color=COLORS['sea_teal'])

            ax2.set_ylabel('Delinquency Rate (%)', fontweight='bold')
            ax2.set_title('Other Consumer Stress Metrics',
                          fontsize=12, fontweight='bold')
            ax2.legend(loc='upper left')
        except:
            ax2.text(0.5, 0.5, 'Additional data unavailable',
                    transform=ax2.transAxes, ha='center', va='center')

    # Common formatting
    for ax in [ax1, ax2]:
        ax.spines['top'].set_visible(False)
        ax.grid(False)

        # Recession shading
        recessions = [('2020-02-01', '2020-04-01')]
        for start, end in recessions:
            ax.axvspan(pd.Timestamp(start), pd.Timestamp(end),
                       alpha=0.1, color='gray', zorder=0)

    ax2.xaxis.set_major_locator(mdates.YearLocator())
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    # Branding
    fig.text(0.01, 0.99, 'LIGHTHOUSE MACRO', fontsize=10, fontweight='bold',
             color=COLORS['ocean_blue'], ha='left', va='top')
    fig.text(0.99, 0.01, 'MACRO, ILLUMINATED.', fontsize=8, style='italic',
             color=COLORS['ocean_blue'], ha='right', va='bottom', alpha=0.7)
    fig.text(0.01, 0.01,
             'Source: FRED (PSAVERT, DRCCLACBS, WFRBST01134, WFRBSB50215) | Raw data, no smoothing',
             fontsize=7, color=COLORS['neutral'], ha='left', va='bottom', style='italic')

    plt.tight_layout()

    if output_path is None:
        output_path = Path('/Users/bob/LHM/data/charts/institutional/chart_two_speed_consumer.png')

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close(fig)

    print(f"  Saved: {output_path}")
    print(f"  Savings Rate: {savings_current:.1f}% (as of {savings_date.strftime('%b %Y')})")
    print(f"  CC Delinquency: {cc_current:.2f}% (as of {cc_date.strftime('%b %Y')})")

    return output_path


if __name__ == "__main__":
    generate_two_speed_consumer_chart()
