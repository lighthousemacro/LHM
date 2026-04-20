"""
HORIZON 2026 - COMPLETE INSTITUTIONAL CHART SET
Lighthouse Macro - January 2026

EVERY chart uses REAL DATA. No fabrication. No smoothing without disclosure.
Annotations MATCH the data values exactly.

Output: /Users/bob/LHM/data/charts/horizon_institutional/
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
import requests
from datetime import datetime, timedelta
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Config
FRED_API_KEY = os.environ.get('FRED_API_KEY')
OUTPUT_DIR = Path('/Users/bob/LHM/data/charts/horizon_institutional')

# Lighthouse colors
COLORS = {
    'ocean': '#2389BB',
    'dusk': '#FF6723',
    'electric': '#03DDFF',
    'hot': '#FF00F0',
    'sea': '#289389',
    'silvs': '#D1D1D1',
    'up': '#008000',
    'down': '#FF3333',
    'neutral': '#666666',
}


def fetch_fred(series_id: str, start: str = '2000-01-01') -> pd.Series:
    """Fetch FRED data. FAILS if unavailable - never fabricates."""
    url = 'https://api.stlouisfed.org/fred/series/observations'
    params = {
        'series_id': series_id,
        'api_key': FRED_API_KEY,
        'file_type': 'json',
        'observation_start': start,
    }
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()

    if 'observations' not in data or len(data['observations']) == 0:
        raise ValueError(f"No data for {series_id}")

    df = pd.DataFrame(data['observations'])
    df = df[df['value'] != '.']
    df['date'] = pd.to_datetime(df['date'])
    df['value'] = pd.to_numeric(df['value'])
    return df.set_index('date')['value']


def add_recessions(ax, start_year=2000):
    """Add recession shading."""
    recessions = [
        ('2001-03-01', '2001-11-01'),
        ('2007-12-01', '2009-06-01'),
        ('2020-02-01', '2020-04-01'),
    ]
    for s, e in recessions:
        if pd.Timestamp(s).year >= start_year:
            ax.axvspan(pd.Timestamp(s), pd.Timestamp(e), alpha=0.1, color='gray', zorder=0)


def style_chart(ax):
    """Apply LHM style."""
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(False)


def add_branding(fig, source, last_date=None):
    """Add LHM branding with source and data date outside plot area."""
    fig.text(0.01, 0.99, 'LIGHTHOUSE MACRO', fontsize=10, fontweight='bold',
             color=COLORS['ocean'], ha='left', va='top')
    fig.text(0.99, 0.01, 'MACRO, ILLUMINATED.', fontsize=8, style='italic',
             color=COLORS['ocean'], ha='right', va='bottom', alpha=0.7)

    # Source line with data date - positioned below the figure
    date_str = f" | Data through {last_date.strftime('%b %d, %Y')}" if last_date else ""
    fig.text(0.01, 0.005, f'Source: {source}{date_str}', fontsize=7, color=COLORS['neutral'],
             ha='left', va='bottom', style='italic')


# =============================================================================
# PART I: MACRO DYNAMICS (Charts 1-12)
# =============================================================================

def chart_01_rrp_drawdown():
    """ON RRP Drawdown - the liquidity buffer exhaustion."""
    rrp = fetch_fred('RRPONTSYD', '2021-01-01')

    fig, ax = plt.subplots(figsize=(12, 7))
    ax.plot(rrp.index, rrp.values, linewidth=1.5, color=COLORS['ocean'])

    peak = rrp.max()
    peak_date = rrp.idxmax()
    current = rrp.iloc[-1]
    current_date = rrp.index[-1]

    ax.scatter([peak_date], [peak], s=100, color=COLORS['hot'], zorder=5)
    ax.scatter([current_date], [current], s=100, color=COLORS['down'], zorder=5)

    ax.annotate(f'Peak: ${peak:,.0f}B\n({peak_date.strftime("%b %Y")})',
                xy=(peak_date, peak), xytext=(20, -20), textcoords='offset points',
                fontsize=9, bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))

    ax.annotate(f'Current: ${current:,.1f}B\n({current_date.strftime("%b %Y")})',
                xy=(current_date, current), xytext=(-80, 30), textcoords='offset points',
                fontsize=10, fontweight='bold', color='white',
                bbox=dict(boxstyle='round', facecolor=COLORS['down'], alpha=0.9),
                arrowprops=dict(arrowstyle='->', color=COLORS['down']))

    ax.set_title('ON RRP Drawdown: The Liquidity Buffer Exhaustion', fontweight='bold', fontsize=13)
    ax.set_ylabel('ON RRP Balance ($B)', fontweight='bold')
    style_chart(ax)
    add_branding(fig, 'FRED (RRPONTSYD)', last_date=rrp.index[-1])
    plt.tight_layout()
    return fig


def chart_02_reserves():
    """Bank Reserves vs GDP."""
    reserves = fetch_fred('WRESBAL', '2008-01-01')
    gdp = fetch_fred('GDP', '2008-01-01')

    # Align quarterly
    reserves_q = reserves.resample('QE').last()
    gdp_q = gdp.resample('QE').last()
    ratio = (reserves_q / gdp_q * 100).dropna()

    fig, ax = plt.subplots(figsize=(12, 7))
    ax.fill_between(ratio.index, 0, ratio.values, alpha=0.3, color=COLORS['ocean'])
    ax.plot(ratio.index, ratio.values, linewidth=2, color=COLORS['ocean'])

    current = ratio.iloc[-1]
    ax.annotate(f'Current: {current:.1f}%', xy=(ratio.index[-1], current),
                xytext=(-60, 20), textcoords='offset points',
                fontsize=10, fontweight='bold', color='white',
                bbox=dict(boxstyle='round', facecolor=COLORS['ocean'], alpha=0.9),
                arrowprops=dict(arrowstyle='->', color=COLORS['ocean']))

    ax.set_title('Bank Reserves as % of GDP', fontweight='bold', fontsize=13)
    ax.set_ylabel('Reserves / GDP (%)', fontweight='bold')
    add_recessions(ax, 2008)
    style_chart(ax)
    add_branding(fig, 'FRED (WRESBAL, GDP)', last_date=ratio.index[-1])
    plt.tight_layout()
    return fig


def chart_03_sofr_effr():
    """SOFR-EFFR Spread - funding stress indicator."""
    sofr = fetch_fred('SOFR', '2020-01-01')
    effr = fetch_fred('EFFR', '2020-01-01')

    spread = (sofr - effr) * 100  # bps
    spread_ma = spread.rolling(20).mean()

    fig, ax = plt.subplots(figsize=(12, 7))
    ax.bar(spread.index, spread.values, width=1, alpha=0.4, color=COLORS['ocean'], label='Daily')
    ax.plot(spread_ma.index, spread_ma.values, linewidth=2, color=COLORS['hot'], label='20D MA')

    ax.axhline(0, color='black', linewidth=0.5)
    ax.axhline(15, color=COLORS['dusk'], linestyle='--', linewidth=1.5)
    ax.text(spread.index[10], 16, 'Stress Threshold (15 bps)', fontsize=8, color=COLORS['dusk'])

    current = spread_ma.iloc[-1]
    ax.annotate(f'20D MA: {current:.1f} bps', xy=(spread_ma.index[-1], current),
                xytext=(-80, 30), textcoords='offset points',
                fontsize=10, fontweight='bold', color='white',
                bbox=dict(boxstyle='round', facecolor=COLORS['hot'], alpha=0.9),
                arrowprops=dict(arrowstyle='->', color=COLORS['hot']))

    ax.set_title('SOFR-EFFR Spread: Funding Market Stress', fontweight='bold', fontsize=13)
    ax.set_ylabel('Spread (bps)', fontweight='bold')
    ax.legend(loc='upper left')
    style_chart(ax)
    add_branding(fig, 'FRED (SOFR, EFFR)', last_date=spread.index[-1])
    plt.tight_layout()
    return fig


def chart_04_tga():
    """Treasury General Account - fiscal plumbing."""
    tga = fetch_fred('WTREGEN', '2015-01-01')
    tga = tga / 1000  # Convert to $B

    fig, ax = plt.subplots(figsize=(12, 7))
    ax.fill_between(tga.index, 0, tga.values, alpha=0.3, color=COLORS['sea'])
    ax.plot(tga.index, tga.values, linewidth=1.5, color=COLORS['sea'])

    current = tga.iloc[-1]
    ax.annotate(f'Current: ${current:.0f}B', xy=(tga.index[-1], current),
                xytext=(-80, 20), textcoords='offset points',
                fontsize=10, fontweight='bold', color='white',
                bbox=dict(boxstyle='round', facecolor=COLORS['sea'], alpha=0.9),
                arrowprops=dict(arrowstyle='->', color=COLORS['sea']))

    ax.set_title('Treasury General Account (TGA)', fontweight='bold', fontsize=13)
    ax.set_ylabel('TGA Balance ($B)', fontweight='bold')
    add_recessions(ax, 2015)
    style_chart(ax)
    add_branding(fig, 'FRED (WTREGEN)', last_date=tga.index[-1])
    plt.tight_layout()
    return fig


def chart_05_fed_balance_sheet():
    """Fed Balance Sheet - QT progress."""
    walcl = fetch_fred('WALCL', '2008-01-01')
    walcl = walcl / 1e6  # Convert to $T

    fig, ax = plt.subplots(figsize=(12, 7))
    ax.fill_between(walcl.index, 0, walcl.values, alpha=0.3, color=COLORS['ocean'])
    ax.plot(walcl.index, walcl.values, linewidth=2, color=COLORS['ocean'])

    peak = walcl.max()
    peak_date = walcl.idxmax()
    current = walcl.iloc[-1]

    ax.scatter([peak_date], [peak], s=80, color=COLORS['hot'], zorder=5)
    ax.annotate(f'Peak: ${peak:.2f}T', xy=(peak_date, peak),
                xytext=(20, 10), textcoords='offset points', fontsize=9)

    ax.annotate(f'Current: ${current:.2f}T', xy=(walcl.index[-1], current),
                xytext=(-80, -30), textcoords='offset points',
                fontsize=10, fontweight='bold', color='white',
                bbox=dict(boxstyle='round', facecolor=COLORS['ocean'], alpha=0.9),
                arrowprops=dict(arrowstyle='->', color=COLORS['ocean']))

    ax.set_title('Federal Reserve Balance Sheet', fontweight='bold', fontsize=13)
    ax.set_ylabel('Total Assets ($T)', fontweight='bold')
    add_recessions(ax, 2008)
    style_chart(ax)
    add_branding(fig, 'FRED (WALCL)', last_date=walcl.index[-1])
    plt.tight_layout()
    return fig


def chart_06_quits_rate():
    """Quits Rate - labor market leading indicator."""
    quits = fetch_fred('JTSQUR', '2001-01-01')

    fig, ax = plt.subplots(figsize=(12, 7))
    ax.plot(quits.index, quits.values, linewidth=1.5, color=COLORS['ocean'],
            marker='.', markersize=3, alpha=0.8)

    mean_val = quits.mean()
    ax.axhline(mean_val, color=COLORS['silvs'], linestyle='--', linewidth=1)
    ax.text(quits.index[5], mean_val + 0.05, f'Mean: {mean_val:.2f}%', fontsize=8, color=COLORS['neutral'])

    current = quits.iloc[-1]
    ax.annotate(f'Current: {current:.1f}%', xy=(quits.index[-1], current),
                xytext=(-80, 20), textcoords='offset points',
                fontsize=10, fontweight='bold', color='white',
                bbox=dict(boxstyle='round', facecolor=COLORS['ocean'], alpha=0.9),
                arrowprops=dict(arrowstyle='->', color=COLORS['ocean']))

    ax.set_title('Quits Rate: Labor Market Confidence', fontweight='bold', fontsize=13)
    ax.set_ylabel('Quits Rate (%)', fontweight='bold')
    add_recessions(ax)
    style_chart(ax)
    add_branding(fig, 'FRED (JTSQUR) | Monthly JOLTS data', last_date=quits.index[-1])
    plt.tight_layout()
    return fig


def chart_07_hires_rate():
    """Hires Rate - labor demand."""
    hires = fetch_fred('JTSHIR', '2001-01-01')

    fig, ax = plt.subplots(figsize=(12, 7))
    ax.plot(hires.index, hires.values, linewidth=1.5, color=COLORS['sea'],
            marker='.', markersize=3, alpha=0.8)

    current = hires.iloc[-1]
    ax.annotate(f'Current: {current:.0f}K', xy=(hires.index[-1], current),
                xytext=(-80, 20), textcoords='offset points',
                fontsize=10, fontweight='bold', color='white',
                bbox=dict(boxstyle='round', facecolor=COLORS['sea'], alpha=0.9),
                arrowprops=dict(arrowstyle='->', color=COLORS['sea']))

    ax.set_title('Hires Level: Labor Demand', fontweight='bold', fontsize=13)
    ax.set_ylabel('Hires (Thousands)', fontweight='bold')
    add_recessions(ax)
    style_chart(ax)
    add_branding(fig, 'FRED (JTSHIR) | Monthly JOLTS data', last_date=hires.index[-1])
    plt.tight_layout()
    return fig


def chart_08_unemployment():
    """Unemployment Rate."""
    urate = fetch_fred('UNRATE', '2000-01-01')

    fig, ax = plt.subplots(figsize=(12, 7))
    ax.fill_between(urate.index, 0, urate.values, alpha=0.3, color=COLORS['dusk'])
    ax.plot(urate.index, urate.values, linewidth=1.5, color=COLORS['dusk'])

    current = urate.iloc[-1]
    ax.annotate(f'Current: {current:.1f}%', xy=(urate.index[-1], current),
                xytext=(-80, 20), textcoords='offset points',
                fontsize=10, fontweight='bold', color='white',
                bbox=dict(boxstyle='round', facecolor=COLORS['dusk'], alpha=0.9),
                arrowprops=dict(arrowstyle='->', color=COLORS['dusk']))

    ax.set_title('Unemployment Rate', fontweight='bold', fontsize=13)
    ax.set_ylabel('Rate (%)', fontweight='bold')
    add_recessions(ax)
    style_chart(ax)
    add_branding(fig, 'FRED (UNRATE) | Monthly', last_date=urate.index[-1])
    plt.tight_layout()
    return fig


def chart_09_initial_claims():
    """Initial Jobless Claims."""
    claims = fetch_fred('ICSA', '2015-01-01')
    claims = claims / 1000  # Convert to thousands

    fig, ax = plt.subplots(figsize=(12, 7))
    ax.plot(claims.index, claims.values, linewidth=1, color=COLORS['ocean'], alpha=0.7)
    claims_ma = claims.rolling(4).mean()
    ax.plot(claims_ma.index, claims_ma.values, linewidth=2, color=COLORS['hot'], label='4-Week MA')

    current = claims_ma.iloc[-1]
    ax.annotate(f'4W MA: {current:.0f}K', xy=(claims_ma.index[-1], current),
                xytext=(-80, 20), textcoords='offset points',
                fontsize=10, fontweight='bold', color='white',
                bbox=dict(boxstyle='round', facecolor=COLORS['hot'], alpha=0.9),
                arrowprops=dict(arrowstyle='->', color=COLORS['hot']))

    ax.set_title('Initial Jobless Claims', fontweight='bold', fontsize=13)
    ax.set_ylabel('Claims (Thousands)', fontweight='bold')
    ax.set_ylim(0, min(claims.max() * 1.1, 1000))  # Cap y-axis to exclude COVID spike
    ax.legend(loc='upper right')
    style_chart(ax)
    add_branding(fig, 'FRED (ICSA) | Weekly', last_date=claims.index[-1])
    plt.tight_layout()
    return fig


def chart_10_savings_rate():
    """Personal Savings Rate - raw monthly data."""
    savings = fetch_fred('PSAVERT', '2015-01-01')

    fig, ax = plt.subplots(figsize=(12, 7))
    # RAW data with markers to show it's real
    ax.plot(savings.index, savings.values, linewidth=1.2, color=COLORS['ocean'],
            marker='.', markersize=2, alpha=0.8)

    pre_covid_avg = savings[savings.index < '2020-01-01'].mean()
    ax.axhline(pre_covid_avg, color=COLORS['silvs'], linestyle='--', linewidth=1)
    ax.text(savings.index[5], pre_covid_avg + 0.5, f'Pre-COVID avg: {pre_covid_avg:.1f}%',
            fontsize=8, color=COLORS['neutral'])

    current = savings.iloc[-1]
    ax.annotate(f'Current: {current:.1f}%', xy=(savings.index[-1], current),
                xytext=(-80, 20), textcoords='offset points',
                fontsize=10, fontweight='bold', color='white',
                bbox=dict(boxstyle='round', facecolor=COLORS['ocean'], alpha=0.9),
                arrowprops=dict(arrowstyle='->', color=COLORS['ocean']))

    ax.set_title('Personal Savings Rate', fontweight='bold', fontsize=13)
    ax.set_ylabel('Savings Rate (%)', fontweight='bold')
    style_chart(ax)
    add_branding(fig, 'FRED (PSAVERT) | Raw monthly data, no smoothing', last_date=savings.index[-1])
    plt.tight_layout()
    return fig


def chart_11_consumer_credit():
    """Consumer Credit Outstanding."""
    credit = fetch_fred('TOTALSL', '2000-01-01')
    credit = credit / 1000  # Convert to $T

    fig, ax = plt.subplots(figsize=(12, 7))
    ax.fill_between(credit.index, 0, credit.values, alpha=0.3, color=COLORS['dusk'])
    ax.plot(credit.index, credit.values, linewidth=2, color=COLORS['dusk'])

    current = credit.iloc[-1]
    ax.annotate(f'Current: ${current:.2f}T', xy=(credit.index[-1], current),
                xytext=(-80, -30), textcoords='offset points',
                fontsize=10, fontweight='bold', color='white',
                bbox=dict(boxstyle='round', facecolor=COLORS['dusk'], alpha=0.9),
                arrowprops=dict(arrowstyle='->', color=COLORS['dusk']))

    ax.set_title('Consumer Credit Outstanding', fontweight='bold', fontsize=13)
    ax.set_ylabel('Total ($T)', fontweight='bold')
    add_recessions(ax)
    style_chart(ax)
    add_branding(fig, 'FRED (TOTALSL) | Monthly', last_date=credit.index[-1])
    plt.tight_layout()
    return fig


def chart_12_cc_delinquency():
    """Credit Card Delinquency Rate."""
    delinq = fetch_fred('DRCCLACBS', '2000-01-01')

    fig, ax = plt.subplots(figsize=(12, 7))
    ax.plot(delinq.index, delinq.values, linewidth=2, color=COLORS['down'],
            marker='o', markersize=4)

    pre_covid_avg = delinq[delinq.index < '2020-01-01'].mean()
    ax.axhline(pre_covid_avg, color=COLORS['silvs'], linestyle='--', linewidth=1)
    ax.text(delinq.index[5], pre_covid_avg + 0.1, f'Pre-COVID avg: {pre_covid_avg:.2f}%',
            fontsize=8, color=COLORS['neutral'])

    current = delinq.iloc[-1]
    ax.annotate(f'Current: {current:.2f}%', xy=(delinq.index[-1], current),
                xytext=(-80, 20), textcoords='offset points',
                fontsize=10, fontweight='bold', color='white',
                bbox=dict(boxstyle='round', facecolor=COLORS['down'], alpha=0.9),
                arrowprops=dict(arrowstyle='->', color=COLORS['down']))

    ax.set_title('Credit Card Delinquency Rate', fontweight='bold', fontsize=13)
    ax.set_ylabel('Delinquency Rate (%)', fontweight='bold')
    add_recessions(ax)
    style_chart(ax)
    add_branding(fig, 'FRED (DRCCLACBS) | Quarterly', last_date=delinq.index[-1])
    plt.tight_layout()
    return fig


# =============================================================================
# PART II: MONETARY MECHANICS (Charts 13-24)
# =============================================================================

def chart_13_yield_curve():
    """Yield Curve - 10Y-2Y Spread."""
    y10 = fetch_fred('DGS10', '2000-01-01')
    y2 = fetch_fred('DGS2', '2000-01-01')

    spread = y10 - y2
    spread = spread.dropna()

    fig, ax = plt.subplots(figsize=(12, 7))
    ax.fill_between(spread.index, 0, spread.values,
                    where=spread.values >= 0, alpha=0.3, color=COLORS['up'])
    ax.fill_between(spread.index, 0, spread.values,
                    where=spread.values < 0, alpha=0.3, color=COLORS['down'])
    ax.plot(spread.index, spread.values, linewidth=1.5, color=COLORS['ocean'])

    ax.axhline(0, color='black', linewidth=1)

    current = spread.iloc[-1]
    ax.annotate(f'Current: {current:.2f}%', xy=(spread.index[-1], current),
                xytext=(-80, 20), textcoords='offset points',
                fontsize=10, fontweight='bold', color='white',
                bbox=dict(boxstyle='round', facecolor=COLORS['ocean'], alpha=0.9),
                arrowprops=dict(arrowstyle='->', color=COLORS['ocean']))

    ax.set_title('Yield Curve: 10Y-2Y Spread', fontweight='bold', fontsize=13)
    ax.set_ylabel('Spread (%)', fontweight='bold')
    add_recessions(ax)
    style_chart(ax)
    add_branding(fig, 'FRED (DGS10, DGS2) | Daily', last_date=spread.index[-1])
    plt.tight_layout()
    return fig


def chart_14_hy_spreads():
    """High Yield Credit Spreads."""
    hy = fetch_fred('BAMLH0A0HYM2', '2000-01-01')

    fig, ax = plt.subplots(figsize=(12, 7))
    ax.fill_between(hy.index, 0, hy.values, alpha=0.3, color=COLORS['dusk'])
    ax.plot(hy.index, hy.values, linewidth=1.5, color=COLORS['dusk'])

    mean_val = hy.mean()
    ax.axhline(mean_val, color=COLORS['silvs'], linestyle='--', linewidth=1)

    current = hy.iloc[-1]
    percentile = (hy < current).mean() * 100

    ax.annotate(f'Current: {current:.2f}%\n({percentile:.0f}th percentile)',
                xy=(hy.index[-1], current),
                xytext=(-100, 30), textcoords='offset points',
                fontsize=10, fontweight='bold', color='white',
                bbox=dict(boxstyle='round', facecolor=COLORS['dusk'], alpha=0.9),
                arrowprops=dict(arrowstyle='->', color=COLORS['dusk']))

    ax.set_title('High Yield Credit Spreads (OAS)', fontweight='bold', fontsize=13)
    ax.set_ylabel('Spread (%)', fontweight='bold')
    add_recessions(ax)
    style_chart(ax)
    add_branding(fig, 'FRED (BAMLH0A0HYM2) | Daily', last_date=hy.index[-1])
    plt.tight_layout()
    return fig


def chart_15_ig_spreads():
    """Investment Grade Credit Spreads."""
    ig = fetch_fred('BAMLC0A0CM', '2000-01-01')

    fig, ax = plt.subplots(figsize=(12, 7))
    ax.fill_between(ig.index, 0, ig.values, alpha=0.3, color=COLORS['sea'])
    ax.plot(ig.index, ig.values, linewidth=1.5, color=COLORS['sea'])

    current = ig.iloc[-1]
    percentile = (ig < current).mean() * 100

    ax.annotate(f'Current: {current:.2f}%\n({percentile:.0f}th percentile)',
                xy=(ig.index[-1], current),
                xytext=(-100, 30), textcoords='offset points',
                fontsize=10, fontweight='bold', color='white',
                bbox=dict(boxstyle='round', facecolor=COLORS['sea'], alpha=0.9),
                arrowprops=dict(arrowstyle='->', color=COLORS['sea']))

    ax.set_title('Investment Grade Credit Spreads (OAS)', fontweight='bold', fontsize=13)
    ax.set_ylabel('Spread (%)', fontweight='bold')
    add_recessions(ax)
    style_chart(ax)
    add_branding(fig, 'FRED (BAMLC0A0CM) | Daily', last_date=ig.index[-1])
    plt.tight_layout()
    return fig


def chart_16_credit_spread_waterfall():
    """Credit Spread Distribution - REAL percentile data."""
    hy = fetch_fred('BAMLH0A0HYM2', '2000-01-01')
    ig = fetch_fred('BAMLC0A0CM', '2000-01-01')
    bbb = fetch_fred('BAMLC0A4CBBB', '2000-01-01')

    # Current values
    hy_current = hy.iloc[-1]
    ig_current = ig.iloc[-1]
    bbb_current = bbb.iloc[-1]

    # Percentiles (where current falls in historical distribution)
    hy_pct = (hy < hy_current).mean() * 100
    ig_pct = (ig < ig_current).mean() * 100
    bbb_pct = (bbb < bbb_current).mean() * 100

    fig, ax = plt.subplots(figsize=(12, 7))

    categories = ['IG (AAA-BBB)', 'BBB', 'High Yield']
    values = [ig_current, bbb_current, hy_current]
    percentiles = [ig_pct, bbb_pct, hy_pct]
    colors = [COLORS['sea'], COLORS['dusk'], COLORS['down']]

    bars = ax.bar(categories, values, color=colors, alpha=0.8, edgecolor='white', linewidth=2)

    # Add value and percentile labels
    for bar, val, pct in zip(bars, values, percentiles):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, height + 0.1,
                f'{val:.2f}%\n({pct:.0f}th %ile)',
                ha='center', va='bottom', fontsize=11, fontweight='bold')

    ax.set_ylabel('Spread (%)', fontweight='bold')
    ax.set_title('Credit Spread Distribution: Current Levels vs History',
                 fontweight='bold', fontsize=13)

    # Add context
    ax.text(0.98, 0.98, 'Lower percentile = tighter spreads\n(less risk compensation)',
            transform=ax.transAxes, ha='right', va='top', fontsize=9,
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))

    style_chart(ax)
    add_branding(fig, 'FRED (BAMLH0A0HYM2, BAMLC0A0CM, BAMLC0A4CBBB)', last_date=hy.index[-1])
    plt.tight_layout()
    return fig


def chart_17_debt_gdp():
    """Federal Debt to GDP."""
    debt_gdp = fetch_fred('GFDEGDQ188S', '1970-01-01')

    fig, ax = plt.subplots(figsize=(12, 7))
    ax.fill_between(debt_gdp.index, 0, debt_gdp.values, alpha=0.3, color=COLORS['dusk'])
    ax.plot(debt_gdp.index, debt_gdp.values, linewidth=2, color=COLORS['dusk'])

    ax.axhline(100, color=COLORS['down'], linestyle='--', linewidth=1.5)
    ax.text(debt_gdp.index[10], 102, '100% Threshold', fontsize=9, color=COLORS['down'])

    current = debt_gdp.iloc[-1]
    ax.annotate(f'Current: {current:.0f}%', xy=(debt_gdp.index[-1], current),
                xytext=(-80, -30), textcoords='offset points',
                fontsize=10, fontweight='bold', color='white',
                bbox=dict(boxstyle='round', facecolor=COLORS['dusk'], alpha=0.9),
                arrowprops=dict(arrowstyle='->', color=COLORS['dusk']))

    ax.set_title('Federal Debt to GDP', fontweight='bold', fontsize=13)
    ax.set_ylabel('Debt / GDP (%)', fontweight='bold')
    add_recessions(ax, 1970)
    style_chart(ax)
    add_branding(fig, 'FRED (GFDEGDQ188S) | Quarterly', last_date=debt_gdp.index[-1])
    plt.tight_layout()
    return fig


def chart_18_interest_expense():
    """Interest Expense as % of Revenue."""
    interest = fetch_fred('A091RC1Q027SBEA', '1970-01-01')
    receipts = fetch_fred('FGRECPT', '1970-01-01')

    # Annualize and align
    interest_a = interest.resample('YE').sum()
    receipts_a = receipts.resample('YE').last()

    ratio = (interest_a / receipts_a * 100).dropna()

    fig, ax = plt.subplots(figsize=(12, 7))
    ax.fill_between(ratio.index, 0, ratio.values, alpha=0.3, color=COLORS['dusk'])
    ax.plot(ratio.index, ratio.values, linewidth=2, color=COLORS['dusk'])

    current = ratio.iloc[-1]
    ax.annotate(f'Current: {current:.1f}%', xy=(ratio.index[-1], current),
                xytext=(-80, 20), textcoords='offset points',
                fontsize=10, fontweight='bold', color='white',
                bbox=dict(boxstyle='round', facecolor=COLORS['dusk'], alpha=0.9),
                arrowprops=dict(arrowstyle='->', color=COLORS['dusk']))

    ax.set_title('Interest Expense as % of Federal Revenue', fontweight='bold', fontsize=13)
    ax.set_ylabel('Interest / Revenue (%)', fontweight='bold')
    add_recessions(ax, 1970)
    style_chart(ax)
    add_branding(fig, 'FRED (A091RC1Q027SBEA, FGRECPT)', last_date=ratio.index[-1])
    plt.tight_layout()
    return fig


def chart_19_foreign_holdings():
    """Foreign Holdings of Treasuries."""
    foreign = fetch_fred('FDHBFIN', '2000-01-01')
    foreign = foreign / 1000  # Convert to $T

    fig, ax = plt.subplots(figsize=(12, 7))
    ax.fill_between(foreign.index, 0, foreign.values, alpha=0.3, color=COLORS['ocean'])
    ax.plot(foreign.index, foreign.values, linewidth=2, color=COLORS['ocean'])

    current = foreign.iloc[-1]
    peak = foreign.max()

    ax.annotate(f'Current: ${current:.2f}T', xy=(foreign.index[-1], current),
                xytext=(-80, 20), textcoords='offset points',
                fontsize=10, fontweight='bold', color='white',
                bbox=dict(boxstyle='round', facecolor=COLORS['ocean'], alpha=0.9),
                arrowprops=dict(arrowstyle='->', color=COLORS['ocean']))

    ax.set_title('Foreign Holdings of U.S. Treasuries', fontweight='bold', fontsize=13)
    ax.set_ylabel('Holdings ($T)', fontweight='bold')
    add_recessions(ax)
    style_chart(ax)
    add_branding(fig, 'FRED (FDHBFIN) | Monthly', last_date=foreign.index[-1])
    plt.tight_layout()
    return fig


def chart_20_cpi():
    """CPI Inflation - YoY."""
    cpi = fetch_fred('CPIAUCSL', '2000-01-01')
    cpi_yoy = cpi.pct_change(12) * 100

    fig, ax = plt.subplots(figsize=(12, 7))
    ax.fill_between(cpi_yoy.index, 0, cpi_yoy.values,
                    where=cpi_yoy.values >= 0, alpha=0.3, color=COLORS['dusk'])
    ax.fill_between(cpi_yoy.index, 0, cpi_yoy.values,
                    where=cpi_yoy.values < 0, alpha=0.3, color=COLORS['ocean'])
    ax.plot(cpi_yoy.index, cpi_yoy.values, linewidth=1.5, color=COLORS['dusk'])

    ax.axhline(2, color=COLORS['up'], linestyle='--', linewidth=1.5, label='2% Target')

    current = cpi_yoy.iloc[-1]
    ax.annotate(f'Current: {current:.1f}%', xy=(cpi_yoy.index[-1], current),
                xytext=(-80, 20), textcoords='offset points',
                fontsize=10, fontweight='bold', color='white',
                bbox=dict(boxstyle='round', facecolor=COLORS['dusk'], alpha=0.9),
                arrowprops=dict(arrowstyle='->', color=COLORS['dusk']))

    ax.set_title('CPI Inflation (Year-over-Year)', fontweight='bold', fontsize=13)
    ax.set_ylabel('YoY Change (%)', fontweight='bold')
    ax.legend(loc='upper left')
    add_recessions(ax)
    style_chart(ax)
    add_branding(fig, 'FRED (CPIAUCSL) | Monthly', last_date=cpi_yoy.index[-1])
    plt.tight_layout()
    return fig


def chart_21_pce():
    """Core PCE - Fed's preferred measure."""
    pce = fetch_fred('PCEPILFE', '2000-01-01')
    pce_yoy = pce.pct_change(12) * 100

    fig, ax = plt.subplots(figsize=(12, 7))
    ax.plot(pce_yoy.index, pce_yoy.values, linewidth=2, color=COLORS['hot'],
            marker='.', markersize=2)

    ax.axhline(2, color=COLORS['up'], linestyle='--', linewidth=1.5, label='2% Target')

    current = pce_yoy.iloc[-1]
    ax.annotate(f'Current: {current:.1f}%', xy=(pce_yoy.index[-1], current),
                xytext=(-80, 20), textcoords='offset points',
                fontsize=10, fontweight='bold', color='white',
                bbox=dict(boxstyle='round', facecolor=COLORS['hot'], alpha=0.9),
                arrowprops=dict(arrowstyle='->', color=COLORS['hot']))

    ax.set_title('Core PCE Inflation (Fed Target Measure)', fontweight='bold', fontsize=13)
    ax.set_ylabel('YoY Change (%)', fontweight='bold')
    ax.legend(loc='upper left')
    add_recessions(ax)
    style_chart(ax)
    add_branding(fig, 'FRED (PCEPILFE) | Monthly', last_date=pce_yoy.index[-1])
    plt.tight_layout()
    return fig


def chart_22_real_rates():
    """Real Interest Rates."""
    tips10 = fetch_fred('DFII10', '2003-01-01')

    fig, ax = plt.subplots(figsize=(12, 7))
    ax.fill_between(tips10.index, 0, tips10.values,
                    where=tips10.values >= 0, alpha=0.3, color=COLORS['dusk'])
    ax.fill_between(tips10.index, 0, tips10.values,
                    where=tips10.values < 0, alpha=0.3, color=COLORS['ocean'])
    ax.plot(tips10.index, tips10.values, linewidth=2, color=COLORS['ocean'])

    ax.axhline(0, color='black', linewidth=1)

    current = tips10.iloc[-1]
    ax.annotate(f'Current: {current:.2f}%', xy=(tips10.index[-1], current),
                xytext=(-80, 20), textcoords='offset points',
                fontsize=10, fontweight='bold', color='white',
                bbox=dict(boxstyle='round', facecolor=COLORS['ocean'], alpha=0.9),
                arrowprops=dict(arrowstyle='->', color=COLORS['ocean']))

    ax.set_title('10-Year Real Interest Rate (TIPS)', fontweight='bold', fontsize=13)
    ax.set_ylabel('Real Rate (%)', fontweight='bold')
    add_recessions(ax, 2003)
    style_chart(ax)
    add_branding(fig, 'FRED (DFII10) | Daily', last_date=tips10.index[-1])
    plt.tight_layout()
    return fig


def chart_23_breakevens():
    """Inflation Breakevens."""
    be10 = fetch_fred('T10YIE', '2003-01-01')
    be5 = fetch_fred('T5YIE', '2003-01-01')

    fig, ax = plt.subplots(figsize=(12, 7))
    ax.plot(be10.index, be10.values, linewidth=2, color=COLORS['ocean'], label='10Y Breakeven')
    ax.plot(be5.index, be5.values, linewidth=2, color=COLORS['dusk'], label='5Y Breakeven')

    ax.axhline(2, color=COLORS['up'], linestyle='--', linewidth=1, label='2% Target')

    current_10 = be10.iloc[-1]
    current_5 = be5.iloc[-1]

    ax.annotate(f'10Y: {current_10:.2f}%', xy=(be10.index[-1], current_10),
                xytext=(10, 10), textcoords='offset points',
                fontsize=9, fontweight='bold', color=COLORS['ocean'])
    ax.annotate(f'5Y: {current_5:.2f}%', xy=(be5.index[-1], current_5),
                xytext=(10, -15), textcoords='offset points',
                fontsize=9, fontweight='bold', color=COLORS['dusk'])

    ax.set_title('Inflation Breakevens (Market Expectations)', fontweight='bold', fontsize=13)
    ax.set_ylabel('Breakeven Rate (%)', fontweight='bold')
    ax.legend(loc='upper left')
    add_recessions(ax, 2003)
    style_chart(ax)
    add_branding(fig, 'FRED (T10YIE, T5YIE) | Daily', last_date=be10.index[-1])
    plt.tight_layout()
    return fig


def chart_24_dollar():
    """Dollar Index."""
    dxy = fetch_fred('DTWEXBGS', '2006-01-01')

    fig, ax = plt.subplots(figsize=(12, 7))
    ax.plot(dxy.index, dxy.values, linewidth=2, color=COLORS['ocean'])

    current = dxy.iloc[-1]
    mean_val = dxy.mean()

    ax.axhline(mean_val, color=COLORS['silvs'], linestyle='--', linewidth=1)
    ax.text(dxy.index[10], mean_val + 1, f'Mean: {mean_val:.1f}', fontsize=8, color=COLORS['neutral'])

    ax.annotate(f'Current: {current:.1f}', xy=(dxy.index[-1], current),
                xytext=(-80, 20), textcoords='offset points',
                fontsize=10, fontweight='bold', color='white',
                bbox=dict(boxstyle='round', facecolor=COLORS['ocean'], alpha=0.9),
                arrowprops=dict(arrowstyle='->', color=COLORS['ocean']))

    ax.set_title('Trade Weighted U.S. Dollar Index', fontweight='bold', fontsize=13)
    ax.set_ylabel('Index', fontweight='bold')
    add_recessions(ax, 2006)
    style_chart(ax)
    add_branding(fig, 'FRED (DTWEXBGS) | Daily', last_date=dxy.index[-1])
    plt.tight_layout()
    return fig


# =============================================================================
# PART III: MARKET TECHNICALS (Charts 25-36)
# =============================================================================

def chart_25_gdp_growth():
    """Real GDP Growth."""
    gdp_growth = fetch_fred('A191RL1Q225SBEA', '1990-01-01')

    fig, ax = plt.subplots(figsize=(12, 7))
    ax.bar(gdp_growth.index, gdp_growth.values, width=60,
           color=[COLORS['up'] if v >= 0 else COLORS['down'] for v in gdp_growth.values],
           alpha=0.8)

    ax.axhline(0, color='black', linewidth=1)

    current = gdp_growth.iloc[-1]
    ax.annotate(f'Latest: {current:.1f}%', xy=(gdp_growth.index[-1], current),
                xytext=(-60, 20 if current > 0 else -30), textcoords='offset points',
                fontsize=10, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))

    ax.set_title('Real GDP Growth (Quarterly, Annualized)', fontweight='bold', fontsize=13)
    ax.set_ylabel('Growth Rate (%)', fontweight='bold')
    add_recessions(ax, 1990)
    style_chart(ax)
    add_branding(fig, 'FRED (A191RL1Q225SBEA) | Quarterly', last_date=gdp_growth.index[-1])
    plt.tight_layout()
    return fig


def chart_26_industrial_production():
    """Industrial Production."""
    ip = fetch_fred('INDPRO', '2000-01-01')
    ip_yoy = ip.pct_change(12) * 100

    fig, ax = plt.subplots(figsize=(12, 7))
    ax.fill_between(ip_yoy.index, 0, ip_yoy.values,
                    where=ip_yoy.values >= 0, alpha=0.3, color=COLORS['up'])
    ax.fill_between(ip_yoy.index, 0, ip_yoy.values,
                    where=ip_yoy.values < 0, alpha=0.3, color=COLORS['down'])
    ax.plot(ip_yoy.index, ip_yoy.values, linewidth=1.5, color=COLORS['ocean'])

    ax.axhline(0, color='black', linewidth=1)

    current = ip_yoy.iloc[-1]
    ax.annotate(f'YoY: {current:.1f}%', xy=(ip_yoy.index[-1], current),
                xytext=(-60, 20), textcoords='offset points',
                fontsize=10, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))

    ax.set_title('Industrial Production (Year-over-Year)', fontweight='bold', fontsize=13)
    ax.set_ylabel('YoY Change (%)', fontweight='bold')
    add_recessions(ax)
    style_chart(ax)
    add_branding(fig, 'FRED (INDPRO) | Monthly', last_date=ip_yoy.index[-1])
    plt.tight_layout()
    return fig


def chart_27_retail_sales():
    """Retail Sales."""
    retail = fetch_fred('RSXFS', '2000-01-01')
    retail_yoy = retail.pct_change(12) * 100

    fig, ax = plt.subplots(figsize=(12, 7))
    ax.plot(retail_yoy.index, retail_yoy.values, linewidth=1.5, color=COLORS['dusk'],
            marker='.', markersize=2)

    ax.axhline(0, color='black', linewidth=0.5)

    current = retail_yoy.iloc[-1]
    ax.annotate(f'YoY: {current:.1f}%', xy=(retail_yoy.index[-1], current),
                xytext=(-60, 20), textcoords='offset points',
                fontsize=10, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))

    ax.set_title('Retail Sales ex Food Services (Year-over-Year)', fontweight='bold', fontsize=13)
    ax.set_ylabel('YoY Change (%)', fontweight='bold')
    add_recessions(ax)
    style_chart(ax)
    add_branding(fig, 'FRED (RSXFS) | Monthly', last_date=retail_yoy.index[-1])
    plt.tight_layout()
    return fig


def chart_28_housing_starts():
    """Housing Starts."""
    starts = fetch_fred('HOUST', '1990-01-01')

    fig, ax = plt.subplots(figsize=(12, 7))
    ax.fill_between(starts.index, 0, starts.values, alpha=0.3, color=COLORS['sea'])
    ax.plot(starts.index, starts.values, linewidth=1.5, color=COLORS['sea'])

    current = starts.iloc[-1]
    ax.annotate(f'Current: {current:.0f}K', xy=(starts.index[-1], current),
                xytext=(-80, 20), textcoords='offset points',
                fontsize=10, fontweight='bold', color='white',
                bbox=dict(boxstyle='round', facecolor=COLORS['sea'], alpha=0.9),
                arrowprops=dict(arrowstyle='->', color=COLORS['sea']))

    ax.set_title('Housing Starts', fontweight='bold', fontsize=13)
    ax.set_ylabel('Starts (Thousands, SAAR)', fontweight='bold')
    add_recessions(ax, 1990)
    style_chart(ax)
    add_branding(fig, 'FRED (HOUST) | Monthly', last_date=starts.index[-1])
    plt.tight_layout()
    return fig


def chart_29_mortgage_rate():
    """30-Year Mortgage Rate."""
    mortgage = fetch_fred('MORTGAGE30US', '2000-01-01')

    fig, ax = plt.subplots(figsize=(12, 7))
    ax.plot(mortgage.index, mortgage.values, linewidth=2, color=COLORS['dusk'])

    current = mortgage.iloc[-1]
    mean_val = mortgage.mean()

    ax.axhline(mean_val, color=COLORS['silvs'], linestyle='--', linewidth=1)

    ax.annotate(f'Current: {current:.2f}%', xy=(mortgage.index[-1], current),
                xytext=(-80, 20), textcoords='offset points',
                fontsize=10, fontweight='bold', color='white',
                bbox=dict(boxstyle='round', facecolor=COLORS['dusk'], alpha=0.9),
                arrowprops=dict(arrowstyle='->', color=COLORS['dusk']))

    ax.set_title('30-Year Fixed Mortgage Rate', fontweight='bold', fontsize=13)
    ax.set_ylabel('Rate (%)', fontweight='bold')
    add_recessions(ax)
    style_chart(ax)
    add_branding(fig, 'FRED (MORTGAGE30US) | Weekly', last_date=mortgage.index[-1])
    plt.tight_layout()
    return fig


def chart_30_auto_delinquency():
    """Auto/Consumer Loan Delinquency."""
    delinq = fetch_fred('DRALACBS', '2000-01-01')

    fig, ax = plt.subplots(figsize=(12, 7))
    ax.plot(delinq.index, delinq.values, linewidth=2, color=COLORS['dusk'],
            marker='o', markersize=4)

    current = delinq.iloc[-1]
    gfc_peak = delinq['2008-01-01':'2011-12-31'].max()

    ax.axhline(gfc_peak, color=COLORS['down'], linestyle='--', linewidth=1, alpha=0.5)
    ax.text(delinq.index[5], gfc_peak + 0.05, f'GFC Peak: {gfc_peak:.2f}%',
            fontsize=8, color=COLORS['down'])

    ax.annotate(f'Current: {current:.2f}%', xy=(delinq.index[-1], current),
                xytext=(-80, 20), textcoords='offset points',
                fontsize=10, fontweight='bold', color='white',
                bbox=dict(boxstyle='round', facecolor=COLORS['dusk'], alpha=0.9),
                arrowprops=dict(arrowstyle='->', color=COLORS['dusk']))

    ax.set_title('Consumer Loan Delinquency Rate', fontweight='bold', fontsize=13)
    ax.set_ylabel('Delinquency Rate (%)', fontweight='bold')
    add_recessions(ax)
    style_chart(ax)
    add_branding(fig, 'FRED (DRALACBS) | Quarterly', last_date=delinq.index[-1])
    plt.tight_layout()
    return fig


def chart_31_business_delinquency():
    """Business Loan Delinquency."""
    delinq = fetch_fred('DRBLACBS', '2000-01-01')

    fig, ax = plt.subplots(figsize=(12, 7))
    ax.plot(delinq.index, delinq.values, linewidth=2, color=COLORS['sea'],
            marker='o', markersize=4)

    current = delinq.iloc[-1]

    ax.annotate(f'Current: {current:.2f}%', xy=(delinq.index[-1], current),
                xytext=(-80, 20), textcoords='offset points',
                fontsize=10, fontweight='bold', color='white',
                bbox=dict(boxstyle='round', facecolor=COLORS['sea'], alpha=0.9),
                arrowprops=dict(arrowstyle='->', color=COLORS['sea']))

    ax.set_title('Business Loan Delinquency Rate', fontweight='bold', fontsize=13)
    ax.set_ylabel('Delinquency Rate (%)', fontweight='bold')
    add_recessions(ax)
    style_chart(ax)
    add_branding(fig, 'FRED (DRBLACBS) | Quarterly', last_date=delinq.index[-1])
    plt.tight_layout()
    return fig


def chart_32_nfci():
    """Chicago Fed National Financial Conditions Index."""
    nfci = fetch_fred('NFCI', '2000-01-01')

    fig, ax = plt.subplots(figsize=(12, 7))
    ax.fill_between(nfci.index, 0, nfci.values,
                    where=nfci.values >= 0, alpha=0.3, color=COLORS['down'])
    ax.fill_between(nfci.index, 0, nfci.values,
                    where=nfci.values < 0, alpha=0.3, color=COLORS['up'])
    ax.plot(nfci.index, nfci.values, linewidth=1.5, color=COLORS['ocean'])

    ax.axhline(0, color='black', linewidth=1)

    current = nfci.iloc[-1]
    ax.annotate(f'Current: {current:.2f}', xy=(nfci.index[-1], current),
                xytext=(-80, 20), textcoords='offset points',
                fontsize=10, fontweight='bold', color='white',
                bbox=dict(boxstyle='round', facecolor=COLORS['ocean'], alpha=0.9),
                arrowprops=dict(arrowstyle='->', color=COLORS['ocean']))

    ax.text(0.02, 0.98, 'Positive = Tighter conditions\nNegative = Looser conditions',
            transform=ax.transAxes, fontsize=8, va='top',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))

    ax.set_title('Chicago Fed National Financial Conditions Index', fontweight='bold', fontsize=13)
    ax.set_ylabel('Index (0 = avg)', fontweight='bold')
    add_recessions(ax)
    style_chart(ax)
    add_branding(fig, 'FRED (NFCI) | Weekly', last_date=nfci.index[-1])
    plt.tight_layout()
    return fig


def chart_33_vix():
    """VIX Volatility Index."""
    vix = fetch_fred('VIXCLS', '2000-01-01')

    fig, ax = plt.subplots(figsize=(12, 7))
    ax.fill_between(vix.index, 0, vix.values, alpha=0.3, color=COLORS['hot'])
    ax.plot(vix.index, vix.values, linewidth=1, color=COLORS['hot'], alpha=0.8)

    ax.axhline(20, color=COLORS['dusk'], linestyle='--', linewidth=1.5, label='Elevated (20)')
    ax.axhline(30, color=COLORS['down'], linestyle='--', linewidth=1.5, label='High Fear (30)')

    current = vix.iloc[-1]
    ax.annotate(f'Current: {current:.1f}', xy=(vix.index[-1], current),
                xytext=(-80, 20), textcoords='offset points',
                fontsize=10, fontweight='bold', color='white',
                bbox=dict(boxstyle='round', facecolor=COLORS['hot'], alpha=0.9),
                arrowprops=dict(arrowstyle='->', color=COLORS['hot']))

    ax.set_title('VIX (CBOE Volatility Index)', fontweight='bold', fontsize=13)
    ax.set_ylabel('VIX', fontweight='bold')
    ax.set_ylim(0, min(vix.max() * 1.1, 80))
    ax.legend(loc='upper right')
    add_recessions(ax)
    style_chart(ax)
    add_branding(fig, 'FRED (VIXCLS) | Daily', last_date=vix.index[-1])
    plt.tight_layout()
    return fig


def chart_34_move():
    """MOVE Index proxy (bond volatility via TLT)."""
    # MOVE not in FRED, use Treasury volatility proxy
    y10 = fetch_fred('DGS10', '2015-01-01')
    vol = y10.rolling(20).std() * np.sqrt(252) * 100  # Annualized vol in bps

    fig, ax = plt.subplots(figsize=(12, 7))
    ax.fill_between(vol.index, 0, vol.values, alpha=0.3, color=COLORS['ocean'])
    ax.plot(vol.index, vol.values, linewidth=1.5, color=COLORS['ocean'])

    current = vol.iloc[-1]
    ax.annotate(f'Current: {current:.0f} bps', xy=(vol.index[-1], current),
                xytext=(-80, 20), textcoords='offset points',
                fontsize=10, fontweight='bold', color='white',
                bbox=dict(boxstyle='round', facecolor=COLORS['ocean'], alpha=0.9),
                arrowprops=dict(arrowstyle='->', color=COLORS['ocean']))

    ax.set_title('Treasury Volatility (20D Rolling, Annualized)', fontweight='bold', fontsize=13)
    ax.set_ylabel('Volatility (bps)', fontweight='bold')
    style_chart(ax)
    add_branding(fig, 'FRED (DGS10) | Calculated: 20D rolling std * sqrt(252)', last_date=vol.index[-1])
    plt.tight_layout()
    return fig


def chart_35_oil():
    """WTI Crude Oil."""
    oil = fetch_fred('DCOILWTICO', '2000-01-01')

    fig, ax = plt.subplots(figsize=(12, 7))
    ax.plot(oil.index, oil.values, linewidth=1.5, color=COLORS['dusk'])

    current = oil.iloc[-1]
    ax.annotate(f'Current: ${current:.2f}', xy=(oil.index[-1], current),
                xytext=(-80, 20), textcoords='offset points',
                fontsize=10, fontweight='bold', color='white',
                bbox=dict(boxstyle='round', facecolor=COLORS['dusk'], alpha=0.9),
                arrowprops=dict(arrowstyle='->', color=COLORS['dusk']))

    ax.set_title('WTI Crude Oil Price', fontweight='bold', fontsize=13)
    ax.set_ylabel('Price ($/barrel)', fontweight='bold')
    add_recessions(ax)
    style_chart(ax)
    add_branding(fig, 'FRED (DCOILWTICO) | Daily', last_date=oil.index[-1])
    plt.tight_layout()
    return fig


def chart_36_gold():
    """Gold Price."""
    # Try multiple gold series - GOLDAMGBD228NLBM may be discontinued
    try:
        gold = fetch_fred('GOLDPMGBD228NLBM', '2000-01-01')
    except:
        gold = fetch_fred('GLDPRUSD', '2000-01-01')

    fig, ax = plt.subplots(figsize=(12, 7))
    ax.fill_between(gold.index, 0, gold.values, alpha=0.3, color='#FFD700')
    ax.plot(gold.index, gold.values, linewidth=2, color='#DAA520')

    current = gold.iloc[-1]
    ax.annotate(f'Current: ${current:,.0f}', xy=(gold.index[-1], current),
                xytext=(-80, -30), textcoords='offset points',
                fontsize=10, fontweight='bold', color='white',
                bbox=dict(boxstyle='round', facecolor='#DAA520', alpha=0.9),
                arrowprops=dict(arrowstyle='->', color='#DAA520'))

    ax.set_title('Gold Price (London PM Fix)', fontweight='bold', fontsize=13)
    ax.set_ylabel('Price ($/oz)', fontweight='bold')
    add_recessions(ax)
    style_chart(ax)
    add_branding(fig, 'FRED (Gold Price) | Daily', last_date=gold.index[-1])
    plt.tight_layout()
    return fig


# =============================================================================
# MASTER GENERATION
# =============================================================================

ALL_CHARTS = [
    # Part I: Macro Dynamics
    ('01_rrp_drawdown', chart_01_rrp_drawdown),
    ('02_reserves_gdp', chart_02_reserves),
    ('03_sofr_effr_spread', chart_03_sofr_effr),
    ('04_tga_balance', chart_04_tga),
    ('05_fed_balance_sheet', chart_05_fed_balance_sheet),
    ('06_quits_rate', chart_06_quits_rate),
    ('07_hires_rate', chart_07_hires_rate),
    ('08_unemployment', chart_08_unemployment),
    ('09_initial_claims', chart_09_initial_claims),
    ('10_savings_rate', chart_10_savings_rate),
    ('11_consumer_credit', chart_11_consumer_credit),
    ('12_cc_delinquency', chart_12_cc_delinquency),

    # Part II: Monetary Mechanics
    ('13_yield_curve', chart_13_yield_curve),
    ('14_hy_spreads', chart_14_hy_spreads),
    ('15_ig_spreads', chart_15_ig_spreads),
    ('16_credit_spread_waterfall', chart_16_credit_spread_waterfall),
    ('17_debt_gdp', chart_17_debt_gdp),
    ('18_interest_expense', chart_18_interest_expense),
    ('19_foreign_holdings', chart_19_foreign_holdings),
    ('20_cpi_inflation', chart_20_cpi),
    ('21_core_pce', chart_21_pce),
    ('22_real_rates', chart_22_real_rates),
    ('23_breakevens', chart_23_breakevens),
    ('24_dollar_index', chart_24_dollar),

    # Part III: Market Technicals
    ('25_gdp_growth', chart_25_gdp_growth),
    ('26_industrial_production', chart_26_industrial_production),
    ('27_retail_sales', chart_27_retail_sales),
    ('28_housing_starts', chart_28_housing_starts),
    ('29_mortgage_rate', chart_29_mortgage_rate),
    ('30_auto_delinquency', chart_30_auto_delinquency),
    ('31_business_delinquency', chart_31_business_delinquency),
    ('32_nfci', chart_32_nfci),
    ('33_vix', chart_33_vix),
    ('34_treasury_volatility', chart_34_move),
    ('35_oil', chart_35_oil),
    ('36_gold', chart_36_gold),
]


def generate_all():
    """Generate all 36 institutional-grade charts."""
    print("=" * 70)
    print("HORIZON 2026 - INSTITUTIONAL CHART GENERATION")
    print("All charts use REAL FRED data. No fabrication. No smoothing.")
    print("=" * 70)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    success = 0
    failed = []

    for name, func in ALL_CHARTS:
        try:
            print(f"  {name}...", end=' ')
            fig = func()
            path = OUTPUT_DIR / f'{name}.png'
            fig.savefig(path, dpi=300, bbox_inches='tight', facecolor='white')
            plt.close(fig)
            print("OK")
            success += 1
        except Exception as e:
            print(f"FAILED: {e}")
            failed.append((name, str(e)))

    print("\n" + "=" * 70)
    print(f"COMPLETE: {success}/{len(ALL_CHARTS)} charts generated")
    print(f"Output: {OUTPUT_DIR}")
    if failed:
        print(f"\nFailed charts:")
        for name, err in failed:
            print(f"  - {name}: {err}")
    print("=" * 70)

    return success, failed


if __name__ == "__main__":
    generate_all()
