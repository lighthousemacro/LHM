# LIGHTHOUSE MACRO - PROPRIETARY INDICATORS REFERENCE
## Complete Guide to Bob Sheehan's Custom Measurements, Indices & Frameworks

**Last Updated:** January 19, 2026
**Compiled From:** All published articles on [lighthousemacro.com](https://www.lighthousemacro.com) + 12-Pillar Macro Framework (The Diagnostic Dozen)

---

## TABLE OF CONTENTS

### SECTION 1: MASTER COMPOSITE INDEX
1\. Macro Risk Index (MRI) v2.0 - Updated 12-Pillar Formula

### SECTION 2: PILLAR COMPOSITE INDICES
2\. Labor Pillar Composite Index (LPI)
3\. Prices Pillar Composite Index (PCI)
4\. Growth Pillar Composite Index (GCI)
5\. Housing Pillar Composite Index (HCI)
6\. Consumer Pillar Composite Index (CCI)
7\. Business Pillar Composite Index (BCI)
8\. Trade Pillar Composite Index (TCI)
9\. Government Pillar Composite Index (GCI-Gov)
10\. Financial Pillar Composite Index (FCI)
11\. Liquidity Cushion Index (LCI) - Plumbing Formula
12\. Market Structure Index (MSI) - NEW in v2.0
13\. Sentiment Pillar Index (SPI) - NEW in v2.0

### SECTION 3: LABOR MARKET INDICATORS
14\. Labor Fragility Index (LFI)
15\. Labor Dynamism Index (LDI)
16\. Job-Hopper Premium

### SECTION 4: CREDIT & FUNDING STRESS INDICATORS
17\. Yield-Funding Stress (YFS)
18\. Credit-Labor Gap (CLG)
19\. Spread-Volatility Imbalance (SVI)
20\. Repo Rate Dispersion Index

### SECTION 5: EQUITY & MARKET POSITIONING
21\. Equity Momentum Divergence (EMD)
22\. QUAL/SPY Ratio (Quality vs Risk)

### SECTION 6: LIQUIDITY INDICATORS
23\. Liquidity Transmission Framework
24\. Leverage Capacity Matrix
25\. Liquidity Composite Index

### SECTION 7: TREASURY MARKET MICROSTRUCTURE
26\. Collateral Shortage Index
27\. Treasury Auction Tailing Metric
28\. Bid-to-Cover Ratio Analysis
29\. Dealer Allotment Percentage
30\. Dealer Accumulation Momentum
31\. Treasury Stress Dashboard (4-Metric System)
32\. Bill-Bond Divergence Analysis
33\. Treasury Composition Shift Index

### SECTION 8: STABLECOIN & CRYPTO INTEGRATION
34\. Stablecoin Treasury Holdings Percentage
35\. Stablecoin Supply Correlation with T-Bill Richness
36\. 3M Bill-SOFR Spread
37\. Stablecoin Liquidity Impulse (SLI)

### SECTION 9: ADVANCED TRADING FRAMEWORKS
38\. Z-Score Positioning Index (Basis Trades)
39\. Compression Function Model
40\. Recovery Half-Life Metric
41\. Market-Neutral Basis Sharpe Ratio

---

# SECTION 1: MASTER COMPOSITE INDEX

## 1. Macro Risk Index (MRI) v2.0 - Updated 12-Pillar Formula

**Source:** 12-Pillar Macro Framework "The Diagnostic Dozen" (January 2026)

### Formula (v2.0)

```
MRI = 0.12 × (-LPI)           # Labor (inverted: low LPI = high risk)
    + 0.08 × PCI              # Prices (high = inflation risk)
    + 0.12 × (-GCI)           # Growth (inverted: low GCI = high risk)
    + 0.06 × (-HCI)           # Housing (inverted)
    + 0.08 × (-CCI)           # Consumer (inverted)
    + 0.08 × (-BCI)           # Business (inverted)
    + 0.05 × (-TCI)           # Trade (inverted)
    + 0.10 × GCI-Gov          # Government (high = fiscal stress)
    + 0.05 × (-FCI)           # Financial (inverted: low FCI = tight conditions)
    + 0.10 × (-LCI)           # Plumbing (inverted: low LCI = thin cushion)
    + 0.08 × (-MSI)           # Market Structure (inverted: low MSI = weak structure)
    + 0.08 × SPI              # Sentiment (high = contrarian risk)
```

### Component Weighting Rationale (v2.0)
- **Labor (12%):** Leading indicator, drives the cycle
- **Growth (12%):** Core GDP health, investment focus
- **Government (10%):** Fiscal dominance regime
- **Plumbing (10%):** System vulnerability, amplifies shocks
- **Consumer (8%):** 68% of GDP, confirms labor signals
- **Business (8%):** Transmission mechanism, capex decisions
- **Prices (8%):** Inflation risk, Fed reaction function
- **Structure (8%):** Market health and breadth confirmation
- **Sentiment (8%):** Contrarian crowding gauge
- **Housing (6%):** Interest rate sensitive, wealth effect
- **Trade (5%):** Global margin, tariff transmission
- **Financial (5%):** Already embedded in other pillars

**v2.0 Change:** Added Pillars 11-12 (Structure, Sentiment) with 8% weight each, rebalanced other pillars accordingly.

### Interpretation

| **MRI Range** | **Regime** | **Portfolio Stance** | **Historical Context** |
|---|---|---|---|
| > +1.5 | Crisis | Maximum defensive | 2008, March 2020 |
| +1.0 to +1.5 | High Risk | Underweight risk | Late 2007, Q4 2018 |
| +0.5 to +1.0 | Elevated | Neutral to cautious | Late-cycle transitions |
| -0.5 to +0.5 | Normal | Standard allocation | Mid-cycle stability |
| < -0.5 | Low Risk | Overweight risk | Early-cycle expansion |

### Current State (January 2026)
- **MRI: +1.1** (High Risk Regime)
- **Key Contributors:** LFI +0.93, GCI -0.4, LCI -0.8, GCI-Gov +1.1
- **Interpretation:** System operating with thin margins. Labor fragility + fiscal stress + exhausted liquidity buffer = elevated risk despite equity resilience.

---

# SECTION 2: PILLAR COMPOSITE INDICES

## 2. Labor Pillar Composite Index (LPI)

**Source:** Pillar 1: Labor (January 2026)

### Formula

```
LPI = 0.20 × z(Quits_Rate)
    + 0.15 × z(Hires_Quits_Ratio)
    + 0.15 × z(-Long_Term_Unemployed_Share)   # Inverted (high = weak)
    + 0.15 × z(-Initial_Claims_4wk_MA)         # Inverted
    + 0.10 × z(Prime_Age_LFPR)
    + 0.10 × z(Avg_Weekly_Hours_Mfg)
    + 0.10 × z(-Temp_Help_YoY)                 # Inverted (declining = weak)
    + 0.05 × z(Job_Hopper_Premium)
```

### Component Weighting Rationale
- **Quits Rate (20%):** Primary leading indicator of worker confidence
- **Hires/Quits Ratio (15%):** Labor market dynamism gauge
- **Long-Term Unemployment (15%):** Structural damage indicator (inverted)
- **Initial Claims (15%):** High-frequency stress signal (inverted)
- **Prime-Age LFPR (10%):** Supply-side health
- **Weekly Hours (10%):** Intensive margin, leads payrolls
- **Temp Help (10%):** Early-cycle canary (inverted)
- **Job-Hopper Premium (5%):** Wage dynamism confirmation

### Interpretation

| **LPI Range** | **Regime** | **Labor Allocation** | **Signal** |
|---|---|---|---|
| > +1.0 | Boom | Overweight cyclicals | Full employment, wage pressure |
| +0.5 to +1.0 | Healthy | Neutral | Sustainable growth |
| -0.5 to +0.5 | Neutral | Slight caution | Decelerating |
| -1.0 to -0.5 | Weak | Underweight consumer discretionary | Stress emerging |
| < -1.0 | Crisis | Defensive positioning | Recession confirmed |

### Current State (January 2026)
- **LPI: -0.2** (Neutral, weakening)
- **Key Drivers:** Quits at 2.1% (declining), LFI at +0.93 (fragility), claims stable but rising

---

## 3. Prices Pillar Composite Index (PCI)

**Source:** Pillar 2: Prices (January 2026)

### Formula

```
PCI = 0.30 × z(Core_PCE_3M_Ann)
    + 0.20 × z(Services_ex_Shelter_YoY)
    + 0.15 × z(Shelter_CPI_YoY)
    + 0.15 × z(Sticky_CPI_YoY)
    + 0.10 × z(5Y5Y_Forward_Inflation)
    + 0.10 × z(-Goods_CPI_YoY)                 # Inverted (deflation = drag on headline)
```

### Interpretation

| **PCI Range** | **Regime** | **Duration Stance** | **Signal** |
|---|---|---|---|
| > +1.5 | Inflation Crisis | Maximum short duration | 1970s echo |
| +1.0 to +1.5 | High Inflation | Underweight duration | Fed must tighten |
| +0.5 to +1.0 | Elevated | Neutral duration | "Last mile" sticky |
| -0.5 to +0.5 | Target | Standard allocation | 2% achieved |
| < -0.5 | Deflation Risk | Overweight duration | Demand collapse |

### Current State (January 2026)
- **PCI: +0.7** (Elevated—"Last Mile" Regime)
- **Core PCE at 3.2%**, Services ex-Shelter at 3.6%, Goods at -1.2%

---

## 4. Growth Pillar Composite Index (GCI)

**Source:** Pillar 3: Growth (January 2026)

### Formula

```
GCI = 0.25 × z(Industrial_Production_YoY)
    + 0.20 × z(ISM_Manufacturing)
    + 0.15 × z(Core_Capital_Goods_Orders_YoY)
    + 0.15 × z(Aggregate_Weekly_Hours_YoY)
    + 0.10 × z(Real_Retail_Sales_YoY)
    + 0.10 × z(Housing_Starts_YoY)
    + 0.05 × z(-GDI_GDP_Spread)                # Inverted (negative spread = income weak)
```

### Interpretation

| **GCI Range** | **Regime** | **Cyclical Allocation** | **Signal** |
|---|---|---|---|
| > +1.0 | Strong Growth | Overweight cyclicals | Expansion acceleration |
| +0.5 to +1.0 | Above Trend | Moderate cyclical | Healthy growth |
| -0.5 to +0.5 | Trend | Balanced | Sustainable pace |
| -1.0 to -0.5 | Below Trend | Underweight cyclicals | Contraction risk |
| < -1.0 | Contraction | Defensive | Recession confirmed |

### Current State (January 2026)
- **GCI: -0.4** (Below Trend—Contraction Risk)
- **IP at -0.8% YoY**, ISM Mfg at 49.3, Capex orders at -2.8% YoY

---

## 5. Housing Pillar Composite Index (HCI)

**Source:** Pillar 4: Housing (January 2026)

### Formula

```
HCI = 0.20 × z(Housing_Starts_YoY)
    + 0.15 × z(Existing_Home_Sales_YoY)
    + 0.15 × z(NAHB_Index)
    + 0.15 × z(-Months_Supply)                  # Inverted (high supply = weak)
    + 0.10 × z(HPI_YoY)
    + 0.10 × z(-30Y_Mortgage_Rate)              # Inverted (high rates = drag)
    + 0.10 × z(MBA_Purchase_Index_YoY)
    + 0.05 × z(-Mortgage_Delinquency_30Day)     # Inverted
```

### Interpretation

| **HCI Range** | **Regime** | **Housing Allocation** | **Signal** |
|---|---|---|---|
| > +1.0 | Housing Boom | Overweight homebuilders | Transaction surge |
| +0.5 to +1.0 | Healthy | Neutral | Sustainable activity |
| -0.5 to +0.5 | Neutral/Frozen | Slight underweight | Rate-constrained |
| -1.0 to -0.5 | Weak | Underweight housing | Demand destruction |
| < -1.0 | Crisis | Avoid housing exposure | Price correction underway |

### Current State (January 2026)
- **HCI: -0.6** (Weak—Frozen Market)
- **Mortgage rates at 6.95%**, Sales -15% YoY, Starts -12% YoY

---

## 6. Consumer Pillar Composite Index (CCI)

**Source:** Pillar 5: Consumer (January 2026)

### Formula

```
CCI = 0.25 × z(Real_PCE_YoY)
    + 0.20 × z(Personal_Saving_Rate)
    + 0.15 × z(-Credit_Card_Delinquency)        # Inverted (high DQ = weak)
    + 0.15 × z(CB_Expectations)
    + 0.10 × z(Real_DPI_YoY)
    + 0.10 × z(-Debt_Service_Ratio)             # Inverted (high DSR = weak)
    + 0.05 × z(Card_Spending_YoY)
```

### Interpretation

| **CCI Range** | **Regime** | **Discretionary Allocation** | **Signal** |
|---|---|---|---|
| > +1.0 | Consumer Boom | Overweight discretionary, travel | Full expansion |
| +0.5 to +1.0 | Healthy | Neutral discretionary | Sustainable growth |
| -0.5 to +0.5 | Neutral/Fatigued | Slight underweight | Deceleration |
| -1.0 to -0.5 | Stressed | Underweight discretionary, overweight staples | Demand destruction |
| < -1.0 | Crisis | Maximum defensive (staples, discount) | Recession confirmed |

### Current State (January 2026)
- **CCI: -0.3** (Fatigued Regime)
- **Real PCE +2.1%**, Saving rate 4.5% (depleted), CC delinquency 3.0%

---

## 7. Business Pillar Composite Index (BCI)

**Source:** Pillar 6: Business (January 2026)

### Formula

```
BCI = 0.20 × z(NFIB_Optimism)
    + 0.20 × z(Core_Capex_Orders_YoY)
    + 0.15 × z(ISM_Manufacturing)
    + 0.15 × z(ISM_Services)
    + 0.10 × z(-Inventory_Sales_Ratio)          # Inverted (high I/S = weak)
    + 0.10 × z(SP500_Earnings_YoY)
    + 0.05 × z(-SLOOS_Net_Tightening)           # Inverted (tightening = weak)
    + 0.05 × z(-HY_Spreads)                     # Inverted (wide = weak)
```

### Interpretation

| **BCI Range** | **Regime** | **Cyclical Allocation** | **Signal** |
|---|---|---|---|
| > +1.0 | Business Boom | Overweight industrials, small caps | Full expansion |
| +0.5 to +1.0 | Expansion | Neutral cyclicals | Healthy growth |
| -0.5 to +0.5 | Neutral/Slowing | Underweight small caps | Deceleration |
| -1.0 to -0.5 | Contraction | Avoid small caps, underweight cyclicals | Earnings recession |
| < -1.0 | Crisis | Maximum defensive | Broad recession |

### Current State (January 2026)
- **BCI: -0.4** (Slowing Regime)
- **NFIB at 89.4** (lowest since 2012), Capex orders -2.8%, ISM Mfg 49.3

---

## 8. Trade Pillar Composite Index (TCI)

**Source:** Pillar 7: Trade (January 2026)

### Formula

```
TCI = 0.20 × z(-Import_Price_YoY)               # Inverted (high = inflationary)
    + 0.20 × z(-Trade_Balance_GDP_Ratio)        # Inverted (larger deficit = weaker)
    + 0.15 × z(Export_Volume_YoY)
    + 0.15 × z(-NY_Fed_GSCPI)                   # Inverted (high = supply stress)
    + 0.10 × z(Container_Volume_YoY)
    + 0.10 × z(-DXY_YoY)                        # Inverted (strong dollar = headwind)
    + 0.10 × z(-Trade_Policy_Uncertainty)       # Inverted (high = negative)
```

### Interpretation

| **TCI Range** | **Regime** | **Trade Allocation** | **Signal** |
|---|---|---|---|
| > +1.0 | Trade Tailwind | Overweight exporters, EM | Globalization tailwind |
| +0.5 to +1.0 | Favorable | Neutral global exposure | Stable trade conditions |
| -0.5 to +0.5 | Neutral | Balanced | Mixed conditions |
| -1.0 to -0.5 | Headwind | Underweight trade-sensitive | Tariff/dollar drag |
| < -1.0 | Trade Crisis | Maximum defensive | De-globalization shock |

### Current State (January 2026)
- **TCI: -0.5** (Headwind Regime)
- **Import prices +3.8%** (tariff pass-through), DXY +7.2% YoY

---

## 9. Government Pillar Composite Index (GCI-Gov)

**Source:** Pillar 8: Government (January 2026)

### Formula

```
GCI-Gov = 0.25 × z(Deficit_GDP)
        + 0.20 × z(Interest_Outlays_Pct)
        + 0.15 × z(Debt_GDP)
        + 0.15 × z(Term_Premium)
        + 0.10 × z(Quarterly_Issuance)
        + 0.10 × z(-Receipts_YoY)               # Inverted (falling receipts = stress)
        + 0.05 × z(-Foreign_Holdings_Pct)       # Inverted (falling = less demand)
```

### Interpretation

| **GCI-Gov Range** | **Regime** | **Duration Allocation** | **Signal** |
|---|---|---|---|
| > +1.5 | Fiscal Crisis | Maximum underweight duration | Yields spiking |
| +1.0 to +1.5 | High Stress | Underweight duration | Term premium repricing |
| +0.5 to +1.0 | Elevated | Neutral duration | Fiscal drag building |
| -0.5 to +0.5 | Normal | Standard allocation | Sustainable path |
| < -0.5 | Fiscal Health | Overweight duration | Surplus/consolidation |

### Current State (January 2026)
- **GCI-Gov: +1.1** (High Stress—Fiscal Dominance Regime)
- **Deficit/GDP 7.2%**, Interest 16% of outlays, Term premium +25 bps (rising)

---

## 10. Financial Pillar Composite Index (FCI)

**Source:** Pillar 9: Financial (January 2026)

### Formula

```
FCI = 0.20 × z(-HY_OAS)                         # Inverted (tight spreads = loose)
    + 0.15 × z(-NFCI)                           # Inverted (negative = loose)
    + 0.15 × z(Yield_Curve_10Y2Y)
    + 0.15 × z(-Real_Fed_Funds)                 # Inverted (high = tight)
    + 0.10 × z(C&I_Loan_Growth)
    + 0.10 × z(-VIX)                            # Inverted (high = stressed)
    + 0.10 × z(LCI)
    + 0.05 × z(-SLOOS_Tightening)               # Inverted (tightening = negative)
```

### Interpretation

| **FCI Range** | **Regime** | **Risk Allocation** | **Signal** |
|---|---|---|---|
| > +1.0 | Very Loose | Overweight risk assets | Financial tailwind |
| +0.5 to +1.0 | Loose | Moderate risk-on | Conditions supportive |
| -0.5 to +0.5 | Neutral | Balanced | Mixed conditions |
| -1.0 to -0.5 | Tight | Underweight risk | Conditions headwind |
| < -1.0 | Crisis | Maximum defensive | Financial stress |

### Current State (January 2026)
- **FCI: +0.3** (Neutral, but DIVERGENT signals)
- **HY OAS 290 bps** (3rd percentile), VIX 14.2, but SLOOS +38% tightening

---

## 11. Liquidity Cushion Index (LCI) - Updated Plumbing Formula

**Source:** Pillar 10: Plumbing (January 2026)

### Formula (Updated)

```
LCI = 0.25 × z(Reserves_vs_LCLOR)
    + 0.20 × z(-EFFR_IORB_Spread)               # Inverted (positive spread = stress)
    + 0.15 × z(-SOFR_IORB_Spread)               # Inverted
    + 0.15 × z(RRP_Balance)                     # Buffer level
    + 0.10 × z(-GCF_TPR_Spread)                 # Inverted (dealer stress)
    + 0.10 × z(-Dealer_Net_Position)            # Inverted (congestion)
    + 0.05 × z(-EUR_USD_Basis)                  # Inverted (offshore stress)
```

### Interpretation

| **LCI Range** | **Regime** | **Risk Asset Stance** | **Signal** |
|---|---|---|---|
| > +1.0 | Abundant Liquidity | Overweight risk | Flush system, tailwind |
| +0.5 to +1.0 | Ample | Neutral | Normal functioning |
| -0.5 to +0.5 | Tight | Slight underweight | Vigilance required |
| -1.0 to -0.5 | Scarce | Underweight risk | Stress emerging |
| < -1.0 | Crisis | Maximum defense | Systemic stress, intervention likely |

### Current State (January 2026)
- **LCI: -0.8** (Scarce Regime—Buffer Exhausted)
- **RRP at $150B** (94% drained from $2.55T peak)
- **Reserves at $3.3T** (~$300B above LCLOR estimate)
- **EFFR-IORB at +3 bps** (drifting toward scarcity)

---

## 12. Market Structure Index (MSI) — NEW in v2.0

**Source:** Pillar 11: Market Structure (January 2026)

### Formula

```
MSI = 0.15 × z(Price_vs_200d_MA_%)
    + 0.10 × z(Price_vs_50d_MA_%)
    + 0.10 × z(50d_MA_Slope)
    + 0.10 × z(20d_MA_Slope)
    + 0.12 × z(Z_RoC_63d)
    + 0.10 × z(%_Stocks_>_50d_MA)
    + 0.08 × z(%_Stocks_>_20d_MA)
    + 0.08 × z(%_Stocks_>_200d_MA)
    + 0.07 × z(Net_New_Highs_Lows_20d_Avg)
    + 0.05 × z(AD_Line_50d_Slope)
    + 0.05 × z(McClellan_Summation)
```

### Component Weighting Rationale
- **Price vs 200d MA (15%):** Long-term trend anchor
- **Z-RoC 63d (12%):** Momentum confirmation
- **Price vs 50d MA (10%):** Medium-term positioning
- **50d MA Slope (10%):** Trend direction
- **20d MA Slope (10%):** Short-term momentum
- **% Stocks > 50d MA (10%):** Breadth health
- **% Stocks > 20d MA (8%):** Near-term breadth
- **% Stocks > 200d MA (8%):** Regime classification
- **Net New Highs/Lows (7%):** Leadership
- **AD Line Slope (5%):** Cumulative breadth
- **McClellan Summation (5%):** Breadth momentum

### Interpretation

| **MSI Range** | **Regime** | **Action** |
|---------------|-----------|------------|
| > +1.0 | Healthy Structure | Full allocation |
| +0.5 to +1.0 | Constructive | Standard allocation |
| -0.5 to +0.5 | Mixed | Monitor for divergences |
| -1.0 to -0.5 | Deteriorating | Reduce exposure |
| < -1.0 | Broken | Defensive positioning |

### Breadth Thrust Detection
**Signal:** % Stocks > 20d MA moves from <30% to >70% within 10 trading days
**Interpretation:** Powerful momentum shift, historically bullish
**Action:** Override cautious stance, increase equity allocation

---

## 13. Sentiment Pillar Index (SPI) — NEW in v2.0

**Source:** Pillar 12: Sentiment (January 2026)

### Formula

```
SPI = 0.20 × z(AAII_Bull_Bear_Spread)
    + 0.15 × z(Put_Call_Ratio_Inverted)
    + 0.15 × z(VIX_vs_Realized_Vol)
    + 0.15 × z(Fund_Flows_Equity)
    + 0.15 × z(CNN_Fear_Greed)
    + 0.10 × z(NAAIM_Exposure)
    + 0.10 × z(Options_Skew)
```

### Component Weighting Rationale
- **AAII Bull/Bear (20%):** Retail sentiment, strong contrarian signal
- **Put/Call Ratio (15%):** Options market positioning
- **VIX vs Realized Vol (15%):** Implied vs actual volatility
- **Fund Flows (15%):** Institutional money movement
- **CNN Fear/Greed (15%):** Composite sentiment gauge
- **NAAIM Exposure (10%):** Active manager positioning
- **Options Skew (10%):** Tail risk demand

### Interpretation

| **SPI Range** | **Regime** | **Signal** |
|---------------|-----------|------------|
| > +1.5 | Extreme Greed | Contrarian bearish |
| +0.5 to +1.5 | Optimistic | Caution warranted |
| -0.5 to +0.5 | Neutral | No signal |
| -1.5 to -0.5 | Pessimistic | Accumulation zone |
| < -1.5 | Extreme Fear | Contrarian bullish |

### Sentiment-Structure Divergence (SSD)
```
SSD = SPI - MSI
```
- **SSD > +1.5:** Sentiment euphoric but structure weak = High risk
- **SSD < -1.5:** Sentiment washed but structure intact = Opportunity

---

# SECTION 3: LABOR MARKET INDICATORS

## 14. Labor Fragility Index (LFI)

**Source:** "The Beacon | It's Getting Spooky" (Oct 30, 2025) + Pillar 1 Enhancement

### Formula

```
LFI = 0.35 × z(Long_Duration_Unemployment_Share)
    + 0.35 × z(-Quits_Rate)                     # Inverted (declining quits = fragile)
    + 0.30 × z(-Hires_to_Quits_Ratio)           # Inverted
```

### Data Inputs
- **Long-Duration Unemployment Share:** % of unemployed persons jobless ≥27 weeks (BLS, monthly)
- **Quits Rate:** JOLTS quits as % of employment (BLS JOLTS, monthly)
- **Hires-to-Quits Ratio:** JOLTS hires divided by quits (monthly)

### Interpretation
- **LFI > +1σ:** Elevated labor fragility, structural deterioration
- **LFI near 0:** Normal labor market health
- **LFI < -1σ:** Robust labor market, low fragility

### Current State (January 2026)
- **LFI: +0.93** (Elevated Fragility)
- **Long-term unemployment 24.5%**, Quits 2.1% (declining), Hires/Quits 1.18

### Cross-Pillar Signal
When **LFI > +0.8** AND **CCI < -0.3**, recession probability exceeds 65% within 12 months. **Current: LFI +0.93, CCI -0.3** — Warning threshold engaged.

---

## 13. Labor Dynamism Index (LDI)

**Source:** "The Beacon | It's Getting Spooky" (Oct 30, 2025)

### Formula

```
LDI = z(Quits_Rate)
    + z(Hires_to_Quits_Ratio)
    + z(Quits_to_Layoffs_Ratio)

LDI = average of three components
```

### Interpretation
- **High LDI (>+1σ):** Workers have optionality, confident in job-switching
- **Low LDI (<-1σ):** Workers hesitant to quit, late-cycle caution
- **Below 0σ (current):** Reduced worker mobility, risk aversion

### Relationship to LFI
- **LDI measures:** Worker confidence/optionality (behavioral)
- **LFI measures:** Labor market stress/fragility (structural)
- **Divergence:** Rising LFI + Falling LDI = Late-cycle deterioration (**Current State**)

---

## 14. Job-Hopper Premium

**Source:** "The Vanishing Job-Hopper Premium" (Mar 14, 2025)

### Formula

```
Job_Hopper_Premium = Wage_Growth_Job_Switchers - Wage_Growth_Job_Stayers
```

### Data Source
- **Atlanta Fed Wage Growth Tracker** (breaks down wage growth by job-switchers vs stayers)

### Current State (January 2026)
- Premium at **0.3 percentage points** (historical average: 2-4 ppts)
- Signals employer leverage over workers
- Confirms declining labor dynamism

---

# SECTION 4: CREDIT & FUNDING STRESS INDICATORS

## 15. Yield-Funding Stress (YFS)

**Source:** "The Beacon | It's Getting Spooky" (Oct 30, 2025)

### Formula

```
YFS = weighted_average([
    z_score(10Y_2Y_Spread),
    z_score(10Y_3M_Spread),
    z_score(BGCR_EFFR_Spread)
])
```

### Interpretation
- **High YFS (>+1σ):** Inverted curve + money market stress = Fed tightening/stress
- **Low YFS (<-1σ):** Steep curve + smooth plumbing = Easing conditions

### Current State (January 2026)
- Curve dis-inverted (+32 bps), BGCR-EFFR at +5 bps
- YFS normalized from 2023 peaks but vigilance required

---

## 16. Credit-Labor Gap (CLG)

**Source:** "The Beacon | It's Getting Spooky" (Oct 30, 2025)

### Formula

```
CLG = z_score(HY_OAS) - z_score(LFI)
```

### Interpretation
- **CLG > 0 (Positive):** Credit spreads wide relative to labor stress = Fair pricing
- **CLG ≈ 0:** Credit spreads match labor fundamentals
- **CLG < 0 (Negative):** Spreads too tight given labor deterioration = Pre-widening setup

### Current State (January 2026)
- **CLG: Negative** (spreads too tight)
- HY OAS at 290 bps (3rd percentile) vs LFI at +0.93
- Credit markets underpricing labor fragility by **100-150 bps**

### Investment Signal
- **Negative CLG:** Reduce credit exposure, spreads likely to widen
- Current reading suggests HY spreads should be ~400-450 bps

---

## 17. Spread-Volatility Imbalance (SVI)

**Source:** "The Beacon | It's Getting Spooky" (Oct 30, 2025)

### Formula

```
SVI = z_score(HY_Spread_Level) / z_score(HY_Spread_Volatility)
```

### Current State (January 2026)
- "Tight spreads with rising vol = poor compensation for risk"
- Classic late-cycle mismatch

---

## 18. Repo Rate Dispersion Index

**Source:** "The Beacon | It's Getting Spooky" (Oct 30, 2025)

### Formula

```
Repo_Dispersion = BGCR_99th_Percentile - BGCR_1st_Percentile
```

### Current State (January 2026)
- Rising dispersion + elevated tri-party volume
- "Classic pre-stress configuration" (similar to Sept 2019)

---

# SECTION 5: EQUITY & MARKET POSITIONING

## 19. Equity Momentum Divergence (EMD)

**Source:** "The Beacon | It's Getting Spooky" (Oct 30, 2025)

### Formula

```
EMD = z_score((SP500 - SP500_MA) / Realized_Volatility)
```

### Interpretation
- **EMD > +1σ:** Stretched momentum, thin shock-absorption, prone to air pockets
- **EMD near 0:** Normal momentum conditions
- **EMD < -1σ:** Oversold, potential mean reversion

### Current State (January 2026)
- **Above +1σ** with VIX at 14.2 (vol mispriced)
- High EMD + Negative CLG = Asymmetric downside risk

---

## 20. QUAL/SPY Ratio (Quality vs Risk)

**Source:** "The Beacon | It's Getting Spooky" (Oct 30, 2025)

### Formula

```
QUAL_SPY_Ratio = QUAL_Price / SPY_Price
```

### Current State (January 2026)
- "At or near all-time lows"
- Maximum complacency despite mounting macro fragility

---

# SECTION 6: LIQUIDITY INDICATORS

## 21. Liquidity Transmission Framework

**Source:** "Liquidity Transmission Framework" (Nov 8, 2025)

### Framework Structure
**Stage 1: RRP Depletion** → **Stage 2: Reserve Drainage** → **Stage 3: SRF Usage Surge** → **Stage 4: Collateral Stress** → **Stage 5: Stablecoin Flow Stalls** → **Stage 6: Perp Basis Collapse** → **Stage 7: Crypto Liquidations**

### Current Status (January 2026)
- **Stage 1: Complete** (RRP at $150B, 94% drained)
- **Stage 2: In Progress** (Reserves at $3.3T, QT continuing)
- **Stage 3: Approaching** (SRF at $0, but EFFR drifting up)

---

## 22. Leverage Capacity Matrix

**Source:** "Liquidity Transmission Framework" (Nov 8, 2025)

### State Classification

| System State | RRP Level | Capacity | Constraint Type |
|--------------|-----------|----------|-----------------|
| **Ample** | >$1T | High | None |
| **Adequate** | $500B-$1T | Moderate | Minimal |
| **Scarce** | $50B-$500B | Low | Dealer balance sheets |
| **Crisis** | <$50B | Minimal | Plumbing infrastructure |

### Current State (January 2026)
- **RRP: $150B** → Between Scarce and Crisis
- Leverage constrained by plumbing infrastructure, not policy settings

---

## 23. Liquidity Composite Index

**Source:** "Liquidity Transmission Framework" (Nov 8, 2025)

### Formula

```
Liquidity_Composite = weighted_average([
    RRP_balance,
    T_bill_SOFR_spread,
    OFR_FSI,
    Repo_volumes
])
```

### Key Relationship
- One-for-one correlation between RRP balance and composite
- Validates RRP as primary liquidity barometer

---

# SECTION 7: TREASURY MARKET MICROSTRUCTURE

## 24. Collateral Shortage Index

**Source:** "Collateral Fragility" (Aug 19, 2025)

### Current Level: ~80 (vs historical baseline ~30)
- "Echoing the mechanics that led to the 2019 repo crisis"

---

## 25. Treasury Auction Tailing Metric

**Source:** "Collateral Fragility" (Aug 19, 2025)

### Key Thresholds

| Period | Tail % | Interpretation |
|--------|--------|----------------|
| Historical | 15% | Normal market function |
| **2025-26** | **35%** | Structural demand weakness |

---

## 26. Bid-to-Cover Ratio Analysis

**Source:** "Seemingly Stable, Systemically Stressed" (Sep 15, 2025)

### Formula

```
Bid_to_Cover = Total_Bids_Received / Amount_of_Securities_Offered
```

### Key Thresholds

| Maturity | Strong | Neutral | Weak |
|----------|--------|---------|------|
| T-Bills | >3.0x | 2.5-3.0x | <2.5x |
| 10Y Notes | >2.5x | 2.2-2.5x | **<2.2x** |
| 30Y Bonds | >2.3x | 2.0-2.3x | <2.0x |

---

## 27. Dealer Allotment Percentage

**Source:** "Seemingly Stable, Systemically Stressed" (Sep 15, 2025)

### Formula

```
Dealer_Allotment_% = (Amount_Allocated_to_Primary_Dealers / Total_Auctioned) * 100
```

### Critical Threshold
- **Historical norm:** <20%
- **Stress signal:** **>20%** ("Anything above the dashed 20% line is historically rare")

---

## 28. Dealer Accumulation Momentum

**Source:** "Cracks in the Foundation" (Aug 12, 2025)

### Formula

```
Accumulation_Momentum = Short_Term_Accumulation_Rate / Long_Term_Trend_Rate
```

### Current State
- Dealers at "96% of their regulatory ceiling" (SLR constraint)

---

## 29. Treasury Stress Dashboard (4-Metric System)

**Source:** "Cracks in the Foundation" (Aug 12, 2025)

### Framework

| Metric | Current State | Threshold | Status |
|--------|---------------|-----------|---------|
| **1. Auction Tail Frequency** | 35% | Historical <15% | Red |
| **2. Foreign Demand** | 63.8% | Historical ~70% | Red |
| **3. Dealer Capacity** | 96% | <85% comfortable | Red |
| **4. Funding Stress** | 30% | <40% manageable | Green |

**3 of 4 metrics flashing red** = Structural weakness

---

## 30. Bill-Bond Divergence Analysis

**Source:** "Cracks in the Foundation" (Aug 12, 2025)

### Key Observations

| Maturity | Bid-to-Cover | Demand Driver |
|----------|--------------|---------------|
| **T-Bills** | 3.4x | Technical (stablecoins) |
| **10Y Notes** | 2.32x | Fundamental (real money) |

Strong bills + Weak bonds = "Technical versus fundamental" demand split

---

## 31. Treasury Composition Shift Index

**Source:** "Cracks in the Foundation" (Aug 12, 2025)

### Historical vs Current Allocation

| Buyer Class | 2020 | Current |
|-------------|------|---------|
| **Foreign CBs** | 45% | **28%** |
| **Domestic Banks** | 20% | **35%** |
| **Primary Dealers** | 15% | **25%** |

"Buyer-Mix Transformation" = Quality deterioration of Treasury demand base

---

# SECTION 8: STABLECOIN & CRYPTO INTEGRATION

## 32. Stablecoin Treasury Holdings Percentage

**Source:** "Cracks in the Foundation" (Aug 19, 2025)

### Formula

```
Stablecoin_Holdings_% = (Stablecoin_Treasury_Holdings / Total_Treasury_Bills_Outstanding) * 100
```

### Key Levels (2026)
- **Global T-bill demand:** 3.0%
- **Market composition:** 6% (stablecoin issuers as buyer segment)
- High concentration = vulnerability to redemption shocks

---

## 33. Stablecoin Supply Correlation with T-Bill Richness

**Source:** "Collateral Fragility" (Aug 19, 2025)

### Relationship
- Rising stablecoin supply → Tighter 3M Bill-SOFR spreads (bills trade "rich")
- Creates feedback loop: More crypto inflows → More T-bill demand → Lower yields

---

## 34. 3M Bill-SOFR Spread

**Source:** "Collateral Fragility" (Aug 19, 2025)

### Formula

```
Bill_SOFR_Spread = 3M_T_Bill_Rate - SOFR
```

### Interpretation
- **Positive spread:** Bills trading rich (high demand)
- **Negative spread:** Bills trading cheap (supply pressure)

---

## 35. Stablecoin Liquidity Impulse (SLI)

**Source:** CLAUDE.md Proprietary Indicator Codex

### Formula

```
SLI = Rate_of_Change(Stablecoin_Market_Cap, 30d)
```

### Interpretation
- **SLI > 0:** On-chain liquidity expanding, T-bill demand increasing
- **SLI < 0:** Liquidity contracting, potential T-bill supply pressure
- Proxy for on-chain liquidity and T-bill absorption capacity

---

# SECTION 9: ADVANCED TRADING FRAMEWORKS

## 36. Z-Score Positioning Index (Basis Trades)

**Source:** "The Beam | Treasury Buybacks & The Mechanical Basis Squeeze" (Oct 10, 2025)

### Formula

```
Z_Score = (Current_Basis - Mean_Basis) / StdDev_Basis
```

Applied separately to maturity buckets: 7-10Y, 10-20Y, 20-30Y

### Key Thresholds

| Maturity | Z-Score | Positioning Signal |
|----------|---------|-------------------|
| 7-10Y | **-1.22σ** | Oversold → Long candidate |
| 10-20Y | **+0.97σ** | Approaching compression trigger |
| 20-30Y | +0.90σ | Elevated conditions |

---

## 37. Compression Function Model

**Source:** "The Beam | Treasury Buybacks & The Mechanical Basis Squeeze" (Oct 10, 2025)

### Formula

```
C(t) = -α * exp(-((t-t₀)/β)²) * H(t₀-t)
       + -γ * exp(-t/τ) * H(t-t₀)
```

### Parameter Calibration by Maturity

| Bucket | α | β | γ | τ | R² |
|--------|---|---|---|---|-----|
| 7-10Y | 0.5 | 2.0 | 3.0 | 2.0 | >0.85 |
| 10-20Y | 0.4 | 2.5 | 2.5 | 3.0 | >0.85 |
| 20-30Y | 0.3 | 3.0 | 2.8 | 4.0 | >0.85 |

---

## 38. Recovery Half-Life Metric

**Source:** "The Beam | Treasury Buybacks & The Mechanical Basis Squeeze" (Oct 10, 2025)

### Formula

```
Recovery_Half_Life = ln(2) / τ
```

### Observed Half-Lives

| Maturity | τ (days) | Half-Life |
|----------|----------|-----------|
| 7-10Y | 2.0 | ~1.4 days |
| 10-20Y | 3.0 | ~2.1 days |
| 20-30Y | 4.0 | ~2.8 days |

---

## 39. Market-Neutral Basis Sharpe Ratio

**Source:** "The Beam | Treasury Buybacks & The Mechanical Basis Squeeze" (Oct 10, 2025)

### Value
**Sharpe Ratio: 1.84**

### Sample Statistics (180-day trailing)
- Mean compression: -2.77 basis points
- Standard deviation: 0.38 basis points
- Win rate: 68%
- Sample size: 27 operations

---

# APPENDIX: MASTER FORMULA SHEET

## Quick Reference - All Pillar Composites

```python
# MASTER COMPOSITE (v2.0 - 12 Pillars)
MRI = 0.12×(-LPI) + 0.08×PCI + 0.12×(-GCI) + 0.06×(-HCI) + 0.08×(-CCI)
    + 0.08×(-BCI) + 0.05×(-TCI) + 0.10×GCI-Gov + 0.05×(-FCI) + 0.10×(-LCI)
    + 0.08×(-MSI) + 0.08×SPI

# PILLAR 1: LABOR
LPI = 0.20×z(Quits) + 0.15×z(Hires/Quits) + 0.15×z(-LongTermUnemp)
    + 0.15×z(-Claims) + 0.10×z(LFPR) + 0.10×z(Hours)
    + 0.10×z(-TempHelp) + 0.05×z(JobHopperPrem)

LFI = 0.35×z(LongUnemployment%) + 0.35×z(-Quits) + 0.30×z(-Hires/Quits)

# PILLAR 2: PRICES
PCI = 0.30×z(CorePCE_3M) + 0.20×z(ServicesExShelter) + 0.15×z(Shelter)
    + 0.15×z(StickyCPI) + 0.10×z(5Y5Y) + 0.10×z(-GoodsCPI)

# PILLAR 3: GROWTH
GCI = 0.25×z(IP_YoY) + 0.20×z(ISM_Mfg) + 0.15×z(Capex_YoY)
    + 0.15×z(AggHours_YoY) + 0.10×z(RealRetail_YoY)
    + 0.10×z(Starts_YoY) + 0.05×z(-GDI_GDP_Spread)

# PILLAR 4: HOUSING
HCI = 0.20×z(Starts_YoY) + 0.15×z(ExistingSales_YoY) + 0.15×z(NAHB)
    + 0.15×z(-MonthsSupply) + 0.10×z(HPI_YoY) + 0.10×z(-MortgageRate)
    + 0.10×z(MBA_Purchase_YoY) + 0.05×z(-Delinquency)

# PILLAR 5: CONSUMER
CCI = 0.25×z(RealPCE_YoY) + 0.20×z(SavingRate) + 0.15×z(-CC_Delinquency)
    + 0.15×z(CB_Expectations) + 0.10×z(RealDPI_YoY)
    + 0.10×z(-DebtServiceRatio) + 0.05×z(CardSpending_YoY)

# PILLAR 6: BUSINESS
BCI = 0.20×z(NFIB) + 0.20×z(Capex_YoY) + 0.15×z(ISM_Mfg)
    + 0.15×z(ISM_Svc) + 0.10×z(-I_S_Ratio) + 0.10×z(SP500_EPS_YoY)
    + 0.05×z(-SLOOS) + 0.05×z(-HY_OAS)

# PILLAR 7: TRADE
TCI = 0.20×z(-ImportPrice_YoY) + 0.20×z(-TradeBalance_GDP)
    + 0.15×z(ExportVol_YoY) + 0.15×z(-GSCPI) + 0.10×z(Container_YoY)
    + 0.10×z(-DXY_YoY) + 0.10×z(-TradePolicyUncertainty)

# PILLAR 8: GOVERNMENT
GCI-Gov = 0.25×z(Deficit_GDP) + 0.20×z(Interest_Outlays)
        + 0.15×z(Debt_GDP) + 0.15×z(TermPremium)
        + 0.10×z(Issuance) + 0.10×z(-Receipts_YoY)
        + 0.05×z(-ForeignHoldings)

# PILLAR 9: FINANCIAL
FCI = 0.20×z(-HY_OAS) + 0.15×z(-NFCI) + 0.15×z(Curve_10Y2Y)
    + 0.15×z(-RealFedFunds) + 0.10×z(C&I_Growth) + 0.10×z(-VIX)
    + 0.10×z(LCI) + 0.05×z(-SLOOS)

# PILLAR 10: PLUMBING
LCI = 0.25×z(Reserves_vs_LCLOR) + 0.20×z(-EFFR_IORB)
    + 0.15×z(-SOFR_IORB) + 0.15×z(RRP) + 0.10×z(-GCF_TPR)
    + 0.10×z(-DealerPosition) + 0.05×z(-EUR_USD_Basis)

# PILLAR 11: MARKET STRUCTURE (NEW in v2.0)
MSI = 0.15×z(Price_vs_200d) + 0.10×z(Price_vs_50d) + 0.10×z(50d_Slope)
    + 0.10×z(20d_Slope) + 0.12×z(Z_RoC_63d) + 0.10×z(%>50d)
    + 0.08×z(%>20d) + 0.08×z(%>200d) + 0.07×z(NetHighsLows)
    + 0.05×z(AD_Slope) + 0.05×z(McClellan)

# PILLAR 12: SENTIMENT (NEW in v2.0)
SPI = 0.20×z(AAII) + 0.15×z(-PutCall) + 0.15×z(VIX_RealVol)
    + 0.15×z(FundFlows) + 0.15×z(FearGreed) + 0.10×z(NAAIM)
    + 0.10×z(Skew)

SSD = SPI - MSI  # Sentiment-Structure Divergence

# LEGACY INDICATORS
LDI = (z(Quits) + z(Hires/Quits) + z(Quits/Layoffs)) / 3
YFS = (z(10Y-2Y) + z(10Y-3M) + z(BGCR-EFFR)) / 3
CLG = z(HY_OAS) - z(LFI)
SVI = z(HY_OAS_Level) / z(HY_OAS_Volatility)
EMD = z((SP500 - MA(SP500)) / Realized_Vol)
```

---

# CURRENT STATE SUMMARY (January 2026)

| **Index** | **Current** | **Regime** | **Key Driver** |
|-----------|-------------|------------|----------------|
| **MRI** | +1.1 | HIGH RISK | Labor + Fiscal + Liquidity |
| **LPI** | -0.2 | Neutral/Weakening | Quits declining |
| **PCI** | +0.7 | Elevated (Last Mile) | Services sticky |
| **GCI** | -0.4 | Below Trend | Manufacturing recession |
| **HCI** | -0.6 | Weak (Frozen) | Rate-constrained |
| **CCI** | -0.3 | Fatigued | Savings depleted |
| **BCI** | -0.4 | Slowing | Small biz collapsing |
| **TCI** | -0.5 | Headwind | Tariff pass-through |
| **GCI-Gov** | +1.1 | High Stress | Fiscal Dominance |
| **FCI** | +0.3 | Neutral (Divergent) | Spreads mispriced |
| **LCI** | -0.8 | Scarce | Buffer exhausted |
| **MSI** | [Live] | [Live] | Monitor breadth divergence |
| **SPI** | [Live] | [Live] | Monitor crowding extremes |
| **LFI** | +0.93 | Elevated | Structural fragility |
| **CLG** | Negative | Mispriced | Spreads 100-150 bps too tight |

---

# DATA SOURCE SUMMARY

| Indicator | Primary Data Source | Frequency | FRED Series ID |
|-----------|---------------------|-----------|----------------|
| **RRP** | NY Fed / FRED | Daily | RRPONTSYD |
| **Bank Reserves** | FRED | Weekly | WRBWFRBL |
| **JOLTS** | BLS / FRED | Monthly | JTSJOL, JTSHIL, JTSQUL |
| **HY OAS** | FRED (BofA) | Daily | BAMLH0A0HYM2 |
| **NFCI** | Chicago Fed | Weekly | NFCI |
| **ISM** | ISM | Monthly | Web scrape |
| **NFIB** | NFIB | Monthly | Web scrape |
| **Treasury Yields** | FRED | Daily | DGS2, DGS10, DGS30 |
| **SOFR/EFFR** | NY Fed | Daily | SOFR, EFFR |
| **Term Premium** | NY Fed | Daily | NY Fed ACM model |

---

**End of Proprietary Indicators Reference**

**Compiled by:** Lighthouse Macro
**For:** Bob Sheehan, CFA, CMT
**Date:** January 19, 2026
**Version:** 2.0 (The Diagnostic Dozen - 12 Pillars)

**All formulas, methodologies, and frameworks are proprietary to Lighthouse Macro and Bob Sheehan unless otherwise noted.**

*41 proprietary indicators spanning macro dynamics, monetary mechanics, and market structure.*
