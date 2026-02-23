"""
HORIZON 2026 - CHART GENERATOR V2
Lighthouse Macro | December 2025

Correct LHM Visual Style:
- NO gridlines
- Clean spines
- RIGHT Y-axis primary
- Pink/salmon danger zones (shaded backgrounds)
- "NOW:" callout box on right with current value
- Formula box bottom left
- Source line bottom left (gray)
- LIGHTHOUSE MACRO top left (ocean blue)
- MACRO, ILLUMINATED. bottom right (ocean blue, NOT gray)
- Historical event markers with pink dots
- Dashed threshold lines (orange/red)
- No fill under single-line curves
- Hot pink/magenta for moving averages
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
import warnings

warnings.filterwarnings('ignore')

# ============================================================================
# LHM VISUAL STANDARDS
# ============================================================================

LHM_COLORS = {
    'ocean': '#2389BB',      # Primary data series, branding
    'dusk': '#FF6723',       # Secondary / Warning thresholds
    'electric': '#03DDFF',   # Volatility / Highlights
    'hot': '#FF00F0',        # Moving averages, extreme stress
    'sea': '#289389',        # Neutral / Balanced
    'silvs': '#D1D1D1',      # Source text only
    'down_red': '#FF3333',   # Bearish / Danger
    'up_green': '#008000',   # Bullish
    'danger_zone': '#FFE4E1', # Light pink for danger shading
    'safe_zone': '#E6F3FF',   # Light blue for safe shading
}

plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans']
plt.rcParams['font.size'] = 10
plt.rcParams['axes.facecolor'] = 'white'
plt.rcParams['figure.facecolor'] = 'white'

# Database path
DB_PATH = '/Users/bob/LHM/projects/lighthouse-macro/charts/output/horizon_data.db'


def get_db_data(table: str, start_date: str = '2000-01-01') -> pd.Series:
    """Fetch data from SQLite database."""
    try:
        conn = sqlite3.connect(DB_PATH)
        query = f"SELECT date, value FROM {table} WHERE date >= '{start_date}' ORDER BY date"
        df = pd.read_sql_query(query, conn, parse_dates=['date'])
        conn.close()
        if df.empty:
            return pd.Series(dtype=float)
        return df.set_index('date')['value']
    except Exception as e:
        print(f"Warning: Could not fetch {table}: {e}")
        return pd.Series(dtype=float)


def apply_lhm_style(ax):
    """Apply LHM visual standards. RIGHT Y-axis primary, no left gap, gap on right."""
    ax.grid(False)
    ax.spines['top'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['right'].set_color('#CCCCCC')
    ax.spines['bottom'].set_color('#CCCCCC')
    ax.tick_params(colors='#666666', labelsize=9)

    # Move Y-axis to right
    ax.yaxis.set_label_position('right')
    ax.yaxis.tick_right()

    # No gap on left, gap on right (extend x-axis ~3% past last data point)
    xlim = ax.get_xlim()
    xrange = xlim[1] - xlim[0]
    ax.set_xlim(xlim[0], xlim[1] + xrange * 0.03)


def add_branding(fig):
    """Add LHM branding - BOTH in ocean blue."""
    fig.text(0.01, 0.99, 'LIGHTHOUSE MACRO',
             fontsize=9, fontweight='bold',
             color=LHM_COLORS['ocean'],
             verticalalignment='top', horizontalalignment='left')
    fig.text(0.99, 0.01, 'MACRO, ILLUMINATED.',
             fontsize=8, style='italic',
             color=LHM_COLORS['ocean'],  # Ocean blue, NOT gray
             verticalalignment='bottom', horizontalalignment='right')


def add_source(ax, source_text: str):
    """Add source citation in gray at bottom left."""
    ax.text(0.01, -0.08, f'Source: {source_text}',
            transform=ax.transAxes, fontsize=8,
            color=LHM_COLORS['silvs'],  # Gray for source only
            verticalalignment='top', horizontalalignment='left')


def add_formula_box(ax, formula: str):
    """Add formula box at bottom left."""
    props = dict(boxstyle='round,pad=0.3', facecolor='white',
                 edgecolor=LHM_COLORS['ocean'], linewidth=1, alpha=0.95)
    ax.text(0.01, 0.08, formula, transform=ax.transAxes, fontsize=8,
            verticalalignment='bottom', horizontalalignment='left',
            bbox=props, family='monospace')


def add_now_box(ax, value: str, x_pos=0.98, y_pos=0.85):
    """Add 'NOW:' callout box on right side."""
    props = dict(boxstyle='round,pad=0.4', facecolor='white',
                 edgecolor=LHM_COLORS['down_red'], linewidth=2, alpha=0.95)
    ax.text(x_pos, y_pos, f'NOW: {value}', transform=ax.transAxes,
            fontsize=11, fontweight='bold',
            color=LHM_COLORS['down_red'],
            verticalalignment='top', horizontalalignment='right',
            bbox=props)


def add_danger_zone(ax, threshold, direction='above', label=None):
    """Add pink shaded danger zone above or below threshold."""
    ylim = ax.get_ylim()
    if direction == 'above':
        ax.axhspan(threshold, ylim[1] * 1.1, alpha=0.15, color=LHM_COLORS['down_red'], zorder=0)
    else:
        ax.axhspan(ylim[0] * 1.1, threshold, alpha=0.15, color=LHM_COLORS['down_red'], zorder=0)

    # Add threshold line
    ax.axhline(threshold, color=LHM_COLORS['dusk'], linestyle='--', linewidth=1.5, alpha=0.8)
    if label:
        ax.text(0.02, threshold, f' {label}', transform=ax.get_yaxis_transform(),
                fontsize=9, color=LHM_COLORS['dusk'], fontweight='bold',
                verticalalignment='bottom')


def add_event_marker(ax, date, value, label, offset=(30, 20)):
    """Add historical event marker with pink dot and label."""
    ax.scatter([date], [value], s=80, color=LHM_COLORS['hot'],
               edgecolors='white', linewidth=1.5, zorder=10)
    ax.annotate(label, xy=(date, value), xytext=offset,
                textcoords='offset points', fontsize=8,
                color=LHM_COLORS['hot'],
                bbox=dict(boxstyle='round,pad=0.2', facecolor='white',
                         edgecolor=LHM_COLORS['hot'], alpha=0.9))


def add_current_dot(ax, date, value):
    """Add current value dot (larger, red)."""
    ax.scatter([date], [value], s=100, color=LHM_COLORS['down_red'],
               edgecolors='white', linewidth=2, zorder=10)


def add_recession_bars(ax, start_date='2000-01-01'):
    """Add subtle gray recession shading."""
    recessions = [
        ('2001-03-01', '2001-11-01'),
        ('2007-12-01', '2009-06-01'),
        ('2020-02-01', '2020-04-01')
    ]
    for start, end in recessions:
        if pd.to_datetime(start) >= pd.to_datetime(start_date):
            ax.axvspan(pd.to_datetime(start), pd.to_datetime(end),
                       alpha=0.08, color='gray', zorder=0)


# ============================================================================
# CHART FUNCTIONS
# ============================================================================

def chart_01_rrp_drawdown():
    """ON RRP Drawdown: The 35-Month Exhaustion"""
    rrp = get_db_data('rrp_balance', '2021-01-01')
    if rrp.empty:
        return None

    fig, ax = plt.subplots(figsize=(12, 7))

    # Main line - no fill
    ax.plot(rrp.index, rrp.values, linewidth=2, color=LHM_COLORS['ocean'])

    # Stats
    peak_val = rrp.max()
    peak_date = rrp.idxmax()
    current_val = rrp.iloc[-1]
    current_date = rrp.index[-1]
    pct_decline = ((peak_val - current_val) / peak_val) * 100

    # Peak marker
    add_event_marker(ax, peak_date, peak_val, f'Peak: ${peak_val:,.0f}B', offset=(40, -20))

    # Current dot
    add_current_dot(ax, current_date, current_val)

    # Stats box upper right
    stats = f'Peak: ${peak_val:,.0f}B\nCurrent: ${current_val:.1f}B\nDecline: {pct_decline:.1f}%'
    props = dict(boxstyle='round', facecolor='white', edgecolor=LHM_COLORS['ocean'], linewidth=1.5)
    ax.text(0.98, 0.98, stats, transform=ax.transAxes, fontsize=9,
            verticalalignment='top', horizontalalignment='right',
            bbox=props, family='monospace')

    ax.set_ylabel('ON RRP Balance ($B)', fontweight='bold')
    ax.set_title('ON RRP Drawdown: The 35-Month Exhaustion', fontsize=13, fontweight='bold', pad=15)

    apply_lhm_style(ax)
    add_branding(fig)
    add_source(ax, 'Federal Reserve H.4.1')

    plt.tight_layout()
    return fig


def chart_02_liquidity_cushion_index():
    """Liquidity Cushion Index"""
    rrp = get_db_data('rrp_balance', '2017-01-01')
    reserves = get_db_data('reserves', '2017-01-01')
    gdp = get_db_data('gdp', '2017-01-01')

    if rrp.empty or reserves.empty or gdp.empty:
        return None

    # Align and calculate
    df = pd.DataFrame({'rrp': rrp, 'reserves': reserves}).dropna()
    gdp_aligned = gdp.reindex(df.index, method='ffill')

    rrp_gdp = (df['rrp'] / gdp_aligned) * 100
    res_gdp = (df['reserves'] / gdp_aligned) * 100

    # Z-scores
    z_rrp = (rrp_gdp - rrp_gdp.mean()) / rrp_gdp.std()
    z_res = (res_gdp - res_gdp.mean()) / res_gdp.std()
    lci = (z_rrp + z_res) / 2
    lci = lci.dropna()

    fig, ax = plt.subplots(figsize=(12, 7))

    # Main line
    ax.plot(lci.index, lci.values, linewidth=2, color=LHM_COLORS['ocean'])

    # Danger zone below -1
    ylim = ax.get_ylim()
    ax.set_ylim(min(lci.min() - 0.5, -3), max(lci.max() + 0.5, 2.5))
    ax.axhspan(ax.get_ylim()[0], -1, alpha=0.12, color=LHM_COLORS['down_red'], zorder=0)

    # Stress threshold
    ax.axhline(-1, color=LHM_COLORS['dusk'], linestyle='--', linewidth=1.5)
    ax.text(0.02, -1.05, 'STRESS THRESHOLD', transform=ax.get_yaxis_transform(),
            fontsize=9, color=LHM_COLORS['dusk'], fontweight='bold')

    # Historical markers
    # Sept 2019
    sept_2019 = lci.loc['2019-09-01':'2019-09-30']
    if len(sept_2019) > 0:
        val = sept_2019.iloc[0]
        add_event_marker(ax, sept_2019.index[0], val, f'Sept 2019\n{val:.2f}σ', offset=(20, -40))

    # Mar 2020
    mar_2020 = lci.loc['2020-03-01':'2020-03-31']
    if len(mar_2020) > 0:
        val = mar_2020.iloc[0]
        add_event_marker(ax, mar_2020.index[0], val, f'Mar 2020\n{val:.2f}σ', offset=(20, 30))

    # Current
    current_val = lci.iloc[-1]
    add_current_dot(ax, lci.index[-1], current_val)
    add_now_box(ax, f'{current_val:.2f}σ')

    ax.set_ylabel('LCI (Z-Score)', fontweight='bold')
    ax.set_title('Liquidity Cushion Index', fontsize=13, fontweight='bold', pad=15)

    apply_lhm_style(ax)
    add_branding(fig)
    add_source(ax, 'Federal Reserve, BEA')
    add_formula_box(ax, 'LCI = Avg[z(RRP/GDP), z(Reserves/GDP)]')

    plt.tight_layout()
    return fig


def chart_16_labor_fragility_index():
    """Labor Fragility Index"""
    quits = get_db_data('quits_rate', '2001-01-01')
    hires = get_db_data('hires_rate', '2001-01-01')
    urate = get_db_data('unemployment_rate', '2001-01-01')

    if quits.empty or hires.empty or urate.empty:
        return None

    # Align
    df = pd.DataFrame({'quits': quits, 'hires': hires, 'urate': urate}).dropna()

    # Z-scores (inverted for quits and hires/quits ratio)
    z_quits = -(df['quits'] - df['quits'].mean()) / df['quits'].std()
    z_hq = -((df['hires']/df['quits']) - (df['hires']/df['quits']).mean()) / (df['hires']/df['quits']).std()
    z_urate = (df['urate'] - df['urate'].mean()) / df['urate'].std()

    lfi = (z_quits + z_hq + z_urate) / 3

    fig, ax = plt.subplots(figsize=(12, 7))

    # Main line
    ax.plot(lfi.index, lfi.values, linewidth=2, color=LHM_COLORS['ocean'])

    # Danger zone above 1.0
    ax.set_ylim(min(lfi.min() - 0.3, -1.5), max(lfi.max() + 0.3, 3.5))
    ax.axhspan(1.0, ax.get_ylim()[1], alpha=0.12, color=LHM_COLORS['down_red'], zorder=0)

    # Recession threshold
    ax.axhline(1.0, color=LHM_COLORS['down_red'], linestyle='--', linewidth=1.5)
    ax.text(0.02, 1.05, 'RECESSION THRESHOLD', transform=ax.get_yaxis_transform(),
            fontsize=9, color=LHM_COLORS['down_red'], fontweight='bold')

    # Recession bars
    add_recession_bars(ax, '2001-01-01')

    # Current
    current_val = lfi.iloc[-1]
    add_current_dot(ax, lfi.index[-1], current_val)
    add_now_box(ax, f'{current_val:.2f}σ')

    ax.set_ylabel('LFI (Z-Score)', fontweight='bold')
    ax.set_title('Labor Fragility Index', fontsize=13, fontweight='bold', pad=15)

    apply_lhm_style(ax)
    add_branding(fig)
    add_source(ax, 'BLS JOLTS')
    add_formula_box(ax, 'LFI = Avg[z(-Quits), z(-Hires/Quits), z(Unrate)]')

    plt.tight_layout()
    return fig


def chart_23_credit_labor_gap():
    """Credit-Labor Gap: Are Spreads Ignoring Labor?"""
    hy = get_db_data('hy_spread', '2001-01-01')
    quits = get_db_data('quits_rate', '2001-01-01')
    hires = get_db_data('hires_rate', '2001-01-01')
    urate = get_db_data('unemployment_rate', '2001-01-01')

    if hy.empty or quits.empty:
        return None

    # Calculate LFI
    df = pd.DataFrame({'hy': hy, 'quits': quits, 'hires': hires, 'urate': urate}).dropna()

    z_quits = -(df['quits'] - df['quits'].mean()) / df['quits'].std()
    z_hq = -((df['hires']/df['quits']) - (df['hires']/df['quits']).mean()) / (df['hires']/df['quits']).std()
    z_urate = (df['urate'] - df['urate'].mean()) / df['urate'].std()
    lfi = (z_quits + z_hq + z_urate) / 3

    # Z-score of HY
    z_hy = (df['hy'] - df['hy'].mean()) / df['hy'].std()

    # CLG = z(HY) - z(LFI)
    clg = z_hy - lfi

    fig, ax1 = plt.subplots(figsize=(12, 7))

    # CLG on left axis (primary)
    ax1.plot(clg.index, clg.values, linewidth=2, color=LHM_COLORS['ocean'], label='CLG')
    ax1.set_ylabel('CLG (Z-Score)', fontweight='bold', color=LHM_COLORS['ocean'])

    # HY OAS on right axis (secondary)
    ax2 = ax1.twinx()
    ax2.plot(df.index, df['hy'].values, linewidth=1.5, color=LHM_COLORS['dusk'], alpha=0.7, label='HY OAS')
    ax2.set_ylabel('HY OAS (bps)', fontweight='bold', color=LHM_COLORS['dusk'])

    # Danger zone where CLG < 0 (spreads too tight)
    ax1.set_ylim(min(clg.min() - 0.3, -2.5), max(clg.max() + 0.3, 2))
    ax1.axhspan(ax1.get_ylim()[0], 0, alpha=0.12, color=LHM_COLORS['down_red'], zorder=0)

    # Zero line and threshold
    ax1.axhline(0, color='black', linewidth=0.5)
    ax1.axhline(-0.5, color=LHM_COLORS['dusk'], linestyle='--', linewidth=1.5, alpha=0.7)

    # Current CLG
    current_clg = clg.iloc[-1]
    add_current_dot(ax1, clg.index[-1], current_clg)

    # NOW box
    props = dict(boxstyle='round,pad=0.4', facecolor='white',
                 edgecolor=LHM_COLORS['down_red'], linewidth=2, alpha=0.95)
    ax1.text(0.98, 0.85, f'CLG: {current_clg:.2f}σ\nCLG < 0 = Credit ignoring labor',
             transform=ax1.transAxes, fontsize=10, fontweight='bold',
             color=LHM_COLORS['down_red'],
             verticalalignment='top', horizontalalignment='right', bbox=props)

    ax1.set_title('Credit-Labor Gap: Are Spreads Ignoring Labor?', fontsize=13, fontweight='bold', pad=15)

    apply_lhm_style(ax1)
    ax2.spines['right'].set_visible(True)
    ax2.spines['right'].set_color('#CCCCCC')

    add_branding(fig)
    add_source(ax1, 'ICE BofA, BLS')

    plt.tight_layout()
    return fig


def chart_04_sofr_effr_spread():
    """SOFR-EFFR Spread: Funding Market Early Warning"""
    sofr = get_db_data('sofr', '2024-01-01')
    effr = get_db_data('effr', '2024-01-01')

    if sofr.empty or effr.empty:
        return None

    df = pd.DataFrame({'sofr': sofr, 'effr': effr}).dropna()
    spread = (df['sofr'] - df['effr']) * 100  # bps

    # 20-day MA
    spread_ma = spread.rolling(20).mean()

    fig, ax = plt.subplots(figsize=(12, 7))

    # Bar chart for daily spread (light blue)
    ax.bar(spread.index, spread.values, width=1, alpha=0.4, color=LHM_COLORS['ocean'])

    # 20D MA in hot pink
    ax.plot(spread_ma.index, spread_ma.values, linewidth=2.5, color=LHM_COLORS['hot'],
            label='20-Day Moving Avg')

    # Danger zone above 15 bps
    ax.set_ylim(spread.min() - 2, max(spread.max() + 2, 22))
    ax.axhspan(15, ax.get_ylim()[1], alpha=0.12, color=LHM_COLORS['down_red'], zorder=0)

    # Stress threshold
    ax.axhline(15, color=LHM_COLORS['dusk'], linestyle='--', linewidth=1.5)
    ax.text(0.02, 15.3, 'STRESS THRESHOLD (15 bps)', transform=ax.get_yaxis_transform(),
            fontsize=9, color=LHM_COLORS['dusk'], fontweight='bold')

    # Current values
    current_spread = spread.iloc[-1]
    current_ma = spread_ma.iloc[-1]

    # NOW box
    props = dict(boxstyle='round,pad=0.4', facecolor='white',
                 edgecolor=LHM_COLORS['down_red'], linewidth=2, alpha=0.95)
    ax.text(0.98, 0.95, f'Current: {current_spread:.0f} bps\n20D Avg: {current_ma:.0f} bps',
            transform=ax.transAxes, fontsize=10, fontweight='bold',
            color=LHM_COLORS['down_red'],
            verticalalignment='top', horizontalalignment='right', bbox=props)

    ax.set_ylabel('SOFR-EFFR Spread (Basis Points)', fontweight='bold')
    ax.set_title('SOFR-EFFR Spread: Funding Market Early Warning', fontsize=13, fontweight='bold', pad=15)

    ax.legend(loc='upper left', frameon=False)
    apply_lhm_style(ax)
    add_branding(fig)
    add_source(ax, 'Federal Reserve')

    plt.tight_layout()
    return fig


def chart_07_debt_trajectory():
    """Federal Debt Trajectory"""
    debt = get_db_data('federal_debt', '1970-01-01')
    gdp = get_db_data('gdp', '1970-01-01')

    if debt.empty or gdp.empty:
        return None

    # Align - debt is quarterly, gdp is quarterly
    df = pd.DataFrame({'debt': debt, 'gdp': gdp}).dropna()
    debt_gdp = (df['debt'] / df['gdp']) * 100

    fig, ax = plt.subplots(figsize=(12, 7))

    # Main line
    ax.plot(debt_gdp.index, debt_gdp.values, linewidth=2, color=LHM_COLORS['dusk'])

    # 100% threshold
    ax.axhline(100, color=LHM_COLORS['down_red'], linestyle='--', linewidth=2)
    ax.text(0.02, 101, '100% THRESHOLD', transform=ax.get_yaxis_transform(),
            fontsize=9, color=LHM_COLORS['down_red'], fontweight='bold')

    # Recession bars
    add_recession_bars(ax, '1970-01-01')

    # Current
    current_val = debt_gdp.iloc[-1]
    add_current_dot(ax, debt_gdp.index[-1], current_val)
    add_now_box(ax, f'{current_val:.0f}%')

    ax.set_ylabel('Federal Debt / GDP (%)', fontweight='bold')
    ax.set_title('Federal Debt Trajectory', fontsize=13, fontweight='bold', pad=15)

    apply_lhm_style(ax)
    add_branding(fig)
    add_source(ax, 'Treasury, BEA')

    plt.tight_layout()
    return fig


def chart_11_term_premium():
    """Term Premium (10Y)"""
    # Use 10Y-2Y spread as proxy for term premium
    y10 = get_db_data('treasury_10y', '2000-01-01')
    y2 = get_db_data('treasury_2y', '2000-01-01')

    if y10.empty or y2.empty:
        return None

    df = pd.DataFrame({'y10': y10, 'y2': y2}).dropna()
    spread = df['y10'] - df['y2']  # 10Y-2Y as term premium proxy

    fig, ax = plt.subplots(figsize=(12, 7))

    # Fill positive/negative differently
    ax.fill_between(spread.index, 0, spread.values,
                    where=spread.values >= 0, alpha=0.3, color=LHM_COLORS['up_green'])
    ax.fill_between(spread.index, 0, spread.values,
                    where=spread.values < 0, alpha=0.3, color=LHM_COLORS['down_red'])
    ax.plot(spread.index, spread.values, linewidth=1.5, color=LHM_COLORS['ocean'])

    ax.axhline(0, color='black', linewidth=0.5)

    # Target line for 2026
    ax.axhline(1.5, color=LHM_COLORS['dusk'], linestyle='--', linewidth=1.5)
    ax.text(0.98, 1.55, '~150 bps target (2026 thesis)', transform=ax.get_yaxis_transform(),
            fontsize=9, color=LHM_COLORS['dusk'], fontweight='bold', ha='right')

    # Recession bars
    add_recession_bars(ax, '2000-01-01')

    # Current
    current_val = spread.iloc[-1]
    add_current_dot(ax, spread.index[-1], current_val)
    add_now_box(ax, f'{current_val:.2f}%')

    ax.set_ylabel('10Y-2Y Spread (%)', fontweight='bold')
    ax.set_title('Term Premium Proxy: 10Y-2Y Spread', fontsize=13, fontweight='bold', pad=15)

    apply_lhm_style(ax)
    add_branding(fig)
    add_source(ax, 'Treasury')

    plt.tight_layout()
    return fig


def chart_08_interest_expense():
    """Interest Expense as % of Revenue"""
    interest = get_db_data('interest_payments', '1970-01-01')
    receipts = get_db_data('federal_receipts', '1970-01-01')

    if interest.empty or receipts.empty:
        return None

    df = pd.DataFrame({'interest': interest, 'receipts': receipts}).dropna()
    ratio = (df['interest'] / df['receipts']) * 100

    fig, ax = plt.subplots(figsize=(12, 7))

    ax.plot(ratio.index, ratio.values, linewidth=2, color=LHM_COLORS['dusk'])

    # Historical stress level
    ax.axhline(15, color=LHM_COLORS['down_red'], linestyle='--', linewidth=1.5)
    ax.text(0.02, 15.5, 'HISTORICAL STRESS (15%)', transform=ax.get_yaxis_transform(),
            fontsize=9, color=LHM_COLORS['down_red'], fontweight='bold')

    add_recession_bars(ax, '1970-01-01')

    current_val = ratio.iloc[-1]
    add_current_dot(ax, ratio.index[-1], current_val)
    add_now_box(ax, f'{current_val:.1f}%')

    ax.set_ylabel('Interest / Federal Receipts (%)', fontweight='bold')
    ax.set_title('Interest Expense: Crowding Out Fiscal Space', fontsize=13, fontweight='bold', pad=15)

    apply_lhm_style(ax)
    add_branding(fig)
    add_source(ax, 'Treasury')

    plt.tight_layout()
    return fig


def chart_21_credit_card():
    """Credit Card Delinquency"""
    cc = get_db_data('cc_delinquency', '2000-01-01')

    if cc.empty:
        return None

    fig, ax = plt.subplots(figsize=(12, 7))

    ax.plot(cc.index, cc.values, linewidth=2, color=LHM_COLORS['dusk'])

    # Mean line
    mean_val = cc.mean()
    ax.axhline(mean_val, color=LHM_COLORS['silvs'], linestyle='--', linewidth=1.5)
    ax.text(0.02, mean_val + 0.1, f'Mean: {mean_val:.1f}%', transform=ax.get_yaxis_transform(),
            fontsize=9, color=LHM_COLORS['silvs'])

    add_recession_bars(ax, '2000-01-01')

    current_val = cc.iloc[-1]
    add_current_dot(ax, cc.index[-1], current_val)
    add_now_box(ax, f'{current_val:.2f}%')

    ax.set_ylabel('Credit Card Delinquency Rate (%)', fontweight='bold')
    ax.set_title('Consumer Bifurcation: Credit Card Stress', fontsize=13, fontweight='bold', pad=15)

    apply_lhm_style(ax)
    add_branding(fig)
    add_source(ax, 'Federal Reserve')

    plt.tight_layout()
    return fig


# ============================================================================
# GENERATION
# ============================================================================

def generate_all_charts(output_dir: str = '.'):
    """Generate all HORIZON 2026 charts with correct LHM style."""
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    charts = [
        ('chart_01_rrp_drawdown', chart_01_rrp_drawdown),
        ('chart_02_liquidity_cushion_index', chart_02_liquidity_cushion_index),
        ('chart_04_sofr_effr_spread', chart_04_sofr_effr_spread),
        ('chart_07_debt_trajectory', chart_07_debt_trajectory),
        ('chart_08_interest_expense', chart_08_interest_expense),
        ('chart_11_term_premium', chart_11_term_premium),
        ('chart_16_labor_fragility_index', chart_16_labor_fragility_index),
        ('chart_21_credit_card_bifurcation', chart_21_credit_card),
        ('chart_23_credit_labor_gap', chart_23_credit_labor_gap),
    ]

    print("=" * 60)
    print("HORIZON 2026 - CHART GENERATION V2")
    print("Correct LHM Style | Left Y-Axis Primary")
    print("=" * 60)

    success = 0
    for name, func in charts:
        try:
            print(f"Generating {name}...", end=' ')
            fig = func()
            if fig is None:
                print("SKIPPED (no data)")
                continue
            filepath = f"{output_dir}/{name}.png"
            fig.savefig(filepath, dpi=300, bbox_inches='tight', facecolor='white')
            plt.close(fig)
            print("OK")
            success += 1
        except Exception as e:
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()

    print("=" * 60)
    print(f"Complete! {success}/{len(charts)} charts generated.")
    print(f"Output: {output_dir}")
    print("=" * 60)


if __name__ == "__main__":
    generate_all_charts()
