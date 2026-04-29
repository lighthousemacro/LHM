#!/usr/bin/env python3
"""
Phase 2 Threshold Optimization v2 — domain-appropriate targets
================================================================
v1 used forward 63d SPX returns for everything. That's wrong for LCI
(funding stress) and CLG (credit widening). v2 uses domain targets:

  MSI: fwd SPX 21d/63d (broader equity risk)
  SPI: fwd SPX 5d/10d/21d (contrarian; short horizons; both tails)
  SBD: fwd SPX 21d/63d (distribution warning)
  SSD: fwd SPX 5d/10d/21d (sentiment-structure divergence; short)
  LCI: fwd HY OAS WIDENING events (1-4 weeks; not equity returns)
  CLG: fwd HY OAS WIDENING events (3-6 months)

For LCI/CLG, we need an HY OAS series. The DB likely has BAMLH0A0HYM2.
Test: when LCI/CLG hits extreme, does HY OAS spike in next 4-12 weeks?

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
OUT_PATH = OUTPUT_DIR / "phase2_threshold_v2_results.json"


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
    """For each date t, compute max(series[t:t+h]) - series[t]."""
    s = series.copy()
    out = pd.Series(index=s.index, dtype=float)
    arr = s.values
    for i in range(len(arr) - horizon_days):
        out.iloc[i] = arr[i:i+horizon_days+1].max() - arr[i]
    return out


def threshold_sweep_returns(signal_z, fwd_returns, name, risk_side, horizons):
    """Sweep against forward returns at multiple horizons."""
    print(f"\n=== {name} threshold sweep (forward equity returns) ===")
    print(f"Risk side: {risk_side}, horizons: {horizons}")

    results = {}
    for h in horizons:
        col = f'fwd_{h}d'
        if col not in fwd_returns.columns:
            continue

        df = pd.DataFrame({'sig': signal_z, 'fwd': fwd_returns[col]}).dropna()
        if len(df) < 200:
            continue

        base_dd5 = (df['fwd'] < -0.05).mean()
        base_neg = (df['fwd'] < 0).mean()
        print(f"\n  {h}d horizon: base <0% = {base_neg:.1%}, "
              f"<-5% = {base_dd5:.1%}, n={len(df)}")
        print(f"  {'Thresh':>7} {'Side':>6} {'N':>5} {'%pop':>5} "
              f"{'Mean':>9} {'%neg':>6} {'%<-5':>6} "
              f"{'Lift5':>6}")
        print(f"  {'-'*68}")

        h_results = []
        sides_to_test = ['below'] if risk_side == 'low' else \
                        ['above'] if risk_side == 'high' else \
                        ['below', 'above']

        for side in sides_to_test:
            t_range = np.arange(-2.0, 0.6, 0.2) if side == 'below' \
                else np.arange(-0.5, 2.5, 0.2)
            best = None
            for t in t_range:
                t = round(t, 2)
                if side == 'below':
                    sub = df[df['sig'] <= t]
                else:
                    sub = df[df['sig'] >= t]
                n = len(sub)
                if n < 30:
                    continue
                pct_pop = n / len(df)
                mean = sub['fwd'].mean()
                pct_neg = (sub['fwd'] < 0).mean()
                pct_dd5 = (sub['fwd'] < -0.05).mean()
                lift5 = pct_dd5 / base_dd5 if base_dd5 > 0 else np.nan
                row = {
                    'side': side, 'threshold': t, 'n': n,
                    'pct_population': float(pct_pop),
                    'mean': float(mean),
                    'pct_neg': float(pct_neg),
                    'pct_below_neg5': float(pct_dd5),
                    'lift_5pct': float(lift5),
                }
                h_results.append(row)
                if best is None or lift5 > best['lift_5pct']:
                    best = row

            # Print only the best 3 per side
            sorted_side = sorted([r for r in h_results if r['side'] == side],
                                 key=lambda r: -r['lift_5pct'])[:3]
            for r in sorted_side:
                print(f"  {r['threshold']:>+7.2f} {r['side']:>6} {r['n']:>5} "
                      f"{r['pct_population']:>5.1%} "
                      f"{r['mean']:>+9.4f} {r['pct_neg']:>6.1%} "
                      f"{r['pct_below_neg5']:>6.1%} {r['lift_5pct']:>6.2f}")

        results[f'{h}d'] = h_results

    return results


def threshold_sweep_hy_widening(signal_z, hy_oas, name, risk_side, horizons_days):
    """
    Sweep signal against forward HY OAS widening events.
    Event = HY OAS rises by >= X bps within horizon_days.
    """
    print(f"\n=== {name} threshold sweep (forward HY OAS widening) ===")
    print(f"Risk side: {risk_side}, horizons: {horizons_days} days")

    # HY OAS spread (already in percentage points)
    hy = hy_oas.copy()
    df_align = pd.DataFrame({'sig': signal_z, 'hy': hy}).dropna()

    if len(df_align) < 200:
        print(f"  Insufficient aligned data ({len(df_align)} obs)")
        return None

    # For each horizon, compute fwd max widening
    print(f"  Computing forward widening over {horizons_days} days...")
    results = {}
    for h in horizons_days:
        df = df_align.copy()
        df[f'fwd_widening_{h}d'] = fwd_max_change(df['hy'], h)
        df = df.dropna()
        if len(df) < 200:
            continue

        # Define a "widening event" as fwd max widening > 100 bps (1.00 pp)
        EVENT_BPS = 1.00
        base_event = (df[f'fwd_widening_{h}d'] >= EVENT_BPS).mean()

        print(f"\n  {h}d horizon: base event rate (>=100bps widening) = "
              f"{base_event:.1%}, n={len(df)}")
        print(f"  {'Thresh':>7} {'Side':>6} {'N':>5} {'%pop':>5} "
              f"{'Mean wid':>10} {'%event':>7} {'Lift':>6}")
        print(f"  {'-'*65}")

        h_results = []
        sides_to_test = ['below'] if risk_side == 'low' else ['above']
        for side in sides_to_test:
            t_range = np.arange(-2.0, 0.6, 0.2) if side == 'below' \
                else np.arange(-0.5, 2.5, 0.2)
            for t in t_range:
                t = round(t, 2)
                if side == 'below':
                    sub = df[df['sig'] <= t]
                else:
                    sub = df[df['sig'] >= t]
                n = len(sub)
                if n < 30:
                    continue
                pct_pop = n / len(df)
                mean_wid = sub[f'fwd_widening_{h}d'].mean()
                pct_event = (sub[f'fwd_widening_{h}d'] >= EVENT_BPS).mean()
                lift = pct_event / base_event if base_event > 0 else np.nan
                h_results.append({
                    'side': side, 'threshold': t, 'n': n,
                    'pct_population': float(pct_pop),
                    'mean_widening_pp': float(mean_wid),
                    'pct_event_100bps': float(pct_event),
                    'lift': float(lift),
                })

            sorted_side = sorted([r for r in h_results if r['side'] == side],
                                 key=lambda r: -r['lift'])[:3]
            for r in sorted_side:
                print(f"  {r['threshold']:>+7.2f} {r['side']:>6} {r['n']:>5} "
                      f"{r['pct_population']:>5.1%} "
                      f"{r['mean_widening_pp']:>+10.3f} {r['pct_event_100bps']:>7.1%} "
                      f"{r['lift']:>6.2f}")

        results[f'{h}d'] = h_results

    return results


def main():
    print("="*70)
    print("PHASE 2 v2 — DOMAIN-APPROPRIATE TARGETS")
    print(f"Run: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("="*70)

    # SPX forward returns
    print("\nLoading SPX + computing forward returns...")
    pillars, spx, _, _ = load_data(DB_PATH)
    fwd_returns = compute_forward_returns(spx)

    conn = sqlite3.connect(DB_PATH)

    # HY OAS — try BAMLH0A0HYM2 and a few alternates
    hy_candidates = ['BAMLH0A0HYM2', 'HY_OAS', 'BofAMLHYOAS']
    hy_oas = None
    for sid in hy_candidates:
        s = load_observation(conn, sid)
        if len(s) > 1000:
            hy_oas = s
            print(f"HY OAS series: {sid} ({len(s)} obs, "
                  f"{s.index.min().date()} to {s.index.max().date()})")
            break
    if hy_oas is None:
        # Search for HY-like
        hy_search = pd.read_sql(
            "SELECT series_id, title, frequency FROM series_meta "
            "WHERE LOWER(title) LIKE '%high yield%' OR LOWER(title) LIKE '%hy oas%' "
            "OR series_id LIKE '%BAML%' LIMIT 10", conn)
        print(f"HY OAS not found. Search results:")
        print(hy_search.to_string())

    out = {
        'run_date': datetime.now().isoformat(),
        'indicators': {},
    }

    # MSI/SPI/SBD/SSD against forward SPX
    fwd_targets = {
        'MSI':  ('low', [21, 63]),
        'SPI':  ('high', [5, 10, 21]),
        'SBD':  ('high', [21, 63]),
        'SSD':  ('extreme', [5, 10, 21]),
    }
    for name, (side, horizons) in fwd_targets.items():
        sig = load_indicator(conn, name)
        if sig.empty:
            continue
        sig_z = expanding_zscore(sig)
        out['indicators'][name] = {
            'risk_side': side,
            'target': 'forward_spx_returns',
            'results': threshold_sweep_returns(sig_z, fwd_returns, name, side, horizons)
        }

    # LCI/CLG against forward HY widening
    if hy_oas is not None:
        for name in ['LCI', 'CLG']:
            sig = load_indicator(conn, name)
            if sig.empty:
                continue
            sig_z = expanding_zscore(sig)
            horizons = [21, 63] if name == 'LCI' else [63, 126]
            out['indicators'][name] = {
                'risk_side': 'low',
                'target': 'forward_hy_oas_widening',
                'results': threshold_sweep_hy_widening(
                    sig_z, hy_oas, name, 'low', horizons)
            }

    conn.close()
    OUT_PATH.write_text(json.dumps(out, indent=2, default=str))
    print(f"\nSaved to: {OUT_PATH}")


if __name__ == "__main__":
    main()
