#!/usr/bin/env python3
"""
LIGHTHOUSE MACRO - RELEASE-DAY FRESHNESS CHECK
==============================================
Lightweight mid-morning refresh that targets release-sensitive FRED series.

Problem: the daily 06:00 ET pipeline runs before FRED mirrors the morning
Census/BEA/BLS economic releases (typically ~08:30 ET). Retail, industrial
production, housing starts, PCE, CPI, PPI, trade balance, and the
employment situation report all land after the morning pipeline has
already fetched. Without this script we miss same-day data on release
mornings and need a manual re-pull.

Design (Option C from the fix spec):
- Keep the 06:00 ET full pipeline untouched.
- Add a narrow, scheduled check at ~10:00 ET that only hits FRED /series
  metadata for a small list of release-sensitive IDs.
- For any series where FRED's `observation_end` is newer than max(date)
  in `Lighthouse_Master.db`, re-fetch that series via the existing
  FREDFetcher._fetch_series() path. No new write path, no fabricated data,
  no duplicate fetches when nothing changed.

Cost budget:
- One /series metadata call per release-sensitive ticker (~50 ids).
- Zero observation fetches unless FRED has newer data than the DB.
- Typical release day: 1-5 series actually get re-fetched.

Usage:
    python check_for_updates.py              # Run the check, fetch any updates
    python check_for_updates.py --dry-run    # Print what would update, fetch nothing
    python check_for_updates.py --verbose    # Per-series trace

PYTHONPATH: /Users/bob/LHM
"""

import argparse
import logging
import os
import sqlite3
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Make the `lighthouse` package importable when this file is run directly.
_THIS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_THIS_DIR))
os.chdir(_THIS_DIR)  # so .env next to the package resolves

from lighthouse.config import API_KEYS, DB_PATH, FETCH_CONFIG, FRED_CURATED  # noqa: E402
from lighthouse.fetchers import FREDFetcher, fetch_with_retry  # noqa: E402


# ==========================================
# LOGGING
# ==========================================

LOG_DIR = Path("/Users/bob/LHM/logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_PATH = LOG_DIR / "pipeline_freshness.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(LOG_PATH),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("freshness_check")


# ==========================================
# RELEASE-SENSITIVE SERIES LIST
# ==========================================
# Kept short on purpose. These are FRED series that mirror government
# data releases which typically drop mid-morning ET (after the 06:00 ET
# pipeline run) and which we actively use in published research.
#
# To extend: add the FRED series id to the appropriate bucket below.
# The scheduler is dumb; it checks every entry regardless of release
# calendar, relying on FRED's observation_end to be the source of truth.

RELEASE_SENSITIVE_SERIES: Dict[str, List[str]] = {
    # Census: Advance Monthly Retail Trade (~08:30 ET day of release)
    "retail": [
        "RSAFS", "RSXFS", "RSFSDP", "RSMVPD", "RSGASS",
        "RSBMGESD", "RSFHFS", "RSEAS", "RSCCAS", "RSSGHBMS",
        "RSHPCS", "RSNSR", "RSGMS", "RSDBS", "RSMSR",
        "RSGCSN", "RRSFS", "RSFSXMV",
    ],
    # BLS: CPI (~08:30 ET)
    "cpi": [
        "CPIAUCSL", "CPILFESL", "CUSR0000SAH1", "CUSR0000SEHA",
        "CUSR0000SEHC", "CUSR0000SAS", "CUSR0000SACL1E",
        "MEDCPIM158SFRBCLE", "CORESTICKM159SFRBATL",
    ],
    # BLS: PPI (~08:30 ET)
    "ppi": [
        "PPIFIS", "PPIFGS", "PPIDSS", "PPIFDS",
    ],
    # BEA: Personal Income & Outlays / PCE (~08:30 ET, end of month)
    "pce": [
        "PCEPI", "PCEPILFE", "PCE", "PCEDG", "PCEND", "PCES",
        "PSAVERT", "DSPIC96",
    ],
    # BLS: Employment Situation (~08:30 ET, first Friday)
    "employment": [
        "PAYEMS", "UNRATE", "U6RATE", "CIVPART", "AWHAETP",
        "CES0500000003",  # Avg Hourly Earnings, if present
    ],
    # BLS: JOLTS (~10:00 ET, ~6 weeks lag)
    "jolts": [
        "JTSJOL", "JTSHIL", "JTSQUL", "JTSQUR",
        "JTSHIR", "JTSTSR", "JTS1000JOR", "JTS1000QUR", "JTS1000HIR",
    ],
    # BLS: Weekly Claims (~08:30 ET every Thursday)
    "claims": ["ICSA", "CCSA"],
    # Fed: Industrial Production (~09:15 ET, mid-month)
    "industrial_production": ["INDPRO"],
    # Census: New Residential Construction (~08:30 ET)
    "housing_starts": ["HOUST", "PERMIT", "PERMIT1", "COMPUTSA", "UNDCONTSA"],
    # Census: New Home Sales (~10:00 ET)
    "new_home_sales": ["HSN1F", "MSPNHSUS", "MSACSR"],
    # NAR: Existing Home Sales mirror (~10:00 ET)
    "existing_home_sales": ["EXHOSLUSM495S", "HOSINVUSM495N"],
    # BEA: International Trade in Goods and Services (~08:30 ET)
    "trade": ["BOPGSTB", "BOPGTB", "NETEXP"],
    # Census: Durable Goods (~08:30 ET)
    "durable_goods": ["DGORDER", "ADXTNO", "NEWORDER", "ANDENO"],
    # BEA: GDP (~08:30 ET, quarterly)
    "gdp": ["GDP", "GDPC1"],
    # Conference Board / UMich sentiment (~10:00 ET)
    "sentiment": ["UMCSENT", "MICH"],
    # Consumer Credit (~15:00 ET, monthly — technically PM, harmless to include)
    "consumer_credit": ["TOTALSL"],
}


def _flatten_series_ids() -> List[str]:
    """Flatten the release-sensitive buckets into a deduped, FRED_CURATED-filtered list."""
    seen = set()
    out: List[str] = []
    for bucket, ids in RELEASE_SENSITIVE_SERIES.items():
        for sid in ids:
            if sid in seen:
                continue
            seen.add(sid)
            # Only check series we already manage. Avoids bootstrapping
            # a brand-new series out of a freshness hook.
            if sid in FRED_CURATED:
                out.append(sid)
            else:
                logger.debug(f"Skipping {sid} from bucket '{bucket}' - not in FRED_CURATED")
    return out


# ==========================================
# FRED METADATA CALL
# ==========================================

FRED_SERIES_URL = "https://api.stlouisfed.org/fred/series"


def fred_observation_end(series_id: str, api_key: str) -> Optional[str]:
    """
    Return the FRED `observation_end` date (YYYY-MM-DD) for a series.
    Returns None if FRED can't be reached or the series is missing.
    """
    params = {
        "series_id": series_id,
        "api_key": api_key,
        "file_type": "json",
    }
    try:
        data = fetch_with_retry(FRED_SERIES_URL, params)
    except Exception as e:
        logger.warning(f"{series_id}: FRED /series call failed: {e}")
        return None

    items = data.get("seriess") or []
    if not items:
        return None
    return items[0].get("observation_end")


# ==========================================
# DB LOOKUPS
# ==========================================


def db_last_observation_date(conn: sqlite3.Connection, series_id: str) -> Optional[str]:
    """Return the max(date) stored in `observations` for this series, or None if absent."""
    cur = conn.execute(
        "SELECT MAX(date) FROM observations WHERE series_id = ?",
        (series_id,),
    )
    row = cur.fetchone()
    if not row:
        return None
    return row[0]


def db_last_observation_dates_bulk(conn: sqlite3.Connection, series_ids: List[str]) -> Dict[str, Optional[str]]:
    """
    Return {series_id: max(date)} for all requested series in a single query.
    This is the preferred path for the freshness check - one short-lived
    DB read instead of N round-trips that can each hit a writer-held lock.
    """
    if not series_ids:
        return {}
    # Chunk to avoid the SQLite variable limit (default 999).
    out: Dict[str, Optional[str]] = {sid: None for sid in series_ids}
    CHUNK = 500
    for i in range(0, len(series_ids), CHUNK):
        chunk = series_ids[i : i + CHUNK]
        placeholders = ",".join("?" * len(chunk))
        sql = (
            f"SELECT series_id, MAX(date) FROM observations "
            f"WHERE series_id IN ({placeholders}) GROUP BY series_id"
        )
        for sid, max_date in conn.execute(sql, chunk):
            out[sid] = max_date
    return out


# ==========================================
# MAIN CHECK
# ==========================================


def run_check(dry_run: bool = False, verbose: bool = False) -> Tuple[int, int]:
    """
    Walk the release-sensitive series list. For each series where FRED's
    `observation_end` is newer than the DB's last observation date,
    re-fetch via FREDFetcher. Returns (refreshed_series, total_obs_added).
    """
    api_key = API_KEYS.get("FRED")
    if not api_key:
        logger.error("FRED_API_KEY not set; aborting freshness check.")
        return (0, 0)

    series_ids = _flatten_series_ids()
    if verbose:
        logger.info(f"Checking {len(series_ids)} release-sensitive series.")

    if not DB_PATH.exists():
        logger.error(f"Database missing at {DB_PATH}; aborting.")
        return (0, 0)

    # --- Pass 1: FRED metadata (no DB) ---
    # Do all the network calls first so we never hold a DB connection
    # while waiting on FRED.
    fred_ends: Dict[str, Optional[str]] = {}
    for sid in series_ids:
        fred_ends[sid] = fred_observation_end(sid, api_key)
        time.sleep(FETCH_CONFIG.get("rate_limit_delay", 0.1))

    # --- Pass 2: one bulk DB read, with retry on lock ---
    db_ends: Dict[str, Optional[str]] = {}
    last_err: Optional[Exception] = None
    for attempt in range(6):  # ~ up to ~2 min total wait across backoff
        try:
            read_conn = sqlite3.connect(DB_PATH, timeout=60.0)
            try:
                db_ends = db_last_observation_dates_bulk(read_conn, series_ids)
            finally:
                read_conn.close()
            break
        except sqlite3.OperationalError as e:
            last_err = e
            wait = 2 ** attempt
            logger.warning(
                f"DB read attempt {attempt + 1} failed ({e}); waiting {wait}s."
            )
            time.sleep(wait)
    else:
        logger.error(f"Giving up on DB read: {last_err}")
        return (0, 0)

    # --- Compare ---
    stale_series: List[Tuple[str, str, str]] = []  # (series_id, db_end, fred_end)
    for sid in series_ids:
        fred_end = fred_ends.get(sid)
        db_end = db_ends.get(sid)

        if fred_end is None:
            if verbose:
                logger.info(f"  {sid}: no FRED metadata (skipping)")
            continue
        if db_end is None:
            stale_series.append((sid, "<missing>", fred_end))
            if verbose:
                logger.info(f"  {sid}: not in DB yet, FRED has {fred_end}")
            continue
        if fred_end > db_end:
            stale_series.append((sid, db_end, fred_end))
            if verbose:
                logger.info(f"  {sid}: stale (db={db_end}, fred={fred_end})")
        elif verbose:
            logger.info(f"  {sid}: up-to-date (db=fred={db_end})")

    if not stale_series:
        logger.info("All release-sensitive series are up-to-date. Nothing to fetch.")
        return (0, 0)

    logger.info(
        "Stale series (%d):\n  %s",
        len(stale_series),
        "\n  ".join(
            f"{sid}: db={db_end} -> fred={fred_end}"
            for sid, db_end, fred_end in stale_series
        ),
    )

    if dry_run:
        logger.info("--dry-run: skipping fetches.")
        return (len(stale_series), 0)

    # Open the writer connection now, once we know we have work to do.
    # Long busy_timeout so we coexist with any late-running pipeline stage
    # or the 15-minute sync_all.py push.
    conn = sqlite3.connect(DB_PATH, timeout=60.0)
    fetcher = FREDFetcher(conn)

    # Re-fetch each stale series via the existing FREDFetcher path.
    # This reuses retry/backoff, rate limiting, and the INSERT OR REPLACE
    # observation write path used by the daily pipeline.
    refreshed = 0
    obs_added = 0
    for sid, _, _ in stale_series:
        try:
            title = FRED_CURATED.get(sid, sid)
            series_info = {"id": sid, "title": title}
            u, o = fetcher._fetch_series(sid, series_info, "Curated")
            refreshed += u
            obs_added += o
            logger.info(f"  {sid}: refreshed (+{o} obs)")
        except Exception as e:
            logger.error(f"  {sid}: fetch failed: {e}")
        time.sleep(FETCH_CONFIG.get("rate_limit_delay", 0.1))

    # Log to the existing update_log table so this shows up alongside
    # the full-pipeline runs in any audit query.
    try:
        conn.execute(
            """INSERT INTO update_log
                (timestamp, source, series_updated, observations_added, duration_seconds, status, errors)
                VALUES (?,?,?,?,?,?,?)""",
            (
                datetime.now().isoformat(),
                "FRED_FRESHNESS_CHECK",
                refreshed,
                obs_added,
                0.0,
                "completed",
                None,
            ),
        )
        conn.commit()
    except Exception as e:
        logger.warning(f"update_log insert failed: {e}")

    conn.close()

    logger.info(
        f"Freshness check done: {refreshed} series refreshed, {obs_added:,} obs added."
    )
    return (refreshed, obs_added)


# ==========================================
# CLI
# ==========================================


def main() -> int:
    parser = argparse.ArgumentParser(description="Lighthouse pipeline freshness check")
    parser.add_argument("--dry-run", action="store_true", help="List stale series without fetching")
    parser.add_argument("--verbose", "-v", action="store_true", help="Per-series trace")
    args = parser.parse_args()

    refreshed, obs = run_check(dry_run=args.dry_run, verbose=args.verbose)
    # Exit 0 whether or not anything was stale; non-zero only on hard failure.
    return 0


if __name__ == "__main__":
    sys.exit(main())
