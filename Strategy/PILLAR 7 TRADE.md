# PILLAR 7: TRADE

## The Trade Transmission Chain

Trade isn't imports and exports. It's the **global margin of adjustment**. The transmission mechanism operates through cascading price and flow dynamics:

```
Dollar Strength → Import Prices → Domestic Inflation →
Export Competitiveness → Manufacturing Output →
Trade Balance → Capital Flows → Dollar Strength (Reinforcing Loop)
```

**The Insight:** Trade is the **pressure release valve** for domestic imbalances. When the U.S. runs a $1T trade deficit, it's exporting demand and importing disinflation. When tariffs disrupt that flow, the adjustment happens somewhere else: prices, margins, or supply chains.

The beauty of trade data: it exposes what domestic data can't. **Relative competitiveness, global demand, and the dollar's purchasing power.** When container volumes collapse before retail sales do, trade data caught it first. When input costs spike before CPI does, import prices told you.

---

## Why Trade Matters: The Global Transmission Belt

Trade is ~25% of U.S. GDP (exports + imports), but its **impact is 2-3x larger** through:
- **Price transmission:** Import prices flow into PPI, then CPI (3-6 month lag)
- **Manufacturing linkage:** 70% of U.S. manufacturing output is globally integrated
- **Dollar hegemony:** Trade deficit = capital account surplus = Treasury demand
- **Margin pressure:** Input costs determine corporate profitability
- **Capital account mirror:** Every dollar of trade deficit is matched by foreign capital inflow

**The Cascade:**

**1. Trade → Prices:** Import costs drive goods inflation (2-4 month lag)
**2. Trade → Manufacturing:** Export demand determines factory output (coincident)
**3. Trade → Dollar:** Trade flows influence currency valuation (6-12 month lag)
**4. Trade → Corporate Margins:** Input costs squeeze profits (1-2 quarter lag)
**5. Trade → Fed Policy:** Imported inflation complicates monetary stance
**6. Trade → Capital Flows:** Deficit financing determines foreign Treasury demand

Get the trade call right, and you've triangulated the inflation pipeline, manufacturing outlook, dollar trajectory, and Treasury demand. Miss it, and you're treating the U.S. economy as a closed system, which it hasn't been since 1971.

**Current State:** Trade exhibiting **tariff-induced distortion**. Import prices spiking (+3.8% YoY) as tariff pass-through intensifies. Export volumes contracting (-2.1% YoY) as retaliatory measures bite. Trade deficit narrowing but for the wrong reason: demand destruction, not competitiveness gains. The 2026 tariff regime is rewiring global supply chains in real time.

---

## Primary Indicators: The Complete Architecture

### A. TRADE BALANCE (The Flow Signal)

The trade balance measures the net exchange of goods and services. Deficits aren't inherently bad, they reflect demand strength, but persistent deficits funded by debt create fragility. The goods deficit (~$100B/mo) is partially offset by a services surplus (~$22B/mo). The composition matters as much as the level.

| **Indicator** | **FRED Code** | **Frequency** | **Lead/Lag** | **Interpretation** |
|---|---|---|---|---|
| **Trade Balance (Goods & Services)** | BOPGSTB | Monthly | Coincident | Net trade position, headline figure |
| **Trade Balance (Goods Only)** | BOPGTB | Monthly | Coincident | Merchandise trade (larger deficit) |
| **Trade Balance (Services Only)** | BOPSTB | Monthly | Coincident | Services trade (consistent surplus ~$22B) |
| **Exports (Goods & Services, BOP)** | BOPTEXP | Monthly | Coincident | Total U.S. exports, BOP basis |
| **Imports (Goods & Services, BOP)** | BOPTIMP | Monthly | Coincident | Total U.S. imports, BOP basis |
| **Real Exports (Goods & Services)** | EXPGSC1 | Quarterly | Coincident | Volume-based exports (chained 2017$) |
| **Real Imports (Goods & Services)** | IMPGSC1 | Quarterly | Coincident | Volume-based imports (chained 2017$) |
| **Net Exports (GDP Component)** | NETEXP | Quarterly | Lagging | Trade contribution to GDP |
| **Real Net Exports** | NETEXC | Quarterly | Lagging | Real trade contribution to GDP |
| **Nominal Exports (NIPA)** | EXPGS | Quarterly | Coincident | BEA national accounts basis |
| **Nominal Imports (NIPA)** | IMPGS | Quarterly | Coincident | BEA national accounts basis |
| **Trade Employment** | USTRADE | Monthly | Lagging | All employees, retail trade sector |

#### Derived Balance Metrics

| **Metric** | **Formula** | **Threshold** | **Signal** |
|---|---|---|---|
| **Trade Balance / GDP** | Balance / GDP x 100 | >-4% | Sustainable deficit range |
| **Export Growth YoY%** | Current - Year Ago | <0% | Export weakness |
| **Import Growth YoY%** | Current - Year Ago | <0% | Demand destruction (or tariff effect) |
| **Goods-Services Split** | Services Surplus / Total Deficit | >25% | Services partially offset goods |
| **Export Concentration** | Top 5 Partners / Total Exports | >50% | Diversification risk |

#### Regime Thresholds: Trade Balance

| **Indicator** | **Crisis** | **Stressed** | **Normal** | **Strong** |
|---|---|---|---|---|
| **Trade Balance (Monthly, $B)** | >-$100B | -$100B to -$70B | -$70B to -$50B | >-$50B |
| **Export Growth YoY%** | <-5% | -5% to 0% | 0% to +5% | >+5% |
| **Import Growth YoY%** | <-5% or >+10% | -5% to +0% | 0% to +5% | +5% to +10% |
| **Trade Balance / GDP** | >-5% | -5% to -3.5% | -3.5% to -2.5% | <-2.5% |

**The Deficit Paradox:** Trade deficit at **-$78B** (Nov 2025), narrowing from -$95B peak (March 2025). But the narrowing is **demand destruction, not competitiveness**. Imports falling faster than exports. Tariffs suppressing inbound goods. This is the wrong kind of improvement. It signals domestic weakness, not manufacturing renaissance.

---

### B. IMPORT/EXPORT PRICES (The Inflation Pipeline)

Import and export prices are the **leading edge of inflation transmission**. Import prices today are CPI goods inflation in 3-6 months. This is the pipeline where tariffs, dollar moves, and commodity prices convert into domestic purchasing power changes. The BLS releases these monthly, ~14 days after month-end, making them among the earliest inflation signals available.

| **Indicator** | **FRED Code** | **Frequency** | **Lead/Lag** | **Interpretation** |
|---|---|---|---|---|
| **Import Price Index (All)** | IR | Monthly | **Leads CPI goods 3-6 mo** | Total import prices |
| **Import Prices ex-Petroleum** | IRFPPF | Monthly | Leads core goods 3-4 mo | Core import prices (strips oil noise) |
| **Import Prices: Industrial Supplies** | IRFPIF | Monthly | Leads PPI 2-3 mo | Commodity input costs |
| **Import Prices: Consumer Goods** | IRFPCF | Monthly | **Leads retail prices 2-4 mo** | Final goods prices |
| **Import Prices: Capital Goods** | IRFPKF | Monthly | Coincident | Equipment/machinery costs |
| **Export Price Index** | IQ | Monthly | Coincident | U.S. competitiveness proxy |
| **Export Prices: Agricultural** | EAFPAG | Monthly | Coincident | Farm export prices (weather, demand) |
| **Export Prices: Nonagricultural** | EAFPNA | Monthly | Coincident | Manufactured export prices |
| **Imports from China** | IMPCH | Monthly | Coincident | China-specific import prices/volumes |
| **Exports to China** | EXPCH | Monthly | Coincident | China-specific export demand |

#### Derived Price Metrics

| **Metric** | **Formula** | **Threshold** | **Signal** |
|---|---|---|---|
| **Import Price YoY%** | Current - Year Ago | >+5% | Imported inflation pressure |
| **Import ex-Petro YoY%** | Current - Year Ago | >+3% | Core import inflation |
| **Terms of Trade Change** | Export Price YoY - Import Price YoY | <-2 ppts | Competitiveness deteriorating |
| **Tariff Pass-Through** | Import Price Change / Tariff Rate Change | >0.6 | High pass-through to consumers |
| **Import-CPI Goods Spread** | Import Price YoY - CPI Goods YoY | >+3 ppts | Pipeline pressure building |

#### Regime Thresholds: Trade Prices

| **Indicator** | **Deflationary** | **Stable** | **Inflationary** | **Crisis** |
|---|---|---|---|---|
| **Import Price YoY%** | <-3% | -3% to +3% | **+3% to +8%** | >+8% |
| **Import ex-Petro YoY%** | <-2% | -2% to +2% | **+2% to +5%** | >+5% |
| **Export Price YoY%** | <-3% | -3% to +3% | +3% to +6% | >+6% |
| **Terms of Trade YoY%** | <-3% | -3% to +3% | +3% to +6% | >+6% |

**The Tariff Transmission:** Import prices at **+3.8% YoY** (Dec 2025), highest since 2022. Ex-petroleum at **+2.9%**. This isn't oil. This is **tariff pass-through**. The 25% tariffs on Chinese goods are flowing into consumer prices with a 3-6 month lag. We're seeing the inflationary impact of trade policy in real time.

---

### C. DOLLAR DYNAMICS (The Relative Price of Everything)

The dollar is the **meta-variable** of trade. Strong dollar = cheap imports, expensive exports. Weak dollar = inflation imported, exports competitive. The Fed's trade-weighted dollar indices are superior to the DXY for trade analysis because they weight by actual trade flows rather than arbitrary currency baskets. The BIS real effective exchange rate adjusts for inflation differentials, making it the gold standard for competitiveness analysis.

| **Indicator** | **FRED Code** | **Frequency** | **Lead/Lag** | **Interpretation** |
|---|---|---|---|---|
| **Broad Dollar Index (Goods & Services)** | DTWEXBGS | Daily | **Leads trade prices 3-6 mo** | USD vs all trading partners (Fed index) |
| **Advanced Foreign Economies Dollar Index** | DTWEXAFEGS | Daily | Leads DM trade 3-6 mo | USD vs developed markets (EU, Japan, UK, etc.) |
| **Emerging Market Economies Dollar Index** | DTWEXEMEGS | Daily | Leads EM trade 3-6 mo | USD vs EM currencies (China, Mexico, Korea, etc.) |
| **Real Broad Trade-Weighted Dollar** | RTWEXBGS | Monthly | Coincident | Inflation-adjusted competitiveness (Fed) |
| **BIS Real Effective Exchange Rate (US)** | RBUSBIS | Monthly | Coincident | BIS-calculated real competitiveness |
| **BIS Nominal Effective Exchange Rate (US)** | NBUSBIS | Monthly | Coincident | BIS nominal dollar strength |
| **BIS Real Narrow Dollar Index (US)** | RNUSBIS | Monthly | Coincident | BIS narrow (27 economies) real index |
| **EUR/USD** | DEXUSEU | Daily | Coincident | USD vs Euro (largest trade partner) |
| **USD/CNY** | DEXCHUS | Daily | Coincident | USD vs Yuan (key bilateral, managed float) |
| **USD/JPY** | DEXJPUS | Daily | Coincident | USD vs Yen (carry trade signal) |
| **USD/CAD** | DEXCAUS | Daily | Coincident | USD vs Canadian Dollar (USMCA) |

#### Derived Dollar Metrics

| **Metric** | **Formula** | **Threshold** | **Signal** |
|---|---|---|---|
| **Broad Dollar YoY%** | DTWEXBGS Current - Year Ago | >+10% | Dollar strength crushing trade |
| **Real TWI YoY%** | RTWEXBGS Current - Year Ago | >+8% | Competitiveness deteriorating |
| **DM-EM Dollar Spread** | DTWEXAFEGS YoY - DTWEXEMEGS YoY | >+5 ppts | EM under disproportionate stress |
| **Dollar-Rate Spread** | Broad Dollar YoY - Fed Funds Change | >+5 ppts | Dollar strength beyond rate differential |
| **Yuan Deviation** | USD/CNY vs 50d MA | >3% | Currency tensions escalating |
| **BIS REER Deviation from Mean** | RBUSBIS vs 10Y avg | >+10% | Dollar overvalued on competitiveness basis |

#### Regime Thresholds: Dollar

| **Indicator** | **USD Weak** | **USD Neutral** | **USD Strong** | **USD Crisis** |
|---|---|---|---|---|
| **Broad Dollar Level (Index)** | <105 | 105-120 | **120-135** | >135 |
| **Broad Dollar YoY%** | <-5% | -5% to +5% | **+5% to +12%** | >+12% |
| **Real TWI YoY%** | <-3% | -3% to +5% | **+5% to +10%** | >+10% |
| **USD/CNY** | <7.0 | 7.0-7.3 | **7.3-7.5** | >7.5 |
| **BIS REER vs 10Y Avg** | <-5% | -5% to +5% | **+5% to +10%** | >+10% |

**The Strong Dollar Trap:** Broad dollar index at **108.5** (Jan 2026), near 20-year highs. Real trade-weighted at **+7.8% YoY**. This **crushes export competitiveness** and **pressures EM debtors** (dollar-denominated debt). But it also **imports disinflation**: strong dollar = cheap imports. The Fed's rate differential vs ECB/BoJ keeps the dollar elevated. The BIS REER confirms: the dollar is ~12% above its 10-year average in real terms. This is unsustainable long-term but can persist for years when driven by rate differentials.

---

### D. BILATERAL TRADE (The Geopolitical Signal)

Not all trade partners are equal. The U.S.-China relationship, nearshoring to Mexico, and European dynamics tell different stories. Bilateral data exposes the real-world impact of tariffs, supply chain rerouting, and geopolitical alignment. FRED provides monthly bilateral goods data for China and Japan. Census Bureau provides comprehensive bilateral data for all partners via their International Trade API.

| **Indicator** | **FRED Code** | **Frequency** | **Lead/Lag** | **Interpretation** |
|---|---|---|---|---|
| **U.S. Exports to China** | EXPCH | Monthly | Coincident | China export demand (retaliatory target) |
| **U.S. Imports from China** | IMPCH | Monthly | Coincident | China import dependence (tariff impact) |
| **U.S. Exports to Japan** | EXPJP | Monthly | Coincident | Japan trade relationship |
| **U.S. Imports from Japan** | IMPJP | Monthly | Coincident | Japan supply chain (autos, semiconductors) |
| **China Bilateral Balance** | Derived: IMPCH - EXPCH | Monthly | Coincident | U.S.-China trade gap |
| **Census Bilateral (All Partners)** | Census API | Monthly | Coincident | Full bilateral matrix |

#### Bilateral Trade Matrix (Current)

| **Bilateral** | **Trade Balance** | **YoY Change** | **Trend** | **Signal** |
|---|---|---|---|---|
| **China** | -$24.5B/mo (Nov 2025) | -18% | Narrowing | Tariff impact + decoupling |
| **Mexico** | -$12.8B/mo | +8% | Widening | Nearshoring beneficiary |
| **Canada** | -$6.2B/mo | +2% | Stable | USMCA normalization |
| **EU** | -$18.4B/mo | +5% | Widening | Dollar strength + demand |
| **Vietnam** | -$9.1B/mo | +32% | Widening rapidly | China-substitute |
| **Japan** | -$6.8B/mo | -5% | Narrowing | Yen weakness offsetting |

#### Derived Bilateral Metrics

| **Metric** | **Formula** | **Threshold** | **Signal** |
|---|---|---|---|
| **China Share of Deficit** | China Deficit / Total Deficit | <20% | Decoupling accelerating |
| **China Import Share** | China Imports / Total Imports | <14% | Structural diversification |
| **Mexico + Vietnam Share** | Combined / Total Imports | >18% | Nearshoring success |
| **Ally vs Adversary Trade Ratio** | (EU+Japan+UK) / (China+Russia) | >3.0 | Friendshoring strengthening |
| **USMCA Concentration** | (Mexico+Canada) / Total Trade | >35% | North American integration |

#### Regime Thresholds: Bilateral

| **Indicator** | **Decoupled** | **Diversifying** | **Dependent** | **Concentrated** |
|---|---|---|---|---|
| **China Import Share** | <10% | **10-14%** | 14-18% | >18% |
| **Top 5 Partner Concentration** | <40% | 40-50% | 50-60% | >60% |
| **USMCA Share of Total Trade** | <25% | 25-35% | **35-45%** | >45% |
| **Vietnam YoY Import Growth** | <5% | 5-15% | **15-30%** | >30% |

**The Decoupling Reality:** China's share of U.S. goods imports has fallen from **21.6%** (2017) to **12.8%** (Dec 2025). But the deficit hasn't disappeared. It's **shifted to Mexico (+$8.4B YoY), Vietnam (+$6.2B YoY), and India (+$2.1B YoY)**. We're not reducing dependence on imports. We're diversifying supply chains. That's resilience, not autarky.

---

### E. CURRENT ACCOUNT & CAPITAL FLOWS (The Financial Mirror)

Every trade deficit has a capital account surplus mirror. When the U.S. imports more than it exports, foreigners accumulate dollar assets. This is the **financial plumbing of trade**: Treasury International Capital (TIC) flows show who is buying U.S. assets, BEA current account data shows the comprehensive external position (trade + income + transfers), and capital flow data reveals whether foreigners are financing the deficit willingly or reluctantly.

| **Indicator** | **FRED Code** | **Frequency** | **Lead/Lag** | **Interpretation** |
|---|---|---|---|---|
| **Current Account Balance** | IEABC | Quarterly | Lagging | Comprehensive external balance (trade + income + transfers) |
| **Current Account: Goods** | IEABCG | Quarterly | Lagging | Goods component (mirrors BOPGTB, quarterly) |
| **Current Account: Services** | IEABCS | Quarterly | Lagging | Services surplus (tech, finance, IP) |
| **Current Account: Primary Income** | IEABCPI | Quarterly | Lagging | Investment income (dividends, interest on foreign assets) |
| **Current Account: Secondary Income** | IEABCSI | Quarterly | Lagging | Transfers (remittances, foreign aid) |
| **TIC Net Long-Term Flows** | Treasury.gov | Monthly | **Leads Treasury demand 1-3 mo** | Foreign buying of U.S. long-term securities |
| **Foreign Holdings of Treasuries** | FDHBFIN | Monthly | Lagging | Total foreign Treasury holdings |
| **Current Account / GDP** | Derived: IEABC / GDP | Quarterly | Lagging | Structural external position |

#### Derived Capital Flow Metrics

| **Metric** | **Formula** | **Threshold** | **Signal** |
|---|---|---|---|
| **Current Account / GDP** | IEABC / GDP x 100 | >-4% | Sustainable deficit range |
| **Primary Income Balance** | IEABCPI level | <$0 | U.S. earning less on foreign assets than paying |
| **TIC Net Flows (3M Avg)** | Rolling 3M avg of net long-term flows | <$0 | Foreign selling of U.S. assets |
| **Foreign Official vs Private Flows** | Official / Total TIC | >50% | Central bank driven (political) |
| **Services Surplus Trend** | 4Q avg YoY change | <0% | U.S. competitive edge eroding |

#### Regime Thresholds: Capital Flows

| **Indicator** | **Crisis** | **Stressed** | **Sustainable** | **Strong** |
|---|---|---|---|---|
| **Current Account / GDP** | >-6% | -6% to -4% | **-4% to -2%** | >-2% |
| **TIC Net Long-Term Flows (Monthly)** | <-$50B | -$50B to $0 | **$0 to +$50B** | >+$50B |
| **Primary Income Balance (Quarterly)** | <-$20B | -$20B to $0 | **$0 to +$30B** | >+$30B |
| **Services Surplus (Quarterly)** | <$15B | $15B to $20B | **$20B to $30B** | >$30B |

**The Financing Question:** The U.S. current account deficit is ~**-3.5% of GDP** (Q3 2025). Historically sustainable, but the composition matters. **Primary income remains positive** (~$60B/quarter), meaning the U.S. earns more on its foreign investments than foreigners earn on their U.S. holdings. This is the "dark matter" of international finance: U.S. assets are higher-returning despite the deficit. The risk is when TIC flows turn negative, meaning foreigners are **selling** U.S. assets rather than buying. Watch Japan and China's Treasury holdings: both have been slowly reducing, offset by European and Middle Eastern buying.

---

### F. SUPPLY CHAIN INDICATORS (The Flow Disruption Signal)

Supply chains are the **circulatory system** of global trade. When they clog, prices spike and production stalls. The NY Fed's Global Supply Chain Pressure Index (GSCPI) synthesizes 27 variables across shipping costs, delivery times, and backlogs into a single z-score. Port of LA/Long Beach container data provides real-time U.S. import volume signals. Freight indices (Baltic Dry, Harpex) lead import prices by 2-3 months.

| **Indicator** | **Source** | **Frequency** | **Lead/Lag** | **Interpretation** |
|---|---|---|---|---|
| **NY Fed GSCPI** | NY Fed (Excel) | Monthly | **Leads IP 2-4 mo** | Global Supply Chain Pressure Index (z-score) |
| **Container Throughput (LA/LB Ports)** | Port of LA (Socrata API) | Monthly | **Leads retail 2-3 mo** | U.S. import volume proxy (~40% of containers) |
| **Baltic Dry Index** | Baltic Exchange | Daily | **Leads global trade 2-4 mo** | Bulk shipping demand (raw materials) |
| **Harpex Container Index** | Harper Petersen | Weekly | Leads container rates 1-2 mo | Container shipping rates |
| **ISM Supplier Delivery Times** | ISM | Monthly | Leads IP 1-2 mo | Manufacturing bottlenecks (>50 = slowing) |
| **ISM Backlogs of Orders** | ISM | Monthly | Leads production 1-2 mo | Order pipeline pressure |
| **Rail Intermodal Volume** | RAILFRTINTERMODALD11 | Monthly | Coincident | Container-on-rail (domestic distribution) |
| **Cass Freight Shipments Index** | FRGSHPUSM649NCIS | Monthly | Coincident | Domestic freight shipment volumes |
| **Transportation Services Index** | TSIFRGHT | Monthly | Coincident | BTS freight index |

#### Derived Supply Chain Metrics

| **Metric** | **Formula** | **Threshold** | **Signal** |
|---|---|---|---|
| **GSCPI Level** | NY Fed Index (z-score) | >+1.5 | Supply stress |
| **GSCPI Momentum** | Current - 3M Avg | >+0.5 | Deterioration accelerating |
| **Container Volume YoY%** | LA/LB TEU Current - Year Ago | <-5% | Trade contraction |
| **Delivery Time Gap** | ISM Deliveries - 50 (neutral) | >+5 | Bottlenecks building |
| **Freight-GDP Divergence** | Freight Vol YoY - GDP YoY | <-3 ppts | Goods recession |

#### Regime Thresholds: Supply Chains

| **Indicator** | **Loose** | **Normal** | **Tight** | **Crisis** |
|---|---|---|---|---|
| **NY Fed GSCPI** | <-1.0 | -1.0 to +1.0 | **+1.0 to +2.5** | >+2.5 |
| **ISM Supplier Deliveries** | <48 | 48-55 | **55-65** | >65 |
| **Container Volume YoY%** | >+10% | -2% to +10% | **-10% to -2%** | <-10% |
| **Baltic Dry Index** | >2000 | 1200-2000 | **800-1200** | <800 |
| **Cass Freight YoY%** | >+5% | -2% to +5% | **-8% to -2%** | <-8% |

**The Supply Chain Reset:** NY Fed GSCPI at **+0.8** (Dec 2025), elevated but not crisis. Supplier deliveries at **52.4** (normalizing). Container rates at **$3,850/FEU** (up from $1,500 lows but below $20k peak). The **supply chain crisis is over**. But tariff-induced rerouting (Vietnam, Mexico, India instead of China) creates **new inefficiencies**. We're trading capacity constraints for logistics complexity.

---

### G. TARIFFS & TRADE POLICY (The 2026 Regime Shift)

Tariffs are no longer cyclical noise. They're **structural reshaping** of global trade. The 2025-2026 tariff escalation changed the game. The Trade Policy Uncertainty Index (EPUTRADE on FRED) captures newspaper coverage of trade policy uncertainty and leads capex decisions by 3-6 months. The effective tariff rate (tariff revenue / import value) provides a single number for the aggregate tariff burden.

| **Indicator** | **Source** | **Frequency** | **Lead/Lag** | **Interpretation** |
|---|---|---|---|---|
| **Trade Policy Uncertainty Index** | FRED (EPUTRADE) | Monthly | **Leads capex 3-6 mo** | Newspaper-based uncertainty gauge |
| **Average Tariff Rate (Imports)** | USITC | Annual + Ad Hoc | Structural | Weighted-average tariff on all imports |
| **Tariff Revenue** | Treasury Monthly Statement | Monthly | Coincident | Customs duties collected |
| **China Section 301 Tariff Rate** | USTR | Structural | Lagging | China-specific tariff rate |
| **Retaliatory Tariff Tracker** | WTO | Ad hoc | Lagging | Foreign tariffs on U.S. exports |
| **Iacoviello TPU Index** | Fed Board | Monthly | Leads capex 3-6 mo | Fed staff trade uncertainty measure |
| **World Trade Uncertainty Index** | WorldUncertaintyIndex.com | Quarterly | Structural | Global trade uncertainty (143 countries) |

#### Derived Tariff Metrics

| **Metric** | **Formula** | **Threshold** | **Signal** |
|---|---|---|---|
| **Effective Tariff Rate** | Tariff Revenue / Import Value | >4% | Elevated protection |
| **China Import Share** | China Imports / Total Imports | <14% | Decoupling accelerating |
| **Tariff-Inflation Correlation** | Tariff YoY vs CPI Goods YoY (6M lag) | >+0.5 | High pass-through |
| **Trade Policy Uncertainty** | EPUTRADE Index Level | >200 | Elevated uncertainty |
| **Tariff Escalation Rate** | Avg Tariff Current - Avg Tariff 1Y Ago | >+2 ppts | Active escalation |

#### Regime Thresholds: Tariffs

| **Indicator** | **Free Trade** | **Moderate** | **Protectionist** | **Trade War** |
|---|---|---|---|---|
| **Average Tariff Rate** | <2.5% | 2.5-4.0% | **4.0-8.0%** | >8.0% |
| **China Import Share** | >18% | 14-18% | **10-14%** | <10% |
| **Trade Policy Uncertainty (EPUTRADE)** | <100 | 100-150 | **150-250** | >250 |
| **Tariff Revenue (Monthly, $B)** | <$5B | $5-8B | **$8-12B** | >$12B |
| **Effective Tariff Rate** | <2% | 2-4% | **4-6%** | >6% |

**The Tariff Regime:** Average effective tariff rate at **6.2%** (Dec 2025), highest since 1930s Smoot-Hawley. China import share has fallen from 22% (2017) to **12.8%** (Dec 2025): decoupling is real. EPUTRADE at **187**, elevated but below 2019 peaks. We're not in a trade war. We're in a **new normal** of managed trade.

---

### H. INVENTORIES & WHOLESALE (The Absorption Signal)

Inventories sit at the intersection of trade and domestic demand. When imports surge ahead of demand, inventories build. When supply chains break, inventories deplete. The inventory-to-sales ratio is the barometer: rising I/S signals either weakening demand or over-ordering, falling I/S signals either strong demand or supply constraints. Wholesale inventories are particularly trade-sensitive because wholesalers are the first domestic link in the import chain.

| **Indicator** | **FRED Code** | **Frequency** | **Lead/Lag** | **Interpretation** |
|---|---|---|---|---|
| **Total Business I/S Ratio** | ISRATIO | Monthly | **Leads GDP 1-2 qtrs** | Broadest inventory signal |
| **Retail I/S Ratio** | RETAILIRSA | Monthly | Leads retail sales 1-2 mo | Retail stock levels |
| **Wholesale I/S Ratio** | WHLSLRIRSA | Monthly | Leads wholesale orders 1-2 mo | Wholesale absorption (trade-sensitive) |
| **Manufacturers I/S Ratio** | MNFCTRIRSA | Monthly | Coincident | Factory stock levels |
| **Retail Inventories** | RETAILIMSA | Monthly | Coincident | Nominal inventory levels |
| **Total Business Inventories** | BUSINV | Monthly | Coincident | Nominal business inventories |
| **Real Manufacturing & Trade Sales** | CMRMTSPL | Monthly | Coincident | Real sales (denominator for I/S) |
| **E-Commerce Share of Retail** | ECOMPCTSA | Quarterly | Structural | Structural shift in goods distribution |
| **E-Commerce Sales** | ECOMSA | Quarterly | Coincident | Online goods purchases |

#### Derived Inventory Metrics

| **Metric** | **Formula** | **Threshold** | **Signal** |
|---|---|---|---|
| **Total I/S vs 5Y Average** | ISRATIO - 5Y Mean | >+0.05 | Inventory bloat |
| **Wholesale I/S Trend** | 3M MA Slope | >0 | Wholesale absorption weakening |
| **Retail I/S vs Pre-COVID** | RETAILIRSA - Feb 2020 level | >+0.10 | Overstock vs normalized demand |
| **Manufacturer I/S Momentum** | Current - 6M Avg | >+0.03 | Factory destocking signal |
| **Import-Inventory Divergence** | Import Growth YoY - Inventory Growth YoY | >+5 ppts | Imports outpacing absorption |

#### Regime Thresholds: Inventories

| **Indicator** | **Lean** | **Normal** | **Heavy** | **Bloated** |
|---|---|---|---|---|
| **Total Business I/S Ratio** | <1.25 | 1.25-1.40 | **1.40-1.50** | >1.50 |
| **Retail I/S Ratio** | <1.20 | 1.20-1.40 | **1.40-1.55** | >1.55 |
| **Wholesale I/S Ratio** | <1.20 | 1.20-1.35 | **1.35-1.45** | >1.45 |
| **Manufacturers I/S Ratio** | <1.30 | 1.30-1.45 | **1.45-1.55** | >1.55 |

**The Inventory Cycle:** Total business I/S at **1.37** (Nov 2025), in normal range. Wholesale I/S at **1.33**, also normal. But the composition tells a story: **import-sensitive wholesale inventories** are rising while **retail inventories** remain tight. This suggests a front-loading effect, importers stocking ahead of tariff escalation, that will reverse in Q1-Q2 2026. When it does, import volumes will drop sharply, temporarily narrowing the trade deficit for the wrong reason.

---

## Trade Pillar Composite Index (TCI)

### Formula

The Trade Pillar Composite synthesizes trade flows, prices, volumes, policy, and currency into a single trade health indicator:

```
TCI = 0.20 x z(-Import_Price_YoY)                    # Inverted (high = inflationary headwind)
    + 0.20 x z(-Trade_Balance_GDP_Ratio)             # Inverted (larger deficit = weaker)
    + 0.15 x z(Export_Volume_YoY)                    # Positive = stronger exports
    + 0.15 x z(-NY_Fed_GSCPI)                        # Inverted (high = supply stress)
    + 0.10 x z(Container_Volume_YoY)                 # Port throughput proxy
    + 0.10 x z(-DXY_YoY)                             # Inverted (strong dollar = trade headwind)
    + 0.10 x z(-Trade_Policy_Uncertainty)            # Inverted (high = negative)
```

### Component Weighting Rationale

- **Import Prices (20%):** Primary inflation transmission channel. Tariffs, dollar, and commodity prices all flow through here. Inverted because rising import prices are a trade headwind.
- **Trade Balance/GDP (20%):** Structural trade position normalized to economy size. Inverted because a widening deficit signals growing imbalances.
- **Export Volumes (15%):** Real export activity strips price effects. Captures global demand for U.S. goods and competitiveness.
- **Supply Chain Pressure (15%):** NY Fed GSCPI captures bottlenecks, shipping costs, and delivery disruptions. Inverted because supply stress is a trade headwind.
- **Container Volumes (10%):** Real-time import activity from LA/Long Beach ports. Physical flow proxy.
- **Dollar Strength (10%):** Trade-weighted dollar directly impacts competitiveness and pricing. Inverted because strong dollar hurts trade.
- **Policy Uncertainty (10%):** EPUTRADE captures tariff uncertainty, which delays capex and supply chain decisions. Inverted.

### Interpretation

| **TCI Range** | **Regime** | **Trade Allocation** | **Signal** |
|---|---|---|---|
| > +1.0 | Trade Tailwind | Overweight exporters, EM | Globalization tailwind |
| +0.5 to +1.0 | Favorable | Neutral global exposure | Stable trade conditions |
| -0.5 to +0.5 | Neutral | Balanced | Mixed conditions |
| -1.0 to -0.5 | Headwind | **Underweight trade-sensitive** | Tariff/dollar drag |
| < -1.0 | Trade Crisis | Maximum defensive | De-globalization shock |

### Historical Calibration

| **Period** | **TCI** | **Regime** | **Outcome (12M Forward)** |
|---|---|---|---|
| **Dec 2007** | -0.6 | Headwind | GFC trade collapse, exports -16% |
| **Dec 2011** | +0.2 | Neutral | European crisis, mild trade drag |
| **Dec 2014** | +0.6 | Favorable | Dollar surge begins, oil collapse |
| **Dec 2018** | -0.8 | Headwind | Trade war escalation, ISM <50 |
| **April 2020** | -1.8 | Crisis | COVID supply chain collapse |
| **Dec 2021** | -1.2 | Crisis | Supply chain crisis peak |
| **Dec 2023** | +0.3 | Neutral | Normalization underway |
| **Dec 2025** | **-0.5** | **Headwind** | **Tariff regime, strong dollar** |

**Current Assessment (Dec 2025):** TCI at **-0.5** places trade in "Headwind" regime, not crisis, but **persistent drag**:
- **Import prices at +3.8% YoY** (tariff pass-through)
- **Trade deficit at -3.2% of GDP** (narrowing on demand weakness)
- **Export volumes at -2.1% YoY** (retaliatory tariffs + strong dollar)
- **NY Fed GSCPI at +0.8** (elevated but not crisis)
- **Container volumes at -4.2% YoY** (post-front-loading normalization)
- **DXY at +7.2% YoY** (competitiveness headwind)
- **Trade Policy Uncertainty (EPUTRADE) at 187** (elevated)

Trade is a **structural headwind** in 2026. Not collapsing, but not helping.

---

## Lead/Lag Relationships: The Trade Cascade

```
LEADING                           COINCIDENT                  LAGGING
────────────────────────────────────────────────────────────────────────────────────
│                                 │                          │
│  Baltic Dry Index (2-4 mo)     │  Trade Balance            │  Trade Deficit / GDP (1-2 qtrs)
│  Container Volumes (2-3 mo)    │  Import/Export Levels     │  Corporate Margins (1-2 qtrs)
│  Import Prices (3-6 mo→CPI)    │  Dollar Index             │  Manufacturing Employment (3-6 mo)
│  NY Fed GSCPI (2-4 mo→IP)      │  Tariff Revenue           │  Net Exports GDP (1 qtr)
│  Shipping Rates (2-3 mo)       │  Bilateral Balances       │  Terms of Trade (lagging)
│  EPUTRADE (3-6 mo→capex)       │  Supply Chain Deliveries  │  Reshoring Capex (12+ mo)
│  DXY Changes (3-6 mo→trade)    │  Export Orders            │  Current Account (1 qtr)
│  TIC Flows (1-3 mo→Treasury)   │  Inventory Levels         │  Trade Agreement Effects
│                                │                          │
────────────────────────────────────────────────────────────────────────────────────
```

**The Critical Chain:**

**1. Dollar strengthens** (rate differentials, safe haven) → 3-6 months later → **Export competitiveness deteriorates**
**2. Tariffs imposed** (policy shock) → 2-4 months later → **Import prices rise**
**3. Import prices rise** → 3-6 months later → **PPI/CPI goods inflation**
**4. Container volumes fall** → 2-3 months later → **Retail inventory adjustments**
**5. Export volumes fall** → 3-6 months later → **Manufacturing output contracts**
**6. Trade deficit narrows** → 1-2 quarters later → **Net exports add to GDP** (but for wrong reason if import-driven)
**7. Capital flows shift** → 1-3 months later → **Treasury demand adjusts** (TIC data confirms)

This is the transmission mechanism we're living through. Tariffs imposed Q1 2025 → import price spike Q3 2025 → goods inflation Q4 2025 → margin compression now. We're currently at Steps 3-5: import prices are elevated, export volumes are contracting, and manufacturing IP is weakening.

---

## Integration with Three-Engine Framework

### Pillar 7 → Pillar 1 (Labor)

Trade directly affects **manufacturing employment** and indirectly affects wages through import competition.

```
Exports ↓ → Manufacturing Output ↓ →
Factory Jobs ↓ → Wage Pressure in Goods Sector ↓ →
Services Sector Absorbs Some (lagged) → But Total Hours Worked ↓
```

**Current Linkage:** Export volumes at -2.1% YoY. Manufacturing IP at -0.8% YoY. Manufacturing employment at **-0.4% YoY** (37k jobs lost). Trade weakness is contributing to the goods-sector labor stress captured in LFI.

**Cross-Pillar Signal:** When **TCI < -0.5** (trade headwind) AND **LFI > +0.8** (labor fragile), goods-producing sectors face **double pressure**: weak export demand AND structural fragility. Current: **TCI -0.5, LFI +0.93**. Manufacturing is the weak link. Historical precedent: this combination preceded the 2001 and 2008 manufacturing recessions.

---

### Pillar 7 → Pillar 2 (Prices)

Trade prices are the **pipeline** for goods inflation. Import prices lead CPI goods by 3-6 months with ~70% pass-through for non-petroleum goods.

```
Import Prices ↑ → PPI Intermediate Goods ↑ →
PPI Final Demand ↑ → CPI Goods ↑ (3-6 month lag)
```

**Current Linkage:** Import prices at +3.8% YoY. PPI Final Demand at +2.6% YoY. CPI Goods at -1.2% YoY (still deflationary but **narrowing**). The tariff-driven import price spike is **transmitting** into the domestic price chain. Goods deflation is ending.

**Cross-Pillar Signal:** Import prices (+3.8%) suggest goods CPI deflation (-1.2%) is **temporary**. Watch for goods CPI to flip positive by Q2 2026. This complicates the "last mile" disinflation thesis in PCI. When **Import Price YoY > +3%** AND **CPI Goods YoY is negative**, the pipeline is building pressure that hasn't yet released. We're in that configuration now.

---

### Pillar 7 → Pillar 3 (Growth)

Net exports are a **GDP component** (~-3% contribution):

```
Trade Deficit Widens → Net Exports Drag on GDP
Trade Deficit Narrows → Net Exports Adds to GDP (if export-driven)
Import-Driven Narrowing → Misleading GDP Add (demand weakness)
```

**Current Linkage:** Trade deficit narrowing (-$78B from -$95B peak). But it's **import-driven** (demand destruction), not export-driven (competitiveness). Net exports will **add ~+0.2 ppts** to Q4 2025 GDP, but this is **low-quality growth**: shrinking pie, not expanding trade.

**Cross-Pillar Signal:** When **TCI < -0.5** AND **GCI < -0.3**, trade weakness is **confirming** (not causing) the growth slowdown. Current: **TCI -0.5, GCI -0.4**. Trade and growth are synchronized. The inventory cycle (Section H) adds nuance: front-loaded imports boosted prior GDP, now the payback is starting.

---

### Pillar 7 → Pillar 5 (Consumer)

Trade policy directly affects consumer prices and purchasing power. Tariffs are a consumption tax.

```
Tariffs ↑ → Import Prices ↑ → Retail Prices ↑ →
Real Purchasing Power ↓ → Consumer Spending ↓ (2-4 month lag)
```

**Current Linkage:** Tariff pass-through estimated at ~$1,200/year per household (Peterson Institute). Real disposable income growth at **+1.1% YoY**, partially offset by rising goods prices. Import-dependent categories (electronics, apparel, toys) showing the most price pressure.

**Cross-Pillar Signal:** When **Import Price YoY > +5%** AND **CCI < -0.3**, tariffs are biting the consumer. Current: Import prices at +3.8% (approaching but not yet >+5%), CCI at -0.3. The consumer is absorbing tariff costs so far, but the margin for error is thin.

---

### Pillar 7 → Pillar 9 (Financial/Dollar)

Trade flows affect **capital flows**, which affect **dollar, rates, and Treasury demand**:

```
Trade Deficit → Capital Account Surplus →
Foreign Treasury Buying → Rates Suppressed → Dollar Supported
Trade Deficit Narrows → Less Foreign Inflow → Rates Rise → Dollar Adjusts
```

**Current Linkage:** The trade deficit is **funding** the Treasury market. $1T+ annual deficits require $1T+ foreign capital inflows. As the trade deficit narrows (tariff-driven), foreign capital inflows slow, putting **upward pressure on Treasury yields**. TIC data shows Japan and China slowly reducing Treasury holdings, offset by European and sovereign wealth fund buying.

**Cross-Pillar Signal:** Trade deficit narrowing is **rate-bearish** in the long run. Less trade deficit = less automatic Treasury demand from trade partners. When **Current Account / GDP improves by >1 ppt** AND **TIC Net Flows < $0**, Treasury supply/demand dynamics worsen. This feeds into the Plumbing Pillar's fiscal dominance thesis and the Government Pillar's term premium analysis.

---

## Data Source Summary

| **Category** | **Primary Source** | **Frequency** | **Release Lag** | **Access** |
|---|---|---|---|---|
| **Trade Balance** | Census Bureau / BEA | Monthly | ~35 days | FRED: BOPGSTB, BOPGTB, BOPTEXP, BOPTIMP |
| **Import/Export Prices** | BLS | Monthly | ~14 days | FRED: IR, IQ, IRFPPF, IRFPCF, IRFPKF |
| **Dollar Indices (Fed)** | Federal Reserve | Daily/Monthly | Same day | FRED: DTWEXBGS, DTWEXAFEGS, DTWEXEMEGS |
| **Dollar Indices (BIS)** | BIS | Monthly | ~2 months | FRED: RBUSBIS, NBUSBIS, RNUSBIS |
| **Bilateral Trade** | Census Bureau | Monthly | ~35 days | FRED: EXPCH, IMPCH, EXPJP, IMPJP; Census API for all partners |
| **Current Account** | BEA | Quarterly | ~3 months | FRED: IEABC, IEABCG, IEABCS, IEABCPI |
| **TIC Flows** | Treasury Department | Monthly | ~45 days | Treasury.gov CSV (manual download) |
| **Supply Chain (GSCPI)** | NY Fed | Monthly | ~4 business days | NY Fed Excel download (direct URL) |
| **Container Volumes** | Port of LA | Monthly | ~15 days | Socrata API (data.lacity.org, no auth) |
| **Baltic Dry Index** | Baltic Exchange | Daily | Real-time | Manual CSV (Investing.com / MacroMicro) |
| **Inventories** | Census Bureau | Monthly | ~6 weeks | FRED: ISRATIO, RETAILIRSA, WHLSLRIRSA |
| **Trade Policy Uncertainty** | PolicyUncertainty.com | Monthly | ~30 days | FRED: EPUTRADE; Daily from PolicyUncertainty.com |
| **Tariff Data** | USITC | Annual + Ad Hoc | Varies | USITC DataWeb (dataweb.usitc.gov) |
| **Bilateral (Granular)** | UN Comtrade | Monthly/Annual | ~2 months | API with free registration (comtradeapicall pkg) |
| **Freight/Logistics** | AAR, BTS, Cass | Monthly/Weekly | ~2 weeks | FRED: RAILFRTINTERMODALD11, TSIFRGHT, FRGSHPUSM649NCIS |

**Critical Timing:** Trade balance released ~35 days after month-end. Use import/export prices (14-day lag) and container volumes for earlier signals. NY Fed GSCPI releases 4th business day of each month. Baltic Dry is daily and leads by 2-4 months. EPUTRADE provides monthly trade policy uncertainty on FRED.

**Free Data Sources Beyond FRED:**

| **Source** | **URL** | **Data** | **Format** | **Auth** |
|---|---|---|---|---|
| **NY Fed GSCPI** | newyorkfed.org/research/policy/gscpi | 27-component supply chain index | Excel (.xlsx) | None |
| **Port of LA** | data.lacity.org (Socrata API) | Monthly TEU container volumes | JSON/CSV | None |
| **PolicyUncertainty.com** | policyuncertainty.com/trade_uncertainty.html | Daily U.S. trade policy uncertainty | Excel | None |
| **Iacoviello TPU** | matteoiacoviello.com/tpu.htm | Country-level trade uncertainty | CSV | None |
| **Treasury TIC** | home.treasury.gov/data/treasury-international-capital-tic-system | Monthly foreign holdings + flows | CSV/Excel | None |
| **Census Trade API** | api.census.gov/data/timeseries/intltrade/ | Bilateral trade by commodity | JSON | Free key (500 calls/day without) |
| **UN Comtrade** | comtrade.un.org | Global bilateral trade flows | JSON/CSV | Free registration |
| **BIS EER** | data.bis.org/topics/EER | Effective exchange rates (64 economies) | CSV/SDMX | None |
| **WTO Stats** | stats.wto.org | Global trade, tariffs, NTMs | CSV/JSON | Free registration |
| **World Uncertainty Index** | worlduncertaintyindex.com/data | World/trade uncertainty (quarterly) | Excel | None |

---

## Current State Assessment (January 2026)

| **Indicator** | **Current** | **Threshold** | **Assessment** |
|---|---|---|---|
| **Trade Balance** | -$78B | >-$85B = improving | Narrowing (demand destruction) |
| **Trade Balance / GDP** | -3.2% | >-4% = sustainable | Manageable |
| **Import Price YoY%** | +3.8% | >+3% = inflationary | **Tariff pass-through** |
| **Import ex-Petro YoY%** | +2.9% | >+2% = core inflation | **Core import inflation** |
| **Export Volume YoY%** | -2.1% | <0% = weak | **Retaliatory drag** |
| **Container Volume YoY%** | -4.2% | <-5% = contracting | Weak (post-front-loading) |
| **Broad Dollar YoY%** | +7.2% | >+5% = headwind | **Strong dollar drag** |
| **BIS REER vs 10Y Avg** | +12% | >+10% = overvalued | **Dollar overvalued** |
| **NY Fed GSCPI** | +0.8 | >+1.0 = stress | Elevated |
| **EPUTRADE** | 187 | >150 = elevated | Elevated |
| **China Import Share** | 12.8% | <14% = decoupling | Diversifying |
| **Current Account / GDP** | -3.5% | >-4% = sustainable | Manageable |
| **Effective Tariff Rate** | 6.2% | >4% = protectionist | **Protectionist regime** |
| **TCI Estimate** | **-0.5** | <-0.5 = headwind | **Trade Headwind** |

### Narrative Synthesis

**The Tariff Effect:**
- Average tariff rate at **6.2%** (highest since 1930s Smoot-Hawley)
- Import prices at **+3.8% YoY** (tariff pass-through, not commodity-driven)
- Goods deflation (-1.2% CPI) is **ending**. Watch for goods CPI to flip positive by Q2 2026.
- Consumer impact: ~$1,200/year higher prices per household
- EPUTRADE at **187**, elevated but below 2019 trade war peaks

**The Dollar Effect:**
- Broad dollar at **+7.2% YoY**, BIS REER **+12% above 10Y average**
- Export volumes at **-2.1% YoY**: retaliatory tariffs + strong dollar double hit
- Manufacturing IP at **-0.8% YoY**: trade weakness flowing into production
- EM stress building: dollar-denominated debt service costs rising

**The Decoupling Effect:**
- China import share at **12.8%** (down from 22% in 2017)
- Mexico, Vietnam, India absorbing displaced trade
- Supply chains longer, more complex, less efficient
- Resilience gained, cost efficiency lost

**The Capital Flow Effect:**
- Current account at **-3.5% of GDP**, sustainable range
- Primary income still positive (~$60B/quarter): U.S. outearns foreigners on assets
- Japan and China slowly reducing Treasury holdings
- TIC flows remain positive overall (European and Middle Eastern offsets)

**Translation:** Trade is a **persistent headwind**, not a crisis. Tariffs are inflationary. Strong dollar is contractionary for manufacturing. Decoupling is real but costly. Capital flows are adjusting but not disrupted. The globalization tailwind of 1990-2020 is **gone**. We're in managed trade now.

**Cross-Pillar Confirmation:**
- **Prices Pillar:** Import prices (+3.8%) threatening goods disinflation narrative
- **Growth Pillar:** Export weakness contributing to manufacturing recession
- **Labor Pillar:** Manufacturing jobs down 37k YoY, trade a contributing factor
- **Consumer Pillar:** Tariff pass-through reducing real purchasing power
- **Plumbing Pillar:** Trade deficit narrowing = less automatic Treasury demand

**MRI (Macro Risk Index):** Trade contributes **TCI = -0.5** to the composite via the 0.05 weight. Trade headwinds are **chronic**, not acute. They grind on margins and competitiveness rather than triggering systemic events. The TCI contribution to MRI: 0.05 x (-(-0.5)) = +0.025. Small in isolation but confirming when combined with other engines.

---

## Invalidation Criteria

### Bull Case (Trade Tailwind) Invalidation Thresholds

If the following occur **simultaneously for 3+ months**, the bearish trade thesis is invalidated:

✅ **Import Prices YoY%** drops below **+2%** (tariff absorption, rollback, or dollar reversal)
✅ **Export Volumes YoY%** turns **positive** (+3%+) (global demand revival or dollar weakness)
✅ **Broad Dollar YoY%** drops below **+2%** (dollar weakness restoring competitiveness)
✅ **Container Volumes YoY%** exceeds **+5%** (trade acceleration)
✅ **EPUTRADE** drops below **120** (trade policy clarity)
✅ **TCI** exceeds **+0.3** (neutral/favorable regime)

**Action if Invalidated:** Rotate to **exporters** (industrials: XLI, tech hardware: SOXX), **emerging markets** (EEM, VWO), **global logistics** (shipping, rails). Trade tailwind = global growth revival. Increase exposure to trade-sensitive sectors within equity allocation.

---

### Bear Case (Trade Crisis) Confirmation Thresholds

If the following occur, trade is **deteriorating beyond headwind into crisis**:

🔴 **Import Prices YoY%** exceeds **+8%** (tariff escalation or supply shock)
🔴 **Export Volumes YoY%** drops below **-8%** (trade war intensification)
🔴 **NY Fed GSCPI** exceeds **+2.5** (supply chain crisis)
🔴 **Container Volumes YoY%** drops below **-15%** (trade collapse)
🔴 **Broad Dollar** exceeds **+15% YoY** (dollar crisis crushing EM)
🔴 **EPUTRADE** exceeds **300** (policy chaos)
🔴 **TCI** drops below **-1.0** (crisis regime)

**Action if Confirmed:** Maximum defensive. Avoid **all trade-sensitive sectors** (industrials: XLI, materials: XLB, EM: EEM). Overweight **domestic services** (healthcare: XLV, utilities: XLU), **gold** (GLD), **cash** (SGOV). Trade crisis = global recession risk. Monitor TIC flows for signs of foreign capital flight from U.S. assets.

---

## Conclusion: Trade as the Global Margin

Trade isn't imports and exports. It's the **global margin of adjustment**: the release valve for domestic imbalances, the transmission belt for prices, the competitive arena for manufacturing, and the financial pipeline for capital flows.

**Current State:**
- **TCI -0.5** (Trade Headwind Regime)
- **Import prices +3.8% YoY** (tariff pass-through)
- **Export volumes -2.1% YoY** (competitiveness drag)
- **Trade deficit -$78B/month** (narrowing on demand weakness)
- **Broad dollar +7.2% YoY** (strong dollar headwind)
- **BIS REER +12% above 10Y avg** (dollar overvalued in real terms)
- **GSCPI +0.8** (supply chains elevated but stable)
- **EPUTRADE 187** (trade policy uncertainty elevated)
- **Current account -3.5% of GDP** (sustainable range)
- **Effective tariff rate 6.2%** (highest since 1930s)

**The Structural Shift:**

| Segment | Old Regime (1990-2020) | New Regime (2025+) |
|---|---|---|
| **Tariffs** | ~2% average | ~6%+ and rising |
| **China share** | 15-22% of imports | 12% and falling |
| **Supply chains** | Optimized for cost | Optimized for resilience |
| **Dollar role** | Exorbitant privilege | Weaponized tool |
| **Trade growth** | 2x GDP growth | At or below GDP growth |
| **Policy framework** | WTO multilateral | Bilateral managed trade |

**The Trade Paradox:** The trade deficit is narrowing, usually bullish, but for the **wrong reason**: import demand destruction, not export competitiveness. Meanwhile, import prices are spiking, inflationary at exactly the moment when the Fed hoped for goods deflation. Trade is complicating every other pillar's thesis.

**Cross-Pillar Context:** Trade headwind (**TCI -0.5**) + labor fragility (**LFI +0.93**) + growth weakness (**GCI -0.4**) + elevated inflation (**PCI +0.7**) = **MRI +1.1** (HIGH RISK regime).

The globalization dividend is over. We're not going back to 2019. We're building a new trade architecture: slower, costlier, more resilient, less efficient. The adjustment is priced in over years, not quarters.

**That's our view from the Watch. Until next time, we'll be sure to keep the light on....**

*Bob Sheehan, CFA, CMT*
*Founder & CIO, Lighthouse Macro*
*January 15, 2026*
