#!/usr/bin/env python3
"""
LIGHTHOUSE MACRO — DAILY BRIEFING
==================================
Generates the v3 daily briefing as a self-contained HTML document with
10 brand-compliant inline charts and inline-hyperlinked source phrases.

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
import io
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
import numpy as np
import pandas as pd

DB_PATH = Path("/Users/bob/LHM/Data/databases/Lighthouse_Master.db")
OUTPUT_DIR = Path("/Users/bob/LHM/Outputs")
LATEST_PATH = OUTPUT_DIR / "daily_briefing_latest.html"

# Brand palette
OCEAN     = "#2389BB"
DUSK      = "#FF6723"
SKY       = "#23BBFF"
SEA       = "#00BB89"
VENUS     = "#FF2389"
DOLDRUMS  = "#898989"
STARBOARD = "#238923"
PORT      = "#892323"
FOG       = "#D1D1D1"
INK       = "#1a1a1a"
PAPER     = "#ffffff"

# Inline link map. Anchor phrase → canonical source URL. Replacements only
# fire once per phrase per render so we don't link every occurrence.
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
    """Convert known anchor phrases in plain text to inline HTML hyperlinks.
    First occurrence only per phrase. Preserves the rest of the text."""
    if not text:
        return text
    seen: set[str] = set()
    # Sort phrases longest-first so we don't get partial-match collisions.
    for phrase in sorted(LINK_MAP.keys(), key=len, reverse=True):
        if phrase in seen:
            continue
        url = LINK_MAP[phrase]
        # Plain replace, first occurrence only.
        idx = text.find(phrase)
        if idx == -1:
            continue
        text = text[:idx] + f'<a href="{url}" target="_blank">{phrase}</a>' + text[idx + len(phrase):]
        seen.add(phrase)
    return text


# ============================================================================
# CHART HELPERS — brand-compliant matplotlib
# ============================================================================

def _style_axes(ax) -> None:
    ax.tick_params(colors=DOLDRUMS, labelsize=8)
    for spine in ax.spines.values():
        spine.set_color(DOLDRUMS)
        spine.set_linewidth(0.5)
    ax.grid(False)
    ax.set_facecolor(PAPER)


def _stamp(fig, ax, title: str, subtitle: str, source: str) -> None:
    """Add the brand stamps: accent bar, title, subtitle, source, watermark."""
    fig.patch.set_facecolor(PAPER)
    # Top accent bar
    fig.add_artist(plt.Rectangle((0, 0.985), 0.66, 0.012, color=OCEAN,
                                 transform=fig.transFigure, clip_on=False))
    fig.add_artist(plt.Rectangle((0.66, 0.985), 0.34, 0.012, color=DUSK,
                                 transform=fig.transFigure, clip_on=False))
    fig.text(0.02, 0.955, "LIGHTHOUSE MACRO", color=OCEAN,
             font="Montserrat", weight=700, fontsize=9, va="top")
    fig.text(0.02, 0.93, title, color=INK,
             font="Montserrat", weight=700, fontsize=13, va="top")
    if subtitle:
        fig.text(0.02, 0.895, subtitle, color=DOLDRUMS,
                 font="Inter", fontsize=9, va="top")
    fig.text(0.02, 0.02, f"Lighthouse Macro | {source}", color=DOLDRUMS,
             font="Source Code Pro", fontsize=7.5, va="bottom")
    fig.text(0.98, 0.02, "MACRO, ILLUMINATED.", color=OCEAN,
             font="Montserrat", weight=700, fontsize=8, ha="right", va="bottom")


def fig_to_b64(fig, dpi: int = 150) -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=dpi, bbox_inches="tight",
                facecolor=PAPER, pad_inches=0.06)
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode("ascii")


def chart_mri(conn) -> str:
    df = pd.read_sql(
        "SELECT date, value FROM lighthouse_indices "
        "WHERE index_id='MRI' AND date >= date('now','-3 year') "
        "ORDER BY date",
        conn, parse_dates=["date"],
    ).set_index("date")
    if df.empty:
        return ""
    fig, ax = plt.subplots(figsize=(9, 3.2))
    _style_axes(ax)
    fig.subplots_adjust(top=0.82, bottom=0.18, left=0.06, right=0.96)
    ax.axhspan(-3, -0.20, color="#e7f5ec", alpha=0.4, lw=0)
    ax.axhspan(-0.20, 0.10, color="#f2f7fc", alpha=0.5, lw=0)
    ax.axhspan(0.10, 0.25, color="#fff2e3", alpha=0.5, lw=0)
    ax.axhspan(0.25, 0.50, color="#fce0d2", alpha=0.5, lw=0)
    ax.axhspan(0.50, 3, color="#f0d4d4", alpha=0.5, lw=0)
    ax.plot(df.index, df["value"], color=OCEAN, lw=1.6)
    ax.axhline(0, color=DOLDRUMS, lw=0.5, ls="--")
    ax.set_ylim(df["value"].min() - 0.2, df["value"].max() + 0.2)
    ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 7]))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %y"))
    latest_val = df["value"].iloc[-1]
    ax.scatter([df.index[-1]], [latest_val], color=OCEAN, s=24, zorder=5)
    ax.annotate(f"{latest_val:+.2f}", xy=(df.index[-1], latest_val),
                xytext=(8, 0), textcoords="offset points",
                color=OCEAN, fontsize=9, weight="bold", va="center")
    _stamp(fig, ax,
           "Macro Risk Index", "3y history with cycle-phase shading",
           "Lighthouse Macro composites; date " + df.index.max().date().isoformat())
    return fig_to_b64(fig)


def chart_pillar_heatmap(conn) -> str:
    pillar_codes = {
        1: "LFI", 2: "PCI", 3: "GCI", 4: "HCI", 5: "CCI", 6: "BCI",
        7: "TCI", 8: "FPI", 9: "FCI", 10: "LCI", 11: "MSI", 12: "SPI",
    }
    pillar_names = {
        1: "Labor", 2: "Prices", 3: "Growth", 4: "Housing",
        5: "Consumer", 6: "Business", 7: "Trade", 8: "Govt",
        9: "Financial", 10: "Plumbing", 11: "Structure", 12: "Sentiment",
    }
    vals = {}
    for p, code in pillar_codes.items():
        r = conn.execute(
            "SELECT value FROM lighthouse_indices WHERE index_id=? "
            "ORDER BY date DESC LIMIT 1", (code,)
        ).fetchone()
        vals[p] = r[0] if r else None

    fig, ax = plt.subplots(figsize=(9, 3.4))
    _style_axes(ax)
    fig.subplots_adjust(top=0.78, bottom=0.10, left=0.04, right=0.98)
    ax.set_xlim(0, 12); ax.set_ylim(0, 2.4)
    ax.set_xticks([]); ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)

    def color_for(z):
        if z is None:
            return DOLDRUMS
        if z <= -1.5: return PORT
        if z <= -0.5: return DUSK
        if z <= 0.5:  return DOLDRUMS
        if z <= 1.5:  return SEA
        return STARBOARD

    for i in range(12):
        p = i + 1
        cx = i + 0.5
        cy = 1.4
        z = vals[p]
        ax.add_patch(plt.Circle((cx, cy), 0.34, color=color_for(z), zorder=3))
        ax.text(cx, cy, f"{p}", color="#fff",
                font="Montserrat", weight=700, fontsize=12,
                ha="center", va="center", zorder=4)
        ax.text(cx, 0.78, pillar_names[p], color=INK,
                font="Inter", fontsize=8.5, weight=600,
                ha="center", va="center")
        ax.text(cx, 0.42, f"{z:+.2f}" if z is not None else "—",
                color=DOLDRUMS, font="Source Code Pro", fontsize=8,
                ha="center", va="center")
    _stamp(fig, ax,
           "The Diagnostic Dozen",
           "Current pillar-composite z-score. Color: red = stressed, orange = elevated, gray = neutral, green = healthy",
           "Lighthouse Macro composites")
    return fig_to_b64(fig)


def chart_labor_stack(conn) -> str:
    fig, ax = plt.subplots(figsize=(9, 3.2))
    _style_axes(ax)
    fig.subplots_adjust(top=0.80, bottom=0.16, left=0.06, right=0.96)
    palette = {"LFI": OCEAN, "LPI": DUSK, "LDI": SEA}
    for code, color in palette.items():
        df = pd.read_sql(
            "SELECT date, value FROM lighthouse_indices "
            "WHERE index_id=? AND date >= date('now','-2 year') "
            "ORDER BY date",
            conn, parse_dates=["date"], params=(code,),
        ).set_index("date")
        if df.empty:
            continue
        ax.plot(df.index, df["value"], color=color, lw=1.4, label=code)
    ax.axhline(0, color=DOLDRUMS, lw=0.4, ls="--")
    ax.legend(loc="lower left", frameon=False, fontsize=8.5,
              labelcolor=DOLDRUMS, ncol=3)
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %y"))
    _stamp(fig, ax,
           "Pillar 1 — Labor",
           "LFI fragility (Ocean), LPI pressure (Dusk), LDI dynamism (Sea). 2y view.",
           "Lighthouse Macro composites")
    return fig_to_b64(fig)


def chart_pci_history(conn) -> str:
    df = pd.read_sql(
        "SELECT date, value FROM lighthouse_indices "
        "WHERE index_id='PCI' AND date >= date('now','-3 year') "
        "ORDER BY date",
        conn, parse_dates=["date"],
    ).set_index("date")
    if df.empty:
        return ""
    fig, ax = plt.subplots(figsize=(9, 3.0))
    _style_axes(ax)
    fig.subplots_adjust(top=0.80, bottom=0.16, left=0.06, right=0.96)
    ax.fill_between(df.index, 0, df["value"], where=df["value"] > 0,
                    color=DUSK, alpha=0.15)
    ax.fill_between(df.index, 0, df["value"], where=df["value"] < 0,
                    color=OCEAN, alpha=0.15)
    ax.plot(df.index, df["value"], color=INK, lw=1.4)
    ax.axhline(0, color=DOLDRUMS, lw=0.4, ls="--")
    ax.axhline(1.5, color=PORT, lw=0.5, ls=":")
    ax.axhline(-1.5, color=STARBOARD, lw=0.5, ls=":")
    ax.text(df.index[-1], 1.55, "+1.5 inflation crisis", color=PORT,
            fontsize=7, ha="right", va="bottom")
    ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 7]))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %y"))
    _stamp(fig, ax,
           "Pillar 2 — Inflation Heat",
           "3y composite. Dusk shading = above-target heat, Ocean shading = below-target slack.",
           "Lighthouse Macro composites")
    return fig_to_b64(fig)


def chart_growth_vs_wei(conn) -> str:
    gci = pd.read_sql(
        "SELECT date, value FROM lighthouse_indices "
        "WHERE index_id='GCI' AND date >= date('now','-2 year') ORDER BY date",
        conn, parse_dates=["date"]
    ).set_index("date")
    wei = pd.read_sql(
        "SELECT date, value FROM observations WHERE series_id='WEI' "
        "AND date >= date('now','-2 year') ORDER BY date",
        conn, parse_dates=["date"]
    ).set_index("date")
    if gci.empty:
        return ""
    fig, ax = plt.subplots(figsize=(9, 3.0))
    _style_axes(ax)
    fig.subplots_adjust(top=0.80, bottom=0.16, left=0.06, right=0.92)
    ax.plot(gci.index, gci["value"], color=OCEAN, lw=1.4, label="Activity Pulse (GCI)")
    ax.axhline(0, color=DOLDRUMS, lw=0.4, ls="--")
    if not wei.empty:
        ax2 = ax.twinx()
        ax2.plot(wei.index, wei["value"], color=DUSK, lw=1.0, alpha=0.8,
                 label="NY Fed WEI (right)")
        ax2.tick_params(colors=DOLDRUMS, labelsize=8)
        for spine in ax2.spines.values():
            spine.set_color(DOLDRUMS); spine.set_linewidth(0.5)
        ax2.spines["right"].set_color(DUSK)
        ax2.tick_params(axis="y", colors=DUSK)
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %y"))
    _stamp(fig, ax,
           "Pillar 3 — Activity Pulse + WEI",
           "GCI (Ocean, left) with NY Fed Weekly Economic Index (Dusk, right).",
           "Lighthouse Macro composites; NY Fed")
    return fig_to_b64(fig)


def chart_housing_vs_10y(conn) -> str:
    hci = pd.read_sql(
        "SELECT date, value FROM lighthouse_indices "
        "WHERE index_id='HCI' AND date >= date('now','-3 year') ORDER BY date",
        conn, parse_dates=["date"]
    ).set_index("date")
    tsy = pd.read_sql(
        "SELECT date, value FROM observations WHERE series_id='DGS10' "
        "AND date >= date('now','-3 year') ORDER BY date",
        conn, parse_dates=["date"]
    ).set_index("date")
    if hci.empty:
        return ""
    fig, ax = plt.subplots(figsize=(9, 3.0))
    _style_axes(ax)
    fig.subplots_adjust(top=0.80, bottom=0.16, left=0.06, right=0.92)
    ax.plot(hci.index, hci["value"], color=OCEAN, lw=1.4, label="Housing Tide")
    ax.axhline(0, color=DOLDRUMS, lw=0.4, ls="--")
    if not tsy.empty:
        ax2 = ax.twinx()
        ax2.plot(tsy.index, tsy["value"], color=DUSK, lw=1.0, alpha=0.8,
                 label="10Y yield")
        ax2.tick_params(colors=DOLDRUMS, labelsize=8)
        for spine in ax2.spines.values():
            spine.set_color(DOLDRUMS); spine.set_linewidth(0.5)
        ax2.spines["right"].set_color(DUSK)
        ax2.tick_params(axis="y", colors=DUSK)
        ax2.set_ylabel("10Y yield, %", color=DUSK, fontsize=8)
    ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 7]))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %y"))
    _stamp(fig, ax,
           "Pillar 4 — Housing Tide vs 10-year",
           "HCI composite (Ocean, left) overlaid with 10Y yield (Dusk, right).",
           "Lighthouse Macro composites; FRED DGS10")
    return fig_to_b64(fig)


def chart_credit_spreads(conn) -> str:
    hy = pd.read_sql(
        "SELECT date, value FROM observations WHERE series_id='BAMLH0A0HYM2' "
        "AND date >= date('now','-3 year') ORDER BY date",
        conn, parse_dates=["date"]
    ).set_index("date")
    ig = pd.read_sql(
        "SELECT date, value FROM observations WHERE series_id='BAMLC0A0CM' "
        "AND date >= date('now','-3 year') ORDER BY date",
        conn, parse_dates=["date"]
    ).set_index("date")
    if hy.empty:
        return ""
    fig, ax = plt.subplots(figsize=(9, 3.0))
    _style_axes(ax)
    fig.subplots_adjust(top=0.80, bottom=0.16, left=0.06, right=0.92)
    ax.plot(hy.index, hy["value"] * 100, color=OCEAN, lw=1.4, label="HY OAS")
    ax.axhline(3.00 * 100, color=DUSK, lw=0.5, ls=":")
    ax.axhline(5.00 * 100, color=PORT, lw=0.5, ls=":")
    ax.text(hy.index[-1], 305, "300 complacent floor", color=DUSK,
            fontsize=7, ha="right", va="bottom")
    ax.text(hy.index[-1], 505, "500 stress threshold", color=PORT,
            fontsize=7, ha="right", va="bottom")
    if not ig.empty:
        ax2 = ax.twinx()
        ax2.plot(ig.index, ig["value"] * 100, color=DOLDRUMS, lw=1.0,
                 alpha=0.7, label="IG OAS (right)")
        ax2.tick_params(colors=DOLDRUMS, labelsize=8)
        for spine in ax2.spines.values():
            spine.set_color(DOLDRUMS); spine.set_linewidth(0.5)
    ax.set_ylabel("HY OAS, bps", color=OCEAN, fontsize=8)
    ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 7]))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %y"))
    _stamp(fig, ax,
           "Pillar 9 — Credit Spreads",
           "ICE BofA HY OAS (Ocean) and IG OAS (Doldrums). Thresholds at 300 bps and 500 bps.",
           "FRED BAMLH0A0HYM2 / BAMLC0A0CM")
    return fig_to_b64(fig)


def chart_plumbing(conn) -> str:
    rrp = pd.read_sql(
        "SELECT date, value FROM observations WHERE series_id='RRPONTSYD' "
        "AND date >= date('now','-3 year') ORDER BY date",
        conn, parse_dates=["date"]
    ).set_index("date")
    walcl = pd.read_sql(
        "SELECT date, value FROM observations WHERE series_id='WALCL' "
        "AND date >= date('now','-3 year') ORDER BY date",
        conn, parse_dates=["date"]
    ).set_index("date")
    if rrp.empty:
        return ""
    fig, ax = plt.subplots(figsize=(9, 3.0))
    _style_axes(ax)
    fig.subplots_adjust(top=0.80, bottom=0.16, left=0.07, right=0.92)
    ax.fill_between(rrp.index, 0, rrp["value"] / 1e3, color=OCEAN, alpha=0.18)
    ax.plot(rrp.index, rrp["value"] / 1e3, color=OCEAN, lw=1.2, label="RRP, $B")
    if not walcl.empty:
        ax2 = ax.twinx()
        ax2.plot(walcl.index, walcl["value"] / 1e6, color=DUSK, lw=1.0,
                 alpha=0.85, label="Fed BS, $T (right)")
        ax2.tick_params(colors=DOLDRUMS, labelsize=8)
        for spine in ax2.spines.values():
            spine.set_color(DOLDRUMS); spine.set_linewidth(0.5)
        ax2.spines["right"].set_color(DUSK)
        ax2.tick_params(axis="y", colors=DUSK)
        ax2.set_ylabel("Fed balance sheet, $T", color=DUSK, fontsize=8)
    ax.set_ylabel("RRP balance, $B", color=OCEAN, fontsize=8)
    ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 7]))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %y"))
    _stamp(fig, ax,
           "Pillar 10 — Plumbing",
           "RRP balance (Ocean fill, left) and Fed balance sheet (Dusk, right).",
           "FRED RRPONTSYD / WALCL")
    return fig_to_b64(fig)


def chart_breadth(conn) -> str:
    series_ids = ["SPX_PCT_ABOVE_20D", "SPX_PCT_ABOVE_50D", "SPX_PCT_ABOVE_200D"]
    palette = [OCEAN, DUSK, SEA]
    fig, ax = plt.subplots(figsize=(9, 3.0))
    _style_axes(ax)
    fig.subplots_adjust(top=0.80, bottom=0.16, left=0.06, right=0.96)
    for sid, color in zip(series_ids, palette):
        df = pd.read_sql(
            "SELECT date, value FROM observations WHERE series_id=? "
            "AND date >= date('now','-2 year') ORDER BY date",
            conn, parse_dates=["date"], params=(sid,)
        ).set_index("date")
        if df.empty:
            continue
        label = sid.replace("SPX_PCT_ABOVE_", "% > ")
        ax.plot(df.index, df["value"], color=color, lw=1.3, label=label, alpha=0.85)
    ax.axhline(80, color=DOLDRUMS, lw=0.4, ls=":")
    ax.axhline(25, color=DOLDRUMS, lw=0.4, ls=":")
    ax.set_ylim(0, 100)
    ax.set_ylabel("% members", color=DOLDRUMS, fontsize=8)
    ax.legend(loc="upper left", frameon=False, fontsize=8.5,
              labelcolor=DOLDRUMS, ncol=3)
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %y"))
    _stamp(fig, ax,
           "Pillar 11 — Market Breadth",
           "% of S&P 500 members above 20d / 50d / 200d MAs. Bands at 25 / 80.",
           "Lighthouse Macro breadth fetcher")
    return fig_to_b64(fig)


def chart_sentiment(conn) -> str:
    aaii = pd.read_sql(
        "SELECT date, value FROM observations WHERE series_id='AAII_Bull_Bear_Spread' "
        "AND date >= date('now','-2 year') ORDER BY date",
        conn, parse_dates=["date"]
    ).set_index("date")
    vix = pd.read_sql(
        "SELECT date, value FROM observations WHERE series_id='VIXCLS' "
        "AND date >= date('now','-2 year') ORDER BY date",
        conn, parse_dates=["date"]
    ).set_index("date")
    if aaii.empty:
        return ""
    fig, ax = plt.subplots(figsize=(9, 3.0))
    _style_axes(ax)
    fig.subplots_adjust(top=0.80, bottom=0.16, left=0.07, right=0.92)
    ax.bar(aaii.index, aaii["value"] * 100, color=OCEAN, alpha=0.55, width=4)
    ax.axhline(30, color=PORT, lw=0.5, ls=":")
    ax.axhline(-20, color=STARBOARD, lw=0.5, ls=":")
    ax.text(aaii.index[-1], 30.5, "+30 euphoria", color=PORT,
            fontsize=7, ha="right", va="bottom")
    ax.text(aaii.index[-1], -19.5, "-20 capitulation", color=STARBOARD,
            fontsize=7, ha="right", va="top")
    ax.set_ylabel("AAII bull-bear, pp", color=OCEAN, fontsize=8)
    if not vix.empty:
        ax2 = ax.twinx()
        ax2.plot(vix.index, vix["value"], color=DUSK, lw=1.1, alpha=0.9)
        ax2.set_ylabel("VIX", color=DUSK, fontsize=8)
        ax2.tick_params(colors=DOLDRUMS, labelsize=8)
        for spine in ax2.spines.values():
            spine.set_color(DOLDRUMS); spine.set_linewidth(0.5)
        ax2.spines["right"].set_color(DUSK)
        ax2.tick_params(axis="y", colors=DUSK)
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %y"))
    _stamp(fig, ax,
           "Pillar 12 — Sentiment",
           "AAII bull-bear spread (Ocean bars) and VIX (Dusk line). 2y view.",
           "AAII; CBOE VIXCLS")
    return fig_to_b64(fig)


def chart_cross_asset() -> str:
    """Cross-asset normalized performance over last 12 months via yfinance."""
    try:
        import yfinance as yf
    except ImportError:
        return ""
    tickers = {"SPY": OCEAN, "QQQ": DUSK, "TLT": SEA, "HYG": VENUS,
               "GLD": STARBOARD, "BTC-USD": PORT}
    fig, ax = plt.subplots(figsize=(9, 3.2))
    _style_axes(ax)
    fig.subplots_adjust(top=0.80, bottom=0.16, left=0.06, right=0.96)
    for t, color in tickers.items():
        try:
            h = yf.Ticker(t).history(period="370d", auto_adjust=False)
            if h.empty:
                continue
            h.index = h.index.tz_localize(None).normalize()
            norm = h["Close"] / h["Close"].iloc[0] * 100
            label = t.replace("-USD", "")
            ax.plot(norm.index, norm.values, color=color, lw=1.3, label=label)
        except Exception:
            continue
    ax.axhline(100, color=DOLDRUMS, lw=0.4, ls="--")
    ax.set_ylabel("Indexed = 100", color=DOLDRUMS, fontsize=8)
    ax.legend(loc="upper left", frameon=False, fontsize=8.5,
              labelcolor=DOLDRUMS, ncol=6)
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %y"))
    _stamp(fig, ax,
           "Cross-Asset, 12 Months",
           "Normalized total return. SPY, QQQ, TLT, HYG, GLD, BTC.",
           "yfinance close prices")
    return fig_to_b64(fig)


# ============================================================================
# DATA PULLS
# ============================================================================

def fetch_state(conn) -> dict:
    """Latest value + 7d/21d delta + status for each macro indicator."""
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
        v = r[1]; v7 = r[4]; v21 = r[5]
        out[r[0]] = {
            "value": v, "status": r[2], "date": r[3],
            "delta_7d": (v - v7) if (v is not None and v7 is not None) else None,
            "delta_21d": (v - v21) if (v is not None and v21 is not None) else None,
        }
    return out


def fetch_markets() -> dict:
    """Cross-asset snapshot via yfinance."""
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
            roc20 = c.pct_change(20)
            z = None
            if len(c) >= 252:
                m = roc20.rolling(252).mean().iloc[-1]
                s = roc20.rolling(252).std().iloc[-1]
                if s and not pd.isna(s):
                    z = float((roc20.iloc[-1] - m) / s)
            out[name] = {
                "price": last, "chg_1d_pct": chg,
                "vs_50": (last / ma50 - 1) * 100 if ma50 else None,
                "vs_200": (last / ma200 - 1) * 100 if ma200 else None,
                "z_roc": z,
                "asof": h.index[-1].date().isoformat(),
            }
        except Exception:
            continue
    return out


# ============================================================================
# RENDER
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
    if d is None:
        return "n/a"
    return f"{d:+.2f}"


def render_brief(state: dict, mkt: dict, charts: dict, run_date: str) -> str:
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M ET")

    def row(code: str, label: str | None = None) -> str:
        d = state.get(code, {})
        v = d.get("value"); st = d.get("status") or "—"
        c = color_for_status(st)
        return (
            f'<tr>'
            f'<td>{label or code}</td>'
            f'<td class="num">{(v if v is not None else 0):+.3f}</td>'
            f'<td class="num delta">{fmt_delta(d.get("delta_7d"))}</td>'
            f'<td class="num delta">{fmt_delta(d.get("delta_21d"))}</td>'
            f'<td><span class="pill" style="background:{c};">{st}</span></td>'
            f'</tr>'
        )

    def master_tile(code: str, name: str, fmt: str) -> str:
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

    def chart_block(key: str, alt: str) -> str:
        b64 = charts.get(key, "")
        if not b64:
            return ""
        return f'<figure class="chart"><img alt="{alt}" src="data:image/png;base64,{b64}"/></figure>'

    def market_row(name: str) -> str:
        m = mkt.get(name, {})
        if not m:
            return f'<tr><td>{name}</td><td colspan="4" class="num">—</td></tr>'
        chg = m.get("chg_1d_pct")
        chg_color = STARBOARD if (chg or 0) >= 0 else PORT
        return (
            f'<tr>'
            f'<td>{name}</td>'
            f'<td class="num">{m.get("price"):.2f}</td>'
            f'<td class="num" style="color:{chg_color};">{chg:+.2f}%</td>'
            f'<td class="num">{m.get("vs_50") or 0:+.1f}%</td>'
            f'<td class="num">{m.get("vs_200") or 0:+.1f}%</td>'
            f'</tr>'
        )

    # Daily note prose with inline links applied
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
<html lang="en">
<head>
<meta charset="UTF-8">
<title>LHM Daily Briefing · {run_date}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@600;700;800&family=Inter:wght@400;500;600&family=Source+Code+Pro:wght@400;600&display=swap" rel="stylesheet">
<style>
  :root{{
    --ocean:{OCEAN}; --dusk:{DUSK}; --sky:{SKY}; --sea:{SEA}; --venus:{VENUS};
    --doldrums:{DOLDRUMS}; --starboard:{STARBOARD}; --port:{PORT}; --fog:{FOG};
    --ink:{INK}; --paper:{PAPER};
  }}
  *{{box-sizing:border-box;}}
  html,body{{background:var(--paper); color:var(--ink); margin:0; padding:0; font-family:'Inter', sans-serif; font-size:14px; line-height:1.6;}}
  .wrap{{max-width:1120px; margin:0 auto; padding:28px 32px 64px;}}
  .accent-bar{{display:flex; height:6px; width:100%; margin-bottom:18px;}}
  .accent-bar .ocean{{flex:2; background:var(--ocean);}}
  .accent-bar .dusk{{flex:1; background:var(--dusk);}}
  .header{{display:flex; justify-content:space-between; align-items:flex-end; flex-wrap:wrap; gap:12px;}}
  .kicker{{font-family:'Source Code Pro', monospace; font-size:11px; letter-spacing:0.14em; color:var(--ocean); text-transform:uppercase; font-weight:600;}}
  h1{{font-family:'Montserrat', sans-serif; font-weight:800; font-size:34px; letter-spacing:-0.015em; margin:6px 0 0;}}
  .stamps{{text-align:right; font-family:'Source Code Pro', monospace; font-size:11px; color:var(--doldrums);}}
  .stamps strong{{color:var(--ink); font-size:13px; font-weight:600;}}
  h2{{font-family:'Montserrat', sans-serif; font-weight:700; font-size:18px; margin:36px 0 8px; padding-bottom:6px; border-bottom:1px solid var(--fog); letter-spacing:-0.005em;}}
  h3{{font-family:'Montserrat', sans-serif; font-weight:600; font-size:12px; margin:14px 0 6px; color:var(--ocean); text-transform:uppercase; letter-spacing:0.06em;}}
  p{{margin:0 0 12px;}}
  a{{color:var(--ocean); text-decoration:none;}}
  a:hover{{text-decoration:underline;}}
  .master-row{{display:grid; grid-template-columns:repeat(4, 1fr); gap:12px; margin:14px 0 20px;}}
  .master-tile{{border:1px solid var(--fog); border-radius:10px; padding:14px 16px; background:var(--paper);}}
  .master-tile-name{{font-family:'Montserrat', sans-serif; font-weight:700; font-size:12px; text-transform:uppercase; letter-spacing:0.05em; color:var(--doldrums);}}
  .master-tile-value{{font-family:'Source Code Pro', monospace; font-weight:600; font-size:30px; margin:6px 0 8px; letter-spacing:-0.01em;}}
  .master-tile-status{{display:inline-block; padding:3px 10px; border-radius:11px; font-family:'Source Code Pro', monospace; font-size:11px; font-weight:600; color:#fff; letter-spacing:0.04em;}}
  table{{width:100%; border-collapse:collapse; font-size:12.5px; margin:8px 0 8px;}}
  th,td{{padding:6px 9px; text-align:left; border-bottom:1px solid var(--fog); vertical-align:top;}}
  th{{font-family:'Source Code Pro', monospace; font-size:10.5px; color:var(--doldrums); text-transform:uppercase; letter-spacing:0.05em; border-bottom:1px solid var(--doldrums);}}
  td.num{{font-family:'Source Code Pro', monospace; text-align:right;}}
  td.delta{{color:var(--doldrums); font-size:11.5px;}}
  .pill{{display:inline-block; padding:2px 9px; border-radius:11px; font-family:'Source Code Pro', monospace; font-size:10.5px; font-weight:600; color:#fff; letter-spacing:0.04em; white-space:nowrap;}}
  figure.chart{{margin:14px 0 20px; border:1px solid var(--fog); border-radius:10px; overflow:hidden; background:var(--paper);}}
  figure.chart img{{display:block; width:100%; height:auto;}}
  .grid-2col{{display:grid; grid-template-columns:1fr 1fr; gap:12px;}}
  .footer{{margin-top:48px; padding-top:14px; border-top:1px solid var(--fog); color:var(--doldrums); font-size:11px; font-family:'Source Code Pro', monospace; display:flex; justify-content:space-between;}}
  .footer a{{color:var(--ocean);}}
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

  {chart_block("mri", "Macro Risk Index 3y history")}

  <h2>The Diagnostic Dozen</h2>
  {chart_block("heatmap", "12-pillar heatmap")}

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

  {chart_block("labor", "Labor stack: LFI / LPI / LDI")}
  {chart_block("pci", "Inflation Heat 3y")}
  {chart_block("growth", "Activity Pulse vs WEI")}
  {chart_block("housing", "Housing Tide vs 10Y yield")}

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

  {chart_block("credit", "Credit spreads HY / IG")}
  {chart_block("plumbing", "Plumbing — RRP + Fed BS")}

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

  {chart_block("breadth", "SPX breadth %s above MAs")}
  {chart_block("sentiment", "AAII bull-bear + VIX")}

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

  {chart_block("crossasset", "Cross-asset 12-month normalized")}

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

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--no-open", action="store_true")
    args = p.parse_args()

    conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    try:
        state = fetch_state(conn)
        run_date = max((s["date"] for s in state.values() if s.get("date")), default="—")
        mkt = fetch_markets()
        charts = {
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
