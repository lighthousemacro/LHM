#!/usr/bin/env python3
"""
Per-Pillar Weight Optimization v2 — tighter bounds + shrinkage
================================================================
v1 found optimization corner solutions (max weight = 0.40 bound).
v2 tightens bounds to [0.05, 0.30] AND tests shrinkage at alpha = 0.5
for the three pillars that showed meaningful improvement (LPI, PCI, BCI).

For pillars where v1 said "keep judgment", we don't re-test. For the
three candidates, we report:
  - alpha = 0.0 (judgment)
  - alpha = 0.25
  - alpha = 0.50
  - alpha = 0.75
  - alpha = 1.0 (full optimization with new bounds)

Author: Lighthouse Macro
Date: 2026-04-29
"""

import json
import sqlite3
import sys
import warnings
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from scipy.optimize import minimize

warnings.filterwarnings('ignore')

sys.path.insert(0, '/Users/bob/LHM/Scripts/backtest')
from pillar_weight_optimization import (
    DB_PATH, PILLAR_SPECS,
    build_components, build_target,
    expanding_zscore, evaluate_weights,
    compute_composite,
)

OUTPUT_DIR = Path("/Users/bob/LHM/Outputs/mri_optimization")
OUT_PATH = OUTPUT_DIR / "pillar_weight_optimization_v2.json"

# Tighter bounds
NEW_BOUNDS = (0.05, 0.30)


def neg_abs_rank_ic(w, z, target):
    w = np.abs(w)
    if w.sum() <= 0:
        return 1e6
    w = w / w.sum()
    composite = z.values @ w
    df = pd.DataFrame({'sig': composite, 'fwd': target.values}, index=z.index).dropna()
    if len(df) < 250:
        return 1e6
    ic, _ = stats.spearmanr(df['sig'], df['fwd'])
    if np.isnan(ic):
        return 1e6
    return -abs(ic)


def optimize_with_bounds(z_components, target, bounds, n_restarts=30):
    n = z_components.shape[1]
    bnds = [bounds] * n
    cons = [{'type': 'eq', 'fun': lambda w: np.sum(np.abs(w)) - 1.0}]
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
            res = minimize(neg_abs_rank_ic, w0, args=(z_components, target),
                           method='SLSQP', bounds=bnds, constraints=cons,
                           options={'maxiter': 300, 'ftol': 1e-9})
            if res.fun < best_obj:
                best_obj = res.fun
                best = res
        except Exception:
            pass
    if best is None:
        return None
    w = np.abs(best.x) / np.abs(best.x).sum()
    return {c: float(w[i]) for i, c in enumerate(z_components.columns)}


def main():
    print("="*70)
    print(f"PILLAR WEIGHT OPT v2 — bounds={NEW_BOUNDS}")
    print(f"Run: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("="*70)

    # Re-test only the three "adopt" candidates from v1 plus PCI's instability
    pillars_to_retest = ['LPI', 'PCI', 'BCI']

    conn = sqlite3.connect(DB_PATH)
    out = {'run_date': datetime.now().isoformat(), 'pillars': {}}

    for name in pillars_to_retest:
        spec = PILLAR_SPECS[name]
        print(f"\n{'='*70}\n{name}\n{'='*70}")

        z_comp, _ = build_components(conn, spec)
        target, _ = build_target(conn, spec)
        aligned = z_comp.join(target.rename('fwd')).dropna()
        z_aligned = aligned[z_comp.columns]
        fwd_aligned = aligned['fwd']
        n = len(aligned)
        print(f"Aligned: {n}")

        # Build judgment weights
        has_j = any(c[3] is not None for c in spec['components'])
        if has_j:
            spec_total = sum(c[3] for c in spec['components'] if c[3] is not None)
            unspec = [c[0] for c in spec['components'] if c[3] is None]
            remaining = max(0, 1 - spec_total)
            per_unspec = remaining / max(len(unspec), 1)
            judgment = {sid: (w if w is not None else per_unspec)
                        for sid, sign, mode, w in spec['components']
                        if sid in z_aligned.columns}
            s = sum(judgment.values())
            judgment = {k: v / s for k, v in judgment.items()}
        else:
            judgment = {c: 1.0 / len(z_aligned.columns) for c in z_aligned.columns}

        # 90/10 split
        n_is = int(n * 0.9)
        z_is = z_aligned.iloc[:n_is]
        fwd_is = fwd_aligned.iloc[:n_is]
        z_oos = z_aligned.iloc[n_is:]
        fwd_oos = fwd_aligned.iloc[n_is:]

        # Optimize on IS with new bounds
        opt_w = optimize_with_bounds(z_is, fwd_is, NEW_BOUNDS, n_restarts=30)
        if opt_w is None:
            print("[FAIL] opt failed")
            continue

        # Test alphas
        print(f"\n{'Alpha':>6}  {'Full IC':>10}  {'OOS IC':>10}  "
              f"{'Max W':>7}")
        print(f"  {'-'*45}")

        results = {}
        for alpha in [0.0, 0.25, 0.5, 0.75, 1.0]:
            blended = {
                k: alpha * opt_w[k] + (1 - alpha) * judgment[k]
                for k in opt_w
            }
            s = sum(blended.values())
            blended = {k: v / s for k, v in blended.items()}
            full_eval = evaluate_weights(z_aligned, fwd_aligned, blended)
            oos_eval = evaluate_weights(z_oos, fwd_oos, blended)
            mx = max(blended.values())
            full_ic = full_eval['ic'] if full_eval else np.nan
            oos_ic = oos_eval['ic'] if oos_eval else np.nan
            print(f"  {alpha:>5.2f}  {full_ic:>+10.4f}  {oos_ic:>+10.4f}  "
                  f"{mx:>7.3f}")
            results[f'alpha_{alpha}'] = {
                'alpha': alpha,
                'weights': blended,
                'full_ic': float(full_ic),
                'oos_ic': float(oos_ic) if not np.isnan(oos_ic) else None,
                'max_weight': float(mx),
            }

        # Best alpha by OOS magnitude
        valid = [(a, r) for a, r in results.items() if r['oos_ic'] is not None]
        if valid:
            best = max(valid, key=lambda kv: abs(kv[1]['oos_ic']))
            print(f"\n  Best alpha by |OOS IC|: {best[0]} "
                  f"(ic={best[1]['oos_ic']:+.4f}, max_w={best[1]['max_weight']:.3f})")

        out['pillars'][name] = {
            'optimized_weights': opt_w,
            'judgment_weights': judgment,
            'alpha_results': results,
            'bounds': list(NEW_BOUNDS),
        }

    conn.close()
    OUT_PATH.write_text(json.dumps(out, indent=2, default=str))
    print(f"\nSaved to: {OUT_PATH}")


if __name__ == "__main__":
    main()
