#!/usr/bin/env python3
"""
sync_substack_export.py — keep the Substack export current without a manual download.

The Reading Room builds off Pharos/content/substack_export (posts.csv + posts/*.html),
which is only refreshed when Bob downloads a full export from Substack. That export
goes stale the moment anything publishes. This script pulls the public archive API,
finds anything published since the last sync, and writes it into the export directory
in exactly the shape build_reading_room.py already expects.

Free posts get their full body. Paid posts get the subtitle as a dek and nothing
else, because the Reading Room blocks paid bodies on the open site anyway and we
never want a gated body sitting on disk in a directory the site builder reads.

Run:
    PYTHONPATH=/Users/bob/LHM python3 Scripts/website/sync_substack_export.py
"""

import csv
import html as ihtml
import json
import os
import sys
import time
import urllib.request

ROOT = os.environ.get("LHM_ROOT", "/Users/bob/LHM")
EXPORT = os.path.join(ROOT, "Pharos/content/substack_export")
POSTS_DIR = os.path.join(EXPORT, "posts")
POSTS_CSV = os.path.join(EXPORT, "posts.csv")

PUB = "https://research.lighthousemacro.com"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"
FIELDS = ["post_id", "post_date", "is_published", "email_sent_at", "inbox_sent_at",
          "type", "audience", "title", "subtitle", "podcast_url"]


def get_json(url, tries=3):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:
            if i == tries - 1:
                print(f"  ! fetch failed {url}: {e}")
                return None
            time.sleep(2 * (i + 1))
    return None


def archive(limit=200):
    """Newest-first list of published posts from the public archive API."""
    out, offset = [], 0
    while len(out) < limit:
        page = get_json(f"{PUB}/api/v1/archive?sort=new&limit=50&offset={offset}")
        if not page:
            break
        out.extend(page)
        if len(page) < 50:
            break
        offset += 50
    return out[:limit]


def existing_ids():
    if not os.path.exists(POSTS_CSV):
        return set(), []
    with open(POSTS_CSV, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return {r["post_id"].split(".", 1)[0] for r in rows}, rows


def paid_stub(subtitle: str) -> str:
    """Public-safe placeholder body for a members piece: the dek, nothing more."""
    sub = ihtml.escape(subtitle or "Members research. Read it in full inside Pharos.")
    return f"<blockquote><p>{sub}</p></blockquote>"


def main():
    os.makedirs(POSTS_DIR, exist_ok=True)
    have, rows = existing_ids()
    posts = archive()
    if not posts:
        print("archive fetch returned nothing, leaving the export untouched")
        return 1

    added = 0
    for p in posts:
        pid = str(p.get("id"))
        if pid in have:
            continue
        slug = p.get("slug") or pid
        audience = p.get("audience") or "only_paid"
        title = (p.get("title") or "Untitled").strip()
        subtitle = (p.get("subtitle") or "").strip()
        fn = os.path.join(POSTS_DIR, f"{pid}.{slug}.html")

        if audience == "everyone":
            full = get_json(f"{PUB}/api/v1/posts/by-id/{pid}") or {}
            if isinstance(full, dict) and "post" in full:
                full = full["post"]
            body = full.get("body_html") or ""
            # a free post with no body means the API disagreed with the archive.
            # treat it as gated rather than publishing an empty page.
            if not body.strip():
                print(f"  ~ {slug}: free but no body returned, stubbing as members")
                audience = "only_paid"
                body = paid_stub(subtitle)
        else:
            body = paid_stub(subtitle)

        with open(fn, "w", encoding="utf-8") as f:
            f.write(body)

        rows.append({
            "post_id": f"{pid}.{slug}",
            "post_date": p.get("post_date") or "",
            "is_published": "true",
            "email_sent_at": p.get("post_date") or "",
            "inbox_sent_at": "",
            "type": p.get("type") or "newsletter",
            "audience": audience,
            "title": title,
            "subtitle": subtitle,
            "podcast_url": p.get("podcast_url") or "",
        })
        have.add(pid)
        added += 1
        print(f"  + {p.get('post_date','')[:10]}  {audience:10s}  {slug}")

    if added:
        rows.sort(key=lambda r: r.get("post_date") or "")
        with open(POSTS_CSV, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
            w.writeheader()
            w.writerows(rows)

    print(f"substack export sync: {added} new post(s), {len(rows)} total")
    return 0


if __name__ == "__main__":
    sys.exit(main())
