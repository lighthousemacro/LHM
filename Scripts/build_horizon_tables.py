"""
Render the three Horizon tables as branded LHM PNGs.

Outputs:
  table_01_book.png       — The Book (positions/weights/status/stops)
  table_02_risk_matrix.png — Risk Matrix
  table_03_chart_specs.png — Chart Specifications (production reference)
"""
import os
import sys
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

sys.path.insert(0, '/Users/bob/LHM/Scripts/chart_generation')
from lhm_chart_template import (COLORS, set_theme, brand_fig, save_fig)

OUT_DIR = '/Users/bob/LHM/Outputs/charts/horizon_may_2026'


def render_table(headers, rows, col_weights, save_path,
                 title, subtitle, source,
                 figsize=None, status_col=None):
    """Render a clean LHM-branded table as a PNG.

    headers: list[str]
    rows: list[list[str]] - cells can use markers:
        '!!ALERT!!' prefix → render in Port red bold
        '!!ACTIVE!!' prefix → render in Sea green bold
        '!!STAGED!!' prefix → render in Dusk orange bold
    col_weights: list[float] - relative widths summing to 1
    status_col: int - which column index is the status col (gets special color treatment)
    """
    set_theme('white')
    n_rows = len(rows)
    row_h = 0.42
    if figsize is None:
        figsize = (16, max(6, n_rows * row_h + 3.2))

    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_facecolor('white')
    fig.subplots_adjust(top=0.86, bottom=0.10, left=0.025, right=0.975)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_axis_off()

    # Compute column x positions
    col_x = [0.0]
    for w in col_weights:
        col_x.append(col_x[-1] + w)

    # ---- HEADER ----
    header_y_top = 0.96
    header_h = 0.07
    # Ocean fill
    ax.add_patch(Rectangle((0, header_y_top - header_h), 1, header_h,
                            color=COLORS['ocean'], zorder=2))
    for i, h in enumerate(headers):
        x_center = (col_x[i] + col_x[i+1]) / 2
        ax.text(x_center, header_y_top - header_h/2, h,
                ha='center', va='center', fontsize=11, fontweight='bold',
                color='white', zorder=3)

    # ---- ROWS ----
    body_top = header_y_top - header_h
    body_h = body_top - 0.02
    row_height = body_h / n_rows

    for ri, row in enumerate(rows):
        y_top = body_top - ri * row_height
        y_mid = y_top - row_height/2

        # Alternating shading
        if ri % 2 == 1:
            ax.add_patch(Rectangle((0, y_top - row_height), 1, row_height,
                                    color='#f5f8fa', zorder=1))

        # Bottom border for the row
        ax.plot([0, 1], [y_top - row_height, y_top - row_height],
                color='#e8eef2', linewidth=0.5, zorder=2)

        for ci, cell in enumerate(row):
            x_left = col_x[ci]
            x_right = col_x[ci+1]
            x_center = (x_left + x_right) / 2

            text = str(cell)
            color = '#1a1a1a'
            weight = 'normal'
            ha = 'center'

            # Special handling for marker prefixes
            if text.startswith('!!ALERT!!'):
                text = text[len('!!ALERT!!'):]
                color = COLORS['port']
                weight = 'bold'
            elif text.startswith('!!ACTIVE!!'):
                text = text[len('!!ACTIVE!!'):]
                color = COLORS['starboard']
                weight = 'bold'
            elif text.startswith('!!STAGED!!'):
                text = text[len('!!STAGED!!'):]
                color = COLORS['dusk']
                weight = 'bold'
            elif text.startswith('!!ANCHOR!!'):
                text = text[len('!!ANCHOR!!'):]
                color = COLORS['ocean']
                weight = 'bold'

            # First column (often label) gets bold ocean
            if ci == 0:
                color = COLORS['ocean']
                weight = 'bold'
                ha = 'left'
                ax.text(x_left + 0.008, y_mid, text, ha=ha, va='center',
                        fontsize=10, fontweight=weight, color=color, zorder=3,
                        wrap=True)
            else:
                # Long text wrapping support
                if len(text) > 60:
                    fontsize = 8.5
                else:
                    fontsize = 9.5
                ax.text(x_center, y_mid, text, ha=ha, va='center',
                        fontsize=fontsize, fontweight=weight, color=color, zorder=3,
                        wrap=True)

    # ---- BORDER ----
    ax.add_patch(Rectangle((0, body_top - body_h), 1, body_h + header_h,
                            fill=False, edgecolor=COLORS['ocean'],
                            linewidth=1.0, zorder=4))

    brand_fig(fig, title=title, subtitle=subtitle, source=source,
              data_date=__import__('datetime').datetime.now())
    return save_fig(fig, save_path)


# =====================================================================
# TABLE 1 — THE BOOK
# =====================================================================
def build_book():
    headers = ['Position', 'Ticker', 'Target wt', 'Source', 'Status today', 'Thesis stop', 'Price stop']
    col_weights = [0.13, 0.07, 0.10, 0.08, 0.16, 0.22, 0.24]
    rows = [
        ['Gold', 'GLD', '12%', 'Macro', '!!STAGED!!Staged',
         'Real yields above 2.5% sustained', 'Z-63 below -1.0 (current -1.66)'],
        ['Energy', 'XLE', '10%', 'Macro', '!!STAGED!!Staged',
         'WTI sub-$80 sustained post-Iran-deal', 'Z-21 below -1.0 (current -1.19)'],
        ['Utilities', 'XLU', '10%', 'Macro', '!!ALERT!!DO NOT ENTER',
         'Long-end repricing decouples (firing now)', '200d at $44.31 vs last $44.80'],
        ['Short-duration Tsy', 'SHY', '10%', 'Macro', '!!ANCHOR!!Active (anchor)',
         'Fed pivots dovish without growth shock', 'n/a (anchor)'],
        ['Consumer Staples', 'XLP', '8%', 'Macro', '!!ACTIVE!!Active',
         'Real DPI re-accelerates above 2% sustained', '-10% entry or 200d MA'],
        ['Quality (FCF yield)', 'COWZ', '8%', 'Technical', '!!ACTIVE!!Active (half-size)',
         'Trend break below 50d MA', '50d MA break'],
        ['Long vol', 'VIXY', '7%', 'Macro', '!!ACTIVE!!Active',
         'Catalyst resolves without dispersion', '7% cap, no add-ons'],
        ['Cash', '(cash)', '35% / 67% today', 'n/a', 'Strategic + staged',
         'Deploys as triggers fire', 'n/a'],
    ]
    return render_table(
        headers, rows, col_weights,
        save_path=f'{OUT_DIR}/table_01_book.png',
        title='The Book — target weights, today\'s status, and the stops that gate them',
        subtitle='29% active, 36% staged behind technical triggers, 65% effective cash',
        source='Lighthouse Macro')


# =====================================================================
# TABLE 2 — RISK MATRIX
# =====================================================================
def build_risk_matrix():
    headers = ['Risk', 'Probability', 'Impact', 'Trigger', 'Pillar']
    col_weights = [0.27, 0.12, 0.13, 0.40, 0.08]
    rows = [
        ['Term premium gaps higher', 'High', 'High',
         'Auction tails > 3bps, dealer takedown > 30%, 30Y > 5.25%', '8'],
        ['HY OAS widens to 350+', 'Medium', 'High',
         'Quits < 1.9% with claims breakout > 250k', '1, 9'],
        ['Iran deal collapses, oil > $115', 'Medium', 'Medium',
         'Talks break down, Strait of Hormuz disruption', '2, 7'],
        ['Iran deal completes, oil < $75', 'Medium', 'Medium-positive',
         'Memorandum signed, Strait reopens', '2, 7'],
        ['Warsh signals continuity at confirmation', 'Medium', 'Medium-positive',
         'Hearing tone matches Powell trajectory', '8'],
        ['Warsh signals harder hawk shift', 'Medium', 'High',
         'Dot-plot signal hawkish, restart hike discussion', '8'],
        ['AI capex guides flinch on next print', 'Medium', 'High',
         'Cloud growth deceleration, capex envelope cut', '6, 11'],
        ['Breadth thrust higher', 'Medium', 'Medium-positive',
         '%>50d crosses 60% with %>20d > 70%', '11'],
    ]
    return render_table(
        headers, rows, col_weights,
        save_path=f'{OUT_DIR}/table_02_risk_matrix.png',
        title='Risk Matrix — eight scenarios, mapped to pillars and trigger levels',
        subtitle='Top three rows are where the asymmetry sits',
        source='Lighthouse Macro')


# =====================================================================
# TABLE 3 — CHART SPECIFICATIONS
# =====================================================================
def build_chart_specs():
    headers = ['#', 'Title', 'Series', 'Range', 'Annotations']
    col_weights = [0.04, 0.22, 0.22, 0.12, 0.40]
    rows = [
        ['1', 'MRI Regime History', 'MRI composite + regime bands',
         '2023 - present', 'High Risk → Neutral transition mid-Apr 2026, current +0.04'],
        ['2', 'FOMC Dissents Per Meeting', 'FOMC voting record',
         '1990 - present', 'April 2026 highlighted, "Most since Oct 1992"'],
        ['3', 'Q2 Treasury Borrowing Est vs Actual', 'Feb $110B / May $189B',
         'Q2 2026', '$79B differential, "70% overshoot"'],
        ['4', 'SPY with RSI(14)', 'SPY close + 14d RSI',
         'Last 12 months', 'Fresh ATH $737.55 May 8, RSI 75.1'],
        ['5', '10Y and 30Y Treasury Yields', 'DGS10, DGS30',
         'Last 90 days', '"30Y > 5%" May 4, "Iran peace memo" May 6'],
        ['6', '10Y Term Premium (ACM)', 'NY Fed ACM term premium',
         '1990 - present', '150bps anchor, "Pre-QE regime median: 150bps"'],
        ['7', 'Structure-Breadth Divergence', 'LHM SBD composite',
         'Last 12 months', '"Crossed Apr 14, re-breached May 6 at +1.17"'],
        ['8', 'Credit-Labor Gap', 'LHM CLG composite',
         'Last 5 years', '"Crossed -1.0 Feb 23, latest -1.68 March 10"'],
        ['9', 'Hire Rate', 'JTSHIR',
         '2002 - present', 'Current 3.1%, "GFC-era / 2020 lockdown levels"'],
        ['10', 'Quit Rate', 'JTSQUR',
         '2002 - present', '2.0% threshold, "Below 2.0% for 8 months"'],
        ['11', 'Hyperscaler Capex + % GDP', 'AMZN+GOOGL+MSFT+META',
         '2015 - 2026E', '"$610-640B 2026 guide ≈ 2% of GDP"'],
        ['12', 'Semi IP minus Mfg IP', 'G.17 IP series, YoY spread',
         '2010 - present', 'Current +7.1pp'],
        ['13', 'S&P 500 EPS Decomposition', 'Mag7 ex-Nvidia / ex-Mag7 / Mag7',
         'Current quarter', '6%, 10%, 23% annotations'],
        ['14', 'Book Composition by Bucket', 'Target weights',
         'Snapshot', '29% active, 36% staged, 35% strategic cash'],
    ]
    return render_table(
        headers, rows, col_weights,
        save_path=f'{OUT_DIR}/table_03_chart_specs.png',
        title='Chart Specifications — production reference',
        subtitle='14 charts, white theme primary, 200 DPI, 23/89/BB palette',
        source='Lighthouse Macro')


if __name__ == '__main__':
    p1 = build_book()
    print(f'OK  table_01_book -> {p1}')
    p2 = build_risk_matrix()
    print(f'OK  table_02_risk_matrix -> {p2}')
    p3 = build_chart_specs()
    print(f'OK  table_03_chart_specs -> {p3}')
