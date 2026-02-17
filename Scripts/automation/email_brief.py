#!/usr/bin/env python3
"""
LIGHTHOUSE MACRO - EMAIL BRIEF
================================
Sends the morning brief HTML dashboard via email using Google Workspace SMTP.
Designed to run 5 minutes after morning_brief.py generates the HTML file.

Prerequisites:
    1. Google Workspace App Password (NOT your regular password)
       - Go to myaccount.google.com -> Security -> 2-Step Verification -> App Passwords
       - Generate password for "Mail" on "Mac"
    2. Add to /Users/bob/LHM/Scripts/data_pipeline/.env:
       GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
       GMAIL_FROM=bob@lighthousemacro.com

Usage:
    python email_brief.py               # Send the brief
    python email_brief.py --dry-run     # Preview without sending
    python email_brief.py --test        # Send a test email
"""

import argparse
import smtplib
import sys
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from pathlib import Path

# Load .env
ENV_PATH = Path("/Users/bob/LHM/Scripts/data_pipeline/.env")
BRIEF_PATH = Path.home() / "Desktop" / "LHM_Morning_Brief.html"
LOG_PATH = Path("/Users/bob/LHM/logs/email_brief.log")

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
TO_EMAIL = "bob@lighthousemacro.com"


def load_env() -> dict:
    """Load environment variables from .env file."""
    env = {}
    if ENV_PATH.exists():
        with open(ENV_PATH) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    env[key.strip()] = val.strip()
    return env


def send_brief(html_content: str, subject: str, from_email: str, app_password: str,
               to_email: str = TO_EMAIL, dry_run: bool = False) -> bool:
    """Send HTML email via SMTP."""
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"Lighthouse Macro <{from_email}>"
    msg["To"] = to_email

    # Plain text fallback
    plain = f"Lighthouse Macro Morning Brief - {datetime.now().strftime('%B %d, %Y')}\n\nView the HTML version in your email client."
    msg.attach(MIMEText(plain, "plain"))
    msg.attach(MIMEText(html_content, "html"))

    if dry_run:
        print(f"  DRY RUN: Would send to {to_email}")
        print(f"  Subject: {subject}")
        print(f"  HTML size: {len(html_content)} chars")
        return True

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30) as server:
            server.starttls()
            server.login(from_email, app_password)
            server.sendmail(from_email, to_email, msg.as_string())
        print(f"  Brief sent to {to_email}")
        return True
    except smtplib.SMTPAuthenticationError:
        print("  ERROR: SMTP authentication failed. Check your App Password.")
        print("  Go to myaccount.google.com -> Security -> App Passwords")
        return False
    except Exception as e:
        print(f"  ERROR: Failed to send: {e}")
        return False


def log_result(success: bool, subject: str):
    """Log email send result."""
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    status = "OK" if success else "FAILED"
    with open(LOG_PATH, "a") as f:
        f.write(f"[{datetime.now().isoformat()}] {status}: {subject}\n")


def main():
    parser = argparse.ArgumentParser(description="Email the LHM Morning Brief")
    parser.add_argument("--dry-run", action="store_true", help="Preview without sending")
    parser.add_argument("--test", action="store_true", help="Send a test email")
    parser.add_argument("--file", type=str, help="Path to HTML file (default: Desktop brief)")
    args = parser.parse_args()

    env = load_env()
    app_password = env.get("GMAIL_APP_PASSWORD", "")
    from_email = env.get("GMAIL_FROM", "bob@lighthousemacro.com")

    if not app_password and not args.dry_run:
        print("  ERROR: GMAIL_APP_PASSWORD not set in .env")
        print(f"  Add to {ENV_PATH}:")
        print("  GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx")
        sys.exit(1)

    now = datetime.now()

    if args.test:
        html = f"""
        <html><body style="background:#0A1628;color:#e6edf3;font-family:Inter,sans-serif;padding:2rem">
        <h1 style="color:#0089D1">LHM Email Test</h1>
        <p>If you're reading this, email delivery works.</p>
        <p style="color:#8b949e">{now.strftime('%Y-%m-%d %H:%M:%S')}</p>
        </body></html>
        """
        subject = f"LHM Test - {now.strftime('%H:%M')}"
    else:
        brief_path = Path(args.file) if args.file else BRIEF_PATH
        if not brief_path.exists():
            print(f"  ERROR: Brief not found at {brief_path}")
            print("  Run morning_brief.py first.")
            sys.exit(1)

        html = brief_path.read_text()
        subject = f"LHM Morning Brief - {now.strftime('%A %b %d')}"

    success = send_brief(html, subject, from_email, app_password, dry_run=args.dry_run)
    log_result(success, subject)

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
