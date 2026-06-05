#!/usr/bin/env python3
"""Lighthouse Macro - Substack per-subscriber engagement puller.

Fills the gap left by Substack's standard CSV exports by pulling per-subscriber
engagement data via the publication's logged-in session cookie. Writes
``subscriber_list.csv`` into the most recent snapshot folder so
``substack_outreach.py`` can populate the Warm Free Subs and Top Engagers tabs.

Architecture
------------
1. Load auth cookie from one of three locations (env override, canonical, legacy)
2. Page through ``POST /api/v1/subscriber-stats`` for the subscription metadata
   (email, name, plan, subscribed_at, status). This is the documented-by-
   reverse-engineering endpoint that every other Substack tool uses.
3. For engagement (``opens_last_10`` / ``clicks_last_10`` / ``last_seen_at``):
   - First try to read those fields directly from the subscriber-stats response
     (some publication tiers return them inline).
   - Otherwise probe the per-post engagement endpoint
     ``GET /api/v1/post/{id}/engagement`` for the last N email posts and
     aggregate opens / clicks per email.
   - Fall back to leaving those columns at 0 so the dashboard still renders
     the subscriber list (the score is just less informative).
4. Write a CSV with exactly the column names ``substack_outreach.py`` expects.

CLI
---
    python substack_api_pull.py                       # full pull, scheduled run
    python substack_api_pull.py --probe               # auth + endpoint probe only
    python substack_api_pull.py --mock                # write a fixture CSV (no auth)
    python substack_api_pull.py --no-engagement       # skip derivation step
    python substack_api_pull.py --limit 100           # cap subscriber fetch
    python substack_api_pull.py --snapshot <stamp>    # target a specific snapshot
    python substack_api_pull.py --engagement-posts 10 # how many recent posts to scan

Cookie file
-----------
Stored at ``~/.config/lhm/substack_session.json`` (or env-var override). 0600 perms,
never committed. JSON shape::

    {
      "cookie_string": "connect.sid=...; substack.sid=...; substack.lli=...",
      "publication_url": "https://lighthousemacro.substack.com",
      "saved_at": "2026-06-05T12:00:00Z"
    }

The legacy plain-text ``~/.lhm_substack_cookie`` (written by
``Scripts/grab_substack_cookie.py``) is read as a fallback so Bob's existing
setup keeps working.

Exit codes
----------
    0  success (CSV written, or --probe completed cleanly)
    1  generic error
    2  auth missing or expired - clear instructions printed
    3  endpoint discovery failed (API shape changed)
"""
from __future__ import annotations

import argparse
import csv
import json
import logging
import os
import random
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Optional

# Activate the same venv the launchd plist will use so `requests` is available
# regardless of how the script is invoked.
_VENV = Path("/Users/bob/LHM/.venv/lib")
for _d in _VENV.glob("python*/site-packages"):
    if str(_d) not in sys.path:
        sys.path.insert(0, str(_d))

try:
    import requests
except ImportError:  # pragma: no cover - clear failure when venv is wrong
    sys.stderr.write(
        "ERROR: `requests` is not importable. Run with the LHM venv:\n"
        "    /Users/bob/LHM/.venv/bin/python "
        "/Users/bob/LHM/Scripts/dashboards/substack_api_pull.py\n"
    )
    raise


# ---------------------------------------------------------------------------
# Paths and config
# ---------------------------------------------------------------------------

REPO = Path("/Users/bob/LHM")
SNAP_ROOT = REPO / "Data" / "substack_snapshots"
LOG_DIR = REPO / "Scripts" / "dashboards" / "logs"

CANONICAL_COOKIE_PATH = Path.home() / ".config" / "lhm" / "substack_session.json"
LEGACY_COOKIE_PATH = Path.home() / ".lhm_substack_cookie"

DEFAULT_PUBLICATION = "https://lighthousemacro.substack.com"

# Browser-like UA. Substack returns 403 on python-requests/* sometimes.
UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)

# Reverse-engineered endpoint, well-documented by every other Substack tool.
SUBSCRIBER_STATS_PATH = "/api/v1/subscriber-stats"
# Per-post engagement endpoint (used as fallback to derive opens/clicks).
POSTS_LIST_PATH = "/api/v1/posts"
# Multiple paths exist depending on Substack vintage. We try them in order.
POST_ENGAGEMENT_PATHS = [
    "/api/v1/post/{post_id}/engagement",
    "/api/v1/post/{post_id}/subscribers/engagement",
    "/api/v1/email/{post_id}/stats",
]
WHOAMI_PATH = "/api/v1/user/profile/self"

PAGE_SIZE = 50           # subscriber-stats page size (matches Substack's UI)
RATE_LIMIT_SLEEP = 1.5   # seconds between requests, recommended to avoid 429s


# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------

def configure_logging() -> logging.Logger:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("substack_api_pull")
    logger.setLevel(logging.INFO)
    # Avoid duplicate handlers on re-runs in same Python session
    if logger.handlers:
        return logger
    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    fh = logging.FileHandler(LOG_DIR / "substack_api_pull.log")
    fh.setFormatter(fmt)
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(fmt)
    logger.addHandler(fh)
    logger.addHandler(sh)
    return logger


log = configure_logging()


# ---------------------------------------------------------------------------
# Auth: cookie loading
# ---------------------------------------------------------------------------

@dataclass
class Session:
    cookie_string: str
    publication_url: str
    source: str  # which file / env produced the cookie
    raw: dict = field(default_factory=dict)


def _read_canonical(path: Path) -> Optional[Session]:
    if not path.exists():
        return None
    try:
        raw = json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        log.warning("Cookie file %s is not valid JSON: %s", path, exc)
        return None
    cookie = (raw.get("cookie_string") or "").strip()
    if not cookie:
        log.warning("Cookie file %s has empty cookie_string", path)
        return None
    pub = (raw.get("publication_url") or DEFAULT_PUBLICATION).rstrip("/")
    return Session(cookie_string=cookie, publication_url=pub,
                   source=str(path), raw=raw)


def _read_legacy(path: Path) -> Optional[Session]:
    if not path.exists():
        return None
    cookie = path.read_text().strip()
    if not cookie:
        return None
    return Session(cookie_string=cookie, publication_url=DEFAULT_PUBLICATION,
                   source=str(path))


def load_session() -> Session:
    """Resolve the auth cookie. Raises SystemExit(2) with clear instructions."""
    # 1. Env-var override (handy for testing)
    env_path = os.environ.get("LHM_SUBSTACK_COOKIE_FILE")
    if env_path:
        sess = _read_canonical(Path(env_path)) or _read_legacy(Path(env_path))
        if sess:
            log.info("Loaded cookie from env LHM_SUBSTACK_COOKIE_FILE=%s", env_path)
            return sess
        log.warning("LHM_SUBSTACK_COOKIE_FILE set to %s but file unreadable", env_path)

    # 2. Canonical JSON file at the LHM spec'd path
    sess = _read_canonical(CANONICAL_COOKIE_PATH)
    if sess:
        log.info("Loaded cookie from %s", CANONICAL_COOKIE_PATH)
        return sess

    # 3. Legacy plain-text fallback so existing grab_substack_cookie.py setups work
    sess = _read_legacy(LEGACY_COOKIE_PATH)
    if sess:
        log.info("Loaded cookie from legacy %s", LEGACY_COOKIE_PATH)
        return sess

    # No cookie. Print a friendly setup guide and bail.
    msg = (
        "\n"
        "================================================================\n"
        "  SUBSTACK SESSION COOKIE NOT FOUND\n"
        "----------------------------------------------------------------\n"
        "  No cookie at any of:\n"
        f"    - $LHM_SUBSTACK_COOKIE_FILE  (env override)\n"
        f"    - {CANONICAL_COOKIE_PATH}  (canonical)\n"
        f"    - {LEGACY_COOKIE_PATH}  (legacy)\n"
        "\n"
        "  To set up (one time, ~60 seconds):\n"
        "    1. Log into https://lighthousemacro.substack.com in Chrome.\n"
        "    2. Open DevTools (Cmd+Option+I), Network tab, reload page.\n"
        "    3. Click the very first request. In the right panel,\n"
        "       Request Headers, copy the entire 'cookie:' value.\n"
        "    4. Save it with:\n"
        "         mkdir -p ~/.config/lhm\n"
        "         cat > ~/.config/lhm/substack_session.json <<'EOF'\n"
        "         {\n"
        "           \"cookie_string\": \"PASTE_THE_COOKIE_HERE\",\n"
        "           \"publication_url\": \"https://lighthousemacro.substack.com\",\n"
        "           \"saved_at\": \"2026-06-05T00:00:00Z\"\n"
        "         }\n"
        "         EOF\n"
        "         chmod 600 ~/.config/lhm/substack_session.json\n"
        "\n"
        "  Cookie typically lasts ~30 days. When it expires, repeat steps 1-4.\n"
        "================================================================\n"
    )
    log.error("Substack session cookie missing")
    sys.stderr.write(msg)
    raise SystemExit(2)


# ---------------------------------------------------------------------------
# HTTP session
# ---------------------------------------------------------------------------

def build_http_session(sess: Session) -> requests.Session:
    s = requests.Session()
    for part in sess.cookie_string.split(";"):
        part = part.strip()
        if "=" not in part:
            continue
        k, v = part.split("=", 1)
        s.cookies.set(k.strip(), v.strip(), domain=".substack.com")
    s.headers.update({
        "User-Agent": UA,
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": sess.publication_url + "/publish/subscribers",
        "Origin": sess.publication_url,
    })
    return s


def whoami(http: requests.Session) -> Optional[dict]:
    r = http.get("https://substack.com" + WHOAMI_PATH, timeout=15)
    if r.status_code != 200:
        return None
    try:
        return r.json()
    except json.JSONDecodeError:
        return None


# ---------------------------------------------------------------------------
# Subscriber-stats: the metadata pull
# ---------------------------------------------------------------------------

def fetch_subscribers(
    http: requests.Session,
    publication_url: str,
    limit_total: Optional[int] = None,
) -> list[dict]:
    """Page through /api/v1/subscriber-stats. Returns the raw subscriber dicts."""
    url = publication_url.rstrip("/") + SUBSCRIBER_STATS_PATH
    offset = 0
    out: list[dict] = []
    page = 0
    while True:
        payload = {
            "filters": {"order_by_desc_nulls_last": "subscription_created_at"},
            "limit": PAGE_SIZE,
            "offset": offset,
        }
        page += 1
        log.info("subscriber-stats page %d (offset=%d)", page, offset)
        r = http.post(url, json=payload, timeout=30)
        if r.status_code == 401:
            log.error("Auth rejected (401). Cookie likely expired. "
                      "Re-grab it per ~/.config/lhm/substack_session.json instructions.")
            raise SystemExit(2)
        if r.status_code == 403:
            log.error("Forbidden (403). Check that the cookie owner is a "
                      "publisher on %s.", publication_url)
            raise SystemExit(2)
        if not r.ok:
            log.error("subscriber-stats failed: HTTP %s body=%s",
                      r.status_code, r.text[:300])
            raise SystemExit(3)
        try:
            data = r.json()
        except json.JSONDecodeError:
            log.error("subscriber-stats returned non-JSON: %s", r.text[:300])
            raise SystemExit(3)
        batch = data.get("subscribers") or data.get("results") or []
        if not isinstance(batch, list):
            log.error("Unexpected subscriber-stats shape: %s", list(data.keys()))
            raise SystemExit(3)
        if not batch:
            log.info("subscriber-stats page %d empty, end of list reached", page)
            break
        out.extend(batch)
        log.info("  +%d subs (total=%d)", len(batch), len(out))
        if limit_total is not None and len(out) >= limit_total:
            out = out[:limit_total]
            break
        offset += PAGE_SIZE
        time.sleep(RATE_LIMIT_SLEEP + random.uniform(0, 0.3))
    return out


# ---------------------------------------------------------------------------
# Engagement derivation (per-post fallback)
# ---------------------------------------------------------------------------

def fetch_recent_email_posts(http: requests.Session, publication_url: str,
                             n: int = 10) -> list[dict]:
    """Return metadata for the most recent N posts that were emailed."""
    url = publication_url.rstrip("/") + POSTS_LIST_PATH
    try:
        r = http.get(url, params={"limit": max(n * 2, 25), "offset": 0}, timeout=30)
    except requests.RequestException as exc:
        log.warning("posts list request failed: %s", exc)
        return []
    if not r.ok:
        log.warning("posts list HTTP %s, skipping engagement derivation",
                    r.status_code)
        return []
    try:
        payload = r.json()
    except json.JSONDecodeError:
        log.warning("posts list returned non-JSON, skipping engagement")
        return []
    posts = payload if isinstance(payload, list) else payload.get("posts", [])
    emailed = [p for p in posts if p.get("type") == "newsletter"
               or p.get("is_published") or p.get("post_date")]
    return emailed[:n]


def fetch_post_engagement(http: requests.Session, publication_url: str,
                          post_id: Any) -> Optional[dict]:
    """Try the candidate engagement endpoints in order. Return the first hit."""
    base = publication_url.rstrip("/")
    for tmpl in POST_ENGAGEMENT_PATHS:
        path = tmpl.format(post_id=post_id)
        try:
            r = http.get(base + path, timeout=30)
        except requests.RequestException as exc:
            log.debug("engagement probe %s failed: %s", path, exc)
            continue
        if r.status_code == 404:
            continue
        if not r.ok:
            log.debug("engagement probe %s -> HTTP %s", path, r.status_code)
            continue
        try:
            return r.json()
        except json.JSONDecodeError:
            continue
    return None


def derive_engagement(http: requests.Session, publication_url: str,
                      subs: list[dict], posts_to_scan: int = 10) -> dict[str, dict]:
    """Build per-email counts by aggregating per-post opens / clicks.

    Returns {email_lower: {"opens": int, "clicks": int, "last_seen_at": iso8601}}
    """
    out: dict[str, dict] = {}
    posts = fetch_recent_email_posts(http, publication_url, posts_to_scan)
    if not posts:
        log.warning("No recent posts retrieved - cannot derive engagement")
        return out
    log.info("Deriving engagement from %d recent posts", len(posts))
    for i, p in enumerate(posts, 1):
        pid = p.get("id") or p.get("post_id") or p.get("uuid")
        if not pid:
            continue
        time.sleep(RATE_LIMIT_SLEEP)
        eng = fetch_post_engagement(http, publication_url, pid)
        if not eng:
            log.info("  post %d (%s) - no engagement endpoint matched", i, pid)
            continue
        post_date = p.get("post_date") or p.get("publishedAt") or ""
        # Two common shapes:
        #   eng = {"opens": [{"email": ...}, ...], "clicks": [{"email": ...}, ...]}
        #   eng = {"recipients": [{"email":..., "opened": true, "clicked": true}, ...]}
        opens_emails = []
        clicks_emails = []
        if isinstance(eng.get("opens"), list):
            opens_emails = [e.get("email") or e.get("user_email_address")
                            for e in eng["opens"] if isinstance(e, dict)]
        if isinstance(eng.get("clicks"), list):
            clicks_emails = [e.get("email") or e.get("user_email_address")
                             for e in eng["clicks"] if isinstance(e, dict)]
        if isinstance(eng.get("recipients"), list):
            for rec in eng["recipients"]:
                if not isinstance(rec, dict):
                    continue
                em = rec.get("email") or rec.get("user_email_address")
                if not em:
                    continue
                if rec.get("opened"):
                    opens_emails.append(em)
                if rec.get("clicked"):
                    clicks_emails.append(em)
        log.info("  post %d (%s) opens=%d clicks=%d", i, pid,
                 len(opens_emails), len(clicks_emails))
        for em in opens_emails:
            if not em:
                continue
            slot = out.setdefault(em.lower(), {"opens": 0, "clicks": 0,
                                               "last_seen_at": ""})
            slot["opens"] += 1
            if post_date and post_date > slot["last_seen_at"]:
                slot["last_seen_at"] = post_date
        for em in clicks_emails:
            if not em:
                continue
            slot = out.setdefault(em.lower(), {"opens": 0, "clicks": 0,
                                               "last_seen_at": ""})
            slot["clicks"] += 1
            if post_date and post_date > slot["last_seen_at"]:
                slot["last_seen_at"] = post_date
    log.info("Engagement derived for %d emails across %d posts",
             len(out), len(posts))
    return out


# ---------------------------------------------------------------------------
# Row shaping
# ---------------------------------------------------------------------------

CSV_COLUMNS = [
    "email", "name", "plan", "status", "subscribed_at",
    "opens_last_10", "clicks_last_10", "last_seen_at", "open_rate",
]


def normalize_plan(raw: dict) -> str:
    """Map Substack's flags into the simple plan vocabulary the dashboard
    expects: 'free', 'paid', 'comp', 'gift', 'founding'."""
    if raw.get("is_founding"):
        return "founding"
    if raw.get("is_comp"):
        return "comp"
    if raw.get("is_gift"):
        return "gift"
    interval = (raw.get("subscription_interval") or "").lower()
    if interval in ("free", "", "none"):
        return "free"
    if interval in ("monthly", "annual", "yearly", "lifetime"):
        return "paid"
    return interval or "free"


def normalize_status(raw: dict) -> str:
    s = (raw.get("subscription_status") or raw.get("status") or "").lower()
    if s in ("active", ""):  # blank defaults to active for visible subs
        return "active"
    if s in ("unsubscribed", "cancelled", "canceled", "expired"):
        return "unsubscribed"
    return s


def build_rows(subs: list[dict], engagement: dict[str, dict]) -> list[dict]:
    rows = []
    for s in subs:
        email = (s.get("user_email_address") or s.get("email") or "").strip()
        if not email:
            continue
        eng = engagement.get(email.lower(), {})
        # Inline engagement (if subscriber-stats returned it) takes priority
        opens_inline = (s.get("email_opens_30d")
                        or s.get("opens_last_10")
                        or s.get("opens_30d"))
        clicks_inline = (s.get("email_clicks_30d")
                         or s.get("clicks_last_10")
                         or s.get("clicks_30d"))
        last_seen_inline = (s.get("email_last_opened_at")
                            or s.get("last_seen_at")
                            or s.get("last_opened_at"))
        open_rate_inline = s.get("open_rate") or s.get("email_open_rate") or 0
        rows.append({
            "email": email,
            "name": (s.get("user_name") or s.get("name") or "").strip(),
            "plan": normalize_plan(s),
            "status": normalize_status(s),
            "subscribed_at": s.get("subscription_created_at")
                             or s.get("subscribed_at") or "",
            "opens_last_10": int(opens_inline) if opens_inline is not None
                             else int(eng.get("opens", 0)),
            "clicks_last_10": int(clicks_inline) if clicks_inline is not None
                              else int(eng.get("clicks", 0)),
            "last_seen_at": last_seen_inline or eng.get("last_seen_at", ""),
            "open_rate": float(open_rate_inline) if open_rate_inline else 0.0,
        })
    return rows


def write_csv(rows: list[dict], snapshot_dir: Path) -> Path:
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    out_path = snapshot_dir / "subscriber_list.csv"
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    return out_path


# ---------------------------------------------------------------------------
# Snapshot discovery
# ---------------------------------------------------------------------------

def latest_snapshot() -> Path:
    import re
    pat = re.compile(r"^\d{4}-\d{2}-\d{2}_\d{4}$")
    folders = [p for p in SNAP_ROOT.iterdir()
               if p.is_dir() and pat.match(p.name)]
    if not folders:
        raise SystemExit(f"No snapshots under {SNAP_ROOT}. "
                         f"Run substack_dashboard.py first.")
    folders.sort(key=lambda p: p.name, reverse=True)
    return folders[0]


# ---------------------------------------------------------------------------
# Mock / probe modes
# ---------------------------------------------------------------------------

def write_mock_csv(snapshot_dir: Path) -> Path:
    """Tiny synthetic dataset for verifying the dashboard ingestion path.
    Used only with --mock; clearly labelled emails so it can't be confused
    with real data."""
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    out_path = snapshot_dir / "subscriber_list.csv"
    today = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
    fixture = [
        {"email": "mock.warm.free@example.invalid", "name": "Mock Warm Free",
         "plan": "free", "status": "active",
         "subscribed_at": "2025-08-12T14:22:01Z",
         "opens_last_10": 9, "clicks_last_10": 4, "last_seen_at": today,
         "open_rate": 0.91},
        {"email": "mock.top.paid@example.invalid", "name": "Mock Top Paid",
         "plan": "paid", "status": "active",
         "subscribed_at": "2024-12-01T10:00:00Z",
         "opens_last_10": 10, "clicks_last_10": 7, "last_seen_at": today,
         "open_rate": 0.98},
        {"email": "mock.lukewarm.free@example.invalid", "name": "Mock Lukewarm",
         "plan": "free", "status": "active",
         "subscribed_at": "2026-01-15T09:00:00Z",
         "opens_last_10": 6, "clicks_last_10": 2, "last_seen_at": today,
         "open_rate": 0.62},
        {"email": "mock.cold.free@example.invalid", "name": "Mock Cold",
         "plan": "free", "status": "active",
         "subscribed_at": "2025-03-22T16:11:00Z",
         "opens_last_10": 1, "clicks_last_10": 0,
         "last_seen_at": "2026-04-01T00:00:00Z",
         "open_rate": 0.08},
        {"email": "mock.paid.atrisk@example.invalid", "name": "Mock At Risk Paid",
         "plan": "paid", "status": "active",
         "subscribed_at": "2025-11-09T08:00:00Z",
         "opens_last_10": 1, "clicks_last_10": 0,
         "last_seen_at": "2026-04-15T00:00:00Z",
         "open_rate": 0.06},
    ]
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(fixture)
    return out_path


def probe(sess: Session) -> int:
    http = build_http_session(sess)
    log.info("=== PROBE MODE ===")
    me = whoami(http)
    if not me:
        log.error("whoami failed - cookie invalid or expired")
        return 2
    log.info("Authenticated as: name=%r id=%r",
             me.get("name"), me.get("id"))
    # Try one page of subscriber-stats and inspect the keys present
    url = sess.publication_url.rstrip("/") + SUBSCRIBER_STATS_PATH
    r = http.post(url, json={"filters": {
        "order_by_desc_nulls_last": "subscription_created_at"
    }, "limit": 5, "offset": 0}, timeout=30)
    log.info("subscriber-stats HTTP %s", r.status_code)
    if r.ok:
        sample = (r.json().get("subscribers") or [None])[0]
        if sample:
            log.info("Subscriber row keys: %s", sorted(sample.keys()))
            engagement_keys = [k for k in sample.keys() if any(
                token in k.lower() for token in
                ("open", "click", "last_seen", "engagement", "activity"))]
            if engagement_keys:
                log.info("  Engagement fields detected inline: %s",
                         engagement_keys)
            else:
                log.info("  No inline engagement - will need per-post derivation")
    else:
        log.warning("subscriber-stats probe body: %s", r.text[:300])
        return 3
    posts = fetch_recent_email_posts(http, sess.publication_url, 3)
    log.info("Recent posts fetched: %d", len(posts))
    if posts:
        pid = posts[0].get("id") or posts[0].get("post_id") or posts[0].get("uuid")
        log.info("Probing engagement endpoints for post %s", pid)
        for tmpl in POST_ENGAGEMENT_PATHS:
            path = tmpl.format(post_id=pid)
            rr = http.get(sess.publication_url.rstrip("/") + path, timeout=30)
            log.info("  %s -> HTTP %s", path, rr.status_code)
    log.info("=== PROBE DONE ===")
    return 0


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--probe", action="store_true",
                    help="Auth + endpoint discovery only, write nothing")
    ap.add_argument("--mock", action="store_true",
                    help="Write a 5-row synthetic CSV (no auth) to verify "
                         "dashboard ingestion")
    ap.add_argument("--no-engagement", action="store_true",
                    help="Skip per-post engagement derivation")
    ap.add_argument("--limit", type=int, default=None,
                    help="Cap total subscribers fetched (testing)")
    ap.add_argument("--engagement-posts", type=int, default=10,
                    help="Number of recent posts to scan for engagement "
                         "(default: 10)")
    ap.add_argument("--snapshot", type=str, default=None,
                    help="Target snapshot folder name (default: latest)")
    args = ap.parse_args(argv)

    # Resolve target snapshot
    if args.snapshot:
        snap = SNAP_ROOT / args.snapshot
        if not snap.exists():
            log.error("Snapshot %s does not exist", snap)
            return 1
    else:
        snap = latest_snapshot()
    log.info("Target snapshot: %s", snap)

    # Mock mode: no network
    if args.mock:
        out = write_mock_csv(snap)
        log.info("Wrote MOCK subscriber_list.csv (%d rows) to %s",
                 5, out)
        return 0

    # Auth
    sess = load_session()
    if args.probe:
        return probe(sess)

    http = build_http_session(sess)
    me = whoami(http)
    if not me:
        log.error("whoami returned no profile. Cookie likely expired. "
                  "Refresh per instructions.")
        return 2
    log.info("Authenticated as %r (publication=%s)",
             me.get("name"), sess.publication_url)

    # Pull subscriber metadata
    subs = fetch_subscribers(http, sess.publication_url, limit_total=args.limit)
    log.info("Fetched %d subscriber metadata rows", len(subs))
    if not subs:
        log.error("No subscribers returned. API shape may have changed.")
        return 3

    # Derive engagement
    engagement: dict[str, dict] = {}
    if not args.no_engagement:
        try:
            engagement = derive_engagement(http, sess.publication_url, subs,
                                           args.engagement_posts)
        except Exception as exc:  # never let engagement kill the pull
            log.warning("Engagement derivation crashed: %s "
                        "(continuing with subscription metadata only)", exc)

    rows = build_rows(subs, engagement)
    out_path = write_csv(rows, snap)
    n_with_engagement = sum(1 for r in rows if r["opens_last_10"] > 0)
    log.info("Wrote %d rows to %s (%d with non-zero engagement)",
             len(rows), out_path, n_with_engagement)
    return 0


if __name__ == "__main__":
    sys.exit(main())
