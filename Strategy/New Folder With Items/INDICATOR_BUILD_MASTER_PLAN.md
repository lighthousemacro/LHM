# Indicator Build Master Plan

**Author:** Bob Sheehan, CFA, CMT | Lighthouse Macro
**Created:** 2026-04-23
**Status:** Active. Supersedes `/Users/bob/LHM/_Inbox/misc/indicator_optimization/INDICATOR_OPTIMIZATION_CONTEXT.md` (Feb 2026, deprecated — kept for historical reference only).
**Assumption:** All 12 pillar docs are finalized at equal depth. The pillar rebuild in progress completes before Phase 1 executes.

---

## What This Is

Single source of truth for the full indicator buildout across Lighthouse Macro's framework. Covers three distinct layers (composites, tradeable signals, descriptive indicators), sequencing, methodology standards, and governance. Written as an internal working doc — hand it to any fresh Claude session or future-Bob and the full plan is recoverable.

---

## The Three Layers

Not every indicator serves the same purpose. Keeping these separate prevents methodology confusion.

| Layer | Purpose | Validation | Examples |
|---|---|---|---|
| **Composites** | Feed MRI, drive allocation bands and regime multiplier | Forward returns or forward domain variable, OOS optimization | LPI, PCI, GCI, ..., MRI |
| **Tradeable signals** | Standalone entry/exit or timing signals | Quintile sorts, slugging, t-stats, CLI-grade rigor | CLI, CLG, SBD, SSD, future standalones |
| **Descriptive indicators** | Make a thing visible that raw data doesn't | Historical legibility, information vs noise | Hires/Quits, V/U, ISM mfg vs services spread, etc. |

Optimization work (Phases 0-4) applies to layers 1 and 2. The descriptive atlas (Phase 5) is cataloguing and charting, not optimization. Cross-pillar divergences (Phase 6) sit between layers 1 and 2.

---

## Current State (Anchor)

- **12 pillars finalized** at equal depth. Composite formulas documented in each `PILLAR [1-12] *.md` and in `CLAUDE_MASTER.md` Section 3.
- **MRI judgment weights in place** per `CLAUDE_MASTER.md` Section 3. Current weights sum to 1.00, set by reasoning not empirics.
- **CLI published (March 10, 2026)** as the 8-component architecture (Tier 1 Macro + Tier 2 Plumbing + Tier 3 Crypto-Native + leverage regime filter). Public article at `/Users/bob/Desktop/_Archive/2026-03/CLI_Substack_Article_March10.html`.
- **CLI drift flagged 2026-04-22.** Production script `/Users/bob/LHM/Scripts/backtest/cli_final.py` renders a 4-component robustness subset, not the published 8-component build. Needs rebuild. See Phase 0.
- **MRI optimization doc written** at `/Users/bob/LHM/Strategy/MRI_WEIGHT_OPTIMIZATION.md`. 7-phase script ready to execute.
- **Data:** `Lighthouse_Master.db` (~2,141 series), pillar sub-DBs rebuilt daily.

---

## Known Caveats

Flag these explicitly so a fresh Claude session (or future-Bob) doesn't walk into them blind.

### 1. CLI component-count confusion across artifacts
Three different numbers have appeared in CLI references:
- **8 components** — the published March 10 Substack article and `CLAUDE_MASTER.md` Section 3. This is canonical.
- **4 components** — `cli_final.py` robustness subset (Feb 2026) that became the default chart source by path dependency. This is the drift flagged 2026-04-22.
- **10 components** — appeared in the March 2026 prompt that generated `MRI_WEIGHT_OPTIMIZATION.md`. Source unclear, possibly prompt bloat or a mid-March revision that didn't land in any persistent doc.

Phase 0 must resolve this to a single truth: the 8-component published architecture. Every downstream doc should be auditable against it.

### 2. `mri_weight_optimization.py` has never been executed
The script was written in a Claude.ai web session that had no access to `Lighthouse_Master.db`. It was built blind against the context file and the CLI methodology description — structurally sound but unverified against real data. Expect at least one debugging pass on first run:
- SPX series_id may not match any of the candidates (`SP500`, `SPX`, `GSPC`, `^GSPC`, `SPY`) — the script will print alternatives from `series_meta` if it fails
- Pillar index sparsity could truncate the aligned dataset severely — check date ranges per pillar before trusting the quintile sort
- Early-period quintile cuts may fail with `duplicates='drop'` if z-scores cluster; already handled but worth watching
- SLSQP with 30 restarts on 12 weights is tractable but not instant — budget 5-15 minutes per optimization run

Also: inline comments reference "CLI standard" methodology. The methodology itself (expanding z-scores, quintile sorts, walk-forward) is self-contained and valid. But if a reviewer follows the "CLI standard" reference back to `cli_final.py`, they hit the 4-component drift. Rebuild CLI first (Phase 0) so the audit trail terminates at the right file.

---

## Phase 0: CLI Rebuild (Template Fix)

**Status:** Blocker. Must happen before Phase 1 methodology citations hold.

Every subsequent optimization cites CLI as the methodological template. If the CLI reference script doesn't match the published CLI architecture, the audit trail rots and every downstream doc inherits the wrong quality bar.

**Tasks:**
1. Build `/Users/bob/LHM/Scripts/backtest/cli_v8_production.py` reproducing the 8-component published architecture:
   - Tier 1 (Macro Liquidity Tide, 40%): Global M2 Momentum, DXY 63D RoC
   - Tier 2 (US Plumbing Mechanics, 35%): WALCL, TGA, RRP, SOFR-IORB, HY OAS (inverted)
   - Tier 3 (Crypto-Native Transmission, 25%): Stablecoin supply momentum, BTC ETF 20D flows, Exchange stablecoin reserves
   - Leverage Regime Filter (multiplicative): perp funding rates
2. Reproduce quintile/slugging/tercile numbers from the March 10 Substack article within rounding tolerance (Q5-Q1 +13.3/+22.0/+27.2 at 21/42/63D, t-stats 14-16, Q5 slugging 4.81x/4.56x/3.70x).
3. Archive `cli_final.py` to `/Users/bob/LHM/Scripts/backtest/_deprecated/cli_final_4component_2026Q1.py` with a header note explaining the drift.
4. Repoint `cli_chart_data.csv` generator at the 8-component version.
5. Update `/Users/bob/LHM/Strategy/CLI_CRYPTO_LIQUIDITY_IMPULSE.md` to reflect the rebuilt production model.

**Deliverable:** Working `cli_v8_production.py` whose outputs reconcile with the published article. The file becomes the canonical template referenced by every Phase 1-4 optimization doc.

---

## Phase 1: MRI Weight Optimization

**Status:** Doc + script ready. Execute after Phase 0.
**Spec:** `/Users/bob/LHM/Strategy/MRI_WEIGHT_OPTIMIZATION.md`
**Script:** `/Users/bob/LHM/Scripts/backtest/mri_weight_optimization.py`

Highest-leverage single optimization. MRI drives the equity allocation bands (65-70% at low risk down to 25-35% at crisis) and the regime multiplier for position sizing. Getting the 12 pillar weights right has the biggest downstream impact on the book.

**Target variable:** Forward SPX log returns, primary horizon 63d (quarterly, matches tactical core book timeframe). Secondary targets: 21d, 42d, 126d, 252d; forward max drawdown at 63/126/252d.

**Methodology:** Expanding z-scores (min 63 periods, ±3 winsorized). Quintile sorts with monotonicity + t-stats + slugging + rank IC. SLSQP optimization with 30 Dirichlet restarts, bounds [0.02, 0.30] per weight. 90/10 IS/OOS split plus 5-split walk-forward. Sortino on Q1-Q5 spread as default objective (switchable to spread or IC).

**Invalidation criteria** (weights rejected if any hold):
1. IS/OOS spread > 2x at primary horizon
2. Walk-forward weight std > 0.06 for 3+ pillars
3. Monotonicity breaks OOS at primary horizon
4. Any weight > 0.25 (dominance → overfit)
5. Annual IC sign flip in >30% of windows
6. Elevated regime MDD not meaningfully worse than Low Risk

**Decision framework:** adopt / shrink-toward-judgment / keep current. Full table in the MRI doc.

**Publishing output:** Beam. "How we rebuilt the master signal."

---

## Phase 2: Tier A Composites (MSI, SPI, LCI)

Run in parallel — independent optimizations. Each gets its own `*_WEIGHT_OPTIMIZATION.md` doc modeled on the MRI one. Only three things differ: components, target variable, objective function.

### MSI — Market Structure Index
- **Drives:** gross exposure decisions
- **Components:** 11 (price vs 50d/200d, slopes, Z-RoC, breadth %>20d/50d/200d, NH-NL, AD slope, McClellan)
- **Target:** forward SPX returns, same horizons as MRI
- **Objective:** Sortino on Q1-Q5 spread (identical to MRI)
- **Secondary test:** Does MSI alone (outside MRI) produce tradeable signals at Q1/Q5 extremes? If yes, it's also a standalone signal — document in Phase 4 as well.

### SPI — Sentiment & Positioning Index
- **Drives:** contrarian fades at extremes
- **Components:** 8 (Put/Call 10d, VIX vs 50d, AAII, NAAIM, II, ETF flows, VIX backwardation, MMF assets)
- **Target:** forward SPX returns at shorter horizons (5d, 10d, 21d primary)
- **Objective:** **This is the methodology divergence.** SPI is contrarian — don't reward monotonic Q1→Q5. Reward tail asymmetry: `mean(|Q1_ret|) + mean(|Q5_ret|) - mean(|Q3_ret|)`. Middle quintiles are noise for a contrarian signal. Validate separately: conditional forward reversal magnitude at SPI > +1.5 and SPI < -1.0.
- **Note in script:** standard quintile-monotonicity assertions should be disabled; SPI is expected to be non-monotonic by design.

### LCI — Liquidity Cushion Index
- **Drives:** cash allocation
- **Components:** 7 (Reserves vs LCLOR, EFFR-IORB, SOFR-IORB, RRP, GCF-TPR, Dealer positioning, EUR/USD basis)
- **Target:** **Not forward equity returns.** Forward funding-stress events: SOFR spikes, repo rate dislocations, HY OAS widening events, cross-currency basis blowouts.
- **Objective:** event-based validation. Count funding-stress episodes caught at N-week lead when LCI < -0.5. Supplement with quintile sort against forward HY OAS change.
- **Horizon:** short — 1-4 weeks primary, because LCI is designed as an acute-stress indicator, not a regime signal.

**Deliverables:** three docs (`MSI_WEIGHT_OPTIMIZATION.md`, `SPI_WEIGHT_OPTIMIZATION.md`, `LCI_WEIGHT_OPTIMIZATION.md`), three scripts, three adoption decisions.

**Publishing output:** one compiled Beam ("We rebuilt three more signals") or three Notes.

---

## Phase 3: Tier B Pillars (9 Diagnostic Composites)

Nine pillars feeding MRI as inputs. **Do not optimize these against forward equity returns** — that creates collinearity with MRI and double-counts the Phase 1 work. Each optimizes against its *domain* variable. The point is to make each pillar the best possible thermometer for its domain. MRI handles translation to positioning.

Run sequentially, two per week feasible after Phases 1-2 complete.

| Pillar | Target Variable | Primary Horizon |
|---|---|---|
| **LPI** | Forward UR change, forward quits rate | 6-12m |
| **PCI** | Forward core PCE YoY | 3-12m |
| **GCI** | Forward real GDP YoY (or ISM composite) | 3-6m |
| **HCI** | Forward housing starts YoY | 6-9m |
| **CCI** | Forward real PCE YoY *(verify Feb 2026 v2 rebuild holds against new pillar doc)* | 6-12m |
| **BCI** | Forward non-def capgoods orders YoY | 4-8m |
| **TCI** | Forward net exports contribution to GDP | 3-6m |
| **GCI_Gov** | Forward term premium (ACM) | structural |
| **FCI** | Forward HY default rate | 6-12m |

**Methodology:** Same framework as MRI/Phase 2, except:
- Target is the domain variable, not returns
- Quintile sort is against domain variable
- Sortino objective replaced with rank IC (spread methodology less meaningful for non-return targets)
- Monotonicity still required — higher pillar reading should correspond to higher/lower domain outcome

**Exception — threshold optimization:** where a pillar has a direct trade mapping (e.g., "LFI > +0.8 = reduce cyclical equity"), backtest that *specific threshold* against that *specific trade expression*. That's a threshold optimization, separate exercise, run after weight optimization settles.

**Publishing output:** each pillar optimization = Beam opportunity. Compiled = Chartbook section.

---

## Phase 4: Standalone Signals

Not composites. Not constrained by pillar structure. Use framework data but validated as independent tradeable signals. Each proven signal gets the full CLI 10-point documentation template and becomes its own asset.

Priority order:

1. **CLG — Credit-Labor Gap as credit timing tool.** Already defined: `z(HY_OAS) - z(LFI)`. Target: forward HY OAS widening events, forward IG→HY downgrade ratio. Test binary signal at CLG < -1.0 for credit protection timing.
2. **SBD — Structure-Breadth Divergence.** Already defined: `z(Price_vs_200d) - z(%>50d_MA)`. Binary signal testing at SBD > +1.0 (distribution warning). Target: forward SPX returns and drawdown asymmetry.
3. **SSD — Sentiment-Structure Divergence.** Already defined: `z(SPI) + z(MSI)`. Capitulation detector at SSD > +1.5, blow-off detector at SSD < -1.5. Target: forward reversal magnitude and duration.
4. **Quits-to-Claims ratio.** New build. Labor data → credit timing. Target: forward HY OAS widening at 3-6m horizons.
5. **Dealer Positioning vs Auction Tails.** New build. Plumbing data → rate vol. Target: forward MOVE index, forward 10Y realized vol.
6. **Breadth thrust binary.** %>20d going from <30% to >70% in 10d (Zweig-style). Target: forward SPX returns at 3/6/12m.

**Deliverables:** up to 6 standalone indicator docs in `/Users/bob/LHM/Strategy/`, each modeled on `CLI_CRYPTO_LIQUIDITY_IMPULSE.md`. Each with its own script in `/Users/bob/LHM/Scripts/backtest/`.

**Publishing output:** each standalone signal = Beam + promotional thread. The full set = potential Horizon piece on "Signals beyond the pillars."

---

## Phase 5: Descriptive Atlas

Indicators that earn their keep by making something visible that raw data doesn't. No forward-return optimization needed. Validation: does it make the 2008/2020/2022 regime legible in a way the raw series doesn't?

Built by extracting from the finalized pillar docs — once pillar rebuild is complete, this is mechanical cataloguing, not speculation.

**Deliverable:** `/Users/bob/LHM/Strategy/DESCRIPTIVE_INDICATORS.md`. Single flat doc, ~60-80 entries across pillars. Each entry:
- Name
- Formula
- Chart type
- What it shows (1-2 sentences)
- Historical example where it was informative
- Pillar it belongs to

**Candidate list (to validate against finalized pillar docs):**

**Labor:** Hires/Quits ratio, Full-time/Part-time ratio, Median vs mean UR duration, Prime-age vs headline LFPR, V/U ratio (Beveridge in one number)

**Prices:** Supercore ex-housing vs shelter, Goods vs Services CPI spread, Trimmed mean vs core, ISM prices paid vs CPI lead

**Growth:** ISM mfg vs services spread, LEI/CEI/LAG diffusion, Real final sales to private domestic purchasers YoY

**Housing:** Payment-to-income affordability, New vs Existing sales ratio, Months' supply existing vs new, NAHB traffic vs current sales

**Consumer:** Savings rate vs 10y avg, Real DPI ex-transfers YoY, CC delinquency 30d vs 90d, Services vs Goods PCE YoY

**Business:** Regional Fed capex intentions composite vs actual orders, Temp help vs total payrolls, Inventory/Sales by sector

**Trade:** Import vs Export volume YoY spread, Real broad dollar vs nominal, Container rates vs goods CPI lead

**Government:** Term premium vs neutral rate, Bills vs coupons issuance, Net interest/revenue ratio

**Financial:** HY OAS vs realized default rate, SLOOS C&I standards vs HY spreads, IG-HY spread

**Plumbing:** Reserves/Bank assets ratio, Bills/Total issuance, Foreign Treasury holdings/total

**Market Structure:** Equal-weight/Cap-weight ratio, Cyclicals/Defensives, Small/Large cap, Junk/IG, A-D line divergence from price

**Sentiment:** Put/Call 10d vs 63d z-score, VIX term structure slope, Fund manager cash (BofA) vs SPX, Gold/SPX ratio

**Chart pack tie-in:** these populate the 50-100 charts per pillar in the chart pack product (Pierotti-validated). Composite = 1-2 charts. Atlas fills the rest.

---

## Phase 6: Cross-Pillar Divergences

Proprietary by construction — only exist because we built the 12-pillar framework. Spreads and differentials between pillar composites that surface regime shifts, stagflation, late-cycle, and divergence setups.

**Deliverable:** `/Users/bob/LHM/Strategy/CROSS_PILLAR_DIVERGENCES.md`. Each entry gets the standalone-signal treatment (formula, what it shows, threshold levels, historical examples).

**Already defined (test-validated in Phase 4):**
- **CLG** = `z(HY_OAS) - z(LFI)` — credit vs labor
- **SBD** = `z(Price_vs_200d) - z(%>50d_MA)` — price vs breadth
- **SSD** = `z(SPI) + z(MSI)` — sentiment vs structure

**New spreads to define and validate:**
- **MRI - MSI** — fundamental risk vs technical risk. Divergence signals regime shift.
- **GCI - LPI** — growth vs labor divergence. Late-cycle tell (growth holds up while labor cracks).
- **PCI - GCI** — stagflation gauge. Positive = prices accelerating while growth decelerates.
- **FCI - LCI** — credit stress vs plumbing stress. What kind of tightening is this?
- **GCI_Gov - LCI** — fiscal impulse vs monetary impulse. Push/pull dynamics.
- **HCI - BCI** — consumer-facing vs business-facing real economy. Which side breaks first?

Each needs: formula, z-score specification, threshold bands, backtested forward-return asymmetry (even if modest, the story matters), published examples.

**Publishing output:** this is a Horizon-grade piece. "The divergences that matter" or similar. High proprietary value because nobody else has the pillar structure to build these.

---

## Phase 7: Integration / Cross-Validation

Run after Phases 1-6 complete. One last sanity layer on the whole stack.

1. **Correlation matrix of all optimized indicators.** If MSI and MRI are 0.95 correlated, something's redundant. Detect and document.
2. **Incremental information test.** Does each standalone signal add independent info beyond optimized MRI? Regress forward returns on MRI + each standalone individually. Coefficient significance + R² delta. Flag standalones that are really just MRI in disguise.
3. **Regime-by-regime stability.** Does the full stack still work in 2008, 2020, 2022? One bad crisis breaks sizing confidence. Each major composite and standalone tested through each regime with notes on behavior.
4. **Weight-sensitivity audit.** For each optimized composite, perturb weights by ±10% and measure Q5-Q1 spread change. High sensitivity = fragile signal.

**Deliverable:** `/Users/bob/LHM/Strategy/INDICATOR_STACK_AUDIT.md`. Cross-validation results + go/no-go per indicator.

**Publishing output:** internal only, unless results are clean enough to publish as a credibility piece ("how we stress-tested our own framework").

---

## Governance

Three rules to prevent the CLI drift from happening again.

### 1. Adoption Rule
Optimized weights replace judgment weights only if:
- OOS Q5-Q1 spread improves by >10%, AND
- Monotonicity holds at primary horizon, AND
- Walk-forward weight stability (std < 0.06 for all but 1-2 pillars)

Otherwise keep judgment. Prevents chasing overfit.

### 2. Versioning Registry
Every optimization run tagged and logged in `/Users/bob/LHM/Strategy/optimization_registry.json`:
```json
{
  "indicator": "MRI",
  "version": "v2_optimized_2026Q2",
  "run_date": "2026-05-15",
  "weights": {...},
  "objective_value": 0.XXX,
  "oos_spread": 0.XXX,
  "decision": "adopt|shrink|keep",
  "rationale": "short text",
  "prior_version": "v1_judgment_2026"
}
```
Scripts filename-version accordingly: `mri_v1_judgment.py`, `mri_v2_optimized_2026Q2.py`. Production script at `mri_production.py` is a symlink or import shim pointing at the currently adopted version. No silent drift.

### 3. Shrinkage Option
When optimized weights improve signal but are unstable OOS, don't pick a binary. Test `FINAL_WEIGHTS = α * opt_dict + (1-α) * judgment_dict` at α = 0.25, 0.5, 0.75. Pick the α that maximizes OOS spread × stability. Often outperforms both pure judgment and pure optimization. Already contemplated in the MRI decision framework.

---

## Methodology Standards (Carried Across All Phases)

From the CLI build, inherited by every downstream optimization.

- **Z-scores:** Expanding window, min 63 periods, ±3.0 winsorized. Test rolling alternatives (504d, 756d) if expanding shows instability.
- **Quintile sorts:** Primary validation. Multiple horizons (5/10/21/42/63/126/252d, picked per signal's intended timeframe).
- **Monotonicity:** Strict 5-quintile preferred, 3-quintile (Q1 < Q3 < Q5) acceptable. Not required for contrarian signals (SPI).
- **Statistical significance:** t-stat on Q5-Q1 spread, p < 0.01 minimum, p < 0.001 preferred.
- **Slugging:** Win/loss size ratio per quintile. Catches asymmetry that win rate hides.
- **Regime analysis:** Tercile splits for cleaner classification.
- **Year-by-year stability:** Annual IC check for regime dependence.
- **OOS:** 90/10 split minimum, walk-forward preferred.
- **Never fabricate data.** Code-first, reproducibility-first.

---

## Publishing Leverage

Each phase maps to a content opportunity. Roughly 8 weeks of backtesting becomes 8+ weeks of content.

| Phase | Publishing Output |
|---|---|
| Phase 0 (CLI rebuild) | Beam — "We drifted. Here's what we fixed." (transparency piece) |
| Phase 1 (MRI) | Beam — "How we rebuilt the master signal" |
| Phase 2 (MSI/SPI/LCI) | One compiled Beam or three Notes |
| Phase 3 (9 Tier B pillars) | Beam per pillar (9 total) + Chartbook section |
| Phase 4 (Standalones) | Beam per signal + promotional thread each |
| Phase 5 (Descriptive atlas) | Feeds chart packs (Pierotti-validated product) |
| Phase 6 (Cross-pillar divergences) | Horizon-grade piece — "The divergences that matter" |
| Phase 7 (Integration audit) | Internal; optional credibility publish |

Total publishable surface from the full sweep: ~15-20 Beams, 1-2 Horizons, Chartbook content, a product (chart packs), plus framework-level differentiation vs any competitor.

---

## Sequencing Summary

```
[Parallel] Pillar rebuild completes (other window)
    ↓
Phase 0: CLI rebuild         [~1 week]
    ↓
Phase 1: MRI optimization    [~1-2 weeks]
    ↓
Phase 2: Tier A parallel     [~1-2 weeks]
    ↓
Phase 3: Tier B sequential   [~2-3 weeks]
    ↓
Phase 4: Standalone signals  [~2-3 weeks, can overlap w/ Phase 5]
    ↓
Phase 5: Descriptive atlas   [mechanical extract after pillars done]
    ↓
Phase 6: Cross-pillar divergences
    ↓
Phase 7: Integration audit
```

Total elapsed: ~8-10 weeks of focused backtesting, cataloguing, and documentation. Publishable output along the way.

---

## Reference Files

| Content | Path |
|---|---|
| This master plan | `/Users/bob/LHM/Strategy/INDICATOR_BUILD_MASTER_PLAN.md` |
| MRI optimization spec | `/Users/bob/LHM/Strategy/MRI_WEIGHT_OPTIMIZATION.md` |
| CLI published doc | `/Users/bob/LHM/Strategy/CLI_CRYPTO_LIQUIDITY_IMPULSE.md` |
| CLI published article | `/Users/bob/Desktop/_Archive/2026-03/CLI_Substack_Article_March10.html` |
| Deprecated context file | `/Users/bob/LHM/_Inbox/misc/indicator_optimization/INDICATOR_OPTIMIZATION_CONTEXT.md` (Feb 2026) |
| Pillar docs | `/Users/bob/LHM/Strategy/PILLAR [1-12] *.md` |
| Trading strategy | `/Users/bob/LHM/Strategy/LIGHTHOUSE MACRO TRADING STRATEGY - MASTER.md` |
| Master context | `/Users/bob/.claude/CLAUDE.md` → synced from `/Users/bob/LHM/Strategy/CLAUDE_MASTER.md` |
| Master database | `/Users/bob/LHM/Data/databases/Lighthouse_Master.db` |
| Pillar sub-DBs | `/Users/bob/LHM/Data/databases/pillars/` |
| Script directory | `/Users/bob/LHM/Scripts/backtest/` |
| Output directory | `/Users/bob/LHM/Outputs/` |

---

*Bob Sheehan, CFA, CMT | Founder & Chief Investment Officer*
*Lighthouse Macro | LighthouseMacro.com | @LHMacro*
