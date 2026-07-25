#!/usr/bin/env python3
"""
humanize_lint.py — paragraph-level cadence red-team for Lighthouse Macro copy.

Layer 2 of the pre-ship gate (voice_lint.py is layer 1, hard mechanical rules).
This one reads like Pangram does: statistical prose-shape tells, scored per
paragraph, worst first. It exists because Substack now runs AI detection on
posts, and the only durable response is prose that is actually human.

THE FIX MODEL — read this before acting on a report:
    A flagged paragraph gets REWRITTEN BY BOB, in his own words, out loud
    first if that helps. The remedy is human authorship. Never machine-
    paraphrase a flagged paragraph until a detector passes: that is
    detector-dodging, it violates the public transparency stance, and it
    loses the arms race anyway. This tool points at where the machine
    cadence lives. A human removes it.

Usage:
    python Scripts/utilities/humanize_lint.py <file.md> [more.md ...]
    python Scripts/utilities/humanize_lint.py --top 10 draft.md

Exit codes: 0 = clean-ish (no paragraph >= HIGH), 1 = at least one HIGH.
Scope: published editorial copy. Internal docs exempt.
"""
from __future__ import annotations

import argparse
import re
import statistics
import sys
from pathlib import Path

# ---------------------------------------------------------------- helpers

SENT_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-Z\"'\(\$0-9])")
WORD = re.compile(r"[A-Za-z][A-Za-z'\-]*")

# vocabulary that clusters heavily in machine prose and thinly in Bob's
AI_LEXICON = re.compile(
    r"\b(delve|delving|crucially|notably|moreover|furthermore|in essence|"
    r"ultimately|it'?s worth noting|worth noting|landscape|tapestry|"
    r"underscores?|highlights? the|testament to|robust|seamless(?:ly)?|"
    r"pivotal|navigate the|navigating the|complexities|multifaceted|"
    r"holistic|leverage[sd]? the|foster(?:ing|s)?|garner(?:ing|ed|s)?|"
    r"realm|myriad|plethora|paradigm|synergy|streamline[sd]?|"
    r"in today'?s [a-z]+ (world|environment|market)|serves? as a|"
    r"stands? as a|represents? a [a-z]+ shift|marks? a [a-z]+ shift|"
    r"key takeaways?|important to (note|remember|understand)|"
    r"a range of|a variety of|a number of|plays? a (key|crucial|vital) role)\b",
    re.I,
)

# scaffolding constructions AI leans on
SCAFFOLD = re.compile(
    r"\b(not only\b.{1,60}\bbut (also )?|whether\b.{1,50}\bor\b|"
    r"from\b.{1,40}\bto\b.{1,40}\bto\b|isn'?t just\b|not just\b.{1,50},\s*(but|it))",
    re.I,
)

FIRST_SECOND = re.compile(r"\b(First|Second|Third|Fourth|Finally|Lastly),", re.M)


def sentences(par: str) -> list[str]:
    par = re.sub(r"\s+", " ", par.strip())
    if not par:
        return []
    return [s for s in SENT_SPLIT.split(par) if WORD.search(s)]


def wc(s: str) -> int:
    return len(WORD.findall(s))


def triad_count(par: str) -> int:
    # "x, y, and z" balanced triads
    return len(re.findall(r"\b[\w'\-]+(?: [\w'\-]+){0,3}, [\w'\-]+(?: [\w'\-]+){0,3},? (?:and|or) [\w'\-]+", par))


# ---------------------------------------------------------------- scoring

def score_paragraph(par: str) -> tuple[int, list[str]]:
    """Return (score, tells). Higher = more machine-shaped."""
    sents = sentences(par)
    if len(sents) < 2:
        return 0, []
    lens = [wc(s) for s in sents]
    n = len(sents)
    words = sum(lens)
    tells: list[str] = []
    score = 0

    # 1. cadence uniformity — Bob's paragraphs have high variance
    #    (long builders then a short punch). Machines write metronomes.
    if n >= 3:
        stdev = statistics.pstdev(lens)
        mean = statistics.fmean(lens)
        cv = stdev / mean if mean else 0
        if cv < 0.30 and 8 <= mean <= 30:
            score += 3
            tells.append(f"metronome cadence (cv={cv:.2f}, {n} sentences all ~{mean:.0f} words)")
        if mean < 9 and max(lens) < 14:
            score += 3
            tells.append(f"machine-gun: all {n} sentences short (mean {mean:.0f}w), no builder before the punch")

    # 2. sentence-start clustering
    starts = [re.match(r"[\"'\(]*(\w+)", s).group(1).lower() for s in sents if re.match(r"[\"'\(]*(\w+)", s)]
    if n >= 4:
        common = {"the", "this", "that", "it", "these", "those"}
        frac = sum(1 for s in starts if s in common) / n
        if frac >= 0.75:
            score += 2
            tells.append(f"{frac:.0%} of sentences start with The/This/That/It")
    # anaphora: 3+ consecutive identical starts
    run = 1
    for a, b in zip(starts, starts[1:]):
        run = run + 1 if a == b else 1
        if run == 3:
            score += 2
            tells.append(f"anaphora run: 3+ consecutive sentences open with '{a.title()}'")
            break

    # 3. triads
    t = triad_count(par)
    if t and words and t / (words / 100) >= 1.5:
        score += 2
        tells.append(f"{t} balanced triads in {words} words")
    elif t >= 3:
        score += 1
        tells.append(f"{t} balanced triads")

    # 4. AI lexicon
    hits = AI_LEXICON.findall(par)
    if hits:
        score += min(3, len(hits))
        flat = [h if isinstance(h, str) else h[0] for h in hits]
        tells.append("AI-cluster vocabulary: " + ", ".join(sorted(set(x.lower() for x in flat if x))[:5]))

    # 5. scaffolding constructions
    sc = SCAFFOLD.findall(par)
    if len(sc) >= 2:
        score += 2
        tells.append(f"{len(sc)} not-only/whether-or/from-to scaffolds in one paragraph")

    # 6. listicle prose
    if len(FIRST_SECOND.findall(par)) >= 2:
        score += 2
        tells.append("First/Second/Third listicle skeleton in prose")

    # 7. rhetorical question density
    q = sum(1 for s in sents if s.rstrip().endswith("?"))
    if q >= 2:
        score += 1
        tells.append(f"{q} rhetorical questions in one paragraph")

    # 8. perfect parallel openers ("X did A. Y did B. Z did C.")
    if n >= 3:
        shapes = []
        for s in sents:
            toks = WORD.findall(s)[:3]
            shapes.append(tuple(t.istitle() for t in toks))
        if len(set(shapes)) == 1 and all(shapes[0]) and statistics.pstdev(lens) < 4:
            score += 1
            tells.append("perfectly parallel sentence shapes")

    return score, tells


SEVERITY = [(6, "HIGH"), (4, "MED"), (2, "LOW")]


def sev(score: int) -> str | None:
    for cut, label in SEVERITY:
        if score >= cut:
            return label
    return None


# ---------------------------------------------------------------- document

SKIP_LINE = re.compile(r"^\s*(#|\||\[Figure|\*\[Figure|>|```|<!--|-->|\*\*Sources:|\*\*Substack tags:|-\s|\d+\.\s)")


def paragraphs(text: str):
    """Yield (first_line_no, paragraph_text) for prose paragraphs only."""
    # strip html comments entirely
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    buf, start = [], None
    for i, line in enumerate(text.splitlines(), 1):
        if line.strip() and not SKIP_LINE.match(line):
            if start is None:
                start = i
            buf.append(line.strip())
        else:
            if buf:
                yield start, " ".join(buf)
            buf, start = [], None
    if buf:
        yield start, " ".join(buf)


def doc_level_tells(pars: list[tuple[int, str]]) -> list[str]:
    out = []
    all_sents = [s for _, p in pars for s in sentences(p)]
    if len(all_sents) >= 20:
        lens = [wc(s) for s in all_sents]
        cv = statistics.pstdev(lens) / statistics.fmean(lens)
        if cv < 0.42:
            out.append(f"DOC: whole-piece sentence-length variance is low (cv={cv:.2f}; Bob's real pieces run ~0.55+). Reads uniform.")
        longs = sum(1 for x in lens if x >= 30)
        if longs / len(lens) < 0.05:
            out.append("DOC: almost no long building sentences (>=30w). The punches have no setup.")
    return out


def lint_file(path: Path, top: int) -> int:
    text = path.read_text(encoding="utf-8", errors="ignore")
    pars = list(paragraphs(text))
    scored = []
    for line_no, par in pars:
        s, tells = score_paragraph(par)
        label = sev(s)
        if label:
            scored.append((s, label, line_no, par, tells))
    scored.sort(reverse=True)
    doc_tells = doc_level_tells(pars)

    high = sum(1 for s in scored if s[1] == "HIGH")
    med = sum(1 for s in scored if s[1] == "MED")
    mark = "✘" if high else ("⚠" if med else "✓")
    print(f"\n{mark} {path}  ({len(pars)} paragraphs: {high} HIGH, {med} MED, "
          f"{len(scored) - high - med} LOW)")
    for note in doc_tells:
        print(f"   {note}")
    for s, label, line_no, par, tells in scored[:top]:
        preview = (par[:110] + "…") if len(par) > 110 else par
        print(f"\n   [{label} {s}] L{line_no}: {preview}")
        for t in tells:
            print(f"        - {t}")
    if scored[top:]:
        print(f"\n   (+{len(scored[top:])} more below threshold — rerun with --top {len(scored)})")
    if high:
        print("\n   HIGH paragraphs: Bob rewrites these by hand, in his own words."
              "\n   Do not machine-paraphrase them. Say it out loud, then type that.")
    return 1 if high else 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--top", type=int, default=12, help="show N worst paragraphs (default 12)")
    args = ap.parse_args(argv)
    rc = 0
    for a in args.paths:
        p = Path(a)
        targets = sorted(p.rglob("*.md")) if p.is_dir() else [p]
        for t in targets:
            if not t.exists():
                print(f"?? {t} not found")
                continue
            rc = max(rc, lint_file(t, args.top))
    print()
    return rc


if __name__ == "__main__":
    sys.exit(main())
