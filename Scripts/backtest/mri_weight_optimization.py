#!/usr/bin/env python3
"""
MRI Weight Optimization — Lighthouse Macro
============================================
Applies CLI-grade rigor to the Macro Risk Index.

Methodology:
  - Pull 12 pillar indices from lighthouse_indices
  - Compute expanding z-scores (min 63 periods, ±3 winsorized)
  - Compute forward SPX returns at multiple horizons
  - Evaluate current (judgment) weights via quintile sorts
  - Optimize weights via Sortino-maximizing objective
  - Validate: monotonicity, t-stats, slugging, regime analysis
  - Walk-forward OOS (90/10 expanding window)

Target Variables:
  - Forward SPX total return (5d, 10d, 21d, 42d, 63d, 126d, 252d)
  - Forward max drawdown (63d, 126d, 252d)

Author: Bob Sheehan, CFA, CMT | Lighthouse Macro
Date: 2026-03-11
"""

import sqlite3
import pandas as pd
import numpy as np
from scipy.optimize import minimize
from scipy import stats
from datetime import datetime
import warnings
import json
import os

warnings.filterwarnings('ignore')

# ============================================================
# CONFIGURATION
# ============================================================

DB_PATH = "/Users/bob/LHM/Data/databases/Lighthouse_Master.db"
OUTPUT_DIR = "/Users/bob/LHM/Outputs/mri_optimization"
SCRIPT_DIR = "/Users/bob/LHM/Scripts/backtest"

# MRI component indices (from lighthouse_indices)
MRI_COMPONENTS = {
    'LPI':     {'sign': -1, 'current_weight': 0.13},
    'PCI':     {'sign': +1, 'current_weight': 0.08},
    'GCI':     {'sign': -1, 'current_weight': 0.13},
    'HCI':     {'sign': -1, 'current_weight': 0.06},
    'CCI':     {'sign': -1, 'current_weight': 0.08},
    'BCI':     {'sign': -1, 'current_weight': 0.08},
    'TCI':     {'sign': -1, 'current_weight': 0.05},
    'GCI_Gov': {'sign': +1, 'current_weight': 0.08},
    'FCI':     {'sign': -1, 'current_weight': 0.04},
    'LCI':     {'sign': -1, 'current_weight': 0.08},
    'MSI':     {'sign': -1, 'current_weight': 0.12},
    'SPI':     {'sign': -1, 'current_weight': 0.07},
}

# SPX series for forward returns
SPX_SERIES_ID = "SP500"  # Adjust if your FRED series_id differs

# Forward return horizons (trading days)
FWD_HORIZONS = [5, 10, 21, 42, 63, 126, 252]

# Drawdown horizons
DD_HORIZONS = [63, 126, 252]

# Z-score parameters (CLI standard)
Z_MIN_PERIODS = 63
Z_WINSORIZE = 3.0

# Quintile parameters
N_QUANTILES = 5

# Walk-forward OOS split
OOS_FRACTION = 0.10  # last 10% for OOS

# Optimization settings
OPT_PRIMARY_HORIZON = 63   # 63d (quarterly) as primary optimization horizon
OPT_OBJECTIVE = 'sortino'  # 'sortino', 'spread', 'ic'

# ============================================================
# DATA LOADING
# ============================================================

def load_data(db_path):
    """Load pillar indices and SPX prices from the database."""
    conn = sqlite3.connect(db_path)

    # --- Load pillar indices ---
    index_ids = list(MRI_COMPONENTS.keys())
    placeholders = ','.join(['?' for _ in index_ids])
    query = f"""
        SELECT index_id, date, value
        FROM lighthouse_indices
        WHERE index_id IN ({placeholders})
        ORDER BY date
    """
    idx_df = pd.read_sql(query, conn, params=index_ids)
    idx_df['date'] = pd.to_datetime(idx_df['date'])

    # Pivot: date x index_id
    pillars = idx_df.pivot(index='date', columns='index_id', values='value')
    pillars = pillars.sort_index()

    # --- Load existing MRI for comparison ---
    mri_query = """
        SELECT date, value AS MRI_existing
        FROM lighthouse_indices
        WHERE index_id = 'MRI'
        ORDER BY date
    """
    mri_df = pd.read_sql(mri_query, conn)
    mri_df['date'] = pd.to_datetime(mri_df['date'])
    mri_df = mri_df.set_index('date')

    # --- Load SPX prices ---
    # Try multiple possible series IDs
    spx_candidates = ['SPX_Close', 'SP500', 'SPX', 'GSPC', '^GSPC', 'SPY']
    spx_df = None
    spx_id_used = None

    for sid in spx_candidates:
        test_query = f"""
            SELECT date, value
            FROM observations
            WHERE series_id = ?
              AND value IS NOT NULL
            ORDER BY date
        """
        test_df = pd.read_sql(test_query, conn, params=[sid])
        if len(test_df) > 500:
            spx_df = test_df
            spx_id_used = sid
            break

    if spx_df is None:
        # Fallback: search series_meta
        search_query = """
            SELECT series_id, title, frequency
            FROM series_meta
            WHERE (title LIKE '%S&P 500%' OR title LIKE '%SP 500%'
                   OR title LIKE '%S&P500%' OR series_id LIKE '%SPY%'
                   OR series_id LIKE '%SP500%')
              AND frequency IN ('D', 'Daily', 'daily', 'd')
            LIMIT 10
        """
        candidates = pd.read_sql(search_query, conn)
        print("\n[INFO] Could not auto-detect SPX series. Found candidates:")
        print(candidates.to_string(index=False))
        print("\nUpdate SPX_SERIES_ID in config and re-run.")
        conn.close()
        return None, None, None, None

    spx_df['date'] = pd.to_datetime(spx_df['date'])
    spx_df = spx_df.set_index('date').sort_index()
    spx_df.columns = ['SPX']

    print(f"\n{'='*70}")
    print("DATA LOADED")
    print(f"{'='*70}")
    print(f"SPX series: {spx_id_used} ({len(spx_df)} obs, "
          f"{spx_df.index.min().date()} to {spx_df.index.max().date()})")
    print(f"Pillar indices: {len(pillars.columns)} loaded")
    for col in pillars.columns:
        valid = pillars[col].dropna()
        print(f"  {col:>8}: {len(valid):>5} obs, "
              f"{valid.index.min().date()} to {valid.index.max().date()}")
    print(f"Existing MRI: {len(mri_df)} obs")

    conn.close()
    return pillars, spx_df, mri_df, spx_id_used


# ============================================================
# Z-SCORE ENGINE (CLI Standard)
# ============================================================

def expanding_zscore(series, min_periods=Z_MIN_PERIODS, winsorize=Z_WINSORIZE):
    """
    Expanding-window z-score with winsorization.
    CLI standard: min 63 periods, ±3.0 clip.
    """
    mean = series.expanding(min_periods=min_periods).mean()
    std = series.expanding(min_periods=min_periods).std()
    z = (series - mean) / std.replace(0, np.nan)
    z = z.clip(-winsorize, winsorize)
    return z


def compute_pillar_zscores(pillars):
    """Compute expanding z-scores for each pillar index."""
    z_pillars = pd.DataFrame(index=pillars.index)
    for col in pillars.columns:
        z_pillars[col] = expanding_zscore(pillars[col])
    return z_pillars


# ============================================================
# FORWARD RETURNS
# ============================================================

def compute_forward_returns(spx, horizons=FWD_HORIZONS):
    """Compute forward log returns at multiple horizons."""
    fwd = pd.DataFrame(index=spx.index)
    for h in horizons:
        fwd[f'fwd_{h}d'] = np.log(spx['SPX'].shift(-h) / spx['SPX'])
    return fwd


def compute_forward_max_drawdown(spx, horizons=DD_HORIZONS):
    """Compute forward max drawdown over rolling windows."""
    dd = pd.DataFrame(index=spx.index)
    prices = spx['SPX'].values
    idx = spx.index

    for h in horizons:
        mdd = np.full(len(prices), np.nan)
        for i in range(len(prices) - h):
            window = prices[i:i+h+1]
            peak = np.maximum.accumulate(window)
            drawdowns = (window - peak) / peak
            mdd[i] = drawdowns.min()
        dd[f'mdd_{h}d'] = mdd

    dd.index = idx
    return dd


# ============================================================
# MRI COMPUTATION
# ============================================================

def compute_mri(z_pillars, weights_dict, components=MRI_COMPONENTS):
    """
    Compute MRI from z-scored pillars and a weight dictionary.
    weights_dict: {index_id: weight} (unsigned, signs from components config)
    """
    mri = pd.Series(0.0, index=z_pillars.index)
    for idx_id, config in components.items():
        if idx_id in z_pillars.columns and idx_id in weights_dict:
            mri += config['sign'] * weights_dict[idx_id] * z_pillars[idx_id]
    return mri


def weights_array_to_dict(w_array, component_names):
    """Convert optimization array to named dict."""
    return dict(zip(component_names, w_array))


# ============================================================
# QUINTILE SORT ENGINE (CLI Standard)
# ============================================================

def quintile_analysis(signal, forward_ret, n_quantiles=N_QUANTILES,
                      label="Signal"):
    """
    Full quintile sort analysis following CLI methodology.

    Returns dict with:
      - quintile_stats: mean, median, std, count, win_rate, t_stat per quintile
      - spread: Q5-Q1 mean return
      - spread_t: t-stat on Q5-Q1 spread
      - monotonic: True if strict or 3-quintile monotonicity holds
      - ic: rank IC (Spearman correlation)
    """
    # Align
    df = pd.DataFrame({'signal': signal, 'fwd': forward_ret}).dropna()
    if len(df) < n_quantiles * 20:
        return None

    # Assign quintiles (1 = lowest signal, 5 = highest)
    df['quintile'] = pd.qcut(df['signal'], n_quantiles, labels=False,
                             duplicates='drop') + 1

    results = {}
    q_stats = []

    for q in sorted(df['quintile'].unique()):
        grp = df[df['quintile'] == q]['fwd']
        q_mean = grp.mean()
        q_std = grp.std()
        q_count = len(grp)
        win_rate = (grp > 0).mean()

        # Slugging: avg win / abs(avg loss)
        wins = grp[grp > 0]
        losses = grp[grp < 0]
        if len(losses) > 0 and losses.mean() != 0:
            slugging = wins.mean() / abs(losses.mean()) if len(wins) > 0 else 0
        else:
            slugging = np.nan

        # T-stat vs zero
        if q_std > 0 and q_count > 1:
            t_stat = q_mean / (q_std / np.sqrt(q_count))
        else:
            t_stat = np.nan

        q_stats.append({
            'quintile': int(q),
            'mean_ret': q_mean,
            'median_ret': grp.median(),
            'std': q_std,
            'count': q_count,
            'win_rate': win_rate,
            'slugging': slugging,
            't_stat': t_stat,
        })

    q_df = pd.DataFrame(q_stats)
    results['quintile_stats'] = q_df

    # Spread: Q_max - Q_min (highest quintile minus lowest)
    q_max = q_df[q_df['quintile'] == q_df['quintile'].max()]['mean_ret'].values[0]
    q_min = q_df[q_df['quintile'] == q_df['quintile'].min()]['mean_ret'].values[0]
    results['spread'] = q_max - q_min

    # T-stat on spread (Welch's)
    g_high = df[df['quintile'] == df['quintile'].max()]['fwd']
    g_low = df[df['quintile'] == df['quintile'].min()]['fwd']
    t_spread, p_spread = stats.ttest_ind(g_high, g_low, equal_var=False)
    results['spread_t'] = t_spread
    results['spread_p'] = p_spread

    # Monotonicity checks
    means = q_df.sort_values('quintile')['mean_ret'].values
    strict_mono = all(means[i] <= means[i+1] for i in range(len(means)-1)) or \
                  all(means[i] >= means[i+1] for i in range(len(means)-1))
    # 3-quintile: Q1 vs Q3 vs Q5
    if len(means) >= 5:
        three_q = [means[0], means[2], means[4]]
        three_mono = (three_q[0] <= three_q[1] <= three_q[2]) or \
                     (three_q[0] >= three_q[1] >= three_q[2])
    else:
        three_mono = strict_mono

    results['strict_monotonic'] = strict_mono
    results['three_q_monotonic'] = three_mono

    # Rank IC (Spearman)
    ic, ic_p = stats.spearmanr(df['signal'], df['fwd'])
    results['ic'] = ic
    results['ic_p'] = ic_p

    return results


def print_quintile_table(results, horizon_label, label="MRI"):
    """Pretty-print quintile analysis results."""
    if results is None:
        print(f"  {horizon_label}: Insufficient data")
        return

    q_df = results['quintile_stats']
    print(f"\n  {label} → {horizon_label} Forward Returns")
    print(f"  {'Q':>3} {'Mean':>9} {'Median':>9} {'WinRate':>8} "
          f"{'Slug':>7} {'t-stat':>8} {'N':>6}")
    print(f"  {'-'*55}")

    for _, row in q_df.iterrows():
        print(f"  {int(row['quintile']):>3} {row['mean_ret']:>+9.4f} "
              f"{row['median_ret']:>+9.4f} {row['win_rate']:>7.1%} "
              f"{row['slugging']:>7.2f} {row['t_stat']:>+8.2f} "
              f"{int(row['count']):>6}")

    print(f"\n  Spread (Q{int(q_df['quintile'].max())}-Q{int(q_df['quintile'].min())}): "
          f"{results['spread']:>+.4f}  "
          f"t={results['spread_t']:>+.2f}  "
          f"p={results['spread_p']:.4f}")
    print(f"  Rank IC: {results['ic']:>+.4f}  "
          f"p={results['ic_p']:.4f}")
    print(f"  Monotonic: strict={results['strict_monotonic']}, "
          f"3-Q={results['three_q_monotonic']}")


# ============================================================
# OPTIMIZATION ENGINE
# ============================================================

def objective_function(w_array, z_pillars, fwd_returns, component_names,
                       components, horizon_col, objective='sortino'):
    """
    Objective to MINIMIZE. Negated for maximization targets.

    Objectives:
      'sortino': maximize Sortino ratio of Q5-Q1 quintile spread
      'spread': maximize Q5-Q1 spread
      'ic': maximize rank IC (Spearman)
      'neg_dd_q5': minimize max drawdown in top quintile (defensive)
    """
    # Normalize weights to sum to 1
    w = np.abs(w_array)
    w = w / w.sum()
    w_dict = weights_array_to_dict(w, component_names)

    mri = compute_mri(z_pillars, w_dict, components)

    df = pd.DataFrame({'mri': mri, 'fwd': fwd_returns[horizon_col]}).dropna()
    if len(df) < 250:
        return 1e6  # Penalty for insufficient data

    # MRI is a RISK index: higher = more risk = lower forward returns expected
    # So we want NEGATIVE rank IC (high MRI → low returns)
    # Or equivalently, Q1 (low risk) should have HIGHER returns than Q5

    try:
        df['quintile'] = pd.qcut(df['mri'], N_QUANTILES, labels=False,
                                 duplicates='drop') + 1
    except ValueError:
        return 1e6

    if objective == 'spread':
        # For MRI (risk index): Q1 returns MINUS Q5 returns (want positive)
        q1_ret = df[df['quintile'] == 1]['fwd'].mean()
        q5_ret = df[df['quintile'] == df['quintile'].max()]['fwd'].mean()
        spread = q1_ret - q5_ret  # Positive = low-risk outperforms
        return -spread  # Minimize negative = maximize spread

    elif objective == 'sortino':
        # Sortino of the Q1-Q5 spread series
        q1_rets = df[df['quintile'] == 1]['fwd']
        q5_rets = df[df['quintile'] == df['quintile'].max()]['fwd']
        # Use quintile-level means by period (approximate Sortino)
        spread_mean = q1_rets.mean() - q5_rets.mean()
        downside = q5_rets[q5_rets > 0].std()  # Q5 upside = spread downside
        if downside > 0:
            sortino = spread_mean / downside
        else:
            sortino = spread_mean * 100
        return -sortino

    elif objective == 'ic':
        # Negative rank IC (high MRI should predict low returns)
        ic, _ = stats.spearmanr(df['mri'], df['fwd'])
        return ic  # Want negative IC, so minimize ic (which is already negative)

    else:
        return 1e6


def optimize_weights(z_pillars, fwd_returns, components,
                     horizon_col=f'fwd_{OPT_PRIMARY_HORIZON}d',
                     objective=OPT_OBJECTIVE, n_restarts=25):
    """
    Optimize MRI weights using scipy.minimize with multiple random restarts.
    Constrained: weights sum to 1, each weight in [0.02, 0.30].
    """
    component_names = list(components.keys())
    n_weights = len(component_names)

    # Bounds: each weight between 2% and 30%
    bounds = [(0.02, 0.30)] * n_weights

    # Constraint: weights sum to 1
    constraints = [{'type': 'eq', 'fun': lambda w: np.sum(np.abs(w)) - 1.0}]

    best_result = None
    best_obj = 1e6

    # Current weights as one of the starting points
    current_w = np.array([components[c]['current_weight'] for c in component_names])

    starts = [current_w]
    rng = np.random.RandomState(42)
    for _ in range(n_restarts - 1):
        w = rng.dirichlet(np.ones(n_weights))
        w = np.clip(w, 0.02, 0.30)
        w = w / w.sum()
        starts.append(w)

    for i, w0 in enumerate(starts):
        try:
            result = minimize(
                objective_function,
                w0,
                args=(z_pillars, fwd_returns, component_names, components,
                      horizon_col, objective),
                method='SLSQP',
                bounds=bounds,
                constraints=constraints,
                options={'maxiter': 500, 'ftol': 1e-9}
            )
            if result.fun < best_obj:
                best_obj = result.fun
                best_result = result
        except Exception as e:
            continue

    if best_result is None:
        print("[WARN] Optimization failed on all restarts.")
        return None

    # Normalize final weights
    opt_w = np.abs(best_result.x)
    opt_w = opt_w / opt_w.sum()
    opt_dict = weights_array_to_dict(opt_w, component_names)

    return opt_dict, best_obj


# ============================================================
# WALK-FORWARD OOS VALIDATION
# ============================================================

def walk_forward_oos(z_pillars, fwd_returns, components,
                     horizon_col=f'fwd_{OPT_PRIMARY_HORIZON}d',
                     objective=OPT_OBJECTIVE,
                     n_splits=5, min_train_pct=0.50):
    """
    Expanding-window walk-forward test.
    Train on first N%, test on next chunk. Expand training window each split.
    """
    # Align data
    df = pd.DataFrame(index=z_pillars.index)
    for col in z_pillars.columns:
        df[col] = z_pillars[col]
    df[horizon_col] = fwd_returns[horizon_col]
    df = df.dropna()

    n = len(df)
    component_names = list(components.keys())
    results = []

    for split in range(n_splits):
        train_end_pct = min_train_pct + (1.0 - min_train_pct) * split / n_splits
        test_end_pct = min_train_pct + (1.0 - min_train_pct) * (split + 1) / n_splits

        train_end = int(n * train_end_pct)
        test_end = int(n * test_end_pct)

        if test_end <= train_end or test_end > n:
            continue

        z_train = df.iloc[:train_end][component_names]
        fwd_train = df.iloc[:train_end][[horizon_col]]

        z_test = df.iloc[train_end:test_end][component_names]
        fwd_test = df.iloc[train_end:test_end][[horizon_col]]

        if len(z_test) < 60:
            continue

        # Optimize on training set
        opt_dict, _ = optimize_weights(
            z_train, fwd_train, components,
            horizon_col=horizon_col, objective=objective,
            n_restarts=10
        )

        if opt_dict is None:
            continue

        # Evaluate on test set (OOS)
        mri_oos = compute_mri(z_test, opt_dict, components)
        qa = quintile_analysis(
            mri_oos, fwd_test[horizon_col],
            label=f"OOS Split {split+1}"
        )

        # Also evaluate current weights on same OOS period
        current_dict = {k: v['current_weight'] for k, v in components.items()}
        mri_current_oos = compute_mri(z_test, current_dict, components)
        qa_current = quintile_analysis(
            mri_current_oos, fwd_test[horizon_col],
            label=f"Current Split {split+1}"
        )

        results.append({
            'split': split + 1,
            'train_start': df.index[0].date(),
            'train_end': df.index[train_end-1].date(),
            'test_start': df.index[train_end].date(),
            'test_end': df.index[min(test_end-1, n-1)].date(),
            'test_n': len(z_test),
            'opt_weights': opt_dict,
            'oos_spread': qa['spread'] if qa else np.nan,
            'oos_ic': qa['ic'] if qa else np.nan,
            'oos_mono': qa['strict_monotonic'] if qa else False,
            'current_spread': qa_current['spread'] if qa_current else np.nan,
            'current_ic': qa_current['ic'] if qa_current else np.nan,
            'current_mono': qa_current['strict_monotonic'] if qa_current else False,
        })

    return results


# ============================================================
# REGIME ANALYSIS
# ============================================================

def regime_analysis(mri, fwd_returns, label="MRI"):
    """
    Tercile-based regime analysis.
    Classifies into Low Risk / Neutral / Elevated+.
    """
    df = pd.DataFrame({'mri': mri}).join(fwd_returns).dropna()

    df['regime'] = pd.qcut(df['mri'], 3, labels=['Low Risk', 'Neutral', 'Elevated'])

    print(f"\n  {label} Regime Analysis (Terciles)")
    print(f"  {'Regime':<12} {'N':>5} ", end="")
    for h in FWD_HORIZONS:
        col = f'fwd_{h}d'
        if col in df.columns:
            print(f"  {h}d", end="")
            print(f"{'':>5}", end="")
    print()
    print(f"  {'-'*70}")

    for regime in ['Low Risk', 'Neutral', 'Elevated']:
        grp = df[df['regime'] == regime]
        print(f"  {regime:<12} {len(grp):>5} ", end="")
        for h in FWD_HORIZONS:
            col = f'fwd_{h}d'
            if col in df.columns:
                mean_ret = grp[col].mean()
                print(f"  {mean_ret:>+.4f}  ", end="")
        print()


# ============================================================
# YEAR-BY-YEAR STABILITY
# ============================================================

def year_by_year_ic(mri, fwd_returns, horizon_col):
    """Annual rank IC stability check."""
    df = pd.DataFrame({'mri': mri, 'fwd': fwd_returns[horizon_col]}).dropna()
    df['year'] = df.index.year

    print(f"\n  Year-by-Year Rank IC ({horizon_col})")
    print(f"  {'Year':>6} {'IC':>8} {'p-val':>8} {'N':>6}")
    print(f"  {'-'*32}")

    for year in sorted(df['year'].unique()):
        grp = df[df['year'] == year]
        if len(grp) < 30:
            continue
        ic, p = stats.spearmanr(grp['mri'], grp['fwd'])
        print(f"  {year:>6} {ic:>+8.4f} {p:>8.4f} {len(grp):>6}")


# ============================================================
# COMPARISON: CURRENT vs OPTIMIZED
# ============================================================

def compare_weights(current_dict, opt_dict, components):
    """Side-by-side weight comparison."""
    print(f"\n{'='*70}")
    print("WEIGHT COMPARISON: Current (Judgment) vs Optimized")
    print(f"{'='*70}")
    print(f"  {'Pillar':>8} {'Sign':>5} {'Current':>9} {'Optimized':>10} {'Delta':>8}")
    print(f"  {'-'*45}")

    for idx_id in components:
        c_w = current_dict.get(idx_id, 0)
        o_w = opt_dict.get(idx_id, 0)
        sign = '+' if components[idx_id]['sign'] > 0 else '-'
        delta = o_w - c_w
        marker = ' **' if abs(delta) > 0.03 else ''
        print(f"  {idx_id:>8} {sign:>5} {c_w:>9.3f} {o_w:>10.3f} "
              f"{delta:>+8.3f}{marker}")

    print(f"\n  Sum:            {sum(current_dict.values()):>9.3f} "
          f"{sum(opt_dict.values()):>10.3f}")
    print(f"\n  ** = delta > 3pp (material shift)")


# ============================================================
# MAIN
# ============================================================

def main():
    print("="*70)
    print("MRI WEIGHT OPTIMIZATION — LIGHTHOUSE MACRO")
    print(f"Run Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("="*70)

    # --- Load Data ---
    data = load_data(DB_PATH)
    if data[0] is None:
        return

    pillars, spx, mri_existing, spx_id = data

    # --- Compute z-scores ---
    print(f"\nComputing expanding z-scores (min_periods={Z_MIN_PERIODS}, "
          f"winsorize=±{Z_WINSORIZE})...")
    z_pillars = compute_pillar_zscores(pillars)

    # --- Compute forward returns ---
    print("Computing forward returns...")
    fwd_returns = compute_forward_returns(spx)
    fwd_dd = compute_forward_max_drawdown(spx)

    # --- Align all data ---
    combined = z_pillars.join(fwd_returns, how='inner').join(fwd_dd, how='inner')
    z_aligned = combined[list(MRI_COMPONENTS.keys())]
    fwd_aligned = combined[[f'fwd_{h}d' for h in FWD_HORIZONS if f'fwd_{h}d' in combined.columns]]
    dd_aligned = combined[[f'mdd_{h}d' for h in DD_HORIZONS if f'mdd_{h}d' in combined.columns]]

    valid_mask = z_aligned.notna().all(axis=1) & fwd_aligned.iloc[:, 0].notna()
    z_valid = z_aligned[valid_mask]
    fwd_valid = fwd_aligned[valid_mask]
    dd_valid = dd_aligned[valid_mask]

    print(f"\nAligned dataset: {len(z_valid)} observations "
          f"({z_valid.index.min().date()} to {z_valid.index.max().date()})")

    if len(z_valid) < 500:
        print("[ERROR] Insufficient aligned data. Check index date ranges.")
        return

    # ============================================================
    # PHASE 1: EVALUATE CURRENT WEIGHTS
    # ============================================================

    print(f"\n{'='*70}")
    print("PHASE 1: CURRENT WEIGHTS BASELINE")
    print(f"{'='*70}")

    current_dict = {k: v['current_weight'] for k, v in MRI_COMPONENTS.items()}
    mri_current = compute_mri(z_valid, current_dict, MRI_COMPONENTS)

    # Note: MRI is a RISK index. Higher MRI = higher risk = expected LOWER fwd returns.
    # So for quintile sorts: Q1 (low risk) should have highest returns.
    # The signal we pass to quintile_analysis is MRI, and we expect NEGATIVE IC.

    print("\nQuintile Sorts (Current Weights):")
    print("  NOTE: MRI is a RISK index. Q1=Low Risk, Q5=High Risk.")
    print("  Expect: Q1 returns > Q5 returns (negative rank IC).")

    current_results = {}
    for h in FWD_HORIZONS:
        col = f'fwd_{h}d'
        if col in fwd_valid.columns:
            qa = quintile_analysis(mri_current, fwd_valid[col])
            current_results[col] = qa
            print_quintile_table(qa, f"{h}d", label="Current MRI")

    # Regime analysis
    regime_analysis(mri_current, fwd_valid, label="Current MRI")

    # Year-by-year IC
    primary_col = f'fwd_{OPT_PRIMARY_HORIZON}d'
    year_by_year_ic(mri_current, fwd_valid, primary_col)

    # ============================================================
    # PHASE 2: OPTIMIZE WEIGHTS
    # ============================================================

    print(f"\n{'='*70}")
    print(f"PHASE 2: WEIGHT OPTIMIZATION (horizon={OPT_PRIMARY_HORIZON}d, "
          f"objective={OPT_OBJECTIVE})")
    print(f"{'='*70}")

    # Split: in-sample (first 90%) and holdout (last 10%)
    n_is = int(len(z_valid) * (1 - OOS_FRACTION))
    z_is = z_valid.iloc[:n_is]
    fwd_is = fwd_valid.iloc[:n_is]
    z_oos = z_valid.iloc[n_is:]
    fwd_oos = fwd_valid.iloc[n_is:]

    print(f"\nIn-sample:  {len(z_is)} obs "
          f"({z_is.index.min().date()} to {z_is.index.max().date()})")
    print(f"Out-of-sample: {len(z_oos)} obs "
          f"({z_oos.index.min().date()} to {z_oos.index.max().date()})")

    # Optimize on in-sample
    print(f"\nOptimizing ({OPT_OBJECTIVE}, {primary_col})...")
    opt_result = optimize_weights(
        z_is, fwd_is, MRI_COMPONENTS,
        horizon_col=primary_col, objective=OPT_OBJECTIVE,
        n_restarts=30
    )

    if opt_result is None:
        print("[ERROR] Optimization failed.")
        return

    opt_dict, best_obj = opt_result
    print(f"Best objective value: {best_obj:.6f}")

    # Compare weights
    compare_weights(current_dict, opt_dict, MRI_COMPONENTS)

    # ============================================================
    # PHASE 3: IN-SAMPLE EVALUATION (OPTIMIZED)
    # ============================================================

    print(f"\n{'='*70}")
    print("PHASE 3: IN-SAMPLE EVALUATION (OPTIMIZED WEIGHTS)")
    print(f"{'='*70}")

    mri_opt_is = compute_mri(z_is, opt_dict, MRI_COMPONENTS)

    print("\nQuintile Sorts (Optimized, In-Sample):")
    opt_is_results = {}
    for h in FWD_HORIZONS:
        col = f'fwd_{h}d'
        if col in fwd_is.columns:
            qa = quintile_analysis(mri_opt_is, fwd_is[col])
            opt_is_results[col] = qa
            print_quintile_table(qa, f"{h}d", label="Opt MRI (IS)")

    # ============================================================
    # PHASE 4: OUT-OF-SAMPLE EVALUATION
    # ============================================================

    print(f"\n{'='*70}")
    print("PHASE 4: OUT-OF-SAMPLE EVALUATION")
    print(f"{'='*70}")

    if len(z_oos) < 60:
        print("[WARN] OOS sample too small for reliable quintile sorts.")
        print("       Using full-period tercile analysis instead.")
        mri_opt_oos = compute_mri(z_oos, opt_dict, MRI_COMPONENTS)
        mri_cur_oos = compute_mri(z_oos, current_dict, MRI_COMPONENTS)

        for label, mri_series in [("Optimized", mri_opt_oos),
                                   ("Current", mri_cur_oos)]:
            df_oos = pd.DataFrame({'mri': mri_series}).join(fwd_oos).dropna()
            ic, p = stats.spearmanr(df_oos['mri'], df_oos[primary_col])
            print(f"\n  {label} OOS Rank IC ({primary_col}): {ic:>+.4f} (p={p:.4f})")
    else:
        mri_opt_oos = compute_mri(z_oos, opt_dict, MRI_COMPONENTS)
        mri_cur_oos = compute_mri(z_oos, current_dict, MRI_COMPONENTS)

        print("\nOptimized Weights (OOS):")
        for h in FWD_HORIZONS:
            col = f'fwd_{h}d'
            if col in fwd_oos.columns:
                qa = quintile_analysis(mri_opt_oos, fwd_oos[col])
                print_quintile_table(qa, f"{h}d", label="Opt MRI (OOS)")

        print("\nCurrent Weights (OOS) for comparison:")
        for h in [OPT_PRIMARY_HORIZON]:
            col = f'fwd_{h}d'
            if col in fwd_oos.columns:
                qa = quintile_analysis(mri_cur_oos, fwd_oos[col])
                print_quintile_table(qa, f"{h}d", label="Current MRI (OOS)")

    # ============================================================
    # PHASE 5: WALK-FORWARD VALIDATION
    # ============================================================

    print(f"\n{'='*70}")
    print("PHASE 5: WALK-FORWARD VALIDATION (5 Expanding Splits)")
    print(f"{'='*70}")

    wf_results = walk_forward_oos(
        z_valid, fwd_valid, MRI_COMPONENTS,
        horizon_col=primary_col, objective=OPT_OBJECTIVE,
        n_splits=5
    )

    if wf_results:
        print(f"\n  {'Split':>5} {'Test Period':>25} {'N':>5} "
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

        # Summary
        opt_spreads = [r['oos_spread'] for r in wf_results if not np.isnan(r['oos_spread'])]
        cur_spreads = [r['current_spread'] for r in wf_results if not np.isnan(r['current_spread'])]
        opt_ics = [r['oos_ic'] for r in wf_results if not np.isnan(r['oos_ic'])]
        cur_ics = [r['current_ic'] for r in wf_results if not np.isnan(r['current_ic'])]

        print(f"\n  Walk-Forward Summary:")
        print(f"  Avg OOS Spread:  Optimized={np.mean(opt_spreads):>+.4f}  "
              f"Current={np.mean(cur_spreads):>+.4f}")
        print(f"  Avg OOS IC:      Optimized={np.mean(opt_ics):>+.4f}  "
              f"Current={np.mean(cur_ics):>+.4f}")

        # Weight stability across splits
        print(f"\n  Weight Stability Across Splits:")
        component_names = list(MRI_COMPONENTS.keys())
        weight_matrix = []
        for r in wf_results:
            if r['opt_weights']:
                weight_matrix.append([r['opt_weights'].get(c, 0)
                                      for c in component_names])

        if weight_matrix:
            wm = np.array(weight_matrix)
            print(f"  {'Pillar':>8} {'Mean':>8} {'Std':>8} {'Min':>8} {'Max':>8}")
            print(f"  {'-'*40}")
            for i, c in enumerate(component_names):
                print(f"  {c:>8} {wm[:, i].mean():>8.3f} {wm[:, i].std():>8.3f} "
                      f"{wm[:, i].min():>8.3f} {wm[:, i].max():>8.3f}")

    # ============================================================
    # PHASE 6: MULTI-HORIZON ROBUSTNESS
    # ============================================================

    print(f"\n{'='*70}")
    print("PHASE 6: MULTI-HORIZON ROBUSTNESS (Full-Period, Optimized Weights)")
    print(f"{'='*70}")

    mri_opt_full = compute_mri(z_valid, opt_dict, MRI_COMPONENTS)
    mri_cur_full = compute_mri(z_valid, current_dict, MRI_COMPONENTS)

    print(f"\n  {'Horizon':>8} {'Opt Spread':>11} {'Cur Spread':>11} "
          f"{'Opt IC':>8} {'Cur IC':>8} "
          f"{'Opt Mono':>9} {'Cur Mono':>9}")
    print(f"  {'-'*70}")

    for h in FWD_HORIZONS:
        col = f'fwd_{h}d'
        if col not in fwd_valid.columns:
            continue
        qa_opt = quintile_analysis(mri_opt_full, fwd_valid[col])
        qa_cur = quintile_analysis(mri_cur_full, fwd_valid[col])

        if qa_opt and qa_cur:
            print(f"  {h:>6}d "
                  f"{qa_opt['spread']:>+11.4f} {qa_cur['spread']:>+11.4f} "
                  f"{qa_opt['ic']:>+8.4f} {qa_cur['ic']:>+8.4f} "
                  f"{'Y' if qa_opt['strict_monotonic'] else 'N':>9} "
                  f"{'Y' if qa_cur['strict_monotonic'] else 'N':>9}")

    # ============================================================
    # PHASE 7: DRAWDOWN ANALYSIS
    # ============================================================

    print(f"\n{'='*70}")
    print("PHASE 7: DRAWDOWN ANALYSIS BY REGIME")
    print(f"{'='*70}")

    for label, mri_series in [("Optimized", mri_opt_full),
                               ("Current", mri_cur_full)]:
        df_dd = pd.DataFrame({'mri': mri_series}).join(dd_aligned).dropna()
        df_dd['regime'] = pd.qcut(df_dd['mri'], 3,
                                   labels=['Low Risk', 'Neutral', 'Elevated'])

        print(f"\n  {label} Weights — Avg Forward Max Drawdown by Regime:")
        print(f"  {'Regime':<12}", end="")
        for h in DD_HORIZONS:
            col = f'mdd_{h}d'
            if col in df_dd.columns:
                print(f"  {h}d MDD   ", end="")
        print(f"  {'N':>5}")
        print(f"  {'-'*55}")

        for regime in ['Low Risk', 'Neutral', 'Elevated']:
            grp = df_dd[df_dd['regime'] == regime]
            print(f"  {regime:<12}", end="")
            for h in DD_HORIZONS:
                col = f'mdd_{h}d'
                if col in grp.columns:
                    print(f"  {grp[col].mean():>+.4f}  ", end="")
            print(f"  {len(grp):>5}")

    # ============================================================
    # OUTPUT
    # ============================================================

    print(f"\n{'='*70}")
    print("FINAL OUTPUT")
    print(f"{'='*70}")

    print("\nOptimized MRI Weights:")
    print("```python")
    print("MRI_OPTIMIZED_WEIGHTS = {")
    for idx_id in MRI_COMPONENTS:
        sign_str = '-' if MRI_COMPONENTS[idx_id]['sign'] < 0 else '+'
        print(f"    '{idx_id}': {opt_dict[idx_id]:.4f},  "
              f"# ({sign_str}) current={current_dict[idx_id]:.2f}")
    print("}")
    print("```")

    print("\nOptimized MRI Formula:")
    terms = []
    for idx_id in MRI_COMPONENTS:
        sign = MRI_COMPONENTS[idx_id]['sign']
        w = opt_dict[idx_id]
        sign_str = '+' if sign > 0 else '-'
        neg = '(-' if sign < 0 else ''
        close = ')' if sign < 0 else ''
        terms.append(f"{w:.3f}*{neg}{idx_id}{close}")
    print(f"MRI_opt = {' + '.join(terms)}")

    # Save results
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output = {
        'run_date': datetime.now().isoformat(),
        'optimization_horizon': f'{OPT_PRIMARY_HORIZON}d',
        'objective': OPT_OBJECTIVE,
        'n_observations': len(z_valid),
        'date_range': f"{z_valid.index.min().date()} to {z_valid.index.max().date()}",
        'current_weights': current_dict,
        'optimized_weights': opt_dict,
        'spx_series': spx_id,
    }

    output_path = os.path.join(OUTPUT_DIR, 'mri_optimization_results.json')
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to: {output_path}")


if __name__ == '__main__':
    main()
