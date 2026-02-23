"""
LIGHTHOUSE MACRO — Positioning Update #2: Table & Box Images
Generates branded PNG images for elements that need color rendering on Substack.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import os

OUT_DIR = '/Users/bob/LHM/Outputs/positioning_update_2/white'
os.makedirs(OUT_DIR, exist_ok=True)

# Brand colors
OCEAN = '#2389BB'
DUSK = '#FF6723'
SKY = '#00BBFF'
SEA = '#00BB89'
VENUS = '#FF2389'
DOLDRUMS = '#898989'
STARBOARD = '#238923'
PORT = '#892323'
FOG = '#D1D1D1'
BG = '#ffffff'
FG = '#1a1a1a'
MUTED = '#555555'
SPINE = '#cccccc'


def save_table_fig(fig, name):
    """Save with Ocean border, matching chart style."""
    fig.patches.append(plt.Rectangle(
        (0, 0), 1, 1, transform=fig.transFigure,
        fill=False, edgecolor=OCEAN, linewidth=4.0,
        zorder=100, clip_on=False
    ))
    path = os.path.join(OUT_DIR, name)
    fig.savefig(path, dpi=200, bbox_inches='tight', pad_inches=0.025,
                facecolor=BG, edgecolor='none')
    plt.close(fig)
    print(f'  Saved: {path}')
    return path


# =============================================================================
# 1. SUMMARY BANNER (SCOTUS / Labor / Credit)
# =============================================================================

def build_summary_banner():
    print('Building: Summary Banner...')
    fig = plt.figure(figsize=(14, 3.2))
    fig.patch.set_facecolor(BG)

    # Dark banner background
    banner = fig.add_axes([0.03, 0.15, 0.94, 0.75])
    banner.set_facecolor('#1a2a3a')
    banner.set_xlim(0, 1)
    banner.set_ylim(0, 1)
    banner.axis('off')

    # Three column headers
    cols = [
        ('SCOTUS Tariff Shock', 0.17),
        ('Labor Threshold', 0.50),
        ('Credit Denial', 0.83),
    ]
    for title, x in cols:
        banner.text(x, 0.72, title, fontsize=16, fontweight='bold',
                    color='white', ha='center', va='center',
                    fontfamily='sans-serif')

    # Subtext
    banner.text(0.50, 0.30,
                'IEEPA tariffs struck down 6-3. Section 122 at 15% max replaces. '
                'SOFR-EFFR: Quiet. Still Defensive, not Disorderly.',
                fontsize=11, color='#aabbcc', ha='center', va='center',
                fontfamily='sans-serif', style='italic')

    # Accent bars
    tbar = fig.add_axes([0.03, 0.92, 0.94, 0.03])
    tbar.axhspan(0, 1, 0, 0.67, color=OCEAN)
    tbar.axhspan(0, 1, 0.67, 1.0, color=DUSK)
    tbar.set_xlim(0, 1); tbar.set_ylim(0, 1); tbar.axis('off')

    bbar = fig.add_axes([0.03, 0.05, 0.94, 0.03])
    bbar.axhspan(0, 1, 0, 0.67, color=OCEAN)
    bbar.axhspan(0, 1, 0.67, 1.0, color=DUSK)
    bbar.set_xlim(0, 1); bbar.set_ylim(0, 1); bbar.axis('off')

    return save_table_fig(fig, 'table_summary_banner.png')


# =============================================================================
# 2. SCORECARD TABLE
# =============================================================================

def build_scorecard():
    print('Building: Scorecard Table...')
    fig = plt.figure(figsize=(14, 7))
    fig.patch.set_facecolor(BG)
    ax = fig.add_axes([0.03, 0.05, 0.94, 0.88])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    # Column positions
    cols = [0.02, 0.16, 0.30, 0.44, 0.56, 0.68, 0.82]
    headers = ['Call', 'Direction', 'Open\n(Jan 16)', 'Close\n(Feb 20)', 'Return', 'vs\nSPY', 'Verdict']

    # Header row
    header_rect = mpatches.FancyBboxPatch((0.0, 0.88), 1.0, 0.12,
                                           boxstyle='square,pad=0',
                                           facecolor=OCEAN, edgecolor='none')
    ax.add_patch(header_rect)
    for x, h in zip(cols, headers):
        ax.text(x + 0.06, 0.94, h, fontsize=11, fontweight='bold',
                color='white', va='center', ha='center')

    # Data rows
    rows = [
        ['SPY\n(underweight)', 'Reduced\nexposure', '$693.66', '$689.43', '-0.6%', '--', 'Correct to\nunderweight'],
        ['IWM\n(underweight)', 'Reduced\nexposure', '$265.87', '$264.61', '-0.5%', '--', 'Correct to\nunderweight'],
        ['XLV\n(overweight)', 'Long', '$156.64', '$156.82', '+0.1%', '+0.7%', 'Outperformed'],
        ['XLP\n(overweight)', 'Long', '$82.15', '$87.89', '+7.0%', '+7.6%', 'Outperformed'],
        ['XLU\n(overweight)', 'Long', '$43.17', '$46.33', '+7.3%', '+7.9%', 'Strong\noutperformance'],
        ['Credit\n(UW HY)', 'Reduced\nexposure', 'HY OAS\n~290 bps', 'HY OAS\n~288 bps', 'Spreads\nstill tight', '--', 'Structurally\ncorrect, early'],
        ['Vol (long\nconvexity)', 'Directional\nview', 'VIX at\n15.44', 'VIX at\n19.09', '+23.6%\n(VIX level)', '--', 'Directional call\nconfirmed'],
    ]

    verdict_colors = [STARBOARD, STARBOARD, STARBOARD, STARBOARD, STARBOARD, DUSK, OCEAN]

    row_height = 0.88 / len(rows)
    for i, (row, vc) in enumerate(zip(rows, verdict_colors)):
        y_top = 0.88 - (i * row_height)
        y_center = y_top - row_height / 2

        # Alternating row background
        if i % 2 == 0:
            row_rect = mpatches.FancyBboxPatch((0.0, y_top - row_height), 1.0, row_height,
                                                boxstyle='square,pad=0',
                                                facecolor='#f8f9fa', edgecolor='none')
            ax.add_patch(row_rect)

        for j, (x, val) in enumerate(zip(cols, row)):
            color = FG
            weight = 'normal'
            if j == 6:  # Verdict column
                color = vc
                weight = 'bold'
            ax.text(x + 0.06, y_center, val, fontsize=10, color=color,
                    fontweight=weight, va='center', ha='center')

    # Grid lines
    for i in range(len(rows) + 1):
        y = 0.88 - (i * row_height)
        ax.axhline(y, color=SPINE, linewidth=0.5, xmin=0, xmax=1)

    return save_table_fig(fig, 'table_scorecard.png')


# =============================================================================
# 3. POSITION TABLES (Equities, Rates, Credit, Real Assets)
# =============================================================================

def build_position_table(title, rows, filename):
    """Generic position table builder."""
    print(f'Building: {title}...')
    n_rows = len(rows)
    fig_height = 1.8 + n_rows * 0.7
    fig = plt.figure(figsize=(14, fig_height))
    fig.patch.set_facecolor(BG)
    ax = fig.add_axes([0.03, 0.05, 0.94, 0.85])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    # Title
    fig.text(0.50, 0.95, title, fontsize=16, fontweight='bold',
             color=FG, ha='center', va='top', fontfamily='sans-serif')

    # Column positions and headers
    cols = [0.01, 0.22, 0.44, 0.72]
    headers = ['Expression', 'Direction', 'Change from January', 'Invalidation']
    col_widths = [0.21, 0.22, 0.28, 0.28]

    # Header row
    header_rect = mpatches.FancyBboxPatch((0.0, 0.85), 1.0, 0.15,
                                           boxstyle='square,pad=0',
                                           facecolor=OCEAN, edgecolor='none')
    ax.add_patch(header_rect)
    for x, h, w in zip(cols, headers, col_widths):
        ax.text(x + w/2, 0.925, h, fontsize=11, fontweight='bold',
                color='white', va='center', ha='center')

    # Data rows
    row_height = 0.85 / n_rows
    for i, row in enumerate(rows):
        y_top = 0.85 - (i * row_height)
        y_center = y_top - row_height / 2

        if i % 2 == 0:
            row_rect = mpatches.FancyBboxPatch((0.0, y_top - row_height), 1.0, row_height,
                                                boxstyle='square,pad=0',
                                                facecolor='#f8f9fa', edgecolor='none')
            ax.add_patch(row_rect)

        for j, (x, val, w) in enumerate(zip(cols, row, col_widths)):
            color = FG
            weight = 'normal'
            fontsize = 10
            if j == 1:  # Direction column
                weight = 'bold'
                val_lower = val.lower()
                if 'overweight' in val_lower or 'long' in val_lower:
                    color = STARBOARD
                elif 'underweight' in val_lower or 'avoid' in val_lower:
                    color = DUSK
                elif 'active' in val_lower or 'new' in val_lower or 'elevated' in val_lower:
                    color = OCEAN
                else:
                    color = FG
            ax.text(x + w/2, y_center, val, fontsize=fontsize, color=color,
                    fontweight=weight, va='center', ha='center',
                    wrap=True)

        ax.axhline(y_top - row_height, color=SPINE, linewidth=0.5)

    return save_table_fig(fig, filename)


def build_all_position_tables():
    # Equities
    build_position_table('Equities', [
        ['SPY', 'Underweight', 'Maintained', 'Quits above 2.3%,\nbreadth thrust'],
        ['IWM', 'Underweight', 'Maintained (Jan 22\nheadfake to ATH)', 'HY OAS below 250 bps\nwith breadth confirming'],
        ['XLV, XLP, XLU', 'Overweight', 'Maintained.\nXLU +7.3% since Jan 16', 'Relative strength\nvs SPY reverses'],
        ['Long quality /\nShort cyclicals', 'Active', 'Maintained', 'Multiple macro inputs\nturn constructive'],
    ], 'table_positions_equities.png')

    # Rates
    build_position_table('Rates', [
        ['IEF (5-7yr belly)', 'Long, reduced\nconviction', 'Maintained but\nconviction lower', 'Fed signals renewed\nhiking cycle'],
        ['TLT', 'Avoid', 'Maintained', '10Y-2Y inverts\nbelow -20 bps'],
        ['Steepener', 'New lean', 'Tariff path inflationary\n+ deficit-expanding', 'Curve flattens\nbelow +30 bps'],
    ], 'table_positions_rates.png')

    # Credit
    build_position_table('Credit', [
        ['HYG, JNK', 'Underweight', 'Maintained', 'HY OAS above 400 bps\nor labor rebounds'],
        ['Short-duration IG', 'Preferred if\nyield needed', 'Maintained', 'Spreads widen\nabove 150 bps'],
        ['HY downside\nvia options', 'Active', 'Credit-labor divergence\nhas not closed', 'CLG normalizes'],
    ], 'table_positions_credit.png')

    # Real Assets and Cash
    build_position_table('Real Assets and Cash', [
        ['Gold (GLD)', 'New Core Book\nexpression', 'Added. DXY weakening +\nrefund impulse constructive.', 'DXY above 108,\nreal yields above 2.5%'],
        ['Tail hedges', 'Vol call has\nplayed out', 'Jan call confirmed.\nWould not add at VIX ~20.', 'VIX drops below 14'],
        ['Cash (T-bill\nproxies)', 'Active position', 'Maintained. Dry powder\nfor plumbing dislocation.', 'MRI drops below -0.5'],
    ], 'table_positions_real_assets.png')


# =============================================================================
# 4. INVALIDATION CRITERIA (Two-column green/red box)
# =============================================================================

def build_invalidation():
    print('Building: Invalidation Criteria...')
    fig = plt.figure(figsize=(14, 8))
    fig.patch.set_facecolor(BG)

    # Title
    fig.text(0.50, 0.96, 'INVALIDATION CRITERIA', fontsize=20, fontweight='bold',
             color=FG, ha='center', va='top', fontfamily='sans-serif')

    # Divider line under title
    line = fig.add_axes([0.05, 0.91, 0.90, 0.003])
    line.axhspan(0, 1, color=OCEAN)
    line.set_xlim(0, 1); line.set_ylim(0, 1); line.axis('off')

    # LEFT BOX: Defensive Case Breaks If (green-ish)
    left = fig.add_axes([0.04, 0.05, 0.44, 0.83])
    left.set_xlim(0, 1)
    left.set_ylim(0, 1)
    left.axis('off')

    # Light green background
    left_bg = mpatches.FancyBboxPatch((0, 0), 1, 1,
                                       boxstyle='round,pad=0.02',
                                       facecolor='#e8f5e9', edgecolor=STARBOARD,
                                       linewidth=1.5)
    left.add_patch(left_bg)

    left.text(0.50, 0.93, 'Defensive Case Breaks If:', fontsize=14, fontweight='bold',
              color=STARBOARD, ha='center', va='top')

    left_items = [
        ('Labor recovers:', 'Quits rebounds above\n2.2% and job openings reverse higher.\nLong-term unemployment stabilizes.'),
        ('Credit reconciles:', 'HY OAS widens to 350+\nbps, closing the gap between what\nspreads are pricing and what labor is saying.'),
        ('Multiple macro inputs improve\nsimultaneously:', 'Labor, credit, and breadth\nall turn constructive. Risk environment\nshifts to neutral.'),
        ('Breadth confirms:', 'Nasdaq % above 200d\nrecovers above 60%, price-breadth\ndivergence normalizes. Rally is real.'),
    ]

    y = 0.82
    for title, desc in left_items:
        left.text(0.08, y, title, fontsize=11, fontweight='bold', color=FG, va='top')
        y -= 0.04
        left.text(0.08, y, desc, fontsize=10, color=MUTED, va='top', linespacing=1.4)
        y -= 0.18

    # RIGHT BOX: Defensive Case Deepens If (red-ish)
    right = fig.add_axes([0.52, 0.05, 0.44, 0.83])
    right.set_xlim(0, 1)
    right.set_ylim(0, 1)
    right.axis('off')

    right_bg = mpatches.FancyBboxPatch((0, 0), 1, 1,
                                        boxstyle='round,pad=0.02',
                                        facecolor='#fce4ec', edgecolor=PORT,
                                        linewidth=1.5)
    right.add_patch(right_bg)

    right.text(0.50, 0.93, 'Defensive Case Deepens If:', fontsize=14, fontweight='bold',
               color=PORT, ha='center', va='top')

    right_items = [
        ('Quits breaks below 2.0%:', 'Pre-recessionary\nconfirmation. Core Book shifts to maximum\ndefensive. Overlay tightens stops.'),
        ('Credit ignores further:', 'HY OAS holds\nbelow 300 while openings continue falling.\nThe snap-back, when it comes, will be violent.'),
        ('Section 301/232 escalation:', 'If the\nadministration replaces IEEPA with broader,\nmore durable tariff authority, the tariff\nrelief trade reverses.'),
        ('Plumbing stress emerges:', 'SOFR-EFFR\nspread breaks 15 bps. Defensive to\nDisorderly. Full risk-off.'),
    ]

    y = 0.82
    for title, desc in right_items:
        right.text(0.08, y, title, fontsize=11, fontweight='bold', color=FG, va='top')
        y -= 0.04
        right.text(0.08, y, desc, fontsize=10, color=MUTED, va='top', linespacing=1.4)
        y -= 0.18

    return save_table_fig(fig, 'table_invalidation.png')


# =============================================================================
# MAIN
# =============================================================================

if __name__ == '__main__':
    print(f'\n{"="*60}')
    print('LIGHTHOUSE MACRO — PU#2 Table Images')
    print(f'{"="*60}\n')

    paths = []
    paths.append(build_summary_banner())
    paths.append(build_scorecard())
    build_all_position_tables()
    paths.append(build_invalidation())

    print(f'\n{"="*60}')
    print(f'All table images saved to: {OUT_DIR}')
    print(f'{"="*60}')
