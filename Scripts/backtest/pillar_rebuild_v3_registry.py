#!/usr/bin/env python3
"""
Indicator Registry v3 — Multi-Role Optimization
================================================
Each pillar's component basket can feed multiple composites with role-specific
weights. The registry defines (basket, target, role, expected_sign) tuples;
each runs through the v2 walk-forward + signed-IC methodology.

Roles:
  - diagnostic         : concurrent r vs ground-truth reference (what is X right now)
  - asset_predictive   : forward IC vs single asset (X predicts SPX/DGS10/HY OAS)
  - relative_predictive: forward IC vs ratio target (X predicts SPY/TLT, HYG/LQD, etc.)

Output: Outputs/mri_optimization/pillar_registry_v3.json
        Outputs/mri_optimization/pillar_registry_v3_summary.md

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
    load_obs,
)

OUTPUT_DIR = Path("/Users/bob/LHM/Outputs/mri_optimization")
OUT_JSON = OUTPUT_DIR / "pillar_registry_v3.json"
OUT_MD = OUTPUT_DIR / "pillar_registry_v3_summary.md"

# Optimization parameters
BOUNDS = (0.02, 0.40)
N_RESTARTS = 15  # fewer restarts since we're running many cells
N_FOLDS = 5
MIN_FOLD_OBS = 250


# =============================================================================
# INDICATOR REGISTRY
# =============================================================================
# Format: (indicator_id, basket_pillar, target_spec, role, expected_sign)
# target_spec = (series_id_or_ratio, horizon_days, mode)
# mode in: "level", "yoy_pct_level", "delta", "log_fwd_return",
#          "log_fwd_return_ratio" (uses A/B in series_id), "fwd_max_change"

INDICATOR_REGISTRY: list[tuple[str, str, tuple, str, int]] = []

# --- DIAGNOSTIC COMPANIONS (concurrent r vs ground-truth reference) ---
# horizon=0 means no forward shift; we test how well the composite tracks the
# reference in real time, with walk-forward fold consistency as the validator.
DIAGNOSTIC_REFS: list[tuple[str, str, tuple, int]] = [
    # (pillar, indicator_suffix, target_spec, expected_sign)
    ("LPI",     "diag_unrate",       ("UNRATE",                 0, "level"),         +1),
    ("PCI",     "diag_corepce",      ("PCEPILFE",               0, "yoy_pct_level"), +1),
    ("GCI",     "diag_cfnai",        ("CFNAIMA3",               0, "level"),         +1),
    ("HCI",     "diag_caseshiller",  ("CSUSHPINSA",             0, "yoy_pct_level"), +1),
    ("CCI",     "diag_realpce",      ("PCEC96",                 0, "yoy_pct_level"), +1),
    ("BCI",     "diag_capex_orders", ("ANDENO",                 0, "yoy_pct_level"), +1),
    ("TCI",     "diag_twi_yoy",      ("DTWEXBGS",               0, "yoy_pct_level"), +1),
    ("GCI_Gov", "diag_term_premium", ("THREEFYTP10",            0, "level"),         +1),
    ("FCI",     "diag_chi_nfci",     ("ANFCI",                  0, "level"),         +1),
    ("LCI",     "diag_reserves_yoy", ("TOTRESNS",               0, "yoy_pct_level"), +1),
    ("MSI",     "diag_pct_above_200",("SPX_vs_200d_pct",        0, "level"),         +1),
    ("SPI",     "diag_aaii_spread",  ("AAII_Bull_Bear_Spread",  0, "level"),         -1),
]
for pillar, suffix, tgt, sign in DIAGNOSTIC_REFS:
    INDICATOR_REGISTRY.append((f"{pillar}_{suffix}", pillar, tgt, "diagnostic", sign))


# --- RELATIVE-PERFORMANCE (forward IC vs ratio target) ---
# Each ratio runs at 63d and 252d horizons across all 12 pillars.
RATIO_TARGETS: list[tuple[str, str, str]] = [
    # (label, numerator_etf, denominator_etf)
    ("stocks_vs_bonds",       "SPY",  "TLT"),  # equity vs long bond
    ("stocks_vs_belly",       "SPY",  "IEF"),  # equity vs 7-10y
    ("cyc_vs_def_equity",     "XLY",  "XLP"),  # consumer disc vs staples
    ("tech_vs_def_equity",    "XLK",  "XLU"),  # tech vs utilities
    ("tech_vs_broad",         "QQQ",  "SPY"),  # nasdaq-large vs broad
    ("small_vs_large",        "IWM",  "SPY"),  # small cap vs large
    ("credit_risk_on_off",    "HYG",  "LQD"),  # HY vs IG
    ("short_vs_long_duration","SHY",  "TLT"),  # short tsy vs long
    ("us_vs_intl",            "SPY",  "EFA"),  # US vs developed intl
    ("em_vs_dm",              "EEM",  "EFA"),  # EM vs DM
    ("gold_vs_equity",        "GLD",  "SPY"),  # real asset vs equity
    ("homebuilders_vs_broad", "XHB",  "SPY"),  # housing-cyclical vs broad
]

for pillar in PILLAR_SPECS.keys():
    for label, num, den in RATIO_TARGETS:
        for horizon in (63, 252):
            ratio_id = f"{num}/{den}"
            INDICATOR_REGISTRY.append((
                f"{pillar}_relperf_{label}_{horizon}d",
                pillar,
                (ratio_id, horizon, "log_fwd_return_ratio"),
                "relative_predictive",
                0,  # 0 = no expected sign for relative-perf, just discover
            ))


# =============================================================================
# TARGET BUILDER
# =============================================================================

def build_target_v3(conn, target_spec):
    """Build target series. Supports concurrent (h=0), forward, and ratio targets."""
    sid, h, mode = target_spec

    if mode == "log_fwd_return_ratio":
        # sid = "A/B" where A and B are ETF tickers (will append _Close)
        a, b = sid.split("/")
        sa_id = a if a.endswith("_Close") else f"{a}_Close"
        sb_id = b if b.endswith("_Close") else f"{b}_Close"
        sa = load_obs(conn, sa_id)
        sb = load_obs(conn, sb_id)
        if sa.empty or sb.empty:
            return None
        sa_d = sa.resample("D").ffill()
        sb_d = sb.resample("D").ffill()
        # Inner-join on common dates
        common = sa_d.index.intersection(sb_d.index)
        sa_d = sa_d.loc[common]
        sb_d = sb_d.loc[common]
        ratio = sa_d / sb_d
        ratio = ratio.replace([np.inf, -np.inf], np.nan).dropna()
        return np.log(ratio.shift(-h) / ratio) * 100

    s = load_obs(conn, sid)
    if s.empty:
        return None
    s_d = s.resample("D").ffill()

    if h == 0:
        # Concurrent (diagnostic mode)
        if mode == "level":
            return s_d
        if mode == "yoy_pct_level":
            return (s_d / s_d.shift(252) - 1) * 100
        return s_d

    if mode == "delta":
        return s_d.shift(-h) - s_d
    if mode == "log_fwd_return":
        return np.log(s_d.shift(-h) / s_d) * 100
    if mode == "yoy_pct_level":
        yoy = (s_d / s_d.shift(252) - 1) * 100
        return yoy.shift(-h)
    if mode == "fwd_max_change":
        out = pd.Series(index=s_d.index, dtype=float)
        arr = s_d.values
        for i in range(len(arr) - h):
            out.iloc[i] = arr[i:i+h+1].max() - arr[i]
        return out
    return s_d.shift(-h) - s_d


# =============================================================================
# OPTIMIZATION (same engine as v2)
# =============================================================================

def neg_abs_ic(weights_arr, z_components, target):
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


def optimize_weights(z_components, target, n_restarts=N_RESTARTS, bounds=BOUNDS):
    n = z_components.shape[1]
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
            res = minimize(
                neg_abs_ic, w0, args=(z_components, target),
                method="SLSQP", bounds=bnds, constraints=cons,
                options={"maxiter": 200, "ftol": 1e-9},
            )
            if res.fun < best_obj:
                best_obj = res.fun
                best = res
        except Exception:
            pass
    if best is None or best_obj > 1e5:
        return None
    w = np.abs(best.x) / np.abs(best.x).sum()
    return {c: float(w[i]) for i, c in enumerate(z_components.columns)}


def evaluate_signed_ic(z_components, target, weights):
    cols = list(z_components.columns)
    w_arr = np.array([weights[c] for c in cols])
    w_arr = w_arr / w_arr.sum()
    composite = z_components.values @ w_arr
    df = pd.DataFrame({"sig": composite, "fwd": target}, index=z_components.index).dropna()
    if len(df) < 50:
        return None, 0
    ic, _ = stats.spearmanr(df["sig"], df["fwd"])
    return float(ic) if not np.isnan(ic) else None, len(df)


def walk_forward(z_components, target, n_folds=N_FOLDS):
    aligned = z_components.join(target.rename("fwd")).dropna()
    if len(aligned) < MIN_FOLD_OBS * (n_folds + 1):
        return None, len(aligned)
    z_aligned = aligned[z_components.columns]
    fwd_aligned = aligned["fwd"]

    tscv = TimeSeriesSplit(n_splits=n_folds)
    fold_oos_ics = []
    for is_idx, oos_idx in tscv.split(z_aligned):
        z_is = z_aligned.iloc[is_idx]
        fwd_is = fwd_aligned.iloc[is_idx]
        z_oos = z_aligned.iloc[oos_idx]
        fwd_oos = fwd_aligned.iloc[oos_idx]
        if len(z_is) < MIN_FOLD_OBS or len(z_oos) < MIN_FOLD_OBS:
            continue
        weights = optimize_weights(z_is, fwd_is, n_restarts=10)
        if weights is None:
            continue
        oos_ic, _ = evaluate_signed_ic(z_oos, fwd_oos, weights)
        if oos_ic is not None:
            fold_oos_ics.append(oos_ic)

    if not fold_oos_ics:
        return None, len(aligned)

    arr = np.array(fold_oos_ics)
    n_pos = sum(1 for x in arr if x > 0)
    dominant = max(n_pos, len(arr) - n_pos) / len(arr)

    return {
        "n_folds": len(arr),
        "oos_ic_mean": float(arr.mean()),
        "oos_ic_std": float(arr.std()),
        "oos_abs_ic_mean": float(np.abs(arr).mean()),
        "oos_dominant_pct": float(dominant),
        "fold_ics": [float(x) for x in arr],
    }, len(aligned)


def run_indicator(conn, indicator_id, basket_pillar, target_spec, role, expected_sign):
    spec = PILLAR_SPECS.get(basket_pillar)
    if spec is None:
        return None
    z_comp, _ = build_components(conn, spec)
    if z_comp.empty:
        return None
    target = build_target_v3(conn, target_spec)
    if target is None or target.dropna().empty:
        return None

    wf, n_aligned = walk_forward(z_comp, target)
    if not wf:
        return {
            "indicator_id": indicator_id,
            "basket_pillar": basket_pillar,
            "target": target_spec,
            "role": role,
            "expected_sign": expected_sign,
            "n_aligned": n_aligned,
            "status": "insufficient_data",
        }

    # Full-sample re-optimization for production weights
    aligned = z_comp.join(target.rename("fwd")).dropna()
    weights = optimize_weights(aligned[z_comp.columns], aligned["fwd"], n_restarts=N_RESTARTS)
    full_ic, _ = evaluate_signed_ic(aligned[z_comp.columns], aligned["fwd"], weights) if weights else (None, 0)

    # Sign matches expected (only if expected_sign is non-zero)
    sign_match_expected = None
    if expected_sign != 0:
        sign_match_expected = sum(1 for x in wf["fold_ics"] if expected_sign * x > 0) / len(wf["fold_ics"])

    # Quality: signal is real if dominant_pct ≥ 80% AND |mean| ≥ 0.10
    signal_real = wf["oos_dominant_pct"] >= 0.8 and abs(wf["oos_ic_mean"]) >= 0.10

    return {
        "indicator_id": indicator_id,
        "basket_pillar": basket_pillar,
        "target": target_spec,
        "role": role,
        "expected_sign": expected_sign,
        "n_aligned": n_aligned,
        "full_ic": full_ic,
        "weights": weights,
        "walk_forward": wf,
        "sign_match_expected": sign_match_expected,
        "signal_real": signal_real,
        "status": "ok",
    }


def main():
    print("=" * 80)
    print("INDICATOR REGISTRY v3 — multi-role per-pillar optimization")
    print(f"Run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Registry size: {len(INDICATOR_REGISTRY)} indicators")
    print(f"Folds: {N_FOLDS}  Restarts: {N_RESTARTS}  Bounds: {BOUNDS}")
    print("=" * 80)

    conn = sqlite3.connect(DB_PATH)
    out: dict[str, Any] = {
        "run_date": datetime.now().isoformat(),
        "methodology": "v2 walk-forward (5-fold TimeSeriesSplit), |IC| optimization, signed-IC evaluation",
        "indicators": {},
    }

    # Group by role for ordered processing
    diagnostics = [r for r in INDICATOR_REGISTRY if r[3] == "diagnostic"]
    relperf = [r for r in INDICATOR_REGISTRY if r[3] == "relative_predictive"]

    print(f"\n{'='*80}\nDIAGNOSTIC COMPANIONS ({len(diagnostics)})\n{'='*80}")
    print(f"  {'Indicator':<32} {'Target':<28} {'WF mean':>9} {'|IC|':>7} {'Dom%':>5} {'Real':>5}")
    print(f"  {'-'*92}")
    for ind_id, basket, tgt, role, sign in diagnostics:
        result = run_indicator(conn, ind_id, basket, tgt, role, sign)
        if result is None:
            print(f"  {ind_id:<32} [skipped]")
            continue
        out["indicators"][ind_id] = result
        if result.get("status") != "ok":
            print(f"  {ind_id:<32} [{result['status']}]")
            continue
        wf = result["walk_forward"]
        target_str = f"{tgt[0][:25]}"
        print(f"  {ind_id:<32} {target_str:<28} {wf['oos_ic_mean']:>+9.3f} {wf['oos_abs_ic_mean']:>7.3f} {wf['oos_dominant_pct']:>4.0%} {'YES' if result['signal_real'] else 'no':>5}")

    print(f"\n{'='*80}\nRELATIVE PERFORMANCE ({len(relperf)})\n{'='*80}")
    print(f"  {'Indicator':<48} {'WF mean':>9} {'|IC|':>7} {'Dom%':>5} {'Real':>5}")
    print(f"  {'-'*82}")
    for ind_id, basket, tgt, role, sign in relperf:
        result = run_indicator(conn, ind_id, basket, tgt, role, sign)
        if result is None:
            continue
        out["indicators"][ind_id] = result
        if result.get("status") != "ok":
            continue
        wf = result["walk_forward"]
        print(f"  {ind_id:<48} {wf['oos_ic_mean']:>+9.3f} {wf['oos_abs_ic_mean']:>7.3f} {wf['oos_dominant_pct']:>4.0%} {'YES' if result['signal_real'] else 'no':>5}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(out, indent=2, default=str))
    print(f"\n{'='*80}\nOutput JSON: {OUT_JSON}")

    # Generate summary markdown
    write_summary(out)
    print(f"Output MD:   {OUT_MD}\n{'='*80}")


def write_summary(out):
    indicators = out["indicators"]
    diagnostics = {k: v for k, v in indicators.items() if v.get("role") == "diagnostic"}
    relperf = {k: v for k, v in indicators.items() if v.get("role") == "relative_predictive"}

    real_diag = [v for v in diagnostics.values() if v.get("signal_real")]
    real_rp = [v for v in relperf.values() if v.get("signal_real")]

    lines = []
    lines.append("# Pillar Indicator Registry v3 — Run Results")
    lines.append("")
    lines.append(f"_Generated {out['run_date']}_")
    lines.append(f"_Methodology: {out['methodology']}_")
    lines.append("")
    lines.append("## Summary")
    lines.append(f"- **{len(indicators)}** indicators run, **{sum(1 for v in indicators.values() if v.get('signal_real'))}** real signals (dominant % ≥80% AND |OOS IC| ≥0.10).")
    lines.append(f"- Diagnostics: {len(real_diag)} / {len(diagnostics)} real")
    lines.append(f"- Relative performance: {len(real_rp)} / {len(relperf)} real")
    lines.append("")

    # ---- Diagnostic table ----
    lines.append("## Diagnostic companions (concurrent r vs ground-truth reference)")
    lines.append("")
    lines.append("Composite weights here are tuned for **concurrent** tracking — they answer 'what is X right now'. Different from the predictive composite.")
    lines.append("")
    lines.append("| Indicator | Pillar | Reference | WF mean | \\|IC\\| | Dom% | Real |")
    lines.append("|---|---|---|---:|---:|---:|:---:|")
    for k, v in sorted(diagnostics.items()):
        if v.get("status") != "ok":
            continue
        wf = v["walk_forward"]
        real = "✅" if v["signal_real"] else "—"
        lines.append(f"| {k} | {v['basket_pillar']} | {v['target'][0]} | {wf['oos_ic_mean']:+.3f} | {wf['oos_abs_ic_mean']:.3f} | {wf['oos_dominant_pct']:.0%} | {real} |")
    lines.append("")

    # ---- Relative-performance: top signals ----
    lines.append("## Relative-performance — real signals (Dom%≥80% AND |WF mean|≥0.10)")
    lines.append("")
    lines.append("These are the cells where a pillar's basket predicts a rotation pair with consistent walk-forward signal.")
    lines.append("")
    lines.append("| Indicator | Pillar | Ratio | Horizon | WF mean | \\|IC\\| | Dom% |")
    lines.append("|---|---|---|---:|---:|---:|---:|")
    real_rp_sorted = sorted(real_rp, key=lambda v: -abs(v["walk_forward"]["oos_ic_mean"]))
    for v in real_rp_sorted:
        wf = v["walk_forward"]
        ratio = v["target"][0]
        h = v["target"][1]
        lines.append(f"| {v['indicator_id']} | {v['basket_pillar']} | {ratio} | {h}d | {wf['oos_ic_mean']:+.3f} | {wf['oos_abs_ic_mean']:.3f} | {wf['oos_dominant_pct']:.0%} |")
    lines.append("")

    # ---- Per-pillar relative-perf grid ----
    lines.append("## Per-pillar relative-performance grid")
    lines.append("")
    lines.append("Walk-forward mean OOS IC. Bold = signal_real (Dom%≥80% AND |IC|≥0.10).")
    lines.append("")
    pillars = sorted({v["basket_pillar"] for v in relperf.values()})
    ratios_h = sorted({(v["target"][0], v["target"][1]) for v in relperf.values()})
    header = "| Pillar | " + " | ".join(f"{r}@{h}d" for r, h in ratios_h) + " |"
    sep = "|---|" + "|".join("---:" for _ in ratios_h) + "|"
    lines.append(header)
    lines.append(sep)
    for p in pillars:
        cells = []
        for r, h in ratios_h:
            cell_val = "—"
            for v in relperf.values():
                if v["basket_pillar"] == p and v["target"][0] == r and v["target"][1] == h and v.get("status") == "ok":
                    wf_mean = v["walk_forward"]["oos_ic_mean"]
                    if v["signal_real"]:
                        cell_val = f"**{wf_mean:+.2f}**"
                    else:
                        cell_val = f"{wf_mean:+.2f}"
                    break
            cells.append(cell_val)
        lines.append(f"| {p} | " + " | ".join(cells) + " |")
    lines.append("")

    OUT_MD.write_text("\n".join(lines))


if __name__ == "__main__":
    main()
