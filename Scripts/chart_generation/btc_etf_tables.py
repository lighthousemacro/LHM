"""
BTC ETF Article - Table Charts
Renders data tables as styled PNG images for Bear/Substack
"""

import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# ———————— COLORS ————————
COLORS = {
    'ocean': '#2389BB',
    'dusk': '#FF6723',
    'sky': '#00BBFF',
    'sea': '#00BB89',
    'venus': '#FF2389',
    'doldrums': '#898989',
}

THEME = {
    'bg': '#0A1628',
    'fg': '#e6edf3',
    'muted': '#8b949e',
    'spine': '#1e3350',
    'primary': '#2389BB',
}

OUTPUT_DIR = Path('/Users/bob/Desktop/BTC_ETF_Article')


def add_outer_border(fig):
    """Add 4pt Ocean border."""
    fig.patches.append(plt.Rectangle(
        (0, 0), 1, 1, transform=fig.transFigure,
        fill=False, edgecolor=COLORS['ocean'], linewidth=4.0,
        zorder=100, clip_on=False
    ))


def brand_fig_minimal(fig, title):
    """Minimal branding for table charts."""
    # Top accent bar
    ax_top = fig.add_axes([0.02, 0.94, 0.96, 0.006])
    ax_top.axhspan(0, 1, 0, 0.67, color=COLORS['ocean'])
    ax_top.axhspan(0, 1, 0.67, 1.0, color=COLORS['dusk'])
    ax_top.set_xlim(0, 1)
    ax_top.set_ylim(0, 1)
    ax_top.axis('off')

    # Title
    fig.text(0.5, 0.88, title, fontsize=14, fontweight='bold',
             color=THEME['fg'], ha='center')


def save_fig(fig, name):
    path = OUTPUT_DIR / f'{name}.png'
    fig.savefig(path, dpi=200, pad_inches=0.10,
                facecolor=THEME['bg'], edgecolor='none')
    print(f"Saved: {path}")
    plt.close(fig)


# ———————— TABLE 1: ON-CHAIN METRICS ————————
def table_onchain_metrics():
    """MVRV, NUPL, SOPR table"""
    fig, ax = plt.subplots(figsize=(12, 4))
    fig.patch.set_facecolor(THEME['bg'])
    ax.set_facecolor(THEME['bg'])
    ax.axis('off')

    # Table data
    columns = ['Indicator', 'Value', 'Signal', 'Threshold Context']
    data = [
        ['MVRV', '1.31', 'Accumulation', 'Trading 18% above realized price. 1.0-2.0 = buy zone.'],
        ['NUPL', '0.2387', 'Hope Phase', 'Far from "Euphoria" (>0.75). Market has reset.'],
        ['SOPR', '0.9765', 'Capitulation', '<1.0 = sellers realizing losses. Classic bottom signal.'],
    ]

    # Create table
    table = ax.table(
        cellText=data,
        colLabels=columns,
        cellLoc='left',
        loc='center',
        colWidths=[0.12, 0.10, 0.15, 0.53]
    )

    # Style the table
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 2.0)

    # Style header row
    for j, col in enumerate(columns):
        cell = table[(0, j)]
        cell.set_facecolor(COLORS['ocean'])
        cell.set_text_props(color='white', fontweight='bold')
        cell.set_edgecolor(THEME['spine'])

    # Style data rows
    row_colors = [COLORS['sea'], COLORS['ocean'], COLORS['dusk']]
    for i in range(len(data)):
        for j in range(len(columns)):
            cell = table[(i + 1, j)]
            cell.set_facecolor(THEME['bg'])
            cell.set_text_props(color=THEME['fg'])
            cell.set_edgecolor(THEME['spine'])
            # Color the value column
            if j == 1:
                cell.set_text_props(color=row_colors[i], fontweight='bold')
            if j == 2:
                cell.set_text_props(color=row_colors[i], fontweight='bold')

    brand_fig_minimal(fig, 'ON-CHAIN ACCUMULATION SIGNALS')
    fig.subplots_adjust(top=0.78, bottom=0.08, left=0.05, right=0.95)
    add_outer_border(fig)
    save_fig(fig, 'table_onchain_metrics')


# ———————— TABLE 2: BASE TVL ————————
def table_base_tvl():
    """Base Chain TVL growth table"""
    fig, ax = plt.subplots(figsize=(12, 4.5))
    fig.patch.set_facecolor(THEME['bg'])
    ax.set_facecolor(THEME['bg'])
    ax.axis('off')

    columns = ['Date', 'DeFi TVL', 'Context & Milestones']
    data = [
        ['Jan 2024', '~$430M', 'Early growth phase shortly after mainnet launch.'],
        ['Sep 2024', '~$1.42B', 'Steady adoption; surpassed Optimism in key metrics.'],
        ['Jan 2025', '~$2.00B+', 'Major surge; overtook Arbitrum One in daily active users.'],
        ['Feb 2026', '~$3.89B', 'Current State. Mature ecosystem with $12.3B bridged assets.'],
    ]

    table = ax.table(
        cellText=data,
        colLabels=columns,
        cellLoc='left',
        loc='center',
        colWidths=[0.12, 0.12, 0.66]
    )

    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 2.0)

    # Style header
    for j, col in enumerate(columns):
        cell = table[(0, j)]
        cell.set_facecolor(COLORS['ocean'])
        cell.set_text_props(color='white', fontweight='bold')
        cell.set_edgecolor(THEME['spine'])

    # Style data rows
    for i in range(len(data)):
        for j in range(len(columns)):
            cell = table[(i + 1, j)]
            cell.set_facecolor(THEME['bg'])
            cell.set_text_props(color=THEME['fg'])
            cell.set_edgecolor(THEME['spine'])
            # Highlight current row
            if i == len(data) - 1:
                cell.set_text_props(color=COLORS['sea'], fontweight='bold')
            # Color TVL values
            if j == 1:
                cell.set_text_props(color=COLORS['ocean'], fontweight='bold')

    brand_fig_minimal(fig, 'BASE CHAIN TVL GROWTH')
    fig.subplots_adjust(top=0.78, bottom=0.08, left=0.05, right=0.95)
    add_outer_border(fig)
    save_fig(fig, 'table_base_tvl')


# ———————— TABLE 3: cbBTC ————————
def table_cbbtc():
    """cbBTC growth table"""
    fig, ax = plt.subplots(figsize=(12, 4.5))
    fig.patch.set_facecolor(THEME['bg'])
    ax.set_facecolor(THEME['bg'])
    ax.axis('off')

    columns = ['Date', 'Supply', 'Market Cap', 'Context']
    data = [
        ['Pre-Launch', '0', '$0', 'Prior to Sep 2024 launch.'],
        ['Sep 2024', '~1,000 BTC', '<$60M', 'Official Launch.'],
        ['Early 2025', '~30,500 BTC', '~$2.0B', 'Rapid adoption across Base and Ethereum DeFi.'],
        ['Feb 2026', '~84,040 BTC', '~$6.0B', 'Current State. Massive WBTC market share capture.'],
    ]

    table = ax.table(
        cellText=data,
        colLabels=columns,
        cellLoc='left',
        loc='center',
        colWidths=[0.12, 0.15, 0.12, 0.51]
    )

    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 2.0)

    # Style header
    for j, col in enumerate(columns):
        cell = table[(0, j)]
        cell.set_facecolor(COLORS['dusk'])
        cell.set_text_props(color='white', fontweight='bold')
        cell.set_edgecolor(THEME['spine'])

    # Style data rows
    for i in range(len(data)):
        for j in range(len(columns)):
            cell = table[(i + 1, j)]
            cell.set_facecolor(THEME['bg'])
            cell.set_text_props(color=THEME['fg'])
            cell.set_edgecolor(THEME['spine'])
            # Highlight current row
            if i == len(data) - 1:
                cell.set_text_props(color=COLORS['dusk'], fontweight='bold')
            # Color supply/cap values
            if j in [1, 2]:
                cell.set_text_props(color=COLORS['dusk'], fontweight='bold')

    brand_fig_minimal(fig, 'THE RISE OF cbBTC')
    fig.subplots_adjust(top=0.78, bottom=0.08, left=0.05, right=0.95)
    add_outer_border(fig)
    save_fig(fig, 'table_cbbtc')


if __name__ == '__main__':
    print("Generating table PNGs...")
    table_onchain_metrics()
    table_base_tvl()
    table_cbbtc()
    print("Done.")
