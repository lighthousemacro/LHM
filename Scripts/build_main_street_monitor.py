#!/usr/bin/env python3
"""
Main Street Monitor — Retail, Restaurants & Local Services
Pulls from Lighthouse_Master.db, builds a self-contained HTML dashboard with
base64-embedded charts. Paste-and-publish.

Usage:
    python build_main_street_monitor.py
    python build_main_street_monitor.py --open
"""

from __future__ import annotations

import argparse
import base64
import io
import sqlite3
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import FancyBboxPatch
from matplotlib.ticker import FuncFormatter

BASE = Path("/Users/bob/LHM")
DB_PATH = BASE / "Data/databases/Lighthouse_Master.db"
OUTPUT_HTML = BASE / "Data/databases/pillars/main_street_monitor.html"

C = {
    "ocean": "#2389BB",
    "dusk": "#FF6723",
    "sky": "#23BBFF",
    "venus": "#FF2389",
    "sea": "#00BB89",
    "doldrums": "#898989",
    "starboard": "#238923",
    "port": "#892323",
    "fog": "#D1D1D1",
}
RECESSIONS = [("2001-03-01", "2001-11-01"), ("2007-12-01", "2009-06-01"), ("2020-02-01", "2020-04-01")]
MIN_HISTORY_YEARS = 5


# ---------- data ----------

def load(series_id: str) -> pd.Series:
    with sqlite3.connect(DB_PATH) as conn:
        df = pd.read_sql_query(
            "SELECT date, value FROM observations WHERE series_id = ? ORDER BY date",
            conn,
            params=(series_id,),
            parse_dates=["date"],
        )
    if df.empty:
        raise ValueError(f"No data for {series_id}")
    return df.set_index("date")["value"].astype(float).dropna()


def yoy(s: pd.Series) -> pd.Series:
    return s.pct_change(12, fill_method=None) * 100


def latest(s: pd.Series) -> tuple[float, pd.Timestamp]:
    s = s.dropna()
    return float(s.iloc[-1]), s.index[-1]


def trend(s: pd.Series, lookback: int = 3) -> str:
    """Direction over last `lookback` prints."""
    s = s.dropna()
    if len(s) < lookback + 1:
        return "stable"
    recent = s.iloc[-1] - s.iloc[-1 - lookback]
    sd = s.diff().dropna().iloc[-24:].std()
    if abs(recent) < 0.3 * sd * lookback:
        return "stable"
    return "rising" if recent > 0 else "falling"


# ---------- plotting ----------

def _style_ax(ax):
    ax.spines["top"].set_color(C["doldrums"])
    ax.spines["right"].set_color(C["doldrums"])
    ax.spines["bottom"].set_color(C["doldrums"])
    ax.spines["left"].set_color(C["doldrums"])
    for s in ax.spines.values():
        s.set_linewidth(0.5)
    ax.tick_params(colors=C["doldrums"], length=0, labelsize=9)
    ax.yaxis.tick_right()
    ax.yaxis.set_label_position("right")
    for lbl in ax.get_xticklabels() + ax.get_yticklabels():
        lbl.set_color("#1a1a1a")
    ax.set_facecolor("white")


def _add_recessions(ax, start):
    for rs, re in RECESSIONS:
        rs_d, re_d = pd.Timestamp(rs), pd.Timestamp(re)
        if re_d < start:
            continue
        ax.axvspan(max(rs_d, start), re_d, color="#1a1a1a", alpha=0.08, zorder=0)


def _pill(ax, x, y, text, color):
    ax.annotate(
        text,
        xy=(x, y),
        xytext=(8, 0),
        textcoords="offset points",
        fontsize=9,
        fontweight="bold",
        color="white",
        ha="left",
        va="center",
        bbox=dict(boxstyle="round,pad=0.35", facecolor=color, edgecolor="none"),
        annotation_clip=False,
    )


def _xlim_from(ax, earliest_start: pd.Timestamp):
    end = pd.Timestamp.today() + pd.DateOffset(months=6)
    ax.set_xlim(earliest_start - pd.DateOffset(months=1), end)
    locator = mdates.YearLocator(base=1)
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))


def _fig():
    fig, ax = plt.subplots(figsize=(7.5, 3.9), dpi=140)
    fig.patch.set_facecolor("white")
    return fig, ax


def _to_base64(fig) -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=140, bbox_inches="tight", pad_inches=0.1, facecolor="white")
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode("ascii")


def _start_date(*series) -> pd.Timestamp:
    """Latest start among plotted series, clamped to >= 5yr back from max end."""
    starts = [s.dropna().index.min() for s in series]
    ends = [s.dropna().index.max() for s in series]
    start = max(starts)
    max_end = max(ends)
    five_yr = max_end - pd.DateOffset(years=MIN_HISTORY_YEARS)
    return min(start, five_yr)


def _fmt_pct(x, _):
    return f"{x:.0f}%"


# ---------- chart builders ----------

def chart_spending_pulse():
    pce = yoy(load("PCEC96"))
    rsx = load("RSXFS")
    cpi = load("CPIAUCSL")
    real_rsx = (rsx / cpi) * cpi.iloc[-1]
    rsx_yoy = yoy(real_rsx)
    start = _start_date(pce, rsx_yoy)
    fig, ax = _fig()
    _add_recessions(ax, start)
    ax.axhline(0, color=C["fog"], linestyle="--", linewidth=1, zorder=1)
    ax.plot(pce.index, pce.values, color=C["ocean"], linewidth=2.2, label="Real PCE YoY")
    ax.plot(rsx_yoy.index, rsx_yoy.values, color=C["dusk"], linewidth=2.2, label="Real Retail Sales YoY")
    _style_ax(ax)
    _xlim_from(ax, start)
    ax.yaxis.set_major_formatter(FuncFormatter(_fmt_pct))
    pce_v, pce_d = latest(pce)
    rsx_v, rsx_d = latest(rsx_yoy)
    _pill(ax, pce_d, pce_v, f"{pce_v:+.1f}%", C["ocean"])
    _pill(ax, rsx_d, rsx_v, f"{rsx_v:+.1f}%", C["dusk"])
    leg = ax.legend(loc="upper left", frameon=False, fontsize=9)
    for t in leg.get_texts():
        t.set_color("#1a1a1a")
    return _to_base64(fig), (pce_v, rsx_v)


def chart_wage_price_squeeze():
    wages = yoy(load("CES0500000003"))
    cpi = yoy(load("CPIAUCSL"))
    real_gap = wages - cpi
    start = _start_date(wages, cpi)
    fig, ax = _fig()
    _add_recessions(ax, start)
    ax.axhline(0, color=C["fog"], linestyle="--", linewidth=1, zorder=1)
    ax.fill_between(
        real_gap.index,
        0,
        real_gap.values,
        where=real_gap.values >= 0,
        color=C["sea"],
        alpha=0.25,
        interpolate=True,
        label="Real wage gain",
    )
    ax.fill_between(
        real_gap.index,
        0,
        real_gap.values,
        where=real_gap.values < 0,
        color=C["port"],
        alpha=0.25,
        interpolate=True,
        label="Real wage loss",
    )
    ax.plot(wages.index, wages.values, color=C["ocean"], linewidth=2.2, label="Wages YoY")
    ax.plot(cpi.index, cpi.values, color=C["dusk"], linewidth=2.2, label="CPI YoY")
    _style_ax(ax)
    _xlim_from(ax, start)
    ax.yaxis.set_major_formatter(FuncFormatter(_fmt_pct))
    w_v, w_d = latest(wages)
    c_v, c_d = latest(cpi)
    _pill(ax, w_d, w_v, f"{w_v:+.1f}%", C["ocean"])
    _pill(ax, c_d, c_v, f"{c_v:+.1f}%", C["dusk"])
    leg = ax.legend(loc="upper left", frameon=False, fontsize=8, ncol=2)
    for t in leg.get_texts():
        t.set_color("#1a1a1a")
    gap_v = w_v - c_v
    return _to_base64(fig), (w_v, c_v, gap_v)


def chart_rent_stress():
    zori = yoy(load("ZILLOW_ZORI_NATIONAL"))
    cpi_rent = yoy(load("CUSR0000SEHA"))
    start = _start_date(zori, cpi_rent)
    fig, ax = _fig()
    _add_recessions(ax, start)
    ax.axhline(0, color=C["fog"], linestyle="--", linewidth=1, zorder=1)
    ax.plot(zori.index, zori.values, color=C["dusk"], linewidth=2.2, label="Zillow ZORI (market rents)")
    ax.plot(cpi_rent.index, cpi_rent.values, color=C["ocean"], linewidth=2.2, label="CPI Rent (lease renewals, lagged)")
    _style_ax(ax)
    _xlim_from(ax, start)
    ax.yaxis.set_major_formatter(FuncFormatter(_fmt_pct))
    z_v, z_d = latest(zori)
    r_v, r_d = latest(cpi_rent)
    _pill(ax, z_d, z_v, f"{z_v:+.1f}%", C["dusk"])
    _pill(ax, r_d, r_v, f"{r_v:+.1f}%", C["ocean"])
    leg = ax.legend(loc="upper right", frameon=False, fontsize=8)
    for t in leg.get_texts():
        t.set_color("#1a1a1a")
    return _to_base64(fig), (z_v, r_v)


def chart_credit_balance_sheet():
    cc = load("DRCCLACBS")
    save = load("PSAVERT")
    start = _start_date(cc, save)
    fig, ax = _fig()
    _add_recessions(ax, start)
    ax2 = ax.twinx()
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    ax2.spines["bottom"].set_visible(False)
    ax2.spines["left"].set_visible(False)
    ax2.tick_params(colors=C["doldrums"], length=0, labelsize=9)
    ax2.yaxis.tick_left()
    ax2.yaxis.set_label_position("left")
    for lbl in ax2.get_yticklabels():
        lbl.set_color("#1a1a1a")
    ax.fill_between(cc.index, 0, cc.values, color=C["port"], alpha=0.15)
    ax.plot(cc.index, cc.values, color=C["port"], linewidth=2.2, label="CC Delinquency (RHS)")
    ax2.plot(save.index, save.values, color=C["ocean"], linewidth=2.2, label="Saving Rate (LHS)")
    _style_ax(ax)
    _xlim_from(ax, start)
    ax.yaxis.set_major_formatter(FuncFormatter(_fmt_pct))
    ax2.yaxis.set_major_formatter(FuncFormatter(_fmt_pct))
    cc_v, cc_d = latest(cc)
    s_v, s_d = latest(save)
    _pill(ax, cc_d, cc_v, f"{cc_v:.1f}%", C["port"])
    ax2.annotate(
        f"{s_v:.1f}%",
        xy=(s_d, s_v),
        xytext=(-8, 0),
        textcoords="offset points",
        fontsize=9,
        fontweight="bold",
        color="white",
        ha="right",
        va="center",
        bbox=dict(boxstyle="round,pad=0.35", facecolor=C["ocean"], edgecolor="none"),
        annotation_clip=False,
    )
    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    leg = ax.legend(h1 + h2, l1 + l2, loc="upper left", frameon=False, fontsize=8)
    for t in leg.get_texts():
        t.set_color("#1a1a1a")
    return _to_base64(fig), (cc_v, s_v)


def chart_main_street_jobs():
    retail = yoy(load("USTRADE"))
    leisure = yoy(load("USLAH"))
    start = _start_date(retail, leisure)
    fig, ax = _fig()
    _add_recessions(ax, start)
    ax.axhline(0, color=C["fog"], linestyle="--", linewidth=1, zorder=1)
    ax.plot(retail.index, retail.values, color=C["ocean"], linewidth=2.2, label="Retail Trade")
    ax.plot(leisure.index, leisure.values, color=C["dusk"], linewidth=2.2, label="Leisure & Hospitality")
    _style_ax(ax)
    _xlim_from(ax, start)
    ax.set_ylim(-15, 10)
    ax.yaxis.set_major_formatter(FuncFormatter(_fmt_pct))
    r_v, r_d = latest(retail)
    l_v, l_d = latest(leisure)
    _pill(ax, r_d, r_v, f"{r_v:+.1f}%", C["ocean"])
    _pill(ax, l_d, l_v, f"{l_v:+.1f}%", C["dusk"])
    leg = ax.legend(loc="upper left", frameon=False, fontsize=9)
    for t in leg.get_texts():
        t.set_color("#1a1a1a")
    return _to_base64(fig), (r_v, l_v)


def chart_quit_signal():
    r_quits = load("JTS4400QUR")
    l_quits = load("JTS7000QUR")
    start = _start_date(r_quits, l_quits)
    fig, ax = _fig()
    _add_recessions(ax, start)
    ax.plot(r_quits.index, r_quits.values, color=C["ocean"], linewidth=2.2, label="Retail Trade Quits Rate")
    ax.plot(l_quits.index, l_quits.values, color=C["dusk"], linewidth=2.2, label="Leisure & Hospitality Quits Rate")
    ax.axhline(2.0, color=C["venus"], linestyle="-", linewidth=1.2, alpha=0.7, label="2.0% floor")
    _style_ax(ax)
    _xlim_from(ax, start)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{x:.1f}%"))
    r_v, r_d = latest(r_quits)
    l_v, l_d = latest(l_quits)
    _pill(ax, r_d, r_v, f"{r_v:.1f}%", C["ocean"])
    _pill(ax, l_d, l_v, f"{l_v:.1f}%", C["dusk"])
    leg = ax.legend(loc="upper right", frameon=False, fontsize=8)
    for t in leg.get_texts():
        t.set_color("#1a1a1a")
    return _to_base64(fig), (r_v, l_v)


# ---------- regime verdict ----------

@dataclass
class Scorecard:
    label: str
    value: str
    sublabel: str
    trend: str
    color_class: str


def compute_verdict(metrics: dict) -> tuple[str, str]:
    """Produce a regime verdict and color from headline metrics."""
    flags = 0
    total = 0
    pce, rsx = metrics["spending"]
    wages, cpi, gap = metrics["wage_price"]
    zori, rent = metrics["rent"]
    cc, save = metrics["credit"]
    retail_jobs, leisure_jobs = metrics["jobs"]
    retail_quits, leisure_quits = metrics["quits"]

    checks = [
        pce > 1.5,
        rsx > 1.0,
        gap > 0,
        cpi < 3.0,
        cc < 3.0,
        save > 4.5,
        retail_jobs > 0,
        leisure_jobs > 0,
        retail_quits > 2.0,
        leisure_quits > 3.0,
    ]
    flags = sum(checks)
    total = len(checks)
    score = flags / total
    if score >= 0.75:
        return "EXPANDING", C["starboard"]
    if score >= 0.55:
        return "STABLE", C["ocean"]
    if score >= 0.35:
        return "COOLING", C["dusk"]
    return "CONTRACTING", C["port"]


# ---------- html ----------

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Main Street Monitor | Lighthouse Macro</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@600;700&family=Inter:wght@400;500;600&family=Source+Code+Pro:wght@400;500;600&display=swap" rel="stylesheet">
<style>
:root {{
  --ocean:#2389BB; --dusk:#FF6723; --sky:#23BBFF; --venus:#FF2389;
  --sea:#00BB89; --doldrums:#898989; --starboard:#238923; --port:#892323;
  --fog:#D1D1D1; --bg:#FFFFFF; --fg:#1a1a1a;
  --card-bg:#fafbfc; --card-border:#e9ecef;
}}
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{font-family:'Inter',-apple-system,sans-serif;background:var(--bg);color:var(--fg);line-height:1.5;}}
.dashboard{{max-width:1240px;margin:0 auto;padding:0;}}
.accent-bar{{height:5px;background:linear-gradient(to right,var(--ocean) 66.6%,var(--dusk) 66.6%);}}
.header{{padding:28px 32px 18px;display:flex;justify-content:space-between;align-items:flex-start;gap:24px;}}
.header-left h1{{font-family:'Montserrat',sans-serif;font-weight:700;font-size:30px;color:var(--ocean);letter-spacing:-0.5px;}}
.header-left .subtitle{{font-size:14px;color:var(--doldrums);margin-top:4px;}}
.header-left .tagline{{font-family:'Montserrat',sans-serif;font-weight:600;font-size:10px;color:var(--doldrums);letter-spacing:2px;text-transform:uppercase;margin-top:3px;opacity:0.6;}}
.header-right{{display:flex;align-items:flex-start;gap:12px;}}
.asof{{font-family:'Source Code Pro',monospace;font-size:11px;color:var(--doldrums);padding-top:6px;}}
.verdict{{margin:0 32px 20px;padding:14px 20px;border-radius:8px;display:flex;align-items:center;gap:16px;color:white;}}
.verdict-label{{font-family:'Montserrat',sans-serif;font-weight:700;font-size:11px;letter-spacing:2px;text-transform:uppercase;opacity:0.85;}}
.verdict-state{{font-family:'Montserrat',sans-serif;font-weight:700;font-size:20px;letter-spacing:1px;}}
.verdict-text{{font-size:13px;opacity:0.92;flex:1;}}
.scorecards{{display:grid;grid-template-columns:repeat(6,1fr);gap:12px;padding:0 32px 24px;}}
.scorecard{{background:var(--card-bg);border:1px solid var(--card-border);border-radius:8px;padding:14px 14px 12px;position:relative;overflow:hidden;}}
.scorecard::before{{content:'';position:absolute;top:0;left:0;right:0;height:3px;}}
.scorecard.c1::before{{background:var(--ocean);}}
.scorecard.c2::before{{background:var(--dusk);}}
.scorecard.c3::before{{background:var(--sky);}}
.scorecard.c4::before{{background:var(--sea);}}
.scorecard.c5::before{{background:var(--venus);}}
.scorecard.c6::before{{background:var(--starboard);}}
.scorecard-label{{font-family:'Montserrat',sans-serif;font-weight:600;font-size:10px;text-transform:uppercase;letter-spacing:1px;color:var(--doldrums);margin-bottom:6px;}}
.scorecard-value{{font-family:'Source Code Pro',monospace;font-size:26px;font-weight:600;color:var(--fg);line-height:1;}}
.scorecard-unit{{font-size:14px;color:var(--doldrums);}}
.scorecard-meta{{display:flex;justify-content:space-between;align-items:center;margin-top:10px;}}
.scorecard-sublabel{{font-size:10px;color:var(--doldrums);}}
.scorecard-trend{{font-family:'Source Code Pro',monospace;font-size:10px;font-weight:600;padding:2px 6px;border-radius:3px;}}
.trend-good{{background:rgba(35,137,35,0.12);color:var(--starboard);}}
.trend-bad{{background:rgba(137,35,35,0.12);color:var(--port);}}
.trend-flat{{background:rgba(137,137,137,0.12);color:var(--doldrums);}}
.charts{{display:grid;grid-template-columns:1fr 1fr;gap:18px;padding:0 32px 24px;}}
.chart-card{{background:var(--card-bg);border:1px solid var(--card-border);border-radius:8px;padding:16px 18px 18px;position:relative;overflow:hidden;}}
.chart-card::before{{content:'';position:absolute;top:0;left:0;right:0;height:3px;background:var(--ocean);}}
.chart-title{{font-family:'Montserrat',sans-serif;font-weight:700;font-size:14px;color:var(--fg);margin-bottom:2px;margin-top:4px;}}
.chart-sub{{font-size:11px;color:var(--doldrums);margin-bottom:10px;line-height:1.4;}}
.chart-card img{{width:100%;height:auto;display:block;}}
.footer{{border-top:1px solid var(--card-border);padding:14px 32px;display:flex;justify-content:space-between;font-family:'Source Code Pro',monospace;font-size:10px;color:var(--doldrums);}}
.footer-right{{font-family:'Montserrat',sans-serif;font-weight:600;letter-spacing:1.5px;}}
</style>
</head>
<body>
<div class="dashboard">
  <div class="accent-bar"></div>
  <div class="header">
    <div class="header-left">
      <h1>MAIN STREET MONITOR</h1>
      <div class="subtitle">Retail, Restaurants &amp; Local Services</div>
      <div class="tagline">MACRO, ILLUMINATED.</div>
    </div>
    <div class="header-right">
      <div class="asof">AS OF {asof}</div>
    </div>
  </div>

  <div class="verdict" style="background:{verdict_color};">
    <div>
      <div class="verdict-label">Main Street Regime</div>
      <div class="verdict-state">{verdict_state}</div>
    </div>
    <div class="verdict-text">{verdict_text}</div>
  </div>

  <div class="scorecards">
    {scorecards}
  </div>

  <div class="charts">
    {chart_cards}
  </div>

  <div class="footer">
    <div>Lighthouse Macro  |  Sources: BEA, BLS, Census, Federal Reserve, Zillow  |  Data thru {datathru}  |  Generated {generated}</div>
    <div class="footer-right">LIGHTHOUSE MACRO</div>
  </div>
</div>
</body>
</html>
"""


def render_scorecard(cls: str, label: str, value: str, unit: str, sublabel: str, trend_label: str, trend_class: str) -> str:
    arrow = {"good": "▲", "bad": "▼", "flat": "▶"}[trend_class]
    return f"""
    <div class="scorecard {cls}">
      <div class="scorecard-label">{label}</div>
      <div class="scorecard-value">{value}<span class="scorecard-unit">{unit}</span></div>
      <div class="scorecard-meta">
        <div class="scorecard-sublabel">{sublabel}</div>
        <div class="scorecard-trend trend-{trend_class}">{arrow} {trend_label}</div>
      </div>
    </div>"""


def render_chart(title: str, sub: str, b64: str) -> str:
    return f"""
    <div class="chart-card">
      <div class="chart-title">{title}</div>
      <div class="chart-sub">{sub}</div>
      <img src="data:image/png;base64,{b64}" alt="{title}">
    </div>"""


def trend_class(direction: str, good_is_rising: bool) -> str:
    if direction == "stable":
        return "flat"
    if direction == "rising":
        return "good" if good_is_rising else "bad"
    return "bad" if good_is_rising else "good"


# ---------- main ----------

def build():
    print("Loading data...", file=sys.stderr)

    pce = yoy(load("PCEC96"))
    rsx = load("RSXFS")
    cpi_lvl = load("CPIAUCSL")
    rsx_real_yoy = yoy((rsx / cpi_lvl) * cpi_lvl.iloc[-1])
    wages = yoy(load("CES0500000003"))
    cpi_yoy = yoy(load("CPIAUCSL"))
    core_cpi = yoy(load("CPILFESL"))
    cc_delq = load("DRCCLACBS")
    save_rt = load("PSAVERT")

    print("Building charts...", file=sys.stderr)
    c1, m1 = chart_spending_pulse()
    c2, m2 = chart_wage_price_squeeze()
    c3, m3 = chart_rent_stress()
    c4, m4 = chart_credit_balance_sheet()
    c5, m5 = chart_main_street_jobs()
    c6, m6 = chart_quit_signal()

    pce_v, pce_d = latest(pce)
    rsx_v, rsx_d = latest(rsx_real_yoy)
    wage_v, wage_d = latest(wages)
    core_v, core_d = latest(core_cpi)
    cc_v, cc_d = latest(cc_delq)
    save_v, save_d = latest(save_rt)

    metrics = {
        "spending": m1,
        "wage_price": m2,
        "rent": m3,
        "credit": m4,
        "jobs": m5,
        "quits": m6,
    }
    verdict_state, verdict_color = compute_verdict(metrics)
    verdict_text_map = {
        "EXPANDING": "Real spending and wages positive, credit clean, quits elevated. Consumers are healthy.",
        "STABLE": "Mixed but functional. Watch the divergence between wages and delinquencies.",
        "COOLING": "Flows are softening. Not broken yet, but the margin of safety has thinned.",
        "CONTRACTING": "Multiple stress points. The last domino is wobbling.",
    }
    verdict_text = verdict_text_map[verdict_state]

    cards = [
        render_scorecard("c1", "Customer Spending", f"{pce_v:+.1f}", "%", "Real PCE YoY",
                         trend(pce).capitalize(), trend_class(trend(pce), good_is_rising=True)),
        render_scorecard("c2", "Retail Pulse", f"{rsx_v:+.1f}", "%", "Real Retail YoY",
                         trend(rsx_real_yoy).capitalize(), trend_class(trend(rsx_real_yoy), good_is_rising=True)),
        render_scorecard("c3", "Service Wages", f"{wage_v:+.1f}", "%", "AHE YoY",
                         trend(wages).capitalize(), trend_class(trend(wages), good_is_rising=True)),
        render_scorecard("c4", "Core Prices", f"{core_v:+.1f}", "%", "Core CPI YoY",
                         trend(core_cpi).capitalize(), trend_class(trend(core_cpi), good_is_rising=False)),
        render_scorecard("c5", "Credit Strain", f"{cc_v:.1f}", "%", "CC Delinquency",
                         trend(cc_delq).capitalize(), trend_class(trend(cc_delq), good_is_rising=False)),
        render_scorecard("c6", "Safety Margin", f"{save_v:.1f}", "%", "Saving Rate",
                         trend(save_rt).capitalize(), trend_class(trend(save_rt), good_is_rising=True)),
    ]

    chart_cards = [
        render_chart("Spending Pulse", "Real PCE YoY vs real retail sales YoY. Is the customer still showing up?", c1),
        render_chart("The Wage-Price Squeeze", "Service-sector wages versus CPI. The shaded gap is real purchasing power.", c2),
        render_chart("Rent Stress", "Zillow market rents lead CPI shelter by 9-12 months. What lease renewals will price.", c3),
        render_chart("Customer Balance Sheet", "Credit card delinquency vs personal saving rate. Borrowing or cushioning?", c4),
        render_chart("Main Street Jobs", "Retail trade and leisure/hospitality payroll growth. Main Street's employment pulse.", c5),
        render_chart("The Quit Signal", "JOLTS quits rate for retail and hospitality. Confidence to walk away = labor power.", c6),
    ]

    data_thru = max([pce_d, rsx_d, wage_d, core_d, cc_d, save_d]).strftime("%Y-%m")
    asof = datetime.today().strftime("%b %d, %Y").upper()
    generated = datetime.today().strftime("%Y-%m-%d %H:%M ET")

    html = HTML.format(
        asof=asof,
        verdict_color=verdict_color,
        verdict_state=verdict_state,
        verdict_text=verdict_text,
        scorecards="".join(cards),
        chart_cards="".join(chart_cards),
        datathru=data_thru,
        generated=generated,
    )

    OUTPUT_HTML.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_HTML.write_text(html, encoding="utf-8")
    print(f"Wrote {OUTPUT_HTML} ({len(html):,} bytes)", file=sys.stderr)
    return OUTPUT_HTML


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--open", action="store_true")
    args = p.parse_args()
    out = build()
    if args.open:
        import subprocess
        subprocess.run(["open", str(out)])
