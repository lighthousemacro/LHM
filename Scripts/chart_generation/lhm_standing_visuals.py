#!/usr/bin/env python3
"""
LHM Standing Visuals — the recurring three
=========================================

Three visuals meant to run on a fixed cadence, always the same shape, so a
reader learns to read them once and then reads them fast every time.

  1. The Regime Ribbon    Activity x Credit state probabilities, 1977 to now,
                          plus a recent-sessions probability table.
  2. The Trend Board      Every name in the cross-asset universe scored on the
                          LHM technical hierarchy: price vs 200-day, relative
                          trend vs SPY, absolute Z-RoC. Grid plus history.
  3. The Program Panel    Cumulative excess path, drawdown, summary statistics,
                          rolling six-month excess. INTERNAL until the OOS
                          figures are separately verified.

Data comes from Lighthouse_Master.db and Outputs/regime_book/returns.parquet.
Nothing here is simulated or filled.

Usage:
    python Scripts/chart_generation/lhm_standing_visuals.py [ribbon|board|program|all]

Author: Bob Sheehan, CFA, CMT
"""

from __future__ import annotations

import os
import sqlite3
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Rectangle

sys.path.insert(0, '/Users/bob/LHM/Scripts/chart_generation')
from lhm_chart_template import (  # noqa: E402
    COLORS, brand_fig, new_fig, save_fig, set_theme, style_ax,
)

DB = '/Users/bob/LHM/Data/databases/Lighthouse_Master.db'
OUT = '/Users/bob/LHM/Charts/standing'
os.makedirs(OUT, exist_ok=True)

SRC_DB = 'FRED, BLS, BEA, Chicago Fed, Yahoo Finance'


# ============================================================
# data helpers
# ============================================================

def _index(index_id: str) -> pd.Series:
    with sqlite3.connect(DB) as c:
        d = pd.read_sql(
            'SELECT date, value FROM lighthouse_indices WHERE index_id = ? ORDER BY date',
            c, params=(index_id,), parse_dates=['date'],
        )
    return d.set_index('date')['value'].dropna()


def _closes(tickers) -> pd.DataFrame:
    ids = [f'{t}_Close' for t in tickers]
    q = 'SELECT series_id, date, value FROM observations WHERE series_id IN (%s)' % (
        ','.join('?' * len(ids)))
    with sqlite3.connect(DB) as c:
        d = pd.read_sql(q, c, params=ids, parse_dates=['date'])
    px = d.pivot(index='date', columns='series_id', values='value')
    px.columns = [c.replace('_Close', '') for c in px.columns]
    return px.sort_index()


def _norm_cdf(z):
    """Standard normal CDF without pulling scipy in."""
    from math import erf, sqrt
    return np.vectorize(lambda x: 0.5 * (1 + erf(x / sqrt(2))))(z)


# ============================================================
# 1. THE REGIME RIBBON
# ============================================================

RIBBON_STATES = [
    ('Expansion / Easy Credit',  COLORS['ocean']),
    ('Expansion / Tight Credit', COLORS['dusk']),
    ('Slowdown / Easy Credit',   COLORS['sky']),
    ('Slowdown / Tight Credit',  COLORS['deep']),
]


def ribbon_probabilities(smooth: int = 21) -> pd.DataFrame:
    """
    State probabilities on the two axes we actually trade off: activity and
    credit. Prometheus splits growth against inflation. We split growth against
    the credit channel, because credit is what decides whether a slowdown gets
    to stay orderly.

    Each composite is a standardized z. Smoothed 21 sessions (daily composites
    get a 21-day average, per house rule), mapped through a normal link to a
    marginal probability, then crossed. Independence across the two axes is an
    assumption, stated here rather than hidden.
    """
    g = _index('GCI').rolling(smooth, min_periods=smooth // 2).mean()
    f = _index('FCI').rolling(smooth, min_periods=smooth // 2).mean()
    df = pd.concat({'g': g, 'f': f}, axis=1).dropna()

    p_growth = pd.Series(_norm_cdf(df['g'].values), index=df.index)
    p_easy = pd.Series(_norm_cdf(df['f'].values), index=df.index)

    return pd.DataFrame({
        'Expansion / Easy Credit':  p_growth * p_easy,
        'Expansion / Tight Credit': p_growth * (1 - p_easy),
        'Slowdown / Easy Credit':   (1 - p_growth) * p_easy,
        'Slowdown / Tight Credit':  (1 - p_growth) * (1 - p_easy),
    })


def chart_ribbon():
    probs = ribbon_probabilities()

    set_theme('white')
    fig, ax = new_fig(figsize=(16, 8))
    labels = [s for s, _ in RIBBON_STATES]
    ax.stackplot(probs.index, [probs[l].values for l in labels],
                 colors=[c for _, c in RIBBON_STATES], labels=labels, linewidth=0)
    ax.set_ylim(0, 1)
    ax.set_xlim(probs.index[0], probs.index[-1])
    ax.set_yticks(np.arange(0, 1.01, 0.1))
    ax.set_yticklabels([f'{int(v*100)}%' for v in np.arange(0, 1.01, 0.1)])
    ax.set_ylabel('State probability')
    style_ax(ax)

    leg = ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.06), ncol=4,
                    frameon=False, fontsize=10)
    for t in leg.get_texts():
        t.set_color(COLORS['doldrums'])

    latest = probs.iloc[-1].sort_values(ascending=False)
    brand_fig(
        fig,
        'The Regime Ribbon',
        f'Activity x credit state probabilities. Today: {latest.index[0]} at {latest.iloc[0]*100:.0f}%.',
        source=SRC_DB,
        data_date=probs.index[-1],
    )
    fig.subplots_adjust(bottom=0.20)
    path = f'{OUT}/regime_ribbon.png'
    save_fig(fig, path)
    return path, probs


def chart_ribbon_table(probs: pd.DataFrame, n: int = 20):
    """Companion table. Last n sessions, one row each, cell-shaded by probability."""
    tab = probs.tail(n).iloc[::-1]
    labels = [s for s, _ in RIBBON_STATES]

    set_theme('white')
    fig, ax = plt.subplots(figsize=(11, 0.42 * len(tab) + 2.6))
    fig.patch.set_facecolor('#FFFFFF')
    ax.axis('off')

    ncol = len(labels)
    col_w = 1.0 / (ncol + 1.15)
    x0 = 1.15 * col_w
    row_h = 1.0 / (len(tab) + 1)

    short = ['Expansion\nEasy Credit', 'Expansion\nTight Credit',
             'Slowdown\nEasy Credit', 'Slowdown\nTight Credit']
    for j, (lab, col) in enumerate(zip(short, [c for _, c in RIBBON_STATES])):
        ax.text(x0 + (j + 0.5) * col_w, 1.0 - row_h * 0.35, lab, ha='center',
                va='center', fontsize=9, fontweight='bold', color=col)

    for i, (dt, row) in enumerate(tab.iterrows()):
        y = 1.0 - row_h * (i + 1.35)
        ax.text(x0 * 0.9, y, dt.strftime('%m/%d/%Y'), ha='right', va='center',
                fontsize=9, color=COLORS['doldrums'])
        for j, lab in enumerate(labels):
            v = row[lab]
            base = RIBBON_STATES[j][1]
            ax.add_patch(Rectangle((x0 + j * col_w, y - row_h * 0.42),
                                   col_w * 0.96, row_h * 0.84,
                                   facecolor=base, alpha=min(0.9, 0.12 + v * 1.5),
                                   edgecolor='none'))
            ax.text(x0 + (j + 0.48) * col_w, y, f'{v*100:.0f}%', ha='center',
                    va='center', fontsize=9,
                    color='#FFFFFF' if v > 0.42 else COLORS['deep'])

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    brand_fig(fig, 'The Regime Ribbon: Recent Sessions',
              'Daily state probabilities, most recent first.',
              source=SRC_DB, data_date=tab.index[0])
    path = f'{OUT}/regime_ribbon_table.png'
    save_fig(fig, path)
    return path


# ============================================================
# 2. THE TREND BOARD
# ============================================================

BOARD_UNIVERSE = [
    ('Equities', ['SPY', 'QQQ', 'IWM', 'RSP', 'ACWI', 'EFA', 'EEM']),
    ('Sectors',  ['XLK', 'XLV', 'XLY', 'XLC', 'XLF', 'XLI', 'XLP',
                  'XLU', 'XLB', 'XLE', 'XLRE', 'XHB']),
    ('Style',    ['IWF', 'IWD', 'MTUM', 'QUAL', 'USMV', 'VLUE']),
    ('Rates',    ['SHY', 'IEF', 'TLT', 'TIP', 'MBB']),
    ('Credit',   ['LQD', 'HYG', 'EMB']),
    ('Real',     ['GLD', 'SLV', 'GDX', 'DBC', 'DBA', 'VNQ']),
    ('Crypto',   ['BTC']),
]
BENCH = 'SPY'


def board_signals(px: pd.DataFrame) -> pd.DataFrame:
    """
    Three states per name, on the LHM hierarchy in its own order:
      1. Price versus its 200-day average.       Primary trend.
      2. Relative strength versus SPY, versus    Are we being paid to own it.
         that ratio's own 63-day average.
      3. Absolute Z-RoC.                         Momentum, standardized.
    Score is the sum of the three, so it runs -3 to +3. Prometheus runs a
    two-speed binary. We run three tests and let the middle ground exist.
    """
    out = {}
    bench = px[BENCH]
    for t in px.columns:
        s = px[t].dropna()
        if len(s) < 300:
            continue
        ma200 = s.rolling(200).mean()
        rs = (s / bench.reindex(s.index).ffill()) * 100
        rs_ma = rs.rolling(63).mean()
        roc = s.pct_change(63)
        z_roc = (roc - roc.rolling(252).mean()) / roc.rolling(252).std()

        out[t] = pd.DataFrame({
            'price': np.sign(s - ma200),
            'relative': np.sign(rs - rs_ma),
            'zroc': np.where(z_roc > 0.5, 1, np.where(z_roc < -0.5, -1, 0)),
        }, index=s.index)
    return out


BOARD_COLS = ['price', 'relative', 'zroc']
BOARD_COL_LABELS = ['Price vs\n200-day', 'Relative trend\nvs SPY', 'Z-RoC\nabsolute']


def _state_color(v):
    if v > 0:
        return COLORS['ocean']
    if v < 0:
        return COLORS['dusk']
    return COLORS['fog']


def chart_trend_board():
    tickers = sorted({t for _, g in BOARD_UNIVERSE for t in g} | {BENCH})
    px = _closes(tickers).ffill(limit=5)
    sigs = board_signals(px)
    asof = max(v.index[-1] for v in sigs.values())

    rows = []
    for group, names in BOARD_UNIVERSE:
        rows.append(('__group__', group))
        for t in names:
            if t in sigs:
                rows.append((t, group))

    set_theme('white')
    fig, ax = plt.subplots(figsize=(12, 0.30 * (len(rows) + 2) + 3.0))
    fig.patch.set_facecolor('#FFFFFF')
    ax.axis('off')
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    n = len(rows)
    row_h = 0.92 / (n + 1)
    x_lab = 0.20
    col_w = 0.15
    x_score = x_lab + 3 * col_w + 0.04

    for j, lab in enumerate(BOARD_COL_LABELS):
        ax.text(x_lab + (j + 0.5) * col_w, 0.955, lab, ha='center', va='center',
                fontsize=9, fontweight='bold', color=COLORS['deep'])
    ax.text(x_score + 0.06, 0.955, 'Score\n-3 to +3', ha='center', va='center',
            fontsize=9, fontweight='bold', color=COLORS['deep'])

    for i, (t, group) in enumerate(rows):
        y = 0.92 - row_h * (i + 1)
        if t == '__group__':
            ax.text(0.02, y, group.upper(), fontsize=9, fontweight='bold',
                    color=COLORS['ocean'], va='center')
            ax.plot([0.02, x_score + 0.12], [y - row_h * 0.48] * 2, lw=0.6,
                    color=COLORS['fog'])
            continue
        last = sigs[t].iloc[-1]
        ax.text(0.055, y, t, fontsize=9.5, color=COLORS['deep'], va='center')
        for j, key in enumerate(BOARD_COLS):
            v = last[key]
            ax.add_patch(Rectangle((x_lab + j * col_w, y - row_h * 0.40),
                                   col_w * 0.94, row_h * 0.80,
                                   facecolor=_state_color(v), edgecolor='none'))
        score = int(last[BOARD_COLS].sum())
        ax.add_patch(Rectangle((x_score, y - row_h * 0.40), 0.12, row_h * 0.80,
                               facecolor=_state_color(score),
                               alpha=0.25 + 0.25 * abs(score), edgecolor='none'))
        ax.text(x_score + 0.06, y, f'{score:+d}', ha='center', va='center',
                fontsize=9, fontweight='bold', color=COLORS['deep'])

    ax.text(0.02, 0.92 - row_h * (n + 1.9),
            'Ocean = confirming    Dusk = breaking    Fog = mixed',
            fontsize=9, color=COLORS['doldrums'], va='center')

    brand_fig(fig, 'The Trend Board',
              'Three tests per name: primary trend, relative trend, absolute momentum.',
              source=SRC_DB, data_date=asof)
    path = f'{OUT}/trend_board.png'
    save_fig(fig, path)
    return path, sigs


def chart_board_history(sigs, sessions: int = 40):
    """Composite score history. Rows are names, columns are the last n sessions."""
    names = [t for _, g in BOARD_UNIVERSE for t in g if t in sigs]
    scores = pd.DataFrame({t: sigs[t][BOARD_COLS].sum(axis=1) for t in names}).dropna(how='all')
    scores = scores.tail(sessions)

    set_theme('white')
    fig, ax = plt.subplots(figsize=(16, 0.24 * len(names) + 3.0))
    fig.patch.set_facecolor('#FFFFFF')

    cmap = plt.matplotlib.colors.LinearSegmentedColormap.from_list(
        'lhm_board', [COLORS['dusk'], '#F4F7F9', COLORS['ocean']])
    ax.imshow(scores[names].T.values, aspect='auto', cmap=cmap, vmin=-3, vmax=3,
              interpolation='nearest')

    ax.set_yticks(range(len(names)))
    ax.set_yticklabels(names, fontsize=8, color=COLORS['deep'])
    step = max(1, len(scores) // 12)
    ax.set_xticks(range(0, len(scores), step))
    ax.set_xticklabels([d.strftime('%m/%d') for d in scores.index[::step]],
                       fontsize=8, color=COLORS['doldrums'], rotation=0)
    for sp in ax.spines.values():
        sp.set_color(COLORS['doldrums'])
        sp.set_linewidth(0.5)
    ax.tick_params(length=0)
    fig.subplots_adjust(top=0.86, bottom=0.10, left=0.10, right=0.94)

    brand_fig(fig, 'The Trend Board: Rolling History',
              f'Composite score, last {len(scores)} sessions. Dusk breaking, Ocean confirming.',
              source=SRC_DB, data_date=scores.index[-1])
    path = f'{OUT}/trend_board_history.png'
    save_fig(fig, path)
    return path


# ============================================================
# 3. THE PROGRAM PANEL
# ============================================================

def _stats(r: pd.Series, bench: pd.Series) -> dict:
    ann = 252
    ex = r - bench
    cum = (1 + r).cumprod()
    dd = cum / cum.cummax() - 1
    downside = r[r < 0].std() * np.sqrt(ann)
    yrs = len(r) / ann
    cagr = cum.iloc[-1] ** (1 / yrs) - 1
    vol = r.std() * np.sqrt(ann)
    return {
        'Excess Return, ann.': f'{(cagr - ((1+bench).cumprod().iloc[-1] ** (1/yrs) - 1))*100:.1f}%',
        'Return, ann.': f'{cagr*100:.1f}%',
        'Volatility': f'{vol*100:.0f}%',
        'Semi-Variance': f'{downside*100:.0f}%',
        'Max Drawdown': f'{dd.min()*100:.0f}%',
        'Sharpe Ratio': f'{cagr/vol:.2f}',
        'Sortino Ratio': f'{cagr/downside:.2f}',
        'Calmar Ratio': f'{cagr/abs(dd.min()):.2f}',
        'Days Positive': f'{(r > 0).mean()*100:.0f}%',
        'Skew': f'{r.skew():.2f}',
        'Kurtosis': f'{r.kurtosis():.1f}',
        'Max DD Days': f'{int((dd < 0).groupby((dd == 0).cumsum()).cumcount().max())}',
    }


def chart_program_panel(path_returns='/Users/bob/LHM/Outputs/regime_book/returns.parquet'):
    r = pd.read_parquet(path_returns).dropna()
    book, spy = r['book'], r['spy']

    set_theme('white')
    fig = plt.figure(figsize=(16, 10))
    fig.patch.set_facecolor('#FFFFFF')
    gs = fig.add_gridspec(2, 2, width_ratios=[3, 1], height_ratios=[1.35, 1],
                          left=0.075, right=0.955, top=0.855, bottom=0.11,
                          hspace=0.30, wspace=0.14)

    # -- growth of a dollar, log scale, drawdown ghosted underneath
    ax = fig.add_subplot(gs[0, 0])
    for s, c, lab in [(spy, COLORS['dusk'], 'Benchmark (SPY)'),
                      (book, COLORS['ocean'], 'Regime Book')]:
        ax.plot(s.index, (1 + s).cumprod(), color=c, lw=1.5, label=lab)
    ax.set_yscale('log')
    ax.set_ylabel('Growth of $1, log scale')
    style_ax(ax)

    ax2 = ax.twinx()
    for s, c in [(spy, COLORS['dusk']), (book, COLORS['ocean'])]:
        cum = (1 + s).cumprod()
        ax2.fill_between(s.index, (cum / cum.cummax() - 1) * 100, 0,
                         color=c, alpha=0.10, lw=0)
    ax2.set_ylim(-260, 0)
    ax2.set_yticks([])
    ax2.spines[:].set_visible(False)
    leg = ax.legend(loc='upper left', frameon=False, fontsize=10)
    for t in leg.get_texts():
        t.set_color(COLORS['doldrums'])

    # -- summary stats
    axs = fig.add_subplot(gs[0, 1])
    axs.axis('off')
    sb, ss = _stats(book, spy), _stats(spy, spy)
    axs.text(0.50, 1.0, 'Summary Statistics', ha='center', fontsize=11,
             fontweight='bold', color=COLORS['deep'])
    axs.text(0.62, 0.945, 'Book', ha='center', fontsize=9, fontweight='bold',
             color=COLORS['ocean'])
    axs.text(0.88, 0.945, 'SPY', ha='center', fontsize=9, fontweight='bold',
             color=COLORS['dusk'])
    for i, k in enumerate(sb):
        y = 0.90 - i * 0.072
        axs.text(0.0, y, k, fontsize=9, color=COLORS['doldrums'], va='center')
        axs.text(0.62, y, sb[k], ha='center', fontsize=9, va='center',
                 color=COLORS['deep'], fontweight='bold')
        axs.text(0.88, y, ss[k], ha='center', fontsize=9, va='center',
                 color=COLORS['doldrums'])

    # -- rolling six-month excess
    axr = fig.add_subplot(gs[1, :])
    def _roll_ann(s):
        g = (1 + s).rolling(126).apply(np.prod, raw=True)
        return g ** (252 / 126) - 1

    roll = ((_roll_ann(book) - _roll_ann(spy)) * 100).dropna()
    axr.plot(roll.index, roll, color=COLORS['ocean'], lw=1.2)
    axr.axhline(0, color=COLORS['fog'], lw=0.8)
    axr.axhline(roll.mean(), color=COLORS['sea'], ls='--', lw=1.0,
                label=f'Average: {roll.mean():.0f}%')
    axr.axhline(roll.min(), color=COLORS['venus'], ls='--', lw=1.0,
                label=f'Low: {roll.min():.0f}%')
    axr.set_ylabel('6-month rolling excess, ann. %')
    # The 2017 crypto slot puts a genuine 1,200% spike on this axis. Clip the
    # view so the other eighteen years stay readable, and say so on the chart.
    hi = np.nanpercentile(roll.values, 99.0)
    lo = np.nanpercentile(roll.values, 0.5)
    if roll.max() > hi * 1.5:
        axr.set_ylim(min(lo * 1.3, -20), hi * 1.4)
        axr.text(0.995, 0.94, f'Scale clipped. Peak {roll.max():.0f}% (2017 crypto slot).',
                 transform=axr.transAxes, ha='right', fontsize=8,
                 color=COLORS['doldrums'])
    style_ax(axr)
    leg = axr.legend(loc='upper left', frameon=False, fontsize=9, ncol=2)
    for t in leg.get_texts():
        t.set_color(COLORS['doldrums'])

    brand_fig(fig, 'The Program Panel',
              'Regime-aware concentrated book versus benchmark. INTERNAL: OOS figures unverified.',
              source=SRC_DB, data_date=r.index[-1])
    path = f'{OUT}/program_panel.png'
    save_fig(fig, path)
    return path


# ============================================================

def main():
    what = (sys.argv[1] if len(sys.argv) > 1 else 'all').lower()
    made = []
    if what in ('all', 'ribbon'):
        p, probs = chart_ribbon()
        made += [p, chart_ribbon_table(probs)]
    if what in ('all', 'board'):
        p, sigs = chart_trend_board()
        made += [p, chart_board_history(sigs)]
    if what in ('all', 'program'):
        made.append(chart_program_panel())
    for p in made:
        print(p)


if __name__ == '__main__':
    main()
