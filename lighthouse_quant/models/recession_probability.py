"""
Recession Probability Model (Model B, adopted 2026-07-25)
=========================================================
Walk-forward fitted logistic recession model. Replaces the hand-set
coefficient model calibrated 2026-01-19, per the July 2026 regime-model
study (/Users/bob/LHM/Working/regime_model_2026_07/REGIME_MODEL_REPORT.md).

Why the old model was retired:
    - Its 4.0 coefficient on the (since 2026-06-15) unit-variance MRI
      saturated the sigmoid: the raw model flipped between ~0 and ~1
      daily, and the stored REC_PROB was a 63-trading-day rolling-mean
      bandage over that defect.
    - Its curve term divided a percentage-point series by 100, leaving
      the one input with stable cross-sample coefficients effectively
      disconnected.
    - Inputs were fillna(0): missing data silently read as neutral.

Model B architecture (identical to the study protocol, seed 42):
    - Same four inputs: MRI, 10y-3m curve, HY OAS z, inverted quits z.
    - Monthly month-end panel with point-in-time availability rules
      (JOLTS quits lagged by publication delay; no fillna(0) — training
      median imputation with availability flags).
    - L2 logistic regression, C chosen by TimeSeriesSplit log-loss CV
      inside the training window only. Training from 2002-01.
    - Annual January refits. The model in force at any date is the most
      recent January 31 refit on or before it. Embargo: a row enters
      training only if its label was knowable at the refit date.
    - Horizons: 6m and 12m, published as REC_PROB_6M and REC_PROB.
    - History is walk-forward from 2010-02 (first OOS month after the
      first January 2010 refit). No pre-2010 values are emitted: the
      old 1990-2010 history came from the defective model and is retired.

Guardrail for any write-up: this is a calibration fix, not a claim of
recession-forecasting skill. The 2010+ OOS window contains one recession.
"""

import sqlite3
import warnings
from dataclasses import dataclass
from typing import Dict

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss
from sklearn.model_selection import TimeSeriesSplit
from sklearn.preprocessing import StandardScaler

from lighthouse_quant.config import NBER_RECESSIONS, DB_PATH

SEED = 42
TRAIN_START = pd.Timestamp("2002-01-31")
PANEL_START = pd.Timestamp("1997-01-31")
FIRST_REFIT_YEAR = 2010
JOLTS_LAG_DAYS = 35  # PUBLICATION_LAGS convention (JOLTS ~40d after ref month)
FEATURES = ["mri", "curve_10y3m", "hy_oas_z", "quits_inv"]
AVAIL_FLAGS = ["mri_avail", "quits_inv_avail"]
C_GRID = [0.001, 0.01, 0.1, 1.0, 10.0, 100.0]
HORIZONS = (6, 12)


@dataclass
class RecessionProbabilityResult:
    """Results from recession probability model."""
    date: str
    probability_12m: float  # Probability of recession in next 12 months
    probability_6m: float   # Probability of recession in next 6 months
    probability_3m: float   # Not modeled by Model B; always NaN (kept for API compat)
    regime: str             # Current regime classification
    key_drivers: Dict[str, float]  # Standardized coefficient x feature contribution
    confidence: str         # Model confidence level


def create_recession_forward_target(index: pd.DatetimeIndex, horizon_months: int = 12) -> pd.Series:
    """Forward-looking recession-start indicator (kept for API compatibility)."""
    recession_starts = [pd.Timestamp(start) for start, _ in NBER_RECESSIONS]
    target = pd.Series(0, index=index, name=f"recession_next_{horizon_months}m")
    for date in index:
        horizon_end = date + pd.DateOffset(months=horizon_months)
        for rec_start in recession_starts:
            if date < rec_start <= horizon_end:
                target.loc[date] = 1
                break
    return target


def sigmoid(x: np.ndarray) -> np.ndarray:
    """Logistic sigmoid function (kept for API compatibility)."""
    return 1 / (1 + np.exp(-np.clip(x, -500, 500)))


def classify_regime(p12: float) -> str:
    if pd.isna(p12):
        return "NO DATA"
    if p12 > 0.7:
        return "HIGH RISK"
    if p12 > 0.4:
        return "ELEVATED"
    if p12 > 0.2:
        return "MODERATE"
    return "LOW RISK"


class RecessionProbabilityModel:
    """
    Model B: walk-forward fitted L2 logistic on the core four inputs.

    The heavy lifting (panel build, per-January refits) happens once per
    instance and is cached, so predict()/predict_history() are cheap.
    """

    def __init__(self, conn: sqlite3.Connection = None):
        self.conn = conn or sqlite3.connect(DB_PATH)
        self._panel = None
        self._fits = {}  # (refit_year, horizon) -> (clf, scaler, med, cols, info)

    # ------------------------------------------------------------- data --
    def _load_index(self, index_id):
        df = pd.read_sql(
            "SELECT date, value FROM lighthouse_indices WHERE index_id=? ORDER BY date",
            self.conn, params=(index_id,), parse_dates=["date"])
        return df.set_index("date")["value"].dropna()

    def _load_horizon(self, col):
        df = pd.read_sql(f"SELECT date, {col} FROM horizon_dataset ORDER BY date",
                         self.conn, parse_dates=["date"])
        return df.set_index("date")[col].dropna()

    def _load_obs(self, sid):
        df = pd.read_sql(
            "SELECT date, value FROM observations WHERE series_id=? ORDER BY date",
            self.conn, params=(sid,), parse_dates=["date"])
        return df.set_index("date")["value"].dropna()

    @staticmethod
    def _asof(series, t):
        s = series.loc[:t]
        return s.iloc[-1] if len(s) else np.nan

    def _quits_availability(self):
        """Quits z by AVAILABILITY date: reference month M becomes available
        at M month-end + JOLTS_LAG_DAYS. Only reference months with a raw
        published JTSQUR print count (no nowcast splice)."""
        z_daily = self._load_horizon("JOLTS_Quits_Rate_z")
        monthly = z_daily.resample("MS").first().dropna()
        published = self._load_obs("JTSQUR")
        monthly = monthly[monthly.index.isin(published.index)]
        avail = monthly.index + pd.DateOffset(months=1) + pd.Timedelta(days=JOLTS_LAG_DAYS)
        return pd.Series(monthly.values, index=avail).sort_index()

    def build_panel(self, asof_date: pd.Timestamp = None) -> pd.DataFrame:
        """Month-end panel of the core four features + rec_within labels.
        Includes one extra partial-month row at asof_date (features as-of
        that day) so the live read updates daily between month-ends."""
        if self._panel is not None:
            return self._panel
        asof_date = asof_date or pd.Timestamp.today().normalize()
        last_complete = asof_date.replace(day=1) - pd.Timedelta(days=1)
        idx = pd.date_range(PANEL_START, last_complete, freq="ME")
        if asof_date > last_complete:
            idx = idx.append(pd.DatetimeIndex([asof_date]))

        panel = pd.DataFrame(index=idx)
        mri = self._load_index("MRI")
        curve = self._load_horizon("Curve_10Y_3M")
        hy = self._load_horizon("HY_OAS_z")
        quits_avail = self._quits_availability()

        panel["mri"] = [self._asof(mri, t) for t in idx]
        panel["curve_10y3m"] = [self._asof(curve, t) for t in idx]
        panel["hy_oas_z"] = [self._asof(hy, t) for t in idx]
        qv = [self._asof(quits_avail, t) for t in idx]
        panel["quits_inv"] = [-v if not pd.isna(v) else np.nan for v in qv]
        for col in ("mri", "quits_inv"):
            panel[f"{col}_avail"] = panel[col].notna().astype(float)

        # labels: USREC==1 within the next h months (exclusive of current),
        # 0 only when all h future months are observed and zero, else NaN
        usrec = self._load_obs("USREC")
        month_starts = idx.to_period("M").to_timestamp().unique()
        ext = pd.date_range(month_starts[0],
                            month_starts[-1] + pd.DateOffset(months=12), freq="MS")
        u = usrec.reindex(ext)
        for h in HORIZONS:
            fwd = pd.concat([u.shift(-k) for k in range(1, h + 1)], axis=1)
            any1 = (fwd == 1).any(axis=1)
            full = fwd.notna().all(axis=1)
            tgt = pd.Series(np.nan, index=ext)
            tgt[any1] = 1.0
            tgt[(~any1) & full] = 0.0
            tgt = tgt.reindex(idx.to_period("M").to_timestamp())
            panel[f"rec_within_{h}m"] = tgt.values
        self._panel = panel
        return panel

    # -------------------------------------------------------- estimation --
    @staticmethod
    def _cv_choose_C(Xtr, ytr):
        n_splits = min(5, max(2, len(ytr) // 24))
        tss = TimeSeriesSplit(n_splits=n_splits)
        best_C, best_ll = C_GRID[0], np.inf
        for C in C_GRID:
            lls = []
            for tr_idx, va_idx in tss.split(Xtr):
                if len(np.unique(ytr[tr_idx])) < 2:
                    continue
                clf = LogisticRegression(C=C, solver="lbfgs",
                                         max_iter=2000, random_state=SEED)
                clf.fit(Xtr[tr_idx], ytr[tr_idx])
                pv = clf.predict_proba(Xtr[va_idx])[:, 1].clip(1e-6, 1 - 1e-6)
                lls.append(log_loss(ytr[va_idx], pv, labels=[0, 1]))
            if lls and np.mean(lls) < best_ll:
                best_ll, best_C = float(np.mean(lls)), C
        return best_C

    def _fit_in_force(self, refit_year: int, h: int):
        """Fit (and cache) the January refit for a given year and horizon."""
        key = (refit_year, h)
        if key in self._fits:
            return self._fits[key]
        panel = self.build_panel()
        refit_date = pd.Timestamp(refit_year, 1, 31)
        cols = FEATURES + AVAIL_FLAGS
        ycol = f"rec_within_{h}m"
        cutoff = refit_date - pd.DateOffset(months=h + 1)  # embargo
        tr = panel.loc[(panel.index >= TRAIN_START) & (panel.index <= cutoff)]
        tr = tr[tr[ycol].notna()]
        if len(tr) < 36 or tr[ycol].nunique() < 2:
            raise RuntimeError(f"insufficient training data for {refit_year} h={h}")
        med = tr[cols].median()
        Xtr_raw = tr[cols].fillna(med).values
        ytr = tr[ycol].astype(int).values
        scaler = StandardScaler().fit(Xtr_raw)
        clf = LogisticRegression(C=self._cv_choose_C(scaler.transform(Xtr_raw), ytr),
                                 solver="lbfgs", max_iter=2000, random_state=SEED)
        clf.fit(scaler.transform(Xtr_raw), ytr)
        info = {"refit": str(refit_date.date()), "n_train": int(len(tr)),
                "n_pos": int(ytr.sum()), "C": float(clf.C)}
        self._fits[key] = (clf, scaler, med, cols, info)
        return self._fits[key]

    @staticmethod
    def _refit_year_for(date: pd.Timestamp) -> int:
        """Most recent January 31 refit on or before date."""
        y = date.year if date >= pd.Timestamp(date.year, 1, 31) else date.year - 1
        return max(y, FIRST_REFIT_YEAR)

    def _predict_rows(self, rows: pd.DataFrame, refit_year: int, h: int):
        clf, scaler, med, cols, _ = self._fit_in_force(refit_year, h)
        X = rows[cols].fillna(med).values
        return clf.predict_proba(scaler.transform(X))[:, 1]

    # ------------------------------------------------------------ public --
    def predict(self, date: str = None) -> RecessionProbabilityResult:
        """Predict recession probability as of a date (default: latest row)."""
        panel = self.build_panel()
        date = pd.Timestamp(date) if date is not None else panel.index.max()
        avail = panel.index[panel.index <= date]
        if len(avail) == 0:
            raise ValueError(f"No panel data available for {date}")
        t = avail.max()
        refit_year = self._refit_year_for(t)
        row = panel.loc[[t]]
        p12 = float(self._predict_rows(row, refit_year, 12)[0])
        p6 = float(self._predict_rows(row, refit_year, 6)[0])

        # driver contributions from the 12m in-force model (standardized units)
        clf, scaler, med, cols, _ = self._fit_in_force(refit_year, 12)
        x_std = scaler.transform(row[cols].fillna(med).values)[0]
        contrib = clf.coef_[0] * x_std
        core = {c: contrib[i] for i, c in enumerate(cols) if c in FEATURES}
        total = sum(abs(v) for v in core.values()) or 1.0
        key_drivers = {
            "MRI": core["mri"] / total,
            "Yield Curve": core["curve_10y3m"] / total,
            "Credit Spreads": core["hy_oas_z"] / total,
            "Labor Flows": core["quits_inv"] / total,
        }
        n_valid = int(row[FEATURES].notna().sum(axis=1).iloc[0])
        confidence = "HIGH" if n_valid >= 4 else ("MEDIUM" if n_valid >= 2 else "LOW")
        return RecessionProbabilityResult(
            date=t.strftime("%Y-%m-%d"),
            probability_12m=round(p12, 4),
            probability_6m=round(p6, 4),
            probability_3m=float("nan"),
            regime=classify_regime(p12),
            key_drivers=key_drivers,
            confidence=confidence,
        )

    def predict_history(self, start_date: str = "2010-02-01") -> pd.DataFrame:
        """Walk-forward monthly history: each month scored by the model in
        force at that month (latest January refit before it). Starts at the
        first OOS month after the first refit; earlier dates are not emitted."""
        panel = self.build_panel()
        start = max(pd.Timestamp(start_date),
                    pd.Timestamp(FIRST_REFIT_YEAR, 1, 31) + pd.Timedelta(days=1))
        rows = panel.loc[panel.index >= start]
        if rows.empty:
            return pd.DataFrame()
        out = {"date": [], "prob_12m": [], "prob_6m": []}
        for year, grp in rows.groupby(rows.index.map(self._refit_year_for)):
            p12 = self._predict_rows(grp, year, 12)
            p6 = self._predict_rows(grp, year, 6)
            out["date"].extend(grp.index)
            out["prob_12m"].extend(p12)
            out["prob_6m"].extend(p6)
        df = pd.DataFrame(out).sort_values("date").reset_index(drop=True)
        df["prob_3m"] = np.nan
        df["regime"] = [classify_regime(p) for p in df["prob_12m"]]
        actual = create_recession_forward_target(
            pd.DatetimeIndex(df["date"]), horizon_months=12)
        df["actual_recession"] = actual.values
        df["date"] = df["date"].dt.strftime("%Y-%m-%d")
        return df

    def calibrate(self, start_date: str = "2002-01-01") -> Dict:
        """Model B refits itself every January; there is no separate grid
        search. Returns the current in-force fit info for inspection."""
        year = self._refit_year_for(pd.Timestamp.today().normalize())
        info = {}
        for h in HORIZONS:
            _, _, _, _, fit_info = self._fit_in_force(year, h)
            info[f"h{h}"] = fit_info
        return info

    def evaluate(self, start_date: str = "2010-02-01") -> Dict:
        """Walk-forward evaluation over the emitted history. One recession
        in the window: report metrics, claim nothing."""
        history = self.predict_history(start_date)
        if len(history) < 10:
            return {"error": "Insufficient data for evaluation"}
        y_true = history["actual_recession"].values
        y_prob = history["prob_12m"].values
        y_pred = (y_prob > 0.4).astype(int)
        tp = int(((y_pred == 1) & (y_true == 1)).sum())
        fp = int(((y_pred == 1) & (y_true == 0)).sum())
        fn = int(((y_pred == 0) & (y_true == 1)).sum())
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        return {
            "n_samples": len(history),
            "n_positive": int(y_true.sum()),
            "base_rate": round(float(y_true.mean()), 4),
            "threshold": 0.4,
            "precision": round(precision, 3),
            "recall": round(recall, 3),
            "false_alarm_months": fp,
            "note": "Single-recession OOS window. Calibration fix, not a skill claim.",
        }


def compute_recession_probabilities(conn: sqlite3.Connection = None) -> pd.DataFrame:
    """
    Walk-forward 12m and 6m probabilities as daily series.

    Monthly walk-forward values are carried forward daily (a month-end
    reading is the standing estimate until the next one), and the final
    row is today's model-in-force read on current-month features. No
    rolling-mean smoothing: Model B does not need the 63-day bandage.

    Returns a DataFrame indexed by date with columns REC_PROB (12m) and
    REC_PROB_6M. History starts 2010-02 (first walk-forward month).
    """
    model = RecessionProbabilityModel(conn)
    history = model.predict_history()
    if history.empty:
        return pd.DataFrame(columns=["REC_PROB", "REC_PROB_6M"])
    df = history.set_index(pd.to_datetime(history["date"]))[["prob_12m", "prob_6m"]]
    daily_idx = pd.date_range(df.index.min(), df.index.max(), freq="D")
    daily = df.reindex(daily_idx).ffill()
    daily.columns = ["REC_PROB", "REC_PROB_6M"]
    return daily


def compute_recession_probability(conn: sqlite3.Connection = None) -> pd.Series:
    """12m walk-forward probability as a daily Series (back-compat wrapper)."""
    daily = compute_recession_probabilities(conn)
    if daily.empty:
        return pd.Series(dtype=float, name="REC_PROB")
    s = daily["REC_PROB"].copy()
    s.name = "REC_PROB"
    return s


# CLI interface
if __name__ == "__main__":
    import sys

    conn = sqlite3.connect(DB_PATH)
    model = RecessionProbabilityModel(conn)

    if len(sys.argv) > 1 and sys.argv[1] == "--calibrate":
        print("Current in-force January refits:")
        for h, info in model.calibrate().items():
            print(f"  {h}: {info}")
    elif len(sys.argv) > 1 and sys.argv[1] == "--evaluate":
        metrics = model.evaluate()
        for k, v in metrics.items():
            print(f"  {k}: {v}")
    else:
        result = model.predict()
        print(f"\nRecession Probability Model B - {result.date}")
        print("=" * 50)
        print(f"12-Month Probability: {result.probability_12m:.1%}")
        print(f"6-Month Probability:  {result.probability_6m:.1%}")
        print(f"Regime: {result.regime}")
        print(f"Confidence: {result.confidence}")
        print("\nKey Drivers (12m, standardized contributions):")
        for driver, contrib in result.key_drivers.items():
            print(f"  {driver}: {contrib:+.1%}")

    conn.close()
