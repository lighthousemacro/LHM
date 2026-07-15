"""
LHM branded table renderer — for the Telegram bot's /scan (and any ranked list).

Tables in LHM surfaces are ALWAYS a styled PNG, never markdown. This renders a
ranked scan through the LHM lens (Price vs 200d, Relative trend vs SPY, Z-RoC,
setup, binding stop) in the house style established by scan_visualizer.py:
hand-placed cells, Ocean header + underline, alternating row shading, regime
coloring, wrapped in the canonical brand frame.

    from lhm_table import build_scan_table
    rows = [
      {"ticker":"NVDA","last":205.10,"vs200":11.4,"rs":"MIXED",
       "zroc":-0.1,"setup":"Breakout 7/10","stop":"184 (200d)"},
      ...
    ]
    png = build_scan_table(rows, subtitle="Watchlist · ranked by LHM setup")

Coloring is semantic: RS LEADING=Starboard, LAGGING=Port, MIXED=Doldrums;
below-200d and Z-RoC<-1.0 go Port. Regime colors are used only for regime
meaning, per the brand rule.
"""
from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # headless-safe
from matplotlib.patches import Rectangle

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lhm_chart_template import COLORS, set_theme, new_fig, brand_fig, save_fig  # noqa: E402

DEFAULT_OUT_DIR = Path("/Users/bob/LHM/Outputs/lhmbot")
DARK = "#1a1a1a"

# (header, key, width). Widths sum < 1; a 0.03 left margin is added.
COLUMNS = [
    ("Ticker", "ticker", 0.12),
    ("Last", "last", 0.12),
    ("vs 200d", "vs200", 0.13),
    ("RS vs SPY", "rs", 0.16),
    ("Z-RoC", "zroc", 0.11),
    ("Setup", "setup", 0.18),
    ("Stop", "stop", 0.16),
]


def _rs_color(rs: str) -> str:
    r = str(rs).upper()
    if r.startswith("LEAD"):
        return COLORS["starboard"]
    if r.startswith("LAG"):
        return COLORS["port"]
    return COLORS["doldrums"]


def _fmt_cell(key: str, row: dict) -> tuple[str, str, str]:
    """Return (text, color, weight) for a cell."""
    v = row.get(key)
    if key == "ticker":
        return str(v), COLORS["ocean"], "bold"
    if key == "last":
        return (f"{v:,.2f}" if isinstance(v, (int, float)) else str(v or "—")), DARK, "normal"
    if key == "vs200":
        if isinstance(v, (int, float)):
            return f"{v:+.1f}%", (COLORS["ocean"] if v >= 0 else COLORS["port"]), "normal"
        return str(v or "—"), DARK, "normal"
    if key == "rs":
        return str(v or "—").upper(), _rs_color(v), "bold"
    if key == "zroc":
        if isinstance(v, (int, float)):
            return f"{v:+.2f}", (COLORS["port"] if v < -1.0 else DARK), "normal"
        return str(v or "—"), DARK, "normal"
    if key == "stop":
        return str(v or "—"), COLORS["doldrums"], "normal"
    # setup
    return str(v or "—"), DARK, "normal"


def build_scan_table(rows: list[dict], title: str = "LHM Scan",
                     subtitle: str | None = None,
                     source: str = "Price, relative strength & momentum vs SPY",
                     out_path: str | Path | None = None,
                     max_rows: int = 20) -> str:
    """Render a ranked scan as a branded PNG. Returns the file path.

    Each row dict: ticker, last, vs200 (% vs 200d), rs (LEADING/LAGGING/MIXED),
    zroc (float), setup (str), stop (str). Missing keys render as "—"."""
    if not rows:
        raise ValueError("build_scan_table: no rows")
    rows = rows[:max_rows]
    n = len(rows)

    set_theme("white")
    fig, ax = new_fig(figsize=(15, max(4.5, n * 0.42 + 2.2)))
    ax.set_axis_off()

    widths = [w for _, _, w in COLUMNS]
    import numpy as np
    col_x = np.cumsum([0.03] + widths[:-1])

    # Header
    y_top = 0.93
    for (hdr, _, w), x in zip(COLUMNS, col_x):
        ax.text(x + w / 2, y_top, hdr, ha="center", va="center",
                fontsize=11, fontweight="bold", color=COLORS["ocean"],
                transform=ax.transAxes)
    ax.plot([0.03, 0.99], [y_top - 0.03, y_top - 0.03],
            color=COLORS["ocean"], linewidth=1.2, transform=ax.transAxes)

    row_h = 0.82 / n
    for i, row in enumerate(rows):
        y = y_top - 0.07 - i * row_h
        if i % 2 == 1:
            ax.add_patch(Rectangle((0.02, y - row_h * 0.45), 0.97, row_h * 0.9,
                                   color="#f5f8fa", zorder=0, transform=ax.transAxes))
        for (_, key, w), x in zip(COLUMNS, col_x):
            text, color, weight = _fmt_cell(key, row)
            ax.text(x + w / 2, y, text, ha="center", va="center",
                    fontsize=10, fontweight=weight, color=color,
                    transform=ax.transAxes)

    brand_fig(fig, title=title,
              subtitle=subtitle or "Ranked through the LHM technical hierarchy",
              source=source, data_date=datetime.now())

    out_path = Path(out_path) if out_path else (DEFAULT_OUT_DIR / "scan_table.png")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    return save_fig(fig, str(out_path))


if __name__ == "__main__":
    # Smoke test with REAL data — compute a mini-scan for a few names vs SPY.
    # No synthetic data: prices and the SPY benchmark come from yfinance.
    import yfinance as yf
    import pandas as pd
    sys.path.insert(0, "/Users/bob/LHM/Scripts/chart_generation")
    from lhm_tape_read import compute_z_roc

    syms = sys.argv[1:] or ["NVDA", "AAPL", "MSFT", "XLE", "TLT"]
    bench = yf.download("SPY", period="3y", interval="1d", progress=False, auto_adjust=True)
    if isinstance(bench.columns, pd.MultiIndex):
        bench.columns = [c[0] for c in bench.columns]
    bclose = bench["Close"].dropna()

    rows = []
    for s in syms:
        d = yf.download(s, period="3y", interval="1d", progress=False, auto_adjust=True)
        if isinstance(d.columns, pd.MultiIndex):
            d.columns = [c[0] for c in d.columns]
        px = d["Close"].dropna()
        if len(px) < 200:
            continue
        last = float(px.iloc[-1])
        sma200 = float(px.rolling(200).mean().iloc[-1])
        vs200 = (last / sma200 - 1) * 100
        z = compute_z_roc(px)
        zroc = float(z.iloc[-1]) if len(z) else float("nan")
        common = px.index.intersection(bclose.index)
        rs = (px.loc[common] / bclose.loc[common]) * 100
        rs63, rs252 = rs.rolling(63).mean().iloc[-1], rs.rolling(252).mean().iloc[-1]
        regime = ("LEADING" if rs.iloc[-1] > rs63 and rs.iloc[-1] > rs252
                  else "LAGGING" if rs.iloc[-1] < rs63 and rs.iloc[-1] < rs252 else "MIXED")
        rows.append({"ticker": s, "last": last, "vs200": vs200, "rs": regime,
                     "zroc": zroc, "setup": "trend" if vs200 > 0 else "below trend",
                     "stop": f"{sma200:,.0f} (200d)"})
    out = build_scan_table(rows, subtitle="Smoke test · real data vs SPY",
                           out_path=str(DEFAULT_OUT_DIR / "scan_smoketest.png"))
    import os
    print("WROTE", out, os.path.getsize(out), "bytes")
