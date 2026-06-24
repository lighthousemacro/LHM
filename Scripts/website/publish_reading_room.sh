#!/bin/zsh
# Publish the Lighthouse Macro Reading Room.
#
# Rebuilds research/ from the Substack export honoring the curation lists at the
# top of Scripts/website/build_reading_room.py (EXCLUDE = pieces to hide,
# FRAMEWORK_ORDER = The Blueprint order), then commits + pushes the live site.
#
# To curate: edit those two lists, then run `lhm-reading-room`. That's it.
set -e

ROOT="/Users/bob/LHM"
cd "$ROOT"

echo "Rebuilding the Reading Room..."
PYTHONPATH="$ROOT" python3 "$ROOT/Scripts/website/build_reading_room.py"

cd "$ROOT/Website"
if git diff --quiet && git diff --cached --quiet; then
  echo "Nothing changed — Reading Room is already up to date."
  exit 0
fi

git add -A
git commit -q -m "Reading Room update ($(date '+%Y-%m-%d %H:%M'))"
git pull --rebase origin main --quiet
git push origin main

echo ""
echo "Published. Live in a few minutes at https://lighthousemacro.com/research/"
