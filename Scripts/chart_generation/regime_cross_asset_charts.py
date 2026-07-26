#!/usr/bin/env python3
"""
Regime x Cross-Asset chart pack
===============================
Builds the LHM answer to the Prometheus-style regime exhibits: what every
asset class actually pays in each macro regime, plus the regime history,
trend monitors, and the rolling-return periodic table.

Renders to Outputs/Charts/regime_cross_asset/.

Author: Lighthouse Macro
Date: 2026-07-26
"""

from __future__ import annotations

import os
import sys
from datetime import datetime

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
from matplotlib.patches import Patch, Rectangle

sys.path.insert(0, '/Users/bob/LHM/Scripts/chart_generation')
sys.path.insert(0, '/Users/bob/LHM/Scripts/analysis')

from lhm_chart_template import (  # noqa: E402
    COLORS, add_last_value_label, add_recessions, add_smart_legend, brand_fig,
    new_fig, new_fig_multi, save_fig, set_theme, set_xlim_to_data, style_ax,
    style_single_ax,
)
import regime_asset_returns as rar  # noqa: E402

OUT = '/Users/bob/LHM/Outputs/Charts/regime_cross_asset'
os.makedirs(OUT, exist_ok=True)

SRC_MACRO = 'Lighthouse Macro composites; NBER'
SRC_ASSET = 'Lighthouse Macro; total-return index data'

QUAD_COLOR = {
    'Goldilocks':  COLORS['sea'],
    'Overheat':    COLORS['dusk'],
    'Stagflation': COLORS['venus'],
    'Contraction': COLORS['deep'],
}
MRI_COLOR = {
    'Low Risk': COLORS['sea'], 'Neutral': COLORS['sky'],
    'Elevated': COLORS['dusk'], 'High Risk': COLORS['venus'],
    'Crisis': COLORS['port'],
}

DIVERGING = LinearSegmentedColormap.from_list(
    'lhm_div', [COLORS['port'], '#f6e6e6', '#ffffff', '#dceaf3', COLORS['ocean']])


# --------------------------------------------------------------- shared data

print('Loading regimes and returns...')
GI = rar.growth_inflation_regime()
MRI = rar.mri_regime()
RET_MAJ = rar.daily_returns(rar.MAJORS_PLUS)
RET_SEC = rar.daily_returns(rar.SECTORS)
RET_SUB = rar.daily_returns(rar.SUB_ASSETS)
RET_FAC = rar.daily_returns(rar.FACTORS)
DATA_DATE = RET_MAJ.dropna(how='all').index[-1]

Q = rar.QUADRANTS
STATS_MAJ = rar.regime_stats(RET_MAJ, GI.quadrant, Q)
STATS_SEC = rar.regime_stats(RET_SEC, GI.quadrant, Q)
STATS_SUB = rar.regime_stats(RET_SUB, GI.quadrant, Q)
STATS_FAC = rar.regime_stats(RET_FAC, GI.quadrant, Q)
STATS_MRI = rar.regime_stats(RET_MAJ, MRI.band, rar.MRI_BANDS)
STATS_MRI_SUB = rar.regime_stats(RET_SUB, MRI.band, rar.MRI_BANDS)


# ------------------------------------------------------------------- helpers

def heatmap(ax, mat: pd.DataFrame, fmt='{:+.1f}', vcenter=0.0, cbar_label=None,
            fig=None, sort_by=None, lim=None):
    """Diverging heatmap with in-cell value labels. Rows = assets, cols = regimes."""
    m = mat.copy().astype(float)
    if sort_by is not None and sort_by in m.columns:
        m = m.sort_values(sort_by, ascending=False)
    vals = m.values
    finite = vals[np.isfinite(vals)]
    if lim is None:
        lim = max(abs(np.nanpercentile(finite, 10) - vcenter),
                  abs(np.nanpercentile(finite, 90) - vcenter)) or 1.0
    norm = TwoSlopeNorm(vmin=vcenter - lim, vcenter=vcenter, vmax=vcenter + lim)
    im = ax.imshow(vals, cmap=DIVERGING, norm=norm, aspect='auto')

    ax.set_xticks(range(m.shape[1]))
    ax.set_xticklabels(m.columns, fontsize=10, fontweight='bold')
    ax.set_yticks(range(m.shape[0]))
    ax.set_yticklabels(m.index, fontsize=9.5)
    ax.yaxis.tick_left()
    ax.xaxis.tick_top()
    if fig is not None:
        fig.subplots_adjust(left=0.17, right=0.90)
    ax.tick_params(axis='both', length=0)
    for spine in ax.spines.values():
        spine.set_color(COLORS['doldrums'])
        spine.set_linewidth(0.5)

    for r in range(m.shape[0]):
        for c in range(m.shape[1]):
            v = vals[r, c]
            if not np.isfinite(v):
                ax.text(c, r, 'n/a', ha='center', va='center', fontsize=8,
                        color=COLORS['doldrums'])
                continue
            shade = abs(v - vcenter) / lim
            colr = 'white' if shade > 0.62 else COLORS['deep']
            ax.text(c, r, fmt.format(v), ha='center', va='center',
                    fontsize=9.5, fontweight='bold', color=colr)
    # cell separators
    for r in range(m.shape[0] + 1):
        ax.axhline(r - 0.5, color='white', linewidth=1.2)
    for c in range(m.shape[1] + 1):
        ax.axvline(c - 0.5, color='white', linewidth=1.2)

    if cbar_label and fig is not None:
        cb = fig.colorbar(im, ax=ax, fraction=0.024, pad=0.02)
        cb.set_label(cbar_label, fontsize=9, color=COLORS['doldrums'])
        cb.ax.tick_params(labelsize=8, length=0, colors=COLORS['doldrums'])
        cb.outline.set_edgecolor(COLORS['doldrums'])
        cb.outline.set_linewidth(0.5)
    return m


def regime_ribbon(ax, quad: pd.Series, colors: dict, y0=0.0, y1=1.0, alpha=0.85):
    """Paint contiguous regime blocks as background bands."""
    q = quad.dropna()
    change = (q != q.shift()).cumsum()
    for _, blk in q.groupby(change):
        ax.axvspan(blk.index[0], blk.index[-1], ymin=y0, ymax=y1,
                   color=colors.get(blk.iloc[0], COLORS['fog']), alpha=alpha,
                   linewidth=0, zorder=0)


def footnote(fig, text):
    fig.text(0.03, 0.055, text, fontsize=8, color=COLORS['doldrums'],
             ha='left', va='bottom', style='italic')


def sample_note(stats, cols=None):
    n = stats['n_days']
    cols = cols if cols is not None else n.columns
    parts = [f'{c}: {int(n[c].max()):,}d' for c in cols]
    return 'Trading days per regime (deepest series) — ' + ' | '.join(parts)


# ------------------------------------------------------------------- exhibits

def chart_01_regime_history():
    fig, ax = new_fig(figsize=(14, 8))
    regime_ribbon(ax, GI.quadrant, QUAD_COLOR, alpha=0.30)
    ax.plot(GI.index, GI.growth, color=COLORS['ocean'], linewidth=2.4,
            label='Growth (Activity Pulse, 21d avg)')
    ax.plot(GI.index, GI.inflation, color=COLORS['dusk'], linewidth=2.4,
            label='Inflation (Inflation Heat, 21d avg)')
    ax.axhline(0, color=COLORS['fog'], linestyle='--', linewidth=1.0, zorder=1)
    style_single_ax(ax, fmt='{:+.1f}')
    fig.subplots_adjust(right=0.90)
    ax.set_ylabel('Standard deviations from average', fontsize=10, labelpad=12)
    add_last_value_label(ax, GI.growth, COLORS['ocean'], fmt='{:+.2f}')
    add_last_value_label(ax, GI.inflation, COLORS['dusk'], fmt='{:+.2f}')
    set_xlim_to_data(ax, GI.index)
    ax.set_ylim(ax.get_ylim()[0] - 1.1, ax.get_ylim()[1])
    handles = [Patch(facecolor=c, alpha=0.30, label=f'{k} ({rar.QUAD_DESC[k]})')
               for k, c in QUAD_COLOR.items()]
    leg1 = ax.legend(handles=handles, loc='lower left', fontsize=8.5, ncol=2,
                     frameon=True, framealpha=0.95, edgecolor=COLORS['doldrums'])
    leg1.get_frame().set_linewidth(0.5)
    ax.add_artist(leg1)
    add_smart_legend(ax, fontsize=9, prefer='top')
    add_recessions(ax)
    brand_fig(fig,
              title=f'The Macro Regime Map: Currently {GI.quadrant.iloc[-1]}',
              subtitle='Growth and inflation pressure, standardized, with the four-quadrant regime shaded behind',
              source=SRC_MACRO, data_date=GI.index[-1])
    save_fig(fig, f'{OUT}/chart_01_regime_history.png')


def chart_02_majors_bar():
    m = STATS_MAJ['ann_return'].loc[list(rar.MAJORS_PLUS.keys())]
    fig, ax = new_fig(figsize=(14, 8))
    x = np.arange(len(m.index))
    w = 0.20
    for i, q in enumerate(Q):
        ax.bar(x + (i - 1.5) * w, m[q].values, w, label=q, color=QUAD_COLOR[q],
               edgecolor='white', linewidth=0.6)
    for i, q in enumerate(Q):
        for j, v in enumerate(m[q].values):
            if not np.isfinite(v):
                continue
            yv = min(v, 34.0)
            ax.text(x[j] + (i - 1.5) * w, yv + (1.5 if v >= 0 else -1.5),
                    f'{v:+.0f}', ha='center',
                    va='bottom' if v >= 0 else 'top', fontsize=7.5,
                    color=COLORS['deep'])
    ax.set_xticks(x)
    ax.set_xticklabels(m.index, fontsize=10, fontweight='bold')
    ax.axhline(0, color=COLORS['deep'], linewidth=1.0)
    # Bitcoin's Goldilocks bar runs off the top. Clip the axis so the other
    # seven asset classes stay readable; the printed value carries the truth.
    ax.set_ylim(min(-25, np.nanmin(m.values) - 5), 40)
    style_single_ax(ax, fmt='{:+.0f}%')
    ax.set_ylabel('Annualized total return', fontsize=10)
    ax.legend(loc='upper right', fontsize=9, frameon=True, framealpha=0.95,
              edgecolor=COLORS['doldrums'], ncol=2).get_frame().set_linewidth(0.5)
    brand_fig(fig,
              title='Every Asset Class Has a Regime It Gets Paid In',
              subtitle='Annualized total return by growth/inflation regime, 2004 to present',
              source=SRC_ASSET, data_date=DATA_DATE)
    footnote(fig, sample_note(STATS_MAJ) + '. Bitcoin sample starts 2014; its '
                  'Goldilocks bar is clipped by the axis, the printed value is the true reading.')
    save_fig(fig, f'{OUT}/chart_02_majors_return_by_regime.png')


def chart_03_majors_heatmap():
    fig, ax = new_fig(figsize=(13, 8))
    heatmap(ax, STATS_MAJ['ann_return'].loc[list(rar.MAJORS_PLUS.keys())],
            fmt='{:+.1f}%', fig=fig, cbar_label='Annualized return %', lim=25)
    brand_fig(fig,
              title='The Regime Payoff Grid',
              subtitle='Annualized total return by asset class and growth/inflation regime',
              source=SRC_ASSET, data_date=DATA_DATE)
    footnote(fig, 'Colour scale capped at +/-25% so a single outlier does not wash out the grid; printed values are uncapped. ' + sample_note(STATS_MAJ))
    save_fig(fig, f'{OUT}/chart_03_majors_heatmap_return.png')


def chart_04_majors_sharpe():
    fig, ax = new_fig(figsize=(13, 8))
    heatmap(ax, STATS_MAJ['sharpe'].loc[list(rar.MAJORS_PLUS.keys())],
            fmt='{:+.2f}', fig=fig, cbar_label='Return / volatility')
    brand_fig(fig,
              title='Risk-Adjusted, the Regime Map Looks Different',
              subtitle='Annualized return divided by annualized volatility, by asset class and regime',
              source=SRC_ASSET, data_date=DATA_DATE)
    footnote(fig, 'Ratio of annualized total return to annualized daily volatility within each regime. '
                  'Not a Sharpe ratio: no cash rate is subtracted.')
    save_fig(fig, f'{OUT}/chart_04_majors_heatmap_riskadj.png')


def chart_05_majors_hitrate():
    fig, ax = new_fig(figsize=(13, 8))
    m = STATS_MAJ['hit_rate'].loc[list(rar.MAJORS_PLUS.keys())]
    heatmap(ax, m, fmt='{:.0f}%', vcenter=50.0, fig=fig,
            cbar_label='Share of up days %')
    brand_fig(fig,
              title='How Often Each Asset Wins, By Regime',
              subtitle='Share of positive daily returns within each growth/inflation regime',
              source=SRC_ASSET, data_date=DATA_DATE)
    footnote(fig, 'Centered at 50%. Blue = wins more days than it loses.')
    save_fig(fig, f'{OUT}/chart_05_majors_heatmap_hitrate.png')


def chart_06_majors_drawdown():
    fig, ax = new_fig(figsize=(13, 8))
    heatmap(ax, STATS_MAJ['max_dd'].loc[list(rar.MAJORS_PLUS.keys())],
            fmt='{:.0f}%', fig=fig, cbar_label='Worst peak-to-trough %')
    brand_fig(fig,
              title='What It Costs You To Be Wrong',
              subtitle='Worst peak-to-trough drawdown experienced within each regime',
              source=SRC_ASSET, data_date=DATA_DATE)
    footnote(fig, 'Drawdown measured on the return path inside each regime only, '
                  'so episodes are stitched across separate regime spells.')
    save_fig(fig, f'{OUT}/chart_06_majors_heatmap_drawdown.png')


def chart_07_sectors():
    fig, ax = new_fig(figsize=(13, 9))
    heatmap(ax, STATS_SEC['ann_return'], fmt='{:+.1f}%', fig=fig,
            cbar_label='Annualized return %', sort_by='Goldilocks', lim=25)
    brand_fig(fig,
              title='Sector Leadership Rotates With the Regime',
              subtitle='Annualized total return by S&P 500 sector and growth/inflation regime',
              source=SRC_ASSET, data_date=DATA_DATE)
    footnote(fig, 'Real Estate and Communication Services carry shorter histories '
                  '(2015 and 2018 sector reconstitutions), so their cells cover fewer regime days.')
    save_fig(fig, f'{OUT}/chart_07_sectors_heatmap.png')


def chart_08_subassets():
    fig, ax = new_fig(figsize=(13, 13))
    heatmap(ax, STATS_SUB['ann_return'], fmt='{:+.1f}%', fig=fig,
            cbar_label='Annualized return %', sort_by='Goldilocks', lim=25)
    brand_fig(fig,
              title='The Full Sub-Asset Class Regime Grid',
              subtitle='Annualized total return across rates, credit, regions, style, real assets and crypto',
              source=SRC_ASSET, data_date=DATA_DATE)
    footnote(fig, 'Colour scale capped at +/-25% so a single outlier does not wash out the grid; printed values are uncapped. ' + sample_note(STATS_SUB) + '. Start dates vary by instrument.')
    save_fig(fig, f'{OUT}/chart_08_subassets_heatmap.png')


def chart_09_factors():
    fig, ax = new_fig(figsize=(13, 8))
    heatmap(ax, STATS_FAC['ann_return'], fmt='{:+.1f}%', fig=fig,
            cbar_label='Annualized return %', sort_by='Goldilocks', lim=20)
    brand_fig(fig,
              title='Factors Are Regime Bets in Disguise',
              subtitle='Annualized total return by US equity style factor and growth/inflation regime',
              source=SRC_ASSET, data_date=DATA_DATE)
    footnote(fig, 'Momentum, Quality, Min Vol and Value ETFs launched 2011 to 2013, '
                  'so those rows exclude the 2008 to 2009 cycle.')
    save_fig(fig, f'{OUT}/chart_09_factors_heatmap.png')


def chart_10_mri_bands():
    fig, ax = new_fig(figsize=(13, 8))
    heatmap(ax, STATS_MRI['ann_return'].loc[list(rar.MAJORS_PLUS.keys())],
            fmt='{:+.1f}%', fig=fig, cbar_label='Annualized return %', lim=25)
    brand_fig(fig,
              title='The Risk Dial Pays Differently Than the Regime Map',
              subtitle='Annualized total return by asset class and Macro Risk Index band',
              source=SRC_ASSET, data_date=DATA_DATE)
    footnote(fig, 'Colour scale capped at +/-25% so a single outlier does not wash out the grid; printed values are uncapped. ' + sample_note(STATS_MRI) + '. Bands are the canonical MRI thresholds.')
    save_fig(fig, f'{OUT}/chart_10_mri_band_heatmap.png')


def chart_11_mri_subassets():
    fig, ax = new_fig(figsize=(13, 13))
    heatmap(ax, STATS_MRI_SUB['ann_return'], fmt='{:+.1f}%', fig=fig,
            cbar_label='Annualized return %', sort_by='Crisis', lim=25)
    brand_fig(fig,
              title='What Actually Works When the Risk Dial Redlines',
              subtitle='Annualized total return by sub-asset class and Macro Risk Index band, ranked by crisis performance',
              source=SRC_ASSET, data_date=DATA_DATE)
    footnote(fig, 'Colour scale capped at +/-25% so a single outlier does not wash out the grid; printed values are uncapped. ' + sample_note(STATS_MRI_SUB))
    save_fig(fig, f'{OUT}/chart_11_mri_subassets_heatmap.png')


def chart_12_mri_history():
    fig, ax = new_fig(figsize=(14, 8))
    regime_ribbon(ax, MRI.band.astype(object), MRI_COLOR, alpha=0.22)
    ax.plot(MRI.index, MRI.mri, color=COLORS['deep'], linewidth=2.4,
            label='Macro Risk Index (21d avg)')
    for lvl in (-0.5, 0.5, 1.0, 1.5):
        ax.axhline(lvl, color=COLORS['fog'], linestyle='--', linewidth=0.9, zorder=1)
    style_single_ax(ax, fmt='{:+.1f}')
    ax.set_ylabel('Standard deviations', fontsize=10)
    add_last_value_label(ax, MRI.mri, COLORS['deep'], fmt='{:+.2f}')
    set_xlim_to_data(ax, MRI.index)
    handles = [Patch(facecolor=c, alpha=0.22, label=k) for k, c in MRI_COLOR.items()]
    leg = ax.legend(handles=handles, loc='upper left', fontsize=9, ncol=5,
                    frameon=True, framealpha=0.95, edgecolor=COLORS['doldrums'])
    leg.get_frame().set_linewidth(0.5)
    add_recessions(ax)
    brand_fig(fig,
              title=f'The Risk Dial Reads {MRI.band.iloc[-1]}',
              subtitle='Macro Risk Index with the five canonical regime bands shaded behind',
              source=SRC_MACRO, data_date=MRI.index[-1])
    save_fig(fig, f'{OUT}/chart_12_mri_history.png')


def chart_13_trend_monitors():
    px = rar.load_prices(list(rar.MAJORS.values()))
    fig, axes = new_fig_multi(3, 2, figsize=(14, 12))
    for ax, (name, tkr) in zip(axes.flat, rar.MAJORS.items()):
        s = px[tkr].dropna()
        sig = rar.trend_signal(s)
        cum = (1 + s.pct_change().fillna(0)).cumprod()
        ax2 = ax.twinx()
        ax.fill_between(sig.index, 0, sig.values, where=sig.values > 0,
                        color=COLORS['ocean'], alpha=0.28, linewidth=0, step='mid')
        ax.fill_between(sig.index, 0, sig.values, where=sig.values < 0,
                        color=COLORS['dusk'], alpha=0.28, linewidth=0, step='mid')
        ax.set_ylim(-1.15, 1.15)
        ax.set_yticks([-1, 0, 1])
        ax.set_yticklabels(['Bear', 'Mixed', 'Bull'], fontsize=8)
        ax2.plot(cum.index, cum.values, color=COLORS['deep'], linewidth=1.8)
        ax2.set_yscale('log')
        style_ax(ax, right_primary=False)
        ax.tick_params(axis='both', length=0, labelsize=8)
        ax2.tick_params(axis='both', length=0, labelsize=8)
        for sp in ax2.spines.values():
            sp.set_visible(False)
        ax2.set_yticks([])
        ax.set_title(f'{name}  ({tkr})   trend: '
                     f'{"Bullish" if sig.iloc[-1] > 0 else "Bearish" if sig.iloc[-1] < 0 else "Mixed"}',
                     fontsize=10, fontweight='bold', loc='left',
                     color=COLORS['deep'])
        ax.xaxis.set_major_locator(mdates.YearLocator(4))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    brand_fig(fig,
              title='Trend Monitors: The Six Majors',
              subtitle='Two-speed trend state (50-day and 200-day) shaded behind cumulative total return, log scale',
              source=SRC_ASSET, data_date=DATA_DATE)
    footnote(fig, 'Bull = price above both the 50-day and 200-day average. '
                  'Bear = below both. Mixed = the two disagree.')
    save_fig(fig, f'{OUT}/chart_13_trend_monitors.png')


def chart_14_extended_trend():
    tickers = {**rar.SECTORS, **{k: v for k, v in rar.SUB_ASSETS.items()
                                 if v not in rar.SECTORS.values()}}
    px = rar.load_prices(list(tickers.values()))
    end = px.index[-1]
    start = end - pd.Timedelta(days=365)
    rows, labels = [], []
    for name, tkr in tickers.items():
        if tkr not in px.columns:
            continue
        sig = rar.trend_signal(px[tkr].dropna()).loc[start:end]
        rows.append(sig.resample('W-FRI').last())
        labels.append(f'{name} ({tkr})')
    mat = pd.concat(rows, axis=1).T
    mat.index = labels
    order = mat.mean(axis=1).sort_values(ascending=False).index
    mat = mat.loc[order]

    fig, ax = new_fig(figsize=(14, 14))
    cmap = LinearSegmentedColormap.from_list('trend3', [COLORS['dusk'], COLORS['fog'], COLORS['ocean']])
    ax.imshow(mat.values, cmap=cmap, vmin=-1, vmax=1, aspect='auto')
    ax.set_yticks(range(len(mat.index)))
    ax.set_yticklabels(mat.index, fontsize=8.5)
    ax.yaxis.tick_left()
    step = max(1, mat.shape[1] // 13)
    ticks = list(range(0, mat.shape[1], step))
    ax.set_xticks(ticks)
    ax.set_xticklabels([mat.columns[i].strftime('%m/%d/%y') for i in ticks],
                       fontsize=8, rotation=0)
    ax.xaxis.tick_top()
    ax.tick_params(axis='both', length=0)
    for sp in ax.spines.values():
        sp.set_color(COLORS['doldrums']); sp.set_linewidth(0.5)
    handles = [Patch(facecolor=COLORS['ocean'], label='Bullish (above both averages)'),
               Patch(facecolor=COLORS['fog'], label='Mixed'),
               Patch(facecolor=COLORS['dusk'], label='Bearish (below both averages)')]
    leg = ax.legend(handles=handles, loc='lower center', bbox_to_anchor=(0.5, -0.075),
                    ncol=3, fontsize=9, frameon=True, framealpha=0.95,
                    edgecolor=COLORS['doldrums'])
    leg.get_frame().set_linewidth(0.5)
    brand_fig(fig,
              title='Two-Speed Trend Across the Extended Universe',
              subtitle='Weekly trend state over the last twelve months, ranked by how bullish the year has been',
              source=SRC_ASSET, data_date=DATA_DATE)
    save_fig(fig, f'{OUT}/chart_14_extended_trend_universe.png')


def chart_15_periodic_table():
    tickers = {
        'SPX': 'SPY', 'Nasdaq': 'QQQ', 'SmCap': 'IWM', 'EAFE': 'EFA', 'EM': 'EEM',
        'Agg': 'AGG', 'LT Tsy': 'TLT', 'IG': 'LQD', 'HY': 'HYG', 'TIPS': 'TIP',
        'Cash': 'BIL', 'Gold': 'GLD', 'Comdty': 'DBC', 'REITs': 'VNQ',
        'USD': 'UUP', 'BTC': 'BTC',
    }
    roll = rar.rolling_returns(tickers, months=3).dropna(how='all')
    roll = roll.loc['2017-01-01':]
    roll = roll.iloc[::13]  # quarterly columns keep the table readable
    palette = [COLORS['ocean'], COLORS['dusk'], COLORS['sky'], COLORS['sea'],
               COLORS['venus'], COLORS['deep'], COLORS['starboard'], COLORS['port'],
               '#89CCFF', '#FFB08C', '#8CD9C4', '#C48CBB', '#A3B7C9', '#F4D06F',
               '#6FA8C4', '#B5651D']
    cmap = {k: palette[i % len(palette)] for i, k in enumerate(tickers)}
    dark = {COLORS['deep'], COLORS['port'], COLORS['starboard'], COLORS['ocean'],
            COLORS['venus'], '#B5651D'}

    n_rows = len(tickers)
    fig, ax = new_fig(figsize=(19, 10))
    for ci, (dt, col) in enumerate(roll.iterrows()):
        ranked = col.dropna().sort_values(ascending=False)
        for ri, (name, val) in enumerate(ranked.items()):
            c = cmap[name]
            ax.add_patch(Rectangle((ci, n_rows - ri - 1), 1, 1, facecolor=c,
                                   edgecolor='white', linewidth=0.7))
            ax.text(ci + 0.5, n_rows - ri - 0.5, name, ha='center', va='center',
                    fontsize=8.5, fontweight='bold',
                    color='white' if c in dark else COLORS['deep'])
    ax.set_xlim(0, roll.shape[0])
    ax.set_ylim(0, n_rows)
    ticks = list(range(roll.shape[0]))
    ax.set_xticks([t + 0.5 for t in ticks])
    ax.set_xticklabels([roll.index[t].strftime("%b '%y") for t in ticks],
                       fontsize=8, rotation=45, ha='right')
    ax.set_yticks([])
    ax.tick_params(axis='both', length=0)
    for sp in ax.spines.values():
        sp.set_color(COLORS['doldrums']); sp.set_linewidth(0.5)
    ax.text(-0.006, 0.985, 'Best', transform=ax.transAxes, ha='right', va='top',
            fontsize=9, fontweight='bold', color=COLORS['ocean'])
    ax.text(-0.006, 0.015, 'Worst', transform=ax.transAxes, ha='right', va='bottom',
            fontsize=9, fontweight='bold', color=COLORS['dusk'])
    brand_fig(fig,
              title='Periodic Table of Rolling Three-Month Returns',
              subtitle='Total return by asset class, ranked best to worst on a rolling three-month basis',
              source=SRC_ASSET, data_date=DATA_DATE)
    fig.subplots_adjust(bottom=0.16)
    footnote(fig, 'Columns sampled quarterly from weekly data. '
                  'Cash = 1-3 month T-Bills. Comdty = broad commodity basket.')
    save_fig(fig, f'{OUT}/chart_15_periodic_table.png')


def chart_16_current_read():
    """Where every major asset stands right now, against its regime average."""
    cur = GI.quadrant.iloc[-1]
    names = list(rar.MAJORS_PLUS.keys())
    reg_avg = STATS_MAJ['ann_return'][cur].loc[names]
    last_63 = (RET_MAJ[names].tail(63).add(1).prod() ** (252 / 63) - 1) * 100
    dfp = pd.DataFrame({'Regime average': reg_avg,
                        'Last 3 months (annualized)': last_63}).dropna()
    dfp = dfp.sort_values('Last 3 months (annualized)')

    fig, ax = new_fig(figsize=(14, 8))
    y = np.arange(len(dfp))
    ax.barh(y + 0.19, dfp['Regime average'], 0.38, color=COLORS['sky'],
            label=f'{cur} regime average since 2004', edgecolor='white', linewidth=0.6)
    ax.barh(y - 0.19, dfp['Last 3 months (annualized)'], 0.38, color=COLORS['ocean'],
            label='Trailing 3 months, annualized', edgecolor='white', linewidth=0.6)
    ax.set_yticks(y)
    ax.set_yticklabels(dfp.index, fontsize=10, fontweight='bold')
    ax.yaxis.tick_left()
    ax.axvline(0, color=COLORS['deep'], linewidth=1.0)
    style_ax(ax, right_primary=False)
    ax.tick_params(axis='both', length=0)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, p: f'{v:+.0f}%'))
    ax.set_xlabel('Annualized total return', fontsize=10)
    leg = ax.legend(loc='lower right', fontsize=9.5, frameon=True, framealpha=0.95,
                    edgecolor=COLORS['doldrums'])
    leg.get_frame().set_linewidth(0.5)
    brand_fig(fig,
              title=f'Running Hot or Cold Against the {cur} Script',
              subtitle='Trailing three-month annualized return versus the regime average for each asset class',
              source=SRC_ASSET, data_date=DATA_DATE)
    save_fig(fig, f'{OUT}/chart_16_current_vs_regime_average.png')


def chart_17_regime_frequency():
    q = GI.quadrant.dropna()
    counts = q.value_counts().reindex(Q)
    share = counts / counts.sum() * 100
    yr = q.groupby([q.index.year, q]).size().unstack().reindex(columns=Q).fillna(0)
    yr = yr.div(yr.sum(axis=1), axis=0) * 100

    fig, ax = new_fig(figsize=(14, 8))
    bottom = np.zeros(len(yr))
    for qd in Q:
        ax.bar(yr.index, yr[qd], bottom=bottom, color=QUAD_COLOR[qd],
               label=f'{qd} ({share[qd]:.0f}% of sample)', width=0.82,
               edgecolor='white', linewidth=0.5)
        bottom += yr[qd].values
    ax.set_ylim(0, 100)
    style_single_ax(ax, fmt='{:.0f}%')
    ax.set_ylabel('Share of days in the year', fontsize=10)
    fig.subplots_adjust(bottom=0.20)
    leg = ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.10), ncol=2,
                    fontsize=9, frameon=True, framealpha=0.95,
                    edgecolor=COLORS['doldrums'])
    leg.get_frame().set_linewidth(0.5)
    brand_fig(fig,
              title='Regimes Cluster, They Do Not Alternate',
              subtitle='Share of each calendar year spent in each growth/inflation regime',
              source=SRC_MACRO, data_date=GI.index[-1])
    save_fig(fig, f'{OUT}/chart_17_regime_frequency.png')


def chart_18_best_worst():
    m = STATS_SUB['ann_return']
    fig, axes = new_fig_multi(2, 2, figsize=(14, 11))
    for ax, qd in zip(axes.flat, Q):
        s = m[qd].dropna().sort_values()
        top = pd.concat([s.head(5), s.tail(5)])
        colors = [COLORS['dusk'] if v < 0 else COLORS['ocean'] for v in top.values]
        ax.barh(range(len(top)), top.values, color=colors, edgecolor='white',
                linewidth=0.5)
        ax.set_yticks(range(len(top)))
        ax.set_yticklabels(top.index, fontsize=8.5)
        ax.yaxis.tick_left()
        ax.axvline(0, color=COLORS['deep'], linewidth=0.9)
        style_ax(ax, right_primary=False)
        ax.tick_params(axis='both', length=0, labelsize=8)
        ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, p: f'{v:+.0f}%'))
        ax.set_title(f'{qd} — {rar.QUAD_DESC[qd]}', fontsize=10.5,
                     fontweight='bold', loc='left', color=QUAD_COLOR[qd])
        for i, v in enumerate(top.values):
            ax.text(v + (1.5 if v >= 0 else -1.5), i, f'{v:+.0f}%',
                    va='center', ha='left' if v >= 0 else 'right',
                    fontsize=7.5, color=COLORS['doldrums'])
    fig.subplots_adjust(wspace=0.45)
    brand_fig(fig,
              title='Five Best, Five Worst, In Every Regime',
              subtitle='Annualized total return extremes across the sub-asset class universe',
              source=SRC_ASSET, data_date=DATA_DATE)
    save_fig(fig, f'{OUT}/chart_18_best_worst_by_regime.png')


def chart_19_regime_dispersion():
    m = STATS_SUB['ann_return'].dropna(how='any')
    spread = (m.max(axis=1) - m.min(axis=1)).sort_values(ascending=True)
    fig, ax = new_fig(figsize=(13, 11))
    ax.barh(range(len(spread)), spread.values, color=COLORS['ocean'],
            edgecolor='white', linewidth=0.5)
    ax.set_yticks(range(len(spread)))
    ax.set_yticklabels(spread.index, fontsize=8.5)
    ax.yaxis.tick_left()
    style_ax(ax, right_primary=False)
    ax.tick_params(axis='both', length=0)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, p: f'{v:.0f}pp'))
    ax.set_xlabel('Best regime minus worst regime, annualized return', fontsize=10)
    for i, v in enumerate(spread.values):
        ax.text(v + 1.2, i, f'{v:.0f}', va='center', fontsize=7.5,
                color=COLORS['doldrums'])
    brand_fig(fig,
              title='Which Assets Care Most About the Regime',
              subtitle='Gap between the best and worst growth/inflation regime for each sub-asset class',
              source=SRC_ASSET, data_date=DATA_DATE)
    footnote(fig, 'Only instruments with a full reading in all four regimes are shown.')
    save_fig(fig, f'{OUT}/chart_19_regime_dispersion.png')


def chart_20_vol_by_regime():
    fig, ax = new_fig(figsize=(13, 8))
    heatmap(ax, STATS_MAJ['ann_vol'].loc[list(rar.MAJORS_PLUS.keys())],
            fmt='{:.0f}%', vcenter=float(np.nanmedian(STATS_MAJ['ann_vol'].values)),
            fig=fig, cbar_label='Annualized volatility %')
    brand_fig(fig,
              title='Volatility Is Regime-Dependent Too',
              subtitle='Annualized volatility of daily total returns by asset class and regime',
              source=SRC_ASSET, data_date=DATA_DATE)
    footnote(fig, 'Centered on the median cell. Blue = calmer than typical, orange = wilder.')
    save_fig(fig, f'{OUT}/chart_20_majors_heatmap_vol.png')


def main():
    set_theme('white')
    charts = [
        chart_01_regime_history, chart_02_majors_bar, chart_03_majors_heatmap,
        chart_04_majors_sharpe, chart_05_majors_hitrate, chart_06_majors_drawdown,
        chart_07_sectors, chart_08_subassets, chart_09_factors, chart_10_mri_bands,
        chart_11_mri_subassets, chart_12_mri_history, chart_13_trend_monitors,
        chart_14_extended_trend, chart_15_periodic_table, chart_16_current_read,
        chart_17_regime_frequency, chart_18_best_worst, chart_19_regime_dispersion,
        chart_20_vol_by_regime,
    ]
    for fn in charts:
        print(f'  {fn.__name__} ...', end=' ', flush=True)
        fn()
        print('ok')
    print(f'\nRendered {len(charts)} charts to {OUT}')


if __name__ == '__main__':
    main()
