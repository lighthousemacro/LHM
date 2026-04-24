# PILLAR 12: SENTIMENT & POSITIONING

## The Sentiment Transmission Chain

Sentiment isn't noise. It's the crowd's positioning expressed through surveys, options, and flows. And the crowd is a source of liquidity, not information.

```
Fear → Underexposure → Forced Buying →
Price Rise → Confidence → Overexposure →
Complacency → Forced Selling → Fear (Cycle)
```

**The Insight:** Sentiment is a contrarian indicator. Extreme fear = buy. Extreme greed = sell. The crowd isn't wrong because they're stupid—they're wrong because they're late. By the time everyone is bullish, they've already bought. By the time everyone is bearish, they've already sold. The marginal buyer/seller is always on the other side of consensus.

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

**The Extreme Edge:** Sentiment only matters at extremes. In the middle, it's noise. We don't trade sentiment—we use sentiment to size and time trades identified by fundamentals and structure.

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

**The SSD Signal:** SSD > +1.5 = the crowd has capitulated while structure is weak—classic bottom formation. SSD < -1.5 = the crowd is euphoric while structure is strong—classic blow-off top formation.

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

Sentiment doesn't determine direction—fundamentals and structure do. Sentiment determines *how much* and *when*.

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
6. **SPI > +1.0** (fear elevated—contrarian edge present)

Without elevated fear, there's no contrarian edge to exploit. Don't bottom-fish without sentiment support.

---

## Current State Template

**NOTE:** Fill in current values from live data sources. Do not reference any pre-filled values as current—they are outdated.

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

*That's how we read the crowd from the Watch. The market is a voting machine in the short term—and the crowd always votes last.*
