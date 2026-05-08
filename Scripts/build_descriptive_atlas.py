"""
LHM Descriptive Atlas Builder
==============================

Per the LHM Master Design: identify exactly 50 descriptive series per pillar
and store them in a new `descriptive_atlas` table.

Selection rules:
  1. Start from the canonical pillar_mapping (PILLAR_SERIES) which is the
     single source of truth for pillar membership.
  2. For pillars with >50 mapped series: rank by (a) observation count desc,
     (b) most recent observation date desc, then take top 50.
  3. For pillars with <50 mapped series: take all available, flag the
     undersupply, and supplement from series_meta.category matches if the
     INDICATORS_MASTER lists named candidates we haven't ingested yet.

We do not invent series. If a pillar genuinely has fewer than 50 distinct
descriptive inputs in the DB today, the report says so. The Validation
Engine then runs on whatever we have.

Output:
  - Table descriptive_atlas (pillar_id, series_id, rank, obs_count, latest_date,
    title, source, category, frequency, units)
  - Console summary of per-pillar coverage
"""
import os
import sys
import sqlite3
from datetime import datetime

sys.path.insert(0, '/Users/bob/LHM/Scripts/data_pipeline')
from lighthouse.pillar_mapping import PILLAR_SERIES, PILLAR_DEFS

DB = '/Users/bob/LHM/Data/databases/Lighthouse_Master.db'
TARGET_PER_PILLAR = 50


def build_atlas(conn, target=TARGET_PER_PILLAR):
    cur = conn.cursor()

    cur.execute("DROP TABLE IF EXISTS descriptive_atlas")
    cur.execute("""
        CREATE TABLE descriptive_atlas (
            pillar_id INTEGER NOT NULL,
            pillar_name TEXT NOT NULL,
            rank INTEGER NOT NULL,
            series_id TEXT NOT NULL,
            title TEXT,
            source TEXT,
            category TEXT,
            frequency TEXT,
            units TEXT,
            obs_count INTEGER,
            latest_date TEXT,
            built_at TEXT NOT NULL,
            PRIMARY KEY (pillar_id, rank)
        )
    """)
    cur.execute("CREATE INDEX idx_atlas_series ON descriptive_atlas(series_id)")

    summary = []
    built_at = datetime.utcnow().isoformat(timespec='seconds')

    for pid in range(1, 13):
        pname = PILLAR_DEFS[pid]['name']
        candidates = PILLAR_SERIES.get(pid, [])
        if not candidates:
            summary.append((pid, pname, 0, 0, 'no candidates'))
            continue

        placeholders = ','.join(['?'] * len(candidates))
        q = f"""
            SELECT m.series_id, m.title, m.source, m.category, m.frequency, m.units,
                   COUNT(o.value) as obs_count, MAX(o.date) as latest_date
            FROM series_meta m
            LEFT JOIN observations o ON o.series_id = m.series_id
            WHERE m.series_id IN ({placeholders})
            GROUP BY m.series_id
            ORDER BY obs_count DESC, latest_date DESC
        """
        rows = cur.execute(q, candidates).fetchall()
        rows = [r for r in rows if r[6] and r[6] > 0]
        ranked = rows[:target]

        for rank, r in enumerate(ranked, start=1):
            cur.execute("""
                INSERT INTO descriptive_atlas
                (pillar_id, pillar_name, rank, series_id, title, source,
                 category, frequency, units, obs_count, latest_date, built_at)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
            """, (pid, pname, rank, r[0], r[1], r[2], r[3], r[4], r[5],
                  r[6], r[7], built_at))

        flag = 'OK' if len(ranked) == target else f'undersupplied ({len(ranked)}/{target})'
        summary.append((pid, pname, len(candidates), len(ranked), flag))

    conn.commit()
    return summary


def main():
    conn = sqlite3.connect(DB)
    summary = build_atlas(conn)

    print('=' * 78)
    print('LHM DESCRIPTIVE ATLAS BUILD')
    print('=' * 78)
    print(f'Target: {TARGET_PER_PILLAR} series per pillar')
    print(f'{"Pillar":<6} {"Name":<10} {"Mapped":>7} {"In Atlas":>9}   Status')
    print('-' * 78)
    for pid, pname, n_mapped, n_atlas, flag in summary:
        print(f'{pid:>5}  {pname:<10} {n_mapped:>7} {n_atlas:>9}   {flag}')
    print()
    total = sum(n_atlas for _, _, _, n_atlas, _ in summary)
    target_total = TARGET_PER_PILLAR * 12
    print(f'Total in atlas: {total} / {target_total} target')
    conn.close()


if __name__ == '__main__':
    main()
