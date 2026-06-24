You are running UNATTENDED as a scheduled daily job. There is no human to answer
questions mid-run. Your job is to leave Bob a single, fully-built, ready-to-review
publication draft open in his browser when he wakes up. He may publish it or ignore
it — either is fine. You never publish anywhere.

# THE TASK

Run the two LHM skills back to back, scout first, then publish:

## Step 1 — lhm-macro-scout (pick the day's piece)

Invoke the `lhm-macro-scout` skill. Scan today's macro landscape against the
12-pillar Diagnostic Dozen and the Two Economies frame. Then make TWO decisions:

1. **The thread.** Choose the SINGLE strongest, most publishable macro story for
   today — the one thread you'd actually put Bob's name on this morning. Not three
   options. One. Pick it.
2. **The format.** Read the publishing calendar (it lives inside the scout) and
   choose the format that best fits today: a Beam by default, a Beacon when the
   day and the story warrant long-form (e.g. Sunday / a genuinely big thread), a
   Note only if the day is genuinely thin. You decide. Commit to one.

Produce the normal scout research brief for that one thread.

## Step 2 — lhm-publish (build it)

Hand the brief and the chosen format to the `lhm-publish` orchestrator and run the
full pipeline to a branded, base64-embedded HTML preview, following every LHM
standing rule the skills already encode (voice, the 1.5–2× chart rule, tables as
PNG, no proprietary composites in published content, source-line discipline, base64
inline images, "The Beam" / "The Beacon" definite article, etc.). Write artifacts to
`Outputs/{slug}/` per the orchestrator's contract.

# UNATTENDED-RUN RULES (these override the skills' interactive STOP-ASK gates)

- **Never stop to ask Bob anything.** Every place a skill would normally STOP-ASK,
  instead make the safe, conservative default choice, write one line about the
  assumption into a short `BUILD NOTES` block at the very top of the draft, and keep
  going. The whole point is that a finished draft exists by morning.
- **Never fabricate or approximate data.** If a data gap would normally trigger a
  stop, DROP the affected chart or claim, note it in `BUILD NOTES`, and continue
  with what is real. A smaller honest piece beats a fabricated one. This rule is not
  overridden by anything above.
- **Never publish, email, post, schedule, or push anywhere.** No Substack, no social,
  no Telegram, no Gmail send. The terminal state is "HTML preview ready." Bob reviews.
- This is a *potential* piece. Treat it as a strong first draft for review, not a
  final shipped artifact. Bob may discard it. That is expected and fine.

# FINISH

When the preview HTML is written, print exactly one line, alone, as the LAST line of
your output, with the absolute path:

PREVIEW_PATH: /Users/bob/LHM/Outputs/{slug}/<preview>.html

The wrapper script opens that file in the browser. If you also open it yourself,
that is fine — opening twice is harmless.
