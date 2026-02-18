"""
LIGHTHOUSE MACRO - TRADINGVIEW DATA FETCHER
============================================
Fetches ECONOMICS: series from TradingView via websocket.
No API key required. Uses TradingView's public websocket endpoint.

Series stored in master DB as TV_{SYMBOL}:
  - TV_USHMI:     NAHB Housing Market Index (monthly, 1985+)
  - TV_USPIND:    MBA Purchase Application Index (weekly)
  - TV_USMRI:     MBA Refinance Index (weekly)
  - TV_USPHSIYY:  Pending Home Sales YoY% (monthly)
  - TV_USPHSIMM:  Pending Home Sales MoM% (monthly)
  - TV_USCONSTS:  Construction Spending (monthly)
  - TV_USPRR:     Price-to-Rent Ratio (quarterly)
  - TV_USAMS:     Average Mortgage Size (quarterly)
  - TV_USEHS:     Existing Home Sales SAAR (monthly)
  - TV_USMAPL:    MBA Mortgage Applications Composite (weekly)
  - TV_USMMI:     MBA Mortgage Market Index (weekly)
  - TV_USMOR:     Mortgage Originations (quarterly)
"""

import json
import random
import string
import struct
import sqlite3
import logging
import time
from datetime import datetime, timezone
from typing import Tuple, Optional

logger = logging.getLogger(__name__)

# ==========================================
# CONFIGURATION
# ==========================================

TV_WS_URL = "wss://data.tradingview.com/socket.io/websocket"

# Series to fetch: TV ticker -> (DB series_id, title, frequency, units, category)
TV_SERIES = {
    "ECONOMICS:USHMI": ("TV_USHMI", "NAHB Housing Market Index", "Monthly", "Index", "Housing"),
    "ECONOMICS:USPIND": ("TV_USPIND", "MBA Purchase Application Index", "Weekly", "Index", "Housing"),
    "ECONOMICS:USMRI": ("TV_USMRI", "MBA Refinance Index", "Weekly", "Index", "Housing"),
    "ECONOMICS:USPHSIYY": ("TV_USPHSIYY", "Pending Home Sales YoY%", "Monthly", "Percent", "Housing"),
    "ECONOMICS:USPHSIMM": ("TV_USPHSIMM", "Pending Home Sales MoM%", "Monthly", "Percent", "Housing"),
    "ECONOMICS:USCONSTS": ("TV_USCONSTS", "Construction Spending", "Monthly", "Millions USD", "Housing"),
    "ECONOMICS:USPRR": ("TV_USPRR", "Price-to-Rent Ratio", "Quarterly", "Ratio", "Housing"),
    "ECONOMICS:USAMS": ("TV_USAMS", "Average Mortgage Size", "Quarterly", "USD", "Housing"),
    "ECONOMICS:USEHS": ("TV_USEHS", "Existing Home Sales SAAR", "Monthly", "Units", "Housing"),
    "ECONOMICS:USMAPL": ("TV_USMAPL", "MBA Mortgage Applications Composite", "Weekly", "Index", "Housing"),
    "ECONOMICS:USMMI": ("TV_USMMI", "MBA Mortgage Market Index", "Weekly", "Index", "Housing"),
    "ECONOMICS:USMOR": ("TV_USMOR", "Mortgage Originations", "Quarterly", "USD", "Housing"),
    # Business Pillar - ISM Manufacturing
    "ECONOMICS:USISMMP": ("TV_USISMMP", "ISM Manufacturing PMI", "Monthly", "Index", "Business"),
    "ECONOMICS:USMNO": ("TV_USMNO", "ISM Manufacturing New Orders", "Monthly", "Index", "Business"),
    "ECONOMICS:USMEMP": ("TV_USMEMP", "ISM Manufacturing Employment", "Monthly", "Index", "Business"),
    "ECONOMICS:USMPR": ("TV_USMPR", "ISM Manufacturing Prices Paid", "Monthly", "Index", "Business"),
    # Business Pillar - ISM Services/Non-Manufacturing
    "ECONOMICS:USBCOI": ("TV_USBCOI", "ISM Services PMI", "Monthly", "Index", "Business"),
    "ECONOMICS:USNMBA": ("TV_USNMBA", "ISM Services Business Activity", "Monthly", "Index", "Business"),
    "ECONOMICS:USNMNO": ("TV_USNMNO", "ISM Services New Orders", "Monthly", "Index", "Business"),
    "ECONOMICS:USNMEMP": ("TV_USNMEMP", "ISM Services Employment", "Monthly", "Index", "Business"),
    "ECONOMICS:USNMPR": ("TV_USNMPR", "ISM Services Prices", "Monthly", "Index", "Business"),
    # Business Pillar - Regional Fed Surveys (additional)
    "ECONOMICS:USRFMI": ("TV_USRFMI", "Richmond Fed Manufacturing Index", "Monthly", "Index", "Business"),
    "ECONOMICS:USKFMI": ("TV_USKFMI", "Kansas City Fed Manufacturing Index", "Monthly", "Index", "Business"),
    # Business Pillar - Leading/Confidence
    "ECONOMICS:USLEI": ("TV_USLEI", "Conference Board Leading Economic Index", "Monthly", "Index", "Business"),
    "ECONOMICS:USBOI": ("TV_USBOI", "OECD Business Outlook Index", "Monthly", "Index", "Business"),
    "ECONOMICS:USFO": ("TV_USFO", "Factory Orders MoM", "Monthly", "Percent", "Business"),
}


def _gen_session() -> str:
    """Generate a random session ID like TradingView client."""
    chars = string.ascii_lowercase
    return "qs_" + "".join(random.choice(chars) for _ in range(12))


def _encode_msg(msg: str) -> str:
    """Encode message in TradingView's ~m~{length}~m~ framing."""
    return f"~m~{len(msg)}~m~{msg}"


def _parse_messages(raw: str) -> list:
    """Parse TradingView websocket frames from raw data."""
    messages = []
    i = 0
    while i < len(raw):
        if raw[i:i+3] == "~m~":
            end_marker = raw.index("~m~", i + 3)
            length = int(raw[i+3:end_marker])
            payload_start = end_marker + 3
            payload = raw[payload_start:payload_start + length]
            messages.append(payload)
            i = payload_start + length
        else:
            i += 1
    return messages


def _fetch_series(tv_symbol: str, timeout: int = 15) -> Optional[list]:
    """
    Fetch historical data for a single ECONOMICS: symbol from TradingView.

    Returns list of (date_str, value) tuples, or None on failure.
    """
    try:
        import websocket
    except ImportError:
        logger.error("  websocket-client not installed. Run: pip install websocket-client")
        return None

    session = _gen_session()
    results = []

    try:
        ws = websocket.create_connection(
            TV_WS_URL,
            origin="https://www.tradingview.com",
            timeout=timeout,
        )

        # Send session setup
        ws.send(_encode_msg(json.dumps({"m": "set_auth_token", "p": ["unauthorized_user_token"]})))
        ws.send(_encode_msg(json.dumps({"m": "quote_create_session", "p": [session]})))
        ws.send(_encode_msg(json.dumps({"m": "quote_set_fields", "p": [session, "short_name", "description", "exchange"]})))
        ws.send(_encode_msg(json.dumps({"m": "quote_add_symbols", "p": [session, tv_symbol]})))

        # Request historical data
        ws.send(_encode_msg(json.dumps({
            "m": "quote_fast_symbols",
            "p": [session, tv_symbol]
        })))

        # Create a chart session for actual history
        chart_session = "cs_" + "".join(random.choice(string.ascii_lowercase) for _ in range(12))
        ws.send(_encode_msg(json.dumps({"m": "chart_create_session", "p": [chart_session, ""]})))
        ws.send(_encode_msg(json.dumps({
            "m": "resolve_symbol",
            "p": [chart_session, "sds_sym_1", f"={{\"symbol\":\"{tv_symbol}\",\"adjustment\":\"splits\"}}"]
        })))
        ws.send(_encode_msg(json.dumps({
            "m": "create_series",
            "p": [chart_session, "sds_1", "s1", "sds_sym_1", "1M", 5000, ""]
        })))

        # Collect responses
        data_received = False
        start = time.time()
        while time.time() - start < timeout:
            try:
                raw = ws.recv()
            except websocket.WebSocketTimeoutException:
                break

            if not raw:
                continue

            # Handle heartbeat
            if "~h~" in raw:
                # Echo heartbeat back
                for msg in _parse_messages(raw):
                    if msg.startswith("~h~"):
                        ws.send(_encode_msg(msg))
                continue

            for msg in _parse_messages(raw):
                if not msg.startswith("{"):
                    continue
                try:
                    data = json.loads(msg)
                except json.JSONDecodeError:
                    continue

                if data.get("m") == "timescale_update":
                    # Extract OHLCV bars
                    params = data.get("p", [])
                    if len(params) >= 2:
                        for key, val in params[1].items():
                            if isinstance(val, dict) and "s" in val:
                                for bar in val["s"]:
                                    v = bar.get("v", [])
                                    if len(v) >= 5:
                                        ts = v[0]  # Unix timestamp
                                        close = v[4]  # Close price
                                        dt = datetime.fromtimestamp(ts, tz=timezone.utc)
                                        date_str = dt.strftime("%Y-%m-01")
                                        results.append((date_str, close))
                                data_received = True

                elif data.get("m") == "series_completed":
                    data_received = True

            if data_received and results:
                break

        ws.close()

    except Exception as e:
        logger.error(f"  WebSocket error for {tv_symbol}: {e}")
        return None

    return results if results else None


class TradingViewFetcher:
    """Fetch economic data series from TradingView."""

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def _store_series(self, series_id: str, title: str, frequency: str,
                      units: str, category: str, data: list) -> Tuple[int, int]:
        """Store fetched data in the master database."""
        c = self.conn.cursor()

        # Deduplicate by date (keep latest value for each date)
        date_map = {}
        for date_str, value in data:
            date_map[date_str] = value

        obs_list = [(series_id, d, v) for d, v in sorted(date_map.items())]

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
                "TradingView",
                category,
                frequency,
                units,
                datetime.now().isoformat(),
                datetime.now().isoformat(),
            ),
        )

        self.conn.commit()
        return 1, len(obs_list)

    def fetch_all(self) -> Tuple[int, int]:
        """Fetch all configured TradingView series."""
        total_series = 0
        total_obs = 0

        for tv_symbol, (series_id, title, freq, units, cat) in TV_SERIES.items():
            logger.info(f"  Fetching {tv_symbol} -> {series_id}...")
            print(f"  Fetching {tv_symbol}...")

            data = _fetch_series(tv_symbol)
            if data:
                s, o = self._store_series(series_id, title, freq, units, cat, data)
                total_series += s
                total_obs += o
                logger.info(f"    {series_id}: {o} observations")
                print(f"    {series_id}: {o} observations")
            else:
                logger.warning(f"    {series_id}: No data returned")
                print(f"    {series_id}: No data returned")

            # Brief pause between requests
            time.sleep(1)

        return total_series, total_obs
