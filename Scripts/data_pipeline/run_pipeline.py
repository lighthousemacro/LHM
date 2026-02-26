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
                       choices=["FRED", "BLS", "BEA", "NYFED", "OFR", "MARKET", "CRYPTO", "ZILLOW", "TRADINGVIEW"],
                       help="Only update specific sources")
    parser.add_argument("--skip-indices", action="store_true",
                       help="Skip proprietary index computation")
    parser.add_argument("--skip-pillars", action="store_true",
                       help="Skip pillar sub-database build")
    parser.add_argument("--build-pillars", action="store_true",
                       help="Only build pillar sub-databases (skip data fetch)")

    args = parser.parse_args()

    if args.stats:
        get_stats()
        return

    if args.build_pillars:
        print("\n" + "=" * 70)
        print("BUILDING PILLAR SUB-DATABASES (standalone)")
        print("=" * 70)
        try:
            from build_pillar_dbs import main as build_pillars_main
            sys.argv = [sys.argv[0]]  # Reset argv for sub-parser
            build_pillars_main()
        except Exception as e:
            print(f"ERROR building pillar DBs: {e}")
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

    # Rebuild horizon dataset (transforms raw observations -> z-scores for index computation)
    if not args.skip_indices:
        print("\n" + "=" * 70)
        print("REBUILDING HORIZON DATASET")
        print("=" * 70)
        try:
            from horizon_dataset_builder import build_horizon_dataset
            build_horizon_dataset()
        except Exception as e:
            print(f"WARNING: Horizon dataset rebuild failed: {e}")

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

    # Run threshold alerts
    print("\n" + "=" * 70)
    print("THRESHOLD ALERTS")
    print("=" * 70)
    try:
        from threshold_alerts import (
            load_state, save_state, get_latest_indices as get_alert_indices,
            evaluate_rules, detect_status_transitions, format_alert_log,
            format_alerts_md, send_notification,
            ALERT_LOG_PATH, ALERT_MD_PATH, STATE_PATH
        )
        import sqlite3 as _sqlite3

        _conn = _sqlite3.connect(INDICES_DB_PATH)
        _state = load_state()
        _current = get_alert_indices(_conn)
        _alerts = evaluate_rules(_current, _state)
        _transitions = detect_status_transitions(_current, _state)

        _log_entry = format_alert_log(_alerts, _transitions)
        _md_content = format_alerts_md(_alerts, _transitions, _current)

        ALERT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        ALERT_MD_PATH.parent.mkdir(parents=True, exist_ok=True)
        ALERT_MD_PATH.write_text(_md_content)
        with open(ALERT_LOG_PATH, "a") as _f:
            _f.write(_log_entry + "\n")

        # Update state
        for _a in _alerts:
            _key = _a.get("rule_key", _a.get("index", "unknown"))
            _state.setdefault("active_alerts", {})[_key] = {
                "triggered": datetime.now().isoformat(),
                "severity": _a["severity"],
                "msg": _a["msg"],
            }
        _state["index_states"] = {
            _idx: {"value": _info["value"], "status": _info["status"], "date": _info["date"]}
            for _idx, _info in _current.items()
        }
        _state["last_check"] = datetime.now().isoformat()
        save_state(_state)

        if _alerts or _transitions:
            for _t in _transitions:
                print(f"  TRANSITION: {_t['index']} {_t['from_status']} -> {_t['to_status']}")
            for _a in _alerts:
                print(f"  [{_a['severity']}] {_a['msg']}")
        else:
            print("  No new alerts or transitions.")

        _conn.close()
    except Exception as e:
        print(f"WARNING: Threshold alerts failed: {e}")

    # Generate morning brief
    print("\n" + "=" * 70)
    print("MORNING BRIEF")
    print("=" * 70)
    try:
        from morning_brief import build_brief, build_notification_summary, send_notification as send_brief_notify, log_brief
        import sqlite3 as _sqlite3b

        _conn2 = _sqlite3b.connect(INDICES_DB_PATH)
        _brief = build_brief(_conn2)
        _output_path = Path.home() / "Desktop" / "LHM_Morning_Brief.html"
        _output_path.write_text(_brief)
        log_brief(_brief)
        _summary = build_notification_summary(_conn2)
        send_brief_notify("LHM Morning Brief", _summary)
        print(f"  Brief written to {_output_path}")
        print(f"  Notification: {_summary}")
        _conn2.close()
    except Exception as e:
        print(f"WARNING: Morning brief failed: {e}")

    # Build pillar sub-databases
    if not args.skip_pillars:
        print("\n" + "=" * 70)
        print("BUILDING PILLAR SUB-DATABASES")
        print("=" * 70)
        try:
            from build_pillar_dbs import build_pillar_db, show_stats, PILLAR_DB_DIR
            PILLAR_DB_DIR.mkdir(parents=True, exist_ok=True)
            _master_conn = sqlite3.connect(str(DB_PATH))
            for _p in range(1, 13):
                build_pillar_db(_p, _master_conn, verbose=True)
            _master_conn.close()
            show_stats()
        except Exception as e:
            print(f"WARNING: Pillar DB build failed: {e}")


if __name__ == "__main__":
    main()
