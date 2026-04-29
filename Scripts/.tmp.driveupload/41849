"""
Labor Fragility Index (LFI)
===========================

Canonical Lighthouse Macro labor fragility composite. Captures structural
weakness underneath the headline unemployment rate. Per CLAUDE_MASTER.md
Section 3:

    LFI = 0.35 * z(LongTermUnemp%)
        + 0.35 * z(-Quits)
        + 0.30 * z(-Hires/Quits)

All inputs z-scored on a 5-year rolling window. Higher LFI = more fragile
labor market. The LFI > +0.5 threshold flags elevated fragility.

Inputs (monthly):
    LongTermUnemp%   = UEMP27OV / UNEMPLOY    (BLS, Employment Situation)
    Quits Rate       = JTSQUR                 (BLS, JOLTS, total nonfarm)
    Hires / Quits    = JTSHIL / JTSQUL        (BLS, JOLTS levels)

Note: JOLTS releases ~7 weeks after month-end, so the latest LFI value
typically lags the latest unemployment-rate value by one month.

Usage:
    from lfi import compute_lfi, load_lfi_inputs
    df = compute_lfi(db_path='/path/to/Lighthouse_Master.db')
    # df is a monthly DataFrame indexed by date with columns:
    #   ltu_pct, quits_rate, hires_quits_ratio,
    #   ltu_z, neg_quits_z, neg_hires_quits_z,
    #   lfi
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Optional

import pandas as pd


# ---------------------------------------------------------------------------
# Spec — pinned to CLAUDE_MASTER.md Section 3
# ---------------------------------------------------------------------------
WEIGHTS = {
    "ltu_z":            0.35,   # long-term unemployed share, sign-positive
    "neg_quits_z":      0.35,   # negative quits rate (low quits = fragile)
    "neg_hires_quits_z": 0.30,  # negative hires/quits (slow rehire = fragile)
}

ROLLING_WINDOW_MONTHS = 60       # 5-year rolling window for z-scores
ROLLING_MIN_PERIODS   = 36       # need at least 3y of history before LFI prints


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------
def _pull_series(conn, sid: str) -> pd.Series:
    df = pd.read_sql(
        f"SELECT date, value FROM observations WHERE series_id = ? ORDER BY date",
        conn, params=(sid,),
    )
    df["date"] = pd.to_datetime(df["date"])
    s = (df.dropna(subset=["value"])
           .drop_duplicates(subset=["date"], keep="last")
           .set_index("date")["value"]
           .astype(float)
           .sort_index())
    return s


def load_lfi_inputs(db_path: str | Path) -> pd.DataFrame:
    """Load and align the four monthly series the LFI needs.

    Returns a monthly DataFrame indexed by month-start with columns:
        ltu_pct, quits_rate, hires_quits_ratio
    """
    conn = sqlite3.connect(str(db_path))
    try:
        ltu_lvl   = _pull_series(conn, "UEMP27OV")    # 27+ weeks unemployed, level
        unemp_lvl = _pull_series(conn, "UNEMPLOY")    # total unemployed, level
        quits_r   = _pull_series(conn, "JTSQUR")      # quits rate, %
        hires_l   = _pull_series(conn, "JTSHIL")      # hires level
        quits_l   = _pull_series(conn, "JTSQUL")      # quits level
    finally:
        conn.close()

    # All series are monthly (BLS) but raw timestamps may not align perfectly.
    # Resample each to month-start last-observation to be safe.
    def to_month_start(s):
        return s.resample("MS").last()

    ltu_pct = (to_month_start(ltu_lvl) / to_month_start(unemp_lvl)) * 100.0
    quits_rate = to_month_start(quits_r)
    hires_quits = to_month_start(hires_l) / to_month_start(quits_l)

    df = pd.concat({
        "ltu_pct":            ltu_pct,
        "quits_rate":         quits_rate,
        "hires_quits_ratio":  hires_quits,
    }, axis=1).dropna(how="all")
    return df


# ---------------------------------------------------------------------------
# Composite
# ---------------------------------------------------------------------------
def _rolling_z(s: pd.Series, window: int = ROLLING_WINDOW_MONTHS,
               min_periods: int = ROLLING_MIN_PERIODS) -> pd.Series:
    mu = s.rolling(window, min_periods=min_periods).mean()
    sd = s.rolling(window, min_periods=min_periods).std()
    return (s - mu) / sd


def compute_lfi(db_path: str | Path,
                start: Optional[str] = None) -> pd.DataFrame:
    """Compute the LFI from raw inputs.

    Parameters
    ----------
    db_path : path to Lighthouse_Master.db
    start   : optional start date for the returned DataFrame (e.g. '2010-01-01').
              The z-score window still uses all available history before `start`.

    Returns a monthly DataFrame with input series, z-score components, and LFI.
    """
    inputs = load_lfi_inputs(db_path)

    z = pd.DataFrame(index=inputs.index)
    z["ltu_z"]              = _rolling_z(inputs["ltu_pct"])
    z["neg_quits_z"]        = _rolling_z(-inputs["quits_rate"])
    z["neg_hires_quits_z"]  = _rolling_z(-inputs["hires_quits_ratio"])

    z["lfi"] = sum(WEIGHTS[k] * z[k] for k in WEIGHTS)

    out = pd.concat([inputs, z], axis=1)
    if start is not None:
        out = out.loc[pd.Timestamp(start):]
    return out


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--db", default="/Users/bob/LHM/Data/databases/Lighthouse_Master.db")
    p.add_argument("--start", default="2010-01-01")
    args = p.parse_args()
    df = compute_lfi(args.db, start=args.start)
    print(df.tail(15).to_string())
    print(f"\nLatest LFI: {df['lfi'].iloc[-1]:+.2f} as of {df.index[-1].date()}")
