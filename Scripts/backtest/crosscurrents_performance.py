#!/usr/bin/env python3
"""
crosscurrents_performance.py — risk-adjusted tear sheet for the live Crosscurrents book.

The book went LIVE 2026-05-08 (Fri, funded) and the first trade was 2026-05-11 (Mon).
This reconstructs daily NAV from an actual trade ledger, marks it against daily
closes, and computes the LHM objective metrics vs QAI (primary) + secondaries.

Give it the real ledger and it produces the audited risk-adjusted record. Until
then it runs on whatever CSV you point it at.

LEDGER CSV format (one row per fill):
    date,ticker,action,shares,price
    2026-05-11,GLD,BUY,12.0,434.65
    2026-05-11,XLP,BUY,300,83.37
    2026-05-11,SHY,BUY,400,81.98
    2026-06-09,GLD,SELL,12.0,390.78
(action = BUY or SELL; price = your actual fill. Cash is inferred from the fills
and the starting capital. Idle cash earns a bill rate, default ~4%/yr.)

Usage:
    python crosscurrents_performance.py LEDGER.csv --capital 100000 --inception 2026-05-08
    python crosscurrents_performance.py --selftest      # validates the engine on a synthetic ledger
"""
from __future__ import annotations
import argparse, sys, io
import numpy as np, pandas as pd

BENCHES = {"QAI": "QAI (primary)", "SPY": "SPY", "QQQ": "QQQ", "DIA": "Dow", "BTC-USD": "BTC"}
TRADING_DAYS = 252
RF_ANNUAL = 0.04            # ~T-bill; used for Sharpe and idle-cash accrual


def prices(tickers, start, end):
    import yfinance as yf
    df = yf.download(list(tickers), start=start, end=end, auto_adjust=True,
                     progress=False)["Close"]
    if isinstance(df, pd.Series):
        df = df.to_frame(tickers[0] if not hasattr(tickers, "__len__") else list(tickers)[0])
    return df.ffill().dropna(how="all")


def build_nav(ledger: pd.DataFrame, capital: float, inception: str) -> pd.Series:
    ledger = ledger.copy()
    ledger["date"] = pd.to_datetime(ledger["date"])
    ledger["signed"] = np.where(ledger["action"].str.upper() == "SELL", -1, 1) * ledger["shares"]
    tickers = sorted(ledger["ticker"].unique())
    start = pd.to_datetime(inception)
    end = pd.Timestamp.today().normalize() + pd.Timedelta(days=1)
    px = prices(tickers, start, end)
    cal = px.index
    # running share count per ticker, and running cash
    holdings = pd.DataFrame(0.0, index=cal, columns=tickers)
    cash = pd.Series(0.0, index=cal)
    cash_bal = float(capital)
    sh = {t: 0.0 for t in tickers}
    daily_rf = (1 + RF_ANNUAL) ** (1 / TRADING_DAYS) - 1
    fills_by_day = ledger.groupby(ledger["date"])
    for i, day in enumerate(cal):
        cash_bal *= (1 + daily_rf)                 # idle cash accrues a bill rate
        if day in fills_by_day.groups:
            for _, r in fills_by_day.get_group(day).iterrows():
                sh[r["ticker"]] += r["signed"]
                cash_bal -= r["signed"] * r["price"]   # BUY drains cash, SELL adds
        for t in tickers:
            holdings.at[day, t] = sh[t]
        cash.at[day] = cash_bal
    mv = (holdings * px[tickers]).sum(axis=1)
    nav = mv + cash
    return nav.dropna()


def metrics(nav: pd.Series, bench: pd.Series, label: str) -> dict:
    r = nav.pct_change().dropna()
    b = bench.pct_change().reindex(r.index).dropna()
    r = r.reindex(b.index)
    tot = nav.iloc[-1] / nav.iloc[0] - 1
    n = len(r)
    ann = (1 + tot) ** (TRADING_DAYS / max(n, 1)) - 1
    vol = r.std() * np.sqrt(TRADING_DAYS)
    dn = r[r < 0].std() * np.sqrt(TRADING_DAYS)
    cum = (1 + r).cumprod()
    mdd = (cum / cum.cummax() - 1).min()
    rf_d = (1 + RF_ANNUAL) ** (1 / TRADING_DAYS) - 1
    sharpe = (r.mean() - rf_d) / r.std() * np.sqrt(TRADING_DAYS) if r.std() else np.nan
    sortino = (r.mean() - rf_d) / (r[r < 0].std() or np.nan) * np.sqrt(TRADING_DAYS)
    calmar = ann / abs(mdd) if mdd else np.nan
    omega = r[r > 0].sum() / -r[r < 0].sum() if (r < 0).any() else np.inf
    # vs benchmark
    beta = np.cov(r, b)[0, 1] / np.var(b) if np.var(b) else np.nan
    alpha_ann = (r.mean() - beta * b.mean()) * TRADING_DAYS
    corr = r.corr(b)
    up = r[b > 0].mean() / b[b > 0].mean() if (b > 0).any() else np.nan
    dncap = r[b < 0].mean() / b[b < 0].mean() if (b < 0).any() else np.nan
    act = r - b
    ir = act.mean() / act.std() * np.sqrt(TRADING_DAYS) if act.std() else np.nan
    return dict(label=label, n=n, tot=tot, ann=ann, vol=vol, mdd=mdd,
                sharpe=sharpe, sortino=sortino, calmar=calmar, omega=omega,
                beta=beta, alpha=alpha_ann, corr=corr, up=up, dn=dncap, ir=ir)


def lhm_score(m: dict) -> float:
    # Tier-2 LHM Score: geometric mean of Sortino / Omega / Calmar (book's own).
    vals = [v for v in (m["sortino"], m["omega"], m["calmar"]) if v and np.isfinite(v) and v > 0]
    return float(np.exp(np.mean(np.log(vals)))) if vals else np.nan


def report(nav: pd.Series):
    start = nav.index[0].date(); end = nav.index[-1].date()
    bpx = prices(list(BENCHES), nav.index[0], nav.index[-1] + pd.Timedelta(days=1))
    print(f"\nCROSSCURRENTS — risk-adjusted record  {start} -> {end}  ({len(nav)} trading days)")
    print(f"NAV {nav.iloc[0]:,.0f} -> {nav.iloc[-1]:,.0f}   total {nav.iloc[-1]/nav.iloc[0]-1:+.2%}\n")
    book = metrics(nav, nav, "Crosscurrents")   # book vs itself for absolute stats
    print(f"  {'metric':<14}{'BOOK':>10}")
    for k, lab in [("ann","Ann return"),("vol","Ann vol"),("mdd","Max drawdown"),
                   ("sharpe","Sharpe"),("sortino","Sortino"),("calmar","Calmar"),("omega","Omega")]:
        v = book[k]
        print(f"  {lab:<14}{(f'{v:>9.2%}' if k in ('ann','vol','mdd') else f'{v:>9.2f}')}")
    print(f"\n  vs benchmarks (alpha ann / beta / up-capture / down-capture / info ratio):")
    rows = []
    for t, lab in BENCHES.items():
        if t not in bpx: continue
        m = metrics(nav, bpx[t], lab)
        rows.append(m)
        print(f"   {lab:<14} a={m['alpha']:+7.2%}  b={m['beta']:+5.2f}  up={m['up']:>6.0%}  dn={m['dn']:>6.0%}  IR={m['ir']:>5.2f}  corr={m['corr']:+.2f}")
    qai = next((m for m in rows if m['label'].startswith('QAI')), None)
    print(f"\n  LHM SCORE (Tier-2, geo-mean Sortino/Omega/Calmar): {lhm_score(book):.2f}")
    if qai:
        print(f"  vs QAI: alpha {qai['alpha']:+.2%} ann, down-capture {qai['dn']:.0%}, up-capture {qai['up']:.0%}")
    print("\n(Idle cash accrued at ~4%/yr bill rate. Provide exact fills for the audited number.)")


def selftest():
    led = pd.read_csv(io.StringIO(
        "date,ticker,action,shares,price\n"
        "2026-05-11,XLP,BUY,400,83.37\n"
        "2026-05-11,SHY,BUY,500,81.98\n"
        "2026-05-11,GLD,BUY,30,434.65\n"
        "2026-06-09,GLD,SELL,30,390.78\n"))
    nav = build_nav(led, 100000, "2026-05-08")
    print("SELFTEST ledger (SYNTHETIC, not the real book) — engine validation only:")
    report(nav)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ledger", nargs="?")
    ap.add_argument("--capital", type=float, default=100000)
    ap.add_argument("--inception", default="2026-05-08")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest or not a.ledger:
        selftest(); return
    led = pd.read_csv(a.ledger)
    report(build_nav(led, a.capital, a.inception))


if __name__ == "__main__":
    main()
