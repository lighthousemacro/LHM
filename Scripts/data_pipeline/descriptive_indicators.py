#!/usr/bin/env python3
"""
DESCRIPTIVE / DIAGNOSTIC INDICATORS — pillar-doc expansion (2026-06-15)

11 legitimate indicators surfaced by reading the full 12 pillar docs, taking the
live lineup from 39 to 50. All honest by construction: descriptive composites,
diagnostics, and divergences that combine real DB series into one meaningful
read (no data-mined filler, no predictive overclaim). Computed on NATIVE monthly
frequency (correct YoY/z windows), coverage-weighted, standardized, daily-FF —
the same correct math as the ALLOC_* composites.

Writes to lighthouse_indices (upsert). Wired into the daily pipeline.
Run: /opt/homebrew/bin/python3 Scripts/data_pipeline/descriptive_indicators.py
"""
import sqlite3
import numpy as np
import pandas as pd

DB_PATH = "/Users/bob/LHM/Data/databases/Lighthouse_Master.db"

# code_id -> {"name", "basket": [(series, sign, transform)], "label": one-liner}
# transform: "yoy" (12m % change of an index/level) or "level" (already a rate/spread)
INDICATORS = {
    "SUPERCORE_HEAT": dict(  # services-ex-shelter inflation (Fed supercore)
        basket=[("CUSR0000SASLE", +1, "yoy"), ("CUSR0000SAH1", -1, "yoy"),
                ("IA001260M", +1, "yoy")]),
    "PERSISTENCE_GAP": dict(  # sticky minus flexible CPI (persistence vs transitory)
        basket=[("CORESTICKM159SFRBATL", +1, "level"),
                ("COREFLEXCPIM159SFRBATL", -1, "level")]),
    "PIPELINE_IMPULSE": dict(  # PPI running ahead of CPI (upstream inflation lead)
        basket=[("PPIFIS", +1, "yoy"), ("CPIAUCSL", -1, "yoy"),
                ("PPIFES", +1, "yoy"), ("CPILFESL", -1, "yoy")]),
    "TREND_HEAT": dict(  # trimmed-mean / median underlying inflation
        basket=[("PCETRIM12M159SFRBDAL", +1, "level"),
                ("MEDCPIM158SFRBCLE", +1, "level"),
                ("TRMMEANCPIM157SFRBCLE", +1, "level"),
                ("PCETRIM6M680SFRBDAL", +1, "level")]),
    "AFFORD_PRESSURE": dict(  # true cost of homeownership (rate + price vs wage)
        basket=[("MORTGAGE30US", +1, "level"), ("MSPUS", +1, "yoy"),
                ("CES0500000003", -1, "yoy")]),
    "FROZEN_DIVERGENCE": dict(  # rate-frozen housing: price up while sales collapse
        basket=[("CSUSHPINSA", +1, "yoy"), ("EXHOSLUSM495S", -1, "yoy"),
                ("HSN1F", -1, "yoy")]),
    "INTEREST_CROWDOUT": dict(  # federal interest expense outrunning the economy
        basket=[("A091RC1Q027SBEA", +1, "yoy"), ("GDP", -1, "yoy")]),
    "QUALITY_PRESSURE": dict(  # within-IG quality premium (BAA minus AAA)
        basket=[("BAA10Y", +1, "level"), ("AAA10Y", -1, "level")]),
    "VOL_TERM_GAP": dict(  # equity-vol term structure (spot VIX vs 3-month)
        basket=[("VIXCLS", +1, "level"), ("VXVCLS", -1, "level")]),
    "FCI_CHANNELS": dict(  # financial-conditions sub-channels (risk+credit+leverage)
        basket=[("NFCIRISK", +1, "level"), ("NFCICREDIT", +1, "level"),
                ("NFCILEVERAGE", +1, "level")]),
    "CAPACITY_SLACK": dict(  # spare industrial/manufacturing capacity (disinflationary)
        basket=[("TCU", -1, "level"), ("MCUMFN", -1, "level")]),
}

BANDS = [(1.5, "EXTREME"), (0.5, "ELEVATED"), (-0.5, "NEUTRAL"),
         (-1.5, "LOW"), (-999, "VERY LOW")]


def status_for(v):
    if pd.isna(v):
        return "NO DATA"
    for t, s in BANDS:
        if v >= t:
            return s
    return "NO DATA"


def load_series(conn, sid):
    d = pd.read_sql("SELECT date, value FROM observations WHERE series_id=? "
                    "AND value IS NOT NULL ORDER BY date", conn, params=(sid,),
                    parse_dates=["date"])
    if d.empty:
        return pd.Series(dtype=float)
    s = pd.Series(d["value"].astype(float).values, index=pd.to_datetime(d["date"]))
    return s[~s.index.duplicated(keep="last")].sort_index()


def compute(conn, basket, target_index, z_window=60):
    cols = {}
    for sid, sign, tf in basket:
        s = load_series(conn, sid)
        if s.empty:
            continue
        # resample to month-end; ffill carries quarterly series (e.g. GDP,
        # interest expense) across the intervening months so YoY is well-defined.
        m = s.resample("ME").last().ffill()
        v = m.pct_change(12, fill_method=None) * 100.0 if tf == "yoy" else m
        mu = v.rolling(z_window, min_periods=24).mean()
        sd = v.rolling(z_window, min_periods=24).std().replace(0, np.nan)
        cols[sid] = ((v - mu) / sd) * sign
    if not cols:
        return pd.Series(dtype=float)
    Z = pd.DataFrame(cols)
    present = Z.notna().sum(axis=1)
    comp = Z.mean(axis=1, skipna=True).where(present >= max(1, 0.5 * Z.shape[1]))
    cd = comp.dropna()
    if len(cd) > 24 and cd.std() > 0:
        comp = (comp - cd.mean()) / cd.std()
    full = comp.index.union(target_index)
    return comp.reindex(full).sort_index().ffill().reindex(target_index)


def main():
    conn = sqlite3.connect(DB_PATH, timeout=60)
    conn.execute("PRAGMA busy_timeout=60000")
    target_index = pd.date_range("1990-01-01", pd.Timestamp.today().normalize(), freq="D")
    total = 0
    for code, spec in INDICATORS.items():
        s = compute(conn, spec["basket"], target_index).dropna()
        if s.empty:
            print(f"   [skip] {code}: empty"); continue
        rows = [(d.strftime("%Y-%m-%d"), code, round(float(v), 4), status_for(v))
                for d, v in s.items() if pd.notna(v)]
        conn.executemany(
            "INSERT OR REPLACE INTO lighthouse_indices (date, index_id, value, status) "
            "VALUES (?,?,?,?)", rows)
        total += len(rows)
        print(f"   [ok] {code:<22} {len(rows):>6} rows  {s.index.min().date()}..{s.index.max().date()}  "
              f"latest {s.iloc[-1]:+.2f} ({status_for(s.iloc[-1])})")
    conn.commit()
    conn.close()
    print(f"\nWrote {total} rows across {len(INDICATORS)} descriptive indicators")


if __name__ == "__main__":
    main()
