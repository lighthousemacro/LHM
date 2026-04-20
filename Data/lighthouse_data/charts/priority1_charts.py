"""
Priority 1 Charts for The Horizon Report
Lighthouse Macro - January 2026

Charts:
1. TGA Balance History
2. Fed Balance Sheet vs Reserve Adequacy
3. MOVE Index vs VIX
4. Money Market Fund Flows
5. Bank Lending Standards (SLOOS)
6. Real Rates & Breakevens
7. Dollar Index vs Foreign Demand
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from matplotlib.ticker import FuncFormatter
from pathlib import Path
from datetime import datetime

from ..config import CONFIG
from ..collect.fred_extended import (
    get_tga_history,
    get_fed_balance_sheet,
    get_real_rates,
    get_sloos_data,
    get_mmf_flows,
    update_fred_extended,
)
from ..collect.volatility import get_vix_move_analysis, update_volatility_raw
from ..utils.logging import get_logger

log = get_logger(__name__)

# === LIGHTHOUSE MACRO COLORS ===
COLORS = {
    'ocean_blue': '#2389BB',
    'dusk_orange': '#FF6723',
    'electric_cyan': '#03DDFF',
    'hot_magenta': '#FF00F0',
    'sea_teal': '#289389',
    'silvs_gray': '#D1D1D1',
    'up_green': '#008000',
    'down_red': '#FF3333',
    'neutral': '#808080',
    'black': '#000000',
}

# Chart output directory
CHART_DIR = CONFIG.base_dir / "charts" / "priority1"


def setup_chart_style():
    """Apply Lighthouse Macro chart styling."""
    plt.rcParams.update({
        'font.family': 'sans-serif',
        'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans'],
        'font.size': 10,
        'axes.titlesize': 14,
        'axes.labelsize': 11,
        'axes.titleweight': 'bold',
        'figure.figsize': (11, 8.5),
        'figure.dpi': 150,
        'axes.grid': False,
        'axes.spines.top': False,
        'axes.spines.right': False,
        'axes.edgecolor': COLORS['neutral'],
        'xtick.color': COLORS['neutral'],
        'ytick.color': COLORS['neutral'],
    })


def add_branding(fig, ax, chart_number, source='FRED'):
    """Add Lighthouse Macro branding to chart."""
    ax.grid(False)

    # Chart number badge
    circle = Circle((0.02, 0.98), 0.015, transform=ax.transAxes,
                    facecolor=COLORS['ocean_blue'], edgecolor='none', zorder=100)
    ax.add_patch(circle)
    ax.text(0.02, 0.98, str(chart_number),
            ha='center', va='center', fontsize=10, fontweight='bold',
            color='white', transform=ax.transAxes, zorder=101)

    ax.text(0.045, 0.98, 'LIGHTHOUSE MACRO',
            ha='left', va='center', fontsize=9, fontweight='bold',
            color=COLORS['ocean_blue'], transform=ax.transAxes)

    fig.text(0.02, 0.02, f'Source: {source}',
             ha='left', va='bottom', fontsize=7, color=COLORS['neutral'],
             style='italic')

    fig.text(0.98, 0.02, 'MACRO, ILLUMINATED.',
             ha='right', va='bottom', fontsize=8, fontweight='bold',
             color=COLORS['ocean_blue'], alpha=0.6)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color(COLORS['neutral'])
    ax.spines['bottom'].set_color(COLORS['neutral'])


def add_last_value(ax, series, color, side='right', fmt='{:.1f}'):
    """Add last value annotation."""
    if len(series.dropna()) == 0:
        return
    last_val = series.dropna().iloc[-1]
    x_pos = 1.01 if side == 'right' else -0.01
    ha = 'left' if side == 'right' else 'right'

    ax.text(x_pos, last_val, fmt.format(last_val),
            transform=ax.get_yaxis_transform(),
            ha=ha, va='center', fontsize=9,
            color=color, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                      edgecolor=color, linewidth=1.5))


def billions_formatter(x, pos):
    """Format axis in billions."""
    return f'${x/1e3:.1f}T' if x >= 1000 else f'${x:.0f}B'


# ============================================================
# CHART 1: TGA BALANCE HISTORY
# ============================================================
def chart_tga_balance(save=True) -> plt.Figure:
    """
    TGA Balance History - Treasury cash volatility as liquidity lever.

    Shows:
    - TGA balance over time
    - Key events (debt ceiling episodes, QT periods)
    - Current level vs historical range
    """
    setup_chart_style()
    log.info("Generating TGA Balance History chart...")

    df = get_tga_history()
    if df.empty:
        log.error("No TGA data available")
        return None

    # Convert to billions
    df['TGA_Billions'] = df['TGA_Balance'] / 1e6

    # Filter to recent history (2015+)
    df = df[df.index >= '2015-01-01']

    fig, ax = plt.subplots(figsize=(11, 8.5))

    # Main line
    ax.plot(df.index, df['TGA_Billions'], color=COLORS['ocean_blue'],
            linewidth=2, label='TGA Balance')

    # Fill area
    ax.fill_between(df.index, df['TGA_Billions'], alpha=0.2,
                    color=COLORS['ocean_blue'])

    # Reference lines
    median_tga = df['TGA_Billions'].median()
    ax.axhline(median_tga, color=COLORS['silvs_gray'], linestyle='--',
               linewidth=1, alpha=0.7, label=f'Median: ${median_tga:.0f}B')

    # Debt ceiling danger zone (typically when TGA < $100B)
    ax.axhline(100, color=COLORS['down_red'], linestyle=':', linewidth=1.5,
               alpha=0.8, label='Danger Zone (<$100B)')

    # Annotations for key events
    events = [
        ('2019-09-17', 'Repo Crisis'),
        ('2021-07-31', 'Debt Ceiling'),
        ('2023-05-01', 'Debt Ceiling'),
    ]
    for date, label in events:
        try:
            event_date = pd.Timestamp(date)
            if event_date in df.index:
                val = df.loc[event_date, 'TGA_Billions']
            else:
                val = df.loc[df.index.asof(event_date), 'TGA_Billions']
            ax.annotate(label, xy=(event_date, val),
                        xytext=(10, 20), textcoords='offset points',
                        fontsize=8, color=COLORS['neutral'],
                        arrowprops=dict(arrowstyle='->', color=COLORS['neutral']))
        except:
            pass

    ax.set_title('Treasury General Account (TGA) Balance\nLiquidity Lever for Fiscal Operations',
                 fontsize=14, fontweight='bold', pad=15)
    ax.set_ylabel('Balance ($B)', fontsize=11, fontweight='bold')
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'${x:.0f}B'))

    ax.margins(x=0)
    ax.legend(loc='upper left', fontsize=9, framealpha=0.95)

    add_last_value(ax, df['TGA_Billions'], COLORS['ocean_blue'], fmt='${:.0f}B')
    add_branding(fig, ax, 'P1.1', source='FRED (WTREGEN)')

    plt.tight_layout()

    if save:
        CHART_DIR.mkdir(parents=True, exist_ok=True)
        out_path = CHART_DIR / "chart_tga_balance.png"
        plt.savefig(out_path, dpi=300, bbox_inches='tight')
        log.info(f"Saved: {out_path}")

    return fig


# ============================================================
# CHART 2: FED BALANCE SHEET VS RESERVE ADEQUACY
# ============================================================
def chart_fed_balance_sheet(save=True) -> plt.Figure:
    """
    Fed Balance Sheet vs Reserve Adequacy.

    Shows:
    - Total Fed assets
    - Bank reserves
    - RRP balance
    - Reserve adequacy threshold
    """
    setup_chart_style()
    log.info("Generating Fed Balance Sheet chart...")

    df = get_fed_balance_sheet()
    if df.empty:
        log.error("No Fed balance sheet data available")
        return None

    # Convert to trillions
    for col in df.columns:
        df[col] = df[col] / 1e6  # Millions to trillions

    # Filter to QE/QT era (2008+)
    df = df[df.index >= '2008-01-01']

    fig, ax = plt.subplots(figsize=(11, 8.5))

    # Stacked area for liabilities
    ax.fill_between(df.index, 0, df['Reserves'],
                    color=COLORS['ocean_blue'], alpha=0.7, label='Bank Reserves')
    ax.fill_between(df.index, df['Reserves'], df['Reserves'] + df['RRP'],
                    color=COLORS['dusk_orange'], alpha=0.7, label='RRP')
    ax.fill_between(df.index, df['Reserves'] + df['RRP'],
                    df['Reserves'] + df['RRP'] + df['TGA'],
                    color=COLORS['sea_teal'], alpha=0.7, label='TGA')

    # Total assets line
    ax.plot(df.index, df['Total_Assets'], color=COLORS['black'],
            linewidth=2, label='Total Assets')

    # Reserve adequacy threshold (~$3T)
    ax.axhline(3.0, color=COLORS['down_red'], linestyle='--', linewidth=1.5,
               label='Reserve Adequacy (~$3T)')

    ax.set_title('Federal Reserve Balance Sheet Composition\nRRP Offset to QT Now Exhausted',
                 fontsize=14, fontweight='bold', pad=15)
    ax.set_ylabel('Trillions ($)', fontsize=11, fontweight='bold')
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'${x:.1f}T'))

    ax.margins(x=0)
    ax.legend(loc='upper left', fontsize=9, framealpha=0.95)

    add_branding(fig, ax, 'P1.2', source='FRED (WALCL, WRESBAL, RRPONTSYD, WTREGEN)')

    plt.tight_layout()

    if save:
        CHART_DIR.mkdir(parents=True, exist_ok=True)
        out_path = CHART_DIR / "chart_fed_balance_sheet.png"
        plt.savefig(out_path, dpi=300, bbox_inches='tight')
        log.info(f"Saved: {out_path}")

    return fig


# ============================================================
# CHART 3: MOVE INDEX VS VIX
# ============================================================
def chart_move_vs_vix(save=True) -> plt.Figure:
    """
    MOVE Index vs VIX - Rates vol leading equity vol.

    Shows:
    - VIX (equity volatility)
    - MOVE proxy (Treasury volatility)
    - Correlation regime
    """
    setup_chart_style()
    log.info("Generating MOVE vs VIX chart...")

    df = get_vix_move_analysis()
    if df.empty:
        log.error("No volatility data available")
        return None

    # Filter to recent history
    df = df[df.index >= '2015-01-01']

    fig, ax_left = plt.subplots(figsize=(11, 8.5))
    ax_right = ax_left.twinx()

    # Ensure no gridlines on both axes
    ax_left.grid(False)
    ax_right.grid(False)

    # MOVE on left (secondary)
    ax_left.plot(df.index, df['MOVE_Proxy'], color=COLORS['dusk_orange'],
                 linewidth=1.5, alpha=0.8, label='MOVE Proxy (Treasury Vol)')
    ax_left.fill_between(df.index, df['MOVE_Proxy'], alpha=0.1,
                         color=COLORS['dusk_orange'])

    # VIX on right (primary)
    ax_right.plot(df.index, df['VIX'], color=COLORS['ocean_blue'],
                  linewidth=2, label='VIX')

    # Stress thresholds
    ax_right.axhline(20, color=COLORS['silvs_gray'], linestyle='--',
                     linewidth=1, alpha=0.5)
    ax_right.axhline(30, color=COLORS['down_red'], linestyle='--',
                     linewidth=1, alpha=0.5, label='VIX Stress (>30)')

    ax_left.set_title('Rates Volatility (MOVE) vs Equity Volatility (VIX)\nRates Vol Often Leads Equity Vol',
                      fontsize=14, fontweight='bold', pad=15)
    ax_left.set_ylabel('MOVE Proxy', fontsize=10, color=COLORS['dusk_orange'])
    ax_right.set_ylabel('VIX', fontsize=11, color=COLORS['ocean_blue'], fontweight='bold')

    ax_left.tick_params(axis='y', labelcolor=COLORS['dusk_orange'])
    ax_right.tick_params(axis='y', labelcolor=COLORS['ocean_blue'])

    ax_left.margins(x=0)

    # Combined legend
    lines1, labels1 = ax_left.get_legend_handles_labels()
    lines2, labels2 = ax_right.get_legend_handles_labels()
    ax_left.legend(lines1 + lines2, labels1 + labels2, loc='upper left',
                   fontsize=9, framealpha=0.95)

    # Style right axis
    ax_right.spines['left'].set_visible(False)
    ax_right.spines['top'].set_visible(False)
    ax_right.spines['right'].set_color(COLORS['neutral'])
    ax_right.spines['bottom'].set_color(COLORS['neutral'])

    add_last_value(ax_right, df['VIX'], COLORS['ocean_blue'], side='right', fmt='{:.1f}')
    add_branding(fig, ax_left, 'P1.3', source='CBOE, ICE BofA (proxy)')

    plt.tight_layout()

    if save:
        CHART_DIR.mkdir(parents=True, exist_ok=True)
        out_path = CHART_DIR / "chart_move_vs_vix.png"
        plt.savefig(out_path, dpi=300, bbox_inches='tight')
        log.info(f"Saved: {out_path}")

    return fig


# ============================================================
# CHART 4: MONEY MARKET FUND FLOWS
# ============================================================
def chart_mmf_flows(save=True) -> plt.Figure:
    """
    Money Market Fund Flows - Where RRP cash migrated.

    Shows:
    - Retail vs Institutional MMF assets
    - 4-week flow momentum
    - RRP drain correlation
    """
    setup_chart_style()
    log.info("Generating MMF Flows chart...")

    df = get_mmf_flows()
    if df.empty:
        log.error("No MMF data available")
        return None

    # Convert to trillions
    for col in ['Retail_MMF', 'Inst_MMF', 'Total_MMF']:
        if col in df.columns:
            df[col] = df[col] / 1e6

    # Filter to recent
    df = df[df.index >= '2018-01-01']

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 10), height_ratios=[2, 1])

    # Top panel: Stacked area of MMF assets
    ax1.grid(False)
    ax1.fill_between(df.index, 0, df['Retail_MMF'],
                     color=COLORS['ocean_blue'], alpha=0.7, label='Retail MMF')
    ax1.fill_between(df.index, df['Retail_MMF'], df['Total_MMF'],
                     color=COLORS['dusk_orange'], alpha=0.7, label='Institutional MMF')

    ax1.set_title('Money Market Fund Assets\nWhere RRP Cash Migrated',
                  fontsize=14, fontweight='bold', pad=15)
    ax1.set_ylabel('Total Assets ($T)', fontsize=11, fontweight='bold')
    ax1.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'${x:.1f}T'))
    ax1.margins(x=0)
    ax1.legend(loc='upper left', fontsize=9, framealpha=0.95)

    # Bottom panel: 4-week flows
    ax2.grid(False)
    if 'MMF_4W_Flow' in df.columns:
        flow = df['MMF_4W_Flow'] / 1e3  # Convert to billions
        colors = [COLORS['up_green'] if x > 0 else COLORS['down_red'] for x in flow]
        ax2.bar(df.index, flow, color=colors, alpha=0.7, width=7)

    ax2.axhline(0, color=COLORS['neutral'], linewidth=1)
    ax2.set_ylabel('4-Week Flow ($B)', fontsize=10)
    ax2.margins(x=0)

    add_branding(fig, ax1, 'P1.4', source='FRED (WRMFSL, WIMFSL)')

    plt.tight_layout()

    if save:
        CHART_DIR.mkdir(parents=True, exist_ok=True)
        out_path = CHART_DIR / "chart_mmf_flows.png"
        plt.savefig(out_path, dpi=300, bbox_inches='tight')
        log.info(f"Saved: {out_path}")

    return fig


# ============================================================
# CHART 5: BANK LENDING STANDARDS (SLOOS)
# ============================================================
def chart_sloos(save=True) -> plt.Figure:
    """
    Bank Lending Standards (SLOOS) - Credit tightening evidence.

    Shows:
    - Net % of banks tightening standards for C&I loans
    - Consumer credit card standards
    - Recession shading
    """
    setup_chart_style()
    log.info("Generating SLOOS chart...")

    df = get_sloos_data()
    if df.empty:
        log.error("No SLOOS data available")
        return None

    # Filter to modern era
    df = df[df.index >= '2000-01-01']

    fig, ax = plt.subplots(figsize=(11, 8.5))

    # C&I Loans to Large Firms
    if 'CandI_Large_Tightening' in df.columns:
        ax.plot(df.index, df['CandI_Large_Tightening'], color=COLORS['ocean_blue'],
                linewidth=2, label='C&I Loans (Large Firms)')

    # C&I Loans to Small Firms
    if 'CandI_Small_Tightening' in df.columns:
        ax.plot(df.index, df['CandI_Small_Tightening'], color=COLORS['dusk_orange'],
                linewidth=2, label='C&I Loans (Small Firms)')

    # Consumer Credit Cards
    if 'Consumer_CC_Tightening' in df.columns:
        ax.plot(df.index, df['Consumer_CC_Tightening'], color=COLORS['sea_teal'],
                linewidth=1.5, linestyle='--', label='Consumer Credit Cards')

    # Reference lines
    ax.axhline(0, color=COLORS['neutral'], linewidth=1)
    ax.axhline(40, color=COLORS['down_red'], linestyle=':', linewidth=1,
               alpha=0.7, label='Recession Warning (>40%)')

    # Shade recession periods
    recessions = [
        ('2001-03-01', '2001-11-01'),
        ('2007-12-01', '2009-06-01'),
        ('2020-02-01', '2020-04-01'),
    ]
    for start, end in recessions:
        ax.axvspan(pd.Timestamp(start), pd.Timestamp(end),
                   color=COLORS['silvs_gray'], alpha=0.3)

    ax.set_title('Senior Loan Officer Survey (SLOOS)\nNet % of Banks Tightening Lending Standards',
                 fontsize=14, fontweight='bold', pad=15)
    ax.set_ylabel('Net % Tightening', fontsize=11, fontweight='bold')

    ax.margins(x=0)
    ax.legend(loc='upper left', fontsize=9, framealpha=0.95)

    add_branding(fig, ax, 'P1.5', source='FRED (DRTSCILM, DRTSCLCC)')

    plt.tight_layout()

    if save:
        CHART_DIR.mkdir(parents=True, exist_ok=True)
        out_path = CHART_DIR / "chart_sloos.png"
        plt.savefig(out_path, dpi=300, bbox_inches='tight')
        log.info(f"Saved: {out_path}")

    return fig


# ============================================================
# CHART 6: REAL RATES & BREAKEVENS
# ============================================================
def chart_real_rates(save=True) -> plt.Figure:
    """
    Real Rates & Inflation Breakevens - Inflation expectations regime.

    Shows:
    - 10Y nominal vs real yield
    - 10Y breakeven inflation
    - 5Y5Y forward expectations
    """
    setup_chart_style()
    log.info("Generating Real Rates chart...")

    df = get_real_rates()
    if df.empty:
        log.error("No real rates data available")
        return None

    # Filter to recent
    df = df[df.index >= '2010-01-01']

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 10), height_ratios=[1.5, 1])

    # Top panel: Nominal vs Real 10Y
    ax1.grid(False)
    if 'Nominal_10Y' in df.columns:
        ax1.plot(df.index, df['Nominal_10Y'], color=COLORS['ocean_blue'],
                 linewidth=2, label='Nominal 10Y')
    if 'Real_10Y' in df.columns:
        ax1.plot(df.index, df['Real_10Y'], color=COLORS['dusk_orange'],
                 linewidth=2, label='Real 10Y (TIPS)')

    ax1.axhline(0, color=COLORS['neutral'], linewidth=1, linestyle='--')

    ax1.set_title('Treasury Yields: Nominal vs Real\nReal Rates Drive Financial Conditions',
                  fontsize=14, fontweight='bold', pad=15)
    ax1.set_ylabel('Yield (%)', fontsize=11, fontweight='bold')
    ax1.margins(x=0)
    ax1.legend(loc='upper left', fontsize=9, framealpha=0.95)

    # Bottom panel: Breakevens
    ax2.grid(False)
    if 'Breakeven_10Y' in df.columns:
        ax2.plot(df.index, df['Breakeven_10Y'], color=COLORS['hot_magenta'],
                 linewidth=2, label='10Y Breakeven')
    if 'Forward_5Y5Y' in df.columns:
        ax2.plot(df.index, df['Forward_5Y5Y'], color=COLORS['sea_teal'],
                 linewidth=1.5, linestyle='--', label='5Y5Y Forward')

    # Fed target zone
    ax2.axhline(2.0, color=COLORS['down_red'], linestyle=':', linewidth=1,
                alpha=0.7, label='Fed Target (2%)')
    ax2.axhspan(2.0, 2.5, color=COLORS['up_green'], alpha=0.1)

    ax2.set_ylabel('Breakeven Inflation (%)', fontsize=10)
    ax2.margins(x=0)
    ax2.legend(loc='upper left', fontsize=9, framealpha=0.95)

    add_branding(fig, ax1, 'P1.6', source='FRED (DGS10, DFII10, T10YIE, T5YIFR)')

    plt.tight_layout()

    if save:
        CHART_DIR.mkdir(parents=True, exist_ok=True)
        out_path = CHART_DIR / "chart_real_rates.png"
        plt.savefig(out_path, dpi=300, bbox_inches='tight')
        log.info(f"Saved: {out_path}")

    return fig


# ============================================================
# CHART 7: DOLLAR INDEX VS FOREIGN DEMAND
# ============================================================
def chart_dollar_index(save=True) -> plt.Figure:
    """
    Dollar Index vs Foreign Demand - USD funding demand connection.

    Shows:
    - Trade-weighted USD
    - Foreign official Treasury holdings (from TIC data)
    """
    setup_chart_style()
    log.info("Generating Dollar Index chart...")

    # Fetch dollar data from extended FRED
    from ..utils.io import read_parquet
    fred_path = CONFIG.raw_dir / "fred" / "fred_extended.parquet"

    if fred_path.exists():
        df = read_parquet(fred_path)
    else:
        df = update_fred_extended()

    if df.empty or 'Trade_Weighted_USD' not in df.columns:
        log.error("No dollar index data available")
        return None

    # Filter to recent
    df = df[df.index >= '2015-01-01']

    fig, ax = plt.subplots(figsize=(11, 8.5))

    # Trade-weighted USD
    ax.plot(df.index, df['Trade_Weighted_USD'], color=COLORS['ocean_blue'],
            linewidth=2, label='Trade-Weighted USD (Broad)')

    # Add USD vs Advanced economies if available
    if 'USD_vs_AFE' in df.columns:
        ax.plot(df.index, df['USD_vs_AFE'], color=COLORS['dusk_orange'],
                linewidth=1.5, linestyle='--', alpha=0.7,
                label='USD vs Advanced Economies')

    # USD vs Emerging markets if available
    if 'USD_vs_EME' in df.columns:
        ax.plot(df.index, df['USD_vs_EME'], color=COLORS['sea_teal'],
                linewidth=1.5, linestyle=':', alpha=0.7,
                label='USD vs Emerging Markets')

    ax.set_title('Trade-Weighted U.S. Dollar Index\nStrong Dollar = Tight Global Financial Conditions',
                 fontsize=14, fontweight='bold', pad=15)
    ax.set_ylabel('Index Level', fontsize=11, fontweight='bold')

    ax.margins(x=0)
    ax.legend(loc='upper left', fontsize=9, framealpha=0.95)

    add_last_value(ax, df['Trade_Weighted_USD'], COLORS['ocean_blue'], fmt='{:.1f}')
    add_branding(fig, ax, 'P1.7', source='FRED (DTWEXBGS)')

    plt.tight_layout()

    if save:
        CHART_DIR.mkdir(parents=True, exist_ok=True)
        out_path = CHART_DIR / "chart_dollar_index.png"
        plt.savefig(out_path, dpi=300, bbox_inches='tight')
        log.info(f"Saved: {out_path}")

    return fig


# ============================================================
# GENERATE ALL PRIORITY 1 CHARTS
# ============================================================
def generate_all_priority1_charts():
    """Generate all Priority 1 charts."""
    log.info("=" * 50)
    log.info("GENERATING ALL PRIORITY 1 CHARTS")
    log.info("=" * 50)

    charts = [
        ("TGA Balance", chart_tga_balance),
        ("Fed Balance Sheet", chart_fed_balance_sheet),
        ("MOVE vs VIX", chart_move_vs_vix),
        ("MMF Flows", chart_mmf_flows),
        ("SLOOS", chart_sloos),
        ("Real Rates", chart_real_rates),
        ("Dollar Index", chart_dollar_index),
    ]

    results = {}
    for name, func in charts:
        try:
            log.info(f"\nGenerating: {name}")
            fig = func(save=True)
            results[name] = "Success" if fig else "No data"
            if fig:
                plt.close(fig)
        except Exception as e:
            log.error(f"Failed to generate {name}: {e}")
            results[name] = f"Error: {e}"

    log.info("\n" + "=" * 50)
    log.info("PRIORITY 1 CHART GENERATION COMPLETE")
    log.info("=" * 50)
    for name, status in results.items():
        log.info(f"  {name}: {status}")

    return results


if __name__ == "__main__":
    generate_all_priority1_charts()
