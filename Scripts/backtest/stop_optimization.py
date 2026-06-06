"""
LHM Stop Optimization Backtest
==============================
Optimize the three LHM technical stops to maximize risk/reward (downside
minimization AND upside capture), scored on Sortino / Calmar / Omega.

The three technical stops (each a parameter to optimize):
  1. 200d break  — exit when close < 200d_SMA * (1 - X). TIGHT buffer (~1%).
  2. ATR chandelier — exit when close < (trailing-22d high) - k * ATR(14).
  3. Negative relative-trend vs QAI — exit when RS = close/QAI falls below its
     L-day SMA (the position stops beating the benchmark).

Technical stops are the only exit here (thesis stop is discretionary, not
backtestable). Entry is held FIXED so the optimization is about the STOPS:
  entry = close > 200d_SMA AND RS(vs QAI) > RS_63d_SMA  (a trend + relative-
  strength entry), with a 3-day cooldown after a stop to limit churn.

Benchmark = QAI (IQ Hedge Multi-Strategy Tracker ETF). Walk-forward: optimize
on the in-sample window, validate out-of-sample. No look-ahead (all signals use
trailing windows; positions earn next-day returns).

OOS numbers are NOT externally citable until separately verified.
"""
import os, sys, pickle, itertools, warnings
import numpy as np
import pandas as pd
warnings.filterwarnings("ignore")

OUT = "/Users/bob/LHM/Outputs/stop_optimization"
os.makedirs(OUT, exist_ok=True)
CACHE = f"{OUT}/price_cache.pkl"
ANN = 252
IS_END = "2020-12-31"      # in-sample through 2020; OOS 2021+
START = "2013-01-01"

BENCH = "QAI"
ETFS = ("XLK XLF XLV XLY XLP XLE XLI XLB XLU XLRE XLC SPY QQQ DIA IWM MDY EEM "
        "EFA VEA VWO TLT IEF SHY LQD HYG TIP GLD SLV GDX DBC USO MTUM QUAL VLUE "
        "USMV SPLV VTV VUG SMH XBI ITB KRE XHB XOP").split()
STOCKS = ("AAPL MSFT NVDA AMZN GOOGL META TSLA AVGO JPM V MA UNH HD PG XOM CVX "
          "LLY ABBV MRK PEP KO COST WMT BAC WFC GS MS C ORCL CRM ADBE AMD INTC "
          "CSCO QCOM TXN IBM NFLX DIS CMCSA T VZ TMUS NKE MCD SBUX LOW CAT DE BA "
          "HON UNP UPS GE MMM LMT RTX NEE DUK SO PFE TMO ABT DHR BMY AMGN GILD "
          "CVS LIN").split()
UNIVERSE = ETFS + STOCKS

# Stop parameter grids
X_GRID = [0.0, 0.005, 0.01, 0.015, 0.02, 0.03]   # 200d buffer (tight)
K_GRID = [2.0, 2.5, 3.0, 3.5, 4.0]               # ATR chandelier multiple
L_GRID = [21, 42, 63, 126]                        # relative-trend SMA lookback


def fetch():
    if os.path.exists(CACHE):
        with open(CACHE, "rb") as f:
            return pickle.load(f)
    import yfinance as yf
    tickers = sorted(set(UNIVERSE + [BENCH]))
    print(f"Downloading {len(tickers)} tickers via yfinance...")
    raw = yf.download(tickers, start=START, auto_adjust=True, progress=False,
                      group_by="ticker", threads=True)
    data = {}
    for t in tickers:
        try:
            df = raw[t][["High", "Low", "Close"]].dropna()
            if len(df) > 300:
                data[t] = df
        except Exception:
            pass
    with open(CACHE, "wb") as f:
        pickle.dump(data, f)
    print(f"Cached {len(data)} tickers with usable history.")
    return data


def atr(df, n=14):
    h, l, c = df["High"], df["Low"], df["Close"]
    pc = c.shift(1)
    tr = pd.concat([h - l, (h - pc).abs(), (l - pc).abs()], axis=1).max(axis=1)
    return tr.rolling(n).mean()


def precompute(data):
    """Per-ticker: aligned close, entry signal, and the per-param stop-trigger
    boolean arrays (all vectorized, trailing-window only)."""
    qai = data[BENCH]["Close"]
    pre = {}
    for t in UNIVERSE:
        if t not in data:
            continue
        df = data[t]
        c = df["Close"]
        sma200 = c.rolling(200).mean()
        rs = (c / qai.reindex(c.index)).dropna()
        c = c.loc[rs.index]; df = df.loc[rs.index]; sma200 = sma200.loc[rs.index]
        if len(c) < 400:
            continue
        rs63 = rs.rolling(63).mean()
        a = atr(df)
        trail_hi = c.rolling(22).max()
        entry = (c > sma200) & (rs > rs63)
        # per-param stop booleans
        stop200 = {X: (c < sma200 * (1 - X)).values for X in X_GRID}
        atrk = {k: (c < (trail_hi - k * a)).values for k in K_GRID}
        rsl = {L: (rs < rs.rolling(L).mean()).values for L in L_GRID}
        ret = c.pct_change().values
        pre[t] = dict(index=c.index, ret=ret, entry=entry.values.astype(bool),
                      stop200=stop200, atrk=atrk, rsl=rsl, close=c.values)
    return pre


def simulate(p, X, k, L, cooldown=3):
    """Return (daily position array, list of per-trade returns) for one combo."""
    entry = p["entry"]
    exit_sig = p["stop200"][X] | p["atrk"][k] | p["rsl"][L]
    n = len(entry)
    pos = np.zeros(n)
    trades = []
    in_pos = False; cd = 0; ent_i = -1
    close = p["close"]
    for i in range(n):
        if in_pos:
            pos[i] = 1
            if exit_sig[i] or i == n - 1:
                in_pos = False; cd = cooldown
                trades.append(close[i] / close[ent_i] - 1.0)
        else:
            if cd > 0:
                cd -= 1
            elif entry[i] and not (np.isnan(close[i])):
                in_pos = True; pos[i] = 1; ent_i = i
    return pos, trades


def strat_returns(pre, X, k, L):
    """Equal-weight daily book return across the universe + pooled trades."""
    cols = {}
    all_trades = []
    for t, p in pre.items():
        pos, trades = simulate(p, X, k, L)
        # position decided at close t earns return t+1
        sr = pd.Series(np.r_[0.0, pos[:-1]] * np.nan_to_num(p["ret"]), index=p["index"])
        cols[t] = sr
        all_trades.extend(trades)
    book = pd.DataFrame(cols).mean(axis=1).dropna()   # equal-weight, cash when flat
    return book, np.array(all_trades)


def metrics(book, trades):
    if len(book) < 50:
        return None
    eq = (1 + book).cumprod()
    yrs = len(book) / ANN
    cagr = eq.iloc[-1] ** (1 / yrs) - 1
    dd = (eq / eq.cummax() - 1).min()
    downside = book[book < 0]
    sortino = (book.mean() * ANN) / (downside.std() * np.sqrt(ANN)) if len(downside) else np.nan
    calmar = cagr / abs(dd) if dd < 0 else np.nan
    pos_sum = book[book > 0].sum(); neg_sum = -book[book < 0].sum()
    omega = pos_sum / neg_sum if neg_sum > 0 else np.nan
    wins = trades[trades > 0]; losses = trades[trades < 0]
    win_rate = len(wins) / len(trades) if len(trades) else np.nan
    payoff = wins.mean() / abs(losses.mean()) if len(wins) and len(losses) else np.nan
    expectancy = trades.mean() if len(trades) else np.nan
    return dict(CAGR=cagr, MaxDD=dd, Sortino=sortino, Calmar=calmar, Omega=omega,
                WinRate=win_rate, Payoff=payoff, Expectancy=expectancy,
                NTrades=len(trades))


def window(book, trades, lo, hi):
    b = book[(book.index >= lo) & (book.index <= hi)]
    return b


def run():
    data = fetch()
    print(f"Universe with data: {sum(1 for t in UNIVERSE if t in data)}/{len(UNIVERSE)}")
    pre = precompute(data)
    print(f"Precomputed {len(pre)} tickers. Grid = {len(X_GRID)*len(K_GRID)*len(L_GRID)} combos.\n")

    rows = []
    series_cache = {}
    combos = list(itertools.product(X_GRID, K_GRID, L_GRID))
    for n, (X, k, L) in enumerate(combos, 1):
        book, trades = strat_returns(pre, X, k, L)
        series_cache[(X, k, L)] = book
        m_is = metrics(window(book, trades, START, IS_END), trades)
        if m_is is None:
            continue
        rows.append(dict(X=X, k=k, L=L, **{f"IS_{kk}": vv for kk, vv in m_is.items()}))
        if n % 20 == 0:
            print(f"  {n}/{len(combos)} combos done")

    res = pd.DataFrame(rows)
    # rank-blend the three objective metrics on IS (higher better)
    for col in ["IS_Sortino", "IS_Calmar", "IS_Omega"]:
        res[col + "_rank"] = res[col].rank(ascending=True)
    res["IS_blend"] = res[["IS_Sortino_rank", "IS_Calmar_rank", "IS_Omega_rank"]].mean(axis=1)
    res = res.sort_values("IS_blend", ascending=False).reset_index(drop=True)

    # OOS metrics for the top IS combos + baseline
    def full_metrics(X, k, L, lo, hi):
        book = series_cache[(X, k, L)]
        # recompute trades windowed is overkill; use full-trade metrics on windowed book
        b = window(book, np.array([]), lo, hi)
        if len(b) < 50:
            return None
        eq = (1 + b).cumprod(); yrs = len(b) / ANN
        cagr = eq.iloc[-1] ** (1 / yrs) - 1
        dd = (eq / eq.cummax() - 1).min()
        ds = b[b < 0]
        sortino = (b.mean() * ANN) / (ds.std() * np.sqrt(ANN)) if len(ds) else np.nan
        calmar = cagr / abs(dd) if dd < 0 else np.nan
        omega = b[b > 0].sum() / (-b[b < 0].sum()) if (b < 0).any() else np.nan
        return dict(CAGR=cagr, MaxDD=dd, Sortino=sortino, Calmar=calmar, Omega=omega)

    oos_lo = "2021-01-01"; oos_hi = "2026-12-31"
    top = res.head(5).copy()
    for _, r in top.iterrows():
        m = full_metrics(r.X, r.k, r.L, oos_lo, oos_hi)
        for kk, vv in (m or {}).items():
            res.loc[r.name, f"OOS_{kk}"] = vv

    # baseline: plain 200d-close stop only (X=0, ATR off via huge k, RS off via L=huge)
    # emulate "200d only" by using X=0 and disabling the other two:
    base_book, base_trades = strat_returns_baseline(pre)
    base_is = metrics(window(base_book, base_trades, START, IS_END), base_trades)
    base_oos = full_metrics_series(base_book, oos_lo, oos_hi)

    res.to_csv(f"{OUT}/grid_results.csv", index=False)

    print("\n" + "=" * 78)
    print("TOP 5 STOP PARAM SETS  (ranked by IS blend of Sortino/Calmar/Omega)")
    print("=" * 78)
    show = ["X", "k", "L", "IS_Sortino", "IS_Calmar", "IS_Omega", "IS_CAGR",
            "IS_MaxDD", "IS_WinRate", "IS_Payoff", "OOS_Sortino", "OOS_Calmar",
            "OOS_Omega", "OOS_CAGR", "OOS_MaxDD"]
    with pd.option_context("display.width", 200, "display.max_columns", 30):
        print(res[show].head(5).round(3).to_string(index=False))

    print("\nBASELINE (plain 200d-close stop only, same entry):")
    print("  IS :", {kk: round(vv, 3) for kk, vv in base_is.items()
                     if kk in ("Sortino", "Calmar", "Omega", "CAGR", "MaxDD", "WinRate", "Payoff")})
    print("  OOS:", {kk: round(vv, 3) for kk, vv in (base_oos or {}).items()})

    best = res.iloc[0]
    print("\n" + "=" * 78)
    print(f"WINNER (IS-optimal): X={best.X:.3f} ({best.X*100:.1f}% below 200d), "
          f"k={best.k} ATR, L={int(best.L)}d relative-trend")
    print(f"  IS  Sortino {best.IS_Sortino:.2f} | Calmar {best.IS_Calmar:.2f} | "
          f"Omega {best.IS_Omega:.2f} | CAGR {best.IS_CAGR*100:.1f}% | MaxDD {best.IS_MaxDD*100:.1f}%")
    if "OOS_Sortino" in best and pd.notna(best.OOS_Sortino):
        print(f"  OOS Sortino {best.OOS_Sortino:.2f} | Calmar {best.OOS_Calmar:.2f} | "
              f"Omega {best.OOS_Omega:.2f} | CAGR {best.OOS_CAGR*100:.1f}% | MaxDD {best.OOS_MaxDD*100:.1f}%")
    print(f"\nvs baseline IS Sortino {base_is['Sortino']:.2f} / Calmar {base_is['Calmar']:.2f} "
          f"/ Omega {base_is['Omega']:.2f}")
    print(f"Results CSV: {OUT}/grid_results.csv")
    return res, best, base_is, base_oos, series_cache


def strat_returns_baseline(pre):
    """200d-close stop only (X=0), ATR and RS stops disabled."""
    cols = {}; all_trades = []
    for t, p in pre.items():
        entry = p["entry"]; exit_sig = p["stop200"][0.0]
        n = len(entry); pos = np.zeros(n); close = p["close"]
        in_pos = False; cd = 0; ent_i = -1
        for i in range(n):
            if in_pos:
                pos[i] = 1
                if exit_sig[i] or i == n - 1:
                    in_pos = False; cd = 3; all_trades.append(close[i]/close[ent_i]-1)
            else:
                if cd > 0: cd -= 1
                elif entry[i]: in_pos = True; pos[i] = 1; ent_i = i
        cols[t] = pd.Series(np.r_[0.0, pos[:-1]] * np.nan_to_num(p["ret"]), index=p["index"])
    book = pd.DataFrame(cols).mean(axis=1).dropna()
    return book, np.array(all_trades)


def full_metrics_series(book, lo, hi):
    b = book[(book.index >= lo) & (book.index <= hi)]
    if len(b) < 50: return None
    eq = (1 + b).cumprod(); yrs = len(b)/ANN
    cagr = eq.iloc[-1]**(1/yrs)-1; dd = (eq/eq.cummax()-1).min()
    ds = b[b < 0]
    return dict(Sortino=(b.mean()*ANN)/(ds.std()*np.sqrt(ANN)) if len(ds) else np.nan,
                Calmar=cagr/abs(dd) if dd < 0 else np.nan,
                Omega=b[b > 0].sum()/(-b[b < 0].sum()) if (b < 0).any() else np.nan,
                CAGR=cagr, MaxDD=dd)


if __name__ == "__main__":
    res, best, base_is, base_oos, series = run()
