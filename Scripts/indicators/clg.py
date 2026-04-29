"""
Credit-Labor Gap (CLG)
======================

Canonical Lighthouse Macro indicator. Per CLAUDE_MASTER.md Section 3:

    CLG = z(HY OAS) - z(LFI)

CLG < -1.0 is the warning threshold: HY spreads are pricing a labor market
that the LFI says does not exist (i.e. credit is too tight... wait, sign
convention).

Sign reading (the careful part):
    LFI is constructed so HIGHER = MORE FRAGILE.
    HY OAS is HIGHER = MORE STRESSED.
    z(HY) - z(LFI) = how much MORE stressed credit is than labor would suggest.

    CLG > +1.0 : credit way more stressed than labor warrants (rare).
    CLG <  0   : credit relatively complacent given labor fragility.
    CLG < -1.0 : credit pricing a labor market that does not exist.
                 The canonical 'credit ignoring fundamentals' warning.

This is the cleanest single-frame statement of the labor-credit-equity chain.

Inputs (mixed frequency):
    HY OAS   = BAMLH0A0HYM2  (FRED, daily)
    LFI      = composite from indicators/lfi.py (monthly)

Both are resampled to month-end and z-scored on a 5-year rolling window
before differencing.

Usage:
    from clg import compute_clg
    df = compute_clg(db_path='/path/to/Lighthouse_Master.db')
    # df is a monthly DataFrame indexed by month-end with columns:
    #   hy_oas, hy_oas_z, lfi, lfi_z, clg
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Optional

import pandas as pd

from lfi import compute_lfi, _rolling_z, ROLLING_WINDOW_MONTHS, ROLLING_MIN_PERIODS


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------
def _load_hy_oas_monthly(db_path: str | Path) -> pd.Series:
    conn = sqlite3.connect(str(db_path))
    try:
        df = pd.read_sql(
            "SELECT date, value FROM observations WHERE series_id = 'BAMLH0A0HYM2' ORDER BY date",
            conn,
        )
    finally:
        conn.close()
    df["date"] = pd.to_datetime(df["date"])
    s = (df.dropna(subset=["value"])
           .drop_duplicates(subset=["date"], keep="last")
           .set_index("date")["value"]
           .astype(float)
           .sort_index())
    # Resample daily -> monthly. Use month-end last observation to align with
    # JOLTS, which is reported as the level for the month (timestamp = month start
    # but observation describes activity through end-of-month).
    return s.resample("MS").last()


# ---------------------------------------------------------------------------
# Composite
# ---------------------------------------------------------------------------
def compute_clg(db_path: str | Path,
                start: Optional[str] = None) -> pd.DataFrame:
    """Compute the canonical Credit-Labor Gap.

    Returns monthly DataFrame with:
        hy_oas, hy_oas_z, lfi, lfi_z, clg
    """
    lfi_df = compute_lfi(db_path)
    hy = _load_hy_oas_monthly(db_path)

    df = pd.concat({
        "hy_oas": hy,
        "lfi":    lfi_df["lfi"],
    }, axis=1).dropna()

    df["hy_oas_z"] = _rolling_z(df["hy_oas"])
    df["lfi_z"]    = _rolling_z(df["lfi"])
    df["clg"]      = df["hy_oas_z"] - df["lfi_z"]

    df = df.dropna(subset=["clg"])
    if start is not None:
        df = df.loc[pd.Timestamp(start):]
    return df


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--db", default="/Users/bob/LHM/Data/databases/Lighthouse_Master.db")
    p.add_argument("--start", default="2010-01-01")
    args = p.parse_args()
    df = compute_clg(args.db, start=args.start)
    print(df.tail(15).to_string())
    print(f"\nLatest CLG: {df['clg'].iloc[-1]:+.2f} as of {df.index[-1].date()}")
    print(f"Latest LFI: {df['lfi'].iloc[-1]:+.2f}, HY OAS: {df['hy_oas'].iloc[-1]*100:.0f} bps")
