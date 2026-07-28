#!/bin/zsh
# publish_site_daily.sh — the whole public site, refreshed and pushed, once a day.
#
# Site staleness used to be structural: the DB refreshed every morning but
# nothing rebuilt the site, so "LIVE" was only true right after a manual push.
# This closes that loop. Runs after the 06:00 pipeline and the 07:00 indicator
# recompute, so the dashboard picks up the same morning's numbers.
#
# Order matters:
#   1. pull anything published on Substack into the local export
#   2. rebuild the Reading Room (article pages + index + feed.xml + sitemap)
#   3. rebuild the homepage (live dashboard tiles + research feed)
#   4. commit + push only if something actually changed
#
# Install: launchctl load ~/Library/LaunchAgents/com.lighthousemacro.site-publish.plist
set -u

ROOT="/Users/bob/LHM"
export PYTHONPATH="$ROOT"
export PATH="/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin"
# Pin the interpreter. /usr/local/bin/python3 has no CA bundle wired up, so every
# https fetch here (Substack API, RSS) dies with CERTIFICATE_VERIFY_FAILED and the
# site quietly publishes fallback content instead of the live feed.
PY=/opt/homebrew/bin/python3
cd "$ROOT"

echo "=== site publish $(date '+%Y-%m-%d %H:%M:%S') ==="

echo "-- syncing Substack export"
"$PY" "$ROOT/Scripts/website/sync_substack_export.py" || echo "  ! export sync failed, building on what we have"

echo "-- rebuilding Reading Room"
"$PY" "$ROOT/Scripts/website/build_reading_room.py" || { echo "  !! Reading Room build FAILED, aborting"; exit 1; }

echo "-- rebuilding homepage"
BUILD_OUT="$("$PY" "$ROOT/Scripts/website/build_site.py" 2>&1)" || { echo "$BUILD_OUT"; echo "  !! homepage build FAILED, aborting"; exit 1; }
echo "$BUILD_OUT"

# A degraded build is worse than yesterday's good one. If the dashboard fell back
# to the hardcoded snapshot or the research feed fell back to the canned list,
# publish nothing and leave the last good push in place.
if echo "$BUILD_OUT" | grep -q "using fallback research list"; then
  echo "  !! research feed fell back, refusing to publish a degraded homepage"
  exit 1
fi
if ! echo "$BUILD_OUT" | grep -q "dashboard read from live"; then
  echo "  !! dashboard did not read live, refusing to publish a stale board"
  exit 1
fi

# Refuse to publish a homepage that fell back to the hardcoded snapshot instead
# of reading the DB. A stale board on the storefront is worse than no push.
if ! grep -q "AS OF" "$ROOT/Website/index.html"; then
  echo "  !! homepage has no as-of stamp, aborting"
  exit 1
fi

cd "$ROOT/Website"
if git diff --quiet && git diff --cached --quiet && [ -z "$(git status --porcelain)" ]; then
  echo "-- nothing changed, site already current"
  exit 0
fi

git add -A
git commit -q -m "Site refresh $(date '+%Y-%m-%d %H:%M')"
git pull --rebase --quiet origin main || echo "  ! rebase pull failed, pushing anyway"
if git push -q origin main; then
  echo "-- pushed, live in a few minutes at https://lighthousemacro.com"
else
  echo "  !! push FAILED (check the credential helper / token)"
  exit 1
fi
