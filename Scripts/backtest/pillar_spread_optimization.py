#!/usr/bin/env python3
"""
Per-Pillar Spread (Relative-Performance) Tests
================================================
For each pillar, test against asset SPREADS rather than absolute returns.
Spreads are the natural way macro books express views and are regime-neutral.

Spread = log(asset_A / asset_B) over horizon h. Signal predicts how
the spread evolves.

Examples:
  - Financial Conditions Index → SPY/TLT spread compression
  - Consumer Conditions Index → XLY/XLP spread (cyclicals/defensives)
  - Trade Conditions Index → EEM/SPY spread (EM dollar sensitivity)
  - Housing Conditions Index → XHB/SPY spread

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
    build_components, evaluate_weights, expanding_zscore,
)

OUTPUT_DIR = Path("/Users/bob/LHM/Outputs/mri_optimization")
OUT_PATH = OUTPUT_DIR / "pillar_spread_optimization.json"

BOUNDS = (0.05, 0.30)


# Pillar -> list of (asset_a, asset_b, horizon_days, label)
# Spread = log(asset_a / asset_b) over horizon h
PILLAR_SPREAD_TARGETS = {
    'PCI': [
        ('SHY_Close', 'TLT_Close', 252, 'SHY/TLT (front vs long duration)'),
        ('TLT_Close', 'IEF_Close', 252, 'TLT/IEF (long vs intermediate)'),
        ('IEF_Close', 'SHY_Close', 252, 'IEF/SHY (intermediate vs front)'),
    ],
    'LCI': [
        ('HYG_Close', 'LQD_Close', 63, 'HYG/LQD (HY vs IG credit)'),
        ('SPY_Close', 'TLT_Close', 63, 'SPY/TLT (risk-on/risk-off)'),
    ],
    'LPI': [
        ('XLY_Close', 'XLP_Close', 252, 'XLY/XLP (cyclicals/defensives)'),
        ('SPY_Close', 'TLT_Close', 252, 'SPY/TLT'),
    ],
    'GCI': [
        ('XLI_Close', 'XLP_Close', 252, 'XLI/XLP (industrials/staples)'),
        ('SPY_Close', 'TLT_Close', 252, 'SPY/TLT'),
        ('IWM_Close', 'SPY_Close', 252, 'IWM/SPY (small/large)'),
    ],
    'BCI': [
        ('XLI_Close', 'XLP_Close', 252, 'XLI/XLP'),
        ('IWM_Close', 'SPY_Close', 252, 'IWM/SPY'),
        ('XLB_Close', 'XLP_Close', 252, 'XLB/XLP (materials/staples)'),
    ],
    'HCI': [
        ('XHB_Close', 'SPY_Close', 252, 'XHB/SPY (homebuilders relative)'),
        ('ITB_Close', 'SPY_Close', 252, 'ITB/SPY'),
    ],
    'CCI': [
        ('XLY_Close', 'XLP_Close', 252, 'XLY/XLP (cyclicals/defensives)'),
        ('SPY_Close', 'TLT_Close', 252, 'SPY/TLT'),
    ],
    'TCI': [
        ('EEM_Close', 'SPY_Close', 252, 'EEM/SPY (EM/US)'),
        ('EFA_Close', 'SPY_Close', 252, 'EFA/SPY (DM ex-US/US)'),
    ],
    'GCI_Gov': [
        ('TLT_Close', 'IEF_Close', 252, 'TLT/IEF (long vs intermediate)'),
        ('TLT_Close', 'SHY_Close', 252, 'TLT/SHY (long vs front)'),
    ],
    'FCI': [
        ('SPY_Close', 'TLT_Close', 63, 'SPY/TLT (risk-on/risk-off)'),
        ('HYG_Close', 'LQD_Close', 63, 'HYG/LQD'),
        ('XLY_Close', 'XLP_Close', 63, 'XLY/XLP'),
        ('XLF_Close', 'XLP_Close', 63, 'XLF/XLP (financials/staples)'),
    ],
    'MSI': [
        ('SPY_Close', 'TLT_Close', 21, 'SPY/TLT'),
        ('IWM_Close', 'SPY_Close', 21, 'IWM/SPY'),
    ],
    'SPI': [
        ('SPY_Close', 'TLT_Close', 21, 'SPY/TLT'),
        ('XLY_Close', 'XLP_Close', 21, 'XLY/XLP'),
    ],
}


def load_obs(conn, sid):
    df = pd.read_sql(
        "SELECT date, value FROM observations WHERE series_id = ? ORDER BY date",
        conn, params=(sid,), parse_dates=['date']
    ).set_index('date').sort_index()
    return df['value'].dropna()


def build_spread_target(conn, sid_a, sid_b, h):
    """spread = log(A/B); fwd_spread_change = spread[t+h] - spread[t]"""
    a = load_obs(conn, sid_a).resample('D').ffill()
    b = load_obs(conn, sid_b).resample('D').ffill()
    df = pd.DataFrame({'a': a, 'b': b}).dropna()
    if df.empty:
        return None
    df['spread'] = np.log(df['a'] / df['b'])
    df['fwd_change'] = df['spread'].shift(-h) - df['spread']
    return df['fwd_change'].dropna() * 100  # in pp


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


def optimize(z_components, target, bounds=BOUNDS, n_restarts=15):
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
        return None
    w = np.abs(best.x) / np.abs(best.x).sum()
    return {c: float(w[i]) for i, c in enumerate(z_components.columns)}


def threshold_lift(signal_z, target, target_threshold, side='above', sig_thresholds=None):
    """For threshold sig_threshold (z), what % of obs see |target| >= target_threshold?"""
    if sig_thresholds is None:
        sig_thresholds = [-2.0, -1.5, -1.0, -0.5, 0.5, 1.0, 1.5, 2.0]
    df = pd.DataFrame({'sig': signal_z, 'fwd': target}).dropna()
    if len(df) < 100:
        return []
    base_rate = (df['fwd'] >= target_threshold).mean() if side == 'above' \
        else (df['fwd'] <= target_threshold).mean()
    base_mean = df['fwd'].mean()
    out = []
    for t in sig_thresholds:
        sub = df[df['sig'] >= t] if t > 0 else df[df['sig'] <= t]
        if len(sub) < 30:
            continue
        if side == 'above':
            rate = (sub['fwd'] >= target_threshold).mean()
        else:
            rate = (sub['fwd'] <= target_threshold).mean()
        mean = sub['fwd'].mean()
        lift = rate / base_rate if base_rate > 0 else np.nan
        out.append({
            'sig_threshold': t,
            'side': 'above' if t > 0 else 'below',
            'n': int(len(sub)),
            'pct_pop': float(len(sub) / len(df)),
            'mean_target': float(mean),
            'rate': float(rate),
            'lift': float(lift),
            'mean_target_diff_vs_base': float(mean - base_mean),
        })
    return out


def main():
    print("="*70)
    print("PILLAR SPREAD OPTIMIZATION (relative performance)")
    print(f"Run: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("="*70)

    conn = sqlite3.connect(DB_PATH)
    out = {'run_date': datetime.now().isoformat(), 'pillars': {}}

    for pillar, targets in PILLAR_SPREAD_TARGETS.items():
        print(f"\n{'='*70}\n{pillar}\n{'='*70}")
        spec = PILLAR_SPECS.get(pillar)
        if spec is None:
            continue
        z_comp, _ = build_components(conn, spec)
        if z_comp.empty:
            print("  no components")
            continue

        pillar_results = []
        print(f"  {'Spread Target':<40} {'h':>4} {'N':>5} {'Full IC':>8} {'OOS IC':>8} {'Mean@z>1':>10}")
        print(f"  {'-'*82}")

        for sid_a, sid_b, h, label in targets:
            target = build_spread_target(conn, sid_a, sid_b, h)
            if target is None:
                continue
            aligned = z_comp.join(target.rename('fwd')).dropna()
            if len(aligned) < 500:
                continue
            z_a = aligned[z_comp.columns]
            fwd = aligned['fwd']

            n_is = int(len(aligned) * 0.9)
            z_is = z_a.iloc[:n_is]
            fwd_is = fwd.iloc[:n_is]
            z_oos = z_a.iloc[n_is:]
            fwd_oos = fwd.iloc[n_is:]

            w = optimize(z_is, fwd_is)
            if w is None:
                continue
            full_e = evaluate_weights(z_a, fwd, w)
            oos_e = evaluate_weights(z_oos, fwd_oos, w)
            full_ic = full_e['ic'] if full_e else None
            oos_ic = oos_e['ic'] if oos_e else None

            # Compute composite & threshold lifts
            composite = (z_a.values @ np.array([w[c] for c in z_a.columns]))
            composite = pd.Series(composite, index=z_a.index)

            # Use 5pp move as the "event" threshold for spread tests
            EVENT_PCT = 5.0
            lifts_above = threshold_lift(composite, fwd, EVENT_PCT, side='above',
                                         sig_thresholds=[1.0, 1.5, 2.0])
            lifts_below = threshold_lift(composite, fwd, -EVENT_PCT, side='below',
                                         sig_thresholds=[-2.0, -1.5, -1.0])

            # Mean spread move at z >= +1
            df_test = pd.DataFrame({'sig': composite, 'fwd': fwd}).dropna()
            mean_at_z1_pos = df_test[df_test['sig'] >= 1.0]['fwd'].mean()
            mean_at_z1_neg = df_test[df_test['sig'] <= -1.0]['fwd'].mean()

            mz_print = f"{mean_at_z1_pos:>+10.2f}" if not np.isnan(mean_at_z1_pos) else "       n/a"
            print(f"  {label:<40} {h:>4} {len(aligned):>5} "
                  f"{(full_ic if full_ic else 0):>+8.4f} "
                  f"{(oos_ic if oos_ic else 0):>+8.4f} "
                  f"{mz_print}")

            pillar_results.append({
                'asset_a': sid_a,
                'asset_b': sid_b,
                'horizon_days': h,
                'label': label,
                'n_aligned': len(aligned),
                'optimized_weights': w,
                'full_ic': float(full_ic) if full_ic else None,
                'oos_ic': float(oos_ic) if oos_ic else None,
                'mean_spread_at_z_ge_1': float(mean_at_z1_pos)
                    if not (isinstance(mean_at_z1_pos, float) and np.isnan(mean_at_z1_pos)) else None,
                'mean_spread_at_z_le_neg1': float(mean_at_z1_neg)
                    if not (isinstance(mean_at_z1_neg, float) and np.isnan(mean_at_z1_neg)) else None,
                'threshold_lifts_above': lifts_above,
                'threshold_lifts_below': lifts_below,
                'event_pct': EVENT_PCT,
            })

        valid = [r for r in pillar_results if r['oos_ic'] is not None]
        best = max(valid, key=lambda r: abs(r['oos_ic'])) if valid else None
        if best:
            mz1 = best.get('mean_spread_at_z_ge_1')
            mz_neg1 = best.get('mean_spread_at_z_le_neg1')
            mz1_str = f"{mz1:+.2f}pp" if mz1 is not None and not (isinstance(mz1, float) and np.isnan(mz1)) else "n/a"
            mz_neg1_str = f"{mz_neg1:+.2f}pp" if mz_neg1 is not None and not (isinstance(mz_neg1, float) and np.isnan(mz_neg1)) else "n/a"
            print(f"\n  -> BEST SPREAD: {best['label']} "
                  f"(OOS IC = {best['oos_ic']:+.4f}, "
                  f"mean@z>=1 = {mz1_str}, mean@z<=-1 = {mz_neg1_str})")

        out['pillars'][pillar] = {
            'targets_tested': pillar_results,
            'best_spread': best,
        }

    conn.close()
    OUT_PATH.write_text(json.dumps(out, indent=2, default=str))
    print(f"\nSaved: {OUT_PATH}")

    # Summary
    print("\n" + "="*70)
    print("SUMMARY: BEST SPREAD PER PILLAR")
    print("="*70)
    print(f"  {'Pillar':<10} {'Best spread':<40} {'OOS IC':>9} {'Mean@z+1':>10} {'Mean@z-1':>10}")
    print(f"  {'-'*82}")
    for name, p in out['pillars'].items():
        b = p.get('best_spread')
        if b:
            mz1 = b.get('mean_spread_at_z_ge_1')
            mz_neg1 = b.get('mean_spread_at_z_le_neg1')
            def _fmt(v):
                if v is None:
                    return '       n/a'
                if isinstance(v, float) and np.isnan(v):
                    return '       n/a'
                return f"{v:>+10.2f}"
            print(f"  {name:<10} {b['label']:<40} "
                  f"{b['oos_ic']:>+9.4f} "
                  f"{_fmt(mz1)} {_fmt(mz_neg1)}")


if __name__ == "__main__":
    main()
