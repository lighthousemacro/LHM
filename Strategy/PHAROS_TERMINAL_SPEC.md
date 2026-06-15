# PHAROS — The Lighthouse Macro Terminal

**Status:** working spec, evolving · **Started:** 2026-06-15

Pharos is the paid Lighthouse Macro platform: read the research, view charts, open dozens of
dashboards, and talk in a community room, all in one gated place. The LHM terminal, the LHM version
of TBL Pulse but broader. Name repurposed from the retired hackathon project (the Lighthouse of
Alexandria, on-brand). NOTE: the old hackathon code at `Projects/pharos/` (a macro prediction market)
is unrelated and will be retired.

## Access tiers
- **Public** (`lighthousemacro.com`, static site): marketing, free educational (framework,
  methodology, philosophy, services, about), the **dashboard teaser**, the public feed.
- **Pharos** (`pharos.lighthousemacro.com`, PAID ONLY): the **full research**, **exclusive
  non-Substack content**, the **full live dashboard + 25-yr z-score charts**, the dozens of
  dashboards, the **chatroom**. Access = an active paid Substack subscription, verified in real time.

## Content model
- **Substack content** (Notes, Beams, Beacons): pulled via Substack **export** (full text including
  paid) to seed on-site reading + the feeds. Substack stays as email list + top-of-funnel.
- **Pharos-exclusive content**: authored natively through a lightweight in-Pharos CMS, never on
  Substack. The premium differentiator and the reason to pay beyond "I could read it on Substack."

## Feeds
- **Public feed** (`lighthousemacro.com/feed`): free posts in full, paid research shows only the
  non-paywalled preview. Open to visitors, RSS readers, search, AI crawlers. Reliable, on our domain,
  preview controlled by us (not Substack).
- **Newstex feed** (OPEN DECISION): either full content (private/tokenized URL, maximizes the
  usage-based Content Fee) or also free+preview (protects the paid product, smaller check). Default to
  protective until Bob flips it. Changing the covered URL from `lighthousemacro.substack.com` to our
  feed requires **30 days written notice to Newstex** (per the signed S.29.1 agreement; Content Fee =
  30% of a usage pool, so more real content reaching Newstex = more money).

## Auth
- **Magic-link login** (email a one-click sign-in link, no passwords to manage or leak).
- **Verification via Stripe**: is this email an active paid subscriber in Bob's Stripe (the account
  behind Substack payments)? Real-time. The Substack subscriber-list export is the cross-check/backup.

## Stack & hosting
- **FastAPI backend** running alongside the OpenBB backend on the current Mac, moving to the Mac mini
  when it lands. Same language as the data pipeline.
- **Frontend**: custom shell (front door, auth, Reading Room, community) + **OpenBB Workspace** as the
  data-terminal engine for the dashboards (white-label TBD — Bob to ask Didier Lopes whether Workspace
  can be white-labeled + subscriber-gated as Pharos; that answer could save months).

## Build phases
1. **Foundation + hook:** FastAPI auth (magic-link) + Stripe verification + data API; the Reading Room
   (full research on-site); the core macro dashboard (MRI + 12 pillars + 25-yr charts); the
   exclusive-content CMS stub.
2. **Terminal breadth:** the dozens of dashboards + deeper chart library, via OpenBB Workspace
   (white-labeled if Didier confirms) or custom.
3. **Community:** the subscriber chatroom.

## Open items / needs from Bob
- Stripe **secret key** (goes in `.env`, never in chat) for the subscriber verification.
- Substack **export** (Settings → Exports) for full content seed + subscriber cross-check.
- Newstex feed scope decision (full vs preview).
- OpenBB white-label feasibility (ask Didier).
- The 25-yr backfill check (blocked until the indicator recompute releases the DB).
