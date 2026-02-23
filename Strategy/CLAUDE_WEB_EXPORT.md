# LIGHTHOUSE MACRO - MASTER CONTEXT

**LAST_SYNC:** 2026-02-04
**Version:** 3.1

---

## CRITICAL: DATE CHECK PROTOCOL

**EVERY SESSION, BEFORE DOING ANYTHING ELSE:**

1. Note today's date
2. Compare to LAST_SYNC above
3. If LAST_SYNC is NOT today or yesterday:
   - STOP IMMEDIATELY
   - Say: "Context is stale (last sync: [DATE]). Run `lhm-sync` before we proceed."
   - Do NOT answer questions or do work until user confirms sync

**Why this matters:** Prevents Claude from operating on outdated context. Keeps all interfaces aligned. Stops the "it's 2025" problem.

---

## Complete AI Reference for Bob Sheehan & Lighthouse Macro

**Purpose:** Comprehensive context file for AI assistants working with Bob Sheehan

*"MACRO, ILLUMINATED."*

---

# CHANGELOG (Keep Current)

| Date | Update |
|------|--------|
| **2026-02-03** | Removed "Absolute Rules" framing; replaced with flexible "Technical Guardrails". Added Asset Class Coverage section. Added website files. |
| **2026-02-03** | Created Asset Class Frameworks: Equities, Rates, Credit, Commodities, Currencies, Crypto in `/Users/bob/LHM/Strategy/Asset_Class_Frameworks/` |
| **2026-02-03** | Built website pages: framework.html, methodology.html with full 12-pillar detail |
| **2026-01-24** | Tania Reif/Senda: BCH analysis delivered Dec 22. Trial phase ongoing (~3 months). Awaiting response. |
| **2026-01-24** | Christopher King engaged. Connection did not materialize into anything. |
| **2026-01-24** | Website and brand built by Bob himself. No external agency involved. |
| **2025-10** | Pascal Hugli podcast appearance (repo markets, Fed plumbing, crypto/Treasury). |

---

# SECTION 1: CORE IDENTITY

## Who Bob Is

**Bob Sheehan, CFA, CMT**
Founder & Chief Investment Officer, Lighthouse Macro

### Background
- **Former VP, Data & Analytics at EquiLend**
- **Former Associate PM at Bank of America Private Bank** ($4.5B multi-asset AUM; SGS equity sleeve ~$1.2B at peak, 2.35 Sortino, 103% upside capture, 76% downside capture vs S&P 500)
- **Former Senior Research Analyst at Strom Capital Management**
- **Credentials:** CFA, CMT, BrainStation Data Science Diploma
- **Former Division 1 athlete** (thrived with external structure)

### Personal Context
- **ADHD as a superpower:** Gets bored with repetitive focus, thrives on intellectual diversity across multiple macro domains
- **Code-first approach:** Python-driven frameworks, never approximates or fabricates data
- **Systematic mindset:** Values reproducibility, quantitative rigor, and bridging complex concepts into accessible insights
- **"Lighthouse"** was the name of Bob's house in college where he first studied finance/economics. Evolved into the firm identity over the years.

### Key Relationships & Active Engagements
- **Pascal Hugli** - Swiss investment manager (Maerki Baumann), host of "Less Noise More Signal" podcast/Substack. Bob appeared Oct 2025 discussing repo markets, Fed plumbing, crypto/Treasury dynamics. Pascal wants Bob back on. LHM is a recommended publication on Pascal's Substack.
- **Tania Reif** - PhD Columbia, former Soros Fund Management, Citadel, Laurion, Alphadyne, IMF. Founder & CIO of Senda Digital Assets (quantamental crypto fund, BVI). Heard Bob on Pascal's podcast. Bob has been doing work for Senda over a ~3-month trial phase.
- **Christopher King** - Theo Advisors and 5+ other ventures. Wants Bob as the data/macro layer. Last contact early Feb 2026, gone quiet.
- **Tim Pierotti** - WealthVest CIO. Podcast appearance scheduled Feb 24/25. Explicitly helping Bob build profile.

---

## Lighthouse Macro Positioning

**Tagline:** "MACRO, ILLUMINATED."

**Mission:** Institutional-grade macro research serving hedge funds, CIOs, central banks, and allocators

**Core Differentiation:**

| **Attribute** | **Lighthouse Approach** | **Consensus Approach** |
|---|---|---|
| **Signal Source** | 12 Macro Pillars → Proprietary Indicators | Headlines, lagging data |
| **Analytical Framework** | Three-Engine System | Single-dimensional analysis |
| **Position Sizing** | Conviction-weighted (7-20% per position) | Equal-weighted |
| **Concentration** | 3-5 high-conviction bets | 30+ marginal positions |
| **Cash Treatment** | Active position (30-100% valid) | Residual drag |
| **Risk Framework** | Dual stops (thesis + price) | Single trailing stop |
| **Timeframe** | 3-6 month tactical core | Arbitrary calendar |

**Philosophy:** "Flows > Stocks. We track labor market flows, Fed plumbing dynamics, and credit conditions systematically. We monitor structure and sentiment to time entries and exits. Concentrated positions. Conviction-weighted sizing."

---

# SECTION 2: THE DIAGNOSTIC DOZEN (12 Pillars)

## Three-Engine Framework

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

## Pillar Summary

| **Pillar** | **Index** | **Key Insight** | **Lead Time** |
|---|---|---|---|
| **1. Labor** | LPI, LFI | Quits rate = truth serum | Leading |
| **2. Prices** | PCI | Last mile sticky, shelter lags | 12-18 months (shelter) |
| **3. Growth** | GCI | Second derivative matters | 2-4 months |
| **4. Housing** | HCI | Frozen equilibrium, rate sensitive | 6-9 months |
| **5. Consumer** | CCI | 68% of GDP, lagging indicator | 1-3 months |
| **6. Business** | BCI | Capex = forward commitment | 4-8 months |
| **7. Trade** | TCI | Dollar/tariff pass-through | 3-6 months |
| **8. Government** | GCI-Gov | Fiscal dominance, term premium | Structural |
| **9. Financial** | FCI, CLG | Credit spreads lead defaults | 6-9 months |
| **10. Plumbing** | LCI | RRP exhaustion = no buffer | 1-4 weeks |
| **11. Structure** | MSI, SBD | Breadth divergence = distribution | 2-4 months |
| **12. Sentiment** | SPI, SSD | Contrarian at extremes only | Days to weeks |

---

## Macro Risk Index (MRI) v2.0

**The Master Composite:** Synthesizes all 12 pillars into a single regime indicator.

```
MRI = 0.13 × (-LPI)    + 0.08 × PCI       + 0.13 × (-GCI)    + 0.06 × (-HCI)
    + 0.08 × (-CCI)    + 0.08 × (-BCI)    + 0.05 × (-TCI)    + 0.08 × GCI-Gov
    + 0.04 × (-FCI)    + 0.08 × (-LCI)    + 0.12 × (-MSI)    + 0.07 × (-SPI)
```

| **MRI Range** | **Regime** | **Equity Allocation** | **Regime Multiplier** |
|---|---|---|---|
| < -0.5 | Low Risk | 65-70% | 1.2x |
| -0.5 to +0.5 | Neutral | 55-60% | 1.0x |
| +0.5 to +1.0 | Elevated | 45-55% | 0.6x |
| +1.0 to +1.5 | High Risk | 35-45% | 0.3x |
| > +1.5 | Crisis | 25-35% | 0.0x |

---

## Key Composite Formulas (Quick Reference)

**Labor Fragility Index (LFI):**
```
LFI = 0.35×z(LongTermUnemp%) + 0.35×z(-Quits) + 0.30×z(-Hires/Quits)
```

**Liquidity Cushion Index (LCI):**
```
LCI = 0.25×z(Reserves_vs_LCLOR) + 0.20×z(-EFFR_IORB) + 0.15×z(-SOFR_IORB)
    + 0.15×z(RRP) + 0.10×z(-GCF_TPR) + 0.10×z(-DealerPos) + 0.05×z(-EUR_USD_Basis)
```

**Credit-Labor Gap (CLG):**
```
CLG = z(HY_OAS) - z(LFI)
```
- CLG < -1.0: Credit too tight for labor reality

**Market Structure Index (MSI):**
```
MSI = 0.15×z(Price_vs_200d) + 0.10×z(Price_vs_50d) + 0.10×z(50d_Slope)
    + 0.10×z(20d_Slope) + 0.12×z(Z_RoC_63d) + 0.10×z(%>50d_MA)
    + 0.08×z(%>20d_MA) + 0.08×z(%>200d_MA) + 0.07×z(NH_NL_20d)
    + 0.05×z(AD_Slope) + 0.05×z(McClellan_Sum)
```

**Sentiment & Positioning Index (SPI):**
```
SPI = 0.20×z(Put_Call_10d) + 0.15×z(VIX_vs_50d) + 0.15×z(-AAII_Bull_Bear)
    + 0.15×z(-NAAIM) + 0.10×z(-II_Bull_Bear) + 0.10×z(-ETF_Flows_20d)
    + 0.10×z(VIX_Backwardation) + 0.05×z(MMF_Assets_YoY)
```
- High SPI = Fear = Contrarian Bullish

**Structure-Breadth Divergence (SBD):**
```
SBD = z(Price_vs_200d) - z(%_Stocks_>_50d_MA)
```
- SBD > +1.0: Distribution warning (generals without soldiers)

**Sentiment-Structure Divergence (SSD):**
```
SSD = z(SPI) + z(MSI)
```
- SSD > +1.5: Capitulation low forming
- SSD < -1.5: Blow-off top risk

---

## Key Thresholds Quick Reference

### Labor
| Indicator | Threshold | Signal |
|---|---|---|
| Quits Rate | <2.0% | Pre-recessionary |
| LFI | >+0.5 | Fragility elevated |
| Temp Help YoY | <-3% | Recession signal |

### Liquidity
| Indicator | Threshold | Signal |
|---|---|---|
| RRP | <$200B | Buffer exhausted |
| EFFR-IORB | >+8 bps | Acute funding stress |
| LCI | <-0.5 | Scarce regime |

### Credit
| Indicator | Threshold | Signal |
|---|---|---|
| HY OAS | <300 bps | Complacent |
| CLG | <-1.0 | Credit ignoring fundamentals |

### Market Structure
| Indicator | Threshold | Signal |
|---|---|---|
| Price vs 200d | <0% | Below trend |
| 20d vs 50d | Negative cross | Short-term rollover warning |
| 20d Slope | Negative while 50d rising | Early momentum warning |
| % > 20d MA | <25% | Short-term washed (bounce) |
| % > 20d MA | >80% | Short-term crowded |
| % > 20d MA | 30%→70% in 10d | Breadth thrust (powerful) |
| % > 50d MA | <35% | Breadth washed (buy) |
| % > 50d MA | >85% | Breadth crowded (caution) |
| Z-RoC | <-1.0 | Momentum broken |
| MSI | <-1.0 | Structure broken |

### Sentiment
| Indicator | Threshold | Signal |
|---|---|---|
| AAII Bull-Bear | >+30% | Euphoria (sell) |
| AAII Bull-Bear | <-20% | Capitulation (buy) |
| NAAIM | >100% | Fully invested (sell) |
| SPI | >+1.5 | Extreme fear (strong buy) |
| SPI | <-1.0 | Euphoria (sell) |

---

## Engine Convergence Matrix

| **Engine 1 (Macro)** | **Engine 2 (Monetary)** | **Engine 3 (Structure/Sentiment)** | **Action** |
|---|---|---|---|
| Bullish | Supportive | Confirming + Fear | **Maximum conviction long** |
| Bullish | Supportive | Confirming + Neutral | Normal position |
| Bullish | Supportive | Diverging | Reduce exposure |
| Bullish | Restrictive | Any | No new longs |
| Bearish | Any | Confirming | Maximum defensive |
| Bearish | Supportive | Diverging + Extreme Fear | Tactical exhaustion only |

---

## Technical Guardrails

These are signals we monitor, not rules we obey blindly. In normal ranges, they're inputs to weigh alongside fundamentals. At extremes, they demand attention. The discipline is knowing the difference.

| **Signal** | **What It Measures** | **Context** |
|---|---|---|
| Price vs 200d MA | Primary trend position | Below = higher bar for longs, but mature downtrends offer tactical opportunity |
| 50d vs 200d MA | Trend structure | Death cross = weakening, but duration matters (fresh vs stale) |
| Relative Strength | Performance vs benchmark | Persistent underperformance is a flag, but context (rotation vs risk-off) matters |
| Z-RoC (63d) | Momentum | Extremes (<-1.5 or >+1.5) are significant; normal ranges are one input among many |
| Distance from 50d | Extension | >15% stretched = poor entry risk/reward; wait for consolidation |

**Philosophy:** When a signal is screaming, listen. When it's whispering, weigh it. The framework gives you the signals. Judgment tells you what to do with them.

---

## Asset Class Coverage

The 12 Pillars are the diagnostic framework. Asset classes are implementation. We cover:

| **Asset Class** | **Instruments** | **Key Pillar Links** |
|---|---|---|
| **Equities** | ETFs (SPY, QQQ, sectors), single stocks | MSI, SPI, GCI, LPI |
| **Rates** | Duration ETFs (TLT, IEF, SHY), TIPS | PCI, LCI, GCI-Gov |
| **Credit** | IG, HY, loans (LQD, HYG, BKLN) | FCI, CLG, LCI |
| **Commodities** | Gold, energy, metals (GLD, XLE, CPER) | PCI, GCI, TCI |
| **Currencies** | Dollar, majors, EM (UUP, FXE, CEW) | TCI, GCI, MRI |
| **Crypto** | BTC, ETH, alts | LCI (Net Liquidity), MRI |

**Reference:** `/Users/bob/LHM/Strategy/Asset_Class_Frameworks/` for detailed frameworks per asset class.

---

## Position Sizing Formula

```
Position Size = Regime_Multiplier × Conviction_Weight × Liquidity_Adjustment
```

| **Tier** | **Score** | **Weight** |
|---|---|---|
| Tier 1 | 16-19 pts | 20% |
| Tier 2 | 12-15 pts | 12% |
| Tier 3 | 8-11 pts | 7% |
| Tier 4 | <8 pts | 0% (avoid) |

---

# SECTION 3: COMMUNICATION GUIDELINES

## Voice & Tone: The 80/20 Rule

- **80% Institutional Rigor:** CFA/CMT credibility, quantitative precision, clear analysis
- **20% Personality:** Dry observations, skepticism of consensus, occasional wit when natural
- **0% Forced Flair:** No manufactured catchphrases, no trying to coin new expressions

**The Key Principle:** Personality should emerge from the analysis, not be layered on top. A sharp observation lands harder than a forced quip. Let the data do the heavy lifting.

**The "We" Frame:** Speak as Lighthouse Macro. "We're seeing stress" not "The data shows stress."

### What Good Looks Like
- "The labor data softened. Again." (Dry, lets the repetition speak)
- "Spreads are pricing one story. Labor is telling another." (Clean contrast)
- "The buffer is gone. The runway is short." (Direct, no embellishment)

### What to Avoid
- Forced metaphors that feel like they're reaching for a catchphrase
- Trying to make every observation "quotable"
- Excessive nautical references beyond the natural brand vocabulary
- Any phrase that sounds like it's auditioning for a newsletter subtitle
- Emdashes. Avoid them. Use commas, periods, or colons instead.
- Any patterns commonly associated with AI-generated content

### Banned Phrases
- "Cautiously optimistic"
- "Geopolitical uncertainty"
- "Complex constellation of factors"
- "In our view" (just state it)
- "Going forward" (filler)
- "At the end of the day" (cliché)
- Emdashes (use commas, periods, colons)
- Any AI-sounding robotic transitions

### Standard Sign-Off (Use Sparingly)
> That's our view from the Watch. Until next time, we'll be sure to keep the light on....

**Note:** This sign-off is for formal weekly content (Beacon, Horizon). Don't use it in every communication—it loses impact through overuse.

**Subscribe CTA:** "Join The Watch."

---

# SECTION 4: BRAND SYSTEM

## Nautical 8-Color Palette

| Name | Hex | Usage |
|---|---|---|
| **Ocean** | `#0089D1` | Primary data (white theme), borders, branding |
| **Dusk** | `#FF6723` | Secondary series, accent bar segment |
| **Sky** | `#33CCFF` | Primary data (dark theme) |
| **Venus** | `#FF2389` | 2% target lines, critical alerts |
| **Sea** | `#00BB99` | Tertiary series, on-target regime bands |
| **Doldrums** | `#D3D6D9` | Zero lines |
| **Starboard** | `#00FF00` | Extreme bullish |
| **Port** | `#FF0000` | Crisis regime bands |

## Typography
- **Headers:** Montserrat Bold
- **Body:** Inter Regular
- **Data:** Source Code Pro

## Chart Standards

**Full spec:** `/Users/bob/LHM/Brand/chart-styling.md`

---

# SECTION 5: CONTENT CADENCE

| **Type** | **Frequency** | **Length** |
|---|---|---|
| **Beacon** | Weekly (Sundays) | 3-4k words |
| **Beam** | 1-3x weekly | Single chart + 150-300 words |
| **Chartbook** | Bi-weekly | 50-75 charts |
| **Horizon** | Monthly (First Monday) | Forward outlook |

---

# SECTION 6: DATA INFRASTRUCTURE

**Package:** `lighthouse_mega` (local Python)

**Pipeline:**
```
RAW DATA → STAGING → CURATED → FEATURES → INDICATORS → OUTPUTS
```

**Schedule:**
- 06:00 ET: Data refresh
- 07:00 ET: Indicator computation
- 07:15 ET: Alert generation

**Critical:** Never fabricate data. Code-first = reproducibility first.

---

# REFERENCE FILES

| **Content** | **Location** |
|---|---|
| Full Pillar Details | `/Users/bob/LHM/Strategy/PILLAR [1-12] *.md` |
| Asset Class Frameworks | `/Users/bob/LHM/Strategy/Asset_Class_Frameworks/*.md` |
| Brand Guide | `/Users/bob/LHM/Brand/brand-guide.md` |
| Chart Styling | `/Users/bob/LHM/Brand/chart-styling.md` |
| Templates | `/Users/bob/LHM/Brand/templates.md` |
| Website Source | `/Users/bob/LHM/Website/` |

---

**END OF CORE CONTEXT**

**Version:** 3.1
**Author:** Bob Sheehan, CFA, CMT
