"""
LIGHTHOUSE MACRO - MASTER PIPELINE
===================================
One database. All sources. Zero headaches.

Run daily at 06:00 ET via launchd.
"""

import sqlite3
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Tuple, Optional

from .config import DB_PATH, validate_api_keys, API_KEYS
from .fetchers import FREDFetcher, BLSFetcher, BEAFetcher, NYFedFetcher, OFRFetcher
from .market_fetchers import MarketDataFetcher
from .crypto_free_fetchers import FreeCryptoFetcher  # Replaced TokenTerminal with free APIs
from .breadth_fetcher import BreadthDataFetcher  # New: DIY breadth from S&P 500 components
from .zillow_fetcher import ZillowFetcher  # Zillow ZHVI + ZORI (free public CSVs)
from .quality import update_quality_flags

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)


# ==========================================
# DATABASE SCHEMA
# ==========================================

def init_db(db_path: Path = None) -> sqlite3.Connection:
    """Initialize the master database with unified schema."""
    db_path = db_path or DB_PATH
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Master observations table
    c.execute('''CREATE TABLE IF NOT EXISTS observations (
        series_id TEXT,
        date TEXT,
        value REAL,
        PRIMARY KEY (series_id, date)
    )''')

    # Series metadata
    c.execute('''CREATE TABLE IF NOT EXISTS series_meta (
        series_id TEXT PRIMARY KEY,
        title TEXT,
        source TEXT,
        category TEXT,
        frequency TEXT,
        units TEXT,
        last_updated TEXT,
        last_fetched TEXT,
        data_quality TEXT,
        last_value_date TEXT,
        obs_count INTEGER
    )''')

    # Update log
    c.execute('''CREATE TABLE IF NOT EXISTS update_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        source TEXT,
        series_updated INTEGER,
        observations_added INTEGER,
        duration_seconds REAL,
        status TEXT,
        errors TEXT
    )''')

    # Indexes
    c.execute('CREATE INDEX IF NOT EXISTS idx_obs_series ON observations(series_id)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_obs_date ON observations(date)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_meta_source ON series_meta(source)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_meta_category ON series_meta(category)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_meta_quality ON series_meta(data_quality)')

    conn.commit()
    logger.info(f"Database initialized: {db_path}")
    return conn


# ==========================================
# MAIN UPDATE ROUTINE
# ==========================================

def run_daily_update(
    db_path: Path = None,
    skip_quality: bool = False,
    sources: list = None
) -> Tuple[int, int]:
    """
    Master update routine - run this daily.

    Args:
        db_path: Optional custom database path
        skip_quality: Skip quality checks (faster)
        sources: List of sources to update (default: all)
            Options: ['FRED', 'BLS', 'BEA', 'NYFED', 'OFR']

    Returns:
        Tuple of (total_series_updated, total_observations_added)
    """
    start_time = time.time()
    errors = []

    print("=" * 70)
    print("LIGHTHOUSE MACRO - MASTER DATABASE UPDATE")
    print(f"Database: {db_path or DB_PATH}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    # Validate API keys
    try:
        validate_api_keys()
    except EnvironmentError as e:
        logger.error(str(e))
        print(f"\nERROR: {e}")
        print("Please set API keys in .env file or environment variables.")
        return 0, 0

    # Initialize database
    conn = init_db(db_path)

    # Default to all sources
    if sources is None:
        sources = ["FRED", "BLS", "BEA", "NYFED", "OFR", "MARKET", "CRYPTO", "BREADTH", "ZILLOW"]

    # Track totals
    total_series = 0
    total_obs = 0
    results = {}

    # Fetch each source
    if "FRED" in sources:
        print("\n--- FRED ---")
        try:
            fetcher = FREDFetcher(conn)
            series, obs = fetcher.fetch_all()
            results["FRED"] = (series, obs)
            total_series += series
            total_obs += obs
        except Exception as e:
            logger.error(f"FRED failed: {e}")
            errors.append(f"FRED: {e}")
            results["FRED"] = (0, 0)

    if "BLS" in sources:
        print("\n--- BLS ---")
        try:
            fetcher = BLSFetcher(conn)
            series, obs = fetcher.fetch_all()
            results["BLS"] = (series, obs)
            total_series += series
            total_obs += obs
        except Exception as e:
            logger.error(f"BLS failed: {e}")
            errors.append(f"BLS: {e}")
            results["BLS"] = (0, 0)

    if "BEA" in sources:
        print("\n--- BEA ---")
        try:
            fetcher = BEAFetcher(conn)
            series, obs = fetcher.fetch_all()
            results["BEA"] = (series, obs)
            total_series += series
            total_obs += obs
        except Exception as e:
            logger.error(f"BEA failed: {e}")
            errors.append(f"BEA: {e}")
            results["BEA"] = (0, 0)

    if "NYFED" in sources:
        print("\n--- NY FED ---")
        try:
            fetcher = NYFedFetcher(conn)
            series, obs = fetcher.fetch_all()
            results["NYFED"] = (series, obs)
            total_series += series
            total_obs += obs
        except Exception as e:
            logger.error(f"NYFED failed: {e}")
            errors.append(f"NYFED: {e}")
            results["NYFED"] = (0, 0)

    if "OFR" in sources:
        print("\n--- OFR ---")
        try:
            fetcher = OFRFetcher(conn)
            series, obs = fetcher.fetch_all()
            results["OFR"] = (series, obs)
            total_series += series
            total_obs += obs
        except Exception as e:
            logger.error(f"OFR failed: {e}")
            errors.append(f"OFR: {e}")
            results["OFR"] = (0, 0)

    if "MARKET" in sources:
        print("\n--- MARKET DATA (MSI/SPI) ---")
        try:
            fetcher = MarketDataFetcher(conn, API_KEYS["FRED"])
            market_results = fetcher.fetch_all()
            # Aggregate market results
            market_series = sum(r[0] for r in market_results.values())
            market_obs = sum(r[1] for r in market_results.values())
            results["MARKET"] = (market_series, market_obs)
            total_series += market_series
            total_obs += market_obs
        except Exception as e:
            logger.error(f"MARKET failed: {e}")
            errors.append(f"MARKET: {e}")
            results["MARKET"] = (0, 0)

    if "CRYPTO" in sources:
        print("\n--- CRYPTO (DefiLlama + CoinGecko) ---")
        try:
            fetcher = FreeCryptoFetcher(conn)
            crypto_series, crypto_obs = fetcher.fetch_all(price_days=30)
            results["CRYPTO"] = (crypto_series, crypto_obs)
            total_series += crypto_series
            total_obs += crypto_obs
        except Exception as e:
            logger.error(f"CRYPTO failed: {e}")
            errors.append(f"CRYPTO: {e}")
            results["CRYPTO"] = (0, 0)

    if "BREADTH" in sources:
        print("\n--- MARKET BREADTH (S&P 500 Components) ---")
        try:
            fetcher = BreadthDataFetcher(conn)
            breadth_series, breadth_obs = fetcher.fetch_and_compute(lookback_years=3)
            results["BREADTH"] = (breadth_series, breadth_obs)
            total_series += breadth_series
            total_obs += breadth_obs
        except Exception as e:
            logger.error(f"BREADTH failed: {e}")
            errors.append(f"BREADTH: {e}")
            results["BREADTH"] = (0, 0)

    if "ZILLOW" in sources:
        print("\n--- ZILLOW (ZHVI + ZORI) ---")
        try:
            fetcher = ZillowFetcher(conn)
            zillow_series, zillow_obs = fetcher.fetch_all()
            results["ZILLOW"] = (zillow_series, zillow_obs)
            total_series += zillow_series
            total_obs += zillow_obs
        except Exception as e:
            logger.error(f"ZILLOW failed: {e}")
            errors.append(f"ZILLOW: {e}")
            results["ZILLOW"] = (0, 0)

    # Run quality checks
    if not skip_quality:
        print("\n--- QUALITY CHECKS ---")
        try:
            update_quality_flags(conn)
        except Exception as e:
            logger.error(f"Quality checks failed: {e}")
            errors.append(f"Quality: {e}")

    # Log the update
    duration = time.time() - start_time
    c = conn.cursor()
    c.execute("""INSERT INTO update_log
                (timestamp, source, series_updated, observations_added, duration_seconds, status, errors)
                VALUES (?,?,?,?,?,?,?)""",
             (datetime.now().isoformat(), "ALL", total_series, total_obs, duration,
              "completed" if not errors else "completed_with_errors",
              "; ".join(errors) if errors else None))
    conn.commit()

    # Summary
    print("\n" + "=" * 70)
    print("UPDATE COMPLETE")
    print("=" * 70)

    # Database stats
    db_total_obs = conn.execute("SELECT COUNT(*) FROM observations").fetchone()[0]
    db_total_series = conn.execute("SELECT COUNT(*) FROM series_meta").fetchone()[0]
    date_range = conn.execute("SELECT MIN(date), MAX(date) FROM observations").fetchone()

    print(f"\nDatabase Statistics:")
    print(f"  Total Observations: {db_total_obs:,}")
    print(f"  Total Series: {db_total_series}")
    print(f"  Date Range: {date_range[0]} to {date_range[1]}")
    print(f"  Duration: {duration:.1f} seconds")

    print(f"\nThis Update:")
    for source, (series, obs) in results.items():
        print(f"  {source}: {series} series, {obs:,} observations")

    if errors:
        print(f"\nErrors ({len(errors)}):")
        for err in errors:
            print(f"  - {err}")

    conn.close()
    print("=" * 70)

    return total_series, total_obs


def get_stats(db_path: Path = None):
    """Print database statistics."""
    db_path = db_path or DB_PATH
    conn = sqlite3.connect(db_path)

    print("\n--- Lighthouse Master Database ---")

    total_obs = conn.execute("SELECT COUNT(*) FROM observations").fetchone()[0]
    total_series = conn.execute("SELECT COUNT(*) FROM series_meta").fetchone()[0]
    print(f"Total Observations: {total_obs:,}")
    print(f"Total Series: {total_series}")

    date_range = conn.execute("SELECT MIN(date), MAX(date) FROM observations").fetchone()
    print(f"Date Range: {date_range[0]} to {date_range[1]}")

    print("\nBy Source:")
    import pandas as pd
    by_source = pd.read_sql("""
        SELECT source, COUNT(*) as series FROM series_meta GROUP BY source
    """, conn)
    print(by_source.to_string(index=False))

    print("\nBy Category (Top 15):")
    by_cat = pd.read_sql("""
        SELECT category, COUNT(*) as series FROM series_meta GROUP BY category ORDER BY series DESC LIMIT 15
    """, conn)
    print(by_cat.to_string(index=False))

    # Quality summary
    print("\nData Quality:")
    quality = pd.read_sql("""
        SELECT data_quality, COUNT(*) as series FROM series_meta
        WHERE data_quality IS NOT NULL
        GROUP BY data_quality
    """, conn)
    if not quality.empty:
        print(quality.to_string(index=False))

    print("\nRecent Updates:")
    updates = pd.read_sql("""
        SELECT timestamp, source, series_updated, observations_added, duration_seconds, status
        FROM update_log ORDER BY id DESC LIMIT 5
    """, conn)
    print(updates.to_string(index=False))

    conn.close()


# ==========================================
# CLI ENTRY POINT
# ==========================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Lighthouse Macro Data Pipeline")
    parser.add_argument("--stats", action="store_true", help="Show database statistics only")
    parser.add_argument("--skip-quality", action="store_true", help="Skip quality checks")
    parser.add_argument("--sources", nargs="+", choices=["FRED", "BLS", "BEA", "NYFED", "OFR", "MARKET"],
                       help="Only update specific sources")

    args = parser.parse_args()

    if args.stats:
        get_stats()
    else:
        run_daily_update(
            skip_quality=args.skip_quality,
            sources=args.sources
        )
        get_stats()
