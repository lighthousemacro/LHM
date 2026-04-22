"""
CLI reading snapshot — 2026-04-22
Uses the same methodology as cli_final.py (winning method: Rolling 2yr +
Winsorize per v5 calibration). Outputs current reading, tier-by-tier
contributions, and 90-day trajectory.
"""

import sqlite3
import pandas as pd
import numpy as np
import yfinance as yf
import requests
import warnings
warnings.filterwarnings('ignore')

DB_PATH = '/Users/bob/LHM/Data/databases/Lighthouse_Master.db'

FINAL_WEIGHTS = {
    'DollarYoY': 0.20,
    'ResRatio_RoC': 0.50,
    'StableBTC_RoC': 0.15,
    'ResRatio': 0.15,
}

# Tier mapping (per CLAUDE_MASTER Section 3 architecture, mapped to v5 components)
TIER_MAP = {
    'DollarYoY': 'Tier 1: Macro Liquidity Tide',
    'ResRatio': 'Tier 2: US Plumbing Mechanics',
    'ResRatio_RoC': 'Tier 2: US Plumbing Mechanics',
    'StableBTC_RoC': 'Tier 3: Crypto-Native Transmission',
}


def load_series(conn, sid):
    df = pd.read_sql(
        "SELECT date, value FROM observations WHERE series_id = ? ORDER BY date",
        conn, params=(sid,), parse_dates=['date']
    ).set_index('date').rename(columns={'value': sid})
    return df


def fetch_btc():
    btc = yf.download('BTC-USD', start='2014-01-01', progress=False)
    if isinstance(btc.columns, pd.MultiIndex):
        btc = btc.droplevel(1, axis=1)
    btc = btc[['Close']].rename(columns={'Close': 'BTC'})
    btc.index = pd.to_datetime(btc.index).tz_localize(None)
    return btc


def fetch_stablecoins():
    total = None
    for sid in [1, 2]:
        url = f"https://stablecoins.llama.fi/stablecoin/{sid}"
        resp = requests.get(url)
        data = resp.json()
        rows = []
        for pt in data.get('tokens', []):
            dt = pd.to_datetime(pt['date'], unit='s')
            circ = pt.get('circulating', {})
            mc = circ.get('peggedUSD', 0) if isinstance(circ, dict) else 0
            if mc > 0:
                rows.append({'date': dt, 'mcap': mc})
        if not rows:
            continue
        s = pd.DataFrame(rows).set_index('date').sort_index()
        s = s[~s.index.duplicated(keep='last')]
        if total is None:
            total = s.rename(columns={'mcap': 'stable_mcap'})
        else:
            total['stable_mcap'] = total['stable_mcap'].add(
                s['mcap'].reindex(total.index, method='ffill'), fill_value=0)
    return total


def build_raw_components(btc, conn, stable):
    dtwex = load_series(conn, 'DTWEXBGS')
    totres = load_series(conn, 'TOTRESNS')
    walcl = load_series(conn, 'WALCL')

    raw_latest = {
        'DTWEXBGS': (dtwex['DTWEXBGS'].dropna().index[-1],
                     dtwex['DTWEXBGS'].dropna().iloc[-1]),
        'TOTRESNS': (totres['TOTRESNS'].dropna().index[-1],
                     totres['TOTRESNS'].dropna().iloc[-1]),
        'WALCL': (walcl['WALCL'].dropna().index[-1],
                  walcl['WALCL'].dropna().iloc[-1]),
        'STABLE': (stable['stable_mcap'].dropna().index[-1],
                   stable['stable_mcap'].dropna().iloc[-1]),
        'BTC': (btc['BTC'].dropna().index[-1],
                btc['BTC'].dropna().iloc[-1]),
    }

    dtwex_d = dtwex['DTWEXBGS'].reindex(btc.index, method='ffill')
    res = totres['TOTRESNS'].reindex(btc.index, method='ffill')
    fed = walcl['WALCL'].reindex(btc.index, method='ffill')
    stable_d = stable['stable_mcap'].reindex(btc.index, method='ffill')

    comps = {}
    comps['DollarYoY'] = -(dtwex_d / dtwex_d.shift(252) - 1)
    comps['ResRatio'] = res / fed
    rr = comps['ResRatio']
    comps['ResRatio_RoC'] = rr / rr.shift(63) - 1
    ratio = stable_d / btc['BTC']
    comps['StableBTC_RoC'] = -(ratio / ratio.shift(21) - 1)

    return comps, raw_latest


def z_rolling(s, window=504, min_periods=126):
    m = s.rolling(window=window, min_periods=min_periods).mean()
    sd = s.rolling(window=window, min_periods=min_periods).std()
    return (s - m) / sd


def winsorize(s, lo=-3, hi=3):
    return s.clip(lower=lo, upper=hi)


def main():
    btc = fetch_btc()
    stable = fetch_stablecoins()
    conn = sqlite3.connect(DB_PATH)
    raw, raw_latest = build_raw_components(btc, conn, stable)
    conn.close()

    # Rolling 2yr + winsorize (winning method)
    z = {k: winsorize(z_rolling(v)) for k, v in raw.items()}
    parts = {k: FINAL_WEIGHTS[k] * z[k] for k in FINAL_WEIGHTS}
    composite = sum(parts.values()).dropna()

    asof = composite.index[-1]
    cli = composite.iloc[-1]

    print("=" * 70)
    print(f"  CRYPTO LIQUIDITY IMPULSE (CLI) — as of {asof.strftime('%Y-%m-%d')}")
    print("=" * 70)
    print(f"\n  HEADLINE CLI: {cli:+.3f}")
    print(f"  Direction: {'EXPANDING (positive)' if cli > 0 else 'CONTRACTING (negative)'}")

    # Regime (based on quintiles from cli_final.py)
    if cli > 0.45:
        regime = "Q5 (Strongest, most bullish)"
    elif cli > 0.14:
        regime = "Q4 (Mild bullish)"
    elif cli > -0.16:
        regime = "Q3 (Neutral)"
    elif cli > -0.57:
        regime = "Q2 (Mild bearish)"
    else:
        regime = "Q1 (Weakest, most bearish)"
    print(f"  Quintile regime: {regime}")

    # Raw component latest values & as-of
    print("\n  --- RAW COMPONENT INPUTS ---")
    for k, (d, v) in raw_latest.items():
        print(f"    {k:<12} latest={v:>14.4f}  asof={d.strftime('%Y-%m-%d')}")

    # Component-level breakdown
    print("\n  --- COMPONENT CONTRIBUTIONS (latest) ---")
    print(f"  {'Component':<18} {'Raw':>12} {'Z-score':>9} {'Weight':>7} {'Contrib':>9} {'Tier':<40}")
    for k in FINAL_WEIGHTS:
        raw_val = raw[k].dropna().iloc[-1]
        z_val = z[k].dropna().iloc[-1]
        w = FINAL_WEIGHTS[k]
        contrib = parts[k].dropna().iloc[-1]
        print(f"  {k:<18} {raw_val:>+12.4f} {z_val:>+9.2f} {w:>7.2f} {contrib:>+9.3f} {TIER_MAP[k]}")

    # Tier contributions
    print("\n  --- TIER CONTRIBUTIONS ---")
    tier_contrib = {}
    for k in FINAL_WEIGHTS:
        tier = TIER_MAP[k]
        tier_contrib.setdefault(tier, 0.0)
        tier_contrib[tier] += parts[k].dropna().iloc[-1]
    for t, v in tier_contrib.items():
        print(f"    {t:<42} {v:+.3f}")

    # 90-day trajectory
    print("\n  --- 90-DAY TRAJECTORY ---")
    recent = composite.last('90D')
    print(f"    Current:    {recent.iloc[-1]:+.3f}  ({recent.index[-1].strftime('%Y-%m-%d')})")
    print(f"    30 days ago:{recent.iloc[-30]:+.3f}")
    print(f"    60 days ago:{recent.iloc[-60]:+.3f}")
    print(f"    90 days ago:{recent.iloc[-90]:+.3f}")
    print(f"    90D change: {recent.iloc[-1] - recent.iloc[-90]:+.3f}")
    print(f"    90D mean:   {recent.mean():+.3f}")
    print(f"    90D min:    {recent.min():+.3f} on {recent.idxmin().strftime('%Y-%m-%d')}")
    print(f"    90D max:    {recent.max():+.3f} on {recent.idxmax().strftime('%Y-%m-%d')}")

    # Historical percentile
    print("\n  --- HISTORICAL PERCENTILE (full history) ---")
    pct = (composite <= cli).mean() * 100
    print(f"    Current CLI is at the {pct:.1f}th percentile of full history")
    print(f"    Full-history median: {composite.median():+.3f}")

    # "Net liquidity expanding AND dollar weakening" regime check
    # Dollar weakening proxy: DollarYoY z-score > 0 (i.e., dollar down YoY)
    # Net liquidity expanding proxy: ResRatio_RoC z-score > 0
    print("\n  --- BULLISH-REGIME DIAGNOSTIC ---")
    dollar_weak = z['DollarYoY'].dropna().iloc[-1] > 0
    liq_expand = z['ResRatio_RoC'].dropna().iloc[-1] > 0
    print(f"    Dollar weakening?       {'YES' if dollar_weak else 'NO'} (DollarYoY z = {z['DollarYoY'].dropna().iloc[-1]:+.2f})")
    print(f"    Net liquidity expanding? {'YES' if liq_expand else 'NO'} (ResRatio_RoC z = {z['ResRatio_RoC'].dropna().iloc[-1]:+.2f})")
    if dollar_weak and liq_expand:
        print("    Regime: BOTH BULLISH (historical BTC +34.1% next Q, 84.7% hit rate)")
    elif (not dollar_weak) and (not liq_expand):
        print("    Regime: BOTH BEARISH (historical BTC +0.9% next Q, 41.7% hit rate)")
    else:
        print("    Regime: MIXED (one bullish, one bearish)")

    # Save snapshot
    snapshot = {
        'asof': asof.strftime('%Y-%m-%d'),
        'cli': float(cli),
        'regime': regime,
        'tier_contrib': tier_contrib,
        'components': {k: {'raw': float(raw[k].dropna().iloc[-1]),
                           'z': float(z[k].dropna().iloc[-1]),
                           'contrib': float(parts[k].dropna().iloc[-1])}
                       for k in FINAL_WEIGHTS},
        'raw_latest': {k: {'asof': d.strftime('%Y-%m-%d'), 'value': float(v)}
                       for k, (d, v) in raw_latest.items()},
    }
    import json
    with open('/Users/bob/LHM/Outputs/cli_snapshot_2026-04-22.json', 'w') as f:
        json.dump(snapshot, f, indent=2)
    print("\n  Saved snapshot: /Users/bob/LHM/Outputs/cli_snapshot_2026-04-22.json")

    # Also save a 90d CLI series for chart
    composite.last('365D').to_csv('/Users/bob/LHM/Outputs/cli_series_1y.csv')


if __name__ == '__main__':
    main()
