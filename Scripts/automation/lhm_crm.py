#!/usr/bin/env python3
"""
LIGHTHOUSE MACRO - CRM CLI
============================
Contact management, interaction logging, and pipeline tracking.

Usage:
    lhm-crm add "Jane Smith" --email jane@fund.com --company "Acme Capital" --category prospect
    lhm-crm search "pascal"
    lhm-crm show 1                          # Full contact + history
    lhm-crm list                             # All active contacts
    lhm-crm list --category client --tier vip

    lhm-crm log 1 --type email_sent --summary "Sent research sample"
    lhm-crm log 1 --type call --summary "Discussed podcast" --followup 2026-02-25 "Send outline"

    lhm-crm followups                        # Today's follow-ups
    lhm-crm overdue                          # Overdue follow-ups
    lhm-crm stale                            # VIPs with no contact in 30+ days

    lhm-crm pipeline                         # Pipeline summary
    lhm-crm pipeline add 2 --type advisory --stage trial --value 5000
    lhm-crm pipeline advance 1              # Move to next stage
"""

import argparse
import sqlite3
import sys
from datetime import datetime, date, timedelta
from pathlib import Path

DB_PATH = Path("/Users/bob/LHM/Data/databases/lhm_contacts.db")

CATEGORIES = ["client", "trial_client", "founding_member", "prospect", "podcast_host", "partner", "recruiter", "press", "other"]
TIERS = ["vip", "standard", "cold"]
SOURCES = ["inbound", "referral", "podcast", "twitter", "substack", "cold_outreach", "conference"]
INTERACTION_TYPES = ["email_sent", "email_received", "call", "meeting", "twitter_dm", "podcast", "coffee", "conference", "note"]
PIPELINE_STAGES = ["awareness", "engaged", "pitch", "trial", "negotiation", "closed_won", "closed_lost"]
OPP_TYPES = ["subscription", "advisory", "consulting", "podcast", "partnership"]

# Colors
OCEAN = "\033[96m"
DUSK = "\033[93m"
VENUS = "\033[91m"
SEA = "\033[92m"
MUTED = "\033[90m"
BOLD = "\033[1m"
RESET = "\033[0m"


def init_db():
    """Create tables if they don't exist."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            company TEXT,
            title TEXT,
            category TEXT DEFAULT 'prospect',
            tier TEXT DEFAULT 'standard',
            source TEXT,
            twitter_handle TEXT,
            notes TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            last_contact_date TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contact_id INTEGER NOT NULL REFERENCES contacts(id),
            interaction_type TEXT NOT NULL,
            direction TEXT,
            summary TEXT,
            interaction_date TEXT DEFAULT (date('now')),
            follow_up_date TEXT,
            follow_up_action TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS pipeline (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contact_id INTEGER NOT NULL REFERENCES contacts(id),
            stage TEXT DEFAULT 'awareness',
            opportunity_type TEXT,
            estimated_value REAL,
            stage_entered_date TEXT DEFAULT (date('now')),
            expected_close_date TEXT,
            notes TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_contacts_email ON contacts(email)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_contacts_category ON contacts(category)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_interactions_contact ON interactions(contact_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_interactions_followup ON interactions(follow_up_date)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_pipeline_stage ON pipeline(stage)")
    conn.commit()
    return conn


# ============================================================
# DISPLAY
# ============================================================

def _tier_badge(tier: str) -> str:
    if tier == "vip":
        return f"{DUSK}VIP{RESET}"
    return f"{MUTED}{tier}{RESET}"


def _category_badge(cat: str) -> str:
    colors = {"client": SEA, "trial_client": OCEAN, "founding_member": SEA,
              "prospect": MUTED, "podcast_host": DUSK, "partner": OCEAN}
    color = colors.get(cat, MUTED)
    return f"{color}{cat}{RESET}"


def print_contact_row(c: dict):
    name = f"{c['first_name']} {c['last_name']}"
    company = f" @ {c['company']}" if c.get('company') else ""
    tier = _tier_badge(c.get('tier', 'standard'))
    cat = _category_badge(c.get('category', 'other'))
    last = c.get('last_contact_date') or 'never'
    print(f"  [{c['id']:>3}] {BOLD}{name}{RESET}{company}")
    print(f"        {cat}  {tier}  last: {MUTED}{last}{RESET}")


def print_contact_detail(c: dict, interactions: list, pipeline: list):
    name = f"{c['first_name']} {c['last_name']}"
    print(f"\n  {BOLD}{OCEAN}{'=' * 50}{RESET}")
    print(f"  {BOLD}{name}{RESET}")
    if c.get('title'):
        print(f"  {c['title']}")
    if c.get('company'):
        print(f"  {c['company']}")
    print(f"  {BOLD}{'=' * 50}{RESET}")
    print()

    details = []
    if c.get('email'):
        details.append(f"  Email:    {c['email']}")
    if c.get('phone'):
        details.append(f"  Phone:    {c['phone']}")
    if c.get('twitter_handle'):
        details.append(f"  Twitter:  {c['twitter_handle']}")
    details.append(f"  Category: {_category_badge(c.get('category', 'other'))}")
    details.append(f"  Tier:     {_tier_badge(c.get('tier', 'standard'))}")
    details.append(f"  Source:   {c.get('source') or 'unknown'}")
    details.append(f"  Added:    {c.get('created_at', '')[:10]}")
    details.append(f"  Last:     {c.get('last_contact_date') or 'never'}")
    if c.get('notes'):
        details.append(f"  Notes:    {c['notes']}")
    print("\n".join(details))

    if pipeline:
        print(f"\n  {OCEAN}PIPELINE{RESET}")
        for p in pipeline:
            val_str = f"${p['estimated_value']:,.0f}" if p.get('estimated_value') else "n/a"
            print(f"    {p['stage']:<15} {p.get('opportunity_type', ''):<15} {val_str}")

    if interactions:
        print(f"\n  {OCEAN}INTERACTIONS{RESET}")
        for i in interactions[:10]:
            direction = f"{'>' if i.get('direction') == 'outbound' else '<'}" if i.get('direction') else " "
            fu = f" {DUSK}follow up: {i['follow_up_date']}{RESET}" if i.get('follow_up_date') else ""
            print(f"    {i['interaction_date']}  {direction} {i['interaction_type']:<15} {i.get('summary', '')[:60]}{fu}")
    print()


# ============================================================
# COMMANDS
# ============================================================

def cmd_add(args, conn):
    # Parse "First Last" from name
    parts = args.name.strip().split(None, 1)
    first = parts[0]
    last = parts[1] if len(parts) > 1 else ""

    conn.execute(
        "INSERT INTO contacts (first_name, last_name, email, phone, company, title, category, tier, source, twitter_handle, notes) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (first, last, args.email, args.phone, args.company, args.title,
         args.category, args.tier, args.source, args.twitter, args.notes),
    )
    conn.commit()
    cid = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    print(f"  Contact #{cid} created: {first} {last}")


def cmd_search(args, conn):
    conn.row_factory = sqlite3.Row
    query = "%" + args.query + "%"
    rows = conn.execute(
        "SELECT * FROM contacts WHERE first_name LIKE ? OR last_name LIKE ? OR company LIKE ? OR email LIKE ?",
        (query, query, query, query),
    ).fetchall()
    if not rows:
        print(f"  No contacts matching '{args.query}'")
        return
    print(f"\n  {len(rows)} result(s)")
    for r in rows:
        print_contact_row(dict(r))


def cmd_show(args, conn):
    conn.row_factory = sqlite3.Row
    c = conn.execute("SELECT * FROM contacts WHERE id = ?", (args.contact_id,)).fetchone()
    if not c:
        print(f"  Contact #{args.contact_id} not found.")
        return
    interactions = conn.execute(
        "SELECT * FROM interactions WHERE contact_id = ? ORDER BY interaction_date DESC",
        (args.contact_id,),
    ).fetchall()
    pipeline = conn.execute(
        "SELECT * FROM pipeline WHERE contact_id = ? ORDER BY created_at DESC",
        (args.contact_id,),
    ).fetchall()
    print_contact_detail(dict(c), [dict(i) for i in interactions], [dict(p) for p in pipeline])


def cmd_list(args, conn):
    conn.row_factory = sqlite3.Row
    query = "SELECT * FROM contacts WHERE 1=1"
    params = []
    if args.category:
        query += " AND category = ?"
        params.append(args.category)
    if args.tier:
        query += " AND tier = ?"
        params.append(args.tier)
    query += " ORDER BY tier DESC, last_contact_date DESC NULLS LAST"
    rows = conn.execute(query, params).fetchall()
    print(f"\n  {len(rows)} contact(s)")
    for r in rows:
        print_contact_row(dict(r))
    print()


def cmd_log(args, conn):
    direction = "outbound" if args.type in ("email_sent", "note") else "inbound" if args.type == "email_received" else None
    follow_up_date = None
    follow_up_action = None
    if args.followup:
        follow_up_date = args.followup[0]
        follow_up_action = args.followup[1] if len(args.followup) > 1 else "Follow up"

    conn.execute(
        "INSERT INTO interactions (contact_id, interaction_type, direction, summary, follow_up_date, follow_up_action) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (args.contact_id, args.type, direction, args.summary, follow_up_date, follow_up_action),
    )
    # Update last_contact_date
    conn.execute(
        "UPDATE contacts SET last_contact_date = ? WHERE id = ?",
        (date.today().isoformat(), args.contact_id),
    )
    conn.commit()
    print(f"  Interaction logged for contact #{args.contact_id}: {args.type}")
    if follow_up_date:
        print(f"  Follow-up: {follow_up_date} - {follow_up_action}")


def cmd_followups(args, conn):
    conn.row_factory = sqlite3.Row
    today = date.today().isoformat()
    rows = conn.execute("""
        SELECT i.*, c.first_name, c.last_name, c.company
        FROM interactions i
        JOIN contacts c ON i.contact_id = c.id
        WHERE i.follow_up_date = ?
        ORDER BY i.id
    """, (today,)).fetchall()
    print(f"\n  TODAY'S FOLLOW-UPS ({len(rows)})")
    print(f"  {'=' * 50}")
    if not rows:
        print("  None due today.")
    for r in rows:
        r = dict(r)
        name = f"{r['first_name']} {r['last_name']}"
        company = f" ({r['company']})" if r.get('company') else ""
        action = r.get('follow_up_action') or "Follow up"
        print(f"  {BOLD}{name}{RESET}{company}")
        print(f"    {action}")
        if r.get('summary'):
            print(f"    {MUTED}Context: {r['summary'][:70]}{RESET}")
        print()


def cmd_overdue(args, conn):
    conn.row_factory = sqlite3.Row
    today = date.today().isoformat()
    rows = conn.execute("""
        SELECT i.*, c.first_name, c.last_name, c.company
        FROM interactions i
        JOIN contacts c ON i.contact_id = c.id
        WHERE i.follow_up_date < ? AND i.follow_up_date IS NOT NULL
        ORDER BY i.follow_up_date
    """, (today,)).fetchall()
    print(f"\n  OVERDUE FOLLOW-UPS ({len(rows)})")
    print(f"  {'=' * 50}")
    if not rows:
        print("  None overdue.")
    for r in rows:
        r = dict(r)
        name = f"{r['first_name']} {r['last_name']}"
        company = f" ({r['company']})" if r.get('company') else ""
        action = r.get('follow_up_action') or "Follow up"
        days = (date.today() - datetime.strptime(r['follow_up_date'], "%Y-%m-%d").date()).days
        print(f"  {VENUS}{r['follow_up_date']}{RESET} ({days}d overdue)")
        print(f"    {BOLD}{name}{RESET}{company}")
        print(f"    {action}")
        print()


def cmd_stale(args, conn):
    conn.row_factory = sqlite3.Row
    days = args.days if args.days else 30
    cutoff = (date.today() - timedelta(days=days)).isoformat()
    rows = conn.execute("""
        SELECT * FROM contacts
        WHERE tier = 'vip'
          AND (last_contact_date IS NULL OR last_contact_date < ?)
        ORDER BY last_contact_date
    """, (cutoff,)).fetchall()
    print(f"\n  STALE VIP CONTACTS (>{days} days)")
    print(f"  {'=' * 50}")
    if not rows:
        print("  All VIPs recently contacted.")
    for r in rows:
        r = dict(r)
        name = f"{r['first_name']} {r['last_name']}"
        company = f" @ {r['company']}" if r.get('company') else ""
        last = r.get('last_contact_date') or 'never'
        print(f"  [{r['id']:>3}] {BOLD}{name}{RESET}{company}")
        print(f"        last contact: {DUSK}{last}{RESET}")
        print()


def cmd_pipeline(args, conn):
    conn.row_factory = sqlite3.Row
    rows = conn.execute("""
        SELECT p.*, c.first_name, c.last_name, c.company
        FROM pipeline p
        JOIN contacts c ON p.contact_id = c.id
        WHERE p.stage NOT IN ('closed_won', 'closed_lost')
        ORDER BY CASE p.stage
            WHEN 'awareness' THEN 1
            WHEN 'engaged' THEN 2
            WHEN 'pitch' THEN 3
            WHEN 'trial' THEN 4
            WHEN 'negotiation' THEN 5
        END
    """).fetchall()

    print(f"\n  PIPELINE ({len(rows)} active)")
    print(f"  {'=' * 50}")
    if not rows:
        print("  Pipeline empty.")
        return

    current_stage = None
    for r in rows:
        r = dict(r)
        if r['stage'] != current_stage:
            current_stage = r['stage']
            print(f"\n  {OCEAN}{current_stage.upper()}{RESET}")
        name = f"{r['first_name']} {r['last_name']}"
        company = f" ({r['company']})" if r.get('company') else ""
        val = f"${r['estimated_value']:,.0f}" if r.get('estimated_value') else ""
        opp = r.get('opportunity_type') or ""
        print(f"    {name}{company}  {opp}  {SEA}{val}{RESET}")
    print()


def cmd_pipeline_add(args, conn):
    conn.execute(
        "INSERT INTO pipeline (contact_id, stage, opportunity_type, estimated_value, expected_close_date) "
        "VALUES (?, ?, ?, ?, ?)",
        (args.contact_id, args.stage, args.type, args.value, args.close),
    )
    conn.commit()
    print(f"  Pipeline entry added for contact #{args.contact_id}: {args.stage}")


def cmd_pipeline_advance(args, conn):
    current = conn.execute(
        "SELECT stage FROM pipeline WHERE id = ?", (args.pipeline_id,)
    ).fetchone()
    if not current:
        print(f"  Pipeline entry #{args.pipeline_id} not found.")
        return
    current_stage = current[0]
    try:
        idx = PIPELINE_STAGES.index(current_stage)
        next_stage = PIPELINE_STAGES[idx + 1]
    except (ValueError, IndexError):
        print(f"  Cannot advance from '{current_stage}'.")
        return
    conn.execute(
        "UPDATE pipeline SET stage = ?, stage_entered_date = ?, updated_at = ? WHERE id = ?",
        (next_stage, date.today().isoformat(), datetime.now().isoformat(), args.pipeline_id),
    )
    conn.commit()
    print(f"  Pipeline #{args.pipeline_id}: {current_stage} -> {next_stage}")


def cmd_edit(args, conn):
    updates = []
    params = []
    for field in ["email", "phone", "company", "title", "category", "tier", "source", "twitter", "notes"]:
        val = getattr(args, field, None)
        if val is not None:
            db_field = "twitter_handle" if field == "twitter" else field
            updates.append(f"{db_field} = ?")
            params.append(val)
    if not updates:
        print("  Nothing to update.")
        return
    params.append(args.contact_id)
    conn.execute(f"UPDATE contacts SET {', '.join(updates)} WHERE id = ?", params)
    conn.commit()
    print(f"  Contact #{args.contact_id} updated.")


# ============================================================
# MAIN
# ============================================================

def main():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = init_db()

    parser = argparse.ArgumentParser(prog="lhm-crm", description="Lighthouse Macro CRM")
    sub = parser.add_subparsers(dest="command")

    # add
    p_add = sub.add_parser("add", help="Add contact")
    p_add.add_argument("name", help='"First Last"')
    p_add.add_argument("--email", "-e")
    p_add.add_argument("--phone")
    p_add.add_argument("--company")
    p_add.add_argument("--title")
    p_add.add_argument("--category", "-c", choices=CATEGORIES, default="prospect")
    p_add.add_argument("--tier", "-t", choices=TIERS, default="standard")
    p_add.add_argument("--source", "-s", choices=SOURCES)
    p_add.add_argument("--twitter")
    p_add.add_argument("--notes", "-n")

    # search
    p_search = sub.add_parser("search", aliases=["find"], help="Search contacts")
    p_search.add_argument("query")

    # show
    p_show = sub.add_parser("show", help="Show contact detail")
    p_show.add_argument("contact_id", type=int)

    # list
    p_list = sub.add_parser("list", aliases=["ls"], help="List contacts")
    p_list.add_argument("--category", "-c", choices=CATEGORIES)
    p_list.add_argument("--tier", "-t", choices=TIERS)

    # edit
    p_edit = sub.add_parser("edit", help="Edit contact")
    p_edit.add_argument("contact_id", type=int)
    p_edit.add_argument("--email", "-e")
    p_edit.add_argument("--phone")
    p_edit.add_argument("--company")
    p_edit.add_argument("--title")
    p_edit.add_argument("--category", "-c", choices=CATEGORIES)
    p_edit.add_argument("--tier", "-t", choices=TIERS)
    p_edit.add_argument("--source", "-s", choices=SOURCES)
    p_edit.add_argument("--twitter")
    p_edit.add_argument("--notes", "-n")

    # log
    p_log = sub.add_parser("log", help="Log interaction")
    p_log.add_argument("contact_id", type=int)
    p_log.add_argument("--type", required=True, choices=INTERACTION_TYPES)
    p_log.add_argument("--summary", required=True)
    p_log.add_argument("--followup", nargs="+", metavar=("DATE", "ACTION"), help="YYYY-MM-DD [action text]")

    # followups
    sub.add_parser("followups", aliases=["fu"], help="Today's follow-ups")

    # overdue
    sub.add_parser("overdue", help="Overdue follow-ups")

    # stale
    p_stale = sub.add_parser("stale", help="Stale VIP contacts")
    p_stale.add_argument("--days", type=int, default=30)

    # pipeline
    p_pipe = sub.add_parser("pipeline", aliases=["pipe"], help="Pipeline view")
    pipe_sub = p_pipe.add_subparsers(dest="pipe_command")

    p_pipe_add = pipe_sub.add_parser("add", help="Add pipeline entry")
    p_pipe_add.add_argument("contact_id", type=int)
    p_pipe_add.add_argument("--type", choices=OPP_TYPES)
    p_pipe_add.add_argument("--stage", choices=PIPELINE_STAGES, default="awareness")
    p_pipe_add.add_argument("--value", type=float)
    p_pipe_add.add_argument("--close", help="Expected close date YYYY-MM-DD")

    p_pipe_adv = pipe_sub.add_parser("advance", help="Advance pipeline stage")
    p_pipe_adv.add_argument("pipeline_id", type=int)

    args = parser.parse_args()

    if not args.command:
        cmd_list(argparse.Namespace(category=None, tier=None), conn)
    elif args.command == "add":
        cmd_add(args, conn)
    elif args.command in ("search", "find"):
        cmd_search(args, conn)
    elif args.command == "show":
        cmd_show(args, conn)
    elif args.command in ("list", "ls"):
        cmd_list(args, conn)
    elif args.command == "edit":
        cmd_edit(args, conn)
    elif args.command == "log":
        cmd_log(args, conn)
    elif args.command in ("followups", "fu"):
        cmd_followups(args, conn)
    elif args.command == "overdue":
        cmd_overdue(args, conn)
    elif args.command == "stale":
        cmd_stale(args, conn)
    elif args.command in ("pipeline", "pipe"):
        if hasattr(args, "pipe_command") and args.pipe_command == "add":
            cmd_pipeline_add(args, conn)
        elif hasattr(args, "pipe_command") and args.pipe_command == "advance":
            cmd_pipeline_advance(args, conn)
        else:
            cmd_pipeline(args, conn)

    conn.close()


if __name__ == "__main__":
    main()
