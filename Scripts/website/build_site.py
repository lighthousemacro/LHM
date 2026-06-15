#!/usr/bin/env python3
"""
build_site.py — Lighthouse Macro marketing site generator.

Renders Website/index.html from index.template.html (Jinja2), injecting:
  - The Live Dashboard (master tiles + 12-pillar grid) pulled LIVE from
    Lighthouse_Master.db (lighthouse_indices), each tile stamped with its own
    as-of date so the board self-heals as the daily pipeline refreshes.
  - The Featured Research feed pulled LIVE from the Substack RSS.

Design goal: the output is 100% static HTML (GitHub Pages serves it unchanged),
but the data layer is regenerated on every build instead of hand-edited.

The "No NaN" pact is honored literally: a missing index never renders as
"None"/"NaN" — it falls back to an em-dash placeholder and neutral tone.

Run:  python Scripts/website/build_site.py
"""
from __future__ import annotations

import sqlite3
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

# ---------------------------------------------------------------- paths
LHM_ROOT = Path("/Users/bob/LHM")
DB_PATH = LHM_ROOT / "Data" / "databases" / "Lighthouse_Master.db"
TEMPLATE_DIR = LHM_ROOT / "Scripts" / "website"
OUT_PATH = LHM_ROOT / "Website" / "index.html"
RSS_URL = "https://research.lighthousemacro.com/feed"
DASH = "—"  # em-dash placeholder used ONLY for missing data, never in copy

# ---------------------------------------------------------------- mappings
# Master tiles: (display label, index_id, value format)
MASTER = [
    ("MACRO RISK INDEX", "MRI", "signed"),
    ("RECESSION PROBABILITY", "REC_PROB", "pct"),
    ("ALLOCATION MULTIPLIER", "ALLOC_MULTIPLIER", "mult"),
    ("WARNING LEVEL", "WARNING_LEVEL", "int"),
]

# 12 pillars: (n, display name, primary composite index_id)
PILLARS = [
    (1, "Labor", "LFI"),
    (2, "Prices", "PCI"),
    (3, "Growth", "GCI"),
    (4, "Housing", "HCI"),
    (5, "Consumer", "CCI"),
    (6, "Business", "BCI"),
    (7, "Trade", "TCI"),
    (8, "Government", "FPI"),
    (9, "Financial", "FCI"),
    (10, "Plumbing", "LCI"),
    (11, "Structure", "MSI"),
    (12, "Sentiment", "SPI"),
]

# Status keyword -> tone. Checked alert -> caution -> good -> neutral.
TONE_KEYWORDS = {
    "alert": ("STRESS", "HEADWIND", "FRAGILE", "CRISIS", "RED", "PRESERVATION",
              "EXTREME", "FEAR", "WEAK", "SCARCE", "ACUTE", "PRE_CRISIS"),
    "caution": ("ELEVATED", "SLOWING", "TIGHT", "TRANSITIONAL", "LATE", "FROZEN",
                "CAUTIOUS", "RICH", "DEPLETION", "WARNING", "HIGH ACTIVITY"),
    "good": ("ON TARGET", "STRONG", "HEALTHY", "BULLISH", "EXPANSION", "LOW RISK",
             "ACCUMULATION", "NORMAL", "BALANCED", "FAIR VALUE", "GROWTH"),
}


def status_to_tone(status: str | None) -> str:
    if not status:
        return "neutral"
    s = status.upper()
    for tone in ("alert", "caution", "good"):
        if any(k in s for k in TONE_KEYWORDS[tone]):
            return tone
    return "neutral"


def fmt_value(value, kind: str) -> str:
    if value is None:
        return DASH
    try:
        v = float(value)
    except (TypeError, ValueError):
        return DASH
    if kind == "signed":
        return f"{v:+.2f}"
    if kind == "pct":
        return f"{v * 100:.1f}%"
    if kind == "mult":
        return f"{v:.2f}×"
    if kind == "int":
        return f"{int(round(v))}"
    return f"{v:.2f}"


def pretty_status(status: str | None) -> str:
    return (status or "").replace("_", " ").strip().title() if status else DASH


# ---------------------------------------------------------------- DB layer
def load_indices() -> dict[str, dict]:
    """Return {index_id: {value, status, date}} using the latest row per id."""
    if not DB_PATH.exists():
        print(f"WARN: DB not found at {DB_PATH}; dashboard will use placeholders.")
        return {}
    uri = f"file:{DB_PATH}?mode=ro"
    con = sqlite3.connect(uri, uri=True)
    try:
        rows = con.execute(
            """
            SELECT index_id, value, status, date
            FROM lighthouse_indices li
            WHERE date = (SELECT MAX(date) FROM lighthouse_indices
                          WHERE index_id = li.index_id)
            """
        ).fetchall()
    finally:
        con.close()
    return {r[0]: {"value": r[1], "status": r[2], "date": r[3]} for r in rows}


def build_dashboard(indices: dict[str, dict]) -> dict:
    master, dates = [], []
    for label, idx, kind in MASTER:
        rec = indices.get(idx, {})
        master.append({
            "label": label,
            "value": fmt_value(rec.get("value"), kind),
            "status": pretty_status(rec.get("status")),
            "tone": status_to_tone(rec.get("status")),
            "as_of": rec.get("date") or DASH,
        })
        if rec.get("date"):
            dates.append(rec["date"])

    pillars = []
    for n, name, idx in PILLARS:
        rec = indices.get(idx, {})
        pillars.append({
            "n": f"{n:02d}",
            "name": name,
            "code": idx,
            "value": fmt_value(rec.get("value"), "signed"),
            "status": (rec.get("status") or DASH).upper() if rec.get("status") else DASH,
            "tone": status_to_tone(rec.get("status")),
            "as_of": rec.get("date") or DASH,
        })
        if rec.get("date"):
            dates.append(rec["date"])

    missing = [m["label"] for m in master if m["value"] == DASH] + \
              [p["name"] for p in pillars if p["value"] == DASH]
    if missing:
        print(f"WARN: no DB reading for: {', '.join(missing)} (rendered as placeholder)")

    return {
        "master": master,
        "pillars": pillars,
        "as_of": max(dates) if dates else DASH,
    }


# ---------------------------------------------------------------- RSS layer
FALLBACK_RESEARCH = [
    {"type": "Chartbook", "date": "Jun 11, 2026", "title": "The Lighthouse Macro Chartbook",
     "dek": "June opened with the market doing the one thing it only does at turns.",
     "url": "https://research.lighthousemacro.com/p/the-lighthouse-macro-chartbook", "read": ""},
    {"type": "Beacon", "date": "Jun 10, 2026", "title": "Markets Turn in Order, and the Order Is Almost Done",
     "dek": "The yield back-up is real and it is fiscal, not a price scare.",
     "url": "https://research.lighthousemacro.com/p/markets-turn-in-order-and-the-order", "read": ""},
    {"type": "Beacon", "date": "Jun 6, 2026", "title": "Markets Turn in Order",
     "dek": "The leading reads were flashing for weeks while credit and volatility slept.",
     "url": "https://research.lighthousemacro.com/p/markets-turn-in-order", "read": ""},
]


def infer_type(title: str) -> str:
    t = (title or "").lower()
    for key, label in (("chartbook", "Chartbook"), ("beacon", "Beacon"),
                       ("beam", "Beam"), ("horizon", "Horizon"), ("note", "Note")):
        if key in t:
            return label
    return "Research"


def read_minutes(html_text: str) -> str:
    if not html_text:
        return ""
    import re
    words = len(re.sub(r"<[^>]+>", " ", html_text).split())
    return f"{max(1, round(words / 200))} min" if words > 80 else ""


def load_research(limit: int = 7) -> list[dict]:
    try:
        req = urllib.request.Request(RSS_URL, headers={"User-Agent": "LHM-site-build/1.0"})
        with urllib.request.urlopen(req, timeout=12) as resp:
            raw = resp.read()
        root = ET.fromstring(raw)
        content_ns = "{http://purl.org/rss/1.0/modules/content/}encoded"
        items = []
        for it in root.iter("item"):
            title = (it.findtext("title") or "").strip()
            link = (it.findtext("link") or "").strip()
            desc = (it.findtext("description") or "").strip()
            body = it.findtext(content_ns) or ""
            pub = it.findtext("pubDate")
            try:
                dt = parsedate_to_datetime(pub) if pub else None
                date_str = dt.strftime("%b %d, %Y") if dt else ""
            except Exception:
                date_str = ""
            import re
            dek = re.sub(r"<[^>]+>", "", desc).strip()
            dek = (dek[:140] + "…") if len(dek) > 140 else dek
            items.append({
                "type": infer_type(title),
                "date": date_str,
                "title": title,
                "dek": dek,
                "url": link,
                "read": read_minutes(body),
            })
            if len(items) >= limit:
                break
        if items:
            return items
        print("WARN: RSS returned no items; using fallback research list.")
    except Exception as e:  # noqa: BLE001
        print(f"WARN: RSS fetch failed ({e}); using fallback research list.")
    return FALLBACK_RESEARCH[:limit]


# ---------------------------------------------------------------- render
def main() -> int:
    indices = load_indices()
    dashboard = build_dashboard(indices)
    research = load_research()
    featured = research[0] if research else None
    rest = research[1:] if len(research) > 1 else []

    env = Environment(
        loader=FileSystemLoader(str(TEMPLATE_DIR)),
        autoescape=select_autoescape(["html"]),
    )
    template = env.get_template("index.template.html")
    html = template.render(
        dashboard=dashboard,
        featured=featured,
        research=rest,
        build_date=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        year=datetime.now(timezone.utc).year,
    )
    OUT_PATH.write_text(html, encoding="utf-8")
    print(f"OK: wrote {OUT_PATH} ({len(html):,} bytes)")
    print(f"    dashboard as-of {dashboard['as_of']}; {len(rest) + 1} research items")
    return 0


if __name__ == "__main__":
    sys.exit(main())
