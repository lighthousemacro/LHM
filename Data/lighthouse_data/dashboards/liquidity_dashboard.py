"""
Liquidity Stress Dashboard - Daily Update
Lighthouse Macro - January 2026

Components:
- LCI (Liquidity Cushion Index)
- SOFR-EFFR Spread
- SRF Usage
- TGA Balance
- Reserves/GDP
- RRP Balance

Update Frequency: Daily
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch
from matplotlib.ticker import FuncFormatter
from datetime import datetime
from pathlib import Path

from ..config import CONFIG
from ..collect.fred_extended import fetch_fred_series, get_tga_history, get_fed_balance_sheet
from ..features.transforms_core import zscore
from ..utils.logging import get_logger
from ..utils.io import read_parquet, write_parquet

log = get_logger(__name__)

# Colors
COLORS = {
    'ocean_blue': '#2389BB',
    'dusk_orange': '#FF6723',
    'electric_cyan': '#03DDFF',
    'hot_magenta': '#FF00F0',
    'sea_teal': '#289389',
    'silvs_gray': '#D1D1D1',
    'up_green': '#008000',
    'down_red': '#FF3333',
    'neutral': '#808080',
    'bg_dark': '#0E1117',
    'text_light': '#E0E0E0',
}

DASHBOARD_DIR = CONFIG.base_dir / "dashboards" / "liquidity"


def get_liquidity_metrics() -> dict:
    """
    Fetch and compute all liquidity metrics for the dashboard.

    Returns:
        dict with current values, changes, and signal status
    """
    api_key = CONFIG.fred_api_key
    if not api_key:
        log.error("FRED_API_KEY missing")
        return {}

    metrics = {}

    # 1. TGA Balance
    tga = get_tga_history()
    if not tga.empty:
        current_tga = tga['TGA_Balance'].iloc[-1] / 1e6  # Billions
        prev_tga = tga['TGA_Balance'].iloc[-7] / 1e6 if len(tga) > 7 else current_tga
        metrics['TGA'] = {
            'value': current_tga,
            'change_1w': current_tga - prev_tga,
            'unit': '$B',
            'status': 'danger' if current_tga < 100 else 'warning' if current_tga < 300 else 'normal'
        }

    # 2. Fed Balance Sheet Components
    fed_bs = get_fed_balance_sheet()
    if not fed_bs.empty:
        # Reserves
        reserves = fed_bs['Reserves'].iloc[-1] / 1e6  # Trillions
        metrics['Reserves'] = {
            'value': reserves,
            'unit': '$T',
            'status': 'danger' if reserves < 2.8 else 'warning' if reserves < 3.2 else 'normal'
        }

        # RRP
        rrp = fed_bs['RRP'].iloc[-1] / 1e6
        metrics['RRP'] = {
            'value': rrp,
            'unit': '$T',
            'status': 'danger' if rrp < 0.1 else 'warning' if rrp < 0.3 else 'normal'
        }

    # 3. SOFR - EFFR Spread
    sofr = fetch_fred_series("SOFR", api_key, "2023-01-01")
    effr = fetch_fred_series("EFFR", api_key, "2023-01-01")
    if sofr is not None and effr is not None:
        sofr_effr = (sofr - effr) * 100  # Convert to bps
        current_spread = sofr_effr.iloc[-1]
        metrics['SOFR_EFFR'] = {
            'value': current_spread,
            'unit': 'bps',
            'status': 'danger' if current_spread > 20 else 'warning' if current_spread > 10 else 'normal'
        }

    # 4. Reserves/GDP ratio
    reserves_series = fetch_fred_series("WRESBAL", api_key, "2015-01-01")
    gdp_series = fetch_fred_series("GDP", api_key, "2015-01-01")
    if reserves_series is not None and gdp_series is not None:
        # Align and compute ratio
        df = pd.DataFrame({'Reserves': reserves_series, 'GDP': gdp_series})
        df = df.resample('D').ffill().dropna()
        if not df.empty:
            # GDP is quarterly in billions, reserves is weekly in millions
            # Convert reserves to billions
            df['Reserves_B'] = df['Reserves'] / 1e3
            df['Reserves_GDP'] = df['Reserves_B'] / df['GDP'] * 100
            current_ratio = df['Reserves_GDP'].iloc[-1]
            metrics['Reserves_GDP'] = {
                'value': current_ratio,
                'unit': '%',
                'status': 'danger' if current_ratio < 11 else 'warning' if current_ratio < 12 else 'normal'
            }

    # 5. Compute LCI
    if 'Reserves' in metrics and 'RRP' in metrics and 'Reserves_GDP' in metrics:
        # Simplified LCI = avg of z-scores
        # For dashboard, we use a heuristic based on current levels
        rrp_depleted = metrics['RRP']['value'] < 0.1
        reserves_tight = metrics['Reserves_GDP']['value'] < 12

        if rrp_depleted and reserves_tight:
            lci_status = 'danger'
            lci_value = -1.5
        elif rrp_depleted or reserves_tight:
            lci_status = 'warning'
            lci_value = -0.5
        else:
            lci_status = 'normal'
            lci_value = 0.5

        metrics['LCI'] = {
            'value': lci_value,
            'unit': 'z-score',
            'status': lci_status
        }

    return metrics


def create_gauge(ax, value, min_val, max_val, label, status='normal'):
    """Create a gauge-style indicator."""
    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-0.2, 1.2)
    ax.axis('off')

    # Gauge arc
    theta = np.linspace(np.pi, 0, 100)
    r = 1
    x = r * np.cos(theta)
    y = r * np.sin(theta)
    ax.plot(x, y, color=COLORS['silvs_gray'], linewidth=8, solid_capstyle='round')

    # Colored segment based on value
    norm_val = (value - min_val) / (max_val - min_val)
    norm_val = np.clip(norm_val, 0, 1)

    # Color zones
    if status == 'danger':
        color = COLORS['down_red']
    elif status == 'warning':
        color = COLORS['dusk_orange']
    else:
        color = COLORS['up_green']

    theta_val = np.pi - norm_val * np.pi
    x_needle = [0, 0.8 * np.cos(theta_val)]
    y_needle = [0, 0.8 * np.sin(theta_val)]
    ax.plot(x_needle, y_needle, color=color, linewidth=3, solid_capstyle='round')

    # Center dot
    ax.scatter([0], [0], s=100, color=color, zorder=10)

    # Value text
    ax.text(0, -0.1, f'{value:.2f}', ha='center', va='top',
            fontsize=16, fontweight='bold', color=color)

    # Label
    ax.text(0, 1.15, label, ha='center', va='bottom',
            fontsize=11, fontweight='bold', color=COLORS['neutral'])


def create_metric_box(ax, label, value, unit, change=None, status='normal'):
    """Create a metric box with value and change."""
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    # Background
    if status == 'danger':
        bg_color = '#FF333320'
        text_color = COLORS['down_red']
    elif status == 'warning':
        bg_color = '#FF672320'
        text_color = COLORS['dusk_orange']
    else:
        bg_color = '#00800020'
        text_color = COLORS['up_green']

    box = FancyBboxPatch((0.05, 0.05), 0.9, 0.9, boxstyle="round,pad=0.02",
                         facecolor=bg_color, edgecolor=text_color, linewidth=2)
    ax.add_patch(box)

    # Label
    ax.text(0.5, 0.85, label, ha='center', va='top',
            fontsize=10, fontweight='bold', color=COLORS['neutral'])

    # Value
    ax.text(0.5, 0.5, f'{value:.1f}', ha='center', va='center',
            fontsize=24, fontweight='bold', color=text_color)

    # Unit
    ax.text(0.5, 0.25, unit, ha='center', va='center',
            fontsize=10, color=COLORS['neutral'])

    # Change (if provided)
    if change is not None:
        change_color = COLORS['up_green'] if change >= 0 else COLORS['down_red']
        change_text = f'+{change:.1f}' if change >= 0 else f'{change:.1f}'
        ax.text(0.5, 0.1, f'1W: {change_text}', ha='center', va='center',
                fontsize=8, color=change_color)


def generate_liquidity_dashboard(save=True) -> plt.Figure:
    """
    Generate the Liquidity Stress Dashboard.

    Layout:
    - Top row: LCI gauge + status indicators
    - Middle row: TGA, Reserves, RRP boxes
    - Bottom row: SOFR-EFFR spread, Reserves/GDP
    """
    log.info("Generating Liquidity Stress Dashboard...")

    metrics = get_liquidity_metrics()
    if not metrics:
        log.error("Could not fetch liquidity metrics")
        return None

    # Create figure with dark background
    fig = plt.figure(figsize=(14, 10))
    fig.patch.set_facecolor(COLORS['bg_dark'])

    # Title
    fig.suptitle('LIQUIDITY STRESS DASHBOARD',
                 fontsize=18, fontweight='bold', color=COLORS['ocean_blue'],
                 y=0.97)

    # Subtitle with timestamp
    fig.text(0.5, 0.93, f'Updated: {datetime.now().strftime("%Y-%m-%d %H:%M")} ET',
             ha='center', fontsize=10, color=COLORS['text_light'])

    # Create grid
    gs = fig.add_gridspec(3, 4, hspace=0.3, wspace=0.2,
                          left=0.05, right=0.95, top=0.88, bottom=0.08)

    # Row 1: LCI Gauge (spans 2 cols)
    ax_lci = fig.add_subplot(gs[0, 1:3])
    if 'LCI' in metrics:
        create_gauge(ax_lci, metrics['LCI']['value'], -2, 2,
                     'Liquidity Cushion Index (LCI)', metrics['LCI']['status'])

    # Overall status
    ax_status = fig.add_subplot(gs[0, 3])
    ax_status.axis('off')
    overall_status = 'STRESSED' if any(m.get('status') == 'danger' for m in metrics.values()) else \
                     'CAUTION' if any(m.get('status') == 'warning' for m in metrics.values()) else 'NORMAL'
    status_color = COLORS['down_red'] if overall_status == 'STRESSED' else \
                   COLORS['dusk_orange'] if overall_status == 'CAUTION' else COLORS['up_green']
    ax_status.text(0.5, 0.5, f'STATUS:\n{overall_status}', ha='center', va='center',
                   fontsize=14, fontweight='bold', color=status_color)

    # Row 2: TGA, Reserves, RRP
    if 'TGA' in metrics:
        ax_tga = fig.add_subplot(gs[1, 0])
        create_metric_box(ax_tga, 'TGA Balance', metrics['TGA']['value'],
                          metrics['TGA']['unit'], metrics['TGA'].get('change_1w'),
                          metrics['TGA']['status'])

    if 'Reserves' in metrics:
        ax_res = fig.add_subplot(gs[1, 1])
        create_metric_box(ax_res, 'Bank Reserves', metrics['Reserves']['value'],
                          metrics['Reserves']['unit'], status=metrics['Reserves']['status'])

    if 'RRP' in metrics:
        ax_rrp = fig.add_subplot(gs[1, 2])
        create_metric_box(ax_rrp, 'RRP Balance', metrics['RRP']['value'],
                          metrics['RRP']['unit'], status=metrics['RRP']['status'])

    # Placeholder for SRF Usage
    ax_srf = fig.add_subplot(gs[1, 3])
    create_metric_box(ax_srf, 'SRF Usage', 0.0, '$B', status='normal')

    # Row 3: SOFR-EFFR, Reserves/GDP
    if 'SOFR_EFFR' in metrics:
        ax_spread = fig.add_subplot(gs[2, 0:2])
        create_metric_box(ax_spread, 'SOFR-EFFR Spread', metrics['SOFR_EFFR']['value'],
                          metrics['SOFR_EFFR']['unit'], status=metrics['SOFR_EFFR']['status'])

    if 'Reserves_GDP' in metrics:
        ax_ratio = fig.add_subplot(gs[2, 2:4])
        create_metric_box(ax_ratio, 'Reserves/GDP', metrics['Reserves_GDP']['value'],
                          metrics['Reserves_GDP']['unit'], status=metrics['Reserves_GDP']['status'])

    # Watermark
    fig.text(0.5, 0.02, 'LIGHTHOUSE MACRO | MACRO, ILLUMINATED.',
             ha='center', fontsize=10, fontweight='bold',
             color=COLORS['ocean_blue'], alpha=0.6)

    if save:
        DASHBOARD_DIR.mkdir(parents=True, exist_ok=True)
        out_path = DASHBOARD_DIR / f"liquidity_dashboard_{datetime.now().strftime('%Y%m%d')}.png"
        plt.savefig(out_path, dpi=200, facecolor=COLORS['bg_dark'], bbox_inches='tight')
        log.info(f"Saved: {out_path}")

        # Also save as "latest"
        latest_path = DASHBOARD_DIR / "liquidity_dashboard_latest.png"
        plt.savefig(latest_path, dpi=200, facecolor=COLORS['bg_dark'], bbox_inches='tight')

    return fig


def print_liquidity_summary():
    """Print a text summary of liquidity conditions."""
    metrics = get_liquidity_metrics()
    if not metrics:
        print("Could not fetch liquidity metrics")
        return

    print("\n" + "=" * 60)
    print("LIQUIDITY STRESS DASHBOARD - SUMMARY")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M')} ET")
    print("-" * 60)

    for name, data in metrics.items():
        status_icon = "  " if data['status'] == 'normal' else "!!" if data['status'] == 'danger' else "! "
        print(f"{status_icon} {name:15} : {data['value']:>10.2f} {data['unit']:<6} [{data['status'].upper()}]")

    print("-" * 60)

    # Overall assessment
    if any(m.get('status') == 'danger' for m in metrics.values()):
        print("OVERALL: STRESSED - Liquidity conditions are tight")
    elif any(m.get('status') == 'warning' for m in metrics.values()):
        print("OVERALL: CAUTION - Monitor for deterioration")
    else:
        print("OVERALL: NORMAL - Liquidity conditions adequate")

    print("=" * 60 + "\n")


if __name__ == "__main__":
    print_liquidity_summary()
    fig = generate_liquidity_dashboard()
    if fig:
        plt.show()
