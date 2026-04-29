#!/usr/bin/env python3
"""
Phase 2 Threshold Optimization — MSI / SPI / LCI / CLG / SBD / SSD
====================================================================
Track A: treat existing lighthouse_indices composites as black boxes,
find threshold breakpoints for each.

For each indicator:
  - MSI: threshold below which gross exposure should compress
  - SPI: threshold above which contrarian fade triggers
  - LCI: threshold below which cash should rise (event-based)
  - CLG: threshold below which credit protection triggers
  - SBD: threshold above which distribution warning triggers
  - SSD: thresholds at extremes (capitulation / blow-off)

Methodology: same as MRI threshold sweep — find drawdown frequency
lifts, identify natural breakpoints.

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
OUT_PATH = OUTPUT_DIR / "phase2_threshold_results.json"

# Indicators and their interpretation (which side is "risky")
INDICATORS = {
    'MSI':  {'risk_side': 'low',   'desc': 'Market Structure (low = broken structure)'},
    'SPI':  {'risk_side': 'high',  'desc': 'Sentiment & Positioning (high = euphoria, contrarian)'},
    'LCI':  {'risk_side': 'low',   'desc': 'Liquidity Cushion (low = scarce)'},
    'CLG':  {'risk_side': 'low',   'desc': 'Credit-Labor Gap (low = credit too tight for labor)'},
    'SBD':  {'risk_side': 'high',  'desc': 'Structure-Breadth Divergence (high = distribution warning)'},
    'SSD':  {'risk_side': 'extreme', 'desc': 'Sentiment-Structure Divergence (both ends matter)'},
}


def load_indicator(conn, idx_id):
    df = pd.read_sql(
        "SELECT date, value FROM lighthouse_indices WHERE index_id = ? ORDER BY date",
        conn, params=(idx_id,), parse_dates=['date']
    ).set_index('date').sort_index()
    return df['value']


def expanding_zscore(series, min_periods=63, winsorize=3.0):
    mean = series.expanding(min_periods=min_periods).mean()
    std = series.expanding(min_periods=min_periods).std()
    z = (series - mean) / std.replace(0, np.nan)
    return z.clip(-winsorize, winsorize)


def threshold_sweep(signal_z, fwd_returns, name, risk_side='low'):
    """
    Sweep thresholds. For 'low' risk_side, test obs BELOW threshold.
    For 'high', test obs ABOVE threshold. For 'extreme', do both tails.
    """
    primary_col = f'fwd_{OPT_PRIMARY_HORIZON}d'
    df = pd.DataFrame({'sig': signal_z}).join(fwd_returns).dropna()
    if len(df) < 200:
        print(f"  [{name}] insufficient data ({len(df)} obs)")
        return None

    base_dd5 = (df[primary_col] < -0.05).mean()
    base_dd10 = (df[primary_col] < -0.10).mean()
    base_neg = (df[primary_col] < 0).mean()

    print(f"\n=== {name} threshold sweep ===")
    print(f"Aligned: {len(df)} obs, "
          f"{df.index.min().date()} to {df.index.max().date()}")
    print(f"Base 63d <-5%: {base_dd5:.1%}  <-10%: {base_dd10:.1%}")
    print(f"Risk side: {risk_side}")
    print()

    results = []

    if risk_side in ('low', 'extreme'):
        # Test obs BELOW threshold (signal weakens)
        print("Testing OBS BELOW threshold (signal weakens):")
        print(f"  {'Thresh':>7}  {'N':>5}  {'%pop':>5}  "
              f"{'63d Mean':>9}  {'<-5%':>6}  {'<-10%':>6}  "
              f"{'Lift5':>6}  {'Lift10':>6}")
        print(f"  {'-'*72}")
        for t in np.arange(-2.0, 0.6, 0.1):
            t = round(t, 2)
            sub = df[df['sig'] <= t]
            n = len(sub)
            if n < 30:
                continue
            pct_pop = n / len(df)
            mean63 = sub[primary_col].mean()
            dd5 = (sub[primary_col] < -0.05).mean()
            dd10 = (sub[primary_col] < -0.10).mean()
            lift5 = dd5 / base_dd5 if base_dd5 > 0 else np.nan
            lift10 = dd10 / base_dd10 if base_dd10 > 0 else np.nan
            print(f"  {t:>+7.2f}  {n:>5}  {pct_pop:>5.1%}  "
                  f"{mean63:>+9.4f}  {dd5:>6.1%}  {dd10:>6.1%}  "
                  f"{lift5:>6.2f}  {lift10:>6.2f}")
            results.append({
                'side': 'below', 'threshold': t, 'n': n,
                'pct_population': float(pct_pop),
                'mean_63d': float(mean63),
                'pct_below_neg5_63d': float(dd5),
                'pct_below_neg10_63d': float(dd10),
                'lift_5pct': float(lift5),
                'lift_10pct': float(lift10),
            })

    if risk_side in ('high', 'extreme'):
        print()
        print("Testing OBS ABOVE threshold (signal extreme):")
        print(f"  {'Thresh':>7}  {'N':>5}  {'%pop':>5}  "
              f"{'63d Mean':>9}  {'<-5%':>6}  {'<-10%':>6}  "
              f"{'Lift5':>6}  {'Lift10':>6}")
        print(f"  {'-'*72}")
        for t in np.arange(-0.5, 2.5, 0.1):
            t = round(t, 2)
            sub = df[df['sig'] >= t]
            n = len(sub)
            if n < 30:
                continue
            pct_pop = n / len(df)
            mean63 = sub[primary_col].mean()
            dd5 = (sub[primary_col] < -0.05).mean()
            dd10 = (sub[primary_col] < -0.10).mean()
            lift5 = dd5 / base_dd5 if base_dd5 > 0 else np.nan
            lift10 = dd10 / base_dd10 if base_dd10 > 0 else np.nan
            print(f"  {t:>+7.2f}  {n:>5}  {pct_pop:>5.1%}  "
                  f"{mean63:>+9.4f}  {dd5:>6.1%}  {dd10:>6.1%}  "
                  f"{lift5:>6.2f}  {lift10:>6.2f}")
            results.append({
                'side': 'above', 'threshold': t, 'n': n,
                'pct_population': float(pct_pop),
                'mean_63d': float(mean63),
                'pct_below_neg5_63d': float(dd5),
                'pct_below_neg10_63d': float(dd10),
                'lift_5pct': float(lift5),
                'lift_10pct': float(lift10),
            })

    # Recommend strongest break
    valid = [r for r in results if r['lift_10pct'] >= 1.5 and r['n'] >= 30]
    if valid:
        # For 'below' side, want most negative threshold; for 'above', most positive
        below = sorted([r for r in valid if r['side'] == 'below'],
                       key=lambda r: -r['threshold'])  # least extreme first
        above = sorted([r for r in valid if r['side'] == 'above'],
                       key=lambda r: r['threshold'])
        print()
        print("Strongest meaningful break(s):")
        for cands, label in [(below, 'BELOW'), (above, 'ABOVE')]:
            best = max(cands, key=lambda r: r['lift_10pct']) if cands else None
            if best:
                print(f"  {label} {best['threshold']:+.2f}: "
                      f"n={best['n']} ({best['pct_population']:.1%}), "
                      f"lift10={best['lift_10pct']:.2f}x, "
                      f"63d mean={best['mean_63d']:+.2%}")

    return {
        'name': name,
        'n_aligned': len(df),
        'date_range': [str(df.index.min().date()), str(df.index.max().date())],
        'base_pct_below_neg5_63d': float(base_dd5),
        'base_pct_below_neg10_63d': float(base_dd10),
        'sweep': results,
    }


def main():
    print("="*70)
    print("PHASE 2 THRESHOLD OPTIMIZATION")
    print(f"Run: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("="*70)

    # SPX forward returns
    print("\nLoading SPX + computing forward returns...")
    pillars, spx, _, _ = load_data(DB_PATH)
    fwd_returns = compute_forward_returns(spx)

    # Load each indicator
    conn = sqlite3.connect(DB_PATH)
    out = {
        'run_date': datetime.now().isoformat(),
        'indicators': {},
    }

    for name, cfg in INDICATORS.items():
        sig = load_indicator(conn, name)
        if sig.empty:
            print(f"\n[SKIP] {name}: no data")
            continue
        sig_z = expanding_zscore(sig)
        result = threshold_sweep(sig_z, fwd_returns, name, cfg['risk_side'])
        if result:
            result['risk_side'] = cfg['risk_side']
            result['description'] = cfg['desc']
            out['indicators'][name] = result

    conn.close()

    OUT_PATH.write_text(json.dumps(out, indent=2, default=str))
    print(f"\nSaved to: {OUT_PATH}")


if __name__ == "__main__":
    main()
