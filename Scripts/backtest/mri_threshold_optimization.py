#!/usr/bin/env python3
"""
MRI Threshold Optimization — Lighthouse Macro
==============================================
Reframe: MRI's job is identifying the restrictive regime, not continuous
regime conditioning. Find the cleanest threshold for the framework-sleeve
compression trigger.

Sweep MRI thresholds from -0.5 to +2.0 in 0.1 steps. For each threshold,
compute:
  - n observations above threshold
  - 63d drawdown frequency (% with fwd_63d < -5%) above threshold
  - 63d drawdown frequency (% with fwd_63d < -10%) above threshold
  - Lift vs base rate
  - Mean forward 63d/126d/252d return above threshold

Output: clean break-points + recommendation for new regime table.

Author: Lighthouse Macro
Date: 2026-04-29
"""

import json
import sys
import warnings
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

warnings.filterwarnings('ignore')

sys.path.insert(0, '/Users/bob/LHM/Scripts/backtest')
from mri_weight_optimization import (
    DB_PATH, MRI_COMPONENTS, FWD_HORIZONS, OPT_PRIMARY_HORIZON,
    load_data, compute_pillar_zscores, compute_forward_returns,
    compute_mri,
)

OUTPUT_DIR = Path("/Users/bob/LHM/Outputs/mri_optimization")
OUT_PATH = OUTPUT_DIR / "mri_threshold_results.json"


def setup():
    pillars, spx, _, _ = load_data(DB_PATH)
    z_pillars = compute_pillar_zscores(pillars)
    fwd_returns = compute_forward_returns(spx)
    combined = z_pillars.join(fwd_returns, how='inner')
    z = combined[list(MRI_COMPONENTS.keys())]
    f = combined[[f'fwd_{h}d' for h in FWD_HORIZONS
                  if f'fwd_{h}d' in combined.columns]]
    valid = z.notna().all(axis=1) & f.iloc[:, 0].notna()
    return z[valid], f[valid]


def main():
    print("="*70)
    print("MRI THRESHOLD OPTIMIZATION")
    print(f"Run: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("="*70)

    z_valid, fwd_valid = setup()
    cur_dict = {k: v['current_weight'] for k, v in MRI_COMPONENTS.items()}
    mri = compute_mri(z_valid, cur_dict, MRI_COMPONENTS)

    df = pd.DataFrame({'mri': mri}).join(fwd_valid).dropna()
    print(f"\nAligned: {len(df)} obs "
          f"({df.index.min().date()} to {df.index.max().date()})")

    primary_col = f'fwd_{OPT_PRIMARY_HORIZON}d'
    base_dd5 = (df[primary_col] < -0.05).mean()
    base_dd10 = (df[primary_col] < -0.10).mean()
    base_neg = (df[primary_col] < 0).mean()
    print(f"Base rates (full sample):")
    print(f"  63d return < 0%:    {base_neg:>6.1%}")
    print(f"  63d return < -5%:   {base_dd5:>6.1%}")
    print(f"  63d return < -10%:  {base_dd10:>6.1%}")
    print()

    print("MRI threshold sweep (test = obs above threshold):")
    print(f"  {'Thresh':>7}  {'N':>5}  {'%pop':>5}  "
          f"{'63d Mean':>9}  {'%neg':>6}  {'%<-5':>6}  {'%<-10':>6}  "
          f"{'Lift5':>6}  {'Lift10':>7}")
    print(f"  {'-'*85}")

    sweep = []
    n_total = len(df)
    for thresh in np.arange(-0.5, 2.1, 0.1):
        thresh = round(thresh, 2)
        sub = df[df['mri'] >= thresh]
        n = len(sub)
        if n < 20:
            continue
        pct_pop = n / n_total
        mean63 = sub[primary_col].mean()
        pct_neg = (sub[primary_col] < 0).mean()
        pct_dd5 = (sub[primary_col] < -0.05).mean()
        pct_dd10 = (sub[primary_col] < -0.10).mean()
        lift5 = pct_dd5 / base_dd5 if base_dd5 > 0 else np.nan
        lift10 = pct_dd10 / base_dd10 if base_dd10 > 0 else np.nan

        print(f"  {thresh:>+7.2f}  {n:>5}  {pct_pop:>5.1%}  "
              f"{mean63:>+9.4f}  {pct_neg:>6.1%}  {pct_dd5:>6.1%}  "
              f"{pct_dd10:>6.1%}  {lift5:>6.2f}  {lift10:>7.2f}")

        sweep.append({
            'threshold': thresh, 'n': n, 'pct_population': float(pct_pop),
            'mean_63d': float(mean63),
            'pct_neg_63d': float(pct_neg),
            'pct_below_neg5_63d': float(pct_dd5),
            'pct_below_neg10_63d': float(pct_dd10),
            'lift_5pct': float(lift5),
            'lift_10pct': float(lift10),
        })

    # Find natural break points: where lift_10pct jumps materially
    print("\n" + "="*70)
    print("BREAK-POINT ANALYSIS")
    print("="*70)
    print("Looking for monotonic acceleration in lift_10pct across thresholds.")
    print()

    # Compute marginal change in lift between successive thresholds
    if len(sweep) >= 2:
        print(f"  {'From':>6} {'To':>6}  {'dLift10':>8}  {'New Lift10':>10}")
        print(f"  {'-'*45}")
        for i in range(1, len(sweep)):
            t0 = sweep[i-1]['threshold']
            t1 = sweep[i]['threshold']
            d = sweep[i]['lift_10pct'] - sweep[i-1]['lift_10pct']
            print(f"  {t0:>+6.2f} {t1:>+6.2f}  {d:>+8.2f}  "
                  f"{sweep[i]['lift_10pct']:>10.2f}")

    # Recommendation: pick the lowest threshold with lift_10pct >= 2.0
    candidates = [s for s in sweep if s['lift_10pct'] >= 2.0 and s['n'] >= 30]
    print()
    if candidates:
        best = candidates[0]  # lowest threshold meeting the bar
        print(f"RECOMMENDED RESTRICTIVE THRESHOLD: MRI >= {best['threshold']:+.2f}")
        print(f"  - n={best['n']} ({best['pct_population']:.1%} of sample)")
        print(f"  - 63d return mean: {best['mean_63d']:+.2%}")
        print(f"  - 63d <0% rate: {best['pct_neg_63d']:.1%}")
        print(f"  - 63d <-5% rate: {best['pct_below_neg5_63d']:.1%} "
              f"(lift {best['lift_5pct']:.2f}x)")
        print(f"  - 63d <-10% rate: {best['pct_below_neg10_63d']:.1%} "
              f"(lift {best['lift_10pct']:.2f}x)")
    else:
        print("No threshold meets the lift>=2.0 bar with n>=30.")
        print("MRI may not be tradeable as a binary restrictive signal.")
        best = None

    # Three-regime cuts
    print()
    print("THREE-REGIME RECOMMENDATION (v2.0 framework):")
    cuts = []
    for low, high, name in [
        (-np.inf, -0.5, 'Supportive'),
        (-0.5, 1.0, 'Neutral'),
        (1.0, np.inf, 'Restrictive'),
    ]:
        sub = df[(df['mri'] >= low) & (df['mri'] < high)]
        if len(sub) == 0:
            continue
        cuts.append({
            'name': name,
            'mri_low': None if low == -np.inf else float(low),
            'mri_high': None if high == np.inf else float(high),
            'n': int(len(sub)),
            'pct_pop': float(len(sub) / n_total),
            'mean_63d': float(sub[primary_col].mean()),
            'pct_below_neg5': float((sub[primary_col] < -0.05).mean()),
            'pct_below_neg10': float((sub[primary_col] < -0.10).mean()),
        })
        print(f"  {name:<12} ({low:+.1f} to {high:+.1f}): "
              f"n={len(sub):>5}  "
              f"63d mean {sub[primary_col].mean():+.2%}  "
              f"<-5%: {(sub[primary_col] < -0.05).mean():.1%}  "
              f"<-10%: {(sub[primary_col] < -0.10).mean():.1%}")

    out = {
        'run_date': datetime.now().isoformat(),
        'n_observations': len(df),
        'sample_range': [str(df.index.min().date()),
                         str(df.index.max().date())],
        'base_rates': {
            'pct_neg_63d': float(base_neg),
            'pct_below_neg5_63d': float(base_dd5),
            'pct_below_neg10_63d': float(base_dd10),
        },
        'sweep': sweep,
        'recommended_threshold': best,
        'three_regime_cuts': cuts,
    }
    OUT_PATH.write_text(json.dumps(out, indent=2, default=str))
    print(f"\nSaved to: {OUT_PATH}")


if __name__ == "__main__":
    main()
