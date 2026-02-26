"""
LIGHTHOUSE MACRO — "What Is REALLY Driving Bitcoin's Price?" Charts
====================================================================
6 Figures for the BTC Drivers PDF (February 2026)

Figure 1: DXY (inverted) vs BTC/USD — CLI Tier 1
Figure 2: CLI vs 42-Day Forward BTC Returns
Figure 3: Average BTC Forward Returns by CLI Quintile (bar chart)
Figure 4: BTC Trend Structure (price vs 21d EMA / 200d SMA, regime shading)
Figure 5: Z-RoC Regime-Aware Momentum (dual-timeframe, color-coded)
Figure 6: BTC Relative Strength vs SPX (ratio + 50d MA)

Usage:
    python3 btc_drivers_charts.py
"""

import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.image as mpimg
from matplotlib.ticker import FuncFormatter, FixedLocator
from matplotlib.collections import LineCollection
from datetime import datetime
import yfinance as yf
import os
import sys
import warnings
warnings.filterwarnings('ignore')

# =============================================================================
# PATHS & CONFIG
# =============================================================================
BASE_PATH = '/Users/bob/LHM'
DB_PATH = f'{BASE_PATH}/Data/databases/Lighthouse_Master.db'
ICON_PATH = f'{BASE_PATH}/Brand/icon_transparent_128.png'
CLI_DATA = f'{BASE_PATH}/Scripts/backtest/cli_chart_data.csv'
OUT_DIR = f'{BASE_PATH}/Outputs/BTC_Drivers/white'
os.makedirs(OUT_DIR, exist_ok=True)

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

THEME = {
    'bg': '#ffffff',
    'fg': '#1a1a1a',
    'muted': '#555555',
    'spine': '#898989',
    'primary': C['ocean'],
    'secondary': C['dusk'],
    'tertiary': C['sky'],
    'quaternary': C['sea'],
    'bullish': C['starboard'],
    'bearish': C['port'],
    'legend_bg': '#f8f8f8',
    'legend_fg': '#1a1a1a',
}

# =============================================================================
# STYLING HELPERS
# =============================================================================

def new_fig(figsize=(14, 8)):
    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_facecolor(THEME['bg'])
    ax.set_facecolor(THEME['bg'])
    fig.subplots_adjust(top=0.88, bottom=0.08, left=0.06, right=0.94)
    return fig, ax


def new_fig_2panel(figsize=(14, 10), height_ratios=[2.5, 1]):
    fig, (ax_top, ax_bot) = plt.subplots(2, 1, figsize=figsize,
                                          height_ratios=height_ratios,
                                          sharex=True)
    fig.patch.set_facecolor(THEME['bg'])
    ax_top.set_facecolor(THEME['bg'])
    ax_bot.set_facecolor(THEME['bg'])
    fig.subplots_adjust(top=0.88, bottom=0.08, left=0.06, right=0.94, hspace=0.05)
    return fig, ax_top, ax_bot


def style_ax(ax, right_primary=True):
    ax.grid(False)
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_color(THEME['spine'])
        spine.set_linewidth(0.5)
    ax.tick_params(axis='both', which='both', length=0, labelsize=10,
                   colors=THEME['muted'])
    if right_primary:
        ax.yaxis.tick_right()
        ax.yaxis.set_label_position('right')


def style_dual_ax(ax1, ax2, c1, c2):
    style_ax(ax1, right_primary=False)
    ax1.tick_params(axis='y', labelcolor=c1)
    for spine in ax2.spines.values():
        spine.set_visible(True)
        spine.set_color(THEME['spine'])
        spine.set_linewidth(0.5)
    ax2.grid(False)
    ax2.tick_params(axis='both', which='both', length=0)
    ax2.tick_params(axis='y', labelcolor=c2, labelsize=10)


def set_xlim_to_data(ax, idx, pad_left=30, pad_right=180):
    ax.set_xlim(idx.min() - pd.Timedelta(days=pad_left),
                idx.max() + pd.Timedelta(days=pad_right))


def brand_fig(fig, title, subtitle=None, source=None, data_date=None):
    fig.patch.set_facecolor(THEME['bg'])
    OCEAN, DUSK = C['ocean'], C['dusk']

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

    fig.text(0.035, 0.98, 'LIGHTHOUSE MACRO', fontsize=13, fontweight='bold',
             color=OCEAN, va='top')
    fig.text(0.97, 0.98, DATE_STR, fontsize=11, color=THEME['muted'],
             va='top', ha='right')

    # Top accent bar
    bar = fig.add_axes([0.03, 0.955, 0.94, 0.004])
    bar.axhspan(0, 1, 0, 0.67, color=OCEAN)
    bar.axhspan(0, 1, 0.67, 1.0, color=DUSK)
    bar.set_xlim(0, 1); bar.set_ylim(0, 1); bar.axis('off')

    # Bottom accent bar
    bbar = fig.add_axes([0.03, 0.035, 0.94, 0.004])
    bbar.axhspan(0, 1, 0, 0.67, color=OCEAN)
    bbar.axhspan(0, 1, 0.67, 1.0, color=DUSK)
    bbar.set_xlim(0, 1); bbar.set_ylim(0, 1); bbar.axis('off')

    fig.suptitle(title, fontsize=15, fontweight='bold', y=0.945,
                 color=THEME['fg'])
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
                     fontsize=9, color=THEME['muted'], ha='left', va='top', style='italic')
        else:
            fig.text(0.03, 0.022, f'Lighthouse Macro | {source}; {pull_str}',
                     fontsize=9, color=THEME['muted'], ha='left', va='top', style='italic')


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
    return dict(framealpha=0.95, facecolor=THEME['legend_bg'],
                edgecolor=THEME['spine'], labelcolor=THEME['legend_fg'])


def btc_log_ticks(ax):
    """Set clean dollar tick labels on a log-scale BTC axis."""
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


def save_fig(fig, name):
    fig.patches.append(plt.Rectangle(
        (0, 0), 1, 1, transform=fig.transFigure,
        fill=False, edgecolor=C['ocean'], linewidth=4.0,
        zorder=100, clip_on=False
    ))
    path = os.path.join(OUT_DIR, name)
    fig.savefig(path, dpi=200, bbox_inches='tight', pad_inches=0.025,
                facecolor=THEME['bg'], edgecolor='none')
    plt.close(fig)
    print(f'  Saved: {path}')
    return path


def ann_box(ax, text, x=0.72, y=0.97, fontsize=10, mono=False):
    family = 'monospace' if mono else None
    ax.text(x, y, text, transform=ax.transAxes,
            fontsize=fontsize, color=THEME['fg'], ha='left', va='top',
            family=family,
            bbox=dict(boxstyle='round,pad=0.5', facecolor=THEME['bg'],
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


def fetch_spy(start='2017-01-01'):
    spy = yf.download('SPY', start=start, progress=False)
    if isinstance(spy.columns, pd.MultiIndex):
        spy = spy.droplevel(1, axis=1)
    spy = spy[['Close']].rename(columns={'Close': 'SPY'})
    spy.index = pd.to_datetime(spy.index).tz_localize(None)
    return spy


# =============================================================================
# FIGURE 1: DXY (Inverted) vs BTC/USD — Tier 1
# =============================================================================

def fig_01_dxy_vs_btc():
    print('\n  Figure 1: DXY (Inverted) vs BTC/USD')
    btc = fetch_btc(start='2017-06-01')
    dxy = load_fred('DTWEXBGS', start='2017-06-01')

    # Align to daily
    dxy_d = dxy['DTWEXBGS'].reindex(btc.index, method='ffill').dropna()
    btc_d = btc['BTC'].reindex(dxy_d.index).dropna()
    common = dxy_d.index.intersection(btc_d.index)
    dxy_d = dxy_d.loc[common]
    btc_d = btc_d.loc[common]

    fig, ax1 = new_fig()
    ax2 = ax1.twinx()

    c_dxy, c_btc = C['dusk'], C['ocean']

    # DXY inverted on LHS
    ax1.plot(dxy_d.index, dxy_d.values, color=c_dxy, linewidth=2.0,
             label='DXY Inverted (LHS)', zorder=3)
    ax1.invert_yaxis()
    ax1.set_ylabel('DXY (Inverted)', color=c_dxy, fontsize=11)

    # BTC on RHS, log scale
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
              'FRED, Yahoo Finance', data_date=dxy_d.index[-1])

    save_fig(fig, 'fig_01_dxy_vs_btc.png')


# =============================================================================
# FIGURE 2: CLI vs 42-Day Forward BTC Returns
# =============================================================================

def fig_02_cli_vs_fwd():
    print('\n  Figure 2: CLI vs 42-Day Forward BTC Returns')
    df = pd.read_csv(CLI_DATA, index_col=0, parse_dates=True)

    cli = df['CLI'].dropna()
    btc_price = df['BTC_Price'].dropna()
    btc_fwd = (btc_price.shift(-42) / btc_price - 1) * 100
    btc_fwd = btc_fwd.dropna()

    common = cli.index.intersection(btc_fwd.index)
    cli_plot = cli.loc[common]
    btc_plot = btc_fwd.loc[common]

    last_cli = cli.dropna().iloc[-1]
    if last_cli > 0.45: regime = 'Q5'
    elif last_cli > 0.14: regime = 'Q4'
    elif last_cli > -0.16: regime = 'Q3'
    elif last_cli > -0.57: regime = 'Q2'
    else: regime = 'Q1'

    fig, ax1 = new_fig()
    ax2 = ax1.twinx()

    c_cli, c_btc = C['dusk'], C['ocean']

    # Quintile bands
    Q1_TOP, Q2_TOP, Q3_TOP, Q4_TOP = -0.57, -0.16, 0.14, 0.45
    ax1.axhspan(-5.0, Q1_TOP, color=C['port'], alpha=0.10, zorder=0)
    ax1.axhspan(Q1_TOP, Q2_TOP, color=C['dusk'], alpha=0.08, zorder=0)
    ax1.axhspan(Q2_TOP, Q3_TOP, color=C['sea'], alpha=0.06, zorder=0)
    ax1.axhspan(Q3_TOP, Q4_TOP, color=C['sea'], alpha=0.12, zorder=0)
    ax1.axhspan(Q4_TOP, 5.0, color=C['starboard'], alpha=0.08, zorder=0)

    ax1.axhline(0, color=C['doldrums'], linewidth=0.8, linestyle='--', zorder=1)

    # BTC forward returns (RHS, behind)
    ax2.plot(btc_plot.index, btc_plot.values, color=c_btc, linewidth=1.2,
             alpha=0.85, label='BTC 42D Forward Return', zorder=2)
    ax2.fill_between(btc_plot.index, 0, btc_plot.values,
                     where=btc_plot.values > 0, color=c_btc, alpha=0.08, zorder=1)
    ax2.fill_between(btc_plot.index, 0, btc_plot.values,
                     where=btc_plot.values < 0, color=C['port'], alpha=0.08, zorder=1)

    # CLI (LHS, foreground)
    ax1.plot(cli_plot.index, cli_plot.values, color=c_cli, linewidth=2.0,
             label=f'CLI ({last_cli:+.2f}, {regime})', zorder=5)

    for thresh in [Q1_TOP, Q2_TOP, Q3_TOP, Q4_TOP]:
        ax1.axhline(thresh, color=C['doldrums'], linewidth=0.4, linestyle=':', alpha=0.4)

    # Quintile labels
    bls = dict(fontsize=8, fontweight='bold', ha='right', va='center', alpha=0.65)
    ax1.text(0.995, (Q4_TOP + 1.2) / 2, 'Q5', color=C['sea'],
             transform=ax1.get_yaxis_transform(), **bls)
    ax1.text(0.995, (Q3_TOP + Q4_TOP) / 2, 'Q4', color=C['sea'],
             transform=ax1.get_yaxis_transform(), **bls)
    ax1.text(0.995, (Q2_TOP + Q3_TOP) / 2, 'Q3', color=THEME['muted'],
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

    add_pill(ax1, cli_plot, c_cli, fmt='{:+.2f}', side='left')
    add_pill(ax2, btc_plot, c_btc, fmt='{:+.0f}%', side='right')

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', **legend_style())

    ann_box(ax1, ('Weighted composite across 3\n'
                  'liquidity impulse channels:\n'
                  '  \u2022 Dollar Momentum\n'
                  '  \u2022 Reserve Dynamics\n'
                  '  \u2022 Stablecoin Flows'))

    # Stats box
    box2 = ('42D Fwd Returns:   Avg Ret  Slugging\n'
            ' Q5 (Strongest):      +14.3%    4.56x\n'
            ' Q4:                   +6.0%    2.17x\n'
            ' Q3:                   +3.9%    1.56x\n'
            ' Q2:                   -0.2%    0.97x\n'
            ' Q1 (Weakest):         -7.8%    0.43x\n\n'
            f'Q5-Q1: +22.1% (t=15.6, p<0.0001) | n={len(cli_plot):,}')
    ax1.text(0.55, 0.03, box2, transform=ax1.transAxes,
             fontsize=9.5, color=THEME['fg'], ha='center', va='bottom',
             family='monospace',
             bbox=dict(boxstyle='round,pad=0.5', facecolor=THEME['bg'],
                       edgecolor=C['ocean'], alpha=0.92, linewidth=1.5))

    brand_fig(fig, 'Crypto Liquidity Impulse',
              'CLI vs 42-Day Forward BTC Returns',
              'FRED, DefiLlama, Yahoo Finance',
              data_date=cli_plot.index[-1])

    save_fig(fig, 'fig_02_cli_vs_fwd42d.png')


# =============================================================================
# FIGURE 3: CLI Regime Bars
# =============================================================================

def fig_03_regime_bars():
    print('\n  Figure 3: CLI Regime Bars')
    fig, ax = new_fig()

    quintiles = ['Q1\n(Weakest)', 'Q2', 'Q3', 'Q4', 'Q5\n(Strongest)']
    ret_21d = [-4.8, 0.5, 1.0, 2.0, 8.6]
    ret_42d = [-7.8, -0.2, 3.9, 6.0, 14.3]
    ret_63d = [-9.8, -2.1, 9.0, 11.1, 17.2]

    x = np.arange(len(quintiles))
    width = 0.25

    bars1 = ax.bar(x - width, ret_21d, width, label='21D Fwd',
                   color=C['ocean'], zorder=3)
    bars2 = ax.bar(x, ret_42d, width, label='42D Fwd',
                   color=C['dusk'], zorder=3)
    bars3 = ax.bar(x + width, ret_63d, width, label='63D Fwd',
                   color=C['sky'], zorder=3)

    for bars in [bars1, bars2, bars3]:
        for bar in bars:
            val = bar.get_height()
            va = 'bottom' if val >= 0 else 'top'
            offset = 0.4 if val >= 0 else -0.4
            ax.text(bar.get_x() + bar.get_width() / 2, val + offset,
                    f'{val:+.1f}%', ha='center', va=va,
                    fontsize=8, fontweight='bold', color=THEME['fg'])

    ax.axhline(0, color=C['doldrums'], linewidth=0.8, linestyle='--', zorder=1)
    ax.set_xticks(x)
    ax.set_xticklabels(quintiles, fontsize=11, color=THEME['fg'])
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:+.0f}%'))

    ymin, ymax = ax.get_ylim()
    ax.set_ylim(ymin - 2.0, ymax + 3.0)

    style_ax(ax, right_primary=True)
    ax.legend(loc='upper left', **legend_style())

    ann_text = ('Weighted composite across 3 liquidity impulse channels:\n'
                'Dollar Momentum | Reserve Dynamics | Stablecoin Flows\n\n'
                'Q5-Q1 Spread:                Slugging (Q1 / Q5):\n'
                '21D: +13.4%  (t = 14.2)      0.45x  /  4.81x\n'
                '42D: +22.1%  (t = 15.6)      0.43x  /  4.56x\n'
                '63D: +27.0%  (t = 15.0)      0.39x  /  3.70x\n'
                'All p < 0.0001             Monotonic at all horizons')
    ax.text(0.52, 0.95, ann_text, transform=ax.transAxes,
            fontsize=10, color=THEME['fg'], ha='center', va='top',
            family='monospace',
            bbox=dict(boxstyle='round,pad=0.6', facecolor=THEME['bg'],
                      edgecolor=C['ocean'], alpha=0.92, linewidth=1.5))

    brand_fig(fig, 'Crypto Liquidity Impulse',
              'Average BTC Forward Returns by CLI Quintile (2018-2025)',
              'Lighthouse Macro Backtest')

    save_fig(fig, 'fig_03_cli_regime_bars.png')


# =============================================================================
# FIGURE 4: BTC Trend Structure
# =============================================================================

def fig_04_trend_structure():
    print('\n  Figure 4: BTC Trend Structure')
    btc = fetch_btc(start='2016-01-01')
    price = btc['BTC']

    # 50d SMA, 200d SMA, 200w SMA (1400 trading days)
    sma50 = price.rolling(50).mean()
    sma200 = price.rolling(200).mean()
    sma200w = price.rolling(1400).mean()

    # Drop NaN from 200d, then trim display to 2022+
    valid = sma200.dropna().index
    valid = valid[valid >= '2022-01-01']
    price = price.loc[valid]
    sma50 = sma50.loc[valid]
    sma200 = sma200.loc[valid]
    sma200w = sma200w.loc[valid]

    # Regime: bullish = price > 50d AND 50d > 200d (more stable than 21d EMA)
    raw_bull = (price > sma50) & (sma50 > sma200)

    # Build regime segments, then iteratively merge short ones
    segments = []
    start_idx = valid[0]
    prev = raw_bull.iloc[0]
    for i in range(1, len(valid)):
        curr = raw_bull.iloc[i]
        if curr != prev:
            segments.append([start_idx, valid[i-1], prev])
            start_idx = valid[i]
        prev = curr
    segments.append([start_idx, valid[-1], prev])

    # Iteratively merge segments shorter than min_days until stable
    min_days = 30
    changed = True
    while changed:
        changed = False
        new_segs = []
        for seg in segments:
            duration = (seg[1] - seg[0]).days
            if duration < min_days and new_segs:
                new_segs[-1][1] = seg[1]
                changed = True
            else:
                new_segs.append(seg)
        segments = new_segs

    fig, ax = new_fig()

    # Regime shading from merged segments
    for start_s, end_s, is_bull in segments:
        color = C['starboard'] if is_bull else C['port']
        alpha = 0.10 if is_bull else 0.08
        ax.axvspan(start_s, end_s, color=color, alpha=alpha, zorder=0)

    # Plot price and MAs
    ax.plot(price.index, price.values, color=C['doldrums'], linewidth=1.5,
            alpha=0.7, label='BTC/USD', zorder=3)
    ax.plot(sma50.index, sma50.values, color=C['dusk'], linewidth=2.0,
            label='50-Day MA', zorder=4)
    ax.plot(sma200.index, sma200.values, color=C['ocean'], linewidth=2.0,
            label='200-Day MA', zorder=4)
    sma200w_plot = sma200w.dropna()
    if len(sma200w_plot) > 0:
        ax.plot(sma200w_plot.index, sma200w_plot.values, color=C['sky'], linewidth=2.0,
                label='200-Week MA', zorder=4)

    ax.set_yscale('log')
    btc_log_ticks(ax)

    style_ax(ax, right_primary=True)
    set_xlim_to_data(ax, price.index, pad_left=15, pad_right=120)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))

    # Stagger pills so they don't overlap
    last_price = float(price.dropna().iloc[-1])
    last_50 = float(sma50.dropna().iloc[-1])
    last_sma = float(sma200.dropna().iloc[-1])
    # Sort by value descending, assign offsets
    pills = [
        (last_price, C['doldrums'], 'BTC'),
        (last_50, C['dusk'], '50d'),
        (last_sma, C['ocean'], '200d'),
    ]
    sma200w_valid = sma200w.dropna()
    if len(sma200w_valid) > 0:
        last_200w = float(sma200w_valid.iloc[-1])
        pills.append((last_200w, C['sky'], '200w'))
    pills = sorted(pills, key=lambda x: -x[0])
    for idx_p, (val, col, _) in enumerate(pills):
        label = f'${val:,.0f}'
        pill_box = dict(boxstyle='round,pad=0.25', facecolor=col, edgecolor=col, alpha=0.95)
        y_offset = idx_p * -16  # stagger vertically
        ax.annotate(label, xy=(1.0, val), xycoords=('axes fraction', 'data'),
                    fontsize=9, fontweight='bold', color='white',
                    ha='left', va='center', xytext=(6, y_offset),
                    textcoords='offset points', bbox=pill_box, clip_on=False)

    ax.legend(loc='upper left', **legend_style())

    ann_box(ax, ('Technical Overlay Component 1: Trend\n'
                 'Price vs 50d vs 200d alignment + slope\n'
                 'Green = bullish structure | Pink = bearish'),
            x=0.55, y=0.12, fontsize=10)

    brand_fig(fig, 'BTC Trend Structure',
              'Price vs 50-Day and 200-Day Moving Averages (2022-2026)',
              'Yahoo Finance', data_date=price.index[-1])

    save_fig(fig, 'fig_04_trend_structure.png')


# =============================================================================
# FIGURE 5: Z-RoC Regime-Aware Momentum
# =============================================================================

def fig_05_zroc():
    print('\n  Figure 5: Z-RoC Regime-Aware Momentum')
    btc = fetch_btc(start='2021-06-01')
    price = btc['BTC']

    # 63d and 21d rate of change
    roc_63 = price / price.shift(63) - 1
    roc_21 = price / price.shift(21) - 1

    # Z-score (expanding)
    def z_exp(s, min_p=63):
        return (s - s.expanding(min_p).mean()) / s.expanding(min_p).std()

    z63 = z_exp(roc_63, 126)
    z21 = z_exp(roc_21, 63)

    # Drop NaN
    valid = z63.dropna().index.intersection(z21.dropna().index)
    # Start from 2022 for clean display
    valid = valid[valid >= '2022-01-01']
    z63 = z63.loc[valid]
    z21 = z21.loc[valid]
    price_plot = price.loc[valid]

    # Color logic: both positive = Ocean (bullish), both negative = Dusk (bearish), else gray
    both_bull = (z63 > 0) & (z21 > 0)
    both_bear = (z63 < 0) & (z21 < 0)

    fig, ax_top, ax_bot = new_fig_2panel(figsize=(14, 10), height_ratios=[2, 1])

    # TOP PANEL: BTC Price (log), color-coded by regime
    # Color-coded price segments using LineCollection
    points = np.column_stack([mdates.date2num(price_plot.index), price_plot.values])
    segments = np.stack([points[:-1], points[1:]], axis=1)
    colors = []
    for i in range(len(valid) - 1):
        if both_bull.iloc[i]:
            colors.append(C['ocean'])
        elif both_bear.iloc[i]:
            colors.append(C['dusk'])
        else:
            colors.append(C['doldrums'])
    lc = LineCollection(segments, colors=colors, linewidths=2.5, zorder=3)
    ax_top.add_collection(lc)

    ax_top.set_yscale('log')
    btc_log_ticks(ax_top)
    style_ax(ax_top, right_primary=True)
    ax_top.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    add_pill(ax_top, price_plot, C['ocean'], fmt='${:,.0f}', side='right', pad=0.25)

    ann_box(ax_top, ('Technical Overlay Component 2: Momentum\n'
                     '63d Z-RoC (regime) + 21d Z-RoC (tactical)\n'
                     'Dual-timeframe color logic'),
            x=0.02, y=0.97, fontsize=10)

    # BOTTOM PANEL: Z-RoC
    ax_bot.axhline(0, color=C['fog'], linewidth=0.8, linestyle='--', zorder=1)
    ax_bot.axhline(1, color=C['doldrums'], linewidth=0.6, linestyle=':', alpha=0.4)
    ax_bot.axhline(-1, color=C['doldrums'], linewidth=0.6, linestyle=':', alpha=0.4)
    ax_bot.axhline(2, color=C['doldrums'], linewidth=0.8, linestyle='--', alpha=0.8)
    ax_bot.axhline(-2, color=C['doldrums'], linewidth=0.8, linestyle='--', alpha=0.8)
    ax_bot.text(1.02, 2, '+2\u03c3', transform=ax_bot.get_yaxis_transform(),
                fontsize=8, color=THEME['muted'], va='center')
    ax_bot.text(1.02, -2, '-2\u03c3', transform=ax_bot.get_yaxis_transform(),
                fontsize=8, color=THEME['muted'], va='center')

    # Color-coded Z-RoC line
    z_points = np.column_stack([mdates.date2num(z63.index), z63.values])
    z_segments = np.stack([z_points[:-1], z_points[1:]], axis=1)
    z_colors = []
    for i in range(len(valid) - 1):
        if both_bull.iloc[i]:
            z_colors.append(C['ocean'])
        elif both_bear.iloc[i]:
            z_colors.append(C['dusk'])
        else:
            z_colors.append(C['doldrums'])
    z_lc = LineCollection(z_segments, colors=z_colors, linewidths=2.0, zorder=3)
    ax_bot.add_collection(z_lc)
    ax_bot.set_ylim(z63.min() - 0.5, z63.max() + 0.5)

    # Fill extremes
    ax_bot.fill_between(z63.index, 2, z63.values.clip(min=2),
                        color=C['ocean'], alpha=0.15, zorder=1)
    ax_bot.fill_between(z63.index, -2, z63.values.clip(max=-2),
                        color=C['dusk'], alpha=0.15, zorder=1)

    ax_bot.set_ylabel('Z-RoC (63d)', color=THEME['muted'], fontsize=10)
    style_ax(ax_bot, right_primary=True)
    ax_bot.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.0f}'))

    add_pill(ax_bot, z63, C['dusk'] if z63.iloc[-1] < 0 else C['ocean'],
             fmt='{:+.2f}', side='right')

    set_xlim_to_data(ax_top, price_plot.index, pad_left=15, pad_right=120)
    set_xlim_to_data(ax_bot, z63.index, pad_left=15, pad_right=120)

    # Legend for color logic (bottom panel)
    from matplotlib.lines import Line2D
    handles = [
        Line2D([0], [0], color=C['ocean'], lw=3, label='Long bias (both TFs agree bullish)'),
        Line2D([0], [0], color=C['dusk'], lw=3, label='Short bias (both TFs agree bearish)'),
        Line2D([0], [0], color=C['doldrums'], lw=3, label='Neutral (timeframes diverge)'),
    ]
    ax_bot.legend(handles=handles, loc='lower left', fontsize=9, **legend_style())

    brand_fig(fig, 'Z-RoC: Regime-Aware Momentum',
              'BTC/USD (top) vs 63-Day Z-Score Rate of Change (bottom)',
              'Yahoo Finance', data_date=price_plot.index[-1])

    save_fig(fig, 'fig_05_zroc.png')


# =============================================================================
# FIGURE 6: BTC Relative Strength vs SPX
# =============================================================================

def fig_06_relative_strength():
    print('\n  Figure 6: BTC Relative Strength vs SPX')
    btc_full = fetch_btc(start='2019-06-01')
    spy = fetch_spy(start='2019-06-01')

    # For ratio: align to SPY trading days
    common = btc_full.index.intersection(spy.index)
    btc_common = btc_full['BTC'].loc[common]
    spy_d = spy['SPY'].loc[common]

    ratio = btc_common / spy_d
    ratio_ma50 = ratio.rolling(50).mean()

    valid = ratio_ma50.dropna().index
    ratio = ratio.loc[valid]
    ratio_ma50 = ratio_ma50.loc[valid]

    # For top panel: use full BTC data (includes weekends) for accurate latest price
    btc_top = btc_full['BTC'].loc[btc_full.index >= valid[0]]

    fig, ax_top, ax_bot = new_fig_2panel(figsize=(14, 11), height_ratios=[1.2, 1])

    # TOP PANEL: BTC Price (full daily data)
    ax_top.plot(btc_top.index, btc_top.values, color=C['ocean'], linewidth=1.8,
                alpha=0.9, label='BTC/USD', zorder=3)
    ax_top.set_yscale('log')
    btc_log_ticks(ax_top)
    style_ax(ax_top, right_primary=True)

    add_pill(ax_top, btc_top, C['ocean'], fmt='${:,.0f}', side='right', pad=0.25)

    ann_box(ax_top, ('Technical Overlay Component 3: Relative Strength\n'
                     'BTC vs SPX across multiple timeframes\n'
                     'Rising ratio + rising slope = institutional conviction'),
            x=0.02, y=0.97, fontsize=10)

    # BOTTOM PANEL: Ratio + 50d MA
    ax_bot.plot(ratio.index, ratio.values, color=C['ocean'], linewidth=1.0,
                alpha=0.4, label='BTC/SPY Ratio', zorder=2)
    ax_bot.plot(ratio_ma50.index, ratio_ma50.values, color=C['dusk'],
                linewidth=2.0, label='50-Day MA', zorder=3)

    ax_bot.set_ylabel('BTC/SPY Ratio', color=THEME['muted'], fontsize=10)
    style_ax(ax_bot, right_primary=True)
    ax_bot.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.0f}'))

    add_pill(ax_bot, ratio_ma50, C['dusk'], fmt='{:.0f}', side='right')

    set_xlim_to_data(ax_top, btc_top.index, pad_left=15, pad_right=120)
    set_xlim_to_data(ax_bot, ratio.index, pad_left=15, pad_right=120)

    ax_top.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax_bot.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    ax_bot.legend(loc='upper left', fontsize=9, **legend_style())

    brand_fig(fig, 'BTC Relative Strength vs SPX',
              'BTC/SPY Ratio with 50-Day Moving Average (2020-2026)',
              'Yahoo Finance', data_date=btc_top.index[-1])

    save_fig(fig, 'fig_06_relative_strength.png')


# =============================================================================
# MAIN
# =============================================================================

def main():
    print('='*60)
    print('  BTC DRIVERS — All 6 Figures')
    print('='*60)

    fig_01_dxy_vs_btc()
    fig_02_cli_vs_fwd()
    fig_03_regime_bars()
    fig_04_trend_structure()
    fig_05_zroc()
    fig_06_relative_strength()

    print('\n' + '='*60)
    print(f'  All charts saved to {OUT_DIR}')
    print('='*60)


if __name__ == '__main__':
    main()
