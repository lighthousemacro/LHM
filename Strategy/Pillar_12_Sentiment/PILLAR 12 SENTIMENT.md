# PILLAR 12: SENTIMENT & POSITIONING

## The Sentiment Transmission Chain

Sentiment isn't noise. It's the crowd's positioning expressed through surveys, options, and flows. And the crowd is a source of liquidity, not information.

```
Fear → Underexposure → Forced Buying →
Price Rise → Confidence → Overexposure →
Complacency → Forced Selling → Fear (Cycle)
```

**The Insight:** Sentiment is a contrarian indicator at extremes. Extreme fear = buy. Extreme greed = sell. The crowd isn't wrong because they're stupid. They're wrong because they're late. By the time everyone is bullish, they've already bought. By the time everyone is bearish, they've already sold. The marginal buyer/seller is always on the other side of consensus.

The beauty of sentiment data: it tells you who's left. When NAAIM shows managers 100%+ invested, who's left to buy? When AAII shows -30% bull-bear, who's left to sell? The answer determines price.

---

## Why Sentiment Matters

Sentiment is the **contrarian edge** in the 12-pillar framework for a simple reason: it captures positioning asymmetry. Markets move on marginal flows, and sentiment tells you where the marginals are.

**The Contrarian Logic:**

**1. High Fear (Underexposed):** Marginal buyers available → bullish
**2. High Greed (Overexposed):** Only sellers remain → bearish
**3. Neutral:** No contrarian edge → trade fundamentals and structure
**4. Extreme Fear + Weak Structure:** Capitulation setup → maximum buy zone
**5. Extreme Greed + Strong Structure:** Blow-off setup → maximum caution

Get the sentiment call right at extremes, and you've identified where liquidity will come from. Miss it, and you're trading with the crowd instead of against them.

**The Extreme Edge:** Sentiment only matters at extremes. In the middle, it's noise. We don't trade sentiment in isolation. We use sentiment to size and time trades identified by fundamentals and structure.

---

## Primary Indicators: The Complete Architecture

### A. RETAIL SENTIMENT (The Masses)

Retail sentiment captures the emotional state of individual investors. They are the most reliable contrary indicator at extremes.

| **Indicator** | **Source** | **Frequency** | **Interpretation** |
|---|---|---|---|
| **AAII Bull-Bear Spread** | AAII | Weekly (Thursday) | Primary retail sentiment (most reliable) |
| **AAII % Bulls** | AAII | Weekly | Bullish individual investors |
| **AAII % Bears** | AAII | Weekly | Bearish individual investors |
| **AAII % Neutral** | AAII | Weekly | Undecided (low = conviction extreme) |
| **Investor Intelligence Bull/Bear** | II | Weekly | Newsletter writer sentiment |
| **II % Bulls** | II | Weekly | Bullish newsletters |
| **II % Bears** | II | Weekly | Bearish newsletters |
| **CNN Fear & Greed Index** | CNN | Daily | Composite retail gauge (7 inputs) |
| **UMich Consumer Sentiment** | UMich | Monthly | Consumer confidence (broader) |

#### Derived Retail Metrics

| **Metric** | **Formula** | **Threshold** | **Signal** |
|---|---|---|---|
| **AAII Extreme Bullish** | Bull-Bear > +30% | Above threshold | Contrarian sell zone |
| **AAII Extreme Bearish** | Bull-Bear < -20% | Below threshold | Contrarian buy zone |
| **AAII Washed** | Bulls < 25% | Below threshold | Capitulation signal |
| **II Divergence** | II vs AAII diverging | Notable gap | Mixed crowd signal |
| **Fear & Greed Extreme** | F&G < 20 or > 80 | At extremes | Contrarian signal |

#### Regime Thresholds: Retail Sentiment

| **AAII Bull-Bear** | **Regime** | **Historical Forward Returns (1 yr)** | **Signal** |
|---|---|---|---|
| > +30% | Extreme Bullish | Below average | Contrarian sell |
| +15% to +30% | Bullish | Slightly below avg | Caution |
| -10% to +15% | Neutral | Average | No edge |
| -20% to -10% | Bearish | Above average | Favorable |
| < -20% | Extreme Bearish | **+15%+ avg** | Contrarian buy |

**The AAII Truth:** Below -20% bull-bear, forward 12-month returns average +15%+. The crowd's fear is your opportunity.

---

### B. PROFESSIONAL POSITIONING (The Smart Money)

Professional positioning captures how active managers and institutions are allocated. They have more capital but similar emotional biases.

| **Indicator** | **Source** | **Frequency** | **Interpretation** |
|---|---|---|---|
| **NAAIM Exposure Index** | NAAIM | Weekly (Wednesday) | Active manager equity exposure (0-200%) |
| **NAAIM Median Exposure** | NAAIM | Weekly | Median manager (less skewed) |
| **COT Net Speculative Position** | CFTC | Weekly (Tuesday) | Futures positioning by category |
| **COT Asset Manager Net** | CFTC | Weekly | Institutional futures positioning |
| **COT Leveraged Net** | CFTC | Weekly | Hedge fund futures positioning |
| **Hedge Fund Beta** | Prime Broker Data | Weekly | Gross/net exposure (when available) |
| **Mutual Fund Cash Levels** | ICI | Monthly | Cash drag / dry powder |

#### Derived Professional Metrics

| **Metric** | **Formula** | **Threshold** | **Signal** |
|---|---|---|---|
| **NAAIM Fully Invested** | Exposure > 100% | Above threshold | No marginal buyers |
| **NAAIM Underweight** | Exposure < 50% | Below threshold | Dry powder available |
| **NAAIM Extreme Low** | Exposure < 25% | At threshold | Capitulation |
| **COT Crowded Long** | Net position > 2σ | Above threshold | Contrarian sell |
| **COT Crowded Short** | Net position < -2σ | Below threshold | Contrarian buy (cover squeeze) |

#### Regime Thresholds: Professional Positioning

| **NAAIM Exposure** | **Regime** | **Interpretation** | **Signal** |
|---|---|---|---|
| > 100% | Fully Invested | Managers levered long | Contrarian sell |
| 80-100% | Bullish | Normal bullish positioning | Caution |
| 50-80% | Neutral | Balanced | No edge |
| 25-50% | Underweight | Cash on sidelines | Favorable |
| < 25% | Capitulation | Extreme underweight | **Contrarian buy** |

**The NAAIM Signal:** When managers are >100% invested, they've borrowed to buy more. When they're <25%, they've panic-sold. Neither state is sustainable.

---

### C. OPTIONS POSITIONING (The Hedgers)

Options positioning captures hedging demand (puts) vs speculation (calls). Elevated put buying indicates fear; elevated call buying indicates greed.

| **Indicator** | **Source** | **Frequency** | **Interpretation** |
|---|---|---|---|
| **Equity Put/Call Ratio** | CBOE | Daily | Total equity P/C (primary) |
| **Equity P/C (10d MA)** | CBOE | Daily | Smoothed P/C |
| **Index Put/Call Ratio** | CBOE | Daily | SPX/SPY options only |
| **Total Put/Call Ratio** | CBOE | Daily | All options (equity + index) |
| **VIX Level** | CBOE | Daily | Implied volatility (fear gauge) |
| **VIX vs 50d MA** | Derived | Daily | Fear relative to recent |
| **VIX vs 200d MA** | Derived | Daily | Fear relative to normal |
| **VIX Term Structure** | CBOE | Daily | Contango (calm) vs Backwardation (stress) |
| **VVIX** | CBOE | Daily | Vol of vol (uncertainty) |
| **SKEW** | CBOE | Daily | Tail risk pricing |

#### Derived Options Metrics

| **Metric** | **Formula** | **Threshold** | **Signal** |
|---|---|---|---|
| **P/C Elevated Fear** | Equity P/C (10d) > 1.1 | Above threshold | Contrarian buy |
| **P/C Complacency** | Equity P/C (10d) < 0.7 | Below threshold | Contrarian sell |
| **VIX Spike** | VIX > 30 | Above threshold | Fear spike (buy zone) |
| **VIX Complacent** | VIX < 15 | Below threshold | Complacency (caution) |
| **VIX Backwardation** | VIX > VIX3M | Inverted | Acute stress (buy) |
| **SKEW Elevated** | SKEW > 140 | Above threshold | Tail hedging active |

#### Regime Thresholds: Options

| **VIX Level** | **Term Structure** | **P/C Ratio** | **Regime** | **Signal** |
|---|---|---|---|---|
| > 40 | Backwardation | > 1.2 | Panic | **Extreme buy** |
| 30-40 | Backwardation | > 1.0 | Fear | Buy zone |
| 20-30 | Flat | 0.8-1.0 | Elevated | Neutral to favorable |
| 15-20 | Contango | 0.7-0.8 | Normal | No edge |
| < 15 | Steep Contango | < 0.7 | Complacency | **Caution/Sell** |

**The VIX Truth:** Buy when VIX spikes above 30 with backwardation. Sell when VIX compresses below 15 with steep contango. Fear creates opportunity; complacency creates risk.

---

### D. FUND FLOWS (The Capital)

Fund flows capture actual capital movement. Flows follow price but indicate crowding when extreme.

| **Indicator** | **Source** | **Frequency** | **Interpretation** |
|---|---|---|---|
| **ETF Equity Flows (20d)** | ICI/Bloomberg | Weekly | Retail flow proxy |
| **SPY/QQQ Flows** | Bloomberg | Daily | Large-cap equity flows |
| **Mutual Fund Equity Flows** | ICI | Weekly/Monthly | Institutional flows |
| **Bond Fund Flows** | ICI | Weekly | Risk-off indicator |
| **Money Market Fund Assets** | ICI | Weekly | Cash on sidelines |
| **MMF Assets YoY%** | ICI | Weekly | Cash accumulation rate |
| **Bank Deposit Flows** | H.8 | Weekly | Consumer cash positioning |

#### Derived Flow Metrics

| **Metric** | **Formula** | **Threshold** | **Signal** |
|---|---|---|---|
| **Equity Outflows Extreme** | 4-wk equity outflows > $50B | Above threshold | Capitulation |
| **Equity Inflows Extreme** | 4-wk equity inflows > $50B | Above threshold | Euphoria |
| **MMF Record High** | MMF > prior peak | New high | Dry powder available |
| **Bond Rotation** | Bond inflows + equity outflows | Both occurring | Risk-off in progress |

#### Regime Thresholds: Flows

| **Flow State** | **Equity Flows** | **MMF Assets** | **Interpretation** | **Signal** |
|---|---|---|---|---|
| **Capitulation** | Heavy outflows (4+ wks) | Rising sharply | Panic selling | Contrarian buy |
| **Rotation Out** | Moderate outflows | Rising | De-risking | Cautious |
| **Neutral** | Mixed | Stable | No clear signal | No edge |
| **Rotation In** | Moderate inflows | Falling | Re-risking | Favorable |
| **Euphoria** | Heavy inflows (4+ wks) | Falling sharply | FOMO buying | **Contrarian sell** |

**The Flow Truth:** Sustained outflows with rising MMF assets = capitulation setup. Sustained inflows with falling MMF = euphoria setup. Trade against extremes.

---

## Sentiment & Positioning Index (SPI)

The SPI synthesizes all sentiment indicators into a single composite. **Convention: High SPI = Contrarian Bullish** (fear, light positioning, outflows).

### Formula

```
SPI = 0.20 × z(Put_Call_Ratio_10d)
    + 0.15 × z(VIX_vs_50d_MA)
    + 0.15 × z(-AAII_Bull_Bear)           # Inverted (low bull-bear = high SPI)
    + 0.15 × z(-NAAIM_Exposure)           # Inverted (low exposure = high SPI)
    + 0.10 × z(-Investor_Intelligence)    # Inverted
    + 0.10 × z(-ETF_Equity_Flows_20d)     # Inverted (outflows = high SPI)
    + 0.10 × z(VIX_Term_Backwardation)    # Backwardation = stress = high SPI
    + 0.05 × z(Money_Market_Assets_YoY)   # Cash on sidelines
```

### Weight Rationale

| **Component** | **Weight** | **Rationale** |
|---|---|---|
| Put/Call Ratio | 0.20 | Real-time hedging demand |
| VIX vs 50d | 0.15 | Fear relative to recent |
| AAII Bull-Bear | 0.15 | Primary retail sentiment |
| NAAIM Exposure | 0.15 | Professional positioning |
| II Bull-Bear | 0.10 | Newsletter sentiment |
| ETF Flows | 0.10 | Capital flows |
| VIX Backwardation | 0.10 | Acute stress indicator |
| MMF Assets | 0.05 | Dry powder gauge |

### SPI Interpretation

| **SPI Range** | **Regime** | **Contrarian Signal** | **Implication** |
|---|---|---|---|
| > +1.5 | Extreme Fear | **Strong buy zone** | Capitulation, wash-out |
| +1.0 to +1.5 | High Fear | Buy zone | Underexposed crowd |
| +0.5 to +1.0 | Elevated Fear | Favorable entry | Light positioning |
| -0.5 to +0.5 | Neutral | No contrarian edge | Balanced |
| -1.0 to -0.5 | Optimistic | Elevated risk | Crowded longs |
| < -1.0 | Euphoria | **Contrarian sell zone** | Complacency peak |

---

## Sentiment-Structure Divergence (SSD)

SSD measures alignment between sentiment and structure. It's the "capitulation vs blow-off" indicator.

### Formula

```
SSD = z(SPI) + z(MSI)
```

### Interpretation

| **SSD Range** | **State** | **Interpretation** | **Action** |
|---|---|---|---|
| > +2.0 | Extreme Capitulation | Fear + broken structure | Maximum buy zone |
| +1.5 to +2.0 | Capitulation | Fear + weak structure | Strong buy zone |
| +0.5 to +1.5 | Fear Dominates | Fear with mixed structure | Favorable |
| -0.5 to +0.5 | Aligned | Sentiment and structure in sync | Trade structure |
| -1.5 to -0.5 | Euphoria Dominates | Greed with mixed structure | Caution |
| -2.0 to -1.5 | Blow-Off | Euphoria + strong structure | Sell zone |
| < -2.0 | Extreme Blow-Off | Maximum greed + strong structure | **Maximum sell zone** |

**The SSD Signal:** SSD > +1.5 means the crowd has capitulated while structure is weak, a classic bottom formation. SSD < -1.5 means the crowd is euphoric while structure is strong, a classic blow-off top formation.

---

## Key Thresholds Summary

| **Indicator** | **Threshold** | **Signal** |
|---|---|---|
| **AAII Bull-Bear** | >+30% | Euphoria (contrarian sell) |
| **AAII Bull-Bear** | <-20% | Capitulation (contrarian buy) |
| **NAAIM Exposure** | >100% | Fully invested (contrarian sell) |
| **NAAIM Exposure** | <50% | Underexposed (contrarian buy) |
| **Put/Call (10d)** | >1.1 | Fear elevated (buy) |
| **Put/Call (10d)** | <0.7 | Complacency (sell) |
| **VIX** | >30 | Fear spike (buy) |
| **VIX** | <15 | Complacency (sell) |
| **VIX Term Structure** | Backwardation | Acute stress (buy) |
| **SPI** | >+1.5 | Extreme fear (strong buy) |
| **SPI** | <-1.0 | Euphoria (sell) |
| **SSD** | >+1.5 | Capitulation low (buy) |
| **SSD** | <-1.5 | Blow-off top (sell) |

---

## Integration with Trading Strategy

### Using Sentiment for Sizing (Not Direction)

Sentiment doesn't determine direction. Fundamentals and structure do. Sentiment determines *how much* and *when*.

| **Scenario** | **Fundamental** | **Structure** | **Sentiment** | **Action** |
|---|---|---|---|---|
| Full Setup | Bullish | Confirming | Fear | **Maximum position** |
| Standard | Bullish | Confirming | Neutral | Normal position |
| Cautious | Bullish | Confirming | Euphoric | Reduced position |
| Wait | Bullish | Diverging | Any | No new positions |
| Counter-Trend | Bearish | Weak | Extreme Fear | Tactical exhaustion only |

### Sentiment Confirmation for Entries

Before entering a Perfect Setup position, check SPI:

- **SPI > +0.5:** Sentiment favorable, full position
- **SPI -0.5 to +0.5:** Sentiment neutral, normal position
- **SPI < -0.5:** Sentiment unfavorable, reduced position or wait

### Sentiment Triggers for Exits

Sentiment extremes can trigger exit reviews:

- **SPI < -1.0 with strong structure:** Blow-off warning, trail stops tight
- **SPI > +1.5 with weak structure:** Capitulation may be forming, prepare to add
- **SSD < -1.5:** Active blow-off, consider profit-taking

---

## Tactical Exhaustion Trade Qualification

Pillar 12 adds a sentiment requirement to tactical exhaustion trades:

**Original Criteria (from Pillar 11/Structure):**
1. Price below 200d MA for >60 trading days
2. Z-RoC > -1.0 and rising
3. Volatility compressing
4. Price stabilizing near support
5. No new lows in last 10 trading days

**Additional Sentiment Requirement:**
6. **SPI > +1.0** (fear elevated, contrarian edge present)

Without elevated fear, there's no contrarian edge to exploit. Don't bottom-fish without sentiment support.

---

## Current State Template

**NOTE:** Fill in current values from live data sources. Do not reference any pre-filled values as current.

| **Indicator** | **Current** | **Signal** | **Implication** |
|---|---|---|---|
| AAII Bull-Bear | [VALUE] | [Euphoric/Bullish/Neutral/Bearish/Capitulation] | [INTERPRETATION] |
| NAAIM Exposure | [VALUE] | [Fully Invested/Bullish/Neutral/Underweight/Capitulation] | [INTERPRETATION] |
| Put/Call (10d) | [VALUE] | [Complacent/Normal/Elevated/Fear] | [INTERPRETATION] |
| VIX | [VALUE] | [Complacent/Normal/Elevated/Spike] | [INTERPRETATION] |
| VIX Term | [VALUE] | [Contango/Flat/Backwardation] | [INTERPRETATION] |
| ETF Flows (20d) | [VALUE] | [Inflows/Neutral/Outflows] | [INTERPRETATION] |
| MMF Assets | [VALUE] | [Rising/Stable/Falling] | [INTERPRETATION] |
| SPI | [VALUE] | [Regime] | [INTERPRETATION] |
| SSD | [VALUE] | [Capitulation/Aligned/Blow-off] | [INTERPRETATION] |

---

## The Contrarian's Creed

1. **The crowd is a lagging indicator.** By the time they're bullish, they've bought. By the time they're bearish, they've sold.

2. **Extremes mean-revert.** Sentiment above +1.5 or below -1.0 doesn't persist. Trade the reversion.

3. **Fear creates opportunity.** SPI > +1.5 with broken structure is where fortunes are made.

4. **Euphoria creates risk.** SPI < -1.0 with strong structure is where fortunes are lost.

5. **Sentiment alone is not a trade.** It sizes and times trades identified by fundamentals and structure.

---

---

## E. SENTIMENT SUB-COMPONENT DEEP DIVE (Beyond the Headlines)

Headline sentiment surveys (AAII, II) obscure structural shifts. Decomposing surveys into demographic cuts, time-series dynamics, and ratio behaviors reveals signals the aggregates mask.

### AAII Survey Decomposition

| **Component** | **Formula/Source** | **Threshold** | **Signal** |
|---|---|---|---|
| **Bull-Bear Spread** | Bulls - Bears | <-20% or >+30% | Primary contrarian signal |
| **Neutral Share** | AAII Neutral % | <15% | High conviction (either direction) |
| **Bulls vs Historical** | Z-score vs 10Y avg | >+1.5 or <-1.5 | Level extreme |
| **4-Week MA Bull-Bear** | Smoothed spread | Less noisy than weekly | Trend in sentiment |
| **Weekly Change** | WoW delta in spread | >±15 ppts | Rapid sentiment shift |

### AAII Regime Dynamics

Historical AAII readings cluster in recognizable patterns:

- **Structural Bull:** 4-wk avg bull-bear spread >+15 for 6+ months
- **Structural Bear:** 4-wk avg bull-bear spread <-5 for 6+ months
- **Transition:** Spread crossing zero from extreme regime
- **Noise Regime:** Spread oscillating 0 to +15 range

The transitions are more informative than absolute levels. Watch for sustained crossovers from extreme regimes.

### Investors Intelligence (II) Survey

II surveys newsletter writers rather than individual investors. Historically II diverges from AAII at major turns because newsletters lag individual fear/greed reactions.

| **II Signal** | **Interpretation** |
|---|---|
| **II Bulls > 55% with AAII Neutral** | Advisor complacency warning |
| **II Bears > 40%** | Extreme professional fear |
| **II - AAII Spread** | Divergence between newsletters and retail |

### NAAIM Sub-Component Analysis

NAAIM Exposure Index is the headline, but NAAIM also publishes:

- **NAAIM Mean Exposure:** Cross-sectional average
- **NAAIM Median Exposure:** Less skewed by extreme managers
- **NAAIM Min/Max:** Range of manager positioning
- **NAAIM Standard Deviation:** Cross-sectional dispersion

When NAAIM SD is very high, managers disagree materially. When SD is low, crowd behavior is uniform. Uniform bullish at extremes is particularly dangerous.

### CNN Fear & Greed Index Components

The CNN F&G aggregate hides seven sub-components:

1. **Market Momentum** (SPX vs 125d MA)
2. **Stock Price Strength** (52-week NH-NL)
3. **Stock Price Breadth** (McClellan advance-decline volume)
4. **Put/Call Ratio** (5-day avg)
5. **Junk Bond Demand** (HY vs IG spread)
6. **Market Volatility** (VIX vs 50d MA)
7. **Safe Haven Demand** (Stocks vs bonds 20-day returns)

When F&G composite is extreme but sub-components diverge (e.g., sentiment-reading is "extreme fear" but breadth is holding up), the signal is weaker. When all 7 align, conviction is highest.

### Derived Sentiment Metrics

| **Metric** | **Formula** | **Threshold** | **Signal** |
|---|---|---|---|
| **Crowd Divergence** | AAII Bull-Bear - II Bull-Bear | >±15 ppts | Retail-professional split |
| **Sentiment Thrust** | 4-wk Δ AAII Bull-Bear | >+25 ppts | Rapid fear-to-greed shift |
| **Capitulation Crosscheck** | AAII <-15 AND NAAIM <30 AND VIX >25 | All conditions | High-conviction bottom signal |
| **Blow-Off Crosscheck** | AAII >+20 AND NAAIM >85 AND VIX <13 | All conditions | High-conviction top signal |

---

## F. POSITIONING DATA DEEP DIVE (Beyond Surveys)

Actual positioning (not just survey sentiment) provides market-verified extremes. The CFTC Commitment of Traders (COT) report, hedge fund data, and gamma positioning reveal where capital actually sits.

### COT Report Structure

The CFTC publishes weekly positioning (Tuesday-dated, Friday-released) for futures contracts by trader category:

| **Category** | **Role** | **Interpretation** |
|---|---|---|
| **Asset Managers (Large Investors)** | Long-only institutional | Structural positioning |
| **Leveraged Funds** | Hedge funds | Tactical positioning |
| **Commercials (Producers/Users)** | Hedgers | Often counter-trend |
| **Non-Reportable (Small Specs)** | Retail | Contrarian indicator |
| **Dealer** | Swap dealers | Hedging of counterparty activity |

### Key COT Contracts for Macro

| **Contract** | **Relevance** |
|---|---|
| **S&P 500 (E-mini)** | Equity exposure positioning |
| **10Y / 30Y Treasury** | Duration positioning |
| **2Y Treasury** | Fed-path positioning |
| **USD Index** | Dollar positioning |
| **Gold** | Safe-haven positioning |
| **Crude Oil** | Commodity/inflation positioning |
| **VIX** | Vol positioning |

### COT Signals

| **Signal** | **Interpretation** |
|---|---|
| **Leveraged Funds Crowded Long** | Net position > +2σ vs 5Y | Contrarian short setup |
| **Leveraged Funds Crowded Short** | Net position < -2σ vs 5Y | Contrarian long setup (squeeze risk) |
| **Asset Manager Positioning** | More structural, less contrarian |
| **Small Spec Extreme** | High contrarian value |
| **Commercial Divergence** | Producers hedging at extremes often right |

### Hedge Fund Beta and Exposure

Hedge fund aggregate data (Goldman Sachs, Morgan Stanley prime broker flows, Bloomberg NAV indices):

| **Metric** | **Source** | **Signal** |
|---|---|---|
| **HFRX Equity Hedge Net Exposure** | HFRX | Industry net long/short |
| **GS Prime Book Net Exposure** | Goldman (subscription) | Hedge fund net equity exposure |
| **GS Prime Gross Exposure** | Goldman | Leverage indicator |
| **Macro Fund Positioning** | HFRX Macro | Systematic macro positioning |

### Dealer Gamma Positioning (Options Market)

Dealer gamma is the aggregate gamma exposure of market makers. It materially affects intraday volatility and support/resistance levels.

| **Regime** | **Dealer Gamma** | **Market Impact** |
|---|---|---|
| **Long Gamma** | Dealers long gamma | Dealers sell rallies, buy dips; suppresses vol |
| **Short Gamma** | Dealers short gamma | Dealers buy rallies, sell dips; amplifies vol |
| **Gamma Flip Level** | Price where gamma crosses zero | Magnetic support/resistance |

Monitor via SpotGamma, Nomura QDS, or SqueezeMetrics.

### 0DTE (Zero Days to Expiry) Options

Since 2022, 0DTE options trading has grown to >40% of SPX options volume. These options have dramatic intraday gamma effects and have reshaped short-term sentiment dynamics.

| **Signal** | **Interpretation** |
|---|---|
| **0DTE Put Volume Spike** | Intraday fear (short-term) |
| **0DTE Call Volume Spike** | Intraday FOMO (short-term) |
| **End-of-Day Pin Risk** | Gamma-driven expiration levels |

### Derived Positioning Metrics

| **Metric** | **Formula** | **Threshold** | **Signal** |
|---|---|---|---|
| **Leveraged Long Crowding** | COT lev fund net / 5Y max | >0.85 | Crowded long |
| **Leveraged Short Crowding** | COT lev fund net / 5Y min | >0.85 | Crowded short (squeeze) |
| **Gross Leverage** | HF Gross Exposure | >250% | High-conviction regime |
| **Dealer Gamma Level** | SpotGamma SPX gamma | Negative | Short gamma regime |

---

## G. FLOW DATA DEEP DIVE (Where Capital Actually Moves)

Fund flows capture actual capital movement, not just expressed sentiment. Flows lag price but indicate crowding at extremes.

### Flow Categories

| **Flow Type** | **Source** | **Interpretation** |
|---|---|---|
| **ETF Flows (Equity)** | Bloomberg, ICI | Passive/active retail + institutional |
| **ETF Flows (Fixed Income)** | Bloomberg, ICI | Risk-off signal |
| **Mutual Fund Flows** | ICI | More institutional (lagging) |
| **Money Market Fund Assets** | ICI | Cash on sidelines |
| **Margin Debt** | FINRA | Leverage in system |
| **Cash in Brokerage** | Call reports | Dry powder |
| **Sector ETF Flows** | Bloomberg | Rotation dynamics |
| **International Fund Flows** | EPFR Global | Cross-border capital |

### Flow Signal Interpretation

| **Flow Pattern** | **Signal** |
|---|---|
| **Sustained equity inflows + falling MMF assets** | Full risk-on (potential euphoria) |
| **Equity outflows + rising MMF assets** | Risk-off rotation |
| **Sector rotation into defensives** | Late-cycle signal |
| **TLT (duration) inflows + SPX outflows** | Flight-to-quality active |
| **Gold ETF inflows + Equity outflows** | Safe-haven demand |
| **HYG outflows + TLT inflows** | Credit-to-duration rotation |

### Margin Debt Dynamics

FINRA publishes monthly margin debt (lagged ~30 days). Margin debt as % of market cap signals leverage extremes.

| **Margin Debt Metric** | **Signal** |
|---|---|
| **Margin Debt YoY Growth** | >+30% = Speculative buildup |
| **Margin Debt / Market Cap** | >2% historically peak zone |
| **Margin Debt 6M Change** | Rapid deleveraging signals risk-off |

### Dark Pool Flow Data

FINRA ATS publishes dark pool volumes. Rising dark pool share signals institutional repositioning.

| **Signal** | **Interpretation** |
|---|---|
| **Dark Pool Volume > 40%** | High institutional activity |
| **Rising Dark Pool %** | Institutions positioning ahead of move |

### Derived Flow Metrics

| **Metric** | **Formula** | **Threshold** | **Signal** |
|---|---|---|---|
| **4-Week Net Equity Flow** | Bloomberg aggregate | >+$50B = Euphoria risk |
| **Cash as % of S&P Market Cap** | MMF / SPX MC | >5% = Dry powder high |
| **Margin Debt Velocity** | 3M change in margin | Rapid rise = Speculation |
| **Sector Rotation Index** | % sectors with positive flows | <30% = Broad de-risking |

---

## H. INTERNATIONAL SENTIMENT (Global Positioning)

Sentiment isn't just a US phenomenon. International sentiment indicators cross-verify US signals and sometimes lead US moves.

### Global Sentiment Surveys

| **Survey** | **Region** | **Frequency** | **Interpretation** |
|---|---|---|---|
| **BofA Global Fund Manager Survey** | Global institutional | Monthly | Key institutional positioning |
| **ZEW Economic Sentiment (Germany)** | Germany | Monthly | European leading indicator |
| **Sentix Indices** | Global | Monthly | Investor sentiment by region |
| **Nikkei Heikin Ashi Sentiment** | Japan | Monthly | Japanese equity sentiment |
| **Hang Seng/CSI Positioning** | Greater China | Various | China-specific |

### BofA Global Fund Manager Survey (GFMS)

The monthly BofA survey of ~200 global institutional managers is particularly valuable. Tracked items:

- **Cash level %** (historically <3.5% = sell signal, >5.5% = buy signal)
- **Equity overweight/underweight**
- **US vs International positioning**
- **Growth vs Value preference**
- **Most crowded trades**
- **Tail risks**

Extreme cash levels in GFMS have historically been reliable contrarian signals.

### Cross-Border Capital Flows (EPFR)

EPFR Global tracks cross-border mutual fund and ETF flows. Key signals:

- **Outflows from EM equity funds** = Global risk-off
- **Outflows from US equity funds to international** = Rotation away from US
- **Inflows to safe-haven currencies (CHF, JPY)** = Flight-to-quality

### Global Retail Sentiment

Retail sentiment measures outside the US:

- **Tokyo Retail Sentiment** (various Japanese brokers)
- **Shanghai Composite Margin Debt** (weekly, key for China)
- **European Retail Sentiment** (various EU brokers)

### Derived International Sentiment Metrics

| **Metric** | **Formula** | **Threshold** | **Signal** |
|---|---|---|---|
| **GFMS Cash % Extreme** | Current cash % | <3.5% = Euphoria; >5.5% = Fear | Contrarian |
| **EM Sentiment Divergence** | EM flows vs DM flows | Net outflow spread | EM-specific stress |
| **Global Risk Diffusion** | % of major markets with extreme fear readings | >60% = Global capitulation | Contrarian buy |

---

## I. BEHAVIORAL SIGNALS (Non-Traditional Sentiment)

Beyond surveys and positioning, behavioral signals from trading patterns, search data, and social media provide real-time sentiment reads.

### Google Trends Keywords

Search volume for specific terms correlates with sentiment at extremes:

| **Keyword** | **Signal** |
|---|---|
| **"recession"** | Fear spike |
| **"market crash"** | Acute fear |
| **"bear market"** | Structural concern |
| **"roaring kitty" / meme terms** | Retail speculation |
| **"coupon", "payday loan"** | Consumer stress |

### Social Media Sentiment

Aggregated social media data (Twitter/X, Reddit WallStreetBets, StockTwits) provides real-time retail sentiment:

- **WSB Mentions** of specific tickers (retail attention flow)
- **Twitter Sentiment** (positive/negative ratio)
- **StockTwits Bullish/Bearish** (explicit tagging)

### Options Activity Extremes

Beyond headline put/call ratios, specific options patterns:

| **Signal** | **Interpretation** |
|---|---|
| **Equity-Only P/C > 1.2** | Retail fear extreme |
| **VIX call buying surge** | Tail hedge demand |
| **Short-duration call buying** | Retail FOMO |
| **0DTE Call/Put ratio extreme** | Intraday sentiment spike |

### Cryptocurrency as Sentiment Proxy

Bitcoin and high-beta crypto often trade as risk-on/risk-off proxies:

| **Signal** | **Interpretation** |
|---|---|
| **BTC 30d vol > SPX 30d vol × 5** | Normal risk regime |
| **BTC rallying while equities fall** | Risk-on bleed into alts |
| **Crypto volume spikes** | Retail speculation peaks |
| **Stablecoin supply growth** | Sidelines building |

### Meme Stock and Retail Flow Signals

The 2021 meme stock phenomenon revealed retail coordination via social media. Markers:

- **GME/AMC volume spikes** = Retail speculation active
- **Short squeeze frequency** = Positioning extremes
- **Zero-commission trading volumes (Robinhood, IBKR)** = Retail engagement

### Derived Behavioral Metrics

| **Metric** | **Formula** | **Threshold** | **Signal** |
|---|---|---|---|
| **Recession Search Index** | Google Trends "recession" | 2x 3Y avg | Fear spike |
| **WSB Mention Volume** | Aggregate ticker mentions | Spike >3σ | Retail attention extreme |
| **BTC-SPX Correlation (60d)** | Rolling correlation | Falling to 0 = decoupling | Regime shift |

---

## J. SENTIMENT CYCLE STAGES (The Four-Phase Framework)

Sentiment cycles progress through predictable stages, each with distinct positioning and action signals.

### The Four Stages

```
STAGE 1: Fear / Capitulation (the bottom)
→ AAII deeply bearish, NAAIM low, VIX spiking
→ Cash on sidelines builds
→ Marginal seller exhausted
→ ACTION: Accumulate

STAGE 2: Skepticism (early recovery)
→ Sentiment rising but lagging price
→ Retail still bearish, institutions beginning to build
→ "Bull trap" narratives common
→ ACTION: Build positions, trend confirmation

STAGE 3: Confidence (mid-cycle)
→ Sentiment normalizing, neutral-to-bullish
→ Flows constructive, positioning rising
→ Volatility compressing
→ ACTION: Hold, monitor for extremes

STAGE 4: Euphoria / Blow-Off (the top)
→ AAII bullish extreme, NAAIM near max
→ Cash depleted, leverage peaked
→ Complacency extreme (low VIX, low SKEW)
→ ACTION: Reduce, prepare for mean-reversion
```

### Stage Detection Signals

| **Stage** | **Key Markers** | **SPI Range** |
|---|---|---|
| **Stage 1 (Capitulation)** | VIX >30, AAII <-15, NAAIM <25, MMF spike | SPI > +1.5 |
| **Stage 2 (Skepticism)** | VIX normalizing, sentiment improving lag | SPI +0.5 to +1.5 |
| **Stage 3 (Confidence)** | VIX <18, sentiment positive, flows in | SPI -0.5 to +0.5 |
| **Stage 4 (Euphoria)** | VIX <13, AAII >+20, NAAIM >90, cash low | SPI < -1.0 |

### Stage Transitions

Transitions between stages are the actionable moments. Stage 1 → 2 transition signals are particularly valuable (early recovery):

- NAAIM crosses above 50 (from below)
- VIX falls below 20 (from above 25)
- 4-wk AAII bull-bear spread crosses zero
- Monthly MMF assets peak and start declining

Stage 3 → 4 transitions are warnings:

- NAAIM crosses above 85
- VIX compresses below 13
- AAII bull-bear > +20 and rising
- Monthly MMF assets falling rapidly

---

## K. TACTICAL APPLICATION FRAMEWORK

Sentiment integrates with fundamentals, structure, and positioning into the broader trading framework.

### The Sentiment Sizing Matrix

The below combines sentiment with fundamentals and structure to determine position size:

| **Fundamentals** | **Structure** | **Sentiment** | **Position Size** |
|---|---|---|---|
| Strong bullish | Confirming | Fear (SPI >+1.0) | 100% target (max) |
| Strong bullish | Confirming | Neutral | 80% target |
| Strong bullish | Confirming | Euphoria (SPI <-0.5) | 50% target |
| Bullish | Diverging | Any | No new longs |
| Neutral | Confirming | Fear extreme | Tactical exhaustion only |
| Bearish | Weak | Euphoria (SPI <-1.0) | Short setup |

### Perfect Setup Criteria

"Perfect Setups" require alignment across all three dimensions. Sentiment confirmation is required:

1. **Fundamentals:** Pillar analysis supports direction
2. **Structure:** Trend + momentum + breadth + relative strength confirm
3. **Sentiment:** Not opposing the trade (SPI > -0.5 for longs; SPI < +0.5 for shorts)
4. **Cross-Pillar:** No red flags from other pillars
5. **Plumbing:** Liquidity regime supportive
6. **Risk/Reward:** Favorable asymmetry

### Tactical Exhaustion Trades

Exhaustion trades are counter-trend. They require sentiment extremes as the catalyst:

- **Long Setup:** SPI > +1.5, SSD > +1.5, price at/near support, vol spiking
- **Short Setup:** SPI < -1.0, SSD < -1.0, price extended, vol compressed

Exhaustion trades are tactical, not core. Expected duration: 5-20 trading days. Tight stops.

---

## L. SEGMENTED SENTIMENT INDEX (SPI by Cohort)

The aggregate SPI can be decomposed to isolate specific cohort positioning.

### SPI Sub-Composites

| **Sub-Composite** | **Key Inputs** | **Measures** |
|---|---|---|
| **Retail SPI** | AAII, CNN F&G retail components, Google Trends | Individual investor positioning |
| **Professional SPI** | NAAIM, II, GFMS, hedge fund data | Institutional positioning |
| **Options SPI** | Put/call, VIX, SKEW, dealer gamma | Options market stress |
| **Flow SPI** | ETF flows, MMF assets, margin debt | Capital movement |
| **International SPI** | GFMS cash, EPFR flows, Sentix | Global sentiment |

### Composite Segmented SPI

```
Segmented_SPI = 0.20 × z(Retail_Sub_Composite)
              + 0.20 × z(Professional_Sub_Composite)
              + 0.20 × z(Options_Sub_Composite)
              + 0.15 × z(Flow_Sub_Composite)
              + 0.15 × z(International_Sub_Composite)
              + 0.10 × z(Behavioral_Sub_Composite)
```

### Sub-Composite Divergence Patterns

| **Pattern** | **Retail** | **Professional** | **Interpretation** |
|---|---|---|---|
| **Retail fear, Pros calm** | Extreme fear | Neutral | Buy: pros know retail is overreacting |
| **Pros fear, Retail calm** | Neutral | Extreme fear | Warn: pros see what retail doesn't |
| **Both fear** | Extreme fear | Extreme fear | Maximum buy conviction |
| **Both euphoria** | Extreme bullish | Extreme bullish | Maximum sell conviction |

**The Smart-Dumb Money Divergence:** When retail is euphoric while professionals are defensive, it's a classic late-cycle signal. When retail is terrified while professionals are quietly accumulating, it's a classic bottom formation.

---

## Integration with Three-Engine Framework

### Pillar 12 → Pillar 11 (Market Structure)

The Sentiment-Structure Divergence (SSD) is the formal bridge. When sentiment extremes align with structure extremes, conviction maximizes.

**Transmission:** Sentiment extremes precede structural turns by 1-3 weeks at bottoms (fear exhaustion) and 2-6 weeks at tops (euphoria persistence).

**Cross-Pillar Signal:** SSD > +1.5 is the highest-conviction tactical long setup; SSD < -1.5 is the highest-conviction tactical short setup. Both rare (2-3 times per cycle).

### Pillar 12 → Pillar 9 (Financial)

Sentiment extremes often precede financial conditions repricing. Extreme complacency (low VIX, tight spreads, euphoric sentiment) typically precedes spread widening.

**Transmission:** Sentiment extremes at market tops lead credit spread widening by 1-3 months. SPI < -1.0 sustained for 4+ weeks is a leading warning for HY OAS repricing risk.

**Cross-Pillar Signal:** SPI < -1.0 AND HY OAS < 300 bps = mispricing warning. When both converge, credit spread repricing follows.

### Pillar 12 → Pillar 5 (Consumer)

Consumer confidence and financial wealth sentiment affect spending with 1-3 month lag. Retail sentiment extremes can precede consumer confidence shifts.

**Transmission:** Equity-driven wealth effects combine with sentiment to affect consumer spending. Top quintile spends based on equity wealth; their sentiment swings create spending swings.

**Cross-Pillar Signal:** When SPI < -1.0 AND CCI weakening, K-shaped consumer stress accelerates because top quintile confidence wavers.

### Pillar 12 → Pillar 1 (Labor)

Sentiment affects hiring confidence, especially at small businesses. Extreme fear can accelerate hiring freezes; extreme greed can drive wage inflation (worker confidence in outside options).

**Transmission:** Small business sentiment (NFIB) correlates with broad sentiment at extremes. Labor hoarding shifts to labor cutting when sentiment breaks.

**Cross-Pillar Signal:** Sentiment capitulation combined with LFI > +0.8 creates layoff acceleration risk.

### Pillar 12 → Pillar 3 (Growth)

Sentiment affects both actual growth (via spending and investment decisions) and perceived growth (via expectations). Sentiment extremes often precede growth inflections by 2-6 months.

**Transmission:** Business and consumer sentiment converge with hiring and spending decisions to affect real GDP. The sentiment → spending → GDP chain has 2-4 quarter lag.

**Cross-Pillar Signal:** When SPI extremes align with cross-pillar fundamentals, growth turning points are often imminent.

---

## Invalidation Criteria

### Bull Case (Sentiment Remains Fearful, Buy Valid) Invalidation

If the following occur simultaneously for 2+ weeks, the bullish contrarian sentiment thesis is invalidated:

- AAII Bull-Bear Spread rises above +15% (neutral turning bullish)
- NAAIM Exposure rises above 70% (managers re-leveraging)
- VIX falls below 18 (fear dissipating)
- Put/Call Ratio falls below 0.8 (complacency returning)
- MMF assets peak and decline (cash being deployed)
- SPI drops below +0.5 (exhausted fear dissipating)

**Action if Invalidated:** The capitulation has been absorbed. Sentiment is no longer providing contrarian edge. Position sizing should revert to fundamental/structural signals.

### Bear Case (Sentiment Remains Euphoric, Sell Valid) Invalidation

If the following occur simultaneously, the bearish contrarian sentiment thesis is invalidated:

- AAII Bull-Bear Spread drops below 0 (bullish extreme relieved)
- NAAIM Exposure drops below 50 (managers de-leveraging)
- VIX rises above 22 (fear returning)
- Put/Call Ratio rises above 1.0 (fear building)
- MMF assets start rising (risk-off rotation)
- SPI rises above -0.3 (euphoria exhausted)

**Action if Invalidated:** The blow-off top has rolled over. Euphoria has begun to reset. Sentiment is no longer providing contrarian edge.

---

## Additional Indicators & External Research

### The AAII Bull-Bear Anomaly

AAII Bull-Bear spread historically exhibits strong mean reversion. Robert Schiller and others have documented that sentiment extremes (top or bottom decile of historical readings) have preceded forward 12-month returns materially different from average.

**Empirical result:** AAII Bull-Bear below -20% has historically preceded 12-month returns averaging +15% or more. Above +30% has preceded returns averaging 0% to -5%.

### The VIX Mean Reversion

VIX exhibits strong mean reversion around its long-run average (~19). VIX above 30 reliably reverts within 3-6 months; VIX below 13 reliably reverts within 3-6 months.

**Trading implication:** Long vol when VIX compressed; short vol when VIX spiked. Timing depends on structural confirmation.

### The Weekly Vs. Daily Noise Problem

Weekly sentiment surveys (AAII, II, NAAIM) suffer from survey-specific noise. Individual weekly readings can be misleading. 4-week moving averages reduce noise without sacrificing signal.

**Rule:** Don't act on single-week sentiment readings. Require 4-week confirmation, or combine multiple sentiment sources.

### Barone-Adesi / Whaley VIX Modeling

VIX options pricing has known biases at extremes. VIX futures term structure provides additional information beyond VIX spot:

- **Deep contango** (front-month VIX < mid-curve): Calm regime
- **Flat** (front matches mid): Transition
- **Backwardation** (front > mid): Acute stress

### The Zweig Breadth Thrust Confirming Sentiment Turns

Zweig Breadth Thrusts (NYSE advances/declines going from <0.40 to >0.615 in 10 days) have historically coincided with sentiment turns from fear to neutral. Combining breadth thrust with sentiment capitulation signals has produced unusually strong forward returns.

### The Commitment of Traders Historical Record

COT positioning extremes (>2 standard deviations) have been reliable contrarian signals in commodities and currencies but less so in equities. In equity indices, the "smart money" label for commercials doesn't hold; CFTC category interpretation differs by contract.

### Behavioral Finance Foundations

- **Prospect Theory (Kahneman-Tversky):** Loss aversion explains asymmetric sentiment responses
- **Herding:** Individual investors cluster around recent outcomes (recency bias)
- **Representativeness:** Patterns extrapolated from small samples create sentiment feedback
- **Availability heuristic:** Sentiment responds more to memorable events than statistical patterns

These biases are what sentiment indicators measure. The framework monetizes crowd behavior that deviates from rational allocation.

### Google Trends Research

Academic research (Da, Engelberg, Gao and others) has shown that Google search volume for specific terms ("recession", "unemployment", "crash") correlates with market moves and can precede them by days to weeks.

### The VIX-SPX Correlation

VIX and SPX are negatively correlated (~-0.7 over multi-year windows). When this correlation breaks down (e.g., both falling or both rising), it signals regime shift. Typical divergences reflect structural changes in options markets or extreme positioning.

### Gamma Mechanics and SPX Pinning

Large expirations (monthly OpEx, quarterly OpEx, SPX weeklies) create "pin" levels where options gamma mathematically attracts price. SpotGamma and others publish estimated pin levels; these become magnetic short-term support/resistance.

---

## External Research Sources

**Sentiment Data:**
- [AAII Weekly Sentiment Survey](https://www.aaii.com/sentimentsurvey) - Weekly individual investor survey, Thursday release
- [Investors Intelligence](https://investorsintelligence.com/) - Weekly newsletter writer survey (subscription)
- [NAAIM Exposure Index](https://www.naaim.org/programs/naaim-exposure-index/) - Weekly active manager exposure, Wednesday release
- [CNN Fear & Greed Index](https://money.cnn.com/data/fear-and-greed/) - Daily composite (free)
- [University of Michigan Consumer Sentiment](https://data.sca.isr.umich.edu/) - Monthly, prelim mid-month, final ~25th
- [BofA Global Fund Manager Survey](https://business.bofa.com/en-us/content/global-fund-manager-survey.html) - Monthly institutional survey (summary free)
- [Sentix Indices](https://www.sentix.de/) - Global investor sentiment (premium)

**Positioning Data:**
- [CFTC Commitment of Traders](https://www.cftc.gov/MarketReports/CommitmentsofTraders/index.htm) - Weekly futures positioning, Tuesday-dated, Friday-released
- [FINRA Margin Debt](https://www.finra.org/rules-guidance/key-topics/margin-accounts) - Monthly margin statistics
- [FINRA ATS Transparency](https://www.finra.org/filing-reporting/alternative-trading-system-ats-transparency-data) - Dark pool volume
- [ICI Fund Flow Reports](https://www.ici.org/research/stats) - Weekly and monthly fund flows
- [EPFR Global](https://www.epfrglobal.com/) - Cross-border capital flows (subscription)

**Options Data:**
- [CBOE Options Volume and Sentiment](https://www.cboe.com/us/options/market_statistics/) - Daily put/call, VIX family
- [CBOE SKEW Index](https://www.cboe.com/indices/skew) - Daily tail risk index
- [SpotGamma](https://spotgamma.com/) - Dealer gamma positioning (premium)
- [SqueezeMetrics](https://squeezemetrics.com/) - Dark pool and options analytics (premium)
- [Nomura QDS](https://www.nomura.com/) - Dealer positioning research (research subscription)

**Alternative Sentiment:**
- [Google Trends](https://trends.google.com/trends/) - Search volume for sentiment-indicative terms (free)
- [Reddit WallStreetBets](https://www.reddit.com/r/wallstreetbets/) - Retail attention proxy (free but unstructured)
- [StockTwits](https://stocktwits.com/) - Tagged bullish/bearish posts (free API limited)

**Academic/Professional:**
- [SSRN Behavioral Finance](https://www.ssrn.com/) - Academic research on sentiment and markets
- [Journal of Behavioral Finance](https://www.tandfonline.com/) - Peer-reviewed research
- [NBER Behavioral Finance](https://www.nber.org/) - Working papers

---

## Reference: Published Analysis

**"Sentiment & Positioning: The Contrarian Edge"** (Educational Series, 2026) is the published article version of this pillar. Available at `research.lighthousemacro.com/p/sentiment-and-positioning-the-contrarian-216` (note Substack slug collision suffix).

The article covers:
- Why sentiment only matters at extremes
- The four-stage sentiment cycle (fear → skepticism → confidence → euphoria)
- The Sentiment-Structure Divergence (SSD) as the formal bridge to Pillar 11
- The contrarian logic: crowd positioning signals marginal liquidity, not information
- Sentiment-based sizing (not direction) for systematic positioning
- The specific signal combinations that have historically identified capitulation lows and blow-off tops

The article positions sentiment as the contrarian edge that sizes and times trades identified through fundamental and structural analysis. Sentiment alone is not a trade; combined with aligned fundamentals and structure, it's the high-conviction configuration.

---

## Historical Validation

### Pattern Recognition

| **Episode** | **SPI** | **SSD** | **Key Signal** | **Outcome** |
|---|---|---|---|---|
| **Oct 2002** | +2.1 | +1.8 | AAII <-25, VIX 45, full capitulation | Bear market low; forward 12M +33% |
| **Oct 2008** | +2.5 | +2.0 | VIX 80, AAII <-50, max fear | Deeper leg then bottom March 2009 |
| **March 2009** | +2.3 | +2.5 | AAII <-50, II bears >60%, margin debt collapsed | Generational low |
| **Aug 2015** | +1.4 | +0.9 | VIX spike, AAII bearish surge | V-bottom on Fed dovish |
| **Jan-Feb 2016** | +1.8 | +1.5 | Oil capitulation, EM stress, broad fear | Feb 2016 low; +20%+ rally |
| **Dec 2018** | +1.9 | +1.5 | NAAIM <25, AAII capitulation, VIX 36 | V-bottom on Powell pivot |
| **March 2020** | +2.2 | +2.0 | VIX 82, AAII <-45, full capitulation | COVID bottom |
| **Oct 2022** | +1.7 | +1.4 | AAII 56% bears (record), margin debt collapse | Cycle low |
| **Jan 2000** | -1.9 | -1.7 | AAII 75% bulls, Margin debt peak, retail mania | Tech top |
| **Dec 2021** | -1.6 | -1.5 | NAAIM >95, extreme call buying, meme mania | Cycle peak |

### False Signals

**Late 2015 - early 2016:** Multiple AAII bearish extremes didn't immediately resolve to durable low. The capitulation process took 6+ months of choppy sideways action before the February 2016 low. Lesson: sentiment extremes mean mean-reversion is likely but timing is variable.

**April-May 2022:** Bearish sentiment readings during the bear market were "relief rally" triggers but not structural bottoms. Bear markets produce multiple contrarian signals; confirmation through structure (MSI > -0.5 sustained) is required for durable bottom.

**Late 2021:** Euphoria indicators peaked but markets continued rising into January 2022. Top signals can be early by weeks to months. Position sizing should reflect probability of continuation; don't short euphoric markets without structural confirmation.

### Structural Breaks

**Post-2018 0DTE Options Growth:** Zero-day-to-expiry options have changed intraday sentiment dynamics. Daily put/call ratios now include 0DTE distortions that don't reflect multi-day sentiment. Focus on 10-day averages or equity-only metrics to reduce 0DTE noise.

**Post-2020 Retail Surge:** COVID-era retail investor growth (Robinhood, IBKR, Fidelity zero-commission) materially affected retail sentiment signals. Meme stock episodes, gamma squeezes, and coordinated buying changed classical sentiment relationships.

**Post-2022 Crypto Integration:** Cryptocurrency has become a retail sentiment proxy. BTC price action correlates with retail risk appetite. BTC rallying while equities fall signals retail risk rotation rather than structural regime change.

**Rise of Systematic Strategies:** CTAs, risk parity, and volatility-targeting strategies have grown to meaningful AUM. Their mechanical responses to sentiment signals (vol spikes trigger de-risking) have become self-reinforcing dynamics that amplify short-term vol clusters.

---

## Alternative & High-Frequency Data

| **Source** | **Indicator** | **Frequency** | **Access** | **Use Case** |
|---|---|---|---|---|
| **AAII** | Bull/Bear Survey | Weekly (Thu) | Free | Primary retail sentiment |
| **Investors Intelligence** | Newsletter Sentiment | Weekly | Subscription | Professional sentiment |
| **NAAIM** | Exposure Index | Weekly (Wed) | Free summary | Active manager positioning |
| **BofA** | Global Fund Manager Survey | Monthly | Free summary | Institutional positioning |
| **CNN** | Fear & Greed Index | Daily | Free | Multi-factor composite |
| **CFTC** | Commitment of Traders | Weekly | Free | Futures positioning |
| **CBOE** | Put/Call, VIX family, SKEW | Daily | Free | Options sentiment |
| **SpotGamma** | Dealer gamma | Daily | Subscription | Options positioning |
| **SqueezeMetrics** | Dark pool index | Daily | Subscription | Institutional activity |
| **FINRA** | Margin Debt, ATS | Monthly, Daily | Free | Leverage, dark pool |
| **ICI** | Fund Flows | Weekly/Monthly | Free | Capital movement |
| **EPFR Global** | Cross-border flows | Weekly | Subscription | Global flow data |
| **Google Trends** | Keyword search | Daily | Free | Alternative sentiment |
| **Reddit / WSB** | Mention volume | Real-time | Free / API | Retail attention |
| **Sentix** | Global indices | Monthly | Subscription | International sentiment |
| **Nomura QDS** | Dealer positioning | Daily | Subscription | Gamma estimates |
| **SqueezeMetrics DIX** | Dark pool activity | Daily | Subscription | Institutional flow |
| **ASFP data** | Hedge fund leverage | Quarterly | Fed publication | Sector leverage |

---

## Academic & Research Foundation

| **Paper/Framework** | **Author(s)** | **Key Insight** |
|---|---|---|
| "Prospect Theory" (1979) | Kahneman & Tversky | Loss aversion; asymmetric response to gains vs losses |
| "Investor Sentiment and the Cross-Section of Stock Returns" (2006) | Baker & Wurgler | Sentiment drives cross-sectional returns |
| "Investor Sentiment" (2007) | Baker & Wurgler | Sentiment index methodology |
| "Noise Trader Risk in Financial Markets" (1990) | DeLong, Shleifer, Summers, Waldmann | Rational traders can't arbitrage sentiment fully |
| "Herd Behavior in Financial Markets" (2001) | Bikhchandani & Sharma | Information cascades drive sentiment extremes |
| "The Limits of Arbitrage" (1997) | Shleifer & Vishny | Mispricings persist because arbitrageurs are constrained |
| "Bubbles, Financial Crises, and Systemic Risk" (2013) | Brunnermeier & Oehmke | Feedback between sentiment and fundamentals |
| "In Search of Attention" (2011) | Da, Engelberg, Gao | Google search volume predicts returns |
| "Investor Attention and Stock Market Volatility" (2014) | Andrei & Hasler | Attention affects volatility patterns |
| "Fear and the Stock Market" | Baker, Wurgler | Fear-indexed sentiment measures |
| "Dividend Yield Strategy: A Theory of Choice" | Various | Income-seeking behavior during stress |
| "VIX and the Sentiment Bubble" | Various market microstructure research | VIX as sentiment proxy |
| CBOE research on Put/Call, SKEW | CBOE historical research | Options-based sentiment |
| "Behavioral Risk Premium" (various) | Multiple researchers | Risk premium components include sentiment |

---

## FRED Series Reference Appendix

Most Pillar 12 data is not on FRED because surveys are published by private organizations. The following are available or have FRED proxies:

### Available on FRED

| **Series ID** | **Description** | **Frequency** |
|---|---|---|
| UMCSENT | University of Michigan Consumer Sentiment | Monthly |
| VIXCLS | CBOE Volatility Index (VIX) | Daily |
| VXNCLS | CBOE NASDAQ-100 Volatility | Daily |
| MICH | UMich 1-Year Inflation Expectations | Monthly |
| STLFSI4 | St. Louis Fed Financial Stress Index | Weekly |

### Non-FRED Sources (Primary for this Pillar)

| **Indicator** | **Source** | **Notes** |
|---|---|---|
| AAII Bull-Bear | AAII | Weekly, free; access via aaii.com/sentimentsurvey |
| Investors Intelligence | II | Weekly, subscription required |
| NAAIM Exposure Index | NAAIM | Weekly, free summary |
| BofA GFMS | BofA Institute | Monthly, free summaries; full survey subscription |
| CFTC COT Report | CFTC | Weekly, free |
| CBOE Put/Call Ratios | CBOE | Daily, free |
| CBOE SKEW | CBOE | Daily, free |
| VIX Term Structure (VIX9D, VIX3M, VIX6M, VVIX) | CBOE | Daily, free |
| CNN Fear & Greed | CNN | Daily, free |
| ICI Fund Flows | ICI | Weekly/monthly, free |
| FINRA Margin Debt | FINRA | Monthly, free |
| FINRA ATS Transparency | FINRA | Daily, free |
| EPFR Cross-Border Flows | EPFR Global | Weekly, subscription |
| SpotGamma Dealer Gamma | SpotGamma | Daily, subscription |
| Nomura QDS Dealer Positioning | Nomura | Daily, research subscription |
| Sentix Global Indices | Sentix | Monthly, subscription |
| Google Trends Keyword Data | Google | Daily, free |
| Reddit WSB Mention Data | Reddit/third parties | Real-time, free via API |
| StockTwits Tagged Posts | StockTwits | Real-time, limited free API |
| BTC Price and Volume | Multiple exchanges | Daily/intraday, free |
| 0DTE Options Volume | CBOE | Daily, free |

---

*Bob Sheehan, CFA, CMT*
*Founder & CIO, Lighthouse Macro*
*Last Updated: February 2026*

*That's how we read the crowd from the Watch. The market is a voting machine in the short term, and the crowd always votes last.*
