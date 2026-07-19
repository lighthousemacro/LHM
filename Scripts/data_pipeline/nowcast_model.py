"""LHM Nowcast Model — generalized proprietary multi-proxy engine
================================================================
Config-driven. Each target = an official series nowcast from a basket of high-frequency proxies via
elastic-net (fitted weights = the proprietary combination). Walk-forward OOS validated. Optionally
benchmarked against an external reference nowcast (e.g. our GDP nowcast vs Atlanta Fed GDPNow).

Run:  python3 nowcast_model.py [TARGET ...] [--write]     (default: all targets, dry-run)
"""
import sys, sqlite3, datetime
import numpy as np, pandas as pd
from sklearn.linear_model import ElasticNetCV
from sklearn.preprocessing import StandardScaler

DB = "/Users/bob/LHM/Data/databases/Lighthouse_Master.db"

GROWTH_BASKET = {
    "COPPER_Close":"yoy","DCOILWTICO":"yoy","SMH_Close":"yoy","IYT_Close":"yoy","HYG_Close":"yoy",
    "NFCI":"level","ICSA":"level","T10Y2Y":"level","DTWEXBGS":"yoy","XLI_XLP":"ratio:XLI_Close/XLP_Close",
}
GDP_BASKET = dict(GROWTH_BASKET, **{"XLY_XLP":"ratio:XLY_Close/XLP_Close","RSAFS":"yoy_m"})  # + consumption
LABOR_BASKET = {"ICSA":"level","CCSA":"level","IC4WSA":"level","TEMPHELPS":"yoy_m","HYG_Close":"yoy","XLI_XLP":"ratio:XLI_Close/XLP_Close"}
INFLATION_BASKET = {"T5YIE":"level","T10YIE":"level","DCOILWTICO":"yoy","COPPER_Close":"yoy","DTWEXBGS":"yoy","GASREGW":"yoy"}
HOUSING_BASKET = {"MORTGAGE30US":"level","ZILLOW_ZHVI_NATIONAL":"yoy_m","TV_USMAPL":"level","XHB_Close":"yoy","WPU081":"yoy_m"}

TARGETS = {
    "INDPRO": dict(target="INDPRO", transform="yoy", freq="MS", horizon_col="Industrial_Production",
                   basket=GROWTH_BASKET, start="2004-01-01", label="Industrial Production YoY"),
    # GDP YoY: OOS r=0.88. (QoQ-annualized was tried — OOS 0.09; market proxies nowcast the
    # smooth growth-trend far better than the noisy quarterly print, which is GDPNow's turf.)
    "GDP":    dict(target="GDPC1", transform="yoy", freq="QS", horizon_col=None,
                   basket=GDP_BASKET, start="2004-01-01", label="Real GDP YoY"),
    "LABOR":  dict(target="PAYEMS", transform="yoy", freq="MS", horizon_col=None,
                   basket=LABOR_BASKET, start="2004-01-01", label="Nonfarm Payrolls YoY"),
    "INFLATION": dict(target="CPILFESL", transform="yoy", freq="MS", horizon_col=None,
                   basket=INFLATION_BASKET, start="2004-01-01", label="Core CPI YoY"),
    "HOUSING": dict(target="CSUSHPINSA", transform="yoy", freq="MS", horizon_col=None,
                   basket=HOUSING_BASKET, start="2004-01-01", label="Case-Shiller Home Prices YoY"),
}

def load(c, sid):
    df = pd.read_sql_query("SELECT date,value FROM observations WHERE series_id=? ORDER BY date", c, params=(sid,))
    if df.empty: return None
    df['date']=pd.to_datetime(df['date']); return df.set_index('date')['value'].dropna()

def proxy_series(c, spec_name, spec):
    if spec.startswith("ratio:"):
        num,den=spec[6:].split("/"); a,b=load(c,num),load(c,den)
        if a is None or b is None: return None
        return (a/b).dropna().pct_change(252)*100
    s=load(c, spec_name)
    if s is None: return None
    if spec=="yoy": return s.pct_change(252)*100
    if spec=="yoy_m": return (s.pct_change(12)*100).reindex(pd.date_range(s.index.min(),s.index.max())).ffill()
    return s

def target_transform(s, how, freq="MS"):
    ppy = 4 if str(freq).upper().startswith("Q") else 12   # periods per year
    if how=="yoy": return (s.pct_change(ppy)*100).dropna()
    if how=="qoq_ann": return ((s.pct_change(1)+1)**4-1).mul(100).dropna()
    return s

def run_target(c, key, cfg, write=False):
    tgt=load(c, cfg["target"]); ty=target_transform(tgt, cfg["transform"], cfg["freq"])
    rule=cfg["freq"]
    P={}
    for nm,spec in cfg["basket"].items():
        s=proxy_series(c, nm.split("_X")[0] if nm.startswith(("XLI_XLP","XLY_XLP")) else nm, spec)
        # ratio specs carry their own series; use key name for column
        if spec.startswith("ratio:"):
            num,den=spec[6:].split("/"); a,b=load(c,num),load(c,den)
            s=(a/b).dropna().pct_change(252)*100 if a is not None and b is not None else None
        if s is not None: P[nm]=s
    Pdf=pd.DataFrame(P).sort_index().ffill()
    Pm=Pdf.resample(rule).mean()
    d=pd.concat([ty.rename("y"), Pm],axis=1).dropna(); d=d[d.index>=cfg["start"]]
    if len(d)<40: print(f"[{key}] insufficient overlap ({len(d)})"); return
    X,y=d.drop(columns="y").values, d["y"].values
    sc=StandardScaler().fit(X)
    model=ElasticNetCV(l1_ratio=[.1,.5,.7,.9,.95,1],cv=5,max_iter=6000,random_state=0).fit(sc.transform(X),y)
    ins=np.corrcoef(model.predict(sc.transform(X)),y)[0,1]
    n0=max(24,len(d)//4); preds,acts=[],[]
    for i in range(n0,len(d)):
        m=ElasticNetCV(l1_ratio=[.5,.9,1],cv=4,max_iter=3000).fit(sc.transform(X[:i]),y[:i])
        preds.append(m.predict(sc.transform(X[i:i+1]))[0]); acts.append(y[i])
    oos=np.corrcoef(preds,acts)[0,1]
    W=sorted(zip(d.drop(columns="y").columns,model.coef_),key=lambda x:-abs(x[1]))
    print(f"\n=== {key}: {cfg['label']} ===")
    print(f"  in-sample r={ins:.2f} | walk-forward OOS r={oos:.2f} | n={len(d)}")
    print("  proprietary weights:", ", ".join(f"{n}{w:+.2f}" for n,w in W[:6]))
    # daily nowcast
    Xd=Pdf.dropna(); yhat=pd.Series(model.predict(sc.transform(Xd.values)),index=Xd.index)
    gap=yhat[yhat.index>tgt.index.max()]
    latest=gap.iloc[-1] if len(gap) else yhat.iloc[-1]
    print(f"  latest nowcast: {latest:.2f}  (last actual print {ty.iloc[-1]:.2f})")
    if cfg.get("benchmark"):
        bench=load(c, cfg["benchmark"])
        if bench is not None:
            # align our quarterly nowcast vs external nowcast on quarter starts
            ours_q=yhat.resample(rule).last(); j=pd.concat([ours_q.rename("ours"),bench.rename("ext")],axis=1).dropna()
            if len(j)>8:
                r=np.corrcoef(j["ours"],j["ext"])[0,1]
                print(f"  BENCHMARK vs {cfg['benchmark']}: correlation {r:.2f} over {len(j)} quarters "
                      f"(ours latest {ours_q.iloc[-1]:.2f} vs {cfg['benchmark']} {bench.iloc[-1]:.2f})")
    if write and len(gap):
        now=datetime.datetime.now().isoformat()
        keys=[f"{cfg['target']}_NOWCAST"] + ([f"{cfg['horizon_col']}_NOWCAST"] if cfg.get("horizon_col") else [])
        # write the nowcast VALUE (transformed) under LHM_<KEY>_NOWCAST for the transformed read,
        # and a level reconstruction under the raw/horizon keys for splice paths
        val_id=f"LHM_{key}_NOWCAST"
        rows=[(val_id,dt.strftime('%Y-%m-%d'),float(v)) for dt,v in gap.items()]
        c.executemany("INSERT OR REPLACE INTO observations VALUES(?,?,?)",rows)
        c.execute("INSERT OR REPLACE INTO series_meta VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                  (val_id,f"LHM {cfg['label']} Nowcast","LHM Nowcast","Nowcast","Daily",cfg["transform"],
                   now,now,"nowcast",rows[-1][1],len(rows)))
        c.commit(); print(f"  wrote {val_id} ({len(rows)} daily pts)")

def main():
    args=[a for a in sys.argv[1:] if not a.startswith("--")]
    write="--write" in sys.argv
    c=sqlite3.connect(DB)
    for key in (args or TARGETS):
        if key in TARGETS: run_target(c, key, TARGETS[key], write=write)

if __name__=="__main__":
    main()
