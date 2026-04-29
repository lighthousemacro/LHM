"""
LHM Morning Brief — Telegram sender (reusable, daily).

Reads a manifest.json from a brief directory and sends ONE text message
(headline + summary + chart-by-chart takeaways + footer) plus ONE photo
album of all 10 charts.

Manifest schema (manifest.json in the brief dir):
{
  "date": "2026-04-29",
  "headline": "FOMC day. Credit complacent, sentiment euphoric, quits at 1.9%.",
  "summary": "<paragraph>",
  "calendar": "Today: ... Tomorrow: ...",
  "charts": [
    {"file": "chart_01_hy_oas.png", "figure": 1, "takeaway": "..."},
    ...
  ]
}

Reads bot credentials from /Users/bob/LHM/Scripts/data_pipeline/.env:
  TELEGRAM_BOT_TOKEN=...
  TELEGRAM_CHAT_ID=...

Usage:
  python send_telegram.py [--brief-dir /path/to/dir]
  # default brief dir = /Users/bob/LHM/Outputs/morning_brief/<today>
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

import requests

ENV_PATH = Path("/Users/bob/LHM/Scripts/data_pipeline/.env")
DEFAULT_BRIEF_ROOT = Path("/Users/bob/LHM/Outputs/morning_brief")
TG_API = "https://api.telegram.org"

# Telegram limits
MAX_TEXT_LEN = 4096
MAX_CAPTION_LEN = 1024
ALBUM_MAX = 10


def load_env() -> dict:
    env = {}
    if not ENV_PATH.exists():
        raise FileNotFoundError(f".env not found at {ENV_PATH}")
    for line in ENV_PATH.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip()
    return env


def esc_html(s: str) -> str:
    """Telegram HTML parse mode escapes only & < >."""
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def send_message(token: str, chat_id: str, text: str,
                 disable_preview: bool = True) -> dict:
    if len(text) > MAX_TEXT_LEN:
        raise ValueError(f"Text length {len(text)} exceeds Telegram limit {MAX_TEXT_LEN}")
    r = requests.post(
        f"{TG_API}/bot{token}/sendMessage",
        data={
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": str(disable_preview).lower(),
        },
        timeout=30,
    )
    r.raise_for_status()
    return r.json()


def send_album(token: str, chat_id: str, photos: list[Path]) -> dict:
    """Send up to 10 photos as a single album. No captions on photos in the
    one-message format — the lead text holds all the analysis."""
    if not photos:
        raise ValueError("No photos to send")
    if len(photos) > ALBUM_MAX:
        raise ValueError(f"Album max is {ALBUM_MAX}, got {len(photos)}")

    media = [{"type": "photo", "media": f"attach://photo{i}"} for i in range(len(photos))]
    files = {f"photo{i}": (p.name, open(p, "rb"), "image/png")
             for i, p in enumerate(photos)}

    r = requests.post(
        f"{TG_API}/bot{token}/sendMediaGroup",
        data={"chat_id": chat_id, "media": json.dumps(media)},
        files=files,
        timeout=180,
    )
    r.raise_for_status()
    return r.json()


def build_lead_text(manifest: dict) -> str:
    """Compose the single text message: headline + summary + numbered takeaways
    + calendar + footer. Stays under MAX_TEXT_LEN."""
    date_str = manifest.get("date", datetime.now().strftime("%Y-%m-%d"))
    try:
        nice_date = datetime.strptime(date_str, "%Y-%m-%d").strftime("%B %d, %Y")
    except ValueError:
        nice_date = date_str

    parts = []
    parts.append(f"<b>LHM MORNING BRIEF</b>  ·  {nice_date}")
    parts.append(f"<b>{esc_html(manifest['headline'])}</b>")
    parts.append("")
    parts.append(esc_html(manifest["summary"]))
    parts.append("")
    parts.append("<b>What's in the charts:</b>")
    for c in manifest["charts"]:
        parts.append(f"<b>{c['figure']}.</b> {esc_html(c['takeaway'])}")
    parts.append("")
    if manifest.get("calendar"):
        parts.append(f"<i>{esc_html(manifest['calendar'])}</i>")
        parts.append("")
    parts.append(
        '<i>MACRO, ILLUMINATED.</i>\n'
        '<a href="https://lighthousemacro.com">Lighthouse Macro</a>  |  '
        '<a href="https://research.lighthousemacro.com">Research</a>  |  '
        '<a href="https://x.com/LHMacro">@LHMacro</a>'
    )
    text = "\n".join(parts)

    if len(text) > MAX_TEXT_LEN:
        # Should not happen with disciplined takeaways but truncate safely if so
        text = text[: MAX_TEXT_LEN - 80] + "\n\n[truncated - see email for full brief]"
    return text


def find_brief_dir(brief_root: Path) -> Path:
    today = datetime.now().strftime("%Y-%m-%d")
    candidate = brief_root / today
    if candidate.exists():
        return candidate
    # Fallback: most recent dir in brief_root
    dirs = sorted([d for d in brief_root.iterdir() if d.is_dir()])
    if not dirs:
        raise FileNotFoundError(f"No brief dirs in {brief_root}")
    return dirs[-1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--brief-dir", type=Path, default=None,
                    help="Brief output directory (defaults to today's)")
    ap.add_argument("--dry-run", action="store_true",
                    help="Print the lead text instead of sending")
    args = ap.parse_args()

    brief_dir = args.brief_dir or find_brief_dir(DEFAULT_BRIEF_ROOT)
    manifest_path = brief_dir / "manifest.json"
    if not manifest_path.exists():
        print(f"ERROR: manifest.json not found in {brief_dir}", file=sys.stderr)
        sys.exit(1)
    manifest = json.loads(manifest_path.read_text())

    photos = [brief_dir / c["file"] for c in manifest["charts"]]
    missing = [p for p in photos if not p.exists()]
    if missing:
        print(f"ERROR: missing chart files: {missing}", file=sys.stderr)
        sys.exit(1)

    lead = build_lead_text(manifest)

    if args.dry_run:
        print("=== LEAD MESSAGE ===")
        print(lead)
        print(f"\n=== {len(photos)} photos ===")
        for p in photos:
            print(f"  {p.name}")
        return

    env = load_env()
    token = env.get("TELEGRAM_BOT_TOKEN")
    chat_id = env.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        print("ERROR: TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID missing in .env",
              file=sys.stderr)
        sys.exit(1)

    print(f"[1/2] Sending lead message ({len(lead)} chars) ...")
    send_message(token, chat_id, lead)
    time.sleep(1.5)

    print(f"[2/2] Sending album of {len(photos)} charts ...")
    send_album(token, chat_id, photos)
    print("Sent.")


if __name__ == "__main__":
    main()
