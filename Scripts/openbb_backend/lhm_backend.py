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

import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lhm_brand import line_chart  # noqa: E402

DB_PATH = Path("/Users/bob/LHM/Data/databases/Lighthouse_Master.db")
BACKEND_DIR = Path(__file__).resolve().parent
WIDGETS_PATH = BACKEND_DIR / "widgets.json"
APPS_PATH = BACKEND_DIR / "apps.json"

app = FastAPI(
    title="Lighthouse Macro Data Backend",
    description="Query interface to Lighthouse_Master.db (2,530 macro/market/crypto series across 18 sources).",
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
def apps_manifest() -> list[dict[str, Any]]:
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
) -> dict[str, Any]:
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
    dates = [r["date"] for r in rows]
    values = [r["value"] for r in rows]
    return line_chart(
        dates=dates,
        series=[{"name": index_id, "values": values}],
        title=f"{index_id} — History",
        zscore=True,
    )


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
    "Government": {"composite": "FPI",     "engine": "Monetary Mechanics"},
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


@app.get("/series_panel")
def series_panel(
    series_ids: str = Query(..., description="Comma-separated series IDs to overlay"),
    start_date: str | None = Query(None),
    end_date: str | None = Query(None),
    rebase: str = Query("false", description="Rebase each series to 100 at window start ('true'/'false')"),
    transform: str = Query("none", description="'none' or 'yoy' (percent change over `periods` observations)"),
    periods: int = Query(12, ge=1, le=60, description="Lookback (observations) for the yoy transform. 12=monthly YoY, 4=quarterly YoY"),
) -> list[dict[str, Any]]:
    """Generic multi-series overlay. Long format [{date, series_id, value}].

    Set rebase=true to index every series to 100 at its first in-window point —
    use for cross-asset performance overlays (equity indices, sectors, FX, crypto)
    where absolute levels live on different scales. Leave false for like-scaled
    series (yields, spreads, vol) where levels carry the read.

    Set transform=yoy to return year-over-year percent change (percent change over
    `periods` observations: 12 for monthly series, 4 for quarterly). Use for the
    operator cost / hiring reads where the rate of change is the story.
    """
    ids = [s.strip() for s in series_ids.split(",") if s.strip()]
    if not ids:
        raise HTTPException(status_code=400, detail="No series_ids provided")
    with _conn() as c:
        rows = _multi_series(c, ids, start_date, end_date)
    if not rows:
        raise HTTPException(status_code=404, detail=f"No observations for {series_ids}")
    if transform.strip().lower() == "yoy":
        from collections import defaultdict
        seqs: dict[str, list[tuple[str, float]]] = defaultdict(list)
        for r in rows:  # rows are globally date-ascending, so each sub-sequence is too
            if r["value"] is not None:
                seqs[r["series_id"]].append((r["date"], r["value"]))
        out: list[dict[str, Any]] = []
        for sid, seq in seqs.items():
            for i in range(periods, len(seq)):
                d, v = seq[i]
                v0 = seq[i - periods][1]
                if v0 in (None, 0):
                    continue
                out.append({"date": d, "series_id": sid, "value": round((v / v0 - 1) * 100.0, 2)})
        out.sort(key=lambda x: x["date"])
        if not out:
            raise HTTPException(status_code=404, detail="Not enough history for YoY transform")
        return out
    if rebase.strip().lower() in ("1", "true", "yes", "on"):
        base: dict[str, float] = {}
        out: list[dict[str, Any]] = []
        for r in rows:  # already date-ascending
            sid, val = r["series_id"], r["value"]
            if val is None:
                continue
            if sid not in base:
                if val == 0:
                    continue
                base[sid] = val
            out.append({
                "date": r["date"],
                "series_id": sid,
                "value": round(val / base[sid] * 100.0, 2),
            })
        return out
    return rows


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


@app.get("/treasury_auctions")
def treasury_auctions(
    start_date: str | None = Query(None),
    end_date: str | None = Query(None),
) -> list[dict[str, Any]]:
    """Treasury auction quality + supply mix from fiscaldata.treasury.gov.

    10Y note: tail (bp), bid-to-cover, indirect bidder share.
    Aggregate: bills share of marketable debt, weighted-avg maturity.
    """
    ids = [
        "TD_AUCTION_TAIL_10Y",
        "TD_AUCTION_BTC_10Y",
        "TD_INDIRECT_SHARE_10Y",
        "TD_BILLS_SHARE",
        "TD_WAM_MARKETABLE",
    ]
    with _conn() as c:
        rows = _multi_series(c, ids, start_date, end_date)
    if not rows:
        raise HTTPException(status_code=404, detail="No Treasury auction observations found")
    return rows


@app.get("/risk_model")
def risk_model() -> list[dict[str, Any]]:
    """Latest output from the lighthouse_quant risk ensemble.

    Surfaces recession probability, ensemble risk score, warning level,
    allocation multiplier, and liquidity-stage / discontinuity-premium tags.
    All values pulled from lighthouse_indices.
    """
    ids = [
        "REC_PROB",
        "BASE_REC_PROB",
        "ENSEMBLE_RISK",
        "WARNING_LEVEL",
        "ALLOC_MULTIPLIER",
        "LIQ_STAGE",
        "DISCONTINUITY_PREMIUM",
    ]
    placeholders = ",".join("?" * len(ids))
    sql = f"""
        SELECT i.index_id, i.date AS as_of, i.value, i.status
        FROM lighthouse_indices i
        JOIN (
            SELECT index_id, MAX(date) AS max_date
            FROM lighthouse_indices
            WHERE index_id IN ({placeholders})
            GROUP BY index_id
        ) m ON m.index_id = i.index_id AND m.max_date = i.date
        ORDER BY i.index_id
    """
    with _conn() as c:
        rows = c.execute(sql, ids).fetchall()
    if not rows:
        raise HTTPException(status_code=404, detail="No risk-model outputs found in lighthouse_indices")
    return [dict(r) for r in rows]


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


# ---------------------------------------------------------------------------
# Main Street Monitor — the operator read (non-market participants)
#
# Two Economies frame: this side of the house serves business owners, operators
# and corporates whose decisions hinge on the macro environment without trading
# on it. Mirrors Scripts/build_main_street_monitor.py so the standalone HTML and
# the OpenBB terminal tell the same story off the same series.
# ---------------------------------------------------------------------------

def _ms_series(c: sqlite3.Connection, series_id: str) -> list[tuple[str, float]]:
    rows = c.execute(
        "SELECT date, value FROM observations WHERE series_id = ? AND value IS NOT NULL ORDER BY date ASC",
        (series_id,),
    ).fetchall()
    return [(r["date"], float(r["value"])) for r in rows]


def _ms_yoy(seq: list[tuple[str, float]], periods: int = 12) -> list[tuple[str, float]]:
    out: list[tuple[str, float]] = []
    for i in range(periods, len(seq)):
        v0 = seq[i - periods][1]
        if v0 == 0:
            continue
        out.append((seq[i][0], (seq[i][1] / v0 - 1.0) * 100.0))
    return out


def _ms_real_yoy(nom: list[tuple[str, float]], deflator: list[tuple[str, float]], periods: int = 12) -> list[tuple[str, float]]:
    """YoY of a nominal series deflated by a price index, aligned on date."""
    defl = {d: v for d, v in deflator}
    real = [(d, v / defl[d]) for d, v in nom if d in defl and defl[d]]
    return _ms_yoy(real, periods)


def _ms_long(
    named: dict[str, list[tuple[str, float]]],
    start_date: str | None = None,
    end_date: str | None = None,
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for label, seq in named.items():
        for d, v in seq:
            if start_date and d < start_date:
                continue
            if end_date and d > end_date:
                continue
            out.append({"date": d, "series_id": label, "value": round(v, 3)})
    out.sort(key=lambda x: x["date"])
    return out


def _ms_last(seq: list[tuple[str, float]]) -> float | None:
    return seq[-1][1] if seq else None


def _ms_trend(seq: list[tuple[str, float]], lookback: int = 3) -> str:
    if len(seq) < lookback + 1:
        return "stable"
    vals = [v for _, v in seq]
    recent = vals[-1] - vals[-1 - lookback]
    diffs = [vals[i] - vals[i - 1] for i in range(max(1, len(vals) - 24), len(vals))]
    if len(diffs) < 2:
        return "stable"
    mean = sum(diffs) / len(diffs)
    sd = (sum((x - mean) ** 2 for x in diffs) / len(diffs)) ** 0.5
    if abs(recent) < 0.3 * sd * lookback:
        return "stable"
    return "rising" if recent > 0 else "falling"


def _ms_metrics(c: sqlite3.Connection) -> dict[str, Any]:
    cpi = _ms_series(c, "CPIAUCSL")
    pce = _ms_yoy(_ms_series(c, "PCEC96"))
    rsx = _ms_real_yoy(_ms_series(c, "RSXFS"), cpi)
    wages = _ms_yoy(_ms_series(c, "CES0500000003"))
    cpi_yoy = _ms_yoy(cpi)
    core = _ms_yoy(_ms_series(c, "CPILFESL"))
    cc = _ms_series(c, "DRCCLACBS")
    save = _ms_series(c, "PSAVERT")
    retail_jobs = _ms_yoy(_ms_series(c, "USTRADE"))
    leisure_jobs = _ms_yoy(_ms_series(c, "USLAH"))
    retail_quits = _ms_series(c, "JTS4400QUR")
    leisure_quits = _ms_series(c, "JTS7000QUR")
    return {
        "pce": pce, "rsx": rsx, "wages": wages, "cpi_yoy": cpi_yoy, "core": core,
        "cc": cc, "save": save, "retail_jobs": retail_jobs, "leisure_jobs": leisure_jobs,
        "retail_quits": retail_quits, "leisure_quits": leisure_quits,
    }


def _ms_verdict(m: dict[str, Any]) -> dict[str, Any]:
    pce = _ms_last(m["pce"]); rsx = _ms_last(m["rsx"]); wages = _ms_last(m["wages"])
    cpi = _ms_last(m["cpi_yoy"]); cc = _ms_last(m["cc"]); save = _ms_last(m["save"])
    rj = _ms_last(m["retail_jobs"]); lj = _ms_last(m["leisure_jobs"])
    rq = _ms_last(m["retail_quits"]); lq = _ms_last(m["leisure_quits"])
    gap = (wages - cpi) if (wages is not None and cpi is not None) else None
    checks = [
        (pce or -9) > 1.5, (rsx or -9) > 1.0, (gap or -9) > 0, (cpi or 9) < 3.0,
        (cc or 9) < 3.0, (save or -9) > 4.5, (rj or -9) > 0, (lj or -9) > 0,
        (rq or -9) > 2.0, (lq or -9) > 3.0,
    ]
    score = sum(checks) / len(checks)
    if score >= 0.75:
        state = "EXPANDING"
    elif score >= 0.55:
        state = "STABLE"
    elif score >= 0.35:
        state = "COOLING"
    else:
        state = "CONTRACTING"
    text = {
        "EXPANDING": "Real spending and wages positive, credit clean, quits elevated. Consumers are healthy.",
        "STABLE": "Mixed but functional. Watch the divergence between wages and delinquencies.",
        "COOLING": "Flows are softening. Not broken yet, but the margin of safety has thinned.",
        "CONTRACTING": "Multiple stress points. The last domino is wobbling.",
    }[state]
    return {"state": state, "score": round(score, 2), "checks_passed": sum(checks),
            "checks_total": len(checks), "text": text, "gap": gap}


@app.get("/ms_spending")
def ms_spending(start_date: str | None = Query(None), end_date: str | None = Query(None)) -> list[dict[str, Any]]:
    """Real PCE YoY vs real retail sales YoY. Is the customer still showing up?"""
    with _conn() as c:
        cpi = _ms_series(c, "CPIAUCSL")
        return _ms_long({
            "Real PCE YoY": _ms_yoy(_ms_series(c, "PCEC96")),
            "Real Retail Sales YoY": _ms_real_yoy(_ms_series(c, "RSXFS"), cpi),
        }, start_date, end_date)


@app.get("/ms_wage_price")
def ms_wage_price(start_date: str | None = Query(None), end_date: str | None = Query(None)) -> list[dict[str, Any]]:
    """Service-sector wages vs CPI. The gap is real purchasing power."""
    with _conn() as c:
        return _ms_long({
            "Wages YoY": _ms_yoy(_ms_series(c, "CES0500000003")),
            "CPI YoY": _ms_yoy(_ms_series(c, "CPIAUCSL")),
        }, start_date, end_date)


@app.get("/ms_rent")
def ms_rent(start_date: str | None = Query(None), end_date: str | None = Query(None)) -> list[dict[str, Any]]:
    """Zillow market rents lead CPI shelter by 9-12 months. What renewals will price."""
    with _conn() as c:
        return _ms_long({
            "Zillow Market Rents YoY": _ms_yoy(_ms_series(c, "ZILLOW_ZORI_NATIONAL")),
            "CPI Rent YoY (lagged)": _ms_yoy(_ms_series(c, "CUSR0000SEHA")),
        }, start_date, end_date)


@app.get("/ms_credit")
def ms_credit(start_date: str | None = Query(None), end_date: str | None = Query(None)) -> list[dict[str, Any]]:
    """Credit-card delinquency vs personal saving rate. Borrowing or cushioning?"""
    with _conn() as c:
        return _ms_long({
            "CC Delinquency Rate": _ms_series(c, "DRCCLACBS"),
            "Personal Saving Rate": _ms_series(c, "PSAVERT"),
        }, start_date, end_date)


@app.get("/ms_jobs")
def ms_jobs(start_date: str | None = Query(None), end_date: str | None = Query(None)) -> list[dict[str, Any]]:
    """Retail trade and leisure/hospitality payroll growth. Main Street's employment pulse."""
    with _conn() as c:
        return _ms_long({
            "Retail Trade YoY": _ms_yoy(_ms_series(c, "USTRADE")),
            "Leisure & Hospitality YoY": _ms_yoy(_ms_series(c, "USLAH")),
        }, start_date, end_date)


@app.get("/ms_quits")
def ms_quits(start_date: str | None = Query(None), end_date: str | None = Query(None)) -> list[dict[str, Any]]:
    """JOLTS quits rate for retail and hospitality. Confidence to walk away = labor power."""
    with _conn() as c:
        return _ms_long({
            "Retail Trade Quits Rate": _ms_series(c, "JTS4400QUR"),
            "Leisure & Hospitality Quits Rate": _ms_series(c, "JTS7000QUR"),
        }, start_date, end_date)


@app.get("/ms_scorecard")
def ms_scorecard() -> list[dict[str, Any]]:
    """Six headline Main Street reads, latest value + direction. Operator glance card."""
    with _conn() as c:
        m = _ms_metrics(c)
    def row(metric, seq, detail, good_rising):
        v = _ms_last(seq)
        tr = _ms_trend(seq)
        if tr == "stable":
            health = "Flat"
        elif (tr == "rising") == good_rising:
            health = "Improving"
        else:
            health = "Deteriorating"
        return {"metric": metric, "reading": round(v, 2) if v is not None else None,
                "detail": detail, "trend": tr.capitalize(), "health": health}
    return [
        row("Customer Spending", m["pce"], "Real PCE YoY %", True),
        row("Retail Pulse", m["rsx"], "Real Retail YoY %", True),
        row("Service Wages", m["wages"], "AHE YoY %", True),
        row("Core Prices", m["core"], "Core CPI YoY %", False),
        row("Credit Strain", m["cc"], "CC Delinquency %", False),
        row("Safety Margin", m["save"], "Saving Rate %", True),
        row("Retail Quits", m["retail_quits"], "Quits Rate %", True),
        row("Hospitality Quits", m["leisure_quits"], "Quits Rate %", True),
    ]


@app.get("/ms_regime")
def ms_regime() -> str:
    """Main Street regime verdict as markdown. The one-glance operator read."""
    with _conn() as c:
        m = _ms_metrics(c)
    v = _ms_verdict(m)
    pce = _ms_last(m["pce"]); rsx = _ms_last(m["rsx"]); wages = _ms_last(m["wages"])
    cpi = _ms_last(m["cpi_yoy"]); cc = _ms_last(m["cc"]); save = _ms_last(m["save"])
    gap = v["gap"]
    def f(x, sign=True):
        if x is None:
            return "n/a"
        return f"{x:+.1f}%" if sign else f"{x:.1f}%"
    return (
        f"## Main Street Regime — {v['state']}\n\n"
        f"**{v['text']}**\n\n"
        f"Health checks passed: **{v['checks_passed']} / {v['checks_total']}** (score {v['score']}).\n\n"
        f"| Read | Latest |\n|---|---|\n"
        f"| Real PCE YoY | {f(pce)} |\n"
        f"| Real Retail YoY | {f(rsx)} |\n"
        f"| Wage-CPI gap | {f(gap)} |\n"
        f"| Wages YoY | {f(wages)} |\n"
        f"| CPI YoY | {f(cpi)} |\n"
        f"| CC Delinquency | {f(cc, sign=False)} |\n"
        f"| Saving Rate | {f(save, sign=False)} |\n"
    )
