#!/usr/bin/env python3
"""
Regime-Aware Concentrated Cross-Asset Book — backtest
=====================================================
The trading expression of the regime work. One book, ten slots, no calendar
rebalancing. Winners are left alone until price says otherwise. Losers are cut
by the single best stop for their asset class.

Rules
-----
Universe    Six major asset classes plus sub-asset detail (rates, credit,
            regions, style, real assets, crypto) — total-return instruments.
Entry       Price above its 200-day average AND relative strength versus SPY
            above its own 63-day average. Among fresh signals, rank by a blend
            of 6-month relative-strength momentum and the asset's historical
            edge in the CURRENT growth/inflation regime. Regime edge is
            estimated on an expanding window of past data only.
Sizing      New money buys equity/10 per slot. No rebalancing afterwards, so a
            winner compounds into an oversized share of the book by design.
Exit        Per-asset-class best stop, chosen by walk-forward search over the
            three canonical candidates: 200-day break with a tight buffer, ATR
            chandelier, negative relative trend versus SPY. Each class uses the
            SINGLE BEST of the three, not a first-to-fire race.
Walk-fwd    Stops optimized in-sample through 2020-12-31, held fixed and
            evaluated out-of-sample 2021 onward.

OOS figures are internal until separately verified. Not for publication.

Author: Lighthouse Macro
Date: 2026-07-26
"""

from __future__ import annotations

import itertools
import os
import pickle
import sys
import warnings

import numpy as np
import pandas as pd

warnings.filterwarnings('ignore')

sys.path.insert(0, '/Users/bob/LHM/Scripts/analysis')
import regime_asset_returns as rar  # noqa: E402

OUT = '/Users/bob/LHM/Outputs/regime_book'
os.makedirs(OUT, exist_ok=True)
CACHE = f'{OUT}/price_cache.pkl'

ANN = 252
START = '2007-01-01'          # deepest common start across the six majors
IS_END = '2020-12-31'
OOS_LO, OOS_HI = '2021-01-01', '2026-12-31'
BENCH = 'SPY'
K_BOOK = 10

# ticker -> asset class bucket (stops are optimized per bucket)
CLASS_MAP = {
    # equity
    **{t: 'us_equity' for t in
       'SPY QQQ IWM RSP IWF IWD MTUM QUAL USMV VLUE XLK XLF XLV XLY XLP XLI '
       'XLE XLB XLU XLRE XLC ITB XHB SMH'.split()},
    **{t: 'intl_equity' for t in 'EFA EEM VGK EWJ FXI ACWI'.split()},
    # rates and credit
    **{t: 'rates' for t in 'SHY IEF TLT TIP MBB AGG BIL'.split()},
    **{t: 'credit' for t in 'LQD HYG EMB'.split()},
    # real assets
    **{t: 'real_assets' for t in 'GLD SLV GDX DBC DBE DBA CPER XME VNQ'.split()},
    # crypto
    'BTC-USD': 'crypto',
}
UNIVERSE = list(CLASS_MAP)

SUBSETS = [('200d',), ('atr',), ('rs',), ('200d', 'atr'), ('200d', 'rs'),
           ('atr', 'rs'), ('200d', 'atr', 'rs')]
X_GRID, K_GRID, L_GRID = [0.005, 0.02], [2.0, 2.5, 3.0, 3.5], [21, 63, 126]


# ------------------------------------------------------------------ data prep

def fetch():
    if os.path.exists(CACHE):
        return pickle.load(open(CACHE, 'rb'))
    import yfinance as yf
    tickers = sorted(set(UNIVERSE + [BENCH]))
    raw = yf.download(tickers, start=START, auto_adjust=True, progress=False,
                      group_by='ticker', threads=True)
    data = {}
    for t in tickers:
        try:
            df = raw[t][['High', 'Low', 'Close']].dropna()
            if len(df) > 300:
                data[t] = df
        except Exception:
            pass
    pickle.dump(data, open(CACHE, 'wb'))
    return data


def atr(df, n=14):
    h, l, c = df['High'], df['Low'], df['Close']
    pc = c.shift(1)
    tr = pd.concat([h - l, (h - pc).abs(), (l - pc).abs()], axis=1).max(axis=1)
    return tr.rolling(n).mean()


def precompute(data, regime: pd.Series):
    """Per-ticker signal arrays plus the regime label aligned to each date."""
    bench = data[BENCH]['Close']
    pre = {}
    for t in UNIVERSE:
        if t not in data:
            continue
        df = data[t]
        c = df['Close']
        sma200 = c.rolling(200).mean()
        rs = (c / bench.reindex(c.index)).dropna()
        idx = rs.index
        c, df, sma200 = c.loc[idx], df.loc[idx], sma200.loc[idx]
        if len(c) < 400:
            continue
        a, trail = atr(df), c.rolling(22).max()
        entry = ((c > sma200) & (rs > rs.rolling(63).mean())).values
        pre[t] = dict(
            cls=CLASS_MAP[t], index=idx, close=c.values,
            ret=c.pct_change().fillna(0).values, rs=rs.values,
            mom=(rs / rs.shift(126) - 1).values,
            entry=entry,
            below200={X: (c < sma200 * (1 - X)).values for X in X_GRID},
            atrk={k: (c < (trail - k * a)).values for k in K_GRID},
            rsl={L: (rs < rs.rolling(L).mean()).values for L in L_GRID},
            regime=regime.reindex(idx).ffill().values,
        )
    return pre


def exit_array(p, subset, X, k, L):
    ex = np.zeros(len(p['close']), dtype=bool)
    if '200d' in subset:
        ex |= p['below200'][X]
    if 'atr' in subset:
        ex |= p['atrk'][k]
    if 'rs' in subset:
        ex |= p['rsl'][L]
    return ex


def simulate(entry, exit_sig, close, cooldown=3):
    n = len(entry)
    pos = np.zeros(n)
    trades = []
    in_pos, cd, ei = False, 0, -1
    for i in range(n):
        if in_pos:
            pos[i] = 1
            if exit_sig[i] or i == n - 1:
                in_pos = False
                cd = cooldown
                trades.append(close[i] / close[ei] - 1)
        elif cd > 0:
            cd -= 1
        elif entry[i]:
            in_pos = True
            pos[i] = 1
            ei = i
    return pos, trades


def book_eq_active(class_pre, subset, X, k, L):
    cols, trades = {}, []
    for t, p in class_pre.items():
        pos, tr = simulate(p['entry'], exit_array(p, subset, X, k, L), p['close'])
        posS = np.r_[0.0, pos[:-1]]
        cols[t] = pd.Series(np.where(posS > 0, posS * p['ret'], np.nan), index=p['index'])
        trades.extend(tr)
    book = pd.DataFrame(cols).mean(axis=1).fillna(0.0)
    book = book.loc[book.ne(0).idxmax():] if (book != 0).any() else book
    return book, np.array(trades)


def metrics(book, trades, lo=None, hi=None):
    b = book
    if lo:
        b = b[(b.index >= lo) & (b.index <= hi)]
    if len(b) < 50:
        return None
    eq = (1 + b).cumprod()
    yrs = len(b) / ANN
    cagr = eq.iloc[-1] ** (1 / yrs) - 1
    dd = (eq / eq.cummax() - 1).min()
    ds = b[b < 0]
    sortino = (b.mean() * ANN) / (ds.std() * np.sqrt(ANN)) if len(ds) else np.nan
    calmar = cagr / abs(dd) if dd < 0 else np.nan
    omega = b[b > 0].sum() / (-b[b < 0].sum()) if (b < 0).any() else np.nan
    tr = np.asarray(trades)
    w, l = tr[tr > 0], tr[tr < 0]
    return dict(CAGR=cagr, MaxDD=dd, Sortino=sortino, Calmar=calmar, Omega=omega,
                Vol=b.std() * np.sqrt(ANN),
                Payoff=w.mean() / abs(l.mean()) if len(w) and len(l) else np.nan,
                Expectancy=tr.mean() if len(tr) else np.nan,
                ProfitFactor=w.sum() / abs(l.sum()) if len(l) and l.sum() != 0 else np.nan,
                WinRate=len(w) / len(tr) if len(tr) else np.nan, NTrades=len(tr))


def objective(m):
    if m is None or m['NTrades'] < 20:
        return -1e9
    vals = [m['Sortino'], m['Calmar'], m['Omega'], np.log1p(max(m['Payoff'], 0)),
            m['Expectancy'] * 100]
    return float(np.nansum(vals))


# ------------------------------------------------------------- regime scoring

def regime_edge_panel(pre, regime: pd.Series) -> pd.DataFrame:
    """Expanding-window annualized return of each asset inside each regime.

    Recomputed at each month end using ONLY data available up to that date, so
    the ranking never sees its own future. Returned frame is indexed by
    (month_end, regime) with one column per ticker.
    """
    rets = pd.DataFrame({t: pd.Series(p['ret'], index=p['index']) for t, p in pre.items()})
    reg = regime.reindex(rets.index).ffill().shift(1)
    month_ends = rets.resample('ME').last().index
    rows = {}
    for me in month_ends:
        hist = rets.loc[:me]
        rh = reg.loc[:me]
        if len(hist) < ANN:
            continue
        for st in rar.QUADRANTS:
            sub = hist[rh == st]
            if len(sub) < 120:
                continue
            n = sub.notna().sum()
            ann = (1 + sub.fillna(0)).prod() ** (ANN / n.replace(0, np.nan)) - 1
            rows[(me, st)] = ann * 100
    return pd.DataFrame(rows).T


def concentrated_book(pre, exit_of, regime: pd.Series, edge: pd.DataFrame,
                      K=K_BOOK, edge_weight=0.5, max_weight=None):
    """Top-K book that compounds. Returns (daily returns, weights frame, trades)."""
    dates = pd.DatetimeIndex(sorted(set().union(*[set(p['index']) for p in pre.values()])))
    di = {d: i for i, d in enumerate(dates)}
    tks = list(pre)
    n, m = len(dates), len(tks)
    RET = np.full((n, m), np.nan)
    ENT = np.zeros((n, m))
    MOM = np.full((n, m), np.nan)
    EX = np.zeros((n, m))
    CL = np.full((n, m), np.nan)
    for j, t in enumerate(tks):
        p = pre[t]
        rows = [di[d] for d in p['index']]
        RET[rows, j] = p['ret']
        ENT[rows, j] = p['entry']
        MOM[rows, j] = p['mom']
        CL[rows, j] = p['close']
        EX[rows, j] = exit_of[t]

    reg = regime.reindex(dates).ffill().shift(1)
    # edge lookup: for each date use the most recent month-end estimate
    edge_dates = edge.index.get_level_values(0).unique().sort_values()

    cash = 1.0
    posval, entry_px, cd = {}, {}, {}
    equity_curve = np.zeros(n)
    weights = np.zeros((n, m))
    trades, trade_log = [], []

    edge_cache, cached_key = None, None
    for i, d in enumerate(dates):
        for j in list(posval):
            r = RET[i, j]
            if not np.isnan(r):
                posval[j] *= (1 + r)
        equity = cash + sum(posval.values())
        # Optional single-position cap. Pure "let winners run" has no cap, which
        # is how one parabolic name can become most of the book. Trimming the
        # excess back to cash is the only place the book ever sells a winner.
        if max_weight is not None and equity > 0:
            for j in list(posval):
                over = posval[j] - max_weight * equity
                if over > 0:
                    posval[j] -= over
                    cash += over
        equity = cash + sum(posval.values())
        equity_curve[i] = equity
        if equity > 0:
            for j, v in posval.items():
                weights[i, j] = v / equity

        for j in list(cd):
            cd[j] -= 1
            if cd[j] <= 0:
                del cd[j]

        for j in list(posval):
            if np.isnan(CL[i, j]) or EX[i, j] == 1 or i == n - 1:
                if not np.isnan(CL[i, j]):
                    r = CL[i, j] / entry_px[j] - 1
                    trades.append(r)
                    trade_log.append(dict(ticker=tks[j], exit=d, ret=r))
                cash += posval[j]
                del posval[j]
                del entry_px[j]
                cd[j] = 3

        if len(posval) < K and cash > 1e-6:
            st = reg.iloc[i]
            prior = edge_dates[edge_dates < d]
            key = (prior[-1] if len(prior) else None, st)
            if key != cached_key:
                cached_key = key
                edge_cache = (edge.loc[key] if (key[0] is not None and key in edge.index)
                              else None)
            cand = []
            for j in range(m):
                if j in posval or j in cd or ENT[i, j] != 1 or np.isnan(MOM[i, j]):
                    continue
                score = MOM[i, j]
                if edge_cache is not None:
                    e = edge_cache.get(tks[j], np.nan)
                    if np.isfinite(e):
                        score += edge_weight * (e / 100.0)
                cand.append((score, j))
            cand.sort(reverse=True)
            for _, j in cand[:K - len(posval)]:
                alloc = min(equity / K, cash)
                if alloc <= 1e-6:
                    break
                posval[j] = alloc
                cash -= alloc
                entry_px[j] = CL[i, j]

    eqc = pd.Series(equity_curve, index=dates)
    first = eqc.ne(eqc.iloc[0]).idxmax() if (eqc != eqc.iloc[0]).any() else eqc.index[0]
    eqc = eqc.loc[first:]
    wdf = pd.DataFrame(weights, index=dates, columns=tks).loc[first:]
    wdf['Cash'] = 1 - wdf.sum(axis=1)
    return eqc.pct_change().fillna(0.0), wdf, np.array(trades), pd.DataFrame(trade_log)


# -------------------------------------------------------------------- runner

def run():
    print('Fetching prices...')
    data = fetch()
    gi = rar.growth_inflation_regime()
    regime = gi.quadrant
    pre = precompute(data, regime)

    classes = {}
    for t, p in pre.items():
        classes.setdefault(p['cls'], {})[t] = p
    print(f'Universe: {len(pre)} instruments across {len(classes)} classes: '
          + ', '.join(f'{c}({len(v)})' for c, v in classes.items()))

    # ---- Stage 1: best single stop per asset class, in-sample only ----
    print('\nStage 1 — walk-forward stop search per asset class (in-sample <= 2020)')
    best_by_class, rows = {}, []
    for cls, cp in classes.items():
        scored = []
        for subset in SUBSETS:
            xs = X_GRID if '200d' in subset else [None]
            ks = K_GRID if 'atr' in subset else [None]
            ls = L_GRID if 'rs' in subset else [None]
            for X, k, L in itertools.product(xs, ks, ls):
                book, trades = book_eq_active(cp, subset, X, k, L)
                m_is = metrics(book, trades, START, IS_END)
                scored.append((objective(m_is), subset, X, k, L, m_is))
        scored.sort(key=lambda r: r[0], reverse=True)
        s, subset, X, k, L, m_is = scored[0]
        best_by_class[cls] = (subset, X, k, L)
        rows.append(dict(asset_class=cls, stop='+'.join(subset), X=X, k=k, L=L,
                         IS_Sortino=m_is['Sortino'], IS_Calmar=m_is['Calmar'],
                         IS_Payoff=m_is['Payoff'], IS_CAGR=m_is['CAGR'],
                         IS_MaxDD=m_is['MaxDD'], NTrades=m_is['NTrades']))
        print(f'  {cls:12s} -> {"+".join(subset):14s} X={X} k={k} L={L}   '
              f'IS Sortino {m_is["Sortino"]:.2f}  Payoff {m_is["Payoff"]:.2f}')
    stops = pd.DataFrame(rows)
    stops.to_csv(f'{OUT}/best_stops_by_class.csv', index=False)

    # ---- Stage 2: the concentrated regime book ----
    print('\nStage 2 — concentrated book, 10 slots, no rebalancing')
    exit_of = {t: exit_array(p, *best_by_class[p['cls']]) for t, p in pre.items()}
    edge = regime_edge_panel(pre, regime)

    book, weights, trades, tlog = concentrated_book(pre, exit_of, regime, edge)
    base_exit = {t: exit_array(p, ('200d',), 0.02, None, None) for t, p in pre.items()}
    base, base_w, base_tr, base_log = concentrated_book(pre, base_exit, regime, edge, edge_weight=0.0)
    capped, capped_w, capped_tr, capped_log = concentrated_book(
        pre, exit_of, regime, edge, max_weight=0.25)

    spy = data[BENCH]['Close'].pct_change().fillna(0)
    spy = spy.reindex(book.index).fillna(0)
    agg = data['AGG']['Close'].pct_change().fillna(0).reindex(book.index).fillna(0)
    sixty40 = 0.6 * spy + 0.4 * agg

    def window_trades(log, lo, hi):
        if log is None or log.empty:
            return np.array([])
        d = pd.to_datetime(log['exit'])
        return log.loc[(d >= lo) & (d <= hi), 'ret'].values

    out = {}
    for label, series, tlg in [('Regime Book', book, tlog),
                               ('Regime Book, 25% cap', capped, capped_log),
                               ('Plain 200d top-10', base, base_log),
                               ('SPY', spy, None),
                               ('60/40', sixty40, None)]:
        for tag, lo, hi in [('FULL', START, OOS_HI), ('IS', START, IS_END),
                            ('OOS', OOS_LO, OOS_HI)]:
            m = metrics(series, window_trades(tlg, lo, hi), lo, hi)
            if m:
                out[(label, tag)] = m
    res = pd.DataFrame(out).T
    res.index.names = ['strategy', 'window']
    res.to_csv(f'{OUT}/performance_summary.csv')

    pd.set_option('display.width', 220)
    print('\n' + res[['CAGR', 'Vol', 'MaxDD', 'Sortino', 'Calmar', 'Omega',
                      'Payoff', 'WinRate', 'NTrades']].round(3).to_string())

    weights.to_parquet(f'{OUT}/weights.parquet')
    capped_w.to_parquet(f'{OUT}/weights_capped.parquet')
    pd.DataFrame({'book': book, 'capped': capped, 'baseline': base, 'spy': spy,
                  'sixty40': sixty40}).to_parquet(f'{OUT}/returns.parquet')
    tlog.to_csv(f'{OUT}/trade_log.csv', index=False)

    cur = weights.iloc[-1]
    cur = cur[cur > 1e-4].sort_values(ascending=False)
    print('\nCurrent book:')
    for k, v in cur.items():
        print(f'  {k:10s} {v*100:5.1f}%')
    print(f'\nWritten to {OUT}')
    return dict(stops=stops, results=res, weights=weights, book=book,
                capped=capped, capped_weights=capped_w, capped_trades=capped_log,
                baseline=base, spy=spy, sixty40=sixty40, trades=tlog)


if __name__ == '__main__':
    run()
