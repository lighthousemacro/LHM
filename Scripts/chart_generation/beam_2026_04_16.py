"""
Beam — April 16, 2026
Stocks Printed a Record. Bonds and Gold Didn't Buy It.

Generates 5 charts from Lighthouse_Master.db. Writes to
/Users/bob/LHM/Outputs/Beams/2026-04-16/.

Charts:
  F1: SPX + 50d/200d MA with war-period shading
  F2: Cross-asset rebased to Feb 27, 2026 (SPX, 10Y yield, Gold proxy, WTI)
  F3: HY OAS with 300 bps threshold
  F4: AAII bull-bear with SPX overlay
  F5: RSXFS YoY nominal vs real (CARTS proxy)
"""

import os
import sys
import sqlite3
from datetime import date
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lhm_chart_template import (
    COLORS, set_theme, new_fig,
    style_ax, style_dual_ax, style_single_ax,
    add_last_value_label, add_recessions,
    set_xlim_to_data, brand_fig, save_fig, legend_style,
)


def set_xlim_proportional(ax, start, end, right_frac=0.02):
    """Zero left pad, right pad = right_frac of the data span."""
    span = (end - start).days
    pad = pd.Timedelta(days=max(1, int(span * right_frac)))
    ax.set_xlim(start, end + pad)

DB_PATH = '/Users/bob/LHM/Data/databases/Lighthouse_Master.db'
OUT_DIR = '/Users/bob/LHM/Outputs/Beams/2026-04-16'
WAR_START = pd.Timestamp('2026-02-27')
WAR_END = pd.Timestamp('2026-04-07')

# Apr 15, 2026 tips pulled from TradingView (pipeline did not yet refresh in time).
APR15 = pd.Timestamp('2026-04-15')
TIPS = {
    'SPX_Close': 7022.96,
    'VIXCLS': 18.23,
    'DGS10': 4.27,
    'DCOILWTICO': 91.96,
    # No BAMLH0A0HYM2 tip — FRED H.15 BAML series publishes T+1. Use DB latest (Apr 14 = 2.84).
}
# AAII survey for week ending Apr 15, 2026 (from aaii.com): Bull 31.7%, Bear 42.8%, spread = -11.1%
AAII_APR15_SPREAD = -0.111  # as fraction (to match DB schema)

os.makedirs(OUT_DIR, exist_ok=True)
set_theme('white')


def q(sql, params=()):
    with sqlite3.connect(f'file:{DB_PATH}?mode=ro', uri=True, timeout=30) as con:
        return pd.read_sql_query(sql, con, params=params, parse_dates=['date']).set_index('date').sort_index()


def obs(series_id, start='2018-01-01', tip=True):
    """Pull series from DB; optionally append TIPS[series_id] at APR15 if the
    DB is stale (latest obs < APR15)."""
    df = q(
        "SELECT date, value FROM observations WHERE series_id=? AND date>=? ORDER BY date",
        (series_id, start),
    )
    s = df['value'].dropna()
    if tip and series_id in TIPS and (len(s) == 0 or s.index[-1] < APR15):
        s = pd.concat([s, pd.Series({APR15: TIPS[series_id]})]).sort_index()
    return s


# -----------------------------------------------------------------------------
# Figure 1 — SPX + 50d / 200d MAs, war shading
# -----------------------------------------------------------------------------
def fig1():
    # Pull a long-enough window to compute 200d MA ourselves so the tip
    # flows through into the moving averages.
    spx_full = obs('SPX_Close', '2024-01-01')
    ma50 = spx_full.rolling(50).mean().dropna()
    ma200 = spx_full.rolling(200).mean().dropna()
    spx = spx_full.loc['2025-02-01':]
    ma50 = ma50.loc['2025-02-01':]
    ma200 = ma200.loc['2025-02-01':]

    fig, ax = new_fig(figsize=(14, 7.5))
    ax.plot(spx.index, spx.values, color=COLORS['doldrums'], linewidth=2.5, label='S&P 500')
    ax.plot(ma50.index, ma50.values, color=COLORS['dusk'], linewidth=2, linestyle='--', label='50d MA')
    ax.plot(ma200.index, ma200.values, color=COLORS['ocean'], linewidth=2, linestyle='--', label='200d MA')

    ax.axvspan(WAR_START, WAR_END, color=COLORS['port'], alpha=0.10, zorder=0, label='Iran War')

    last_date = spx.index[-1]
    last_val = spx.iloc[-1]

    style_single_ax(ax, fmt='{:,.0f}')
    add_last_value_label(ax, spx, COLORS['doldrums'], fmt='{:,.0f}')
    set_xlim_proportional(ax, spx.index.min(), spx.index.max())
    ax.legend(loc='upper left', **legend_style())

    brand_fig(
        fig,
        title='S&P 500: Fully Round-Tripped the War',
        subtitle='Close through 50d and 200d moving averages, with war-period shading',
        source='FRED (S&P 500)',
        data_date=last_date,
    )
    path = os.path.join(OUT_DIR, 'fig1_spx_mas.png')
    save_fig(fig, path)
    return path, last_date, last_val


# -----------------------------------------------------------------------------
# Figure 2 — Cross-asset rebased to war start (Feb 27, 2026)
# -----------------------------------------------------------------------------
def fig2(gold_override=None):
    """Rebased cross-asset. gold_override lets us pass a hardcoded Gold series
    (dict of {date: price}) if no DB series exists."""
    spx = obs('SPX_Close', '2025-12-01')
    ten = obs('DGS10', '2025-12-01')
    wti = obs('DCOILWTICO', '2025-12-01')

    # Gold from TradingView CSV (TVC_GOLD, 1D).
    gold_csv = '/Users/bob/LHM/Data/TVC_GOLD, 1D.csv'
    gdf = pd.read_csv(gold_csv, parse_dates=['time']).set_index('time').sort_index()
    gold = gdf['close'].loc['2025-12-01':].dropna()

    # Anchor all series at the leftmost common start date so everything
    # begins at 100 and diverges from there.
    def first_val(s):
        if s is None or len(s) == 0:
            return None
        return float(s.iloc[0])

    base_spx = first_val(spx)
    base_ten = first_val(ten)
    base_wti = first_val(wti)
    base_gold = first_val(gold) if gold is not None else None

    fig, ax1 = new_fig(figsize=(14, 7.5))
    ax2 = ax1.twinx()

    # LHS: SPX, 10Y, Gold (all moved modestly)
    spx_r = 100 * spx / base_spx
    ten_r = 100 * ten / base_ten
    gold_r = 100 * gold / base_gold if gold is not None else None
    wti_r = 100 * wti / base_wti

    ax1.plot(spx_r.index, spx_r.values, color=COLORS['ocean'], linewidth=3, label='S&P 500')
    ax1.plot(ten_r.index, ten_r.values, color=COLORS['dusk'], linewidth=2, label='10Y Yield')
    if gold is not None:
        ax1.plot(gold_r.index, gold_r.values, color=COLORS['sky'], linewidth=2, label='Gold')

    # RHS: WTI (big swing)
    ax2.plot(wti_r.index, wti_r.values, color=COLORS['sea'], linewidth=2, label='WTI Crude')

    # Symmetric axes around 100 so both scales anchor at the rebase line.
    # LHS (SPX/10Y/Gold): tight range around 100
    lhs_series = [spx_r, ten_r] + ([gold_r] if gold is not None else [])
    lhs_max_dev = max(abs(s.max() - 100) for s in lhs_series) + \
                  max(abs(s.min() - 100) for s in lhs_series)
    lhs_half = max(abs(s - 100).max() for s in lhs_series) * 1.15
    ax1.set_ylim(100 - lhs_half, 100 + lhs_half)

    # RHS (WTI): wider range, also centered on 100
    rhs_half = abs(wti_r - 100).max() * 1.15
    ax2.set_ylim(100 - rhs_half, 100 + rhs_half)

    # War start + ceasefire markers
    ax1.axvline(WAR_START, color=COLORS['doldrums'], linestyle='--', linewidth=1, alpha=0.6)
    ax1.axvline(WAR_END, color=COLORS['doldrums'], linestyle='--', linewidth=1, alpha=0.6)
    ymin, ymax = ax1.get_ylim()
    ax1.text(WAR_START, ymax - (ymax-ymin)*0.02, ' War starts Feb 27', fontsize=9, color=COLORS['doldrums'], va='top')
    ax1.text(WAR_END, ymax - (ymax-ymin)*0.02, ' Ceasefire Apr 7', fontsize=9, color=COLORS['doldrums'], va='top')

    # Reference line at 100 (aligned on both axes since both are centered at 100)
    ax1.axhline(100, color=COLORS['fog'], linestyle='--', linewidth=1, zorder=0)

    style_dual_ax(ax1, ax2, COLORS['ocean'], COLORS['sea'])
    add_last_value_label(ax1, spx_r, COLORS['ocean'], fmt='{:.0f}', side='left')
    add_last_value_label(ax1, ten_r, COLORS['dusk'], fmt='{:.0f}', side='left')
    if gold is not None:
        add_last_value_label(ax1, gold_r, COLORS['sky'], fmt='{:.0f}', side='left')
    add_last_value_label(ax2, wti_r, COLORS['sea'], fmt='{:.0f}', side='right')

    all_end = max(spx.index.max(), ten.index.max(), wti.index.max())
    all_start = max(spx.index.min(), ten.index.min(), wti.index.min())
    set_xlim_proportional(ax1, all_start, all_end)

    # Combined legend
    from matplotlib.lines import Line2D
    legend_items = [
        Line2D([0],[0], color=COLORS['ocean'], linewidth=3, label='S&P 500 (LHS)'),
        Line2D([0],[0], color=COLORS['dusk'], linewidth=2, label='10Y Yield (LHS)'),
    ]
    if gold is not None:
        legend_items.append(Line2D([0],[0], color=COLORS['sky'], linewidth=2, label='Gold (LHS)'))
    legend_items.append(Line2D([0],[0], color=COLORS['sea'], linewidth=2, label='WTI Crude (RHS)'))
    ax1.legend(handles=legend_items, loc='upper left', **legend_style())

    brand_fig(
        fig,
        title='Cross-Asset: Stocks Priced a Ceasefire. Others Didn\'t.',
        subtitle=f'Rebased to 100 at Dec 1, 2025. Ceasefire line marks war end (Apr 7).',
        source='FRED, TradingView (Gold)',
        data_date=spx.index[-1],
    )
    path = os.path.join(OUT_DIR, 'fig2_crossasset_rebased.png')
    save_fig(fig, path)
    return path, spx.index[-1]


# -----------------------------------------------------------------------------
# Figure 3 — HY OAS with 300 bps threshold
# -----------------------------------------------------------------------------
def fig3():
    hy = obs('BAMLH0A0HYM2', '2018-01-01')
    fig, ax = new_fig(figsize=(14, 7.5))
    ax.plot(hy.index, hy.values, color=COLORS['ocean'], linewidth=3, label='HY OAS')
    ax.axhline(3.00, color=COLORS['venus'], linewidth=2, linestyle='-', alpha=0.8,
               label='300 bps (Complacency Threshold)')

    add_recessions(ax, start_date='2018-01-01')
    style_single_ax(ax, fmt='{:.2f}%')
    add_last_value_label(ax, hy, COLORS['ocean'], fmt='{:.2f}%')
    set_xlim_proportional(ax, hy.index.min(), hy.index.max())
    ax.legend(loc='upper right', **legend_style())

    brand_fig(
        fig,
        title='High Yield Spreads: Back Through Complacent',
        subtitle='ICE BofA US HY OAS, daily',
        source='FRED (BAMLH0A0HYM2)',
        data_date=hy.index[-1],
    )
    path = os.path.join(OUT_DIR, 'fig3_hy_oas.png')
    save_fig(fig, path)
    return path, hy.index[-1], hy.iloc[-1]


# -----------------------------------------------------------------------------
# Figure 4 — AAII Bull-Bear with SPX overlay
# -----------------------------------------------------------------------------
def fig4():
    aaii = obs('AAII_Bull_Bear_Spread', '2020-01-01', tip=False)  # weekly, fraction
    # Append Apr 15 AAII reading from aaii.com
    if len(aaii) == 0 or aaii.index[-1] < APR15:
        aaii = pd.concat([aaii, pd.Series({APR15: AAII_APR15_SPREAD})]).sort_index()
    spx = obs('SPX_Close', '2020-01-01')

    fig, ax1 = new_fig(figsize=(14, 7.5))
    ax2 = ax1.twinx()

    # AAII bars on LHS (left axis). Values are fractions (e.g., -0.025 = -2.5%), convert to %.
    aaii_pct = aaii * 100
    colors = np.where(aaii_pct >= 0, COLORS['starboard'], COLORS['venus'])
    ax1.bar(aaii_pct.index, aaii_pct.values, color=colors, width=6, alpha=0.55, label='AAII Bull-Bear')
    ax1.axhline(0, color=COLORS['fog'], linewidth=1, linestyle='--')

    ax2.plot(spx.index, spx.values, color=COLORS['ocean'], linewidth=2.5, label='S&P 500')

    style_dual_ax(ax1, ax2, COLORS['venus'], COLORS['ocean'])
    ax1.yaxis.set_major_formatter(plt_pct_fmt())
    ax2.yaxis.set_major_formatter(plt_comma_fmt())
    add_last_value_label(ax1, aaii_pct, COLORS['venus'], fmt='{:+.1f}%', side='left')
    add_last_value_label(ax2, spx, COLORS['ocean'], fmt='{:,.0f}', side='right')
    xmin = min(aaii_pct.index.min(), spx.index.min())
    xmax = max(aaii_pct.index.max(), spx.index.max())
    set_xlim_proportional(ax1, xmin, xmax)

    # Manual legend (combining both axes)
    from matplotlib.patches import Patch
    from matplotlib.lines import Line2D
    legend_items = [
        Patch(facecolor=COLORS['venus'], alpha=0.55, label='AAII Bull-Bear (LHS)'),
        Line2D([0], [0], color=COLORS['ocean'], linewidth=2.5, label='S&P 500 (RHS)'),
    ]
    ax1.legend(handles=legend_items, loc='upper left', **legend_style())

    brand_fig(
        fig,
        title='Record Highs. Net-Bearish Retail.',
        subtitle='AAII Bull-Bear Spread (bars) with S&P 500 (line)',
        source='AAII Sentiment Survey, FRED',
        data_date=max(aaii.index[-1], spx.index[-1]),
    )
    path = os.path.join(OUT_DIR, 'fig4_aaii_spx.png')
    save_fig(fig, path)
    return path, aaii.index[-1], float(aaii_pct.iloc[-1])


# -----------------------------------------------------------------------------
# Figure 5 — Retail sales YoY, nominal vs real proxy
# -----------------------------------------------------------------------------
def fig5():
    # Nominal retail sales (RSXFS = Advance Retail Sales: Retail Trade and Food Services ex-Auto Dealers)
    # CPI Headline YoY for real deflation
    rsx = obs('RSXFS', '2016-01-01', tip=False)
    rsx_yoy = (rsx.pct_change(12) * 100).dropna()

    cpi = obs('CPIAUCSL', '2015-01-01', tip=False)
    cpi_yoy = (cpi.pct_change(12) * 100).dropna()

    # Align and compute real approximation: nominal YoY minus CPI YoY
    joined = pd.concat([rsx_yoy.rename('nom'), cpi_yoy.rename('cpi')], axis=1).dropna()
    joined['real'] = joined['nom'] - joined['cpi']

    fig, ax = new_fig(figsize=(14, 7.5))
    ax.plot(joined.index, joined['nom'], color=COLORS['ocean'], linewidth=3, label='Nominal Retail YoY')
    ax.plot(joined.index, joined['real'], color=COLORS['dusk'], linewidth=3, label='Real Retail YoY (CPI-deflated)')
    ax.axhline(0, color=COLORS['fog'], linewidth=1, linestyle='--')

    add_recessions(ax, start_date='2018-01-01')
    style_single_ax(ax, fmt='{:+.1f}%')
    add_last_value_label(ax, joined['nom'], COLORS['ocean'], fmt='{:+.1f}%')
    add_last_value_label(ax, joined['real'], COLORS['dusk'], fmt='{:+.1f}%')
    set_xlim_proportional(ax, joined.index.min(), joined.index.max())
    ax.legend(loc='upper left', **legend_style())

    brand_fig(
        fig,
        title='The Nominal-Real Gap Is Widening',
        subtitle='Retail sales ex-auto dealers, YoY. Real = nominal less headline CPI.',
        source='FRED (RSXFS, CPIAUCSL)',
        data_date=joined.index[-1],
    )
    path = os.path.join(OUT_DIR, 'fig5_retail_nominal_real.png')
    save_fig(fig, path)
    return path, joined.index[-1], float(joined['nom'].iloc[-1]), float(joined['real'].iloc[-1])


# Helper formatters (imported inline to avoid polluting template)
def plt_pct_fmt():
    from matplotlib.ticker import FuncFormatter
    return FuncFormatter(lambda x, _: f'{x:+.0f}%')


def plt_comma_fmt():
    from matplotlib.ticker import FuncFormatter
    return FuncFormatter(lambda x, _: f'{x:,.0f}')


if __name__ == '__main__':
    print('=' * 70)
    print('BEAM 2026-04-16 — CHART GENERATION')
    print('=' * 70)

    print('\n[1/5] SPX + MAs ...')
    p1, d1, v1 = fig1()
    print(f'  → {p1}')
    print(f'  → Latest SPX: {d1.date()} = {v1:,.2f}')

    print('\n[2/5] Cross-asset rebased ...')
    p2, d2 = fig2()
    print(f'  → {p2}')
    print(f'  → Latest: {d2.date()}')

    print('\n[3/5] HY OAS ...')
    p3, d3, v3 = fig3()
    print(f'  → {p3}')
    print(f'  → Latest HY OAS: {d3.date()} = {v3:.2f}%')

    print('\n[4/5] AAII Bull-Bear ...')
    p4, d4, v4 = fig4()
    print(f'  → {p4}')
    print(f'  → Latest AAII: {d4.date()} = {v4:+.2f}%')

    print('\n[5/5] Retail nominal vs real ...')
    p5, d5, nom, real = fig5()
    print(f'  → {p5}')
    print(f'  → Latest: {d5.date()} nom={nom:+.2f}%  real={real:+.2f}%')

    print('\nAll charts saved to:', OUT_DIR)
