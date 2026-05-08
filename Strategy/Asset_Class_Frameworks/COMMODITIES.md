# Asset Class Framework: Commodities

## Primary ETF Universe

### Broad Commodities
| Ticker | Name | Expense | Use Case |
|--------|------|---------|----------|
| **DBC** | Invesco DB Commodity Index | 0.87% | Broad commodity exposure |
| **GSG** | iShares S&P GSCI | 0.75% | Energy-heavy broad |
| **PDBC** | Invesco Optimum Yield Diversified | 0.59% | K-1 free, roll-optimized |

### Energy
| Ticker | Name | Expense | Use Case |
|--------|------|---------|----------|
| **USO** | United States Oil Fund | 0.79% | WTI crude (front-month, contango drag) |
| **BNO** | United States Brent Oil | 0.90% | Brent crude |
| **UNG** | United States Natural Gas | 1.06% | Natural gas (high volatility, contango) |
| **XLE** | Energy Select Sector SPDR | 0.10% | Energy equities (preferred) |
| **XOP** | SPDR S&P Oil & Gas E&P | 0.35% | E&P equities |

### Precious Metals
| Ticker | Name | Expense | Use Case |
|--------|------|---------|----------|
| **GLD** | SPDR Gold Shares | 0.40% | Gold exposure |
| **IAU** | iShares Gold Trust | 0.25% | Gold (lower cost) |
| **SLV** | iShares Silver Trust | 0.50% | Silver |
| **GDX** | VanEck Gold Miners | 0.51% | Gold miners (leveraged gold beta) |

### Industrial Metals
| Ticker | Name | Expense | Use Case |
|--------|------|---------|----------|
| **CPER** | United States Copper Index | 0.88% | Copper |
| **DBB** | Invesco DB Base Metals | 0.77% | Copper, aluminum, zinc |

### Agriculture
| Ticker | Name | Expense | Use Case |
|--------|------|---------|----------|
| **DBA** | Invesco DB Agriculture | 0.85% | Broad agriculture |
| **CORN** | Teucrium Corn Fund | 1.14% | Corn |
| **WEAT** | Teucrium Wheat Fund | 1.14% | Wheat |

---

## Pillar-to-Commodity Translation

### Prices Pillar (PCI) → Inflation Hedge

| PCI Range | Regime | Commodity Stance | Preferred |
|-----------|--------|------------------|-----------|
| > +1.0 | High Inflation | **Overweight** | GLD, DBC, TIPS |
| +0.5 to +1.0 | Elevated | Tactical allocation | GLD |
| -0.5 to +0.5 | On Target | Neutral | Market weight |
| < -0.5 | Deflationary | **Underweight** | Avoid |

### Growth Pillar (GCI) → Demand Signal

| GCI Range | Regime | Industrial Commodities | Energy |
|-----------|--------|------------------------|--------|
| > +0.5 | Expansion | Overweight (DBB, CPER) | Overweight |
| -0.5 to +0.5 | Neutral | Neutral | Neutral |
| < -0.5 | Contraction | **Underweight** | Underweight |

### Dollar Channel

| DXY Direction | Impact | Trade |
|---------------|--------|-------|
| DXY falling | Bullish commodities | Add DBC, GLD |
| DXY rising | Bearish commodities | Reduce exposure |
| DXY < 100 | Significant tailwind | Overweight |
| DXY > 105 | Significant headwind | Underweight |

---

## Gold Framework (Primary Commodity Allocation)

### Gold Drivers

1. **Real Rates** (inverse): Lower real rates = higher gold
2. **Dollar** (inverse): Weaker dollar = higher gold
3. **Uncertainty**: Geopolitical/financial stress = higher gold
4. **Central Bank Demand**: Structural bid from EM central banks

### Real Rate → Gold Relationship

| 10Y Real Rate | Gold Stance |
|---------------|-------------|
| > +2.0% | Underweight |
| +1.0 to +2.0% | Neutral |
| 0 to +1.0% | Overweight |
| < 0% | **Strong overweight** |

### Gold Regime Matrix

| Real Rates | Dollar | Gold Signal |
|------------|--------|-------------|
| Falling | Falling | **Strong Buy** |
| Falling | Rising | Buy (real rates dominate) |
| Rising | Falling | Neutral |
| Rising | Rising | **Sell** |

### Gold Allocation by MRI

| MRI Range | Gold Allocation |
|-----------|-----------------|
| < +0.5 | 0-3% |
| +0.5 to +1.0 | 3-5% |
| +1.0 to +1.5 | 5-8% |
| > +1.5 | 8-12% |

---

## Energy Framework

### Oil Drivers

1. **Global Growth** (GCI): Demand signal
2. **OPEC+ Policy**: Supply management
3. **Inventories**: Weekly EIA data
4. **Geopolitics**: Supply disruption risk

### Oil → Inflation Pass-Through

| WTI Level | CPI Impact | Signal |
|-----------|------------|--------|
| > $100 | +0.3-0.5 pp to headline | Inflationary |
| $75-100 | Neutral | Baseline |
| $60-75 | -0.1-0.2 pp | Disinflationary |
| < $60 | Demand destruction signal | Deflationary |

### Energy expression — the XLE / PDBC split

The framework expresses energy through two complementary lines, not one. Each captures a different piece of the thread, and they trigger on a deliberately asymmetric Iran path.

| Line | Captures | Benchmark | Why this bench |
|---|---|---|---|
| **XLE** | Equity-operator pricing power, capital discipline, dividend yield from integrated and E&P names. Operational leverage to WTI without futures-curve drag. | **SPY** | Sector ETF benched against the PiTrade portfolio benchmark; the position-level RS gate must match the headline-level scoreboard. |
| **PDBC** | Direct fiscal-dominance and inflation-pass-through commodity exposure. K-1-free, 1099 reporting (no partnership tax friction). Roll-optimized to mitigate contango drag versus naive front-month exposure. | **KMLM** | Cross-asset macro hedge against the managed-futures CTA bench, which carries trend exposure across rates, currencies, and commodities — the right peer set for a direct-commodity expression. |

**Asymmetric Iran trigger.** The Iran path resolves either direction with different consequences for each line, and the trigger structure is built around that asymmetry.

| Iran resolution | XLE | PDBC | Reasoning |
|---|---|---|---|
| WTI re-anchors **above $85** (deal collapses, supply premium re-priced) | Fires | Fires | Both threads work. Operators get pricing power, commodity gets pass-through. |
| WTI breaks **below $78** (deal completes, Strait reopens, supply normalizes) | Fires (smaller) | **Stays cash** | XLE's equity-operator capital-discipline thesis still works at lower WTI; the dividend-and-buyback profile of US E&P is structural. PDBC's commodity-pass-through thesis invalidates on a deal that re-supplies the market. |

**On direct commodity ETFs.** Earlier framework drafts blanket-avoided direct commodity ETFs (USO, UNG) for contango roll drag, tracking error, and K-1 tax friction. PDBC is the explicit exception: roll-optimized, K-1-free, and the cleanest off-the-shelf vehicle for direct-commodity exposure when the framework wants pass-through rather than equity-operator beta. Naive single-commodity ETFs (USO, UNG, BNO) remain disfavored for the same reasons; the avoidance was about structure, not about commodities-as-an-expression.

**Position sizing.** The two lines size independently. In the May 2026 launch book each line targets 5%, with both staged behind the trigger structure above. Combined energy exposure tops out at ~10% of book on a both-fire path, which is the framework's standing energy ceiling for fiscal-dominance regimes.

---

## Industrial Metals as Growth Signal

### Copper ("Dr. Copper")

Copper demand is ~50% from China and highly cyclical. Copper prices often lead global industrial production.

| Copper Signal | Implication |
|---------------|-------------|
| Copper up, equities up | Confirmed expansion |
| Copper up, equities flat | Early cycle recovery |
| Copper down, equities up | Divergence warning |
| Copper down, equities down | Confirmed contraction |

### When to Own Industrial Metals

- GCI > 0 AND PMIs expanding → DBB, CPER
- China stimulus announced → Copper rally likely
- Infrastructure bill passage → Metals demand

---

## Position Sizing

### Commodity Allocation by Regime

| MRI Regime | Total Commodities | Gold | Energy | Industrial |
|------------|-------------------|------|--------|------------|
| Low Risk | 5-10% | 2-3% | 2-4% | 1-3% |
| Neutral | 5-8% | 2-3% | 2-3% | 1-2% |
| Elevated | 8-12% | 3-5% | 3-5% | 2-2% |
| High Risk | 10-15% | 5-8% | 3-5% | 2-2% |
| Crisis | 8-15% | 8-12% | 0-3% | 0% |

### Roll Yield Consideration

For direct commodity ETFs, check the futures curve:
- **Backwardation** (near > far): Positive roll yield, ETF outperforms spot
- **Contango** (near < far): Negative roll yield, ETF underperforms spot

---

## Current Assessment Template

| Metric | Reading | Signal |
|--------|---------|--------|
| **WTI Crude** | | Energy |
| **Gold** | | Safe haven |
| **Copper** | | Growth |
| **DXY** | | Dollar impact |
| **10Y Real Rate** | | Gold driver |
| **GCI** | | Demand regime |
| **PCI** | | Inflation regime |

*Update dynamically with current readings.*

---

*Bob Sheehan, CFA, CMT*
*Founder & CIO, Lighthouse Macro*
