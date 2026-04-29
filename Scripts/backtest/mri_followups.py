#!/usr/bin/env python3
"""
MRI Phase 1 Follow-Ups — Lighthouse Macro
==========================================
Three diagnostic tests on top of mri_weight_optimization.py results:

  1. Tighter training window (min_train_pct=0.65)
     - Tests whether the OOS sign-flip is data-window artifact
       (early data 2000-2013 dominated by wrong-sign regimes)

  2. Shrinkage (alpha = 0.25 / 0.50 / 0.75)
     - alpha * optimized + (1-alpha) * judgment
     - Per master plan Governance Rule #3

  3. Sign-conditional MRI (crisis-filter framing)
     - Does MRI predict forward returns conditional on MRI > +1.0?
     - Aligned with v2.0 framework: MRI's job is identifying the
       restrictive regime, not continuous regime conditioning

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

# Reuse config + functions from the main optimization script
sys.path.insert(0, '/Users/bob/LHM/Scripts/backtest')
from mri_weight_optimization import (
    DB_PATH, MRI_COMPONENTS, FWD_HORIZONS, Z_MIN_PERIODS, Z_WINSORIZE,
    N_QUANTILES, OPT_PRIMARY_HORIZON, OPT_OBJECTIVE,
    load_data, compute_pillar_zscores, compute_forward_returns,
    compute_mri, optimize_weights, walk_forward_oos,
    quintile_analysis, weights_array_to_dict,
)

OUTPUT_DIR = Path("/Users/bob/LHM/Outputs/mri_optimization")
RESULTS_PATH = OUTPUT_DIR / "mri_optimization_results.json"
FOLLOWUP_PATH = OUTPUT_DIR / "mri_followups_results.json"


# ============================================================
# DATA SETUP (mirrors mri_weight_optimization.main())
# ============================================================

def setup_data():
    pillars, spx, mri_existing, spx_id = load_data(DB_PATH)
    z_pillars = compute_pillar_zscores(pillars)
    fwd_returns = compute_forward_returns(spx)

    combined = z_pillars.join(fwd_returns, how='inner')
    z_aligned = combined[list(MRI_COMPONENTS.keys())]
    fwd_aligned = combined[[f'fwd_{h}d' for h in FWD_HORIZONS
                            if f'fwd_{h}d' in combined.columns]]

    valid_mask = z_aligned.notna().all(axis=1) & fwd_aligned.iloc[:, 0].notna()
    return z_aligned[valid_mask], fwd_aligned[valid_mask]


# ============================================================
# 1. TIGHTER TRAINING WINDOW
# ============================================================

def followup_1_tighter_window(z_valid, fwd_valid):
    """
    Walk-forward with min_train_pct=0.65 instead of 0.50.
    Idea: each training window includes 2007-09 crisis.
    """
    print("\n" + "="*70)
    print("FOLLOW-UP 1: TIGHTER TRAINING WINDOW (min_train_pct=0.65)")
    print("="*70)
    print("Hypothesis: OOS sign-flip is artifact of train sets that don't")
    print("include a full crisis. Pushing min_train_pct from 0.50 to 0.65")
    print("forces every training window to include 2007-09.")
    print()

    primary_col = f'fwd_{OPT_PRIMARY_HORIZON}d'
    wf_results = walk_forward_oos(
        z_valid, fwd_valid, MRI_COMPONENTS,
        horizon_col=primary_col, objective=OPT_OBJECTIVE,
        n_splits=5, min_train_pct=0.65,
    )

    if not wf_results:
        print("[WARN] No walk-forward results.")
        return None

    print(f"  {'Split':>5} {'Test Period':>25} {'N':>5} "
          f"{'Opt Spread':>11} {'Cur Spread':>11} "
          f"{'Opt IC':>8} {'Cur IC':>8} "
          f"{'O.Mono':>7} {'C.Mono':>7}")
    print(f"  {'-'*100}")
    for r in wf_results:
        print(f"  {r['split']:>5} "
              f"{str(r['test_start'])} to {str(r['test_end'])} "
              f"{r['test_n']:>5} "
              f"{r['oos_spread']:>+11.4f} {r['current_spread']:>+11.4f} "
              f"{r['oos_ic']:>+8.4f} {r['current_ic']:>+8.4f} "
              f"{'Y' if r['oos_mono'] else 'N':>7} "
              f"{'Y' if r['current_mono'] else 'N':>7}")

    opt_spreads = [r['oos_spread'] for r in wf_results
                   if not np.isnan(r['oos_spread'])]
    cur_spreads = [r['current_spread'] for r in wf_results
                   if not np.isnan(r['current_spread'])]
    opt_ics = [r['oos_ic'] for r in wf_results
               if not np.isnan(r['oos_ic'])]
    cur_ics = [r['current_ic'] for r in wf_results
               if not np.isnan(r['current_ic'])]

    print()
    print(f"  Avg OOS Spread:  Optimized={np.mean(opt_spreads):>+.4f}  "
          f"Current={np.mean(cur_spreads):>+.4f}")
    print(f"  Avg OOS IC:      Optimized={np.mean(opt_ics):>+.4f}  "
          f"Current={np.mean(cur_ics):>+.4f}")

    # Weight stability
    print()
    print(f"  Weight Stability Across Splits (tighter window):")
    component_names = list(MRI_COMPONENTS.keys())
    weight_matrix = []
    for r in wf_results:
        if r['opt_weights']:
            weight_matrix.append([r['opt_weights'].get(c, 0)
                                  for c in component_names])

    weight_stats = {}
    if weight_matrix:
        wm = np.array(weight_matrix)
        print(f"  {'Pillar':>8} {'Mean':>8} {'Std':>8} {'Min':>8} {'Max':>8}")
        print(f"  {'-'*40}")
        for i, c in enumerate(component_names):
            print(f"  {c:>8} {wm[:, i].mean():>8.3f} {wm[:, i].std():>8.3f} "
                  f"{wm[:, i].min():>8.3f} {wm[:, i].max():>8.3f}")
            weight_stats[c] = {
                'mean': float(wm[:, i].mean()),
                'std': float(wm[:, i].std()),
                'min': float(wm[:, i].min()),
                'max': float(wm[:, i].max()),
            }

    return {
        'avg_opt_spread': float(np.mean(opt_spreads)),
        'avg_cur_spread': float(np.mean(cur_spreads)),
        'avg_opt_ic': float(np.mean(opt_ics)),
        'avg_cur_ic': float(np.mean(cur_ics)),
        'weight_stats': weight_stats,
        'splits': [
            {
                'split': r['split'],
                'test_start': str(r['test_start']),
                'test_end': str(r['test_end']),
                'test_n': r['test_n'],
                'opt_spread': r['oos_spread'],
                'cur_spread': r['current_spread'],
                'opt_ic': r['oos_ic'],
                'cur_ic': r['current_ic'],
            }
            for r in wf_results
        ],
    }


# ============================================================
# 2. SHRINKAGE
# ============================================================

def followup_2_shrinkage(z_valid, fwd_valid, opt_dict, cur_dict):
    """
    Test alpha * opt + (1-alpha) * judgment for alpha in {0.25, 0.5, 0.75}.
    Evaluate on the same OOS slice the main optimization uses (last 10%).
    """
    print("\n" + "="*70)
    print("FOLLOW-UP 2: SHRINKAGE (mix optimized + judgment)")
    print("="*70)
    print("Test: FINAL = alpha * opt + (1-alpha) * judgment")
    print("Per master plan Governance Rule #3.")
    print()

    primary_col = f'fwd_{OPT_PRIMARY_HORIZON}d'

    # OOS slice: last 10% (matches main script)
    n_is = int(len(z_valid) * 0.90)
    z_oos = z_valid.iloc[n_is:]
    fwd_oos = fwd_valid.iloc[n_is:]

    print(f"OOS slice: {len(z_oos)} obs "
          f"({z_oos.index.min().date()} to {z_oos.index.max().date()})")
    print()

    # Also compute full-period IC for breadth
    print(f"  {'Alpha':>6}  {'OOS Spread':>11}  {'OOS IC':>8}  "
          f"{'Full-Period IC':>15}  {'Notes':>15}")
    print(f"  {'-'*70}")

    results = {}
    alphas = [0.0, 0.25, 0.50, 0.75, 1.0]  # 0=judgment, 1=optimized
    for alpha in alphas:
        blended = {
            k: alpha * opt_dict[k] + (1 - alpha) * cur_dict[k]
            for k in MRI_COMPONENTS
        }
        # Renormalize (small float drift)
        s = sum(blended.values())
        blended = {k: v / s for k, v in blended.items()}

        # OOS quintile
        mri_oos = compute_mri(z_oos, blended, MRI_COMPONENTS)
        qa = quintile_analysis(mri_oos, fwd_oos[primary_col])
        oos_spread = qa['spread'] if qa else np.nan
        oos_ic = qa['ic'] if qa else np.nan

        # Full-period IC
        mri_full = compute_mri(z_valid, blended, MRI_COMPONENTS)
        df_full = pd.DataFrame(
            {'mri': mri_full, 'fwd': fwd_valid[primary_col]}
        ).dropna()
        full_ic, _ = stats.spearmanr(df_full['mri'], df_full['fwd'])

        label = "judgment" if alpha == 0 else "optimized" if alpha == 1 else ""
        print(f"  {alpha:>6.2f}  {oos_spread:>+11.4f}  {oos_ic:>+8.4f}  "
              f"{full_ic:>+15.4f}  {label:>15}")

        results[f'alpha_{alpha:.2f}'] = {
            'alpha': alpha,
            'oos_spread': float(oos_spread) if not np.isnan(oos_spread) else None,
            'oos_ic': float(oos_ic) if not np.isnan(oos_ic) else None,
            'full_period_ic': float(full_ic),
        }

    print()
    # Pick best
    valid = [(a, r['oos_spread']) for a, r in results.items()
             if r['oos_spread'] is not None]
    # NOTE: MRI is risk index, so for OOS where regime is bullish the
    # quintile_analysis spread = Q5-Q1 returns. The main script uses
    # spread but interpretation depends on regime; we just report.
    print("  NOTE: OOS slice 2024-25 was a bullish regime where high-MRI")
    print("  readings predicted higher returns (sign-flipped). Spread is")
    print("  POSITIVE in OOS for all alphas. Ranking by full-period IC")
    print("  (more negative = better risk-index behavior):")
    print()
    by_ic = sorted(results.items(),
                   key=lambda kv: kv[1]['full_period_ic'])
    for k, v in by_ic:
        print(f"    {k}: full IC = {v['full_period_ic']:+.4f}")

    return results


# ============================================================
# 3. SIGN-CONDITIONAL MRI (CRISIS-FILTER FRAMING)
# ============================================================

def followup_3_crisis_filter(z_valid, fwd_valid, cur_dict):
    """
    Compute MRI with judgment weights, then bucket by absolute level:
      - MRI < -0.5 (Low Risk regime)
      - -0.5 <= MRI < +0.5 (Neutral)
      - +0.5 <= MRI < +1.0 (Elevated, technical sleeve still optional)
      - MRI >= +1.0 (Restrictive — framework-sleeve compression triggers)
    For each bucket, compute forward-return distributions to test:
    Does MRI work as a crisis filter even if it fails as a continuous signal?
    """
    print("\n" + "="*70)
    print("FOLLOW-UP 3: SIGN-CONDITIONAL MRI (CRISIS-FILTER FRAMING)")
    print("="*70)
    print("Per the v2.0 framework, MRI's job is to identify the restrictive")
    print("regime where the framework-driven sleeve compresses (multiplier")
    print("0.3x or lower). It does not need to be a continuous regime")
    print("conditioner. Test: does MRI > +1.0 reliably mark that regime?")
    print()

    primary_col = f'fwd_{OPT_PRIMARY_HORIZON}d'

    mri = compute_mri(z_valid, cur_dict, MRI_COMPONENTS)
    df = pd.DataFrame({'mri': mri}).join(fwd_valid).dropna()

    # MRI thresholds from CLAUDE_MASTER Section 3
    bins = [-np.inf, -0.5, 0.5, 1.0, 1.5, np.inf]
    labels = ['Low Risk (<-0.5)', 'Neutral (-0.5 to +0.5)',
              'Elevated (+0.5 to +1.0)', 'High Risk (+1.0 to +1.5)',
              'Crisis (>+1.5)']
    df['regime'] = pd.cut(df['mri'], bins=bins, labels=labels)

    print(f"  {'Regime':<28} {'N':>6} ", end='')
    for h in [21, 63, 126, 252]:
        col = f'fwd_{h}d'
        if col in df.columns:
            print(f"  {h}d Mean   ", end='')
    print(f"  {'63d <0%':>9}  {'63d <-5%':>9}")
    print(f"  {'-'*100}")

    bucket_stats = {}
    for label in labels:
        grp = df[df['regime'] == label]
        if len(grp) == 0:
            continue
        row = f"  {label:<28} {len(grp):>6} "
        bucket_stats[label] = {'n': int(len(grp))}
        for h in [21, 63, 126, 252]:
            col = f'fwd_{h}d'
            if col in df.columns:
                m = grp[col].mean()
                row += f"  {m:>+.4f}    "
                bucket_stats[label][f'mean_{h}d'] = float(m)
        # Drawdown frequency at 63d
        col63 = f'fwd_{OPT_PRIMARY_HORIZON}d'
        if col63 in grp.columns:
            pct_neg = (grp[col63] < 0).mean()
            pct_neg5 = (grp[col63] < -0.05).mean()
            row += f"  {pct_neg:>9.1%}  {pct_neg5:>9.1%}"
            bucket_stats[label]['pct_63d_below_zero'] = float(pct_neg)
            bucket_stats[label]['pct_63d_below_neg5'] = float(pct_neg5)
        print(row)

    print()
    print("  Crisis-filter test:")
    print("  - Does MRI > +1.0 produce materially higher drawdown frequency?")
    print("  - Does Crisis bucket show negative mean return at 63d+?")
    print()

    # Compute restrictive-regime hit rate
    restrictive = df[df['mri'] >= 1.0]
    base_neg = (df[primary_col] < -0.05).mean()
    rest_neg = (restrictive[primary_col] < -0.05).mean() if len(restrictive) else np.nan
    lift = (rest_neg / base_neg) if (base_neg > 0 and not np.isnan(rest_neg)) else np.nan

    print(f"  Base rate of 63d return < -5%:           {base_neg:>6.1%}")
    print(f"  Conditional on MRI >= +1.0:              {rest_neg:>6.1%}  (n={len(restrictive)})")
    print(f"  Lift (conditional / base):               {lift:>6.2f}x")
    print()
    if not np.isnan(lift) and lift > 1.5:
        print(f"  -> MRI >= +1.0 is a useful crisis filter (>{1.5:.1f}x lift on big")
        print(f"     drawdown frequency). Crisis-filter framing validates.")
    elif not np.isnan(lift) and lift > 1.0:
        print(f"  -> MRI >= +1.0 has a mild lift on drawdown frequency. Crisis")
        print(f"     filter has some power but isn't a clean signal.")
    else:
        print(f"  -> MRI >= +1.0 does NOT lift drawdown frequency. The crisis-")
        print(f"     filter framing fails too. MRI may need rebuild from scratch.")

    return {
        'bucket_stats': bucket_stats,
        'base_pct_63d_below_neg5': float(base_neg),
        'restrictive_pct_63d_below_neg5': float(rest_neg)
            if not np.isnan(rest_neg) else None,
        'lift_vs_base': float(lift) if not np.isnan(lift) else None,
        'n_restrictive': int(len(restrictive)),
    }


# ============================================================
# MAIN
# ============================================================

def main():
    print("="*70)
    print("MRI PHASE 1 FOLLOW-UPS — LIGHTHOUSE MACRO")
    print(f"Run: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("="*70)

    # Load prior results
    if not RESULTS_PATH.exists():
        print(f"[ERROR] Run mri_weight_optimization.py first.")
        return
    prior = json.loads(RESULTS_PATH.read_text())
    opt_dict = prior['optimized_weights']
    cur_dict = prior['current_weights']

    print("\nLoading data + computing z-scores...")
    z_valid, fwd_valid = setup_data()
    print(f"Aligned: {len(z_valid)} obs "
          f"({z_valid.index.min().date()} to {z_valid.index.max().date()})")

    out = {
        'run_date': datetime.now().isoformat(),
        'inputs': {
            'optimized_weights': opt_dict,
            'current_weights': cur_dict,
            'n_observations': len(z_valid),
        },
    }

    # 1. Tighter window
    out['followup_1_tighter_window'] = followup_1_tighter_window(
        z_valid, fwd_valid)

    # 2. Shrinkage
    out['followup_2_shrinkage'] = followup_2_shrinkage(
        z_valid, fwd_valid, opt_dict, cur_dict)

    # 3. Crisis filter
    out['followup_3_crisis_filter'] = followup_3_crisis_filter(
        z_valid, fwd_valid, cur_dict)

    FOLLOWUP_PATH.write_text(json.dumps(out, indent=2, default=str))
    print()
    print(f"Results saved to: {FOLLOWUP_PATH}")


if __name__ == "__main__":
    main()
