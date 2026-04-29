#!/usr/bin/env python3
"""
Per-Pillar Multi-Asset Weight Optimization
============================================
Each pillar tested against multiple plausible asset targets:
  - Yields (forward 2y, 10y, 2s10s)
  - Inflation breakevens (5y, 10y)
  - Dollar (DTWEXBGS)
  - Credit (HY OAS, IG OAS)
  - Equity (S&P 500)
  - Vol (VIX)

For each pillar+target pair, optimize component weights and report
OOS information coefficient. The "best target" for each pillar is
whichever gives the cleanest OOS lead signal.

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
    build_components, expanding_zscore, evaluate_weights,
)

OUTPUT_DIR = Path("/Users/bob/LHM/Outputs/mri_optimization")
OUT_PATH = OUTPUT_DIR / "pillar_multiasset_optimization.json"

BOUNDS = (0.05, 0.30)


# Multi-asset targets per pillar (series_id, horizon_days, mode, label)
# mode: 'delta', 'log_fwd_return', 'fwd_max_change', 'yoy_pct_level'
MULTIASSET_TARGETS = {
    'LPI': [
        ('UNRATE', 252, 'delta', 'Unemployment rate change 252d'),
        ('DGS2', 252, 'delta', '2y yield change 252d'),
        ('DGS10', 252, 'delta', '10y yield change 252d'),
        ('T10Y2Y', 252, 'delta', '2s10s change 252d'),
        ('SPX_Close', 63, 'log_fwd_return', 'SPX 63d log return'),
    ],
    'PCI': [
        ('PCEPILFE', 365, 'yoy_pct_level', 'Core PCE YoY 365d'),
        ('T5YIE', 252, 'delta', '5y breakeven change 252d'),
        ('T10YIE', 252, 'delta', '10y breakeven change 252d'),
        ('DGS10', 252, 'delta', '10y yield change 252d'),
        ('DGS2', 252, 'delta', '2y yield change 252d'),
    ],
    'GCI': [
        ('INDPRO', 252, 'yoy_pct_level', 'Industrial Prod YoY 252d'),
        ('DGS10', 252, 'delta', '10y yield change 252d'),
        ('DGS2', 252, 'delta', '2y yield change 252d'),
        ('SPX_Close', 252, 'log_fwd_return', 'SPX 252d log return'),
        ('BAMLH0A0HYM2', 252, 'fwd_max_change', 'HY OAS widening 252d'),
    ],
    'HCI': [
        ('HOUST', 365, 'yoy_pct_level', 'Housing starts YoY 365d'),
        ('MORTGAGE30US', 365, 'delta', '30y mortgage change 365d'),
        ('DGS10', 252, 'delta', '10y yield change 252d'),
    ],
    'CCI': [
        ('RSXFS', 252, 'yoy_pct_level', 'Retail sales YoY 252d'),
        ('SPX_Close', 252, 'log_fwd_return', 'SPX 252d log return'),
        ('BAMLH0A0HYM2', 252, 'fwd_max_change', 'HY OAS widening 252d'),
    ],
    'BCI': [
        ('NEWORDER', 252, 'yoy_pct_level', 'New orders YoY 252d'),
        ('DGS10', 252, 'delta', '10y yield change 252d'),
        ('SPX_Close', 252, 'log_fwd_return', 'SPX 252d log return'),
        ('BAMLH0A0HYM2', 252, 'fwd_max_change', 'HY OAS widening 252d'),
    ],
    'TCI': [
        ('NETEXP', 252, 'delta', 'Net exports change 252d'),
        ('DTWEXBGS', 252, 'log_fwd_return', 'Dollar 252d return'),
        ('DEXJPUS', 252, 'log_fwd_return', 'USD/JPY 252d return'),
    ],
    'GCI_Gov': [
        ('DGS10', 252, 'delta', '10y yield change 252d'),
        ('THREEFYTP10', 252, 'delta', '10y term premium change 252d'),
        ('T10Y2Y', 252, 'delta', '2s10s change 252d'),
        ('BAMLH0A0HYM2', 252, 'fwd_max_change', 'HY OAS widening 252d'),
        ('DTWEXBGS', 252, 'log_fwd_return', 'Dollar 252d return'),
    ],
    'FCI': [
        ('BAMLH0A0HYM2', 126, 'fwd_max_change', 'HY OAS widening 126d'),
        ('BAMLC0A0CM', 126, 'fwd_max_change', 'IG OAS widening 126d'),
        ('VIXCLS', 21, 'log_fwd_return', 'VIX 21d return'),
        ('SPX_Close', 63, 'log_fwd_return', 'SPX 63d log return'),
    ],
    'LCI': [
        ('BAMLH0A0HYM2', 63, 'fwd_max_change', 'HY OAS widening 63d'),
        ('DGS2', 63, 'delta', '2y yield change 63d'),
        ('BAA10Y', 63, 'delta', 'Baa-10y spread change 63d'),
        ('SPX_Close', 21, 'log_fwd_return', 'SPX 21d log return'),
        ('VIXCLS', 21, 'log_fwd_return', 'VIX 21d return'),
    ],
    'MSI': [
        ('SPX_Close', 63, 'log_fwd_return', 'SPX 63d log return'),
        ('SPX_Close', 21, 'log_fwd_return', 'SPX 21d log return'),
        ('VIXCLS', 21, 'log_fwd_return', 'VIX 21d return'),
    ],
    'SPI': [
        ('SPX_Close', 21, 'log_fwd_return', 'SPX 21d log return'),
        ('SPX_Close', 5, 'log_fwd_return', 'SPX 5d log return'),
        ('VIXCLS', 21, 'log_fwd_return', 'VIX 21d return'),
    ],
}


def load_obs(conn, sid):
    df = pd.read_sql(
        "SELECT date, value FROM observations WHERE series_id = ? ORDER BY date",
        conn, params=(sid,), parse_dates=['date']
    ).set_index('date').sort_index()
    return df['value'].dropna()


def fwd_max_change(series, h):
    s = series.copy().sort_index()
    out = pd.Series(index=s.index, dtype=float)
    arr = s.values
    for i in range(len(arr) - h):
        out.iloc[i] = arr[i:i+h+1].max() - arr[i]
    return out


def build_target(conn, sid, h, mode):
    s = load_obs(conn, sid)
    if s.empty:
        return None
    s_d = s.resample('D').ffill()
    if mode == 'delta':
        return s_d.shift(-h) - s_d
    elif mode == 'log_fwd_return':
        return np.log(s_d.shift(-h) / s_d) * 100
    elif mode == 'yoy_pct_level':
        yoy = (s_d / s_d.shift(252) - 1) * 100
        return yoy.shift(-h)
    elif mode == 'fwd_max_change':
        return fwd_max_change(s_d, h)
    return None


def neg_abs_ic(w, z, target):
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


def optimize(z_components, target, bounds=BOUNDS, n_restarts=20):
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
            res = minimize(neg_abs_ic, w0, args=(z_components, target),
                           method='SLSQP', bounds=bnds, constraints=cons,
                           options={'maxiter': 200, 'ftol': 1e-9})
            if res.fun < best_obj:
                best_obj = res.fun
                best = res
        except Exception:
            pass
    if best is None:
        return None, None
    w = np.abs(best.x) / np.abs(best.x).sum()
    weights_dict = {c: float(w[i]) for i, c in enumerate(z_components.columns)}
    return weights_dict, -best_obj


def main():
    print("="*70)
    print("PILLAR MULTI-ASSET OPTIMIZATION")
    print(f"Run: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("="*70)

    conn = sqlite3.connect(DB_PATH)
    out = {'run_date': datetime.now().isoformat(), 'pillars': {}}

    for pillar, targets in MULTIASSET_TARGETS.items():
        print(f"\n{'='*70}\n{pillar}\n{'='*70}")
        spec = PILLAR_SPECS.get(pillar)
        if spec is None:
            continue
        z_comp, _ = build_components(conn, spec)
        if z_comp.empty:
            print(f"  [SKIP] no components")
            continue

        pillar_results = []
        print(f"  {'Target':<35} {'N':>5} {'Full IC':>9} {'OOS IC':>9} {'Max W':>7}")
        print(f"  {'-'*70}")

        for sid, h, mode, label in targets:
            target = build_target(conn, sid, h, mode)
            if target is None:
                continue
            aligned = z_comp.join(target.rename('fwd')).dropna()
            if len(aligned) < 500:
                continue
            z_aligned = aligned[z_comp.columns]
            fwd_aligned = aligned['fwd']

            # 90/10
            n_is = int(len(aligned) * 0.9)
            z_is = z_aligned.iloc[:n_is]
            fwd_is = fwd_aligned.iloc[:n_is]
            z_oos = z_aligned.iloc[n_is:]
            fwd_oos = fwd_aligned.iloc[n_is:]

            w, _ = optimize(z_is, fwd_is, n_restarts=20)
            if w is None:
                continue
            full_eval = evaluate_weights(z_aligned, fwd_aligned, w)
            oos_eval = evaluate_weights(z_oos, fwd_oos, w)
            full_ic = full_eval['ic'] if full_eval else None
            oos_ic = oos_eval['ic'] if oos_eval else None
            mx = max(w.values())
            print(f"  {label:<35} {len(aligned):>5} "
                  f"{full_ic:>+9.4f} "
                  f"{(oos_ic if oos_ic is not None else 0):>+9.4f} "
                  f"{mx:>7.3f}")

            pillar_results.append({
                'target_series': sid,
                'horizon_days': h,
                'mode': mode,
                'target_label': label,
                'n_aligned': len(aligned),
                'optimized_weights': w,
                'full_ic': float(full_ic) if full_ic is not None else None,
                'oos_ic': float(oos_ic) if oos_ic is not None else None,
                'max_weight': float(mx),
            })

        # Best target by |OOS IC|
        valid = [r for r in pillar_results
                 if r['oos_ic'] is not None]
        best = max(valid, key=lambda r: abs(r['oos_ic'])) if valid else None
        if best:
            print(f"\n  -> BEST TARGET: {best['target_label']} "
                  f"(OOS IC = {best['oos_ic']:+.4f})")
        out['pillars'][pillar] = {
            'targets_tested': pillar_results,
            'best_target': best,
        }

    conn.close()
    OUT_PATH.write_text(json.dumps(out, indent=2, default=str))
    print(f"\nSaved to: {OUT_PATH}")

    # Summary
    print("\n" + "="*70)
    print("SUMMARY: BEST TARGET PER PILLAR")
    print("="*70)
    print(f"  {'Pillar':<10} {'Best target':<35} {'OOS IC':>9}")
    print(f"  {'-'*60}")
    for name, p in out['pillars'].items():
        best = p.get('best_target')
        if best:
            print(f"  {name:<10} {best['target_label']:<35} {best['oos_ic']:>+9.4f}")
        else:
            print(f"  {name:<10} {'(no valid target)':<35}")


if __name__ == "__main__":
    main()
