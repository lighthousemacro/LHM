#!/bin/bash
# Lighthouse Macro - Master Context Sync Script
# Syncs CLAUDE_MASTER.md to all AI interfaces
# Updates LAST_SYNC date automatically

MASTER="/Users/bob/LHM/Strategy/CLAUDE_MASTER.md"
CODE_TARGET="/Users/bob/.claude/CLAUDE.md"
DESKTOP_EXPORT="/Users/bob/Desktop/LHM_MASTER_CONTEXT.md"
LOG="/Users/bob/LHM/logs/sync.log"

# Ensure master exists
if [ ! -f "$MASTER" ]; then
    echo "ERROR: Master file not found at $MASTER"
    exit 1
fi

# Get today's date
TODAY=$(date '+%Y-%m-%d')
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Update LAST_SYNC in master file
sed -i '' "s/^\*\*LAST_SYNC:\*\* .*/\*\*LAST_SYNC:\*\* $TODAY/" "$MASTER"
echo "[$TIMESTAMP] Updated LAST_SYNC to $TODAY" >> "$LOG"

# Sync to Claude Code
cp "$MASTER" "$CODE_TARGET"
echo "[$TIMESTAMP] Synced to Claude Code: $CODE_TARGET" >> "$LOG"

# Create desktop export (one unified file for all platforms)
cp "$MASTER" "$DESKTOP_EXPORT"
echo "[$TIMESTAMP] Created desktop export: $DESKTOP_EXPORT" >> "$LOG"

# Push to GitHub so cloud environments and remote triggers see the latest context.
# Only commits if CLAUDE_MASTER.md actually changed (other than LAST_SYNC, which changes daily).
# We only push if there's a real content change to avoid churning the repo every 15 minutes.
cd /Users/bob/LHM || exit 0
if git diff --quiet -- Strategy/CLAUDE_MASTER.md; then
    : # nothing changed, skip
else
    # Check if the only change is the LAST_SYNC date line
    CHANGED_LINES=$(git diff --unified=0 Strategy/CLAUDE_MASTER.md | grep -E '^[+-]' | grep -v '^[+-]\{3\}' | wc -l | tr -d ' ')
    SYNC_ONLY=$(git diff --unified=0 Strategy/CLAUDE_MASTER.md | grep -E '^[+-]' | grep -v '^[+-]\{3\}' | grep -v 'LAST_SYNC' | wc -l | tr -d ' ')
    if [ "$SYNC_ONLY" = "0" ]; then
        echo "[$TIMESTAMP] Only LAST_SYNC changed, skipping commit" >> "$LOG"
    else
        git add Strategy/CLAUDE_MASTER.md
        git commit -m "sync: update CLAUDE_MASTER.md ($TODAY)" >> "$LOG" 2>&1
        git push origin main >> "$LOG" 2>&1 && echo "[$TIMESTAMP] Pushed to GitHub" >> "$LOG" || echo "[$TIMESTAMP] Push failed (not fatal)" >> "$LOG"
    fi
fi

# Summary
echo "========================================"
echo "MASTER CONTEXT SYNCED - $TIMESTAMP"
echo "========================================"
echo ""
echo "LAST_SYNC updated to: $TODAY"
echo ""
echo "AUTOMATIC:"
echo "  1. Claude Code:    DONE"
echo "  2. Desktop Export: DONE (~/Desktop/LHM_MASTER_CONTEXT.md)"
echo ""
echo "MANUAL (copy from Desktop - accessible from phone via iCloud):"
echo "  3. Claude.ai/iOS  → paste into custom instructions"
echo "  4. Claude Desktop → paste into custom instructions"
echo "  5. Gemini          → paste into context"
echo "  6. ChatGPT         → paste into custom instructions"
echo ""
echo "========================================"
