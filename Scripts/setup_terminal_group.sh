#!/bin/bash
# Builds 3 Terminal profiles cloned from "Bob" with distinct background colors.
# Profiles: Bob-Main (dark red, current), Bob-Remote (dark blue), Bob-Second (dark green)

set -e

PLIST=~/Library/Preferences/com.apple.Terminal.plist
PB=/usr/libexec/PlistBuddy

# Quit Terminal first so plist writes take effect on next launch
echo "This will modify Terminal profiles. Quit Terminal first, then press enter."
read -r

# Helper: encode an NSColor plist for a given R G B (0-1 floats) and write to a plist key.
# Terminal stores BackgroundColor as an NSKeyedArchiver-encoded NSColor.
# Easiest path: clone Bob, then overwrite the BackgroundColor via a Python helper.

python3 <<'PYEOF'
import plistlib, subprocess, os, copy
from pathlib import Path

plist_path = Path.home() / "Library/Preferences/com.apple.Terminal.plist"

# Terminal caches preferences — force a read from disk
subprocess.run(["defaults", "read", "com.apple.Terminal"], capture_output=True)

with open(plist_path, "rb") as f:
    data = plistlib.load(f)

settings = data["Window Settings"]
base = copy.deepcopy(settings["Bob"])

def make_nscolor_archive(r, g, b):
    """Build an NSKeyedArchiver plist for NSColor with given RGB (0-1)."""
    rgb_str = f"{r} {g} {b}"
    archive = {
        "$version": 100000,
        "$archiver": "NSKeyedArchiver",
        "$top": {"root": plistlib.UID(1)},
        "$objects": [
            "$null",
            {
                "$class": plistlib.UID(3),
                "NSRGB": rgb_str.encode("ascii") + b"\x00",
                "NSColorSpace": 2,
            },
            "NSColor",
            {
                "$classname": "NSColor",
                "$classes": ["NSColor", "NSObject"],
            },
        ],
    }
    # fix: class UID should point to the class dict (index 3), object's $class -> 3
    archive["$objects"][1]["$class"] = plistlib.UID(3)
    return plistlib.dumps(archive, fmt=plistlib.FMT_BINARY)

def clone(name, command, r, g, b, window_title):
    p = copy.deepcopy(base)
    p["name"] = name
    p["CommandString"] = command
    p["WindowTitle"] = window_title
    p["RunCommandAsShell"] = 1  # run inside shell so `cd` and aliases work
    p["BackgroundColor"] = make_nscolor_archive(r, g, b)
    p["shellExitAction"] = 1  # don't close on exit
    p["warnOnShellCloseAction"] = 2  # always prompt
    return p

# Profiles
# Bob-Main: keep Bob's current dark red (0.5, 0, 0)
settings["Bob-Main"] = clone(
    "Bob-Main",
    "cd /Users/bob/LHM && caffeinate -i claude",
    0.5, 0.0, 0.0,
    "LHM Main",
)

# Bob-Remote: dark blue, remote-control
settings["Bob-Remote"] = clone(
    "Bob-Remote",
    "cd /Users/bob/LHM && caffeinate -i claude remote-control",
    0.0, 0.15, 0.35,
    "LHM Remote",
)

# Bob-Second: dark green, second main
settings["Bob-Second"] = clone(
    "Bob-Second",
    "cd /Users/bob/LHM && caffeinate -i claude",
    0.05, 0.25, 0.1,
    "LHM Second",
)

with open(plist_path, "wb") as f:
    plistlib.dump(data, f)

print("Wrote profiles: Bob-Main, Bob-Remote, Bob-Second")
PYEOF

# Force cfprefsd to reload
killall cfprefsd 2>/dev/null || true

echo ""
echo "Done. Next steps:"
echo "  1. Open Terminal"
echo "  2. Open 3 new windows: Shell > New Window > [Bob-Main | Bob-Remote | Bob-Second]"
echo "  3. Position: Bob-Main left half, Bob-Second right half"
echo "  4. Move Bob-Remote to a different Space (3-finger swipe up, drag to new desktop)"
echo "  5. Terminal menu > Window > Save Windows as Group... > name it 'LHM'"
echo "  6. Check 'Use window group when Terminal starts' if you want auto-open"
echo ""
echo "To open later: Window > Open Window Group > LHM"
