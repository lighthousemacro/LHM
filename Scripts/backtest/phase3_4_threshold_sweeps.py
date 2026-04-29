#!/usr/bin/env python3
"""
Phase 3 + 4 — Tier B Pillars + Standalone Signals
====================================================
Phase 3: 9 Tier B pillars (LPI, PCI, GCI, HCI, CCI, BCI, TCI, GCI_Gov, FCI)
        target = domain variable (forward UR change for LPI, fwd PCE for CCI, etc)
        Per master plan, do NOT optimize against forward equity returns.

Phase 4: Standalone signals (CLG, SBD, SSD already covered in Phase 2;
        focus on threshold validation against domain targets here)

Methodology: same threshold-sweep approach. For each pillar:
  - Find the threshold where the domain variable's forward outcome
    deviates most from base rate
  - Report: best threshold, n, lift, mean fwd outcome

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
OUT_PATH = OUTPUT_DIR / "phase3_4_threshold_results.json"


# Pillar -> (target series_id, fwd horizon in days, risk_side, what to test)
# All targets are series in the observations table or computed
TIER_B_TARGETS = {
    'LPI': {
        'targets': [
            ('UNRATE', 'forward unemployment rate change', 'monthly_to_daily', 252),
        ],
        'risk_side': 'low',  # low LPI = labor weak
    },
    'PCI': {
        'targets': [
            ('PCEPILFE', 'forward core PCE YoY', 'monthly_to_daily', 365),
        ],
        'risk_side': 'high',  # high PCI = inflation pressure
    },
    'GCI': {
        'targets': [
            ('GDPC1', 'forward real GDP YoY', 'quarterly_to_daily', 365),
        ],
        'risk_side': 'low',  # low GCI = growth weak
    },
    'HCI': {
        'targets': [
            ('HOUST', 'forward housing starts YoY', 'monthly_to_daily', 365),
        ],
        'risk_side': 'low',
    },
    'CCI': {
        'targets': [
            ('PCEC96', 'forward real PCE YoY', 'monthly_to_daily', 365),
        ],
        'risk_side': 'low',
    },
    'BCI': {
        'targets': [
            ('NEWORDER', 'forward non-def cap goods orders YoY',
             'monthly_to_daily', 365),
        ],
        'risk_side': 'low',
    },
    'TCI': {
        'targets': [
            # Net exports / GDP — try a few candidates
            ('NETEXP', 'forward net exports', 'quarterly_to_daily', 365),
        ],
        'risk_side': 'low',
    },
    'GCI_Gov': {
        'targets': [
            # Term premium — ACM model series at NY Fed
            ('THREEFYTP10', 'forward 10y term premium', 'daily', 252),
        ],
        'risk_side': 'high',  # high GCI_Gov = fiscal stress
    },
    'FCI': {
        'targets': [
            # HY OAS — already loaded
            ('BAMLH0A0HYM2', 'forward HY OAS widening', 'daily', 126),
        ],
        'risk_side': 'low',  # low FCI = financial conditions tight
    },
}


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


def fwd_change(series, horizon_days, mode='delta'):
    """For each date t: series[t+h] - series[t] (delta) or YoY (yoy)."""
    s = series.copy().sort_index()
    out = pd.Series(index=s.index, dtype=float)
    if mode == 'delta':
        out = s.shift(-horizon_days) - s
    elif mode == 'yoy_pct':
        out = (s.shift(-horizon_days) / s - 1) * 100
    return out


def fwd_max(series, horizon_days):
    """For each t: max(series[t:t+h]) - series[t]"""
    s = series.copy().sort_index()
    out = pd.Series(index=s.index, dtype=float)
    arr = s.values
    for i in range(len(arr) - horizon_days):
        out.iloc[i] = arr[i:i+horizon_days+1].max() - arr[i]
    return out


def threshold_sweep(signal_z, fwd_target, name, target_name, risk_side,
                    event_threshold=None, event_label='event'):
    """
    Sweep signal threshold against forward target.

    If event_threshold is set: bucket fwd_target as event/non-event
    (e.g. UR change > 0.5 = event)
    Otherwise: report mean and lift on negative outcome.
    """
    df = pd.DataFrame({'sig': signal_z, 'fwd': fwd_target}).dropna()
    if len(df) < 100:
        return None

    print(f"\n=== {name} → {target_name} ===")
    print(f"Aligned: {len(df)} obs, "
          f"{df.index.min().date()} to {df.index.max().date()}")

    # Determine event direction
    # For LPI low: UR rises (delta > 0). For GCI low: GDP YoY negative. Etc.
    # Use event_threshold to define.
    if event_threshold is not None:
        if risk_side == 'low':  # signal weak -> event happens
            base_event = (df['fwd'] >= event_threshold).mean()
            event_op = '>='
        else:  # signal strong -> event happens
            base_event = (df['fwd'] >= event_threshold).mean()
            event_op = '>='
    else:
        # Use median split as fallback
        event_threshold = df['fwd'].median()
        base_event = 0.5
        event_op = '>'

    print(f"Base event rate ({event_label} {event_op} {event_threshold:.3f}): "
          f"{base_event:.1%}")
    print(f"Risk side: {risk_side}")
    print()
    print(f"  {'Thresh':>7} {'Side':>6} {'N':>5} {'%pop':>5} "
          f"{'Mean fwd':>10} {'%event':>7} {'Lift':>6}")
    print(f"  {'-'*65}")

    results = []
    sides_to_test = ['below'] if risk_side == 'low' else ['above']
    for side in sides_to_test:
        if side == 'below':
            t_range = np.arange(-2.0, 0.6, 0.2)
        else:
            t_range = np.arange(-0.5, 2.5, 0.2)
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
            mean_fwd = sub['fwd'].mean()
            pct_event = (sub['fwd'] >= event_threshold).mean()
            lift = pct_event / base_event if base_event > 0 else np.nan
            results.append({
                'side': side, 'threshold': t, 'n': n,
                'pct_population': float(pct_pop),
                'mean_fwd': float(mean_fwd),
                'pct_event': float(pct_event),
                'lift': float(lift),
            })

        # Print top 3 by lift
        sorted_top = sorted([r for r in results if r['side'] == side],
                            key=lambda r: -r['lift'])[:3]
        for r in sorted_top:
            print(f"  {r['threshold']:>+7.2f} {r['side']:>6} {r['n']:>5} "
                  f"{r['pct_population']:>5.1%} "
                  f"{r['mean_fwd']:>+10.4f} {r['pct_event']:>7.1%} "
                  f"{r['lift']:>6.2f}")

    return {
        'pillar': name,
        'target': target_name,
        'event_threshold': float(event_threshold),
        'event_label': event_label,
        'base_event_rate': float(base_event),
        'n_aligned': len(df),
        'sweep': results,
    }


def main():
    print("="*70)
    print("PHASE 3+4 — TIER B PILLARS / STANDALONE SIGNALS")
    print(f"Run: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("="*70)

    conn = sqlite3.connect(DB_PATH)
    out = {'run_date': datetime.now().isoformat(), 'pillars': {}}

    # Custom configurations (target_series_id, horizon_days, mode, event_threshold, label)
    configs = {
        'LPI': ('UNRATE', 252, 'delta', 0.5, 'UR rise >= 0.5pp'),
        'PCI': ('PCEPILFE', 365, 'yoy_pct', 3.0, 'core PCE YoY >= 3%'),
        'GCI': ('GDPC1', 365, 'yoy_pct', -0.5, 'real GDP YoY <= -0.5%'),  # rare
        'HCI': ('HOUST', 365, 'yoy_pct', -10.0, 'housing starts YoY <= -10%'),
        'CCI': ('PCEC96', 365, 'yoy_pct', 0.5, 'real PCE YoY <= 0.5%'),
        'BCI': ('NEWORDER', 365, 'yoy_pct', -2.0, 'cap goods YoY <= -2%'),
        'TCI': ('NETEXP', 365, 'delta', 0.0, 'net exports declining'),
        'GCI_Gov': ('THREEFYTP10', 252, 'delta', 0.5, '10y term premium rising 0.5pp'),
        'FCI': ('BAMLH0A0HYM2', 126, 'fwd_max', 1.0, 'HY OAS widens >= 100bps'),
    }

    # Map flip for "low" risk side: actually, event_thresholds for "low" pillars
    # should denote the bad outcome. Adjusting:
    # LPI risk side = low means LPI weak; bad outcome = UR rises (event_threshold = 0.5 already correct)
    # For GCI low: GDP -0.5% bad. We compare fwd >= -0.5? No, want fwd <= -0.5 to be the event.
    # I'll handle directionality in the sweep function using a 'event_direction' flag.

    for pillar in ['LPI', 'PCI', 'GCI', 'HCI', 'CCI', 'BCI', 'TCI', 'GCI_Gov', 'FCI']:
        cfg = configs.get(pillar)
        if cfg is None:
            continue
        target_sid, h, mode, event_threshold, event_label = cfg

        sig = load_indicator(conn, pillar)
        if sig.empty:
            print(f"\n[SKIP] {pillar}: no indicator data")
            continue
        sig_z = expanding_zscore(sig)

        target_series = load_observation(conn, target_sid)
        if target_series.empty:
            print(f"\n[SKIP] {pillar}: target series {target_sid} not found")
            continue

        # Forward-fill monthly/quarterly to daily before computing fwd change
        target_daily = target_series.resample('D').ffill()

        if mode == 'delta':
            fwd = fwd_change(target_daily, h, 'delta')
        elif mode == 'yoy_pct':
            fwd = fwd_change(target_daily, h, 'yoy_pct')
        elif mode == 'fwd_max':
            fwd = fwd_max(target_daily, h)
        else:
            continue

        # Determine which direction is "bad"
        # For pillars with risk_side='low' (LPI, GCI, HCI, CCI, BCI, TCI, FCI):
        #   - LPI low -> UR rises (positive delta is bad)        -> event = fwd >= +threshold
        #   - GCI low -> GDP negative (negative YoY is bad)      -> event = fwd <= threshold (negative)
        #   - HCI low -> housing YoY very negative is bad        -> event = fwd <= -threshold
        #   - CCI low -> PCE YoY very low is bad                 -> event = fwd <= threshold
        #   - BCI low -> cap goods YoY negative is bad           -> event = fwd <= threshold
        #   - TCI low -> net exports declining (negative delta)  -> event = fwd <= threshold
        #   - FCI low -> HY OAS WIDENING (positive change is bad)-> event = fwd >= threshold
        # For 'high' (PCI, GCI_Gov):
        #   - PCI high -> inflation high                         -> event = fwd >= threshold
        #   - GCI_Gov high -> term premium rising                -> event = fwd >= threshold

        # Adjusted event_threshold sign-aware logic:
        # If event_threshold is positive, event = fwd >= threshold
        # If event_threshold is negative, event = fwd <= threshold
        # If zero, event = fwd <= 0
        risk_side = TIER_B_TARGETS[pillar]['risk_side']

        df = pd.DataFrame({'sig': sig_z, 'fwd': fwd}).dropna()
        if len(df) < 100:
            print(f"\n[SKIP] {pillar}: insufficient aligned data ({len(df)})")
            continue

        # Event definition based on threshold sign
        if event_threshold > 0:
            base_event = (df['fwd'] >= event_threshold).mean()
            event_op = '>='
        elif event_threshold < 0:
            base_event = (df['fwd'] <= event_threshold).mean()
            event_op = '<='
        else:
            # zero: assume "bad" means negative for low-risk-side
            base_event = (df['fwd'] <= 0).mean()
            event_op = '<= 0'

        print(f"\n=== {pillar} → {event_label} (h={h}d, side={risk_side}) ===")
        print(f"Aligned: {len(df)} obs, "
              f"{df.index.min().date()} to {df.index.max().date()}")
        print(f"Base event rate: {base_event:.1%}")
        if base_event < 0.01:
            print(f"  [WARN] Event too rare to test reliably")
            continue

        print(f"  {'Thresh':>7} {'Side':>6} {'N':>5} {'%pop':>5} "
              f"{'Mean fwd':>10} {'%event':>7} {'Lift':>6}")
        print(f"  {'-'*65}")

        results = []
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
                mean_fwd = sub['fwd'].mean()
                if event_threshold > 0:
                    pct_event = (sub['fwd'] >= event_threshold).mean()
                elif event_threshold < 0:
                    pct_event = (sub['fwd'] <= event_threshold).mean()
                else:
                    pct_event = (sub['fwd'] <= 0).mean()
                lift = pct_event / base_event if base_event > 0 else np.nan
                results.append({
                    'side': side, 'threshold': t, 'n': n,
                    'pct_population': float(pct_pop),
                    'mean_fwd': float(mean_fwd),
                    'pct_event': float(pct_event),
                    'lift': float(lift),
                })

            # Print top 3 by lift
            sorted_top = sorted([r for r in results if r['side'] == side],
                                key=lambda r: -r['lift'])[:3]
            for r in sorted_top:
                print(f"  {r['threshold']:>+7.2f} {r['side']:>6} {r['n']:>5} "
                      f"{r['pct_population']:>5.1%} "
                      f"{r['mean_fwd']:>+10.4f} {r['pct_event']:>7.1%} "
                      f"{r['lift']:>6.2f}")

        out['pillars'][pillar] = {
            'target': target_sid,
            'event_label': event_label,
            'event_threshold': float(event_threshold),
            'event_op': event_op,
            'horizon_days': h,
            'risk_side': risk_side,
            'base_event_rate': float(base_event),
            'n_aligned': len(df),
            'sweep': results,
        }

    conn.close()
    OUT_PATH.write_text(json.dumps(out, indent=2, default=str))
    print(f"\nSaved to: {OUT_PATH}")


if __name__ == "__main__":
    main()
