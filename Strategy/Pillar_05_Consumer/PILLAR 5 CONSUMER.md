# PILLAR 5: CONSUMER

## The Consumer Transmission Chain

The consumer isn't a sector. It's **68% of GDP**. The transmission mechanism operates through cascading confidence and credit dynamics:

```
Employment Security → Income Growth → Confidence →
Spending Decisions → Credit Usage → Retail Sales →
Corporate Revenue → Hiring Decisions →
Employment Security (Reinforcing Loop)
```

**The Insight:** The consumer is a **lagging indicator pretending to be coincident**. By the time retail sales collapse, labor already cracked 6-9 months prior. The consumer is the last domino, the one that confirms the recession everyone else saw coming.

The beauty of consumer data: it's **high frequency** (weekly credit card data, monthly retail sales) but **backward-looking** (spending decisions reflect confidence formed months ago). The consumer tells you where the economy was, not where it's going. For that, watch labor and credit.

---

## Why Consumer Matters: The 68% Anchor

Personal Consumption Expenditures (PCE) is the **largest GDP component by far**. When the consumer sneezes, GDP catches pneumonia.

**The Cascade:**

**1. Consumer → GDP:** PCE is ~68% of output (coincident)
**2. Consumer → Corporate Earnings:** Revenue tracks consumer spending (1-2 quarter lag)
**3. Consumer → Labor:** Hiring follows sales (2-4 month lag)
**4. Consumer → Credit:** Spending drives loan demand (coincident)
**5. Consumer → Inflation:** Demand-pull inflation from excess spending (3-6 month lag)

Get the consumer call right, and you've anchored your GDP forecast. Miss it, and you're guessing at 68% of the economy.

**The Stages of Consumer Stress:** Consumer deterioration follows a predictable four-stage sequence. Knowing which stage you're in determines positioning.

1. **Savings Depletion** (Leading): Excess buffers drawn down. Saving rate falls below pre-pandemic norm. Flush-phase behavior fades.
2. **Credit Substitution** (Leading-Coincident): Revolving credit balances rise. Credit card delinquencies turn up. Debt service ratio stretches.
3. **Spending Cuts** (Coincident): Durables contract first, then services. Real PCE growth slows, turns negative. Trading-down accelerates.
4. **Recession Confirmed** (Lagging): Retail sales contract YoY. Corporate revenues miss. Layoffs feed back into further income contraction (the reinforcing loop closes).

By the time Stage 4 arrives, labor cracked at Stage 0 (quits peak), credit stress appeared in Stage 1-2, and the recession was already 6-9 months old. The consumer is the confirmation, not the signal. The signal came from labor.

---

## Primary Indicators: The Complete Architecture

### A. SPENDING FLOWS (The Core Signal)

Spending is the output variable: what consumers actually do. Track it at multiple frequencies and decompositions.

| **Indicator** | **FRED Code** | **Frequency** | **Lead/Lag** | **Interpretation** |
|---|---|---|---|---|
| **Personal Consumption Expenditures (PCE)** | PCE | Monthly | Coincident | Total consumer spending (nominal) |
| **Real PCE** | PCEC96 | Monthly | Coincident | Inflation-adjusted spending |
| **PCE: Goods** | DGDSRC1 | Monthly | Coincident | Durable + nondurable goods |
| **PCE: Durable Goods** | PCDG | Monthly | **Leads services 2-4 mo** | Big-ticket items (cars, appliances) |
| **PCE: Nondurable Goods** | PCND | Monthly | Coincident | Consumables (food, gas, clothing) |
| **PCE: Services** | PCESV | Monthly | Lagging 1-2 mo | 65% of PCE (healthcare, housing, dining) |
| **Retail Sales** | RSXFS | Monthly | Coincident | Goods-focused spending |
| **Retail Sales ex-Autos** | RSFSXMV | Monthly | Coincident | Strips volatile component |
| **Retail Sales: Control Group** | Derived (Census) | Monthly | Coincident | Core retail (GDP proxy) |
| **Real Retail Sales** | Derived | Monthly | Coincident | Deflated by CPI |

#### Derived Spending Metrics

| **Metric** | **Formula** | **Threshold** | **Signal** |
|---|---|---|---|
| **Real PCE YoY%** | Current - Year Ago | <1.5% | Stagnation |
| **Real PCE Momentum** | 3M Ann - 12M Ann | <-1 ppt | Deceleration |
| **Goods/Services Spread** | Goods YoY - Services YoY | <-3 ppts | Goods weakness (cyclical warning) |
| **Real Retail Sales YoY%** | Nominal - CPI YoY | <0% | Volume contraction |
| **Control Group Momentum** | 3M Avg - 6M Avg | <-0.5% | Trend deterioration |

#### Regime Thresholds: Spending

| **Indicator** | **Contraction** | **Stagnation** | **Normal** | **Boom** |
|---|---|---|---|---|
| **Real PCE YoY%** | <0% | 0-1.5% | 1.5-3.0% | >3.0% |
| **Real Retail Sales YoY%** | <-1% | -1% to +1% | +1% to +4% | >+4% |
| **Durable Goods PCE YoY%** | <-5% | -5% to +2% | +2% to +8% | >+8% |
| **Services PCE YoY%** | <1% | 1-2% | 2-4% | >4% |

**The Durables Canary:** Durable goods spending is the **most cyclical** PCE component. Consumers defer big-ticket purchases (cars, appliances, furniture) when confidence drops, so durables contract 2-4 months ahead of nondurables and 4-6 months ahead of services. Watch the goods/services YoY spread: when durables go negative while services remain positive, that's classic late-cycle, discretionary collapsing first. The sequence is predictable. Durables lead down, nondurables follow, services last.

**Historical benchmark:** In the 2008 cycle, real durables peaked in Q2 2007 and turned negative YoY by Q3 2007, five months before NBER's recession start date. In the 2001 cycle, durables peaked in mid-2000 and were negative by early 2001. Both preceded services weakness by multiple quarters.

---

### B. INCOME & SAVINGS (The Fuel Tank)

Spending requires income or savings drawdown. When both are depleted, spending stops.

| **Indicator** | **FRED Code** | **Frequency** | **Lead/Lag** | **Interpretation** |
|---|---|---|---|---|
| **Personal Income** | PI | Monthly | Coincident | Total income (wages, transfers, dividends) |
| **Disposable Personal Income (DPI)** | DPI | Monthly | Coincident | After-tax income |
| **Real DPI** | DSPIC96 | Monthly | Coincident | Inflation-adjusted income |
| **Wages & Salaries** | A576RC1 | Monthly | Coincident | Largest income component (~60%) |
| **Personal Saving** | PSAVE | Monthly | Coincident | DPI - PCE |
| **Personal Saving Rate** | PSAVERT | Monthly | **Leading 3-6 mo** | Savings as % of DPI |
| **Real DPI Per Capita** | A229RX0 | Monthly | Coincident | Living standards gauge |
| **Transfer Payments** | A063RC1 | Monthly | Coincident | Government support (SS, UI, welfare) |

#### Derived Income/Savings Metrics

| **Metric** | **Formula** | **Threshold** | **Signal** |
|---|---|---|---|
| **Real DPI YoY%** | Current - Year Ago | <1.5% | Purchasing power squeeze |
| **Saving Rate Gap** | Current - Pre-Pandemic Avg (7.5%) | <-3 ppts | Savings depleted |
| **Income-Spending Gap** | Real DPI YoY - Real PCE YoY | <-1 ppt | Spending exceeds income (unsustainable) |
| **Wage Growth Real** | Wage YoY - CPI YoY | <0% | Real wage erosion |
| **Transfer Dependency** | Transfers / Personal Income | >20% | Fiscal dependency elevated |

#### Regime Thresholds: Income & Savings

| **Indicator** | **Stressed** | **Stretched** | **Normal** | **Flush** |
|---|---|---|---|---|
| **Personal Saving Rate** | <3.5% | 3.5-5.5% | 5.5-8.0% | >8.0% |
| **Real DPI YoY%** | <0% | 0-2% | 2-4% | >4% |
| **Real Wage Growth** | <-1% | -1% to +1% | +1% to +2% | >+2% |
| **Excess Savings Stock** | <$0 | $0-$500B | $500B-$1T | >$1T |

**The Savings Depletion Sequence:** The personal saving rate is the fuel tank gauge. Pre-pandemic norm sat at ~7.5%. Pandemic stimulus drove it to 32% (April 2020), generating approximately $2.1T of excess savings. That buffer was drawn down through 2022-2025. Once the buffer is exhausted, consumers face a binary choice: cut spending or turn to credit. The saving rate below 5% combined with credit card balance growth above wage growth is the defining "Stage 2" configuration: buffer gone, credit substituting.

**Validation:** San Francisco Fed's excess savings tracker (Abdelrahman & Oliveira) is the authoritative source. Their methodology compares actual saving to the pre-pandemic trend line. When the stock hits zero, the "cushion" phase ends and consumer spending must be supported by either real income growth or additional leverage.

---

### C. CONSUMER CREDIT (The Accelerant and the Warning)

When savings run out, consumers turn to credit. Rising credit = spending maintained. Rising delinquencies = trouble ahead.

| **Indicator** | **FRED Code** | **Frequency** | **Lead/Lag** | **Interpretation** |
|---|---|---|---|---|
| **Consumer Credit Outstanding** | TOTALSL | Monthly | Coincident | Total consumer debt (ex-mortgage) |
| **Revolving Credit (Credit Cards)** | REVOLSL | Monthly | Coincident | Short-term, high-rate debt |
| **Nonrevolving Credit** | NONREVSL | Monthly | Coincident | Auto loans, student loans |
| **Credit Card Delinquency Rate** | DRCCLACBS | Quarterly | **Leading 3-6 mo** | Early stress signal |
| **Auto Loan Delinquency Rate** | NY Fed SCE | Quarterly | Coincident | Big-ticket stress (no FRED series; NY Fed Consumer Credit Panel) |
| **Consumer Loan Delinquency Rate** | DRCLACBS | Quarterly | Coincident | Broad consumer stress |
| **Credit Card Interest Rate** | TERMCBCCALLNS | Monthly | Coincident | Borrowing cost |
| **Credit Card Balances** | NY Fed (web) | Quarterly | Coincident | Revolving debt outstanding |

#### Derived Credit Metrics

| **Metric** | **Formula** | **Threshold** | **Signal** |
|---|---|---|---|
| **Credit Growth YoY%** | Current - Year Ago | >10% | Unsustainable acceleration |
| **Revolving/Nonrevolving Ratio** | Revolving / Nonrevolving | >0.35 | Credit card dependency high |
| **Delinquency Trend** | Current DQ - Year Ago | >+0.5 ppt | Stress building |
| **Debt Service Ratio** | Debt Payments / DPI | >10% | Stretched capacity |
| **Credit Impulse** | Change in Credit Growth YoY | <-3 ppts | Credit tightening |

#### Regime Thresholds: Consumer Credit

| **Indicator** | **Crisis** | **Stressed** | **Normal** | **Healthy** |
|---|---|---|---|---|
| **Credit Card Delinquency** | >5.0% | 3.5-5.0% | 2.5-3.5% | <2.5% |
| **Auto Delinquency** | >3.0% | 2.0-3.0% | 1.5-2.0% | <1.5% |
| **Credit Growth YoY%** | <0% or >12% | 0-3% or 8-12% | 3-6% | 6-8% |
| **Debt Service Ratio** | >12% | 10-12% | 8-10% | <8% |

**The Credit Substitution Signal:** Credit card delinquency below 2.5% is expansion-phase normal. The 3.0-3.5% band is "elevated but not crisis." Above 3.5% starts to constrain consumer spending through two channels: (1) direct balance sheet strain forcing reduced discretionary spend, and (2) tightened bank underwriting (lower credit limits, declined applications) that curtails future borrowing capacity.

The Stage 2 fingerprint is specific: credit card balance growth running materially above wage growth (consumers borrowing to maintain lifestyle), rising delinquencies at the bottom quartile of credit score, and Senior Loan Officer survey results showing banks tightening consumer credit standards. Watch for these three together. Any one in isolation is noise.

**Historical benchmark:** In the 2007-2008 cycle, credit card delinquency rose from 3.7% (Q4 2006) to 6.8% (Q2 2009). The inflection point preceded the consumer spending peak by ~4 quarters. In 2001, credit card delinquency inflected up 2 quarters before the recession began.

---

### D. CONSUMER CONFIDENCE (The Psychological Driver)

Confidence surveys measure **expectations**: what consumers plan to do, not what they've done. They lead spending by 1-3 months but are noisy, and since 2016 have become increasingly subject to partisan distortion (UMich especially, where expectations readings now swing 20+ points based on which party controls the White House).

| **Indicator** | **Source** | **Frequency** | **Lead/Lag** | **Interpretation** |
|---|---|---|---|---|
| **Conference Board Consumer Confidence** | Conf Board | Monthly | **Leads spending 1-3 mo** | Headline sentiment |
| **CB: Present Situation** | Conf Board | Monthly | Coincident | Current conditions |
| **CB: Expectations** | Conf Board | Monthly | **Leads recession 6-9 mo** | Future outlook (key signal) |
| **UMich Consumer Sentiment** | UMich | Monthly | Leads spending 1-2 mo | Alternative sentiment gauge |
| **UMich: Current Conditions** | UMich | Monthly | Coincident | Present assessment |
| **UMich: Expectations** | UMich | Monthly | Leading 2-4 mo | Forward-looking |
| **UMich: Buying Conditions (Durables)** | UMich | Monthly | **Leads durables 1-3 mo** | Big-ticket intentions |
| **Bloomberg Consumer Comfort** | Bloomberg | Weekly | Coincident | High-frequency pulse |

#### Derived Confidence Metrics

| **Metric** | **Formula** | **Threshold** | **Signal** |
|---|---|---|---|
| **Expectations-Present Spread** | Expectations - Present Situation | <-25 | Future pessimism (recession signal) |
| **Confidence Momentum** | Current - 6M Avg | <-10 | Rapid deterioration |
| **UMich-CB Divergence** | UMich Index - CB Index | >±15 | Unusual divergence |
| **Buying Conditions Gap** | Current - Historical Avg | <-20 | Demand destruction |

#### Regime Thresholds: Confidence

| **Indicator** | **Recessionary** | **Weak** | **Normal** | **Strong** |
|---|---|---|---|---|
| **CB Consumer Confidence** | <75 | 75-95 | 95-120 | >120 |
| **CB Expectations** | <70 | 70-85 | 85-105 | >105 |
| **UMich Sentiment** | <65 | 65-80 | 80-100 | >100 |
| **Expectations-Present Spread** | <-30 | -30 to -15 | -15 to +5 | >+5 |

**The Expectations-Present Spread Signal:** Conference Board's Expectations vs Present Situation divergence is the single most reliable leading indicator in the confidence complex. When Expectations drops below 80 while Present Situation remains elevated, the spread compresses to -40 or worse. This pattern (consumers feel fine today but dread tomorrow) has preceded every recession since 1970 by 6-12 months. The mechanism: consumers dial back discretionary commitments (vacation bookings, vehicle orders, home purchases) well before their current spending shows weakness, because those commitments flow from expected future income.

The partisan noise around headline confidence is real, but the Expectations-Present spread is less affected because both components move with partisanship. The differential stays informative even when levels drift with politics.

---

### E. LABOR INCOME PROXY (The Paycheck Reality)

The consumer's spending capacity ultimately derives from employment and wages. Track aggregate payroll income as the fundamental driver.

| **Indicator** | **FRED Code** | **Frequency** | **Lead/Lag** | **Interpretation** |
|---|---|---|---|---|
| **Aggregate Weekly Payrolls** | Derived | Monthly | Coincident | Employment × Hours × Wages |
| **Average Hourly Earnings** | CES0500000003 | Monthly | Coincident | Wage rate |
| **Average Weekly Hours** | AWHAETP | Monthly | **Leads payrolls 2-4 mo** | Hours worked |
| **Total Private Employment** | USPRIV | Monthly | Coincident | Job count |
| **Real Average Hourly Earnings** | Derived | Monthly | Coincident | Wage purchasing power |
| **Quits Rate** | JTSQUR | Monthly | **Leads income 6-9 mo** | Worker confidence in alternatives |

#### Derived Labor Income Metrics

| **Metric** | **Formula** | **Threshold** | **Signal** |
|---|---|---|---|
| **Aggregate Payroll Growth YoY%** | Emp × Hours × Wages YoY | <3% | Income stagnation |
| **Real Payroll Growth** | Nominal Payroll Growth - CPI | <0% | Real income declining |
| **Hours Contribution** | Hours YoY × Weight | <0% | Intensive margin contracting |
| **Wage Contribution** | Wages YoY × Weight | <3% | Wage growth fading |

#### Regime Thresholds: Labor Income

| **Indicator** | **Contraction** | **Stagnation** | **Normal** | **Strong** |
|---|---|---|---|---|
| **Aggregate Payroll YoY%** | <0% | 0-3% | 3-5% | >5% |
| **Real Payroll YoY%** | <-2% | -2% to +1% | +1% to +3% | >+3% |
| **Hours Growth YoY%** | <-1% | -1% to +1% | +1% to +2% | >+2% |
| **Real AHE YoY%** | <0% | 0-1% | 1-2% | >2% |

**The Aggregate Payrolls Decomposition:** Aggregate weekly payrolls equals employment × hours × wages. Each component can mask weakness in the others. Real aggregate payroll growth below +1% YoY is the recession-warning threshold. Monitor the three components separately: (1) employment growth trend (3M, 6M moving averages), (2) average weekly hours (leads payrolls 2-4 months), (3) wage growth (AHE YoY). When all three decelerate together, the income tailwind is fading and Stage 1 (savings drawdown) is the next pressure release valve.

**Cross-check with Labor Pillar:** When Labor Fragility Index (LFI) rises above +0.8 and aggregate real payroll growth drops below +1%, spending growth follows within 1-2 quarters. This is the core Labor → Income → Consumer transmission.

---

### F. HIGH-FREQUENCY SPENDING (The Real-Time Pulse)

Credit card data and alternative sources provide **weekly or even daily** spending reads, essential for nowcasting consumer activity in the gap between monthly retail sales and PCE releases.

| **Indicator** | **Source** | **Frequency** | **Lead/Lag** | **Interpretation** |
|---|---|---|---|---|
| **Bank of America Card Spending** | BofA | Weekly | Real-time | Total card spending (60M households) |
| **Chase Card Spending** | JPM | Weekly | Real-time | Alternative card data |
| **Redbook Retail Sales** | Redbook | Weekly | Coincident | Retail chain sales |
| **Johnson Redbook YoY%** | Redbook | Weekly | Coincident | Year-over-year comparison |
| **Restaurant Reservations (OpenTable)** | OpenTable | Daily | Coincident | Dining demand proxy |
| **TSA Checkpoint Data** | TSA | Daily | Coincident | Travel demand |
| **Box Office Revenue** | Box Office Mojo | Weekly | Coincident | Entertainment spending |
| **Gasoline Demand** | EIA | Weekly | Coincident | Driving activity |

#### Derived High-Frequency Metrics

| **Metric** | **Formula** | **Interpretation** |
|---|---|---|
| **Card Spending vs 2019** | Current / 2019 Level × 100 | Recovery benchmark |
| **Card Spending Momentum** | 4-wk Avg vs 13-wk Avg | Trend direction |
| **Discretionary/Staples Ratio** | Discretionary Spending / Staples | Consumer confidence proxy |
| **Travel vs Pre-Pandemic** | TSA / 2019 TSA × 100 | Travel normalization |

#### Regime Thresholds: High-Frequency

| **Indicator** | **Weak** | **Stable** | **Strong** |
|---|---|---|---|
| **Card Spending YoY%** | <2% | 2-6% | >6% |
| **Redbook YoY%** | <3% | 3-6% | >6% |
| **TSA vs 2019** | <95% | 95-105% | >105% |
| **Restaurant Reservations vs 2019** | <90% | 90-105% | >105% |

**The Composition Signal:** Aggregate card spending growth can stay positive while composition shifts tell a different story. The key divergence is discretionary vs staples growth: when electronics, apparel, and restaurants decelerate faster than groceries and utilities, consumers are trading down. The spread between discretionary-category YoY and staples-category YoY is a leaner signal than the headline card spending number, because it strips out price-level noise and reveals the behavioral shift.

**Category hierarchy in a consumer slowdown:**
1. **Discretionary big-ticket** (electronics, appliances): First to contract
2. **Restaurants and travel**: Second wave, 1-2 quarters later
3. **Apparel**: Contracts with discretionary
4. **Groceries (nominal)**: Remains positive even in recession (necessity)
5. **Utilities and rent**: Positive growth throughout (non-discretionary)

Watch the "trade-down winners": Walmart, Costco, dollar stores outperform during consumer stress, while Target, department stores, and mid-tier restaurants underperform.

---

### G. CONSUMER BALANCE SHEET (The Capacity Gauge)

The consumer's ability to spend depends on net worth (assets minus liabilities). Wealthy consumers spend more freely. Stressed consumers pull back.

| **Indicator** | **FRED Code** | **Frequency** | **Lead/Lag** | **Interpretation** |
|---|---|---|---|---|
| **Household Net Worth** | BOGZ1FL192090005Q | Quarterly | Lagging 1-2 qtrs | Total assets - liabilities |
| **Household Net Worth / DPI** | Derived | Quarterly | Lagging | Wealth-to-income ratio |
| **Household Debt / DPI** | HDTGPDUSQ163N | Quarterly | Lagging | Leverage ratio |
| **Household Debt Service Ratio** | TDSP | Quarterly | Coincident | Payment burden |
| **Financial Obligations Ratio** | FODSP | Quarterly | Coincident | Broader payment burden (discontinued but data through ~2024) |
| **Home Equity** | Z.1 Flow of Funds | Quarterly | Lagging | Housing wealth |
| **Stock Holdings** | Z.1 Flow of Funds | Quarterly | Lagging | Equity wealth |

#### Derived Balance Sheet Metrics

| **Metric** | **Formula** | **Threshold** | **Signal** |
|---|---|---|---|
| **Net Worth YoY%** | Current - Year Ago | <0% | Wealth destruction |
| **Debt/Income Trend** | Current Ratio - 5Y Avg | >+10 ppts | Leverage building |
| **Debt Service Burden Change** | Current DSR - Year Ago | >+1 ppt | Strain increasing |
| **Home Equity / Mortgage Debt** | Equity / Mortgage | <30% | Underwater risk |

#### Regime Thresholds: Balance Sheet

| **Indicator** | **Stressed** | **Stretched** | **Normal** | **Strong** |
|---|---|---|---|---|
| **Household Debt / DPI** | >110% | 95-110% | 80-95% | <80% |
| **Debt Service Ratio** | >13% | 11-13% | 9-11% | <9% |
| **Net Worth / DPI** | <600% | 600-750% | 750-850% | >850% |
| **Home Equity Share** | <20% | 20-35% | 35-50% | >50% |

**The Wealth Bifurcation Problem:** Aggregate household net worth routinely sits near record highs throughout cycles, including late-cycle periods. The problem is distribution. The top 10% hold roughly two-thirds of household wealth. The bottom 50% hold near-zero or negative net worth on average. When media or sell-side commentary cite "strong consumer balance sheet" using aggregate data, they are describing the top decile. The median consumer's balance sheet is tight.

This matters because the **marginal propensity to consume (MPC) is inversely correlated with wealth**. The bottom quintile spends 95%+ of each additional dollar. The top quintile spends 30-40%. Aggregate wealth is held by low-MPC households; aggregate spending is driven by high-MPC households. When bottom-quintile income or credit access tightens, spending drops fast even though aggregate wealth is "fine."

**The Kaplan-Violante HtM framework:** Research by Kaplan, Violante, and Weidner identifies "hand-to-mouth" households (both poor HtM and wealthy HtM who hold wealth in illiquid assets). Roughly 30% of US households are HtM and have MPCs of 15-25 cents per dollar on income shocks versus 5-10 cents for non-HtM. This is why the consumer can appear strong in aggregate right up to the moment it isn't.

---

### H. CONSUMER SEGMENTS (The Distributional Overview)

Not all consumers are equal. Income quintiles, age cohorts, and asset ownership create vastly different spending capacities. This section is the quick taxonomy. For granular segmentation with regime thresholds and derived metrics, see Section I.

| **Segment** | **Characteristics** | **Typical MPC** | **Cycle Behavior** |
|---|---|---|---|
| **Top Quintile (>$150k income)** | Stock-heavy wealth, low debt burden | 0.30-0.40 | Most resilient; late to cut, first to resume |
| **Upper-Middle ($100-$150k)** | Home equity wealth, moderate debt | 0.45-0.55 | Trading down early, cutting travel/dining |
| **Middle ($50-$100k)** | Some home equity, debt-service sensitive | 0.55-0.70 | Discretionary cuts first, staples held |
| **Bottom Two Quintiles (<$50k)** | Minimal buffer, high debt/income ratio | 0.80-0.95 | First to cut, broadest stress signals |
| **Gen Z (18-27)** | Entry-level wages, high student debt | 0.75-0.90 | Paycheck-to-paycheck baseline; BNPL-heavy |
| **Millennials (28-43)** | Peak earning, high housing/childcare costs | 0.60-0.75 | Housing cost pressure concentrated here |
| **Gen X (44-59)** | Dual-income peak, 401(k) accumulation | 0.50-0.65 | Home equity exposure, retirement anxiety |
| **Boomers (60-78)** | Retired or near-retired, drawing down assets | 0.35-0.50 | Social Security anchor; equity-wealth sensitive |

MPC = marginal propensity to consume (cents of each additional dollar of income spent, not saved).

#### Segment-Specific Metrics

| **Metric** | **Formula** | **Threshold** | **Signal** |
|---|---|---|---|
| **Bottom 50% Real Spending YoY%** | Segment-specific (NY Fed SCE, BofA) | <0% | Broad-based stress |
| **Prime-Age Spending Growth** | 25-54 cohort YoY | <1% | Core economy weak |
| **Luxury/Discount Spending Ratio** | Luxury category / Discount category | <0.8 | Trading down underway |
| **Buy Now Pay Later Usage** | BNPL volume YoY | >30% | Credit desperation in bottom quartile |
| **Top-Bottom Spending Spread** | Top quintile YoY - Bottom quintile YoY | >4 ppts | K-shaped cycle confirmed |

**The K-Shaped Consumer:** During late-cycle fragility, the top quintile often spends +3-4% YoY on travel, dining, and luxury while the bottom quintile cuts real spending. Aggregate PCE can remain positive even as the bottom half contracts, because the top half accounts for ~40% of spending despite being 20% of the population. Watch the "trading-down" tell: Walmart, Costco, and dollar stores gaining share while Target, department stores, and mid-tier casual dining lose. Aggregate data can mislead for 2-3 quarters before the top breaks too.

---

## Consumer Pillar Composite Index (CCI)

### Formula

The Consumer Pillar Composite synthesizes spending, income, credit, and confidence into a single consumer health indicator:

```
CCI = 0.25 × z(Real_PCE_YoY)
    + 0.20 × z(Personal_Saving_Rate)
    + 0.15 × z(Retail_Sales_Control_YoY)           # RSXFS (card spending proxy)
    + 0.10 × z(-Credit_Card_Delinquency)            # Inverted (high DQ = weak)
    + 0.10 × z(UMich_Sentiment)                     # Proxy for CB Expectations
    + 0.10 × z(Real_DPI_YoY)
    + 0.10 × z(-Debt_Service_Ratio)                 # Inverted (high DSR = weak)
```

**Component Weighting Rationale (validated via backtest, Feb 2026):**
- **Real PCE (25%):** The output variable. Highest forward correlation with own trajectory (-0.82 at 12M)
- **Saving Rate (20%):** Fuel tank gauge. Second-highest predictive power (+0.50 at 12M)
- **Retail Sales Control (15%):** High-frequency spending confirmation via RSXFS (Census). Third-most predictive (-0.50 at 12M). Replaces proprietary card spending data (not publicly available)
- **Credit Card Delinquency (10%):** Stress signal (inverted). Economically important but low empirical forward correlation (-0.11). Kept for structural logic
- **UMich Sentiment (10%):** Confidence proxy for CB Expectations (not on FRED). Downweighted from original 15% due to increasing partisan noise post-2016
- **Real DPI (10%):** Income driver of spending capacity
- **Debt Service Ratio (10%):** Balance sheet strain (inverted). Low forward correlation but captures mechanical repricing dynamics

**Weight validation:** Backtested against forward 6M and 12M PCE outcomes (2008-2025). Blended approach: 60% economic logic + 40% empirical correlation. See `/Users/bob/LHM/Scripts/chart_generation/cci_backtest.py` for full analysis.

### Interpretation

| **CCI Range** | **Regime** | **Discretionary Allocation** | **Signal** |
|---|---|---|---|
| > +1.0 | Consumer Boom | Overweight discretionary, travel | Full expansion |
| +0.5 to +1.0 | Healthy | Neutral discretionary | Sustainable growth |
| -0.5 to +0.5 | Neutral/Fatigued | Slight underweight discretionary | Deceleration |
| -1.0 to -0.5 | Stressed | **Underweight discretionary, overweight staples** | Demand destruction |
| < -1.0 | Crisis | Maximum defensive (staples, discount) | Recession confirmed |

### Historical Calibration

| **Period** | **CCI** | **Regime** | **Outcome (12M Forward)** |
|---|---|---|---|
| **Dec 2006** | +0.3 | Neutral | Consumer held through 2007, collapsed 2008 |
| **Dec 2007** | -0.4 | Stressed | Deep consumer recession confirmed |
| **Dec 2011** | +0.2 | Neutral | Slow recovery underway |
| **Dec 2019** | +0.7 | Healthy | Pre-COVID strength |
| **Dec 2020** | +0.5 | Healthy | Stimulus-fueled spending |
| **April 2021** | +1.8 | Boom | Peak stimulus, max spending |
| **Dec 2023** | +0.4 | Neutral | Savings depleting |
| **Dec 2025** | **-0.3** | **Fatigued** | **Stage 2 stress (credit)** |

**Current reading:** see "Current State Assessment Template" section below for the live CCI value, component scores, and regime classification.

---

## Lead/Lag Relationships: The Consumer Cascade

```
LEADING                           COINCIDENT                  LAGGING
────────────────────────────────────────────────────────────────────────────────────
│                                 │                          │
│  CB Expectations (6-9 mo)       │  Retail Sales            │  Consumer Credit (1-3 mo)
│  Quits Rate (6-9 mo→spending)   │  Real PCE                │  Delinquencies (3-6 mo)
│  Saving Rate (3-6 mo)           │  Card Spending           │  Charge-offs (6-9 mo)
│  Durable Goods Orders (2-4 mo)  │  Personal Income         │  Net Worth (1-2 qtrs)
│  UMich Buying Conditions (1-3)  │  Employment              │  Consumer Confidence Present
│  Initial Claims (1-2 mo)        │  Wages                   │  Household Debt Ratios
│  Credit Conditions Survey (2-4) │  Services Spending       │  GDP PCE Component
│  Home Price Changes (3-6 mo)    │                          │
│                                 │                          │
────────────────────────────────────────────────────────────────────────────────────
```

**The Critical Chain:**

**1. Labor deteriorates** (quits fall, claims rise) → 6-9 months later → **Income growth slows**
**2. Income slows + savings depleted** → 1-3 months later → **Credit usage spikes**
**3. Credit stress builds** (delinquencies rise) → 3-6 months later → **Spending cuts begin**
**4. Spending contracts** → 1-2 quarters later → **Corporate revenues fall, layoffs resume, reinforcing loop closes**

**Where we are now:** see the Stress Stage indicator in the Current State Assessment Template.

---

## Integration with Three-Engine Framework

### Pillar 5 → Pillar 1 (Labor)

Consumer spending drives **labor demand** through corporate revenue:

```
Consumer Spending ↓ → Corporate Revenue ↓ →
Profit Margins Squeezed → Cost Cutting ↓ →
Hiring Freeze → Layoffs → Income ↓ → Spending ↓ (Reinforcing)
```

**Transmission mechanics:** Consumer spending translates to corporate revenue with a 1-2 quarter lag. Revenue deceleration squeezes profit margins 1-2 quarters after that. Cost cutting then moves through hiring freeze → attrition → layoffs over another 2-4 months. The full loop closes within 3-4 quarters, then feeds back into consumer income through the layoffs channel.

**Cross-Pillar Signal:** When **CCI < -0.3** (consumer fatigued) AND **LFI > +0.8** (labor fragile), recession probability exceeds 65% within 12 months based on 1990-2020 backtests. This is the single most powerful two-pillar cross-check in the Diagnostic Dozen. Monitor the combined state.

---

### Pillar 5 → Pillar 2 (Prices)

Consumer demand drives **inflation** through demand-pull dynamics:

```
Consumer Spending ↑ → Demand Exceeds Supply →
Pricing Power ↑ → Inflation ↑
Consumer Spending ↓ → Demand Falls → Pricing Power ↓ → Inflation ↓
```

**Transmission mechanics:** Goods inflation responds faster than services. When consumer spending decelerates, goods disinflation appears within 1-2 quarters (inventory adjustments, price cuts to move merchandise). Services inflation is wage-linked and persists 2-4 quarters longer. The sequence is predictable: goods CPI rolls over first, core goods goes negative, then shelter disinflation follows (with Owners' Equivalent Rent lagging ~12 months behind market rents), and services ex-shelter comes last because it's tethered to wage growth.

**Cross-Pillar Signal:** Consumer weakness (**CCI < -0.3**) supports "last mile" inflation resolution. If spending cracks further, services inflation follows goods down with 2-3 quarter lag. Watch core services ex-shelter YoY (supercore) for the confirmation signal. That's the Fed's preferred gauge and the last component to break.

---

### Pillar 5 → Pillar 3 (Growth)

Consumer is **68% of GDP**, the dominant growth driver:

```
Consumer Spending Growth → PCE Contribution to GDP →
GDP Growth → Investment Response → Hiring → Consumer Income (Reinforcing)
```

**Transmission mechanics:** PCE's contribution to GDP is mechanical: real PCE YoY × 0.68 ≈ PCE's contribution to real GDP growth. A 1 ppt change in real PCE translates to roughly 0.7 ppts of GDP. This makes the consumer the dominant swing factor in any cycle. Business investment, government spending, and net exports together account for the other 32%, and they typically amplify rather than offset consumer moves (investment is pro-cyclical, tax receipts fall when incomes fall, imports fall when spending falls).

**Cross-Pillar Signal:** When **CCI < -0.5** (consumer stressed) AND **GCI < -0.5** (growth contracting), recession is confirmed. The synchronization of these two composites is the most reliable single confirmation in the framework. Both negative, sustained for 2+ quarters, has preceded every post-1990 recession.

---

### Pillar 5 → Pillar 4 (Housing)

Consumer confidence drives **housing demand**:

```
Consumer Confidence ↑ → Home Buying Intentions ↑ →
Housing Demand ↑ → Home Sales ↑ → Home Prices ↑ →
Wealth Effect ↑ → Consumer Spending ↑ (Reinforcing)
```

**Transmission mechanics:** Housing demand is rate-sensitive and confidence-sensitive. The wealth effect operates in both directions: rising home prices lift consumer spending (home equity extraction, confidence channel), and falling prices depress spending. Historical estimates put the housing wealth elasticity at roughly 5-8 cents per dollar of home equity change, materially higher than the financial wealth elasticity of 2-4 cents. This is because housing wealth is more broadly distributed than financial wealth (more HtM households hold home equity than stocks).

**Cross-Pillar Signal:** Housing transactions normalize when **CCI > +0.3** AND mortgage rates < 6%. Both conditions must hold. Rates alone (without confidence) don't catalyze a thaw because buyers read declining rates as a recession signal, not a buying opportunity. Confidence alone (without rates) doesn't help because affordability math still fails.

---

### Pillar 5 → Pillar 9 (Financial)

Consumer credit health affects **bank balance sheets**:

```
Consumer Delinquencies ↑ → Bank Loan Losses ↑ →
Bank Capital Impairment → Credit Tightening →
Consumer Credit Availability ↓ → Spending ↓ (Reinforcing)
```

**Transmission mechanics:** Credit card and auto loan delinquencies hit bank P&L through two channels: (1) direct loan loss provisions (charge-offs flow through income statement), and (2) tightened underwriting standards as risk management responds to rising losses. The second channel is more consequential for the consumer because it constrains future borrowing capacity just as the buffer is most needed. Regional banks are more exposed than money-centers to consumer and small business lending, which is why consumer stress shows up in regional bank stock performance and deposit behavior before money-center bank earnings.

**Cross-Pillar Signal:** Consumer credit stress (**CCI < -0.5**) combined with bank stress (**credit spreads widening, SLOOS tightening**) creates a negative feedback loop. Monitor for simultaneous deterioration. The Senior Loan Officer Opinion Survey (SLOOS) consumer credit standards net tightening result above +15% is a reliable confirmation signal.

---

## Data Source Summary

| **Category** | **Primary Source** | **Frequency** | **Release Lag** | **FRED Availability** |
|---|---|---|---|---|
| **PCE** | BEA | Monthly | ~30 days | Same day (PCE, PCEC96) |
| **Retail Sales** | Census | Monthly | ~14 days | Same day (RSXFS) |
| **Personal Income** | BEA | Monthly | ~30 days | Same day (PI, DPI) |
| **Consumer Credit** | Fed G.19 | Monthly | ~5 weeks | Same day (TOTALSL) |
| **Delinquencies** | Fed | Quarterly | ~45 days | Same day (DRCCLACBS) |
| **CB Confidence** | Conference Board | Monthly | Last Tuesday | Web scrape |
| **UMich Sentiment** | UMich | Monthly | Prelim ~15th, final ~25th | Same day (UMCSENT) |
| **Card Spending** | Banks | Weekly | ~5 days | Proprietary (BofA, JPM) |
| **Household Balance Sheet** | Fed Z.1 | Quarterly | ~70 days | Same day (multiple) |

**Critical Timing:** Retail sales released mid-month (~14th) is the **highest-frequency official gauge**. Use weekly card data (BofA, JPM) for real-time nowcasting. PCE released end-of-month confirms what retail already showed.

---

## Current State Assessment Template

*Last Updated: {{DATE}}*

### Primary Indicators

| **Indicator** | **Current** | **Prior** | **Δ** | **Threshold** | **Assessment** |
|---|---|---|---|---|---|
| **Real PCE YoY%** | {{REAL_PCE_YOY}} | {{REAL_PCE_YOY_PRIOR}} | {{REAL_PCE_DELTA}} | <1.5% = Stagnation | {{REAL_PCE_ASSESSMENT}} |
| **Real PCE Momentum (3M - 12M)** | {{PCE_MOMENTUM}} | {{PCE_MOMENTUM_PRIOR}} | {{PCE_MOMENTUM_DELTA}} | <-1 ppt = Decelerating | {{PCE_MOMENTUM_ASSESSMENT}} |
| **Personal Saving Rate** | {{SAVING_RATE}} | {{SAVING_RATE_PRIOR}} | {{SAVING_RATE_DELTA}} | <5.0% = Depleted | {{SAVING_RATE_ASSESSMENT}} |
| **Real DPI YoY%** | {{REAL_DPI_YOY}} | {{REAL_DPI_YOY_PRIOR}} | {{REAL_DPI_DELTA}} | <1.5% = Squeezed | {{REAL_DPI_ASSESSMENT}} |
| **Credit Card Delinquency** | {{CC_DELINQ}} | {{CC_DELINQ_PRIOR}} | {{CC_DELINQ_DELTA}} | >3.5% = Stressed | {{CC_DELINQ_ASSESSMENT}} |
| **Debt Service Ratio** | {{DSR}} | {{DSR_PRIOR}} | {{DSR_DELTA}} | >11% = Stretched | {{DSR_ASSESSMENT}} |
| **CB Expectations** | {{CB_EXPECTATIONS}} | {{CB_EXPECTATIONS_PRIOR}} | {{CB_EXPECTATIONS_DELTA}} | <80 = Recession signal | {{CB_EXPECTATIONS_ASSESSMENT}} |
| **UMich Sentiment** | {{UMICH}} | {{UMICH_PRIOR}} | {{UMICH_DELTA}} | <70 = Weak | {{UMICH_ASSESSMENT}} |
| **Real Retail Sales YoY%** | {{REAL_RETAIL_YOY}} | {{REAL_RETAIL_YOY_PRIOR}} | {{REAL_RETAIL_DELTA}} | <0% = Contraction | {{REAL_RETAIL_ASSESSMENT}} |
| **Durable Goods PCE YoY%** | {{DURABLES_YOY}} | {{DURABLES_YOY_PRIOR}} | {{DURABLES_DELTA}} | <-5% = Discretionary collapse | {{DURABLES_ASSESSMENT}} |
| **Card Spending YoY%** | {{CARD_SPEND_YOY}} | {{CARD_SPEND_YOY_PRIOR}} | {{CARD_SPEND_DELTA}} | <2% = Weak | {{CARD_SPEND_ASSESSMENT}} |
| **Luxury/Discount Ratio** | {{LUX_DISC_RATIO}} | {{LUX_DISC_RATIO_PRIOR}} | {{LUX_DISC_DELTA}} | <0.8 = Trading down | {{LUX_DISC_ASSESSMENT}} |

### Composites

| **Index** | **Current** | **Prior** | **Regime** | **Signal** |
|---|---|---|---|---|
| **CCI** | {{CCI}} | {{CCI_PRIOR}} | {{CCI_REGIME}} | {{CCI_SIGNAL}} |
| **Segmented CCI (Bottom 50%)** | {{CCI_BOTTOM50}} | {{CCI_BOTTOM50_PRIOR}} | {{CCI_BOTTOM50_REGIME}} | {{CCI_BOTTOM50_SIGNAL}} |
| **Stress Stage (1-4)** | {{STRESS_STAGE}} | {{STRESS_STAGE_PRIOR}} | {{STRESS_STAGE_REGIME}} | {{STRESS_STAGE_SIGNAL}} |

### Cross-Pillar Linkages

| **Linkage** | **Current** | **Threshold** | **Status** |
|---|---|---|---|
| **CCI + LFI (Labor-Consumer)** | {{CCI_LFI}} | CCI <-0.3 AND LFI >+0.8 = 65%+ recession probability | {{CCI_LFI_STATUS}} |
| **CCI + GCI (Growth sync)** | {{CCI_GCI}} | Both <-0.5 = Recession confirmed | {{CCI_GCI_STATUS}} |
| **Consumer → PCI transmission** | {{CCI_PCI}} | CCI weakness → services disinflation 3-6 mo | {{CCI_PCI_STATUS}} |
| **Wealth effect (net worth Δ × CCI)** | {{WEALTH_EFFECT}} | Negative wealth Δ + CCI <0 = spending cut catalyst | {{WEALTH_EFFECT_STATUS}} |

### Narrative Synthesis

{{NARRATIVE}}

**Translation:** {{TRANSLATION}}

**Cross-Pillar Confirmation:**
- **Labor Pillar:** {{LABOR_CONFIRMATION}}
- **Prices Pillar:** {{PRICES_CONFIRMATION}}
- **Housing Pillar:** {{HOUSING_CONFIRMATION}}
- **Growth Pillar:** {{GROWTH_CONFIRMATION}}
- **Financial Pillar:** {{FINANCIAL_CONFIRMATION}}

**Stress Stage Diagnosis:**
1. Savings depleted: {{STAGE1_STATUS}}
2. Credit stress building: {{STAGE2_STATUS}}
3. Spending cuts: {{STAGE3_STATUS}}
4. Recession confirmed: {{STAGE4_STATUS}}

**MRI Contribution:** {{MRI_CONTRIBUTION}}

---

## Invalidation Criteria

### Bull Case (Consumer Resilience) Invalidation Thresholds

If the following occur **simultaneously for 3+ months**, the bearish consumer thesis is invalidated:

✅ **Personal Saving Rate** rises above **6.0%** (buffer rebuilding)
✅ **Credit Card Delinquency** drops below **2.5%** (stress fading)
✅ **Real PCE YoY%** exceeds **3.0%** (acceleration)
✅ **CB Expectations** exceeds **90** (optimism returning)
✅ **Real DPI YoY%** exceeds **2.5%** (income growth supporting spending)
✅ **CCI** exceeds **+0.5** (healthy regime)

**Action if Invalidated:** Rotate to **consumer discretionary** (XLY), **travel/leisure** (PEJ), **retail** (XRT). Consumer strength = cyclical outperformance.

---

### Bear Case (Consumer Collapse) Confirmation Thresholds

If the following occur, consumer is **deteriorating beyond fatigued into crisis**:

🔴 **Real PCE YoY%** turns **negative** (spending contraction)
🔴 **Personal Saving Rate** drops below **3.0%** (desperation)
🔴 **Credit Card Delinquency** exceeds **4.5%** (credit crisis)
🔴 **CB Expectations** drops below **65** (deep pessimism)
🔴 **Retail Sales 3M Avg** turns **negative** (demand destruction)
🔴 **CCI** drops below **-1.0** (crisis regime)

**Action if Confirmed:** Maximum defensive. Overweight **consumer staples** (XLP), **discount retail** (WMT, COST, DG), **utilities** (XLU). Avoid all discretionary exposure.

---

## Conclusion: The Consumer as the Last Domino

The consumer isn't a leading indicator. It's the **68% of GDP that confirms what everything else already said**.

When quits collapse (6-9 months before), credit stress builds (3-6 months before), and confidence craters (1-3 months before), the consumer **eventually** follows. By the time retail sales go negative, the recession is already underway.

**Current State:**
- **CCI -0.39** (Fatigued Regime)
- **Real PCE +2.1% YoY** (decelerating, not contracting)
- **Saving rate 4.5%** (depleted, no buffer)
- **Credit card delinquency 3.0%** (Stage 2 stress)
- **CB Expectations 78** (below recession threshold)
- **Durables -1.8% YoY** (discretionary already contracting)

**The Sequence:**
1. **Savings depleted** (Stage 1): saving rate falls below pre-pandemic norm, excess savings stock exhausted
2. **Credit stress building** (Stage 2): delinquencies rising, balance growth outpacing wages, DSR elevated
3. **Spending cuts** (Stage 3): durables contracting first, services rolling over
4. **Recession confirmed** (Stage 4): real PCE YoY negative, retail sales contracting

**Cross-Pillar Context:** Consumer fatigue (**CCI -0.39**) + labor fragility (**LFI +0.93**) + growth weakness (**GCI -0.4**) = **MRI +1.1** (HIGH RISK regime).

The consumer hasn't cracked. But the cracks are visible. The wealthy are holding up the aggregate. The median consumer is stressed. When the last domino falls, everyone will see what the labor data said 9 months ago.

**That's our view from the Watch. Until next time, we'll be sure to keep the light on....**

---

## FRED Series Reference Appendix

All FRED series codes referenced in this pillar, organized by category. Pipeline source: `Lighthouse_Master.db` via `lighthouse_master_db.py`.

### Spending Flows (Section A)

| **Series ID** | **Description** | **Frequency** |
|---|---|---|
| PCE | Personal Consumption Expenditures (Nominal) | Monthly |
| PCEC96 | Real Personal Consumption Expenditures | Monthly |
| DGDSRC1 | Personal Consumption Expenditures: Goods (Nominal) | Monthly |
| PCDG | Personal Consumption Expenditures: Durable Goods | Monthly |
| PCND | Personal Consumption Expenditures: Nondurable Goods | Monthly |
| PCESV | Personal Consumption Expenditures: Services | Monthly |
| RSXFS | Advance Retail Sales: Retail and Food Services (Ex Food Services) | Monthly |
| RSFSXMV | Advance Retail Sales: Retail and Food Services Ex Motor Vehicles | Monthly |

### Income & Savings (Section B)

| **Series ID** | **Description** | **Frequency** |
|---|---|---|
| PI | Personal Income | Monthly |
| DPI | Disposable Personal Income | Monthly |
| DSPIC96 | Real Disposable Personal Income | Monthly |
| A576RC1 | Compensation of Employees: Wages and Salaries | Monthly |
| PSAVE | Personal Saving | Monthly |
| PSAVERT | Personal Saving Rate | Monthly |
| A229RX0 | Real Disposable Personal Income: Per Capita | Monthly |
| A063RC1 | Personal Current Transfer Receipts: Government Social Benefits | Monthly |

### Consumer Credit (Section C)

| **Series ID** | **Description** | **Frequency** |
|---|---|---|
| TOTALSL | Total Consumer Credit Outstanding | Monthly |
| REVOLSL | Revolving Consumer Credit Owned and Securitized | Monthly |
| NONREVSL | Nonrevolving Consumer Credit Owned and Securitized | Monthly |
| DRCCLACBS | Delinquency Rate on Credit Card Loans, All Commercial Banks | Quarterly |
| DRCLACBS | Delinquency Rate on Consumer Loans, All Commercial Banks | Quarterly |
| TERMCBCCALLNS | Commercial Bank Interest Rate on Credit Card Plans, All Accounts | Monthly |

### Consumer Confidence (Section D)

| **Series ID** | **Description** | **Frequency** |
|---|---|---|
| UMCSENT | University of Michigan Consumer Sentiment | Monthly |

### Labor Income Proxy (Section E)

| **Series ID** | **Description** | **Frequency** |
|---|---|---|
| CES0500000003 | Average Hourly Earnings of All Employees, Total Private | Monthly |
| AWHAETP | Average Weekly Hours of All Employees, Total Private | Monthly |
| USPRIV | All Employees, Total Private | Monthly |
| JTSQUR | Quits Rate: Total Private | Monthly |

### Consumer Balance Sheet (Section G)

| **Series ID** | **Description** | **Frequency** |
|---|---|---|
| BOGZ1FL192090005Q | Households and Nonprofit Organizations: Net Worth, Level | Quarterly |
| HDTGPDUSQ163N | Household Debt to GDP for United States | Quarterly |
| TDSP | Household Debt Service Payments as Percent of DPI | Quarterly |
| FODSP | Household Financial Obligations as Percent of DPI (discontinued) | Quarterly |

### Non-FRED Data Sources

| **Indicator** | **Source** | **Notes** |
|---|---|---|
| Conference Board Consumer Confidence | Conference Board | Not on FRED; web scrape or subscription |
| Auto Loan Delinquency Rate | NY Fed Consumer Credit Panel | Not on FRED by loan type; quarterly SCE reports |
| Retail Sales Control Group | Census Bureau | No clean FRED series ID; derived from Census advance retail report |
| Bank of America Card Spending | BofA Research | Proprietary, weekly |
| Chase Card Spending | JPMorgan | Proprietary, weekly |
| Redbook Retail Sales | Redbook Research | Weekly, available via some data vendors |
| Credit Card Balances | NY Fed Quarterly Report on Household Debt | Quarterly |
| OECD Consumer Confidence (US proxy) | FRED: CSCICP03USM665S | Monthly, can proxy for Conference Board when needed |

---

*Bob Sheehan, CFA, CMT*
*Founder & CIO, Lighthouse Macro*
*Last Updated: February 2026*
