#!/usr/bin/env python3
"""
LIGHTHOUSE MACRO - BRIEF CHART LIBRARY
========================================
~45 chart functions organized by pillar, white theme primary.
Used by the morning brief via release_chart_selector.

Each function takes a sqlite3.Connection and returns:
    {"title": str, "base64": str}

All data comes from the master DB. No external API calls.
"""

import io
import base64
import sqlite3
from datetime import datetime, timedelta

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
import matplotlib.image as mpimg
import pandas as pd
import numpy as np
from pathlib import Path

# ============================================================
# BRAND PALETTE
# ============================================================

COLORS = {
    'ocean': '#2389BB',
    'dusk': '#FF6723',
    'sky': '#00BBFF',
    'venus': '#FF2389',
    'sea': '#00BB89',
    'doldrums': '#898989',
    'starboard': '#238923',
    'port': '#892323',
    'fog': '#D1D1D1',
}

# White theme (primary for all publications)
THEME = {
    'bg': '#ffffff',
    'fg': '#1a1a1a',
    'muted': '#555555',
    'spine': '#898989',
    'zero_line': '#D1D1D1',
    'recession': 'gray',
    'recession_alpha': 0.12,
    'fill_alpha': 0.15,
}

ICON_PATH = '/Users/bob/LHM/Brand/icon_transparent_128.png'

RECESSIONS = [
    ('2001-03-01', '2001-11-01'),
    ('2007-12-01', '2009-06-01'),
    ('2020-02-01', '2020-04-01'),
]

MRI_REGIMES = [
    (-999, -0.20, COLORS['sea'], 'Early Expansion', 0.06),
    (-0.20, 0.10, COLORS['ocean'], 'Mid-Cycle', 0.04),
    (0.10, 0.25, COLORS['dusk'], 'Late Cycle', 0.06),
    (0.25, 0.50, COLORS['venus'], 'Pre-Recession', 0.06),
    (0.50, 999, COLORS['port'], 'Recession', 0.08),
]


# ============================================================
# DATA HELPERS
# ============================================================

def _fetch_series(conn, series_id, start_date='2022-01-01'):
    """Fetch a single series from observations table."""
    query = """
        SELECT date, value FROM observations
        WHERE series_id = ? AND date >= ?
        ORDER BY date
    """
    df = pd.read_sql(query, conn, params=[series_id, start_date],
                     parse_dates=['date'])
    if df.empty:
        return pd.Series(dtype=float)
    df = df.set_index('date')
    df = df[~df.index.duplicated(keep='last')]
    return df['value'].dropna()


def _fetch_index(conn, index_id, start_date='2022-01-01'):
    """Fetch an index from lighthouse_indices table."""
    query = """
        SELECT date, value, status FROM lighthouse_indices
        WHERE index_id = ? AND date >= ?
        ORDER BY date
    """
    df = pd.read_sql(query, conn, params=[index_id, start_date],
                     parse_dates=['date'])
    if df.empty:
        return pd.DataFrame()
    df = df.set_index('date')
    df = df[~df.index.duplicated(keep='last')]
    return df


def _yoy_pct(series, periods=12):
    """Compute YoY % change."""
    return series.pct_change(periods, fill_method=None) * 100


# ============================================================
# STYLING HELPERS (white theme)
# ============================================================

def _style_ax(ax):
    """Apply white theme styling."""
    ax.set_facecolor(THEME['bg'])
    ax.grid(False)
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_color(THEME['spine'])
        spine.set_linewidth(0.5)
    ax.tick_params(colors=THEME['fg'], which='both', length=0, labelsize=8)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %y'))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    ax.yaxis.tick_right()
    ax.yaxis.set_label_position('right')


def _add_last_value(ax, series, color, fmt='.2f', side='right'):
    """Add a last-value pill label."""
    if series.empty:
        return
    last_val = series.iloc[-1]
    txt = f'{last_val:{fmt}}'
    ax.annotate(txt, xy=(1.01, last_val), xycoords=('axes fraction', 'data'),
                fontsize=8, fontweight='bold', color='white',
                bbox=dict(boxstyle='round,pad=0.3', facecolor=color,
                          edgecolor='none', alpha=0.9),
                va='center', ha='left')


def _add_recessions(ax, start_date='2022-01-01'):
    """Add NBER recession shading (gray for white theme)."""
    start = pd.Timestamp(start_date)
    for r_start, r_end in RECESSIONS:
        rs, re = pd.Timestamp(r_start), pd.Timestamp(r_end)
        if re >= start:
            ax.axvspan(max(rs, start), re, color=THEME['recession'],
                       alpha=THEME['recession_alpha'], zorder=0)


def _zero_line(ax):
    """Add a zero reference line."""
    ax.axhline(y=0, color=THEME['zero_line'], linewidth=0.8, linestyle='--')


def _threshold_line(ax, y, label, color=None):
    """Add a threshold reference line with label."""
    color = color or COLORS['venus']
    ax.axhline(y=y, color=color, linewidth=0.8, linestyle='--', alpha=0.7)


def _make_fig(title):
    """Create a branded figure (white theme)."""
    fig, ax = plt.subplots(figsize=(10, 4.5))
    fig.patch.set_facecolor(THEME['bg'])
    ax.set_facecolor(THEME['bg'])

    # Title left-aligned
    ax.set_title(title, fontsize=11, fontweight='bold',
                 color=THEME['fg'], pad=12, loc='left',
                 fontfamily='sans-serif')

    # Brand text top-right
    fig.text(0.98, 0.98, 'LIGHTHOUSE MACRO', fontsize=7,
             color=COLORS['ocean'], fontweight='bold', ha='right', va='top',
             alpha=0.6)

    return fig, ax


def _fig_to_base64(fig):
    """Convert figure to base64 PNG string."""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=150, bbox_inches='tight',
                pad_inches=0.08, facecolor=THEME['bg'], edgecolor='none')
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.getvalue()).decode('utf-8')


# ============================================================
# ALWAYS-ON CHARTS
# ============================================================

def chart_mri(conn):
    """MRI time series with regime bands."""
    df = _fetch_index(conn, 'MRI', '2024-01-01')
    fig, ax = _make_fig('Macro Risk Index (MRI)')
    _style_ax(ax)

    if not df.empty:
        for lo, hi, color, label, alpha in MRI_REGIMES:
            ax.axhspan(max(lo, -1.5), min(hi, 1.5), color=color,
                       alpha=alpha, zorder=0)
        ax.plot(df.index, df['value'], color=COLORS['ocean'],
                linewidth=2.5, zorder=5)
        _zero_line(ax)
        _add_last_value(ax, df['value'], COLORS['ocean'], fmt='.3f')
        if not df.empty:
            last_status = df['status'].iloc[-1] or ''
            ax.text(0.99, 0.95, last_status, transform=ax.transAxes,
                    fontsize=9, color=COLORS['ocean'], fontweight='bold',
                    ha='right', va='top',
                    bbox=dict(boxstyle='round,pad=0.3',
                              facecolor=THEME['bg'], edgecolor=COLORS['ocean'],
                              alpha=0.9))

    ax.set_ylim(-0.8, 0.8)
    return {'title': 'Macro Risk Index', 'base64': _fig_to_base64(fig)}


def chart_spx(conn):
    """S&P 500: 3-panel (Price + MAs, RS vs ACWX, Z-RoC)."""
    spx = _fetch_series(conn, 'SPX_Close', '2023-01-01')
    ma200 = _fetch_series(conn, 'SPX_200d_MA', '2023-01-01')
    ma50 = _fetch_series(conn, 'SPX_50d_MA', '2023-01-01')
    zroc = _fetch_series(conn, 'SPX_Z_RoC_63d', '2023-01-01')

    fig, axes = plt.subplots(3, 1, figsize=(10, 10), height_ratios=[3, 1.5, 1.5])
    fig.patch.set_facecolor(THEME['bg'])

    # Brand text top-right
    fig.text(0.98, 0.99, 'LIGHTHOUSE MACRO', fontsize=7,
             color=COLORS['ocean'], fontweight='bold', ha='right', va='top',
             alpha=0.6)

    # ---- Panel 1: Price + MAs ----
    ax1 = axes[0]
    ax1.set_title('S&P 500', fontsize=11, fontweight='bold',
                   color=THEME['fg'], pad=12, loc='left', fontfamily='sans-serif')
    _style_ax(ax1)

    if not spx.empty:
        ax1.plot(spx.index, spx, color=COLORS['doldrums'], linewidth=1.5,
                 label='Price', zorder=2)
        ax1.fill_between(spx.index, spx.min() * 0.98, spx,
                         color=COLORS['doldrums'], alpha=0.04, zorder=1)
    if not ma50.empty:
        ax1.plot(ma50.index, ma50, color=COLORS['dusk'], linewidth=2,
                 label='50d MA', zorder=3)
    if not ma200.empty:
        ax1.plot(ma200.index, ma200, color=COLORS['ocean'], linewidth=2.5,
                 label='200d MA', zorder=4)
    if not spx.empty:
        _add_last_value(ax1, spx, COLORS['doldrums'], fmt=',.0f')
    ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:,.0f}'))
    ax1.legend(loc='upper left', fontsize=7, facecolor=THEME['bg'],
               edgecolor=THEME['spine'], labelcolor=THEME['fg'])

    # ---- Panel 2: Relative Strength vs ACWX ----
    ax2 = axes[1]
    ax2.set_title('Relative Strength vs ACWX', fontsize=9, fontweight='bold',
                   color=THEME['fg'], pad=8, loc='left', fontfamily='sans-serif')
    _style_ax(ax2)

    try:
        import yfinance as yf
        acwx = yf.download('ACWX', start='2022-06-01', progress=False, auto_adjust=True)
        if not acwx.empty:
            acwx_close = acwx['Close'].squeeze()
            acwx_close.index = acwx_close.index.tz_localize(None)
            # Align dates
            common = spx.index.intersection(acwx_close.index)
            if len(common) > 50:
                rs = (spx.loc[common] / acwx_close.loc[common])
                rs = rs / rs.iloc[0] * 100  # Rebase to 100
                rs_ma50 = rs.rolling(50, min_periods=25).mean()
                ax2.plot(rs.index, rs, color=COLORS['ocean'], linewidth=2, label='SPX/ACWX')
                ax2.plot(rs_ma50.index, rs_ma50, color=COLORS['dusk'], linewidth=1.2,
                         linestyle='--', alpha=0.8, label='50d MA')
                _add_last_value(ax2, rs, COLORS['ocean'], fmt='.1f')
                ax2.legend(loc='upper left', fontsize=7, facecolor=THEME['bg'],
                           edgecolor=THEME['spine'], labelcolor=THEME['fg'])
            else:
                ax2.text(0.5, 0.5, 'Insufficient ACWX data', transform=ax2.transAxes,
                         ha='center', va='center', color=THEME['muted'], fontsize=9)
        else:
            ax2.text(0.5, 0.5, 'ACWX data unavailable', transform=ax2.transAxes,
                     ha='center', va='center', color=THEME['muted'], fontsize=9)
    except Exception:
        ax2.text(0.5, 0.5, 'ACWX data unavailable', transform=ax2.transAxes,
                 ha='center', va='center', color=THEME['muted'], fontsize=9)

    # ---- Panel 3: Z-RoC (63d) ----
    ax3 = axes[2]
    ax3.set_title('Z-RoC (63-Day Momentum)', fontsize=9, fontweight='bold',
                   color=THEME['fg'], pad=8, loc='left', fontfamily='sans-serif')
    _style_ax(ax3)

    if not zroc.empty:
        ax3.fill_between(zroc.index, 0, zroc, where=zroc >= 0,
                         color=COLORS['sea'], alpha=THEME['fill_alpha'])
        ax3.fill_between(zroc.index, 0, zroc, where=zroc < 0,
                         color=COLORS['port'], alpha=THEME['fill_alpha'])
        ax3.plot(zroc.index, zroc, color=COLORS['ocean'], linewidth=2)
        _add_last_value(ax3, zroc, COLORS['ocean'], fmt='.2f')
        _threshold_line(ax3, 1.5, '', COLORS['venus'])
        _threshold_line(ax3, -1.5, '', COLORS['venus'])
    _zero_line(ax3)

    fig.tight_layout(h_pad=1.5)
    return {'title': 'S&P 500', 'base64': _fig_to_base64(fig)}


# ============================================================
# PILLAR 1: LABOR
# ============================================================

def chart_unemployment_rate(conn):
    """Unemployment rate (U3 and U6)."""
    u3 = _fetch_series(conn, 'UNRATE', '2018-01-01')
    u6 = _fetch_series(conn, 'U6RATE', '2018-01-01')
    fig, ax = _make_fig('Unemployment Rate')
    _style_ax(ax)

    if not u3.empty:
        ax.plot(u3.index, u3, color=COLORS['ocean'], linewidth=2.5, label='U-3')
        _add_last_value(ax, u3, COLORS['ocean'], fmt='.1f')
    if not u6.empty:
        ax.plot(u6.index, u6, color=COLORS['dusk'], linewidth=1.5,
                linestyle='--', label='U-6', alpha=0.8)
    if not u3.empty or not u6.empty:
        ax.legend(loc='upper right', fontsize=7, facecolor=THEME['bg'],
                  edgecolor=THEME['spine'], labelcolor=THEME['fg'])
    _add_recessions(ax, '2018-01-01')
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:.1f}%'))
    return {'title': 'Unemployment Rate', 'base64': _fig_to_base64(fig)}


def chart_nfp_momentum(conn):
    """Nonfarm Payrolls MoM change (bar chart)."""
    nfp = _fetch_series(conn, 'PAYEMS', '2020-01-01')
    fig, ax = _make_fig('Nonfarm Payrolls (MoM Change, Thousands)')
    _style_ax(ax)

    if not nfp.empty:
        mom = nfp.diff() / 1000  # Already in thousands from FRED, diff gives change
        # NFP is in thousands, diff is the MoM change
        mom_k = nfp.diff()
        if mom_k.max() > 1000:
            mom_k = mom_k / 1000  # Convert if in units
        colors = [COLORS['sea'] if v >= 0 else COLORS['port'] for v in mom_k.dropna()]
        ax.bar(mom_k.dropna().index, mom_k.dropna(), width=25,
               color=colors, alpha=0.7)
        ma3 = mom_k.rolling(3).mean()
        ax.plot(ma3.dropna().index, ma3.dropna(), color=COLORS['ocean'],
                linewidth=2, label='3-mo avg')
        _zero_line(ax)
        ax.legend(loc='upper left', fontsize=7, facecolor=THEME['bg'],
                  edgecolor=THEME['spine'], labelcolor=THEME['fg'])
    _add_recessions(ax, '2020-01-01')
    return {'title': 'Nonfarm Payrolls', 'base64': _fig_to_base64(fig)}


def chart_wages(conn):
    """Average Hourly Earnings YoY."""
    ahe = _fetch_series(conn, 'CES0500000003', '2018-01-01')
    fig, ax = _make_fig('Average Hourly Earnings (YoY %)')
    _style_ax(ax)

    if not ahe.empty:
        yoy = _yoy_pct(ahe)
        yoy = yoy.dropna().loc['2019-01-01':]
        ax.plot(yoy.index, yoy, color=COLORS['ocean'], linewidth=2.5)
        _add_last_value(ax, yoy, COLORS['ocean'], fmt='.1f')
        _threshold_line(ax, 3.5, '3.5% (Fed comfort)', COLORS['sea'])
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:.1f}%'))
    _add_recessions(ax, '2019-01-01')
    return {'title': 'Wage Growth', 'base64': _fig_to_base64(fig)}


def chart_lfpr(conn):
    """Labor Force Participation Rate (Prime Age 25-54)."""
    lfpr = _fetch_series(conn, 'LNS11300060', '2018-01-01')
    fig, ax = _make_fig('Prime Age LFPR (25-54)')
    _style_ax(ax)

    if not lfpr.empty:
        ax.plot(lfpr.index, lfpr, color=COLORS['ocean'], linewidth=2.5)
        _add_last_value(ax, lfpr, COLORS['ocean'], fmt='.1f')
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:.1f}%'))
    _add_recessions(ax, '2018-01-01')
    return {'title': 'Prime Age LFPR', 'base64': _fig_to_base64(fig)}


def chart_jolts_quits(conn):
    """JOLTS Quits Rate with threshold."""
    quits = _fetch_series(conn, 'JTS1000QUR', '2018-01-01')
    fig, ax = _make_fig('JOLTS Quits Rate')
    _style_ax(ax)

    if not quits.empty:
        ax.plot(quits.index, quits, color=COLORS['ocean'], linewidth=2.5)
        _add_last_value(ax, quits, COLORS['ocean'], fmt='.1f')
        _threshold_line(ax, 2.0, '<2.0% pre-recessionary', COLORS['venus'])
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:.1f}%'))
    _add_recessions(ax, '2018-01-01')
    return {'title': 'JOLTS Quits Rate', 'base64': _fig_to_base64(fig)}


def chart_jolts_hires_separations(conn):
    """JOLTS Hires vs Openings rates."""
    hires = _fetch_series(conn, 'JTS1000HIR', '2018-01-01')
    openings = _fetch_series(conn, 'JTS1000JOR', '2018-01-01')
    fig, ax = _make_fig('JOLTS: Openings vs Hires Rate')
    _style_ax(ax)

    if not openings.empty:
        ax.plot(openings.index, openings, color=COLORS['ocean'], linewidth=2,
                label='Openings Rate')
    if not hires.empty:
        ax.plot(hires.index, hires, color=COLORS['dusk'], linewidth=2,
                label='Hires Rate')
    if not openings.empty or not hires.empty:
        ax.legend(loc='upper right', fontsize=7, facecolor=THEME['bg'],
                  edgecolor=THEME['spine'], labelcolor=THEME['fg'])
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:.1f}%'))
    _add_recessions(ax, '2018-01-01')
    return {'title': 'JOLTS Openings vs Hires', 'base64': _fig_to_base64(fig)}


def chart_claims(conn):
    """Initial Claims with 4-week MA."""
    claims = _fetch_series(conn, 'ICSA', '2022-01-01')
    fig, ax = _make_fig('Initial Jobless Claims')
    _style_ax(ax)

    if not claims.empty:
        claims_k = claims / 1000 if claims.max() > 1000 else claims
        ma4 = claims_k.rolling(4, min_periods=2).mean()
        ax.bar(claims_k.index, claims_k, width=5, color=COLORS['ocean'],
               alpha=0.3, label='Weekly')
        ax.plot(ma4.index, ma4, color=COLORS['dusk'], linewidth=2,
                label='4-wk MA')
        _add_last_value(ax, ma4, COLORS['dusk'], fmt=',.0f')
        ax.legend(loc='upper left', fontsize=7, facecolor=THEME['bg'],
                  edgecolor=THEME['spine'], labelcolor=THEME['fg'])
    ax.set_ylabel('Thousands', fontsize=8, color=THEME['muted'])
    _add_recessions(ax)
    return {'title': 'Initial Claims', 'base64': _fig_to_base64(fig)}


# ============================================================
# PILLAR 2: PRICES
# ============================================================

def chart_cpi_headline_core(conn):
    """CPI Headline vs Core YoY."""
    headline = _fetch_series(conn, 'CPIAUCSL', '2018-01-01')
    core = _fetch_series(conn, 'CPILFESL', '2018-01-01')
    fig, ax = _make_fig('CPI: Headline vs Core (YoY %)')
    _style_ax(ax)

    if not headline.empty:
        h_yoy = _yoy_pct(headline).dropna().loc['2019-01-01':]
        ax.plot(h_yoy.index, h_yoy, color=COLORS['ocean'], linewidth=2,
                label='Headline')
    if not core.empty:
        c_yoy = _yoy_pct(core).dropna().loc['2019-01-01':]
        ax.plot(c_yoy.index, c_yoy, color=COLORS['dusk'], linewidth=2,
                label='Core')
        _add_last_value(ax, c_yoy, COLORS['dusk'], fmt='.1f')
    _threshold_line(ax, 2.0, '2% target', COLORS['venus'])
    ax.legend(loc='upper right', fontsize=7, facecolor=THEME['bg'],
              edgecolor=THEME['spine'], labelcolor=THEME['fg'])
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:.1f}%'))
    _add_recessions(ax, '2019-01-01')
    return {'title': 'CPI Headline vs Core', 'base64': _fig_to_base64(fig)}


def chart_cpi_shelter(conn):
    """CPI Shelter YoY with ZORI lead."""
    shelter = _fetch_series(conn, 'CUSR0000SAH1', '2018-01-01')
    fig, ax = _make_fig('CPI Shelter (YoY %)')
    _style_ax(ax)

    if not shelter.empty:
        s_yoy = _yoy_pct(shelter).dropna().loc['2019-01-01':]
        ax.plot(s_yoy.index, s_yoy, color=COLORS['ocean'], linewidth=2.5)
        _add_last_value(ax, s_yoy, COLORS['ocean'], fmt='.1f')
    _threshold_line(ax, 2.0, '2% target', COLORS['venus'])
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:.1f}%'))
    _add_recessions(ax, '2019-01-01')
    return {'title': 'CPI Shelter', 'base64': _fig_to_base64(fig)}


def chart_pce_core(conn):
    """PCE Core YoY (Fed's preferred gauge)."""
    pce = _fetch_series(conn, 'PCEPILFE', '2018-01-01')
    fig, ax = _make_fig('Core PCE (YoY %) - Fed\'s Preferred Gauge')
    _style_ax(ax)

    if not pce.empty:
        yoy = _yoy_pct(pce).dropna().loc['2019-01-01':]
        ax.plot(yoy.index, yoy, color=COLORS['ocean'], linewidth=2.5)
        _add_last_value(ax, yoy, COLORS['ocean'], fmt='.1f')
    _threshold_line(ax, 2.0, '2% target', COLORS['venus'])
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:.1f}%'))
    _add_recessions(ax, '2019-01-01')
    return {'title': 'Core PCE', 'base64': _fig_to_base64(fig)}


def chart_breakevens(conn):
    """5Y and 10Y breakeven inflation."""
    be5 = _fetch_series(conn, 'T5YIE', '2022-01-01')
    be10 = _fetch_series(conn, 'T10YIE', '2022-01-01')
    fig, ax = _make_fig('Breakeven Inflation')
    _style_ax(ax)

    if not be5.empty:
        ax.plot(be5.index, be5, color=COLORS['ocean'], linewidth=2, label='5Y')
        _add_last_value(ax, be5, COLORS['ocean'], fmt='.2f')
    if not be10.empty:
        ax.plot(be10.index, be10, color=COLORS['dusk'], linewidth=2,
                label='10Y', alpha=0.8)
    _threshold_line(ax, 2.0, '2% target', COLORS['venus'])
    ax.legend(loc='upper right', fontsize=7, facecolor=THEME['bg'],
              edgecolor=THEME['spine'], labelcolor=THEME['fg'])
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:.2f}%'))
    return {'title': 'Breakeven Inflation', 'base64': _fig_to_base64(fig)}


# ============================================================
# PILLAR 3: GROWTH
# ============================================================

def chart_gdp_growth(conn):
    """Real GDP YoY growth."""
    gdp = _fetch_series(conn, 'GDPC1', '2015-01-01')
    fig, ax = _make_fig('Real GDP (YoY %)')
    _style_ax(ax)

    if not gdp.empty:
        yoy = _yoy_pct(gdp, periods=4).dropna().loc['2016-01-01':]
        colors = [COLORS['sea'] if v >= 0 else COLORS['port'] for v in yoy]
        ax.bar(yoy.index, yoy, width=80, color=colors, alpha=0.7)
        _add_last_value(ax, yoy, COLORS['ocean'], fmt='.1f')
    _zero_line(ax)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:.1f}%'))
    _add_recessions(ax, '2016-01-01')
    return {'title': 'Real GDP Growth', 'base64': _fig_to_base64(fig)}


def chart_industrial_production(conn):
    """Industrial Production YoY."""
    ip = _fetch_series(conn, 'INDPRO', '2018-01-01')
    fig, ax = _make_fig('Industrial Production (YoY %)')
    _style_ax(ax)

    if not ip.empty:
        yoy = _yoy_pct(ip).dropna().loc['2019-01-01':]
        ax.fill_between(yoy.index, 0, yoy, where=yoy >= 0,
                        color=COLORS['sea'], alpha=THEME['fill_alpha'])
        ax.fill_between(yoy.index, 0, yoy, where=yoy < 0,
                        color=COLORS['port'], alpha=THEME['fill_alpha'])
        ax.plot(yoy.index, yoy, color=COLORS['ocean'], linewidth=2)
        _add_last_value(ax, yoy, COLORS['ocean'], fmt='.1f')
    _zero_line(ax)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:.1f}%'))
    _add_recessions(ax, '2019-01-01')
    return {'title': 'Industrial Production', 'base64': _fig_to_base64(fig)}


# ============================================================
# PILLAR 4: HOUSING
# ============================================================

def chart_housing_starts(conn):
    """Housing starts (SAAR, thousands)."""
    starts = _fetch_series(conn, 'HOUST', '2018-01-01')
    fig, ax = _make_fig('Housing Starts (SAAR, Thousands)')
    _style_ax(ax)

    if not starts.empty:
        ax.plot(starts.index, starts, color=COLORS['ocean'], linewidth=2.5)
        ma3 = starts.rolling(3).mean()
        ax.plot(ma3.index, ma3, color=COLORS['dusk'], linewidth=1.5,
                linestyle='--', alpha=0.7, label='3-mo MA')
        _add_last_value(ax, starts, COLORS['ocean'], fmt=',.0f')
        ax.legend(loc='upper right', fontsize=7, facecolor=THEME['bg'],
                  edgecolor=THEME['spine'], labelcolor=THEME['fg'])
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:,.0f}'))
    _add_recessions(ax, '2018-01-01')
    return {'title': 'Housing Starts', 'base64': _fig_to_base64(fig)}


def chart_mortgage_vs_starts(conn):
    """30Y Mortgage Rate vs Housing Starts."""
    mtg = _fetch_series(conn, 'MORTGAGE30US', '2018-01-01')
    starts = _fetch_series(conn, 'HOUST', '2018-01-01')
    fig, ax = _make_fig('Mortgage Rate vs Housing Starts')
    _style_ax(ax)

    if not mtg.empty:
        ax.plot(mtg.index, mtg, color=COLORS['dusk'], linewidth=2, label='30Y Mortgage (%)')
        _add_last_value(ax, mtg, COLORS['dusk'], fmt='.2f')
    if not starts.empty:
        ax2 = ax.twinx()
        ax2.set_facecolor(THEME['bg'])
        for spine in ax2.spines.values():
            spine.set_color(THEME['spine'])
            spine.set_linewidth(0.5)
        ax2.tick_params(colors=THEME['fg'], which='both', length=0, labelsize=8)
        ax2.plot(starts.index, starts, color=COLORS['ocean'], linewidth=2,
                 label='Starts (K)')
        ax2.yaxis.tick_left()
        ax2.yaxis.set_label_position('left')
        ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:,.0f}'))
        lines1, labels1 = ax.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax.legend(lines1 + lines2, labels1 + labels2, loc='upper left',
                  fontsize=7, facecolor=THEME['bg'],
                  edgecolor=THEME['spine'], labelcolor=THEME['fg'])
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:.1f}%'))
    _add_recessions(ax, '2018-01-01')
    return {'title': 'Mortgage vs Starts', 'base64': _fig_to_base64(fig)}


def chart_case_shiller(conn):
    """Case-Shiller Home Prices YoY."""
    cs = _fetch_series(conn, 'CSUSHPINSA', '2018-01-01')
    fig, ax = _make_fig('Case-Shiller Home Prices (YoY %)')
    _style_ax(ax)

    if not cs.empty:
        yoy = _yoy_pct(cs).dropna().loc['2019-01-01':]
        ax.plot(yoy.index, yoy, color=COLORS['ocean'], linewidth=2.5)
        _add_last_value(ax, yoy, COLORS['ocean'], fmt='.1f')
    _zero_line(ax)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:.1f}%'))
    _add_recessions(ax, '2019-01-01')
    return {'title': 'Case-Shiller YoY', 'base64': _fig_to_base64(fig)}


# ============================================================
# PILLAR 5: CONSUMER
# ============================================================

def chart_retail_sales(conn):
    """Retail Sales Control Group YoY."""
    rs = _fetch_series(conn, 'RSXFS', '2018-01-01')
    fig, ax = _make_fig('Retail Sales Control Group (YoY %)')
    _style_ax(ax)

    if not rs.empty:
        yoy = _yoy_pct(rs).dropna().loc['2019-01-01':]
        ax.plot(yoy.index, yoy, color=COLORS['ocean'], linewidth=2.5)
        _add_last_value(ax, yoy, COLORS['ocean'], fmt='.1f')
    _zero_line(ax)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:.1f}%'))
    _add_recessions(ax, '2019-01-01')
    return {'title': 'Retail Sales', 'base64': _fig_to_base64(fig)}


def chart_saving_rate(conn):
    """Personal Saving Rate."""
    sr = _fetch_series(conn, 'PSAVERT', '2018-01-01')
    fig, ax = _make_fig('Personal Saving Rate (%)')
    _style_ax(ax)

    if not sr.empty:
        ax.fill_between(sr.index, 0, sr, color=COLORS['ocean'],
                        alpha=THEME['fill_alpha'])
        ax.plot(sr.index, sr, color=COLORS['ocean'], linewidth=2)
        _add_last_value(ax, sr, COLORS['ocean'], fmt='.1f')
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:.1f}%'))
    _add_recessions(ax, '2018-01-01')
    return {'title': 'Saving Rate', 'base64': _fig_to_base64(fig)}


def chart_income_spending(conn):
    """Real DPI vs Real PCE YoY."""
    dpi = _fetch_series(conn, 'DSPIC96', '2018-01-01')
    pce = _fetch_series(conn, 'PCEC96', '2018-01-01')
    fig, ax = _make_fig('Real Income vs Real Spending (YoY %)')
    _style_ax(ax)

    if not dpi.empty:
        d_yoy = _yoy_pct(dpi).dropna().loc['2019-01-01':]
        ax.plot(d_yoy.index, d_yoy, color=COLORS['ocean'], linewidth=2,
                label='Real DPI')
    if not pce.empty:
        p_yoy = _yoy_pct(pce).dropna().loc['2019-01-01':]
        ax.plot(p_yoy.index, p_yoy, color=COLORS['dusk'], linewidth=2,
                label='Real PCE')
    _zero_line(ax)
    ax.legend(loc='upper right', fontsize=7, facecolor=THEME['bg'],
              edgecolor=THEME['spine'], labelcolor=THEME['fg'])
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:.1f}%'))
    _add_recessions(ax, '2019-01-01')
    return {'title': 'Income vs Spending', 'base64': _fig_to_base64(fig)}


def chart_consumer_sentiment(conn):
    """UMich Consumer Sentiment."""
    cs = _fetch_series(conn, 'UMCSENT', '2018-01-01')
    fig, ax = _make_fig('UMich Consumer Sentiment')
    _style_ax(ax)

    if not cs.empty:
        ax.plot(cs.index, cs, color=COLORS['ocean'], linewidth=2.5)
        _add_last_value(ax, cs, COLORS['ocean'], fmt='.1f')
    _add_recessions(ax, '2018-01-01')
    return {'title': 'Consumer Sentiment', 'base64': _fig_to_base64(fig)}


def chart_consumer_credit(conn):
    """Consumer Credit YoY growth."""
    cc = _fetch_series(conn, 'TOTALSL', '2018-01-01')
    fig, ax = _make_fig('Consumer Credit (YoY %)')
    _style_ax(ax)

    if not cc.empty:
        yoy = _yoy_pct(cc).dropna().loc['2019-01-01':]
        ax.plot(yoy.index, yoy, color=COLORS['ocean'], linewidth=2.5)
        _add_last_value(ax, yoy, COLORS['ocean'], fmt='.1f')
    _zero_line(ax)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:.1f}%'))
    _add_recessions(ax, '2019-01-01')
    return {'title': 'Consumer Credit', 'base64': _fig_to_base64(fig)}


# ============================================================
# PILLAR 6: BUSINESS
# ============================================================

def chart_ism_pmi(conn):
    """ISM Manufacturing PMI (from TradingView)."""
    ism = _fetch_series(conn, 'TV_USISMMP', '2018-01-01')
    fig, ax = _make_fig('ISM Manufacturing PMI')
    _style_ax(ax)

    if not ism.empty:
        ax.fill_between(ism.index, 50, ism, where=ism >= 50,
                        color=COLORS['sea'], alpha=THEME['fill_alpha'])
        ax.fill_between(ism.index, 50, ism, where=ism < 50,
                        color=COLORS['port'], alpha=THEME['fill_alpha'])
        ax.plot(ism.index, ism, color=COLORS['ocean'], linewidth=2.5)
        _add_last_value(ax, ism, COLORS['ocean'], fmt='.1f')
    _threshold_line(ax, 50, '50 = breakeven', COLORS['fog'])
    _add_recessions(ax, '2018-01-01')
    return {'title': 'ISM Manufacturing', 'base64': _fig_to_base64(fig)}


# ============================================================
# PILLAR 7: TRADE
# ============================================================

def chart_dollar(conn):
    """Trade-Weighted Dollar Index."""
    dxy = _fetch_series(conn, 'DTWEXBGS', '2022-01-01')
    fig, ax = _make_fig('Trade-Weighted Dollar Index')
    _style_ax(ax)

    if not dxy.empty:
        ax.plot(dxy.index, dxy, color=COLORS['ocean'], linewidth=2)
        ma50 = dxy.rolling(50, min_periods=25).mean()
        ax.plot(ma50.index, ma50, color=COLORS['dusk'], linewidth=1,
                linestyle='--', alpha=0.7, label='50d MA')
        _add_last_value(ax, dxy, COLORS['ocean'], fmt='.1f')
        ax.legend(loc='upper left', fontsize=7, facecolor=THEME['bg'],
                  edgecolor=THEME['spine'], labelcolor=THEME['fg'])
    return {'title': 'Dollar Index', 'base64': _fig_to_base64(fig)}


def chart_trade_balance(conn):
    """Trade Balance (Goods & Services)."""
    tb = _fetch_series(conn, 'BOPGSTB', '2018-01-01')
    fig, ax = _make_fig('Trade Balance ($B)')
    _style_ax(ax)

    if not tb.empty:
        tb_b = tb / 1000 if tb.min() < -500000 else tb  # Convert if in millions
        colors = [COLORS['sea'] if v >= 0 else COLORS['port'] for v in tb_b]
        ax.bar(tb_b.index, tb_b, width=25, color=colors, alpha=0.7)
        _add_last_value(ax, tb_b, COLORS['ocean'], fmt=',.1f')
    _zero_line(ax)
    _add_recessions(ax, '2018-01-01')
    return {'title': 'Trade Balance', 'base64': _fig_to_base64(fig)}


# ============================================================
# PILLAR 8: GOVERNMENT / RATES
# ============================================================

def chart_yield_curve(conn):
    """10Y-2Y Treasury Spread."""
    t10 = _fetch_series(conn, 'DGS10', '2022-01-01')
    t2 = _fetch_series(conn, 'DGS2', '2022-01-01')
    fig, ax = _make_fig('Yield Curve (10Y - 2Y Spread)')
    _style_ax(ax)

    if not t10.empty and not t2.empty:
        common = t10.index.intersection(t2.index)
        spread = t10.loc[common] - t2.loc[common]
        ax.fill_between(spread.index, 0, spread, where=spread >= 0,
                        color=COLORS['sea'], alpha=THEME['fill_alpha'])
        ax.fill_between(spread.index, 0, spread, where=spread < 0,
                        color=COLORS['venus'], alpha=THEME['fill_alpha'])
        ax.plot(spread.index, spread, color=COLORS['ocean'], linewidth=2)
        _add_last_value(ax, spread, COLORS['ocean'], fmt='.2f')
    _zero_line(ax)
    ax.set_ylabel('Spread (pp)', fontsize=8, color=THEME['muted'])
    _add_recessions(ax)
    return {'title': 'Yield Curve', 'base64': _fig_to_base64(fig)}


def chart_term_premium(conn):
    """10Y Term Premium (ACM)."""
    tp = _fetch_series(conn, 'THREEFYTP10', '2022-01-01')
    fig, ax = _make_fig('10Y Term Premium (ACM)')
    _style_ax(ax)

    if not tp.empty:
        ax.fill_between(tp.index, 0, tp, where=tp >= 0,
                        color=COLORS['sea'], alpha=THEME['fill_alpha'])
        ax.fill_between(tp.index, 0, tp, where=tp < 0,
                        color=COLORS['venus'], alpha=THEME['fill_alpha'])
        ax.plot(tp.index, tp, color=COLORS['ocean'], linewidth=2)
        _add_last_value(ax, tp, COLORS['ocean'], fmt='.2f')
    _zero_line(ax)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:.2f}%'))
    return {'title': 'Term Premium', 'base64': _fig_to_base64(fig)}


def chart_real_rates(conn):
    """Real rates (10Y TIPS yield)."""
    tips = _fetch_series(conn, 'DFII10', '2022-01-01')
    fig, ax = _make_fig('10Y Real Rate (TIPS Yield)')
    _style_ax(ax)

    if not tips.empty:
        ax.plot(tips.index, tips, color=COLORS['ocean'], linewidth=2.5)
        _add_last_value(ax, tips, COLORS['ocean'], fmt='.2f')
    _zero_line(ax)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:.2f}%'))
    return {'title': 'Real Rates', 'base64': _fig_to_base64(fig)}


# ============================================================
# PILLAR 9: FINANCIAL
# ============================================================

def chart_hy_oas(conn):
    """High Yield OAS spread."""
    hy = _fetch_series(conn, 'BAMLH0A0HYM2', '2022-01-01')
    fig, ax = _make_fig('HY OAS Spread')
    _style_ax(ax)

    if not hy.empty:
        hy_bps = hy * 100 if hy.max() < 20 else hy
        ax.fill_between(hy_bps.index, 0, hy_bps, color=COLORS['ocean'],
                        alpha=THEME['fill_alpha'])
        ax.plot(hy_bps.index, hy_bps, color=COLORS['ocean'], linewidth=2)
        _threshold_line(ax, 300, '300 bps (complacent)', COLORS['venus'])
        _add_last_value(ax, hy_bps, COLORS['ocean'], fmt=',.0f')
    ax.set_ylabel('bps', fontsize=8, color=THEME['muted'])
    _add_recessions(ax)
    return {'title': 'HY OAS', 'base64': _fig_to_base64(fig)}


def chart_credit_labor_gap(conn):
    """Credit-Labor Gap (CLG) index."""
    df = _fetch_index(conn, 'CLG', '2024-01-01')
    fig, ax = _make_fig('Credit-Labor Gap (CLG)')
    _style_ax(ax)

    if not df.empty:
        ax.plot(df.index, df['value'], color=COLORS['ocean'], linewidth=2.5)
        _add_last_value(ax, df['value'], COLORS['ocean'], fmt='.2f')
    _zero_line(ax)
    _threshold_line(ax, -1.0, '<-1.0 mispriced', COLORS['venus'])
    return {'title': 'Credit-Labor Gap', 'base64': _fig_to_base64(fig)}


# ============================================================
# PILLAR 10: PLUMBING
# ============================================================

def chart_fed_balance_sheet(conn):
    """Fed Balance Sheet and RRP."""
    walcl = _fetch_series(conn, 'WALCL', '2022-01-01')
    rrp = _fetch_series(conn, 'RRPONTSYD', '2022-01-01')
    fig, ax = _make_fig('Fed Balance Sheet & RRP')
    _style_ax(ax)

    if not walcl.empty:
        walcl_t = walcl / 1e6
        ax.plot(walcl_t.index, walcl_t, color=COLORS['ocean'], linewidth=2,
                label='WALCL ($T)')
        _add_last_value(ax, walcl_t, COLORS['ocean'], fmt='.2f')

    if not rrp.empty:
        ax2 = ax.twinx()
        ax2.set_facecolor(THEME['bg'])
        for spine in ax2.spines.values():
            spine.set_color(THEME['spine'])
            spine.set_linewidth(0.5)
        ax2.tick_params(colors=THEME['fg'], which='both', length=0, labelsize=8)
        rrp_b = rrp / 1e3 if rrp.max() > 1000 else rrp
        ax2.plot(rrp_b.index, rrp_b, color=COLORS['dusk'], linewidth=1.5,
                 label='RRP ($B)', alpha=0.8)
        ax2.set_ylabel('RRP ($B)', fontsize=8, color=COLORS['dusk'])
        ax2.tick_params(axis='y', labelcolor=COLORS['dusk'])
        ax2.yaxis.tick_left()
        ax2.yaxis.set_label_position('left')
        lines1, labels1 = ax.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax.legend(lines1 + lines2, labels1 + labels2, loc='upper right',
                  fontsize=7, facecolor=THEME['bg'],
                  edgecolor=THEME['spine'], labelcolor=THEME['fg'])

    _add_recessions(ax)
    return {'title': 'Fed Balance Sheet & RRP', 'base64': _fig_to_base64(fig)}


def chart_sofr_iorb(conn):
    """SOFR vs IORB spread."""
    sofr = _fetch_series(conn, 'SOFR', '2023-01-01')
    iorb = _fetch_series(conn, 'IORB', '2023-01-01')
    fig, ax = _make_fig('SOFR vs IORB')
    _style_ax(ax)

    if not sofr.empty and not iorb.empty:
        common = sofr.index.intersection(iorb.index)
        if len(common) > 0:
            spread_bps = (sofr.loc[common] - iorb.loc[common]) * 100
            ax.plot(spread_bps.index, spread_bps, color=COLORS['ocean'], linewidth=2)
            _add_last_value(ax, spread_bps, COLORS['ocean'], fmt='.1f')
            _zero_line(ax)
            _threshold_line(ax, 8, '+8 bps (stress)', COLORS['venus'])
    ax.set_ylabel('bps', fontsize=8, color=THEME['muted'])
    return {'title': 'SOFR-IORB Spread', 'base64': _fig_to_base64(fig)}


# ============================================================
# PILLAR 11: STRUCTURE
# ============================================================

def chart_breadth(conn):
    """Market breadth: % stocks above 50d MA."""
    pct50 = _fetch_series(conn, 'SPX_PCT_ABOVE_50D', '2023-01-01')
    fig, ax = _make_fig('S&P 500: % Stocks Above 50d MA')
    _style_ax(ax)

    if not pct50.empty:
        ax.fill_between(pct50.index, 0, pct50, color=COLORS['ocean'],
                        alpha=THEME['fill_alpha'])
        ax.plot(pct50.index, pct50, color=COLORS['ocean'], linewidth=2)
        _add_last_value(ax, pct50, COLORS['ocean'], fmt='.0f')
        _threshold_line(ax, 35, '35% (washed)', COLORS['venus'])
        _threshold_line(ax, 85, '85% (crowded)', COLORS['dusk'])
    ax.set_ylim(0, 100)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:.0f}%'))
    return {'title': 'Breadth: >50d MA', 'base64': _fig_to_base64(fig)}


# ============================================================
# PILLAR 12: SENTIMENT
# ============================================================

def chart_vix(conn):
    """VIX with thresholds."""
    vix = _fetch_series(conn, 'VIXCLS', '2022-01-01')
    fig, ax = _make_fig('VIX')
    _style_ax(ax)

    if not vix.empty:
        ax.fill_between(vix.index, 0, vix, color=COLORS['ocean'],
                        alpha=THEME['fill_alpha'])
        ax.plot(vix.index, vix, color=COLORS['ocean'], linewidth=2)
        _threshold_line(ax, 20, '20', COLORS['fog'])
        _threshold_line(ax, 30, '30 (fear)', COLORS['venus'])
        _add_last_value(ax, vix, COLORS['ocean'], fmt='.1f')
    _add_recessions(ax)
    return {'title': 'VIX', 'base64': _fig_to_base64(fig)}


def chart_aaii(conn):
    """AAII Bull-Bear Spread."""
    bull = _fetch_series(conn, 'AAII_Bullish', '2022-01-01')
    bear = _fetch_series(conn, 'AAII_Bearish', '2022-01-01')
    fig, ax = _make_fig('AAII Bull-Bear Spread')
    _style_ax(ax)

    if not bull.empty and not bear.empty:
        common = bull.index.intersection(bear.index)
        spread = bull.loc[common] - bear.loc[common]
        ax.fill_between(spread.index, 0, spread, where=spread >= 0,
                        color=COLORS['sea'], alpha=THEME['fill_alpha'])
        ax.fill_between(spread.index, 0, spread, where=spread < 0,
                        color=COLORS['port'], alpha=THEME['fill_alpha'])
        ax.plot(spread.index, spread, color=COLORS['ocean'], linewidth=2)
        _add_last_value(ax, spread, COLORS['ocean'], fmt='.1f')
        _threshold_line(ax, 30, '+30 (euphoria)', COLORS['venus'])
        _threshold_line(ax, -20, '-20 (capitulation)', COLORS['sea'])
    _zero_line(ax)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:.0f}%'))
    return {'title': 'AAII Bull-Bear', 'base64': _fig_to_base64(fig)}


# ============================================================
# CHART REGISTRY
# ============================================================

CHART_REGISTRY = {
    # Always On
    "chart_mri": chart_mri,
    "chart_spx": chart_spx,
    # Pillar 1: Labor
    "chart_unemployment_rate": chart_unemployment_rate,
    "chart_nfp_momentum": chart_nfp_momentum,
    "chart_wages": chart_wages,
    "chart_lfpr": chart_lfpr,
    "chart_jolts_quits": chart_jolts_quits,
    "chart_jolts_hires_separations": chart_jolts_hires_separations,
    "chart_claims": chart_claims,
    # Pillar 2: Prices
    "chart_cpi_headline_core": chart_cpi_headline_core,
    "chart_cpi_shelter": chart_cpi_shelter,
    "chart_pce_core": chart_pce_core,
    "chart_breakevens": chart_breakevens,
    # Pillar 3: Growth
    "chart_gdp_growth": chart_gdp_growth,
    "chart_industrial_production": chart_industrial_production,
    # Pillar 4: Housing
    "chart_housing_starts": chart_housing_starts,
    "chart_mortgage_vs_starts": chart_mortgage_vs_starts,
    "chart_case_shiller": chart_case_shiller,
    # Pillar 5: Consumer
    "chart_retail_sales": chart_retail_sales,
    "chart_saving_rate": chart_saving_rate,
    "chart_income_spending": chart_income_spending,
    "chart_consumer_sentiment": chart_consumer_sentiment,
    "chart_consumer_credit": chart_consumer_credit,
    # Pillar 6: Business
    "chart_ism_pmi": chart_ism_pmi,
    # Pillar 7: Trade
    "chart_dollar": chart_dollar,
    "chart_trade_balance": chart_trade_balance,
    # Pillar 8: Government / Rates
    "chart_yield_curve": chart_yield_curve,
    "chart_term_premium": chart_term_premium,
    "chart_real_rates": chart_real_rates,
    # Pillar 9: Financial
    "chart_hy_oas": chart_hy_oas,
    "chart_credit_labor_gap": chart_credit_labor_gap,
    # Pillar 10: Plumbing
    "chart_fed_balance_sheet": chart_fed_balance_sheet,
    "chart_sofr_iorb": chart_sofr_iorb,
    # Pillar 11: Structure
    "chart_breadth": chart_breadth,
    # Pillar 12: Sentiment
    "chart_vix": chart_vix,
    "chart_aaii": chart_aaii,
}


def generate_selected_charts(conn, chart_specs):
    """
    Generate charts from a list of specs (from release_chart_selector).

    Args:
        conn: sqlite3 connection
        chart_specs: list of {"func_name": str, "context": str, ...}

    Returns:
        list of {"title": str, "base64": str, "context": str}
    """
    results = []
    for spec in chart_specs:
        func_name = spec["func_name"]
        func = CHART_REGISTRY.get(func_name)
        if not func:
            print(f"  WARNING: Unknown chart function: {func_name}")
            continue
        try:
            result = func(conn)
            result["context"] = spec.get("context", "")
            results.append(result)
        except Exception as e:
            print(f"  WARNING: Chart {func_name} failed: {e}")
    return results


# Legacy compatibility
def generate_dashboard_charts(conn, dashboard='morning_brief'):
    """Legacy entry point. Generates default charts."""
    default_funcs = [
        chart_mri, chart_spx, chart_yield_curve, chart_hy_oas,
        chart_vix, chart_fed_balance_sheet, chart_dollar, chart_claims,
    ]
    results = []
    for func in default_funcs:
        try:
            results.append(func(conn))
        except Exception as e:
            print(f"  WARNING: Chart {func.__name__} failed: {e}")
    return results


# ============================================================
# CLI
# ============================================================

if __name__ == '__main__':
    DB_PATH = Path("/Users/bob/LHM/Data/databases/Lighthouse_Master.db")
    conn = sqlite3.connect(DB_PATH)
    charts = generate_dashboard_charts(conn)
    print(f"Generated {len(charts)} charts:")
    for c in charts:
        size = len(c.get('base64', '')) * 3 / 4 / 1024
        status = f"{size:.0f} KB" if c.get('base64') else "FAILED"
        print(f"  {c['title']}: {status}")
    conn.close()
