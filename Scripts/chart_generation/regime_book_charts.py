#!/usr/bin/env python3
"""
Regime book: backtest and allocation charts
===========================================
Companion to Scripts/backtest/regime_book_backtest.py. Renders the equity
curve, drawdowns, allocation through time, current allocation, the per-class
stop table, and the trade distribution.

Author: Lighthouse Macro
Date: 2026-07-26
"""

from __future__ import annotations

import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.insert(0, '/Users/bob/LHM/Scripts/chart_generation')
sys.path.insert(0, '/Users/bob/LHM/Scripts/backtest')
sys.path.insert(0, '/Users/bob/LHM/Scripts/analysis')

from lhm_chart_template import (  # noqa: E402
    COLORS, brand_fig, new_fig, save_fig, set_theme, set_xlim_to_data,
    style_ax, style_single_ax,
)
import regime_book_backtest as rbb  # noqa: E402
import regime_asset_returns as rar  # noqa: E402

OUT = '/Users/bob/LHM/Outputs/Charts/regime_book'
os.makedirs(OUT, exist_ok=True)
SRC = 'Lighthouse Macro; total-return index data'

CLASS_LABEL = {
    'us_equity': 'US Equity', 'intl_equity': 'International Equity',
    'rates': 'Rates', 'credit': 'Credit', 'real_assets': 'Real Assets',
    'crypto': 'Crypto', 'Cash': 'Cash',
}
CLASS_COLOR = {
    'US Equity': COLORS['ocean'], 'International Equity': COLORS['sky'],
    'Rates': COLORS['deep'], 'Credit': COLORS['sea'],
    'Real Assets': COLORS['dusk'], 'Crypto': COLORS['venus'],
    'Cash': COLORS['fog'],
}

R = rbb.run()
BOOK, BASE, SPY, S6040 = R['book'], R['baseline'], R['spy'], R['sixty40']
CAPPED = R['capped']
W = R['weights']
RES = R['results']
STOPS = R['stops']
TRADES = R['trades']
DATA_DATE = BOOK.index[-1]


def _footnote(fig, text):
    fig.text(0.03, 0.055, text, fontsize=8, color=COLORS['doldrums'],
             ha='left', va='bottom', style='italic')


def class_weights() -> pd.DataFrame:
    cols = {}
    for c in W.columns:
        lab = CLASS_LABEL.get(rbb.CLASS_MAP.get(c, 'Cash'), 'Cash')
        cols.setdefault(lab, []).append(c)
    return pd.DataFrame({lab: W[tk].sum(axis=1) for lab, tk in cols.items()})


def chart_21_equity_curve():
    fig, ax = new_fig(figsize=(14, 8))
    series = [('Regime Book, 25% position cap', CAPPED, COLORS['ocean'], 2.8),
              ('Regime Book, no cap (pure let-winners-run)', BOOK, COLORS['sea'], 2.0),
              ('Plain 200-day top-10 baseline', BASE, COLORS['sky'], 1.8),
              ('S&P 500', SPY, COLORS['dusk'], 2.0),
              ('60/40', S6040, COLORS['doldrums'], 1.8)]
    ends = sorted([(1 + s).cumprod().iloc[-1] for _, s, _, _ in series], reverse=True)
    for label, s, c, lw in series:
        eq = (1 + s).cumprod()
        ax.plot(eq.index, eq.values, color=c, linewidth=lw, label=label)
        # stagger the end pills so near-identical finishes do not overlap
        dy = (ends.index(eq.iloc[-1]) - (len(ends) - 1) / 2) * 3
        ax.annotate(f'{eq.iloc[-1]:.1f}x', xy=(eq.index[-1], eq.iloc[-1]),
                    xytext=(8, dy), textcoords='offset points', fontsize=9,
                    fontweight='bold', color='white', va='center',
                    bbox=dict(boxstyle='round,pad=0.28', facecolor=c, edgecolor='none'))
    ax.set_yscale('log')
    ax.axvline(pd.Timestamp(rbb.IS_END), color=COLORS['venus'], linestyle='--',
               linewidth=1.2)
    ax.text(pd.Timestamp(rbb.IS_END), ax.get_ylim()[1], ' stops locked, out-of-sample begins',
            fontsize=8.5, color=COLORS['venus'], va='top', ha='left')
    style_ax(ax)
    ax.tick_params(axis='both', length=0)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, p: f'{v:.0f}x'))
    ax.set_ylabel('Growth of $1, log scale', fontsize=10)
    set_xlim_to_data(ax, BOOK.index)
    leg = ax.legend(loc='upper left', fontsize=9.5, frameon=True, framealpha=0.95,
                    edgecolor=COLORS['doldrums'])
    leg.get_frame().set_linewidth(0.5)
    brand_fig(fig,
              title='Ten Slots, No Rebalancing, Stops That Fit the Asset',
              subtitle='Growth of one dollar since 2007, regime book versus a plain trend baseline, the S&P 500 and 60/40',
              source=SRC, data_date=DATA_DATE)
    _footnote(fig, 'Uncapped, one parabolic position (Bitcoin, 2017) grows into most of the book and takes it down with it.\n'
                   'Long-only, no leverage, gross of costs. Stops fixed after 2020. Internal research, not a track record.')
    save_fig(fig, f'{OUT}/chart_21_equity_curve.png')


def chart_22_drawdowns():
    fig, ax = new_fig(figsize=(14, 8))
    for label, s, c in [('Regime Book, 25% cap', CAPPED, COLORS['ocean']),
                        ('Regime Book, no cap', BOOK, COLORS['sea']),
                        ('S&P 500', SPY, COLORS['dusk']),
                        ('60/40', S6040, COLORS['doldrums'])]:
        eq = (1 + s).cumprod()
        dd = (eq / eq.cummax() - 1) * 100
        ax.plot(dd.index, dd.values, color=c, linewidth=2.0, label=label)
        ax.fill_between(dd.index, dd.values, 0, color=c, alpha=0.12)
    ax.axhline(0, color=COLORS['fog'], linewidth=1.0)
    style_single_ax(ax, fmt='{:.0f}%')
    ax.set_ylabel('Peak-to-trough drawdown', fontsize=10)
    set_xlim_to_data(ax, BOOK.index)
    leg = ax.legend(loc='lower left', fontsize=9.5, frameon=True, framealpha=0.95,
                    edgecolor=COLORS['doldrums'])
    leg.get_frame().set_linewidth(0.5)
    brand_fig(fig,
              title='Where the Stops Earn Their Keep',
              subtitle='Drawdown path of the regime book against the S&P 500 and 60/40',
              source=SRC, data_date=DATA_DATE)
    _footnote(fig, 'The uncapped book takes a 55% drawdown when its largest position unwinds. '
                   'Capping any single name at 25% cuts that to 21% and costs about a point of return a year.')
    save_fig(fig, f'{OUT}/chart_22_drawdowns.png')


def chart_23_allocation_through_time():
    cw = class_weights()
    order = ['US Equity', 'International Equity', 'Credit', 'Real Assets',
             'Crypto', 'Rates', 'Cash']
    cw = cw[[c for c in order if c in cw.columns]]
    cw = cw.resample('W-FRI').last().dropna(how='all') * 100

    fig, ax = new_fig(figsize=(14, 8))
    ax.stackplot(cw.index, [cw[c].values for c in cw.columns],
                 labels=list(cw.columns),
                 colors=[CLASS_COLOR[c] for c in cw.columns], linewidth=0)
    ax.set_ylim(0, 100)
    style_single_ax(ax, fmt='{:.0f}%')
    ax.set_ylabel('Share of book', fontsize=10)
    set_xlim_to_data(ax, cw.index)
    leg = ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.06), ncol=4,
                    fontsize=9, frameon=True, framealpha=0.95,
                    edgecolor=COLORS['doldrums'])
    leg.get_frame().set_linewidth(0.5)
    fig.subplots_adjust(bottom=0.20)
    brand_fig(fig,
              title='The Book Rotates Because Price Makes It Rotate',
              subtitle='Allocation by asset class through time, weights drift with performance between trades',
              source=SRC, data_date=DATA_DATE)
    _footnote(fig, 'Weights are market value shares. There is no calendar rebalancing, '
                   'so a position grows its own weight until it stops out.')
    save_fig(fig, f'{OUT}/chart_23_allocation_through_time.png')


def chart_24_current_allocation():
    cur = W.iloc[-1]
    cur = cur[cur > 1e-4].sort_values(ascending=True) * 100
    labels, colors = [], []
    for t in cur.index:
        cls = CLASS_LABEL.get(rbb.CLASS_MAP.get(t, 'Cash'), 'Cash')
        labels.append(f'{t}   ({cls})' if t != 'Cash' else 'Cash')
        colors.append(CLASS_COLOR[cls])

    fig, ax = new_fig(figsize=(13, 8))
    ax.barh(range(len(cur)), cur.values, color=colors, edgecolor='white',
            linewidth=0.7)
    ax.set_yticks(range(len(cur)))
    ax.set_yticklabels(labels, fontsize=10)
    ax.yaxis.tick_left()
    fig.subplots_adjust(left=0.20, right=0.95)
    style_ax(ax, right_primary=False)
    ax.tick_params(axis='both', length=0)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, p: f'{v:.0f}%'))
    ax.set_xlabel('Share of book', fontsize=10)
    for i, v in enumerate(cur.values):
        ax.text(v + 0.25, i, f'{v:.1f}%', va='center', fontsize=9,
                fontweight='bold', color=COLORS['deep'])
    cw = class_weights().iloc[-1].sort_values(ascending=False) * 100
    summary = '   '.join(f'{k} {v:.0f}%' for k, v in cw.items() if v > 0.5)
    brand_fig(fig,
              title=f'The Book Today: {rar.growth_inflation_regime().quadrant.iloc[-1]} Regime',
              subtitle='Current positions by market value share, colored by asset class',
              source=SRC, data_date=DATA_DATE)
    _footnote(fig, 'By asset class — ' + summary)
    save_fig(fig, f'{OUT}/chart_24_current_allocation.png')


def chart_25_stops_table():
    df = STOPS.copy()
    df['Stop'] = df.apply(lambda r: {
        '200d': f'200-day break, {r.X*100:.1f}% buffer',
        'atr': f'ATR chandelier, {r.k}x',
        'rs': f'Relative trend, {int(r.L)}-day',
    }.get(r.stop, ' + '.join(
        {'200d': f'200-day break {r.X*100:.1f}%', 'atr': f'ATR {r.k:g}x',
         'rs': f'Rel trend {int(r.L)}d'}[s] for s in r.stop.split('+'))), axis=1)
    df['Asset class'] = df.asset_class.map(CLASS_LABEL)
    show = df[['Asset class', 'Stop', 'IS_Sortino', 'IS_Payoff', 'IS_CAGR',
               'IS_MaxDD', 'NTrades']].copy()
    show['IS_CAGR'] = (show.IS_CAGR * 100).round(1).astype(str) + '%'
    show['IS_MaxDD'] = (show.IS_MaxDD * 100).round(1).astype(str) + '%'
    show['IS_Sortino'] = show.IS_Sortino.round(2)
    show['IS_Payoff'] = show.IS_Payoff.round(2)
    show.columns = ['Asset class', 'Winning stop', 'Sortino', 'Payoff ratio',
                    'CAGR', 'Max drawdown', 'Trades']

    fig, ax = new_fig(figsize=(14, 7))
    ax.axis('off')
    tbl = ax.table(cellText=show.values, colLabels=show.columns,
                   cellLoc='center', loc='center')
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(10)
    tbl.auto_set_column_width(col=list(range(len(show.columns))))
    tbl.scale(1, 2.1)
    for (r, c), cell in tbl.get_celld().items():
        cell.set_edgecolor('white')
        cell.set_linewidth(1.2)
        if r == 0:
            cell.set_facecolor(COLORS['ocean'])
            cell.set_text_props(color='white', fontweight='bold')
        else:
            cell.set_facecolor(COLORS['offwhite'] if r % 2 else 'white')
            cell.set_text_props(color=COLORS['deep'])
        if c == 1 and r > 0:
            cell.set_text_props(fontweight='bold')
    brand_fig(fig,
              title='One Stop Per Asset Class, Chosen By the Data',
              subtitle='Winning stop from the walk-forward search, with its in-sample statistics',
              source=SRC, data_date=pd.Timestamp(rbb.IS_END))
    _footnote(fig, 'Search covers every subset of the three candidate stops and their parameter grids, '
                   'scored in-sample through 2020 on a payoff-preserving blend of Sortino, Calmar, Omega, '
                   'payoff ratio and expectancy. Each class keeps the single best result.')
    save_fig(fig, f'{OUT}/chart_25_stops_by_class.png')


def chart_26_trade_distribution():
    tr = TRADES.copy()
    tr['ret'] = tr.ret * 100
    fig, ax = new_fig(figsize=(14, 8))
    bins = np.arange(-40, 205, 5)
    ax.hist(tr.ret[tr.ret >= 0], bins=bins, color=COLORS['ocean'],
            edgecolor='white', linewidth=0.5, label='Winners')
    ax.hist(tr.ret[tr.ret < 0], bins=bins, color=COLORS['dusk'],
            edgecolor='white', linewidth=0.5, label='Losers')
    wins, losses = tr.ret[tr.ret > 0], tr.ret[tr.ret < 0]
    ax.axvline(wins.mean(), color=COLORS['ocean'], linestyle='--', linewidth=1.4)
    ax.axvline(losses.mean(), color=COLORS['dusk'], linestyle='--', linewidth=1.4)
    ax.text(wins.mean(), ax.get_ylim()[1] * 0.92, f'  avg winner {wins.mean():+.1f}%',
            fontsize=9.5, color=COLORS['ocean'], fontweight='bold')
    ax.text(losses.mean(), ax.get_ylim()[1] * 0.82, f'avg loser {losses.mean():+.1f}%  ',
            fontsize=9.5, color=COLORS['dusk'], fontweight='bold', ha='right')
    style_single_ax(ax, fmt='{:.0f}')
    ax.set_ylabel('Number of trades', fontsize=10)
    ax.set_xlabel('Trade return', fontsize=10)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, p: f'{v:+.0f}%'))
    leg = ax.legend(loc='upper right', fontsize=9.5, frameon=True, framealpha=0.95,
                    edgecolor=COLORS['doldrums'])
    leg.get_frame().set_linewidth(0.5)
    brand_fig(fig,
              title='Small Losses, Long Right Tail',
              subtitle='Distribution of closed trade returns across the full backtest',
              source=SRC, data_date=DATA_DATE)
    _footnote(fig, f'{len(tr):,} closed trades. Win rate {(tr.ret>0).mean()*100:.0f}%. '
                   f'Payoff ratio {wins.mean()/abs(losses.mean()):.1f}x. '
                   'The book is designed to be wrong more than half the time and still compound.')
    save_fig(fig, f'{OUT}/chart_26_trade_distribution.png')


def chart_27_rolling_excess():
    exc = (BOOK - SPY).rolling(252).sum() * 100
    exc = exc.dropna()
    fig, ax = new_fig(figsize=(14, 8))
    ax.fill_between(exc.index, exc.values, 0, where=exc.values >= 0,
                    color=COLORS['ocean'], alpha=0.35, interpolate=True)
    ax.fill_between(exc.index, exc.values, 0, where=exc.values < 0,
                    color=COLORS['dusk'], alpha=0.35, interpolate=True)
    ax.plot(exc.index, exc.values, color=COLORS['deep'], linewidth=1.6)
    ax.axhline(0, color=COLORS['fog'], linewidth=1.0)
    style_single_ax(ax, fmt='{:+.0f}%')
    ax.set_ylabel('Trailing 12-month excess return vs S&P 500', fontsize=10)
    set_xlim_to_data(ax, exc.index)
    brand_fig(fig,
              title='The Book Gives Ground in Straight-Up Tapes',
              subtitle='Rolling twelve-month return of the regime book minus the S&P 500',
              source=SRC, data_date=DATA_DATE)
    _footnote(fig, 'Positive means the book beat the index over the prior year. '
                   'A cash-holding, stop-driven book is expected to lag a relentless bull tape.')
    save_fig(fig, f'{OUT}/chart_27_rolling_excess.png')


def chart_28_summary_table():
    r = RES.reset_index()
    r = r[r.window.isin(['FULL', 'IS', 'OOS'])]
    piv = r.set_index(['strategy', 'window'])
    show = pd.DataFrame({
        'CAGR': (piv.CAGR * 100).round(1).astype(str) + '%',
        'Volatility': (piv.Vol * 100).round(1).astype(str) + '%',
        'Max drawdown': (piv.MaxDD * 100).round(1).astype(str) + '%',
        'Sortino': piv.Sortino.round(2),
        'Calmar': piv.Calmar.round(2),
        'Omega': piv.Omega.round(2),
        'Payoff': piv.Payoff.round(2).fillna('—'),
        'Trades': piv.NTrades.fillna(0).astype(int),
    })
    show = show.reset_index()
    show.columns = ['Strategy', 'Window'] + list(show.columns[2:])

    fig, ax = new_fig(figsize=(14, 9))
    ax.axis('off')
    tbl = ax.table(cellText=show.values, colLabels=show.columns,
                   cellLoc='center', loc='center')
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(9.5)
    tbl.auto_set_column_width(col=list(range(len(show.columns))))
    tbl.scale(1, 1.9)
    for (rr, c), cell in tbl.get_celld().items():
        cell.set_edgecolor('white')
        cell.set_linewidth(1.2)
        if rr == 0:
            cell.set_facecolor(COLORS['ocean'])
            cell.set_text_props(color='white', fontweight='bold')
        else:
            strat = show.iloc[rr - 1, 0]
            hero = strat == 'Regime Book, 25% cap'
            cell.set_facecolor('#e8f1f7' if hero
                               else (COLORS['offwhite'] if rr % 2 else 'white'))
            cell.set_text_props(color=COLORS['deep'],
                                fontweight='bold' if hero else 'normal')
    brand_fig(fig,
              title='The Scorecard',
              subtitle='Full sample, in-sample and out-of-sample statistics for the book and its benchmarks',
              source=SRC, data_date=DATA_DATE)
    _footnote(fig, 'In-sample runs 2007 to 2020, out-of-sample 2021 to date. Gross of costs and taxes. '
                   'Out-of-sample figures are internal research and are not externally citable until separately verified.')
    save_fig(fig, f'{OUT}/chart_28_summary_table.png')


def main():
    set_theme('white')
    for fn in [chart_21_equity_curve, chart_22_drawdowns,
               chart_23_allocation_through_time, chart_24_current_allocation,
               chart_25_stops_table, chart_26_trade_distribution,
               chart_27_rolling_excess, chart_28_summary_table]:
        print(f'  {fn.__name__} ...', end=' ', flush=True)
        fn()
        print('ok')
    print(f'\nRendered to {OUT}')


if __name__ == '__main__':
    main()
