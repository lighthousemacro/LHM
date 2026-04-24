# THE TWO BOOKS FRAMEWORK
## Core Book & Technical Overlay Book

**Version:** 1.0
**Date:** January 20, 2026
**Author:** Bob Sheehan, CFA, CMT

*"MACRO, ILLUMINATED."*

---

## Philosophy

True global macro is directional, not directionally constrained. Soros didn't break the Bank of England by being too bullish on the UK's currency. He shorted the shit out of the pound. We are directional macro, not relative value. We have views. In a world where prices go up most of the time, our bias will be towards owning as opposed to shorting. The framework accommodates wherever the thesis takes us: long or short.

The distinction between the two books isn't about direction or duration. It's about what drives the position:

- **Core Book:** Position follows a macro/fundamental thesis
- **Technical Overlay:** Position follows price structure alone

**Critical Insight:** The books are entry frameworks, not holding period constraints. The moment you own something, you're managing a position. Entry logic determines how you get in. Price and drivers determine how long you stay.

---

## Portfolio Structure

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         THE TWO BOOKS                                            │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  CORE BOOK (50-100% of capital)                                                 │
│  ─────────────────────────────────                                              │
│  • Macro + Fundamental + Technical driven                                       │
│  • LONG OR SHORT based on thesis                                                │
│  • MRI regime multiplier applies to sizing                                      │
│  • Thesis-driven entry with 3-6 month catalyst horizon                          │
│  • Full position sizing (up to 20% per position)                                │
│  • Can go to 100% cash when no setups qualify                                   │
│                                                                                  │
│  TECHNICAL OVERLAY BOOK (0-50% of capital)                                      │
│  ─────────────────────────────────────────                                      │
│  • Pure technical (trend + momentum + relative strength)                        │
│  • LONG OR SHORT based on price structure                                       │
│  • Activated when Core Book is defensive (MRI > +1.0)                           │
│  • No macro thesis required, following price                                    │
│  • Sizing at 50% of Core (max 10% longs, 5% shorts per position)                │
│  • Tighter stops (10% longs, 8% shorts)                                         │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## Core Book

### Entry Framework

The Core Book requires convergence across the three-engine framework:

| Engine | Focus | Key Question |
|--------|-------|--------------|
| **Macro Dynamics** | Pillars 1-7 (Labor, Prices, Growth, etc.) | What's the fundamental thesis? |
| **Monetary Mechanics** | Pillars 8-10 (Fiscal, Credit, Plumbing) | Is liquidity supportive or restrictive? |
| **Market Structure** | Pillars 11-12 (Structure, Sentiment) | Is price confirming the thesis? |

### Direction

**Long or Short based on thesis.** Examples:

- **Long thesis:** Labor stable, liquidity ample, structure confirming, sentiment washed
- **Short thesis:** Labor deteriorating, credit complacent (CLG < -1.0), structure breaking, sentiment euphoric

### Position Sizing

```
Position Size = Base Weight × Conviction Multiplier × Regime Multiplier
```

| Conviction Tier | Score | Base Weight |
|-----------------|-------|-------------|
| Tier 1 | 16-19 pts | 20% |
| Tier 2 | 12-15 pts | 12% |
| Tier 3 | 8-11 pts | 7% |
| Tier 4 | <8 pts | 0% (avoid) |

| MRI Regime | Multiplier |
|------------|------------|
| Supportive (< +0.5) | 1.0x |
| Neutral (+0.5 to +1.0) | 0.6x |
| Restrictive (> +1.0) | 0.3x |

### Dual Stop System

Every Core Book position has TWO stops:

**1. Thesis Stop (Fundamental)**
- Revenue declines 3 consecutive quarters
- Key indicator crosses invalidation threshold
- Macro regime shift against thesis

**2. Price Stop (Technical)**
- Price closes below 200d MA (longs) / above 200d MA (shorts)
- Z-RoC drops below -1.0 (longs) / rises above +1.0 (shorts)
- 15% drawdown from entry (hard stop)

**Use whichever triggers first.**

---

## Technical Overlay Book

### Concept

When the Core Book is defensive (MRI > +1.0) and regime multipliers compress position sizes, clear technical trends can still exist. The Technical Overlay Book provides a structured way to follow price when macro is uncertain but trends are evident.

**This is not shorter-term trading.** Price trends can last years to decades. The distinction is about drivers, not duration.

### Activation Criteria

```
TECHNICAL BOOK ACTIVATION CHECKLIST:
────────────────────────────────────
[ ] Core Book is in defensive mode (MRI > +1.0)
[ ] At least 3 clear technical setups exist (long OR short)
[ ] BTC or SPX showing directional trend (not chop)
[ ] You explicitly decide to activate (not automatic)

ALL conditions must be met.
```

### 12-Point Scoring System

Three components, 4 points each. Clean 2:1 ratio to Core Book's 24 points.

| Component | Points | What It Measures |
|-----------|--------|------------------|
| **Trend Structure** | 0-4 | Price vs 50d vs 200d alignment + slope |
| **Momentum (Z-RoC)** | 0-4 | Direction, magnitude, and trajectory |
| **Relative Strength** | 0-4 | vs BTC/SPX (multiple timeframes + slope) |

**Minimum score to enter: 8/12**

#### Trend Structure Scoring (0-4 pts)

| Condition (Longs) | Condition (Shorts) | Points |
|-------------------|-------------------|--------|
| Price > 50d > 200d, both rising, 50d slope steepening | Price < 50d < 200d, both falling, 50d slope steepening | 4 |
| Price > 50d > 200d, both rising | Price < 50d < 200d, both falling | 3 |
| Price > 50d > 200d, MAs flat | Price < 50d < 200d, MAs flat | 2 |
| Price > 50d, 50d near/crossing 200d | Price < 50d, 50d near/crossing 200d | 1 |
| Price < 50d (longs) / > 50d (shorts) | - | 0 |

#### Momentum Scoring (0-4 pts)

**Longs:** Absolute Z-RoC level matters. Higher = stronger momentum confirmation.

| Z-RoC Condition (Longs) | Points |
|-------------------------|--------|
| > +1.5, rising | 4 |
| > +1.0 | 3 |
| +0.5 to +1.0 | 2 |
| 0 to +0.5 | 1 |
| < 0 | 0 |

**Shorts:** Trajectory and divergence matter more than absolute level. Z-RoC is confirming, not primary.

| Z-RoC Condition (Shorts) | Points |
|--------------------------|--------|
| Declining + bearish divergence + Z-RoC < 0 | 4 |
| Declining + bearish divergence (Z-RoC any level) | 3 |
| Declining (no divergence yet) | 2 |
| Flat or mixed | 1 |
| Rising | 0 |

*Note: For shorts, waiting for Z-RoC to reach deeply negative levels means missing the move. Trend and relative strength are primary; momentum confirms via trajectory.*

#### Relative Strength Scoring (0-4 pts)

| Condition (Longs) | Condition (Shorts) | Points |
|-------------------|-------------------|--------|
| Outperforming 63d AND 252d, RS slope positive | Underperforming 63d AND 252d, RS slope negative | 4 |
| Outperforming 63d AND 252d | Underperforming 63d AND 252d | 3 |
| Outperforming 63d OR 252d | Underperforming 63d OR 252d | 2 |
| Flat relative (within 5% of benchmark) | Flat relative | 1 |
| Underperforming (longs) / Outperforming (shorts) | - | 0 |

### Position Limits

| Parameter | Longs | Shorts |
|-----------|-------|--------|
| Max per position | 10% | 5% |
| Max total Technical Book | 50% | 50% |
| Hard stop | 10% | 8% |
| Technical stop | Close below 50d MA | Close above 50d MA |
| Momentum stop | Z-RoC crosses below 0 | Z-RoC crosses above 0 |
| Time stop | 20 trading days | 20 trading days |

### Short-Specific Requirements

Shorts have additional hurdles:

```
SHORT ENTRY CHECKLIST (All must be true):
─────────────────────────────────────────
[ ] Price < 50d < 200d (both MAs falling)
[ ] Z-RoC declining with bearish divergence (trajectory > level)
[ ] Relative strength RED on both 63d and 252d
[ ] Clear breakdown pattern (not just weakness)
[ ] NOT extended (price not >10% below 50d MA)
[ ] Score ≥ 8/12
```

*Key insight: For shorts, Z-RoC trajectory and divergence matter more than absolute level. Trend and relative strength are the primary drivers. By the time Z-RoC is deeply negative, the move is already underway.*

---

## Position Graduation

**The key insight:** A Technical Book position can graduate to Core Book treatment when fundamental drivers emerge.

### Scenario: Technical Entry → Fundamental Confirmation

1. Enter position in Technical Book (pure price-driven)
2. Hold for 3 months following trend
3. Macro regime shifts, MRI improves
4. Fundamental catalyst emerges for the position
5. **The position now has both engines firing**

**Action:** The position graduates. You can:
- Size up to Core Book weights (if conviction score supports)
- Shift to Core Book stop framework (thesis + price stops)
- Extend holding period expectation

### Scenario: Core Book Entry → Macro Uncertainty

1. Enter position in Core Book (thesis-driven)
2. Thesis plays out partially
3. MRI deteriorates, Core Book goes defensive
4. Position still has strong technical structure

**Action:** The position can remain, but:
- Sizing governed by Technical Book limits
- Stops tighten to Technical Book framework
- Monitor for thesis repair or technical breakdown

---

## Integration Rules

### When Core is Active (MRI < +1.0)

- Core Book: 50-100% allocation
- Technical Overlay: 0-50% allocation
- **Core takes priority for capital allocation**

### When Core is Defensive (MRI > +1.0)

- Core Book: Reduced exposure (regime multiplier 0.3x or lower)
- Technical Overlay: Can expand to 50% if setups exist
- **Technical provides a way to stay engaged without violating macro discipline**

### Capital Allocation Priority

1. Core Book positions with both thesis AND technical confirmation
2. Core Book positions with thesis (technical neutral)
3. Technical Overlay positions with strong scores
4. Cash

---

## What the Books Are NOT

**The Technical Overlay Book is NOT:**
- A way to override macro when impatient
- A license to trade every setup
- A replacement for the Core Book
- Active all the time
- An excuse to ignore MRI signals

**The Core Book is NOT:**
- Long only (true global macro is directional)
- Restricted to 3-6 month holds (that's the catalyst horizon, not the exit requirement)
- Blind to price (technicals confirm the thesis)

---

## Absolute Rules (Apply to Both Books)

| Rule | Condition | Override |
|------|-----------|----------|
| **#1: Below 200d** | Price < 200d MA | Conditional (mature downtrend >60d allows tactical) |
| **#2: Death Cross** | 50d < 200d | Conditional (>60 days allows tactical) |
| **#3: Red Relative** | Underperforming benchmark | **UNCONDITIONAL - never override** |
| **#4: Z-RoC Broken** | Z-RoC < -1.0 (longs) | Reduce 50% minimum, full exit if combined |
| **#5: Extended** | >15% above 50d MA | **UNCONDITIONAL - never chase** |

---

## Summary

| Attribute | Core Book | Technical Overlay |
|-----------|-----------|-------------------|
| **Driver** | Macro/Fundamental thesis | Price structure |
| **Direction** | Long or short | Long or short |
| **Allocation** | 50-100% | 0-50% |
| **Max Position** | 20% | 10% (longs), 5% (shorts) |
| **Scoring** | 24-point (Tech + Fundy + Micro) | 12-point (Trend + Momo + RS) |
| **Stops** | Dual (Thesis + Price) | Price only (tighter) |
| **Duration** | Determined by drivers | Determined by price |
| **When Active** | Always available | When Core is defensive |

**The books are entry taxonomies, not duration boxes. Entry logic determines how you get in. Price and drivers determine how long you stay.**

---

*That's our view from the Watch. Until next time, we'll be sure to keep the light on....*

*Bob Sheehan, CFA, CMT*
*Founder & CIO, Lighthouse Macro*

---

**MACRO, ILLUMINATED.**
