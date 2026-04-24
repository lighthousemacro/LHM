"""
Gold Extension Study - Branded Chart + Table
Lighthouse Macro
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import numpy as np
from PIL import Image

# Lighthouse colors
OCEAN = '#0089D1'
DUSK = '#FF6723'
SKY = '#00D4FF'
VENUS = '#FF2389'
SEA = '#00BB99'
DOLDRUMS = '#D3D6D9'
STARBOARD = '#00FF00'
PORT = '#FF0000'
DARK_BG = '#1a1a2e'
DARKER_BG = '#0f0f1a'

# Load the TradingView chart
tv_chart = Image.open('/Users/bob/Library/Mobile Documents/com~apple~CloudDocs/GOLD_2026-01-24_21-07-16_41de3.png')

# Create figure with chart on top, table below
fig = plt.figure(figsize=(16, 14), facecolor=DARK_BG)

# Add the TradingView chart at top (as image)
ax_chart = fig.add_axes([0.01, 0.32, 0.98, 0.66])  # [left, bottom, width, height]
ax_chart.imshow(tv_chart)
ax_chart.axis('off')

# Table section
ax_table = fig.add_axes([0.05, 0.03, 0.90, 0.28], facecolor=DARK_BG)
ax_table.axis('off')

# Title for table section
ax_table.text(0.5, 0.98, 'FORWARD RETURNS WHEN GOLD >30% ABOVE 52-WEEK MA',
              transform=ax_table.transAxes, fontsize=16, fontweight='bold',
              color='white', ha='center', va='top',
              fontfamily='monospace')

ax_table.text(0.5, 0.86, 'Modern Era (1985-Present)  |  n=7 instances',
              transform=ax_table.transAxes, fontsize=12,
              color=DOLDRUMS, ha='center', va='top',
              fontfamily='monospace')

# Table data
headers = ['PERIOD', 'MEAN', 'MEDIAN', 'WIN RATE']
data = [
    ['1 Week', '-2.1%', '-3.3%', '29%'],
    ['2 Weeks', '-2.0%', '-3.7%', '29%'],
    ['1 Month', '-4.0%', '-4.5%', '14%'],
    ['6 Weeks', '-9.6%', '-9.4%', '0%'],
]

# Table positioning
table_top = 0.74
row_height = 0.13
col_positions = [0.18, 0.40, 0.60, 0.82]

# Draw header row
for i, (header, col_x) in enumerate(zip(headers, col_positions)):
    ax_table.text(col_x, table_top, header, transform=ax_table.transAxes,
                  fontsize=13, fontweight='bold', color=OCEAN,
                  ha='center', va='center', fontfamily='monospace')

# Draw separator line
ax_table.plot([0.10, 0.90], [table_top - 0.04, table_top - 0.04],
              color=OCEAN, linewidth=2, transform=ax_table.transAxes)

# Draw data rows
for row_idx, row in enumerate(data):
    y_pos = table_top - 0.10 - (row_idx * row_height)

    for col_idx, (value, col_x) in enumerate(zip(row, col_positions)):
        # Color coding for values
        if col_idx == 0:  # Period column
            color = 'white'
        elif col_idx == 3:  # Win rate column
            pct = int(value.replace('%', ''))
            if pct <= 20:
                color = PORT
            elif pct <= 40:
                color = DUSK
            else:
                color = SEA
        else:  # Mean/Median columns
            if value.startswith('-'):
                color = PORT
            else:
                color = SEA

        fontweight = 'bold' if col_idx > 0 else 'normal'
        ax_table.text(col_x, y_pos, value, transform=ax_table.transAxes,
                      fontsize=14, fontweight=fontweight, color=color,
                      ha='center', va='center', fontfamily='monospace')

# Add key insight box
insight_y = 0.12
ax_table.add_patch(FancyBboxPatch((0.12, insight_y - 0.06), 0.76, 0.12,
                                   boxstyle="round,pad=0.02,rounding_size=0.02",
                                   facecolor=DARKER_BG, edgecolor=DUSK,
                                   linewidth=2.5, transform=ax_table.transAxes))

ax_table.text(0.5, insight_y + 0.01,
              'Current: 39% above 52w MA (98th percentile)  |  6-week win rate: 0%',
              transform=ax_table.transAxes, fontsize=13, fontweight='bold',
              color=DUSK, ha='center', va='center', fontfamily='monospace')

# Branding
fig.text(0.03, 0.005, 'LIGHTHOUSE MACRO', fontsize=11, color=OCEAN,
         fontweight='bold', fontfamily='monospace', alpha=0.9)
fig.text(0.97, 0.005, 'MACRO, ILLUMINATED.', fontsize=10, color=DOLDRUMS,
         ha='right', fontfamily='monospace', alpha=0.7)

plt.savefig('/Users/bob/gold_extension_study.png', dpi=200,
            facecolor=DARK_BG, edgecolor='none', bbox_inches='tight',
            pad_inches=0.1)
plt.close()

print("Saved: /Users/bob/gold_extension_study.png")
