"""
Schema discovery for Lighthouse_Master.db.

Interrogates every table, prints columns + dtypes + row counts + date ranges,
and writes a Markdown manifest to scripts/schema_manifest.md so widget
authoring can map endpoints to real columns instead of guessing.

Run:
    /Users/bob/LHM/OpenBB/conda/envs/lhm-obb/bin/python \
        /Users/bob/LHM/Scripts/openbb_backend/scripts/discover_schema.py
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = Path("/Users/bob/LHM/Data/databases/Lighthouse_Master.db")
OUT_PATH = Path(__file__).resolve().parent / "schema_manifest.md"

DATE_COL_HINTS = ("date", "as_of", "timestamp", "ts")


def list_tables(c: sqlite3.Connection) -> list[str]:
    rows = c.execute(
        "SELECT name FROM sqlite_master "
        "WHERE type='table' AND name NOT LIKE 'sqlite_%' "
        "ORDER BY name"
    ).fetchall()
    return [r[0] for r in rows]


def table_columns(c: sqlite3.Connection, table: str) -> list[tuple[str, str]]:
    rows = c.execute(f"PRAGMA table_info({table})").fetchall()
    return [(r[1], r[2]) for r in rows]


def first_rows(c: sqlite3.Connection, table: str, n: int = 5) -> list[tuple]:
    try:
        return c.execute(f"SELECT * FROM {table} LIMIT {n}").fetchall()
    except sqlite3.Error:
        return []


def row_count(c: sqlite3.Connection, table: str) -> int:
    try:
        return c.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    except sqlite3.Error:
        return -1


def date_range(c: sqlite3.Connection, table: str, cols: list[str]) -> tuple[str, str | None, str | None]:
    for col in cols:
        if col.lower() in DATE_COL_HINTS or col.lower().endswith("_date"):
            try:
                lo, hi = c.execute(
                    f"SELECT MIN({col}), MAX({col}) FROM {table}"
                ).fetchone()
                return col, lo, hi
            except sqlite3.Error:
                continue
    return "", None, None


def main() -> None:
    if not DB_PATH.exists():
        raise SystemExit(f"DB not found: {DB_PATH}")

    con = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    tables = list_tables(con)

    lines: list[str] = []
    lines.append("# Lighthouse_Master.db — schema manifest")
    lines.append("")
    lines.append(f"- Path: `{DB_PATH}`")
    lines.append(f"- Tables: {len(tables)}")
    lines.append("")

    # Top-level summary
    lines.append("## Summary")
    lines.append("")
    lines.append("| Table | Rows | Date column | Earliest | Latest |")
    lines.append("|---|---:|---|---|---|")
    summary: list[dict] = []
    for t in tables:
        cols = [c for c, _ in table_columns(con, t)]
        n = row_count(con, t)
        date_col, lo, hi = date_range(con, t, cols)
        summary.append({"table": t, "rows": n, "date_col": date_col, "lo": lo, "hi": hi})
        lines.append(
            f"| `{t}` | {n:,} | {date_col or '—'} | {lo or '—'} | {hi or '—'} |"
        )
    lines.append("")

    # Detail per table
    for t in tables:
        cols = table_columns(con, t)
        n = row_count(con, t)
        sample = first_rows(con, t, 5)
        lines.append(f"## `{t}`")
        lines.append("")
        lines.append(f"- Rows: {n:,}")
        lines.append("")
        lines.append("### Columns")
        lines.append("")
        lines.append("| Column | Type |")
        lines.append("|---|---|")
        for cn, ct in cols:
            lines.append(f"| `{cn}` | `{ct or 'TEXT'}` |")
        lines.append("")

        if sample:
            lines.append("### First 5 rows")
            lines.append("")
            lines.append("```")
            header = " | ".join(c for c, _ in cols)
            lines.append(header)
            lines.append("-" * min(len(header), 120))
            for row in sample:
                lines.append(" | ".join("" if v is None else str(v) for v in row))
            lines.append("```")
            lines.append("")

    # series_meta drilldown if present
    if "series_meta" in tables:
        lines.append("## `series_meta` — categories and sources")
        lines.append("")
        try:
            cats = con.execute(
                "SELECT category, COUNT(*) FROM series_meta "
                "WHERE category IS NOT NULL GROUP BY category ORDER BY 2 DESC"
            ).fetchall()
            lines.append("### Categories")
            lines.append("")
            lines.append("| Category | Series |")
            lines.append("|---|---:|")
            for cat, cnt in cats:
                lines.append(f"| {cat} | {cnt} |")
            lines.append("")
        except sqlite3.Error:
            pass

        try:
            srcs = con.execute(
                "SELECT source, COUNT(*) FROM series_meta "
                "WHERE source IS NOT NULL GROUP BY source ORDER BY 2 DESC"
            ).fetchall()
            lines.append("### Sources")
            lines.append("")
            lines.append("| Source | Series |")
            lines.append("|---|---:|")
            for src, cnt in srcs:
                lines.append(f"| {src} | {cnt} |")
            lines.append("")
        except sqlite3.Error:
            pass

    # lighthouse_indices drilldown if present
    if "lighthouse_indices" in tables:
        lines.append("## `lighthouse_indices` — composites available")
        lines.append("")
        try:
            ids = con.execute(
                "SELECT index_id, COUNT(*) AS n, MIN(date) AS lo, MAX(date) AS hi "
                "FROM lighthouse_indices GROUP BY index_id ORDER BY index_id"
            ).fetchall()
            lines.append("| index_id | rows | earliest | latest |")
            lines.append("|---|---:|---|---|")
            for idx, n, lo, hi in ids:
                lines.append(f"| `{idx}` | {n:,} | {lo} | {hi} |")
            lines.append("")
        except sqlite3.Error:
            pass

    OUT_PATH.write_text("\n".join(lines))
    con.close()
    print(f"Wrote {OUT_PATH}")
    print(f"Tables: {len(tables)}")
    for s in summary:
        print(f"  {s['table']:30s} rows={s['rows']:>12,}  range={s['lo']}..{s['hi']}")


if __name__ == "__main__":
    main()
