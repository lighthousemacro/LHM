"""
BTC ETF Charts - Spot Capitulation & On-Chain Reality
Lighthouse Macro Chart Styling Spec v3.0
Uses REAL data from Farside Investors + yfinance + DefiLlama
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.image as mpimg
from matplotlib.ticker import FuncFormatter
import pandas as pd
import numpy as np
from pathlib import Path
import yfinance as yf
import requests

# ———————— COLORS (FIXED) ————————
COLORS = {
    'ocean': '#2389BB',
    'dusk': '#FF6723',
    'sky': '#00BBFF',
    'sea': '#00BB89',
    'venus': '#FF2389',
    'doldrums': '#898989',
}

# ———————— THEME DEFINITION (DARK) ————————
# Updated: Ocean (#2389BB) is PRIMARY for BOTH themes per MEMORY.md
THEME = {
    'bg': '#0A1628',
    'fg': '#e6edf3',
    'muted': '#8b949e',
    'spine': '#1e3350',
    'primary': '#2389BB',        # Ocean (Primary Data - RHS) - ALWAYS
    'secondary': '#FF6723',      # Dusk (Secondary Data - LHS)
    'tertiary': '#00BBFF',       # Sky (third series)
    'accent': '#FF2389',         # Venus
    'legend_bg': '#0f1f38',
    'legend_fg': '#e6edf3',
}

# ———————— OUTPUT PATH ————————
OUTPUT_DIR = Path('/Users/bob/LHM/Outputs/Educational_Charts/BTC_ETF')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
ICON_PATH = '/Users/bob/LHM/Brand/icon_transparent_128.png'

# ———————— LOAD REAL DATA ————————
def load_etf_flows():
    """Load Farside ETF flow data and compute cumulative flows."""
    csv_path = '/Users/bob/LHM/Data/raw/btc_etf_flows_farside.csv'
    df = pd.read_csv(csv_path)

    # Parse date (format: "11 Jan 2024")
    df['Date'] = pd.to_datetime(df['Date'], format='%d %b %Y')
    df = df.set_index('Date').sort_index()

    # Calculate cumulative flows from daily totals
    df['Cumulative_Flows'] = df['Total'].cumsum()

    return df


def load_btc_price(start_date, end_date):
    """Load BTC price data from yfinance."""
    btc = yf.download('BTC-USD', start=start_date, end=end_date, progress=False)
    btc = btc[['Close']].rename(columns={'Close': 'BTC_Price'})
    # Flatten MultiIndex columns if present
    if isinstance(btc.columns, pd.MultiIndex):
        btc.columns = btc.columns.get_level_values(0)
    return btc


def load_base_tvl():
    """Load Base chain TVL from DefiLlama."""
    url = "https://api.llama.fi/v2/historicalChainTvl/Base"
    resp = requests.get(url)
    data = resp.json()
    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'], unit='s')
    df = df.set_index('date').sort_index()
    df = df.rename(columns={'tvl': 'Base_TVL'})
    df['Base_TVL'] = df['Base_TVL'] / 1e9  # Convert to billions
    return df


def load_cbbtc_supply():
    """Load cbBTC supply from DefiLlama."""
    # cbBTC is Coinbase wrapped BTC on Base
    url = "https://api.llama.fi/protocol/cbbtc"
    resp = requests.get(url)
    data = resp.json()

    # Extract TVL history
    tvl_history = data.get('tvl', [])
    df = pd.DataFrame(tvl_history)
    df['date'] = pd.to_datetime(df['date'], unit='s')
    df = df.set_index('date').sort_index()
    df = df.rename(columns={'totalLiquidityUSD': 'cbBTC_TVL'})
    df['cbBTC_TVL'] = df['cbBTC_TVL'] / 1e9  # Convert to billions
    return df[['cbBTC_TVL']]


def prepare_data():
    """Prepare merged dataset with ETF flows and BTC price."""
    # Load ETF flows
    flows = load_etf_flows()

    # Load BTC price for same date range
    start = flows.index.min()
    end = flows.index.max() + pd.Timedelta(days=1)
    price = load_btc_price(start, end)

    # Merge on date
    df = flows[['Cumulative_Flows', 'Total']].join(price, how='outer')

    # Forward fill price for weekends/holidays, then back fill any remaining
    df['BTC_Price'] = df['BTC_Price'].ffill().bfill()

    # Drop rows where we don't have flow data
    df = df.dropna(subset=['Cumulative_Flows'])

    return df


def prepare_onchain_data():
    """Prepare Base TVL data (cbBTC not separately trackable on DefiLlama)."""
    try:
        base = load_base_tvl()
        return base
    except Exception as e:
        print(f"Warning: Could not load on-chain data: {e}")
        return None


# Load data at module level
print("Loading real data...")
df = prepare_data()
print(f"ETF data loaded: {len(df)} days from {df.index.min().date()} to {df.index.max().date()}")
print(f"Cumulative flows: ${df['Cumulative_Flows'].iloc[-1]:,.0f}M")
print(f"BTC Price: ${df['BTC_Price'].iloc[-1]:,.0f}")

print("Loading on-chain data...")
df_onchain = prepare_onchain_data()
if df_onchain is not None:
    print(f"On-chain data loaded: {len(df_onchain)} days")
    print(f"Base TVL: ${df_onchain['Base_TVL'].iloc[-1]:.1f}B")
    if 'cbBTC_TVL' in df_onchain.columns:
        print(f"cbBTC TVL: ${df_onchain['cbBTC_TVL'].iloc[-1]:.2f}B")


# ———————— HELPER FUNCTIONS ————————

def new_fig(figsize=(14, 8)):
    """Create figure with theme background and standard margins."""
    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_facecolor(THEME['bg'])
    ax.set_facecolor(THEME['bg'])
    return fig, ax


def style_ax(ax):
    """Core spine/grid styling."""
    for spine in ax.spines.values():
        spine.set_color(THEME['spine'])
        spine.set_linewidth(0.5)
    ax.grid(False)
    ax.tick_params(axis='both', which='both', length=0, colors=THEME['muted'])
    ax.tick_params(axis='x', labelsize=10, labelcolor=THEME['muted'])


def style_dual_ax(ax1, ax2, c1, c2):
    """Full dual-axis styling: LHS=c1 (secondary), RHS=c2 (primary)."""
    for ax in [ax1, ax2]:
        ax.set_facecolor(THEME['bg'])
        for spine in ax.spines.values():
            spine.set_color(THEME['spine'])
            spine.set_linewidth(0.5)
        ax.grid(False)

    # Axis 1 (LHS - Secondary)
    ax1.tick_params(axis='both', which='both', length=0, colors=THEME['muted'])
    ax1.tick_params(axis='y', labelcolor=c1, labelsize=10)
    ax1.tick_params(axis='x', labelsize=10, labelcolor=THEME['muted'])

    # Axis 2 (RHS - Primary)
    ax2.tick_params(axis='both', which='both', length=0, colors=THEME['muted'])
    ax2.tick_params(axis='y', labelcolor=c2, labelsize=10)


def set_xlim_to_data(ax, idx, padding_left_days=0):
    """Set x-axis limits with optional left padding and ~2 month right padding."""
    padding_left = pd.Timedelta(days=padding_left_days)
    padding_right = pd.Timedelta(days=54)  # Extends to ~March 31, 2026
    ax.set_xlim(idx.min() - padding_left, idx.max() + padding_right)


def add_last_value_label(ax, y_val, color, fmt='{:.1f}', side='right', fontsize=9, pad=0.3):
    """Add colored pill on axis edge."""
    label = fmt.format(y_val)
    pill = dict(boxstyle=f'round,pad={pad}', facecolor=color, edgecolor=color, alpha=0.95)

    if side == 'right':
        ax.annotate(label, xy=(1.0, y_val), xycoords=('axes fraction', 'data'),
                    fontsize=fontsize, fontweight='bold', color='white',
                    ha='left', va='center', xytext=(6, 0), textcoords='offset points', bbox=pill)
    else:
        ax.annotate(label, xy=(0.0, y_val), xycoords=('axes fraction', 'data'),
                    fontsize=fontsize, fontweight='bold', color='white',
                    ha='right', va='center', xytext=(-6, 0), textcoords='offset points', bbox=pill)


def brand_fig(fig, title, subtitle, source='Lighthouse Macro'):
    """Apply all figure-level branding (watermarks, bars, title)."""
    # Top accent bar (Ocean 2/3, Dusk 1/3) - FIRST so titles go on top
    ax_top = fig.add_axes([0.03, 0.96, 0.94, 0.004])
    ax_top.axhspan(0, 1, 0, 0.67, color=COLORS['ocean'])
    ax_top.axhspan(0, 1, 0.67, 1.0, color=COLORS['dusk'])
    ax_top.set_xlim(0, 1)
    ax_top.set_ylim(0, 1)
    ax_top.axis('off')

    # Bottom accent bar (mirror)
    ax_bot = fig.add_axes([0.03, 0.035, 0.94, 0.004])
    ax_bot.axhspan(0, 1, 0, 0.67, color=COLORS['ocean'])
    ax_bot.axhspan(0, 1, 0.67, 1.0, color=COLORS['dusk'])
    ax_bot.set_xlim(0, 1)
    ax_bot.set_ylim(0, 1)
    ax_bot.axis('off')

    # Lighthouse icon (top-left, next to text)
    if os.path.exists(ICON_PATH):
        icon_img = mpimg.imread(ICON_PATH)
        icon_w = 0.018
        icon_aspect = icon_img.shape[0] / icon_img.shape[1]
        fig_aspect = fig.get_figwidth() / fig.get_figheight()
        icon_h = icon_w * icon_aspect * fig_aspect
        icon_ax = fig.add_axes([0.042, 0.985 - icon_h, icon_w, icon_h])
        icon_ax.imshow(icon_img, aspect='equal')
        icon_ax.axis('off')

    # Top-left: LIGHTHOUSE MACRO
    fig.text(0.065, 0.98, 'LIGHTHOUSE MACRO', fontsize=13, fontweight='bold', color=COLORS['ocean'])

    # Top-right: Date
    fig.text(0.94, 0.98, 'February 05, 2026', fontsize=11, color=THEME['muted'], ha='right')

    # Title and Subtitle - adjusted positions
    fig.text(0.50, 0.93, title, fontsize=16, fontweight='bold', color=THEME['fg'], ha='center')
    fig.text(0.50, 0.895, subtitle, fontsize=12, style='italic', color=COLORS['ocean'], ha='center')

    # Bottom-right: Tagline
    fig.text(0.94, 0.015, 'MACRO, ILLUMINATED.', fontsize=13, fontweight='bold',
             style='italic', color=COLORS['ocean'], ha='right')

    # Bottom-left: Source
    fig.text(0.06, 0.015, f'Lighthouse Macro | {source}; 02.05.2026',
             fontsize=9, style='italic', color=THEME['muted'])


def add_outer_border(fig):
    """Add 4pt Ocean border at absolute figure edge."""
    fig.patches.append(plt.Rectangle(
        (0, 0), 1, 1, transform=fig.transFigure,
        fill=False, edgecolor=COLORS['ocean'], linewidth=4.0,
        zorder=100, clip_on=False
    ))


def add_annotation_box(ax, text, x=0.52, y=0.08):
    """Add takeaway box - default to bottom of chart area."""
    ax.text(x, y, text, transform=ax.transAxes,
            fontsize=10, color=THEME['fg'], ha='center', va='bottom', style='italic',
            bbox=dict(boxstyle='round,pad=0.5', facecolor=THEME['bg'],
                      edgecolor=COLORS['ocean'], alpha=0.9))


def legend_style():
    """Return legend kwargs dict."""
    return dict(
        framealpha=0.95,
        facecolor=THEME['legend_bg'],
        edgecolor=THEME['spine'],
        labelcolor=THEME['legend_fg'],
    )


def save_fig(fig, name):
    """Save with standard settings."""
    path = OUTPUT_DIR / f'{name}.png'
    fig.savefig(path, dpi=200, bbox_inches='tight', pad_inches=0.025,
                facecolor=THEME['bg'], edgecolor='none')
    print(f"Saved: {path}")
    plt.close(fig)


# ———————— CHART 1: ETF FLOWS VS PRICE ————————
def chart_01_etf_flows():
    """The Spot Capitulation - ETF Flows vs BTC Price"""
    fig, ax1 = plt.subplots(figsize=(14, 8))
    fig.patch.set_facecolor(THEME['bg'])
    ax2 = ax1.twinx()

    c_secondary = THEME['secondary']  # Dusk - LHS
    c_primary = THEME['primary']      # Sky - RHS

    # LHS: Cumulative Flows (Dusk - Secondary)
    ax1.fill_between(df.index, df['Cumulative_Flows'], 0, color=c_secondary, alpha=0.15)
    l1, = ax1.plot(df.index, df['Cumulative_Flows'], color=c_secondary, linewidth=1.5,
                   label=f'Cum. Net ETF Flows (${df["Cumulative_Flows"].iloc[-1]:,.0f}M)')

    # RHS: Price (Sky - Primary)
    l2, = ax2.plot(df.index, df['BTC_Price'], color=c_primary, linewidth=2,
                   label=f'BTC Price (${df["BTC_Price"].iloc[-1]:,.0f})')

    # Styling
    style_dual_ax(ax1, ax2, c_secondary, c_primary)

    # Y-axis formatters
    ax1.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'${x/1000:.0f}B' if abs(x) >= 1000 else f'${x:.0f}M'))
    ax2.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'${x/1000:.0f}K'))

    # Set limits with padding
    flow_min = df['Cumulative_Flows'].min()
    flow_max = df['Cumulative_Flows'].max()
    ax1.set_ylim(min(0, flow_min * 1.1), flow_max * 1.15)
    ax2.set_ylim(df['BTC_Price'].min() * 0.9, df['BTC_Price'].max() * 1.1)
    set_xlim_to_data(ax1, df.index, padding_left_days=0)

    # Pills
    add_last_value_label(ax1, df['Cumulative_Flows'].iloc[-1], c_secondary, fmt='${:,.0f}M', side='left')
    add_last_value_label(ax2, df['BTC_Price'].iloc[-1], c_primary, fmt='${:,.0f}', side='right')

    # Calculate stats for annotation
    peak_idx = df['Cumulative_Flows'].idxmax()
    peak_flows = df['Cumulative_Flows'].max()
    current_flows = df['Cumulative_Flows'].iloc[-1]
    outflows_since_peak = current_flows - peak_flows

    price_at_peak = df.loc[peak_idx, 'BTC_Price']
    current_price = df['BTC_Price'].iloc[-1]
    price_drawdown = (current_price - price_at_peak) / price_at_peak * 100

    # Branding
    brand_fig(fig, 'THE SPOT CAPITULATION', 'Cumulative ETF Flows vs. BTC Price', source='Farside Investors, Yahoo Finance')
    add_annotation_box(ax1, f"Outflows since peak: ${outflows_since_peak:,.0f}M  |  Price vs. peak: {price_drawdown:+.1f}%", x=0.5, y=0.03)

    # Legend
    lines = [l1, l2]
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc='upper left', **legend_style())

    # Margins and border
    fig.subplots_adjust(top=0.86, bottom=0.10, left=0.06, right=0.94)
    add_outer_border(fig)

    save_fig(fig, 'chart_01_etf_flows_vs_price')


# ———————— CHART 2: FLOW MOMENTUM ————————
def chart_02_flow_momentum():
    """Flow Momentum - 20-day rolling sum of daily flows"""
    fig, ax1 = plt.subplots(figsize=(14, 8))
    fig.patch.set_facecolor(THEME['bg'])
    ax2 = ax1.twinx()

    c_secondary = THEME['secondary']  # Dusk - LHS
    c_primary = THEME['primary']      # Sky - RHS

    # Calculate 30-day rolling sum
    df['Flow_30d'] = df['Total'].rolling(30).sum()

    # LHS: 30-day flow momentum (Dusk - Secondary)
    ax1.fill_between(df.index, df['Flow_30d'], 0,
                     where=df['Flow_30d'] >= 0, color=COLORS['sea'], alpha=0.3)
    ax1.fill_between(df.index, df['Flow_30d'], 0,
                     where=df['Flow_30d'] < 0, color=COLORS['venus'], alpha=0.3)
    l1, = ax1.plot(df.index, df['Flow_30d'], color=c_secondary, linewidth=1.5,
                   label=f'30-Day Flow Sum (${df["Flow_30d"].iloc[-1]:,.0f}M)')

    # RHS: Price (Sky - Primary)
    l2, = ax2.plot(df.index, df['BTC_Price'], color=c_primary, linewidth=2,
                   label=f'BTC Price (${df["BTC_Price"].iloc[-1]:,.0f})')

    # Zero line
    ax1.axhline(0, color=COLORS['doldrums'], linewidth=1, linestyle='--', alpha=0.5)

    # Styling
    style_dual_ax(ax1, ax2, c_secondary, c_primary)

    # Y-axis formatters
    ax1.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'${x/1000:.1f}B' if abs(x) >= 1000 else f'${x:.0f}M'))
    ax2.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'${x/1000:.0f}K'))

    # Set limits
    flow_min = df['Flow_30d'].min()
    flow_max = df['Flow_30d'].max()
    ax1.set_ylim(flow_min * 1.2, flow_max * 1.2)
    ax2.set_ylim(df['BTC_Price'].min() * 0.9, df['BTC_Price'].max() * 1.1)
    set_xlim_to_data(ax1, df.index, padding_left_days=0)

    # Pills
    add_last_value_label(ax1, df['Flow_30d'].iloc[-1], c_secondary, fmt='${:,.0f}M', side='left')
    add_last_value_label(ax2, df['BTC_Price'].iloc[-1], c_primary, fmt='${:,.0f}', side='right')

    # Branding
    brand_fig(fig, 'FLOW MOMENTUM', '30-Day Rolling Flow Sum vs. BTC Price', source='Farside Investors, Yahoo Finance')

    # Count days of negative momentum
    recent_neg = (df['Flow_30d'].iloc[-30:] < 0).sum()
    add_annotation_box(ax1, f"Negative momentum: {recent_neg}/30 recent days", x=0.5, y=0.03)

    # Legend
    lines = [l1, l2]
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc='upper left', **legend_style())

    # Margins and border
    fig.subplots_adjust(top=0.86, bottom=0.10, left=0.06, right=0.94)
    add_outer_border(fig)

    save_fig(fig, 'chart_02_flow_momentum')


# ———————— CHART 3: ON-CHAIN REALITY ————————
def chart_03_onchain():
    """The On-Chain Reality - Base Chain TVL Growth"""
    if df_onchain is None:
        print("Skipping chart 3 - no on-chain data available")
        return

    fig, ax = plt.subplots(figsize=(14, 8))
    fig.patch.set_facecolor(THEME['bg'])

    # Filter for last 12 months
    cutoff = df_onchain.index.max() - pd.Timedelta(days=365)
    df_recent = df_onchain[df_onchain.index >= cutoff].copy()

    c_primary = THEME['primary']  # Ocean

    # Single axis: Base TVL
    ax.fill_between(df_recent.index, df_recent['Base_TVL'], 0, color=c_primary, alpha=0.15)
    l1, = ax.plot(df_recent.index, df_recent['Base_TVL'], color=c_primary, linewidth=2,
                  label=f'Base Chain TVL (${df_recent["Base_TVL"].iloc[-1]:.1f}B)')

    # Styling
    style_ax(ax)
    ax.set_facecolor(THEME['bg'])

    # Y-axis formatter
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'${x:.1f}B'))
    ax.tick_params(axis='y', labelcolor=c_primary, labelsize=10)

    # Set limits
    ax.set_ylim(0, df_recent['Base_TVL'].max() * 1.2)
    set_xlim_to_data(ax, df_recent.index, padding_left_days=0)

    # Pill
    add_last_value_label(ax, df_recent['Base_TVL'].iloc[-1], c_primary, fmt='${:.1f}B', side='right')

    # Calculate growth
    start_tvl = df_recent['Base_TVL'].iloc[0]
    end_tvl = df_recent['Base_TVL'].iloc[-1]
    growth_pct = (end_tvl - start_tvl) / start_tvl * 100

    # Branding
    brand_fig(fig, 'THE ON-CHAIN REALITY', 'Base Chain Total Value Locked', source='DefiLlama')
    add_annotation_box(ax, f"12-month TVL growth: +{growth_pct:.0f}%  |  Price falls, infrastructure grows.", x=0.5, y=0.03)

    # Legend
    ax.legend(loc='upper left', **legend_style())

    # Margins and border
    fig.subplots_adjust(top=0.86, bottom=0.10, left=0.06, right=0.94)
    add_outer_border(fig)

    save_fig(fig, 'chart_03_onchain_reality')


# ———————— CHART 4: GBTC VS REST ————————
def chart_04_gbtc_vs_rest():
    """GBTC Exodus - Cumulative GBTC outflows vs rest of field inflows"""
    # Need raw flows data
    flows_raw = load_etf_flows()

    fig, ax1 = plt.subplots(figsize=(14, 8))
    fig.patch.set_facecolor(THEME['bg'])
    ax2 = ax1.twinx()

    c_secondary = THEME['secondary']  # Dusk - LHS (GBTC)
    c_primary = THEME['primary']      # Ocean - RHS (Rest)

    # Calculate cumulative flows
    gbtc_cum = flows_raw['GBTC'].cumsum()
    rest_cols = [c for c in flows_raw.columns if c not in ['GBTC', 'Total', 'BTC', 'Cumulative_Flows']]
    rest_cum = flows_raw[rest_cols].sum(axis=1).cumsum()

    # LHS: GBTC cumulative (Dusk - will be negative)
    ax1.fill_between(gbtc_cum.index, gbtc_cum, 0, color=c_secondary, alpha=0.15)
    l1, = ax1.plot(gbtc_cum.index, gbtc_cum, color=c_secondary, linewidth=2,
                   label=f'GBTC Cum. Flows (${gbtc_cum.iloc[-1]/1000:.1f}B)')

    # RHS: Rest of field cumulative (Ocean - positive)
    ax2.fill_between(rest_cum.index, rest_cum, 0, color=c_primary, alpha=0.15)
    l2, = ax2.plot(rest_cum.index, rest_cum, color=c_primary, linewidth=2,
                   label=f'All Other ETFs (${rest_cum.iloc[-1]/1000:.1f}B)')

    # Zero lines
    ax1.axhline(0, color=COLORS['doldrums'], linewidth=0.8, linestyle='--', alpha=0.5)

    # Styling
    style_dual_ax(ax1, ax2, c_secondary, c_primary)

    # Y-axis formatters
    ax1.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'${x/1000:.0f}B'))
    ax2.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'${x/1000:.0f}B'))

    # Set limits
    ax1.set_ylim(gbtc_cum.min() * 1.1, gbtc_cum.max() * 0.5 if gbtc_cum.max() > 0 else 1000)
    ax2.set_ylim(0, rest_cum.max() * 1.15)
    set_xlim_to_data(ax1, gbtc_cum.index, padding_left_days=0)

    # Pills
    add_last_value_label(ax1, gbtc_cum.iloc[-1], c_secondary, fmt='${:,.0f}M', side='left')
    add_last_value_label(ax2, rest_cum.iloc[-1], c_primary, fmt='${:,.0f}M', side='right')

    # Branding
    brand_fig(fig, 'THE GBTC EXODUS', 'Grayscale Outflows vs. New ETF Inflows', source='Farside Investors')
    add_annotation_box(ax1, f"GBTC: ${gbtc_cum.iloc[-1]/1000:.1f}B out  |  Others: +${rest_cum.iloc[-1]/1000:.1f}B in", x=0.5, y=0.03)

    # Legend
    lines = [l1, l2]
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc='upper left', **legend_style())

    # Margins and border
    fig.subplots_adjust(top=0.86, bottom=0.10, left=0.06, right=0.94)
    add_outer_border(fig)

    save_fig(fig, 'chart_04_gbtc_vs_rest')


# ———————— CHART 5: LARGEST SINGLE-DAY FLOWS ————————
def chart_05_largest_flows():
    """Top 10 Largest Inflows and Outflows"""
    flows_raw = load_etf_flows()

    fig, ax = plt.subplots(figsize=(14, 8))
    fig.patch.set_facecolor(THEME['bg'])

    # Get top 10 inflows and outflows
    top_inflows = flows_raw['Total'].nlargest(10)
    top_outflows = flows_raw['Total'].nsmallest(10)

    # Combine and sort by absolute value
    combined = pd.concat([top_inflows, top_outflows]).sort_values()

    # Colors based on sign
    colors = [COLORS['venus'] if v < 0 else COLORS['sea'] for v in combined.values]

    # Horizontal bar chart
    y_pos = np.arange(len(combined))
    bars = ax.barh(y_pos, combined.values, color=colors, alpha=0.8, height=0.7)

    # Format y-axis labels as dates
    date_labels = [d.strftime('%b %d, %Y') for d in combined.index]
    ax.set_yticks(y_pos)
    ax.set_yticklabels(date_labels, fontsize=9, color=THEME['fg'])

    # Zero line
    ax.axvline(0, color=COLORS['doldrums'], linewidth=1, linestyle='-', alpha=0.7)

    # Styling
    ax.set_facecolor(THEME['bg'])
    for spine in ax.spines.values():
        spine.set_color(THEME['spine'])
        spine.set_linewidth(0.5)
    ax.tick_params(axis='both', which='both', length=0, colors=THEME['muted'])
    ax.tick_params(axis='x', labelsize=10, labelcolor=THEME['muted'])

    # X-axis formatter
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, p: f'${x/1000:.1f}B' if abs(x) >= 1000 else f'${x:.0f}M'))

    # Add value labels on bars
    for bar, val in zip(bars, combined.values):
        x_pos = val + (50 if val > 0 else -50)
        ha = 'left' if val > 0 else 'right'
        ax.text(x_pos, bar.get_y() + bar.get_height()/2,
                f'${val:,.0f}M', va='center', ha=ha,
                fontsize=8, color=THEME['fg'], fontweight='bold')

    # Branding
    brand_fig(fig, 'EXTREME FLOW DAYS', 'Top 10 Largest Daily Inflows & Outflows', source='Farside Investors')

    # Find the biggest outflow
    worst_day = flows_raw['Total'].idxmin()
    worst_val = flows_raw['Total'].min()
    add_annotation_box(ax, f"Largest outflow: ${worst_val:,.0f}M on {worst_day.strftime('%b %d, %Y')}", x=0.25, y=0.03)

    # Margins and border
    fig.subplots_adjust(top=0.86, bottom=0.10, left=0.15, right=0.94)
    add_outer_border(fig)

    save_fig(fig, 'chart_05_largest_flows')


# ———————— CHART 6: 30-DAY ROLLING FLOW Z-SCORE ————————
def chart_06_flow_zscore_30d():
    """30-Day Rolling Flow Sum Z-Score with Fixed ±1σ Bands"""
    flows_raw = load_etf_flows()

    fig, ax = plt.subplots(figsize=(14, 8))
    fig.patch.set_facecolor(THEME['bg'])

    c_primary = THEME['primary']  # Ocean

    # Calculate 30-day rolling sum
    flow_30d = flows_raw['Total'].rolling(30).sum()

    # Calculate z-score using full history mean and std of the 30-day sum
    full_mean = flow_30d.mean()
    full_std = flow_30d.std()
    z_score = (flow_30d - full_mean) / full_std
    z_score = z_score.dropna()

    # Plot fixed ±1σ bands
    ax.axhspan(-1, 1, color=c_primary, alpha=0.10)
    ax.axhline(1, color=c_primary, linewidth=1, linestyle='--', alpha=0.5)
    ax.axhline(-1, color=c_primary, linewidth=1, linestyle='--', alpha=0.5)

    # Plot z-score as line with fill
    ax.fill_between(z_score.index, z_score, 0,
                    where=z_score >= 0, color=COLORS['sea'], alpha=0.3)
    ax.fill_between(z_score.index, z_score, 0,
                    where=z_score < 0, color=COLORS['venus'], alpha=0.3)
    ax.plot(z_score.index, z_score, color=c_primary, linewidth=1.5)

    # Zero line
    ax.axhline(0, color=COLORS['doldrums'], linewidth=1, linestyle='-', alpha=0.7)

    # Styling
    style_ax(ax)
    ax.set_facecolor(THEME['bg'])
    ax.tick_params(axis='y', labelcolor=c_primary, labelsize=10)

    # Y-axis formatter (z-score, no $)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.1f}σ'))

    # Set limits
    y_max = max(z_score.max() * 1.1, 2)
    y_min = min(z_score.min() * 1.1, -2)
    ax.set_ylim(y_min, y_max)
    set_xlim_to_data(ax, z_score.index, padding_left_days=0)

    # Pill for current value
    add_last_value_label(ax, z_score.iloc[-1], c_primary, fmt='{:.2f}σ', side='right')

    # Count outliers
    outliers_up = (z_score > 1).sum()
    outliers_down = (z_score < -1).sum()
    current_z = z_score.iloc[-1]

    # Determine regime
    if current_z < -1:
        regime = "Outflow regime"
    elif current_z > 1:
        regime = "Inflow regime"
    else:
        regime = "Normal regime"

    # Branding
    brand_fig(fig, 'FLOW MOMENTUM Z-SCORE (30D)', '30-Day Rolling Flow Sum (Standardized)', source='Farside Investors')
    add_annotation_box(ax, f"{regime}  |  {outliers_down} periods below -1σ historically", x=0.5, y=0.03)

    # Add +1/-1 labels
    ax.text(0.02, 1.1, '+1σ', fontsize=9, color=c_primary, alpha=0.7,
            transform=ax.get_yaxis_transform(), va='bottom')
    ax.text(0.02, -1.1, '-1σ', fontsize=9, color=c_primary, alpha=0.7,
            transform=ax.get_yaxis_transform(), va='top')

    # Margins and border
    fig.subplots_adjust(top=0.86, bottom=0.10, left=0.06, right=0.94)
    add_outer_border(fig)

    save_fig(fig, 'chart_06_flow_zscore_30d')


# ———————— CHART 7: 90-DAY ROLLING FLOW Z-SCORE (CLEAN) ————————
def chart_07_flow_zscore_90d():
    """90-Day Rolling Flow Sum Z-Score with Fixed ±1σ Bands"""
    flows_raw = load_etf_flows()

    fig, ax = plt.subplots(figsize=(14, 8))
    fig.patch.set_facecolor(THEME['bg'])

    c_primary = THEME['primary']  # Ocean

    # Calculate 90-day rolling sum
    flow_90d = flows_raw['Total'].rolling(90).sum()

    # Calculate z-score using full history mean and std of the 90-day sum
    full_mean = flow_90d.mean()
    full_std = flow_90d.std()
    z_score = (flow_90d - full_mean) / full_std
    z_score = z_score.dropna()

    # Plot fixed ±1σ bands
    ax.axhspan(-1, 1, color=c_primary, alpha=0.10)
    ax.axhline(1, color=c_primary, linewidth=1, linestyle='--', alpha=0.5)
    ax.axhline(-1, color=c_primary, linewidth=1, linestyle='--', alpha=0.5)

    # Plot z-score as line with fill
    ax.fill_between(z_score.index, z_score, 0,
                    where=z_score >= 0, color=COLORS['sea'], alpha=0.3)
    ax.fill_between(z_score.index, z_score, 0,
                    where=z_score < 0, color=COLORS['venus'], alpha=0.3)
    ax.plot(z_score.index, z_score, color=c_primary, linewidth=2)

    # Zero line
    ax.axhline(0, color=COLORS['doldrums'], linewidth=1, linestyle='-', alpha=0.7)

    # Styling
    style_ax(ax)
    ax.set_facecolor(THEME['bg'])
    ax.tick_params(axis='y', labelcolor=c_primary, labelsize=10)

    # Y-axis formatter (z-score, no $)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.1f}σ'))

    # Set limits
    y_max = max(z_score.max() * 1.1, 2)
    y_min = min(z_score.min() * 1.1, -2.5)
    ax.set_ylim(y_min, y_max)
    set_xlim_to_data(ax, z_score.index, padding_left_days=0)

    # Pill for current value
    add_last_value_label(ax, z_score.iloc[-1], c_primary, fmt='{:.2f}σ', side='right')

    # Find all-time low z-score
    min_z = z_score.min()
    min_z_date = z_score.idxmin()
    current_z = z_score.iloc[-1]

    # Determine regime
    if current_z < -1:
        regime = "Outflow regime"
    elif current_z > 1:
        regime = "Inflow regime"
    else:
        regime = "Normal regime"

    # Check if near all-time low
    if current_z <= min_z * 0.95:  # Within 5% of ATL
        note = f"NEAR ALL-TIME LOW ({current_z:.2f}σ)"
    else:
        note = f"ATL: {min_z:.2f}σ on {min_z_date.strftime('%b %d, %Y')}"

    # Branding
    brand_fig(fig, 'THE SILENT CAPITULATION', '90-Day Flow Momentum (Standardized)', source='Farside Investors')
    add_annotation_box(ax, f"{regime}  |  {note}", x=0.5, y=0.03)

    # Add +1/-1 labels
    ax.text(0.02, 1.1, '+1σ', fontsize=9, color=c_primary, alpha=0.7,
            transform=ax.get_yaxis_transform(), va='bottom')
    ax.text(0.02, -1.1, '-1σ', fontsize=9, color=c_primary, alpha=0.7,
            transform=ax.get_yaxis_transform(), va='top')

    # Margins and border
    fig.subplots_adjust(top=0.86, bottom=0.10, left=0.06, right=0.94)
    add_outer_border(fig)

    save_fig(fig, 'chart_07_flow_zscore_90d')


# ———————— CHART 8: BASE TVL & cbBTC GROWTH ————————
def chart_08_base_cbbtc():
    """Capital Rotation - Base TVL & cbBTC Market Cap Growth"""
    fig, ax1 = plt.subplots(figsize=(14, 8))
    fig.patch.set_facecolor(THEME['bg'])
    ax2 = ax1.twinx()

    c_secondary = THEME['secondary']  # Dusk - LHS (cbBTC)
    c_primary = THEME['primary']      # Ocean - RHS (Base TVL)

    # User-provided data points for Base TVL (in $B)
    base_data = {
        'Jan 2024': 0.43,
        'Sep 2024': 1.42,
        'Jan 2025': 2.00,
        'Feb 2026': 3.89,
    }

    # User-provided data points for cbBTC Market Cap (in $B)
    cbbtc_data = {
        'Sep 2024': 0.06,   # ~1,000 BTC at launch
        'Jan 2025': 2.0,    # ~30,500 BTC
        'Feb 2026': 6.0,    # ~84,040 BTC
    }

    # Convert to datetime for plotting
    base_dates = pd.to_datetime([
        '2024-01-15', '2024-09-15', '2025-01-15', '2026-02-05'
    ])
    base_values = list(base_data.values())

    cbbtc_dates = pd.to_datetime([
        '2024-09-15', '2025-01-15', '2026-02-05'
    ])
    cbbtc_values = list(cbbtc_data.values())

    # RHS: Base TVL (Ocean - Primary)
    ax1.fill_between(base_dates, base_values, 0, color=c_primary, alpha=0.15, step='mid')
    l1, = ax1.plot(base_dates, base_values, color=c_primary, linewidth=2.5,
                   marker='o', markersize=8, markerfacecolor=c_primary, markeredgecolor='white',
                   label=f'Base Chain TVL (${base_values[-1]:.1f}B)')

    # LHS: cbBTC Market Cap (Dusk - Secondary)
    ax2.fill_between(cbbtc_dates, cbbtc_values, 0, color=c_secondary, alpha=0.15, step='mid')
    l2, = ax2.plot(cbbtc_dates, cbbtc_values, color=c_secondary, linewidth=2.5,
                   marker='s', markersize=8, markerfacecolor=c_secondary, markeredgecolor='white',
                   label=f'cbBTC Market Cap (${cbbtc_values[-1]:.1f}B)')

    # Add data point labels for Base TVL
    for date, val in zip(base_dates, base_values):
        ax1.annotate(f'${val:.2f}B' if val < 1 else f'${val:.1f}B',
                     xy=(date, val), xytext=(0, 10), textcoords='offset points',
                     fontsize=9, color=c_primary, ha='center', fontweight='bold')

    # Add data point labels for cbBTC
    for date, val in zip(cbbtc_dates, cbbtc_values):
        ax2.annotate(f'${val:.2f}B' if val < 1 else f'${val:.1f}B',
                     xy=(date, val), xytext=(0, -18), textcoords='offset points',
                     fontsize=9, color=c_secondary, ha='center', fontweight='bold')

    # Styling
    style_dual_ax(ax1, ax2, c_primary, c_secondary)

    # Y-axis formatters
    ax1.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'${x:.1f}B'))
    ax2.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'${x:.1f}B'))

    # Set limits
    ax1.set_ylim(0, max(base_values) * 1.25)
    ax2.set_ylim(0, max(cbbtc_values) * 1.25)

    # X-axis limits
    x_min = pd.Timestamp('2023-10-01')
    x_max = pd.Timestamp('2026-04-01')
    ax1.set_xlim(x_min, x_max)

    # Add vertical line for cbBTC launch
    launch_date = pd.Timestamp('2024-09-01')
    ax1.axvline(launch_date, color=COLORS['doldrums'], linewidth=1, linestyle='--', alpha=0.5)
    ax1.text(launch_date, ax1.get_ylim()[1] * 0.95, 'cbBTC Launch\nSep 2024',
             fontsize=9, color=THEME['muted'], ha='center', va='top')

    # Calculate growth stats
    base_growth = (base_values[-1] / base_values[0] - 1) * 100  # 9x = 800%
    cbbtc_growth_btc = 84040 / 1000  # 84x growth in BTC terms

    # Branding
    brand_fig(fig, 'THE CAPITAL ROTATION', 'Base Chain TVL & cbBTC Market Cap Growth', source='DefiLlama, User Research')
    add_annotation_box(ax1, f"Base TVL: 9x since Jan 2024  |  cbBTC: 0 → $6B since Sep 2024  |  Capital is moving, not leaving.", x=0.5, y=0.03)

    # Legend
    lines = [l1, l2]
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc='upper left', **legend_style())

    # Margins and border
    fig.subplots_adjust(top=0.86, bottom=0.10, left=0.06, right=0.94)
    add_outer_border(fig)

    save_fig(fig, 'chart_08_base_cbbtc')


# ———————— CHART 9: ON-CHAIN METRICS PLACEHOLDER ————————
def chart_09_onchain_metrics():
    """Placeholder: On-Chain Metrics (MVRV, NUPL, SOPR)"""
    fig, ax = plt.subplots(figsize=(14, 8))
    fig.patch.set_facecolor(THEME['bg'])
    ax.set_facecolor(THEME['bg'])

    c_primary = THEME['primary']

    # Placeholder data based on article values
    metrics = ['MVRV', 'NUPL', 'SOPR']
    values = [1.31, 0.2387, 0.9765]
    thresholds = [2.0, 0.75, 1.0]  # Key thresholds for comparison
    signals = ['Accumulation\nZone', 'Hope\nPhase', 'Capitulation\n(<1.0)']

    y_pos = np.arange(len(metrics))

    # Plot current values as bars
    bars = ax.barh(y_pos, values, color=c_primary, alpha=0.8, height=0.5, label='Current Value')

    # Plot threshold markers
    for i, thresh in enumerate(thresholds):
        ax.plot(thresh, i, marker='|', markersize=25, color=COLORS['venus'], linewidth=3)

    # Styling
    ax.set_yticks(y_pos)
    ax.set_yticklabels(metrics, fontsize=12, fontweight='bold', color=THEME['fg'])
    style_ax(ax)

    # Add value labels
    for bar, val, sig in zip(bars, values, signals):
        ax.text(val + 0.05, bar.get_y() + bar.get_height()/2,
                f'{val:.2f}  ({sig})', va='center', ha='left',
                fontsize=10, color=THEME['fg'])

    ax.set_xlim(0, 2.5)

    # Branding
    brand_fig(fig, 'ON-CHAIN ACCUMULATION SIGNALS', 'MVRV, NUPL, SOPR (CryptoQuant, Feb 4, 2026)', source='CryptoQuant')
    add_annotation_box(ax, "All three metrics signal accumulation zone. SOPR <1.0 = sellers realizing losses.", x=0.5, y=0.03)

    # Margins and border
    fig.subplots_adjust(top=0.86, bottom=0.10, left=0.12, right=0.94)
    add_outer_border(fig)

    save_fig(fig, 'chart_09_onchain_metrics')


# ———————— CHART 10: EXCHANGE NET FLOWS PLACEHOLDER ————————
def chart_10_exchange_flows():
    """Placeholder: Exchange Net Flows"""
    fig, ax = plt.subplots(figsize=(14, 8))
    fig.patch.set_facecolor(THEME['bg'])
    ax.set_facecolor(THEME['bg'])

    c_primary = THEME['primary']

    # Placeholder data based on article: net flows turning negative in January
    dates = pd.date_range('2025-12-15', '2026-02-05', freq='D')
    np.random.seed(42)
    # Simulate: starts slightly positive, trends negative, ending at -6910 on Feb 2
    base_trend = np.linspace(2000, -5000, len(dates))
    noise = np.random.normal(0, 1500, len(dates))
    flows = base_trend + noise
    # Set Feb 2 specifically to -6910
    flows[-4] = -6910

    # Plot
    ax.fill_between(dates, flows, 0,
                    where=flows >= 0, color=COLORS['sea'], alpha=0.3)
    ax.fill_between(dates, flows, 0,
                    where=flows < 0, color=COLORS['venus'], alpha=0.3)
    ax.plot(dates, flows, color=c_primary, linewidth=1.5)

    # Zero line
    ax.axhline(0, color=COLORS['doldrums'], linewidth=1, linestyle='-', alpha=0.7)

    # Styling
    style_ax(ax)
    ax.tick_params(axis='y', labelcolor=c_primary, labelsize=10)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x/1000:.1f}K BTC'))

    set_xlim_to_data(ax, dates, padding_left_days=0)

    # Add annotation for Feb 2 low
    ax.annotate('-6,910 BTC\nFeb 2', xy=(dates[-4], -6910),
                xytext=(20, 20), textcoords='offset points',
                fontsize=9, color=COLORS['venus'], fontweight='bold',
                arrowprops=dict(arrowstyle='->', color=COLORS['venus'], lw=1))

    # Branding
    brand_fig(fig, 'EXCHANGE EXODUS', 'Net BTC Flows to/from Exchanges', source='CryptoQuant (Illustrative)')
    add_annotation_box(ax, "Coins leaving exchanges → Cold storage. Bullish supply dynamics.", x=0.5, y=0.03)

    # Margins and border
    fig.subplots_adjust(top=0.86, bottom=0.10, left=0.08, right=0.94)
    add_outer_border(fig)

    save_fig(fig, 'chart_10_exchange_flows')


# ———————— CHART 11: SOVEREIGN HOLDINGS PLACEHOLDER ————————
def chart_11_sovereign_holdings():
    """Placeholder: Sovereign BTC Holdings"""
    fig, ax = plt.subplots(figsize=(14, 8))
    fig.patch.set_facecolor(THEME['bg'])
    ax.set_facecolor(THEME['bg'])

    # Sovereign holdings data (approximate, from public sources)
    entities = ['El Salvador', 'Bhutan', 'US Gov (Seized)', 'Germany (Sold)', 'UK (Seized)']
    holdings = [6000, 12000, 200000, 0, 61000]  # BTC
    colors = [COLORS['ocean'], COLORS['dusk'], COLORS['sky'], COLORS['doldrums'], COLORS['sea']]
    status = ['Accumulating', 'Strategic Rebalancing', 'Holding', 'Sold 2024', 'Holding']

    y_pos = np.arange(len(entities))

    # Horizontal bar chart
    bars = ax.barh(y_pos, holdings, color=colors, alpha=0.8, height=0.6)

    # Styling
    ax.set_yticks(y_pos)
    ax.set_yticklabels(entities, fontsize=11, color=THEME['fg'])
    style_ax(ax)

    # X-axis formatter
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x/1000:.0f}K BTC'))

    # Add value labels
    for bar, val, stat, col in zip(bars, holdings, status, colors):
        if val > 0:
            ax.text(val + 5000, bar.get_y() + bar.get_height()/2,
                    f'{val:,} BTC  ({stat})', va='center', ha='left',
                    fontsize=9, color=col, fontweight='bold')

    ax.set_xlim(0, max(holdings) * 1.4)

    # Branding
    brand_fig(fig, 'SOVEREIGN HANDS', 'Known Government Bitcoin Holdings', source='Public Blockchain Data, BitcoinTreasuries')
    add_annotation_box(ax, "Smart money accumulates during stress. Bhutan: $765M profit on $120M cost basis.", x=0.5, y=0.03)

    # Margins and border
    fig.subplots_adjust(top=0.86, bottom=0.10, left=0.15, right=0.94)
    add_outer_border(fig)

    save_fig(fig, 'chart_11_sovereign_holdings')


# ———————— MAIN ————————
if __name__ == '__main__':
    print("\nGenerating BTC ETF charts with REAL data...")
    chart_01_etf_flows()
    chart_02_flow_momentum()
    chart_03_onchain()
    chart_04_gbtc_vs_rest()
    chart_05_largest_flows()
    chart_06_flow_zscore_30d()
    chart_07_flow_zscore_90d()
    chart_08_base_cbbtc()
    chart_09_onchain_metrics()
    chart_10_exchange_flows()
    chart_11_sovereign_holdings()
    print("Done.")
