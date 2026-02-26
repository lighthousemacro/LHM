#!/usr/bin/env python3
"""
LIGHTHOUSE MACRO - MORNING BRIEF (v2.0)
========================================
Charts-first morning briefing driven by the FRED release calendar.
Picks charts based on what released yesterday, today, and tomorrow,
with day-of-week rotation for quiet days.

Outputs:
    1. HTML file: ~/Desktop/LHM_Morning_Brief.html
    2. macOS notification with headline summary
    3. Persistent log: /Users/bob/LHM/logs/morning_brief.log

Usage:
    python morning_brief.py              # Full brief
    python morning_brief.py --no-notify  # Skip macOS notification
    python morning_brief.py --stdout     # Print to stdout instead of file
    python morning_brief.py --no-charts  # Skip chart generation (faster)
"""

import sqlite3
import subprocess
import sys
import os
from datetime import datetime
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from compute_indices import STATUS_THRESHOLDS, get_status

DB_PATH = Path("/Users/bob/LHM/Data/databases/Lighthouse_Master.db")
OUTPUT_PATH = Path.home() / "Desktop" / "LHM_Morning_Brief.html"
LOG_PATH = Path("/Users/bob/LHM/logs/morning_brief.log")

# Thresholds that demand attention when crossed
ALERT_THRESHOLDS = {
    "MRI": [(0.50, "RECESSION"), (0.25, "PRE-RECESSION"), (-0.20, "EARLY EXPANSION")],
    "LFI": [(1.0, "HIGH"), (0.5, "ELEVATED")],
    "LCI": [(-1.0, "SCARCE"), (-0.5, "TIGHT")],
    "CLG": [(-1.0, "MISPRICED")],
    "MSI": [(-1.0, "WEAK"), (-0.5, "TRANSITIONAL"), (0.5, "BULLISH")],
    "SPI": [(1.5, "EXTREME FEAR"), (1.0, "FEARFUL"), (-1.0, "EUPHORIC")],
    "SBD": [(1.0, "DISTRIBUTION"), (1.5, "EXTREME DISTRIBUTION")],
    "SSD": [(1.5, "CAPITULATION LOW"), (-1.5, "BLOW-OFF TOP RISK")],
    "REC_PROB": [(0.40, "ELEVATED"), (0.70, "HIGH RISK")],
    "SLI": [(-0.5, "CONTRACTING"), (-1.0, "SEVERELY CONTRACTING")],
}


# ============================================================
# DATA FUNCTIONS
# ============================================================

def get_latest_indices(conn: sqlite3.Connection) -> dict:
    """Get the most recent value for each index."""
    query = """
        SELECT li.index_id, li.value, li.status, li.date
        FROM lighthouse_indices li
        INNER JOIN (
            SELECT index_id, MAX(date) as max_date
            FROM lighthouse_indices
            GROUP BY index_id
        ) latest ON li.index_id = latest.index_id AND li.date = latest.max_date
        ORDER BY li.index_id
    """
    cursor = conn.execute(query)
    results = {}
    for row in cursor:
        results[row[0]] = {
            "value": row[1],
            "status": row[2],
            "date": row[3],
        }
    return results


def get_prior_indices(conn: sqlite3.Connection, current_dates: dict) -> dict:
    """Get the prior day's value for each index to compute changes."""
    prior = {}
    for index_id, info in current_dates.items():
        query = """
            SELECT value, status, date
            FROM lighthouse_indices
            WHERE index_id = ? AND date < ?
            ORDER BY date DESC
            LIMIT 1
        """
        cursor = conn.execute(query, (index_id, info["date"]))
        row = cursor.fetchone()
        if row:
            prior[index_id] = {
                "value": row[0],
                "status": row[1],
                "date": row[2],
            }
    return prior


def detect_regime_changes(current: dict, prior: dict) -> list:
    """Detect when an index has crossed into a new regime."""
    changes = []
    for index_id, curr in current.items():
        prev = prior.get(index_id)
        if prev and curr["status"] != prev["status"]:
            changes.append({
                "index": index_id,
                "from_status": prev["status"],
                "to_status": curr["status"],
                "from_value": prev["value"],
                "to_value": curr["value"],
                "date": curr["date"],
            })
    return changes


def detect_threshold_alerts(current: dict) -> list:
    """Flag indices at attention-worthy levels."""
    alerts = []
    for index_id, thresholds in ALERT_THRESHOLDS.items():
        if index_id not in current:
            continue
        val = current[index_id]["value"]
        for threshold, label in thresholds:
            if (threshold > 0 and val >= threshold) or (threshold < 0 and val <= threshold):
                alerts.append({
                    "index": index_id,
                    "value": val,
                    "threshold": threshold,
                    "label": label,
                    "status": current[index_id]["status"],
                })
                break
    return alerts


# ============================================================
# STATUS COLOR
# ============================================================

def _status_color(status: str) -> str:
    """Map a status string to a CSS color."""
    if not status:
        return "#898989"
    s = status.upper()
    if any(w in s for w in ["CRISIS", "SCARCE", "HIGH RISK", "WEAK", "TRADE CRISIS",
                            "SEVERELY", "BLOW-OFF", "PORT", "RECESSION"]):
        return "#FF2389"  # Venus
    if any(w in s for w in ["ELEVATED", "PRE-RECESSION", "CAUTIOUS", "LATE",
                            "TIGHT", "STRESSED", "HEADWIND", "FEARFUL",
                            "MISPRICED", "BEARISH", "RED", "PRE_CRISIS"]):
        return "#FF6723"  # Dusk
    if any(w in s for w in ["NEUTRAL", "MID-CYCLE", "BALANCED", "NORMAL",
                            "FROZEN", "SLOWING", "STAGE"]):
        return "#898989"  # Doldrums
    if any(w in s for w in ["EXPANSION", "ON TARGET", "TREND", "LOOSE",
                            "LOW RISK", "BULLISH", "GREEN", "ACCUMULATION",
                            "CAPITAL", "RAPID"]):
        return "#00BB89"  # Sea
    return "#898989"


# ============================================================
# HTML BUILDER
# ============================================================

def build_brief(conn: sqlite3.Connection, include_charts: bool = True) -> str:
    """Build the full morning brief as self-contained HTML."""
    now = datetime.now()
    current = get_latest_indices(conn)
    prior = get_prior_indices(conn, current)
    regime_changes = detect_regime_changes(current, prior)
    alerts = detect_threshold_alerts(current)

    # Fetch release calendar context and select charts
    calendar_ctx = {"yesterday": [], "today": [], "upcoming": []}
    chart_specs = []
    release_headlines = []
    try:
        from release_chart_selector import fetch_calendar_context, select_charts
        calendar_ctx = fetch_calendar_context()
        chart_specs, release_headlines = select_charts(calendar_ctx)
        print(f"  Release context: {len(release_headlines)} headlines, {len(chart_specs)} charts selected")
    except Exception as e:
        print(f"  WARNING: Release chart selector failed: {e}")

    # Generate charts
    chart_data = []
    if include_charts and chart_specs:
        try:
            from brief_charts import generate_selected_charts
            chart_data = generate_selected_charts(conn, chart_specs)
            print(f"  Generated {len(chart_data)} charts")
        except Exception as e:
            print(f"  WARNING: Chart generation failed: {e}")

    # Hero card values
    mri_val = current.get("MRI", {}).get("value", 0)
    mri_status = current.get("MRI", {}).get("status", "N/A") or "N/A"
    rec_val = current.get("REC_PROB", {}).get("value", 0)
    rec_status = current.get("REC_PROB", {}).get("status", "N/A") or "N/A"
    warn_val = current.get("WARNING_LEVEL", {}).get("value", 0)
    warn_status = current.get("WARNING_LEVEL", {}).get("status", "N/A") or "N/A"
    alloc_val = current.get("ALLOC_MULTIPLIER", {}).get("value", 0)
    alloc_status = current.get("ALLOC_MULTIPLIER", {}).get("status", "N/A") or "N/A"

    # Context banner (what drove chart selection)
    context_html = ""
    if release_headlines:
        tags = " ".join(
            f'<span class="ctx-tag">{h}</span>' for h in release_headlines[:6]
        )
        context_html = f"""
        <div class="context-banner">
            <span class="ctx-label">RELEASE CONTEXT</span>
            {tags}
        </div>"""

    # Alerts banner (regime changes + threshold alerts)
    _ALERT_NAMES = {
        "MRI": "Macro Risk", "LPI": "Labor Pressure", "LFI": "Labor Fragility",
        "PCI": "Price Conditions", "GCI": "Growth", "HCI": "Housing",
        "CCI": "Consumer", "BCI": "Business", "TCI": "Trade",
        "GCI_Gov": "Government", "FCI": "Financial", "LCI": "Liquidity Cushion",
        "CLG": "Credit-Labor Gap", "MSI": "Market Structure",
        "SBD": "Breadth Divergence", "SPI": "Sentiment", "SSD": "Sent-Structure Div",
        "SLI": "Stablecoin Liquidity", "REC_PROB": "Recession Prob",
        "ENSEMBLE_RISK": "Ensemble Risk", "WARNING_LEVEL": "Warning Level",
        "ALLOC_MULTIPLIER": "Allocation", "CTI": "Trade Conditions",
    }

    alert_items = []
    for rc in regime_changes[:4]:
        name = _ALERT_NAMES.get(rc["index"], rc["index"])
        alert_items.append(
            f'<span class="alert-tag regime">{name}: '
            f'{rc["from_status"]} &#8594; {rc["to_status"]}</span>'
        )
    for a in alerts[:4]:
        name = _ALERT_NAMES.get(a["index"], a["index"])
        alert_items.append(
            f'<span class="alert-tag threshold">{name}: '
            f'{a["value"]:+.2f} [{a["label"]}]</span>'
        )
    alerts_html = ""
    if alert_items:
        alerts_html = f"""
        <div class="alerts-banner">
            <span class="ctx-label">ALERTS</span>
            {"".join(alert_items)}
        </div>"""

    # Charts HTML (grouped by context)
    charts_html = ""
    if chart_data:
        # Group charts by context label
        groups = {}
        for c in chart_data:
            ctx = c.get("context", "")
            groups.setdefault(ctx, []).append(c)

        sections = []
        for ctx_label, charts in groups.items():
            items = []
            for c in charts:
                if c.get("base64"):
                    items.append(
                        f'<div class="chart-card">'
                        f'<img src="data:image/png;base64,{c["base64"]}" alt="{c["title"]}" />'
                        f'</div>'
                    )
            if items:
                label_html = ""
                if ctx_label:
                    label_html = f'<div class="chart-group-label">{ctx_label}</div>'
                sections.append(
                    f'<div class="chart-group">'
                    f'{label_html}'
                    f'<div class="chart-grid">{"".join(items)}</div>'
                    f'</div>'
                )
        charts_html = "\n".join(sections)

    # Calendar HTML (next 3 days only, key releases)
    calendar_html = ""
    all_releases = []
    for time_label, releases in [("Today", calendar_ctx.get("today", [])),
                                  ("Upcoming", calendar_ctx.get("upcoming", []))]:
        for r in releases:
            all_releases.append(r)

    if all_releases:
        cal_items = []
        for r in all_releases[:12]:
            try:
                d = datetime.strptime(r["date"], "%Y-%m-%d")
                day_str = d.strftime("%a %b %d")
            except (ValueError, TypeError):
                day_str = r["date"]
            cal_items.append(
                f'<div class="cal-item">'
                f'<span class="cal-date">{day_str}</span>'
                f'<span class="cal-name">{r["name"]}</span>'
                f'</div>'
            )
        calendar_html = f"""
        <div class="section">
            <h2>Upcoming Releases</h2>
            {"".join(cal_items)}
        </div>"""

    # Assemble full HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LHM Morning Brief - {now.strftime('%b %d, %Y')}</title>
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@600;700&family=Inter:wght@400;500;600&family=Source+Code+Pro:wght@400;500&display=swap" rel="stylesheet">
    <style>
        :root {{
            --ocean: #2389BB;
            --dusk: #FF6723;
            --sky: #00BBFF;
            --venus: #FF2389;
            --sea: #00BB89;
            --doldrums: #898989;
            --starboard: #238923;
            --port: #892323;
            --fog: #D1D1D1;
            --bg: #ffffff;
            --card: #f9fafb;
            --text: #1a1a1a;
            --muted: #555555;
            --border: #e5e7eb;
        }}

        * {{ margin: 0; padding: 0; box-sizing: border-box; }}

        body {{
            font-family: 'Inter', -apple-system, sans-serif;
            background: var(--bg);
            color: var(--text);
            min-height: 100vh;
            padding: 0;
        }}

        .wrapper {{
            max-width: 1100px;
            margin: 0 auto;
            padding: 1.5rem;
        }}

        /* ---- ACCENT BAR ---- */
        .accent-bar {{
            height: 4px;
            background: linear-gradient(90deg, var(--ocean) 66%, var(--dusk) 66%);
            margin-bottom: 1.5rem;
        }}

        /* ---- HEADER ---- */
        .header {{
            text-align: center;
            padding: 1rem 0;
            border-bottom: 2px solid var(--ocean);
            margin-bottom: 1.2rem;
        }}
        .header-brand {{
            font-family: 'Montserrat', sans-serif;
            font-size: 1rem;
            font-weight: 700;
            letter-spacing: 3px;
            color: var(--ocean);
            margin-bottom: 0.2rem;
        }}
        .header-title {{
            font-family: 'Montserrat', sans-serif;
            font-size: 1.5rem;
            font-weight: 600;
            color: var(--text);
            margin-bottom: 0.2rem;
        }}
        .header-meta {{
            font-size: 0.8rem;
            color: var(--muted);
            font-family: 'Source Code Pro', monospace;
        }}

        /* ---- CONTEXT BANNER ---- */
        .context-banner, .alerts-banner {{
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 0.5rem;
            padding: 0.8rem 1rem;
            margin-bottom: 1rem;
            border-radius: 6px;
        }}
        .context-banner {{
            background: #f0f7fb;
            border: 1px solid #c8e2f0;
        }}
        .alerts-banner {{
            background: #fef7f0;
            border: 1px solid #f5d6b8;
        }}
        .ctx-label {{
            font-family: 'Montserrat', sans-serif;
            font-size: 0.65rem;
            font-weight: 700;
            letter-spacing: 1.5px;
            color: var(--ocean);
            text-transform: uppercase;
        }}
        .alerts-banner .ctx-label {{
            color: var(--dusk);
        }}
        .ctx-tag {{
            font-size: 0.78rem;
            font-weight: 500;
            color: var(--ocean);
            background: rgba(35, 137, 187, 0.08);
            padding: 0.2rem 0.5rem;
            border-radius: 4px;
        }}
        .alert-tag {{
            font-size: 0.75rem;
            font-weight: 500;
            padding: 0.2rem 0.5rem;
            border-radius: 4px;
            font-family: 'Source Code Pro', monospace;
        }}
        .alert-tag.regime {{
            color: var(--dusk);
            background: rgba(255, 103, 35, 0.08);
        }}
        .alert-tag.threshold {{
            color: var(--venus);
            background: rgba(255, 35, 137, 0.08);
        }}

        /* ---- HERO CARDS ---- */
        .hero-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 1rem;
            margin-bottom: 1.5rem;
        }}
        .hero-card {{
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 1rem;
            text-align: center;
        }}
        .hero-label {{
            font-size: 0.7rem;
            color: var(--muted);
            text-transform: uppercase;
            letter-spacing: 1.5px;
            margin-bottom: 0.4rem;
        }}
        .hero-value {{
            font-family: 'Source Code Pro', monospace;
            font-size: 1.8rem;
            font-weight: 700;
            margin-bottom: 0.2rem;
        }}
        .hero-status {{
            font-size: 0.75rem;
            font-weight: 600;
            letter-spacing: 0.5px;
            margin-bottom: 0.3rem;
        }}
        .hero-desc {{
            font-size: 0.65rem;
            color: var(--muted);
            line-height: 1.3;
            margin-top: 0.15rem;
        }}

        /* ---- CHART GROUPS ---- */
        .chart-group {{
            margin-bottom: 1.5rem;
        }}
        .chart-group-label {{
            font-family: 'Montserrat', sans-serif;
            font-size: 0.8rem;
            font-weight: 700;
            color: var(--ocean);
            text-transform: uppercase;
            letter-spacing: 1.5px;
            margin-bottom: 0.6rem;
            padding-bottom: 0.3rem;
            border-bottom: 1px solid var(--border);
        }}
        .chart-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 0.8rem;
        }}
        .chart-card {{
            border: 2px solid var(--ocean);
            border-radius: 6px;
            overflow: hidden;
        }}
        .chart-card img {{
            width: 100%;
            height: auto;
            display: block;
        }}

        /* ---- SECTIONS ---- */
        .section {{
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 1.2rem;
            margin-bottom: 1rem;
        }}
        .section h2 {{
            font-family: 'Montserrat', sans-serif;
            font-size: 0.85rem;
            font-weight: 700;
            color: var(--ocean);
            text-transform: uppercase;
            letter-spacing: 1.5px;
            margin-bottom: 0.8rem;
            padding-bottom: 0.4rem;
            border-bottom: 1px solid var(--border);
        }}

        /* ---- CALENDAR ---- */
        .cal-item {{
            display: flex;
            gap: 1rem;
            padding: 0.35rem 0;
            font-size: 0.82rem;
            border-bottom: 1px solid var(--border);
        }}
        .cal-item:last-child {{ border-bottom: none; }}
        .cal-date {{
            font-family: 'Source Code Pro', monospace;
            color: var(--ocean);
            font-weight: 600;
            min-width: 90px;
        }}
        .cal-name {{
            color: var(--text);
        }}

        /* ---- FOOTER ---- */
        .footer {{
            text-align: center;
            padding: 1.5rem 0 1rem;
            font-size: 0.75rem;
            color: var(--muted);
        }}
        .footer-tagline {{
            font-family: 'Montserrat', sans-serif;
            font-weight: 700;
            letter-spacing: 2px;
            color: var(--ocean);
            font-size: 0.8rem;
            margin-bottom: 0.3rem;
        }}

        /* ---- RESPONSIVE ---- */
        @media (max-width: 768px) {{
            .hero-grid {{ grid-template-columns: repeat(2, 1fr); }}
            .chart-grid {{ grid-template-columns: 1fr; }}
            .wrapper {{ padding: 0.8rem; }}
        }}
    </style>
</head>
<body>
<div class="wrapper">

    <div class="accent-bar"></div>

    <div class="header">
        <div class="header-brand">LIGHTHOUSE MACRO</div>
        <div class="header-title">Morning Brief &bull; {now.strftime('%A, %B %d, %Y')}</div>
        <div class="header-meta">{now.strftime('%H:%M ET')}</div>
    </div>

    {context_html}
    {alerts_html}

    <!-- Hero Cards -->
    <div class="hero-grid">
        <div class="hero-card">
            <div class="hero-label">Macro Risk Index</div>
            <div class="hero-value" style="color:{_status_color(mri_status)}">{mri_val:+.3f}</div>
            <div class="hero-status" style="color:{_status_color(mri_status)}">{mri_status}</div>
            <div class="hero-desc">12-pillar composite. Positive = rising risk.</div>
        </div>
        <div class="hero-card">
            <div class="hero-label">Recession Probability</div>
            <div class="hero-value" style="color:{_status_color(rec_status)}">{rec_val:.1%}</div>
            <div class="hero-status" style="color:{_status_color(rec_status)}">{rec_status}</div>
            <div class="hero-desc">6-12 month forward probability.</div>
        </div>
        <div class="hero-card">
            <div class="hero-label">Warning Level</div>
            <div class="hero-value" style="color:{_status_color(warn_status)}">{warn_val:.0f}</div>
            <div class="hero-status" style="color:{_status_color(warn_status)}">{warn_status}</div>
            <div class="hero-desc">Pillar indices in elevated or worse.</div>
        </div>
        <div class="hero-card">
            <div class="hero-label">Allocation Multiplier</div>
            <div class="hero-value" style="color:{_status_color(alloc_status)}">{alloc_val:.2f}x</div>
            <div class="hero-status" style="color:{_status_color(alloc_status)}">{alloc_status}</div>
            <div class="hero-desc">Regime-driven equity sizing. 1.0x = neutral.</div>
        </div>
    </div>

    {charts_html}
    {calendar_html}

    <div class="footer">
        <div class="footer-tagline">MACRO, ILLUMINATED.</div>
        Lighthouse Macro &bull; {now.strftime('%Y-%m-%d %H:%M ET')}
    </div>

</div>
</body>
</html>"""

    return html


# ============================================================
# NOTIFICATION + LOGGING
# ============================================================

def build_notification_summary(conn: sqlite3.Connection) -> str:
    """Build a short summary for macOS notification."""
    current = get_latest_indices(conn)
    prior = get_prior_indices(conn, current)
    regime_changes = detect_regime_changes(current, prior)

    parts = []
    if "MRI" in current:
        parts.append(f"MRI: {current['MRI']['value']:.2f} [{current['MRI']['status']}]")
    if "MSI" in current:
        parts.append(f"MSI: {current['MSI']['value']:.2f} [{current['MSI']['status']}]")
    if regime_changes:
        for rc in regime_changes[:2]:
            parts.append(f"{rc['index']}: {rc['from_status']}->{rc['to_status']}")

    return " | ".join(parts) if parts else "Pipeline complete. No alerts."


def send_notification(title: str, message: str):
    """Send a macOS notification via terminal-notifier or osascript."""
    try:
        subprocess.run(
            ["terminal-notifier",
             "-title", title,
             "-message", message,
             "-group", "lhm-morning-brief",
             "-sound", "default"],
            capture_output=True, timeout=5
        )
        return
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    try:
        escaped_msg = message.replace('"', '\\"').replace("'", "\\'")
        escaped_title = title.replace('"', '\\"')
        subprocess.run(
            ["osascript", "-e",
             f'display notification "{escaped_msg}" with title "{escaped_title}"'],
            capture_output=True, timeout=5
        )
    except (subprocess.TimeoutExpired, Exception):
        pass


def log_brief(brief: str):
    """Append a timestamped entry to the morning brief log."""
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_PATH, "a") as f:
        f.write(f"\n{'='*70}\n")
        f.write(f"MORNING BRIEF - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"{'='*70}\n")
        f.write(f"HTML dashboard generated at {OUTPUT_PATH}\n")


# ============================================================
# CLI
# ============================================================

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Lighthouse Macro Morning Brief")
    parser.add_argument("--no-notify", action="store_true", help="Skip macOS notification")
    parser.add_argument("--stdout", action="store_true", help="Print to stdout instead of file")
    parser.add_argument("--no-charts", action="store_true", help="Skip chart generation (faster)")
    args = parser.parse_args()

    conn = sqlite3.connect(DB_PATH, timeout=30)

    brief = build_brief(conn, include_charts=not args.no_charts)

    if args.stdout:
        print(brief)
    else:
        OUTPUT_PATH.write_text(brief)
        print(f"Morning brief written to {OUTPUT_PATH}")

    log_brief(brief)

    if not args.no_notify:
        summary = build_notification_summary(conn)
        send_notification("LHM Morning Brief", summary)
        print(f"Notification sent: {summary}")

    conn.close()


if __name__ == "__main__":
    main()
