#!/usr/bin/env python3
"""
Lighthouse Macro Risk Dashboard Generator (HTML)
=================================================
Generates a branded HTML dashboard summarizing the current risk assessment
from the ensemble model (probability + warning system + RMP).

Usage:
    python generate_dashboard_html.py

Output:
    Opens the dashboard in the default browser
"""

import sys
sys.path.insert(0, "/Users/bob/LHM")

import webbrowser
import tempfile
import os
from datetime import datetime

from lighthouse_quant.models.warning_system import WarningSystem, WarningLevel
from lighthouse_quant.models.risk_ensemble import RiskEnsemble


def generate_html_dashboard():
    """Generate HTML dashboard and open in browser."""
    # Get data
    ws = WarningSystem()
    warning = ws.evaluate()
    ensemble = RiskEnsemble()
    result = ensemble.evaluate()
    rmp = warning.rmp_assessment

    # Regime colors
    regime_colors = {
        "EXPANSION": "#00BB89",
        "LATE_CYCLE": "#FF6723",
        "HOLLOW_RALLY": "#FF6723",
        "PRE_CRISIS": "#FF2389",
        "CRISIS": "#892323",
    }
    regime_color = regime_colors.get(result.regime.name, "#FF2389")

    warning_colors = {
        "GREEN": "#00BB89",
        "YELLOW": "#FFD700",
        "AMBER": "#FF6723",
        "RED": "#FF2389",
    }
    warning_color = warning_colors.get(result.warning_level.name, "#FF2389")

    # Build HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lighthouse Macro Risk Dashboard</title>
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@600;700&family=Inter:wght@400;500;600&family=Source+Code+Pro:wght@400;500&display=swap" rel="stylesheet">
    <style>
        :root {{
            --ocean: #2389BB;
            --dusk: #FF6723;
            --sky: #00D4FF;
            --venus: #FF2389;
            --sea: #00BB89;
            --doldrums: #898989;
            --starboard: #238923;
            --port: #892323;
            --bg-dark: #0a1628;
            --bg-card: #0f2140;
            --text-primary: #ffffff;
            --text-secondary: #a0aec0;
            --border: #1e3a5f;
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Inter', sans-serif;
            background: var(--bg-dark);
            color: var(--text-primary);
            min-height: 100vh;
            padding: 2rem;
        }}

        .dashboard {{
            max-width: 1200px;
            margin: 0 auto;
        }}

        .header {{
            text-align: center;
            margin-bottom: 2rem;
            padding-bottom: 1.5rem;
            border-bottom: 2px solid var(--ocean);
        }}

        .header h1 {{
            font-family: 'Montserrat', sans-serif;
            font-size: 2.5rem;
            font-weight: 700;
            color: var(--ocean);
            letter-spacing: 0.1em;
            margin-bottom: 0.5rem;
        }}

        .header .subtitle {{
            font-size: 1.1rem;
            color: var(--text-secondary);
            margin-bottom: 0.5rem;
        }}

        .header .date {{
            font-family: 'Source Code Pro', monospace;
            color: var(--sky);
            font-size: 0.9rem;
        }}

        .regime-banner {{
            background: linear-gradient(135deg, {regime_color}22, {regime_color}11);
            border: 2px solid {regime_color};
            border-radius: 12px;
            padding: 1.5rem;
            text-align: center;
            margin-bottom: 2rem;
        }}

        .regime-banner h2 {{
            font-family: 'Montserrat', sans-serif;
            font-size: 2rem;
            color: {regime_color};
            margin-bottom: 1rem;
        }}

        .regime-stats {{
            display: flex;
            justify-content: center;
            gap: 3rem;
            flex-wrap: wrap;
        }}

        .regime-stat {{
            text-align: center;
        }}

        .regime-stat .label {{
            font-size: 0.75rem;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.1em;
            margin-bottom: 0.25rem;
        }}

        .regime-stat .value {{
            font-family: 'Source Code Pro', monospace;
            font-size: 1.1rem;
            font-weight: 600;
        }}

        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }}

        .card {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 1.5rem;
        }}

        .card-header {{
            font-family: 'Montserrat', sans-serif;
            font-size: 0.85rem;
            font-weight: 600;
            color: var(--ocean);
            text-transform: uppercase;
            letter-spacing: 0.1em;
            margin-bottom: 1rem;
            padding-bottom: 0.75rem;
            border-bottom: 1px solid var(--border);
        }}

        .probability-breakdown {{
            margin-bottom: 1rem;
        }}

        .prob-row {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.5rem 0;
            font-family: 'Source Code Pro', monospace;
        }}

        .prob-row.base {{
            color: var(--text-secondary);
        }}

        .prob-row.premium {{
            color: var(--dusk);
        }}

        .prob-row.total {{
            font-size: 1.25rem;
            font-weight: 600;
            color: var(--venus);
            border-top: 1px dashed var(--border);
            padding-top: 0.75rem;
            margin-top: 0.5rem;
        }}

        .prob-bar {{
            height: 8px;
            background: var(--border);
            border-radius: 4px;
            overflow: hidden;
            margin-top: 1rem;
        }}

        .prob-bar-fill {{
            height: 100%;
            border-radius: 4px;
            transition: width 0.5s ease;
        }}

        .trigger-list {{
            list-style: none;
        }}

        .trigger-item {{
            padding: 0.75rem;
            margin-bottom: 0.5rem;
            background: rgba(255, 35, 137, 0.1);
            border-left: 3px solid var(--venus);
            border-radius: 0 8px 8px 0;
        }}

        .trigger-item .flag {{
            font-family: 'Source Code Pro', monospace;
            font-weight: 600;
            color: var(--venus);
            font-size: 0.85rem;
        }}

        .trigger-item .desc {{
            font-size: 0.8rem;
            color: var(--text-secondary);
            margin-top: 0.25rem;
        }}

        .rmp-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 1rem;
        }}

        .rmp-item {{
            background: rgba(0, 137, 209, 0.1);
            padding: 0.75rem;
            border-radius: 8px;
        }}

        .rmp-item .label {{
            font-size: 0.7rem;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}

        .rmp-item .value {{
            font-family: 'Source Code Pro', monospace;
            font-size: 1.1rem;
            font-weight: 600;
            color: var(--sky);
        }}

        .rmp-runway {{
            grid-column: span 2;
            text-align: center;
            background: rgba(0, 187, 153, 0.15);
            border: 1px solid var(--sea);
        }}

        .rmp-runway .value {{
            font-size: 1.5rem;
            color: var(--sea);
        }}

        .thesis-box {{
            background: linear-gradient(135deg, rgba(0, 137, 209, 0.1), rgba(255, 103, 35, 0.1));
            border: 1px solid var(--ocean);
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 2rem;
        }}

        .thesis-box h3 {{
            font-family: 'Montserrat', sans-serif;
            color: var(--ocean);
            margin-bottom: 1rem;
        }}

        .thesis-box p {{
            color: var(--text-secondary);
            line-height: 1.6;
            margin-bottom: 0.75rem;
        }}

        .thesis-box p strong {{
            color: var(--text-primary);
        }}

        .two-col {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }}

        .action-list {{
            list-style: none;
        }}

        .action-item {{
            padding: 0.5rem 0;
            padding-left: 1.5rem;
            position: relative;
            color: var(--text-secondary);
        }}

        .action-item::before {{
            content: '';
            position: absolute;
            left: 0;
            top: 0.75rem;
            width: 8px;
            height: 8px;
            border-radius: 50%;
        }}

        .action-item.dont::before {{
            background: var(--venus);
        }}

        .action-item.do::before {{
            background: var(--sea);
        }}

        .invalidation-list {{
            list-style: none;
        }}

        .invalidation-item {{
            padding: 0.5rem 0;
            padding-left: 1.5rem;
            position: relative;
            color: var(--text-secondary);
            font-size: 0.9rem;
        }}

        .invalidation-item::before {{
            content: '→';
            position: absolute;
            left: 0;
            color: var(--sky);
        }}

        .footer {{
            text-align: center;
            padding-top: 2rem;
            border-top: 2px solid var(--ocean);
        }}

        .footer .tagline {{
            font-family: 'Montserrat', sans-serif;
            font-size: 1rem;
            color: var(--ocean);
            letter-spacing: 0.2em;
        }}

        .footer .timestamp {{
            font-family: 'Source Code Pro', monospace;
            font-size: 0.75rem;
            color: var(--text-secondary);
            margin-top: 0.5rem;
        }}

        .watermark {{
            position: fixed;
            bottom: 1rem;
            right: 1rem;
            font-family: 'Montserrat', sans-serif;
            font-size: 0.7rem;
            color: rgba(0, 137, 209, 0.3);
            letter-spacing: 0.1em;
        }}
    </style>
</head>
<body>
    <div class="dashboard">
        <header class="header">
            <h1>LIGHTHOUSE MACRO</h1>
            <div class="subtitle">Risk Assessment Dashboard</div>
            <div class="date">As of {result.date}</div>
        </header>

        <div class="regime-banner">
            <h2>🔴 REGIME: {result.regime.name.replace('_', ' ')} 🔴</h2>
            <div class="regime-stats">
                <div class="regime-stat">
                    <div class="label">Warning Level</div>
                    <div class="value" style="color: {warning_color}">{result.warning_level.name}</div>
                </div>
                <div class="regime-stat">
                    <div class="label">Model Agreement</div>
                    <div class="value" style="color: var(--dusk)">{result.model_agreement}</div>
                </div>
                <div class="regime-stat">
                    <div class="label">Confidence</div>
                    <div class="value">{result.confidence}</div>
                </div>
                <div class="regime-stat">
                    <div class="label">Allocation</div>
                    <div class="value" style="color: var(--venus)">{result.allocation_multiplier:.2f}x</div>
                </div>
            </div>
        </div>

        <div class="grid">
            <div class="card">
                <div class="card-header">Probability Decomposition</div>
                <div class="probability-breakdown">
                    <div class="prob-row base">
                        <span>Base Recession Probability (12-mo)</span>
                        <span>{result.base_probability:.1%}</span>
                    </div>
                    <div class="prob-row premium">
                        <span>+ Discontinuity Premium</span>
                        <span>+{result.discontinuity_premium:.1%}</span>
                    </div>
                    <div class="prob-row total">
                        <span>ADJUSTED PROBABILITY</span>
                        <span>{result.adjusted_probability:.1%}</span>
                    </div>
                </div>
                <div class="prob-bar">
                    <div class="prob-bar-fill" style="width: {result.adjusted_probability * 100}%; background: linear-gradient(90deg, var(--dusk), var(--venus))"></div>
                </div>
            </div>

            <div class="card">
                <div class="card-header">Critical Warning Triggers</div>
                <ul class="trigger-list">
                    {"".join(f'''
                    <li class="trigger-item">
                        <div class="flag">🚨 {trigger.split(":")[0].strip()}</div>
                        <div class="desc">{trigger.split(":", 1)[1].strip() if ":" in trigger else ""}</div>
                    </li>
                    ''' for trigger in result.warning_triggers[:4])}
                </ul>
            </div>
        </div>

        <div class="card" style="margin-bottom: 2rem">
            <div class="card-header">Fed Reserve Management (RMP) Assessment</div>
            <div class="rmp-grid">
                <div class="rmp-item">
                    <div class="label">Current Reserves</div>
                    <div class="value">${rmp.reserves_current:,.0f}B</div>
                </div>
                <div class="rmp-item">
                    <div class="label">LCLOR Threshold</div>
                    <div class="value">${rmp.reserves_lclor:,.0f}B</div>
                </div>
                <div class="rmp-item">
                    <div class="label">Organic Drain</div>
                    <div class="value">${rmp.drain_rate_monthly:.0f}B/mo</div>
                </div>
                <div class="rmp-item">
                    <div class="label">RMP Offset</div>
                    <div class="value">-${rmp.rmp_estimated_pace:.0f}B/mo</div>
                </div>
                <div class="rmp-item">
                    <div class="label">Net Drain Rate</div>
                    <div class="value">${rmp.net_drain_rate:.1f}B/mo</div>
                </div>
                <div class="rmp-item">
                    <div class="label">Risk Modifier</div>
                    <div class="value" style="color: var(--sea)">{rmp.risk_modifier:+.0%}</div>
                </div>
                <div class="rmp-item rmp-runway">
                    <div class="label">Runway to LCLOR</div>
                    <div class="value">{rmp.months_to_lclor:.0f} months</div>
                </div>
            </div>
        </div>

        <div class="thesis-box">
            <h3>The Hollow Rally Thesis</h3>
            <p>Base probability (<strong>{result.base_probability:.1%}</strong>) reflects gradual deterioration in macro fundamentals. But this undersells the true risk.</p>
            <p><strong>Buffers are exhausted.</strong> RRP depleted below $100B. Reserves within $80B of LCLOR. The shock absorbers that smoothed previous corrections are gone.</p>
            <p><strong>Credit is mispricing labor fragility.</strong> The Credit-Labor Gap sits below -1.0, meaning HY spreads are tight relative to where labor dynamics suggest they should be.</p>
            <p>The ensemble model adds a <strong>+{result.discontinuity_premium:.0%} discontinuity premium</strong> to capture this hidden fragility. Liquidity still exists. But it no longer absorbs risk. It transmits it.</p>
        </div>

        <div class="two-col">
            <div class="card">
                <div class="card-header">Positioning Guidance</div>
                <ul class="action-list">
                    <li class="action-item dont">Max defensive: {result.allocation_multiplier:.2f}x allocation multiplier</li>
                    <li class="action-item dont">No new longs until buffer rebuilds</li>
                    <li class="action-item do">Cash is an active position</li>
                    <li class="action-item do">Daily monitoring of funding stress indicators</li>
                </ul>
            </div>

            <div class="card">
                <div class="card-header">Invalidation Conditions</div>
                <ul class="invalidation-list">
                    {"".join(f'<li class="invalidation-item">{cond}</li>' for cond in result.invalidation_conditions[:4])}
                </ul>
            </div>
        </div>

        <footer class="footer">
            <div class="tagline">MACRO, ILLUMINATED.</div>
            <div class="timestamp">Generated {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>
        </footer>
    </div>

    <div class="watermark">LIGHTHOUSE MACRO</div>
</body>
</html>
"""

    # Write to temp file and open
    output_path = "/Users/bob/LHM/Outputs/risk_dashboard.html"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, 'w') as f:
        f.write(html)

    print(f"Dashboard saved to: {output_path}")
    webbrowser.open(f"file://{output_path}")

    return output_path


if __name__ == "__main__":
    generate_html_dashboard()
