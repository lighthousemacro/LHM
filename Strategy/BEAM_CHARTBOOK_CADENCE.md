# Beam & Chartbook Cadence

**Author:** Bob Sheehan, CFA, CMT | Lighthouse Macro
**Created:** 2026-04-24
**Status:** Active. Supersedes ad-hoc cadence; applies to all Beams and Chartbooks going forward.

---

## TL;DR

1. **Ship pre-market, not post-close.** Target drop: 6:30-7:30am ET. Rendering happens the night before.
2. **Topic decided the night before, not days ahead.** A nightly synthesis run surfaces what's hot, what's overlooked, what gets people talking. The Beam is the best lane out of that synthesis.
3. **Beams are tactical.** Timely reads, 750 words, 5 charts, one clear takeaway. Not pillar explainers.
4. **Chartbooks lead the day.** 65-70 charts, paid tier, same pre-market window. Bi-weekly Fridays.

---

## Why pre-market

**Reader behavior we're leaning into:**

- **Email opens cluster 6-9am ET.** A 7am drop arrives when allocators, CIOs, and PMs are actively scanning. A 4pm drop competes with every wrap-up and recap email on the street.
- **Framing effect.** Readers who see our pillars before the open frame the whole trading day through that lens. A post-close drop is reference material; a pre-market drop is their starting playbook.
- **Social amplification window.** A 7am Substack Note gets the full day of Twitter/LinkedIn traction. A 4pm drop gets one news cycle then dies overnight.
- **Institutional reading time.** CIOs have ten minutes at 7am. They don't have ten minutes at 4pm when they're managing the close.

**Tradeoff flagged and dismissed:** a pre-market drop uses yesterday's close, not today's. For a framework-driven product, that doesn't matter. MSI, CLG, SBD, LCI, MRI don't change intraday. The pillar readings ARE yesterday's close regardless of when we publish.

---

## Beam cadence

### Schedule

| Element | Rule |
|---|---|
| **Frequency** | 2x/week (Tue + Thu, default) |
| **Ship time** | 6:30-7:30am ET |
| **Topic lock** | Night before, not earlier |
| **Topic source** | Nightly synthesis run (see below) |
| **Length** | 750 words |
| **Charts** | 5 |
| **Template** | Locked 6-section (Setup, Data, Mechanism, Consensus Miss, Invalidation, So-What) |

### Topic rule: decide the night before

**Hard rule: no Beam topic is booked more than 16 hours before ship.**

Historical failure mode: Tuesday morning writing what Thursday's Beam will be. By Thursday the news has moved, the data is different, the angle is stale. Beams are supposed to be tactical — the topic must reflect what's hot, overlooked, or talking-point-worthy *that morning*, not 48 hours earlier.

**Exception:** A Beam can be reserved but not written for a known-upcoming catalyst (FOMC, CPI, NFP, QRA). The topic slot is "FOMC reaction"; the angle is decided the night of the print.

### Nightly synthesis run

Runs every evening at 7-9pm ET. Purpose: surface the three to five best candidate Beam angles for the next morning based on three criteria:

1. **What's hot** — what the market is already talking about (news flow, price action, social chatter). Leaning into this gets attention but risks being one of many voices.
2. **What's likely to get attention** — a known catalyst landing tomorrow, a print hitting a threshold, a regime change our framework flagged. We're early on a conversation that's about to happen.
3. **What's overlooked** — a data release or indicator reading nobody else is flagging. Our 12-pillar framework is designed to surface these. This is where we differentiate.

The output is a ranked list. The winning angle is the one that combines **framework edge + likely attention capture**. A hot topic alone is a Bloomberg summary. An overlooked topic nobody cares about is a journal entry. The Beam sits at the intersection.

### Beam selection criteria (explicit)

The synthesis should score candidate angles against:

| Dimension | Question | Weight |
|---|---|---|
| **Framework edge** | Does our framework say something non-consensus? | 30% |
| **Attention capture** | Will this get reshares, quotes, replies? | 25% |
| **Timeliness** | Is this tied to a data release, print, or event in the last 24h or next 24h? | 20% |
| **Invalidation clarity** | Can we write explicit "what would change our mind"? | 15% |
| **Chart-worthiness** | Does the data tell the story visually in 5 charts? | 10% |

Rejected angles:
- Pillar explainers (that's the Diagnostic Dozen series, done)
- Rehashes of last week's Beacon without a new wrinkle
- Evergreen topics with no timely hook
- Anything requiring speculation without data to anchor it

### Nightly workflow (mechanical)

**7:00pm ET — Synthesis run fires.**
- `lhm-macro-scout` pulls last 24h of news, price action, data releases
- Cross-references against all 12 pillar composites (threshold breaches, regime shifts, divergences)
- Spits out 3-5 candidate angles with framework hook + suggested charts + invalidation criteria

**7:30pm ET — Human selection.**
- Bob picks the angle (or overrides with something scout missed)
- Lock the template: Beam is always the 6-section format

**8:00pm ET — Draft.**
- `lhm-content-engine` drafts the 750 words against the locked angle
- `lhm-data-analyst` pulls the 5 charts
- `chart-god` renders

**9:00pm ET — QC + review.**
- `lhm-chart-qc` audits the 5 charts
- Bob reads the draft, fixes voice, tightens
- Charts embed

**Overnight — Hold.** Render is done. Nothing ships until morning.

**6:30am ET — Final read + publish.**
- One pass for anything that moved overnight (major news, gap open)
- If the thesis still holds: publish
- If something invalidates: pull the Beam, write a new one against the new fact (rare but should be a real option)

---

## Chartbook cadence

### Schedule

| Element | Rule |
|---|---|
| **Frequency** | Bi-weekly (Fridays, alternating with off-weeks) |
| **Ship time** | 6:30-7:30am ET |
| **Render window** | Thursday evening, 6-10pm ET |
| **Topic lock** | Thursday morning earliest |
| **Length** | 65-70 charts |
| **Template** | 4 per pillar × 12 pillars + 19 layered + cover + arc dividers |

### Topic rule

Chartbooks have a thesis, not a news hook. The Thursday-morning lock is because the thesis is usually obvious by mid-week (this week's Chartbook thesis crystallized from the April 21 Beam and April 23 Beam — "tape at a record, framework at late cycle"). The lock is late enough that the Thursday internals confirm the thesis; early enough that the Thursday evening render has time.

Thursday 10am: thesis locked. Thursday 10am-6pm: scope doc, chart list, arc dividers drafted. Thursday 6-10pm: full render + brand assembly + QC. Friday 6:30am: publish.

### Pre-market drop rationale (Chartbook-specific)

Chartbooks especially benefit from pre-market. A 65-chart deck at 4pm Friday lands in inboxes at the start of the weekend — read Saturday morning at the earliest, forgotten by Monday open. A 7am Friday drop gets read Friday morning pre-market, shared through Friday, and becomes Monday's reference for the week ahead.

---

## Synthesis run — what it actually does

This is the piece that's new. Building it properly takes the guesswork out of topic selection.

### Inputs

- **DB state:** latest readings on all 17 LHM composites (MRI, LFI, PCI, GCI, HCI, CCI, BCI, TCI, GCI_Gov, FCI, CLG, LCI, MSI, SPI, SBD, SSD, CLI) and flagged threshold breaches / regime shifts in the last 7 days
- **News corpus:** last 24h from the sources we trust (FT, WSJ, Bloomberg, Reuters headlines; Fed speakers; data release wires)
- **Social chatter:** top 20 most-discussed macro topics on Twitter/X and Substack Notes in the last 24h
- **Upcoming calendar:** next 48h of data releases, FOMC speakers, earnings that matter to macro

### Outputs

A ranked shortlist of 3-5 Beam candidates. Each candidate has:

1. **One-line angle** (e.g., "CLG widened to -1.8, the widest in the series, while HY OAS continues to compress")
2. **Framework hook** — which pillar(s), which composite, what threshold or divergence
3. **Attention score** (1-10) — how much noise is already around this
4. **Overlooked score** (1-10) — how few others have connected this to the framework
5. **Suggested charts** — 5 candidates with data sources
6. **Invalidation criteria** — what would kill the thesis
7. **So-what** — why it matters for positioning

The "sweet spot" candidate scores **high-mid on attention + high on overlooked**. That's where we win.

### Examples of good Beam topics by this rubric

- "The Broadening Broke" (April 23) — MSI + breadth divergence, hot topic (record tape), overlooked angle (framework was screaming this before it was obvious)
- "A 1.7% Print, a 0.14% Tell" (April 21) — retail sales print everyone saw, but services-side decomp nobody discussed
- "Two Economies" (Beacon, April 19) — saving rate by decile, hot topic (K-shape), framework angle nobody runs (distributional CCI components)

### Examples of what NOT to write

- "Five things to watch this week" — generic, no framework edge
- "Explaining MSI" — done in Pillar 11 article
- "Fed probably cuts in June" — speculation without framework hook
- "Why inflation is sticky" — evergreen, no timely wrinkle

---

## Roles

| Role | Who | When |
|---|---|---|
| **Scout (synthesis)** | `lhm-macro-scout` | Nightly 7pm |
| **Selection** | Bob | Nightly 7:30pm |
| **Data pull** | `lhm-data-analyst` | Nightly 8pm |
| **Chart render** | `chart-god` | Nightly 8-9pm |
| **Draft** | `lhm-content-engine` | Nightly 8-9pm |
| **QC** | `lhm-chart-qc` | Nightly 9pm |
| **Final read + publish** | Bob | Morning 6:30am |

---

## Automation path

Step 1 (manual, now): Bob runs scout + selection manually each evening, uses the other skills as specialists.

Step 2 (near-term): A scheduled remote trigger at 7pm ET fires the scout, drops a ranked shortlist into email or Slack. Bob picks from phone, triggers the downstream pipeline from phone if desired.

Step 3 (later): The full pipeline (scout → select → render → QC → hold-for-morning) runs on a Mac mini overnight. Bob's role reduces to "read at 6:30am, publish or override."

---

## Rules of thumb

- **Never write Thursday's Beam on Tuesday.** If it needs to be written that far ahead, it's not a Beam, it's a Beacon.
- **The synthesis surfaces, Bob selects.** Never let the model pick the topic autonomously. The framework has taste; the human has judgment.
- **If the overnight data moves, the Beam moves.** A 6:30am scramble to re-angle is better than publishing a stale read.
- **The thesis must be invalidate-able.** If we can't write "what would change our mind," we don't publish.
- **Beams are tactical, Beacons are strategic.** Beams run hot and fast against the news flow. Beacons build the framework. Chartbooks show the framework in action.

---

**End of doc.**

*Bob Sheehan, CFA, CMT | Founder & Chief Investment Officer*
*Lighthouse Macro | LighthouseMacro.com | @LHMacro*
