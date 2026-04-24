# PILLAR 9: FINANCIAL

## The Financial Transmission Chain

Financial conditions aren't just rates. They're the **transmission layer** between Fed policy and the real economy. The mechanism operates through cascading liquidity and credit dynamics:

```
Fed Policy Rate → Bank Funding Costs → Credit Availability →
Lending Standards → Loan Growth → Business Investment →
Hiring → Income → Spending → Fed Policy Rate (Reinforcing Loop)
```

**The Insight:** The Fed sets the policy rate, but **financial conditions determine whether it matters**. When credit spreads are tight and banks are lending freely, restrictive policy is blunted. When spreads blow out and banks tighten standards, even neutral policy becomes contractionary. The transmission mechanism is the variable, not the rate itself.

The beauty of financial data: it's **real-time and market-priced**. Credit spreads don't wait for BLS releases. Yield curves don't care about seasonal adjustments. When financial stress emerges, markets tell you immediately. The lag is in the real economy's response, not in the signal.

---

## Why Financial Conditions Matter: The Transmission Multiplier

Financial conditions are the **amplifier or dampener** of monetary policy. A 100 bps rate hike can be effectively neutral (if credit loosens in offset) or significantly contractionary (if credit tightens simultaneously), depending on the full financial conditions picture.

**The Cascade:**

**1. Financial → Credit:** Spreads determine borrowing costs beyond the policy rate (coincident)
**2. Financial → Investment:** Credit availability drives capex decisions (2-4 quarter lag)
**3. Financial → Housing:** Mortgage rates + spreads determine affordability (1-3 month lag)
**4. Financial → Consumer:** Credit card rates, auto loan availability (1-2 month lag)
**5. Financial → Wealth:** Equity/bond prices drive wealth effects (coincident)

Get the financial conditions call right, and you've triangulated the **effective** monetary stance. Miss it, and you're watching the Fed Funds rate while the economy responds to something else entirely.

**The Four Stages of Financial Stress:** Financial conditions deterioration follows a recognizable sequence. Knowing which stage dominates shapes risk-asset positioning.

1. **Risk Pricing Inflection** (Leading): Credit spreads widen from compressed levels. Equity volatility rises from suppressed levels. The market starts demanding risk compensation.
2. **Credit Channel Tightening** (Leading-Coincident): Bank lending standards tighten (SLOOS). Loan growth decelerates. C&I credit becomes scarcer for small/mid borrowers first.
3. **Liquidity Stress** (Coincident): Funding markets show stress (SOFR-IORB spread, repo rates). Dealer balance sheets stretch. Treasury auctions tail.
4. **Transmission Complete** (Lagging): Default rates rise. Bankruptcy filings accelerate. Bank earnings compress. Real economy responds.

The divergence window (when spreads stay tight while SLOOS tightens) is characteristic of late-cycle mispricing. When the divergence closes, it typically closes through spread widening, not credit easing. The unbuffered plumbing environment (Pillar 10) amplifies any stress that emerges.

---

## Primary Indicators: The Complete Architecture

### A. CREDIT SPREADS (The Risk Pricing Signal)

Credit spreads measure the **price of risk** beyond the risk-free rate. They're the market's real-time assessment of default probability, liquidity, and risk appetite. The ICE BofA OAS series (BAMLH0A0HYM2 for HY, BAMLC0A0CM for IG) are the standard US corporate credit benchmarks, updated daily.

| **Indicator** | **FRED Code** | **Frequency** | **Lead/Lag** | **Interpretation** |
|---|---|---|---|---|
| **HY OAS (ICE BofA)** | BAMLH0A0HYM2 | Daily | **Leads defaults 6-9 mo** | High-yield corporate spread |
| **IG OAS (ICE BofA)** | BAMLC0A0CM | Daily | Leads HY 1-2 mo | Investment-grade spread |
| **BBB OAS** | BAMLC0A4CBBB | Daily | Coincident | Lowest IG tier (downgrade risk) |
| **CCC OAS** | BAMLH0A3HYC | Daily | Coincident | Distressed debt spread |
| **HY-IG Spread** | Derived | Daily | **Leading 3-6 mo** | Risk appetite gauge |
| **TED Spread** | Derived | Daily | Leading 1-3 mo | Bank funding stress |
| **LIBOR-OIS Spread** | Derived | Daily | Leading 1-2 mo | Interbank stress (legacy) |
| **SOFR-Fed Funds Spread** | Derived | Daily | Coincident | Secured funding stress |

#### Derived Spread Metrics

| **Metric** | **Formula** | **Threshold** | **Signal** |
|---|---|---|---|
| **HY OAS Percentile** | Current vs 20Y History | <10th %ile | Complacency (risk-on) |
| **HY OAS YoY Change** | Current - Year Ago | >+100 bps | Stress building |
| **IG-HY Compression** | HY OAS / IG OAS | <3.0x | Risk underpriced |
| **CCC-B Spread** | CCC OAS - B OAS | <400 bps | Distressed risk underpriced |

#### Regime Thresholds: Credit Spreads

| **Indicator** | **Complacent** | **Normal** | **Elevated** | **Crisis** |
|---|---|---|---|---|
| **HY OAS** | <300 bps | 300-450 bps | **450-650 bps** | >650 bps |
| **IG OAS** | <100 bps | 100-150 bps | **150-220 bps** | >220 bps |
| **BBB OAS** | <130 bps | 130-180 bps | **180-280 bps** | >280 bps |
| **CCC OAS** | <800 bps | 800-1200 bps | **1200-1800 bps** | >1800 bps |

**The Spread Percentile Signal:** HY OAS percentiles below the 10th percentile of the 1997-present distribution signal extreme complacency. Historically, this configuration has been followed by one of two outcomes: (a) sustained tight conditions (soft-landing path), or (b) rapid spread widening (cycle transition). The determining factor is cross-pillar: when labor and growth pillars are fragile, tight spreads tend to reprice higher within 2-4 quarters.

**Credit spreads as a leading indicator:** HY OAS widening by +100 bps over 3 months precedes default rate increases by 6-9 months. The credit market absorbs information before fundamentals print. This is why Gilchrist-Zakrajsek's Excess Bond Premium (EBP) methodology isolates the component of credit spreads not explained by default risk alone as a predictor of real economy outcomes.

**Quality migration within HY:** The CCC-B spread captures within-HY quality premium. Compression below 400 bps signals distressed-debt risk underpricing and typically precedes default rate spikes. The CCC default rate typically runs 3-5x the B default rate, so CCC-B spread should reflect substantial quality differentiation. Compression indicates complacency even within the risky credit tier.

---

### B. YIELD CURVE (The Recession Signal)

The yield curve is the **oldest recession predictor**. Inverted curves have preceded every US recession since 1970. But the signal is in the **shape and its changes**, not just the level at a point in time.

| **Indicator** | **FRED Code** | **Frequency** | **Lead/Lag** | **Interpretation** |
|---|---|---|---|---|
| **10Y-2Y Spread** | T10Y2Y | Daily | **Leads recession 12-18 mo** | Classic inversion signal |
| **10Y-3M Spread** | T10Y3M | Daily | **Leads recession 6-12 mo** | Fed's preferred measure |
| **2Y-Fed Funds Spread** | Derived | Daily | Leading 3-6 mo | Near-term rate expectations |
| **10Y-Fed Funds Spread** | Derived | Daily | Coincident | Real rate proxy |
| **30Y-10Y Spread** | Derived | Daily | Coincident | Term premium signal |
| **2Y Treasury Yield** | DGS2 | Daily | **Leads Fed 3-6 mo** | Market rate expectations |
| **10Y Treasury Yield** | DGS10 | Daily | Coincident | Benchmark long rate |
| **30Y Treasury Yield** | DGS30 | Daily | Coincident | Long-duration signal |

#### Derived Curve Metrics

| **Metric** | **Formula** | **Threshold** | **Signal** |
|---|---|---|---|
| **Curve Slope (10Y-2Y)** | 10Y - 2Y | <0 bps | Inversion (recession signal) |
| **Curve Steepening Momentum** | Current Slope - 6M Ago | >+50 bps | Bear steepening (risk-off) |
| **Term Premium (ACM Model)** | NY Fed estimate | <0 bps | Term premium compressed |
| **Real 10Y Yield** | 10Y Nominal - 10Y Breakeven | >+2% | Restrictive |

#### Regime Thresholds: Yield Curve

| **Indicator** | **Inverted** | **Flat** | **Normal** | **Steep** |
|---|---|---|---|---|
| **10Y-2Y Spread** | <0 bps | 0-50 bps | **50-150 bps** | >150 bps |
| **10Y-3M Spread** | <0 bps | 0-75 bps | **75-200 bps** | >200 bps |
| **10Y Yield Level** | <3.5% | 3.5-4.0% | **4.0-4.75%** | >4.75% |
| **Term Premium** | <-50 bps | -50 to +25 bps | **+25 to +100 bps** | >+100 bps |

**The Dis-Inversion Signal:** The yield curve typically *inverts* 12-18 months before recession (Fed's preferred 10Y-3M curve leads recession by 6-12 months). But the *dis-inversion* (when the curve returns to positive slope after being inverted) is often the more proximate recession signal. Every post-1970 recession began 6-12 months after the 10Y-2Y dis-inverted from the prior inversion episode.

**Why dis-inversion is the trigger:** Inversion reflects tight monetary policy and restrictive financial conditions. Dis-inversion reflects the market pricing Fed rate cuts in response to weakening economic conditions. The Fed typically cuts when fundamentals have already deteriorated; dis-inversion captures this moment.

**Bull vs bear steepening:** The direction of steepening matters. Bull steepening (front-end rates falling faster than back-end) is the classic recession-response pattern. Bear steepening (back-end rates rising faster than front-end) reflects fiscal risk premium or inflation concerns and has different implications. Distinguish which type of steepening is occurring.

---

### C. FINANCIAL CONDITIONS INDICES (The Composite Signal)

Financial Conditions Indices (FCIs) synthesize rates, spreads, equities, and dollar into a single gauge of monetary transmission. Multiple FCIs exist (Chicago Fed NFCI, Goldman FCI, Bloomberg FCI, OFR FSI, St. Louis Fed FSI). They frequently diverge; reading the divergences is often more informative than any single composite.

| **Indicator** | **Source** | **Frequency** | **Lead/Lag** | **Interpretation** |
|---|---|---|---|---|
| **Chicago Fed NFCI** | Chicago Fed | Weekly | **Leads GDP 2-4 qtrs** | National Financial Conditions |
| **Chicago Fed ANFCI** | Chicago Fed | Weekly | Leads GDP 2-4 qtrs | Adjusted for cycle |
| **Goldman Sachs FCI** | Goldman | Daily | Coincident | Proprietary, widely followed |
| **Bloomberg FCI** | Bloomberg | Daily | Coincident | Composite gauge |
| **St. Louis Fed FSI** | St. Louis Fed | Weekly | Coincident | Financial Stress Index |
| **Kansas City Fed FSI** | KC Fed | Monthly | Coincident | Alternative stress gauge |
| **OFR FSI** | OFR | Daily | Coincident | Official sector gauge |

#### Derived FCI Metrics

| **Metric** | **Formula** | **Threshold** | **Signal** |
|---|---|---|---|
| **NFCI Level** | Chicago Fed Index | >0 | Tighter than average |
| **NFCI Momentum** | Current - 3M Avg | >+0.2 | Rapid tightening |
| **FCI-Policy Divergence** | FCI Change - Fed Funds Change | >+50 bps equiv | Conditions tightening beyond policy |
| **Stress Index Spike** | FSI 1-week change | >+0.5 | Acute stress event |

#### Regime Thresholds: Financial Conditions

| **Indicator** | **Loose** | **Neutral** | **Tight** | **Crisis** |
|---|---|---|---|---|
| **Chicago Fed NFCI** | <-0.5 | -0.5 to +0.25 | **+0.25 to +0.75** | >+0.75 |
| **Chicago Fed ANFCI** | <-0.5 | -0.5 to +0.25 | **+0.25 to +0.75** | >+0.75 |
| **St. Louis FSI** | <-0.5 | -0.5 to +0.5 | **+0.5 to +1.5** | >+1.5 |
| **OFR FSI** | <-0.5 | -0.5 to +1.0 | **+1.0 to +3.0** | >+3.0 |

**FCI-Policy Divergence Pattern:** NFCI below zero (looser than average) while Fed Funds is above 4% reflects a well-documented dynamic: equity wealth effect, tight credit spreads, and accommodative non-rate factors can offset rate hikes in the composite FCI. When this pattern sustains, the Fed's effective restrictiveness is lower than the policy rate suggests. The Fed has explicitly commented on this dynamic, arguing that FCI loosening during Fed tightening undermines monetary transmission.

**Methodology differences across FCIs:** Chicago Fed NFCI weights risk indicators (credit, equity, money market) heavily. Goldman FCI weights rates and exchange rate more. Bloomberg FCI weights money market funding stress. When they diverge, the decomposition reveals which channel is driving conditions. Use multiple FCIs for robustness; don't rely on a single composite.

---

### D. BANK LENDING & CREDIT GROWTH (The Transmission Channel)

Bank lending is the **physical transmission** of financial conditions to the real economy. When banks lend, policy transmits. When banks tighten, the credit channel contracts and capital-dependent borrowers face higher costs or reduced access. Non-bank lenders (private credit, BDCs) have grown in importance post-2008 but bank lending remains the largest credit channel.

| **Indicator** | **FRED Code** | **Frequency** | **Lead/Lag** | **Interpretation** |
|---|---|---|---|---|
| **Commercial & Industrial Loans** | BUSLOANS | Weekly | Coincident | Business credit demand |
| **Consumer Loans (Revolving)** | REVOLSL | Monthly | Coincident | Credit card lending |
| **Consumer Loans (Nonrevolving)** | NONREVSL | Monthly | Coincident | Auto + student loans |
| **Real Estate Loans** | REALLN | Weekly | Coincident | Mortgage + CRE |
| **Total Bank Credit** | H8 Data | Weekly | Coincident | All bank lending |
| **SLOOS: C&I Tightening** | Fed Survey | Quarterly | **Leads loan growth 2-4 qtrs** | Lending standards |
| **SLOOS: CRE Tightening** | Fed Survey | Quarterly | Leads CRE loans 2-4 qtrs | Commercial real estate |
| **SLOOS: Consumer Tightening** | Fed Survey | Quarterly | Leads consumer loans 1-2 qtrs | Consumer credit |

#### Derived Lending Metrics

| **Metric** | **Formula** | **Threshold** | **Signal** |
|---|---|---|---|
| **C&I Loan Growth YoY%** | Current - Year Ago | <0% | Credit contraction |
| **Total Credit Growth YoY%** | Current - Year Ago | <3% | Below nominal GDP |
| **SLOOS Net Tightening** | % Tightening - % Easing | >+20% | Significant tightening |
| **Loan-Deposit Spread** | Loan Rate - Deposit Rate | >3.5% | Bank margins healthy |

#### Regime Thresholds: Bank Lending

| **Indicator** | **Contraction** | **Tight** | **Normal** | **Loose** |
|---|---|---|---|---|
| **C&I Loan Growth YoY%** | <-3% | -3% to +3% | **+3% to +8%** | >+8% |
| **Total Credit Growth YoY%** | <0% | 0-4% | **4-8%** | >8% |
| **SLOOS C&I Tightening (Net %)** | >+40% | +20% to +40% | **-10% to +20%** | <-10% |
| **SLOOS CRE Tightening (Net %)** | >+50% | +30% to +50% | **0% to +30%** | <0% |

**The SLOOS Leading Indicator:** Senior Loan Officer Opinion Survey results on C&I tightening lead actual C&I loan growth by 2-4 quarters. When SLOOS net tightening exceeds +20%, loan growth typically slows meaningfully within 2 quarters. Net tightening above +40% (credit crunch territory) has preceded every post-1990 recession.

**The divergence signal:** SLOOS tightening while credit spreads stay compressed is characteristic of late-cycle mispricing. The bank-channel signal (SLOOS, loan growth) typically leads the market-pricing signal (credit spreads) because banks have access to proprietary borrower data that markets price with a lag. When SLOOS and spreads diverge, bank-channel signals tend to prove correct.

**Small vs large firm bifurcation:** SLOOS separately tracks tightening for large vs small firm C&I lending. Small firms (<250 employees) lose credit access earlier and more severely because they lack public debt market alternatives. Net tightening on small-firm C&I above +40% combined with small-business bankruptcy filings rising is a specific signal of the small-business credit squeeze.

---

### E. EQUITY MARKET CONDITIONS (The Wealth Effect Channel)

Equity markets transmit financial conditions through three channels: **wealth effects** (consumer spending via Pillar 5), **cost of capital** (corporate investment via Pillar 6), and **sentiment/confidence** (expectations across households and businesses). The S&P 500 is the most widely-tracked benchmark; breadth and sector rotation provide more granular signals than the headline index.

| **Indicator** | **Symbol** | **Frequency** | **Lead/Lag** | **Interpretation** |
|---|---|---|---|---|
| **S&P 500** | SPX | Daily | Coincident | Broad equity market |
| **S&P 500 P/E (Forward)** | Derived | Daily | Coincident | Valuation signal |
| **VIX** | VIX | Daily | **Leads corrections 1-2 wks** | Equity volatility |
| **VVIX** | VVIX | Daily | Leads VIX 1-2 wks | Vol-of-vol |
| **Put/Call Ratio** | CBOE | Daily | Coincident | Sentiment gauge |
| **Equity Risk Premium** | Derived | Daily | Coincident | Stocks vs bonds |
| **S&P 500 Breadth** | Advance/Decline | Daily | **Leads SPX 1-3 mo** | Market participation |
| **Russell 2000/S&P 500** | Derived | Daily | **Leading 2-4 mo** | Risk appetite |

#### Derived Equity Metrics

| **Metric** | **Formula** | **Threshold** | **Signal** |
|---|---|---|---|
| **Equity Risk Premium** | Earnings Yield - 10Y Real Yield | <2.5% | Expensive vs bonds |
| **VIX Term Structure** | VIX - VIX3M | >0 | Backwardation (stress) |
| **Breadth Divergence** | SPX YTD% - Equal Weight YTD% | >+5 ppts | Narrow leadership |
| **Small/Large Spread** | R2000 YoY - SPX YoY | <-10 ppts | Risk-off rotation |

#### Regime Thresholds: Equity Markets

| **Indicator** | **Stressed** | **Cautious** | **Normal** | **Euphoric** |
|---|---|---|---|---|
| **VIX** | >30 | 20-30 | **12-20** | <12 |
| **S&P 500 Forward P/E** | <14x | 14-17x | **17-21x** | >21x |
| **Equity Risk Premium** | >5% | 3.5-5% | **2.5-3.5%** | <2.5% |
| **Breadth (% Above 200 DMA)** | <30% | 30-50% | **50-70%** | >70% |

**Equity Risk Premium (ERP):** Earnings yield minus real 10Y yield is the standard ERP calculation. Historical average ~4%. ERP below 3% signals equity expensiveness relative to bonds; below 2% is historically high mean-reversion risk. ERP compression during late cycles is common: rising real yields and expanding forward P/E both pressure the ERP lower. Resolution comes via either multiple compression, earnings growth, or bond yields falling.

**The Breadth Divergence Pattern:** When the S&P 500 makes new highs while the equal-weight index lags and %-above-200DMA falls below 50%, narrow leadership is the signature. This pattern preceded the 1972, 1999, 2007, and 2021 market peaks by 3-9 months. Breadth leads price when narrow leadership emerges late-cycle.

**Small vs large equity spread:** Russell 2000 underperforming S&P 500 persistently (by >10 ppts YoY) signals risk-off rotation within equities. Small caps are more bank-credit-dependent and less hedged, so they roll over first when financial conditions deteriorate. Watch R2K/SPX ratio for the within-equity risk signal.

---

### F. VOLATILITY & RISK METRICS (The Stress Signal)

Volatility measures **uncertainty and risk compensation**. Low vol reflects either genuine calm (early cycle) or complacency (late cycle mispricing). Spiking vol reflects stress. The structure of volatility (term, skew, cross-asset) tells you more than the level alone.

| **Indicator** | **Symbol** | **Frequency** | **Lead/Lag** | **Interpretation** |
|---|---|---|---|---|
| **VIX Index** | VIX | Daily | Coincident | 30-day implied vol (SPX) |
| **VIX3M** | VIX3M | Daily | Coincident | 3-month implied vol |
| **MOVE Index** | MOVE | Daily | **Leads equity vol 1-2 wks** | Treasury volatility |
| **CVIX** | CVIX | Daily | Coincident | Currency volatility |
| **Skew Index** | SKEW | Daily | Leading 1-2 wks | Tail risk pricing |
| **Credit Vol (CDX)** | CDX | Daily | Coincident | Credit volatility |
| **Realized Vol (SPX)** | Derived | Daily | Lagging | Actual volatility |

#### Derived Volatility Metrics

| **Metric** | **Formula** | **Threshold** | **Signal** |
|---|---|---|---|
| **VIX-Realized Spread** | VIX - 30D Realized Vol | >+5 | Fear premium elevated |
| **MOVE/VIX Ratio** | MOVE / VIX | >6x | Bond vol leading |
| **Vol Term Structure** | VIX / VIX3M | >1.0 | Backwardation (near-term fear) |
| **Skew Premium** | SKEW - 100 | >+30 | Tail hedging elevated |

#### Regime Thresholds: Volatility

| **Indicator** | **Complacent** | **Normal** | **Elevated** | **Crisis** |
|---|---|---|---|---|
| **VIX** | <13 | 13-20 | **20-30** | >30 |
| **MOVE** | <80 | 80-110 | **110-150** | >150 |
| **VIX Term Structure** | <0.90 | 0.90-1.0 | **1.0-1.1** | >1.1 |
| **SKEW** | <115 | 115-130 | **130-145** | >145 |

**VIX Compression Patterns:** VIX below 13 is historically rare (below 10th percentile). Sustained compression reflects either genuinely stable underlying conditions or complacency combined with structured product selling pressure (short vol ETFs, put-selling strategies). When compressed vol resolves upward, the move tends to be abrupt and severe because systematic short-vol strategies force-cover on the move.

**Cross-Asset Vol Relationships:** MOVE (Treasury vol) often leads VIX (equity vol) by 1-2 weeks. Rising MOVE while VIX stays compressed is the early warning. The MOVE/VIX ratio above 6x is unusual and historically precedes equity volatility regime shifts. The ratio dropping back toward 4x typically coincides with VIX normalizing higher.

**Vol Term Structure Signal:** VIX/VIX3M above 1.0 means near-term volatility is pricing higher than medium-term (backwardation), typical of acute stress. Contango (VIX/VIX3M below 1.0) is the normal regime. Backwardation persisting for 5+ trading days signals sustained stress; brief backwardation spikes are common around events.

---

### G. REAL RATES (The True Policy Stance)

Real rates are the **inflation-adjusted** cost of money. The Fed sets nominal rates; real rates determine actual restrictiveness. TIPS (Treasury Inflation-Protected Securities) yields are the cleanest market-based measure of real rates, with 5Y and 10Y TIPS being the most liquid reference points.

| **Indicator** | **FRED Code** | **Frequency** | **Lead/Lag** | **Interpretation** |
|---|---|---|---|---|
| **Fed Funds Rate** | DFEDTARL | Daily | Coincident | Nominal policy rate |
| **5Y TIPS Yield** | DFII5 | Daily | Coincident | Real 5Y rate |
| **10Y TIPS Yield** | DFII10 | Daily | Coincident | Real 10Y rate |
| **5Y Breakeven Inflation** | T5YIE | Daily | Coincident | Inflation expectations |
| **10Y Breakeven Inflation** | T10YIE | Daily | Coincident | Long-term expectations |
| **5Y5Y Forward Inflation** | T5YIFR | Daily | **Leads realized 12-24 mo** | Fed's anchor gauge |
| **Real Fed Funds** | Derived | Daily | Coincident | Policy rate - Core PCE |

#### Derived Real Rate Metrics

| **Metric** | **Formula** | **Threshold** | **Signal** |
|---|---|---|---|
| **Real Fed Funds** | Fed Funds - Core PCE YoY | >+1.5% | Restrictive |
| **Real 10Y vs r*** | 10Y TIPS - Estimated r* (0.5%) | >+1.5% | Very restrictive |
| **Real Rate Momentum** | Current - 6M Avg | >+50 bps | Tightening |
| **Breakeven Change** | Current - 1Y Ago | >+50 bps | Inflation expectations rising |

#### Regime Thresholds: Real Rates

| **Indicator** | **Accommodative** | **Neutral** | **Restrictive** | **Very Restrictive** |
|---|---|---|---|---|
| **Real Fed Funds** | <0% | 0-1.0% | **1.0-2.0%** | >2.0% |
| **Real 10Y** | <0.5% | 0.5-1.5% | **1.5-2.5%** | >2.5% |
| **5Y5Y Forward** | <2.0% | 2.0-2.3% | **2.3-2.6%** | >2.6% |

**Real Rate Regime Identification:** Real Fed Funds above +1% is restrictive; above +2% is very restrictive. The neutral real rate (r*) is estimated between 0.5-1% per Laubach-Williams and Holston-Laubach-Williams models. Real Fed Funds minus estimated r* gives the effective policy stance.

**Real 10Y vs r*:** The 10-year real yield captures long-run restrictiveness beyond short-term policy. Real 10Y above +2% is materially above the 2010-2019 average (near zero) and provides sustained headwind to long-duration assets: real estate (via cap rates), growth equities (via discount rate), and rate-sensitive cyclicals. The real 10Y matters more for long-horizon asset pricing than the Fed Funds rate.

**Breakeven Inflation as Fed Credibility Gauge:** 5Y5Y forward breakeven inflation (T5YIFR) is the Fed's preferred long-run inflation expectations anchor. Stability in this measure signals anchored expectations. 5Y5Y above 2.5% or below 1.5% reflects de-anchoring risk. The Fed speaks to this measure in policy communications.

---

### H. PLUMBING & LIQUIDITY (The System's Circulatory System)

Fed plumbing determines how policy transmits through the banking system. Reserves, RRP, dealer balance sheets, and funding market spreads are the pipes. This section overlaps with Pillar 10 (Plumbing) but focuses on the financial conditions channel rather than the plumbing mechanics themselves.

| **Indicator** | **FRED Code** | **Frequency** | **Lead/Lag** | **Interpretation** |
|---|---|---|---|---|
| **Reserve Balances** | WRBWFRBL | Weekly | Coincident | Bank reserves at Fed |
| **Reverse Repo (RRP)** | RRPONTSYD | Daily | **Leads reserves 1-3 mo** | Money market liquidity buffer |
| **Treasury General Account (TGA)** | WTREGEN | Weekly | Leads reserves 1-2 wks | Treasury cash balance |
| **Fed Balance Sheet** | WALCL | Weekly | Coincident | Total Fed assets |
| **QT Pace** | Derived | Monthly | Coincident | Balance sheet runoff rate |
| **Repo Rates (SOFR)** | SOFR | Daily | Coincident | Secured funding rate |
| **Repo Spread (SOFR-IORB)** | Derived | Daily | Leading 1-2 wks | Funding stress |
| **Dealer Treasury Holdings** | NY Fed | Weekly | Coincident | Market-maker capacity |

#### Derived Plumbing Metrics

| **Metric** | **Formula** | **Threshold** | **Signal** |
|---|---|---|---|
| **LCI (Liquidity Cushion Index)** | z(RRP/GDP) + z(Reserves/GDP) | <-0.5 | Thin cushion |
| **Reserve Scarcity** | Reserves - Ample Threshold (~$3T) | <$0 | Scarcity regime |
| **RRP Drain Rate** | Monthly Change in RRP | <-$100B/mo | Rapid liquidity drain |
| **SOFR-IORB Spread** | SOFR - IORB | >+10 bps | Funding stress |

#### Regime Thresholds: Plumbing

| **Indicator** | **Scarce** | **Adequate** | **Ample** | **Abundant** |
|---|---|---|---|---|
| **Reserve Balances** | <$3.0T | $3.0-3.3T | **$3.3-3.8T** | >$3.8T |
| **RRP Facility** | <$100B | $100-300B | **$300-800B** | >$800B |
| **SOFR-IORB Spread** | >+15 bps | +5 to +15 bps | **-5 to +5 bps** | <-5 bps |
| **LCI** | <-1.0 | -1.0 to -0.3 | **-0.3 to +0.5** | >+0.5 |

**The Unbuffered Plumbing Dynamic:** RRP (Reverse Repo Facility) peaked above $2T in late 2022 as excess money market liquidity accumulated. Drawdown through 2023-2024 reflects Treasury bill issuance absorbing the excess. When RRP is substantially exhausted and reserves are near the ample threshold (~$3T), the system loses its buffer against liquidity shocks.

**Why the buffer matters:** In a buffered system, Treasury issuance, banking demand shifts, and Fed operations can be absorbed through RRP drainage without affecting bank reserves. In an unbuffered system, any shock hits reserves directly, and bank balance sheets must contract lending or the Fed must intervene. The 2019 repo spike occurred in a partially-buffered system; an unbuffered version would have been more severe.

**LCI (Liquidity Cushion Index):** Pillar 10's composite captures this dynamic. Cross-reference LCI readings alongside FCI for a complete financial conditions picture. When FCI shows loose market-based conditions but LCI is deeply negative, the system is mispriced: tight spreads cannot persist if a liquidity shock depletes reserves.

---

## I. CREDIT SPREAD DECOMPOSITION DEEP DIVE (Quality, Sector, and Geographic)

Headline HY OAS and IG OAS are composite measures. Decomposing them by quality tier, sector, and geographic exposure reveals where stress concentrates and often provides early warning that aggregate spreads miss.

### Quality Tier Decomposition

| **Tier** | **Rating Range** | **FRED/ICE Code** | **Typical OAS Range** | **Default Rate (historical avg)** |
|---|---|---|---|---|
| **AAA** | AAA | BAMLC0A1CAAA | 40-80 bps | <0.1% |
| **AA** | AA+ to AA- | BAMLC0A2CAA | 60-110 bps | <0.1% |
| **A** | A+ to A- | BAMLC0A3CA | 80-150 bps | 0.1-0.2% |
| **BBB** | BBB+ to BBB- | BAMLC0A4CBBB | 120-220 bps | 0.3-0.5% |
| **BB** | BB+ to BB- | BAMLH0A1HYBB | 250-400 bps | 1-2% |
| **B** | B+ to B- | BAMLH0A2HYB | 400-700 bps | 4-6% |
| **CCC** | CCC+ and below | BAMLH0A3HYC | 800-1500 bps | 15-25% |

### Quality Migration Signal

The spread ratio between adjacent quality tiers is a powerful within-credit signal:

- **BBB/A ratio:** Rising signals investment-grade stress. BBBs are the lowest IG tier; downgrades to HY ("fallen angels") can create forced selling from index-tracking IG funds
- **BB/BBB ratio:** Measures the IG-to-HY boundary; compression signals late-cycle complacency
- **B/BB ratio:** Middle-HY quality differentiation; widening signals risk aversion returning to HY
- **CCC/B ratio:** Within-HY distress differentiation; compression is extreme complacency signal

**Fallen Angel Dynamics:** When a BBB issuer is downgraded to HY, IG-index funds must sell. This mechanical selling creates "fallen angel alpha" opportunities for HY buyers. Fallen angel volume rising sharply indicates deteriorating IG credit quality and forward-downgrade risk.

### Sector Spread Decomposition

Credit spreads vary materially by sector. Sector-specific stress often leads broad HY widening by 1-3 months.

| **Sector** | **Typical Relative OAS vs HY Index** | **Cycle Sensitivity** |
|---|---|---|
| **Energy** | -50 to +200 bps (highly variable) | Oil price sensitive |
| **Technology** | -100 to -50 bps | Secular growth buffers |
| **Consumer Discretionary** | Around HY average | Consumer cycle sensitive |
| **Consumer Staples** | -50 to +50 bps | Defensive |
| **Healthcare** | -50 to 0 bps | Defensive |
| **Financials** | Around HY average (excl. banks) | Credit-cycle sensitive |
| **Industrials** | Around HY average | Cyclical |
| **Real Estate (REITs)** | 0 to +100 bps | Rate-sensitive |
| **Materials** | -50 to +100 bps | Commodity-linked |
| **Telecommunications** | -50 to +50 bps | Defensive, cash-flow stable |
| **Utilities** | -100 to -50 bps | Regulated, defensive |

**Sector-Specific Leading Indicators:**

- **Energy HY spreads** lead broad HY by 2-4 weeks when oil prices move materially
- **Consumer Discretionary HY spreads** lead consumer confidence inflections by 1-2 months
- **Real Estate HY spreads** lead commercial real estate distress by 3-6 months
- **Technology HY spreads** lead tech sector equity corrections by 1-3 weeks

### Emerging Market Sovereign Spreads

EM sovereign credit spreads (J.P. Morgan EMBI Global) provide a global credit signal often leading US HY by 1-3 months. Dollar strength and US financial conditions drive EM credit stress first; broader contagion typically follows.

| **Indicator** | **Source** | **Signal** |
|---|---|---|
| **EMBI Global OAS** | J.P. Morgan | Broad EM sovereign stress |
| **EMBI Investment Grade** | J.P. Morgan | Higher-quality EM |
| **CEMBI Broad** | J.P. Morgan | EM corporate credit |
| **JPM GBI-EM** | J.P. Morgan | Local-currency EM sovereign |

### Municipal Bond Spreads

Municipal bond (muni) spreads provide a different lens on state and local fiscal health, often isolated from corporate credit dynamics.

| **Indicator** | **Typical Relationship** | **Signal Content** |
|---|---|---|
| **Muni/Treasury Yield Ratio (10Y)** | >90% for high-tax buyers | Muni cheap vs Treasury |
| **HY Muni OAS** | 200-500 bps | Distressed muni (Puerto Rico, Illinois) |
| **Muni-Corporate Spread** | Varies by tax status | Tax-adjusted relative value |

### Derived Spread Decomposition Metrics

| **Metric** | **Formula** | **Threshold** | **Signal** |
|---|---|---|---|
| **BBB/A Ratio** | BBB OAS / A OAS | >1.6x | IG quality stress |
| **HY/IG Ratio** | HY OAS / IG OAS | <3.0x | Cross-tier compression |
| **CCC/B Ratio** | CCC OAS / B OAS | <2.0x | Distressed underpriced |
| **Energy-HY Spread** | Energy sector OAS - HY Index | >+100 bps | Energy-specific stress |
| **EM-US HY Spread** | EMBI - US HY OAS | >+200 bps | EM leading stress |

---

## J. CURVE DYNAMICS DEEP DIVE (Segments, Steepening, and Carry)

The yield curve is not one indicator; it's a multi-dimensional structure. Different curve segments convey different information, and the *type* of steepening or flattening reveals the underlying drivers.

### Curve Segment Anatomy

```
FRONT-END          BELLY          LONG-END          ULTRA-LONG
(0-2Y)            (3-10Y)         (10-30Y)          (30Y+)
  │                 │                 │                 │
  │                 │                 │                 │
Fed Policy        Growth +         Term Premium     Duration risk
Expectations      Inflation        + Fiscal Risk    concentration
  │                 │                 │                 │
  2Y yield         5Y-10Y           10Y-30Y           Long bonds
  Fed path         Nominal GDP      Supply/demand     LDI strategies
  proxy            expectations     balance           Pension duration
```

### Segment-Specific Signals

**Front-End (0-2Y):** Primarily driven by Fed policy path expectations. The 2Y yield minus Fed Funds rate captures market expectations of near-term Fed cuts or hikes. 2Y yield falling below Fed Funds by >50 bps signals the market pricing imminent cuts.

**Belly (3-10Y):** Most sensitive to nominal GDP and inflation expectations. The 5Y yield is often the cleanest growth-plus-inflation proxy because it sits between short policy expectations and long-run fiscal/supply concerns.

**Long-End (10-30Y):** Most sensitive to term premium, fiscal risk, and duration supply (Pillar 8 linkage). The 30Y-10Y spread isolates long-end term premium dynamics: widening 30Y-10Y signals increasing duration risk compensation.

**Ultra-Long:** Specialized demand from pension LDI, insurance liabilities, and long-duration institutional buyers. Relative value vs 30Y signals duration-demand imbalances.

### Bull vs Bear Steepening and Flattening

The *direction* of curve changes matters as much as the shape itself:

| **Pattern** | **Front-End Move** | **Long-End Move** | **Interpretation** |
|---|---|---|---|
| **Bull Steepening** | Falling faster | Falling | Recession-response; Fed cuts priced |
| **Bear Steepening** | Rising less | Rising faster | Fiscal risk; inflation concerns |
| **Bull Flattening** | Falling | Falling more | Safe-haven; flight to duration |
| **Bear Flattening** | Rising faster | Rising less | Hawkish Fed; cyclical early |

**The most powerful recession signal:** Bull steepening after prolonged inversion. This pattern reflects the market pricing Fed rate cuts as growth deteriorates, with front-end rates falling faster than long-end rates. This pattern preceded every post-1980 recession.

**Bear steepening in fiscal dominance:** When the curve bear-steepens during periods of persistent large deficits (Pillar 8), the long-end is pricing fiscal risk premium rather than growth expectations. The 2023-2024 period featured episodes of bear steepening correlated with TBAC announcements of increased coupon issuance.

### The Real Yield Curve

TIPS yields form a parallel real yield curve (5Y TIPS, 10Y TIPS, 30Y TIPS). Comparing real vs nominal curves decomposes moves into real-rate vs inflation-expectations changes.

- **Real curve steepening** = long-run growth expectations rising or term premium in real rates
- **Real curve flattening** = real long-run expectations falling or term premium compression
- **Breakeven curve** (10Y breakeven minus 5Y breakeven) measures forward inflation expectations

### Carry and Roll-Down

Bond total return has three components: (1) yield income, (2) price change from yield change, (3) "carry and roll" from the bond moving down the yield curve as it ages. In a steep curve, carry-and-roll is positive and substantial; in flat/inverted curves, it's minimal or negative.

**Carry-and-Roll by Tenor (typical expansion-phase):**
- 2Y: 5-15 bps per month
- 5Y: 15-30 bps per month
- 10Y: 20-40 bps per month
- 30Y: 25-50 bps per month

When the curve is inverted, carry-and-roll goes negative for short tenors, creating headwind for bond strategies that rely on curve carry.

### Derived Curve Metrics

| **Metric** | **Formula** | **Threshold** | **Signal** |
|---|---|---|---|
| **2Y-Fed Funds Gap** | 2Y Yield - Fed Funds Upper | <-50 bps | Market pricing cuts |
| **10Y-5Y Spread** | 10Y - 5Y | Rising = bear steepening of long-end |
| **30Y-10Y Spread** | 30Y - 10Y | Rising = long-end term premium |
| **Real 10Y vs Real 5Y** | DFII10 - DFII5 | Real curve slope |
| **5Y5Y Inflation Forward** | T5YIFR | Long-run inflation expectations |

---

## K. BANKING SYSTEM HEALTH (Beyond SLOOS)

Bank balance sheets are where financial conditions become credit transmission. Beyond SLOOS lending standards, a suite of banking health indicators reveals stress before it transmits to the real economy.

### Capital and Liquidity Ratios

| **Ratio** | **Source** | **Threshold** | **Signal** |
|---|---|---|---|
| **CET1 Capital Ratio** | Bank filings, FFIEC | Minimum 4.5% + buffers | Regulatory capital strength |
| **Tier 1 Capital Ratio** | FFIEC | Minimum 6% + buffers | Core capital cushion |
| **Total Capital Ratio** | FFIEC | Minimum 8% + buffers | Full capital measure |
| **Leverage Ratio (SLR)** | FFIEC | Minimum 3% (5% for GSIBs) | Balance sheet constraint |
| **LCR (Liquidity Coverage Ratio)** | FFIEC | Minimum 100% | 30-day liquidity stress |
| **NSFR (Net Stable Funding Ratio)** | FFIEC | Minimum 100% | 1-year funding stability |

### Net Interest Margin (NIM)

NIM is the spread between lending yields and deposit costs. It's the primary driver of bank profitability and capital generation.

| **Metric** | **Formula** | **Interpretation** |
|---|---|---|
| **NIM (Aggregate)** | Interest Income - Interest Expense / Earning Assets | Bank profitability |
| **NIM Trend (YoY)** | Current - Year Ago | Pressure direction |
| **Deposit Beta** | Δ Deposit Rate / Δ Fed Funds | Sensitivity to policy rates |

**NIM compression dynamics:** Rising Fed Funds initially compresses NIM as deposit costs rise before loan yields adjust. Over time, loans reprice and NIM recovers. This is the "lag effect" in bank earnings during tightening cycles.

### Deposit Flow Dynamics

Deposit flows are a leading indicator of bank stress. Post-SVB (March 2023), deposit flight risk has been elevated.

| **Indicator** | **Source** | **Signal** |
|---|---|---|
| **Total Commercial Bank Deposits** | Fed H.8 | Aggregate deposit level |
| **Small Bank Deposits** | Fed H.8 | Regional bank specific |
| **Uninsured Deposit Share** | Call Reports / FDIC | Flight risk exposure |
| **Deposit Beta (large banks)** | Calculated | Pricing power |

**The SVB lesson:** Silicon Valley Bank's rapid collapse revealed deposit flight speed in the digital banking era. Uninsured deposits above 50% of total deposits combined with duration-mismatched securities portfolios is the stress configuration that led to the 2023 regional bank crisis.

### Commercial Real Estate Exposure

Banks hold approximately $3T of commercial real estate (CRE) loans, concentrated in regional banks. CRE is the highest-risk lending category post-COVID due to office vacancy and remote work dynamics.

| **Indicator** | **Source** | **Signal** |
|---|---|---|
| **CRE Loan Delinquency Rate** | Fed H.8, FDIC | Loss expectations |
| **Office Vacancy Rates** | CoStar, Cushman | Underlying collateral stress |
| **CMBS Delinquency (CRED iQ, Trepp)** | CRED iQ / Trepp | CMBS-specific stress |
| **Regional Bank CRE Concentration** | FFIEC Call Reports | Bank-specific exposure |

### Loan Loss Provisioning

Bank loan loss provisions are forward-looking estimates of expected losses. Rising provisions signal bank management anticipation of deteriorating credit quality.

| **Metric** | **Source** | **Signal** |
|---|---|---|
| **Aggregate Loan Loss Provisions** | FFIEC | Forward-loss expectations |
| **Net Charge-Off Rate** | FDIC | Realized losses |
| **Allowance for Loan Losses / Loans** | FFIEC | Reserve adequacy |

### Derived Banking Metrics

| **Metric** | **Formula** | **Threshold** | **Signal** |
|---|---|---|---|
| **CET1 Trend** | Current - Year Ago | <-50 bps | Capital erosion |
| **Deposit Flight (Small Banks)** | 3M Change in Small Bank Deposits | <-$50B | Regional bank stress |
| **CRE Delinquency Direction** | 6M Change | >+50 bps | CRE stress accelerating |
| **Provision Coverage** | Allowance / Annualized Charge-Offs | <1.5x | Under-reserved |

---

## L. ASSET PRICE CHANNELS (Equity Wealth, Housing Wealth, Sector Rotation)

Financial conditions transmit to the real economy through asset price channels. Equity and housing wealth, sector rotation, and currency-credit linkages each carry distinct signals.

### Equity Wealth Effect Channel

Equity wealth effects operate through the household consumption response to stock market changes. Case-Quigley-Shiller estimates: ~2-4 cents per dollar of financial wealth change feeds into spending over 2-4 quarters.

| **Indicator** | **Source** | **Use Case** |
|---|---|---|
| **Household Equity Holdings** | Fed Z.1 | Aggregate wealth exposure |
| **Top-10% Equity Concentration** | Fed DFA | Distributional wealth gauge |
| **S&P 500 1-Year Change** | Market | Coincident wealth signal |
| **Wealth-Income Ratio** | Z.1 / BEA | Asset-price-to-income |

### Housing Wealth Effect Channel

Housing wealth elasticity is materially higher than financial wealth: ~5-8 cents per dollar per Carroll-Otsuka-Slacalek. Housing wealth is also more broadly distributed than equity wealth, affecting more households.

| **Indicator** | **Source** | **Use Case** |
|---|---|---|
| **Owner Equity in Real Estate** | Fed Z.1 | Aggregate housing wealth |
| **Case-Shiller Home Price Index** | S&P / Case-Shiller | Nominal home price trend |
| **Zillow Home Value Index** | Zillow | Alternative nominal measure |
| **Home Equity Extraction** | Z.1, Fannie/Freddie | Wealth-to-spending conduit |

### Sector Rotation Signals

Within equity markets, sector rotation provides a within-market financial conditions signal. Defensive vs cyclical performance rotates predictably across cycle stages.

| **Rotation Pattern** | **Sectors Favored** | **Cycle Stage** |
|---|---|---|
| **Early-cycle** | Consumer Discretionary, Financials, Industrials | Expansion beginning |
| **Mid-cycle** | Technology, Communication Services, Industrials | Growth acceleration |
| **Late-cycle** | Energy, Materials, Financials | Inflation, tight policy |
| **Recession** | Staples, Healthcare, Utilities | Defensive rotation |
| **Recovery** | Discretionary, Financials, Tech | Return to risk |

### Credit-Equity Relative Value

Credit and equity markets often diverge before major regime changes. Credit typically leads equity in bearish rotations; equity leads credit in bullish rotations.

| **Signal** | **Threshold** | **Interpretation** |
|---|---|---|
| **HY OAS Rising + S&P Making Highs** | 50+ bps divergence over 3 months | Credit leading equity weakness |
| **HY OAS Tight + Equity Volatile** | Compressed spreads, rising vol | Vol priced before credit |
| **IG Spreads Widening + Equity Stable** | 20+ bps IG widening | High-quality credit stress first |

### Currency-Credit Linkages

US dollar strength/weakness affects financial conditions through multiple channels: (1) EM dollar debt servicing, (2) commodity pricing, (3) foreign earnings of US multinationals, (4) global carry trade dynamics.

| **Indicator** | **Source** | **FCI Impact** |
|---|---|---|
| **DXY Dollar Index** | ICE | Broad dollar strength |
| **EM FX Index (J.P. Morgan EMCI)** | JPM | EM currency stress |
| **JPY/USD** | Market | Safe-haven yen dynamics |
| **CNY/USD** | Market | Chinese currency pressure |

### Derived Asset Price Channel Metrics

| **Metric** | **Formula** | **Threshold** | **Signal** |
|---|---|---|---|
| **Wealth/Income Ratio (Household)** | Net Worth / DPI | >8x (historical) | Elevated but sustainable |
| **Housing/Income Ratio** | Median Home Price / Median Income | >5x | Affordability stress |
| **Cyclical-Defensive Equity Spread** | Cyclical YoY - Defensive YoY | <-5 ppts | Defensive rotation active |
| **HY OAS vs S&P 500 (3M)** | Credit spread widening vs equity gains | Divergent | Credit-equity misalignment |
| **DXY YoY% Change** | Dollar index momentum | >+8% | EM stress building |

---

## M. VOLATILITY COMPLEX DEEP DIVE (Cross-Asset and Regime Analysis)

Volatility analysis goes beyond the VIX. Cross-asset vol relationships, skew, dispersion, and volatility regimes provide a richer signal set.

### The Volatility Complex

| **Indicator** | **Measures** | **Typical Range** |
|---|---|---|
| **VIX** | 30-day implied vol on S&P 500 | 10-40 |
| **VIX9D** | 9-day implied vol | 10-40 (more sensitive) |
| **VIX3M** | 3-month implied vol | 12-30 |
| **VIX6M** | 6-month implied vol | 14-28 |
| **VVIX** | Vol-of-vol (VIX volatility) | 80-150 |
| **MOVE** | Treasury option vol | 60-160 |
| **CVIX** | G7 currency vol | 5-15 |
| **OVX** | Oil vol | 25-60 |
| **GVZ** | Gold vol | 10-30 |
| **CDX Credit Vol** | Credit index vol | Variable |

### Skew and Tail Risk

The CBOE SKEW Index measures the perceived probability of a tail event in the S&P 500 over 30 days. Higher SKEW = more tail risk priced into out-of-the-money puts.

| **SKEW Level** | **Interpretation** |
|---|---|
| **<115** | Complacent (low tail hedging) |
| **115-130** | Normal tail risk pricing |
| **130-145** | Elevated tail hedging |
| **>145** | Extreme tail risk pricing |

### Vol Term Structure Regimes

| **Regime** | **Structure** | **Signal** |
|---|---|---|
| **Contango (normal)** | VIX < VIX3M < VIX6M | Calm conditions, vol sellers profitable |
| **Flat** | VIX ≈ VIX3M | Transition regime |
| **Backwardation** | VIX > VIX3M > VIX6M | Acute stress |
| **Curve Collapse** | VIX spikes toward VIX9D | Imminent event risk |

### Realized vs Implied Vol

The VRP (Variance Risk Premium) is the premium of implied vol over realized vol. It represents compensation for bearing vol risk.

| **VRP** | **Calculation** | **Signal** |
|---|---|---|
| **Normal VRP** | VIX - 30D Realized > +3 | Calm, vol sellers compensated |
| **Compressed VRP** | VIX - 30D Realized < +1 | Realized catching up to implied |
| **Negative VRP** | VIX < 30D Realized | Stress, realized exceeds implied |

### Dispersion

Dispersion measures single-stock vol vs index vol. Rising dispersion reflects stock-specific risk increasing relative to systematic risk, often seen in late-cycle stock-picking environments.

| **Indicator** | **Calculation** | **Signal** |
|---|---|---|
| **Implied Correlation** | 1 - (Index Vol / Constituent Vol) | Falling = rising dispersion |
| **SDEX (Dispersion Index)** | CBOE index | Stock-specific risk gauge |

### Cross-Asset Vol Signals

| **Relationship** | **Typical Pattern** | **Divergence Signal** |
|---|---|---|
| **MOVE leads VIX** | MOVE rises first, VIX follows 1-2 weeks | MOVE up, VIX flat = warning |
| **VIX vs CDX HY** | Correlated movements | Credit vol rising, VIX flat = credit stress coming |
| **CVIX vs VIX** | Often correlated via dollar | CVIX up sharp, VIX flat = FX-driven stress |
| **OVX vs Equity Energy** | Oil vol and XLE correlated | Divergence = structural shifts |

### Derived Volatility Metrics

| **Metric** | **Formula** | **Threshold** | **Signal** |
|---|---|---|---|
| **VIX Term Structure** | VIX / VIX3M | >1.0 | Backwardation (stress) |
| **VRP (30D)** | VIX - 30D Realized | <+1 | VRP compression |
| **MOVE/VIX Ratio** | MOVE / VIX | >6x | Bond vol leading |
| **SKEW-Implied Tail** | SKEW - 100 | >+30 | Tail hedging elevated |
| **Implied Correlation (SPX)** | Derived from index vol | <0.30 | High dispersion (stock-picking) |

---

## N. SEGMENTED FINANCIAL CONDITIONS INDEX (FCI by Channel)

The aggregate FCI can be decomposed into sub-composites that isolate different channels. Sub-composite divergences are often where the actionable signal lives.

### FCI Sub-Composites

| **Sub-Composite** | **Key Inputs** | **Measures** |
|---|---|---|
| **Market-Pricing** | HY OAS, IG OAS, VIX, Equity ERP | Market-based risk pricing |
| **Banking Channel** | SLOOS, C&I loan growth, NIM, deposit flows | Bank credit transmission |
| **Plumbing Channel** | Reserves, RRP, SOFR-IORB, LCI | System liquidity conditions |
| **Real-Rate Channel** | Real Fed Funds, real 10Y, 5Y5Y forward inflation | Policy restrictiveness |
| **Asset-Price Channel** | Equity wealth, housing wealth, DXY | Wealth effect transmission |

### Composite Segmented FCI

```
Segmented_FCI = 0.20 × z(-HY_OAS)                         # Market (inverted)
              + 0.15 × z(-NFCI)                            # Market composite (inverted)
              + 0.15 × z(SLOOS_C&I_Tightening)             # Banking
              + 0.10 × z(-C&I_Loan_Growth_YoY)             # Banking (inverted)
              + 0.10 × z(-LCI)                             # Plumbing (inverted)
              + 0.10 × z(Real_Fed_Funds)                   # Real rate
              + 0.10 × z(VIX)                              # Market vol
              + 0.05 × z(MOVE)                             # Bond vol
              + 0.05 × z(-DXY_YoY)                         # Dollar (inverted for asset prices)
```

**Higher segmented FCI = tighter conditions (note: sign convention opposite of traditional FCIs where loose = positive).**

### Sub-Composite Divergence Patterns

| **Pattern** | **Market** | **Banking** | **Plumbing** | **Real-Rate** | **Diagnosis** |
|---|---|---|---|---|---|
| **Unified Loose** | Loose | Loose | Ample | Accommodative | Expansion |
| **Unified Tight** | Tight | Tight | Scarce | Restrictive | Stress |
| **Market-Bank Divergence** | Loose | Tight | Variable | Variable | Late-cycle mispricing |
| **Plumbing-Leading Tight** | Loose | Loose | Scarce | Neutral | Pre-stress signal |
| **Real-Rate Isolation** | Loose | Loose | Ample | Restrictive | Policy only, transmission blocked |

**Interpretation:** When sub-composites diverge, focus on which channel has typically proven leading historically. Bank-channel signals often lead market-pricing signals by 1-3 months. Plumbing signals often lead by 4-8 weeks when reserves get scarce. Market-pricing signals reflect current positioning, which can stay loose even as underlying stress builds.

---

## Financial Pillar Composite Index (FCI)

### Formula

The Financial Pillar Composite synthesizes spreads, curve, conditions, lending, and plumbing into a single financial conditions indicator:

```
FCI = 0.20 × z(-HY_OAS)                              # Inverted (tight spreads = loose)
    + 0.15 × z(-NFCI)                                # Inverted (negative = loose)
    + 0.15 × z(Yield_Curve_10Y2Y)
    + 0.15 × z(-Real_Fed_Funds)                      # Inverted (high = tight)
    + 0.10 × z(C&I_Loan_Growth)
    + 0.10 × z(-VIX)                                 # Inverted (high = stressed)
    + 0.10 × z(LCI)
    + 0.05 × z(-SLOOS_Tightening)                    # Inverted (tightening = negative)
```

**Component Weighting Rationale:**
- **HY OAS (20%):** Primary risk pricing signal (inverted, since tight spreads = loose conditions)
- **NFCI (15%):** Composite conditions gauge (inverted)
- **Yield Curve (15%):** Recession signal and term premium
- **Real Fed Funds (15%):** Actual policy restrictiveness (inverted)
- **C&I Loan Growth (10%):** Credit transmission channel
- **VIX (10%):** Risk sentiment (inverted)
- **LCI (10%):** Liquidity cushion
- **SLOOS (5%):** Lending standards (inverted)

### Interpretation

| **FCI Range** | **Regime** | **Risk Allocation** | **Signal** |
|---|---|---|---|
| > +1.0 | Very Loose | Overweight risk assets | Financial tailwind |
| +0.5 to +1.0 | Loose | Moderate risk-on | Conditions supportive |
| -0.5 to +0.5 | Neutral | Balanced | Mixed conditions |
| -1.0 to -0.5 | Tight | **Underweight risk** | Conditions headwind |
| < -1.0 | Crisis | Maximum defensive | Financial stress |

### Historical Calibration

| **Period** | **FCI** | **Regime** | **Outcome (12M Forward)** |
|---|---|---|---|
| **Dec 2006** | +0.4 | Loose | Conditions tightened into GFC |
| **Sep 2008** | -2.1 | Crisis | Lehman collapse, max stress |
| **Dec 2012** | +0.6 | Loose | QE3 tailwind |
| **Dec 2018** | -0.7 | Tight | Fed pivot, recovery |
| **March 2020** | -1.8 | Crisis | COVID shock, max stress |
| **Dec 2021** | +1.2 | Very Loose | Peak liquidity |
| **Oct 2022** | -0.6 | Tight | SVB stress building |
| **Dec 2025** | **+0.3** | **Neutral** | **Divergent signals** |

**Current reading:** see "Current State Assessment Template" section below for the live FCI value, component scores, and regime classification.

---

## Lead/Lag Relationships: The Financial Cascade

```
LEADING                           COINCIDENT                  LAGGING
────────────────────────────────────────────────────────────────────────────────────
│                                 │                          │
│  Yield Curve Inversion (12-18) │  HY/IG Spreads           │  Bank Earnings (1-2 qtrs)
│  SLOOS Tightening (2-4 qtrs)   │  VIX                     │  Default Rates (6-12 mo)
│  Credit Growth Decel (1-2 qtrs)│  NFCI                    │  Loan Loss Provisions (2-4 qtrs)
│  MOVE Index (1-2 wks→VIX)      │  Fed Funds Rate          │  Charge-off Rates (6-9 mo)
│  2Y Treasury (3-6 mo→Fed)      │  Real Rates              │  NPL Ratios (2-4 qtrs)
│  RRP Drain (1-3 mo→reserves)   │  Equity Valuations       │  Bankruptcy Filings (6-12 mo)
│  Breadth Divergence (1-3 mo)   │  Dollar Index            │  Unemployment (6-9 mo)
│  Term Premium (6-12 mo)        │                          │
│                                │                          │
────────────────────────────────────────────────────────────────────────────────────
```

**The Critical Chain:**

**1. Yield curve inverts** (policy restrictive vs expectations) → 12-18 months later → **Recession begins**
**2. SLOOS tightening** (banks restrict credit) → 2-4 quarters later → **Loan growth contracts**
**3. Credit growth contracts** → 1-2 quarters later → **Capex and hiring slow**
**4. Spreads widen** (risk repricing) → 6-12 months later → **Defaults spike**
**5. VIX spikes** (fear) → 1-2 months later → **Wealth effect reverses**

We're between Steps 1-2. Curve dis-inverted. SLOOS tightening at +38%. Credit growth at +1.2% (barely positive). Spreads **haven't repriced yet**. That's the shoe waiting to drop.

---

## Integration with Three-Engine Framework

### Pillar 9 → Pillar 1 (Labor)

Financial conditions affect labor through **corporate access to capital**:

```
Credit Tightening → Cost of Capital ↑ →
Capex Deferred → Hiring Frozen → Payrolls ↓
```

**Transmission mechanics:** Financial conditions affect labor through two channels. First, the direct credit channel: tighter lending standards restrict business borrowing capacity, reducing capex and hiring within 2-4 quarters. Second, the indirect wealth channel: equity market performance affects consumer spending via wealth effects (Pillar 5), which feeds back into business revenue and employment decisions. The first channel typically dominates in credit-constrained environments; the second dominates in wealth-driven cycles.

**Cross-Pillar Signal:** When **FCI < -0.3** (conditions tightening) AND **LFI > +0.8** (labor fragile), layoff acceleration becomes likely within 2-4 quarters. The FCI-LFI cross-check complements the BCI-LFI and CCI-LFI cross-checks as the full set of labor-transmission signals.

---

### Pillar 9 → Pillar 2 (Prices)

Financial conditions affect inflation through **wealth effects and expectations**:

```
Equity Wealth ↑ → Consumer Spending ↑ → Demand-Pull Inflation
Equity Wealth ↓ → Consumer Spending ↓ → Disinflationary
```

**Transmission mechanics:** Equity wealth effects generate spending responses with MPC estimates of 2-4 cents per dollar for financial wealth (vs 5-8 cents for housing wealth, per Case-Quigley-Shiller). A 15% equity drawdown, which represents roughly $8-10T of household wealth destruction at current aggregate market cap levels, would reduce consumer spending by approximately 0.3-0.8 ppts over 2-4 quarters. This is the wealth effect's quantified contribution to the financial-to-inflation channel.

**Cross-Pillar Signal:** Loose financial conditions blunt disinflationary pressure via the wealth effect. When **FCI > +0.5** (very loose) and **PCI > +0.5** (elevated inflation), the wealth channel is supporting demand and working against disinflation. Tightening financial conditions would accelerate the "last mile" services inflation resolution.

---

### Pillar 9 → Pillar 3 (Growth)

Financial conditions are the **primary transmission** of monetary policy to growth:

```
Financial Conditions Loose → Credit Available →
Investment ↑ → Output ↑ → GDP ↑
Financial Conditions Tight → Credit Restricted →
Investment ↓ → Output ↓ → GDP ↓
```

**Transmission mechanics:** Financial conditions transmit to GDP with 2-4 quarter lag through investment decisions and wealth effects. Tight conditions reduce business capex (~20% of GDP) and suppress consumer spending (68% of GDP via wealth channel). A 0.5-point move in FCI (roughly equivalent to 150 bps of credit spread widening plus moderate equity correction) subtracts approximately 0.5-1 ppt from GDP growth over 4 quarters.

**Cross-Pillar Signal:** FCI-GCI divergence provides early warning. When FCI is loose but GCI is weak, the growth weakness reflects non-financial factors (trade, demographics, structural). If FCI tightens to match GCI weakness, financial tightening compounds the existing growth drag and typically tips mild slowdown into recession.

---

### Pillar 9 → Pillar 4 (Housing)

Financial conditions directly determine **mortgage rates and housing demand**:

```
10Y Yield ↑ + Mortgage Spread → Mortgage Rate ↑ →
Affordability ↓ → Housing Demand ↓ → Prices Stable/Down
```

**Transmission mechanics:** Mortgage rates equal 10Y Treasury yield plus mortgage spread (primary-secondary spread plus MBS OAS). Mortgage spreads compressed pre-2022 and have widened materially post-2022 due to: (1) MBS duration extension as refi optionality increased, (2) reduced Fed MBS purchases during QT, (3) bank reluctance to hold MBS after SVB episode exposed duration risk. Mortgage rates therefore respond to both 10Y Treasury moves and spread dynamics; a 50 bps 10Y decline with stable spreads moves mortgages 50 bps, but spread normalization can add or subtract 50+ bps.

**Cross-Pillar Signal:** Housing activity unfreezes when 30Y mortgage rate drops below ~6% combined with HCI above -0.3. Both conditions typically require FCI loosening (lower Treasury yields, tighter mortgage spreads). Until financial conditions ease, housing transaction volumes stay depressed regardless of income or demographic tailwinds.

---

### Pillar 9 → Pillar 5 (Consumer)

Financial conditions affect consumer through **wealth and credit availability**:

```
Equity Wealth ↑ → Wealth Effect → Spending ↑
Credit Available → Credit Card Limits ↑ → Spending Sustained
Credit Tightening → Limits Cut → Spending Constrained
```

**Transmission mechanics:** The consumer has two distinct financial-conditions transmission channels. Top-quintile households (who hold most equity wealth) respond to equity market performance through the wealth effect. Bottom-half households (who rely on credit access and hold minimal equity) respond to credit availability and borrowing rates (credit card APRs, auto loan rates, BNPL terms). Financial tightening affects these cohorts asymmetrically: equity drawdowns hit top quintile; credit tightening hits bottom half.

**Cross-Pillar Signal:** Consumer exposure to financial conditions is higher than aggregate data suggests. An equity drawdown exceeding 15% combined with SLOOS consumer-credit tightening above +20% creates simultaneous stress on both consumer cohorts. This configuration accelerates CCI deterioration and cross-pillar recession probability.

---

## Data Source Summary

| **Category** | **Primary Source** | **Frequency** | **Release Lag** | **FRED Availability** |
|---|---|---|---|---|
| **Credit Spreads** | ICE BofA | Daily | Real-time | Same day (BAMLH0A0HYM2, etc.) |
| **Yield Curve** | Treasury | Daily | Real-time | Same day (DGS2, DGS10, etc.) |
| **NFCI** | Chicago Fed | Weekly | ~2 days | Same day (NFCI) |
| **Bank Lending** | Fed H.8 | Weekly | ~5 days | Same day (BUSLOANS, etc.) |
| **SLOOS** | Fed | Quarterly | ~30 days | Fed website |
| **VIX/Equity** | CBOE/Exchanges | Daily | Real-time | Yahoo Finance, etc. |
| **Reserve Balances** | Fed H.4.1 | Weekly | ~1 day | Same day (WRBWFRBL) |
| **RRP/TGA** | NY Fed | Daily | Real-time | NY Fed website |
| **TIPS/Breakevens** | Treasury | Daily | Real-time | Same day (DFII10, T10YIE) |

**Critical Timing:** Credit spreads, VIX, and yields are **real-time**. SLOOS is quarterly (most lagging but most predictive). Use daily markets for nowcasting, SLOOS for 2-4 quarter forward view.

---

## Current State Assessment Template

*Last Updated: {{DATE}}*

### Primary Indicators

| **Indicator** | **Current** | **Prior** | **Δ** | **Threshold** | **Assessment** |
|---|---|---|---|---|---|
| **HY OAS** | {{HY_OAS}} | {{HY_OAS_PRIOR}} | {{HY_OAS_DELTA}} | <300 bps = Complacent | {{HY_OAS_ASSESSMENT}} |
| **HY OAS Percentile** | {{HY_PERCENTILE}} | {{HY_PERCENTILE_PRIOR}} | {{HY_PERCENTILE_DELTA}} | <10th = Extreme | {{HY_PERCENTILE_ASSESSMENT}} |
| **IG OAS** | {{IG_OAS}} | {{IG_OAS_PRIOR}} | {{IG_OAS_DELTA}} | <100 bps = Tight | {{IG_OAS_ASSESSMENT}} |
| **BBB OAS** | {{BBB_OAS}} | {{BBB_OAS_PRIOR}} | {{BBB_OAS_DELTA}} | >200 bps = Downgrade risk | {{BBB_OAS_ASSESSMENT}} |
| **CCC-B Spread** | {{CCCB_SPREAD}} | {{CCCB_SPREAD_PRIOR}} | {{CCCB_SPREAD_DELTA}} | <400 bps = Distressed mispriced | {{CCCB_SPREAD_ASSESSMENT}} |
| **10Y-2Y Spread** | {{CURVE_10Y2Y}} | {{CURVE_10Y2Y_PRIOR}} | {{CURVE_10Y2Y_DELTA}} | <0 bps = Inverted | {{CURVE_10Y2Y_ASSESSMENT}} |
| **10Y-3M Spread** | {{CURVE_10Y3M}} | {{CURVE_10Y3M_PRIOR}} | {{CURVE_10Y3M_DELTA}} | <0 bps = Fed's preferred inversion | {{CURVE_10Y3M_ASSESSMENT}} |
| **Chicago Fed NFCI** | {{NFCI}} | {{NFCI_PRIOR}} | {{NFCI_DELTA}} | >0 = Tighter than avg | {{NFCI_ASSESSMENT}} |
| **Real Fed Funds** | {{REAL_FFR}} | {{REAL_FFR_PRIOR}} | {{REAL_FFR_DELTA}} | >+1.5% = Restrictive | {{REAL_FFR_ASSESSMENT}} |
| **Real 10Y (TIPS)** | {{REAL_10Y}} | {{REAL_10Y_PRIOR}} | {{REAL_10Y_DELTA}} | >+2% = Headwind | {{REAL_10Y_ASSESSMENT}} |
| **VIX** | {{VIX}} | {{VIX_PRIOR}} | {{VIX_DELTA}} | <13 = Compression | {{VIX_ASSESSMENT}} |
| **MOVE Index** | {{MOVE}} | {{MOVE_PRIOR}} | {{MOVE_DELTA}} | >150 = Crisis | {{MOVE_ASSESSMENT}} |
| **MOVE/VIX Ratio** | {{MOVE_VIX}} | {{MOVE_VIX_PRIOR}} | {{MOVE_VIX_DELTA}} | >6x = Bond vol leading | {{MOVE_VIX_ASSESSMENT}} |
| **C&I Loan Growth YoY%** | {{CI_LOAN_YOY}} | {{CI_LOAN_YOY_PRIOR}} | {{CI_LOAN_YOY_DELTA}} | <+3% = Weak | {{CI_LOAN_YOY_ASSESSMENT}} |
| **SLOOS Net Tightening (Large)** | {{SLOOS_LARGE}} | {{SLOOS_LARGE_PRIOR}} | {{SLOOS_LARGE_DELTA}} | >+20% = Tightening | {{SLOOS_LARGE_ASSESSMENT}} |
| **SLOOS Net Tightening (Small)** | {{SLOOS_SMALL}} | {{SLOOS_SMALL_PRIOR}} | {{SLOOS_SMALL_DELTA}} | >+30% = Squeeze | {{SLOOS_SMALL_ASSESSMENT}} |
| **Equity Risk Premium** | {{ERP}} | {{ERP_PRIOR}} | {{ERP_DELTA}} | <2.5% = Expensive vs bonds | {{ERP_ASSESSMENT}} |
| **S&P 500 Forward P/E** | {{SPX_PE}} | {{SPX_PE_PRIOR}} | {{SPX_PE_DELTA}} | >21x = Euphoric | {{SPX_PE_ASSESSMENT}} |
| **Breadth (% >200DMA)** | {{BREADTH}} | {{BREADTH_PRIOR}} | {{BREADTH_DELTA}} | <40% = Narrow leadership | {{BREADTH_ASSESSMENT}} |
| **Reserve Balances** | {{RESERVES}} | {{RESERVES_PRIOR}} | {{RESERVES_DELTA}} | <$3.0T = Scarce | {{RESERVES_ASSESSMENT}} |
| **RRP Balance** | {{RRP}} | {{RRP_PRIOR}} | {{RRP_DELTA}} | <$100B = Exhausted | {{RRP_ASSESSMENT}} |
| **LCI** | {{LCI}} | {{LCI_PRIOR}} | {{LCI_DELTA}} | <-0.5 = Thin cushion | {{LCI_ASSESSMENT}} |

### Composites

| **Index** | **Current** | **Prior** | **Regime** | **Signal** |
|---|---|---|---|---|
| **FCI** | {{FCI}} | {{FCI_PRIOR}} | {{FCI_REGIME}} | {{FCI_SIGNAL}} |
| **Market-Pricing Sub-Composite** | {{MARKET_COMP}} | {{MARKET_COMP_PRIOR}} | {{MARKET_COMP_REGIME}} | {{MARKET_COMP_SIGNAL}} |
| **Banking Sub-Composite** | {{BANKING_COMP}} | {{BANKING_COMP_PRIOR}} | {{BANKING_COMP_REGIME}} | {{BANKING_COMP_SIGNAL}} |
| **Plumbing Sub-Composite** | {{PLUMBING_COMP}} | {{PLUMBING_COMP_PRIOR}} | {{PLUMBING_COMP_REGIME}} | {{PLUMBING_COMP_SIGNAL}} |
| **Real-Rate Sub-Composite** | {{REALRATE_COMP}} | {{REALRATE_COMP_PRIOR}} | {{REALRATE_COMP_REGIME}} | {{REALRATE_COMP_SIGNAL}} |
| **Divergence Score** | {{DIVERGENCE}} | {{DIVERGENCE_PRIOR}} | {{DIVERGENCE_REGIME}} | {{DIVERGENCE_SIGNAL}} |
| **Stress Stage (1-4)** | {{STRESS_STAGE}} | {{STRESS_STAGE_PRIOR}} | {{STRESS_STAGE_REGIME}} | {{STRESS_STAGE_SIGNAL}} |

### Cross-Pillar Linkages

| **Linkage** | **Current** | **Threshold** | **Status** |
|---|---|---|---|
| **FCI + LFI (financial-labor)** | {{FCI_LFI}} | FCI <-0.3 AND LFI >+0.8 = layoff acceleration | {{FCI_LFI_STATUS}} |
| **FCI + GCI (financial-growth)** | {{FCI_GCI}} | Both negative = recession catalyst | {{FCI_GCI_STATUS}} |
| **FCI + LCI (market vs plumbing)** | {{FCI_LCI}} | FCI loose + LCI thin = unstable | {{FCI_LCI_STATUS}} |
| **CLG (Credit-Labor Gap)** | {{CLG}} | <-1.0 = Credit too tight for labor reality OR Credit too loose | {{CLG_STATUS}} |

### Narrative Synthesis

{{NARRATIVE}}

**Translation:** {{TRANSLATION}}

**Divergence Analysis:**
- Market-priced signals: {{MARKET_SIGNAL_SUMMARY}}
- Bank-channel signals: {{BANK_SIGNAL_SUMMARY}}
- Plumbing signals: {{PLUMBING_SIGNAL_SUMMARY}}
- Real-rate signals: {{REALRATE_SIGNAL_SUMMARY}}

**Cross-Pillar Confirmation:**
- **Labor Pillar:** {{LABOR_CONFIRMATION}}
- **Growth Pillar:** {{GROWTH_CONFIRMATION}}
- **Prices Pillar:** {{PRICES_CONFIRMATION}}
- **Consumer Pillar:** {{CONSUMER_CONFIRMATION}}
- **Plumbing Pillar:** {{PLUMBING_CONFIRMATION}}

**Stress Stage Diagnosis:**
1. Risk Pricing Inflection: {{STAGE1_STATUS}}
2. Credit Channel Tightening: {{STAGE2_STATUS}}
3. Liquidity Stress: {{STAGE3_STATUS}}
4. Transmission Complete: {{STAGE4_STATUS}}

**MRI Contribution:** {{MRI_CONTRIBUTION}}

---

## Invalidation Criteria

### Bull Case (Conditions Stay Loose) Invalidation Thresholds

If the following occur **simultaneously for 3+ months**, the bearish financial thesis is invalidated:

✅ **HY OAS** stays below **350 bps** (spreads don't reprice)
✅ **SLOOS** shows **net easing** (<+10% tightening)
✅ **C&I Loan Growth** accelerates above **+5%** (credit flowing)
✅ **VIX** stays below **18** (vol remains suppressed)
✅ **10Y-2Y** steepens above **+75 bps** (healthy curve)
✅ **FCI** stays above **+0.3** (conditions remain loose)

**Action if Invalidated:** Financial conditions are **correctly pricing a soft landing**. Overweight **high-beta credit** (HYG, JNK), **financials** (XLF), **cyclicals**. Risk-on positioning warranted.

---

### Bear Case (Financial Stress) Confirmation Thresholds

If the following occur, financial conditions are **tightening into crisis**:

🔴 **HY OAS** exceeds **500 bps** (risk repricing)
🔴 **VIX** exceeds **30** (fear spike)
🔴 **NFCI** exceeds **+0.5** (tighter than average)
🔴 **SLOOS** exceeds **+50% net tightening** (credit crunch)
🔴 **10Y-2Y** inverts again **or** bear steepens >+100 bps (panic)
🔴 **SOFR-IORB** exceeds **+20 bps** (funding stress)
🔴 **FCI** drops below **-0.7** (crisis regime)

**Action if Confirmed:** Maximum defensive. Overweight **cash** (SGOV), **long Treasuries** (TLT), **gold** (GLD). Avoid **all credit risk** (HY, IG, financials). Financial stress = risk-off regime.

---

## Conclusion: Financial Conditions as the Transmission Mechanism

Financial conditions aren't just rates. They're the **transmission layer** that connects Fed policy to the real economy. And the layer routinely sends contradictory signals across its components.

**The Four-Stage Sequence:**
1. Risk Pricing Inflection (Stage 1): credit spreads widen, equity vol rises
2. Credit Channel Tightening (Stage 2): SLOOS tightens, loan growth decelerates
3. Liquidity Stress (Stage 3): funding markets strain, auctions tail, dealers stretch
4. Transmission Complete (Stage 4): defaults rise, earnings compress, real economy responds

**The Divergence Problem:** When market-priced signals (spreads, VIX) show loose conditions while bank-channel signals (SLOOS, loan growth) show tight conditions, the reading is unstable. Historical pattern: divergences typically resolve through spread widening to match bank-channel signals, not through bank-channel easing to match spreads. Banks have better borrower-level information than the credit market, and their aggregated judgment often proves correct.

**The Coiled Spring Dynamic:** Tight credit spreads, low equity volatility, and tight IG spreads can compress simultaneously. When they decompress, the moves tend to be abrupt because: (a) short-vol strategies force-cover on vol spikes, (b) credit liquidity is thinner than it appears (systemic hedge fund deleveraging), (c) correlation spikes during stress events flatten portfolio diversification. A 100 bps HY spread widening typically correlates with VIX spiking 8-12 points and equity drawdowns of 5-10%.

**The Policy Trap:** When the Fed faces simultaneous inflation pressure (PCI elevated) and financial stress (FCI deteriorating), it must choose between fighting inflation and preventing financial stress. In this configuration, the Fed typically prioritizes financial stability because stress is more immediately market-visible. Rate cuts follow. But this creates inflation risk if the stress abates without completing the cycle transmission. Late-cycle Fed decisions are binary; the optionality disappears.

**Cross-Pillar Framework:** Financial conditions are the amplifier of labor, consumer, and business dynamics. Loose conditions delay transmission of cross-pillar stress. Tight conditions accelerate it. Watch for FCI-LFI cross-checks, FCI-CCI via wealth effects, and FCI-BCI via credit channels as the three primary transmission dynamics.

The 2026 theme: financial conditions divergence, credit spread repricing risk, and the policy trap. The spring is coiled. The spark can come from anywhere.

---

## Additional Indicators & External Research

### Bernanke-Gertler Financial Accelerator

Ben Bernanke and Mark Gertler's financial accelerator framework (1989, 1999) argues that credit market frictions amplify business cycles. During expansions, collateral values rise, balance sheets strengthen, borrowing capacity grows, and credit flows freely. During contractions, the reverse: falling collateral values weaken balance sheets, reduce borrowing capacity, and amplify downturns through a credit contraction channel.

**Application:** The financial accelerator is why credit markets move faster than real economic fundamentals. When the HY market freezes, business investment collapses within quarters because small/mid-market firms lose access to marginal credit. Monitor HY primary market issuance as a real-time indicator of accelerator dynamics.

### Gilchrist-Zakrajsek Excess Bond Premium (EBP)

Simon Gilchrist and Egon Zakrajsek (Fed FEDS 2012) decomposed credit spreads into (a) a default-risk component and (b) an "excess bond premium" (EBP) reflecting investor risk aversion and intermediary balance sheet constraints. EBP is a superior recession predictor than raw spread levels.

**Application:** The Fed publishes the GZ Spread and EBP monthly. EBP above +0.5 standard deviations for 2+ months has historically preceded recessions by 4-6 quarters. The EBP is available at federalreserve.gov/econres/notes/feds-notes/.

### Adrian-Shin Intermediary Asset Pricing

Tobias Adrian and Hyun Song Shin developed a framework where broker-dealer balance sheet capacity drives asset prices. When dealers are well-capitalized and expanding balance sheets, risk assets rally and spreads compress. When dealers pull back, asset prices fall and spreads widen.

**Application:** Track primary dealer Treasury holdings and credit inventory as real-time intermediary capacity measures. Dealers retracting from market-making ahead of earnings or regulatory deadlines has repeatedly preceded liquidity events.

### Minsky Instability Hypothesis

Hyman Minsky's "Financial Instability Hypothesis" argues that stability breeds instability: prolonged calm periods lead to progressive risk-taking (hedge finance → speculative finance → Ponzi finance), culminating in crisis. The "Minsky moment" is when Ponzi-stage leverage is exposed.

**Application:** Extended periods of tight spreads, low vol, and compressed risk premia are Minsky-consistent warning periods. The longer the calm, the more leveraged the subsequent unwind. Post-2008 decade was a notable test case: extended calm, extreme accommodation, followed by 2020 shock and 2022 rate/inflation repricing.

### Credit-to-GDP Gap

The Basel III framework monitors "credit-to-GDP gap" as an early warning of credit cycles. Deviations of private non-financial credit from long-run trend above +10 ppts signal excessive credit expansion. Deviations below -10 ppts signal credit scarcity.

**Application:** The BIS publishes credit-to-GDP gap data quarterly for major economies. US gap declined from 2007 peaks (+15 ppts) to post-2010 trough (-10 ppts), then stabilized near trend. Current gap readings help assess whether credit markets are in expansion or correction phase.

### Shin's Global Financial Cycle

Hyun Song Shin and colleagues (BIS) demonstrate that US financial conditions drive a "global financial cycle" affecting EM capital flows, cross-border bank lending, and EM credit conditions. Dollar strength is the primary channel.

**Application:** When US financial conditions tighten, EM dollar debt servicing stress rises, EM credit spreads widen, and EM capital outflows accelerate. EM financial stress often leads US stress by 1-3 months because EM is the marginal absorber of dollar liquidity.

### Credit Impulse (BIS)

The credit impulse is the change in credit flow as a percentage of GDP. It's a more sensitive cycle indicator than credit stock levels.

```
Credit Impulse = ΔCredit Flow / GDP
```

Negative credit impulse means credit growth is slowing on a flow basis, which typically leads real economic deceleration by 2-4 quarters. The BIS publishes credit impulse data for major economies.

### Rey's Dilemma (Global Financial Cycle)

Hélène Rey (2013 Jackson Hole) argues that the "trilemma" of international economics (free capital, fixed FX, independent monetary policy) is actually a "dilemma": in a world of free capital flows, monetary policy is not independent because global financial cycles dominated by US policy constrain all open economies.

**Application:** When the Fed tightens, global financial conditions tighten regardless of other central banks' stances. This is why EM central banks often follow Fed moves even when domestic conditions don't warrant.

### The Bank-Dealer-Hedge Fund Nexus

Modern market-making relies on a chain: customers trade with dealers, dealers hedge through hedge funds (via derivatives), hedge funds hold offsetting risk in various formats. Stress in any link propagates to the others. The 2019 repo spike, 2020 Treasury dysfunction, and 2022 LDI crisis all reflected stress in this nexus.

**Application:** Monitor hedge fund leverage (ASFP data from NY Fed, SEC Form PF aggregates) and dealer positioning (NY Fed Primary Dealer data) as leading indicators of market liquidity risk.

### Non-Bank Financial Intermediation (NBFI)

Since 2008, a substantial portion of credit creation has migrated from banks to non-bank financial intermediaries (private credit, BDCs, hedge funds, mutual funds). FSB tracks NBFI assets globally at ~$240T. The key concern is that NBFI is less regulated and less transparent than banking.

**Application:** Track FSB Global Monitoring Report on NBFI for systemic risk commentary. Private credit AUM growth, BDC underwriting standards, and mutual fund bond holdings provide non-bank credit channel visibility.

### The Yield Curve Dead-Zone

The 2022-2024 period featured an unusual pattern: deep and sustained yield curve inversion without recession. This has led to debate about whether curve signals remain reliable post-QE/QT regime changes. Several hypotheses: (1) QE distorted term premium, obscuring the inversion signal, (2) strong fiscal impulse offset the curve's restrictive signal, (3) the dis-inversion (not inversion) is the true signal, still ahead.

**Practical rule:** Don't abandon the yield curve; decompose it. The 10Y-3M curve (Fed's preferred) and the 18-month forward rate minus current 3M (near-term forward spread) may provide cleaner signals than 10Y-2Y during unusual regime periods.

---

## External Research Sources

**Federal Reserve Resources:**
- [Chicago Fed NFCI](https://www.chicagofed.org/publications/nfci/index) - Weekly National Financial Conditions Index
- [Fed Financial Accounts (Z.1)](https://www.federalreserve.gov/releases/z1/) - Quarterly household and corporate balance sheet
- [Fed H.8 Commercial Bank Credit](https://www.federalreserve.gov/releases/h8/) - Weekly bank credit data
- [SLOOS](https://www.federalreserve.gov/data/sloos.htm) - Quarterly Senior Loan Officer Opinion Survey
- [Fed Financial Stability Report](https://www.federalreserve.gov/publications/financial-stability-report.htm) - Semi-annual financial stability assessment
- [Fed FEDS Working Papers](https://www.federalreserve.gov/econres/feds/index.htm) - Fed research on financial conditions
- [NY Fed Primary Dealer Data](https://www.newyorkfed.org/markets/desk-operations/primary-dealer-statistics) - Weekly dealer positions
- [NY Fed Policy Rate Expectations](https://www.newyorkfed.org/markets/primarydealer_survey_questions.html) - Dealer survey on Fed path
- [St. Louis Fed Financial Stress Index](https://fred.stlouisfed.org/series/STLFSI4) - Weekly stress composite
- [Kansas City Fed Financial Stress Index](https://www.kansascityfed.org/research/financial-stability-report/) - Monthly stress index
- [OFR Financial Stress Index](https://www.financialresearch.gov/financial-stress-index/) - Daily OFR stress gauge

**Market Data Sources:**
- [ICE BofA Bond Indices (FRED)](https://fred.stlouisfed.org/categories/32991) - Daily corporate bond OAS
- [Chicago Fed EBP (Excess Bond Premium)](https://www.federalreserve.gov/econres/notes/feds-notes/) - Monthly GZ Spread and EBP
- [CBOE Volatility Indices](https://www.cboe.com/us/options/products/) - VIX, VIX3M, SKEW, VVIX
- [ICE Credit Indices](https://www.ice.com/indices/fixed-income-indices) - Corporate OAS benchmarks

**International/Global Research:**
- [BIS Credit Statistics](https://www.bis.org/statistics/totcredit.htm) - Quarterly global credit data
- [BIS Global Liquidity Indicators](https://www.bis.org/statistics/gli.htm) - Monthly cross-border banking
- [FSB Global Monitoring Report on NBFI](https://www.fsb.org/work-of-the-fsb/financial-innovation-and-structural-change/non-bank-financial-intermediation/) - Annual non-bank data
- [IMF Global Financial Stability Report](https://www.imf.org/en/Publications/GFSR) - Semi-annual assessment

**Industry and Market Commentary:**
- [Goldman Sachs Financial Conditions Index](https://www.gspublishing.com/) - Daily, subscription
- [Bloomberg Financial Conditions Index](https://www.bloomberg.com/) - Subscription
- [Moody's Analytics Default Rates](https://www.moodys.com/) - Monthly default data
- [S&P Global Ratings](https://www.spglobal.com/ratings/) - Rating actions, distressed debt
- [SIFMA Bond Issuance Data](https://www.sifma.org/resources/research/) - Monthly US bond market data

---

## Reference: Published Analysis

**"Financial: The Cascade"** (Educational Series, 2026) is the published article version of this pillar. Available at `research.lighthousemacro.com/p/financial-the-cascade`.

The article covers:
- The four-stage financial conditions deterioration sequence
- Why credit spreads and banking channel signals often diverge, and why bank signals tend to win
- The financial accelerator mechanism and the EBP as a recession predictor
- The policy trap dynamics when fiscal stress meets financial stress
- The unbuffered plumbing amplification dynamic (Pillar 10 linkage)
- Invalidation criteria for both conditions-stay-loose and crisis scenarios

The article positions financial conditions as the transmission layer: Fed policy matters only to the extent it flows through financial conditions, and the composition of financial conditions (which channels are tight vs loose) determines real economy outcomes.

---

## Historical Validation

### Pattern Recognition

| **Episode** | **FCI** | **Key Signal** | **Outcome** | **Lead Time** |
|---|---|---|---|---|
| **Sep 1998 (LTCM)** | -0.8 | LTCM near-default, dealer balance sheet stress | Fed cuts Sept-Nov 1998; V-shaped recovery | Weeks-coincident |
| **Mid 2007** | +0.2 | HY spreads 300 bps, SLOOS beginning to tighten | Subprime stress growing; full GFC 12 months later | 6-12 months |
| **Sep 2008 (Lehman)** | -2.1 | HY OAS 1500+ bps, bank runs, money market freeze | Deep recession, TARP, QE1 | Coincident |
| **May 2011** | -0.5 | Euro sovereign stress, bank runs | Operation Twist, OMT | 6 months to resolution |
| **Aug 2015** | -0.6 | China devaluation, commodity collapse, HY energy | Brief risk-off, Fed hikes delayed | Weeks |
| **Dec 2018** | -0.7 | Fed tightening into slowdown, HY 500+ bps | Fed pivot Jan 2019; recovery | 3 months |
| **March 2020 (COVID)** | -1.8 | HY 1100 bps, Treasury market dysfunction | Emergency Fed action; QE infinite; V recovery | Coincident |
| **Oct-Dec 2022** | -0.4 | UK gilt crisis, Fed 75 bps hikes, HY 500 bps | Soft patch; crypto/tech stress | 1-2 months |
| **March 2023 (SVB)** | -0.3 | Regional bank runs, deposit flight | Fed emergency lending (BTFP); contained | Coincident |

### False Signals

**Late 2018 "Powell Pivot":** FCI tightened sharply Oct-Dec 2018 as Fed hiked and HY spreads widened to 500+ bps. Expected recession did not materialize because the Fed pivoted in January 2019, financial conditions reversed, and the economy re-accelerated. Lesson: Fed response function matters; FCI tightening can reverse quickly if Fed responds.

**March 2020 "Instant Recovery":** FCI dropped to -1.8 at peak COVID stress, but Fed intervention (emergency rate cuts, unlimited QE, emergency lending facilities) reversed conditions within weeks. Historic example of policy response breaking the transmission mechanism. Lesson: fiscal/monetary response capacity matters for how stress transmits.

**October 2023 Yield Spike:** 10Y yields rose to 5% in Oct 2023, tightening FCI meaningfully. Markets expected recession; instead, fiscal dominance dynamics reversed as Treasury adjusted issuance mix. Lesson: the supply-side of Treasury market matters as much as demand-side for yield dynamics.

### Structural Breaks

**Post-GFC Regulatory Regime:** Dodd-Frank bank capital requirements, Volcker Rule, and Basel III have changed bank-credit provision. Banks are better capitalized but less willing to warehouse inventory. Market-making capacity has declined, amplifying liquidity stress when it occurs.

**Non-Bank Financial Intermediation Growth:** NBFI (private credit, mutual funds, ETFs, hedge funds) has grown substantially post-2008. Credit creation increasingly happens outside banks, making SLOOS a less comprehensive measure. Watch private credit AUM and BDC data alongside traditional bank signals.

**Passive Investing Dominance:** Index funds and ETFs have grown to ~50% of equity AUM. This changes market microstructure: passive flows respond to money flow, not fundamentals. Concentrated top-of-index positions (FAANG/Mag 7) reflect passive flow concentration, complicating breadth signal interpretation.

**Post-SVB Regional Bank Fragility:** March 2023 SVB episode revealed digital-era deposit flight speed. Regional banks must hold more liquid assets; this constrains their lending capacity. SLOOS small-firm credit tightness may be structurally higher going forward.

**Central Bank Balance Sheet Regime:** Fed balance sheet expanded to ~$9T then contracted via QT to ~$7T. This represents a major shift from pre-2008 operating framework. QT has drained RRP but kept reserves ample; any future QT will need to be managed carefully to avoid 2019-style repo stress.

---

## Alternative & High-Frequency Data

| **Source** | **Indicator** | **Frequency** | **Access** | **Use Case** |
|---|---|---|---|---|
| **Chicago Fed NFCI** | Weekly FCI | Weekly | Free (FRED: NFCI) | Policy-weighted composite |
| **St. Louis Fed STLFSI4** | Weekly Financial Stress Index | Weekly | Free (FRED) | Stress-focused gauge |
| **Goldman Sachs FCI** | Daily FCI | Daily | Subscription | Widely-cited FCI |
| **Bloomberg FCI** | Daily FCI | Daily | Subscription | Alternative daily measure |
| **OFR Financial Stress Index** | Daily stress gauge | Daily | Free (financialresearch.gov) | Official sector view |
| **ICE BofA Bond Indices** | Daily OAS by rating | Daily | Free (FRED) | Credit spread benchmarks |
| **Fed EBP (Gilchrist-Zakrajsek)** | Monthly excess bond premium | Monthly | Free (Fed notes) | Forward-looking credit signal |
| **FRED H.8** | Weekly bank credit | Weekly | Free | Real-time lending |
| **FRED H.6** | Weekly money supply | Weekly | Free | Monetary aggregate |
| **CBOE VIX and family** | Daily volatility | Daily | Free | Equity vol complex |
| **ICE BAML MOVE Index** | Daily Treasury vol | Daily | Free summary | Bond volatility |
| **JP Morgan EMBI** | Daily EM sovereign | Daily | Subscription | Global credit signal |
| **Moody's Default Rates** | Monthly default rates | Monthly | Subscription summary | Realized credit losses |
| **S&P Distressed Debt** | Monthly distressed share | Monthly | Subscription | Leading default indicator |
| **CMBS Trepp Data** | CMBS delinquency, loss | Monthly | Subscription | CRE specific stress |
| **ICI Money Market Fund Data** | Weekly MMF AUM, composition | Weekly | Free (ici.org) | Money market dynamics |
| **DTCC Derivatives Data** | Daily derivatives activity | Daily | Free summaries | Derivatives leverage |

---

## Academic & Research Foundation

| **Paper/Framework** | **Author(s)** | **Key Insight** |
|---|---|---|
| "Financial Instability Hypothesis" (various, 1970s-1980s) | Hyman Minsky | Stability breeds instability; cycle progression from hedge → speculative → Ponzi |
| "Agency Costs, Net Worth, and Business Fluctuations" (1989) | Bernanke & Gertler | Financial accelerator: credit frictions amplify cycles |
| "The Financial Accelerator in a Quantitative Business Cycle Framework" (1999) | Bernanke, Gertler & Gilchrist | Quantitative framework for accelerator dynamics |
| "Credit Spreads as Predictors of Real-Time Economic Activity" (2012 FEDS) | Gilchrist & Zakrajsek | Excess Bond Premium (EBP) methodology |
| "Intermediary Asset Pricing" (2014 AEA) | Adrian, Etula, Muir | Broker-dealer balance sheet drives asset prices |
| "Liquidity and Leverage" (2010) | Adrian & Shin | Book-equity-to-asset ratios drive financial intermediary behavior |
| "The Global Financial Cycle" (2013 Jackson Hole) | Hélène Rey | US financial conditions drive global financial cycle |
| "Dilemma not Trilemma" (2013) | Hélène Rey | Monetary policy constrained by global cycle regardless of FX regime |
| "Safe Assets" (2018) | Gorton | Safe asset demand and financial fragility |
| "Banking and Macroprudential Policy" (various) | Hyun Song Shin | Bank-dealer-hedge fund nexus, cross-border spillovers |
| "Credit-to-GDP Gap" (BIS methodology) | Drehmann, Tsatsaronis | Basel III credit cycle early warning indicator |
| "Net Capital Flows, Global Imbalances" (various) | Caballero, Farhi, Gourinchas | Safe asset demand, persistent global imbalances |
| "ACM Term Premium" (various) | Adrian, Crump, Moench | Affine term structure model for term premium estimation |
| Non-Bank Financial Intermediation | FSB research | Post-GFC shift of credit from banks to NBFIs |
| Yield Curve Predictions | Estrella, Mishkin, Bauer, others | Curve inversion as recession predictor; variations by segment |

---

## FRED Series Reference Appendix

All FRED series codes referenced in this pillar, organized by category.

### Credit Spreads (Section A, I)

| **Series ID** | **Description** | **Frequency** |
|---|---|---|
| BAMLH0A0HYM2 | ICE BofA US High Yield OAS | Daily |
| BAMLC0A0CM | ICE BofA US Corporate OAS | Daily |
| BAMLC0A1CAAA | ICE BofA US AAA Corporate OAS | Daily |
| BAMLC0A2CAA | ICE BofA US AA Corporate OAS | Daily |
| BAMLC0A3CA | ICE BofA US A Corporate OAS | Daily |
| BAMLC0A4CBBB | ICE BofA US BBB Corporate OAS | Daily |
| BAMLH0A1HYBB | ICE BofA US BB Corporate OAS | Daily |
| BAMLH0A2HYB | ICE BofA US B Corporate OAS | Daily |
| BAMLH0A3HYC | ICE BofA US CCC and Below OAS | Daily |
| BAMLH0A0HYM2EY | ICE BofA US HY Effective Yield | Daily |

### Yield Curve (Sections B, J)

| **Series ID** | **Description** | **Frequency** |
|---|---|---|
| DGS2 | 2-Year Treasury Constant Maturity Rate | Daily |
| DGS3MO | 3-Month Treasury Constant Maturity Rate | Daily |
| DGS5 | 5-Year Treasury Constant Maturity Rate | Daily |
| DGS10 | 10-Year Treasury Constant Maturity Rate | Daily |
| DGS30 | 30-Year Treasury Constant Maturity Rate | Daily |
| T10Y2Y | 10-Year minus 2-Year Treasury Spread | Daily |
| T10Y3M | 10-Year minus 3-Month Treasury Spread | Daily |
| T5YIE | 5-Year Breakeven Inflation | Daily |
| T10YIE | 10-Year Breakeven Inflation | Daily |
| T5YIFR | 5-Year 5-Year Forward Inflation | Daily |
| DFII5 | 5-Year Treasury Inflation-Indexed Rate | Daily |
| DFII10 | 10-Year Treasury Inflation-Indexed Rate | Daily |
| DFII30 | 30-Year Treasury Inflation-Indexed Rate | Daily |

### Financial Conditions Indices (Section C)

| **Series ID** | **Description** | **Frequency** |
|---|---|---|
| NFCI | Chicago Fed National Financial Conditions Index | Weekly |
| ANFCI | Chicago Fed Adjusted NFCI | Weekly |
| STLFSI4 | St. Louis Fed Financial Stress Index | Weekly |
| NFCICREDIT | NFCI Credit Subindex | Weekly |
| NFCILEVERAGE | NFCI Leverage Subindex | Weekly |
| NFCINONFINLEVERAGE | NFCI Nonfinancial Leverage Subindex | Weekly |
| NFCIRISK | NFCI Risk Subindex | Weekly |

### Bank Lending (Section D, K)

| **Series ID** | **Description** | **Frequency** |
|---|---|---|
| BUSLOANS | Commercial and Industrial Loans, All Commercial Banks | Weekly |
| TOTLL | Total Loans and Leases in Bank Credit | Weekly |
| REALLN | Real Estate Loans, All Commercial Banks | Weekly |
| CONSUMER | Consumer Loans, All Commercial Banks | Weekly |
| DPSACBW027SBOG | Deposits, All Commercial Banks | Weekly |
| USGSEC | Treasury and Agency Securities, All Commercial Banks | Weekly |
| DRTSCLCC | Net Percentage Tightening Standards: C&I Loans to Large Firms | Quarterly |
| DRTSCLMSC | Net Percentage Tightening Standards: C&I Loans to Small Firms | Quarterly |
| DRTSCRE | Net Percentage Tightening Standards: CRE Loans | Quarterly |
| SUBLPDCLCSNQ | Net Percentage Tightening Standards: Credit Card Loans | Quarterly |

### Equity Markets (Section E, L)

| **Series ID** | **Description** | **Frequency** |
|---|---|---|
| SP500 | S&P 500 | Daily |
| NASDAQCOM | NASDAQ Composite | Daily |
| DJIA | Dow Jones Industrial Average | Daily |
| WILL5000INDFC | Wilshire 5000 Full Cap Index | Daily |

### Volatility (Section F, M)

| **Series ID** | **Description** | **Frequency** |
|---|---|---|
| VIXCLS | CBOE Volatility Index (VIX) | Daily |
| VXNCLS | CBOE NASDAQ-100 Volatility | Daily |

### Fed Funds and Policy Rates (Section G)

| **Series ID** | **Description** | **Frequency** |
|---|---|---|
| DFF | Effective Federal Funds Rate | Daily |
| DFEDTARU | Federal Funds Target Rate Upper Limit | Daily |
| DFEDTARL | Federal Funds Target Rate Lower Limit | Daily |
| IORB | Interest on Reserve Balances | Daily |
| SOFR | Secured Overnight Financing Rate | Daily |
| EFFR | Effective Federal Funds Rate | Daily |

### Plumbing and Liquidity (Section H)

| **Series ID** | **Description** | **Frequency** |
|---|---|---|
| WRBWFRBL | Reserve Balances with Federal Reserve Banks | Weekly |
| WLCFLPCL | Assets of Federal Reserve Banks | Weekly |
| WALCL | Total Assets: Federal Reserve | Weekly |
| RRPONTSYD | Overnight Reverse Repo Facility | Daily |
| WTREGEN | Treasury General Account Balance | Weekly |

### Dollar and Cross-Asset

| **Series ID** | **Description** | **Frequency** |
|---|---|---|
| DTWEXBGS | Broad US Dollar Index (Trade-Weighted) | Daily |
| DTWEXAFEGS | Advanced Foreign Economies Dollar Index | Daily |
| DTWEXEMEGS | Emerging Markets Dollar Index | Daily |
| DCOILWTICO | WTI Crude Oil Price | Daily |
| GOLDAMGBD228NLBM | Gold Fixing Price | Daily |

### Non-FRED Data Sources

| **Indicator** | **Source** | **Notes** |
|---|---|---|
| Goldman Sachs FCI | Goldman | Daily, subscription |
| Bloomberg FCI | Bloomberg | Daily, subscription |
| OFR Financial Stress Index | OFR | Daily, free from financialresearch.gov |
| Kansas City Fed Financial Stress Index | KC Fed | Monthly, free |
| Gilchrist-Zakrajsek EBP | Fed FEDS | Monthly, free (FEDS Notes) |
| SLOOS Detail by Loan Type | Fed | Quarterly, PDF |
| VIX Family (VIX3M, VIX9D, VIX6M, VVIX) | CBOE | Daily |
| SKEW Index | CBOE | Daily |
| MOVE Index | ICE BofA | Daily (limited free) |
| Primary Dealer Positions | NY Fed | Weekly |
| FSB NBFI Monitoring Report | FSB | Annual |
| BIS Credit Statistics | BIS | Quarterly |
| EMBI Global, CEMBI, GBI-EM | J.P. Morgan | Daily, subscription |
| Moody's Default Rates | Moody's | Monthly |
| S&P Distressed Ratio | S&P Global | Monthly |
| CMBS Delinquency (Trepp) | Trepp | Monthly |
| Private Credit AUM | Preqin, PitchBook | Quarterly |
| ICI Money Market Fund Statistics | ICI | Weekly |
| CBOE Options Activity | CBOE | Daily |

---

*Bob Sheehan, CFA, CMT*
*Founder & CIO, Lighthouse Macro*
*Last Updated: February 2026*
