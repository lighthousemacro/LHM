"""
BTC ETF Interactive Report Charts
Extracted from HTML interactive report and rendered in Lighthouse Macro style
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.ticker import FuncFormatter
import pandas as pd
import numpy as np
from pathlib import Path

# ———————— COLORS (FIXED) ————————
COLORS = {
    'ocean': '#2389BB',
    'dusk': '#FF6723',
    'sky': '#00BBFF',
    'sea': '#00BB89',
    'venus': '#FF2389',
    'doldrums': '#898989',
}

# ———————— THEME DEFINITION (DARK) ————————
THEME = {
    'bg': '#0A1628',
    'fg': '#e6edf3',
    'muted': '#8b949e',
    'spine': '#1e3350',
    'primary': '#2389BB',
    'secondary': '#FF6723',
    'tertiary': '#00BBFF',
    'accent': '#FF2389',
    'legend_bg': '#0f1f38',
    'legend_fg': '#e6edf3',
}

# ———————— OUTPUT PATH ————————
OUTPUT_DIR = Path('/Users/bob/LHM/Outputs/Educational_Charts/BTC_ETF')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ———————— HELPER FUNCTIONS ————————

def new_fig(figsize=(14, 8)):
    """Create figure with theme background and standard margins."""
    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_facecolor(THEME['bg'])
    ax.set_facecolor(THEME['bg'])
    return fig, ax


def style_ax(ax):
    """Core spine/grid styling."""
    for spine in ax.spines.values():
        spine.set_color(THEME['spine'])
        spine.set_linewidth(0.5)
    ax.grid(False)
    ax.tick_params(axis='both', which='both', length=0, colors=THEME['muted'])
    ax.tick_params(axis='x', labelsize=10, labelcolor=THEME['muted'])


def brand_fig(fig, title, subtitle, source='Lighthouse Macro'):
    """Apply all figure-level branding (watermarks, bars, title)."""
    # Top accent bar (Ocean 2/3, Dusk 1/3)
    ax_top = fig.add_axes([0.03, 0.96, 0.94, 0.004])
    ax_top.axhspan(0, 1, 0, 0.67, color=COLORS['ocean'])
    ax_top.axhspan(0, 1, 0.67, 1.0, color=COLORS['dusk'])
    ax_top.set_xlim(0, 1)
    ax_top.set_ylim(0, 1)
    ax_top.axis('off')

    # Bottom accent bar (mirror)
    ax_bot = fig.add_axes([0.03, 0.035, 0.94, 0.004])
    ax_bot.axhspan(0, 1, 0, 0.67, color=COLORS['ocean'])
    ax_bot.axhspan(0, 1, 0.67, 1.0, color=COLORS['dusk'])
    ax_bot.set_xlim(0, 1)
    ax_bot.set_ylim(0, 1)
    ax_bot.axis('off')

    # Top-left: LIGHTHOUSE MACRO
    fig.text(0.06, 0.98, 'LIGHTHOUSE MACRO', fontsize=13, fontweight='bold', color=COLORS['ocean'])

    # Top-right: Date
    fig.text(0.94, 0.98, 'February 05, 2026', fontsize=11, color=THEME['muted'], ha='right')

    # Title and Subtitle
    fig.text(0.50, 0.93, title, fontsize=16, fontweight='bold', color=THEME['fg'], ha='center')
    fig.text(0.50, 0.895, subtitle, fontsize=12, style='italic', color=COLORS['ocean'], ha='center')

    # Bottom-right: Tagline
    fig.text(0.94, 0.015, 'MACRO, ILLUMINATED.', fontsize=13, fontweight='bold',
             style='italic', color=COLORS['ocean'], ha='right')

    # Bottom-left: Source
    fig.text(0.06, 0.015, f'Lighthouse Macro | {source}; 02.05.2026',
             fontsize=9, style='italic', color=THEME['muted'])


def add_outer_border(fig):
    """Add 4pt Ocean border at absolute figure edge."""
    fig.patches.append(plt.Rectangle(
        (0, 0), 1, 1, transform=fig.transFigure,
        fill=False, edgecolor=COLORS['ocean'], linewidth=4.0,
        zorder=100, clip_on=False
    ))


def add_annotation_box(ax, text, x=0.52, y=0.08):
    """Add takeaway box - default to bottom of chart area."""
    ax.text(x, y, text, transform=ax.transAxes,
            fontsize=10, color=THEME['fg'], ha='center', va='bottom', style='italic',
            bbox=dict(boxstyle='round,pad=0.5', facecolor=THEME['bg'],
                      edgecolor=COLORS['ocean'], alpha=0.9))


def legend_style():
    """Return legend kwargs dict."""
    return dict(
        framealpha=0.95,
        facecolor=THEME['legend_bg'],
        edgecolor=THEME['spine'],
        labelcolor=THEME['legend_fg'],
    )


def save_fig(fig, name):
    """Save with standard settings."""
    path = OUTPUT_DIR / f'{name}.png'
    fig.savefig(path, dpi=200, bbox_inches='tight', pad_inches=0.10,
                facecolor=THEME['bg'], edgecolor='none')
    print(f"Saved: {path}")
    plt.close(fig)


# ———————— CHART: 90-DAY Z-SCORE (FROM HTML) ————————
def chart_zscore_interactive():
    """90-Day Flow Z-Score from interactive report data"""
    fig, ax = new_fig()

    # Data from HTML: months and z-score values
    months = ['Jul 25', 'Aug 25', 'Sep 25', 'Oct 25', 'Nov 25', 'Dec 25', 'Jan 26', 'Feb 26']
    z_scores = [0.5, -0.2, -0.8, 1.5, 1.8, 0.2, -1.2, -1.93]

    c_primary = THEME['primary']

    # Plot ±1σ bands
    ax.axhspan(-1, 1, color=c_primary, alpha=0.10)
    ax.axhline(1, color=c_primary, linewidth=1, linestyle='--', alpha=0.5)
    ax.axhline(-1, color=c_primary, linewidth=1, linestyle='--', alpha=0.5)
    ax.axhline(0, color=COLORS['doldrums'], linewidth=1, linestyle='-', alpha=0.7)

    # Fill areas
    x = np.arange(len(months))
    z_arr = np.array(z_scores)
    ax.fill_between(x, z_arr, 0, where=z_arr >= 0, color=COLORS['sea'], alpha=0.3, interpolate=True)
    ax.fill_between(x, z_arr, 0, where=z_arr < 0, color=COLORS['venus'], alpha=0.3, interpolate=True)

    # Plot line
    ax.plot(x, z_scores, color=c_primary, linewidth=2.5, marker='o', markersize=6,
            markerfacecolor=c_primary, markeredgecolor='white', markeredgewidth=1.5)

    # Styling
    style_ax(ax)
    ax.set_xticks(x)
    ax.set_xticklabels(months, fontsize=10, color=THEME['muted'])
    ax.tick_params(axis='y', labelcolor=c_primary, labelsize=10)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, p: f'{v:.1f}σ'))

    # Set limits
    ax.set_ylim(-2.5, 2.5)
    ax.set_xlim(-0.3, len(months) - 0.7)

    # Add current value label
    current_val = z_scores[-1]
    ax.annotate(f'{current_val:.2f}σ', xy=(len(months)-1, current_val),
                xytext=(10, -10), textcoords='offset points',
                fontsize=11, fontweight='bold', color=COLORS['venus'],
                bbox=dict(boxstyle='round,pad=0.3', facecolor=COLORS['venus'],
                         edgecolor=COLORS['venus'], alpha=0.95),
                arrowprops=dict(arrowstyle='->', color=COLORS['venus'], lw=1.5))
    ax.text(len(months)-1, current_val, '', fontsize=11, fontweight='bold', color='white')

    # Redraw the annotation with white text
    ax.annotate(f'{current_val:.2f}σ', xy=(len(months)-1, current_val),
                xytext=(15, -15), textcoords='offset points',
                fontsize=10, fontweight='bold', color='white',
                bbox=dict(boxstyle='round,pad=0.3', facecolor=COLORS['venus'],
                         edgecolor=COLORS['venus'], alpha=0.95))

    # Add +1/-1 labels
    ax.text(0.02, 1.15, '+1σ', fontsize=9, color=c_primary, alpha=0.7,
            transform=ax.get_yaxis_transform(), va='bottom')
    ax.text(0.02, -1.15, '-1σ', fontsize=9, color=c_primary, alpha=0.7,
            transform=ax.get_yaxis_transform(), va='top')

    # Branding
    brand_fig(fig, 'THE SILENT CAPITULATION', '90-Day Flow Momentum Z-Score', source='Farside Investors')
    add_annotation_box(ax, "Outflow regime  |  NEAR ALL-TIME LOWS (-1.93σ)", x=0.5, y=0.03)

    # Margins and border
    fig.subplots_adjust(top=0.86, bottom=0.10, left=0.08, right=0.94)
    add_outer_border(fig)

    save_fig(fig, 'chart_interactive_zscore')


# ———————— CHART: CUMULATIVE FLOWS (FROM HTML) ————————
def chart_cumulative_interactive():
    """Cumulative Net Flows from interactive report"""
    fig, ax = new_fig()

    # Data from HTML
    months = ['Jan 24', 'Mar 24', 'Jun 24', 'Sep 24', 'Dec 24', 'Jan 25', 'Feb 26']
    cum_flows = [0, 15, 30, 45, 54.7, 50, 46.7]  # in Billions

    c_primary = THEME['primary']
    c_secondary = THEME['secondary']

    x = np.arange(len(months))

    # Fill under curve
    ax.fill_between(x, cum_flows, 0, color=c_primary, alpha=0.15)

    # Plot line
    ax.plot(x, cum_flows, color=c_primary, linewidth=2.5, marker='o', markersize=6,
            markerfacecolor=c_primary, markeredgecolor='white', markeredgewidth=1.5)

    # Mark the peak
    peak_idx = np.argmax(cum_flows)
    ax.annotate(f'Peak: ${cum_flows[peak_idx]:.1f}B', xy=(peak_idx, cum_flows[peak_idx]),
                xytext=(0, 15), textcoords='offset points',
                fontsize=10, fontweight='bold', color=COLORS['sea'], ha='center',
                bbox=dict(boxstyle='round,pad=0.3', facecolor=COLORS['sea'], alpha=0.9))

    # Mark current
    ax.annotate(f'Now: ${cum_flows[-1]:.1f}B', xy=(len(months)-1, cum_flows[-1]),
                xytext=(0, -20), textcoords='offset points',
                fontsize=10, fontweight='bold', color=COLORS['venus'], ha='center',
                bbox=dict(boxstyle='round,pad=0.3', facecolor=COLORS['venus'], alpha=0.9))

    # Styling
    style_ax(ax)
    ax.set_xticks(x)
    ax.set_xticklabels(months, fontsize=10, color=THEME['muted'])
    ax.tick_params(axis='y', labelcolor=c_primary, labelsize=10)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, p: f'${v:.0f}B'))

    # Set limits
    ax.set_ylim(0, max(cum_flows) * 1.2)
    ax.set_xlim(-0.3, len(months) - 0.7)

    # Branding
    brand_fig(fig, 'CUMULATIVE ETF FLOWS', 'Net Inflows Since Launch ($ Billions)', source='Farside Investors')

    drawdown = cum_flows[-1] - cum_flows[peak_idx]
    add_annotation_box(ax, f"${cum_flows[-1]:.1f}B total  |  ${drawdown:.1f}B bleed since peak", x=0.5, y=0.03)

    # Margins and border
    fig.subplots_adjust(top=0.86, bottom=0.10, left=0.08, right=0.94)
    add_outer_border(fig)

    save_fig(fig, 'chart_interactive_cumulative')


# ———————— CHART: BASE TVL BAR (FROM HTML) ————————
def chart_base_tvl_interactive():
    """Base Chain TVL Growth bar chart from interactive report"""
    fig, ax = new_fig()

    # Data from HTML
    periods = ['Jan 2024', 'Sep 2024', 'Jan 2025', 'Feb 2026']
    tvl_values = [0.43, 1.42, 2.00, 3.89]  # in Billions

    c_primary = THEME['primary']

    x = np.arange(len(periods))
    bars = ax.bar(x, tvl_values, color=c_primary, alpha=0.85, width=0.6,
                  edgecolor=c_primary, linewidth=1.5)

    # Add value labels on bars
    for bar, val in zip(bars, tvl_values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                f'${val:.2f}B', ha='center', va='bottom',
                fontsize=11, fontweight='bold', color=c_primary)

    # Styling
    style_ax(ax)
    ax.set_xticks(x)
    ax.set_xticklabels(periods, fontsize=11, color=THEME['muted'])
    ax.tick_params(axis='y', labelcolor=c_primary, labelsize=10)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, p: f'${v:.1f}B'))

    # Set limits
    ax.set_ylim(0, max(tvl_values) * 1.3)

    # Growth calculation
    growth = (tvl_values[-1] / tvl_values[0] - 1) * 100

    # Branding
    brand_fig(fig, 'BASE CHAIN TVL GROWTH', 'Total Value Locked (DeFi)', source='DefiLlama')
    add_annotation_box(ax, f"+{growth:.0f}% growth  |  Aerodrome commands >40% of liquidity", x=0.5, y=0.88)

    # Margins and border
    fig.subplots_adjust(top=0.86, bottom=0.10, left=0.08, right=0.94)
    add_outer_border(fig)

    save_fig(fig, 'chart_interactive_base_tvl')


# ———————— CHART: cbBTC GROWTH (FROM HTML) ————————
def chart_cbbtc_interactive():
    """cbBTC Supply Growth from interactive report"""
    fig, ax = new_fig()

    # Data from HTML
    periods = ['Aug 24', 'Sep 24', 'Dec 24', 'Early 25', 'Feb 26']
    supply = [0, 1000, 15000, 30500, 84040]  # in BTC

    c_secondary = THEME['secondary']

    x = np.arange(len(periods))

    # Fill under curve
    ax.fill_between(x, supply, 0, color=c_secondary, alpha=0.15)

    # Plot line
    ax.plot(x, supply, color=c_secondary, linewidth=2.5, marker='s', markersize=8,
            markerfacecolor=c_secondary, markeredgecolor='white', markeredgewidth=1.5)

    # Add key labels
    ax.annotate('Launch', xy=(1, supply[1]), xytext=(0, 15), textcoords='offset points',
                fontsize=9, color=THEME['muted'], ha='center')
    ax.annotate(f'{supply[-1]:,} BTC\n(~$6B)', xy=(len(periods)-1, supply[-1]),
                xytext=(-40, -30), textcoords='offset points',
                fontsize=10, fontweight='bold', color='white', ha='center',
                bbox=dict(boxstyle='round,pad=0.3', facecolor=c_secondary, alpha=0.95))

    # Styling
    style_ax(ax)
    ax.set_xticks(x)
    ax.set_xticklabels(periods, fontsize=10, color=THEME['muted'])
    ax.tick_params(axis='y', labelcolor=c_secondary, labelsize=10)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, p: f'{v/1000:.0f}K BTC' if v >= 1000 else f'{v:.0f}'))

    # Set limits
    ax.set_ylim(0, max(supply) * 1.2)
    ax.set_xlim(-0.3, len(periods) - 0.7)

    # Branding
    brand_fig(fig, 'THE RISE OF cbBTC', 'Coinbase Wrapped BTC Supply Growth', source='DefiLlama')
    add_annotation_box(ax, "From $0 to $6B in 18 months  |  Capital rotating to productive collateral", x=0.5, y=0.88)

    # Margins and border
    fig.subplots_adjust(top=0.86, bottom=0.10, left=0.08, right=0.94)
    add_outer_border(fig)

    save_fig(fig, 'chart_interactive_cbbtc')


# ———————— CHART: KEY METRICS DASHBOARD ————————
def chart_metrics_dashboard():
    """MVRV, NUPL, SOPR dashboard - card style with high contrast"""
    fig, axes = plt.subplots(1, 3, figsize=(16, 7))
    fig.patch.set_facecolor(THEME['bg'])

    metrics = [
        {'name': 'MVRV', 'value': 1.31, 'max': 3.7, 'zone': 'ACCUMULATION',
         'color': COLORS['sea'], 'desc': '18% above realized price\n1.0-2.0 = Buy Zone'},
        {'name': 'NUPL', 'value': 0.24, 'max': 1.0, 'zone': 'HOPE PHASE',
         'color': COLORS['ocean'], 'desc': 'Far from Euphoria (>0.75)\nMarket has reset'},
        {'name': 'SOPR', 'value': 0.97, 'max': 1.5, 'zone': 'CAPITULATION',
         'color': COLORS['dusk'], 'desc': '<1.0 = Selling at loss\nClassic bottom signal'},
    ]

    for ax, m in zip(axes, metrics):
        ax.set_facecolor(THEME['bg'])
        ax.axis('off')

        # Draw colored card background
        card = plt.Rectangle((-0.9, -0.6), 1.8, 1.5,
                             facecolor=m['color'], alpha=0.15,
                             edgecolor=m['color'], linewidth=2,
                             transform=ax.transData, zorder=1)
        ax.add_patch(card)

        # Metric name at top (white on dark)
        ax.text(0, 0.7, m['name'], ha='center', va='center',
                fontsize=18, fontweight='bold', color=THEME['fg'], zorder=2)

        # Big value in the middle with colored background pill
        ax.text(0, 0.25, f"{m['value']:.2f}", ha='center', va='center',
                fontsize=42, fontweight='bold', color='white', zorder=3,
                bbox=dict(boxstyle='round,pad=0.4', facecolor=m['color'],
                         edgecolor=m['color'], alpha=1.0))

        # Zone label below value
        ax.text(0, -0.15, m['zone'], ha='center', va='center',
                fontsize=12, fontweight='bold', color=m['color'], zorder=2)

        # Description at bottom
        ax.text(0, -0.45, m['desc'], ha='center', va='center',
                fontsize=9, color=THEME['muted'], zorder=2, linespacing=1.3)

        ax.set_xlim(-1.1, 1.1)
        ax.set_ylim(-0.7, 1.0)
        ax.set_aspect('equal')

    # Branding
    brand_fig(fig, 'ON-CHAIN ACCUMULATION SIGNALS', 'MVRV, NUPL, SOPR (CryptoQuant, Feb 4, 2026)', source='CryptoQuant')

    # Add annotation at top of chart area
    fig.text(0.5, 0.80, "All three metrics signal accumulation zone. SOPR <1.0 = sellers realizing losses.",
             ha='center', fontsize=10, color=THEME['fg'], style='italic',
             bbox=dict(boxstyle='round,pad=0.5', facecolor=THEME['bg'],
                       edgecolor=COLORS['ocean'], alpha=0.9))

    # Margins and border
    fig.subplots_adjust(top=0.85, bottom=0.12, left=0.03, right=0.97, wspace=0.15)
    add_outer_border(fig)

    save_fig(fig, 'chart_interactive_metrics')


# ———————— MAIN ————————
if __name__ == '__main__':
    print("\nGenerating charts from interactive HTML report...")
    # Skip z-score - the real Farside data version (chart_07) is better
    # chart_zscore_interactive()
    chart_cumulative_interactive()
    chart_base_tvl_interactive()
    chart_cbbtc_interactive()
    chart_metrics_dashboard()
    print("Done.")
