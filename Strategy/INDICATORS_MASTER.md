# LIGHTHOUSE MACRO — INDICATORS MASTER

**Single source of truth for every proprietary measurement, composite, and framework.**

**Last consolidated:** 2026-05-01
**DB snapshot:** 2,498 series · 4.15M observations · 45 live composites in `lighthouse_indices`
**Replaces / consolidates:**
- `Strategy/LIGHTHOUSE MACRO - PROPRIETARY INDICATORS REFERENCE.md` (39 numbered indicators, formulas + thresholds)
- `Outputs/mri_optimization/PILLAR_DOCS/` (12 per-pillar audit writeups, Apr 30)
- `Outputs/mri_optimization/{LIVE_STATUS,DECISIONS,CANDIDATE_NEW_INDICATORS,PHASE_1_FINDINGS,PILLAR_BASKET_AUDIT,PILLAR_BASKET_CURATED,SIGNAL_SERIES_PLAN,BEAM_PLAN_BY_ASSET}.md`
- `Outputs/mri_optimization/descriptive/PILLAR_DESCRIPTIVE_ANALYSIS.md`
- `Outputs/mri_optimization/predictive/PILLAR_PREDICTIVE_GRID.md`
- `Outputs/mri_optimization/*.json` (4 optimization runs)

The detail files stay in place. This document is the index, the live state, and the canonical names + formulas + thresholds. When information conflicts, this file wins.

---

## TABLE OF CONTENTS

1. [How to read this document](#how-to-read-this-document)
2. [Live composite snapshot (45 indices)](#live-composite-snapshot)
3. [Master Composite — MRI](#master-composite-mri)
4. [12-Pillar Diagnostic Dozen](#12-pillar-diagnostic-dozen)
   - [Macro Dynamics (1-7)](#macro-dynamics-17)
   - [Monetary Mechanics (8-10)](#monetary-mechanics-810)
   - [Market Structure (11-12)](#market-structure-1112)
5. [Cross-pillar derived indices](#cross-pillar-derived-indices)
6. [Risk regime outputs](#risk-regime-outputs)
7. [Crypto sector composites](#crypto-sector-composites)
8. [Treasury microstructure indicators](#treasury-microstructure-indicators)
9. [Advanced trading frameworks](#advanced-trading-frameworks)
10. [Audit findings & live trading whitelist](#audit-findings--live-trading-whitelist)
11. [Candidate indicators (proposed, unbuilt)](#candidate-indicators-proposed-unbuilt)
12. [Naming conventions and aliases](#naming-conventions-and-aliases)

---

## HOW TO READ THIS DOCUMENT

**Three states a composite can be in:**

- **LIVE** — exists in `lighthouse_indices` table, refreshed by the pipeline, currently driving decisions. 45 of these.
- **DOCUMENTED** — has a formula in the proprietary indicators reference but no row in `lighthouse_indices` yet. Build candidate.
- **PROPOSED** — surfaced during the Apr 30 audit as a future indicator. Not built. Not approved.

**Three layers per indicator:**

1. **What it is** — one-line claim, the canonical name and abbreviation.
2. **Formula** — components and weights as documented in CLAUDE_MASTER or the reference doc.
3. **State** — LIVE / DOCUMENTED / PROPOSED, current value if live, audit notes if relevant.

**When a name appears in two places with two formulas** (e.g. LFI vs LPI, the optimized CCI vs the documented 7-component CCI), this document flags the divergence and names the canonical version.

---

## LIVE COMPOSITE SNAPSHOT

**As of 2026-05-01.** All 45 composites in `lighthouse_indices`. Latest reading per index_id.

### Master & risk regime

| Index | Latest | Value | Status |
|---|---|---|---|
| MRI (Macro Risk Index) | 2026-04-30 | 0.030 | MID-CYCLE |
| ENSEMBLE_RISK | 2026-04-30 | 0.629 | PRE_CRISIS |
| WARNING_LEVEL | 2026-04-30 | 4.0 | RED |
| ALLOC_MULTIPLIER | 2026-04-30 | 0.15 | CAPITAL PRESERVATION |
| BASE_REC_PROB | 2026-04-30 | 0.179 | LOW RISK |
| REC_PROB | 2026-04-30 | 0.179 | LOW RISK |
| LIQ_STAGE | 2026-04-30 | 2.0 | STAGE 2 — RESERVE DRAIN |

### 12-pillar composites

| Pillar | Index | Latest | Value | Status |
|---|---|---|---|---|
| 1. Labor | LPI | 2026-02-28 | 0.017 | NEUTRAL |
| 2. Prices | PCI | 2026-04-30 | 0.058 | ON TARGET |
| 3. Growth | GCI | 2026-01-01 | 0.022 | TREND |
| 4. Housing | HCI | 2026-02-01 | 0.204 | FROZEN |
| 5. Consumer | CCI | 2026-01-01 | 0.569 | HEALTHY |
| 6. Business | BCI | 2026-04-21 | 0.143 | SLOWING |
| 7. Trade | TCI | 2026-03-06 | -2.502 | TRADE CRISIS |
| 8. Government | GCI_Gov | 2026-03-06 | 0.035 | NORMAL |
| 9. Financial | FCI | 2026-04-30 | 0.017 | NEUTRAL |
| 10. Plumbing | LCI | 2026-04-30 | -0.207 | TIGHT |
| 11. Market Structure | MSI | 2026-04-30 | 0.942 | BULLISH |
| 12. Sentiment | SPI | 2026-04-29 | -0.304 | NEUTRAL |

### Sub-indices and derived

| Index | Latest | Value | Status |
|---|---|---|---|
| LFI (Labor Fragility) | 2026-03-10 | 0.186 | NEUTRAL |
| LDI (Labor Dynamism) | 2025-12-01 | 0.832 | HEALTHY |
| CLG (Credit-Labor Gap) | 2026-03-10 | -1.681 | SEVERELY MISPRICED |
| YFS (Yield-Funding Stress) | 2026-04-30 | 0.770 | ELEVATED |
| SVI (Spread-Vol Imbalance) | 2026-03-09 | 0.647 | BALANCED |
| EMD (Equity Momentum Divergence) | 2026-04-21 | -0.070 | OVERSOLD |
| BILL_SOFR (3M Bill-SOFR Spread) | 2026-03-09 | 0.060 | BILLS RICH |
| SBD (Structure-Breadth Divergence) | 2026-04-29 | 0.599 | ALIGNED |
| SSD (Sentiment-Structure Divergence) | 2026-04-29 | 0.992 | FEAR + WEAK |
| DISCONTINUITY_PREMIUM | 2026-04-30 | 0.450 | EXTREME |

### Crypto / stablecoin

| Index | Latest | Value | Status |
|---|---|---|---|
| SLI (Stablecoin Liquidity Impulse) | 2026-01-19 | 1.336 | EXPANSION |
| SLI_MCAP | 2026-01-12 | 187.046 | — |
| SLI_ROC_30D | 2026-01-12 | 0.400 | — |
| SLI_ROC_90D_ANN | 2026-01-12 | 15.400 | — |
| CDI (Crypto Demand Index) | 2026-02-02 | 1.209 | HIGH ACTIVITY |
| CFI (Crypto Fundamental Index) | 2026-02-02 | 61.350 | HEALTHY |
| CTI (Crypto Technical Index) | 2026-02-02 | 0.382 | CAUTIOUS |
| CVI (Crypto Valuation Index) | 2026-02-02 | -0.344 | FAIR VALUE |
| Crypto DeFi Derivatives Health | 2026-02-02 | 73.0 | HEALTHY |
| Crypto DeFi DEX Health | 2026-02-02 | 78.25 | HEALTHY |
| Crypto DeFi Lending Health | 2026-02-02 | 60.0 | NEUTRAL |
| Crypto Infrastructure Health | 2026-02-02 | 48.33 | WEAK |
| Crypto Layer 1 (Settlement) Health | 2026-02-02 | 55.0 | NEUTRAL |
| Crypto Layer 2 (Scaling) Health | 2026-02-02 | 73.0 | HEALTHY |
| Crypto Liquid Staking Health | 2026-02-02 | 56.25 | NEUTRAL |
| Crypto Uncategorized Health | 2026-02-02 | 51.29 | NEUTRAL |

---

## MASTER COMPOSITE — MRI

### Macro Risk Index (MRI) v2.0 — 12-pillar formula

**Status:** LIVE. `lighthouse_indices.index_id = 'MRI'`. Refreshed daily.

**Claim:** Single number capturing aggregate macro risk across all twelve Diagnostic Dozen pillars. The output that drives the equity allocation table and the position-sizing regime multiplier.

**Formula (v2.0):**

```
MRI = 0.10*LPI + 0.10*PCI + 0.08*GCI + 0.06*HCI + 0.08*CCI + 0.06*BCI + 0.05*TCI
    + 0.10*GCI_Gov + 0.12*FCI + 0.08*LCI
    + 0.09*MSI + 0.08*SPI
```

Weights sum to 1.00. Macro Dynamics block = 0.53. Monetary Mechanics block = 0.30. Market Structure block = 0.17.

**Regime classification → equity allocation table:**

| MRI z-score | Regime | Equity allocation | Position multiplier |
|---|---|---|---|
| < -0.5 | Low Risk | 65-70% | 1.2x |
| -0.5 to +0.5 | Neutral | 55-60% | 1.0x |
| +0.5 to +1.0 | Elevated | 45-55% | 0.6x |
| +1.0 to +1.5 | High Risk | 35-45% | 0.3x |
| > +1.5 | Crisis | 25-35% | 0.0x |

**Audit findings (Apr 30):**
- The MRI structural decisions (regime sizing, dual stops, conviction tiers) survive the audit untouched. Independent of OOS IC numbers.
- Three component pillars (CCI, BCI, FCI) failed descriptive integrity checks. The MRI weighting itself is sound but those three component composites need rebuilding before the MRI carries the same conviction it did pre-audit.
- See `Outputs/mri_optimization/LIVE_STATUS.md` for the full whitelist of what's safe for live trading.

---

## 12-PILLAR DIAGNOSTIC DOZEN

Twelve pillars across three engines. Pillars = inputs. Engines = processors.

### Macro Dynamics (1-7)

#### 1. Labor Pressure Index (LPI) / Labor Fragility Index (LFI)

**Status:** LIVE (both LPI and LFI rows in `lighthouse_indices`).

**Naming note:** CLAUDE_MASTER uses LPI as the pillar identifier and LFI as the labor sub-composite. The optimization JSON treats them as one indicator. For external publication use the full name on first reference: "Labor Pressure Index (LPI)" or "Labor Fragility Index (LFI)" depending on what's being measured.

**Documented LFI formula (CLAUDE_MASTER):**
```
LFI = 0.35*z(LongTermUnemp%) + 0.35*z(-Quits) + 0.30*z(-Hires/Quits)
```

**Optimized LPI basket (`pillar_multiasset_optimization.json`):**
| Component | Weight |
|---|---|
| UNRATE | 0.300 |
| UEMP27OV | 0.300 |
| JTSQUR (Quits rate) | 0.140 |
| TEMPHELPS | 0.123 |
| JTSHIR (Hires rate) | 0.070 |
| JTSJOL (Job openings) | 0.067 |

**Documented thresholds:**
- Quits Rate < 2.0% → Pre-recessionary
- LFI z > +0.5 → Fragility elevated
- Temp Help YoY < -3% → Recession signal
- Long-Term Unemployed > 22% of total → Structural fragility

**Audit (Apr 30):** Drop UNRATE from input basket — it's the target, not a flow. Documented LFI excludes UNRATE because the pillar is supposed to LEAD it. Composite tracks UNRATE concurrently at +0.88 Pearson; best single component (UEMP27OV) at 0.84 — marginal +0.04 from compositing. See `Outputs/mri_optimization/PILLAR_DOCS/01_LPI.md`.

#### 2. Price Conditions Index (PCI)

**Status:** LIVE.

**Documented formula:**
```
PCI = 0.30*z(CoreCPI YoY) + 0.25*z(CorePCE YoY) + 0.20*z(StickyCPI) + 0.15*z(TrimmedMeanCPI) + 0.10*z(CPIShelter)
```

**Documented thresholds:**
- Core PCE > 3.0% → Above target, restrictive policy implied
- Core PCE 2.0-3.0% → Last-mile zone
- Sticky CPI > 4.0% → Service inflation entrenched
- Shelter contribution > 50% of core → Lagging measurement masking real disinflation

**Audit:** Optimization for 2y yield prediction has only +0.81 r with core PCE YoY. Single-best component (CPIAUCSL alone) hits +0.90. Pillar isn't doing the descriptive job. Candidate A1 (Concurrent Inflation Lens) proposed as descriptive sibling. See `Outputs/mri_optimization/PILLAR_DOCS/02_PCI.md`.

#### 3. Growth Conditions Index (GCI)

**Status:** LIVE.

**Documented formula:**
```
GCI = 0.25*z(TCU) + 0.25*z(INDPRO YoY) + 0.20*z(CFNAIMA3) + 0.15*z(NewOrders 3m) + 0.15*z(PMI Composite)
```

**Documented thresholds:**
- CFNAIMA3 < -0.7 → Recession underway
- TCU < 76% → Slack rising
- INDPRO YoY < 0% → Industrial contraction
- CFNAIMA3 > +0.5 → Above-trend growth

**Audit:** GCI has only 0.43 r with CFNAIMA3 itself; TCU alone hits 0.47. Descriptive growth-tracking job done worse by GCI than by single component. Candidate A2 (Concurrent Activity Tracker) proposed. See `Outputs/mri_optimization/PILLAR_DOCS/03_GCI.md`.

#### 4. Housing Conditions Index (HCI)

**Status:** LIVE.

**Documented formula:**
```
HCI = 0.25*z(MortgageRate30Y - 6) + 0.20*z(-CaseShillerYoY) + 0.20*z(-NHSDemand) + 0.20*z(-Affordability) + 0.15*z(InventoryMonths - 6)
```

**Documented thresholds:**
- 30Y Mortgage > 7.0% → Demand crushed
- Case-Shiller YoY < -2% → Asset deflation risk
- NHS Demand < 600k SAAR → Stalled
- Affordability Index < 100 → Locked out
- Inventory > 9 months → Buyer's market

**Audit:** See `Outputs/mri_optimization/PILLAR_DOCS/04_HCI.md`.

#### 5. Consumer Conditions Index (CCI) — UPDATED FEB 2026 (7-component)

**Status:** LIVE but DESCRIPTIVELY BROKEN (audit Apr 30).

**Documented formula (Feb 2026):**
```
CCI = 0.25*z(Real PCE YoY) + 0.20*z(-RetailSales 3m) + 0.15*z(SavingsRate - 5%)
    + 0.10*z(-CC Delinquency) + 0.10*z(-DSR) + 0.10*z(UMCSENT z) + 0.10*z(-PSAVRT)
```

**Optimized basket (post-Apr-30 audit, NOT canonical):** Missing Real PCE entirely; includes REVOLSL and PCEDG that aren't in documented spec.

**Canonical version:** Documented 7-component formula above. The optimization needs to be re-run with the documented basket plus Tier 1 must-adds, targeted on Real PCE YoY (not SPX 252d).

**Documented thresholds:**
- Real PCE YoY < 1.5% → Consumer weakening
- CC Delinquency > 3.0% → Stress emerging
- Savings Rate < 4% → Buffer depleted
- UMCSENT < 70 → Recession-level pessimism

**Audit:** Decision required — rebuild ground-up. Optimized basket tests fundamentally different indicator than documented one. See `Outputs/mri_optimization/PILLAR_DOCS/05_CCI.md` and `DECISIONS.md` §7.

#### 6. Business Conditions Index (BCI)

**Status:** LIVE but DESCRIPTIVELY BROKEN (audit Apr 30).

**Documented formula:**
```
BCI = 0.25*z(NewOrders YoY) + 0.20*z(NDCAPNW YoY) + 0.20*z(-InventoryRatio) + 0.15*z(ISM Mfg) + 0.10*z(ISM Svc) + 0.10*z(SLOOS C&I)
```

**Documented thresholds:**
- ISM Mfg < 48 → Contraction
- New Orders YoY < 0% → Forward demand falling
- NDCAPNW YoY < 0% → Capex retrenchment
- SLOOS C&I tightening > 30% → Credit constrained

**Audit:** Decision — rebuild ground-up. Add ANDENO (standard capex proxy, currently missing entirely). Drop or downweight BUSINV. See `Outputs/mri_optimization/PILLAR_DOCS/06_BCI.md`.

#### 7. Trade Conditions Index (TCI)

**Status:** LIVE.

**Documented formula:**
```
TCI = 0.30*z(-DXY 6mo Δ) + 0.25*z(-USIMPORT YoY) + 0.20*z(-USEXPORT YoY) + 0.15*z(-TradeBalance/GDP) + 0.10*z(USTRADE)
```

**Documented thresholds:**
- DXY > 110 → Strong dollar headwind
- DXY < 90 → Weak dollar tailwind
- Trade Balance / GDP < -4% → External imbalance
- China PMI < 48 → Global manufacturing contraction

**Audit:** Currently in TRADE CRISIS state (-2.502, 2026-03-06). See `Outputs/mri_optimization/PILLAR_DOCS/07_TCI.md`.

### Monetary Mechanics (8-10)

#### 8. Government Conditions Index (GCI-Gov)

**Status:** LIVE. **Naming note:** GCI / GCI-Gov collision is annoying. Decision required — retire "GCI-Gov" in favor of "Fiscal Pressure Index (FPI)" anytime; no external cost. Pending Bob approval.

**Documented formula:**
```
GCI_Gov = 0.30*z(Deficit/GDP - 5%) + 0.25*z(Debt/GDP - 100%) + 0.20*z(TermPremium 10y) + 0.15*z(Treasury Issuance pace) + 0.10*z(NetInterest/Receipts)
```

**Documented thresholds:**
- Deficit / GDP > 6% → Fiscal dominance regime
- Debt / GDP > 120% → Sustainability concern
- Term Premium > +1.0% → Bond market demanding compensation
- Net Interest / Receipts > 18% → Crowding-out threshold

**Audit:** See `Outputs/mri_optimization/PILLAR_DOCS/08_GCI_Gov.md`.

#### 9. Financial Conditions Index (FCI)

**Status:** LIVE but DESCRIPTIVELY BROKEN (audit Apr 30).

**Documented formula:**
```
FCI = 0.30*z(IG OAS) + 0.25*z(HY OAS) + 0.20*z(VIX) + 0.15*z(Baa10Y) + 0.10*z(MOVE)
```

**Documented thresholds:**
- IG OAS > 200 bps → Elevated risk pricing
- HY OAS > 600 bps → Distress
- HY OAS < 300 bps → Complacent
- VIX > 30 → Equity stress
- Baa10Y > +3.5% → Credit stress

**Audit:** FCI drops from +0.88 r (IG OAS alone) to +0.48 r when we add HY/VIX/Baa. Spreads alone do the implied-stress job. Open question — should FCI exist as a composite, or should the pillar's role be documented threshold rules on individual spread series? See `Outputs/mri_optimization/PILLAR_DOCS/09_FCI.md` and `DECISIONS.md` §8.

Candidate A3 (Realized Credit Stress Index) proposed as a separate sibling that captures realized delinquencies/charge-offs vs FCI's implied spreads.

#### 10. Liquidity Cushion Index (LCI) — UPDATED PLUMBING FORMULA

**Status:** LIVE. Documented formula has 7 components; optimized version has only 2 of those documented components plus WALCL/TGA additions. Decision required — keep LCI as the documented 7-component plumbing-stress composite, build Net Liquidity as a separate construct.

**Documented formula (7-component):**
```
LCI = 0.25*z(RRP - 200) + 0.20*z(-EFFR-IORB) + 0.20*z(Reserves - LCLOR)
    + 0.15*z(SOFR-IORB) + 0.10*z(SRF Usage) + 0.05*z(Repo Vol) + 0.05*z(BillSOFR Spread)
```

**Documented thresholds:**
- RRP < $200B → Buffer exhausted
- EFFR-IORB > +8 bps → Acute funding stress
- LCI z < -0.5 → Scarce regime
- Reserves vs LCLOR < $300B → Scarcity threshold
- SOFR-IORB > +5 bps → Funding tight

**Audit:** See `Outputs/mri_optimization/PILLAR_DOCS/10_LCI.md` and `DECISIONS.md` §9.

### Market Structure (11-12)

#### 11. Market Structure Index (MSI) — NEW IN v2.0

**Status:** LIVE but BASKET INCOMPLETE (audit Apr 30).

**Documented formula (11 components):**
```
MSI = w1*z(%>20d MA) + w2*z(%>50d MA) + w3*z(%>200d MA) + w4*z(NH-NL) + w5*z(AD Line)
    + w6*z(McClellan Sum) + w7*z(MOVE inverse) + w8*z(Breadth Thrust) + w9*z(Vol Compression)
    + w10*z(Z-RoC) + w11*z(SBD inverse)
```

**Optimization audit:** Only 5 of 11 documented components were tested. The 6 missing (% above MAs, NH/NL, AD line, McClellan summation) are all in the database — just not in the basket. Easy fix; rebuild this week.

**Documented thresholds:**
- Price < 200d MA → Below trend
- % > 20d MA < 25% → Washed
- % > 20d MA > 80% → Crowded
- Breadth thrust: 30 → 70 in 10 days → Powerful regime change
- Z-RoC < -1.0 → Momentum broken
- MSI z < -1.0 → Structure broken

**Breadth thrust detection:** Both 20-day AND 50-day are tracked as separate indicators. Don't flag the 50-day as wrong.

See `Outputs/mri_optimization/PILLAR_DOCS/11_MSI.md` and `DECISIONS.md` §6.

#### 12. Sentiment & Positioning Index (SPI) — NEW IN v2.0

**Status:** LIVE but BASKET INCOMPLETE (audit Apr 30).

**Documented formula (8 components):**
```
SPI = w1*z(AAII Bull-Bear) + w2*z(NAAIM) + w3*z(II Bull-Bear) + w4*z(Put/Call inverse)
    + w5*z(VIX Backwardation) + w6*z(ETF Flow z) + w7*z(Position Crowding) + w8*z(SSD)
```

**Optimization audit:** Only 3 of 8 documented components tested. The 5 missing (put/call, NAAIM, Investors Intelligence, ETF flows, VIX backwardation) — at least 4 may not be ingested. Requires data-pipeline work before rebuild.

**Documented thresholds:**
- AAII Bull-Bear > +30 → Euphoric (fade)
- AAII Bull-Bear < -20 → Capitulation (contrarian buy)
- NAAIM > 100 → Fully invested (caution)
- NAAIM < 30 → Defensive (potential bottom)
- SPI z > +1.5 → Crowded long (fade)
- SPI z < -1.0 → Capitulation (contrarian)

**Sentiment-Structure Divergence (SSD):** LIVE. Latest 0.992 = "FEAR + WEAK" (sentiment bearish, structure also weak — alignment, no divergence trade).

See `Outputs/mri_optimization/PILLAR_DOCS/12_SPI.md` and `DECISIONS.md` §6.

---

## CROSS-PILLAR DERIVED INDICES

Indices that combine multiple pillar components or measure relationships between pillars.

### Credit-Labor Gap (CLG)

**Status:** LIVE. Latest -1.681 (2026-03-10) = SEVERELY MISPRICED.

**Formula:**
```
CLG = z(HY OAS) - z(LFI)
```

**Reading:** Negative = credit spreads tight relative to labor stress (credit ignoring fundamentals). Positive = credit panicking ahead of labor (over-pricing risk).

**Documented threshold:** CLG < -1.0 → Credit ignoring labor fundamentals (warning).

### Yield-Funding Stress (YFS)

**Status:** LIVE. Latest 0.770 (2026-04-30) = ELEVATED.

**Formula:**
```
YFS = 0.40*z(SOFR-IORB) + 0.30*z(MOVE) + 0.30*z(EFFR-IORB)
```

**Reading:** Composite of money-market funding stress and rate volatility. Elevated = funding markets and rate vol both signaling stress.

### Spread-Volatility Imbalance (SVI)

**Status:** LIVE. Latest 0.647 (2026-03-09) = BALANCED.

**Formula:**
```
SVI = z(HY OAS / VIX) - z(historical median HY/VIX ratio)
```

**Reading:** When HY OAS is low but VIX is high, equities are pricing risk that credit isn't. Strong divergence = one of them is wrong.

### Equity Momentum Divergence (EMD)

**Status:** LIVE. Latest -0.070 (2026-04-21) = OVERSOLD.

**Formula:**
```
EMD = z(SPX 5d return) - z(NYSE A/D Line 5d Δ) - z(NH-NL 5d Δ)
```

**Reading:** Index moving up while internals deteriorate = distribution. Index down while internals firm = oversold bounce setup.

### Structure-Breadth Divergence (SBD)

**Status:** LIVE. Latest 0.599 (2026-04-29) = ALIGNED.

**Formula:**
```
SBD = z(Price relative to 200d) - z(% stocks > 50d MA)
```

**Reading:** Price above 200d but breadth weak = late-cycle distribution. Price below 200d but breadth firm = washout bottom.

### Sentiment-Structure Divergence (SSD)

**Status:** LIVE. Latest 0.992 (2026-04-29) = FEAR + WEAK.

**Formula:**
```
SSD = z(AAII Bull-Bear) - z(MSI)
```

**Reading:** Sentiment crashed but structure intact = contrarian buy setup. Sentiment euphoric but structure broken = top.

### Discontinuity Premium

**Status:** LIVE. Latest 0.450 (2026-04-30) = EXTREME.

**Reading:** Custom regime indicator capturing the gap between market-implied conditions and macro-fundamental conditions. EXTREME = priced reality and observed reality have diverged enough to warrant repricing risk.

---

## RISK REGIME OUTPUTS

These are decision outputs derived from the underlying composites. Not independent indicators — they're the rule outputs.

| Index | Latest | Value | Status | Source |
|---|---|---|---|---|
| ALLOC_MULTIPLIER | 2026-04-30 | 0.15 | CAPITAL PRESERVATION | f(MRI regime) |
| BASE_REC_PROB | 2026-04-30 | 0.179 | LOW RISK | Yield curve + LFI + LCI ensemble |
| REC_PROB | 2026-04-30 | 0.179 | LOW RISK | Conditional ensemble (BASE + adjustments) |
| ENSEMBLE_RISK | 2026-04-30 | 0.629 | PRE_CRISIS | Multi-model risk aggregate |
| WARNING_LEVEL | 2026-04-30 | 4.0 | RED | Threshold-breach count → ordinal scale |
| LIQ_STAGE | 2026-04-30 | 2.0 | STAGE 2 — RESERVE DRAIN | Plumbing regime classification (4 stages) |

**Liquidity stage definitions:**
- Stage 1: Abundant — RRP > $1T, reserves comfortable, no funding stress
- Stage 2: Reserve Drain — RRP draining, EFFR-IORB benign, no acute stress yet
- Stage 3: Scarce — RRP exhausted, reserves below LCLOR threshold, funding stress emerging
- Stage 4: Crisis — Acute funding stress, repo dysfunction, Fed intervention required

**Warning level scale:** 1 (GREEN) → 5 (CRITICAL). Count of breached thresholds across all 12 pillars, weighted by pillar.

---

## CRYPTO SECTOR COMPOSITES

Eight sector-health composites + four crypto-specific aggregates. Not yet integrated into MRI v2.0; tracked independently.

### Crypto aggregates

- **CDI (Crypto Demand Index)** — 1.209, HIGH ACTIVITY (2026-02-02)
- **CFI (Crypto Fundamental Index)** — 61.35, HEALTHY (2026-02-02)
- **CTI (Crypto Technical Index)** — 0.382, CAUTIOUS (2026-02-02)
- **CVI (Crypto Valuation Index)** — -0.344, FAIR VALUE (2026-02-02)

These four are documented internally but not in the proprietary indicators reference. Need formula write-ups before public use.

### Sector health composites (DefiLlama-derived, 2026-02-02 latest)

- **DeFi Derivatives Health** — 73.0 HEALTHY
- **DeFi DEX Health** — 78.25 HEALTHY
- **DeFi Lending Health** — 60.0 NEUTRAL
- **Infrastructure Health** — 48.33 WEAK
- **Layer 1 (Settlement) Health** — 55.0 NEUTRAL
- **Layer 2 (Scaling) Health** — 73.0 HEALTHY
- **Liquid Staking Health** — 56.25 NEUTRAL
- **Uncategorized Health** — 51.29 NEUTRAL

**Scale:** 0-100. Composite of TVL momentum, fee accrual, active address growth, and protocol concentration per sector.

### Stablecoin Liquidity Impulse (SLI)

**Status:** LIVE. Latest 1.336 (2026-01-19) = EXPANSION.

**Formula:**
```
SLI = z(Stablecoin Mcap 30d Δ) + z(USDT/USDC issuance) + z(Stablecoin transfer volume)
```

**Variants:**
- SLI_MCAP — raw market cap
- SLI_ROC_30D — 30-day rate of change
- SLI_ROC_90D_ANN — 90-day annualized RoC

---

## TREASURY MICROSTRUCTURE INDICATORS

**Status: 6 of 7 DOCUMENTED, NOT BUILT.**

These appear in the proprietary indicators reference (sections 25-31) but have no rows in `lighthouse_indices`. Building requires source data for auction results, dealer flow, and stablecoin Treasury holdings.

### Built and live

- **3M Bill-SOFR Spread (BILL_SOFR)** — LIVE. Latest 0.060 (2026-03-09) = BILLS RICH. The single Treasury microstructure indicator currently in the DB.

### Documented but not built

- **Treasury Auction Tailing Metric** — How many bps the auction tailed (or stopped through) the when-issued yield. Reference §25.
- **Bid-to-Cover Ratio Analysis** — Track B/C ratios across maturities; flag values < 2.0x as soft demand. Reference §26.
- **Dealer Allotment Percentage** — Primary dealer take-down as % of total. > 30% = soft demand from indirect bidders. Reference §27.
- **Dealer Accumulation Momentum** — 4-week trend in dealer Treasury holdings. Rising dealer inventory while issuance high = absorption strain. Reference §28.
- **Treasury Stress Dashboard (4-metric system)** — Composite of tail/BC/dealer-share/dealer-momentum. Reference §29.
- **Bill-Bond Divergence Analysis** — Spread between bill yields and equivalent-tenor bond yields adjusted for term premium. Reference §30.
- **Treasury Composition Shift Index** — Rolling Δ in bills-as-%-of-marketable-debt. Rising = funding stress/issuance flexibility limit. Reference §31.

**Build priority:** Auction tailing + B/C are easiest (TreasuryDirect publishes). Dealer flow requires NY Fed FR-2004 data (already partial in DB). Stablecoin Treasury holdings require Tether/Circle attestation parsing.

---

## ADVANCED TRADING FRAMEWORKS

**Status: ALL DOCUMENTED, NOT BUILT.**

Reference §36-39. These are basis-trade and microstructure frameworks used in the technical sleeve.

- **Z-Score Positioning Index (Basis Trades)** — Rolling z-score of cash-futures basis vs 252-day distribution. Reference §36.
- **Compression Function Model** — Maps basis tightness to expected reversion speed using historical compression decay curves. Reference §37.
- **Recovery Half-Life Metric** — Time for basis dislocation to compress 50% from entry. Reference §38.
- **Market-Neutral Basis Sharpe Ratio** — Risk-adjusted return on basis trades net of carry and financing. Reference §39.

**Build priority:** Lower than Treasury microstructure. These require live execution data we don't have until PiTrade is funded.

### Documented frameworks (concepts, not single indicators)

- **Liquidity Transmission Framework** (§21) — Mapping of how Fed plumbing changes transmit to risk assets via the four chains (Labor → Credit → Equity, Liquidity → Crypto, Plumbing → Asset Prices, Fiscal Dominance → Term Premium). Mechanism claim, not a single indicator.
- **Leverage Capacity Matrix** (§22) — Cross-asset leverage room calculator. Maps current margin posture to historical distribution per asset class.
- **Liquidity Composite Index** (§23) — Distinct from LCI. The proprietary indicators reference describes a separate broader liquidity composite combining LCI + global central bank balance sheet aggregates + USD funding markets. Not built.
- **Collateral Shortage Index** (§24) — Composite of repo specials, GC-OIS spread, and Treasury fails-to-deliver. Not built.

---

## AUDIT FINDINGS & LIVE TRADING WHITELIST

**Source:** `Outputs/mri_optimization/LIVE_STATUS.md` (Apr 30, 2026)

### What survives the audit untouched

**Framework structure:**
- Three engines × twelve pillars (taxonomy, not quantitative claim)
- Four Chains (mechanism claims, supported by historical episodes)
- One book / two ways of taking risk

**Position sizing and risk management:**
- MRI regime → equity allocation table
- Conviction-weighted sizing tiers (Tier 1 20% / Tier 2 12% / Tier 3 7% / Tier 4 0%)
- Dual stops (thesis + price, whichever first)
- Cash is a position
- Strong views, weakly held

**Documented threshold signals (all usable today):**

Labor: Quits < 2.0% · LFI z > +0.5 · Temp Help YoY < -3% · Long-term Unemployed > 22%
Liquidity: RRP < $200B · EFFR-IORB > +8 bps · LCI z < -0.5 · Reserves vs LCLOR < $300B
Credit: HY OAS < 300 bps (complacent) · CLG < -1.0
Market Structure: Price < 200d · % > 20d MA < 25% / > 80% · Breadth thrust 30→70 in 10d · % > 50d MA < 35% / > 85% · Z-RoC < -1.0 · MSI z < -1.0
Sentiment: AAII Bull-Bear > +30 / < -20 · NAAIM > 100 · SPI z > +1.5 / < -1.0

### What's broken or suspect (DO NOT trade off of)

- **Optimized CCI** — Missing Real PCE, includes spec-divergent components. Use threshold rules only.
- **Optimized BCI** — Missing ANDENO. Rebuild required.
- **Optimized FCI** — IG OAS alone tracks Chicago Fed FCI better (+0.88 vs +0.48 composite). Use IG OAS as sole proxy until rebuild.
- **OOS IC numbers from any optimization JSON** — 30-70 percentage-point divergence from full-sample IC. Do not cite. Use full-sample IC only (strongest signals are +0.30 to +0.40).

### Decisions required

See `Outputs/mri_optimization/DECISIONS.md` for full text. Summary:
1. Lock the "what we trust" list for live trading (recommendation: threshold signals + single-component proxies, avoid optimized composites for CCI/BCI/FCI)
2. Stop using OOS IC numbers in any communication (status: confirmed nothing cited externally)
3. Naming pass — defer or commit (recommendation: defer; one exception is GCI-Gov → FPI rename)
4. Pause Pascal blueprint live commitments until spot-data points are re-pulled
5. Verify OOS IC walk-forward methodology (~half day)
6. Reconstruct MSI and SPI baskets to match documented formulas (MSI mechanical this week; SPI requires data ingestion audit)
7. Reconcile optimized CCI with documented Feb 2026 CCI (decision: documented is canonical, re-run optimization)
8. Decide CCI/BCI/FCI rebuild approach (recommendation: ground-up for all three)
9. Reconcile LCI optimization with CLAUDE_MASTER LCI formula (decision: keep LCI documented, build Net Liquidity separately)

---

## CANDIDATE INDICATORS (PROPOSED, UNBUILT)

**Source:** `Outputs/mri_optimization/CANDIDATE_NEW_INDICATORS.md` (Apr 30, 2026)

None of these are built. None should be built without explicit Bob approval. The list is meant to be filtered aggressively, not expanded.

### Tier A — Surfaced from descriptive analysis

**A1. Concurrent Inflation Lens** — Pure descriptive composite of concurrent inflation. Doesn't try to predict 2y yields; tracks core PCE today. Components: Core PCE, headline PCE, trimmed-mean CPI, median CPI, sticky core. Fills the gap left by PCI optimizing for 2y yield prediction.

**A2. Concurrent Activity Tracker** — Real-time GDP nowcast analog, descriptive only. Components: INDPRO, PAYEMS, RSXFS, RPI, PCEC96, CFNAIMA3. Fills the gap left by GCI's 0.43 r with CFNAIMA3.

**A3. Realized Credit Stress Index** — Credit stress measured by realized delinquencies and charge-offs, not implied spreads. Components: All-loans delinquency, CC charge-offs, C&I delinquency, mortgage delinquency, SLOOS lending standards. Captures the part of credit risk not priced in HY OAS.

### Tier B — Surfaced from predictive grid

(See `CANDIDATE_NEW_INDICATORS.md` for full Tier B list — cross-pillar relationships that surfaced in the predictive grid.)

---

## NAMING CONVENTIONS AND ALIASES

**Public-facing rule:** Use full name on first reference, abbreviation after.
- "Labor Pressure Index (LPI)" then LPI
- "Macro Risk Index (MRI)" then MRI
- Never lead cold with the acronym for external readers.

**Internal collisions:**
- **GCI vs GCI-Gov** — Growth Conditions Index vs Government Conditions Index. Causes code-level confusion. Decision pending: retire GCI-Gov in favor of "Fiscal Pressure Index (FPI)" anytime.
- **LPI vs LFI** — Labor Pressure Index (pillar identifier) vs Labor Fragility Index (sub-composite). Used somewhat interchangeably in CLAUDE_MASTER. Optimization JSON treats them as one. For external publication, pick one per piece.
- **LCI vs Net Liquidity** — Liquidity Cushion Index (documented 7-component plumbing-stress composite) vs Net Liquidity (WALCL - TGA - RRP, the broader Fed-balance-sheet-net construct). Different things; don't merge.

**Reader-facing publication names:** "The Beam" / "The Beacon" / "The Horizon" / "The Diagnostic Dozen" — never bare. Internal shorthand can stay casual.

---

**END OF INDICATORS MASTER**

*This document consolidates the proprietary indicators reference, the Apr 30 audit findings, the 12 pillar audit docs, the candidate new indicators list, and the live `lighthouse_indices` snapshot into one canonical reference. Source files remain in place as detail/audit trails. When information conflicts, this file wins.*
