"""
TreasuryDirect / fiscaldata.treasury.gov fetchers for Lighthouse_Master.db.

Adds four series families:
  TD_AUCTION_TAIL_10Y     daily, bp     stop yield - average yield (proxy for tail)
  TD_AUCTION_BTC_10Y      daily         bid-to-cover ratio at 10Y note auctions
  TD_INDIRECT_SHARE_10Y   daily, %      indirect bidder accepted / total accepted
  TD_BILLS_SHARE          monthly, %    bills outstanding / total marketable outstanding (MSPD table 3)
  TD_WAM_MARKETABLE       monthly, mo   weighted-average maturity of marketable Treasury debt (MSPD table 5)

Usage (one-shot backfill):
    PYTHONPATH=/Users/bob/LHM python -m Scripts.data_pipeline.lighthouse.treasury_direct backfill
"""

from __future__ import annotations

import logging
import sqlite3
import sys
import time
from datetime import datetime, date
from pathlib import Path
from typing import Iterator

import pandas as pd
import requests

DB_PATH = Path("/Users/bob/LHM/Data/databases/Lighthouse_Master.db")
BASE = "https://api.fiscaldata.treasury.gov/services/api/fiscal_service"
PAGE_SIZE = 5000
TIMEOUT = 30
MAX_RETRIES = 4

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
log = logging.getLogger("td_fetcher")


def _get_paged(path: str, params: dict | None = None) -> Iterator[dict]:
    """Yield rows from a paged fiscaldata endpoint."""
    params = dict(params or {})
    params.setdefault("page[size]", PAGE_SIZE)
    page = 1
    while True:
        params["page[number]"] = page
        url = f"{BASE}{path}"
        last_exc: Exception | None = None
        for attempt in range(MAX_RETRIES):
            try:
                r = requests.get(url, params=params, timeout=TIMEOUT)
                r.raise_for_status()
                payload = r.json()
                break
            except (requests.RequestException, ValueError) as e:
                last_exc = e
                wait = 2 ** attempt
                log.warning(f"  attempt {attempt+1} failed ({e}); retrying in {wait}s")
                time.sleep(wait)
        else:
            raise last_exc  # type: ignore

        rows = payload.get("data", [])
        if not rows:
            return
        for row in rows:
            yield row
        meta = payload.get("meta", {})
        total = meta.get("total-pages") or meta.get("total_pages") or 1
        if page >= total:
            return
        page += 1


def _to_float(x) -> float | None:
    if x is None or x == "" or x == "null":
        return None
    try:
        return float(str(x).replace(",", ""))
    except ValueError:
        return None


def fetch_auction_results(security_term: str = "10-Year") -> pd.DataFrame:
    """10y note auction microstructure. Returns one row per auction date."""
    log.info(f"Fetching {security_term} note auctions from TreasuryDirect ...")
    fields = ",".join([
        "auction_date", "issue_date", "security_type", "security_term",
        "high_yield", "avg_med_yield", "low_yield",
        "bid_to_cover_ratio", "offering_amt", "total_accepted",
        "indirect_bidder_accepted", "direct_bidder_accepted", "primary_dealer_accepted",
    ])
    params = {
        "fields": fields,
        "filter": f"security_type:eq:Note,security_term:eq:{security_term}",
        "sort": "auction_date",
    }
    rows = list(_get_paged("/v1/accounting/od/auctions_query", params))
    log.info(f"  got {len(rows)} auction rows")

    df = pd.DataFrame(rows)
    if df.empty:
        return df
    df["auction_date"] = pd.to_datetime(df["auction_date"])
    for col in ["high_yield", "avg_med_yield", "low_yield", "bid_to_cover_ratio",
                "offering_amt", "total_accepted",
                "indirect_bidder_accepted", "direct_bidder_accepted", "primary_dealer_accepted"]:
        df[col] = df[col].apply(_to_float)
    df = df.dropna(subset=["auction_date", "high_yield"])
    df = df.sort_values("auction_date").reset_index(drop=True)
    return df


def fetch_mspd_table_3(start_date: str = "2000-01-31") -> pd.DataFrame:
    """MSPD table 3 (marketable detail). Used for bills share."""
    log.info("Fetching MSPD table 3 (marketable detail) ...")
    params = {
        "fields": "record_date,security_class1_desc,outstanding_amt",
        "filter": f"record_date:gte:{start_date}",
        "sort": "record_date",
    }
    rows = list(_get_paged("/v1/debt/mspd/mspd_table_3_market", params))
    log.info(f"  got {len(rows)} mspd_3 rows")
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    df["record_date"] = pd.to_datetime(df["record_date"])
    df["outstanding_amt"] = df["outstanding_amt"].apply(_to_float)
    return df


def compute_bills_share(mspd3: pd.DataFrame) -> pd.DataFrame:
    """Bills outstanding / total marketable outstanding by month. Returns date, value (%)."""
    if mspd3.empty:
        return pd.DataFrame(columns=["date", "value"])

    def is_bills(row) -> bool:
        s = (row.get("security_class1_desc") or "").lower()
        return "bills" in s

    bills_total = (mspd3[mspd3.apply(is_bills, axis=1)]
                   .groupby("record_date")["outstanding_amt"].sum())
    grand_total = mspd3.groupby("record_date")["outstanding_amt"].sum()
    out = (bills_total / grand_total * 100.0).reset_index()
    out.columns = ["date", "value"]
    out = out.dropna()
    out = out.sort_values("date").reset_index(drop=True)
    return out


def fetch_mspd_table_5(start_date: str = "2000-01-31") -> pd.DataFrame:
    """MSPD table 5 (CUSIP-level outstanding). Used to compute WAM."""
    log.info("Fetching MSPD table 5 (CUSIP detail) — this is the largest pull ...")
    params = {
        "fields": "record_date,security_class1_desc,maturity_date,outstanding_amt",
        "filter": f"record_date:gte:{start_date}",
        "sort": "record_date",
    }
    rows = list(_get_paged("/v1/debt/mspd/mspd_table_5", params))
    log.info(f"  got {len(rows)} mspd_5 rows")
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    df["record_date"] = pd.to_datetime(df["record_date"])
    df["maturity_date"] = pd.to_datetime(df["maturity_date"], errors="coerce")
    df["outstanding_amt"] = df["outstanding_amt"].apply(_to_float)
    return df


MARKETABLE_CLASSES = {
    "Bills Maturity Value", "Treasury Bills",
    "Notes", "Treasury Notes",
    "Bonds", "Treasury Bonds",
    "Treasury Inflation-Protected Securities",
    "Inflation-Protected Securities",
    "Treasury Floating Rate Notes",
    "Floating Rate Notes",
}


def compute_wam(mspd5: pd.DataFrame) -> pd.DataFrame:
    """Weighted-average maturity of marketable Treasury debt in months. Returns date, value."""
    if mspd5.empty:
        return pd.DataFrame(columns=["date", "value"])
    df = mspd5[mspd5["security_class1_desc"].isin(MARKETABLE_CLASSES)].copy()
    df = df.dropna(subset=["maturity_date", "outstanding_amt"])
    df = df[df["outstanding_amt"] > 0]
    df["months_to_maturity"] = ((df["maturity_date"] - df["record_date"]).dt.days / 30.4375)
    df = df[df["months_to_maturity"] >= 0]

    def wam_for_date(g: pd.DataFrame) -> float:
        w = g["outstanding_amt"]
        return float((g["months_to_maturity"] * w).sum() / w.sum())

    out = (df.groupby("record_date")
             .apply(wam_for_date)
             .reset_index(name="value")
             .rename(columns={"record_date": "date"}))
    out = out.sort_values("date").reset_index(drop=True)
    return out


def upsert_series(conn: sqlite3.Connection, series_id: str, title: str,
                  category: str, frequency: str, units: str, source: str,
                  obs: pd.DataFrame) -> int:
    """Insert/replace a series + its observations. obs must have columns date, value."""
    if obs.empty:
        log.warning(f"  {series_id}: no observations to write")
        return 0
    c = conn.cursor()
    obs = obs.dropna().copy()
    obs["date"] = pd.to_datetime(obs["date"]).dt.strftime("%Y-%m-%d")
    rows = [(series_id, d, float(v)) for d, v in zip(obs["date"], obs["value"])]
    c.executemany("INSERT OR REPLACE INTO observations VALUES (?,?,?)", rows)
    last_date = obs["date"].iloc[-1]
    c.execute("""INSERT OR REPLACE INTO series_meta
                 (series_id, title, source, category, frequency, units,
                  last_updated, last_fetched, data_quality, last_value_date, obs_count)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
              (series_id, title, source, category, frequency, units,
               last_date, datetime.utcnow().isoformat(timespec="seconds"),
               "ok", last_date, len(rows)))
    conn.commit()
    log.info(f"  {series_id}: wrote {len(rows)} observations through {last_date}")
    return len(rows)


def backfill(db_path: Path = DB_PATH) -> None:
    conn = sqlite3.connect(db_path)
    try:
        # 10Y auctions
        au = fetch_auction_results("10-Year")
        if not au.empty:
            au["tail_bp"] = (au["high_yield"] - au["avg_med_yield"]) * 100.0
            au["indirect_share_pct"] = (au["indirect_bidder_accepted"] /
                                        au["total_accepted"]) * 100.0
            tail_df = au[["auction_date", "tail_bp"]].rename(
                columns={"auction_date": "date", "tail_bp": "value"}).dropna()
            btc_df = au[["auction_date", "bid_to_cover_ratio"]].rename(
                columns={"auction_date": "date", "bid_to_cover_ratio": "value"}).dropna()
            ind_df = au[["auction_date", "indirect_share_pct"]].rename(
                columns={"auction_date": "date", "indirect_share_pct": "value"}).dropna()
            upsert_series(conn, "TD_AUCTION_TAIL_10Y", "10-Year Note Auction Tail (bp)",
                          "Treasury_Auctions", "irregular", "bp", "TreasuryDirect", tail_df)
            upsert_series(conn, "TD_AUCTION_BTC_10Y", "10-Year Note Auction Bid-to-Cover",
                          "Treasury_Auctions", "irregular", "ratio", "TreasuryDirect", btc_df)
            upsert_series(conn, "TD_INDIRECT_SHARE_10Y", "10-Year Note Auction Indirect Bidder Share",
                          "Treasury_Auctions", "irregular", "%", "TreasuryDirect", ind_df)

        # MSPD bills share + WAM
        mspd3 = fetch_mspd_table_3()
        bills = compute_bills_share(mspd3)
        upsert_series(conn, "TD_BILLS_SHARE", "Bills Share of Marketable Treasury Debt",
                      "Treasury_Composition", "monthly", "%", "TreasuryDirect", bills)

        mspd5 = fetch_mspd_table_5()
        wam = compute_wam(mspd5)
        upsert_series(conn, "TD_WAM_MARKETABLE", "Weighted Average Maturity of Marketable Treasury Debt",
                      "Treasury_Composition", "monthly", "months", "TreasuryDirect", wam)
    finally:
        conn.close()


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "backfill"
    if cmd == "backfill":
        backfill()
    else:
        print(f"unknown command: {cmd}", file=sys.stderr)
        sys.exit(2)
