"""
LHM live framework snapshot — the single source for the regime read.

Reads Lighthouse_Master.db (lighthouse_indices) and produces the live
12-pillar + risk snapshot in LHM language: regime, allocation posture, the
loud signals, and the one-line pillar scan. Telegram-HTML out.

No deps beyond stdlib. Reused by:
  - lhmbot_push.py   (proactive morning snapshot + alert deltas)
  - the reactive lhmbot skill (on-demand /snapshot, macro context for /read)
  - future website / brief surfaces

The regime table is the canonical CLAUDE_MASTER Section 3 mapping. We also
surface the system's own ALLOC_MULTIPLIER so the published band and the live
computed multiplier are both visible (no silent re-derivation).
"""
from __future__ import annotations

import html
import json
import math
import os
import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(
    os.environ.get(
        "LIGHTHOUSE_DB_PATH",
        "/Users/bob/LHM/Data/databases/Lighthouse_Master.db",
    )
)
ALERT_STATE_PATH = Path("/Users/bob/LHM/Data/alert_state.json")

# MRI -> regime. Canonical CLAUDE_MASTER Section 3. (low, high] half-open.
REGIME_TABLE = [
    (-math.inf, -0.5, "LOW RISK", "65–70%", "1.2x"),
    (-0.5, 0.5, "NEUTRAL", "55–60%", "1.0x"),
    (0.5, 1.0, "ELEVATED", "45–55%", "0.6x"),
    (1.0, 1.5, "HIGH RISK", "35–45%", "0.3x"),
    (1.5, math.inf, "CRISIS", "25–35%", "0.0x"),
]

# Pillar display -> (primary index_id, secondary index_id or None).
# The 12 Diagnostic Dozen pillars, in canonical order.
PILLARS = [
    ("Labor", "LPI", "LFI"),
    ("Prices", "PCI", None),
    ("Growth", "GCI", None),
    ("Housing", "HCI", None),
    ("Consumer", "CCI", None),
    ("Business", "BCI", None),
    ("Trade", "TCI", None),
    ("Fiscal", "FPI", None),
    ("Credit", "FCI", "CLG"),
    ("Plumbing", "LCI", None),
    ("Structure", "MSI", "SBD"),
    ("Sentiment", "SPI", "SSD"),
]

# Risk dashboard ids (computed daily, separate from the pillars).
RISK_IDS = [
    "MRI",
    "WARNING_LEVEL",
    "ENSEMBLE_RISK",
    "REC_PROB",
    "LIQ_STAGE",
    "ALLOC_MULTIPLIER",
    "DISCONTINUITY_PREMIUM",
]

SEV_EMOJI = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "INFO": "🔵"}
SEV_RANK = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "INFO": 3}


# --------------------------------------------------------------------------- #
# DB access
# --------------------------------------------------------------------------- #
def _conn() -> sqlite3.Connection:
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Lighthouse_Master.db not found at {DB_PATH}")
    c = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    c.row_factory = sqlite3.Row
    return c


def latest_snapshot() -> dict[str, dict]:
    """index_id -> {value, status, date}, latest row per index."""
    sql = """
        SELECT li.index_id, li.value, li.status, li.date
        FROM lighthouse_indices li
        JOIN (SELECT index_id, MAX(date) AS d
              FROM lighthouse_indices GROUP BY index_id) m
          ON li.index_id = m.index_id AND li.date = m.d
    """
    with _conn() as c:
        return {
            r["index_id"]: {
                "value": r["value"],
                "status": r["status"],
                "date": r["date"],
            }
            for r in c.execute(sql)
        }


def direction(conn: sqlite3.Connection, index_id: str, lookback: int = 5,
              deadband: float = 0.05) -> tuple[str, float | None]:
    """Arrow vs `lookback` rows back. Returns (arrow, delta). Real change over
    the window — honest even with weekend forward-fill in the rows."""
    rows = conn.execute(
        "SELECT value FROM lighthouse_indices WHERE index_id=? "
        "ORDER BY date DESC LIMIT ?",
        (index_id, lookback + 1),
    ).fetchall()
    if len(rows) < lookback + 1 or rows[0]["value"] is None or rows[-1]["value"] is None:
        return "→", None
    delta = rows[0]["value"] - rows[-1]["value"]
    if delta > deadband:
        return "↑", delta
    if delta < -deadband:
        return "↓", delta
    return "→", delta


# --------------------------------------------------------------------------- #
# Framework logic
# --------------------------------------------------------------------------- #
def mri_regime(mri_value: float) -> dict:
    for lo, hi, name, equity, mult in REGIME_TABLE:
        if lo < mri_value <= hi:
            return {"name": name, "equity": equity, "mult_table": mult}
    return {"name": "UNKNOWN", "equity": "n/a", "mult_table": "n/a"}


def _fmt(v: float | None, places: int = 2) -> str:
    if v is None:
        return "n/a"
    return f"{v:+.{places}f}" if places else f"{v:.0f}"


def loud_signals(snap: dict[str, dict]) -> list[tuple[int, str]]:
    """The signals worth leading with, data-driven. Returns (rank, line)."""
    out: list[tuple[int, str]] = []

    def g(i):
        return snap.get(i, {})

    w = g("WARNING_LEVEL")
    if w.get("value") is not None and w["value"] >= 2.5:
        out.append((0, f"Warning system {html.escape(str(w['status']))} "
                       f"({w['value']:.1f})."))
    er = g("ENSEMBLE_RISK")
    if str(er.get("status", "")).upper() in {"PRE_CRISIS", "CRISIS"}:
        out.append((0, f"Ensemble risk {html.escape(str(er['status']))} "
                       f"({er['value']:.2f})."))
    rp = g("REC_PROB")
    if rp.get("value") is not None and rp["value"] >= 0.35:
        out.append((1, f"Recession probability {html.escape(str(rp['status']))} "
                       f"({rp['value']:.2f})."))
    clg = g("CLG")
    if clg.get("value") is not None and clg["value"] <= -1.0:
        out.append((1, f"Credit-Labor Gap {clg['value']:+.2f} — spreads "
                       f"mispriced vs labor reality."))
    tci = g("TCI")
    if "CRISIS" in str(tci.get("status", "")).upper():
        out.append((1, f"Trade tide {html.escape(str(tci['status']))} "
                       f"({tci['value']:+.2f})."))
    spi = g("SPI")
    if spi.get("value") is not None and abs(spi["value"]) >= 1.5:
        lean = "contrarian bullish" if spi["value"] > 0 else "fade-the-greed"
        out.append((2, f"Sentiment {html.escape(str(spi['status']))} "
                       f"(SPI {spi['value']:+.2f}, {lean})."))
    sbd = g("SBD")
    if sbd.get("value") is not None and abs(sbd["value"]) >= 1.5:
        out.append((1, f"Structure-Breadth Divergence {sbd['value']:+.2f} — "
                       f"breadth split from price."))
    # Any pillar stretched beyond 2 sigma that we haven't already named.
    named = {"WARNING_LEVEL", "ENSEMBLE_RISK", "REC_PROB", "CLG", "TCI",
             "SPI", "SBD"}
    for disp, pid, _ in PILLARS:
        if pid in named:
            continue
        v = g(pid).get("value")
        if v is not None and abs(v) >= 2.0:
            out.append((2, f"{disp} stretched ({pid} {v:+.2f}, "
                           f"{html.escape(str(g(pid)['status']))})."))
    out.sort(key=lambda t: t[0])
    return out[:6]


def pillar_line(snap: dict[str, dict], conn: sqlite3.Connection) -> str:
    """Compact one-line 12-pillar scan with direction arrows."""
    chunks = []
    for disp, pid, sec in PILLARS:
        d = snap.get(pid, {})
        if d.get("value") is None:
            continue
        arrow, _ = direction(conn, pid)
        seg = f"{disp} {d['value']:+.2f}{arrow}"
        if sec and snap.get(sec, {}).get("value") is not None:
            seg += f"/{snap[sec]['value']:+.2f}"
        chunks.append(seg)
    return " · ".join(chunks)


def data_asof(snap: dict[str, dict]) -> str:
    mri = snap.get("MRI", {})
    return mri.get("date", "")


# --------------------------------------------------------------------------- #
# Telegram-HTML formatter
# --------------------------------------------------------------------------- #
FOOTER = (
    '<i>MACRO, ILLUMINATED.</i>\n'
    '<a href="https://lighthousemacro.com">Lighthouse Macro</a>  |  '
    '<a href="https://research.lighthousemacro.com">Research</a>  |  '
    '<a href="https://x.com/LHMacro">@LHMacro</a>'
)


def format_snapshot_html(snap: dict[str, dict] | None = None,
                         now: datetime | None = None) -> str:
    now = now or datetime.now()
    with _conn() as conn:
        if snap is None:
            snap = latest_snapshot()
        mri = snap.get("MRI", {})
        mri_v = mri.get("value")
        reg = mri_regime(mri_v) if mri_v is not None else None
        mri_arrow, _ = direction(conn, "MRI") if mri_v is not None else ("→", None)
        plines = pillar_line(snap, conn)

    asof = data_asof(snap)
    nice = now.strftime("%B %d, %Y")
    stale_flag = ""
    if asof and asof != now.strftime("%Y-%m-%d"):
        stale_flag = f"  <i>(data as of {asof})</i>"

    parts: list[str] = []
    parts.append(f"<b>LHM FRAMEWORK SNAPSHOT</b>  ·  {nice}{stale_flag}")
    parts.append("")

    if reg:
        parts.append(f"<b>Regime: {reg['name']}</b>  (MRI {mri_v:+.2f}{mri_arrow})")
        alloc = snap.get("ALLOC_MULTIPLIER", {})
        alloc_bits = []
        if alloc.get("value") is not None:
            alloc_bits.append(f"Allocation multiplier {alloc['value']:.2f}x")
            if alloc.get("status"):
                alloc_bits.append(html.escape(str(alloc["status"]).lower()))
        line = " — ".join(alloc_bits) if alloc_bits else ""
        if line:
            parts.append(f"{line}. Regime band {reg['equity']} equity.")
        else:
            parts.append(f"Regime band {reg['equity']} equity, {reg['mult_table']} multiplier.")
    parts.append("")

    loud = loud_signals(snap)
    if loud:
        parts.append("<b>What's loud</b>")
        for _, line in loud:
            parts.append(f"• {line}")
        parts.append("")

    if plines:
        parts.append("<b>12 pillars</b>")
        parts.append(plines)
        parts.append("")

    parts.append(FOOTER)
    return "\n".join(parts)


# --------------------------------------------------------------------------- #
# Alert state (for the delta pusher)
# --------------------------------------------------------------------------- #
def read_active_alerts() -> dict[str, dict]:
    if not ALERT_STATE_PATH.exists():
        return {}
    data = json.loads(ALERT_STATE_PATH.read_text())
    return data.get("active_alerts", {})


if __name__ == "__main__":
    # Quick local check: print the snapshot text.
    print(format_snapshot_html())
