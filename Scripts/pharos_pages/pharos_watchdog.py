#!/usr/bin/env python3
"""pharos_watchdog.py — tell Bob when Pharos is down, before a subscriber does.

On 2026-08-03 a paying subscriber reported the terminal was down. It had been
dark for 84 hours: the Mac slept on 07-31 at 1% battery and Pharos is served off
this machine, so the tunnel and the app went with it. Nothing was watching.

This checks the PUBLIC url the way a subscriber would, on a schedule, and pushes
a Telegram alert on a state change. It alerts once when it goes down and once
when it recovers, so a long outage does not spam.

Checks, in order of what a subscriber would notice:
  1. the public origin answers at all
  2. /healthz returns 200
  3. the gate still works (a junk email is refused)
  4. the landing board is not stale

State lives in /tmp so a reboot re-arms it. Exit code is 0 even when down, so
launchd does not mark the job failed for doing its job.
"""
from __future__ import annotations
import json, sys, urllib.error, urllib.parse, urllib.request
from datetime import datetime, timezone
from pathlib import Path

BASE = "https://pharos.lighthousemacro.com"
STATE = Path("/tmp/pharos_watchdog_state.json")
BOARD = Path("/Users/bob/LHM/Data/databases/pillars/the_watch.html")
PUSH = "/Users/bob/LHM/Scripts/data_pipeline/lhmbot_push.py"
STALE_HOURS = 30
UA = {"User-Agent": "lhm-pharos-watchdog/1"}


def get(path: str, timeout: int = 20):
    try:
        req = urllib.request.Request(BASE + path, headers=UA)
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read(2048)
    except Exception as e:  # noqa: BLE001
        return None, str(e).encode()


def check() -> list[str]:
    """Return a list of human-readable failures. Empty list means healthy."""
    bad: list[str] = []

    status, _ = get("/")
    if status != 200:
        bad.append(f"origin not answering ({status or 'no response'})")
        return bad  # everything downstream is meaningless if the door is shut

    status, _ = get("/healthz")
    if status != 200:
        bad.append(f"/healthz returned {status}")

    # The gate itself: a junk address must be refused. If this starts returning
    # 303 the paywall is open and that is worse than an outage.
    try:
        req = urllib.request.Request(
            BASE + "/auth/request", data=b"email=watchdog-not-a-sub@example.invalid",
            headers={**UA, "Content-Type": "application/x-www-form-urlencoded"})
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                if r.status < 400:
                    bad.append(f"GATE OPEN: junk email accepted ({r.status})")
        except urllib.error.HTTPError as he:
            if he.code != 403:
                bad.append(f"gate returned {he.code}, expected 403")
    except Exception as e:  # noqa: BLE001
        bad.append(f"gate check failed: {e}")

    if BOARD.exists():
        age_h = (datetime.now().timestamp() - BOARD.stat().st_mtime) / 3600
        if age_h > STALE_HOURS:
            bad.append(f"landing board {age_h:.0f}h stale")
    else:
        bad.append("landing board missing")

    return bad


def _env(key: str) -> str:
    for line in Path("/Users/bob/LHM/Scripts/data_pipeline/.env").read_text().splitlines():
        if line.startswith(key + "="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    return ""


def notify(text: str) -> None:
    """Push to Telegram directly. lhmbot_push.py has a fixed command menu with no
    free-text option, so this posts to the bot API itself."""
    try:
        token = _env("TELEGRAM_BOT_TOKEN")
        # TELEGRAM_CHAT_ID in .env (-1003926200150) returns 400 as of 2026-08-03,
        # so try it but always fall back to Bob's DM, which is the channel that
        # actually has to receive an outage alert.
        targets = [c for c in (_env("TELEGRAM_CHAT_ID"), "7556962272") if c]
        for chat in targets:
            try:
                data = urllib.parse.urlencode({"chat_id": chat, "text": text}).encode()
                req = urllib.request.Request(
                    f"https://api.telegram.org/bot{token}/sendMessage", data=data)
                urllib.request.urlopen(req, timeout=30).read()
                break
            except Exception:
                continue
    except Exception as e:  # noqa: BLE001
        print(f"  telegram push failed: {e}", file=sys.stderr)
    # Telegram is best-effort. The log is the durable record either way.
    print(f"{datetime.now(timezone.utc).isoformat()}  {text}")


def main() -> int:
    failures = check()
    was_down = False
    if STATE.exists():
        try:
            was_down = json.loads(STATE.read_text()).get("down", False)
        except Exception:
            pass

    now_down = bool(failures)
    if now_down and not was_down:
        notify("PHAROS DOWN\n" + "\n".join(f"- {f}" for f in failures) +
               f"\n{BASE}")
    elif was_down and not now_down:
        notify(f"PHAROS RECOVERED\n{BASE}")
    else:
        print(f"{datetime.now(timezone.utc).isoformat()}  "
              f"{'still down: ' + '; '.join(failures) if now_down else 'ok'}")

    STATE.write_text(json.dumps({"down": now_down, "failures": failures,
                                 "checked": datetime.now(timezone.utc).isoformat()}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
