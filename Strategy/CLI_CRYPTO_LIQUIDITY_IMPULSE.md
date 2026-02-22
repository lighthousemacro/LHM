# CRYPTO LIQUIDITY IMPULSE (CLI)

**Status:** Built & Backtested
**Version:** 1.0 (Final)
**Created:** February 12, 2026
**Author:** Bob Sheehan, CFA, CMT | Lighthouse Macro

---

## What It Is

A weighted z-score composite measuring how fast global liquidity transmits into crypto. Positive CLI = expanding liquidity impulse. Negative = contracting. "Impulse" (not "Flow") because the indicator measures rate of change (second derivative), not cumulative direction.

Originally named CLTI (Crypto Liquidity Transmission Index), renamed to CLI after an unfortunate phonetic resemblance. "Index" dropped to match existing LHM naming convention (LPI, PCI, GCI, etc.).

---

## Origin

Developed for Pascal Hügli's "What is REALLY driving Bitcoin's price?" report (Feb 2026). CLI was Bob's #1 indicator pick, paired with Technical Structure as #2 (200d MA slope, vol-adjusted Z-RoC, relative strength). MVRV Z-Score was demoted to honorable mention: useful as a valuation lens but not a timing tool.

---

## WHAT'S ACTUALLY BUILT (4 Components)

This is the tested, validated model that produced the backtest results and charts.

### Final Weights (from `cli_final.py`)

```python
FINAL_WEIGHTS = {
    'DollarYoY':      0.20,   # Inverted DTWEXBGS YoY change
    'ResRatio_RoC':   0.50,   # 63d rate of change of Reserves/WALCL
    'StableBTC_RoC':  0.15,   # Inverted 21d RoC of stablecoin mcap / BTC ratio
    'ResRatio':       0.15,   # Reserves/WALCL level
}
```

### Component Detail

| Component | Weight | Construction | Data Source | What It Captures |
|---|---|---|---|---|
| Dollar YoY (inv) | 20% | -(DTWEXBGS / DTWEXBGS[252d] - 1) | FRED: DTWEXBGS | Dollar momentum as global risk appetite proxy |
| Reserve Ratio RoC | 50% | (Res/WALCL) / (Res/WALCL)[63d] - 1 | FRED: TOTRESNS, WALCL | Rate of change in system plumbing adequacy |
| Stablecoin/BTC RoC (inv) | 15% | -(StableMcap/BTC) / (StableMcap/BTC)[21d] - 1 | DefiLlama (USDT+USDC), Yahoo (BTC-USD) | Capital rotation: stablecoin vs BTC flow dynamics |
| Reserve Ratio Level | 15% | TOTRESNS / WALCL | FRED: TOTRESNS, WALCL | Banking system liquidity buffer health |

### Z-Score Methodology

- Expanding window z-scores (minimum 63 periods)
- Winsorization at ±3.0 to cap outliers
- Tested against rolling 2yr and 3yr alternatives; expanding + winsorize was selected as best method
- `CLI = Σ (weight_i × z_score_i)` for all 4 components

### Data Sources

| Source | Series | Access |
|---|---|---|
| FRED | DTWEXBGS (Trade-Weighted Dollar), TOTRESNS (Total Reserves), WALCL (Fed Balance Sheet) | Free API |
| DefiLlama | Stablecoin API (sid=1 USDT, sid=2 USDC) | Free |
| Yahoo Finance | BTC-USD daily close | Free |

### Pipeline

- All data pulled into `Lighthouse_Master.db` (SQLite)
- CLI computation: `cli_final.py` → exports `cli_chart_data.csv`
- Chart generation: `cli_chart.py` (reads CSV, produces branded charts in both themes)

---

## BACKTEST RESULTS

### Sample: 2018-2025 (~2,850-2,900 daily observations)

### Quintile Sort: CLI Quintile → Forward BTC Returns

| Horizon | Q1 (Weakest) | Q2 | Q3 | Q4 | Q5 (Strongest) | Q5-Q1 Spread | t-stat | p-value |
|---|---|---|---|---|---|---|---|---|
| 21D | -4.8% | +0.5% | +1.0% | +2.0% | +8.6% | **+13.4%** | 14.2 | <0.0001 |
| 42D | -7.8% | -0.2% | +3.9% | +6.0% | +14.3% | **+22.1%** | 15.6 | <0.0001 |
| 63D | -9.8% | -2.1% | +9.0% | +11.1% | +17.2% | **+27.0%** | 15.0 | <0.0001 |

- **Monotonic at all horizons.** Every step up in CLI corresponds to higher forward returns.
- All p < 0.0001.

### Slugging Percentage (Win Size Ratio: Q1 vs Q5)

| Horizon | Q1 Slugging | Q5 Slugging |
|---|---|---|
| 21D | 0.45x | 4.81x |
| 42D | 0.43x | 4.50x |
| 63D | 0.39x | 3.70x |

In expanding environments, wins are nearly 4x the size of losses. In contracting environments, losses dominate by more than 2:1.

### Tercile Regime Stats (63D Forward)

| CLI Regime | Avg 63D Return | Win Rate | Slugging |
|---|---|---|---|
| Contracting | -8.5% | 33% | 0.43x |
| Neutral | +6.9% | 55% | 2.06x |
| Expanding | +16.8% | 73% | 3.92x |

---

## CONCEPTUAL ARCHITECTURE (Full Vision)

The tested model above is the core. The broader conceptual framework describes the full 3-tier, 8-component architecture that CLI could evolve into. This is what's described in public-facing materials (Pascal's report, master context docs).

### Three Tiers (Conceptual)

**Tier 1: Macro Liquidity Tide (conceptual 40%, 11-13 week lead)**
- Global M2 Momentum (YoY %)
- DXY 63-Day Rate of Change ← *implemented as DollarYoY*

**Tier 2: US Plumbing Mechanics (conceptual 35%, 1-6 week lead)**
- Fed Balance Sheet (WALCL) weekly change ← *implemented via ResRatio and ResRatio_RoC*
- TGA drawdown/buildup rate ← *not yet implemented*
- RRP facility balance ← *not yet implemented (near zero, structurally compromised)*
- SOFR-IORB spread ← *not yet implemented*
- HY OAS (inverted) ← *not yet implemented*

**Tier 3: Crypto-Native Transmission (conceptual 25%, 0-2 week lead)**
- Stablecoin supply momentum ← *implemented as StableBTC_RoC*
- BTC ETF net flows (20d) ← *not yet implemented*
- Exchange stablecoin reserves ← *not yet implemented*

**Leverage Regime Filter:** Perpetual futures funding rates as multiplicative overlay ← *not yet implemented*

### What's Built vs What's Conceptual

| Status | Components |
|---|---|
| **Built & tested** | DollarYoY, ResRatio_RoC, StableBTC_RoC, ResRatio |
| **Conceptual (not implemented)** | Global M2, TGA, RRP, SOFR-IORB, HY OAS, ETF flows, exchange reserves, leverage filter |

The 4-component model already captures the core signal. The conceptual components would add granularity but the backtest proves the current construction works. Future iterations may add components if they improve out-of-sample performance.

---

## DIFFERENTIATION

| vs Who | CLI Advantage |
|---|---|
| **Michael Howell (CrossBorder Capital)** | Howell's GLI is institutional-grade but doesn't include crypto-native transmission channels. CLI captures both macro liquidity AND how it actually reaches crypto markets. |
| **Lyn Alden** | Broader measurement (wholesale via reserves ratio, not just M2) plus crypto-native integration. |
| **Arthur Hayes** | Systematic construction with statistical grounding rather than narrative-driven tactical calls. |
| **Standard Net Liquidity (BS - TGA - RRP)** | CLI uses rate of change (not levels), includes crypto-native channels, captures reserve adequacy (not just reserves), and isn't broken by RRP depletion. |

---

## DISCLOSURE STRATEGY

| Public (OK to share) | Proprietary (do not publish) |
|---|---|
| Three-tier conceptual architecture | Exact 4-component weights |
| Component names (conceptual) | Specific series IDs and transformations |
| Empirical results (quintile tables, t-stats, regime stats) | Z-score methodology details |
| Tiered lag structure | Winsorization parameters |
| Regime filter concept | Which components are actually implemented vs conceptual |

---

## KEY FILES

| File | Location | Purpose |
|---|---|---|
| `cli_final.py` | `/Users/bob/LHM/Scripts/backtest/` | **Production model.** Weights, z-scores, robustness tests, chart data export. |
| `cli_chart_data.csv` | `/Users/bob/LHM/Scripts/backtest/` | Exported composite + BTC returns for charting. |
| `cli_chart.py` | `/Users/bob/LHM/Scripts/chart_generation/` | Branded chart generation (dual theme). |
| `cli_backtest.py` | `/Users/bob/LHM/Scripts/backtest/` | Original backtest (v1). |
| `cli_backtest_v2.py` - `v5.py` | `/Users/bob/LHM/Scripts/backtest/` | Development iterations. v4 found winning structure, v5 forced stablecoin inclusion + presentation outputs. |
| `cli_oos_90_10.py` | `/Users/bob/LHM/Scripts/backtest/` | Out-of-sample 90/10 split test. |
| `cli_oos_test.py` | `/Users/bob/LHM/Scripts/backtest/` | Additional OOS validation. |
| `cli_asymmetry.py` | `/Users/bob/LHM/Scripts/backtest/` | Asymmetry / slugging analysis. |
| `PASCAL_CONTRIBUTION_DRAFT.md` | `/Users/bob/Desktop/BTC_ETF_Article/` | Pascal report draft (CLI + Technical Structure + debunks). NOT YET SUBMITTED. |

---

## CURRENT READING

As of Feb 13, 2026: **+0.05 to +0.07 (Q3, Neutral)**

No strong directional signal. Dollar headwind and plumbing dynamics roughly offsetting.

---

## INVALIDATION

The CLI framework breaks if:
- The correlation between dollar direction and BTC reverses persistently (it has before: pre-2020, Fed tightening *increased* BTC prices)
- Stablecoin market structure changes fundamentally (e.g., regulatory crackdown eliminates the on-ramp channel)
- Reserve dynamics decouple from risk asset transmission (structural regime shift in Fed operations)
- Bitcoin's correlation to macro liquidity collapses as it transitions to a different asset class identity

---

*Last updated: February 22, 2026*
*Lighthouse Macro | lighthousemacro.com | @LHMacro*
