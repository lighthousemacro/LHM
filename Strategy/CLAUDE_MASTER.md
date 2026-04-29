# LIGHTHOUSE MACRO — MASTER CONTEXT

**LAST_SYNC:** 2026-04-29
**Version:** 5.7
**Purpose:** Single source of truth for all AI assistants (Claude, Gemini, ChatGPT)

*"MACRO, ILLUMINATED."*

---

## DATE CHECK PROTOCOL (Claude Code Only)

1. Note today's date
2. Compare to LAST_SYNC above
3. If LAST_SYNC is NOT today or yesterday: say "Context is stale (last sync: [DATE]). Run `lhm-sync` before we proceed." and STOP until user confirms

---

# SECTION 0: MEMORY SUMMARY

*Source: Claude.ai memory export. Regenerated nightly. Does not include projects, which have their own specific memory.*

## Work context

Bob runs Lighthouse Macro (LHM), a Substack-based macro research publication with a tiered content structure: Notes (free), Beacon, Beam, and Horizon (paid). He operates a proprietary analytical system built around composite indices (LFI, LCI, CLG, MRI, SPI, MSI), pillar-based scanning logic, and a database (Lighthouse_Master.db), with Claude integrated deeply into his publishing and research pipeline via a master reference at `/Users/bob/LHM/CLAUDE_MASTER.md`. Mercor is active with two contracts not yet started: econ chart work at $75/hr and wealth & asset management work pending at $150/hr (requires ~90 min onboarding doc completion).

## Personal context

Bob is NYC-based, a former D1 athlete who functions best with external structure, and thrives on intellectual diversity (ADHD as a superpower; bored by repetition). He has two sisters — Cayley (older, NYC) and Arden (younger, Denver) — and a close friend named Asher. Bob currently lives at Cayley's place with plans to move out; hardware plans (Mac Pro M5 + Mac mini M5 bundle) and the move are anchored to revenue conversion from active prospects.

## Top of mind

The paid tier launched publicly around the week of Apr 13–20 at $320/yr (36% off standard), with five external paid subs signed on Apr 21. The Two Economies Beacon (Apr 20) generated the most meaningful external validation to date — Tim Pierotti restacked and posted publicly, Nixon Apple reposted on X, Leon Liao left a substantive comment, and mondayswife (PhD research economist) engaged. A Tim Pierotti commercial ladder is taking shape: (1) solo WealthVest podcast (free, near-term), (2) paid deck, (3) monthly roundtable with Aahan (Prometheus) and ideally Bob Elliott, (4) potential OCIO seat at Tim's new RIA — the anchor piece if real, with a possible call after his Apr 29 RIA meeting. The Tania Reif engagement closed Apr 28 with no revenue after 6 months, 3 calls, and 11 deliverables; four lessons extracted around conversion signals, soft-no interpretation, trial kill dates, and proposal discipline (see Working Principles). Bob has also been building out the lhm-publish orchestrator skill to unify six specialist pipeline skills, and an ad hoc subscriber analytics dashboard (HTML/React/Recharts) from Substack CSV exports.

## Brief history

### Recent months

The Diagnostic Dozen series (all 12 LHM pillars) completed Apr 12, followed by a transition Beacon ("The Foundation Is Set. Now We Build.") on Apr 14 that framed the pivot to the paid-tier launch. The March 2026 retail sales Beam was drafted and published with database verification via Claude Code; a data discrepancy (web source vs. Lighthouse_Master.db) was caught and corrected before publication. The piece ran ~740 words across six locked sections with five embedded charts, using Substack's one-free-article-per-reader feature. The analytical frame centered on the Two Economies thesis: the 1.66% headline print driven by gasoline pass-through (Iran conflict), tax refund timing, and wealth-effect goods spending; the CCI decomposition gives nominal retail sales zero weight, Real PCE 25%, and the control group 15%.

Infrastructure decisions addressed: Morning Brief and Pulse Check scheduled triggers were flagged for manual deletion at claude.ai/code/scheduled; meaningful scout/scan automation remains blocked until an always-on Mac mini enables the bridge environment (env_019dok5DYQfwpL611fsNN6hk). Pine Script files (lhm_relative_strength.pine, lhm_z_roc.pine) were created at `/Users/bob/LHM/Scripts/tradingview/` and a TradingView section was appended to `/Users/bob/LHM/Brand/chart-styling.md`; CLAUDE_MASTER.md Section 10 still needs a path update to the new tradingview directory.

Active relationship updates from this period: Theo Advisors MOU signed with James Moton as active contact (Christopher King no longer primary); OpenBB / Didier Lopes active on pillar dashboard builds; Permutable AI collaboration scoping underway; Pascal Hügli podcast published with LHM featured; Tim Pierotti podcast ("The Weekly Bull & Bear") published. Founding member locked lifetime rates: Michael Zhang $300, Josh Giordano $400, Ryan Salah $400. Friends-and-family paid cohort (exclude from conversion analysis): murdakes (good friend, $320 supporter), Asher (comp/support).

Pace University MS Economic Analysis & Data Science application accepted to Accelerated Admission Day (Mar 20).

### Earlier context

Bob was building out LHM's structured repository and brand system, including the 23/89/BB named-color palette (Ocean, Sky, Venus, Sea, Starboard, Port, Dusk, Doldrums) and charting conventions (3-panel stack: Price, RS, Z-RoC; hollow candles; MA hierarchy; RS benchmark auto-detect). The Diagnostic Dozen series was in active publication across this window. Regime monitoring focused on the shift from RRP to reserves vs. LCLOR, EFFR-IORB, SOFR-IORB as the relevant plumbing signals.

### Long-term background

Bob's research identity is built around framework-first macro analysis — process over takes — and a belief that most macro commentary fails to discuss process. The LHM composite index system (LFI, LCI, CLG, MRI, SPI, MSI) and pillar-based scanning logic are the stable structural layer documented in CLAUDE_MASTER.md. He has run model portfolios benchmarked against SPY and maintains an active network across institutional macro, DeFi/crypto research, and financial media.

## Working principles (always active)

- **Voice:** "We" voice. Bob varies sentence cadence deliberately — don't collapse rhythm into uniform short sentences. No emdashes.
- **"Not X, it's Y" construction:** Use sparingly and deliberately. The vocabulary (e.g., "camouflage") is fine; the structural pattern is the tell. Not a default rhetorical move.
- **Data:** Never fabricate or approximate. Real sourced data only, always.
- **Breadth thrust:** Bob uses both 20-day and 50-day as separate indicators. Don't flag the 50-day as wrong — the 20-day canonical in master context is not exclusive. Real flag is internal threshold inconsistency within a single piece.
- **Gmail drafts via API:** Omit signature block entirely. Use "Best,\nBob" as placeholder if needed; HTML signature auto-appends on send.
- **Paid pricing:** Public. $320/yr launch rate is live. The old "don't name pricing without green light" rule is obsolete.
- **Founding member rates (locked for life, 3 external):** Michael Zhang $300, Josh Giordano $400, Ryan Salah $400. New comps (e.g., Tim Pierotti) are gifts, not additions to this tier unless Bob says so.
- **Tania lessons (Apr 28):** (1) Engagement ≠ conversion signal; cleanest predictor is whether they paid the public Substack tier within 30 days of being told it exists. (2) Soft no's with "when ready" or "I'll reach out" are current no's. Max 2 warm follow-ups, then back-burner until prospect re-initiates with explicit budget reference. (3) Trials need explicit kill dates and a defined deliverable count. (4) The proposal is the SOW — going pricing-live with a champion produces free deliverables.
- **Tim Pierotti:** Comp a founding sub as thank-you. If paid chart work materializes, treat as a separate consulting engagement with clear rates.
- **Don't tell Bob what to do** unless he explicitly asks for a recommendation on action. Answer the question asked. Stop there.
- **Tegus:** Not an active platform. Do not reference.
- **Personal context:** Carry forward quietly. Don't surface unprompted.

---

# SECTION 1: CORE IDENTITY

## Who Bob Is

**Robert Brown Sheehan, CFA, CMT** (goes by Bob)
Founder & Chief Investment Officer, Lighthouse Macro, LLC (Delaware)

### Background

- Former VP, Data & Analytics at EquiLend (authored Short Squeeze Score articles, built proprietary indices)
- Former Associate PM at Bank of America Private Bank ($4.5B multi-asset AUM; SGS equity sleeve ~$1.2B at peak, 2.35 Sortino, 103% upside capture, 76% downside capture vs S&P 500)
- Former Senior Research Analyst at Strom Capital Management
- Former at Trahan Macro Research
- CFA, CMT, BrainStation Data Science Diploma
- Providence College, Division 1 lacrosse

### Personal Context

- ADHD as a superpower: thrives on intellectual diversity across macro domains, bored by repetitive focus
- Code-first approach: Python-driven frameworks, never approximates or fabricates data
- "Lighthouse" was the name of Bob's house in college where he first studied finance/economics

### Contact

| Type | Value |
|------|-------|
| Website | LighthouseMacro.com |
| Email | bob@lighthousemacro.com |
| Advisory | advisory@lighthousemacro.com |
| Research | research@lighthousemacro.com |
| Phone | +1 (929) 238-9397 |
| Twitter/X | @LHMacro |
| Bank | Mercury |

### Document Footer

Single-line footer with three hyperlinks:

```
Lighthouse Macro | Research | @LHMacro
```

- "Lighthouse Macro" → https://lighthousemacro.com
- "Research" → https://research.lighthousemacro.com
- "@LHMacro" → https://x.com/LHMacro

Hyperlinks render in Ocean (#2389BB) in both PDF and HTML.

---

## Positioning

**Tagline:** "MACRO, ILLUMINATED."

**Mission:** Institutional-grade macro research serving hedge funds, CIOs, central banks, and allocators

**Dual-Track Business Model:**
- Track 1 (Market Positioning): Serves allocators and hedge funds
- Track 2 (Economic Intelligence): Serves small businesses and regional institutions
- Same research, different applications

**Philosophy:** "Flows > Stocks. We track labor market flows, Fed plumbing dynamics, and credit conditions systematically. Concentrated positions. Conviction-weighted sizing."

| Attribute | Lighthouse | Consensus |
|---|---|---|
| Signal Source | 12 Macro Pillars, Proprietary Indicators | Headlines, lagging data |
| Framework | Three-Engine System | Single-dimensional |
| Position Sizing | Conviction-weighted (7-20%) | Equal-weighted |
| Concentration | 3-10 high-conviction positions | 30+ marginal |
| Cash | Active position (30-100% valid) | Residual drag |
| Risk | Dual stops (thesis + price) | Single trailing stop |
| Timeframe | 3-6 month tactical core | Arbitrary calendar |

---

# SECTION 2: THE DIAGNOSTIC DOZEN (12 Pillars)

## Nomenclature

- **Pillars** = inputs (12 diagnostic categories)
- **Engines** = processors (3 synthesis layers)
- Correct phrasing: "Twelve pillars across three engines."

## Three-Engine Framework

```
+---------------------------------------------------------------------------------+
|                              12 MACRO PILLARS                                    |
|                          (The Diagnostic Dozen)                                  |
+------------------------+-------------------------+-------------------------------+
|   MACRO DYNAMICS       |   MONETARY MECHANICS    |      MARKET STRUCTURE         |
|   (Pillars 1-7)        |   (Pillars 8-10)        |      (Pillars 11-12)          |
+------------------------+-------------------------+-------------------------------+
| 1. Labor    -> LPI,LFI | 8. Government -> GCI-Gov| 11. Structure -> MSI, SBD     |
| 2. Prices   -> PCI     | 9. Financial  -> FCI,CLG| 12. Sentiment -> SPI, SSD     |
| 3. Growth   -> GCI     | 10. Plumbing  -> LCI    |                               |
| 4. Housing  -> HCI     |                         |                               |
| 5. Consumer -> CCI     |                         |                               |
| 6. Business -> BCI     |                         |                               |
| 7. Trade    -> TCI     |                         |                               |
+------------------------+-------------------------+-------------------------------+
                                       |
                               MRI (Master Composite)
                                       |
                           TRADING STRATEGY EXECUTION
```

## Framework Outputs (Three Distinct Layers)

1. **Recession Probability:** 6-12 month forward probability
2. **Warning System:** Threshold alerts
3. **MRI (Master Risk Index):** Regime classification

## Pillar Summary

| Pillar | Index | Key Insight | Lead Time |
|---|---|---|---|
| 1. Labor | LPI, LFI | Quits rate = truth serum. Flows lead, stocks lag. | Leading |
| 2. Prices | PCI | Last mile sticky, shelter lags | 12-18 months (shelter) |
| 3. Growth | GCI | Second derivative matters | 2-4 months |
| 4. Housing | HCI | Frozen equilibrium, rate sensitive | 6-9 months |
| 5. Consumer | CCI | 68% of GDP, lagging. "The Last Domino." | 1-3 months |
| 6. Business | BCI | Capex = forward commitment | 4-8 months |
| 7. Trade | TCI | Dollar/tariff pass-through | 3-6 months |
| 8. Government | GCI-Gov | Fiscal dominance, term premium | Structural |
| 9. Financial | FCI, CLG | Credit spreads lead defaults | 6-9 months |
| 10. Plumbing | LCI | RRP exhaustion = no buffer | 1-4 weeks |
| 11. Structure | MSI, SBD | Breadth divergence = distribution | 2-4 months |
| 12. Sentiment | SPI, SSD | Contrarian at extremes only | Days to weeks |

---

# SECTION 3: COMPOSITES, FORMULAS & THRESHOLDS

## Macro Risk Index (MRI) v2.0

The master composite synthesizing all 12 pillars:

```
MRI = 0.13*(-LPI) + 0.08*PCI + 0.13*(-GCI) + 0.06*(-HCI)
    + 0.08*(-CCI) + 0.08*(-BCI) + 0.05*(-TCI) + 0.08*GCI-Gov
    + 0.04*(-FCI) + 0.08*(-LCI) + 0.12*(-MSI) + 0.07*(-SPI)
```

| MRI Range | Regime | Equity Allocation | Multiplier |
|---|---|---|---|
| < -0.5 | Low Risk | 65-70% | 1.2x |
| -0.5 to +0.5 | Neutral | 55-60% | 1.0x |
| +0.5 to +1.0 | Elevated | 45-55% | 0.6x |
| +1.0 to +1.5 | High Risk | 35-45% | 0.3x |
| > +1.5 | Crisis | 25-35% | 0.0x |

## Component Formulas

**Labor Fragility Index (LFI):**
```
LFI = 0.35*z(LongTermUnemp%) + 0.35*z(-Quits) + 0.30*z(-Hires/Quits)
```

**Liquidity Cushion Index (LCI):**
```
LCI = 0.25*z(Reserves_vs_LCLOR) + 0.20*z(-EFFR_IORB) + 0.15*z(-SOFR_IORB)
    + 0.15*z(RRP) + 0.10*z(-GCF_TPR) + 0.10*z(-DealerPos) + 0.05*z(-EUR_USD_Basis)
```

**Credit-Labor Gap (CLG):**
```
CLG = z(HY_OAS) - z(LFI)
```
CLG < -1.0: Credit too tight for labor reality

**Market Structure Index (MSI):**
```
MSI = 0.15*z(Price_vs_200d) + 0.10*z(Price_vs_50d) + 0.10*z(50d_Slope)
    + 0.10*z(20d_Slope) + 0.12*z(Z_RoC_63d) + 0.10*z(%>50d_MA)
    + 0.08*z(%>20d_MA) + 0.08*z(%>200d_MA) + 0.07*z(NH_NL_20d)
    + 0.05*z(AD_Slope) + 0.05*z(McClellan_Sum)
```

**Sentiment & Positioning Index (SPI):**
```
SPI = 0.20*z(Put_Call_10d) + 0.15*z(VIX_vs_50d) + 0.15*z(-AAII_Bull_Bear)
    + 0.15*z(-NAAIM) + 0.10*z(-II_Bull_Bear) + 0.10*z(-ETF_Flows_20d)
    + 0.10*z(VIX_Backwardation) + 0.05*z(MMF_Assets_YoY)
```
High SPI = Fear = Contrarian Bullish

**Structure-Breadth Divergence (SBD):**
```
SBD = z(Price_vs_200d) - z(%_Stocks_>_50d_MA)
```
SBD > +1.0: Distribution warning (generals without soldiers)

**Sentiment-Structure Divergence (SSD):**
```
SSD = z(SPI) + z(MSI)
```
SSD > +1.5: Capitulation low forming. SSD < -1.5: Blow-off top risk.

## Consumer Conditions Index (CCI) — 7-Component (Updated Feb 2026)

| Component | Weight | 12M Fwd PCE Corr |
|---|---|---|
| Real PCE YoY | 0.25 | -0.817 |
| Saving Rate | 0.20 | +0.504 |
| Retail Sales Control (RSXFS) | 0.15 | -0.498 |
| CC Delinquency (inv) | 0.10 | -0.114 |
| UMich Sentiment | 0.10 | -0.162 |
| Real DPI YoY | 0.10 | +0.260 |
| DSR (inv) | 0.10 | +0.033 |

## Crypto Liquidity Impulse (CLI)

Three-channel liquidity composite measuring how fast global liquidity transmits into crypto.

**Architecture (3 Tiers, 8 Components):**
- Tier 1: Macro Liquidity Tide (40%) — Global M2 Momentum, DXY 63-Day RoC
- Tier 2: US Plumbing Mechanics (35%) — WALCL, TGA, RRP, SOFR-IORB, HY OAS (inv)
- Tier 3: Crypto-Native Transmission (25%) — Stablecoin supply momentum, BTC ETF flows (20d), Exchange stablecoin reserves

Leverage Regime Filter applied multiplicatively (perpetual futures funding rates). Captures the ~17% of time when crypto positioning dynamics override macro liquidity.

Positive CLI = expanding liquidity transmission. Negative = contracting.

**Key empirical findings:**
- Net Liquidity expanding AND dollar weakening: BTC +34.1% next quarter, 84.7% hit rate
- Both bearish: +0.9%, 41.7% hit rate
- Q5-Q1 quintile spread: +22.1%, t-stat 15.6

**Disclosure:** Architecture, components, and empirical results are public. Exact weights, z-score methodology, and regime filter calibration are proprietary.

**Known drift (flagged 2026-04-22):** The chart pipeline at `/Users/bob/LHM/Scripts/backtest/cli_final.py` renders a 4-component v5 subset (Dollar / TOTRESNS-WALCL ratio + its 63D RoC / Stablecoin-BTC ratio) rather than the published 8-component architecture above. This was a Feb 2026 robustness-test script that became the default chart source by path dependency. The 8-component version outperforms it on the data available when published; the 4-component subset showed a higher Q5-Q1 spread in the Feb pass but excluded M2, Net Liquidity, funding stress, ETF flows, exchange reserves, and the leverage regime filter. Needs a rebuild: reconstruct the published 8-component CLI as the production composite, move `cli_final.py` into an `Archive/` or `_deprecated_` path, and repoint `cli_chart_data.csv` at the rebuilt version.

## Key Thresholds

### Labor
| Indicator | Threshold | Signal |
|---|---|---|
| Quits Rate | <2.0% | Pre-recessionary |
| LFI | >+0.5 | Fragility elevated |
| Temp Help YoY | <-3% | Recession signal |
| Long-Term Unemployed | >22% | Structural fragility |

### Liquidity
| Indicator | Threshold | Signal |
|---|---|---|
| RRP | <$200B | Buffer exhausted |
| EFFR-IORB | >+8 bps | Acute funding stress |
| LCI | <-0.5 | Scarce regime |
| Reserves vs LCLOR | <$300B | Scarcity threshold |

### Credit
| Indicator | Threshold | Signal |
|---|---|---|
| HY OAS | <300 bps | Complacent |
| CLG | <-1.0 | Credit ignoring fundamentals |

### Market Structure
| Indicator | Threshold | Signal |
|---|---|---|
| Price vs 200d | <0% | Below trend |
| % > 20d MA | <25% / >80% | Washed / Crowded |
| % > 20d MA | 30% to 70% in 10d | Breadth thrust |
| % > 50d MA | <35% / >85% | Washed / Crowded |
| Z-RoC | <-1.0 | Momentum broken |
| MSI | <-1.0 | Structure broken |

### Sentiment
| Indicator | Threshold | Signal |
|---|---|---|
| AAII Bull-Bear | >+30% / <-20% | Euphoria / Capitulation |
| NAAIM | >100% | Fully invested (sell) |
| SPI | >+1.5 / <-1.0 | Extreme fear (buy) / Euphoria (sell) |

---

# SECTION 4: TRADING & POSITION SIZING

## Engine Convergence Matrix

| Macro | Monetary | Structure/Sentiment | Action |
|---|---|---|---|
| Bullish | Supportive | Confirming + Fear | **Maximum conviction long** |
| Bullish | Supportive | Confirming + Neutral | Normal position |
| Bullish | Supportive | Diverging | Reduce exposure |
| Bullish | Restrictive | Any | No new longs |
| Bearish | Any | Confirming | Maximum defensive |
| Bearish | Supportive | Diverging + Extreme Fear | Tactical exhaustion only |

## 4 Signature Synthesis Chains

1. **Labor to Credit to Equity:** Labor flows (Quits) deteriorate first, credit spreads widen, equity multiples compress. Watch "Silent Deceleration."
2. **Collateral Fragility (Crypto-Treasury Loop):** Crypto is marginal buyer of Treasuries via stablecoins. Volatility forces liquidation.
3. **Plumbing to Asset Prices:** RRP drain, reserve scarcity, dealer SLR constraints, repo spread widening, Treasury auction tails.
4. **Fiscal Dominance (2026 Theme):** Term premium is the "Honest Signal." Must reprice to ~150bps for structural deficits in post-QT world.

## Pillar-to-Trade Mapping

| Signal | Expression | Asset |
|---|---|---|
| LFI > +0.8 | Reduce cyclical equity | Equities |
| LCI < -0.5 | Reduce gross, add cash | All |
| CLG < -1.0 | Credit protection (HY short) | Credit |
| PCI > +1.0 | Short duration, inflation hedges | Rates |
| GCI-Gov > +1.0 | Steepener trades | Rates |
| BCI < -0.5 | Underweight small vs large | Equities |
| HCI < -0.5 | Avoid homebuilders | Equities |
| MSI < -0.5 | Reduce gross exposure | All |
| SPI > +1.5 | Contrarian fade | All |

## Two Books Framework

### Core Book (50-100% of capital)
- Macro + fundamental + technical driven, LONG OR SHORT
- MRI regime multiplier applies to sizing
- 3-6 month catalyst horizon, up to 20% per position
- Can go 100% cash

### Technical Overlay Book (0-50% of capital)
- Pure technical (trend + momentum + relative strength), LONG OR SHORT
- Activated when Core Book defensive (MRI > +1.0)
- Max 10% longs, 5% shorts per position
- Tighter stops (10% longs, 8% shorts)

### Position Sizing

```
Position Size = Base Weight * Conviction Multiplier * Regime Multiplier
```

| Tier | Score | Weight |
|---|---|---|
| Tier 1 | 16-19 pts | 20% |
| Tier 2 | 12-15 pts | 12% |
| Tier 3 | 8-11 pts | 7% |
| Tier 4 | <8 pts | 0% (avoid) |

### Dual Stop System (Core Book)

Every position has TWO stops. Whichever triggers first.

**Thesis Stop:** Revenue declines 3 consecutive quarters, key indicator crosses invalidation, macro regime shift.

**Price Stop:** Price closes below 200d MA (longs), Z-RoC < -1.0, or 15% drawdown from entry.

### Technical Overlay Scoring (12-Point System)

3 components, 4 points each. Minimum 8/12 to enter.

| Component | Points | Measures |
|---|---|---|
| Trend Structure | 0-4 | Price vs 50d vs 200d alignment + slope |
| Momentum (Z-RoC) | 0-4 | Direction, magnitude, trajectory |
| Relative Strength | 0-4 | vs BTC/SPX (multiple timeframes + slope) |

### Perfect Setup Requirements

4+ of 6 elements: trend alignment, momentum (Z-RoC), technical structure, relative strength, macro catalyst, risk/reward >2.5:1

### Technical Guardrails

Signals we monitor, not rules we obey blindly. At extremes, they demand attention.

| Signal | Measures | Context |
|---|---|---|
| Price vs 200d MA | Primary trend | Below = higher bar for longs |
| 50d vs 200d MA | Trend structure | Death cross = weakening, duration matters |
| Relative Strength | vs benchmark | Persistent underperformance is a flag |
| Z-RoC (63d) | Momentum | Extremes (<-1.5 or >+1.5) significant |
| Distance from 50d | Extension | >15% stretched = poor entry |

**Philosophy:** When a signal is screaming, listen. When it's whispering, weigh it.

---

# SECTION 5: ASSET CLASS COVERAGE

| Asset Class | Instruments | Key Pillar Links |
|---|---|---|
| Equities | ETFs (SPY, QQQ, sectors), single stocks | MSI, SPI, GCI, LPI |
| Rates | Duration ETFs (TLT, IEF, SHY), TIPS | PCI, LCI, GCI-Gov |
| Credit | IG, HY, loans (LQD, HYG, BKLN) | FCI, CLG, LCI |
| Commodities | Gold, energy, metals (GLD, XLE, CPER) | PCI, GCI, TCI |
| Currencies | Dollar, majors, EM (UUP, FXE, CEW) | TCI, GCI, MRI |
| Crypto | BTC, ETH, alts | LCI, MRI, CLI |

---

# SECTION 6: COMMUNICATION & VOICE

## Voice & Tone: The 80/20 Rule

- **80% Institutional Rigor:** CFA/CMT credibility, quantitative precision
- **20% Personality:** Dry observations, skepticism of consensus, wit when natural
- **0% Forced Flair:** No manufactured catchphrases

**Core voice:** Macroeconomist who can talk to traders and teach civilians. Confident but humble. Data-backed, explicitly wrong-able. Dry wit over sensationalism. Simplify without dumbing down.

**The "We" Frame:** Speak as Lighthouse Macro. "We're seeing stress" not "The data shows stress."

**"Strong views weakly held"** with explicit invalidation criteria. If [X] happens, the bearish case breaks. This isn't hedging. It's intellectual honesty.

### What Good Looks Like

- "The labor data softened. Again."
- "Spreads are pricing one story. Labor is telling another."
- "The buffer is gone. The runway is short."
- "The Fed's in a box. They just haven't admitted it yet."

### What to Avoid

- Forced metaphors, trying to make every observation "quotable"
- Excessive nautical references beyond natural brand vocabulary
- **Emdashes. Never. Use commas, periods, colons, parentheses, or ellipses.**
- Semicolons (use commas)
- AI-sounding transitions, over-excited adjectives
- "Cautiously optimistic," "geopolitical uncertainty," "complex constellation of factors"
- "In our view," "going forward," "at the end of the day," "it is important to note"

### Sign-Offs

- **CTA button (all readers):** "Don't navigate in the dark. Subscribe." (Ocean `#2389BB` button, white italic Montserrat Bold)
- **Existing subscribers (Beacon/Horizon only):** "That's our view from the Watch. We'll keep the light on..."
- Don't overuse the formal sign-off. It loses impact.

### Social Media Promotional Template (Framework-First)

> We tracked [X] indicators across [Y] categories to build our [Pillar Name] assessment. [One sentence on what the pillar measures]. We include explicit invalidation criteria for both directions because the framework can be wrong.
>
> Here's what the data says, what it doesn't say, and what would change our mind.

Framework first. Depth first.

### Bob's Writing Cadence

- Skeptical of consensus, allergic to vague platitudes
- Lets data talk, then adds a dry observation
- Short sentences control rhythm
- Casual precision with occasional slang
- Emoji usage: sparse, purposeful (flame for hot takes, eyes for "look at this")

---

# SECTION 7: BRAND SYSTEM

## Signature 8-Color Palette (23/89/BB Mnemonic)

Every color contains some combination of 23, 89, and BB. The brand palette is a signature.

| Name | Hex | Mnemonic | Usage |
|------|-----|----------|-------|
| **Ocean** | `#2389BB` | 23+89+BB | Primary brand, headers, borders, chart primary |
| **Dusk** | `#FF6723` | 23 | Secondary series, accent bar, CTA buttons |
| **Sky** | `#23BBFF` | 23+BB | Lighter blue for secondary chart lines |
| **Venus** | `#FF2389` | 23+89 | 2% target lines, critical alerts |
| **Sea** | `#00BB89` | BB+89 | Tertiary series, on-target regime bands |
| **Doldrums** | `#898989` | 89+89 | Axis spines, labels, secondary text |
| **Starboard** | `#238923` | 23+89 | Bullish regime, professional green |
| **Port** | `#892323` | 89+23 | Bearish regime, crisis bands |

### Reference Colors (Not in Mnemonic)

| Name | Hex | Usage |
|------|-----|-------|
| **Fog** | `#D1D1D1` | Zero lines, ghost reference lines |

### Accent Bar

- Ocean `#2389BB` for 2/3 width (left)
- Dusk `#FF6723` for 1/3 width (right)
- Height: 4-6px documents, scalable for presentations

## Typography

| Element | Font | Weight | Size |
|---|---|---|---|
| Document Title | Montserrat | Bold | 28-36pt |
| Section Headers | Montserrat | Bold | 18-24pt |
| Subheaders | Montserrat | SemiBold | 14-16pt |
| Body Text | Inter | Regular | 11-12pt |
| Captions | Inter | Regular | 9-10pt |
| Data/Tables | Source Code Pro | Regular | 10-11pt |

## Logo & Watermarks

- **Logo:** White lighthouse on ocean blue background. Top-left, 40px margin.
- **Chart Icon:** `Brand/icon_transparent_128.png` (128x290px, Ocean blue, transparent bg). Placed top-left on all charts next to "LIGHTHOUSE MACRO" text.
- **Banner:** Horizontal lockup with icon, text, tagline, accent bar.
- **Watermarks:** "LIGHTHOUSE MACRO" top-left, "MACRO, ILLUMINATED." bottom-right. Montserrat Bold, Ocean at 15-20% opacity.

---

# SECTION 8: CHART STYLING

## Core Rules

- **White theme is primary.** Generate white theme for all publications (Substack, PDF, social). Dark theme is optional secondary.
- No gridlines. All four spines visible at 0.5pt.
- Right axis is primary. No tick marks.
- Spine color: Doldrums `#898989` (both themes). Dark theme may use `#1e3350` if contrast needed.
- Every chart: `border: 4.0pt solid #2389BB`
- DPI 200, bbox_inches='tight', pad_inches=0.025

## Axis Configuration

**Dual-Axis:** RHS = Primary (Ocean), LHS = Secondary (Dusk). Both get last-value pills.

**Single-Axis:** Ticks on RHS, RHS pill only.

**X-Axis Padding:** 30-day left, 180-day right (for pills).

## Data Handling

- Always `dropna()`. Forward-fill quarterly to daily.
- Smooth volatile series with 3-month MA. Don't smooth already-smoothed measures.

## Reference Lines

| Type | Color | Style |
|---|---|---|
| Zero line | Fog `#D1D1D1` | Dashed |
| 2% Target | Venus `#FF2389` | Solid |
| 3% Danger | Sea `#00BB89` | Solid |

## Recession Shading

White theme (primary): gray, alpha 0.12. Dark theme (optional): white, alpha 0.06.

## Chart Layout

- 1 column: full width
- 2 columns: 48% each, 4% gutter
- 4 panels: 48% x 48% grid
- Caption: centered below, Inter 9-10pt, "Figure N: Description"

## Helper Functions

```python
new_fig()               # Create branded figure
style_ax()              # Style axis with theme
style_dual_ax()         # Dual-axis chart
style_single_ax()       # Single-axis chart
set_xlim_to_data()      # X-axis range with padding
brand_fig()             # Watermarks, date, accent bar, source
add_last_value_label()  # Pill labels on axes
add_annotation_box()    # Commentary box
add_recessions()        # NBER recession shading
legend_style()          # Themed legend
```

---

# SECTION 9: CONTENT CADENCE

## Publication Schedule

| Type | Frequency | Length | Format |
|---|---|---|---|
| **Beacon** | Weekly (Sundays) | 3-4k words | Long-form analysis |
| **Beam** | 2x/week | 750 words + 5 charts | Multi-chart insight |
| **Notes** | 3x/week | 150 words + 1 chart (free) | Substack Notes / social |
| **Chartbook** | Bi-weekly (Fridays) | 50-75 charts | Visual compilation |
| **Horizon** | Monthly (1st Monday) | Forward outlook | Strategic perspective |

## Diagnostic Dozen Educational Series

One post per pillar. 3,000-3,500 words, 8-12 charts each.

Structure: Hook, Core Insight, What to Watch, Indicators (7-9 subsections with charts), Consensus Trap, Where We Are Now, How to Track, Invalidation Criteria, Bottom Line

**Published (all 12 as of April 14, 2026):**
1. "Labor: The Source Code" (Jan 27) → `research.lighthousemacro.com/p/labor-the-source-code`
2. "Prices: The Transmission Belt" (Feb 2) → `/p/prices-the-transmission-belt`
3. "Growth: The Second Derivative" (Feb 5) → `/p/growth-the-second-derivative`
4. "Consumer: The Last Domino" (Feb 11) → `/p/consumer-the-last-domino`
5. "Housing: The Collateral Engine" (Feb 16) → `/p/housing-the-collateral-engine`
6. "Business: The Forward Commitment" → `/p/business-the-forward-commitment`
7. "Trade: The Pipeline" → `/p/trade-the-pipeline`
8. "Government: The Fiscal Overhang" → `/p/government-the-fiscal-overhang`
9. "Financial: The Cascade" → `/p/financial-the-cascade`
10. "Plumbing: The Invisible Infrastructure" → `/p/plumbing-the-invisible-infrastructure`
11. "Market Structure: The Weight of Evidence" (Apr 10) → `/p/market-structure-the-weight-of-evidence`
12. "Sentiment & Positioning: The Contrarian Edge" → `/p/sentiment-and-positioning-the-contrarian-216` (note: Substack slug collision suffix)

Note: Pillar numbers may not match post numbers (Consumer is Pillar 5 but Post 4). Slug pattern is `{pillar}-the-{subtitle}` with a few exceptions noted above.

## Free vs Paid Content

**Free:** Pillar explanations, framework mechanics, historical examples, threshold definitions. No real-time positioning.

**Paid:** Real-time indicator readings, position sizing, trade setups, forward outlook, proprietary composites.

## Substack Tags (Max 5)

Economics, Finance, Macro, Investing, Markets

## Document Templates (Summary)

- **Beacon:** Banner, Executive Summary, Macro Context, Monetary Dynamics, Market Technicals, Conclusion, Sign-off. Structure is skeleton + mandatory sections (Exec Summary, Framework Synthesis, Invalidation Criteria, Bottom Line), with flexible body analysis sections.
- **Beam:** **LOCKED 6-section template (April 14, 2026).** Every Beam follows the same six questions in the same order: (1) The Setup, (2) The Data, (3) The Mechanism, (4) What Consensus Is Missing, (5) What Would Change Our Mind, (6) The So-What. Target 700-800 words, 5 charts. Section headers can be rewritten for punch but the question order is fixed. Full spec in `/Users/bob/LHM/Strategy/BEAM_TEMPLATE.md`.
- **Notes:** Single chart + 150 words (social/Substack Notes)
- **Chartbook:** Cover, TOC, Sections (Macro, Labor, Monetary, Treasury, Credit, Equity Internals, Cross-Asset, Global/EM), 2-4 charts per page
- **Horizon:** State of Play, Key Themes, Risk Matrix, Watchlist, Tactical Implications. NO fixed body template, by design — Horizon's monthly thematic work needs flex room.

---

# SECTION 10: DATA INFRASTRUCTURE

## Lighthouse Macro Master Database

- **Path:** `/Users/bob/LHM/Data/databases/Lighthouse_Master.db` (SQLite)
- **Pipeline:** `/Users/bob/LHM/Scripts/data_pipeline/lighthouse_master_db.py`
- **Config:** `/Users/bob/LHM/Scripts/data_pipeline/lighthouse/config.py`
- **Sources:** FRED, BLS, BEA, NY Fed, OFR, Yahoo, AAII, Zillow, TradingView
- **Stats:** ~1,400+ series, ~2.5M+ observations

## Pipeline

```
RAW DATA -> STAGING -> CURATED -> FEATURES -> INDICATORS -> OUTPUTS
```

Schedule: 06:00 ET data refresh, 07:00 ET indicator computation, 07:15 ET alerts.

## Data Sources

| Source | Type | Access |
|---|---|---|
| FRED | Primary macro/financial | Free API |
| BLS, BEA, Census | Government releases | Free |
| NY Fed, OFR, TreasuryDirect | Fed/Treasury plumbing | Free |
| Yahoo Finance | Market prices | Free |
| AAII | Sentiment | Free |
| Zillow | Housing (ZHVI, ZORI) | Free CSV |
| TradingView | NAHB HMI, MBA data | Subscription |
| DefiLlama | Crypto TVL, stablecoins | Free |
| CoinGecko | Crypto prices | Free (30/min) |

## TradingView Pine Script Indicators (Built Feb 2026)

- **Relative Strength Indicator:** Auto-detects benchmark by asset type. Color-coded hierarchical MA structure.
- **LHM Z-RoC:** Dual-timeframe momentum (21d tactical, 63d regime). Three colors: Ocean (neutral), Sky (long bias), Venus (short bias). Regime-aware. Hidden signal lines, divergence detection.

## Critical Data Rules

- Never fabricate or approximate data. Code-first = reproducibility first.
- Never use synthetic or illustrative data in charts.
- PYTHONPATH: `/Users/bob/LHM`

## Repository Structure

```
/Users/bob/LHM/
  Strategy/         # Pillar docs, CLAUDE_MASTER.md, frameworks
  Brand/            # brand-guide.md, chart-styling.md, templates.md
  Scripts/          # Chart generation, data pipeline
  Data/             # databases/, raw, processed
  Outputs/          # Charts, content, PDFs
  Website/          # LighthouseMacro.com source
  lighthouse_quant/ # Quantitative models
```

---

# SECTION 11: CODING STANDARDS

## Python

- Python 3.8+, PEP8, type hints + docstrings on public functions
- Core stack: pandas, numpy, matplotlib, statsmodels optional
- Charts to `Outputs/` directory, both themes

## Charting in Code

- No gridlines. All four spines. Right axis primary.
- Palette: Ocean, Dusk, Sky, Venus, Sea, Doldrums, Starboard, Port
- Line thickness ~3, longest history available
- Axes matched at zero, independently scaled
- Watermark "MACRO, ILLUMINATED." bottom-right (never overlap data)
- Always both dark and white themes

---

# SECTION 12: PROPRIETARY INDICATORS (The Codex)

| Indicator | Full Name | Definition |
|---|---|---|
| **LPI** | Labor Pressure Index | Composite labor health across flows and stocks |
| **LFI** | Labor Fragility Index | z(LongTermUnemp, -Quits, -Hires/Quits). Structural weakness before headline unemployment. |
| **PCI** | Price Conditions Index | Inflation pressure composite |
| **GCI** | Growth Conditions Index | Real economy momentum (second derivative) |
| **HCI** | Housing Conditions Index | Housing market health and rate sensitivity |
| **CCI** | Consumer Conditions Index | 7-component consumer spending/credit composite (updated Feb 2026) |
| **BCI** | Business Conditions Index | Business investment and capex commitment |
| **TCI** | Trade Conditions Index | Dollar dynamics and trade flow impact |
| **GCI-Gov** | Government Conditions Index | Fiscal dominance and term premium |
| **FCI** | Financial Conditions Index | Credit spreads and financial stress |
| **CLG** | Credit-Labor Gap | z(HY_OAS) - z(LFI). Negative = spreads too tight for labor reality. |
| **LCI** | Liquidity Cushion Index | System shock absorption via RRP, Reserves, Funding spreads |
| **MSI** | Market Structure Index | Breadth, trend, momentum composite |
| **SPI** | Sentiment & Positioning Index | Contrarian. High = Fear = Bullish |
| **SBD** | Structure-Breadth Divergence | z(Price_vs_200d) - z(%>50d_MA). Distribution warning. |
| **SSD** | Sentiment-Structure Divergence | z(SPI) + z(MSI). Capitulation/blow-off detector. |
| **MRI** | Macro Risk Index | Master composite. Synthesizes all 12 pillars. |
| **CLI** | Crypto Liquidity Impulse | 3-tier liquidity transmission composite (Macro/Plumbing/Crypto-Native). |
| **SLI** | Stablecoin Liquidity Impulse | Rate of change in stablecoin market cap. On-chain liquidity proxy. |

---

# SECTION 13: BUSINESS & RELATIONSHIPS

## Pricing

- $50/month or $500/year (not publicly announced, launching after 12-pillar series completes)

## Founding Members (Locked Rates for Life)

- Michael Zhang: $300/year
- Josh Giordano: $400/year
- Ryan Salah: $400/year

Note: Custom research / signal databases = institutional-tier work, not included in founding member rates.

## Key Relationships

| Person | Role | Status |
|---|---|---|
| **Pascal Hugli** | Maerki Baumann, "Less Noise More Signal" podcast | Built CLI for his report. Podcast collab planned (liquidity deep-dive). LHM recommended on his Substack. |
| **Tania Reif** | PhD Columbia, ex-Soros/Citadel/IMF. CIO Senda Digital Assets | ~3 month trial phase. Q1 formalization pending. |
| **Christopher King** | Theo Advisors + ventures | Wants Bob as macro/data layer. Last contact ~early Feb 2026, gone quiet. |
| **Tim Pierotti** | WealthVest CIO | Podcast appearance scheduled Feb 24/25. Explicitly helping Bob build profile. |
| **Michael Nadeau** | The DeFi Report | Introductory call went well. Complementary: Bob top-down macro, Nadeau bottom-up DeFi. |

## Domain Setup

- lighthousemacro.com -> Main website (built by Bob + Claude, GitHub Pages)
- research.lighthousemacro.com -> Substack (custom domain)
- Network Solutions (expires Sep 9, 2026)

---

# SECTION 14: SYNC WORKFLOW

## Context Sync Script

**Location:** `/Users/bob/LHM/Scripts/sync_claude_context.sh`
**Alias:** `lhm-sync`
**Cron:** runs every 15 minutes via user crontab

**What it does automatically:**
1. Updates LAST_SYNC date in this file
2. Copies to Claude Code: `/Users/bob/.claude/CLAUDE.md`
3. Creates desktop export: `~/Desktop/LHM_MASTER_CONTEXT.md`
4. Commits + pushes `Strategy/CLAUDE_MASTER.md` to `github.com/BobSheehan23/LHM` when content changes (skips commits where only LAST_SYNC changed, to avoid churn)

**Downstream surfaces that auto-pick up context:**
- **Claude Code local** — reads `~/.claude/CLAUDE.md` on every session start
- **Claude Code remote-control** — same as local (remote-control dispatches into the local CLI)
- **Claude Code cloud environments** — clone the LHM repo on each run, so they see whatever was last pushed
- **Scheduled remote triggers** (Pulse Check, Morning Brief, others) — same mechanism as cloud environments
- **Memory system** — `~/.claude/projects/-Users-bob/memory/MEMORY.md` + topic files, auto-loaded on every Claude Code session
- **Skills** — `~/.claude/skills/` auto-loads six LHM skills on every session

**Manual targets (paste from Desktop export):**
- Claude.ai web / iOS / Android — paste into Profile → Settings → Custom Instructions
- Claude Desktop — paste into custom instructions
- Gemini — paste into context
- ChatGPT — paste into custom instructions

These four need re-pasting only when `CLAUDE_MASTER.md` has meaningful content changes (not daily). Do a batch refresh weekly or whenever a major section changes.

---

# SECTION 15: AUTOMATION & REMOTE WORK

## Claude Code Remote Control

Bob runs `claude remote-control` in a dedicated terminal tab (from `/Users/bob/LHM`) to dispatch Claude Code sessions into his Mac from any Claude.ai surface (web, desktop, mobile).

- **Bridge environment ID:** `env_019dok5DYQfwpL611fsNN6hk` (MacBookAir:LHM:1c24)
- **Requires:** Mac awake + terminal tab running `claude remote-control`
- **Full access:** local files, Lighthouse_Master.db, Python env, pipeline — everything
- **Use case:** work from phone without losing access to the DB and pipeline

When the Mac mini arrives (always-on), the bridge becomes reliable 24/7 and the Morning Brief trigger should be migrated off cloud onto the bridge so it can read the real DB for MRI/LFI/LCI values.

## Cloud Environments

Two cloud environments available for dispatch or scheduling:
- **LHM:** `env_01GnNcwscshi2BW1uALdMuZc` (anthropic_cloud, LHM-flavored)
- **Default Cloud Environment:** `env_011CUQkTDVrA7HzeaUfpaRvv` (generic anthropic_cloud)

Cloud environments **cannot** reach `Lighthouse_Master.db`. They can clone the LHM repo on GitHub, so anything committed to the repo is accessible, but the DB file itself is not in git.

## Scheduled Remote Triggers (Cloud Cron)

Two triggers run on cron in the Default Cloud Environment. Manage all triggers at https://claude.ai/code/scheduled.

### Pulse Check — `trig_01Lc4BVhD9Lb9dD2PhFFnSBg`
- **Cron:** `3 13-23 * * 1-5` (hourly Mon-Fri, 9am-7pm ET, off-minute)
- **Purpose:** ADHD-friendly triage of last ~90 min of Gmail + Google Calendar
- **Output:** sent email to bob@lighthousemacro.com with urgency-ranked triage (URGENT / SOON / FYI). Subject line designed for phone lock screen.
- **Named contacts to flag:** Pascal Hugli, Tania Reif, Christopher King, Tim Pierotti, Michael Nadeau
- **MCP:** Gmail + Google Calendar

### LHM Morning Brief — `trig_01UnidvkWSLvV8FzWJfy45N1`
- **Cron:** `27 10 * * 1-5` (6:27am ET weekdays, UTC-4 during EDT)
- **Purpose:** Daily pre-market brief in Lighthouse voice
- **Four sections:** overnight market moves → biggest macro news → today's calendar (econ releases + meetings) → urgent inbox
- **Data sources:** WebFetch/WebSearch (cloud env can't read local DB). Migrate to bridge environment once Mac mini is live.
- **Voice:** 80% institutional rigor + 20% dry observation, no emdashes, no AI-isms, speaks as "we"
- **Target length:** 350-450 words, hard max 550
- **DST note:** when clocks flip to EST, cron needs to shift to `27 11 * * 1-5`

### Killed: old launchd morning brief
The previous `com.lighthousemacro.morning-brief.plist` + `com.lighthousemacro.email-brief.plist` chain (07:30/07:35 local) was unloaded and deleted on 2026-04-14. Source scripts at `morning_brief.py` and `email_brief.py` are kept as reference for one week, then delete.

## LHM Claude Skills (six installed)

Source bundles at `/Users/bob/LHM/claude skills/` (note the space in the folder name). Installed copies at `~/.claude/skills/` load automatically on every Claude Code session start (local, remote-control, and cloud alike if synced).

| Skill | Purpose |
|---|---|
| `chart-god` | Static chart generation for all distribution channels (Twitter, Substack Notes, Beams, Beacons, Chartbooks, PDFs) |
| `lhm-brand-system` | Branded document generation (PDF, PPTX, DOCX, HTML) using 23/89/BB palette. Bundles brand-guide.md, chart-styling.md, templates.md |
| `lhm-data-analyst` | Database wizard + SQL savant for Lighthouse_Master.db and pillar sub-DBs |
| `lhm-macro-scout` | Autonomous research engine combining DB analysis with web search |
| `lhm-content-engine` | Autonomous content drafter in Bob's voice; consumes scout briefs + calendar specs |
| `lhm-content-calendar` | Publishing intelligence layer; knows Beacon/Beam/Note/Chartbook/Horizon schedule and macro release calendar |

**Pipeline:** scout (researches) → engine (drafts) → calendar (validates format/timing). lhm-data-analyst is the backbone — other skills delegate DB queries to it rather than writing raw SQL.

**To update a skill:** extract the `.skill` zip from `/Users/bob/LHM/claude skills/`, copy the inner folder into `~/.claude/skills/`, and restart the session. Skills don't hot-reload.

## Local launchd jobs (still running)

- **com.lighthousemacro.pipeline** — data pipeline
- **com.lighthousemacro.strategy-sync** — docs sync
- **crontab: sync_claude_context.sh** — every 15 min (updates master context + pushes to GitHub on real changes)

---

# REFERENCE FILES

| Content | Location |
|---|---|
| This Master Context | `/Users/bob/LHM/Strategy/CLAUDE_MASTER.md` |
| Full Pillar Details | `/Users/bob/LHM/Strategy/PILLAR [1-12] *.md` |
| Trading Strategy | `/Users/bob/LHM/Strategy/LIGHTHOUSE MACRO TRADING STRATEGY - MASTER.md` |
| Two Books Framework | `/Users/bob/LHM/Strategy/TWO_BOOKS_FRAMEWORK.md` |
| Asset Class Frameworks | `/Users/bob/LHM/Strategy/Asset_Class_Frameworks/*.md` |
| Brand Guide | `/Users/bob/LHM/Brand/brand-guide.md` |
| Chart Styling (Full Spec) | `/Users/bob/LHM/Brand/chart-styling.md` |
| Templates | `/Users/bob/LHM/Brand/templates.md` |
| Website Source | `/Users/bob/LHM/Website/` |
| Sync Script | `/Users/bob/LHM/Scripts/sync_claude_context.sh` |

---

**END OF MASTER CONTEXT**

**Version:** 5.7
**Compiled:** 2026-02-16 (v5.0); 2026-04-14 (v5.1 — added Section 15: Automation & Remote Work, updated Section 14 for git-push sync); 2026-04-28 (v5.3 — document footer updated to single-line three-link format); 2026-04-29 (v5.4 — added Section 0: Memory Summary from Claude.ai nightly memory export); 2026-04-29 (v5.5 — phone updated to +1 (929) 238-9397; "Founder" framing flagged as not preferred verbally but kept in canonical signature/title); 2026-04-29 (v5.6 — appended voice working guide; clarified we/I usage for written vs spoken); 2026-04-29 (v5.7 — clarified "we" frame; data-as-subject framing is also on-brand, only third-person hedge framing is the failure mode)
**Author:** Bob Sheehan, CFA, CMT

---

# APPENDIX: BOB'S REAL VOICE — A WORKING GUIDE

*Use this alongside the master context above when drafting anything in my voice. The master context tells you WHAT to know. This tells you HOW I actually sound.*

*For Claude, Gemini, ChatGPT, or anyone helping me write. Read this before drafting anything in my voice.*

---

## The core mistake to avoid

Most assistants overcorrect into a clipped, declarative style — short sentences, parallel structure, every line doing work. That is not my voice. That's the polished Substack-headline version of my voice, which sands off everything that makes it sound like me.

My real voice is rhythmic and varied. Long winding sentences when a thought is building. Short crystallizing lines at the end. Digressions, mid-thought corrections, and "and so" chained clauses are features, not bugs.

---

## The cadence rule

Vary sentence length deliberately.

- A typical paragraph builds with 3–5 longer sentences (some with mid-thought corrections, some that breathe out as far as the idea needs to go), and then lands with one or two short clarifying lines.
- The short sentences are the punches. They only work because the long sentences set them up.
- If a draft reads like a machine gun (every line clipped to 8–12 words), it is wrong.
- If it reads like a closing argument that occasionally slaps, it is right.
- Drafting everything in uniform short sentences strips the voice of its shape.

## The ADHD-flow piece

Sometimes I am an ADHD-raddled brain that has a long, windy run-on as thoughts come to me. That is real, and it should survive into the writing.

- A long building sentence with imperfect grammar, a mid-thought correction, an "and again" pivot, and an "and so" chain — that is how I actually talk. Reference: any answers in podcasts. They are paragraphs of building thought followed by short crystallizing lines.
- Don't force every long thought into clipped bullets. Let the thought breathe as far as it needs to go.
- When in doubt, write toward how I would say it aloud — including the digressions — not how a Substack editor would tighten it.

## Specific failure pattern to avoid

Taking my correction "tighter" or "shorter" as a global rule rather than a one-off.

- I say "tighter" when a specific sentence is bloated. I don't mean rewrite everything in 8-word sentences forever.
- I say "cut this" when a specific line doesn't earn its place. I don't mean strip every flourish from every section.
- Apply corrections locally, not globally.

---

## What good looks like

- "The labor data softened. Again."
- "Spreads are pricing one story. Labor is telling another."
- "The buffer is gone. The runway is short."
- "The Fed's in a box. They just haven't admitted it yet."

These work because they are short by design and are surrounded by longer analytical sentences that earn the punch.

## What to avoid

- **Em-dashes.** Never. Use commas, periods, colons, parentheses, or ellipses.
- **Semicolons.** Use commas.
- **AI-sounding transitions:** "It is important to note," "going forward," "in our view," "at the end of the day."
- **Hedging phrases:** "cautiously optimistic," "geopolitical uncertainty," "complex constellation of factors."
- **"Not X, it's Y" construction.** Default zero per piece. Never as a closer. Keep the lexicon (e.g., "camouflage" is fine), kill the structural pattern.
- **Forced metaphors and manufactured catchphrases.** No quotable-line factory.
- **Excessive nautical references** beyond what is naturally in the brand vocabulary.
- **Contrarian-flex framings I can't actually defend on stage.** Specifically: don't write "add more, you add noise, subtract any, you go blind" or "nobody covers this." Those overclaim. Use defendable framing like "for us, this does a great job of [X]" or "what's rare is connecting them with math, not the count."

---

## The "we" frame

For published written content (Beacons, Beams, Notes, Chartbooks, Horizons), default to "we" voice as Lighthouse Macro: "we're seeing stress," "we read the print as..." Letting the data speak directly is also fine: "the data shows stress," "spreads are pricing one story." Both register as on-brand. What to avoid is hedge framing that uses third-person to dodge a view: "some observers note," "the consensus suggests." In speech (podcasts, calls, video), both "I" and "we" are fine, whichever lands naturally. In internal notes and drafts, "I" is the default.

## Strong views, weakly held

State a thesis. State the conditions under which the thesis breaks. That is not hedging. It is intellectual honesty. Pre-commitment beats the urge to defend a losing trade.

## The 80/20 rule

- 80% institutional rigor — CFA / CMT credibility, quantitative precision.
- 20% personality — dry observations, skepticism of consensus, wit when it's natural.
- 0% forced flair.

## What the framework lets me say

- "We measure the pressure underneath the labor market — the stuff that moves before the headline. We call it the Labor Fragility Index, LFI." (Concept first, term second. Always.)
- "By the time the unemployment rate moves, the story is already over."
- "Because it's boring until it isn't, and by then it's too late."
- "Worldview without a portfolio is a tweet. A portfolio without a worldview is a series of guesses. The framework is the bridge."

## What the framework prevents me from saying

- "We are uniquely positioned to..." (no, just describe what we do)
- "Nobody else covers..." (false in most cases — the edge is the framework, not the topic)
- "The only way to..." (overclaim; use "the way we do it" or "for us")
- "It is important to note that..." (delete and try again)

---

## Bottom line

Write the way I actually talk. Long thoughts that breathe. Short lines that land. Digressions that show the brain working. No emdashes. No false certainty. No contrarian poses I can't back up.

If a draft sounds like a McKinsey deck, it is wrong.
If it sounds like a closing argument from someone who has actually been in the chair, it is right.
