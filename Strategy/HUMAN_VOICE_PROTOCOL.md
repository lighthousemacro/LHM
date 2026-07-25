# HUMAN VOICE PROTOCOL — the Pangram-era publishing gate

**Locked:** 2026-07-25
**Trigger:** Substack × Pangram partnership (live 2026-07-22). Readers can scan any post over 100 words with Pangram 3.3. There is also a creator AI-statement space on every post.
**Owner:** Bob. This document is canon for every published surface: Beacon, Beam, Note, Horizon, Chartbook, social copy, guest pieces.

---

## The position (unchanged, now operational)

We do not dodge detectors. We make the prose actually human. Those are different projects, and only the second one survives contact with a classifier that retrains faster than any paraphrase trick.

The stack that produces LHM research is public-defensible: the data pipeline, the composites, the charts, the fact-checking, the brief-building are machine-assisted and we are not embarrassed by that. The sentences are Bob's. The protocol below is how that stays true under deadline pressure.

## The three-layer gate (every piece, before ship)

**Layer 0 — authorship (the real fix).** The Bob-first drafting protocol (locked 2026-07-23) is the foundation: the engine delivers the brief, the verified numbers, the charts, the structure, and interview questions. Bob writes the sentences. Engine-written fragments carry [eng] markers until Bob rewrites or explicitly adopts them. Full-prose drafting happens only on an explicit "just write it," and anything drafted that way gets a Bob rewrite pass at the paragraph level before it ships, not a skim.

**Layer 1 — hard rules.** `python Scripts/utilities/voice_lint.py <draft.md>` — em-dashes, semicolons, markdown tables, banned phrases, antithesis structure, dead pricing, retired coverage. Exit 1 blocks ship.

**Layer 2 — cadence red-team.** `python Scripts/utilities/humanize_lint.py <draft.md>` — paragraph-level prose-shape tells: metronome cadence, machine-gun runs with no builders, sentence-start clustering, triad density, AI-cluster vocabulary, scaffolding constructions, listicle skeletons. Any HIGH paragraph gets rewritten by Bob, out loud first if that helps. HIGH blocks ship.

**Layer 3 — optional external check.** Pangram's own checker (pangram.com) on the final text, as QC only. The response to a flag is Layer 0, a human rewrite of the flagged section. Never iterate machine paraphrases against the checker. If a piece that is genuinely Bob's flags anyway, ship it and let the AI statement carry the position. False positives are their problem to defend, not ours to pre-surrender to.

## The AI statement (per-post, set once, reuse)

Substack now gives every post a creator statement space. Ours, standing:

> Research at Lighthouse Macro runs on a proprietary data pipeline and a set of AI tools I built for data work, fact-checking, and chart production. The analysis and the writing are mine. Where a machine touched the process, it touched the plumbing, not the view.

Adjust per piece only if the piece genuinely differed. Never leave it blank on a flagged post.

## What this changes operationally

1. Both lints run in the publish pipeline on every draft (lhm-publish orchestration and any manual ship). Green before assembly, not after.
2. The supplementary chart-pack posts and Notes count as published surfaces. Same gate, including social copy over 100 words.
3. Engine-drafted interior prose (data recaps, chart captions) is the highest-risk zone for cadence tells. Captions stay short and factual. Recaps get Bob's pass.
4. If Bob pastes a draft he wrote elsewhere, the gate still runs: the lints exist to catch machine cadence wherever it comes from, including Bob writing tired.

## What we never do

- Machine-paraphrase to lower a detector score.
- Prompt any model to "make this sound more human" as a substitute for Bob rewriting it.
- Publicly discuss detector mechanics, scores, or workarounds. If asked, the answer is the AI statement above, said confidently.
