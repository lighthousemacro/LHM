"""
LHM technical read for a symbol — deterministic, no Claude/MCP.

Pulls real price data (yfinance) + the SPY benchmark and computes the LHM read:
price vs 50d/200d, relative strength regime vs SPY, absolute Z-RoC, and the
200d-buffer binding stop. Used by the standalone lhmbot (lhmbot_server.py) so
the reactive reads never depend on the flaky MCP bridge.

Returns a dict including the raw price frames so /read can render the branded
3-panel chart without re-downloading.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import pandas as pd

sys.path.insert(0, "/Users/bob/LHM/Scripts/chart_generation")
from lhm_tape_read import compute_z_roc  # noqa: E402

_BENCH_CACHE: dict[str, tuple[float, pd.DataFrame]] = {}
BENCH_TTL = 600  # 10 min — SPY doesn't move fast enough to re-pull per request


def _dl(ticker: str, period: str = "3y") -> pd.DataFrame | None:
    import yfinance as yf
    try:
        d = yf.download(ticker, period=period, interval="1d",
                        progress=False, auto_adjust=True)
    except Exception:
        return None
    if d is None or d.empty:
        return None
    if isinstance(d.columns, pd.MultiIndex):
        d.columns = [c[0] for c in d.columns]
    return d


def _bench(name: str = "SPY") -> pd.DataFrame | None:
    now = time.time()
    c = _BENCH_CACHE.get(name)
    if c and now - c[0] < BENCH_TTL:
        return c[1]
    df = _dl(name)
    if df is not None:
        _BENCH_CACHE[name] = (now, df)
    return df


def _rs_regime(px: pd.Series, bdf: pd.DataFrame | None) -> str:
    if bdf is None or "Close" not in bdf.columns:
        return "n/a"
    bclose = bdf["Close"].dropna()
    common = px.index.intersection(bclose.index)
    if len(common) < 252:
        return "n/a"
    rs = (px.loc[common] / bclose.loc[common]) * 100
    rs63 = rs.rolling(63).mean().iloc[-1]
    rs252 = rs.rolling(252).mean().iloc[-1]
    last = rs.iloc[-1]
    if last > rs63 and last > rs252:
        return "LEADING"
    if last < rs63 and last < rs252:
        return "LAGGING"
    return "MIXED"


def read_symbol(ticker: str, benchmark: str = "SPY") -> dict | None:
    """The LHM read for one symbol. None if the ticker can't be pulled."""
    px_df = _dl(ticker)
    if px_df is None or "Close" not in px_df.columns:
        return None
    px = px_df["Close"].dropna()
    if len(px) < 60:
        return {"ticker": ticker.upper(), "error": "insufficient history"}

    last = float(px.iloc[-1])
    prev = float(px.iloc[-2]) if len(px) > 1 else last
    day_chg = (last / prev - 1) * 100 if prev else 0.0
    sma50 = px.rolling(50).mean().iloc[-1]
    sma200 = px.rolling(200).mean().iloc[-1]
    vs50 = (last / float(sma50) - 1) * 100 if pd.notna(sma50) else None
    vs200 = (last / float(sma200) - 1) * 100 if pd.notna(sma200) else None
    z = compute_z_roc(px)
    zroc = float(z.iloc[-1]) if len(z) else None

    bdf = _bench(benchmark)
    rs = _rs_regime(px, bdf)
    stop = float(sma200) * 0.99 if pd.notna(sma200) else None  # 200d-buffer ~1% under

    return {
        "ticker": ticker.upper(), "last": last, "day_chg": day_chg,
        "vs50": vs50, "vs200": vs200, "zroc": zroc, "rs": rs,
        "sma50": float(sma50) if pd.notna(sma50) else None,
        "sma200": float(sma200) if pd.notna(sma200) else None,
        "stop": stop, "benchmark": benchmark,
        "px_df": px_df, "bench_df": bdf,
    }


def scan_row(r: dict) -> dict:
    """Reduce a read dict to a build_scan_table row."""
    setup = ("uptrend" if (r.get("vs200") or 0) >= 0 else "below trend")
    stop = f"{r['stop']:,.0f} (200d)" if r.get("stop") else "—"
    return {"ticker": r["ticker"], "last": r.get("last"), "vs200": r.get("vs200"),
            "rs": r.get("rs"), "zroc": r.get("zroc"), "setup": setup, "stop": stop}


if __name__ == "__main__":
    import json
    sym = sys.argv[1] if len(sys.argv) > 1 else "NVDA"
    r = read_symbol(sym)
    if r:
        slim = {k: v for k, v in r.items() if k not in ("px_df", "bench_df")}
        print(json.dumps(slim, indent=2, default=str))
    else:
        print(f"could not read {sym}")
