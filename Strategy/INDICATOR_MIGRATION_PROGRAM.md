# LHM INDICATOR MIGRATION PROGRAM — Resumable Spec

**Status as of 2026-05-16. This file is the single source of truth. It is
written to survive context compaction and session restarts. On resume: read
this top-to-bottom, then continue at the first incomplete phase.**

Approved by Bob 2026-05-16 ("it looks good"). Carte blanche to run the full
migration path autonomously, no further check-ins until a validated lineup
exists. Diagram: `Outputs/indicator_architecture_2026-05-16.html`.

---

## THE MANDATE

Re-found the LHM indicator framework on Macrosynergy-grade discipline. The
framework currently *asserts* predictive skill the data does not support
(proven empirically in Phase A — see scorecard below). Target: a registry of
many mathematically-sound indicators, each **validated out-of-sample against
the specific thing it predicts, in a specific role**. Broken ones get
re-optimized, re-targeted, or demoted to honest diagnostics. The framework
proves skill instead of asserting it.

`INDICATORS_MASTER.md` is treated as **UNVERIFIED, not gospel** (Bob:
"im not even sure if its right"). It gets **rebuilt from validated evidence,
not additively patched**. This overrides the older additive-only rule for
this program.

---

## SCOPE RECONCILIATION (2026-05-17, Bob correction — READ FIRST, overrides narrow framing)

Bob flagged two things and both are correct.

**1. The scope was too narrow.** Phase A (`signal_eval`) and Phase B
(`pillar_reoptimize_v3`, `signal_registry_v3`) collapsed the system to
~16 pillar composites times ONE winning target each. The ACTUAL system
is a multi-role registry already modeled May 8-9:
`Outputs/mri_optimization/pillar_registry_v{3,4,5,6}*` driven by
`Scripts/backtest/pillar_specs_v2.py`. Structure = per indicator times
{diagnostic, relative-predictive (~24 rotation pairs at 63/252d),
asset-predictive (13 asset targets), lead-lag event}. v3 = 300 cells /
115 "real"; v5 = 130 asset cells / 53 "real"; v6 = 776 lead-lag / 609
significant. THAT is the sheet, not 16-by-one.

**2. v3-v6 carries the SAME two leaks Phase B already caught**, so its
"real" counts are inflated, not ground truth:
- ref-in-basket TAUTOLOGY in the diagnostic companions
  (`LPI_diag_unrate` +0.85, `PCI_diag_corepce` +0.72,
  `SPI_diag_aaii_spread` −0.77 = the reference predicting itself);
- overlapping-horizon PSEUDO-REPLICATION in the 63/252d daily
  predictive / relperf / asset cells (same class as the pre-fix PCI
  +0.76; v5 "Inflation Heat → t10y2y_252d −0.60" is the tell).

**3. INDICATORS_MASTER.md is NOT the deliverable** (Bob, explicit). The
deliverable is the validated multi-role registry itself: the
`(indicator × role × target) → honest-OOS verdict + weights` table.
Strike "rebuild INDICATORS_MASTER" as the Phase B goal everywhere below.

**Corrected path (supersedes the narrow NEXT in the checklist):** re-run
the FULL multi-role v3-v6 registry through the leak-corrected harness —
diagnostic with the ref EXCLUDED from the basket, macro/asset/relative
predictive with PURGED non-overlap headline OOS IC, lead-lag as an honest
event study, noise-controlled throughout. Output replaces v3-v6's
inflated registry. The Phase B-1/B-2 survivors (PCI/GCI/HCI predictive;
HCI/FPI/BCI descriptive; CLG→HY-OAS) stand as the honest narrow-slice
result and a sanity anchor for the full re-run (any full-run number that
contradicts them without explanation is a bug).

---

## REGISTRY ARCHITECTURE (the target)

Each pillar's **expanded Tier-1 basket** feeds MULTIPLE composites, one per
role (registry of `(basket × target × role)` tuples — never one blended
guess per pillar):

| Role | Question | Target / method |
|---|---|---|
| **Diagnostic** | "what is X right now" | concurrent r vs ground-truth ref, |r| ≥ 0.6 floor |
| **Asset-predictive** | "X predicts SPX/DGS10/HY-OAS at h" | walk-forward OOS signed IC vs the asset |
| **Relative-predictive** | "X predicts the rotation" | OOS IC vs ratio (SPY/TLT, XLY/XLP, IWF/IWD, IAU/SGOV, SHY/TLT) |
| **Macro-predictive** *(ADDED 2026-05-16 per Bob)* | "when X moves, spending/inflation/hiring follows at h" | walk-forward OOS signed IC of X_t vs forward path of a macro series Y (PCE, core PCE, payrolls, etc.). This is the transmission-chain thesis made testable. |
| **Lead-lag event** | "when X breaches T, Y follows ~Nmo" | event study, binary, not continuous IC |

Every composite must pass the GATE before reaching INDICATORS_MASTER:
dual-objective optimize → noise-control check → vintage/point-in-time → only
then propagate.

**Vocabulary:** Pulse = vital-sign state. Impulse = its rate-of-change
(CLI/SLI family). They stack.

---

## METHODOLOGY (locked, Macrosynergy sklearn-native — Bob chose this)

- Features: component basket, zn-scored point-in-time (expanding mean/std,
  neutral=0, winsorize ±3σ) + 2 deterministic noise controls.
- Walk-forward: expanding window, refit cadence ~63 trading days, inner
  `TimeSeriesSplit(4)` CV. Candidate zoo: LinearRegression / Ridge(α grid) /
  ElasticNet(α,l1 grid). Model+hyperparams re-selected each refit.
- Dual-objective: maximize OOS predictive IC **subject to** concurrent
  descriptive |r| vs the pillar's ground-truth ref ≥ ~0.6. If the predictive
  model violates the floor, blend toward / fall back to the
  descriptive-weighted composite.
- Skill = OOS correlation, sign accuracy, balanced accuracy. **Never
  in-sample R².** Confidence band = OOS residual σ (±1.96σ).
- Honest fallback: OOS corr < 0.10 → no real skill → hold last value /
  demote to diagnostic, flagged. Do NOT extrapolate on noise.
- Reference implementations already built:
  - `Scripts/data_pipeline/compute_indices.py` :: `bridge_via_walkforward`
    (the working walk-forward+adaptive engine — REUSE THIS PATTERN).
  - `Scripts/backtest/signal_eval.py` (the scorecard harness — extend it
    with the macro-predictive role + the per-pillar TARGET registry).

---

## PHASE A RESULT (done — the empirical baseline, do not re-run unless data changed)

Tested point-in-time, OOS, vs each indicator's economic target:

- **Real, correctly-signed:** REC_PROB→recession (IC +0.14, sign 69%,
  n=13,285); CCI→XLY/XLP rotation (IC +0.16, n=9,279).
- **Damaging negatives:** LFI→recession IC +0.06 (sign 53% ≈ coin flip) —
  the flagship barely leads recession. PCI diagnostic vs concurrent core
  PCE IC −0.01 (doesn't even describe inflation).
- **Weak/noise (|IC|<0.1):** GCI, SPI, MSI, LPI, BCI.
- **FLIP vs expected sign (need sign-convention audit, may be registry
  error not model failure):** MRI/SPY (+0.50 but n=353 — no real history),
  FPI/DGS10, FPI/TLT, CLG/HY-OAS.
- **Caveat:** trust the >9,000-n reads; MRI/HCI/FCI/LCI small-n unreliable.

### MACRO-PREDICTIVE RESULT (done 2026-05-16 — the key finding)

The macro-predictive role surfaced real signal the asset/recession role
missed. **The framework's indicators ARE useful — in the transmission role,
not the asset-prediction role they'd been judged on.** Re-optimization must
target each composite at its best (role,target), per-composite:

- **LFI → forward PAYEMS (hiring), 126d: rankIC −0.37, n=1406, sign-ok.**
  Labor Fragility's real edge is leading HIRING, not recession (Phase A
  showed LFI→recession ≈ coin flip). Re-target LFI to hiring.
  **[REVISED — see PHASE B-1. This −0.37 reproduces EXACTLY (daily-overlap
  rankIC −0.371, n=1406) but is a FULL-SAMPLE, recession-dominated
  association with ≈0 OOS skill (purged WF OOS −0.10). "Re-target LFI to
  hiring" does NOT survive honest evaluation — LFI→hiring is a diagnostic,
  not a predictive composite.]**
- **LDI → PAYEMS rankIC +0.37 (n=449); LPI → PAYEMS rankIC +0.31 (n=483)**
  — labor pillar genuinely leads hiring.
- **PCI → forward core PCE, 126d: IC +0.16, OOS +0.29, n=1780, ok.** PCI's
  real role is macro-predictive (forward inflation), NOT asset-pred (DGS10,
  weak) nor concurrent diagnostic (failed). Re-target PCI.
- BCI → INDPRO rankIC +0.19 (ok, modest). GCI → PAYEMS +0.09 (weak).
- **CLG → UNRATE: rankIC +0.30 but sign FLIP** — strong monotonic relation,
  wrong sign vs my exp. CLG sign-convention audit needed (z(HY)−z(LFI));
  the relationship is real, the registry expected-sign is likely wrong.
- Insufficient n: HCI→INDPRO, MRI→UNRATE (MRI history problem persists).

Implication for re-opt: build per-composite to its winning role. Don't
keep judging LFI on recession or PCI on yields.

**REVISED by PHASE B-1 (2026-05-16):** the macro-pred rankICs above are
full-sample associations, NOT out-of-sample skill. Under purged
non-overlap walk-forward only PCI / GCI / HCI clear the bar. The PHASE B-1
RESULT section below supersedes the per-composite re-target list here.

This empirically confirmed the two April-30 audits
(`PILLAR_DESCRIPTIVE_ANALYSIS` + `PILLAR_BASKET_AUDIT` curated companion):
"no pillar composite earns the real-composite verdict"; CCI/BCI/FCI
descriptively broken; MSI/SPI optimized on half their published formula.

---

## PHASE B-1 RESULT — dual-objective re-optimizer (done 2026-05-16)

`Scripts/backtest/pillar_reoptimize_v3.py`. Expanded baskets, zn-scored
point-in-time, **purged/embargoed expanding walk-forward, NON-OVERLAPPING
headline OOS IC**, monthly grid for macro targets, impute-absent-to-neutral
(no survivorship). Full JSON + run log:
`Outputs/mri_optimization/pillar_reoptimize_v3.json`.

**Harness honesty — validated, not assumed.** (1) A daily-ffill
pseudo-replication leak was caught in smoke test (PCI inflated to OOS
+0.76); fixed → honest +0.62 with non-overlap ≈ overlap. (2) First-
principles check reproduces Phase A's LFI→PAYEMS EXACTLY (daily-overlap
rankIC −0.371, n=1406) → loaders/data correct, optimizer not
mis-specified. (3) Negative controls behave: MSI +0.02, SPI −0.03 (Phase
A weak/noise → honest ≈0 DEMOTE). (4) noise-control coef mass ≈0 on every
KEEP/BLEND pillar (BCI 0.12 the only elevated one).

Scorecard (OOS = non-overlap purged WF; ov = overlapping, for contrast;
dR = concurrent |r| vs ground-truth ref):

| Pillar | Winning target | OOS IC | ov | rankIC | dR | Verdict |
|---|---|---|---|---|---|---|
| PCI | fwd core PCE 6m | +0.62 | +0.59 | +0.49 | 0.69 | **BLEND λ0.8** |
| FCI | fwd PAYEMS 6m | +0.45 | +0.23 | +0.32 | −0.76 | KEEP `*` |
| GCI | fwd PAYEMS 6m | +0.37 | +0.28 | +0.43 | 0.88 | **KEEP** |
| TCI | fwd core PCE 6m | +0.31 | +0.26 | +0.47 | 0.38 | DEMOTE `†` |
| HCI | fwd INDPRO 6m | +0.22 | +0.18 | +0.31 | 0.66 | **KEEP** |
| BCI | fwd INDPRO 6m | +0.17 | +0.14 | +0.12 | 0.62 | BLEND λ0.85 |
| MRI | fwd UNRATE 12m | +0.19 | +0.06 | +0.05 | 0.39 | DEMOTE (n=23) |
| MSI | fwd SPY 3m | +0.02 | +0.00 | +0.07 | — | DEMOTE |
| SPI | fwd SPY 3m | −0.03 | −0.02 | −0.07 | — | DEMOTE |
| LFI/LPI/LDI | fwd PAYEMS 6m | −0.10 | −0.03 | +0.24 | — | DEMOTE |
| CLG | fwd UNRATE 6m | −0.11 | −0.04 | +0.36 | −0.73 | KEEP `*°` |
| FPI | fwd DGS10 6m | −0.22 | −0.25 | −0.10 | — | DEMOTE |
| LCI | fwd HY-OAS 3m | −0.30 | −0.31 | −0.00 | 0.42 | DEMOTE `†` |
| CCI | XLY/XLP 6m | n=9 | — | — | — | INVALID `‡` |

**THE HEADLINE — the program's celebrated finding does NOT survive.**
"LFI leads HIRING (rankIC −0.37)" reproduces exactly as a *full-sample*
statistic (daily −0.371 / monthly-overlap −0.318 / monthly NON-overlap
−0.484 — real, and NOT an overlap artifact). But it is recession-
dominated with **≈0 out-of-sample skill** (purged WF OOS −0.10, rank sign
flips to +0.24; toy expanding-OOS +0.009). This is the exact "asserts
skill the data does not support" failure the program exists to kill, one
layer up in our own Phase A reading. Honest verdict: **LFI → hiring is a
DIAGNOSTIC, not a predictive composite.** LFI's only real lead is forward
UNRATE (rankIC +0.395, correct sign, the original recession/labor-stress
thesis) and even that is still untested OOS. Do NOT re-target LFI to
hiring.

**Survivors (genuine, OOS-validated, descriptively coherent):** PCI,
GCI, HCI. BCI marginal (elevated noise ratio 0.12).

**DEMOTE is two different things — do not collapse them:** (a) no OOS
skill at all → FPI, MSI, SPI, the labor trio. (b) *predicts but fails the
0.60 descriptive-integrity floor* → TCI (OOS +0.31) and LCI (OOS −0.30)
are predictive-only diagnostics; keep as signals, not as pillar
composites.

**Caveats Phase B MUST resolve before any rebuild:**
- `*` FCI KEEP sits on a NEGATIVE descR (−0.76) with non-overlap (+0.45)
  ≫ overlap (+0.23): sign-convention + likely small-n inflation. Verify
  before trusting.
- `°` CLG OOS −0.11 is *at* the 0.10 floor — borderline KEEP; the
  z(HY)−z(LFI) sign-convention audit (Phase A flag) is still OPEN.
- `‡` CCI INVALID here: rel-pred put a monthly consumer basket on a
  business-day grid → 9 non-overlap windows. Phase A's CCI→XLY/XLP +0.16
  is NOT refuted, just untested. Re-run with a monthly ratio target.
- `†` TCI/LCI demoted on the descriptive floor, not on prediction.
- LFI/LPI/LDI share one LABOR basket+target → identical results. Phase B
  must give them distinct targets (LFI→fwd UNRATE is the candidate).
- MRI weights untrustworthy (n=23) — needs the history/vintage fix first.
- GCI dR 0.88 is partly mechanical (CFNAIMA3 is both a component AND the
  descriptive ref) — real KEEP, but the descriptive bar was easy there.

Proposed new weights for survivors are in the JSON. NOT propagated to
`INDICATORS_MASTER.md` or pillar dirs — that waits for Bob.

---

## PHASE B-2 RESULT — signal registry: descriptive + divergences + interactions (done 2026-05-17)

`Scripts/backtest/signal_registry_v3.py` (imports the validated v3
machinery, does not modify it). JSON:
`Outputs/mri_optimization/signal_registry_v3.json`. Built because Bob
asked for (a) descriptive composites as a first-class track, not just
predictive, (b) divergence indicators evaluated as constructs, (c) a
"weak alone, strong together" pairwise screen.

**Caught and fixed before reporting (scrutiny mattered again):** the
first descriptive pass scored 9 pillars at a tautological r_OOS = +1.00
because the ground-truth ref was itself a basket component (predict X
from a basket containing X). Fixed by excluding the ref from its own
features. Numbers below are post-fix.

### Descriptive track (OOS-honest concurrent tracking, ref excluded)

REAL = adds over best single component. PROXY = is its best single in
disguise. WEAK / BROKEN = does not track.

| Pillar | Ref | r_OOS | bestSingle | incr | Verdict |
|---|---|---|---|---|---|
| HCI | Case-Shiller YoY | +0.87 | 0.78 | +0.09 | **REAL** |
| FPI | 10y term premium | +0.87 | 0.76 | +0.12 | **REAL** |
| BCI | capex orders YoY | +0.70 | 0.57 | +0.13 | **REAL** |
| PCI | core PCE YoY | +0.91 | 0.90 | +0.00 | PROXY |
| LFI/LPI/LDI/CLG | UNRATE | +0.92 | 0.93 | −0.01 | PROXY |
| MSI | SPX vs 200d | +0.73 | 0.73 | +0.00 | PROXY |
| GCI | CFNAI 3m | +0.40 | 0.57 | −0.17 | WEAK |
| FCI | ANFCI | +0.57 | 0.76 | −0.19 | WEAK |
| CCI | real PCE YoY | −0.13 | 0.65 | −0.52 | BROKEN |
| TCI | TW dollar YoY | +0.06 | 0.11 | −0.05 | BROKEN |
| LCI | bank reserves YoY | −0.03 | 0.79 | −0.75 | BROKEN |
| MRI | UNRATE | +0.05 | 0.42 | −0.37 | BROKEN |
| SPI | AAII Bull-Bear | (+1.00) | 0.92 | n/a | INVALID |

Only **HCI, FPI, BCI** have a genuine descriptive composite (real lift
over the best single series). SPI is a residual tautology: the ref is
definitionally Bullish minus Bearish and both are still basket members,
so Phase B must exclude definitional siblings before SPI's descriptive
read is valid. The April-30 audit's broken calls (CCI, FCI-redundant,
LCI-proxy, TCI) are confirmed out-of-sample.

### Divergence constructs (gap evaluated AS DEFINED, not reweighted)

This corrects the Phase B-1 CLG "borderline KEEP, sign-audit open" line.

- **CLG = zn(HY-OAS) − zn(LFI) DOES predict, just not unemployment.** vs
  forward UNRATE: purged-OOS signed IC +0.06 (no OOS skill; Phase A's
  +0.30 there was the same full-sample artifact class as LFI to hiring).
  vs forward HY-OAS 3m: purged-OOS signed IC **+0.16, sign resolved
  (−gap)**, PREDICTS. CLG's real OOS role is leading CREDIT SPREADS,
  which is its original thesis ("spreads correct toward labor reality").
  **Re-target CLG to forward HY-OAS, not UNRATE.** The v3 free-weight
  optimizer had dissolved this (HY-OAS got ~0 weight); only the
  construct-intact test recovered it. Bob's pushback was correct.
- SBD (structure vs breadth) +0.04, SSD (sentiment vs structure) +0.00:
  honest nulls, no OOS skill (both depend on MSI/SPI, already DEMOTE'd).

### Pairwise interaction screen — definitive NULL (and that is a result)

364 pair-target tests, purged non-overlap, with NOISE x NOISE as the
false-discovery yardstick. **The control fired.** NOISE1 x NOISE2
reached joint OOS IC +0.42 (vs forward core PCE); noise-involved pairs
hit +0.60. Real pairs: median |joint| 0.23, p90 0.46, max 0.70,
statistically indistinguishable from noise. PCI x NOISE2 scored +0.57,
beating both "flagged" real pairs (LFI x CLG +0.41, GCI x CLG +0.33), so
those flags are false discoveries. Honest conclusion: the interaction
question is **untestable at the available monthly non-overlap
resolution**. Not "no interactions exist", but "this method cannot find
them without manufacturing them". The NOISE control is the only reason
we are not reporting LFI x CLG as a finding. A valid test needs
economically pre-specified single interaction hypotheses (not a 364-pair
sweep) or far more independent data. That is Phase C/D, not a patch.

### Net Phase B picture (both phases)

Under honest evaluation (OOS, purged, non-overlap, ref-excluded,
noise-controlled) most asserted structure collapses. Genuine survivors:
predictive composites **PCI, GCI, HCI**; descriptive composites **HCI,
FPI, BCI**; divergence **CLG to forward HY-OAS** (+0.16). HCI is the only
pillar strong on BOTH tracks. Everything else is an honest diagnostic at
best. The validated footprint is far narrower than the framework
asserts, and the survivors are real. Weights in the JSON, NOT propagated
to canonical docs. That waits for Bob.

---

## DATA STATE (done)

Inventory: **74/83 audit Tier-1 components already in `Lighthouse_Master.db`.**

Ingested 2026-05-16:
- U-6 unemployment → `U6RATE` + `LNS13327709` alias (387 obs, 1994–2026).
- `VIX_BACKWARDATION` = ^VIX/^VIX3M (4,990 obs, 2006–2026).

Still unsourced (proprietary / no free API — do NOT block on these; flag
for a paid-feed decision): NAAIM, Investors Intelligence Bull-Bear,
Put/Call ratio, ETF flows. SPI re-opt runs on the expanded available set
(VIX, AAII raw+spread, VIX-vs-50d, VIX_BACKWARDATION).

Known limits: MSI breadth components (`SPX_PCT_ABOVE_*`, AD line,
McClellan) only exist from 2023-02 (~3y) — short history caps long-window
Structure optimization. `OFR_NYPD-PD_RP_TOT-A` stale (ends 2021).
`FYGFD` redundant (have `GFDEBTN` quarterly).

---

## EXPANDED TIER-1 BASKETS (from PILLAR_BASKET_AUDIT — use these for re-opt)

- **LPI** + ICSA, CCSA, AHETPI, ECIWAG, FRBATLWGT12MMUMHGO, U6RATE, AWHAETP
- **PCI** + PCEPI, MEDCPIM158SFRBCLE, PCETRIM12M159SFRBDAL, STICKCPIM158SFRBATL,
  CORESTICKM158SFRBATL, T5YIE, T10YIE, T5YIFR, MICH, PPIFIS
- **GCI** + CFNAIMA3, BBKMLEIX, RPI, PCEC96, HOANBS
- **HCI** + HOUST1F, CSUSHPINSA, MSPUS, MORTGAGE15US, DRSFRMACBS (EXHOSLUSM495S n=17 too short)
- **CCI** + PCEC96, DRCCLACBS, RPI, TOTALSL, TDSP, DRCLACBS, PSAVE
- **BCI** + ANDENO, ANXAVS, ACDGNO, AMTMNO, CAPB50001S, DRTSCILM
- **TCI** + DEXJPUS, DEXCHUS, DEXMXUS, BOPTEXP, BOPTIMP, IQ, IR
- **FPI** + DGS30, DGS3MO, T10Y3M, GFDEBTN, FDHBFIN
- **FCI** + ANFCI, AAA10Y, DRALACBS, CORCCACBS, STLFSI4, KCFSI
- **LCI** + IORB, EFFR, NYFED_TGCR, OFR_MMF-MMF_RP_TOT-M, OFR_MMF-MMF_TOT-M
- **MSI** + SPX_PCT_ABOVE_50D/20D/200D, SPX_NET_NEW_HIGHS, SPX_AD_LINE,
  SPX_MCCLELLAN_SUM, SPX_BREADTH_THRUST (all only ~3y history — note in output)
- **SPI** + AAII_Bullish/Bearish/Neutral, VIX_vs_50d_pct, VIX_BACKWARDATION

---

## NEW INDICATORS TO BUILD (audit shortlist — validate each via signal_eval before keeping)

1. Wage Inflation Composite — AHETPI, ECIWAG, FRBATLWGT12MMUMHGO, COMPNFB
2. Inflation Expectations Composite — MICH, EXPINF1/5/10YR, T5YIE, T10YIE, T5YIFR
3. Realized Credit Stress — DRALACBS, CORCCACBS, DRCLACBS, DRTSCILM (vs implied HY OAS = divergence)
4. Late-Cycle Equity Drag — GCI inputs + TCU + capex momentum + employment diffusion, target = SPX 252d fwd (exp −)
5. MMF Pulse — OFR MMF total + composition (Tsy/Repo/RRP) + flows (Impulse family)
6. Term-Premium Pressure — THREEFYTP10 + T10Y3M + 30y-2y + FDHBFIN + auction tails
7. Composite-Drift monitor — internal tool (rolling-12m r of each composite vs its descriptive ref; alert <0.5). Build as a script, not a published composite.

---

## MIGRATION PATH — EXECUTION CHECKLIST

- [x] Phase A scorecard (`Scripts/backtest/signal_eval.py`)
- [x] Data-gap inventory
- [x] Ingest obtainable missing (U-6, VIX backwardation)
- [x] extend `signal_eval.py` with the macro-predictive role — DONE
      2026-05-16. `MACRO_PRED` dict added (LFI→PCEC96/PAYEMS, LPI/LDI/GCI→
      PAYEMS, CLG→UNRATE, LCI→HY-OAS, FCI→PAYEMS, PCI/TCI→core-PCE,
      HCI/BCI→INDPRO, MRI→UNRATE; all `db_fwd_chg`, signed per transmission
      thesis). Scorecard re-run pending watcher; results to append here.
- [x] Build dual-objective walk-forward re-optimizer
      (`Scripts/backtest/pillar_reoptimize_v3.py`) — DONE 2026-05-16.
      Purged non-overlap WF; caught + fixed a daily-ffill pseudo-
      replication leak (had inflated PCI to +0.76; honest +0.62). Full
      run + JSON shipped. Survivors PCI/GCI/HCI; the "LFI leads hiring"
      headline does NOT survive OOS. See PHASE B-1 RESULT above.
- [x] Signal registry: descriptive track + divergence constructs +
      pairwise interaction screen (`Scripts/backtest/signal_registry_v3.py`)
      — DONE 2026-05-17 (Bob-added scope). Caught + fixed a ref-in-basket
      tautology. Descriptive REAL: HCI/FPI/BCI. CLG re-targeted to fwd
      HY-OAS (predicts +0.16, not UNRATE — Phase A's UNRATE read was an
      artifact). Pairwise interaction = honest NULL (noise pairs hit
      +0.60; method has no resolution at monthly non-overlap). See
      PHASE B-2 RESULT above.
- [x] **DONE 2026-06-06 (was NEXT): honest full-registry re-run.**
      `registry_honest_v4.py` -> `registry_honest_v4.json` (600 cells).
      Reproduces every B-1/B-2 anchor; RAW counts inflated, see PHASE B-3
      RESULT below. (Re-run after a crash lost the original output — the
      script had survived on disk, the JSON was never written.) Re-run the
      entire multi-role v3-v6 registry
      (`pillar_specs_v2.py` baskets × {diagnostic ref-excluded,
      macro/asset/relative predictive purged + non-overlap, lead-lag
      event study}) through the leak-corrected harness. This SUPERSEDES
      "build the 7 new indicators" as the immediate next step (the 7 new
      candidates fold in as additional rows validated by the same
      harness, not a separate pass). Build it the disciplined way that
      caught the leak / tautology / noise-pair: smoke-test each role on a
      known cell before the full grid. Sanity gate: must reproduce the
      Phase B-1/B-2 survivors (PCI/GCI/HCI, HCI/FPI/BCI, CLG→HY-OAS).
      Deliverable = the honest registry, NOT an INDICATORS_MASTER rewrite.
- [ ] Rewrite the stale nowcast anchor+bridge external diagram to describe
      the regression/walk-forward model (currently describes the dead
      single-proxy offset story — do NOT ship the stale one externally).
- [ ] Phase B: from the validated results, per (composite,role):
      keep / re-optimized-weights / demote-to-diagnostic. Then **rebuild**
      `INDICATORS_MASTER.md` from the validated lineup. Surface
      trade-offs/parked-decisions for Bob (ideation, not exec summary).
- [ ] Phase C: vintage / point-in-time data layer (the real staleness
      fix — information-state vintages so backtests are point-in-time).
- [ ] Phase D: HMM/GMM regime layer (research track —
      `/Users/bob/Library/Mobile Documents/com~apple~CloudDocs/macrosynergy/5_hidden_markov.pdf`
      + the numbered stochastic-processes corpus).

**After each checklist item: tick it here and append a one-line result.
This file is the resume anchor — keep it current.**

---

## ENVIRONMENT NOTES (so a cold resume doesn't relearn the hard way)

- Use `/opt/homebrew/bin/python3.14` (has yfinance, sklearn 1.8, reportlab,
  bs4). The conda `python3` does NOT have yfinance.
- DB is WAL mode. `compute_indices.py` runs walk-forward bridges per
  composite already (slow; runs in background, watch with an until-loop).
- FRED key in `Scripts/data_pipeline/.env` (`FRED_API_KEY`, 32 chars,
  works). Correct U-6 FRED id is `U6RATE` (NOT `LNS13327709` — that 400s).
- Verify every visual artifact by rasterizing + viewing (pdftoppm +
  contact sheet). Page-count/text-extract checks miss layout defects —
  that lesson cost real rework this session.
- `timeout` is not on macOS; use background + until-loop watcher.
- Don't touch canonical docs (INDICATORS_MASTER, pillar dirs) until the
  validated lineup is in front of Bob.
