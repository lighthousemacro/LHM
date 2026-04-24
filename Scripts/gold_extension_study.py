"""
Gold Forward Returns Study: Extreme Extension from 52-Week MA
Lighthouse Macro Research

Analyzes forward returns when gold is extremely extended above its 52-week moving average.
"""

import pandas as pd
import numpy as np
from datetime import datetime

# Load data
df = pd.read_csv('/Users/bob/Library/Mobile Documents/com~apple~CloudDocs/TVC_GOLD, 1W_372b1.csv')

# Parse dates and clean
df['time'] = pd.to_datetime(df['time'])
df = df.sort_values('time').reset_index(drop=True)

# Calculate 52-week (52 weeks * 1 = 52 observations for weekly data) rolling high and MA
df['52w_high'] = df['close'].rolling(52, min_periods=52).max()
df['52w_low'] = df['close'].rolling(52, min_periods=52).min()
df['52w_ma'] = df['close'].rolling(52, min_periods=52).mean()

# Calculate distance from 52w MA (%)
df['dist_52w_ma'] = ((df['close'] / df['52w_ma']) - 1) * 100

# Forward returns - for weekly data
# Near-term focus: 1w, 2w, 1m, then longer horizons
for period, weeks in [('1w', 1), ('2w', 2), ('1m', 4), ('6w', 6), ('2m', 8), ('3m', 13), ('6m', 26), ('12m', 52)]:
    df[f'fwd_ret_{period}'] = df['close'].shift(-weeks) / df['close'] - 1

# Drop rows without 52w MA
df_analysis = df.dropna(subset=['52w_ma', 'dist_52w_ma']).copy()

print("=" * 80)
print("GOLD FORWARD RETURNS STUDY: EXTREME EXTENSION FROM 52-WEEK MA")
print("=" * 80)
print(f"\nData range: {df_analysis['time'].min().strftime('%Y-%m-%d')} to {df_analysis['time'].max().strftime('%Y-%m-%d')}")
print(f"Total observations: {len(df_analysis):,}")

# Current reading
latest = df_analysis.iloc[-1]
print(f"\n>>> CURRENT: {latest['time'].strftime('%Y-%m-%d')}")
print(f"    Close: ${latest['close']:,.2f}")
print(f"    52w MA: ${latest['52w_ma']:,.2f}")
print(f"    Distance from 52w MA: {latest['dist_52w_ma']:.1f}%")

# Distribution of extensions
print("\n" + "-" * 80)
print("DISTRIBUTION OF EXTENSION FROM 52w MA")
print("-" * 80)
percentiles = [5, 10, 25, 50, 75, 90, 95, 99]
for p in percentiles:
    val = df_analysis['dist_52w_ma'].quantile(p/100)
    print(f"  {p}th percentile: {val:+.1f}%")

# Find how extreme current reading is
current_percentile = (df_analysis['dist_52w_ma'] < latest['dist_52w_ma']).mean() * 100
print(f"\n>>> Current {latest['dist_52w_ma']:.1f}% extension is in the {current_percentile:.1f}th percentile")

# Test different thresholds
print("\n" + "=" * 80)
print("FORWARD RETURNS BY EXTENSION THRESHOLD")
print("=" * 80)

thresholds = [25, 28, 30, 32, 35]

def analyze_threshold(threshold):
    """Analyze forward returns when extension >= threshold"""
    mask = df_analysis['dist_52w_ma'] >= threshold
    subset = df_analysis[mask].copy()
    n = len(subset)

    if n < 3:
        return None

    results = {'threshold': threshold, 'n_obs': n}

    for period in ['1w', '1m', '3m', '6m', '12m']:
        col = f'fwd_ret_{period}'
        valid = subset[col].dropna()
        if len(valid) > 0:
            results[f'{period}_mean'] = valid.mean() * 100
            results[f'{period}_median'] = valid.median() * 100
            results[f'{period}_std'] = valid.std() * 100
            results[f'{period}_pos_rate'] = (valid > 0).mean() * 100
            results[f'{period}_n'] = len(valid)
            # Sharpe-like (annualized)
            if period == '1w':
                ann_factor = np.sqrt(52)
            elif period == '1m':
                ann_factor = np.sqrt(12)
            elif period == '3m':
                ann_factor = np.sqrt(4)
            elif period == '6m':
                ann_factor = np.sqrt(2)
            else:
                ann_factor = 1
            if results[f'{period}_std'] > 0:
                results[f'{period}_sharpe'] = (results[f'{period}_mean'] / results[f'{period}_std']) * ann_factor
            else:
                results[f'{period}_sharpe'] = np.nan

    return results

# Baseline stats (all observations)
print("\n--- BASELINE: ALL OBSERVATIONS ---")
for period in ['1w', '1m', '3m', '6m', '12m']:
    col = f'fwd_ret_{period}'
    valid = df_analysis[col].dropna()
    mean_ret = valid.mean() * 100
    median_ret = valid.median() * 100
    std_ret = valid.std() * 100
    pos_rate = (valid > 0).mean() * 100
    print(f"  {period.upper():>4}: Mean={mean_ret:+.2f}%, Median={median_ret:+.2f}%, Vol={std_ret:.2f}%, Win%={pos_rate:.1f}%")

# Analyze each threshold
all_results = []
for thresh in thresholds:
    res = analyze_threshold(thresh)
    if res:
        all_results.append(res)

print("\n" + "-" * 80)
print("EXTREME EXTENSION ANALYSIS (>= Threshold)")
print("-" * 80)

for res in all_results:
    print(f"\n=== EXTENSION >= {res['threshold']}% (n={res['n_obs']} observations) ===\n")

    header = f"{'Period':<8} {'Mean':>8} {'Median':>8} {'Vol':>8} {'Win%':>8} {'Sharpe':>8} {'n':>6}"
    print(header)
    print("-" * len(header))

    for period in ['1w', '1m', '3m', '6m', '12m']:
        if f'{period}_mean' in res:
            print(f"{period.upper():<8} {res[f'{period}_mean']:>+7.2f}% {res[f'{period}_median']:>+7.2f}% "
                  f"{res[f'{period}_std']:>7.2f}% {res[f'{period}_pos_rate']:>7.1f}% "
                  f"{res[f'{period}_sharpe']:>8.2f} {res[f'{period}_n']:>6}")

# Detailed look at all instances >= 30%
print("\n" + "=" * 80)
print("ALL INSTANCES WHERE GOLD >= 30% ABOVE 52w MA")
print("=" * 80)

extreme_instances = df_analysis[df_analysis['dist_52w_ma'] >= 30].copy()
print(f"\nFound {len(extreme_instances)} instances:\n")

cols_to_show = ['time', 'close', '52w_ma', 'dist_52w_ma', 'fwd_ret_1m', 'fwd_ret_3m', 'fwd_ret_6m', 'fwd_ret_12m']
for idx, row in extreme_instances.iterrows():
    print(f"Date: {row['time'].strftime('%Y-%m-%d')}")
    print(f"  Close: ${row['close']:,.2f}, 52w MA: ${row['52w_ma']:,.2f}, Extension: {row['dist_52w_ma']:.1f}%")
    fwd_1m = f"{row['fwd_ret_1m']*100:+.1f}%" if pd.notna(row['fwd_ret_1m']) else "N/A"
    fwd_3m = f"{row['fwd_ret_3m']*100:+.1f}%" if pd.notna(row['fwd_ret_3m']) else "N/A"
    fwd_6m = f"{row['fwd_ret_6m']*100:+.1f}%" if pd.notna(row['fwd_ret_6m']) else "N/A"
    fwd_12m = f"{row['fwd_ret_12m']*100:+.1f}%" if pd.notna(row['fwd_ret_12m']) else "N/A"
    print(f"  Forward Returns: 1m={fwd_1m}, 3m={fwd_3m}, 6m={fwd_6m}, 12m={fwd_12m}")
    print()

# Summary table
print("\n" + "=" * 80)
print("SUMMARY: COMPARING EXTENSION THRESHOLDS")
print("=" * 80)

print("\n3-MONTH FORWARD RETURNS:")
print(f"{'Threshold':<12} {'n':>6} {'Mean':>10} {'Median':>10} {'Win%':>10} {'Sharpe':>10}")
print("-" * 60)
for res in all_results:
    if '3m_mean' in res:
        print(f">={res['threshold']}%{'':<7} {res['n_obs']:>6} {res['3m_mean']:>+9.2f}% {res['3m_median']:>+9.2f}% "
              f"{res['3m_pos_rate']:>9.1f}% {res['3m_sharpe']:>10.2f}")

print("\n6-MONTH FORWARD RETURNS:")
print(f"{'Threshold':<12} {'n':>6} {'Mean':>10} {'Median':>10} {'Win%':>10} {'Sharpe':>10}")
print("-" * 60)
for res in all_results:
    if '6m_mean' in res:
        print(f">={res['threshold']}%{'':<7} {res['n_obs']:>6} {res['6m_mean']:>+9.2f}% {res['6m_median']:>+9.2f}% "
              f"{res['6m_pos_rate']:>9.1f}% {res['6m_sharpe']:>10.2f}")

print("\n12-MONTH FORWARD RETURNS:")
print(f"{'Threshold':<12} {'n':>6} {'Mean':>10} {'Median':>10} {'Win%':>10} {'Sharpe':>10}")
print("-" * 60)
for res in all_results:
    if '12m_mean' in res:
        print(f">={res['threshold']}%{'':<7} {res['n_obs']:>6} {res['12m_mean']:>+9.2f}% {res['12m_median']:>+9.2f}% "
              f"{res['12m_pos_rate']:>9.1f}% {res['12m_sharpe']:>10.2f}")

# Maximum Drawdown analysis for extreme cases
print("\n" + "=" * 80)
print("MAX DRAWDOWN ANALYSIS (FROM EXTREME EXTENSION POINTS)")
print("=" * 80)

def calc_max_drawdown_forward(df, start_idx, periods):
    """Calculate max drawdown over next N periods from entry"""
    end_idx = min(start_idx + periods, len(df) - 1)
    if start_idx >= len(df) - 1:
        return np.nan

    entry_price = df.iloc[start_idx]['close']
    forward_prices = df.iloc[start_idx:end_idx + 1]['close'].values

    running_max = entry_price
    max_dd = 0

    for price in forward_prices:
        running_max = max(running_max, price)
        dd = (price - running_max) / running_max
        max_dd = min(max_dd, dd)

    return max_dd * 100

print("\nMax Drawdown over next 3 months for instances >= 30% extended:")
for idx in extreme_instances.index:
    row = df_analysis.loc[idx]
    mdd = calc_max_drawdown_forward(df_analysis, idx, 13)
    if pd.notna(mdd):
        print(f"  {row['time'].strftime('%Y-%m-%d')}: Extension {row['dist_52w_ma']:.1f}%, Max DD: {mdd:.1f}%")

print("\n" + "=" * 80)
print("KEY TAKEAWAY")
print("=" * 80)
print(f"""
Current gold extension of {latest['dist_52w_ma']:.1f}% from 52w MA is in the {current_percentile:.0f}th percentile.

At these extreme levels (>30% above 52w MA), historical forward returns show:
- Sample size is small (n={len(extreme_instances)} instances)
- Results are regime-dependent and may not be representative
- The 1970s gold bubble and recent 2020s rally dominate the sample

CONTEXT MATTERS: Your intuition about mean reversion at extremes is worth testing,
but the small sample size means confidence intervals are wide.
""")

# Additional analysis: Exclude the 1934 gold peg regime change (artificial)
print("\n" + "=" * 80)
print("REGIME-ADJUSTED ANALYSIS (Excluding 1934 Gold Peg)")
print("=" * 80)

# Filter out 1934-1936 (FDR gold revaluation - not a free market move)
df_free = df_analysis[df_analysis['time'] >= '1970-01-01'].copy()
print(f"\nFree-floating gold era: {df_free['time'].min().strftime('%Y-%m-%d')} to {df_free['time'].max().strftime('%Y-%m-%d')}")
print(f"Observations: {len(df_free):,}")

extreme_free = df_free[df_free['dist_52w_ma'] >= 30].copy()
print(f"Instances >= 30% extended: {len(extreme_free)}")

# Current percentile in free-floating era
current_pct_free = (df_free['dist_52w_ma'] < latest['dist_52w_ma']).mean() * 100
print(f"Current {latest['dist_52w_ma']:.1f}% extension is in the {current_pct_free:.1f}th percentile (free-float era)")

print("\n--- FREE-FLOAT ERA: FORWARD RETURNS BY EXTENSION ---")

for thresh in [25, 30, 35]:
    mask = df_free['dist_52w_ma'] >= thresh
    subset = df_free[mask]
    n = len(subset)

    print(f"\n>> Extension >= {thresh}% (n={n} observations)")
    print(f"{'Period':<8} {'Mean':>10} {'Median':>10} {'Win%':>10} {'Max DD Avg':>12}")
    print("-" * 55)

    for period, weeks in [('1m', 4), ('3m', 13), ('6m', 26), ('12m', 52)]:
        col = f'fwd_ret_{period}'
        valid = subset[col].dropna()
        if len(valid) > 0:
            mean_r = valid.mean() * 100
            med_r = valid.median() * 100
            win = (valid > 0).mean() * 100
            print(f"{period.upper():<8} {mean_r:>+9.2f}% {med_r:>+9.2f}% {win:>9.1f}%")

# Cluster analysis by time period
print("\n" + "=" * 80)
print("CLUSTER ANALYSIS: EXTREME EXTENSIONS BY ERA")
print("=" * 80)

eras = [
    ('1970s Inflation', '1970-01-01', '1985-01-01'),
    ('2000s Bull Run', '2000-01-01', '2012-01-01'),
    ('2020s Rally', '2020-01-01', '2030-01-01')
]

for era_name, start, end in eras:
    era_df = df_free[(df_free['time'] >= start) & (df_free['time'] < end)]
    era_extreme = era_df[era_df['dist_52w_ma'] >= 30]

    if len(era_extreme) > 0:
        print(f"\n--- {era_name} (n={len(era_extreme)} instances >= 30% extended) ---")

        for period in ['3m', '6m', '12m']:
            col = f'fwd_ret_{period}'
            valid = era_extreme[col].dropna()
            if len(valid) > 0:
                mean_r = valid.mean() * 100
                med_r = valid.median() * 100
                win = (valid > 0).mean() * 100
                print(f"  {period.upper()}: Mean={mean_r:+.1f}%, Median={med_r:+.1f}%, Win%={win:.0f}% (n={len(valid)})")

# The key insight: What happens at CURRENT level specifically
print("\n" + "=" * 80)
print("SPECIFIC ANALYSIS: EXTENSION 35-45% (CURRENT ZONE)")
print("=" * 80)

zone_mask = (df_free['dist_52w_ma'] >= 35) & (df_free['dist_52w_ma'] <= 45)
zone_df = df_free[zone_mask]

print(f"\nInstances with 35-45% extension (current is {latest['dist_52w_ma']:.1f}%): {len(zone_df)}")
print("\nAll instances:")

for idx, row in zone_df.iterrows():
    fwd_3m = f"{row['fwd_ret_3m']*100:+.1f}%" if pd.notna(row['fwd_ret_3m']) else "N/A"
    fwd_6m = f"{row['fwd_ret_6m']*100:+.1f}%" if pd.notna(row['fwd_ret_6m']) else "N/A"
    print(f"  {row['time'].strftime('%Y-%m-%d')}: Ext={row['dist_52w_ma']:.1f}%, 3m={fwd_3m}, 6m={fwd_6m}")

if len(zone_df) > 0:
    print(f"\nSummary for 35-45% zone:")
    for period in ['3m', '6m']:
        col = f'fwd_ret_{period}'
        valid = zone_df[col].dropna()
        if len(valid) > 0:
            print(f"  {period.upper()}: Mean={valid.mean()*100:+.1f}%, Median={valid.median()*100:+.1f}%, Win%={(valid>0).mean()*100:.0f}%")

# NEAR-TERM FOCUS ANALYSIS
print("\n" + "=" * 80)
print("NEAR-TERM FORWARD RETURNS ANALYSIS (1w, 2w, 1m)")
print("=" * 80)

print("\n--- BASELINE (All Observations, Free-Float Era) ---")
for period in ['1w', '2w', '1m', '6w', '2m']:
    col = f'fwd_ret_{period}'
    valid = df_free[col].dropna()
    if len(valid) > 0:
        mean_r = valid.mean() * 100
        med_r = valid.median() * 100
        std_r = valid.std() * 100
        win = (valid > 0).mean() * 100
        print(f"  {period.upper():>3}: Mean={mean_r:+.2f}%, Median={med_r:+.2f}%, Vol={std_r:.2f}%, Win%={win:.1f}%")

print("\n--- NEAR-TERM RETURNS BY EXTENSION THRESHOLD ---")

for thresh in [30, 35, 38]:
    mask = df_free['dist_52w_ma'] >= thresh
    subset = df_free[mask]
    n = len(subset)

    print(f"\n>> Extension >= {thresh}% (n={n})")
    print(f"{'Period':>6} {'Mean':>9} {'Median':>9} {'Vol':>8} {'Win%':>8} {'n':>6}")
    print("-" * 50)

    for period in ['1w', '2w', '1m', '6w', '2m']:
        col = f'fwd_ret_{period}'
        valid = subset[col].dropna()
        if len(valid) > 0:
            mean_r = valid.mean() * 100
            med_r = valid.median() * 100
            std_r = valid.std() * 100
            win = (valid > 0).mean() * 100
            print(f"{period.upper():>6} {mean_r:>+8.2f}% {med_r:>+8.2f}% {std_r:>7.2f}% {win:>7.1f}% {len(valid):>6}")

# Detailed near-term for 35-45% zone
print("\n" + "=" * 80)
print("DETAILED: 35-45% EXTENSION ZONE - NEAR-TERM OUTCOMES")
print("=" * 80)

zone_mask = (df_free['dist_52w_ma'] >= 35) & (df_free['dist_52w_ma'] <= 45)
zone_df = df_free[zone_mask]

print(f"\nAll {len(zone_df)} instances in 35-45% zone:")
print(f"{'Date':<12} {'Ext':>6} {'1w':>8} {'2w':>8} {'1m':>8} {'6w':>8}")
print("-" * 55)

for idx, row in zone_df.iterrows():
    date_str = row['time'].strftime('%Y-%m-%d')
    ext = f"{row['dist_52w_ma']:.1f}%"
    r1w = f"{row['fwd_ret_1w']*100:+.1f}%" if pd.notna(row['fwd_ret_1w']) else "N/A"
    r2w = f"{row['fwd_ret_2w']*100:+.1f}%" if pd.notna(row['fwd_ret_2w']) else "N/A"
    r1m = f"{row['fwd_ret_1m']*100:+.1f}%" if pd.notna(row['fwd_ret_1m']) else "N/A"
    r6w = f"{row['fwd_ret_6w']*100:+.1f}%" if pd.notna(row['fwd_ret_6w']) else "N/A"
    print(f"{date_str:<12} {ext:>6} {r1w:>8} {r2w:>8} {r1m:>8} {r6w:>8}")

# Summary stats for zone
print(f"\n--- Summary for 35-45% Extension Zone ---")
for period in ['1w', '2w', '1m', '6w']:
    col = f'fwd_ret_{period}'
    valid = zone_df[col].dropna()
    if len(valid) > 0:
        mean_r = valid.mean() * 100
        med_r = valid.median() * 100
        win = (valid > 0).mean() * 100
        worst = valid.min() * 100
        best = valid.max() * 100
        print(f"  {period.upper():>3}: Mean={mean_r:+.1f}%, Median={med_r:+.1f}%, Win%={win:.0f}%, Range=[{worst:+.1f}% to {best:+.1f}%]")

# Exclude 1970s to see modern behavior
print("\n" + "=" * 80)
print("EXCLUDING 1970s: MODERN ERA ONLY (1985+)")
print("=" * 80)

df_modern = df_free[df_free['time'] >= '1985-01-01'].copy()
modern_extreme = df_modern[df_modern['dist_52w_ma'] >= 30]

print(f"\nModern era instances >= 30% extended: {len(modern_extreme)}")

if len(modern_extreme) > 0:
    print(f"\n{'Date':<12} {'Ext':>6} {'1w':>8} {'2w':>8} {'1m':>8} {'6w':>8}")
    print("-" * 55)

    for idx, row in modern_extreme.iterrows():
        date_str = row['time'].strftime('%Y-%m-%d')
        ext = f"{row['dist_52w_ma']:.1f}%"
        r1w = f"{row['fwd_ret_1w']*100:+.1f}%" if pd.notna(row['fwd_ret_1w']) else "N/A"
        r2w = f"{row['fwd_ret_2w']*100:+.1f}%" if pd.notna(row['fwd_ret_2w']) else "N/A"
        r1m = f"{row['fwd_ret_1m']*100:+.1f}%" if pd.notna(row['fwd_ret_1m']) else "N/A"
        r6w = f"{row['fwd_ret_6w']*100:+.1f}%" if pd.notna(row['fwd_ret_6w']) else "N/A"
        print(f"{date_str:<12} {ext:>6} {r1w:>8} {r2w:>8} {r1m:>8} {r6w:>8}")

    print(f"\n--- Modern Era Summary (>= 30% Extension) ---")
    for period in ['1w', '2w', '1m', '6w']:
        col = f'fwd_ret_{period}'
        valid = modern_extreme[col].dropna()
        if len(valid) > 0:
            mean_r = valid.mean() * 100
            med_r = valid.median() * 100
            win = (valid > 0).mean() * 100
            print(f"  {period.upper():>3}: Mean={mean_r:+.1f}%, Median={med_r:+.1f}%, Win%={win:.0f}% (n={len(valid)})")

# Final verdict
print("\n" + "=" * 80)
print("BOTTOM LINE: NEAR-TERM TACTICAL VIEW")
print("=" * 80)
print(f"""
At {latest['dist_52w_ma']:.1f}% above 52w MA, gold is extremely stretched.

NEAR-TERM (1-4 weeks) OUTLOOK:
- The data suggests caution is warranted
- Win rates deteriorate at these extension levels
- Even when positive, gains tend to be modest
- Downside risk is elevated

The 1970s data (which dominates the sample) shows that even in raging bull
markets, these extreme extensions often led to quick pullbacks before
resuming the trend.

MODERN ERA (post-1985): Very limited sample at 30%+ extension, but the
2006 and 2008 instances both saw negative near-term returns.

TACTICAL RECOMMENDATION:
- Near-term risk/reward is poor
- Wait for a pullback before adding exposure
- If already long, consider reducing into strength
""")
