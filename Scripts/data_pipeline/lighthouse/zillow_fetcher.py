"""
LIGHTHOUSE MACRO - ZILLOW DATA FETCHER
=======================================
Downloads Zillow ZHVI (home values) and ZORI (rent index) from public CSVs.
No API key required. Data updated monthly by Zillow.

Series stored in master DB:
  - ZILLOW_ZHVI_NATIONAL: Zillow Home Value Index (national, all homes, SA)
  - ZILLOW_ZORI_NATIONAL: Zillow Observed Rent Index (national, all homes, SA)
  - ZILLOW_ZHVI_{METRO}: Metro-level home values (top 20 MSAs)
  - ZILLOW_ZORI_{METRO}: Metro-level rents (top 20 MSAs)
"""

import requests
import pandas as pd
import sqlite3
import logging
from datetime import datetime
from io import StringIO
from typing import Tuple

logger = logging.getLogger(__name__)

# ==========================================
# CONFIGURATION
# ==========================================

# Direct CSV download URLs (Zillow public S3)
ZILLOW_URLS = {
    "ZHVI": "https://files.zillowstatic.com/research/public_csvs/zhvi/Metro_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv",
    "ZORI": "https://files.zillowstatic.com/research/public_csvs/zori/Metro_zori_uc_sfrcondomfr_sm_sa_month.csv",
}

# Top MSAs to track (by SizeRank in Zillow data)
# We always get "United States" (SizeRank 0) plus these
TOP_METROS = 20  # Track top 20 MSAs by size


def _clean_metro_name(name: str) -> str:
    """Convert metro name to a clean series ID suffix.
    'New York, NY' -> 'NEW_YORK'
    'Los Angeles, CA' -> 'LOS_ANGELES'
    """
    # Take part before comma (city name), uppercase, replace spaces
    city = name.split(",")[0].strip()
    return city.upper().replace(" ", "_").replace("-", "_").replace(".", "")


class ZillowFetcher:
    """Fetch Zillow ZHVI and ZORI data from public CSVs."""

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def _download_csv(self, url: str) -> pd.DataFrame:
        """Download CSV from Zillow."""
        logger.info(f"  Downloading {url.split('/')[-1]}...")
        r = requests.get(url, timeout=60)
        r.raise_for_status()
        return pd.read_csv(StringIO(r.text))

    def _melt_to_timeseries(self, df: pd.DataFrame, prefix: str) -> Tuple[int, int]:
        """
        Convert wide-format Zillow CSV to long-format and store in DB.

        Zillow CSVs have columns: RegionID, SizeRank, RegionName, RegionType, StateName, 2000-01-31, 2000-02-29, ...
        We melt date columns into (series_id, date, value) rows.
        """
        c = self.conn.cursor()
        total_series = 0
        total_obs = 0

        # Get date columns (YYYY-MM-DD format)
        date_cols = [col for col in df.columns if col[:2] == "20" or col[:2] == "19"]

        # Filter to national + top N metros
        df_filtered = df[df["SizeRank"] <= TOP_METROS].copy()

        for _, row in df_filtered.iterrows():
            region_name = row["RegionName"]
            region_type = row["RegionType"]

            if region_type == "country":
                series_id = f"ZILLOW_{prefix}_NATIONAL"
                title = f"Zillow {prefix} National"
            else:
                metro_suffix = _clean_metro_name(region_name)
                series_id = f"ZILLOW_{prefix}_{metro_suffix}"
                title = f"Zillow {prefix} {region_name}"

            # Extract date-value pairs, skip NaN
            obs_list = []
            for date_col in date_cols:
                val = row[date_col]
                if pd.notna(val):
                    # Normalize date to first of month for consistency
                    dt = pd.Timestamp(date_col)
                    date_str = dt.strftime("%Y-%m-01")
                    obs_list.append((series_id, date_str, float(val)))

            if not obs_list:
                continue

            c.executemany(
                "INSERT OR REPLACE INTO observations VALUES (?,?,?)", obs_list
            )

            c.execute(
                """INSERT OR REPLACE INTO series_meta
                (series_id, title, source, category, frequency, units, last_updated, last_fetched)
                VALUES (?,?,?,?,?,?,?,?)""",
                (
                    series_id,
                    title,
                    "Zillow",
                    "Housing",
                    "Monthly",
                    "USD" if prefix == "ZHVI" else "USD/mo",
                    datetime.now().isoformat(),
                    datetime.now().isoformat(),
                ),
            )

            total_series += 1
            total_obs += len(obs_list)

        self.conn.commit()
        return total_series, total_obs

    def fetch_zhvi(self) -> Tuple[int, int]:
        """Fetch Zillow Home Value Index."""
        try:
            df = self._download_csv(ZILLOW_URLS["ZHVI"])
            series, obs = self._melt_to_timeseries(df, "ZHVI")
            logger.info(f"  ZHVI: {series} series, {obs:,} observations")
            return series, obs
        except Exception as e:
            logger.error(f"  ZHVI fetch failed: {e}")
            return 0, 0

    def fetch_zori(self) -> Tuple[int, int]:
        """Fetch Zillow Observed Rent Index."""
        try:
            df = self._download_csv(ZILLOW_URLS["ZORI"])
            series, obs = self._melt_to_timeseries(df, "ZORI")
            logger.info(f"  ZORI: {series} series, {obs:,} observations")
            return series, obs
        except Exception as e:
            logger.error(f"  ZORI fetch failed: {e}")
            return 0, 0

    def fetch_all(self) -> Tuple[int, int]:
        """Fetch all Zillow data."""
        total_series = 0
        total_obs = 0

        s, o = self.fetch_zhvi()
        total_series += s
        total_obs += o

        s, o = self.fetch_zori()
        total_series += s
        total_obs += o

        return total_series, total_obs
