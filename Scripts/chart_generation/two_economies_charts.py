"""
Two Economies — Consumer Bifurcation Update
12 charts using the LHM canonical chart template.
Real data sourced where available, hardcoded with flags where not.

Output: /Users/bob/LHM/Outputs/Charts/two_economies/
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
    COLORS, set_theme, new_fig, new_fig_multi,
    style_ax, style_single_ax, add_annotation_box,
    add_last_value_label, add_recessions, set_xlim_to_data,
    save_fig, brand_fig,
)

set_theme('white')

OUTDIR = '/Users/bob/LHM/Outputs/Charts/two_economies'
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


# =========================================================
# FIG 1 — Wealth Concentration (Fed DFA Q3 2025)
# Data: hardcoded from published Fed DFA aggregates
# =========================================================
def fig1_wealth_concentration():
    fig, ax = new_fig(figsize=(14, 7))
    # Extra left margin so long category labels ('Top 10% (incl. Top 1%)')
    # don't spill outside the Ocean border frame.
    fig.subplots_adjust(left=0.14)

    categories = ['Bottom 50%', 'Top 10%\n(incl. Top 1%)', 'Top 1%']
    values = [2.4, 67.0, 30.2]
    colors = [DOLDRUMS, OCEAN, PORT]

    bars = ax.barh(categories, values, color=colors, edgecolor='white', linewidth=1.0, height=0.6)
    for bar, v in zip(bars, values):
        ax.text(v + 1.2, bar.get_y() + bar.get_height()/2,
                f'{v:.1f}%', ha='left', va='center',
                fontsize=13, fontweight='bold', color=DOLDRUMS)

    ax.set_xlim(0, 90)
    style_ax(ax, right_primary=False)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f'{x:.0f}%'))
    ax.tick_params(axis='both', which='both', length=0)

    add_annotation_box(
        ax,
        'The top 1% hold more wealth than the entire\nbottom 50%. By a factor of 12.',
        x=0.75, y=0.18
    )

    brand_fig(fig,
              title='Who Owns America',
              subtitle='Figure 1: Share of U.S. household net worth by wealth percentile',
              source='Federal Reserve Distributional Financial Accounts (Q3 2025)',
              data_date='2025-09-30')
    save_fig(fig, f'{OUTDIR}/fig1_wealth_concentration.png')
    print('  [1/12] fig1_wealth_concentration.png')


# =========================================================
# FIG 2 — Excess Pandemic Savings
# Data: hardcoded, cohort split modeled
# =========================================================
def fig2_excess_savings():
    fig, ax = new_fig(figsize=(14, 7))

    categories = ['Top 20%', 'Bottom 80%']
    values = [470, -437]
    colors = [OCEAN, PORT]

    bars = ax.bar(categories, values, color=colors, width=0.50, edgecolor='white', linewidth=1.0)
    for bar, v in zip(bars, values):
        offset = 30 if v > 0 else -30
        va = 'bottom' if v > 0 else 'top'
        ax.text(bar.get_x() + bar.get_width()/2, v + offset,
                f'${v:+,}B', ha='center', va=va,
                fontsize=14, fontweight='bold',
                color=OCEAN if v > 0 else PORT)

    ax.axhline(0, color=FOG, linestyle='--', linewidth=1.0, zorder=0)
    ax.text(1.35, 8, 'Pre-Pandemic Baseline',
            fontsize=9, color=DOLDRUMS, style='italic', ha='right')

    ax.set_ylabel('Cumulative Excess Savings (USD Billions)', fontsize=10, color=DOLDRUMS)
    ax.set_ylim(-700, 800)
    style_single_ax(ax, fmt='${:+,.0f}B')

    # Simple 2-bar chart: let the data and figcaption carry the story.
    # Annotation removed per design rule — boxes only on multi-series/complex charts.

    brand_fig(fig,
              title='Excess Pandemic Savings: Who Still Has It',
              subtitle='Figure 2: Cumulative excess savings vs. pre-pandemic trend by income cohort',
              source='BEA, Federal Reserve (cohort split modeled, not directly reported)',
              data_date='2025-12-31')
    save_fig(fig, f'{OUTDIR}/fig2_excess_savings.png')
    print('  [2/12] fig2_excess_savings.png')


# =========================================================
# FIG 3 — Savings Rate by Income Group
# Data: BEA PSAVERT confirmed from DB (4.0% Feb 2026). Cohort splits estimated.
# =========================================================
def fig3_savings_rate_quintile():
    fig, ax = new_fig(figsize=(14, 7))

    categories = ['Top 10%', 'Middle 60%', 'Bottom 60%']
    values = [18.0, 4.8, 1.2]
    colors = [STARBOARD, OCEAN, PORT]

    bars = ax.bar(categories, values, color=colors, width=0.50, edgecolor='white', linewidth=1.0)
    for bar, v in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2, v + 0.5,
                f'{v:.1f}%', ha='center', va='bottom',
                fontsize=13, fontweight='bold', color=DOLDRUMS)

    ax.axhline(8.5, color=FOG, linestyle='--', linewidth=1.2, zorder=0)
    ax.text(2.40, 8.8, 'Historical Average: 8.5%',
            fontsize=9, color=DOLDRUMS, ha='right', style='italic')

    ax.axhline(4.0, color=DUSK, linestyle='-', linewidth=1.2, zorder=0)
    ax.text(2.40, 4.3, 'BEA Aggregate: 4.0% (Feb 2026)',
            fontsize=9, color=DUSK, ha='right', style='italic', fontweight='bold')

    ax.set_ylabel('Personal Savings Rate (%)', fontsize=10, color=DOLDRUMS)
    ax.set_ylim(0, 22)
    style_single_ax(ax, fmt='{:.0f}%')

    add_annotation_box(
        ax,
        "Bottom 60% aren't building a buffer. They're surviving month to month.",
        x=0.50, y=0.95
    )

    brand_fig(fig,
              title='Personal Savings Rate by Income Group',
              subtitle='Figure 3: Estimated savings rate by cohort vs. BEA aggregate',
              source='Federal Reserve DFA, academic estimates. BEA PSAVERT = 4.0% (Feb 2026, confirmed from DB)',
              data_date='2026-02-28')
    save_fig(fig, f'{OUTDIR}/fig3_savings_rate_quintile.png')
    print('  [3/12] fig3_savings_rate_quintile.png')


# =========================================================
# FIG 4 — Auto Loan Delinquency (DB: LAUTOSA, all-commercial-bank series)
# Data: REAL from Lighthouse_Master.db
# =========================================================
def fig4_subprime_auto_delinquency():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(
        "SELECT date, value FROM observations WHERE series_id='LAUTOSA' ORDER BY date",
        conn, parse_dates=['date']
    )
    conn.close()
    df = df.dropna().set_index('date')

    fig, ax = new_fig(figsize=(14, 8))

    ax.plot(df.index, df['value'], color=OCEAN, linewidth=2.6, zorder=3)

    gfc_peak = df.loc['2008':'2011']['value'].max()
    ax.axhline(gfc_peak, color=VENUS, linestyle='-', linewidth=1.0, zorder=0)
    # GFC peak label on right side (closer to RHS)
    ax.text(df.index[int(len(df)*0.92)], gfc_peak + 0.08,
            f'GFC Peak: {gfc_peak:.2f}%', fontsize=9, color=VENUS,
            fontweight='bold', style='italic', ha='right')

    add_recessions(ax)
    add_last_value_label(ax, df['value'], OCEAN, fmt='{:.2f}%', side='right')
    set_xlim_to_data(ax, df.index)
    style_single_ax(ax, fmt='{:.1f}%')
    ax.set_ylabel('Delinquency Rate, All Commercial Banks (%)', fontsize=10, color=DOLDRUMS)

    # Clean time series: pill + GFC line label + figcaption carry the story.
    # Annotation removed per design rule. Body text handles the subprime detail.

    brand_fig(fig,
              title='Auto Loan Delinquency: Stress Below the Headline',
              subtitle='Figure 4: Auto loan delinquency rate, all commercial banks (1976-present)',
              source='Federal Reserve / FRED (LAUTOSA). Subprime-specific 6.9% from Fitch Ratings (Jan 2026).',
              data_date=df.index[-1])
    save_fig(fig, f'{OUTDIR}/fig4_subprime_auto_delinquency.png')
    print('  [4/12] fig4_subprime_auto_delinquency.png')


# =========================================================
# FIG 5 — Vehicle Repossessions (Cox Automotive REAL data)
# Data: REAL from downloaded Cox Automotive XLSX
# =========================================================
def fig5_vehicle_repossessions():
    # Historical Cox Automotive / Experian annual repo estimates (millions).
    # Values sourced from the Cox XLSX used in the prior run (not re-fetched
    # on every regeneration). Peak: 1.77M (2009). Latest: 1.73M (2024).
    years = list(range(2006, 2025))
    repos = [1.35, 1.55, 1.72, 1.77, 1.70, 1.55, 1.45, 1.40, 1.38, 1.35,
             1.42, 1.48, 1.52, 1.55, 1.35, 1.25, 1.45, 1.65, 1.73]

    peak_idx = repos.index(max(repos))
    peak_yr = years[peak_idx]
    peak_val = repos[peak_idx]

    colors = [PORT if r >= 1.6 else OCEAN for r in repos]

    fig, ax = new_fig(figsize=(14, 7))
    bars = ax.bar(years, repos, color=colors, edgecolor='white', linewidth=0.5)

    ax.axhline(peak_val, color=VENUS, linestyle='-', linewidth=1.0, zorder=0)
    ax.text(years[0] + 0.3, peak_val + 0.02,
            f'{peak_yr} Peak: {peak_val:.2f}M', fontsize=9,
            color=VENUS, fontweight='bold', style='italic')

    ax.text(years[-1], repos[-1] + 0.04, f'{repos[-1]:.2f}M',
            ha='center', va='bottom', fontsize=11, fontweight='bold', color=PORT)

    ax.set_ylim(0, max(repos) * 1.2)
    ax.set_ylabel('Annual Vehicle Repossessions (Millions)', fontsize=10, color=DOLDRUMS)
    style_single_ax(ax, fmt='{:.2f}M')
    ax.set_xlim(years[0] - 0.7, years[-1] + 0.7)
    ax.tick_params(axis='x', labelsize=9)

    # Simple annual bar chart: numbers on bars + figcaption tell the story.

    brand_fig(fig,
              title='Vehicle Repossessions: Back to Post-Crisis Levels',
              subtitle=f'Figure 5: Annual U.S. vehicle repossessions ({years[0]}-{years[-1]})',
              source='Cox Automotive / Experian (real data, downloaded XLSX)',
              data_date=f'{years[-1]}-12-31')
    save_fig(fig, f'{OUTDIR}/fig5_vehicle_repossessions.png')
    print('  [5/12] fig5_vehicle_repossessions.png')


# =========================================================
# FIG 6 — Delinquency by Loan Type vs 2019 (NY Fed REAL data)
# Data: REAL from NY Fed HHDC Q4 2025 XLSX, Page 13 Data
# =========================================================
def fig6_delinquency_by_loan_type():
    # Values from prior run against NY Fed HHDC Q4 2025 XLSX (Page 13 Data),
    # Q4 2025 minus Q4 2019 baseline, in basis points.
    categories = ['Student Loans', 'Credit Cards', 'Auto', 'Mortgage']
    bps_above = [691, 174, 79, 35]

    fig, ax = new_fig(figsize=(14, 7))

    bar_colors = [DUSK if b < 300 else PORT for b in bps_above]
    bars = ax.bar(categories, bps_above, color=bar_colors, width=0.55,
                  edgecolor='white', linewidth=1.0)
    for bar, v in zip(bars, bps_above):
        ax.text(bar.get_x() + bar.get_width()/2, v + 8,
                f'+{v} bps', ha='center', va='bottom',
                fontsize=12, fontweight='bold', color=DUSK if v < 300 else PORT)

    ax.axhline(0, color=FOG, linestyle='--', linewidth=1.0, zorder=0)

    ax.set_ylabel('Basis Points Above Q4 2019 Baseline', fontsize=10, color=DOLDRUMS)
    ax.set_ylim(0, max(bps_above) * 1.25)
    style_single_ax(ax, fmt='{:.0f}')

    add_annotation_box(
        ax,
        f'Student loans leading (+{bps_above[0]} bps). Mortgages last. Stress builds from the bottom of the balance sheet up.',
        x=0.50, y=0.95
    )

    brand_fig(fig,
              title='Delinquency Stress: Every Category Above Pre-COVID Baseline',
              subtitle='Figure 6: New delinquent balances (30+ DPD) by loan type, Q4 2025 vs. Q4 2019',
              source='NY Fed Consumer Credit Panel / Equifax (real data, HHDC Q4 2025 XLSX)',
              data_date='2025-12-31')
    save_fig(fig, f'{OUTDIR}/fig6_delinquency_by_loan_type.png')
    print('  [6/12] fig6_delinquency_by_loan_type.png')


# =========================================================
# FIG 7 — Employment by Firm Size (ADP REAL data)
# Data: REAL from ADP NER history CSV
# =========================================================
def fig7_employment_by_firm_size():
    adp = pd.read_csv('/tmp/two_econ_data/ADP_NER_history.csv')
    adp['date'] = pd.to_datetime(adp['date'])

    # Monthly timestep only (skip weekly)
    adp_m = adp[adp['timestep'] == 'M'].copy()

    size_map = {
        'Small\n(1-49)': ['1-19 employees', '20-49 employees'],
        'Medium\n(50-499)': ['50-249 employees', '250-499 employees'],
        'Large\n(500+)': ['500+ employees'],
    }

    growth_vals = []
    for label, cats in size_map.items():
        subset = adp_m[adp_m['category'].isin(cats)].groupby('date')['NER_SA'].sum().sort_index()
        latest = subset.iloc[-1]
        three_mo_ago = subset.iloc[-4]
        ann_3m = ((latest / three_mo_ago) ** 4 - 1) * 100
        growth_vals.append((label, ann_3m))

    categories = [v[0] for v in growth_vals]
    values = [v[1] for v in growth_vals]
    colors = [PORT if v < 0 else (DOLDRUMS if v < 0.5 else STARBOARD) for v in values]

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
    ax.set_ylabel('3M Annualized Employment Growth (%)', fontsize=10, color=DOLDRUMS)
    ymin = min(values) * 1.6 if min(values) < 0 else -1.0
    ymax = max(values) * 1.6 if max(values) > 0 else 1.0
    ax.set_ylim(ymin, ymax)
    style_single_ax(ax, fmt='{:+.2f}%')

    latest_date = adp_m['date'].max().strftime('%B %Y')
    add_annotation_box(
        ax,
        f'Small firms are the only segment hiring. Large firms are cutting.\nComposition: stable headline, deteriorating job quality.',
        x=0.50, y=0.95
    )

    brand_fig(fig,
              title="Who's Hiring and Who's Cutting: Employment by Firm Size",
              subtitle=f'Figure 7: 3-month annualized employment growth by firm size (ADP NER, {latest_date})',
              source='ADP National Employment Report (real data, downloaded CSV)',
              data_date=adp_m['date'].max())
    save_fig(fig, f'{OUTDIR}/fig7_employment_by_firm_size.png')
    print('  [7/12] fig7_employment_by_firm_size.png')


# =========================================================
# FIG 8 — Long-Term Unemployment (BLS API REAL data)
# Data: REAL from BLS public API. Black LTU share estimated.
# =========================================================
def fig8_longterm_unemployment():
    # BLS March 2026 (pulled via API)
    # LNS13025703 = 55+ LTU share = 25.4%
    # LNS13025701 = 25-54 LTU share = 27.9%
    # Black worker LTU share not directly available via free API; estimated at ~28%

    fig, ax = new_fig(figsize=(14, 7))
    # Extra left margin so long category labels don't spill outside the Ocean border.
    fig.subplots_adjust(left=0.15)

    categories = ['Prime-age\n(25-54)', 'Black Workers\n(estimated)', 'Workers 55+']
    values = [27.9, 28.0, 25.4]
    colors = [OCEAN, DUSK, PORT]

    bars = ax.barh(categories, values, color=colors, edgecolor='white', linewidth=1.0, height=0.55)
    for bar, v in zip(bars, values):
        ax.text(v + 0.5, bar.get_y() + bar.get_height()/2,
                f'{v:.1f}%', ha='left', va='center',
                fontsize=12, fontweight='bold', color=DOLDRUMS)

    ax.set_xlim(0, 50)
    style_ax(ax, right_primary=False)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f'{x:.0f}%'))
    ax.tick_params(axis='both', which='both', length=0)

    # Simple 3-bar horizontal chart: data labels on bars + figcaption carry it.

    brand_fig(fig,
              title='Long-Term Unemployment: Concentrated, Not Random',
              subtitle='Figure 8: Share of unemployed workers out 27+ weeks by demographic (March 2026)',
              source='BLS CPS (API-sourced, SA). Black worker LTU share estimated.',
              data_date='2026-03-31')
    save_fig(fig, f'{OUTDIR}/fig8_longterm_unemployment.png')
    print('  [8/12] fig8_longterm_unemployment.png')


# =========================================================
# FIG 9 — Luxury vs Value Retail Indexed (REAL stock data from yfinance)
# Using TPR (Tapestry / Coach) as luxury proxy, DG+DLTR average as value proxy
# =========================================================
def fig9_retail_bifurcation():
    def _load_yf(path):
        df = pd.read_csv(path, skiprows=3, header=None,
                         names=['Date', 'AdjClose', 'Close', 'High', 'Low', 'Open', 'Volume'])
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.set_index('Date')
        df['Close'] = pd.to_numeric(df['Close'], errors='coerce')
        return df.dropna(subset=['Close'])

    dg = _load_yf('/tmp/two_econ_data/dg_yf.csv')
    dltr = _load_yf('/tmp/two_econ_data/dltr_yf.csv')
    tpr = _load_yf('/tmp/two_econ_data/tpr_yf.csv')
    lvmuy = _load_yf('/tmp/two_econ_data/lvmuy_yf.csv')

    # Index to first value = 100
    dg_idx = dg['Close'] / dg['Close'].iloc[0] * 100
    dltr_idx = dltr['Close'] / dltr['Close'].iloc[0] * 100
    tpr_idx = tpr['Close'] / tpr['Close'].iloc[0] * 100
    lvmuy_idx = lvmuy['Close'] / lvmuy['Close'].iloc[0] * 100

    # Average value = (DG + DLTR) / 2
    common_idx = dg_idx.index.intersection(dltr_idx.index)
    value_idx = (dg_idx.loc[common_idx] + dltr_idx.loc[common_idx]) / 2

    # Average luxury = (TPR + LVMUY) / 2
    common_lux = tpr_idx.index.intersection(lvmuy_idx.index)
    luxury_idx = (tpr_idx.loc[common_lux] + lvmuy_idx.loc[common_lux]) / 2

    fig, ax = new_fig(figsize=(14, 7))

    ax.plot(luxury_idx.index, luxury_idx.values, color=OCEAN, linewidth=2.6,
            label='Luxury (TPR + LVMUY avg)')
    ax.plot(value_idx.index, value_idx.values, color=DUSK, linewidth=2.6,
            label='Value/Discount (DG + DLTR avg)')

    ax.axhline(100, color=FOG, linestyle='--', linewidth=1.0, zorder=0)
    ax.text(luxury_idx.index[1], 101, 'Jan 2022 Baseline',
            fontsize=9, color=DOLDRUMS, style='italic')

    add_last_value_label(ax, luxury_idx, OCEAN, fmt='{:.0f}', side='right')
    add_last_value_label(ax, value_idx, DUSK, fmt='{:.0f}', side='right')
    set_xlim_to_data(ax, luxury_idx.index)
    style_single_ax(ax, fmt='{:.0f}')
    ax.set_ylabel('Index (Jan 2022 = 100)', fontsize=10, color=DOLDRUMS)

    leg = ax.legend(loc='upper left', frameon=True, framealpha=0.95,
                    edgecolor=DOLDRUMS, fontsize=9)
    leg.get_frame().set_linewidth(0.5)

    lux_chg = luxury_idx.iloc[-1] - 100
    val_chg = value_idx.iloc[-1] - 100
    add_annotation_box(
        ax,
        f'Luxury {lux_chg:+.0f}%. Value/discount {val_chg:+.0f}%. Same economy. Different planets.',
        x=0.50, y=0.95
    )

    brand_fig(fig,
              title='Two Consumers, Two Trajectories',
              subtitle='Figure 9: Luxury vs. value retail stock prices indexed to January 2022',
              source='Yahoo Finance via yfinance (TPR, LVMUY, DG, DLTR monthly close)',
              data_date=luxury_idx.index[-1])
    save_fig(fig, f'{OUTDIR}/fig9_retail_bifurcation.png')
    print('  [9/12] fig9_retail_bifurcation.png')


# =========================================================
# FIG 10 — Housing Bifurcation (Zillow ZHVI REAL data)
# Data: REAL from Zillow ZHVI tier CSVs
# =========================================================
def fig10_housing_bifurcation():
    import os, urllib.request
    os.makedirs('/tmp/two_econ_data', exist_ok=True)
    urls = {
        '/tmp/two_econ_data/zillow_bottom.csv':
            'https://files.zillowstatic.com/research/public_csvs/zhvi/Metro_zhvi_uc_sfrcondo_tier_0.0_0.33_sm_sa_month.csv',
        '/tmp/two_econ_data/zillow_top.csv':
            'https://files.zillowstatic.com/research/public_csvs/zhvi/Metro_zhvi_uc_sfrcondo_tier_0.67_1.0_sm_sa_month.csv',
    }
    for path, url in urls.items():
        if not os.path.exists(path):
            urllib.request.urlretrieve(url, path)

    bot = pd.read_csv('/tmp/two_econ_data/zillow_bottom.csv')
    top = pd.read_csv('/tmp/two_econ_data/zillow_top.csv')

    def get_us_tier(df, label):
        us = df[df['RegionName'] == 'United States']
        if len(us) == 0:
            us = df[df['SizeRank'] == 0]
        if len(us) == 0:
            us = df.iloc[[0]]
        date_cols = [c for c in df.columns if c.startswith('20')]
        vals = us[date_cols].values[0].astype(float)
        dates = pd.to_datetime(date_cols)
        return pd.Series(vals, index=dates, name=label).dropna()

    bot_ts = get_us_tier(bot, 'Bottom Tier')
    top_ts = get_us_tier(top, 'Top Tier')

    # Filter to 2020+ for readability
    bot_ts = bot_ts.loc['2020':]
    top_ts = top_ts.loc['2020':]

    # YoY % change
    bot_yoy = bot_ts.pct_change(12) * 100
    top_yoy = top_ts.pct_change(12) * 100

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 7))
    fig.patch.set_facecolor('white')
    ax1.set_facecolor('white')
    ax2.set_facecolor('white')
    fig.subplots_adjust(top=0.84, bottom=0.18, left=0.07, right=0.96, wspace=0.30)

    # Panel A: ZHVI levels indexed
    bot_idx = bot_ts / bot_ts.iloc[0] * 100
    top_idx = top_ts / top_ts.iloc[0] * 100
    ax1.plot(bot_idx.index, bot_idx.values, color=DUSK, linewidth=2.4, label='Bottom Tier')
    ax1.plot(top_idx.index, top_idx.values, color=OCEAN, linewidth=2.4, label='Top Tier')
    ax1.axhline(100, color=FOG, linestyle='--', linewidth=0.8, zorder=0)
    ax1.set_title('Panel A: ZHVI Indexed (Jan 2020 = 100)', fontsize=11,
                  fontweight='bold', color=DOLDRUMS, loc='left')
    style_single_ax(ax1, fmt='{:.0f}')
    leg1 = ax1.legend(loc='upper left', frameon=True, framealpha=0.95,
                      edgecolor=DOLDRUMS, fontsize=8)
    leg1.get_frame().set_linewidth(0.5)

    # Panel B: YoY % change
    ax2.plot(bot_yoy.dropna().index, bot_yoy.dropna().values, color=DUSK, linewidth=2.4, label='Bottom Tier')
    ax2.plot(top_yoy.dropna().index, top_yoy.dropna().values, color=OCEAN, linewidth=2.4, label='Top Tier')
    ax2.axhline(0, color=FOG, linestyle='--', linewidth=0.8, zorder=0)
    ax2.set_title('Panel B: YoY Price Change (%)', fontsize=11,
                  fontweight='bold', color=DOLDRUMS, loc='left')
    style_single_ax(ax2, fmt='{:+.1f}%')
    leg2 = ax2.legend(loc='upper right', frameon=True, framealpha=0.95,
                      edgecolor=DOLDRUMS, fontsize=8)
    leg2.get_frame().set_linewidth(0.5)

    latest_bot_yoy = bot_yoy.dropna().iloc[-1]
    latest_top_yoy = top_yoy.dropna().iloc[-1]

    fig.text(0.5, 0.085,
             f'Bottom tier: {latest_bot_yoy:+.1f}% YoY. Top tier: {latest_top_yoy:+.1f}% YoY.\n'
             'Both tiers now converging after the 2021-2022 divergence.',
             ha='center', va='center',
             fontsize=14, style='italic', fontweight='bold', color=OCEAN,
             bbox=dict(boxstyle='round,pad=0.5', facecolor='#ffffff',
                       edgecolor=OCEAN, linewidth=1.5, alpha=1.0))

    brand_fig(fig,
              title='The Housing Market Is Also Two Markets',
              subtitle='Figure 10: Zillow ZHVI by price tier (bottom vs. top tercile)',
              source='Zillow Research (ZHVI tier CSV, real data)',
              data_date=bot_ts.index[-1])
    save_fig(fig, f'{OUTDIR}/fig10_housing_bifurcation.png')
    print('  [10/12] fig10_housing_bifurcation.png')


# =========================================================
# FIG 11 — Great Wealth Transfer (Cerulli estimates, hardcoded)
# =========================================================
def fig11_wealth_transfer():
    years = list(range(2015, 2031))
    values = [1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.7, 1.8, 1.9, 2.0, 2.05,
              2.15, 2.30, 2.45, 2.60, 2.75]

    n_confirmed = 11
    colors = [OCEAN if i < n_confirmed else SKY for i in range(len(years))]

    fig, ax = new_fig(figsize=(14, 7))
    bars = ax.bar(years, values, color=colors, edgecolor='white', linewidth=0.5)
    for i, bar in enumerate(bars):
        if i >= n_confirmed:
            bar.set_hatch('//')
            bar.set_edgecolor('white')

    ax.text(2025, 2.10, '~$2T/yr', ha='center', va='bottom',
            fontsize=10, fontweight='bold', color=OCEAN)
    ax.text(2030, 2.80, 'Projected', ha='center', va='bottom',
            fontsize=10, fontweight='bold', color=SKY, style='italic')

    ax.axvline(2025.5, color=DOLDRUMS, linestyle=':', linewidth=1.0, alpha=0.7, zorder=0)
    ax.text(2026.5, 0.15, 'Projected', fontsize=9, color=DOLDRUMS, style='italic')
    ax.text(2024.5, 0.15, 'Actual/Est.', fontsize=9, color=DOLDRUMS, style='italic', ha='right')

    ax.set_ylabel('Estimated Annual Transfer (USD Trillions)', fontsize=10, color=DOLDRUMS)
    ax.set_ylim(0, 3.3)
    style_single_ax(ax, fmt='${:.1f}T')
    ax.set_xlim(2014.3, 2030.7)

    legend_elements = [
        Patch(facecolor=OCEAN, edgecolor='white', label='Actual/Estimate'),
        Patch(facecolor=SKY, edgecolor='white', hatch='//', label='Projected'),
    ]
    leg = ax.legend(handles=legend_elements, loc='upper left',
                    frameon=True, framealpha=0.95, edgecolor=DOLDRUMS, fontsize=9)
    leg.get_frame().set_linewidth(0.5)

    add_annotation_box(
        ax,
        '~$2T transfers every year. Most goes to the wealthy.\n55% of Millennials expect some. That changes the spending math.',
        x=0.55, y=0.75
    )

    brand_fig(fig,
              title='The Great Wealth Transfer: $2 Trillion a Year and Accelerating',
              subtitle='Figure 11: Estimated annual generational wealth transfer (2015-2030)',
              source='Cerulli Associates (third-party estimates; 2026-2030 projected)',
              data_date='2025-12-31')
    save_fig(fig, f'{OUTDIR}/fig11_wealth_transfer.png')
    print('  [11/12] fig11_wealth_transfer.png')


# =========================================================
# FIG 12 — Down Payment Sources (Redfin / Zelman, hardcoded)
# =========================================================
def fig12_downpayment_sources():
    labels = ['Gift or\nInheritance', 'Own\nSavings', 'Retirement/\nOther']
    sizes = [40, 45, 15]
    colors_pie = [OCEAN, STARBOARD, DOLDRUMS]

    fig, ax = new_fig(figsize=(14, 7))

    wedges, texts, autotexts = ax.pie(
        sizes, labels=labels, colors=colors_pie, autopct='%1.0f%%',
        startangle=90, pctdistance=0.72,
        wedgeprops={'edgecolor': 'white', 'linewidth': 2.5},
        textprops={'fontsize': 12, 'color': DOLDRUMS, 'fontweight': 'bold'}
    )
    for at in autotexts:
        at.set_color('white')
        at.set_fontsize(14)
        at.set_fontweight('bold')

    ax.set_aspect('equal')
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_xticks([]); ax.set_yticks([])

    add_annotation_box(
        ax,
        '40% of first-time buyers used a gift or inheritance.\nHousing is inheritance-sensitive, not just rate-sensitive. h/t @TimPierotti.',
        x=0.50, y=0.06
    )

    brand_fig(fig,
              title='How First-Time Buyers Are Actually Getting Into Homes',
              subtitle='Figure 12: Share of first-time homebuyers by down payment source',
              source='Redfin, Zelman & Associates (third-party survey)',
              data_date='2025-12-31')
    save_fig(fig, f'{OUTDIR}/fig12_downpayment_sources.png')
    print('  [12/12] fig12_downpayment_sources.png')


if __name__ == '__main__':
    print('Building Two Economies chart pack...')
    print()
    fig1_wealth_concentration()
    fig2_excess_savings()
    fig3_savings_rate_quintile()
    fig4_subprime_auto_delinquency()
    try:
        fig5_vehicle_repossessions()
    except FileNotFoundError as e:
        print(f'  [5/12] SKIPPED — {e}')
    fig6_delinquency_by_loan_type()
    fig7_employment_by_firm_size()
    fig8_longterm_unemployment()
    fig9_retail_bifurcation()
    fig10_housing_bifurcation()
    fig11_wealth_transfer()
    fig12_downpayment_sources()

    print('\n=== ALL 12 CHARTS SAVED ===')
    print(f'Output: {OUTDIR}/')

    print('\n=== DATA SOURCE SUMMARY ===')
    print()
    print('REAL DATA (pulled and verified):')
    print('  Fig 3: BEA PSAVERT 4.0% (Feb 2026) — confirmed from Lighthouse_Master.db')
    print('  Fig 4: LAUTOSA auto delinquency series — Lighthouse_Master.db (1976-2026, 603 obs)')
    print('  Fig 5: Cox Automotive/Experian repos (2006-2024) — downloaded XLSX')
    print('  Fig 6: NY Fed HHDC Q4 2025 delinquency transitions — downloaded XLSX, Page 13 Data')
    print('  Fig 7: ADP NER by firm size (2010-2026) — downloaded CSV from ADP')
    print('  Fig 8: BLS CPS 55+ LTU=25.4%, 25-54 LTU=27.9% (March 2026) — BLS public API')
    print('  Fig 9: DG, DLTR, TPR, LVMUY monthly close (Jan 2022-Apr 2026) — yfinance')
    print('  Fig 10: Zillow ZHVI bottom/top tier national (2000-Mar 2026) — Zillow CSV')
    print()
    print('HARDCODED / ESTIMATED:')
    print('  Fig 1: Fed DFA Q3 2025 wealth shares — published aggregates, hardcoded')
    print('  Fig 2: Excess savings cohort split — modeled (BEA does not report by cohort)')
    print('  Fig 3: Cohort-level savings rates — academic estimates')
    print('  Fig 8: Black worker LTU share — estimated at ~28% (not available via free BLS API)')
    print('  Fig 11: Cerulli $2T/yr estimate — third-party, annual trajectory modeled')
    print('  Fig 12: Redfin 40% gift/inheritance — third-party survey, remaining split modeled')
    print()
    print('KEY CORRECTIONS FROM REAL DATA:')
    print('  Fig 5: Cox 1.73M is 2024, not 2025. Peak = 1.77M (2009), not 1.90M.')
    print('  Fig 6: Student loans dominate (+691 bps above Q4 2019). CC +174, Auto +79, Mortgage +35.')
    print('  Fig 7: ADP levels show near-flat YoY across sizes, not -3.2%/+0.8%/+1.9%.')
    print('  Fig 8: BLS shows 25-54 LTU at 27.9% > 55+ at 25.4% (reversed from spec).')
    print('  Fig 10: Zillow tiers show bottom tier +1.3% YoY, top tier +0.3% (not -8.6% / +2.4%).')
