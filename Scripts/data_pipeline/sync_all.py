#!/usr/bin/env python3
"""
LIGHTHOUSE MACRO - MULTI-DESTINATION SYNC
==========================================
Syncs database backups, strategy docs, and code to all backup destinations.
Called automatically after daily pipeline run, or standalone.

Destinations:
    1. LOCAL  - Dated database backups (7-day rolling)
    2. GITHUB - Pull --rebase, auto-commit and push code, strategy, brand, logs
    3. ICLOUD - Database backup copy
    4. DROPBOX - Database backup copy + Strategy + Brand

Note: Google Drive was retired 2026-05-12 (chronic "Resource deadlock avoided"
errors on the CloudStorage mount). iCloud + Dropbox cover the same ground.

Usage:
    python sync_all.py              # Full sync to all destinations
    python sync_all.py --git-only   # Only git commit + push
    python sync_all.py --cloud-only # Only cloud sync (no git)
    python sync_all.py --dry-run    # Show what would happen
"""

import os
import sys
import shutil
import subprocess
import argparse
from datetime import datetime, timedelta
from pathlib import Path

# === PATHS ===
LHM_ROOT = Path("/Users/bob/LHM")
DB_SOURCE = LHM_ROOT / "Data" / "databases" / "Lighthouse_Master.db"
BACKUP_DIR = LHM_ROOT / "Data" / "databases" / "backups"
LOGS_DIR = LHM_ROOT / "logs"

# Cloud destinations
DROPBOX_DIR = Path.home() / "Dropbox" / "LHM_Backups"


def _get_icloud_dir():
    """Find writable iCloud path. Prefers Mobile Documents (writable), falls back to CloudStorage."""
    # Primary: Mobile Documents (always writable)
    mobile_docs = Path.home() / "Library" / "Mobile Documents" / "com~apple~CloudDocs"
    if mobile_docs.exists():
        return mobile_docs / "LHM_Backups"
    # Fallback: CloudStorage mount (may need entitlements)
    cloud_base = Path.home() / "Library" / "CloudStorage"
    matches = sorted(cloud_base.glob("iCloudDrive-*"), key=lambda p: p.stat().st_mtime, reverse=True)
    if matches:
        return matches[0] / "LHM_Backups"
    return None


# Cloud retention (days)
CLOUD_RETENTION_DAYS = 30
LOCAL_RETENTION_DAYS = 7

# Where loud, human-visible failure breadcrumbs go
FAILURE_LOG = LOGS_DIR / "SYNC_FAILURES.log"


def log(msg):
    """Print with timestamp."""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {msg}")


def notify_failure(title, msg):
    """Surface a sync failure where Bob will actually see it.

    Three channels, all best-effort: timestamped line in logs/SYNC_FAILURES.log,
    a macOS notification, and stderr. The point is that a silent FAILED in
    sync.log never happens again.
    """
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {title}: {msg}"
    try:
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        with open(FAILURE_LOG, "a") as fh:
            fh.write(line + "\n")
    except Exception:
        pass
    try:
        # Keep it short; notifications truncate hard.
        short = msg.strip().splitlines()[0][:200] if msg.strip() else title
        subprocess.run(
            ["osascript", "-e",
             f'display notification {short!r} with title "LHM sync: {title}"'],
            capture_output=True, timeout=10,
        )
    except Exception:
        pass
    print(line, file=sys.stderr)


def _git(*args, **kw):
    """Run a git command in LHM_ROOT, capturing output."""
    kw.setdefault("capture_output", True)
    kw.setdefault("text", True)
    return subprocess.run(["git", *args], cwd=str(LHM_ROOT), **kw)


def git_reconcile_remote(dry_run=False):
    """Fetch and rebase local commits on top of origin/main before pushing.

    This is the fix for the silent wedge: a plain `git push` rejects forever
    (non-fast-forward) the moment anything lands on the remote out of band.
    Rebasing keeps the pipeline-sync commits linear on top. On conflict we
    abort cleanly (so the next run isn't stuck mid-rebase) and shout.
    """
    fetch = _git("fetch", "origin", "main", timeout=120)
    if fetch.returncode != 0:
        notify_failure("git fetch failed", fetch.stderr or fetch.stdout)
        return False

    # How far has the remote moved ahead of us?
    behind = _git("rev-list", "--count", "HEAD..origin/main")
    n_behind = int(behind.stdout.strip() or "0") if behind.returncode == 0 else 0
    if n_behind == 0:
        return True

    log(f"GIT SYNC: remote is {n_behind} commit(s) ahead, rebasing local work on top.")
    if dry_run:
        log("GIT SYNC [DRY RUN]: would `git rebase --autostash origin/main`")
        return True

    reb = _git("rebase", "--autostash", "origin/main", timeout=180)
    if reb.returncode != 0:
        _git("rebase", "--abort")
        notify_failure(
            "git rebase conflict",
            "Local pipeline history diverged from origin/main and auto-rebase "
            "hit a conflict. Resolve by hand:\n"
            "  cd /Users/bob/LHM && git pull --rebase origin main\n"
            f"git said:\n{reb.stderr or reb.stdout}",
        )
        return False
    return True


def git_sync(dry_run=False):
    """Reconcile with remote, auto-commit changed files, push to GitHub."""
    log("GIT SYNC: Starting...")

    os.chdir(LHM_ROOT)

    # Pull remote changes down first so the push can't wedge on non-fast-forward.
    if not git_reconcile_remote(dry_run=dry_run):
        return False

    # Stage specific directories (not everything)
    stage_paths = [
        "Strategy/",
        "Brand/",
        "Scripts/",
        "lighthouse_quant/",
        "logs/",
        ".gitignore",
    ]

    if dry_run:
        log(f"GIT SYNC [DRY RUN]: Would stage: {', '.join(stage_paths)}")
        log("GIT SYNC [DRY RUN]: Would commit and push to origin/main")
        return True

    for path in stage_paths:
        full = LHM_ROOT / path
        if full.exists():
            _git("add", path)

    # Commit if anything is staged.
    if _git("diff", "--cached", "--quiet").returncode != 0:
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        commit = _git("commit", "-m", f"Daily pipeline sync {date_str}")
        if commit.returncode != 0:
            notify_failure("git commit failed", commit.stderr or commit.stdout)
            return False
        log(f"GIT SYNC: Committed: Daily pipeline sync {date_str}")
    else:
        log("GIT SYNC: Nothing new staged.")

    # Push if we're ahead of the remote (covers fresh commits AND any
    # previously-committed-but-unpushed work the rebase carried forward).
    ahead = _git("rev-list", "--count", "origin/main..HEAD")
    if ahead.returncode == 0 and ahead.stdout.strip() == "0":
        log("GIT SYNC: Already in sync with origin/main.")
        return True

    push = _git("push", "origin", "main", timeout=120)
    if push.returncode != 0:
        notify_failure(
            "git push failed",
            "Push to origin/main was rejected. If it says 'non-fast-forward', "
            "the remote moved again — rerun the sync (it will rebase) or:\n"
            "  cd /Users/bob/LHM && git pull --rebase origin main && git push\n"
            f"git said:\n{push.stderr or push.stdout}",
        )
        return False

    log("GIT SYNC: Pushed to origin/main.")
    return True


def cloud_sync(dry_run=False):
    """Copy database backup and key folders to cloud destinations."""
    log("CLOUD SYNC: Starting...")

    date_str = datetime.now().strftime("%Y%m%d")
    backup_name = f"Lighthouse_Master_{date_str}.db"

    if not DB_SOURCE.exists():
        log(f"CLOUD SYNC: Database not found at {DB_SOURCE}")
        return False

    destinations = {
        "iCloud": _get_icloud_dir(),
        "Dropbox": DROPBOX_DIR,
    }

    success = True

    for name, dest_dir in destinations.items():
        try:
            # Check if cloud storage mount exists
            if dest_dir is None:
                log(f"CLOUD SYNC [{name}]: Mount not found, skipping.")
                continue
            if not dest_dir.parent.exists():
                log(f"CLOUD SYNC [{name}]: Mount point not found, skipping.")
                continue

            if dry_run:
                log(f"CLOUD SYNC [{name}] [DRY RUN]: Would copy {backup_name} to {dest_dir}")
                continue

            dest_dir.mkdir(parents=True, exist_ok=True)

            # Copy dated database backup
            dest_file = dest_dir / backup_name
            if not dest_file.exists():
                shutil.copy2(DB_SOURCE, dest_file)
                log(f"CLOUD SYNC [{name}]: Copied {backup_name}")
            else:
                log(f"CLOUD SYNC [{name}]: {backup_name} already exists, skipping.")

            # Dropbox also mirrors the Strategy and Brand folders (this used
            # to live on Google Drive; moved here when GDrive was retired).
            if name == "Dropbox":
                dropbox_lhm = dest_dir.parent / "LHM"
                for folder in ["Strategy", "Brand"]:
                    src = LHM_ROOT / folder
                    dst = dropbox_lhm / folder
                    if src.exists():
                        dst.mkdir(parents=True, exist_ok=True)
                        result = subprocess.run(
                            ["rsync", "-a", "--delete",
                             str(src) + "/", str(dst) + "/"],
                            capture_output=True, text=True
                        )
                        if result.returncode == 0:
                            log(f"CLOUD SYNC [{name}]: Synced {folder}/")
                        else:
                            log(f"CLOUD SYNC [{name}]: rsync {folder} failed: {result.stderr}")

            # Clean up old backups
            cleanup_cloud_backups(dest_dir, name)

        except Exception as e:
            log(f"CLOUD SYNC [{name}]: Error: {e}")
            notify_failure(f"cloud sync [{name}] failed", str(e))
            success = False

    # Chart library: canonical copy lives in Dropbox (~/Dropbox/LHM_Charts,
    # also symlinked at ~/LHM/Charts). Mirror it into iCloud Drive as a plain
    # Files folder (NOT the Photos app) so it's reachable from the phone.
    if not dry_run:
        chart_lib = Path.home() / "Dropbox" / "LHM_Charts"
        icloud_mirror = (Path.home() / "Library" / "Mobile Documents" /
                         "com~apple~CloudDocs" / "LHM_Charts")
        if chart_lib.exists():
            try:
                icloud_mirror.mkdir(parents=True, exist_ok=True)
                r = subprocess.run(["rsync", "-a", "--delete",
                                    str(chart_lib) + "/", str(icloud_mirror) + "/"],
                                   capture_output=True, text=True)
                if r.returncode == 0:
                    log("CLOUD SYNC [iCloud]: Mirrored chart library")
                else:
                    log(f"CLOUD SYNC [iCloud]: chart-library rsync failed: {r.stderr}")
            except Exception as e:
                log(f"CLOUD SYNC [iCloud]: chart-library mirror error: {e}")

    return success


def cleanup_cloud_backups(dest_dir, name):
    """Remove cloud backups older than retention period."""
    try:
        cutoff = datetime.now().timestamp() - (CLOUD_RETENTION_DAYS * 24 * 60 * 60)
        removed = 0
        for f in dest_dir.glob("Lighthouse_Master_*.db"):
            if f.stat().st_mtime < cutoff:
                f.unlink()
                removed += 1
        if removed:
            log(f"CLOUD SYNC [{name}]: Removed {removed} old backup(s) (>{CLOUD_RETENTION_DAYS} days)")
    except Exception as e:
        log(f"CLOUD SYNC [{name}]: Cleanup error: {e}")


def sync_to_all_destinations(dry_run=False):
    """Run full sync to all destinations."""
    log("=" * 60)
    log("LIGHTHOUSE MACRO - MULTI-DESTINATION SYNC")
    log("=" * 60)

    results = {}

    # 1. Git sync
    try:
        results["GitHub"] = git_sync(dry_run=dry_run)
    except Exception as e:
        log(f"GIT SYNC: Exception: {e}")
        results["GitHub"] = False

    # 2. Cloud sync
    try:
        results["Cloud"] = cloud_sync(dry_run=dry_run)
    except Exception as e:
        log(f"CLOUD SYNC: Exception: {e}")
        results["Cloud"] = False

    # Summary
    log("-" * 40)
    log("SYNC SUMMARY:")
    for dest, ok in results.items():
        status = "OK" if ok else "FAILED"
        log(f"  {dest}: {status}")
    log("=" * 60)

    return all(results.values())


def main():
    parser = argparse.ArgumentParser(description="Lighthouse Macro Multi-Destination Sync")
    parser.add_argument("--git-only", action="store_true", help="Only git commit + push")
    parser.add_argument("--cloud-only", action="store_true", help="Only cloud sync")
    parser.add_argument("--dry-run", action="store_true", help="Show what would happen")

    args = parser.parse_args()

    if args.git_only:
        git_sync(dry_run=args.dry_run)
    elif args.cloud_only:
        cloud_sync(dry_run=args.dry_run)
    else:
        sync_to_all_destinations(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
