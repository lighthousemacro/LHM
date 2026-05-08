"""
LHM Validation Engine
=====================

Walk-forward weight optimization for the 11 pillar composites (excluding CLI,
which is its own validated v5 architecture). Objective: maximize the 63-day
forward Information Coefficient (IC) against the appropriate benchmark.

Design:
  1. Pull each pillar's series from the descriptive_atlas table.
  2. Convert each series into a z-score representation:
       - Daily/weekly series: 252-day rolling z
       - Monthly series: forward-fill to daily, then 252-day rolling z
  3. Build a panel of (date, series_id) z-score values.
  4. Walk-forward windows:
       - Train on 5 years
       - Optimize weights via scipy.optimize.minimize, objective = -rank IC
         of weighted composite vs 63d forward log return of benchmark
       - Test on next 1 year out-of-sample
       - Roll forward 1 year
  5. Aggregate out-of-sample IC across all windows.
  6. Compare empirical weights to expert (equal-weight + named-component)
     baselines.

Outputs:
  - validation_results.json keyed by pillar_id with:
      - empirical_weights (component -> weight)
      - oos_ic (out-of-sample IC mean)
      - oos_ic_t_stat
      - is_ic (in-sample for comparison)
      - benchmark
  - Optional per-pillar plot of weight stability across rolling windows.

Usage:
  python scripts/validation_engine.py --pillar 1
  python scripts/validation_engine.py --pillar all --benchmark SPY
"""
import os
import sys
import json
import argparse
import sqlite3
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf
from scipy.optimize import minimize
from scipy.stats import spearmanr

DB = '/Users/bob/LHM/Data/databases/Lighthouse_Master.db'
OUT_DIR = '/Users/bob/LHM/Outputs/validation'
os.makedirs(OUT_DIR, exist_ok=True)

PILLAR_BENCHMARK = {
    1:  'SPY',   # Labor
    2:  'SPY',   # Prices
    3:  'SPY',   # Growth
    4:  'SPY',   # Housing -> XLRE if available, else SPY
    5:  'SPY',   # Consumer -> XLY/XLP composite preferred, default SPY
    6:  'SPY',   # Business
    7:  'SPY',   # Trade -> dollar-sensitive; SPY default
    8:  '^TYX',  # Government -> 30Y yield (TYX)
    9:  'HYG',   # Financial -> high yield
    10: 'BTC-USD',  # Plumbing -> liquidity to BTC
    11: 'SPY',   # Structure -> SPY directly
}

FORWARD_HORIZON_DAYS = 63
TRAIN_YEARS = 5
TEST_YEARS = 1
ROLL_YEARS = 1


# ---------------------------------------------------------------
# Data utilities
# ---------------------------------------------------------------
def load_atlas(conn, pillar_id):
    q = """
        SELECT series_id, title, frequency
        FROM descriptive_atlas
        WHERE pillar_id = ?
        ORDER BY rank
    """
    return pd.read_sql(q, conn, params=(pillar_id,))


def load_observations(conn, series_ids, start_date='2005-01-01'):
    placeholders = ','.join(['?'] * len(series_ids))
    q = f"""
        SELECT series_id, date, value
        FROM observations
        WHERE series_id IN ({placeholders}) AND date >= ?
        ORDER BY series_id, date
    """
    df = pd.read_sql(q, conn, params=list(series_ids) + [start_date],
                     parse_dates=['date'])
    return df.pivot(index='date', columns='series_id', values='value')


def rolling_z(panel, window=252, min_periods=126):
    """Rolling z-score per column. Forward-fills first to align mixed frequencies."""
    panel = panel.ffill()
    mean = panel.rolling(window, min_periods=min_periods).mean()
    std = panel.rolling(window, min_periods=min_periods).std()
    return (panel - mean) / std


def fetch_benchmark(symbol, start='2005-01-01'):
    df = yf.download(symbol, start=start, auto_adjust=True, progress=False)['Close']
    if isinstance(df, pd.DataFrame):
        df = df.iloc[:, 0]
    df.index = pd.DatetimeIndex(df.index).tz_localize(None)
    return df


def forward_return(price, horizon=FORWARD_HORIZON_DAYS):
    return np.log(price.shift(-horizon) / price)


# ---------------------------------------------------------------
# Optimization
# ---------------------------------------------------------------
def neg_rank_ic(weights, X, y):
    """Negative rank IC for use with scipy.optimize.minimize."""
    composite = X @ weights
    mask = composite.notna() & y.notna()
    if mask.sum() < 30:
        return 1.0  # bad fit
    rho, _ = spearmanr(composite[mask], y[mask])
    return -rho if not np.isnan(rho) else 1.0


def optimize_weights(z_panel, fwd_ret, n_components):
    """Find optimal weights summing to 1, each in [0, 0.5]."""
    aligned = z_panel.copy().fillna(0.0)
    aligned['__y'] = fwd_ret
    aligned = aligned.dropna(subset=['__y'])
    if len(aligned) < 100:
        return None, None
    X = aligned.iloc[:, :-1]
    y = aligned['__y']

    x0 = np.ones(n_components) / n_components
    bounds = [(0.0, 0.5)] * n_components
    constraints = [{'type': 'eq', 'fun': lambda w: np.sum(w) - 1.0}]

    res = minimize(neg_rank_ic, x0, args=(X, y), bounds=bounds,
                   constraints=constraints, method='SLSQP',
                   options={'maxiter': 100, 'ftol': 1e-6})
    if not res.success:
        return None, None
    return res.x, -res.fun


def walk_forward(z_panel, fwd_ret, train_y=TRAIN_YEARS, test_y=TEST_YEARS,
                 roll_y=ROLL_YEARS):
    """Run walk-forward optimization. Returns list of (window_end, weights, oos_ic)."""
    aligned = z_panel.copy()
    # Fill missing component z-scores with 0 (neutral) instead of dropping rows.
    # This keeps the panel populated when components have different start dates.
    aligned = aligned.fillna(0.0)
    aligned['__y'] = fwd_ret
    aligned = aligned.dropna(subset=['__y'])
    if len(aligned) < 252 * (train_y + test_y):
        print(f'[debug] aligned len={len(aligned)}, need {252*(train_y+test_y)}')
        return []

    n_components = z_panel.shape[1]
    results = []
    start = aligned.index[0]
    train_end = start + pd.DateOffset(years=train_y)
    end = aligned.index[-1]

    while train_end + pd.DateOffset(years=test_y) <= end:
        test_end = train_end + pd.DateOffset(years=test_y)
        train_data = aligned.loc[start:train_end]
        test_data = aligned.loc[train_end:test_end]

        if len(train_data) < 252 or len(test_data) < 60:
            train_end += pd.DateOffset(years=roll_y)
            continue

        weights, train_ic = optimize_weights(
            train_data.iloc[:, :-1], train_data['__y'], n_components)
        if weights is None:
            train_end += pd.DateOffset(years=roll_y)
            continue

        # OOS IC
        composite_oos = test_data.iloc[:, :-1] @ weights
        y_oos = test_data['__y']
        mask = composite_oos.notna() & y_oos.notna()
        if mask.sum() > 30:
            oos_ic, _ = spearmanr(composite_oos[mask], y_oos[mask])
        else:
            oos_ic = np.nan

        results.append({
            'train_end': train_end.strftime('%Y-%m-%d'),
            'test_end': test_end.strftime('%Y-%m-%d'),
            'weights': weights.tolist(),
            'train_ic': train_ic,
            'oos_ic': oos_ic if not np.isnan(oos_ic) else None,
            'n_train': len(train_data),
            'n_test': len(test_data),
        })

        train_end += pd.DateOffset(years=roll_y)

    return results


# ---------------------------------------------------------------
# Pillar runner
# ---------------------------------------------------------------
def run_pillar(pillar_id, max_components=20):
    conn = sqlite3.connect(DB)
    atlas = load_atlas(conn, pillar_id)
    if atlas.empty:
        print(f'[Pillar {pillar_id}] no atlas series')
        return None

    series_ids = atlas['series_id'].tolist()[:max_components]
    print(f'[Pillar {pillar_id}] loading {len(series_ids)} series ...')
    panel = load_observations(conn, series_ids)
    panel = panel[series_ids]  # preserve atlas rank order
    z = rolling_z(panel)
    z = z.dropna(axis=1, how='all')
    z.index = pd.DatetimeIndex(z.index).tz_localize(None)
    conn.close()

    bench_sym = PILLAR_BENCHMARK.get(pillar_id, 'SPY')
    print(f'[Pillar {pillar_id}] benchmark: {bench_sym}')
    bench = fetch_benchmark(bench_sym)
    fwd = forward_return(bench)

    z = z.reindex(fwd.index, method='ffill')
    z = z.dropna(how='all')
    fwd = fwd.loc[z.index]

    print(f'[Pillar {pillar_id}] panel shape: {z.shape}, fwd shape: {fwd.shape}')
    wf = walk_forward(z, fwd)
    if not wf:
        print(f'[Pillar {pillar_id}] insufficient data for walk-forward')
        return None

    oos_ics = [w['oos_ic'] for w in wf if w['oos_ic'] is not None]
    if not oos_ics:
        return None

    mean_oos_ic = float(np.mean(oos_ics))
    t_stat = float(np.mean(oos_ics) / (np.std(oos_ics) / np.sqrt(len(oos_ics))))

    # Average weights across windows for the "empirical weight" spec
    all_weights = np.array([w['weights'] for w in wf])
    empirical_weights = all_weights.mean(axis=0)
    empirical_weights = empirical_weights / empirical_weights.sum()

    component_weights = dict(zip(z.columns, empirical_weights.round(4).tolist()))

    result = {
        'pillar_id': pillar_id,
        'benchmark': bench_sym,
        'n_components': len(z.columns),
        'n_windows': len(wf),
        'oos_ic_mean': mean_oos_ic,
        'oos_ic_t_stat': t_stat,
        'oos_ic_per_window': oos_ics,
        'empirical_weights': component_weights,
        'windows': wf,
    }

    out_path = f'{OUT_DIR}/pillar_{pillar_id:02d}_validation.json'
    with open(out_path, 'w') as f:
        json.dump(result, f, indent=2, default=str)
    print(f'[Pillar {pillar_id}] OOS IC: {mean_oos_ic:+.4f} (t={t_stat:+.2f}, n={len(oos_ics)} windows)')
    print(f'[Pillar {pillar_id}] saved -> {out_path}')
    return result


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--pillar', default='1', help='Pillar ID (1-11) or "all"')
    p.add_argument('--max-components', type=int, default=20,
                   help='Max series per pillar to optimize over (default 20)')
    args = p.parse_args()

    if args.pillar == 'all':
        results = {}
        for pid in range(1, 12):
            print(f'\n{"="*60}\nPILLAR {pid}\n{"="*60}')
            r = run_pillar(pid, args.max_components)
            if r:
                results[pid] = r
        # Aggregate summary
        with open(f'{OUT_DIR}/all_pillars_summary.json', 'w') as f:
            summary = {pid: {
                'oos_ic': r['oos_ic_mean'],
                't_stat': r['oos_ic_t_stat'],
                'n_components': r['n_components'],
                'benchmark': r['benchmark'],
            } for pid, r in results.items()}
            json.dump(summary, f, indent=2)
    else:
        run_pillar(int(args.pillar), args.max_components)


if __name__ == '__main__':
    main()
