#!/usr/bin/env python3
"""Measure how far a composite actually leads a target, instead of asserting it.

Any "leads by N months" claim on a pillar page should trace back to a run of this.
Usage:
    python Scripts/pharos_pages/lead_calibration.py HCI
    python Scripts/pharos_pages/lead_calibration.py HCI --max-lead 36

Two rules the sweep enforces, because both are easy to get wrong:

1. Components are excluded. Correlating a composite against one of its own inputs
   measures construction, not lead. HCI is built from housing starts, existing home
   sales, months' supply, Case-Shiller and the 30Y mortgage, so all five (and near
   twins like permits) are barred as targets.

2. The peak is reported alongside the whole profile. A single argmax over a wide
   window will happily land on an edge. Read the profile before trusting the peak.
"""

from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path

import pandas as pd

DB = Path("/Users/bob/LHM/Data/databases/Lighthouse_Master.db")

# Inputs to each composite. A target in this set is circular and gets skipped.
COMPONENTS = {
    "HCI": {"HOUST", "PERMIT", "EXHOSLUSM495S", "MSACSR", "CSUSHPINSA", "MORTGAGE30US"},
}

# Non-component macro targets, with the transform each one needs.
TARGETS = {
    "UNRATE": ("Unemployment rate, 12m chg", "diff12"),
    "INDPRO": ("Industrial production YoY", "yoy"),
    "PAYEMS": ("Payrolls YoY", "yoy"),
    "RSXFS": ("Retail sales YoY", "yoy"),
    "NEWORDER": ("Core capex orders YoY", "yoy"),
    "GDPC1": ("Real GDP YoY", "yoy"),
    "PRFI": ("Residential fixed investment YoY", "yoy"),
    "ICSA": ("Initial claims YoY", "yoy"),
}

MIN_OVERLAP = 100


def monthly(conn, sid: str) -> pd.Series:
    s = pd.read_sql(
        "select date, value from observations where series_id=? order by date",
        conn, params=(sid,), parse_dates=["date"],
    ).set_index("date")["value"]
    return s.resample("MS").mean().dropna()


def transformed(s: pd.Series, how: str) -> pd.Series:
    return (s.diff(12) if how == "diff12" else s.pct_change(12) * 100).dropna()


def sweep(index_id: str, max_lead: int, window: int) -> None:
    conn = sqlite3.connect(DB)
    comp = pd.read_sql(
        "select date, value from lighthouse_indices where index_id=? order by date",
        conn, params=(index_id,), parse_dates=["date"],
    ).set_index("date")["value"]
    if comp.empty:
        sys.exit(f"No history for {index_id}")
    compm = comp.rolling(window).mean().dropna().resample("MS").mean().dropna()

    banned = COMPONENTS.get(index_id, set())
    results = []
    for sid, (label, how) in TARGETS.items():
        if sid in banned:
            print(f"  skip {sid}: input to {index_id}, correlation would be circular")
            continue
        try:
            t = transformed(monthly(conn, sid), how)
        except Exception as exc:  # noqa: BLE001
            print(f"  skip {sid}: {exc}")
            continue
        profile = {}
        for lead in range(max_lead + 1):
            shifted = compm.shift(lead)
            j = pd.concat([shifted.rename("c"), t.rename("t")], axis=1).dropna()
            if len(j) < MIN_OVERLAP:
                continue
            profile[lead] = j["c"].corr(j["t"])
        if profile:
            peak = max(profile, key=lambda k: abs(profile[k]))
            results.append((label, sid, peak, profile[peak], profile))

    results.sort(key=lambda r: -abs(r[3]))
    print(f"\n{index_id}: peak lead by target ({window}d smoothed, "
          f"min {MIN_OVERLAP} monthly overlaps)\n")
    print(f"{'target':36} {'series':11} {'lead(mo)':>9} {'corr':>7}")
    for label, sid, peak, r, _ in results:
        print(f"{label:36} {sid:11} {peak:>9} {r:>7.3f}")

    if results:
        label, sid, peak, r, profile = results[0]
        print(f"\nProfile for the strongest target ({label}):")
        for lead in sorted(profile):
            if lead % 2 == 0:
                bar = "#" * int(abs(profile[lead]) * 50)
                mark = "  <- peak" if lead == peak else ""
                print(f"  {lead:>3}mo {profile[lead]:>7.3f} {bar}{mark}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("index_id", help="composite code, e.g. HCI")
    ap.add_argument("--max-lead", type=int, default=24, help="months to sweep (default 24)")
    ap.add_argument("--window", type=int, default=21, help="smoothing window in days (default 21)")
    main_args = ap.parse_args()
    sweep(main_args.index_id.upper(), main_args.max_lead, main_args.window)


if __name__ == "__main__":
    main()
