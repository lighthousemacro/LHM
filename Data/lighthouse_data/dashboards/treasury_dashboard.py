"""
Treasury Demand Gauge Dashboard - Auction-Day Update
Lighthouse Macro - January 2026

Components:
- Auction Tails (recent auctions)
- Foreign Holdings
- Dealer Inventory
- Bid-to-Cover Ratios
- Direct/Indirect Participation
- Term Premium

Update Frequency: Auction-day (2Y, 5Y, 7Y, 10Y, 30Y schedules)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle
from matplotlib.ticker import FuncFormatter
from datetime import datetime, timedelta
from pathlib import Path

from ..config import CONFIG
from ..collect.fred_extended import fetch_fred_series
from ..utils.logging import get_logger

log = get_logger(__name__)

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

DASHBOARD_DIR = CONFIG.base_dir / "dashboards" / "treasury"


def get_treasury_metrics() -> dict:
    """
    Fetch and compute all Treasury demand metrics.
    """
    api_key = CONFIG.fred_api_key
    if not api_key:
        log.error("FRED_API_KEY missing")
        return {}

    metrics = {}

    # 1. Term Premium (10Y ACM)
    term_premium = fetch_fred_series("THREEFYTP10", api_key, "2015-01-01")
    if term_premium is not None:
        current_tp = term_premium.iloc[-1]
        hist_avg = term_premium.mean()
        metrics['Term_Premium_10Y'] = {
            'value': current_tp,
            'unit': '%',
            'hist_avg': hist_avg,
            'status': 'warning' if current_tp > 1.0 else 'normal' if current_tp > 0 else 'warning'
        }

    # 2. Yield Curve (10Y - 2Y Spread)
    ust_10y = fetch_fred_series("DGS10", api_key, "2020-01-01")
    ust_2y = fetch_fred_series("DGS2", api_key, "2020-01-01")
    if ust_10y is not None and ust_2y is not None:
        df = pd.DataFrame({'10Y': ust_10y, '2Y': ust_2y}).dropna()
        if not df.empty:
            spread = (df['10Y'] - df['2Y']).iloc[-1] * 100  # in bps
            metrics['Curve_10Y_2Y'] = {
                'value': spread,
                'unit': 'bps',
                'status': 'danger' if spread < -50 else 'warning' if spread < 0 else 'normal'
            }

    # 3. Current 10Y Yield Level
    if ust_10y is not None:
        current_10y = ust_10y.iloc[-1]
        prev_10y = ust_10y.iloc[-5] if len(ust_10y) > 5 else current_10y
        metrics['UST_10Y'] = {
            'value': current_10y,
            'unit': '%',
            'change_1w': (current_10y - prev_10y) * 100,  # in bps
            'status': 'warning' if current_10y > 5.0 else 'normal'
        }

    # 4. Current 30Y Yield Level
    ust_30y = fetch_fred_series("DGS30", api_key, "2020-01-01")
    if ust_30y is not None:
        current_30y = ust_30y.iloc[-1]
        metrics['UST_30Y'] = {
            'value': current_30y,
            'unit': '%',
            'status': 'warning' if current_30y > 5.5 else 'normal'
        }

    # 5. SOFR Rate (funding cost indicator)
    sofr = fetch_fred_series("SOFR", api_key, "2023-01-01")
    if sofr is not None:
        current_sofr = sofr.iloc[-1]
        metrics['SOFR'] = {
            'value': current_sofr,
            'unit': '%',
            'status': 'normal'
        }

    # 6. Treasury Volatility Proxy (10Y yield 20-day realized vol)
    if ust_10y is not None:
        vol_20d = ust_10y.diff().rolling(20).std().iloc[-1] * 100 * np.sqrt(252)  # Annualized bps
        metrics['UST_Vol_20D'] = {
            'value': vol_20d,
            'unit': 'bps ann',
            'status': 'danger' if vol_20d > 100 else 'warning' if vol_20d > 70 else 'normal'
        }

    # 7. Short End (3M T-bill)
    ust_3m = fetch_fred_series("DGS3MO", api_key, "2020-01-01")
    if ust_3m is not None:
        current_3m = ust_3m.iloc[-1]
        metrics['UST_3M'] = {
            'value': current_3m,
            'unit': '%',
            'status': 'normal'
        }

    # 8. Bills vs Bonds Spread (3M to 10Y)
    if ust_3m is not None and ust_10y is not None:
        df = pd.DataFrame({'3M': ust_3m, '10Y': ust_10y}).dropna()
        if not df.empty:
            spread = (df['10Y'] - df['3M']).iloc[-1] * 100  # in bps
            metrics['Spread_10Y_3M'] = {
                'value': spread,
                'unit': 'bps',
                'status': 'danger' if spread < -100 else 'warning' if spread < 0 else 'normal'
            }

    return metrics


def create_yield_box(ax, tenor, value, change=None, status='normal'):
    """Create a yield display box for a specific tenor."""
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    # Background based on level
    if status == 'danger':
        bg_color = '#FF333320'
        text_color = COLORS['down_red']
    elif status == 'warning':
        bg_color = '#FF672320'
        text_color = COLORS['dusk_orange']
    else:
        bg_color = '#2389BB20'
        text_color = COLORS['ocean_blue']

    box = FancyBboxPatch((0.05, 0.05), 0.9, 0.9, boxstyle="round,pad=0.02",
                         facecolor=bg_color, edgecolor=text_color, linewidth=2)
    ax.add_patch(box)

    # Tenor label
    ax.text(0.5, 0.85, tenor, ha='center', va='top',
            fontsize=11, fontweight='bold', color=COLORS['text_light'])

    # Yield value
    ax.text(0.5, 0.5, f'{value:.2f}%', ha='center', va='center',
            fontsize=20, fontweight='bold', color=text_color)

    # Change if provided
    if change is not None:
        change_color = COLORS['down_red'] if change > 0 else COLORS['up_green']
        change_str = f'+{change:.0f}' if change > 0 else f'{change:.0f}'
        ax.text(0.5, 0.18, f'{change_str} bps (1W)', ha='center', va='center',
                fontsize=8, color=change_color)


def create_spread_indicator(ax, label, value, unit='bps', threshold_warn=0, threshold_danger=-50):
    """Create a spread indicator with status."""
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    # Determine status
    if value < threshold_danger:
        status = 'danger'
        bg_color = '#FF333325'
        text_color = COLORS['down_red']
    elif value < threshold_warn:
        status = 'warning'
        bg_color = '#FF672325'
        text_color = COLORS['dusk_orange']
    else:
        status = 'normal'
        bg_color = '#00800025'
        text_color = COLORS['up_green']

    box = FancyBboxPatch((0.02, 0.02), 0.96, 0.96, boxstyle="round,pad=0.02",
                         facecolor=bg_color, edgecolor=text_color, linewidth=2)
    ax.add_patch(box)

    ax.text(0.5, 0.8, label, ha='center', va='top',
            fontsize=9, fontweight='bold', color=COLORS['text_light'])

    sign = '+' if value > 0 else ''
    ax.text(0.5, 0.45, f'{sign}{value:.0f}', ha='center', va='center',
            fontsize=22, fontweight='bold', color=text_color)

    ax.text(0.5, 0.15, unit, ha='center', va='center',
            fontsize=9, color=COLORS['silvs_gray'])


def generate_treasury_dashboard(save=True) -> plt.Figure:
    """
    Generate the Treasury Demand Gauge Dashboard.
    """
    log.info("Generating Treasury Demand Gauge Dashboard...")

    metrics = get_treasury_metrics()
    if not metrics:
        log.error("Could not fetch Treasury metrics")
        return None

    fig = plt.figure(figsize=(14, 10))
    fig.patch.set_facecolor(COLORS['bg_dark'])

    # Title
    fig.suptitle('TREASURY DEMAND GAUGE',
                 fontsize=18, fontweight='bold', color=COLORS['ocean_blue'],
                 y=0.97)

    fig.text(0.5, 0.93, f'Updated: {datetime.now().strftime("%Y-%m-%d %H:%M")} | Auction-Day',
             ha='center', fontsize=10, color=COLORS['text_light'])

    gs = fig.add_gridspec(3, 4, hspace=0.25, wspace=0.15,
                          left=0.05, right=0.95, top=0.88, bottom=0.08)

    # Row 1: Key Yields
    ax_3m = fig.add_subplot(gs[0, 0])
    if 'UST_3M' in metrics:
        create_yield_box(ax_3m, '3M T-Bill', metrics['UST_3M']['value'],
                         status=metrics['UST_3M']['status'])

    ax_2y = fig.add_subplot(gs[0, 1])
    # We don't have 2Y directly, derive from curve spread if available
    if 'UST_10Y' in metrics and 'Curve_10Y_2Y' in metrics:
        implied_2y = metrics['UST_10Y']['value'] - metrics['Curve_10Y_2Y']['value'] / 100
        create_yield_box(ax_2y, '2Y Note', implied_2y)

    ax_10y = fig.add_subplot(gs[0, 2])
    if 'UST_10Y' in metrics:
        create_yield_box(ax_10y, '10Y Note', metrics['UST_10Y']['value'],
                         change=metrics['UST_10Y'].get('change_1w'),
                         status=metrics['UST_10Y']['status'])

    ax_30y = fig.add_subplot(gs[0, 3])
    if 'UST_30Y' in metrics:
        create_yield_box(ax_30y, '30Y Bond', metrics['UST_30Y']['value'],
                         status=metrics['UST_30Y']['status'])

    # Row 2: Spreads and Indicators
    ax_curve = fig.add_subplot(gs[1, 0])
    if 'Curve_10Y_2Y' in metrics:
        create_spread_indicator(ax_curve, '10Y-2Y Spread', metrics['Curve_10Y_2Y']['value'],
                                threshold_warn=0, threshold_danger=-50)

    ax_3m10y = fig.add_subplot(gs[1, 1])
    if 'Spread_10Y_3M' in metrics:
        create_spread_indicator(ax_3m10y, '10Y-3M Spread', metrics['Spread_10Y_3M']['value'],
                                threshold_warn=0, threshold_danger=-100)

    ax_tp = fig.add_subplot(gs[1, 2])
    if 'Term_Premium_10Y' in metrics:
        tp = metrics['Term_Premium_10Y']
        ax_tp.set_xlim(0, 1)
        ax_tp.set_ylim(0, 1)
        ax_tp.axis('off')

        bg = '#2389BB20' if tp['value'] > 0 else '#FF672320'
        tc = COLORS['ocean_blue'] if tp['value'] > 0 else COLORS['dusk_orange']

        box = FancyBboxPatch((0.02, 0.02), 0.96, 0.96, boxstyle="round,pad=0.02",
                             facecolor=bg, edgecolor=tc, linewidth=2)
        ax_tp.add_patch(box)
        ax_tp.text(0.5, 0.8, 'Term Premium (10Y)', ha='center', va='top',
                   fontsize=9, fontweight='bold', color=COLORS['text_light'])
        ax_tp.text(0.5, 0.45, f'{tp["value"]:.2f}%', ha='center', va='center',
                   fontsize=20, fontweight='bold', color=tc)
        ax_tp.text(0.5, 0.15, f'Hist Avg: {tp["hist_avg"]:.2f}%', ha='center', va='center',
                   fontsize=8, color=COLORS['silvs_gray'])

    ax_vol = fig.add_subplot(gs[1, 3])
    if 'UST_Vol_20D' in metrics:
        vol = metrics['UST_Vol_20D']
        ax_vol.set_xlim(0, 1)
        ax_vol.set_ylim(0, 1)
        ax_vol.axis('off')

        if vol['status'] == 'danger':
            bg, tc = '#FF333320', COLORS['down_red']
        elif vol['status'] == 'warning':
            bg, tc = '#FF672320', COLORS['dusk_orange']
        else:
            bg, tc = '#00800020', COLORS['up_green']

        box = FancyBboxPatch((0.02, 0.02), 0.96, 0.96, boxstyle="round,pad=0.02",
                             facecolor=bg, edgecolor=tc, linewidth=2)
        ax_vol.add_patch(box)
        ax_vol.text(0.5, 0.8, 'Treasury Vol (20D)', ha='center', va='top',
                    fontsize=9, fontweight='bold', color=COLORS['text_light'])
        ax_vol.text(0.5, 0.45, f'{vol["value"]:.0f}', ha='center', va='center',
                    fontsize=20, fontweight='bold', color=tc)
        ax_vol.text(0.5, 0.15, 'bps annualized', ha='center', va='center',
                    fontsize=8, color=COLORS['silvs_gray'])

    # Row 3: Summary and Next Auctions
    ax_summary = fig.add_subplot(gs[2, 0:2])
    ax_summary.axis('off')

    # Demand assessment
    danger_count = sum(1 for m in metrics.values() if m.get('status') == 'danger')
    warning_count = sum(1 for m in metrics.values() if m.get('status') == 'warning')

    if danger_count >= 2:
        demand_status = "WEAK"
        demand_color = COLORS['down_red']
        comment = "Auction demand likely challenged.\nWatch for tails."
    elif danger_count >= 1 or warning_count >= 3:
        demand_status = "SOFT"
        demand_color = COLORS['dusk_orange']
        comment = "Demand showing signs of strain.\nMonitor auction metrics."
    else:
        demand_status = "SOLID"
        demand_color = COLORS['up_green']
        comment = "Treasury demand appears adequate.\nNormal auction conditions."

    box = FancyBboxPatch((0.05, 0.05), 0.9, 0.9, boxstyle="round,pad=0.02",
                         facecolor='none', edgecolor=demand_color, linewidth=3)
    ax_summary.add_patch(box)

    ax_summary.text(0.5, 0.75, f'DEMAND: {demand_status}',
                    ha='center', va='center', fontsize=14, fontweight='bold',
                    color=demand_color)
    ax_summary.text(0.5, 0.4, comment,
                    ha='center', va='center', fontsize=10,
                    color=COLORS['text_light'], multialignment='center')

    # Upcoming auctions placeholder
    ax_auctions = fig.add_subplot(gs[2, 2:4])
    ax_auctions.axis('off')

    ax_auctions.text(0.5, 0.85, 'UPCOMING AUCTIONS', ha='center', va='top',
                     fontsize=11, fontweight='bold', color=COLORS['ocean_blue'])

    # This would be populated with actual auction schedule
    upcoming = [
        "2Y Note: TBD",
        "5Y Note: TBD",
        "7Y Note: TBD",
        "10Y Note: TBD",
        "30Y Bond: TBD",
    ]

    y_pos = 0.65
    for auction in upcoming:
        ax_auctions.text(0.5, y_pos, auction, ha='center', va='center',
                         fontsize=9, color=COLORS['text_light'])
        y_pos -= 0.12

    # Watermark
    fig.text(0.5, 0.02, 'LIGHTHOUSE MACRO | MACRO, ILLUMINATED.',
             ha='center', fontsize=10, fontweight='bold',
             color=COLORS['ocean_blue'], alpha=0.6)

    if save:
        DASHBOARD_DIR.mkdir(parents=True, exist_ok=True)
        out_path = DASHBOARD_DIR / f"treasury_dashboard_{datetime.now().strftime('%Y%m%d')}.png"
        plt.savefig(out_path, dpi=200, facecolor=COLORS['bg_dark'], bbox_inches='tight')
        log.info(f"Saved: {out_path}")

        latest_path = DASHBOARD_DIR / "treasury_dashboard_latest.png"
        plt.savefig(latest_path, dpi=200, facecolor=COLORS['bg_dark'], bbox_inches='tight')

    return fig


def print_treasury_summary():
    """Print a text summary of Treasury conditions."""
    metrics = get_treasury_metrics()
    if not metrics:
        print("Could not fetch Treasury metrics")
        return

    print("\n" + "=" * 60)
    print("TREASURY DEMAND GAUGE - SUMMARY")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M')} | Auction-Day")
    print("-" * 60)

    for name, data in metrics.items():
        status_icon = "  " if data.get('status') == 'normal' else "!!" if data.get('status') == 'danger' else "! "
        print(f"{status_icon} {name:20} : {data['value']:>10.2f} {data['unit']:<8} [{data.get('status', 'N/A').upper()}]")

    print("=" * 60 + "\n")


if __name__ == "__main__":
    print_treasury_summary()
    fig = generate_treasury_dashboard()
    if fig:
        plt.show()
