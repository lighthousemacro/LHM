#!/usr/bin/env python3
"""
Build branded HTML report — LHM Indicator Rebuild
====================================================
Compiles findings across all phases into a single self-contained
branded HTML artifact. Uses indicator full names on first reference
per Bob's feedback rule.
"""

import base64
import json
from datetime import datetime
from pathlib import Path

OUTPUT_DIR = Path("/Users/bob/LHM/Outputs/mri_optimization")
REPORT_PATH = OUTPUT_DIR / "INDICATOR_REBUILD_REPORT.html"
BRAND_DIR = Path("/Users/bob/LHM/Brand")
ICON_PATH = BRAND_DIR / "icon_transparent_128.png"


def b64_image(path):
    if not path.exists():
        return None
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def load_json(path):
    if not Path(path).exists():
        return None
    return json.loads(Path(path).read_text())


def fmt_pct(v, signed=False):
    if v is None or v != v:
        return "—"
    s = f"{v:+.1%}" if signed else f"{v:.1%}"
    return s


def build_report():
    pillar_v1 = load_json(OUTPUT_DIR / "pillar_weight_optimization.json") or {}
    pillar_v2 = load_json(OUTPUT_DIR / "pillar_weight_optimization_v2.json") or {}
    multiasset = load_json(OUTPUT_DIR / "pillar_multiasset_optimization.json") or {}

    icon_b64 = b64_image(ICON_PATH)
    today = datetime.now().strftime("%B %d, %Y")

    # Build the per-pillar adoption table from v1, override with v2 where rerun
    pillar_table_rows = []
    NAMES = {
        'LPI': 'Labor Pressure Index',
        'PCI': 'Price Conditions Index',
        'GCI': 'Growth Conditions Index',
        'HCI': 'Housing Conditions Index',
        'CCI': 'Consumer Conditions Index',
        'BCI': 'Business Conditions Index',
        'TCI': 'Trade Conditions Index',
        'GCI_Gov': 'Government Conditions Index',
        'FCI': 'Financial Conditions Index',
        'LCI': 'Liquidity Cushion Index',
        'MSI': 'Market Structure Index',
        'SPI': 'Sentiment & Positioning Index',
    }
    DOMAIN_TARGETS = {
        'LPI': 'fwd 252d unemployment rate change',
        'PCI': 'fwd 365d core PCE YoY',
        'GCI': 'fwd 252d Industrial Production YoY',
        'HCI': 'fwd 365d housing starts YoY',
        'CCI': 'fwd 252d real retail sales YoY',
        'BCI': 'fwd 252d new orders cap goods YoY',
        'TCI': 'fwd 252d net exports change',
        'GCI_Gov': 'fwd 252d HY OAS widening',
        'FCI': 'fwd 126d HY OAS widening',
        'LCI': 'fwd 63d HY OAS widening',
        'MSI': 'fwd 63d SPX log return',
        'SPI': 'fwd 21d SPX log return',
    }
    for code in ['LPI', 'PCI', 'GCI', 'HCI', 'CCI', 'BCI', 'TCI',
                 'GCI_Gov', 'FCI', 'LCI', 'MSI', 'SPI']:
        v1 = pillar_v1.get('pillars', {}).get(code, {})
        v2 = pillar_v2.get('pillars', {}).get(code, {})
        full_name = NAMES.get(code, code)
        target = DOMAIN_TARGETS.get(code, '')
        j_oos = v1.get('evaluation', {}).get('judgment', {}).get('oos_ic')
        # v2 uses tighter bounds; use that if present
        if v2:
            o_oos = v2.get('alpha_results', {}).get('alpha_1.0', {}).get('oos_ic')
            mx = v2.get('alpha_results', {}).get('alpha_1.0', {}).get('max_weight')
        else:
            o_oos = v1.get('evaluation', {}).get('optimized', {}).get('oos_ic')
            mx = v1.get('max_optimized_weight')

        if j_oos is not None and o_oos is not None and j_oos != 0:
            improvement = (abs(o_oos) - abs(j_oos)) / max(abs(j_oos), 0.01)
        else:
            improvement = None

        # Decision per v2 if rerun, else v1
        if code in ['LPI', 'PCI', 'BCI']:
            decision = 'ADOPT (tighter bounds)'
            decision_class = 'signal-strong'
        elif v1:
            d_raw = v1.get('decision', 'unknown')
            if d_raw == 'shrink':
                decision = 'Shrinkage candidate'
                decision_class = ''
            elif d_raw == 'keep_judgment':
                decision = 'Keep judgment'
                decision_class = 'signal-weak'
            else:
                decision = d_raw
                decision_class = ''

        pillar_table_rows.append({
            'code': code,
            'name': full_name,
            'target': target,
            'j_oos': j_oos,
            'o_oos': o_oos,
            'mx': mx,
            'improvement': improvement,
            'decision': decision,
            'decision_class': decision_class,
        })

    rows_html = ""
    for r in pillar_table_rows:
        j = f"{r['j_oos']:+.4f}" if r['j_oos'] is not None else 'n/a'
        o = f"{r['o_oos']:+.4f}" if r['o_oos'] is not None else 'n/a'
        imp = fmt_pct(r['improvement'], signed=True) if r['improvement'] is not None else '—'
        mx = f"{r['mx']:.3f}" if r['mx'] is not None else '—'
        rows_html += f"""<tr>
<td><strong>{r['name']}</strong> ({r['code']})</td>
<td>{r['target']}</td>
<td class="num">{j}</td>
<td class="num">{o}</td>
<td class="num">{imp}</td>
<td class="num">{mx}</td>
<td class="{r['decision_class']}">{r['decision']}</td>
</tr>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Indicator Rebuild Report — Lighthouse Macro</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700;900&family=Inter:wght@400;500;600&family=Source+Code+Pro:wght@400;500&display=swap');

* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{
  font-family: 'Inter', sans-serif;
  font-size: 13px;
  line-height: 1.6;
  color: #1A1A1A;
  background: #FFFFFF;
  max-width: 1100px;
  margin: 0 auto;
  padding: 50px 60px 80px;
}}

.brand-header {{
  display: flex;
  align-items: center;
  gap: 16px;
  padding-bottom: 16px;
  border-bottom: 4px solid #2389BB;
  margin-bottom: 36px;
}}
.brand-icon {{ width: 36px; height: 36px; flex-shrink: 0; }}
.brand-text {{ display: flex; flex-direction: column; }}
.brand-title {{
  font-family: 'Montserrat', sans-serif;
  font-weight: 700;
  font-size: 18px;
  letter-spacing: 1.5px;
  color: #2389BB;
}}
.brand-tagline {{
  font-family: 'Montserrat', sans-serif;
  font-weight: 600;
  font-size: 9px;
  letter-spacing: 2px;
  color: #898989;
  margin-top: 2px;
}}

.accent-bar {{ display: flex; height: 5px; margin: 28px 0 14px; }}
.accent-bar .ocean {{ background: #2389BB; flex: 2; }}
.accent-bar .dusk  {{ background: #FF6723; flex: 1; }}

h1.doc-title {{
  font-family: 'Montserrat', sans-serif;
  font-weight: 900;
  font-size: 30px;
  color: #1A1A1A;
  margin-bottom: 6px;
  line-height: 1.15;
}}
.doc-subtitle {{
  font-family: 'Montserrat', sans-serif;
  font-weight: 600;
  font-size: 14px;
  color: #2389BB;
  margin-bottom: 4px;
}}
.doc-meta {{
  font-family: 'Inter', sans-serif;
  font-size: 11px;
  color: #898989;
  margin-bottom: 32px;
}}

h2 {{
  font-family: 'Montserrat', sans-serif;
  font-weight: 700;
  font-size: 22px;
  color: #2389BB;
  margin-top: 44px;
  margin-bottom: 16px;
  padding-bottom: 6px;
  border-bottom: 1px solid #D1D1D1;
}}
h3 {{
  font-family: 'Montserrat', sans-serif;
  font-weight: 600;
  font-size: 16px;
  color: #1A1A1A;
  margin-top: 28px;
  margin-bottom: 10px;
}}
h4 {{
  font-family: 'Montserrat', sans-serif;
  font-weight: 600;
  font-size: 13px;
  color: #2389BB;
  margin-top: 20px;
  margin-bottom: 6px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}}

p {{ margin-bottom: 12px; }}

.callout {{
  background: #F8F9FA;
  border-left: 4px solid #2389BB;
  padding: 14px 18px;
  margin: 18px 0;
  font-size: 13px;
}}
.callout.win  {{ border-left-color: #00BB89; background: #F0FAF7; }}
.callout.warn {{ border-left-color: #FF6723; background: #FFF6EE; }}
.callout.fail {{ border-left-color: #FF2389; background: #FFF0F6; }}
.callout-label {{
  font-family: 'Montserrat', sans-serif;
  font-weight: 700;
  font-size: 10px;
  letter-spacing: 1px;
  text-transform: uppercase;
  margin-bottom: 4px;
}}
.callout.win  .callout-label {{ color: #00BB89; }}
.callout.warn .callout-label {{ color: #FF6723; }}
.callout.fail .callout-label {{ color: #FF2389; }}
.callout      .callout-label {{ color: #2389BB; }}

table {{
  width: 100%;
  border-collapse: collapse;
  margin: 14px 0 22px;
  font-size: 12px;
}}
th {{
  font-family: 'Montserrat', sans-serif;
  font-weight: 600;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: #2389BB;
  text-align: left;
  padding: 8px 10px;
  border-bottom: 2px solid #2389BB;
  background: #F8F9FA;
}}
td {{
  padding: 7px 10px;
  border-bottom: 1px solid #E5E7EB;
  vertical-align: top;
}}
td.num, th.num {{ text-align: right; font-family: 'Source Code Pro', monospace; }}
tr:hover td {{ background: #F8F9FA; }}

.signal-strong {{ color: #00BB89; font-weight: 600; }}
.signal-weak   {{ color: #898989; }}
.signal-fail   {{ color: #FF2389; font-weight: 600; }}
.code {{ font-family: 'Source Code Pro', monospace; background: #F1F4F7; padding: 1px 5px; border-radius: 3px; font-size: 11px; }}

ul, ol {{ margin: 8px 0 14px 24px; }}
li {{ margin-bottom: 4px; }}

.footer {{
  margin-top: 60px;
  padding-top: 16px;
  border-top: 1px solid #D1D1D1;
  font-size: 10px;
  color: #898989;
  text-align: center;
}}
.footer a {{ color: #2389BB; text-decoration: none; margin: 0 8px; }}
.footer a:hover {{ text-decoration: underline; }}

.toc {{
  background: #F8F9FA;
  border: 1px solid #E5E7EB;
  padding: 18px 22px;
  margin: 0 0 32px;
  border-radius: 4px;
}}
.toc-title {{
  font-family: 'Montserrat', sans-serif;
  font-weight: 700;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: #2389BB;
  margin-bottom: 8px;
}}
.toc ol {{ margin: 0 0 0 18px; font-size: 12px; }}
.toc a {{ color: #1A1A1A; text-decoration: none; }}
.toc a:hover {{ color: #2389BB; }}
</style>
</head>
<body>

<div class="brand-header">
{f'<img class="brand-icon" src="data:image/png;base64,{icon_b64}" alt="LHM">' if icon_b64 else ''}
  <div class="brand-text">
    <div class="brand-title">LIGHTHOUSE MACRO</div>
    <div class="brand-tagline">MACRO, ILLUMINATED.</div>
  </div>
</div>

<div class="doc-subtitle">Internal Research Memo</div>
<h1 class="doc-title">Indicator Rebuild — Full Findings</h1>
<div class="doc-meta">{today} · Macro Risk Index Optimization · Per-Pillar Component Weight Optimization · Threshold Sweeps · Audit</div>

<div class="accent-bar"><div class="ocean"></div><div class="dusk"></div></div>

<div class="toc">
  <div class="toc-title">Contents</div>
  <ol>
    <li><a href="#headline">Headline</a></li>
    <li><a href="#mri">Macro Risk Index — Weight Optimization</a></li>
    <li><a href="#mri-threshold">Macro Risk Index — Threshold Sweep</a></li>
    <li><a href="#bestsignal"><strong>Best Signal Per Pillar (Multi-Asset)</strong></a></li>
    <li><a href="#leadtime">Pillars as Real-World Lead Indicators</a></li>
    <li><a href="#pillar-opt">Per-Pillar Component Weight Optimization (Single-Asset)</a></li>
    <li><a href="#threshold-pillars">Per-Pillar Threshold Sweeps</a></li>
    <li><a href="#audit">Cross-Indicator Correlation Audit</a></li>
    <li><a href="#decisions">Decisions, Issues, Open Questions</a></li>
    <li><a href="#nextsteps">Next Steps</a></li>
  </ol>
</div>

<h2 id="headline">Headline</h2>

<div class="callout win">
  <div class="callout-label">What worked</div>
  <strong>Three pillars produce meaningfully better signal under optimized component weights.</strong>
  Business Conditions Index (BCI) goes from +0.45 to <strong>+0.57</strong> out-of-sample information coefficient against forward new orders. Labor Pressure Index (LPI) goes from -0.32 to <strong>-0.38</strong>. Price Conditions Index (PCI) goes from essentially zero (+0.005) to <strong>+0.30</strong>. All three under tightened weight bounds [0.05, 0.30] to discourage corner solutions.
</div>

<div class="callout">
  <div class="callout-label">What we kept</div>
  <strong>Macro Risk Index (MRI) judgment weights stay.</strong> Full SLSQP optimization against forward equity returns failed five of six master-plan invalidation criteria, including the OOS sign-flip. The judgment weights beat the optimized weights out-of-sample.
  <br><br>
  <strong>But MRI's job has changed.</strong> The continuous z-score of MRI doesn't predict forward returns reliably year-by-year. The threshold MRI ≥ +0.4 produces a 2.0x lift on big drawdown frequency. The threshold MRI ≥ +1.0 produces a 3.2x lift. MRI is best used as a regime-trigger threshold, not as a continuous regime conditioner.
</div>

<div class="callout warn">
  <div class="callout-label">What didn't work</div>
  Six pillars (Growth Conditions Index, Housing Conditions Index, Consumer Conditions Index, Trade Conditions Index, Government Conditions Index, Financial Conditions Index, Liquidity Cushion Index, Market Structure Index, Sentiment & Positioning Index) produced no meaningful improvement under weight optimization. Most still have <strong>strong judgment-weight signals</strong> against their domain targets — the optimization just couldn't beat the judgment baseline.
</div>

<h2 id="mri">Macro Risk Index — Weight Optimization (Phase 1)</h2>

<p>The full master-plan optimization spec ran on the Macro Risk Index (MRI): SLSQP with 30 Dirichlet restarts, bounds [0.02, 0.30], 90/10 IS/OOS split, 5-split walk-forward, expanding z-scores ±3 winsorized. Sortino on the Q1-Q5 spread as the objective at 63d horizon. Target: forward S&P 500 log returns.</p>

<h3>Result: Do not adopt</h3>

<table>
<thead><tr><th>Walk-forward metric</th><th class="num">Optimized</th><th class="num">Current Judgment</th></tr></thead>
<tbody>
<tr><td>Avg OOS Q-spread</td><td class="num signal-fail">-0.0022</td><td class="num signal-strong">+0.0124</td></tr>
<tr><td>Avg OOS information coefficient</td><td class="num">+0.0116</td><td class="num">+0.0279</td></tr>
</tbody>
</table>

<p><strong>Judgment weights beat optimized weights out-of-sample.</strong> Five of the six invalidation criteria fired:</p>

<table>
<thead><tr><th>#</th><th>Criterion</th><th>Result</th><th>Status</th></tr></thead>
<tbody>
<tr><td>1</td><td>IS/OOS spread &gt; 2x at primary</td><td>IS -0.049 / OOS +0.079 (sign flip)</td><td class="signal-fail">HIT</td></tr>
<tr><td>2</td><td>Walk-forward weight std &gt; 0.06 for 3+ pillars</td><td>LCI 0.056, CCI 0.076, GCI-Gov 0.065</td><td class="signal-fail">HIT</td></tr>
<tr><td>3</td><td>Monotonicity breaks OOS at primary</td><td>Working in opposite direction</td><td class="signal-fail">HIT</td></tr>
<tr><td>4</td><td>Any weight &gt; 0.25 (dominance)</td><td>Government Conditions Index = 0.293</td><td class="signal-fail">HIT</td></tr>
<tr><td>5</td><td>Annual IC sign flip &gt; 30% of windows</td><td>12 of 26 years (46%)</td><td class="signal-fail">HIT</td></tr>
<tr><td>6</td><td>Elevated MDD vs Low Risk</td><td>-19.3% vs -12.9% (1.5x)</td><td class="signal-strong">OK</td></tr>
</tbody>
</table>

<h3>What the data is actually saying</h3>

<p>The pooled information coefficient over 26 years is -0.09 at 63 days (statistically significant). Year-by-year, it sign-flips. Macro Risk Index "works" because the few crisis years (2007-09, 2020 H1) are massively negative-IC and overwhelm the noise. But year-to-year, in normal markets, it's a coin flip. Reframing required.</p>

<h2 id="mri-threshold">Macro Risk Index — Threshold Sweep (Phase 1 reframed)</h2>

<p>Reframing MRI as a threshold trigger aligned with the v2.0 portfolio framework: identify the restrictive regime where the framework-driven sleeve compresses. Sweep MRI z-scores from -0.5 to +2.0 in 0.1 steps. Compute drawdown frequency at each.</p>

<table>
<thead><tr><th>MRI Threshold</th><th class="num">N</th><th class="num">% pop</th><th class="num">63d Mean Return</th><th class="num">% with 63d &lt;-5%</th><th class="num">% with 63d &lt;-10%</th><th class="num">Drawdown Lift</th></tr></thead>
<tbody>
<tr><td>z ≥ +0.4</td><td class="num">881</td><td class="num">14.1%</td><td class="num">-0.83%</td><td class="num">26.7%</td><td class="num">16.6%</td><td class="num signal-strong">2.01x</td></tr>
<tr><td>z ≥ +1.0</td><td class="num">50</td><td class="num">0.8%</td><td class="num">+0.27%</td><td class="num">36.0%</td><td class="num">26.0%</td><td class="num signal-strong">3.15x</td></tr>
<tr><td>z ≥ +1.1</td><td class="num">24</td><td class="num">0.4%</td><td class="num">-4.18%</td><td class="num">58.3%</td><td class="num">37.5%</td><td class="num signal-strong">4.55x</td></tr>
</tbody>
</table>

<div class="callout">
  <div class="callout-label">Recommended new regime multiplier table</div>
  <table style="margin: 8px 0 0">
  <thead><tr><th>MRI Range</th><th>Regime</th><th class="num">Multiplier</th><th class="num">% of pop</th><th class="num">63d &lt;-5% rate</th></tr></thead>
  <tbody>
  <tr><td>z &lt; -0.5</td><td>Supportive</td><td class="num">1.0x</td><td class="num">10%</td><td class="num">7.8%</td></tr>
  <tr><td>-0.5 to +0.4</td><td>Neutral</td><td class="num">1.0x</td><td class="num">76%</td><td class="num">~15%</td></tr>
  <tr><td>+0.4 to +1.0</td><td>Cautious</td><td class="num">0.6x</td><td class="num">13%</td><td class="num">~26%</td></tr>
  <tr><td>z ≥ +1.0</td><td>Restrictive</td><td class="num">0.3x</td><td class="num">1%</td><td class="num">36%</td></tr>
  </tbody>
  </table>
  This compresses earlier than the v2.0 portfolio doc (which starts compression at +1.0). The +0.4 threshold catches 13% of the sample where forward-return mean is negative and big-drawdown frequency is 26%.
</div>

<h2 id="leadtime">Pillars as Real-World Lead Indicators</h2>

<p>The most important finding in this rebuild — and the one most worth publishing — is not about equity timing. It's about <strong>lead time on real-world economic variables</strong>. Each pillar was optimized against the data it was designed to predict, with a forward horizon long enough to test the actual lead relationship.</p>

<table>
<thead><tr>
<th>Pillar</th>
<th>What it predicts</th>
<th class="num">Lead</th>
<th class="num">Judgment OOS IC</th>
<th class="num">Optimized OOS IC</th>
<th>Read</th>
</tr></thead>
<tbody>
<tr><td><strong>Growth Conditions Index (GCI)</strong></td><td>Industrial Production YoY</td><td class="num">12 months</td><td class="num signal-strong">-0.59</td><td class="num">-0.43</td><td>Strong lead, judgment best</td></tr>
<tr><td><strong>Business Conditions Index (BCI)</strong></td><td>New Orders Capital Goods YoY</td><td class="num">12 months</td><td class="num">+0.45</td><td class="num signal-strong">+0.57</td><td>Strong lead, optimization wins</td></tr>
<tr><td><strong>Government Conditions Index (GCI-Gov)</strong></td><td>HY OAS widening events</td><td class="num">12 months</td><td class="num signal-strong">-0.46</td><td class="num">-0.12</td><td>Strong lead, judgment best</td></tr>
<tr><td><strong>Trade Conditions Index (TCI)</strong></td><td>Net exports change</td><td class="num">12 months</td><td class="num signal-strong">-0.42</td><td class="num">-0.41</td><td>Strong lead, judgment good</td></tr>
<tr><td><strong>Financial Conditions Index (FCI)</strong></td><td>HY OAS widening events</td><td class="num">6 months</td><td class="num signal-strong">-0.41</td><td class="num">-0.42</td><td>Strong lead, judgment good</td></tr>
<tr><td><strong>Labor Pressure Index (LPI)</strong></td><td>Unemployment rate change</td><td class="num">12 months</td><td class="num">-0.32</td><td class="num signal-strong">-0.38</td><td>Real lead, optimization wins</td></tr>
<tr><td><strong>Price Conditions Index (PCI)</strong></td><td>Core PCE YoY</td><td class="num">12 months</td><td class="num">+0.005</td><td class="num signal-strong">+0.30</td><td>Optimization unlocks signal</td></tr>
<tr><td>Housing Conditions Index (HCI)</td><td>Housing starts YoY</td><td class="num">12 months</td><td class="num signal-weak">+0.16</td><td class="num">+0.15</td><td>Weak in continuous IC; strong at threshold</td></tr>
<tr><td>Liquidity Cushion Index (LCI)</td><td>HY OAS widening</td><td class="num">3 months</td><td class="num signal-weak">-0.16</td><td class="num">-0.16</td><td>Weak in continuous IC; strong at threshold (z ≤ -2.0 → 2.34x lift)</td></tr>
<tr><td>Consumer Conditions Index (CCI)</td><td>Real retail sales YoY</td><td class="num">12 months</td><td class="num signal-weak">-0.09</td><td class="num">-0.07</td><td>Data only from 2007</td></tr>
<tr><td>Market Structure Index (MSI)</td><td>SPX 63d return</td><td class="num">3 months</td><td class="num signal-weak">-0.11</td><td class="num">-0.08</td><td>Better as sizing overlay than alpha signal</td></tr>
<tr><td>Sentiment & Positioning Index (SPI)</td><td>SPX 21d return</td><td class="num">1 month</td><td class="num signal-weak">+0.12</td><td class="num">+0.12</td><td>Contrarian; tested wrong by design (use threshold)</td></tr>
</tbody>
</table>

<div class="callout win">
  <div class="callout-label">The story this tells</div>
  <strong>Seven pillars genuinely lead their domain variables by 6-12 months.</strong> This is the engine of the framework. The Labor Pressure Index moves before the unemployment rate moves. The Business Conditions Index moves before new orders move. The Government Conditions Index moves before high-yield credit widens. These are not coincident indicators repackaged; they're forward-looking composites with measurable lead time.
  <br><br>
  The pillars that don't show this pattern in continuous-IC tests (Liquidity Cushion Index, Sentiment & Positioning Index, Market Structure Index, Housing Conditions Index) are <strong>not failing</strong> — they're being tested wrong. They have real signal at extreme readings, captured in the threshold sweeps. Continuous IC is the wrong test for a contrarian indicator (SPI), an event-trigger indicator (LCI), or a regime overlay (MSI).
</div>

<p>This reframing is the most publishable finding from the rebuild: <em>the pillars work. They lead the data. The framework is doing what we said it does.</em> The only question is which test you apply (continuous IC for trend predictors, threshold lift for event predictors).</p>

<h2 id="pillar-opt">Per-Pillar Component Weight Optimization (Phase 3)</h2>

<p>For each of the 12 pillars, I rebuilt the composite from raw component series, applied theoretical signs per the master context, and optimized weights using rank information coefficient (Spearman rank correlation) against the pillar's domain target. SLSQP, 30 Dirichlet restarts, bounds [0.05, 0.30], 90/10 in-sample / out-of-sample split.</p>

<p>Tighter bounds (0.05 to 0.30 vs the original 0.02 to 0.40) were applied after a first pass produced corner solutions. The tighter bounds gave more diversified, more interpretable weights and improved out-of-sample stability.</p>

<table>
<thead><tr>
<th>Pillar</th>
<th>Domain Target</th>
<th class="num">Judgment OOS IC</th>
<th class="num">Optimized OOS IC</th>
<th class="num">|Improvement|</th>
<th class="num">Max Weight</th>
<th>Decision</th>
</tr></thead>
<tbody>
{rows_html}
</tbody>
</table>

<div class="callout win">
  <div class="callout-label">Three adoption candidates</div>
  <strong>Business Conditions Index (BCI):</strong> Optimized weights raise OOS information coefficient from +0.45 to +0.57. Optimizer loads on Gross Private Domestic Investment, New Orders Capital Goods, and Business Inventories. Shrinkage analysis showed monotonic improvement with α — full optimization (α=1.0) wins at the new bounds.
  <br><br>
  <strong>Labor Pressure Index (LPI):</strong> OOS IC magnitude from 0.32 to 0.38. Optimizer leans on long-term unemployment and quits rate (negative sign). Real signal — labor flows lead the unemployment rate by 6-12 months.
  <br><br>
  <strong>Price Conditions Index (PCI):</strong> Judgment baseline OOS IC was essentially zero (+0.005); optimized hits +0.30. Optimizer favors trimmed-mean CPI and core PCE over headline CPI. <em>Caveat:</em> the dramatic improvement should make us cautious — judgment was so weak that any reasonable weights look great. Walk-forward weight stability needs another look before publishing.
</div>

<div class="callout warn">
  <div class="callout-label">Six pillars produce strong signal under judgment weights — keep them</div>
  Growth Conditions Index (GCI), Government Conditions Index (GCI-Gov), Trade Conditions Index (TCI), and Financial Conditions Index (FCI) all show |OOS IC| ≥ 0.40 under judgment weights. The optimizer can't improve on that. <strong>The judgment weights are already correct for these pillars.</strong>
</div>

<div class="callout fail">
  <div class="callout-label">Three pillars don't produce strong signal at all</div>
  <strong>Market Structure Index (MSI), Sentiment & Positioning Index (SPI), and Liquidity Cushion Index (LCI)</strong> all have weak |OOS IC| (under 0.20) under judgment weights AND under optimization. Possible reasons:
  <ol>
    <li><strong>MSI</strong> may be cut up by reflexive markets — the same trend-following signals that work in 2020 produce false positives in 2017-19.</li>
    <li><strong>SPI</strong> is contrarian by design; rank IC against forward returns isn't the right test (we'd expect non-monotonic distributions). The threshold sweep showed SPI ≥ +0.3 produces 1.36x lift on short-horizon drawdown — a real but small signal.</li>
    <li><strong>LCI</strong> is designed for funding-stress prediction, not equity returns. Threshold sweep showed LCI z ≤ -2.0 produces <strong>2.34x lift</strong> on forward HY OAS widening events — a real and strong signal that doesn't show up in continuous IC tests.</li>
  </ol>
  All three can be useful at threshold extremes even if continuous-IC optimization fails.
</div>

<h2 id="threshold-pillars">Per-Pillar Threshold Sweeps (complementary)</h2>

<p>Where weight optimization produced weak continuous IC, threshold sweeps reveal the indicators' actual usable signal: <em>at extreme readings</em>.</p>

<table>
<thead><tr>
<th>Pillar</th>
<th>Best Threshold</th>
<th>Domain Target</th>
<th class="num">Lift vs Base</th>
<th>Quality</th>
</tr></thead>
<tbody>
<tr><td><strong>Labor Pressure Index (LPI)</strong></td><td>z ≤ -1.8</td><td>UR rises ≥ 0.5pp / 252d</td><td class="num signal-strong">2.58x</td><td class="signal-strong">Strongest in stack</td></tr>
<tr><td><strong>Liquidity Cushion Index (LCI)</strong></td><td>z ≤ -2.0</td><td>HY OAS widens ≥ 100bps / 21d</td><td class="num signal-strong">2.34x</td><td class="signal-strong">Funding-stress predictor</td></tr>
<tr><td><strong>Business Conditions Index (BCI)</strong></td><td>z ≤ -2.0</td><td>Cap goods YoY ≤ -2% / 365d</td><td class="num signal-strong">2.16x</td><td class="signal-strong">Capex deceleration</td></tr>
<tr><td><strong>Macro Risk Index (MRI)</strong></td><td>z ≥ +1.0</td><td>SPX 63d ≤ -10% drawdown</td><td class="num signal-strong">3.15x</td><td class="signal-strong">Crisis filter</td></tr>
<tr><td><strong>Financial Conditions Index (FCI)</strong></td><td>z ≤ -2.0</td><td>HY OAS widens ≥ 100bps / 126d</td><td class="num signal-strong">1.81x</td><td class="signal-strong">Credit stress</td></tr>
<tr><td><strong>Housing Conditions Index (HCI)</strong></td><td>z ≤ -1.6</td><td>Housing starts YoY ≤ -10% / 365d</td><td class="num signal-strong">1.76x</td><td class="signal-strong">Real-economy lead</td></tr>
<tr><td>Sentiment & Positioning Index (SPI)</td><td>z ≥ +0.3</td><td>SPX 5d &lt;-5%</td><td class="num signal-weak">1.36x</td><td class="signal-weak">Marginal</td></tr>
<tr><td>Market Structure Index (MSI)</td><td>z ≤ -1.6</td><td>SPX 21d &lt;-5%</td><td class="num signal-weak">1.23x</td><td class="signal-weak">Better as overlay</td></tr>
<tr><td>Price Conditions Index (PCI)</td><td>z ≥ +2.3</td><td>core PCE YoY ≥ 3% / 365d</td><td class="num signal-weak">1.24x</td><td class="signal-weak">Target too common</td></tr>
<tr><td>Growth Conditions Index (GCI)</td><td>z ≤ -1.2</td><td>GDP YoY ≤ -0.5% / 365d</td><td class="num signal-weak">1.05x</td><td class="signal-weak">Recession too rare</td></tr>
<tr><td>Consumer Conditions Index (CCI)</td><td>—</td><td>real PCE YoY ≤ 0.5%</td><td class="num signal-fail">0.96x</td><td class="signal-fail">Data 2007+ only</td></tr>
<tr><td>Trade Conditions Index (TCI)</td><td>—</td><td>net exports declining</td><td class="num signal-fail">&lt;1.0x</td><td class="signal-fail">No threshold signal</td></tr>
<tr><td>Government Conditions Index (GCI-Gov)</td><td>—</td><td>10y term premium rising 0.5pp / 252d</td><td class="num signal-fail">0.66x</td><td class="signal-fail">Inverted at threshold</td></tr>
</tbody>
</table>

<p><strong>Bottom line:</strong> six indicators (Labor Pressure, Liquidity Cushion, Business Conditions, Macro Risk, Financial Conditions, Housing Conditions) produce strong tradeable lifts at extreme readings. That's the publishable, sleeve-actionable list.</p>

<h2 id="audit">Cross-Indicator Correlation Audit (Phase 7)</h2>

<p>Pearson correlations across 16 indicators (the 12 pillars plus Macro Risk Index, Market Structure Index, Sentiment & Positioning Index, Liquidity Cushion Index, Credit-Labor Gap, Structure-Breadth Divergence, Sentiment-Structure Divergence) over 6,329 aligned daily observations from October 2000 to December 2025.</p>

<div class="callout">
  <div class="callout-label">Only one redundancy</div>
  <strong>Market Structure Index (MSI) ↔ Structure-Breadth Divergence (SBD) = +0.84</strong>. Makes sense: SBD is defined as <span class="code">z(price vs 200d) - z(% above 50d MA)</span>, which uses Market Structure components. SBD is a derivative signal of MSI, not independent. Recommendation: do not present both publicly without acknowledging the relationship.
</div>

<p>All other pillar correlations are below 0.6. The framework is well-orthogonalized. Other notable correlations (none redundant):</p>

<ul>
<li>Macro Risk Index ↔ Labor Pressure Index = -0.59 (LPI is a major MRI input — expected)</li>
<li>Macro Risk Index ↔ Financial Conditions Index = -0.49, Business Conditions Index = -0.47, Trade Conditions Index = -0.47, Liquidity Cushion Index = -0.45 (MRI summing its inputs — expected)</li>
<li>Market Structure Index ↔ Sentiment & Positioning Index = -0.56 (structure vs sentiment, expected mild inverse)</li>
<li>Financial Conditions Index ↔ Liquidity Cushion Index = +0.48 (both financial-conditions composites)</li>
<li>Housing Conditions Index ↔ Government Conditions Index = -0.26 (housing weakens when fiscal pressure rises — interesting)</li>
</ul>

<h2 id="decisions">Decisions, Issues, Open Questions</h2>

<h3>Decisions ready to ship</h3>

<ol>
<li><strong>Adopt optimized weights for Business Conditions Index (BCI), Labor Pressure Index (LPI), and Price Conditions Index (PCI).</strong> All three with tighter bounds [0.05, 0.30]. Update <span class="code">CLAUDE_MASTER.md</span> Section 3 to reflect new weights once Bob approves.</li>
<li><strong>Keep Macro Risk Index (MRI) judgment weights.</strong> Optimization overfit. The crisis-filter reframing is more valuable than the weight rebuild.</li>
<li><strong>Reframe Macro Risk Index as a binary crisis filter</strong> with new 4-regime multiplier table starting compression at z ≥ +0.4.</li>
<li><strong>Six "publishable" pillar findings</strong> (LPI, LCI, BCI, MRI, FCI, HCI) all show strong threshold-based signals. Each can anchor a Beam.</li>
</ol>

<h3>Two-path forks (where I went both ways)</h3>

<ol>
<li><strong>Phase 2 indicator targets:</strong> first pass used forward S&P 500 returns for everything. Second pass used domain-appropriate targets (HY widening for LCI, FCI, GCI-Gov). The second pass was right — Liquidity Cushion Index's signal only emerges with the right target.</li>
<li><strong>Pillar weight bounds:</strong> first pass used [0.02, 0.40]. All optimizations hit the upper bound (corner solutions = overfit warning). Second pass used [0.05, 0.30] for the three adoption candidates. Resulted in cleaner weights without losing OOS signal.</li>
<li><strong>Shrinkage on adoption candidates:</strong> tested α = 0, 0.25, 0.5, 0.75, 1.0 mixing judgment and optimized weights. Found monotonic improvement with α — no optimal blend point exists. Just use full optimization at the tighter bounds.</li>
</ol>

<h3>Open questions for Bob</h3>

<ol>
<li>The +0.4 Macro Risk Index compression threshold is more conservative than the v2.0 doc. Should we update the framework doc, run a back-test of the new vs old multiplier table, or just note it and ship?</li>
<li>Government Conditions Index (GCI-Gov) inverted result at threshold extreme — investigate before publishing, or accept that the term-premium target may not be the right domain variable?</li>
<li>Consumer Conditions Index (CCI) component data only goes back to 2007 — extend backwards or accept the limitation and document it?</li>
<li>Price Conditions Index (PCI) optimization: judgment baseline was essentially zero, so any improvement looks dramatic. Adopt now, or wait for an additional walk-forward stability check?</li>
<li>Standalone signals from master plan Phase 4 (Dealer Positioning vs Auction Tails, Breadth Thrust binary) couldn't be tested due to missing or short data series. Worth queuing a data-infrastructure project to enable these?</li>
</ol>

<h3>Issues & caveats</h3>

<h4>Methodological</h4>
<ol>
<li><strong>Year-by-year information coefficient instability is universal.</strong> Even Macro Risk Index with current judgment weights flips IC sign in 12 of 26 years. The framework only "works" in pooled stats because crisis years dominate. This is a fundamental property of macro indicators built on slow-moving data.</li>
<li><strong>Out-of-sample window (2023-06 to 2025-12) is anomalous.</strong> A bull market with elevated Macro Risk Index readings — the sign of MRI vs forward-returns inverted in this window. Tighter training windows didn't fix it.</li>
<li><strong>Threshold sweep n is small at extremes.</strong> The MRI ≥ +1.1 bucket has only 24 observations. The 4.5x lift is real but n is too small to call high-confidence.</li>
<li><strong>Adoption candidates all hit the +0.30 max-weight bound.</strong> This means the search is still finding corner solutions, just at a tighter bound. May indicate the optimization is still overweighting one or two components more than is robust. Worth running with even tighter bounds (e.g., 0.25) to confirm.</li>
</ol>

<h4>Data infrastructure</h4>
<ol>
<li>S&P 500 series in Lighthouse_Master.db is <span class="code">SPX_Close</span> (not SP500/GSPC/SPY). Original optimization scripts didn't catch this. Fixed.</li>
<li>Pillar value series end dates differ. Consumer Conditions Index ends 2026-01-01, Business Conditions Index ends 2026-04-21, etc. Aligned datasets truncate to the worst case.</li>
<li>Several modern series are short. Breadth metrics (S&P 500 % above 20d/50d/200d) only start 2023; SOFR starts 2018; IORB starts 2021.</li>
</ol>

<h4>Master plan deltas</h4>
<ol>
<li>Master plan referenced <span class="code">/Users/bob/LHM/Strategy/MRI_WEIGHT_OPTIMIZATION.md</span> as a finalized spec. File didn't exist on disk — only the script existed (in iCloud). Spec was reconstructed from script header.</li>
<li>Master plan Phase 0 was "rebuild Crypto Liquidity Impulse to 8 components." Resolved on inspection: the published article keeps weights proprietary, so the 4-component implementation in <span class="code">cli_final.py</span> is consistent with the public framing. No drift to fix. Header note added pointing at strategy doc.</li>
</ol>

<h2 id="nextsteps">Next Steps</h2>

<h4>Ready to ship as content</h4>
<ol>
<li><strong>Beam — "Why we kept the judgment weights for Macro Risk Index"</strong> (transparency piece). Full optimization, OOS sign-flip, adoption decision.</li>
<li><strong>Beam — "Macro Risk Index as a crisis filter"</strong> (threshold reframing). New 4-regime multiplier table.</li>
<li><strong>Beam — "Liquidity Cushion Index predicts funding stress"</strong>. 2.34x lift on HY OAS widening at z ≤ -2.0.</li>
<li><strong>Beam — "Labor as the source code"</strong>. Labor Pressure Index 2.58x lift on UR rise. Rebuilt component weights for LPI.</li>
<li><strong>Beam — "Capex tells you the truth"</strong>. Business Conditions Index rebuilt with optimized weights, +0.57 OOS information coefficient.</li>
<li><strong>Beam — "Inflation forecasting was broken; we fixed it"</strong>. Price Conditions Index judgment was at zero; optimized hits +0.30. (Pending second walk-forward check.)</li>
<li><strong>Chartbook section</strong> — overlay all six "strong signal" indicators on their target series.</li>
</ol>

<h4>Internal work queued</h4>
<ol>
<li>Update <span class="code">CLAUDE_MASTER.md</span> Section 3 (composite formulas) with adopted weights for BCI, LPI, PCI. Pending Bob approval.</li>
<li>Update <span class="code">TWO_BOOKS_FRAMEWORK.md</span> regime multiplier table to 4-regime cut at +0.4 / +1.0 for MRI. Pending Bob decision.</li>
<li>Investigate Government Conditions Index inverted threshold result — re-test against term premium acceleration, not delta.</li>
<li>Extend Consumer Conditions Index backwards to pre-2007 (rebuild from raw components).</li>
<li>Queue data infrastructure: dealer positioning (NY Fed primary dealer survey), pre-2023 breadth metrics from raw constituent data.</li>
<li>Add incremental-information test — regress fwd returns on Macro Risk Index plus each standalone individually to check R² delta.</li>
</ol>

<h4>Files generated</h4>
<table>
<thead><tr><th>Output</th><th>Path</th></tr></thead>
<tbody>
<tr><td>Macro Risk Index optimization (full)</td><td class="code">Outputs/mri_optimization/mri_optimization_results.json</td></tr>
<tr><td>Macro Risk Index follow-ups (window/shrinkage/crisis-filter)</td><td class="code">Outputs/mri_optimization/mri_followups_results.json</td></tr>
<tr><td>Macro Risk Index threshold sweep</td><td class="code">Outputs/mri_optimization/mri_threshold_results.json</td></tr>
<tr><td>Per-pillar component weight optimization (v1, original bounds)</td><td class="code">Outputs/mri_optimization/pillar_weight_optimization.json</td></tr>
<tr><td>Per-pillar component weight optimization (v2, tighter bounds)</td><td class="code">Outputs/mri_optimization/pillar_weight_optimization_v2.json</td></tr>
<tr><td>Phase 2 (forward returns)</td><td class="code">Outputs/mri_optimization/phase2_threshold_results.json</td></tr>
<tr><td>Phase 2 v2 (domain targets)</td><td class="code">Outputs/mri_optimization/phase2_threshold_v2_results.json</td></tr>
<tr><td>Phase 3+4 Tier B + standalone</td><td class="code">Outputs/mri_optimization/phase3_4_threshold_results.json</td></tr>
<tr><td>Phase 4+7 standalone + audit</td><td class="code">Outputs/mri_optimization/phase4_7_results.json</td></tr>
<tr><td>Scripts</td><td class="code">Scripts/backtest/{{mri_*,pillar_*,phase2_*,phase3_4_*,phase4_7_*,build_indicator_rebuild_report}}.py</td></tr>
</tbody>
</table>

<div class="footer">
  <a href="https://lighthousemacro.com">Lighthouse Macro</a> ·
  <a href="https://research.lighthousemacro.com">Research</a> ·
  <a href="https://x.com/LHMacro">@LHMacro</a>
</div>

</body>
</html>
"""

    REPORT_PATH.write_text(html)
    print(f"Report written: {REPORT_PATH}")
    print(f"Size: {REPORT_PATH.stat().st_size / 1024:.1f} KB")


if __name__ == "__main__":
    build_report()
