#!/usr/bin/env python3
"""
LIGHTHOUSE MACRO — INDICATOR FRESHNESS AUDIT
============================================

The "once and for all" guard. Every proprietary indicator in
`lighthouse_indices` is supposed to be daily forward-filled and nowcast
through yesterday's close. This script proves it (or names exactly what
isn't), so the silent-staleness incident (macro composites froze 2026-05-17
-> 2026-06-15 while the pipeline limped in latest_only mode) can't recur
undetected.

Usage:
    python indicator_freshness_audit.py            # full report
    python indicator_freshness_audit.py --fail-stale   # exit 1 if any STALE
    python indicator_freshness_audit.py --json         # machine-readable

Wire into run_pipeline.py (after index computation) or the morning brief.
"""

import argparse
import json
import sqlite3
import sys
from datetime import datetime, timedelta

DB_PATH = "/Users/bob/LHM/Data/databases/Lighthouse_Master.db"

# Per-indicator tolerance in CALENDAR days before we call it stale. Daily-native
# composites should never be more than a long weekend behind; monthly-fed
# composites are daily-forward-filled so they too should track to ~yesterday,
# but we allow a little slack for release/publish windows. Crypto is on its own
# (broken feed) cadence until the fetcher is repaired.
TOLERANCE_DAYS = {
    "_daily_default": 4,     # daily-native: MSI, SPI, SBD, SSD, REC_PROB, etc.
    "_macro_default": 5,     # monthly-fed but daily-FF: LPI, PCI, GCI, ...
    "_crypto_default": 9999,  # SLI/CTI/CVI/CRYPTO_* — known-broken feed, don't alarm
}

# Indicators whose freshness is gated by a daily-FF macro nowcast (not a live
# market feed). Everything else defaults to the daily tolerance.
MACRO_COMPOSITES = {
    "LPI", "LFI", "LDI", "PCI", "GCI", "HCI", "CCI", "BCI", "TCI", "FPI",
    "FCI", "LCI", "CLG", "MRI", "YFS", "SVI", "EMD", "LIQ_STAGE", "BILL_SOFR",
}
CRYPTO_PREFIXES = ("SLI", "CDI", "CFI", "CTI", "CVI", "CRYPTO_")


def tolerance_for(index_id: str) -> int:
    if any(index_id.startswith(p) for p in CRYPTO_PREFIXES):
        return TOLERANCE_DAYS["_crypto_default"]
    if index_id in MACRO_COMPOSITES:
        return TOLERANCE_DAYS["_macro_default"]
    return TOLERANCE_DAYS["_daily_default"]


def audit(db_path: str = DB_PATH):
    conn = sqlite3.connect(db_path)
    rows = conn.execute(
        """
        SELECT index_id, COUNT(*) n, MIN(date) first, MAX(date) last
        FROM lighthouse_indices GROUP BY index_id
        """
    ).fetchall()

    # Also flag flat-lined tails (value hasn't moved in the last 10 distinct
    # dates) for daily-native composites — a different failure mode than stale.
    today = datetime.now().date()
    results = []
    for index_id, n, first, last in rows:
        last_d = datetime.fromisoformat(last).date()
        stale_days = (today - last_d).days
        tol = tolerance_for(index_id)
        is_crypto = any(index_id.startswith(p) for p in CRYPTO_PREFIXES)

        # flat-tail check (daily-native only)
        flat = False
        if not is_crypto and index_id not in MACRO_COMPOSITES:
            tail = conn.execute(
                "SELECT value FROM lighthouse_indices WHERE index_id=? "
                "ORDER BY date DESC LIMIT 10",
                (index_id,),
            ).fetchall()
            vals = [r[0] for r in tail if r[0] is not None]
            if len(vals) >= 5 and len(set(round(v, 6) for v in vals)) == 1:
                flat = True

        if is_crypto:
            verdict = "CRYPTO_FEED_DOWN" if stale_days > 30 else "OK"
        elif stale_days > tol:
            verdict = "STALE"
        elif flat:
            verdict = "FLAT_TAIL"
        else:
            verdict = "OK"

        results.append({
            "index_id": index_id,
            "n": n,
            "first": first[:10],
            "last": last[:10],
            "stale_days": stale_days,
            "tolerance": tol,
            "verdict": verdict,
        })
    conn.close()
    results.sort(key=lambda r: (r["verdict"] == "OK", -r["stale_days"]))
    return results


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fail-stale", action="store_true",
                    help="exit 1 if any indicator is STALE (for CI / launchd)")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args()

    results = audit()

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print("=" * 78)
        print(f"INDICATOR FRESHNESS AUDIT — {datetime.now():%Y-%m-%d %H:%M}")
        print("=" * 78)
        hdr = f"{'INDEX':<34} {'LAST':<12} {'STALE':>6} {'N':>7}  VERDICT"
        print(hdr)
        print("-" * 78)
        for r in results:
            flag = "" if r["verdict"] == "OK" else "  <<<"
            print(f"{r['index_id']:<34} {r['last']:<12} "
                  f"{r['stale_days']:>5}d {r['n']:>7}  {r['verdict']}{flag}")
        stale = [r for r in results if r["verdict"] == "STALE"]
        flat = [r for r in results if r["verdict"] == "FLAT_TAIL"]
        down = [r for r in results if r["verdict"] == "CRYPTO_FEED_DOWN"]
        print("-" * 78)
        print(f"OK: {sum(1 for r in results if r['verdict']=='OK')} | "
              f"STALE: {len(stale)} | FLAT: {len(flat)} | CRYPTO_DOWN: {len(down)}")
        if stale:
            print("\nSTALE (real-time guarantee broken — fix the pipeline):")
            for r in stale:
                print(f"   {r['index_id']}  last {r['last']} ({r['stale_days']}d)")

    if args.fail_stale and any(r["verdict"] == "STALE" for r in results):
        sys.exit(1)


if __name__ == "__main__":
    main()
