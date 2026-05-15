#!/usr/bin/env python3
"""
LIGHTHOUSE MACRO — DAILY BRIEFING
==================================
Generates the v3 daily briefing as a self-contained HTML document with 10
brand-compliant inline charts. Each chart is rendered twice: in the canonical
white theme AND in the dark theme (Deep #123456 bg). A toggle at the top of
the page swaps both the page palette and the chart images.

Reads:
    /Users/bob/LHM/Data/databases/Lighthouse_Master.db
    Live market data via yfinance

Writes:
    /Users/bob/LHM/Outputs/daily_briefing_latest.html
    /Users/bob/LHM/Outputs/daily_briefing_YYYY-MM-DD.html

Schedule:
    ~/Library/LaunchAgents/com.lighthousemacro.daily-briefing.plist
    Weekday mornings at 7:42am ET (post-pipeline).
"""

from __future__ import annotations

import argparse
import base64
import os
import sqlite3
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

# Canonical brand helpers
sys.path.insert(0, "/Users/bob/LHM/Scripts/chart_generation")
from lhm_chart_template import (  # noqa: E402
    COLORS,
    LHM_PALETTE,
    set_theme,
    new_fig,
    style_single_ax,
    style_dual_ax,
    add_last_value_label,
    add_recessions,
    set_xlim_to_data,
    legend_style,
    align_yaxis_zero,
    align_yaxis_midpoint,
    align_yaxis_smart,
    brand_fig,
    save_fig_buffer,
)

DB_PATH = Path("/Users/bob/LHM/Data/databases/Lighthouse_Master.db")
OUTPUT_DIR = Path("/Users/bob/LHM/Outputs")
LATEST_PATH = OUTPUT_DIR / "daily_briefing_latest.html"

# Web palette (used for the HTML scaffold)
OCEAN     = COLORS["ocean"]
DUSK      = COLORS["dusk"]
SKY       = COLORS["sky"]
BRIGHT    = COLORS["bright"]
DEEP      = COLORS["deep"]
SEA       = COLORS["sea"]
VENUS     = COLORS["venus"]
DOLDRUMS  = COLORS["doldrums"]
STARBOARD = COLORS["starboard"]
PORT      = COLORS["port"]
FOG       = COLORS["fog"]
OFFWHITE  = COLORS["offwhite"]
GLACIER   = COLORS["glacier"]
INK       = "#1a1a1a"

# Inline-link map. Anchor phrase → canonical source URL. First-occurrence only.
LINK_MAP: dict[str, str] = {
    "10-year Treasury":      "https://fred.stlouisfed.org/series/DGS10",
    "10-year":               "https://fred.stlouisfed.org/series/DGS10",
    "2-year":                "https://fred.stlouisfed.org/series/DGS2",
    "VIX":                   "https://www.cboe.com/tradable-products/vix/",
    "HY OAS":                "https://fred.stlouisfed.org/series/BAMLH0A0HYM2",
    "IG OAS":                "https://fred.stlouisfed.org/series/BAMLC0A0CM",
    "AAII bull-bear":        "https://www.aaii.com/sentimentsurvey",
    "AAII":                  "https://www.aaii.com/sentimentsurvey",
    "FOMC":                  "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm",
    "Federal Reserve":       "https://www.federalreserve.gov/",
    "JOLTS":                 "https://www.bls.gov/jlt/",
    "CPI":                   "https://www.bls.gov/cpi/",
    "PPI":                   "https://www.bls.gov/ppi/",
    "Retail Sales":          "https://www.census.gov/retail/marts/www/marts_current.pdf",
    "GDP":                   "https://www.bea.gov/data/gdp/gross-domestic-product",
    "WEI":                   "https://www.newyorkfed.org/research/policy/weekly-economic-index",
    "Atlanta Fed GDPNow":    "https://www.atlantafed.org/cqer/research/gdpnow",
    "RRP":                   "https://www.newyorkfed.org/markets/desk-operations/reverse-repo",
    "TGA":                   "https://fiscaldata.treasury.gov/datasets/daily-treasury-statement/operating-cash-balance",
    "SOFR":                  "https://www.newyorkfed.org/markets/reference-rates/sofr",
    "EFFR":                  "https://www.newyorkfed.org/markets/reference-rates/effr",
    "S&P 500":               "https://finance.yahoo.com/quote/%5EGSPC",
    "SPY":                   "https://finance.yahoo.com/quote/SPY",
    "QQQ":                   "https://finance.yahoo.com/quote/QQQ",
    "TLT":                   "https://finance.yahoo.com/quote/TLT",
    "HYG":                   "https://finance.yahoo.com/quote/HYG",
    "GLD":                   "https://finance.yahoo.com/quote/GLD",
    "DXY":                   "https://finance.yahoo.com/quote/DX-Y.NYB",
    "BTC":                   "https://finance.yahoo.com/quote/BTC-USD",
    "ETH":                   "https://finance.yahoo.com/quote/ETH-USD",
    "QAI":                   "https://finance.yahoo.com/quote/QAI",
    "UMich":                 "https://data.sca.isr.umich.edu/",
}


def link_phrase(text: str) -> str:
    if not text:
        return text
    seen: set[str] = set()
    for phrase in sorted(LINK_MAP.keys(), key=len, reverse=True):
        if phrase in seen:
            continue
        idx = text.find(phrase)
        if idx == -1:
            continue
        url = LINK_MAP[phrase]
        text = text[:idx] + f'<a href="{url}" target="_blank">{phrase}</a>' + text[idx + len(phrase):]
        seen.add(phrase)
    return text


def fig_b64(fig) -> str:
    return base64.b64encode(save_fig_buffer(fig)).decode("ascii")


# ============================================================================
# CHARTS — all use canonical lhm_chart_template helpers
# ============================================================================

def chart_mri(conn) -> str:
    df = pd.read_sql(
        "SELECT date, value FROM lighthouse_indices "
        "WHERE index_id='MRI' AND date >= date('now','-25 year') ORDER BY date",
        conn, parse_dates=["date"],
    ).set_index("date").dropna()
    if df.empty:
        return ""
    fig, ax = new_fig(figsize=(13, 5.4))
    color = COLORS["bright"] if matplotlib.rcParams.get("__lhm_dark__") else COLORS["ocean"]
    # Cycle-phase shading (light bands)
    ax.axhspan(-3,    -0.20, color=COLORS["sea"],   alpha=0.08, zorder=0)
    ax.axhspan(-0.20,  0.10, color=COLORS["fog"],   alpha=0.20, zorder=0)
    ax.axhspan( 0.10,  0.25, color=COLORS["dusk"],  alpha=0.10, zorder=0)
    ax.axhspan( 0.25,  0.50, color=COLORS["dusk"],  alpha=0.18, zorder=0)
    ax.axhspan( 0.50,  3,    color=COLORS["port"],  alpha=0.18, zorder=0)
    ax.plot(df.index, df["value"], color=color, linewidth=2.4)
    ax.axhline(0, color=COLORS["fog"], linestyle="--", linewidth=0.7, zorder=0)
    style_single_ax(ax, fmt="{:+.2f}")
    add_last_value_label(ax, df["value"], color, fmt="{:+.2f}", side="right")
    set_xlim_to_data(ax, df.index)
    add_recessions(ax, start_date=df.index[0])
    brand_fig(fig,
              title="Macro Risk Index",
              subtitle="25y composite with cycle-phase shading and NBER recessions",
              source="Lighthouse Macro composites",
              data_date=df.index[-1])
    return fig_b64(fig)


def chart_pillar_heatmap(conn) -> str:
    """A horizontal mini-bar heatmap, in canonical style."""
    pillar_codes = {
        1: "LFI", 2: "PCI", 3: "GCI", 4: "HCI", 5: "CCI", 6: "BCI",
        7: "TCI", 8: "FPI", 9: "FCI", 10: "LCI", 11: "MSI", 12: "SPI",
    }
    pillar_names = {
        1: "Labor", 2: "Prices", 3: "Growth", 4: "Housing",
        5: "Consumer", 6: "Business", 7: "Trade", 8: "Govt",
        9: "Financial", 10: "Plumbing", 11: "Structure", 12: "Sentiment",
    }
    values = []
    labels = []
    for p in range(1, 13):
        r = conn.execute(
            "SELECT value FROM lighthouse_indices WHERE index_id=? "
            "ORDER BY date DESC LIMIT 1", (pillar_codes[p],)
        ).fetchone()
        v = r[0] if r else 0.0
        values.append(v if v is not None else 0.0)
        labels.append(f"{p}. {pillar_names[p]}")

    fig, ax = new_fig(figsize=(13, 5.4))

    def color_for(z):
        if z is None:
            return COLORS["doldrums"]
        if z <= -1.5: return COLORS["port"]
        if z <= -0.5: return COLORS["dusk"]
        if z <= 0.5:  return COLORS["doldrums"]
        if z <= 1.5:  return COLORS["sea"]
        return COLORS["starboard"]

    colors = [color_for(v) for v in values]
    y = list(range(len(values)))
    ax.barh(y, values, color=colors, edgecolor="none", height=0.7)
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=10, color=COLORS["doldrums"])
    ax.invert_yaxis()
    ax.axvline(0, color=COLORS["fog"], linewidth=0.6, linestyle="--")
    for i, v in enumerate(values):
        ax.text(v + (0.04 if v >= 0 else -0.04), i, f"{v:+.2f}",
                ha="left" if v >= 0 else "right", va="center",
                fontsize=10, color=COLORS["doldrums"], fontweight="bold")
    style_single_ax(ax, fmt="{:+.1f}")
    ax.tick_params(axis="y", which="both", left=False, right=False)
    pad = max(abs(min(values)), abs(max(values))) * 1.25 or 1.0
    ax.set_xlim(-pad, pad)
    brand_fig(fig,
              title="The Diagnostic Dozen",
              subtitle="Current pillar-composite z-score, ordered 1-12",
              source="Lighthouse Macro composites")
    return fig_b64(fig)


def _composite_series(conn, code: str, years: int = 25) -> pd.Series:
    """Default to 25y of history for pillar context. Override years= per chart."""
    df = pd.read_sql(
        f"SELECT date, value FROM lighthouse_indices "
        f"WHERE index_id=? AND date >= date('now','-{years} year') ORDER BY date",
        conn, parse_dates=["date"], params=(code,),
    ).set_index("date").dropna()
    return df["value"]


def chart_labor_stack(conn) -> str:
    fig, ax = new_fig(figsize=(13, 5.4))
    palette = {
        "LFI": (COLORS["ocean"], "Labor Fragility (LFI)"),
        "LPI": (COLORS["dusk"],  "Labor Pressure (LPI)"),
        "LDI": (COLORS["sea"],   "Labor Dynamism (LDI)"),
    }
    indices_used = []
    earliest = None
    for code, (color, label) in palette.items():
        s = _composite_series(conn, code, years=25)
        if s.empty:
            continue
        ax.plot(s.index, s.values, color=color, linewidth=1.6, label=label)
        indices_used.append(s.index)
        if earliest is None or s.index[0] < earliest:
            earliest = s.index[0]
    ax.axhline(0, color=COLORS["fog"], linestyle="--", linewidth=0.7)
    if indices_used:
        set_xlim_to_data(ax, *indices_used)
    style_single_ax(ax, fmt="{:+.1f}")
    leg = ax.legend(loc="upper left", **legend_style(), fontsize=9)
    leg.get_frame().set_linewidth(0.5)
    if earliest is not None:
        add_recessions(ax, start_date=earliest)
    brand_fig(fig,
              title="Pillar 1 — Labor",
              subtitle="Fragility, Pressure, Dynamism over 25 years",
              source="Lighthouse Macro composites")
    return fig_b64(fig)


def chart_pci_history(conn) -> str:
    s = _composite_series(conn, "PCI", years=25)
    if s.empty:
        return ""
    fig, ax = new_fig(figsize=(13, 5.0))
    ax.fill_between(s.index, 0, s.values, where=(s.values > 0),
                    color=COLORS["dusk"], alpha=0.18, linewidth=0)
    ax.fill_between(s.index, 0, s.values, where=(s.values < 0),
                    color=COLORS["ocean"], alpha=0.18, linewidth=0)
    ax.plot(s.index, s.values, color=COLORS["ocean"], linewidth=1.6)
    ax.axhline(0, color=COLORS["fog"], linestyle="--", linewidth=0.7)
    ax.axhline(1.5, color=COLORS["port"], linestyle=":", linewidth=0.8)
    ax.axhline(-1.5, color=COLORS["starboard"], linestyle=":", linewidth=0.8)
    style_single_ax(ax, fmt="{:+.1f}")
    add_last_value_label(ax, s, COLORS["ocean"], fmt="{:+.2f}")
    set_xlim_to_data(ax, s.index)
    add_recessions(ax, start_date=s.index[0])
    brand_fig(fig,
              title="Pillar 2 — Inflation Heat",
              subtitle="25y composite. Dusk shading above zero, Ocean below.",
              source="Lighthouse Macro composites",
              data_date=s.index[-1])
    return fig_b64(fig)


def chart_growth_vs_wei(conn) -> str:
    gci = _composite_series(conn, "GCI", years=25)
    # WEI starts ~2008; full history of overlap is the real story.
    wei = pd.read_sql(
        "SELECT date, value FROM observations WHERE series_id='WEI' "
        "ORDER BY date",
        conn, parse_dates=["date"]
    ).set_index("date")["value"].dropna()
    if gci.empty:
        return ""
    fig, ax = new_fig(figsize=(13, 5.0))
    ax2 = ax.twinx()
    ax.plot(gci.index, gci.values, color=COLORS["dusk"], linewidth=1.6,
            label="Activity Pulse (GCI)")
    if not wei.empty:
        ax2.plot(wei.index, wei.values, color=COLORS["ocean"], linewidth=1.6,
                 label="NY Fed WEI (right)")
    style_dual_ax(ax, ax2, COLORS["dusk"], COLORS["ocean"])
    ax.axhline(0, color=COLORS["fog"], linestyle="--", linewidth=0.7)
    align_yaxis_smart(ax, ax2, s1=gci.values, s2=(wei.values if not wei.empty else None))
    add_last_value_label(ax, gci, COLORS["dusk"], fmt="{:+.2f}", side="left")
    if not wei.empty:
        add_last_value_label(ax2, wei, COLORS["ocean"], fmt="{:+.2f}", side="right")
        set_xlim_to_data(ax, gci.index, wei.index)
    else:
        set_xlim_to_data(ax, gci.index)
    add_recessions(ax, start_date=gci.index[0])
    brand_fig(fig,
              title="Pillar 3 — Activity Pulse vs NY Fed WEI",
              subtitle="GCI (Dusk, left) and Weekly Economic Index (Ocean, right)",
              source="Lighthouse Macro composites; NY Fed",
              data_date=gci.index[-1])
    return fig_b64(fig)


def chart_housing_vs_10y(conn) -> str:
    hci = _composite_series(conn, "HCI", years=25)
    tsy = pd.read_sql(
        "SELECT date, value FROM observations WHERE series_id='DGS10' "
        "AND date >= date('now','-25 year') ORDER BY date",
        conn, parse_dates=["date"]
    ).set_index("date")["value"].dropna()
    if hci.empty:
        return ""
    fig, ax = new_fig(figsize=(13, 5.0))
    ax2 = ax.twinx()
    ax.plot(hci.index, hci.values, color=COLORS["ocean"], linewidth=1.6,
            label="Housing Tide (HCI)")
    if not tsy.empty:
        ax2.plot(tsy.index, tsy.values, color=COLORS["dusk"], linewidth=1.6,
                 label="10Y yield (right)")
    style_dual_ax(ax, ax2, COLORS["ocean"], COLORS["dusk"])
    ax.axhline(0, color=COLORS["fog"], linestyle="--", linewidth=0.7)
    align_yaxis_smart(ax, ax2, s1=hci.values,
                      s2=(tsy.values if not tsy.empty else None))
    add_last_value_label(ax, hci, COLORS["ocean"], fmt="{:+.2f}", side="left")
    if not tsy.empty:
        add_last_value_label(ax2, tsy, COLORS["dusk"], fmt="{:.2f}%", side="right")
        set_xlim_to_data(ax, hci.index, tsy.index)
    else:
        set_xlim_to_data(ax, hci.index)
    add_recessions(ax, start_date=hci.index[0])
    brand_fig(fig,
              title="Pillar 4 — Housing Tide vs 10Y",
              subtitle="HCI (Ocean, left) vs 10Y Treasury (Dusk, right) over 25y",
              source="Lighthouse Macro composites; FRED DGS10",
              data_date=hci.index[-1])
    return fig_b64(fig)


def chart_credit_spreads(conn) -> str:
    hy = pd.read_sql(
        "SELECT date, value FROM observations WHERE series_id='BAMLH0A0HYM2' "
        "AND date >= date('now','-25 year') ORDER BY date",
        conn, parse_dates=["date"]
    ).set_index("date")["value"].dropna() * 100  # to bps
    ig = pd.read_sql(
        "SELECT date, value FROM observations WHERE series_id='BAMLC0A0CM' "
        "AND date >= date('now','-25 year') ORDER BY date",
        conn, parse_dates=["date"]
    ).set_index("date")["value"].dropna() * 100
    if hy.empty:
        return ""
    fig, ax = new_fig(figsize=(13, 5.0))
    ax2 = ax.twinx()
    ax.plot(hy.index, hy.values, color=COLORS["ocean"], linewidth=1.4,
            label="HY OAS, bps")
    if not ig.empty:
        ax2.plot(ig.index, ig.values, color=COLORS["dusk"], linewidth=1.4,
                 label="IG OAS, bps (right)")
    ax.axhline(300, color=COLORS["dusk"], linestyle=":", linewidth=0.8)
    ax.axhline(500, color=COLORS["port"], linestyle=":", linewidth=0.8)
    style_dual_ax(ax, ax2, COLORS["ocean"], COLORS["dusk"])
    # Spread levels are positive-only; midpoint alignment lets the two curves
    # overlay meaningfully despite very different scales.
    align_yaxis_midpoint(ax, ax2, s1=hy.values,
                         s2=(ig.values if not ig.empty else None))
    add_last_value_label(ax, hy, COLORS["ocean"], fmt="{:.0f}", side="left")
    if not ig.empty:
        add_last_value_label(ax2, ig, COLORS["dusk"], fmt="{:.0f}", side="right")
        set_xlim_to_data(ax, hy.index, ig.index)
    else:
        set_xlim_to_data(ax, hy.index)
    add_recessions(ax, start_date=hy.index[0])
    brand_fig(fig,
              title="Pillar 9 — Credit Spreads",
              subtitle="ICE BofA HY OAS (Ocean) and IG OAS (Dusk) over 25y",
              source="FRED BAMLH0A0HYM2 / BAMLC0A0CM",
              data_date=hy.index[-1])
    return fig_b64(fig)


def chart_plumbing(conn) -> str:
    # RRP starts ~2003; WALCL has decades of history. Use 25y window so the
    # full QE / QT cycle is visible.
    rrp = pd.read_sql(
        "SELECT date, value FROM observations WHERE series_id='RRPONTSYD' "
        "AND date >= date('now','-25 year') ORDER BY date",
        conn, parse_dates=["date"]
    ).set_index("date")["value"].dropna() / 1e3  # to $B
    walcl = pd.read_sql(
        "SELECT date, value FROM observations WHERE series_id='WALCL' "
        "AND date >= date('now','-25 year') ORDER BY date",
        conn, parse_dates=["date"]
    ).set_index("date")["value"].dropna() / 1e6  # to $T
    if rrp.empty and walcl.empty:
        return ""
    fig, ax = new_fig(figsize=(13, 5.0))
    ax2 = ax.twinx()
    if not rrp.empty:
        ax.fill_between(rrp.index, 0, rrp.values, color=COLORS["ocean"], alpha=0.15)
        ax.plot(rrp.index, rrp.values, color=COLORS["ocean"], linewidth=1.4,
                label="RRP, $B")
    if not walcl.empty:
        ax2.plot(walcl.index, walcl.values, color=COLORS["dusk"], linewidth=1.4,
                 label="Fed BS, $T (right)")
    style_dual_ax(ax, ax2, COLORS["ocean"], COLORS["dusk"])
    # Both positive-only and on different scales — midpoint align.
    align_yaxis_midpoint(
        ax, ax2,
        s1=(rrp.values if not rrp.empty else None),
        s2=(walcl.values if not walcl.empty else None),
    )
    if not rrp.empty:
        add_last_value_label(ax, rrp, COLORS["ocean"], fmt="${:.0f}B", side="left")
    if not walcl.empty:
        add_last_value_label(ax2, walcl, COLORS["dusk"], fmt="${:.2f}T", side="right")
    if not rrp.empty and not walcl.empty:
        set_xlim_to_data(ax, rrp.index, walcl.index)
    elif not walcl.empty:
        set_xlim_to_data(ax, walcl.index)
    else:
        set_xlim_to_data(ax, rrp.index)
    start_date = (rrp.index[0] if not rrp.empty else walcl.index[0])
    add_recessions(ax, start_date=start_date)
    end_date = (rrp.index[-1] if not rrp.empty else walcl.index[-1])
    brand_fig(fig,
              title="Pillar 10 — Plumbing",
              subtitle="RRP balance ($B, left) and Fed balance sheet ($T, right) — 25y",
              source="FRED RRPONTSYD / WALCL",
              data_date=end_date)
    return fig_b64(fig)


def chart_breadth(conn) -> str:
    series_ids = [
        ("SPX_PCT_ABOVE_20D",  COLORS["ocean"],  "% > 20d"),
        ("SPX_PCT_ABOVE_50D",  COLORS["dusk"],   "% > 50d"),
        ("SPX_PCT_ABOVE_200D", COLORS["sea"],    "% > 200d"),
    ]
    fig, ax = new_fig(figsize=(13, 5.0))
    indices_used = []
    earliest = None
    for sid, color, label in series_ids:
        df = pd.read_sql(
            "SELECT date, value FROM observations WHERE series_id=? "
            "AND date >= date('now','-25 year') ORDER BY date",
            conn, parse_dates=["date"], params=(sid,)
        ).set_index("date")["value"].dropna()
        if df.empty:
            continue
        ax.plot(df.index, df.values, color=color, linewidth=1.0, label=label,
                alpha=0.85)
        indices_used.append(df.index)
        if earliest is None or df.index[0] < earliest:
            earliest = df.index[0]
    ax.axhline(80, color=COLORS["fog"], linewidth=0.7, linestyle=":")
    ax.axhline(25, color=COLORS["fog"], linewidth=0.7, linestyle=":")
    ax.set_ylim(0, 100)
    style_single_ax(ax, fmt="{:.0f}")
    leg = ax.legend(loc="lower left", ncol=3, **legend_style(), fontsize=9)
    leg.get_frame().set_linewidth(0.5)
    if indices_used:
        set_xlim_to_data(ax, *indices_used)
    if earliest is not None:
        add_recessions(ax, start_date=earliest)
    brand_fig(fig,
              title="Pillar 11 — S&P 500 Breadth",
              subtitle="% of members above 20d, 50d, and 200d MAs — full history",
              source="Lighthouse Macro breadth fetcher")
    return fig_b64(fig)


def chart_sentiment(conn) -> str:
    # AAII goes back to 1987; VIX to 1990. Use full history.
    aaii = pd.read_sql(
        "SELECT date, value FROM observations WHERE series_id='AAII_Bull_Bear_Spread' "
        "AND date >= date('now','-25 year') ORDER BY date",
        conn, parse_dates=["date"]
    ).set_index("date")["value"].dropna() * 100  # to percentage points
    vix = pd.read_sql(
        "SELECT date, value FROM observations WHERE series_id='VIXCLS' "
        "AND date >= date('now','-25 year') ORDER BY date",
        conn, parse_dates=["date"]
    ).set_index("date")["value"].dropna()
    if aaii.empty:
        return ""
    fig, ax = new_fig(figsize=(13, 5.0))
    ax2 = ax.twinx()
    ax.bar(aaii.index, aaii.values, color=COLORS["ocean"], alpha=0.45, width=4)
    ax.axhline(30, color=COLORS["port"], linewidth=0.8, linestyle=":")
    ax.axhline(-20, color=COLORS["starboard"], linewidth=0.8, linestyle=":")
    if not vix.empty:
        ax2.plot(vix.index, vix.values, color=COLORS["dusk"], linewidth=1.0,
                 alpha=0.85, label="VIX (right)")
    style_dual_ax(ax, ax2, COLORS["ocean"], COLORS["dusk"])
    # AAII spread crosses zero; VIX is positive-only. align_yaxis_smart
    # detects this and uses zero alignment.
    align_yaxis_smart(ax, ax2, s1=aaii.values,
                      s2=(vix.values if not vix.empty else None))
    add_last_value_label(ax, aaii, COLORS["ocean"], fmt="{:+.1f}", side="left")
    if not vix.empty:
        add_last_value_label(ax2, vix, COLORS["dusk"], fmt="{:.1f}", side="right")
        set_xlim_to_data(ax, aaii.index, vix.index)
    else:
        set_xlim_to_data(ax, aaii.index)
    add_recessions(ax, start_date=aaii.index[0])
    brand_fig(fig,
              title="Pillar 12 — Sentiment",
              subtitle="AAII bull-bear (Ocean bars, left) and VIX (Dusk, right) — 25y",
              source="AAII; CBOE VIXCLS",
              data_date=aaii.index[-1])
    return fig_b64(fig)


def chart_cross_asset() -> str:
    """12-month normalized cross-asset performance via yfinance."""
    try:
        import yfinance as yf
    except ImportError:
        return ""
    tickers = [
        ("SPY",     COLORS["ocean"]),
        ("QQQ",     COLORS["dusk"]),
        ("TLT",     COLORS["sea"]),
        ("HYG",     COLORS["sky"]),
        ("GLD",     COLORS["bright"]),
        ("BTC-USD", COLORS["venus"]),
    ]
    fig, ax = new_fig(figsize=(13, 5.4))
    last_date = None
    for sym, color in tickers:
        try:
            h = yf.Ticker(sym).history(period="370d", auto_adjust=False)
            if h.empty:
                continue
            h.index = h.index.tz_localize(None).normalize()
            norm = h["Close"] / h["Close"].iloc[0] * 100
            label = sym.replace("-USD", "")
            ax.plot(norm.index, norm.values, color=color, linewidth=1.8,
                    label=label)
            last_date = norm.index[-1]
        except Exception:
            continue
    ax.axhline(100, color=COLORS["fog"], linewidth=0.7, linestyle="--")
    style_single_ax(ax, fmt="{:.0f}")
    leg = ax.legend(loc="upper left", ncol=6, **legend_style(), fontsize=9)
    leg.get_frame().set_linewidth(0.5)
    brand_fig(fig,
              title="Cross-Asset, 12 Months",
              subtitle="Normalized total return. SPY, QQQ, TLT, HYG, GLD, BTC.",
              source="Yahoo Finance close prices",
              data_date=last_date)
    return fig_b64(fig)


# ============================================================================
# DATA
# ============================================================================

def fetch_state(conn) -> dict:
    rows = conn.execute("""
        WITH latest AS (
          SELECT i.index_id, i.value, i.status, i.date
          FROM lighthouse_indices i
          JOIN (SELECT index_id AS iid, MAX(date) AS md FROM lighthouse_indices
                GROUP BY index_id) m ON m.iid=i.index_id AND m.md=i.date
        )
        SELECT l.index_id, l.value, l.status, l.date,
          (SELECT value FROM lighthouse_indices p
            WHERE p.index_id=l.index_id AND p.date <= date(l.date,'-7 day')
            ORDER BY p.date DESC LIMIT 1) AS v_7d,
          (SELECT value FROM lighthouse_indices p
            WHERE p.index_id=l.index_id AND p.date <= date(l.date,'-21 day')
            ORDER BY p.date DESC LIMIT 1) AS v_21d
        FROM latest l
    """).fetchall()
    out = {}
    for r in rows:
        v, v7, v21 = r[1], r[4], r[5]
        out[r[0]] = {
            "value": v, "status": r[2], "date": r[3],
            "delta_7d":  (v - v7) if (v is not None and v7 is not None) else None,
            "delta_21d": (v - v21) if (v is not None and v21 is not None) else None,
        }
    return out


def fetch_markets() -> dict:
    try:
        import yfinance as yf
    except ImportError:
        return {}
    tickers = {
        "SPY": "SPY", "QQQ": "QQQ", "IWM": "IWM", "RSP": "RSP",
        "EFA": "EFA", "EEM": "EEM", "TLT": "TLT", "SHY": "SHY",
        "^TNX": "10Y", "^FVX": "5Y", "^TYX": "30Y", "^IRX": "3M",
        "HYG": "HYG", "LQD": "LQD",
        "DX-Y.NYB": "DXY", "EURUSD=X": "EURUSD",
        "GLD": "GLD", "USO": "USO", "DBC": "DBC",
        "BTC-USD": "BTC", "ETH-USD": "ETH",
        "^VIX": "VIX", "QAI": "QAI",
    }
    out = {}
    for sym, name in tickers.items():
        try:
            h = yf.Ticker(sym).history(period="260d", auto_adjust=False)
            if h.empty or len(h) < 5:
                continue
            h.index = h.index.tz_localize(None).normalize()
            c = h["Close"]
            last = float(c.iloc[-1]); prev = float(c.iloc[-2])
            chg = (last - prev) / prev * 100
            ma50 = float(c.rolling(50).mean().iloc[-1])
            ma200 = float(c.rolling(200).mean().iloc[-1]) if len(c) >= 200 else None
            out[name] = {
                "price": last, "chg_1d_pct": chg,
                "vs_50": (last / ma50 - 1) * 100 if ma50 else None,
                "vs_200": (last / ma200 - 1) * 100 if ma200 else None,
                "asof": h.index[-1].date().isoformat(),
            }
        except Exception:
            continue
    return out


# ============================================================================
# RENDER HTML
# ============================================================================

def color_for_status(status: str | None) -> str:
    s = (status or "").upper()
    if any(w in s for w in ("CRISIS", "RECESSION", "EXTREME", "CRITICAL",
                            "STRESS RISK", "RED", "MISPRICED", "MAX DEFENSIVE",
                            "INFLATION CRISIS", "DEFLATIONARY",
                            "CAPITAL PRESERVATION")):
        return PORT
    if any(w in s for w in ("PRE-RECESSION", "PRE_CRISIS", "LATE CYCLE",
                            "ELEVATED", "HEADWIND", "FROZEN", "WEAK",
                            "DISTRIBUTION", "SLUGGISH", "EUPHORIC", "TIGHT",
                            "BILLS VERY RICH", "FEAR + WEAK", "HIGH INFLATION",
                            "STRESSED")):
        return DUSK
    if any(w in s for w in ("HEALTHY", "BOOM", "EXPANSION", "STRONG",
                            "BULLISH", "ABUNDANT", "EARLY EXPANSION",
                            "LOW RISK", "ON TARGET", "FISCAL HEALTH",
                            "HIGH DYNAMISM")):
        return STARBOARD
    if any(w in s for w in ("NEUTRAL", "MID-CYCLE", "BALANCED", "TREND",
                            "MODERATE", "AMPLE", "NORMAL")):
        return DOLDRUMS
    return OCEAN


def fmt_delta(d):
    return "n/a" if d is None else f"{d:+.2f}"


def render_brief(state: dict, mkt: dict,
                 charts: dict, run_date: str) -> str:
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M ET")

    def row(code, label=None):
        d = state.get(code, {})
        v = d.get("value"); st = d.get("status") or "—"
        c = color_for_status(st)
        return (
            f'<tr><td>{label or code}</td>'
            f'<td class="num">{(v if v is not None else 0):+.3f}</td>'
            f'<td class="num delta">{fmt_delta(d.get("delta_7d"))}</td>'
            f'<td class="num delta">{fmt_delta(d.get("delta_21d"))}</td>'
            f'<td><span class="pill" style="background:{c};">{st}</span></td></tr>'
        )

    def master_tile(code, name, fmt):
        d = state.get(code, {})
        v = d.get("value"); st = d.get("status") or "—"
        c = color_for_status(st)
        if v is None:
            val_txt = "—"
        elif fmt == "pct":
            val_txt = f"{v*100:.1f}%" if abs(v) < 2 else f"{v:.1f}%"
        elif fmt == "mult":
            val_txt = f"{v:.2f}×"
        elif fmt == "level":
            val_txt = f"{int(round(v))}"
        else:
            val_txt = f"{v:+.2f}"
        return (
            f'<div class="master-tile">'
            f'<div class="master-tile-name">{name}</div>'
            f'<div class="master-tile-value" style="color:{c};">{val_txt}</div>'
            f'<div class="master-tile-status" style="background:{c};">{st}</div>'
            f'</div>'
        )

    def chart(key, alt):
        # Single white-canvas chart per indicator. Works on both light
        # (Glacier page) and dark (Deep page) — the white card pops against
        # both, premium-dashboard style.
        b64 = charts.get(key, "")
        if not b64:
            return ""
        return (
            f'<figure class="chart">'
            f'<img alt="{alt}" src="data:image/png;base64,{b64}"/>'
            f'</figure>'
        )

    def market_row(name):
        m = mkt.get(name, {})
        if not m:
            return f'<tr><td>{name}</td><td colspan="4" class="num">—</td></tr>'
        chg = m.get("chg_1d_pct") or 0
        cc = STARBOARD if chg >= 0 else PORT
        return (
            f'<tr><td>{name}</td>'
            f'<td class="num">{m.get("price"):.2f}</td>'
            f'<td class="num" style="color:{cc};">{chg:+.2f}%</td>'
            f'<td class="num">{(m.get("vs_50") or 0):+.1f}%</td>'
            f'<td class="num">{(m.get("vs_200") or 0):+.1f}%</td></tr>'
        )

    mri = state.get("MRI", {}).get("value")
    warn = state.get("WARNING_LEVEL", {}).get("value")
    disc = state.get("DISCONTINUITY_PREMIUM", {}).get("value")
    alloc = state.get("ALLOC_MULTIPLIER", {}).get("value")
    sbd = state.get("SBD", {}).get("value")
    ssd = state.get("SSD", {}).get("value")
    rec = state.get("REC_PROB", {}).get("value")
    spy_chg = (mkt.get("SPY") or {}).get("chg_1d_pct")
    vix = (mkt.get("VIX") or {}).get("price")
    ten_y = (mkt.get("10Y") or {}).get("price")
    dxy = (mkt.get("DXY") or {}).get("price")

    note_html = (
        f'<p>The Macro Risk Index sits at <strong>{mri:+.2f}</strong>, '
        f'Warning Level <strong>{int(round(warn)) if warn is not None else "—"}</strong>, '
        f'Allocation Multiplier <strong>{alloc:.2f}×</strong>, '
        f'Discontinuity Premium <strong>{disc:+.2f}</strong>. '
        f'Recession Probability prints at <strong>{rec*100:.1f}%</strong>.</p>'
        if mri is not None and disc is not None and alloc is not None and rec is not None
        else "<p>State unavailable.</p>"
    )

    market_prose = (
        f'<p>{link_phrase("SPY")} closed {spy_chg:+.2f}% with {link_phrase("VIX")} at '
        f'{vix:.2f}. The {link_phrase("10-year Treasury")} prints {ten_y:.2f}%. '
        f'{link_phrase("DXY")} sits at {dxy:.2f}.</p>'
        if spy_chg is not None and vix and ten_y and dxy else ""
    )

    sbd_prose = (
        f'<p>{link_phrase("AAII bull-bear")} and the structure read tell a split story. '
        f'SBD at <strong>{sbd:+.2f}</strong> sits in extreme distribution territory while '
        f'SSD at <strong>{ssd:+.2f}</strong> creeps toward the +1.5 capitulation print.</p>'
        if sbd is not None and ssd is not None else ""
    )

    return f"""<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
<meta charset="UTF-8">
<title>LHM Daily Briefing · {run_date}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@600;700;800&family=Inter:wght@400;500;600&family=Source+Code+Pro:wght@400;600&display=swap" rel="stylesheet">
<style>
  :root{{
    --ocean:{OCEAN}; --dusk:{DUSK}; --sky:{SKY}; --bright:{BRIGHT}; --deep:{DEEP};
    --sea:{SEA}; --venus:{VENUS}; --doldrums:{DOLDRUMS};
    --starboard:{STARBOARD}; --port:{PORT}; --fog:{FOG};
    --offwhite:{OFFWHITE}; --glacier:{GLACIER};
    --ink:{INK}; --paper:#ffffff;
  }}
  *{{box-sizing:border-box;}}
  html,body{{margin:0; padding:0; font-family:'Inter', sans-serif; font-size:14px; line-height:1.6;}}

  /* LIGHT theme (default)
     Page bg = Glacier (pale icy blue). Cards and charts = Paper white. The
     subtle blue tint of the page lets white cards read as lifted surfaces. */
  html[data-theme="light"] body{{ background:var(--glacier); color:var(--ink); }}
  html[data-theme="light"] .card,
  html[data-theme="light"] .master-tile,
  html[data-theme="light"] figure.chart{{ background:var(--paper); border-color:#cfdde6; }}
  html[data-theme="light"] .footer, html[data-theme="light"] th{{ color:var(--doldrums); }}
  html[data-theme="light"] th{{ border-bottom-color:var(--doldrums); }}
  html[data-theme="light"] td{{ border-bottom-color:#cfdde6; }}
  html[data-theme="light"] h2{{ border-bottom-color:#cfdde6; }}
  html[data-theme="light"] a{{ color:var(--ocean); }}

  /* DARK theme
     Page bg = Deep. Cards = Deep-lift. Chart canvas STAYS WHITE (premium
     dashboard pattern): a white card on a Deep page reads sharp without
     forcing the chart palette to fight a dark canvas. */
  html[data-theme="dark"] body{{ background:var(--deep); color:var(--offwhite); }}
  html[data-theme="dark"] .card,
  html[data-theme="dark"] .master-tile{{ background:#1a3a5a; border-color:#3b5a7a; }}
  html[data-theme="dark"] figure.chart{{ background:var(--paper); border-color:#3b5a7a; }}
  html[data-theme="dark"] .footer, html[data-theme="dark"] th{{ color:#9bb1c5; }}
  html[data-theme="dark"] th{{ border-bottom-color:#3b5a7a; }}
  html[data-theme="dark"] td{{ border-bottom-color:#22466e; }}
  html[data-theme="dark"] a{{ color:var(--bright); }}
  html[data-theme="dark"] h2{{ border-bottom-color:#3b5a7a; }}
  html[data-theme="dark"] .theme-toggle{{ border-color:var(--bright); color:var(--bright); }}
  html[data-theme="dark"] .theme-toggle:hover{{ background:var(--bright); color:var(--deep); }}
  html[data-theme="dark"] .kicker{{ color:var(--bright); }}

  .wrap{{max-width:1180px; margin:0 auto; padding:28px 32px 64px;}}
  .accent-bar{{display:flex; height:6px; width:100%; margin-bottom:18px;}}
  .accent-bar .ocean{{flex:2; background:var(--ocean);}}
  .accent-bar .dusk{{flex:1; background:var(--dusk);}}
  .header{{display:flex; justify-content:space-between; align-items:flex-end; flex-wrap:wrap; gap:12px;}}
  .kicker{{font-family:'Source Code Pro', monospace; font-size:11px; letter-spacing:0.14em; color:var(--ocean); text-transform:uppercase; font-weight:600;}}
  h1{{font-family:'Montserrat', sans-serif; font-weight:800; font-size:34px; letter-spacing:-0.015em; margin:6px 0 0;}}
  .stamps{{text-align:right; font-family:'Source Code Pro', monospace; font-size:11px;}}
  .stamps strong{{font-size:13px; font-weight:600;}}
  .theme-toggle{{font-family:'Source Code Pro', monospace; font-size:11px; padding:6px 12px; border-radius:14px; border:1px solid var(--ocean); background:transparent; color:inherit; cursor:pointer; margin-left:12px; font-weight:600; letter-spacing:0.05em;}}
  .theme-toggle:hover{{ background:var(--ocean); color:#fff; }}
  h2{{font-family:'Montserrat', sans-serif; font-weight:700; font-size:18px; margin:36px 0 8px; padding-bottom:6px; border-bottom:1px solid var(--fog); letter-spacing:-0.005em;}}
  h3{{font-family:'Montserrat', sans-serif; font-weight:600; font-size:12px; margin:14px 0 6px; color:var(--ocean); text-transform:uppercase; letter-spacing:0.06em;}}
  p{{margin:0 0 12px;}}
  a{{text-decoration:none;}}
  a:hover{{text-decoration:underline;}}
  .master-row{{display:grid; grid-template-columns:repeat(4, 1fr); gap:12px; margin:14px 0 20px;}}
  .master-tile{{border:1px solid var(--fog); border-radius:10px; padding:14px 16px;}}
  .master-tile-name{{font-family:'Montserrat', sans-serif; font-weight:700; font-size:12px; text-transform:uppercase; letter-spacing:0.05em; color:var(--doldrums);}}
  .master-tile-value{{font-family:'Source Code Pro', monospace; font-weight:600; font-size:30px; margin:6px 0 8px; letter-spacing:-0.01em;}}
  .master-tile-status{{display:inline-block; padding:3px 10px; border-radius:11px; font-family:'Source Code Pro', monospace; font-size:11px; font-weight:600; color:#fff; letter-spacing:0.04em;}}
  table{{width:100%; border-collapse:collapse; font-size:12.5px; margin:8px 0 8px;}}
  th,td{{padding:6px 9px; text-align:left; vertical-align:top; border-bottom:1px solid;}}
  th{{font-family:'Source Code Pro', monospace; font-size:10.5px; text-transform:uppercase; letter-spacing:0.05em;}}
  td.num{{font-family:'Source Code Pro', monospace; text-align:right;}}
  td.delta{{font-size:11.5px;}}
  .pill{{display:inline-block; padding:2px 9px; border-radius:11px; font-family:'Source Code Pro', monospace; font-size:10.5px; font-weight:600; color:#fff; letter-spacing:0.04em; white-space:nowrap;}}
  figure.chart{{margin:18px 0 22px; border:1px solid; border-radius:10px; overflow:hidden;}}
  figure.chart img{{display:block; width:100%; height:auto;}}
  .grid-2col{{display:grid; grid-template-columns:1fr 1fr; gap:12px;}}
  .footer{{margin-top:48px; padding-top:14px; border-top:1px solid var(--fog); font-size:11px; font-family:'Source Code Pro', monospace; display:flex; justify-content:space-between;}}
</style>
</head>
<body>
<div class="wrap">

  <div class="accent-bar"><div class="ocean"></div><div class="dusk"></div></div>
  <div class="header">
    <div>
      <div class="kicker">Lighthouse Macro · Daily Briefing</div>
      <h1>{now.strftime('%A, %B %-d, %Y')}</h1>
    </div>
    <div class="stamps">
      <div>Generated</div>
      <strong>{timestamp}</strong>
      <div>Indicator stamps as of {run_date}</div>
      <button class="theme-toggle" onclick="document.documentElement.dataset.theme = (document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark');">Toggle theme</button>
    </div>
  </div>

  <h2>MRI Regime Snapshot</h2>
  <div class="master-row">
    {master_tile("MRI", "Macro Risk Index", "z")}
    {master_tile("REC_PROB", "Recession Probability", "pct")}
    {master_tile("ALLOC_MULTIPLIER", "Allocation Multiplier", "mult")}
    {master_tile("WARNING_LEVEL", "Warning Level", "level")}
  </div>
  <div class="grid-2col">
    <table>
      <thead><tr><th>Metric</th><th>z / level</th><th>Status</th></tr></thead>
      <tbody>
        <tr><td>Ensemble Risk</td><td class="num">{(state.get('ENSEMBLE_RISK', {}).get('value') or 0):.3f}</td>
            <td><span class="pill" style="background:{color_for_status(state.get('ENSEMBLE_RISK', {}).get('status'))};">{state.get('ENSEMBLE_RISK', {}).get('status') or '—'}</span></td></tr>
        <tr><td>Discontinuity Premium</td><td class="num">{(state.get('DISCONTINUITY_PREMIUM', {}).get('value') or 0):+.3f}</td>
            <td><span class="pill" style="background:{color_for_status(state.get('DISCONTINUITY_PREMIUM', {}).get('status'))};">{state.get('DISCONTINUITY_PREMIUM', {}).get('status') or '—'}</span></td></tr>
        <tr><td>Base Recession Prob</td><td class="num">{(state.get('BASE_REC_PROB', {}).get('value') or 0)*100:.2f}%</td>
            <td><span class="pill" style="background:{color_for_status(state.get('BASE_REC_PROB', {}).get('status'))};">{state.get('BASE_REC_PROB', {}).get('status') or '—'}</span></td></tr>
      </tbody>
    </table>
    <table>
      <thead><tr><th>Asset</th><th>Price</th><th>1d</th><th>vs 50d</th><th>vs 200d</th></tr></thead>
      <tbody>
        {market_row("SPY")}
        {market_row("VIX")}
        {market_row("10Y")}
        {market_row("HYG")}
        {market_row("DXY")}
        {market_row("BTC")}
      </tbody>
    </table>
  </div>

  {chart("mri", "Macro Risk Index 3y history")}

  <h2>The Diagnostic Dozen</h2>
  {chart("heatmap", "12-pillar heatmap")}

  <h3>Engine 1 — Macro Dynamics</h3>
  <table>
    <thead><tr><th>Indicator</th><th>z</th><th>Δ 7d</th><th>Δ 21d</th><th>Read</th></tr></thead>
    <tbody>
      {row("LFI", "Labor Fragility (P1)")}
      {row("LPI", "Labor Pressure (P1)")}
      {row("LDI", "Labor Dynamism (P1)")}
      {row("PCI", "Inflation Heat (P2)")}
      {row("GCI", "Activity Pulse (P3)")}
      {row("HCI", "Housing Tide (P4)")}
      {row("CCI", "Consumer Pulse (P5)")}
      {row("BCI", "Capex Thrust (P6)")}
      {row("TCI", "Global Risk Tide (P7)")}
    </tbody>
  </table>

  {chart("labor", "Labor stack: LFI / LPI / LDI")}
  {chart("pci", "Inflation Heat 3y")}
  {chart("growth", "Activity Pulse vs WEI")}
  {chart("housing", "Housing Tide vs 10Y yield")}

  <h3>Engine 2 — Monetary Mechanics</h3>
  <table>
    <thead><tr><th>Indicator</th><th>z / level</th><th>Δ 7d</th><th>Δ 21d</th><th>Read</th></tr></thead>
    <tbody>
      {row("FPI", "Fiscal Pressure (P8)")}
      {row("FCI", "Credit Tide (P9)")}
      {row("LCI", "Liquidity Cushion (P10)")}
      {row("LIQ_STAGE", "Liquidity Stage (P10)")}
      {row("CLG", "Credit-Labor Gap (cross 1↔9)")}
      {row("YFS", "Yield-Funding Stress (cross 8+10)")}
      {row("SVI", "Spread-Volatility Imbalance (cross 9+12)")}
    </tbody>
  </table>

  {chart("credit", "Credit spreads HY / IG")}
  {chart("plumbing", "Plumbing — RRP + Fed BS")}

  <h3>Engine 3 — Market Structure</h3>
  <table>
    <thead><tr><th>Indicator</th><th>z</th><th>Δ 7d</th><th>Δ 21d</th><th>Read</th></tr></thead>
    <tbody>
      {row("MSI", "Market Breadth Pulse (P11)")}
      {row("SBD", "Structure-Breadth Divergence (P11)")}
      {row("EMD", "Equity Momentum Divergence (P11)")}
      {row("SPI", "Sentiment Tide (P12)")}
      {row("SSD", "Sent-Structure Divergence (cross 11↔12)")}
    </tbody>
  </table>

  {chart("breadth", "SPX breadth %s above MAs")}
  {chart("sentiment", "AAII bull-bear + VIX")}

  <h2>Cross-Asset</h2>
  <table>
    <thead><tr><th>Asset</th><th>Price</th><th>1d</th><th>vs 50d</th><th>vs 200d</th></tr></thead>
    <tbody>
      {market_row("SPY")}
      {market_row("QQQ")}
      {market_row("IWM")}
      {market_row("RSP")}
      {market_row("EFA")}
      {market_row("EEM")}
      {market_row("TLT")}
      {market_row("SHY")}
      {market_row("10Y")}
      {market_row("HYG")}
      {market_row("LQD")}
      {market_row("DXY")}
      {market_row("GLD")}
      {market_row("USO")}
      {market_row("BTC")}
      {market_row("ETH")}
      {market_row("VIX")}
      {market_row("QAI")}
    </tbody>
  </table>

  {chart("crossasset", "Cross-asset 12-month normalized")}

  <h2>Daily Note</h2>
  {note_html}
  {market_prose}
  {sbd_prose}
  <p>The framework is split: Engine 1 reads expansion, Engines 2 and 3 are flashing
  regime-change risk. {link_phrase("HY OAS")} sits below the 300 bps complacency floor.
  {link_phrase("RRP")} balance is functionally exhausted. Bridge tail extends the
  framework via daily proxies so every composite carries a current read.</p>
  <p>Watch the next inflation print and the {link_phrase("FOMC")} leadership transition
  signal. A {link_phrase("UMich")} sentiment break below the consensus would harden
  the Consumer Pulse stress already in the system.</p>

  <div class="footer">
    <span>Lighthouse Macro · Daily Briefing · auto-generated</span>
    <span><a href="https://lighthousemacro.com">Lighthouse Macro</a> · <a href="https://research.lighthousemacro.com">Research</a> · <a href="https://x.com/LHMacro">@LHMacro</a></span>
  </div>

</div>
</body>
</html>
"""


# ============================================================================
# MAIN
# ============================================================================

def _render_all_charts(conn) -> dict:
    """Single white-canvas chart per indicator. The HTML scaffold supplies
    its own light/dark page bg; the chart card pops against both."""
    set_theme("white")
    return {
        "mri":        chart_mri(conn),
        "heatmap":    chart_pillar_heatmap(conn),
        "labor":      chart_labor_stack(conn),
        "pci":        chart_pci_history(conn),
        "growth":     chart_growth_vs_wei(conn),
        "housing":    chart_housing_vs_10y(conn),
        "credit":     chart_credit_spreads(conn),
        "plumbing":   chart_plumbing(conn),
        "breadth":    chart_breadth(conn),
        "sentiment":  chart_sentiment(conn),
        "crossasset": chart_cross_asset(),
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--no-open", action="store_true")
    args = p.parse_args()

    conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    try:
        state = fetch_state(conn)
        run_date = max((s["date"] for s in state.values() if s.get("date")), default="—")
        mkt = fetch_markets()

        print("Rendering charts (white canvas, reused in both themes)...")
        charts = _render_all_charts(conn)
    finally:
        conn.close()

    html = render_brief(state, mkt, charts, run_date)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    dated = OUTPUT_DIR / f"daily_briefing_{datetime.now().strftime('%Y-%m-%d')}.html"
    LATEST_PATH.write_text(html)
    dated.write_text(html)
    print(f"Wrote {LATEST_PATH}")
    print(f"Wrote {dated}")

    if not args.no_open:
        try:
            subprocess.run(["open", str(LATEST_PATH)], check=False)
        except Exception:
            pass


if __name__ == "__main__":
    sys.exit(main() or 0)
