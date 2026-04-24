#!/bin/bash
# Mirror a filtered snapshot of /Users/bob/LHM into ~/Dropbox/LHM
# so the folder is readable from the Dropbox mobile app.
#
# - One-way rsync (Dropbox is a read-only mirror; never sync back).
# - Excludes heavy or phone-useless paths (Data, OpenBB, Archive, .git, caches).
# - Uses --delete so the mirror stays clean when files are removed locally.

set -u

SRC="/Users/bob/LHM/"
DST="$HOME/Dropbox/LHM/"
LOG="/Users/bob/LHM/logs/dropbox_mirror.log"

mkdir -p "$DST"

{
  echo "=== $(date '+%Y-%m-%d %H:%M:%S') mirror start ==="
  rsync -a --delete \
    --exclude='.git/' \
    --exclude='.venv/' \
    --exclude='venv/' \
    --exclude='__pycache__/' \
    --exclude='*.pyc' \
    --exclude='.DS_Store' \
    --exclude='.dropbox.cache/' \
    --exclude='.ipynb_checkpoints/' \
    --exclude='node_modules/' \
    --exclude='Data/' \
    --exclude='OpenBB/' \
    --exclude='OpenBBUserData/' \
    --exclude='Archive/' \
    --exclude='*.db-wal' \
    --exclude='*.db-shm' \
    "$SRC" "$DST"
  echo "=== $(date '+%Y-%m-%d %H:%M:%S') mirror end (exit $?) ==="
} >> "$LOG" 2>&1
