#!/usr/bin/env python3
"""
Ingest equity ETF daily closes into Lighthouse_Master.db
==========================================================
Pulls SPY, TLT, IEF, SHY, XLY, XLP, XLF, XLE, XLU, XLI, XLV, XLB, XLK,
XHB, ITB, IWM, QQQ, EEM, EFA, GLD, SLV, HYG, LQD, GDX from yfinance.

Stores as observations rows with series_id = '{TICKER}_Close' (consistent
with existing SPX_Close convention).

Adds entries to series_meta if not already present.

Author: Lighthouse Macro
Date: 2026-04-29
"""

import sqlite3
import warnings
from datetime import datetime
from pathlib import Path

import pandas as pd
import yfinance as yf

warnings.filterwarnings('ignore')

DB_PATH = "/Users/bob/LHM/Data/databases/Lighthouse_Master.db"

ETFS = {
    # Broad equity / bond
    'SPY':  ('S&P 500 ETF Close',                'Yahoo'),
    'TLT':  ('20+ Year Treasury Bond ETF Close', 'Yahoo'),
    'IEF':  ('7-10 Year Treasury Bond ETF Close','Yahoo'),
    'SHY':  ('1-3 Year Treasury Bond ETF Close', 'Yahoo'),
    'IWM':  ('Russell 2000 ETF Close',           'Yahoo'),
    'QQQ':  ('Nasdaq-100 ETF Close',             'Yahoo'),
    'EEM':  ('Emerging Markets ETF Close',       'Yahoo'),
    'EFA':  ('Developed Markets ex-US ETF Close','Yahoo'),
    # Sectors
    'XLY':  ('Consumer Discretionary ETF Close', 'Yahoo'),
    'XLP':  ('Consumer Staples ETF Close',       'Yahoo'),
    'XLF':  ('Financials ETF Close',             'Yahoo'),
    'XLE':  ('Energy ETF Close',                 'Yahoo'),
    'XLU':  ('Utilities ETF Close',              'Yahoo'),
    'XLI':  ('Industrials ETF Close',            'Yahoo'),
    'XLV':  ('Health Care ETF Close',            'Yahoo'),
    'XLB':  ('Materials ETF Close',              'Yahoo'),
    'XLK':  ('Technology ETF Close',             'Yahoo'),
    # Themes
    'XHB':  ('Homebuilders ETF Close',           'Yahoo'),
    'ITB':  ('Home Construction ETF Close',      'Yahoo'),
    'GDX':  ('Gold Miners ETF Close',            'Yahoo'),
    # Commodities / metals
    'GLD':  ('Gold ETF Close',                   'Yahoo'),
    'SLV':  ('Silver ETF Close',                 'Yahoo'),
    # Credit
    'HYG':  ('High-Yield Corp Bond ETF Close',   'Yahoo'),
    'LQD':  ('Investment-Grade Corp Bond ETF Close','Yahoo'),
}


def ingest():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    today = datetime.now().isoformat()

    for ticker, (title, source) in ETFS.items():
        sid = f"{ticker}_Close"
        print(f"Pulling {ticker}...", end=' ')
        try:
            df = yf.download(ticker, start='2000-01-01', progress=False, auto_adjust=True)
            if df.empty:
                print("[empty]")
                continue
            if isinstance(df.columns, pd.MultiIndex):
                df = df.droplevel(1, axis=1)
            close = df['Close'].dropna()
            close.index = pd.to_datetime(close.index).tz_localize(None)

            rows = [(d.strftime('%Y-%m-%d'), sid, float(v))
                    for d, v in close.items() if v == v]

            cur.executemany(
                "INSERT OR REPLACE INTO observations (date, series_id, value) "
                "VALUES (?, ?, ?)", rows
            )

            # series_meta upsert
            existing = cur.execute(
                "SELECT 1 FROM series_meta WHERE series_id = ?", (sid,)
            ).fetchone()
            if existing:
                cur.execute(
                    "UPDATE series_meta SET title = ?, source = ?, frequency = ?, "
                    "last_updated = ?, last_fetched = ?, data_quality = ?, "
                    "last_value_date = ?, obs_count = ? WHERE series_id = ?",
                    (title, source, 'Daily', today, today, 'good',
                     close.index.max().strftime('%Y-%m-%d'),
                     len(close), sid)
                )
            else:
                cur.execute(
                    "INSERT INTO series_meta (series_id, title, source, category, "
                    "frequency, units, last_updated, last_fetched, data_quality, "
                    "last_value_date, obs_count) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (sid, title, source, 'ETF', 'Daily', 'USD',
                     today, today, 'good',
                     close.index.max().strftime('%Y-%m-%d'),
                     len(close))
                )

            conn.commit()
            print(f"{len(close)} obs, {close.index.min().date()} to {close.index.max().date()}")
        except Exception as e:
            print(f"[ERROR] {e}")

    conn.close()
    print("Done.")


if __name__ == "__main__":
    ingest()
