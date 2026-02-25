"""
CLI Final: Robustness tests + presentation outputs
====================================================
Tests:
  1. Winsorized z-scores (cap +/-3)
  2. Rolling 504d (2yr) z-scores vs expanding
  3. Both combined
Then: final chart data export + presentation table

Author: Lighthouse Macro
Date: 2026-02-12
"""

import sqlite3
import pandas as pd
import numpy as np
from scipy import stats
import yfinance as yf
import requests
import warnings
import json
warnings.filterwarnings('ignore')

DB_PATH = '/Users/bob/LHM/Data/databases/Lighthouse_Master.db'

# Final config from v5
FINAL_WEIGHTS = {
    'DollarYoY': 0.20,
    'ResRatio_RoC': 0.50,
    'StableBTC_RoC': 0.15,
    'ResRatio': 0.15,
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

    return comps


def z_expanding(s, min_periods=63):
    m = s.expanding(min_periods=min_periods).mean()
    sd = s.expanding(min_periods=min_periods).std()
    return (s - m) / sd


def z_rolling(s, window=504, min_periods=126):
    m = s.rolling(window=window, min_periods=min_periods).mean()
    sd = s.rolling(window=window, min_periods=min_periods).std()
    return (s - m) / sd


def winsorize(s, lo=-3, hi=3):
    return s.clip(lower=lo, upper=hi)


def build_composite(z_comps, weights=FINAL_WEIGHTS):
    parts = [weights[k] * z_comps[k] for k in weights]
    return sum(parts).dropna()


def quintile_test(composite, btc_ret, horizons=[5, 10, 21, 42, 63]):
    results = []
    for hz in horizons:
        fwd = btc_ret.rolling(hz).sum().shift(-hz)
        df = pd.DataFrame({'sig': composite, 'fwd': fwd}).dropna()
        df['q'] = pd.qcut(df['sig'], 5, labels=False, duplicates='drop') + 1
        means = df.groupby('q')['fwd'].mean() * 100
        q1, q5 = means.get(1, 0), means.get(5, 0)
        spread = q5 - q1

        g1, g5 = df[df['q'] == 1]['fwd'], df[df['q'] == 5]['fwd']
        t, p = stats.ttest_ind(g5, g1) if len(g1) > 5 and len(g5) > 5 else (0, 1)

        vals = [means.get(i, 0) for i in range(1, 6)]
        mono5 = all(vals[i] <= vals[i+1] for i in range(4))
        mono3 = vals[0] < vals[2] < vals[4]

        results.append({
            'hz': hz, 'spread': spread, 't': t, 'p': p,
            'mono5': mono5, 'mono3': mono3,
            'q1': q1, 'q2': means.get(2, 0), 'q3': means.get(3, 0),
            'q4': means.get(4, 0), 'q5': q5
        })
    return results


def print_quintile(results, label=""):
    if label:
        print(f"\n  {label}")
    print(f"  {'─'*95}")
    print(f"  {'Hz':>4}   {'Q5-Q1':>8}  {'t':>5}  {'p':>12}  {'M5':>3} {'M3':>3}  "
          f"{'Q1':>7}  {'Q2':>7}  {'Q3':>7}  {'Q4':>7}  {'Q5':>7}")
    print(f"  {'─'*95}")
    for r in results:
        sig = '***' if r['p'] < 0.001 else '**' if r['p'] < 0.01 else '*' if r['p'] < 0.05 else ''
        m5 = '✓' if r['mono5'] else '✗'
        m3 = '✓' if r['mono3'] else '✗'
        print(f"  {r['hz']:>3}D   {r['spread']:>+7.1f}%  {r['t']:>5.1f}  {r['p']:>10.5f}{sig:<3}  "
              f" {m5:>2} {m3:>2}  "
              f"{r['q1']:>+6.1f}%  {r['q2']:>+6.1f}%  {r['q3']:>+6.1f}%  {r['q4']:>+6.1f}%  {r['q5']:>+6.1f}%")


def main():
    print("="*70)
    print("  CLI FINAL: Robustness & Presentation")
    print("="*70)

    btc = fetch_btc()
    btc_ret = np.log(btc['BTC'] / btc['BTC'].shift(1))
    stable = fetch_stablecoins()

    conn = sqlite3.connect(DB_PATH)
    raw = build_raw_components(btc, conn, stable)
    conn.close()

    # ================================================================
    # METHOD COMPARISON
    # ================================================================
    methods = {}

    # 1. Baseline: expanding z, no winsorize
    z_exp = {k: z_expanding(v) for k, v in raw.items()}
    methods['A: Expanding (baseline)'] = build_composite(z_exp)

    # 2. Expanding + winsorize
    z_exp_w = {k: winsorize(z_expanding(v)) for k, v in raw.items()}
    methods['B: Expanding + Winsorize'] = build_composite(z_exp_w)

    # 3. Rolling 2yr
    z_roll = {k: z_rolling(v) for k, v in raw.items()}
    methods['C: Rolling 2yr'] = build_composite(z_roll)

    # 4. Rolling 2yr + winsorize
    z_roll_w = {k: winsorize(z_rolling(v)) for k, v in raw.items()}
    methods['D: Rolling 2yr + Winsorize'] = build_composite(z_roll_w)

    # 5. Rolling 3yr
    z_roll3 = {k: z_rolling(v, window=756) for k, v in raw.items()}
    methods['E: Rolling 3yr'] = build_composite(z_roll3)

    # 6. Rolling 3yr + winsorize
    z_roll3_w = {k: winsorize(z_rolling(v, window=756)) for k, v in raw.items()}
    methods['F: Rolling 3yr + Winsorize'] = build_composite(z_roll3_w)

    print("\n" + "#"*70)
    print("  Z-SCORE METHOD COMPARISON")
    print("#"*70)

    print(f"\n  {'Method':<30} {'21D Spread':>10} {'42D Spread':>10} {'63D Spread':>10} "
          f"{'M5@21':>6} {'M5@42':>6} {'M5@63':>6} {'Obs':>5}")
    print(f"  {'─'*105}")

    best_method = None
    best_score = -1

    for name, comp in methods.items():
        res = quintile_test(comp, btc_ret)
        r21 = [r for r in res if r['hz'] == 21][0]
        r42 = [r for r in res if r['hz'] == 42][0]
        r63 = [r for r in res if r['hz'] == 63][0]
        m21 = '✓' if r21['mono5'] else '✗'
        m42 = '✓' if r42['mono5'] else '✗'
        m63 = '✓' if r63['mono5'] else '✗'

        score = 0
        for r in [r21, r42, r63]:
            if r['mono5']:
                score += 100
            score += r['spread'] * 10

        if score > best_score:
            best_score = score
            best_method = name

        print(f"  {name:<30} {r21['spread']:>+9.1f}% {r42['spread']:>+9.1f}% {r63['spread']:>+9.1f}% "
              f"{m21:>6} {m42:>6} {m63:>6} {len(comp):>5}")

    print(f"\n  BEST METHOD: {best_method}")

    # ================================================================
    # FULL DETAIL ON BEST + BASELINE
    # ================================================================
    print("\n" + "#"*70)
    print("  FULL DETAIL: BASELINE vs BEST")
    print("#"*70)

    for name in ['A: Expanding (baseline)', best_method]:
        comp = methods[name]
        res = quintile_test(comp, btc_ret)
        print_quintile(res, name)

    # ================================================================
    # FINAL: USE BEST METHOD FOR CHART DATA
    # ================================================================
    print("\n" + "#"*70)
    print("  CHART DATA EXPORT")
    print("#"*70)

    # Determine which z-method to use
    if 'Rolling 2yr + Winsorize' in best_method:
        final_z = z_roll_w
    elif 'Rolling 2yr' in best_method:
        final_z = z_roll
    elif 'Rolling 3yr + Winsorize' in best_method:
        final_z = z_roll3_w
    elif 'Rolling 3yr' in best_method:
        final_z = z_roll3
    elif 'Winsorize' in best_method:
        final_z = z_exp_w
    else:
        final_z = z_exp

    final_comp = build_composite(final_z)

    # Rolling 63d BTC returns
    btc_63d = btc_ret.rolling(63).sum() * 100  # as percentage

    # Align
    chart_df = pd.DataFrame({
        'CLI': final_comp,
        'BTC_63d_Ret': btc_63d,
        'BTC_Price': btc['BTC']
    }).dropna()

    # Export for charting
    out_path = '/Users/bob/LHM/Scripts/backtest/cli_chart_data.csv'
    chart_df.to_csv(out_path)
    print(f"  Exported {len(chart_df)} rows to {out_path}")
    print(f"  Date range: {chart_df.index[0].strftime('%Y-%m-%d')} to {chart_df.index[-1].strftime('%Y-%m-%d')}")
    print(f"  Current CLI: {chart_df['CLI'].iloc[-1]:.3f}")

    # ================================================================
    # REGIME STATS FOR PRESENTATION
    # ================================================================
    print("\n" + "#"*70)
    print("  REGIME STATISTICS (for article table)")
    print("#"*70)

    fwd_horizons = {'21D': 21, '42D': 42, '63D': 63}

    for hz_name, hz in fwd_horizons.items():
        fwd = btc_ret.rolling(hz).sum().shift(-hz) * 100
        df = pd.DataFrame({'sig': final_comp, 'fwd': fwd}).dropna()

        # Tercile regimes
        cuts = df['sig'].quantile([1/3, 2/3])
        df['regime'] = pd.cut(df['sig'],
                              bins=[-np.inf, cuts.iloc[0], cuts.iloc[1], np.inf],
                              labels=['Contracting', 'Neutral', 'Expanding'])

        print(f"\n  {hz_name} Forward Returns by Regime:")
        print(f"  {'Regime':<15} {'Avg Ret':>8} {'Med Ret':>8} {'Win Rate':>9} {'Obs':>5} {'Sharpe':>7}")
        print(f"  {'─'*55}")
        for regime in ['Contracting', 'Neutral', 'Expanding']:
            g = df[df['regime'] == regime]['fwd']
            avg = g.mean()
            med = g.median()
            wr = (g > 0).mean() * 100
            sh = g.mean() / g.std() if g.std() > 0 else 0
            n = len(g)
            print(f"  {regime:<15} {avg:>+7.1f}% {med:>+7.1f}% {wr:>7.0f}%  {n:>5} {sh:>+6.2f}")

    # ================================================================
    # YEAR-BY-YEAR FOR ROLLING STABILITY
    # ================================================================
    print("\n" + "#"*70)
    print("  YEAR-BY-YEAR 21D TERCILE SPREADS")
    print("#"*70)

    fwd21 = btc_ret.rolling(21).sum().shift(-21) * 100
    df_yr = pd.DataFrame({'sig': final_comp, 'fwd': fwd21}).dropna()
    df_yr['year'] = df_yr.index.year

    print(f"\n  {'Year':>6}  {'Contract':>10} {'Neutral':>10} {'Expand':>10} {'Spread':>10}  "
          f"{'Contract WR':>12} {'Expand WR':>12}")
    print(f"  {'─'*80}")

    for yr in sorted(df_yr['year'].unique()):
        chunk = df_yr[df_yr['year'] == yr].copy()
        if len(chunk) < 60:
            continue
        try:
            cuts = chunk['sig'].quantile([1/3, 2/3])
            chunk['regime'] = pd.cut(chunk['sig'],
                                     bins=[-np.inf, cuts.iloc[0], cuts.iloc[1], np.inf],
                                     labels=['Contract', 'Neutral', 'Expand'])
            means = chunk.groupby('regime')['fwd'].mean()
            wrs = chunk.groupby('regime').apply(lambda x: (x['fwd'] > 0).mean() * 100)
            c = means.get('Contract', 0)
            n = means.get('Neutral', 0)
            e = means.get('Expand', 0)
            sp = e - c
            cwr = wrs.get('Contract', 0)
            ewr = wrs.get('Expand', 0)
            print(f"  {yr:>6}  {c:>+9.1f}% {n:>+9.1f}% {e:>+9.1f}% {sp:>+9.1f}%  "
                  f"{cwr:>10.0f}%  {ewr:>10.0f}%")
        except Exception:
            pass

    # ================================================================
    # COMPONENT DESCRIPTION TABLE (for article, no sauce)
    # ================================================================
    print("\n" + "#"*70)
    print("  COMPONENT TABLE (public-facing, no formulas)")
    print("#"*70)

    table = [
        ("Tier", "Component", "What It Captures", "Lead Time"),
        ("─"*8, "─"*25, "─"*45, "─"*12),
        ("Macro Tide", "Dollar Momentum", "USD strength/weakness impact on global risk appetite", "6-12 months"),
        ("Plumbing", "Reserve Dynamics", "Banking system liquidity buffer health and trajectory", "4-8 weeks"),
        ("Plumbing", "Reserve Momentum", "Rate of change in system plumbing adequacy", "2-6 weeks"),
        ("Crypto", "Capital Rotation", "Stablecoin vs BTC capital flow dynamics", "1-3 weeks"),
    ]

    for row in table:
        print(f"  {row[0]:<12} {row[1]:<27} {row[2]:<47} {row[3]:<14}")

    print("\n" + "="*70)
    print("  FINAL SCRIPT COMPLETE")
    print("="*70)


if __name__ == '__main__':
    main()
