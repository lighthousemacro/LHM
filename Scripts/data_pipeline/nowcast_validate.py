"""LHM Nowcast Validation & Calibration
=======================================
Walk-forward diagnostics for each nowcast target: OOS correlation (direction), bias/RMSE/MAE (magnitude),
directional hit-rate, and recent-regime drift. Then a linear recalibration (actual ~ a + b*pred fitted on
the OOS predictions) that corrects level bias — because a high OOS r can still sit on biased magnitudes,
which is what the payrolls read exposed. Writes calibrated live reads + full diagnostics to nowcast_summary.json.

Run:  python3 nowcast_validate.py [--write]
"""
import sys, json, sqlite3
import numpy as np, pandas as pd
from sklearn.linear_model import ElasticNetCV
from sklearn.preprocessing import StandardScaler
import importlib.util
_spec = importlib.util.spec_from_file_location("nm", "/Users/bob/LHM/Scripts/data_pipeline/nowcast_model.py")
nm = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(nm)

OUT = "/Users/bob/LHM/Working/db_overview/nowcast_summary.json"

def design(c, cfg):
    tgt = nm.load(c, cfg["target"]); ty = nm.target_transform(tgt, cfg["transform"], cfg["freq"])
    P = {}
    for name, spec in cfg["basket"].items():
        if spec.startswith("ratio:"):
            num, den = spec[6:].split("/"); a, b = nm.load(c, num), nm.load(c, den)
            s = (a/b).dropna().pct_change(252)*100 if a is not None and b is not None else None
        else:
            s = nm.proxy_series(c, name, spec)
        if s is not None: P[name] = s
    Pdf = pd.DataFrame(P).sort_index().ffill()
    Pm = Pdf.resample(cfg["freq"]).mean()
    d = pd.concat([ty.rename("y"), Pm], axis=1).dropna(); d = d[d.index >= cfg["start"]]
    return d, Pdf, tgt, ty

def validate(key, cfg, c):
    d, Pdf, tgt, ty = design(c, cfg)
    X, y = d.drop(columns="y").values, d["y"].values
    sc = StandardScaler().fit(X)
    n0 = max(24, len(d)//4)
    preds, acts, prev = [], [], []
    for i in range(n0, len(d)):
        m = ElasticNetCV(l1_ratio=[.5,.9,1], cv=4, max_iter=3000).fit(sc.transform(X[:i]), y[:i])
        preds.append(m.predict(sc.transform(X[i:i+1]))[0]); acts.append(y[i]); prev.append(y[i-1])
    preds, acts, prev = map(np.array, (preds, acts, prev))
    err = preds - acts
    oos_r = np.corrcoef(preds, acts)[0,1]
    bias = err.mean(); rmse = np.sqrt((err**2).mean()); mae = np.abs(err).mean()
    dir_hit = np.mean(np.sign(preds - prev) == np.sign(acts - prev))
    recent_bias = err[-12:].mean()
    # linear recalibration: actual = a + b*pred  (least squares on OOS)
    b_cal, a_cal = np.polyfit(preds, acts, 1)
    # live prediction (full-sample fit) + calibrated
    full = ElasticNetCV(l1_ratio=[.1,.5,.7,.9,.95,1], cv=5, max_iter=6000, random_state=0).fit(sc.transform(X), y)
    live_raw = full.predict(sc.transform(Pdf.dropna().tail(1).values))[0]
    # guard: only trust the linear recalibration when it's stable (near-unit slope). An extreme
    # slope means the OOS scatter is being over-fit — fall back to bias-only and flag.
    stable = 0.5 <= b_cal <= 1.8
    live_cal = (a_cal + b_cal * live_raw) if stable else (live_raw - bias)
    # confidence tier: needs both correlation AND period-to-period directional skill
    if oos_r >= 0.75 and dir_hit >= 0.60 and abs(recent_bias) <= rmse:
        tier = "STRONG"
    elif oos_r >= 0.60 and dir_hit >= 0.58:
        tier = "USABLE"
    else:
        tier = "NOT READY"
    return dict(id=f"LHM_{key}_NOWCAST", label=cfg["label"], oos_r=round(float(oos_r),2),
                bias=round(float(bias),2), rmse=round(float(rmse),2), mae=round(float(mae),2),
                dir_hit=round(float(dir_hit),2), recent_bias=round(float(recent_bias),2), tier=tier,
                latest_raw=round(float(live_raw),2), latest=round(float(live_cal),2),
                last_print=round(float(ty.iloc[-1]),2),
                calib=(f"{a_cal:+.2f}+{b_cal:.2f}x" if stable else "unstable->bias-only"),
                basket=", ".join(cfg["basket"].keys()))

def main(write=False):
    c = sqlite3.connect(nm.DB)
    rows = []
    for key, cfg in nm.TARGETS.items():
        try:
            r = validate(key, cfg, c); rows.append(r)
            print(f"{r['label']:32} OOS r={r['oos_r']:.2f}  bias={r['bias']:+.2f}  RMSE={r['rmse']:.2f}  "
                  f"dir-hit={r['dir_hit']:.0%}  recent-bias={r['recent_bias']:+.2f}")
            print(f"   raw live {r['latest_raw']:+.2f}%  ->  CALIBRATED {r['latest']:+.2f}%  (vs last print {r['last_print']:+.2f}%)  [{r['calib']}]")
        except Exception as e:
            print(f"{key}: FAILED {type(e).__name__} {e}")
    rows.sort(key=lambda x: -x["oos_r"])
    if write:
        json.dump(rows, open(OUT, "w"), indent=1)
        print(f"\nwrote {OUT} with calibrated reads + diagnostics")
    return rows

if __name__ == "__main__":
    main(write="--write" in sys.argv)
