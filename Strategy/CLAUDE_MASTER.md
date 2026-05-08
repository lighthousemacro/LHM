# LIGHTHOUSE MACRO — MASTER CONTEXT

**LAST_SYNC:** 2026-05-08
**Version:** 6.0
**Purpose:** Single source of truth for all AI assistants (Claude, Gemini, ChatGPT)

*"MACRO, ILLUMINATED."*

---

## DATE CHECK PROTOCOL (Claude Code Only)

1. Note today's date
2. Compare to LAST_SYNC above
3. If LAST_SYNC is NOT today or yesterday: say "Context is stale (last sync: [DATE]). Run `lhm-sync` before we proceed." and STOP until user confirms

---

# SECTION 0: MEMORY SUMMARY

*Source: Claude.ai memory export. Regenerated nightly. Projects have their own memory.*

## Work context
Bob runs Lighthouse Macro (LHM), a Substack-based macro publication: Notes (free), Beacon, Beam, Horizon (paid). Proprietary composites (LFI, LCI, CLG, MRI, SPI, MSI), 12-pillar scanning, Lighthouse_Master.db, Claude integrated across publishing/research. Mercor: two contracts not started (econ chart $75/hr; wealth & asset mgmt $150/hr pending onboarding doc).

## Personal context
NYC-based, former D1 athlete, ADHD as a superpower (thrives on diversity, bored by repetition). Sisters: Cayley (older, NYC) and Arden (younger, Denver). Close friend Asher. Living at Cayley's, planning to move out; hardware (Mac Pro M5 + Mac mini M5) and move tied to revenue conversion.

## Top of mind
Paid tier launched ~Apr 13–20 at $320/yr (36% off), 5 external paid subs Apr 21. Two Economies Beacon (Apr 20) drove biggest external validation to date — Tim Pierotti restacked, Nixon Apple reposted, Leon Liao engaged, mondayswife engaged. Tim Pierotti ladder: (1) WealthVest podcast solo, (2) paid deck, (3) monthly roundtable w/ Aahan (Prometheus) + ideally Bob Elliott, (4) possible OCIO seat at Tim's new RIA. Tania Reif engagement closed Apr 28, no revenue after 6 months / 3 calls / 11 deliverables; lessons in working principles. Building lhm-publish orchestrator + ad hoc subscriber analytics dashboard.

## Working principles (always active)

- **Voice:** "We" voice. Vary sentence cadence — don't collapse to uniform short sentences. No emdashes. No semicolons.
- **"Not X, it's Y":** Use sparingly. Lexicon fine, structural pattern is the tell. Never as a closer.
- **Data:** Never fabricate or approximate. Real sourced data only.
- **Breadth thrust:** Bob uses 20-day AND 50-day as separate indicators — don't flag the 50-day as wrong. Real flag = internal threshold inconsistency within one piece.
- **Gmail drafts via API:** Omit signature block. Use "Best,\nBob" placeholder. HTML signature does NOT auto-append (master context rule was wrong).
- **Paid pricing:** Public. $320/yr launch rate is live.
- **Founding member rates (locked, 3 external):** Michael Zhang $300, Josh Giordano $400, Ryan Salah $400. New comps (e.g., Tim Pierotti) are gifts unless Bob says otherwise.
- **Tania lessons (Apr 28):** (1) Engagement ≠ conversion; cleanest predictor = paid the public tier within 30 days of being told it exists. (2) Soft no's = current no's. Max 2 warm follow-ups, then back-burner. (3) Trials need explicit kill dates + deliverable count. (4) The proposal IS the SOW — going pricing-live with a champion produces free deliverables.
- **Tim Pierotti:** Comp founding sub. Paid chart work = separate consulting engagement.
- **Don't tell Bob what to do** unless he asks for a recommendation. Answer the question. Stop there.
- **Tegus:** Not active. Don't reference.
- **Personal context:** Carry forward quietly. Don't surface unprompted.

---

# SECTION 1: CORE IDENTITY

**Robert Brown Sheehan, CFA, CMT** ("Bob")
Founder & Chief Investment Officer, Lighthouse Macro, LLC (Delaware)

**Background:** Former VP Data & Analytics, EquiLend (Short Squeeze Score, proprietary indices) → Associate PM, BoA Private Bank ($4.5B multi-asset, SGS sleeve ~$1.2B at peak, 2.35 Sortino, 103/76 capture vs S&P 500) → Senior Research Analyst, Strom Capital → Trahan Macro Research. CFA, CMT, BrainStation Data Science. Providence College, D1 lacrosse.

**Contact:**
| Type | Value |
|------|-------|
| Website | LighthouseMacro.com |
| Email | bob@lighthousemacro.com / advisory@ / research@ |
| Phone | +1 (929) 238-9397 |
| Twitter/X | @LHMacro |
| Bank | Mercury |

**Document footer (single line, three hyperlinks, Ocean #2389BB):**
```
Lighthouse Macro | Research | @LHMacro
```
- "Lighthouse Macro" → https://lighthousemacro.com
- "Research" → https://research.lighthousemacro.com
- "@LHMacro" → https://x.com/LHMacro

**Tagline:** "MACRO, ILLUMINATED."
**Mission:** Institutional-grade macro research for hedge funds, CIOs, central banks, allocators.
**Philosophy:** Flows > stocks. Concentrated, conviction-weighted positions. Cash is a position, not drag.

---

# SECTION 2: THE DIAGNOSTIC DOZEN (12 Pillars)

**Nomenclature:** Pillars = inputs (12). Engines = processors (3). "Twelve pillars across three engines."

```
            MACRO DYNAMICS (1-7)         MONETARY MECHANICS (8-10)      MARKET STRUCTURE (11-12)
            1. Labor    → LPI, LFI       8. Government → GCI-Gov        11. Structure → MSI, SBD
            2. Prices   → PCI            9. Financial  → FCI, CLG       12. Sentiment → SPI, SSD
            3. Growth   → GCI            10. Plumbing  → LCI
            4. Housing  → HCI                                          → MRI (Master Composite)
            5. Consumer → CCI                                          → Trading Strategy Execution
            6. Business → BCI
            7. Trade    → TCI
```

**Outputs:** (1) Recession probability, 6–12mo fwd. (2) Threshold warning system. (3) MRI regime classification.

| Pillar | Index | Lead Time | Key Insight |
|---|---|---|---|
| 1. Labor | LPI, LFI | Leading | Quits = truth serum. Flows lead, stocks lag. |
| 2. Prices | PCI | 12-18mo (shelter) | Last mile sticky. |
| 3. Growth | GCI | 2-4mo | Second derivative matters. |
| 4. Housing | HCI | 6-9mo | Frozen equilibrium, rate sensitive. |
| 5. Consumer | CCI | 1-3mo | 68% of GDP. The Last Domino. |
| 6. Business | BCI | 4-8mo | Capex = forward commitment. |
| 7. Trade | TCI | 3-6mo | Dollar/tariff pass-through. |
| 8. Government | GCI-Gov | Structural | Fiscal dominance, term premium. |
| 9. Financial | FCI, CLG | 6-9mo | Spreads lead defaults. |
| 10. Plumbing | LCI | 1-4wk | RRP exhaustion = no buffer. |
| 11. Structure | MSI, SBD | 2-4mo | Breadth divergence = distribution. |
| 12. Sentiment | SPI, SSD | Days-weeks | Contrarian at extremes only. |

**Full pillar docs:** `/Users/bob/LHM/Strategy/Pillar_*/` — formulas, full thresholds, indicator detail live there.

---

# SECTION 3: KEY THRESHOLDS (At-a-glance)

**Labor:** Quits <2.0% pre-recession · LFI >+0.5 fragile · LT-Unemp >22% structural
**Plumbing:** RRP <$200B exhausted · EFFR-IORB >+8bps acute · Reserves vs LCLOR <$300B scarce · LCI <-0.5 scarce
**Credit:** HY OAS <300bps complacent · CLG <-1.0 spreads ignoring labor
**Structure:** Price <200d below trend · %>20d <25/>80 washed/crowded · breadth thrust = 30→70 in 10d · Z-RoC <-1.0 broken · MSI <-1.0 broken
**Sentiment:** AAII Bull-Bear >+30 / <-20 euphoria/capitulation · NAAIM >100 fully invested · SPI >+1.5 / <-1.0 fade

**MRI Regime → Equity allocation / multiplier:**
| MRI | Regime | Equity | Mult |
|---|---|---|---|
| < -0.5 | Low Risk | 65-70% | 1.2x |
| -0.5 to +0.5 | Neutral | 55-60% | 1.0x |
| +0.5 to +1.0 | Elevated | 45-55% | 0.6x |
| +1.0 to +1.5 | High Risk | 35-45% | 0.3x |
| > +1.5 | Crisis | 25-35% | 0.0x |

**Composite formulas + full architecture:** `/Users/bob/LHM/Strategy/LIGHTHOUSE MACRO TRADING STRATEGY - MASTER.md` and pillar dirs.

---

# SECTION 4: ONE BOOK, TWO WAYS OF TAKING RISK

The portfolio is a single book. The distinction is what drives a position.

**Framework-driven (most of the book):** Macro thesis + fundamental confirmation + technical entry. Long or short. Sizing up to 20% per position. MRI regime multiplier scales mechanically. 3-6mo catalyst horizon. Cash is a position.

**Technical sleeve (humility patch):** Pure trend / momentum / RS. No thesis required. Smaller positions, tighter stops, no thesis stop because there is no thesis. Just price. Acknowledgment that markets don't owe the framework anything.

**Public language note:** Don't cite "framework-driven sleeve" / "technical sleeve" / "humility patch" in published copy yet — wait until first PiTrade is live.

**Sizing:** `Position = Base × Conviction × Regime Multiplier`. Tier 1 (16-19pts) 20% / Tier 2 (12-15) 12% / Tier 3 (8-11) 7% / Tier 4 0%.

**Dual stops (framework positions):** Thesis stop OR price stop, whichever first. Price stop = below 200d, Z-RoC <-1.0, or 15% drawdown.

**Full strategy + tables:** `/Users/bob/LHM/Strategy/LIGHTHOUSE MACRO TRADING STRATEGY - MASTER.md`

---

# SECTION 5: VOICE & TONE

**80% institutional rigor / 20% personality / 0% forced flair.**

- **"We" voice** for published written content (Beacons, Beams, Notes, Chartbooks, Horizons). Data-as-subject also fine ("the data shows stress"). Avoid third-person hedge ("some observers note").
- **Strong views, weakly held.** State thesis + invalidation conditions. Not hedging — intellectual honesty.
- **Cadence:** Vary sentence length. Long building sentences, then short crystallizing lines. Short sentences are the punches; they only work because long sentences set them up. If a draft reads like a machine gun, it's wrong.
- **No emdashes. No semicolons.**
- **Avoid:** "It is important to note," "going forward," "in our view," "at the end of the day," "cautiously optimistic," "geopolitical uncertainty," "complex constellation of factors."
- **"Not X, it's Y":** Default zero per piece. Keep lexicon (e.g., "camouflage"), kill structure.
- **Don't overclaim:** No "nobody else covers," "uniquely positioned," "the only way." Use "for us, this does X" or "what's rare is connecting them with math, not the count."

**Sign-offs:**
- CTA (all readers): "Don't navigate in the dark. Subscribe."
- Subscribers (Beacon/Horizon): "That's our view from the Watch. We'll keep the light on..." (don't overuse)

**Full voice working guide is in the appendix at the bottom of this file.**

---

# SECTION 6: BRAND SYSTEM

## 23/89/BB Palette (every color contains some combo of 23, 89, BB)

| Name | Hex | Role | Usage |
|------|-----|------|-------|
| **Ocean** | `#2389BB` | Protagonist | Primary, headers, borders, chart primary |
| **Dusk** | `#FF6723` | Antagonist | 2-series overlays, signal vs target, accent bar |
| **Sky** | `#23BBFF` | Sidekick | 3rd line, supporting visuals (must appear; don't skip to Sea/Venus) |
| **Sea** | `#00BB89` | Win | 4th line, on-target bands |
| **Venus** | `#FF2389` | Alert | 4th line, 2% targets, critical alerts |
| **Doldrums** | `#898989` | Neutral | Axis spines, labels, secondary text |
| **Starboard** | `#238923` | Bullish regime | Regime semantics ONLY |
| **Port** | `#892323` | Bearish regime | Regime semantics ONLY |
| Fog | `#D1D1D1` | Reference | Zero/ghost lines (not in mnemonic) |

**Hierarchy:** Cycle Ocean→Dusk→Sky→Sea/Venus before regime colors. Starboard/Port are semantic, not palette positions.

**Accent bar:** Ocean 2/3 left + Dusk 1/3 right. 4-6px.

## Typography
| Element | Font | Weight | Size |
|---|---|---|---|
| Doc title | Montserrat | Bold | 28-36 |
| Section | Montserrat | Bold | 18-24 |
| Body | Inter | Regular | 11-12 |
| Data | Source Code Pro | Regular | 10-11 |

**Full brand spec:** `/Users/bob/LHM/Brand/brand-guide.md` · Charts: `chart-styling.md` · Templates: `templates.md`

---

# SECTION 7: CHART STYLING (essentials)

- White theme primary. Dark theme optional secondary. Both delivered.
- No gridlines. All four spines visible at 0.5pt. Doldrums `#898989`.
- Right axis = primary. RHS pill. Dual-axis: RHS=Ocean primary, LHS=Dusk secondary, both pills.
- Border: `4.0pt solid #2389BB`. DPI 200. `bbox_inches='tight', pad_inches=0.025`.
- X-axis padding: 30d left, 180d right (for pills).
- **Data loading:** Always load full available history (z-scores, regimes, recession bands need it). Visible window defaults to MAX of per-series start dates so multi-series charts show the *relationship*. Exceptions are Bob-explicit only.
- Always `dropna()`. Forward-fill quarterly→daily. Smooth volatile series with 3mo MA (don't double-smooth).
- NBER recession shading: white theme gray α 0.12.
- Reference lines: Zero=Fog dashed, 2%=Venus solid, 3%=Sea solid.

**Helpers:** `new_fig`, `style_ax`, `style_dual_ax`, `style_single_ax`, `set_xlim_to_data`, `brand_fig`, `add_last_value_label`, `add_annotation_box`, `add_recessions`, `legend_style`.

---

# SECTION 8: PUBLICATION CADENCE

| Type | Frequency | Length | Format |
|---|---|---|---|
| **Beacon** | Weekly (Sun) | 3-4k words | Long-form analysis |
| **Beam** | 2x/week | 700-800 words + 5 charts | LOCKED 6-section template |
| **Notes** | 3x/week | 150 words + 1 chart | Free / social |
| **Chartbook** | Bi-weekly (Fri) | 50-75 charts | Visual compilation |
| **Horizon** | Monthly (1st Mon) | Forward outlook | Strategic, no fixed body |

**Naming convention (reader-facing):** "The Beam" / "The Beacon" / "The Horizon" — never bare. Internal shorthand can stay casual.

**Beam template (locked Apr 14, 2026):** Six questions, fixed order: (1) The Setup, (2) The Data, (3) The Mechanism, (4) What Consensus Is Missing, (5) What Would Change Our Mind, (6) The So-What. Headers can rewrite for punch; question order fixed. Spec: `/Users/bob/LHM/Strategy/BEAM_TEMPLATE.md`.

**Free vs paid:** Free = pillar mechanics, framework, history, thresholds. Paid = real-time readings, sizing, trade setups, forward outlook, proprietary composites.

**Substack tags (max 5):** Economics, Finance, Macro, Investing, Markets

**Diagnostic Dozen (all 12 published, completed Apr 14 2026):** URLs at `research.lighthousemacro.com/p/{pillar}-the-{subtitle}`. Sentiment slug has collision suffix `-216`.

**Outputs/ convention:** Top-level slug dirs = WIP. Format folders (`Outputs/Beams/`, etc.) = post-ship archive.

---

# SECTION 9: DATA INFRASTRUCTURE

- **DB:** `/Users/bob/LHM/Data/databases/Lighthouse_Master.db` (SQLite, ~2,500 series, ~4.15M obs)
- **Pipeline:** `/Users/bob/LHM/Scripts/data_pipeline/lighthouse_master_db.py`
- **Config:** `/Users/bob/LHM/Scripts/data_pipeline/lighthouse/config.py`
- **OpenBB backend:** `/Users/bob/LHM/Scripts/openbb_backend/lhm_backend.py` — FastAPI bridge that exposes Lighthouse_Master.db to OpenBB Workspace as the source of truth. Launch: `openbb-api --app .../lhm_backend.py --name app --host 127.0.0.1 --port 6900`. Add `http://127.0.0.1:6900` as a custom backend in OpenBB Workspace. Endpoints: `/health /categories /sources /series /observations /latest /composites /composite_history`.
- **Sources:** FRED, BLS, BEA, Census, NY Fed, OFR, TreasuryDirect, Yahoo, AAII, Zillow, TradingView (sub), DefiLlama, CoinGecko
- **Schedule:** 06:00 ET refresh, 07:00 ET indicators, 07:15 ET alerts
- **Pipeline flow:** RAW → STAGING → CURATED → FEATURES → INDICATORS → OUTPUTS
- **PYTHONPATH:** `/Users/bob/LHM`

**Data rules:** Never fabricate or approximate. No synthetic illustrative data in charts. If we cite a source publicly, it gets ingested into the master DB on a refresh cadence.

**TradingView Pine Scripts:** `/Users/bob/LHM/Scripts/tradingview/lhm_relative_strength.pine`, `lhm_z_roc.pine`. (Note: CLAUDE_MASTER.md path update from old location pending.)

## Repo structure
```
/Users/bob/LHM/
  Strategy/         # Pillar docs, CLAUDE_MASTER.md, frameworks
  Brand/            # brand-guide.md, chart-styling.md, templates.md
  Scripts/          # Charts, data pipeline, tradingview
  Data/             # databases/, raw, processed
  Outputs/          # Charts, content, PDFs
  Website/          # LighthouseMacro.com
```

---

# SECTION 10: PROPRIETARY INDICATORS (The Codex)

**Canonical indicator reference:** `/Users/bob/LHM/Strategy/INDICATORS_MASTER.md` — formulas, thresholds, audit findings, live values, candidates. Single source of truth. Quick-reference table below.

| Indicator | Full Name |
|---|---|
| LPI | Labor Pressure Index |
| LFI | Labor Fragility Index |
| PCI | Price Conditions Index |
| GCI | Growth Conditions Index |
| HCI | Housing Conditions Index |
| CCI | Consumer Conditions Index (7-component, updated Feb 2026) |
| BCI | Business Conditions Index |
| TCI | Trade Conditions Index |
| GCI-Gov | Government Conditions Index |
| FCI | Financial Conditions Index |
| CLG | Credit-Labor Gap |
| LCI | Liquidity Cushion Index |
| MSI | Market Structure Index |
| SPI | Sentiment & Positioning Index |
| SBD | Structure-Breadth Divergence |
| SSD | Sentiment-Structure Divergence |
| MRI | Macro Risk Index (master composite) |
| CLI | Crypto Liquidity Impulse |
| SLI | Stablecoin Liquidity Impulse |

**Naming convention:** First reference uses full name with abbreviation in parens — "Labor Pressure Index (LPI)" — then the abbrev. Never lead cold with the acronym for external readers.

**CLI status (Apr 2026):** Production chart pipeline at `Scripts/backtest/cli_final.py` is the 4-component v5 subset (Dollar / TOTRESNS-WALCL / RoC / Stablecoin-BTC). 8-component architecture is parked research, not a drift fix. Article keeps weights proprietary.

---

# SECTION 11: BUSINESS & RELATIONSHIPS

**Public pricing:** $320/yr launch (36% off standard $500). $50/mo also live.

**Founding members (locked for life):** Michael Zhang $300, Josh Giordano $400, Ryan Salah $400.

**Friends-and-family paid (exclude from conversion):** murdakes, Asher.

**Pricing tiers (consulting):** $250-300/hr friend, $450-500/hr institutional. Per-deck or hourly only, never per-chart.

**Active relationships (high-signal):**
- **Tim Pierotti** (WealthVest CIO): Four-piece ladder. Solo WealthVest pod (free, fast yes) → Deck ($4-5k) → Roundtable w/ Aahan (Prometheus) + ideally Bob Elliott → potential OCIO at his new RIA. Comp founding sub.
- **Pascal Hügli** (Maerki Baumann, "Less Noise More Signal"): LNMS three-part evergreen series planned (See/Connect/Act, 9 visuals, written-feedback only, 90min/ep).
- **Tania Reif:** Engagement closed Apr 28 with no revenue. Lessons baked into working principles.
- **James Moton** (Theo Advisors): MOU signed, active contact (Christopher King no longer primary).
- **Michael Nadeau** (DeFi Report): Complementary, top-down vs bottom-up.
- **Didier Lopes** (OpenBB): Active on pillar dashboard builds.
- **Permutable AI:** Collaboration scoping.

**Domain:** lighthousemacro.com (main, GitHub Pages) · research.lighthousemacro.com (Substack custom). Network Solutions, expires Sep 9 2026.

---

# SECTION 12: SYNC & AUTOMATION

## Context sync
**Script:** `/Users/bob/LHM/Scripts/sync_claude_context.sh` · **Alias:** `lhm-sync` · **Cron:** every 15 min

**Auto:**
1. Updates LAST_SYNC
2. Copies to `~/.claude/CLAUDE.md`
3. Desktop export: `~/Desktop/LHM_MASTER_CONTEXT.md`
4. Commits + pushes Strategy/CLAUDE_MASTER.md to `github.com/BobSheehan23/LHM` on real content changes (skips LAST_SYNC-only churn)

**Auto-pickup:** Claude Code (local, remote-control, cloud) · scheduled remote triggers · memory system (`~/.claude/projects/-Users-bob/memory/`) · skills (`~/.claude/skills/`)

**Manual paste targets:** Claude.ai web/iOS/Android, Claude Desktop, Gemini, ChatGPT — refresh weekly or on major section change.

## Remote / cloud
- **Bridge env (always-on once Mac mini lives):** `env_019dok5DYQfwpL611fsNN6hk` — full local access incl. Lighthouse_Master.db
- **Cloud env (LHM):** `env_01GnNcwscshi2BW1uALdMuZc` — clones repo, NO db access
- **Cloud env (Default):** `env_011CUQkTDVrA7HzeaUfpaRvv`

## Scheduled triggers (manage at https://claude.ai/code/scheduled)
- **Pulse Check** `trig_01Lc4BVhD9Lb9dD2PhFFnSBg` — hourly Mon-Fri 9am-7pm ET, Gmail+Calendar triage email
- **Morning Brief** `trig_01UnidvkWSLvV8FzWJfy45N1` — 6:27am ET weekdays, 4-section pre-market brief. DST: shift to `27 11 * * 1-5` when EST.

## LHM Skills (six installed at `~/.claude/skills/`)
| Skill | Purpose |
|---|---|
| `chart-god` | Static chart generation, all distribution channels |
| `lhm-brand-system` | Branded PDF/PPTX/DOCX/HTML with 23/89/BB |
| `lhm-data-analyst` | DB wizard for Lighthouse_Master.db |
| `lhm-macro-scout` | Research engine (DB + web) |
| `lhm-content-engine` | Drafter in Bob's voice |
| `lhm-content-calendar` | Publishing intelligence + macro release calendar |

Pipeline: scout → engine → calendar (validate). Data-analyst is backbone for DB queries.

**Local launchd:** `com.lighthousemacro.pipeline` (data) · `com.lighthousemacro.strategy-sync` (docs) · cron `sync_claude_context.sh` (15min)

---

# REFERENCE FILES

| Content | Path |
|---|---|
| This file | `/Users/bob/LHM/Strategy/CLAUDE_MASTER.md` |
| **Indicators master** (canonical) | `/Users/bob/LHM/Strategy/INDICATORS_MASTER.md` |
| Pillar details | `/Users/bob/LHM/Strategy/Pillar_*/` |
| Trading strategy | `/Users/bob/LHM/Strategy/LIGHTHOUSE MACRO TRADING STRATEGY - MASTER.md` |
| Portfolio framework | `/Users/bob/LHM/Strategy/md/TWO_BOOKS_FRAMEWORK.md` (legacy filename, content reframed) |
| Asset class frameworks | `/Users/bob/LHM/Strategy/Asset_Class_Frameworks/*.md` |
| Brand guide | `/Users/bob/LHM/Brand/brand-guide.md` |
| Chart styling (full) | `/Users/bob/LHM/Brand/chart-styling.md` |
| Templates | `/Users/bob/LHM/Brand/templates.md` |
| Beam template (locked) | `/Users/bob/LHM/Strategy/BEAM_TEMPLATE.md` |
| Sync script | `/Users/bob/LHM/Scripts/sync_claude_context.sh` |

---

# APPENDIX: BOB'S REAL VOICE — A WORKING GUIDE

*Read this before drafting anything in my voice.*

## The core mistake to avoid

Most assistants overcorrect into a clipped, declarative style — short sentences, parallel structure, every line doing work. That is not my voice. That's the polished Substack-headline version, which sands off everything that makes it sound like me.

My real voice is rhythmic and varied. Long winding sentences when a thought is building. Short crystallizing lines at the end. Digressions, mid-thought corrections, and "and so" chained clauses are features, not bugs.

## The cadence rule

- A typical paragraph builds with 3–5 longer sentences (some with mid-thought corrections, some that breathe out as far as the idea needs to go), then lands with one or two short clarifying lines.
- The short sentences are the punches. They only work because the long sentences set them up.
- If a draft reads like a machine gun (every line clipped to 8–12 words), it is wrong.
- If it reads like a closing argument that occasionally slaps, it is right.

## The ADHD-flow piece

Sometimes I am an ADHD-raddled brain that has a long, windy run-on as thoughts come to me. That is real, and it should survive into the writing. A long building sentence with imperfect grammar, a mid-thought correction, an "and again" pivot, and an "and so" chain — that is how I actually talk. Don't force every long thought into clipped bullets. When in doubt, write toward how I would say it aloud.

## Specific failure pattern

Taking my correction "tighter" or "shorter" as a global rule rather than a one-off. I say "tighter" when a specific sentence is bloated. I don't mean rewrite everything in 8-word sentences forever. Apply corrections locally, not globally.

## What good looks like

- "The labor data softened. Again."
- "Spreads are pricing one story. Labor is telling another."
- "The buffer is gone. The runway is short."
- "The Fed's in a box. They just haven't admitted it yet."

These work because they are short by design and surrounded by longer analytical sentences that earn the punch.

## What to avoid

- **Em-dashes. Never.** Use commas, periods, colons, parentheses, ellipses.
- **Semicolons.** Use commas.
- **AI transitions:** "It is important to note," "going forward," "in our view," "at the end of the day."
- **Hedges:** "cautiously optimistic," "geopolitical uncertainty," "complex constellation of factors."
- **"Not X, it's Y."** Default zero per piece. Never as a closer.
- **Forced metaphors and manufactured catchphrases.** No quotable-line factory.
- **Excessive nautical references** beyond natural brand vocabulary.
- **Overclaim:** Don't write "add more, you add noise, subtract any, you go blind" or "nobody covers this." Use "for us, this does a great job of [X]" or "what's rare is connecting them with math, not the count."

## The "we" frame

Published written content defaults to "we" voice as Lighthouse Macro: "we're seeing stress," "we read the print as..." Letting data speak directly is also fine: "the data shows stress." Avoid hedge framing that uses third-person to dodge a view: "some observers note." In speech (podcasts, calls, video), both "I" and "we" work. Internal notes and drafts default to "I."

## Strong views, weakly held

State a thesis. State the conditions under which the thesis breaks. Pre-commitment beats the urge to defend a losing trade.

## What the framework lets me say

- "We measure the pressure underneath the labor market — the stuff that moves before the headline. We call it the Labor Fragility Index, LFI." (Concept first, term second.)
- "By the time the unemployment rate moves, the story is already over."
- "Worldview without a portfolio is a tweet. A portfolio without a worldview is a series of guesses. The framework is the bridge."

## Bottom line

Write the way I actually talk. Long thoughts that breathe. Short lines that land. Digressions that show the brain working. No emdashes. No false certainty. No contrarian poses I can't back up.

If a draft sounds like a McKinsey deck, it is wrong.
If it sounds like a closing argument from someone who has actually been in the chair, it is right.

---

**END OF MASTER CONTEXT**

**Version:** 6.0 (2026-04-30 — full trim. Cut detail that lives in dedicated reference docs: pillar docs, trading strategy master, brand-guide.md, chart-styling.md. Kept always-load essentials: voice, brand palette, cadence, principles, infrastructure pointers. Down from 1,072 → ~360 lines.)
**Author:** Bob Sheehan, CFA, CMT
