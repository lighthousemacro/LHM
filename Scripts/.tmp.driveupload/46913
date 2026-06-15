#!/usr/bin/env python3
"""
MRI REWEIGHT PROPOSAL (review-only, 2026-06-15)

Derives evidence-based MRI weights from the 10 now-corrected, standardized
pillar composites (post transform-fix) regressed against forward recession
risk, walk-forward validated. Compares to the live v2.0 weights. DOES NOT
modify compute_mri.py — this is a proposal for Bob to approve.

Target = forward 12-month rise in UNRATE (the recession-risk transmission MRI
is meant to capture). Weights = standardized Ridge coefficients (full sample),
sign + magnitude; OOS IC from purged non-overlap walk-forward reports honesty.

Run: PYTHONPATH=/Users/bob/LHM /opt/homebrew/bin/python3 \
       Scripts/backtest/mri_reweight_proposal.py
"""
import json
import sqlite3
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pillar_reoptimize_v3 import (  # noqa: E402
    DB, zn, to_grid, build_target, walk_forward, load_db_series,
    MIN_TRAIN_M, REFIT_M, FFILL_M, NOISE_SEED,
)
from sklearn.linear_model import Ridge  # noqa: E402

warnings.simplefilter("ignore")

# Live v2.0 weights + signs (from compute_indices.compute_mri)
V2 = {
    "LPI": (-1, 0.33), "PCI": (+1, 0.03), "GCI": (-1, 0.02), "HCI": (-1, 0.02),
    "CCI": (-1, 0.02), "BCI": (-1, 0.13), "TCI": (-1, 0.12), "FPI": (+1, 0.12),
    "FCI": (-1, 0.07), "LCI": (-1, 0.14),
}
PILLARS = list(V2.keys())


def load_pillar(conn, pid):
    d = pd.read_sql("SELECT date, value FROM lighthouse_indices WHERE index_id=? "
                    "ORDER BY date", conn, params=(pid,), parse_dates=["date"])
    if d.empty:
        return pd.Series(dtype=float)
    return d.set_index("date")["value"]


def main():
    conn = sqlite3.connect(DB)
    # Features: 10 pillar composites on a monthly grid, zn point-in-time.
    feats = {}
    for p in PILLARS:
        s = load_pillar(conn, p)
        if s.empty:
            print(f"   [warn] {p} missing"); continue
        feats[p] = zn(to_grid(s, "M"), min_periods=24)
    F = pd.DataFrame(feats)
    full = F.dropna(how="all").index
    F = F.reindex(full).ffill(limit=FFILL_M)
    rng = np.random.default_rng(NOISE_SEED)
    for k in (1, 2):
        F[f"NOISE{k}"] = zn(pd.Series(rng.standard_normal(len(full)), index=full), min_periods=24)

    tgt, h = build_target(conn, {"kind": "db_fwd_chg", "tgt": "UNRATE", "h": 252}, full, "M")
    d = pd.concat([F, tgt.rename("__y")], axis=1).dropna()
    cols = PILLARS + ["NOISE1"]
    X, y = d[cols].to_numpy(float), d["__y"].to_numpy(float)

    # Full-sample Ridge for the weight proposal
    ridge = Ridge(alpha=5.0).fit(X, y)
    coef = dict(zip(cols, ridge.coef_))
    noise_coef = abs(coef.pop("NOISE1"))
    # normalize |coef| over pillars -> proposed weights; sign from coef sign
    tot = sum(abs(c) for c in coef.values()) or 1.0
    proposed = {p: (int(np.sign(coef[p]) or 1), round(abs(coef[p]) / tot, 3)) for p in PILLARS}

    # OOS skill of the proposed feature set (purged non-overlap WF)
    wf = walk_forward(F.reindex(d.index), tgt.reindex(d.index), PILLARS, h,
                      MIN_TRAIN_M, REFIT_M)

    print("=" * 74)
    print("MRI REWEIGHT PROPOSAL  (target: forward 12m UNRATE rise) — REVIEW ONLY")
    print("=" * 74)
    print(f"OOS IC (purged non-overlap WF): {wf.get('oos_ic')}  "
          f"overlap {wf.get('oos_ic_overlap')}  n={wf.get('n_oos_noov')}  "
          f"noise_ratio {wf.get('noise_ratio')}")
    print(f"NOISE1 coef magnitude: {noise_coef:.3f} (should be ~0 vs real pillars)")
    print(f"\n{'Pillar':<6} {'v2.0 sign/wt':>14} {'PROPOSED sign/wt':>18}  shift")
    print("-" * 60)
    for p in PILLARS:
        vs, vw = V2[p]; ps, pw = proposed[p]
        flag = "  <<" if abs(pw - vw) > 0.08 or ps != vs else ""
        print(f"{p:<6} {vs:+d} {vw:>10.2f} {ps:+d} {pw:>14.3f}  {pw-vw:+.3f}{flag}")

    out = {"target": "forward 12m UNRATE rise", "oos_ic": wf.get("oos_ic"),
           "oos_ic_overlap": wf.get("oos_ic_overlap"), "n_oos": wf.get("n_oos_noov"),
           "noise_ratio": wf.get("noise_ratio"), "noise_coef": round(noise_coef, 4),
           "v2_weights": {p: {"sign": V2[p][0], "weight": V2[p][1]} for p in PILLARS},
           "proposed_weights": {p: {"sign": proposed[p][0], "weight": proposed[p][1]} for p in PILLARS}}
    outp = Path("/Users/bob/LHM/Outputs/mri_optimization/mri_reweight_proposal_20260615.json")
    outp.write_text(json.dumps(out, indent=2))
    print(f"\nProposal written: {outp}  (NOT applied — awaiting Bob)")
    conn.close()


if __name__ == "__main__":
    main()
