"""
Lighthouse Macro custom backend for OpenBB Workspace.

Exposes Lighthouse_Master.db as the source of truth via FastAPI endpoints
that OpenBB Workspace can render as widgets.

Run:
    /Users/bob/LHM/OpenBB/conda/envs/lhm-obb/bin/openbb-api \
        --app /Users/bob/LHM/Scripts/openbb_backend/lhm_backend.py \
        --name app

Then in OpenBB Workspace: Settings → Backend → add http://127.0.0.1:6900
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

DB_PATH = Path("/Users/bob/LHM/Data/databases/Lighthouse_Master.db")

app = FastAPI(
    title="Lighthouse Macro Data Backend",
    description="Query interface to Lighthouse_Master.db (2,498 macro/market/crypto series).",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _conn() -> sqlite3.Connection:
    if not DB_PATH.exists():
        raise HTTPException(status_code=500, detail=f"DB not found at {DB_PATH}")
    c = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    c.row_factory = sqlite3.Row
    return c


@app.get("/health")
def health() -> dict[str, Any]:
    """Health check + DB stats."""
    with _conn() as c:
        meta = c.execute("SELECT COUNT(*) FROM series_meta").fetchone()[0]
        obs = c.execute("SELECT COUNT(*) FROM observations").fetchone()[0]
        latest = c.execute(
            "SELECT MAX(date) FROM observations"
        ).fetchone()[0]
    return {
        "status": "ok",
        "db_path": str(DB_PATH),
        "series_count": meta,
        "observation_count": obs,
        "latest_observation_date": latest,
    }


@app.get("/categories")
def categories() -> list[dict[str, Any]]:
    """List all data categories with series counts. Use as a directory for browsing the DB."""
    with _conn() as c:
        rows = c.execute(
            "SELECT category, COUNT(*) AS series_count "
            "FROM series_meta WHERE category IS NOT NULL "
            "GROUP BY category ORDER BY series_count DESC"
        ).fetchall()
    return [dict(r) for r in rows]


@app.get("/sources")
def sources() -> list[dict[str, Any]]:
    """List all data sources with series counts."""
    with _conn() as c:
        rows = c.execute(
            "SELECT source, COUNT(*) AS series_count "
            "FROM series_meta WHERE source IS NOT NULL "
            "GROUP BY source ORDER BY series_count DESC"
        ).fetchall()
    return [dict(r) for r in rows]


@app.get("/series")
def list_series(
    category: str | None = Query(None, description="Filter by category"),
    source: str | None = Query(None, description="Filter by source"),
    search: str | None = Query(None, description="Search in series_id or title"),
    limit: int = Query(200, ge=1, le=2500),
) -> list[dict[str, Any]]:
    """List series in the DB. Filter by category, source, or text search."""
    where = []
    params: list[Any] = []
    if category:
        where.append("category = ?")
        params.append(category)
    if source:
        where.append("source = ?")
        params.append(source)
    if search:
        where.append("(series_id LIKE ? OR title LIKE ?)")
        params.extend([f"%{search}%", f"%{search}%"])
    sql = (
        "SELECT series_id, title, source, category, frequency, units, "
        "last_value_date, obs_count "
        "FROM series_meta"
    )
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY series_id LIMIT ?"
    params.append(limit)
    with _conn() as c:
        rows = c.execute(sql, params).fetchall()
    return [dict(r) for r in rows]


@app.get("/observations")
def observations(
    series_id: str = Query(..., description="Series ID (e.g. UNRATE, DGS10)"),
    start_date: str | None = Query(None, description="ISO date YYYY-MM-DD"),
    end_date: str | None = Query(None, description="ISO date YYYY-MM-DD"),
) -> list[dict[str, Any]]:
    """Time series observations for a single series. Returns [{date, value}] sorted ascending."""
    sql = "SELECT date, value FROM observations WHERE series_id = ?"
    params: list[Any] = [series_id]
    if start_date:
        sql += " AND date >= ?"
        params.append(start_date)
    if end_date:
        sql += " AND date <= ?"
        params.append(end_date)
    sql += " ORDER BY date ASC"
    with _conn() as c:
        rows = c.execute(sql, params).fetchall()
    if not rows:
        raise HTTPException(status_code=404, detail=f"No observations for {series_id}")
    return [dict(r) for r in rows]


@app.get("/latest")
def latest(
    series_ids: str = Query(..., description="Comma-separated series IDs"),
) -> list[dict[str, Any]]:
    """Latest observation for one or more series. Useful for dashboard tiles."""
    ids = [s.strip() for s in series_ids.split(",") if s.strip()]
    if not ids:
        raise HTTPException(status_code=400, detail="No series_ids provided")
    placeholders = ",".join("?" * len(ids))
    sql = f"""
        SELECT o.series_id, o.date, o.value, m.title, m.units, m.frequency
        FROM observations o
        JOIN series_meta m ON m.series_id = o.series_id
        WHERE o.series_id IN ({placeholders})
        AND o.date = (
            SELECT MAX(date) FROM observations WHERE series_id = o.series_id
        )
    """
    with _conn() as c:
        rows = c.execute(sql, ids).fetchall()
    return [dict(r) for r in rows]


@app.get("/composites")
def composites() -> list[dict[str, Any]]:
    """Latest reading for every LHM composite index. One row per index_id."""
    sql = """
        SELECT i.index_id, i.date AS as_of, i.value, i.status
        FROM lighthouse_indices i
        JOIN (
            SELECT index_id, MAX(date) AS max_date
            FROM lighthouse_indices
            GROUP BY index_id
        ) m ON m.index_id = i.index_id AND m.max_date = i.date
        ORDER BY i.index_id
    """
    with _conn() as c:
        rows = c.execute(sql).fetchall()
    return [dict(r) for r in rows]


@app.get("/composite_history")
def composite_history(
    index_id: str = Query(..., description="Composite ID (e.g. MRI, LFI, LCI, FCI)"),
    start_date: str | None = None,
    end_date: str | None = None,
) -> list[dict[str, Any]]:
    """Historical time series for a single LHM composite."""
    sql = "SELECT date, value, status FROM lighthouse_indices WHERE index_id = ?"
    params: list[Any] = [index_id]
    if start_date:
        sql += " AND date >= ?"
        params.append(start_date)
    if end_date:
        sql += " AND date <= ?"
        params.append(end_date)
    sql += " ORDER BY date ASC"
    with _conn() as c:
        rows = c.execute(sql, params).fetchall()
    if not rows:
        raise HTTPException(
            status_code=404,
            detail=f"Composite '{index_id}' not found or no data in range",
        )
    return [dict(r) for r in rows]
