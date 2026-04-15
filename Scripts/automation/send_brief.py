#!/usr/bin/env python3
"""
LIGHTHOUSE MACRO - SEND BRIEF
=============================
Stdlib-only SMTP sender for scheduled briefs (Morning Brief, Pulse Check).
Reads body from a file, sends as real email via Gmail SMTP so iOS/Spark fires
a push notification instead of creating a silent Gmail draft.

Usage:
    python send_brief.py \
      --to bob@lighthousemacro.com \
      --subject "LHM Brief 04/15 - futures flat, CPI at 8:30" \
      --body-file /tmp/brief_body.txt

Env vars (required):
    GMAIL_APP_PASSWORD   Google Workspace app password (spaces ok)
    GMAIL_FROM           From address (e.g. bob@lighthousemacro.com)

Optional:
    --content-type       "text/plain" (default) or "text/html"
    --from-name          Display name for From header (default: "Lighthouse Macro")
"""

import argparse
import os
import smtplib
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587


def main() -> int:
    parser = argparse.ArgumentParser(description="Send an LHM brief via Gmail SMTP")
    parser.add_argument("--to", required=True, help="Recipient email address")
    parser.add_argument("--subject", required=True, help="Subject line")
    parser.add_argument("--body-file", required=True, help="Path to body content file")
    parser.add_argument("--content-type", choices=["text/plain", "text/html"], default="text/plain")
    parser.add_argument("--from-name", default="Lighthouse Macro")
    args = parser.parse_args()

    app_password = os.environ.get("GMAIL_APP_PASSWORD", "").strip()
    from_email = os.environ.get("GMAIL_FROM", "").strip()

    if not app_password:
        print("ERROR: GMAIL_APP_PASSWORD not set in environment", file=sys.stderr)
        return 2
    if not from_email:
        print("ERROR: GMAIL_FROM not set in environment", file=sys.stderr)
        return 2

    body_path = Path(args.body_file)
    if not body_path.exists():
        print(f"ERROR: body file not found: {body_path}", file=sys.stderr)
        return 2
    body = body_path.read_text()

    msg = MIMEMultipart("alternative")
    msg["Subject"] = args.subject
    msg["From"] = f"{args.from_name} <{from_email}>"
    msg["To"] = args.to

    if args.content_type == "text/html":
        plain_fallback = "This brief requires an HTML-capable email client."
        msg.attach(MIMEText(plain_fallback, "plain"))
        msg.attach(MIMEText(body, "html"))
    else:
        msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30) as server:
            server.starttls()
            server.login(from_email, app_password)
            server.sendmail(from_email, [args.to], msg.as_string())
    except smtplib.SMTPAuthenticationError as e:
        print(f"ERROR: SMTP auth failed ({e}). Check GMAIL_APP_PASSWORD.", file=sys.stderr)
        return 3
    except Exception as e:
        print(f"ERROR: send failed: {e}", file=sys.stderr)
        return 4

    print(f"sent: {args.subject} -> {args.to}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
