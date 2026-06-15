"""
LHM Telegram pusher — proactive, standalone, no Claude in the loop.

The reactive bot (the MCP bridge) can only reply inside a Claude turn. This
script is the other half: it calls the Telegram Bot API directly so the
morning framework snapshot and threshold/regime alerts reach Bob's DM on a
schedule (launchd/cron), independent of any running session.

Everything is phrased in LHM language (regime, stop/divergence flags), not
"price hit X". Sends to Bob's DM by default; override with --chat-id.

Subcommands:
  snapshot   Live 12-pillar + risk regime read (always works off the DB).
  alerts     Push only NEW / RESOLVED threshold breaches since last push.
  brief      Full 10-chart morning brief (if a fresh manifest exists).
  all        snapshot, then alerts.

  --dry-run  Print instead of send.
  --chat-id  Override destination (default: Bob's DM, 7556962272).

Credentials: TELEGRAM_BOT_TOKEN from Scripts/data_pipeline/.env.
Chat target: --chat-id  >  TELEGRAM_DM_CHAT_ID env  >  DEFAULT_DM_CHAT_ID.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lhm_framework as fw  # noqa: E402

ENV_PATH = Path("/Users/bob/LHM/Scripts/data_pipeline/.env")
PUSH_STATE_PATH = Path("/Users/bob/LHM/Data/telegram_push_state.json")
DEFAULT_DM_CHAT_ID = "7556962272"  # Bob's Telegram user id == DM chat id
TG_API = "https://api.telegram.org"
MAX_TEXT_LEN = 4096


# --------------------------------------------------------------------------- #
# Telegram I/O (self-contained so this schedules without the bridge)
# --------------------------------------------------------------------------- #
def load_env() -> dict:
    env = {}
    if ENV_PATH.exists():
        for line in ENV_PATH.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    return env


def resolve_chat_id(arg_chat: str | None, env: dict) -> str:
    return arg_chat or env.get("TELEGRAM_DM_CHAT_ID") or DEFAULT_DM_CHAT_ID


def tg_send_message(token: str, chat_id: str, text: str) -> dict:
    if len(text) > MAX_TEXT_LEN:
        text = text[: MAX_TEXT_LEN - 40] + "\n\n[truncated]"
    r = requests.post(
        f"{TG_API}/bot{token}/sendMessage",
        data={
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": "true",
        },
        timeout=30,
    )
    r.raise_for_status()
    return r.json()


def tg_send_photo(token: str, chat_id: str, path: Path, caption: str = "") -> dict:
    with open(path, "rb") as fh:
        r = requests.post(
            f"{TG_API}/bot{token}/sendPhoto",
            data={"chat_id": chat_id, "caption": caption[:1024],
                  "parse_mode": "HTML"},
            files={"photo": (path.name, fh, "image/png")},
            timeout=120,
        )
    r.raise_for_status()
    return r.json()


# --------------------------------------------------------------------------- #
# Snapshot
# --------------------------------------------------------------------------- #
def cmd_snapshot(token, chat_id, dry_run) -> None:
    text = fw.format_snapshot_html()
    if dry_run:
        print("=== SNAPSHOT (dry-run) ===\n")
        print(text)
        return
    tg_send_message(token, chat_id, text)
    print(f"snapshot sent to {chat_id}")


# --------------------------------------------------------------------------- #
# Alert deltas
# --------------------------------------------------------------------------- #
def _load_push_state() -> dict:
    if PUSH_STATE_PATH.exists():
        try:
            return json.loads(PUSH_STATE_PATH.read_text())
        except json.JSONDecodeError:
            return {}
    return {}


def _save_push_state(state: dict) -> None:
    state["last_push"] = datetime.now().isoformat()
    PUSH_STATE_PATH.write_text(json.dumps(state, indent=2) + "\n")


def _sev(alert: dict) -> str:
    return str(alert.get("severity", "INFO")).upper()


def build_alert_digest(active: dict[str, dict], prev: dict[str, str]
                       ) -> tuple[str | None, dict[str, str]]:
    """Return (digest_html_or_None, new_pushed_map). Pushes NEW + RESOLVED +
    message-CHANGED only. First run (no prev) -> a grouped 'standing' digest so
    we never wall-of-text 15 separate lines."""
    curr = {k: v.get("msg", "") for k, v in active.items()}
    first_run = not prev

    new_keys = [k for k in curr if k not in prev]
    resolved_keys = [k for k in prev if k not in curr]
    changed_keys = [k for k in curr if k in prev and curr[k] != prev[k]]

    if not (new_keys or resolved_keys or changed_keys):
        return None, curr

    now = datetime.now().strftime("%B %d, %Y")
    parts = [f"<b>LHM ALERTS</b>  ·  {now}", ""]

    if first_run:
        # Standing-state digest, grouped by severity, capped.
        parts.append("<i>Standing threshold breaches (baseline):</i>")
        by_sev = sorted(active.items(),
                        key=lambda kv: fw.SEV_RANK.get(_sev(kv[1]), 9))
        shown = 0
        for k, a in by_sev:
            if shown >= 10:
                parts.append(f"…and {len(by_sev) - shown} more.")
                break
            emoji = fw.SEV_EMOJI.get(_sev(a), "🔵")
            parts.append(f"{emoji} {a.get('msg', k)}")
            shown += 1
    else:
        for k in sorted(new_keys, key=lambda k: fw.SEV_RANK.get(_sev(active[k]), 9)):
            a = active[k]
            emoji = fw.SEV_EMOJI.get(_sev(a), "🔵")
            parts.append(f"{emoji} <b>NEW</b> · {a.get('msg', k)}")
        for k in changed_keys:
            a = active[k]
            emoji = fw.SEV_EMOJI.get(_sev(a), "🔵")
            parts.append(f"{emoji} <b>UPDATED</b> · {a.get('msg', k)}")
        for k in resolved_keys:
            parts.append(f"🟢 <b>RESOLVED</b> · {k}")

    parts.append("")
    parts.append(fw.FOOTER)
    return "\n".join(parts), curr


def cmd_alerts(token, chat_id, dry_run) -> None:
    active = fw.read_active_alerts()
    state = _load_push_state()
    prev = state.get("pushed", {})
    digest, new_pushed = build_alert_digest(active, prev)

    if digest is None:
        print("no new/resolved alerts since last push")
        return
    if dry_run:
        print("=== ALERTS (dry-run) ===\n")
        print(digest)
        print("\n(state NOT written in dry-run)")
        return
    tg_send_message(token, chat_id, digest)
    state["pushed"] = new_pushed
    _save_push_state(state)
    print(f"alerts digest sent to {chat_id}")


# --------------------------------------------------------------------------- #
# Morning — the cohesive daily message (live values + regime-change diff)
# --------------------------------------------------------------------------- #
def cmd_morning(token, chat_id, dry_run) -> None:
    state = _load_push_state()
    prev = state.get("statuses") or None
    text, cur = fw.format_morning_html(prev_statuses=prev)
    if dry_run:
        print("=== MORNING (dry-run) ===\n")
        print(text)
        print("\n(state NOT written in dry-run)")
        return
    tg_send_message(token, chat_id, text)
    state["statuses"] = cur
    _save_push_state(state)
    print(f"morning sent to {chat_id}")


# --------------------------------------------------------------------------- #
# Full brief (delegates to the existing sender with chat override)
# --------------------------------------------------------------------------- #
def cmd_brief(token, chat_id, dry_run) -> None:
    root = Path("/Users/bob/LHM/Outputs/morning_brief")
    today = datetime.now().strftime("%Y-%m-%d")
    brief_dir = root / today
    if not (brief_dir / "manifest.json").exists():
        dirs = sorted(d for d in root.iterdir() if (d / "manifest.json").exists())
        if not dirs:
            print("no brief manifest available; skipping (snapshot covers daily)")
            return
        brief_dir = dirs[-1]
    manifest = json.loads((brief_dir / "manifest.json").read_text())
    sys.path.insert(0, "/Users/bob/LHM/Scripts/morning_brief")
    import send_telegram as st  # noqa: E402
    lead = st.build_lead_text(manifest)
    photos = [brief_dir / c["file"] for c in manifest["charts"]]
    if dry_run:
        print(f"=== BRIEF (dry-run) — {brief_dir.name}, {len(photos)} charts ===\n")
        print(lead)
        return
    tg_send_message(token, chat_id, lead)
    time.sleep(1.5)
    st.send_album(token, chat_id, [p for p in photos if p.exists()])
    print(f"brief ({brief_dir.name}) sent to {chat_id}")


# --------------------------------------------------------------------------- #
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("command",
                    choices=["snapshot", "alerts", "brief", "all", "morning"])
    ap.add_argument("--chat-id", default=None)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    env = load_env()
    token = env.get("TELEGRAM_BOT_TOKEN")
    if not token and not args.dry_run:
        print("ERROR: TELEGRAM_BOT_TOKEN missing in .env", file=sys.stderr)
        sys.exit(1)
    chat_id = resolve_chat_id(args.chat_id, env)

    if args.command in ("snapshot", "all"):
        cmd_snapshot(token, chat_id, args.dry_run)
    if args.command in ("alerts", "all"):
        cmd_alerts(token, chat_id, args.dry_run)
    if args.command == "morning":
        cmd_morning(token, chat_id, args.dry_run)
    if args.command == "brief":
        cmd_brief(token, chat_id, args.dry_run)


if __name__ == "__main__":
    main()
