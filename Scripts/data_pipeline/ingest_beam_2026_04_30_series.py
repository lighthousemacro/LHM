"""
Ad-hoc ingestion: 3 series needed for the Apr 30 2026 Beam (AI is fragmenting
the cycle) that weren't yet in Lighthouse_Master.db.

After this runs, the series live in the DB with full FRED history and the Beam
script can pull them like any other indicator.

Series:
  - A191RL1Q225SBEA  Real GDP, % chg from prev quarter, SAAR (BEA)  -> covers Q1 2026 advance
  - PCU334413334413  PPI: Semiconductor and Related Device Manufacturing  (BLS via FRED)
  - A34SNO           Manufacturers' New Orders: Computer & Electronic Products (Census M3)
  - A34SVS           Manufacturers' Inventories: Computer & Electronic Products (Census M3)
  - A34STI           Computer & Electronic Products: Total Inventories  (Census M3, alt)

Idempotent: rerun any time. Uses INSERT OR REPLACE on observations and series_meta.
"""
import os
import sys
import sqlite3
import time
from datetime import datetime
import requests

DB_PATH = '/Users/bob/LHM/Data/databases/Lighthouse_Master.db'
FRED_API_KEY = os.getenv('FRED_API_KEY')
if not FRED_API_KEY:
    raise SystemExit('FRED_API_KEY env var not set. Source ~/.zshrc or export it before running.')
FRED_BASE = 'https://api.stlouisfed.org/fred/series'

# Series spec: (FRED id, friendly title, source label, category, frequency, units)
SERIES = [
    ('A191RL1Q225SBEA',
     'Real Gross Domestic Product, Percent Change from Preceding Period (SAAR)',
     'BEA via FRED', 'macro_growth', 'Quarterly', 'Percent'),
    ('PCU334413334413',
     'PPI: Semiconductor and Related Device Manufacturing',
     'BLS via FRED', 'macro_prices', 'Monthly', 'Index Dec 2003=100'),
    ('AMNMNO',  # all manufacturing new orders (sanity reference)
     "Manufacturers' New Orders: Total Manufacturing",
     'Census M3 via FRED', 'macro_business', 'Monthly', 'Mil. of $'),
    ('A34SNO',
     "Manufacturers' New Orders: Computer & Electronic Products",
     'Census M3 via FRED', 'macro_business', 'Monthly', 'Mil. of $'),
    ('A34SVS',
     "Manufacturers' Value of Shipments: Computer & Electronic Products",
     'Census M3 via FRED', 'macro_business', 'Monthly', 'Mil. of $'),
    ('A34STI',
     "Manufacturers' Total Inventories: Computer & Electronic Products",
     'Census M3 via FRED', 'macro_business', 'Monthly', 'Mil. of $'),
]


def fetch_fred(series_id, api_key=FRED_API_KEY):
    """Pull all observations from FRED."""
    url = f'{FRED_BASE}/observations'
    params = {
        'series_id': series_id,
        'api_key': api_key,
        'file_type': 'json',
    }
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    return r.json().get('observations', [])


def fetch_fred_meta(series_id, api_key=FRED_API_KEY):
    """Pull series metadata from FRED (frequency, units, last_updated, title)."""
    url = FRED_BASE
    params = {
        'series_id': series_id,
        'api_key': api_key,
        'file_type': 'json',
    }
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    rows = r.json().get('seriess', [])
    return rows[0] if rows else {}


def upsert(con, series_id, title, source, category, frequency, units):
    print(f'\n=== {series_id} ===')
    try:
        meta = fetch_fred_meta(series_id)
    except requests.HTTPError as e:
        print(f'  meta fetch failed: {e}')
        meta = {}
    obs = fetch_fred(series_id)
    if not obs:
        print(f'  no observations returned, skipping')
        return 0

    rows = []
    for o in obs:
        v = o.get('value')
        if v in (None, '.', ''):
            continue
        try:
            val = float(v)
        except ValueError:
            continue
        rows.append((series_id, o['date'], val))

    if not rows:
        print(f'  zero valid observations, skipping')
        return 0

    cur = con.cursor()
    cur.executemany(
        'INSERT OR REPLACE INTO observations (series_id, date, value) VALUES (?, ?, ?)',
        rows,
    )
    last_date = max(r[1] for r in rows)
    last_updated = meta.get('last_updated', datetime.utcnow().isoformat())
    last_fetched = datetime.utcnow().isoformat()
    cur.execute('''
        INSERT OR REPLACE INTO series_meta
            (series_id, title, source, category, frequency, units,
             last_updated, last_fetched, data_quality, last_value_date, obs_count)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (series_id, title, source, category, frequency, units,
          last_updated, last_fetched, 'good', last_date, len(rows)))
    con.commit()
    print(f'  inserted {len(rows):,} obs (range: {min(r[1] for r in rows)} -> {last_date})')
    return len(rows)


def main():
    if not FRED_API_KEY:
        print('FRED_API_KEY not set, aborting')
        sys.exit(1)
    con = sqlite3.connect(DB_PATH)
    total = 0
    for spec in SERIES:
        try:
            total += upsert(con, *spec)
            time.sleep(0.4)  # be polite to FRED
        except Exception as e:
            print(f'  ERROR on {spec[0]}: {e}')
    con.close()
    print(f'\nDone. Total observations inserted: {total:,}')


if __name__ == '__main__':
    main()
