#!/usr/bin/env python3
"""
LIGHTHOUSE MACRO - THRESHOLD ALERT SYSTEM
==========================================
Monitors proprietary indices for regime transitions and threshold crossings.
Tracks prior state to detect changes between runs.

State file: /Users/bob/LHM/Data/alert_state.json
Alert log:  /Users/bob/LHM/logs/alerts.log
Alert file: /Users/bob/LHM/Data/alerts.md (readable by Claude in next session)

Usage:
    python threshold_alerts.py              # Check and alert
    python threshold_alerts.py --reset      # Reset state (treat all as new)
    python threshold_alerts.py --dry-run    # Check but don't update state
    python threshold_alerts.py --stdout     # Print alerts to stdout
"""

import sqlite3
import json
import subprocess
import sys
import os
from datetime import datetime
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from compute_indices import STATUS_THRESHOLDS, get_status

DB_PATH = Path("/Users/bob/LHM/Data/databases/Lighthouse_Master.db")
STATE_PATH = Path("/Users/bob/LHM/Data/alert_state.json")
ALERT_LOG_PATH = Path("/Users/bob/LHM/logs/alerts.log")
ALERT_MD_PATH = Path("/Users/bob/LHM/Data/alerts.md")

# ============================================================
# ALERT RULES
# ============================================================
# Each rule defines: index, condition, severity, message template
# Severity: CRITICAL, HIGH, MEDIUM, INFO

ALERT_RULES = [
    # MRI regime transitions
    {"index": "MRI", "above": 0.50, "severity": "CRITICAL",
     "msg": "MRI entered RECESSION regime ({value:.3f})"},
    {"index": "MRI", "above": 0.25, "severity": "HIGH",
     "msg": "MRI entered PRE-RECESSION regime ({value:.3f})"},
    {"index": "MRI", "above": 0.10, "severity": "MEDIUM",
     "msg": "MRI entered LATE CYCLE regime ({value:.3f})"},
    {"index": "MRI", "below": -0.20, "severity": "INFO",
     "msg": "MRI entered EARLY EXPANSION regime ({value:.3f})"},

    # Labor fragility
    {"index": "LFI", "above": 1.5, "severity": "CRITICAL",
     "msg": "LFI CRITICAL: Labor fragility at {value:.3f}. Recession imminent signal."},
    {"index": "LFI", "above": 1.0, "severity": "HIGH",
     "msg": "LFI HIGH: Labor fragility at {value:.3f}. Pre-recessionary."},
    {"index": "LFI", "above": 0.5, "severity": "MEDIUM",
     "msg": "LFI ELEVATED: Labor fragility at {value:.3f}. Monitor quits rate."},

    # Liquidity
    {"index": "LCI", "below": -1.0, "severity": "CRITICAL",
     "msg": "LCI STRESS: Liquidity cushion at {value:.3f}. System buffer exhausted."},
    {"index": "LCI", "below": -0.5, "severity": "HIGH",
     "msg": "LCI SCARCE: Liquidity cushion at {value:.3f}. Reduce gross exposure."},

    # Credit-Labor Gap
    {"index": "CLG", "below": -1.0, "severity": "HIGH",
     "msg": "CLG MISPRICED: Credit-Labor gap at {value:.3f}. Spreads too tight for labor reality."},
    {"index": "CLG", "below": -1.5, "severity": "CRITICAL",
     "msg": "CLG SEVERELY MISPRICED: Gap at {value:.3f}. Add credit protection."},

    # Market Structure
    {"index": "MSI", "below": -1.0, "severity": "HIGH",
     "msg": "MSI BEARISH: Market structure at {value:.3f}. Reduce gross exposure."},
    {"index": "MSI", "above": 1.0, "severity": "INFO",
     "msg": "MSI STRONG: Market structure at {value:.3f}. Trend confirmed."},

    # Structure-Breadth Divergence
    {"index": "SBD", "above": 1.0, "severity": "HIGH",
     "msg": "SBD DISTRIBUTION: Generals without soldiers ({value:.3f}). Breadth diverging from price."},
    {"index": "SBD", "above": 1.5, "severity": "CRITICAL",
     "msg": "SBD EXTREME: Distribution warning at {value:.3f}. Major divergence."},

    # Sentiment
    {"index": "SPI", "above": 1.5, "severity": "HIGH",
     "msg": "SPI EXTREME FEAR: Sentiment at {value:.3f}. Contrarian bullish signal."},
    {"index": "SPI", "below": -1.0, "severity": "HIGH",
     "msg": "SPI EUPHORIC: Sentiment at {value:.3f}. Contrarian bearish signal."},

    # Sentiment-Structure Divergence
    {"index": "SSD", "above": 1.5, "severity": "HIGH",
     "msg": "SSD CAPITULATION: Fear + weak structure ({value:.3f}). Watch for bottom formation."},
    {"index": "SSD", "below": -1.5, "severity": "HIGH",
     "msg": "SSD BLOW-OFF: Euphoria + strong structure ({value:.3f}). Top risk elevated."},

    # Recession probability
    {"index": "REC_PROB", "above": 0.70, "severity": "CRITICAL",
     "msg": "Recession probability HIGH: {value:.1%}"},
    {"index": "REC_PROB", "above": 0.40, "severity": "HIGH",
     "msg": "Recession probability ELEVATED: {value:.1%}"},

    # Stablecoin liquidity
    {"index": "SLI", "below": -1.0, "severity": "HIGH",
     "msg": "SLI SEVERE CONTRACTION: Stablecoin liquidity at {value:.3f}. On-chain drying up."},
    {"index": "SLI", "below": -0.5, "severity": "MEDIUM",
     "msg": "SLI CONTRACTING: Stablecoin liquidity at {value:.3f}."},

    # Liquidity stage
    {"index": "LIQ_STAGE", "above": 3.5, "severity": "CRITICAL",
     "msg": "LIQUIDITY STAGE {value:.0f}: Collateral stress or worse. Crisis transmission active."},
    {"index": "LIQ_STAGE", "above": 2.5, "severity": "HIGH",
     "msg": "LIQUIDITY STAGE {value:.0f}: SRF usage surge. Funding stress emerging."},

    # Warning system
    {"index": "WARNING_LEVEL", "above": 3.5, "severity": "CRITICAL",
     "msg": "WARNING SYSTEM: RED. Multiple indicators flashing."},
    {"index": "WARNING_LEVEL", "above": 2.5, "severity": "HIGH",
     "msg": "WARNING SYSTEM: AMBER. Elevated risk signals."},

    # Prices
    {"index": "PCI", "above": 1.0, "severity": "HIGH",
     "msg": "PCI HIGH INFLATION: Price conditions at {value:.3f}. Short duration, inflation hedges."},
    {"index": "PCI", "below": -0.5, "severity": "MEDIUM",
     "msg": "PCI DEFLATIONARY: Price conditions at {value:.3f}. Disinflationary pressure."},

    # Financial conditions
    {"index": "FCI", "below": -1.0, "severity": "HIGH",
     "msg": "FCI CRISIS: Financial conditions at {value:.3f}. Credit stress."},
]

# Breadth thrust detection (special rule)
BREADTH_THRUST_RULE = {
    "description": "% > 20d MA moves from <30% to >70% within 10 trading days",
    "series": "SPX_PCT_ABOVE_20D",
    "low_threshold": 30,
    "high_threshold": 70,
    "window_days": 14,  # Calendar days (~10 trading days)
}


def load_state() -> dict:
    """Load prior alert state from JSON file."""
    if STATE_PATH.exists():
        with open(STATE_PATH) as f:
            return json.load(f)
    return {"last_check": None, "active_alerts": {}, "index_states": {}}


def save_state(state: dict):
    """Save alert state to JSON file."""
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2, default=str)


def get_latest_indices(conn: sqlite3.Connection) -> dict:
    """Get latest value for each index."""
    query = """
        SELECT li.index_id, li.value, li.status, li.date
        FROM lighthouse_indices li
        INNER JOIN (
            SELECT index_id, MAX(date) as max_date
            FROM lighthouse_indices
            GROUP BY index_id
        ) latest ON li.index_id = latest.index_id AND li.date = latest.max_date
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


def check_breadth_thrust(conn: sqlite3.Connection) -> dict | None:
    """Check for breadth thrust signal."""
    try:
        rule = BREADTH_THRUST_RULE
        query = """
            SELECT date, value FROM observations
            WHERE series_id = ?
            ORDER BY date DESC
            LIMIT 20
        """
        cursor = conn.execute(query, (rule["series"],))
        rows = list(cursor)
        if len(rows) < 5:
            return None

        # Check if recent value is above high threshold
        latest_val = rows[0][1]
        latest_date = rows[0][0]

        if latest_val < rule["high_threshold"]:
            return None

        # Check if any value in the window was below low threshold
        cutoff = datetime.now() - __import__("datetime").timedelta(days=rule["window_days"])
        for date_str, val in rows:
            try:
                d = datetime.strptime(date_str[:10], "%Y-%m-%d")
                if d >= cutoff and val <= rule["low_threshold"]:
                    return {
                        "severity": "CRITICAL",
                        "msg": f"BREADTH THRUST DETECTED: % > 20d MA surged from "
                               f"{val:.0f}% to {latest_val:.0f}% in {rule['window_days']}d. "
                               f"Powerful bullish signal.",
                        "index": "BREADTH_THRUST",
                        "value": latest_val,
                        "date": latest_date,
                    }
            except (ValueError, TypeError):
                continue

    except Exception:
        pass
    return None


def evaluate_rules(current: dict, state: dict) -> list:
    """Evaluate all alert rules against current values."""
    alerts = []
    prior_states = state.get("index_states", {})

    for rule in ALERT_RULES:
        idx = rule["index"]
        if idx not in current:
            continue

        val = current[idx]["value"]
        triggered = False

        if "above" in rule and val >= rule["above"]:
            triggered = True
        elif "below" in rule and val <= rule["below"]:
            triggered = True

        if not triggered:
            continue

        # Build a unique key for this specific rule
        rule_key = f"{idx}_{'above' if 'above' in rule else 'below'}_{rule.get('above', rule.get('below'))}"

        # Only alert if this is a NEW alert (not already active)
        if rule_key in state.get("active_alerts", {}):
            continue

        alerts.append({
            "rule_key": rule_key,
            "index": idx,
            "severity": rule["severity"],
            "msg": rule["msg"].format(value=val),
            "value": val,
            "status": current[idx]["status"],
            "date": current[idx]["date"],
        })

    return alerts


def detect_status_transitions(current: dict, state: dict) -> list:
    """Detect when any index changes status (regime transition)."""
    transitions = []
    prior_states = state.get("index_states", {})

    for idx, info in current.items():
        prior = prior_states.get(idx)
        if prior and prior.get("status") != info["status"]:
            transitions.append({
                "index": idx,
                "from_status": prior["status"],
                "to_status": info["status"],
                "from_value": prior.get("value"),
                "to_value": info["value"],
                "date": info["date"],
            })

    return transitions


def format_alert_log(alerts: list, transitions: list) -> str:
    """Format alerts for the log file."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [f"\n[{now}] THRESHOLD ALERT CHECK"]

    if not alerts and not transitions:
        lines.append(f"[{now}] No new alerts or transitions.")
        return "\n".join(lines)

    if transitions:
        lines.append(f"[{now}] === REGIME TRANSITIONS ===")
        for t in transitions:
            lines.append(
                f"[{now}] {t['index']}: {t['from_status']} -> {t['to_status']} "
                f"({t['from_value']:.3f} -> {t['to_value']:.3f})"
            )

    if alerts:
        lines.append(f"[{now}] === THRESHOLD ALERTS ===")
        for a in alerts:
            lines.append(f"[{now}] [{a['severity']}] {a['msg']}")

    return "\n".join(lines)


def format_alerts_md(alerts: list, transitions: list, current: dict) -> str:
    """Format alerts as markdown for Claude to read."""
    now = datetime.now()
    lines = [
        f"# LHM Alerts - {now.strftime('%Y-%m-%d %H:%M ET')}",
        "",
    ]

    if not alerts and not transitions:
        lines.append("No active alerts or regime transitions.")
        return "\n".join(lines)

    if transitions:
        lines.append("## Regime Transitions")
        for t in transitions:
            lines.append(f"- **{t['index']}**: {t['from_status']} -> **{t['to_status']}** "
                        f"({t['from_value']:.3f} -> {t['to_value']:.3f}) as of {t['date'][:10]}")
        lines.append("")

    # Group alerts by severity
    if alerts:
        lines.append("## Active Alerts")
        for severity in ["CRITICAL", "HIGH", "MEDIUM", "INFO"]:
            sev_alerts = [a for a in alerts if a["severity"] == severity]
            if sev_alerts:
                lines.append(f"\n### {severity}")
                for a in sev_alerts:
                    lines.append(f"- {a['msg']}")
        lines.append("")

    # Current active alert summary (from state)
    lines.append("## Current Index Snapshot")
    lines.append(f"| {'Index':<16} | {'Value':>8} | {'Status':<22} | {'Date':<12} |")
    lines.append(f"|{'-'*18}|{'-'*10}|{'-'*24}|{'-'*14}|")
    for idx in sorted(current.keys()):
        info = current[idx]
        status = info['status'] or "N/A"
        date = (info['date'] or "")[:10]
        lines.append(f"| {idx:<16} | {info['value']:>8.3f} | {status:<22} | {date:<12} |")

    lines.append("")
    lines.append("---")
    lines.append(f"*Generated {now.strftime('%Y-%m-%d %H:%M ET')}*")
    return "\n".join(lines)


def send_notification(title: str, message: str, severity: str = "INFO"):
    """Send macOS notification."""
    sound = "Basso" if severity in ("CRITICAL", "HIGH") else "default"

    try:
        subprocess.run(
            ["terminal-notifier",
             "-title", title,
             "-message", message,
             "-group", f"lhm-alert-{severity.lower()}",
             "-sound", sound],
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


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Lighthouse Macro Threshold Alert System")
    parser.add_argument("--reset", action="store_true", help="Reset alert state")
    parser.add_argument("--dry-run", action="store_true", help="Check but don't update state")
    parser.add_argument("--stdout", action="store_true", help="Print alerts to stdout")
    parser.add_argument("--no-notify", action="store_true", help="Skip macOS notifications")
    args = parser.parse_args()

    conn = sqlite3.connect(DB_PATH)

    # Load or reset state
    if args.reset:
        state = {"last_check": None, "active_alerts": {}, "index_states": {}}
        print("Alert state reset.")
    else:
        state = load_state()

    # Get current values
    current = get_latest_indices(conn)

    # Evaluate
    alerts = evaluate_rules(current, state)
    transitions = detect_status_transitions(current, state)

    # Check breadth thrust
    thrust = check_breadth_thrust(conn)
    if thrust and thrust["rule_key" if "rule_key" in thrust else "index"] not in state.get("active_alerts", {}):
        alerts.append(thrust)

    # Format output
    log_entry = format_alert_log(alerts, transitions)
    md_content = format_alerts_md(alerts, transitions, current)

    if args.stdout:
        print(md_content)
    else:
        # Write alerts markdown
        ALERT_MD_PATH.parent.mkdir(parents=True, exist_ok=True)
        ALERT_MD_PATH.write_text(md_content)
        print(f"Alerts written to {ALERT_MD_PATH}")

    # Append to log
    ALERT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(ALERT_LOG_PATH, "a") as f:
        f.write(log_entry + "\n")

    # Notifications
    if not args.no_notify and not args.dry_run:
        # Send one notification per severity level
        critical_alerts = [a for a in alerts if a["severity"] == "CRITICAL"]
        high_alerts = [a for a in alerts if a["severity"] == "HIGH"]

        if critical_alerts:
            msg = " | ".join(a["msg"][:60] for a in critical_alerts[:3])
            send_notification("LHM CRITICAL ALERT", msg, "CRITICAL")

        if high_alerts:
            msg = " | ".join(a["msg"][:60] for a in high_alerts[:3])
            send_notification("LHM Alert", msg, "HIGH")

        if transitions:
            msg = " | ".join(
                f"{t['index']}: {t['from_status']}->{t['to_status']}"
                for t in transitions[:3]
            )
            send_notification("LHM Regime Change", msg, "MEDIUM")

    # Update state (unless dry-run)
    if not args.dry_run:
        # Mark new alerts as active
        for a in alerts:
            key = a.get("rule_key", a.get("index", "unknown"))
            state["active_alerts"][key] = {
                "triggered": datetime.now().isoformat(),
                "severity": a["severity"],
                "msg": a["msg"],
            }

        # Clear alerts that are no longer triggered
        to_remove = []
        for rule_key in list(state.get("active_alerts", {}).keys()):
            # Parse the rule key to check if condition still holds
            still_active = False
            for rule in ALERT_RULES:
                idx = rule["index"]
                rk = f"{idx}_{'above' if 'above' in rule else 'below'}_{rule.get('above', rule.get('below'))}"
                if rk == rule_key and idx in current:
                    val = current[idx]["value"]
                    if "above" in rule and val >= rule["above"]:
                        still_active = True
                    elif "below" in rule and val <= rule["below"]:
                        still_active = True
            if not still_active:
                to_remove.append(rule_key)

        for key in to_remove:
            del state["active_alerts"][key]

        # Update index states for next comparison
        state["index_states"] = {
            idx: {"value": info["value"], "status": info["status"], "date": info["date"]}
            for idx, info in current.items()
        }
        state["last_check"] = datetime.now().isoformat()

        save_state(state)
        print(f"State saved. {len(alerts)} new alerts, {len(transitions)} transitions.")
    else:
        print(f"Dry run: {len(alerts)} alerts, {len(transitions)} transitions (state not updated).")

    # Summary
    if alerts or transitions:
        print(f"\nSummary:")
        for t in transitions:
            print(f"  TRANSITION: {t['index']} {t['from_status']} -> {t['to_status']}")
        for a in alerts:
            print(f"  [{a['severity']}] {a['msg']}")

    conn.close()


if __name__ == "__main__":
    main()
