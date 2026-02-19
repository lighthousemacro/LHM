#!/usr/bin/env python3
"""
Lighthouse Macro — Post Publisher
Uploads a markdown educational post to Substack (as draft) and Bear (text only).

Usage:
    # First time setup: get your Substack connect.sid cookie from browser DevTools
    # and save it:
    #   echo "connect.sid=s%3A..." > ~/.lhm_substack_cookie
    #
    # Or pass the FULL cookie string from DevTools > Network > any request > Cookie header

    # Publish to both Substack (draft with images) + Bear (text only):
    python publish_post.py /path/to/06_Business_Post.md

    # Substack only:
    python publish_post.py /path/to/06_Business_Post.md --substack-only

    # Bear only:
    python publish_post.py /path/to/06_Business_Post.md --bear-only
"""

import argparse
import os
import re
import subprocess
import sys
import time
import urllib.parse
from pathlib import Path


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def get_substack_cookie():
    """Read cookie from ~/.lhm_substack_cookie file."""
    cookie_path = os.path.expanduser("~/.lhm_substack_cookie")
    if os.path.exists(cookie_path):
        with open(cookie_path) as f:
            return f.read().strip()
    return None


def parse_markdown_metadata(md_text):
    """Extract title (first H1) and subtitle (first italic line) from markdown."""
    lines = md_text.strip().split("\n")
    title = None
    subtitle = None
    for line in lines:
        s = line.strip()
        if s.startswith("# ") and title is None:
            title = s[2:].strip()
        elif title and not subtitle and s.startswith("*") and s.endswith("*") and "Figure" not in s:
            subtitle = s.strip("*").strip()
            break
    return title or "Untitled", subtitle or ""


# ---------------------------------------------------------------------------
# Substack publishing
# ---------------------------------------------------------------------------

def publish_to_substack(md_path, cookie_string):
    """Create a Substack draft from a markdown file with inline images."""
    # Import from venv
    venv_site = "/Users/bob/LHM/Scripts/.venv/lib"
    for d in Path(venv_site).glob("python*/site-packages"):
        if str(d) not in sys.path:
            sys.path.insert(0, str(d))

    from substack import Api
    from substack.post import Post
    import requests as _requests

    with open(md_path) as f:
        md_text = f.read()

    title, subtitle = parse_markdown_metadata(md_text)
    print(f"  Title: {title}")
    print(f"  Subtitle: {subtitle}")

    # Connect — handle full cookie string (multiple cookies from DevTools)
    print("  Connecting to Substack...")

    # If cookie_string has multiple cookies (semicolon-separated with various names),
    # we need to construct the Api with all of them
    api = Api(
        cookies_string=cookie_string,
        publication_url="https://lighthousemacro.substack.com"
    )
    user_id = api.get_user_id()
    print(f"  Authenticated (user {user_id})")

    # --- Pre-upload images and replace local paths with CDN URLs ---
    image_pattern = re.compile(r'!\[([^\]]*)\]\((/[^)]+)\)')
    images_found = image_pattern.findall(md_text)

    if images_found:
        print(f"  Uploading {len(images_found)} images...")
        for i, (alt, img_path) in enumerate(images_found):
            if os.path.exists(img_path):
                print(f"    [{i+1}/{len(images_found)}] {os.path.basename(img_path)}...", end=" ")
                try:
                    result = api.get_image(img_path)
                    cdn_url = result.get("url", img_path)
                    md_text = md_text.replace(f"]({img_path})", f"]({cdn_url})")
                    print("OK")
                    time.sleep(0.5)
                except Exception as e:
                    print(f"FAILED: {e}")
            else:
                print(f"    [{i+1}/{len(images_found)}] MISSING: {img_path}")

    # --- Prepare markdown body (strip title/subtitle, they go in separate fields) ---
    lines = md_text.split("\n")
    body_lines = []
    skipped_title = False
    skipped_subtitle = False
    for line in lines:
        s = line.strip()
        if not skipped_title and s.startswith("# "):
            skipped_title = True
            continue
        if skipped_title and not skipped_subtitle and s.startswith("*") and s.endswith("*") and "Figure" not in s:
            inner = s.strip("*").strip()
            if inner == subtitle:
                skipped_subtitle = True
                continue
        body_lines.append(line)
    md_body = "\n".join(body_lines)

    # --- Build post ---
    post = Post(
        title=title,
        subtitle=subtitle,
        user_id=user_id,
        audience="everyone",
    )
    post.from_markdown(md_body)

    # --- Create draft ---
    print("  Creating draft...")
    draft = api.post_draft(post.get_draft())
    draft_id = draft.get("id")
    print(f"  Draft created: ID {draft_id}")
    print(f"  Edit: https://lighthousemacro.substack.com/publish/post/{draft_id}")
    return draft_id


# ---------------------------------------------------------------------------
# Bear publishing (text only, no image attachments)
# ---------------------------------------------------------------------------

def publish_to_bear(md_path):
    """Create a Bear note with the markdown text (no image embedding)."""
    with open(md_path) as f:
        md_text = f.read()

    title, _ = parse_markdown_metadata(md_text)
    print(f"  Creating note: {title}")

    # Strip image lines for cleaner Bear note (just keep captions)
    clean_lines = []
    for line in md_text.split("\n"):
        if re.match(r'^!\[.*\]\(.*\)$', line.strip()):
            # Replace image markdown with a placeholder
            alt = re.match(r'!\[([^\]]*)\]', line.strip())
            if alt and alt.group(1):
                clean_lines.append(f"[Image: {alt.group(1)}]")
            continue
        clean_lines.append(line)
    bear_text = "\n".join(clean_lines)

    encoded_text = urllib.parse.quote(bear_text, safe='')

    # Bear's /create makes a new note. Tags help organize.
    create_url = (
        f"bear://x-callback-url/create?"
        f"title={urllib.parse.quote(title)}&"
        f"text={encoded_text}&"
        f"tags={urllib.parse.quote('LHM,Educational Series')}&"
        f"open_note=yes"
    )

    url_len = len(create_url)
    print(f"  URL length: {url_len:,} chars")

    if url_len > 2_000_000:
        print("  WARNING: Very long URL. If Bear truncates, try splitting the note.")

    subprocess.run(["open", create_url], check=True)
    time.sleep(1.5)
    print(f"  Note created in Bear.")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Publish a Lighthouse Macro post to Substack and/or Bear"
    )
    parser.add_argument("markdown_file", help="Path to the markdown file")
    parser.add_argument("--cookie", help="Substack cookie string")
    parser.add_argument("--substack-only", action="store_true")
    parser.add_argument("--bear-only", action="store_true")
    args = parser.parse_args()

    md_path = os.path.abspath(args.markdown_file)
    if not os.path.exists(md_path):
        print(f"ERROR: File not found: {md_path}")
        sys.exit(1)

    print(f"Publishing: {os.path.basename(md_path)}")
    print()

    do_substack = not args.bear_only
    do_bear = not args.substack_only

    # --- Substack ---
    if do_substack:
        print("[SUBSTACK]")
        cookie = args.cookie or get_substack_cookie()
        if not cookie:
            print("  No cookie found. To set up:")
            print("  1. Open lighthousemacro.substack.com in Chrome")
            print("  2. DevTools (F12) > Application > Cookies")
            print("  3. Copy the full 'connect.sid' value")
            print("  4. Run: echo 'connect.sid=VALUE' > ~/.lhm_substack_cookie")
            print()
            if not do_bear:
                sys.exit(1)
        else:
            try:
                publish_to_substack(md_path, cookie)
                print("  DONE\n")
            except Exception as e:
                print(f"  ERROR: {e}")
                import traceback
                traceback.print_exc()
                print()

    # --- Bear ---
    if do_bear:
        print("[BEAR]")
        try:
            publish_to_bear(md_path)
            print("  DONE\n")
        except Exception as e:
            print(f"  ERROR: {e}")
            import traceback
            traceback.print_exc()
            print()

    print("Finished.")


if __name__ == "__main__":
    main()
