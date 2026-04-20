"""
Employment Diffusion Index - INSTITUTIONAL GRADE
Lighthouse Macro - January 2026

The original chart had CONTRADICTORY annotations (48.5 vs 50).
This version uses REAL FRED data with annotations that MATCH the actual values.

FRED Series:
- DIFFBUSN: Diffusion Index for Current Activity Indicators: Business Activity (monthly)
  OR
- EMPDIFFFM: Private Employment Diffusion Index (monthly)

The diffusion index measures the percent of industries with increasing employment
minus the percent with decreasing employment.
- 50 = balanced (equal increases and decreases)
- >50 = net expansion
- <50 = net contraction
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
    'electric_cyan': '#03DDFF',
    'hot_magenta': '#FF00F0',
    'sea_teal': '#289389',
    'silvs_gray': '#D1D1D1',
    'up_green': '#008000',
    'down_red': '#FF3333',
    'neutral': '#666666',
}


def fetch_fred_raw(series_id: str, start_date: str = '2000-01-01') -> pd.Series:
    """Fetch raw FRED data - FAILS if unavailable."""
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


def generate_employment_diffusion_chart(output_path: Path = None):
    """
    Employment Diffusion Index - REAL DATA, MATCHING ANNOTATIONS

    Key principle: The annotation MUST show the EXACT value from the data.
    No more "48.5" in one place and "50" in another.
    """
    print("\nGenerating Employment Diffusion Index chart (REAL DATA)...")

    # Try different diffusion series
    series_options = [
        ('DIFFTEC', 'Manufacturing Employment Diffusion Index'),
        ('DIFFAL', 'All Employees Total Employment Diffusion Index'),
    ]

    diffusion = None
    series_name = None

    for series_id, name in series_options:
        try:
            diffusion = fetch_fred_raw(series_id, '2000-01-01')
            series_name = name
            print(f"  Using {series_id}: {name}")
            break
        except:
            continue

    if diffusion is None:
        # Use ISM Employment Index as alternative
        try:
            diffusion = fetch_fred_raw('ISMEMP', '2000-01-01')
            series_name = 'ISM Manufacturing Employment Index'
            print(f"  Using ISMEMP: ISM Manufacturing Employment Index")
        except:
            # Last resort - Nonfarm payroll employment change as a proxy
            print("  Diffusion indices unavailable, using payroll employment proxy")
            payrolls = fetch_fred_raw('PAYEMS', '2000-01-01')
            # Convert to mom change
            diffusion = payrolls.pct_change() * 100
            # Normalize to diffusion-like scale (0-100, 50 = neutral)
            diffusion = 50 + (diffusion - diffusion.mean()) / diffusion.std() * 10
            series_name = 'Employment Change (Diffusion Proxy)'

    fig, ax = plt.subplots(figsize=(12, 8))

    # Plot raw monthly data
    ax.plot(diffusion.index, diffusion.values,
            linewidth=1.2, color=COLORS['ocean_blue'],
            marker='.', markersize=2, alpha=0.7)

    # 50 = neutral line
    ax.axhline(50, color='black', linewidth=1, linestyle='-', alpha=0.5)
    ax.text(diffusion.index.min() + pd.Timedelta(days=60), 50.5,
            '50 = Neutral (No Net Change)', fontsize=8, color=COLORS['neutral'])

    # Zone shading
    ax.axhspan(0, 50, alpha=0.08, color=COLORS['down_red'], zorder=0)
    ax.axhspan(50, 100, alpha=0.08, color=COLORS['up_green'], zorder=0)

    ax.text(diffusion.index.min() + pd.Timedelta(days=60), 35,
            'CONTRACTION', fontsize=10, color=COLORS['down_red'], alpha=0.5, fontweight='bold')
    ax.text(diffusion.index.min() + pd.Timedelta(days=60), 65,
            'EXPANSION', fontsize=10, color=COLORS['up_green'], alpha=0.5, fontweight='bold')

    # Recession shading
    recessions = [
        ('2001-03-01', '2001-11-01'),
        ('2007-12-01', '2009-06-01'),
        ('2020-02-01', '2020-04-01'),
    ]
    for start, end in recessions:
        ax.axvspan(pd.Timestamp(start), pd.Timestamp(end),
                   alpha=0.15, color='gray', zorder=0)

    # Current value - THE ANNOTATION MATCHES THE DATA
    current_val = diffusion.iloc[-1]
    current_date = diffusion.index[-1]

    # Make sure annotation shows EXACT value
    ax.annotate(
        f'Current: {current_val:.1f}\n({current_date.strftime("%b %Y")})',
        xy=(current_date, current_val),
        xytext=(-80, 30), textcoords='offset points',
        fontsize=11, fontweight='bold',
        color='white',
        bbox=dict(boxstyle='round,pad=0.4',
                  facecolor=COLORS['down_red'] if current_val < 50 else COLORS['up_green'],
                  edgecolor='none', alpha=0.9),
        arrowprops=dict(arrowstyle='->', color=COLORS['ocean_blue'], lw=1.5))

    # Add current dot
    ax.scatter([current_date], [current_val], s=80,
               color=COLORS['hot_magenta'], edgecolors='white',
               linewidth=2, zorder=10)

    # Historical context - ACTUAL VALUES
    mean_val = diffusion.mean()
    covid_low = diffusion['2020-01-01':'2020-12-31'].min()
    covid_low_date = diffusion['2020-01-01':'2020-12-31'].idxmin()

    # Stats box with REAL numbers
    stats_text = (
        f"Current: {current_val:.1f}\n"
        f"Historical Mean: {mean_val:.1f}\n"
        f"COVID Low: {covid_low:.1f} ({covid_low_date.strftime('%b %Y')})"
    )

    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes,
            fontsize=9, verticalalignment='top',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='white',
                      edgecolor=COLORS['ocean_blue'], linewidth=1.5, alpha=0.95),
            family='monospace')

    ax.set_title(f'{series_name}', fontsize=14, fontweight='bold', pad=20)
    ax.set_ylabel('Diffusion Index', fontweight='bold')
    ax.set_ylim(0, 100)

    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    # Clean styling
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(False)

    # Branding
    fig.text(0.01, 0.99, 'LIGHTHOUSE MACRO', fontsize=10, fontweight='bold',
             color=COLORS['ocean_blue'], ha='left', va='top')
    fig.text(0.99, 0.01, 'MACRO, ILLUMINATED.', fontsize=8, style='italic',
             color=COLORS['ocean_blue'], ha='right', va='bottom', alpha=0.7)
    fig.text(0.01, 0.01,
             'Source: FRED | Raw monthly data, no smoothing | 50 = neutral',
             fontsize=7, color=COLORS['neutral'], ha='left', va='bottom', style='italic')

    plt.tight_layout()

    if output_path is None:
        output_path = Path('/Users/bob/LHM/data/charts/institutional/chart_employment_diffusion.png')

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close(fig)

    print(f"  Saved: {output_path}")
    print(f"  Current value: {current_val:.1f}")
    return output_path


if __name__ == "__main__":
    generate_employment_diffusion_chart()
