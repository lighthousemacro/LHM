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

import json
import sqlite3
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

DB_PATH = Path("/Users/bob/LHM/Data/databases/Lighthouse_Master.db")
BACKEND_DIR = Path(__file__).resolve().parent
WIDGETS_PATH = BACKEND_DIR / "widgets.json"
APPS_PATH = BACKEND_DIR / "apps.json"

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


@app.get("/widgets.json")
def widgets_manifest() -> dict[str, Any]:
    """Widget manifest consumed by OpenBB Workspace."""
    if not WIDGETS_PATH.exists():
        raise HTTPException(status_code=500, detail=f"widgets.json missing at {WIDGETS_PATH}")
    return json.loads(WIDGETS_PATH.read_text())


@app.get("/apps.json")
def apps_manifest() -> dict[str, Any]:
    """Apps (dashboard layout) manifest consumed by OpenBB Workspace."""
    if not APPS_PATH.exists():
        raise HTTPException(status_code=500, detail=f"apps.json missing at {APPS_PATH}")
    return json.loads(APPS_PATH.read_text())


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


# ---------------------------------------------------------------------------
# Synthesis layer: pillar map, transmission chains, divergence, heatmap
# ---------------------------------------------------------------------------

PILLAR_MAP: dict[str, dict[str, str]] = {
    "Labor":      {"composite": "LFI",     "engine": "Macro Dynamics"},
    "Prices":     {"composite": "PCI",     "engine": "Macro Dynamics"},
    "Growth":     {"composite": "GCI",     "engine": "Macro Dynamics"},
    "Housing":    {"composite": "HCI",     "engine": "Macro Dynamics"},
    "Consumer":   {"composite": "CCI",     "engine": "Macro Dynamics"},
    "Business":   {"composite": "BCI",     "engine": "Macro Dynamics"},
    "Trade":      {"composite": "TCI",     "engine": "Macro Dynamics"},
    "Government": {"composite": "GCI_Gov", "engine": "Monetary Mechanics"},
    "Financial":  {"composite": "FCI",     "engine": "Monetary Mechanics"},
    "Plumbing":   {"composite": "LCI",     "engine": "Monetary Mechanics"},
    "Structure":  {"composite": "MSI",     "engine": "Market Structure"},
    "Sentiment":  {"composite": "SPI",     "engine": "Market Structure"},
}

CHAINS: dict[str, dict[str, Any]] = {
    "plumbing_credit_labor": {
        "label": "Plumbing → Credit → Labor",
        "description": "Reserves and funding stress feed credit conditions, which lead labor fragility.",
        "links": [
            {"step": 1, "node": "LCI", "role": "Plumbing"},
            {"step": 2, "node": "FCI", "role": "Financial"},
            {"step": 3, "node": "CLG", "role": "Credit-Labor Gap"},
            {"step": 4, "node": "LFI", "role": "Labor Fragility"},
        ],
    },
    "rates_housing_consumer": {
        "label": "Rates → Housing → Consumer",
        "description": "Long rates set mortgage cost, housing transmits to consumer.",
        "links": [
            {"step": 1, "node": "DGS10",        "role": "10Y Treasury",    "kind": "series"},
            {"step": 2, "node": "MORTGAGE30US", "role": "30Y Mortgage",    "kind": "series"},
            {"step": 3, "node": "HCI",          "role": "Housing"},
            {"step": 4, "node": "CCI",          "role": "Consumer"},
        ],
    },
    "sentiment_structure_risk": {
        "label": "Sentiment → Structure → Risk",
        "description": "Positioning extremes diverge from breadth, then resolve into MRI.",
        "links": [
            {"step": 1, "node": "SPI", "role": "Sentiment"},
            {"step": 2, "node": "MSI", "role": "Structure"},
            {"step": 3, "node": "SSD", "role": "Sent-Struct Divergence"},
            {"step": 4, "node": "MRI", "role": "Macro Risk"},
        ],
    },
}


def _zscore(rows: list[sqlite3.Row]) -> tuple[float | None, float | None, float | None]:
    """Return (latest_value, latest_z, lookback_n) from a list of (date, value) rows."""
    vals = [r["value"] for r in rows if r["value"] is not None]
    if len(vals) < 30:
        return (vals[-1] if vals else None, None, len(vals))
    latest = vals[-1]
    mean = sum(vals) / len(vals)
    var = sum((v - mean) ** 2 for v in vals) / len(vals)
    sd = var ** 0.5
    z = (latest - mean) / sd if sd > 0 else None
    return latest, z, len(vals)


def _series_history(c: sqlite3.Connection, node: str, kind: str = "composite") -> list[sqlite3.Row]:
    if kind == "series":
        sql = "SELECT date, value FROM observations WHERE series_id = ? ORDER BY date ASC"
    else:
        sql = "SELECT date, value FROM lighthouse_indices WHERE index_id = ? ORDER BY date ASC"
    return c.execute(sql, (node,)).fetchall()


@app.get("/pillar_heatmap")
def pillar_heatmap() -> list[dict[str, Any]]:
    """Current z-score for all 12 pillar composites. Heatmap-friendly shape."""
    out: list[dict[str, Any]] = []
    with _conn() as c:
        for pillar, meta in PILLAR_MAP.items():
            comp = meta["composite"]
            rows = _series_history(c, comp, kind="composite")
            if not rows:
                continue
            latest, z, n = _zscore(rows)
            as_of = rows[-1]["date"] if rows else None
            out.append({
                "pillar": pillar,
                "engine": meta["engine"],
                "composite": comp,
                "as_of": as_of,
                "value": latest,
                "z_score": round(z, 3) if z is not None else None,
                "lookback_n": n,
            })
    return out


@app.get("/transmission_chain")
def transmission_chain(
    chain_id: str = Query(
        "plumbing_credit_labor",
        description="plumbing_credit_labor / rates_housing_consumer / sentiment_structure_risk",
    ),
) -> dict[str, Any]:
    """Lead/lag normalized z-scores along a predefined transmission chain."""
    chain = CHAINS.get(chain_id)
    if chain is None:
        raise HTTPException(status_code=404, detail=f"Unknown chain_id: {chain_id}")
    nodes: list[dict[str, Any]] = []
    with _conn() as c:
        for link in chain["links"]:
            kind = link.get("kind", "composite")
            rows = _series_history(c, link["node"], kind=kind)
            latest, z, n = _zscore(rows)
            as_of = rows[-1]["date"] if rows else None
            nodes.append({
                "step": link["step"],
                "node": link["node"],
                "role": link["role"],
                "kind": kind,
                "as_of": as_of,
                "value": latest,
                "z_score": round(z, 3) if z is not None else None,
                "lookback_n": n,
            })
    return {
        "chain_id": chain_id,
        "label": chain["label"],
        "description": chain["description"],
        "nodes": nodes,
    }


@app.get("/transmission_chain_table")
def transmission_chain_table(
    chain_id: str = Query("plumbing_credit_labor"),
) -> list[dict[str, Any]]:
    """Same as /transmission_chain but flat shape for OpenBB table widget."""
    payload = transmission_chain(chain_id=chain_id)
    return payload["nodes"]


@app.get("/divergence")
def divergence(
    market_node: str = Query("MSI", description="Market-side composite (MSI, SPI, FCI)"),
    real_node: str = Query("LFI", description="Real-economy composite (LFI, GCI, CCI, HCI, BCI)"),
    threshold: float = Query(1.0, ge=0.0, description="|Δz| above this is flagged"),
) -> dict[str, Any]:
    """Z-score gap between a market-side and real-economy composite. Flags decoupling."""
    with _conn() as c:
        m_rows = _series_history(c, market_node, kind="composite")
        r_rows = _series_history(c, real_node, kind="composite")
    if not m_rows or not r_rows:
        raise HTTPException(
            status_code=404,
            detail=f"Missing history for {market_node} or {real_node}",
        )
    m_val, m_z, _ = _zscore(m_rows)
    r_val, r_z, _ = _zscore(r_rows)
    if m_z is None or r_z is None:
        raise HTTPException(status_code=400, detail="Insufficient history for z-score")
    delta = m_z - r_z
    flag = "DIVERGENT" if abs(delta) >= threshold else "ALIGNED"
    direction = "Market hot vs real soft" if delta > 0 else "Real hot vs market soft"
    return {
        "market_node": market_node,
        "real_node": real_node,
        "as_of_market": m_rows[-1]["date"],
        "as_of_real": r_rows[-1]["date"],
        "market_z": round(m_z, 3),
        "real_z": round(r_z, 3),
        "delta_z": round(delta, 3),
        "threshold": threshold,
        "flag": flag,
        "direction": direction if flag == "DIVERGENT" else "—",
    }


@app.get("/divergence_grid")
def divergence_grid(
    threshold: float = Query(1.0, ge=0.0),
) -> list[dict[str, Any]]:
    """Pairwise divergence across the canonical market vs real-economy pairs."""
    pairs = [
        ("MSI", "LFI"),
        ("MSI", "GCI"),
        ("MSI", "CCI"),
        ("SPI", "LFI"),
        ("SPI", "BCI"),
        ("FCI", "CLG"),
        ("FCI", "LCI"),
    ]
    out: list[dict[str, Any]] = []
    for m, r in pairs:
        try:
            out.append(divergence(market_node=m, real_node=r, threshold=threshold))
        except HTTPException:
            continue
    return out


# ---------------------------------------------------------------------------
# Panel endpoints — multi-series payloads for OpenBB chart widgets
# ---------------------------------------------------------------------------

def _multi_series(
    c: sqlite3.Connection,
    series_ids: list[str],
    start_date: str | None,
    end_date: str | None,
) -> list[dict[str, Any]]:
    """Long-format rows ({date, series_id, value}) for one or more series."""
    if not series_ids:
        return []
    placeholders = ",".join("?" * len(series_ids))
    sql = (
        f"SELECT date, series_id, value FROM observations "
        f"WHERE series_id IN ({placeholders})"
    )
    params: list[Any] = list(series_ids)
    if start_date:
        sql += " AND date >= ?"
        params.append(start_date)
    if end_date:
        sql += " AND date <= ?"
        params.append(end_date)
    sql += " ORDER BY date ASC"
    return [dict(r) for r in c.execute(sql, params).fetchall()]


@app.get("/breadth_panel")
def breadth_panel(
    start_date: str | None = Query(None),
    end_date: str | None = Query(None),
) -> list[dict[str, Any]]:
    """% of S&P 500 above its 20d / 50d / 200d MA. Pillar 11 — Structure."""
    ids = ["SPX_PCT_ABOVE_20D", "SPX_PCT_ABOVE_50D", "SPX_PCT_ABOVE_200D"]
    with _conn() as c:
        rows = _multi_series(c, ids, start_date, end_date)
    if not rows:
        raise HTTPException(status_code=404, detail="No breadth observations found")
    return rows


@app.get("/sentiment_panel")
def sentiment_panel(
    start_date: str | None = Query(None),
    end_date: str | None = Query(None),
) -> list[dict[str, Any]]:
    """AAII bull / bear / spread. Pillar 12 — Sentiment."""
    ids = ["AAII_Bullish", "AAII_Bearish", "AAII_Bull_Bear_Spread"]
    with _conn() as c:
        rows = _multi_series(c, ids, start_date, end_date)
    if not rows:
        raise HTTPException(status_code=404, detail="No sentiment observations found")
    return rows


@app.get("/rates_panel")
def rates_panel(
    start_date: str | None = Query(None),
    end_date: str | None = Query(None),
) -> list[dict[str, Any]]:
    """Treasury curve anchors: 2Y, 5Y, 10Y, 30Y. Plus 30Y mortgage."""
    ids = ["DGS2", "DGS5", "DGS10", "DGS30", "MORTGAGE30US"]
    with _conn() as c:
        rows = _multi_series(c, ids, start_date, end_date)
    if not rows:
        raise HTTPException(status_code=404, detail="No rates observations found")
    return rows


@app.get("/credit_panel")
def credit_panel(
    start_date: str | None = Query(None),
    end_date: str | None = Query(None),
) -> list[dict[str, Any]]:
    """Credit spread anchors: HY OAS, IG OAS, EMD OAS."""
    ids = ["BAMLH0A0HYM2", "BAMLC0A0CM"]
    with _conn() as c:
        rows = _multi_series(c, ids, start_date, end_date)
    if not rows:
        raise HTTPException(status_code=404, detail="No credit observations found")
    return rows


@app.get("/plumbing_panel")
def plumbing_panel(
    start_date: str | None = Query(None),
    end_date: str | None = Query(None),
) -> list[dict[str, Any]]:
    """Plumbing anchors: RRP, WALCL, TGA, IORB."""
    ids = ["RRPONTSYD", "WALCL", "WTREGEN", "IORB"]
    with _conn() as c:
        rows = _multi_series(c, ids, start_date, end_date)
    if not rows:
        raise HTTPException(status_code=404, detail="No plumbing observations found")
    return rows


@app.get("/engine_summary")
def engine_summary() -> list[dict[str, Any]]:
    """One row per engine with mean |z| of its pillar composites. Use as a regime tile."""
    grouped: dict[str, list[float]] = {}
    with _conn() as c:
        for pillar, meta in PILLAR_MAP.items():
            rows = _series_history(c, meta["composite"], kind="composite")
            _, z, _ = _zscore(rows)
            if z is None:
                continue
            grouped.setdefault(meta["engine"], []).append(z)
    out: list[dict[str, Any]] = []
    for engine, zs in grouped.items():
        if not zs:
            continue
        mean_abs = sum(abs(z) for z in zs) / len(zs)
        mean = sum(zs) / len(zs)
        out.append({
            "engine": engine,
            "pillars_n": len(zs),
            "mean_z": round(mean, 3),
            "mean_abs_z": round(mean_abs, 3),
            "max_abs_z": round(max(abs(z) for z in zs), 3),
        })
    return out
