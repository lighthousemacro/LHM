#!/usr/bin/env python3
"""
CRYPTO DeFi LIQUIDITY INDEX (CDLI) — free-data rewire (2026-06-15)

Replaces the retired paid-fundamentals crypto indices (CFI/CVI/CTI/CRYPTO_*_HEALTH,
which read the dead crypto_scores table) with a real, free-data, deep-history
crypto-liquidity read: total DeFi TVL momentum, z-scored. Built from the 17
DEFI_*_TVL protocol series DefiLlama provides with multi-year chart history
(Uniswap 2018+, MakerDAO 2019+, ...). Descriptive (crypto as a liquidity asset),
not a predictive claim.

Writes CRYPTO_DEFI_LIQUIDITY to lighthouse_indices (upsert). Wire into the daily
pipeline; can also run standalone.

Run: /opt/homebrew/bin/python3 Scripts/data_pipeline/crypto_defi_liquidity.py
"""
import sqlite3
import numpy as np
import pandas as pd

DB_PATH = "/Users/bob/LHM/Data/databases/Lighthouse_Master.db"

STATUS = [(1.5, "EXPANDING FAST"), (0.5, "EXPANDING"), (-0.5, "NEUTRAL"),
          (-1.5, "CONTRACTING"), (-999, "CONTRACTING FAST")]


def status_for(v):
    if pd.isna(v):
        return "NO DATA"
    for t, s in STATUS:
        if v >= t:
            return s
    return "NO DATA"


def compute_cdli(conn) -> pd.Series:
    d = pd.read_sql(
        "SELECT date, value FROM observations WHERE series_id LIKE 'DEFI_%_TVL' "
        "AND value IS NOT NULL", conn, parse_dates=["date"])
    if d.empty:
        return pd.Series(dtype=float)
    # Total DeFi TVL across protocols, per day. Require >=5 protocols present so
    # early-history single-protocol noise doesn't dominate.
    g = d.groupby("date")["value"]
    total = g.sum()
    n_proto = g.count()
    total = total[n_proto >= 5].sort_index()
    if total.empty:
        return pd.Series(dtype=float)
    # YoY momentum (liquidity expanding/contracting), z-scored over a rolling 2y.
    yoy = total.pct_change(365, fill_method=None) * 100.0
    z = (yoy - yoy.rolling(504, min_periods=120).mean()) \
        / yoy.rolling(504, min_periods=120).std().replace(0, np.nan)
    return z.dropna()


def main():
    conn = sqlite3.connect(DB_PATH, timeout=60)
    conn.execute("PRAGMA busy_timeout=60000")
    cdli = compute_cdli(conn)
    if cdli.empty:
        print("CDLI: no data"); return
    c = conn.cursor()
    rows = [(d.strftime("%Y-%m-%d"), "CRYPTO_DEFI_LIQUIDITY", round(float(v), 4),
             status_for(v)) for d, v in cdli.items() if pd.notna(v)]
    c.executemany(
        "INSERT OR REPLACE INTO lighthouse_indices (date, index_id, value, status) "
        "VALUES (?,?,?,?)", rows)
    conn.commit()
    conn.close()
    print(f"CRYPTO_DEFI_LIQUIDITY: wrote {len(rows)} rows "
          f"{cdli.index.min().date()}..{cdli.index.max().date()} "
          f"latest={cdli.iloc[-1]:.2f} ({status_for(cdli.iloc[-1])})")


if __name__ == "__main__":
    main()
