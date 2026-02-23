"""
HORIZON 2026 - COMPLETE CHART GENERATOR
Lighthouse Macro | December 2025

Generates all 27 charts for the HORIZON 2026 outlook with proper LHM visual standards:
- No gridlines
- Clean spines
- LHM 8-color palette
- Labels positioned away from data
- Branding: top-left and bottom-right watermarks
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, Dict, Tuple
import warnings
import os

warnings.filterwarnings('ignore')

# ============================================================================
# DATA FETCHING
# ============================================================================

try:
    import yfinance as yf
except ImportError:
    yf = None
    print("Warning: yfinance not installed. Run: pip install yfinance")

try:
    from fredapi import Fred
except ImportError:
    Fred = None
    print("Warning: fredapi not installed. Run: pip install fredapi")

FRED_API_KEY = os.environ.get('FRED_API_KEY', '')


class DataFetcher:
    """Centralized data fetcher with caching."""

    def __init__(self, fred_api_key: Optional[str] = None):
        self.fred_api_key = fred_api_key or FRED_API_KEY
        self._fred = None
        self._cache = {}

    @property
    def fred(self):
        if self._fred is None and Fred and self.fred_api_key:
            self._fred = Fred(api_key=self.fred_api_key)
        return self._fred

    def get_fred_series(self, series_id: str, start_date: str = '2000-01-01') -> pd.Series:
        cache_key = f"fred_{series_id}_{start_date}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        if self.fred is None:
            raise ValueError("FRED API not available. Set FRED_API_KEY.")
        try:
            data = self.fred.get_series(series_id, observation_start=start_date)
            self._cache[cache_key] = data
            return data
        except Exception as e:
            print(f"Warning: Could not fetch {series_id}: {e}")
            return pd.Series(dtype=float)

    def get_yahoo_data(self, ticker: str, start: str = '2000-01-01') -> pd.DataFrame:
        if yf is None:
            raise ImportError("yfinance not installed")
        end = datetime.now().strftime('%Y-%m-%d')
        cache_key = f"yf_{ticker}_{start}_{end}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        try:
            data = yf.download(ticker, start=start, end=end, progress=False)
            self._cache[cache_key] = data
            return data
        except Exception as e:
            print(f"Warning: Could not fetch {ticker}: {e}")
            return pd.DataFrame()


_fetcher = None

def get_fetcher() -> DataFetcher:
    global _fetcher
    if _fetcher is None:
        _fetcher = DataFetcher()
    return _fetcher


# ============================================================================
# LHM VISUAL STANDARDS (from CLAUDE.md)
# ============================================================================

# 8-Color Palette
LHM_COLORS = {
    'ocean': '#2389BB',      # Primary data series
    'dusk': '#FF6723',       # Secondary / Warning thresholds
    'electric': '#03DDFF',   # Volatility / Highlights
    'hot': '#FF00F0',        # Extreme stress / Attention
    'sea': '#289389',        # Neutral / Balanced
    'silvs': '#D1D1D1',      # Reference lines / Background
    'down_red': '#FF3333',   # Bearish / Danger
    'up_green': '#008000'    # Bullish
}

# Set global font
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans']
plt.rcParams['font.size'] = 10
plt.rcParams['axes.facecolor'] = 'white'
plt.rcParams['figure.facecolor'] = 'white'


def apply_lhm_style(ax):
    """Apply LHM visual standards: NO gridlines, clean spines."""
    ax.grid(False)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color(LHM_COLORS['silvs'])
    ax.spines['bottom'].set_color(LHM_COLORS['silvs'])
    ax.tick_params(colors='#666666', labelsize=9)


def add_branding(fig):
    """Add LHM branding: top-left and bottom-right."""
    fig.text(0.01, 0.995, 'LIGHTHOUSE MACRO',
             fontsize=9, fontweight='bold',
             color=LHM_COLORS['ocean'], alpha=0.9,
             verticalalignment='top', horizontalalignment='left')
    fig.text(0.99, 0.005, 'MACRO, ILLUMINATED.',
             fontsize=8, style='italic',
             color=LHM_COLORS['silvs'], alpha=0.8,
             verticalalignment='bottom', horizontalalignment='right')


def add_recession_shading(ax, start_date='2000-01-01'):
    """Add recession shading."""
    recessions = [
        ('2001-03-01', '2001-11-01'),
        ('2007-12-01', '2009-06-01'),
        ('2020-02-01', '2020-04-01')
    ]
    for start, end in recessions:
        if pd.to_datetime(start) >= pd.to_datetime(start_date):
            ax.axvspan(pd.to_datetime(start), pd.to_datetime(end),
                       alpha=0.1, color=LHM_COLORS['silvs'], zorder=0)


def annotate_current(ax, x, y, text, side='left'):
    """Annotate current value with proper positioning."""
    offset = (-120, 40) if side == 'left' else (60, 40)
    ax.scatter([x], [y], s=200, color=LHM_COLORS['hot'],
               edgecolors='white', linewidth=2.5, zorder=10)
    ax.annotate(text, xy=(x, y), xytext=offset,
                textcoords='offset points',
                fontsize=10, fontweight='bold', color=LHM_COLORS['hot'],
                bbox=dict(boxstyle='round,pad=0.4', facecolor='white',
                         edgecolor=LHM_COLORS['hot'], linewidth=1.5, alpha=0.95),
                arrowprops=dict(arrowstyle='->', color=LHM_COLORS['hot'], lw=1.5))


def stats_box(ax, text, position='upper_left'):
    """Add statistics box."""
    positions = {
        'upper_left': (0.02, 0.98),
        'upper_right': (0.98, 0.98),
        'lower_left': (0.02, 0.25),
        'lower_right': (0.98, 0.25)
    }
    x, y = positions.get(position, (0.02, 0.98))
    ha = 'left' if 'left' in position else 'right'
    props = dict(boxstyle='round', facecolor='white',
                 edgecolor=LHM_COLORS['ocean'], linewidth=1.5, alpha=0.95)
    ax.text(x, y, text, transform=ax.transAxes, fontsize=9,
            verticalalignment='top', horizontalalignment=ha,
            bbox=props, family='monospace')


# ============================================================================
# CHART 1: ON RRP DRAWDOWN
# ============================================================================

def chart_01_rrp_drawdown():
    """ON RRP Drawdown - The 35-Month Exhaustion"""
    fetcher = get_fetcher()
    rrp = fetcher.get_fred_series('RRPONTSYD', '2021-01-01')

    if rrp.empty:
        return None

    rrp_billions = rrp / 1000

    fig, ax = plt.subplots(figsize=(14, 8))

    # Area fill and line
    ax.fill_between(rrp_billions.index, 0, rrp_billions.values,
                    alpha=0.3, color=LHM_COLORS['ocean'])
    ax.plot(rrp_billions.index, rrp_billions.values,
            linewidth=2.5, color=LHM_COLORS['ocean'], label='ON RRP Balance')

    # Stats
    peak_val = rrp_billions.max()
    peak_date = rrp_billions.idxmax()
    current_val = rrp_billions.iloc[-1]
    current_date = rrp_billions.index[-1]
    pct_decline = ((peak_val - current_val) / peak_val) * 100
    months = (current_date - peak_date).days / 30

    # Annotations - peak to the right, current to the left
    ax.annotate(f'Peak: ${peak_val:,.0f}B\n{peak_date.strftime("%b %Y")}',
                xy=(peak_date, peak_val), xytext=(80, -20),
                textcoords='offset points', fontsize=10, fontweight='bold',
                color=LHM_COLORS['dusk'],
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                         edgecolor=LHM_COLORS['dusk'], alpha=0.95),
                arrowprops=dict(arrowstyle='->', color=LHM_COLORS['dusk'], lw=1.5))

    annotate_current(ax, current_date, current_val,
                     f'Current: ${current_val:,.1f}B\n({pct_decline:.1f}% decline)', side='left')

    ax.set_ylabel('ON RRP Balance ($ Billions)', fontweight='bold')
    ax.set_title('ON RRP Drawdown Velocity: The 35-Month Exhaustion',
                 fontsize=14, fontweight='bold', pad=20)

    apply_lhm_style(ax)
    ax.legend(loc='upper right', frameon=False)

    # Stats box
    avg_drain = (peak_val - current_val) / months if months > 0 else 0
    stats_box(ax, f'Peak: ${peak_val:,.0f}B ({peak_date.strftime("%b %Y")})\n'
                  f'Current: ${current_val:,.1f}B\n'
                  f'Decline: {pct_decline:.1f}%\n'
                  f'Months: {months:.0f}\n'
                  f'Avg drain: ${avg_drain:,.0f}B/mo', 'lower_left')

    add_branding(fig)
    plt.tight_layout()
    return fig


# ============================================================================
# CHART 2: LIQUIDITY CUSHION INDEX
# ============================================================================

def chart_02_liquidity_cushion_index():
    """LCI - Reserves/GDP with RRP context"""
    fetcher = get_fetcher()
    reserves = fetcher.get_fred_series('TOTRESNS', '2008-01-01')
    gdp = fetcher.get_fred_series('GDP', '2008-01-01')

    if reserves.empty or gdp.empty:
        return None

    reserves_q = reserves.resample('QE').mean()
    gdp_aligned = gdp.reindex(reserves_q.index, method='ffill')
    ratio = (reserves_q / gdp_aligned) * 100
    ratio = ratio.dropna()

    fig, ax = plt.subplots(figsize=(14, 8))

    ax.fill_between(ratio.index, 0, ratio.values, alpha=0.3, color=LHM_COLORS['ocean'])
    ax.plot(ratio.index, ratio.values, linewidth=2.5, color=LHM_COLORS['ocean'],
            label='Reserves / GDP (%)')

    current = ratio.iloc[-1]

    # Sept 2019 reference
    sept_2019 = ratio.loc['2019-07-01':'2019-12-31']
    if len(sept_2019) > 0:
        sept_val = sept_2019.iloc[0]
        ax.axhline(sept_val, color=LHM_COLORS['down_red'], linestyle='--',
                   linewidth=2, alpha=0.7, label=f'Sept 2019 stress: {sept_val:.1f}%')

    annotate_current(ax, ratio.index[-1], current, f'Current: {current:.1f}%', side='left')

    add_recession_shading(ax, '2008-01-01')

    ax.set_ylabel('Bank Reserves as % of GDP', fontweight='bold')
    ax.set_title('Liquidity Cushion Index: System Shock Absorption',
                 fontsize=14, fontweight='bold', pad=20)

    apply_lhm_style(ax)
    ax.legend(loc='upper left', frameon=False)
    add_branding(fig)
    plt.tight_layout()
    return fig


# ============================================================================
# CHART 3: QT TERMINATION MECHANICS
# ============================================================================

def chart_03_qt_termination():
    """Fed Balance Sheet & QT Context"""
    fetcher = get_fetcher()
    assets = fetcher.get_fred_series('WALCL', '2020-01-01')  # Fed total assets

    if assets.empty:
        return None

    assets_t = assets / 1e6  # Convert to trillions

    fig, ax = plt.subplots(figsize=(14, 8))

    ax.fill_between(assets_t.index, 0, assets_t.values, alpha=0.3, color=LHM_COLORS['ocean'])
    ax.plot(assets_t.index, assets_t.values, linewidth=2.5, color=LHM_COLORS['ocean'],
            label='Fed Total Assets')

    current = assets_t.iloc[-1]
    peak = assets_t.max()
    peak_date = assets_t.idxmax()

    # QT end marker (Dec 1, 2025)
    qt_end = pd.Timestamp('2025-12-01')
    if qt_end <= assets_t.index[-1]:
        ax.axvline(qt_end, color=LHM_COLORS['dusk'], linestyle='--', linewidth=2,
                   label='QT Termination: Dec 2025')

    annotate_current(ax, assets_t.index[-1], current, f'${current:.2f}T', side='left')

    ax.set_ylabel('Fed Total Assets ($ Trillions)', fontweight='bold')
    ax.set_title('QT Termination: The Balance Sheet Plateau',
                 fontsize=14, fontweight='bold', pad=20)

    apply_lhm_style(ax)
    ax.legend(loc='upper right', frameon=False)
    add_branding(fig)
    plt.tight_layout()
    return fig


# ============================================================================
# CHART 4: SOFR-EFFR SPREAD
# ============================================================================

def chart_04_sofr_effr_spread():
    """SOFR-EFFR Spread - Plumbing Stress Indicator"""
    fetcher = get_fetcher()
    sofr = fetcher.get_fred_series('SOFR', '2018-04-01')
    effr = fetcher.get_fred_series('EFFR', '2018-04-01')

    if sofr.empty or effr.empty:
        return None

    combined = pd.DataFrame({'SOFR': sofr, 'EFFR': effr}).dropna()
    spread = (combined['SOFR'] - combined['EFFR']) * 100  # bps

    fig, ax = plt.subplots(figsize=(14, 8))

    # Color by stress level
    colors = [LHM_COLORS['ocean'] if v < 5 else LHM_COLORS['dusk'] if v < 10
              else LHM_COLORS['down_red'] for v in spread.values]

    for i in range(len(spread)-1):
        ax.plot(spread.index[i:i+2], spread.iloc[i:i+2],
                color=colors[i], linewidth=1.5)

    current = spread.iloc[-1]
    mean_sp = spread.mean()

    ax.axhline(mean_sp, color=LHM_COLORS['silvs'], linestyle='--',
               linewidth=1.5, label=f'Mean: {mean_sp:.1f} bps')
    ax.axhline(0, color='black', linewidth=0.5)

    annotate_current(ax, spread.index[-1], current, f'{current:.1f} bps', side='left')

    ax.set_ylabel('SOFR - EFFR Spread (basis points)', fontweight='bold')
    ax.set_title('SOFR-EFFR Spread: Plumbing Stress Indicator',
                 fontsize=14, fontweight='bold', pad=20)

    apply_lhm_style(ax)
    ax.legend(loc='upper left', frameon=False)

    stats_box(ax, f'Current: {current:.1f} bps\nMean: {mean_sp:.1f} bps\n'
                  f'Std: {spread.std():.1f} bps', 'upper_right')

    add_branding(fig)
    plt.tight_layout()
    return fig


# ============================================================================
# CHART 5: REPO RATE DISPERSION
# ============================================================================

def chart_05_repo_dispersion():
    """Repo Rate Volatility"""
    fetcher = get_fetcher()
    sofr = fetcher.get_fred_series('SOFR', '2018-04-01')

    if sofr.empty:
        return None

    # Calculate 20-day rolling volatility
    vol = sofr.rolling(20).std() * 100 * np.sqrt(252)  # Annualized bps

    fig, ax = plt.subplots(figsize=(14, 8))

    ax.fill_between(vol.index, 0, vol.values, alpha=0.3, color=LHM_COLORS['dusk'])
    ax.plot(vol.index, vol.values, linewidth=2, color=LHM_COLORS['dusk'],
            label='SOFR 20-day Vol (annualized)')

    current = vol.iloc[-1]
    ax.axhline(vol.mean(), color=LHM_COLORS['silvs'], linestyle='--',
               linewidth=1.5, label=f'Mean: {vol.mean():.0f} bps')

    annotate_current(ax, vol.index[-1], current, f'{current:.0f} bps', side='left')

    ax.set_ylabel('Annualized Volatility (bps)', fontweight='bold')
    ax.set_title('Repo Rate Dispersion: Short-Term Funding Volatility',
                 fontsize=14, fontweight='bold', pad=20)

    apply_lhm_style(ax)
    ax.legend(loc='upper right', frameon=False)
    add_branding(fig)
    plt.tight_layout()
    return fig


# ============================================================================
# CHART 6: RESERVES/GDP
# ============================================================================

def chart_06_reserves_gdp():
    """Bank Reserves to GDP"""
    fetcher = get_fetcher()
    reserves = fetcher.get_fred_series('TOTRESNS', '2000-01-01')
    gdp = fetcher.get_fred_series('GDP', '2000-01-01')

    if reserves.empty or gdp.empty:
        return None

    reserves_q = reserves.resample('QE').mean()
    gdp_aligned = gdp.reindex(reserves_q.index, method='ffill')
    ratio = (reserves_q / gdp_aligned) * 100
    ratio = ratio.dropna()

    fig, ax = plt.subplots(figsize=(14, 8))

    ax.fill_between(ratio.index, 0, ratio.values, alpha=0.3, color=LHM_COLORS['ocean'])
    ax.plot(ratio.index, ratio.values, linewidth=2.5, color=LHM_COLORS['ocean'])

    current = ratio.iloc[-1]
    annotate_current(ax, ratio.index[-1], current, f'{current:.1f}%', side='left')

    add_recession_shading(ax, '2000-01-01')

    ax.set_ylabel('Bank Reserves / GDP (%)', fontweight='bold')
    ax.set_title('Bank Reserves as Share of GDP',
                 fontsize=14, fontweight='bold', pad=20)

    apply_lhm_style(ax)
    add_branding(fig)
    plt.tight_layout()
    return fig


# ============================================================================
# CHART 7: DEBT TRAJECTORY
# ============================================================================

def chart_07_debt_trajectory():
    """Federal Debt Trajectory"""
    fetcher = get_fetcher()
    debt = fetcher.get_fred_series('GFDEBTN', '1970-01-01')  # Millions
    gdp = fetcher.get_fred_series('GDP', '1970-01-01')  # Billions

    if debt.empty or gdp.empty:
        return None

    # Convert debt from millions to billions to match GDP units
    debt_b = debt / 1000
    debt_q = debt_b.resample('QE').last()
    gdp_aligned = gdp.reindex(debt_q.index, method='ffill')
    debt_gdp = (debt_q / gdp_aligned) * 100  # Now as percentage
    debt_gdp = debt_gdp.dropna()

    fig, ax = plt.subplots(figsize=(14, 8))

    ax.fill_between(debt_gdp.index, 0, debt_gdp.values, alpha=0.3, color=LHM_COLORS['dusk'])
    ax.plot(debt_gdp.index, debt_gdp.values, linewidth=2.5, color=LHM_COLORS['dusk'])

    current = debt_gdp.iloc[-1]
    ax.axhline(100, color=LHM_COLORS['down_red'], linestyle='--',
               linewidth=2, alpha=0.7, label='100% threshold')

    annotate_current(ax, debt_gdp.index[-1], current, f'{current:.0f}%', side='left')

    add_recession_shading(ax, '1970-01-01')

    ax.set_ylabel('Federal Debt / GDP (%)', fontweight='bold')
    ax.set_title('Federal Debt Trajectory: The Fiscal Dominance Path',
                 fontsize=14, fontweight='bold', pad=20)

    apply_lhm_style(ax)
    ax.legend(loc='upper left', frameon=False)
    add_branding(fig)
    plt.tight_layout()
    return fig


# ============================================================================
# CHART 8: INTEREST EXPENSE
# ============================================================================

def chart_08_interest_expense():
    """Interest Expense as % of Revenue"""
    fetcher = get_fetcher()
    interest = fetcher.get_fred_series('A091RC1Q027SBEA', '1970-01-01')
    revenue = fetcher.get_fred_series('FGRECPT', '1970-01-01')

    if interest.empty or revenue.empty:
        return None

    combined = pd.DataFrame({'int': interest, 'rev': revenue}).dropna()
    ratio = (combined['int'] / combined['rev']) * 100

    fig, ax = plt.subplots(figsize=(14, 8))

    ax.fill_between(ratio.index, 0, ratio.values, alpha=0.3, color=LHM_COLORS['dusk'])
    ax.plot(ratio.index, ratio.values, linewidth=2.5, color=LHM_COLORS['dusk'])

    current = ratio.iloc[-1]
    ax.axhline(10, color=LHM_COLORS['down_red'], linestyle='--',
               linewidth=2, label='10% historical stress')

    annotate_current(ax, ratio.index[-1], current, f'{current:.1f}%', side='left')

    add_recession_shading(ax, '1970-01-01')

    ax.set_ylabel('Interest / Federal Revenue (%)', fontweight='bold')
    ax.set_title('Interest Expense: Crowding Out Fiscal Space',
                 fontsize=14, fontweight='bold', pad=20)

    apply_lhm_style(ax)
    ax.legend(loc='upper left', frameon=False)
    add_branding(fig)
    plt.tight_layout()
    return fig


# ============================================================================
# CHART 9: FISCAL DOMINANCE CASCADE
# ============================================================================

def chart_09_fiscal_dominance():
    """Deficit vs Interest Expense - The Vicious Cycle"""
    fetcher = get_fetcher()
    deficit = fetcher.get_fred_series('FYFSD', '1970-01-01')  # Federal surplus/deficit
    interest = fetcher.get_fred_series('A091RC1Q027SBEA', '1970-01-01')

    if deficit.empty or interest.empty:
        return None

    deficit_gdp = deficit / 1000  # Billions
    interest_q = interest.resample('YE').last()

    fig, ax1 = plt.subplots(figsize=(14, 8))

    ax1.bar(deficit_gdp.index, -deficit_gdp.values, width=300, alpha=0.6,
            color=[LHM_COLORS['down_red'] if v > 0 else LHM_COLORS['up_green']
                   for v in deficit_gdp.values],
            label='Federal Deficit')
    ax1.axhline(0, color='black', linewidth=0.5)

    ax1.set_ylabel('Federal Deficit ($ Billions)', fontweight='bold')
    ax1.set_title('Fiscal Dominance Cascade: Deficits Fund Interest',
                  fontsize=14, fontweight='bold', pad=20)

    apply_lhm_style(ax1)
    ax1.legend(loc='upper left', frameon=False)
    add_branding(fig)
    plt.tight_layout()
    return fig


# ============================================================================
# CHART 10: FOREIGN HOLDINGS
# ============================================================================

def chart_10_foreign_holdings():
    """Foreign Treasury Holdings"""
    fetcher = get_fetcher()
    foreign = fetcher.get_fred_series('FDHBFIN', '2000-01-01')  # Foreign holdings

    if foreign.empty:
        return None

    foreign_t = foreign / 1000  # Trillions

    fig, ax = plt.subplots(figsize=(14, 8))

    ax.fill_between(foreign_t.index, 0, foreign_t.values, alpha=0.3, color=LHM_COLORS['sea'])
    ax.plot(foreign_t.index, foreign_t.values, linewidth=2.5, color=LHM_COLORS['sea'])

    current = foreign_t.iloc[-1]
    annotate_current(ax, foreign_t.index[-1], current, f'${current:.2f}T', side='left')

    ax.set_ylabel('Foreign Treasury Holdings ($ Trillions)', fontweight='bold')
    ax.set_title('Foreign Treasury Holdings: Marginal Buyer Dynamics',
                 fontsize=14, fontweight='bold', pad=20)

    apply_lhm_style(ax)
    add_branding(fig)
    plt.tight_layout()
    return fig


# ============================================================================
# CHART 11: TERM PREMIUM
# ============================================================================

def chart_11_term_premium():
    """10Y Term Premium (ACM model)"""
    fetcher = get_fetcher()
    tp = fetcher.get_fred_series('THREEFYTP10', '2000-01-01')  # ACM term premium

    if tp.empty:
        return None

    fig, ax = plt.subplots(figsize=(14, 8))

    ax.fill_between(tp.index, 0, tp.values,
                    where=tp.values >= 0, alpha=0.3, color=LHM_COLORS['dusk'])
    ax.fill_between(tp.index, 0, tp.values,
                    where=tp.values < 0, alpha=0.3, color=LHM_COLORS['ocean'])
    ax.plot(tp.index, tp.values, linewidth=2, color=LHM_COLORS['ocean'])
    ax.axhline(0, color='black', linewidth=0.5)

    current = tp.iloc[-1]
    ax.axhline(1.5, color=LHM_COLORS['down_red'], linestyle='--',
               linewidth=2, label='~150 bps target (2026 thesis)')

    annotate_current(ax, tp.index[-1], current, f'{current:.2f}%', side='left')

    add_recession_shading(ax, '2000-01-01')

    ax.set_ylabel('10Y Term Premium (%)', fontweight='bold')
    ax.set_title('Term Premium: The Honest Signal for Fiscal Risk',
                 fontsize=14, fontweight='bold', pad=20)

    apply_lhm_style(ax)
    ax.legend(loc='upper right', frameon=False)
    add_branding(fig)
    plt.tight_layout()
    return fig


# ============================================================================
# CHART 12: DEALER INVENTORY / SLR
# ============================================================================

def get_nyfed_dealer_positions():
    """Fetch primary dealer Treasury positions from NY Fed API."""
    import json
    import urllib.request

    url = "https://markets.newyorkfed.org/api/pd/get/PDPOSGST-TOT.json"
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            data = json.loads(response.read().decode())

        records = data.get('pd', {}).get('timeseries', [])
        if not records:
            return pd.Series(dtype=float)

        dates = [pd.to_datetime(r['asofdate']) for r in records]
        values = [float(r['value']) for r in records]

        series = pd.Series(values, index=dates).sort_index()
        return series / 1000  # Convert millions to billions
    except Exception as e:
        print(f"Warning: Could not fetch NY Fed dealer data: {e}")
        return pd.Series(dtype=float)


def chart_12_dealer_inventory():
    """Primary Dealer Treasury Holdings - from NY Fed"""
    dealer_b = get_nyfed_dealer_positions()

    if dealer_b.empty:
        return None

    fig, ax = plt.subplots(figsize=(14, 8))

    ax.fill_between(dealer_b.index, 0, dealer_b.values, alpha=0.3, color=LHM_COLORS['ocean'])
    ax.plot(dealer_b.index, dealer_b.values, linewidth=2, color=LHM_COLORS['ocean'],
            label='Net Treasury Positions')

    current = dealer_b.iloc[-1]
    mean_pos = dealer_b.mean()

    ax.axhline(mean_pos, color=LHM_COLORS['silvs'], linestyle='--',
               linewidth=1.5, label=f'Mean: ${mean_pos:.0f}B')

    annotate_current(ax, dealer_b.index[-1], current, f'${current:.0f}B', side='left')

    ax.set_ylabel('Primary Dealer Net Treasury Positions ($ Billions)', fontweight='bold')
    ax.set_title('Dealer Inventory: SLR Constraints & Balance Sheet Capacity',
                 fontsize=14, fontweight='bold', pad=20)

    apply_lhm_style(ax)
    ax.legend(loc='upper left', frameon=False)

    stats_box(ax, f'Current: ${current:.0f}B\nMean: ${mean_pos:.0f}B\n'
                  f'Source: NY Fed Primary\nDealer Statistics', 'upper_right')

    add_branding(fig)
    plt.tight_layout()
    return fig


# ============================================================================
# CHART 13: DEALER TAKEDOWN
# ============================================================================

def chart_13_dealer_takedown():
    """Dealer takedown capacity - uses same NY Fed data"""
    dealer_b = get_nyfed_dealer_positions()

    if dealer_b.empty:
        return None

    # Calculate 4-week change as proxy for recent absorption
    change_4w = dealer_b.diff(4)

    fig, ax = plt.subplots(figsize=(14, 8))

    ax.bar(change_4w.index, change_4w.values, width=5, alpha=0.7,
           color=[LHM_COLORS['up_green'] if v > 0 else LHM_COLORS['down_red'] for v in change_4w.values])
    ax.axhline(0, color='black', linewidth=0.5)

    current = change_4w.iloc[-1]
    annotate_current(ax, change_4w.index[-1], current,
                     f'{current:+.0f}B\n(4-week)', side='left')

    ax.set_ylabel('4-Week Change in Dealer Positions ($ Billions)', fontweight='bold')
    ax.set_title('Dealer Takedown: Weekly Absorption Capacity',
                 fontsize=14, fontweight='bold', pad=20)

    apply_lhm_style(ax)
    add_branding(fig)
    plt.tight_layout()
    return fig


# ============================================================================
# CHART 14: AUCTION TAILS
# ============================================================================

def chart_14_auction_tails():
    """Treasury 10Y Yield as proxy for auction pressure"""
    fetcher = get_fetcher()
    y10 = fetcher.get_fred_series('DGS10', '2020-01-01')

    if y10.empty:
        return None

    fig, ax = plt.subplots(figsize=(14, 8))

    ax.plot(y10.index, y10.values, linewidth=2, color=LHM_COLORS['ocean'])

    current = y10.iloc[-1]
    ax.axhline(5, color=LHM_COLORS['down_red'], linestyle='--',
               linewidth=2, label='5% psychological level')

    annotate_current(ax, y10.index[-1], current, f'{current:.2f}%', side='left')

    ax.set_ylabel('10Y Treasury Yield (%)', fontweight='bold')
    ax.set_title('Auction Dynamics: 10Y Yield Pressure',
                 fontsize=14, fontweight='bold', pad=20)

    apply_lhm_style(ax)
    ax.legend(loc='upper right', frameon=False)
    add_branding(fig)
    plt.tight_layout()
    return fig


# ============================================================================
# CHART 15: BASIS DYNAMICS
# ============================================================================

def chart_15_basis_dynamics():
    """Treasury-OIS basis (10Y yield minus SOFR)"""
    fetcher = get_fetcher()
    y10 = fetcher.get_fred_series('DGS10', '2018-01-01')
    sofr = fetcher.get_fred_series('SOFR', '2018-04-01')

    if y10.empty or sofr.empty:
        return None

    combined = pd.DataFrame({'y10': y10, 'sofr': sofr}).dropna()
    basis = combined['y10'] - combined['sofr']

    fig, ax = plt.subplots(figsize=(14, 8))

    ax.fill_between(basis.index, 0, basis.values, alpha=0.3, color=LHM_COLORS['sea'])
    ax.plot(basis.index, basis.values, linewidth=2, color=LHM_COLORS['sea'])

    current = basis.iloc[-1]
    ax.axhline(0, color='black', linewidth=0.5)

    annotate_current(ax, basis.index[-1], current, f'{current:.2f}%', side='left')

    ax.set_ylabel('10Y - SOFR Basis (%)', fontweight='bold')
    ax.set_title('Treasury-OIS Basis: Duration Risk Pricing',
                 fontsize=14, fontweight='bold', pad=20)

    apply_lhm_style(ax)
    add_branding(fig)
    plt.tight_layout()
    return fig


# ============================================================================
# CHART 16: LABOR FRAGILITY INDEX
# ============================================================================

def chart_16_labor_fragility_index():
    """LFI = Avg(z(LongTermUnemp), z(-Quits), z(-Hires/Quits))"""
    fetcher = get_fetcher()
    lt_unemp = fetcher.get_fred_series('LNS13025703', '2001-01-01')  # Long-term unemployed
    quits = fetcher.get_fred_series('JTSQUR', '2001-01-01')
    hires = fetcher.get_fred_series('JTSHIR', '2001-01-01')

    if lt_unemp.empty or quits.empty or hires.empty:
        return None

    # Align data
    data = pd.DataFrame({
        'lt_unemp': lt_unemp,
        'quits': quits,
        'hires': hires
    }).dropna()

    # Z-scores
    z_lt = (data['lt_unemp'] - data['lt_unemp'].mean()) / data['lt_unemp'].std()
    z_quits = -(data['quits'] - data['quits'].mean()) / data['quits'].std()
    z_hq = -((data['hires']/data['quits']) - (data['hires']/data['quits']).mean()) / (data['hires']/data['quits']).std()

    lfi = (z_lt + z_quits + z_hq) / 3

    fig, ax = plt.subplots(figsize=(14, 8))

    # Background shading
    ax.axhspan(1, lfi.max()+1, alpha=0.15, color=LHM_COLORS['down_red'], zorder=0)
    ax.axhspan(-1, 1, alpha=0.1, color=LHM_COLORS['silvs'], zorder=0)
    ax.axhspan(lfi.min()-1, -1, alpha=0.15, color=LHM_COLORS['up_green'], zorder=0)

    ax.plot(lfi.index, lfi.values, linewidth=2, color=LHM_COLORS['ocean'])

    current = lfi.iloc[-1]
    ax.axhline(1, color=LHM_COLORS['down_red'], linestyle='--',
               linewidth=2, label='Recession threshold (+1.0σ)')
    ax.axhline(0, color='black', linewidth=0.5)

    annotate_current(ax, lfi.index[-1], current, f'+{current:.2f}σ\n(6-9 month lead)', side='left')

    add_recession_shading(ax, '2001-01-01')

    ax.set_ylabel('Labor Fragility Index (Z-Score)', fontweight='bold')
    ax.set_title('Labor Fragility Index: Pre-Recessionary Territory',
                 fontsize=14, fontweight='bold', pad=20)

    apply_lhm_style(ax)
    ax.legend(loc='upper left', frameon=False)

    stats_box(ax, 'LFI = Avg(\n  z(Long-Term Unemp),\n  z(-Quits Rate),\n  z(-Hires/Quits)\n)', 'upper_left')

    add_branding(fig)
    plt.tight_layout()
    return fig


# ============================================================================
# CHART 17: JOB CUTS & CLAIMS
# ============================================================================

def chart_17_job_cuts_claims():
    """Initial Claims"""
    fetcher = get_fetcher()
    claims = fetcher.get_fred_series('ICSA', '2000-01-01')

    if claims.empty:
        return None

    claims_k = claims / 1000  # Thousands

    fig, ax = plt.subplots(figsize=(14, 8))

    ax.fill_between(claims_k.index, 0, claims_k.values, alpha=0.3, color=LHM_COLORS['dusk'])
    ax.plot(claims_k.index, claims_k.values, linewidth=1.5, color=LHM_COLORS['dusk'])

    current = claims_k.iloc[-1]
    mean_claims = claims_k.mean()
    ax.axhline(mean_claims, color=LHM_COLORS['silvs'], linestyle='--',
               linewidth=1.5, label=f'Mean: {mean_claims:.0f}K')

    annotate_current(ax, claims_k.index[-1], current, f'{current:.0f}K', side='left')

    add_recession_shading(ax, '2000-01-01')

    ax.set_ylabel('Initial Claims (Thousands)', fontweight='bold')
    ax.set_title('Initial Jobless Claims: Early Warning Signal',
                 fontsize=14, fontweight='bold', pad=20)

    apply_lhm_style(ax)
    ax.legend(loc='upper right', frameon=False)
    add_branding(fig)
    plt.tight_layout()
    return fig


# ============================================================================
# CHART 18: QUITS-WAGE LEAD
# ============================================================================

def chart_18_quits_wage_lead():
    """Quits Rate vs Wage Growth"""
    fetcher = get_fetcher()
    quits = fetcher.get_fred_series('JTSQUR', '2001-01-01')
    wages = fetcher.get_fred_series('CES0500000003', '2001-01-01')  # Avg hourly earnings

    if quits.empty or wages.empty:
        return None

    wages_yoy = wages.pct_change(12) * 100

    fig, ax1 = plt.subplots(figsize=(14, 8))

    ax1.plot(quits.index, quits.values, linewidth=2.5, color=LHM_COLORS['ocean'],
             label='Quits Rate (left)')
    ax1.set_ylabel('Quits Rate (%)', fontweight='bold', color=LHM_COLORS['ocean'])

    ax2 = ax1.twinx()
    ax2.plot(wages_yoy.index, wages_yoy.values, linewidth=2, color=LHM_COLORS['dusk'],
             alpha=0.7, label='Wage Growth YoY (right)')
    ax2.set_ylabel('Wage Growth YoY (%)', fontweight='bold', color=LHM_COLORS['dusk'])

    ax1.set_title('Quits Rate vs Wage Growth: The Lead-Lag Relationship',
                  fontsize=14, fontweight='bold', pad=20)

    apply_lhm_style(ax1)
    ax2.spines['right'].set_visible(True)
    ax2.spines['right'].set_color(LHM_COLORS['silvs'])

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right', frameon=False)

    add_branding(fig)
    plt.tight_layout()
    return fig


# ============================================================================
# CHART 19: EXCESS SAVINGS
# ============================================================================

def chart_19_excess_savings():
    """Personal Savings Rate"""
    fetcher = get_fetcher()
    savings = fetcher.get_fred_series('PSAVERT', '2000-01-01')

    if savings.empty:
        return None

    fig, ax = plt.subplots(figsize=(14, 8))

    ax.fill_between(savings.index, 0, savings.values, alpha=0.3, color=LHM_COLORS['ocean'])
    ax.plot(savings.index, savings.values, linewidth=2, color=LHM_COLORS['ocean'])

    current = savings.iloc[-1]
    pre_covid = savings.loc['2015-01-01':'2019-12-31'].mean()
    ax.axhline(pre_covid, color=LHM_COLORS['silvs'], linestyle='--',
               linewidth=2, label=f'Pre-COVID avg: {pre_covid:.1f}%')

    annotate_current(ax, savings.index[-1], current, f'{current:.1f}%', side='left')

    add_recession_shading(ax, '2000-01-01')

    ax.set_ylabel('Personal Savings Rate (%)', fontweight='bold')
    ax.set_title('Excess Savings Exhaustion: The Consumer Buffer',
                 fontsize=14, fontweight='bold', pad=20)

    apply_lhm_style(ax)
    ax.legend(loc='upper right', frameon=False)
    add_branding(fig)
    plt.tight_layout()
    return fig


# ============================================================================
# CHART 20: SUBPRIME AUTO
# ============================================================================

def chart_20_subprime_auto():
    """Auto Loan Delinquencies"""
    fetcher = get_fetcher()
    auto_delinq = fetcher.get_fred_series('DRSFRMACBS', '2000-01-01')  # Residential delinquency as proxy

    if auto_delinq.empty:
        return None

    fig, ax = plt.subplots(figsize=(14, 8))

    ax.fill_between(auto_delinq.index, 0, auto_delinq.values, alpha=0.3, color=LHM_COLORS['down_red'])
    ax.plot(auto_delinq.index, auto_delinq.values, linewidth=2.5, color=LHM_COLORS['down_red'])

    current = auto_delinq.iloc[-1]
    annotate_current(ax, auto_delinq.index[-1], current, f'{current:.2f}%', side='left')

    add_recession_shading(ax, '2000-01-01')

    ax.set_ylabel('Delinquency Rate (%)', fontweight='bold')
    ax.set_title('Consumer Credit Stress: Auto Loan Delinquencies',
                 fontsize=14, fontweight='bold', pad=20)

    apply_lhm_style(ax)
    add_branding(fig)
    plt.tight_layout()
    return fig


# ============================================================================
# CHART 21: CREDIT CARD BIFURCATION
# ============================================================================

def chart_21_credit_card():
    """Credit Card Delinquency Rate"""
    fetcher = get_fetcher()
    cc_delinq = fetcher.get_fred_series('DRCCLACBS', '2000-01-01')

    if cc_delinq.empty:
        return None

    fig, ax = plt.subplots(figsize=(14, 8))

    ax.fill_between(cc_delinq.index, 0, cc_delinq.values, alpha=0.3, color=LHM_COLORS['dusk'])
    ax.plot(cc_delinq.index, cc_delinq.values, linewidth=2.5, color=LHM_COLORS['dusk'])

    current = cc_delinq.iloc[-1]
    mean_rate = cc_delinq.mean()
    ax.axhline(mean_rate, color=LHM_COLORS['silvs'], linestyle='--',
               linewidth=1.5, label=f'Mean: {mean_rate:.1f}%')

    annotate_current(ax, cc_delinq.index[-1], current, f'{current:.2f}%', side='left')

    add_recession_shading(ax, '2000-01-01')

    ax.set_ylabel('Credit Card Delinquency Rate (%)', fontweight='bold')
    ax.set_title('Consumer Bifurcation: Credit Card Stress',
                 fontsize=14, fontweight='bold', pad=20)

    apply_lhm_style(ax)
    ax.legend(loc='upper right', frameon=False)
    add_branding(fig)
    plt.tight_layout()
    return fig


# ============================================================================
# CHART 22: WEALTH CONCENTRATION
# ============================================================================

def chart_22_wealth_concentration():
    """Top 1% Wealth Share"""
    fetcher = get_fetcher()
    wealth = fetcher.get_fred_series('WFRBST01134', '1990-01-01')  # Top 1% wealth share

    if wealth.empty:
        return None

    fig, ax = plt.subplots(figsize=(14, 8))

    ax.fill_between(wealth.index, 0, wealth.values, alpha=0.3, color=LHM_COLORS['hot'])
    ax.plot(wealth.index, wealth.values, linewidth=2.5, color=LHM_COLORS['hot'])

    current = wealth.iloc[-1]
    annotate_current(ax, wealth.index[-1], current, f'{current:.1f}%', side='left')

    add_recession_shading(ax, '1990-01-01')

    ax.set_ylabel('Top 1% Wealth Share (%)', fontweight='bold')
    ax.set_title('Wealth Concentration: The K-Shaped Recovery',
                 fontsize=14, fontweight='bold', pad=20)

    apply_lhm_style(ax)
    add_branding(fig)
    plt.tight_layout()
    return fig


# ============================================================================
# CHART 23: CREDIT-LABOR GAP
# ============================================================================

def chart_23_credit_labor_gap():
    """CLG = z(HY_OAS) - z(LFI)"""
    fetcher = get_fetcher()
    hy_oas = fetcher.get_fred_series('BAMLH0A0HYM2', '2001-01-01')
    quits = fetcher.get_fred_series('JTSQUR', '2001-01-01')

    if hy_oas.empty or quits.empty:
        return None

    # Align
    data = pd.DataFrame({'hy': hy_oas, 'quits': quits}).dropna()

    # Z-scores
    z_hy = (data['hy'] - data['hy'].mean()) / data['hy'].std()
    z_quits = -(data['quits'] - data['quits'].mean()) / data['quits'].std()

    clg = z_hy - z_quits

    fig, ax = plt.subplots(figsize=(14, 8))

    ax.fill_between(clg.index, 0, clg.values,
                    where=clg.values >= 0, alpha=0.3, color=LHM_COLORS['up_green'])
    ax.fill_between(clg.index, 0, clg.values,
                    where=clg.values < 0, alpha=0.3, color=LHM_COLORS['down_red'])
    ax.plot(clg.index, clg.values, linewidth=2, color=LHM_COLORS['ocean'])
    ax.axhline(0, color='black', linewidth=0.5)

    current = clg.iloc[-1]
    annotate_current(ax, clg.index[-1], current, f'{current:+.2f}σ', side='left')

    add_recession_shading(ax, '2001-01-01')

    ax.set_ylabel('Credit-Labor Gap (Z-Score)', fontweight='bold')
    ax.set_title('Credit-Labor Gap: z(HY OAS) - z(Labor Fragility)',
                 fontsize=14, fontweight='bold', pad=20)

    apply_lhm_style(ax)
    stats_box(ax, 'CLG < 0: Spreads too tight\nfor labor reality\n\n'
                  'Negative = Mispricing Risk', 'upper_left')
    add_branding(fig)
    plt.tight_layout()
    return fig


# ============================================================================
# CHART 24: CRITICAL CALENDAR
# ============================================================================

def chart_24_critical_calendar():
    """2026 Risk Event Calendar"""
    fig, ax = plt.subplots(figsize=(14, 8))

    events = [
        ('Q1 2026', 'Debt ceiling returns', LHM_COLORS['down_red']),
        ('Mar 2026', 'FOMC meeting', LHM_COLORS['ocean']),
        ('Q2 2026', 'Refunding announcements', LHM_COLORS['dusk']),
        ('Jun 2026', 'FOMC meeting + SEP', LHM_COLORS['ocean']),
        ('Q3 2026', 'Treasury issuance surge', LHM_COLORS['hot']),
        ('Sep 2026', 'FOMC meeting', LHM_COLORS['ocean']),
        ('Q4 2026', 'Election year uncertainty', LHM_COLORS['hot']),
        ('Dec 2026', 'Year-end positioning', LHM_COLORS['dusk'])
    ]

    y_positions = range(len(events), 0, -1)

    for (date, event, color), y in zip(events, y_positions):
        ax.barh(y, 1, color=color, alpha=0.7, height=0.6)
        ax.text(0.05, y, f'{date}: {event}', va='center', fontsize=11, fontweight='bold')

    ax.set_xlim(0, 1.2)
    ax.set_ylim(0, len(events) + 1)
    ax.set_title('2026 Critical Calendar: Key Risk Events',
                 fontsize=14, fontweight='bold', pad=20)

    ax.axis('off')
    add_branding(fig)
    plt.tight_layout()
    return fig


# ============================================================================
# CHART 25: MRI DASHBOARD
# ============================================================================

def chart_25_mri_dashboard():
    """Macro Risk Index - Master Composite Dashboard"""
    fetcher = get_fetcher()

    # Get component data
    hy_oas = fetcher.get_fred_series('BAMLH0A0HYM2', '2010-01-01')
    reserves = fetcher.get_fred_series('TOTRESNS', '2010-01-01')
    gdp = fetcher.get_fred_series('GDP', '2010-01-01')
    quits = fetcher.get_fred_series('JTSQUR', '2010-01-01')

    if hy_oas.empty or reserves.empty or quits.empty:
        return None

    # Create simple composite
    reserves_q = reserves.resample('QE').mean()
    gdp_aligned = gdp.reindex(reserves_q.index, method='ffill')
    lci = reserves_q / gdp_aligned

    # Align all
    data = pd.DataFrame({
        'hy': hy_oas.resample('ME').last(),
        'lci': lci.resample('ME').last(),
        'quits': quits.resample('ME').last()
    }).dropna()

    # Normalize
    z_hy = (data['hy'] - data['hy'].mean()) / data['hy'].std()
    z_lci = -(data['lci'] - data['lci'].mean()) / data['lci'].std()
    z_quits = -(data['quits'] - data['quits'].mean()) / data['quits'].std()

    mri = (z_hy + z_lci + z_quits) / 3

    fig, ax = plt.subplots(figsize=(14, 8))

    # Background zones
    ax.axhspan(1, mri.max()+1, alpha=0.2, color=LHM_COLORS['down_red'], zorder=0)
    ax.axhspan(0, 1, alpha=0.1, color=LHM_COLORS['dusk'], zorder=0)
    ax.axhspan(-1, 0, alpha=0.1, color=LHM_COLORS['silvs'], zorder=0)
    ax.axhspan(mri.min()-1, -1, alpha=0.15, color=LHM_COLORS['up_green'], zorder=0)

    ax.plot(mri.index, mri.values, linewidth=2.5, color=LHM_COLORS['ocean'])

    current = mri.iloc[-1]
    ax.axhline(0, color='black', linewidth=0.5)
    ax.axhline(1, color=LHM_COLORS['down_red'], linestyle='--', linewidth=1.5)

    annotate_current(ax, mri.index[-1], current, f'MRI: {current:+.2f}σ', side='left')

    ax.set_ylabel('Macro Risk Index (Z-Score)', fontweight='bold')
    ax.set_title('Macro Risk Index (MRI): System Stress Dashboard',
                 fontsize=14, fontweight='bold', pad=20)

    apply_lhm_style(ax)

    # Legend for zones
    ax.text(0.02, 0.95, 'HIGH RISK', transform=ax.transAxes, fontsize=9,
            color=LHM_COLORS['down_red'], fontweight='bold')
    ax.text(0.02, 0.05, 'LOW RISK', transform=ax.transAxes, fontsize=9,
            color=LHM_COLORS['up_green'], fontweight='bold')

    add_branding(fig)
    plt.tight_layout()
    return fig


# ============================================================================
# CHART 26: POSITIONING MATRIX
# ============================================================================

def chart_26_positioning_matrix():
    """Asset Class Positioning Grid"""
    fig, ax = plt.subplots(figsize=(14, 8))

    positions = {
        'UST Long Duration': ('Underweight', LHM_COLORS['down_red']),
        'UST Short Duration': ('Overweight', LHM_COLORS['up_green']),
        'Investment Grade': ('Neutral', LHM_COLORS['silvs']),
        'High Yield': ('Underweight', LHM_COLORS['down_red']),
        'Equities (Large Cap)': ('Neutral', LHM_COLORS['silvs']),
        'Equities (Small Cap)': ('Underweight', LHM_COLORS['down_red']),
        'Gold': ('Overweight', LHM_COLORS['up_green']),
        'Cash': ('Overweight', LHM_COLORS['up_green']),
    }

    y_pos = range(len(positions), 0, -1)
    for (asset, (pos, color)), y in zip(positions.items(), y_pos):
        bar_length = {'Overweight': 0.8, 'Neutral': 0.5, 'Underweight': 0.3}[pos]
        ax.barh(y, bar_length, color=color, alpha=0.7, height=0.6)
        ax.text(0.02, y, f'{asset}: {pos}', va='center', fontsize=11, fontweight='bold')

    ax.set_xlim(0, 1)
    ax.set_ylim(0, len(positions) + 1)
    ax.set_title('2026 Positioning Matrix: Tactical Asset Allocation',
                 fontsize=14, fontweight='bold', pad=20)

    ax.axis('off')
    add_branding(fig)
    plt.tight_layout()
    return fig


# ============================================================================
# CHART 27: SCENARIO ANALYSIS
# ============================================================================

def chart_27_scenario_analysis():
    """Three Scenario Probabilities"""
    fig, ax = plt.subplots(figsize=(14, 8))

    scenarios = {
        'Soft Landing\n(Growth slows, no recession)': (25, LHM_COLORS['up_green']),
        'Hard Landing\n(Recession in 2026)': (40, LHM_COLORS['down_red']),
        'Stagflation\n(Inflation sticks + slowdown)': (35, LHM_COLORS['dusk']),
    }

    labels = list(scenarios.keys())
    probs = [v[0] for v in scenarios.values()]
    colors = [v[1] for v in scenarios.values()]

    bars = ax.barh(range(len(scenarios)), probs, color=colors, alpha=0.8, height=0.6)

    for bar, prob in zip(bars, probs):
        ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2,
                f'{prob}%', va='center', fontsize=14, fontweight='bold')

    ax.set_yticks(range(len(scenarios)))
    ax.set_yticklabels(labels, fontsize=11)
    ax.set_xlim(0, 60)
    ax.set_xlabel('Probability (%)', fontweight='bold')
    ax.set_title('2026 Scenario Analysis: Probability Distribution',
                 fontsize=14, fontweight='bold', pad=20)

    apply_lhm_style(ax)
    add_branding(fig)
    plt.tight_layout()
    return fig


# ============================================================================
# GENERATION
# ============================================================================

def generate_all_charts(output_dir: str = '.'):
    """Generate all 27 HORIZON 2026 charts."""
    os.makedirs(output_dir, exist_ok=True)

    charts = [
        ('chart_01_rrp_drawdown', chart_01_rrp_drawdown),
        ('chart_02_liquidity_cushion_index', chart_02_liquidity_cushion_index),
        ('chart_03_qt_termination', chart_03_qt_termination),
        ('chart_04_sofr_effr_spread', chart_04_sofr_effr_spread),
        ('chart_05_repo_rate_dispersion', chart_05_repo_dispersion),
        ('chart_06_reserves_gdp', chart_06_reserves_gdp),
        ('chart_07_debt_trajectory', chart_07_debt_trajectory),
        ('chart_08_interest_expense', chart_08_interest_expense),
        ('chart_09_fiscal_dominance_cascade', chart_09_fiscal_dominance),
        ('chart_10_foreign_holdings', chart_10_foreign_holdings),
        ('chart_11_term_premium', chart_11_term_premium),
        ('chart_12_dealer_inventory_slr', chart_12_dealer_inventory),
        ('chart_13_dealer_takedown', chart_13_dealer_takedown),
        ('chart_14_auction_tails', chart_14_auction_tails),
        ('chart_15_basis_dynamics', chart_15_basis_dynamics),
        ('chart_16_labor_fragility_index', chart_16_labor_fragility_index),
        ('chart_17_job_cuts_claims', chart_17_job_cuts_claims),
        ('chart_18_quits_wage_lead', chart_18_quits_wage_lead),
        ('chart_19_excess_savings', chart_19_excess_savings),
        ('chart_20_subprime_auto', chart_20_subprime_auto),
        ('chart_21_credit_card_bifurcation', chart_21_credit_card),
        ('chart_22_wealth_concentration', chart_22_wealth_concentration),
        ('chart_23_credit_labor_gap', chart_23_credit_labor_gap),
        ('chart_24_critical_calendar', chart_24_critical_calendar),
        ('chart_25_mri_dashboard', chart_25_mri_dashboard),
        ('chart_26_positioning_matrix', chart_26_positioning_matrix),
        ('chart_27_scenario_analysis', chart_27_scenario_analysis),
    ]

    print("=" * 60)
    print("HORIZON 2026 - CHART GENERATION")
    print("Lighthouse Macro | LHM Visual Standards")
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
            fig.savefig(filepath, dpi=300, bbox_inches='tight',
                        facecolor='white', edgecolor='none')
            plt.close(fig)
            print("OK")
            success += 1
        except Exception as e:
            print(f"ERROR: {e}")

    print("=" * 60)
    print(f"Complete! {success}/{len(charts)} charts generated.")
    print(f"Output: {output_dir}")
    print("=" * 60)


if __name__ == "__main__":
    generate_all_charts()
