#!/usr/bin/env python3
"""
LIGHTHOUSE MACRO - PILLAR SUB-DATABASE BUILDER
===============================================
Builds per-pillar SQLite databases derived from the master DB.

Each pillar DB is self-contained with:
  - observations: filtered time series data
  - series_meta: metadata for included series
  - pillar_indices: computed index values for this pillar
  - pillar_info: pillar metadata and build stats

Usage:
    python build_pillar_dbs.py              # Build all 12 pillar DBs
    python build_pillar_dbs.py --pillars 1 5 # Build specific pillars
    python build_pillar_dbs.py --stats       # Show stats for existing DBs
    python build_pillar_dbs.py --unmapped    # List series not in any pillar
"""

import sys
import os
import sqlite3
import argparse
from datetime import datetime
from pathlib import Path

# Add the package to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lighthouse.config import DB_PATH
from lighthouse.pillar_mapping import (
    PILLAR_DEFS, PILLAR_SERIES, MASTER_INDICES,
    get_pillar_indices, get_pillar_db_name,
    get_all_mapped_series, get_pillar_summary,
)

# Output directory
PILLAR_DB_DIR = DB_PATH.parent / "pillars"


def build_pillar_db(pillar_num: int, master_conn: sqlite3.Connection, verbose: bool = True):
    """Build a single pillar sub-database from the master DB."""
    defn = PILLAR_DEFS[pillar_num]
    series_list = PILLAR_SERIES[pillar_num]
    index_ids = get_pillar_indices(pillar_num)
    db_name = get_pillar_db_name(pillar_num)
    db_path = PILLAR_DB_DIR / db_name

    if verbose:
        print(f"\n  Building Pillar {pillar_num:2d}: {defn['name']} ({len(series_list)} series mapped)")

    # Delete old DB (full rebuild, no corruption risk)
    if db_path.exists():
        db_path.unlink()

    # Create fresh DB
    conn = sqlite3.connect(str(db_path))
    c = conn.cursor()

    # Create tables
    c.execute("""
        CREATE TABLE observations (
            series_id TEXT,
            date TEXT,
            value REAL,
            PRIMARY KEY (series_id, date)
        )
    """)

    c.execute("""
        CREATE TABLE series_meta (
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
        )
    """)

    c.execute("""
        CREATE TABLE pillar_indices (
            date TEXT NOT NULL,
            index_id TEXT NOT NULL,
            value REAL,
            status TEXT,
            PRIMARY KEY (date, index_id)
        )
    """)

    c.execute("""
        CREATE TABLE pillar_info (
            pillar_num INTEGER PRIMARY KEY,
            name TEXT,
            code TEXT,
            engine TEXT,
            indices TEXT,
            series_count INTEGER,
            obs_count INTEGER,
            built_at TEXT
        )
    """)

    # Copy observations for this pillar's series
    master_c = master_conn.cursor()

    # Build placeholders for IN clause
    placeholders = ",".join(["?"] * len(series_list))

    # Copy observations
    master_c.execute(f"""
        SELECT series_id, date, value
        FROM observations
        WHERE series_id IN ({placeholders})
    """, series_list)

    obs_rows = master_c.fetchall()
    if obs_rows:
        c.executemany("INSERT INTO observations VALUES (?, ?, ?)", obs_rows)

    obs_count = len(obs_rows)

    # Copy series_meta
    master_c.execute(f"""
        SELECT series_id, title, source, category, frequency, units,
               last_updated, last_fetched, data_quality, last_value_date, obs_count
        FROM series_meta
        WHERE series_id IN ({placeholders})
    """, series_list)

    meta_rows = master_c.fetchall()
    if meta_rows:
        c.executemany("INSERT INTO series_meta VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", meta_rows)

    series_found = len(meta_rows)
    series_missing = len(series_list) - series_found

    # Copy pillar indices
    idx_placeholders = ",".join(["?"] * len(index_ids))
    master_c.execute(f"""
        SELECT date, index_id, value, status
        FROM lighthouse_indices
        WHERE index_id IN ({idx_placeholders})
    """, index_ids)

    idx_rows = master_c.fetchall()
    if idx_rows:
        c.executemany("INSERT INTO pillar_indices VALUES (?, ?, ?, ?)", idx_rows)

    # Create indexes
    c.execute("CREATE INDEX idx_obs_series ON observations(series_id)")
    c.execute("CREATE INDEX idx_obs_date ON observations(date)")
    c.execute("CREATE INDEX idx_indices_date ON pillar_indices(date)")
    c.execute("CREATE INDEX idx_indices_id ON pillar_indices(index_id)")

    # Write pillar info
    c.execute("""
        INSERT INTO pillar_info VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        pillar_num,
        defn["name"],
        defn["code"],
        defn["engine"],
        ",".join(defn["indices"]),
        series_found,
        obs_count,
        datetime.now().isoformat(),
    ))

    conn.commit()
    conn.close()

    if verbose:
        size_mb = db_path.stat().st_size / (1024 * 1024)
        print(f"           {series_found} series found, {obs_count:,} obs, "
              f"{len(idx_rows):,} index rows, {size_mb:.1f} MB")
        if series_missing > 0:
            # Find which series are missing
            found_ids = {row[0] for row in meta_rows}
            missing_ids = set(series_list) - found_ids
            print(f"           {series_missing} series not in master DB: "
                  f"{sorted(list(missing_ids))[:10]}{'...' if series_missing > 10 else ''}")


def show_stats():
    """Show stats for all existing pillar databases."""
    print("\n" + "=" * 70)
    print("PILLAR DATABASE STATS")
    print("=" * 70)

    if not PILLAR_DB_DIR.exists():
        print("  No pillar DB directory found.")
        return

    total_size = 0
    for pillar_num in range(1, 13):
        db_name = get_pillar_db_name(pillar_num)
        db_path = PILLAR_DB_DIR / db_name

        if not db_path.exists():
            print(f"  Pillar {pillar_num:2d}: {PILLAR_DEFS[pillar_num]['name']:12s} - NOT BUILT")
            continue

        conn = sqlite3.connect(str(db_path))
        c = conn.cursor()

        c.execute("SELECT COUNT(*) FROM observations")
        obs_count = c.fetchone()[0]

        c.execute("SELECT COUNT(*) FROM series_meta")
        series_count = c.fetchone()[0]

        c.execute("SELECT COUNT(DISTINCT index_id) FROM pillar_indices")
        idx_count = c.fetchone()[0]

        c.execute("SELECT built_at FROM pillar_info LIMIT 1")
        row = c.fetchone()
        built_at = row[0] if row else "unknown"

        conn.close()

        size_mb = db_path.stat().st_size / (1024 * 1024)
        total_size += size_mb
        print(f"  Pillar {pillar_num:2d}: {PILLAR_DEFS[pillar_num]['name']:12s} | "
              f"{series_count:4d} series | {obs_count:>8,} obs | "
              f"{idx_count:2d} indices | {size_mb:5.1f} MB | built {built_at[:19]}")

    print(f"\n  Total size: {total_size:.1f} MB")


def show_unmapped():
    """List series in master DB not assigned to any pillar."""
    print("\n" + "=" * 70)
    print("UNMAPPED SERIES")
    print("=" * 70)

    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    c.execute("SELECT series_id FROM series_meta ORDER BY series_id")
    all_db_series = {row[0] for row in c.fetchall()}
    conn.close()

    mapped = get_all_mapped_series()
    unmapped = sorted(all_db_series - mapped)

    # Categorize unmapped
    categories = {}
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    for sid in unmapped:
        c.execute("SELECT source, category FROM series_meta WHERE series_id = ?", (sid,))
        row = c.fetchone()
        if row:
            key = f"{row[0]}|{row[1]}"
            categories.setdefault(key, []).append(sid)
    conn.close()

    print(f"\n  Total in master DB: {len(all_db_series)}")
    print(f"  Mapped to pillars:  {len(mapped)}")
    print(f"  Unmapped:           {len(unmapped)}")

    print(f"\n  By source|category:")
    for key in sorted(categories.keys()):
        series = categories[key]
        print(f"\n  [{key}] ({len(series)} series)")
        for sid in series[:5]:
            print(f"    {sid}")
        if len(series) > 5:
            print(f"    ... and {len(series) - 5} more")


def main():
    parser = argparse.ArgumentParser(description="Build Lighthouse Macro Pillar Sub-Databases")
    parser.add_argument("--pillars", nargs="+", type=int,
                       help="Build specific pillars (e.g., --pillars 1 5)")
    parser.add_argument("--stats", action="store_true",
                       help="Show stats for existing pillar DBs")
    parser.add_argument("--unmapped", action="store_true",
                       help="List series not assigned to any pillar")
    args = parser.parse_args()

    if args.stats:
        show_stats()
        return

    if args.unmapped:
        show_unmapped()
        return

    # Determine which pillars to build
    if args.pillars:
        pillars_to_build = args.pillars
        for p in pillars_to_build:
            if p < 1 or p > 12:
                print(f"ERROR: Invalid pillar number {p}. Must be 1-12.")
                sys.exit(1)
    else:
        pillars_to_build = list(range(1, 13))

    # Ensure output directory exists
    PILLAR_DB_DIR.mkdir(parents=True, exist_ok=True)

    # Open master DB
    if not DB_PATH.exists():
        print(f"ERROR: Master database not found at {DB_PATH}")
        sys.exit(1)

    print("=" * 70)
    print("BUILDING PILLAR SUB-DATABASES")
    print("=" * 70)
    print(f"  Master DB: {DB_PATH}")
    print(f"  Output:    {PILLAR_DB_DIR}")
    print(f"  Pillars:   {pillars_to_build}")

    master_conn = sqlite3.connect(str(DB_PATH))

    start = datetime.now()
    for pillar_num in pillars_to_build:
        build_pillar_db(pillar_num, master_conn)

    master_conn.close()
    elapsed = (datetime.now() - start).total_seconds()

    print(f"\n  Done. Built {len(pillars_to_build)} pillar DBs in {elapsed:.1f}s")

    # Show summary
    show_stats()


if __name__ == "__main__":
    main()
