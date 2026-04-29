#!/usr/bin/env python3
"""
Phase 4 (subset) + Phase 7 — Standalone Signals + Audit
==========================================================
Phase 4 subset:
  - Quits-to-Claims ratio: JTSQUR / ICSA
    Test: when ratio drops below threshold, does HY OAS widen
    over 3-6m horizon? (master plan: "Labor data → credit timing")

  - Dealer/Auction: skip (insufficient data in DB)
  - Breadth thrust binary: skip (data only starts 2023)

Phase 7:
  - Correlation matrix of all composite indicators (MRI, MSI, SPI,
    LCI, CLG, SBD, SSD + the 12 pillars). Identify >0.7 correlations
    that signal redundancy.
  - Year-by-year stability already computed in MRI run.

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
    DB_PATH, FWD_HORIZONS, OPT_PRIMARY_HORIZON,
    load_data, compute_pillar_zscores, compute_forward_returns,
)
import sqlite3

OUTPUT_DIR = Path("/Users/bob/LHM/Outputs/mri_optimization")
OUT_PATH = OUTPUT_DIR / "phase4_7_results.json"


def load_indicator(conn, idx_id):
    df = pd.read_sql(
        "SELECT date, value FROM lighthouse_indices WHERE index_id = ? ORDER BY date",
        conn, params=(idx_id,), parse_dates=['date']
    ).set_index('date').sort_index()
    return df['value']


def load_observation(conn, sid):
    df = pd.read_sql(
        "SELECT date, value FROM observations WHERE series_id = ? ORDER BY date",
        conn, params=(sid,), parse_dates=['date']
    ).set_index('date').sort_index()
    return df['value']


def expanding_zscore(series, min_periods=63, winsorize=3.0):
    mean = series.expanding(min_periods=min_periods).mean()
    std = series.expanding(min_periods=min_periods).std()
    z = (series - mean) / std.replace(0, np.nan)
    return z.clip(-winsorize, winsorize)


def fwd_max_change(series, horizon_days):
    s = series.copy().sort_index()
    out = pd.Series(index=s.index, dtype=float)
    arr = s.values
    for i in range(len(arr) - horizon_days):
        out.iloc[i] = arr[i:i+horizon_days+1].max() - arr[i]
    return out


def main():
    print("="*70)
    print("PHASE 4 + 7 — STANDALONE + AUDIT")
    print(f"Run: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("="*70)

    conn = sqlite3.connect(DB_PATH)
    out = {'run_date': datetime.now().isoformat()}

    # =========================================================
    # PHASE 4: Quits-to-Claims Ratio
    # =========================================================
    print("\n" + "="*70)
    print("PHASE 4: Quits-to-Claims ratio → HY OAS widening")
    print("="*70)

    quits = load_observation(conn, 'JTSQUR')  # Quits rate (monthly)
    claims = load_observation(conn, 'ICSA')   # Initial claims (weekly)
    hy = load_observation(conn, 'BAMLH0A0HYM2')

    # Resample claims to monthly mean to match quits
    claims_monthly = claims.resample('MS').mean()
    quits_monthly = quits.resample('MS').mean()

    # Ratio (high quits / low claims = healthy labor)
    aligned = pd.DataFrame({'quits': quits_monthly, 'claims': claims_monthly}).dropna()
    aligned['ratio'] = aligned['quits'] / aligned['claims']
    print(f"Quits/Claims ratio: {len(aligned)} obs, "
          f"{aligned.index.min().date()} to {aligned.index.max().date()}")

    # Z-score the ratio
    ratio_z = expanding_zscore(aligned['ratio'])

    # Forward-fill ratio_z to daily for joining with daily HY OAS
    ratio_daily = ratio_z.resample('D').ffill()

    # Forward HY widening at 63d and 126d horizons
    for h in [63, 126]:
        fwd_w = fwd_max_change(hy, h)
        df = pd.DataFrame({'sig': ratio_daily, 'fwd': fwd_w}).dropna()
        if len(df) < 200:
            continue
        EVENT_BPS = 1.0
        base = (df['fwd'] >= EVENT_BPS).mean()
        print(f"\n  {h}d horizon: base widening event rate = {base:.1%}, n={len(df)}")
        print(f"  {'Thresh':>7} {'Side':>6} {'N':>5} {'%pop':>5} "
              f"{'Mean wid':>10} {'%event':>7} {'Lift':>6}")
        print(f"  {'-'*65}")

        results = []
        for t in np.arange(-2.0, 0.6, 0.2):
            t = round(t, 2)
            sub = df[df['sig'] <= t]
            n = len(sub)
            if n < 30:
                continue
            pct_pop = n / len(df)
            mean_w = sub['fwd'].mean()
            pct_event = (sub['fwd'] >= EVENT_BPS).mean()
            lift = pct_event / base if base > 0 else np.nan
            results.append({
                'threshold': t, 'n': n, 'pct_population': float(pct_pop),
                'mean_widening': float(mean_w),
                'pct_event': float(pct_event), 'lift': float(lift),
            })

        sorted_top = sorted(results, key=lambda r: -r['lift'])[:3]
        for r in sorted_top:
            print(f"  {r['threshold']:>+7.2f} {'below':>6} {r['n']:>5} "
                  f"{r['pct_population']:>5.1%} "
                  f"{r['mean_widening']:>+10.3f} {r['pct_event']:>7.1%} "
                  f"{r['lift']:>6.2f}")

        out[f'quits_to_claims_h{h}d'] = {
            'horizon_days': h,
            'base_event_rate': float(base),
            'n_aligned': len(df),
            'sweep': results,
        }

    # =========================================================
    # PHASE 7: Correlation Matrix
    # =========================================================
    print("\n" + "="*70)
    print("PHASE 7: Correlation Matrix Audit")
    print("="*70)

    indicators = ['MRI', 'MSI', 'SPI', 'LCI', 'CLG', 'SBD', 'SSD',
                  'LPI', 'PCI', 'GCI', 'HCI', 'CCI', 'BCI', 'TCI',
                  'GCI_Gov', 'FCI']
    series_dict = {}
    for ind in indicators:
        s = load_indicator(conn, ind)
        if not s.empty:
            series_dict[ind] = s

    df_all = pd.DataFrame(series_dict)
    df_all = df_all.dropna()
    print(f"\nAligned dataset for correlation: {len(df_all)} obs, "
          f"{df_all.index.min().date()} to {df_all.index.max().date()}")
    print(f"Indicators: {list(df_all.columns)}")

    corr = df_all.corr()
    print("\nCorrelation matrix (Pearson):")
    print(corr.round(2).to_string())

    # Find redundancies
    print("\n  Pairs with |corr| >= 0.7:")
    pairs = []
    for i in range(len(corr.columns)):
        for j in range(i+1, len(corr.columns)):
            c = corr.iloc[i, j]
            if abs(c) >= 0.7:
                pair = (corr.columns[i], corr.columns[j], float(c))
                pairs.append(pair)
                print(f"    {pair[0]:>10} <-> {pair[1]:<10}: {c:>+.3f}")

    out['correlation_matrix'] = {
        'columns': list(corr.columns),
        'matrix': corr.values.tolist(),
        'high_correlation_pairs': pairs,
        'n_obs': len(df_all),
    }

    conn.close()

    OUT_PATH.write_text(json.dumps(out, indent=2, default=str))
    print(f"\nSaved to: {OUT_PATH}")


if __name__ == "__main__":
    main()
