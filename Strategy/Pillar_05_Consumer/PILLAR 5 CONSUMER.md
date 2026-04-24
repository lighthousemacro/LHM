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

## I. INCOME SEGMENTATION DEEP DIVE (Quintile Analysis)

Headlines lie about consumer strength because they report means, not distributions. True consumer analysis requires decomposing the aggregate into income cohorts. This is where stress emerges first, and where the richest leading signals live.

### The Segmentation Hierarchy

Different income cohorts exhibit different cyclical sensitivities:

```
LEADING (First to show stress)           LAGGING (Last to show stress)
─────────────────────────────────────────────────────────────────────────
Bottom Quintile                          Top Quintile
Gen Z / Young Millennials                Gen X / Boomers
Renters                                  Homeowners
Hourly Wage Workers                      Salaried Professionals
High-DTI Households                      Low-DTI Households
```

**The Insight:** When bottom-quintile spending and credit metrics deteriorate while top-quintile spending remains positive, you're witnessing the early stages of a consumer turn. By the time top quintile stress appears, recession is already underway.

### A. INCOME QUINTILE SPENDING

Income quintile spending data comes from three primary sources: BLS Consumer Expenditure Survey (quarterly, ~6-month lag), NY Fed Survey of Consumer Expectations (monthly, real-time), and bank card data disaggregated by ZIP code income (BofA, Chase, weekly).

| **Quintile** | **Annual Income Band** | **Share of Spending** | **Wealth Position** | **Cycle Behavior** |
|---|---|---|---|---|
| **Top 20%** | >$160k | ~39% | Top 10% holds ~67% of wealth | Resilient; discretionary holds longest |
| **Fourth 20%** | $100-$160k | ~23% | Home equity concentrated | Trading down mid-cycle |
| **Middle 20%** | $60-$100k | ~16% | Modest home equity, debt-service sensitive | Discretionary cuts first |
| **Second 20%** | $30-$60k | ~13% | Minimal wealth, some housing | Broad pullback, staples only |
| **Bottom 20%** | <$30k | ~9% | Negative median net worth | First to cut; BNPL-dependent |

Income bands shift with wage inflation. Ranges reflect approximate 2024-2025 US cutoffs.

#### Derived Income Distribution Metrics

| **Metric** | **Formula** | **Threshold** | **Signal** |
|---|---|---|---|
| **Top-Bottom Spending Spread** | Q5 YoY - Q1 YoY | >4 ppts | K-shaped divergence |
| **Bottom-40 Real Spending YoY** | (Q1+Q2)/2 real spend YoY | <0% | Median consumer contracting |
| **Spending Concentration Index** | Q5 spending share growth YoY | Rising | Top-heavy growth (late-cycle) |
| **Quintile Delinquency Gap** | Q1 CC DQ - Q5 CC DQ | >3 ppts | Bifurcation widening |

#### Regime Thresholds: Income Quintile Spending

| **Cohort** | **Healthy** | **Neutral** | **Stressed** | **Crisis** |
|---|---|---|---|---|
| **Bottom Quintile Real YoY** | >+1% | 0 to +1% | -1% to 0% | <-1% |
| **Middle Quintile Real YoY** | >+2% | +1% to +2% | 0% to +1% | <0% |
| **Top Quintile Real YoY** | >+3% | +1.5% to +3% | 0% to +1.5% | <0% |
| **Top-Bottom Spread** | <2 ppts | 2-4 ppts | 4-6 ppts | >6 ppts |

**The Bifurcation Pattern:** Top-Bottom spending spreads exceeding 4 ppts are characteristic of late-cycle consumer markets. The spread widens further into recession before compressing as the top finally cuts too. Watch the inflection in the top quintile (positive-to-negative YoY) as the final consumer confirmation signal.

### B. AGE COHORT SPENDING

Age-based spending patterns are driven by life-cycle position, wealth accumulation, and housing costs. Different cohorts weather cycles differently.

| **Cohort** | **Age Band** | **Key Financial Drivers** | **Cycle Sensitivity** |
|---|---|---|---|
| **Gen Z** | 18-27 | Entry wages, student debt, no home equity | Very high; first to cut |
| **Younger Millennials** | 28-35 | Career earnings ramp, high rent, childcare | High; housing cost pressure |
| **Older Millennials** | 36-43 | Peak childcare costs, first homes | High; DTI-constrained |
| **Gen X** | 44-59 | Dual-income peak, 401(k) accumulation | Moderate; wealth-effect sensitive |
| **Younger Boomers** | 60-70 | Late-career or early-retired, SS + 401(k) | Moderate; equity-wealth sensitive |
| **Older Boomers / Silent** | 71+ | Drawing down assets, fixed income | Low; Social Security anchor |

#### Derived Age Metrics

| **Metric** | **Formula** | **Threshold** | **Signal** |
|---|---|---|---|
| **Gen Z-Boomer Spending Spread** | Gen Z YoY - Boomer YoY | <-3 ppts | Young cohort stressed |
| **Millennial Housing Stress** | Rent-burdened share (>30% income) | >50% | Housing cost trap |
| **Prime-Working-Age Real YoY** | (28-54) real spend YoY | <+1% | Core economy weak |

**The Millennial Housing Trap:** Millennials (28-43) carry disproportionate housing cost burden because they bought homes late in the 2010s-2020s rate cycle or are still renters in expensive metros. When mortgage rates stay above 6%, their spending capacity is more constrained than aggregate income would suggest. Track the rent-burdened share (households spending >30% of income on housing) as a millennial-specific stress gauge.

### C. HOUSING TENURE SPENDING

Homeowners and renters behave differently through cycles due to wealth-effect asymmetry and rent-versus-mortgage cost structure.

| **Tenure** | **Share of Households** | **Wealth Exposure** | **Cycle Behavior** |
|---|---|---|---|
| **Owners with Mortgage** | ~40% | Home equity + stock market | Wealth-effect sensitive; DTI-driven |
| **Owners Free & Clear** | ~25% | Home equity only | Most resilient |
| **Renters** | ~35% | No housing wealth | Rent-burden sensitive; fastest to cut |

#### Tenure Metrics

| **Metric** | **Source** | **Threshold** | **Signal** |
|---|---|---|---|
| **Renter Spending YoY (real)** | NY Fed SCE / ACS | <0% | Renter cohort in contraction |
| **Rent-Burden Share** | ACS / HUD | >50% (for metro) | Housing cost crisis |
| **Owner Wealth Effect (home equity ΔYoY × 0.07)** | Z.1 | <0 (contribution to PCE) | Negative wealth effect engaged |

**Housing Wealth Elasticity:** Carroll, Otsuka, and Slacalek estimate long-run MPC out of housing wealth at 5-8 cents per dollar (vs 2-4 cents for financial wealth). This asymmetry matters: when home equity contracts, the spending response from the median homeowner is larger than equivalent stock wealth loss, because more consumers own homes than stocks and the MPC-weighted wealth distribution favors housing.

---

## J. GEOGRAPHIC SEGMENTATION (Where the Stress Concentrates)

National data obscures regional variation. Consumer conditions vary substantially across states and metros, and regional divergence often precedes national turns. Sun Belt growth states behave differently from Rust Belt manufacturing states, which behave differently from coastal tech/finance metros.

### State-Level Consumer Indicators

Multiple state-level consumer data sources exist. None are as clean as FRED headline series, but combined they produce a workable regional picture.

| **Series** | **Source** | **Frequency** | **Geographic Level** |
|---|---|---|---|
| **State Retail Sales (estimated)** | BEA + Census | Quarterly | State |
| **State Personal Income** | BEA | Quarterly (SAGDP/SAINC) | State |
| **State Unemployment Rate** | BLS LAUS | Monthly | State + Metro |
| **Credit Card Delinquency by State** | NY Fed Consumer Credit Panel | Quarterly | State |
| **Auto Delinquency by State** | NY Fed CCP | Quarterly | State |
| **State Coincident Index** | Philadelphia Fed | Monthly | State |
| **BofA/JPM Card Spending by Metro** | Banks | Weekly | Metro |

### Regional Consumer Patterns

| **Region** | **Key States** | **Economic Drivers** | **Consumer Cycle Behavior** |
|---|---|---|---|
| **Sun Belt Growth** | TX, FL, AZ, GA, NC | Housing, services, migration | High cyclicality; housing-linked |
| **Rust Belt** | OH, MI, PA, IN | Manufacturing, auto | Goods-linked; first to weaken in industrial cycles |
| **Coastal Tech** | CA, WA, MA | Tech compensation, equity wealth | Wealth-effect sensitive; equity volatility pass-through |
| **Northeast Finance** | NY, NJ, CT | Financial services | Financial-conditions sensitive |
| **Energy Belt** | TX, ND, OK, WV, LA | Oil & gas | Commodity-price linked |
| **Agricultural Midwest** | IA, NE, KS, MN | Ag commodities, processing | Commodity cycles; slower but deep |

#### Derived Geographic Metrics

| **Metric** | **Formula** | **Threshold** | **Signal** |
|---|---|---|---|
| **State Consumer Diffusion** | % of states with rising card DQ (3M) | >60% | Broad-based stress |
| **Regional Divergence** | StdDev of state retail sales YoY | >2 ppts | Uneven conditions |
| **Sun Belt Migration Spread** | Sun Belt YoY - National YoY | >+2 ppts | Migration-driven outperformance |
| **Rust Belt Spread** | Rust Belt avg - National | <-1 ppt | Manufacturing-led consumer weakness |

**State Diffusion Thresholds:**

| **Diffusion Level** | **% States Rising DQ** | **Interpretation** |
|---|---|---|
| **Localized** | <30% | State-specific issues |
| **Spreading** | 30-50% | Weakness gaining traction |
| **Broad-Based** | 50-70% | National downturn underway |
| **Pervasive** | >70% | Deep consumer recession |

**Historical Pattern:** In the 2008 consumer cycle, credit card delinquency rose in 30 of 50 states by mid-2007, 9-12 months before the national headline. Geographic diffusion is a leading signal because local labor markets, housing markets, and banking conditions vary, so stress appears unevenly before becoming national.

---

## K. CATEGORY DEEP DIVE (What Consumers Are Cutting First)

The composition of spending reveals more than the level. When consumers cut, they cut in a predictable order. Tracking category-level spending provides early confirmation of stress building beneath aggregate growth.

### Category Hierarchy in a Consumer Slowdown

```
FIRST TO CUT                                         LAST TO CUT
─────────────────────────────────────────────────────────────────────
Luxury discretionary (watches, jewelry, high-end restaurants)
Travel and leisure (airfare, hotels, cruises)
Durable big-ticket (vehicles, appliances, electronics)
Mid-tier discretionary (apparel, casual dining)
Home improvement / furniture
Entertainment and subscriptions
Beauty and personal care
Groceries (volume, composition shifts to value brands)
Gasoline and utilities (necessity, inelastic)
Rent / mortgage (contractual, cut last)
─────────────────────────────────────────────────────────────────────
```

### Category-Level Indicators

| **Category** | **Primary Indicator** | **Source** | **Cycle Role** |
|---|---|---|---|
| **Vehicles** | Total Light Vehicle Sales (TOTALSA) | FRED | Big-ticket leading indicator |
| **Home Improvement** | Home Depot / Lowe's same-store sales | Company reports | Mid-cycle housing-linked |
| **Travel** | TSA checkpoint volume vs 2019 | TSA | Real-time discretionary |
| **Restaurants** | OpenTable reservations, NRA sales | OpenTable, NRA | Discretionary leading |
| **Apparel** | Retail sales apparel (RSCCAS) | Census | Discretionary coincident |
| **Electronics** | Retail sales electronics/appliances | Census | Durable discretionary |
| **Luxury** | LVMH / Richemont / Kering sales | Company reports | Top-quintile health |
| **Grocery** | Retail sales food/beverage stores | Census | Staples baseline |
| **Dollar Stores** | Dollar General / Tree same-store sales | Company reports | Trading-down tell |
| **Subscriptions** | Streaming churn, gym membership churn | Industry reports | Discretionary resilience |

### Derived Category Metrics

| **Metric** | **Formula** | **Threshold** | **Signal** |
|---|---|---|---|
| **Discretionary-Staples Spread** | Discretionary YoY - Staples YoY | <0 ppts | Trading down active |
| **Luxury-Discount Spread** | Luxury YoY - Discount YoY | <0 ppts | K-shape broken (top cutting too) |
| **Vehicle Sales Momentum** | 3M Avg - 12M Avg SAAR | <-500k | Big-ticket contraction |
| **Travel vs 2019 Index** | TSA / 2019 TSA × 100 | <95 | Travel demand weakening |
| **Restaurant vs Grocery** | Restaurant sales YoY - Grocery YoY | <-2 ppts | Eating-out pullback |

**The Luxury Canary:** Luxury spending is unusual because it tracks top-quintile wealth, not income. Falls in luxury sales lag consumer weakness by 1-3 quarters but are more definitive: when LVMH/Richemont warn on earnings, the top quintile has finally engaged in trading-down behavior. This is typically the final confirmation that the consumer cycle has completed.

**Buy Now Pay Later (BNPL) as a Stress Signal:** BNPL (Affirm, Klarna, Afterpay, Apple Pay Later) volume has become a meaningful stress gauge for bottom-quartile consumers. Rapid BNPL growth alongside credit card delinquency rising indicates "phantom debt" accumulation outside traditional credit bureau tracking. CFPB and NY Fed track BNPL aggregate volume. YoY growth above 30% combined with rising default rates on primary credit products signals bottom-quartile financial desperation.

---

## L. RETAILER SIZE DYNAMICS (Trade-Down Winners and Losers)

Large retailers and small retailers behave differently through consumer cycles. The competitive landscape shifts predictably as consumers respond to stress.

### The Trade-Down Hierarchy

Consumer spending does not disappear during a slowdown. It migrates across retailer tiers:

```
PREMIUM (lose share in slowdowns)        VALUE (gain share in slowdowns)
───────────────────────────────────────────────────────────────────────
Whole Foods, specialty grocers  ────▶  Walmart, Kroger, Aldi
Target, department stores       ────▶  Walmart, Costco, BJ's
Casual dining (Chili's, OG)     ────▶  Fast food (McDonald's)
Specialty apparel               ────▶  Mass merchants, resale
Prestige beauty                 ────▶  Drugstore beauty, Amazon
Brand-name grocery              ────▶  Private label
Home Depot / Lowe's             ────▶  Deferred maintenance, DIY
Apple / premium electronics     ────▶  Android, used, trade-in
───────────────────────────────────────────────────────────────────────
```

### Public Company Retailer Indicators

| **Retailer Category** | **Representative Names** | **Role in Cycle** |
|---|---|---|
| **Mass Value** | WMT, COST, BJ | Trade-down winners |
| **Deep Discount** | DG, DLTR, FIVE | Bottom-quartile barometer |
| **Mid-Tier Mass** | TGT, KSS, M | Trade-down losers |
| **Specialty Discretionary** | LULU, RH, WSM | Early cyclical indicators |
| **Luxury** | LVMH, CPRI, TPR | Top-quintile health |
| **Off-Price** | TJX, ROST, BURL | Counter-cyclical beneficiaries |
| **Home Improvement** | HD, LOW | Mid-cycle housing-linked |
| **Restaurants (QSR)** | MCD, YUM, CMG | Consumer staples-like |
| **Restaurants (casual)** | DRI, EAT, TXRH | Discretionary coincident |

### Derived Retailer Metrics

| **Metric** | **Formula** | **Threshold** | **Signal** |
|---|---|---|---|
| **Walmart-Target SSS Spread** | WMT SSS YoY - TGT SSS YoY | >+3 ppts | Trade-down active |
| **Off-Price vs Department Spread** | TJX SSS - department avg | >+5 ppts | Value-seeking accelerating |
| **Dollar Store SSS** | DG + DLTR SSS YoY | >+5% | Bottom-quartile stress |
| **Luxury-Discount Spread** | LVMH - WMT SSS | Narrowing | K-shape compressing |
| **Restaurant Spread** | QSR SSS - Casual SSS | >+2 ppts | Trading down in food |

**The Walmart-Target Signal:** The spread between Walmart and Target same-store sales is one of the cleanest real-time trade-down gauges available. Pre-2022, the two companies had similar SSS growth. When Walmart accelerates while Target decelerates (or contracts), the middle-class consumer is trading down. This signal has preceded retail earnings compression by 1-2 quarters in every recent cycle.

---

## M. HIGH-FREQUENCY INDICATORS (Expanded Real-Time Pulse)

Beyond the indicators in Section F, a broader ecosystem of daily and weekly data allows real-time consumer nowcasting.

### Real-Time Spending Data

| **Indicator** | **Source** | **Frequency** | **Lead vs Official Data** |
|---|---|---|---|
| **BofA Spending Pulse** | BofA Institute | Weekly | ~3-4 weeks ahead of retail sales |
| **Chase Consumer Card Insights** | JPMorgan | Weekly | ~3-4 weeks ahead |
| **Visa Spending Momentum Index** | Visa | Monthly | ~2 weeks ahead |
| **Mastercard SpendingPulse** | Mastercard | Monthly | ~2 weeks ahead |
| **Redbook Retail Sales** | Redbook | Weekly | Coincident |
| **Johnson Redbook YoY** | Redbook | Weekly | Coincident |

### Travel and Leisure High-Frequency

| **Indicator** | **Source** | **Frequency** | **Use Case** |
|---|---|---|---|
| **TSA Checkpoint Volume** | TSA | Daily | Air travel demand |
| **OpenTable Reservations** | OpenTable | Daily | Dining demand |
| **STR Hotel Occupancy** | STR | Weekly | Lodging demand |
| **AAA Gas Prices** | AAA | Daily | Driving cost proxy |
| **EIA Gasoline Demand** | EIA | Weekly | Driving activity |
| **Box Office Revenue** | Box Office Mojo | Weekly | Entertainment spending |

### Consumer Behavior Signals

| **Indicator** | **Source** | **Frequency** | **Interpretation** |
|---|---|---|---|
| **Google Trends: "coupon", "discount", "payday loan"** | Google | Daily | Real-time financial stress search |
| **Google Trends: "recession", "layoff"** | Google | Daily | Consumer sentiment proxy |
| **Amazon Bestseller Price Bands** | Amazon / scraped | Daily | Trading down in e-commerce |
| **Apartment List Rent Estimates** | Apartment List | Monthly | Real-time rental market |
| **Zillow Weekly Housing Reports** | Zillow | Weekly | Real-time housing demand |

### Real-Time Regime Thresholds

| **Indicator** | **Weak** | **Stable** | **Strong** |
|---|---|---|---|
| **BofA Card Spending YoY%** | <2% | 2-5% | >5% |
| **Redbook YoY%** | <3% | 3-6% | >6% |
| **TSA vs 2019** | <95% | 95-105% | >105% |
| **OpenTable vs 2019** | <90% | 90-105% | >105% |
| **Box Office Revenue vs 2019** | <75% | 75-100% | >100% |

**The Real-Time Bridge:** During the gap between monthly retail sales and PCE releases, use: (1) weekly bank card data for spending direction, (2) TSA / OpenTable for discretionary demand, (3) Redbook for chain retail momentum, (4) Google Trends for sentiment proxies. This ecosystem provides a consumer nowcast that leads official statistics by 2-4 weeks.

---

## N. SEGMENTED CONSUMER FRAGILITY INDEX (CCI by Cohort)

The aggregate CCI can be decomposed into cohort-specific fragility to identify where stress is concentrated. This mirrors the Labor Pillar's Segmented LFI construction.

### CCI Components by Segment

| **Segment** | **Key Inputs** | **Weighting Rationale** |
|---|---|---|
| **Bottom-50 CCI** | Bottom-quintile spend YoY, CC DQ Q1, BNPL volume | First cohort to show stress |
| **Millennial CCI** | Rent burden, millennial card spend, student debt DSR | Housing-cost-trapped cohort |
| **Category CCI** | Discretionary-staples spread, trade-down spreads | Behavior-based stress gauge |
| **Geographic CCI** | State DQ diffusion, regional retail sales spread | Where weakness concentrates |

### Composite Segmented CCI

```
Segmented_CCI = 0.25 × z(-Bottom40_Real_Spending_YoY)        # Inverted
              + 0.20 × z(Q1_Credit_Card_DQ)
              + 0.15 × z(State_Consumer_Diffusion)
              + 0.15 × z(BNPL_Volume_YoY)
              + 0.15 × z(-Discretionary_Staples_Spread)       # Inverted
              + 0.10 × z(Rent_Burdened_Share)
```

**Higher Segmented CCI = more fragility concentrated in vulnerable cohorts.**

### Segmented CCI Interpretation

| **Segmented CCI** | **Aggregate CCI** | **Diagnosis** |
|---|---|---|
| High, Aggregate Low | Stress concentrated in bottom cohorts; top still spending | Early-stage K-shape |
| High, Aggregate High | Broad-based stress; top finally participating | Late-stage consumer cycle |
| Low, Aggregate Low | Broad-based resilience | Expansion |
| Low, Aggregate High | Unusual; check data | Rare configuration |

**Interpretation:** When segmented CCI diverges upward from aggregate CCI, the weakness is concentrated in vulnerable cohorts but hasn't yet spread to the core consumer. This is the early warning. When they converge (both elevated), the weakness has become broad-based and recession is typically 1-2 quarters away. Track the convergence, not just the levels.

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

## Policy & Regulatory Environment

Consumer behavior is materially affected by fiscal policy, credit regulation, and specific consumer-protection frameworks. Unlike Pillar 8 (Government), this section focuses on how policy flows *into* consumer conditions, not the policy itself.

### Policy Impact Map

| **Policy Area** | **Key Variables** | **Impact Channel** | **Lead Time** |
|---|---|---|---|
| **Federal Income Tax Policy** | TCJA extensions, brackets, SALT cap | Disposable income, saving rate | 2-4 quarters |
| **State/Local Tax Policy** | State income tax, property tax caps | Regional consumer spending | 2-4 quarters |
| **Payroll Tax / Social Security** | Wage base, rates, eligibility | Take-home pay | 1-2 quarters |
| **Unemployment Insurance** | Benefit levels, extended benefits, eligibility | Automatic stabilizer | Coincident |
| **SNAP / Food Stamps** | Eligibility, benefit levels | Bottom-quintile consumption | 1-2 months |
| **Student Loan Policy** | Forbearance, forgiveness, repayment rules | Millennial/Gen Z spending | 1-3 months |
| **Credit Card Regulation (CFPB)** | Late fee caps, disclosure rules | APR, access to credit | 6-12 months |
| **BNPL Regulation (CFPB)** | Reporting rules, underwriting standards | Phantom debt visibility | 6-12 months |
| **Consumer Protection (CFPB)** | Fair lending, servicing standards | Credit availability | Variable |
| **Minimum Wage Policy** | Federal and state floors | Low-wage income growth | 6-12 months |
| **Affordable Care Act / Healthcare** | Subsidies, coverage rules | Healthcare affordability | 1-2 quarters |
| **Tariff Policy** | Import tariffs, retaliation | Goods prices, consumer purchasing power | 1-2 quarters |

### Active Policy Risks (Consumer-Specific)

| **Risk** | **Direction** | **Magnitude** | **Probability Proxy** |
|---|---|---|---|
| **TCJA 2025 Expiration** | Bearish consumer (tax hike) or Bullish deficit (if extended) | ~0.5-1% of GDP in tax | Extension probability via political markets |
| **Student Loan Repayment Resumption Impact** | Bearish millennial spending | 20-30 bps of PCE | Actual repayment rates (Education Dept) |
| **SNAP Benefit Changes** | Bearish bottom-quintile consumption | Variable | Farm Bill / budget reconciliation |
| **CFPB BNPL Rule Impact** | Mixed: more transparency but potentially lower BNPL access | Variable | CFPB rulemaking timeline |
| **Tariff Pass-Through to Consumer** | Bearish real spending | Depends on pass-through rate | Import price data, CPI |
| **Minimum Wage Increases** | Bullish bottom-quintile, bearish employers | Varies by jurisdiction | State legislative action |
| **Healthcare Subsidy Changes** | Variable by income cohort | ~0.3% of GDP at margin | ACA subsidy extension decisions |

**Structural vs Cyclical:** Tax code and entitlement structure are structural (regime-defining, slow-moving). UI benefit levels and emergency programs are cyclical (event-driven, binary). TCJA expiration is a binary 2025-2026 cliff risk with structural implications.

---

## Demographics & Structural Context

Consumer spending is driven by structural forces that operate on multi-year to multi-decade horizons. These set the long-term trajectory independent of cyclical conditions.

### Key Structural Forces

**1. Aging Population:** The US population over 65 grew from ~13% (2010) to ~17% (2024), projected to 21% by 2035 (Census). Aging shifts spending composition: lower goods, higher healthcare, lower housing turnover, higher services. Reduces aggregate MPC (older cohorts spend less of marginal income).

| **Metric** | **Source** | **Trajectory** |
|---|---|---|
| US Population 65+ as % of Total | Census Bureau | Rising 2010-2050 |
| Median Age | Census | Rising from ~38 (2020) |
| Dependency Ratio | Census | Rising; deteriorating |

**2. Millennial / Gen Z Household Formation:** Millennials (28-43) are peak earning age but delayed household formation, lower homeownership rates than prior generations at same age. Gen Z (18-27) entering workforce. Combined ~50% of workforce, but wealth-per-capita lags.

| **Metric** | **Source** | **Signal** |
|---|---|---|
| Millennial Homeownership Rate | Fed, Census | Catching up but below Boomers at same age |
| Gen Z Labor Force Entry | BLS CPS | Accelerating 2024-2030 |
| Millennial Median Net Worth | Fed DFA | Still below prior cohorts at same age |

**3. Wealth Concentration:** Top 10% of households hold ~67% of wealth (Fed DFA). Bottom 50% holds <2%. Concentration has increased since 1990 and matters because MPC varies inversely with wealth. Aggregate PCE is increasingly sensitive to top-quintile spending decisions.

| **Metric** | **Source** | **Trajectory** |
|---|---|---|
| Top 10% Wealth Share | Fed DFA | ~67%, slowly rising |
| Bottom 50% Wealth Share | Fed DFA | <2%, stable-low |
| Top-Bottom Spending Ratio | BLS CEX / NY Fed SCE | Widening in late cycles |

**4. Credit Card / BNPL Financialization:** Consumer debt to income ratios have shifted as financial products evolved. Student loans grew from ~$500B (2005) to ~$1.7T (2024). Credit card balances hit record highs post-2022. BNPL created a new credit channel largely outside bureau reporting. Consumer financial structure is more complex than pre-2008.

| **Metric** | **Source** | **Trajectory** |
|---|---|---|
| Consumer Debt / DPI | Fed G.19, BEA | Rising; well above 2010s trough |
| Student Loan Outstanding | Fed G.19 | $1.7T, stable-high |
| BNPL Volume | CFPB / Affirm-Klarna reports | Structural growth |

**5. Immigration and Labor Supply:** Net immigration affects labor force growth (Pillar 1) and consumer demand (Pillar 5). Policy shifts since 2020 have affected net immigration materially. Both legal and undocumented immigration affect aggregate consumer demand.

| **Metric** | **Source** | **Trajectory** |
|---|---|---|
| Net Immigration (12M trailing) | Census / DHS | Policy-dependent, highly cyclical |
| Foreign-born Labor Force Share | BLS CPS | ~18% in 2024 |

### Derived Structural Metrics

| **Metric** | **Formula** | **Implication** |
|---|---|---|
| **Aggregate MPC Drift** | Weighted MPC by cohort share | Falling as population ages |
| **Wealth-Weighted PCE Sensitivity** | Top-decile wealth Δ × top-decile MPC | Rising as concentration grows |
| **Millennial Household Formation Gap** | Expected formations - actual | Positive = pent-up demand |
| **Immigration Demand Contribution** | Net immigration × per-capita PCE | Annual demand tailwind/headwind |

**Time horizon:** These forces operate over years to decades. They don't determine cyclical turning points but they shape the trajectory around which cycles oscillate. Structural tailwinds: Millennial household formation, Gen Z earnings growth. Structural headwinds: aging, wealth concentration (via lower aggregate MPC), credit burden.

---

## Watchlist: Key Levels & Early Warning Signals

This section identifies specific thresholds that, when breached, demand attention and potential regime reclassification.

### Bullish Triggers (Consumer Resilience / Recovery)

| **Signal** | **Threshold** | **Current Status** | **Significance** |
|---|---|---|---|
| **Personal Saving Rate** | Rises above 6% | {{WATCH_SAVING_RATE}} | Buffer rebuilding; Stage 1 reversal |
| **Real PCE YoY%** | Accelerates above +3% | {{WATCH_REAL_PCE}} | Broad strength |
| **CC Delinquency Rate** | Drops below 2.5% | {{WATCH_CC_DELINQ}} | Stage 2 stress fading |
| **CB Expectations Index** | Rises above 90 | {{WATCH_CB_EXP}} | Confidence returning |
| **Real DPI YoY%** | Above +2.5% | {{WATCH_REAL_DPI}} | Income growth supports spending |
| **Retail Sales Control 3M YoY%** | Above +3% | {{WATCH_RETAIL_CTRL}} | High-frequency confirmation |
| **CCI Composite** | Above +0.5 | {{WATCH_CCI}} | Healthy regime |

### Bearish Triggers (Consumer Stress Acceleration)

| **Signal** | **Threshold** | **Current Status** | **Significance** |
|---|---|---|---|
| **Real PCE YoY%** | Turns negative | {{WATCH_REAL_PCE_NEG}} | Stage 3 confirmed |
| **Personal Saving Rate** | Drops below 3% | {{WATCH_SAVING_RATE_LOW}} | Desperation level |
| **CC Delinquency Rate** | Exceeds 4.5% | {{WATCH_CC_DELINQ_HIGH}} | Credit crisis threshold |
| **CB Expectations Index** | Below 65 | {{WATCH_CB_EXP_LOW}} | Deep pessimism |
| **Retail Sales 3M Avg** | Turns negative | {{WATCH_RETAIL_NEG}} | Demand destruction |
| **Durable Goods PCE YoY%** | Below -5% | {{WATCH_DURABLES}} | Discretionary cliff |
| **CCI Composite** | Below -1.0 | {{WATCH_CCI_LOW}} | Crisis regime |

### Structural Shift Signals

| **Signal** | **Threshold** | **Significance** |
|---|---|---|
| **Excess Savings Stock (SF Fed)** | Fully depleted | Stage 1 complete; consumer relies on credit or wages |
| **Top-Bottom Spending Spread** | >6 ppts persistent | Severe K-shape; bottom stress unrelenting |
| **BNPL Volume YoY%** | >40% sustained | Phantom debt structural growth |
| **Student Loan Delinquency Rate** | Normalizes above 10% | Post-forbearance repayment stress |
| **CFPB BNPL Rule Implementation** | Rule enacted | Credit channel restructuring |
| **TCJA Expiration Resolution** | Pass or expire | Tax cliff resolution; structural baseline shift |

---

## Conclusion: The Consumer as the Last Domino

The consumer isn't a leading indicator. It's the **68% of GDP that confirms what everything else already said**.

When quits collapse (6-9 months before), credit stress builds (3-6 months before), and confidence craters (1-3 months before), the consumer eventually follows. By the time retail sales go negative, the recession is already underway.

**The Sequence:**
1. **Savings depleted** (Stage 1): saving rate falls below pre-pandemic norm, excess savings stock exhausted
2. **Credit stress building** (Stage 2): delinquencies rising, balance growth outpacing wages, DSR elevated
3. **Spending cuts** (Stage 3): durables contracting first, services rolling over
4. **Recession confirmed** (Stage 4): real PCE YoY negative, retail sales contracting

The sequence is the forecast. Stage progression is predictable; only the speed varies.

**Cross-Pillar Anchor:** The CCI + LFI cross-check is the framework's most reliable two-pillar recession signal. When both simultaneously exceed their stress thresholds (CCI < -0.3, LFI > +0.8), recession probability exceeds 65% within 12 months based on post-1990 backtests. Neither pillar alone suffices. Both together, sustained for 2+ quarters, is rarely wrong.

The wealthy hold up the aggregate throughout most of a cycle. The median consumer is where the turn shows up first. When the last domino falls, everyone will see what the labor data said 9 months ago.

---

## Additional Indicators & External Research

### The Sahm Rule (Applied to Consumer Context)

The Sahm Rule triggers a recession signal when the 3-month moving average of unemployment rises 0.50 ppts or more from its 12-month low. Triggered in every US recession since 1950; zero false positives since 1970.

For the consumer pillar, Sahm is a confirmation not a leading signal. By the time Sahm triggers, unemployment is already rising, which means labor income has already peaked, which means the consumer has already entered Stage 1-2 (savings drawdown, credit substitution). Watch proximity to Sahm threshold as a late-stage confirmation of where the consumer is in the four-stage sequence.

**Current Sahm Reading:** Monitor at [FRED SAHMREALTIME](https://fred.stlouisfed.org/series/SAHMREALTIME).

### Saving Rate as a Recession Predictor

Saving rate behavior has historically preceded recessions, though the relationship became unstable post-pandemic due to stimulus distortions.

**Pre-2020 pattern:** Saving rate declines steadily through expansions (confidence high, consumers spending future income). Rate inflects upward 6-12 months before recession as consumers retrench ahead of stress. The inflection is the signal; the level is not.

**Post-2020 complication:** The stimulus injected $2.1T of excess savings, which distorted the trend line through 2025. The SF Fed excess savings tracker (Abdelrahman & Oliveira) restored the signal by normalizing against pre-pandemic trend. Once excess savings fully depleted (late 2025 per SF Fed estimates), the traditional saving-rate inflection signal becomes usable again.

**Key level:** Personal saving rate below 5% while real income growth is slowing is the warning configuration. Buffer is gone; consumer is forced into either credit substitution or spending cuts.

### The Expectations-Present Spread

The Conference Board Expectations minus Present Situation spread is the single cleanest leading indicator in the confidence complex. When the spread compresses below -40, recession has followed within 6-12 months in every post-1970 cycle.

The mechanism: consumers assess present conditions based on their own income stability, so Present Situation stays elevated late in cycles. Expectations reflects forward-looking information (layoff announcements, tightening credit, asset price declines) that leads income weakness. The divergence is the signal.

**Threshold:** Below -40 (and falling) is the warning. Below -60 is consistent with imminent recession.

### BNPL as Phantom Debt

Buy Now Pay Later usage creates "phantom debt" because most BNPL providers do not report to traditional credit bureaus (Experian, Equifax, TransUnion) until loans default. This creates two problems:

1. **Credit score underestimation of stress:** A consumer with high BNPL exposure can appear creditworthy in FICO data while carrying significant unsecured obligations.
2. **Bank underwriting gaps:** Lenders extending credit based on bureau data miss BNPL-driven DTI stress.

**Track:** CFPB and NY Fed aggregate BNPL volume reports. YoY growth above 30% combined with rising default rates on primary credit products indicates bottom-quartile financial desperation.

### Consumer Credit Impulse

Credit impulse (change in the flow of new credit) is a stronger growth predictor than credit stock level. The formula:

```
Credit Impulse = YoY change in (New Credit / GDP)
```

A negative credit impulse means the pace of new credit creation is slowing, even if total credit outstanding is still rising. This leads consumer spending by 1-2 quarters because the marginal dollar of spending often comes from marginal credit extension.

**Source:** BIS publishes credit impulse data for major economies. The US series shows clear inflection 2-4 quarters before recessions.

### The Wealth Effect Asymmetry

Wealth effects are not symmetric. Research (Case, Quigley, Shiller; Carroll, Otsuka, Slacalek) finds that:

- **Housing wealth elasticity:** 5-8 cents per dollar of home equity change (long-run)
- **Financial wealth elasticity:** 2-4 cents per dollar of stock wealth change
- **Negative wealth elasticities are larger than positive:** losses hurt spending more than equivalent gains help

This matters for cross-pillar signals. When housing prices flatten or decline while stocks also correct, the compound wealth-effect drag on consumer spending is material even without a labor shock. Track Z.1 household net worth quarterly changes with this asymmetry in mind.

### Hand-to-Mouth (HtM) Framework

Kaplan, Violante, and Weidner (2014) identify two HtM categories:
- **Poor HtM:** Low-income, minimal assets, high MPC (15-25 cents per dollar)
- **Wealthy HtM:** Significant wealth held in illiquid assets (housing, retirement), near-zero liquid buffer, also high MPC

Combined, roughly 30% of US households are HtM. These are the consumers whose spending responds fastest to income shocks. Aggregate data hides this: the 70% of households with liquid buffers smooth consumption, making aggregate spending appear more stable than it actually is at the margin.

**Implication:** When wage growth decelerates or layoffs concentrate in sectors employing HtM households (retail, hospitality, construction), the spending response is faster and larger than aggregate income decomposition suggests.

### The MPC Timing Gap

Marginal propensity to consume out of transitory income shocks differs significantly across households. Parker, Souleles, Johnson, and McClelland (2013) estimated MPCs out of the 2008 stimulus rebates at 12-30% within three months, rising to 50-90% within six months. This means consumer spending effects from transitory shocks (tax cuts, stimulus, rate cuts) play out over 2-3 quarters, not immediately. When analyzing policy transmission, look 1-3 quarters ahead, not 1 month.

### Shelter Inflation Lag

The Owners' Equivalent Rent (OER) component of CPI lags market rent indices (Apartment List, Zillow Observed Rent Index) by approximately 12 months due to BLS's sampling methodology (6-month lease observation cycle with staggered survey waves).

**Consumer implication:** Consumer spending responds to *current* rent burden, not lagged CPI-reported shelter inflation. When market rents slow (as they did starting mid-2022), the relief to consumer spending capacity appears 6-12 months before the CPI data reflects it. Conversely, when market rents accelerate, CPI shelter remains low for a year while consumers are already under pressure.

### The Labor-to-Consumer Transmission Lag

Research and LHM backtesting show the Labor → Consumer lag operates in two stages:

1. **Hiring freeze → income growth slowdown:** 2-4 months
2. **Wage deceleration → spending deceleration:** 2-4 months

Combined: 4-8 months from initial labor inflection to spending inflection. This matches the empirical pattern of CCI responding to LFI with roughly two-quarter lag, and is why the LFI → CCI cross-check is so powerful.

---

## External Research Sources

**Federal Reserve Regional Banks:**
- [New York Fed Survey of Consumer Expectations](https://www.newyorkfed.org/microeconomics/sce) - Monthly household survey: inflation expectations, spending, credit access, labor market expectations
- [NY Fed Consumer Credit Panel](https://www.newyorkfed.org/microeconomics/hhdc) - Quarterly Household Debt and Credit Report; the authoritative household credit source
- [SF Fed Excess Savings Tracker](https://www.frbsf.org/research-and-insights/publications/economic-letter/2023/05/data-on-pandemic-era-excess-savings/) - Abdelrahman & Oliveira; the definitive excess savings estimate
- [Atlanta Fed GDPNow](https://www.atlantafed.org/cqer/research/gdpnow) - Real-time PCE component nowcast
- [Chicago Fed National Financial Conditions Index](https://www.chicagofed.org/research/data/nfci/current-data) - Includes consumer credit conditions subcomponent
- [Philadelphia Fed State Coincident Indexes](https://www.philadelphiafed.org/surveys-and-data/regional-economic-analysis/state-coincident-indexes) - Monthly state-level economic conditions

**Government Data Sources:**
- [BEA Personal Income and Outlays](https://www.bea.gov/data/income-saving/personal-income) - Monthly PCE, DPI, saving rate release
- [Census Advance Monthly Retail Trade Report](https://www.census.gov/retail/marts/www/marts_current.pdf) - Mid-month retail sales release
- [BLS Consumer Expenditure Survey](https://www.bls.gov/cex/) - Quarterly by demographic; ~6-month lag
- [Fed G.19 Consumer Credit](https://www.federalreserve.gov/releases/g19/) - Monthly consumer credit outstanding
- [Fed Z.1 Financial Accounts](https://www.federalreserve.gov/releases/z1/) - Quarterly household balance sheet (flow of funds)
- [CFPB BNPL Market Report](https://www.consumerfinance.gov/data-research/research-reports/) - Periodic BNPL scale and performance

**Alternative/Private Data:**
- [BofA Institute](https://institute.bankofamerica.com/) - Free weekly card spending reports
- [JPMorgan Chase Institute](https://www.jpmorganchase.com/institute) - Consumer card spending, cash flow research
- [Visa Spending Momentum Index](https://usa.visa.com/partner-with-us/visa-consulting-analytics/visa-economic-insights.html) - Monthly
- [Mastercard SpendingPulse](https://www.mastercardservices.com/en/economic-consulting/spendingpulse) - Monthly
- [Opportunity Insights Economic Tracker](https://tracktherecovery.org/) - ZIP-level spending, employment data
- [Affirm, Klarna, Afterpay earnings reports](https://www.klarna.com/investor-relations/) - BNPL volume and default rates

**Think Tanks:**
- [Urban Institute Financial Health](https://www.urban.org/research-area/housing-finance-policy-center) - Household financial health by demographic
- [Brookings Hamilton Project](https://www.hamiltonproject.org/) - Regular consumer and labor analysis

---

## Reference: Published Analysis

**"Consumer: The Last Domino"** (Educational Series, February 2026) is the published article version of this pillar. Available at `research.lighthousemacro.com/p/consumer-the-last-domino`.

The article covers:
- The four-stage consumer stress sequence (savings depletion → credit substitution → spending cuts → recession confirmation)
- The 68% GDP anchor and why consumer weakness is a coincident confirmation, not a leading signal
- The K-shaped bifurcation pattern and how aggregate data masks it
- The CCI composite architecture and its Labor-Pillar cross-check
- Invalidation criteria in both directions

The article treats the consumer as the "last domino": by the time retail sales contract, labor has already told you the story 6-9 months earlier. The rigorous approach is to watch labor (Pillar 1) and credit (Pillar 9) for the leading signals, then use consumer data for confirmation and position-sizing of the spending response.

---

## Historical Validation

### Pattern Recognition

| **Episode** | **CCI** | **LFI** | **Key Consumer Signal** | **Outcome** | **Lead Time** |
|---|---|---|---|---|---|
| **Late 2006** | +0.3 | +0.6 | Saving rate 3.5%, CC DQ rising, housing cracking | Consumer held through 2007, collapsed 2008 | 12-15 months |
| **Late 2007** | -0.4 | +1.4 | Credit card DQ 3.7%, discretionary softening | Deep consumer recession confirmed | 0-3 months |
| **GFC Trough (Q1 2009)** | -1.8 | +2.3 | CC DQ peaked 6.8%, durables -20% YoY | Recession ended June 2009 | Coincident |
| **Late 2011** | +0.2 | +0.4 | Saving rate normalizing, DQ falling, confidence low | Slow recovery continued | N/A |
| **Late 2018** | +0.4 | +0.2 | Saving rate 7.5%, labor strong, no credit stress | Consumer robust into 2019; trade war scare only | N/A (false recession scare) |
| **Feb 2020** | +0.6 | -0.3 | All consumer metrics healthy. No leading signals. | COVID shock (exogenous) | No lead (exogenous) |
| **Late 2021** | +1.5 | -1.2 | Stimulus surge, saving rate 9%, excess savings $2T | Peak consumer; inflation followed | N/A |
| **Late 2023** | +0.4 | +0.5 | Saving rate 4%, CC DQ 2.8% (rising), excess savings depleting | Normalization without recession (so far) | Ongoing |

### False Signals

**Late 2022 recession fears:** Multiple consumer sentiment indicators (UMich at 50, lowest since 1952) and yield curve inversions triggered widespread recession calls. Actual consumer spending held up because: (1) excess savings still supported the balance sheet, (2) labor market remained historically tight (LFI still negative), (3) wage growth outpaced inflation briefly in 2023. The UMich reading was a partisan/inflation-concern artifact, not a spending signal. Real PCE held positive throughout. Lesson: confidence alone, without credit stress or labor fragility, is not a reliable recession signal.

**2015-2016 oil shock:** Energy-state consumer stress, rising charge-offs in oil & gas regions, and manufacturing recession did not transmit to national consumer. Bottom-quartile CCI fell, aggregate CCI held. The geographic containment is instructive: regional consumer stress that does not reach 30-50 state diffusion remains idiosyncratic.

### Structural Breaks

**Post-COVID consumer dynamics (2020-present):** Several shifts complicate historical comparisons:

1. **Excess savings stock:** $2.1T of pandemic-era excess savings drove a 4-5 year consumer spending overhang that masked underlying income-spending dynamics. Traditional saving-rate indicators were distorted until the stock fully depleted (late 2025 per SF Fed estimates).

2. **BNPL proliferation:** Buy Now Pay Later has become a meaningful consumer finance channel since 2020, creating phantom debt outside traditional bureau tracking. Credit-score-based consumer health indicators understate stress for BNPL-heavy users.

3. **Remote work and geographic arbitrage:** Consumer spending patterns shifted as remote work enabled migration from expensive coastal metros to lower-cost Sun Belt cities. Traditional metro-level retail signals (NYC, SF) became less representative of aggregate consumer health.

4. **Partisan sentiment distortion:** UMich and Conference Board confidence readings since 2016 increasingly reflect partisan political alignment rather than economic conditions. Cross-checks (Expectations-Present spread, which is less affected; Bloomberg Consumer Comfort; actual card spending) are more reliable than raw confidence levels.

5. **K-shaped wealth distribution:** The top-10% share of wealth has risen to historic levels. Aggregate consumer strength metrics are increasingly reliant on top-quintile spending, which masks bottom-half weakness for longer than in prior cycles.

---

## Alternative & High-Frequency Data

| **Source** | **Indicator** | **Frequency** | **Access** | **Lead vs Official Data** |
|---|---|---|---|---|
| **BofA Institute** | BofA Spending Pulse | Weekly | Free public reports | Leads retail sales ~3-4 weeks |
| **JPMorgan Chase Institute** | Consumer Card Insights | Weekly | Free public reports | Leads retail sales ~3-4 weeks |
| **Visa** | Visa Spending Momentum Index | Monthly | Press release (free) | Leads retail sales ~2 weeks |
| **Mastercard** | SpendingPulse | Monthly | Press release / subscription | Leads retail sales ~2 weeks |
| **Redbook** | Johnson Redbook Index | Weekly | Redbook / vendors | Coincident, higher frequency than Census |
| **TSA** | Checkpoint Volume | Daily | TSA website (free) | Real-time travel demand |
| **OpenTable** | Reservations YoY vs 2019 | Daily | OpenTable State of Industry | Real-time dining demand |
| **STR** | Hotel Occupancy | Weekly | STR (subscription) | Weekly lodging demand |
| **Box Office Mojo** | Domestic Box Office | Weekly | Box Office Mojo (free) | Entertainment spending |
| **AAA** | Gas Price National Average | Daily | AAA (free) | Real-time commodity pass-through |
| **EIA** | Gasoline Product Supplied | Weekly | EIA (free) | Driving activity proxy |
| **Apartment List** | National Rent Estimate | Monthly | Apartment List (free) | Leads CPI OER ~12 months |
| **Zillow** | Observed Rent Index (ZORI) | Monthly | Zillow Research (free) | Leads CPI OER ~12 months |
| **Google** | Google Trends (stress keywords) | Daily | Google Trends (free) | Real-time sentiment proxy |
| **Opportunity Insights** | Economic Tracker | Weekly | tracktherecovery.org (free) | ZIP-level spending, employment |
| **NY Fed SCE** | Survey of Consumer Expectations | Monthly | NY Fed (free) | Household inflation/spending expectations |
| **Affirm / Klarna / Afterpay** | BNPL volume / default rates | Quarterly | Earnings releases (free) | Bottom-quartile stress gauge |

---

## Academic & Research Foundation

| **Paper/Framework** | **Author(s)** | **Key Insight** |
|---|---|---|
| "A Theory of the Consumption Function" (1957) | Milton Friedman | Permanent Income Hypothesis: consumption driven by permanent (not current) income; transitory income smoothed |
| "The Life Cycle Hypothesis" (1954) | Modigliani & Brumberg | Households smooth consumption over life cycle; savings profile peaks in middle age |
| "A Model of Intertemporal Choice" (1986) | Hall & Mishkin | Consumption responds to permanent but not transitory income shocks; PIH-consistent |
| "Buffer-Stock Saving" (1997) | Deaton; Carroll | Precautionary savings behavior explains why low-wealth households smooth less |
| "A Model of the Consumption Response to Fiscal Stimulus" (2013) | Kaplan & Violante | 30% of households are hand-to-mouth; MPCs heterogeneous by wealth category |
| "Household Debt and the Great Recession" (2011) | Mian & Sufi | High-leverage households drove 2007-2009 consumption collapse; housing wealth channel |
| "Consumption and the Response to Anticipated Wealth Changes" (2005) | Carroll, Otsuka, Slacalek | Housing wealth elasticity 5-8 cents; financial wealth 2-4 cents |
| "Consumer Spending and Tax Rebates" (2013) | Parker, Souleles, Johnson, McClelland | 2008 rebate MPCs 12-30% in 3 months, 50-90% in 6 months |
| "Wealth, the Stock Market, and Macroeconomy" (2001) | Case, Quigley, Shiller | Housing wealth effect larger than stock wealth effect; asymmetric response to gains vs losses |
| "The Excess Savings of American Households" (2023) | Abdelrahman & Oliveira (SF Fed) | Methodology for measuring pandemic-era excess savings; definitive source |
| Sahm Rule | Claudia Sahm | 3-month MA unemployment rising 0.50+ ppts from 12-month low signals recession |
| Expectations-Present Spread | Conference Board / academic tradition | Divergence of future vs current assessments leads recession by 6-12 months |
| Credit Impulse | BIS research tradition | Change in credit flow (not stock) leads growth by 1-2 quarters |

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
| UMCSENT1 | UMich Consumer Sentiment (alternate code) | Monthly |
| MICH | UMich Inflation Expectations (1-yr) | Monthly |
| CSCICP03USM665S | OECD Consumer Confidence (US) - CB proxy | Monthly |

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

### Category Deep Dive (Section K)

| **Series ID** | **Description** | **Frequency** |
|---|---|---|
| TOTALSA | Total Vehicle Sales (SAAR) | Monthly |
| ALTSALES | Light Weight Vehicle Sales | Monthly |
| DAUTOSAAR | Domestic Auto Sales | Monthly |
| RSAFS | Advance Retail Sales (headline) | Monthly |
| RSFHFS | Retail Sales: Furniture and Home Furnishings | Monthly |
| RSEAS | Retail Sales: Electronics and Appliance Stores | Monthly |
| RSCCAS | Retail Sales: Clothing and Clothing Accessories | Monthly |
| RSDBS | Retail Sales: Food Services and Drinking Places | Monthly |
| RSFSXMV | Retail Sales ex-Motor Vehicles and Parts | Monthly |
| RSDSELD | Retail Sales: Department Stores | Monthly |
| RSSGHBMS | Retail Sales: Sporting Goods, Hobby, Book, Music Stores | Monthly |

### Segmentation and Regional Indicators (Sections I, J)

| **Series ID** | **Description** | **Frequency** |
|---|---|---|
| CUUR0000SEHA | CPI: Rent of Primary Residence (rent burden tracking) | Monthly |
| CUUR0000SEHC | CPI: Owners' Equivalent Rent | Monthly |
| LES1252881600Q | Median Usual Weekly Earnings (real) | Quarterly |
| DSPI | Disposable Personal Income by state (BEA releases; FRED has many per-state codes) | Quarterly |
| [STATE]UR | State Unemployment Rate (per state code: CAUR, TXUR, etc.) | Monthly |
| SMU[STATE][SECTOR] | State/sector employment combinations | Monthly |

### High-Frequency (Section M)

| **Series ID** | **Description** | **Frequency** |
|---|---|---|
| DCOILWTICO | WTI Crude Oil Price (gasoline pass-through) | Daily |
| GASREGCOVW | Retail Gas Price (AAA-equivalent via EIA) | Weekly |
| PPICMM | PPI Commodities (input cost to consumer goods) | Monthly |

### Non-FRED Data Sources

| **Indicator** | **Source** | **Notes** |
|---|---|---|
| Conference Board Consumer Confidence | Conference Board | Not on FRED; web scrape or subscription. Proxy via OECD CSCICP03USM665S |
| Conference Board Present Situation / Expectations | Conference Board | Not on FRED; key for expectations-present spread |
| Auto Loan Delinquency Rate (by type) | NY Fed Consumer Credit Panel | Quarterly Household Debt and Credit Report |
| Auto Loan DQ (90+) | NY Fed CCP | Quarterly |
| Mortgage Delinquency (by vintage/state) | NY Fed CCP, MBA National Delinquency Survey | Quarterly |
| Student Loan Delinquency | NY Fed CCP | Quarterly (distorted by forbearance through 2024) |
| Retail Sales Control Group | Census Bureau | No clean FRED series ID; derived from Census advance retail report |
| Bank of America Card Spending | BofA Institute | Free weekly reports |
| Chase Card Spending | JPMorgan Chase Institute | Free weekly reports |
| Visa Spending Momentum Index | Visa | Monthly press release |
| Mastercard SpendingPulse | Mastercard | Monthly press release |
| Redbook Retail Sales | Redbook Research | Weekly, available via data vendors |
| Credit Card Balances (aggregate) | NY Fed Quarterly Report on Household Debt | Quarterly |
| BNPL Volume / Default | CFPB, Affirm/Klarna/Afterpay reports | Quarterly, irregular |
| TSA Checkpoint Volume | TSA | Daily, free public data |
| OpenTable Reservations (vs 2019) | OpenTable State of Industry | Daily |
| STR Hotel Occupancy | STR | Weekly (subscription) |
| Apartment List Rent Estimate | Apartment List | Monthly, free |
| Zillow Observed Rent Index (ZORI) | Zillow Research | Monthly, free |
| Google Trends (stress keywords) | Google | Daily, free |
| Opportunity Insights Economic Tracker | Harvard / OI | ZIP-level, weekly, free |
| NY Fed Survey of Consumer Expectations | NY Fed | Monthly, free |
| BLS Consumer Expenditure Survey (by quintile) | BLS | Quarterly, ~6-month lag |
| Philadelphia Fed State Coincident Indexes | Philadelphia Fed | Monthly, free |
| SF Fed Excess Savings Tracker | SF Fed | Monthly update, free |
| Atlanta Fed GDPNow PCE decomposition | Atlanta Fed | Continuous during quarter |

---

*Bob Sheehan, CFA, CMT*
*Founder & CIO, Lighthouse Macro*
*Last Updated: February 2026*
