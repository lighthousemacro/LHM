"""
Pillar 12 Sentiment - Table PNGs
Renders the two article tables as styled PNGs in white theme
to match the other pillar_12 figures.
"""

import matplotlib.pyplot as plt
from pathlib import Path

COLORS = {
    'ocean': '#2389BB',
    'dusk': '#FF6723',
    'sky': '#23BBFF',
    'sea': '#00BB89',
    'venus': '#FF2389',
    'doldrums': '#898989',
    'fog': '#D1D1D1',
    'starboard': '#238923',
    'port': '#892323',
}

THEME = {
    'bg': '#FFFFFF',
    'fg': '#1a1a1a',
    'muted': '#555555',
    'spine': '#898989',
    'primary': '#2389BB',
}

OUTPUT_DIR = Path('/Users/bob/LHM/Outputs/Educational_Charts/Sentiment_Post_12/white')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def add_frame(fig):
    # Ocean border
    fig.patches.append(plt.Rectangle(
        (0, 0), 1, 1, transform=fig.transFigure,
        fill=False, edgecolor=COLORS['ocean'], linewidth=4.0,
        zorder=100, clip_on=False,
    ))
    # Top accent bar
    ax_top = fig.add_axes([0.02, 0.955, 0.96, 0.006])
    ax_top.axhspan(0, 1, 0, 0.67, color=COLORS['ocean'])
    ax_top.axhspan(0, 1, 0.67, 1.0, color=COLORS['dusk'])
    ax_top.set_xlim(0, 1); ax_top.set_ylim(0, 1); ax_top.axis('off')
    # Bottom accent bar
    ax_bot = fig.add_axes([0.02, 0.025, 0.96, 0.006])
    ax_bot.axhspan(0, 1, 0, 0.67, color=COLORS['ocean'])
    ax_bot.axhspan(0, 1, 0.67, 1.0, color=COLORS['dusk'])
    ax_bot.set_xlim(0, 1); ax_bot.set_ylim(0, 1); ax_bot.axis('off')


def brand_text(fig, title, subtitle):
    fig.text(0.05, 0.92, 'LIGHTHOUSE MACRO', fontsize=9, fontweight='bold',
             color=COLORS['ocean'], ha='left', family='sans-serif')
    fig.text(0.95, 0.92, 'MACRO, ILLUMINATED.', fontsize=8,
             color=COLORS['doldrums'], ha='right', style='italic', family='sans-serif')
    fig.text(0.5, 0.86, title, fontsize=15, fontweight='bold',
             color=THEME['fg'], ha='center', family='sans-serif')
    fig.text(0.5, 0.815, subtitle, fontsize=10, style='italic',
             color=THEME['muted'], ha='center', family='sans-serif')


def render_table(ax, columns, data, col_widths=None):
    n_cols = len(columns)
    if col_widths is None:
        col_widths = [1.0 / n_cols] * n_cols

    table = ax.table(
        cellText=data,
        colLabels=columns,
        colWidths=col_widths,
        cellLoc='center',
        loc='center',
    )
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1, 2.2)

    for (row, col), cell in table.get_celld().items():
        cell.set_edgecolor(COLORS['doldrums'])
        cell.set_linewidth(0.8)
        if row == 0:
            cell.set_facecolor(COLORS['ocean'])
            cell.set_text_props(color='white', fontweight='bold', fontsize=11)
            cell.set_height(cell.get_height() * 1.1)
        else:
            if row % 2 == 0:
                cell.set_facecolor('#F4F7F9')
            else:
                cell.set_facecolor('#FFFFFF')
            cell.set_text_props(color=THEME['fg'])


def save(fig, name):
    path = OUTPUT_DIR / f'{name}.png'
    fig.savefig(path, dpi=200, bbox_inches=None, pad_inches=0.025,
                facecolor=THEME['bg'], edgecolor='none')
    print(f"Saved: {path}")
    plt.close(fig)


def table_integration():
    fig = plt.figure(figsize=(11, 5.5), facecolor=THEME['bg'])
    add_frame(fig)
    brand_text(
        fig,
        'Integration: Sentiment Sizes the Trade',
        'Multi-pillar convergence matrix. Sentiment is the sizer, not the signal.',
    )

    ax = fig.add_axes([0.05, 0.12, 0.90, 0.62])
    ax.axis('off')
    ax.set_facecolor(THEME['bg'])

    columns = ['Fundamentals', 'Structure', 'Sentiment', 'Action']
    data = [
        ['Bullish', 'Confirming', 'Fear (SPI > +1.0)',      'Maximum conviction long'],
        ['Bullish', 'Confirming', 'Neutral',                 'Normal long position'],
        ['Bullish', 'Confirming', 'Euphoria (SPI < -1.0)',   'Reduce size, tighten stops'],
        ['Bearish', 'Broken',     'Fear (SPI > +1.5)',       'Tactical bounce only'],
        ['Bearish', 'Broken',     'Neutral / Euphoria',      'Maximum defensive'],
    ]
    render_table(ax, columns, data, col_widths=[0.18, 0.18, 0.27, 0.37])

    fig.text(0.5, 0.06,
             'Lighthouse Macro | Diagnostic Dozen Framework',
             fontsize=8, color=COLORS['doldrums'], ha='center', style='italic')

    save(fig, 'pillar_12_table_integration')


def table_current_state():
    fig = plt.figure(figsize=(11, 5.0), facecolor=THEME['bg'])
    add_frame(fig)
    brand_text(
        fig,
        'Where We Are Now: Composite Readings',
        'Sentiment, structure, and the master composite as of the latest data.',
    )

    ax = fig.add_axes([0.05, 0.12, 0.90, 0.62])
    ax.axis('off')
    ax.set_facecolor(THEME['bg'])

    columns = ['Index', 'Value', 'As Of', 'Regime']
    data = [
        ['SPI', '+0.45', 'Mar 10', 'Neutral (slight fear lean)'],
        ['SSD', '-1.28', 'Mar 10', 'Euphoria dominates'],
        ['MSI', '-1.41', 'Mar 11', 'Structure broken'],
        ['MRI', '+0.02', 'Mar 11', 'Neutral regime'],
    ]
    render_table(ax, columns, data, col_widths=[0.14, 0.16, 0.16, 0.54])

    fig.text(0.5, 0.06,
             'Lighthouse Macro | Data thru Mar 11, 2026 | Pulled Apr 12, 2026',
             fontsize=8, color=COLORS['doldrums'], ha='center', style='italic')

    save(fig, 'pillar_12_table_current')


if __name__ == '__main__':
    table_integration()
    table_current_state()
    print('\nDone.')
