#!/usr/bin/env python3
"""
Phase A — LHM signal-evaluation harness.

Macrosynergy SignalReturnRelations discipline applied through the LHM
registry architecture (May-8): every indicator is scored as a
(basket x target x horizon x role) tuple, never one global target,
never a bare "the LPI IC".

For each (composite, role, target, horizon) it computes, strictly
point-in-time (signal at t vs target measured over t -> t+h):

  - IC        : Pearson corr(signal_t, target_{t->t+h})
  - rank IC   : Spearman corr (robust to nonlinearity / outliers)
  - sign acc  : % of periods sign(signal) predicts sign(target move)
  - OOS IC    : mean IC across expanding-window out-of-sample blocks
  - sign_ok   : does realized IC sign match the economic expectation

DIAGNOSIS ONLY. Touches no canonical docs. Output is a scorecard that
informs Phase B (keep / re-optimize / demote).

Run:
    python Scripts/backtest/signal_eval.py
"""

from __future__ import annotations

import sqlite3
import warnings
from datetime import datetime

import numpy as np
import pandas as pd

warnings.simplefilter("ignore")

DB = "/Users/bob/LHM/Data/databases/Lighthouse_Master.db"

# NBER recession start/end (same list as the chart template).
RECESSIONS = [
    ("1953-07-01", "1954-05-01"), ("1957-08-01", "1958-04-01"),
    ("1960-04-01", "1961-02-01"), ("1969-12-01", "1970-11-01"),
    ("1973-11-01", "1975-03-01"), ("1980-01-01", "1980-07-01"),
    ("1981-07-01", "1982-11-01"), ("1990-07-01", "1991-03-01"),
    ("2001-03-01", "2001-11-01"), ("2007-12-01", "2009-06-01"),
    ("2020-02-01", "2020-04-01"),
]

# Registry: composite -> list of evaluation tuples.
#   kind: recession | db_fwd_chg | asset_fwd_ret | ratio_fwd_ret | db_concurrent
#   tgt : DB series_id, yfinance ticker, or "A/B" ratio of tickers
#   h   : horizon in calendar days (0 = concurrent/diagnostic)
#   exp : economically expected IC sign (+1/-1), None if genuinely ambiguous
REG = {
    "LFI": [  # Labor Fragility — leads the cycle
        dict(role="asset-pred", kind="recession",     tgt="NBER", h=126, exp=+1),
        dict(role="asset-pred", kind="recession",     tgt="NBER", h=252, exp=+1),
    ],
    "LPI": [  # Labor Pressure — labor health
        dict(role="asset-pred", kind="asset_fwd_ret", tgt="SPY",  h=126, exp=+1),
        dict(role="rel-pred",   kind="ratio_fwd_ret", tgt="SHY/TLT", h=126, exp=None),
    ],
    "LDI": [
        dict(role="asset-pred", kind="recession",     tgt="NBER", h=252, exp=-1),
    ],
    "PCI": [  # Inflation Heat
        dict(role="diagnostic", kind="db_concurrent", tgt="PCEPILFE", h=0,  exp=+1),
        dict(role="asset-pred", kind="db_fwd_chg",    tgt="DGS10", h=126, exp=+1),
        dict(role="asset-pred", kind="db_fwd_chg",    tgt="DGS10", h=252, exp=+1),
    ],
    "GCI": [  # Activity Pulse
        dict(role="asset-pred", kind="asset_fwd_ret", tgt="SPY",  h=126, exp=+1),
        dict(role="asset-pred", kind="recession",     tgt="NBER", h=252, exp=-1),
    ],
    "HCI": [  # Housing Tide
        dict(role="asset-pred", kind="asset_fwd_ret", tgt="XHB",  h=126, exp=+1),
    ],
    "CCI": [  # Consumer Pulse
        dict(role="rel-pred",   kind="ratio_fwd_ret", tgt="XLY/XLP", h=126, exp=+1),
    ],
    "BCI": [  # Capex Thrust
        dict(role="asset-pred", kind="asset_fwd_ret", tgt="XLI",  h=126, exp=+1),
    ],
    "TCI": [  # Global Risk Tide
        dict(role="asset-pred", kind="asset_fwd_ret", tgt="DX-Y.NYB", h=126, exp=None),
    ],
    "FPI": [  # Fiscal Pressure
        dict(role="asset-pred", kind="asset_fwd_ret", tgt="TLT",  h=126, exp=-1),
        dict(role="asset-pred", kind="db_fwd_chg",    tgt="DGS10", h=126, exp=+1),
    ],
    "FCI": [  # Credit Tide
        dict(role="asset-pred", kind="db_fwd_chg",    tgt="BAMLH0A0HYM2", h=126, exp=None),
        dict(role="asset-pred", kind="asset_fwd_ret", tgt="SPY",  h=126, exp=None),
    ],
    "CLG": [  # Credit-Labor Gap
        dict(role="asset-pred", kind="db_fwd_chg",    tgt="BAMLH0A0HYM2", h=126, exp=+1),
    ],
    "LCI": [  # Liquidity Cushion
        dict(role="asset-pred", kind="asset_fwd_ret", tgt="SPY",  h=63,  exp=+1),
        dict(role="asset-pred", kind="db_fwd_chg",    tgt="BAMLH0A0HYM2", h=126, exp=-1),
    ],
    "MSI": [  # Market Breadth Pulse
        dict(role="asset-pred", kind="asset_fwd_ret", tgt="SPY",  h=63,  exp=+1),
    ],
    "SBD": [  # Structure-Breadth Divergence
        dict(role="asset-pred", kind="asset_fwd_ret", tgt="SPY",  h=63,  exp=-1),
    ],
    "SPI": [  # Sentiment Tide — contrarian
        dict(role="asset-pred", kind="asset_fwd_ret", tgt="SPY",  h=63,  exp=+1),
    ],
    "MRI": [  # master
        dict(role="asset-pred", kind="recession",     tgt="NBER", h=252, exp=+1),
        dict(role="asset-pred", kind="asset_fwd_ret", tgt="SPY",  h=126, exp=-1),
    ],
    "REC_PROB": [
        dict(role="asset-pred", kind="recession",     tgt="NBER", h=252, exp=+1),
    ],
}

# Macro-predictive role (added 2026-05-16): "when X moves, spending drops /
# inflation picks up / hiring falls" — X_t vs the FORWARD change in a macro
# series it should lead. The transmission-chain thesis made testable.
MACRO_PRED = {
    "LFI": [
        dict(role="macro-pred", kind="db_fwd_chg", tgt="PCEC96",   h=126, exp=-1),
        dict(role="macro-pred", kind="db_fwd_chg", tgt="PAYEMS",   h=126, exp=-1),
    ],
    "LPI": [
        dict(role="macro-pred", kind="db_fwd_chg", tgt="PAYEMS",   h=126, exp=+1),
    ],
    "LDI": [
        dict(role="macro-pred", kind="db_fwd_chg", tgt="PAYEMS",   h=126, exp=+1),
    ],
    "CLG": [
        dict(role="macro-pred", kind="db_fwd_chg", tgt="UNRATE",   h=126, exp=-1),
    ],
    "LCI": [
        dict(role="macro-pred", kind="db_fwd_chg", tgt="BAMLH0A0HYM2", h=63, exp=-1),
    ],
    "FCI": [
        dict(role="macro-pred", kind="db_fwd_chg", tgt="PAYEMS",   h=126, exp=None),
    ],
    "PCI": [
        dict(role="macro-pred", kind="db_fwd_chg", tgt="PCEPILFE", h=126, exp=+1),
    ],
    "HCI": [
        dict(role="macro-pred", kind="db_fwd_chg", tgt="INDPRO",   h=126, exp=+1),
    ],
    "BCI": [
        dict(role="macro-pred", kind="db_fwd_chg", tgt="INDPRO",   h=126, exp=+1),
    ],
    "GCI": [
        dict(role="macro-pred", kind="db_fwd_chg", tgt="PAYEMS",   h=126, exp=+1),
    ],
    "TCI": [
        dict(role="macro-pred", kind="db_fwd_chg", tgt="PCEPILFE", h=126, exp=None),
    ],
    "MRI": [
        dict(role="macro-pred", kind="db_fwd_chg", tgt="UNRATE",   h=252, exp=+1),
    ],
}
for _c, _specs in MACRO_PRED.items():
    REG.setdefault(_c, []).extend(_specs)


def load_composite(conn, code):
    df = pd.read_sql(
        "SELECT date, value FROM lighthouse_indices WHERE index_id=? ORDER BY date",
        conn, params=(code,), parse_dates=["date"],
    ).set_index("date")["value"].dropna()
    return df[~df.index.duplicated(keep="last")]


def load_db_series(conn, sid):
    df = pd.read_sql(
        "SELECT date, value FROM observations WHERE series_id=? ORDER BY date",
        conn, params=(sid,), parse_dates=["date"],
    ).set_index("date")["value"].dropna()
    return df[~df.index.duplicated(keep="last")]


_YF_CACHE = {}


def load_yf(ticker):
    if ticker in _YF_CACHE:
        return _YF_CACHE[ticker]
    try:
        import yfinance as yf
        h = yf.Ticker(ticker).history(period="max", auto_adjust=True)
        if h.empty:
            _YF_CACHE[ticker] = None
            return None
        s = h["Close"].copy()
        s.index = s.index.tz_localize(None).normalize()
        _YF_CACHE[ticker] = s
        return s
    except Exception:
        _YF_CACHE[ticker] = None
        return None


def recession_target(idx, h):
    """Binary: 1 if an NBER recession STARTS within (t, t+h] days."""
    starts = pd.to_datetime([s for s, _ in RECESSIONS])
    y = pd.Series(0.0, index=idx)
    for t in idx:
        lo, hi = t, t + pd.Timedelta(days=h)
        if ((starts > lo) & (starts <= hi)).any():
            y.loc[t] = 1.0
    return y


def build_target(conn, spec, sig_idx):
    kind, tgt, h = spec["kind"], spec["tgt"], spec["h"]
    if kind == "recession":
        return recession_target(sig_idx, h)
    if kind == "db_concurrent":
        s = load_db_series(conn, tgt)
        if s.empty:
            return None
        return s.reindex(sig_idx, method="ffill", limit=10)
    if kind == "db_fwd_chg":
        s = load_db_series(conn, tgt)
        if s.empty:
            return None
        s = s.reindex(sig_idx.union(s.index)).sort_index().ffill(limit=10)
        fwd = s.shift(-h) - s
        return fwd.reindex(sig_idx)
    if kind in ("asset_fwd_ret", "ratio_fwd_ret"):
        if kind == "ratio_fwd_ret":
            a, b = tgt.split("/")
            pa, pb = load_yf(a), load_yf(b)
            if pa is None or pb is None:
                return None
            p = (pa / pb.reindex(pa.index).ffill()).dropna()
        else:
            p = load_yf(tgt)
            if p is None:
                return None
        p = p.reindex(sig_idx.union(p.index)).sort_index().ffill(limit=5)
        fwd = p.shift(-h) / p - 1.0
        return fwd.reindex(sig_idx)
    return None


def expanding_oos_ic(sig, tgt, n_blocks=6, min_train=252 * 3):
    """Mean IC across expanding out-of-sample blocks. The target is strictly
    forward so there is no leakage; this measures stability, not luck."""
    df = pd.concat([sig.rename("s"), tgt.rename("t")], axis=1).dropna()
    if len(df) < min_train + 60:
        return np.nan, 0
    s, t = df["s"].to_numpy(float), df["t"].to_numpy(float)
    n = len(s)
    step = max(60, (n - min_train) // n_blocks)
    ics, i = [], min_train
    while i < n:
        j = min(i + step, n)
        a, b = s[i:j], t[i:j]
        if len(a) > 10 and a.std() > 0 and b.std() > 0:
            ics.append(np.corrcoef(a, b)[0, 1])
        i = j
    return (float(np.nanmean(ics)) if ics else np.nan), len(ics)


def evaluate(sig, tgt):
    df = pd.concat([sig.rename("s"), tgt.rename("t")], axis=1).dropna()
    n = len(df)
    if n < 100 or df["s"].std() == 0 or df["t"].std() == 0:
        return None
    s, t = df["s"], df["t"]
    ic = float(s.corr(t))
    ric = float(s.corr(t, method="spearman"))
    # sign accuracy: signal sign vs target-move sign (demeaned signal)
    sd = s - s.mean()
    sign_acc = float((np.sign(sd) == np.sign(t - t.mean())).mean())
    oos_ic, nb = expanding_oos_ic(s, t)
    return dict(n=n, ic=ic, ric=ric, sign_acc=sign_acc,
                oos_ic=oos_ic, oos_blocks=nb)


def main():
    conn = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    rows = []
    for code, specs in REG.items():
        sig = load_composite(conn, code)
        if sig.empty:
            for sp in specs:
                rows.append((code, sp["role"], sp["kind"], sp["tgt"],
                             sp["h"], sp["exp"], None))
            continue
        for sp in specs:
            tgt = build_target(conn, sp, sig.index)
            res = evaluate(sig, tgt) if tgt is not None else None
            rows.append((code, sp["role"], sp["kind"], sp["tgt"],
                         sp["h"], sp["exp"], res))
    conn.close()

    print("=" * 104)
    print("LHM SIGNAL SCORECARD  ·  Phase A  ·  point-in-time, forward targets"
          f"  ·  {datetime.now():%Y-%m-%d %H:%M}")
    print("=" * 104)
    hdr = (f"{'Composite':<10}{'Role':<11}{'Target':<16}{'H':>4}"
           f"{'IC':>8}{'rankIC':>8}{'OOS IC':>8}{'signAcc':>9}"
           f"{'n':>7}  sign?")
    print(hdr); print("-" * 104)

    def sortkey(r):
        res = r[6]
        return -abs(res["ic"]) if res else 1.0

    for code, role, kind, tgt, h, exp, res in sorted(rows, key=sortkey):
        if res is None:
            print(f"{code:<10}{role:<11}{tgt:<16}{h:>4}"
                  f"{'  no data / insufficient':<40}")
            continue
        ic = res["ic"]
        sign_ok = "" if exp is None else (
            "ok" if np.sign(ic) == np.sign(exp) else "FLIP")
        oos = res["oos_ic"]
        oos_s = f"{oos:+.2f}" if oos == oos else " n/a"
        print(f"{code:<10}{role:<11}{tgt:<16}{h:>4}"
              f"{ic:>+8.2f}{res['ric']:>+8.2f}{oos_s:>8}"
              f"{res['sign_acc']:>8.0%}{res['n']:>7}  "
              f"{('exp '+('+' if exp==1 else '-' if exp==-1 else '?')):<6}{sign_ok}")
    print("-" * 104)
    print("IC = corr(signal_t, fwd target).  rankIC = Spearman.  "
          "OOS IC = mean over expanding OOS blocks.")
    print("sign? FLIP = realized IC sign contradicts the economic expectation "
          "(red flag for that tuple).")


if __name__ == "__main__":
    main()
