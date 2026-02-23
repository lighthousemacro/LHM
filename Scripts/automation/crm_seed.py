#!/usr/bin/env python3
"""
LIGHTHOUSE MACRO - CRM SEED DATA
==================================
Seeds the CRM database with known contacts and pipeline entries.
Idempotent: skips if contacts already exist.
"""

import sqlite3
from pathlib import Path

DB_PATH = Path("/Users/bob/LHM/Data/databases/lhm_contacts.db")

SEED_CONTACTS = [
    {
        "first_name": "Pascal", "last_name": "Hugli",
        "email": None, "company": "Maerki Baumann",
        "title": "Investment Manager",
        "category": "podcast_host", "tier": "vip", "source": "inbound",
        "twitter_handle": None,
        "notes": "Host of 'Less Noise More Signal'. Bob appeared Oct 2025. Liquidity episode planned. LHM recommended on his Substack. Built CLI for his report.",
    },
    {
        "first_name": "Tania", "last_name": "Reif",
        "email": None, "company": "Senda Digital Assets",
        "title": "Founder & CIO",
        "category": "trial_client", "tier": "vip", "source": "podcast",
        "twitter_handle": None,
        "notes": "PhD Columbia, ex-Soros/Citadel/IMF. Heard Bob on Pascal's podcast. ~3 month trial phase. Q1 formalization pending.",
    },
    {
        "first_name": "Christopher", "last_name": "King",
        "email": None, "company": "Theo Advisors",
        "title": "Principal",
        "category": "partner", "tier": "vip", "source": "referral",
        "twitter_handle": None,
        "notes": "5+ ventures. Wants Bob as macro/data layer across his businesses. Last contact early Feb 2026, gone quiet.",
    },
    {
        "first_name": "Tim", "last_name": "Pierotti",
        "email": None, "company": "WealthVest",
        "title": "CIO",
        "category": "podcast_host", "tier": "vip", "source": "substack",
        "twitter_handle": None,
        "notes": "BC connection. Podcast Feb 24/25. Explicitly helping Bob build profile. Engaged with Labor and Prices edu posts.",
    },
    {
        "first_name": "Michael", "last_name": "Nadeau",
        "email": None, "company": "The DeFi Report",
        "title": "Founder",
        "category": "partner", "tier": "standard", "source": "inbound",
        "twitter_handle": None,
        "notes": "Introductory call went well. Complementary: Bob top-down macro, Nadeau bottom-up DeFi.",
    },
    {
        "first_name": "Josh", "last_name": "Giordano",
        "email": None, "company": None,
        "title": None,
        "category": "founding_member", "tier": "vip", "source": "inbound",
        "twitter_handle": None,
        "notes": "$400/year locked for life. Wants MRI signal history for overlay with his own indicator.",
    },
    {
        "first_name": "Ryan", "last_name": "Salah",
        "email": None, "company": None,
        "title": None,
        "category": "founding_member", "tier": "vip", "source": "inbound",
        "twitter_handle": None,
        "notes": "$400/year locked for life.",
    },
    {
        "first_name": "Michael", "last_name": "Zhang",
        "email": None, "company": None,
        "title": None,
        "category": "founding_member", "tier": "vip", "source": "inbound",
        "twitter_handle": None,
        "notes": "$300/year locked for life.",
    },
    {
        "first_name": "Rob", "last_name": "Farenden",
        "email": None, "company": "F&L Search",
        "title": "Recruiter",
        "category": "recruiter", "tier": "standard", "source": "inbound",
        "twitter_handle": None,
        "notes": "Has client adding crypto to traditional cap markets research. Bob open to consulting/outsourced, not full-time.",
    },
]

SEED_PIPELINE = [
    # Tania Reif - trial client
    {"contact_last_name": "Reif", "stage": "trial", "opportunity_type": "advisory", "estimated_value": None, "notes": "~3 month trial phase"},
    # Christopher King - partnership
    {"contact_last_name": "King", "stage": "engaged", "opportunity_type": "consulting", "estimated_value": None, "notes": "Macro/data layer across his businesses"},
]


def seed():
    conn = sqlite3.connect(DB_PATH)

    # Check if already seeded
    count = conn.execute("SELECT COUNT(*) FROM contacts").fetchone()[0]
    if count > 0:
        print(f"  CRM already has {count} contacts. Skipping seed.")
        conn.close()
        return

    # Insert contacts
    for c in SEED_CONTACTS:
        conn.execute(
            "INSERT INTO contacts (first_name, last_name, email, company, title, category, tier, source, twitter_handle, notes) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (c["first_name"], c["last_name"], c.get("email"), c.get("company"),
             c.get("title"), c["category"], c["tier"], c["source"],
             c.get("twitter_handle"), c.get("notes")),
        )
    conn.commit()

    # Insert pipeline entries
    for p in SEED_PIPELINE:
        contact = conn.execute(
            "SELECT id FROM contacts WHERE last_name = ?", (p["contact_last_name"],)
        ).fetchone()
        if contact:
            conn.execute(
                "INSERT INTO pipeline (contact_id, stage, opportunity_type, estimated_value, notes) "
                "VALUES (?, ?, ?, ?, ?)",
                (contact[0], p["stage"], p["opportunity_type"], p.get("estimated_value"), p.get("notes")),
            )
    conn.commit()

    total = conn.execute("SELECT COUNT(*) FROM contacts").fetchone()[0]
    pipeline_count = conn.execute("SELECT COUNT(*) FROM pipeline").fetchone()[0]
    print(f"  Seeded {total} contacts and {pipeline_count} pipeline entries.")
    conn.close()


if __name__ == "__main__":
    # Make sure DB and tables exist first
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from lhm_crm import init_db
    init_db()
    seed()
