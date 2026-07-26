#!/usr/bin/env python3
"""
Ingest the cross-asset regime universe into Lighthouse_Master.db
================================================================
Extends ingest_etfs.py to cover the six major asset classes plus
sub-asset-class detail needed for regime-conditioned return work.

All pulls use yfinance auto_adjust=True, so the stored series are
TOTAL-RETURN adjusted closes (dividends and splits reinvested). That
matters for bonds, credit, and REITs where price-only returns are wrong.

series_id convention: '{TICKER}_Close' (matches existing DB rows).

Author: Lighthouse Macro
Date: 2026-07-26
"""

import sqlite3
import warnings
from datetime import datetime

import pandas as pd
import yfinance as yf

warnings.filterwarnings('ignore')

DB_PATH = "/Users/bob/LHM/Data/databases/Lighthouse_Master.db"

# ticker -> (title, category)
UNIVERSE = {
    # --- Six major asset classes (the core) ---
    'AGG':   ('US Aggregate Bond ETF Close',            'ETF'),
    'DBC':   ('Broad Commodities ETF Close',            'ETF'),
    'UUP':   ('US Dollar Index Bullish ETF Close',      'ETF'),
    'BTC-USD': ('Bitcoin Spot Close',                   'Crypto'),
    # --- Sub-asset class: rates / credit ---
    'TIP':   ('TIPS ETF Close',                         'ETF'),
    'EMB':   ('EM USD Sovereign Bond ETF Close',        'ETF'),
    'BIL':   ('1-3 Month T-Bill ETF Close',             'ETF'),
    'MBB':   ('Agency MBS ETF Close',                   'ETF'),
    # --- Sub-asset class: equity regions ---
    'VGK':   ('Europe Equity ETF Close',                'ETF'),
    'EWJ':   ('Japan Equity ETF Close',                 'ETF'),
    'FXI':   ('China Large-Cap ETF Close',              'ETF'),
    'ACWI':  ('MSCI ACWI ETF Close',                    'ETF'),
    # --- Sub-asset class: equity style / factor ---
    'MTUM':  ('US Momentum Factor ETF Close',           'ETF'),
    'QUAL':  ('US Quality Factor ETF Close',            'ETF'),
    'USMV':  ('US Min Volatility ETF Close',            'ETF'),
    'VLUE':  ('US Value Factor ETF Close',              'ETF'),
    'IWF':   ('Russell 1000 Growth ETF Close',          'ETF'),
    'IWD':   ('Russell 1000 Value ETF Close',           'ETF'),
    # --- Sub-asset class: real assets / commodity complex ---
    'VNQ':   ('US REITs ETF Close',                     'ETF'),
    'DBA':   ('Agriculture Commodities ETF Close',      'ETF'),
    'DBE':   ('Energy Commodities ETF Close',           'ETF'),
    'CPER':  ('Copper ETF Close',                       'ETF'),
    'XME':   ('Metals and Mining ETF Close',            'ETF'),
    # --- Sector completeness (XLC / XLRE not in ingest_etfs) ---
    'XLC':   ('Communication Services ETF Close',       'ETF'),
    'XLRE':  ('Real Estate Sector ETF Close',           'ETF'),
}


def ingest(start='1990-01-01'):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    stamp = datetime.now().isoformat()
    total = 0

    for ticker, (title, category) in UNIVERSE.items():
        sid = f"{ticker.replace('-USD', '')}_Close"
        print(f"Pulling {ticker:8s} -> {sid:14s}", end=' ')
        try:
            df = yf.download(ticker, start=start, progress=False, auto_adjust=True)
            if df is None or df.empty:
                print("[empty]")
                continue
            if isinstance(df.columns, pd.MultiIndex):
                df = df.droplevel(1, axis=1)
            close = df['Close'].dropna()
            close.index = pd.to_datetime(close.index).tz_localize(None)

            rows = [(d.strftime('%Y-%m-%d'), sid, float(v)) for d, v in close.items()]
            cur.executemany(
                "INSERT OR REPLACE INTO observations (date, series_id, value) VALUES (?,?,?)",
                rows,
            )
            cur.execute(
                """INSERT OR REPLACE INTO series_meta
                   (series_id, title, source, category, frequency, last_updated)
                   VALUES (?,?,?,?,?,?)""",
                (sid, title, 'Yahoo', category, 'Daily', stamp),
            )
            conn.commit()
            total += len(rows)
            print(f"{len(rows):>6,} obs  {close.index[0].date()} -> {close.index[-1].date()}")
        except Exception as exc:  # noqa: BLE001
            print(f"[FAIL] {exc}")

    conn.close()
    print(f"\nDone. {total:,} observations written.")


if __name__ == '__main__':
    ingest()
