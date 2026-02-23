#!/usr/bin/env python3
"""
LIGHTHOUSE MACRO - BRIEFING HELPERS
====================================
Functions that query task/content/CRM databases and return
HTML sections for the morning brief.
"""

import sqlite3
from datetime import datetime, date, timedelta
from pathlib import Path

TASKS_DB = Path("/Users/bob/LHM/Data/databases/lhm_tasks.db")
CRM_DB = Path("/Users/bob/LHM/Data/databases/lhm_contacts.db")

# Brand colors
OCEAN = "#2389BB"
DUSK = "#FF6723"
SKY = "#00BBFF"
VENUS = "#FF2389"
SEA = "#00BB89"
MUTED = "#8b949e"
CARD_BG = "#0f2140"
BORDER = "#1e3350"


# ============================================================
# TASK QUERIES
# ============================================================

def get_todays_tasks(db_path: Path = TASKS_DB) -> list:
    """Get tasks due today."""
    if not db_path.exists():
        return []
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    today = date.today().isoformat()
    rows = conn.execute(
        "SELECT id, title, category, priority, status, due_date, due_time, notes "
        "FROM tasks WHERE due_date = ? AND status NOT IN ('done') "
        "ORDER BY due_time IS NULL, due_time, priority, id", (today,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_overdue_tasks(db_path: Path = TASKS_DB) -> list:
    """Get tasks past their due date."""
    if not db_path.exists():
        return []
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    today = date.today().isoformat()
    rows = conn.execute(
        "SELECT id, title, category, priority, status, due_date, due_time, notes "
        "FROM tasks WHERE due_date < ? AND due_date IS NOT NULL AND status NOT IN ('done') "
        "ORDER BY due_date, due_time, priority", (today,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_upcoming_tasks(db_path: Path = TASKS_DB, days: int = 7) -> list:
    """Get tasks due within N days (excluding today and overdue)."""
    if not db_path.exists():
        return []
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    today = date.today().isoformat()
    end = (date.today() + timedelta(days=days)).isoformat()
    rows = conn.execute(
        "SELECT id, title, category, priority, status, due_date, due_time, notes "
        "FROM tasks WHERE due_date > ? AND due_date <= ? AND status NOT IN ('done') "
        "ORDER BY due_date, due_time, priority", (today, end)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_upcoming_content(db_path: Path = TASKS_DB, days: int = 14) -> list:
    """Get unpublished content items."""
    if not db_path.exists():
        return []
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT id, content_type, title, pillar, status, planned_date, published_date, notes "
        "FROM content_calendar WHERE status != 'published' "
        "ORDER BY COALESCE(planned_date, '9999-12-31'), pillar"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ============================================================
# CRM QUERIES
# ============================================================

def get_todays_followups(db_path: Path = CRM_DB) -> list:
    """Get CRM follow-ups due today."""
    if not db_path.exists():
        return []
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    today = date.today().isoformat()
    rows = conn.execute("""
        SELECT i.id, i.follow_up_action, i.follow_up_date, i.summary,
               c.first_name, c.last_name, c.company, c.category
        FROM interactions i
        JOIN contacts c ON i.contact_id = c.id
        WHERE i.follow_up_date = ?
        ORDER BY c.tier DESC, i.id
    """, (today,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_overdue_followups(db_path: Path = CRM_DB) -> list:
    """Get CRM follow-ups past due."""
    if not db_path.exists():
        return []
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    today = date.today().isoformat()
    rows = conn.execute("""
        SELECT i.id, i.follow_up_action, i.follow_up_date, i.summary,
               c.first_name, c.last_name, c.company, c.category
        FROM interactions i
        JOIN contacts c ON i.contact_id = c.id
        WHERE i.follow_up_date < ? AND i.follow_up_date IS NOT NULL
        ORDER BY i.follow_up_date, c.tier DESC
    """, (today,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_stale_vips(db_path: Path = CRM_DB, days: int = 30) -> list:
    """Get VIP contacts with no interaction in N days."""
    if not db_path.exists():
        return []
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cutoff = (date.today() - timedelta(days=days)).isoformat()
    rows = conn.execute("""
        SELECT c.id, c.first_name, c.last_name, c.company, c.category,
               c.last_contact_date
        FROM contacts c
        WHERE c.tier = 'vip'
          AND (c.last_contact_date IS NULL OR c.last_contact_date < ?)
        ORDER BY c.last_contact_date
    """, (cutoff,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_pipeline_summary(db_path: Path = CRM_DB) -> dict:
    """Get pipeline stage counts."""
    if not db_path.exists():
        return {}
    conn = sqlite3.connect(db_path)
    rows = conn.execute("""
        SELECT stage, COUNT(*), COALESCE(SUM(estimated_value), 0)
        FROM pipeline
        WHERE stage NOT IN ('closed_won', 'closed_lost')
        GROUP BY stage
        ORDER BY CASE stage
            WHEN 'awareness' THEN 1
            WHEN 'engaged' THEN 2
            WHEN 'pitch' THEN 3
            WHEN 'trial' THEN 4
            WHEN 'negotiation' THEN 5
        END
    """).fetchall()
    conn.close()
    return {row[0]: {"count": row[1], "value": row[2]} for row in rows}


# ============================================================
# HTML FORMATTING
# ============================================================

def _priority_badge(p: int) -> str:
    colors = {1: VENUS, 2: DUSK, 3: MUTED, 4: MUTED}
    labels = {1: "URGENT", 2: "HIGH", 3: "NORMAL", 4: "LOW"}
    color = colors.get(p, MUTED)
    label = labels.get(p, "?")
    return f'<span style="background:rgba({_hex_to_rgb(color)},0.15);color:{color};font-size:0.65rem;padding:0.1rem 0.4rem;border-radius:3px;font-weight:600">{label}</span>'


def _hex_to_rgb(hex_color: str) -> str:
    h = hex_color.lstrip("#")
    return f"{int(h[0:2],16)},{int(h[2:4],16)},{int(h[4:6],16)}"


def _category_badge(cat: str) -> str:
    colors = {"follow_up": OCEAN, "content": SEA, "outreach": DUSK, "research": SKY, "admin": MUTED, "general": MUTED}
    color = colors.get(cat, MUTED)
    return f'<span style="color:{color};font-size:0.7rem;font-weight:500">{cat}</span>'


def format_tasks_html(today_tasks: list, overdue_tasks: list, upcoming_tasks: list) -> str:
    """Format tasks as an HTML section for the morning brief."""
    if not today_tasks and not overdue_tasks and not upcoming_tasks:
        return ""

    items = []

    if overdue_tasks:
        items.append(f'<div style="color:{VENUS};font-size:0.75rem;font-weight:600;margin-bottom:0.4rem">OVERDUE ({len(overdue_tasks)})</div>')
        for t in overdue_tasks:
            items.append(
                f'<div style="display:flex;justify-content:space-between;align-items:center;padding:0.3rem 0;border-bottom:1px solid rgba(30,51,80,0.3)">'
                f'<span style="font-size:0.82rem">{_priority_badge(t["priority"])} {t["title"]}</span>'
                f'<span style="font-family:Source Code Pro,monospace;font-size:0.72rem;color:{VENUS}">{t["due_date"]}</span>'
                f'</div>'
            )

    if today_tasks:
        items.append(f'<div style="color:{OCEAN};font-size:0.75rem;font-weight:600;margin:0.6rem 0 0.4rem">TODAY ({len(today_tasks)})</div>')
        for t in today_tasks:
            time_str = ""
            if t.get("due_time"):
                time_str = f'<span style="font-family:Source Code Pro,monospace;font-size:0.78rem;color:{SKY};font-weight:600;margin-right:0.4rem">{t["due_time"]}</span>'
            items.append(
                f'<div style="display:flex;justify-content:space-between;align-items:center;padding:0.3rem 0;border-bottom:1px solid rgba(30,51,80,0.3)">'
                f'<span style="font-size:0.82rem">{time_str}{_priority_badge(t["priority"])} {t["title"]}</span>'
                f'<span>{_category_badge(t["category"])}</span>'
                f'</div>'
            )

    if upcoming_tasks:
        items.append(f'<div style="color:{MUTED};font-size:0.75rem;font-weight:600;margin:0.6rem 0 0.4rem">UPCOMING ({len(upcoming_tasks)})</div>')
        for t in upcoming_tasks[:5]:  # Cap at 5
            items.append(
                f'<div style="display:flex;justify-content:space-between;align-items:center;padding:0.3rem 0;border-bottom:1px solid rgba(30,51,80,0.3)">'
                f'<span style="font-size:0.82rem;color:{MUTED}">{t["title"]}</span>'
                f'<span style="font-family:Source Code Pro,monospace;font-size:0.72rem;color:{MUTED}">{t["due_date"]}</span>'
                f'</div>'
            )

    return f"""
    <div class="section">
        <h2>Tasks &amp; Follow-ups</h2>
        {"".join(items)}
    </div>"""


def format_content_html(content: list) -> str:
    """Format content calendar as an HTML section."""
    if not content:
        return ""

    items = []
    for c in content:
        status = c["status"]
        status_colors = {
            "planned": MUTED,
            "drafting": OCEAN,
            "charts_done": SEA,
            "review": DUSK,
        }
        color = status_colors.get(status, MUTED)
        pillar = f'P{c["pillar"]}' if c.get("pillar") else ""
        date_str = c.get("planned_date") or ""
        items.append(
            f'<div style="display:flex;justify-content:space-between;align-items:center;padding:0.3rem 0;border-bottom:1px solid rgba(30,51,80,0.3)">'
            f'<span style="font-size:0.82rem"><span style="color:{MUTED};font-size:0.7rem;margin-right:0.3rem">{pillar}</span> {c["title"]}</span>'
            f'<span style="background:rgba({_hex_to_rgb(color)},0.15);color:{color};font-size:0.65rem;padding:0.1rem 0.4rem;border-radius:3px;font-weight:600">{status}</span>'
            f'</div>'
        )

    return f"""
    <div class="section">
        <h2>Content Pipeline</h2>
        {"".join(items)}
    </div>"""


def format_followups_html(today_followups: list, overdue_followups: list) -> str:
    """Format CRM follow-ups as HTML."""
    if not today_followups and not overdue_followups:
        return ""

    items = []

    if overdue_followups:
        items.append(f'<div style="color:{VENUS};font-size:0.75rem;font-weight:600;margin-bottom:0.4rem">OVERDUE FOLLOW-UPS ({len(overdue_followups)})</div>')
        for f in overdue_followups:
            name = f"{f['first_name']} {f['last_name']}"
            company = f" ({f['company']})" if f.get("company") else ""
            action = f.get("follow_up_action") or "Follow up"
            items.append(
                f'<div style="padding:0.3rem 0;border-bottom:1px solid rgba(30,51,80,0.3);font-size:0.82rem">'
                f'<span style="font-weight:600">{name}</span>{company}'
                f'<span style="color:{MUTED};font-size:0.75rem;margin-left:0.5rem">{action}</span>'
                f'<span style="float:right;font-family:Source Code Pro,monospace;font-size:0.72rem;color:{VENUS}">{f["follow_up_date"]}</span>'
                f'</div>'
            )

    if today_followups:
        items.append(f'<div style="color:{OCEAN};font-size:0.75rem;font-weight:600;margin:0.6rem 0 0.4rem">TODAY\'S FOLLOW-UPS ({len(today_followups)})</div>')
        for f in today_followups:
            name = f"{f['first_name']} {f['last_name']}"
            company = f" ({f['company']})" if f.get("company") else ""
            action = f.get("follow_up_action") or "Follow up"
            items.append(
                f'<div style="padding:0.3rem 0;border-bottom:1px solid rgba(30,51,80,0.3);font-size:0.82rem">'
                f'<span style="font-weight:600">{name}</span>{company}'
                f'<span style="color:{MUTED};font-size:0.75rem;margin-left:0.5rem">{action}</span>'
                f'</div>'
            )

    return f"""
    <div class="section">
        <h2>Relationship Follow-ups</h2>
        {"".join(items)}
    </div>"""


def format_stale_vips_html(stale: list) -> str:
    """Format stale VIP contacts as HTML."""
    if not stale:
        return ""

    items = []
    for s in stale:
        name = f"{s['first_name']} {s['last_name']}"
        company = f" ({s['company']})" if s.get("company") else ""
        last = s.get("last_contact_date") or "never"
        items.append(
            f'<div style="display:flex;justify-content:space-between;padding:0.3rem 0;border-bottom:1px solid rgba(30,51,80,0.3);font-size:0.82rem">'
            f'<span>{name}{company}</span>'
            f'<span style="color:{DUSK};font-family:Source Code Pro,monospace;font-size:0.72rem">last: {last}</span>'
            f'</div>'
        )

    return f"""
    <div class="section">
        <h2>Stale VIP Contacts</h2>
        <div style="font-size:0.72rem;color:{MUTED};margin-bottom:0.5rem">No interaction in 30+ days</div>
        {"".join(items)}
    </div>"""


# ============================================================
# MAIN ENTRY POINT (for morning brief integration)
# ============================================================

def get_all_brief_sections() -> str:
    """Generate all task/content/CRM HTML sections for the morning brief."""
    html_parts = []

    # Tasks
    today = get_todays_tasks()
    overdue = get_overdue_tasks()
    upcoming = get_upcoming_tasks()
    tasks_html = format_tasks_html(today, overdue, upcoming)
    if tasks_html:
        html_parts.append(tasks_html)

    # Content calendar
    content = get_upcoming_content()
    content_html = format_content_html(content)
    if content_html:
        html_parts.append(content_html)

    # CRM follow-ups
    today_fu = get_todays_followups()
    overdue_fu = get_overdue_followups()
    followups_html = format_followups_html(today_fu, overdue_fu)
    if followups_html:
        html_parts.append(followups_html)

    # Stale VIPs
    stale = get_stale_vips()
    stale_html = format_stale_vips_html(stale)
    if stale_html:
        html_parts.append(stale_html)

    return "\n".join(html_parts)
