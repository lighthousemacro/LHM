"""
LIGHTHOUSE MACRO - HORIZON DATASET BUILDER
==========================================
Prepares analysis-ready dataset for charting and model ingestion.

Output:
- 200-250 high-value series
- Aligned on shortest timeframe (per series first obs to yesterday)
- Gaps interpolated (not backfilled)
- Raw + 1-5 transformations per series
- SQLite table + CSV export

Now uses centralized transforms from lighthouse package.
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

from lighthouse.config import DB_PATH, OUTPUT_DIR
from lighthouse.transforms import TRANSFORM_REGISTRY, get_periods_for_freq

# ==========================================
# CONFIGURATION
# ==========================================

OUTPUT_CSV = OUTPUT_DIR / "Horizon_Dataset.csv"
YESTERDAY = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

# ==========================================
# SERIES SELECTION - The 200-250 most chart-worthy
# ==========================================

HORIZON_SERIES = {
    # ===== LABOR MARKET (30) =====
    "UNRATE": {"name": "Unemployment_Rate_U3", "freq": "M", "transforms": ["yoy_diff", "mom_diff", "z"]},
    "U6RATE": {"name": "Unemployment_Rate_U6", "freq": "M", "transforms": ["yoy_diff", "mom_diff", "z"]},
    "U1RATE": {"name": "Unemployment_Rate_U1", "freq": "M", "transforms": ["yoy_diff", "z"]},
    "U2RATE": {"name": "Unemployment_Rate_U2", "freq": "M", "transforms": ["yoy_diff", "z"]},
    "CIVPART": {"name": "LFPR", "freq": "M", "transforms": ["yoy_diff", "z"]},
    "LNS11300060": {"name": "LFPR_Prime_Age_25_54", "freq": "M", "transforms": ["yoy_diff", "z"]},
    "PAYEMS": {"name": "Nonfarm_Payrolls", "freq": "M", "transforms": ["yoy_pct", "mom_diff", "mom_diff_3ma"]},
    "ICSA": {"name": "Initial_Claims", "freq": "W", "transforms": ["yoy_pct", "4wk_ma", "z"]},
    "CCSA": {"name": "Continued_Claims", "freq": "W", "transforms": ["yoy_pct", "4wk_ma", "z"]},
    "JTS1000JOR": {"name": "JOLTS_Openings_Rate", "freq": "M", "transforms": ["yoy_diff", "z"]},
    "JTS1000QUR": {"name": "JOLTS_Quits_Rate", "freq": "M", "transforms": ["yoy_diff", "z"]},
    "JTS1000HIR": {"name": "JOLTS_Hires_Rate", "freq": "M", "transforms": ["yoy_diff", "z"]},
    "UEMPMEAN": {"name": "Mean_Unemployment_Duration", "freq": "M", "transforms": ["yoy_pct", "z"]},
    "UEMP27OV": {"name": "Unemployed_27wks_Plus", "freq": "M", "transforms": ["yoy_pct", "z"]},
    "LNS12032194": {"name": "Part_Time_Economic_Reasons", "freq": "M", "transforms": ["yoy_pct", "z"]},
    "LNS14000003": {"name": "Unemployment_White", "freq": "M", "transforms": ["yoy_diff", "z"]},
    "LNS14000006": {"name": "Unemployment_Black", "freq": "M", "transforms": ["yoy_diff", "z"]},
    "LNS14000009": {"name": "Unemployment_Hispanic", "freq": "M", "transforms": ["yoy_diff", "z"]},
    "LNS14000036": {"name": "Unemployment_25_54", "freq": "M", "transforms": ["yoy_diff", "z"]},
    "LNS14024230": {"name": "Unemployment_55_Plus", "freq": "M", "transforms": ["yoy_diff", "z"]},

    # BLS Sector Jobs
    "BLS_CES0000000001": {"name": "Jobs_Total_Nonfarm", "freq": "M", "transforms": ["yoy_pct", "mom_diff"]},
    "BLS_CES2000000001": {"name": "Jobs_Construction", "freq": "M", "transforms": ["yoy_pct", "mom_diff"]},
    "BLS_CES3000000001": {"name": "Jobs_Manufacturing", "freq": "M", "transforms": ["yoy_pct", "mom_diff"]},
    "BLS_CES5500000001": {"name": "Jobs_Financial", "freq": "M", "transforms": ["yoy_pct", "mom_diff"]},
    "BLS_CES6000000001": {"name": "Jobs_Professional_Business", "freq": "M", "transforms": ["yoy_pct", "mom_diff"]},
    "BLS_CES6500000001": {"name": "Jobs_Education_Health", "freq": "M", "transforms": ["yoy_pct", "mom_diff"]},
    "BLS_CES7000000001": {"name": "Jobs_Leisure_Hospitality", "freq": "M", "transforms": ["yoy_pct", "mom_diff"]},
    "BLS_CES9000000001": {"name": "Jobs_Government", "freq": "M", "transforms": ["yoy_pct", "mom_diff"]},

    # ===== INFLATION (30) =====
    "CPIAUCSL": {"name": "CPI_Headline", "freq": "M", "transforms": ["yoy_pct", "mom_pct", "3m_ann", "6m_ann"]},
    "CPILFESL": {"name": "CPI_Core", "freq": "M", "transforms": ["yoy_pct", "mom_pct", "3m_ann", "6m_ann"]},
    "PCEPI": {"name": "PCE_Headline", "freq": "M", "transforms": ["yoy_pct", "mom_pct", "3m_ann", "6m_ann"]},
    "PCEPILFE": {"name": "PCE_Core", "freq": "M", "transforms": ["yoy_pct", "mom_pct", "3m_ann", "6m_ann"]},
    "MEDCPIM158SFRBCLE": {"name": "Median_CPI", "freq": "M", "transforms": ["yoy_pct", "3m_ann"]},
    "CORESTICKM159SFRBATL": {"name": "Sticky_Core_CPI", "freq": "M", "transforms": ["yoy_pct", "3m_ann"]},
    "CUSR0000SAH1": {"name": "CPI_Shelter", "freq": "M", "transforms": ["yoy_pct", "mom_pct", "3m_ann"]},
    "CUSR0000SEHA": {"name": "CPI_Rent_Primary", "freq": "M", "transforms": ["yoy_pct", "mom_pct"]},
    "CUSR0000SEHC": {"name": "CPI_OER", "freq": "M", "transforms": ["yoy_pct", "mom_pct"]},
    "CUSR0000SAM1": {"name": "CPI_Medical_Services", "freq": "M", "transforms": ["yoy_pct"]},
    "CUSR0000SAS4": {"name": "CPI_Transport_Services", "freq": "M", "transforms": ["yoy_pct"]},
    "CUSR0000SETB01": {"name": "CPI_Gasoline", "freq": "M", "transforms": ["yoy_pct", "mom_pct"]},
    "CUSR0000SETA02": {"name": "CPI_Used_Cars", "freq": "M", "transforms": ["yoy_pct", "mom_pct"]},
    "CUSR0000SAF11": {"name": "CPI_Food_Home", "freq": "M", "transforms": ["yoy_pct"]},
    "CUSR0000SEFV": {"name": "CPI_Food_Away", "freq": "M", "transforms": ["yoy_pct"]},
    "PCEDG": {"name": "PCE_Durable_Goods", "freq": "M", "transforms": ["yoy_pct"]},
    "PCEND": {"name": "PCE_Nondurable_Goods", "freq": "M", "transforms": ["yoy_pct"]},
    "PCES": {"name": "PCE_Services", "freq": "M", "transforms": ["yoy_pct"]},
    "T10YIE": {"name": "Breakeven_10Y", "freq": "D", "transforms": ["diff", "z"]},
    "T5YIE": {"name": "Breakeven_5Y", "freq": "D", "transforms": ["diff", "z"]},
    "T5YIFR": {"name": "Forward_Inflation_5Y", "freq": "D", "transforms": ["diff", "z"]},

    # ===== RATES & YIELDS (25) =====
    "FEDFUNDS": {"name": "Fed_Funds", "freq": "M", "transforms": ["diff", "yoy_diff"]},
    "DGS1MO": {"name": "Treasury_1M", "freq": "D", "transforms": ["diff"]},
    "DGS3MO": {"name": "Treasury_3M", "freq": "D", "transforms": ["diff"]},
    "DGS6MO": {"name": "Treasury_6M", "freq": "D", "transforms": ["diff"]},
    "DGS1": {"name": "Treasury_1Y", "freq": "D", "transforms": ["diff", "yoy_diff"]},
    "DGS2": {"name": "Treasury_2Y", "freq": "D", "transforms": ["diff", "yoy_diff"]},
    "DGS5": {"name": "Treasury_5Y", "freq": "D", "transforms": ["diff", "yoy_diff"]},
    "DGS10": {"name": "Treasury_10Y", "freq": "D", "transforms": ["diff", "yoy_diff"]},
    "DGS30": {"name": "Treasury_30Y", "freq": "D", "transforms": ["diff", "yoy_diff"]},
    "T10Y2Y": {"name": "Curve_10Y_2Y", "freq": "D", "transforms": ["diff", "z"]},
    "T10Y3M": {"name": "Curve_10Y_3M", "freq": "D", "transforms": ["diff", "z"]},
    "T10YFF": {"name": "Spread_10Y_FF", "freq": "D", "transforms": ["diff", "z"]},
    "T5YFF": {"name": "Spread_5Y_FF", "freq": "D", "transforms": ["diff"]},
    "DFII5": {"name": "TIPS_5Y", "freq": "D", "transforms": ["diff"]},
    "DFII10": {"name": "TIPS_10Y", "freq": "D", "transforms": ["diff"]},
    "THREEFYTP10": {"name": "Term_Premium_10Y", "freq": "D", "transforms": ["diff", "z"]},
    "MORTGAGE30US": {"name": "Mortgage_30Y", "freq": "W", "transforms": ["diff", "yoy_diff"]},
    "BAMLH0A0HYM2": {"name": "HY_OAS", "freq": "D", "transforms": ["diff", "yoy_diff", "z"]},
    "BAMLC0A0CM": {"name": "IG_OAS", "freq": "D", "transforms": ["diff", "yoy_diff", "z"]},

    # NY Fed Reference Rates
    "NYFED_SOFR": {"name": "SOFR", "freq": "D", "transforms": ["diff"]},
    "NYFED_EFFR": {"name": "EFFR", "freq": "D", "transforms": ["diff"]},
    "NYFED_OBFR": {"name": "OBFR", "freq": "D", "transforms": ["diff"]},
    "NYFED_SOFR_Volume": {"name": "SOFR_Volume", "freq": "D", "transforms": ["yoy_pct", "z"]},

    # ===== LIQUIDITY & FED (20) =====
    "WALCL": {"name": "Fed_Balance_Sheet", "freq": "W", "transforms": ["yoy_pct", "wow_diff"]},
    "RRPONTSYD": {"name": "RRP_Usage", "freq": "D", "transforms": ["diff", "yoy_diff", "z"]},
    "TOTRESNS": {"name": "Bank_Reserves", "freq": "M", "transforms": ["yoy_pct", "mom_pct"]},
    "M2SL": {"name": "M2", "freq": "M", "transforms": ["yoy_pct", "mom_pct"]},
    "WTREGEN": {"name": "Treasury_General_Account", "freq": "W", "transforms": ["diff", "z"]},
    "H41RESPPALDKNWW": {"name": "Fed_RRP_Outstanding", "freq": "W", "transforms": ["diff"]},
    "NFCI": {"name": "Chicago_NFCI", "freq": "W", "transforms": ["diff", "z"]},
    "ANFCI": {"name": "Adjusted_NFCI", "freq": "W", "transforms": ["diff", "z"]},
    "STLFSI4": {"name": "StLouis_FSI", "freq": "W", "transforms": ["diff", "z"]},

    # OFR
    "OFR_FSI": {"name": "OFR_FSI", "freq": "D", "transforms": ["diff", "z"]},
    "OFR_FSI_Credit": {"name": "OFR_FSI_Credit", "freq": "D", "transforms": ["diff", "z"]},
    "OFR_FSI_Funding": {"name": "OFR_FSI_Funding", "freq": "D", "transforms": ["diff", "z"]},
    "OFR_FSI_Volatility": {"name": "OFR_FSI_Volatility", "freq": "D", "transforms": ["diff", "z"]},
    "OFR_FSI_US": {"name": "OFR_FSI_US", "freq": "D", "transforms": ["diff", "z"]},

    # ===== GROWTH & ACTIVITY (25) =====
    "GDP": {"name": "GDP_Nominal", "freq": "Q", "transforms": ["yoy_pct", "qoq_pct"]},
    "GDPC1": {"name": "GDP_Real", "freq": "Q", "transforms": ["yoy_pct", "qoq_pct"]},
    "INDPRO": {"name": "Industrial_Production", "freq": "M", "transforms": ["yoy_pct", "mom_pct", "3m_ann"]},
    "RSAFS": {"name": "Retail_Sales", "freq": "M", "transforms": ["yoy_pct", "mom_pct"]},
    "UMCSENT": {"name": "Consumer_Sentiment", "freq": "M", "transforms": ["yoy_pct", "mom_diff", "z"]},
    "TOTALSL": {"name": "Consumer_Credit", "freq": "M", "transforms": ["yoy_pct"]},
    "PSAVERT": {"name": "Saving_Rate", "freq": "M", "transforms": ["diff", "z"]},
    "TDSP": {"name": "Debt_Service_Ratio", "freq": "Q", "transforms": ["diff", "z"]},

    # Credit/Lending
    "DRTSCILM": {"name": "LO_Survey_CI_Tightening", "freq": "Q", "transforms": ["diff", "z"]},
    "DRTSCLCC": {"name": "LO_Survey_CC_Tightening", "freq": "Q", "transforms": ["diff", "z"]},
    "TOTCI": {"name": "CI_Loans", "freq": "M", "transforms": ["yoy_pct"]},
    "BUSLOANS": {"name": "Business_Loans", "freq": "M", "transforms": ["yoy_pct"]},
    "CONSUMER": {"name": "Consumer_Loans", "freq": "M", "transforms": ["yoy_pct"]},
    "REALLN": {"name": "Real_Estate_Loans", "freq": "M", "transforms": ["yoy_pct"]},

    # ===== HOUSING (20) =====
    "HOUST": {"name": "Housing_Starts", "freq": "M", "transforms": ["yoy_pct", "mom_pct", "z"]},
    "HOUST1F": {"name": "Housing_Starts_1Unit", "freq": "M", "transforms": ["yoy_pct"]},
    "PERMIT": {"name": "Building_Permits", "freq": "M", "transforms": ["yoy_pct", "mom_pct"]},
    "CSUSHPINSA": {"name": "Case_Shiller_Home_Prices", "freq": "M", "transforms": ["yoy_pct", "mom_pct"]},
    "MSPUS": {"name": "Median_Home_Price", "freq": "Q", "transforms": ["yoy_pct"]},
    "HSN1F": {"name": "New_Home_Sales", "freq": "M", "transforms": ["yoy_pct", "mom_pct"]},
    "EXHOSLUSM495S": {"name": "Existing_Home_Sales", "freq": "M", "transforms": ["yoy_pct", "mom_pct"]},
    "MSACSR": {"name": "Months_Supply", "freq": "M", "transforms": ["diff", "z"]},

    # ===== DELINQUENCIES (15) =====
    "DRALACBS": {"name": "Delinquency_All_Loans", "freq": "Q", "transforms": ["diff", "yoy_diff", "z"]},
    "DRSFRMACBS": {"name": "Delinquency_Mortgage", "freq": "Q", "transforms": ["diff", "yoy_diff", "z"]},
    "DRCCLACBS": {"name": "Delinquency_Credit_Card", "freq": "Q", "transforms": ["diff", "yoy_diff", "z"]},
    "DRCLACBS": {"name": "Delinquency_Consumer", "freq": "Q", "transforms": ["diff", "yoy_diff", "z"]},
    "DRBLACBS": {"name": "Delinquency_Business", "freq": "Q", "transforms": ["diff", "yoy_diff", "z"]},
    "DRCRELEXFACBS": {"name": "Delinquency_CRE", "freq": "Q", "transforms": ["diff", "yoy_diff", "z"]},

    # ===== FISCAL (10) =====
    "GFDEBTN": {"name": "Federal_Debt", "freq": "Q", "transforms": ["yoy_pct"]},
    "GFDEGDQ188S": {"name": "Debt_to_GDP", "freq": "Q", "transforms": ["diff"]},
    "FYFSD": {"name": "Federal_Surplus_Deficit", "freq": "A", "transforms": ["diff"]},
    "FGRECPT": {"name": "Federal_Receipts", "freq": "Q", "transforms": ["yoy_pct"]},
    "FGEXPND": {"name": "Federal_Expenditures", "freq": "Q", "transforms": ["yoy_pct"]},

    # ===== VOLATILITY & RISK (10) =====
    "VIXCLS": {"name": "VIX", "freq": "D", "transforms": ["diff", "z", "20d_ma"]},
    "DCOILWTICO": {"name": "WTI_Crude", "freq": "D", "transforms": ["yoy_pct", "mom_pct"]},
    "DTWEXBGS": {"name": "Dollar_Index", "freq": "D", "transforms": ["yoy_pct", "mom_pct"]},
    "DEXUSEU": {"name": "EUR_USD", "freq": "D", "transforms": ["yoy_pct"]},
    "DEXJPUS": {"name": "JPY_USD", "freq": "D", "transforms": ["yoy_pct"]},

    # ===== BEA NATIONAL ACCOUNTS (15) =====
    "BEA_GDP_Components_Gross_domestic_product": {"name": "BEA_GDP", "freq": "Q", "transforms": ["yoy_pct", "qoq_pct"]},
    "BEA_GDP_Components_Personal_consumption_expenditures": {"name": "BEA_PCE", "freq": "Q", "transforms": ["yoy_pct", "qoq_pct"]},
    "BEA_GDP_Components_Gross_private_domestic_investment": {"name": "BEA_Investment", "freq": "Q", "transforms": ["yoy_pct", "qoq_pct"]},
    "BEA_GDP_Components_Net_exports_of_goods_and_services": {"name": "BEA_Net_Exports", "freq": "Q", "transforms": ["diff"]},
    "BEA_GDP_Components_Government_consumption_expenditures_and_gross_investment": {"name": "BEA_Govt", "freq": "Q", "transforms": ["yoy_pct"]},
    "BEA_Personal_Income_Personal_income": {"name": "BEA_Personal_Income", "freq": "Q", "transforms": ["yoy_pct"]},
    "BEA_Personal_Income_Disposable_personal_income": {"name": "BEA_DPI", "freq": "Q", "transforms": ["yoy_pct"]},
    "BEA_Personal_Income_Personal_saving": {"name": "BEA_Personal_Saving", "freq": "Q", "transforms": ["diff"]},
    "BEA_Corporate_Profits_Profits_after_tax_with_IVA_and_CCAdj": {"name": "BEA_Corp_Profits", "freq": "Q", "transforms": ["yoy_pct"]},
}


# ==========================================
# TRANSFORMATION FUNCTIONS
# ==========================================

def apply_transforms(df, transforms, freq):
    """Apply transformations to a series."""
    result = pd.DataFrame(index=df.index)
    result["raw"] = df["value"]

    for t in transforms:
        if t == "yoy_pct":
            # Year-over-year percent change
            if freq == "D":
                result["yoy_pct"] = df["value"].pct_change(252) * 100
            elif freq == "W":
                result["yoy_pct"] = df["value"].pct_change(52) * 100
            elif freq == "M":
                result["yoy_pct"] = df["value"].pct_change(12) * 100
            elif freq == "Q":
                result["yoy_pct"] = df["value"].pct_change(4) * 100
            else:
                result["yoy_pct"] = df["value"].pct_change(1) * 100

        elif t == "yoy_diff":
            # Year-over-year difference (for rates)
            if freq == "D":
                result["yoy_diff"] = df["value"].diff(252)
            elif freq == "W":
                result["yoy_diff"] = df["value"].diff(52)
            elif freq == "M":
                result["yoy_diff"] = df["value"].diff(12)
            elif freq == "Q":
                result["yoy_diff"] = df["value"].diff(4)
            else:
                result["yoy_diff"] = df["value"].diff(1)

        elif t == "mom_pct":
            # Month-over-month percent change
            result["mom_pct"] = df["value"].pct_change(1) * 100

        elif t == "mom_diff":
            # Month-over-month difference
            result["mom_diff"] = df["value"].diff(1)

        elif t == "mom_diff_3ma":
            # 3-month moving average of MoM diff
            result["mom_diff_3ma"] = df["value"].diff(1).rolling(3).mean()

        elif t == "qoq_pct":
            # Quarter-over-quarter percent change
            result["qoq_pct"] = df["value"].pct_change(1) * 100

        elif t == "diff":
            # Simple difference
            result["diff"] = df["value"].diff(1)

        elif t == "wow_diff":
            # Week-over-week difference
            result["wow_diff"] = df["value"].diff(1)

        elif t == "3m_ann":
            # 3-month annualized rate
            result["3m_ann"] = (((df["value"] / df["value"].shift(3)) ** 4) - 1) * 100

        elif t == "6m_ann":
            # 6-month annualized rate
            result["6m_ann"] = (((df["value"] / df["value"].shift(6)) ** 2) - 1) * 100

        elif t == "z":
            # Z-score (rolling 2-year)
            if freq == "D":
                window = 504
            elif freq == "W":
                window = 104
            elif freq == "M":
                window = 24
            else:
                window = 8
            rolling_mean = df["value"].rolling(window, min_periods=window//2).mean()
            rolling_std = df["value"].rolling(window, min_periods=window//2).std()
            result["z"] = (df["value"] - rolling_mean) / rolling_std

        elif t == "4wk_ma":
            # 4-week moving average
            result["4wk_ma"] = df["value"].rolling(4).mean()

        elif t == "20d_ma":
            # 20-day moving average
            result["20d_ma"] = df["value"].rolling(20).mean()

    return result


def interpolate_series(df, first_obs, last_obs):
    """
    Interpolate gaps ONLY between first observation and last_obs.
    Does NOT backfill before first_obs.
    """
    # Trim to valid range
    df = df[(df.index >= first_obs) & (df.index <= last_obs)].copy()

    # Create complete date range
    full_range = pd.date_range(start=first_obs, end=last_obs, freq='D')
    df = df.reindex(full_range)

    # Interpolate (linear for most, could use other methods)
    df = df.interpolate(method='linear', limit_direction='forward')

    return df


# ==========================================
# MAIN BUILD FUNCTION
# ==========================================

def build_horizon_dataset():
    """Build the Horizon-ready dataset."""
    print("=" * 70)
    print("LIGHTHOUSE MACRO - HORIZON DATASET BUILDER")
    print(f"Target: {len(HORIZON_SERIES)} base series")
    print(f"Cutoff: {YESTERDAY}")
    print("=" * 70)

    conn = sqlite3.connect(DB_PATH)

    all_data = {}
    series_count = 0
    transform_count = 0

    print("\n--- Processing Series ---")

    for series_id, config in HORIZON_SERIES.items():
        name = config["name"]
        freq = config["freq"]
        transforms = config["transforms"]

        # Fetch from master database
        query = f"""
            SELECT date, value FROM observations
            WHERE series_id = ?
            ORDER BY date
        """
        df = pd.read_sql(query, conn, params=[series_id])

        if df.empty:
            print(f"   [SKIP] {name}: No data found for {series_id}")
            continue

        # Convert to datetime and set index
        df["date"] = pd.to_datetime(df["date"])
        df = df.set_index("date")
        df = df[~df.index.duplicated(keep='first')]  # Remove dupe dates

        # Get first and last observation dates
        first_obs = df.index.min()
        last_obs = min(df.index.max(), pd.Timestamp(YESTERDAY))

        # Transform on NATIVE frequency, THEN forward-fill to daily.
        # Previously this interpolated to a daily grid BEFORE transforming, so
        # freq="M" period counts (yoy=12, z_window=24) became DAY counts:
        # Retail_Sales_yoy_pct read 0.19% (12-day change) vs the true ~4.9%
        # 12-month change, and every monthly _z column used a ~24-day window.
        # Transforming on the native series fixes the period counts; the
        # forward-fill onto the daily grid carries the latest print until the
        # next release lands (daily-FF / nowcast), instead of fabricating
        # linearly-interpolated intermediate values.
        df_native = df[(df.index >= first_obs) & (df.index <= last_obs)]
        df_native = df_native[~df_native.index.duplicated(keep="last")]
        df_transformed_native = apply_transforms(df_native, transforms, freq)
        daily_idx = pd.date_range(start=first_obs, end=last_obs, freq="D")
        df_transformed = (df_transformed_native
                          .reindex(df_transformed_native.index.union(daily_idx))
                          .sort_index().ffill().reindex(daily_idx))

        # Rename columns with series name prefix
        for col in df_transformed.columns:
            col_name = f"{name}_{col}" if col != "raw" else name
            all_data[col_name] = df_transformed[col]
            transform_count += 1

        series_count += 1
        print(f"   [{series_count}] {name}: {len(df)} obs, {len(transforms)+1} cols, {first_obs.date()} to {last_obs.date()}")

    conn.close()

    # Combine all into single DataFrame
    print("\n--- Building Combined Dataset ---")
    horizon_df = pd.DataFrame(all_data)
    horizon_df.index.name = "date"

    # Sort by date
    horizon_df = horizon_df.sort_index()

    # Summary stats
    print(f"\nDataset Shape: {horizon_df.shape[0]} rows x {horizon_df.shape[1]} columns")
    print(f"Date Range: {horizon_df.index.min().date()} to {horizon_df.index.max().date()}")
    print(f"Base Series: {series_count}")
    print(f"Total Columns (raw + transforms): {transform_count}")

    # Save to SQLite
    print("\n--- Saving to SQLite ---")
    conn = sqlite3.connect(DB_PATH)
    horizon_df.to_sql("horizon_dataset", conn, if_exists="replace", index=True)
    conn.close()
    print(f"   Saved to: {DB_PATH} (table: horizon_dataset)")

    # Export to CSV
    print("\n--- Exporting to CSV ---")
    horizon_df.to_csv(OUTPUT_CSV)
    print(f"   Saved to: {OUTPUT_CSV}")

    # Column summary
    print("\n--- Column Summary ---")
    print(f"Total columns: {len(horizon_df.columns)}")

    # Group by type
    raw_cols = [c for c in horizon_df.columns if not any(x in c for x in ["_yoy", "_mom", "_qoq", "_diff", "_z", "_ma", "_ann"])]
    transform_cols = [c for c in horizon_df.columns if c not in raw_cols]
    print(f"   Raw series: {len(raw_cols)}")
    print(f"   Transformations: {len(transform_cols)}")

    print("\n" + "=" * 70)
    print("HORIZON DATASET COMPLETE")
    print("=" * 70)

    return horizon_df


# ==========================================
# MAIN
# ==========================================

if __name__ == "__main__":
    df = build_horizon_dataset()

    # Show sample
    print("\nSample (last 5 rows, first 10 cols):")
    print(df.iloc[-5:, :10].to_string())
