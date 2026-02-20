#!/usr/bin/env python3
"""
LIGHTHOUSE MACRO - MORNING BRIEF (HTML DASHBOARD)
===================================================
Generates a self-contained HTML morning briefing with:
  - Proprietary index dashboard (Diagnostic Dozen)
  - 8 embedded charts (base64 PNGs)
  - FRED release calendar (next 7 days)
  - RSS macro headlines (Fed, BLS, BEA)
  - Regime change alerts and threshold flags

Designed to run post-pipeline (~07:30 ET) via launchd.

Outputs:
    1. HTML file: ~/Desktop/LHM_Morning_Brief.html
    2. macOS notification with headline summary
    3. Persistent log: /Users/bob/LHM/logs/morning_brief.log

Usage:
    python morning_brief.py              # Full brief
    python morning_brief.py --no-notify  # Skip macOS notification
    python morning_brief.py --stdout     # Print to stdout instead of file
    python morning_brief.py --no-charts  # Skip chart generation (faster)
    python morning_brief.py --no-news    # Skip FRED calendar + RSS
"""

import sqlite3
import subprocess
import sys
import os
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "automation"))
from compute_indices import STATUS_THRESHOLDS, get_status
from lighthouse.config import API_KEYS

DB_PATH = Path("/Users/bob/LHM/Data/databases/Lighthouse_Master.db")
OUTPUT_PATH = Path.home() / "Desktop" / "LHM_Morning_Brief.html"
LOG_PATH = Path("/Users/bob/LHM/logs/morning_brief.log")

# Indices to feature in the brief, grouped by engine
MACRO_INDICES = ["MRI", "LPI", "PCI", "GCI", "HCI", "CCI", "BCI", "TCI"]
MONETARY_INDICES = ["GCI_Gov", "FCI", "LCI"]
STRUCTURE_INDICES = ["MSI", "SBD", "SPI", "SSD"]
CORE_SIGNALS = ["LFI", "CLG"]
ADVANCED = ["REC_PROB", "ENSEMBLE_RISK", "WARNING_LEVEL", "ALLOC_MULTIPLIER", "LIQ_STAGE", "SLI"]

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

# Key FRED releases to watch for
KEY_RELEASES = {
    "Employment Situation", "Consumer Price Index", "Producer Price Index",
    "FOMC", "Gross Domestic Product", "Personal Income and Outlays",
    "JOLTS", "Retail Sales", "Housing Starts", "Industrial Production",
    "Existing Home Sales", "New Residential Sales", "Durable Goods",
    "PCE", "University of Michigan", "ISM Manufacturing",
    "Federal Funds Rate", "Beige Book", "Treasury Statement",
    "Import and Export Prices", "Initial Claims",
}

# RSS feeds for macro headlines
RSS_FEEDS = [
    # Tier 1: Markets & Macro
    ("BBG", "https://feeds.bloomberg.com/markets/news.rss"),
    ("BBG", "https://feeds.bloomberg.com/economics/news.rss"),
    ("FT", "https://www.ft.com/markets?format=rss"),
    ("FT", "https://www.ft.com/global-economy?format=rss"),
    ("WSJ", "https://feeds.content.dowjones.io/public/rss/RSSMarketsMain"),
    ("WSJ", "https://feeds.content.dowjones.io/public/rss/socialeconomyfeed"),
    # Tier 2: Government sources
    ("Fed", "https://www.federalreserve.gov/feeds/press_all.xml"),
    ("BLS", "https://www.bls.gov/feed/bls_latest.rss"),
    ("BEA", "https://apps.bea.gov/rss/rss.xml"),
]


# ============================================================
# DATA FUNCTIONS (unchanged from original)
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


def get_pipeline_health(conn: sqlite3.Connection) -> dict:
    """Check pipeline run status and data freshness."""
    health = {}

    # Latest pipeline run
    try:
        cursor = conn.execute("""
            SELECT timestamp, source, series_updated, observations_added,
                   duration_seconds, status
            FROM update_log
            ORDER BY timestamp DESC
            LIMIT 1
        """)
        row = cursor.fetchone()
        if row:
            health["last_run"] = {
                "timestamp": row[0],
                "source": row[1],
                "series_updated": row[2],
                "observations_added": row[3],
                "duration_seconds": row[4],
                "status": row[5],
            }
    except Exception:
        health["last_run"] = None

    # Data quality summary
    try:
        cursor = conn.execute("""
            SELECT data_quality, COUNT(*) as cnt
            FROM series_meta
            GROUP BY data_quality
            ORDER BY cnt DESC
        """)
        health["quality"] = {row[0]: row[1] for row in cursor}
    except Exception:
        health["quality"] = {}

    # Horizon dataset freshness
    try:
        cursor = conn.execute("SELECT MAX(date) FROM horizon_dataset")
        row = cursor.fetchone()
        health["horizon_latest"] = row[0] if row else None
    except Exception:
        health["horizon_latest"] = None

    # Stale critical series
    try:
        critical_series = [
            "UNRATE", "PAYEMS", "CPIAUCSL", "PCEPILFE", "INDPRO",
            "MORTGAGE30US", "HOUST", "VIXCLS", "DGS10", "DGS2",
            "BAMLH0A0HYM2", "RRPONTSYD", "WALCL"
        ]
        placeholders = ",".join(["?" for _ in critical_series])
        cursor = conn.execute(f"""
            SELECT series_id, MAX(date) as latest_date
            FROM observations
            WHERE series_id IN ({placeholders})
            GROUP BY series_id
        """, critical_series)
        health["critical_freshness"] = {row[0]: row[1] for row in cursor}
    except Exception:
        health["critical_freshness"] = {}

    return health


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
# FRED RELEASE CALENDAR
# ============================================================

def fetch_fred_calendar() -> list:
    """Fetch upcoming FRED releases for the next 7 days."""
    try:
        api_key = API_KEYS.get("FRED", "")
        if not api_key:
            return []

        today = datetime.now().strftime("%Y-%m-%d")
        end = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")

        url = "https://api.stlouisfed.org/fred/releases/dates"
        params = {
            "api_key": api_key,
            "file_type": "json",
            "realtime_start": today,
            "realtime_end": end,
            "include_release_dates_with_no_data": "true",
            "sort_order": "asc",
        }

        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()

        releases = []
        seen = set()
        for item in data.get("release_dates", []):
            name = item.get("release_name", "")
            date = item.get("date", "")
            # Filter to key releases only
            if any(key.lower() in name.lower() for key in KEY_RELEASES):
                key = f"{name}_{date}"
                if key not in seen:
                    seen.add(key)
                    releases.append({"name": name, "date": date})

        return releases[:15]
    except Exception as e:
        print(f"  FRED calendar fetch failed: {e}")
        return []


# ============================================================
# RSS HEADLINES
# ============================================================

def fetch_rss_headlines() -> list:
    """Fetch recent headlines from macro RSS feeds."""
    headlines = []
    for source, url in RSS_FEEDS:
        try:
            headers = {"User-Agent": "LighthouseMacro/1.0 (data pipeline)"}
            resp = requests.get(url, timeout=8, headers=headers)
            resp.raise_for_status()
            root = ET.fromstring(resp.content)

            # Handle both RSS and Atom feeds
            items = root.findall(".//item")
            if not items:
                # Try Atom format
                ns = {"atom": "http://www.w3.org/2005/Atom"}
                items = root.findall(".//atom:entry", ns)

            for item in items[:2]:
                title = ""
                link = ""
                pub_date = ""

                # RSS format
                title_el = item.find("title")
                link_el = item.find("link")
                date_el = item.find("pubDate")

                if title_el is not None and title_el.text:
                    title = title_el.text.strip()
                if link_el is not None:
                    if link_el.text:
                        link = link_el.text.strip()
                    elif link_el.get("href"):
                        link = link_el.get("href")
                if date_el is not None and date_el.text:
                    pub_date = date_el.text.strip()

                # Atom format fallback
                if not title:
                    ns = {"atom": "http://www.w3.org/2005/Atom"}
                    t = item.find("atom:title", ns)
                    if t is not None and t.text:
                        title = t.text.strip()
                    l = item.find("atom:link", ns)
                    if l is not None:
                        link = l.get("href", "")

                if title:
                    headlines.append({
                        "source": source,
                        "title": title[:120],
                        "link": link,
                        "date": pub_date[:25] if pub_date else "",
                    })
        except Exception as e:
            print(f"  RSS fetch failed for {source}: {e}")
            continue

    return headlines


# ============================================================
# HTML TEMPLATE
# ============================================================

def _status_color(status: str) -> str:
    """Map a status string to a CSS color."""
    if not status:
        return "#8b949e"
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
        return "#8b949e"  # muted
    if any(w in s for w in ["EXPANSION", "ON TARGET", "TREND", "LOOSE",
                            "LOW RISK", "BULLISH", "GREEN", "ACCUMULATION",
                            "CAPITAL", "RAPID"]):
        return "#00BB99"  # Sea
    return "#8b949e"


def _change_html(index_id: str, current: dict, prior: dict) -> str:
    """Format value change as styled HTML."""
    if index_id not in current:
        return ""
    val = current[index_id]["value"]
    if index_id not in prior:
        return f"{val:+.3f}"
    delta = val - prior[index_id]["value"]
    if abs(delta) < 0.001:
        return f'<span style="color:#8b949e">=</span>'
    color = "#00BB99" if delta > 0 else "#FF6723"
    arrow = "&#9650;" if delta > 0 else "&#9660;"
    return f'<span style="color:{color}">{arrow} {abs(delta):.3f}</span>'


def _staleness_badge(date_str: str) -> str:
    """Return a staleness badge if data is old."""
    if not date_str:
        return ""
    try:
        d = datetime.strptime(date_str[:10], "%Y-%m-%d")
        days = (datetime.now() - d).days
        if days > 7:
            return f'<span class="stale-badge">{days}d</span>'
        elif days > 2:
            return f'<span class="age-badge">{days}d</span>'
    except (ValueError, TypeError):
        pass
    return ""


# Full names for display
_INDEX_NAMES = {
    "MRI": "Macro Risk Index",
    "LPI": "Labor Pressure",
    "LFI": "Labor Fragility",
    "PCI": "Price Conditions",
    "GCI": "Growth Conditions",
    "HCI": "Housing Conditions",
    "CCI": "Consumer Conditions",
    "BCI": "Business Conditions",
    "TCI": "Trade Conditions",
    "GCI_Gov": "Government Conditions",
    "FCI": "Financial Conditions",
    "LCI": "Liquidity Cushion",
    "CLG": "Credit-Labor Gap",
    "MSI": "Market Structure",
    "SBD": "Structure-Breadth Divergence",
    "SPI": "Sentiment & Positioning",
    "SSD": "Sentiment-Structure Divergence",
    "SLI": "Stablecoin Liquidity",
    "REC_PROB": "Recession Probability",
    "ENSEMBLE_RISK": "Ensemble Risk",
    "WARNING_LEVEL": "Warning Level",
    "ALLOC_MULTIPLIER": "Allocation Multiplier",
    "LIQ_STAGE": "Liquidity Stage",
}

# Indices where higher value = worse outcome (display high-to-low: bad left, good right)
_HIGH_IS_BAD = {
    "MRI", "LFI", "PCI", "GCI_Gov", "YFS", "SVI", "LIQ_STAGE",
    "REC_PROB", "WARNING_LEVEL", "ENSEMBLE_RISK", "DISCONTINUITY_PREMIUM",
    "SBD", "CLG", "RMP_Index", "EMD",
}


def _gauge_colors(n: int) -> list:
    """Return a fixed color gradient for n tiers: bad (left) to good (right)."""
    # Venus -> Dusk -> Gray -> Sea -> Sky
    palette = ["#FF2389", "#FF6723", "#8b949e", "#00BB99", "#33CCFF"]
    if n <= 1:
        return palette[2:3]
    if n == 2:
        return [palette[0], palette[4]]
    if n == 3:
        return [palette[0], palette[2], palette[4]]
    if n == 4:
        return [palette[0], palette[1], palette[3], palette[4]]
    if n == 5:
        return palette
    # 6+ tiers (e.g. LIQ_STAGE): interpolate by stretching palette
    colors = []
    for i in range(n):
        idx = i * (len(palette) - 1) / (n - 1)
        colors.append(palette[round(idx)])
    return colors


def _regime_gauge(index_id: str, current_status: str) -> str:
    """Render an inline HTML gauge strip showing all regime tiers with the active one highlighted."""
    tiers = STATUS_THRESHOLDS.get(index_id, [])
    if not tiers:
        return ""
    # Tiers stored high-to-low. For "high = good" indices, reverse so bad is on left.
    # For "high = bad" indices, keep as-is (highest/worst already on left after display).
    if index_id in _HIGH_IS_BAD:
        # High value = bad. Stored order: [worst, ..., best]. Display as-is: bad left, good right.
        display_tiers = list(tiers)
    else:
        # High value = good. Stored order: [best, ..., worst]. Reverse: bad left, good right.
        display_tiers = list(reversed(tiers))
    colors = _gauge_colors(len(display_tiers))
    segments = []
    for i, (_, label) in enumerate(display_tiers):
        color = colors[i]
        is_active = (label.upper() == (current_status or "").upper())
        cls = "gauge-tier gauge-active" if is_active else "gauge-tier"
        segments.append(f'<span class="{cls}" style="background:{color}">{label}</span>')
    return f'<div class="gauge-strip">{"".join(segments)}</div>'


def _index_panel_row(index_id: str, current: dict, prior: dict) -> str:
    """Build a single panel row for an index with gauge strip and regime change badge."""
    if index_id not in current:
        return ""
    info = current[index_id]
    val = info["value"]
    status = info["status"] or "N/A"
    date = info.get("date", "")
    color = _status_color(status)
    change = _change_html(index_id, current, prior)
    stale = _staleness_badge(date)
    gauge = _regime_gauge(index_id, status)

    # Regime change badge
    regime_badge = ""
    prev = prior.get(index_id)
    if prev and prev["status"] and prev["status"] != status:
        regime_badge = (
            f'<span class="regime-badge">'
            f'was: {prev["status"]}'
            f'</span>'
        )

    full_name = _INDEX_NAMES.get(index_id, index_id)
    display_name = f'{full_name} <span class="idx-abbrev">({index_id})</span>'

    return f"""<div class="panel-row">
        <div class="panel-left">
            <span class="idx-name">{display_name}</span>
            <span class="idx-value">{val:+.3f}</span>
            <span class="idx-change">{change}</span>
            {stale}
        </div>
        <div class="panel-center">{gauge}</div>
        <div class="panel-right">
            <span class="idx-status" style="color:{color}">{status}</span>
            {regime_badge}
        </div>
    </div>"""


def build_brief(conn: sqlite3.Connection, include_charts: bool = True,
                include_news: bool = True) -> str:
    """Build the full morning brief as self-contained HTML."""
    now = datetime.now()
    current = get_latest_indices(conn)
    prior = get_prior_indices(conn, current)
    health = get_pipeline_health(conn)
    regime_changes = detect_regime_changes(current, prior)
    alerts = detect_threshold_alerts(current)

    # Task/Content/CRM sections
    automation_html = ""
    try:
        from briefing_helpers import get_all_brief_sections
        automation_html = get_all_brief_sections()
        if automation_html:
            print(f"  Task/CRM sections loaded")
    except Exception as e:
        print(f"  WARNING: Task/CRM sections skipped: {e}")

    # Generate charts
    chart_data = []
    if include_charts:
        try:
            from brief_charts import generate_dashboard_charts
            chart_data = generate_dashboard_charts(conn)
            print(f"  Generated {len(chart_data)} charts")
        except Exception as e:
            print(f"  WARNING: Chart generation failed: {e}")

    # Fetch calendar and RSS
    calendar = []
    headlines = []
    if include_news:
        calendar = fetch_fred_calendar()
        headlines = fetch_rss_headlines()
        print(f"  Calendar: {len(calendar)} releases | RSS: {len(headlines)} headlines")

    # Pipeline status line
    pipe_status = ""
    if health.get("last_run"):
        run = health["last_run"]
        status_word = "OK" if "completed" in str(run["status"]) else run["status"]
        pipe_status = f'{run["timestamp"][:16]} | {run["series_updated"]} series | {status_word}'
    else:
        pipe_status = "No pipeline run found"

    # Horizon status
    horizon_html = ""
    if health.get("horizon_latest"):
        h_date_str = health["horizon_latest"][:10]
        try:
            h_date = datetime.strptime(h_date_str, "%Y-%m-%d")
            h_days = (now - h_date).days
            if h_days > 3:
                horizon_html = f'<div class="alert-box warning">HORIZON DATASET STALE: {h_date_str} ({h_days}d old). Macro indices frozen.</div>'
            else:
                horizon_html = f'<div class="status-ok">Horizon: {h_date_str}</div>'
        except (ValueError, TypeError):
            pass

    # Quality flags
    quality_html = ""
    if health.get("quality"):
        q = health["quality"]
        suspect = q.get("suspect", 0)
        warning = q.get("warning", 0)
        if suspect > 0 or warning > 0:
            quality_html = f'<span class="quality-flags">{suspect} suspect, {warning} warning</span>'

    # Hero cards (MRI, Recession Prob, Warning Level)
    mri_val = current.get("MRI", {}).get("value", 0)
    mri_status = current.get("MRI", {}).get("status", "N/A") or "N/A"
    rec_val = current.get("REC_PROB", {}).get("value", 0)
    rec_status = current.get("REC_PROB", {}).get("status", "N/A") or "N/A"
    warn_val = current.get("WARNING_LEVEL", {}).get("value", 0)
    warn_status = current.get("WARNING_LEVEL", {}).get("status", "N/A") or "N/A"
    alloc_val = current.get("ALLOC_MULTIPLIER", {}).get("value", 0)
    alloc_status = current.get("ALLOC_MULTIPLIER", {}).get("status", "N/A") or "N/A"

    # Alerts HTML — no longer a separate section; regime changes shown inline via panel badges

    # Charts HTML
    charts_html = ""
    if chart_data:
        chart_items = []
        for c in chart_data:
            if c.get("base64"):
                chart_items.append(
                    f'<div class="chart-card">'
                    f'<img src="data:image/png;base64,{c["base64"]}" alt="{c["title"]}" />'
                    f'</div>'
                )
        charts_html = f"""
        <div class="section">
            <h2>Market Snapshot</h2>
            <div class="chart-grid">
                {"".join(chart_items)}
            </div>
        </div>"""

    # Index panels (gauge-based)
    def _build_panel(title: str, indices: list) -> str:
        rows = [_index_panel_row(idx, current, prior) for idx in indices]
        rows = [r for r in rows if r]
        if not rows:
            return ""
        return f"""
        <div class="section">
            <h2>{title}</h2>
            {"".join(rows)}
        </div>"""

    engine1_html = _build_panel("Engine 1: Macro Dynamics", MACRO_INDICES)
    core_html = _build_panel("Core Signals", CORE_SIGNALS)
    engine2_html = _build_panel("Engine 2: Monetary Mechanics", MONETARY_INDICES)
    engine3_html = _build_panel("Engine 3: Structure &amp; Sentiment", STRUCTURE_INDICES)
    risk_html = _build_panel("Risk Dashboard", ADVANCED)

    # Calendar HTML
    calendar_html = ""
    if calendar:
        cal_items = []
        for r in calendar:
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

    # RSS HTML
    rss_html = ""
    if headlines:
        rss_items = []
        for h in headlines:
            link_attr = f' href="{h["link"]}" target="_blank"' if h.get("link") else ""
            tag = "a" if link_attr else "span"
            rss_items.append(
                f'<div class="rss-item">'
                f'<span class="rss-source">{h["source"]}</span>'
                f'<{tag}{link_attr} class="rss-title">{h["title"]}</{tag}>'
                f'</div>'
            )
        rss_html = f"""
        <div class="section">
            <h2>Macro Headlines</h2>
            {"".join(rss_items)}
        </div>"""

    # Stale series
    stale_html = ""
    if health.get("critical_freshness"):
        stale_items = []
        for series_id, latest_date in health["critical_freshness"].items():
            try:
                s_date = datetime.strptime(latest_date[:10], "%Y-%m-%d")
                days_old = (now - s_date).days
                if days_old > 10:
                    stale_items.append((series_id, latest_date[:10], days_old))
            except (ValueError, TypeError):
                pass
        if stale_items:
            rows = "".join(
                f'<div class="stale-item"><span>{sid}</span><span>{dt}</span><span class="stale-badge">{days}d</span></div>'
                for sid, dt, days in sorted(stale_items, key=lambda x: -x[2])
            )
            stale_html = f"""
            <div class="section">
                <h2>Stale Critical Series</h2>
                {rows}
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
            --ocean: #0089D1;
            --dusk: #FF6723;
            --sky: #33CCFF;
            --venus: #FF2389;
            --sea: #00BB99;
            --doldrums: #D3D6D9;
            --bg: #0A1628;
            --card: #0f2140;
            --text: #e6edf3;
            --muted: #8b949e;
            --border: #1e3350;
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

        /* ---- HEADER ---- */
        .header {{
            text-align: center;
            padding: 1.5rem 0 1rem;
            border-bottom: 3px solid var(--ocean);
            margin-bottom: 1.5rem;
        }}
        .header-brand {{
            font-family: 'Montserrat', sans-serif;
            font-size: 1.1rem;
            font-weight: 700;
            letter-spacing: 3px;
            color: var(--ocean);
            margin-bottom: 0.25rem;
        }}
        .header-title {{
            font-family: 'Montserrat', sans-serif;
            font-size: 1.6rem;
            font-weight: 600;
            color: var(--text);
            margin-bottom: 0.3rem;
        }}
        .header-meta {{
            font-size: 0.8rem;
            color: var(--muted);
            font-family: 'Source Code Pro', monospace;
        }}

        /* ---- ACCENT BAR ---- */
        .accent-bar {{
            height: 4px;
            background: linear-gradient(90deg, var(--ocean) 66%, var(--dusk) 66%);
            margin-bottom: 1.5rem;
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
            font-size: 0.9rem;
            font-weight: 700;
            color: var(--ocean);
            text-transform: uppercase;
            letter-spacing: 1.5px;
            margin-bottom: 0.8rem;
            padding-bottom: 0.4rem;
            border-bottom: 1px solid var(--border);
        }}

        /* ---- PANEL ROWS (Gauge Layout) ---- */
        .panel-row {{
            display: flex;
            align-items: center;
            gap: 0.8rem;
            padding: 0.45rem 0;
            border-bottom: 1px solid rgba(30, 51, 80, 0.4);
            font-family: 'Source Code Pro', monospace;
            font-size: 0.82rem;
        }}
        .panel-row:last-child {{ border-bottom: none; }}
        .panel-row:hover {{ background: rgba(0, 137, 209, 0.05); }}
        .panel-left {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
            min-width: 200px;
            flex-shrink: 0;
        }}
        .panel-center {{
            flex: 1;
            min-width: 0;
        }}
        .panel-right {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
            flex-shrink: 0;
            min-width: 140px;
            justify-content: flex-end;
        }}
        .idx-name {{
            font-weight: 600;
            color: var(--text);
            font-family: 'Inter', sans-serif;
            font-size: 0.8rem;
        }}
        .idx-abbrev {{
            color: var(--muted);
            font-weight: 400;
            font-size: 0.7rem;
        }}
        .idx-value {{
            color: var(--sky);
        }}
        .idx-change {{
            font-size: 0.75rem;
        }}
        .idx-status {{
            font-weight: 600;
            font-size: 0.78rem;
        }}

        /* ---- GAUGE STRIP ---- */
        .gauge-strip {{
            display: flex;
            gap: 2px;
            align-items: center;
        }}
        .gauge-tier {{
            flex: 1;
            padding: 0.15rem 0;
            border-radius: 3px;
            font-size: 0.5rem;
            font-family: 'Inter', sans-serif;
            font-weight: 500;
            color: rgba(255,255,255,0.5);
            opacity: 0.2;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            text-align: center;
        }}
        .gauge-active {{
            opacity: 1;
            color: #fff;
            font-weight: 700;
            font-size: 0.55rem;
            box-shadow: 0 0 6px rgba(255,255,255,0.1);
        }}

        /* ---- REGIME BADGE ---- */
        .regime-badge {{
            font-size: 0.6rem;
            font-family: 'Inter', sans-serif;
            color: var(--dusk);
            background: rgba(255, 103, 35, 0.15);
            padding: 0.1rem 0.35rem;
            border-radius: 3px;
            font-weight: 600;
            white-space: nowrap;
        }}

        /* ---- BADGES ---- */
        .stale-badge {{
            background: rgba(255, 103, 35, 0.2);
            color: var(--dusk);
            font-size: 0.65rem;
            padding: 0.15rem 0.4rem;
            border-radius: 4px;
            font-weight: 600;
        }}
        .age-badge {{
            background: rgba(139, 148, 158, 0.15);
            color: var(--muted);
            font-size: 0.65rem;
            padding: 0.15rem 0.4rem;
            border-radius: 4px;
        }}

        /* ---- ALERTS (status boxes) ---- */
        .alert-box {{
            padding: 0.6rem 0.8rem;
            border-radius: 6px;
            font-size: 0.8rem;
            margin-bottom: 0.8rem;
        }}
        .alert-box.warning {{
            background: rgba(255, 103, 35, 0.1);
            border: 1px solid var(--dusk);
            color: var(--dusk);
        }}
        .status-ok {{
            font-size: 0.8rem;
            color: var(--sea);
            margin-bottom: 0.5rem;
        }}
        .quality-flags {{
            font-size: 0.75rem;
            color: var(--muted);
        }}

        /* ---- CHARTS ---- */
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

        /* ---- CALENDAR ---- */
        .cal-item {{
            display: flex;
            gap: 1rem;
            padding: 0.35rem 0;
            font-size: 0.82rem;
            border-bottom: 1px solid rgba(30, 51, 80, 0.3);
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

        /* ---- RSS ---- */
        .rss-item {{
            display: flex;
            gap: 0.8rem;
            padding: 0.35rem 0;
            font-size: 0.8rem;
            border-bottom: 1px solid rgba(30, 51, 80, 0.3);
            align-items: baseline;
        }}
        .rss-item:last-child {{ border-bottom: none; }}
        .rss-source {{
            font-size: 0.65rem;
            font-weight: 600;
            color: var(--ocean);
            text-transform: uppercase;
            letter-spacing: 1px;
            min-width: 50px;
        }}
        .rss-title {{
            color: var(--text);
            text-decoration: none;
        }}
        a.rss-title:hover {{
            color: var(--sky);
            text-decoration: underline;
        }}

        /* ---- STALE SERIES ---- */
        .stale-item {{
            display: flex;
            justify-content: space-between;
            padding: 0.3rem 0;
            font-size: 0.8rem;
            font-family: 'Source Code Pro', monospace;
            border-bottom: 1px solid rgba(30, 51, 80, 0.3);
        }}
        .stale-item:last-child {{ border-bottom: none; }}

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
        <div class="header-title">Morning Brief &mdash; {now.strftime('%A, %B %d, %Y')}</div>
        <div class="header-meta">Pipeline: {pipe_status} &bull; {now.strftime('%H:%M ET')}</div>
    </div>

    {horizon_html}

    <!-- Hero Cards -->
    <div class="hero-grid">
        <div class="hero-card">
            <div class="hero-label">MRI</div>
            <div class="hero-value" style="color:{_status_color(mri_status)}">{mri_val:+.3f}</div>
            <div class="hero-status" style="color:{_status_color(mri_status)}">{mri_status}</div>
        </div>
        <div class="hero-card">
            <div class="hero-label">Recession Prob</div>
            <div class="hero-value" style="color:{_status_color(rec_status)}">{rec_val:.1%}</div>
            <div class="hero-status" style="color:{_status_color(rec_status)}">{rec_status}</div>
        </div>
        <div class="hero-card">
            <div class="hero-label">Warning Level</div>
            <div class="hero-value" style="color:{_status_color(warn_status)}">{warn_val:.0f}</div>
            <div class="hero-status" style="color:{_status_color(warn_status)}">{warn_status}</div>
        </div>
        <div class="hero-card">
            <div class="hero-label">Allocation</div>
            <div class="hero-value" style="color:{_status_color(alloc_status)}">{alloc_val:.2f}x</div>
            <div class="hero-status" style="color:{_status_color(alloc_status)}">{alloc_status}</div>
        </div>
    </div>

    {automation_html}
    {charts_html}
    {engine1_html}
    {core_html}
    {engine2_html}
    {engine3_html}
    {risk_html}
    {calendar_html}
    {rss_html}
    {stale_html}

    <div class="footer">
        <div class="footer-tagline">MACRO, ILLUMINATED.</div>
        Lighthouse Macro &bull; {now.strftime('%Y-%m-%d %H:%M ET')}
    </div>

</div>
</body>
</html>"""

    return html


def build_notification_summary(conn: sqlite3.Connection) -> str:
    """Build a short summary for macOS notification."""
    current = get_latest_indices(conn)
    prior = get_prior_indices(conn, current)
    regime_changes = detect_regime_changes(current, prior)

    parts = []

    # MRI headline
    if "MRI" in current:
        parts.append(f"MRI: {current['MRI']['value']:.2f} [{current['MRI']['status']}]")

    # MSI
    if "MSI" in current:
        parts.append(f"MSI: {current['MSI']['value']:.2f} [{current['MSI']['status']}]")

    # Regime changes
    if regime_changes:
        for rc in regime_changes[:2]:
            parts.append(f"{rc['index']}: {rc['from_status']}->{rc['to_status']}")

    return " | ".join(parts) if parts else "Pipeline complete. No alerts."


def send_notification(title: str, message: str):
    """Send a macOS notification via terminal-notifier or osascript."""
    # Try terminal-notifier first (better UX)
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

    # Fallback to osascript
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
        # For log, just record a compact summary, not the full HTML
        f.write(f"HTML dashboard generated at {OUTPUT_PATH}\n")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Lighthouse Macro Morning Brief")
    parser.add_argument("--no-notify", action="store_true", help="Skip macOS notification")
    parser.add_argument("--stdout", action="store_true", help="Print to stdout instead of file")
    parser.add_argument("--no-charts", action="store_true", help="Skip chart generation (faster)")
    parser.add_argument("--no-news", action="store_true", help="Skip FRED calendar + RSS")
    args = parser.parse_args()

    conn = sqlite3.connect(DB_PATH, timeout=30)

    # Build the brief
    brief = build_brief(
        conn,
        include_charts=not args.no_charts,
        include_news=not args.no_news,
    )

    # Output
    if args.stdout:
        print(brief)
    else:
        OUTPUT_PATH.write_text(brief)
        print(f"Morning brief written to {OUTPUT_PATH}")

    # Log
    log_brief(brief)

    # Notification
    if not args.no_notify:
        summary = build_notification_summary(conn)
        send_notification("LHM Morning Brief", summary)
        print(f"Notification sent: {summary}")

    conn.close()


if __name__ == "__main__":
    main()
