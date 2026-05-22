"""
LIGHTHOUSE MACRO - OPENBB / OECD INBOUND FEED
=============================================
Reverses the OpenBB flow: instead of only serving Lighthouse_Master.db OUT to
OpenBB Workspace, this pulls OECD international macro IN from the OpenBB
Platform and upserts it into the master DB on the same path every other
fetcher uses (observations + series_meta).

Free, no API key (OECD provider). Series stored as OECD_{METRIC}_{CC}:

  OECD_GDP_REAL_{CC}  Real GDP, national currency, SA (quarterly)
  OECD_CPI_YOY_{CC}   Headline CPI, % YoY (monthly)
  OECD_UNEMP_{CC}     Harmonised unemployment rate, % (monthly)
  OECD_CLI_{CC}       Composite Leading Indicator, 100=trend (monthly)
  OECD_LTIR_{CC}      Long-term (10Y) interest rate, % p.a. (monthly)
  OECD_STIR_{CC}      Short-term (3M) interest rate, % p.a. (monthly)

Country codes: US euro-area(EA) JP GB DE CA CN

This module imports `openbb` lazily inside fetch_all() so importing it never
breaks the daily pipeline in an env where OpenBB is not installed. Run it
under the python that has the openbb-* extensions (the homebrew py3.13 that
runs openbb-api):

  /opt/homebrew/opt/python@3.13/bin/python3.13 \
      Scripts/data_pipeline/lighthouse/openbb_oecd.py

Source label in series_meta: "OECD".
"""

import os
import sqlite3
import logging
import time
from datetime import datetime
from typing import Tuple

logger = logging.getLogger(__name__)

DEFAULT_DB_PATH = os.environ.get(
    "LIGHTHOUSE_DB_PATH", "/Users/bob/LHM/Data/databases/Lighthouse_Master.db"
)

# OECD country name (OpenBB arg) -> short code used in series_id
COUNTRIES = {
    "united_states": "US",
    "euro_area_20": "EA",
    "japan": "JP",
    "united_kingdom": "GB",
    "germany": "DE",
    "canada": "CA",
    "china": "CN",
}

# Some aggregates/countries only carry a subset of OECD series. Restrict the
# loop so we don't fire (and log) calls the provider will reject. Euro-area
# aggregate is CPI-only via OECD (Germany covers core-Europe for the rest);
# China lacks the OECD harmonised GDP/unemployment series.
COUNTRY_METRICS = {
    "EA": {"cpi_yoy"},
    "CN": {"cpi_yoy", "cli", "ltir", "stir"},
}

# metric_key -> (series_id stem, title stem, frequency, units, category,
#                scale)  scale multiplies the raw OECD value (rates come back
#                as decimals; ×100 makes them percent, consistent with FRED).
METRICS = {
    "gdp_real": ("OECD_GDP_REAL", "Real GDP (national currency, SA)",
                 "Quarterly", "National currency", "Growth", 1.0),
    "cpi_yoy": ("OECD_CPI_YOY", "Headline CPI",
                "Monthly", "% YoY", "Prices", 100.0),
    "unemp": ("OECD_UNEMP", "Harmonised unemployment rate",
              "Monthly", "%", "Labor", 100.0),
    "cli": ("OECD_CLI", "Composite Leading Indicator",
            "Monthly", "Index (100=trend)", "Growth", 1.0),
    "ltir": ("OECD_LTIR", "Long-term (10Y) interest rate",
             "Monthly", "% p.a.", "Financial", 100.0),
    "stir": ("OECD_STIR", "Short-term (3M) interest rate",
             "Monthly", "% p.a.", "Financial", 100.0),
}


class OECDOpenBBFetcher:
    """Pull OECD international macro from the OpenBB Platform into the DB."""

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    # -- one OpenBB call -> normalized [(date, value), ...] --------------
    def _pull(self, obb, metric: str, country: str):
        if metric == "gdp_real":
            r = obb.economy.gdp.real(provider="oecd", country=country,
                                     frequency="quarter")
        elif metric == "cpi_yoy":
            r = obb.economy.cpi(provider="oecd", country=country,
                                frequency="monthly")
        elif metric == "unemp":
            r = obb.economy.unemployment(provider="oecd", country=country,
                                         frequency="monthly")
        elif metric == "cli":
            r = obb.economy.composite_leading_indicator(provider="oecd",
                                                        country=country)
        elif metric == "ltir":
            r = obb.economy.interest_rates(provider="oecd", country=country,
                                           duration="long", frequency="monthly")
        elif metric == "stir":
            r = obb.economy.interest_rates(provider="oecd", country=country,
                                           duration="short", frequency="monthly")
        else:
            raise ValueError(f"unknown metric {metric}")

        import pandas as pd

        df = r.to_dataframe()
        if df is None or df.empty or "value" not in df.columns:
            return []

        # CPI returns multiple expenditure rows; keep headline total only.
        if "expenditure" in df.columns:
            df = df[df["expenditure"].astype(str).str.lower() == "total"]

        out = []
        for idx, val in df["value"].items():
            if val is None or pd.isna(val):
                continue
            d = pd.to_datetime(idx)
            out.append((d.strftime("%Y-%m-%d"), float(val)))
        return out

    def _store_series(self, series_id: str, title: str, frequency: str,
                      units: str, category: str, scale: float,
                      data: list) -> Tuple[int, int]:
        c = self.conn.cursor()
        date_map = {d: v * scale for d, v in data}  # dedupe by date
        obs_list = [(series_id, d, v) for d, v in sorted(date_map.items())]
        if not obs_list:
            return 0, 0

        c.executemany(
            "INSERT OR REPLACE INTO observations VALUES (?,?,?)", obs_list
        )
        c.execute(
            """INSERT OR REPLACE INTO series_meta
            (series_id, title, source, category, frequency, units,
             last_updated, last_fetched)
            VALUES (?,?,?,?,?,?,?,?)""",
            (
                series_id, title, "OECD", category, frequency, units,
                datetime.now().isoformat(), datetime.now().isoformat(),
            ),
        )
        self.conn.commit()
        return 1, len(obs_list)

    def fetch_all(self) -> Tuple[int, int]:
        try:
            from openbb import obb  # lazy: keeps pipeline import-safe
        except Exception as e:
            logger.error(f"OECD: openbb import failed ({e}). "
                         f"Run under the py3.13 env that has openbb-oecd.")
            print(f"  OECD: openbb unavailable in this env ({e})")
            return 0, 0

        total_series = 0
        total_obs = 0

        for country, cc in COUNTRIES.items():
            allowed = COUNTRY_METRICS.get(cc)
            for metric, (stem, tstem, freq, units, cat, scale) in METRICS.items():
                if allowed is not None and metric not in allowed:
                    continue
                series_id = f"{stem}_{cc}"
                # OECD throttles; retry transient errors with backoff before
                # giving up so a daily run lands the full set.
                data = None
                last_err = None
                for attempt in range(3):
                    try:
                        data = self._pull(obb, metric, country)
                        last_err = None
                        break
                    except Exception as e:
                        last_err = e
                        time.sleep(2.0 * (attempt + 1))
                if last_err is not None:
                    logger.warning(f"  {series_id}: {type(last_err).__name__}: "
                                   f"{last_err}")
                    print(f"  {series_id}: skipped "
                          f"({type(last_err).__name__}, 3 tries)")
                    continue

                if not data:
                    logger.warning(f"  {series_id}: no data")
                    print(f"  {series_id}: no data")
                    continue

                title = f"{tstem} - {country.replace('_', ' ').title()} (OECD)"
                s, o = self._store_series(series_id, title, freq, units, cat,
                                          scale, data)
                total_series += s
                total_obs += o
                logger.info(f"  {series_id}: {o} obs")
                print(f"  {series_id}: {o} obs")
                time.sleep(0.4)  # be polite to the OECD endpoint

        return total_series, total_obs


def main():
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s %(levelname)s %(message)s")
    db_path = DEFAULT_DB_PATH
    print(f"OECD inbound feed -> {db_path}")
    # Generous busy timeout: the daily pipeline cron may hold the DB.
    conn = sqlite3.connect(db_path, timeout=120)
    conn.execute("PRAGMA busy_timeout = 120000")
    try:
        fetcher = OECDOpenBBFetcher(conn)
        series, obs = fetcher.fetch_all()
        print(f"\nDONE: {series} series, {obs:,} observations upserted.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
