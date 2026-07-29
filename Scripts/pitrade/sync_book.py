"""
Sync the live Crosscurrents book from PiTrade into Lighthouse_Master.db.

This exists so book positioning is never quoted from a phone screenshot
again. Every run writes a dated snapshot, so the holdings log is auditable
and `latest_book()` is always the real thing.

    python3 Scripts/pitrade/sync_book.py            # sync and print
    python3 Scripts/pitrade/sync_book.py --show     # print last snapshot only

Schema:
    crosscurrents_holdings(as_of, ticker, weight_pct, quantity,
                           market_value, cost_basis, unrealized_pct,
                           portfolio, source)
    primary key (as_of, ticker, portfolio)
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from pitrade_client import PiTradeClient, PiTradeError  # noqa: E402

DB_PATH = Path("/Users/bob/LHM/Data/databases/Lighthouse_Master.db")

DDL = """
CREATE TABLE IF NOT EXISTS crosscurrents_holdings (
    as_of          TEXT NOT NULL,
    ticker         TEXT NOT NULL,
    portfolio      TEXT NOT NULL DEFAULT 'Crosscurrents',
    weight_pct     REAL,
    quantity       REAL,
    market_value   REAL,
    cost_basis     REAL,
    unrealized_pct REAL,
    source         TEXT NOT NULL DEFAULT 'pitrade_api',
    PRIMARY KEY (as_of, ticker, portfolio)
);
"""

# PiTrade has not published the holdings schema, so accept the field names
# their payload is most likely to use and normalise to ours.
FIELD_ALIASES = {
    "ticker": ("ticker", "symbol", "securitySymbol", "instrument"),
    "weight_pct": ("weight", "weightPct", "allocation", "allocationPercent", "percentage"),
    "quantity": ("quantity", "qty", "shares", "units"),
    "market_value": ("marketValue", "value", "currentValue", "marketVal"),
    "cost_basis": ("costBasis", "cost", "averageCost", "avgCost"),
    "unrealized_pct": ("unrealizedPct", "gainPercent", "returnPct", "pnlPercent"),
}


def _pick(row: dict, key: str):
    for alias in FIELD_ALIASES[key]:
        if alias in row and row[alias] is not None:
            return row[alias]
    return None


def _iter_holdings(payload) -> list[dict]:
    """Walk an unknown payload shape and pull out anything ticker-like."""
    out: list[dict] = []

    def visit(node, portfolio="Crosscurrents"):
        if isinstance(node, dict):
            name = node.get("name") or node.get("portfolioName") or portfolio
            if any(a in node for a in FIELD_ALIASES["ticker"]):
                out.append({"_portfolio": portfolio, **node})
                return
            for value in node.values():
                visit(value, name)
        elif isinstance(node, list):
            for item in node:
                visit(item, portfolio)

    visit(payload)
    return out


def sync(verbose: bool = True) -> int:
    client = PiTradeClient()
    payload = client.portfolios()
    holdings = _iter_holdings(payload)

    if not holdings:
        raise PiTradeError(
            "No holdings found in the /api/portfolios payload. Raw response:\n"
            + json.dumps(payload, indent=2)[:2000]
        )

    as_of = date.today().isoformat()
    rows = []
    for h in holdings:
        ticker = _pick(h, "ticker")
        if not ticker:
            continue
        rows.append(
            (
                as_of,
                str(ticker).upper(),
                h.get("_portfolio", "Crosscurrents"),
                _pick(h, "weight_pct"),
                _pick(h, "quantity"),
                _pick(h, "market_value"),
                _pick(h, "cost_basis"),
                _pick(h, "unrealized_pct"),
                "pitrade_api",
            )
        )

    conn = sqlite3.connect(DB_PATH)
    conn.execute(DDL)
    conn.executemany(
        "INSERT OR REPLACE INTO crosscurrents_holdings "
        "(as_of, ticker, portfolio, weight_pct, quantity, market_value, "
        " cost_basis, unrealized_pct, source) VALUES (?,?,?,?,?,?,?,?,?)",
        rows,
    )
    conn.commit()

    if verbose:
        print(f"Synced {len(rows)} positions as of {as_of}")
        show(conn)
    conn.close()
    return len(rows)


def show(conn: sqlite3.Connection | None = None) -> None:
    own = conn is None
    conn = conn or sqlite3.connect(DB_PATH)
    conn.execute(DDL)
    latest = conn.execute("SELECT MAX(as_of) FROM crosscurrents_holdings").fetchone()[0]
    if not latest:
        print("No snapshots recorded yet.")
        if own:
            conn.close()
        return
    print(f"\nCrosscurrents book, {latest}")
    print(f"{'Ticker':<8}{'Weight':>9}{'Qty':>12}{'Mkt Value':>13}{'Unreal':>9}")
    for t, w, q, mv, up in conn.execute(
        "SELECT ticker, weight_pct, quantity, market_value, unrealized_pct "
        "FROM crosscurrents_holdings WHERE as_of = ? ORDER BY weight_pct DESC",
        (latest,),
    ):
        print(
            f"{t:<8}{'' if w is None else f'{w:8.2f}%':>9}"
            f"{'' if q is None else f'{q:12.4f}':>12}"
            f"{'' if mv is None else f'${mv:,.2f}':>13}"
            f"{'' if up is None else f'{up:8.2f}%':>9}"
        )
    if own:
        conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--show", action="store_true", help="print last snapshot, no fetch")
    args = parser.parse_args()

    if args.show:
        show()
    else:
        try:
            sync()
        except PiTradeError as exc:
            print(f"Sync failed: {exc}", file=sys.stderr)
            sys.exit(1)
