#!/usr/bin/env python3
"""
LIGHTHOUSE MACRO - DASHBOARD CHART GENERATOR
=============================================
Generates charts from the master database as base64-encoded PNGs.
Used by the morning brief HTML dashboard. Designed to be extended
with per-pillar dashboards.

All charts read from the observations/lighthouse_indices tables.
No external API calls.
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
import pandas as pd
import numpy as np

# ============================================================
# BRAND COLORS & THEME
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
}

DARK_THEME = {
    'bg': '#0A1628',
    'card_bg': '#0f2140',
    'fg': '#e6edf3',
    'muted': '#8b949e',
    'spine': '#1e3350',
    'grid': '#1e3350',
}

# MRI regime bands
MRI_REGIMES = [
    (-999, -0.20, COLORS['sea'], 'Early Expansion', 0.08),
    (-0.20, 0.10, COLORS['ocean'], 'Mid-Cycle', 0.05),
    (0.10, 0.25, COLORS['dusk'], 'Late Cycle', 0.08),
    (0.25, 0.50, COLORS['venus'], 'Pre-Recession', 0.08),
    (0.50, 999, COLORS['port'], 'Recession', 0.10),
]

# NBER recession dates (for shading)
RECESSIONS = [
    ('2001-03-01', '2001-11-01'),
    ('2007-12-01', '2009-06-01'),
    ('2020-02-01', '2020-04-01'),
]


# ============================================================
# HELPERS
# ============================================================

def _fetch_series(conn: sqlite3.Connection, series_id: str,
                  start_date: str = '2022-01-01') -> pd.Series:
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


def _fetch_index(conn: sqlite3.Connection, index_id: str,
                 start_date: str = '2022-01-01') -> pd.DataFrame:
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


def _style_ax(ax):
    """Apply dark theme styling to axes."""
    ax.set_facecolor(DARK_THEME['bg'])
    for spine in ax.spines.values():
        spine.set_color(DARK_THEME['spine'])
        spine.set_linewidth(0.5)
    ax.tick_params(colors=DARK_THEME['muted'], which='both',
                   length=0, labelsize=8)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %y'))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    ax.grid(False)


def _add_last_value(ax, series, color, fmt='.2f', side='right'):
    """Add a last-value label on the axis edge."""
    if series.empty:
        return
    last_val = series.iloc[-1]
    last_date = series.index[-1]
    txt = f'{last_val:{fmt}}'
    y_pos = last_val
    ax.annotate(txt, xy=(1.01, y_pos), xycoords=('axes fraction', 'data'),
                fontsize=8, fontweight='bold', color='white',
                bbox=dict(boxstyle='round,pad=0.3', facecolor=color,
                          edgecolor='none', alpha=0.9),
                va='center', ha='left')


def _add_recessions(ax, start_date='2022-01-01'):
    """Add NBER recession shading."""
    start = pd.Timestamp(start_date)
    for r_start, r_end in RECESSIONS:
        rs = pd.Timestamp(r_start)
        re = pd.Timestamp(r_end)
        if re >= start:
            ax.axvspan(max(rs, start), re, color='white', alpha=0.06, zorder=0)


def _fig_to_base64(fig) -> str:
    """Convert figure to base64 PNG string."""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=150, bbox_inches='tight',
                pad_inches=0.08, facecolor=DARK_THEME['bg'],
                edgecolor='none')
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.getvalue()).decode('utf-8')


def _make_fig(title: str):
    """Create a branded figure."""
    fig, ax = plt.subplots(figsize=(10, 4))
    fig.patch.set_facecolor(DARK_THEME['bg'])
    ax.set_title(title, fontsize=11, fontweight='bold',
                 color=DARK_THEME['fg'], pad=10, loc='left')
    return fig, ax


# ============================================================
# CHART FUNCTIONS
# ============================================================

def chart_mri(conn: sqlite3.Connection) -> dict:
    """MRI time series with regime bands."""
    df = _fetch_index(conn, 'MRI', '2024-01-01')
    fig, ax = _make_fig('Macro Risk Index (MRI)')
    _style_ax(ax)

    if not df.empty:
        # Regime bands
        for lo, hi, color, label, alpha in MRI_REGIMES:
            ax.axhspan(max(lo, -1.5), min(hi, 1.5), color=color,
                       alpha=alpha, zorder=0)

        ax.plot(df.index, df['value'], color=COLORS['ocean'],
                linewidth=2.5, zorder=5)
        ax.axhline(y=0, color=COLORS['doldrums'], linewidth=0.5,
                   linestyle='--', alpha=0.5)
        _add_last_value(ax, df['value'], COLORS['ocean'], fmt='.3f')

        # Current regime label
        if not df.empty:
            last_status = df['status'].iloc[-1] or ''
            ax.text(0.99, 0.95, last_status, transform=ax.transAxes,
                    fontsize=9, color=COLORS['ocean'], fontweight='bold',
                    ha='right', va='top',
                    bbox=dict(boxstyle='round,pad=0.3',
                              facecolor=DARK_THEME['card_bg'],
                              edgecolor=COLORS['ocean'], alpha=0.9))

    ax.set_ylim(-0.8, 0.8)
    _add_recessions(ax, '2024-01-01')
    return {'title': 'Macro Risk Index', 'base64': _fig_to_base64(fig)}


def chart_spx(conn: sqlite3.Connection) -> dict:
    """S&P 500 price with 200-day and 50-day moving averages."""
    spx = _fetch_series(conn, 'SPX_Close', '2023-01-01')
    fig, ax = _make_fig('S&P 500')
    _style_ax(ax)

    if not spx.empty:
        ma_200 = spx.rolling(200, min_periods=100).mean()
        ma_50 = spx.rolling(50, min_periods=25).mean()

        ax.plot(spx.index, spx, color=COLORS['ocean'], linewidth=2,
                label='S&P 500', zorder=5)
        ax.plot(ma_200.index, ma_200, color=COLORS['dusk'], linewidth=1.2,
                label='200d MA', linestyle='--', alpha=0.8)
        ax.plot(ma_50.index, ma_50, color=COLORS['sky'], linewidth=1,
                label='50d MA', linestyle=':', alpha=0.7)
        _add_last_value(ax, spx, COLORS['ocean'], fmt=',.0f')

        ax.legend(loc='upper left', fontsize=7, facecolor=DARK_THEME['bg'],
                  edgecolor=DARK_THEME['spine'], labelcolor=DARK_THEME['fg'])

    _add_recessions(ax, '2023-01-01')
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(
        lambda x, _: f'{x:,.0f}'))
    return {'title': 'S&P 500', 'base64': _fig_to_base64(fig)}


def chart_yield_curve(conn: sqlite3.Connection) -> dict:
    """10Y-2Y Treasury spread."""
    dgs10 = _fetch_series(conn, 'DGS10', '2022-01-01')
    dgs2 = _fetch_series(conn, 'DGS2', '2022-01-01')
    fig, ax = _make_fig('Yield Curve (10Y - 2Y)')
    _style_ax(ax)

    if not dgs10.empty and not dgs2.empty:
        # Align dates
        common = dgs10.index.intersection(dgs2.index)
        spread = dgs10.loc[common] - dgs2.loc[common]

        ax.fill_between(spread.index, 0, spread,
                        where=spread >= 0, color=COLORS['sea'], alpha=0.3)
        ax.fill_between(spread.index, 0, spread,
                        where=spread < 0, color=COLORS['venus'], alpha=0.3)
        ax.plot(spread.index, spread, color=COLORS['ocean'], linewidth=2)
        ax.axhline(y=0, color=COLORS['doldrums'], linewidth=0.8,
                   linestyle='--')
        _add_last_value(ax, spread, COLORS['ocean'], fmt='.2f')

    ax.set_ylabel('Spread (pp)', fontsize=8, color=DARK_THEME['muted'])
    _add_recessions(ax)
    return {'title': 'Yield Curve', 'base64': _fig_to_base64(fig)}


def chart_hy_oas(conn: sqlite3.Connection) -> dict:
    """High Yield OAS spread."""
    hy = _fetch_series(conn, 'BAMLH0A0HYM2', '2022-01-01')
    fig, ax = _make_fig('HY OAS Spread')
    _style_ax(ax)

    if not hy.empty:
        # Convert to basis points if in percentage
        if hy.max() < 20:
            hy = hy * 100

        ax.fill_between(hy.index, 0, hy, color=COLORS['ocean'], alpha=0.2)
        ax.plot(hy.index, hy, color=COLORS['ocean'], linewidth=2)
        ax.axhline(y=300, color=COLORS['venus'], linewidth=0.8,
                   linestyle='--', alpha=0.7)
        ax.text(hy.index[0], 310, '300 bps (complacent)',
                fontsize=7, color=COLORS['venus'], alpha=0.7)
        _add_last_value(ax, hy, COLORS['ocean'], fmt=',.0f')

    ax.set_ylabel('bps', fontsize=8, color=DARK_THEME['muted'])
    _add_recessions(ax)
    return {'title': 'HY OAS', 'base64': _fig_to_base64(fig)}


def chart_vix(conn: sqlite3.Connection) -> dict:
    """VIX index."""
    vix = _fetch_series(conn, 'VIXCLS', '2022-01-01')
    fig, ax = _make_fig('VIX')
    _style_ax(ax)

    if not vix.empty:
        ax.fill_between(vix.index, 0, vix, color=COLORS['ocean'], alpha=0.15)
        ax.plot(vix.index, vix, color=COLORS['ocean'], linewidth=2)
        ax.axhline(y=20, color=COLORS['doldrums'], linewidth=0.5,
                   linestyle='--', alpha=0.5)
        ax.axhline(y=30, color=COLORS['venus'], linewidth=0.8,
                   linestyle='--', alpha=0.7)
        _add_last_value(ax, vix, COLORS['ocean'], fmt='.1f')

    _add_recessions(ax)
    return {'title': 'VIX', 'base64': _fig_to_base64(fig)}


def chart_fed_balance_sheet(conn: sqlite3.Connection) -> dict:
    """Fed balance sheet (WALCL) and RRP."""
    walcl = _fetch_series(conn, 'WALCL', '2022-01-01')
    rrp = _fetch_series(conn, 'RRPONTSYD', '2022-01-01')
    fig, ax = _make_fig('Fed Balance Sheet & RRP')
    _style_ax(ax)

    if not walcl.empty:
        # WALCL is in millions, convert to trillions
        walcl_t = walcl / 1e6
        ax.plot(walcl_t.index, walcl_t, color=COLORS['ocean'], linewidth=2,
                label='WALCL ($T)')
        _add_last_value(ax, walcl_t, COLORS['ocean'], fmt='.2f')

    if not rrp.empty:
        ax2 = ax.twinx()
        _style_ax(ax2)
        # RRP is in billions
        rrp_b = rrp / 1e3 if rrp.max() > 1000 else rrp
        ax2.plot(rrp_b.index, rrp_b, color=COLORS['dusk'], linewidth=1.5,
                 label='RRP ($B)', alpha=0.8)
        ax2.set_ylabel('RRP ($B)', fontsize=8, color=COLORS['dusk'])
        ax2.tick_params(axis='y', labelcolor=COLORS['dusk'])
        _add_last_value(ax2, rrp_b, COLORS['dusk'], fmt=',.0f')

        # Combined legend
        lines1, labels1 = ax.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax.legend(lines1 + lines2, labels1 + labels2, loc='upper right',
                  fontsize=7, facecolor=DARK_THEME['bg'],
                  edgecolor=DARK_THEME['spine'], labelcolor=DARK_THEME['fg'])

    _add_recessions(ax)
    return {'title': 'Fed Balance Sheet & RRP', 'base64': _fig_to_base64(fig)}


def chart_dollar(conn: sqlite3.Connection) -> dict:
    """Dollar index (Trade Weighted)."""
    dxy = _fetch_series(conn, 'DTWEXBGS', '2022-01-01')
    fig, ax = _make_fig('Trade-Weighted Dollar Index')
    _style_ax(ax)

    if not dxy.empty:
        ax.plot(dxy.index, dxy, color=COLORS['ocean'], linewidth=2)
        ma_50 = dxy.rolling(50, min_periods=25).mean()
        ax.plot(ma_50.index, ma_50, color=COLORS['dusk'], linewidth=1,
                linestyle='--', alpha=0.7, label='50d MA')
        _add_last_value(ax, dxy, COLORS['ocean'], fmt='.1f')
        ax.legend(loc='upper left', fontsize=7, facecolor=DARK_THEME['bg'],
                  edgecolor=DARK_THEME['spine'], labelcolor=DARK_THEME['fg'])

    _add_recessions(ax)
    return {'title': 'Dollar Index', 'base64': _fig_to_base64(fig)}


def chart_claims(conn: sqlite3.Connection) -> dict:
    """Initial claims with 4-week MA."""
    claims = _fetch_series(conn, 'ICSA', '2022-01-01')
    fig, ax = _make_fig('Initial Jobless Claims')
    _style_ax(ax)

    if not claims.empty:
        # Claims in thousands
        claims_k = claims / 1000 if claims.max() > 1000 else claims
        ma_4w = claims_k.rolling(4, min_periods=2).mean()

        ax.bar(claims_k.index, claims_k, width=5, color=COLORS['ocean'],
               alpha=0.3, label='Weekly')
        ax.plot(ma_4w.index, ma_4w, color=COLORS['dusk'], linewidth=2,
                label='4-wk MA')
        _add_last_value(ax, ma_4w, COLORS['dusk'], fmt=',.0f')

        ax.legend(loc='upper left', fontsize=7, facecolor=DARK_THEME['bg'],
                  edgecolor=DARK_THEME['spine'], labelcolor=DARK_THEME['fg'])

    ax.set_ylabel('Thousands', fontsize=8, color=DARK_THEME['muted'])
    _add_recessions(ax)
    return {'title': 'Initial Claims', 'base64': _fig_to_base64(fig)}


# ============================================================
# DASHBOARD REGISTRY
# ============================================================

DASHBOARD_CHARTS = {
    'morning_brief': [
        chart_mri,
        chart_spx,
        chart_yield_curve,
        chart_hy_oas,
        chart_vix,
        chart_fed_balance_sheet,
        chart_dollar,
        chart_claims,
    ],
    # Future pillar dashboards:
    # 'labor': [chart_unemployment, chart_jolts_quits, ...],
    # 'prices': [chart_cpi_headline, chart_pce_core, ...],
    # 'growth': [chart_ip, chart_gdp, ...],
    # 'housing': [chart_starts, chart_case_shiller, ...],
    # 'consumer': [chart_retail_sales, chart_saving_rate, ...],
    # 'plumbing': [chart_reserves, chart_rrp, chart_sofr, ...],
}


def generate_dashboard_charts(conn: sqlite3.Connection,
                               dashboard: str = 'morning_brief') -> list:
    """
    Generate all charts for a dashboard.

    Returns list of dicts: [{'title': str, 'base64': str}, ...]
    """
    chart_funcs = DASHBOARD_CHARTS.get(dashboard, [])
    results = []
    for func in chart_funcs:
        try:
            result = func(conn)
            results.append(result)
        except Exception as e:
            print(f"  WARNING: Chart {func.__name__} failed: {e}")
            results.append({
                'title': func.__name__.replace('chart_', '').replace('_', ' ').title(),
                'base64': '',
                'error': str(e),
            })
    return results


# ============================================================
# CLI (for testing)
# ============================================================

if __name__ == '__main__':
    from pathlib import Path

    DB_PATH = Path("/Users/bob/LHM/Data/databases/Lighthouse_Master.db")
    conn = sqlite3.connect(DB_PATH)

    charts = generate_dashboard_charts(conn)
    print(f"Generated {len(charts)} charts:")
    for c in charts:
        size = len(c.get('base64', '')) * 3 / 4 / 1024  # approximate KB
        status = f"{size:.0f} KB" if c.get('base64') else "FAILED"
        print(f"  {c['title']}: {status}")

    conn.close()
