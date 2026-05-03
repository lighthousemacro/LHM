#!/usr/bin/env python3
"""
LIGHTHOUSE MACRO - MORNING BRIEF (v3.0)
========================================
Charts-first morning briefing. Apr 29 layout, dynamic data.

Renders 10 base64-inlined charts with brand styling, computes hero stats
and narrative summary from current DB values + LHM threshold dictionary.
Writes timestamped archive under Outputs/morning_brief/YYYY-MM-DD/ and a
copy at ~/Desktop/LHM_Morning_Brief.html.

Usage:
    python morning_brief.py
    python morning_brief.py --no-charts   # skip chart re-render (use last batch)
    python morning_brief.py --stdout      # print HTML to stdout instead of writing
"""
from __future__ import annotations

import argparse
import base64
import html
import json
import os
import sqlite3
import sys
import traceback
from datetime import date, datetime
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

LHM_ROOT = Path("/Users/bob/LHM")
sys.path.insert(0, str(LHM_ROOT / "Scripts" / "chart_generation"))

from lhm_chart_template import (  # noqa: E402
    COLORS,
    add_last_value_label,
    add_recessions,
    brand_fig,
    legend_style,
    new_fig,
    save_fig,
    set_theme,
    set_xlim_to_data,
    style_ax,
    style_dual_ax,
)

DB_PATH = LHM_ROOT / "Data" / "databases" / "Lighthouse_Master.db"
DESKTOP_PATH = Path.home() / "Desktop" / "LHM_Morning_Brief.html"
ARCHIVE_ROOT = LHM_ROOT / "Outputs" / "morning_brief"
LOG_PATH = LHM_ROOT / "logs" / "morning_brief.log"

set_theme("white")


# ============================================================
# DATA ACCESS
# ============================================================

def _conn() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH, timeout=30)


def pull(conn: sqlite3.Connection, series_id: str, start: str | None = None) -> pd.DataFrame:
    q = "SELECT date, value FROM observations WHERE series_id = ?"
    params: list = [series_id]
    if start:
        q += " AND date >= ?"
        params.append(start)
    q += " ORDER BY date"
    df = pd.read_sql(q, conn, params=params)
    df["date"] = pd.to_datetime(df["date"])
    df = df.dropna(subset=["value"]).sort_values("date").reset_index(drop=True)
    return df


def latest(conn: sqlite3.Connection, series_id: str):
    df = pull(conn, series_id)
    if df.empty:
        return None, None
    row = df.iloc[-1]
    return row["date"], float(row["value"])


def n_back(conn: sqlite3.Connection, series_id: str, n: int):
    df = pull(conn, series_id)
    if len(df) <= n:
        return None
    return float(df.iloc[-1 - n]["value"])


# ============================================================
# CHART RENDERERS
# Each returns the path to the saved PNG and a dict of values used
# in caption / narrative generation.
# ============================================================

def chart_01_hy_oas(conn, out_dir: Path) -> dict:
    df = pull(conn, "BAMLH0A0HYM2", "2018-01-01")
    bps = df["value"] * 100
    fig, ax = new_fig(figsize=(14, 7.5))
    ax.plot(df["date"], bps, color=COLORS["ocean"], linewidth=2.6)
    ax.axhline(300, color=COLORS["venus"], linewidth=1.4, linestyle="--", alpha=0.85)
    ax.text(df["date"].iloc[10], 308, "300 bps  complacency line",
            color=COLORS["venus"], fontsize=10, style="italic")
    last_val = float(bps.iloc[-1])
    ax.scatter([df["date"].iloc[-1]], [last_val], color=COLORS["dusk"], s=70, zorder=5)
    add_recessions(ax)
    style_ax(ax)
    ax.set_ylabel("OAS (bps)", color=COLORS["doldrums"])
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.0f}"))
    add_last_value_label(ax, df.set_index("date")["value"] * 100, COLORS["ocean"], fmt="{:.0f}", side="right")
    set_xlim_to_data(ax, df.set_index("date").index)
    brand_fig(fig,
              "HY OAS",
              subtitle="ICE BofA US High Yield Index, option-adjusted spread",
              source="ICE BofA via FRED", data_date=df["date"].iloc[-1])
    out = out_dir / "chart_01_hy_oas.png"
    save_fig(fig, str(out))
    plt.close(fig)
    bps_4w = float(bps.iloc[-21]) if len(bps) > 21 else last_val
    return {"path": out.name, "value": last_val, "delta_4w": last_val - bps_4w,
            "asof": df["date"].iloc[-1]}


def chart_02_aaii(conn, out_dir: Path) -> dict:
    df = pull(conn, "AAII_Bull_Bear_Spread", "2018-01-01")
    df["pct"] = df["value"] * 100
    fig, ax = new_fig(figsize=(14, 7.5))
    colors = [COLORS["starboard"] if v > 0 else COLORS["port"] for v in df["pct"]]
    ax.bar(df["date"], df["pct"], color=colors, alpha=0.55, width=4.0)
    ax.plot(df["date"], df["pct"].rolling(8).mean(),
            color=COLORS["ocean"], linewidth=2.4, label="8-week MA")
    ax.axhline(30, color=COLORS["venus"], linewidth=1.2, linestyle="--", alpha=0.7)
    ax.axhline(-20, color=COLORS["venus"], linewidth=1.2, linestyle="--", alpha=0.7)
    ax.axhline(0, color=COLORS["fog"], linewidth=1.0, linestyle="-")
    ax.text(df["date"].iloc[5], 32, "Euphoria  +30%", color=COLORS["venus"], fontsize=10, style="italic")
    ax.text(df["date"].iloc[5], -23, "Capitulation  -20%", color=COLORS["venus"], fontsize=10, style="italic")
    style_ax(ax)
    ax.set_ylabel("Bull minus bear (%)", color=COLORS["doldrums"])
    set_xlim_to_data(ax, df.set_index("date").index)
    legend_style()
    last = df.iloc[-1]
    val = float(last["pct"])
    val_5w = float(df.iloc[-6]["pct"]) if len(df) > 6 else val
    brand_fig(fig,
              "AAII Bull-Bear Spread",
              subtitle="AAII Investor Sentiment Survey, bull minus bear spread",
              source="AAII", data_date=last["date"])
    out = out_dir / "chart_02_aaii.png"
    save_fig(fig, str(out))
    plt.close(fig)
    return {"path": out.name, "value": val, "delta_5w": val - val_5w, "asof": last["date"]}


def chart_03_quits(conn, out_dir: Path) -> dict:
    df = pull(conn, "JTSQUR", "2010-01-01")
    fig, ax = new_fig(figsize=(14, 7.5))
    ax.plot(df["date"], df["value"], color=COLORS["ocean"], linewidth=2.6)
    ax.fill_between(df["date"], df["value"], 0, color=COLORS["ocean"], alpha=0.10)
    ax.axhline(2.0, color=COLORS["venus"], linewidth=1.4, linestyle="--", alpha=0.85)
    ax.text(df["date"].iloc[10], 2.04, "2.0%  pre-recessionary threshold",
            color=COLORS["venus"], fontsize=10, style="italic")
    add_recessions(ax)
    style_ax(ax)
    ax.set_ylabel("Quits rate (%)", color=COLORS["doldrums"])
    ax.set_ylim(1.0, 3.2)
    add_last_value_label(ax, df.set_index("date")["value"], COLORS["ocean"], fmt="{:.1f}%")
    set_xlim_to_data(ax, df.set_index("date").index)
    last = df.iloc[-1]
    brand_fig(fig,
              "Quits Rate",
              subtitle="JOLTS quits rate, total nonfarm",
              source="BLS / JOLTS", data_date=last["date"])
    out = out_dir / "chart_03_quits.png"
    save_fig(fig, str(out))
    plt.close(fig)
    return {"path": out.name, "value": float(last["value"]), "asof": last["date"]}


def chart_04_breakevens(conn, out_dir: Path) -> dict:
    df = pull(conn, "T5YIFR", "2022-01-01")
    fig, ax = new_fig(figsize=(14, 7.5))
    ax.plot(df["date"], df["value"], color=COLORS["ocean"], linewidth=2.6,
            label="5Y5Y forward inflation")
    ax.axhline(2.0, color=COLORS["venus"], linewidth=1.4, linestyle="--", alpha=0.85)
    ax.text(df["date"].iloc[10], 2.02, "Fed's 2.0% target",
            color=COLORS["venus"], fontsize=10, style="italic")
    last = df.iloc[-1]
    style_ax(ax)
    ax.set_ylabel("Implied inflation (%)", color=COLORS["doldrums"])
    add_last_value_label(ax, df.set_index("date")["value"], COLORS["ocean"], fmt="{:.2f}%")
    set_xlim_to_data(ax, df.set_index("date").index)
    legend_style()
    val = float(last["value"])
    val_1m = float(df.iloc[-22]["value"]) if len(df) > 22 else val
    brand_fig(fig,
              "5Y5Y Forward Inflation",
              subtitle="5-Year, 5-Year forward inflation expectation rate",
              source="FRED", data_date=last["date"])
    out = out_dir / "chart_04_breakevens.png"
    save_fig(fig, str(out))
    plt.close(fig)
    return {"path": out.name, "value": val, "delta_1m_bps": (val - val_1m) * 100, "asof": last["date"]}


def chart_05_rrp(conn, out_dir: Path) -> dict:
    df = pull(conn, "RRPONTSYD", "2021-01-01")
    fig, ax = new_fig(figsize=(14, 7.5))
    ax.plot(df["date"], df["value"], color=COLORS["ocean"], linewidth=2.6)
    ax.fill_between(df["date"], df["value"], 0, color=COLORS["ocean"], alpha=0.18)
    ax.axhline(200, color=COLORS["venus"], linewidth=1.4, linestyle="--", alpha=0.85)
    ax.text(df["date"].iloc[5], 215, "$200B  buffer-exhaustion line",
            color=COLORS["venus"], fontsize=10, style="italic")
    style_ax(ax)
    ax.set_ylabel("RRP usage ($B)", color=COLORS["doldrums"])
    add_last_value_label(ax, df.set_index("date")["value"], COLORS["ocean"], fmt="${:.0f}B")
    set_xlim_to_data(ax, df.set_index("date").index)
    last = df.iloc[-1]
    brand_fig(fig,
              "Overnight Reverse Repo",
              subtitle="ON RRP usage, daily",
              source="NY Fed via FRED", data_date=last["date"])
    out = out_dir / "chart_05_rrp.png"
    save_fig(fig, str(out))
    plt.close(fig)
    peak = float(df["value"].max())
    return {"path": out.name, "value": float(last["value"]), "peak": peak, "asof": last["date"]}


def chart_06_breadth(conn, out_dir: Path) -> dict:
    spx = pull(conn, "SPX_Close", "2024-06-01")
    pct50 = pull(conn, "SPX_PCT_ABOVE_50D", "2024-06-01")
    fig, ax1 = new_fig(figsize=(14, 7.5))
    ax2 = ax1.twinx()
    l1 = ax1.plot(spx["date"], spx["value"], color=COLORS["ocean"], linewidth=2.4, label="S&P 500")
    l2 = ax2.plot(pct50["date"], pct50["value"], color=COLORS["dusk"], linewidth=2.0,
                  label="% S&P 500 above 50-day MA")
    ax2.axhline(50, color=COLORS["fog"], linewidth=1.0, linestyle="--")
    style_dual_ax(ax1, ax2, COLORS["ocean"], COLORS["dusk"])
    ax1.set_ylabel("S&P 500 level", color=COLORS["ocean"])
    ax2.set_ylabel("% above 50-day MA", color=COLORS["dusk"])
    set_xlim_to_data(ax1, spx.set_index("date").index, pct50.set_index("date").index)
    add_last_value_label(ax1, spx.set_index("date")["value"], COLORS["ocean"], fmt="{:.0f}", side="left")
    add_last_value_label(ax2, pct50.set_index("date")["value"], COLORS["dusk"], fmt="{:.0f}%", side="right")
    last = spx.iloc[-1]
    lines = l1 + l2
    ax1.legend(lines, [l.get_label() for l in lines], loc="upper left",
               frameon=True, facecolor="white", edgecolor=COLORS["fog"])
    brand_fig(fig,
              "S&P 500 vs Breadth",
              subtitle="S&P 500 close vs % of constituents above 50-day MA",
              source="Yahoo / Lighthouse Macro", data_date=last["date"])
    out = out_dir / "chart_06_breadth.png"
    save_fig(fig, str(out))
    plt.close(fig)
    return {"path": out.name, "spx": float(last["value"]),
            "pct50": float(pct50.iloc[-1]["value"]),
            "asof": last["date"]}


def chart_07_clg(conn, out_dir: Path) -> dict:
    hy = pull(conn, "BAMLH0A0HYM2", "2010-01-01")
    quits = pull(conn, "JTSQUR", "2010-01-01")
    hy_m = hy.set_index("date").resample("MS").last()["value"].dropna()
    quits_m = quits.set_index("date").resample("MS").last()["value"].dropna()
    df = pd.DataFrame({"hy": hy_m, "quits": quits_m}).dropna()
    df["hy_z"] = (df["hy"] - df["hy"].rolling(60).mean()) / df["hy"].rolling(60).std()
    df["quits_z"] = (df["quits"] - df["quits"].rolling(60).mean()) / df["quits"].rolling(60).std()
    df["clg"] = df["hy_z"] + df["quits_z"]
    df = df.dropna()
    fig, ax = new_fig(figsize=(14, 7.5))
    ax.plot(df.index, df["clg"], color=COLORS["ocean"], linewidth=2.4)
    ax.fill_between(df.index, df["clg"], 0, where=(df["clg"] > 0),
                    color=COLORS["sea"], alpha=0.25, label="Credit aligned with labor")
    ax.fill_between(df.index, df["clg"], 0, where=(df["clg"] <= 0),
                    color=COLORS["venus"], alpha=0.20, label="Credit too tight or labor too soft")
    ax.axhline(0, color=COLORS["fog"], linewidth=1.0)
    ax.axhline(-1.0, color=COLORS["venus"], linewidth=1.2, linestyle="--", alpha=0.7)
    ax.text(df.index[5], -1.07, "CLG  -1.0  warning line",
            color=COLORS["venus"], fontsize=10, style="italic")
    add_recessions(ax)
    style_ax(ax)
    ax.set_ylabel("CLG (z-score units)", color=COLORS["doldrums"])
    set_xlim_to_data(ax, df.index)
    legend_style()
    last_date = df.index[-1]
    brand_fig(fig,
              "Credit-Labor Gap",
              subtitle="z(HY OAS) + z(Quits Rate). Negative = credit/labor disagreement",
              source="FRED / BLS (LHM composite)", data_date=last_date)
    out = out_dir / "chart_07_clg.png"
    save_fig(fig, str(out))
    plt.close(fig)
    return {"path": out.name, "value": float(df["clg"].iloc[-1]), "asof": last_date}


def chart_08_curve(conn, out_dir: Path) -> dict:
    df = pull(conn, "T10Y2Y", "2018-01-01")
    df["bps"] = df["value"] * 100
    fig, ax = new_fig(figsize=(14, 7.5))
    ax.plot(df["date"], df["bps"], color=COLORS["ocean"], linewidth=2.4)
    ax.fill_between(df["date"], df["bps"], 0, where=(df["bps"] >= 0),
                    color=COLORS["sea"], alpha=0.18)
    ax.fill_between(df["date"], df["bps"], 0, where=(df["bps"] < 0),
                    color=COLORS["venus"], alpha=0.18)
    ax.axhline(0, color=COLORS["fog"], linewidth=1.0)
    add_recessions(ax)
    style_ax(ax)
    ax.set_ylabel("10Y-2Y spread (bps)", color=COLORS["doldrums"])
    add_last_value_label(ax, df.set_index("date")["bps"], COLORS["ocean"], fmt="{:.0f} bps")
    set_xlim_to_data(ax, df.set_index("date").index)
    last = df.iloc[-1]
    brand_fig(fig,
              "2s10s Spread",
              subtitle="10-Year minus 2-Year Treasury yield",
              source="FRED", data_date=last["date"])
    out = out_dir / "chart_08_curve.png"
    save_fig(fig, str(out))
    plt.close(fig)
    return {"path": out.name, "value": float(last["bps"]), "asof": last["date"]}


def chart_09_dollar(conn, out_dir: Path) -> dict:
    df = pull(conn, "DTWEXBGS", "2022-01-01")
    df["ma50"] = df["value"].rolling(50).mean()
    df["ma200"] = df["value"].rolling(200).mean()
    fig, ax = new_fig(figsize=(14, 7.5))
    ax.plot(df["date"], df["value"], color=COLORS["ocean"], linewidth=2.4, label="Trade-weighted dollar")
    ax.plot(df["date"], df["ma50"], color=COLORS["dusk"], linewidth=1.5, alpha=0.85, label="50-day MA")
    ax.plot(df["date"], df["ma200"], color=COLORS["sky"], linewidth=1.3, alpha=0.85, label="200-day MA")
    style_ax(ax)
    ax.set_ylabel("Index level", color=COLORS["doldrums"])
    add_last_value_label(ax, df.set_index("date")["value"], COLORS["ocean"], fmt="{:.1f}")
    set_xlim_to_data(ax, df.set_index("date").index)
    legend_style()
    last = df.iloc[-1]
    val = float(last["value"])
    ma50 = float(df["ma50"].iloc[-1])
    ma200 = float(df["ma200"].iloc[-1])
    brand_fig(fig,
              "Trade-Weighted Dollar",
              subtitle="Nominal broad U.S. dollar index, daily",
              source="Federal Reserve / FRED", data_date=last["date"])
    out = out_dir / "chart_09_dollar.png"
    save_fig(fig, str(out))
    plt.close(fig)
    return {"path": out.name, "value": val, "ma50": ma50, "ma200": ma200,
            "below_ma50": val < ma50, "below_ma200": val < ma200, "asof": last["date"]}


def chart_10_crypto_vs_spx(conn, out_dir: Path) -> dict:
    btc = pull(conn, "CRYPTO_BTC_PRICE", "2026-02-01")
    eth = pull(conn, "CRYPTO_ETH_PRICE", "2026-02-01")
    spx = pull(conn, "SPX_Close", "2026-02-01")
    btc = btc[(btc["value"] > 1000) & (btc["value"] < 1_000_000)].reset_index(drop=True)
    eth = eth[(eth["value"] > 100) & (eth["value"] < 100_000)].reset_index(drop=True)

    def rebase(df):
        df = df.copy()
        df["v"] = df["value"] / df["value"].iloc[0] * 100
        return df

    btc_r, eth_r, spx_r = rebase(btc), rebase(eth), rebase(spx)
    fig, ax = new_fig(figsize=(14, 7.5))
    ax.plot(btc_r["date"], btc_r["v"], color=COLORS["ocean"], linewidth=2.4, label="BTC")
    ax.plot(eth_r["date"], eth_r["v"], color=COLORS["dusk"], linewidth=2.0, label="ETH")
    ax.plot(spx_r["date"], spx_r["v"], color=COLORS["sea"], linewidth=2.0, label="S&P 500")
    ax.axhline(100, color=COLORS["fog"], linewidth=1.0, linestyle="--")
    style_ax(ax)
    ax.set_ylabel("Indexed (Feb 1, 2026 = 100)", color=COLORS["doldrums"])
    set_xlim_to_data(ax, btc_r.set_index("date").index, eth_r.set_index("date").index,
                     spx_r.set_index("date").index)
    legend_style()
    last_date = max(btc_r["date"].iloc[-1], spx_r["date"].iloc[-1])
    brand_fig(fig,
              "Risk Assets Rebased",
              subtitle="BTC, ETH, S&P 500 indexed to February 1, 2026",
              source="CoinGecko / Yahoo", data_date=last_date)
    out = out_dir / "chart_10_crypto_vs_spx.png"
    save_fig(fig, str(out))
    plt.close(fig)
    return {"path": out.name,
            "btc": float(btc_r["v"].iloc[-1]) - 100,
            "eth": float(eth_r["v"].iloc[-1]) - 100,
            "spx": float(spx_r["v"].iloc[-1]) - 100,
            "asof": last_date}


CHART_FUNCS = [
    ("hy_oas", chart_01_hy_oas),
    ("aaii", chart_02_aaii),
    ("quits", chart_03_quits),
    ("breakevens", chart_04_breakevens),
    ("rrp", chart_05_rrp),
    ("breadth", chart_06_breadth),
    ("clg", chart_07_clg),
    ("curve", chart_08_curve),
    ("dollar", chart_09_dollar),
    ("crypto_vs_spx", chart_10_crypto_vs_spx),
]


# ============================================================
# CAPTION + NARRATIVE
# Driven entirely off the values returned by the chart funcs.
# No invented copy.
# ============================================================

def fmt_caption(key: str, v: dict) -> tuple[str, str]:
    """Return (one-line caption, why-it-matters paragraph) for a chart."""
    if key == "hy_oas":
        delta = v["delta_4w"]
        dirn = "tighter" if delta < 0 else "wider"
        comp = "below" if v["value"] < 300 else "above"
        cap = (f"HY OAS at {v['value']:.0f} bps. {comp.capitalize()} the 300 bps "
               f"complacency line. {abs(delta):.0f} bps {dirn} over 4 weeks.")
        why = ("Spreads are pricing the soft landing. Below 300 bps is the LHM "
               "complacency threshold. Watch for repricing on any catalyst that "
               "challenges that view.")
        return cap, why

    if key == "aaii":
        delta = v["delta_5w"]
        cap = (f"AAII Bull-Bear at {v['value']:+.1f}%. "
               f"{abs(delta):.1f} pp swing over 5 weeks.")
        if v["value"] > 30:
            why = ("Above the +30% euphoria line. Contrarian sell signal per the "
                   "SPI threshold framework.")
        elif v["value"] < -20:
            why = ("Below the -20% capitulation line. Contrarian buy zone per the "
                   "SPI threshold framework.")
        else:
            why = ("Inside the neutral band. We watch the rate of change as much as "
                   "the level.")
        return cap, why

    if key == "quits":
        below = v["value"] < 2.0
        cap = (f"Quits rate at {v['value']:.1f}%. "
               f"{'Below' if below else 'Above'} the 2.0% pre-recessionary line.")
        why = ("Workers do not quit when they doubt the next job. Sub-2.0% prints "
               "are the labor market's truth serum, and they show up in LFI before "
               "the headline payroll number turns.")
        return cap, why

    if key == "breakevens":
        delta_bps = v["delta_1m_bps"]
        dirn = "higher" if delta_bps > 0 else "lower"
        cap = (f"5Y5Y forward inflation at {v['value']:.2f}%. "
               f"{abs(delta_bps):.0f} bps {dirn} over the past month.")
        why = ("The market's read on long-run inflation. Sustained moves here "
               "pressure term premium and the long end of the curve.")
        return cap, why

    if key == "rrp":
        cap = f"RRP usage at ${v['value']:.0f}B. Down from ${v['peak']/1000:.1f}T at peak."
        why = ("From here, any liquidity drain hits reserves directly. The buffer "
               "Pillar 10 has tracked for years is effectively gone.")
        return cap, why

    if key == "breadth":
        cap = (f"S&P 500 at {v['spx']:.0f}. "
               f"{v['pct50']:.0f}% of constituents above their 50-day MA.")
        if v["pct50"] < 50:
            why = ("Index higher, breadth lower. Generals without soldiers. "
                   "MSI decays in the background while the headline holds.")
        else:
            why = ("Breadth is participating. The risk-on tape is supported "
                   "by more than the top of the index.")
        return cap, why

    if key == "clg":
        cap = f"Credit-Labor Gap at {v['value']:+.2f} (z-score units)."
        if v["value"] < -1.0:
            why = ("Past the -1.0 warning line. Spreads are pricing one labor "
                   "market and quits are telling another. The chain runs labor "
                   "first, credit second, equity third.")
        elif v["value"] < 0:
            why = ("Negative but inside the warning line. Watch for further drift; "
                   "credit and labor are starting to disagree.")
        else:
            why = ("Credit and labor are aligned. The CLG is not flagging.")
        return cap, why

    if key == "curve":
        cap = f"2s10s spread at {v['value']:+.0f} bps."
        if v["value"] > 0:
            why = ("Steepening regime. The long end demanding term premium for "
                   "fiscal-dominance and inflation risk is consistent with our "
                   "structural call.")
        else:
            why = ("Inverted. The classic recession lead, though duration of "
                   "inversion matters more than the level.")
        return cap, why

    if key == "dollar":
        rel = []
        if v["below_ma50"]:
            rel.append("below 50-day")
        if v["below_ma200"]:
            rel.append("below 200-day")
        rel_str = ", ".join(rel) if rel else "above both moving averages"
        cap = f"Trade-weighted dollar at {v['value']:.1f}. {rel_str}."
        why = ("Net liquidity expanding plus dollar weakening is the setup the "
               "CLI work points to for risk assets. The dollar is the regime "
               "switch.")
        return cap, why

    if key == "crypto_vs_spx":
        cap = (f"Since Feb 1: BTC {v['btc']:+.1f}%, "
               f"ETH {v['eth']:+.1f}%, S&P 500 {v['spx']:+.1f}%.")
        why = ("Risk-on showing up unevenly. Ratio between equities and crypto "
               "is the cleanest read on whether the dollar move has translated "
               "across the risk spectrum.")
        return cap, why

    return "", ""


# ============================================================
# HERO STATS
# ============================================================

def compute_hero(conn) -> dict:
    """Pull current MRI / regime / warning level for the hero block."""
    out = {"mri": None, "regime": None, "rec_prob": None, "warning_level": None,
           "alloc_mult": None, "alloc_label": None}
    try:
        d, mri = latest(conn, "MRI")
        out["mri"] = mri
        if mri is not None:
            if mri < -0.5:
                out["regime"], out["alloc_label"], out["alloc_mult"] = "LOW RISK", "AGGRESSIVE", 1.2
            elif mri < 0.5:
                out["regime"], out["alloc_label"], out["alloc_mult"] = "MID-CYCLE", "NEUTRAL", 1.0
            elif mri < 1.0:
                out["regime"], out["alloc_label"], out["alloc_mult"] = "ELEVATED", "DEFENSIVE", 0.6
            elif mri < 1.5:
                out["regime"], out["alloc_label"], out["alloc_mult"] = "HIGH RISK", "PROTECTIVE", 0.3
            else:
                out["regime"], out["alloc_label"], out["alloc_mult"] = "CRISIS", "CAPITAL PRESERVATION", 0.0
    except Exception:
        pass
    try:
        _, rp = latest(conn, "REC_PROB")
        out["rec_prob"] = rp
    except Exception:
        pass
    return out


# ============================================================
# HTML BUILD
# ============================================================

def b64(path: Path) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")


def build_html(brief_date: date, charts: list[tuple[str, dict]],
               out_dir: Path, hero: dict) -> str:
    chart_blocks = []
    for i, (key, v) in enumerate(charts, 1):
        img_path = out_dir / v["path"]
        if not img_path.exists():
            continue
        cap, why = fmt_caption(key, v)
        data = b64(img_path)
        chart_blocks.append(f"""
    <div style="margin: 32px 0; padding: 0;">
      <img src="data:image/png;base64,{data}" alt="Chart {i}"
           style="width: 100%; max-width: 900px; height: auto; display: block; border: 0;" />
      <div style="font-family: Georgia, serif; font-size: 13px; color: #555; margin-top: 8px; line-height: 1.5;">
        <strong style="color: #2389BB;">Figure {i}.</strong> {html.escape(cap)}
      </div>
      <div style="font-family: -apple-system, Helvetica, Arial, sans-serif; font-size: 14px; color: #1a1a1a; margin-top: 8px; line-height: 1.55;">
        {html.escape(why)}
      </div>
    </div>
""")

    summary_lines = []
    cmap = {k: v for k, v in charts}
    if "hy_oas" in cmap:
        summary_lines.append(f"HY OAS at {cmap['hy_oas']['value']:.0f} bps "
                             f"({'below' if cmap['hy_oas']['value'] < 300 else 'above'} the 300 bps complacency line).")
    if "aaii" in cmap:
        summary_lines.append(f"AAII Bull-Bear at {cmap['aaii']['value']:+.1f}%.")
    if "quits" in cmap:
        summary_lines.append(f"Quits at {cmap['quits']['value']:.1f}%.")
    if "rrp" in cmap:
        summary_lines.append(f"RRP at ${cmap['rrp']['value']:.0f}B.")
    if "clg" in cmap:
        summary_lines.append(f"Credit-Labor Gap at {cmap['clg']['value']:+.2f}.")
    summary = " ".join(summary_lines)

    hero_html = ""
    if hero.get("mri") is not None:
        mri_val = hero["mri"]
        regime = hero.get("regime") or ""
        rec = f"{hero['rec_prob']*100:.1f}%" if hero.get("rec_prob") is not None else "n/a"
        alloc = hero.get("alloc_label") or ""
        mult = f"{hero['alloc_mult']:.1f}x" if hero.get("alloc_mult") is not None else "n/a"
        hero_html = f"""
    <table cellpadding="0" cellspacing="0" border="0" width="100%"
           style="margin: 14px 0 8px 0; border-collapse: collapse;">
      <tr>
        <td style="padding: 10px 14px; background: #2389BB; color: #fff; width: 25%;">
          <div style="font-size: 10px; letter-spacing: 0.08em; opacity: 0.85;">MACRO RISK INDEX</div>
          <div style="font-size: 22px; font-weight: 700; margin-top: 2px;">{mri_val:+.2f}</div>
          <div style="font-size: 11px; margin-top: 2px;">{html.escape(regime)}</div>
        </td>
        <td style="padding: 10px 14px; background: #f0f6fa; width: 25%; border-right: 1px solid #fff;">
          <div style="font-size: 10px; letter-spacing: 0.08em; color: #555;">RECESSION PROBABILITY</div>
          <div style="font-size: 22px; font-weight: 700; color: #2389BB; margin-top: 2px;">{rec}</div>
          <div style="font-size: 11px; color: #555; margin-top: 2px;">6-12 month forward</div>
        </td>
        <td style="padding: 10px 14px; background: #f0f6fa; width: 25%; border-right: 1px solid #fff;">
          <div style="font-size: 10px; letter-spacing: 0.08em; color: #555;">REGIME</div>
          <div style="font-size: 22px; font-weight: 700; color: #2389BB; margin-top: 2px;">{html.escape(regime or "N/A")}</div>
          <div style="font-size: 11px; color: #555; margin-top: 2px;">MRI-driven</div>
        </td>
        <td style="padding: 10px 14px; background: #f0f6fa; width: 25%;">
          <div style="font-size: 10px; letter-spacing: 0.08em; color: #555;">ALLOCATION MULTIPLIER</div>
          <div style="font-size: 22px; font-weight: 700; color: #2389BB; margin-top: 2px;">{mult}</div>
          <div style="font-size: 11px; color: #555; margin-top: 2px;">{html.escape(alloc)}</div>
        </td>
      </tr>
    </table>
"""

    title_str = brief_date.strftime("%B %-d, %Y")
    return f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>LHM Morning Brief — {title_str}</title>
</head>
<body style="margin: 0; padding: 0; background: #f8f8f8; font-family: -apple-system, Helvetica, Arial, sans-serif; color: #1a1a1a;">
  <div style="max-width: 920px; margin: 0 auto; background: #ffffff; padding: 32px 28px;">
    <div style="border-bottom: 4px solid #2389BB; padding-bottom: 14px; margin-bottom: 22px;">
      <div style="font-size: 13px; color: #2389BB; font-weight: 700; letter-spacing: 0.08em;">LIGHTHOUSE MACRO &nbsp;|&nbsp; MORNING BRIEF</div>
      <div style="font-size: 22px; font-weight: 700; margin-top: 6px;">{html.escape(title_str)}</div>
      <div style="font-size: 13px; color: #555; margin-top: 4px;">Ten charts. Live readings from the Lighthouse Master DB.</div>
    </div>

    {hero_html}

    <div style="font-size: 15px; line-height: 1.6; color: #1a1a1a; margin-top: 18px; margin-bottom: 18px;">
      {html.escape(summary)}
    </div>

    {''.join(chart_blocks)}

    <div style="margin-top: 40px; padding-top: 18px; border-top: 1px solid #D1D1D1; font-size: 12px; color: #555; line-height: 1.55;">
      <div style="color: #2389BB; font-weight: 700; font-style: italic;">MACRO, ILLUMINATED.</div>
      <div style="margin-top: 6px;">Bob Sheehan, CFA, CMT &middot; Founder &amp; CIO &middot; Lighthouse Macro</div>
      <div>LighthouseMacro.com &middot; @LHMacro</div>
    </div>
  </div>
</body>
</html>
"""


# ============================================================
# MAIN
# ============================================================

def render_all(conn, out_dir: Path) -> list[tuple[str, dict]]:
    out_dir.mkdir(parents=True, exist_ok=True)
    results = []
    for i, (key, fn) in enumerate(CHART_FUNCS, 1):
        try:
            v = fn(conn, out_dir)
            print(f"  [{i:02d}/10] {key:18s} OK  ({v.get('path')})")
            results.append((key, v))
        except Exception as e:
            print(f"  [{i:02d}/10] {key:18s} FAILED: {e}")
            traceback.print_exc()
    return results


def write_manifest(out_dir: Path, brief_date: date, charts: list[tuple[str, dict]], hero: dict):
    def _ser(v):
        if isinstance(v, (pd.Timestamp, datetime, date)):
            return pd.Timestamp(v).strftime("%Y-%m-%d")
        if isinstance(v, (np.floating,)):
            return float(v)
        if isinstance(v, (np.integer,)):
            return int(v)
        return v

    manifest = {
        "date": brief_date.strftime("%Y-%m-%d"),
        "hero": {k: _ser(v) for k, v in hero.items()},
        "charts": [{"key": k, **{kk: _ser(vv) for kk, vv in v.items()}} for k, v in charts],
    }
    with open(out_dir / "manifest.json", "w") as f:
        json.dump(manifest, f, indent=2, default=str)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-charts", action="store_true",
                        help="skip chart re-render; reuse PNGs in today's archive dir")
    parser.add_argument("--stdout", action="store_true",
                        help="print HTML to stdout instead of writing files")
    parser.add_argument("--date", default=None,
                        help="override brief date (YYYY-MM-DD); defaults to today")
    args = parser.parse_args()

    brief_date = date.today() if not args.date else date.fromisoformat(args.date)
    out_dir = ARCHIVE_ROOT / brief_date.strftime("%Y-%m-%d")
    out_dir.mkdir(parents=True, exist_ok=True)

    conn = _conn()
    hero = compute_hero(conn)

    if args.no_charts:
        existing = []
        for key, _fn in CHART_FUNCS:
            for f in sorted(out_dir.glob(f"chart_*_{key}.png")):
                existing.append((key, {"path": f.name}))
                break
        charts = existing
        print(f"Skipping render. Reusing {len(charts)} chart(s) from {out_dir}")
    else:
        print(f"Rendering 10 charts into {out_dir}")
        charts = render_all(conn, out_dir)

    html_doc = build_html(brief_date, charts, out_dir, hero)
    write_manifest(out_dir, brief_date, charts, hero)

    if args.stdout:
        sys.stdout.write(html_doc)
    else:
        archive_path = out_dir / "morning_brief.html"
        archive_path.write_text(html_doc)
        DESKTOP_PATH.write_text(html_doc)
        print(f"HTML written: {archive_path}")
        print(f"HTML written: {DESKTOP_PATH}")
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(LOG_PATH, "a") as f:
            f.write(f"{datetime.now().isoformat()} v3 ok charts={len(charts)} -> {archive_path}\n")

    conn.close()


if __name__ == "__main__":
    main()
