#!/usr/bin/env python3
"""
Build branded charts for the email summary.
"""

import json
import sqlite3
import sys
import warnings
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd

warnings.filterwarnings('ignore')

sys.path.insert(0, '/Users/bob/LHM/Scripts/backtest')
from pillar_weight_optimization import (
    DB_PATH, PILLAR_SPECS, build_components,
)
from pillar_spread_optimization import build_spread_target

OUTPUT = Path("/Users/bob/LHM/Outputs/mri_optimization/email_charts")
OUTPUT.mkdir(exist_ok=True, parents=True)

# Brand
OCEAN = '#2389BB'
DUSK = '#FF6723'
SKY = '#23BBFF'
SEA = '#00BB89'
VENUS = '#FF2389'
DOLDRUMS = '#898989'
PORT = '#892323'
STARBOARD = '#238923'

plt.rcParams.update({
    'font.family': 'Inter',
    'axes.spines.top': True,
    'axes.spines.right': True,
    'axes.spines.bottom': True,
    'axes.spines.left': True,
    'axes.edgecolor': DOLDRUMS,
    'axes.linewidth': 0.5,
    'axes.grid': False,
    'xtick.color': DOLDRUMS,
    'ytick.color': DOLDRUMS,
    'figure.facecolor': 'white',
    'axes.facecolor': 'white',
})


def style_ax(ax):
    ax.tick_params(left=False, bottom=False, right=False, top=False)
    for spine in ax.spines.values():
        spine.set_linewidth(0.5)
        spine.set_color(DOLDRUMS)


def add_brand(fig, ax, title, subtitle, source):
    fig.text(0.06, 0.96, "LIGHTHOUSE MACRO",
             fontsize=10, fontweight='bold', color=OCEAN,
             family='Montserrat')
    fig.text(0.06, 0.93, title, fontsize=15, fontweight='bold', color='#1A1A1A',
             family='Montserrat')
    fig.text(0.06, 0.905, subtitle, fontsize=10, color=DOLDRUMS, family='Inter')
    # Accent bar
    ax_bar = fig.add_axes([0.06, 0.882, 0.88, 0.006])
    ax_bar.axhspan(0, 1, xmin=0, xmax=0.66, color=OCEAN)
    ax_bar.axhspan(0, 1, xmin=0.66, xmax=1.0, color=DUSK)
    ax_bar.set_xticks([]); ax_bar.set_yticks([])
    for s in ax_bar.spines.values(): s.set_visible(False)
    fig.text(0.06, 0.04, source, fontsize=8, color=DOLDRUMS, style='italic')
    fig.text(0.94, 0.04, "MACRO, ILLUMINATED.",
             fontsize=8, fontweight='bold', color=OCEAN, ha='right',
             family='Montserrat', alpha=0.6)


def expanding_z(s, min_p=63, w=3.0):
    m = s.expanding(min_periods=min_p).mean()
    sd = s.expanding(min_periods=min_p).std()
    z = (s - m) / sd.replace(0, np.nan)
    return z.clip(-w, w)


def chart_pillar_vs_target(conn, pillar, target_series, target_h, target_mode,
                            target_label, output_name, weights=None,
                            chart_title="", chart_subtitle=""):
    """Generic: composite pillar z-score vs forward target."""
    spec = PILLAR_SPECS[pillar]
    z_comp, _ = build_components(conn, spec)
    if weights is None:
        weights = {c: 1.0 / len(z_comp.columns) for c in z_comp.columns}
    composite = (z_comp * pd.Series(weights)).sum(axis=1)

    # Build target
    df = pd.read_sql(
        "SELECT date, value FROM observations WHERE series_id = ? ORDER BY date",
        conn, params=(target_series,), parse_dates=['date']
    ).set_index('date').sort_index()['value']
    df = df.resample('D').ffill()

    if target_mode == 'delta':
        fwd = df.shift(-target_h) - df
    elif target_mode == 'log_fwd_return':
        fwd = np.log(df.shift(-target_h) / df) * 100
    elif target_mode == 'spread_change':
        # not used here
        pass

    aligned = pd.DataFrame({'sig': composite, 'fwd': fwd}).dropna()
    aligned = aligned.iloc[-252*15:]  # last 15 years for legibility

    fig, ax = plt.subplots(figsize=(11, 5.5))
    fig.subplots_adjust(top=0.83, bottom=0.13, left=0.08, right=0.92)

    ax2 = ax.twinx()
    style_ax(ax); style_ax(ax2)
    ax.tick_params(right=False); ax2.tick_params(left=False)

    # 2-series overlay: Ocean (protagonist, signal) + Dusk (antagonist, target)
    l1 = ax.plot(aligned.index, aligned['sig'],
                 color=OCEAN, linewidth=2.4, label=f'{pillar} composite z-score (LHS)')
    l2 = ax2.plot(aligned.index, aligned['fwd'],
                  color=DUSK, linewidth=1.6, alpha=0.85, label=target_label + ' (RHS)')

    ax.axhline(0, color='#D1D1D1', linewidth=0.7, linestyle='--')

    # Pills
    last_d = aligned.index[-1]
    last_sig = aligned['sig'].iloc[-1]
    last_fwd = aligned['fwd'].dropna().iloc[-1]
    ax.text(1.005, last_sig, f'{last_sig:+.2f}', transform=ax.get_yaxis_transform(),
            color='white', backgroundcolor=OCEAN, fontsize=9, fontweight='bold',
            va='center', ha='left',
            bbox=dict(boxstyle='round,pad=0.3', fc=OCEAN, ec='none'))

    add_brand(fig, ax, chart_title, chart_subtitle,
              "Source: Lighthouse Macro analysis. Underlying components from FRED, BLS, Treasury Direct, Yahoo Finance.")
    ax.set_xlim(aligned.index[0], aligned.index[-1])
    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    plt.savefig(OUTPUT / output_name, dpi=180, bbox_inches='tight')
    plt.close()
    return aligned


def chart_spread(conn, pillar, asset_a, asset_b, h, weights, label, output_name,
                 chart_title, chart_subtitle):
    spec = PILLAR_SPECS[pillar]
    z_comp, _ = build_components(conn, spec)
    composite = (z_comp * pd.Series(weights)).sum(axis=1)
    target = build_spread_target(conn, asset_a, asset_b, h)
    aligned = pd.DataFrame({'sig': composite, 'fwd': target}).dropna()
    aligned = aligned.iloc[-252*15:]

    fig, ax = plt.subplots(figsize=(11, 5.5))
    fig.subplots_adjust(top=0.83, bottom=0.13, left=0.08, right=0.92)
    ax2 = ax.twinx()
    style_ax(ax); style_ax(ax2)
    ax.tick_params(right=False); ax2.tick_params(left=False)

    # 2-series overlay: Ocean (signal) + Dusk (target spread)
    ax.plot(aligned.index, aligned['sig'], color=OCEAN, linewidth=2.4,
            label=f'{pillar} composite z-score (LHS)')
    ax2.plot(aligned.index, aligned['fwd'], color=DUSK, linewidth=1.6, alpha=0.85,
             label=label + ' (RHS)')
    ax.axhline(0, color='#D1D1D1', linewidth=0.7, linestyle='--')
    ax2.axhline(0, color='#D1D1D1', linewidth=0.7, linestyle='--')

    add_brand(fig, ax, chart_title, chart_subtitle,
              "Source: Lighthouse Macro analysis. Component data from FRED, BLS, Treasury Direct, Yahoo Finance.")
    ax.set_xlim(aligned.index[0], aligned.index[-1])
    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    plt.savefig(OUTPUT / output_name, dpi=180, bbox_inches='tight')
    plt.close()
    return aligned


def chart_summary_bar(results, output_name):
    """Bar chart of OOS IC magnitudes by indicator/asset."""
    fig, ax = plt.subplots(figsize=(11, 5.5))
    fig.subplots_adjust(top=0.83, bottom=0.18, left=0.30, right=0.95)
    style_ax(ax)
    ax.tick_params(left=False, bottom=False)

    labels = [r['label'] for r in results]
    values = [abs(r['ic']) for r in results]
    colors = [OCEAN if abs(v) >= 0.5 else SKY if abs(v) >= 0.4 else DOLDRUMS
              for v in values]

    y = np.arange(len(labels))
    bars = ax.barh(y, values, color=colors, height=0.7)
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=10)
    ax.invert_yaxis()
    ax.set_xlim(0, max(values) * 1.15)
    ax.axvline(0.30, color=DOLDRUMS, linestyle='--', linewidth=0.6, alpha=0.5)
    ax.text(0.305, len(labels) - 0.5, '|IC| = 0.30 threshold',
            color=DOLDRUMS, fontsize=8, alpha=0.7)

    for i, (bar, v) in enumerate(zip(bars, values)):
        ax.text(bar.get_width() + 0.005, bar.get_y() + bar.get_height()/2,
                f'{v:.2f}', va='center', fontsize=9, color='#1A1A1A',
                family='Source Code Pro', fontweight='bold')

    add_brand(fig, ax,
              "Best Predictive Signal Per Indicator",
              "Out-of-sample rank information coefficient (absolute), best target per indicator",
              "Source: Lighthouse Macro indicator rebuild, 2026-04-29. "
              "Optimization with rank IC objective, SLSQP, bounds [0.05, 0.30], 90/10 IS/OOS split.")
    ax.set_xlabel('|Out-of-sample rank IC|', fontsize=9, color=DOLDRUMS)

    plt.savefig(OUTPUT / output_name, dpi=180, bbox_inches='tight')
    plt.close()


def main():
    conn = sqlite3.connect(DB_PATH)

    # Load all results
    multi = json.loads(Path("/Users/bob/LHM/Outputs/mri_optimization/pillar_multiasset_optimization.json").read_text())
    spread = json.loads(Path("/Users/bob/LHM/Outputs/mri_optimization/pillar_spread_optimization.json").read_text())

    # 1. Summary bar chart — best OOS IC per pillar (mix of multi-asset and spread)
    summary = []
    # Per-pillar best from multi-asset
    for pillar, p in multi['pillars'].items():
        b = p.get('best_target')
        if b is None:
            continue
        full = {
            'LPI':'Labor Pressure', 'PCI':'Price Conditions', 'GCI':'Growth Conditions',
            'HCI':'Housing Conditions', 'CCI':'Consumer Conditions', 'BCI':'Business Conditions',
            'TCI':'Trade Conditions', 'GCI_Gov':'Government Conditions',
            'FCI':'Financial Conditions', 'LCI':'Liquidity Cushion',
            'MSI':'Market Structure', 'SPI':'Sentiment & Positioning',
        }.get(pillar, pillar)
        summary.append({
            'pillar': pillar,
            'label': f"{full} → {b['target_label']}",
            'ic': b['oos_ic'],
        })
    # Sort by |IC|
    summary.sort(key=lambda r: -abs(r['ic']))
    chart_summary_bar(summary, '01_summary_bar.png')
    print("Built: 01_summary_bar.png")

    # Headline charts: top 3 spreads
    # PCI -> 2y yield (the strongest signal, +0.77)
    pci_target = next((t for t in multi['pillars']['PCI']['targets_tested']
                       if t['target_series'] == 'DGS2'), None)
    if pci_target:
        chart_pillar_vs_target(
            conn, 'PCI', 'DGS2', 252, 'delta',
            "Forward 2-year Treasury yield change at 252d",
            '02_pci_vs_2y.png',
            weights=pci_target['optimized_weights'],
            chart_title="The Price Conditions Index Leads The Front Of The Curve",
            chart_subtitle="Out-of-sample rank IC = +0.77. Strongest leading relationship in the framework."
        )
        print("Built: 02_pci_vs_2y.png")

    # LCI -> HYG/LQD spread
    lci_spread = spread['pillars']['LCI']['best_spread']
    if lci_spread:
        chart_spread(
            conn, 'LCI', lci_spread['asset_a'], lci_spread['asset_b'],
            lci_spread['horizon_days'], lci_spread['optimized_weights'],
            "Forward HYG/LQD spread change (63d, log)",
            '03_lci_vs_hyg_lqd.png',
            "Liquidity Cushion Index Leads HY-vs-IG Credit Compression",
            f"OOS rank IC = {lci_spread['oos_ic']:+.2f}. When liquidity scarce, HY underperforms IG."
        )
        print("Built: 03_lci_vs_hyg_lqd.png")

    # LPI -> SPY/TLT
    lpi_spread = spread['pillars']['LPI']['best_spread']
    if lpi_spread:
        chart_spread(
            conn, 'LPI', lpi_spread['asset_a'], lpi_spread['asset_b'],
            lpi_spread['horizon_days'], lpi_spread['optimized_weights'],
            "Forward SPY/TLT spread change (252d, log)",
            '04_lpi_vs_spy_tlt.png',
            "Labor Pressure Index Leads Risk-On vs Risk-Off",
            f"OOS rank IC = {lpi_spread['oos_ic']:+.2f}. Labor weakness predicts equity underperformance vs duration."
        )
        print("Built: 04_lpi_vs_spy_tlt.png")

    # HCI -> XHB/SPY
    hci_spread = spread['pillars']['HCI']['best_spread']
    if hci_spread:
        chart_spread(
            conn, 'HCI', hci_spread['asset_a'], hci_spread['asset_b'],
            hci_spread['horizon_days'], hci_spread['optimized_weights'],
            "Forward XHB/SPY spread change (252d, log)",
            '05_hci_vs_xhb_spy.png',
            "Housing Conditions Lead Homebuilders Relative",
            f"OOS rank IC = {hci_spread['oos_ic']:+.2f}. Housing strength predicts XHB outperformance vs S&P 500."
        )
        print("Built: 05_hci_vs_xhb_spy.png")

    # FCI -> XLY/XLP
    fci_spread = spread['pillars']['FCI']['best_spread']
    if fci_spread:
        chart_spread(
            conn, 'FCI', fci_spread['asset_a'], fci_spread['asset_b'],
            fci_spread['horizon_days'], fci_spread['optimized_weights'],
            "Forward XLY/XLP spread change (63d, log)",
            '06_fci_vs_xly_xlp.png',
            "Financial Conditions Lead Cyclicals vs Defensives",
            f"OOS rank IC = {fci_spread['oos_ic']:+.2f}. Financial stress predicts cyclical underperformance vs staples."
        )
        print("Built: 06_fci_vs_xly_xlp.png")

    conn.close()
    print(f"\nDone. Charts in {OUTPUT}/")


if __name__ == "__main__":
    main()
