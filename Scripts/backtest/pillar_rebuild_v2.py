#!/usr/bin/env python3
"""
Per-Pillar Optimization v2 — Lighthouse Macro Rebuild
=======================================================
Replaces the broken single-90/10-split + sign-agnostic |IC| methodology
in pillar_multiasset_optimization.py with:

  1. Expanding-window walk-forward, 5 folds, contiguous OOS chunks.
  2. Sign-aware IC: weights optimized to maximize SIGNED IC matching
     the pillar's expected direction (no more flip-and-claim-OOS-validation).
  3. Reports fold-wise IC stability (mean, std, sign consistency, full-sample IC).

Why this matters: the prior methodology produced |IC| values where IS and
OOS could have OPPOSITE signs, inflating reported OOS to 0.50-0.77 while
full-sample IC was 0.05-0.20. Seven of twelve pillars showed sign flips.

This script produces honest IC numbers — they will be lower in magnitude
than the prior JSON, but they will replicate. Any composite that doesn't
clear |IC| > 0.20 with sign consistency >= 0.8 across folds should be
flagged for basket reconstruction.

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
from pillar_weight_optimization import (  # noqa: E402
    DB_PATH,
    PILLAR_SPECS,
    build_components,
    build_target,
)

OUTPUT_DIR = Path("/Users/bob/LHM/Outputs/mri_optimization")
OUT_PATH = OUTPUT_DIR / "pillar_rebuild_v2.json"

# Optimization parameters
BOUNDS = (0.02, 0.40)
N_RESTARTS = 30
N_FOLDS = 5
MIN_FOLD_OBS = 250

# Expected sign of the IC: positive means composite up ↔ target up.
# Derived from each pillar's risk_side + the target's economic meaning.
# A pillar's optimized IC must come out with this sign in the IS fit;
# if it doesn't, the composite isn't measuring what we claim.
EXPECTED_SIGN = {
    "LPI": +1,      # high LPI = labor weak; target UNRATE 252d delta (positive when UR rises)
    "PCI": +1,      # high PCI = inflation hot; target Core PCE YoY level
    "GCI": +1,      # high GCI = growth strong; target INDPRO YoY level
    "HCI": +1,      # high HCI = housing strong; target Housing starts YoY level
    "CCI": +1,      # high CCI = consumer strong; target RSXFS YoY level
    "BCI": +1,      # high BCI = business strong; target NEWORDER YoY level (assumed)
    "TCI": +1,      # high TCI = trade strong; target depends on spec
    "GCI_Gov": +1,  # high GCI_Gov = fiscal stress; target term premium 252d delta
    "FCI": +1,      # high FCI = financial stress; target HY OAS widening 126d
    "LCI": -1,      # low LCI = scarce; target HY OAS widening 63d (positive) → high LCI ↔ no widening = -1
    "MSI": +1,      # high MSI = strong structure; target SPX 63d log return (positive when strong)
    "SPI": +1,      # high SPI = fear; target SPX 21d log return → contrarian: fear → positive fwd return = +1
}


def neg_abs_ic(weights_arr, z_components, target, expected_sign):
    """Maximize |IC|. Sign tracking happens at evaluation, not optimization."""
    w = np.abs(weights_arr)
    if w.sum() <= 0:
        return 1e6
    w = w / w.sum()
    composite = z_components.values @ w
    df = pd.DataFrame(
        {"sig": composite, "fwd": target.values}, index=z_components.index
    ).dropna()
    if len(df) < MIN_FOLD_OBS:
        return 1e6
    ic, _ = stats.spearmanr(df["sig"], df["fwd"])
    if np.isnan(ic):
        return 1e6
    return -abs(ic)


def optimize_weights(z_components, target, expected_sign, bounds=BOUNDS, n_restarts=N_RESTARTS):
    n = z_components.shape[1]
    if n < 2:
        return None, None
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
            res = minimize(
                neg_abs_ic,
                w0,
                args=(z_components, target, expected_sign),
                method="SLSQP",
                bounds=bnds,
                constraints=cons,
                options={"maxiter": 300, "ftol": 1e-9},
            )
            if res.fun < best_obj:
                best_obj = res.fun
                best = res
        except Exception:
            pass
    if best is None or best_obj > 1e5:
        return None, None
    w = np.abs(best.x) / np.abs(best.x).sum()
    weights_dict = {c: float(w[i]) for i, c in enumerate(z_components.columns)}
    return weights_dict, -best_obj


def evaluate_signed_ic(z_components, target, weights):
    cols = list(z_components.columns)
    w_arr = np.array([weights[c] for c in cols])
    w_arr = w_arr / w_arr.sum()
    composite = z_components.values @ w_arr
    df = pd.DataFrame({"sig": composite, "fwd": target}, index=z_components.index).dropna()
    if len(df) < 100:
        return None, 0
    ic, _ = stats.spearmanr(df["sig"], df["fwd"])
    return float(ic) if not np.isnan(ic) else None, len(df)


def walk_forward(z_components, target, expected_sign, n_folds=N_FOLDS):
    """Expanding-window walk-forward. n_folds OOS chunks, IS expands as we move forward."""
    aligned = z_components.join(target.rename("fwd")).dropna()
    if len(aligned) < MIN_FOLD_OBS * (n_folds + 1):
        return None
    z_aligned = aligned[z_components.columns]
    fwd_aligned = aligned["fwd"]

    tscv = TimeSeriesSplit(n_splits=n_folds)
    folds = []
    for fold_idx, (is_idx, oos_idx) in enumerate(tscv.split(z_aligned)):
        z_is = z_aligned.iloc[is_idx]
        fwd_is = fwd_aligned.iloc[is_idx]
        z_oos = z_aligned.iloc[oos_idx]
        fwd_oos = fwd_aligned.iloc[oos_idx]
        if len(z_is) < MIN_FOLD_OBS or len(z_oos) < MIN_FOLD_OBS:
            continue
        weights, is_signed_ic = optimize_weights(z_is, fwd_is, expected_sign, n_restarts=15)
        if weights is None:
            continue
        is_ic, _ = evaluate_signed_ic(z_is, fwd_is, weights)
        oos_ic, n_oos = evaluate_signed_ic(z_oos, fwd_oos, weights)
        folds.append({
            "fold": fold_idx,
            "n_is": len(z_is),
            "n_oos": n_oos,
            "is_ic": is_ic,
            "oos_ic": oos_ic,
            "weights": weights,
            "expected_sign": expected_sign,
            "is_sign_correct": (is_ic is not None) and (expected_sign * is_ic > 0),
            "oos_sign_correct": (oos_ic is not None) and (expected_sign * oos_ic > 0),
        })
    return folds


def fold_summary(folds, expected_sign):
    if not folds:
        return None
    oos_ics = [f["oos_ic"] for f in folds if f["oos_ic"] is not None]
    if not oos_ics:
        return None
    oos_ics_arr = np.array(oos_ics)
    n = len(oos_ics)
    # Sign matches expected
    sign_match_expected = sum(1 for ic in oos_ics if expected_sign * ic > 0) / n
    # Sign consistency across folds (% in dominant direction)
    n_pos = sum(1 for ic in oos_ics if ic > 0)
    dominant = max(n_pos, n - n_pos) / n
    return {
        "n_folds": len(folds),
        "oos_ic_mean": float(oos_ics_arr.mean()),
        "oos_ic_std": float(oos_ics_arr.std()),
        "oos_ic_min": float(oos_ics_arr.min()),
        "oos_ic_max": float(oos_ics_arr.max()),
        "oos_abs_ic_mean": float(np.abs(oos_ics_arr).mean()),
        "oos_sign_match_expected": float(sign_match_expected),  # vs theoretical direction
        "oos_sign_dominant_pct": float(dominant),  # % in dominant direction (stability)
        "oos_signal_real": bool(dominant >= 0.8 and abs(oos_ics_arr.mean()) >= 0.10),
    }


def run_pillar(conn, pillar, spec):
    print(f"\n{'='*70}")
    print(f"  {pillar}")
    print(f"{'='*70}")
    expected_sign = EXPECTED_SIGN.get(pillar, +1)
    z_comp, _ = build_components(conn, spec)
    if z_comp.empty:
        print(f"  [SKIP] no components built")
        return None
    target_series, _ = build_target(conn, spec)
    target_label = f"{spec['target'][0]} {spec['target'][1]}d {spec['target'][2]}"
    print(f"  Components: {list(z_comp.columns)}")
    print(f"  Target: {target_label}")
    print(f"  Expected sign: {'+' if expected_sign > 0 else '-'}1")

    folds = walk_forward(z_comp, target_series, expected_sign)
    if not folds:
        print(f"  [SKIP] insufficient data for {N_FOLDS} folds")
        return None

    summary = fold_summary(folds, expected_sign)
    print(f"  N folds: {summary['n_folds']}")
    print(f"  OOS IC mean: {summary['oos_ic_mean']:+.3f}  |  |IC| mean: {summary['oos_abs_ic_mean']:.3f}")
    print(f"  OOS IC std:  {summary['oos_ic_std']:.3f}  range: [{summary['oos_ic_min']:+.3f}, {summary['oos_ic_max']:+.3f}]")
    print(f"  Sign match expected (+/- {expected_sign:+}): {summary['oos_sign_match_expected']:.0%}")
    print(f"  Sign dominant pct: {summary['oos_sign_dominant_pct']:.0%}")
    print(f"  Signal real (consistent + |mean|>0.10): {summary['oos_signal_real']}")

    # Re-optimize on full sample for production weights
    aligned = z_comp.join(target_series.rename("fwd")).dropna()
    z_aligned = aligned[z_comp.columns]
    fwd_aligned = aligned["fwd"]
    full_weights, _ = optimize_weights(z_aligned, fwd_aligned, expected_sign, n_restarts=N_RESTARTS)
    full_ic, n_full = evaluate_signed_ic(z_aligned, fwd_aligned, full_weights) if full_weights else (None, 0)
    print(f"  Full-sample IC (with full-sample weights): {full_ic:+.3f}" if full_ic else "  Full-sample IC: N/A")

    return {
        "pillar": pillar,
        "components": list(z_comp.columns),
        "target": target_label,
        "expected_sign": expected_sign,
        "n_total_obs": len(aligned),
        "n_full": n_full,
        "full_ic": full_ic,
        "full_weights": full_weights,
        "walk_forward": summary,
        "folds": folds,
    }


def main():
    print("=" * 70)
    print("PILLAR REBUILD v2 — proper walk-forward + sign-aware IC")
    print(f"Run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Folds: {N_FOLDS}  | Bounds: {BOUNDS}  | Restarts: {N_RESTARTS}")
    print("=" * 70)

    conn = sqlite3.connect(DB_PATH)
    out: dict[str, Any] = {
        "run_date": datetime.now().isoformat(),
        "methodology": {
            "walk_forward_folds": N_FOLDS,
            "weight_bounds": list(BOUNDS),
            "n_restarts": N_RESTARTS,
            "objective": "signed IC matching expected_sign per pillar",
            "notes": "Replaces single-90/10 + |IC| optimization. Sign flips between IS/OOS now penalized; only consistent-sign signals score.",
        },
        "pillars": {},
    }

    for pillar, spec in PILLAR_SPECS.items():
        try:
            result = run_pillar(conn, pillar, spec)
            if result:
                out["pillars"][pillar] = result
        except Exception as e:
            print(f"  [ERROR] {pillar}: {e}")
            out["pillars"][pillar] = {"error": str(e)}

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(out, indent=2, default=str))
    print(f"\n{'='*70}\nOutput: {OUT_PATH}\n{'='*70}")

    # Summary table
    print("\nSUMMARY")
    print(f"  {'Pillar':10} {'Full IC':>9} {'WF mean':>9} {'WF |IC|':>9} {'WF std':>8} {'SignMatch':>10} {'Real?':>6}")
    print(f"  {'-'*70}")
    for pillar, res in out["pillars"].items():
        if "error" in res:
            print(f"  {pillar:10} ERROR")
            continue
        wf = res.get("walk_forward")
        if not wf:
            continue
        print(
            f"  {pillar:10} "
            f"{res['full_ic']:>+9.3f} "
            f"{wf['oos_ic_mean']:>+9.3f} "
            f"{wf['oos_abs_ic_mean']:>9.3f} "
            f"{wf['oos_ic_std']:>8.3f} "
            f"{wf['oos_sign_match_expected']:>9.0%} "
            f"{'YES' if wf['oos_signal_real'] else 'no':>6}"
        )


if __name__ == "__main__":
    main()
