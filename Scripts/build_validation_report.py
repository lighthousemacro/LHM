"""
Build the LHM Validation Report PDF.

Renders branded charts of OOS IC per pillar + walk-forward stability,
assembles into a single PDF using matplotlib's PdfPages.
"""
import os
import sys
import json
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

sys.path.insert(0, '/Users/bob/LHM/Scripts/chart_generation')
from lhm_chart_template import (COLORS, set_theme, new_fig, style_single_ax,
                                 style_ax, brand_fig, save_fig,
                                 add_annotation_box, set_xlim_to_data,
                                 add_last_value_label)

VAL_DIR = '/Users/bob/LHM/Outputs/validation'
OUT_PDF = '/Users/bob/LHM/Outputs/VALIDATION_REPORT.pdf'

PILLAR_NAMES = {
    1: 'Labor', 2: 'Prices', 3: 'Growth', 4: 'Housing', 5: 'Consumer',
    6: 'Business', 7: 'Trade', 8: 'Government', 9: 'Financial',
    10: 'Plumbing', 11: 'Structure',
}


def load_summary():
    with open(f'{VAL_DIR}/all_pillars_summary.json') as f:
        return {int(k): v for k, v in json.load(f).items()}


def load_pillar_detail(pid):
    path = f'{VAL_DIR}/pillar_{pid:02d}_validation.json'
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)


def fig_summary_bar(summary):
    """Page 1: per-pillar OOS IC with significance bars."""
    set_theme('white')
    fig, ax = new_fig(figsize=(14, 8))
    pids = sorted(summary.keys())
    ics = [summary[p]['oos_ic'] for p in pids]
    ts = [summary[p]['t_stat'] for p in pids]
    benches = [summary[p]['benchmark'] for p in pids]
    labels = [f'P{p} {PILLAR_NAMES[p]}\n(vs {b})' for p, b in zip(pids, benches)]

    colors = []
    for ic, t in zip(ics, ts):
        if abs(t) >= 2.0:
            colors.append(COLORS['ocean'] if ic > 0 else COLORS['port'])
        elif abs(t) >= 1.5:
            colors.append(COLORS['sky'] if ic > 0 else COLORS['dusk'])
        else:
            colors.append(COLORS['doldrums'])

    bars = ax.bar(labels, ics, color=colors, zorder=3, edgecolor='white', linewidth=0.5)

    for bar, ic, t in zip(bars, ics, ts):
        y = bar.get_height()
        offset = 0.015 if y >= 0 else -0.015
        va = 'bottom' if y >= 0 else 'top'
        ax.text(bar.get_x() + bar.get_width()/2, y + offset,
                f'{ic:+.3f}\nt={t:+.2f}', ha='center', va=va,
                fontsize=9, fontweight='bold',
                color=COLORS['ocean'] if abs(t) >= 2 else COLORS['doldrums'])

    ax.axhline(0, color=COLORS['fog'], linestyle='-', linewidth=0.8, zorder=1)
    style_single_ax(ax, fmt='{:+.2f}')
    ax.tick_params(axis='x', labelsize=9, rotation=0)
    ax.set_ylabel('Out-of-Sample IC')
    ax.set_ylim(min(ics) - 0.10, max(ics) + 0.15)

    add_annotation_box(ax,
        '|t| ≥ 2.0 = statistically significant. Three pillars (Prices, Housing, Government) clear that bar.',
        x=0.50, y=0.96)

    brand_fig(fig,
        title='Pillar Validation: walk-forward 63d-forward IC vs benchmark',
        subtitle='Out-of-sample IC across rolling 5y train / 1y test windows',
        source='Lighthouse Macro Validation Engine',
        data_date=datetime.now())
    return fig


def fig_pillar_detail(pid, detail):
    """One page per pillar: walk-forward IC trajectory + weight stability."""
    set_theme('white')
    fig = plt.figure(figsize=(14, 8))
    fig.patch.set_facecolor('white')
    fig.subplots_adjust(top=0.85, bottom=0.10, left=0.07, right=0.93,
                        hspace=0.35)

    ax_ic = fig.add_subplot(2, 1, 1)
    ax_w = fig.add_subplot(2, 1, 2)
    ax_ic.set_facecolor('white')
    ax_w.set_facecolor('white')

    windows = detail['windows']
    test_ends = [w['test_end'] for w in windows]
    oos = [w['oos_ic'] for w in windows]
    train = [w['train_ic'] for w in windows]

    x = np.arange(len(test_ends))
    ax_ic.bar(x - 0.2, train, 0.4, color=COLORS['sky'], label='In-sample IC', alpha=0.7)
    ax_ic.bar(x + 0.2, [v if v is not None else 0 for v in oos], 0.4,
              color=COLORS['ocean'], label='OOS IC')
    ax_ic.axhline(0, color=COLORS['fog'], linestyle='-', linewidth=0.8, zorder=1)
    ax_ic.set_xticks(x)
    ax_ic.set_xticklabels([t[:7] for t in test_ends], rotation=45, ha='right', fontsize=8)
    ax_ic.set_ylabel('IC')
    style_ax(ax_ic)
    ax_ic.legend(loc='lower left', fontsize=9, framealpha=0.95)

    weights_arr = np.array([w['weights'] for w in windows])
    series_ids = list(detail['empirical_weights'].keys())
    palette = [COLORS['ocean'], COLORS['dusk'], COLORS['sky'], COLORS['sea'],
               COLORS['venus'], COLORS['starboard'], COLORS['port'],
               COLORS['doldrums'], '#3a4a5e', '#88aabb']
    for i, sid in enumerate(series_ids):
        if i >= weights_arr.shape[1]:
            break
        ax_w.plot(x, weights_arr[:, i], color=palette[i % len(palette)],
                  linewidth=1.6, label=sid[:18], alpha=0.85)
    ax_w.set_xticks(x)
    ax_w.set_xticklabels([t[:7] for t in test_ends], rotation=45, ha='right', fontsize=8)
    ax_w.set_ylabel('Component Weight')
    style_ax(ax_w)
    ax_w.legend(loc='upper right', fontsize=7, ncol=2, framealpha=0.95)
    ax_w.set_ylim(-0.02, 0.55)

    name = PILLAR_NAMES.get(pid, f'Pillar {pid}')
    bench = detail['benchmark']
    title = f'Pillar {pid}: {name} (vs {bench})'
    subtitle = (f'OOS IC mean: {detail["oos_ic_mean"]:+.3f} | t-stat: {detail["oos_ic_t_stat"]:+.2f} | '
                f'{detail["n_windows"]} walk-forward windows')

    brand_fig(fig, title=title, subtitle=subtitle,
              source='Lighthouse Macro Validation Engine',
              data_date=datetime.now())
    return fig


def fig_methodology():
    """Methodology + interpretation page."""
    set_theme('white')
    fig, ax = new_fig(figsize=(14, 9))
    ax.axis('off')

    text = r"""METHODOLOGY

Walk-forward weight optimization across each pillar's top descriptive series.

Window structure:
  Train: rolling 5-year window
  Test : 1-year out-of-sample
  Roll : 1-year increments

Composite construction:
  $\mathrm{Composite}_t = \sum_i w_i \cdot z_{i,t}$
  where $z_{i,t}$ = 252-day rolling z-score of series $i$ at time $t$

Optimization objective:
  $\min_w \; -\rho_{Spearman}(\mathrm{Composite}_t, r^{63d}_{t+1})$
  subject to $\sum_i w_i = 1$, $0 \leq w_i \leq 0.5$

Forward return:
  $r^{63d}_{t+1} = \log(P_{t+63} / P_t)$ for the pillar's benchmark asset

Validation metrics:
  OOS IC: mean rank correlation across all out-of-sample windows
  t-stat: $\bar{IC} / (\sigma_{IC} / \sqrt{n})$
  Significance: $|t| \geq 2.0$ at the 95% confidence level

INTERPRETATION

Statistically significant pillars carry directional information for forward
returns of their benchmark over the 63-day horizon. Negative IC for a
risk pillar is not a weakness; it is the expected sign for a stress
indicator (high z = stress = lower forward returns).

Insignificant pillars at this horizon-benchmark pair may carry signal at
different horizons (Labor at 6-12mo) or against different benchmarks
(Plumbing against liquidity-sensitive assets). Future work expands the
horizon-benchmark grid."""

    ax.text(0.02, 0.96, text, transform=ax.transAxes,
            fontsize=10, fontfamily='serif', va='top', ha='left',
            color='#1a1a1a')

    brand_fig(fig,
        title='Validation Engine Methodology',
        subtitle='Walk-forward optimization of pillar composite weights',
        source='Lighthouse Macro',
        data_date=datetime.now())
    return fig


def main():
    summary = load_summary()
    with PdfPages(OUT_PDF) as pdf:
        pdf.savefig(fig_methodology(), bbox_inches='tight')
        plt.close()

        pdf.savefig(fig_summary_bar(summary), bbox_inches='tight')
        plt.close()

        for pid in sorted(summary.keys()):
            detail = load_pillar_detail(pid)
            if detail and detail.get('windows'):
                pdf.savefig(fig_pillar_detail(pid, detail), bbox_inches='tight')
                plt.close()

        info = pdf.infodict()
        info['Title'] = 'LHM Pillar Validation Report'
        info['Author'] = 'Lighthouse Macro'
        info['CreationDate'] = datetime.now()

    print(f'Saved: {OUT_PDF}')


if __name__ == '__main__':
    main()
