#!/usr/bin/env python3
"""
Pharos terminal theme — canonical tokens + chart helpers + HTML skeleton (dark).

Tokens per Brand/brand-guide.md (palette locked 2026-06-16) and the dark-theme
role table in Brand/chart-styling.md (May 2026 update): Deep canvas, Sky-led
series cycle, Slate spines, Steel muted text. The retired #23BBFF appears
nowhere in this module.

Chart rules: no gridlines, all 4 spines 0.5pt, right axis primary, RHS
last-value pills, Fog dashed zero line, +/-2 sigma references only on z-charts,
NBER shading white alpha 0.06 on dark, x padding 0 left / 180 days right,
full history loaded and windowed to the relationship (lean longer).
"""

from __future__ import annotations

import base64
import io
import sqlite3
from datetime import datetime
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import FuncFormatter

DB_PATH = Path("/Users/bob/LHM/Data/databases/Lighthouse_Master.db")
OUT_DIR = Path("/Users/bob/LHM/Data/databases/pillars")

# ---------------------------------------------------------------- tokens
OCEAN = "#2389BB"
DUSK = "#FF6723"
SKY = "#89CCFF"          # current Sky (locked 2026-06-16); primary series on dark
DEEP = "#123456"         # dark canvas + ink token
SEA = "#00BB89"
VENUS = "#FF2389"
STARBOARD = "#238923"
PORT = "#892323"
DOLDRUMS = "#898989"
FOG = "#D1D1D1"
FOAM = "#FFFFFF"
GLACIER = "#F4F7F9"
ICE = "#D4E2EF"

# dark-theme roles (chart-styling.md May-2026 dark table)
DARK_BG = DEEP
DARK_FG = GLACIER        # "Offwhite" #f4f7f9
DARK_MUTED = "#9BB1C5"   # Steel
DARK_SPINE = "#2A4A6A"   # Slate
DARK_LIFT = "#1A3A5A"    # Deep-lift (cards / legend bg)

SERIES_CYCLE = [SKY, DUSK, SEA, VENUS]  # dark-canvas cycle, Sky leads

RECESSIONS = [
    ("2001-03-01", "2001-11-01"),
    ("2007-12-01", "2009-06-01"),
    ("2020-02-01", "2020-04-01"),
]

plt.rcParams["font.family"] = ["Inter", "Helvetica Neue", "Arial", "DejaVu Sans"]


# ---------------------------------------------------------------- data
def load_obs(series_id: str) -> pd.Series:
    with sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True) as conn:
        df = pd.read_sql_query(
            "SELECT date, value FROM observations WHERE series_id = ? ORDER BY date",
            conn, params=(series_id,), parse_dates=["date"],
        )
    if df.empty:
        raise ValueError(f"No data for {series_id}")
    return df.set_index("date")["value"].astype(float).dropna()


def load_index(index_id: str) -> pd.Series:
    with sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True) as conn:
        df = pd.read_sql_query(
            "SELECT date, value FROM lighthouse_indices WHERE index_id = ? ORDER BY date",
            conn, params=(index_id,), parse_dates=["date"],
        )
    if df.empty:
        raise ValueError(f"No index data for {index_id}")
    return df.set_index("date")["value"].astype(float).dropna()


def index_status(index_id: str) -> str:
    with sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True) as conn:
        row = conn.execute(
            "SELECT status FROM lighthouse_indices WHERE index_id = ? ORDER BY date DESC LIMIT 1",
            (index_id,),
        ).fetchone()
    return (row[0] or "") if row else ""


def yoy(s: pd.Series, periods: int = 12) -> pd.Series:
    return s.pct_change(periods, fill_method=None) * 100


def latest(s: pd.Series) -> tuple[float, pd.Timestamp]:
    s = s.dropna()
    return float(s.iloc[-1]), s.index[-1]


# ---------------------------------------------------------------- charts
def dark_fig(figsize=(7.6, 3.9)):
    fig, ax = plt.subplots(figsize=figsize, dpi=200)
    fig.patch.set_facecolor(DARK_BG)
    ax.set_facecolor(DARK_BG)
    return fig, ax


def style_ax(ax):
    for s in ax.spines.values():
        s.set_color(DARK_SPINE)
        s.set_linewidth(0.5)
    ax.grid(False)
    ax.tick_params(colors=DARK_MUTED, length=0, labelsize=9)
    ax.yaxis.tick_right()
    ax.yaxis.set_label_position("right")
    for lbl in ax.get_xticklabels() + ax.get_yticklabels():
        lbl.set_color(DARK_MUTED)


def set_xlim(ax, start: pd.Timestamp, end: pd.Timestamp | None = None):
    """House padding: 0 left, ~180 days right (room for pills)."""
    end = end or pd.Timestamp.today()
    ax.set_xlim(start, end + pd.DateOffset(days=180))
    span = (end - start).days / 365.25
    base = 5 if span > 25 else 3 if span > 15 else 2 if span > 8 else 1
    ax.xaxis.set_major_locator(mdates.YearLocator(base=base))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))


def add_recessions(ax, start: pd.Timestamp):
    for rs, re in RECESSIONS:
        rs_d, re_d = pd.Timestamp(rs), pd.Timestamp(re)
        if re_d < start:
            continue
        ax.axvspan(max(rs_d, start), re_d, color=FOAM, alpha=0.06, zorder=0)


def zero_line(ax):
    ax.axhline(0, color=FOG, linewidth=0.8, alpha=0.5, linestyle="--", zorder=1)


def sigma_refs(ax, sigma: float = 2.0):
    """Canonical z references: +/-2 sigma only, never +/-1."""
    for y in (sigma, -sigma):
        ax.axhline(y, color=DOLDRUMS, linewidth=0.8, alpha=0.55, linestyle=":", zorder=1)


def regime_bands(ax):
    """Composite z regime bands per chart-styling.md, retired hex replaced by Sky."""
    ax.axhspan(1.5, 3.0, color=PORT, alpha=0.25, zorder=0)
    ax.axhspan(1.0, 1.5, color=DUSK, alpha=0.20, zorder=0)
    ax.axhspan(0.5, 1.0, color=DUSK, alpha=0.12, zorder=0)
    ax.axhspan(-0.5, 0.5, color=SEA, alpha=0.12, zorder=0)
    ax.axhspan(-3.0, -0.5, color=SKY, alpha=0.10, zorder=0)
    labels = [(1.9, "CRISIS", PORT), (1.25, "HIGH", DUSK), (0.75, "ELEVATED", DUSK),
              (0.0, "NEUTRAL", SEA), (-1.0, "LOW RISK", SKY)]
    for y, txt, color in labels:
        ax.text(0.985, y, txt, transform=ax.get_yaxis_transform(), fontsize=8,
                color=color, va="center", ha="right", fontweight="bold", alpha=0.85)


def pill(ax, x, y, text, color, side="right"):
    dx = 8 if side == "right" else -8
    ha = "left" if side == "right" else "right"
    ax.annotate(
        text, xy=(x, y), xytext=(dx, 0), textcoords="offset points",
        fontsize=9, fontweight="bold", color="white", ha=ha, va="center",
        bbox=dict(boxstyle="round,pad=0.35", facecolor=color, edgecolor="none"),
        annotation_clip=False, zorder=5,
    )


def legend(ax, loc="upper left", ncol=1):
    leg = ax.legend(loc=loc, frameon=True, fontsize=8.5, ncol=ncol,
                    facecolor=DARK_LIFT, edgecolor=DARK_SPINE, framealpha=0.95)
    for t in leg.get_texts():
        t.set_color(DARK_FG)
    return leg


def to_b64(fig) -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=200, bbox_inches="tight", pad_inches=0.1,
                facecolor=DARK_BG)
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode("ascii")


# ---------------------------------------------------------------- html
CSS = """
:root {
  --ocean:#2389BB; --dusk:#FF6723; --sky:#89CCFF; --venus:#FF2389;
  --sea:#00BB89; --doldrums:#898989; --starboard:#238923; --port:#892323;
  --fog:#D1D1D1; --deep:#123456; --lift:#1A3A5A; --spine:#2A4A6A;
  --fg:#F4F7F9; --muted:#9BB1C5; --ice:#D4E2EF;
}
*{margin:0;padding:0;box-sizing:border-box;}
body{font-family:'Inter',-apple-system,sans-serif;background:var(--deep);color:var(--fg);line-height:1.55;}
.dashboard{max-width:1240px;margin:0 auto;}
.accent-bar{height:5px;background:linear-gradient(to right,var(--ocean) 66.6%,var(--dusk) 66.6%);}
.header{padding:26px 32px 14px;display:flex;justify-content:space-between;align-items:flex-start;gap:24px;}
.header-left h1{font-family:'Montserrat',sans-serif;font-weight:700;font-size:30px;color:var(--fg);letter-spacing:-0.5px;}
.header-left .subtitle{font-size:14px;color:var(--muted);margin-top:4px;}
.header-left .tagline{font-family:'Montserrat',sans-serif;font-weight:600;font-size:10px;color:var(--sky);letter-spacing:2px;text-transform:uppercase;margin-top:5px;opacity:0.75;}
.asof{font-family:'Source Code Pro',monospace;font-size:11px;color:var(--muted);padding-top:6px;text-align:right;}
.nav{display:flex;flex-wrap:wrap;gap:8px;padding:0 32px 18px;}
.nav a,.nav span{font-family:'Montserrat',sans-serif;font-weight:600;font-size:11px;letter-spacing:0.5px;text-decoration:none;
  padding:6px 12px;border-radius:6px;border:1px solid var(--spine);}
.nav a{color:var(--sky);}
.nav a.active{background:var(--ocean);color:#fff;border-color:var(--ocean);}
.nav span{color:var(--doldrums);}
.verdict{margin:0 32px 20px;padding:14px 20px;border-radius:8px;display:flex;align-items:center;gap:18px;color:#fff;}
.verdict-label{font-family:'Montserrat',sans-serif;font-weight:700;font-size:11px;letter-spacing:2px;text-transform:uppercase;opacity:0.85;white-space:nowrap;}
.verdict-state{font-family:'Montserrat',sans-serif;font-weight:700;font-size:20px;letter-spacing:1px;white-space:nowrap;}
.verdict-text{font-size:13px;opacity:0.94;flex:1;}
.tiles{display:grid;grid-template-columns:repeat(6,1fr);gap:12px;padding:0 32px 22px;}
@media (max-width:900px){.tiles{grid-template-columns:repeat(3,1fr);}}
.tile{background:var(--lift);border:1px solid var(--spine);border-radius:8px;padding:14px 14px 12px;position:relative;overflow:hidden;}
.tile::before{content:'';position:absolute;top:0;left:0;right:0;height:3px;background:var(--tile-accent,var(--ocean));}
.tile-label{font-family:'Montserrat',sans-serif;font-weight:600;font-size:10px;text-transform:uppercase;letter-spacing:1px;color:var(--muted);margin-bottom:6px;}
.tile-value{font-family:'Source Code Pro',monospace;font-size:25px;font-weight:600;color:var(--fg);line-height:1;}
.tile-unit{font-size:13px;color:var(--muted);}
.tile-meta{display:flex;justify-content:space-between;align-items:center;margin-top:9px;gap:6px;}
.tile-sub{font-size:10px;color:var(--muted);}
.tile-status{font-family:'Source Code Pro',monospace;font-size:9px;font-weight:600;padding:2px 6px;border-radius:3px;white-space:nowrap;}
.st-ok{background:rgba(0,187,137,0.15);color:var(--sea);}
.st-warn{background:rgba(255,103,35,0.15);color:var(--dusk);}
.st-alert{background:rgba(255,35,137,0.16);color:var(--venus);}
.st-flat{background:rgba(155,177,197,0.14);color:var(--muted);}
.section{padding:4px 32px 18px;}
.section h2{font-family:'Montserrat',sans-serif;font-weight:700;font-size:16px;color:var(--sky);margin-bottom:6px;}
.section p{font-size:13px;color:var(--ice);max-width:920px;}
.charts{display:grid;grid-template-columns:1fr 1fr;gap:18px;padding:0 32px 24px;}
@media (max-width:900px){.charts{grid-template-columns:1fr;}}
.chart-card{background:var(--lift);border:1px solid var(--spine);border-radius:8px;padding:16px 18px 18px;position:relative;overflow:hidden;}
.chart-card::before{content:'';position:absolute;top:0;left:0;right:0;height:3px;background:var(--ocean);}
.chart-title{font-family:'Montserrat',sans-serif;font-weight:700;font-size:14px;color:var(--fg);margin:4px 0 2px;}
.chart-sub{font-size:11px;color:var(--muted);margin-bottom:10px;line-height:1.45;}
.chart-card img{width:100%;height:auto;display:block;border-radius:4px;}
.footer{border-top:1px solid var(--spine);margin-top:6px;padding:16px 32px 20px;display:flex;justify-content:space-between;gap:16px;
  font-family:'Source Code Pro',monospace;font-size:10px;color:var(--muted);flex-wrap:wrap;}
.footer .byline{color:var(--ice);}
.footer-right{font-family:'Montserrat',sans-serif;font-weight:600;letter-spacing:1.5px;color:var(--sky);}
"""

PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} | Pharos | Lighthouse Macro</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@600;700&family=Inter:wght@400;500;600&family=Source+Code+Pro:wght@400;500;600&display=swap" rel="stylesheet">
<style>{css}</style>
</head>
<body>
<div class="dashboard">
  <div class="accent-bar"></div>
  <div class="header">
    <div class="header-left">
      <h1>{h1}</h1>
      <div class="subtitle">{subtitle}</div>
      <div class="tagline">MACRO, ILLUMINATED.</div>
    </div>
    <div class="asof">PHAROS<br>AS OF {asof}</div>
  </div>
  <div class="nav">{nav}</div>
  {body}
  <div class="footer">
    <div>
      <div class="byline">Bob Sheehan, CFA, CMT | Lighthouse Macro | LighthouseMacro.com | @LHMacro</div>
      <div>Sources: {sources} | Data thru {datathru} | Generated {generated}</div>
    </div>
    <div class="footer-right">LIGHTHOUSE MACRO</div>
  </div>
</div>
</body>
</html>
"""


def nav_strip(active: str) -> str:
    items = [
        ("index", "PHAROS", "/d"),
        ("the-watch", "00 THE WATCH", "/d/the-watch"),
        ("labor", "07 LABOR", "/d/labor"),
    ]
    out = []
    for slug, label, href in items:
        cls = ' class="active"' if slug == active else ""
        out.append(f'<a href="{href}"{cls}>{label}</a>')
    out.append("<span>26 MORE IN BUILD</span>")
    return "".join(out)


def tile(label: str, value: str, unit: str, sub: str, status: str, status_cls: str, accent: str) -> str:
    return f"""
    <div class="tile" style="--tile-accent:{accent};">
      <div class="tile-label">{label}</div>
      <div class="tile-value">{value}<span class="tile-unit">{unit}</span></div>
      <div class="tile-meta">
        <div class="tile-sub">{sub}</div>
        <div class="tile-status {status_cls}">{status}</div>
      </div>
    </div>"""


def chart_card(title: str, sub: str, b64: str) -> str:
    return f"""
    <div class="chart-card">
      <div class="chart-title">{title}</div>
      <div class="chart-sub">{sub}</div>
      <img src="data:image/png;base64,{b64}" alt="{title}">
    </div>"""


def verdict_block(label: str, state: str, text: str, color: str) -> str:
    return f"""
  <div class="verdict" style="background:{color};">
    <div>
      <div class="verdict-label">{label}</div>
      <div class="verdict-state">{state}</div>
    </div>
    <div class="verdict-text">{text}</div>
  </div>"""


def section(title: str, text: str) -> str:
    return f'<div class="section"><h2>{title}</h2><p>{text}</p></div>'


def render_page(*, title: str, h1: str, subtitle: str, active: str, body: str,
                sources: str, datathru: str) -> str:
    now = datetime.today()
    return PAGE.format(
        title=title, css=CSS, h1=h1, subtitle=subtitle,
        asof=now.strftime("%b %d, %Y").upper(),
        nav=nav_strip(active), body=body, sources=sources,
        datathru=datathru, generated=now.strftime("%Y-%m-%d %H:%M ET"),
    )


def write_page(filename: str, html: str) -> Path:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / filename
    out.write_text(html, encoding="utf-8")
    return out
