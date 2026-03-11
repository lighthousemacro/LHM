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
    "GCI_Gov": [
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

    # Validation-informed weights (sum to 1.0)
    lfi = (0.15 * z_longterm.fillna(0) +    # Reduced from 0.35
           0.45 * z_quits.fillna(0) +        # Increased from 0.35
           0.40 * z_hires_quits.fillna(0))   # Increased from 0.30

    # Only return where we have at least one component
    valid_mask = z_longterm.notna() | z_quits.notna() | hires_quits_ratio.notna()
    lfi = lfi.where(valid_mask)

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

    # Weighted composite (simplified with available components)
    lci = (0.30 * z_reserves.fillna(0) +
           0.25 * z_rrp.fillna(0) +
           0.25 * z_effr_sofr.fillna(0) +
           0.20 * z_nfci.fillna(0))

    # Only return where we have at least one component
    valid_mask = z_reserves.notna() | z_rrp.notna() | z_nfci.notna()
    lci = lci.where(valid_mask)

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

    # Weighted composite
    lpi = (0.25 * z_quits.fillna(0) +
           0.20 * z_hires_quits.fillna(0) +
           0.20 * z_longterm.fillna(0) +
           0.20 * z_claims.fillna(0) +
           0.15 * z_lfpr.fillna(0))

    valid_mask = z_quits.notna() | z_claims.notna() | z_lfpr.notna()
    lpi = lpi.where(valid_mask)

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

    # Weighted composite
    pci = (0.35 * z_pce_3m.fillna(0) +
           0.25 * z_shelter.fillna(0) +
           0.20 * z_sticky.fillna(0) +
           0.20 * z_5y5y.fillna(0))

    valid_mask = z_pce_3m.notna() | z_shelter.notna() | z_5y5y.notna()
    pci = pci.where(valid_mask)

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

    # Weighted composite (simplified)
    gci = (0.40 * z_ip.fillna(0) +
           0.30 * z_retail.fillna(0) +
           0.30 * z_starts.fillna(0))

    valid_mask = z_ip.notna() | z_retail.notna() | z_starts.notna()
    gci = gci.where(valid_mask)

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

    hci = (0.25 * z_starts.fillna(0) +
           0.25 * z_sales.fillna(0) +
           0.20 * z_supply.fillna(0) +
           0.15 * z_cs.fillna(0) +
           0.15 * z_mortgage.fillna(0))

    valid_mask = z_starts.notna() | z_sales.notna() | z_cs.notna()
    hci = hci.where(valid_mask)

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

    cci = (0.35 * z_sentiment.fillna(0) +
           0.35 * z_saving.fillna(0) +
           0.30 * z_delinq.fillna(0))

    valid_mask = z_sentiment.notna() | z_saving.notna() | z_delinq.notna()
    cci = cci.where(valid_mask)

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

    bci = (0.35 * z_ci.fillna(0) +
           0.35 * z_bus.fillna(0) +
           0.30 * z_hy.fillna(0))

    valid_mask = z_ci.notna() | z_bus.notna() | z_hy.notna()
    bci = bci.where(valid_mask)

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

    tci = (0.50 * z_dollar.fillna(0) +
           0.50 * z_eur.fillna(0))

    valid_mask = z_dollar.notna() | z_eur.notna()
    tci = tci.where(valid_mask)

    return tci


def compute_gci_gov(df: pd.DataFrame) -> pd.Series:
    """
    Government Pillar Composite Index (GCI-Gov)
    """
    # Debt to GDP
    debt_gdp = df.get("Debt_to_GDP", pd.Series(dtype=float))
    z_debt = compute_zscore(debt_gdp, window=8)  # Quarterly

    # Term Premium
    z_term = df.get("Term_Premium_10Y_z", pd.Series(dtype=float))

    gci_gov = (0.50 * z_debt.fillna(0) +
               0.50 * z_term.fillna(0))

    valid_mask = z_debt.notna() | z_term.notna()
    gci_gov = gci_gov.where(valid_mask)

    return gci_gov


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

    fci = (0.25 * z_hy.fillna(0) +
           0.25 * z_nfci.fillna(0) +
           0.25 * z_curve.fillna(0) +
           0.15 * z_vix.fillna(0) +
           0.10 * lci.fillna(0))

    valid_mask = z_hy.notna() | z_nfci.notna() | z_curve.notna()
    fci = fci.where(valid_mask)

    return fci


def compute_mri(lpi: pd.Series, pci: pd.Series, gci: pd.Series,
               hci: pd.Series, cci: pd.Series, bci: pd.Series,
               tci: pd.Series, gci_gov: pd.Series, fci: pd.Series,
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
    # Validation-informed weights (sum to 1.0)
    mri = (0.33 * (-lpi).fillna(0) +     # Labor - highest weight (was 0.15)
           0.03 * pci.fillna(0) +         # Prices - reduced (was 0.10)
           0.02 * (-gci).fillna(0) +      # Growth - reduced (was 0.15)
           0.02 * (-hci).fillna(0) +      # Housing - reduced (was 0.08)
           0.02 * (-cci).fillna(0) +      # Consumer - reduced (was 0.10)
           0.13 * (-bci).fillna(0) +      # Business - slight increase (was 0.10)
           0.12 * (-tci).fillna(0) +      # Trade - increased (was 0.07)
           0.12 * gci_gov.fillna(0) +     # Government - slight increase (was 0.10)
           0.07 * (-fci).fillna(0) +      # Financial - increased (was 0.05)
           0.14 * (-lci).fillna(0))       # Plumbing - increased (was 0.10)

    # Need at least a few components to be valid
    valid_mask = lpi.notna() | gci.notna() | lci.notna()
    mri = mri.where(valid_mask)

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

    ldi = (z_quits.fillna(0) + z_hires_quits.fillna(0) + z_quits_claims.fillna(0)) / 3

    valid_mask = z_quits.notna() | hires_quits_ratio.notna()
    ldi = ldi.where(valid_mask)

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

    yfs = (z_10y2y.fillna(0) + z_10y3m.fillna(0) + z_sofr_effr.fillna(0)) / 3

    valid_mask = z_10y2y.notna() | z_10y3m.notna() | z_sofr_effr.notna()
    yfs = yfs.where(valid_mask)

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

    # Compute weighted sum
    msi = pd.Series(0.0, index=market_df.index, name="MSI")
    for name, (series, weight) in components.items():
        aligned = series.reindex(msi.index)
        msi = msi + (aligned * weight).fillna(0)

    # Only keep values where we have at least some data
    valid_mask = sum(
        (~components[k][0].reindex(msi.index).isna()).astype(int)
        for k in components
    ) >= 3  # Require at least 3 components

    msi = msi.where(valid_mask)

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

    # AAII Bull-Bear spread (INVERTED: low bull-bear = high fear = high SPI)
    if 'AAII_Bull_Bear_Spread' in market_df.columns:
        components['aaii'] = (
            compute_zscore(-market_df['AAII_Bull_Bear_Spread']),  # Inverted
            0.15 / 0.30  # 0.50
        )

    if not components:
        print("      Warning: No valid SPI components found")
        return pd.Series(dtype=float, name="SPI")

    # Compute weighted sum
    spi = pd.Series(0.0, index=market_df.index, name="SPI")
    for name, (series, weight) in components.items():
        aligned = series.reindex(spi.index)
        spi = spi + (aligned * weight).fillna(0)

    # Only keep values where we have at least some data
    valid_mask = sum(
        (~components[k][0].reindex(spi.index).isna()).astype(int)
        for k in components
    ) >= 1

    spi = spi.where(valid_mask)

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

    if latest_only:
        # Only compute for last available date
        df = df.iloc[[-1]]

    print("\n--- Computing Indices ---")

    # Compute pillar composites first
    print("   Computing LPI (Labor Pillar)...")
    lpi = compute_lpi(df)

    print("   Computing PCI (Prices Pillar)...")
    pci = compute_pci(df)

    print("   Computing GCI (Growth Pillar)...")
    gci = compute_gci(df)

    print("   Computing HCI (Housing Pillar)...")
    hci = compute_hci(df)

    print("   Computing CCI (Consumer Pillar)...")
    cci = compute_cci(df)

    print("   Computing BCI (Business Pillar)...")
    bci = compute_bci(df)

    print("   Computing TCI (Trade Pillar)...")
    tci = compute_tci(df)

    print("   Computing GCI-Gov (Government Pillar)...")
    gci_gov = compute_gci_gov(df)

    # Compute key indices
    print("   Computing LFI (Labor Fragility Index)...")
    lfi = compute_lfi(df)

    print("   Computing LCI (Liquidity Cushion Index)...")
    lci = compute_lci(df)

    print("   Computing FCI (Financial Conditions)...")
    fci = compute_fci(df, lci)

    print("   Computing CLG (Credit-Labor Gap)...")
    clg = compute_clg(df, lfi)

    print("   Computing MRI (Macro Risk Index)...")
    mri = compute_mri(lpi, pci, gci, hci, cci, bci, tci, gci_gov, fci, lci)

    # Additional indicators
    print("   Computing LDI (Labor Dynamism Index)...")
    ldi = compute_ldi(df)

    print("   Computing YFS (Yield-Funding Stress)...")
    yfs = compute_yfs(df)

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
        "GCI_Gov": gci_gov,
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

    result_df = pd.DataFrame(rows)
    print(f"   Generated {len(result_df)} index observations")

    return result_df


def write_indices_to_db(conn: sqlite3.Connection, indices_df: pd.DataFrame):
    """Write computed indices to lighthouse_indices table."""
    c = conn.cursor()

    # Create table if not exists
    c.execute('''CREATE TABLE IF NOT EXISTS lighthouse_indices (
        date TEXT,
        index_id TEXT,
        value REAL,
        status TEXT,
        PRIMARY KEY (date, index_id)
    )''')

    # Insert/replace data
    for _, row in indices_df.iterrows():
        c.execute("""
            INSERT OR REPLACE INTO lighthouse_indices (date, index_id, value, status)
            VALUES (?, ?, ?, ?)
        """, (row["date"], row["index_id"], row["value"], row["status"]))

    conn.commit()
    print(f"   Wrote {len(indices_df)} rows to lighthouse_indices")


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

    print("\n" + "=" * 70)
    print("INDEX COMPUTATION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
