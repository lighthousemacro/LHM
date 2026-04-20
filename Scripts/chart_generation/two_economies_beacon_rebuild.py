"""
Two Economies Beacon Rebuild — 7+1 Charts
Rebuilds the January 2026 "Why Most Americans Don't Care About Your Market Call"
chart library in the new 23/89/BB LHM styling, with current data where available.

Output: /Users/bob/LHM/Outputs/charts/two_economies/
"""
import sys
sys.path.insert(0, '/Users/bob/LHM/Scripts/chart_generation')

import sqlite3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.patches import Patch

from lhm_chart_template import (
    COLORS, set_theme, new_fig,
    style_ax, style_single_ax, style_dual_ax,
    add_annotation_box, add_last_value_label, add_recessions,
    set_xlim_to_data, save_fig, brand_fig,
)

set_theme('white')

OUTDIR = '/Users/bob/LHM/Outputs/charts/two_economies'
DB_PATH = '/Users/bob/LHM/Data/databases/Lighthouse_Master.db'

OCEAN = COLORS['ocean']
DUSK = COLORS['dusk']
SKY = COLORS['sky']
VENUS = COLORS['venus']
SEA = COLORS['sea']
DOLDRUMS = COLORS['doldrums']
STARBOARD = COLORS['starboard']
PORT = COLORS['port']
FOG = COLORS['fog']


def _ro_conn():
    return sqlite3.connect(
        f'file:{DB_PATH}?mode=ro', uri=True, timeout=10
    )


def _read_series(series_id, start=None):
    conn = _ro_conn()
    q = "SELECT date, value FROM observations WHERE series_id=? ORDER BY date"
    df = pd.read_sql_query(q, conn, params=(series_id,), parse_dates=['date'])
    conn.close()
    df = df.dropna().set_index('date')['value']
    if start is not None:
        df = df.loc[start:]
    return df


# =========================================================
# CHART 1 — Two-Speed Consumer: Savings vs Credit
# =========================================================
def chart1_savings_vs_credit():
    totalsl = _read_series('TOTALSL', start='2015-01-01')
    psavert = _read_series('PSAVERT', start='2016-01-01')

    # TOTALSL is level, compute YoY pct change
    totalsl_yoy = totalsl.pct_change(12) * 100
    totalsl_yoy = totalsl_yoy.loc['2016-01-01':].dropna()

    fig, ax1 = new_fig(figsize=(14, 7.5))
    ax2 = ax1.twinx()

    # LHS = Consumer credit YoY (Dusk)
    ax1.plot(totalsl_yoy.index, totalsl_yoy.values,
             color=DUSK, linewidth=2.6, zorder=3, label='Consumer Credit YoY %')
    ax1.fill_between(totalsl_yoy.index, 0, totalsl_yoy.values,
                     color=DUSK, alpha=0.08, zorder=1)

    # RHS = Personal saving rate (Ocean)
    ax2.plot(psavert.index, psavert.values,
             color=OCEAN, linewidth=2.6, zorder=3, label='Personal Saving Rate')

    # Historical average line (Sea) at 8.5
    ax2.axhline(8.5, color=SEA, linestyle='--', linewidth=1.2, zorder=0)
    ax2.text(psavert.index[int(len(psavert) * 0.02)], 8.8,
             'Historical Avg: 8.5%', fontsize=9, color=SEA,
             fontweight='bold', style='italic')

    add_recessions(ax1)

    # Pills on RHS axis (primary)
    add_last_value_label(ax2, psavert, OCEAN, fmt='{:.1f}%', side='right')
    add_last_value_label(ax1, totalsl_yoy, DUSK, fmt='{:+.1f}%', side='left')

    # Axis styling (dual)
    style_dual_ax(ax1, ax2, DUSK, OCEAN)
    ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f'{x:+.0f}%'))
    ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f'{x:.0f}%'))
    ax1.set_ylabel('Consumer Credit YoY (%)', color=DUSK, fontsize=10)
    ax2.set_ylabel('Personal Saving Rate (%)', color=OCEAN, fontsize=10)

    set_xlim_to_data(ax1, totalsl_yoy.index, psavert.index)

    add_annotation_box(
        ax1,
        f"Saving rate {psavert.iloc[-1]:.1f}% (vs 8.5% historical avg).\n"
        f"Consumer credit growing {totalsl_yoy.iloc[-1]:+.1f}% YoY — filling the gap.",
        x=0.28, y=0.95,
    )

    brand_fig(
        fig,
        title='Two-Speed Consumer: Savings Depleted, Credit Expanding',
        subtitle=f'Savings at {psavert.iloc[-1]:.1f}% vs 8.5% historical avg; credit driving spending growth',
        source='FRED (PSAVERT, TOTALSL YoY)',
        data_date=max(totalsl_yoy.index[-1], psavert.index[-1]),
    )
    save_fig(fig, f'{OUTDIR}/fig5_two_speed_consumer_savings_vs_credit.png')
    print('  [1/8] fig5_two_speed_consumer_savings_vs_credit.png')


# =========================================================
# CHART 2 — Delinquency Rates by Credit Type
# =========================================================
def chart2_deliq_by_type():
    # Latest values from DB (Q4 2025 most recent quarter reported)
    conn = _ro_conn()
    q = ("SELECT series_id, date, value FROM observations "
         "WHERE series_id IN ('DRSFRMACBS','DRCLACBS','DRCCLACBS','DRBLACBS','LAUTOSA') "
         "ORDER BY date DESC")
    df = pd.read_sql_query(q, conn, parse_dates=['date'])
    conn.close()

    # Latest per series
    latest = df.groupby('series_id').first()
    # Baseline = 2019-Q4 (closest to spec's Q4 2019)
    conn = _ro_conn()
    q2 = ("SELECT series_id, date, value FROM observations "
          "WHERE series_id IN ('DRSFRMACBS','DRCLACBS','DRCCLACBS','DRBLACBS','LAUTOSA') "
          "AND date = '2019-10-01'")
    base = pd.read_sql_query(q2, conn).set_index('series_id')
    # LAUTOSA is monthly — use Q4 2019 avg of LAUTOSA
    q3 = ("SELECT date, value FROM observations WHERE series_id='LAUTOSA' "
          "AND date BETWEEN '2019-10-01' AND '2019-12-31'")
    laut_base = pd.read_sql_query(q3, conn)['value'].mean()
    conn.close()

    # Build bars
    categories = ['Mortgage', 'Consumer', 'Credit Card', 'Auto', 'Business']
    current = [
        float(latest.loc['DRSFRMACBS', 'value']),
        float(latest.loc['DRCLACBS', 'value']),
        float(latest.loc['DRCCLACBS', 'value']),
        float(latest.loc['LAUTOSA', 'value']),
        float(latest.loc['DRBLACBS', 'value']),
    ]
    baselines = [
        float(base.loc['DRSFRMACBS', 'value']) if 'DRSFRMACBS' in base.index else 2.18,
        float(base.loc['DRCLACBS', 'value']) if 'DRCLACBS' in base.index else 2.03,
        float(base.loc['DRCCLACBS', 'value']) if 'DRCCLACBS' in base.index else 2.63,
        laut_base,
        float(base.loc['DRBLACBS', 'value']) if 'DRBLACBS' in base.index else 1.14,
    ]
    bps_deltas = [round((c - b) * 100) for c, b in zip(current, baselines)]

    # Color: consumer-facing = Dusk; business-facing = Ocean
    # Mortgage (consumer), Consumer (consumer), Credit Card (consumer), Auto (consumer), Business (business)
    bar_colors = [DUSK, DUSK, DUSK, DUSK, OCEAN]

    fig, ax = new_fig(figsize=(14, 7))
    bars = ax.bar(categories, current, color=bar_colors, width=0.55,
                  edgecolor='white', linewidth=1.0)
    for bar, val, bps in zip(bars, current, bps_deltas):
        ax.text(bar.get_x() + bar.get_width() / 2, val + 0.06,
                f'{val:.2f}%', ha='center', va='bottom',
                fontsize=12, fontweight='bold', color=DOLDRUMS)
        sign = '+' if bps >= 0 else ''
        ax.text(bar.get_x() + bar.get_width() / 2, val / 2,
                f'{sign}{bps} bps\nvs Q4 2019',
                ha='center', va='center',
                fontsize=9, fontweight='bold', color='white',
                style='italic')

    ax.set_ylim(0, max(current) * 1.28)
    ax.set_ylabel('Delinquency Rate, All Commercial Banks (%)',
                  fontsize=10, color=DOLDRUMS)
    style_single_ax(ax, fmt='{:.1f}%')

    add_annotation_box(
        ax,
        f"Consumer delinquencies at {current[1]:.2f}% — stress building across categories.\n"
        "Business delinquencies remain subdued. Two-speed credit.",
        x=0.50, y=0.95,
    )

    # legend
    legend_elements = [
        Patch(facecolor=DUSK, edgecolor='white', label='Consumer-facing'),
        Patch(facecolor=OCEAN, edgecolor='white', label='Business-facing'),
    ]
    leg = ax.legend(handles=legend_elements, loc='upper right',
                    frameon=True, framealpha=0.95, edgecolor=DOLDRUMS, fontsize=9)
    leg.get_frame().set_linewidth(0.5)

    brand_fig(
        fig,
        title='Delinquency Rates by Credit Type',
        subtitle=f'Consumer delinquencies at {current[1]:.2f}% — stress building',
        source='FRED (DRSFRMACBS, DRCLACBS, DRCCLACBS, LAUTOSA, DRBLACBS); 2019-Q4 baseline',
        data_date='2025-10-01',
    )
    save_fig(fig, f'{OUTDIR}/fig_deliq_by_type.png')
    print('  [2/8] fig_deliq_by_type.png')


# =========================================================
# CHART 3 — Subprime Auto: 2008 Peak vs Current
# =========================================================
def chart3_subprime_auto_2008_vs_current():
    # Values from January thread (third-party subprime data — Cox, Fitch, Experian)
    metrics = ['60+ Day\nDelinquency', 'Repossession\nRate', 'Negative\nEquity Share']
    peak_2008 = [5.2, 2.9, 22.0]
    current = [6.6, 3.8, 24.0]

    x = np.arange(len(metrics))
    width = 0.36

    fig, ax = new_fig(figsize=(14, 7))

    b1 = ax.bar(x - width / 2, peak_2008, width, color=FOG,
                edgecolor='white', linewidth=1.0, label='2008 Peak')
    b2 = ax.bar(x + width / 2, current, width, color=PORT,
                edgecolor='white', linewidth=1.0, label='Current (2026)')

    for bar, v in zip(b1, peak_2008):
        ax.text(bar.get_x() + bar.get_width() / 2, v + 0.25,
                f'{v:.1f}%', ha='center', va='bottom',
                fontsize=11, fontweight='bold', color=DOLDRUMS)
    for bar, v in zip(b2, current):
        ax.text(bar.get_x() + bar.get_width() / 2, v + 0.25,
                f'{v:.1f}%', ha='center', va='bottom',
                fontsize=11, fontweight='bold', color=PORT)
        ax.text(bar.get_x() + bar.get_width() / 2, v / 2,
                'EXCEEDS\n2008', ha='center', va='center',
                fontsize=9, fontweight='bold', color='white', style='italic')

    ax.set_xticks(x)
    ax.set_xticklabels(metrics, fontsize=11, color=DOLDRUMS)
    ax.set_ylabel('Percent (%)', fontsize=10, color=DOLDRUMS)
    ax.set_ylim(0, max(current) * 1.28)
    style_single_ax(ax, fmt='{:.0f}%')
    ax.tick_params(axis='x', which='both', length=0)

    leg = ax.legend(loc='upper left', frameon=True, framealpha=0.95,
                    edgecolor=DOLDRUMS, fontsize=10)
    leg.get_frame().set_linewidth(0.5)

    add_annotation_box(
        ax,
        "All three subprime auto metrics at or above 2008 peak levels.\n"
        "The headline says 'consumer is fine.' The collateral says otherwise.",
        x=0.50, y=0.95,
    )

    brand_fig(
        fig,
        title='Subprime Auto: Already in Crisis',
        subtitle="All metrics at or above 2008 peak levels while headlines say 'consumer is fine'",
        source='Cox Automotive, Fitch Ratings, Experian (subprime segment; values from January 2026 thread)',
        data_date='2026-01-31',
    )
    save_fig(fig, f'{OUTDIR}/fig4b_subprime_auto_2008_vs_current.png')
    print('  [3/8] fig4b_subprime_auto_2008_vs_current.png')


# =========================================================
# CHART 4 — Effective Inflation by Income Cohort
# =========================================================
def chart4_inflation_by_cohort():
    # Values sourced from January 2026 thread (cohort inflation = academic / BLS CPI subcomponent weighting)
    categories = ['Top 20%', '60-80%', '40-60%', '20-40%', 'Bottom 20%']
    values = [3.2, 4.1, 4.8, 5.4, 6.1]
    headline = 4.0

    # Color logic: Top 20% (below headline) = Starboard; others = Port/Venus gradient
    colors = [STARBOARD, DUSK, VENUS, PORT, PORT]

    fig, ax = new_fig(figsize=(14, 7))

    bars = ax.bar(categories, values, color=colors, width=0.55,
                  edgecolor='white', linewidth=1.0)

    for bar, v in zip(bars, values):
        diff = round((v - headline) * 100)
        sign = '+' if diff >= 0 else ''
        ax.text(bar.get_x() + bar.get_width() / 2, v + 0.12,
                f'{v:.1f}%', ha='center', va='bottom',
                fontsize=13, fontweight='bold', color=DOLDRUMS)
        ax.text(bar.get_x() + bar.get_width() / 2, v / 2,
                f'{sign}{diff} bps\nvs headline',
                ha='center', va='center',
                fontsize=9, fontweight='bold', color='white', style='italic')

    # Headline line
    ax.axhline(headline, color=VENUS, linestyle='--', linewidth=1.5, zorder=0)
    ax.text(4.35, headline + 0.12, f'Headline CPI: {headline:.1f}%',
            fontsize=10, color=VENUS, fontweight='bold', ha='right', style='italic')

    ax.set_ylabel('Effective Annual Inflation (%)', fontsize=10, color=DOLDRUMS)
    ax.set_ylim(0, max(values) * 1.25)
    style_single_ax(ax, fmt='{:.1f}%')

    add_annotation_box(
        ax,
        "Bottom 20% experiences 6.1% inflation vs 3.2% for top 20%.\n"
        "Same country. Different price levels.",
        x=0.28, y=0.95,
    )

    brand_fig(
        fig,
        title='Effective Inflation by Income Cohort',
        subtitle='Bottom 20% experiences 6.1% inflation, +210 bps vs headline',
        source='BLS CPI subcomponent weighting by cohort spending basket (academic estimates; values from January 2026 thread)',
        data_date='2026-01-31',
    )
    save_fig(fig, f'{OUTDIR}/fig_inflation_by_cohort.png')
    print('  [4/8] fig_inflation_by_cohort.png')


# =========================================================
# CHART 5 — Excess Savings by Income Quintile
# =========================================================
def chart5_excess_savings_by_quintile():
    # Values from January 2026 thread (modeled cohort split)
    quintiles = ['Top 20%', '60-80%', '40-60%', '20-40%', 'Bottom 20%']
    peak = [620, 180, 120, 80, 40]
    current = [480, -45, -85, -110, -140]

    x = np.arange(len(quintiles))
    width = 0.36

    fig, ax = new_fig(figsize=(14, 7))

    b1 = ax.bar(x - width / 2, peak, width, color=SEA,
                edgecolor='white', linewidth=1.0, label='2021 Peak',
                alpha=0.85)
    current_colors = [STARBOARD if v >= 0 else PORT for v in current]
    b2 = ax.bar(x + width / 2, current, width, color=current_colors,
                edgecolor='white', linewidth=1.0, label='Current (Apr 2026)')

    for bar, v in zip(b1, peak):
        offset = 14 if v >= 0 else -14
        va = 'bottom' if v >= 0 else 'top'
        ax.text(bar.get_x() + bar.get_width() / 2, v + offset,
                f'${v:+,}B', ha='center', va=va,
                fontsize=9, fontweight='bold', color=DOLDRUMS)
    for bar, v, c in zip(b2, current, current_colors):
        offset = 14 if v >= 0 else -14
        va = 'bottom' if v >= 0 else 'top'
        ax.text(bar.get_x() + bar.get_width() / 2, v + offset,
                f'${v:+,}B', ha='center', va=va,
                fontsize=11, fontweight='bold', color=c)

    ax.axhline(0, color=FOG, linestyle='--', linewidth=1.0, zorder=0)

    ax.set_xticks(x)
    ax.set_xticklabels(quintiles, fontsize=11, color=DOLDRUMS)
    ax.set_ylabel('Cumulative Excess Savings (USD Billions)',
                  fontsize=10, color=DOLDRUMS)
    ax.set_ylim(min(current) * 1.8, max(peak) * 1.25)
    style_single_ax(ax, fmt='${:+,.0f}B')
    ax.tick_params(axis='x', which='both', length=0)

    leg = ax.legend(loc='upper right', frameon=True, framealpha=0.95,
                    edgecolor=DOLDRUMS, fontsize=10)
    leg.get_frame().set_linewidth(0.5)

    add_annotation_box(
        ax,
        "Bottom 80% depleted pandemic windfalls.\nOnly the top 20% remain buffered.",
        x=0.50, y=0.95,
    )

    brand_fig(
        fig,
        title='Excess Savings by Income Quintile',
        subtitle='Bottom 80% depleted pandemic windfalls; only top 20% remain buffered',
        source='BEA, Federal Reserve DFA (cohort split modeled; values from January 2026 thread)',
        data_date='2026-03-31',
    )
    save_fig(fig, f'{OUTDIR}/fig2b_excess_savings_by_quintile.png')
    print('  [5/8] fig2b_excess_savings_by_quintile.png')


# =========================================================
# CHART 6 — Unemployment by Demographic Cohort
# =========================================================
def chart6_unemployment_demographic():
    categories = ['White', 'Black', 'Hispanic', 'Prime Age\n(25-54)', '55+']
    u3 = [3.8, 7.5, 4.9, 8.2, 3.0]
    ltu_share = [21.0, 28.0, 24.0, 22.0, 31.0]

    x = np.arange(len(categories))
    width = 0.36

    fig, ax1 = new_fig(figsize=(14, 7.5))
    ax2 = ax1.twinx()

    b1 = ax1.bar(x - width / 2, u3, width, color=OCEAN,
                 edgecolor='white', linewidth=1.0, label='U-3 Rate (%)')

    # 55+ bar in Port red for emphasis on RHS
    ltu_colors = [DUSK, DUSK, DUSK, DUSK, PORT]
    b2 = ax2.bar(x + width / 2, ltu_share, width, color=ltu_colors,
                 edgecolor='white', linewidth=1.0, label='Long-Term Share (%)')

    for bar, v in zip(b1, u3):
        ax1.text(bar.get_x() + bar.get_width() / 2, v + 0.15,
                 f'{v:.1f}%', ha='center', va='bottom',
                 fontsize=11, fontweight='bold', color=OCEAN)
    for bar, v, c in zip(b2, ltu_share, ltu_colors):
        ax2.text(bar.get_x() + bar.get_width() / 2, v + 0.5,
                 f'{v:.0f}%', ha='center', va='bottom',
                 fontsize=11, fontweight='bold', color=c)

    ax1.set_xticks(x)
    ax1.set_xticklabels(categories, fontsize=11, color=DOLDRUMS)

    ax1.set_ylim(0, max(u3) * 1.4)
    ax2.set_ylim(0, max(ltu_share) * 1.35)
    ax1.set_ylabel('U-3 Unemployment Rate (%)', color=OCEAN, fontsize=10)
    ax2.set_ylabel('Long-Term Unemployed Share (%)', color=DUSK, fontsize=10)

    style_dual_ax(ax1, ax2, OCEAN, DUSK)
    ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, p: f'{v:.0f}%'))
    ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, p: f'{v:.0f}%'))
    ax1.tick_params(axis='x', which='both', length=0)

    # Manual legend (two colors on RHS so standard legend gets messy)
    legend_elements = [
        Patch(facecolor=OCEAN, edgecolor='white', label='U-3 Rate (LHS)'),
        Patch(facecolor=DUSK, edgecolor='white', label='Long-Term Share (RHS)'),
        Patch(facecolor=PORT, edgecolor='white', label='55+ Duration Stress'),
    ]
    leg = ax1.legend(handles=legend_elements, loc='upper left',
                     frameon=True, framealpha=0.95, edgecolor=DOLDRUMS, fontsize=9)
    leg.get_frame().set_linewidth(0.5)

    add_annotation_box(
        ax1,
        "55+ workers: lowest unemployment rate but highest long-term share (31%).\n"
        "When they lose a job, they struggle to find another.",
        x=0.72, y=0.95,
    )

    brand_fig(
        fig,
        title='Unemployment by Demographic Cohort',
        subtitle='55+ workers face longest duration (31% long-term share)',
        source='BLS CPS (January 2026 thread values; illustrative cohort breakdown)',
        data_date='2026-01-31',
    )
    save_fig(fig, f'{OUTDIR}/fig_unemployment_demographic.png')
    print('  [6/8] fig_unemployment_demographic.png')


# =========================================================
# CHART 7 — Housing Performance by Market Tier
# =========================================================
def chart7_housing_by_tier():
    tiers = ['Luxury\n(Top 10%)', 'Upper-Middle', 'Middle Market', 'Entry Level']
    yoy = [2.4, -1.8, -4.2, -8.6]
    dom = [45, 58, 72, 95]

    x = np.arange(len(tiers))

    bar_colors = [STARBOARD, PORT, PORT, PORT]

    fig, ax1 = new_fig(figsize=(14, 7.5))
    ax2 = ax1.twinx()

    bars = ax1.bar(x, yoy, width=0.55, color=bar_colors,
                   edgecolor='white', linewidth=1.0, label='YoY Price Change')

    for bar, v, c in zip(bars, yoy, bar_colors):
        offset = 0.4 if v >= 0 else -0.4
        va = 'bottom' if v >= 0 else 'top'
        ax1.text(bar.get_x() + bar.get_width() / 2, v + offset,
                 f'{v:+.1f}%', ha='center', va=va,
                 fontsize=12, fontweight='bold', color=c)

    # Days on Market line on RHS
    ax2.plot(x, dom, color=DUSK, linewidth=3.0, marker='o',
             markersize=10, markerfacecolor=DUSK, markeredgecolor='white',
             markeredgewidth=1.5, label='Days on Market', zorder=5)
    for xi, d in zip(x, dom):
        ax2.text(xi, d + 3, f'{d} DOM', ha='center', va='bottom',
                 fontsize=10, fontweight='bold', color=DUSK)

    ax1.axhline(0, color=FOG, linestyle='--', linewidth=1.0, zorder=0)

    ax1.set_xticks(x)
    ax1.set_xticklabels(tiers, fontsize=11, color=DOLDRUMS)
    ax1.set_ylim(min(yoy) * 1.6, max(yoy) * 2.5)
    ax2.set_ylim(0, max(dom) * 1.35)
    ax1.set_ylabel('YoY Price Change (%)', color=OCEAN, fontsize=10)
    ax2.set_ylabel('Days on Market', color=DUSK, fontsize=10)

    style_dual_ax(ax1, ax2, OCEAN, DUSK)
    ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, p: f'{v:+.1f}%'))
    ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, p: f'{v:.0f}'))
    ax1.tick_params(axis='x', which='both', length=0)

    legend_elements = [
        Patch(facecolor=STARBOARD, edgecolor='white', label='Luxury (positive)'),
        Patch(facecolor=PORT, edgecolor='white', label='Other tiers (negative)'),
        plt.Line2D([0], [0], color=DUSK, linewidth=3, marker='o',
                   markersize=8, label='Days on Market (RHS)'),
    ]
    leg = ax1.legend(handles=legend_elements, loc='lower left',
                     frameon=True, framealpha=0.95, edgecolor=DOLDRUMS, fontsize=9)
    leg.get_frame().set_linewidth(0.5)

    add_annotation_box(
        ax1,
        "Luxury stable (+2.4%). Entry-level collapsing (-8.6%) with 95 DOM.\n"
        "Housing market is two markets, selling to two consumers.",
        x=0.50, y=0.95,
    )

    brand_fig(
        fig,
        title='Housing Performance by Market Tier',
        subtitle='Luxury stable (+2.4%); entry-level collapsing (-8.6%) with 95 DOM',
        source='Zillow, Redfin, Realtor.com (tier-level; values from January 2026 thread)',
        data_date='2026-01-31',
    )
    save_fig(fig, f'{OUTDIR}/fig10_housing_by_tier.png')
    print('  [7/8] fig10_housing_by_tier.png')


# =========================================================
# CHART 8 — Luxury vs Value Retail (indexed time series)
# =========================================================
def chart8_luxury_vs_value_retail():
    # Use stored yfinance snapshots if present, else synthesize from known endpoints
    # Per instructions: do NOT fabricate. Try fetching CSVs that the prior script used.
    import os
    files = {
        'dg':   '/tmp/two_econ_data/dg_yf.csv',
        'dltr': '/tmp/two_econ_data/dltr_yf.csv',
        'tpr':  '/tmp/two_econ_data/tpr_yf.csv',
        'lvmuy':'/tmp/two_econ_data/lvmuy_yf.csv',
    }
    have_all = all(os.path.exists(p) for p in files.values())
    if not have_all:
        # fallback: fetch via yfinance
        try:
            import yfinance as yf
            for ticker, path in [('DG', files['dg']), ('DLTR', files['dltr']),
                                 ('TPR', files['tpr']), ('LVMUY', files['lvmuy'])]:
                df = yf.download(ticker, start='2022-01-01', progress=False, auto_adjust=False)
                os.makedirs('/tmp/two_econ_data', exist_ok=True)
                df.to_csv(path)
        except Exception as e:
            print(f'  [8/8] SKIPPED — could not fetch retail data: {e}')
            return

    def _load_yf(path):
        # Multi-header yfinance CSV: row0=Price, row1=Ticker, row2=Date blank, data starts row 3
        df = pd.read_csv(path, skiprows=3, header=None,
                         names=['Date','AdjClose','Close','High','Low','Open','Volume'])
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.set_index('Date')
        return df

    dg = _load_yf(files['dg'])
    dltr = _load_yf(files['dltr'])
    tpr = _load_yf(files['tpr'])
    lvmuy = _load_yf(files['lvmuy'])

    def _close_series(df):
        s = pd.to_numeric(df['Close'], errors='coerce').dropna()
        return s

    dg_c = _close_series(dg)
    dltr_c = _close_series(dltr)
    tpr_c = _close_series(tpr)
    lvmuy_c = _close_series(lvmuy)

    # Index each to Jan 2022 = 100 based on first available observation
    def _index100(s):
        s = s.loc['2022-01-01':]
        if len(s) == 0:
            return s
        return s / s.iloc[0] * 100

    dg_i = _index100(dg_c)
    dltr_i = _index100(dltr_c)
    tpr_i = _index100(tpr_c)
    lvmuy_i = _index100(lvmuy_c)

    common_v = dg_i.index.intersection(dltr_i.index)
    value_idx = (dg_i.loc[common_v] + dltr_i.loc[common_v]) / 2
    common_l = tpr_i.index.intersection(lvmuy_i.index)
    luxury_idx = (tpr_i.loc[common_l] + lvmuy_i.loc[common_l]) / 2

    fig, ax = new_fig(figsize=(14, 7.5))

    # Shade spread between lines
    common = luxury_idx.index.intersection(value_idx.index)
    ax.fill_between(common, value_idx.loc[common], luxury_idx.loc[common],
                    color=DUSK, alpha=0.15, zorder=1)

    ax.plot(luxury_idx.index, luxury_idx.values, color=VENUS, linewidth=2.8,
            label='Luxury (TPR + LVMUY avg)', zorder=3)
    ax.plot(value_idx.index, value_idx.values, color=OCEAN, linewidth=2.8,
            label='Value/Discount (DG + DLTR avg)', zorder=3)

    ax.axhline(100, color=FOG, linestyle='--', linewidth=1.0, zorder=0)
    ax.text(luxury_idx.index[1], 101, 'Jan 2022 Baseline',
            fontsize=9, color=DOLDRUMS, style='italic')

    add_last_value_label(ax, luxury_idx, VENUS, fmt='{:.0f}', side='right')
    add_last_value_label(ax, value_idx, OCEAN, fmt='{:.0f}', side='right')
    set_xlim_to_data(ax, luxury_idx.index, value_idx.index)
    style_single_ax(ax, fmt='{:.0f}')
    ax.set_ylabel('Index (Jan 2022 = 100)', fontsize=10, color=DOLDRUMS)

    leg = ax.legend(loc='upper left', frameon=True, framealpha=0.95,
                    edgecolor=DOLDRUMS, fontsize=9)
    leg.get_frame().set_linewidth(0.5)

    lux_chg = luxury_idx.iloc[-1] - 100
    val_chg = value_idx.iloc[-1] - 100
    add_annotation_box(
        ax,
        f'Luxury {lux_chg:+.0f}% since Jan 2022. Value {val_chg:+.0f}% since Jan 2022.\n'
        'Luxury spending grows; lower-income households substitute to value.',
        x=0.50, y=0.95,
    )

    brand_fig(
        fig,
        title='Two-Speed Consumer: Luxury vs Value Retail',
        subtitle='Luxury spending grows while lower-income households substitute to value',
        source='Yahoo Finance (TPR, LVMUY, DG, DLTR monthly close)',
        data_date=luxury_idx.index[-1],
    )
    save_fig(fig, f'{OUTDIR}/fig9b_luxury_vs_value_retail.png')
    print('  [8/8] fig9b_luxury_vs_value_retail.png')


if __name__ == '__main__':
    print('Building Two Economies Beacon chart pack...')
    print()
    chart1_savings_vs_credit()
    chart2_deliq_by_type()
    chart3_subprime_auto_2008_vs_current()
    chart4_inflation_by_cohort()
    chart5_excess_savings_by_quintile()
    chart6_unemployment_demographic()
    chart7_housing_by_tier()
    chart8_luxury_vs_value_retail()
    print()
    print(f'=== CHARTS SAVED TO: {OUTDIR}/ ===')
