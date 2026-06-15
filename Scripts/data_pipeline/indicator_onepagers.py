#!/usr/bin/env python3
"""
INDICATOR ONE-PAGERS — full reference profile for every live indicator.

Merges authored metadata (category, what-it-measures, formula, confidence tier)
with live DB readings (current value/status, history depth) and the status-band
thresholds, and emits a markdown reference — one tight profile ("one pager") per
indicator, grouped by the 5 categories.

Run: PYTHONPATH=/Users/bob/LHM /opt/homebrew/bin/python3 \
       Scripts/data_pipeline/indicator_onepagers.py
Output: Outputs/INDICATOR_ONE_PAGERS.md
"""
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, "/Users/bob/LHM/Scripts/data_pipeline")
from compute_indices import STATUS_THRESHOLDS, ALLOCATION_BASKETS  # noqa: E402
from descriptive_indicators import INDICATORS as DESC  # noqa: E402

DB = "/Users/bob/LHM/Data/databases/Lighthouse_Master.db"
OUT = Path("/Users/bob/LHM/Outputs/INDICATOR_ONE_PAGERS.md")

# code_id -> profile. cat: 1 Allocation / 2 Macro-impact / 3 Descriptive /
# 4 Macro-regime / 5 Market-regime. f=formula, m=measures, tier, tx=transform.
META = {
  # --- Cat 1: Allocation impact (9 ALLOC_*) — formula pulled from ALLOCATION_BASKETS ---
  "ALLOC_CURVE_STEEPENER": dict(cat=1, name="Labor-Led Curve Steepener", tier="VALIDATED (OOS +0.27, n=80)",
    m="Labor fragility leads the Fed ~6-9mo; when it rises the front end falls faster than the long end → 2s10s bull-steepens.", tgt="2s10s (T10Y2Y), 6m"),
  "ALLOC_CYCLICAL_DEFENSIVE": dict(cat=1, name="Cyclical-Defensive Rotation", tier="VALIDATED (OOS +0.30, n=97)",
    m="Real-economy breadth (employment/IP/surveys) migrating defensive leads the cyclical-vs-defensive equity rotation.", tgt="XLI/XLP, 3m"),
  "ALLOC_ENERGY_MOMENTUM": dict(cat=1, name="Energy CPI Pass-Through", tier="VALIDATED (OOS +0.21, n=97)",
    m="Oil + energy-inflation momentum leads the energy sector vs the broad market.", tgt="XLE/SPY, 3m"),
  "ALLOC_CONS_ROTATION": dict(cat=1, name="Consumer Goods-Services Rotation", tier="VALIDATED (OOS +0.12, n=97)",
    m="Labor-income + durables-minus-services impulse leads discretionary vs staples.", tgt="XLY/XLP, 3m"),
  "ALLOC_REALYIELD_GOLD": dict(cat=1, name="Real-Yield Gold Engine", tier="PROVISIONAL (OOS +0.15, n=38)",
    m="Gold is mechanically inverse to the 10y real yield (DFII10 / DGS10−T10YIE).", tgt="GLD, 6m"),
  "ALLOC_CREDIT_LABOR_GAP": dict(cat=1, name="Credit-Labor Gap (allocation)", tier="PROVISIONAL (OOS +0.11, n=39)",
    m="Labor stress precedes credit stress (income → delinquency); spreads correct toward labor reality.", tgt="HY OAS, 6m"),
  "ALLOC_DOLLAR_EM": dict(cat=1, name="Strong-Dollar EM Stress", tier="PROVISIONAL (OOS −0.15, n=41)",
    m="A strong broad dollar tightens global financial conditions → EM equity underperformance.", tgt="EEM, 6m"),
  "ALLOC_INCOME_DEPLETION": dict(cat=1, name="Income Fuel-Tank Depletion", tier="PROVISIONAL (OOS −0.18, n=48)",
    m="Falling saving rate + real-income drain leads discretionary underperformance.", tgt="XLY/XLP, 6m"),
  "ALLOC_INVENTORY_DESTOCK": dict(cat=1, name="Inventory Destocking", tier="PROVISIONAL (OOS +0.20, n=48)",
    m="Inventory overhang forces destocking that leads materials underperformance.", tgt="XLB/SPY, 6m"),
  # --- Cat 2: Macro impact ---
  "PCI": dict(cat=2, name="Inflation Heat (PCI)", tier="VALIDATED (OOS +0.36)",
    f="z-composite of core PCE/CPI, sticky/supercore, breakevens, PPI; weighted.", m="Inflation pressure; leads forward core PCE ~6mo.", tgt="forward core PCE"),
  "GCI": dict(cat=2, name="Activity Pulse (GCI)", tier="VALIDATED (OOS +0.25)",
    f="z-composite of INDPRO, PAYEMS, RSXFS, TCU, CFNAI, BBKI, RPI, real PCE, hours.", m="Real growth momentum; leads forward payrolls ~6mo.", tgt="forward payrolls"),
  "FPI": dict(cat=2, name="Fiscal Pressure (FPI)", tier="VALIDATED (OOS +0.29; descriptive +0.87)",
    f="0.50·z(Debt/GDP) + 0.50·z(10y term premium).", m="Fiscal/term-premium stress; leads the 10y yield.", tgt="DGS10 / term premium"),
  "LPI": dict(cat=2, name="Labor Pressure (LPI)", tier="VALIDATED (OOS +0.25, n=66)",
    f="z-composite of long-term-unemployed, quits/hires, claims, temp help, wages.", m="Labor-market tightness/pressure; leads forward payrolls.", tgt="forward payrolls"),
  "BCI": dict(cat=2, name="Capex Thrust (BCI)", tier="PROVISIONAL (OOS +0.17; descriptive +0.70)",
    f="z(C&I loans YoY), z(business loans YoY), −z(HY OAS).", m="Business investment impulse; leads industrial production.", tgt="forward INDPRO"),
  "CLG": dict(cat=2, name="Credit-Labor Gap (CLG)", tier="VALIDATED",
    f="z(HY OAS) − z(LFI).", m="Credit spreads vs labor reality; when negative spreads ignore labor stress → widen.", tgt="HY OAS"),
  "PIPELINE_IMPULSE": dict(cat=2, name="Pipeline Impulse", tier="descriptive",
    m="Producer prices running ahead of consumer prices — inflation building/fading in the pipeline 3-6mo.", tgt="CPI (upstream lead)"),
  "INTEREST_CROWDOUT": dict(cat=2, name="Interest Crowd-Out", tier="descriptive",
    m="Federal interest expense outrunning the economy — the budget/fiscal squeeze.", tgt="fiscal drag"),
  # --- Cat 3: Descriptive ---
  "HCI": dict(cat=3, name="Housing Tide (HCI)", tier="VALIDATED descriptive (+0.87, real lift)",
    f="coverage-weighted z of starts, existing-sales, months-supply(inv), Case-Shiller, mortgage(inv).", m="Overall housing-market health."),
  "AFFORD_PRESSURE": dict(cat=3, name="Affordability Pressure (true cost of homeownership)", tier="descriptive",
    m="How stretched the monthly mortgage payment on a median home is (rate × price vs wage) — the binding constraint on marginal demand."),
  "SUPERCORE_HEAT": dict(cat=3, name="Supercore Heat", tier="descriptive",
    m="Core services inflation ex-shelter (the Fed's 'supercore') — wage-driven domestic price persistence."),
  "PERSISTENCE_GAP": dict(cat=3, name="Persistence Gap", tier="descriptive",
    m="Sticky-minus-flexible CPI — how much inflation is structural vs transitory."),
  "TREND_HEAT": dict(cat=3, name="Underlying Trend Heat", tier="descriptive",
    m="Trimmed-mean/median inflation — the noise-cleaned underlying trend."),
  "FROZEN_DIVERGENCE": dict(cat=3, name="Frozen Market Divergence", tier="descriptive",
    m="Rate-frozen housing: prices firm while transaction volume collapses (lock-in)."),
  "CAPACITY_SLACK": dict(cat=3, name="Capacity Slack", tier="descriptive",
    m="Spare industrial/manufacturing capacity — the cleanest disinflationary-pressure read."),
  "CCI": dict(cat=3, name="Consumer Pulse (CCI)", tier="DESCRIPTOR (proxy — use RSXFS)",
    f="z(sentiment), z(saving rate), −z(credit-card delinquency).", m="Consumer health (composite weak vs RSXFS proxy)."),
  "TCI": dict(cat=3, name="Global Risk Tide (TCI)", tier="DESCRIPTOR",
    f="−z(dollar YoY), z(EUR/USD YoY).", m="Trade / dollar conditions; rotation engine."),
  "LCI": dict(cat=3, name="Liquidity Cushion (LCI)", tier="DESCRIPTOR",
    f="z-composite of reserves, IORB/EFFR funding, money-market spreads.", m="System liquidity conditions / buffer."),
  "LFI": dict(cat=3, name="Labor Fragility (LFI)", tier="DESCRIPTOR",
    f="z-composite of LT-unemployed, quits/hires ratio, claims, temp help, wages, U-6.", m="Underlying labor-market stress (leads the headline)."),
  "LDI": dict(cat=3, name="Labor Dynamism (LDI)", tier="DESCRIPTOR",
    f="z(quits), z(hires), −z(claims).", m="Labor-market turnover / dynamism."),
  # --- Cat 4: Macro regime ---
  "MRI": dict(cat=4, name="Macro Risk Index (MRI) — MASTER", tier="REGIME (structural; weights v2.0)",
    f="standardized weighted sum of the 10 pillar composites (LPI/PCI/GCI/HCI/CCI/BCI/TCI/FPI/FCI/LCI).", m="Single aggregate macro-risk gauge; drives the equity-allocation table + sizing multiplier."),
  "REC_PROB": dict(cat=4, name="Recession Probability", tier="REGIME (3-mo smoothed)",
    m="Model probability of recession 3/6/12mo forward."),
  "ENSEMBLE_RISK": dict(cat=4, name="Risk Ensemble", tier="REGIME",
    m="Ensemble-adjusted crisis probability (incorporates dispersion + regime stability)."),
  "BASE_REC_PROB": dict(cat=4, name="Base Recession Probability", tier="REGIME",
    m="Pre-ensemble base recession probability (for comparison)."),
  "WARNING_LEVEL": dict(cat=4, name="Threshold Warning System", tier="REGIME",
    m="Aggregate threshold-breach warning level (1 GREEN → 4 RED)."),
  "ALLOC_MULTIPLIER": dict(cat=4, name="Allocation Multiplier", tier="REGIME",
    m="Position-sizing dial (0–1.2×) derived from the risk ensemble."),
  "DISCONTINUITY_PREMIUM": dict(cat=4, name="Discontinuity Premium", tier="REGIME",
    m="Extra crisis probability from non-linear / tail dynamics the base model misses."),
  "LIQ_STAGE": dict(cat=4, name="Liquidity Stage", tier="REGIME",
    m="Discrete liquidity-regime stage (1 → 7) across the plumbing cascade."),
  # --- Cat 5: Market regime ---
  "MSI": dict(cat=5, name="Market Breadth Pulse (MSI)", tier="DESCRIPTOR",
    f="z-composite of SPX vs 200d/50d, slopes, %>MA, AD line, McClellan.", m="Equity market structure / trend health."),
  "SPI": dict(cat=5, name="Sentiment Tide (SPI)", tier="DESCRIPTOR",
    f="z-composite of VIX, AAII bull-bear, VIX-vs-50d, VIX backwardation.", m="Positioning / sentiment (contrarian at extremes)."),
  "SBD": dict(cat=5, name="Structure-Breadth Divergence (SBD)", tier="DESCRIPTOR",
    m="Price vs breadth gap — distribution (>0) vs accumulation (<0)."),
  "SSD": dict(cat=5, name="Sentiment-Structure Divergence (SSD)", tier="DESCRIPTOR",
    m="Sentiment vs structure gap — capitulation vs blow-off risk."),
  "VOL_TERM_GAP": dict(cat=5, name="Vol Term-Structure Gap", tier="descriptive",
    m="Spot VIX vs 3-month VIX — backwardation (stress) vs contango (calm)."),
  "QUALITY_PRESSURE": dict(cat=5, name="Quality Pressure", tier="descriptive",
    m="Within-investment-grade quality premium (BAA−AAA) — risk appetite inside credit."),
  "FCI_CHANNELS": dict(cat=5, name="FCI Channels", tier="descriptive",
    m="Financial-conditions decomposition (risk + credit + leverage sub-channels)."),
  "FCI": dict(cat=5, name="Credit Tide (FCI)", tier="DESCRIPTOR (provisional →VIX)",
    f="z-composite of HY OAS(inv), NFCI(inv), 10y-2y, VIX(inv), LCI.", m="Aggregate financial conditions."),
  "EMD": dict(cat=5, name="Equity Momentum Divergence (EMD)", tier="DESCRIPTOR",
    m="Price vs momentum divergence — overbought/oversold."),
  "BILL_SOFR": dict(cat=5, name="Bill-SOFR Spread", tier="DESCRIPTOR",
    m="3-month bill vs SOFR — front-end funding richness/cheapness."),
  "SVI": dict(cat=5, name="Spread-Volatility Imbalance (SVI)", tier="DESCRIPTOR",
    m="Credit spreads vs equity vol — complacency vs stress imbalance."),
  "YFS": dict(cat=5, name="Yield-Funding Stress (YFS)", tier="DESCRIPTOR",
    m="Yield vs funding-market stress composite."),
  "CRYPTO_DEFI_LIQUIDITY": dict(cat=5, name="Crypto DeFi Liquidity (CDLI)", tier="descriptive (free-data)",
    f="z of total DeFi TVL momentum (17 DefiLlama protocol series).", m="Crypto-as-liquidity-asset: DeFi TVL expanding/contracting."),
}

CAT_NAMES = {1: "ALLOCATION IMPACT", 2: "MACRO IMPACT", 3: "DESCRIPTIVE",
             4: "MACRO REGIME", 5: "MARKET REGIME"}


def basket_formula(code):
    """Pull formula string from the live registries where available."""
    if code in ALLOCATION_BASKETS:
        return " + ".join(f"{'−' if s < 0 else '+'}{t}({sid})"
                          for sid, s, t in ALLOCATION_BASKETS[code])
    if code in DESC:
        return " + ".join(f"{'−' if s < 0 else '+'}{tf}({sid})"
                          for sid, s, tf in DESC[code]["basket"])
    return None


def thresholds_str(code):
    th = STATUS_THRESHOLDS.get(code)
    if not th:
        return "z-bands ±0.5 / ±1.5 (signal / extreme)"
    parts = [f"≥{t}: {s}" for t, s in th if t > -900]
    parts.append(f"else {th[-1][1]}")
    return " · ".join(parts)


def main():
    conn = sqlite3.connect(DB)
    # Fast: two GROUP BY aggregations (use idx_indices_id), merge in Python.
    agg = {r[0]: r for r in conn.execute(
        "SELECT index_id, MIN(date), MAX(date), COUNT(*) FROM lighthouse_indices "
        "GROUP BY index_id").fetchall()}
    latest = {r[0]: (r[1], r[2]) for r in conn.execute(
        "SELECT li.index_id, li.value, li.status FROM lighthouse_indices li "
        "JOIN (SELECT index_id, MAX(date) d FROM lighthouse_indices GROUP BY index_id) m "
        "ON li.index_id=m.index_id AND li.date=m.d").fetchall()}
    conn.close()
    # rows[code] = (code, value, status, last_date, first_date, n)
    rows = {}
    for code, (cid, first, last, n) in agg.items():
        val, status = latest.get(code, (None, "—"))
        rows[code] = (code, val, status, last, first, n)

    out = ["# Lighthouse Macro — Indicator One-Pagers",
           f"\n*Full reference profile for all {len(META)} live indicators. "
           f"Generated {datetime.now():%Y-%m-%d %H:%M}. Live readings as of latest pipeline run.*\n",
           "Confidence tiers: **VALIDATED** (OOS-confirmed, trade off it) · **PROVISIONAL** "
           "(real, smaller-n) · **DESCRIPTOR** (honest state read, failed predictive OOS — not a "
           "forward signal) · **descriptive** (combined-metric read, honest by construction).\n",
           "---\n"]

    for cat in (1, 2, 3, 4, 5):
        out.append(f"\n# {cat}. {CAT_NAMES[cat]}\n")
        codes = [c for c, m in META.items() if m["cat"] == cat]
        for code in codes:
            m = META[code]
            r = rows.get(code)
            val = f"{r[1]:+.2f}" if r and r[1] is not None else "—"
            status = r[2] if r else "—"
            hist = f"{r[4][:10]} → {r[3][:10]} ({r[5]:,} obs)" if r else "—"
            f = m.get("f") or basket_formula(code) or "—"
            out += [
                f"## {m['name']}  `{code}`",
                f"- **Category:** {CAT_NAMES[cat].title()}" + (f" · **predicts:** {m['tgt']}" if m.get("tgt") else ""),
                f"- **Current:** **{val} — {status}**",
                f"- **Measures:** {m['m']}",
                f"- **Formula:** {f}",
                f"- **Status bands:** {thresholds_str(code)}",
                f"- **History:** {hist}",
                f"- **Confidence:** {m['tier']}",
                "",
            ]
    OUT.write_text("\n".join(out))
    print(f"Wrote {OUT}  ({len(META)} indicators)")


if __name__ == "__main__":
    main()
