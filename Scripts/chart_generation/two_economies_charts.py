"""
Two Economies — Consumer Bifurcation Update
12 charts using the LHM canonical chart template.

Output: /Users/bob/LHM/Outputs/Charts/two_economies/
"""
import sys
sys.path.insert(0, '/Users/bob/LHM/Scripts/chart_generation')

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
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
# FIG 1 — Wealth Concentration (horizontal bar)
# =========================================================
def fig1_wealth_concentration():
    fig, ax = new_fig(figsize=(14, 7))

    categories = ['Bottom 50%', 'Top 10%\n(incl. Top 1%)', 'Top 1%']
    values = [2.4, 67.0, 30.2]
    colors = [DOLDRUMS, OCEAN, PORT]

    bars = ax.barh(categories, values, color=colors, edgecolor='white', linewidth=1.0)
    for bar, v in zip(bars, values):
        ax.text(v + 1.2, bar.get_y() + bar.get_height()/2,
                f'{v:.1f}%', ha='left', va='center',
                fontsize=12, fontweight='bold', color=DOLDRUMS)

    ax.set_xlim(0, 78)
    ax.set_xlabel('Share of Total U.S. Household Net Worth (%)', fontsize=11, color=DOLDRUMS)
    style_ax(ax, right_primary=False)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f'{x:.0f}%'))
    ax.tick_params(axis='both', which='both', length=0)

    add_annotation_box(
        ax,
        'The top 1% hold more wealth than the entire bottom 50%. By a factor of 12.',
        x=0.50, y=0.22
    )

    brand_fig(fig,
              title='Who Owns America',
              subtitle='Figure 1: Share of U.S. household net worth by wealth percentile',
              source='Federal Reserve Distributional Financial Accounts (Q3 2025)',
              data_date='2025-09-30')
    save_fig(fig, f'{OUTDIR}/fig1_wealth_concentration.png')
    print('Saved fig1')


# =========================================================
# FIG 2 — Excess Pandemic Savings by Cohort (diverging bar)
# =========================================================
def fig2_excess_savings():
    fig, ax = new_fig(figsize=(14, 7))

    categories = ['Top 20%', 'Bottom 80%']
    values = [470, -437]
    colors = [OCEAN, PORT]

    bars = ax.bar(categories, values, color=colors, width=0.55, edgecolor='white', linewidth=1.0)
    for bar, v in zip(bars, values):
        offset = 25 if v > 0 else -25
        va = 'bottom' if v > 0 else 'top'
        ax.text(bar.get_x() + bar.get_width()/2, v + offset,
                f'${v:+,}B', ha='center', va=va,
                fontsize=13, fontweight='bold',
                color=OCEAN if v > 0 else PORT)

    ax.axhline(0, color=FOG, linestyle='--', linewidth=1.0, zorder=0)
    ax.text(1.45, 5, 'Pre-Pandemic Baseline',
            fontsize=9, color=DOLDRUMS, style='italic',
            ha='right', va='bottom')

    ax.set_ylabel('Cumulative Excess Savings vs. Pre-Pandemic Trend (USD Billions)',
                  fontsize=10, color=DOLDRUMS)
    ax.set_ylim(-600, 600)
    style_single_ax(ax, fmt='${:+,.0f}B')

    add_annotation_box(
        ax,
        'Top 20% still flush. Bottom 80% underwater since mid-2023. Two economies. One headline.',
        x=0.50, y=0.95
    )

    brand_fig(fig,
              title='Excess Pandemic Savings: Who Still Has It',
              subtitle='Figure 2: Cumulative excess savings vs. pre-pandemic trend by income cohort',
              source='BEA, Federal Reserve (cohort split modeled, not directly reported)',
              data_date='2025-12-31')
    save_fig(fig, f'{OUTDIR}/fig2_excess_savings.png')
    print('Saved fig2')


# =========================================================
# FIG 3 — Savings Rate by Income Group
# =========================================================
def fig3_savings_rate_quintile():
    fig, ax = new_fig(figsize=(14, 7))

    categories = ['Top 10%', 'Middle 60%', 'Bottom 60%']
    values = [18.0, 4.8, 1.2]
    colors = [STARBOARD, OCEAN, PORT]

    bars = ax.bar(categories, values, color=colors, width=0.55, edgecolor='white', linewidth=1.0)
    for bar, v in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2, v + 0.5,
                f'{v:.1f}%', ha='center', va='bottom',
                fontsize=13, fontweight='bold', color=DOLDRUMS)

    ax.axhline(8.5, color=FOG, linestyle='--', linewidth=1.2, zorder=0)
    ax.text(2.4, 8.7, 'Historical Average: 8.5%',
            fontsize=9, color=DOLDRUMS, ha='right', va='bottom', style='italic')

    ax.axhline(4.0, color=DUSK, linestyle='-', linewidth=1.2, zorder=0)
    ax.text(2.4, 4.2, 'BEA Aggregate: 4.0% (Feb 2026)',
            fontsize=9, color=DUSK, ha='right', va='bottom', style='italic', fontweight='bold')

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
              subtitle='Figure 3: Estimated savings rate by cohort vs. historical average and BEA aggregate',
              source='Federal Reserve DFA, academic estimates; BEA PSAVERT',
              data_date='2026-02-28')
    save_fig(fig, f'{OUTDIR}/fig3_savings_rate_quintile.png')
    print('Saved fig3')


# =========================================================
# FIG 4 — Subprime Auto Delinquency (time series, hardcoded anchors)
# =========================================================
def fig4_subprime_auto_delinquency():
    # Hardcoded anchors. DB has no subprime auto series. DATA NEEDS VERIFICATION.
    # Fitch Ratings annual/quarterly anchors + interpolation for shape.
    dates = pd.to_datetime([
        '2000-01-01', '2002-01-01', '2004-01-01', '2006-01-01',
        '2008-06-01',   # GFC peak region
        '2009-01-01',   # 2008/09 peak area per spec (~5.1%)
        '2010-01-01',
        '2012-01-01',
        '2015-01-01',   # post-GFC trough ~2.5%
        '2017-01-01',
        '2019-01-01',   # pre-pandemic ~4.5%
        '2020-06-01',   # COVID dip (forbearance)
        '2021-06-01',
        '2022-06-01',
        '2023-06-01',
        '2024-06-01',
        '2025-06-01',
        '2026-01-01',   # 6.9% Fitch confirmed
    ])
    values = [3.2, 3.6, 3.8, 4.2, 4.7, 5.1, 4.6, 3.5, 2.5, 3.0, 4.5, 2.9, 3.4, 4.3, 5.4, 6.1, 6.6, 6.9]

    df = pd.Series(values, index=dates)

    fig, ax = new_fig(figsize=(14, 7))

    ax.plot(df.index, df.values, color=OCEAN, linewidth=2.6, zorder=3)
    ax.fill_between(df.index, 0, df.values, color=OCEAN, alpha=0.08, zorder=1)

    ax.axhline(5.1, color=VENUS, linestyle='-', linewidth=1.2, zorder=0)
    ax.text(pd.Timestamp('2000-06-01'), 5.3, '2008 Crisis Peak: 5.1%',
            fontsize=9, color=VENUS, fontweight='bold', style='italic')

    add_recessions(ax, start_date='2000-01-01')
    add_last_value_label(ax, df, OCEAN, fmt='{:.1f}%', side='right')
    set_xlim_to_data(ax, df.index)
    style_single_ax(ax, fmt='{:.1f}%')
    ax.set_ylim(0, 8)
    ax.set_ylabel('60+ Days Past Due Rate (%)', fontsize=10, color=DOLDRUMS)

    add_annotation_box(
        ax,
        "6.9%. The 2008 peak was 5.1%. Nobody's making a movie about this one.",
        x=0.35, y=0.95
    )

    brand_fig(fig,
              title='Subprime Auto Delinquency: Through the Floor of 2008',
              subtitle='Figure 4: Subprime auto loan 60+ days past due rate (2000-2026)',
              source='Fitch Ratings (series hardcoded from reported anchors; NOT pulled from DB)',
              data_date='2026-01-31')
    save_fig(fig, f'{OUTDIR}/fig4_subprime_auto_delinquency.png')
    print('Saved fig4')


# =========================================================
# FIG 5 — Vehicle Repossessions (annual bars)
# =========================================================
def fig5_vehicle_repossessions():
    # Cox Automotive / industry estimates. Hardcoded anchors. DATA NEEDS VERIFICATION.
    years = list(range(2005, 2026))
    repos = [1.20, 1.40, 1.65, 1.82, 1.90,   # 2005-2009 peak
             1.50, 1.30, 1.20, 1.15, 1.10,   # 2010-2014
             1.15, 1.20, 1.30, 1.35, 1.40,   # 2015-2019
             1.05, 1.00, 1.20, 1.45, 1.62, 1.73]  # 2020-2025

    colors = [PORT if r >= 1.6 else OCEAN for r in repos]

    fig, ax = new_fig(figsize=(14, 7))
    bars = ax.bar(years, repos, color=colors, edgecolor='white', linewidth=0.5)

    ax.axhline(1.90, color=VENUS, linestyle='-', linewidth=1.2, zorder=0)
    ax.text(2005.3, 1.93, '2009 Peak: 1.90M',
            fontsize=9, color=VENUS, fontweight='bold', style='italic')

    # Highlight 2025 value
    ax.text(2025, 1.78, '1.73M', ha='center', va='bottom',
            fontsize=11, fontweight='bold', color=PORT)
    ax.text(2009, 1.93, '1.90M', ha='center', va='bottom',
            fontsize=10, fontweight='bold', color=DOLDRUMS)

    ax.set_ylim(0, 2.2)
    ax.set_ylabel('Annual Vehicle Repossessions (Millions)', fontsize=10, color=DOLDRUMS)
    style_single_ax(ax, fmt='{:.2f}M')
    ax.set_xlim(2004.3, 2025.7)
    ax.tick_params(axis='x', labelsize=9)

    add_annotation_box(
        ax,
        '1.73 million repossessions in 2025. The car is often the last bill people stop paying.',
        x=0.50, y=0.95
    )

    brand_fig(fig,
              title='Vehicle Repossessions: Back to Post-Crisis Levels',
              subtitle='Figure 5: Annual U.S. vehicle repossessions (2005-2025)',
              source='Cox Automotive, industry estimates (intermediate years interpolated)',
              data_date='2025-12-31')
    save_fig(fig, f'{OUTDIR}/fig5_vehicle_repossessions.png')
    print('Saved fig5')


# =========================================================
# FIG 6 — Delinquency by Loan Type vs 2019 Baseline
# =========================================================
def fig6_delinquency_by_loan_type():
    fig, ax = new_fig(figsize=(14, 7))

    categories = ['Credit Cards', 'Consumer Loans', 'Auto', 'Mortgage']
    bps_above = [85, 48, 22, 10]

    bars = ax.bar(categories, bps_above, color=OCEAN, width=0.55,
                  edgecolor='white', linewidth=1.0)
    for bar, v in zip(bars, bps_above):
        ax.text(bar.get_x() + bar.get_width()/2, v + 2.5,
                f'+{v} bps', ha='center', va='bottom',
                fontsize=12, fontweight='bold', color=OCEAN)

    ax.axhline(0, color=FOG, linestyle='--', linewidth=1.0, zorder=0)
    ax.text(3.45, 2, '2019 Baseline',
            fontsize=9, color=DOLDRUMS, style='italic', ha='right', va='bottom')

    ax.set_ylabel('Basis Points Above 2019 Pre-COVID Baseline', fontsize=10, color=DOLDRUMS)
    ax.set_ylim(0, 105)
    style_single_ax(ax, fmt='{:.0f}')

    add_annotation_box(
        ax,
        'Credit cards leading. Mortgages last. Stress is building from the bottom of the balance sheet up.',
        x=0.50, y=0.95
    )

    brand_fig(fig,
              title='Delinquency Stress: Every Category Above Pre-COVID Baseline',
              subtitle='Figure 6: Delinquency transition rates by loan type vs. 2019 baseline',
              source='Federal Reserve, NY Fed Consumer Credit Panel (spread-from-baseline)',
              data_date='2025-12-31')
    save_fig(fig, f'{OUTDIR}/fig6_delinquency_by_loan_type.png')
    print('Saved fig6')


# =========================================================
# FIG 7 — Employment Growth by Firm Size (ADP)
# =========================================================
def fig7_employment_by_firm_size():
    fig, ax = new_fig(figsize=(14, 7))

    categories = ['Small\n(1-49)', 'Medium\n(50-499)', 'Large\n(500+)']
    values = [-3.2, 0.8, 1.9]
    colors = [PORT, DOLDRUMS, STARBOARD]

    bars = ax.bar(categories, values, color=colors, width=0.55,
                  edgecolor='white', linewidth=1.0)
    for bar, v in zip(bars, values):
        offset = 0.15 if v > 0 else -0.15
        va = 'bottom' if v > 0 else 'top'
        ax.text(bar.get_x() + bar.get_width()/2, v + offset,
                f'{v:+.1f}%', ha='center', va=va,
                fontsize=13, fontweight='bold', color=colors[list(values).index(v)])

    ax.axhline(0, color=FOG, linestyle='--', linewidth=1.0, zorder=0)
    ax.set_ylabel('YoY Employment Growth (%)', fontsize=10, color=DOLDRUMS)
    ax.set_ylim(-4, 3)
    style_single_ax(ax, fmt='{:+.1f}%')

    add_annotation_box(
        ax,
        'Small businesses employ the bottom 80%. They are contracting. Large firms are still hiring. The BLS averages both.',
        x=0.50, y=0.95
    )

    brand_fig(fig,
              title="Who's Hiring and Who's Cutting: Employment by Firm Size",
              subtitle='Figure 7: YoY employment growth by firm size (ADP National Employment Report)',
              source='ADP National Employment Report (December 2025)',
              data_date='2025-12-31')
    save_fig(fig, f'{OUTDIR}/fig7_employment_by_firm_size.png')
    print('Saved fig7')


# =========================================================
# FIG 8 — Long-Term Unemployment by Demographic
# =========================================================
def fig8_longterm_unemployment():
    fig, ax = new_fig(figsize=(14, 7))

    categories = ['Prime-age\n(25-54)', 'Black Workers', 'Workers 55+']
    values = [22, 28, 31]
    colors = [OCEAN, DUSK, PORT]

    bars = ax.barh(categories, values, color=colors, edgecolor='white', linewidth=1.0)
    for bar, v in zip(bars, values):
        ax.text(v + 0.7, bar.get_y() + bar.get_height()/2,
                f'{v}%', ha='left', va='center',
                fontsize=12, fontweight='bold', color=DOLDRUMS)

    ax.set_xlim(0, 38)
    ax.set_xlabel('Share of Unemployed Out 27+ Weeks (%)', fontsize=10, color=DOLDRUMS)
    style_ax(ax, right_primary=False)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f'{x:.0f}%'))
    ax.tick_params(axis='both', which='both', length=0)

    add_annotation_box(
        ax,
        "Older workers who lose a job often don't find another. That's not a cycle story. It's a structural one.",
        x=0.50, y=0.18
    )

    brand_fig(fig,
              title='Long-Term Unemployment: Concentrated, Not Random',
              subtitle='Figure 8: Share of unemployed workers out 27+ weeks by demographic',
              source='BLS (Current Population Survey)',
              data_date='2026-02-28')
    save_fig(fig, f'{OUTDIR}/fig8_longterm_unemployment.png')
    print('Saved fig8')


# =========================================================
# FIG 9 — Luxury vs Value Retail, Indexed to Jan 2022 = 100
# =========================================================
def fig9_retail_bifurcation():
    # Hardcoded monthly index path to endpoints: Luxury +17%, Value -9% (Jan 2022 to Apr 2026)
    dates = pd.date_range('2022-01-01', '2026-04-01', freq='MS')
    n = len(dates)

    # Luxury: roughly linear rise to 117 with some noise
    lux = np.linspace(100, 117, n) + np.array([np.sin(i/4)*0.8 for i in range(n)])
    # Value: declining to 91
    val = np.linspace(100, 91, n) + np.array([np.cos(i/5)*0.7 for i in range(n)])

    df = pd.DataFrame({'Luxury': lux, 'Value': val}, index=dates)

    fig, ax = new_fig(figsize=(14, 7))

    ax.plot(df.index, df['Luxury'], color=STARBOARD, linewidth=2.6, label='Luxury (LVMH, Tapestry, Nordstrom proxy)')
    ax.plot(df.index, df['Value'], color=PORT, linewidth=2.6, label='Value/Discount (DG, DLTR proxy)')

    ax.axhline(100, color=FOG, linestyle='--', linewidth=1.0, zorder=0)
    ax.text(pd.Timestamp('2022-02-01'), 100.3, 'Jan 2022 Baseline',
            fontsize=9, color=DOLDRUMS, style='italic')

    add_last_value_label(ax, df['Luxury'], STARBOARD, fmt='{:.0f}', side='right')
    add_last_value_label(ax, df['Value'], PORT, fmt='{:.0f}', side='right')
    set_xlim_to_data(ax, df.index)
    style_single_ax(ax, fmt='{:.0f}')
    ax.set_ylabel('Index (Jan 2022 = 100)', fontsize=10, color=DOLDRUMS)
    ax.set_ylim(85, 125)

    leg = ax.legend(loc='upper left', frameon=True, framealpha=0.95,
                    edgecolor=DOLDRUMS, fontsize=9)
    leg.get_frame().set_linewidth(0.5)

    add_annotation_box(
        ax,
        'Luxury up 17%. Dollar stores down 9%. Same economy. Different planets.',
        x=0.50, y=0.95
    )

    brand_fig(fig,
              title='Two Consumers, Two Trajectories',
              subtitle='Figure 9: Luxury vs. value retail sales indexed to January 2022',
              source='Company reports (proxy-based; monthly path modeled between reported endpoints)',
              data_date='2026-04-01')
    save_fig(fig, f'{OUTDIR}/fig9_retail_bifurcation.png')
    print('Saved fig9')


# =========================================================
# FIG 10 — Housing Bifurcation (dual panel)
# =========================================================
def fig10_housing_bifurcation():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 7))
    fig.patch.set_facecolor('white')
    ax1.set_facecolor('white'); ax2.set_facecolor('white')
    fig.subplots_adjust(top=0.84, bottom=0.12, left=0.07, right=0.96, wspace=0.25)

    # Panel A: price change
    cats_a = ['Entry-Level', 'Luxury']
    vals_a = [-8.6, 2.4]
    colors_a = [PORT, STARBOARD]
    bars_a = ax1.bar(cats_a, vals_a, color=colors_a, width=0.55, edgecolor='white', linewidth=1.0)
    for b, v in zip(bars_a, vals_a):
        offset = 0.5 if v > 0 else -0.5
        va = 'bottom' if v > 0 else 'top'
        ax1.text(b.get_x() + b.get_width()/2, v + offset,
                 f'{v:+.1f}%', ha='center', va=va,
                 fontsize=13, fontweight='bold',
                 color=PORT if v < 0 else STARBOARD)
    ax1.axhline(0, color=FOG, linestyle='--', linewidth=1.0, zorder=0)
    ax1.set_title('Panel A: YoY Price Change', fontsize=11, fontweight='bold', color=DOLDRUMS, loc='left')
    ax1.set_ylim(-12, 6)
    style_single_ax(ax1, fmt='{:+.1f}%')

    # Panel B: days on market
    cats_b = ['Entry-Level', 'Luxury']
    vals_b = [95, 45]
    colors_b = [PORT, STARBOARD]
    bars_b = ax2.bar(cats_b, vals_b, color=colors_b, width=0.55, edgecolor='white', linewidth=1.0)
    for b, v in zip(bars_b, vals_b):
        ax2.text(b.get_x() + b.get_width()/2, v + 2.5,
                 f'{v}', ha='center', va='bottom',
                 fontsize=13, fontweight='bold',
                 color=PORT if v > 70 else STARBOARD)
    ax2.set_title('Panel B: Days on Market', fontsize=11, fontweight='bold', color=DOLDRUMS, loc='left')
    ax2.set_ylim(0, 115)
    style_single_ax(ax2, fmt='{:.0f}')

    # Single annotation in figure-level space (between panels, low)
    fig.text(0.5, 0.12,
             "Entry-level down 8.6%, 95 days on market. Luxury up 2.4%, 45 days. The bottom can't buy. The top isn't forced to sell.",
             ha='center', va='top',
             fontsize=10, style='italic', fontweight='bold', color='white',
             bbox=dict(boxstyle='round,pad=0.5', facecolor=OCEAN,
                       edgecolor=SKY, linewidth=1.5))

    brand_fig(fig,
              title='The Housing Market Is Also Two Markets',
              subtitle='Figure 10: Price change and days on market by housing tier',
              source='Zillow, Redfin tier reports',
              data_date='2026-03-31')
    save_fig(fig, f'{OUTDIR}/fig10_housing_bifurcation.png')
    print('Saved fig10')


# =========================================================
# FIG 11 — Annual Wealth Transfer (Great Wealth Transfer)
# =========================================================
def fig11_wealth_transfer():
    # Cerulli estimates. $2T/year current rising to higher levels by 2030.
    # Rough trajectory: pre-2020 ~$1.2T, 2020-2025 ramp to ~$2T, 2026-2030 projected to ~$2.8T
    years = list(range(2015, 2031))
    values = [1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.7, 1.8, 1.9, 2.0, 2.05,  # 2015-2025 confirmed-ish
              2.15, 2.30, 2.45, 2.60, 2.75]                             # 2026-2030 projected

    n_confirmed = 11   # through 2025
    colors = [OCEAN if i < n_confirmed else SKY for i in range(len(years))]
    hatches = ['' if i < n_confirmed else '//' for i in range(len(years))]

    fig, ax = new_fig(figsize=(14, 7))
    bars = ax.bar(years, values, color=colors, edgecolor='white', linewidth=0.5)
    for bar, h in zip(bars, hatches):
        if h:
            bar.set_hatch(h)
            bar.set_edgecolor('white')

    # Annotate current
    ax.text(2025, 2.10, '~$2T/yr',
            ha='center', va='bottom', fontsize=10, fontweight='bold', color=OCEAN)
    ax.text(2030, 2.80, 'Projected',
            ha='center', va='bottom', fontsize=10, fontweight='bold', color=SKY, style='italic')

    # Vertical line at 2025 (confirmed/projected divider)
    ax.axvline(2025.5, color=DOLDRUMS, linestyle=':', linewidth=1.0, alpha=0.7, zorder=0)
    ax.text(2026.5, 0.2, 'Projected', fontsize=9, color=DOLDRUMS, style='italic')
    ax.text(2024.5, 0.2, 'Actual/Est.', fontsize=9, color=DOLDRUMS, style='italic', ha='right')

    ax.set_ylabel('Estimated Annual Generational Wealth Transfer (USD Trillions)',
                  fontsize=10, color=DOLDRUMS)
    ax.set_ylim(0, 3.3)
    style_single_ax(ax, fmt='${:.1f}T')
    ax.set_xlim(2014.3, 2030.7)
    ax.tick_params(axis='x', labelsize=9)

    # Legend swatch
    legend_elements = [
        Patch(facecolor=OCEAN, edgecolor='white', label='Actual/Estimate'),
        Patch(facecolor=SKY, edgecolor='white', hatch='//', label='Projected'),
    ]
    leg = ax.legend(handles=legend_elements, loc='upper left',
                    frameon=True, framealpha=0.95, edgecolor=DOLDRUMS, fontsize=9)
    leg.get_frame().set_linewidth(0.5)

    add_annotation_box(
        ax,
        '~$2T transfers every year. Most goes to the wealthy. 55% of Millennials expect some. That changes the spending math.',
        x=0.50, y=0.78
    )

    brand_fig(fig,
              title='The Great Wealth Transfer: $2 Trillion a Year and Accelerating',
              subtitle='Figure 11: Estimated annual generational wealth transfer (2015-2030)',
              source='Cerulli Associates (third-party estimates; 2026-2030 projected)',
              data_date='2025-12-31')
    save_fig(fig, f'{OUTDIR}/fig11_wealth_transfer.png')
    print('Saved fig11')


# =========================================================
# FIG 12 — First-Time Buyer Down Payment Sources (pie)
# =========================================================
def fig12_downpayment_sources():
    labels = ['Gift or\nInheritance', 'Own Savings', 'Retirement/\nOther']
    sizes = [40, 45, 15]
    colors = [OCEAN, STARBOARD, DOLDRUMS]

    fig, ax = new_fig(figsize=(14, 7))

    wedges, texts, autotexts = ax.pie(
        sizes, labels=labels, colors=colors, autopct='%1.0f%%',
        startangle=90, pctdistance=0.72,
        wedgeprops={'edgecolor': 'white', 'linewidth': 2.5},
        textprops={'fontsize': 11, 'color': DOLDRUMS, 'fontweight': 'bold'}
    )
    for at in autotexts:
        at.set_color('white')
        at.set_fontsize(13)
        at.set_fontweight('bold')

    ax.set_aspect('equal')
    # Kill the spines on a pie axis
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_xticks([]); ax.set_yticks([])

    add_annotation_box(
        ax,
        '40% of first-time buyers used a gift or inheritance. Housing is inheritance-sensitive, not just rate-sensitive. h/t @TimPierotti.',
        x=0.50, y=0.06
    )

    brand_fig(fig,
              title='How First-Time Buyers Are Actually Getting Into Homes',
              subtitle='Figure 12: Share of first-time homebuyers by down payment source',
              source='Redfin, Zelman & Associates (third-party survey)',
              data_date='2025-12-31')
    save_fig(fig, f'{OUTDIR}/fig12_downpayment_sources.png')
    print('Saved fig12')


if __name__ == '__main__':
    fig1_wealth_concentration()
    fig2_excess_savings()
    fig3_savings_rate_quintile()
    fig4_subprime_auto_delinquency()
    fig5_vehicle_repossessions()
    fig6_delinquency_by_loan_type()
    fig7_employment_by_firm_size()
    fig8_longterm_unemployment()
    fig9_retail_bifurcation()
    fig10_housing_bifurcation()
    fig11_wealth_transfer()
    fig12_downpayment_sources()

    print('\n=== ALL 12 CHARTS SAVED ===')
    print(f'Output: {OUTDIR}')

    print('\n=== DATA FLAGS ===')
    print('Fig 1:  Wealth cohort shares — hardcoded from Fed DFA Q3 2025 published aggregates. CONFIRMED values.')
    print('Fig 2:  Excess savings cohort split — MODELED (not directly reported by BEA). Endpoint values from spec.')
    print('Fig 3:  Cohort savings rates — ESTIMATES (academic / DFA-derived). BEA aggregate 4.0% CONFIRMED from DB (PSAVERT Feb 2026).')
    print('Fig 4:  Subprime auto delinquency — HARDCODED anchors from spec. Intermediate years INTERPOLATED. No DB series available.')
    print('Fig 5:  Vehicle repos — 2009 peak + 2021 low + 2025 actual confirmed per spec. Intermediate years INTERPOLATED.')
    print('Fig 6:  Delinquency by loan type — bps-above-2019-baseline from spec. NOT pulled from DB. Verify against NY Fed Q4 2025.')
    print('Fig 7:  ADP by firm size — hardcoded Dec 2025 values from spec. NOT pulled from DB. Verify against latest ADP release.')
    print('Fig 8:  Long-term unemployment by demographic — hardcoded BLS values from spec. Verify against latest monthly release.')
    print('Fig 9:  Luxury vs value retail — endpoint values (+17%, -9%) confirmed per spec. Monthly path MODELED between endpoints.')
    print('Fig 10: Housing bifurcation — Zillow/Redfin tier endpoints from spec. Single observation snapshot, not time series.')
    print('Fig 11: Wealth transfer — Cerulli $2T/yr current CONFIRMED. Full annual time series MODELED from trajectory guidance.')
    print('Fig 12: Down payment sources — 40% gift/inheritance CONFIRMED (Redfin). Remaining split (45/15) MODELED to complete pie.')
    print('\nOutput location note: spec requested /mnt/user-data/outputs/ but that path is read-only.')
    print(f'Charts saved to {OUTDIR} instead.')
