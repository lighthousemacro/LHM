#!/bin/zsh
# ─────────────────────────────────────────────────────────────────────────────
# daily_draft.sh — Lighthouse Macro "always-ready piece"
#
# Runs lhm-macro-scout → lhm-publish headless, every morning, so Bob wakes up to a
# fully-built, charts-embedded, ready-to-review draft open in his browser. The job
# NEVER publishes — terminal state is "HTML preview ready, Bob decides."
#
# Scheduled by: ~/Library/LaunchAgents/com.lighthousemacro.daily-draft.plist
# Edit timing in the plist. Edit what gets built in daily_draft_prompt.md.
# ─────────────────────────────────────────────────────────────────────────────

set -u

LHM="/Users/bob/LHM"
CLAUDE_BIN="/Users/bob/.local/bin/claude"
PROMPT_FILE="$LHM/Scripts/automation/daily_draft_prompt.md"
LOG_DIR="$LHM/logs"
RUN_DATE="$(date +%Y-%m-%d)"
RUN_LOG="$LOG_DIR/daily_draft_${RUN_DATE}.log"
LATEST_LOG="$LOG_DIR/daily_draft.log"
LOCK_DIR="$LHM/Outputs/.daily_draft.lock"

export PATH="/Users/bob/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
export PYTHONPATH="$LHM"

# Load API keys (FRED/BLS/BEA/etc.) the same way the pipeline does.
if [[ -f "$LHM/Scripts/data_pipeline/.env" ]]; then
  set -a
  source "$LHM/Scripts/data_pipeline/.env"
  set +a
fi

cd "$LHM" || exit 1

log() { print -r -- "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$RUN_LOG"; }

# ── single-run lock ──────────────────────────────────────────────────────────
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  log "ANOTHER RUN IS IN PROGRESS (lock: $LOCK_DIR). Exiting."
  exit 0
fi
trap 'rmdir "$LOCK_DIR" 2>/dev/null' EXIT INT TERM

: > "$RUN_LOG"
log "════════ DAILY DRAFT RUN START ($RUN_DATE) ════════"
log "claude: $CLAUDE_BIN   cwd: $LHM"

PROMPT="$(cat "$PROMPT_FILE")"
SYS_APPEND="This is an UNATTENDED scheduled daily run. Do not ask the user any \
questions — make safe default choices and continue. Never publish, send, post, \
schedule, email, or push anything externally. Produce only a local HTML preview \
and print its absolute path on the final line as 'PREVIEW_PATH: <path>'."

# Outbound-comms / publish / payment tool surface the draft pipeline never needs.
# Blocking it means the unattended job structurally CANNOT email, post, schedule,
# pay, or push — even though it runs with permission prompts bypassed for local work.
DISALLOW=(
  mcp__claude_ai_Gmail mcp__claude_ai_Slack mcp__claude_ai_Quo
  mcp__claude_ai_Narrareach mcp__writestack mcp__claude_ai_Stripe
  mcp__plugin_telegram_telegram mcp__claude_ai_Vercel mcp__claude_ai_monday_com
  mcp__claude_ai_Canva mcp__claude_ai_Linear mcp__claude_ai_Notion
)

# ── run the pipeline headless (caffeinate keeps the Mac awake for the duration) ─
START_TS=$(date +%s)
caffeinate -i "$CLAUDE_BIN" \
  -p "$PROMPT" \
  --append-system-prompt "$SYS_APPEND" \
  --permission-mode bypassPermissions \
  --disallowedTools "${DISALLOW[@]}" \
  --verbose \
  2>&1 | tee -a "$RUN_LOG"
STATUS=${pipestatus[1]}
END_TS=$(date +%s)
log "claude exited status=$STATUS in $(( (END_TS - START_TS) / 60 ))m $(( (END_TS - START_TS) % 60 ))s"

# ── find the preview and open it ─────────────────────────────────────────────
PREVIEW="$(grep -aoE 'PREVIEW_PATH:[[:space:]]*[^ ]+\.html' "$RUN_LOG" | tail -1 | sed -E 's/^PREVIEW_PATH:[[:space:]]*//')"

if [[ -z "$PREVIEW" || ! -f "$PREVIEW" ]]; then
  log "No PREVIEW_PATH in output — falling back to newest *preview*.html touched in the last 3h."
  PREVIEW="$(find "$LHM/Outputs" -type f -iname '*preview*.html' -mmin -180 2>/dev/null | xargs -I{} stat -f '%m %N' {} 2>/dev/null | sort -rn | head -1 | cut -d' ' -f2-)"
fi

if [[ -n "$PREVIEW" && -f "$PREVIEW" ]]; then
  log "PREVIEW READY → $PREVIEW"
  open "$PREVIEW" 2>>"$RUN_LOG" && log "Opened in browser." || log "open failed (no GUI session?) — path logged above."
else
  log "WARNING: no preview HTML found. Check the run log: $RUN_LOG"
fi

cp -f "$RUN_LOG" "$LATEST_LOG" 2>/dev/null
log "════════ DAILY DRAFT RUN END (status=$STATUS) ════════"
exit 0
