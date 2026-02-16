#!/usr/bin/env python3
"""
LIGHTHOUSE MACRO - DAILY PIPELINE RUNNER
========================================
Run this script daily at 06:00 ET via launchd.

Usage:
    python run_pipeline.py              # Full update with quality checks
    python run_pipeline.py --stats      # Just show database stats
    python run_pipeline.py --quick      # Skip quality checks (faster)
    python run_pipeline.py --fred-only  # Only update FRED
"""

import sys
import os
import shutil
from datetime import datetime
from pathlib import Path

# Add the lighthouse package to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Change to script directory so .env is found
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from lighthouse.pipeline import run_daily_update, get_stats
from lighthouse.config import DB_PATH
from compute_indices import compute_all_indices, write_indices_to_db, verify_indices, DB_PATH as INDICES_DB_PATH
from compute_crypto_indices import compute_all_crypto_indices, write_crypto_indices_to_db, verify_crypto_indices
import sqlite3

# Backup destination
LHM_BACKUP_DIR = Path("/Users/bob/LHM/Data/databases/backups")


def backup_database():
    """Copy database to LHM folder with timestamp."""
    try:
        LHM_BACKUP_DIR.mkdir(parents=True, exist_ok=True)

        # Daily backup with date
        if DB_PATH.exists():
            date_str = datetime.now().strftime("%Y%m%d")
            dated_dest = LHM_BACKUP_DIR / f"Lighthouse_Master_{date_str}.db"
            if not dated_dest.exists():
                shutil.copy2(DB_PATH, dated_dest)

            print(f"Database backed up to {LHM_BACKUP_DIR}")

            # Clean up old backups (keep last 7 days)
            cleanup_old_backups()
    except Exception as e:
        print(f"WARNING: Backup failed: {e}")


def cleanup_old_backups():
    """Remove backups older than 7 days."""
    try:
        cutoff = datetime.now().timestamp() - (7 * 24 * 60 * 60)
        for f in LHM_BACKUP_DIR.glob("Lighthouse_Master_*.db"):
            if f.stat().st_mtime < cutoff:
                f.unlink()
                print(f"Removed old backup: {f.name}")
    except Exception as e:
        print(f"WARNING: Cleanup failed: {e}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Lighthouse Macro Data Pipeline")
    parser.add_argument("--stats", action="store_true", help="Show database statistics only")
    parser.add_argument("--quick", action="store_true", help="Skip quality checks")
    parser.add_argument("--fred-only", action="store_true", help="Only update FRED")
    parser.add_argument("--sources", nargs="+",
                       choices=["FRED", "BLS", "BEA", "NYFED", "OFR", "MARKET", "CRYPTO", "ZILLOW"],
                       help="Only update specific sources")
    parser.add_argument("--skip-indices", action="store_true",
                       help="Skip proprietary index computation")

    args = parser.parse_args()

    if args.stats:
        get_stats()
        return

    sources = None
    if args.fred_only:
        sources = ["FRED"]
    elif args.sources:
        sources = args.sources

    run_daily_update(
        skip_quality=args.quick,
        sources=sources
    )

    # Compute proprietary indices
    if not args.skip_indices:
        print("\n" + "=" * 70)
        print("COMPUTING PROPRIETARY INDICES")
        print("=" * 70)
        try:
            conn = sqlite3.connect(INDICES_DB_PATH)
            indices_df = compute_all_indices(conn, latest_only=True)
            write_indices_to_db(conn, indices_df)
            verify_indices(conn)
            conn.close()
            print("Index computation complete.")
        except Exception as e:
            print(f"ERROR computing indices: {e}")

        # Compute crypto indices (if crypto data was pulled)
        print("\n" + "=" * 70)
        print("COMPUTING CRYPTO INDICES")
        print("=" * 70)
        try:
            conn = sqlite3.connect(INDICES_DB_PATH)
            # Check if crypto tables exist
            c = conn.cursor()
            c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='crypto_scores'")
            if c.fetchone():
                crypto_indices_df = compute_all_crypto_indices(conn, latest_only=True)
                if not crypto_indices_df.empty:
                    write_crypto_indices_to_db(conn, crypto_indices_df)
                    verify_crypto_indices(conn)
                    print("Crypto index computation complete.")
                else:
                    print("No crypto data available for index computation.")
            else:
                print("Crypto tables not found - run with --sources CRYPTO to populate.")
            conn.close()
        except Exception as e:
            print(f"ERROR computing crypto indices: {e}")

    get_stats()

    # Backup to LHM folder
    backup_database()

    # Sync to all destinations (GitHub, iCloud, GDrive, Dropbox)
    try:
        from sync_all import sync_to_all_destinations
        sync_to_all_destinations()
    except Exception as e:
        print(f"WARNING: Post-pipeline sync failed: {e}")


if __name__ == "__main__":
    main()
