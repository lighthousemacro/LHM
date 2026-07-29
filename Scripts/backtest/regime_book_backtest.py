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
# Granularity modes. The book can bet at the asset-class level (six sleeves,
# one instrument each) or at the sub-asset-class level (the full ladder), or
# both. Sub-asset bets give the ranking more to choose from and let the book
# express WHICH part of a sleeve is working, at the cost of more correlated
# candidates competing for the same ten slots.
UNIVERSE_MODES = {
    'majors': 'SPY IEF LQD DBC GLD UUP'.split(),
    'majors_plus': 'SPY IEF LQD DBC GLD UUP BTC-USD VNQ'.split(),
    'sub': list(CLASS_MAP),
}
UNIVERSE = UNIVERSE_MODES['sub']

CAP_GRID = [0.15, 0.20, 0.25, 1 / 3, 0.50, None]

SUBSETS = [('200d',), ('atr',), ('rs',), ('200d', 'atr'), ('200d', 'rs'),
           ('atr', 'rs'), ('200d', 'atr', 'rs')]
X_GRID, K_GRID, L_GRID = [0.005, 0.02], [2.0, 2.5, 3.0, 3.5], [21, 63, 126]


# ------------------------------------------------------------------ data prep

def fetch():
    if os.path.exists(CACHE):
        return pickle.load(open(CACHE, 'rb'))
    import yfinance as yf
    tickers = sorted(set(UNIVERSE_MODES['sub'] + [BENCH]))
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


def precompute(data, regime: pd.Series, universe=None):
    """Per-ticker signal arrays plus the regime label aligned to each date."""
    bench = data[BENCH]['Close']
    pre = {}
    for t in (universe if universe is not None else UNIVERSE):
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
        trough = c.rolling(22).min()
        entry = ((c > sma200) & (rs > rs.rolling(63).mean())).values
        # Short entry is the exact mirror: price below its 200-day AND losing
        # ground to the benchmark. Short stops mirror the long stops too, so a
        # class keeps the same exit logic on both sides of the book.
        entry_s = ((c < sma200) & (rs < rs.rolling(63).mean())).values
        # Short-side GATES. A short has to clear a higher bar than the mirror of
        # a long: being below trend is not a thesis, it is a dip until the trend
        # itself has rolled over and the name is losing ground persistently.
        slope200 = sma200.diff(21)
        gates = dict(
            downtrend=(slope200 < 0).values,                    # the 200d itself is falling
            deep=(c < sma200 * 0.97).values,                    # 3% below, not brushing it
            persistent=(rs < rs.rolling(126).mean()).values,    # 6mo of losing to SPY, not 3
            no_bounce=(c < c.rolling(22).max() * 0.95).values,  # not already snapping back
        )
        pre[t] = dict(
            cls=CLASS_MAP[t], index=idx, close=c.values,
            ret=c.pct_change().fillna(0).values, rs=rs.values,
            mom=(rs / rs.shift(126) - 1).values,
            entry=entry, entry_s=entry_s, gates=gates,
            below200={X: (c < sma200 * (1 - X)).values for X in X_GRID},
            atrk={k: (c < (trail - k * a)).values for k in K_GRID},
            rsl={L: (rs < rs.rolling(L).mean()).values for L in L_GRID},
            above200={X: (c > sma200 * (1 + X)).values for X in X_GRID},
            atrk_s={k: (c > (trough + k * a)).values for k in K_GRID},
            rsl_s={L: (rs > rs.rolling(L).mean()).values for L in L_GRID},
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


def exit_array_short(p, subset, X, k, L):
    """Mirror of exit_array for a short position (a cover signal)."""
    ex = np.zeros(len(p['close']), dtype=bool)
    if '200d' in subset:
        ex |= p['above200'][X]
    if 'atr' in subset:
        ex |= p['atrk_s'][k]
    if 'rs' in subset:
        ex |= p['rsl_s'][L]
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
    """Payoff-preserving blend, for comparing STOPS (same trade structure)."""
    if m is None or m['NTrades'] < 20:
        return -1e9
    vals = [m['Sortino'], m['Calmar'], m['Omega'], np.log1p(max(m['Payoff'], 0)),
            m['Expectancy'] * 100]
    return float(np.nansum(vals))


def objective_pathwise(m):
    """Trade-count-neutral score, for comparing PORTFOLIO CONSTRUCTION choices.

    The per-trade terms in `objective` (payoff, expectancy) are not comparable
    across variants that change how many positions exist. A book that holds five
    names and 50% cash books fewer, longer, larger trades and scores a huge
    expectancy without earning a better return path. Caps and slot limits get
    judged on the equity curve alone.
    """
    if m is None:
        return -1e9
    return float(np.nansum([m['Sortino'], m['Calmar'], m['Omega']]))


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
                      K=K_BOOK, edge_weight=0.5, max_weight=None,
                      max_per_class=None):
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
    # Ten slots is only ten bets if the slots hold different things. SHY, IEF,
    # AGG, TIP and MBB are one duration bet wearing five tickers.
    cls_of = np.array([pre[t]['cls'] for t in tks])

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
            if max_per_class is not None:
                held = {}
                for j in posval:
                    held[cls_of[j]] = held.get(cls_of[j], 0) + 1
            filled = 0
            for _, j in cand:
                if filled >= K - len(posval):
                    break
                if max_per_class is not None:
                    c = cls_of[j]
                    if held.get(c, 0) >= max_per_class:
                        continue
                    held[c] = held.get(c, 0) + 1
                alloc = min(equity / K, cash)
                if alloc <= 1e-6:
                    break
                posval[j] = alloc
                cash -= alloc
                entry_px[j] = CL[i, j]
                filled += 1

    eqc = pd.Series(equity_curve, index=dates)
    first = eqc.ne(eqc.iloc[0]).idxmax() if (eqc != eqc.iloc[0]).any() else eqc.index[0]
    eqc = eqc.loc[first:]
    wdf = pd.DataFrame(weights, index=dates, columns=tks).loc[first:]
    wdf['Cash'] = 1 - wdf.sum(axis=1)
    return eqc.pct_change().fillna(0.0), wdf, np.array(trades), pd.DataFrame(trade_log)



def long_short_book(pre, exit_of, cover_of, regime: pd.Series, edge: pd.DataFrame,
                    K=K_BOOK, edge_weight=0.5, max_weight=0.25, allow_short=True,
                    short_gates=(), risk_gate=None, edge_floor=None,
                    max_shorts=None):
    """Symmetric long/short book. Ten slots total, gross capped at 100%.

    Shorts are fully collateralized: entering a short reserves its notional from
    cash, so gross exposure can never exceed the account and there is no
    leverage in this version. A short's contribution to equity is
    collateral + (notional - current liability), which is the honest mark.
    Net exposure floats with how many slots each side can fill.
    """
    dates = pd.DatetimeIndex(sorted(set().union(*[set(p['index']) for p in pre.values()])))
    di = {d: i for i, d in enumerate(dates)}
    tks = list(pre)
    n, m = len(dates), len(tks)
    RET = np.full((n, m), np.nan)
    ENT_L = np.zeros((n, m)); ENT_S = np.zeros((n, m))
    MOM = np.full((n, m), np.nan)
    EX_L = np.zeros((n, m)); EX_S = np.zeros((n, m))
    CL = np.full((n, m), np.nan)
    for j, t in enumerate(tks):
        p = pre[t]
        rows = [di[d] for d in p['index']]
        RET[rows, j] = p['ret']
        ENT_L[rows, j] = p['entry']
        es = p['entry_s'].copy()
        for g in short_gates:
            es &= p['gates'][g]
        ENT_S[rows, j] = es
        MOM[rows, j] = p['mom']
        CL[rows, j] = p['close']
        EX_L[rows, j] = exit_of[t]; EX_S[rows, j] = cover_of[t]

    reg = regime.reindex(dates).ffill().shift(1)
    edge_dates = edge.index.get_level_values(0).unique().sort_values()
    # Macro permission to be short at all. Shorting into a benign risk regime is
    # how a trend book bleeds; the gate says only press when the dial agrees.
    if risk_gate is not None:
        rg = risk_gate.reindex(dates).ffill().shift(1).fillna(False).astype(bool).values
    else:
        rg = np.ones(n, dtype=bool)

    cash = 1.0
    pos = {}          # j -> dict(side, val, notional, liab, entry_px)
    cd = {}
    equity_curve = np.zeros(n)
    weights = np.zeros((n, m))
    net_exp = np.zeros(n); gross_exp = np.zeros(n)
    trade_log = []
    edge_cache, cached_key = None, None

    def contribution(q):
        return q['val'] if q['side'] > 0 else (q['notional'] + (q['notional'] - q['liab']))

    for i, d in enumerate(dates):
        for j, q in pos.items():
            r = RET[i, j]
            if np.isnan(r):
                continue
            if q['side'] > 0:
                q['val'] *= (1 + r)
            else:
                q['liab'] *= (1 + r)
        equity = cash + sum(contribution(q) for q in pos.values())

        if max_weight is not None and equity > 0:
            for j, q in list(pos.items()):
                if q['side'] > 0:
                    over = q['val'] - max_weight * equity
                    if over > 0:
                        q['val'] -= over
                        cash += over
                else:
                    over = q['notional'] - max_weight * equity
                    if over > 0:
                        # trim the short pro rata, releasing collateral and P&L
                        frac = over / q['notional']
                        released = frac * (q['notional'] + (q['notional'] - q['liab']))
                        q['notional'] -= over
                        q['liab'] *= (1 - frac)
                        cash += released
            equity = cash + sum(contribution(q) for q in pos.values())

        equity_curve[i] = equity
        if equity > 0:
            for j, q in pos.items():
                w = (q['val'] if q['side'] > 0 else -q['notional']) / equity
                weights[i, j] = w
            net_exp[i] = weights[i].sum()
            gross_exp[i] = np.abs(weights[i]).sum()

        for j in list(cd):
            cd[j] -= 1
            if cd[j] <= 0:
                del cd[j]

        for j, q in list(pos.items()):
            hit = (EX_L[i, j] == 1) if q['side'] > 0 else (EX_S[i, j] == 1)
            if np.isnan(CL[i, j]) or hit or i == n - 1:
                if not np.isnan(CL[i, j]):
                    raw = CL[i, j] / q['entry_px'] - 1
                    trade_log.append(dict(ticker=tks[j], exit=d,
                                          side='long' if q['side'] > 0 else 'short',
                                          ret=raw if q['side'] > 0 else -raw))
                cash += contribution(q)
                del pos[j]
                cd[j] = 3

        if len(pos) < K and cash > 1e-6:
            st = reg.iloc[i]
            prior = edge_dates[edge_dates < d]
            key = (prior[-1] if len(prior) else None, st)
            if key != cached_key:
                cached_key = key
                edge_cache = (edge.loc[key] if (key[0] is not None and key in edge.index)
                              else None)
            cand = []
            for j in range(m):
                if j in pos or j in cd or np.isnan(MOM[i, j]):
                    continue
                e = edge_cache.get(tks[j], np.nan) if edge_cache is not None else np.nan
                e = e / 100.0 if np.isfinite(e) else 0.0
                if ENT_L[i, j] == 1:
                    cand.append((MOM[i, j] + edge_weight * e, +1, j))
                elif (allow_short and ENT_S[i, j] == 1 and rg[i]
                      and (edge_floor is None or e * 100 < edge_floor)):
                    # short score is the mirror: most negative momentum and the
                    # worst regime edge become the strongest short candidates
                    cand.append((-(MOM[i, j] + edge_weight * e), -1, j))
            cand.sort(reverse=True)
            n_short_open = sum(1 for q in pos.values() if q['side'] < 0)
            for _, side, j in cand[:K - len(pos)]:
                if side < 0 and max_shorts is not None and n_short_open >= max_shorts:
                    continue
                alloc = min(equity / K, cash)
                if alloc <= 1e-6:
                    break
                cash -= alloc
                if side > 0:
                    pos[j] = dict(side=1, val=alloc, notional=alloc, liab=alloc,
                                  entry_px=CL[i, j])
                else:
                    pos[j] = dict(side=-1, val=0.0, notional=alloc, liab=alloc,
                                  entry_px=CL[i, j])
                    n_short_open += 1

    eqc = pd.Series(equity_curve, index=dates)
    first = eqc.ne(eqc.iloc[0]).idxmax() if (eqc != eqc.iloc[0]).any() else eqc.index[0]
    eqc = eqc.loc[first:]
    wdf = pd.DataFrame(weights, index=dates, columns=tks).loc[first:]
    expo = pd.DataFrame({'net': net_exp, 'gross': gross_exp}, index=dates).loc[first:]
    log = pd.DataFrame(trade_log)
    return eqc.pct_change().fillna(0.0), wdf, expo, log


# -------------------------------------------------------------------- runner

def run(mode='sub', verbose=True):
    print('Fetching prices...')
    data = fetch()
    gi = rar.growth_inflation_regime()
    regime = gi.quadrant
    universe = UNIVERSE_MODES[mode]
    pre = precompute(data, regime, universe)

    classes = {}
    for t, p in pre.items():
        classes.setdefault(p['cls'], {})[t] = p
    print(f'Universe [{mode}]: {len(pre)} instruments across {len(classes)} classes: '
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
    # ---- Stage 2b: the single-position cap, chosen the same way the stops were ----
    # Scored IN-SAMPLE ONLY on the same payoff-preserving objective, so the cap
    # is walk-forward selected rather than picked after seeing the blow-up.
    print('\nStage 2b — single-position cap sweep (in-sample <= 2020)')
    cap_rows, cap_runs = [], {}
    for cap in CAP_GRID:
        cb, cw, ctr, clog = concentrated_book(pre, exit_of, regime, edge, max_weight=cap)
        cap_runs[cap] = (cb, cw, ctr, clog)
        m_is = metrics(cb, clog.loc[pd.to_datetime(clog['exit']) <= IS_END, 'ret'].values
                       if not clog.empty else np.array([]), START, IS_END)
        score = objective_pathwise(m_is)
        cap_rows.append(dict(cap='none' if cap is None else f'{cap*100:.0f}%',
                             score=score, IS_CAGR=m_is['CAGR'], IS_Vol=m_is['Vol'],
                             IS_MaxDD=m_is['MaxDD'], IS_Sortino=m_is['Sortino'],
                             IS_Calmar=m_is['Calmar'], IS_Omega=m_is['Omega']))
        print(f'  cap {"none" if cap is None else f"{cap*100:.0f}%":>5}  score {score:7.2f}  '
              f'IS CAGR {m_is["CAGR"]*100:5.1f}%  MaxDD {m_is["MaxDD"]*100:6.1f}%  '
              f'Sortino {m_is["Sortino"]:.2f}  Calmar {m_is["Calmar"]:.2f}')
    caps = pd.DataFrame(cap_rows).sort_values('score', ascending=False)
    caps.to_csv(f'{OUT}/cap_sweep.csv', index=False)
    best_cap = CAP_GRID[int(np.argmax([r['score'] for r in cap_rows]))]
    CAP_LABEL = 'none' if best_cap is None else f'{best_cap*100:.0f}%'
    print(f'  -> winning cap: {CAP_LABEL}')
    capped, capped_w, capped_tr, capped_log = cap_runs[best_cap]

    # ---- Stage 2c: per-asset-class slot cap ----
    # Ten slots is only ten bets if they are different bets. Search the class
    # cap in-sample on the same objective, same as the stops and the weight cap.
    print('\nStage 2c — per-asset-class slot cap sweep (in-sample <= 2020)')
    cls_rows, cls_runs = [], {}
    for mx in [1, 2, 3, 4, None]:
        cb, cw, ctr, clog = concentrated_book(pre, exit_of, regime, edge,
                                              max_weight=best_cap, max_per_class=mx)
        cls_runs[mx] = (cb, cw, ctr, clog)
        m_is = metrics(cb, clog.loc[pd.to_datetime(clog['exit']) <= IS_END, 'ret'].values
                       if not clog.empty else np.array([]), START, IS_END)
        # how concentrated is the book in practice
        cls_series = pd.Series([pre[t]['cls'] for t in cw.columns if t != 'Cash'],
                               index=[t for t in cw.columns if t != 'Cash'])
        held = (cw.drop(columns=['Cash'], errors='ignore') > 1e-4)
        eff = held.groupby(cls_series, axis=1).any().sum(axis=1)
        cls_rows.append(dict(cap='none' if mx is None else mx,
                             score=objective_pathwise(m_is), IS_CAGR=m_is['CAGR'],
                             IS_Vol=m_is['Vol'], IS_MaxDD=m_is['MaxDD'],
                             IS_Sortino=m_is['Sortino'], IS_Calmar=m_is['Calmar'],
                             avg_classes_held=eff[eff > 0].mean()))
        print(f'  max {"none" if mx is None else mx:>4} per class  score {objective_pathwise(m_is):7.2f}  '
              f'IS CAGR {m_is["CAGR"]*100:5.1f}%  MaxDD {m_is["MaxDD"]*100:6.1f}%  '
              f'Sortino {m_is["Sortino"]:.2f}  avg distinct classes held {eff[eff>0].mean():.1f}')
    cls_tab = pd.DataFrame(cls_rows).sort_values('score', ascending=False)
    cls_tab.to_csv(f'{OUT}/class_cap_sweep.csv', index=False)
    best_class_cap = cls_tab.iloc[0].cap
    best_class_cap = None if best_class_cap == 'none' else int(best_class_cap)
    print(f'  -> winning class cap: {best_class_cap if best_class_cap else "none"}')
    diversified, div_w, div_tr, div_log = cls_runs[best_class_cap]

    # ---- Stage 3: symmetric long/short, same ranking, same stops ----
    print('\nStage 3 — symmetric long/short (margin live 2026-07-26, no leverage in v1)')
    cover_of = {t: exit_array_short(p, *best_by_class[p['cls']]) for t, p in pre.items()}
    # Baseline: the naive mirror, kept as the control.
    mirror_book, mirror_w, mirror_expo, mirror_log = long_short_book(
        pre, exit_of, cover_of, regime, edge, max_weight=best_cap)
    m_is = metrics(mirror_book,
                   mirror_log.loc[pd.to_datetime(mirror_log['exit']) <= IS_END, 'ret'].values,
                   START, IS_END)
    print(f'  mirror (control): IS CAGR {m_is["CAGR"]*100:5.1f}%  '
          f'Sortino {m_is["Sortino"]:.2f}  score {objective(m_is):.2f}')

    # ---- Stage 3b: what does a short have to clear to be worth taking? ----
    # A short is not a long with the sign flipped. Search the gate stack the same
    # way the stops and the cap were searched: in-sample only, same objective.
    print('\nStage 3b — short-side gate ablation (in-sample <= 2020)')
    GATES = ['downtrend', 'deep', 'persistent', 'no_bounce']
    # risk-regime permission: only short when the risk dial is off Low Risk
    mri_band = rar.mri_regime().band
    risk_on_gate = mri_band.isin(['Elevated', 'High Risk', 'Crisis'])
    # or when growth is rolling over
    contraction_gate = regime.isin(['Contraction', 'Stagflation'])

    variants = []
    for r in range(len(GATES) + 1):
        for combo in itertools.combinations(GATES, r):
            variants.append((combo, None, None, None, 'none'))
    # layer the macro permissions onto the full technical stack
    full = tuple(GATES)
    variants += [
        (full, risk_on_gate, None, None, 'MRI elevated+'),
        (full, contraction_gate, None, None, 'growth rolling over'),
        (full, risk_on_gate, -5.0, None, 'MRI + negative regime edge'),
        (full, None, -5.0, None, 'negative regime edge'),
        (full, risk_on_gate, None, 3, 'MRI + max 3 shorts'),
        (full, risk_on_gate, -5.0, 3, 'MRI + edge + max 3 shorts'),
    ]

    ls_rows, ls_runs = [], {}
    for combo, rgate, floor, mx, tag in variants:
        b, w, ex, lg = long_short_book(
            pre, exit_of, cover_of, regime, edge, max_weight=best_cap,
            short_gates=combo, risk_gate=rgate, edge_floor=floor, max_shorts=mx)
        is_tr = (lg.loc[pd.to_datetime(lg['exit']) <= IS_END] if not lg.empty
                 else pd.DataFrame(columns=['ret', 'side']))
        mm = metrics(b, is_tr['ret'].values, START, IS_END)
        if mm is None:
            continue
        sh = is_tr[is_tr.side == 'short'] if 'side' in is_tr else is_tr
        key = ('+'.join(combo) if combo else 'mirror only') + f' | {tag}'
        ls_runs[key] = (b, w, ex, lg)
        ls_rows.append(dict(gates=key, score=objective(mm), IS_CAGR=mm['CAGR'],
                            IS_MaxDD=mm['MaxDD'], IS_Sortino=mm['Sortino'],
                            IS_Calmar=mm['Calmar'], n_short=len(sh),
                            short_avg=sh.ret.mean() if len(sh) else np.nan,
                            short_win=(sh.ret > 0).mean() if len(sh) else np.nan))
    ls_tab = pd.DataFrame(ls_rows).sort_values('score', ascending=False)
    ls_tab.to_csv(f'{OUT}/short_gate_ablation.csv', index=False)
    print(ls_tab.head(12).round(3).to_string(index=False))

    # Long-only is in the running: if no short variant beats it in-sample, the
    # honest answer is that the short side does not belong in the book.
    long_only_score = objective(metrics(
        capped, capped_log.loc[pd.to_datetime(capped_log['exit']) <= IS_END, 'ret'].values,
        START, IS_END))
    best_row = ls_tab.iloc[0]
    print(f'\n  best short variant IS score {best_row.score:.2f}  vs  '
          f'long-only {long_only_score:.2f}')
    if best_row.score <= long_only_score:
        print('  -> no short variant clears long-only in-sample. Shorts stay out.')
    else:
        print(f'  -> shorts earn a place: {best_row.gates}')
    ls_book, ls_w, ls_expo, ls_log = ls_runs[best_row.gates]
    LS_LABEL = best_row.gates
    ls_stats = metrics(ls_book, ls_log.ret.values if not ls_log.empty else np.array([]))
    n_short = int((ls_log.side == 'short').sum()) if not ls_log.empty else 0
    print(f'  gross avg {ls_expo.gross.mean()*100:.0f}%  net avg {ls_expo.net.mean()*100:+.0f}%  '
          f'net range {ls_expo.net.min()*100:+.0f}% to {ls_expo.net.max()*100:+.0f}%')
    print(f'  {n_short} short trades of {len(ls_log)} total')
    if not ls_log.empty:
        by_side = ls_log.groupby('side').ret.agg(['count', 'mean',
                                                  lambda x: (x > 0).mean()])
        by_side.columns = ['trades', 'avg_return', 'win_rate']
        print(by_side.round(3).to_string())
        by_side.to_csv(f'{OUT}/long_short_by_side.csv')
    ls_w.to_parquet(f'{OUT}/weights_long_short.parquet')
    ls_expo.to_parquet(f'{OUT}/exposure_long_short.parquet')
    ls_log.to_csv(f'{OUT}/trade_log_long_short.csv', index=False)

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
                               (f'Regime Book, {CAP_LABEL} cap', capped, capped_log),
                               ('Regime Book + class cap', diversified, div_log),
                               ('Long/short, naive mirror', mirror_book, mirror_log),
                               ('Long/short, gated shorts', ls_book, ls_log),
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
    return dict(mode=mode, stops=stops, results=res, weights=weights, book=book,
                ls_book=ls_book, ls_weights=ls_w, ls_exposure=ls_expo, ls_log=ls_log,
                diversified=diversified, div_weights=div_w, div_log=div_log,
                class_cap=best_class_cap, class_cap_sweep=cls_tab,
                ls_label=LS_LABEL, ls_ablation=ls_tab,
                long_only_is_score=long_only_score, mirror_book=mirror_book,
                mirror_log=mirror_log, mirror_exposure=mirror_expo,
                capped=capped, capped_weights=capped_w, capped_trades=capped_log,
                cap_sweep=caps, best_cap=best_cap, cap_label=CAP_LABEL,
                baseline=base, spy=spy, sixty40=sixty40, trades=tlog)


if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'sub'
    if mode == 'compare':
        summaries = {}
        for m in ('majors', 'majors_plus', 'sub'):
            print('\n' + '=' * 78 + f'\nUNIVERSE MODE: {m}\n' + '=' * 78)
            r = run(m)
            summaries[m] = r['results']
        comp = pd.concat(summaries, names=['universe'])
        comp.to_csv(f'{OUT}/universe_mode_comparison.csv')
        print('\n\nHEAD-TO-HEAD (book only)\n')
        book = comp[comp.index.get_level_values('strategy').str.startswith('Regime Book')]
        print(book[['CAGR', 'Vol', 'MaxDD', 'Sortino', 'Calmar', 'Omega',
                    'NTrades']].round(3).to_string())
    else:
        run(mode)
