"""
LIGHTHOUSE MACRO - MARKET DATA FETCHERS
========================================
Fetchers for market structure (MSI) and sentiment (SPI) data.

Data Sources:
- yfinance: S&P 500 price data for trend/momentum calculations
- FRED: VIX (VIXCLS), Put/Call ratio
- AAII: Investor sentiment survey (web scrape)
- NAAIM: Manager exposure survey (web scrape)
- Barchart/Other: Breadth data (% above MAs, NH-NL, A/D line)
"""

import requests
import pandas as pd
import numpy as np
import sqlite3
import time
import logging
from datetime import datetime, timedelta
from typing import Tuple, Optional, Dict, List
from io import StringIO, BytesIO

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False

logger = logging.getLogger(__name__)


# ==========================================
# YAHOO FINANCE FETCHER (S&P 500 Price Data)
# ==========================================

class YFinanceFetcher:
    """
    Fetch S&P 500 price data from Yahoo Finance.
    Used for computing trend/momentum components of MSI.
    """

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def fetch_spx(self, start_date: str = "2000-01-01") -> Tuple[int, int]:
        """
        Fetch S&P 500 (^GSPC) price data and compute derived metrics.

        Returns:
            Tuple of (series_count, observations_count)
        """
        c = self.conn.cursor()
        total_obs = 0

        try:
            ticker = "^GSPC"
            end_date = datetime.now().strftime("%Y-%m-%d")

            logger.info(f"   Fetching S&P 500 from {start_date}...")

            # Use yfinance library if available
            if YFINANCE_AVAILABLE:
                spx = yf.Ticker(ticker)
                df = spx.history(start=start_date, end=end_date)
                df = df.reset_index()
                df = df.rename(columns={"index": "Date"})
            else:
                # Fallback to direct API call
                url = f"https://query1.finance.yahoo.com/v7/finance/download/{ticker}"
                params = {
                    "period1": int(pd.Timestamp(start_date).timestamp()),
                    "period2": int(pd.Timestamp(end_date).timestamp()),
                    "interval": "1d",
                    "events": "history",
                    "includeAdjustedClose": "true"
                }
                headers = {
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
                }
                r = requests.get(url, params=params, headers=headers, timeout=30)
                if r.status_code != 200:
                    logger.error(f"Yahoo Finance API returned {r.status_code}")
                    return 0, 0
                df = pd.read_csv(StringIO(r.text), parse_dates=["Date"])

            df = df.dropna(subset=["Close"])
            df = df.sort_values("Date")

            if len(df) > 0:

                # Store raw price data
                for _, row in df.iterrows():
                    date_str = row["Date"].strftime("%Y-%m-%d")

                    # Store Close price
                    c.execute("INSERT OR REPLACE INTO observations VALUES (?,?,?)",
                             ("SPX_Close", date_str, float(row["Close"])))
                    total_obs += 1

                    # Store Volume if available
                    if pd.notna(row.get("Volume")):
                        c.execute("INSERT OR REPLACE INTO observations VALUES (?,?,?)",
                                 ("SPX_Volume", date_str, float(row["Volume"])))
                        total_obs += 1

                # Compute derived metrics
                derived_obs = self._compute_derived_metrics(df, c)
                total_obs += derived_obs

                # Update metadata
                series_list = [
                    ("SPX_Close", "S&P 500 Close Price"),
                    ("SPX_Volume", "S&P 500 Volume"),
                    ("SPX_20d_MA", "S&P 500 20-day Moving Average"),
                    ("SPX_50d_MA", "S&P 500 50-day Moving Average"),
                    ("SPX_200d_MA", "S&P 500 200-day Moving Average"),
                    ("SPX_vs_20d_pct", "S&P 500 % vs 20-day MA"),
                    ("SPX_vs_50d_pct", "S&P 500 % vs 50-day MA"),
                    ("SPX_vs_200d_pct", "S&P 500 % vs 200-day MA"),
                    ("SPX_20d_slope", "S&P 500 20-day MA Slope (annualized)"),
                    ("SPX_50d_slope", "S&P 500 50-day MA Slope (annualized)"),
                    ("SPX_200d_slope", "S&P 500 200-day MA Slope (annualized)"),
                    ("SPX_RoC_21d", "S&P 500 21-day Rate of Change"),
                    ("SPX_RoC_63d", "S&P 500 63-day Rate of Change"),
                    ("SPX_Z_RoC_63d", "S&P 500 63-day Rate of Change (Z-scored)"),
                    ("SPX_RSI_14d", "S&P 500 14-day RSI"),
                ]

                for series_id, title in series_list:
                    c.execute("""INSERT OR REPLACE INTO series_meta
                                (series_id, title, source, category, frequency, units, last_updated, last_fetched)
                                VALUES (?,?,?,?,?,?,?,?)""",
                             (series_id, title, "Yahoo", "Market_Structure", "Daily", "",
                              datetime.now().isoformat(), datetime.now().isoformat()))

                self.conn.commit()
                logger.info(f"   S&P 500: {total_obs:,} observations")
                return len(series_list), total_obs
            else:
                logger.warning("No S&P 500 data retrieved")
                return 0, 0

        except Exception as e:
            logger.error(f"Yahoo Finance Error: {e}")
            return 0, 0

        return 0, 0

    def _compute_derived_metrics(self, df: pd.DataFrame, cursor) -> int:
        """Compute trend and momentum metrics from price data."""
        obs_count = 0

        df = df.copy()
        df = df.set_index("Date")
        close = df["Close"]

        # Moving averages
        ma_20 = close.rolling(20).mean()
        ma_50 = close.rolling(50).mean()
        ma_200 = close.rolling(200).mean()

        # % vs MAs
        vs_20 = (close / ma_20 - 1) * 100
        vs_50 = (close / ma_50 - 1) * 100
        vs_200 = (close / ma_200 - 1) * 100

        # MA slopes (annualized % change)
        slope_20 = ma_20.pct_change(5) * 252 * 100  # 5-day slope annualized
        slope_50 = ma_50.pct_change(10) * 252 * 100
        slope_200 = ma_200.pct_change(20) * 252 * 100

        # Rate of change
        roc_21 = close.pct_change(21) * 100
        roc_63 = close.pct_change(63) * 100

        # Z-scored RoC
        roc_63_mean = roc_63.rolling(252).mean()
        roc_63_std = roc_63.rolling(252).std()
        z_roc_63 = (roc_63 - roc_63_mean) / roc_63_std.replace(0, np.nan)

        # RSI
        delta = close.diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss.replace(0, np.nan)
        rsi = 100 - (100 / (1 + rs))

        # Store all metrics
        metrics = {
            "SPX_20d_MA": ma_20,
            "SPX_50d_MA": ma_50,
            "SPX_200d_MA": ma_200,
            "SPX_vs_20d_pct": vs_20,
            "SPX_vs_50d_pct": vs_50,
            "SPX_vs_200d_pct": vs_200,
            "SPX_20d_slope": slope_20,
            "SPX_50d_slope": slope_50,
            "SPX_200d_slope": slope_200,
            "SPX_RoC_21d": roc_21,
            "SPX_RoC_63d": roc_63,
            "SPX_Z_RoC_63d": z_roc_63,
            "SPX_RSI_14d": rsi,
        }

        for series_id, series in metrics.items():
            for date, value in series.dropna().items():
                date_str = date.strftime("%Y-%m-%d")
                cursor.execute("INSERT OR REPLACE INTO observations VALUES (?,?,?)",
                              (series_id, date_str, float(value)))
                obs_count += 1

        return obs_count


# ==========================================
# BREADTH DATA FETCHER
# ==========================================

class BreadthFetcher:
    """
    Fetch market breadth data.
    Sources: Stockcharts, Barchart, or computed from component stocks.
    """

    # FRED series for breadth proxies
    BREADTH_FRED_SERIES = {
        # These don't exist in FRED but we'll compute them differently
    }

    def __init__(self, conn: sqlite3.Connection, fred_api_key: str):
        self.conn = conn
        self.fred_api_key = fred_api_key

    def fetch_all(self) -> Tuple[int, int]:
        """
        Fetch breadth data from available sources.

        Note: True breadth data (% above MAs, A/D line) requires premium data feeds.
        We'll use proxy methods and available free sources.
        """
        c = self.conn.cursor()
        total_obs = 0
        series_count = 0

        # Fetch NYSE Advance-Decline data from FRED (if available)
        # FRED has some breadth proxies

        # For now, we'll create placeholder structure and note data source requirements
        logger.info("   Breadth data requires premium sources (StockCharts, Bloomberg)")
        logger.info("   Using proxy computations where possible...")

        # Compute estimated breadth from sector ETF performance
        # This is a proxy but useful
        sector_obs = self._compute_sector_breadth_proxy(c)
        total_obs += sector_obs

        self.conn.commit()
        return series_count, total_obs

    def _compute_sector_breadth_proxy(self, cursor) -> int:
        """
        Compute breadth proxy from sector ETF performance.
        Uses S&P 500 sector ETFs as a proxy for broader market breadth.
        """
        # This would require fetching sector ETF data
        # For now, return 0 as placeholder
        return 0


# ==========================================
# SENTIMENT DATA FETCHER
# ==========================================

class SentimentFetcher:
    """
    Fetch sentiment and positioning data for SPI.

    Sources:
    - FRED: VIX (VIXCLS)
    - AAII: Investor sentiment survey
    - NAAIM: Manager exposure index
    """

    FRED_BASE_URL = "https://api.stlouisfed.org/fred"
    AAII_URL = "https://www.aaii.com/files/surveys/sentiment.xls"

    def __init__(self, conn: sqlite3.Connection, fred_api_key: str):
        self.conn = conn
        self.fred_api_key = fred_api_key

    def fetch_all(self) -> Tuple[int, int]:
        """Fetch all sentiment data sources."""
        total_obs = 0
        series_count = 0

        # VIX term structure
        vix_series, vix_obs = self._fetch_vix_term_structure()
        series_count += vix_series
        total_obs += vix_obs

        # AAII Sentiment
        aaii_series, aaii_obs = self._fetch_aaii()
        series_count += aaii_series
        total_obs += aaii_obs

        # NAAIM Exposure
        naaim_series, naaim_obs = self._fetch_naaim()
        series_count += naaim_series
        total_obs += naaim_obs

        return series_count, total_obs

    def _fetch_vix_term_structure(self) -> Tuple[int, int]:
        """
        Fetch VIX and compute term structure metrics.
        VIX spot is in FRED (VIXCLS).
        """
        c = self.conn.cursor()
        obs_count = 0

        try:
            # VIX is already fetched via FRED curated series
            # Here we compute additional VIX-based metrics

            # Get existing VIX data
            c.execute("""SELECT date, value FROM observations
                        WHERE series_id = 'VIXCLS'
                        ORDER BY date""")
            rows = c.fetchall()

            if rows:
                df = pd.DataFrame(rows, columns=["date", "VIX"])
                df["date"] = pd.to_datetime(df["date"])
                df = df.set_index("date")

                # VIX vs 50-day MA
                vix_50d = df["VIX"].rolling(50).mean()
                vix_vs_50d = (df["VIX"] / vix_50d - 1) * 100

                # VIX percentile (252-day)
                vix_pct = df["VIX"].rolling(252).apply(
                    lambda x: pd.Series(x).rank(pct=True).iloc[-1] * 100, raw=False
                )

                # Store derived metrics
                for date, value in vix_vs_50d.dropna().items():
                    date_str = date.strftime("%Y-%m-%d")
                    c.execute("INSERT OR REPLACE INTO observations VALUES (?,?,?)",
                             ("VIX_vs_50d_pct", date_str, float(value)))
                    obs_count += 1

                for date, value in vix_pct.dropna().items():
                    date_str = date.strftime("%Y-%m-%d")
                    c.execute("INSERT OR REPLACE INTO observations VALUES (?,?,?)",
                             ("VIX_percentile_252d", date_str, float(value)))
                    obs_count += 1

                # VIX / VIX3M term-structure ratio (>1 = backwardation).
                # Was a one-off ingestion orphaned at 2026-05-15; derived daily here now.
                c.execute("""SELECT date, value FROM observations
                            WHERE series_id = 'VXVCLS'
                            ORDER BY date""")
                vxv_rows = c.fetchall()
                if vxv_rows:
                    vxv = pd.DataFrame(vxv_rows, columns=["date", "VIX3M"])
                    vxv["date"] = pd.to_datetime(vxv["date"])
                    vxv = vxv.set_index("date")["VIX3M"]
                    backwardation = (df["VIX"] / vxv).dropna()
                    for date, value in backwardation.items():
                        date_str = date.strftime("%Y-%m-%d")
                        c.execute("INSERT OR REPLACE INTO observations VALUES (?,?,?)",
                                 ("VIX_BACKWARDATION", date_str, float(value)))
                        obs_count += 1
                    c.execute("""INSERT OR REPLACE INTO series_meta
                                (series_id, title, source, category, frequency, units, last_updated, last_fetched)
                                VALUES (?,?,?,?,?,?,?,?)""",
                             ("VIX_BACKWARDATION", "VIX/VIX3M term structure (>1=backwardation)",
                              "Derived/CBOE", "Sentiment", "Daily", "Ratio",
                              datetime.now().isoformat(), datetime.now().isoformat()))

                # Update metadata
                for series_id, title in [
                    ("VIX_vs_50d_pct", "VIX % vs 50-day MA"),
                    ("VIX_percentile_252d", "VIX Percentile (252-day)"),
                ]:
                    c.execute("""INSERT OR REPLACE INTO series_meta
                                (series_id, title, source, category, frequency, units, last_updated, last_fetched)
                                VALUES (?,?,?,?,?,?,?,?)""",
                             (series_id, title, "Derived", "Sentiment", "Daily", "Percent",
                              datetime.now().isoformat(), datetime.now().isoformat()))

                self.conn.commit()
                logger.info(f"   VIX metrics: {obs_count:,} observations")
                return 2, obs_count

        except Exception as e:
            logger.error(f"VIX metrics error: {e}")

        return 0, 0

    def _fetch_aaii(self) -> Tuple[int, int]:
        """
        Fetch AAII Investor Sentiment Survey.
        Weekly data: % Bullish, % Bearish, % Neutral.
        """
        c = self.conn.cursor()
        obs_count = 0

        try:
            logger.info("   Fetching AAII sentiment...")

            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
            }

            r = requests.get(self.AAII_URL, headers=headers, timeout=30)

            if r.status_code == 200:
                # Parse Excel file (xls format requires xlrd engine)
                try:
                    df = pd.read_excel(
                        BytesIO(r.content),
                        sheet_name=0,
                        skiprows=2,
                        engine='xlrd'
                    )
                except Exception as excel_err:
                    logger.warning(f"Excel parse failed with xlrd: {excel_err}")
                    # Try openpyxl for xlsx format
                    try:
                        df = pd.read_excel(
                            BytesIO(r.content),
                            sheet_name=0,
                            skiprows=2,
                            engine='openpyxl'
                        )
                    except Exception as e2:
                        logger.error(f"Excel parse also failed with openpyxl: {e2}")
                        return 0, 0

                # AAII file has column headers in first data row
                # Columns are: 'Reported' (Date), 'Unnamed: 1' (Bullish), 'Unnamed: 2' (Neutral), etc.
                # First data row (index 0) has labels: Date, Bullish, Neutral, Bearish

                # The data format is:
                # Row 0: Date, Bullish, Neutral, Bearish, ...
                # Row 1: NaN (blank)
                # Row 2+: Actual data

                # Rename columns based on first row content
                first_row = df.iloc[0]
                new_columns = []
                for i, col in enumerate(df.columns):
                    if pd.notna(first_row.iloc[i]):
                        new_columns.append(str(first_row.iloc[i]).strip())
                    else:
                        new_columns.append(col)
                df.columns = new_columns

                # Skip header rows (first 2 rows are labels/blanks)
                df = df.iloc[2:].copy()

                # Parse dates
                date_col = "Date" if "Date" in df.columns else df.columns[0]
                df["Date"] = pd.to_datetime(df[date_col], errors="coerce")
                df = df.dropna(subset=["Date"])

                # The sentiment columns are 'Bullish', 'Neutral', 'Bearish'
                # Also Bull-Bear spread is available
                bullish_col = "Bullish" if "Bullish" in df.columns else None
                neutral_col = "Neutral" if "Neutral" in df.columns else None
                bearish_col = "Bearish" if "Bearish" in df.columns else None

                if bullish_col and bearish_col:
                    for _, row in df.iterrows():
                        if pd.isna(row["Date"]):
                            continue
                        date_str = row["Date"].strftime("%Y-%m-%d")

                        if pd.notna(row.get(bullish_col)):
                            val = float(row[bullish_col])
                            if val > 1:  # Likely percentage, not decimal
                                val = val / 100
                            c.execute("INSERT OR REPLACE INTO observations VALUES (?,?,?)",
                                     ("AAII_Bullish", date_str, val))
                            obs_count += 1

                        if pd.notna(row.get(bearish_col)):
                            val = float(row[bearish_col])
                            if val > 1:
                                val = val / 100
                            c.execute("INSERT OR REPLACE INTO observations VALUES (?,?,?)",
                                     ("AAII_Bearish", date_str, val))
                            obs_count += 1

                        if neutral_col and pd.notna(row.get(neutral_col)):
                            val = float(row[neutral_col])
                            if val > 1:
                                val = val / 100
                            c.execute("INSERT OR REPLACE INTO observations VALUES (?,?,?)",
                                     ("AAII_Neutral", date_str, val))
                            obs_count += 1

                    # Compute Bull-Bear spread
                    c.execute("""SELECT date, value FROM observations
                                WHERE series_id = 'AAII_Bullish' ORDER BY date""")
                    bullish = dict(c.fetchall())

                    c.execute("""SELECT date, value FROM observations
                                WHERE series_id = 'AAII_Bearish' ORDER BY date""")
                    bearish = dict(c.fetchall())

                    for date in bullish:
                        if date in bearish:
                            spread = bullish[date] - bearish[date]
                            c.execute("INSERT OR REPLACE INTO observations VALUES (?,?,?)",
                                     ("AAII_Bull_Bear_Spread", date, spread))
                            obs_count += 1

                    # Update metadata
                    for series_id, title in [
                        ("AAII_Bullish", "AAII % Bullish"),
                        ("AAII_Bearish", "AAII % Bearish"),
                        ("AAII_Neutral", "AAII % Neutral"),
                        ("AAII_Bull_Bear_Spread", "AAII Bull-Bear Spread"),
                    ]:
                        c.execute("""INSERT OR REPLACE INTO series_meta
                                    (series_id, title, source, category, frequency, units, last_updated, last_fetched)
                                    VALUES (?,?,?,?,?,?,?,?)""",
                                 (series_id, title, "AAII", "Sentiment", "Weekly", "Percent",
                                  datetime.now().isoformat(), datetime.now().isoformat()))

                    self.conn.commit()
                    logger.info(f"   AAII sentiment: {obs_count:,} observations")
                    return 4, obs_count

        except Exception as e:
            logger.error(f"AAII fetch error: {e}")

        return 0, 0

    def _fetch_naaim(self) -> Tuple[int, int]:
        """
        Fetch NAAIM Exposure Index.
        Weekly data showing active manager exposure to equities.
        """
        c = self.conn.cursor()
        obs_count = 0

        try:
            logger.info("   Fetching NAAIM exposure...")

            # NAAIM data is available at their website
            # The exact URL and format may change
            naaim_url = "https://www.naaim.org/programs/naaim-exposure-index/"

            # NAAIM provides data in a specific format
            # For now, we'll note this requires manual handling or different approach
            logger.info("   NAAIM requires web scraping or direct data agreement")

            # Placeholder for NAAIM data
            # In production, this would parse their website or use their data feed

        except Exception as e:
            logger.error(f"NAAIM fetch error: {e}")

        return 0, 0


# ==========================================
# PUT/CALL RATIO FETCHER
# ==========================================

class PutCallFetcher:
    """
    Fetch Put/Call ratio data.
    Source: CBOE via various data providers.
    """

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def fetch_all(self) -> Tuple[int, int]:
        """
        Fetch put/call ratio data.
        CBOE equity put/call ratio is the primary metric.
        """
        c = self.conn.cursor()
        obs_count = 0

        try:
            logger.info("   Put/Call ratio requires CBOE data feed...")
            # CBOE data is not freely available via API
            # Options:
            # 1. Manual download from CBOE website
            # 2. Use yfinance for options data (limited)
            # 3. Commercial data feed

            # For now, this is a placeholder
            # In production, integrate with CBOE data or provider like Quandl

        except Exception as e:
            logger.error(f"Put/Call fetch error: {e}")

        return 0, obs_count


# ==========================================
# MASTER MARKET FETCHER
# ==========================================

class MarketDataFetcher:
    """
    Master fetcher coordinating all market data sources.
    """

    def __init__(self, conn: sqlite3.Connection, fred_api_key: str):
        self.conn = conn
        self.yfinance = YFinanceFetcher(conn)
        self.breadth = BreadthFetcher(conn, fred_api_key)
        self.sentiment = SentimentFetcher(conn, fred_api_key)
        self.putcall = PutCallFetcher(conn)

    def fetch_all(self) -> Dict[str, Tuple[int, int]]:
        """
        Fetch all market data.

        Returns:
            Dict mapping source name to (series_count, obs_count)
        """
        results = {}

        logger.info("=== MARKET DATA FETCH ===")

        # S&P 500 price data
        logger.info("--- Yahoo Finance (S&P 500) ---")
        try:
            results["yfinance"] = self.yfinance.fetch_spx()
        except Exception as e:
            logger.error(f"Yahoo Finance error: {e}")
            results["yfinance"] = (0, 0)

        # Breadth data
        logger.info("--- Breadth Data ---")
        try:
            results["breadth"] = self.breadth.fetch_all()
        except Exception as e:
            logger.error(f"Breadth error: {e}")
            results["breadth"] = (0, 0)

        # Sentiment data
        logger.info("--- Sentiment Data ---")
        try:
            results["sentiment"] = self.sentiment.fetch_all()
        except Exception as e:
            logger.error(f"Sentiment error: {e}")
            results["sentiment"] = (0, 0)

        # Put/Call ratio
        logger.info("--- Put/Call Ratio ---")
        try:
            results["putcall"] = self.putcall.fetch_all()
        except Exception as e:
            logger.error(f"Put/Call error: {e}")
            results["putcall"] = (0, 0)

        # Ensure all results are valid tuples
        for key in results:
            if results[key] is None:
                results[key] = (0, 0)

        # Summary
        total_series = sum(r[0] for r in results.values())
        total_obs = sum(r[1] for r in results.values())
        logger.info(f"=== MARKET DATA COMPLETE: {total_series} series, {total_obs:,} obs ===")

        return results
