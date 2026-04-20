"""
Labor Health Monitor Dashboard - Weekly Update
Lighthouse Macro - January 2026

Components:
- LFI (Labor Fragility Index)
- Employment Diffusion Index
- Quits Rate
- Initial Claims
- Hours Worked
- Long-Term Unemployment Share

Update Frequency: Weekly (Thursdays after claims)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from datetime import datetime
from pathlib import Path

from ..config import CONFIG
from ..collect.fred_extended import fetch_fred_series
from ..features.transforms_core import zscore
from ..utils.logging import get_logger
from ..utils.io import read_parquet

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

DASHBOARD_DIR = CONFIG.base_dir / "dashboards" / "labor"


def get_labor_metrics() -> dict:
    """
    Fetch and compute all labor metrics for the dashboard.
    """
    api_key = CONFIG.fred_api_key
    if not api_key:
        log.error("FRED_API_KEY missing")
        return {}

    metrics = {}

    # 1. Quits Rate (JOLTS)
    quits = fetch_fred_series("JTSQUR", api_key, "2015-01-01")
    if quits is not None:
        current_quits = quits.iloc[-1]
        # Pre-COVID average was ~2.3%
        metrics['Quits_Rate'] = {
            'value': current_quits,
            'unit': '%',
            'pre_covid_avg': 2.3,
            'status': 'danger' if current_quits < 1.8 else 'warning' if current_quits < 2.1 else 'normal'
        }

    # 2. Hires Rate
    hires = fetch_fred_series("JTSHIR", api_key, "2015-01-01")
    if hires is not None:
        current_hires = hires.iloc[-1]
        metrics['Hires_Rate'] = {
            'value': current_hires,
            'unit': '%',
            'status': 'danger' if current_hires < 3.5 else 'warning' if current_hires < 3.8 else 'normal'
        }

    # 3. Initial Claims
    claims = fetch_fred_series("ICSA", api_key, "2020-01-01")
    if claims is not None:
        current_claims = claims.iloc[-1] / 1000  # Convert to thousands
        four_wk_avg = claims.tail(4).mean() / 1000
        metrics['Initial_Claims'] = {
            'value': current_claims,
            'avg_4w': four_wk_avg,
            'unit': 'K',
            'status': 'danger' if current_claims > 300 else 'warning' if current_claims > 250 else 'normal'
        }

    # 4. Continuing Claims
    cont_claims = fetch_fred_series("CCSA", api_key, "2020-01-01")
    if cont_claims is not None:
        current_cont = cont_claims.iloc[-1] / 1e6  # Convert to millions
        metrics['Continuing_Claims'] = {
            'value': current_cont,
            'unit': 'M',
            'status': 'danger' if current_cont > 2.0 else 'warning' if current_cont > 1.8 else 'normal'
        }

    # 5. Long-Term Unemployment Share
    lt_unemp = fetch_fred_series("UEMP27OV", api_key, "2015-01-01")
    total_unemp = fetch_fred_series("UNEMPLOY", api_key, "2015-01-01")
    if lt_unemp is not None and total_unemp is not None:
        df = pd.DataFrame({'LT': lt_unemp, 'Total': total_unemp})
        df = df.resample('D').ffill().dropna()
        if not df.empty:
            lt_share = (df['LT'] / df['Total'] * 100).iloc[-1]
            metrics['LT_Unemp_Share'] = {
                'value': lt_share,
                'unit': '%',
                'status': 'danger' if lt_share > 25 else 'warning' if lt_share > 20 else 'normal'
            }

    # 6. Average Weekly Hours (Manufacturing)
    hours = fetch_fred_series("AWHMAN", api_key, "2015-01-01")
    if hours is not None:
        current_hours = hours.iloc[-1]
        metrics['Avg_Hours_Mfg'] = {
            'value': current_hours,
            'unit': 'hrs',
            'status': 'danger' if current_hours < 39.5 else 'warning' if current_hours < 40.0 else 'normal'
        }

    # 7. Employment Diffusion (proxy from ADP or private payrolls momentum)
    payrolls = fetch_fred_series("PAYEMS", api_key, "2015-01-01")
    if payrolls is not None:
        mom_change = payrolls.diff(1).iloc[-1]  # Month-over-month change in thousands
        metrics['Payroll_MoM'] = {
            'value': mom_change,
            'unit': 'K',
            'status': 'danger' if mom_change < 50 else 'warning' if mom_change < 100 else 'normal'
        }

    # 8. Compute LFI (Labor Fragility Index)
    if quits is not None and hires is not None and lt_unemp is not None and total_unemp is not None:
        # Merge all series
        df = pd.DataFrame({
            'Quits': quits,
            'Hires': fetch_fred_series("JTSHIL", api_key, "2015-01-01"),
            'Quits_Level': fetch_fred_series("JTSQUL", api_key, "2015-01-01"),
            'LT_Unemp': lt_unemp,
            'Total_Unemp': total_unemp,
        })
        df = df.resample('D').ffill().dropna()

        if not df.empty:
            # LFI = avg(z(LT_share), z(-quits), z(-hires/quits))
            lt_share = df['LT_Unemp'] / df['Total_Unemp']
            hires_quits = df['Hires'] / df['Quits_Level'].replace(0, np.nan)

            z_lt = zscore(lt_share)
            z_quits = zscore(-df['Quits'])  # Inverted: lower quits = higher fragility
            z_hq = zscore(-hires_quits)  # Inverted: lower ratio = higher fragility

            lfi = (z_lt + z_quits + z_hq) / 3
            current_lfi = lfi.iloc[-1]

            metrics['LFI'] = {
                'value': current_lfi,
                'unit': 'z-score',
                'status': 'danger' if current_lfi > 0.5 else 'warning' if current_lfi > 0 else 'normal'
            }

    return metrics


def create_metric_panel(ax, label, value, unit, change=None, status='normal', sublabel=None):
    """Create a metric panel with value and status."""
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    # Background color based on status
    if status == 'danger':
        bg_color = '#FF333330'
        text_color = COLORS['down_red']
    elif status == 'warning':
        bg_color = '#FF672330'
        text_color = COLORS['dusk_orange']
    else:
        bg_color = '#00800030'
        text_color = COLORS['up_green']

    box = FancyBboxPatch((0.02, 0.02), 0.96, 0.96, boxstyle="round,pad=0.02",
                         facecolor=bg_color, edgecolor=text_color, linewidth=2)
    ax.add_patch(box)

    # Label
    ax.text(0.5, 0.88, label, ha='center', va='top',
            fontsize=9, fontweight='bold', color=COLORS['text_light'])

    # Value
    if isinstance(value, float):
        value_str = f'{value:.2f}' if abs(value) < 10 else f'{value:.1f}'
    else:
        value_str = str(value)

    ax.text(0.5, 0.5, value_str, ha='center', va='center',
            fontsize=20, fontweight='bold', color=text_color)

    # Unit
    ax.text(0.5, 0.25, unit, ha='center', va='center',
            fontsize=9, color=COLORS['silvs_gray'])

    # Sublabel if provided
    if sublabel:
        ax.text(0.5, 0.1, sublabel, ha='center', va='center',
                fontsize=7, color=COLORS['silvs_gray'], style='italic')


def create_trend_arrow(ax, direction='flat'):
    """Create a trend arrow indicator."""
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    if direction == 'up':
        ax.annotate('', xy=(0.5, 0.8), xytext=(0.5, 0.2),
                    arrowprops=dict(arrowstyle='->', color=COLORS['down_red'], lw=3))
    elif direction == 'down':
        ax.annotate('', xy=(0.5, 0.2), xytext=(0.5, 0.8),
                    arrowprops=dict(arrowstyle='->', color=COLORS['up_green'], lw=3))
    else:
        ax.plot([0.2, 0.8], [0.5, 0.5], color=COLORS['silvs_gray'], lw=3)


def generate_labor_dashboard(save=True) -> plt.Figure:
    """
    Generate the Labor Health Monitor Dashboard.
    """
    log.info("Generating Labor Health Monitor Dashboard...")

    metrics = get_labor_metrics()
    if not metrics:
        log.error("Could not fetch labor metrics")
        return None

    fig = plt.figure(figsize=(14, 10))
    fig.patch.set_facecolor(COLORS['bg_dark'])

    # Title
    fig.suptitle('LABOR HEALTH MONITOR',
                 fontsize=18, fontweight='bold', color=COLORS['ocean_blue'],
                 y=0.97)

    fig.text(0.5, 0.93, f'Updated: {datetime.now().strftime("%Y-%m-%d")} | Weekly',
             ha='center', fontsize=10, color=COLORS['text_light'])

    gs = fig.add_gridspec(3, 4, hspace=0.25, wspace=0.15,
                          left=0.05, right=0.95, top=0.88, bottom=0.08)

    # Row 1: LFI (main gauge) + Status
    ax_lfi = fig.add_subplot(gs[0, 0:2])
    if 'LFI' in metrics:
        create_metric_panel(ax_lfi, 'Labor Fragility Index (LFI)',
                            metrics['LFI']['value'], metrics['LFI']['unit'],
                            status=metrics['LFI']['status'],
                            sublabel='High = Structural Weakness')

    # Claims box
    ax_claims = fig.add_subplot(gs[0, 2])
    if 'Initial_Claims' in metrics:
        create_metric_panel(ax_claims, 'Initial Claims',
                            metrics['Initial_Claims']['value'],
                            metrics['Initial_Claims']['unit'],
                            status=metrics['Initial_Claims']['status'],
                            sublabel=f"4W Avg: {metrics['Initial_Claims']['avg_4w']:.0f}K")

    ax_cont = fig.add_subplot(gs[0, 3])
    if 'Continuing_Claims' in metrics:
        create_metric_panel(ax_cont, 'Continuing Claims',
                            metrics['Continuing_Claims']['value'],
                            metrics['Continuing_Claims']['unit'],
                            status=metrics['Continuing_Claims']['status'])

    # Row 2: JOLTS metrics
    ax_quits = fig.add_subplot(gs[1, 0])
    if 'Quits_Rate' in metrics:
        create_metric_panel(ax_quits, 'Quits Rate',
                            metrics['Quits_Rate']['value'],
                            metrics['Quits_Rate']['unit'],
                            status=metrics['Quits_Rate']['status'],
                            sublabel=f"Pre-COVID: {metrics['Quits_Rate']['pre_covid_avg']}%")

    ax_hires = fig.add_subplot(gs[1, 1])
    if 'Hires_Rate' in metrics:
        create_metric_panel(ax_hires, 'Hires Rate',
                            metrics['Hires_Rate']['value'],
                            metrics['Hires_Rate']['unit'],
                            status=metrics['Hires_Rate']['status'])

    ax_lt = fig.add_subplot(gs[1, 2])
    if 'LT_Unemp_Share' in metrics:
        create_metric_panel(ax_lt, 'Long-Term Unemp Share',
                            metrics['LT_Unemp_Share']['value'],
                            metrics['LT_Unemp_Share']['unit'],
                            status=metrics['LT_Unemp_Share']['status'],
                            sublabel='27+ Weeks')

    ax_hours = fig.add_subplot(gs[1, 3])
    if 'Avg_Hours_Mfg' in metrics:
        create_metric_panel(ax_hours, 'Avg Hours (Mfg)',
                            metrics['Avg_Hours_Mfg']['value'],
                            metrics['Avg_Hours_Mfg']['unit'],
                            status=metrics['Avg_Hours_Mfg']['status'])

    # Row 3: Payrolls + Summary
    ax_payroll = fig.add_subplot(gs[2, 0:2])
    if 'Payroll_MoM' in metrics:
        create_metric_panel(ax_payroll, 'Payroll Change (MoM)',
                            metrics['Payroll_MoM']['value'],
                            metrics['Payroll_MoM']['unit'],
                            status=metrics['Payroll_MoM']['status'],
                            sublabel='Thousands')

    # Overall assessment
    ax_summary = fig.add_subplot(gs[2, 2:4])
    ax_summary.axis('off')

    # Determine overall labor health
    danger_count = sum(1 for m in metrics.values() if m.get('status') == 'danger')
    warning_count = sum(1 for m in metrics.values() if m.get('status') == 'warning')

    if danger_count >= 2:
        overall = "DETERIORATING"
        overall_color = COLORS['down_red']
        assessment = "Multiple labor metrics showing stress.\nMonitor for recession signals."
    elif danger_count >= 1 or warning_count >= 3:
        overall = "SOFTENING"
        overall_color = COLORS['dusk_orange']
        assessment = "Labor market cooling.\nWatch for acceleration."
    else:
        overall = "HEALTHY"
        overall_color = COLORS['up_green']
        assessment = "Labor conditions remain solid.\nNo immediate concerns."

    ax_summary.text(0.5, 0.7, f'ASSESSMENT: {overall}',
                    ha='center', va='center', fontsize=14, fontweight='bold',
                    color=overall_color)
    ax_summary.text(0.5, 0.35, assessment,
                    ha='center', va='center', fontsize=10,
                    color=COLORS['text_light'], multialignment='center')

    # Watermark
    fig.text(0.5, 0.02, 'LIGHTHOUSE MACRO | MACRO, ILLUMINATED.',
             ha='center', fontsize=10, fontweight='bold',
             color=COLORS['ocean_blue'], alpha=0.6)

    if save:
        DASHBOARD_DIR.mkdir(parents=True, exist_ok=True)
        out_path = DASHBOARD_DIR / f"labor_dashboard_{datetime.now().strftime('%Y%m%d')}.png"
        plt.savefig(out_path, dpi=200, facecolor=COLORS['bg_dark'], bbox_inches='tight')
        log.info(f"Saved: {out_path}")

        latest_path = DASHBOARD_DIR / "labor_dashboard_latest.png"
        plt.savefig(latest_path, dpi=200, facecolor=COLORS['bg_dark'], bbox_inches='tight')

    return fig


def print_labor_summary():
    """Print a text summary of labor conditions."""
    metrics = get_labor_metrics()
    if not metrics:
        print("Could not fetch labor metrics")
        return

    print("\n" + "=" * 60)
    print("LABOR HEALTH MONITOR - SUMMARY")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d')} | Weekly Update")
    print("-" * 60)

    for name, data in metrics.items():
        status_icon = "  " if data['status'] == 'normal' else "!!" if data['status'] == 'danger' else "! "
        print(f"{status_icon} {name:20} : {data['value']:>10.2f} {data['unit']:<8} [{data['status'].upper()}]")

    print("=" * 60 + "\n")


if __name__ == "__main__":
    print_labor_summary()
    fig = generate_labor_dashboard()
    if fig:
        plt.show()
