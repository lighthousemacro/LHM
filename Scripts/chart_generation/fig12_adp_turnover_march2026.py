"""
Fig 12 — ADP Small-Employer Turnover (March 2026, 9-year low)

Data source: ADP Research Institute, "What small employers are telling us about
the labor market", April 14, 2026 (Nela Richardson).
  https://www.adpresearch.com/main-street-macro/...

Figures reported in that post:
  - Last ~3 years, all private employers: turnover ~4.7% (baseline)
  - March 2026 print at small employers (<50): 3.9% — lowest in 9 years of tracking

No time series is publicly available. This chart presents the two anchor
values side-by-side with clear attribution.
"""
import sys
sys.path.insert(0, '/Users/bob/LHM/Scripts/chart_generation')

import numpy as np

from lhm_chart_template import (
    COLORS, set_theme, new_fig,
    style_single_ax, add_annotation_box,
    save_fig, brand_fig,
)

set_theme('white')

OUTDIR = '/Users/bob/LHM/Outputs/charts/two_economies'

OCEAN = COLORS['ocean']
DUSK = COLORS['dusk']
DOLDRUMS = COLORS['doldrums']
PORT = COLORS['port']
FOG = COLORS['fog']


def fig12_turnover():
    categories = [
        'All Private Employers (3-yr avg)',
        'Small Employers (<50), March 2026',
    ]
    values = [4.7, 3.9]
    colors = [DOLDRUMS, OCEAN]

    fig, ax = new_fig(figsize=(14, 7))

    bars = ax.bar(categories, values, color=colors, width=0.50,
                  edgecolor='white', linewidth=1.0)

    for bar, v, c in zip(bars, values, colors):
        ax.text(bar.get_x() + bar.get_width() / 2, v + 0.08,
                f'{v:.1f}%', ha='center', va='bottom',
                fontsize=14, fontweight='bold', color=c)

    # Delta callout between the bars
    delta = values[0] - values[1]
    ax.text(0.5, values[1] + (values[0] - values[1]) / 2,
            f'−{delta:.1f} pp', ha='center', va='center',
            fontsize=11, fontweight='bold', color=PORT, style='italic')

    ax.axhline(values[0], color=FOG, linestyle='--', linewidth=1.0, zorder=0)
    ax.set_ylabel('Monthly Turnover Rate (%)', fontsize=10, color=DOLDRUMS)
    ax.set_ylim(0, max(values) * 1.35)
    style_single_ax(ax, fmt='{:.1f}%')
    ax.tick_params(axis='x', which='both', length=0)

    add_annotation_box(
        ax,
        "Small-employer turnover at 3.9% — a 9-year low.\n"
        "Workers stopped quitting. The labor market froze.",
    )

    brand_fig(
        fig,
        title='Small-Employer Turnover: A 9-Year Low',
        subtitle='Monthly separations as a % of prior-month active employees',
        source='ADP Research Institute / Main Street Macro (N. Richardson, April 14, 2026)',
        data_date='2026-03-31',
    )
    out = f'{OUTDIR}/fig12_adp_turnover_march2026.png'
    save_fig(fig, out)
    print(f'  [12] {out}')
    return out


if __name__ == '__main__':
    fig12_turnover()
