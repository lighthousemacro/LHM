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
# but we allow a little slack for release/publish windows. Crypto (CLI, SLI +
# variants, CDLI) is live free-data since the 2026-07-09 rewire — DefiLlama /
# CoinGecko feeds are daily but can lag a day, so give them macro-style slack.
# The old 9999 amnesty is GONE: everything still dead was purged, so anything
# crypto going stale now is a real pipeline break.
TOLERANCE_DAYS = {
    "_daily_default": 4,     # daily-native: MSI, SPI, SBD, SSD, REC_PROB, etc.
    "_macro_default": 5,     # monthly-fed but daily-FF: LPI, PCI, GCI, ...
    "_crypto_default": 5,    # CLI/SLI*/CRYPTO_DEFI_LIQUIDITY — live DefiLlama+CoinGecko
}

# Indicators whose freshness is gated by a daily-FF macro nowcast (not a live
# market feed). Everything else defaults to the daily tolerance.
MACRO_COMPOSITES = {
    "LPI", "LFI", "LDI", "PCI", "GCI", "HCI", "CCI", "BCI", "TCI", "FPI",
    "FCI", "LCI", "CLG", "MRI", "YFS", "SVI", "EMD", "LIQ_STAGE", "BILL_SOFR",
    # Descriptive/diagnostic expansion (daily-FF monthly composites, 2026-06-15)
    "SUPERCORE_HEAT", "PERSISTENCE_GAP", "PIPELINE_IMPULSE", "TREND_HEAT",
    "AFFORD_PRESSURE", "FROZEN_DIVERGENCE", "INTEREST_CROWDOUT", "QUALITY_PRESSURE",
    "VOL_TERM_GAP", "FCI_CHANNELS", "CAPACITY_SLACK",
}
CRYPTO_PREFIXES = ("SLI", "CLI", "CRYPTO_")

# Retired paid-fundamentals lineup (crypto_scores feed died 2026-02-02, Bob
# declined a paid replacement; zombie rows purged from lighthouse_indices
# 2026-07-09). These ids should NOT exist — if any reappear, something
# re-inserted zombies and we flag it loudly instead of amnestying it.
RETIRED_CRYPTO = ("CDI", "CFI", "CTI", "CVI")


def is_retired(index_id: str) -> bool:
    return (index_id in RETIRED_CRYPTO
            or (index_id.startswith("CRYPTO_") and index_id.endswith("_HEALTH")))


def tolerance_for(index_id: str) -> int:
    if any(index_id.startswith(p) for p in CRYPTO_PREFIXES):
        return TOLERANCE_DAYS["_crypto_default"]
    if index_id in MACRO_COMPOSITES:
        return TOLERANCE_DAYS["_macro_default"]
    return TOLERANCE_DAYS["_daily_default"]


# History-depth guards (observations table). A canonical series whose history
# suddenly starts "recently" means a backfill was lost or a fetcher recreated
# the series from scratch — the failure mode that made breadth charts start in
# 2024 three separate times. Splice provenance (2026-07-06): TradingView
# INDEX:S5TH/S5FI/S5TW history before 2024-05-01, Lighthouse-computed
# constituent breadth after. min(date) must be on or before these dates.
DEPTH_GUARDS = {
    "SPX_PCT_ABOVE_200D": "2008-01-01",
    "SPX_PCT_ABOVE_50D": "2008-01-01",
    "SPX_PCT_ABOVE_20D": "2008-01-01",
    # CLI/SLI feed series (backfilled 2026-07-09: BTC via yfinance history,
    # stablecoin mcap via DefiLlama full per-asset history). The CoinGecko
    # daily fetch only writes a trailing 30d window, so lost backfill would
    # silently gut the rolling 756d z-windows — exactly what this guard is for.
    "CRYPTO_BTC_PRICE": "2015-01-01",
    "STABLECOIN_TOTAL_MCAP": "2018-01-01",
}

# Value-plausibility ceilings for depth-guarded feed series. 2026-07-09: 11
# CRYPTO_BTC_PRICE rows in Jan 2026 held values near $32M (bad fetcher writes),
# which silently poisoned CLI's StableBTC z-scores for six weeks. Depth and
# staleness checks can't see that; a ceiling can.
VALUE_CEILINGS = {
    "CRYPTO_BTC_PRICE": 500_000,
}


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

        # flat-tail check (daily-native only, crypto included — CLI/SLI move
        # every day). Exempt daily-FF'd monthly composites (macro pillars +
        # ALLOC_*): they're legitimately flat between monthly releases by
        # design.
        flat = False
        if (index_id not in MACRO_COMPOSITES
                and not index_id.startswith("ALLOC_")):
            tail = conn.execute(
                "SELECT value FROM lighthouse_indices WHERE index_id=? "
                "ORDER BY date DESC LIMIT 10",
                (index_id,),
            ).fetchall()
            vals = [r[0] for r in tail if r[0] is not None]
            if len(vals) >= 5 and len(set(round(v, 6) for v in vals)) == 1:
                flat = True

        if is_retired(index_id):
            verdict = "RETIRED_ZOMBIE"
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
    # observations-table history-depth guards (see DEPTH_GUARDS above)
    for sid, need_start in DEPTH_GUARDS.items():
        row = conn.execute(
            "SELECT COUNT(*), MIN(date), MAX(date) FROM observations "
            "WHERE series_id=?", (sid,)
        ).fetchone()
        n, first, last = row
        if n == 0:
            verdict, first, last, stale_days = "SHALLOW_HISTORY", "-", "-", 9999
        else:
            stale_days = (today - datetime.fromisoformat(last).date()).days
            verdict = "SHALLOW_HISTORY" if first > need_start else "OK"
            # Interior zero-run guard: a breadth percentage sitting at exactly
            # 0.0 for 5+ consecutive rows is fetcher warm-up garbage, not data
            # (2026-07-09: 199/49/19 such rows found INSIDE spliced canonicals
            # that passed the depth check). Depth alone can't see this.
            if verdict == "OK":
                zrow = conn.execute(
                    "SELECT COUNT(*) FROM observations "
                    "WHERE series_id=? AND value=0", (sid,)
                ).fetchone()
                if zrow[0] >= 5:
                    verdict = "ZERO_RUN"
            # Value-plausibility ceiling (see VALUE_CEILINGS above)
            if verdict == "OK" and sid in VALUE_CEILINGS:
                bad = conn.execute(
                    "SELECT COUNT(*) FROM observations "
                    "WHERE series_id=? AND value > ?",
                    (sid, VALUE_CEILINGS[sid]),
                ).fetchone()
                if bad[0] > 0:
                    verdict = "IMPLAUSIBLE_VALUE"
        results.append({
            "index_id": f"{sid} (obs depth)",
            "n": n,
            "first": (first or "-")[:10],
            "last": (last or "-")[:10],
            "stale_days": stale_days,
            "tolerance": 0,
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
        zombies = [r for r in results if r["verdict"] == "RETIRED_ZOMBIE"]
        print("-" * 78)
        print(f"OK: {sum(1 for r in results if r['verdict']=='OK')} | "
              f"STALE: {len(stale)} | FLAT: {len(flat)} | ZOMBIE: {len(zombies)}")
        if stale:
            print("\nSTALE (real-time guarantee broken — fix the pipeline):")
            for r in stale:
                print(f"   {r['index_id']}  last {r['last']} ({r['stale_days']}d)")
        if zombies:
            print("\nRETIRED_ZOMBIE (purged 2026-07-09; something re-inserted them):")
            for r in zombies:
                print(f"   {r['index_id']}  last {r['last']}")

    if args.fail_stale and any(r["verdict"] in ("STALE", "SHALLOW_HISTORY", "ZERO_RUN",
                                                "RETIRED_ZOMBIE", "IMPLAUSIBLE_VALUE")
                               for r in results):
        sys.exit(1)


if __name__ == "__main__":
    main()
