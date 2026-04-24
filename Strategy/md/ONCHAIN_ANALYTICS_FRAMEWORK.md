# On-Chain Analytics & Token Fundamental Analysis Framework
## Lighthouse Macro Digital Asset Research

*"Flows > Stocks applies to crypto too. We track protocol revenue flows, user acquisition dynamics, and valuation fundamentals systematically."*

---

## Table of Contents
1. [Framework Overview](#framework-overview)
2. [LHM Sector Taxonomy](#lhm-sector-taxonomy)
3. [The Three Pillars of Token Analysis](#the-three-pillars)
4. [Metric Categories & Definitions](#metric-categories)
5. [LHM Proprietary Ratios](#lhm-proprietary-ratios)
6. [The 24-Point Scoring System](#24-point-scoring)
7. [Microstructure Analysis](#microstructure-analysis)
8. [The Perfect Setup](#the-perfect-setup)
9. [Verdict Logic & Screening](#verdict-logic)
10. [Position Sizing & Risk Management](#position-sizing)
11. [Technical Overlay Book](#technical-overlay-book)
12. [Trading Rules Framework](#trading-rules)
13. [Red Flags & Warning Signs](#red-flags)
14. [Data Sources & Vendor Infrastructure](#data-sources)
15. [Python Implementation](#python-implementation)

---

## Framework Overview

### Philosophy
Token fundamental analysis applies the same rigor we use in macro to digital assets:
- **Revenue quality matters**: Fees from organic usage > fees from incentivized activity
- **Dilution is the enemy**: Token incentives are stock-based compensation, treat them as expenses
- **Users are customers**: DAU/MAU trends reveal product-market fit
- **Cash flow beats narrative**: Earnings > hype

### The Token Terminal Advantage
Token Terminal provides standardized financial metrics across 700+ protocols, enabling:
- Apples-to-apples comparisons across sectors
- Historical trend analysis
- Valuation relative to fundamentals

---

## LHM Sector Taxonomy

We strip away marketing terms ("GameFi," "SocialFi") and categorize by **economic function**.

| LHM Sector | Economic Function | Key Metric | Examples |
|---|---|---|---|
| **Layer 1 (Settlement)** | The economy itself. Security & finality. | Blockspace Demand (Fees) | ETH, SOL, AVAX |
| **Layer 2 (Scaling)** | Execution bandwidth. High throughput. | Margins (L2 Fee - L1 Rent) | ARB, OP, BASE |
| **DeFi - DEX** | Trading services. Liquidity provision. | Volume / TVL (Capital Efficiency) | UNI, CRV, RAY |
| **DeFi - Lending** | Banking services. Interest rate spread. | Revenue / TVL (Utilization) | AAVE, COMP, MKR |
| **DeFi - Derivatives** | Leverage and hedging. | Notional Volume / OI | GMX, DYDX, HLP |
| **Liquid Staking** | Staking derivatives. Yield tokenization. | Assets Staked / Take Rate | LDO, RPL, JTO |
| **Infrastructure** | Oracles, indexers, middleware. | Integrations / Revenue | LINK, GRT, PYTH |
| **Stablecoins** | USD-pegged token issuers. | Outstanding Supply / Revenue | USDC, USDT, SKY |
| **Real World Assets (RWA)** | Off-chain collateral onboarding. | AUM / Yield Spread | ONDO, CFG |

**Key Insight**: L1 chains are infrastructure, not businesses. Their "token incentives" are security budget (paying validators), not marketing spend. Judge L1s by fees and usage, not revenue.

---

## The Three Pillars of Token Analysis

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         TOKEN FUNDAMENTAL FRAMEWORK                              │
├───────────────────────┬─────────────────────────┬───────────────────────────────┤
│   FINANCIAL HEALTH    │   USAGE & ADOPTION      │   VALUATION & DILUTION        │
│   (Is it profitable?) │   (Is it growing?)      │   (Is it cheap?)              │
├───────────────────────┼─────────────────────────┼───────────────────────────────┤
│ • Fees                │ • DAU/WAU/MAU           │ • P/F Ratio                   │
│ • Revenue             │ • Transaction Count     │ • P/S Ratio                   │
│ • Take Rate           │ • TVL                   │ • FDV vs Circulating          │
│ • Gross Profit        │ • Trading Volume        │ • Token Incentives/Revenue    │
│ • Earnings            │ • Active Addresses      │ • Earnings Yield              │
│ • Treasury            │ • Developer Activity    │ • Revenue/FDV                 │
└───────────────────────┴─────────────────────────┴───────────────────────────────┘
```

---

## Metric Categories & Definitions

### 1. MARKET METRICS (Token Valuation)

| Metric | ID | Definition | Use Case |
|--------|-----|------------|----------|
| **Fully Diluted Market Cap** | `market_cap_fully_diluted` | Token price × total supply (including unvested) | True diluted valuation |
| **Circulating Market Cap** | `market_cap_circulating` | Token price × circulating supply | Current market valuation |
| **Token Trading Volume** | `token_trading_volume` | CEX + DEX spot volume | Liquidity assessment |
| **Token Holders** | `tokenholders` | Unique addresses with balance > 0 | Distribution breadth |

**Key Insight**: FDV/Circulating ratio > 3x = significant future dilution risk.

---

### 2. FINANCIAL METRICS (Revenue & Profitability)

| Metric | ID | Definition | Use Case |
|--------|-----|------------|----------|
| **Fees** | `fees` | Total value users pay to use the protocol | Gross economic activity |
| **Revenue** | `revenue` | Fees × Take Rate (what protocol keeps) | Top-line earnings |
| **Take Rate** | `take_rate` | Revenue / Fees | Monetization efficiency |
| **Gross Profit** | `gross_profit` | Revenue - Cost of Revenue | After external payments |
| **Earnings** | `earnings` | Revenue - All Expenses | Bottom line (can be negative) |
| **Token Incentives** | `token_incentives` | Value of tokens paid to users/contributors | Hidden dilution cost |
| **Treasury** | `treasury` | Protocol's onchain holdings (including native token) | Runway assessment |
| **Treasury (net)** | `treasury_net` | Treasury excluding native token | Real dry powder |

**Key Insight**: Earnings = Revenue - Token Incentives - Operating Expenses. Most protocols have negative earnings due to heavy token incentives.

---

### 3. USAGE METRICS (Product-Market Fit)

| Metric | ID | Definition | Use Case |
|--------|-----|------------|----------|
| **Daily Active Users** | `user_dau` | Unique addresses generating revenue daily | Core engagement |
| **Weekly Active Users** | `user_wau` | 7-day rolling unique users | Trend smoothing |
| **Monthly Active Users** | `user_mau` | 30-day rolling unique users | Adoption breadth |
| **Transaction Count** | `transaction_count` | Confirmed transactions | Network activity |
| **TVL** | `tvl` | Total value locked in contracts | Capital commitment |
| **Trading Volume** | `trading_volume` | DEX trading volume | Exchange activity |
| **Active Loans** | `active_loans` | Outstanding loan value | Lending utilization |

**Key Insight**: DAU/MAU ratio (stickiness) > 20% = strong product-market fit.

---

### 4. DEVELOPMENT METRICS (Builder Activity)

| Metric | ID | Definition | Use Case |
|--------|-----|------------|----------|
| **Core Developers** | `active_developers` | GitHub contributors (30-day) | Engineering capacity |
| **Code Commits** | `code_commits` | Total commits to public repos | Development velocity |
| **Contracts Deployed** | `contracts_deployed` | New smart contracts onchain | Ecosystem growth |
| **Contract Deployers** | `contract_deployers` | Unique deployer addresses | Developer adoption |

---

### 5. VALUATION RATIOS

| Metric | ID | Definition | Interpretation |
|--------|-----|------------|----------------|
| **P/F (Circulating)** | `pf_circulating` | Circ. Market Cap / Annualized Fees | < 50 = cheap, > 200 = expensive |
| **P/F (Fully Diluted)** | `pf_fully_diluted` | FDV / Annualized Fees | True diluted valuation |
| **P/S (Circulating)** | `ps_circulating` | Circ. Market Cap / Annualized Revenue | < 20 = cheap, > 100 = expensive |
| **P/S (Fully Diluted)** | `ps_fully_diluted` | FDV / Annualized Revenue | True diluted valuation |

**Custom Ratios to Calculate**:
- **Earnings Yield**: Annualized Earnings / Market Cap
- **Dilution Rate**: Token Incentives / Revenue (< 100% = sustainable)
- **Revenue per User**: Revenue / DAU
- **TVL Efficiency**: Fees / TVL (higher = better capital efficiency)

---

## Sector Classification

### Token Terminal Categories
| Category | Description | Key Metrics to Watch |
|----------|-------------|---------------------|
| **Blockchains (L1)** | Base layer networks | Fees, DAU, TPS, Validator count |
| **Blockchains (L2)** | Scaling solutions | Bridge deposits, DA fees, TPS |
| **Exchanges (DEX)** | Decentralized trading | Trading volume, Liquidity, Take rate |
| **Lending** | Borrowing/lending protocols | Active loans, TVL, Interest rates |
| **Liquid Staking** | Staking derivatives | Assets staked, Staking yield |
| **Stablecoin Issuers** | USD-pegged tokens | Outstanding supply, Holders, Transfer volume |
| **Real-world Assets (RWA)** | Tokenized traditional assets | AUM, Yield, Holder count |
| **Infrastructure** | Developer tooling, oracles | Revenue, Integrations, API calls |
| **DePIN** | Decentralized physical infra | Network capacity, Revenue, Utilization |

### Botsfolio Sector Mapping
| Botsfolio Category | Token Terminal Equivalent | Notes |
|-------------------|--------------------------|-------|
| Smart Contract Platform | Blockchains (L1) | Same |
| Layer 1 (L1) | Blockchains (L1) | Same |
| Layer 2 (L2) | Blockchains (L2) | Same |
| Decentralized Exchange (DEX) | Exchanges (DEX) | Same |
| Oracle | Infrastructure | Subset |
| Storage | Infrastructure | Subset |
| DePIN | Infrastructure | Overlap |
| Metaverse | Gaming | Related |
| Artificial Intelligence (AI) | Infrastructure | Subset |
| RWA Protocol | Real-world asset (RWA) issuers | Same |

---

## LHM Proprietary Ratios

### The "Diagnostic Dozen" for Crypto

We map our macro pillars to on-chain equivalents:

| LHM Pillar | Crypto Equivalent | Metric |
|---|---|---|
| **Labor (1)** | Developer Activity | Weekly Active Developers / Commits |
| **Growth (3)** | User Velocity | Daily Active Addresses (DAU) & Tx Count |
| **Prices (2)** | Gas/Fees | Avg Cost per Tx (Demand for blockspace) |
| **Financial (9)** | Lending Health | Outstanding Loans vs. Total Collateral |
| **Plumbing (10)** | Stablecoin Supply | Total Stablecoins on Chain (USDT+USDC) |
| **Structure (11)** | Holder Distribution | Gini Coefficient / Whale Concentration |

### Core LHM Ratios

**1. Subsidy Score** (Is the protocol organic or paying users to stay?)
```
Subsidy Score = Token Incentives / Revenue

Signal:
- < 0.5  → ORGANIC (Tier 1 candidate)
- 0.5-2.0 → SUBSIDIZED (monitor trend)
- > 2.0  → UNSUSTAINABLE (Avoid)

Exception: L1 chains are exempt. Their "incentives" are security budget.
```

**2. Float Ratio** (Is there a VC unlock overhang?)
```
Float Ratio = Circulating Supply / Total Supply

Signal:
- > 70%  → Healthy (most supply trading)
- 50-70% → Acceptable
- 20-50% → Caution (significant unlocks coming)
- < 20%  → PREDATORY (massive dilution ahead)
```

**3. Capital Efficiency** (Is capital being used productively?)
```
Capital Turnover = Daily Volume / TVL

Signal:
- > 10%  → Efficient (capital working hard)
- 5-10%  → Normal
- < 5%   → Idle capital / possible wash trading
```

**4. DAU/MAU Ratio (Stickiness)**
```
Stickiness = Daily Active Users / Monthly Active Users

Signal:
- > 30%  → Strong product-market fit
- 15-30% → Decent engagement
- < 15%  → Low retention / one-time users
```

---

## The 24-Point Scoring System

### Overview

Every crypto position receives a composite score from 0-24 points across three equally-weighted dimensions. The 24-point system mirrors the 12 Macro Pillars (Diagnostic Dozen × 2 = 24).

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         24-POINT SCORING SYSTEM                                  │
│                    (12 Pillars Macro × 2 = 24 Position)                         │
├───────────────────────┬─────────────────────────┬───────────────────────────────┤
│   TECHNICAL           │   FUNDAMENTAL           │   MICROSTRUCTURE              │
│   (0-8 points)        │   (0-8 points)          │   (0-8 points)                │
├───────────────────────┼─────────────────────────┼───────────────────────────────┤
│ Price vs 200d MA (2)  │ Subsidy Score (2)       │ Funding Rate (2)              │
│ Price vs 50d MA (2)   │ Float / Unlock (2)      │ Liquidation Asymmetry (2)     │
│ 50d vs 200d (2)       │ Revenue Trend (2)       │ Exchange Flows (2)            │
│ Relative Strength (2) │ Valuation (2)           │ OI / Leverage (2)             │
├───────────────────────┴─────────────────────────┴───────────────────────────────┤
│ Equal weighting: 8 + 8 + 8 = 24                                                 │
│ Each pillar matters. No single dimension dominates.                             │
└─────────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
                            CONVICTION TIER ASSIGNMENT
```

**Design Rationale:**
- Technical tells you *when* to enter
- Fundamental tells you *what* to own
- Microstructure tells you *who else* is positioned

All three matter equally. A technically perfect setup with terrible fundamentals will fail. Great fundamentals with crowded positioning will chop you out.

---

### Technical Score (0-8 points)

**1. Price vs 200-Day Moving Average (0-2 points)**
| Condition | Points |
|-----------|--------|
| Price > 200d MA, 200d MA rising | 2 |
| Price > 200d MA, 200d MA flat/falling | 1 |
| Price < 200d MA | 0 |

**2. Price vs 50-Day Moving Average (0-2 points)**
| Condition | Points |
|-----------|--------|
| Price > 50d MA, 50d MA rising | 2 |
| Price > 50d MA, 50d MA flat | 1 |
| Price < 50d MA | 0 |

**3. 50-Day vs 200-Day Relationship (0-2 points)**
| Condition | Points |
|-----------|--------|
| 50d > 200d, both rising (Golden Cross) | 2 |
| 50d > 200d, flat or 50d crossing above | 1 |
| 50d < 200d (Death Cross active) | 0 |

**4. Relative Strength vs Benchmark (0-2 points)**
| Condition | Points |
|-----------|--------|
| Outperforming on 63d AND 252d | 2 |
| Outperforming on one timeframe | 1 |
| Underperforming on both | 0 |

*Benchmark: CRYPTO30 Index or BTC for altcoins, SPX for BTC itself.*

**Z-RoC Note:** Z-RoC is not scored separately. It's used as a confirmation/stop signal, not entry criteria. A positive Z-RoC confirms; Z-RoC < -1.0 triggers exit.

---

### Fundamental Score (0-8 points)

**1. Subsidy Score (0-2 points)**

*Is growth organic or paid for?*

| Condition | Points |
|-----------|--------|
| Subsidy < 0.5 (organic) | 2 |
| Subsidy 0.5-2.0 (subsidized but manageable) | 1 |
| Subsidy > 2.0 (unsustainable) | 0 |

```
Subsidy Score = Token Incentives / Revenue
```

*L1 Exception: Layer 1 chains are exempt. Their "incentives" are security budget (validator rewards), not marketing spend. Score L1s on P/F ratio instead.*

**2. Float & Unlock Calendar (0-2 points)**

*Is there a supply overhang?*

| Condition | Points |
|-----------|--------|
| Float > 70% AND no major unlock in 60 days | 2 |
| Float 50-70% OR unlock in 30-60 days | 1 |
| Float < 50% OR major unlock in < 30 days | 0 |

```
Float Ratio = Circulating Supply / Total Supply
Major Unlock = > 5% of circulating supply
```

**3. Revenue Trend (0-2 points)**

*Is the protocol growing?*

| Condition | Points |
|-----------|--------|
| Revenue growing QoQ AND YoY | 2 |
| Revenue growing on one timeframe | 1 |
| Revenue flat or declining | 0 |

*For L1s, use Fee growth instead of Revenue growth.*

**4. Valuation (0-2 points)**

*Is it cheap relative to fundamentals?*

| Condition (Applications) | Condition (L1s) | Points |
|--------------------------|-----------------|--------|
| P/E < 30 | P/F < 300 | 2 |
| P/E 30-75 | P/F 300-750 | 1 |
| P/E > 75 | P/F > 750 | 0 |

*Compare to sector median. A P/E of 50 might be cheap for high-growth DeFi but expensive for mature infrastructure.*

---

### Microstructure Score (0-8 points)

**1. Funding Rate (0-2 points)**

*Is the market crowded long or short?*

| Condition | Points |
|-----------|--------|
| Funding negative or near-zero (< 0.01%) | 2 |
| Funding moderately positive (0.01-0.03%) | 1 |
| Funding highly positive (> 0.03%) | 0 |

```
Negative funding = shorts paying longs = crowded short = bullish
High positive funding = longs paying shorts = crowded long = bearish
```

*Source: Coinglass, Binance*

**2. Liquidation Asymmetry (0-2 points)**

*Has one side been washed out?*

| Condition | Points |
|-----------|--------|
| Short liquidations > 60% of 24h total (bearish washout) | 2 |
| Balanced (40-60% either side) | 1 |
| Long liquidations > 60% of 24h total (longs wrecked) | 0 |

```
Liquidation Ratio = Long Liqs / (Long Liqs + Short Liqs)
< 0.4 = shorts washed (bullish)
> 0.6 = longs washed (bearish for entry)
```

*Source: Coinglass*

**3. Exchange Flows (0-2 points)**

*Is smart money accumulating or distributing?*

| Condition | Points |
|-----------|--------|
| Net outflows for 7+ days (accumulation) | 2 |
| Mixed or neutral flows | 1 |
| Net inflows for 7+ days (distribution) | 0 |

```
Net Flow = Exchange Inflows - Exchange Outflows
Sustained outflows = coins moving to cold storage = bullish
Sustained inflows = coins moving to exchanges to sell = bearish
```

*Source: Glassnode, CryptoQuant*

**4. Open Interest & Leverage (0-2 points)**

*Is the market over-leveraged?*

| Condition | Points |
|-----------|--------|
| OI/MCap < 3% AND OI declining or stable | 2 |
| OI/MCap 3-5% OR OI rising moderately | 1 |
| OI/MCap > 5% OR OI spiking (leverage flush risk) | 0 |

```
OI/MCap Ratio = Total Open Interest / Market Cap
High ratio = over-leveraged = vulnerable to liquidation cascades
```

*Source: Coinglass*

---

### Conviction Tier Assignment

| Total Score | Conviction Tier | Position Weight | Description |
|-------------|-----------------|-----------------|-------------|
| 20-24 | Tier 1 (High Conviction) | 15-20% | Near-perfect setup, load up |
| 15-19 | Tier 2 (Standard) | 8-12% | Good setup, standard position |
| 10-14 | Tier 3 (Reduced) | 4-7% | Marginal, reduced size |
| < 10 | Tier 4 (Avoid) | 0% | Insufficient conviction |

**Minimum Thresholds by Section:**

A position can be disqualified even with a decent total score if any single section is too weak:

| Section | Minimum Score | Rationale |
|---------|---------------|-----------|
| Technical | 4/8 | Below this, trend is broken |
| Fundamental | 3/8 | Below this, thesis is weak |
| Microstructure | 2/8 | Below this, positioning dangerous |

*Example: A score of 16 (Tier 2) with Technical 7, Fundamental 7, Microstructure 2 should be downgraded or skipped. The microstructure is flashing danger even though total score looks fine.*

---

## Microstructure Analysis

### Overview

Microstructure data reveals positioning, leverage, and flow dynamics invisible to fundamental analysis alone. This is where crypto's 24/7 derivatives markets provide unique edge.

### Key Microstructure Metrics

**1. Funding Rates**
```
Funding Rate = Premium between perpetual and spot prices

Interpretation:
- Positive funding: Longs pay shorts (crowded long)
- Negative funding: Shorts pay longs (crowded short)
- Extreme positive (>0.05%): Distribution setup
- Extreme negative (<-0.03%): Accumulation setup
```

**2. Open Interest**
```
OI Analysis Framework:
- Rising OI + Rising Price = New longs entering (trend continuation)
- Rising OI + Falling Price = New shorts entering (potential squeeze)
- Falling OI + Rising Price = Short covering (weak rally)
- Falling OI + Falling Price = Long liquidation (capitulation)
```

**3. Liquidation Asymmetry**
```
24h Liquidation Ratio = Long Liquidations / Total Liquidations

Signal:
- Ratio > 0.7: Long washout (contrarian bullish)
- Ratio 0.3-0.7: Balanced
- Ratio < 0.3: Short squeeze environment
```

**4. Exchange Flows**
```
Net Flow = Inflows - Outflows

Interpretation:
- Sustained outflows: Accumulation (bullish)
- Sustained inflows: Distribution (bearish)
- Whale alerts (>$10M moves): Immediate attention
```

**5. Holder Distribution**
```
Segments to monitor:
- Whales (>1000 BTC / >10000 ETH): Smart money proxy
- Retail (<1 BTC / <10 ETH): Sentiment indicator
- Exchange reserves: Selling pressure gauge

Ideal setup: Whale accumulation + retail distribution
```

### Data Sources for Microstructure

| Metric | Primary Source | Secondary Source |
|--------|---------------|------------------|
| Funding Rates | Coinglass | Binance API |
| Open Interest | Coinglass | Glassnode |
| Liquidations | Coinglass | CoinGecko |
| Exchange Flows | Glassnode | CryptoQuant |
| Holder Distribution | Glassnode | Nansen |
| Whale Alerts | Whale Alert | Arkham |

---

## The Perfect Setup

### The 6-Element Criterion

A "Perfect Setup" represents maximum conviction and justifies maximum position sizing. All six elements must align:

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            THE PERFECT SETUP                                     │
│                    (All 6 elements must be present)                              │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  1. PRIMARY TREND ALIGNED                                                        │
│     Price > 50d MA > 200d MA, both MAs rising                                   │
│                                                                                  │
│  2. RELATIVE STRENGTH CONFIRMED                                                  │
│     Outperforming BTC on 63d and 252d timeframes                                 │
│                                                                                  │
│  3. CONSOLIDATION PRESENT                                                        │
│     10-30 days of sideways price action                                         │
│     Volatility compressing (Bollinger Bands narrowing)                          │
│                                                                                  │
│  4. MOMENTUM COOLED BUT NOT BROKEN                                              │
│     Z-RoC pulled back but never hit -1.0                                        │
│     RSI(14) between 40-60 (not overbought or oversold)                          │
│                                                                                  │
│  5. BREAKOUT TRIGGER                                                             │
│     Price breaks consolidation range                                            │
│     Volume spike (>1.5x 20-day average)                                         │
│     Z-RoC crosses back above 0                                                  │
│                                                                                  │
│  6. MACRO REGIME SUPPORTIVE                                                      │
│     MRI < +1.5 (not crisis mode)                                                │
│     LCI > -1.0 (liquidity not scarce)                                           │
│     BTC not in death cross                                                      │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Perfect Setup Checklist

```
═══════════════════════════════════════════════════════════════
PERFECT SETUP EVALUATION: [TOKEN]
Date: [DATE]
═══════════════════════════════════════════════════════════════

TECHNICAL STRUCTURE
[ ] Price > 50d MA > 200d MA
[ ] Both MAs rising (slope positive)
[ ] Not extended (< 15% above 50d MA)

RELATIVE PERFORMANCE
[ ] Outperforming BTC 63d
[ ] Outperforming BTC 252d
[ ] Relative strength line making new highs

CONSOLIDATION
[ ] 10-30 days of base building
[ ] Volume declining during consolidation
[ ] Bollinger Band width < 20-day average

MOMENTUM
[ ] Z-RoC never hit -1.0 during pullback
[ ] RSI(14) between 40-60
[ ] MACD histogram turning positive

BREAKOUT QUALITY
[ ] Price cleared consolidation resistance
[ ] Volume > 1.5x 20-day average
[ ] Closed above breakout level (not just wick)

MACRO CONFIRMATION
[ ] MRI < +1.5
[ ] LCI > -1.0
[ ] BTC above its 200d MA
[ ] No major negative catalyst imminent

SCORE: ___/12 elements
VERDICT: [PERFECT SETUP / NEAR SETUP / NOT QUALIFIED]
═══════════════════════════════════════════════════════════════
```

### What Disqualifies a Setup

| Condition | Why It Disqualifies |
|-----------|---------------------|
| Below 200d MA | Primary trend broken |
| Death Cross active | Intermediate trend bearish |
| Underperforming BTC | Relative weakness, better alternatives exist |
| Z-RoC < -1.0 | Momentum broken, need reset |
| Extended > 15% above 50d | Chase risk, poor risk/reward |
| MRI > +1.5 | Macro regime hostile |
| BTC in death cross | Rising tide lifts all boats (reversed) |

---

## Verdict Logic & Screening

### LHM Verdict Categories

| Verdict | Meaning | Action |
|---|---|---|
| **TIER 1 (Accumulate)** | Strong fundamentals, organic traction, fair value | Build position |
| **TIER 2 (Hold)** | Decent fundamentals, reasonable valuation | Maintain exposure |
| **NEUTRAL (Watch)** | Mixed signals, monitor for improvement | Watchlist only |
| **CAUTION (Low Float)** | Good metrics but massive unlock overhang | Avoid until unlocks |
| **AVOID (Vaporware)** | High FDV, minimal revenue | Do not touch |
| **AVOID (Unsustainable)** | Subsidy Score > 2.0 | Ponzi dynamics |
| **AVOID (Dead)** | No developers, no users | Abandoned |

### Verdict Decision Tree

```
START
  │
  ├─→ Is FDV > $1B AND Revenue < $1M (or Fees < $10M for L1)?
  │     YES → AVOID (Vaporware)
  │
  ├─→ Is Subsidy Score > 2.0 (excluding L1s)?
  │     YES → AVOID (Unsustainable)
  │
  ├─→ Is Active Devs < 3 AND DAU < 100?
  │     YES → AVOID (Dead Chain)
  │
  ├─→ Is Float Ratio < 20%?
  │     YES → CAUTION (Low Float)
  │
  ├─→ FOR L1 CHAINS:
  │     Is P/F < 500 AND Float > 50% AND DAU > 10K?
  │       YES → TIER 1
  │     Is P/F < 1000 AND Float > 30%?
  │       YES → TIER 2
  │
  ├─→ FOR APPLICATIONS:
  │     Is P/E < 40 AND Subsidy < 0.5 AND Float > 50%?
  │       YES → TIER 1
  │     Is P/E < 100 AND Subsidy < 1.0 AND Float > 30%?
  │       YES → TIER 2
  │
  └─→ DEFAULT: NEUTRAL (Watch)
```

### Example Output

```
LIGHTHOUSE MACRO CRYPTO FUNDAMENTALS REPORT
Generated: 2026-01-20

TIER 1 - ACCUMULATE
----------------------------------------
  Aave: P/E 19x, Subsidy 0.01x, Score 85
  GMX: P/E 13x, Subsidy 0.00x, Score 75
  Solana: L1 with P/F 318x, Float 91%, DAU 2.2M

TIER 2 - HOLD
----------------------------------------
  OP Mainnet: P/E 45x, Score 80
  Raydium: P/E 60x, Score 63

AVOID
----------------------------------------
  Chainlink: AVOID (Vaporware) - FDV $9B, Revenue $0.3M
  Morpho: AVOID (Vaporware) - No revenue yet
```

---

## Position Sizing & Risk Management

### Macro Regime Multipliers

Position sizing is adjusted based on the broader macro environment. Even great setups deserve smaller positions in hostile regimes.

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         MACRO REGIME MULTIPLIERS                                 │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  SUPPORTIVE REGIME (Multiplier: 1.0x)                                           │
│  ─────────────────────────────────────                                          │
│  • MRI < +0.5 (low macro risk)                                                  │
│  • LCI > 0 (ample liquidity)                                                    │
│  • BTC > 200d MA with golden cross                                              │
│  • Crypto total market cap trending up                                          │
│                                                                                  │
│  NEUTRAL REGIME (Multiplier: 0.6x)                                              │
│  ─────────────────────────────────────                                          │
│  • MRI +0.5 to +1.0                                                             │
│  • LCI between -0.5 and 0                                                       │
│  • BTC above 200d MA but below 50d MA                                           │
│  • Mixed signals, uncertainty elevated                                          │
│                                                                                  │
│  RESTRICTIVE REGIME (Multiplier: 0.3x)                                          │
│  ─────────────────────────────────────                                          │
│  • MRI > +1.0                                                                   │
│  • LCI < -0.5 (liquidity scarce)                                                │
│  • BTC below 200d MA or in death cross                                          │
│  • Flight to quality, risk-off dominant                                         │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Position Sizing Formula

```
Final Position Size = Base Weight × Conviction Multiplier × Regime Multiplier × Liquidity Adjustment

Where:
- Base Weight = Portfolio allocation ceiling (e.g., 5% for diversified, 20% for concentrated)
- Conviction Multiplier = 19-Point Score / 19 (ranges from 0 to 1)
- Regime Multiplier = 1.0 / 0.6 / 0.3 based on macro environment
- Liquidity Adjustment = min(1, Daily Volume / (Position Size × 10))
```

### Conviction Tiers and Weights

| Tier | Score Range | Base Weight | Example: Supportive | Example: Neutral | Example: Restrictive |
|------|-------------|-------------|---------------------|------------------|---------------------|
| **Tier 1** | 16-19 | 20% | 20% × 1.0 = 20% | 20% × 0.6 = 12% | 20% × 0.3 = 6% |
| **Tier 2** | 12-15 | 12% | 12% × 1.0 = 12% | 12% × 0.6 = 7.2% | 12% × 0.3 = 3.6% |
| **Tier 3** | 8-11 | 7% | 7% × 1.0 = 7% | 7% × 0.6 = 4.2% | 7% × 0.3 = 2.1% |
| **Tier 4** | <8 | 0% | No position | No position | No position |

### Portfolio Construction Rules

**Concentration Limits:**
- Maximum single position: 20% (only for Tier 1 in supportive regime)
- Maximum sector exposure: 40%
- Maximum correlated positions: 50%
- Minimum positions: 3 (diversification floor)
- Maximum positions: 10 (focus ceiling)

**Cash as a Position:**
- Restrictive regime: 30-50% cash is valid
- No suitable setups: 100% cash is valid
- Cash is never "residual drag," it's an active position

**Rebalancing Triggers:**
- Position exceeds 1.5x target weight: Trim to target
- Position falls below 0.5x target weight: Evaluate for exit
- Score drops below tier threshold: Reduce to new tier weight
- Absolute rule violation: Immediate exit (no gradual reduction)

### Dual Stop System

Every position has TWO stops. Hitting either triggers action:

**1. Thesis Stop (Fundamental)**
```
Exit if:
- Revenue declines 3 consecutive quarters
- Subsidy Score crosses above 2.0
- Float Ratio drops below 20% (new unlock)
- Key developer departure
- Protocol hack/exploit
```

**2. Price Stop (Technical)**
```
Exit if:
- Price closes below 200d MA (primary trend break)
- Z-RoC drops below -1.5 (momentum collapse)
- 25% drawdown from entry (hard stop)
- Trailing stop: 15% from highest close since entry
```

**Stop Execution Priority:**
1. Thesis stop = Full exit, no re-entry until thesis repairs
2. Price stop = Exit, can re-enter if setup forms again
3. Combined stop = Full exit + remove from watchlist

---

## Technical Overlay Book

### Concept

The Core Book is macro-driven. When MRI is elevated and the regime multiplier compresses position sizes to near-zero, the framework can leave capital idle even when clear technical trends exist. The Technical Overlay Book provides a structured way to participate in pure technical setups when the Core Book is defensive.

**This is not an override of the macro framework.** It's a separate, smaller allocation with different rules.

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         PORTFOLIO STRUCTURE                                      │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  CORE BOOK (70-100% of capital)                                                 │
│  ─────────────────────────────────                                              │
│  • Macro-driven (MRI regime multiplier applies)                                 │
│  • Fundamental + Technical + Microstructure scoring                             │
│  • 3-6 month holding period                                                     │
│  • Full position sizing (up to 20% per position)                                │
│  • Can go to 100% cash when MRI > +1.5                                          │
│  • Long only (shorts require explicit macro thesis)                             │
│                                                                                  │
│  TECHNICAL OVERLAY BOOK (0-30% of capital)                                      │
│  ─────────────────────────────────────────                                      │
│  • Pure technical (trend + momentum only)                                       │
│  • Activated when Core Book is defensive                                        │
│  • Shorter holding period (weeks, not months)                                   │
│  • Reduced sizing (max 5% per position)                                         │
│  • Tighter stops (10% hard stop, no exceptions)                                 │
│  • Can go LONG or SHORT                                                         │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Activation Criteria

The Technical Overlay Book is NOT always active. It requires explicit activation:

```
TECHNICAL BOOK ACTIVATION CHECKLIST:
────────────────────────────────────
[ ] Core Book is in defensive mode (MRI > +1.0)
[ ] At least 3 clear technical setups exist (long OR short)
[ ] BTC or SPX showing directional trend (not chop/range)
[ ] You have bandwidth to monitor shorter timeframes
[ ] You explicitly decide to activate (not automatic)

ALL conditions must be met to allocate to Technical Book.
```

**When to Deactivate:**
- MRI drops below +1.0 (Core Book re-activates fully)
- No remaining setups meet criteria
- Consecutive losses (3 stopped out in a row = pause and reassess)

### Technical Book Scoring (Simplified)

The Technical Book uses the **Technical section only** from the 24-point system. No fundamentals, no microstructure. Pure price action.

| Component | Points | Criteria |
|-----------|--------|----------|
| **Price vs 200d MA** | 0-2 | Trend health |
| **Price vs 50d MA** | 0-2 | Intermediate trend |
| **50d vs 200d** | 0-2 | Golden/Death Cross |
| **Relative Strength** | 0-2 | vs benchmark (63d/252d) |

**Total: 8 points (same as Technical section of 24-point system)**

**Scoring Details:**

**Price vs 200d MA (0-2 pts):**
| Condition (Long) | Condition (Short) | Points |
|------------------|-------------------|--------|
| Price > 200d, 200d rising | Price < 200d, 200d falling | 2 |
| Price > 200d, 200d flat | Price < 200d, 200d flat | 1 |
| Price < 200d | Price > 200d | 0 |

**Price vs 50d MA (0-2 pts):**
| Condition (Long) | Condition (Short) | Points |
|------------------|-------------------|--------|
| Price > 50d, 50d rising | Price < 50d, 50d falling | 2 |
| Price > 50d, 50d flat | Price < 50d, 50d flat | 1 |
| Price < 50d | Price > 50d | 0 |

**50d vs 200d (0-2 pts):**
| Condition (Long) | Condition (Short) | Points |
|------------------|-------------------|--------|
| 50d > 200d, both rising | 50d < 200d, both falling | 2 |
| 50d > 200d, flat | 50d < 200d, flat | 1 |
| 50d < 200d | 50d > 200d | 0 |

**Relative Strength (0-2 pts):**
| Condition (Long) | Condition (Short) | Points |
|------------------|-------------------|--------|
| Outperforming on 63d AND 252d | Underperforming on 63d AND 252d | 2 |
| Outperforming on one timeframe | Underperforming on one timeframe | 1 |
| Wrong direction | Wrong direction | 0 |

**Minimum Score to Enter: 6/8**

*Z-RoC is used as confirmation (positive for longs, negative for shorts) and stop trigger (crosses against position = exit), not as a scoring component.*

### Position Sizing (Technical Book)

The Technical Book uses flat sizing with strict limits:

| Parameter | Limit |
|-----------|-------|
| Max per position | 5% of total portfolio |
| Max total Technical Book | 30% of total portfolio |
| Max positions | 6 (at 5% each = 30% max) |
| Max correlated positions | 2 (e.g., 2 L1s, 2 memes) |

**No conviction tiers.** Every Technical Book position is 5% or skip. The simplified approach matches the simplified analysis.

### Stop Rules (Technical Book)

Stops are tighter and non-negotiable. No thesis stops because there's no fundamental thesis.

**Hard Stop: 10% from entry**
```
Entry at $100 → Stop at $90. No exceptions.
No "giving it room." No "waiting for confirmation."
10% = out.
```

**Technical Stop: MA Cross**
```
Long: Exit if price closes below 50d MA
Short: Exit if price closes above 50d MA
```

**Momentum Stop: Z-RoC Reversal**
```
Long: Exit if Z-RoC crosses below 0
Short: Exit if Z-RoC crosses above 0
```

**Time Stop: 20 trading days**
```
If position hasn't moved meaningfully in your direction
within 20 days, exit. The thesis was wrong or timing was off.
```

**Use whichever stop triggers first.**

### Short-Specific Requirements

Shorting has additional hurdles because markets drift up over time:

```
SHORT ENTRY CHECKLIST (All must be true):
─────────────────────────────────────────
[ ] Price < 50d < 200d (both MAs falling)
[ ] Z-RoC < -1.0 (not just negative, strongly negative)
[ ] Relative strength RED on both 63d and 252d
[ ] Clear breakdown (not just weakness, actual break of support)
[ ] NOT extended (price not >10% below 50d MA)
[ ] Score ≥ 7/9 on Technical Book scoring

ADDITIONAL SHORT RULES:
─────────────────────────────────────────
• Shorts get 3% max position (vs 5% for longs)
• Tighter stop: 8% (vs 10% for longs)
• Must have identifiable catalyst or structural reason
• Avoid shorting into known support levels
• Be aware of funding rates (crypto perps)
```

**Why shorts are harder:**
1. Unlimited upside risk vs limited downside on longs
2. Markets have long-term upward drift
3. Short squeezes are violent and fast
4. Borrowing costs / funding rates eat into returns
5. Timing matters more (trends down faster but bounce harder)

### Example: Technical Book in Action

```
SCENARIO: MRI at +1.2 (Restrictive), Core Book 85% cash

Technical Book Activation Check:
[✓] MRI > +1.0
[✓] Found 4 setups: SOL long, AAVE long, SUI short, LINK short
[✓] BTC in clear uptrend (above rising 50d)
[✓] Have time to monitor
→ ACTIVATE TECHNICAL BOOK

Position Selection:
• SOL: Score 8/9 → 5% long
• AAVE: Score 7/9 → 5% long
• SUI: Score 7/9 → 3% short (reduced for short)
• LINK: Score 6/9 → SKIP (below threshold)

Final Allocation:
• Core Book: 85% cash
• Technical Book: 13% (5% SOL, 5% AAVE, 3% SUI)
• Total: 85% cash + 13% technical + 2% buffer = 100%

Risk per position:
• SOL: 5% × 10% stop = 0.5% portfolio risk
• AAVE: 5% × 10% stop = 0.5% portfolio risk
• SUI: 3% × 8% stop = 0.24% portfolio risk
• Total risk if all stopped: 1.24% portfolio
```

### What the Technical Book is NOT

To be clear about boundaries:

**The Technical Book is NOT:**
- A way to override macro when you're impatient
- A license to trade every setup you see
- A replacement for the Core Book
- Active all the time
- An excuse to ignore MRI signals

**The Technical Book IS:**
- A structured outlet for clear technical opportunities
- Active only when Core is defensive AND setups exist
- Subject to strict position limits and stops
- A way to stay engaged without violating macro discipline
- Optional (you can always stay 100% cash)

### Integration with Core Book

When MRI improves and Core Book re-activates:

1. **Evaluate Technical Book positions** against Core Book criteria
2. **Positions that qualify** for Core Book can be sized up (if fundamentals support)
3. **Positions that don't qualify** should be closed or kept at Technical Book sizing with Technical Book stops
4. **Technical Book allocation shrinks** as Core Book allocation expands

The two books should never compete for the same capital. When Core is active, Technical is small or inactive.

---

## Trading Rules Framework

### Rule Classification

Rules fall into two categories based on their application:

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           TRADING RULES FRAMEWORK                                │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  UNCONDITIONAL RULES (Never Override)                                           │
│  ────────────────────────────────────                                           │
│  These rules have NO exceptions under any circumstance.                         │
│                                                                                  │
│  CONDITIONAL RULES (Context-Dependent)                                          │
│  ────────────────────────────────────                                           │
│  These rules have specific override conditions based on market context.         │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Unconditional Rules (Never Override)

**RULE #3: NEVER BUY RED RELATIVE STRENGTH**
```
If underperforming BTC on 63d AND 252d, do not buy. Period.
NO EXCEPTIONS. Better alternatives always exist.

Rationale: If an altcoin can't outperform BTC, you're taking on more
volatility for less return. Capital is always better deployed in
relative leaders.
```

**RULE #5: NEVER CHASE EXTENDED MOVES**
```
If price > 15% above 50d MA, do not initiate new position.
NO EXCEPTIONS. Wait for consolidation.

Rationale: Parabolic moves mean revert violently. The entry risk/reward
at extension is mathematically unfavorable. Patience is an edge.
```

### Conditional Rules (Context-Dependent)

**RULE #1: BELOW 200-DAY MA**
```
DEFAULT: No new longs when price < 200d MA

OVERRIDE CONDITIONS:
- Mature downtrend (>60 days below 200d MA)
- Clear bottoming structure forming
- Macro regime shifting supportive (MRI improving)

OVERRIDE ACTION:
- Tactical positions only (not core holdings)
- 50% of normal position sizing
- Tight stops (10% max drawdown from entry)
```

**RULE #2: DEATH CROSS (50d < 200d)**
```
DEFAULT: No new longs when 50d MA < 200d MA

OVERRIDE CONDITIONS:
- >60 days into death cross (mature bear)
- 50d MA slope turning positive
- Price established above 50d MA

OVERRIDE ACTION:
- Tactical positions only
- 50% of normal position sizing
- Must have positive relative strength vs BTC
```

**RULE #4: Z-RoC MOMENTUM BREAKDOWN**
```
DEFAULT: Exit when Z-RoC < -1.0

CONDITIONAL RESPONSE:
- Z-RoC < -1.0 alone: Reduce 50% minimum
- Z-RoC < -1.0 + any other rule violation: Full exit
- Z-RoC < -1.5 (severe): Full exit regardless

RE-ENTRY: When Z-RoC crosses back above 0
```

### Rule Violation Response Protocol

| Rule | Type | Violation Response | Re-entry Condition |
|------|------|-------------------|-------------------|
| #1 (Below 200d) | Conditional | Review; tactical allowed after 60d | Price > 200d for 5 days |
| #2 (Death Cross) | Conditional | No new core; tactical allowed after 60d | Golden cross confirmation |
| #3 (Red Relative) | **Unconditional** | **FULL EXIT** | RS positive on both timeframes |
| #4 (Z-RoC < -1.0) | Conditional | Reduce 50%+ | Z-RoC crosses above 0 |
| #5 (Extended >15%) | **Unconditional** | Do not enter | Pullback to within 10% of 50d |
| Multiple Rules | N/A | **FULL EXIT** | Full reset required |

### Crypto-Specific Additions

**Rule #6: Never Add to a Losing Position**
```
Dollar-cost averaging into losses is hope masquerading as strategy.
If thesis is intact and price drops: Wait for technical setup to form again.
If thesis is broken: Exit entirely.
```

**Rule #7: Respect BTC Dominance**
```
When BTC dominance is rising rapidly (>5% in 30 days):
- Reduce altcoin exposure by 50%
- Rotate to BTC or stables
- Altcoins underperform in dominance expansions
```

**Rule #8: Honor the Unlock Calendar**
```
- No new positions within 30 days of major unlock (>5% of supply)
- Reduce existing positions by 25% before major unlocks
- Token unlocks are supply shocks, not buying opportunities
```

---

## Red Flags & Warning Signs

### Financial Red Flags

| Red Flag | Threshold | Implication |
|----------|-----------|-------------|
| Dilution Rate > 500% | Token incentives 5x revenue | Unsustainable, constant sell pressure |
| Negative Earnings + Declining Revenue | Both true | Death spiral risk |
| Treasury < 6 months expenses | Low runway | Forced to sell tokens or shut down |
| Take Rate declining | QoQ decrease | Competitive pressure, margin compression |
| FDV/Circulating > 5x | High ratio | Massive future dilution coming |

### Usage Red Flags

| Red Flag | Threshold | Implication |
|----------|-----------|-------------|
| DAU declining while TVL stable | Divergence | Wash trading or whale concentration |
| Fees per user declining | QoQ decrease | Lower willingness to pay |
| Transaction count up, fees down | Divergence | Activity but no monetization |
| Developer count < 5 and declining | Low and falling | Abandoned protocol risk |

### Valuation Red Flags

| Red Flag | Threshold | Implication |
|----------|-----------|-------------|
| P/F > 1000 | Extreme | Priced for perfection, any miss = crash |
| P/S > 500 + No revenue growth | Both true | Pure speculation |
| Market cap > all sector fees | Larger than TAM | Impossible to justify |

---

## Data Sources & Vendor Infrastructure

### Primary Data Vendors

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         DATA VENDOR HIERARCHY                                    │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  TIER 1: PRIMARY SOURCES (Core Infrastructure)                                  │
│  ────────────────────────────────────────────                                   │
│  • Token Terminal - Protocol fundamentals, fees, revenue, DAU                   │
│  • Glassnode - On-chain analytics, holder distribution, flows                   │
│  • Coinglass - Derivatives data, funding, liquidations, OI                      │
│                                                                                  │
│  TIER 2: SUPPLEMENTARY SOURCES                                                  │
│  ────────────────────────────────────────────                                   │
│  • CryptoQuant - Exchange flows, miner activity                                 │
│  • DefiLlama - TVL, yields, chain comparisons                                   │
│  • Messari - Governance, tokenomics, unlocks                                    │
│                                                                                  │
│  TIER 3: VERIFICATION SOURCES                                                   │
│  ────────────────────────────────────────────                                   │
│  • CoinGecko/CMC - Price, volume, market cap                                    │
│  • Nansen - Wallet labels, smart money                                          │
│  • Arkham - Entity identification, whale tracking                               │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Vendor Assessment Matrix

| Vendor | Strength | Weakness | Use Case | Priority |
|--------|----------|----------|----------|----------|
| **Token Terminal** | Standardized protocol financials | Limited derivatives data | Fundamental analysis | **P0 - Essential** |
| **Glassnode** | Deep on-chain, BTC/ETH focus | Expensive, limited alts | Holder distribution, flows | **P0 - Essential** |
| **Coinglass** | Best derivatives aggregation | Limited fundamentals | Microstructure scoring | **P0 - Essential** |
| **CryptoQuant** | Exchange flow specialization | Overlap with Glassnode | Verification, alerts | P1 - Important |
| **DefiLlama** | Free, comprehensive TVL | No financial metrics | TVL cross-reference | P1 - Important |
| **Messari** | Governance, qualitative | Expensive | Token unlock schedules | P2 - Nice to Have |
| **Nansen** | Smart money labels | Very expensive | Whale tracking | P2 - Nice to Have |
| **Arkham** | Entity identification | Limited history | Forensic analysis | P3 - Optional |

### Data Coverage by Pillar

| Analysis Pillar | Primary Vendor | Secondary Vendor | Key Metrics |
|-----------------|---------------|------------------|-------------|
| **Fundamentals** | Token Terminal | DefiLlama | Fees, revenue, TVL, DAU |
| **Valuation** | Token Terminal | CoinGecko | P/E, P/F, FDV, float |
| **Microstructure** | Coinglass | Glassnode | Funding, OI, liquidations |
| **Holder Distribution** | Glassnode | CryptoQuant | Exchange flows, whale balance |
| **Technical** | Any price API | TradingView | OHLCV, moving averages |

---

### Token Terminal API Reference

**Base URL**: `https://api.tokenterminal.com/v2`

**Authentication**: `Authorization: Bearer {API_KEY}`

**Key Endpoints**:

```bash
# List all projects
GET /projects

# Get project metrics (time series)
GET /projects/{project_id}/metrics

# Get specific metric
GET /projects/{project_id}/metrics?metric_ids=fees,revenue,user_dau

# Filter by date range
GET /projects/{project_id}/metrics?start=2025-01-01&end=2025-12-31

# Get latest snapshot
GET /projects/{project_id}/metrics?limit=1
```

**Example: Get Ethereum Metrics**
```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
  "https://api.tokenterminal.com/v2/projects/ethereum/metrics?limit=30"
```

### Metric IDs Reference

**Market**: `market_cap_fully_diluted`, `market_cap_circulating`, `token_trading_volume`, `tokenholders`

**Financial**: `fees`, `revenue`, `take_rate`, `gross_profit`, `earnings`, `token_incentives`, `treasury`, `treasury_net`, `tvl`, `active_loans`

**Usage**: `user_dau`, `user_wau`, `user_mau`, `transaction_count`, `trading_volume`

**Valuation**: `pf_circulating`, `pf_fully_diluted`, `ps_circulating`, `ps_fully_diluted`

**Development**: `active_developers`, `code_commits`, `contracts_deployed`, `contract_deployers`

---

### Coinglass API Reference

**Base URL**: `https://open-api.coinglass.com/public/v2`

**Key Endpoints**:

```bash
# Funding rates
GET /funding

# Open interest
GET /open_interest

# Liquidation data
GET /liquidation_history

# Long/short ratio
GET /long_short_ratio
```

**Key Metrics for Microstructure Scoring**:

| Metric | Endpoint | Scoring Use |
|--------|----------|-------------|
| Funding Rate | `/funding` | Crowding detection |
| Open Interest | `/open_interest` | Leverage assessment |
| Liquidations (24h) | `/liquidation_history` | Asymmetry scoring |
| Long/Short Ratio | `/long_short_ratio` | Sentiment gauge |

---

### Glassnode API Reference

**Base URL**: `https://api.glassnode.com/v1`

**Key Endpoints**:

```bash
# Exchange flows
GET /metrics/transactions/transfers_volume_to_exchanges_sum

# Supply distribution
GET /metrics/supply/current

# Active addresses
GET /metrics/addresses/active_count

# SOPR (Spent Output Profit Ratio)
GET /metrics/indicators/sopr
```

**Key Metrics for Holder Distribution**:

| Metric | Endpoint | Scoring Use |
|--------|----------|-------------|
| Exchange Netflow | `/transfers_volume_exchanges_net` | Accumulation/distribution |
| Whale Holdings | `/supply/top_holders` | Concentration risk |
| Realized P/L | `/indicators/sopr` | Capitulation detection |
| Active Addresses | `/addresses/active_count` | Engagement trend |

---

### Data Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         DATA PIPELINE FLOW                                       │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  06:00 ET  │  RAW DATA INGESTION                                                │
│            │  └── Token Terminal, Coinglass, Glassnode API calls                │
│            │                                                                     │
│  06:15 ET  │  STAGING & VALIDATION                                              │
│            │  └── Data quality checks, outlier detection                        │
│            │                                                                     │
│  06:30 ET  │  FEATURE COMPUTATION                                               │
│            │  └── LHM ratios (Subsidy Score, Float, etc.)                       │
│            │  └── Microstructure scores                                         │
│            │                                                                     │
│  06:45 ET  │  SCORING & VERDICT                                                 │
│            │  └── 19-point scoring system                                       │
│            │  └── Verdict assignment                                            │
│            │                                                                     │
│  07:00 ET  │  OUTPUT GENERATION                                                 │
│            │  └── CSV export, dashboard refresh                                 │
│            │  └── Alert generation                                              │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### API Keys Management

API keys are stored in `/Users/bob/LHM/Working/API_KEYS.md` (not committed to repo).

**Environment Variables**:
```bash
export TOKEN_TERMINAL_API_KEY='your-key'
export GLASSNODE_API_KEY='your-key'
export COINGLASS_API_KEY='your-key'
```

---

## Implementation Checklist

### Daily Monitoring
- [ ] Fee trends for watchlist protocols
- [ ] User activity changes (DAU/MAU)
- [ ] Treasury changes (large movements = signal)
- [ ] New contract deployments in target sectors

### Weekly Analysis
- [ ] Sector fee rankings update
- [ ] Valuation ratio comparisons
- [ ] Dilution rate calculations
- [ ] Developer activity trends

### Monthly Deep Dives
- [ ] Full financial model update for top holdings
- [ ] Competitive positioning analysis
- [ ] Token unlock impact assessment
- [ ] Growth vs. value rebalancing

---

## Appendix: Sample Protocol Analysis Template

```
═══════════════════════════════════════════════════════════════
PROTOCOL FUNDAMENTAL ANALYSIS: [PROTOCOL NAME]
Sector: [SECTOR] | Date: [DATE]
═══════════════════════════════════════════════════════════════

VALUATION SNAPSHOT
─────────────────────────────────────────────────────────────
Market Cap (Circ):     $XXX.XM    │  FDV:           $XXX.XM
Price:                 $X.XX      │  FDV/Circ:      X.Xx
P/F (Circ):           XX.X       │  P/F (FDV):     XX.X
P/S (Circ):           XX.X       │  P/S (FDV):     XX.X
Sector P/F Median:    XX.X       │  Relative:      CHEAP/FAIR/RICH

FINANCIAL METRICS (30-DAY)
─────────────────────────────────────────────────────────────
Fees:                 $X.XM/mo   │  vs 90d avg:    +XX%
Revenue:              $X.XM/mo   │  vs 90d avg:    +XX%
Take Rate:            XX.X%      │  vs 90d avg:    +X.X%
Token Incentives:     $X.XM/mo   │  Dilution Rate: XXX%
Earnings:             $X.XM/mo   │  Earnings Yield: X.X%
Treasury (net):       $XX.XM     │  Runway:        XX months

USAGE METRICS
─────────────────────────────────────────────────────────────
DAU:                  XX,XXX     │  30d change:    +XX%
MAU:                  XXX,XXX    │  30d change:    +XX%
DAU/MAU (Stickiness): XX%        │  Trend:         IMPROVING/STABLE/DECLINING
TVL:                  $XXX.XM    │  30d change:    +XX%
Trading Volume:       $XX.XM/day │  30d change:    +XX%

DEVELOPMENT ACTIVITY
─────────────────────────────────────────────────────────────
Core Developers:      XX         │  30d change:    +X
Code Commits:         XXX/mo     │  Trend:         ACTIVE/DECLINING
Contracts Deployed:   X,XXX/mo   │  Ecosystem:     GROWING/STABLE

COMPETITIVE POSITION
─────────────────────────────────────────────────────────────
Sector Rank (Fees):   #X of XX
Sector Rank (TVL):    #X of XX
Sector Rank (Users):  #X of XX
Key Competitors:      [List]
Moat Assessment:      STRONG/MODERATE/WEAK

RED FLAGS
─────────────────────────────────────────────────────────────
[ ] Dilution Rate > 200%
[ ] Declining Revenue + Users
[ ] Treasury < 6mo runway
[ ] FDV/Circ > 5x
[ ] Developer exodus

THESIS
─────────────────────────────────────────────────────────────
Bull Case:
[2-3 sentences on upside scenario]

Bear Case:
[2-3 sentences on downside scenario]

Catalyst Timeline:
[Key upcoming events]

VERDICT: [STRONG BUY / BUY / HOLD / AVOID]
Conviction: [HIGH / MEDIUM / LOW]
Position Size: [X% of portfolio]

═══════════════════════════════════════════════════════════════
```

---

## Python Implementation

The framework is implemented in `lighthouse_quant.crypto`:

```python
# Installation (from LHM root)
# pip install requests pandas

# Usage
from lighthouse_quant.crypto import TokenTerminalClient, CryptoFundamentalsEngine

# 1. Direct API access
client = TokenTerminalClient()
eth_metrics = client.get_metrics('ethereum', days=30)
latest = client.get_latest_metrics('aave')

# 2. Full fundamental analysis
engine = CryptoFundamentalsEngine()

# Analyze single protocol
analysis = engine.analyze_protocol('aave')
engine.print_analysis(analysis)

# Screen multiple protocols
watchlist = ['ethereum', 'solana', 'aave', 'uniswap', 'gmx']
df = engine.screen_universe(project_ids=watchlist)

# Generate formatted report
report = engine.generate_report(
    project_ids=watchlist,
    output_path='/Users/bob/LHM/Outputs/LHM_Crypto_Fundamentals.csv'
)
print(report)
```

### Module Structure

```
lighthouse_quant/
└── crypto/
    ├── __init__.py          # Exports TokenTerminalClient, CryptoFundamentalsEngine
    ├── token_terminal.py    # Token Terminal API client
    └── fundamentals.py      # LHM analysis engine with verdict logic
```

### CLI Usage

```bash
# Analyze single protocol
python -m lighthouse_quant.crypto.fundamentals ethereum

# Run full screen (default watchlist)
python -m lighthouse_quant.crypto.fundamentals
```

### Environment Variables

```bash
# Optional: Override API key
export TOKEN_TERMINAL_API_KEY='your-api-key'
```

---

*MACRO, ILLUMINATED.*
