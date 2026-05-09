#!/usr/bin/env python3
"""
Pillar Rebuild v5 — Asset-Predictive Grid (per-target re-optimized)
====================================================================
For each pillar (using EXPANDED_PILLAR_SPECS), optimize composite weights
SEPARATELY against each single-asset forward target. This is the missing
third role from the audit's predictive grid — that grid evaluated single-
target weights against other assets, but didn't re-optimize per target.

The point: a pillar's basket can produce different optimal composites for
different forward asset targets. PCI tuned for 2y yields ≠ PCI tuned for SPX.

Run with v3/v4 walk-forward methodology (5-fold TimeSeriesSplit + signed IC).

Author: Lighthouse Macro
Date: 2026-05-08
"""

from __future__ import annotations

import json
import sqlite3
import sys
import warnings
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats
from scipy.optimize import minimize
from sklearn.model_selection import TimeSeriesSplit

warnings.filterwarnings("ignore")

sys.path.insert(0, "/Users/bob/LHM/Scripts/backtest")
from pillar_weight_optimization import DB_PATH, build_components, load_obs  # noqa: E402
from pillar_specs_v2 import EXPANDED_PILLAR_SPECS, DISPLAY_NAMES  # noqa: E402

OUTPUT_DIR = Path("/Users/bob/LHM/Outputs/mri_optimization")
OUT_JSON = OUTPUT_DIR / "pillar_registry_v5_assets.json"
OUT_MD = OUTPUT_DIR / "pillar_registry_v5_assets_summary.md"

BOUNDS = (0.02, 0.40)
N_RESTARTS = 12
N_FOLDS = 5
MIN_FOLD_OBS = 250

# ---- Asset-predictive targets (single asset, multiple horizons) ----
ASSET_TARGETS = [
    # (label, series_id, horizon, mode)
    ("spx_21d",      "SPY_Close",     21,  "log_fwd_return"),
    ("spx_63d",      "SPY_Close",     63,  "log_fwd_return"),
    ("spx_252d",     "SPY_Close",     252, "log_fwd_return"),
    ("vix_21d",      "VIXCLS",        21,  "log_fwd_return"),
    ("vix_63d",      "VIXCLS",        63,  "log_fwd_return"),
    ("hyoas_63d",    "BAMLH0A0HYM2",  63,  "fwd_max_change"),
    ("hyoas_126d",   "BAMLH0A0HYM2",  126, "fwd_max_change"),
    ("igoas_63d",    "BAMLC0A0CM",    63,  "fwd_max_change"),
    ("dgs2_252d",    "DGS2",          252, "delta"),
    ("dgs10_252d",   "DGS10",         252, "delta"),
    ("t10y2y_252d",  "T10Y2Y",        252, "delta"),
    ("dxy_252d",     "DTWEXBGS",      252, "log_fwd_return"),
    ("usdjpy_252d",  "DEXJPUS",       252, "log_fwd_return"),
]


def build_target(conn, sid, h, mode):
    s = load_obs(conn, sid)
    if s.empty:
        return None
    s_d = s.resample("D").ffill()
    if mode == "delta":
        return s_d.shift(-h) - s_d
    if mode == "log_fwd_return":
        return np.log(s_d.shift(-h) / s_d) * 100
    if mode == "fwd_max_change":
        out = pd.Series(index=s_d.index, dtype=float)
        arr = s_d.values
        for i in range(len(arr) - h):
            out.iloc[i] = arr[i:i+h+1].max() - arr[i]
        return out
    return s_d.shift(-h) - s_d


def neg_abs_ic(w, z, target):
    w = np.abs(w)
    if w.sum() <= 0:
        return 1e6
    w = w / w.sum()
    composite = z.values @ w
    df = pd.DataFrame({"sig": composite, "fwd": target.values}, index=z.index).dropna()
    if len(df) < MIN_FOLD_OBS:
        return 1e6
    ic, _ = stats.spearmanr(df["sig"], df["fwd"])
    if np.isnan(ic):
        return 1e6
    return -abs(ic)


def optimize_weights(z, target, n_restarts=N_RESTARTS, bounds=BOUNDS):
    n = z.shape[1]
    if n < 2:
        return None
    bnds = [bounds] * n
    cons = [{"type": "eq", "fun": lambda w: np.sum(np.abs(w)) - 1.0}]
    rng = np.random.RandomState(42)
    starts = [np.ones(n) / n]
    for _ in range(n_restarts - 1):
        w0 = rng.dirichlet(np.ones(n))
        w0 = np.clip(w0, bounds[0], bounds[1])
        w0 = w0 / w0.sum()
        starts.append(w0)
    best, best_obj = None, 1e6
    for w0 in starts:
        try:
            res = minimize(neg_abs_ic, w0, args=(z, target), method="SLSQP",
                           bounds=bnds, constraints=cons,
                           options={"maxiter": 200, "ftol": 1e-9})
            if res.fun < best_obj:
                best_obj = res.fun
                best = res
        except Exception:
            pass
    if best is None or best_obj > 1e5:
        return None
    w = np.abs(best.x) / np.abs(best.x).sum()
    return {c: float(w[i]) for i, c in enumerate(z.columns)}


def evaluate_signed_ic(z, target, weights):
    cols = list(z.columns)
    w_arr = np.array([weights[c] for c in cols]) / sum(weights.values())
    composite = z.values @ w_arr
    df = pd.DataFrame({"sig": composite, "fwd": target}, index=z.index).dropna()
    if len(df) < 50:
        return None
    ic, _ = stats.spearmanr(df["sig"], df["fwd"])
    return float(ic) if not np.isnan(ic) else None


def walk_forward(z, target, n_folds=N_FOLDS):
    aligned = z.join(target.rename("fwd")).dropna()
    if len(aligned) < MIN_FOLD_OBS * (n_folds + 1):
        return None, len(aligned)
    z_a = aligned[z.columns]
    fwd_a = aligned["fwd"]
    tscv = TimeSeriesSplit(n_splits=n_folds)
    fold_ics = []
    for is_idx, oos_idx in tscv.split(z_a):
        z_is = z_a.iloc[is_idx]
        fwd_is = fwd_a.iloc[is_idx]
        z_oos = z_a.iloc[oos_idx]
        fwd_oos = fwd_a.iloc[oos_idx]
        if len(z_is) < MIN_FOLD_OBS or len(z_oos) < MIN_FOLD_OBS:
            continue
        weights = optimize_weights(z_is, fwd_is, n_restarts=8)
        if weights is None:
            continue
        ic = evaluate_signed_ic(z_oos, fwd_oos, weights)
        if ic is not None:
            fold_ics.append(ic)
    if not fold_ics:
        return None, len(aligned)
    arr = np.array(fold_ics)
    n_pos = sum(1 for x in arr if x > 0)
    dominant = max(n_pos, len(arr) - n_pos) / len(arr)
    return {
        "n_folds": len(arr),
        "oos_ic_mean": float(arr.mean()),
        "oos_abs_ic_mean": float(np.abs(arr).mean()),
        "oos_dominant_pct": float(dominant),
        "fold_ics": [float(x) for x in arr],
    }, len(aligned)


def main():
    print("=" * 80)
    print("PILLAR REBUILD v5 — ASSET-PREDICTIVE GRID")
    print(f"Run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    pillars = list(EXPANDED_PILLAR_SPECS.keys())
    print(f"Pillars: {len(pillars)}, asset targets: {len(ASSET_TARGETS)}")
    print(f"Total cells: {len(pillars) * len(ASSET_TARGETS)}")
    print("=" * 80)

    conn = sqlite3.connect(DB_PATH)
    out: dict[str, Any] = {
        "run_date": datetime.now().isoformat(),
        "methodology": "v2 walk-forward, |IC| optimization with per-target re-optimization, signed-IC OOS",
        "display_names": DISPLAY_NAMES,
        "cells": {},
    }

    for pillar in pillars:
        spec = EXPANDED_PILLAR_SPECS[pillar]
        z, _ = build_components(conn, spec)
        if z.empty:
            continue
        name = DISPLAY_NAMES.get(pillar, pillar)
        print(f"\n{name} ({pillar})")
        for label, sid, h, mode in ASSET_TARGETS:
            target = build_target(conn, sid, h, mode)
            if target is None or target.dropna().empty:
                continue
            wf, n_aligned = walk_forward(z, target)
            cell_id = f"{pillar}__{label}"
            if not wf:
                out["cells"][cell_id] = {"pillar": pillar, "target": label, "status": "insufficient_data"}
                print(f"  {label:<14} [insufficient]")
                continue
            # Full-sample re-opt for production weights
            aligned = z.join(target.rename("fwd")).dropna()
            weights = optimize_weights(aligned[z.columns], aligned["fwd"], n_restarts=N_RESTARTS)
            full_ic = evaluate_signed_ic(aligned[z.columns], aligned["fwd"], weights) if weights else None
            real = wf["oos_dominant_pct"] >= 0.8 and abs(wf["oos_ic_mean"]) >= 0.10
            out["cells"][cell_id] = {
                "pillar": pillar,
                "target": label,
                "target_spec": (sid, h, mode),
                "n_aligned": n_aligned,
                "full_ic": full_ic,
                "weights": weights,
                "walk_forward": wf,
                "signal_real": real,
                "status": "ok",
            }
            tag = "REAL" if real else "    "
            print(f"  {label:<14} WF mean {wf['oos_ic_mean']:>+.3f}  |IC| {wf['oos_abs_ic_mean']:>.3f}  Dom {wf['oos_dominant_pct']:>4.0%}  {tag}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(out, indent=2, default=str))
    print(f"\nOutput JSON: {OUT_JSON}")
    write_md(out)
    print(f"Output MD:   {OUT_MD}")


def write_md(out):
    cells = out["cells"]
    pillars = sorted({v["pillar"] for v in cells.values()})
    targets = [t[0] for t in ASSET_TARGETS]
    lines = [
        "# Pillar Asset-Predictive Grid (v5)",
        "",
        f"_Generated {out['run_date']}_",
        f"_{out['methodology']}_",
        "",
        "Walk-forward mean OOS IC per (pillar × asset target). **Bold** = signal_real (Dom%≥80% AND |WF mean|≥0.10).",
        "Each cell uses weights re-optimized per target — different from the single-target collapse in pillar_multiasset_optimization.json.",
        "",
        "| Pillar | " + " | ".join(targets) + " |",
        "|---|" + "|".join(["---:" for _ in targets]) + "|",
    ]
    for p in pillars:
        name = DISPLAY_NAMES.get(p, p)
        cells_row = []
        for t in targets:
            cell_id = f"{p}__{t}"
            v = cells.get(cell_id, {})
            if v.get("status") != "ok":
                cells_row.append("—")
                continue
            mean = v["walk_forward"]["oos_ic_mean"]
            cells_row.append(f"**{mean:+.2f}**" if v.get("signal_real") else f"{mean:+.2f}")
        lines.append(f"| {name} | " + " | ".join(cells_row) + " |")

    # Top signals
    real_cells = [v for v in cells.values() if v.get("signal_real")]
    real_sorted = sorted(real_cells, key=lambda x: -abs(x["walk_forward"]["oos_ic_mean"]))[:30]
    lines.append("")
    lines.append("## Top 30 real asset-predictive signals")
    lines.append("")
    lines.append("| Pillar | Target | WF mean | \\|IC\\| | Dom% |")
    lines.append("|---|---|---:|---:|---:|")
    for v in real_sorted:
        wf = v["walk_forward"]
        name = DISPLAY_NAMES.get(v["pillar"], v["pillar"])
        lines.append(f"| {name} | {v['target']} | {wf['oos_ic_mean']:+.3f} | {wf['oos_abs_ic_mean']:.3f} | {wf['oos_dominant_pct']:.0%} |")
    OUT_MD.write_text("\n".join(lines))


if __name__ == "__main__":
    main()
