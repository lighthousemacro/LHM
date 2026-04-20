"""
Fig 11 — ADP Employment by Firm Size (March 2026 YoY)
Fig 11c — December 2025 vs March 2026 YoY by firm size (2-panel)

Used for Bob's Monday Beacon (Apr 20, 2026).

Data: ADP National Employment Report by Establishment Size (NER_SA)
Source CSV: /tmp/two_econ_data/ADP_NER_history.csv
Vintage: 20260401 (data through March 2026)

Bucket definitions match /Users/bob/LHM/Scripts/chart_generation/two_economies_charts.py:
    Small  = 1-19 + 20-49 employees
    Medium = 50-249 + 250-499 employees
    Large  = 500+ employees
"""
import sys
sys.path.insert(0, '/Users/bob/LHM/Scripts/chart_generation')

import pandas as pd
import matplotlib.pyplot as plt

from lhm_chart_template import (
    COLORS, set_theme, new_fig, new_fig_multi,
    style_single_ax, add_annotation_box,
    save_fig, brand_fig,
)

set_theme('white')

OUTDIR = '/Users/bob/LHM/Outputs/charts/two_economies'
ADP_CSV = '/tmp/two_econ_data/ADP_NER_history.csv'
VINTAGE = '20260401'

OCEAN = COLORS['ocean']
DUSK = COLORS['dusk']
DOLDRUMS = COLORS['doldrums']
STARBOARD = COLORS['starboard']
PORT = COLORS['port']
FOG = COLORS['fog']

SIZE_MAP = {
    'Small\n(1-49)':    ['1-19 employees', '20-49 employees'],
    'Medium\n(50-499)': ['50-249 employees', '250-499 employees'],
    'Large\n(500+)':    ['500+ employees'],
}


def _load_buckets():
    df = pd.read_csv(ADP_CSV)
    df['date'] = pd.to_datetime(df['date'])
    df = df[(df['timestep'] == 'M') & (df['agg_RIS'] == 'Establishment Size')].copy()
    buckets = {}
    for label, cats in SIZE_MAP.items():
        s = df[df['category'].isin(cats)].groupby('date')['NER_SA'].sum().sort_index()
        buckets[label] = s
    return buckets


def _yoy(series, ref_date):
    ref = pd.Timestamp(ref_date)
    prior = ref - pd.DateOffset(years=1)
    return (series.loc[ref] / series.loc[prior] - 1) * 100


def _bar_color(v, near_zero=0.2):
    if v > near_zero:
        return STARBOARD
    if v < -near_zero:
        return PORT
    return DOLDRUMS


# =========================================================
# FIG 11 — March 2026 YoY by firm size (primary chart)
# =========================================================
def fig11_march2026_yoy():
    buckets = _load_buckets()
    ref_date = '2026-03-01'

    categories = list(buckets.keys())
    values = [_yoy(buckets[c], ref_date) for c in categories]
    colors = [_bar_color(v) for v in values]

    fig, ax = new_fig(figsize=(14, 7))
    bars = ax.bar(categories, values, color=colors, width=0.50,
                  edgecolor='white', linewidth=1.0)
    for bar, v, c in zip(bars, values, colors):
        offset = 0.08 if v > 0 else -0.08
        va = 'bottom' if v > 0 else 'top'
        ax.text(bar.get_x() + bar.get_width()/2, v + offset,
                f'{v:+.2f}%', ha='center', va=va,
                fontsize=13, fontweight='bold', color=c)

    ax.axhline(0, color=FOG, linestyle='--', linewidth=1.0, zorder=0)
    ax.set_ylabel('YoY Change (%)', fontsize=10, color=DOLDRUMS)

    ymin = min(values + [0]) - 0.6
    ymax = max(values + [0]) + 0.6
    ax.set_ylim(ymin, ymax)
    style_single_ax(ax, fmt='{:+.2f}%')

    add_annotation_box(
        ax,
        'Composition has flipped since January.\nSmall firms back to growth, medium firms still shedding.',
        x=0.50, y=0.92
    )

    brand_fig(
        fig,
        title='Job Creation by Firm Size (ADP March 2026)',
        subtitle='Composition has flipped since January: large firms decelerating',
        source=f'ADP National Employment Report (NER_SA, vintage {VINTAGE})',
        data_date='2026-03-01'
    )
    out = f'{OUTDIR}/fig11_adp_firm_size_march2026.png'
    save_fig(fig, out)
    print(f'  [A] {out}')
    return out


# =========================================================
# FIG 11C — Dec 2025 vs Mar 2026 YoY (2-panel)
# =========================================================
def fig11c_dec25_vs_mar26():
    buckets = _load_buckets()
    categories = list(buckets.keys())

    dec25 = [_yoy(buckets[c], '2025-12-01') for c in categories]
    mar26 = [_yoy(buckets[c], '2026-03-01') for c in categories]

    fig, axes = new_fig_multi(1, 2, figsize=(15, 7))

    for ax, values, label in zip(axes, [dec25, mar26],
                                  ['December 2025', 'March 2026']):
        colors = [_bar_color(v) for v in values]
        bars = ax.bar(categories, values, color=colors, width=0.55,
                      edgecolor='white', linewidth=1.0)
        for bar, v, c in zip(bars, values, colors):
            offset = 0.08 if v > 0 else -0.08
            va = 'bottom' if v > 0 else 'top'
            ax.text(bar.get_x() + bar.get_width()/2, v + offset,
                    f'{v:+.2f}%', ha='center', va=va,
                    fontsize=12, fontweight='bold', color=c)
        ax.axhline(0, color=FOG, linestyle='--', linewidth=1.0, zorder=0)
        ax.set_title(label, fontsize=12, fontweight='bold', color=DOLDRUMS, pad=8)
        ax.set_ylabel('YoY Change (%)', fontsize=10, color=DOLDRUMS)
        style_single_ax(ax, fmt='{:+.2f}%')

    # Match y-axis across panels for easy visual compare
    all_vals = dec25 + mar26
    ymin = min(all_vals + [0]) - 0.6
    ymax = max(all_vals + [0]) + 0.6
    for ax in axes:
        ax.set_ylim(ymin, ymax)

    brand_fig(
        fig,
        title='Firm-Size Employment: Composition Shift',
        subtitle='December 2025 vs March 2026 YoY (current ADP vintage)',
        source=f'ADP National Employment Report (NER_SA, vintage {VINTAGE})',
        data_date='2026-03-01'
    )
    out = f'{OUTDIR}/fig11c_adp_december_vs_march.png'
    save_fig(fig, out)
    print(f'  [C] {out}')
    return out


if __name__ == '__main__':
    print('Generating ADP firm-size charts for Monday Beacon...')
    fig11_march2026_yoy()
    fig11c_dec25_vs_mar26()
    print('Done.')
