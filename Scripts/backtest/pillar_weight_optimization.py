#!/usr/bin/env python3
"""
Per-Pillar Weight Optimization — Lighthouse Macro
====================================================
For each of the 12 pillars, rebuild the composite from raw components
and optimize the weights against the pillar's DOMAIN target (not
forward equity returns — per master plan rule for Tier B).

Methodology per master plan Phase 3:
  - Pull component series, z-score (expanding, min 63, ±3 winsorize)
  - Apply theoretical sign per CLAUDE_MASTER Section 3
  - Optimize weights via rank IC (Spearman) — Sortino on Q-spread is
    for return targets, not domain targets
  - Bounds [0.02, 0.40] per weight, sum to 1, SLSQP, 30 restarts
  - 90/10 IS/OOS split
  - Compare optimized vs judgment vs equal-weight

Adoption rule (per master plan):
  - OOS rank IC magnitude improves >= 10% over judgment, AND
  - walk-forward weight std < 0.06 for all but 1-2 weights, AND
  - no single weight > 0.30 (>0.40 is the search bound)

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

DB_PATH = "/Users/bob/LHM/Data/databases/Lighthouse_Master.db"
OUTPUT_DIR = Path("/Users/bob/LHM/Outputs/mri_optimization")
OUT_PATH = OUTPUT_DIR / "pillar_weight_optimization.json"

# Z-score parameters (CLI standard)
Z_MIN_PERIODS = 63
Z_WINSORIZE = 3.0

# Pillar specifications. Each pillar:
#   components: list of (series_id, sign, transform, current_weight)
#       sign = +1 or -1 (theoretical direction; e.g. -1 for Quits in LPI)
#       transform = 'level', 'yoy_pct', 'delta', 'log_yoy'
#       current_weight = from CLAUDE_MASTER if specified, else None (=> equal weight)
#   target: (series_id, horizon_days, mode, event_threshold)
#       mode: 'delta' = fwd_h - now; 'yoy_pct' = fwd_h pct change YoY
#             'fwd_max_change' = max change over fwd horizon
#   risk_side: 'low' (signal weak = bad) or 'high' (signal strong = bad)

PILLAR_SPECS = {
    'LPI': {
        # CLAUDE_MASTER LFI = 0.35*z(LongTermUnemp%) + 0.35*z(-Quits) + 0.30*z(-Hires/Quits)
        # Broaden: all available labor flow series
        'components': [
            ('UNRATE',    +1, 'level', None),
            ('UEMP27OV',  +1, 'level', 0.35),  # Long-term unemployed
            ('JTSQUR',    -1, 'level', 0.35),  # Quits rate (high = healthy)
            ('JTSHIR',    -1, 'level', None),  # Hires rate
            ('JTSJOL',    -1, 'level', None),  # Job openings
            ('TEMPHELPS', -1, 'yoy_pct', None),  # Temp help (high = healthy)
        ],
        'target': ('UNRATE', 252, 'delta', 0.5),
        'risk_side': 'high',  # high LPI z-score = labor weak (UR will rise)
    },
    'PCI': {
        'components': [
            ('CPIAUCSL', +1, 'yoy_pct', None),  # Headline CPI
            ('CPILFESL', +1, 'yoy_pct', None),  # Core CPI
            ('PCEPILFE', +1, 'yoy_pct', None),  # Core PCE (Fed's target)
            ('CPIHOSSL', +1, 'yoy_pct', None),  # Shelter CPI
            ('TRMMEANCPIM158SFRBCLE', +1, 'yoy_pct', None),  # Trimmed mean
        ],
        'target': ('PCEPILFE', 365, 'yoy_pct_level', None),
        # Use level not delta — PCI should predict where PCE WILL be
        'risk_side': 'high',
    },
    'GCI': {
        'components': [
            ('INDPRO',  +1, 'yoy_pct', None),
            ('PAYEMS',  +1, 'yoy_pct', None),
            ('RSXFS',   +1, 'yoy_pct', None),
            ('TCU',     +1, 'level',   None),  # Capacity utilization
            ('MANEMP',  +1, 'yoy_pct', None),  # Mfg employment
        ],
        'target': ('INDPRO', 252, 'yoy_pct_level', None),
        # IndPro YoY in 252 days — proxy for cycle
        'risk_side': 'low',  # Low GCI = growth weak
    },
    'HCI': {
        'components': [
            ('HOUST',         +1, 'yoy_pct', None),
            ('PERMIT',        +1, 'yoy_pct', None),
            ('HSN1F',         +1, 'yoy_pct', None),
            ('MORTGAGE30US',  -1, 'level',   None),  # High rates = bad housing
            ('MSACSR',        -1, 'level',   None),  # High supply = soft
        ],
        'target': ('HOUST', 365, 'yoy_pct_level', -10.0),
        'risk_side': 'low',
    },
    'CCI': {
        'components': [
            ('RSXFS',   +1, 'yoy_pct', 0.15),
            ('PSAVERT', +1, 'level',   0.20),
            ('UMCSENT', +1, 'level',   0.10),
            ('DSPIC96', +1, 'yoy_pct', 0.10),
            ('REVOLSL', -1, 'yoy_pct', 0.10),  # Rising revolving = stress
            ('PCEDG',   +1, 'yoy_pct', None),
        ],
        # Target: RSXFS YoY since PCEC96 only starts 2007
        'target': ('RSXFS', 252, 'yoy_pct_level', None),
        'risk_side': 'low',
    },
    'BCI': {
        'components': [
            ('NEWORDER', +1, 'yoy_pct', None),
            ('BUSINV',   -1, 'yoy_pct', None),  # Rising inventories = bad
            ('BUSLOANS', +1, 'yoy_pct', None),
            ('GPDIC1',   +1, 'yoy_pct', None),
        ],
        'target': ('NEWORDER', 252, 'yoy_pct_level', None),
        'risk_side': 'low',
    },
    'TCI': {
        'components': [
            ('DTWEXBGS', -1, 'yoy_pct', None),  # Strong dollar = bad for trade
            ('BOPGSTB',  +1, 'level',   None),
            ('NETEXP',   +1, 'level',   None),
        ],
        'target': ('NETEXP', 252, 'delta', 0.0),
        'risk_side': 'low',
    },
    'GCI_Gov': {
        'components': [
            ('THREEFYTP10', +1, 'level', None),  # Term premium
            ('T10Y2Y',      -1, 'level', None),  # Steepener (negative = inverted = stress)
            ('BAA10Y',      +1, 'level', None),  # Credit-treasury spread
            ('DGS10',       +1, 'level', None),
        ],
        'target': ('BAMLH0A0HYM2', 252, 'fwd_max_change', 1.0),
        # Use HY widening as fiscal-stress proxy. HY widens when fiscal/credit pressure spikes.
        'risk_side': 'high',
    },
    'FCI': {
        'components': [
            ('BAMLH0A0HYM2', +1, 'level', None),  # HY OAS
            ('BAMLC0A0CM',   +1, 'level', None),  # IG OAS
            ('VIXCLS',       +1, 'level', None),  # Volatility
            ('BAA10YM',      +1, 'level', None),  # Baa-treasury spread
        ],
        'target': ('BAMLH0A0HYM2', 126, 'fwd_max_change', 1.0),
        'risk_side': 'high',  # high FCI = financial stress already (predicts more widening)
    },
    'LCI': {
        'components': [
            ('TOTRESNS',  +1, 'level',   None),  # Reserves
            ('RRPONTSYD', +1, 'level',   None),  # RRP usage (positive buffer)
            ('WALCL',     +1, 'level',   None),  # Fed balance sheet
            ('WTREGEN',   -1, 'level',   None),  # TGA (high TGA drains reserves)
            ('SOFR',      -1, 'level',   None),  # Funding stress proxy
        ],
        'target': ('BAMLH0A0HYM2', 63, 'fwd_max_change', 1.0),
        'risk_side': 'low',
    },
    'MSI': {
        # MSI components — use only those with full history (skip post-2023 breadth)
        'components': [
            ('SPX_vs_200d_pct', +1, 'level', None),
            ('SPX_vs_50d_pct',  +1, 'level', None),
            ('SPX_50d_slope',   +1, 'level', None),
            ('SPX_20d_slope',   +1, 'level', None),
            ('SPX_Z_RoC_63d',   +1, 'level', None),
        ],
        'target': ('SPX_Close', 63, 'log_fwd_return', None),
        # Different! For MSI, target IS forward equity returns (per master plan exception)
        'risk_side': 'low',  # weak MSI = below-trend, breakdown = bad fwd returns
    },
    'SPI': {
        'components': [
            ('VIXCLS',          +1, 'level', None),
            ('AAII_Bull_Bear_Spread', -1, 'level', None),  # Inverted: bullish = bad fwd returns
            ('VIX_percentile_252d',   +1, 'level', None),
        ],
        # SPI is contrarian. High SPI z = fear = good fwd returns
        # So target: forward SPX returns; expect HIGH SPI -> POSITIVE returns (sign-flip risk)
        'target': ('SPX_Close', 21, 'log_fwd_return', None),
        'risk_side': 'extreme',  # contrarian — both ends matter
    },
}


# ============================================================
# DATA LOADING + TRANSFORMS
# ============================================================

def load_obs(conn, sid):
    df = pd.read_sql(
        "SELECT date, value FROM observations WHERE series_id = ? ORDER BY date",
        conn, params=(sid,), parse_dates=['date']
    ).set_index('date').sort_index()
    return df['value'].dropna()


def transform_series(s, mode, periods=None):
    """Apply transform to series. Returns same-frequency series."""
    if mode == 'level':
        return s
    elif mode == 'yoy_pct':
        # Detect frequency
        freq = pd.infer_freq(s.index[-100:]) if len(s) > 100 else None
        if freq and freq.startswith('M'):
            shift = 12
        elif freq and freq.startswith('Q'):
            shift = 4
        elif freq and freq.startswith('W'):
            shift = 52
        else:
            shift = 252  # daily
        return (s / s.shift(shift) - 1) * 100
    elif mode == 'delta':
        return s.diff()
    elif mode == 'log_yoy':
        return np.log(s / s.shift(252)) * 100
    return s


def expanding_zscore(series, min_periods=Z_MIN_PERIODS, winsorize=Z_WINSORIZE):
    mean = series.expanding(min_periods=min_periods).mean()
    std = series.expanding(min_periods=min_periods).std()
    z = (series - mean) / std.replace(0, np.nan)
    return z.clip(-winsorize, winsorize)


def build_components(conn, spec):
    """Build z-scored, signed component dataframe at daily frequency."""
    parts = {}
    signs = {}
    for sid, sign, mode, _w in spec['components']:
        s = load_obs(conn, sid)
        if s.empty:
            continue
        s_t = transform_series(s, mode)
        s_d = s_t.resample('D').ffill()  # to daily
        z = expanding_zscore(s_d)
        parts[sid] = z * sign
        signs[sid] = sign
    df = pd.DataFrame(parts)
    return df, signs


def build_target(conn, spec):
    """Build forward target series (daily)."""
    sid, h, mode, event_threshold = spec['target']
    s = load_obs(conn, sid)
    s_d = s.resample('D').ffill()

    if mode == 'delta':
        fwd = s_d.shift(-h) - s_d
    elif mode == 'yoy_pct':
        fwd = (s_d.shift(-h) / s_d - 1) * 100
    elif mode == 'yoy_pct_level':
        # Forward level of YoY% (i.e. what will YoY% BE in h days)
        yoy_now = (s_d / s_d.shift(252) - 1) * 100
        fwd = yoy_now.shift(-h)
    elif mode == 'log_fwd_return':
        fwd = np.log(s_d.shift(-h) / s_d) * 100
    elif mode == 'fwd_max_change':
        out = pd.Series(index=s_d.index, dtype=float)
        arr = s_d.values
        for i in range(len(arr) - h):
            out.iloc[i] = arr[i:i+h+1].max() - arr[i]
        fwd = out
    else:
        fwd = s_d.shift(-h) - s_d
    return fwd, event_threshold


# ============================================================
# COMPOSITE COMPUTATION
# ============================================================

def compute_composite(z_components, weights):
    """Sum weighted z-scored signed components."""
    cols = z_components.columns
    w_arr = np.array([weights[c] for c in cols])
    w_arr = w_arr / w_arr.sum()  # normalize
    return (z_components * w_arr).sum(axis=1)


# ============================================================
# OPTIMIZATION
# ============================================================

def neg_abs_rank_ic(weights_arr, z_components, target, component_names):
    """Maximize |rank IC|. Return negative for minimizer."""
    w = np.abs(weights_arr)
    if w.sum() <= 0:
        return 1e6
    w = w / w.sum()
    composite = z_components.values @ w
    df = pd.DataFrame({'sig': composite, 'fwd': target.values}, index=z_components.index).dropna()
    if len(df) < 250:
        return 1e6
    ic, _ = stats.spearmanr(df['sig'], df['fwd'])
    if np.isnan(ic):
        return 1e6
    return -abs(ic)


def optimize_weights(z_components, target, n_restarts=30, bounds=(0.02, 0.40)):
    component_names = list(z_components.columns)
    n = len(component_names)
    if n < 2:
        return None
    bnds = [bounds] * n
    cons = [{'type': 'eq', 'fun': lambda w: np.sum(np.abs(w)) - 1.0}]

    rng = np.random.RandomState(42)
    starts = [np.ones(n) / n]  # equal weight start
    for _ in range(n_restarts - 1):
        w0 = rng.dirichlet(np.ones(n))
        w0 = np.clip(w0, bounds[0], bounds[1])
        w0 = w0 / w0.sum()
        starts.append(w0)

    best = None
    best_obj = 1e6
    for w0 in starts:
        try:
            res = minimize(
                neg_abs_rank_ic, w0,
                args=(z_components, target, component_names),
                method='SLSQP', bounds=bnds, constraints=cons,
                options={'maxiter': 300, 'ftol': 1e-9}
            )
            if res.fun < best_obj:
                best_obj = res.fun
                best = res
        except Exception:
            continue

    if best is None:
        return None
    w = np.abs(best.x)
    w = w / w.sum()
    return {n: float(w[i]) for i, n in enumerate(component_names)}, -best_obj


# ============================================================
# EVALUATION
# ============================================================

def evaluate_weights(z_components, target, weights):
    composite = compute_composite(z_components, weights)
    df = pd.DataFrame({'sig': composite, 'fwd': target}).dropna()
    if len(df) < 100:
        return None
    ic, p = stats.spearmanr(df['sig'], df['fwd'])
    # Quintile spread
    try:
        df['q'] = pd.qcut(df['sig'], 5, labels=False, duplicates='drop') + 1
        q1 = df[df['q'] == df['q'].min()]['fwd'].mean()
        q5 = df[df['q'] == df['q'].max()]['fwd'].mean()
        spread = q5 - q1
    except Exception:
        spread = np.nan
    return {
        'ic': float(ic),
        'p_value': float(p),
        'q5_minus_q1': float(spread) if not np.isnan(spread) else None,
        'n': int(len(df)),
    }


def walk_forward_oos(z_components, target, n_splits=5, min_train_pct=0.50):
    """Expanding-window walk-forward. Optimize on train, evaluate on test."""
    df = z_components.join(target.rename('fwd')).dropna()
    n = len(df)
    component_names = list(z_components.columns)
    results = []

    for split in range(n_splits):
        train_end_pct = min_train_pct + (1.0 - min_train_pct) * split / n_splits
        test_end_pct = min_train_pct + (1.0 - min_train_pct) * (split + 1) / n_splits
        train_end = int(n * train_end_pct)
        test_end = int(n * test_end_pct)
        if test_end <= train_end:
            continue
        z_train = df.iloc[:train_end][component_names]
        fwd_train = df.iloc[:train_end]['fwd']
        z_test = df.iloc[train_end:test_end][component_names]
        fwd_test = df.iloc[train_end:test_end]['fwd']
        if len(z_test) < 60:
            continue

        opt_result = optimize_weights(z_train, fwd_train, n_restarts=10)
        if opt_result is None:
            continue
        opt_w, _ = opt_result
        eval_oos = evaluate_weights(z_test, fwd_test, opt_w)
        if eval_oos is None:
            continue
        results.append({
            'split': split + 1,
            'train_n': len(z_train),
            'test_n': len(z_test),
            'test_start': str(z_test.index[0].date()),
            'test_end': str(z_test.index[-1].date()),
            'opt_weights': opt_w,
            'oos_ic': eval_oos['ic'],
            'oos_q_spread': eval_oos['q5_minus_q1'],
        })
    return results


# ============================================================
# MAIN
# ============================================================

def run_pillar(conn, name, spec):
    print(f"\n{'='*70}")
    print(f"PILLAR: {name}")
    print(f"{'='*70}")
    print(f"Components: {[c[0] for c in spec['components']]}")
    print(f"Target: {spec['target']}, risk_side={spec['risk_side']}")

    z_comp, signs = build_components(conn, spec)
    if z_comp.empty:
        print(f"  [SKIP] no component data")
        return None

    target, event_threshold = build_target(conn, spec)

    # Align
    aligned = z_comp.join(target.rename('fwd')).dropna()
    n = len(aligned)
    if n < 500:
        print(f"  [SKIP] insufficient aligned ({n})")
        return None

    z_aligned = aligned[z_comp.columns]
    fwd_aligned = aligned['fwd']
    print(f"Aligned: {n} obs, {aligned.index.min().date()} to {aligned.index.max().date()}")

    # Build judgment weights (use spec, fall back to equal)
    has_judgment = any(c[3] is not None for c in spec['components'])
    if has_judgment:
        # Use specified weights, equal-distribute the rest
        specified_total = sum(c[3] for c in spec['components'] if c[3] is not None)
        unspecified = [c[0] for c in spec['components'] if c[3] is None]
        remaining = max(0, 1 - specified_total)
        per_unspec = remaining / max(len(unspecified), 1)
        judgment = {}
        for sid, sign, mode, w in spec['components']:
            if sid in z_aligned.columns:
                judgment[sid] = w if w is not None else per_unspec
        # Renormalize
        s = sum(judgment.values())
        judgment = {k: v / s for k, v in judgment.items()}
    else:
        judgment = {c: 1.0 / len(z_aligned.columns) for c in z_aligned.columns}

    equal_weight = {c: 1.0 / len(z_aligned.columns) for c in z_aligned.columns}

    # 90/10 IS/OOS split
    n_is = int(n * 0.9)
    z_is = z_aligned.iloc[:n_is]
    fwd_is = fwd_aligned.iloc[:n_is]
    z_oos = z_aligned.iloc[n_is:]
    fwd_oos = fwd_aligned.iloc[n_is:]

    print(f"\nIS: {len(z_is)} obs, OOS: {len(z_oos)} obs")

    # Optimize on IS
    print("Optimizing on IS (rank IC objective, 30 restarts)...")
    opt_result = optimize_weights(z_is, fwd_is, n_restarts=30)
    if opt_result is None:
        print("[FAIL] optimization failed")
        return None
    opt_weights, opt_obj = opt_result

    # Evaluate all three on OOS and full
    print("\n  Evaluation:")
    print(f"  {'Method':<12} {'Full IC':>9} {'OOS IC':>9} "
          f"{'Full Q-spread':>14} {'OOS Q-spread':>13}")
    print(f"  {'-'*65}")

    eval_results = {}
    for label, w in [('Equal', equal_weight),
                     ('Judgment', judgment),
                     ('Optimized', opt_weights)]:
        full_eval = evaluate_weights(z_aligned, fwd_aligned, w)
        oos_eval = evaluate_weights(z_oos, fwd_oos, w)
        eval_results[label] = {
            'weights': w,
            'full': full_eval,
            'oos': oos_eval,
        }
        full_ic = full_eval['ic'] if full_eval else np.nan
        oos_ic = oos_eval['ic'] if oos_eval else np.nan
        full_qs = full_eval['q5_minus_q1'] if full_eval and full_eval['q5_minus_q1'] else np.nan
        oos_qs = oos_eval['q5_minus_q1'] if oos_eval and oos_eval['q5_minus_q1'] else np.nan
        print(f"  {label:<12} {full_ic:>+9.4f} {oos_ic:>+9.4f} "
              f"{full_qs:>+14.4f} {oos_qs:>+13.4f}")

    # Walk-forward
    print("\nWalk-forward (5 splits)...")
    wf = walk_forward_oos(z_aligned, fwd_aligned, n_splits=5)
    wf_oos_ics = [r['oos_ic'] for r in wf if not np.isnan(r['oos_ic'])]
    if wf_oos_ics:
        print(f"  Avg WF OOS IC: {np.mean(wf_oos_ics):+.4f}")
        # Weight stability
        component_names = list(z_aligned.columns)
        wm = np.array([[r['opt_weights'].get(c, 0) for c in component_names]
                       for r in wf if r['opt_weights']])
        if len(wm) >= 2:
            print(f"  Weight stability:")
            print(f"  {'Component':>20} {'Mean':>7} {'Std':>7} {'Min':>7} {'Max':>7}")
            for i, c in enumerate(component_names):
                print(f"  {c:>20} {wm[:, i].mean():>7.3f} {wm[:, i].std():>7.3f} "
                      f"{wm[:, i].min():>7.3f} {wm[:, i].max():>7.3f}")

    # Apply adoption rule
    judgment_full_ic = abs(eval_results['Judgment']['full']['ic'])
    optimized_full_ic = abs(eval_results['Optimized']['full']['ic'])
    judgment_oos_ic = abs(eval_results['Judgment']['oos']['ic']) if eval_results['Judgment']['oos'] else 0
    optimized_oos_ic = abs(eval_results['Optimized']['oos']['ic']) if eval_results['Optimized']['oos'] else 0

    improvement = (optimized_oos_ic - judgment_oos_ic) / max(judgment_oos_ic, 0.01)

    weights_max = max(opt_weights.values())
    print(f"\n  ADOPTION DECISION:")
    print(f"    OOS IC improvement vs judgment: {improvement:+.1%}")
    print(f"    Max weight: {weights_max:.3f}")

    if improvement >= 0.10 and weights_max <= 0.30:
        decision = 'adopt'
        print(f"    -> ADOPT optimized weights")
    elif improvement >= 0.05:
        decision = 'shrink'
        print(f"    -> SHRINKAGE candidate (modest improvement)")
    else:
        decision = 'keep_judgment'
        print(f"    -> KEEP judgment")

    return {
        'pillar': name,
        'n_aligned': n,
        'date_range': [str(aligned.index.min().date()),
                       str(aligned.index.max().date())],
        'components': list(z_aligned.columns),
        'judgment_weights': judgment,
        'optimized_weights': opt_weights,
        'equal_weights': equal_weight,
        'evaluation': {
            'judgment': {
                'full_ic': eval_results['Judgment']['full']['ic'] if eval_results['Judgment']['full'] else None,
                'oos_ic': eval_results['Judgment']['oos']['ic'] if eval_results['Judgment']['oos'] else None,
            },
            'optimized': {
                'full_ic': eval_results['Optimized']['full']['ic'] if eval_results['Optimized']['full'] else None,
                'oos_ic': eval_results['Optimized']['oos']['ic'] if eval_results['Optimized']['oos'] else None,
            },
            'equal': {
                'full_ic': eval_results['Equal']['full']['ic'] if eval_results['Equal']['full'] else None,
                'oos_ic': eval_results['Equal']['oos']['ic'] if eval_results['Equal']['oos'] else None,
            },
        },
        'walk_forward': {
            'avg_oos_ic': float(np.mean(wf_oos_ics)) if wf_oos_ics else None,
            'splits': wf,
        },
        'oos_improvement': float(improvement),
        'max_optimized_weight': float(weights_max),
        'decision': decision,
    }


def main():
    print("="*70)
    print("PER-PILLAR WEIGHT OPTIMIZATION")
    print(f"Run: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("="*70)

    conn = sqlite3.connect(DB_PATH)
    out = {'run_date': datetime.now().isoformat(), 'pillars': {}}

    for name, spec in PILLAR_SPECS.items():
        try:
            result = run_pillar(conn, name, spec)
            if result:
                out['pillars'][name] = result
        except Exception as e:
            print(f"\n[ERROR] {name}: {e}")
            import traceback
            traceback.print_exc()

    conn.close()
    OUT_PATH.write_text(json.dumps(out, indent=2, default=str))
    print(f"\nSaved to: {OUT_PATH}")

    # Summary table
    print("\n" + "="*70)
    print("SUMMARY: ADOPTION DECISIONS")
    print("="*70)
    print(f"  {'Pillar':<10} {'Judgment OOS IC':>17} {'Optimized OOS IC':>18} "
          f"{'Improvement':>13} {'Max W':>7} {'Decision':>17}")
    print(f"  {'-'*90}")
    for name, r in out['pillars'].items():
        j = r['evaluation']['judgment']['oos_ic']
        o = r['evaluation']['optimized']['oos_ic']
        imp = r['oos_improvement']
        mx = r['max_optimized_weight']
        d = r['decision']
        j_s = f"{j:+.4f}" if j is not None else 'n/a'
        o_s = f"{o:+.4f}" if o is not None else 'n/a'
        print(f"  {name:<10} {j_s:>17} {o_s:>18} {imp:>+13.1%} {mx:>7.3f} {d:>17}")


if __name__ == "__main__":
    main()
