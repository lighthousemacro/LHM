#!/usr/bin/env python3
"""
Regenerate CLI (Fig 2) and DXY vs BTC (Fig 1) charts in both themes.
Output to Outputs/Charts/ with standard naming.

Usage:
    python3 regen_cli_dxy.py
"""

import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.image as mpimg
from matplotlib.ticker import FuncFormatter, FixedLocator
from datetime import datetime
import yfinance as yf
import os
import warnings
warnings.filterwarnings('ignore')

# =============================================================================
# PATHS & CONFIG
# =============================================================================
BASE_PATH = '/Users/bob/LHM'
DB_PATH = f'{BASE_PATH}/Data/databases/Lighthouse_Master.db'
ICON_PATH = f'{BASE_PATH}/Brand/icon_transparent_128.png'
CLI_DATA = f'{BASE_PATH}/Scripts/backtest/cli_chart_data.csv'
OUT_BASE = f'{BASE_PATH}/Outputs/Charts'

DATE_STR = datetime.now().strftime('%B %d, %Y')

# =============================================================================
# PALETTE
# =============================================================================
C = {
    'ocean':     '#2389BB',
    'dusk':      '#FF6723',
    'sky':       '#00BBFF',
    'venus':     '#FF2389',
    'sea':       '#00BB89',
    'doldrums':  '#898989',
    'starboard': '#238923',
    'port':      '#892323',
    'fog':       '#D1D1D1',
}

THEMES = {
    'white': {
        'bg': '#ffffff', 'fg': '#1a1a1a', 'muted': '#555555',
        'spine': '#898989', 'zero_line': '#D1D1D1',
        'primary': C['ocean'], 'secondary': C['dusk'],
        'legend_bg': '#f8f8f8', 'legend_fg': '#1a1a1a',
    },
    'dark': {
        'bg': '#0A1628', 'fg': '#e6edf3', 'muted': '#8b949e',
        'spine': '#1e3350', 'zero_line': '#e6edf3',
        'primary': C['sky'], 'secondary': C['dusk'],
        'legend_bg': '#0f1f38', 'legend_fg': '#e6edf3',
    },
}

T = {}  # Active theme


def set_theme(mode):
    global T
    T = THEMES[mode].copy()
    T['mode'] = mode


# =============================================================================
# STYLING HELPERS
# =============================================================================

def new_fig(figsize=(14, 8)):
    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_facecolor(T['bg'])
    ax.set_facecolor(T['bg'])
    fig.subplots_adjust(top=0.88, bottom=0.08, left=0.06, right=0.94)
    return fig, ax


def style_ax(ax, right_primary=True):
    ax.grid(False)
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_color(T['spine'])
        spine.set_linewidth(0.5)
    ax.tick_params(axis='both', which='both', length=0, labelsize=10,
                   colors=T['muted'])
    if right_primary:
        ax.yaxis.tick_right()
        ax.yaxis.set_label_position('right')


def style_dual_ax(ax1, ax2, c1, c2):
    style_ax(ax1, right_primary=False)
    ax1.tick_params(axis='y', labelcolor=c1)
    for spine in ax2.spines.values():
        spine.set_visible(True)
        spine.set_color(T['spine'])
        spine.set_linewidth(0.5)
    ax2.grid(False)
    ax2.tick_params(axis='both', which='both', length=0)
    ax2.tick_params(axis='y', labelcolor=c2, labelsize=10)


def set_xlim_to_data(ax, idx, pad_left=30, pad_right=180):
    ax.set_xlim(idx.min() - pd.Timedelta(days=pad_left),
                idx.max() + pd.Timedelta(days=pad_right))


def brand_fig(fig, title, subtitle=None, source=None, data_date=None):
    fig.patch.set_facecolor(T['bg'])
    OCEAN, DUSK = C['ocean'], C['dusk']

    if os.path.exists(ICON_PATH):
        icon_img = mpimg.imread(ICON_PATH)
        icon_w = 0.018
        icon_aspect = icon_img.shape[0] / icon_img.shape[1]
        fig_aspect = fig.get_figwidth() / fig.get_figheight()
        icon_h = icon_w * icon_aspect * fig_aspect
        icon_ax = fig.add_axes([0.012, 0.985 - icon_h, icon_w, icon_h])
        icon_ax.imshow(icon_img, aspect='equal')
        icon_ax.axis('off')

    fig.text(0.035, 0.98, 'LIGHTHOUSE MACRO', fontsize=13, fontweight='bold',
             color=OCEAN, va='top')
    fig.text(0.97, 0.98, DATE_STR, fontsize=11, color=T['muted'],
             va='top', ha='right')

    bar = fig.add_axes([0.03, 0.955, 0.94, 0.004])
    bar.axhspan(0, 1, 0, 0.67, color=OCEAN)
    bar.axhspan(0, 1, 0.67, 1.0, color=DUSK)
    bar.set_xlim(0, 1); bar.set_ylim(0, 1); bar.axis('off')

    bbar = fig.add_axes([0.03, 0.035, 0.94, 0.004])
    bbar.axhspan(0, 1, 0, 0.67, color=OCEAN)
    bbar.axhspan(0, 1, 0.67, 1.0, color=DUSK)
    bbar.set_xlim(0, 1); bbar.set_ylim(0, 1); bbar.axis('off')

    fig.suptitle(title, fontsize=15, fontweight='bold', y=0.945,
                 color=T['fg'])
    if subtitle:
        fig.text(0.50, 0.895, subtitle, fontsize=14, fontstyle='italic',
                 ha='center', color=OCEAN)

    fig.text(0.97, 0.025, 'MACRO, ILLUMINATED.', fontsize=13, fontweight='bold',
             fontstyle='italic', color=OCEAN, ha='right', va='top')

    if source:
        pull_str = datetime.now().strftime('%m.%d.%Y')
        if data_date is not None:
            if isinstance(data_date, str):
                data_date = pd.Timestamp(data_date)
            data_str = data_date.strftime('%m.%d.%Y')
            fig.text(0.03, 0.022,
                     f'Lighthouse Macro | {source} | Data thru {data_str} | Pulled {pull_str}',
                     fontsize=9, color=T['muted'], ha='left', va='top', style='italic')
        else:
            fig.text(0.03, 0.022, f'Lighthouse Macro | {source}; {pull_str}',
                     fontsize=9, color=T['muted'], ha='left', va='top', style='italic')


def add_pill(ax, y_data, color, fmt='{:.1f}', side='right', fontsize=9, pad=0.3):
    last_y = float(y_data.dropna().iloc[-1])
    label = fmt.format(last_y)
    pill = dict(boxstyle=f'round,pad={pad}', facecolor=color, edgecolor=color, alpha=0.95)
    if side == 'right':
        ax.annotate(label, xy=(1.0, last_y), xycoords=('axes fraction', 'data'),
                    fontsize=fontsize, fontweight='bold', color='white',
                    ha='left', va='center', xytext=(6, 0),
                    textcoords='offset points', bbox=pill, clip_on=False)
    else:
        ax.annotate(label, xy=(0.0, last_y), xycoords=('axes fraction', 'data'),
                    fontsize=fontsize, fontweight='bold', color='white',
                    ha='right', va='center', xytext=(-6, 0),
                    textcoords='offset points', bbox=pill, clip_on=False)


def legend_style():
    return dict(framealpha=0.95, facecolor=T['legend_bg'],
                edgecolor=T['spine'], labelcolor=T['legend_fg'])


def btc_log_ticks(ax):
    ticks = [5000, 10000, 15000, 20000, 30000, 40000, 50000,
             60000, 80000, 100000, 150000, 200000]
    ymin, ymax = ax.get_ylim()
    visible = [t for t in ticks if ymin <= t <= ymax]
    if visible:
        ax.yaxis.set_major_locator(FixedLocator(visible))
    ax.yaxis.set_major_formatter(FuncFormatter(
        lambda x, p: f'${x:,.0f}' if x >= 1000 else f'${x:.0f}'))
    ax.yaxis.set_minor_formatter(FuncFormatter(lambda x, p: ''))


def align_yaxis_zero(a1, a2):
    y1_min, y1_max = a1.get_ylim()
    y2_min, y2_max = a2.get_ylim()
    r1 = abs(y1_min) / max(abs(y1_max), 1e-6)
    r2 = abs(y2_min) / max(abs(y2_max), 1e-6)
    r = max(r1, r2)
    a1.set_ylim(bottom=-r * abs(y1_max), top=y1_max)
    a2.set_ylim(bottom=-r * abs(y2_max), top=y2_max)


def save_fig(fig, name, theme_mode):
    fig.patches.append(plt.Rectangle(
        (0, 0), 1, 1, transform=fig.transFigure,
        fill=False, edgecolor=C['ocean'], linewidth=4.0,
        zorder=100, clip_on=False
    ))
    out_dir = os.path.join(OUT_BASE, theme_mode)
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, name)
    fig.savefig(path, dpi=200, bbox_inches='tight', pad_inches=0.025,
                facecolor=T['bg'], edgecolor='none')
    plt.close(fig)
    print(f'  Saved: {path}')
    return path


def ann_box(ax, text, x=0.72, y=0.97, fontsize=10):
    ax.text(x, y, text, transform=ax.transAxes,
            fontsize=fontsize, color=T['fg'], ha='left', va='top',
            bbox=dict(boxstyle='round,pad=0.5', facecolor=T['bg'],
                      edgecolor=C['ocean'], alpha=0.92, linewidth=1.5))


# =============================================================================
# DATA LOADING
# =============================================================================

def load_fred(sid, start='2014-01-01'):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql(
        "SELECT date, value FROM observations WHERE series_id = ? AND date >= ? ORDER BY date",
        conn, params=(sid, start), parse_dates=['date']
    ).set_index('date').rename(columns={'value': sid})
    conn.close()
    return df


def fetch_btc(start='2017-01-01'):
    btc = yf.download('BTC-USD', start=start, progress=False)
    if isinstance(btc.columns, pd.MultiIndex):
        btc = btc.droplevel(1, axis=1)
    btc = btc[['Close']].rename(columns={'Close': 'BTC'})
    btc.index = pd.to_datetime(btc.index).tz_localize(None)
    return btc


# =============================================================================
# FIGURE 1: DXY (Inverted) vs BTC/USD
# =============================================================================

def fig_01_dxy_vs_btc(theme_mode):
    print(f'\n  [{theme_mode}] Figure 1: DXY (Inverted) vs BTC/USD')
    btc = fetch_btc(start='2017-06-01')
    dxy = load_fred('DTWEXBGS', start='2017-06-01')

    dxy_d = dxy['DTWEXBGS'].reindex(btc.index, method='ffill').dropna()
    btc_d = btc['BTC'].reindex(dxy_d.index).dropna()
    common = dxy_d.index.intersection(btc_d.index)
    dxy_d = dxy_d.loc[common]
    btc_d = btc_d.loc[common]

    fig, ax1 = new_fig()
    ax2 = ax1.twinx()

    c_dxy, c_btc = C['dusk'], T['primary']

    ax1.plot(dxy_d.index, dxy_d.values, color=c_dxy, linewidth=2.0,
             label='DXY Inverted (LHS)', zorder=3)
    ax1.invert_yaxis()
    ax1.set_ylabel('DXY (Inverted)', color=c_dxy, fontsize=11)

    ax2.plot(btc_d.index, btc_d.values, color=c_btc, linewidth=2.0,
             label='BTC/USD (RHS, log)', zorder=3)
    ax2.set_yscale('log')
    ax2.set_ylabel('BTC/USD (log scale)', color=c_btc, fontsize=11)
    btc_log_ticks(ax2)

    style_dual_ax(ax1, ax2, c_dxy, c_btc)
    ax1.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.0f}'))
    set_xlim_to_data(ax1, common)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    add_pill(ax1, dxy_d, c_dxy, fmt='{:.1f}', side='left')
    add_pill(ax2, btc_d, c_btc, fmt='${:,.0f}', side='right')

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', **legend_style())

    ann_box(ax1, ('CLI Tier 1: Dollar momentum as\n'
                  'global risk appetite proxy\n'
                  'DXY 63-Day RoC = 25% of CLI weight'),
            x=0.60, y=0.12, fontsize=10)

    brand_fig(fig, 'Crypto Liquidity Impulse: Tier 1',
              'DXY (Inverted) vs BTC/USD (2018-2026)',
              'FRED, Yahoo Finance', data_date=common[-1])

    save_fig(fig, 'fig_01_dxy_vs_btc.png', theme_mode)


# =============================================================================
# FIGURE 2: CLI vs 42-Day Forward BTC Returns
# =============================================================================

def fig_02_cli_vs_fwd(theme_mode):
    print(f'\n  [{theme_mode}] Figure 2: CLI vs 42-Day Forward BTC Returns')
    df = pd.read_csv(CLI_DATA, index_col=0, parse_dates=True)

    cli = df['CLI'].dropna()
    btc_price = df['BTC_Price'].dropna()
    btc_fwd = (btc_price.shift(-42) / btc_price - 1) * 100
    btc_fwd = btc_fwd.dropna()

    # Plot full CLI series (not truncated to forward return availability)
    cli_plot = cli
    # Forward returns only exist where we have 42 days of future data
    btc_plot = btc_fwd

    last_cli = cli.iloc[-1]
    if last_cli > 0.45: regime = 'Q5'
    elif last_cli > 0.14: regime = 'Q4'
    elif last_cli > -0.16: regime = 'Q3'
    elif last_cli > -0.57: regime = 'Q2'
    else: regime = 'Q1'

    print(f'    CLI = {last_cli:+.2f}, Regime = {regime}')

    fig, ax1 = new_fig()
    ax2 = ax1.twinx()

    c_cli, c_btc = C['dusk'], T['primary']

    Q1_TOP, Q2_TOP, Q3_TOP, Q4_TOP = -0.57, -0.16, 0.14, 0.45
    ax1.axhspan(-5.0, Q1_TOP, color=C['port'], alpha=0.10, zorder=0)
    ax1.axhspan(Q1_TOP, Q2_TOP, color=C['dusk'], alpha=0.08, zorder=0)
    ax1.axhspan(Q2_TOP, Q3_TOP, color=C['sea'], alpha=0.06, zorder=0)
    ax1.axhspan(Q3_TOP, Q4_TOP, color=C['sea'], alpha=0.12, zorder=0)
    ax1.axhspan(Q4_TOP, 5.0, color=C['starboard'], alpha=0.08, zorder=0)

    ax1.axhline(0, color=C['doldrums'], linewidth=0.8, linestyle='--', zorder=1)

    ax2.plot(btc_plot.index, btc_plot.values, color=c_btc, linewidth=1.2,
             alpha=0.85, label='BTC 42D Forward Return', zorder=2)
    ax2.fill_between(btc_plot.index, 0, btc_plot.values,
                     where=btc_plot.values > 0, color=c_btc, alpha=0.08, zorder=1)
    ax2.fill_between(btc_plot.index, 0, btc_plot.values,
                     where=btc_plot.values < 0, color=C['port'], alpha=0.08, zorder=1)

    ax1.plot(cli_plot.index, cli_plot.values, color=c_cli, linewidth=2.0,
             label=f'CLI ({last_cli:+.2f}, {regime})', zorder=5)

    for thresh in [Q1_TOP, Q2_TOP, Q3_TOP, Q4_TOP]:
        ax1.axhline(thresh, color=C['doldrums'], linewidth=0.4, linestyle=':', alpha=0.4)

    bls = dict(fontsize=8, fontweight='bold', ha='right', va='center', alpha=0.65)
    ax1.text(0.995, (Q4_TOP + 1.2) / 2, 'Q5', color=C['sea'],
             transform=ax1.get_yaxis_transform(), **bls)
    ax1.text(0.995, (Q3_TOP + Q4_TOP) / 2, 'Q4', color=C['sea'],
             transform=ax1.get_yaxis_transform(), **bls)
    ax1.text(0.995, (Q2_TOP + Q3_TOP) / 2, 'Q3', color=T['muted'],
             transform=ax1.get_yaxis_transform(), **bls)
    ax1.text(0.995, (Q1_TOP + Q2_TOP) / 2, 'Q2', color=C['dusk'],
             transform=ax1.get_yaxis_transform(), **bls)
    ax1.text(0.995, (Q1_TOP - 0.8) / 2, 'Q1', color=C['dusk'],
             transform=ax1.get_yaxis_transform(), **bls)

    ax1.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.1f}'))
    ax2.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.0f}%'))

    align_yaxis_zero(ax1, ax2)
    style_dual_ax(ax1, ax2, c_cli, c_btc)
    set_xlim_to_data(ax1, cli_plot.index)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    # Pill uses full CLI series so it matches the legend value
    add_pill(ax1, cli, c_cli, fmt='{:+.2f}', side='left')
    add_pill(ax2, btc_plot, c_btc, fmt='{:+.0f}%', side='right')

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', **legend_style())

    ann_box(ax1, ('Weighted composite across 3\n'
                  'liquidity impulse channels:\n'
                  '  \u2022 Dollar Momentum\n'
                  '  \u2022 Reserve Dynamics\n'
                  '  \u2022 Stablecoin Flows'))

    box2 = ('42D Fwd Returns:   Avg Ret  Slugging\n'
            ' Q5 (Strongest):      +14.3%    4.56x\n'
            ' Q4:                   +4.8%    2.17x\n'
            ' Q3:                   +3.4%    1.56x\n'
            ' Q2:                   -0.0%    0.97x\n'
            ' Q1 (Weakest):         -7.7%    0.43x\n\n'
            f'Q5-Q1: +22.0% (t=15.6, p<0.0001) | n={len(btc_plot):,}')
    ax1.text(0.55, 0.03, box2, transform=ax1.transAxes,
             fontsize=9.5, color=T['fg'], ha='center', va='bottom',
             family='monospace',
             bbox=dict(boxstyle='round,pad=0.5', facecolor=T['bg'],
                       edgecolor=C['ocean'], alpha=0.92, linewidth=1.5))

    brand_fig(fig, 'Crypto Liquidity Impulse',
              'CLI vs 42-Day Forward BTC Returns',
              'FRED, DefiLlama, Yahoo Finance',
              data_date=cli.index[-1])

    save_fig(fig, 'fig_02_cli_vs_fwd42d.png', theme_mode)


# =============================================================================
# MAIN
# =============================================================================

def main():
    print('=' * 60)
    print('  REGENERATE: Fig 1 (DXY vs BTC) + Fig 2 (CLI vs Fwd)')
    print('=' * 60)

    for mode in ['white', 'dark']:
        print(f'\n  === {mode.upper()} THEME ===')
        set_theme(mode)
        fig_01_dxy_vs_btc(mode)
        fig_02_cli_vs_fwd(mode)

    print('\n' + '=' * 60)
    print(f'  All charts saved to {OUT_BASE}/[white|dark]/')
    print('=' * 60)


if __name__ == '__main__':
    main()
