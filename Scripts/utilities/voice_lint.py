#!/usr/bin/env python3
"""
voice_lint.py — pre-ship hard-rule gate for Lighthouse Macro published copy.

Run this on any publish target (Beacon / Beam / Note / Horizon / Chartbook /
edu post) BEFORE it ships. It enforces the hard, mechanical rules so a slip is
caught by code, not by Bob or the model missing it (the June-6 "not X, it's Y"
miss is exactly what this exists to prevent).

Usage:
    python Scripts/utilities/voice_lint.py <file.md> [more.md ...]
    python Scripts/utilities/voice_lint.py Outputs/horizon_2026-06-09_forward/draft.md

Exit code 0 = no FAILs. Exit code 1 = at least one FAIL (do not ship).
WARNs are review items (the antithesis structure, overclaim, sign-off) and do
not block, but should be eyeballed.

Scope note: this is for PUBLISHED editorial copy. Internal docs/specs are exempt.
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------- FAIL rules
# (rule_name, compiled_regex, human note). A match = hard FAIL, blocks ship.
FAIL = [
    ("emdash",              re.compile(r"[—–]"),
        "No emdashes (— –). Use commas, periods, colons, parentheses."),
    ("semicolon",           re.compile(r";"),
        "No semicolons. Use commas or a period."),
    ("markdown-table",      re.compile(r"^\s*\|.*\|\s*$|\|\s*[-:]{3,}\s*\|"),
        "Tables ship as PNG via chart-god/brand-system, never markdown."),
    ("dead-$320-pricing",   re.compile(r"\$320\b|36%\s*off|best deal we (will|'?ll) offer", re.I),
        "The $320 / 36%-off launch deal is dead. Floor is $400."),
    ("RRP/reserve-buffer",  re.compile(r"\bRRP\b|reverse[ -]?repo|reserve buffer|EFFR[- ]?IORB|reserve[- ]?management buy", re.I),
        "The RRP / reserve-buffer / plumbing story is retired. Do not cover it."),
    ("two-books-language",  re.compile(r"Core Book|Technical Overlay|technical sleeve|framework-driven sleeve|humility patch", re.I),
        "Two-books / sleeve language is gated. Use framework-neutral positioning."),
]

# ---------------------------------------------------------------- WARN rules
WARN = [
    # The banned ANTITHESIS STRUCTURE (period-split pivot). Lexicon ("real, not
    # inflationary") is fine; THIS is the structural "X is not A. It is B." that
    # the rule bans, especially at closers. Cap 0-2/piece, never on a closer.
    ("not-X-its-Y STRUCTURE",
        re.compile(r"\b(is|are|was|were|it'?s|that'?s|there'?s)\s+not\b[^.?!\n]{0,90}?[.?!]\s+(It|That|They|It'?s|That'?s|They'?re)\b\s+(is|are|'?s|does|do|was|were|about)\b", re.I),
        "Banned 'X is not A. It is B.' structural pivot. Cap 0-2/piece, never as a closer."),
    # recycled offenders the corpus audit caught propagating verbatim
    ("recycled-antithesis",
        re.compile(r"not a curve responding to growth|Not because [^.]{0,40} is one indicator among many", re.I),
        "Recycled antithesis line reused verbatim across pieces. Rewrite fresh."),
    ("AI-tell",
        re.compile(r"it is important to note|going forward|in our view|at the end of the day|cautiously optimistic|geopolitical uncertainty|needless to say|that being said|remains to be seen", re.I),
        "AI-tell phrase. Cut or rephrase."),
    ("overclaim",
        re.compile(r"\bnobody\b|the only (way|one)|uniquely positioned|single most important|on (Earth|the planet)|largest [a-z ]*participant", re.I),
        "Overclaim / power-language. Soften to a defendable claim."),
    ("website-pointer",
        re.compile(r"(visit|go to|see|check out)[^.]{0,30}lighthousemacro\.com", re.I),
        "No 'visit the site' CTA while the rebuild is in progress (footer wordmark is fine)."),
]

# Closing antithesis: a line (paragraph) that ENDS on a ", not Y" clause is the
# banned-as-closer case. Flagged separately.
CLOSER_ANTITHESIS = re.compile(r",\s+not\s+[^.,;:\n]{1,45}[.?!]?\s*$")

SIGNOFF = re.compile(r"view from the Watch|keep the light on", re.I)
LONGFORM = ("beacon", "horizon", "beam")


def lint(path: Path) -> tuple[list, list]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    lines = text.splitlines()
    fails, warns = [], []
    for i, line in enumerate(lines, 1):
        s = line.strip()
        if not s:
            continue
        for name, rx, note in FAIL:
            for m in rx.finditer(line):
                fails.append((i, name, m.group(0)[:60], note))
        for name, rx, note in WARN:
            for m in rx.finditer(line):
                warns.append((i, name, m.group(0)[:70], note))
        # a paragraph line that ENDS on "X, not Y" = banned closer position
        if CLOSER_ANTITHESIS.search(s) and not s.startswith(("|", "#", "[Figure")):
            warns.append((i, "antithesis-at-closer", s[-55:],
                          "Line ends on a 'X, not Y' antithesis. Never as a closer."))
    # sign-off presence (long-form only)
    name = path.stem.lower() + str(path.parent).lower()
    if any(k in name for k in LONGFORM) and not SIGNOFF.search(text):
        warns.append((0, "missing-signoff", "(none found)",
                      "Long-form piece is missing the canonical 'view from the Watch / keep the light on' sign-off."))
    return fails, warns


def main(argv):
    targets = []
    for a in argv:
        p = Path(a)
        targets += sorted(p.rglob("*.md")) if p.is_dir() else [p]
    if not targets:
        print("usage: voice_lint.py <file.md|dir> [...]"); return 2
    any_fail = False
    for p in targets:
        if not p.exists():
            print(f"  ?? {p} (not found)"); continue
        fails, warns = lint(p)
        status = "FAIL" if fails else ("warn" if warns else "PASS")
        mark = {"FAIL": "✘", "warn": "⚠", "PASS": "✓"}[status]
        print(f"\n{mark} {status}  {p}  ({len(fails)} fail, {len(warns)} warn)")
        for i, name, hit, note in fails:
            any_fail = True
            print(f"   FAIL L{i:>4} [{name}] {hit!r}\n            -> {note}")
        for i, name, hit, note in warns:
            print(f"   warn L{i:>4} [{name}] {hit!r}")
    print()
    return 1 if any_fail else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
