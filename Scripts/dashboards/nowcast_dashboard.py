#!/usr/bin/env python3
"""
LIGHTHOUSE MACRO — NOWCAST DASHBOARD
=====================================
Reads lighthouse_indices and renders a branded daily-fresh dashboard.
Stable output path so the same URL/file always reflects the latest state.

Run:
    python Scripts/dashboards/nowcast_dashboard.py
    # or, called automatically at the end of compute_indices.py

Output:
    /Users/bob/LHM/Outputs/nowcast_dashboard.html
"""

from __future__ import annotations

import argparse
import sqlite3
import subprocess
import sys
from datetime import datetime
from pathlib import Path

DB_PATH = Path("/Users/bob/LHM/Data/databases/Lighthouse_Master.db")
OUTPUT_PATH = Path("/Users/bob/LHM/Outputs/nowcast_dashboard.html")

# Indicator metadata — name, pillar number/label, pillar group, format hint.
# Pillar group drives section placement on the dashboard.
INDICATORS: dict = {
    # MASTER + OUTPUTS — top row
    "MRI": ("Macro Risk Index",          "Master",  "master",  "z"),
    "REC_PROB": ("Recession Probability","Output",  "master",  "pct"),
    "ALLOC_MULTIPLIER": ("Allocation Multiplier","Output","master","mult"),
    "WARNING_LEVEL": ("Warning Level",   "Output",  "master",  "level"),

    # PILLARS 1-7 · MACRO DYNAMICS
    "LFI": ("Labor Fragility",           "1 · Labor",      "macro", "z"),
    "LPI": ("Labor Pressure",            "1 · Labor",      "macro", "z"),
    "LDI": ("Labor Dynamism",            "1 · Labor",      "macro", "z"),
    "PCI": ("Inflation Heat",            "2 · Prices",     "macro", "z"),
    "GCI": ("Activity Pulse",            "3 · Growth",     "macro", "z"),
    "HCI": ("Housing Tide",              "4 · Housing",    "macro", "z"),
    "CCI": ("Consumer Pulse",            "5 · Consumer",   "macro", "z"),
    "BCI": ("Capex Thrust",              "6 · Business",   "macro", "z"),
    "TCI": ("Global Risk Tide",          "7 · Trade",      "macro", "z"),

    # PILLARS 8-10 · MONETARY MECHANICS
    "FPI": ("Fiscal Pressure",           "8 · Government", "monetary", "z"),
    "FCI": ("Credit Tide",               "9 · Financial",  "monetary", "z"),
    "LCI": ("Liquidity Cushion",         "10 · Plumbing",  "monetary", "z"),
    "LIQ_STAGE": ("Liquidity Stage",     "10 · Plumbing",  "monetary", "stage"),

    # PILLARS 11-12 · MARKET STRUCTURE
    "MSI": ("Market Breadth Pulse",      "11 · Structure", "structure", "z"),
    "SBD": ("Structure-Breadth Divergence","11 · Structure","structure","z"),
    "EMD": ("Equity Momentum Divergence","11 · Structure", "structure", "z"),
    "SPI": ("Sentiment Tide",            "12 · Sentiment", "structure", "z"),
    "SSD": ("Sentiment-Structure Divergence","cross · 11 ↔ 12","structure","z"),

    # CROSS-PILLAR
    "CLG": ("Credit-Labor Gap",          "cross · 1 ↔ 9",  "cross", "z"),
    "YFS": ("Yield-Funding Stress",      "cross · 8 + 10", "cross", "z"),
    "SVI": ("Spread-Volatility Imbalance","cross · 9 + 12","cross", "z"),

    # ADDITIONAL OUTPUTS
    "BASE_REC_PROB": ("Base Recession Probability","Output","extra", "pct"),
    "ENSEMBLE_RISK": ("Ensemble Risk",   "Output",  "extra", "pct"),
    "DISCONTINUITY_PREMIUM": ("Discontinuity Premium","Output","extra","pct"),
}

# Pillar number → friendly name, used in the heatmap.
PILLAR_LABELS = {
    1: "Labor",       2: "Prices",      3: "Growth",       4: "Housing",
    5: "Consumer",    6: "Business",    7: "Trade",        8: "Government",
    9: "Financial",  10: "Plumbing",   11: "Structure",  12: "Sentiment",
}

# Best-available pillar composite for the heatmap dot.
PILLAR_COMPOSITE = {
    1: "LFI", 2: "PCI", 3: "GCI", 4: "HCI", 5: "CCI", 6: "BCI",
    7: "TCI", 8: "FPI", 9: "FCI", 10: "LCI", 11: "MSI", 12: "SPI",
}


# Brand colors
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


def status_color(status: str | None, value: float | None = None) -> str:
    """Heuristic color for status pill. Reads keywords."""
    s = (status or "").upper()
    if any(w in s for w in ("CRISIS", "RECESSION", "EXTREME", "CRITICAL",
                            "STRESS RISK", "HIGH RISK", "RED", "MISPRICED",
                            "SEVERELY MISPRICED", "MAX DEFENSIVE", "DEFLATIONARY",
                            "CAPITAL PRESERVATION", "INFLATION CRISIS")):
        return PORT
    if any(w in s for w in ("PRE-RECESSION", "PRE_CRISIS", "LATE CYCLE",
                            "ELEVATED", "HEADWIND", "FROZEN", "WEAK",
                            "DISTRIBUTION", "SLUGGISH", "EUPHORIC", "TIGHT",
                            "BILLS VERY RICH", "FEAR + WEAK", "HIGH INFLATION",
                            "FEAR")):
        return DUSK
    if any(w in s for w in ("HEALTHY", "BOOM", "EXPANSION", "STRONG",
                            "BULLISH", "ABUNDANT", "EARLY EXPANSION",
                            "LOW RISK", "ON TARGET", "FISCAL HEALTH",
                            "HIGH DYNAMISM", "STRONG GROWTH")):
        return STARBOARD
    if any(w in s for w in ("NEUTRAL", "MID-CYCLE", "BALANCED", "TREND",
                            "MODERATE", "AMPLE")):
        return DOLDRUMS
    return OCEAN


def fetch_state() -> tuple[dict, dict, str]:
    """Pull latest values, 90-day history, and pipeline run date."""
    conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    try:
        # Latest per index
        rows = conn.execute("""
            SELECT i.index_id, i.value, i.status, i.date
            FROM lighthouse_indices i
            JOIN (
                SELECT index_id, MAX(date) AS max_date
                FROM lighthouse_indices
                GROUP BY index_id
            ) m ON m.index_id = i.index_id AND m.max_date = i.date
        """).fetchall()
        latest = {r[0]: {"value": r[1], "status": r[2], "date": r[3]} for r in rows}

        # 90-day history
        history: dict = {}
        for index_id in INDICATORS.keys():
            hrows = conn.execute("""
                SELECT date, value FROM lighthouse_indices
                WHERE index_id = ? AND date >= date('now', '-180 day')
                ORDER BY date
            """, (index_id,)).fetchall()
            history[index_id] = hrows

        max_date_row = conn.execute(
            "SELECT MAX(date) FROM lighthouse_indices"
        ).fetchone()
        run_date = max_date_row[0] if max_date_row else None
    finally:
        conn.close()
    return latest, history, run_date


def fmt_value(v: float | None, fmt: str) -> str:
    if v is None:
        return "—"
    if fmt == "pct":
        return f"{v * 100:.1f}%" if abs(v) < 2 else f"{v:.1f}%"
    if fmt == "mult":
        return f"{v:.2f}×"
    if fmt == "level":
        # warning level 1-4, render as the integer
        return f"{int(round(v))}"
    if fmt == "stage":
        return f"Stage {int(round(v))}"
    # default z-score
    return f"{v:+.3f}"


def sparkline_svg(values: list, width: int = 130, height: int = 30,
                  color: str = OCEAN) -> str:
    """Inline SVG sparkline. Values = list of (date_str, value)."""
    nums = [v for _, v in values if v is not None]
    if len(nums) < 3:
        return ""
    vmin, vmax = min(nums), max(nums)
    rng = (vmax - vmin) or 1.0
    n = len(nums)
    pts = []
    for i, v in enumerate(nums):
        x = (i / (n - 1)) * (width - 4) + 2
        y = height - 3 - ((v - vmin) / rng) * (height - 6)
        pts.append(f"{x:.1f},{y:.1f}")
    polyline = " ".join(pts)
    last_x, last_y = pts[-1].split(",")
    # Zero line if data crosses zero
    zero_line = ""
    if vmin < 0 < vmax:
        zy = height - 3 - ((0 - vmin) / rng) * (height - 6)
        zero_line = (
            f'<line x1="2" y1="{zy:.1f}" x2="{width - 2}" y2="{zy:.1f}" '
            f'stroke="{FOG}" stroke-width="0.5" stroke-dasharray="2,2"/>'
        )
    return (
        f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}">'
        f'{zero_line}'
        f'<polyline points="{polyline}" fill="none" stroke="{color}" '
        f'stroke-width="1.5" stroke-linejoin="round"/>'
        f'<circle cx="{last_x}" cy="{last_y}" r="2.5" fill="{color}"/>'
        f'</svg>'
    )


def pillar_dot_color(z: float | None) -> str:
    """Heatmap dot color for a pillar composite z-score."""
    if z is None:
        return DOLDRUMS
    if z <= -1.5:
        return PORT
    if z <= -0.5:
        return DUSK
    if z <= 0.5:
        return DOLDRUMS
    if z <= 1.5:
        return SEA
    return STARBOARD


def render_master_tile(code: str, latest: dict, history: dict) -> str:
    name, pillar, group, fmt = INDICATORS[code]
    cur = latest.get(code, {})
    v = cur.get("value")
    status = cur.get("status") or "—"
    color = status_color(status, v)
    spark = sparkline_svg(history.get(code, []), width=180, height=44, color=color)
    return f"""
    <div class="master-tile">
      <div class="master-tile-row">
        <span class="master-tile-name">{name}</span>
        <span class="master-tile-tag">{pillar}</span>
      </div>
      <div class="master-tile-value" style="color:{color};">{fmt_value(v, fmt)}</div>
      <div class="master-tile-status" style="background:{color};">{status}</div>
      <div class="master-tile-spark">{spark}</div>
    </div>
    """


def render_card(code: str, latest: dict, history: dict) -> str:
    name, pillar, group, fmt = INDICATORS[code]
    cur = latest.get(code, {})
    v = cur.get("value")
    status = cur.get("status") or "—"
    color = status_color(status, v)
    spark = sparkline_svg(history.get(code, []), width=130, height=28, color=color)
    return f"""
    <div class="card">
      <div class="card-head">
        <div class="card-name">{name}</div>
        <div class="card-pillar">{pillar}</div>
      </div>
      <div class="card-value" style="color:{color};">{fmt_value(v, fmt)}</div>
      <div class="card-status-row">
        <span class="card-status" style="background:{color};">{status}</span>
        <span class="card-spark">{spark}</span>
      </div>
    </div>
    """


def render_pillar_heatmap(latest: dict) -> str:
    cells = []
    for pillar_num in range(1, 13):
        code = PILLAR_COMPOSITE[pillar_num]
        v = (latest.get(code) or {}).get("value")
        color = pillar_dot_color(v)
        cells.append(f"""
        <div class="pillar-cell">
          <div class="pillar-num">{pillar_num}</div>
          <div class="pillar-dot" style="background:{color};"></div>
          <div class="pillar-name">{PILLAR_LABELS[pillar_num]}</div>
          <div class="pillar-z">{fmt_value(v, "z")}</div>
        </div>
        """)
    return f'<div class="pillar-heatmap">{"".join(cells)}</div>'


def render_section(title: str, subtitle: str, codes: list, latest: dict,
                   history: dict) -> str:
    cards = "".join(render_card(c, latest, history) for c in codes)
    return f"""
    <section class="section">
      <h2 class="section-title">{title}</h2>
      <div class="section-subtitle">{subtitle}</div>
      <div class="card-grid">{cards}</div>
    </section>
    """


def render_dashboard(latest: dict, history: dict, run_date: str | None) -> str:
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M ET")

    master_tiles = "".join(
        render_master_tile(c, latest, history)
        for c in ("MRI", "REC_PROB", "ALLOC_MULTIPLIER", "WARNING_LEVEL")
    )

    macro_codes = ["LFI", "LPI", "LDI", "PCI", "GCI", "HCI", "CCI", "BCI", "TCI"]
    monetary_codes = ["FPI", "FCI", "LCI", "LIQ_STAGE"]
    structure_codes = ["MSI", "SBD", "EMD", "SPI", "SSD"]
    cross_codes = ["CLG", "YFS", "SVI"]
    extra_codes = ["BASE_REC_PROB", "ENSEMBLE_RISK", "DISCONTINUITY_PREMIUM"]

    pillar_heatmap = render_pillar_heatmap(latest)

    sections = (
        render_section(
            "Macro Dynamics",
            "Pillars 1-7. The real economy.",
            macro_codes, latest, history,
        )
        + render_section(
            "Monetary Mechanics",
            "Pillars 8-10. Fiscal, financial, and plumbing.",
            monetary_codes, latest, history,
        )
        + render_section(
            "Market Structure",
            "Pillars 11-12. Price, breadth, sentiment.",
            structure_codes, latest, history,
        )
        + render_section(
            "Cross-Pillar Diagnostics",
            "Composites that read across pillars.",
            cross_codes, latest, history,
        )
        + render_section(
            "Risk Outputs",
            "Model outputs derived from the full pillar set.",
            extra_codes, latest, history,
        )
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>LHM Nowcast Dashboard · {run_date}</title>
<meta http-equiv="refresh" content="900">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@600;700&family=Inter:wght@400;500;600&family=Source+Code+Pro:wght@400;600&display=swap" rel="stylesheet">
<style>
  :root{{
    --ocean:{OCEAN}; --dusk:{DUSK}; --sky:{SKY}; --sea:{SEA}; --venus:{VENUS};
    --doldrums:{DOLDRUMS}; --starboard:{STARBOARD}; --port:{PORT}; --fog:{FOG};
    --ink:{INK}; --paper:{PAPER};
  }}
  *{{box-sizing:border-box;}}
  html,body{{background:var(--paper); color:var(--ink); margin:0; padding:0; font-family:'Inter', sans-serif; font-size:14px; line-height:1.55;}}
  .wrap{{max-width:1280px; margin:0 auto; padding:24px 28px 56px;}}
  .accent-bar{{display:flex; height:5px; width:100%; margin-bottom:18px;}}
  .accent-bar .ocean{{flex:2; background:var(--ocean);}}
  .accent-bar .dusk{{flex:1; background:var(--dusk);}}
  .header{{display:flex; align-items:flex-end; justify-content:space-between; margin-bottom:8px; flex-wrap:wrap; gap:12px;}}
  .header-left .kicker{{font-family:'Source Code Pro', monospace; font-size:11px; letter-spacing:0.12em; color:var(--ocean); text-transform:uppercase; font-weight:600; margin-bottom:4px;}}
  .header-left h1{{font-family:'Montserrat', sans-serif; font-weight:700; font-size:30px; margin:0; letter-spacing:-0.01em;}}
  .header-right{{text-align:right; font-family:'Source Code Pro', monospace; font-size:11px; color:var(--doldrums);}}
  .header-right .latest-stamp{{font-size:14px; color:var(--ink); font-weight:600;}}
  .pact{{font-size:13px; color:var(--doldrums); margin:8px 0 24px; max-width:780px;}}

  /* Master tiles row */
  .master-row{{display:grid; grid-template-columns:repeat(4, 1fr); gap:14px; margin-bottom:28px;}}
  .master-tile{{border:1px solid var(--fog); border-radius:10px; padding:14px 16px; background:var(--paper); position:relative; overflow:hidden;}}
  .master-tile-row{{display:flex; align-items:center; justify-content:space-between; margin-bottom:6px;}}
  .master-tile-name{{font-family:'Montserrat', sans-serif; font-weight:700; font-size:13px;}}
  .master-tile-tag{{font-family:'Source Code Pro', monospace; font-size:10px; color:var(--doldrums); text-transform:uppercase; letter-spacing:0.05em;}}
  .master-tile-value{{font-family:'Source Code Pro', monospace; font-weight:600; font-size:30px; margin:6px 0 8px; letter-spacing:-0.01em;}}
  .master-tile-status{{display:inline-block; padding:3px 10px; border-radius:11px; font-family:'Source Code Pro', monospace; font-size:11px; font-weight:600; letter-spacing:0.04em; color:#fff;}}
  .master-tile-spark{{margin-top:8px;}}

  /* Pillar heatmap */
  .pillar-heatmap{{display:grid; grid-template-columns:repeat(12, 1fr); gap:6px; margin-bottom:28px; padding:14px; border:1px solid var(--fog); border-radius:10px; background:#fafdff;}}
  .pillar-cell{{display:flex; flex-direction:column; align-items:center; gap:4px; padding:4px;}}
  .pillar-num{{font-family:'Source Code Pro', monospace; font-size:10px; color:var(--doldrums); font-weight:600;}}
  .pillar-dot{{width:36px; height:36px; border-radius:50%; box-shadow:0 0 0 1px rgba(0,0,0,0.04);}}
  .pillar-name{{font-family:'Inter', sans-serif; font-size:11px; font-weight:600; text-align:center;}}
  .pillar-z{{font-family:'Source Code Pro', monospace; font-size:10px; color:var(--doldrums);}}

  /* Section */
  .section{{margin-bottom:32px;}}
  .section-title{{font-family:'Montserrat', sans-serif; font-weight:700; font-size:18px; margin:0 0 4px; letter-spacing:-0.005em;}}
  .section-subtitle{{font-family:'Source Code Pro', monospace; font-size:11px; color:var(--doldrums); text-transform:uppercase; letter-spacing:0.05em; margin-bottom:12px;}}

  /* Indicator cards */
  .card-grid{{display:grid; grid-template-columns:repeat(auto-fill, minmax(220px, 1fr)); gap:12px;}}
  .card{{border:1px solid var(--fog); border-radius:8px; padding:11px 13px; background:var(--paper);}}
  .card-head{{display:flex; justify-content:space-between; align-items:baseline; margin-bottom:4px; gap:8px;}}
  .card-name{{font-family:'Montserrat', sans-serif; font-weight:600; font-size:13px; line-height:1.2;}}
  .card-pillar{{font-family:'Source Code Pro', monospace; font-size:9.5px; color:var(--doldrums); text-transform:uppercase; letter-spacing:0.04em; white-space:nowrap;}}
  .card-value{{font-family:'Source Code Pro', monospace; font-weight:600; font-size:22px; margin:2px 0 6px; letter-spacing:-0.01em;}}
  .card-status-row{{display:flex; justify-content:space-between; align-items:center;}}
  .card-status{{display:inline-block; padding:2px 8px; border-radius:10px; font-family:'Source Code Pro', monospace; font-size:9.5px; font-weight:600; letter-spacing:0.04em; color:#fff; max-width:120px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;}}

  /* Footer */
  .footer{{margin-top:36px; padding-top:14px; border-top:1px solid var(--fog); color:var(--doldrums); font-size:11px; font-family:'Source Code Pro', monospace; display:flex; justify-content:space-between;}}
  .footer a{{color:var(--ocean); text-decoration:none;}}

  @media (max-width:900px) {{
    .master-row{{grid-template-columns:repeat(2, 1fr);}}
    .pillar-heatmap{{grid-template-columns:repeat(6, 1fr);}}
  }}
</style>
</head>
<body>
<div class="wrap">

  <div class="accent-bar"><div class="ocean"></div><div class="dusk"></div></div>
  <div class="header">
    <div class="header-left">
      <div class="kicker">LIGHTHOUSE MACRO · NOWCAST DASHBOARD</div>
      <h1>The framework, live.</h1>
    </div>
    <div class="header-right">
      <div>Page rendered</div>
      <div class="latest-stamp">{timestamp}</div>
      <div>Indicator stamps as of {run_date or "—"}</div>
    </div>
  </div>
  <p class="pact">Every indicator below carries a current reading. No NaN. No fake-fresh zero. When official inputs are between releases, a daily proxy stands in. When that proxy is between releases, the next tier does. The confidence band widens with each tier down. The framework always has a read.</p>

  <h2 class="section-title">Master readings</h2>
  <div class="section-subtitle">Read these first.</div>
  <div class="master-row">
    {master_tiles}
  </div>

  <h2 class="section-title">The Diagnostic Dozen</h2>
  <div class="section-subtitle">Twelve pillars. Color = current pillar-composite z-score.</div>
  {pillar_heatmap}

  {sections}

  <div class="footer">
    <span>Lighthouse Macro · Nowcast Dashboard · auto-refreshes every 15 minutes</span>
    <span><a href="https://lighthousemacro.com">Lighthouse Macro</a> · <a href="https://research.lighthousemacro.com">Research</a> · <a href="https://x.com/LHMacro">@LHMacro</a></span>
  </div>

</div>
</body>
</html>
"""


def write_dashboard(html: str) -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(html)


def open_in_browser() -> None:
    try:
        subprocess.run(["open", str(OUTPUT_PATH)], check=False)
    except Exception:
        pass


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--no-open", action="store_true", help="Skip opening in browser")
    args = p.parse_args()

    latest, history, run_date = fetch_state()
    html = render_dashboard(latest, history, run_date)
    write_dashboard(html)
    print(f"Dashboard written to {OUTPUT_PATH}")
    if not args.no_open:
        open_in_browser()


if __name__ == "__main__":
    sys.exit(main() or 0)
