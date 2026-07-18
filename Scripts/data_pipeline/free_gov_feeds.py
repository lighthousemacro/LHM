"""Free government / central-bank data feeds — direct-source pulls that aren't on FRED.

These are all FREE public data we should always carry. FRED covers most gov series, but some live only
on the source site (NY Fed GSCPI, some OFR tables, regional-Fed nowcasts). This module pulls those
directly and upserts into Lighthouse_Master.db, so they refresh on the daily pipeline like everything else.

Run standalone:   python3 free_gov_feeds.py
Import in pipeline:  from free_gov_feeds import run_free_gov_feeds; run_free_gov_feeds(db_path)

Add a feed = write a fetch_*() that returns (series_id, meta_dict, [(date,value),...]) and add it to FEEDS.
"""
import sqlite3, datetime, ssl, urllib.request, io

_UA = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/126.0 Safari/537.36'}
_CTX = ssl.create_default_context(); _CTX.check_hostname = False; _CTX.verify_mode = ssl.CERT_NONE
DB_DEFAULT = '/Users/bob/LHM/Data/databases/Lighthouse_Master.db'

def _get(url, timeout=40):
    return urllib.request.urlopen(urllib.request.Request(url, headers=_UA), context=_CTX, timeout=timeout).read()

# ---- FEED: NY Fed Global Supply Chain Pressure Index ----
def fetch_gscpi():
    import pandas as pd
    raw = _get("https://www.newyorkfed.org/medialibrary/research/interactives/gscpi/downloads/gscpi_data.xlsx")
    df = pd.read_excel(io.BytesIO(raw), sheet_name='GSCPI Monthly Data')[['Date', 'GSCPI']].dropna()
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce'); df = df.dropna(subset=['Date'])
    rows = [(d.strftime('%Y-%m-%d'), float(v)) for d, v in zip(df['Date'], df['GSCPI'])]
    meta = dict(title='Global Supply Chain Pressure Index', source='NY Fed', category='Trade',
                frequency='Monthly', units='std dev from mean')
    return 'GSCPI', meta, rows

# Registry of active free-gov feeds. Add more fetchers here (each returns (sid, meta, rows)).
FEEDS = [fetch_gscpi]

# ---- Roadmap / audit notes (2026-07-18) ----
# RESOLVED (no direct-pull needed — already covered elsewhere):
#   - GDPNow: on FRED as GDPNOW + PCECONTRIBNOW/EQUIPCONTRIBNOW/CHNGNETEXPORTSCONTRIBNOW/CHNGNETINVENTCONTRIBNOW.
#     Added to FRED_CURATED 2026-07-18 (the 10.8MB frbatlanta xlsx is model internals — do NOT parse it).
#   - OFR Financial Stress Index (headline + 5 subindices + 3 regional): already in DB via the OFR fetcher, fresh.
#   - Atlanta Fed Wage Growth Tracker switcher/stayer: already in DB via FRED (FRBATLWGT12MMUMHWGJSW/JST).
#   - TreasuryDirect: repaired + wired as the TREASURY pipeline source (was dark; not stale-by-bug).
# DEAD AT SOURCE (no fix possible): OFR NYPD primary-dealer repo (NYPD-PD_RP_TOT-A etc.) — OFR discontinued
#   these ~Dec 2021; their own API returns None past that. Historical only.
# STILL TO ADD (clean direct pulls, when wanted): NY Fed SCE (consumer expectations), more OFR short-term
#   funding monitor cuts, regional Fed manufacturing surveys not on FRED.

def run_free_gov_feeds(db_path=DB_DEFAULT, verbose=True):
    c = sqlite3.connect(db_path); now = datetime.datetime.now().isoformat(); done = []
    for fetch in FEEDS:
        try:
            sid, meta, rows = fetch()
            if not rows: raise ValueError("no rows")
            c.executemany("INSERT OR REPLACE INTO observations(series_id,date,value) VALUES(?,?,?)",
                          [(sid, d, v) for d, v in rows])
            lvd = rows[-1][0]
            c.execute("""INSERT OR REPLACE INTO series_meta
              (series_id,title,source,category,frequency,units,last_updated,last_fetched,data_quality,last_value_date,obs_count)
              VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
              (sid, meta['title'], meta['source'], meta.get('category', ''), meta.get('frequency', ''),
               meta.get('units', ''), now, now, 'ok', lvd, len(rows)))
            done.append((sid, len(rows), lvd))
            if verbose: print(f"  {sid}: {len(rows)} obs, latest {lvd}")
        except Exception as e:
            if verbose: print(f"  {fetch.__name__} FAILED: {type(e).__name__} {e}")
    c.commit(); return done

if __name__ == '__main__':
    print("Running free gov feeds...")
    run_free_gov_feeds()
