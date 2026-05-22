#!/usr/bin/env python3
"""
LHM Phase-B step 3 — HONEST FULL multi-role registry re-run.

Resume anchor: Strategy/INDICATOR_MIGRATION_PROGRAM.md (SCOPE
RECONCILIATION + checklist NEXT). This re-runs the SAME SCOPE as the
May 8-9 v3-v6 registry (pillar x {diagnostic, predictive[own + asset
grid + rotation grid], lead-lag}) but through the LEAK-CORRECTED
harness, because v3-v6 carried the same two leaks Phase B caught:
  - ref-in-basket tautology in diagnostic companions, and
  - overlapping-horizon pseudo-replication in 63/252d daily cells.

It imports the validated engines, does not reimplement them:
  - pillar_reoptimize_v3 : zn (PIT), build_target, walk_forward
    (purged + NON-OVERLAP headline OOS IC), _ic, loaders.
  - signal_registry_v3   : walk_forward_concurrent (ref-excluded
    diagnostic).
The ONE new engine here is the lead-lag event study (v6 scope), built
with the same discipline: non-overlapping sampling so t-stats are not
overlap-inflated, plus a NOISE-breach false-discovery control.

Baskets + per-component sign/transform come from `pillar_specs_v2.py`
(the canonical spec sheet, 10 pillars) plus a small supplement for
MSI/SPI/LFI/LDI/CLG (not in pillar_specs_v2).

Deliverable: the honest registry table. NOT an INDICATORS_MASTER
rewrite (Bob, explicit).

Run (py3.14 only):
  .../python3.14 Scripts/backtest/registry_honest_v4.py cell PCI diag
  .../python3.14 Scripts/backtest/registry_honest_v4.py cell GCI pred own
  .../python3.14 Scripts/backtest/registry_honest_v4.py cell TCI pred spx_252d
  .../python3.14 Scripts/backtest/registry_honest_v4.py cell GCI rel XLY/XLP 252
  .../python3.14 Scripts/backtest/registry_honest_v4.py cell FCI leadlag spx_63d
  .../python3.14 Scripts/backtest/registry_honest_v4.py full
"""
from __future__ import annotations

import json
import sqlite3
import sys
import warnings
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pillar_reoptimize_v3 import (  # noqa: E402
    DB, zn, to_grid, build_target, walk_forward, _ic, normalize_weights,
    load_db_series, load_yf, load_composite, grid_of,
    MIN_TRAIN_M, REFIT_M, MIN_TRAIN_B, REFIT_B, FFILL_M, FFILL_B,
    NOISE_SEED, SKILL_FLOOR,
)
from signal_registry_v3 import walk_forward_concurrent, _wf_light  # noqa: E402
sys.path.insert(0, "/Users/bob/LHM/Scripts/backtest")
from pillar_specs_v2 import EXPANDED_PILLAR_SPECS, DISPLAY_NAMES  # noqa: E402

warnings.simplefilter("ignore")
OUT = Path("/Users/bob/LHM/Outputs/mri_optimization/registry_honest_v4.json")

# Pillars not in pillar_specs_v2 (breadth/sentiment/divergence/labor subs).
# (series_id, sign, transform) tuples, same shape as the spec components.
SUPPLEMENT = {
    "MSI": dict(components=[
        ("SPX_vs_200d_pct", +1, "level"), ("SPX_vs_50d_pct", +1, "level"),
        ("SPX_20d_slope", +1, "level"), ("SPX_Z_RoC_63d", +1, "level"),
        ("SPX_50d_slope", +1, "level"), ("SPX_PCT_ABOVE_50D", +1, "level"),
        ("SPX_PCT_ABOVE_200D", +1, "level"), ("SPX_NET_NEW_HIGHS", +1, "level"),
        ("SPX_AD_LINE", +1, "level"), ("SPX_MCCLELLAN_SUM", +1, "level"),
        ("SPX_BREADTH_THRUST", +1, "level")],
        target=("SPY", 63, "asset")),
    "SPI": dict(components=[
        ("VIXCLS", -1, "level"), ("AAII_Bull_Bear_Spread", +1, "level"),
        ("VIX_percentile_252d", -1, "level"), ("AAII_Bullish", +1, "level"),
        ("AAII_Bearish", -1, "level"), ("VIX_vs_50d_pct", -1, "level"),
        ("VIX_BACKWARDATION", -1, "level")],
        target=("SPY", 63, "asset")),
    "LFI": dict(components=[
        ("UEMP27OV", +1, "level"), ("UNRATE", +1, "level"),
        ("JTSQUR", -1, "level"), ("JTSHIR", -1, "level"),
        ("JTSJOL", -1, "level"), ("TEMPHELPS", -1, "yoy_pct"),
        ("ICSA", +1, "yoy_pct"), ("CCSA", +1, "yoy_pct"),
        ("AHETPI", -1, "yoy_pct"), ("U6RATE", +1, "level"),
        ("AWHAETP", -1, "yoy_pct")],
        target=("PAYEMS", 126, "macro")),
    "LDI": dict(components=[
        ("JTSQUR", +1, "level"), ("JTSHIR", +1, "level"),
        ("ICSA", -1, "yoy_pct"), ("CCSA", -1, "yoy_pct")],
        target=("PAYEMS", 126, "macro")),
    "CLG": dict(components=[
        ("BAMLH0A0HYM2", +1, "level"), ("UEMP27OV", -1, "level"),
        ("UNRATE", -1, "level"), ("JTSQUR", +1, "level"),
        ("AWHAETP", +1, "yoy_pct")],
        target=("BAMLH0A0HYM2", 63, "credit")),
}

# Diagnostic ground-truth refs (from pillar_registry_v3_summary). Excluded
# from the feature basket before fitting (no ref-in-basket tautology).
DIAG_REFS = {
    "LPI": ("UNRATE", "level"), "PCI": ("PCEPILFE", "yoy_pct"),
    "GCI": ("CFNAIMA3", "level"), "HCI": ("CSUSHPINSA", "yoy_pct"),
    "CCI": ("PCEC96", "yoy_pct"), "BCI": ("ANDENO", "yoy_pct"),
    "TCI": ("DTWEXBGS", "yoy_pct"), "GCI_Gov": ("THREEFYTP10", "level"),
    "FCI": ("ANFCI", "level"), "LCI": ("TOTRESNS", "yoy_pct"),
    "MSI": ("SPX_vs_200d_pct", "level"),
    "SPI": ("AAII_Bull_Bear_Spread", "level"),
    "LFI": ("UNRATE", "level"), "LDI": ("UNRATE", "level"),
    "CLG": ("UNRATE", "level"),
}

# v5 asset-predictive grid (13). Mapped to honest build_target specs:
# rates/spreads/vix via db_fwd_chg (DB series), equities/fx via yf return.
ASSET_TARGETS = {
    "spx_63d":    dict(kind="asset_fwd_ret", tgt="SPY", h=63),
    "spx_252d":   dict(kind="asset_fwd_ret", tgt="SPY", h=252),
    "vix_63d":    dict(kind="db_fwd_chg", tgt="VIXCLS", h=63),
    "hyoas_63d":  dict(kind="db_fwd_chg", tgt="BAMLH0A0HYM2", h=63),
    "hyoas_126d": dict(kind="db_fwd_chg", tgt="BAMLH0A0HYM2", h=126),
    "igoas_63d":  dict(kind="db_fwd_chg", tgt="BAMLC0A0CM", h=63),
    "dgs2_252d":  dict(kind="db_fwd_chg", tgt="DGS2", h=252),
    "dgs10_252d": dict(kind="db_fwd_chg", tgt="DGS10", h=252),
    "t10y2y_252d": dict(kind="db_fwd_chg", tgt="T10Y2Y", h=252),
    "dxy_252d":   dict(kind="asset_fwd_ret", tgt="DX-Y.NYB", h=252),
    "usdjpy_252d": dict(kind="asset_fwd_ret", tgt="JPY=X", h=252),
}
ROTATIONS = ["EEM/EFA", "GLD/SPY", "HYG/LQD", "IWM/SPY", "QQQ/SPY",
             "SHY/TLT", "SPY/EFA", "SPY/IEF", "SPY/TLT", "XHB/SPY",
             "XLK/XLU", "XLY/XLP"]
ROT_HORIZONS = [63, 252]


# --------------------------------------------------------------------------
def transform_series(s: pd.Series, kind: str) -> pd.Series:
    if kind == "yoy_pct":
        return s.pct_change(12) * 100.0
    if kind == "log_yoy":
        return np.log(s.replace(0, np.nan)).diff(12)
    if kind == "delta":
        return s.diff(1)
    return s  # level


def get_components(pillar):
    if pillar in EXPANDED_PILLAR_SPECS:
        sp = EXPANDED_PILLAR_SPECS[pillar]
        comps = [(c[0], c[1], c[2]) for c in sp["components"]]
        return comps, sp["target"]
    sup = SUPPLEMENT[pillar]
    return [(c[0], c[1], c[2]) for c in sup["components"]], sup["target"]


def build_feat_spec(conn, comps, grid, znmp, ff, exclude=None):
    """Per-component: load, to grid, sign*transform, zn PIT. + NOISE."""
    exclude = exclude or set()
    series, dropped = {}, []
    for sid, sign, tf in comps:
        if sid in exclude:
            continue
        s = load_db_series(conn, sid)
        if s is None or s.empty:
            dropped.append(sid)
            continue
        st = transform_series(to_grid(s, grid), tf) * sign
        series[sid] = st
    if not series:
        return None, [], [], dropped
    full = pd.DatetimeIndex([])
    for s in series.values():
        full = full.union(s.index)
    full = full.sort_values()
    feat = pd.DataFrame(index=full)
    pnames = []
    for sid, s in series.items():
        feat[sid] = zn(s.reindex(full).ffill(limit=ff), min_periods=znmp)
        pnames.append(sid)
    rng = np.random.default_rng(NOISE_SEED)
    for k in (1, 2):
        feat[f"NOISE{k}"] = zn(pd.Series(rng.standard_normal(len(full)),
                                         index=full), min_periods=znmp)
    sig_idx = feat[pnames].dropna(how="all").index
    return feat, pnames, sig_idx, dropped


# --------------------------------------------------------------------------
# ROLE 1 — diagnostic (concurrent, ref EXCLUDED)
# --------------------------------------------------------------------------
def run_diagnostic(conn, pillar):
    comps, _ = get_components(pillar)
    ref_sid, ref_tf = DIAG_REFS[pillar]
    feat, pnames, sig_idx, dropped = build_feat_spec(
        conn, comps, "M", 24, FFILL_M, exclude={ref_sid})
    if feat is None or len(pnames) < 2:
        return dict(pillar=pillar, role="diagnostic",
                    status="degenerate", dropped=dropped)
    rs = load_db_series(conn, ref_sid)
    if rs is None or rs.empty:
        return dict(pillar=pillar, role="diagnostic", status="no_ref")
    ref = zn(transform_series(to_grid(rs, "M"), ref_tf)
             .reindex(sig_idx).ffill(limit=FFILL_M), min_periods=24)
    r = walk_forward_concurrent(
        feat[pnames + ["NOISE1", "NOISE2"]].reindex(sig_idx),
        ref.reindex(sig_idx), pnames, MIN_TRAIN_M, REFIT_M)
    r.update(pillar=pillar, role="diagnostic",
             ref=f"{ref_sid}({ref_tf})", excluded_ref=ref_sid,
             dropped=dropped)
    return r


# --------------------------------------------------------------------------
# ROLE 2 — predictive (own / asset grid / rotation grid), purged non-overlap
# --------------------------------------------------------------------------
def run_predictive(conn, pillar, spec, label, light=False):
    grid = grid_of(spec["kind"])
    mt, rf = ((MIN_TRAIN_M, REFIT_M) if grid == "M"
              else (MIN_TRAIN_B, REFIT_B))
    znmp = 24 if grid == "M" else 252
    ff = FFILL_M if grid == "M" else FFILL_B
    comps, _ = get_components(pillar)
    feat, pnames, sig_idx, dropped = build_feat_spec(
        conn, comps, grid, znmp, ff)
    if feat is None or len(pnames) < 2:
        return dict(pillar=pillar, role="predictive", cell=label,
                    status="degenerate", dropped=dropped)
    tgt, h_steps = build_target(conn, spec, sig_idx, grid)
    if tgt is None or tgt.dropna().empty:
        return dict(pillar=pillar, role="predictive", cell=label,
                    status="no_target")
    if light:
        # ridge-only purged non-overlap screen (faithful to v3/v5 single-
        # model WF; full zoo reserved for own-target survivors).
        d = pd.concat([feat[pnames].reindex(sig_idx),
                       tgt.reindex(sig_idx).rename("__y")], axis=1)
        d = d[np.isfinite(d["__y"])]
        if len(d) < mt + 2 * h_steps + 6:
            return dict(pillar=pillar, role="predictive", cell=label,
                        grid=grid, status="insufficient_overlap")
        ic, nn = _wf_light(d[pnames].to_numpy(float),
                           d["__y"].to_numpy(float), h_steps, mt, rf)
        verdict = ("DEMOTE" if (ic is None or abs(ic) < SKILL_FLOOR)
                   else "KEEP")
        return dict(pillar=pillar, role="predictive", cell=label,
                    grid=grid, status="ok", mode="light",
                    oos_ic=round(ic, 3) if ic is not None else None,
                    n_oos_noov=nn, verdict=verdict, dropped=dropped)
    wf = walk_forward(feat.reindex(sig_idx), tgt.reindex(sig_idx),
                      pnames, h_steps, mt, rf)
    ic = wf.get("oos_ic")
    verdict = ("DEMOTE" if (wf.get("status") != "ok" or ic is None
                            or abs(ic) < SKILL_FLOOR) else "KEEP")
    return dict(pillar=pillar, role="predictive", cell=label,
                grid=grid, status=wf.get("status"), mode="full",
                oos_ic=round(ic, 3) if ic is not None else None,
                oos_ic_overlap=(round(wf["oos_ic_overlap"], 3)
                                if wf.get("oos_ic_overlap") is not None
                                else None),
                oos_rank_ic=(round(wf["oos_rank_ic"], 3)
                             if wf.get("oos_rank_ic") is not None else None),
                n_oos_noov=wf.get("n_oos_noov"),
                noise_ratio=(round(wf["noise_ratio"], 3)
                             if wf.get("noise_ratio") is not None else None),
                verdict=verdict, dropped=dropped)


# --------------------------------------------------------------------------
# ROLE 3 — lead-lag event study (NEW). Non-overlap sampled => honest t.
# --------------------------------------------------------------------------
def run_leadlag(conn, pillar, spec, label, thr=1.0):
    grid = grid_of(spec["kind"])
    znmp = 24 if grid == "M" else 252
    ff = FFILL_M if grid == "M" else FFILL_B
    comps, _ = get_components(pillar)
    feat, pnames, sig_idx, dropped = build_feat_spec(
        conn, comps, grid, znmp, ff)
    if feat is None or len(pnames) < 2:
        return dict(pillar=pillar, role="leadlag", cell=label,
                    status="degenerate")
    tgt, h_steps = build_target(conn, spec, sig_idx, grid)
    if tgt is None or tgt.dropna().empty:
        return dict(pillar=pillar, role="leadlag", cell=label,
                    status="no_target")
    cz = feat[pnames].reindex(sig_idx).mean(axis=1)          # eq-weight z
    nz = feat["NOISE1"].reindex(sig_idx)                     # control

    def event(zser):
        d = pd.concat([zser.rename("z"), tgt.rename("r")], axis=1).dropna()
        if len(d) < 120:
            return None
        d = d.iloc[::max(1, h_steps)]                        # NON-OVERLAP
        z, r = d["z"].to_numpy(float), d["r"].to_numpy(float)
        base = float(np.mean(r))
        out = {}
        for nm, mask in (("up", z > thr), ("dn", z < -thr)):
            rs = r[mask]
            rn = r[~mask]
            if len(rs) < 8 or len(rn) < 8 or rs.std() == 0:
                out[nm] = None
                continue
            # Welch t of conditional vs the rest (non-overlap sample)
            t = ((rs.mean() - rn.mean())
                 / np.sqrt(rs.var(ddof=1) / len(rs)
                           + rn.var(ddof=1) / len(rn))) if rn.std() else 0.0
            out[nm] = dict(n=int(len(rs)), excess=round(float(rs.mean()
                           - base), 4), t=round(float(t), 2))
        return out

    sig = event(cz)
    ctl = event(nz)
    if sig is None:
        return dict(pillar=pillar, role="leadlag", cell=label,
                    status="insufficient")
    # honest verdict: |t|>=2 AND beats the noise-breach control on |t|
    best = max((abs(sig[k]["t"]) for k in ("up", "dn")
                if sig.get(k)), default=0.0)
    ctl_best = max((abs(ctl[k]["t"]) for k in ("up", "dn")
                    if ctl and ctl.get(k)), default=0.0)
    verdict = ("SIGNAL" if best >= 2.0 and best > ctl_best + 0.5
               else "null")
    return dict(pillar=pillar, role="leadlag", cell=label, grid=grid,
                h_steps=h_steps, signal=sig, noise_ctrl=ctl,
                noise_best_t=round(ctl_best, 2), verdict=verdict,
                status="ok")


# --------------------------------------------------------------------------
def own_spec(pillar):
    _, tg = get_components(pillar)
    sid, h, mode = tg[0], tg[1], tg[2] if len(tg) > 2 else "macro"
    if pillar in EXPANDED_PILLAR_SPECS:
        # spec target tuple: (series_id, horizon_days, mode, thresh)
        t = EXPANDED_PILLAR_SPECS[pillar]["target"]
        sid, h = t[0], t[1]
        kind = ("asset_fwd_ret" if "fwd_return" in t[2]
                else "db_fwd_chg")
    else:
        kind = "asset_fwd_ret" if mode == "asset" else "db_fwd_chg"
    return dict(kind=kind, tgt=sid, h=h)


ALL_PILLARS = (list(EXPANDED_PILLAR_SPECS.keys())
               + list(SUPPLEMENT.keys()))


def main():
    a = sys.argv[1:]
    conn = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)

    if a and a[0] == "cell":
        pillar, role = a[1], a[2]
        if role == "diag":
            print(json.dumps(run_diagnostic(conn, pillar), indent=2,
                             default=str))
        elif role == "pred":
            sub = a[3]
            if sub == "own":
                sp = own_spec(pillar)
            elif sub in ASSET_TARGETS:
                sp = ASSET_TARGETS[sub]
            else:
                sp = dict(kind="db_fwd_chg", tgt=sub, h=126)
            print(json.dumps(run_predictive(conn, pillar, sp, sub),
                             indent=2, default=str))
        elif role == "rel":
            pair, h = a[3], int(a[4])
            sp = dict(kind="ratio_fwd_ret", tgt=pair, h=h)
            print(json.dumps(run_predictive(conn, pillar, sp,
                             f"{pair}@{h}d"), indent=2, default=str))
        elif role == "leadlag":
            sub = a[3]
            sp = (ASSET_TARGETS.get(sub)
                  or dict(kind="db_fwd_chg", tgt=sub, h=126))
            print(json.dumps(run_leadlag(conn, pillar, sp, sub),
                             indent=2, default=str))
        conn.close()
        return

    # FULL grid
    reg = []
    for p in ALL_PILLARS:
        print(f"  diag  {p}", flush=True)
        reg.append(run_diagnostic(conn, p))
        print(f"  pred-own {p}", flush=True)
        reg.append(run_predictive(conn, p, own_spec(p), "own"))  # full zoo
        for lbl, sp in ASSET_TARGETS.items():
            reg.append(run_predictive(conn, p, sp, lbl, light=True))
        for pair in ROTATIONS:
            for h in ROT_HORIZONS:
                reg.append(run_predictive(
                    conn, p, dict(kind="ratio_fwd_ret", tgt=pair, h=h),
                    f"{pair}@{h}d", light=True))
        print(f"  leadlag {p}", flush=True)
        for lbl in ("spx_63d", "spx_252d", "hyoas_126d"):
            reg.append(run_leadlag(conn, p, ASSET_TARGETS[lbl], lbl))
    conn.close()

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(dict(
        generated=datetime.now().isoformat(timespec="seconds"),
        method="leak-corrected: diag ref-excluded, pred purged non-overlap, "
               "leadlag non-overlap t-test + noise-breach control",
        n_cells=len(reg), registry=reg), indent=2, default=str))

    diag = [r for r in reg if r.get("role") == "diagnostic"]
    pred = [r for r in reg if r.get("role") == "predictive"]
    ll = [r for r in reg if r.get("role") == "leadlag"]
    pred_real = [r for r in pred if r.get("verdict") == "KEEP"]
    ll_real = [r for r in ll if r.get("verdict") == "SIGNAL"]
    diag_real = [r for r in diag if r.get("verdict") == "REAL"]
    print("\n" + "=" * 78)
    print(f"HONEST REGISTRY v4  ·  {len(reg)} cells  ·  "
          f"{datetime.now():%Y-%m-%d %H:%M}")
    print("=" * 78)
    print(f"diagnostic : {len(diag_real)}/{len(diag)} REAL "
          f"(vs v3 claim 10/12)")
    print(f"predictive : {len(pred_real)}/{len(pred)} KEEP "
          f"(vs v3/v5 claim ~168/418)")
    print(f"lead-lag   : {len(ll_real)}/{len(ll)} SIGNAL "
          f"(vs v6 claim 609/776)")
    print(f"\nJSON -> {OUT}")


if __name__ == "__main__":
    main()
