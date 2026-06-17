"""
fused_brief.py — the LHM Bot daily brief, fused.

Real proprietary framework (MRI, risk, allocation, pillars — local) + real tape
(quotes, technicals, news, calendar, TV positions — tvremix MCP) -> one LLM pass
in Bob's voice -> one Telegram-ready brief. The framework numbers are GROUND
TRUTH; the model never invents or overrides the regime (that is the failure mode
of a tape-only bot that guesses "[LHM] Risk-On").

Config (.env):
  ANTHROPIC_API_KEY   required for the synthesis
  ANTHROPIC_MODEL     default claude-sonnet-4-6 (bump to claude-opus-4-8 for max quality)
  plus the TVREMIX_* vars in tvremix_client.py

Degrades gracefully: if tvremix isn't connected yet (no auth), it still writes a
framework-only brief and says the tape is offline, instead of crashing the push.
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lhm_framework as fw  # noqa: E402
import tvremix_client as tv  # noqa: E402

KEY_INDICATORS = ["MRI", "ALLOC_MULTIPLIER", "WARNING_LEVEL", "REC_PROB",
                  "ENSEMBLE_RISK", "TCI", "CLG"]
ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"


# --------------------------------------------------------------------------- #
# Framework half (the authoritative read)
# --------------------------------------------------------------------------- #
def gather_framework(prev_statuses: dict | None = None) -> dict:
    snap = fw.latest_snapshot()
    # The bot's existing morning formatter is the authoritative framework read
    # (correct regime / allocation / warning / loud / pillars). Reuse it as
    # ground truth and let the model wrap the tape around it.
    auth_text, cur_statuses = fw.format_morning_html(prev_statuses=prev_statuses)
    with fw._conn() as c:
        regime_since, run_days = fw.regime_run(c)
        pillars = fw.pillar_line(snap, c)
    mri = snap.get("MRI", {}).get("value")
    return {
        "authoritative_text": _strip_html(auth_text),
        "regime_since": regime_since,
        "regime_run_days": run_days,
        "mri": mri,
        "regime_name": fw.mri_regime(mri)["name"] if mri is not None else None,
        "key_indicators": {k: snap.get(k) for k in KEY_INDICATORS if k in snap},
        "loud": [line for _, line in fw.loud_signals(snap)],
        "pillars": _strip_html(pillars),
        "as_of": fw.data_asof(snap),
    }, cur_statuses


def _strip_html(s: str) -> str:
    import re
    s = re.sub(r"<a [^>]*>(.*?)</a>", r"\1", s)
    return re.sub(r"<[^>]+>", "", s).strip()


# --------------------------------------------------------------------------- #
# LLM synthesis
# --------------------------------------------------------------------------- #
SYSTEM = """You write the Lighthouse Macro (LHM) daily Telegram brief for Bob Sheehan, CFA, CMT.

You are handed TWO things:
1. THE FRAMEWORK — Bob's proprietary read (regime, MRI, allocation multiplier, warning level, 12 pillars). This is computed truth. NEVER change, soften, or override these numbers or the regime. If the framework says HIGH RISK / capital preservation, the brief says HIGH RISK. The whole point is that the bot does NOT guess the regime from the tape.
2. THE TAPE — live market data from tvremix (quotes, technicals, news, calendar, positions). Use it for real context, prices, and what the market is actually doing today.

Your job: fuse them into one sharp brief. The framework is the spine; the tape is the confirmation or the tension. Lead with whether the tape agrees with or fights the framework.

VOICE (Bob's, non-negotiable):
- "We" voice. Vary sentence length: long building sentences, then a short line that lands.
- NO em-dashes. NO semicolons. Use commas, periods, colons.
- No hedging filler ("it is important to note", "cautiously optimistic", "geopolitical uncertainty").
- Confident, specific, a little dry. Short punches only land because longer sentences set them up.

RULES:
- Use ONLY numbers you are given. Never fabricate a price, level, or print. If a datum is missing, say so plainly or skip it. Do not invent technicals or calendar events.
- Cite real prices and % moves from the tape. Tie moves to the framework read.
- Credit is the tell: always check HYG/LQD. Flat credit during an equity wobble = reduce-risk tape, not crisis tape. Call it.
- If positions are present, do a thesis check: price vs entry, whether any stop is near, whether the posture is on the right side of today's tape.
- End with an Actionable Watchlist: 3-5 concrete lines, each with a level and what it would mean.
- If the tape is offline (not connected), write the framework brief and state plainly that the live tape is offline so it gets fixed.

FORMAT (Telegram):
- Plain text with simple <b>bold</b> for section labels. No markdown headers, no tables.
- Tight. Under ~3500 characters. Sign off with the LHM footer line.
- Start with: 🟠 <b>LHM MORNING · {date}</b>
"""


def _anthropic(system: str, user: str) -> str:
    key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not key:
        raise RuntimeError("ANTHROPIC_API_KEY missing in .env — required for the fused brief.")
    model = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-6").strip()
    r = httpx.post(
        ANTHROPIC_URL,
        headers={"x-api-key": key, "anthropic-version": "2023-06-01",
                 "content-type": "application/json"},
        json={"model": model, "max_tokens": 2200, "system": system,
              "messages": [{"role": "user", "content": user}]},
        timeout=120,
    )
    r.raise_for_status()
    data = r.json()
    return "".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text").strip()


def _packet(framework: dict, tape: dict) -> str:
    today = datetime.now().strftime("%B %-d, %Y")
    parts = [f"DATE: {today}", "", "=== THE FRAMEWORK (ground truth, never override) ===",
             framework["authoritative_text"], ""]
    if not tape.get("connected"):
        parts += ["=== THE TAPE ===", f"OFFLINE. {tape.get('error', '')}. "
                  "Write the framework brief and note the live tape is offline.", ""]
    else:
        parts += ["=== THE TAPE (tvremix, live) ===",
                  "QUOTES: " + json.dumps(_slim_quotes(tape.get("quotes"))),
                  "CALENDAR: " + json.dumps(tape.get("calendar"))[:1500],
                  "TECHNICALS: " + json.dumps(tape.get("technicals"))[:1800],
                  "NEWS: " + json.dumps(_slim_news(tape.get("news")))[:1500],
                  "POSITIONS: " + json.dumps(tape.get("portfolios"))[:1200], ""]
        if tape.get("errors"):
            parts.append("TAPE GAPS: " + "; ".join(tape["errors"][:6]))
    parts.append("Write the fused LHM MORNING brief now.")
    return "\n".join(parts)


def _slim_quotes(q):
    if not isinstance(q, dict):
        return q
    data = q.get("data", q)
    out = {}
    for sym, d in (data.items() if isinstance(data, dict) else []):
        if isinstance(d, dict):
            out[d.get("name", sym)] = {"px": d.get("price"),
                                       "chg%": round(d.get("change_percent", 0), 2)}
    return out


def _slim_news(news):
    if not isinstance(news, dict):
        return news
    out = {}
    for sym, n in news.items():
        items = n.get("data") or n.get("news") or n if isinstance(n, dict) else n
        heads = []
        for it in (items if isinstance(items, list) else [])[:4]:
            if isinstance(it, dict):
                heads.append(it.get("title") or it.get("headline") or "")
        out[sym] = heads
    return out


# --------------------------------------------------------------------------- #
# Public entry
# --------------------------------------------------------------------------- #
FOOTER = ("\n\n<i>MACRO, ILLUMINATED.</i>\n"
          '<a href="https://lighthousemacro.com">Lighthouse Macro</a>  |  '
          '<a href="https://research.lighthousemacro.com">Research</a>  |  '
          '<a href="https://x.com/LHMacro">@LHMacro</a>')


def generate(prev_statuses: dict | None = None) -> tuple[str, dict]:
    framework, cur_statuses = gather_framework(prev_statuses)
    tape = tv.gather_tape()
    brief = _anthropic(SYSTEM, _packet(framework, tape))
    if "lighthousemacro.com" not in brief:
        brief += FOOTER
    return brief, cur_statuses


if __name__ == "__main__":
    text, _ = generate()
    print(text)
