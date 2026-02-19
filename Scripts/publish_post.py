#!/usr/bin/env python3
"""
Lighthouse Macro — Post Publisher
Uploads a markdown educational post to Substack (as draft) and Bear,
with all local chart images embedded inline.

Usage:
    # First time: get your Substack connect.sid cookie from browser DevTools
    # Store it in ~/.lhm_substack_cookie (or pass via --cookie)

    # Publish to both Substack + Bear:
    python publish_post.py /path/to/06_Business_Post.md

    # Substack only:
    python publish_post.py /path/to/06_Business_Post.md --substack-only

    # Bear only:
    python publish_post.py /path/to/06_Business_Post.md --bear-only

    # With explicit cookie:
    python publish_post.py /path/to/06_Business_Post.md --cookie "connect.sid=s%3A..."
"""

import argparse
import base64
import json
import os
import re
import subprocess
import sys
import time
import urllib.parse
from pathlib import Path

# ---------------------------------------------------------------------------
# Substack publishing (uses python-substack library)
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
        line_s = line.strip()
        if line_s.startswith("# ") and title is None:
            title = line_s[2:].strip()
        elif line_s.startswith("*") and line_s.endswith("*") and subtitle is None:
            # First italic line is the subtitle
            subtitle = line_s.strip("*").strip()
            break
    return title or "Untitled", subtitle or ""


def publish_to_substack(md_path, cookie_string):
    """Create a Substack draft from a markdown file with inline images."""
    # Add venv to path so we can import substack
    venv_site = "/Users/bob/LHM/Scripts/.venv/lib"
    for d in Path(venv_site).glob("python*/site-packages"):
        if str(d) not in sys.path:
            sys.path.insert(0, str(d))

    from substack import Api
    from substack.post import Post

    with open(md_path) as f:
        md_text = f.read()

    title, subtitle = parse_markdown_metadata(md_text)
    print(f"  Title: {title}")
    print(f"  Subtitle: {subtitle}")

    # Connect to Substack
    print("  Connecting to Substack...")
    api = Api(
        cookies_string=cookie_string,
        publication_url="https://lighthousemacro.substack.com"
    )
    user_id = api.get_user_id()
    print(f"  Authenticated as user {user_id}")

    # Build the post using from_markdown with API for image uploads
    post = Post(
        title=title,
        subtitle=subtitle,
        user_id=user_id,
        audience="everyone",
    )

    # The library's from_markdown strips leading "/" from image paths,
    # breaking absolute paths. We need to pre-upload images and replace
    # paths in the markdown before passing to from_markdown.
    image_pattern = re.compile(r'!\[([^\]]*)\]\((/[^)]+)\)')
    images_found = image_pattern.findall(md_text)

    if images_found:
        print(f"  Found {len(images_found)} images. Uploading...")
        for i, (alt, img_path) in enumerate(images_found):
            if os.path.exists(img_path):
                print(f"    [{i+1}/{len(images_found)}] Uploading {os.path.basename(img_path)}...")
                try:
                    result = api.get_image(img_path)
                    cdn_url = result.get("url", img_path)
                    # Replace local path with CDN URL in markdown
                    md_text = md_text.replace(f"]({img_path})", f"]({cdn_url})")
                    print(f"      -> {cdn_url[:80]}...")
                    time.sleep(0.5)  # Rate limiting
                except Exception as e:
                    print(f"      FAILED: {e}")
            else:
                print(f"    [{i+1}/{len(images_found)}] File not found: {img_path}")

    # Strip the H1 title line (Substack uses separate title field)
    lines = md_text.split("\n")
    body_lines = []
    skipped_title = False
    for line in lines:
        if not skipped_title and line.strip().startswith("# "):
            skipped_title = True
            continue
        body_lines.append(line)
    md_body = "\n".join(body_lines)

    # Also skip the subtitle line (first italic line after title)
    # to avoid duplication
    body_lines2 = []
    skipped_subtitle = False
    for line in body_lines:
        if not skipped_subtitle and line.strip().startswith("*") and line.strip().endswith("*") and "Figure" not in line:
            stripped = line.strip().strip("*").strip()
            if stripped == subtitle:
                skipped_subtitle = True
                continue
        body_lines2.append(line)
    md_body = "\n".join(body_lines2)

    # Use from_markdown to build the post structure
    # (images are already CDN URLs so no api needed here)
    post.from_markdown(md_body)

    # Create draft
    print("  Creating draft...")
    draft = api.post_draft(post.get_draft())
    draft_id = draft.get("id")
    slug = draft.get("slug", "")
    print(f"  Draft created! ID: {draft_id}")
    print(f"  Edit at: https://lighthousemacro.substack.com/publish/post/{draft_id}")
    return draft_id


# ---------------------------------------------------------------------------
# Bear publishing (via x-callback-url scheme)
# ---------------------------------------------------------------------------

def publish_to_bear(md_path):
    """Create/update a Bear note from markdown with embedded images."""
    with open(md_path) as f:
        md_text = f.read()

    title, _ = parse_markdown_metadata(md_text)

    # Collect image paths and their positions
    image_pattern = re.compile(r'!\[([^\]]*)\]\((/[^)]+)\)')
    images = []
    for match in image_pattern.finditer(md_text):
        alt = match.group(1)
        path = match.group(2)
        images.append((alt, path))

    # Replace image markdown with placeholder text that Bear will display
    # We'll add images after each relevant heading using /add-file
    # But first, create the note with text content

    # For Bear, keep image references as-is (Bear won't render local paths,
    # but we'll attach the actual files separately)
    # Replace image lines with a placeholder caption
    md_for_bear = md_text
    for alt, path in images:
        # Keep the image line - Bear will show it as text, then we replace via /add-file
        # Actually, remove the markdown image syntax and just keep caption
        pass

    # Step 1: Create the note with /create (replaces if title matches)
    print(f"  Creating Bear note: {title}")
    encoded_text = urllib.parse.quote(md_text, safe='')

    # Use /create which makes a new note (or we can use /add-text with title to replace)
    # First, try to create. If exists, we'll replace.
    create_url = (
        f"bear://x-callback-url/create?"
        f"title={urllib.parse.quote(title)}&"
        f"text={encoded_text}&"
        f"tags={urllib.parse.quote('LHM,Educational Series')}&"
        f"open_note=no"
    )

    # Check URL length - macOS has limits around 200KB for URLs
    if len(create_url) > 200000:
        print("  Note text too long for URL scheme. Using chunked approach...")
        # Create with just the title first, then add text
        create_url = (
            f"bear://x-callback-url/create?"
            f"title={urllib.parse.quote(title)}&"
            f"tags={urllib.parse.quote('LHM,Educational Series')}&"
            f"open_note=no"
        )
        subprocess.run(["open", create_url], check=True)
        time.sleep(1.5)

        # Then replace body with full text using /add-text
        add_url = (
            f"bear://x-callback-url/add-text?"
            f"title={urllib.parse.quote(title)}&"
            f"mode=replace&"
            f"text={encoded_text}&"
            f"open_note=no"
        )
        if len(add_url) > 200000:
            print("  WARNING: Text exceeds URL limit. Note may be truncated.")
            print("  Consider using Bear's import or manual paste for very long articles.")
        subprocess.run(["open", add_url], check=True)
        time.sleep(1.5)
    else:
        subprocess.run(["open", create_url], check=True)
        time.sleep(1.5)

    # Step 2: Attach images using /add-file
    if images:
        print(f"  Attaching {len(images)} images...")
        for i, (alt, img_path) in enumerate(images):
            if not os.path.exists(img_path):
                print(f"    [{i+1}/{len(images)}] MISSING: {img_path}")
                continue

            print(f"    [{i+1}/{len(images)}] {os.path.basename(img_path)}")

            # Read and base64-encode the image
            with open(img_path, "rb") as f:
                img_b64 = base64.b64encode(f.read()).decode("utf-8")

            filename = os.path.basename(img_path)

            # Determine which heading this image falls under
            # by looking at the markdown context
            header = find_preceding_header(md_text, img_path)

            # Build /add-file URL
            # Note: base64 images can be very large, may exceed URL limits
            encoded_file = urllib.parse.quote(img_b64, safe='')

            add_file_url = (
                f"bear://x-callback-url/add-file?"
                f"title={urllib.parse.quote(title)}&"
                f"filename={urllib.parse.quote(filename)}&"
                f"file={encoded_file}&"
                f"open_note=no"
            )

            # Check if URL is too long (macOS limit ~2MB for some handlers)
            if len(add_file_url) > 2_000_000:
                print(f"      WARNING: Image too large for URL scheme ({len(img_b64)} bytes b64)")
                print(f"      Skipping - will need manual attachment")
                continue

            if header:
                add_file_url += f"&header={urllib.parse.quote(header)}&mode=prepend"
            else:
                add_file_url += "&mode=append"

            subprocess.run(["open", add_file_url], check=True)
            time.sleep(2)  # Give Bear time to process each image

    print(f"  Bear note created with {len(images)} images attached.")
    print(f"  Open Bear and search for: {title}")


def find_preceding_header(md_text, img_path):
    """Find the markdown heading that precedes this image reference."""
    lines = md_text.split("\n")
    last_header = None
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("## ") or stripped.startswith("### "):
            last_header = stripped.lstrip("#").strip()
        if img_path in line:
            return last_header
    return None


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Publish a Lighthouse Macro markdown post to Substack and/or Bear"
    )
    parser.add_argument("markdown_file", help="Path to the markdown file")
    parser.add_argument("--cookie", help="Substack cookie string (connect.sid=...)")
    parser.add_argument("--substack-only", action="store_true", help="Only publish to Substack")
    parser.add_argument("--bear-only", action="store_true", help="Only publish to Bear")
    parser.add_argument("--no-images-bear", action="store_true",
                       help="Skip image attachment in Bear (just create the text note)")

    args = parser.parse_args()

    md_path = os.path.abspath(args.markdown_file)
    if not os.path.exists(md_path):
        print(f"ERROR: File not found: {md_path}")
        sys.exit(1)

    print(f"Publishing: {md_path}")
    print()

    do_substack = not args.bear_only
    do_bear = not args.substack_only

    # --- Substack ---
    if do_substack:
        print("[SUBSTACK]")
        cookie = args.cookie or get_substack_cookie()
        if not cookie:
            print("  ERROR: No Substack cookie found.")
            print("  Either pass --cookie or save to ~/.lhm_substack_cookie")
            print("  To get cookie: Browser DevTools > Application > Cookies > connect.sid")
            if not do_bear:
                sys.exit(1)
        else:
            try:
                publish_to_substack(md_path, cookie)
                print("  DONE\n")
            except Exception as e:
                print(f"  ERROR: {e}\n")
                import traceback
                traceback.print_exc()

    # --- Bear ---
    if do_bear:
        print("[BEAR]")
        try:
            publish_to_bear(md_path)
            print("  DONE\n")
        except Exception as e:
            print(f"  ERROR: {e}\n")
            import traceback
            traceback.print_exc()

    print("Finished.")


if __name__ == "__main__":
    main()
