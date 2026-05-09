#!/usr/bin/env python3
"""
Pillar Rebuild v4 — Expanded Baskets + Multi-Role Registry
============================================================
Re-runs the v3 indicator registry (diagnostic + relative-performance) with
the Tier 1 expanded baskets in pillar_specs_v2.EXPANDED_PILLAR_SPECS.

Outputs comparison vs v3 (which used the original baskets) so we can see
which Tier 1 component additions actually lifted the walk-forward IC.

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
    build_components,
    load_obs,
)
from pillar_specs_v2 import EXPANDED_PILLAR_SPECS, DISPLAY_NAMES  # noqa: E402

OUTPUT_DIR = Path("/Users/bob/LHM/Outputs/mri_optimization")
OUT_JSON = OUTPUT_DIR / "pillar_registry_v4.json"
OUT_MD = OUTPUT_DIR / "pillar_registry_v4_summary.md"
OUT_DIFF = OUTPUT_DIR / "pillar_v3_vs_v4_basket_diff.md"

BOUNDS = (0.02, 0.40)
N_RESTARTS = 15
N_FOLDS = 5
MIN_FOLD_OBS = 250


# =============================================================================
# SAME REGISTRY AS V3 (diagnostic + relative-perf)
# =============================================================================

DIAGNOSTIC_REFS = [
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
]
# Note: MSI/SPI not in expanded specs — they need separate work (data backfill / ingestion)

RATIO_TARGETS = [
    ("stocks_vs_bonds",       "SPY",  "TLT"),
    ("stocks_vs_belly",       "SPY",  "IEF"),
    ("cyc_vs_def_equity",     "XLY",  "XLP"),
    ("tech_vs_def_equity",    "XLK",  "XLU"),
    ("tech_vs_broad",         "QQQ",  "SPY"),
    ("small_vs_large",        "IWM",  "SPY"),
    ("credit_risk_on_off",    "HYG",  "LQD"),
    ("short_vs_long_duration","SHY",  "TLT"),
    ("us_vs_intl",            "SPY",  "EFA"),
    ("em_vs_dm",              "EEM",  "EFA"),
    ("gold_vs_equity",        "GLD",  "SPY"),
    ("homebuilders_vs_broad", "XHB",  "SPY"),
]

INDICATOR_REGISTRY = []
for pillar, suffix, tgt, sign in DIAGNOSTIC_REFS:
    INDICATOR_REGISTRY.append((f"{pillar}_{suffix}", pillar, tgt, "diagnostic", sign))
for pillar in EXPANDED_PILLAR_SPECS.keys():
    for label, num, den in RATIO_TARGETS:
        for horizon in (63, 252):
            INDICATOR_REGISTRY.append((
                f"{pillar}_relperf_{label}_{horizon}d",
                pillar,
                (f"{num}/{den}", horizon, "log_fwd_return_ratio"),
                "relative_predictive",
                0,
            ))


# =============================================================================
# TARGET BUILDER + OPTIMIZER (same as v3)
# =============================================================================

def build_target_v3(conn, target_spec):
    sid, h, mode = target_spec
    if mode == "log_fwd_return_ratio":
        a, b = sid.split("/")
        sa_id = a if a.endswith("_Close") else f"{a}_Close"
        sb_id = b if b.endswith("_Close") else f"{b}_Close"
        sa = load_obs(conn, sa_id)
        sb = load_obs(conn, sb_id)
        if sa.empty or sb.empty:
            return None
        sa_d = sa.resample("D").ffill()
        sb_d = sb.resample("D").ffill()
        common = sa_d.index.intersection(sb_d.index)
        ratio = (sa_d.loc[common] / sb_d.loc[common]).replace([np.inf, -np.inf], np.nan).dropna()
        return np.log(ratio.shift(-h) / ratio) * 100
    s = load_obs(conn, sid)
    if s.empty:
        return None
    s_d = s.resample("D").ffill()
    if h == 0:
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


def neg_abs_ic(weights_arr, z_components, target):
    w = np.abs(weights_arr)
    if w.sum() <= 0:
        return 1e6
    w = w / w.sum()
    composite = z_components.values @ w
    df = pd.DataFrame({"sig": composite, "fwd": target.values}, index=z_components.index).dropna()
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
            res = minimize(neg_abs_ic, w0, args=(z_components, target),
                           method="SLSQP", bounds=bnds, constraints=cons,
                           options={"maxiter": 200, "ftol": 1e-9})
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
    spec = EXPANDED_PILLAR_SPECS.get(basket_pillar)
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
        return {"indicator_id": indicator_id, "basket_pillar": basket_pillar,
                "target": target_spec, "role": role, "expected_sign": expected_sign,
                "n_aligned": n_aligned, "status": "insufficient_data"}
    aligned = z_comp.join(target.rename("fwd")).dropna()
    weights = optimize_weights(aligned[z_comp.columns], aligned["fwd"], n_restarts=N_RESTARTS)
    full_ic, _ = evaluate_signed_ic(aligned[z_comp.columns], aligned["fwd"], weights) if weights else (None, 0)
    sign_match_expected = None
    if expected_sign != 0:
        sign_match_expected = sum(1 for x in wf["fold_ics"] if expected_sign * x > 0) / len(wf["fold_ics"])
    signal_real = wf["oos_dominant_pct"] >= 0.8 and abs(wf["oos_ic_mean"]) >= 0.10
    return {
        "indicator_id": indicator_id, "basket_pillar": basket_pillar,
        "target": target_spec, "role": role, "expected_sign": expected_sign,
        "n_aligned": n_aligned, "full_ic": full_ic, "weights": weights,
        "walk_forward": wf, "sign_match_expected": sign_match_expected,
        "signal_real": signal_real, "status": "ok",
    }


def main():
    print("=" * 80)
    print("PILLAR REBUILD v4 — EXPANDED BASKETS + MULTI-ROLE REGISTRY")
    print(f"Run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Registry: {len(INDICATOR_REGISTRY)} indicators ({len(DIAGNOSTIC_REFS)} diag + relperf)")
    print(f"Pillars (expanded baskets): {list(EXPANDED_PILLAR_SPECS.keys())}")
    print("=" * 80)

    conn = sqlite3.connect(DB_PATH)
    out: dict[str, Any] = {
        "run_date": datetime.now().isoformat(),
        "methodology": "v2 walk-forward (5-fold TimeSeriesSplit), |IC| optimization, signed-IC evaluation, EXPANDED Tier 1 baskets",
        "display_names": DISPLAY_NAMES,
        "indicators": {},
    }

    diagnostics = [r for r in INDICATOR_REGISTRY if r[3] == "diagnostic"]
    relperf = [r for r in INDICATOR_REGISTRY if r[3] == "relative_predictive"]

    print(f"\nDIAGNOSTIC ({len(diagnostics)})")
    print(f"  {'Indicator':<32} {'WF mean':>9} {'|IC|':>7} {'Dom%':>5}  Real")
    for ind_id, basket, tgt, role, sign in diagnostics:
        r = run_indicator(conn, ind_id, basket, tgt, role, sign)
        if not r:
            continue
        out["indicators"][ind_id] = r
        if r.get("status") != "ok":
            print(f"  {ind_id:<32} [{r['status']}]")
            continue
        wf = r["walk_forward"]
        print(f"  {ind_id:<32} {wf['oos_ic_mean']:>+9.3f} {wf['oos_abs_ic_mean']:>7.3f} {wf['oos_dominant_pct']:>4.0%}  {'YES' if r['signal_real'] else 'no'}")

    print(f"\nRELATIVE PERFORMANCE ({len(relperf)})")
    real_count = 0
    for ind_id, basket, tgt, role, sign in relperf:
        r = run_indicator(conn, ind_id, basket, tgt, role, sign)
        if not r:
            continue
        out["indicators"][ind_id] = r
        if r.get("status") == "ok" and r.get("signal_real"):
            real_count += 1
            wf = r["walk_forward"]
            print(f"  REAL: {ind_id:<48} {wf['oos_ic_mean']:>+9.3f} {wf['oos_abs_ic_mean']:>7.3f} {wf['oos_dominant_pct']:>4.0%}")
    print(f"  ({real_count} real signals out of {len(relperf)})")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(out, indent=2, default=str))
    print(f"\nOutput JSON: {OUT_JSON}")

    write_summary_md(out)
    write_diff_md(out)
    print(f"Output MD:   {OUT_MD}")
    print(f"Diff vs v3:  {OUT_DIFF}")


def write_summary_md(out):
    indicators = out["indicators"]
    diags = {k: v for k, v in indicators.items() if v.get("role") == "diagnostic"}
    relperf = {k: v for k, v in indicators.items() if v.get("role") == "relative_predictive"}
    real_relperf = [v for v in relperf.values() if v.get("signal_real")]

    lines = [
        "# Pillar Indicator Registry v4 — Expanded Baskets",
        "",
        f"_Generated {out['run_date']}_",
        f"_{out['methodology']}_",
        "",
        "## Summary",
        f"- {len(indicators)} indicators run",
        f"- Diagnostics: {sum(1 for v in diags.values() if v.get('signal_real'))} / {len(diags)} real",
        f"- Relative performance: {len(real_relperf)} / {len(relperf)} real",
        "",
        "## Diagnostic companions (concurrent r vs ground-truth reference)",
        "",
        "| Indicator | Pillar (new name) | Reference | WF mean | \\|IC\\| | Dom% | Real |",
        "|---|---|---|---:|---:|---:|:---:|",
    ]
    for k, v in sorted(diags.items()):
        if v.get("status") != "ok":
            continue
        wf = v["walk_forward"]
        real = "✅" if v["signal_real"] else "—"
        name = DISPLAY_NAMES.get(v["basket_pillar"], v["basket_pillar"])
        lines.append(f"| {k} | {name} | {v['target'][0]} | {wf['oos_ic_mean']:+.3f} | {wf['oos_abs_ic_mean']:.3f} | {wf['oos_dominant_pct']:.0%} | {real} |")
    lines.append("")
    lines.append("## Real relative-performance signals (Dom%≥80% AND |WF mean|≥0.10)")
    lines.append("")
    lines.append("| Indicator | Pillar | Ratio | Horizon | WF mean | \\|IC\\| | Dom% |")
    lines.append("|---|---|---|---:|---:|---:|---:|")
    real_sorted = sorted(real_relperf, key=lambda v: -abs(v["walk_forward"]["oos_ic_mean"]))
    for v in real_sorted:
        wf = v["walk_forward"]
        name = DISPLAY_NAMES.get(v["basket_pillar"], v["basket_pillar"])
        lines.append(f"| {v['indicator_id']} | {name} | {v['target'][0]} | {v['target'][1]}d | {wf['oos_ic_mean']:+.3f} | {wf['oos_abs_ic_mean']:.3f} | {wf['oos_dominant_pct']:.0%} |")
    OUT_MD.write_text("\n".join(lines))


def write_diff_md(out):
    """Compare v3 (original baskets) vs v4 (expanded) for the same indicator IDs."""
    v3_path = OUTPUT_DIR / "pillar_registry_v3.json"
    if not v3_path.exists():
        return
    v3 = json.load(open(v3_path))
    v3_inds = v3.get("indicators", {})
    v4_inds = out["indicators"]
    common = sorted(set(v3_inds.keys()) & set(v4_inds.keys()))
    lines = [
        "# v3 (original) vs v4 (expanded baskets) — Walk-Forward IC Diff",
        "",
        "Positive `|IC| delta` means the expanded basket lifted signal magnitude.",
        "Sign-flip = the WF mean changed sign between v3 and v4 (basket changed character).",
        "",
        "## Diagnostic companions",
        "",
        "| Indicator | v3 WF mean | v4 WF mean | v3 \\|IC\\| | v4 \\|IC\\| | \\|IC\\| Δ | v3 Dom | v4 Dom | Verdict |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    diag_keys = [k for k in common if v4_inds[k].get("role") == "diagnostic"]
    for k in diag_keys:
        v3i = v3_inds[k]
        v4i = v4_inds[k]
        if v3i.get("status") != "ok" or v4i.get("status") != "ok":
            continue
        v3wf = v3i["walk_forward"]
        v4wf = v4i["walk_forward"]
        delta_abs = v4wf["oos_abs_ic_mean"] - v3wf["oos_abs_ic_mean"]
        sign_flip = v3wf["oos_ic_mean"] * v4wf["oos_ic_mean"] < 0
        verdict = "🔄 sign-flip" if sign_flip else ("📈 lift" if delta_abs > 0.02 else "📉 drop" if delta_abs < -0.02 else "≈ flat")
        lines.append(f"| {k} | {v3wf['oos_ic_mean']:+.3f} | {v4wf['oos_ic_mean']:+.3f} | {v3wf['oos_abs_ic_mean']:.3f} | {v4wf['oos_abs_ic_mean']:.3f} | {delta_abs:+.3f} | {v3wf['oos_dominant_pct']:.0%} | {v4wf['oos_dominant_pct']:.0%} | {verdict} |")
    lines.append("")
    lines.append("## Relative-performance — became real after expansion")
    lines.append("")
    lines.append("Indicators that were NOT real in v3 but ARE real in v4.")
    lines.append("")
    lines.append("| Indicator | v3 WF mean | v4 WF mean | v3 Dom | v4 Dom |")
    lines.append("|---|---:|---:|---:|---:|")
    for k in common:
        v3i = v3_inds[k]
        v4i = v4_inds[k]
        if v3i.get("role") != "relative_predictive" or v4i.get("role") != "relative_predictive":
            continue
        if v3i.get("status") != "ok" or v4i.get("status") != "ok":
            continue
        if not v4i.get("signal_real") or v3i.get("signal_real"):
            continue
        v3wf = v3i["walk_forward"]
        v4wf = v4i["walk_forward"]
        lines.append(f"| {k} | {v3wf['oos_ic_mean']:+.3f} | {v4wf['oos_ic_mean']:+.3f} | {v3wf['oos_dominant_pct']:.0%} | {v4wf['oos_dominant_pct']:.0%} |")
    lines.append("")
    lines.append("## Relative-performance — was real but lost in v4 (red flag)")
    lines.append("")
    lines.append("| Indicator | v3 WF mean | v4 WF mean | v3 Dom | v4 Dom |")
    lines.append("|---|---:|---:|---:|---:|")
    for k in common:
        v3i = v3_inds[k]
        v4i = v4_inds[k]
        if v3i.get("role") != "relative_predictive" or v4i.get("role") != "relative_predictive":
            continue
        if v3i.get("status") != "ok" or v4i.get("status") != "ok":
            continue
        if v4i.get("signal_real") or not v3i.get("signal_real"):
            continue
        v3wf = v3i["walk_forward"]
        v4wf = v4i["walk_forward"]
        lines.append(f"| {k} | {v3wf['oos_ic_mean']:+.3f} | {v4wf['oos_ic_mean']:+.3f} | {v3wf['oos_dominant_pct']:.0%} | {v4wf['oos_dominant_pct']:.0%} |")
    OUT_DIFF.write_text("\n".join(lines))


if __name__ == "__main__":
    main()
