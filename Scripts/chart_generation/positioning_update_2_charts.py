"""
LIGHTHOUSE MACRO — Positioning Update #2 Charts
11 Figures for "The Tariff Regime Breaks. The Defensive Thesis Doesn't."
February 22, 2026
TT Deck Format (White Theme Primary)
"""

import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.image as mpimg
from matplotlib.ticker import FuncFormatter
from datetime import datetime, timedelta
import os

# =============================================================================
# THEME & PALETTE
# =============================================================================

THEME = {
    'bg': '#ffffff',
    'fg': '#1a1a1a',
    'muted': '#555555',
    'spine': '#898989',
    'zero_line': '#D1D1D1',
    'recession': 'gray',
    'recession_alpha': 0.12,
    'brand_color': '#2389BB',
    'brand2_color': '#FF6723',
    'primary': '#2389BB',
    'secondary': '#FF6723',
    'tertiary': '#00BBFF',
    'quaternary': '#00BB89',
    'accent': '#FF2389',
    'bullish': '#238923',
    'bearish': '#892323',
    'fill_alpha': 0.15,
    'box_bg': '#ffffff',
    'box_edge': '#2389BB',
    'legend_bg': '#f8f8f8',
    'legend_fg': '#1a1a1a',
    'mode': 'white',
}

RECESSIONS = [
    ('2001-03-01', '2001-11-01'),
    ('2007-12-01', '2009-06-01'),
    ('2020-02-01', '2020-04-01'),
]

DB_PATH = '/Users/bob/LHM/Data/databases/Lighthouse_Master.db'
ICON_PATH = '/Users/bob/LHM/Brand/icon_transparent_128.png'
OUT_DIR = '/Users/bob/LHM/Outputs/positioning_update_2/white'
os.makedirs(OUT_DIR, exist_ok=True)

DATE_STR = 'February 22, 2026'

# =============================================================================
# HELPER FUNCTIONS — TT DECK FORMAT
# =============================================================================

def new_fig(figsize=(14, 8)):
    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_facecolor(THEME['bg'])
    ax.set_facecolor(THEME['bg'])
    fig.subplots_adjust(top=0.88, bottom=0.08, left=0.06, right=0.94)
    return fig, ax


def style_ax(ax, right_primary=True):
    ax.grid(False)
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_color(THEME['spine'])
        spine.set_linewidth(0.5)
    ax.tick_params(axis='both', which='both', length=0, labelsize=10, colors=THEME['muted'])
    if right_primary:
        ax.yaxis.tick_right()
        ax.yaxis.set_label_position('right')


def style_dual_ax(ax1, ax2, c1, c2):
    """ax1=LHS (secondary), ax2=RHS (primary)"""
    style_ax(ax1, right_primary=False)
    ax1.tick_params(axis='y', labelcolor=c1, labelsize=10)
    ax1.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.1f}'))
    for spine in ax2.spines.values():
        spine.set_visible(True)
        spine.set_color(THEME['spine'])
        spine.set_linewidth(0.5)
    ax2.grid(False)
    ax2.tick_params(axis='both', which='both', length=0)
    ax2.tick_params(axis='y', labelcolor=c2, labelsize=10)
    ax2.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.1f}'))


def style_single_ax(ax):
    style_ax(ax, right_primary=True)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.1f}'))


def set_xlim_to_data(ax, idx):
    pad_right = pd.Timedelta(days=180)
    ax.set_xlim(idx.min(), idx.max() + pad_right)


def brand_fig(fig, title, subtitle=None, source=None, data_date=None):
    """Apply LHM branding at figure level."""
    fig.patch.set_facecolor(THEME['bg'])

    OCEAN = '#2389BB'
    DUSK = '#FF6723'

    # Watermark + date ABOVE accent bar
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
    fig.text(0.97, 0.98, DATE_STR, fontsize=11, color=THEME['muted'], va='top', ha='right')

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

    # Title BELOW accent bar
    fig.suptitle(title, fontsize=15, fontweight='bold', y=0.945,
                 color=THEME['fg'])
    # Subtitle
    if subtitle:
        fig.text(0.50, 0.895, subtitle, fontsize=14, fontstyle='italic', ha='center',
                 color=OCEAN)

    # Bottom-right tagline
    fig.text(0.97, 0.025, 'MACRO, ILLUMINATED.', fontsize=13, fontweight='bold',
             fontstyle='italic', color=OCEAN, ha='right', va='top')
    # Bottom-left source
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


def add_last_value_label(ax, y_data, color, fmt='{:.1f}%', side='right', fontsize=9, pad=0.3):
    last_y = float(y_data.dropna().iloc[-1])
    label = fmt.format(last_y)
    pill = dict(boxstyle=f'round,pad={pad}', facecolor=color, edgecolor=color, alpha=0.95)
    if side == 'right':
        ax.annotate(label, xy=(1.0, last_y), xycoords=('axes fraction', 'data'),
                    fontsize=fontsize, fontweight='bold', color='white',
                    ha='left', va='center',
                    xytext=(6, 0), textcoords='offset points', bbox=pill, clip_on=False)
    else:
        ax.annotate(label, xy=(0.0, last_y), xycoords=('axes fraction', 'data'),
                    fontsize=fontsize, fontweight='bold', color='white',
                    ha='right', va='center',
                    xytext=(-6, 0), textcoords='offset points', bbox=pill, clip_on=False)


def add_annotation_box(ax, text, x=0.52, y=0.92):
    ax.text(x, y, text, transform=ax.transAxes,
            fontsize=12, color='#2389BB', ha='center', va='top',
            fontweight='bold', style='italic',
            bbox=dict(boxstyle='round,pad=0.5',
                      facecolor='#ffffff', edgecolor='#2389BB',
                      linewidth=2.0))


def add_recessions(ax, start_date=None):
    for start, end in RECESSIONS:
        s = pd.Timestamp(start)
        e = pd.Timestamp(end)
        if start_date and e < pd.Timestamp(start_date):
            continue
        ax.axvspan(s, e, color=THEME['recession'], alpha=THEME['recession_alpha'], zorder=0)


def legend_style():
    return dict(
        framealpha=0.95,
        facecolor=THEME['legend_bg'],
        edgecolor=THEME['spine'],
        labelcolor=THEME['legend_fg'],
    )


def add_regime_bands(ax, ymin=-3.0, ymax=3.0):
    ax.axhspan(1.5, ymax, color='#892323', alpha=0.25)
    ax.axhspan(1.0, 1.5, color='#FF6723', alpha=0.20)
    ax.axhspan(0.5, 1.0, color='#FF6723', alpha=0.12)
    ax.axhspan(-0.5, 0.5, color='#00BB89', alpha=0.12)
    ax.axhspan(ymin, -0.5, color='#00BBFF', alpha=0.12)
    # Labels
    ax.text(0.98, 2.0, 'CRISIS', transform=ax.get_yaxis_transform(),
            fontsize=9, color='#892323', va='center', ha='right', fontweight='bold', alpha=0.8)
    ax.text(0.98, 1.25, 'HIGH', transform=ax.get_yaxis_transform(),
            fontsize=9, color='#FF6723', va='center', ha='right', fontweight='bold', alpha=0.8)
    ax.text(0.98, 0.75, 'ELEVATED', transform=ax.get_yaxis_transform(),
            fontsize=8, color='#FF6723', va='center', ha='right', alpha=0.6)
    ax.text(0.98, 0.0, 'NEUTRAL', transform=ax.get_yaxis_transform(),
            fontsize=9, color='#00BB89', va='center', ha='right', fontweight='bold', alpha=0.8)
    ax.text(0.98, -0.75, 'LOW', transform=ax.get_yaxis_transform(),
            fontsize=9, color='#00BBFF', va='center', ha='right', fontweight='bold', alpha=0.8)


def save_fig(fig, name):
    """Save figure to output directory."""
    border_color = '#2389BB'
    border_width = 4.0
    fig.patches.append(plt.Rectangle(
        (0, 0), 1, 1, transform=fig.transFigure,
        fill=False, edgecolor=border_color, linewidth=border_width,
        zorder=100, clip_on=False
    ))
    path = os.path.join(OUT_DIR, name)
    fig.savefig(path, dpi=200, bbox_inches='tight', pad_inches=0.025,
                facecolor=THEME['bg'], edgecolor='none')
    plt.close(fig)
    print(f'  Saved: {path}')
    return path


# =============================================================================
# DATA LOADING
# =============================================================================

def load_series(series_id, start='2015-01-01'):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(
        f"SELECT date, value FROM observations WHERE series_id='{series_id}' AND date >= '{start}' AND value IS NOT NULL ORDER BY date",
        conn
    )
    conn.close()
    df = df[df['date'].str.match(r'^\d{4}-\d{2}-\d{2}', na=False)]
    df['date'] = pd.to_datetime(df['date'])
    df = df.dropna(subset=['value'])
    df = df.set_index('date')
    return df['value']


def load_index(index_id, start='2015-01-01'):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(
        f"SELECT date, value FROM lighthouse_indices WHERE index_id='{index_id}' AND date >= '{start}' ORDER BY date",
        conn
    )
    conn.close()
    df['date'] = pd.to_datetime(df['date'])
    df = df.dropna(subset=['value'])
    df = df.set_index('date')
    return df['value']


def load_all_pillar_latest():
    conn = sqlite3.connect(DB_PATH)
    pillars = {}
    for idx_id in ['LPI','PCI','GCI','HCI','CCI','BCI','TCI','GCI_Gov','FCI','LCI','LFI','CLG','MRI']:
        cur = conn.cursor()
        cur.execute(f"SELECT date, value FROM lighthouse_indices WHERE index_id='{idx_id}' ORDER BY date DESC LIMIT 1")
        r = cur.fetchone()
        if r:
            pillars[idx_id] = r[1]
    conn.close()
    return pillars


# =============================================================================
# FIGURE 1: DEFENSIVE BASKET vs SPY — RELATIVE PERFORMANCE
# =============================================================================

def fig01_defensive_basket():
    print('Building Figure 1: Defensive Basket vs SPY...')

    # Hardcoded relative returns (Jan 15 - Feb 22, 2026)
    positions = ['XLU (Utilities)', 'XLP (Staples)', 'XLV (Healthcare)',
                 'IWM (Small Cap)', 'SPY (Benchmark)']
    rel_returns = [7.9, 7.6, 0.7, 0.1, 0.0]

    fig, ax = new_fig(figsize=(14, 8))
    fig.subplots_adjust(left=0.14, right=0.97)  # Wider left for labels, tighter right
    style_ax(ax, right_primary=False)
    ax.yaxis.tick_left()

    # Colors: Ocean for positive, Doldrums for SPY benchmark
    colors = ['#2389BB' if r > 0 else '#898989' for r in rel_returns]

    # Horizontal bars — thick for mobile readability
    bars = ax.barh(positions, rel_returns, color=colors, height=0.55,
                   edgecolor='none', zorder=2)

    # Zero line
    ax.axvline(0, color=THEME['zero_line'], linewidth=1.0, linestyle='--',
               alpha=0.6, zorder=5)

    # Value labels at bar tips
    for bar_obj, val in zip(bars, rel_returns):
        x_pos = val + 0.15 if val >= 0 else val - 0.15
        ha = 'left' if val >= 0 else 'right'
        label = f'+{val:.1f}%' if val > 0 else '0.0%'
        ax.text(x_pos, bar_obj.get_y() + bar_obj.get_height()/2, label,
                ha=ha, va='center', fontsize=13, fontweight='bold',
                color=THEME['fg'])

    # Invert y-axis so XLU (top performer) is at the top
    ax.invert_yaxis()

    # Clean up x-axis
    ax.set_xlim(-0.5, 9.5)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.0f}%'))
    ax.tick_params(axis='y', labelsize=13, pad=8)
    ax.tick_params(axis='x', labelsize=10)

    add_annotation_box(ax, 'Defensive basket: up to +8% relative in five weeks.\nIn a flat tape, that is the entire game.',
                       x=0.75, y=0.52)

    brand_fig(fig, 'Defensive Basket vs SPY: Jan 15 to Feb 22',
              'Relative performance, 5-week holding period',
              'Yahoo Finance | Period: Jan 15 - Feb 22, 2026')
    return save_fig(fig, 'fig01_defensive_basket.png')


# =============================================================================
# FIGURE 2: JOLTS QUITS RATE
# =============================================================================

def fig02_quits_rate():
    print('Building Figure 2: Quits Rate...')
    quits = load_series('JTSQUR', start='2001-01-01')

    fig, ax = new_fig()
    style_single_ax(ax)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.1f}%'))

    q_plot = quits.dropna()
    ax.fill_between(q_plot.index, q_plot, alpha=THEME['fill_alpha'], color=THEME['primary'], zorder=1)
    ax.plot(q_plot.index, q_plot, color=THEME['primary'], linewidth=2.5,
            label=f'Quits Rate ({q_plot.iloc[-1]:.1f}%)', zorder=2)

    # 2.0% threshold
    ax.axhline(2.0, color=THEME['accent'], linewidth=1.5, linestyle='--', alpha=0.7, zorder=5)
    ax.text(0.37, 2.07, '2.0% Pre-Recessionary Threshold', fontsize=9, color=THEME['accent'],
            alpha=0.8, fontstyle='italic', transform=ax.get_yaxis_transform())

    add_recessions(ax, start_date='2001-01-01')
    set_xlim_to_data(ax, q_plot.index)
    add_last_value_label(ax, q_plot, THEME['primary'], fmt='{:.1f}%')

    last_val = q_plot.iloc[-1]
    add_annotation_box(ax, f'Quits at {last_val:.1f}%: sitting on the exact threshold\nthat preceded the last three recessions.',
                       x=0.40, y=0.92)

    ax.legend(loc='upper left', **legend_style())
    brand_fig(fig, 'JOLTS Quits Rate: Sitting on the Line',
              'Total nonfarm quits rate, seasonally adjusted',
              'BLS JOLTS', data_date=q_plot.index[-1])
    return save_fig(fig, 'fig02_quits_rate.png')


# =============================================================================
# FIGURE 3: JOLTS JOB OPENINGS RATE
# =============================================================================

def fig03_openings_rate():
    print('Building Figure 3: Job Openings Rate...')
    openings = load_series('BLS_JTS000000000000000JOR', start='2001-01-01')

    fig, ax = new_fig()
    style_single_ax(ax)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.1f}%'))

    o_plot = openings.dropna()
    ax.fill_between(o_plot.index, o_plot, alpha=THEME['fill_alpha'], color=THEME['primary'], zorder=1)
    ax.plot(o_plot.index, o_plot, color=THEME['primary'], linewidth=2.5,
            label=f'Openings Rate ({o_plot.iloc[-1]:.1f}%)', zorder=2)

    add_recessions(ax, start_date='2001-01-01')
    set_xlim_to_data(ax, o_plot.index)
    add_last_value_label(ax, o_plot, THEME['primary'], fmt='{:.1f}%')

    last_val = o_plot.iloc[-1]
    add_annotation_box(ax, f'Openings rate at {last_val:.1f}%: lowest since 2020.\nProfessional services, retail, and finance leading the decline.',
                       x=0.50, y=0.92)

    ax.legend(loc='upper left', **legend_style())
    brand_fig(fig, 'JOLTS Job Openings Rate: Collapse to 2020 Lows',
              'Total nonfarm job openings rate, seasonally adjusted',
              'BLS JOLTS', data_date=o_plot.index[-1])
    return save_fig(fig, 'fig03_openings_rate.png')


# =============================================================================
# FIGURE 4: LABOR FRAGILITY INDEX (LFI)
# =============================================================================

def fig04_lfi():
    print('Building Figure 4: LFI...')
    lfi = load_index('LFI', start='2015-01-01')

    fig, ax = new_fig()
    style_single_ax(ax)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.2f}'))

    lfi_plot = lfi.dropna()
    ax.plot(lfi_plot.index, lfi_plot, color=THEME['primary'], linewidth=2.5,
            label=f'LFI ({lfi_plot.iloc[-1]:.2f})')

    # +0.5 threshold
    ax.axhline(0.5, color=THEME['accent'], linewidth=1.5, linestyle='--', alpha=0.7)
    ax.text(0.02, 0.55, '+0.5 Elevated Fragility', fontsize=9, color=THEME['accent'],
            alpha=0.8, fontstyle='italic', transform=ax.get_yaxis_transform())

    # Zero line
    ax.axhline(0, color=THEME['zero_line'], linewidth=0.8, linestyle='--', alpha=0.5)

    add_recessions(ax, start_date='2015-01-01')
    set_xlim_to_data(ax, lfi_plot.index)
    add_last_value_label(ax, lfi_plot, THEME['primary'], fmt='{:.2f}')

    last_val = lfi_plot.iloc[-1]
    add_annotation_box(ax, f'LFI at {last_val:+.2f}: well above the +0.50 fragility threshold.\nLong-term unemployment building, quits decelerating.',
                       x=0.50, y=0.15)

    ax.legend(loc='upper left', **legend_style())
    brand_fig(fig, 'Labor Fragility Index (LFI): Structural Weakness Building',
              'z(Long-Term Unemp, -Quits, -Hires/Quits)',
              'BLS, Lighthouse Macro')
    return save_fig(fig, 'fig04_lfi.png')


# =============================================================================
# FIGURE 5: HY OAS
# =============================================================================

def fig05_hy_oas():
    print('Building Figure 5: HY OAS...')
    hy = load_series('BAMLH0A0HYM2', start='2015-01-01')

    fig, ax = new_fig()
    style_single_ax(ax)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.0f} bps'))

    hy_plot = (hy * 100).dropna()  # Convert to bps
    ax.fill_between(hy_plot.index, hy_plot, alpha=THEME['fill_alpha'], color=THEME['primary'], zorder=1)
    ax.plot(hy_plot.index, hy_plot, color=THEME['primary'], linewidth=2.5,
            label=f'HY OAS ({hy_plot.iloc[-1]:.0f} bps)', zorder=2)

    # 300 bps complacent threshold
    ax.axhline(300, color=THEME['accent'], linewidth=1.5, linestyle='--', alpha=0.7, zorder=5)
    ax.text(0.02, 310, '300 bps: Complacent Threshold', fontsize=9, color=THEME['accent'],
            alpha=0.8, fontstyle='italic', transform=ax.get_yaxis_transform())

    add_recessions(ax, start_date='2015-01-01')
    set_xlim_to_data(ax, hy_plot.index)
    add_last_value_label(ax, hy_plot, THEME['primary'], fmt='{:.0f}')

    last_val = hy_plot.iloc[-1]
    add_annotation_box(ax, f'HY OAS at {last_val:.0f} bps: below the 300 bps complacent\nthreshold. Credit pricing a different economy than labor.',
                       x=0.70, y=0.92)

    ax.legend(loc='upper left', **legend_style())
    brand_fig(fig, 'HY OAS: Credit Still in Denial',
              'ICE BofA US High Yield Option-Adjusted Spread',
              'FRED (ICE/BofA)', data_date=hy_plot.index[-1])
    return save_fig(fig, 'fig05_hy_oas.png')


# =============================================================================
# FIGURE 5 (NEW): CREDIT-LABOR DIVERGENCE — HY OAS (inv) vs QUITS
# =============================================================================

def fig05_credit_labor_divergence():
    print('Building Figure 5: Credit-Labor Divergence...')
    quits = load_series('JTSQUR', start='2001-01-01')
    hy = load_series('BAMLH0A0HYM2', start='2001-01-01')

    fig, ax1 = new_fig()
    ax2 = ax1.twinx()

    c_primary = THEME['primary']    # Ocean — Quits on RHS
    c_secondary = THEME['secondary']  # Dusk — HY OAS inverted on LHS

    style_dual_ax(ax1, ax2, c_secondary, c_primary)

    # RHS = Primary = Quits Rate (Ocean)
    q_plot = quits.dropna()
    ax2.plot(q_plot.index, q_plot, color=c_primary, linewidth=2.5,
             label=f'Quits Rate ({q_plot.iloc[-1]:.1f}%)', zorder=2)
    ax2.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.1f}%'))

    # LHS = Secondary = HY OAS inverted (Dusk)
    hy_bps = (hy * 100).dropna()  # Convert to bps
    ax1.plot(hy_bps.index, hy_bps, color=c_secondary, linewidth=2.0,
             label=f'HY OAS ({hy_bps.iloc[-1]:.0f} bps)', zorder=2)
    ax1.invert_yaxis()  # INVERTED — low spreads go UP
    ax1.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.0f}'))

    # Scale axes so pre-2020 lines roughly tracked
    ax2.set_ylim(1.45, 3.225)
    ax1.set_ylim(1050, 150)  # Inverted: 150 at top, 1050 at bottom

    # Reference lines
    # 2.0% quits threshold on RHS
    ax2.axhline(2.0, color=THEME['accent'], linewidth=1.5, linestyle='--',
                alpha=0.7, zorder=5)
    ax2.text(0.37, 2.07, '2.0% Quits Threshold', fontsize=9, color=THEME['accent'],
             alpha=0.8, fontstyle='italic', transform=ax2.get_yaxis_transform())

    # 300 bps HY OAS threshold on LHS (inverted)
    ax1.axhline(300, color=THEME['accent'], linewidth=1.5, linestyle='--',
                alpha=0.5, zorder=5)
    ax1.text(0.02, 330, '300 bps Complacent', fontsize=9, color=THEME['accent'],
             alpha=0.5, fontstyle='italic', transform=ax1.get_yaxis_transform())

    add_recessions(ax1, start_date='2001-01-01')
    set_xlim_to_data(ax1, q_plot.loc['2020-01-01':].index)

    add_last_value_label(ax2, q_plot, c_primary, fmt='{:.1f}%', side='right')
    add_last_value_label(ax1, hy_bps, c_secondary, fmt='{:.0f}', side='left')

    add_annotation_box(ax1, 'Credit and labor are pricing two different economies.\nThe divergence has persisted for over two years.',
                       x=0.50, y=0.97)

    # Combined legend
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', **legend_style())

    # Use quits date (monthly, lags daily HY OAS)
    brand_fig(fig, 'The Divergence: Credit Spreads vs Labor Flows',
              'HY OAS (inverted) vs JOLTS quits rate',
              'FRED (ICE/BofA, BLS JOLTS)', data_date=q_plot.index[-1])
    return save_fig(fig, 'fig05_credit_labor_divergence.png')


# =============================================================================
# FIGURE 6: CREDIT-LABOR GAP (CLG) — PROPRIETARY, DISABLED
# =============================================================================

def fig06_clg():
    print('Building Figure 6: CLG...')
    clg = load_index('CLG', start='2015-01-01')

    fig, ax = new_fig()
    style_single_ax(ax)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.1f}'))

    clg_plot = clg.dropna()
    ax.plot(clg_plot.index, clg_plot, color=THEME['primary'], linewidth=2.5,
            label=f'CLG ({clg_plot.iloc[-1]:.2f})')
    ax.fill_between(clg_plot.index, clg_plot, alpha=THEME['fill_alpha'], color=THEME['primary'])

    # -1.0 threshold
    ax.axhline(-1.0, color=THEME['accent'], linewidth=1.5, linestyle='--', alpha=0.7)
    ax.text(0.02, -0.85, '-1.0: Credit Ignoring Fundamentals', fontsize=9, color=THEME['accent'],
            alpha=0.8, fontstyle='italic', transform=ax.get_yaxis_transform())

    # Zero line
    ax.axhline(0, color=THEME['zero_line'], linewidth=0.8, linestyle='--', alpha=0.5)

    add_recessions(ax, start_date='2015-01-01')
    set_xlim_to_data(ax, clg_plot.index)
    add_last_value_label(ax, clg_plot, THEME['primary'], fmt='{:.2f}')

    last_val = clg_plot.iloc[-1]
    add_annotation_box(ax, f'CLG at {last_val:.2f}: deeply below -1.0 threshold.\nSpreads too tight for the labor reality underneath.',
                       x=0.50, y=0.92)

    ax.legend(loc='upper left', **legend_style())
    brand_fig(fig, 'Credit-Labor Gap (CLG): Deeply Negative',
              'z(HY OAS) - z(LFI): negative = credit too complacent',
              'FRED, BLS, Lighthouse Macro')
    return save_fig(fig, 'fig06_clg.png')


# =============================================================================
# FIGURE 7: VIX
# =============================================================================

def fig07_vix():
    print('Building Figure 7: VIX...')
    vix = load_series('VIXCLS', start='2004-01-01')

    fig, ax = new_fig()
    style_single_ax(ax)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.0f}'))

    v_plot = vix.dropna()

    # 50-day MA
    vix_50d = v_plot.rolling(50).mean()

    ax.plot(v_plot.index, v_plot, color=THEME['primary'], linewidth=2.0, alpha=0.8,
            label=f'VIX ({v_plot.iloc[-1]:.1f})', zorder=2)
    ax.plot(vix_50d.dropna().index, vix_50d.dropna(), color=THEME['secondary'], linewidth=2.0,
            linestyle='-', label=f'50d MA ({vix_50d.dropna().iloc[-1]:.1f})', zorder=3)

    # Reference zones
    ax.axhspan(10, 16, color='#238923', alpha=0.08, zorder=0)
    ax.axhspan(25, 45, color='#892323', alpha=0.08, zorder=0)
    ax.text(0.98, 11.5, 'Complacent Zone', fontsize=8, color='#238923', alpha=0.6,
            fontstyle='italic', ha='right', transform=ax.get_yaxis_transform())
    ax.text(0.98, 30, 'Fear Zone', fontsize=8, color='#892323', alpha=0.6,
            fontstyle='italic', ha='right', transform=ax.get_yaxis_transform())

    add_recessions(ax, start_date='2004-01-01')
    set_xlim_to_data(ax, v_plot.loc['2020-01-01':].index)
    add_last_value_label(ax, v_plot, THEME['primary'], fmt='{:.1f}')
    add_last_value_label(ax, vix_50d.dropna(), THEME['secondary'], fmt='{:.1f}', side='right')

    last_val = v_plot.iloc[-1]
    add_annotation_box(ax, f'VIX at {last_val:.1f}: no longer complacent, not yet panicking.\nSCOTUS relief compressed the tariff tail.',
                       x=0.55, y=0.92)

    ax.legend(loc='upper left', **legend_style())
    brand_fig(fig, 'VIX: From Complacency to Recalibration',
              'CBOE Volatility Index with 50-day moving average',
              'CBOE via FRED', data_date=v_plot.index[-1])
    return save_fig(fig, 'fig07_vix.png')


# =============================================================================
# FIGURE 8: SOFR vs EFFR
# =============================================================================

def fig08_sofr_effr():
    print('Building Figure 8: SOFR vs EFFR...')
    sofr = load_series('OFR_FNYR-SOFR-A', start='2022-01-01')
    effr = load_series('OFR_FNYR-EFFR-A', start='2022-01-01')

    fig, ax = new_fig()
    style_single_ax(ax)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.2f}%'))

    s_plot = sofr.dropna()
    e_plot = effr.dropna()

    ax.plot(s_plot.index, s_plot, color=THEME['primary'], linewidth=2.5,
            label=f'SOFR ({s_plot.iloc[-1]:.2f}%)', zorder=2)
    ax.plot(e_plot.index, e_plot, color=THEME['secondary'], linewidth=2.0,
            label=f'EFFR ({e_plot.iloc[-1]:.2f}%)', zorder=2)

    # Spread as shaded area
    common_idx = s_plot.index.intersection(e_plot.index)
    s_common = s_plot.reindex(common_idx)
    e_common = effr.reindex(common_idx).ffill()
    spread = s_common - e_common

    set_xlim_to_data(ax, s_plot.index)
    add_last_value_label(ax, s_plot, THEME['primary'], fmt='{:.2f}%')
    add_last_value_label(ax, e_plot, THEME['secondary'], fmt='{:.2f}%', side='left')

    last_spread = (s_plot.iloc[-1] - e_plot.iloc[-1]) * 100
    add_annotation_box(ax, f'SOFR-EFFR spread: ~{last_spread:.0f} bps. Defensive, not Disorderly.\nThe One Switch: 15-20 bps = regime change.',
                       x=0.50, y=0.20)

    ax.legend(loc='upper left', **legend_style())
    brand_fig(fig, 'SOFR vs EFFR: The One Switch',
              'Secured vs unsecured overnight funding rates',
              'NY Fed', data_date=s_plot.index[-1])
    return save_fig(fig, 'fig08_sofr_effr.png')


# =============================================================================
# FIGURE 9: LIQUIDITY CUSHION INDEX (LCI)
# =============================================================================

def fig09_lci():
    print('Building Figure 9: LCI...')
    lci = load_index('LCI', start='2019-01-01')

    fig, ax = new_fig()
    style_single_ax(ax)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.2f}'))

    lci_plot = lci.dropna()
    ax.plot(lci_plot.index, lci_plot, color=THEME['primary'], linewidth=2.5,
            label=f'LCI ({lci_plot.iloc[-1]:.2f})')

    # Regime bands
    ax.axhspan(-0.5, -3.0, color='#892323', alpha=0.12)
    ax.axhspan(-0.5, 0.5, color='#00BB89', alpha=0.08)
    ax.axhspan(0.5, 3.0, color='#00BBFF', alpha=0.08)

    ax.text(0.98, -1.0, 'SCARCE', transform=ax.get_yaxis_transform(),
            fontsize=9, color='#892323', va='center', ha='right', fontweight='bold', alpha=0.8)
    ax.text(0.98, 0.0, 'ADEQUATE', transform=ax.get_yaxis_transform(),
            fontsize=9, color='#00BB89', va='center', ha='right', fontweight='bold', alpha=0.8)
    ax.text(0.98, 1.0, 'ABUNDANT', transform=ax.get_yaxis_transform(),
            fontsize=9, color='#00BBFF', va='center', ha='right', fontweight='bold', alpha=0.8)

    # -0.5 threshold
    ax.axhline(-0.5, color=THEME['accent'], linewidth=1.5, linestyle='--', alpha=0.7)
    ax.text(0.02, -0.42, '-0.5: Scarce Regime', fontsize=9, color=THEME['accent'],
            alpha=0.8, fontstyle='italic', transform=ax.get_yaxis_transform())

    # Zero line
    ax.axhline(0, color=THEME['zero_line'], linewidth=0.8, linestyle='--', alpha=0.5)

    add_recessions(ax, start_date='2019-01-01')
    set_xlim_to_data(ax, lci_plot.index)
    add_last_value_label(ax, lci_plot, THEME['primary'], fmt='{:.2f}')

    last_val = lci_plot.iloc[-1]
    add_annotation_box(ax, f'LCI at {last_val:.2f}: approaching but not yet breaching -0.50.\nRRP exhausted. System operating without a shock absorber.',
                       x=0.45, y=0.92)

    ax.legend(loc='upper left', **legend_style())
    brand_fig(fig, 'Liquidity Cushion Index (LCI): Approaching Scarce',
              'Reserves, RRP, funding spreads composite',
              'NY Fed, OFR, FRED, Lighthouse Macro')
    return save_fig(fig, 'fig09_lci.png')


# =============================================================================
# FIGURE 10: 10Y-2Y CURVE + TERM PREMIUM
# =============================================================================

def fig10_yield_curve():
    print('Building Figure 10: Yield Curve...')
    curve = load_series('T10Y2Y', start='2015-01-01')
    ten_yr = load_series('DGS10', start='2015-01-01')

    fig, ax1 = new_fig()
    ax2 = ax1.twinx()

    c_primary = THEME['primary']
    c_secondary = THEME['secondary']
    style_dual_ax(ax1, ax2, c_secondary, c_primary)

    # RHS = Primary = 10Y-2Y Curve (Ocean)
    c_plot = curve.dropna()
    ax2.fill_between(c_plot.index, c_plot, alpha=0.10, color=c_primary, zorder=1)
    ax2.plot(c_plot.index, c_plot, color=c_primary, linewidth=2.5,
             label=f'10Y-2Y Spread ({c_plot.iloc[-1]:.2f}%)', zorder=2)
    ax2.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.1f}%'))

    # LHS = Secondary = 10Y Yield (Dusk)
    t_plot = ten_yr.dropna()
    ax1.plot(t_plot.index, t_plot, color=c_secondary, linewidth=2.0,
             label=f'10Y Yield ({t_plot.iloc[-1]:.2f}%)', zorder=2)
    ax1.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.1f}%'))

    # Zero line on curve
    ax2.axhline(0, color=THEME['zero_line'], linewidth=0.8, linestyle='--', alpha=0.5, zorder=5)

    add_recessions(ax1, start_date='2015-01-01')
    set_xlim_to_data(ax1, c_plot.index)

    add_last_value_label(ax2, c_plot, c_primary, fmt='{:.2f}%', side='right')
    add_last_value_label(ax1, t_plot, c_secondary, fmt='{:.2f}%', side='left')

    last_curve = c_plot.iloc[-1]
    add_annotation_box(ax1, f'10Y-2Y at +{last_curve*100:.0f} bps. Steepener building:\ndeficit dynamics, tariff pass-through, anchored front end.',
                       x=0.50, y=0.97)

    # Combined legend
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right', **legend_style())

    brand_fig(fig, '10Y-2Y Curve: Steepener Building',
              'Treasury term structure with 10Y yield overlay',
              'FRED (US Treasury)', data_date=c_plot.index[-1])
    return save_fig(fig, 'fig10_yield_curve.png')


# =============================================================================
# FIGURE 11: MRI (MACRO RISK INDEX)
# =============================================================================

def fig11_mri():
    print('Building Figure 11: MRI...')
    mri = load_index('MRI', start='2019-01-01')

    fig, ax = new_fig()
    style_single_ax(ax)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.2f}'))

    mri_plot = mri.dropna()
    ax.plot(mri_plot.index, mri_plot, color=THEME['primary'], linewidth=2.5,
            label=f'MRI ({mri_plot.iloc[-1]:.2f})')

    # Regime bands
    add_regime_bands(ax)
    ax.set_ylim(-2.0, 2.5)

    # Zero line
    ax.axhline(0, color=THEME['zero_line'], linewidth=0.8, linestyle='--', alpha=0.5)

    add_recessions(ax, start_date='2019-01-01')
    set_xlim_to_data(ax, mri_plot.index)
    add_last_value_label(ax, mri_plot, THEME['primary'], fmt='{:.2f}')

    last_val = mri_plot.iloc[-1]
    # Determine regime
    if last_val > 1.5:
        regime = 'Crisis'
    elif last_val > 1.0:
        regime = 'High Risk'
    elif last_val > 0.5:
        regime = 'Elevated'
    elif last_val > -0.5:
        regime = 'Neutral'
    else:
        regime = 'Low Risk'

    add_annotation_box(ax, f'MRI at {last_val:.2f}: {regime} regime.\nLabor and credit divergence persists. Defensive posture holds.',
                       x=0.50, y=0.15)

    ax.legend(loc='upper left', **legend_style())
    brand_fig(fig, 'Macro Risk Index (MRI): Regime Classification',
              'Master composite synthesizing all 12 pillars',
              'Lighthouse Macro')
    return save_fig(fig, 'fig11_mri.png')


# =============================================================================
# MAIN
# =============================================================================

if __name__ == '__main__':
    print(f'\n{"="*60}')
    print('LIGHTHOUSE MACRO — Positioning Update #2 Charts')
    print(f'{"="*60}\n')

    paths = []
    paths.append(fig01_defensive_basket())       # Fig 1: Defensive Basket vs SPY (NEW)
    paths.append(fig02_quits_rate())              # Fig 2: JOLTS Quits Rate
    paths.append(fig03_openings_rate())           # Fig 3: JOLTS Openings Rate
    paths.append(fig05_hy_oas())                  # Fig 4: HY OAS  (rename below)
    paths.append(fig05_credit_labor_divergence()) # Fig 5: Credit-Labor Divergence (NEW)
    paths.append(fig07_vix())                     # Fig 6: VIX     (rename below)
    paths.append(fig08_sofr_effr())               # Fig 7: SOFR/EFFR (rename below)
    paths.append(fig10_yield_curve())             # Fig 8: Yield Curve (rename below)

    # Rename files to match new 1-8 numbering
    import shutil
    renames = {
        'fig05_hy_oas.png': 'fig04_hy_oas.png',
        'fig07_vix.png': 'fig06_vix.png',
        'fig08_sofr_effr.png': 'fig07_sofr_effr.png',
        'fig10_yield_curve.png': 'fig08_yield_curve.png',
    }
    for old_name, new_name in renames.items():
        old_path = os.path.join(OUT_DIR, old_name)
        new_path = os.path.join(OUT_DIR, new_name)
        if os.path.exists(old_path):
            shutil.move(old_path, new_path)
            print(f'  Renamed: {old_name} -> {new_name}')

    print(f'\n{"="*60}')
    print(f'All {len(paths)} charts saved to: {OUT_DIR}')
    print(f'{"="*60}')
