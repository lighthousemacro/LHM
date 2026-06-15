#!/usr/bin/env python3
"""
ALLOCATION-IMPACT OVERLAY CHARTS (validated 2026-06-15)

One branded overlay per validated allocation composite: the standardized macro
signal (Ocean, left axis) against the asset/curve/rotation it predicts (Dusk,
right axis), full history, NBER recessions shaded. The visual proof that the
macro economy drives asset prices through specific channels.

Run: PYTHONPATH=/Users/bob/LHM /opt/homebrew/bin/python3 \
       Scripts/chart_generation/allocation_overlay_charts.py
"""
import sqlite3
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import pandas as pd

sys.path.insert(0, "/Users/bob/LHM/Scripts/chart_generation")
import lhm_chart_template as T

DB = "/Users/bob/LHM/Data/databases/Lighthouse_Master.db"
OUT = Path("/Users/bob/LHM/Outputs/allocation_charts")
OUT.mkdir(parents=True, exist_ok=True)


def load_index(conn, idx):
    d = pd.read_sql("SELECT date, value FROM lighthouse_indices WHERE index_id=? "
                    "ORDER BY date", conn, params=(idx,), parse_dates=["date"])
    return d.set_index("date")["value"] if not d.empty else pd.Series(dtype=float)


def load_obs(conn, sid):
    d = pd.read_sql("SELECT date, value FROM observations WHERE series_id=? "
                    "AND value IS NOT NULL ORDER BY date", conn, params=(sid,),
                    parse_dates=["date"])
    return d.set_index("date")["value"] if not d.empty else pd.Series(dtype=float)


def ratio(conn, a, b):
    pa, pb = load_obs(conn, a), load_obs(conn, b)
    idx = pa.index.union(pb.index)
    return (pa.reindex(idx).ffill() / pb.reindex(idx).ffill()).dropna()


# (composite, target_series_fn, target_label, title, subtitle)
def specs(conn):
    return [
        ("ALLOC_CURVE_STEEPENER", load_obs(conn, "T10Y2Y"), "2s10s curve (10Y−2Y, %)",
         "Labor Stress Leads the Curve",
         "Labor-fragility composite (z) vs the 2s10s Treasury curve · validated OOS IC +0.27, 6-month lead"),
        ("ALLOC_CONS_ROTATION", ratio(conn, "XLY_Close", "XLP_Close"), "XLY / XLP ratio",
         "The Consumer Drives the Discretionary-vs-Staples Trade",
         "Consumer-income composite (z) vs discretionary/staples rotation · validated OOS IC 0.12, 3-month lead"),
        ("ALLOC_CYCLICAL_DEFENSIVE", ratio(conn, "XLI_Close", "XLP_Close"), "XLI / XLP ratio",
         "Real-Economy Breadth Leads the Cyclical-vs-Defensive Rotation",
         "Cyclical-breadth composite (z) vs cyclicals/defensives · validated OOS IC +0.30, 3-month lead"),
        ("ALLOC_ENERGY_MOMENTUM", ratio(conn, "XLE_Close", "SPY_Close"), "XLE / SPY ratio",
         "Energy Inflation Leads Energy Equities",
         "Oil + energy-inflation composite (z) vs energy-vs-market · validated OOS IC +0.21, 3-month lead"),
        ("ALLOC_REALYIELD_GOLD", load_obs(conn, "GLD_Close"), "GLD ($)",
         "Real Yields Drive Gold",
         "Real-yield composite (z, inverted) vs gold · OOS IC +0.15 (provisional), 6-month lead"),
        ("ALLOC_DOLLAR_EM", load_obs(conn, "EEM_Close"), "EEM ($)",
         "The Dollar Sets the Emerging-Market Trade",
         "Dollar-stress composite (z) vs EM equities · OOS IC −0.15 (provisional), 6-month lead"),
    ]


def make_chart(name, comp, tgt, tgt_label, title, subtitle):
    comp, tgt = comp.dropna(), tgt.dropna()
    if comp.empty or tgt.empty:
        print(f"   [skip] {name}: empty"); return None
    start = max(comp.index.min(), tgt.index.min())
    comp, tgt = comp[comp.index >= start], tgt[tgt.index >= start]
    # smooth the daily-FF composite lightly for readability (monthly cadence)
    comp_s = comp.resample("W").last().rolling(4, min_periods=1).mean()

    T.set_theme("white")
    fig, ax1 = T.new_fig(figsize=(14, 7))
    ax2 = ax1.twinx()
    ax1.plot(comp_s.index, comp_s.values, color=T.COLORS["ocean"], lw=1.8,
             label="Macro signal (z, left)")
    ax1.axhline(0, color=T.COLORS["fog"], lw=0.8, ls="--")
    ax2.plot(tgt.index, tgt.values, color=T.COLORS["dusk"], lw=1.4,
             label=tgt_label + " (right)")
    T.style_dual_ax(ax1, ax2, T.COLORS["ocean"], T.COLORS["dusk"])
    T.add_recessions(ax1, start_date=start)
    T.set_xlim_to_data(ax1, comp_s.index, tgt.index)
    try:
        T.align_yaxis_smart(ax1, ax2, comp_s, tgt)
    except Exception:
        pass
    T.add_smart_legend(ax1)
    T.brand_fig(fig, title, subtitle=subtitle,
                source="FRED, BLS, Census, Treasury, market data")
    p = OUT / f"{name}.png"
    T.save_fig(fig, str(p))
    print(f"   [ok] {p.name}")
    return p


def main():
    conn = sqlite3.connect(DB)
    made = []
    for name, tgt, tgt_label, title, subtitle in specs(conn):
        comp = load_index(conn, name)
        p = make_chart(name, comp, tgt, tgt_label, title, subtitle)
        if p:
            made.append(str(p))
    conn.close()
    print(f"\nGenerated {len(made)} charts in {OUT}")
    for m in made:
        print(" ", m)


if __name__ == "__main__":
    main()
