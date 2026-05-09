#!/usr/bin/env python3
"""
Pillar Rebuild v6 — Lead-Lag Pattern Indicators (event study)
==============================================================
Different methodology from v3-v5 walk-forward IC. This is event-study:

For each pillar composite (built with EXPANDED_PILLAR_SPECS), compute z-score
across full history. Then for each z-score threshold breach (e.g., z>+1.5):

  - find the breach dates
  - compute forward returns of target asset at horizon h (1mo, 3mo, 6mo, 12mo)
  - mean breach-conditional forward return
  - compare to unconditional baseline
  - report excess return + t-statistic + sign consistency

This answers "when X breaches threshold, Y at horizon t+h does what?"

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

warnings.filterwarnings("ignore")

sys.path.insert(0, "/Users/bob/LHM/Scripts/backtest")
from pillar_weight_optimization import DB_PATH, build_components, load_obs  # noqa: E402
from pillar_specs_v2 import EXPANDED_PILLAR_SPECS, DISPLAY_NAMES  # noqa: E402

OUTPUT_DIR = Path("/Users/bob/LHM/Outputs/mri_optimization")
OUT_JSON = OUTPUT_DIR / "pillar_registry_v6_leadlag.json"
OUT_MD = OUTPUT_DIR / "pillar_registry_v6_leadlag_summary.md"

# Z-thresholds to test
THRESHOLDS = [
    ("z_gt_+2.0",  +2.0, "above"),
    ("z_gt_+1.5",  +1.5, "above"),
    ("z_lt_-1.5",  -1.5, "below"),
    ("z_lt_-2.0",  -2.0, "below"),
]

# Asset targets at multiple forward horizons (in days)
ASSET_TARGETS = [
    ("SPY",  "SPY_Close",     "log_return"),
    ("VIX",  "VIXCLS",        "log_return"),
    ("HYOAS","BAMLH0A0HYM2",  "level_change"),  # spread change in pp
    ("DGS10","DGS10",         "level_change"),  # yield change in pp
    ("DGS2", "DGS2",          "level_change"),
    ("DXY",  "DTWEXBGS",      "log_return"),
    ("TLT",  "TLT_Close",     "log_return"),
    ("GLD",  "GLD_Close",     "log_return"),
]

HORIZONS = [21, 63, 126, 252]  # ~1mo, 3mo, 6mo, 12mo


def equal_weight_composite(z_components):
    """Equal-weight composite for event study (since lead-lag is about thresholds, not optimized weights)."""
    return z_components.mean(axis=1)


def composite_zscore(composite, min_periods=252, winsorize=3.0):
    mean = composite.expanding(min_periods=min_periods).mean()
    std = composite.expanding(min_periods=min_periods).std()
    z = (composite - mean) / std.replace(0, np.nan)
    return z.clip(-winsorize, winsorize)


def forward_change(s, h, mode):
    s_d = s.resample("D").ffill()
    if mode == "log_return":
        return np.log(s_d.shift(-h) / s_d) * 100
    if mode == "level_change":
        return s_d.shift(-h) - s_d
    return s_d.shift(-h) - s_d


def event_study(z_series, fwd_series, threshold, direction):
    """Compute breach-conditional vs baseline forward returns."""
    aligned = pd.DataFrame({"z": z_series, "fwd": fwd_series}).dropna()
    if len(aligned) < 200:
        return None
    if direction == "above":
        breach_mask = aligned["z"] > threshold
    else:
        breach_mask = aligned["z"] < threshold
    breach = aligned.loc[breach_mask, "fwd"].dropna()
    base = aligned.loc[~breach_mask, "fwd"].dropna()
    if len(breach) < 20 or len(base) < 100:
        return None
    breach_mean = float(breach.mean())
    base_mean = float(base.mean())
    excess = breach_mean - base_mean
    try:
        t_stat, p_val = stats.ttest_ind(breach, base, equal_var=False)
        t_stat, p_val = float(t_stat), float(p_val)
    except Exception:
        t_stat, p_val = np.nan, np.nan
    # Hit rate: % of breaches where forward return same sign as excess
    if excess > 0:
        hit_rate = float((breach > 0).mean())
    elif excess < 0:
        hit_rate = float((breach < 0).mean())
    else:
        hit_rate = 0.5
    return {
        "threshold": threshold,
        "direction": direction,
        "n_breaches": int(len(breach)),
        "n_base": int(len(base)),
        "breach_mean": breach_mean,
        "base_mean": base_mean,
        "excess": excess,
        "t_stat": t_stat,
        "p_value": p_val,
        "hit_rate": hit_rate,
        "significant": bool(p_val < 0.05) if not np.isnan(p_val) else False,
    }


def main():
    print("=" * 80)
    print("PILLAR REBUILD v6 — LEAD-LAG PATTERN INDICATORS (event study)")
    print(f"Run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    pillars = list(EXPANDED_PILLAR_SPECS.keys())
    print(f"Pillars: {len(pillars)}, assets: {len(ASSET_TARGETS)}, horizons: {len(HORIZONS)}, thresholds: {len(THRESHOLDS)}")
    print(f"Total cells: {len(pillars) * len(ASSET_TARGETS) * len(HORIZONS) * len(THRESHOLDS)}")
    print("=" * 80)

    conn = sqlite3.connect(DB_PATH)
    out: dict[str, Any] = {
        "run_date": datetime.now().isoformat(),
        "methodology": "Event study — equal-weight composite z-score breach → forward return mean vs baseline; t-test for significance",
        "display_names": DISPLAY_NAMES,
        "patterns": [],
    }

    # Pre-compute composites (equal-weight) and z-scores per pillar
    pillar_z = {}
    for pillar in pillars:
        spec = EXPANDED_PILLAR_SPECS[pillar]
        z_comp, _ = build_components(conn, spec)
        if z_comp.empty:
            continue
        composite = equal_weight_composite(z_comp)
        composite_z = composite_zscore(composite)
        pillar_z[pillar] = composite_z
        print(f"  {pillar:<8} composite z built, n={composite_z.dropna().shape[0]}")

    # Pre-compute forward asset series (just need raw + ffill, then per-horizon shift in event_study)
    asset_data = {}
    for asset_label, sid, mode in ASSET_TARGETS:
        s = load_obs(conn, sid)
        if s.empty:
            continue
        asset_data[asset_label] = (s, mode)

    print(f"\nRunning event study...\n")

    for pillar, z in pillar_z.items():
        for asset_label, (asset_s, asset_mode) in asset_data.items():
            for h in HORIZONS:
                fwd = forward_change(asset_s, h, asset_mode)
                for thresh_label, thresh_val, direction in THRESHOLDS:
                    es = event_study(z, fwd, thresh_val, direction)
                    if es is None:
                        continue
                    pattern = {
                        "pillar": pillar,
                        "asset": asset_label,
                        "horizon_d": h,
                        "threshold_label": thresh_label,
                        **es,
                    }
                    out["patterns"].append(pattern)

    # Filter for significant + meaningful patterns
    sig = [p for p in out["patterns"] if p["significant"] and p["n_breaches"] >= 30]
    sig_by_excess = sorted(sig, key=lambda p: -abs(p["excess"]))

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(out, indent=2, default=str))
    print(f"Total patterns: {len(out['patterns'])}")
    print(f"Significant (p<0.05, n_breaches≥30): {len(sig)}")
    print(f"\nTop 30 by absolute excess return:")
    print(f"  {'Pillar':<10} {'Asset':<6} {'h':>4} {'thresh':<12} {'breaches':>8} {'excess':>9} {'t':>7} {'p':>7} {'hit%':>5}")
    for p in sig_by_excess[:30]:
        print(f"  {p['pillar']:<10} {p['asset']:<6} {p['horizon_d']:>4} {p['threshold_label']:<12} {p['n_breaches']:>8} {p['excess']:>+9.3f} {p['t_stat']:>+7.2f} {p['p_value']:>7.4f} {p['hit_rate']:>4.0%}")

    write_md(out, sig_by_excess)
    print(f"\nOutput JSON: {OUT_JSON}")
    print(f"Output MD:   {OUT_MD}")


def write_md(out, sig_by_excess):
    lines = [
        "# Pillar Lead-Lag Patterns (v6) — Event Study",
        "",
        f"_Generated {out['run_date']}_",
        f"_{out['methodology']}_",
        "",
        "Reads: \"When [pillar] z-score [breaches threshold], [asset] over the next [horizon] does X% (vs baseline Y%).\"",
        "",
        f"## Top 50 statistically-significant patterns (p<0.05, n_breaches≥30)",
        "",
        "Sorted by absolute excess return (breach mean - baseline mean).",
        "",
        "| Pillar | Asset | Horizon | Threshold | Breaches | Breach mean | Base mean | Excess | t | p | Hit% |",
        "|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for p in sig_by_excess[:50]:
        name = DISPLAY_NAMES.get(p["pillar"], p["pillar"])
        lines.append(
            f"| {name} | {p['asset']} | {p['horizon_d']}d | {p['threshold_label']} | {p['n_breaches']} | "
            f"{p['breach_mean']:+.3f} | {p['base_mean']:+.3f} | {p['excess']:+.3f} | "
            f"{p['t_stat']:+.2f} | {p['p_value']:.4f} | {p['hit_rate']:.0%} |"
        )
    OUT_MD.write_text("\n".join(lines))


if __name__ == "__main__":
    main()
