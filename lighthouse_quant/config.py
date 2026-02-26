"""
Configuration for Lighthouse Quant package.
"""

from pathlib import Path

# Paths
LHM_ROOT = Path("/Users/bob/LHM")
DATA_DIR = LHM_ROOT / "Data"
DB_PATH = DATA_DIR / "databases" / "Lighthouse_Master.db"
PILLAR_DB_DIR = DATA_DIR / "databases" / "pillars"
OUTPUT_DIR = LHM_ROOT / "lighthouse_quant" / "outputs"

# Ensure output directory exists
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Publication lags (in days) for key series
# Critical for avoiding look-ahead bias in backtesting
PUBLICATION_LAGS = {
    # Labor (JOLTS ~5 weeks lag, BLS jobs ~1 week)
    "JOLTS_Quits_Rate": 35,
    "JOLTS_Hires_Rate": 35,
    "JOLTS_Openings_Rate": 35,
    "Nonfarm_Payrolls": 7,
    "Initial_Claims": 5,
    "Continued_Claims": 12,
    "Unemployment_Rate_U3": 7,
    "Unemployment_Rate_U6": 7,
    "Unemployed_27wks_Plus": 7,
    "LFPR_Prime_Age_25_54": 7,

    # Prices (CPI ~2 weeks, PCE ~4 weeks)
    "CPI_Core_yoy_pct": 14,
    "CPI_Headline_yoy_pct": 14,
    "CPI_Shelter_yoy_pct": 14,
    "PCE_Core_yoy_pct": 28,
    "PCE_Headline_yoy_pct": 28,

    # Growth (GDP ~4 weeks, IP ~2 weeks)
    "GDP_Real_yoy_pct": 28,
    "Industrial_Production_yoy_pct": 14,
    "Retail_Sales_yoy_pct": 14,

    # Housing (~3-4 weeks)
    "Housing_Starts": 21,
    "Existing_Home_Sales": 21,
    "Case_Shiller_Home_Prices_yoy_pct": 60,  # 2-month lag

    # Financial (real-time or next day)
    "HY_OAS": 1,
    "IG_OAS": 1,
    "VIX": 1,
    "Chicago_NFCI": 7,
    "Treasury_10Y": 1,
    "Curve_10Y_2Y": 1,

    # Fed/Liquidity (weekly or daily)
    "RRP_Usage": 1,
    "Bank_Reserves": 7,
    "Fed_Balance_Sheet": 7,
    "EFFR": 1,
    "SOFR": 1,

    # Sentiment/Surveys
    "Consumer_Sentiment": 14,
    "LO_Survey_CI_Tightening": 90,  # Quarterly SLOOS
}

# Default z-score window (monthly = 24 months, daily = 252 days)
ZSCORE_WINDOW_MONTHLY = 24
ZSCORE_WINDOW_DAILY = 252

# NBER recession periods (for validation)
# Format: (start_date, end_date)
NBER_RECESSIONS = [
    ("1948-11-01", "1949-10-01"),
    ("1953-07-01", "1954-05-01"),
    ("1957-08-01", "1958-04-01"),
    ("1960-04-01", "1961-02-01"),
    ("1969-12-01", "1970-11-01"),
    ("1973-11-01", "1975-03-01"),
    ("1980-01-01", "1980-07-01"),
    ("1981-07-01", "1982-11-01"),
    ("1990-07-01", "1991-03-01"),
    ("2001-03-01", "2001-11-01"),
    ("2007-12-01", "2009-06-01"),
    ("2020-02-01", "2020-04-01"),
]

# Key indicator relationships to validate
# Format: (leading_indicator, lagging_indicator, expected_lag_months, relationship)
INDICATOR_RELATIONSHIPS = [
    # Labor leading indicators
    ("JOLTS_Quits_Rate", "Unemployment_Rate_U3", 6, "negative"),
    ("JOLTS_Quits_Rate", "Initial_Claims", 4, "negative"),
    ("Initial_Claims", "Unemployment_Rate_U3", 3, "positive"),
    ("JOLTS_Hires_Rate", "Nonfarm_Payrolls_yoy_pct", 2, "positive"),
    ("Unemployed_27wks_Plus", "Unemployment_Rate_U3", -2, "positive"),  # Lagging

    # Credit leading indicators
    ("HY_OAS", "GDP_Real_yoy_pct", 6, "negative"),
    ("HY_OAS", "Unemployment_Rate_U3", 9, "positive"),
    ("Chicago_NFCI", "GDP_Real_yoy_pct", 3, "negative"),
    ("LO_Survey_CI_Tightening", "CI_Loans_yoy_pct", 6, "negative"),

    # Housing leading indicators
    ("Housing_Starts_yoy_pct", "GDP_Real_yoy_pct", 3, "positive"),
    ("Mortgage_30Y", "Housing_Starts_yoy_pct", 6, "negative"),

    # Yield curve
    ("Curve_10Y_2Y", "Unemployment_Rate_U3", 12, "negative"),
    ("Curve_10Y_3M", "GDP_Real_yoy_pct", 6, "positive"),

    # Inflation dynamics
    ("CPI_Shelter_yoy_pct", "CPI_Core_yoy_pct", -6, "positive"),  # Shelter lags
]
