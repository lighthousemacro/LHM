"""
Gold Extension Study - Standalone Table
Lighthouse Macro
"""

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

# Lighthouse colors
OCEAN = '#0089D1'
DUSK = '#FF6723'
DOLDRUMS = '#D3D6D9'
PORT = '#FF0000'
DARK_BG = '#1a1a2e'
DARKER_BG = '#0f0f1a'

# Create figure
fig = plt.figure(figsize=(10, 6), facecolor=DARK_BG)
ax = fig.add_axes([0.05, 0.1, 0.90, 0.85], facecolor=DARK_BG)
ax.axis('off')

# Title
ax.text(0.5, 0.95, 'FORWARD RETURNS WHEN GOLD >30% ABOVE 52-WEEK MA',
        transform=ax.transAxes, fontsize=18, fontweight='bold',
        color='white', ha='center', va='top', fontfamily='monospace')

ax.text(0.5, 0.85, 'Modern Era (1985-Present)  |  n=7 instances',
        transform=ax.transAxes, fontsize=13,
        color=DOLDRUMS, ha='center', va='top', fontfamily='monospace')

# Table data
headers = ['PERIOD', 'MEAN', 'MEDIAN', 'WIN RATE']
data = [
    ['1 Week', '-2.1%', '-3.3%', '29%'],
    ['2 Weeks', '-2.0%', '-3.7%', '29%'],
    ['1 Month', '-4.0%', '-4.5%', '14%'],
    ['6 Weeks', '-9.6%', '-9.4%', '0%'],
]

# Table positioning
table_top = 0.72
row_height = 0.11
col_positions = [0.18, 0.40, 0.60, 0.82]

# Draw header row
for header, col_x in zip(headers, col_positions):
    ax.text(col_x, table_top, header, transform=ax.transAxes,
            fontsize=14, fontweight='bold', color=OCEAN,
            ha='center', va='center', fontfamily='monospace')

# Draw separator line
ax.plot([0.08, 0.92], [table_top - 0.04, table_top - 0.04],
        color=OCEAN, linewidth=2.5, transform=ax.transAxes)

# Draw data rows
for row_idx, row in enumerate(data):
    y_pos = table_top - 0.10 - (row_idx * row_height)

    for col_idx, (value, col_x) in enumerate(zip(row, col_positions)):
        if col_idx == 0:
            color = 'white'
        elif col_idx == 3:
            pct = int(value.replace('%', ''))
            color = PORT if pct <= 20 else DUSK
        else:
            color = PORT if value.startswith('-') else 'white'

        fontweight = 'bold' if col_idx > 0 else 'normal'
        ax.text(col_x, y_pos, value, transform=ax.transAxes,
                fontsize=16, fontweight=fontweight, color=color,
                ha='center', va='center', fontfamily='monospace')

# Key insight box
insight_y = 0.18
ax.add_patch(FancyBboxPatch((0.08, insight_y - 0.06), 0.84, 0.12,
                             boxstyle="round,pad=0.02,rounding_size=0.02",
                             facecolor=DARKER_BG, edgecolor=DUSK,
                             linewidth=2.5, transform=ax.transAxes))

ax.text(0.5, insight_y + 0.01,
        'Current: 39% above 52w MA (98th percentile)  |  6-week win rate: 0%',
        transform=ax.transAxes, fontsize=13, fontweight='bold',
        color=DUSK, ha='center', va='center', fontfamily='monospace')

# Branding
fig.text(0.03, 0.02, 'LIGHTHOUSE MACRO', fontsize=11, color=OCEAN,
         fontweight='bold', fontfamily='monospace', alpha=0.9)
fig.text(0.97, 0.02, 'MACRO, ILLUMINATED.', fontsize=10, color=DOLDRUMS,
         ha='right', fontfamily='monospace', alpha=0.7)

plt.savefig('/Users/bob/gold_extension_table.png', dpi=200,
            facecolor=DARK_BG, edgecolor='none', bbox_inches='tight',
            pad_inches=0.15)
plt.close()

print("Saved: /Users/bob/gold_extension_table.png")
