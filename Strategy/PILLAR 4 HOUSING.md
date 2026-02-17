# PILLAR 4: HOUSING

## The Housing Transmission Chain

Housing isn't shelter. It's the financial system's collateral backbone. The transmission mechanism operates through cascading wealth effects and credit amplification:

```
Mortgage Rates → Affordability → Purchase Demand →
Home Prices → Household Wealth → Consumer Spending →
Collateral Values → Credit Availability →
Mortgage Rates (Reinforcing Loop)
```

**The Insight:** Housing is a leveraged bet on rates and demographics. When mortgage rates spike 400 bps in 18 months (2022-2023), transaction volumes collapse. But prices don't fall proportionally because locked-in sellers refuse to list, creating the "golden handcuffs" phenomenon. The market freezes, not crashes.

The beauty of housing data: it leads the broader economy by 6-12 months. Housing peaked in April 2022. The rest of the economy is still catching up. When housing thaws, recovery begins. Until then, we're in stasis.

---

## Why Housing Matters: The Wealth Effect Multiplier

Housing is 15-20% of GDP directly (residential investment + imputed rent). But its true impact is 2-3x larger through:
- **Wealth effect:** $1 of home equity → $0.05-0.08 of additional consumer spending
- **Employment:** Construction, real estate, mortgage finance = 6% of employment
- **Collateral:** Home equity is 70% of median household net worth
- **Credit transmission:** Mortgage delinquencies → bank stress → credit tightening

**The Cascade:**

**1. Housing → Consumer:** Wealth effect drives spending (3-6 month lag)
**2. Housing → Employment:** Construction jobs lead payrolls (2-4 month lag)
**3. Housing → Banking:** Mortgage health determines credit availability (6-12 month lag)
**4. Housing → Inflation:** Shelter is 34% of CPI, 18% of Core PCE (12-18 month lag)
**5. Housing → Fed Policy:** Rate sensitivity makes housing the Fed's primary transmission channel

Get the housing call right, and you've triangulated the consumer, construction, and collateral outlook. Miss it, and you're trading the economy of 2023 while living in 2026.

---

## Primary Indicators: The Complete Architecture

### A. HOUSING CONSTRUCTION (The Leading Edge)

New construction is the most leading housing indicator. Permits lead starts, starts lead completions, completions lead GDP residential investment.

| **Indicator** | **FRED Code** | **Frequency** | **Lead/Lag** | **Interpretation** |
|---|---|---|---|---|
| **Building Permits** | PERMIT | Monthly | **Leads starts 1-2 mo** | Future construction pipeline |
| **Building Permits: Single-Family** | PERMIT1 | Monthly | Leads multi-family 1-2 mo | Core housing demand signal |
| **Building Permits: Multi-Family** | Derived (PERMIT - PERMIT1) | Monthly | Coincident | Rental market demand |
| **Housing Starts** | HOUST | Monthly | **Leads GDP 6-9 mo** | New construction begins |
| **Housing Starts: Single-Family** | HOUST1F | Monthly | Leads GDP 6-9 mo | Owner-occupied construction |
| **Housing Starts: Multi-Family** | Derived (HOUST - HOUST1F) | Monthly | Coincident | Rental construction |
| **Housing Completions** | COMPUTSA | Monthly | Lagging 4-6 mo | Finished units (inventory addition) |
| **Under Construction** | UNDCONTSA | Monthly | Coincident | Work in progress (employment proxy) |
| **Manufactured Housing Shipments** | MHI/MHARR Reports | Monthly | Coincident | Alt-supply: ~9-10% of new SF supply |
| **ADU Permits** | Census (emerging) | Annual/Quarterly | Coincident | Supplemental supply, growing fast |

#### Regional Construction Breakdowns

Construction activity is tracked across four Census regions. Regional divergences often lead national turns.

| **Region** | **FRED Permits** | **FRED Starts** | **Share of National** |
|---|---|---|---|
| **Northeast** | PERMITNSA (NE component) | HOUSTNE | ~10-12% |
| **Midwest** | PERMITNSA (MW component) | HOUSTMW | ~12-15% |
| **South** | PERMITNSA (S component) | HOUSTS | ~50-55% |
| **West** | PERMITNSA (W component) | HOUSTW | ~22-28% |

**Why Regional Matters:** The South accounts for over half of all construction. When Southern permits roll over, it drags national figures even if other regions hold. During the 2022-2024 correction, the South's oversupply (particularly in TX, FL, AZ) masked relative resilience in the Northeast and Midwest.

#### Derived Construction Metrics

| **Metric** | **Formula** | **Threshold** | **Signal** |
|---|---|---|---|
| **Permits-Starts Gap** | (Permits - Starts) / Starts × 100 | >+10% | Pipeline building; <-10% = draining |
| **SF/MF Ratio (Permits)** | SF Permits / MF Permits | <1.5 | Shift to rentals (affordability stress) |
| **Construction Pipeline** | Under Construction / Monthly Completions | >6 months | Supply glut risk |
| **Starts Momentum** | 3M Avg Starts - 12M Avg Starts | <-100k | Deterioration |
| **Starts vs Population Growth** | Starts SAAR / Annual Population Growth | <1.0x | Undersupply accumulating |
| **Completion Rate** | Completions / (Under Construction) | <0.10 | Construction bottleneck |
| **MF Pipeline Drag** | MF Under Construction / MF Starts (trailing 12m) | >2.0x | MF glut forming |
| **Regional Concentration** | South Permits / Total Permits | >0.60 | Overconcentration risk |

#### Regime Thresholds: Construction

| **Indicator** | **Recession** | **Stagnation** | **Expansion** | **Boom** |
|---|---|---|---|---|
| **Housing Starts** | <1.0M | 1.0-1.3M | 1.3-1.6M | >1.6M |
| **SF Starts** | <0.6M | 0.6-0.8M | 0.8-1.0M | >1.0M |
| **MF Starts** | <0.2M | 0.2-0.35M | 0.35-0.5M | >0.5M |
| **Building Permits YoY%** | <-15% | -15% to +5% | +5% to +15% | >+15% |
| **Starts YoY%** | <-10% | -10% to +5% | +5% to +15% | >+15% |
| **Completions YoY%** | <-10% | -10% to 0% | 0% to +10% | >+10% |
| **Under Construction** | <1.0M | 1.0-1.3M | 1.3-1.6M | >1.6M |
| **Manufactured Shipments YoY%** | <-15% | -15% to 0% | 0% to +10% | >+10% |

---

### B. HOME SALES (The Transaction Signal)

Sales volumes tell you about market liquidity and turnover. In frozen markets, both buyers and sellers retreat. Transactions collapse even as prices hold.

| **Indicator** | **FRED Code** | **Frequency** | **Lead/Lag** | **Interpretation** |
|---|---|---|---|---|
| **New Home Sales** | HSN1F | Monthly | **Leads starts 1-3 mo** | Builder sales (forward-looking) |
| **Existing Home Sales** | EXHOSLUSM495S | Monthly | Coincident | Resale market (backward-looking) |
| **Pending Home Sales Index** | NAR (web) | Monthly | **Leads existing 1-2 mo** | Contracts signed, not closed |
| **MBA Purchase Index** | MBA (web) | Weekly | **Leads sales 4-8 wks** | Mortgage applications for purchase |
| **Months' Supply: New Homes** | MSACSR | Monthly | Coincident | Inventory/sales ratio (new) |
| **Months' Supply: Existing Homes** | Derived | Monthly | Coincident | Inventory/sales ratio (resale) |
| **Median Days on Market** | NAR | Monthly | Coincident | Market velocity |
| **Redfin Days on Market** | Redfin | Weekly | **Leads NAR 2-4 wks** | Real-time market velocity |

#### Buyer Composition Indicators

These metrics track who is buying. Shifts in composition signal structural market changes.

| **Indicator** | **Source** | **Frequency** | **Interpretation** |
|---|---|---|---|
| **First-Time Buyer Share** | NAR Profile of Home Buyers | Monthly/Annual | Demand health; <30% = affordability crisis |
| **Cash Buyer Share** | NAR / Redfin | Monthly | Liquidity signal; >30% = institutional/wealthy dominance |
| **Investor Share** | NAR / Redfin | Monthly | Speculation gauge; >20% = overheated |
| **Distressed Sale Share** | NAR / RealtyTrac | Monthly | Credit stress; >5% = emerging problems |
| **Foreign Buyer Activity** | NAR International Report | Annual | Capital flow signal |
| **iBuyer Market Share** | Redfin / Opendoor filings | Quarterly | Algorithmic liquidity provision |
| **Contract Cancellation Rate** | Redfin / Builder surveys | Monthly | Demand fragility signal |

#### Derived Sales Metrics

| **Metric** | **Formula** | **Threshold** | **Signal** |
|---|---|---|---|
| **New/Existing Ratio** | New Sales / Existing Sales | >0.20 | Builders capturing locked-in market share |
| **Sales Momentum** | 3M Sales - 12M Avg Sales | <-10% | Deterioration |
| **Transaction Volume ($$)** | Sales × Median Price | YoY < 0% | Market shrinking |
| **MBA Purchase YoY%** | Current - Year Ago | <-10% | Demand weakening |
| **Days on Market Trend** | Current DOM - 6M Avg DOM | >+10 days | Market slowing |
| **Cash-to-Finance Ratio** | Cash Sales / Financed Sales | >0.40 | Rate sensitivity maxed out |
| **Cancellation Spread** | Builder Cancel Rate - Historical Avg (~12%) | >+5 ppts | Demand fragility |
| **First-Time vs Repeat Gap** | FTB Share - Historical Avg (33%) | <-5 ppts | Affordability excluding entry buyers |

#### Regime Thresholds: Sales

| **Indicator** | **Frozen** | **Weak** | **Normal** | **Hot** |
|---|---|---|---|---|
| **Existing Home Sales (SAAR)** | <3.5M | 3.5-4.5M | 4.5-5.5M | >5.5M |
| **New Home Sales (SAAR)** | <550k | 550-650k | 650-750k | >750k |
| **Pending Home Sales Index** | <65 | 65-85 | 85-110 | >110 |
| **Months' Supply (Existing)** | >6.0 | 4.0-6.0 | 2.5-4.0 | <2.5 |
| **Median Days on Market** | >60 | 40-60 | 20-40 | <20 |
| **First-Time Buyer Share** | <25% | 25-30% | 30-38% | >38% |
| **Cash Buyer Share** | >35% | 28-35% | 20-28% | <20% |
| **Investor Share** | >25% | 18-25% | 12-18% | <12% |
| **Distressed Sale Share** | >8% | 4-8% | 1-4% | <1% |

---

### C. HOME PRICES (The Wealth Effect Anchor)

Home prices are the lagging confirmation of what sales already told you. But they matter enormously for household wealth ($17+ trillion in home equity at peak).

| **Indicator** | **Source** | **Frequency** | **Lead/Lag** | **Interpretation** |
|---|---|---|---|---|
| **Case-Shiller National HPI** | S&P/Cotality | Monthly | **Lags sales 3-6 mo** | Gold standard, repeat-sales methodology |
| **Case-Shiller 20-City Composite** | S&P/Cotality | Monthly | Lags 3-6 mo | Major metro composite |
| **Case-Shiller 10-City Composite** | S&P/Cotality | Monthly | Lags 3-6 mo | Concentrated metro sample |
| **FHFA House Price Index** | FHFA | Monthly | Lags 3-6 mo | Conforming loans only, broader coverage |
| **FHFA Quarterly (by state)** | FHFA | Quarterly | Lags 3-6 mo | State-level price dynamics |
| **Zillow Home Value Index (ZHVI)** | Zillow | Monthly | **Leads Case-Shiller 1-2 mo** | Real-time estimate (all homes) |
| **Redfin Median Sale Price** | Redfin | Weekly | **Leads Case-Shiller 2-3 mo** | Transaction-based, real-time |
| **Median Existing Home Price** | NAR | Monthly | Coincident | Reported with sales data |
| **Median New Home Price** | Census | Monthly | Coincident | Reported with new sales |
| **Altos Research Market Action Index** | Altos (HousingWire) | Weekly | **Leading 4-8 wks** | Real-time price pressure signal |

#### Price Tier & Segment Analysis

| **Indicator** | **Source** | **Frequency** | **Interpretation** |
|---|---|---|---|
| **Case-Shiller Price Tiers (Low/Mid/High)** | S&P/Cotality | Monthly | Tier divergence = affordability stress |
| **Redfin Luxury vs Non-Luxury** | Redfin | Monthly | Top 5% vs middle segment divergence |
| **FHFA by Census Division** | FHFA | Quarterly | 9 divisions, granular geography |
| **FHFA by State** | FHFA | Quarterly | State-level winners/losers |
| **Zillow by Metro** | Zillow | Monthly | City-level, most granular real-time |
| **New Home Price by Size** | Census | Monthly | Builder mix-shift detection |
| **Price Per Square Foot** | Redfin/Zillow | Monthly | Quality-adjusted measure |

#### Derived Price Metrics

| **Metric** | **Formula** | **Threshold** | **Signal** |
|---|---|---|---|
| **HPI YoY%** | Current - Year Ago | <0% | Declining (wealth destruction) |
| **Real HPI YoY%** | Nominal HPI YoY - CPI YoY | <-3% | Real depreciation (affordability improving) |
| **Price-Income Ratio** | Median Price / Median Income | >5.5x | Severely unaffordable |
| **Price Momentum** | 3M Ann - 12M Ann | <-5 ppts | Deceleration |
| **CS-Zillow Lead Signal** | Zillow MoM (2M Prior) vs CS MoM | Directional divergence | Early turn detection |
| **Luxury-Entry Spread** | Redfin Luxury YoY - Non-Luxury YoY | >+3 ppts | K-shaped market |
| **New vs Existing Price Gap** | Median New / Median Existing | <1.0x | Builder desperation (cutting below resale) |
| **Regional Dispersion** | Max CS-20 City YoY - Min CS-20 City YoY | >8 ppts | Geographic divergence elevated |
| **Price-to-Rent Ratio** | Median Price / (Median Rent × 12) | >20x | Ownership overvalued vs renting |

#### Regime Thresholds: Prices

| **Indicator** | **Deflation** | **Stable** | **Appreciation** | **Bubble** |
|---|---|---|---|---|
| **Case-Shiller YoY%** | <0% | 0-3% | 3-8% | >8% |
| **FHFA HPI YoY%** | <0% | 0-4% | 4-10% | >10% |
| **Real HPI YoY%** | <-2% | -2% to +2% | +2% to +5% | >+5% |
| **Price-Income Ratio** | <3.5x | 3.5-4.5x | 4.5-5.5x | >5.5x |
| **Zillow ZHVI YoY%** | <0% | 0-3% | 3-7% | >7% |
| **Regional Dispersion** | <3 ppts | 3-6 ppts | 6-10 ppts | >10 ppts |

---

### D. AFFORDABILITY & RATES (The Binding Constraint)

Affordability determines marginal demand. When mortgage rates double, monthly payments spike 40%. The buyer pool shrinks. Transactions freeze.

| **Indicator** | **FRED Code** | **Frequency** | **Lead/Lag** | **Interpretation** |
|---|---|---|---|---|
| **30Y Fixed Mortgage Rate** | MORTGAGE30US | Weekly | Coincident | Primary rate benchmark |
| **15Y Fixed Mortgage Rate** | MORTGAGE15US | Weekly | Coincident | Refinance benchmark |
| **5/1 ARM Rate** | Freddie Mac (web) | Weekly | Coincident | ARM demand gauge |
| **10Y Treasury Yield** | DGS10 | Daily | **Leads mortgages 0-1 wk** | Rate floor |
| **Mortgage Spread (30Y - 10Y)** | Derived | Daily | Coincident | MBS credit/prepay risk |
| **Housing Affordability Index** | NAR | Monthly | Lagging 1 mo | 100 = median income qualifies for median home |
| **NAHB Affordability Index** | NAHB | Quarterly | Lagging 1 qtr | Builder-calculated metric |
| **Payment-to-Income Ratio** | Derived | Monthly | Coincident | Monthly mortgage payment / monthly income |
| **ARM Share of Originations** | MBA | Weekly | Coincident | Rate sensitivity gauge; >10% = stretched |
| **FHA/VA Share of Purchase Apps** | MBA | Monthly | Coincident | Low-down-payment demand proxy |
| **Mortgage Banker Rate Forecast** | MBA | Quarterly | Forward-looking | Industry consensus rate path |

#### Derived Affordability Metrics

| **Metric** | **Formula** | **Threshold** | **Signal** |
|---|---|---|---|
| **Mortgage Rate YoY Change** | Current Rate - Year Ago | >+100 bps | Demand destruction |
| **Mortgage-Treasury Spread** | 30Y Mortgage - 10Y Treasury | >250 bps | Credit stress elevated |
| **Spread vs Historical Norm** | Current Spread - 170 bps (long-run avg) | >+60 bps | MBS market impaired |
| **Affordability Gap** | Current Affordability - Historical Avg (100) | <-20 | Severely unaffordable |
| **Payment Shock** | Monthly Pmt (Current Rate) - Pmt (3% Rate) | >$800/month | Demand frozen |
| **Rate Lock-In Severity** | % Mortgages with Rate < Current - 200 bps | >70% | Extreme lock-in effect |
| **Income Required for Median Home** | Annual Income to Qualify (28% DTI) | >$100k | Excluding median households |
| **Buy vs Rent Gap** | Monthly Mortgage Pmt - Monthly Median Rent | >$800 | Strong rent preference |
| **Refi Incentive Share** | % Mortgages with Rate > Current + 50 bps | >30% | Refi wave catalyst |
| **ARM Penetration Trend** | Current ARM Share - 12M Avg | >+3 ppts | Borrowers reaching for affordability |

#### Regime Thresholds: Affordability

| **Indicator** | **Frozen** | **Stretched** | **Normal** | **Easy** |
|---|---|---|---|---|
| **30Y Mortgage Rate** | >7.5% | 6.5-7.5% | 5.0-6.5% | <5.0% |
| **Affordability Index** | <85 | 85-100 | 100-120 | >120 |
| **Payment-to-Income** | >35% | 28-35% | 22-28% | <22% |
| **Mortgage Spread** | >300 bps | 200-300 bps | 150-200 bps | <150 bps |
| **ARM Share** | >15% | 10-15% | 5-10% | <5% |
| **Income Required** | >$120k | $100-120k | $75-100k | <$75k |
| **Buy vs Rent Gap** | >$1,200/mo | $800-1,200 | $400-800 | <$400 |

**The Rate Sensitivity Rule of Thumb:** Every 100 bps in mortgage rates = ~10% change in affordability = ~5-10% change in sales volumes. Every 50 bps lower unlocks a new cohort of locked-in sellers willing to transact.

---

### E. INVENTORY & SUPPLY (The Scarcity Signal)

Inventory determines whether prices rise or fall. Low inventory = seller's market = prices up. High inventory = buyer's market = prices down.

| **Indicator** | **Source** | **Frequency** | **Lead/Lag** | **Interpretation** |
|---|---|---|---|---|
| **Existing Home Inventory** | NAR | Monthly | Coincident | Active listings (resale) |
| **New Home Inventory** | Census | Monthly | Coincident | Builder inventory (new) |
| **Months' Supply (Existing)** | NAR | Monthly | **Leads prices 3-6 mo** | Inventory/sales ratio |
| **Months' Supply (New)** | Census | Monthly | Leads prices 3-6 mo | Builder inventory/sales |
| **Active Listings (Realtor.com)** | Realtor.com | Weekly | **Leads NAR 2-4 wks** | Real-time inventory |
| **New Listings** | Redfin/Realtor.com | Weekly | Leading 2-4 wks | Fresh supply hitting market |
| **Altos Active Inventory** | HousingWire/Altos | Weekly | **Leading 2-4 wks** | Highest frequency inventory data |
| **Price Reductions Share** | Redfin/Realtor.com | Weekly | Coincident | Seller desperation gauge |
| **Housing Starts Backlog** | Derived | Monthly | Lagging | Under construction - completions |

#### Structural Supply Metrics

| **Indicator** | **Source** | **Frequency** | **Interpretation** |
|---|---|---|---|
| **Structural Housing Deficit** | Freddie Mac/NAR/NAHB | Annual | Gap between units needed and units built |
| **Vacancy Rate: Homeowner** | Census (H&V) | Quarterly | Ownership market slack |
| **Vacancy Rate: Rental** | Census (H&V) | Quarterly | Rental market slack |
| **Housing Stock Growth** | Census | Annual | Net new units added |
| **Household Formation Rate** | Census (CPS) | Annual | Demand driver for new units |
| **Demolitions/Removals** | Census/HUD | Annual | Units leaving inventory |
| **Second Home Share** | Census (ACS) | Annual | Non-primary demand for units |

#### Derived Supply Metrics

| **Metric** | **Formula** | **Threshold** | **Signal** |
|---|---|---|---|
| **Inventory Gap vs 2019** | Current - 2019 Level | <-40% | Structural undersupply |
| **Inventory Gap vs Pre-Pandemic Norm** | Current - 2017-2019 Avg | <-20% | Below normal |
| **Months Supply Change** | Current - 6M Ago | >+1.0 mo | Supply building (bearish prices) |
| **New Listings YoY%** | Current - Year Ago | <-10% | Sellers on strike |
| **Construction/Household Formation** | Starts / Annual HH Formation | <1.0x | Undersupply accumulating |
| **Price Reductions Trend** | Current % - 12M Avg % | >+5 ppts | Seller capitulation building |
| **Existing/New Inventory Split** | Existing Inv / (Existing + New Inv) | <0.65 | Resale market dysfunctional |
| **Homeowner Vacancy Trend** | Current Rate - 4Q Avg | >+0.3 ppts | Owners vacating (stress) |

#### Regime Thresholds: Inventory

| **Indicator** | **Undersupplied** | **Balanced** | **Oversupplied** |
|---|---|---|---|
| **Months' Supply (Existing)** | <3.0 | 3.0-5.0 | >5.0 |
| **Months' Supply (New)** | <5.0 | 5.0-7.0 | >7.0 |
| **Existing Inventory Level** | <1.5M | 1.5-2.5M | >2.5M |
| **Active Listings YoY%** | <-10% | -10% to +10% | >+10% |
| **Inventory vs 2019 (%)** | <-30% | -30% to 0% | >0% |
| **Price Reductions Share** | <12% | 12-18% | >18% |
| **Homeowner Vacancy Rate** | <1.0% | 1.0-1.5% | >1.5% |
| **Structural Deficit (units)** | >3M | 1.5-3M | <1.5M |

---

### F. BUILDER SENTIMENT & ACTIVITY (The Forward Bet)

Builders are the smart money in housing. They commit capital 12-18 months ahead of sales. Their sentiment and actions are highly predictive.

| **Indicator** | **Source** | **Frequency** | **Lead/Lag** | **Interpretation** |
|---|---|---|---|---|
| **NAHB Home Builder Confidence** | NAHB | Monthly | **Leads starts 1-3 mo** | Traffic, sales expectations |
| **NAHB: Current Sales** | NAHB | Monthly | Coincident | Present conditions |
| **NAHB: Future Sales** | NAHB | Monthly | **Leads starts 2-4 mo** | 6-month outlook |
| **NAHB: Traffic of Prospective Buyers** | NAHB | Monthly | **Leads sales 1-2 mo** | Foot traffic proxy |
| **NAHB by Region** | NAHB | Monthly | Coincident | Regional builder confidence |
| **Builder Price Cuts (% of builders)** | NAHB | Monthly | Coincident | Desperation gauge |
| **Builders Offering Incentives (%)** | NAHB | Monthly | Coincident | Incentive intensity |
| **Average Incentive Value** | Builder surveys / earnings | Quarterly | Coincident | Cost of sustaining volume |

#### Public Homebuilder Operating Metrics

Public homebuilder earnings provide the highest-quality, forward-looking housing data available. These companies collectively represent ~40% of new home sales.

| **Metric** | **Builders** | **Frequency** | **Interpretation** |
|---|---|---|---|
| **Net New Orders** | DHI, LEN, PHM, TOL, KBH, NVR, TMHC, MTH, MDC, MHO | Quarterly | Forward demand signal |
| **Order Cancellation Rate** | All publics | Quarterly | Demand fragility; >15% = stress |
| **Backlog (units & $$)** | All publics | Quarterly | Revenue pipeline; declining = weakening |
| **Average Selling Price (ASP)** | All publics | Quarterly | Mix-shift and pricing power |
| **Gross Margin** | All publics | Quarterly | Incentive cost absorption |
| **Incentives as % of Revenue** | LEN, DHI, PHM | Quarterly | Cost of sustaining volume |
| **Community Count Growth** | All publics | Quarterly | Forward capacity investment |
| **Lots Owned/Controlled** | All publics | Quarterly | Land pipeline for future starts |
| **Spec Home Inventory** | DHI, LEN | Quarterly | Unsold completed homes; rising = demand miss |

**Key Builder Earnings Calendar:**
- D.R. Horton (DHI): Jan, Apr, Jul, Oct (fiscal Q ends Dec, Mar, Jun, Sep)
- Lennar (LEN): Jan, Mar, Jun, Sep (fiscal Q ends Nov, Feb, May, Aug)
- PulteGroup (PHM): Jan, Apr, Jul, Oct
- Toll Brothers (TOL): Dec, Mar, Jun, Sep (fiscal Q ends Oct, Jan, Apr, Jul)
- KB Home (KBH): Jan, Mar, Jun, Sep (fiscal Q ends Nov, Feb, May, Aug)
- NVR (NVR): Jan, Apr, Jul, Oct

#### Derived Builder Metrics

| **Metric** | **Formula** | **Threshold** | **Signal** |
|---|---|---|---|
| **NAHB Momentum** | Current - 6M Avg | <-10 | Rapid deterioration |
| **Future-Current Gap** | Future Sales - Current Sales | <-5 | Pessimism about pipeline |
| **Price Cuts Share** | % of Builders with Price Reductions | >30% | Buyer's market |
| **Aggregate Order Growth** | Weighted Avg Orders YoY (Top 5 Builders) | <-5% | Demand weakening |
| **Aggregate Backlog Change** | Weighted Avg Backlog YoY (Top 5) | <-15% | Revenue pipeline shrinking |
| **Margin Compression** | Current Gross Margin - Year Ago | <-200 bps | Incentive costs rising |
| **Community Count vs Orders** | Community Count YoY - Order Growth YoY | >+10 ppts | Overexpansion risk |
| **Months of Backlog** | Backlog Units / Monthly Closings | <3 months | Pipeline thin |

#### Regime Thresholds: Builder Sentiment

| **Indicator** | **Pessimistic** | **Neutral** | **Optimistic** | **Euphoric** |
|---|---|---|---|---|
| **NAHB Index** | <40 | 40-50 | 50-65 | >65 |
| **Future Sales Component** | <45 | 45-55 | 55-70 | >70 |
| **Traffic Component** | <30 | 30-45 | 45-55 | >55 |
| **Price Cuts Share** | >35% | 25-35% | 15-25% | <15% |
| **Incentive Share** | >60% | 45-60% | 30-45% | <30% |
| **Aggregate Order Growth** | <-10% | -10% to +5% | +5% to +15% | >+15% |
| **Avg Cancel Rate** | >18% | 13-18% | 8-13% | <8% |

---

### G. MORTGAGE MARKET HEALTH (The Credit Channel)

Mortgage credit health determines whether housing stress transmits to the banking system. Delinquencies and defaults matter for systemic risk.

| **Indicator** | **FRED Code** | **Frequency** | **Lead/Lag** | **Interpretation** |
|---|---|---|---|---|
| **Mortgage Delinquency Rate (30+ Days)** | DRSFRMACBS | Quarterly | Lagging 1-2 qtrs | Stress gauge |
| **Mortgage Delinquency Rate (60+ Days)** | MBA NDS | Quarterly | Lagging 1-2 qtrs | Intermediate stress |
| **Mortgage Delinquency Rate (90+ Days)** | MBA NDS | Quarterly | Lagging 2-3 qtrs | Serious delinquency |
| **Foreclosure Inventory Rate** | MBA NDS | Quarterly | Lagging 2-4 qtrs | Active foreclosures |
| **Foreclosure Starts** | MBA NDS | Quarterly | Leads inventory 1-2 qtrs | New foreclosure initiations |
| **Foreclosure Filings** | ATTOM | Monthly | Lagging 3-6 qtrs | End-stage stress |
| **Mortgage Originations** | MBA | Quarterly | Coincident | Lending activity |
| **Refinance Activity** | MBA | Weekly | Coincident | Rate sensitivity gauge |
| **Home Equity as % of Value** | FRED (Z.1) | Quarterly | Lagging | Equity cushion |
| **Negative Equity Share** | Cotality (fka CoreLogic) | Quarterly | Lagging | Underwater borrowers |
| **Total Home Equity ($)** | Cotality / Fed Z.1 | Quarterly | Lagging | Aggregate wealth buffer |
| **Tappable Equity** | Cotality / ICE | Quarterly | Lagging | Available for HELOC/cash-out |

#### Credit Availability & Origination Quality

| **Indicator** | **Source** | **Frequency** | **Interpretation** |
|---|---|---|---|
| **Mortgage Credit Availability Index (MCAI)** | MBA | Monthly | Higher = looser standards; rising = easing |
| **MCAI by Component (Govt/Jumbo/Conforming)** | MBA | Monthly | Which segment is loosening/tightening |
| **Median FICO (Purchase)** | FHFA / Ellie Mae | Monthly | Origination quality; >750 = tight box |
| **Average LTV (Purchase)** | FHFA / Ellie Mae | Monthly | Leverage at origination |
| **Average DTI (Purchase)** | FHFA / Ellie Mae | Monthly | Debt burden at origination |
| **FHA Delinquency Rate** | MBA NDS | Quarterly | Low-down-payment stress; most vulnerable |
| **VA Delinquency Rate** | MBA NDS | Quarterly | Veteran borrower health |
| **Conventional Delinquency Rate** | MBA NDS | Quarterly | Prime borrower health |
| **HELOC Originations** | ICE / Equifax | Quarterly | Equity extraction activity |
| **Cash-Out Refi Volume** | MBA / ICE | Quarterly | Equity extraction via refi |
| **Fed SLOOS: Residential Lending Standards** | Federal Reserve | Quarterly | Bank willingness to lend |
| **Fed SLOOS: Residential Demand** | Federal Reserve | Quarterly | Borrower demand for mortgages |

#### Derived Credit Metrics

| **Metric** | **Formula** | **Threshold** | **Signal** |
|---|---|---|---|
| **Delinquency Trend** | Current 30+ Day - Year Ago | >+0.5 ppt | Stress building |
| **Equity Cushion** | Median Equity / Median Value | <20% | Negative equity risk |
| **Originations YoY%** | Current - Year Ago | <-20% | Credit contraction |
| **Refi Share of Apps** | Refi Apps / Total Apps | <20% | Rate-locked homeowners |
| **FHA-Conventional DQ Spread** | FHA DQ Rate - Conv DQ Rate | >+7 ppts | Low-income stress concentrated |
| **Foreclosure Pipeline** | FC Starts + FC Inventory | Rising for 3+ qtrs | Stress accumulating |
| **MCAI Trend** | Current - 12M Avg | <-10% | Credit tightening |
| **SLOOS Net Tightening** | % Tightening - % Easing | >+20% net | Banks pulling back |
| **Equity Extraction Rate** | (Cash-Out Refi + HELOC) / Total Tappable Equity | >5% | Aggressive extraction |

#### Regime Thresholds: Credit Health

| **Indicator** | **Crisis** | **Stressed** | **Normal** | **Healthy** |
|---|---|---|---|---|
| **30+ Day Delinquency** | >5.0% | 3.5-5.0% | 2.5-3.5% | <2.5% |
| **90+ Day Delinquency** | >2.0% | 1.0-2.0% | 0.5-1.0% | <0.5% |
| **Negative Equity Share** | >10% | 5-10% | 2-5% | <2% |
| **Foreclosure Rate** | >3.0% | 1.5-3.0% | 0.5-1.5% | <0.5% |
| **FHA Delinquency Rate** | >14% | 10-14% | 7-10% | <7% |
| **Median FICO (Purchase)** | <680 | 680-720 | 720-760 | >760 |
| **MCAI Level** | <80 | 80-100 | 100-130 | >130 |
| **SLOOS: Net Tightening** | >+40% | +20-40% | -10 to +20% | <-10% |

---

### H. RENTAL MARKET (The Affordability Release Valve)

When buying becomes unaffordable, people rent. Rental market dynamics affect housing demand, shelter inflation, and multifamily construction.

| **Indicator** | **Source** | **Frequency** | **Lead/Lag** | **Interpretation** |
|---|---|---|---|---|
| **Zillow Observed Rent Index (ZORI)** | Zillow | Monthly | **Leads CPI Shelter 12 mo** | Real-time market rents (all rentals) |
| **Apartment List Rent Index** | Apartment List | Monthly | Leads CPI 10-12 mo | National median rent (apartment-focused) |
| **CoreLogic Single-Family Rent** | Cotality | Monthly | Leads CPI 12 mo | SFR rental market |
| **Zumper National Rent Report** | Zumper | Monthly | Leads CPI 10-12 mo | 1BR/2BR median rents |
| **BLS CPI Shelter (OER + Rent)** | BLS | Monthly | **Lags market rents 12-18 mo** | Official inflation measure |
| **Vacancy Rate (Rental)** | Census | Quarterly | Lagging 1-2 qtrs | Supply/demand balance |
| **Apartment List Vacancy Index** | Apartment List | Monthly | **Leads Census 1-2 qtrs** | Higher-frequency vacancy proxy |
| **Multifamily Starts** | Census | Monthly | **Leads supply 18-24 mo** | Future rental supply |
| **Multifamily Completions** | Census | Monthly | Coincident | Current supply additions |
| **Multifamily Absorption Rate** | Census/RealPage | Quarterly | Coincident | Demand for completed units |
| **Concession Rate** | Zillow/RealPage | Monthly | Coincident | Share of listings offering concessions |
| **Rent Collection Rate** | NMHC | Monthly | Coincident | Tenant payment health |

#### Derived Rental Metrics

| **Metric** | **Formula** | **Threshold** | **Signal** |
|---|---|---|---|
| **Market Rent → CPI Lag** | Zillow YoY (12M Prior) vs CPI Shelter | Gap = mechanical disinflation | Predictive for shelter CPI |
| **Rent-to-Own Ratio** | Median Rent × 12 / Median Price | >6% | Renting preferable |
| **MF Completions vs Absorption** | Completions - Net Absorption | >0 for 2+ qtrs | Oversupply building |
| **Real Rent Growth** | Nominal Rent YoY - CPI YoY | <0% | Real rents declining |
| **Vacancy Change** | Current - Year Ago | >+1.0 ppt | Supply overwhelming demand |
| **Concession Spread** | Current % - Historical Avg (~20%) | >+15 ppts | Landlord desperation |
| **MF Pipeline Ratio** | MF Under Construction / Annual MF Completions | >2.0x | Supply wave incoming |
| **Rent-Wage Gap** | Rent YoY - Avg Hourly Earnings YoY | >+2 ppts | Affordability deteriorating |
| **Eviction Filing Trend** | Current vs Pre-Pandemic Avg | >+10% | Tenant stress emerging |

#### Regime Thresholds: Rental

| **Indicator** | **Deflationary** | **Stable** | **Inflationary** |
|---|---|---|---|
| **Zillow Rent YoY%** | <0% | 0-4% | >4% |
| **Apartment List YoY%** | <-1% | -1% to +3% | >+3% |
| **Rental Vacancy Rate** | >8% | 6-8% | <6% |
| **MF Starts YoY%** | <-20% | -20% to +20% | >+20% |
| **Concession Rate** | >40% | 25-40% | <25% |
| **Eviction Filings vs 2019** | >+15% | -5% to +15% | <-5% |


---

### I. DEMOGRAPHICS & HOUSEHOLD FORMATION (The Structural Demand Floor)

Demographics are destiny on a 5-10 year horizon. Household formation drives baseline housing demand regardless of rates or prices. This is where you separate cyclical weakness from structural undersupply.

| **Indicator** | **Source** | **Frequency** | **Lead/Lag** | **Interpretation** |
|---|---|---|---|---|
| **Household Formation Rate** | Census (CPS/HVS) | Annual/Quarterly | **Structural leading** | Net new households per year |
| **Population Growth (Total)** | Census | Annual | Structural | Baseline demand |
| **Population Growth (25-44)** | Census ACS | Annual | **Key cohort** | Peak homebuying age |
| **Millennials in Peak Buying Years** | Census ACS | Annual | Structural | 72M cohort, 29-44 in 2026 |
| **Gen Z Entry Cohort (25-29)** | Census ACS | Annual | Emerging | Next wave of first-time buyers |
| **Marriage Rate** | CDC NCHS | Annual | Leads formation 1-2 yrs | Household formation catalyst |
| **Divorce Rate** | CDC NCHS | Annual | Creates 2 households | Net addition to demand |
| **Net Migration (Domestic)** | Census/IRS SOI | Annual | Structural | Interstate demand shifts |
| **Net Immigration** | DHS/Census | Annual | Structural | Net new demand entrants |
| **Homeownership Rate** | Census (HVS) | Quarterly | Lagging | Structural tenure split |
| **Homeownership Rate by Age** | Census (CPS/ASEC) | Annual | Structural | Generational access |
| **Homeownership Rate by Race** | Census (HVS) | Quarterly | Structural | Equity gap monitor |

#### Derived Demographic Metrics

| **Metric** | **Formula** | **Threshold** | **Signal** |
|---|---|---|---|
| **Formation-Starts Gap** | HH Formation - Housing Starts (trailing 12M) | >+200k | Deficit accumulating |
| **Generational Ownership Gap** | Current 30-34 Rate - Boomer 30-34 Rate | <-8 ppts | Structural exclusion |
| **Prime Buyer Cohort Growth** | 25-44 Population YoY | <+0.5% | Demand headwind (unlikely near-term) |
| **Migration Concentration** | Top 5 Inbound States as % of Total | >60% | Geographic demand concentration |
| **Minority HH Formation Share** | Minority New HHs / Total New HHs | >80% | Compositional demand shift |
| **Immigration Impact** | Net Immigration × HH Formation Rate | >500k HHs | Significant demand boost |

#### Regime Thresholds: Demographics

| **Indicator** | **Headwind** | **Neutral** | **Tailwind** | **Structural Boom** |
|---|---|---|---|---|
| **Annual HH Formation** | <1.0M | 1.0-1.3M | 1.3-1.6M | >1.6M |
| **25-44 Pop Growth** | <+0.3% | +0.3-0.7% | +0.7-1.2% | >+1.2% |
| **Homeownership Rate** | <63% | 63-66% | 66-68% | >68% |
| **Net Immigration** | <500k | 500k-1M | 1-1.5M | >1.5M |
| **Cumulative Deficit** | <1M | 1-2M | 2-4M | >4M |

---

### J. CONSTRUCTION COSTS & MATERIALS (The Supply-Side Constraint)

Construction costs determine builder profitability and housing supply response. When costs rise faster than prices, builders pull back even if demand exists.

| **Indicator** | **Source** | **Frequency** | **Lead/Lag** | **Interpretation** |
|---|---|---|---|---|
| **PPI: Construction Materials** | BLS | Monthly | Coincident | Input cost pressure |
| **Lumber Futures** | CME | Daily | **Leads PPI 1-2 mo** | Real-time supply/demand |
| **Copper Futures** | COMEX | Daily | Coincident | Broad construction activity proxy |
| **Concrete/Cement PPI** | BLS | Monthly | Coincident | Non-substitutable input |
| **Steel (HRC) Futures** | CME | Daily | Leads PPI 1-2 mo | Structural material cost |
| **Construction Wages (AHE)** | BLS (CES) | Monthly | Lagging | Labor cost pressure |
| **Construction Employment** | BLS (CES) | Monthly | **Leads starts 1-2 mo** | Worker availability |
| **Construction Job Openings** | BLS (JOLTS) | Monthly | Leading 2-3 mo | Labor demand signal |
| **Residential Construction Cost Index** | Census | Monthly | Lagging | Official cost tracking |
| **RS Means Construction Cost** | Gordian | Quarterly | Lagging | Detailed cost benchmarks |
| **Regulatory Cost per Unit** | NAHB | Annual | Structural | Permitting/compliance burden |

#### Tariff & Trade Policy Inputs

| **Indicator** | **Source** | **Frequency** | **Interpretation** |
|---|---|---|---|
| **Canadian Softwood Lumber Tariff Rate** | USTR/Commerce | As announced | Direct cost impact (~35% of US lumber is imported) |
| **Steel/Aluminum Tariff Rate** | USTR | As announced | Structural materials cost |
| **Chinese Goods Tariff Rate** | USTR | As announced | Cabinets, hardware, fixtures, appliances |
| **Estimated Per-Unit Tariff Impact** | NAHB/Industry estimates | As updated | Dollar impact on new construction cost |
| **Import Share by Material** | Census/ITC | Annual | Vulnerability assessment |

#### Derived Cost Metrics

| **Metric** | **Formula** | **Threshold** | **Signal** |
|---|---|---|---|
| **Lumber YoY%** | Current - Year Ago | >+30% | Cost spike (margin squeeze) |
| **Materials PPI vs Home Prices** | PPI Construction YoY - HPI YoY | >+3 ppts | Margin compression |
| **Construction Wage Growth vs Overall** | Constr AHE YoY - Total AHE YoY | >+2 ppts | Skilled labor scarcity |
| **Regulatory Cost as % of Price** | Avg Regulatory Cost / Median New Price | >25% | Supply-restrictive policy |
| **Construction Employment vs Starts** | Constr Employment YoY - Starts YoY | >+5 ppts | Labor hoarding |
| **Tariff Cost Burden** | Estimated Per-Unit Tariff / Median Price | >5% | Meaningful cost headwind |

#### Regime Thresholds: Costs

| **Indicator** | **Deflationary** | **Normal** | **Inflationary** | **Crisis** |
|---|---|---|---|---|
| **Lumber ($/MBF)** | <$350 | $350-550 | $550-800 | >$800 |
| **Construction PPI YoY%** | <0% | 0-3% | 3-8% | >8% |
| **Construction AHE YoY%** | <2% | 2-4% | 4-6% | >6% |
| **Construction Employment YoY%** | <-3% | -3% to +3% | +3% to +5% | >+5% (or <-5%) |
| **Regulatory Cost/Unit** | <$85k | $85-95k | $95-110k | >$110k |

---

### K. POLICY & REGULATORY (The Exogenous Shock Layer)

Government policy can override market fundamentals. Regulatory changes, tax policy, and GSE status create binary risks that demand monitoring.

| **Policy Domain** | **Current Instruments** | **Impact Channel** | **Monitoring Source** |
|---|---|---|---|
| **Fed Mortgage Purchases** | MBS holdings (QT runoff ~$18B/mo) | Direct rate/spread impact | Fed H.4.1 |
| **GSE Status (Fannie/Freddie)** | Conservatorship since 2008 | IPO/privatization risk → pricing, guarantee fees | FHFA, Treasury |
| **FHA/VA Loan Limits** | Conforming limits (updated annually) | Access to government-backed credit | FHFA annual announcement |
| **Mortgage Interest Deduction** | Tax policy | Ownership incentive (primarily high earners) | IRS/Congress |
| **SALT Deduction Cap** | $10k cap (TCJA) | High-tax state housing demand | IRS/Congress |
| **Zoning/Land Use** | Local regulations | Supply constraints (NIMBY vs YIMBY) | Local/state legislatures |
| **Rent Control** | State/local laws | Rental supply/investment disincentive | State legislatures |
| **Institutional Investor Restrictions** | Proposed SFR purchase limits | Investor demand channel | Congress/state legislatures |
| **Immigration Policy** | Visa/asylum/enforcement | Both demand (buyers) and supply (labor) | DHS/Congress |
| **Treasury MBS Purchase Proposals** | Ad hoc policy proposals | Spread compression 20-50 bps | White House/Treasury |

#### Key Policy Risk Indicators

| **Indicator** | **Source** | **What to Watch** |
|---|---|---|
| **Fed MBS Holdings** | H.4.1 | Pace of runoff; any pause = supportive |
| **Fed MBS Reinvestment Policy** | FOMC Minutes | Shift from passive runoff to active sales |
| **FHFA Guarantee Fee Changes** | FHFA | Fee increases = tighter credit |
| **Conforming Loan Limit** | FHFA (annual) | Higher limits = more credit access |
| **LIHTC Allocation** | HUD | Affordable housing pipeline |
| **Section 8 Voucher Funding** | HUD | Rental demand support |
| **State ADU Legislation** | State capitals | Supply-side deregulation |
| **Municipal Permitting Timelines** | NAHB surveys | Supply bottleneck gauge |

---

### L. ALTERNATIVE & HIGH-FREQUENCY DATA (The Edge)

These indicators provide earlier signals than traditional data. They're noisier individually, but powerful in aggregate.

#### High-Frequency Transaction Data

| **Indicator** | **Source** | **Frequency** | **Lead Time vs Traditional** |
|---|---|---|---|
| **Altos Research Active Inventory** | HousingWire | Weekly | Leads NAR 2-4 weeks |
| **Altos Market Action Index** | HousingWire | Weekly | Leads prices 4-8 weeks |
| **Redfin Housing Demand Index** | Redfin | Weekly | Leads sales 4-6 weeks |
| **Redfin Homebuyer Demand Index** | Redfin | Daily | Real-time demand proxy |
| **Mortgage News Daily Rate Index** | MND | Daily | Same-day rate moves |
| **Optimal Blue Mortgage Lock Data** | Optimal Blue (ICE) | Daily | Leads MBA by 3-5 days |

#### Google Trends & Search Activity

| **Search Term** | **Interpretation** | **Lead Time** |
|---|---|---|
| **"Homes for sale"** | Buyer demand proxy | Leads sales 4-8 weeks |
| **"Mortgage rates"** | Rate sensitivity gauge | Coincident with rate moves |
| **"Refinance"** | Refi demand proxy | Leads MBA Refi Index 2-4 weeks |
| **"Sell my house"** | Seller intent proxy | Leads new listings 4-8 weeks |
| **"Home appraisal"** | Transaction pipeline | Leads closings 4-6 weeks |
| **"Moving companies"** | Relocation activity | Leads sales 2-4 weeks |

#### Cross-Asset Housing Proxies

These market prices embed housing expectations and provide real-time signals.

| **Indicator** | **Ticker** | **Frequency** | **Interpretation** |
|---|---|---|---|
| **XHB (SPDR S&P Homebuilders)** | XHB | Daily | Broad housing sector |
| **ITB (iShares Home Construction)** | ITB | Daily | Pureplay homebuilder index |
| **XLRE (Real Estate Select)** | XLRE | Daily | Broader real estate sector |
| **VNQ (Vanguard Real Estate)** | VNQ | Daily | REIT benchmark |
| **SFR REITs (AMH, INVH)** | AMH, INVH | Daily | Single-family rental demand |
| **Apartment REITs (EQR, AVB, MAA)** | EQR, AVB, MAA | Daily | Multifamily rent/occupancy proxy |
| **MBS ETFs (MBB, VMBS)** | MBB, VMBS | Daily | MBS spread proxy |
| **Mortgage Lenders (RKT, UWMC)** | RKT, UWMC | Daily | Origination volume proxy |
| **Building Materials (VMC, MLM, OC)** | VMC, MLM, OC | Daily | Construction activity proxy |
| **Home Improvement (HD, LOW)** | HD, LOW | Daily | Existing home turnover proxy |

**Cross-Asset Divergence Signals:**

| **Divergence** | **Signal** | **Interpretation** |
|---|---|---|
| **XHB rising, NAHB falling** | Market pricing recovery before fundamentals | Early bullish or speculative excess |
| **XHB falling, starts rising** | Market pricing slowdown before data confirms | Early bearish |
| **MBB rising, rates rising** | Spread compression despite rate increase | Credit risk appetite improving |
| **HD/LOW falling, HPI rising** | Turnover declining despite price appreciation | Lock-in effect confirmed |
| **AMH/INVH vs EQR/AVB** | SFR vs MF rental divergence | Structural vs cyclical rental demand |

#### Other Alternative Indicators

| **Indicator** | **Source** | **Frequency** | **Interpretation** |
|---|---|---|---|
| **U-Haul Growth Index** | U-Haul (annual) | Annual | Migration direction signal |
| **USPS Change of Address** | USPS | Monthly | Relocation volume |
| **Power Hookups (Utility Data)** | Local utilities | Monthly | New occupancy proxy |
| **Construction Crane Counts** | Rider Levett Bucknall | Semi-annual | Visual construction activity |
| **Satellite Construction Activity** | Orbital Insight / Kayrros | Daily | Real-time starts proxy |
| **Sentiment: r/RealEstate, r/FirstTimeHomeBuyer** | Reddit | Real-time | Retail buyer/seller sentiment |
| **Auction Clearance Rates** | Auction.com | Weekly | Distressed market velocity |

---

## Housing Composite Index (HCI) v2.0: The Master Signal

### Formula

The HCI synthesizes all housing sub-indicators into a single regime score, weighted by predictive power and signal reliability.

```
HCI = 0.15 × z(Construction)    +  0.12 × z(Sales)
    + 0.10 × z(Prices)          +  0.15 × z(Affordability)
    + 0.10 × z(Inventory)       +  0.10 × z(Builder_Sentiment)
    + 0.12 × z(Mortgage_Credit)  +  0.08 × z(Rental)
    + 0.05 × z(Alt_HF_Data)     +  0.03 × z(Demographics)
```

**Component Calculations:**

| **Component** | **Weight** | **Constituent Sub-Indicators** | **Direction** |
|---|---|---|---|
| **Construction** | 0.15 | Starts YoY, Permits YoY, SF/MF Ratio, Pipeline Rate | Higher = Bullish |
| **Sales** | 0.12 | Existing YoY, New YoY, Pending HSI, MBA Purchase YoY | Higher = Bullish |
| **Prices** | 0.10 | Case-Shiller YoY, FHFA YoY, Real HPI YoY | Higher = Bullish* |
| **Affordability** | 0.15 | NAR Affordability Index, Payment-to-Income (inv), Rate Level (inv) | Higher = Better Affordability |
| **Inventory** | 0.10 | Months' Supply (inv), Inventory YoY (inv), Deficit Estimate | Balanced target ~4 months |
| **Builder Sentiment** | 0.10 | NAHB Index, Future Sales, Order Growth, Margin Trend | Higher = Bullish |
| **Mortgage Credit** | 0.12 | Delinquency (inv), MCAI, Equity Cushion, SLOOS (inv) | Higher = Healthier |
| **Rental** | 0.08 | Rent YoY (inv for disinflation), Vacancy Change (inv), MF Pipeline (inv) | Higher = Less Inflationary |
| **Alt/HF Data** | 0.05 | XHB Rel Strength, Google Trends, Lumber Momentum | Higher = Bullish |
| **Demographics** | 0.03 | Formation-Construction Gap, Millennial Ownership Gap | Higher = More Structural Demand |

*Note: For prices, "bullish" in HCI context means housing sector health, not necessarily a positive macro signal. Rapidly appreciating prices without volume = unhealthy.*

### Sub-Composite Definitions

Each sub-composite rolls up the key indicators from its section:

```
z(Construction)      = 0.30×z(SF_Starts_YoY) + 0.25×z(Permits_YoY) + 0.20×z(Completions_YoY)
                     + 0.15×z(Under_Construction) + 0.10×z(MF_Starts_YoY)

z(Sales)             = 0.25×z(Existing_Sales_YoY) + 0.20×z(New_Sales_YoY)
                     + 0.25×z(Pending_Index) + 0.15×z(MBA_Purchase_YoY)
                     + 0.15×z(-Days_on_Market)

z(Prices)            = 0.30×z(CS_National_YoY) + 0.25×z(FHFA_YoY) + 0.20×z(Zillow_YoY)
                     + 0.15×z(Real_HPI_YoY) + 0.10×z(-Regional_Dispersion)

z(Affordability)     = 0.25×z(-Mortgage_Rate) + 0.25×z(NAR_Afford_Index)
                     + 0.25×z(-Payment_to_Income) + 0.15×z(-Mortgage_Spread)
                     + 0.10×z(-ARM_Share)

z(Inventory)         = 0.30×z(-Months_Supply_Existing) + 0.20×z(-Months_Supply_New)
                     + 0.20×z(-Active_Listings_YoY) + 0.15×z(-Price_Reductions_Share)
                     + 0.15×z(Structural_Deficit)

z(Builder_Sentiment) = 0.30×z(NAHB_Index) + 0.25×z(NAHB_Future)
                     + 0.20×z(-Price_Cuts_Share) + 0.25×z(Aggregate_Orders_YoY)

z(Mortgage_Credit)   = 0.25×z(-Delinquency_30d) + 0.20×z(-Foreclosure_Rate)
                     + 0.15×z(-Negative_Equity) + 0.15×z(MCAI_Level)
                     + 0.15×z(-FHA_DQ_Rate) + 0.10×z(-SLOOS_Net_Tightening)

z(Rental)            = 0.25×z(-Vacancy_Rate) + 0.25×z(Rent_YoY)
                     + 0.20×z(MF_Absorption_Rate) + 0.15×z(-Concession_Rate)
                     + 0.15×z(-MF_Pipeline_Ratio)

z(Alt_HF_Data)       = 0.35×z(XHB_Rel_Strength) + 0.35×z(Google_Trends_Momentum)
                     + 0.30×z(Lumber_Momentum)

z(Demographics)      = 0.40×z(HH_Formation) + 0.30×z(25_44_Pop_Growth)
                     + 0.30×z(Homeownership_Rate)
```

**v2.0 Changes from v1.0:** Dropped Costs and Policy as standalone components (their signals are embedded in Affordability and Builder Sentiment). Added Alt/HF Data (real-time leading indicators). Increased Construction weight (0.12→0.15) and Affordability (0.12→0.15) to reflect their forward-looking power. Reduced Demographics (0.06→0.03) given its slow-moving structural nature.

### HCI Regime Classification

| **HCI Range** | **Regime** | **Description** | **MRI Input** |
|---|---|---|---|
| > +1.0 | **Boom** | Strong across all dimensions. Overheating risk. | Bullish (watch for excess) |
| +0.5 to +1.0 | **Expansion** | Broad-based improvement, sustainable growth | Bullish |
| -0.5 to +0.5 | **Neutral / Frozen** | Mixed signals, low turnover, stasis | Neutral |
| -1.0 to -0.5 | **Contraction** | Weakening demand, builder stress, rising inventory | Bearish |
| < -1.0 | **Crisis** | Systemic stress, credit deterioration, price declines | Very Bearish |

### HCI Interpretation Notes

1. **Frozen ≠ Neutral.** The current regime (low transactions, stable prices, locked-in sellers) reads as "neutral" on HCI but is fundamentally abnormal. Monitor the spread between the Sales component (very weak) and the Prices component (stable) as a frozen market signature.

2. **Affordability is the swing factor.** A 100 bps decline in mortgage rates can shift HCI by +0.3 to +0.5 points through affordability alone. This is the most rate-sensitive pillar in the entire framework.

3. **Construction leads, prices lag.** Construction and builder sentiment components tend to turn 3-6 months before prices confirm. Weight early signals accordingly.

4. **Credit is the systemic risk channel.** If Mortgage Credit drops below -0.5 while other components are stable, it signals trouble the rest of the market hasn't priced. The 2008 analog: credit deteriorated 12 months before prices collapsed.

### HCI Integration with MRI

The HCI feeds into the MRI (Macro Risk Index) through the HCI weight (0.06). But housing's influence on the macro picture is larger than its direct MRI weight because it transmits through multiple other pillars:

```
Housing → Consumer Confidence (CCI: via wealth effect)
Housing → Business Investment (BCI: via construction employment)
Housing → Price Dynamics (PCI: via shelter inflation, 34% of CPI)
Housing → Financial Conditions (FCI: via MBS/mortgage credit)
Housing → Labor Market (LPI: via construction employment, RE services)
```

**Effective Housing Influence on MRI:** ~15-20% when transmission channels are included, despite a direct weight of 6%.

---

## Cross-Pillar Integration

### Pillar 4 → Other Pillars

| **Receiving Pillar** | **Transmission Mechanism** | **Lead Time** | **Key Indicator** |
|---|---|---|---|
| **Pillar 1 (Labor)** | Construction employment, RE agent employment, mortgage industry employment | 2-4 months | Starts → Construction Payrolls |
| **Pillar 2 (Prices)** | Shelter CPI/PCE (34% of CPI, 18% of Core PCE) | **12-18 months** | Zillow ZORI → CPI Shelter |
| **Pillar 3 (Growth)** | Residential fixed investment (3-5% of GDP), wealth-effect-driven consumption | 3-6 months | Starts + Sales → GDP Residential Investment |
| **Pillar 5 (Consumer)** | Home equity wealth effect ($1 equity → $0.05-0.08 spending) | 3-6 months | HPI → Consumer Spending |
| **Pillar 6 (Business)** | Building materials demand, home improvement, real estate services | 2-4 months | Starts → Materials/Services Demand |
| **Pillar 7 (Trade)** | Lumber/materials imports, foreign buyer flows | 1-3 months | Construction Activity → Imports |
| **Pillar 8 (Government)** | Property tax revenue, GSE exposure, MID tax expenditure | 6-12 months | HPI → Local Government Revenue |
| **Pillar 9 (Financial)** | MBS markets, bank mortgage exposure, HELOC credit | 3-9 months | Delinquency → Bank Stress |
| **Pillar 10 (Plumbing)** | MBS holdings, Fed QT pace, repo collateral | 1-4 weeks | Fed MBS Runoff → Reserve Dynamics |
| **Pillar 11 (Structure)** | Homebuilder/REIT equity performance | Real-time | XHB/ITB → Sector Rotation |
| **Pillar 12 (Sentiment)** | Consumer confidence (home as largest asset), builder confidence | 1-3 months | NAHB → Broad Sentiment |

### Other Pillars → Pillar 4

| **Sending Pillar** | **Transmission Mechanism** | **Key Indicator** |
|---|---|---|
| **Pillar 1 (Labor)** | Employment/wage growth → affordability → demand | Payrolls, AHE → MBA Purchase |
| **Pillar 2 (Prices)** | Inflation → Fed rates → mortgage rates | CPI → Fed Funds → Mortgage Rate |
| **Pillar 3 (Growth)** | GDP growth → income growth → housing demand | GDP → Consumer Income |
| **Pillar 5 (Consumer)** | Consumer health → willingness to commit to mortgage | Consumer Confidence → Home Sales |
| **Pillar 8 (Government)** | Fiscal policy, housing tax incentives | Tax Policy → Ownership Incentive |
| **Pillar 9 (Financial)** | Credit conditions → mortgage availability | SLOOS → Mortgage Credit Access |
| **Pillar 10 (Plumbing)** | Fed MBS policy → mortgage spreads → rates | QT Pace → MBS Spread → 30Y Rate |

### The Shelter Inflation Bridge (Pillar 4 → Pillar 2)

This is the single most important cross-pillar link in the entire framework. Shelter represents:
- 34.4% of CPI
- ~18% of Core PCE (the Fed's preferred measure)
- 12-18 month lag from market rents to official measures

**The Mapping:**
```
Zillow ZORI YoY (today) → CPI Shelter YoY (12-18 months from now)

If Zillow ZORI YoY = -1.5% today:
→ CPI Shelter will decelerate to ~2.5-3.0% within 12-18 months
→ Core CPI mechanical drag of ~0.5-0.7 ppts
→ Fed has cover to cut (if labor allows)
```

**Why This Matters for Trading:** The shelter CPI component is the most predictable inflation input. When market rents are falling, the disinflation is baked in. The only question is timing. This gives 12-18 months of forward visibility on the inflation trajectory, which is enormously valuable for rates positioning.

---

## Lead/Lag Relationships: The Housing Cascade

```
LEADING                           COINCIDENT                  LAGGING
────────────────────────────────────────────────────────────────────────────────────
│                                 │                          │
│  MBA Purchase Index (4-8 wks)   │  Housing Starts          │  Case-Shiller HPI (3-6 mo)
│  Building Permits (1-2 mo)      │  Existing Home Sales     │  CPI Shelter (12-18 mo)
│  NAHB Index (1-3 mo)            │  New Home Sales          │  Mortgage Delinquency (1-2 qtrs)
│  Mortgage Rate Changes (1-2 mo) │  Active Inventory        │  Foreclosures (3-6 qtrs)
│  Pending Home Sales (1-2 mo)    │  Months' Supply          │  FHFA HPI (3-6 mo)
│  Zillow Rent Index (12 mo→CPI)  │  Median Prices           │  Residential Investment GDP
│  10Y Treasury (0-1 wk→Mortgage) │  Completions             │  Home Equity Loans
│  Redfin Listings Data (2-4 wks) │                          │  Property Tax Receipts
│                                 │                          │
────────────────────────────────────────────────────────────────────────────────────
```

**The Critical Chain:**

1. **Mortgage rates rise** (Fed hikes, Treasury selloff) → 4-8 weeks later → **MBA purchase apps collapse**
2. **Purchase apps collapse** → 1-2 months later → **Sales volumes drop**
3. **Sales drop + Supply frozen** → 3-6 months later → **Prices adjust (or don't, if supply collapses)**
4. **Construction slows** → 6-9 months later → **GDP residential investment contracts**
5. **Market rents cool** → 12-18 months later → **CPI shelter falls** (mechanical)

---

## Historical Pattern Recognition

### Cycle Archetypes

| **Pattern** | **Characteristics** | **Historical Examples** | **Trading Implications** |
|---|---|---|---|
| **Classic Boom-Bust** | Rates low → credit loose → prices surge → overbuilding → bust | 2003-2009 | Short builders late, long distressed early |
| **Rate Shock Freeze** | Rates spike → transactions collapse → prices sticky → stalemate | 2022-2026 | Lock-in creates opportunity when rates ease |
| **Supply-Constrained Appreciation** | Structural deficit + demand → steady price appreciation | 2012-2019 | Long homebuilders on any pullback |
| **Regional Divergence** | Migration-driven boom/bust in specific markets | Sun Belt 2020-2025 | Regional pairs: long undersupplied, short oversupplied |
| **Policy-Driven Distortion** | Government intervention alters natural price discovery | QE MBS purchases 2020-2022, First-Time Buyer Credits 2009-2010 | Position ahead of policy expiration/implementation |

### Key Historical Thresholds and What Happened Next

| **Condition** | **What Happened** | **Lead Time** |
|---|---|---|
| **Existing sales < 4.0M SAAR** | Preceded bottom, then gradual recovery | 6-12 months to trough |
| **NAHB < 40 for 6+ months** | Builder capitulation; starts bottom within 3-6 months | 3-6 months |
| **Mortgage rates fall 100+ bps from peak** | Sales volume recovers 15-25% within 6 months | 4-8 months |
| **Months' supply > 7 (existing)** | Prices decline 5-15% over subsequent 12 months | 6-12 months |
| **HPI YoY turns negative** | Wealth effect drag on consumption within 2 quarters | 3-6 months |
| **FHA DQ > 12%** | Policy intervention typically follows within 2-3 quarters | 6-9 months |
| **Rental vacancy > 7%** | Rent growth decelerates; shelter CPI follows 12-18 months later | 12-18 months |
| **XHB outperforms SPY by 20%+ YTD** | Market pricing recovery before fundamentals confirm | 3-9 months |

### Divergence Signals Worth Monitoring

| **Divergence** | **What It Means** | **Resolution** |
|---|---|---|
| **Sales down, prices up** | Lock-in effect dominating; low inventory supporting prices | Resolves when rates ease enough to unlock supply |
| **Starts up, NAHB down** | Builders completing commitments but not starting new ones | Starts will follow NAHB down within 2-3 months |
| **MBS spreads tight, rates high** | Credit risk appetite present despite rate pain | Supports housing at margin; recovery catalyst |
| **Rents falling, CPI shelter rising** | Mechanical lag in official data | CPI shelter will catch down to market rents |
| **Builder earnings down, XHB up** | Market looking through trough, pricing recovery | Confirms cycle bottom if fundamentals inflect within 6 months |
| **FHA DQ rising, conventional DQ flat** | Stress concentrated in low-income/first-time buyers | Not systemic; localized policy risk |
| **Permits up, starts down** | Builders approved but delaying ground-breaking | Cost, labor, or demand uncertainty; resolves with catalyst |

---

## Data Sources & Infrastructure

### Primary Data Sources

| **Source** | **Key Data** | **Update Schedule** | **Access** |
|---|---|---|---|
| **Census Bureau** | Starts, permits, completions, new home sales, vacancy, construction spending | Monthly (17th-ish) | FRED / Census.gov |
| **NAR** | Existing home sales, inventory, prices, affordability, buyer profile | Monthly (21st-ish) | NAR.realtor |
| **FHFA** | House Price Index (national, state, metro) | Monthly/Quarterly | FHFA.gov / FRED |
| **S&P/Cotality (CoreLogic)** | Case-Shiller HPI, negative equity, foreclosures | Monthly (last Tues) | S&P Global / FRED |
| **NAHB** | Builder confidence, price cuts, incentive usage | Monthly (mid-month) | NAHB.org |
| **MBA** | Purchase/refi apps, delinquency survey, originations, MCAI | Weekly/Quarterly | MBA.org |
| **Freddie Mac** | PMMS (mortgage rates), housing deficit estimates | Weekly/Annual | FreddieMac.com / FRED |
| **Zillow** | ZHVI (prices), ZORI (rents), inventory, days on market | Monthly | Zillow Research |
| **Redfin** | Median prices, days on market, demand index, luxury/non-luxury | Weekly/Monthly | Redfin Data Center |
| **Apartment List** | Rent index, vacancy index | Monthly | ApartmentList.com |
| **Realtor.com** | Active listings, new listings, median list price | Weekly/Monthly | Realtor.com Research |
| **Altos Research / HousingWire** | Market Action Index, weekly inventory | Weekly | HousingWire.com |
| **ATTOM** | Foreclosure filings, auction data, property data | Monthly/Quarterly | ATTOM.com |
| **ICE (fka Black Knight)** | Mortgage monitor, prepayment data, tappable equity | Monthly | ICE Mortgage Technology |
| **Federal Reserve** | SLOOS (lending standards), Z.1 (household balance sheet), H.4.1 (MBS holdings) | Quarterly/Weekly | FederalReserve.gov |
| **BLS** | CPI Shelter, Construction Employment, Construction Wages, PPI Construction | Monthly | BLS.gov / FRED |

### FRED Series Quick Reference

| **Metric** | **FRED Code** | **Notes** |
|---|---|---|
| Housing Starts | HOUST | SAAR, thousands |
| SF Starts | HOUST1F | SAAR, thousands |
| Building Permits | PERMIT | SAAR, thousands |
| SF Permits | PERMIT1 | SAAR, thousands |
| New Home Sales | HSN1F | SAAR, thousands |
| Existing Home Sales | EXHOSLUSM495S | SAAR, millions |
| Months' Supply (New) | MSACSR | Months |
| CS National HPI | CSUSHPINSA | Index, not seasonally adjusted |
| CS 20-City Composite | SPCS20RSA | Index, seasonally adjusted |
| FHFA HPI | USSTHPI | Index |
| 30Y Mortgage Rate | MORTGAGE30US | Percent, weekly |
| 15Y Mortgage Rate | MORTGAGE15US | Percent, weekly |
| 10Y Treasury | DGS10 | Percent, daily |
| Homeownership Rate | RHORUSQ156N | Percent, quarterly |
| Rental Vacancy Rate | RRVRUSQ156N | Percent, quarterly |
| Homeowner Vacancy Rate | RHVRUSQ156N | Percent, quarterly |
| Mortgage Delinquency 30+ | DRSFRMACBS | Percent, quarterly |
| CPI Shelter | CUSR0000SAH1 | Index |
| Residential Constr Employment | USCONS | Thousands |
| Construction AHE | CES2000000003 | $/hour |

---

## Appendix: Housing Economic Release Calendar

| **Release** | **Source** | **Typical Date** | **Market Impact** |
|---|---|---|---|
| **MBA Weekly Apps** | MBA | Wednesday 7AM ET | Low-moderate |
| **NAHB Builder Confidence** | NAHB | 3rd Monday of month | Moderate |
| **Housing Starts & Permits** | Census | ~17th of month (prior month) | **High** |
| **Existing Home Sales** | NAR | ~21st of month (prior month) | **High** |
| **New Home Sales** | Census | ~25th of month (prior month) | Moderate-High |
| **Case-Shiller HPI** | S&P | Last Tuesday of month (2M lag) | **High** |
| **FHFA HPI** | FHFA | Last week of month (2M lag) | Moderate |
| **Pending Home Sales** | NAR | Last business day of month | Moderate |
| **Construction Spending** | Census | 1st business day of month | Moderate |
| **MBA Delinquency Survey** | MBA | Quarterly (~6 week lag) | Moderate |
| **Fed SLOOS** | Fed | Quarterly (Feb, May, Aug, Nov) | Moderate-High |
| **Freddie Mac PMMS** | Freddie Mac | Thursday | Moderate |

---

**END OF PILLAR 4: HOUSING**

---

## Watchlist: Key Levels & Early Warning Signals

These are the thresholds that, when breached, demand attention and potential regime reclassification.

### Bullish Triggers (Housing Recovery Accelerating)

| **Signal** | **Threshold** | **Current Status** | **Significance** |
|---|---|---|---|
| Mortgage rates below 5.5% | 30Y < 5.5% | Not yet (~6.1%) | Unlocks significant locked-in cohort |
| Existing sales above 4.5M SAAR | >4.5M | Not yet (~3.9M) | Market unfreezing |
| NAHB above 50 | >50 | Not yet (37) | Builder breakeven |
| MBA Purchase Index +15% YoY | >+15% YoY | ~+4% | Demand acceleration |
| Price reductions share declining | <25% from elevated | Elevated (~35-40%) | Seller confidence returning |
| Pending Home Sales > 90 | >90 | ~72 | Pipeline rebuilding |
| FTB share above 35% | >35% | ~31% | Entry buyers returning |

### Bearish Triggers (Housing Stress Escalating)

| **Signal** | **Threshold** | **Current Status** | **Significance** |
|---|---|---|---|
| FHA delinquency above 13% | >13% | ~11.5% | Low-income borrower stress |
| Foreclosure filings +50% YoY | >+50% YoY | ~+14-32% | Credit cycle turning |
| Months' supply (existing) above 6 | >6.0 months | ~3.7 | Buyer's market (prices will fall) |
| NAHB below 30 | <30 | 37 | Builder capitulation |
| Builder gross margins below 18% | <18% aggregate | Mixed (17-27%) | Incentive costs unsustainable |
| Negative equity above 5% | >5% | ~2.1% | Underwater risk systemic |
| XHB underperforming SPX by >10% (63d) | <-10% rel strength | Currently outperforming | Market pricing housing downturn |

### Structural Shift Signals

| **Signal** | **Threshold** | **Significance** |
|---|---|---|
| Homeownership rate breaking above 67% | >67% | Structural demand wave (currently ~65.6%) |
| Millennial ownership rate converging with prior gen | Gap < 5 ppts | Pent-up demand releasing |
| Structural deficit narrowing below 1.5M | <1.5M units | Supply/demand normalizing |
| Rental vacancy above 9% | >9% | Multifamily oversupply structural |
| Remote work share stabilizing above 25% | >25% | Permanent geographic demand shift |

---

## Appendix: Housing's Place in the MRI

Housing enters the MRI as Pillar 4 with a weight of 0.06 (6%). This is the lowest single-pillar weight in the macro framework, reflecting three realities:

1. **Housing is slow.** Its lead times (6-12 months) are already embedded in other pillars by the time housing data confirms.
2. **Housing is amplified through other channels.** Its impact on labor (P1), prices (P2), consumer (P5), and credit (P9) means housing's true influence on MRI is much larger than 6%.
3. **Housing is regime-dependent.** In normal cycles, housing is a moderate input. In 2008-type credit events, housing IS the cycle. The 6% weight prevents overweighting in normal times while the cross-pillar transmission captures housing's amplification during stress.

**MRI Input Mapping:**

```
HCI → MRI (Pillar 4 contribution):
    MRI_P4 = 0.06 × (-HCI)

    Negative sign: Higher HCI = lower macro risk
    When HCI < -1.0 (housing crisis): MRI_P4 adds +0.06 to risk
    When HCI > +1.0 (housing boom): MRI_P4 subtracts 0.06 from risk
```

**The 2008 Exception:** In a true housing credit crisis, the cross-pillar transmission turns housing from a 6% input into the dominant macro driver. The framework captures this not through the HCI weight, but through simultaneous deterioration in FCI (credit spreads), LPI (construction employment), CCI (wealth effect), and LCI (MBS market stress). When all those pillars flash red together and housing is the common cause, you don't need a higher HCI weight. You need to recognize the pattern.

---

## Invalidation Criteria

### Bull Case (Housing Thaw) Invalidation Thresholds

If the following occur simultaneously for 3+ months, the bearish housing thesis is invalidated:

| **Signal** | **Threshold** |
|---|---|
| 30Y Mortgage Rate | Drops below 6.0% |
| Existing Home Sales | Exceeds 4.5M SAAR |
| Housing Starts | Exceeds 1.5M |
| NAHB Index | Exceeds 55 |
| MBA Purchase Index YoY% | Turns positive (+10%+) |
| HCI | Exceeds +0.3 (neutral regime) |

**Action if Invalidated:** Rotate to homebuilders (XHB, ITB), building materials (lumber, copper), home improvement (HD, LOW). Housing thaw = consumer confidence revival.

### Bear Case (Housing Crisis) Confirmation Thresholds

If the following occur, housing is deteriorating beyond frozen into crisis:

| **Signal** | **Threshold** |
|---|---|
| Mortgage Delinquency 30+ | Exceeds 4.0% |
| Existing Home Sales | Drops below 3.0M |
| Case-Shiller YoY% | Turns negative for 3+ months |
| Housing Starts | Drops below 1.0M |
| Negative Equity Share | Exceeds 5% |
| HCI | Drops below -1.0 (crisis regime) |

**Action if Confirmed:** Maximum defensive. Avoid all housing exposure (homebuilders, REITs, mortgage lenders). Overweight cash (SGOV), long duration (TLT). Housing crisis = recession confirmation.

---

## FRED Series Reference Appendix

All FRED series codes referenced in this pillar, organized by category. Pipeline source: `Lighthouse_Master.db` via `lighthouse_master_db.py`.

### Construction (Section A)

| **Series ID** | **Description** | **Frequency** |
|---|---|---|
| PERMIT | Building Permits (SAAR) | Monthly |
| PERMIT1 | Building Permits: Single-Family | Monthly |
| HOUST | Housing Starts (SAAR) | Monthly |
| HOUST1F | Housing Starts: Single-Family | Monthly |
| COMPUTSA | Housing Completions (SAAR) | Monthly |
| UNDCONTSA | Units Under Construction | Monthly |
| PERMITNSA | Building Permits (NSA) | Monthly |
| HOUSTNE | Housing Starts: Northeast | Monthly |
| HOUSTMW | Housing Starts: Midwest | Monthly |
| HOUSTS | Housing Starts: South | Monthly |
| HOUSTW | Housing Starts: West | Monthly |

### Sales (Section B)

| **Series ID** | **Description** | **Frequency** |
|---|---|---|
| HSN1F | New Home Sales (SAAR) | Monthly |
| EXHOSLUSM495S | Existing Home Sales (SAAR) | Monthly |
| MSACSR | Months' Supply of New Houses | Monthly |

### Prices (Section C)

| **Series ID** | **Description** | **Frequency** |
|---|---|---|
| CSUSHPINSA | Case-Shiller National Home Price Index (NSA) | Monthly |
| SPCS20RSA | Case-Shiller 20-City Composite (SA) | Monthly |
| USSTHPI | FHFA House Price Index | Monthly |

### Affordability & Rates (Section D)

| **Series ID** | **Description** | **Frequency** |
|---|---|---|
| MORTGAGE30US | 30-Year Fixed Rate Mortgage Average | Weekly |
| MORTGAGE15US | 15-Year Fixed Rate Mortgage Average | Weekly |
| DGS10 | 10-Year Treasury Constant Maturity Rate | Daily |

### Mortgage Credit Health (Section G)

| **Series ID** | **Description** | **Frequency** |
|---|---|---|
| DRSFRMACBS | Delinquency Rate on SF Residential Mortgages, All CB (SA) | Quarterly |

### Rental Market (Section H)

| **Series ID** | **Description** | **Frequency** |
|---|---|---|
| RRVRUSQ156N | Rental Vacancy Rate in the United States | Quarterly |
| CUSR0000SAH1 | CPI: Shelter (SA, All Urban Consumers) | Monthly |

### Demographics (Section I/K)

| **Series ID** | **Description** | **Frequency** |
|---|---|---|
| RHORUSQ156N | Homeownership Rate in the United States | Quarterly |
| RHVRUSQ156N | Homeowner Vacancy Rate in the United States | Quarterly |

### Construction Costs & Labor (Section J/L)

| **Series ID** | **Description** | **Frequency** |
|---|---|---|
| USCONS | All Employees: Construction (Thousands) | Monthly |
| CES2000000003 | Average Hourly Earnings: Construction | Monthly |

### Non-FRED Data Sources

| **Indicator** | **Source** | **Notes** |
|---|---|---|
| NAHB HMI | nahb.org | Excel download, free, monthly |
| MBA Purchase Index | MBA | Proprietary, no free FRED source |
| NAR Pending Home Sales | NAR | Not on FRED, NAR subscription |
| NAR Existing Home Sales (regional) | FRED | EXHOSLUSNEM495S, EXHOSLUSMWM495S, EXHOSLUSSOM495S, EXHOSLUSWTM495S |
| Mortgage Delinquency 60+/90+ Day | MBA NDS | MBA National Delinquency Survey (not on FRED by duration bucket) |
| Zillow ZHVI / ZORI | Zillow Research | Free CSV downloads, in pipeline via zillow_fetcher.py |
| Foreclosure Filings | ATTOM | attomdata.com |
| Tappable Equity | Cotality / ICE | Quarterly reports |
| MCAI | MBA | Monthly, not on FRED |
| SLOOS Residential | Federal Reserve | Quarterly survey, not a FRED series |

---

**END OF PILLAR 4: HOUSING**

*Framework Version: 2.0*
*Indicators Tracked: 120+*
*Categories: 12 (Construction, Sales, Prices, Affordability, Inventory, Builder Sentiment, Mortgage Credit, Rental, Alternative/HF, Policy, Demographics, Construction Costs)*
*Derived Metrics: 60+*
*Regime Thresholds: 80+*
*Last Updated: February 2026*

