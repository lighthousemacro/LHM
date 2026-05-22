#!/usr/bin/env python3
"""Pull NY Fed market data into LHM/ny_fed_data/ for ny_fed_dashboard_live.py."""

from __future__ import annotations

import argparse
import sys
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
import requests

_REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = _REPO_ROOT / "ny_fed_data"
BASE = "https://markets.newyorkfed.org"
HEADERS = {"Accept": "application/json", "User-Agent": "LighthouseMacro/1.0"}
DEFAULT_RATES_START = "2018-04-03"
OPS_LAST_N = 500


def _get(path: str, timeout: int = 90) -> dict:
    url = f"{BASE}{path}"
    r = requests.get(url, headers=HEADERS, timeout=timeout)
    r.raise_for_status()
    return r.json()


def fetch_reference_rates(start_date: str) -> pd.DataFrame:
    data = _get(f"/api/rates/all/search.json?startDate={start_date}")
    rows = data.get("refRates") or []
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    if "effectiveDate" in df.columns:
        df["effectiveDate"] = pd.to_datetime(df["effectiveDate"], errors="coerce")
    for col in (
        "percentRate",
        "volumeInBillions",
        "average30day",
        "average90day",
        "average180day",
    ):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df.sort_values("effectiveDate")


def fetch_soma() -> pd.DataFrame:
    data = _get("/api/soma/summary.json", timeout=120)
    rows = data.get("soma", {}).get("summary") or []
    df = pd.DataFrame(rows)
    if "asOfDate" in df.columns:
        df["asOfDate"] = pd.to_datetime(df["asOfDate"], errors="coerce")
    for col in (
        "mbs",
        "cmbs",
        "tips",
        "tipsInflationCompensation",
        "notesbonds",
        "bills",
        "agencies",
        "frn",
        "total",
    ):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df.sort_values("asOfDate")


def fetch_repo_ops(kind: str, last_n: int) -> pd.DataFrame:
    if kind == "repo":
        path = f"/api/rp/repo/all/results/last/{last_n}.json"
    elif kind == "rrp":
        path = f"/api/rp/reverserepo/all/results/last/{last_n}.json"
    else:
        raise ValueError(kind)
    data = _get(path)
    rows = data.get("repo", {}).get("operations") or []
    df = pd.DataFrame(rows)
    for col in (
        "operationDate",
        "settlementDate",
        "maturityDate",
        "lastUpdated",
    ):
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    for col in (
        "totalAmtSubmitted",
        "totalAmtAccepted",
        "participatingCpty",
        "acceptedCpty",
        "operationLimit",
    ):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    if "operationDate" in df.columns:
        df = df.sort_values("operationDate")
    return df


def write_csv(df: pd.DataFrame, prefix: str) -> Path:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = date.today().isoformat()
    out = OUT_DIR / f"{prefix}_{stamp}.csv"
    df.to_csv(out, index=False)
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch NY Fed CSVs for the live dashboard")
    parser.add_argument(
        "--rates-start",
        default=DEFAULT_RATES_START,
        help=f"Start date for reference rates (default {DEFAULT_RATES_START})",
    )
    parser.add_argument(
        "--ops-last",
        type=int,
        default=OPS_LAST_N,
        help=f"Number of recent repo/RRP operations (default {OPS_LAST_N})",
    )
    parser.add_argument(
        "--rates-years",
        type=int,
        default=0,
        help="If set, override --rates-start with N years of history",
    )
    args = parser.parse_args()

    rates_start = args.rates_start
    if args.rates_years > 0:
        rates_start = (date.today() - timedelta(days=365 * args.rates_years)).isoformat()

    print(f"Writing CSVs to {OUT_DIR}")
    try:
        ref = fetch_reference_rates(rates_start)
        ref_path = write_csv(ref, "reference_rates")
        print(f"  reference_rates: {len(ref):,} rows -> {ref_path.name}")

        soma = fetch_soma()
        soma_path = write_csv(soma, "soma_holdings")
        print(f"  soma_holdings:   {len(soma):,} rows -> {soma_path.name}")

        repo = fetch_repo_ops("repo", args.ops_last)
        repo_path = write_csv(repo, "repo_operations")
        print(f"  repo_operations: {len(repo):,} rows -> {repo_path.name}")

        rrp = fetch_repo_ops("rrp", args.ops_last)
        rrp_path = write_csv(rrp, "reverse_repo_detailed")
        print(f"  reverse_repo:    {len(rrp):,} rows -> {rrp_path.name}")
    except requests.RequestException as exc:
        print(f"NY Fed API error: {exc}", file=sys.stderr)
        return 1

    print("Done. Run: .venv/bin/python Scripts/ny_fed_dashboard_live.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
