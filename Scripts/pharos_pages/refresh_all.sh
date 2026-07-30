#!/bin/zsh
# refresh_all.sh — rebuild every Pharos dashboard from the live DB.
#
# The terminal serves static HTML built by Scripts/pharos_pages/*. Nothing rebuilt
# them, so the PAID product sat on 2026-07-25 data while the free public site
# refreshed daily. This closes that gap. Runs after the pipeline and the indicator
# recompute so the boards carry the same morning's numbers as the homepage.
#
# Install: launchctl load ~/Library/LaunchAgents/com.lighthousemacro.pharos-refresh.plist
set -u

ROOT="/Users/bob/LHM"
export PYTHONPATH="$ROOT"
export PATH="/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin"
# Pharos/.venv has no pandas; the pillar builders need the homebrew interpreter.
PY=/opt/homebrew/bin/python3
OUT="$ROOT/Data/databases/pillars"
cd "$ROOT"

echo "=== pharos refresh $(date '+%Y-%m-%d %H:%M:%S') ==="

# The Watch first: it is the landing board, so if the run dies partway the most
# important page is already current.
ORDER=(
  build_the_watch.py
  build_pillar_labor.py
  build_pillar_02_prices.py
  build_pillar_03_growth.py
  build_pillar_04_housing.py
  build_pillar_05_consumer.py
  build_pillar_06_business.py
  build_pillar_07_trade.py
  build_pillar_08_government.py
  build_pillar_09_financial.py
  build_pillar_10_plumbing.py
  build_pillar_11_structure.py
  build_pillar_12_sentiment.py
  build_index.py
)

ok=0; failed=()
for script in $ORDER; do
  path="$ROOT/Scripts/pharos_pages/$script"
  [[ -f "$path" ]] || { echo "  ! missing $script"; failed+=("$script"); continue; }
  # Builders write the .html only on success, so a failure leaves yesterday's
  # good page in place rather than truncating it.
  if "$PY" "$path" > /tmp/pharos_$script.log 2>&1; then
    ok=$((ok+1)); echo "  ok   $script"
  else
    failed+=("$script"); echo "  FAIL $script"; tail -3 /tmp/pharos_$script.log | sed 's/^/       /'
  fi
done

echo "-- rebuilt $ok/${#ORDER[@]} boards"
if (( ${#failed[@]} > 0 )); then
  echo "-- FAILED: ${failed[*]}"
fi

# Staleness guard: the landing board must carry today's date or the paid terminal
# is quietly serving an old tape.
TODAY=$(date '+%Y-%m-%d')
if [[ -f "$OUT/the_watch.html" ]]; then
  AGE=$(( ( $(date +%s) - $(stat -f %m "$OUT/the_watch.html") ) / 3600 ))
  echo "-- the_watch.html last written ${AGE}h ago"
  (( AGE > 26 )) && echo "   !! WARNING: landing board did not refresh"
fi

(( ${#failed[@]} > 0 )) && exit 1
exit 0
