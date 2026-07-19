"""LHM Growth Nowcast — proprietary multi-proxy model
=====================================================
Our own daily activity nowcast: a basket of high-frequency market/credit proxies combined with
fitted (elastic-net) weights to nowcast Industrial Production YoY between the monthly prints.
The weight vector is the proprietary combination. Writes Industrial_Production_NOWCAST (level) so
horizon_dataset_builder splices it into GCI -> GCI moves daily.

Run:  python3 growth_nowcast.py [--write]
"""
import sys, sqlite3, datetime
import numpy as np, pandas as pd
from sklearn.linear_model import ElasticNetCV
from sklearn.preprocessing import StandardScaler

DB = "/Users/bob/LHM/Data/databases/Lighthouse_Master.db"
TARGET = "INDPRO"            # raw level
TARGET_COL = "Industrial_Production"   # horizon_dataset name

# proxy basket: series_id -> transform ('yoy' vs ~1y ago, 'level', or 'ratio:num/den')
PROXIES = {
    "COPPER_Close": "yoy", "DCOILWTICO": "yoy", "SMH_Close": "yoy", "IYT_Close": "yoy",
    "HYG_Close": "yoy", "NFCI": "level", "ICSA": "level", "T10Y2Y": "level",
    "DTWEXBGS": "yoy", "XLI_XLP": "ratio:XLI_Close/XLP_Close",
}

def load(c, sid):
    df = pd.read_sql_query("SELECT date,value FROM observations WHERE series_id=? ORDER BY date", c, params=(sid,))
    if df.empty: return None
    df['date'] = pd.to_datetime(df['date']); return df.set_index('date')['value'].dropna()

def proxy_daily(c, name, spec):
    if spec.startswith("ratio:"):
        num, den = spec[6:].split("/")
        a, b = load(c, num), load(c, den)
        s = (a / b).dropna(); return s.pct_change(252) * 100     # RS momentum
    s = load(c, name)
    if s is None: return None
    if spec == "yoy": return s.pct_change(252) * 100
    return s  # level

def main(write=False):
    c = sqlite3.connect(DB)
    tgt = load(c, TARGET); tgt_yoy = (tgt.pct_change(12) * 100).dropna()
    # daily proxy frame
    P = {}
    for name, spec in PROXIES.items():
        s = proxy_daily(c, name, spec)
        if s is not None: P[name if not spec.startswith("ratio") else "XLI_XLP"] = s
    Pdf = pd.DataFrame(P).sort_index().ffill()
    # monthly design matrix aligned to INDPRO YoY prints
    Pm = Pdf.resample("MS").mean()
    d = pd.concat([tgt_yoy.rename("y"), Pm], axis=1).dropna()
    d = d[d.index >= "2004-01-01"]
    X, y = d.drop(columns="y").values, d["y"].values
    sc = StandardScaler().fit(X)
    model = ElasticNetCV(l1_ratio=[.1,.5,.7,.9,.95,1], cv=5, max_iter=5000, random_state=0).fit(sc.transform(X), y)
    insample_r = np.corrcoef(model.predict(sc.transform(X)), y)[0,1]
    # walk-forward OOS: expanding window, predict next
    preds, acts = [], []
    for i in range(48, len(d)):
        Xtr, ytr = sc.transform(X[:i]), y[:i]
        m = ElasticNetCV(l1_ratio=[.5,.9,1], cv=4, max_iter=3000).fit(Xtr, ytr)
        preds.append(m.predict(sc.transform(X[i:i+1]))[0]); acts.append(y[i])
    oos_r = np.corrcoef(preds, acts)[0,1]
    # proprietary weights (on standardized proxies)
    weights = sorted(zip(d.drop(columns="y").columns, model.coef_), key=lambda x: -abs(x[1]))
    print(f"LHM Growth Nowcast — INDPRO YoY | in-sample r={insample_r:.2f}  walk-forward OOS r={oos_r:.2f}  (n={len(d)})")
    print("proprietary proxy weights (standardized):")
    for nm, w in weights: print(f"    {nm:14} {w:+.3f}")
    # daily nowcast of INDPRO YoY, then -> level, fill gap after last print
    Xdaily = sc.transform(Pdf.dropna().values)
    yhat = pd.Series(model.predict(Xdaily), index=Pdf.dropna().index)
    last_rel = tgt.index.max()
    gap = yhat[yhat.index > last_rel]
    if gap.empty: print("no gap to fill"); return
    lvl = pd.Series(index=gap.index, dtype=float)
    for dt, yy in gap.items():
        base_dt = dt - pd.DateOffset(years=1)
        base = tgt.reindex([base_dt], method="nearest").iloc[0]
        lvl[dt] = base * (1 + yy/100)
    # seam anchor
    lvl = lvl + (tgt.loc[last_rel] - lvl.iloc[0] + (lvl.iloc[0]-lvl.iloc[0]))
    out_id = f"{TARGET_COL}_NOWCAST"
    print(f"\n{'WROTE' if write else 'DRY'} {out_id}: {len(lvl)} daily nowcast pts, {gap.index.min().date()}->{gap.index.max().date()}")
    print("  latest INDPRO-YoY nowcast:", round(gap.iloc[-1],2), "% (last actual print", round(tgt_yoy.iloc[-1],2),"%)")
    if write:
        now = datetime.datetime.now().isoformat()
        # write under BOTH keys: horizon_column (for horizon_dataset splice) and raw sid
        # (for _gci_raw_series splice) — different indicator data paths use different keys.
        for oid in (out_id, f"{TARGET}_NOWCAST"):
            rows = [(oid, dt.strftime('%Y-%m-%d'), float(v)) for dt, v in lvl.items()]
            c.executemany("INSERT OR REPLACE INTO observations VALUES(?,?,?)", rows)
            c.execute("""INSERT OR REPLACE INTO series_meta VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
                      (oid, "Industrial Production (LHM Growth Nowcast)", "LHM Nowcast", "Nowcast",
                       "Daily", "index", now, now, "nowcast", rows[-1][1], len(rows)))
        c.commit()

if __name__ == "__main__":
    main(write="--write" in sys.argv)
