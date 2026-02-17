#!/usr/bin/env python3
"""
LIGHTHOUSE MACRO - MORNING BRIEF
=================================
Generates a daily morning briefing from the latest pipeline data.
Designed to run post-pipeline (~07:30 ET) via launchd or cron.

Outputs:
    1. Markdown file: ~/Desktop/LHM_Morning_Brief.md (overwritten daily)
    2. macOS notification with headline summary
    3. Persistent log: /Users/bob/LHM/logs/morning_brief.log

Usage:
    python morning_brief.py              # Full brief
    python morning_brief.py --no-notify  # Skip macOS notification
    python morning_brief.py --stdout     # Print to stdout instead of file
"""

import sqlite3
import subprocess
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from compute_indices import STATUS_THRESHOLDS, get_status

DB_PATH = Path("/Users/bob/LHM/Data/databases/Lighthouse_Master.db")
OUTPUT_PATH = Path.home() / "Desktop" / "LHM_Morning_Brief.md"
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
                break  # Only report the most severe threshold crossed
    return alerts


def format_index_line(index_id: str, info: dict, prior: dict = None, width: int = 12) -> str:
    """Format a single index line with value, status, and change."""
    val = info["value"]
    status = info["status"]
    date = info["date"]

    change_str = ""
    if prior and index_id in prior:
        delta = val - prior[index_id]["value"]
        arrow = "^" if delta > 0 else "v" if delta < 0 else "="
        change_str = f" ({arrow}{abs(delta):+.3f})"

    # Staleness warning
    stale = ""
    try:
        idx_date = datetime.strptime(date[:10], "%Y-%m-%d")
        days_old = (datetime.now() - idx_date).days
        if days_old > 7:
            stale = f" [STALE: {days_old}d old]"
        elif days_old > 2:
            stale = f" [{days_old}d old]"
    except (ValueError, TypeError):
        pass

    return f"| {index_id:<{width}} | {val:>8.3f}{change_str:<14} | {status:<22} |{stale}"


def build_brief(conn: sqlite3.Connection) -> str:
    """Build the full morning brief markdown."""
    now = datetime.now()
    current = get_latest_indices(conn)
    prior = get_prior_indices(conn, current)
    health = get_pipeline_health(conn)
    regime_changes = detect_regime_changes(current, prior)
    alerts = detect_threshold_alerts(current)

    lines = []
    lines.append(f"# LHM Morning Brief - {now.strftime('%A, %B %d, %Y')}")
    lines.append(f"*Generated {now.strftime('%H:%M ET')}*\n")

    # Pipeline health header
    lines.append("## Pipeline Status")
    if health.get("last_run"):
        run = health["last_run"]
        run_status = "OK" if "completed" in str(run["status"]) else run["status"]
        lines.append(f"- Last run: {run['timestamp'][:16]} | {run['series_updated']} series | {run_status}")
        duration_min = run["duration_seconds"] / 60 if run["duration_seconds"] else 0
        lines.append(f"- Duration: {duration_min:.0f} min | {run['observations_added']:,} observations added")
    else:
        lines.append("- **WARNING: No pipeline run found**")

    # Horizon dataset staleness
    if health.get("horizon_latest"):
        horizon_date = health["horizon_latest"][:10]
        try:
            h_date = datetime.strptime(horizon_date, "%Y-%m-%d")
            h_days = (now - h_date).days
            if h_days > 3:
                lines.append(f"- **HORIZON DATASET STALE: {horizon_date} ({h_days} days old)**")
                lines.append(f"  - Macro indices (MRI, LFI, LCI, etc.) frozen at {horizon_date}")
                lines.append(f"  - Run: `python horizon_dataset_builder.py` to update")
            else:
                lines.append(f"- Horizon dataset: {horizon_date} (current)")
        except (ValueError, TypeError):
            pass

    # Data quality
    if health.get("quality"):
        q = health["quality"]
        suspect = q.get("suspect", 0)
        warning = q.get("warning", 0)
        if suspect > 0 or warning > 0:
            lines.append(f"- Quality flags: {suspect} suspect, {warning} warning")

    lines.append("")

    # ALERTS section (regime changes + threshold alerts)
    if regime_changes or alerts:
        lines.append("## Alerts")
        if regime_changes:
            lines.append("### Regime Changes")
            for rc in regime_changes:
                lines.append(f"- **{rc['index']}**: {rc['from_status']} -> **{rc['to_status']}** "
                           f"({rc['from_value']:.3f} -> {rc['to_value']:.3f})")
            lines.append("")

        if alerts:
            lines.append("### Threshold Flags")
            for a in alerts:
                lines.append(f"- **{a['index']}** at {a['value']:.3f} [{a['status']}]")
            lines.append("")

    # MRI headline
    if "MRI" in current:
        mri = current["MRI"]
        lines.append(f"## MRI: {mri['value']:.3f} [{mri['status']}]")
        # Allocation guidance
        if "ALLOC_MULTIPLIER" in current:
            am = current["ALLOC_MULTIPLIER"]
            lines.append(f"Allocation Multiplier: {am['value']:.2f}x [{am['status']}]")
        if "REC_PROB" in current:
            rp = current["REC_PROB"]
            lines.append(f"Recession Probability: {rp['value']:.1%} [{rp['status']}]")
        lines.append("")

    # Engine 1: Macro Dynamics
    lines.append("## Engine 1: Macro Dynamics")
    lines.append(f"| {'Index':<12} | {'Value':<22} | {'Status':<22} |")
    lines.append(f"|{'-'*14}|{'-'*24}|{'-'*24}|")
    for idx in MACRO_INDICES:
        if idx in current:
            lines.append(format_index_line(idx, current[idx], prior))
    lines.append("")

    # Core Signals
    lines.append("### Core Signals")
    for idx in CORE_SIGNALS:
        if idx in current:
            lines.append(format_index_line(idx, current[idx], prior))
    lines.append("")

    # Engine 2: Monetary Mechanics
    lines.append("## Engine 2: Monetary Mechanics")
    lines.append(f"| {'Index':<12} | {'Value':<22} | {'Status':<22} |")
    lines.append(f"|{'-'*14}|{'-'*24}|{'-'*24}|")
    for idx in MONETARY_INDICES:
        if idx in current:
            lines.append(format_index_line(idx, current[idx], prior))
    lines.append("")

    # Engine 3: Market Structure & Sentiment
    lines.append("## Engine 3: Structure & Sentiment")
    lines.append(f"| {'Index':<12} | {'Value':<22} | {'Status':<22} |")
    lines.append(f"|{'-'*14}|{'-'*24}|{'-'*24}|")
    for idx in STRUCTURE_INDICES:
        if idx in current:
            lines.append(format_index_line(idx, current[idx], prior))
    lines.append("")

    # Advanced / Risk
    lines.append("## Risk Dashboard")
    lines.append(f"| {'Index':<12} | {'Value':<22} | {'Status':<22} |")
    lines.append(f"|{'-'*14}|{'-'*24}|{'-'*24}|")
    for idx in ADVANCED:
        if idx in current:
            lines.append(format_index_line(idx, current[idx], prior))
    lines.append("")

    # Critical data freshness
    if health.get("critical_freshness"):
        stale_series = []
        for series_id, latest_date in health["critical_freshness"].items():
            try:
                s_date = datetime.strptime(latest_date[:10], "%Y-%m-%d")
                days_old = (now - s_date).days
                if days_old > 10:
                    stale_series.append((series_id, latest_date[:10], days_old))
            except (ValueError, TypeError):
                pass
        if stale_series:
            lines.append("## Stale Critical Series")
            for sid, dt, days in sorted(stale_series, key=lambda x: -x[2]):
                lines.append(f"- {sid}: last updated {dt} ({days}d ago)")
            lines.append("")

    lines.append("---")
    lines.append(f"*Lighthouse Macro | {now.strftime('%Y-%m-%d %H:%M ET')}*")

    return "\n".join(lines)


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
        f.write(brief)
        f.write("\n")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Lighthouse Macro Morning Brief")
    parser.add_argument("--no-notify", action="store_true", help="Skip macOS notification")
    parser.add_argument("--stdout", action="store_true", help="Print to stdout instead of file")
    args = parser.parse_args()

    conn = sqlite3.connect(DB_PATH)

    # Build the brief
    brief = build_brief(conn)

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
