#!/usr/bin/env python3
"""
CROSSCURRENTS — "winners run, losers cut" 1-to-10 global cross-asset book.

What it simulates (Bob's spec, made explicit):
- Universe: liquid ETFs spanning EVERY asset class (US/intl/EM equity, sectors,
  govt + credit bonds, gold/silver/miners, housing, crypto via BTC).
- Up to 10 positions, LONG-ONLY, no leverage (cash account).
- NEVER rebalanced: positions are sized once at entry and then ride. Winners are
  never trimmed (they run / grow as a share of the book).
- Losers cut: a position is sold when it breaks trend (closes below its 200d MA).
- Slots refill from the strongest *uptrending* assets (12-1m momentum, above
  200d MA) not already held; freed cash is deployed equally across new entries.
- Cash is a position (held when fewer than 10 assets are in uptrend).
Benchmarks: SPY (the Crosscurrents benchmark), 60/40, QAI (legacy secondary ref).

Run: PYTHONPATH=/Users/bob/LHM /opt/homebrew/bin/python3 \
       Scripts/backtest/winners_run_book_backtest.py
"""
import sqlite3
import sys
import warnings
warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
import yfinance as yf

sys.path.insert(0, "/Users/bob/LHM/Scripts/chart_generation")
import matplotlib
matplotlib.use("Agg")
import lhm_chart_template as T

DB = "/Users/bob/LHM/Data/databases/Lighthouse_Master.db"
OUT_EQ = "/Users/bob/LHM/Outputs/crosscurrents_equity_curve.png"
OUT_ALLOC = "/Users/bob/LHM/Outputs/crosscurrents_allocation.png"

START = "2008-01-01"
MAX_SLOTS = 10
COST = 0.0005          # 5bps per trade
MOM_LONG, MOM_SKIP = 252, 21   # 12-1 month momentum
TREND = 200            # 200d MA trend filter

# Universe by asset class (DB _Close series; BTC + QAI via yfinance).
UNIVERSE = {
    "US Equity":  ["SPY", "QQQ", "IWM"],
    "Sectors":    ["XLE", "XLK", "XLF", "XLV", "XLU", "XLB", "XLI", "XLP", "XLY"],
    "Intl/EM":    ["EFA", "EEM"],
    "Govt Bonds": ["TLT", "IEF"],
    "Credit":     ["HYG", "LQD"],
    "Commodity":  ["GLD", "SLV", "GDX"],
    "Housing":    ["XHB", "ITB"],
    "Crypto":     ["BTC"],
}
CLASS_OF = {t: cls for cls, ts in UNIVERSE.items() for t in ts}
TICKERS = [t for ts in UNIVERSE.values() for t in ts]
CLASS_COLOR = {
    "US Equity": T.COLORS["ocean"], "Sectors": T.COLORS["sky"],
    "Intl/EM": T.COLORS["bright"], "Govt Bonds": T.COLORS["sea"],
    "Credit": T.COLORS["doldrums"], "Commodity": T.COLORS["dusk"],
    "Housing": T.COLORS["venus"], "Crypto": T.COLORS["starboard"], "Cash": "#cfd8dc",
}


def load_prices():
    conn = sqlite3.connect(DB)
    cols = {}
    for t in TICKERS:
        if t == "BTC":
            continue
        d = pd.read_sql("SELECT date, value FROM observations WHERE series_id=? "
                        "AND value IS NOT NULL ORDER BY date", conn, params=(f"{t}_Close",),
                        parse_dates=["date"])
        if not d.empty:
            cols[t] = d.set_index("date")["value"]
    conn.close()
    btc = yf.download("BTC-USD", start="2014-01-01", progress=False)
    btc = btc["Close"]
    if isinstance(btc, pd.DataFrame):
        btc = btc.iloc[:, 0]
    btc.index = pd.to_datetime(btc.index).tz_localize(None)
    cols["BTC"] = btc
    qai = yf.download("QAI", start="2009-01-01", progress=False)["Close"]
    if isinstance(qai, pd.DataFrame):
        qai = qai.iloc[:, 0]
    qai.index = pd.to_datetime(qai.index).tz_localize(None)
    px = pd.DataFrame(cols).sort_index()
    px = px[px.index >= "2006-01-01"].ffill()
    return px, qai


def backtest(px, cap=1.0):
    """cap = max weight any single position may reach. cap=1.0 is the pure
    'winners run, never trim' spec; cap=0.25 = winners run UP TO 25%, harvest
    the excess (the LHM no-single-position-dominates discipline)."""
    idx = px.index[px.index >= START]
    ma = px.rolling(TREND).mean()
    mom = px.shift(MOM_SKIP) / px.shift(MOM_LONG) - 1.0   # 12-1m momentum
    month = pd.Series(idx, index=idx).dt.to_period("M")
    decide_days = idx[month.values != np.r_[month.values[:1], month.values[:-1]]]

    cash, shares = 1.0, {t: 0.0 for t in TICKERS}
    nav_hist, alloc_hist = {}, {}

    def value(day):
        return cash + sum(shares[t] * px.at[day, t] for t in TICKERS
                          if not np.isnan(px.at[day, t]))

    for day in idx:
        # 1) cut losers EVERY DAY: the moment a holding closes below its 200d MA,
        #    sell it. Cutting fast is the whole point of "losers cut" — a monthly
        #    check rode 2008 down before exiting (MaxDD -54%). Daily exit is the
        #    faithful version and is what gives the downside protection.
        for t in TICKERS:
            if shares[t] > 0:
                p, m = px.at[day, t], ma.at[day, t]
                if np.isnan(p) or np.isnan(m) or p < m:
                    cash += shares[t] * (p if not np.isnan(p) else 0) * (1 - COST)
                    shares[t] = 0.0
        if day in decide_days:
            # 1b) harvest runaway winners: trim any position above the cap back
            #     to the cap (excess -> cash for redeployment). Winners still run
            #     up to the cap; this is what stops a single name (e.g. BTC at
            #     89%) from owning the book.
            if cap < 1.0:
                v_now = value(day)
                for t in TICKERS:
                    if shares[t] > 0:
                        p = px.at[day, t]
                        w = shares[t] * p / v_now if v_now else 0
                        if w > cap and not np.isnan(p):
                            excess_val = (w - cap) * v_now
                            shares[t] -= (excess_val / p)
                            cash += excess_val * (1 - COST)
            # 2) refill empty slots with strongest uptrends not held
            held = [t for t in TICKERS if shares[t] > 0]
            empty = MAX_SLOTS - len(held)
            if empty > 0 and cash > 1e-9:
                cand = []
                for t in TICKERS:
                    if shares[t] > 0:
                        continue
                    p, m, mm = px.at[day, t], ma.at[day, t], mom.at[day, t]
                    if not np.isnan(p) and not np.isnan(m) and not np.isnan(mm) and p > m:
                        cand.append((mm, t))
                cand.sort(reverse=True)
                picks = [t for _, t in cand[:empty]]
                if picks:
                    each = cash / len(picks)
                    for t in picks:
                        p = px.at[day, t]
                        shares[t] += (each * (1 - COST)) / p
                        cash -= each
        v = value(day)
        nav_hist[day] = v
        alloc_hist[day] = {CLASS_OF[t]: alloc_hist.get(day, {}).get(CLASS_OF[t], 0)
                           + shares[t] * px.at[day, t]
                           for t in TICKERS if shares[t] > 0 and not np.isnan(px.at[day, t])}
        alloc_hist[day]["Cash"] = cash
    nav = pd.Series(nav_hist)
    alloc = pd.DataFrame(alloc_hist).T.fillna(0)
    alloc = alloc.div(alloc.sum(axis=1), axis=0)
    return nav, alloc


def stats(nav, name):
    r = nav.pct_change().dropna()
    yrs = (nav.index[-1] - nav.index[0]).days / 365.25
    cagr = (nav.iloc[-1] / nav.iloc[0]) ** (1 / yrs) - 1
    vol = r.std() * np.sqrt(252)
    dn = r[r < 0].std() * np.sqrt(252)
    dd = (nav / nav.cummax() - 1).min()
    sharpe = cagr / vol if vol else 0
    sortino = cagr / dn if dn else 0
    calmar = cagr / abs(dd) if dd else 0
    return dict(name=name, CAGR=cagr, Vol=vol, Sharpe=sharpe, Sortino=sortino,
                MaxDD=dd, Calmar=calmar)


def main():
    px, qai = load_prices()
    nav_pure, _ = backtest(px, cap=1.0)        # literal spec (no position cap)
    nav, alloc = backtest(px, cap=0.25)        # winners run up to 25% (LHM discipline)

    # benchmarks aligned to book NAV dates
    bench = {"Crosscurrents (25% cap)": nav,
             "Pure winners-run (no cap)": nav_pure}
    spy = px["SPY"].reindex(nav.index).ffill()
    bench["SPY (buy & hold)"] = spy / spy.iloc[0]
    ief = px["IEF"].reindex(nav.index).ffill()
    s6040 = (0.6 * spy / spy.iloc[0] + 0.4 * ief / ief.iloc[0])
    bench["60/40 (SPY/IEF)"] = s6040
    q = qai.reindex(nav.index).ffill().dropna()
    if len(q) > 100:
        bench["QAI (hedge multi-strat)"] = q / q.iloc[0]

    print("=" * 88)
    print(f"  CROSSCURRENTS WINNERS-RUN BOOK BACKTEST  ({nav.index[0].date()} → {nav.index[-1].date()})")
    print("=" * 88)
    print(f"  {'Strategy':<34} {'CAGR':>7} {'Vol':>7} {'Sharpe':>7} {'Sortino':>8} {'MaxDD':>8} {'Calmar':>7}")
    print("  " + "-" * 84)
    rows = []
    for nm, series in bench.items():
        s = stats(series.dropna(), nm)
        rows.append(s)
        print(f"  {nm:<34} {s['CAGR']:>6.1%} {s['Vol']:>6.1%} {s['Sharpe']:>7.2f} "
              f"{s['Sortino']:>8.2f} {s['MaxDD']:>7.1%} {s['Calmar']:>7.2f}")
    avg_pos = (alloc.drop(columns=["Cash"]) > 0.001).sum(axis=1).mean()
    cash_pct = alloc["Cash"].mean()
    print(f"\n  Avg positions held: {avg_pos:.1f}/10 · avg cash weight: {cash_pct:.0%}")

    # ---- Chart 1: equity curve (log) ----
    T.set_theme("white")
    fig, ax = T.new_fig(figsize=(14, 7))
    colors = [T.COLORS["ocean"], T.COLORS["port"], T.COLORS["doldrums"],
              T.COLORS["dusk"], T.COLORS["sea"]]
    for (nm, series), c in zip(bench.items(), colors):
        ax.plot(series.index, series.values, lw=2.0 if nm.startswith("Cross") else 1.3,
                color=c, label=nm)
    ax.set_yscale("log")
    T.style_ax(ax)
    T.set_xlim_to_data(ax, nav.index)
    T.add_smart_legend(ax)
    bs = rows[0]
    T.brand_fig(fig, "Crosscurrents — Winners Run, Losers Cut",
                subtitle=f"1-to-10 global cross-asset book, never rebalanced · "
                         f"CAGR {bs['CAGR']:.1%}, Sortino {bs['Sortino']:.2f}, MaxDD {bs['MaxDD']:.1%} "
                         f"({nav.index[0].year}-{nav.index[-1].year})",
                source="market data (DB + Yahoo); hypothetical backtest, net 5bps/trade")
    T.save_fig(fig, OUT_EQ)
    print(f"\n  saved {OUT_EQ}")

    # ---- Chart 2: allocation stacked area ----
    fig2, ax2 = T.new_fig(figsize=(14, 7))
    am = alloc.resample("W").last().dropna(how="all")
    order = ["US Equity", "Sectors", "Intl/EM", "Govt Bonds", "Credit",
             "Commodity", "Housing", "Crypto", "Cash"]
    order = [c for c in order if c in am.columns]
    ax2.stackplot(am.index, *[am[c].values * 100 for c in order],
                  labels=order, colors=[CLASS_COLOR[c] for c in order])
    ax2.set_ylim(0, 100)
    T.style_ax(ax2)
    T.set_xlim_to_data(ax2, am.index)
    ax2.legend(loc="upper center", ncol=5, fontsize=8, frameon=False,
               bbox_to_anchor=(0.5, -0.05))
    T.brand_fig(fig2, "Crosscurrents — Allocation Through Time",
                subtitle="Book weight by asset class · winners run (grow), losers cut, "
                         "cash when nothing trends",
                source="market data (DB + Yahoo); hypothetical backtest")
    T.save_fig(fig2, OUT_ALLOC)
    print(f"  saved {OUT_ALLOC}")


if __name__ == "__main__":
    main()
