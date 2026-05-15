#!/usr/bin/env python3
"""
LIGHTHOUSE MACRO - PROPRIETARY INDEX COMPUTATION
=================================================
Computes all proprietary indices from horizon_dataset and writes to lighthouse_indices table.

Indices computed:
    - LFI (Labor Fragility Index)
    - LCI (Liquidity Cushion Index)
    - CLG (Credit-Labor Gap)
    - MRI (Macro Risk Index) - master composite
    - SLI (Stablecoin Liquidity Impulse) - placeholder, needs crypto data
    - RMP_Index (Reserve Management Purchases) - placeholder, needs Treasury data
    - Pillar Composites (LPI, PCI, GCI, HCI, CCI, BCI, TCI, GCI_Gov, FCI)
    - Additional: LDI, YFS, SVI, EMD, LIQ_STAGE, BILL_SOFR

Formulas from: Lighthouse_Macro_Trading_Strategy.pdf

Usage:
    python compute_indices.py              # Compute all indices, backfill history
    python compute_indices.py --latest     # Only compute latest date
    python compute_indices.py --verify     # Verify against expected thresholds
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import sys
import os

# Add lighthouse package to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# Add lighthouse_quant to path
sys.path.insert(0, "/Users/bob/LHM")

from lighthouse.config import DB_PATH as CONFIG_DB_PATH
from lighthouse_quant.models.recession_probability import compute_recession_probability
from lighthouse_quant.models.warning_system import WarningSystem, WarningLevel
from lighthouse_quant.models.risk_ensemble import RiskEnsemble, compute_ensemble_risk

# Override DB_PATH to use the correct database with horizon_dataset
DB_PATH = Path("/Users/bob/LHM/Data/databases/Lighthouse_Master.db")

# ==========================================
# STATUS THRESHOLDS
# ==========================================

STATUS_THRESHOLDS = {
    # Core Indices
    "LFI": [
        (1.5, "CRITICAL"),
        (1.0, "HIGH"),
        (0.5, "ELEVATED"),
        (0.0, "NEUTRAL"),
        (-999, "HEALTHY")
    ],
    "LCI": [
        (1.0, "ABUNDANT"),
        (0.5, "AMPLE"),
        (-0.5, "TIGHT"),
        (-1.0, "SCARCE"),
        (-999, "STRESS RISK")
    ],
    "CLG": [
        (1.0, "SPREADS WIDE"),
        (0.0, "NEUTRAL"),
        (-1.0, "MISPRICED"),
        (-999, "SEVERELY MISPRICED")
    ],
    "MRI": [
        # Recalibrated thresholds based on actual MRI distribution (2026-01-19)
        # Cycle-based naming convention for economic regimes
        # Thresholds based on percentile analysis:
        #   Recession: top 1% (>0.50)
        #   Pre-Recession: 90th-99th percentile (0.25-0.50)
        #   Late Cycle: 75th-90th percentile (0.10-0.25)
        #   Mid-Cycle: 25th-75th percentile (-0.20 to 0.10)
        #   Early Expansion: bottom 25% (<-0.20)
        (0.50, "RECESSION"),
        (0.25, "PRE-RECESSION"),
        (0.10, "LATE CYCLE"),
        (-0.20, "MID-CYCLE"),
        (-999, "EARLY EXPANSION")
    ],
    "SLI": [
        (1.0, "EXPANDING"),
        (0.0, "NEUTRAL"),
        (-0.5, "CONTRACTING"),
        (-999, "SEVERELY CONTRACTING")
    ],
    # Pillar Composites (positive = good, negative = weak)
    "LPI": [
        (1.0, "BOOM"),
        (0.5, "HEALTHY"),
        (-0.5, "NEUTRAL"),
        (-1.0, "WEAK"),
        (-999, "CRISIS")
    ],
    "PCI": [
        (1.5, "INFLATION CRISIS"),
        (1.0, "HIGH INFLATION"),
        (0.5, "ELEVATED"),
        (-0.5, "ON TARGET"),
        (-999, "DEFLATIONARY")
    ],
    "GCI": [
        (1.0, "STRONG GROWTH"),
        (0.5, "ABOVE TREND"),
        (-0.5, "TREND"),
        (-1.0, "BELOW TREND"),
        (-999, "CONTRACTION")
    ],
    "HCI": [
        (1.0, "HOUSING BOOM"),
        (0.5, "HEALTHY"),
        (-0.5, "FROZEN"),
        (-1.0, "WEAK"),
        (-999, "CRISIS")
    ],
    "CCI": [
        (1.0, "CONSUMER BOOM"),
        (0.5, "HEALTHY"),
        (-0.5, "FATIGUED"),
        (-1.0, "STRESSED"),
        (-999, "CRISIS")
    ],
    "BCI": [
        (1.0, "BUSINESS BOOM"),
        (0.5, "EXPANSION"),
        (-0.5, "SLOWING"),
        (-1.0, "CONTRACTION"),
        (-999, "CRISIS")
    ],
    "TCI": [
        (1.0, "TRADE TAILWIND"),
        (0.5, "FAVORABLE"),
        (-0.5, "NEUTRAL"),
        (-1.0, "HEADWIND"),
        (-999, "TRADE CRISIS")
    ],
    "FPI": [
        (1.5, "FISCAL CRISIS"),
        (1.0, "HIGH STRESS"),
        (0.5, "ELEVATED"),
        (-0.5, "NORMAL"),
        (-999, "FISCAL HEALTH")
    ],
    "FCI": [
        (1.0, "VERY LOOSE"),
        (0.5, "LOOSE"),
        (-0.5, "NEUTRAL"),
        (-1.0, "TIGHT"),
        (-999, "CRISIS")
    ],
    # Additional Indicators
    "LDI": [
        (1.0, "HIGH DYNAMISM"),
        (0.5, "HEALTHY"),
        (-0.5, "SLUGGISH"),
        (-1.0, "FROZEN"),
        (-999, "CRISIS")
    ],
    "YFS": [
        (1.0, "HIGH STRESS"),
        (0.5, "ELEVATED"),
        (-0.5, "NORMAL"),
        (-999, "LOW STRESS")
    ],
    "SVI": [
        (2.0, "EXTREME COMPLACENCY"),
        (1.0, "COMPLACENT"),
        (-1.0, "BALANCED"),
        (-999, "STRESSED")
    ],
    "EMD": [
        (1.0, "OVERBOUGHT"),
        (0.0, "NEUTRAL"),
        (-1.0, "OVERSOLD"),
        (-999, "EXTREMELY OVERSOLD")
    ],
    "LIQ_STAGE": [
        (6.5, "STAGE 7 - LIQUIDATIONS"),
        (5.5, "STAGE 6 - BASIS COLLAPSE"),
        (4.5, "STAGE 5 - STABLECOIN STALL"),
        (3.5, "STAGE 4 - COLLATERAL STRESS"),
        (2.5, "STAGE 3 - SRF USAGE"),
        (1.5, "STAGE 2 - RESERVE DRAIN"),
        (-999, "STAGE 1 - RRP DEPLETION")
    ],
    "BILL_SOFR": [
        (0.10, "BILLS VERY RICH"),
        (0.05, "BILLS RICH"),
        (-0.05, "NEUTRAL"),
        (-0.10, "BILLS CHEAP"),
        (-999, "BILLS VERY CHEAP")
    ],
    "RMP_Index": [
        (1.0, "HIGH INTERVENTION"),
        (0.5, "ELEVATED ACTIVITY"),
        (-0.5, "NORMAL OPS"),
        (-999, "LOW/NO INTERVENTION")
    ],
    # Market Structure (Pillar 11)
    "MSI": [
        (1.0, "STRONG UPTREND"),
        (0.5, "BULLISH"),
        (-0.5, "TRANSITIONAL"),
        (-1.0, "WEAK"),
        (-999, "BEARISH")
    ],
    "SBD": [
        (1.5, "EXTREME DISTRIBUTION"),
        (1.0, "DISTRIBUTION"),
        (-0.5, "ALIGNED"),
        (-1.5, "ACCUMULATION"),
        (-999, "EXTREME ACCUMULATION")
    ],
    # Sentiment & Positioning (Pillar 12)
    "SPI": [
        (1.5, "EXTREME FEAR"),
        (1.0, "FEARFUL"),
        (-0.5, "NEUTRAL"),
        (-1.0, "EUPHORIC"),
        (-999, "EXTREME EUPHORIA")
    ],
    "SSD": [
        (1.5, "CAPITULATION LOW"),
        (0.5, "FEAR + WEAK"),
        (-0.5, "BALANCED"),
        (-1.5, "EUPHORIA + STRONG"),
        (-999, "BLOW-OFF TOP RISK")
    ],
    # Recession Probability
    "REC_PROB": [
        (0.70, "HIGH RISK"),
        (0.40, "ELEVATED"),
        (0.20, "MODERATE"),
        (-999, "LOW RISK")
    ],
    # Warning System Level (1=GREEN, 2=YELLOW, 3=AMBER, 4=RED)
    "WARNING_LEVEL": [
        (3.5, "RED"),
        (2.5, "AMBER"),
        (1.5, "YELLOW"),
        (-999, "GREEN")
    ],
    # Ensemble Risk (adjusted probability)
    "ENSEMBLE_RISK": [
        (0.70, "CRISIS"),
        (0.50, "PRE-CRISIS"),
        (0.30, "HOLLOW RALLY"),
        (0.15, "LATE CYCLE"),
        (-999, "EXPANSION")
    ],
    # Discontinuity Premium
    "DISCONTINUITY_PREMIUM": [
        (0.30, "EXTREME"),
        (0.15, "HIGH"),
        (0.05, "MODERATE"),
        (-999, "LOW")
    ],
    # Allocation Multiplier
    "ALLOC_MULTIPLIER": [
        (1.0, "AGGRESSIVE"),
        (0.7, "NORMAL"),
        (0.4, "DEFENSIVE"),
        (0.2, "MAX DEFENSIVE"),
        (-999, "CAPITAL PRESERVATION")
    ],
}


def get_status(index_name: str, value: float) -> str:
    """Get status label for an index value."""
    if pd.isna(value):
        return "NO DATA"
    thresholds = STATUS_THRESHOLDS.get(index_name, [])
    for threshold, status in thresholds:
        if value >= threshold:
            return status
    return "UNKNOWN"


# ==========================================
# Z-SCORE COMPUTATION
# ==========================================

def compute_zscore(series: pd.Series, window: int = 24, min_periods: int = None) -> pd.Series:
    """
    Compute rolling z-score for a series.

    Args:
        series: Input series
        window: Rolling window (default 24 for monthly = 2 years)
        min_periods: Minimum periods required (default: window // 2)

    Returns:
        Z-score series. Returns NaN where std is zero (constant values in window).
    """
    if min_periods is None:
        min_periods = max(1, window // 2)
    else:
        min_periods = min(min_periods, window)

    rolling_mean = series.rolling(window, min_periods=min_periods).mean()
    rolling_std = series.rolling(window, min_periods=min_periods).std()

    # Protect against division by zero when std is 0 (constant values in window)
    # Replace zero std with NaN to produce NaN z-score instead of inf
    rolling_std = rolling_std.replace(0, np.nan)

    return (series - rolling_mean) / rolling_std


def weighted_sum_strict(components: list) -> pd.Series:
    """
    Strict weighted sum of z-score components — the canonical composite formula.

    The composite is computed only at dates where every input is present.
    Any NaN input propagates to NaN output at that date. This preserves the
    exact published formula and weights — no implicit substitutions, no
    silent reweighting. Trailing-tail freshness is provided separately by
    bridge_to_today() using Layer-1 nowcasts.

    Args:
        components: list of (series, weight) tuples.

    Returns:
        Weighted composite, NaN at any date with a missing input.
    """
    if not components:
        return pd.Series(dtype=float)

    series_list, weights = zip(*components)
    df = pd.concat(series_list, axis=1)
    df.columns = range(len(series_list))

    w = np.asarray(weights, dtype=float)
    valid = df.notna().all(axis=1)
    # Plain weighted sum where valid; NaN elsewhere.
    weighted_sum = df.fillna(0).to_numpy() @ w
    out = pd.Series(weighted_sum, index=df.index, dtype=float)
    return out.where(valid)


# Back-compat alias. Both names point at the strict implementation so we don't
# have to rename every call site.
nan_weighted_sum = weighted_sum_strict


def all_present_mean(*serieses: pd.Series) -> pd.Series:
    """
    Strict mean across equally-weighted series. NaN at any date where any input
    is NaN. Used for composites defined as a simple average (LDI, YFS).
    """
    if not serieses:
        return pd.Series(dtype=float)
    df = pd.concat(serieses, axis=1)
    valid = df.notna().all(axis=1)
    return df.mean(axis=1, skipna=False).where(valid)


# Back-compat alias.
nan_mean = all_present_mean


# Bridge tier labels — track which method produced each value.
TIER_ANCHOR = "anchor"             # strict formula, all inputs present
TIER_REGRESSION = "regression"     # OLS prediction from fitted proxy model
TIER_PERSIST = "persistence"       # last value carried forward
TIER_OFFSET = "offset"             # legacy offset-glue fallback (deprecated)


def bridge_via_regression(
    anchor: pd.Series,
    proxies: dict,
    target_index: pd.DatetimeIndex | None = None,
    min_overlap: int = 252,
) -> tuple[pd.Series, pd.Series, dict]:
    """
    Multi-proxy regression bridge.

    Fits the composite's historical anchor against a basket of daily/weekly
    proxies via ordinary least squares over the full available overlap, then
    uses the fitted model to project the composite forward from the last
    full-coverage date to the latest date in target_index.

    This is the canonical bridge. It is NOT a level-translation of one
    partner curve. The model learns each proxy's empirical contribution (and
    sign) from the data. Where proxies disagree historically with the
    anchor's economic intuition, OLS sorts it out.

    Args:
        anchor: strict composite series (NaN past last full-coverage date).
        proxies: dict[name -> pd.Series], raw (unsigned). Each is a daily
            or weekly Layer-1 partner.
        target_index: dates the bridge should extend to.
        min_overlap: minimum overlapping observations required to fit. Below
            this we fall back to persistence.

    Returns:
        (bridged_series, tier_series, fit_info) where:
          - bridged_series: anchor + regression forward
          - tier_series: per-date label (anchor / regression / persistence)
          - fit_info: dict with alpha, betas, sigma (residual std error),
            r2, n_overlap, partner_names. Sigma is usable for confidence
            bands at ± 1.96σ for 95%.
    """
    import numpy as np

    if anchor.empty or anchor.dropna().empty:
        return anchor, pd.Series(index=anchor.index, dtype=object), {}

    proxies = {k: v for k, v in proxies.items()
               if v is not None and not v.dropna().empty}
    if not proxies:
        return anchor, pd.Series(index=anchor.index, dtype=object), {}

    if target_index is None:
        target_index = anchor.index

    full_index = anchor.index.union(target_index)
    for p in proxies.values():
        full_index = full_index.union(p.index)
    full_index = full_index.sort_values()

    df = pd.DataFrame({"y": anchor.reindex(full_index)})
    for name, p in proxies.items():
        df[name] = p.reindex(full_index)

    overlap = df.dropna()
    n_overlap = int(len(overlap))

    last_anchor_date = anchor.last_valid_index()
    last_anchor_value = float(anchor.loc[last_anchor_date])

    tier = pd.Series(index=full_index, dtype=object)
    tier.loc[anchor.dropna().index] = TIER_ANCHOR
    result = anchor.reindex(full_index).copy()

    if n_overlap < min_overlap:
        # Not enough historical overlap to trust a fit. Persist.
        for d in full_index[full_index > last_anchor_date]:
            result.at[d] = last_anchor_value
            tier.at[d] = TIER_PERSIST
        return result, tier, {
            "n_overlap": n_overlap,
            "fallback": "persistence",
            "partner_names": list(proxies.keys()),
        }

    # OLS via lstsq. Design matrix = [intercept, proxy_1, proxy_2, ...]
    proxy_names = [c for c in overlap.columns if c != "y"]
    Y = overlap["y"].to_numpy(dtype=float)
    X = np.column_stack([
        np.ones(n_overlap),
        *(overlap[c].to_numpy(dtype=float) for c in proxy_names),
    ])
    beta, *_ = np.linalg.lstsq(X, Y, rcond=None)
    alpha = float(beta[0])
    betas = {name: float(b) for name, b in zip(proxy_names, beta[1:])}

    fitted = X @ beta
    resid = Y - fitted
    k = len(beta)
    sigma = float(np.std(resid, ddof=k) if n_overlap > k else np.std(resid))
    ss_res = float((resid ** 2).sum())
    ss_tot = float(((Y - Y.mean()) ** 2).sum())
    r2 = (1.0 - ss_res / ss_tot) if ss_tot > 0 else 0.0

    # Forward prediction: every date where ALL proxies are present.
    proxy_present = df[proxy_names].notna().all(axis=1)
    pred_idx = df.index[proxy_present]
    X_pred = np.column_stack([
        np.ones(len(pred_idx)),
        *(df.loc[pred_idx, c].to_numpy(dtype=float) for c in proxy_names),
    ])
    pred = X_pred @ beta
    pred_series = pd.Series(pred, index=pred_idx, dtype=float)

    # Combine: anchor up through last_anchor_date; regression after.
    last_filled = last_anchor_value
    for d in full_index[full_index > last_anchor_date]:
        if d in pred_series.index:
            result.at[d] = float(pred_series.loc[d])
            tier.at[d] = TIER_REGRESSION
            last_filled = result.at[d]
        else:
            result.at[d] = last_filled
            tier.at[d] = TIER_PERSIST

    return result, tier, {
        "n_overlap": n_overlap,
        "alpha": alpha,
        "betas": betas,
        "sigma": sigma,
        "r2": r2,
        "partner_names": proxy_names,
    }


def bridge_to_today(
    anchor: pd.Series,
    partners: list,
    target_index: pd.DatetimeIndex | None = None,
) -> tuple[pd.Series, pd.Series]:
    """
    Extend a composite from its last full-coverage anchor to the end of
    target_index using a tiered list of Layer-1 partners.

    The composite always has a value past the anchor. The bridge walks the
    partner list in priority order at each date. The first partner with a
    value at that date is used, offset-anchored to keep the level continuous
    at the handoff. If every partner is NaN at a given date, the bridge
    persists the last published value rather than emitting NaN.

    Args:
        anchor: strict composite series.
        partners: list of pd.Series, each ALREADY signed (multiplied by its
            partner sign). Order is priority: index 0 is primary.
        target_index: dates to extend to. Defaults to anchor.index.

    Returns:
        (bridged_series, tier_series) where tier_series labels each row's
        source (anchor / primary / secondary / tertiary / persistence).
    """
    if anchor.empty or anchor.dropna().empty:
        return anchor, pd.Series(index=anchor.index, dtype=object)
    partners = [p for p in partners if p is not None and not p.dropna().empty]

    last_anchor_date = anchor.last_valid_index()
    anchor_level = float(anchor.loc[last_anchor_date])

    # Pre-compute the offset for each partner at the handoff point.
    offsets = []
    for p in partners:
        history = p.loc[:last_anchor_date].dropna()
        if history.empty:
            offsets.append(None)
        else:
            offsets.append(anchor_level - float(history.iloc[-1]))

    # Build the full target index.
    if target_index is None:
        target_index = anchor.index
    full_index = anchor.index.union(target_index)
    for p in partners:
        full_index = full_index.union(p.index)
    full_index = full_index.sort_values()

    result = anchor.reindex(full_index).copy()
    tier = pd.Series(index=full_index, dtype=object)
    tier.loc[anchor.dropna().index] = TIER_ANCHOR

    tail_dates = full_index[full_index > last_anchor_date]
    last_value = anchor_level
    tier_names = [TIER_PRIMARY, TIER_SECONDARY, TIER_TERTIARY]
    for d in tail_dates:
        found = False
        for i, (p, off) in enumerate(zip(partners, offsets)):
            if off is None:
                continue
            if d in p.index:
                pv = p.loc[d]
                if pd.notna(pv):
                    result.at[d] = float(pv) + off
                    tier.at[d] = tier_names[min(i, len(tier_names) - 1)]
                    last_value = result.at[d]
                    found = True
                    break
        if not found:
            result.at[d] = last_value
            tier.at[d] = TIER_PERSIST

    return result, tier


# ==========================================
# INDEX FORMULAS
# ==========================================

def compute_lfi(df: pd.DataFrame) -> pd.Series:
    """
    Labor Fragility Index (LFI)

    Weights recalibrated 2026-01-19 based on validation analysis.
    Flow indicators (quits, hires/quits) are more predictive than stock
    indicators (long-term unemployment).

    Formula (v2.0 - Validation-Informed):
        LFI = 0.15 × z(Long_Duration_Unemployment_Share)  # Reduced (was 0.35)
            + 0.45 × z(-Quits_Rate)                       # Increased (was 0.35)
            + 0.40 × z(-Hires_to_Quits_Ratio)             # Increased (was 0.30)

    Rationale:
        - Quits rate is the "truth serum" of labor markets
        - Hires/Quits ratio shows labor market dynamics
        - Long-term unemployment is more lagging/coincident

    Interpretation:
        < 0.0: Healthy labor market
        0.0 - 0.5: Neutral
        0.5 - 1.0: Elevated fragility
        1.0 - 1.5: High fragility
        > 1.5: Critical - recession imminent
    """
    # Components
    # Long-term unemployed share: Unemployed_27wks_Plus as % of total unemployed
    # We use the z-score of the raw level as proxy since share isn't directly computed
    z_longterm = df.get("Unemployed_27wks_Plus_z", pd.Series(dtype=float))

    # Quits rate (INVERTED - low quits = high fragility)
    z_quits = -df.get("JOLTS_Quits_Rate_z", pd.Series(dtype=float))

    # Hires/Quits ratio (INVERTED)
    # Compute from raw values
    hires = df.get("JOLTS_Hires_Rate", pd.Series(dtype=float))
    quits = df.get("JOLTS_Quits_Rate", pd.Series(dtype=float))
    hires_quits_ratio = hires / quits.replace(0, np.nan)
    z_hires_quits = -compute_zscore(hires_quits_ratio, window=24)

    lfi = nan_weighted_sum([
        (z_longterm, 0.15),
        (z_quits, 0.45),
        (z_hires_quits, 0.40),
    ])

    # Smooth with 3-month (63 trading day) moving average to reduce noise
    # Raw z-score composites are choppy at daily frequency
    lfi = lfi.rolling(63, min_periods=21).mean()

    return lfi


def compute_lci(df: pd.DataFrame) -> pd.Series:
    """
    Liquidity Cushion Index (LCI)

    Formula:
        LCI = 0.25 × z(Reserves_vs_LCLOR)
            + 0.20 × z(-EFFR_IORB_Spread)        # Inverted (positive spread = stress)
            + 0.15 × z(-SOFR_IORB_Spread)        # Inverted
            + 0.15 × z(RRP_Balance)              # Buffer level
            + 0.10 × z(-GCF_TPR_Spread)          # Inverted
            + 0.10 × z(-Dealer_Net_Position)     # Inverted
            + 0.05 × z(-EUR_USD_Basis)           # Inverted

    Simplified version using available data:
        - Bank_Reserves (proxy for reserves vs LCLOR)
        - RRP_Usage
        - EFFR/SOFR spreads (computed from rates)

    Interpretation:
        > 1.0: Abundant liquidity
        0.5 - 1.0: Ample
        -0.5 - 0.5: Tight
        -1.0 - -0.5: Scarce (CURRENT)
        < -1.0: Crisis
    """
    # Bank reserves z-score (proxy for reserves vs LCLOR)
    reserves = df.get("Bank_Reserves", pd.Series(dtype=float))
    z_reserves = compute_zscore(reserves, window=24)

    # RRP Usage z-score
    z_rrp = df.get("RRP_Usage_z", pd.Series(dtype=float))

    # EFFR level (we don't have IORB directly, use EFFR z-score inverted as proxy)
    effr = df.get("EFFR", pd.Series(dtype=float))
    sofr = df.get("SOFR", pd.Series(dtype=float))

    # Compute EFFR-SOFR spread as funding stress proxy
    effr_sofr_spread = effr - sofr
    z_effr_sofr = -compute_zscore(effr_sofr_spread, window=252)  # Daily data

    # Chicago NFCI as financial conditions proxy (inverted - negative = loose)
    z_nfci = -df.get("Chicago_NFCI_z", pd.Series(dtype=float))

    lci = nan_weighted_sum([
        (z_reserves, 0.30),
        (z_rrp, 0.25),
        (z_effr_sofr, 0.25),
        (z_nfci, 0.20),
    ])

    return lci


def compute_clg(df: pd.DataFrame, lfi: pd.Series) -> pd.Series:
    """
    Credit-Labor Gap (CLG)

    Formula:
        CLG = z(HY_OAS) - z(LFI)

    Interpretation:
        Positive: Spreads pricing in more risk than labor suggests
        Negative: Spreads too tight for underlying labor fragility (MISPRICED)

    Current: -1.84 (MISPRICED - spreads ~100-150 bps too tight)
    """
    z_hy_oas = df.get("HY_OAS_z", pd.Series(dtype=float))

    # Z-score the LFI itself to put on same scale
    z_lfi = compute_zscore(lfi, window=24)

    clg = z_hy_oas - z_lfi

    # Smooth with 3-month (63 trading day) moving average to reduce noise
    clg = clg.rolling(63, min_periods=21).mean()

    return clg


def compute_lpi(df: pd.DataFrame) -> pd.Series:
    """
    Labor Pillar Composite Index (LPI)

    Formula:
        LPI = 0.20 × z(Quits_Rate)
            + 0.15 × z(Hires_Quits_Ratio)
            + 0.15 × z(-Long_Term_Unemployed_Share)   # Inverted
            + 0.15 × z(-Initial_Claims_4wk_MA)         # Inverted
            + 0.10 × z(Prime_Age_LFPR)
            + 0.10 × z(Avg_Weekly_Hours_Mfg)
            + 0.10 × z(-Temp_Help_YoY)                 # Inverted
            + 0.05 × z(Job_Hopper_Premium)

    Simplified with available data.
    """
    # Quits rate
    z_quits = df.get("JOLTS_Quits_Rate_z", pd.Series(dtype=float))

    # Hires/Quits ratio
    hires = df.get("JOLTS_Hires_Rate", pd.Series(dtype=float))
    quits = df.get("JOLTS_Quits_Rate", pd.Series(dtype=float))
    hires_quits_ratio = hires / quits.replace(0, np.nan)
    z_hires_quits = compute_zscore(hires_quits_ratio, window=24)

    # Long-term unemployed (INVERTED)
    z_longterm = -df.get("Unemployed_27wks_Plus_z", pd.Series(dtype=float))

    # Initial Claims (INVERTED)
    z_claims = -df.get("Initial_Claims_z", pd.Series(dtype=float))

    # Prime Age LFPR
    z_lfpr = df.get("LFPR_Prime_Age_25_54_z", pd.Series(dtype=float))

    lpi = nan_weighted_sum([
        (z_quits, 0.25),
        (z_hires_quits, 0.20),
        (z_longterm, 0.20),
        (z_claims, 0.20),
        (z_lfpr, 0.15),
    ])

    return lpi


def compute_pci(df: pd.DataFrame) -> pd.Series:
    """
    Prices Pillar Composite Index (PCI)

    Formula:
        PCI = 0.30 × z(Core_PCE_3M_Ann)
            + 0.20 × z(Services_ex_Shelter_YoY)
            + 0.15 × z(Shelter_CPI_YoY)
            + 0.15 × z(Sticky_CPI_YoY)
            + 0.10 × z(5Y5Y_Forward_Inflation)
            + 0.10 × z(-Goods_CPI_YoY)           # Inverted
    """
    # Core PCE 3M annualized
    pce_3m = df.get("PCE_Core_3m_ann", pd.Series(dtype=float))
    z_pce_3m = compute_zscore(pce_3m, window=24)

    # Shelter CPI
    shelter = df.get("CPI_Shelter_yoy_pct", pd.Series(dtype=float))
    z_shelter = compute_zscore(shelter, window=24)

    # Sticky CPI
    sticky = df.get("Sticky_Core_CPI_yoy_pct", pd.Series(dtype=float))
    z_sticky = compute_zscore(sticky, window=24)

    # 5Y5Y Forward Inflation
    z_5y5y = df.get("Forward_Inflation_5Y_z", pd.Series(dtype=float))

    pci = nan_weighted_sum([
        (z_pce_3m, 0.35),
        (z_shelter, 0.25),
        (z_sticky, 0.20),
        (z_5y5y, 0.20),
    ])

    return pci


def compute_gci(df: pd.DataFrame) -> pd.Series:
    """
    Growth Pillar Composite Index (GCI)

    Formula:
        GCI = 0.25 × z(Industrial_Production_YoY)
            + 0.20 × z(ISM_Manufacturing)
            + 0.15 × z(Core_Capital_Goods_Orders_YoY)
            + 0.15 × z(Aggregate_Weekly_Hours_YoY)
            + 0.10 × z(Real_Retail_Sales_YoY)
            + 0.10 × z(Housing_Starts_YoY)
            + 0.05 × z(-GDI_GDP_Spread)
    """
    # Industrial Production YoY
    ip_yoy = df.get("Industrial_Production_yoy_pct", pd.Series(dtype=float))
    z_ip = compute_zscore(ip_yoy, window=24)

    # Retail Sales YoY
    retail_yoy = df.get("Retail_Sales_yoy_pct", pd.Series(dtype=float))
    z_retail = compute_zscore(retail_yoy, window=24)

    # Housing Starts YoY
    starts_yoy = df.get("Housing_Starts_yoy_pct", pd.Series(dtype=float))
    z_starts = compute_zscore(starts_yoy, window=24)

    gci = nan_weighted_sum([
        (z_ip, 0.40),
        (z_retail, 0.30),
        (z_starts, 0.30),
    ])

    return gci


def compute_hci(df: pd.DataFrame) -> pd.Series:
    """
    Housing Pillar Composite Index (HCI)
    """
    # Housing Starts YoY
    z_starts = df.get("Housing_Starts_z", pd.Series(dtype=float))

    # Existing Home Sales
    sales_yoy = df.get("Existing_Home_Sales_yoy_pct", pd.Series(dtype=float))
    z_sales = compute_zscore(sales_yoy, window=24)

    # Months Supply (INVERTED)
    z_supply = -df.get("Months_Supply_z", pd.Series(dtype=float))

    # Case-Shiller
    cs_yoy = df.get("Case_Shiller_Home_Prices_yoy_pct", pd.Series(dtype=float))
    z_cs = compute_zscore(cs_yoy, window=24)

    # Mortgage Rate (INVERTED)
    mortgage = df.get("Mortgage_30Y", pd.Series(dtype=float))
    z_mortgage = -compute_zscore(mortgage, window=52)

    hci = nan_weighted_sum([
        (z_starts, 0.25),
        (z_sales, 0.25),
        (z_supply, 0.20),
        (z_cs, 0.15),
        (z_mortgage, 0.15),
    ])

    return hci


def compute_cci(df: pd.DataFrame) -> pd.Series:
    """
    Consumer Pillar Composite Index (CCI)
    """
    # Consumer Sentiment
    z_sentiment = df.get("Consumer_Sentiment_z", pd.Series(dtype=float))

    # Saving Rate
    z_saving = df.get("Saving_Rate_z", pd.Series(dtype=float))

    # Credit Card Delinquency (INVERTED)
    z_delinq = -df.get("Delinquency_Credit_Card_z", pd.Series(dtype=float))

    cci = nan_weighted_sum([
        (z_sentiment, 0.35),
        (z_saving, 0.35),
        (z_delinq, 0.30),
    ])

    return cci


def compute_bci(df: pd.DataFrame) -> pd.Series:
    """
    Business Pillar Composite Index (BCI)
    """
    # CI Loans YoY
    ci_yoy = df.get("CI_Loans_yoy_pct", pd.Series(dtype=float))
    z_ci = compute_zscore(ci_yoy, window=24)

    # Business Loans YoY
    bus_yoy = df.get("Business_Loans_yoy_pct", pd.Series(dtype=float))
    z_bus = compute_zscore(bus_yoy, window=24)

    # HY Spreads (INVERTED - tight spreads = good for business)
    z_hy = -df.get("HY_OAS_z", pd.Series(dtype=float))

    bci = nan_weighted_sum([
        (z_ci, 0.35),
        (z_bus, 0.35),
        (z_hy, 0.30),
    ])

    return bci


def compute_tci(df: pd.DataFrame) -> pd.Series:
    """
    Trade Pillar Composite Index (TCI)
    """
    # Dollar Index (INVERTED - strong dollar = headwind)
    dollar_yoy = df.get("Dollar_Index_yoy_pct", pd.Series(dtype=float))
    z_dollar = -compute_zscore(dollar_yoy, window=252)

    # EUR/USD
    eur_yoy = df.get("EUR_USD_yoy_pct", pd.Series(dtype=float))
    z_eur = compute_zscore(eur_yoy, window=252)

    tci = nan_weighted_sum([
        (z_dollar, 0.50),
        (z_eur, 0.50),
    ])

    return tci


def compute_fpi(df: pd.DataFrame) -> pd.Series:
    """
    Fiscal Pressure Index (FPI) — Pillar 8 (Government).
    Previously coded as GCI-Gov; renamed per 2026-05-08 naming lock.
    """
    # Debt to GDP
    debt_gdp = df.get("Debt_to_GDP", pd.Series(dtype=float))
    z_debt = compute_zscore(debt_gdp, window=8)  # Quarterly

    # Term Premium
    z_term = df.get("Term_Premium_10Y_z", pd.Series(dtype=float))

    fpi = nan_weighted_sum([
        (z_debt, 0.50),
        (z_term, 0.50),
    ])

    return fpi


def compute_fci(df: pd.DataFrame, lci: pd.Series) -> pd.Series:
    """
    Financial Pillar Composite Index (FCI)
    """
    # HY OAS (INVERTED - tight spreads = loose conditions)
    z_hy = -df.get("HY_OAS_z", pd.Series(dtype=float))

    # NFCI (INVERTED - negative NFCI = loose)
    z_nfci = -df.get("Chicago_NFCI_z", pd.Series(dtype=float))

    # Yield Curve 10Y-2Y
    z_curve = df.get("Curve_10Y_2Y_z", pd.Series(dtype=float))

    # VIX (INVERTED - low VIX = loose)
    z_vix = -df.get("VIX_z", pd.Series(dtype=float))

    fci = nan_weighted_sum([
        (z_hy, 0.25),
        (z_nfci, 0.25),
        (z_curve, 0.25),
        (z_vix, 0.15),
        (lci, 0.10),
    ])

    return fci


def compute_mri(lpi: pd.Series, pci: pd.Series, gci: pd.Series,
               hci: pd.Series, cci: pd.Series, bci: pd.Series,
               tci: pd.Series, fpi: pd.Series, fci: pd.Series,
               lci: pd.Series) -> pd.Series:
    """
    Macro Risk Index (MRI) - Master Composite

    Weights recalibrated 2026-01-19 based on validation analysis using:
    - Correlation analysis with recession prediction
    - Elastic Net regularized regression
    - Random Forest feature importance
    - Average of all methods normalized to 1.0

    Formula (v2.0 - Validation-Informed):
        MRI = 0.33 × (-LPI)           # Labor (highest predictive power)
            + 0.03 × PCI              # Prices (reduced - less predictive)
            + 0.02 × (-GCI)           # Growth (reduced - lags significantly)
            + 0.02 × (-HCI)           # Housing (reduced - less predictive)
            + 0.02 × (-CCI)           # Consumer (reduced - lagging indicator)
            + 0.13 × (-BCI)           # Business (maintained - leading)
            + 0.12 × (-TCI)           # Trade (increased - more predictive)
            + 0.12 × GCI-Gov          # Government (maintained - fiscal stress)
            + 0.07 × (-FCI)           # Financial (slight increase)
            + 0.14 × (-LCI)           # Plumbing (increased - leading)

    Interpretation (cycle-based regime naming):
        < -0.20: Early Expansion
        -0.20 to 0.10: Mid-Cycle
        0.10 to 0.25: Late Cycle
        0.25 to 0.50: Pre-Recession
        > 0.50: Recession

    Validation Notes:
        - LPI shows highest correlation with recession (0.33 avg importance)
        - GCI, HCI, CCI, PCI show low importance (<0.03) in prediction
        - LCI and TCI show higher importance than originally weighted
        - BCI and GCI_Gov remain important leading indicators
    """
    mri = nan_weighted_sum([
        (-lpi,    0.33),   # Labor
        (pci,     0.03),   # Prices
        (-gci,    0.02),   # Growth
        (-hci,    0.02),   # Housing
        (-cci,    0.02),   # Consumer
        (-bci,    0.13),   # Business
        (-tci,    0.12),   # Trade
        (fpi,     0.12),   # Government (Fiscal Pressure)
        (-fci,    0.07),   # Financial
        (-lci,    0.14),   # Plumbing
    ])

    return mri


def compute_ldi(df: pd.DataFrame) -> pd.Series:
    """
    Labor Dynamism Index (LDI)

    Formula:
        LDI = (z(Quits) + z(Hires/Quits) + z(Quits/Layoffs)) / 3

    Measures overall labor market dynamism/fluidity.
    High = healthy churn, Low = frozen market.
    """
    # Quits rate z-score
    z_quits = df.get("JOLTS_Quits_Rate_z", pd.Series(dtype=float))

    # Hires/Quits ratio
    hires = df.get("JOLTS_Hires_Rate", pd.Series(dtype=float))
    quits = df.get("JOLTS_Quits_Rate", pd.Series(dtype=float))
    hires_quits_ratio = hires / quits.replace(0, np.nan)
    z_hires_quits = compute_zscore(hires_quits_ratio, window=24)

    # Quits/Layoffs ratio (proxy using quits / claims inverse)
    claims = df.get("Initial_Claims", pd.Series(dtype=float))
    quits_claims_ratio = quits / (claims / 1000).replace(0, np.nan)  # Scale claims
    z_quits_claims = compute_zscore(quits_claims_ratio, window=24)

    ldi = nan_mean(z_quits, z_hires_quits, z_quits_claims)

    return ldi


def compute_yfs(df: pd.DataFrame) -> pd.Series:
    """
    Yield-Funding Stress (YFS)

    Formula:
        YFS = avg([z(10Y_2Y), z(10Y_3M), z(BGCR_EFFR)])

    Measures yield curve + funding stress combination.
    """
    z_10y2y = df.get("Curve_10Y_2Y_z", pd.Series(dtype=float))
    z_10y3m = df.get("Curve_10Y_3M_z", pd.Series(dtype=float))

    # BGCR-EFFR spread proxy (use SOFR-EFFR)
    sofr = df.get("SOFR", pd.Series(dtype=float))
    effr = df.get("EFFR", pd.Series(dtype=float))
    sofr_effr = sofr - effr
    z_sofr_effr = compute_zscore(sofr_effr, window=252)

    yfs = nan_mean(z_10y2y, z_10y3m, z_sofr_effr)

    return yfs


def compute_svi(df: pd.DataFrame) -> pd.Series:
    """
    Spread-Volatility Imbalance (SVI)

    Formula:
        SVI = z(HY_Spread_Level) / z(HY_Spread_Volatility)

    High SVI = spreads elevated but not volatile (complacent)
    Low SVI = spreads moving appropriately with vol
    """
    z_hy = df.get("HY_OAS_z", pd.Series(dtype=float))

    # HY spread volatility (rolling std of changes)
    hy_oas = df.get("HY_OAS", pd.Series(dtype=float))
    hy_vol = hy_oas.diff().rolling(21).std()
    z_hy_vol = compute_zscore(hy_vol, window=252)

    # Avoid division by zero
    svi = z_hy / z_hy_vol.replace(0, np.nan)
    svi = svi.clip(-5, 5)  # Cap extreme values

    return svi


def compute_emd(df: pd.DataFrame) -> pd.Series:
    """
    Equity Momentum Divergence (EMD)

    Formula:
        EMD = z((SP500 - SP500_MA) / Realized_Volatility)

    Requires equity price data. Using VIX as realized vol proxy.
    This is a placeholder - needs equity data integration.
    """
    # VIX as volatility proxy
    vix = df.get("VIX", pd.Series(dtype=float))
    z_vix = df.get("VIX_z", pd.Series(dtype=float))

    # Without SP500 price data, return VIX-based momentum proxy
    emd = -z_vix  # Inverted: low VIX = bullish momentum

    return emd


def compute_liquidity_stage(df: pd.DataFrame) -> pd.Series:
    """
    Liquidity Transmission Stage (1-7)

    Stages:
        1: RRP Depletion (RRP < $500B)
        2: Reserve Drainage (Reserves declining, RRP < $200B)
        3: SRF Usage Surge (EFFR-IORB > +5bps)
        4: Collateral Stress (funding spreads widening)
        5: Stablecoin Flow Stalls
        6: Perp Basis Collapse
        7: Crypto Liquidations

    Returns numeric stage (1-7) based on available indicators.
    """
    rrp = df.get("RRP_Usage", pd.Series(dtype=float))
    reserves = df.get("Bank_Reserves", pd.Series(dtype=float))
    effr = df.get("EFFR", pd.Series(dtype=float))
    sofr = df.get("SOFR", pd.Series(dtype=float))

    # Determine stage based on thresholds
    stage = pd.Series(index=df.index, dtype=float)

    # Stage 1: RRP < $500B
    stage = stage.fillna(1)

    # Stage 2: RRP < $200B
    stage = stage.where(~(rrp < 200000), 2)

    # Stage 3: EFFR elevated (proxy: EFFR > SOFR + 5bps)
    effr_sofr_spread = effr - sofr
    stage = stage.where(~((rrp < 200000) & (effr_sofr_spread > 0.05)), 3)

    return stage


def compute_bill_sofr_spread(df: pd.DataFrame) -> pd.Series:
    """
    3M Bill-SOFR Spread

    Formula:
        Bill_SOFR_Spread = 3M_Bill_Rate - SOFR

    Positive = Bills "rich" (high demand, often from stablecoins)
    Negative = Bills "cheap"
    """
    bill_3m = df.get("Treasury_3M", pd.Series(dtype=float))
    sofr = df.get("SOFR", pd.Series(dtype=float))

    spread = bill_3m - sofr

    return spread


def compute_rmp_index(df: pd.DataFrame) -> pd.Series:
    """
    Reserve Management Purchase (RMP) Index

    Measures Treasury buyback activity targeting off-the-run securities.
    Elevated RMP activity signals Treasury is actively managing collateral
    stress and market liquidity—a key intervention in the liquidity
    transmission framework.

    Formula (when data available):
        RMP_Index = 0.40 × z(RMP_Volume_30d)           # Rolling 30d buyback volume
                  + 0.30 × z(RMP_Frequency)            # Operations per week
                  + 0.30 × z(-Off_Run_On_Run_Spread)   # Inverted: tight spread = success

    Interpretation:
        > 1.0:  High Intervention (Treasury actively supporting market)
        0.5-1.0: Elevated Activity
        -0.5-0.5: Normal Operations
        < -0.5: Low/No Intervention (market functioning well OR no capacity)

    DATA SOURCES NEEDED:
    =====================
    1. TreasuryDirect Buyback Announcements
       - URL: https://www.treasurydirect.gov/auctions/announcements-data-results/
       - Contains: Operation dates, amounts, CUSIP ranges, settlement dates
       - Format: XML/JSON via Treasury API

    2. NY Fed Primary Dealer Statistics
       - URL: https://www.newyorkfed.org/markets/primarydealers
       - Contains: Dealer positions, fails, financing
       - Relevant: Off-the-run vs on-the-run positioning

    3. TRACE/FINRA Bond Data (for spread calculation)
       - Off-the-run vs on-the-run yield spreads
       - Liquidity metrics by CUSIP

    INTEGRATION NOTES:
    ==================
    - Treasury began regular buybacks in 2024 for "cash management" and
      "liquidity support" purposes
    - RMPs are distinct from QE—they're maturity-neutral swaps
    - High RMP + tight spreads = successful intervention
    - High RMP + wide spreads = stress overwhelming intervention
    - Should be incorporated into LCI formula once data available

    Current: Returns NaN placeholder until data source integrated.
    """
    # PLACEHOLDER: Return NaN series until Treasury buyback data integrated
    # TODO: Add Treasury API integration for RMP data
    #       Fields needed: operation_date, settlement_date, accepted_amount,
    #                      cusip_range, operation_type (cash_mgmt vs liquidity)

    return pd.Series(index=df.index, dtype=float, name="RMP_Index")


def compute_sli(conn: sqlite3.Connection) -> pd.DataFrame:
    """
    Stablecoin Liquidity Impulse (SLI)

    Measures rate of change in stablecoin market cap.
    This requires external data source (not in FRED/BLS/BEA).

    For now, return placeholder with available crypto-related data.
    Future: integrate with CoinGecko/DeFiLlama API.

    Returns DataFrame with columns: date, SLI, SLI_MCAP, SLI_ROC_30D, SLI_ROC_90D_ANN
    """
    # For now, return empty - SLI requires crypto data integration
    # This is a placeholder for the pipeline
    return pd.DataFrame(columns=["date", "SLI", "SLI_MCAP", "SLI_ROC_30D", "SLI_ROC_90D_ANN"])


# ==========================================
# LAYER-1 NOWCAST OVERLAYS
# ==========================================

# Per-overlay daily-ffill cap. Weekly cadence with publication slack ~14 days.
# Beyond the cap, the overlay surfaces as NaN.
NOWCAST_FFILL_LIMIT_DAYS = 14


# Bridge registry — per composite, the Layer-1 daily series that carries it
# from its last full-coverage anchor to today.
#
# Each entry: composite_id → (partner_name, sign)
#   partner_name: column in horizon_dataset OR "overlay:<key>" for overlays
#                 loaded via load_nowcast_overlays.
#   sign:        +1 if partner moves with the composite, -1 if inverse.
#
# Partners are picked from daily-fresh series in horizon_dataset:
#   Initial_Claims_z         — weekly, labor stress proxy
#   HY_OAS_z, IG_OAS_z       — daily credit spread proxies
#   Forward_Inflation_5Y_z   — daily TIPS breakeven, inflation proxy
#   Mortgage_30Y             — weekly mortgage rate
#   Term_Premium_10Y_z       — daily, fiscal pressure proxy
#   OFR_FSI_US_z             — daily financial stress, inverse of liquidity cushion
#   Dollar_Index_yoy_pct     — daily, trade headwind proxy
#   overlay:Growth_Nowcast_WEI_z — NY Fed Weekly Economic Index, growth nowcast
#
# These bridges are interim — Phase 2 will swap each one for a proper
# regression / state-space model with confidence bands and vintage tracking.
BRIDGE_REGISTRY: dict = {
    # Composite → ordered list of (partner_name, sign) tuples.
    # First entry is the primary partner. If it has no value at a date, the
    # bridge falls through to the secondary, then tertiary. If every partner
    # is NaN, the last published value is persisted. By construction the
    # composite always has a current value past the strict-formula anchor.
    "GCI": [
        ("overlay:Growth_Nowcast_WEI_z", +1),   # NY Fed WEI, daily real-economy
        ("HY_OAS_z",              -1),          # spreads as macro risk proxy
        ("VIX_z",                 -1),          # volatility regime proxy
    ],
    "LFI": [
        ("HY_OAS_z",              +1),          # credit stress leads labor stress
        ("VIX_z",                 +1),          # risk-off regime
        ("Initial_Claims_z",      +1),          # weekly truth-serum
    ],
    "LPI": [
        ("HY_OAS_z",              -1),
        ("VIX_z",                 -1),
        ("Initial_Claims_z",      -1),
    ],
    "LDI": [
        ("HY_OAS_z",              -1),
        ("VIX_z",                 -1),
        ("Initial_Claims_z",      -1),
    ],
    "PCI": [
        ("Forward_Inflation_5Y_z", +1),         # TIPS-derived 5Y forward
        ("Breakeven_5Y_z",         +1),         # 5Y breakeven backup
    ],
    "HCI": [
        ("Treasury_10Y",          -1),          # mortgage rates track 10Y
        ("Mortgage_30Y",          -1),          # weekly mortgage rate
        ("Treasury_30Y",          -1),          # long-rate fallback
    ],
    "CCI": [
        ("HY_OAS_z",              -1),
        ("VIX_z",                 -1),
    ],
    "BCI": [
        ("HY_OAS_z",              -1),
        ("IG_OAS_z",              -1),
        ("VIX_z",                 -1),
    ],
    "TCI": [
        ("HY_OAS_z",              -1),
        ("VIX_z",                 -1),
        ("Dollar_Index_yoy_pct",  -1),
    ],
    "FPI": [
        ("Curve_10Y_2Y_z",        +1),          # curve steepening = term premium
        ("Curve_10Y_3M_z",        +1),
        ("Term_Premium_10Y_z",    +1),
    ],
    "LCI": [
        ("RRP_Usage_z",           +1),          # RRP balance is the cushion itself
        ("VIX_z",                 -1),          # stress regime as inverse cushion
        ("OFR_FSI_US_z",          -1),
    ],
    "FCI": [
        ("HY_OAS_z",              -1),
        ("VIX_z",                 -1),
        ("Curve_10Y_2Y_z",        +1),
    ],
}


# Reader-facing names per the 2026-05-08 naming lock. Used for print output
# and diagrams. Database index_id codes remain unchanged as legacy keys,
# except GCI_Gov → FPI (rename authorized).
COMPOSITE_NAMES: dict = {
    "LPI": "Labor Pressure",
    "LFI": "Labor Fragility",
    "LDI": "Labor Dynamism",
    "PCI": "Inflation Heat",
    "GCI": "Activity Pulse",
    "HCI": "Housing Tide",
    "CCI": "Consumer Pulse",
    "BCI": "Capex Thrust",
    "TCI": "Global Risk Tide",
    "FPI": "Fiscal Pressure",
    "FCI": "Credit Tide",
    "LCI": "Liquidity Cushion",
    "CLG": "Credit-Labor Gap",
    "MSI": "Market Breadth Pulse",
    "SBD": "Structure-Breadth Divergence",
    "SPI": "Sentiment Tide",
    "SSD": "Sentiment-Structure Divergence",
    "MRI": "Macro Risk Index",
    "YFS": "Yield-Funding Stress",
    "SVI": "Spread-Volatility Imbalance",
    "EMD": "Equity Momentum Divergence",
}


def _display(code: str) -> str:
    """Reader-facing label for log lines and diagrams."""
    name = COMPOSITE_NAMES.get(code)
    return f"{name} ({code})" if name else code


def _resolve_bridge_partner(
    name: str,
    df: pd.DataFrame,
    overlays: dict,
) -> pd.Series | None:
    """
    Resolve a BRIDGE_REGISTRY partner spec to a daily-indexed z-score series.

    Names prefixed with "overlay:" pull from the loaded nowcast overlays.
    Names matching a horizon_dataset column ending in "_z" are used directly.
    Other column names get a daily 252d z-score computed inline.
    Returns None if the partner cannot be found.
    """
    if name.startswith("overlay:"):
        return overlays.get(name[len("overlay:"):])
    if name in df.columns:
        s = df[name].astype(float)
        if name.endswith("_z"):
            return s
        return compute_zscore(s, window=252, min_periods=63)
    return None


def _bridge_apply(
    composite_id: str,
    anchor: pd.Series,
    df: pd.DataFrame,
    overlays: dict,
) -> pd.Series:
    """
    Resolve the partner basket for a composite and apply the regression bridge.

    BRIDGE_REGISTRY entries used to carry (partner, sign) tuples for the
    legacy offset-glue bridge. With the regression model we let OLS recover
    signs empirically — the sign field is ignored. The partner *names* are
    still meaningful: they pick which Layer-1 series feed the model.
    """
    spec_list = BRIDGE_REGISTRY.get(composite_id)
    if not spec_list:
        return anchor
    if isinstance(spec_list, tuple):
        spec_list = [spec_list]

    proxies: dict = {}
    for entry in spec_list:
        partner_name = entry[0] if isinstance(entry, tuple) else entry
        p = _resolve_bridge_partner(partner_name, df, overlays)
        if p is None or p.dropna().empty:
            continue
        proxies[partner_name] = p

    if not proxies:
        return anchor

    pre = anchor.last_valid_index()
    bridged, tier, info = bridge_via_regression(
        anchor, proxies, target_index=df.index
    )
    post = bridged.last_valid_index()
    if pre is not None and post is not None and post > pre:
        n = info.get("n_overlap", 0)
        r2 = info.get("r2")
        sigma = info.get("sigma")
        names = info.get("partner_names", list(proxies.keys()))
        if r2 is not None and sigma is not None:
            betas = info.get("betas", {})
            beta_summary = ", ".join(f"{k}={v:+.2f}" for k, v in betas.items())
            print(
                f"      bridge: {composite_id} anchor ends {pre.date()}, "
                f"projected to {post.date()} via OLS on {len(names)} proxies "
                f"(n={n}, R²={r2:.2f}, σ={sigma:.2f}) · betas: {beta_summary}"
            )
        else:
            print(
                f"      bridge: {composite_id} anchor ends {pre.date()}, "
                f"carried to {post.date()} (fallback: "
                f"{info.get('fallback', 'persistence')})"
            )
    return bridged


# Yahoo Finance intraday tickers → horizon_dataset column name.
# These are quotes that update every business day during market hours, so
# they should never be more than a few hours stale. Used by
# _extend_intraday_quotes() below to close any FRED-publish-window gap.
INTRADAY_QUOTE_MAP: dict = {
    "^TNX":  "Treasury_10Y",
    "^TYX":  "Treasury_30Y",
    "^FVX":  "Treasury_5Y",
    "^IRX":  "Treasury_3M",
    "^VIX":  "VIX",
    "^GSPC": "SPX_Close",
}


def _extend_intraday_quotes(df: pd.DataFrame) -> pd.DataFrame:
    """
    Splice in today's intraday quotes from yfinance for key daily series.

    The horizon_dataset's max date comes from whatever sources FRED has
    published by pipeline run time. Treasury yields, VIX, and equity index
    closes are quoted continuously during market hours — there is no reason
    for those columns to lag by a day. This function:

      1. Pulls the last few business days' closes for each ticker in
         INTRADAY_QUOTE_MAP from yfinance.
      2. Extends df.index forward through today if needed.
      3. Fills any NaN values in the target column with the yfinance close.

    Falls back silently if yfinance isn't importable or a fetch errors —
    the bridges then just stamp at whatever the prior data supports.
    """
    try:
        import yfinance as yf
    except ImportError:
        print("   intraday extend: yfinance not available, skipping")
        return df

    today = pd.Timestamp.today().normalize()
    new_dates = pd.date_range(df.index.max() + pd.Timedelta(days=1), today, freq="D")
    if len(new_dates):
        # Extend index with NaN rows so bridges have somewhere to stamp.
        df = df.reindex(df.index.union(new_dates))

    extended_to: dict = {}
    for ticker, col in INTRADAY_QUOTE_MAP.items():
        if col not in df.columns:
            continue
        try:
            hist = yf.Ticker(ticker).history(period="10d", auto_adjust=False)
            if hist.empty:
                continue
            # yfinance returns tz-aware dates; normalize to naive daily.
            hist = hist.copy()
            hist.index = hist.index.tz_localize(None).normalize()
            for d, row in hist[["Close"]].iterrows():
                v = float(row["Close"])
                if d in df.index and pd.isna(df.at[d, col]):
                    df.at[d, col] = v
                    extended_to.setdefault(col, d)
                    if d > extended_to[col]:
                        extended_to[col] = d
        except Exception as e:
            print(f"   intraday extend {ticker} → {col} failed: {e}")

    for col, d in extended_to.items():
        print(f"   intraday extend: {col} carried to {d.date()} via yfinance")

    return df.sort_index()


def load_nowcast_overlays(
    conn: sqlite3.Connection,
    daily_index: pd.DatetimeIndex,
) -> dict:
    """
    Pull Layer-1 nowcast partners from observations and return as z-score
    series aligned to the supplied daily index.

    Currently wired:
        WEI (NY Fed Weekly Economic Index, series_id='WEI')
            → Growth_Nowcast_WEI_z
            Weekly, ffill-capped at NOWCAST_FFILL_LIMIT_DAYS.
            Daily z-score, 252d rolling.

    The architecture rule (see Outputs/nowcast_architecture_2026-05-14.html):
    Layer 1 produces a daily value for every column or stamps it NaN.
    Layer 2 (the composites) consumes Layer 1 outputs only.

    Returns:
        dict[column_name -> pd.Series] keyed by horizon_dataset column name.
    """
    overlays: dict = {}

    wei_df = pd.read_sql(
        "SELECT date, value FROM observations WHERE series_id = 'WEI' ORDER BY date",
        conn,
        parse_dates=["date"],
    )
    if not wei_df.empty:
        wei = wei_df.set_index("date")["value"].sort_index()
        wei_daily = wei.reindex(daily_index, method="ffill", limit=NOWCAST_FFILL_LIMIT_DAYS)
        z_wei = compute_zscore(wei_daily, window=252, min_periods=63)
        overlays["Growth_Nowcast_WEI_z"] = z_wei

    return overlays


# ==========================================
# MARKET STRUCTURE INDEX (MSI) - PILLAR 11
# ==========================================

def load_market_data(conn: sqlite3.Connection) -> pd.DataFrame:
    """
    Load market structure data from observations table.
    This data is fetched by the market_fetchers.py module.
    """
    series_needed = [
        'SPX_Close', 'SPX_vs_200d_pct', 'SPX_vs_50d_pct', 'SPX_vs_20d_pct',
        'SPX_50d_slope', 'SPX_20d_slope', 'SPX_200d_slope',
        'SPX_Z_RoC_63d', 'SPX_RoC_63d', 'SPX_RSI_14d',
        'VIXCLS', 'VIX_vs_50d_pct', 'VIX_percentile_252d',
        'AAII_Bullish', 'AAII_Bearish', 'AAII_Bull_Bear_Spread', 'AAII_Neutral'
    ]

    dfs = []
    for series_id in series_needed:
        query = f"""
            SELECT date, value as {series_id}
            FROM observations
            WHERE series_id = '{series_id}'
            ORDER BY date
        """
        try:
            series_df = pd.read_sql(query, conn, parse_dates=['date'])
            series_df = series_df.set_index('date')
            dfs.append(series_df)
        except Exception as e:
            print(f"      Warning: Could not load {series_id}: {e}")

    if not dfs:
        return pd.DataFrame()

    # Merge all series
    market_df = dfs[0]
    for df in dfs[1:]:
        market_df = market_df.join(df, how='outer')

    return market_df.sort_index()


def compute_msi(conn: sqlite3.Connection) -> pd.Series:
    """
    Market Structure Index (MSI) - Pillar 11

    Synthesizes trend, momentum, and breadth into a single composite.

    Formula (from PILLAR 11 MARKET STRUCTURE.md):
    MSI = 0.15 × z(Price_vs_200d_MA_%)
        + 0.10 × z(Price_vs_50d_MA_%)
        + 0.10 × z(50d_MA_Slope)
        + 0.10 × z(20d_MA_Slope)
        + 0.12 × z(Z_RoC_63d)
        + 0.10 × z(%_Stocks_>_50d_MA)  # Not available - using proxy
        + 0.08 × z(%_Stocks_>_20d_MA)  # Not available - using proxy
        + 0.08 × z(%_Stocks_>_200d_MA) # Not available - using proxy
        + 0.07 × z(Net_New_Highs_Lows_20d_Avg)  # Not available - using proxy
        + 0.05 × z(AD_Line_50d_Slope)  # Not available
        + 0.05 × z(McClellan_Summation)  # Not available

    Due to breadth data requiring premium sources, we use a simplified version
    with available components (trend + momentum) and rescale weights.

    Returns:
        pd.Series: MSI values indexed by date
    """
    market_df = load_market_data(conn)

    if market_df.empty:
        print("      Warning: No market data available for MSI")
        return pd.Series(dtype=float, name="MSI")

    # Components we have (trend + momentum)
    # Simplified MSI with available data, rescaled weights to sum to 1.0
    # Original weights for available components: 0.15 + 0.10 + 0.10 + 0.10 + 0.12 = 0.57
    # Rescale: each weight / 0.57

    components = {}

    # Trend components
    if 'SPX_vs_200d_pct' in market_df.columns:
        components['vs_200d'] = (
            compute_zscore(market_df['SPX_vs_200d_pct']),
            0.15 / 0.57  # ~0.26
        )

    if 'SPX_vs_50d_pct' in market_df.columns:
        components['vs_50d'] = (
            compute_zscore(market_df['SPX_vs_50d_pct']),
            0.10 / 0.57  # ~0.18
        )

    if 'SPX_50d_slope' in market_df.columns:
        components['slope_50d'] = (
            compute_zscore(market_df['SPX_50d_slope']),
            0.10 / 0.57
        )

    if 'SPX_20d_slope' in market_df.columns:
        components['slope_20d'] = (
            compute_zscore(market_df['SPX_20d_slope']),
            0.10 / 0.57
        )

    # Momentum component
    if 'SPX_Z_RoC_63d' in market_df.columns:
        # Already z-scored
        components['z_roc'] = (
            market_df['SPX_Z_RoC_63d'],
            0.12 / 0.57  # ~0.21
        )

    if not components:
        print("      Warning: No valid MSI components found")
        return pd.Series(dtype=float, name="MSI")

    pairs = [
        (series.reindex(market_df.index), weight)
        for series, weight in components.values()
    ]
    msi = nan_weighted_sum(pairs)
    msi.name = "MSI"

    # Quality gate: require at least 3 of the configured components to be
    # present at a given date. Below that bar we'd be renormalizing over a
    # thin subset that doesn't represent the structure pillar.
    present_count = sum(
        (~components[k][0].reindex(msi.index).isna()).astype(int)
        for k in components
    )
    msi = msi.where(present_count >= 3)

    return msi


def compute_sbd(conn: sqlite3.Connection) -> pd.Series:
    """
    Structure-Breadth Divergence (SBD)

    Measures the gap between price strength and participation.
    SBD = z(Price_vs_200d) - z(%_Stocks_>_50d_MA)

    Since we don't have breadth data, we use VIX as a proxy for
    market stress (high VIX often coincides with poor breadth).

    Proxy: SBD = z(Price_vs_200d) + z(VIX_vs_50d)
    (Adding VIX because high VIX with high price = divergence)

    Returns:
        pd.Series: SBD values indexed by date
    """
    market_df = load_market_data(conn)

    if market_df.empty:
        return pd.Series(dtype=float, name="SBD")

    sbd = pd.Series(index=market_df.index, dtype=float, name="SBD")

    if 'SPX_vs_200d_pct' in market_df.columns and 'VIX_vs_50d_pct' in market_df.columns:
        z_price = compute_zscore(market_df['SPX_vs_200d_pct'])
        z_vix = compute_zscore(market_df['VIX_vs_50d_pct'])
        # When price is high AND VIX is elevated, SBD is positive (divergence)
        sbd = z_price + z_vix * 0.5  # Dampened VIX influence
        sbd.name = "SBD"

    return sbd


# ==========================================
# SENTIMENT & POSITIONING INDEX (SPI) - PILLAR 12
# ==========================================

def compute_spi(conn: sqlite3.Connection) -> pd.Series:
    """
    Sentiment & Positioning Index (SPI) - Pillar 12

    Synthesizes sentiment and positioning data into a contrarian indicator.

    Formula (from PILLAR 12 SENTIMENT.md):
    SPI = 0.20 × z(Put_Call_10d)        # Not available
        + 0.15 × z(VIX_vs_50d)
        + 0.15 × z(-AAII_Bull_Bear)     # Inverted: high bullishness = low SPI
        + 0.15 × z(-NAAIM)              # Not available
        + 0.10 × z(-II_Bull_Bear)       # Not available
        + 0.10 × z(-ETF_Flows_20d)      # Not available
        + 0.10 × z(VIX_Backwardation)   # Not available
        + 0.05 × z(MMF_Assets_YoY)      # Not available

    High SPI = Fear = Contrarian Bullish
    Low SPI = Euphoria = Contrarian Bearish

    Returns:
        pd.Series: SPI values indexed by date
    """
    market_df = load_market_data(conn)

    if market_df.empty:
        print("      Warning: No market data available for SPI")
        return pd.Series(dtype=float, name="SPI")

    # Components we have
    # Available weights: 0.15 (VIX) + 0.15 (AAII) = 0.30
    # Rescale to 1.0

    components = {}

    # VIX component (high VIX = high fear = high SPI)
    if 'VIX_vs_50d_pct' in market_df.columns:
        components['vix'] = (
            compute_zscore(market_df['VIX_vs_50d_pct']),
            0.15 / 0.30  # 0.50
        )

    # AAII Bull-Bear spread (INVERTED: low bull-bear = high fear = high SPI).
    # AAII is a weekly print; ffill within its publication cadence so the
    # daily z-score isn't NaN six days out of seven.
    if 'AAII_Bull_Bear_Spread' in market_df.columns:
        aaii_daily = market_df['AAII_Bull_Bear_Spread'].ffill(limit=7)
        components['aaii'] = (
            compute_zscore(-aaii_daily),  # Inverted
            0.15 / 0.30  # 0.50
        )

    if not components:
        print("      Warning: No valid SPI components found")
        return pd.Series(dtype=float, name="SPI")

    pairs = [
        (series.reindex(market_df.index), weight)
        for series, weight in components.values()
    ]
    spi = nan_weighted_sum(pairs)
    spi.name = "SPI"

    return spi


def compute_ssd(spi: pd.Series, msi: pd.Series) -> pd.Series:
    """
    Sentiment-Structure Divergence (SSD)

    Measures divergence between sentiment and structure.
    SSD = z(SPI) + z(MSI)

    High SSD (>+1.5): Capitulation low forming (fear + weak structure)
    Low SSD (<-1.5): Blow-off top risk (euphoria + strong structure)

    Returns:
        pd.Series: SSD values indexed by date
    """
    # Align indices
    common_idx = spi.index.intersection(msi.index)

    if len(common_idx) == 0:
        return pd.Series(dtype=float, name="SSD")

    z_spi = compute_zscore(spi.loc[common_idx])
    z_msi = compute_zscore(msi.loc[common_idx])

    ssd = z_spi + z_msi
    ssd.name = "SSD"

    return ssd


# ==========================================
# MAIN COMPUTATION ENGINE
# ==========================================

def compute_all_indices(conn: sqlite3.Connection, latest_only: bool = False) -> pd.DataFrame:
    """
    Compute all proprietary indices from horizon_dataset.

    Args:
        conn: Database connection
        latest_only: If True, only compute for latest date

    Returns:
        DataFrame with columns: date, index_id, value, status
    """
    print("\n--- Loading Horizon Dataset ---")
    df = pd.read_sql("SELECT * FROM horizon_dataset", conn, parse_dates=["date"])
    df = df.set_index("date").sort_index()
    print(f"   Loaded {len(df)} rows, {len(df.columns)} columns")
    print(f"   Date range: {df.index.min().date()} to {df.index.max().date()}")

    # Splice in today's intraday quotes from yfinance so bridges through
    # market-quoted series (Treasury yields, VIX, SPX) stamp through today.
    print("\n--- Extending intraday quotes (yfinance) ---")
    df = _extend_intraday_quotes(df)
    print(f"   Extended date range: {df.index.min().date()} to {df.index.max().date()}")

    # Layer-1 nowcast overlays. These feed bridge_to_today() below so the
    # strict composite formulas can be carried forward from their last
    # full-coverage anchor to the latest real-time reading, without morphing
    # the published formula at any in-coverage date.
    print("\n--- Loading Layer-1 Nowcast Overlays ---")
    nowcast_overlays = load_nowcast_overlays(conn, df.index)
    for col, series in nowcast_overlays.items():
        latest = series.dropna().index.max() if not series.dropna().empty else None
        latest_str = latest.date().isoformat() if latest is not None else "—"
        print(f"   {col}: latest {latest_str}, {series.notna().sum()} non-NaN obs")

    if latest_only:
        # Only compute for last available date
        df = df.iloc[[-1]]

    print("\n--- Computing Indices (strict anchor + Layer-1 bridge) ---")

    # Pillar composites: compute strict anchor then bridge to today.
    print(f"   Computing {_display('LPI')}...")
    lpi = _bridge_apply("LPI", compute_lpi(df), df, nowcast_overlays)

    print(f"   Computing {_display('PCI')}...")
    pci = _bridge_apply("PCI", compute_pci(df), df, nowcast_overlays)

    print(f"   Computing {_display('GCI')}...")
    gci = _bridge_apply("GCI", compute_gci(df), df, nowcast_overlays)

    print(f"   Computing {_display('HCI')}...")
    hci = _bridge_apply("HCI", compute_hci(df), df, nowcast_overlays)

    print(f"   Computing {_display('CCI')}...")
    cci = _bridge_apply("CCI", compute_cci(df), df, nowcast_overlays)

    print(f"   Computing {_display('BCI')}...")
    bci = _bridge_apply("BCI", compute_bci(df), df, nowcast_overlays)

    print(f"   Computing {_display('TCI')}...")
    tci = _bridge_apply("TCI", compute_tci(df), df, nowcast_overlays)

    print(f"   Computing {_display('FPI')}...")
    fpi = _bridge_apply("FPI", compute_fpi(df), df, nowcast_overlays)

    # Bridge LFI / LCI before they feed FCI and CLG.
    print(f"   Computing {_display('LFI')}...")
    lfi = _bridge_apply("LFI", compute_lfi(df), df, nowcast_overlays)

    print(f"   Computing {_display('LCI')}...")
    lci = _bridge_apply("LCI", compute_lci(df), df, nowcast_overlays)

    print(f"   Computing {_display('FCI')}...")
    fci = _bridge_apply("FCI", compute_fci(df, lci), df, nowcast_overlays)

    print(f"   Computing {_display('CLG')}...")
    # CLG = z(HY_OAS) − z(LFI); both inputs daily-fresh after LFI bridge.
    clg = compute_clg(df, lfi)

    print(f"   Computing {_display('MRI')}...")
    # MRI consumes the bridged pillars. Strict weighted sum across the 10
    # pillars: MRI is fresh wherever every pillar is fresh.
    mri = compute_mri(lpi, pci, gci, hci, cci, bci, tci, fpi, fci, lci)

    # Additional indicators
    print(f"   Computing {_display('LDI')}...")
    ldi = _bridge_apply("LDI", compute_ldi(df), df, nowcast_overlays)

    print(f"   Computing {_display('YFS')}...")
    yfs = compute_yfs(df)  # all-daily inputs, no bridge needed

    print("   Computing SVI (Spread-Volatility Imbalance)...")
    svi = compute_svi(df)

    print("   Computing EMD (Equity Momentum Divergence)...")
    emd = compute_emd(df)

    print("   Computing Liquidity Stage...")
    liq_stage = compute_liquidity_stage(df)

    print("   Computing Bill-SOFR Spread...")
    bill_sofr = compute_bill_sofr_spread(df)

    print("   Computing RMP Index (placeholder - needs Treasury data)...")
    rmp_index = compute_rmp_index(df)

    # Market Structure Indices (Pillar 11 & 12)
    print("   Computing MSI (Market Structure Index)...")
    msi = compute_msi(conn)

    print("   Computing SBD (Structure-Breadth Divergence)...")
    sbd = compute_sbd(conn)

    print("   Computing SPI (Sentiment & Positioning Index)...")
    spi = compute_spi(conn)

    print("   Computing SSD (Sentiment-Structure Divergence)...")
    ssd = compute_ssd(spi, msi)

    # Recession Probability Model
    print("   Computing REC_PROB (Recession Probability)...")
    try:
        rec_prob = compute_recession_probability(conn)
        print(f"      Generated {len(rec_prob)} probability estimates")
    except Exception as e:
        print(f"      WARNING: Recession probability computation failed: {e}")
        rec_prob = pd.Series(dtype=float, name="REC_PROB")

    # Warning System & Risk Ensemble (latest only - these are point-in-time)
    print("   Computing WARNING_LEVEL (Threshold Warning System)...")
    print("   Computing ENSEMBLE_RISK (Risk Ensemble)...")
    try:
        warning_system = WarningSystem(conn)
        warning_result = warning_system.evaluate()
        warning_level_value = warning_result.overall_level.value
        print(f"      Warning Level: {warning_result.overall_level.name}")

        ensemble = RiskEnsemble(conn)
        ensemble_result = ensemble.evaluate()
        print(f"      Ensemble Regime: {ensemble_result.regime.name}")
        print(f"      Adjusted Probability: {ensemble_result.adjusted_probability:.1%}")
        print(f"      Discontinuity Premium: +{ensemble_result.discontinuity_premium:.1%}")
        print(f"      Allocation Multiplier: {ensemble_result.allocation_multiplier}x")
    except Exception as e:
        print(f"      WARNING: Warning/Ensemble computation failed: {e}")
        warning_result = None
        ensemble_result = None
        warning_level_value = None

    # Build output DataFrame
    print("\n--- Building Output ---")
    indices = {
        # Core indices
        "LFI": lfi,
        "LCI": lci,
        "CLG": clg,
        "MRI": mri,
        # Pillar composites (1-10)
        "LPI": lpi,
        "PCI": pci,
        "GCI": gci,
        "HCI": hci,
        "CCI": cci,
        "BCI": bci,
        "TCI": tci,
        "FPI": fpi,
        "FCI": fci,
        # Market Structure (Pillar 11)
        "MSI": msi,
        "SBD": sbd,
        # Sentiment & Positioning (Pillar 12)
        "SPI": spi,
        "SSD": ssd,
        # Additional indicators
        "LDI": ldi,
        "YFS": yfs,
        "SVI": svi,
        "EMD": emd,
        "LIQ_STAGE": liq_stage,
        "BILL_SOFR": bill_sofr,
        "RMP_Index": rmp_index,  # Placeholder - needs Treasury buyback data
        # Recession Probability
        "REC_PROB": rec_prob,
    }

    # Ensure every macro composite carries a value through today via
    # persistence. Daily-native composites (MSI, SPI, SBD, SSD, EMD, SVI,
    # YFS, LIQ_STAGE) don't go through the tiered bridge — their last value
    # is held forward to df.index.max() so every indicator always has a
    # current read.
    today_stamp = df.index.max()
    for index_id, series in list(indices.items()):
        if not isinstance(series, pd.Series) or series.dropna().empty:
            continue
        last_valid = series.last_valid_index()
        if last_valid is None or last_valid >= today_stamp:
            continue
        last_value = float(series.loc[last_valid])
        # Extend index to today and fill NaN tail with the last value.
        new_idx = series.index.union(
            pd.date_range(last_valid + pd.Timedelta(days=1), today_stamp, freq="D")
        )
        extended = series.reindex(new_idx).sort_index()
        tail = extended.index[extended.index > last_valid]
        for d in tail:
            if pd.isna(extended.at[d]):
                extended.at[d] = last_value
        indices[index_id] = extended

    # Convert to long format for database storage
    rows = []
    for index_id, series in indices.items():
        for date, value in series.items():
            if pd.notna(value):
                status = get_status(index_id, value)
                rows.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "index_id": index_id,
                    "value": round(value, 4),
                    "status": status
                })

    # Add Warning System & Ensemble outputs (single point-in-time values)
    if ensemble_result is not None:
        ensemble_date = ensemble_result.date
        # Warning Level (1-4 scale)
        rows.append({
            "date": ensemble_date,
            "index_id": "WARNING_LEVEL",
            "value": warning_level_value,
            "status": warning_result.overall_level.name
        })
        # Ensemble Risk (adjusted probability)
        rows.append({
            "date": ensemble_date,
            "index_id": "ENSEMBLE_RISK",
            "value": round(ensemble_result.adjusted_probability, 4),
            "status": ensemble_result.regime.name
        })
        # Discontinuity Premium
        rows.append({
            "date": ensemble_date,
            "index_id": "DISCONTINUITY_PREMIUM",
            "value": round(ensemble_result.discontinuity_premium, 4),
            "status": get_status("DISCONTINUITY_PREMIUM", ensemble_result.discontinuity_premium)
        })
        # Allocation Multiplier
        rows.append({
            "date": ensemble_date,
            "index_id": "ALLOC_MULTIPLIER",
            "value": round(ensemble_result.allocation_multiplier, 4),
            "status": get_status("ALLOC_MULTIPLIER", ensemble_result.allocation_multiplier)
        })
        # Base Probability (for comparison)
        rows.append({
            "date": ensemble_date,
            "index_id": "BASE_REC_PROB",
            "value": round(ensemble_result.base_probability, 4),
            "status": get_status("REC_PROB", ensemble_result.base_probability)
        })

        # Persist ensemble outputs to today if the ensemble's anchor date
        # is behind df.index.max() (typically by one publish-window day).
        ensemble_outputs = [
            ("WARNING_LEVEL", warning_level_value, warning_result.overall_level.name),
            ("ENSEMBLE_RISK", round(ensemble_result.adjusted_probability, 4), ensemble_result.regime.name),
            ("DISCONTINUITY_PREMIUM", round(ensemble_result.discontinuity_premium, 4),
                get_status("DISCONTINUITY_PREMIUM", ensemble_result.discontinuity_premium)),
            ("ALLOC_MULTIPLIER", round(ensemble_result.allocation_multiplier, 4),
                get_status("ALLOC_MULTIPLIER", ensemble_result.allocation_multiplier)),
            ("BASE_REC_PROB", round(ensemble_result.base_probability, 4),
                get_status("REC_PROB", ensemble_result.base_probability)),
        ]
        try:
            ensemble_ts = pd.Timestamp(ensemble_date)
        except Exception:
            ensemble_ts = None
        if ensemble_ts is not None and ensemble_ts < today_stamp:
            for d in pd.date_range(ensemble_ts + pd.Timedelta(days=1), today_stamp, freq="D"):
                for eid, val, st in ensemble_outputs:
                    rows.append({
                        "date": d.strftime("%Y-%m-%d"),
                        "index_id": eid,
                        "value": val,
                        "status": st,
                    })

    result_df = pd.DataFrame(rows)
    print(f"   Generated {len(result_df)} index observations")

    return result_df


def write_indices_to_db(conn: sqlite3.Connection, indices_df: pd.DataFrame):
    """Write computed indices to lighthouse_indices table.

    For each index_id present in indices_df, all existing rows for that
    index_id are deleted before re-insert. This is the only way to remove
    rows that the previous run produced but the current run did not — e.g.
    when a composite's strict formula no longer stamps the recent tail
    because an input went stale. Without the delete, those stale rows
    would persist and silently lie to downstream readers.
    """
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS lighthouse_indices (
        date TEXT,
        index_id TEXT,
        value REAL,
        status TEXT,
        PRIMARY KEY (date, index_id)
    )''')

    # Per-index clean re-write.
    ids = sorted(indices_df["index_id"].unique())
    for index_id in ids:
        c.execute("DELETE FROM lighthouse_indices WHERE index_id = ?", (index_id,))
    deleted = c.rowcount  # last DELETE's count, not cumulative — informational only

    for _, row in indices_df.iterrows():
        c.execute("""
            INSERT INTO lighthouse_indices (date, index_id, value, status)
            VALUES (?, ?, ?, ?)
        """, (row["date"], row["index_id"], row["value"], row["status"]))

    conn.commit()
    print(f"   Cleaned and rewrote {len(indices_df)} rows across {len(ids)} index_ids in lighthouse_indices")


def verify_indices(conn: sqlite3.Connection):
    """Verify latest index values against expected thresholds."""
    print("\n--- Verification: Latest Index Values ---")

    query = """
        SELECT index_id, value, status, date
        FROM lighthouse_indices
        WHERE date = (SELECT MAX(date) FROM lighthouse_indices)
        ORDER BY index_id
    """
    latest = pd.read_sql(query, conn)

    print(f"\nLatest values ({latest['date'].iloc[0] if len(latest) > 0 else 'N/A'}):")
    print("-" * 50)

    # Expected ranges from framework
    expected = {
        "LFI": {"range": (0.5, 1.5), "current_expect": "~0.93 (Elevated)"},
        "LCI": {"range": (-1.0, -0.5), "current_expect": "~-0.8 (Scarce)"},
        "CLG": {"range": (-2.0, 0.0), "current_expect": "~-1.84 (Mispriced)"},
        "MRI": {"range": (0.5, 1.5), "current_expect": "~1.1 (High Risk)"},
    }

    for _, row in latest.iterrows():
        exp = expected.get(row["index_id"], {})
        exp_range = exp.get("range", (None, None))
        exp_current = exp.get("current_expect", "")

        in_range = ""
        if exp_range[0] is not None:
            if exp_range[0] <= row["value"] <= exp_range[1]:
                in_range = "✓"
            else:
                in_range = "⚠"

        status_str = row['status'] if row['status'] else "N/A"
        print(f"   {row['index_id']:10} {row['value']:>8.3f}  [{status_str:20}] {in_range} {exp_current}")

    print("-" * 50)


# ==========================================
# CLI
# ==========================================

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Compute Lighthouse Macro Proprietary Indices")
    parser.add_argument("--latest", action="store_true", help="Only compute latest date")
    parser.add_argument("--verify", action="store_true", help="Verify against expected values")
    parser.add_argument("--dry-run", action="store_true", help="Compute but don't write to database")
    parser.add_argument("--no-dashboard", action="store_true", help="Skip rebuilding the nowcast dashboard")
    parser.add_argument("--no-open", action="store_true", help="Skip auto-opening the dashboard in browser")

    args = parser.parse_args()

    print("=" * 70)
    print("LIGHTHOUSE MACRO - PROPRIETARY INDEX COMPUTATION")
    print(f"Database: {DB_PATH}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    conn = sqlite3.connect(DB_PATH)

    # Compute indices
    indices_df = compute_all_indices(conn, latest_only=args.latest)

    # Write to database
    if not args.dry_run:
        print("\n--- Writing to Database ---")
        write_indices_to_db(conn, indices_df)
    else:
        print("\n--- Dry Run: Skipping database write ---")

    # Verify
    if args.verify or not args.dry_run:
        verify_indices(conn)

    conn.close()

    # Rebuild the nowcast dashboard so the same file Bob always opens
    # reflects the latest indicator state. Runs in-process; failures are
    # logged but never block the pipeline.
    if not args.dry_run and not args.no_dashboard:
        print("\n--- Rebuilding Nowcast Dashboard ---")
        try:
            sys.path.insert(0, "/Users/bob/LHM/Scripts/dashboards")
            import nowcast_dashboard  # noqa: WPS433
            latest, history, run_date = nowcast_dashboard.fetch_state()
            html = nowcast_dashboard.render_dashboard(latest, history, run_date)
            nowcast_dashboard.write_dashboard(html)
            print(f"   Wrote {nowcast_dashboard.OUTPUT_PATH}")
            if not args.no_open:
                nowcast_dashboard.open_in_browser()
        except Exception as e:  # noqa: BLE001
            print(f"   Dashboard rebuild failed: {e}")

    print("\n" + "=" * 70)
    print("INDEX COMPUTATION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
