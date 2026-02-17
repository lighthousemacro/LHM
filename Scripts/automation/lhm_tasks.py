#!/usr/bin/env python3
"""
LIGHTHOUSE MACRO - TASK & CONTENT CALENDAR CLI
===============================================
Simple task management and content calendar tracking.

Usage:
    lhm-task add "Follow up with Pascal" --due 2026-02-20 --category follow_up
    lhm-task list                    # Open tasks sorted by due date
    lhm-task list --today            # Due today
    lhm-task list --overdue          # Past due
    lhm-task list --category content # Filter by category
    lhm-task done 5                  # Mark task #5 complete
    lhm-task defer 3 --to 2026-02-25 # Push due date
    lhm-task edit 3 --title "New title" --priority 1
    lhm-task delete 3                # Remove task

    lhm-task content                 # Show content calendar
    lhm-task content update 3 --status drafting
"""

import argparse
import sqlite3
import sys
from datetime import datetime, date
from pathlib import Path

DB_PATH = Path("/Users/bob/LHM/Data/databases/lhm_tasks.db")

CATEGORIES = ["general", "follow_up", "content", "research", "outreach", "admin"]
STATUSES = ["open", "in_progress", "done", "deferred"]
PRIORITIES = {1: "URGENT", 2: "HIGH", 3: "NORMAL", 4: "LOW"}
CONTENT_TYPES = ["beacon", "beam", "note", "chartbook", "horizon", "edu_series"]
CONTENT_STATUSES = ["planned", "drafting", "charts_done", "review", "published"]


def init_db():
    """Create tables if they don't exist."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            category TEXT NOT NULL DEFAULT 'general',
            priority INTEGER DEFAULT 3,
            status TEXT NOT NULL DEFAULT 'open',
            due_date TEXT,
            contact_id INTEGER,
            created_at TEXT DEFAULT (datetime('now')),
            completed_at TEXT,
            notes TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS content_calendar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content_type TEXT NOT NULL,
            title TEXT NOT NULL,
            pillar INTEGER,
            status TEXT DEFAULT 'planned',
            planned_date TEXT,
            published_date TEXT,
            notes TEXT
        )
    """)
    conn.commit()
    return conn


def seed_content_calendar(conn):
    """Seed content calendar with edu series posts (idempotent)."""
    cursor = conn.execute("SELECT COUNT(*) FROM content_calendar WHERE content_type = 'edu_series'")
    if cursor.fetchone()[0] > 0:
        return  # Already seeded

    posts = [
        (1, "Labor: The Source Code", "published", "2026-01-27"),
        (2, "Prices: The Transmission Belt", "published", "2026-02-02"),
        (3, "Growth: The Second Derivative", "published", "2026-02-05"),
        (5, "Consumer: The Last Domino", "published", "2026-02-11"),
        (4, "Housing: The Collateral Engine", "published", "2026-02-16"),
        (6, "Business: TBD", "planned", None),
        (7, "Trade: TBD", "planned", None),
        (8, "Government: TBD", "planned", None),
        (9, "Financial: TBD", "planned", None),
        (10, "Plumbing: TBD", "planned", None),
        (11, "Market Structure: TBD", "planned", None),
        (12, "Sentiment: TBD", "planned", None),
    ]
    for pillar, title, status, pub_date in posts:
        conn.execute(
            "INSERT INTO content_calendar (content_type, title, pillar, status, published_date) VALUES (?, ?, ?, ?, ?)",
            ("edu_series", title, pillar, status, pub_date),
        )
    conn.commit()
    print("Content calendar seeded with 12 edu series posts.")


# ============================================================
# DISPLAY HELPERS
# ============================================================

def _priority_str(p: int) -> str:
    label = PRIORITIES.get(p, "?")
    if p == 1:
        return f"\033[91m{label}\033[0m"  # Red
    elif p == 2:
        return f"\033[93m{label}\033[0m"  # Yellow
    return label


def _due_str(due: str) -> str:
    if not due:
        return "no date"
    try:
        d = datetime.strptime(due, "%Y-%m-%d").date()
        today = date.today()
        delta = (d - today).days
        if delta < 0:
            return f"\033[91m{due} (OVERDUE {abs(delta)}d)\033[0m"
        elif delta == 0:
            return f"\033[93m{due} (TODAY)\033[0m"
        elif delta <= 3:
            return f"\033[93m{due} ({delta}d)\033[0m"
        return f"{due} ({delta}d)"
    except ValueError:
        return due


def print_tasks(tasks: list):
    if not tasks:
        print("  No tasks found.")
        return
    for t in tasks:
        tid, title, cat, pri, status, due, notes = t
        print(f"  [{tid:>3}] {_priority_str(pri):>8}  {title}")
        print(f"        {cat:<12} due: {_due_str(due)}  [{status}]")
        if notes:
            print(f"        note: {notes[:80]}")
        print()


def print_content(items: list):
    if not items:
        print("  No content items found.")
        return
    for c in items:
        cid, ctype, title, pillar, status, planned, published, notes = c
        pillar_str = f"P{pillar}" if pillar else "  "
        status_color = "\033[92m" if status == "published" else "\033[93m" if status in ("drafting", "charts_done", "review") else "\033[0m"
        date_str = published or planned or "no date"
        print(f"  [{cid:>2}] {pillar_str}  {status_color}{status:<12}\033[0m {title}")
        if notes:
            print(f"                        {notes[:60]}")
    print()


# ============================================================
# COMMANDS
# ============================================================

def cmd_add(args, conn):
    due = args.due if args.due else None
    priority = args.priority if args.priority else 3
    category = args.category if args.category else "general"
    notes = args.notes if args.notes else None

    if category not in CATEGORIES:
        print(f"Invalid category. Choose from: {', '.join(CATEGORIES)}")
        return

    conn.execute(
        "INSERT INTO tasks (title, category, priority, due_date, notes) VALUES (?, ?, ?, ?, ?)",
        (args.title, category, priority, due, notes),
    )
    conn.commit()
    tid = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    print(f"  Task #{tid} created: {args.title}")
    if due:
        print(f"  Due: {due}")


def cmd_list(args, conn):
    query = "SELECT id, title, category, priority, status, due_date, notes FROM tasks WHERE status NOT IN ('done')"
    params = []

    if args.today:
        query += " AND due_date = ?"
        params.append(date.today().isoformat())
    elif args.overdue:
        query += " AND due_date < ? AND due_date IS NOT NULL"
        params.append(date.today().isoformat())

    if args.category:
        query += " AND category = ?"
        params.append(args.category)

    if args.all:
        # Override: show everything including done
        query = "SELECT id, title, category, priority, status, due_date, notes FROM tasks"
        if args.category:
            query += " WHERE category = ?"
            params = [args.category]

    query += " ORDER BY CASE WHEN due_date IS NULL THEN 1 ELSE 0 END, due_date, priority"
    tasks = conn.execute(query, params).fetchall()

    header = "ALL TASKS" if args.all else "TODAY" if args.today else "OVERDUE" if args.overdue else "OPEN TASKS"
    print(f"\n  {header}")
    print(f"  {'=' * 50}")
    print_tasks(tasks)


def cmd_done(args, conn):
    conn.execute(
        "UPDATE tasks SET status = 'done', completed_at = ? WHERE id = ?",
        (datetime.now().isoformat(), args.task_id),
    )
    conn.commit()
    print(f"  Task #{args.task_id} marked done.")


def cmd_defer(args, conn):
    conn.execute(
        "UPDATE tasks SET due_date = ?, status = 'deferred' WHERE id = ?",
        (args.to, args.task_id),
    )
    conn.commit()
    print(f"  Task #{args.task_id} deferred to {args.to}.")


def cmd_edit(args, conn):
    updates = []
    params = []
    if args.title:
        updates.append("title = ?")
        params.append(args.title)
    if args.priority:
        updates.append("priority = ?")
        params.append(args.priority)
    if args.category:
        updates.append("category = ?")
        params.append(args.category)
    if args.due:
        updates.append("due_date = ?")
        params.append(args.due)
    if args.notes:
        updates.append("notes = ?")
        params.append(args.notes)
    if args.status:
        updates.append("status = ?")
        params.append(args.status)

    if not updates:
        print("  Nothing to update. Use --title, --priority, --category, --due, --notes, or --status.")
        return

    params.append(args.task_id)
    conn.execute(f"UPDATE tasks SET {', '.join(updates)} WHERE id = ?", params)
    conn.commit()
    print(f"  Task #{args.task_id} updated.")


def cmd_delete(args, conn):
    conn.execute("DELETE FROM tasks WHERE id = ?", (args.task_id,))
    conn.commit()
    print(f"  Task #{args.task_id} deleted.")


def cmd_content(args, conn):
    query = "SELECT id, content_type, title, pillar, status, planned_date, published_date, notes FROM content_calendar"
    params = []
    if args.status:
        query += " WHERE status = ?"
        params.append(args.status)
    query += " ORDER BY COALESCE(pillar, 99), id"
    items = conn.execute(query, params).fetchall()
    print(f"\n  CONTENT CALENDAR")
    print(f"  {'=' * 50}")
    print_content(items)


def cmd_content_update(args, conn):
    updates = []
    params = []
    if args.status:
        updates.append("status = ?")
        params.append(args.status)
        if args.status == "published":
            updates.append("published_date = ?")
            params.append(date.today().isoformat())
    if args.title:
        updates.append("title = ?")
        params.append(args.title)
    if args.planned:
        updates.append("planned_date = ?")
        params.append(args.planned)
    if args.notes:
        updates.append("notes = ?")
        params.append(args.notes)

    if not updates:
        print("  Nothing to update.")
        return

    params.append(args.content_id)
    conn.execute(f"UPDATE content_calendar SET {', '.join(updates)} WHERE id = ?", params)
    conn.commit()
    print(f"  Content #{args.content_id} updated.")


# ============================================================
# MAIN
# ============================================================

def main():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = init_db()
    seed_content_calendar(conn)

    parser = argparse.ArgumentParser(
        prog="lhm-task",
        description="Lighthouse Macro Task Manager",
    )
    sub = parser.add_subparsers(dest="command")

    # add
    p_add = sub.add_parser("add", help="Add a new task")
    p_add.add_argument("title", help="Task title")
    p_add.add_argument("--due", help="Due date (YYYY-MM-DD)")
    p_add.add_argument("--category", "-c", choices=CATEGORIES, default="general")
    p_add.add_argument("--priority", "-p", type=int, choices=[1, 2, 3, 4], default=3)
    p_add.add_argument("--notes", "-n", help="Additional notes")

    # list
    p_list = sub.add_parser("list", aliases=["ls"], help="List tasks")
    p_list.add_argument("--today", "-t", action="store_true")
    p_list.add_argument("--overdue", "-o", action="store_true")
    p_list.add_argument("--category", "-c", choices=CATEGORIES)
    p_list.add_argument("--all", "-a", action="store_true", help="Include completed")

    # done
    p_done = sub.add_parser("done", help="Mark task complete")
    p_done.add_argument("task_id", type=int)

    # defer
    p_defer = sub.add_parser("defer", help="Defer task to new date")
    p_defer.add_argument("task_id", type=int)
    p_defer.add_argument("--to", required=True, help="New due date (YYYY-MM-DD)")

    # edit
    p_edit = sub.add_parser("edit", help="Edit a task")
    p_edit.add_argument("task_id", type=int)
    p_edit.add_argument("--title")
    p_edit.add_argument("--priority", "-p", type=int, choices=[1, 2, 3, 4])
    p_edit.add_argument("--category", "-c", choices=CATEGORIES)
    p_edit.add_argument("--due")
    p_edit.add_argument("--notes", "-n")
    p_edit.add_argument("--status", choices=STATUSES)

    # delete
    p_del = sub.add_parser("delete", aliases=["rm"], help="Delete a task")
    p_del.add_argument("task_id", type=int)

    # content
    p_content = sub.add_parser("content", aliases=["cal"], help="Show content calendar")
    p_content.add_argument("--status", choices=CONTENT_STATUSES)
    content_sub = p_content.add_subparsers(dest="content_command")

    # content update
    p_cupdate = content_sub.add_parser("update", help="Update content item")
    p_cupdate.add_argument("content_id", type=int)
    p_cupdate.add_argument("--status", choices=CONTENT_STATUSES)
    p_cupdate.add_argument("--title")
    p_cupdate.add_argument("--planned", help="Planned date (YYYY-MM-DD)")
    p_cupdate.add_argument("--notes", "-n")

    args = parser.parse_args()

    if not args.command:
        # Default: show open tasks
        args.command = "list"
        args.today = False
        args.overdue = False
        args.category = None
        args.all = False

    if args.command in ("list", "ls"):
        cmd_list(args, conn)
    elif args.command == "add":
        cmd_add(args, conn)
    elif args.command == "done":
        cmd_done(args, conn)
    elif args.command == "defer":
        cmd_defer(args, conn)
    elif args.command == "edit":
        cmd_edit(args, conn)
    elif args.command in ("delete", "rm"):
        cmd_delete(args, conn)
    elif args.command in ("content", "cal"):
        if hasattr(args, "content_command") and args.content_command == "update":
            cmd_content_update(args, conn)
        else:
            cmd_content(args, conn)

    conn.close()


if __name__ == "__main__":
    main()
