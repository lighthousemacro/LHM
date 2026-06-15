#!/usr/bin/env python3
"""
VALIDATE ALLOCATION CANDIDATES — honest purged-WF OOS for arbitrary baskets.

Reuses the leak-corrected engines (pillar_reoptimize_v3 / registry_honest_v4):
point-in-time zn-scoring, NON-OVERLAP purged walk-forward OOS IC, and a
NOISE-pair false-discovery control. Lets us validate the NEW allocation-impact
candidates surfaced from the full pillar docs (cross-asset / sector / curve /
rotation targets) the same honest way the migration program validates pillars.

Input  : a JSON list of candidates, each
  {"name","components":[["SERIES_ID",sign,"level|yoy_pct|log_yoy|delta"],...],
   "target":{"kind":"db_fwd_chg|asset_fwd_ret|ratio_fwd_ret","tgt":"SPY|XLY/XLP|...","h":63}}
Output : per-candidate OOS IC, overlap IC, rank IC, noise ratio, n, verdict.

Run (py3.14):
  PYTHONPATH=/Users/bob/LHM /opt/homebrew/bin/python3 \
    Scripts/backtest/validate_allocation_candidates.py <candidates.json> [out.json]

Verdict tiers (honest):
  VALIDATED   |oos_ic|>=0.10, n_oos>=50, noise_ratio<0.5, overlap-confirmed
  PROVISIONAL |oos_ic|>=0.10 but small-n (<50) or single-grid
  NOISE       noise_ratio>=0.5 (the noise pair matched it -> false discovery)
  DEMOTE      |oos_ic|<0.10
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
    DB, zn, to_grid, build_target, walk_forward, load_db_series, grid_of,
    MIN_TRAIN_M, REFIT_M, MIN_TRAIN_B, REFIT_B, FFILL_M, FFILL_B,
    NOISE_SEED, SKILL_FLOOR,
)

warnings.simplefilter("ignore")


def transform_series(s: pd.Series, kind: str) -> pd.Series:
    if kind == "yoy_pct":
        return s.pct_change(12) * 100.0
    if kind == "log_yoy":
        return np.log(s.replace(0, np.nan)).diff(12)
    if kind == "delta":
        return s.diff(1)
    return s  # level


def build_feat(conn, comps, grid, znmp, ff):
    """Load each component -> grid -> sign*transform -> zn PIT. + 2 NOISE cols."""
    series, dropped = {}, []
    for sid, sign, tf in comps:
        s = load_db_series(conn, sid)
        if s is None or s.empty:
            dropped.append(sid)
            continue
        series[sid] = transform_series(to_grid(s, grid), tf) * sign
    if not series:
        return None, [], None, dropped
    full = pd.DatetimeIndex([])
    for s in series.values():
        full = full.union(s.index)
    full = full.sort_values()
    feat = pd.DataFrame(index=full)
    pnames = []
    for sid, s in series.items():
        feat[sid] = zn(s.reindex(full).ffill(limit=ff), min_periods=znmp)
        pnames.append(sid)
    rng = np.random.default_rng(NOISE_SEED)
    for k in (1, 2):
        feat[f"NOISE{k}"] = zn(pd.Series(rng.standard_normal(len(full)),
                                         index=full), min_periods=znmp)
    sig_idx = feat[pnames].dropna(how="all").index
    return feat, pnames, sig_idx, dropped


def validate_one(conn, cand):
    name = cand["name"]
    comps = [(c[0], int(c[1]), c[2]) for c in cand["components"]]
    spec = cand["target"]
    grid = grid_of(spec["kind"])
    mt, rf = ((MIN_TRAIN_M, REFIT_M) if grid == "M" else (MIN_TRAIN_B, REFIT_B))
    znmp = 24 if grid == "M" else 252
    ff = FFILL_M if grid == "M" else FFILL_B

    feat, pnames, sig_idx, dropped = build_feat(conn, comps, grid, znmp, ff)
    if feat is None or len(pnames) < 1:
        return dict(name=name, status="degenerate", dropped=dropped)
    tgt, h_steps = build_target(conn, spec, sig_idx, grid)
    if tgt is None or tgt.dropna().empty:
        return dict(name=name, status="no_target", target=spec, dropped=dropped)

    wf = walk_forward(feat.reindex(sig_idx), tgt.reindex(sig_idx),
                      pnames, h_steps, mt, rf)
    ic = wf.get("oos_ic")
    nr = wf.get("noise_ratio")
    n = wf.get("n_oos_noov") or 0
    if wf.get("status") != "ok" or ic is None:
        verdict = "DEMOTE"
    elif nr is not None and nr >= 0.5:
        verdict = "NOISE"
    elif abs(ic) < SKILL_FLOOR:
        verdict = "DEMOTE"
    elif n >= 50:
        verdict = "VALIDATED"
    else:
        verdict = "PROVISIONAL"
    return dict(
        name=name, target=f"{spec['kind']}:{spec['tgt']}@{spec['h']}",
        status=wf.get("status"),
        oos_ic=round(ic, 3) if ic is not None else None,
        oos_ic_overlap=(round(wf["oos_ic_overlap"], 3)
                        if wf.get("oos_ic_overlap") is not None else None),
        oos_rank_ic=(round(wf["oos_rank_ic"], 3)
                     if wf.get("oos_rank_ic") is not None else None),
        noise_ratio=round(nr, 3) if nr is not None else None,
        n_oos=n, components=len(pnames), dropped=dropped, verdict=verdict,
    )


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    cands = json.loads(Path(sys.argv[1]).read_text())
    out_path = Path(sys.argv[2]) if len(sys.argv) > 2 else None
    conn = sqlite3.connect(DB)
    results = []
    for c in cands:
        try:
            r = validate_one(conn, c)
        except Exception as e:  # noqa: BLE001
            r = dict(name=c.get("name", "?"), status="error", error=str(e)[:200])
        results.append(r)

        def _f(x):
            return f"{x:>6}" if x is not None else f"{'—':>6}"
        print(f"{r.get('verdict', r.get('status', '?')):<11} "
              f"{r['name'][:42]:<42} "
              f"ic={_f(r.get('oos_ic'))} ov={_f(r.get('oos_ic_overlap'))} "
              f"noise={_f(r.get('noise_ratio'))} "
              f"n={r.get('n_oos', 0):>5}  -> {r.get('target', r.get('status', ''))}")
    conn.close()
    if out_path:
        out_path.write_text(json.dumps(results, indent=2))
        print(f"\nWrote {out_path}")
    v = sum(1 for r in results if r.get("verdict") == "VALIDATED")
    p = sum(1 for r in results if r.get("verdict") == "PROVISIONAL")
    print(f"\nVALIDATED: {v} | PROVISIONAL: {p} | total: {len(results)}")


if __name__ == "__main__":
    main()
