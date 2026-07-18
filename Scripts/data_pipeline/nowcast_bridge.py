"""LHM Nowcast Bridge (Layer 2)
==============================
Turns the design in nowcast_map.yaml into DAILY-moving inputs. Between official releases, a monthly/
quarterly indicator input is projected forward each day from a high-frequency daily proxy via a rolling
regression, so the composites that consume it (GCI, LFI, ...) move every day instead of stepping only on
release days. Actual prints are always kept; only the post-last-release gap is nowcast.

Writes a daily series <RAW>_NOWCAST into observations for each bridged input, plus a coverage report.
Run:  python3 nowcast_bridge.py [--write]   (dry-run without --write)

Method (proxy_regression): aggregate the daily proxy to the raw series' cadence, fit a rolling OLS of the
raw series on the proxy over the trailing window, and apply the latest fit to the daily proxy to nowcast
the raw level forward from its last actual release. proxy_carry = carry last actual (direction flag only).
external = use the named external nowcast series directly.
"""
import sys, os, re, sqlite3, datetime
import numpy as np, pandas as pd
try:
    import yaml
except ImportError:
    print("pyyaml required"); sys.exit(1)

DB = "/Users/bob/LHM/Data/databases/Lighthouse_Master.db"
MAP = "/Users/bob/LHM/Scripts/data_pipeline/lighthouse/nowcast_map.yaml"
WIN = 60  # rolling regression window (months)

def load_series(c, sid):
    df = pd.read_sql_query("SELECT date,value FROM observations WHERE series_id=? ORDER BY date", c, params=(sid,))
    if df.empty: return None
    df['date'] = pd.to_datetime(df['date']); return df.set_index('date')['value'].dropna()

def first_ticker_in_db(c, text):
    """Pull the first candidate ticker from a proxy_daily text field that actually exists in the DB."""
    for t in re.findall(r'\b[A-Z][A-Z0-9_]{2,}\b', str(text or '')):
        if t in ('FRED','ICE','YoY','MA','US'): continue
        if c.execute("SELECT 1 FROM observations WHERE series_id=? LIMIT 1", (t,)).fetchone():
            return t
    return None

def nowcast_proxy_regression(raw, proxy):
    """Return a daily nowcast series for `raw` (monthly) driven by `proxy` (daily),
    filling only dates after raw's last actual print up to proxy's last date."""
    prox_m = proxy.resample('MS').mean()
    r = raw.copy(); r.index = r.index.to_period('M').to_timestamp()
    df = pd.concat([r.rename('r'), prox_m.rename('p')], axis=1).dropna()
    if len(df) < 24: return None
    # rolling OLS r ~ a + b*p on trailing WIN months, take latest coefficients
    d = df.tail(WIN)
    b, a = np.polyfit(d['p'].values, d['r'].values, 1)
    last_release = raw.index.max()
    proxy_gap = proxy[proxy.index > last_release]
    if proxy_gap.empty: return None
    nowcast = a + b * proxy_gap  # daily nowcast of the raw level
    # blend: anchor to the actual last print so we don't jump on day 1
    anchor_gap = (a + b * prox_m.get(last_release.to_period('M').to_timestamp(), proxy_gap.iloc[0]))
    nowcast = nowcast + (raw.loc[last_release] - anchor_gap)  # level-match at the seam
    return nowcast.dropna()

def main(write=False):
    c = sqlite3.connect(DB)
    m = yaml.safe_load(open(MAP))
    now = datetime.datetime.now().isoformat()
    built, skipped = [], []
    for row in m['inputs']:
        strat = row.get('nowcast_strategy'); raw_id = row.get('raw_series_id')
        col = row['horizon_column']
        if strat in ('none', None) or not raw_id: continue
        raw = load_series(c, raw_id)
        if raw is None: skipped.append((col, f"raw {raw_id} not in DB")); continue
        nc = None
        if strat in ('proxy_regression', 'proxy_carry'):
            prox_id = first_ticker_in_db(c, row.get('proxy_daily'))
            if not prox_id: skipped.append((col, f"no usable proxy in DB for {row.get('proxy_daily')}")); continue
            proxy = load_series(c, prox_id)
            nc = nowcast_proxy_regression(raw, proxy)
            if nc is None or nc.empty: skipped.append((col, f"proxy {prox_id}: no gap or insufficient overlap")); continue
            meta_src = f"nowcast:{prox_id}"
        elif strat == 'external':
            ext_id = first_ticker_in_db(c, row.get('external_nowcast')) or first_ticker_in_db(c, row.get('proxy_daily'))
            if not ext_id: skipped.append((col, "no external series in DB")); continue
            ext = load_series(c, ext_id)
            nc = ext[ext.index > raw.index.max()]
            if nc.empty: skipped.append((col, f"external {ext_id}: no gap")); continue
            meta_src = f"external:{ext_id}"
        else:
            continue
        # Key the nowcast by the horizon_column (shared join key with horizon_dataset_builder),
        # not raw_series_id — the builder uses different source IDs (BLS JTS1000QUR vs FRED JTSQUR).
        out_id = f"{col}_NOWCAST"
        gap_days = (nc.index.max() - nc.index.min()).days
        built.append((col, raw_id, out_id, len(nc), gap_days, meta_src))
        if write:
            rows = [(out_id, d.strftime('%Y-%m-%d'), float(v)) for d, v in nc.items()]
            c.executemany("INSERT OR REPLACE INTO observations(series_id,date,value) VALUES(?,?,?)", rows)
            c.execute("""INSERT OR REPLACE INTO series_meta
              (series_id,title,source,category,frequency,units,last_updated,last_fetched,data_quality,last_value_date,obs_count)
              VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
              (out_id, f"{col} (daily nowcast)", meta_src, "Nowcast", "Daily", "nowcast",
               now, now, "nowcast", rows[-1][1], len(rows)))
    if write: c.commit()
    print(f"{'WROTE' if write else 'DRY-RUN'} nowcast bridge — built {len(built)}, skipped {len(skipped)}\n")
    print("BUILT (daily nowcast fills the gap since last release):")
    for col, raw, out, n, gap, src in built:
        print(f"  {col[:28]:28} <- {src:22} | {n} gap-days ({gap}d), -> {out}")
    print("\nSKIPPED (need proxy ingestion or fix):")
    for col, why in skipped:
        print(f"  {col[:28]:28} {why}")
    return built, skipped

if __name__ == "__main__":
    main(write="--write" in sys.argv)
