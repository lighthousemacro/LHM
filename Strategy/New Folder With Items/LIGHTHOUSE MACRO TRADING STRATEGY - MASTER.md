# LIGHTHOUSE MACRO TRADING STRATEGY
## Complete Framework for Multi-Asset Macro Execution

**Version:** 2.0 (The Diagnostic Dozen)
**Date:** January 19, 2026
**Author:** Bob Sheehan, CFA, CMT
**Status:** Production-Ready

*"MACRO, ILLUMINATED."*

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Investment Philosophy](#i-investment-philosophy)
3. [The Macro Foundation: Connecting to the 12 Pillars](#ii-the-macro-foundation-connecting-to-the-12-pillars)
4. [The Three-Engine Analytical Framework](#iii-the-three-engine-analytical-framework)
5. [Proprietary Indicators](#iv-proprietary-indicators)
6. [Position Sizing & Conviction Framework](#v-position-sizing--conviction-framework)
7. [The Perfect Setup: Anatomical Breakdown](#vi-the-perfect-setup-anatomical-breakdown)
8. [Absolute Rules: Non-Negotiable Filters](#vii-absolute-rules-non-negotiable-filters)
9. [Asset Class Framework & Implementation](#viii-asset-class-framework--implementation)
10. [Tactical Timeframe Optimization](#ix-tactical-timeframe-optimization)
11. [Risk Management Framework](#x-risk-management-framework)
12. [Implementation Workflow](#xi-implementation-workflow)
13. [Crypto-Specific Considerations](#xii-crypto-specific-considerations)
14. [Current Regime Assessment](#xiii-current-regime-assessment)

---

## Executive Summary

Lighthouse Macro's trading strategy combines **systematic regime identification** with **disciplined position sizing** to generate alpha at macro inflection points. We don't predict—we measure. We don't diversify for safety—we concentrate when conviction is high.

### Core Differentiation

| **Attribute** | **Lighthouse Approach** | **Consensus Approach** |
|---------------|-------------------------|------------------------|
| **Signal Source** | 12 Macro Pillars → Proprietary Indicators | Headlines, lagging data |
| **Position Sizing** | Conviction-weighted (7-20% per position) | Equal-weighted |
| **Concentration** | 3-5 high-conviction bets | 30+ marginal positions |
| **Cash Treatment** | Active position (30-100% valid) | Residual drag |
| **Risk Framework** | Dual stops (thesis + price) | Single trailing stop |
| **Timeframe** | 3-6 month tactical core | Arbitrary calendar |

### The Edge

**Flows > Stocks.** We measure labor market deterioration 6-9 months before unemployment rises. We track Fed plumbing stress before funding markets break. We identify credit complacency before spreads widen. We see structure break before fundamentals confirm. By the time everyone knows, it's too late. That's the window where we operate.

**Current MRI: +1.1 (HIGH RISK)** → Defensive positioning warranted.

---

## I. Investment Philosophy

### Regime-Based Concentration

**Core Principles:**

**1. Regimes Matter More Than Assets**

Asset class returns are regime-dependent. A bull market in equities under abundant liquidity (LCI > 0) behaves fundamentally differently than a bull market under scarce liquidity (LCI < -0.5). Identifying regime shifts earlier = alpha generation.

**2. Position Sizing is Alpha**

Risk management matters more than instrument selection. The difference between 7% and 20% position sizing on a correct call is the difference between marginal and exceptional performance. Bet size reflects signal strength, not equal-weighting.

**3. Simplicity Over Complexity**

Implement with liquid instruments (ETFs, futures, spot). Avoid exotic structures for complexity's sake. Most blowups start with options leverage; we prefer simple execution with proper sizing.

**4. Dual Risk Framework**

Every position has two invalidation criteria:
- **Thesis-based stops:** Fundamental regime change (e.g., LFI drops below 0.5)
- **Price-based stops:** Technical structure breaks (e.g., 50d MA < 200d MA)

Use whichever triggers first. Preserve capital.

**5. Flows > Stocks**

Leading indicators (quits rate, RRP flows, funding spreads) > lagging indicators (unemployment, GDP). Position ahead of data confirmation. The "Honest Signal" is always in the flows.

---

## II. The Macro Foundation: Connecting to the 12 Pillars

Our trading framework doesn't exist in isolation. It's the **execution layer** of the 12 Macro Pillars (The Diagnostic Dozen). Every position traces back to a pillar signal.

### The Three-Engine Framework

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              12 MACRO PILLARS                                    │
│                          (The Diagnostic Dozen)                                  │
├───────────────────────┬─────────────────────────┬───────────────────────────────┤
│   MACRO DYNAMICS      │   MONETARY MECHANICS    │      MARKET STRUCTURE         │
│   (Pillars 1-7)       │   (Pillars 8-10)        │      (Pillars 11-12)          │
├───────────────────────┼─────────────────────────┼───────────────────────────────┤
│ 1. Labor    → LPI,LFI │ 8. Government → GCI-Gov │ 11. Structure → MSI, SBD      │
│ 2. Prices   → PCI     │ 9. Financial  → FCI,CLG │ 12. Sentiment → SPI, SSD      │
│ 3. Growth   → GCI     │ 10. Plumbing  → LCI     │                               │
│ 4. Housing  → HCI     │                         │                               │
│ 5. Consumer → CCI     │                         │                               │
│ 6. Business → BCI     │                         │                               │
│ 7. Trade    → TCI     │                         │                               │
└───────────────────────┴─────────────────────────┴───────────────────────────────┘
                                       ↓
                               MRI (Master Composite)
                                       ↓
                           TRADING STRATEGY EXECUTION
```

### Pillar-to-Trade Mapping

| **Pillar Signal** | **Trading Expression** | **Asset Class** |
|-------------------|------------------------|-----------------|
| LFI > +0.8 | Reduce cyclical equity exposure | Equities |
| LCI < -0.5 | Reduce gross exposure, add cash | All |
| CLG < -1.0 | Add credit protection (HY short) | Credit |
| PCI > +1.0 | Short duration, inflation hedges | Rates |
| GCI-Gov > +1.0 | Steepener trades, term premium | Rates |
| BCI < -0.5 | Underweight small caps vs large | Equities |
| HCI < -0.5 | Avoid homebuilders, housing-sensitive | Equities |
| MSI < -0.5 | Reduce gross exposure | All |
| SPI > +1.5 | Contrarian fade (crowding risk) | All |

### Current Pillar State (January 2026)

| **Pillar** | **Composite** | **Trading Signal** |
|------------|---------------|-------------------|
| Labor | LFI +0.93 | ⚠️ Reduce cyclicals |
| Prices | PCI +0.7 | ⚠️ Fed constrained |
| Growth | GCI -0.4 | ⚠️ Manufacturing weak |
| Housing | HCI -0.6 | 🔴 Avoid sector |
| Consumer | CCI -0.3 | ⚠️ Credit stress building |
| Business | BCI -0.4 | ⚠️ Small biz weak |
| Trade | TCI -0.5 | ⚠️ Dollar headwind |
| Government | GCI-Gov +1.1 | 🔴 Fiscal dominance |
| Financial | FCI +0.3 | ⚠️ Spreads too tight |
| Plumbing | LCI -0.8 | 🔴 Buffer exhausted |
| Structure | MSI [Live] | Monitor for breadth divergence |
| Sentiment | SPI [Live] | Monitor for crowding extremes |

**MRI: +1.1 = HIGH RISK REGIME**

---

## III. The Three-Engine Analytical Framework

Every trade must pass through the integrated three-engine framework. Single-engine signals are insufficient; we require **convergence across engines** for high-conviction positioning.

### Engine 1: Macro Dynamics (Pillars 1-7)

**Focus:** Labor, Prices, Growth, Housing, Consumer, Business, Trade

**Key Insight:** Flows precede stocks. Labor market deterioration shows up in quits rate and hires/quits ratio 6-9 months before unemployment rises. The transmission chain runs: Labor → Income → Spending → Profits.

**Primary Indicators:**

| **Indicator** | **Threshold** | **Current** | **Signal** |
|---------------|---------------|-------------|------------|
| Quits Rate | < 2.0% = Pre-recessionary | 1.9% | 🔴 Breach |
| Long-Term Unemployed | > 22% = Fragility | 25.7% | 🔴 Breach |
| Hires/Quits Ratio | < 2.0 = Demand weakening | 1.85 | 🔴 Breach |
| Temp Help YoY | < -3% = Recession signal | -7.1% | 🔴 Breach |
| Core PCE | > 2.5% = Elevated | 3.2% | 🔴 Above target |
| ISM Manufacturing | < 48 = Recession | 49.3 | ⚠️ Contraction |

**LFI Current: +0.93** (Elevated fragility—defensive signal)

### Engine 2: Monetary Mechanics (Pillars 8-10)

**Focus:** Government (Fiscal), Financial (Credit/Conditions), Plumbing (Liquidity)

**Key Insight:** RRP exhaustion removes the system's shock absorber. Treasury issuance now drains reserves directly. We've entered Fiscal Dominance—the regime where fiscal policy overwhelms monetary policy.

**Primary Indicators:**

| **Indicator** | **Threshold** | **Current** | **Signal** |
|---------------|---------------|-------------|------------|
| RRP Balance | < $200B = Buffer gone | $150B | 🔴 Drained |
| Reserves vs LCLOR | < $300B = Scarcity | $300B | ⚠️ At limit |
| EFFR-IORB Spread | > +8 bps = Stress | +3 bps | 🟢 OK |
| SOFR-IORB Spread | > +10 bps = Funding stress | +5 bps | 🟡 Elevated |
| Deficit/GDP | > 5% = Elevated | 7.2% | 🔴 Wartime levels |
| Term Premium | > +50 bps = Repricing | +25 bps | ⚠️ Rising |

**LCI Current: -0.8** (Scarce liquidity—monitor funding stress)

### Engine 3: Market Technicals (Broad Market Diagnostics)

**Focus:** Breadth, internals, volatility regime, cross-asset correlations

**Key Insight:** This is the health check on the *environment*, not the individual position. Breadth measures reveal internal market health that headline indices obscure. When the S&P 500 makes new highs but only 40% of stocks are above their 50d MA, the generals are marching without the troops. You can have a perfect setup on an individual asset, but if the broad market is deteriorating underneath, the tide will eventually pull everything down.

**Breadth Diagnostics & Conditional Forward Returns:**

We track breadth metrics and then ask: given where we are *now*, what do forward returns historically look like? The current reading frames the conditional.

| **Diagnostic** | **Current Reading** | **Condition** | **Forward Returns (Historical)** |
|----------------|---------------------|---------------|----------------------------------|
| % Stocks > 20d MA | [Live] | < 30% (washed out) | Next 20d: +2.1% avg, 68% win rate |
| | | > 80% (crowded) | Next 20d: +0.3% avg, 52% win rate |
| % Stocks > 50d MA | [Live] | < 35% (washed out) | Next 63d: +4.8% avg, 71% win rate |
| | | > 85% (crowded) | Next 63d: +1.2% avg, 55% win rate |
| % Stocks > 200d MA | [Live] | < 45% (bear regime) | Next 126d: bifurcated—either recovery or acceleration |
| | | > 75% (bull regime) | Next 126d: +6.2% avg, but elevated drawdown risk |
| % Stocks at 63d High | [Live] | < 3% (no leadership) | Next 20d: watch for breadth thrust or continued deterioration |
| | | > 20% (broad breakout) | Next 63d: momentum tends to persist |
| % Stocks at 63d Low | [Live] | > 20% (capitulation) | Next 20d: mean reversion probable, +2.8% avg |
| | | < 2% (complacent) | Next 20d: low vol drift, but vulnerable to shock |
| New Highs - New Lows | [Live] | < -300 for 3+ days | Next 20d: oversold bounce typical |
| | | > +300 for 5+ days | Next 63d: breadth thrust, historically bullish |
| SPX Drawdown | [Live] | Down >5% over 10d | Next 20d: mean reversion +1.9% avg |
| | | Down >10% over 20d | Next 63d: +5.4% avg, but wide distribution |

*Note: Historical returns are illustrative baselines from backtesting. Actual figures updated in production dashboards.*

**The Framework:**
```
1. Observe current breadth reading
2. Look up historical forward returns for that condition
3. Calibrate aggression accordingly
```

This isn't prediction—it's base rates. If % stocks > 50d MA is at 28% right now, history says forward 63-day returns average +4.8% with 71% win rate. Doesn't mean it *will* rally, but the odds favor leaning in. We use this to size positions and set expectations, not to make binary bets.

**Volatility & Positioning:**

| **Indicator** | **Threshold** | **Current** | **Signal** |
|---------------|---------------|-------------|------------|
| VIX | < 15 = Complacent, > 25 = Fear | ~18 | ⚠️ Elevated |
| VIX Term Structure | Contango = Calm, Backwardation = Fear | Contango | 🟢 OK |
| HY OAS | < 300 bps = Complacent | 290 bps | 🔴 Too tight |
| Equity-Bond Correlation | > +0.3 = Diversification breaking | Rising | ⚠️ Watch |

**Diagnostic Use Case:** Breadth divergences often lead price by 2-4 weeks. Conditional return analysis helps calibrate *how much* to lean into or against the current setup. When indices are rising but breadth is deteriorating, reduce position sizes and tighten stops—the foundation is cracking even if the roof looks fine.

---

### Position-Level Technicals (The Actual Trade)

**Focus:** The specific asset's trend, momentum, structure, and relative strength

**Key Insight:** This is completely separate from broad market diagnostics. Engine 3 tells you *whether* to be aggressive or defensive. Position-level technicals tell you *what* to buy and *when* to buy it. A stock can be in a perfect uptrend while the broad market is deteriorating (defensive sector, relative strength leader) or vice versa (cyclical garbage rallying into a weakening tape).

**The 3-Panel Chart:**

| **Panel** | **What It Shows** | **Decision** |
|-----------|-------------------|--------------|
| **Panel 1: Price & Trend** | Price, 50d MA, 200d MA | Is the trend intact? |
| **Panel 2: Relative Strength** | Asset/Benchmark ratio with 63d & 252d MAs | Is it outperforming? |
| **Panel 3: Momentum (Z-RoC)** | Z-scored rate of change | Is momentum confirming? |

**Position-Level Checklist (Before Any Entry):**

| **Element** | **Requirement** | **Fail = No Trade** |
|-------------|-----------------|---------------------|
| Price vs 200d MA | Price > 200d MA | ❌ Absolute Rule #1 |
| 50d vs 200d MA | 50d > 200d (no death cross) | ❌ Absolute Rule #2 |
| MA Direction | Both MAs rising (not flat/declining) | ⚠️ Reduced conviction |
| Relative Strength | Green panel (outperforming benchmark) | ❌ Absolute Rule #3 |
| Z-RoC | > -1.0 (momentum not broken) | ❌ Exit signal if held |
| Extension | Within 15% of 50d MA | ❌ Absolute Rule #5 |

**The Interaction:**

```
BROAD MARKET (Engine 3)          POSITION TECHNICALS
        ↓                                ↓
   Environment                     Specific Setup
        ↓                                ↓
  "Should I be aggressive       "Is THIS asset ready
   or defensive overall?"         to buy right now?"
        ↓                                ↓
   Regime Multiplier             Conviction Score
        ↓                                ↓
        └──────────────┬─────────────────┘
                       ↓
               POSITION SIZE
```

**Example:** Broad market breadth is deteriorating (Engine 3 = Warning), but XLV (Healthcare) is in a perfect uptrend with rising relative strength (Position Technicals = Strong). You still take the trade, but the deteriorating environment reduces your regime multiplier. A Tier 1 setup that would get 20% in a healthy tape gets 12% in a deteriorating one.

---

## IV. Proprietary Indicators

### Macro Risk Index (MRI) v2.0 — Master Composite

The MRI synthesizes all 12 pillar composites into a single regime indicator:

```
MRI = 0.12 × (-LPI)           # Labor (inverted)
    + 0.08 × PCI              # Prices
    + 0.12 × (-GCI)           # Growth (inverted)
    + 0.06 × (-HCI)           # Housing (inverted)
    + 0.08 × (-CCI)           # Consumer (inverted)
    + 0.08 × (-BCI)           # Business (inverted)
    + 0.05 × (-TCI)           # Trade (inverted)
    + 0.10 × GCI_Gov          # Government
    + 0.05 × (-FCI)           # Financial (inverted)
    + 0.10 × (-LCI)           # Plumbing (inverted)
    + 0.08 × (-MSI)           # Market Structure (inverted)
    + 0.08 × SPI              # Sentiment (high = contrarian risk)
```

**v2.0 Change:** Added Pillars 11-12 (Structure, Sentiment) with 8% weight each, rebalanced other pillars accordingly.

**Signal Thresholds:**

| **MRI Range** | **Regime** | **Equity Allocation** | **Regime Multiplier** |
|---------------|------------|----------------------|----------------------|
| < -0.5 | Low Risk | 65-70% | 1.2x |
| -0.5 to +0.5 | Neutral | 55-60% | 1.0x |
| +0.5 to +1.0 | Elevated | 45-55% | 0.6x |
| +1.0 to +1.5 | High Risk | 35-45% | 0.3x |
| > +1.5 | Crisis | 25-35% | 0.0x (cash) |

**Current MRI: +1.1 → HIGH RISK → Regime Multiplier: 0.3x**

### Labor Fragility Index (LFI)

```
LFI = 0.30 × z(Long_Term_Unemployed_Share)
    + 0.25 × z(-Quits_Rate)                    # Inverted
    + 0.20 × z(-Hires_Quits_Ratio)             # Inverted
    + 0.15 × z(-Temp_Help_YoY)                 # Inverted
    + 0.10 × z(-Job_Hopper_Premium)            # Inverted
```

| **LFI Range** | **Regime** | **Action** |
|---------------|-----------|------------|
| < 0.0 | Healthy | Full cyclical exposure |
| 0.0 to +0.5 | Neutral | Strategic allocation |
| +0.5 to +1.0 | Elevated | Reduce cyclicals, add defensives |
| +1.0 to +1.5 | High | Defensive posture |
| > +1.5 | Critical | Maximum defense |

**Current LFI: +0.93** → Elevated → Defensive signal

### Liquidity Cushion Index (LCI)

```
LCI = 0.25 × z(Reserves_vs_LCLOR)
    + 0.20 × z(-EFFR_IORB_Spread)
    + 0.15 × z(-SOFR_IORB_Spread)
    + 0.15 × z(RRP_Balance)
    + 0.10 × z(-GCF_TPR_Spread)
    + 0.10 × z(-Dealer_Net_Position)
    + 0.05 × z(-EUR_USD_Basis)
```

| **LCI Range** | **Regime** | **Action** |
|---------------|-----------|------------|
| > +1.0 | Abundant | Full risk allocation |
| +0.5 to +1.0 | Ample | Normal positioning |
| -0.5 to +0.5 | Tight | Reduced leverage |
| -1.0 to -0.5 | Scarce | Elevated caution |
| < -1.0 | Crisis | Cash priority |

**Current LCI: -0.8** → Scarce → Elevated caution

### Credit-Labor Gap (CLG)

```
CLG = z(HY_OAS) - z(LFI)
```

| **CLG Range** | **Interpretation** | **Action** |
|---------------|--------------------|------------|
| > +1.0 | Credit pricing in stress labor doesn't show | Potential buying opportunity |
| -1.0 to +1.0 | Aligned | No spread trade |
| < -1.0 | Credit ignoring labor reality | Add credit hedges |

**Current CLG: -1.2** → Credit complacent → Add credit protection

### Market Structure Index (MSI) — NEW in v2.0

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

| **MSI Range** | **Regime** | **Action** |
|---------------|-----------|------------|
| > +1.0 | Healthy Structure | Full allocation |
| +0.5 to +1.0 | Constructive | Standard allocation |
| -0.5 to +0.5 | Mixed | Monitor divergences |
| -1.0 to -0.5 | Deteriorating | Reduce exposure |
| < -1.0 | Broken | Defensive positioning |

### Sentiment Pillar Index (SPI) — NEW in v2.0

```
SPI = 0.20 × z(AAII_Bull_Bear_Spread)
    + 0.15 × z(Put_Call_Ratio_Inverted)
    + 0.15 × z(VIX_vs_Realized_Vol)
    + 0.15 × z(Fund_Flows_Equity)
    + 0.15 × z(CNN_Fear_Greed)
    + 0.10 × z(NAAIM_Exposure)
    + 0.10 × z(Options_Skew)
```

| **SPI Range** | **Regime** | **Signal** |
|---------------|-----------|------------|
| > +1.5 | Extreme Greed | Contrarian bearish |
| +0.5 to +1.5 | Optimistic | Caution |
| -0.5 to +0.5 | Neutral | No signal |
| -1.5 to -0.5 | Pessimistic | Accumulation zone |
| < -1.5 | Extreme Fear | Contrarian bullish |

---

## V. Position Sizing & Conviction Framework

### The Regime-Conviction-Size Formula

```
Position Size = Regime_Multiplier × Conviction_Weight × Liquidity_Adjustment
```

**Components:**

1. **Regime Multiplier** (0.0x to 1.2x): Set by MRI
2. **Conviction Weight** (0% to 20%): Set by Conviction Tier
3. **Liquidity Adjustment** (0.5x to 1.0x): Asset-specific

### Conviction Scoring System

**Total Possible: 19 points**
- Technical Score: 0-9 pts
- Fundamental Score: 0-5 pts
- Microstructure Score: 0-5 pts

#### Technical Score Components (0-9 pts)

**1. Primary Trend (0-2 pts)**

| **Condition** | **Score** |
|---------------|-----------|
| Price > 50d > 200d, both MAs rising | 2 pts |
| Price > 50d > 200d, MAs flat/declining | 1 pt |
| Price > 50d BUT 50d < 200d | 0.5 pts |
| Price < 50d | 0 pts (disqualified) |

**2. Momentum Quality — Context Aware (0-2 pts)**

*In Uptrend (Price > 50d > 200d):*

| **Z-RoC Range** | **Score** | **Interpretation** |
|-----------------|-----------|-------------------|
| > +1.0 | 2 pts | Strong momentum confirmed |
| 0 to +1.0 | 1 pt | Building momentum |
| -1.0 to 0 | 0 pts | Cooling, acceptable if at support |
| < -1.0 | -2 pts | Breakdown, override to exit |

**Critical Insight:** Overbought in uptrend = STRENGTH. Overbought in downtrend = EXHAUSTION. Context is everything.

**3. Structure Confluence (0-1 pt)**

| **Condition** | **Score** |
|---------------|-----------|
| Price at rising 50d MA (support) | +1 pt |
| Price at resistance | -1 pt |
| Price in no-man's-land | 0 pts |

**4. Extension Filter (0-1 pt)**

| **Distance from 50d MA** | **Score** |
|--------------------------|-----------|
| -8% to -12% (pullback entry) | +1 pt |
| ±3% (near MA) | +0.5 pts |
| 0% to +8% | 0 pts |
| > +15% | Do not enter |

**5. Relative Strength (0-1 pt)**

| **Condition** | **Score** |
|---------------|-----------|
| Green panel (relative uptrend) | +1 pt |
| Gray panel (transitional) | 0 pts |
| Red/Magenta panel | Disqualified |

**6. Perfect Setup Bonus (0-2 pts)**

When all six Perfect Setup elements align (see Section VI), award bonus:
- 5-6 elements: +2 pts
- 3-4 elements: +1 pt
- < 3 elements: 0 pts

#### Fundamental Score (0-5 pts)

| **Component** | **Points** |
|---------------|------------|
| On-chain/Earnings Health | 0-2 pts |
| Valuation Positioning | 0-2 pts |
| Narrative/Catalyst | 0-1 pt |

#### Microstructure Score (0-5 pts)

| **Component** | **Points** |
|---------------|------------|
| Positioning/Liquidation Asymmetry | 0-2 pts |
| Funding/Carry Regime | 0-2 pts |
| Holder/Flow Distribution | 0-1 pt |

### Conviction Tiers

| **Tier** | **Score Range** | **Conviction Weight** | **Description** |
|----------|-----------------|----------------------|-----------------|
| Tier 1 | 16-19 pts | 20% | Perfect or near-perfect setup |
| Tier 2 | 12-15 pts | 12% | Strong setup, one pillar weaker |
| Tier 3 | 8-11 pts | 7% | Marginal setup, mixed signals |
| Tier 4 | < 8 pts | 0% | Insufficient conviction, avoid |

### Position Size Examples by Regime

**High Conviction Setup (Tier 1, Score 17) in Different Regimes:**

| **Regime** | **MRI** | **Multiplier** | **Conviction** | **Size** |
|------------|---------|----------------|----------------|----------|
| Low Risk | -0.6 | 1.2x | 20% | 24% |
| Neutral | +0.3 | 1.0x | 20% | 20% |
| Elevated | +0.8 | 0.6x | 20% | 12% |
| High Risk | +1.2 | 0.3x | 20% | 6% |
| Crisis | +1.8 | 0.0x | 20% | 0% (cash) |

**Current Regime (MRI +1.1):**
- Tier 1 (20% base) → 20% × 0.3 = **6% maximum position**
- Tier 2 (12% base) → 12% × 0.3 = **3.6% maximum position**
- Tier 3 (7% base) → 7% × 0.3 = **2.1% maximum position**

---

## VI. The Perfect Setup: Anatomical Breakdown

The Perfect Setup is the **only configuration** that justifies maximum position sizing. Everything else is partial position or pass.

### The Six-Element Configuration

**Element 1: Primary Trend Structure**
- Price > 50d MA
- 50d MA > 200d MA
- **Both MAs rising** (not just aligned, but ascending)
- Non-negotiable. Flat or declining MAs = skip.

**Element 2: Relative Trend Alignment**
- Asset outperforming benchmark (Panel 2 = Green)
- Relative price > Relative 63d MA > Relative 252d MA
- No exceptions. Relative downtrend = not interested.

**Element 3: Consolidation Pattern**
- **Sideways price action** for 10-30 days after prior uptrend leg
- **Volatility compression** (ATR declining during consolidation)
- Price oscillating around rising 50d MA but not breaking below
- Volume declining during consolidation (lack of distribution)

**Element 4: Momentum Behavior During Consolidation**
- Z-RoC was strong (+1.0 to +2.0) leading into consolidation
- Z-RoC cooled to -0.5 to +0.5 during consolidation
- **Key:** Momentum dissipated but didn't collapse (never hit -1.0)
- **Interpretation:** Buyers took a breather. Sellers didn't show up.

**Element 5: Breakout Trigger**
- Price breaks above consolidation range
- Z-RoC crosses back above 0 (momentum resuming)
- Ideally bouncing off or near rising 50d MA
- Volume expansion on breakout (commitment signal)

**Element 6: Macro Regime Confirmation**
- MRI not in Crisis territory (< +1.5)
- LCI not critically scarce (> -1.0)
- No acute funding stress signals

### Visual Recognition

```
Price Action (Top Panel):
  - Rising blue 200d MA (steady upward slope)
  - Rising red 50d MA (steeper slope than 200d)
  - Price consolidating horizontally around 50d MA for 2-3 weeks
  - Then: Price breaks up, 50d continues rising

Relative Strength (Middle Panel):
  - Filled GREEN throughout
  - Relative price oscillating but staying above both relative MAs
  - No breakdown signals

Z-RoC Momentum (Bottom Panel):
  - Came from +1.5 range (prior leg up)
  - Cooled to +0.2 during consolidation (buyers rested)
  - Never dropped below -0.5 (sellers didn't take control)
  - Now turning back up through 0 (momentum resuming)
```

**This is the only setup we truly load up on.**

---

## VII. Absolute Rules: Non-Negotiable Filters

Before any trade consideration, these filters must pass. If any fail, the trade doesn't happen.

### Rule 1: Never Own Below 200d MA

**Logic:** Below 200d = long-term downtrend or broken structure

**No Exceptions:** Not for "value," not for "oversold," not for "turnaround story"

**Why:** Statistical edge evaporates in long-term downtrends

### Rule 2: Never Own When 50d < 200d (Death Cross)

**Logic:** Short-term momentum counter to long-term trend = danger zone

**Visual:** Red MA below blue MA = automatic pass

**Why:** This configuration precedes most major declines

### Rule 3: Never Own a Relative Downtrend

**Logic:** If asset underperforming benchmark, you're in wrong asset

**Visual:** Panel 2 shows red/magenta = automatic pass

**Why:** Opportunity cost—capital better deployed in relative leaders

### Rule 4: Never Add to Losers

**Logic:** Averaging down violates trend-following philosophy

**Why:** Catching knives vs riding rockets—we choose rockets

### Rule 5: Never Chase Above +15% Extension from 50d MA

**Logic:** Parabolic moves mean revert violently

**Exception:** Can hold existing position with trailing stop, but no new entry

### Rule 6: Never Fight the Macro Regime

**Logic:** MRI > +1.5 = Crisis = no new equity longs regardless of setup quality

**Why:** Regime overwhelms individual setup quality

---

## VIII. Asset Class Framework & Implementation

### Core Portfolio (90% of Capital)

**1. U.S. Equities (40-70%)**
- Primary: SPY (S&P 500 ETF)
- Alternatives: VTI (Total Market), QQQ (Nasdaq), sector tilts
- Futures: ES (E-mini S&P 500) for tactical overlays

**2. U.S. Bonds (20-50%)**
- Primary: AGG (Aggregate Bond), TLT (Long Duration)
- Alternatives: SHY (Short Duration), IEF (Intermediate)
- Futures: ZN (10-Year Notes), ZB (Long Bond)

**3. Cash (0-30%)**
- Primary: SGOV (Short-term T-bills), money market
- **Active position, not residual.** 100% cash is valid when MRI > +1.5.

### Tactical Overlays (10% of Capital, Rotational)

| **Asset** | **Allocation** | **Vehicle** | **Use Case** |
|-----------|---------------|-------------|--------------|
| Gold | 0-10% | GLD, GC futures | Crisis hedge, real rate hedge |
| Commodities | 0-10% | DBC, CL futures | Inflation hedge |
| International | 0-15% | VEA, VWO | Diversification, rotation |
| Sector Tilts | 0-20% | XLU, XLP, XLV (defensive) | Late-cycle positioning |
| Volatility | 0-5% | VXX, TAIL | Tail risk hedging |
| Crypto | 0-10% | BTC, ETH, spot ETFs | Liquidity cycle beta |

### Instrument Selection: Futures vs ETFs

**Use Futures When:**
- Position > $500,000 (cost advantage dominates)
- Any leverage required (ETF borrowing costs punitive)
- Short positions (stock borrow costs avoided)
- Holding period 3-6 months (roll costs manageable)
- International investor (dividend withholding avoided)

**Use ETFs When:**
- Position < $100,000 (operational simplicity)
- Unleveraged long only
- Tax-advantaged accounts (no mark-to-market)
- Assets lacking liquid futures (sectors, thematics)

### Cost Comparison (3-Month Hold)

| **Asset** | **Futures Cost** | **ETF Cost** | **Advantage** |
|-----------|-----------------|--------------|---------------|
| S&P 500 | ~3 bps | ~5.8 bps | Futures +2.8 bps |
| 10-Year Treasury | ~2 bps | ~8 bps | Futures +6 bps |
| Gold | ~4 bps | ~14 bps | Futures +10 bps |
| Crude Oil | Variable | 125-375 bps* | Futures (massive) |

*Futures-based commodity ETFs suffer severe contango drag

---

## IX. Tactical Timeframe Optimization

### The 3-6 Month Tactical Sweet Spot

Research across 80+ years of market data reveals that the 3-6 month horizon represents a "Goldilocks zone":

| **Timeframe** | **GDP Forecast Error** | **Momentum Persistence** | **Verdict** |
|---------------|------------------------|--------------------------|-------------|
| < 1 month | N/A | +1.0 Sharpe | Noise, high turnover |
| 1-3 months | ±1.5 ppts | +0.9 Sharpe | Event-driven overlay |
| **3-6 months** | **±2.0 ppts** | **+0.8 Sharpe** | **Optimal tactical** |
| 6-12 months | ±2.2 ppts | +0.5 Sharpe | Signal decay |
| > 12 months | ±2.6 ppts | Reversal risk | Mean reversion |

### The Magic Number: Formation + Holding = 14-18 Months

For 3-month tactical positions: Use 9-12 month lookback
For 6-month tactical positions: Use 6-12 month lookback

**The 12-14 Month Danger Zone:** Momentum-to-mean-reversion transition. Exit or reverse by month 12-14.

### Three-Layer Position Architecture

**Layer 1: Core Strategic-Tactical (60-70% of risk budget)**
- Holding period: 3-6 months
- Adjustment frequency: Monthly to quarterly
- Signal source: MRI, LFI, LCI regime changes
- Current example: 40% equity / 45% bonds / 15% cash (MRI +1.1 defensive)

**Layer 2: Tactical Intermediate (20-30% of risk budget)**
- Holding period: 1-3 months
- Adjustment frequency: Weekly to monthly
- Signal source: Relative strength rotation, sector momentum
- Current example: Overweight XLV (healthcare), underweight XLF (financials)

**Layer 3: Event-Driven Overlays (10-20% of risk budget)**
- Holding period: 1-3 weeks
- Adjustment frequency: Event-triggered
- Signal source: FOMC, data releases, liquidity stress

### Event-Driven Positioning: The FOMC Trade

**Pre-FOMC Equity Drift (49 bps average, 1.14 Sharpe):**
- Days -10 to -5: Establish 5-10% long equity position
- Day -1 (24 hours before): Scale to 15-20%
- Day 0 (announcement): Exit 75-100% at or before 2:15pm

**Post-FOMC Treasury Drift (120+ bps over 50 days):**
- Day 0 (post-announcement): Establish 10-15% duration position
- Day 20: Scale to 20% if drift confirms
- Day 45-50: Exit before mean reversion begins

**Annual Opportunity:** 8 FOMC meetings × (49 bps equity + 100 bps bonds) = 400-800 bps gross potential

---

## X. Risk Management Framework

### Position Limits (Hard Limits—Never Exceed)

| **Limit Type** | **Maximum** |
|----------------|-------------|
| Single position | 30% |
| Sector concentration | 40% |
| Gross exposure | 100% (no leverage) |
| Minimum liquidity | 5% (for rebalancing) |
| Correlated positions (ρ > 0.7) | Combined < 40% |

### Drawdown Protocols

| **Drawdown Level** | **Action** |
|-------------------|-----------|
| -5% | Review positioning, tighten stops, confirm thesis |
| -10% | Reduce gross exposure 25%, increase cash |
| -15% | Cut to minimum (20-30% equity), maximum defense |
| -20% | Emergency reassessment, potential strategy pause |

### Dual Stop-Loss Framework

**1. Thesis-Based Stops (Fundamental Invalidation)**

Exit when regime indicators reverse:
- LFI drops below 0.0 (labor stabilizing)
- Quits rate rises above 2.1% (confidence returning)
- Fed announces emergency liquidity intervention
- Credit spreads widen > 500 bps (stress already priced)
- MRI drops below +0.5 (risk normalizing)

**2. Price-Based Stops (Technical Invalidation)**

Exit when technical structure breaks:
- 50d MA crosses below 200d MA (trend broken)
- Relative strength breaks support (rotation signal)
- Stop-loss triggered (-5% to -10% depending on volatility)
- Z-RoC < -1.0 (momentum breakdown)

**Rule: Use whichever stop triggers first.**

### Rebalancing Protocol

**Threshold-Based (Not Calendar-Based):**
- Monitor: Biweekly (every 10 trading days)
- Trigger: 20% relative tolerance band breach
- Example: 50% target → rebalance at 40% or 60%
- Benefit: +55 bps annual vs no rebalancing, +22 bps vs annual calendar

**Signal-Driven Triggers:**
- MRI crosses threshold (+0.5, +1.0, +1.5)
- Any absolute rule violation
- Correlation spike > 2σ from average

---

## XI. Implementation Workflow

### Morning Routine (06:30 - 07:30 ET)

**1. Macro Regime Check (10 min)**
- Update LCI (RRP, reserves, TGA)
- Check stablecoin supply delta (7d, 30d)
- Review MRI composite
- **Determine:** Supportive (1.0x) / Neutral (0.6x) / Restrictive (0.3x)

**2. Portfolio Health Check (10 min)**

For each position, verify:
- [ ] Price still > 50d > 200d?
- [ ] Relative panel still green?
- [ ] Z-RoC still > -1.0?
- [ ] No absolute rule violations?

**Action:** If any fail, mark for review/exit

**3. Opportunity Scan (20 min)**

Screen for:
- Price > 50d > 200d (both rising)
- Relative panel green
- Z-RoC between -0.5 and +1.5 (not broken, not euphoric)
- Recent consolidation near 50d MA (10-30 days)

**Result:** 3-5 candidates for deeper analysis

**4. Deep Dive Analysis (10 min per candidate)**
- Pull up 3-panel chart
- Score Technical (0-9), Fundamental (0-5), Microstructure (0-5)
- Calculate composite, assign tier
- Check Perfect Setup elements (6-point checklist)

**Result:** Ranked list with position size targets

### Weekly Review (Sunday Evening, 60 min)

**1. Position Rescore (30 min)**
- Recalculate conviction scores for all positions
- Check for 25%+ drift from target size
- Update stops based on new structure

**2. Framework Calibration (15 min)**
- Review win/loss ratio past week
- Check if stops are too tight/loose (> 40% stopped out = too tight)
- Assess if regime classification accurate

**3. Opportunity Pipeline (15 min)**
- Review candidates that didn't qualify
- Note any approaching Perfect Setup configurations
- Set alerts for Z-RoC crosses, breakout levels

### Monthly Deep Dive (First Sunday, 2 hours)

**1. Performance Attribution (45 min)**
- Which setups worked? (Perfect Setup vs others)
- Which regime classification was accurate?
- Any rule violations? (did we break absolute rules?)

**2. Framework Refinement (30 min)**
- Should conviction tier thresholds adjust?
- Are momentum thresholds valid for current volatility regime?
- Any systematic errors in scoring?

**3. Macro Outlook Update (45 min)**
- Deep dive all 12 pillar composites
- Fed policy trajectory assessment
- Update regime probability distribution (next 3 months)

---

## XII. Crypto-Specific Considerations

### Benchmark Selection Hierarchy

**Tier 1: BTC as Universal Default (80% of positions)**

Use for: L1 competitors, infrastructure, store-of-value alternatives, cross-chain protocols

**Rationale:** BTC is the liquidity anchor. If an asset can't beat BTC, why hold it?

**Tier 2: ETH for Ethereum Ecosystem (15% of positions)**

Use for: L2s (ARB, OP), DeFi protocols (UNI, AAVE), ETH-denominated assets

**Rationale:** These are leveraged bets on Ethereum's success. Primary benchmark = ETH, secondary check = BTC.

**Tier 3: Sector Indices (5% of positions)**

Use for: Sector rotation strategies with 10+ positions

**Practical recommendation:** Skip this for concentrated portfolios.

### Crypto Position Sizing Adjustments

**Liquidity Adjustment:**
- BTC, ETH: 1.0x (fully liquid)
- Top 10 by market cap: 0.9x
- Top 11-50: 0.7x
- Top 51-100: 0.5x
- Outside Top 100: 0.3x or avoid

**Volatility Adjustment:**
- Crypto positions should generally be sized 40-60% of equivalent conviction equity positions
- Example: Tier 1 equity = 20%, Tier 1 crypto = 8-12%

### Crypto Instrument Selection

**Use Spot ETFs (IBIT, FBTC, BITB) When:**
- 3-6 month tactical horizon
- Tax-advantaged accounts
- Simplicity preferred
- All-in cost: 9-33 bps for 3 months

**Use Spot (Direct Holdings) When:**
- Longer holding periods
- Self-custody preference
- Access to DeFi yield

**Avoid Perpetual Futures Unless:**
- Very short-term (< 1 week)
- Funding rates neutral to negative
- Running dedicated short-term technical book

---

## XIII. Current Regime Assessment

### January 2026 State

**MRI: +1.1 (HIGH RISK)**

| **Indicator** | **Reading** | **Signal** |
|---------------|-------------|------------|
| LFI | +0.93 | 🔴 Labor fragility elevated |
| LCI | -0.8 | 🔴 Liquidity buffer exhausted |
| CLG | -1.2 | 🔴 Credit complacent |
| PCI | +0.7 | ⚠️ Inflation elevated |
| GCI-Gov | +1.1 | 🔴 Fiscal dominance |

### Current Tactical Allocation

| **Asset** | **Strategic** | **Tactical** | **Rationale** |
|-----------|---------------|--------------|---------------|
| SPY (Equities) | 60% | 40% | Underweight -20% (MRI +1.1, expensive) |
| AGG (Bonds) | 40% | 45% | Overweight +5% (Fed cutting likely) |
| Cash | 0% | 10% | Add +10% (liquidity, reduce vol) |
| XLV (Healthcare) | 0% | 3% | Defensive sector tilt |
| GLD (Gold) | 0% | 2% | Crisis hedge |

### Invalidation Criteria

**Exit defensive positioning if:**
- Quits rate rises above 2.1%
- LFI drops below +0.5
- MRI drops below +0.5
- Fed announces emergency liquidity intervention
- Credit spreads widen > 500 bps (stress priced)

### Expected Outcomes

**If Thesis Correct (Recession Q4 2026):**
- Portfolio: -3.5% (vs strategic -11.5%)
- **Outperformance: +8%**

**If Thesis Wrong (Goldilocks Continues):**
- Portfolio: +5.0% (vs strategic +7%)
- **Underperformance: -2%**

**Risk/Reward:** Asymmetric—avoid -8% vs give up -2%

---

## The Psychological Edge: Trusting the Framework

The hardest part isn't calculating scores. It's following the rules when your gut screams otherwise.

### Scenario 1: Missing the Moonshot
- Asset you passed on runs +200%
- **Framework Response:** How many wrong setups did you avoid? One winner doesn't validate ignoring rules.
- **Action:** Log the miss, analyze if scoring was wrong or luck.

### Scenario 2: Stopped Out at the Bottom
- Entry at $100, stopped at $92, asset rallies to $130 next week
- **Framework Response:** Stop protected capital when thesis in question.
- **Action:** If setup re-qualifies, re-enter. Don't regret risk management.

### Scenario 3: Watching from Sidelines in Restrictive Regime
- MRI elevated, 80% cash, market rips 15%
- **Framework Response:** Regime filter exists for inevitable reversal.
- **Action:** Wait for regime shift confirmation before deploying.

### Scenario 4: The Perfect Setup That Fails
- All 6 elements align, 20% position, drops -12% to stop
- **Framework Response:** 50-60% win rate means 40-50% fail. This is expected.
- **Action:** Check if setup truly met criteria. If legit, accept and move on.

**The Edge:** Most traders abandon their system after 2-3 losses. We trust ours through 40-50 losses knowing the 50-60 wins compound harder.

---

## Closing: The Edge is in the Discipline

We've built a framework that combines:
- **Macro overlay** (12 Pillars → MRI regime filter)
- **Technical precision** (trend + momentum + structure + relative strength)
- **Systematic scoring** (removes emotion from conviction assessment)
- **Absolute rules** (prevents mistakes that blow up accounts)

But here's the truth: **None of this works if you don't follow it.**

The market will show you a thousand reasons to override the rules:
- "This one's different"
- "I have special information"
- "Rules are for other people"

Every overridden rule is a deposit in the account of regret. Every followed rule—even when painful—is compounding discipline.

You don't need to be smarter than the market. You need to be more disciplined than your past self.

**That's the only edge that matters.**

---

**That's our view from the Watch. Until next time, we'll be sure to keep the light on....**

*Bob Sheehan, CFA, CMT*
*Founder & CIO, Lighthouse Macro*
*January 19, 2026*

---

*This document integrates the Position Sizing & Risk Management Framework, Multi-Asset Macro Strategy, Tactical Timeframe Optimization Framework, Benchmark Selection for Crypto Relative Strength Analysis, and the 12 Macro Pillars (The Diagnostic Dozen) into a single cohesive trading strategy. For detailed pillar-level analysis, refer to the individual PILLAR documents (1-12).*
