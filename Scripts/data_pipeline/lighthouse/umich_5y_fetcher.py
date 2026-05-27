"""
UMich 5-year inflation expectations fetcher.

The University of Michigan Surveys of Consumers Table 33 publishes the median
5-year-ahead expected change in prices. Question asked monthly since 1979 (a few
gaps in the early 80s). FRED does not host this series directly, so we fetch the
historical XLS from UMich's data portal and upsert it into Lighthouse_Master.db
under series_id = MICH5Y.

Source: https://data.sca.isr.umich.edu/tables.php  (Table 33, Historical / RB)

The k= query param in the public URL is a per-revision hash that UMich rotates.
The fetcher scrapes the tables.php landing for the current Table 33 XLS URL
so the link stays valid across UMich updates.
"""

from __future__ import annotations

import logging
import re
import sqlite3
from pathlib import Path
from typing import Optional

import pandas as pd
import requests

log = logging.getLogger(__name__)

UMICH_TABLES_URL = "https://data.sca.isr.umich.edu/tables.php"
UMICH_BASE = "https://data.sca.isr.umich.edu/"
SERIES_ID = "MICH5Y"
SERIES_LABEL = "UMich 5Y Inflation Expectations (median)"
MEDIAN_COL = 13


def _resolve_historical_xls_url() -> str:
    """Scrape tables.php for the current Table 33 historical (RB) XLS URL."""
    resp = requests.get(UMICH_TABLES_URL, timeout=30)
    resp.raise_for_status()
    pattern = re.compile(r"get-table\.php\?c=RB&y=\d{4}&m=\d+&n=33&f=xls&k=[a-f0-9]+")
    matches = pattern.findall(resp.text)
    if not matches:
        raise RuntimeError("Could not locate Table 33 historical XLS link on tables.php")
    return UMICH_BASE + matches[0]


def fetch_mich5y() -> pd.DataFrame:
    """Fetch the UMich 5y median inflation expectations history.

    Returns a DataFrame with columns: date (Timestamp month-start), value (float pct).
    """
    url = _resolve_historical_xls_url()
    log.info("Fetching UMich Table 33 from %s", url)
    resp = requests.get(url, timeout=60)
    resp.raise_for_status()
    from io import BytesIO
    raw = pd.read_excel(BytesIO(resp.content), sheet_name=0, header=None)

    # Data starts at row 10; columns 0=month name, 1=year, 13=median.
    rows = []
    for i in range(10, len(raw)):
        month = raw.iat[i, 0]
        year = raw.iat[i, 1]
        median = raw.iat[i, MEDIAN_COL]
        if pd.isna(month) or pd.isna(year) or pd.isna(median):
            continue
        try:
            d = pd.Timestamp(f"{int(year):04d}-{month}-01")
        except Exception:
            continue
        rows.append((d, float(median)))

    df = pd.DataFrame(rows, columns=["date", "value"]).sort_values("date").reset_index(drop=True)
    log.info("Parsed %d UMich 5y observations from %s to %s",
             len(df), df["date"].min().date(), df["date"].max().date())
    return df


def upsert_to_db(df: pd.DataFrame, conn) -> int:
    """Upsert the series into observations + register meta. Returns rows written.

    Accepts an open sqlite3.Connection so it can share a transaction with the
    rest of the daily pipeline.
    """
    cur = conn.cursor()
    cur.execute(
        """
        INSERT OR IGNORE INTO series_meta
            (series_id, title, source, category, frequency, units)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (SERIES_ID, SERIES_LABEL, "UMich", "Inflation Expectations", "monthly", "Percent"),
    )
    n = 0
    for d, v in df.itertuples(index=False):
        cur.execute(
            "INSERT OR REPLACE INTO observations (series_id, date, value) VALUES (?, ?, ?)",
            (SERIES_ID, d.strftime("%Y-%m-%d"), float(v)),
        )
        n += 1
    conn.commit()
    log.info("Upserted %d rows for %s", n, SERIES_ID)
    return n


class UMichFetcher:
    """Pipeline-compatible fetcher wrapper.

    Matches the interface of the other lighthouse/* fetchers so it can be
    invoked from run_daily_update as a standard "UMICH" source.
    """

    def __init__(self, conn):
        self.conn = conn

    def fetch_all(self) -> tuple[int, int]:
        """Returns (num_series, num_observations) for the daily logger."""
        df = fetch_mich5y()
        n_obs = upsert_to_db(df, self.conn)
        return 1, n_obs


def run(db_path: Optional[str] = None) -> int:
    """Standalone entry point: fetch + upsert. Returns row count."""
    db_path = db_path or "/Users/bob/LHM/Data/databases/Lighthouse_Master.db"
    df = fetch_mich5y()
    conn = sqlite3.connect(db_path)
    try:
        n = upsert_to_db(df, conn)
    finally:
        conn.close()
    return n


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    n = run()
    print(f"Wrote {n} rows for {SERIES_ID}")
