# PILLAR 6: BUSINESS

## The Business Transmission Chain

Business activity isn't just corporate earnings. It's the **forward bet on demand**. The transmission mechanism operates through cascading investment and hiring decisions:

```
CEO Confidence → Capex Plans → Equipment Orders →
Production Schedules → Inventory Decisions →
Hiring Plans → Payroll Expansion →
Consumer Income → Final Demand →
CEO Confidence (Reinforcing Loop)
```

**The Insight:** Businesses are **leading indicators** because they commit capital 6-18 months before sales materialize. When CEOs cut capex, they're telling you demand will be weak before demand actually weakens. Listen to what they do, not what they say on earnings calls.

The beauty of business data: surveys capture **intentions**, orders capture **commitments**, and inventories capture **mistakes**. When orders collapse while inventories build, someone's forecast was wrong. That someone is usually the optimist.

---

## Why Business Matters: The Investment Multiplier

Business investment is the **most cyclical** GDP component. First to fall in recessions, first to rise in recoveries. It amplifies every cycle.

**The Cascade:**

**1. Business → Capex:** Equipment orders lead GDP by 3-6 months
**2. Business → Employment:** Hiring follows production plans (2-4 month lag)
**3. Business → Productivity:** Investment determines output per worker (long-term)
**4. Business → Inflation:** Capacity utilization determines pricing power (3-6 month lag)
**5. Business → Credit:** Corporate borrowing drives credit conditions (coincident)

Get the business call right, and you've captured the GDP growth rate 6 months forward. Miss it, and you're surprised by every earnings recession.

**The Four Stages of Business Cycle Deterioration:** Business downturns follow a sequence that mirrors (and partially drives) the consumer stress sequence. Knowing which stage you're in shapes positioning.

1. **Sentiment Inflection** (Leading): NFIB Optimism rolls over, regional Fed surveys turn negative, CEO Confidence falls. Intentions shift before action.
2. **Capex Retreat** (Leading-Coincident): Core capital goods orders go negative YoY, bookings/billings ratio drops below 1.0, SLOOS shows tightening. The forward commitment is being withdrawn.
3. **Manufacturing Recession** (Coincident): ISM Manufacturing below 50 for 3+ months, industrial production YoY negative, manufacturing employment contracts. Goods sector leads.
4. **Services Transmission** (Lagging): ISM Services breaks 50, earnings recession confirmed, services employment rolls over. Late-cycle bifurcation closes.

The bifurcation window (Stage 3 active, Stage 4 pending) is where late-cycle risk concentrates. Small business in collapse while large cap earnings hold, manufacturing in contraction while services expand, old economy weak while tech/AI invests through the cycle. These divergences are signatures of pre-recession stress, not stability. They close when the labor-to-consumer-to-business loop completes.

---

## Primary Indicators: The Complete Architecture

### A. SMALL BUSINESS SENTIMENT (The Canary)

Small businesses are 44% of GDP and 48% of employment. They're also **more rate-sensitive**, **less hedged**, and **first to feel pain**. NFIB is the canary in the coal mine.

| **Indicator** | **Source** | **Frequency** | **Lead/Lag** | **Interpretation** |
|---|---|---|---|---|
| **NFIB Small Business Optimism Index** | NFIB | Monthly | **Leads GDP 3-6 mo** | Headline sentiment |
| **NFIB: Plans to Increase Employment** | NFIB | Monthly | **Leads payrolls 2-4 mo** | Hiring intentions |
| **NFIB: Plans to Increase Capex** | NFIB | Monthly | **Leads business investment 3-6 mo** | Investment intentions |
| **NFIB: Expect Economy to Improve** | NFIB | Monthly | Leads GDP 4-6 mo | Economic outlook |
| **NFIB: Expect Higher Sales** | NFIB | Monthly | Leads revenue 3-4 mo | Demand expectations |
| **NFIB: Current Inventory Satisfaction** | NFIB | Monthly | Coincident | Inventory balance |
| **NFIB: Credit Conditions** | NFIB | Monthly | Coincident | Access to capital |
| **NFIB: Single Most Important Problem** | NFIB | Monthly | Thematic | Inflation vs labor vs demand |

#### Derived NFIB Metrics

| **Metric** | **Formula** | **Threshold** | **Signal** |
|---|---|---|---|
| **NFIB Momentum** | Current - 6M Avg | <-5 | Rapid deterioration |
| **Hiring Plans Net %** | % Higher - % Lower | <+5% | Hiring freeze imminent |
| **Capex Plans Net %** | % Higher - % Lower | <+20% | Investment pullback |
| **Sales Expectations Net %** | % Higher - % Lower | <-10% | Demand destruction |
| **Credit Difficulty %** | Harder to Get Credit | >+10% | Credit crunch |

#### Regime Thresholds: Small Business

| **Indicator** | **Recessionary** | **Weak** | **Normal** | **Strong** |
|---|---|---|---|---|
| **NFIB Optimism Index** | <90 | 90-95 | 95-102 | >102 |
| **Hiring Plans Net %** | <+5% | +5% to +12% | +12% to +20% | >+20% |
| **Capex Plans Net %** | <+20% | +20% to +25% | +25% to +30% | >+30% |
| **Economy Will Improve** | <-30% | -30% to -10% | -10% to +10% | >+10% |

**The NFIB Lead Pattern:** NFIB Optimism below 90 for 6+ consecutive months has preceded every post-1985 recession by 6-12 months. The component mix matters more than the headline: Hiring Plans net percentage below +10%, Capex Plans below +20%, and "Economy Will Improve" below -20% together form the late-cycle configuration. NFIB is the cleanest small-business read available. Small business is 44% of GDP and 48% of employment, more rate-sensitive than large firms, less hedged against cost shocks, and without access to the investment-grade bond market. When small business capitulates, it is typically 3-6 months ahead of large-cap earnings compression.

**Data note:** NFIB is not on FRED. Access via nfib.com monthly reports, or scrape the Small Business Economic Trends PDF released second Tuesday of each month.

---

### B. CAPITAL EXPENDITURE & ORDERS (The Forward Commitment)

Capex orders are commitments to future production capacity. When CEOs order equipment, they're betting on future demand. When they cancel orders, they're betting on weakness.

| **Indicator** | **FRED Code** | **Frequency** | **Lead/Lag** | **Interpretation** |
|---|---|---|---|---|
| **Durable Goods Orders** | DGORDER | Monthly | **Leads capex 3-6 mo** | Total durable orders |
| **Core Capital Goods Orders** | NEWORDER | Monthly | **Leads capex 4-8 mo** | Nondefense, ex-aircraft (purest) |
| **Core Capital Goods Shipments** | AMDMUO | Monthly | Coincident | Actual equipment deliveries |
| **Nondefense Capital Goods Orders** | AMDMNO | Monthly | Leads capex 3-6 mo | Business equipment ex-defense |
| **Defense Capital Goods Orders** | AMDMDE | Monthly | Lagging | Government procurement |
| **Aircraft Orders** | Boeing (web) | Monthly | Volatile | Lumpy, skip for trend |
| **Machinery Orders** | Census M3 | Monthly | Leads 3-6 mo | Industrial machinery |
| **Computer Orders** | Census M3 | Monthly | Leads 2-4 mo | Tech investment |

#### Derived Capex Metrics

| **Metric** | **Formula** | **Threshold** | **Signal** |
|---|---|---|---|
| **Core Capex Orders YoY%** | Current - Year Ago | <-3% | Investment pullback |
| **Orders-Shipments Spread** | Orders YoY - Shipments YoY | <-5 ppts | Backlog shrinking |
| **Capex Momentum** | 3M Avg YoY - 12M Avg YoY | <-3 ppts | Deceleration |
| **Bookings/Billings Ratio** | Orders / Shipments | <0.95 | Demand < Supply |
| **Durable Goods ex-Transport YoY%** | Core durables | <0% | Broad weakness |

#### Regime Thresholds: Capital Expenditure

| **Indicator** | **Contraction** | **Stagnation** | **Expansion** | **Boom** |
|---|---|---|---|---|
| **Core Capital Goods Orders YoY%** | <-5% | -5% to +2% | +2% to +8% | >+8% |
| **Durable Goods Orders YoY%** | <-3% | -3% to +3% | +3% to +10% | >+10% |
| **Orders-Shipments Spread** | <-8 ppts | -8 to -3 ppts | -3 to +3 ppts | >+3 ppts |
| **Bookings/Billings** | <0.90 | 0.90-0.98 | 0.98-1.05 | >1.05 |

**The Capex Lead Pattern:** Core capital goods orders (NEWORDER: nondefense ex-aircraft) is the purest forward capex signal. Negative YoY for 3+ consecutive months precedes earnings disappointments by 2-3 quarters because commitment decisions reflect demand forecasts made 6-12 months earlier. The bookings/billings ratio (orders/shipments) below 1.0 means backlog is shrinking, which forward-prices the next production cut.

**Historical benchmark:** In the 2001 recession, core capex orders went negative YoY in Q2 2000, eight months before the recession began. In 2008, they turned negative in Q4 2007, coincident with the official start but well ahead of the earnings collapse. In 2015-16 (manufacturing-only recession), they went negative but services held, and no broad recession followed. The signal has to combine with services-side weakness (Section E) to confirm a broad downturn.

---

### C. INVENTORIES (The Mistake Detector)

Inventories are the **buffer between production and sales**. When inventories build faster than sales, someone overestimated demand. Inventory liquidation is the mechanism that turns slowdowns into recessions.

| **Indicator** | **FRED Code** | **Frequency** | **Lead/Lag** | **Interpretation** |
|---|---|---|---|---|
| **Total Business Inventories** | BUSINV | Monthly | Coincident | Wholesale + retail + mfg |
| **Inventory/Sales Ratio (Total)** | ISRATIO | Monthly | **Leads recession 3-6 mo** | Overstock signal |
| **Manufacturing Inventories** | MNFCTRIRSA | Monthly | Coincident | Factory inventory |
| **Retail Inventories** | RETAILIRSA | Monthly | Coincident | Store inventory |
| **Wholesale Inventories** | WHLSLRIRSA | Monthly | Coincident | Distributor inventory |
| **Inventory/Sales Ratio (Retail)** | RETAILISR | Monthly | Leads retail 2-4 mo | Retail overstock |
| **Change in Private Inventories (GDP)** | CBI | Quarterly | Coincident | GDP inventory contribution |
| **ISM Manufacturing Inventories** | ISM | Monthly | Leading 1-2 mo | Survey-based |

#### Derived Inventory Metrics

| **Metric** | **Formula** | **Threshold** | **Signal** |
|---|---|---|---|
| **I/S Ratio vs Trend** | Current I/S - 5Y Avg I/S | >+0.05 | Overstocked |
| **Inventory Growth - Sales Growth** | Inv YoY - Sales YoY | >+5 ppts | Demand miss |
| **Inventory Correction Risk** | I/S Ratio × Inventory Growth | High combo | Liquidation coming |
| **ISM New Orders - Inventories** | New Orders - Inventories | <0 | Demand < Supply |

#### Regime Thresholds: Inventories

| **Indicator** | **Overstocked** | **Elevated** | **Balanced** | **Lean** |
|---|---|---|---|---|
| **Total Business I/S Ratio** | >1.45 | 1.38-1.45 | 1.30-1.38 | <1.30 |
| **Manufacturing I/S Ratio** | >1.55 | 1.45-1.55 | 1.35-1.45 | <1.35 |
| **Retail I/S Ratio** | >1.55 | 1.45-1.55 | 1.35-1.45 | <1.35 |
| **ISM Orders - Inventories** | <-5 | -5 to 0 | 0 to +5 | >+5 |

**The Inventory Liquidation Cycle:** When I/S ratios exceed trend by more than 0.05, inventory correction becomes a material GDP risk. The mechanism is mechanical: retailers discount to move product, manufacturers cut production schedules, hours are reduced before layoffs begin, and the GDP inventory subtraction takes 1-2 quarters to fully work through. ISM New Orders minus Inventories going below zero is an early warning: demand is weakening relative to supply before inventories peak.

**Historical benchmark:** The 2001 and 2008 recessions both featured pre-recession inventory buildups. I/S ratios peaked 3-6 months before formal recession onset. The 2015-16 manufacturing recession also featured elevated inventories but without broad recession, because services demand held up and allowed controlled liquidation. Watch the I/S ratio in combination with ISM New Orders: both negative for 2+ months is the clean signal.

---

### D. MANUFACTURING SURVEYS (The Forward-Looking Pulse)

PMIs and regional Fed surveys capture **business intentions**: what managers plan to do before they do it. Leading industrial production by 2-4 months.

| **Indicator** | **Source** | **Frequency** | **Lead/Lag** | **Interpretation** |
|---|---|---|---|---|
| **ISM Manufacturing PMI** | ISM | Monthly | **Leads IP 2-4 mo** | National manufacturing (>50 = expansion) |
| **ISM Manufacturing: New Orders** | ISM | Monthly | **Leads PMI 1-2 mo** | Demand signal |
| **ISM Manufacturing: Production** | ISM | Monthly | Coincident | Output gauge |
| **ISM Manufacturing: Employment** | ISM | Monthly | Leads payrolls 1-3 mo | Hiring intentions |
| **ISM Manufacturing: Supplier Deliveries** | ISM | Monthly | Coincident | Supply chain stress |
| **ISM Manufacturing: Prices Paid** | ISM | Monthly | Leads PPI 1-2 mo | Input cost pressure |
| **ISM Manufacturing: Backlog** | ISM | Monthly | Leads production 2-4 mo | Order pipeline |
| **Philly Fed Manufacturing** | Philadelphia Fed | Monthly | Leads ISM 1 mo | Regional bellwether |
| **Empire State Manufacturing** | NY Fed | Monthly | Leads ISM 1 mo | Regional bellwether |
| **Dallas Fed Manufacturing** | Dallas Fed | Monthly | Coincident | Energy-sensitive region |
| **Richmond Fed Manufacturing** | Richmond Fed | Monthly | Coincident | Southeast |
| **Kansas City Fed Manufacturing** | KC Fed | Monthly | Coincident | Midwest/Plains |
| **Chicago PMI** | MNI | Monthly | Leads ISM 0-1 mo | Industrial heartland |

#### Derived Survey Metrics

| **Metric** | **Formula** | **Threshold** | **Signal** |
|---|---|---|---|
| **ISM Composite Momentum** | Current - 3M Avg | <-3 | Rapid deterioration |
| **Regional Fed Average** | Avg of Philly, Empire, Dallas, etc. | <0 | Broad contraction |
| **New Orders - Inventories** | ISM subcomponents | <0 | Demand < Supply |
| **Employment - Production Gap** | Employment - Production | <-5 | Layoffs coming |
| **Prices Paid Trend** | Current - 6M Avg | <-10 | Disinflation in pipeline |

#### Regime Thresholds: Manufacturing Surveys

| **Indicator** | **Deep Contraction** | **Contraction** | **Neutral** | **Expansion** |
|---|---|---|---|---|
| **ISM Manufacturing** | <45 | 45-48 | 48-52 | >52 |
| **ISM New Orders** | <45 | 45-50 | 50-55 | >55 |
| **Philly Fed Index** | <-20 | -20 to -5 | -5 to +10 | >+10 |
| **Empire State Index** | <-15 | -15 to 0 | 0 to +10 | >+10 |

**The Manufacturing Lead Pattern:** ISM Manufacturing below 50 for 6+ consecutive months is a durable manufacturing contraction. Whether it transmits to a broad recession depends on the services side (Section E) and labor fragility (Pillar 1). Manufacturing recessions without broad transmission are common (1995-96, 2015-16). Manufacturing recessions that do transmit to services have preceded every broad US recession since 1970.

**The sub-components:** ISM New Orders below 48 signals demand weakness, Employment below 48 signals hiring pullback ahead of payroll declines, Supplier Deliveries above 50 signals either real supply chain stress or inventory overhang working through. Watch the composite: New Orders minus Inventories < 0 for 2+ months is the cleanest sub-50 confirmation.

**Regional Fed ensemble:** The Philadelphia, New York (Empire State), Dallas, Richmond, and Kansas City Fed manufacturing indexes collectively lead ISM by 1-3 weeks due to earlier release. Philadelphia Fed has the longest continuous history and strongest national correlation. The simple average of the five regional indexes is a useful ISM preview.

---

### E. SERVICES SURVEYS (The 80% of Economy)

Services are 80% of GDP and employment. Manufacturing gets the headlines, but services determine the economy's fate.

| **Indicator** | **Source** | **Frequency** | **Lead/Lag** | **Interpretation** |
|---|---|---|---|---|
| **ISM Services PMI** | ISM | Monthly | Coincident | National services (>50 = expansion) |
| **ISM Services: Business Activity** | ISM | Monthly | Coincident | Output gauge |
| **ISM Services: New Orders** | ISM | Monthly | **Leads PMI 1-2 mo** | Demand signal |
| **ISM Services: Employment** | ISM | Monthly | Coincident | Hiring gauge |
| **ISM Services: Prices Paid** | ISM | Monthly | Leads services CPI 1-2 mo | Cost pressure |
| **S&P Global Services PMI** | S&P Global | Monthly | Coincident | Alternative gauge |
| **S&P Global Composite PMI** | S&P Global | Monthly | Coincident | Mfg + Services weighted |

#### Derived Services Metrics

| **Metric** | **Formula** | **Threshold** | **Signal** |
|---|---|---|---|
| **Services-Manufacturing Spread** | Services PMI - Mfg PMI | >+10 | Bifurcation (late-cycle) |
| **Services Momentum** | Current - 6M Avg | <-3 | Deceleration |
| **Services New Orders Trend** | 3M Avg - 12M Avg | <-5 | Demand fading |

#### Regime Thresholds: Services Surveys

| **Indicator** | **Contraction** | **Weak** | **Normal** | **Strong** |
|---|---|---|---|---|
| **ISM Services** | <50 | 50-52 | 52-56 | >56 |
| **ISM Services New Orders** | <50 | 50-53 | 53-58 | >58 |
| **ISM Services Employment** | <48 | 48-52 | 52-55 | >55 |

**The Services-Manufacturing Divergence:** A services-manufacturing PMI spread above +5 points (services higher) is characteristic of late-cycle mid-transmission, when manufacturing has already rolled over but services haven't yet. The divergence historically closes within 2-4 quarters, either through services rolling over (recession scenario) or manufacturing reaccelerating (soft landing scenario). Watch the services sub-components, especially New Orders and Employment, as the confirmation signals. When services New Orders drops below 52 and Employment below 50, services transmission has begun.

**ISM vs S&P Global Services:** S&P Global (formerly Markit) produces a separate services PMI that often diverges from ISM by 2-5 points. Methodology differences: S&P Global samples more small-to-mid firms; ISM samples larger enterprises with greater international exposure. In late-cycle periods, cross-check both for signal robustness.

---

### F. CORPORATE PROFITS & MARGINS (The Bottom Line)

Profits are the ultimate outcome: what's left after revenue, costs, and interest. Margin compression precedes layoffs and capex cuts, typically by 2-4 quarters.

| **Indicator** | **FRED Code** | **Frequency** | **Lead/Lag** | **Interpretation** |
|---|---|---|---|---|
| **Corporate Profits After Tax** | CP | Quarterly | Lagging 1-2 qtrs | NIPA profits |
| **Corporate Profits / GDP** | Derived | Quarterly | Lagging | Profit share of economy |
| **S&P 500 Operating Earnings** | S&P (web) | Quarterly | Coincident | Large cap profits |
| **S&P 500 Earnings YoY%** | Derived | Quarterly | Coincident | Earnings growth |
| **S&P 500 Net Profit Margin** | S&P (web) | Quarterly | **Leads layoffs 2-4 qtrs** | Margin pressure |
| **S&P 500 Revenue YoY%** | S&P (web) | Quarterly | Coincident | Top-line growth |
| **Unit Labor Costs** | ULCNFB | Quarterly | Lagging | Labor cost pressure |
| **Earnings Revisions** | FactSet (web) | Weekly | **Leading 1-3 mo** | Analyst sentiment |

#### Derived Profit Metrics

| **Metric** | **Formula** | **Threshold** | **Signal** |
|---|---|---|---|
| **Profit Margin Change** | Current Margin - Year Ago | <-1 ppt | Compression |
| **Revenue-Earnings Gap** | Revenue YoY - Earnings YoY | >+5 ppts | Margin squeeze |
| **Earnings Revision Ratio** | Upgrades / (Upgrades + Downgrades) | <0.45 | Negative momentum |
| **Profit Growth Momentum** | Current YoY - 4Q Avg YoY | <-5 ppts | Deceleration |
| **ULC Growth vs Productivity** | ULC YoY - Productivity YoY | >+2 ppts | Margin pressure |

#### Regime Thresholds: Profits

| **Indicator** | **Contraction** | **Pressure** | **Stable** | **Expansion** |
|---|---|---|---|---|
| **S&P 500 Earnings YoY%** | <-10% | -10% to 0% | 0% to +10% | >+10% |
| **S&P 500 Net Margin** | <10% | 10-11% | 11-12.5% | >12.5% |
| **Earnings Revision Ratio** | <0.40 | 0.40-0.50 | 0.50-0.60 | >0.60 |
| **Corporate Profits/GDP** | <9% | 9-10% | 10-11% | >11% |

**The Margin Compression Signal:** When revenue growth exceeds earnings growth (revenue-earnings gap positive by +3 ppts or more) for 2+ consecutive quarters, margin compression is structural and cost-cutting becomes likely. The driver is typically unit labor costs rising faster than productivity (ULC YoY minus OPHNFB YoY > +2 ppts). Once this configuration appears, layoff announcements typically follow by 2-4 quarters as management protects margins.

**The Earnings Revisions Ratio:** The ratio of upward to total analyst revisions (Refinitiv, FactSet, Bloomberg compile this) is the highest-frequency forward-earnings signal available. Ratio below 0.45 for 3+ months confirms negative momentum in analyst expectations. This often leads reported earnings disappointments by 1-2 quarters. Combine with ISM Manufacturing new orders for a robust profit-cycle read.

**The Corporate Profits/GDP Ratio:** NIPA corporate profits divided by GDP is a stationary series that mean-reverts. Peaks around 11-12% of GDP; troughs around 6-8% during recessions. Watch the direction change from a cycle peak, not the level. Levels above 10% sustained for 2+ years historically precede recessions because they invite labor-cost rebalancing (rising wage share) and policy responses (tax reform, antitrust).

---

### G. BUSINESS CREDIT & FINANCING (The Capital Constraint)

Business credit conditions determine whether companies can fund capex, inventories, and operations. Tightening precedes slowdowns.

| **Indicator** | **Source** | **Frequency** | **Lead/Lag** | **Interpretation** |
|---|---|---|---|---|
| **SLOOS: Tightening Standards (C&I Large)** | Fed | Quarterly | **Leads lending 2-4 qtrs** | Bank willingness to lend |
| **SLOOS: Tightening Standards (C&I Small)** | Fed | Quarterly | Leads lending 2-4 qtrs | Small business access |
| **SLOOS: Loan Demand (C&I)** | Fed | Quarterly | Coincident | Business borrowing appetite |
| **C&I Loan Growth YoY%** | Fed H.8 | Weekly | Coincident | Actual lending activity |
| **High Yield Spreads (OAS)** | FRED | Daily | **Leads stress 3-6 mo** | Credit risk pricing |
| **Investment Grade Spreads** | FRED | Daily | Leads stress 2-4 mo | Corporate bond risk |
| **Commercial Paper Rates** | FRED | Daily | Coincident | Short-term funding cost |
| **Bankruptcy Filings** | ABI | Monthly | Lagging 3-6 mo | End-stage stress |

#### Derived Credit Metrics

| **Metric** | **Formula** | **Threshold** | **Signal** |
|---|---|---|---|
| **Net Tightening (Large Firms)** | % Tightening - % Easing | >+20% | Credit crunch |
| **Net Tightening (Small Firms)** | % Tightening - % Easing | >+30% | Small biz squeeze |
| **Loan Demand Net %** | % Stronger - % Weaker | <-10% | Demand destruction |
| **C&I Loan Momentum** | Current YoY - 6M Ago YoY | <-5 ppts | Credit contraction |
| **HY Spread Level** | Current OAS | >450 bps | Stress elevated |

#### Regime Thresholds: Business Credit

| **Indicator** | **Crisis** | **Tight** | **Neutral** | **Easy** |
|---|---|---|---|---|
| **SLOOS Net Tightening (Large)** | >+40% | +20% to +40% | 0% to +20% | <0% |
| **SLOOS Net Tightening (Small)** | >+50% | +30% to +50% | +10% to +30% | <+10% |
| **C&I Loan Growth YoY%** | <-5% | -5% to +3% | +3% to +8% | >+8% |
| **HY OAS** | >600 bps | 400-600 bps | 300-400 bps | <300 bps |

**The SLOOS Lead Pattern:** The Senior Loan Officer Opinion Survey is quarterly, Fed-administered, and released 2 weeks after each FOMC meeting. Net tightening in C&I standards (% tightening minus % easing) is the cleanest forward credit signal available. Net tightening above +20% for large firms, +30% for small firms, is the late-cycle configuration. The signal leads C&I loan growth by 2-4 quarters because tightened underwriting takes time to show in stock data.

**The Small-Large Credit Bifurcation:** Small firms (<250 employees) rely disproportionately on bank credit, while large firms access the investment-grade bond market directly. In late cycles, the spread between small-firm and large-firm SLOOS tightening widens as banks preserve capital and shift toward larger, better-collateralized borrowers. Small-firm tightening above +40% combined with small-business bankruptcy filings rising is a specific signal of small-business squeeze.

**HY Spread Integration:** High-yield OAS is a real-time market proxy for business credit stress. Tight spreads (below 300 bps) can coexist with tightening bank standards in early-cycle periods, but persistent divergence is unstable. Either spreads widen to reflect bank-level caution, or SLOOS loosens. Watch for spread widening combined with tightening SLOOS as the "credit reversal" signal that historically precedes earnings downgrades by 2-3 quarters.

---

### H. BUSINESS INVESTMENT GDP (The Realized Commitment)

GDP business investment components show what actually happened: the lagging confirmation of forward-looking order data.

| **Indicator** | **FRED Code** | **Frequency** | **Lead/Lag** | **Interpretation** |
|---|---|---|---|---|
| **Nonresidential Fixed Investment** | PNFI | Quarterly | Lagging 1-2 qtrs | Total business capex |
| **Equipment Investment** | Y033RC1Q027SBEA | Quarterly | Lagging | Machinery, computers, vehicles |
| **Structures Investment** | B009RC1Q027SBEA | Quarterly | Lagging | Commercial buildings, factories |
| **Intellectual Property Investment** | Y001RC1Q027SBEA | Quarterly | Lagging | Software, R&D |
| **Business Investment Contribution to GDP** | Derived | Quarterly | Lagging | Percentage point impact |

#### Derived Investment Metrics

| **Metric** | **Formula** | **Threshold** | **Signal** |
|---|---|---|---|
| **Business Investment YoY%** | Current - Year Ago | <0% | Contraction |
| **Equipment vs IP Spread** | Equipment YoY - IP YoY | <-10 ppts | Traditional capex weak |
| **Investment/GDP Ratio** | PNFI / GDP | <13% | Underinvestment |
| **Investment Contribution** | Weight × Growth | <0 ppts | Drag on GDP |

#### Regime Thresholds: Business Investment GDP

| **Indicator** | **Contraction** | **Stagnation** | **Normal** | **Strong** |
|---|---|---|---|---|
| **Nonres Fixed Investment QoQ Ann** | <-3% | -3% to +2% | +2% to +6% | >+6% |
| **Equipment Investment QoQ Ann** | <-5% | -5% to +2% | +2% to +8% | >+8% |
| **Structures Investment QoQ Ann** | <-8% | -8% to 0% | 0% to +5% | >+5% |
| **Investment/GDP Ratio** | <12% | 12-13% | 13-14% | >14% |

**The Investment Stall:** Nonresidential fixed investment at **+2.1% QoQ Ann** (Q3 2025)—barely positive. Equipment at **-1.2%** (contracting). Structures at **+4.8%** (held up by data center and reshoring). IP at **+3.5%** (software, AI). The composition is shifting: **traditional capex collapsing** while tech/AI investment holds up. This is not broad-based strength.

---

## Business Pillar Composite Index (BCI)

### Formula

The Business Pillar Composite synthesizes small business sentiment, capex, surveys, profits, and credit into a single business health indicator:

```
BCI = 0.20 × z(NFIB_Optimism)
    + 0.20 × z(Core_Capex_Orders_YoY)
    + 0.15 × z(ISM_Manufacturing)
    + 0.15 × z(ISM_Services)
    + 0.10 × z(-Inventory_Sales_Ratio)           # Inverted (high I/S = weak)
    + 0.10 × z(SP500_Earnings_YoY)
    + 0.05 × z(-SLOOS_Net_Tightening)            # Inverted (tightening = weak)
    + 0.05 × z(-HY_Spreads)                      # Inverted (wide = weak)
```

**Component Weighting Rationale:**
- **NFIB Optimism (20%):** Small business canary, most rate-sensitive
- **Core Capex Orders (20%):** Forward commitment, purest investment signal
- **ISM Manufacturing (15%):** Goods economy, leading indicator
- **ISM Services (15%):** 80% of economy, breadth gauge
- **Inventory/Sales (10%):** Mistake detector (inverted)
- **S&P 500 Earnings (10%):** Profit outcome
- **SLOOS Tightening (5%):** Credit availability (inverted)
- **HY Spreads (5%):** Credit risk pricing (inverted)

### Interpretation

| **BCI Range** | **Regime** | **Cyclical Allocation** | **Signal** |
|---|---|---|---|
| > +1.0 | Business Boom | Overweight industrials, small caps | Full expansion |
| +0.5 to +1.0 | Expansion | Neutral cyclicals | Healthy growth |
| -0.5 to +0.5 | Neutral/Slowing | Underweight small caps | Deceleration |
| -1.0 to -0.5 | Contraction | **Avoid small caps, underweight cyclicals** | Earnings recession |
| < -1.0 | Crisis | Maximum defensive | Broad recession |

### Historical Calibration

| **Period** | **BCI** | **Regime** | **Outcome (12M Forward)** |
|---|---|---|---|
| **Dec 2006** | +0.2 | Neutral | Earnings peaked, recession coming |
| **Dec 2007** | -0.8 | Contraction | Deep earnings recession |
| **Dec 2011** | +0.1 | Neutral | European crisis, mild slowdown |
| **Dec 2015** | -0.3 | Slowing | Manufacturing recession, no broad downturn |
| **Dec 2019** | +0.5 | Expansion | Pre-COVID strength |
| **Dec 2021** | +1.1 | Boom | Peak earnings, capex surge |
| **Dec 2023** | +0.3 | Neutral | Normalization |
| **Dec 2025** | **-0.4** | **Slowing** | **Late-cycle stress** |

**Current Assessment (Dec 2025):** BCI at **-0.4** places business in "Neutral/Slowing" regime—not crisis, but clear deterioration:
- **NFIB at 89.4** (lowest since 2012, below 90 threshold)
- **Core capex orders at -2.8% YoY** (contracting)
- **ISM Manufacturing at 49.3** (26-month contraction)
- **ISM Services at 54.1** (still expanding, but divergence)
- **I/S ratio at 1.41** (elevated, liquidation risk)
- **S&P 500 earnings at +4% YoY** (positive but decelerating)
- **SLOOS tightening at +28%** (banks cautious)
- **HY spreads at 290 bps** (tight but widening)

The bifurcation is stark: **small business collapsing**, **large cap holding**. **Manufacturing in recession**, **services expanding**. This is late-cycle—the divergences close as services follow manufacturing down.

---

## Lead/Lag Relationships: The Business Cascade

```
LEADING                           COINCIDENT                  LAGGING
────────────────────────────────────────────────────────────────────────────────────
│                                 │                          │
│  NFIB Optimism (3-6 mo)         │  ISM Manufacturing       │  Corporate Profits (1-2 qtrs)
│  Core Capex Orders (4-8 mo)     │  ISM Services            │  GDP Business Investment
│  ISM New Orders (2-4 mo)        │  Industrial Production   │  Bankruptcy Filings
│  SLOOS Tightening (2-4 qtrs)    │  C&I Loan Growth         │  S&P 500 Earnings (reported)
│  Philly Fed (1 mo)              │  Inventory Levels        │  Employment Cost Index
│  Earnings Revisions (1-3 mo)    │  Profit Margins          │  Unit Labor Costs
│  HY Spread Widening (3-6 mo)    │  Business Activity       │  Charge-offs
│  Capex Plans (3-6 mo)           │                          │
│                                 │                          │
────────────────────────────────────────────────────────────────────────────────────
```

**The Critical Chain:**

**1. NFIB collapses** (small biz sees trouble) → 3-6 months later → **Hiring slows**
**2. Capex orders fall** (CEOs cut investment) → 4-8 months later → **Equipment production drops**
**3. ISM Manufacturing contracts** → 6-9 months later → **Services follows**
**4. Inventories build** → 3-6 months later → **Production cuts to liquidate**
**5. Margins compress** → 2-4 quarters later → **Layoffs and restructuring**

We're currently at Steps 1-3: NFIB collapsed, capex orders contracting, manufacturing in 26-month recession, services still expanding but the divergence is closing.

---

## Integration with Three-Engine Framework

### Pillar 6 → Pillar 1 (Labor)

Business decisions drive **hiring and firing**:

```
Business Confidence ↓ → Hiring Plans ↓ →
Capex Cuts → Employment Growth ↓ →
Layoffs → Unemployment ↑ → Consumer Income ↓
```

**Current Linkage:** NFIB Hiring Plans at +8% (barely positive). ISM Employment at 46.8 (manufacturing shedding). Small business drives 48% of employment—when NFIB collapses, payrolls follow 3-6 months later.

**Cross-Pillar Signal:** When **BCI < -0.3** (business slowing) AND **LFI > +0.8** (labor fragile), recession probability exceeds 65% within 12 months. Current: **BCI -0.4, LFI +0.93**. **Warning threshold engaged.**

---

### Pillar 6 → Pillar 2 (Prices)

Business pricing power drives **inflation**:

```
Capacity Utilization ↓ → Pricing Power ↓ →
Output Gap Widens → Goods Disinflation →
Services Eventually Follow
```

**Current Linkage:** Capacity utilization at 77.4% (below 79% average)—slack building. ISM Prices Paid falling. Goods CPI at -1.2% (deflation). Business weakness is **disinflationary**—supports the "last mile" resolution.

**Cross-Pillar Signal:** Business weakness (**BCI -0.4**) + falling capacity utilization = goods deflation continues. Services inflation (wage-driven) next to fall as business cuts labor costs.

---

### Pillar 6 → Pillar 3 (Growth)

Business investment is **18% of GDP** and the most cyclical component:

```
Capex ↓ → GDP Business Investment ↓ →
Equipment Production ↓ → Industrial Production ↓ →
GDP Growth ↓
```

**Current Linkage:** Core capex orders at -2.8% YoY. Equipment investment at -1.2% QoQ Ann. Business fixed investment contributing ~0 ppts to GDP (Q3 2025). If capex continues to contract, GDP takes a direct hit.

**Cross-Pillar Signal:** When **BCI < -0.5** (business contraction) AND **GCI < -0.5** (growth contraction), recession confirmed. Current: **BCI -0.4, GCI -0.4**. Close to synchronized weakness.

---

### Pillar 6 → Pillar 5 (Consumer)

Business health determines **consumer income**:

```
Business Profits ↓ → Cost Cutting → Layoffs →
Consumer Income ↓ → Consumer Spending ↓ →
Business Revenue ↓ (Reinforcing)
```

**Current Linkage:** S&P 500 margins compressing (11.2% vs 12.8% peak). Earnings revisions turning negative. Cost cutting underway (layoffs announced). This feeds into consumer income with 2-4 quarter lag.

**Cross-Pillar Signal:** Business margin compression (**BCI earnings component weak**) precedes consumer stress (**CCI < -0.5**) by 2-4 quarters. Business is the leading indicator, consumer is the lagging confirmation.

---

### Pillar 6 → Pillar 9 (Financial)

Business credit affects **bank balance sheets** and **market conditions**:

```
Business Defaults ↑ → Bank Loan Losses ↑ →
Credit Tightening → Lending ↓ →
Business Investment ↓ (Reinforcing)
```

**Current Linkage:** SLOOS showing +28% net tightening for large firms, +42% for small firms. C&I loan growth at +1.8% (barely positive). HY spreads at 290 bps (tight but widening). Banks are cautious. The credit channel is tightening—this constrains business activity going forward.

**Cross-Pillar Signal:** Business credit tightening (**SLOOS elevated**) combined with HY spread widening (**>350 bps**) creates negative feedback loop. Monitor for acceleration.

---

## Data Source Summary

| **Category** | **Primary Source** | **Frequency** | **Release Lag** | **FRED Availability** |
|---|---|---|---|---|
| **NFIB** | NFIB | Monthly | ~10 days | Web scrape (not in FRED) |
| **Durable Goods Orders** | Census | Monthly | ~26 days | Same day (DGORDER, NEWORDER) |
| **ISM Manufacturing** | ISM | Monthly | 1st business day | Web scrape (not in FRED) |
| **ISM Services** | ISM | Monthly | 3rd business day | Web scrape (not in FRED) |
| **Business Inventories** | Census | Monthly | ~45 days | Same day (BUSINV, ISRATIO) |
| **SLOOS** | Fed | Quarterly | ~2 weeks after FOMC | PDF (not in FRED) |
| **Corporate Profits** | BEA | Quarterly | ~30 days | Same day (CP) |
| **S&P 500 Earnings** | S&P/FactSet | Quarterly | During earnings season | Proprietary |
| **Regional Fed Surveys** | Regional Feds | Monthly | ~15-20 days | Some in FRED |
| **HY Spreads** | ICE/FRED | Daily | Real-time | Same day (BAMLH0A0HYM2) |

**Critical Timing:** ISM released first business day of month is the **earliest signal**. NFIB mid-month. Durable goods ~26th. Use regional Fed surveys (Philly, Empire) to preview ISM by 2-3 weeks.

---

## Current State Assessment (January 2026)

| **Indicator** | **Current** | **Threshold** | **Assessment** |
|---|---|---|---|
| **NFIB Optimism** | 89.4 | <90 = recessionary | 🔴 **Lowest since 2012** |
| **NFIB Hiring Plans** | +8% | <+10% = hiring freeze | 🟡 Barely positive |
| **Core Capex Orders YoY%** | -2.8% | <-3% = contraction | 🔴 **Contracting** |
| **ISM Manufacturing** | 49.3 | <48 = deep contraction | 🟡 **26-month contraction** |
| **ISM Services** | 54.1 | <52 = weak | 🟢 Still expanding |
| **Inventory/Sales Ratio** | 1.41 | >1.40 = overstocked | 🟡 **Elevated** |
| **S&P 500 Earnings YoY%** | +4% | <0% = earnings recession | 🟢 Positive but slowing |
| **S&P 500 Net Margin** | 11.2% | <11% = compression | 🟡 Compressing |
| **SLOOS Net Tightening (Large)** | +28% | >+20% = tight | 🟡 **Banks cautious** |
| **SLOOS Net Tightening (Small)** | +42% | >+30% = squeeze | 🔴 **Small biz squeeze** |
| **HY Spreads** | 290 bps | >350 bps = stress | 🟢 Tight (but widening) |
| **BCI Estimate** | **-0.4** | <-0.5 = contraction | 🟡 **Business Slowing** |

### Narrative Synthesis

Business activity is in **late-cycle bifurcation**—small vs large, manufacturing vs services, old economy vs new economy.

**The Collapse:**
- **Small business sentiment at 12-year low** (NFIB 89.4)—rate-sensitive, credit-constrained, cutting back
- **Manufacturing in 26-month recession** (ISM 49.3)—longest since 2008-09
- **Capex orders contracting** (-2.8% YoY)—CEOs cutting future investment
- **Inventories elevated** (I/S 1.41)—liquidation risk building

**The (Temporary) Strength:**
- **Large cap earnings positive** (+4% YoY)—big tech, AI holding up
- **Services still expanding** (ISM 54.1)—80% of economy, but divergence closing
- **HY spreads still tight** (290 bps)—credit markets not pricing recession

**The Bifurcation:**
- **Small business dying, large cap surviving**—NFIB 89 vs S&P earnings +4%
- **Manufacturing collapsing, services holding**—ISM 49 vs 54
- **Old economy weak, new economy (AI/tech) strong**—equipment -1.2% vs IP +3.5%

**Translation:** The divergences are late-cycle signatures. Manufacturing leads services by 6-9 months. Small business leads large cap by 3-6 months. When the divergences close, it's called a recession.

**Cross-Pillar Confirmation:**
- **Labor Pillar:** LFI +0.93 (fragility)—business weakness will flow to payrolls
- **Consumer Pillar:** CCI -0.3 (fatigued)—business income cuts will hit consumer
- **Growth Pillar:** GCI -0.4 (contraction risk)—capex drag on GDP

**MRI (Macro Risk Index):** Business contributes **-0.4 (BCI)** to composite. The business slowdown is the **transmission mechanism**—it's how labor fragility becomes consumer weakness becomes GDP contraction.

---

## Invalidation Criteria

### Bull Case (Business Reacceleration) Invalidation Thresholds

If the following occur **simultaneously for 3+ months**, the bearish business thesis is invalidated:

✅ **NFIB Optimism** exceeds **95** (recovery)
✅ **Core Capex Orders YoY%** turns **positive** (+3%+)
✅ **ISM Manufacturing** exceeds **52** (expansion)
✅ **ISM New Orders - Inventories** exceeds **+5** (demand > supply)
✅ **SLOOS Net Tightening** falls below **+10%** (credit easing)
✅ **BCI** exceeds **+0.3** (expansion regime)

**Action if Invalidated:** Rotate to **industrials** (XLI), **small caps** (IWM), **materials** (XLB). Business expansion = cyclical outperformance.

---

### Bear Case (Business Collapse) Confirmation Thresholds

If the following occur, business is **deteriorating beyond slowing into crisis**:

🔴 **NFIB Optimism** drops below **85** (depression sentiment)
🔴 **ISM Manufacturing** drops below **45** (deep contraction)
🔴 **ISM Services** drops below **50** (services recession)
🔴 **S&P 500 Earnings YoY%** turns **negative** (earnings recession)
🔴 **HY Spreads** exceed **450 bps** (credit stress)
🔴 **BCI** drops below **-1.0** (crisis regime)

**Action if Confirmed:** Maximum defensive. Avoid **all cyclical exposure** (industrials, materials, small caps). Overweight **quality** (QUAL), **low vol** (SPLV), **cash** (SGOV).

---

## Conclusion: Business as the Transmission Mechanism

Business activity isn't just corporate earnings—it's the **transmission mechanism** that connects labor markets to consumer spending to GDP growth.

When CEOs cut capex, they're telling you demand will be weak. When small business collapses while large cap holds, it's late-cycle bifurcation. When manufacturing contracts for 26 months while services expand, the divergence is about to close.

**Current State:**
- **BCI -0.4** (Slowing Regime)
- **NFIB 89.4** (12-year low, small business collapsing)
- **Core capex -2.8% YoY** (CEOs cutting investment)
- **ISM Manufacturing 49.3** (26-month contraction)
- **ISM Services 54.1** (still expanding, but divergence)
- **I/S ratio 1.41** (elevated, liquidation risk)
- **Margins compressing** (11.2% vs 12.8% peak)

**The Bifurcation:**
| Segment | Status | Signal |
|---------|--------|--------|
| Small business | Collapsing | NFIB 89, credit squeeze |
| Large cap | Holding | S&P earnings +4% |
| Manufacturing | Recession | ISM 49, 26 months |
| Services | Expanding | ISM 54, but slowing |
| Old economy | Weak | Equipment -1.2% |
| New economy | Strong | IP/software +3.5% |

**The Transmission:** Business weakness → Capex cuts → Production cuts → Layoffs → Consumer income decline → Spending contraction → GDP falls. We're in the early stages of this transmission. The divergences are late-cycle. They close in recessions.

**That's our view from the Watch. Until next time, we'll be sure to keep the light on....**

*Bob Sheehan, CFA, CMT*
*Founder & CIO, Lighthouse Macro*
*January 15, 2026*
