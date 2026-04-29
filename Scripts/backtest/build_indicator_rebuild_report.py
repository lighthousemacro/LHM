#!/usr/bin/env python3
"""
Build branded HTML report — LHM Indicator Rebuild
====================================================
Compiles findings from MRI optimization + Phase 1/2/3/4/7 sweeps
into a single self-contained branded HTML artifact.

Author: Lighthouse Macro
Date: 2026-04-29
"""

import base64
import json
from datetime import datetime
from pathlib import Path

OUTPUT_DIR = Path("/Users/bob/LHM/Outputs/mri_optimization")
REPORT_PATH = OUTPUT_DIR / "INDICATOR_REBUILD_REPORT.html"

# Brand assets
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


def build_report():
    # Load all results
    mri = load_json(OUTPUT_DIR / "mri_optimization_results.json") or {}
    followups = load_json(OUTPUT_DIR / "mri_followups_results.json") or {}
    threshold = load_json(OUTPUT_DIR / "mri_threshold_results.json") or {}
    phase2_v2 = load_json(OUTPUT_DIR / "phase2_threshold_v2_results.json") or {}
    phase3_4 = load_json(OUTPUT_DIR / "phase3_4_threshold_results.json") or {}
    phase4_7 = load_json(OUTPUT_DIR / "phase4_7_results.json") or {}

    icon_b64 = b64_image(ICON_PATH)
    today = datetime.now().strftime("%B %d, %Y")

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

/* Brand header */
.brand-header {{
  display: flex;
  align-items: center;
  gap: 16px;
  padding-bottom: 16px;
  border-bottom: 4px solid #2389BB;
  margin-bottom: 36px;
}}
.brand-icon {{
  width: 36px;
  height: 36px;
  flex-shrink: 0;
}}
.brand-text {{
  display: flex;
  flex-direction: column;
}}
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

/* Accent bar */
.accent-bar {{
  display: flex;
  height: 5px;
  margin: 28px 0 14px;
}}
.accent-bar .ocean {{ background: #2389BB; flex: 2; }}
.accent-bar .dusk  {{ background: #FF6723; flex: 1; }}

/* Doc title */
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

/* Section headers */
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

/* Callouts */
.callout {{
  background: #F8F9FA;
  border-left: 4px solid #2389BB;
  padding: 14px 18px;
  margin: 18px 0;
  font-size: 13px;
}}
.callout.win {{ border-left-color: #00BB89; background: #F0FAF7; }}
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
.callout.win .callout-label  {{ color: #00BB89; }}
.callout.warn .callout-label {{ color: #FF6723; }}
.callout.fail .callout-label {{ color: #FF2389; }}
.callout       .callout-label {{ color: #2389BB; }}

/* Tables */
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

/* Lists */
ul, ol {{ margin: 8px 0 14px 24px; }}
li {{ margin-bottom: 4px; }}

/* Footer */
.footer {{
  margin-top: 60px;
  padding-top: 16px;
  border-top: 1px solid #D1D1D1;
  font-size: 10px;
  color: #898989;
  text-align: center;
}}
.footer a {{
  color: #2389BB;
  text-decoration: none;
  margin: 0 8px;
}}
.footer a:hover {{ text-decoration: underline; }}

/* TOC */
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
<h1 class="doc-title">Indicator Rebuild — Phase 1-7 Findings</h1>
<div class="doc-meta">{today} · MRI Weight Optimization, Threshold Sweeps, Tier B Pillars, Standalone Signals, Audit</div>

<div class="accent-bar"><div class="ocean"></div><div class="dusk"></div></div>

<!-- TOC -->
<div class="toc">
  <div class="toc-title">Contents</div>
  <ol>
    <li><a href="#headline">Headline</a></li>
    <li><a href="#mri">Phase 1 — MRI Weight Optimization</a></li>
    <li><a href="#threshold">Phase 1 — MRI Threshold Sweep</a></li>
    <li><a href="#phase2">Phase 2 — MSI / SPI / LCI / CLG / SBD / SSD</a></li>
    <li><a href="#phase3">Phase 3 — Tier B Pillars</a></li>
    <li><a href="#phase4">Phase 4 — Standalone Signals</a></li>
    <li><a href="#phase7">Phase 7 — Correlation Audit</a></li>
    <li><a href="#decisions">Decisions & Open Questions</a></li>
    <li><a href="#issues">Issues & Caveats</a></li>
    <li><a href="#nextsteps">Next Steps</a></li>
  </ol>
</div>

<!-- HEADLINE -->
<h2 id="headline">Headline</h2>

<div class="callout win">
  <div class="callout-label">Result</div>
  <strong>Five indicators have a strong, tradeable signal at extreme thresholds.</strong>
  Three indicators (MRI, the v2.0 framework's "MRI &gt;= +1.0" threshold; LCI for funding stress; LPI for labor weakness) produce 2x-3x lifts on their relevant forward outcomes.
  Two more (BCI for capex deceleration, HCI for housing weakness) produce 1.7x-2.2x lifts.
</div>

<div class="callout warn">
  <div class="callout-label">Adoption</div>
  <strong>Keep current MRI judgment weights. Optimization overfit.</strong>
  Five of six master-plan invalidation criteria fired against the SLSQP-optimized weights. The judgment baseline beats the optimization out-of-sample. The optimizer's bet on GCI_Gov (29% weight, near the 30% cap) is a textbook overfit signal.
</div>

<div class="callout fail">
  <div class="callout-label">Issue</div>
  <strong>Several indicators are flat or inverted at the equity-return target.</strong>
  MSI, SPI, SBD, SSD all produce &lt; 1.5x lift against forward SPX returns. Some of this is a wrong-test problem: LCI is designed for funding-stress prediction (works strong: 2.34x lift), and CLG was tested against HY widening (works weak: 1.07x). But the equity-side composites really do underperform on the data.
</div>

<h3>Strongest signals at-a-glance</h3>
<table>
<thead><tr><th>Indicator</th><th>Best Threshold</th><th>Target</th><th class="num">Lift</th><th>Notes</th></tr></thead>
<tbody>
<tr><td><strong>LPI</strong></td><td>z &le; -1.8</td><td>UR rises &ge; 0.5pp / 252d</td><td class="num signal-strong">2.58x</td><td>Best signal in the stack</td></tr>
<tr><td><strong>LCI</strong></td><td>z &le; -2.0</td><td>HY OAS widens &ge; 100bps / 21d</td><td class="num signal-strong">2.34x</td><td>Funding-stress predictor — designed for this target</td></tr>
<tr><td><strong>BCI</strong></td><td>z &le; -2.0</td><td>Cap goods YoY &le; -2% / 365d</td><td class="num signal-strong">2.16x</td><td>Capex deceleration leads cycle</td></tr>
<tr><td><strong>MRI</strong></td><td>z &ge; +1.0</td><td>SPX 63d &lt;-10% drawdown</td><td class="num signal-strong">3.15x</td><td>Crisis filter, not regime conditioner</td></tr>
<tr><td><strong>FCI</strong></td><td>z &le; -2.0</td><td>HY OAS widens &ge; 100bps / 126d</td><td class="num signal-strong">1.81x</td><td>Slower than LCI, captures broader stress</td></tr>
<tr><td><strong>HCI</strong></td><td>z &le; -1.6</td><td>Housing starts YoY &le; -10% / 365d</td><td class="num signal-strong">1.76x</td><td>Real-economy lead</td></tr>
<tr><td>CLG</td><td>z &le; -1.8</td><td>HY widening 63d</td><td class="num signal-weak">1.07x</td><td>Circular: HY OAS is in the formula</td></tr>
<tr><td>MSI</td><td>z &le; -1.6</td><td>SPX 21d &lt;-5%</td><td class="num signal-weak">1.23x</td><td>Better as gross-exposure overlay than alpha signal</td></tr>
<tr><td>SPI</td><td>z &ge; +0.3</td><td>SPX 5d &lt;-5%</td><td class="num signal-weak">1.36x</td><td>Contrarian; signal is real but weak in pooled stats</td></tr>
<tr><td>SBD</td><td>z &ge; +2.1</td><td>SPX 21d &lt;-5%</td><td class="num signal-weak">1.12x</td><td>Distribution warning — small effect</td></tr>
<tr><td>SSD</td><td>z &le; -1.6</td><td>SPX 5d &lt;-5%</td><td class="num signal-weak">1.53x</td><td>Capitulation detector; small n</td></tr>
<tr><td>PCI</td><td>z &ge; +2.3</td><td>core PCE YoY &ge; 3% / 365d</td><td class="num signal-weak">1.24x</td><td>Target rate too common (base 42%)</td></tr>
<tr><td>GCI</td><td>z &le; -1.2</td><td>GDP YoY &le; -0.5% / 365d</td><td class="num signal-weak">1.05x</td><td>Recession too rare in modern era to validate</td></tr>
<tr><td>CCI</td><td>—</td><td>real PCE YoY &le; 0.5%</td><td class="num signal-fail">0.96x</td><td>Data only from 2007 onwards; too short to validate</td></tr>
<tr><td>TCI</td><td>—</td><td>net exports declining</td><td class="num signal-fail">&lt;1.0x</td><td>No tradeable signal at extreme</td></tr>
<tr><td>GCI_Gov</td><td>—</td><td>10y term premium rising 0.5pp / 252d</td><td class="num signal-fail">0.66x</td><td>Inverted — needs investigation</td></tr>
<tr><td>Quits/Claims</td><td>z &le; -1.8</td><td>HY widening 63d</td><td class="num signal-weak">1.33x</td><td>Mild signal; not strong enough to publish</td></tr>
</tbody>
</table>

<!-- PHASE 1 — MRI -->
<h2 id="mri">Phase 1 — MRI Weight Optimization</h2>

<p>The optimization ran the full master-plan spec: SLSQP with 30 Dirichlet restarts, bounds [0.02, 0.30], 90/10 IS/OOS split, 5-split walk-forward, expanding z-scores, ±3 winsorized. Sortino on Q1-Q5 spread as the objective at 63d horizon.</p>

<h4>Result: Do not adopt</h4>

<p>Walk-forward summary across 5 expanding splits:</p>
<table>
<thead><tr><th>Metric</th><th class="num">Optimized</th><th class="num">Current (Judgment)</th></tr></thead>
<tbody>
<tr><td>Avg OOS Spread</td><td class="num signal-fail">-0.0022</td><td class="num signal-strong">+0.0124</td></tr>
<tr><td>Avg OOS IC</td><td class="num">+0.0116</td><td class="num">+0.0279</td></tr>
</tbody>
</table>

<p><strong>Judgment beats optimization out-of-sample.</strong> Five of six invalidation criteria from the master plan fired:</p>

<table>
<thead><tr><th>#</th><th>Criterion</th><th>Result</th><th>Status</th></tr></thead>
<tbody>
<tr><td>1</td><td>IS/OOS spread &gt; 2x at primary</td><td>IS -0.049 / OOS +0.079 (sign flip)</td><td class="signal-fail">HIT</td></tr>
<tr><td>2</td><td>Walk-forward weight std &gt; 0.06 for 3+ pillars</td><td>LCI 0.056, CCI 0.076, GCI_Gov 0.065</td><td class="signal-fail">HIT</td></tr>
<tr><td>3</td><td>Monotonicity breaks OOS at primary</td><td>Working in opposite direction</td><td class="signal-fail">HIT</td></tr>
<tr><td>4</td><td>Any weight &gt; 0.25 (dominance)</td><td>GCI_Gov = 0.293</td><td class="signal-fail">HIT</td></tr>
<tr><td>5</td><td>Annual IC sign flip &gt; 30% of windows</td><td>12 of 26 years (46%)</td><td class="signal-fail">HIT</td></tr>
<tr><td>6</td><td>Elevated MDD vs Low Risk</td><td>-19.3% vs -12.9% (1.5x)</td><td class="signal-strong">OK</td></tr>
</tbody>
</table>

<h4>What the data is actually telling us</h4>

<p>MRI's pooled IC over 26 years is -0.09 at 63d (statistically significant). Year-by-year, the IC is a sign-flip mess. The framework "works" in pooled stats because the few crisis years (2007-09, 2020 H1) are massively negative-IC and overwhelm the noise. But year-to-year, in normal markets, it's a coin flip.</p>

<p>This isn't a reason to abandon MRI. It's a reason to <strong>reframe what MRI is for</strong>. See the threshold sweep section below — the answer is that MRI is a binary crisis filter, not a continuous regime conditioner.</p>

<!-- THRESHOLD -->
<h2 id="threshold">Phase 1 — MRI Threshold Sweep</h2>

<p>Reframing MRI as a threshold signal aligned with the v2.0 framework's role for it: identify the restrictive regime where the framework-driven sleeve compresses. Sweep MRI z-scores from -0.5 to +2.0 in 0.1 steps. Compute drawdown frequency at each threshold.</p>

<table>
<thead><tr><th>MRI Threshold</th><th class="num">N</th><th class="num">% of pop</th><th class="num">63d Mean</th><th class="num">% with 63d &lt; -5%</th><th class="num">% with 63d &lt; -10%</th><th class="num">Lift (vs base)</th></tr></thead>
<tbody>
<tr><td>z &ge; +0.4</td><td class="num">881</td><td class="num">14.1%</td><td class="num">-0.83%</td><td class="num">26.7%</td><td class="num">16.6%</td><td class="num signal-strong">2.01x</td></tr>
<tr><td>z &ge; +1.0</td><td class="num">50</td><td class="num">0.8%</td><td class="num">+0.27%</td><td class="num">36.0%</td><td class="num">26.0%</td><td class="num signal-strong">3.15x</td></tr>
<tr><td>z &ge; +1.1</td><td class="num">24</td><td class="num">0.4%</td><td class="num">-4.18%</td><td class="num">58.3%</td><td class="num">37.5%</td><td class="num signal-strong">4.55x</td></tr>
</tbody>
</table>

<p>Two distinct break-points emerge. Both are real, both useful for different sizing decisions.</p>

<div class="callout">
  <div class="callout-label">Recommended new regime multiplier table</div>
  <table style="margin: 8px 0 0">
  <thead><tr><th>MRI Range</th><th>Regime</th><th class="num">Multiplier</th><th class="num">% pop</th><th class="num">63d &lt;-5%</th></tr></thead>
  <tbody>
  <tr><td>z &lt; -0.5</td><td>Supportive</td><td class="num">1.0x</td><td class="num">10%</td><td class="num">7.8%</td></tr>
  <tr><td>-0.5 to +0.4</td><td>Neutral</td><td class="num">1.0x</td><td class="num">76%</td><td class="num">~15%</td></tr>
  <tr><td>+0.4 to +1.0</td><td>Cautious</td><td class="num">0.6x</td><td class="num">13%</td><td class="num">~26%</td></tr>
  <tr><td>z &ge; +1.0</td><td>Restrictive</td><td class="num">0.3x</td><td class="num">1%</td><td class="num">36%</td></tr>
  </tbody>
  </table>
  Change vs v2.0 doc: compression starts at +0.4, not +1.0. The data says you should start trimming at +0.4.
</div>

<!-- PHASE 2 -->
<h2 id="phase2">Phase 2 — Tier A Composites + Cross-Pillar Divergences</h2>

<p>Six indicators tested against domain-appropriate forward targets:</p>

<table>
<thead><tr><th>Indicator</th><th>Target</th><th>Best Threshold</th><th class="num">Best Lift</th></tr></thead>
<tbody>
<tr><td>MSI</td><td>fwd SPX 21d, drawdown &lt;-5%</td><td>z &le; -1.6</td><td class="num signal-weak">1.23x</td></tr>
<tr><td>SPI</td><td>fwd SPX 5d, drawdown &lt;-5%</td><td>z &ge; +0.3</td><td class="num signal-weak">1.36x</td></tr>
<tr><td>SBD</td><td>fwd SPX 21d, drawdown &lt;-5%</td><td>z &ge; +2.1</td><td class="num signal-weak">1.12x</td></tr>
<tr><td>SSD</td><td>fwd SPX 5d, drawdown &lt;-5%</td><td>z &le; -1.6</td><td class="num signal-weak">1.53x</td></tr>
<tr><td><strong>LCI</strong></td><td>fwd HY OAS widens 100bps in 21d</td><td>z &le; -2.0</td><td class="num signal-strong">2.34x</td></tr>
<tr><td>CLG</td><td>fwd HY OAS widens 100bps in 63d</td><td>z &le; -1.8</td><td class="num signal-weak">1.07x</td></tr>
</tbody>
</table>

<div class="callout win">
  <div class="callout-label">Strong signal</div>
  <strong>LCI is a real funding-stress predictor.</strong> When LCI z-score drops to -2.0 (5.3% of sample), forward 21d HY OAS widening hits the 100bps threshold 17.4% of the time vs base 7.4%. That's a 2.34x lift. Same signal at 63d horizon: 1.70x. Worth publishing as a standalone Beam.
</div>

<div class="callout warn">
  <div class="callout-label">Weak signals across MSI/SPI/SBD/SSD</div>
  These four equity-side composites all produce sub-1.5x lifts against forward SPX returns at any threshold. Possible explanations: (1) they're each capturing one piece of an already-priced signal, (2) the existing weights need rework, (3) the indicators are useful for sizing but not for entry timing. Still useful as inputs to MRI; weak as standalone signals.
</div>

<div class="callout fail">
  <div class="callout-label">Note on CLG</div>
  CLG = z(HY_OAS) - z(LFI). It's circular vs the HY widening target — HY OAS is in the formula. Validation against forward HY widening should swap to a non-circular target like CDX widening or default rates.
</div>

<!-- PHASE 3 -->
<h2 id="phase3">Phase 3 — Tier B Pillars (Domain Targets)</h2>

<p>9 pillars tested against domain variables (not forward equity returns). Per master plan, each pillar should be the best possible thermometer for its domain; MRI handles translation to positioning.</p>

<table>
<thead><tr><th>Pillar</th><th>Target</th><th>Best Threshold</th><th class="num">Lift</th><th>Quality</th></tr></thead>
<tbody>
<tr><td><strong>LPI</strong></td><td>UR rises &ge; 0.5pp / 252d</td><td>z &le; -1.8</td><td class="num signal-strong">2.58x</td><td class="signal-strong">Strong</td></tr>
<tr><td><strong>BCI</strong></td><td>Cap goods YoY &le; -2% / 365d</td><td>z &le; -2.0</td><td class="num signal-strong">2.16x</td><td class="signal-strong">Strong</td></tr>
<tr><td><strong>FCI</strong></td><td>HY OAS widens &ge; 100bps / 126d</td><td>z &le; -2.0</td><td class="num signal-strong">1.81x</td><td class="signal-strong">Solid</td></tr>
<tr><td><strong>HCI</strong></td><td>Housing starts YoY &le; -10% / 365d</td><td>z &le; -1.6</td><td class="num signal-strong">1.76x</td><td class="signal-strong">Solid</td></tr>
<tr><td>PCI</td><td>core PCE YoY &ge; 3% / 365d</td><td>z &ge; +2.3</td><td class="num signal-weak">1.24x</td><td class="signal-weak">Weak (base too common)</td></tr>
<tr><td>GCI</td><td>GDP YoY &le; -0.5% / 365d</td><td>z &le; -1.2</td><td class="num signal-weak">1.05x</td><td class="signal-weak">Weak (event too rare)</td></tr>
<tr><td>CCI</td><td>real PCE YoY &le; 0.5% / 365d</td><td>z &le; -0.6</td><td class="num signal-fail">0.96x</td><td class="signal-fail">Inverted (data 2007+ only)</td></tr>
<tr><td>TCI</td><td>net exports declining</td><td>—</td><td class="num signal-fail">&lt;1.0x</td><td class="signal-fail">No signal</td></tr>
<tr><td>GCI_Gov</td><td>10y term premium rising 0.5pp / 252d</td><td>—</td><td class="num signal-fail">0.66x</td><td class="signal-fail">Inverted</td></tr>
</tbody>
</table>

<h4>The framework holds across four pillars</h4>

<p>LPI, BCI, FCI, HCI all produce 1.7x-2.6x lifts at their thermometer targets. That's a strong validation that the pillar-by-pillar architecture works for the parts where (a) the target is well-defined and (b) the historical data window includes enough events to validate.</p>

<h4>Three failures and one open question</h4>

<ul>
<li><strong>CCI:</strong> aligned dataset starts 2007 — the v2 (Feb 2026) rebuild only goes back that far. Need to extend backward.</li>
<li><strong>TCI:</strong> net exports as target may be the wrong domain variable. Better: trade balance change, container rates, or dollar pass-through. Re-test.</li>
<li><strong>GCI_Gov:</strong> inverted result. When GCI_Gov z &gt; +1, term premium <em>falls</em> in the next 252d. This is counterintuitive — needs investigation. Possible: GCI_Gov is loading on stale variables (debt levels, deficits), and during periods when those are extreme the term premium has already moved and is mean-reverting.</li>
<li><strong>PCI:</strong> "core PCE YoY &ge; 3%" is true 42% of the time historically. Threshold target is too easy; the target should be "core PCE accelerating" or "core PCE in top decile" instead.</li>
</ul>

<!-- PHASE 4 -->
<h2 id="phase4">Phase 4 — Standalone Signals</h2>

<p>Master plan listed six priority standalone signals. Status:</p>

<table>
<thead><tr><th>Signal</th><th>Status</th><th>Findings</th></tr></thead>
<tbody>
<tr><td>CLG</td><td>Tested in Phase 2</td><td>Weak signal (1.07x lift). Circular formula vs HY target.</td></tr>
<tr><td>SBD</td><td>Tested in Phase 2</td><td>Weak signal (1.12x). Distribution warning is real but small effect.</td></tr>
<tr><td>SSD</td><td>Tested in Phase 2</td><td>Marginal (1.53x at extreme low side, small n).</td></tr>
<tr><td>Quits-to-Claims</td><td>Tested here</td><td>Mild signal (1.33x lift on HY widening at 63d). Not strong enough to publish.</td></tr>
<tr><td>Dealer Positioning vs Auction Tails</td><td>Skipped</td><td>Insufficient data in Lighthouse_Master.db. Needs ingestion before testable.</td></tr>
<tr><td>Breadth Thrust binary</td><td>Skipped</td><td>SPX_PCT_ABOVE_20D only goes back to Feb 2023. Need pre-2023 reconstruction.</td></tr>
</tbody>
</table>

<p>Net: of 6 priority standalones, 3 were testable (CLG, SBD, SSD, Quits-to-Claims) and all came back weak-to-marginal. The other 2 are blocked on data infrastructure.</p>

<!-- PHASE 7 -->
<h2 id="phase7">Phase 7 — Correlation Audit</h2>

<p>Pearson correlations across 16 indicators (MRI, MSI, SPI, LCI, CLG, SBD, SSD, plus 12 pillars) over 6,329 aligned daily observations from October 2000 to December 2025.</p>

<div class="callout">
  <div class="callout-label">Only one redundancy</div>
  <strong>MSI ↔ SBD = +0.84</strong>. Makes sense: SBD is <span class="code">z(Price_vs_200d) - z(%>50d_MA)</span>, which uses MSI's components. SBD is a derivative signal of MSI, not independent. Recommendation: do not present both publicly without acknowledging the relationship.
</div>

<p>Most pillar correlations are below 0.5. The framework is well-orthogonalized. Other notable correlations:</p>

<ul>
<li>MRI ↔ LPI -0.59 (LPI is a major MRI input — expected)</li>
<li>MRI ↔ FCI -0.49, BCI -0.47, TCI -0.47, LCI -0.45 (MRI summing its inputs — expected)</li>
<li>MSI ↔ SPI -0.56 (structure vs sentiment — expected mild inverse)</li>
<li>FCI ↔ LCI +0.48 (both financial-conditions composites)</li>
<li>HCI ↔ GCI_Gov -0.26 (housing weakens when fiscal pressure rises — interesting)</li>
</ul>

<p>No incremental information test was performed (Phase 7 task #2 from master plan); could be added.</p>

<!-- DECISIONS -->
<h2 id="decisions">Decisions & Open Questions</h2>

<h3>Decisions ready to ship</h3>
<ol>
<li><strong>Keep current MRI judgment weights.</strong> Optimization overfit. Master-plan adoption rule fires: not 5 of 6 invalidation criteria.</li>
<li><strong>Reframe MRI as a binary crisis filter</strong>, not a continuous regime conditioner. The +1.0 threshold has 3.15x lift on 63d big drawdowns; the +0.4 threshold has 2.01x.</li>
<li><strong>Update the regime multiplier table in <span class="code">CLAUDE_MASTER.md</span> Section 4 / TWO_BOOKS_FRAMEWORK.md</strong> to start compression at +0.4 instead of +1.0. Add a 4th regime level.</li>
<li><strong>Publish-grade findings:</strong> LPI labor-flow indicator (2.58x lift) and LCI funding-stress predictor (2.34x lift) are clean enough to anchor a Beam each.</li>
</ol>

<h3>Two-path forks (where I went both ways)</h3>
<ol>
<li><strong>Phase 2 indicator targets:</strong> Track A used forward SPX returns for everything. Track A v2 used domain-appropriate targets (HY widening for LCI/CLG). Track A v2 was the right call — LCI signal only emerges with the right target.</li>
<li><strong>MSI vs SBD redundancy:</strong> Could collapse SBD into MSI (since SBD is a derivative). Or keep both for narrative purposes (SBD has a clean 'distribution warning' story even if it doesn't add information). Kept both, flagged the redundancy.</li>
</ol>

<h3>Open questions for Bob</h3>
<ol>
<li>The +0.4 MRI compression threshold is more conservative than the v2.0 doc. Should we update the framework doc, run a back-test of the new vs old multiplier table, or just note it and ship the +1.0 threshold?</li>
<li>GCI_Gov inverted result — investigate before next phase, or accept that the term-premium target may not be the right domain variable?</li>
<li>CCI 2007+ data window — extend backward (rebuild from raw components), or accept the post-2007 limitation and document it?</li>
<li>Dealer positioning + breadth thrust signals: data infrastructure work needed before these can be tested. Worth queuing as a separate engineering project, or skip?</li>
</ol>

<!-- ISSUES -->
<h2 id="issues">Issues & Caveats</h2>

<h4>Methodological</h4>
<ol>
<li><strong>Year-by-year IC instability is universal.</strong> Even MRI with current weights flips IC sign in 12 of 26 years. The framework only "works" in pooled stats because crisis years dominate. This is a fundamental property of macro indicators built on slow-moving data, not a bug of these specific indicators.</li>
<li><strong>OOS slice (2023-06 to 2025-12) is anomalous.</strong> A bull market with elevated MRI readings — the sign of MRI&rarr;forward-returns inverted in this window. Tighter training windows didn't fix it.</li>
<li><strong>Threshold sweep n is small at extremes.</strong> The MRI &gt;= +1.1 bucket has only 24 observations. The 4.5x lift is real but n is too small to call high-confidence.</li>
</ol>

<h4>Data infrastructure</h4>
<ol>
<li><strong>SPX series in DB is <span class="code">SPX_Close</span></strong> (not SP500/GSPC/SPY). The script defaults didn't catch it. Fixed in <span class="code">mri_weight_optimization.py</span> for future runs.</li>
<li><strong>Pillar series end dates differ.</strong> CCI ends 2026-01-01, BCI ends 2026-04-21, etc. Aligned dataset truncates to the worst case (CCI Jan 1) — losing 4 months of recent data.</li>
<li><strong>Several modern series are short.</strong> SPX_PCT_ABOVE_* breadth series start 2023; IORB starts 2021; SOFR starts 2018. Backtests across these are constrained.</li>
<li><strong>HY OAS series</strong> (BAMLH0A0HYM2) loaded fine. Used for LCI/FCI/CLG validation.</li>
</ol>

<h4>Master plan deltas</h4>
<ol>
<li>Master plan referenced <span class="code">/Users/bob/LHM/Strategy/MRI_WEIGHT_OPTIMIZATION.md</span> as a finalized spec. File didn't exist on disk — only the script existed (in iCloud, never copied to LHM). Spec was reconstructed from script header.</li>
<li>Master plan Phase 0 was the CLI v8 rebuild. Resolved: the published article keeps weights proprietary, so the 4-component implementation in <span class="code">cli_final.py</span> is consistent. No drift to fix. Header note added pointing at strategy doc.</li>
<li>Master plan path <span class="code">Strategy/CLI_CRYPTO_LIQUIDITY_IMPULSE.md</span> was wrong. Actual: <span class="code">Strategy/md/CLI_CRYPTO_LIQUIDITY_IMPULSE.md</span>. Updated.</li>
</ol>

<!-- NEXT STEPS -->
<h2 id="nextsteps">Next Steps</h2>

<h4>Ready to ship as content</h4>
<ol>
<li><strong>Beam — "Why we kept the judgment weights for MRI"</strong> (Phase 1 transparency piece). The full SLSQP optimization, the OOS sign-flip, the adoption decision. ~750 words, reuses the run logs.</li>
<li><strong>Beam — "MRI as a crisis filter" </strong>(threshold sweep finding). Reframes the master signal: regime multiplier compresses based on threshold, not continuous score. Includes the new 4-regime table.</li>
<li><strong>Beam — "LCI predicts funding stress" </strong>(Phase 2 LCI finding). 2.34x lift on HY widening. Real signal.</li>
<li><strong>Beam — "Labor as the source code" </strong>(LPI 2.58x lift on UR rise). Strongest signal in the stack.</li>
<li><strong>Chartbook section</strong> — overlay all six "strong signal" indicators on their target series.</li>
</ol>

<h4>Internal work queued</h4>
<ol>
<li>Update <span class="code">TWO_BOOKS_FRAMEWORK.md</span> regime multiplier table to 4-regime cut at +0.4 / +1.0. Pending Bob decision.</li>
<li>Investigate GCI_Gov inversion. Re-test with different target (term premium acceleration, not delta).</li>
<li>Extend CCI backwards to pre-2007. Requires rebuilding from raw components.</li>
<li>Queue Dealer Positioning + Breadth Thrust as data infrastructure projects.</li>
<li>Add incremental-information test (Phase 7 task #2) — regress fwd returns on MRI + each standalone individually, check R² delta.</li>
</ol>

<h4>Files generated</h4>
<table>
<thead><tr><th>Output</th><th>Path</th></tr></thead>
<tbody>
<tr><td>MRI optimization JSON</td><td class="code">Outputs/mri_optimization/mri_optimization_results.json</td></tr>
<tr><td>MRI follow-ups JSON</td><td class="code">Outputs/mri_optimization/mri_followups_results.json</td></tr>
<tr><td>MRI threshold JSON</td><td class="code">Outputs/mri_optimization/mri_threshold_results.json</td></tr>
<tr><td>Phase 2 (forward returns)</td><td class="code">Outputs/mri_optimization/phase2_threshold_results.json</td></tr>
<tr><td>Phase 2 v2 (domain targets)</td><td class="code">Outputs/mri_optimization/phase2_threshold_v2_results.json</td></tr>
<tr><td>Phase 3+4 Tier B</td><td class="code">Outputs/mri_optimization/phase3_4_threshold_results.json</td></tr>
<tr><td>Phase 4+7 standalone+audit</td><td class="code">Outputs/mri_optimization/phase4_7_results.json</td></tr>
<tr><td>Phase 1 markdown summary</td><td class="code">Outputs/mri_optimization/PHASE_1_FINDINGS.md</td></tr>
<tr><td>Scripts</td><td class="code">Scripts/backtest/mri_*.py + phase2_*.py + phase3_4_*.py + phase4_7_*.py</td></tr>
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
    print(f"File size: {REPORT_PATH.stat().st_size / 1024:.1f} KB")


if __name__ == "__main__":
    build_report()
