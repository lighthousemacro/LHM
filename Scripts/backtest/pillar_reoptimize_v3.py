#!/usr/bin/env python3
"""
LHM Phase-B step 1 — dual-objective walk-forward pillar re-optimizer.

Resume anchor: Strategy/INDICATOR_MIGRATION_PROGRAM.md  (NEXT item).

What this does, per pillar, on the EXPANDED Tier-1 basket:

  features  = basket components, point-in-time zn-scored (expanding mean/std,
              neutral=0, winsorize +/-3 sigma) + 2 deterministic noise controls.
              Absent components impute to 0.0 = the neutral prior (matches the
              zn neutral=zero convention; avoids survivorship toward only the
              recent intersection of long+short series).
  target    = the pillar's WINNING (role, target) forward path, taken from the
              Phase-A macro-predictive result (NOT the role each composite was
              unfairly judged on in Phase A). e.g. LFI -> forward PAYEMS, PCI
              -> forward core PCE, not LFI -> recession / PCI -> DGS10.

  HONEST EVALUATION (this is the whole point — Macrosynergy/LdP discipline):
    * macro (db/recession) targets are evaluated on a MONTHLY grid, not a
      daily ffill grid. A 6-month overlapping target sampled daily is ~21x
      pseudo-replicated and a flexible model just fits the ffill plateaus.
    * PURGED/EMBARGOED walk-forward: the last `h` rows of every training
      block are dropped so a training row's forward window cannot bleed into
      the OOS block.
    * Headline OOS IC is computed on NON-OVERLAPPING OOS points (one per
      horizon). The overlapping figure is reported too, as a secondary.

  PREDICTIVE objective : purged walk-forward, expanding window, periodic
                         refit, inner TimeSeriesSplit(4), candidate zoo
                         {OLS, Ridge(alpha grid), ElasticNet(alpha,l1 grid)}
                         (impute->scale->model), model+hyperparams re-selected
                         each refit. Skill is OOS only, never in-sample R^2.
  DESCRIPTIVE objective: the fitted composite's CONCURRENT |r| vs the pillar's
                         ground-truth reference (PILLAR_DESCRIPTIVE_ANALYSIS).

  GATE (dual-objective, per INDICATOR_MIGRATION_PROGRAM lines 60-67):
    |OOS IC| < skill_floor (0.10)          -> DEMOTE to diagnostic (honest
                                              fallback; report descriptive
                                              weights, do not extrapolate noise)
    OOS IC ok AND |r_desc| >= 0.60         -> KEEP re-optimized weights
    OOS IC ok AND |r_desc| <  0.60         -> BLEND toward the descriptive
                                              composite; report the blend
                                              lambda that restores the floor

Output: Outputs/mri_optimization/pillar_reoptimize_v3.json + a printed
scorecard with new-vs-current weights, OOS IC (non-overlap headline +
overlap secondary), descriptive r, noise ratio, gate verdict.

DIAGNOSIS / PROPOSAL ONLY. Touches no canonical docs. Phase B reads this.

Run (env note: py3.14 has sklearn 1.8 / yfinance; conda python3 does NOT):
    /opt/homebrew/bin/python3.14 Scripts/backtest/pillar_reoptimize_v3.py
    /opt/homebrew/bin/python3.14 Scripts/backtest/pillar_reoptimize_v3.py PCI
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
from signal_eval import (  # noqa: E402
    DB,
    load_db_series,
    load_yf,
    load_composite,
    recession_target,
)

warnings.simplefilter("ignore")

OUT = Path("/Users/bob/LHM/Outputs/mri_optimization/pillar_reoptimize_v3.json")
SKILL_FLOOR = 0.10        # |OOS corr| below this => no real skill => demote
DESC_FLOOR = 0.60         # concurrent |r| floor for the descriptive objective
TD_PER_MONTH = 21         # trading days/month, to map h (trading days) -> months

# monthly evaluation grid (macro db/recession targets)
MIN_TRAIN_M = 120         # >=10y monthly before the first OOS block
REFIT_M = 12              # annual refit
# business-day grid (asset/ratio price targets)
MIN_TRAIN_B = 252 * 3     # 3y before first OOS
REFIT_B = 63              # ~quarterly refit
FFILL_M = 4               # monthly grid: carry quarterly inputs ~1 quarter
FFILL_B = 5               # business grid: bridge weekend/holiday gaps
NOISE_SEED = 42

LABOR = ["UEMP27OV", "UNRATE", "JTSQUR", "TEMPHELPS", "JTSHIR", "JTSJOL",
         "ICSA", "CCSA", "AHETPI", "ECIWAG", "FRBATLWGT12MMUMHGO",
         "U6RATE", "AWHAETP"]

# basket = raw observations series_ids (expanded Tier-1, migration spec).
# target = WINNING (role,target) from the Phase-A macro-pred result.
# desc   = (series_id, transform) concurrent ground-truth ref.
# current= last-round raw-id weights (PILLAR_DESCRIPTIVE_ANALYSIS) for the
#          new-vs-current diff; {} where no raw-id baseline exists (flagged).
PILLARS = {
    "LFI": dict(basket=LABOR,
        target=dict(role="macro-pred", kind="db_fwd_chg", tgt="PAYEMS", h=126, exp=-1),
        desc=("UNRATE", "level"), current={},
        note="flagship re-target: leads HIRING, not recession (Phase A)"),
    "LPI": dict(basket=LABOR,
        target=dict(role="macro-pred", kind="db_fwd_chg", tgt="PAYEMS", h=126, exp=+1),
        desc=("UNRATE", "level"),
        current={"UEMP27OV": .300, "UNRATE": .300, "JTSQUR": .140,
                 "TEMPHELPS": .123, "JTSHIR": .070, "JTSJOL": .067}),
    "LDI": dict(basket=LABOR,
        target=dict(role="macro-pred", kind="db_fwd_chg", tgt="PAYEMS", h=126, exp=+1),
        desc=("UNRATE", "level"), current={}),
    "PCI": dict(
        basket=["CPIAUCSL", "PCEPILFE", "TRMMEANCPIM158SFRBCLE", "CPILFESL",
                "CPIHOSSL", "PCEPI", "MEDCPIM158SFRBCLE", "PCETRIM12M159SFRBDAL",
                "STICKCPIM158SFRBATL", "CORESTICKM158SFRBATL", "T5YIE",
                "T10YIE", "T5YIFR", "MICH", "PPIFIS"],
        target=dict(role="macro-pred", kind="db_fwd_chg", tgt="PCEPILFE", h=126, exp=+1),
        desc=("PCEPILFE", "yoy"),
        current={"CPIAUCSL": .300, "PCEPILFE": .291, "TRMMEANCPIM158SFRBCLE": .291,
                 "CPILFESL": .059, "CPIHOSSL": .059},
        note="re-target: forward inflation, not DGS10, not concurrent gauge"),
    "GCI": dict(
        basket=["TCU", "INDPRO", "PAYEMS", "RSXFS", "MANEMP", "CFNAIMA3",
                "BBKMLEIX", "RPI", "PCEC96", "HOANBS"],
        target=dict(role="macro-pred", kind="db_fwd_chg", tgt="PAYEMS", h=126, exp=+1),
        desc=("CFNAIMA3", "level"),
        current={"TCU": .300, "INDPRO": .300, "PAYEMS": .184,
                 "RSXFS": .166, "MANEMP": .050},
        note="weak in Phase A (+0.09) — DEMOTE is a plausible verdict"),
    "HCI": dict(
        basket=["HOUST", "PERMIT", "MORTGAGE30US", "HSN1F", "MSACSR",
                "HOUST1F", "CSUSHPINSA", "MSPUS", "MORTGAGE15US", "DRSFRMACBS"],
        target=dict(role="macro-pred", kind="db_fwd_chg", tgt="INDPRO", h=126, exp=+1),
        desc=("CSUSHPINSA", "yoy"),
        current={"HOUST": .300, "PERMIT": .300, "MORTGAGE30US": .197,
                 "HSN1F": .101, "MSACSR": .101},
        note="Phase A flagged insufficient n — expanded basket may help"),
    "CCI": dict(
        basket=["PSAVERT", "REVOLSL", "DSPIC96", "RSXFS", "UMCSENT", "PCEDG",
                "PCEC96", "DRCCLACBS", "RPI", "TOTALSL", "TDSP", "DRCLACBS",
                "PSAVE"],
        target=dict(role="rel-pred", kind="ratio_fwd_ret", tgt="XLY/XLP", h=126, exp=+1),
        desc=("PCEC96", "yoy"),
        current={"PSAVERT": .300, "REVOLSL": .245, "DSPIC96": .187,
                 "RSXFS": .158, "UMCSENT": .057, "PCEDG": .052},
        note="Phase A real signal (IC +0.16 vs XLY/XLP rotation)"),
    "BCI": dict(
        basket=["NEWORDER", "GPDIC1", "BUSINV", "BUSLOANS", "ANDENO",
                "ANXAVS", "ACDGNO", "AMTMNO", "CAPB50001S", "DRTSCILM"],
        target=dict(role="macro-pred", kind="db_fwd_chg", tgt="INDPRO", h=126, exp=+1),
        desc=("NEWORDER", "yoy"),
        current={"NEWORDER": .300, "GPDIC1": .300, "BUSINV": .300, "BUSLOANS": .100}),
    "TCI": dict(
        basket=["DTWEXBGS", "BOPGSTB", "NETEXP", "DEXJPUS", "DEXCHUS",
                "DEXMXUS", "BOPTEXP", "BOPTIMP", "IQ", "IR"],
        target=dict(role="macro-pred", kind="db_fwd_chg", tgt="PCEPILFE", h=126, exp=None),
        desc=("DTWEXBGS", "yoy"),
        current={"DTWEXBGS": .333, "BOPGSTB": .333, "NETEXP": .333}),
    "FPI": dict(
        basket=["THREEFYTP10", "DGS10", "BAA10Y", "T10Y2Y", "DGS30",
                "DGS3MO", "T10Y3M", "GFDEBTN", "FDHBFIN"],
        target=dict(role="asset-pred", kind="db_fwd_chg", tgt="DGS10", h=126, exp=+1),
        desc=("THREEFYTP10", "level"),
        current={"THREEFYTP10": .300, "DGS10": .300, "BAA10Y": .276, "T10Y2Y": .124}),
    "FCI": dict(
        basket=["BAMLH0A0HYM2", "BAA10YM", "BAMLC0A0CM", "VIXCLS", "ANFCI",
                "AAA10Y", "DRALACBS", "CORCCACBS", "STLFSI4", "KCFSI"],
        target=dict(role="macro-pred", kind="db_fwd_chg", tgt="PAYEMS", h=126, exp=None),
        desc=("ANFCI", "level"),
        current={"BAMLH0A0HYM2": .300, "BAA10YM": .300, "BAMLC0A0CM": .300,
                 "VIXCLS": .100}),
    "LCI": dict(
        basket=["WTREGEN", "TOTRESNS", "WALCL", "RRPONTSYD", "SOFR", "IORB",
                "EFFR", "NYFED_TGCR", "OFR_MMF-MMF_RP_TOT-M", "OFR_MMF-MMF_TOT-M"],
        target=dict(role="macro-pred", kind="db_fwd_chg", tgt="BAMLH0A0HYM2", h=63, exp=-1),
        desc=("TOTRESNS", "yoy"),
        current={"WTREGEN": .300, "TOTRESNS": .300, "WALCL": .238,
                 "RRPONTSYD": .106, "SOFR": .056}),
    "MSI": dict(
        basket=["SPX_vs_200d_pct", "SPX_vs_50d_pct", "SPX_20d_slope",
                "SPX_Z_RoC_63d", "SPX_50d_slope", "SPX_PCT_ABOVE_50D",
                "SPX_PCT_ABOVE_20D", "SPX_PCT_ABOVE_200D", "SPX_NET_NEW_HIGHS",
                "SPX_AD_LINE", "SPX_MCCLELLAN_SUM", "SPX_BREADTH_THRUST"],
        target=dict(role="asset-pred", kind="asset_fwd_ret", tgt="SPY", h=63, exp=+1),
        desc=("SPX_vs_200d_pct", "level"),
        current={"SPX_vs_200d_pct": .300, "SPX_vs_50d_pct": .300,
                 "SPX_20d_slope": .270, "SPX_Z_RoC_63d": .072,
                 "SPX_50d_slope": .059},
        note="breadth components only ~3y (2023-02+) — long-window capped"),
    "SPI": dict(
        basket=["VIXCLS", "AAII_Bull_Bear_Spread", "VIX_percentile_252d",
                "AAII_Bullish", "AAII_Bearish", "AAII_Neutral",
                "VIX_vs_50d_pct", "VIX_BACKWARDATION"],
        target=dict(role="asset-pred", kind="asset_fwd_ret", tgt="SPY", h=63, exp=+1),
        desc=("AAII_Bull_Bear_Spread", "level"),
        current={"VIXCLS": .333, "AAII_Bull_Bear_Spread": .333,
                 "VIX_percentile_252d": .333}),
    "CLG": dict(basket=["BAMLH0A0HYM2"] + LABOR,
        target=dict(role="macro-pred", kind="db_fwd_chg", tgt="UNRATE", h=126, exp=None),
        desc=("UNRATE", "level"), current={},
        note="sign-convention audit: Phase A rankIC +0.30 but sign FLIP; "
             "let the model fit the sign, report it"),
    "MRI": dict(
        basket=["LPI", "PCI", "GCI", "HCI", "CCI", "BCI", "TCI", "FPI",
                "FCI", "LCI"],
        target=dict(role="macro-pred", kind="db_fwd_chg", tgt="UNRATE", h=252, exp=+1),
        desc=("UNRATE", "level"),
        current={"LPI": -.33, "PCI": .03, "GCI": -.02, "HCI": -.02,
                 "CCI": -.02, "BCI": -.13, "TCI": -.12, "FPI": .12,
                 "FCI": -.07, "LCI": -.14},
        composite_basket=True,
        note="history problem persists (Phase A) — flag small-n"),
}


# --------------------------------------------------------------------------
# point-in-time helpers
# --------------------------------------------------------------------------
def zn(s: pd.Series, thresh: float = 3.0, min_periods: int = 24) -> pd.Series:
    """Expanding z-score, neutral=0, winsorized +/-thresh. No look-ahead.
    min_periods is in grid steps (24 = 2y monthly / ~5wk daily warmup)."""
    m = s.expanding(min_periods=min_periods).mean()
    sd = s.expanding(min_periods=min_periods).std()
    z = (s - m) / sd.replace(0.0, np.nan)
    return z.clip(-thresh, thresh)


def yoy(s: pd.Series) -> pd.Series:
    return s.pct_change(12) * 100.0


def grid_of(kind: str) -> str:
    return "B" if kind in ("asset_fwd_ret", "ratio_fwd_ret") else "M"


def to_grid(s: pd.Series, grid: str) -> pd.Series:
    """Resample a native series onto the evaluation grid (period-end last)."""
    rule = "ME" if grid == "M" else "B"
    return s.resample(rule).last()


def build_target(conn, spec, idx, grid):
    """Forward target on the eval grid, point-in-time (signal_t vs t->t+h).

    Returns (target_series, h_steps) where h_steps is the horizon expressed
    in grid steps (months for 'M', trading days for 'B')."""
    kind, tgt, h = spec["kind"], spec["tgt"], spec["h"]
    h_steps = max(1, round(h / TD_PER_MONTH)) if grid == "M" else h
    if kind == "recession":
        return recession_target(idx, h), h_steps
    if kind == "db_fwd_chg":
        s = load_db_series(conn, tgt)
        if s is None or s.empty:
            return None, h_steps
        s = to_grid(s, grid).ffill(limit=FFILL_M if grid == "M" else FFILL_B)
        s = s.reindex(idx)
        return s.shift(-h_steps) - s, h_steps
    if kind in ("asset_fwd_ret", "ratio_fwd_ret"):
        if kind == "ratio_fwd_ret":
            a, b = tgt.split("/")
            pa, pb = load_yf(a), load_yf(b)
            if pa is None or pb is None:
                return None, h_steps
            p = (pa / pb.reindex(pa.index).ffill()).dropna()
        else:
            p = load_yf(tgt)
            if p is None:
                return None, h_steps
        p = to_grid(p, grid).ffill(limit=FFILL_B).reindex(idx)
        return p.shift(-h_steps) / p - 1.0, h_steps
    return None, h_steps


def build_desc_ref(conn, desc, idx, grid, znmp):
    sid, transform = desc
    s = load_db_series(conn, sid)
    if s is None or s.empty:
        return None
    if transform == "yoy":
        s = yoy(s)
    s = to_grid(s, grid).ffill(limit=FFILL_M if grid == "M" else FFILL_B)
    return zn(s.reindex(idx), min_periods=znmp)


# --------------------------------------------------------------------------
# walk-forward engine — purged, non-overlap-scored
# --------------------------------------------------------------------------
def candidate_zoo():
    from sklearn.linear_model import LinearRegression, Ridge, ElasticNet
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import StandardScaler
    from sklearn.impute import SimpleImputer
    # impute missing zn -> 0.0 (neutral prior) BEFORE scaling.
    base = lambda m: Pipeline([
        ("imp", SimpleImputer(strategy="constant", fill_value=0.0)),
        ("sc", StandardScaler()), ("m", m)])
    return {
        "ols": (base(LinearRegression()), {}),
        "ridge": (base(Ridge()), {"m__alpha": [0.3, 1.0, 3.0, 10.0]}),
        "enet": (base(ElasticNet(max_iter=5000)),
                 {"m__alpha": [0.01, 0.05, 0.2],
                  "m__l1_ratio": [0.2, 0.5, 0.8]}),
    }


def _select(Xtr, Ytr):
    from sklearn.model_selection import (TimeSeriesSplit, GridSearchCV,
                                         cross_val_score)
    inner = TimeSeriesSplit(n_splits=4)
    best, best_score = None, -np.inf
    for _, (pipe, grid) in candidate_zoo().items():
        try:
            if grid:
                gs = GridSearchCV(pipe, grid, cv=inner,
                                  scoring="neg_mean_squared_error", n_jobs=1)
                gs.fit(Xtr, Ytr)
                cand, score = gs.best_estimator_, gs.best_score_
            else:
                score = float(np.mean(cross_val_score(
                    pipe, Xtr, Ytr, cv=inner,
                    scoring="neg_mean_squared_error")))
                cand = pipe.fit(Xtr, Ytr)
        except Exception:
            continue
        if score > best_score:
            best, best_score = cand, score
    return best


def _ic(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    ok = np.isfinite(a) & np.isfinite(b)
    a, b = a[ok], b[ok]
    if len(a) < 8 or a.std() == 0 or b.std() == 0:
        return None, len(a)
    return float(np.corrcoef(a, b)[0, 1]), len(a)


def walk_forward(feat: pd.DataFrame, y: pd.Series, pnames: list,
                 h_steps: int, min_train: int, refit: int):
    """Purged expanding walk-forward.

    Training block for an OOS window starting at i is rows [0 : i - h_steps]
    (embargo of h_steps so a train row's forward target cannot reach into
    the OOS block). Headline OOS IC uses NON-OVERLAPPING OOS points (every
    h_steps-th), so a 6mo overlapping target is not counted ~h times.
    """
    cols = pnames + ["NOISE1", "NOISE2"]
    # require the TARGET present; features may be NaN (imputed to neutral 0).
    df = feat[cols].copy()
    df["__y"] = y
    df = df[np.isfinite(df["__y"])]
    n = len(df)
    if n < min_train + 2 * h_steps + 10:
        return dict(n=n, status="insufficient_overlap")

    X = df[cols].to_numpy(float)
    Y = df["__y"].to_numpy(float)

    oos_pred, oos_true, oos_pos = [], [], []
    i = min_train
    while i < n:
        j = min(i + refit, n)
        tr_end = i - h_steps                       # purge/embargo
        if tr_end < max(60, h_steps + 5):
            i = j
            continue
        best = _select(X[:tr_end], Y[:tr_end])
        if best is not None:
            try:
                best.fit(X[:tr_end], Y[:tr_end])
                oos_pred.extend(best.predict(X[i:j]).tolist())
                oos_true.extend(Y[i:j].tolist())
                oos_pos.extend(range(i, j))
            except Exception:
                pass
        i = j

    if len(oos_pred) < 12:
        return dict(n=n, n_oos=len(oos_pred), status="insufficient_oos")

    op = np.asarray(oos_pred, float)
    ot = np.asarray(oos_true, float)
    pos = np.asarray(oos_pos, int)
    ic_ov, _ = _ic(op, ot)                          # overlapping (secondary)
    # non-overlapping headline: keep one OOS point every h_steps.
    keep = (pos - pos[0]) % h_steps == 0
    ic_no, n_no = _ic(op[keep], ot[keep])
    rank_no = None
    if n_no >= 8:
        rk = pd.Series(op[keep]).corr(pd.Series(ot[keep]), method="spearman")
        rank_no = float(rk) if rk == rk else None
    sub_t, sub_p = ot[keep], op[keep]
    sign_acc = (float(np.mean(np.sign(sub_p - sub_p.mean())
                              == np.sign(sub_t - sub_t.mean())))
                if n_no >= 8 else None)

    fbest = _select(X, Y)
    if fbest is None:
        return dict(n=n, n_oos=len(op), oos_ic=ic_no, status="final_fit_failed")
    fbest.fit(X, Y)
    model_name = type(fbest.named_steps["m"]).__name__
    coef = np.ravel(getattr(fbest.named_steps["m"], "coef_",
                            np.zeros(len(cols))))
    sig_mass = float(np.abs(coef[:len(pnames)]).sum())
    noi_mass = float(np.abs(coef[len(pnames):]).sum())
    noise_ratio = (noi_mass / (sig_mass + noi_mass)
                   if (sig_mass + noi_mass) > 0 else None)
    raw_coef = {p: float(c) for p, c in zip(pnames, coef[:len(pnames)])}

    return dict(n=n, n_oos=len(op), n_oos_noov=n_no,
                oos_ic=ic_no, oos_ic_overlap=ic_ov,
                oos_rank_ic=rank_no, oos_sign_acc=sign_acc,
                final_model=model_name, noise_ratio=noise_ratio,
                raw_coef=raw_coef, status="ok")


# --------------------------------------------------------------------------
# dual-objective gate
# --------------------------------------------------------------------------
def normalize_weights(raw):
    tot = sum(abs(v) for v in raw.values())
    return ({k: 0.0 for k in raw} if tot == 0
            else {k: round(v / tot, 4) for k, v in raw.items()})


def comp_from_w(feat, pnames, w):
    ws = pd.Series({p: w.get(p, 0.0) for p in pnames})
    return (feat[pnames].fillna(0.0) * ws).sum(axis=1)


def descriptive_weights(feat, pnames, ref):
    """Concurrent ridge of zn-components -> zn-ref. A DESCRIPTIVE anchor
    (what the pillar should look like today), not a forecast — full-sample
    concurrent fit is the right object, matching PILLAR_DESCRIPTIVE_ANALYSIS."""
    from sklearn.linear_model import RidgeCV
    d = feat[pnames].fillna(0.0).copy()
    d["__r"] = ref
    d = d[np.isfinite(d["__r"])]
    if len(d) < 60:
        return None
    m = RidgeCV(alphas=[0.3, 1.0, 3.0, 10.0])
    m.fit(d[pnames].to_numpy(float), d["__r"].to_numpy(float))
    return {p: float(c) for p, c in zip(pnames, np.ravel(m.coef_))}


def concurrent_r(comp, ref):
    if ref is None:
        return None
    d = pd.concat([comp.rename("c"), ref.rename("r")], axis=1).dropna()
    if len(d) < 60 or d["c"].std() == 0:
        return None
    return float(d["c"].corr(d["r"]))


def apply_gate(wf, feat, pnames, ref):
    if wf.get("status") != "ok":
        return dict(verdict="DEMOTE", reason=wf.get("status"),
                    weights={}, desc_r=None, lam=None)
    if wf["oos_ic"] is None or abs(wf["oos_ic"]) < SKILL_FLOOR:
        dw = descriptive_weights(feat, pnames, ref) if ref is not None else None
        return dict(verdict="DEMOTE", reason="oos_ic<skill_floor",
                    weights=normalize_weights(dw) if dw else {},
                    desc_r=None, lam=None)

    pred_w = wf["raw_coef"]
    pred_comp = comp_from_w(feat, pnames, pred_w)
    r_pred = concurrent_r(pred_comp, ref)
    if r_pred is not None and abs(r_pred) >= DESC_FLOOR:
        return dict(verdict="KEEP", reason="meets both objectives",
                    weights=normalize_weights(pred_w),
                    desc_r=round(r_pred, 3), lam=1.0)

    dw = descriptive_weights(feat, pnames, ref) if ref is not None else None
    if dw is None or r_pred is None:
        return dict(verdict="DEMOTE", reason="no_descriptive_anchor",
                    weights=normalize_weights(pred_w),
                    desc_r=(round(r_pred, 3) if r_pred is not None else None),
                    lam=None)
    desc_comp = comp_from_w(feat, pnames, dw)
    for lam in [round(x, 2) for x in np.arange(1.0, -0.01, -0.05)]:
        rb = concurrent_r(lam * pred_comp + (1 - lam) * desc_comp, ref)
        if rb is not None and abs(rb) >= DESC_FLOOR:
            bw = {p: lam * pred_w.get(p, 0.0) + (1 - lam) * dw.get(p, 0.0)
                  for p in pnames}
            return dict(verdict="BLEND", reason=f"lambda={lam} restores floor",
                        weights=normalize_weights(bw),
                        desc_r=round(rb, 3), lam=lam)
    rb0 = concurrent_r(desc_comp, ref)
    return dict(verdict="DEMOTE", reason="descriptive_floor_unreachable",
                weights=normalize_weights(dw),
                desc_r=(round(rb0, 3) if rb0 is not None else None), lam=0.0)


# --------------------------------------------------------------------------
# driver
# --------------------------------------------------------------------------
def run_pillar(conn, code, cfg):
    composite = cfg.get("composite_basket", False)
    grid = grid_of(cfg["target"]["kind"])
    min_train = MIN_TRAIN_M if grid == "M" else MIN_TRAIN_B
    refit = REFIT_M if grid == "M" else REFIT_B
    znmp = 24 if grid == "M" else 252      # zn warmup: 2y monthly / 1y daily

    series, dropped = {}, []
    for sid in cfg["basket"]:
        s = load_composite(conn, sid) if composite else load_db_series(conn, sid)
        if s is None or s.empty:
            dropped.append(sid)
        else:
            series[sid] = to_grid(s, grid)
    if not series:
        return dict(pillar=code, status="no_components", dropped=dropped)

    full = pd.DatetimeIndex([])
    for s in series.values():
        full = full.union(s.index)
    full = full.sort_values()

    feat = pd.DataFrame(index=full)
    pnames = []
    ff = FFILL_M if grid == "M" else FFILL_B
    for sid, s in series.items():
        feat[sid] = zn(s.reindex(full).ffill(limit=ff), min_periods=znmp)
        pnames.append(sid)
    rng = np.random.default_rng(NOISE_SEED)
    for k in (1, 2):
        feat[f"NOISE{k}"] = zn(pd.Series(
            rng.standard_normal(len(full)), index=full), min_periods=znmp)

    sig_idx = feat[pnames].dropna(how="all").index
    tgt, h_steps = build_target(conn, cfg["target"], sig_idx, grid)
    if tgt is None or tgt.dropna().empty:
        return dict(pillar=code, status="no_target", dropped=dropped,
                    target=cfg["target"])
    ref = build_desc_ref(conn, cfg["desc"], sig_idx, grid, znmp)

    wf = walk_forward(feat, tgt, pnames, h_steps, min_train, refit)
    gate = apply_gate(wf, feat, pnames, ref)

    cur = cfg.get("current", {})
    new_w = gate["weights"]
    keys = sorted(set(list(cur) + list(new_w)),
                  key=lambda k: -abs(new_w.get(k, 0)))
    wtbl = [dict(series=k, current=cur.get(k), new=new_w.get(k, 0.0))
            for k in keys]

    exp = cfg["target"].get("exp")
    ic = wf.get("oos_ic")
    sign_ok = (None if exp is None or ic is None
               else bool(np.sign(ic) == np.sign(exp)))

    return dict(
        pillar=code, role=cfg["target"]["role"], target=cfg["target"]["tgt"],
        target_kind=cfg["target"]["kind"], horizon_td=cfg["target"]["h"],
        eval_grid=grid, h_steps=h_steps, exp_sign=exp, sign_ok=sign_ok,
        desc_ref=f"{cfg['desc'][0]}({cfg['desc'][1]})",
        status=wf.get("status"), n=wf.get("n"),
        n_oos=wf.get("n_oos"), n_oos_noov=wf.get("n_oos_noov"),
        oos_ic=(round(ic, 3) if ic is not None else None),
        oos_ic_overlap=(round(wf["oos_ic_overlap"], 3)
                        if wf.get("oos_ic_overlap") is not None else None),
        oos_rank_ic=(round(wf["oos_rank_ic"], 3)
                     if wf.get("oos_rank_ic") is not None else None),
        oos_sign_acc=(round(wf["oos_sign_acc"], 3)
                      if wf.get("oos_sign_acc") is not None else None),
        final_model=wf.get("final_model"),
        noise_ratio=(round(wf["noise_ratio"], 3)
                     if wf.get("noise_ratio") is not None else None),
        verdict=gate["verdict"], gate_reason=gate["reason"],
        desc_r=gate["desc_r"], blend_lambda=gate["lam"],
        weights=wtbl, dropped=dropped, note=cfg.get("note", ""))


def fmt(v, w, p="+.2f"):
    return ("n/a".rjust(w) if v is None else format(v, p).rjust(w))


def main():
    only = sys.argv[1].upper() if len(sys.argv) > 1 else None
    conn = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    results = []
    for code, cfg in PILLARS.items():
        if only and code != only:
            continue
        print(f"  .. {code}", flush=True)
        try:
            results.append(run_pillar(conn, code, cfg))
        except Exception as e:
            results.append(dict(pillar=code, status=f"ERROR: {e!r}"))
    conn.close()

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(
        dict(generated=datetime.now().isoformat(timespec="seconds"),
             skill_floor=SKILL_FLOOR, desc_floor=DESC_FLOOR,
             method="purged WF, monthly grid for macro, non-overlap OOS IC",
             results=results), indent=2))

    print("\n" + "=" * 116)
    print("LHM PILLAR RE-OPTIMIZER v3  ·  purged WF · non-overlap OOS IC  ·  "
          f"{datetime.now():%Y-%m-%d %H:%M}")
    print("=" * 116)
    print(f"{'Pillar':<7}{'Role':<11}{'Target':<12}{'grid':>5}{'OOS IC':>8}"
          f"{'(ov)':>7}{'rankIC':>8}{'descR':>7}{'noise':>7}{'nNO':>5}"
          f"  {'Verdict':<8} sign")
    print("-" * 116)
    for r in results:
        if "oos_ic" not in r:
            print(f"{r['pillar']:<7}{'':30}{r.get('status', '?')}")
            continue
        so = ("" if r.get("sign_ok") is None
              else ("ok" if r["sign_ok"] else "FLIP"))
        print(f"{r['pillar']:<7}{r.get('role', ''):<11}"
              f"{str(r.get('target', '')):<12}{r.get('eval_grid', ''):>5}"
              f"{fmt(r.get('oos_ic'), 8)}{fmt(r.get('oos_ic_overlap'), 7)}"
              f"{fmt(r.get('oos_rank_ic'), 8)}{fmt(r.get('desc_r'), 7)}"
              f"{fmt(r.get('noise_ratio'), 7, '.2f')}"
              f"{str(r.get('n_oos_noov', '')):>5}  "
              f"{r.get('verdict', '?'):<8} {so}")
    print("-" * 116)
    print("OOS IC = NON-OVERLAPPING walk-forward out-of-sample corr (headline)."
          "  (ov) = overlapping, inflated, shown for contrast.")
    print("descR = concurrent |r| vs ground-truth ref.  Verdict: KEEP / "
          "BLEND lambda / DEMOTE (no OOS skill).  nNO = non-overlap OOS n.")
    print(f"detail + new-vs-current weights -> {OUT}")


if __name__ == "__main__":
    main()
