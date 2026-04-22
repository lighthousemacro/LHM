# Pipeline Freshness Fix

**Status:** Implemented 2026-04-22
**Owner:** Bob Sheehan
**Scope:** additive fix, does not modify the 06:00 ET pipeline

---

## The Problem

The Lighthouse daily pipeline runs at **06:00 ET** via launchd
(`com.lighthousemacro.pipeline`). Most government economic releases hit
FRED between **08:30 ET and 10:00 ET** on release days:

| Release | Publisher | Typical FRED drop |
|---|---|---|
| Advance Retail Trade | Census | 08:30-08:35 ET |
| CPI, PPI, Employment Situation | BLS | 08:30 ET |
| Personal Income & Outlays (PCE) | BEA | 08:30 ET |
| Trade Balance, Durable Goods, Housing Starts | Census / BEA | 08:30 ET |
| Industrial Production | Fed | 09:15 ET |
| JOLTS, New Home Sales, Existing Home Sales | BLS / Census / NAR | 10:00 ET |

Because the morning pipeline finishes ~09:30 ET and never reads FRED again
until tomorrow, **same-day release data is systematically missed**.

The symptom that triggered this fix: on 2026-04-21, Bob needed March 2026
retail sales for a Beam. The 06:00 pipeline ran at 07:09-07:16 ET; Census
pushed to FRED at 08:35 ET. A prior agent had to re-pull manually. See
`/Users/bob/LHM/Outputs/beam_retail_sales_march2026/pipeline_fix_report.md`.

---

## The Fix (Option C: targeted freshness check)

A lightweight mid-morning script runs at **11:00 ET on weekdays**. For a
short list of release-sensitive FRED series, it:

1. Calls FRED's `/series` metadata endpoint to read `observation_end`.
2. Compares to `MAX(date)` in `Lighthouse_Master.db` for that series.
3. If FRED is newer, re-fetches via the existing `FREDFetcher._fetch_series()`
   path — same write path, same dedup (`INSERT OR REPLACE`), same rate limits.
4. If nothing is new, exits cheap. No observation fetches, nothing written.

It also writes an entry into `update_log` tagged `FRED_FRESHNESS_CHECK`
so this shows up in audit queries alongside the full pipeline runs.

### Why Option C over A or B

- **Option A (second full pipeline run):** simplest, but re-runs 1,400+
  series, BLS/BEA/market/crypto/etc. when 99% of them don't need it.
  Wastes API budget and causes DB contention with the 15-min sync.
- **Option B (observation_end check inside `fetch_curated`):** elegant,
  but adds a metadata round-trip for every curated series on every run.
  That's 400+ extra FRED calls per daily run, and the problem it solves
  only matters for ~50 release-sensitive tickers.
- **Option C (targeted release-sensitive list):** cheapest (~80 metadata
  calls, one extra run per weekday, and fetches only when there's
  actually new data). Aligns with the actual problem.

---

## Files

| Path | Purpose |
|---|---|
| `/Users/bob/LHM/Scripts/data_pipeline/check_for_updates.py` | the freshness check script |
| `/Users/bob/LHM/Scripts/data_pipeline/com.lighthousemacro.freshness-check.plist` | launchd template (copy into `~/Library/LaunchAgents/` to install) |
| `/Users/bob/LHM/logs/freshness_check.log` | launchd stdout |
| `/Users/bob/LHM/logs/freshness_check_error.log` | launchd stderr |
| `/Users/bob/LHM/logs/pipeline_freshness.log` | the script's own detailed log |

The 06:00 pipeline (`com.lighthousemacro.pipeline`) is unchanged. This
new job is purely additive.

---

## How to install the launchd job

```bash
cp /Users/bob/LHM/Scripts/data_pipeline/com.lighthousemacro.freshness-check.plist \
   ~/Library/LaunchAgents/

# Unload first in case an older version is loaded, ignore error if not.
launchctl unload ~/Library/LaunchAgents/com.lighthousemacro.freshness-check.plist 2>/dev/null

launchctl load ~/Library/LaunchAgents/com.lighthousemacro.freshness-check.plist

# Optional: run immediately to confirm it works end-to-end
launchctl start com.lighthousemacro.freshness-check
tail -f /Users/bob/LHM/logs/freshness_check.log
```

To remove: `launchctl unload ~/Library/LaunchAgents/com.lighthousemacro.freshness-check.plist && rm ~/Library/LaunchAgents/com.lighthousemacro.freshness-check.plist`.

---

## How to test manually

```bash
cd /Users/bob/LHM/Scripts/data_pipeline
PYTHONPATH=/Users/bob/LHM python3 check_for_updates.py --dry-run --verbose
```

Dry-run lists which series FRED has newer than the DB, but fetches nothing.
Drop `--dry-run` to actually fetch.

To audit what the check has done historically:

```sql
SELECT timestamp, series_updated, observations_added
FROM update_log
WHERE source = 'FRED_FRESHNESS_CHECK'
ORDER BY id DESC
LIMIT 10;
```

---

## How to extend the release-sensitive series list

Open `check_for_updates.py` and edit `RELEASE_SENSITIVE_SERIES`. The dict
is grouped by release name (retail, cpi, ppi, pce, employment, jolts,
claims, industrial_production, housing_starts, new_home_sales,
existing_home_sales, trade, durable_goods, gdp, sentiment, consumer_credit).

Add the FRED series id to the appropriate bucket. Two rules:

1. The series id must already exist in `FRED_CURATED` (in
   `lighthouse/config.py`). The freshness check intentionally will not
   bootstrap a brand-new series; that belongs in the main pipeline config.
2. Keep the list tight. Every id added is one extra FRED metadata call
   per run. The point of Option C is to target release-day misses, not
   to shadow the full curated set.

---

## Edge cases worth knowing

- **DB lock coexistence.** The checker opens SQLite with `timeout=60`, so
  if the 06:00 pipeline is still finishing (e.g. computing indices) or
  the 15-minute `sync_all.py` push is running, the checker waits rather
  than crashing. The fetch loop also releases its transactions between
  series (one commit per series via `_fetch_series`).
- **DST handling.** launchd's `Hour` key is local time. The Mac stays on
  US Eastern time, so 11:00 local = 11:00 ET in both EDT and EST. No DST
  toggle needed.
- **Weekends.** Plist is configured for Mon-Fri only. Economic releases
  don't land on weekends, and Mon is covered for any late-Friday
  revisions.
- **FRED rate limits.** The script reuses the pipeline's `fetch_with_retry`
  helper and honors `FETCH_CONFIG["rate_limit_delay"]`. A full run is
  ~80 metadata calls + up to ~20 observation fetches. Well under FRED's
  120 req/min limit.
- **No fabricated data.** If FRED has no new observation, nothing writes.
  If FRED says `observation_end > db_end` but the payload is empty, the
  existing `_fetch_series` returns (0, 0) and no meta row is stamped
  falsely.
- **First-run bootstrapping.** If a series is in `FRED_CURATED` but
  absent from `observations` (e.g. just added to config), the check
  treats it as stale and pulls it. This is intentional; it's cheap and
  catches lag between config edits and the next full pipeline.
- **When the Mac is asleep at 11:00 ET.** launchd will fire the job at
  the next wake. If you miss the release-day window you can always run
  the script manually.

---

## What this does *not* do

- Does not replace the 06:00 ET pipeline.
- Does not touch BLS, BEA, NY Fed, OFR, or market/crypto/breadth fetchers.
  FRED mirrors most release data anyway, and adding the rest would drift
  into Option A territory.
- Does not modify `fetchers.py` (no Option B plumbing added). If the
  release-sensitive list grows past ~200 ids, revisit Option B.

