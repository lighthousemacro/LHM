#!/usr/bin/env python3
"""
LHM Phase-B step 2 — the SIGNAL REGISTRY: descriptive track + divergence
constructs + pairwise interaction screen.

Resume anchor: Strategy/INDICATOR_MIGRATION_PROGRAM.md.

Built on the LEAK-CORRECTED, validated machinery in
`pillar_reoptimize_v3.py` (purged WF, monthly grid for macro,
non-overlap headline OOS IC, impute-absent-to-neutral). This file does
NOT touch that one — it imports it.

Three things Bob explicitly asked for:

  1. DESCRIPTIVE TRACK (he wants both, not just predictive). Per pillar,
     a composite optimized for CONCURRENT tracking of the ground-truth
     reference, validated OUT-OF-SAMPLE (expanding WF, concurrent — fixes
     the April-30 PILLAR_DESCRIPTIVE_ANALYSIS in-sample-r inflation).
     Verdict: REAL (adds over best single component) / PROXY (is its best
     single in disguise) / WEAK / BROKEN.

  2. DIVERGENCE CONSTRUCTS (CLG/SBD/SSD). A gap z(A)-z(B) is NOT a
     reweightable basket — the v3 free-weight optimizer dissolved CLG
     into labor (HY-OAS got ~0 weight). Here the gap is evaluated AS
     DEFINED, single-feature, both sign conventions, so the Phase-A
     sign-flip is resolved instead of hidden.

  3. PAIRWISE INTERACTION SCREEN ("alone no signal, together great").
     Small candidate set = the pillar composites (controls multiple
     comparisons; raw-series pairs would be hundreds). Per economic
     target: purged non-overlap OOS IC of {X}, {Y}, {X,Y}, {X,Y,X*Y}.
     Flag weak-alone / strong-together. A NOISE x NOISE pair is carried
     as the false-discovery yardstick, and n_pairs is reported, because
     interaction mining is the single most overfit-prone pass here —
     flagged pairs are HYPOTHESES TO CONFIRM, not conclusions.

DIAGNOSIS / PROPOSAL ONLY. Canonical docs untouched.

Run (py3.14 only):
    /opt/homebrew/bin/python3.14 Scripts/backtest/signal_registry_v3.py
    .../python3.14 Scripts/backtest/signal_registry_v3.py desc PCI
    .../python3.14 Scripts/backtest/signal_registry_v3.py gap CLG
    .../python3.14 Scripts/backtest/signal_registry_v3.py pairs
"""

from __future__ import annotations

import json
import sqlite3
import sys
import warnings
from datetime import datetime
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pillar_reoptimize_v3 import (  # noqa: E402
    DB, PILLARS, LABOR, zn, to_grid, build_target, build_desc_ref,
    _select, _ic, normalize_weights, load_db_series, load_composite,
    TD_PER_MONTH, MIN_TRAIN_M, REFIT_M, FFILL_M, NOISE_SEED,
    SKILL_FLOOR, DESC_FLOOR,
)

warnings.simplefilter("ignore")
OUT = Path("/Users/bob/LHM/Outputs/mri_optimization/signal_registry_v3.json")

# divergence indicators: gap = sign * ( zn(A) - zn(B) ).  Evaluated AS THE
# GAP (single feature), never reweighted.  a/b: ("ID","series"|"composite").
GAPS = {
    "CLG": dict(  # credit spread vs labor fragility
        a=("BAMLH0A0HYM2", "series"), b=("LFI", "composite"),
        targets=[("UNRATE", 126), ("BAMLH0A0HYM2", 63)],
        desc=("UNRATE", "level"),
        note="Phase A: rankIC +0.30 vs fwd UNRATE but sign FLIP — resolve"),
    "SBD": dict(  # structure vs breadth
        a=("MSI", "composite"), b=("SPX_vs_200d_pct", "series"),
        targets=[("PAYEMS", 126)],
        desc=("SPX_vs_200d_pct", "level"),
        note="structure-breadth divergence"),
    "SSD": dict(  # sentiment vs structure
        a=("SPI", "composite"), b=("MSI", "composite"),
        targets=[("PAYEMS", 126)],
        desc=None, note="sentiment-structure divergence"),
}

# pairwise candidate set — pillar composites only (small => MC-controlled).
PAIR_CANDS = ["LPI", "PCI", "GCI", "HCI", "CCI", "BCI", "TCI", "FPI",
              "FCI", "LCI", "MSI", "SPI", "LFI", "LDI", "CLG"]
PAIR_TARGETS = [("PAYEMS", 126), ("UNRATE", 126),
                ("PCEPILFE", 126), ("INDPRO", 126)]


# --------------------------------------------------------------------------
# shared feature builder (compact re-impl; does not destabilize v3)
# --------------------------------------------------------------------------
def build_feat(conn, basket, composite, grid, znmp, ff):
    series = {}
    dropped = []
    for sid in basket:
        s = load_composite(conn, sid) if composite else load_db_series(conn, sid)
        if s is None or s.empty:
            dropped.append(sid)
        else:
            series[sid] = to_grid(s, grid)
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
# 1. DESCRIPTIVE TRACK — OOS-honest concurrent tracking
# --------------------------------------------------------------------------
def walk_forward_concurrent(feat, ref, pnames, min_train, refit):
    """Expanding WF, CONCURRENT target (ref_t from features_t). No purge
    (no forward overlap). OOS r is honest tracking, not the in-sample r
    the April-30 audit reported."""
    cols = pnames + ["NOISE1", "NOISE2"]
    df = feat[cols].copy()
    df["__r"] = ref
    df = df[np.isfinite(df["__r"])]
    n = len(df)
    if n < min_train + 24:
        return dict(n=n, status="insufficient")
    X = df[cols].to_numpy(float)
    Y = df["__r"].to_numpy(float)
    op, ot, pos = [], [], []
    i = min_train
    while i < n:
        j = min(i + refit, n)
        best = _select(X[:i], Y[:i])
        if best is not None:
            try:
                best.fit(X[:i], Y[:i])
                op.extend(best.predict(X[i:j]).tolist())
                ot.extend(Y[i:j].tolist())
                pos.extend(range(i, j))
            except Exception:
                pass
        i = j
    if len(op) < 24:
        return dict(n=n, n_oos=len(op), status="insufficient_oos")
    op, ot = np.asarray(op, float), np.asarray(ot, float)
    pos = np.asarray(pos, int)
    r_oos, _ = _ic(op, ot)
    rk = pd.Series(op).corr(pd.Series(ot), method="spearman")
    rk = float(rk) if rk == rk else None
    # best single component, measured on the SAME OOS rows.
    idx_oos = df.index[pos]
    best_single, best_sid = 0.0, None
    for p in pnames:
        rr, _ = _ic(feat[p].reindex(idx_oos).to_numpy(float), ot)
        if rr is not None and abs(rr) > best_single:
            best_single, best_sid = abs(rr), p
    incr = (abs(r_oos) - best_single) if r_oos is not None else None
    fbest = _select(X, Y)
    nz, raw = None, {}
    model = None
    if fbest is not None:
        fbest.fit(X, Y)
        model = type(fbest.named_steps["m"]).__name__
        coef = np.ravel(getattr(fbest.named_steps["m"], "coef_",
                                np.zeros(len(cols))))
        sm = float(np.abs(coef[:len(pnames)]).sum())
        nm = float(np.abs(coef[len(pnames):]).sum())
        nz = nm / (sm + nm) if (sm + nm) > 0 else None
        raw = {p: float(c) for p, c in zip(pnames, coef[:len(pnames)])}
    if r_oos is None:
        verdict = "BROKEN"
    elif abs(r_oos) >= DESC_FLOOR and (incr is not None and incr >= 0.03):
        verdict = "REAL"
    elif abs(r_oos) >= DESC_FLOOR:
        verdict = "PROXY"
    elif abs(r_oos) >= 0.40:
        verdict = "WEAK"
    else:
        verdict = "BROKEN"
    return dict(n=n, n_oos=len(op), r_oos=round(r_oos, 3) if r_oos else None,
                rank_oos=round(rk, 3) if rk is not None else None,
                best_single=round(best_single, 3), best_single_id=best_sid,
                incremental=round(incr, 3) if incr is not None else None,
                noise_ratio=round(nz, 3) if nz is not None else None,
                final_model=model, weights=normalize_weights(raw) if raw else {},
                verdict=verdict, status="ok")


def descriptive_track(conn, code, cfg):
    if cfg.get("desc") is None:
        return dict(pillar=code, status="no_desc_ref")
    feat, pnames, sig_idx, dropped = build_feat(
        conn, cfg["basket"], cfg.get("composite_basket", False),
        "M", 24, FFILL_M)
    if feat is None:
        return dict(pillar=code, status="no_components", dropped=dropped)
    ref = build_desc_ref(conn, cfg["desc"], sig_idx, "M", 24)
    if ref is None or ref.dropna().empty:
        return dict(pillar=code, status="no_ref", dropped=dropped)
    # CRITICAL: the ground-truth ref (and its level/transform twin, same
    # series_id) must NOT be a feature, or "predict X from a basket
    # containing X" gives a tautological r=1.00. Exclude it.
    ref_sid = cfg["desc"][0]
    pnames_d = [p for p in pnames if p != ref_sid]
    excluded = [p for p in pnames if p == ref_sid]
    if len(pnames_d) < 2:
        return dict(pillar=code, status="degenerate_after_ref_exclusion",
                    excluded_ref=excluded, dropped=dropped)
    r = walk_forward_concurrent(
        feat[pnames_d + ["NOISE1", "NOISE2"]].reindex(sig_idx),
        ref.reindex(sig_idx), pnames_d, MIN_TRAIN_M, REFIT_M)
    r.update(pillar=code, desc_ref=f"{cfg['desc'][0]}({cfg['desc'][1]})",
             excluded_ref_from_basket=excluded, dropped=dropped)
    return r


# --------------------------------------------------------------------------
# 2. DIVERGENCE CONSTRUCTS — the gap, intact, both signs
# --------------------------------------------------------------------------
def _load_leg(conn, leg):
    sid, kind = leg
    s = load_composite(conn, sid) if kind == "composite" else load_db_series(conn, sid)
    return None if (s is None or s.empty) else to_grid(s, "M")


def gap_eval(conn, name, cfg):
    a = _load_leg(conn, cfg["a"])
    b = _load_leg(conn, cfg["b"])
    if a is None or b is None:
        miss = [cfg["a"][0] if a is None else None,
                cfg["b"][0] if b is None else None]
        return dict(gap=name, status=f"missing {[m for m in miss if m]}")
    full = a.index.union(b.index).sort_values()
    za = zn(a.reindex(full).ffill(limit=FFILL_M), min_periods=24)
    zb = zn(b.reindex(full).ffill(limit=FFILL_M), min_periods=24)
    gap = (za - zb).dropna()                       # the construct, AS DEFINED
    out = dict(gap=name, definition=f"zn({cfg['a'][0]}) - zn({cfg['b'][0]})",
               n=int(len(gap)), note=cfg.get("note", ""), targets=[])
    for tsid, h in cfg["targets"]:
        spec = dict(kind="db_fwd_chg", tgt=tsid, h=h)
        tgt, h_steps = build_target(conn, spec, gap.index, "M")
        if tgt is None:
            out["targets"].append(dict(target=tsid, status="no_target"))
            continue
        d = pd.concat([gap.rename("g"), tgt.rename("t")], axis=1).dropna()
        if len(d) < 60:
            out["targets"].append(dict(target=tsid, status="insufficient"))
            continue
        g, t = d["g"], d["t"]
        # full-sample (transparent), monthly non-overlap, and purged
        # expanding-OOS mean signed IC — same shape as the LFI check Bob
        # found convincing.  Reported for BOTH sign conventions.
        full_r = float(g.corr(t, method="spearman"))
        idx = d.index
        keep = (np.arange(len(idx)) % h_steps == 0)
        no_r, _ = _ic(g.values[keep], t.values[keep])
        gv, tv = g.values, t.values
        ics = []
        for i in range(60, len(gv) - h_steps, h_steps):
            a_, b_ = gv[:i - h_steps], tv[:i - h_steps]
            if np.std(a_) > 0 and np.std(b_) > 0:
                sgn = np.sign(np.corrcoef(a_, b_)[0, 1])
                j = min(i + h_steps, len(gv))
                aa, bb = gv[i:j], tv[i:j]
                if len(aa) >= 2 and np.std(aa) > 0 and np.std(bb) > 0:
                    ics.append(sgn * np.corrcoef(aa, bb)[0, 1])
        oos_signed = float(np.nanmean(ics)) if ics else None
        out["targets"].append(dict(
            target=tsid, h_td=h, h_months=h_steps, n=int(len(d)),
            fullsample_rankIC=round(full_r, 3),
            nonoverlap_IC=round(no_r, 3) if no_r is not None else None,
            purged_OOS_signedIC=(round(oos_signed, 3)
                                 if oos_signed is not None else None),
            sign_resolved=("+gap" if (no_r or 0) >= 0 else "-gap"),
            verdict=("PREDICTS" if (oos_signed is not None
                     and abs(oos_signed) >= SKILL_FLOOR) else
                     "NO OOS (full-sample only)")))
    return out


# --------------------------------------------------------------------------
# 3. PAIRWISE INTERACTION SCREEN
# --------------------------------------------------------------------------
def _wf_light(X, y, h_steps, min_train=MIN_TRAIN_M, refit=24):
    """Ridge-only purged WF, non-overlap headline IC. Fast screen."""
    from sklearn.linear_model import RidgeCV
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import StandardScaler
    from sklearn.impute import SimpleImputer
    m = lambda: Pipeline([("imp", SimpleImputer(strategy="constant",
                                                fill_value=0.0)),
                          ("sc", StandardScaler()),
                          ("m", RidgeCV(alphas=[0.3, 1.0, 3.0, 10.0]))])
    n = len(y)
    if n < min_train + 2 * h_steps + 6:
        return None, 0
    op, ot, pos = [], [], []
    i = min_train
    while i < n:
        j = min(i + refit, n)
        te = i - h_steps
        if te < 60:
            i = j
            continue
        try:
            mdl = m().fit(X[:te], y[:te])
            op.extend(mdl.predict(X[i:j]).tolist())
            ot.extend(y[i:j].tolist())
            pos.extend(range(i, j))
        except Exception:
            pass
        i = j
    if len(op) < 10:
        return None, 0
    op, ot = np.asarray(op, float), np.asarray(ot, float)
    pos = np.asarray(pos, int)
    keep = (pos - pos[0]) % h_steps == 0
    ic, nn = _ic(op[keep], ot[keep])
    return ic, nn


def pair_screen(conn):
    # candidate composites + 2 noise controls, monthly grid.
    cols = {}
    for c in PAIR_CANDS:
        s = load_composite(conn, c)
        if s is not None and not s.empty:
            cols[c] = to_grid(s, "M")
    full = pd.DatetimeIndex([])
    for s in cols.values():
        full = full.union(s.index)
    full = full.sort_values()
    Z = pd.DataFrame(index=full)
    for c, s in cols.items():
        Z[c] = zn(s.reindex(full).ffill(limit=FFILL_M), min_periods=24)
    rng = np.random.default_rng(NOISE_SEED)
    for k in (1, 2):
        Z[f"NOISE{k}"] = zn(pd.Series(rng.standard_normal(len(full)),
                                      index=full), min_periods=24)
    names = list(cols) + ["NOISE1", "NOISE2"]

    results = []
    for tsid, h in PAIR_TARGETS:
        spec = dict(kind="db_fwd_chg", tgt=tsid, h=h)
        tgt, h_steps = build_target(conn, spec, full, "M")
        if tgt is None:
            continue
        ta = tgt.reindex(full)
        single = {}
        for nm in names:
            d = pd.concat([Z[nm].rename("x"), ta.rename("y")], axis=1).dropna()
            if len(d) < MIN_TRAIN_M:
                single[nm] = None
                continue
            ic, _ = _wf_light(d[["x"]].to_numpy(float),
                              d["y"].to_numpy(float), h_steps)
            single[nm] = ic
        pairs = list(combinations(names, 2))
        for x, y in pairs:
            d = pd.concat([Z[x].rename("x"), Z[y].rename("y"),
                           ta.rename("t")], axis=1).dropna()
            if len(d) < MIN_TRAIN_M + 2 * h_steps + 6:
                continue
            XY = d[["x", "y"]].to_numpy(float)
            tv = d["t"].to_numpy(float)
            ic_xy, n_xy = _wf_light(XY, tv, h_steps)
            inter = (d["x"] * d["y"]).to_numpy(float).reshape(-1, 1)
            ic_xyi, _ = _wf_light(np.hstack([XY, inter]), tv, h_steps)
            sx, sy = single.get(x), single.get(y)
            best_single = max([abs(v) for v in (sx, sy) if v is not None],
                              default=None)
            joint = max([abs(v) for v in (ic_xy, ic_xyi) if v is not None],
                        default=None)
            if best_single is None or joint is None:
                continue
            weak_alone = best_single < 0.12
            strong_together = joint >= 0.15 and joint >= best_single + 0.08
            results.append(dict(
                target=tsid, x=x, y=y,
                ic_x=round(sx, 3) if sx is not None else None,
                ic_y=round(sy, 3) if sy is not None else None,
                ic_xy=round(ic_xy, 3) if ic_xy is not None else None,
                ic_xy_inter=round(ic_xyi, 3) if ic_xyi is not None else None,
                best_single=round(best_single, 3), joint=round(joint, 3),
                lift=round(joint - best_single, 3),
                flag=("WEAK-ALONE/STRONG-TOGETHER"
                      if (weak_alone and strong_together) else
                      ("synergy" if strong_together else ""))))
    flagged = [r for r in results
               if r["flag"] == "WEAK-ALONE/STRONG-TOGETHER"]
    noise_ctrl = [r for r in results
                  if "NOISE1" in (r["x"], r["y"]) or "NOISE2" in (r["x"], r["y"])]
    noise_max = max([r["joint"] for r in noise_ctrl], default=None)
    return dict(n_pairs_tested=len(results),
                noise_pair_max_joint=noise_max,
                flagged=sorted(flagged, key=lambda r: -r["lift"]),
                synergy=sorted([r for r in results if r["flag"] == "synergy"],
                               key=lambda r: -r["lift"])[:15],
                all_results=results)


# --------------------------------------------------------------------------
def main():
    args = [a for a in sys.argv[1:]]
    conn = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    mode = args[0] if args else "all"

    if mode == "desc":
        code = args[1].upper()
        print(json.dumps(descriptive_track(conn, code, PILLARS[code]),
                         indent=2, default=str))
        conn.close()
        return
    if mode == "gap":
        nm = args[1].upper()
        print(json.dumps(gap_eval(conn, nm, GAPS[nm]), indent=2, default=str))
        conn.close()
        return
    if mode == "pairs":
        out = pair_screen(conn)
        OUT.parent.mkdir(parents=True, exist_ok=True)
        prev = json.loads(OUT.read_text()) if OUT.exists() else {}
        prev["pairs"] = out
        prev["generated"] = datetime.now().isoformat(timespec="seconds")
        OUT.write_text(json.dumps(prev, indent=2, default=str))
        print(f"pairs tested: {out['n_pairs_tested']}  "
              f"noise-pair max joint: {out['noise_pair_max_joint']}")
        print(f"WEAK-ALONE/STRONG-TOGETHER flagged: {len(out['flagged'])}")
        for r in out["flagged"][:20]:
            print(f"  {r['target']:<9} {r['x']:<5} x {r['y']:<7} "
                  f"alone(best)={r['best_single']:+.2f} "
                  f"together={r['joint']:+.2f} lift={r['lift']:+.2f}")
        conn.close()
        return

    if mode == "descall":
        desc = []
        for code, cfg in PILLARS.items():
            print(f"  desc .. {code}", flush=True)
            try:
                desc.append(descriptive_track(conn, code, cfg))
            except Exception as e:
                desc.append(dict(pillar=code, status=f"ERROR {e!r}"))
        conn.close()
        prev = json.loads(OUT.read_text()) if OUT.exists() else {}
        prev["descriptive"] = desc
        prev["descriptive_rerun"] = datetime.now().isoformat(timespec="seconds")
        OUT.write_text(json.dumps(prev, indent=2, default=str))
        print(f"\n{'Pillar':<7}{'Ref':<20}{'r_OOS':>7}{'bestSng':>8}"
              f"{'incr':>7}{'noise':>7}{'nOOS':>6}  Verdict  (ref excluded)")
        print("-" * 90)
        for d in desc:
            if d.get("status") != "ok":
                print(f"{d['pillar']:<7}{'':20}{d.get('status', '?')}")
                continue
            f = lambda v, w, p="+.2f": ("n/a".rjust(w) if v is None
                                        else format(v, p).rjust(w))
            ex = (d.get("excluded_ref_from_basket") or ["-"])[0]
            print(f"{d['pillar']:<7}{d.get('desc_ref', ''):<20}"
                  f"{f(d.get('r_oos'), 7)}{f(d.get('best_single'), 8)}"
                  f"{f(d.get('incremental'), 7)}"
                  f"{f(d.get('noise_ratio'), 7, '.2f')}"
                  f"{str(d.get('n_oos', '')):>6}  {d.get('verdict', '?'):<8} "
                  f"−{ex}")
        return

    # full registry
    desc = []
    for code, cfg in PILLARS.items():
        print(f"  desc .. {code}", flush=True)
        try:
            desc.append(descriptive_track(conn, code, cfg))
        except Exception as e:
            desc.append(dict(pillar=code, status=f"ERROR {e!r}"))
    gaps = []
    for nm, cfg in GAPS.items():
        print(f"  gap  .. {nm}", flush=True)
        try:
            gaps.append(gap_eval(conn, nm, cfg))
        except Exception as e:
            gaps.append(dict(gap=nm, status=f"ERROR {e!r}"))
    print("  pairs ..", flush=True)
    try:
        pairs = pair_screen(conn)
    except Exception as e:
        pairs = dict(status=f"ERROR {e!r}")
    conn.close()

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(dict(
        generated=datetime.now().isoformat(timespec="seconds"),
        descriptive=desc, gaps=gaps, pairs=pairs), indent=2, default=str))

    print("\n" + "=" * 104)
    print("DESCRIPTIVE TRACK  ·  OOS-honest concurrent tracking  ·  "
          f"{datetime.now():%Y-%m-%d %H:%M}")
    print("=" * 104)
    print(f"{'Pillar':<7}{'Ref':<18}{'r_OOS':>7}{'rankOOS':>8}"
          f"{'bestSng':>8}{'incr':>7}{'noise':>7}{'nOOS':>6}  Verdict")
    print("-" * 104)
    for d in desc:
        if d.get("status") != "ok":
            print(f"{d['pillar']:<7}{'':18}{d.get('status', '?')}")
            continue
        f = lambda v, w, p="+.2f": ("n/a".rjust(w) if v is None
                                    else format(v, p).rjust(w))
        print(f"{d['pillar']:<7}{d.get('desc_ref', ''):<18}"
              f"{f(d.get('r_oos'), 7)}{f(d.get('rank_oos'), 8)}"
              f"{f(d.get('best_single'), 8)}{f(d.get('incremental'), 7)}"
              f"{f(d.get('noise_ratio'), 7, '.2f')}"
              f"{str(d.get('n_oos', '')):>6}  {d.get('verdict', '?')}")
    print("-" * 104)
    print("REAL = adds over best single component · PROXY = is its best "
          "single in disguise · WEAK/BROKEN = doesn't track.")

    print("\n" + "=" * 104)
    print("DIVERGENCE CONSTRUCTS  ·  gap evaluated AS DEFINED (no reweight)")
    print("=" * 104)
    for g in gaps:
        if g.get("status"):
            print(f"{g['gap']}: {g['status']}")
            continue
        print(f"\n{g['gap']} = {g['definition']}   (n={g['n']})  {g['note']}")
        for t in g["targets"]:
            if t.get("status"):
                print(f"  -> {t['target']}: {t['status']}")
                continue
            print(f"  -> fwd {t['target']} {t['h_months']}m: "
                  f"full-rankIC {t['fullsample_rankIC']:+.2f} · "
                  f"non-ov IC {t['nonoverlap_IC']:+.2f} · "
                  f"purged-OOS {t['purged_OOS_signedIC']} · "
                  f"sign={t['sign_resolved']} · {t['verdict']}")

    print("\n" + "=" * 104)
    print("PAIRWISE INTERACTION  ·  weak-alone / strong-together")
    print("=" * 104)
    if pairs.get("status"):
        print(pairs["status"])
    else:
        print(f"pairs tested: {pairs['n_pairs_tested']}  ·  "
              f"NOISE-pair max joint IC: {pairs['noise_pair_max_joint']} "
              f"(false-discovery yardstick)")
        print(f"WEAK-ALONE/STRONG-TOGETHER: {len(pairs['flagged'])}")
        for r in pairs["flagged"][:20]:
            print(f"  {r['target']:<9} {r['x']:>5} x {r['y']:<7} "
                  f"alone≈{r['best_single']:+.2f} together={r['joint']:+.2f} "
                  f"lift={r['lift']:+.2f} (xy={r['ic_xy']}, "
                  f"+inter={r['ic_xy_inter']})")
        if not pairs["flagged"]:
            print("  (none cleared the bar — honest null is a result)")
    print(f"\nfull JSON -> {OUT}")


if __name__ == "__main__":
    main()
