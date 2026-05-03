# Lighthouse_Master.db — schema manifest

- Path: `/Users/bob/LHM/Data/databases/Lighthouse_Master.db`
- Tables: 11

## Summary

| Table | Rows | Date column | Earliest | Latest |
|---|---:|---|---|---|
| `crypto_integrated_scores` | 34 | date | 2026-01-20 | 2026-01-20 |
| `crypto_meta` | 34 | — | — | — |
| `crypto_metrics` | 993,542 | date | 2012-12-01 | 2026-02-01 |
| `crypto_scores` | 374 | date | 2026-01-20 | 2026-02-02 |
| `horizon_dataset` | 45,597 | date | 1901-06-30 00:00:00 | 2026-05-01 00:00:00 |
| `lighthouse_indices` | 470,885 | date | 1901-06-30 | 2026-05-01 |
| `lost_and_found` | 1,935,853 | — | — | — |
| `lost_and_found_0` | 72,250 | — | — | — |
| `observations` | 4,199,160 | date | 1854-10-01 | 2036-10-01 |
| `series_meta` | 2,504 | last_value_date | 1934-03-01 | 2036-10-01 |
| `update_log` | 101 | timestamp | 2026-01-10T22:16:08.103729 | 2026-05-03T06:23:16.730892 |

## `crypto_integrated_scores`

- Rows: 34

### Columns

| Column | Type |
|---|---|
| `project_id` | `TEXT` |
| `date` | `TEXT` |
| `total_score` | `REAL` |
| `technical_score` | `REAL` |
| `fundamental_score` | `REAL` |
| `microstructure_score` | `REAL` |
| `signal` | `TEXT` |
| `tier` | `TEXT` |
| `has_override` | `INTEGER` |
| `warning_count` | `INTEGER` |

### First 5 rows

```
project_id | date | total_score | technical_score | fundamental_score | microstructure_score | signal | tier | has_override | warning_count
------------------------------------------------------------------------------------------------------------------------
aave | 2026-01-20 | 18.425109411764705 | 7.0 | 6.925109411764706 | 4.5 | STRONG_BUY | TIER 1 (Accumulate) | 0 | 0
aerodrome | 2026-01-20 | 16.393109411764705 | 5.5 | 6.893109411764706 | 4.0 | BUY | TIER 1 (Accumulate) | 0 | 0
aptos | 2026-01-20 | 8.897109411764706 | 5.0 | 1.3971094117647058 | 2.5 | SELL | NEUTRAL (Watch) | 0 | 3
arbitrum | 2026-01-20 | 15.665109411764705 | 5.5 | 6.165109411764705 | 4.0 | BUY | TIER 2 (Hold) | 0 | 0
avalanche | 2026-01-20 | 13.893109411764705 | 4.0 | 5.393109411764706 | 4.5 | NEUTRAL | TIER 2 (Hold) | 0 | 1
```

## `crypto_meta`

- Rows: 34

### Columns

| Column | Type |
|---|---|
| `project_id` | `TEXT` |
| `name` | `TEXT` |
| `symbol` | `TEXT` |
| `sector` | `TEXT` |
| `last_updated` | `TEXT` |
| `last_fetched` | `TEXT` |
| `data_quality` | `TEXT` |

### First 5 rows

```
project_id | name | symbol | sector | last_updated | last_fetched | data_quality
--------------------------------------------------------------------------------
ethereum | ethereum |  | layer1 | 2026-02-01T11:33:54.182476 | 2026-02-01T11:33:54.270178 | 
solana | solana |  | layer1 | 2026-02-02T09:27:46.790480 | 2026-02-02T09:27:46.790505 | 
avalanche | avalanche |  | layer1 | 2026-02-02T09:27:53.060166 | 2026-02-02T09:27:53.060185 | 
near-protocol | near-protocol |  | layer1 | 2026-02-02T09:45:11.592454 | 2026-02-02T09:45:11.686631 | 
sui | sui |  | layer1 | 2026-02-02T09:46:39.518352 | 2026-02-02T09:46:39.578006 | 
```

## `crypto_metrics`

- Rows: 993,542

### Columns

| Column | Type |
|---|---|
| `project_id` | `TEXT` |
| `date` | `TEXT` |
| `metric_id` | `TEXT` |
| `value` | `REAL` |

### First 5 rows

```
project_id | date | metric_id | value
-------------------------------------
ethereum | 2013-12-19 | active_developers | 1.0
ethereum | 2013-12-19 | code_commits | 1.0
ethereum | 2013-12-20 | active_developers | 1.0
ethereum | 2013-12-20 | code_commits | 3.0
ethereum | 2013-12-21 | active_developers | 1.0
```

## `crypto_scores`

- Rows: 374

### Columns

| Column | Type |
|---|---|
| `project_id` | `TEXT` |
| `date` | `TEXT` |
| `name` | `TEXT` |
| `sector` | `TEXT` |
| `verdict` | `TEXT` |
| `overall_score` | `INTEGER` |
| `financial_score` | `INTEGER` |
| `usage_score` | `INTEGER` |
| `valuation_score` | `INTEGER` |
| `fdv` | `REAL` |
| `market_cap` | `REAL` |
| `ann_revenue` | `REAL` |
| `ann_fees` | `REAL` |
| `pe_ratio` | `REAL` |
| `pf_ratio` | `REAL` |
| `subsidy_score` | `REAL` |
| `float_ratio` | `REAL` |
| `dau` | `INTEGER` |
| `mau` | `INTEGER` |
| `active_developers` | `INTEGER` |
| `tvl` | `REAL` |
| `red_flags` | `TEXT` |

### First 5 rows

```
project_id | date | name | sector | verdict | overall_score | financial_score | usage_score | valuation_score | fdv | market_cap | ann_revenue | ann_fees | pe_ratio | pf_ratio | subsidy_score | float_ratio | dau | mau | active_developers | tvl | red_flags
------------------------------------------------------------------------------------------------------------------------
ethereum | 2026-01-20 | Ethereum | Layer 1 (Settlement) | NEUTRAL (Watch) | 58 | 40 | 90 | 45 | 384492450394.5867 | 384410444146.86456 | 23131074.17884493 | 136763517.5166778 | 16622.334415676785 | 2811.3670763674186 | 119.06642976402732 | 0.9997867155840434 | 864030 | 13553886 | 150 | 0.0 | Elevated subsidy: 119.1x; Expensive: P/E 16622x
solana | 2026-01-20 | Solana | Layer 1 (Settlement) | TIER 1 (Accumulate) | 78 | 100 | 90 | 45 | 82546822247.9408 | 75486541005.88855 | 34964199.39988439 | 338454255.31207234 | 2360.895534997256 | 243.89358665864123 | 0.0 | 0.9144693756854053 | 2681245 | 40598294 | 21 | 0.0 | 
avalanche | 2026-01-20 | Avalanche | Layer 1 (Settlement) | AVOID (Vaporware) | 73 | 75 | 100 | 45 | 5892565768.923621 | 5489196143.503593 | 4162521.5301662027 | 4162521.5301662027 | 1415.6240937661505 | 1415.6240937661505 | 0.0 | 0.9315460121722646 | 508208 | 1561672 | 61 | 0.0 | Insufficient fee revenue for valuation
near-protocol | 2026-01-20 | NEAR Protocol | Uncategorized | AVOID (Unsustainable) | 55 | 30 | 90 | 45 | 2053905951.2949135 | 2054172641.4507186 | 1577741.6879664424 | 75952946.6140092 | 1301.8011547518918 | 27.04182053308356 | 27.644468598322906 | 1.0001298453591008 | 2451900 | 38117124 | 41 | 0.0 | Unsustainable token economics
sui | 2026-01-20 | Sui | Layer 1 (Settlement) | AVOID (Vaporware) | 31 | 10 | 55 | 30 | 15673304774.799744 | 5943827456.715626 | 0.0 | 0.0 |  |  |  | 0.37923255765895547 | 0 | 0 | 70 | 0.0 | Insufficient fee revenue for valuation
```

## `horizon_dataset`

- Rows: 45,597

### Columns

| Column | Type |
|---|---|
| `date` | `TIMESTAMP` |
| `Unemployment_Rate_U3` | `REAL` |
| `Unemployment_Rate_U3_yoy_diff` | `REAL` |
| `Unemployment_Rate_U3_mom_diff` | `REAL` |
| `Unemployment_Rate_U3_z` | `REAL` |
| `Unemployment_Rate_U6` | `REAL` |
| `Unemployment_Rate_U6_yoy_diff` | `REAL` |
| `Unemployment_Rate_U6_mom_diff` | `REAL` |
| `Unemployment_Rate_U6_z` | `REAL` |
| `Unemployment_Rate_U1` | `REAL` |
| `Unemployment_Rate_U1_yoy_diff` | `REAL` |
| `Unemployment_Rate_U1_z` | `REAL` |
| `Unemployment_Rate_U2` | `REAL` |
| `Unemployment_Rate_U2_yoy_diff` | `REAL` |
| `Unemployment_Rate_U2_z` | `REAL` |
| `LFPR` | `REAL` |
| `LFPR_yoy_diff` | `REAL` |
| `LFPR_z` | `REAL` |
| `LFPR_Prime_Age_25_54` | `REAL` |
| `LFPR_Prime_Age_25_54_yoy_diff` | `REAL` |
| `LFPR_Prime_Age_25_54_z` | `REAL` |
| `Nonfarm_Payrolls` | `REAL` |
| `Nonfarm_Payrolls_yoy_pct` | `REAL` |
| `Nonfarm_Payrolls_mom_diff` | `REAL` |
| `Nonfarm_Payrolls_mom_diff_3ma` | `REAL` |
| `Initial_Claims` | `REAL` |
| `Initial_Claims_yoy_pct` | `REAL` |
| `Initial_Claims_4wk_ma` | `REAL` |
| `Initial_Claims_z` | `REAL` |
| `Continued_Claims` | `REAL` |
| `Continued_Claims_yoy_pct` | `REAL` |
| `Continued_Claims_4wk_ma` | `REAL` |
| `Continued_Claims_z` | `REAL` |
| `JOLTS_Openings_Rate` | `REAL` |
| `JOLTS_Openings_Rate_yoy_diff` | `REAL` |
| `JOLTS_Openings_Rate_z` | `REAL` |
| `JOLTS_Quits_Rate` | `REAL` |
| `JOLTS_Quits_Rate_yoy_diff` | `REAL` |
| `JOLTS_Quits_Rate_z` | `REAL` |
| `JOLTS_Hires_Rate` | `REAL` |
| `JOLTS_Hires_Rate_yoy_diff` | `REAL` |
| `JOLTS_Hires_Rate_z` | `REAL` |
| `Mean_Unemployment_Duration` | `REAL` |
| `Mean_Unemployment_Duration_yoy_pct` | `REAL` |
| `Mean_Unemployment_Duration_z` | `REAL` |
| `Unemployed_27wks_Plus` | `REAL` |
| `Unemployed_27wks_Plus_yoy_pct` | `REAL` |
| `Unemployed_27wks_Plus_z` | `REAL` |
| `Part_Time_Economic_Reasons` | `REAL` |
| `Part_Time_Economic_Reasons_yoy_pct` | `REAL` |
| `Part_Time_Economic_Reasons_z` | `REAL` |
| `Unemployment_White` | `REAL` |
| `Unemployment_White_yoy_diff` | `REAL` |
| `Unemployment_White_z` | `REAL` |
| `Unemployment_Black` | `REAL` |
| `Unemployment_Black_yoy_diff` | `REAL` |
| `Unemployment_Black_z` | `REAL` |
| `Unemployment_Hispanic` | `REAL` |
| `Unemployment_Hispanic_yoy_diff` | `REAL` |
| `Unemployment_Hispanic_z` | `REAL` |
| `Unemployment_25_54` | `REAL` |
| `Unemployment_25_54_yoy_diff` | `REAL` |
| `Unemployment_25_54_z` | `REAL` |
| `Unemployment_55_Plus` | `REAL` |
| `Unemployment_55_Plus_yoy_diff` | `REAL` |
| `Unemployment_55_Plus_z` | `REAL` |
| `Jobs_Total_Nonfarm` | `REAL` |
| `Jobs_Total_Nonfarm_yoy_pct` | `REAL` |
| `Jobs_Total_Nonfarm_mom_diff` | `REAL` |
| `Jobs_Construction` | `REAL` |
| `Jobs_Construction_yoy_pct` | `REAL` |
| `Jobs_Construction_mom_diff` | `REAL` |
| `Jobs_Manufacturing` | `REAL` |
| `Jobs_Manufacturing_yoy_pct` | `REAL` |
| `Jobs_Manufacturing_mom_diff` | `REAL` |
| `Jobs_Financial` | `REAL` |
| `Jobs_Financial_yoy_pct` | `REAL` |
| `Jobs_Financial_mom_diff` | `REAL` |
| `Jobs_Professional_Business` | `REAL` |
| `Jobs_Professional_Business_yoy_pct` | `REAL` |
| `Jobs_Professional_Business_mom_diff` | `REAL` |
| `Jobs_Education_Health` | `REAL` |
| `Jobs_Education_Health_yoy_pct` | `REAL` |
| `Jobs_Education_Health_mom_diff` | `REAL` |
| `Jobs_Leisure_Hospitality` | `REAL` |
| `Jobs_Leisure_Hospitality_yoy_pct` | `REAL` |
| `Jobs_Leisure_Hospitality_mom_diff` | `REAL` |
| `Jobs_Government` | `REAL` |
| `Jobs_Government_yoy_pct` | `REAL` |
| `Jobs_Government_mom_diff` | `REAL` |
| `CPI_Headline` | `REAL` |
| `CPI_Headline_yoy_pct` | `REAL` |
| `CPI_Headline_mom_pct` | `REAL` |
| `CPI_Headline_3m_ann` | `REAL` |
| `CPI_Headline_6m_ann` | `REAL` |
| `CPI_Core` | `REAL` |
| `CPI_Core_yoy_pct` | `REAL` |
| `CPI_Core_mom_pct` | `REAL` |
| `CPI_Core_3m_ann` | `REAL` |
| `CPI_Core_6m_ann` | `REAL` |
| `PCE_Headline` | `REAL` |
| `PCE_Headline_yoy_pct` | `REAL` |
| `PCE_Headline_mom_pct` | `REAL` |
| `PCE_Headline_3m_ann` | `REAL` |
| `PCE_Headline_6m_ann` | `REAL` |
| `PCE_Core` | `REAL` |
| `PCE_Core_yoy_pct` | `REAL` |
| `PCE_Core_mom_pct` | `REAL` |
| `PCE_Core_3m_ann` | `REAL` |
| `PCE_Core_6m_ann` | `REAL` |
| `Median_CPI` | `REAL` |
| `Median_CPI_yoy_pct` | `REAL` |
| `Median_CPI_3m_ann` | `REAL` |
| `Sticky_Core_CPI` | `REAL` |
| `Sticky_Core_CPI_yoy_pct` | `REAL` |
| `Sticky_Core_CPI_3m_ann` | `REAL` |
| `CPI_Shelter` | `REAL` |
| `CPI_Shelter_yoy_pct` | `REAL` |
| `CPI_Shelter_mom_pct` | `REAL` |
| `CPI_Shelter_3m_ann` | `REAL` |
| `CPI_Rent_Primary` | `REAL` |
| `CPI_Rent_Primary_yoy_pct` | `REAL` |
| `CPI_Rent_Primary_mom_pct` | `REAL` |
| `CPI_OER` | `REAL` |
| `CPI_OER_yoy_pct` | `REAL` |
| `CPI_OER_mom_pct` | `REAL` |
| `CPI_Medical_Services` | `REAL` |
| `CPI_Medical_Services_yoy_pct` | `REAL` |
| `CPI_Transport_Services` | `REAL` |
| `CPI_Transport_Services_yoy_pct` | `REAL` |
| `CPI_Gasoline` | `REAL` |
| `CPI_Gasoline_yoy_pct` | `REAL` |
| `CPI_Gasoline_mom_pct` | `REAL` |
| `CPI_Used_Cars` | `REAL` |
| `CPI_Used_Cars_yoy_pct` | `REAL` |
| `CPI_Used_Cars_mom_pct` | `REAL` |
| `CPI_Food_Home` | `REAL` |
| `CPI_Food_Home_yoy_pct` | `REAL` |
| `CPI_Food_Away` | `REAL` |
| `CPI_Food_Away_yoy_pct` | `REAL` |
| `PCE_Durable_Goods` | `REAL` |
| `PCE_Durable_Goods_yoy_pct` | `REAL` |
| `PCE_Nondurable_Goods` | `REAL` |
| `PCE_Nondurable_Goods_yoy_pct` | `REAL` |
| `PCE_Services` | `REAL` |
| `PCE_Services_yoy_pct` | `REAL` |
| `Breakeven_10Y` | `REAL` |
| `Breakeven_10Y_diff` | `REAL` |
| `Breakeven_10Y_z` | `REAL` |
| `Breakeven_5Y` | `REAL` |
| `Breakeven_5Y_diff` | `REAL` |
| `Breakeven_5Y_z` | `REAL` |
| `Forward_Inflation_5Y` | `REAL` |
| `Forward_Inflation_5Y_diff` | `REAL` |
| `Forward_Inflation_5Y_z` | `REAL` |
| `Fed_Funds` | `REAL` |
| `Fed_Funds_diff` | `REAL` |
| `Fed_Funds_yoy_diff` | `REAL` |
| `Treasury_1M` | `REAL` |
| `Treasury_1M_diff` | `REAL` |
| `Treasury_3M` | `REAL` |
| `Treasury_3M_diff` | `REAL` |
| `Treasury_6M` | `REAL` |
| `Treasury_6M_diff` | `REAL` |
| `Treasury_1Y` | `REAL` |
| `Treasury_1Y_diff` | `REAL` |
| `Treasury_1Y_yoy_diff` | `REAL` |
| `Treasury_2Y` | `REAL` |
| `Treasury_2Y_diff` | `REAL` |
| `Treasury_2Y_yoy_diff` | `REAL` |
| `Treasury_5Y` | `REAL` |
| `Treasury_5Y_diff` | `REAL` |
| `Treasury_5Y_yoy_diff` | `REAL` |
| `Treasury_10Y` | `REAL` |
| `Treasury_10Y_diff` | `REAL` |
| `Treasury_10Y_yoy_diff` | `REAL` |
| `Treasury_30Y` | `REAL` |
| `Treasury_30Y_diff` | `REAL` |
| `Treasury_30Y_yoy_diff` | `REAL` |
| `Curve_10Y_2Y` | `REAL` |
| `Curve_10Y_2Y_diff` | `REAL` |
| `Curve_10Y_2Y_z` | `REAL` |
| `Curve_10Y_3M` | `REAL` |
| `Curve_10Y_3M_diff` | `REAL` |
| `Curve_10Y_3M_z` | `REAL` |
| `Spread_10Y_FF` | `REAL` |
| `Spread_10Y_FF_diff` | `REAL` |
| `Spread_10Y_FF_z` | `REAL` |
| `Spread_5Y_FF` | `REAL` |
| `Spread_5Y_FF_diff` | `REAL` |
| `TIPS_5Y` | `REAL` |
| `TIPS_5Y_diff` | `REAL` |
| `TIPS_10Y` | `REAL` |
| `TIPS_10Y_diff` | `REAL` |
| `Term_Premium_10Y` | `REAL` |
| `Term_Premium_10Y_diff` | `REAL` |
| `Term_Premium_10Y_z` | `REAL` |
| `Mortgage_30Y` | `REAL` |
| `Mortgage_30Y_diff` | `REAL` |
| `Mortgage_30Y_yoy_diff` | `REAL` |
| `HY_OAS` | `REAL` |
| `HY_OAS_diff` | `REAL` |
| `HY_OAS_yoy_diff` | `REAL` |
| `HY_OAS_z` | `REAL` |
| `IG_OAS` | `REAL` |
| `IG_OAS_diff` | `REAL` |
| `IG_OAS_yoy_diff` | `REAL` |
| `IG_OAS_z` | `REAL` |
| `SOFR` | `REAL` |
| `SOFR_diff` | `REAL` |
| `EFFR` | `REAL` |
| `EFFR_diff` | `REAL` |
| `OBFR` | `REAL` |
| `OBFR_diff` | `REAL` |
| `SOFR_Volume` | `REAL` |
| `SOFR_Volume_yoy_pct` | `REAL` |
| `SOFR_Volume_z` | `REAL` |
| `Fed_Balance_Sheet` | `REAL` |
| `Fed_Balance_Sheet_yoy_pct` | `REAL` |
| `Fed_Balance_Sheet_wow_diff` | `REAL` |
| `RRP_Usage` | `REAL` |
| `RRP_Usage_diff` | `REAL` |
| `RRP_Usage_yoy_diff` | `REAL` |
| `RRP_Usage_z` | `REAL` |
| `Bank_Reserves` | `REAL` |
| `Bank_Reserves_yoy_pct` | `REAL` |
| `Bank_Reserves_mom_pct` | `REAL` |
| `M2` | `REAL` |
| `M2_yoy_pct` | `REAL` |
| `M2_mom_pct` | `REAL` |
| `Treasury_General_Account` | `REAL` |
| `Treasury_General_Account_diff` | `REAL` |
| `Treasury_General_Account_z` | `REAL` |
| `Fed_RRP_Outstanding` | `REAL` |
| `Fed_RRP_Outstanding_diff` | `REAL` |
| `Chicago_NFCI` | `REAL` |
| `Chicago_NFCI_diff` | `REAL` |
| `Chicago_NFCI_z` | `REAL` |
| `Adjusted_NFCI` | `REAL` |
| `Adjusted_NFCI_diff` | `REAL` |
| `Adjusted_NFCI_z` | `REAL` |
| `StLouis_FSI` | `REAL` |
| `StLouis_FSI_diff` | `REAL` |
| `StLouis_FSI_z` | `REAL` |
| `OFR_FSI` | `REAL` |
| `OFR_FSI_diff` | `REAL` |
| `OFR_FSI_z` | `REAL` |
| `OFR_FSI_Credit` | `REAL` |
| `OFR_FSI_Credit_diff` | `REAL` |
| `OFR_FSI_Credit_z` | `REAL` |
| `OFR_FSI_Funding` | `REAL` |
| `OFR_FSI_Funding_diff` | `REAL` |
| `OFR_FSI_Funding_z` | `REAL` |
| `OFR_FSI_Volatility` | `REAL` |
| `OFR_FSI_Volatility_diff` | `REAL` |
| `OFR_FSI_Volatility_z` | `REAL` |
| `OFR_FSI_US` | `REAL` |
| `OFR_FSI_US_diff` | `REAL` |
| `OFR_FSI_US_z` | `REAL` |
| `GDP_Nominal` | `REAL` |
| `GDP_Nominal_yoy_pct` | `REAL` |
| `GDP_Nominal_qoq_pct` | `REAL` |
| `GDP_Real` | `REAL` |
| `GDP_Real_yoy_pct` | `REAL` |
| `GDP_Real_qoq_pct` | `REAL` |
| `Industrial_Production` | `REAL` |
| `Industrial_Production_yoy_pct` | `REAL` |
| `Industrial_Production_mom_pct` | `REAL` |
| `Industrial_Production_3m_ann` | `REAL` |
| `Retail_Sales` | `REAL` |
| `Retail_Sales_yoy_pct` | `REAL` |
| `Retail_Sales_mom_pct` | `REAL` |
| `Consumer_Sentiment` | `REAL` |
| `Consumer_Sentiment_yoy_pct` | `REAL` |
| `Consumer_Sentiment_mom_diff` | `REAL` |
| `Consumer_Sentiment_z` | `REAL` |
| `Consumer_Credit` | `REAL` |
| `Consumer_Credit_yoy_pct` | `REAL` |
| `Saving_Rate` | `REAL` |
| `Saving_Rate_diff` | `REAL` |
| `Saving_Rate_z` | `REAL` |
| `Debt_Service_Ratio` | `REAL` |
| `Debt_Service_Ratio_diff` | `REAL` |
| `Debt_Service_Ratio_z` | `REAL` |
| `LO_Survey_CI_Tightening` | `REAL` |
| `LO_Survey_CI_Tightening_diff` | `REAL` |
| `LO_Survey_CI_Tightening_z` | `REAL` |
| `LO_Survey_CC_Tightening` | `REAL` |
| `LO_Survey_CC_Tightening_diff` | `REAL` |
| `LO_Survey_CC_Tightening_z` | `REAL` |
| `CI_Loans` | `REAL` |
| `CI_Loans_yoy_pct` | `REAL` |
| `Business_Loans` | `REAL` |
| `Business_Loans_yoy_pct` | `REAL` |
| `Consumer_Loans` | `REAL` |
| `Consumer_Loans_yoy_pct` | `REAL` |
| `Real_Estate_Loans` | `REAL` |
| `Real_Estate_Loans_yoy_pct` | `REAL` |
| `Housing_Starts` | `REAL` |
| `Housing_Starts_yoy_pct` | `REAL` |
| `Housing_Starts_mom_pct` | `REAL` |
| `Housing_Starts_z` | `REAL` |
| `Housing_Starts_1Unit` | `REAL` |
| `Housing_Starts_1Unit_yoy_pct` | `REAL` |
| `Building_Permits` | `REAL` |
| `Building_Permits_yoy_pct` | `REAL` |
| `Building_Permits_mom_pct` | `REAL` |
| `Case_Shiller_Home_Prices` | `REAL` |
| `Case_Shiller_Home_Prices_yoy_pct` | `REAL` |
| `Case_Shiller_Home_Prices_mom_pct` | `REAL` |
| `Median_Home_Price` | `REAL` |
| `Median_Home_Price_yoy_pct` | `REAL` |
| `New_Home_Sales` | `REAL` |
| `New_Home_Sales_yoy_pct` | `REAL` |
| `New_Home_Sales_mom_pct` | `REAL` |
| `Existing_Home_Sales` | `REAL` |
| `Existing_Home_Sales_yoy_pct` | `REAL` |
| `Existing_Home_Sales_mom_pct` | `REAL` |
| `Months_Supply` | `REAL` |
| `Months_Supply_diff` | `REAL` |
| `Months_Supply_z` | `REAL` |
| `Delinquency_All_Loans` | `REAL` |
| `Delinquency_All_Loans_diff` | `REAL` |
| `Delinquency_All_Loans_yoy_diff` | `REAL` |
| `Delinquency_All_Loans_z` | `REAL` |
| `Delinquency_Mortgage` | `REAL` |
| `Delinquency_Mortgage_diff` | `REAL` |
| `Delinquency_Mortgage_yoy_diff` | `REAL` |
| `Delinquency_Mortgage_z` | `REAL` |
| `Delinquency_Credit_Card` | `REAL` |
| `Delinquency_Credit_Card_diff` | `REAL` |
| `Delinquency_Credit_Card_yoy_diff` | `REAL` |
| `Delinquency_Credit_Card_z` | `REAL` |
| `Delinquency_Consumer` | `REAL` |
| `Delinquency_Consumer_diff` | `REAL` |
| `Delinquency_Consumer_yoy_diff` | `REAL` |
| `Delinquency_Consumer_z` | `REAL` |
| `Delinquency_Business` | `REAL` |
| `Delinquency_Business_diff` | `REAL` |
| `Delinquency_Business_yoy_diff` | `REAL` |
| `Delinquency_Business_z` | `REAL` |
| `Delinquency_CRE` | `REAL` |
| `Delinquency_CRE_diff` | `REAL` |
| `Delinquency_CRE_yoy_diff` | `REAL` |
| `Delinquency_CRE_z` | `REAL` |
| `Federal_Debt` | `REAL` |
| `Federal_Debt_yoy_pct` | `REAL` |
| `Debt_to_GDP` | `REAL` |
| `Debt_to_GDP_diff` | `REAL` |
| `Federal_Surplus_Deficit` | `REAL` |
| `Federal_Surplus_Deficit_diff` | `REAL` |
| `Federal_Receipts` | `REAL` |
| `Federal_Receipts_yoy_pct` | `REAL` |
| `Federal_Expenditures` | `REAL` |
| `Federal_Expenditures_yoy_pct` | `REAL` |
| `VIX` | `REAL` |
| `VIX_diff` | `REAL` |
| `VIX_z` | `REAL` |
| `VIX_20d_ma` | `REAL` |
| `WTI_Crude` | `REAL` |
| `WTI_Crude_yoy_pct` | `REAL` |
| `WTI_Crude_mom_pct` | `REAL` |
| `Dollar_Index` | `REAL` |
| `Dollar_Index_yoy_pct` | `REAL` |
| `Dollar_Index_mom_pct` | `REAL` |
| `EUR_USD` | `REAL` |
| `EUR_USD_yoy_pct` | `REAL` |
| `JPY_USD` | `REAL` |
| `JPY_USD_yoy_pct` | `REAL` |
| `BEA_GDP` | `REAL` |
| `BEA_GDP_yoy_pct` | `REAL` |
| `BEA_GDP_qoq_pct` | `REAL` |
| `BEA_PCE` | `REAL` |
| `BEA_PCE_yoy_pct` | `REAL` |
| `BEA_PCE_qoq_pct` | `REAL` |
| `BEA_Investment` | `REAL` |
| `BEA_Investment_yoy_pct` | `REAL` |
| `BEA_Investment_qoq_pct` | `REAL` |
| `BEA_Net_Exports` | `REAL` |
| `BEA_Net_Exports_diff` | `REAL` |
| `BEA_Govt` | `REAL` |
| `BEA_Govt_yoy_pct` | `REAL` |
| `BEA_Personal_Income` | `REAL` |
| `BEA_Personal_Income_yoy_pct` | `REAL` |
| `BEA_Corp_Profits` | `REAL` |
| `BEA_Corp_Profits_yoy_pct` | `REAL` |

### First 5 rows

```
date | Unemployment_Rate_U3 | Unemployment_Rate_U3_yoy_diff | Unemployment_Rate_U3_mom_diff | Unemployment_Rate_U3_z | Unemployment_Rate_U6 | Unemployment_Rate_U6_yoy_diff | Unemployment_Rate_U6_mom_diff | Unemployment_Rate_U6_z | Unemployment_Rate_U1 | Unemployment_Rate_U1_yoy_diff | Unemployment_Rate_U1_z | Unemployment_Rate_U2 | Unemployment_Rate_U2_yoy_diff | Unemployment_Rate_U2_z | LFPR | LFPR_yoy_diff | LFPR_z | LFPR_Prime_Age_25_54 | LFPR_Prime_Age_25_54_yoy_diff | LFPR_Prime_Age_25_54_z | Nonfarm_Payrolls | Nonfarm_Payrolls_yoy_pct | Nonfarm_Payrolls_mom_diff | Nonfarm_Payrolls_mom_diff_3ma | Initial_Claims | Initial_Claims_yoy_pct | Initial_Claims_4wk_ma | Initial_Claims_z | Continued_Claims | Continued_Claims_yoy_pct | Continued_Claims_4wk_ma | Continued_Claims_z | JOLTS_Openings_Rate | JOLTS_Openings_Rate_yoy_diff | JOLTS_Openings_Rate_z | JOLTS_Quits_Rate | JOLTS_Quits_Rate_yoy_diff | JOLTS_Quits_Rate_z | JOLTS_Hires_Rate | JOLTS_Hires_Rate_yoy_diff | JOLTS_Hires_Rate_z | Mean_Unemployment_Duration | Mean_Unemployment_Duration_yoy_pct | Mean_Unemployment_Duration_z | Unemployed_27wks_Plus | Unemployed_27wks_Plus_yoy_pct | Unemployed_27wks_Plus_z | Part_Time_Economic_Reasons | Part_Time_Economic_Reasons_yoy_pct | Part_Time_Economic_Reasons_z | Unemployment_White | Unemployment_White_yoy_diff | Unemployment_White_z | Unemployment_Black | Unemployment_Black_yoy_diff | Unemployment_Black_z | Unemployment_Hispanic | Unemployment_Hispanic_yoy_diff | Unemployment_Hispanic_z | Unemployment_25_54 | Unemployment_25_54_yoy_diff | Unemployment_25_54_z | Unemployment_55_Plus | Unemployment_55_Plus_yoy_diff | Unemployment_55_Plus_z | Jobs_Total_Nonfarm | Jobs_Total_Nonfarm_yoy_pct | Jobs_Total_Nonfarm_mom_diff | Jobs_Construction | Jobs_Construction_yoy_pct | Jobs_Construction_mom_diff | Jobs_Manufacturing | Jobs_Manufacturing_yoy_pct | Jobs_Manufacturing_mom_diff | Jobs_Financial | Jobs_Financial_yoy_pct | Jobs_Financial_mom_diff | Jobs_Professional_Business | Jobs_Professional_Business_yoy_pct | Jobs_Professional_Business_mom_diff | Jobs_Education_Health | Jobs_Education_Health_yoy_pct | Jobs_Education_Health_mom_diff | Jobs_Leisure_Hospitality | Jobs_Leisure_Hospitality_yoy_pct | Jobs_Leisure_Hospitality_mom_diff | Jobs_Government | Jobs_Government_yoy_pct | Jobs_Government_mom_diff | CPI_Headline | CPI_Headline_yoy_pct | CPI_Headline_mom_pct | CPI_Headline_3m_ann | CPI_Headline_6m_ann | CPI_Core | CPI_Core_yoy_pct | CPI_Core_mom_pct | CPI_Core_3m_ann | CPI_Core_6m_ann | PCE_Headline | PCE_Headline_yoy_pct | PCE_Headline_mom_pct | PCE_Headline_3m_ann | PCE_Headline_6m_ann | PCE_Core | PCE_Core_yoy_pct | PCE_Core_mom_pct | PCE_Core_3m_ann | PCE_Core_6m_ann | Median_CPI | Median_CPI_yoy_pct | Median_CPI_3m_ann | Sticky_Core_CPI | Sticky_Core_CPI_yoy_pct | Sticky_Core_CPI_3m_ann | CPI_Shelter | CPI_Shelter_yoy_pct | CPI_Shelter_mom_pct | CPI_Shelter_3m_ann | CPI_Rent_Primary | CPI_Rent_Primary_yoy_pct | CPI_Rent_Primary_mom_pct | CPI_OER | CPI_OER_yoy_pct | CPI_OER_mom_pct | CPI_Medical_Services | CPI_Medical_Services_yoy_pct | CPI_Transport_Services | CPI_Transport_Services_yoy_pct | CPI_Gasoline | CPI_Gasoline_yoy_pct | CPI_Gasoline_mom_pct | CPI_Used_Cars | CPI_Used_Cars_yoy_pct | CPI_Used_Cars_mom_pct | CPI_Food_Home | CPI_Food_Home_yoy_pct | CPI_Food_Away | CPI_Food_Away_yoy_pct | PCE_Durable_Goods | PCE_Durable_Goods_yoy_pct | PCE_Nondurable_Goods | PCE_Nondurable_Goods_yoy_pct | PCE_Services | PCE_Services_yoy_pct | Breakeven_10Y | Breakeven_10Y_diff | Breakeven_10Y_z | Breakeven_5Y | Breakeven_5Y_diff | Breakeven_5Y_z | Forward_Inflation_5Y | Forward_Inflation_5Y_diff | Forward_Inflation_5Y_z | Fed_Funds | Fed_Funds_diff | Fed_Funds_yoy_diff | Treasury_1M | Treasury_1M_diff | Treasury_3M | Treasury_3M_diff | Treasury_6M | Treasury_6M_diff | Treasury_1Y | Treasury_1Y_diff | Treasury_1Y_yoy_diff | Treasury_2Y | Treasury_2Y_diff | Treasury_2Y_yoy_diff | Treasury_5Y | Treasury_5Y_diff | Treasury_5Y_yoy_diff | Treasury_10Y | Treasury_10Y_diff | Treasury_10Y_yoy_diff | Treasury_30Y | Treasury_30Y_diff | Treasury_30Y_yoy_diff | Curve_10Y_2Y | Curve_10Y_2Y_diff | Curve_10Y_2Y_z | Curve_10Y_3M | Curve_10Y_3M_diff | Curve_10Y_3M_z | Spread_10Y_FF | Spread_10Y_FF_diff | Spread_10Y_FF_z | Spread_5Y_FF | Spread_5Y_FF_diff | TIPS_5Y | TIPS_5Y_diff | TIPS_10Y | TIPS_10Y_diff | Term_Premium_10Y | Term_Premium_10Y_diff | Term_Premium_10Y_z | Mortgage_30Y | Mortgage_30Y_diff | Mortgage_30Y_yoy_diff | HY_OAS | HY_OAS_diff | HY_OAS_yoy_diff | HY_OAS_z | IG_OAS | IG_OAS_diff | IG_OAS_yoy_diff | IG_OAS_z | SOFR | SOFR_diff | EFFR | EFFR_diff | OBFR | OBFR_diff | SOFR_Volume | SOFR_Volume_yoy_pct | SOFR_Volume_z | Fed_Balance_Sheet | Fed_Balance_Sheet_yoy_pct | Fed_Balance_Sheet_wow_diff | RRP_Usage | RRP_Usage_diff | RRP_Usage_yoy_diff | RRP_Usage_z | Bank_Reserves | Bank_Reserves_yoy_pct | Bank_Reserves_mom_pct | M2 | M2_yoy_pct | M2_mom_pct | Treasury_General_Account | Treasury_General_Account_diff | Treasury_General_Account_z | Fed_RRP_Outstanding | Fed_RRP_Outstanding_diff | Chicago_NFCI | Chicago_NFCI_diff | Chicago_NFCI_z | Adjusted_NFCI | Adjusted_NFCI_diff | Adjusted_NFCI_z | StLouis_FSI | StLouis_FSI_diff | StLouis_FSI_z | OFR_FSI | OFR_FSI_diff | OFR_FSI_z | OFR_FSI_Credit | OFR_FSI_Credit_diff | OFR_FSI_Credit_z | OFR_FSI_Funding | OFR_FSI_Funding_diff | OFR_FSI_Funding_z | OFR_FSI_Volatility | OFR_FSI_Volatility_diff | OFR_FSI_Volatility_z | OFR_FSI_US | OFR_FSI_US_diff | OFR_FSI_US_z | GDP_Nominal | GDP_Nominal_yoy_pct | GDP_Nominal_qoq_pct | GDP_Real | GDP_Real_yoy_pct | GDP_Real_qoq_pct | Industrial_Production | Industrial_Production_yoy_pct | Industrial_Production_mom_pct | Industrial_Production_3m_ann | Retail_Sales | Retail_Sales_yoy_pct | Retail_Sales_mom_pct | Consumer_Sentiment | Consumer_Sentiment_yoy_pct | Consumer_Sentiment_mom_diff | Consumer_Sentiment_z | Consumer_Credit | Consumer_Credit_yoy_pct | Saving_Rate | Saving_Rate_diff | Saving_Rate_z | Debt_Service_Ratio | Debt_Service_Ratio_diff | Debt_Service_Ratio_z | LO_Survey_CI_Tightening | LO_Survey_CI_Tightening_diff | LO_Survey_CI_Tightening_z | LO_Survey_CC_Tightening | LO_Survey_CC_Tightening_diff | LO_Survey_CC_Tightening_z | CI_Loans | CI_Loans_yoy_pct | Business_Loans | Business_Loans_yoy_pct | Consumer_Loans | Consumer_Loans_yoy_pct | Real_Estate_Loans | Real_Estate_Loans_yoy_pct | Housing_Starts | Housing_Starts_yoy_pct | Housing_Starts_mom_pct | Housing_Starts_z | Housing_Starts_1Unit | Housing_Starts_1Unit_yoy_pct | Building_Permits | Building_Permits_yoy_pct | Building_Permits_mom_pct | Case_Shiller_Home_Prices | Case_Shiller_Home_Prices_yoy_pct | Case_Shiller_Home_Prices_mom_pct | Median_Home_Price | Median_Home_Price_yoy_pct | New_Home_Sales | New_Home_Sales_yoy_pct | New_Home_Sales_mom_pct | Existing_Home_Sales | Existing_Home_Sales_yoy_pct | Existing_Home_Sales_mom_pct | Months_Supply | Months_Supply_diff | Months_Supply_z | Delinquency_All_Loans | Delinquency_All_Loans_diff | Delinquency_All_Loans_yoy_diff | Delinquency_All_Loans_z | Delinquency_Mortgage | Delinquency_Mortgage_diff | Delinquency_Mortgage_yoy_diff | Delinquency_Mortgage_z | Delinquency_Credit_Card | Delinquency_Credit_Card_diff | Delinquency_Credit_Card_yoy_diff | Delinquency_Credit_Card_z | Delinquency_Consumer | Delinquency_Consumer_diff | Delinquency_Consumer_yoy_diff | Delinquency_Consumer_z | Delinquency_Business | Delinquency_Business_diff | Delinquency_Business_yoy_diff | Delinquency_Business_z | Delinquency_CRE | Delinquency_CRE_diff | Delinquency_CRE_yoy_diff | Delinquency_CRE_z | Federal_Debt | Federal_Debt_yoy_pct | Debt_to_GDP | Debt_to_GDP_diff | Federal_Surplus_Deficit | Federal_Surplus_Deficit_diff | Federal_Receipts | Federal_Receipts_yoy_pct | Federal_Expenditures | Federal_Expenditures_yoy_pct | VIX | VIX_diff | VIX_z | VIX_20d_ma | WTI_Crude | WTI_Crude_yoy_pct | WTI_Crude_mom_pct | Dollar_Index | Dollar_Index_yoy_pct | Dollar_Index_mom_pct | EUR_USD | EUR_USD_yoy_pct | JPY_USD | JPY_USD_yoy_pct | BEA_GDP | BEA_GDP_yoy_pct | BEA_GDP_qoq_pct | BEA_PCE | BEA_PCE_yoy_pct | BEA_PCE_qoq_pct | BEA_Investment | BEA_Investment_yoy_pct | BEA_Investment_qoq_pct | BEA_Net_Exports | BEA_Net_Exports_diff | BEA_Govt | BEA_Govt_yoy_pct | BEA_Personal_Income | BEA_Personal_Income_yoy_pct | BEA_Corp_Profits | BEA_Corp_Profits_yoy_pct
------------------------------------------------------------------------------------------------------------------------
1901-06-30 00:00:00 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 63.0 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 
1901-07-01 00:00:00 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 63.038356164383565 | 0.03835616438356482 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 
1901-07-02 00:00:00 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 63.07671232876712 | 0.03835616438355771 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 
1901-07-03 00:00:00 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 63.11506849315069 | 0.03835616438356482 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 
1901-07-04 00:00:00 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 63.153424657534245 | 0.03835616438355771 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 
```

## `lighthouse_indices`

- Rows: 470,885

### Columns

| Column | Type |
|---|---|
| `date` | `TEXT` |
| `index_id` | `TEXT` |
| `value` | `REAL` |
| `status` | `TEXT` |

### First 5 rows

```
date | index_id | value | status
--------------------------------
2026-01-12 | SLI_MCAP | 187.04556356323002 | 
2026-01-12 | SLI_ROC_30D | 0.4 | 
2026-01-12 | SLI_ROC_90D_ANN | 15.4 | 
2018-12-25 | SLI | -0.3271 | STABLE
2018-12-26 | SLI | -0.3214 | STABLE
```

## `lost_and_found`

- Rows: 1,935,853

### Columns

| Column | Type |
|---|---|
| `rootpgno` | `INTEGER` |
| `pgno` | `INTEGER` |
| `nfield` | `INTEGER` |
| `id` | `INTEGER` |
| `c0` | `TEXT` |
| `c1` | `TEXT` |
| `c2` | `TEXT` |
| `c3` | `TEXT` |

### First 5 rows

```
rootpgno | pgno | nfield | id | c0 | c1 | c2 | c3
-------------------------------------------------
123411 | 24 | 3 | 28873246 | TV_USMMI | 2023-01-01 | 233 | 
123411 | 24 | 3 | 28873247 | TV_USMMI | 2023-02-01 | 187.6 | 
123411 | 24 | 3 | 28873248 | TV_USMMI | 2023-03-01 | 217.9 | 
123411 | 24 | 3 | 28873249 | TV_USMMI | 2023-04-01 | 214.4 | 
123411 | 24 | 3 | 28873250 | TV_USMMI | 2023-05-01 | 197.4 | 
```

## `lost_and_found_0`

- Rows: 72,250

### Columns

| Column | Type |
|---|---|
| `rootpgno` | `INTEGER` |
| `pgno` | `INTEGER` |
| `nfield` | `INTEGER` |
| `id` | `INTEGER` |
| `c0` | `TEXT` |
| `c1` | `TEXT` |
| `c2` | `TEXT` |

### First 5 rows

```
rootpgno | pgno | nfield | id | c0 | c1 | c2
--------------------------------------------
468 | 468 | 3 | 44967107 | DALLSRESFRMT100EP | 2009-10-01 | 217186
468 | 468 | 3 | 44967108 | DALLSRESFRMT100EP | 2010-01-01 | 222493
468 | 468 | 3 | 44967109 | DALLSRESFRMT100EP | 2010-04-01 | 209056
468 | 468 | 3 | 44967110 | DALLSRESFRMT100EP | 2010-07-01 | 208275
468 | 468 | 3 | 44967111 | DALLSRESFRMT100EP | 2010-10-01 | 205332
```

## `observations`

- Rows: 4,199,160

### Columns

| Column | Type |
|---|---|
| `series_id` | `TEXT` |
| `date` | `TEXT` |
| `value` | `REAL` |

### First 5 rows

```
series_id | date | value
------------------------
DRCLT100N | 1987-01-01 | 3.92
DRCLT100N | 1987-04-01 | 3.59
DRCLT100N | 1987-07-01 | 3.78
DRCLT100N | 1987-10-01 | 3.87
DRCLT100N | 1988-01-01 | 3.91
```

## `series_meta`

- Rows: 2,504

### Columns

| Column | Type |
|---|---|
| `series_id` | `TEXT` |
| `title` | `TEXT` |
| `source` | `TEXT` |
| `category` | `TEXT` |
| `frequency` | `TEXT` |
| `units` | `TEXT` |
| `last_updated` | `TEXT` |
| `last_fetched` | `TEXT` |
| `data_quality` | `TEXT` |
| `last_value_date` | `TEXT` |
| `obs_count` | `INTEGER` |

### First 5 rows

```
series_id | title | source | category | frequency | units | last_updated | last_fetched | data_quality | last_value_date | obs_count
------------------------------------------------------------------------------------------------------------------------
DRCLT100N | Delinquency Rate on Consumer Loans, Banks Ranked 1st to 100th Largest in Size by Assets | FRED | Employment_Situation | Quarterly, End of Period | Percent | 2025-11-21 07:19:41-06 | 2026-01-10T22:10:20.970793 | stale | 2025-07-01 | 155
PCECTPIRH | FOMC Summary of Economic Projections for the Personal Consumption Expenditures Inflation Rate, Range, High | FRED | CPI_Urban_Consumers | Annual | Fourth Quarter to Fourth Quarter Percent Change | 2025-12-10 14:09:35-06 | 2026-01-10T22:10:39.107225 | insufficient | 2028-01-01 | 4
EUROREC | OECD based Recession Indicators for Euro Area from the Period following the Peak through the Trough (DISCONTINUED) | FRED | Industrial_Production | Monthly | +1 or 0 | 2022-12-09 14:52:02-06 | 2026-01-10T22:10:46.431384 | stale | 2022-08-01 | 750
EURORECD | OECD based Recession Indicators for Euro Area from the Period following the Peak through the Trough (DISCONTINUED) | FRED | Industrial_Production | Daily, 7-Day | +1 or 0 | 2022-12-09 14:50:02-06 | 2026-01-10T22:10:47.096933 | stale | 2022-08-31 | 22829
GBRRECDM | OECD based Recession Indicators for the United Kingdom from the Peak through the Trough (DISCONTINUED) | FRED | Industrial_Production | Daily, 7-Day | +1 or 0 | 2022-12-09 14:43:01-06 | 2026-01-10T22:10:47.473525 | stale | 2022-09-30 | 24714
```

## `update_log`

- Rows: 101

### Columns

| Column | Type |
|---|---|
| `id` | `INTEGER` |
| `timestamp` | `TEXT` |
| `source` | `TEXT` |
| `series_updated` | `INTEGER` |
| `observations_added` | `INTEGER` |
| `duration_seconds` | `REAL` |
| `status` | `TEXT` |
| `errors` | `TEXT` |

### First 5 rows

```
id | timestamp | source | series_updated | observations_added | duration_seconds | status | errors
--------------------------------------------------------------------------------------------------
1 | 2026-01-10T22:16:08.103729 | ALL | 615 | 1406626 | 359.1358678340912 |  | 
2 | 2026-01-11T03:53:57.982669 | ALL | 188 | 535593 | 101.10659694671631 |  | 
3 | 2026-01-11T11:45:15.884457 | ALL | 171 | 405517 | 84.56910419464111 |  | 
4 | 2026-01-11T11:47:00.261475 | ALL | 176 | 434310 | 88.79145693778992 |  | 
5 | 2026-01-11T11:49:06.043280 | ALL | 177 | 443296 | 112.38784575462341 |  | 
```

## `series_meta` — categories and sources

### Categories

| Category | Series |
|---|---:|
| Curated | 704 |
| Crypto_Chain_TVL | 383 |
| Industrial_Production | 180 |
| Business_Lending | 112 |
| Housing | 107 |
| Regional_Fed_Surveys | 99 |
| Personal_Income | 87 |
| Employment_Cost_Index | 73 |
| Employment_Situation | 66 |
| GDP_National_Accounts | 62 |
| CPI_Urban_Consumers | 59 |
| Crypto_Prices | 57 |
| Treasury_Rates | 40 |
| Govt_Receipts_Expenditures | 38 |
| Corporate_Profits | 37 |
| Interest_Rates | 34 |
| Exchange_Rates | 32 |
| Labor_Prices | 31 |
| PCE_Components | 31 |
| PCE_Price_Index | 31 |
| ETF | 24 |
| GDI | 24 |
| GDP_Components | 22 |
| Real_GDP_Growth | 21 |
| Trade | 21 |
| GDP_Price_Index | 20 |
| Business | 17 |
| Crypto_TVL | 16 |
| Market_Structure | 15 |
| Market_Breadth | 13 |
| Short_Term_Funding | 12 |
| Reference_Rates | 10 |
| Financial_Stress | 9 |
| Sentiment | 6 |
| Crypto_Global | 5 |
| macro_business | 3 |
| Retail_Features | 1 |
| macro_growth | 1 |
| macro_prices | 1 |

### Sources

| Source | Series |
|---|---:|
| FRED | 1561 |
| DefiLlama | 399 |
| BEA | 267 |
| CoinGecko | 62 |
| TradingView | 47 |
| Zillow | 42 |
| Yahoo | 39 |
| BLS | 31 |
| OFR | 21 |
| Computed | 13 |
| NYFED | 10 |
| AAII | 4 |
| Census M3 via FRED | 3 |
| Derived | 2 |
| BEA via FRED | 1 |
| BLS via FRED | 1 |
| Lighthouse_Computed | 1 |

## `lighthouse_indices` — composites available

| index_id | rows | earliest | latest |
|---|---:|---|---|
| `ALLOC_MULTIPLIER` | 20 | 2026-01-16 | 2026-05-01 |
| `BASE_REC_PROB` | 20 | 2026-01-16 | 2026-05-01 |
| `BCI` | 28,901 | 1947-01-24 | 2026-04-21 |
| `BILL_SOFR` | 2,898 | 2018-04-03 | 2026-03-09 |
| `CCI` | 26,705 | 1952-11-12 | 2026-01-01 |
| `CDI` | 2 | 2026-02-01 | 2026-02-02 |
| `CFI` | 11 | 2026-01-20 | 2026-02-02 |
| `CLG` | 10,411 | 1997-09-08 | 2026-03-10 |
| `CRYPTO_DEFI___DERIVATIVES_HEALTH` | 11 | 2026-01-20 | 2026-02-02 |
| `CRYPTO_DEFI___DEX_HEALTH` | 11 | 2026-01-20 | 2026-02-02 |
| `CRYPTO_DEFI___LENDING_HEALTH` | 11 | 2026-01-20 | 2026-02-02 |
| `CRYPTO_INFRASTRUCTURE_HEALTH` | 11 | 2026-01-20 | 2026-02-02 |
| `CRYPTO_LAYER_1_(SETTLEMENT)_HEALTH` | 11 | 2026-01-20 | 2026-02-02 |
| `CRYPTO_LAYER_2_(SCALING)_HEALTH` | 11 | 2026-01-20 | 2026-02-02 |
| `CRYPTO_LIQUID_STAKING_HEALTH` | 11 | 2026-01-20 | 2026-02-02 |
| `CRYPTO_UNCATEGORIZED_HEALTH` | 11 | 2026-01-20 | 2026-02-02 |
| `CTI` | 11 | 2026-01-20 | 2026-02-02 |
| `CVI` | 2 | 2026-02-01 | 2026-02-02 |
| `DISCONTINUITY_PREMIUM` | 20 | 2026-01-16 | 2026-05-01 |
| `EMD` | 12,966 | 1990-09-10 | 2026-04-21 |
| `ENSEMBLE_RISK` | 20 | 2026-01-16 | 2026-05-01 |
| `FCI` | 20,114 | 1971-02-28 | 2026-05-01 |
| `GCI` | 39,035 | 1919-01-24 | 2026-01-01 |
| `GCI_Gov` | 21,977 | 1966-01-04 | 2026-03-06 |
| `HCI` | 24,475 | 1959-01-12 | 2026-02-01 |
| `LCI` | 24,300 | 1959-01-12 | 2026-05-01 |
| `LDI` | 9,132 | 2000-12-01 | 2025-12-01 |
| `LFI` | 28,548 | 1948-01-12 | 2026-03-10 |
| `LIQ_STAGE` | 45,559 | 1901-06-30 | 2026-05-01 |
| `LPI` | 27,995 | 1948-01-12 | 2026-02-28 |
| `MRI` | 39,117 | 1919-01-24 | 2026-05-01 |
| `MSI` | 6,552 | 2000-04-12 | 2026-05-01 |
| `PCI` | 26,043 | 1953-01-24 | 2026-05-01 |
| `REC_PROB` | 13,270 | 1990-01-01 | 2026-05-01 |
| `SBD` | 6,411 | 2000-10-31 | 2026-04-30 |
| `SLI` | 2,583 | 2018-12-25 | 2026-01-19 |
| `SLI_MCAP` | 1 | 2026-01-12 | 2026-01-12 |
| `SLI_ROC_30D` | 1 | 2026-01-12 | 2026-01-12 |
| `SLI_ROC_90D_ANN` | 1 | 2026-01-12 | 2026-01-12 |
| `SPI` | 9,236 | 1987-10-09 | 2026-04-30 |
| `SSD` | 6,540 | 2000-04-28 | 2026-04-30 |
| `SVI` | 10,410 | 1997-09-08 | 2026-03-09 |
| `TCI` | 9,547 | 2000-01-16 | 2026-03-06 |
| `WARNING_LEVEL` | 20 | 2026-01-16 | 2026-05-01 |
| `YFS` | 17,943 | 1977-02-07 | 2026-05-01 |
