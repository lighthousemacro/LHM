"""
Consumer Bifurcation Chart - INSTITUTIONAL GRADE
Lighthouse Macro - January 2026

Rebuilt to pass institutional sniff test:
- Raw monthly FRED data, NO smoothing unless explicitly labeled
- Visible noise/jaggedness that says "this is real data"
- Proper event markers for stimulus, tax seasons, fiscal cliffs
- Honest annotations - no manufactured talking points
- Clean axis treatment, no ambiguous overlays

FRED Series:
- PSAVERT: Personal Savings Rate (monthly, %)
- DRCCLACBS: Credit Card Delinquency Rate (quarterly, %)
- TOTALSL: Total Consumer Credit Outstanding (monthly, $B)
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


def fetch_fred_raw(series_id: str, start_date: str = '2015-01-01') -> pd.Series:
    """
    Fetch raw FRED data - NO smoothing, NO interpolation.
    Returns the actual reported values with their actual noise.
    """
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

    if 'observations' not in data:
        raise ValueError(f"No data for {series_id}")

    df = pd.DataFrame(data['observations'])
    df = df[df['value'] != '.']  # Remove missing values marker
    df['date'] = pd.to_datetime(df['date'])
    df['value'] = pd.to_numeric(df['value'])

    series = df.set_index('date')['value']
    series.name = series_id

    return series


def generate_consumer_bifurcation_chart(output_path: Path = None):
    """
    Generate institutionally credible Consumer Bifurcation chart.

    Key principles:
    1. Raw data with visible noise
    2. Event markers for major fiscal/policy events
    3. Honest labeling of any transformations
    4. No manufactured smoothness
    """

    print("Fetching raw FRED data...")

    # Fetch raw monthly data
    savings_rate = fetch_fred_raw('PSAVERT', '2015-01-01')
    cc_delinq = fetch_fred_raw('DRCCLACBS', '2015-01-01')  # Quarterly
    consumer_credit = fetch_fred_raw('TOTALSL', '2015-01-01')  # Monthly, in $B

    # Convert consumer credit to trillions
    consumer_credit = consumer_credit / 1000

    print(f"  Savings Rate: {len(savings_rate)} obs, last={savings_rate.iloc[-1]:.1f}% on {savings_rate.index[-1].strftime('%Y-%m-%d')}")
    print(f"  CC Delinquency: {len(cc_delinq)} obs, last={cc_delinq.iloc[-1]:.2f}% on {cc_delinq.index[-1].strftime('%Y-%m-%d')}")
    print(f"  Consumer Credit: {len(consumer_credit)} obs, last=${consumer_credit.iloc[-1]:.2f}T on {consumer_credit.index[-1].strftime('%Y-%m-%d')}")

    # Set up figure
    fig, ax1 = plt.subplots(figsize=(12, 8))

    # === PANEL 1: Consumer Credit (Left Axis) ===
    # Plot as area fill to show the growing stock
    ax1.fill_between(consumer_credit.index, 0, consumer_credit.values,
                     alpha=0.3, color=COLORS['ocean_blue'], label='Consumer Credit ($T)')
    ax1.plot(consumer_credit.index, consumer_credit.values,
             linewidth=1.5, color=COLORS['ocean_blue'])

    ax1.set_ylabel('Consumer Credit Outstanding ($T)', color=COLORS['ocean_blue'], fontweight='bold')
    ax1.tick_params(axis='y', labelcolor=COLORS['ocean_blue'])
    ax1.set_ylim(3.0, consumer_credit.max() * 1.05)

    # === PANEL 2: Savings Rate (Right Axis) ===
    ax2 = ax1.twinx()

    # RAW monthly data - no smoothing
    # Using step='post' to show the actual data point values clearly
    ax2.plot(savings_rate.index, savings_rate.values,
             linewidth=1.2, color=COLORS['dusk_orange'],
             marker='.', markersize=2, alpha=0.8,
             label='Personal Savings Rate (%)')

    ax2.set_ylabel('Personal Savings Rate (%)', color=COLORS['dusk_orange'], fontweight='bold')
    ax2.tick_params(axis='y', labelcolor=COLORS['dusk_orange'])

    # Set y-axis to show full range including COVID spike
    ax2.set_ylim(-2, max(savings_rate.max() * 1.05, 35))

    # === EVENT MARKERS ===
    # These are the events that should be VISIBLE in the data
    events = [
        ('2020-04-01', 'CARES Act\n$1,200 checks', 33.8),  # Massive spike
        ('2021-01-01', '$600 checks', 20.0),
        ('2021-03-01', 'ARP\n$1,400 checks', 26.6),
        ('2021-07-01', 'Child Tax\nCredit', 10.0),
        ('2022-03-01', 'Reopening\ndrawdown', 6.0),
    ]

    for date_str, label, y_pos in events:
        event_date = pd.Timestamp(date_str)
        if event_date >= savings_rate.index.min():
            ax2.axvline(event_date, color=COLORS['silvs_gray'], linestyle=':', alpha=0.5, linewidth=1)
            ax2.annotate(label, xy=(event_date, y_pos),
                        fontsize=7, ha='center', va='bottom',
                        color=COLORS['neutral'],
                        bbox=dict(boxstyle='round,pad=0.2', facecolor='white',
                                 edgecolor=COLORS['silvs_gray'], alpha=0.8))

    # === CURRENT VALUE ANNOTATION ===
    current_val = savings_rate.iloc[-1]
    current_date = savings_rate.index[-1]

    # Calculate historical average and std dev (pre-COVID)
    pre_covid = savings_rate[savings_rate.index < '2020-01-01']
    hist_avg = pre_covid.mean()
    hist_std = pre_covid.std()

    # Add historical average line
    ax2.axhline(hist_avg, color=COLORS['dusk_orange'], linestyle='--',
                linewidth=1, alpha=0.5)
    ax2.text(savings_rate.index.min(), hist_avg + 0.3,
             f'Pre-COVID avg: {hist_avg:.1f}%', fontsize=8,
             color=COLORS['dusk_orange'], alpha=0.7)

    # Current value callout - with honest context
    ax2.annotate(
        f'Current: {current_val:.1f}%\n'
        f'(Pre-COVID avg: {hist_avg:.1f}%)\n'
        f'As of {current_date.strftime("%b %Y")}',
        xy=(current_date, current_val),
        xytext=(30, 30), textcoords='offset points',
        fontsize=9, fontweight='bold',
        color='white',
        bbox=dict(boxstyle='round,pad=0.4', facecolor=COLORS['dusk_orange'],
                 edgecolor='none', alpha=0.9),
        arrowprops=dict(arrowstyle='->', color=COLORS['dusk_orange'], lw=1.5))

    # === CC DELINQUENCY (Inset or annotation) ===
    # Add as text annotation since it's quarterly and different scale
    cc_current = cc_delinq.iloc[-1]
    cc_date = cc_delinq.index[-1]
    cc_pre_covid_avg = cc_delinq[cc_delinq.index < '2020-01-01'].mean()

    # Info box for delinquency
    info_text = (
        f"Credit Card Delinquency\n"
        f"Current: {cc_current:.2f}%\n"
        f"Pre-COVID avg: {cc_pre_covid_avg:.2f}%\n"
        f"As of {cc_date.strftime('%b %Y')} (quarterly)"
    )

    ax1.text(0.02, 0.98, info_text, transform=ax1.transAxes,
             fontsize=9, verticalalignment='top',
             bbox=dict(boxstyle='round,pad=0.5', facecolor='white',
                      edgecolor=COLORS['down_red'], linewidth=1.5, alpha=0.95),
             color=COLORS['down_red'], fontweight='bold')

    # === STYLING ===
    ax1.set_title('Consumer Bifurcation: Credit Growth vs Savings Collapse',
                  fontsize=14, fontweight='bold', pad=20)

    ax1.set_xlabel('')
    ax1.xaxis.set_major_locator(mdates.YearLocator())
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    # Remove gridlines
    ax1.grid(False)
    ax2.grid(False)

    # Clean spines
    ax1.spines['top'].set_visible(False)
    ax2.spines['top'].set_visible(False)
    ax1.spines['bottom'].set_color(COLORS['silvs_gray'])
    ax1.spines['left'].set_color(COLORS['ocean_blue'])
    ax2.spines['right'].set_color(COLORS['dusk_orange'])

    # === BRANDING ===
    fig.text(0.01, 0.99, 'LIGHTHOUSE MACRO', fontsize=10, fontweight='bold',
             color=COLORS['ocean_blue'], ha='left', va='top')
    fig.text(0.99, 0.01, 'MACRO, ILLUMINATED.', fontsize=8, style='italic',
             color=COLORS['ocean_blue'], ha='right', va='bottom', alpha=0.7)
    fig.text(0.01, 0.01, 'Source: FRED (PSAVERT, TOTALSL, DRCCLACBS) | Raw monthly/quarterly data, no smoothing',
             fontsize=7, color=COLORS['neutral'], ha='left', va='bottom', style='italic')

    # === LEGEND ===
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], color=COLORS['ocean_blue'], linewidth=2, label='Consumer Credit ($T)'),
        Line2D([0], [0], color=COLORS['dusk_orange'], linewidth=2, marker='.',
               markersize=4, label='Savings Rate (%, raw monthly)'),
    ]
    ax1.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(0.02, 0.85),
               frameon=True, facecolor='white', edgecolor=COLORS['silvs_gray'])

    plt.tight_layout()

    # Save
    if output_path is None:
        output_path = Path('/Users/bob/LHM/data/charts/priority1/chart_consumer_bifurcation.png')

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close(fig)

    print(f"\nSaved: {output_path}")
    return output_path


if __name__ == "__main__":
    generate_consumer_bifurcation_chart()
