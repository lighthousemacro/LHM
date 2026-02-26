#!/usr/bin/env python3
"""
Generate CLI Chart: Composite over time with rolling 63D BTC returns
====================================================================
Dual-axis: CLI (LHS, Dusk) vs Rolling 63D BTC Return (RHS, primary/Ocean/Sky)
Regime bands on CLI axis.

Usage:
    python cli_chart.py           # both themes
    python cli_chart.py --dark    # dark only
    python cli_chart.py --white   # white only
"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.image as mpimg
from matplotlib.ticker import FuncFormatter
from datetime import datetime

# ============================================
# PATHS
# ============================================
BASE_PATH = '/Users/bob/LHM'
DATA_PATH = f'{BASE_PATH}/Scripts/backtest/cli_chart_data.csv'
OUTPUT_BASE = f'{BASE_PATH}/Outputs/CLI_Charts'
ICON_PATH = f'{BASE_PATH}/Brand/icon_transparent_128.png'

COLORS = {
    'ocean': '#2389BB',
    'dusk': '#FF6723',
    'sky': '#00BBFF',
    'venus': '#FF2389',
    'sea': '#00BB89',
    'doldrums': '#898989',
    'starboard': '#238923',
    'port': '#892323',
}

THEME = {}
OUTPUT_DIR = ''


def set_theme(mode='dark'):
    global THEME, OUTPUT_DIR
    if mode == 'dark':
        THEME.update({
            'bg': '#0A1628',
            'fg': '#e6edf3',
            'muted': '#8b949e',
            'spine': '#1e3350',
            'zero_line': '#e6edf3',
            'brand_color': COLORS['sky'],
            'brand2_color': COLORS['dusk'],
            'primary': COLORS['sky'],
            'secondary': COLORS['dusk'],
            'tertiary': COLORS['sea'],
            'accent': COLORS['venus'],
            'fill_alpha': 0.20,
            'box_bg': '#0A1628',
            'box_edge': COLORS['sky'],
            'legend_bg': '#0f1f38',
            'legend_fg': '#e6edf3',
            'mode': 'dark',
        })
    else:
        THEME.update({
            'bg': '#ffffff',
            'fg': '#1a1a1a',
            'muted': '#555555',
            'spine': '#898989',
            'zero_line': '#D1D1D1',
            'brand_color': COLORS['ocean'],
            'brand2_color': COLORS['dusk'],
            'primary': COLORS['ocean'],
            'secondary': COLORS['dusk'],
            'tertiary': COLORS['sea'],
            'accent': COLORS['venus'],
            'fill_alpha': 0.15,
            'box_bg': '#ffffff',
            'box_edge': COLORS['ocean'],
            'legend_bg': '#f8f8f8',
            'legend_fg': '#1a1a1a',
            'mode': 'white',
        })
    OUTPUT_DIR = os.path.join(OUTPUT_BASE, mode)
    os.makedirs(OUTPUT_DIR, exist_ok=True)


# ============================================
# STYLING HELPERS
# ============================================
def new_fig(figsize=(14, 8)):
    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_facecolor(THEME['bg'])
    ax.set_facecolor(THEME['bg'])
    fig.subplots_adjust(top=0.88, bottom=0.08, left=0.06, right=0.94)
    return fig, ax


def style_ax(ax, right_primary=True):
    ax.grid(False)
    for spine in ['top', 'right', 'left', 'bottom']:
        ax.spines[spine].set_visible(True)
        ax.spines[spine].set_linewidth(0.5)
        ax.spines[spine].set_color(THEME['spine'])
    ax.tick_params(colors=THEME['fg'], labelsize=10)
    ax.xaxis.label.set_color(THEME['fg'])
    ax.yaxis.label.set_color(THEME['fg'])
    ax.title.set_color(THEME['fg'])
    if right_primary:
        ax.yaxis.tick_right()
        ax.yaxis.set_label_position('right')


def style_dual_ax(ax1, ax2, c1, c2):
    style_ax(ax1, right_primary=False)
    ax1.grid(False)
    ax2.grid(False)
    for spine in ax2.spines.values():
        spine.set_color(THEME['spine'])
        spine.set_linewidth(0.5)
    ax1.tick_params(axis='both', which='both', length=0)
    ax1.tick_params(axis='y', labelcolor=c1, labelsize=10)
    ax2.tick_params(axis='both', which='both', length=0)
    ax2.tick_params(axis='y', labelcolor=c2, labelsize=10)
    ax1.yaxis.set_tick_params(which='both', right=False)
    ax2.yaxis.set_tick_params(which='both', left=False)


def brand_fig(fig, title, subtitle=None, source=None):
    fig.patch.set_facecolor(THEME['bg'])
    OCEAN = '#2389BB'
    DUSK = '#FF6723'

    # Lighthouse icon (top-left, next to text)
    if os.path.exists(ICON_PATH):
        icon_img = mpimg.imread(ICON_PATH)
        icon_w = 0.018
        icon_aspect = icon_img.shape[0] / icon_img.shape[1]
        fig_aspect = fig.get_figwidth() / fig.get_figheight()
        icon_h = icon_w * icon_aspect * fig_aspect
        icon_ax = fig.add_axes([0.012, 0.985 - icon_h, icon_w, icon_h])
        icon_ax.imshow(icon_img, aspect='equal')
        icon_ax.axis('off')

    fig.text(0.035, 0.98, 'LIGHTHOUSE MACRO', fontsize=13,
             color=OCEAN, fontweight='bold', va='top')
    fig.text(0.97, 0.98, datetime.now().strftime('%B %d, %Y'),
             fontsize=11, color=THEME['muted'], ha='right', va='top')

    bar = fig.add_axes([0.03, 0.955, 0.94, 0.004])
    bar.axhspan(0, 1, 0, 0.67, color=OCEAN)
    bar.axhspan(0, 1, 0.67, 1.0, color=DUSK)
    bar.set_xlim(0, 1); bar.set_ylim(0, 1); bar.axis('off')

    bbar = fig.add_axes([0.03, 0.035, 0.94, 0.004])
    bbar.axhspan(0, 1, 0, 0.67, color=OCEAN)
    bbar.axhspan(0, 1, 0.67, 1.0, color=DUSK)
    bbar.set_xlim(0, 1); bbar.set_ylim(0, 1); bbar.axis('off')

    fig.text(0.97, 0.025, 'MACRO, ILLUMINATED.', fontsize=13,
             color=OCEAN, ha='right', va='top', style='italic', fontweight='bold')

    if source:
        date_str = datetime.now().strftime('%m.%d.%Y')
        fig.text(0.03, 0.022, f'Lighthouse Macro | {source}; {date_str}',
                 fontsize=9, color=THEME['muted'], ha='left', va='top', style='italic')

    fig.suptitle(title, fontsize=15, fontweight='bold', y=0.945, color=THEME['fg'])
    if subtitle:
        fig.text(0.5, 0.895, subtitle, fontsize=14, ha='center',
                 color=OCEAN, style='italic')


def add_last_value_label(ax, y_data, color, fmt='{:.1f}%', side='right', fontsize=9, pad=0.3):
    if len(y_data) == 0:
        return
    last_y = float(y_data.iloc[-1]) if hasattr(y_data, 'iloc') else float(y_data[-1])
    label = fmt.format(last_y)
    pill = dict(boxstyle=f'round,pad={pad}', facecolor=color, edgecolor=color, alpha=0.95)
    if side == 'right':
        ax.annotate(label, xy=(1.0, last_y), xycoords=('axes fraction', 'data'),
                    fontsize=fontsize, fontweight='bold', color='white',
                    ha='left', va='center', xytext=(6, 0), textcoords='offset points',
                    bbox=pill)
    else:
        ax.annotate(label, xy=(0.0, last_y), xycoords=('axes fraction', 'data'),
                    fontsize=fontsize, fontweight='bold', color='white',
                    ha='right', va='center', xytext=(-6, 0), textcoords='offset points',
                    bbox=pill)


def set_xlim_to_data(ax, idx):
    padding_left = pd.Timedelta(days=30)
    padding_right = pd.Timedelta(days=180)
    ax.set_xlim(idx.min() - padding_left, idx.max() + padding_right)


def legend_style():
    return dict(
        framealpha=0.95,
        facecolor=THEME['legend_bg'],
        edgecolor=THEME['spine'],
        labelcolor=THEME['legend_fg'],
    )


def save_fig(fig, filename):
    border_color = THEME['primary']
    fig.patches.append(plt.Rectangle(
        (0, 0), 1, 1, transform=fig.transFigure,
        fill=False, edgecolor=border_color, linewidth=1.5,
        zorder=100, clip_on=False
    ))
    filepath = os.path.join(OUTPUT_DIR, filename)
    fig.savefig(filepath, dpi=200, bbox_inches='tight', pad_inches=0.15,
                facecolor=THEME['bg'], edgecolor='none')
    plt.close(fig)
    print(f'  Saved: {filepath}')
    return filepath


def align_yaxis_zero(a1, a2):
    y1_min, y1_max = a1.get_ylim()
    y2_min, y2_max = a2.get_ylim()
    r1 = abs(y1_min) / max(abs(y1_max), 1e-6)
    r2 = abs(y2_min) / max(abs(y2_max), 1e-6)
    r = max(r1, r2)
    a1.set_ylim(bottom=-r * abs(y1_max), top=y1_max)
    a2.set_ylim(bottom=-r * abs(y2_max), top=y2_max)


# ============================================
# MAIN CHART
# ============================================
def chart_cli(fwd_days=63):
    """CLI vs forward BTC returns, dual-axis with regime bands."""
    df = pd.read_csv(DATA_PATH, index_col=0, parse_dates=True)

    cli =df['CLI'].dropna()
    btc_price = df['BTC_Price'].dropna()

    # Compute FORWARD returns: what BTC did over the NEXT fwd_days from each date
    btc_fwd = (btc_price.shift(-fwd_days) / btc_price - 1) * 100
    btc_fwd = btc_fwd.dropna()

    # Align
    common = cli.index.intersection(btc_fwd.index)
    cli_plot = cli.loc[common]
    btc_plot = btc_fwd.loc[common]

    # Current values
    last_cli = cli.dropna().iloc[-1]
    if last_cli > 0.45:
        regime = "Q5"
    elif last_cli > 0.14:
        regime = "Q4"
    elif last_cli > -0.16:
        regime = "Q3"
    elif last_cli > -0.57:
        regime = "Q2"
    else:
        regime = "Q1"

    fig, ax1 = new_fig()
    ax2 = ax1.twinx()

    c_cli =THEME['secondary']
    c_btc = THEME['primary']

    # Quintile bands on CLI (boundaries from data: 20th=-0.57, 40th=-0.16, 60th=0.14, 80th=0.45)
    Q1_TOP = -0.57
    Q2_TOP = -0.16
    Q3_TOP = 0.14
    Q4_TOP = 0.45
    ax1.axhspan(-5.0, Q1_TOP, color=COLORS['port'], alpha=0.10, zorder=0)       # Q1
    ax1.axhspan(Q1_TOP, Q2_TOP, color=COLORS['dusk'], alpha=0.08, zorder=0)     # Q2
    ax1.axhspan(Q2_TOP, Q3_TOP, color=COLORS['sea'], alpha=0.06, zorder=0)      # Q3
    ax1.axhspan(Q3_TOP, Q4_TOP, color=COLORS['sea'], alpha=0.12, zorder=0)      # Q4
    ax1.axhspan(Q4_TOP, 5.0, color=COLORS['starboard'], alpha=0.08, zorder=0)   # Q5

    # Zero line
    ax1.axhline(0, color=COLORS['doldrums'], linewidth=0.8, linestyle='--', zorder=1)

    # Plot forward BTC returns on RHS (behind CLI)
    ax2.plot(btc_plot.index, btc_plot.values, color=c_btc, linewidth=1.2, alpha=0.85,
             label=f'BTC {fwd_days}D Forward Return', zorder=2)
    ax2.fill_between(btc_plot.index, 0, btc_plot.values,
                     where=btc_plot.values > 0, color=c_btc, alpha=0.08, zorder=1)
    ax2.fill_between(btc_plot.index, 0, btc_plot.values,
                     where=btc_plot.values < 0, color=COLORS['port'], alpha=0.08, zorder=1)

    # Plot CLI on LHS (foreground)
    ax1.plot(cli_plot.index, cli_plot.values, color=c_cli, linewidth=2.0,
             label=f'CLI ({last_cli:+.2f}, {regime})', zorder=5)

    # Quintile threshold lines
    for thresh in [Q1_TOP, Q2_TOP, Q3_TOP, Q4_TOP]:
        ax1.axhline(thresh, color=COLORS['doldrums'], linewidth=0.4, linestyle=':', alpha=0.4, zorder=1)

    # Band labels on right edge (use axes coords for x so they sit at the far right)
    band_label_style = dict(fontsize=8, fontweight='bold', ha='right', va='center',
                            alpha=0.65, zorder=6)
    ax1.text(0.995, (Q4_TOP + 1.2) / 2, 'Q5', color=COLORS['sea'], transform=ax1.get_yaxis_transform(), **band_label_style)
    ax1.text(0.995, (Q3_TOP + Q4_TOP) / 2, 'Q4', color=COLORS['sea'], transform=ax1.get_yaxis_transform(), **band_label_style)
    ax1.text(0.995, (Q2_TOP + Q3_TOP) / 2, 'Q3', color=THEME['muted'], transform=ax1.get_yaxis_transform(), **band_label_style)
    ax1.text(0.995, (Q1_TOP + Q2_TOP) / 2, 'Q2', color=COLORS['dusk'], transform=ax1.get_yaxis_transform(), **band_label_style)
    ax1.text(0.995, (Q1_TOP - 0.8) / 2, 'Q1', color=COLORS['dusk'], transform=ax1.get_yaxis_transform(), **band_label_style)

    # Format axes
    ax1.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.1f}'))
    ax2.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.0f}%'))

    align_yaxis_zero(ax1, ax2)
    style_dual_ax(ax1, ax2, c_cli, c_btc)
    set_xlim_to_data(ax1, cli_plot.index)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    # Pills
    add_last_value_label(ax1, cli_plot, color=c_cli, fmt='{:+.2f}', side='left')
    add_last_value_label(ax2, btc_plot, color=c_btc, fmt='{:+.0f}%', side='right')

    # Legend
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', **legend_style())

    # Box 1 (top-right area): What is this
    box1_text = ('Weighted composite across 3\n'
                 'liquidity impulse channels:\n'
                 '  \u2022 Dollar Momentum\n'
                 '  \u2022 Reserve Dynamics\n'
                 '  \u2022 Stablecoin Flows')
    ax1.text(0.72, 0.97, box1_text, transform=ax1.transAxes,
             fontsize=10, color=THEME['fg'], ha='left', va='top',
             bbox=dict(boxstyle='round,pad=0.5',
                       facecolor=THEME['bg'], edgecolor='#2389BB',
                       alpha=0.92, linewidth=1.5))

    # Box 2 (bottom-center): How to read + stats (quintiles)
    if fwd_days == 21:
        box2_text = (f'{fwd_days}D Fwd Returns:   Avg Ret  Slugging\n'
                     ' Q5 (Strongest):       +8.6%    4.81x\n'
                     ' Q4:                   +2.0%    1.43x\n'
                     ' Q3:                   +1.0%    1.20x\n'
                     ' Q2:                   +0.5%    1.11x\n'
                     ' Q1 (Weakest):         -4.8%    0.45x\n\n'
                     f'Q5-Q1: +13.4% (t=14.2, p<0.0001) | n={len(cli_plot):,}')
    elif fwd_days == 42:
        box2_text = (f'{fwd_days}D Fwd Returns:   Avg Ret  Slugging\n'
                     ' Q5 (Strongest):      +14.3%    4.50x\n'
                     ' Q4:                   +6.0%    2.17x\n'
                     ' Q3:                   +3.9%    1.56x\n'
                     ' Q2:                   -0.2%    0.97x\n'
                     ' Q1 (Weakest):         -7.8%    0.43x\n\n'
                     f'Q5-Q1: +22.1% (t=15.6, p<0.0001) | n={len(cli_plot):,}')
    else:
        box2_text = (f'{fwd_days}D Fwd Returns:   Avg Ret  Slugging\n'
                     ' Q5 (Strongest):      +17.2%    3.70x\n'
                     ' Q4:                  +11.1%    3.12x\n'
                     ' Q3:                   +9.0%    2.45x\n'
                     ' Q2:                   -2.1%    0.82x\n'
                     ' Q1 (Weakest):         -9.8%    0.39x\n\n'
                     f'Q5-Q1: +27.0% (t=15.0, p<0.0001) | n={len(cli_plot):,}')

    ax1.text(0.55, 0.03, box2_text, transform=ax1.transAxes,
             fontsize=9.5, color=THEME['fg'], ha='center', va='bottom',
             family='monospace',
             bbox=dict(boxstyle='round,pad=0.5',
                       facecolor=THEME['bg'], edgecolor='#2389BB',
                       alpha=0.92, linewidth=1.5))

    # Branding
    brand_fig(fig,
              'Crypto Liquidity Impulse',
              f'CLI vs {fwd_days}-Day Forward BTC Returns',
              'FRED, DefiLlama, Yahoo Finance')

    save_fig(fig, f'cli_vs_btc_fwd{fwd_days}d.png')


def chart_cli_regime_bars():
    """Bar chart: quintile regime forward returns."""
    fig, ax = new_fig()

    quintiles = ['Q1\n(Weakest)', 'Q2', 'Q3', 'Q4', 'Q5\n(Strongest)']
    # From backtest: expanding z-score, final config
    ret_21d = [-4.8, 0.5, 1.0, 2.0, 8.6]
    ret_42d = [-7.8, -0.2, 3.9, 6.0, 14.3]
    ret_63d = [-9.8, -2.1, 9.0, 11.1, 17.2]

    x = np.arange(len(quintiles))
    width = 0.25

    bars1 = ax.bar(x - width, ret_21d, width, label='21D Fwd', color=COLORS['ocean'], zorder=3)
    bars2 = ax.bar(x, ret_42d, width, label='42D Fwd', color=COLORS['dusk'], zorder=3)
    bars3 = ax.bar(x + width, ret_63d, width, label='63D Fwd', color=COLORS['sky'], zorder=3)

    # Add value labels on each bar
    for bars in [bars1, bars2, bars3]:
        for bar in bars:
            val = bar.get_height()
            va = 'bottom' if val >= 0 else 'top'
            offset = 0.4 if val >= 0 else -0.4
            ax.text(bar.get_x() + bar.get_width() / 2, val + offset,
                    f'{val:+.1f}%', ha='center', va=va,
                    fontsize=8, fontweight='bold', color=THEME['fg'])

    ax.axhline(0, color=COLORS['doldrums'], linewidth=0.8, linestyle='--', zorder=1)
    ax.set_xticks(x)
    ax.set_xticklabels(quintiles, fontsize=11, color=THEME['fg'])
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:+.0f}%'))

    # Add padding so labels don't clip
    ymin, ymax = ax.get_ylim()
    ax.set_ylim(ymin - 2.0, ymax + 3.0)

    style_ax(ax, right_primary=True)
    ax.tick_params(axis='both', which='both', length=0)

    ax.legend(loc='upper left', **legend_style())

    # Annotation box
    ann_text = ('Weighted composite across 3 liquidity impulse channels:\n'
                'Dollar Momentum | Reserve Dynamics | Stablecoin Flows\n\n'
                'Q5-Q1 Spread:                Slugging (Q1 / Q5):\n'
                '21D: +13.4%  (t = 14.2)      0.45x  /  4.81x\n'
                '42D: +22.1%  (t = 15.6)      0.43x  /  4.50x\n'
                '63D: +27.0%  (t = 15.0)      0.39x  /  3.70x\n'
                'All p < 0.0001             Monotonic at all horizons')
    ax.text(0.52, 0.95, ann_text, transform=ax.transAxes,
            fontsize=10, color=THEME['fg'], ha='center', va='top',
            family='monospace',
            bbox=dict(boxstyle='round,pad=0.6',
                      facecolor=THEME['bg'], edgecolor='#2389BB',
                      alpha=0.92, linewidth=1.5))

    brand_fig(fig,
              'Crypto Liquidity Impulse',
              'Average BTC Forward Returns by CLI Quintile (2018-2025)',
              'Lighthouse Macro Backtest')

    save_fig(fig, 'cli_regime_bars.png')


def main():
    themes = ['dark', 'white']
    if '--dark' in sys.argv:
        themes = ['dark']
    elif '--white' in sys.argv:
        themes = ['white']

    for mode in themes:
        print(f'\n  === {mode.upper()} THEME ===')
        set_theme(mode)
        chart_cli(fwd_days=21)
        chart_cli(fwd_days=42)
        chart_cli(fwd_days=63)
        chart_cli_regime_bars()


if __name__ == '__main__':
    main()
