#!/usr/bin/env bash
# Lighthouse Macro - Substack session cookie installer.
#
# One-time setup helper for substack_api_pull.py. Walks you through grabbing
# the session cookie from Chrome DevTools and writes it to the canonical
# location with the right permissions.
#
# Run:
#   bash /Users/bob/LHM/Scripts/dashboards/substack_session_setup.sh
#
# Or pipe the cookie in directly:
#   echo 'connect.sid=...; substack.sid=...' | \
#       bash /Users/bob/LHM/Scripts/dashboards/substack_session_setup.sh
#
# After install, verify with:
#   /Users/bob/LHM/.venv/bin/python \
#       /Users/bob/LHM/Scripts/dashboards/substack_api_pull.py --probe

set -euo pipefail

TARGET_DIR="${HOME}/.config/lhm"
TARGET_FILE="${TARGET_DIR}/substack_session.json"
PUBLICATION_URL="${LHM_SUBSTACK_PUBLICATION_URL:-https://lighthousemacro.substack.com}"

mkdir -p "${TARGET_DIR}"
chmod 700 "${TARGET_DIR}"

# Read cookie: from stdin if piped, otherwise prompt
if [ ! -t 0 ]; then
    COOKIE_STRING="$(cat)"
else
    cat <<EOF
================================================================
  Substack session cookie setup
----------------------------------------------------------------
  1. Open https://lighthousemacro.substack.com in Chrome (logged in)
  2. Cmd+Option+I to open DevTools, Network tab, Cmd+R to reload
  3. Click the very first request in the list (substack.com or /)
  4. Right panel: Headers > Request Headers > find "cookie:"
  5. Copy the ENTIRE cookie value (very long, semicolon-separated)
  6. Paste below, then hit Enter twice:
================================================================

EOF
    COOKIE_STRING=""
    while IFS= read -r LINE; do
        if [ -z "${LINE}" ]; then
            break
        fi
        COOKIE_STRING="${COOKIE_STRING}${LINE}"
    done
fi

# Strip a leading "cookie:" or "Cookie:" header prefix if present
COOKIE_STRING="$(printf '%s' "${COOKIE_STRING}" | sed -E 's/^[[:space:]]*[Cc]ookie:[[:space:]]*//' | tr -d '\n\r')"

if [ -z "${COOKIE_STRING}" ]; then
    echo "ERROR: empty cookie string" >&2
    exit 1
fi

# Sanity check - Substack session cookies always include connect.sid OR substack.sid
if ! printf '%s' "${COOKIE_STRING}" | grep -qE 'connect\.sid=|substack\.sid='; then
    echo "WARNING: didn't see connect.sid or substack.sid in the pasted string." >&2
    echo "         Saving anyway, but the cookie may not authenticate." >&2
fi

# Escape any double quotes in the cookie for JSON-safe embedding
ESCAPED="$(printf '%s' "${COOKIE_STRING}" | sed 's/\\/\\\\/g; s/"/\\"/g')"
NOW="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

cat > "${TARGET_FILE}" <<EOF
{
  "cookie_string": "${ESCAPED}",
  "publication_url": "${PUBLICATION_URL}",
  "saved_at": "${NOW}"
}
EOF
chmod 600 "${TARGET_FILE}"

echo
echo "Wrote ${TARGET_FILE} (chmod 600)"
echo "Publication: ${PUBLICATION_URL}"
echo "Saved at:    ${NOW}"
echo
echo "Verify it works:"
echo "  /Users/bob/LHM/.venv/bin/python \\"
echo "      /Users/bob/LHM/Scripts/dashboards/substack_api_pull.py --probe"
