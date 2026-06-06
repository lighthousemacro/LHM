"""
LHM Stop Optimization Backtest  (v2 — concentrated book, per-asset-class)
========================================================================
Find the BEST stop (or combination) PER ASSET CLASS for the Crosscurrents book,
maximizing risk/reward while PRESERVING the fat right tail (the high payoff
ratio from letting winners run). Cash-only / long-only / no leverage.

The three stops are CANDIDATES to test, not a mandate to use all three:
  1. 200d break    — close < 200d_SMA * (1 - X)        [X tight: 0.5% / 2%]
  2. ATR chandelier— close < trailing-22d-high - k*ATR [k: 2.0 .. 3.5]
  3. Rel-trend QAI — RS = close/QAI < its L-day SMA     [L: 21 / 63 / 126]
We search every non-empty subset {200d, atr, rs} x its params, per asset class.

Two stages:
  STAGE 1 — per asset class, equal-weight-ACTIVE across ALL class names (many
            trades -> robust stop estimate). Rank stop-sets by a payoff-
            preserving blend (Sortino, Calmar, Omega, Payoff, Expectancy).
  STAGE 2 — the real CONCENTRATED book: hold the top-10 names by relative
            strength across the whole universe, applying each name's
            class-specific best stop. Compare to a plain-200d top-10 baseline.
            This is the "10 holdings / concentration" read, with payoff.

Entry is fixed so the search is about STOPS: close>200d AND RS(vs QAI)>RS_63d.
Walk-forward: optimize IS (<=2020), validate OOS (2021+). No look-ahead.
OOS numbers are NOT externally citable until separately verified.
"""
import os, pickle, itertools, warnings
import numpy as np
import pandas as pd
warnings.filterwarnings("ignore")

OUT = "/Users/bob/LHM/Outputs/stop_optimization"
os.makedirs(OUT, exist_ok=True)
CACHE = f"{OUT}/price_cache.pkl"
ANN, IS_END, START = 252, "2020-12-31", "2013-01-01"
OOS_LO, OOS_HI = "2021-01-01", "2026-12-31"
BENCH, K_BOOK = "QAI", 10

ETFS = ("XLK XLF XLV XLY XLP XLE XLI XLB XLU XLRE XLC SPY QQQ DIA IWM MDY EEM "
        "EFA VEA VWO TLT IEF SHY LQD HYG TIP GLD SLV GDX DBC USO MTUM QUAL VLUE "
        "USMV SPLV VTV VUG SMH XBI ITB KRE XHB XOP").split()
STOCKS = ("AAPL MSFT NVDA AMZN GOOGL META TSLA AVGO JPM V MA UNH HD PG XOM CVX "
          "LLY ABBV MRK PEP KO COST WMT BAC WFC GS MS C ORCL CRM ADBE AMD INTC "
          "CSCO QCOM TXN IBM NFLX DIS CMCSA T VZ TMUS NKE MCD SBUX LOW CAT DE BA "
          "HON UNP UPS GE MMM LMT RTX NEE DUK SO PFE TMO ABT DHR BMY AMGN GILD "
          "CVS LIN").split()
UNIVERSE = ETFS + STOCKS

BONDS = set("TLT IEF SHY LQD HYG TIP".split())
COMMOD = set("GLD SLV GDX DBC USO".split())
INTL = set("EEM EFA VEA VWO".split())
def asset_class(t):
    if t in BONDS: return "bonds"
    if t in COMMOD: return "commodities"
    if t in INTL: return "intl_equity"
    return "us_equity"

SUBSETS = [("200d",), ("atr",), ("rs",), ("200d", "atr"), ("200d", "rs"),
           ("atr", "rs"), ("200d", "atr", "rs")]
X_GRID, K_GRID, L_GRID = [0.005, 0.02], [2.0, 2.5, 3.0, 3.5], [21, 63, 126]


def fetch():
    if os.path.exists(CACHE):
        return pickle.load(open(CACHE, "rb"))
    import yfinance as yf
    tickers = sorted(set(UNIVERSE + [BENCH]))
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
    pickle.dump(data, open(CACHE, "wb"))
    return data


def atr(df, n=14):
    h, l, c = df["High"], df["Low"], df["Close"]
    pc = c.shift(1)
    tr = pd.concat([h - l, (h - pc).abs(), (l - pc).abs()], axis=1).max(axis=1)
    return tr.rolling(n).mean()


def precompute(data):
    qai = data[BENCH]["Close"]
    pre = {}
    for t in UNIVERSE:
        if t not in data:
            continue
        df = data[t]; c = df["Close"]
        sma200 = c.rolling(200).mean()
        rs = (c / qai.reindex(c.index)).dropna()
        idx = rs.index
        c, df, sma200 = c.loc[idx], df.loc[idx], sma200.loc[idx]
        if len(c) < 400:
            continue
        a, trail = atr(df), c.rolling(22).max()
        entry = ((c > sma200) & (rs > rs.rolling(63).mean())).values
        below200 = {X: (c < sma200 * (1 - X)).values for X in X_GRID}
        atrk = {k: (c < (trail - k * a)).values for k in K_GRID}
        rsl = {L: (rs < rs.rolling(L).mean()).values for L in L_GRID}
        pre[t] = dict(cls=asset_class(t), index=idx, close=c.values,
                      ret=c.pct_change().fillna(0).values, rs=rs.values,
                      entry=entry, below200=below200, atrk=atrk, rsl=rsl)
    return pre


def exit_array(p, subset, X, k, L):
    n = len(p["close"]); ex = np.zeros(n, dtype=bool)
    if "200d" in subset: ex |= p["below200"][X]
    if "atr" in subset:  ex |= p["atrk"][k]
    if "rs" in subset:   ex |= p["rsl"][L]
    return ex


def simulate(entry, exit_sig, close, cooldown=3):
    n = len(entry); pos = np.zeros(n); trades = []
    in_pos = False; cd = 0; ei = -1
    for i in range(n):
        if in_pos:
            pos[i] = 1
            if exit_sig[i] or i == n - 1:
                in_pos = False; cd = cooldown; trades.append(close[i] / close[ei] - 1)
        elif cd > 0:
            cd -= 1
        elif entry[i]:
            in_pos = True; pos[i] = 1; ei = i
    return pos, trades


def book_eq_active(class_pre, subset, X, k, L):
    cols = {}; trades = []
    for t, p in class_pre.items():
        pos, tr = simulate(p["entry"], exit_array(p, subset, X, k, L), p["close"])
        posS = np.r_[0.0, pos[:-1]]
        cols[t] = pd.Series(np.where(posS > 0, posS * p["ret"], np.nan), index=p["index"])
        trades.extend(tr)
    book = pd.DataFrame(cols).mean(axis=1).fillna(0.0)
    book = book.loc[book.ne(0).idxmax():] if (book != 0).any() else book
    return book, np.array(trades)


def metrics(book, trades, lo=None, hi=None):
    b = book
    if lo: b = b[(b.index >= lo) & (b.index <= hi)]
    if len(b) < 50: return None
    eq = (1 + b).cumprod(); yrs = len(b) / ANN
    cagr = eq.iloc[-1] ** (1 / yrs) - 1
    dd = (eq / eq.cummax() - 1).min()
    ds = b[b < 0]
    sortino = (b.mean() * ANN) / (ds.std() * np.sqrt(ANN)) if len(ds) else np.nan
    calmar = cagr / abs(dd) if dd < 0 else np.nan
    omega = b[b > 0].sum() / (-b[b < 0].sum()) if (b < 0).any() else np.nan
    tr = np.asarray(trades); w = tr[tr > 0]; l = tr[tr < 0]
    payoff = w.mean() / abs(l.mean()) if len(w) and len(l) else np.nan
    pf = w.sum() / abs(l.sum()) if len(l) and l.sum() != 0 else np.nan
    return dict(CAGR=cagr, MaxDD=dd, Sortino=sortino, Calmar=calmar, Omega=omega,
                Payoff=payoff, Expectancy=tr.mean() if len(tr) else np.nan,
                ProfitFactor=pf, WinRate=len(w)/len(tr) if len(tr) else np.nan,
                NTrades=len(tr))


def concentrated_book(pre, exit_of, K=K_BOOK):
    """Top-K-by-RS concentrated long-only book. exit_of: ticker->bool exit array."""
    dates = pd.DatetimeIndex(sorted(set().union(*[set(p["index"]) for p in pre.values()])))
    di = {d: i for i, d in enumerate(dates)}
    n, m = len(dates), len(pre); tks = list(pre)
    RET = np.full((n, m), np.nan); ENT = np.zeros((n, m)); RS = np.full((n, m), np.nan)
    EX = np.zeros((n, m)); CL = np.full((n, m), np.nan)
    for j, t in enumerate(tks):
        p = pre[t]; rows = [di[d] for d in p["index"]]
        RET[rows, j] = p["ret"]; ENT[rows, j] = p["entry"]; RS[rows, j] = p["rs"]
        CL[rows, j] = p["close"]; EX[rows, j] = exit_of[t]
    held = {}; cd = {}; prev = []; port = np.zeros(n); trades = []
    for i in range(n):
        if prev:
            rr = RET[i, prev]; rr = rr[~np.isnan(rr)]
            port[i] = rr.mean() if len(rr) else 0.0
        for t in list(cd):
            cd[t] -= 1
            if cd[t] <= 0: del cd[t]
        for j in list(held):
            if np.isnan(CL[i, j]) or EX[i, j] == 1 or i == n - 1:
                if not np.isnan(CL[i, j]): trades.append(CL[i, j] / held[j] - 1)
                del held[j]; cd[j] = 3
        if len(held) < K:
            cand = [(RS[i, j], j) for j in range(m)
                    if j not in held and j not in cd and ENT[i, j] == 1 and not np.isnan(RS[i, j])]
            cand.sort(reverse=True)
            for _, j in cand[:K - len(held)]:
                held[j] = CL[i, j]
        prev = list(held)
    return pd.Series(port, index=dates), np.array(trades)


def objective(m):
    """Payoff-preserving blend: reward Sortino, Calmar, Omega, Payoff, Expectancy."""
    if m is None or m["NTrades"] < 20: return -1e9
    vals = [m["Sortino"], m["Calmar"], m["Omega"], np.log1p(max(m["Payoff"], 0)),
            m["Expectancy"] * 100]
    return float(np.nansum(vals))


def run():
    data = fetch(); pre = precompute(data)
    classes = {}
    for t, p in pre.items():
        classes.setdefault(p["cls"], {})[t] = p
    print(f"Universe: {len(pre)} names across {len(classes)} classes: "
          + ", ".join(f"{c}({len(v)})" for c, v in classes.items()) + "\n")

    # ---------- STAGE 1: best stop per asset class ----------
    best_by_class = {}; rows = []
    for cls, cp in classes.items():
        scored = []
        for subset in SUBSETS:
            xs = X_GRID if "200d" in subset else [None]
            ks = K_GRID if "atr" in subset else [None]
            ls = L_GRID if "rs" in subset else [None]
            for X, k, L in itertools.product(xs, ks, ls):
                book, trades = book_eq_active(cp, subset, X, k, L)
                m_is = metrics(book, trades, START, IS_END)
                sc = objective(m_is)
                scored.append((sc, subset, X, k, L, book, trades, m_is))
        scored.sort(key=lambda z: z[0], reverse=True)
        sc, subset, X, k, L, book, trades, m_is = scored[0]
        m_oos = metrics(book, trades, OOS_LO, OOS_HI)
        best_by_class[cls] = (subset, X, k, L)
        # baseline for this class: 200d-only, tight 0.5%
        bbook, btr = book_eq_active(cp, ("200d",), 0.005, None, None)
        b_is = metrics(bbook, btr, START, IS_END)
        rows.append((cls, subset, X, k, L, m_is, m_oos, b_is))

    print("=" * 92)
    print("STAGE 1 — BEST STOP PER ASSET CLASS (equal-weight-active, payoff-preserving objective)")
    print("=" * 92)
    for cls, subset, X, k, L, m_is, m_oos, b_is in rows:
        tag = "+".join(subset)
        params = []
        if "200d" in subset: params.append(f"X={X:.3f}")
        if "atr" in subset: params.append(f"k={k}")
        if "rs" in subset: params.append(f"L={int(L)}")
        print(f"\n[{cls}]  BEST: {tag}  ({', '.join(params)})")
        print(f"   IS : Sortino {m_is['Sortino']:.2f} | Calmar {m_is['Calmar']:.2f} | "
              f"Omega {m_is['Omega']:.2f} | Payoff {m_is['Payoff']:.1f}x | "
              f"CAGR {m_is['CAGR']*100:.1f}% | MaxDD {m_is['MaxDD']*100:.0f}% | n={m_is['NTrades']}")
        if m_oos:
            print(f"   OOS: Sortino {m_oos['Sortino']:.2f} | Calmar {m_oos['Calmar']:.2f} | "
                  f"Omega {m_oos['Omega']:.2f} | Payoff {m_oos['Payoff']:.1f}x | CAGR {m_oos['CAGR']*100:.1f}%")
        print(f"   vs 200d-only baseline IS: Sortino {b_is['Sortino']:.2f} | "
              f"Calmar {b_is['Calmar']:.2f} | Payoff {b_is['Payoff']:.1f}x | CAGR {b_is['CAGR']*100:.1f}%")

    # ---------- STAGE 2: concentrated top-10 book ----------
    exit_best = {t: exit_array(p, *best_by_class[p["cls"]]) for t, p in pre.items()}
    exit_200 = {t: exit_array(p, ("200d",), 0.005, None, None) for t, p in pre.items()}
    cb, ctr = concentrated_book(pre, exit_best)
    bb, btr = concentrated_book(pre, exit_200)
    cm_is, cm_oos = metrics(cb, ctr, START, IS_END), metrics(cb, ctr, OOS_LO, OOS_HI)
    bm_is, bm_oos = metrics(bb, btr, START, IS_END), metrics(bb, btr, OOS_LO, OOS_HI)

    print("\n" + "=" * 92)
    print(f"STAGE 2 — CONCENTRATED TOP-{K_BOOK} BOOK (RS-ranked, long-only, cash-only)")
    print("=" * 92)
    def line(tag, m):
        print(f"  {tag:32s} Sortino {m['Sortino']:.2f} | Calmar {m['Calmar']:.2f} | "
              f"Omega {m['Omega']:.2f} | Payoff {m['Payoff']:.1f}x | PF {m['ProfitFactor']:.2f} | "
              f"Win {m['WinRate']*100:.0f}% | CAGR {m['CAGR']*100:.1f}% | MaxDD {m['MaxDD']*100:.0f}% | n={m['NTrades']}")
    print("\nIN-SAMPLE (<=2020):")
    line("per-class optimized stops", cm_is); line("plain 200d-only baseline", bm_is)
    print("\nOUT-OF-SAMPLE (2021+):")
    line("per-class optimized stops", cm_oos); line("plain 200d-only baseline", bm_oos)

    # save equity curves
    pd.DataFrame({"optimized": (1+cb).cumprod(), "baseline_200d": (1+bb).cumprod()}).to_csv(
        f"{OUT}/concentrated_equity.csv")
    print(f"\nEquity curves: {OUT}/concentrated_equity.csv")
    return best_by_class, cb, bb


if __name__ == "__main__":
    run()
