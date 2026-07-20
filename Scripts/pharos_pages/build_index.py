#!/usr/bin/env python3
"""Pharos — the terminal shell. Lists every planned dashboard with live/in-build chips."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from terminal_theme import render_page, write_page  # noqa: E402

DESKS = [
    ("The Framework", "The engine room. The Watch, the Risk Desk, twelve pillars across three engines, the transmission chains.", [
        ("00 The Watch", "the-watch"), ("01 The Pulse", None), ("06 The Risk Desk", None),
        ("07 Labor", "labor"), ("08 Prices", "prices"), ("09 Growth", "growth"),
        ("10 Housing", "housing"), ("11 Consumer", "consumer"), ("12 Business", "business"),
        ("13 Trade", "trade"), ("14 Government", "government"), ("15 Financial", "financial"),
        ("16 Plumbing", "plumbing"), ("17 Structure", "structure"), ("18 Sentiment", "sentiment"),
        ("03 The Chain", None), ("04 Real Check", None), ("05 Divergence", None),
    ]),
    ("Markets & Main Street", "The board. Six asset classes from equities to crypto, and the Main Street suite built for operators.", [
        ("02 Asset Flow", None), ("19 Equities", None), ("20 Rates", None), ("21 Credit", None),
        ("22 Currencies", None), ("23 Commodities", None), ("24 Crypto", None),
        ("25 Main Street Monitor", None), ("26 Operator Cost & Margin", None),
        ("27 Operator Hiring & Credit", None),
    ]),
]

EXTRA_CSS = """
<style>
.desk{padding:6px 32px 10px;}
.desk h2{font-family:'Montserrat',sans-serif;font-weight:700;font-size:18px;color:var(--fg);margin-bottom:2px;}
.desk .desc{font-size:12px;color:var(--muted);margin-bottom:12px;max-width:760px;}
.board{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-bottom:16px;}
@media (max-width:900px){.board{grid-template-columns:1fr;}}
.slot{display:flex;justify-content:space-between;align-items:center;background:var(--lift);
  border:1px solid var(--spine);border-radius:7px;padding:11px 14px;text-decoration:none;}
.slot .name{font-family:'Montserrat',sans-serif;font-weight:600;font-size:12px;color:var(--fg);letter-spacing:0.3px;}
a.slot:hover{border-color:var(--sky);}
a.slot .name{color:var(--sky);}
.chip{font-family:'Source Code Pro',monospace;font-size:9px;font-weight:600;padding:2px 7px;border-radius:3px;}
.chip-live{background:rgba(0,187,137,0.18);color:var(--sea);}
.chip-build{background:rgba(155,177,197,0.12);color:var(--muted);}
</style>
"""


def build():
    parts = [EXTRA_CSS]
    for desk, desc, slots in DESKS:
        rows = []
        for name, slug in slots:
            if slug:
                rows.append(
                    f'<a class="slot" href="/d/{slug}"><span class="name">{name}</span>'
                    f'<span class="chip chip-live">LIVE</span></a>'
                )
            else:
                rows.append(
                    f'<div class="slot"><span class="name">{name}</span>'
                    f'<span class="chip chip-build">IN BUILD</span></div>'
                )
        parts.append(
            f'<div class="desk"><h2>{desk}</h2><div class="desc">{desc}</div>'
            f'<div class="board">{"".join(rows)}</div></div>'
        )

    html = render_page(
        title="Pharos", h1="PHAROS",
        subtitle="The Lighthouse Macro terminal. Two desks, twenty-eight boards, rolling out.",
        active="index", body="".join(parts),
        sources="Lighthouse Macro", datathru="live",
    )
    out = write_page("pharos_index.html", html)
    print(f"Wrote {out} ({out.stat().st_size:,} bytes)")


if __name__ == "__main__":
    build()
