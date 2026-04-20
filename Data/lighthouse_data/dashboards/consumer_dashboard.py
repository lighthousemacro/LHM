"""
Consumer Solvency Tracker Dashboard - Monthly Update
Lighthouse Macro - January 2026

Components:
- Personal Savings Rate
- Consumer Credit Growth
- Credit Card Delinquency Rate
- Auto Delinquency Rate
- Mortgage Delinquency Rate
- Debt Service Ratio

Update Frequency: Monthly
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from datetime import datetime
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

DASHBOARD_DIR = CONFIG.base_dir / "dashboards" / "consumer"


def get_consumer_metrics() -> dict:
    """
    Fetch and compute all consumer metrics for the dashboard.
    """
    api_key = CONFIG.fred_api_key
    if not api_key:
        log.error("FRED_API_KEY missing")
        return {}

    metrics = {}

    # 1. Personal Savings Rate
    savings = fetch_fred_series("PSAVERT", api_key, "2015-01-01")
    if savings is not None:
        current_savings = savings.iloc[-1]
        hist_avg = savings.mean()
        metrics['Savings_Rate'] = {
            'value': current_savings,
            'unit': '%',
            'hist_avg': hist_avg,
            'status': 'danger' if current_savings < 3.5 else 'warning' if current_savings < 5.0 else 'normal'
        }

    # 2. Consumer Credit Growth (YoY)
    credit = fetch_fred_series("TOTALSL", api_key, "2015-01-01")
    if credit is not None:
        yoy_growth = (credit.iloc[-1] / credit.iloc[-12] - 1) * 100 if len(credit) > 12 else 0
        metrics['Credit_Growth_YoY'] = {
            'value': yoy_growth,
            'unit': '%',
            'status': 'warning' if yoy_growth > 8 else 'normal' if yoy_growth > 0 else 'warning'
        }

    # 3. Credit Card Delinquency Rate
    cc_delinq = fetch_fred_series("DRCCLACBS", api_key, "2015-01-01")
    if cc_delinq is not None:
        current_cc = cc_delinq.iloc[-1]
        # Pre-COVID average was ~2.5%
        metrics['CC_Delinquency'] = {
            'value': current_cc,
            'unit': '%',
            'pre_covid': 2.5,
            'status': 'danger' if current_cc > 3.5 else 'warning' if current_cc > 2.8 else 'normal'
        }

    # 4. Auto Loan Delinquency (Subprime)
    # Note: This specific series may not be available on FRED
    # Using general auto delinquency as proxy
    auto_delinq = fetch_fred_series("DRCLACBS", api_key, "2015-01-01")
    if auto_delinq is not None:
        current_auto = auto_delinq.iloc[-1]
        metrics['Auto_Delinquency'] = {
            'value': current_auto,
            'unit': '%',
            'status': 'danger' if current_auto > 3.0 else 'warning' if current_auto > 2.5 else 'normal'
        }

    # 5. Mortgage Delinquency Rate
    mtg_delinq = fetch_fred_series("DRSFRMACBS", api_key, "2015-01-01")
    if mtg_delinq is not None:
        current_mtg = mtg_delinq.iloc[-1]
        metrics['Mortgage_Delinquency'] = {
            'value': current_mtg,
            'unit': '%',
            'status': 'danger' if current_mtg > 4.0 else 'warning' if current_mtg > 2.5 else 'normal'
        }

    # 6. Household Debt Service Ratio
    dsr = fetch_fred_series("TDSP", api_key, "2015-01-01")
    if dsr is not None:
        current_dsr = dsr.iloc[-1]
        hist_avg = dsr.mean()
        metrics['Debt_Service_Ratio'] = {
            'value': current_dsr,
            'unit': '%',
            'hist_avg': hist_avg,
            'status': 'danger' if current_dsr > 14 else 'warning' if current_dsr > 12 else 'normal'
        }

    # 7. Real Personal Income Growth (YoY)
    rpi = fetch_fred_series("RPI", api_key, "2015-01-01")
    if rpi is not None:
        yoy_rpi = (rpi.iloc[-1] / rpi.iloc[-12] - 1) * 100 if len(rpi) > 12 else 0
        metrics['Real_Income_YoY'] = {
            'value': yoy_rpi,
            'unit': '%',
            'status': 'danger' if yoy_rpi < 0 else 'warning' if yoy_rpi < 2 else 'normal'
        }

    # 8. Consumer Sentiment
    sentiment = fetch_fred_series("UMCSENT", api_key, "2015-01-01")
    if sentiment is not None:
        current_sent = sentiment.iloc[-1]
        metrics['Consumer_Sentiment'] = {
            'value': current_sent,
            'unit': 'Index',
            'status': 'danger' if current_sent < 65 else 'warning' if current_sent < 80 else 'normal'
        }

    return metrics


def create_metric_card(ax, label, value, unit, sublabel=None, status='normal'):
    """Create a metric card with styling."""
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    # Background
    if status == 'danger':
        bg_color = '#FF333325'
        text_color = COLORS['down_red']
    elif status == 'warning':
        bg_color = '#FF672325'
        text_color = COLORS['dusk_orange']
    else:
        bg_color = '#00800025'
        text_color = COLORS['up_green']

    box = FancyBboxPatch((0.02, 0.02), 0.96, 0.96, boxstyle="round,pad=0.02",
                         facecolor=bg_color, edgecolor=text_color, linewidth=2)
    ax.add_patch(box)

    # Label
    ax.text(0.5, 0.85, label, ha='center', va='top',
            fontsize=9, fontweight='bold', color=COLORS['text_light'])

    # Value
    if isinstance(value, float):
        value_str = f'{value:.1f}'
    else:
        value_str = str(value)

    ax.text(0.5, 0.5, value_str, ha='center', va='center',
            fontsize=22, fontweight='bold', color=text_color)

    # Unit
    ax.text(0.5, 0.25, unit, ha='center', va='center',
            fontsize=9, color=COLORS['silvs_gray'])

    # Sublabel
    if sublabel:
        ax.text(0.5, 0.08, sublabel, ha='center', va='center',
                fontsize=7, color=COLORS['silvs_gray'], style='italic')


def generate_consumer_dashboard(save=True) -> plt.Figure:
    """
    Generate the Consumer Solvency Tracker Dashboard.
    """
    log.info("Generating Consumer Solvency Tracker Dashboard...")

    metrics = get_consumer_metrics()
    if not metrics:
        log.error("Could not fetch consumer metrics")
        return None

    fig = plt.figure(figsize=(14, 10))
    fig.patch.set_facecolor(COLORS['bg_dark'])

    # Title
    fig.suptitle('CONSUMER SOLVENCY TRACKER',
                 fontsize=18, fontweight='bold', color=COLORS['ocean_blue'],
                 y=0.97)

    fig.text(0.5, 0.93, f'Updated: {datetime.now().strftime("%Y-%m-%d")} | Monthly',
             ha='center', fontsize=10, color=COLORS['text_light'])

    gs = fig.add_gridspec(3, 4, hspace=0.25, wspace=0.15,
                          left=0.05, right=0.95, top=0.88, bottom=0.08)

    # Row 1: Savings, Credit Growth, DSR, Sentiment
    ax1 = fig.add_subplot(gs[0, 0])
    if 'Savings_Rate' in metrics:
        create_metric_card(ax1, 'Savings Rate', metrics['Savings_Rate']['value'],
                           metrics['Savings_Rate']['unit'],
                           sublabel=f"Hist Avg: {metrics['Savings_Rate']['hist_avg']:.1f}%",
                           status=metrics['Savings_Rate']['status'])

    ax2 = fig.add_subplot(gs[0, 1])
    if 'Credit_Growth_YoY' in metrics:
        create_metric_card(ax2, 'Credit Growth (YoY)', metrics['Credit_Growth_YoY']['value'],
                           metrics['Credit_Growth_YoY']['unit'],
                           status=metrics['Credit_Growth_YoY']['status'])

    ax3 = fig.add_subplot(gs[0, 2])
    if 'Debt_Service_Ratio' in metrics:
        create_metric_card(ax3, 'Debt Service Ratio', metrics['Debt_Service_Ratio']['value'],
                           metrics['Debt_Service_Ratio']['unit'],
                           sublabel=f"Hist Avg: {metrics['Debt_Service_Ratio']['hist_avg']:.1f}%",
                           status=metrics['Debt_Service_Ratio']['status'])

    ax4 = fig.add_subplot(gs[0, 3])
    if 'Consumer_Sentiment' in metrics:
        create_metric_card(ax4, 'Consumer Sentiment', metrics['Consumer_Sentiment']['value'],
                           metrics['Consumer_Sentiment']['unit'],
                           status=metrics['Consumer_Sentiment']['status'])

    # Row 2: Delinquencies
    ax5 = fig.add_subplot(gs[1, 0])
    if 'CC_Delinquency' in metrics:
        create_metric_card(ax5, 'Credit Card Delinq', metrics['CC_Delinquency']['value'],
                           metrics['CC_Delinquency']['unit'],
                           sublabel=f"Pre-COVID: {metrics['CC_Delinquency']['pre_covid']}%",
                           status=metrics['CC_Delinquency']['status'])

    ax6 = fig.add_subplot(gs[1, 1])
    if 'Auto_Delinquency' in metrics:
        create_metric_card(ax6, 'Auto Delinquency', metrics['Auto_Delinquency']['value'],
                           metrics['Auto_Delinquency']['unit'],
                           status=metrics['Auto_Delinquency']['status'])

    ax7 = fig.add_subplot(gs[1, 2])
    if 'Mortgage_Delinquency' in metrics:
        create_metric_card(ax7, 'Mortgage Delinq', metrics['Mortgage_Delinquency']['value'],
                           metrics['Mortgage_Delinquency']['unit'],
                           status=metrics['Mortgage_Delinquency']['status'])

    ax8 = fig.add_subplot(gs[1, 3])
    if 'Real_Income_YoY' in metrics:
        create_metric_card(ax8, 'Real Income (YoY)', metrics['Real_Income_YoY']['value'],
                           metrics['Real_Income_YoY']['unit'],
                           status=metrics['Real_Income_YoY']['status'])

    # Row 3: Summary Assessment
    ax_summary = fig.add_subplot(gs[2, :])
    ax_summary.axis('off')

    # Calculate overall consumer health score
    danger_count = sum(1 for m in metrics.values() if m.get('status') == 'danger')
    warning_count = sum(1 for m in metrics.values() if m.get('status') == 'warning')
    total = len(metrics)

    if danger_count >= 3:
        overall = "DISTRESSED"
        overall_color = COLORS['down_red']
        assessment = "Consumer balance sheets under significant stress.\nDelinquencies elevated, savings depleted."
    elif danger_count >= 1 or warning_count >= 4:
        overall = "STRAINED"
        overall_color = COLORS['dusk_orange']
        assessment = "Consumer stress building.\nLower-income households most vulnerable."
    else:
        overall = "STABLE"
        overall_color = COLORS['up_green']
        assessment = "Consumer balance sheets holding.\nMonitor for signs of deterioration."

    # Draw summary box
    box = FancyBboxPatch((0.1, 0.1), 0.8, 0.8, boxstyle="round,pad=0.02",
                         facecolor='none', edgecolor=overall_color, linewidth=3)
    ax_summary.add_patch(box)

    ax_summary.text(0.5, 0.7, f'CONSUMER HEALTH: {overall}',
                    ha='center', va='center', fontsize=16, fontweight='bold',
                    color=overall_color)

    ax_summary.text(0.5, 0.4, assessment,
                    ha='center', va='center', fontsize=11,
                    color=COLORS['text_light'], multialignment='center')

    score_text = f"Danger: {danger_count}/{total}  |  Warning: {warning_count}/{total}"
    ax_summary.text(0.5, 0.15, score_text,
                    ha='center', va='center', fontsize=9,
                    color=COLORS['silvs_gray'])

    # Watermark
    fig.text(0.5, 0.02, 'LIGHTHOUSE MACRO | MACRO, ILLUMINATED.',
             ha='center', fontsize=10, fontweight='bold',
             color=COLORS['ocean_blue'], alpha=0.6)

    if save:
        DASHBOARD_DIR.mkdir(parents=True, exist_ok=True)
        out_path = DASHBOARD_DIR / f"consumer_dashboard_{datetime.now().strftime('%Y%m%d')}.png"
        plt.savefig(out_path, dpi=200, facecolor=COLORS['bg_dark'], bbox_inches='tight')
        log.info(f"Saved: {out_path}")

        latest_path = DASHBOARD_DIR / "consumer_dashboard_latest.png"
        plt.savefig(latest_path, dpi=200, facecolor=COLORS['bg_dark'], bbox_inches='tight')

    return fig


def print_consumer_summary():
    """Print a text summary of consumer conditions."""
    metrics = get_consumer_metrics()
    if not metrics:
        print("Could not fetch consumer metrics")
        return

    print("\n" + "=" * 60)
    print("CONSUMER SOLVENCY TRACKER - SUMMARY")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d')} | Monthly Update")
    print("-" * 60)

    for name, data in metrics.items():
        status_icon = "  " if data['status'] == 'normal' else "!!" if data['status'] == 'danger' else "! "
        print(f"{status_icon} {name:20} : {data['value']:>10.2f} {data['unit']:<8} [{data['status'].upper()}]")

    print("=" * 60 + "\n")


if __name__ == "__main__":
    print_consumer_summary()
    fig = generate_consumer_dashboard()
    if fig:
        plt.show()
