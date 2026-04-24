#!/usr/bin/env python3
"""Chartbook layout — add commentary block to already-branded LHM chart PNGs.

Chartbook-only. Beams, Beacons, Horizons don't use this: their prose carries
the interpretation. Chartbooks have no prose layer, so each chart needs a
2-3 sentence commentary block to stand alone.

Usage:
    from chartbook_layout import wrap_for_chartbook

    wrap_for_chartbook(
        src_png='/path/to/ch10_unemployment.png',
        commentary='Headline UR looks fine at 4.4%. Flows tell a different '
                   'story: quits through 2.0%, temp help down 4% YoY, '
                   'long-term unemployed share at 25%.',
        out_png='/path/to/chartbook/ch10_unemployment.png',
    )

Or batch from a YAML spec:
    python3 chartbook_layout.py --spec chartbook_commentary.yaml

Voice rules (enforced at draft time, validated here):
  - No emdashes (commas, periods, colons, parentheses, ellipses instead)
  - No "Not X, it's Y" / "X, not Y" construction
  - Short sentences, Bob-voice, "we" frame
  - Zero speculation — only what the chart shows
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
from PIL import Image


# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------
COLORS = {
    'ocean':    '#2389BB',
    'dusk':     '#FF6723',
    'doldrums': '#898989',
    'fg':       '#1a1a1a',
    'muted':    '#555555',
    'bg':       '#ffffff',
}

# Commentary block layout inside the figure frame
# The figure total height is set to preserve the original chart's aspect + add room.
# Chart occupies the top ~70%; commentary block occupies bottom ~25%; brand bars fill the rest.
CHARTBOOK_FIGSIZE = (14, 10.5)   # Taller than Beam (14, 8) to fit commentary
CHART_TOP_FRAC = 0.96            # Where the chart sits (top edge)
CHART_BOTTOM_FRAC = 0.36         # Where the chart ends (bottom edge)
COMMENTARY_TOP_FRAC = 0.32       # Where commentary block starts
COMMENTARY_BOTTOM_FRAC = 0.06    # Where commentary block ends


# -----------------------------------------------------------------------------
# Voice validation
# -----------------------------------------------------------------------------
FORBIDDEN_PATTERNS = [
    # Emdashes
    (r'—', 'emdash (use commas, periods, colons, parens, or ellipses instead)'),
    # "Not X, it's Y" / "X, not Y" family
    (r"\bnot\s+[^,\.]{1,40},\s*(it['’]s|it\s+is)\b", '"not X, it\'s Y" construction'),
    (r"[,\.]\s+not\s+[^,\.]{1,30}[,\.\s]", '"X, not Y" construction'),
    (r"\bisn['’]t\s+[^,\.]{1,40},\s*(it['’]s|it\s+is)\b", '"isn\'t X, it\'s Y" construction'),
    # Two Books language (per memory — PiTrade not live yet)
    (r'\bCore Book\b', 'Two Books language ("Core Book") — use framework-neutral positioning'),
    (r'\bTechnical Overlay Book\b', 'Two Books language ("Technical Overlay Book") — use framework-neutral positioning'),
    # AI-tell transitions
    (r'\bcautiously optimistic\b', 'AI-tell phrase "cautiously optimistic"'),
    (r'\bgeopolitical uncertainty\b', 'AI-tell phrase "geopolitical uncertainty"'),
    (r'\bit is important to note\b', 'AI-tell phrase "it is important to note"'),
    (r'\bat the end of the day\b', 'AI-tell phrase "at the end of the day"'),
]


@dataclass
class ValidationResult:
    ok: bool
    violations: List[str]


def validate_commentary(text: str) -> ValidationResult:
    """Check commentary text against voice rules. Returns violations list."""
    violations = []
    for pattern, description in FORBIDDEN_PATTERNS:
        matches = re.findall(pattern, text, flags=re.IGNORECASE)
        if matches:
            for m in matches[:3]:  # Cap at 3 per pattern to avoid spam
                violations.append(f'{description}: "{m[:60]}"' if isinstance(m, str) else description)
    return ValidationResult(ok=not violations, violations=violations)


# -----------------------------------------------------------------------------
# Layout engine
# -----------------------------------------------------------------------------
def wrap_for_chartbook(
    src_png: str | Path,
    commentary: str,
    out_png: str | Path,
    *,
    strict: bool = False,
) -> dict:
    """Take a rendered LHM-branded chart PNG, add a Chartbook commentary block.

    Args:
        src_png: path to the input PNG (already branded per Beam spec).
        commentary: 2-3 sentence read of what the chart is saying. Bob-voice.
        out_png: where to write the Chartbook-layout PNG.
        strict: if True, raise on voice violations. Default: warn and continue.

    Returns:
        dict with `out_path`, `voice_ok`, `voice_violations`.
    """
    src_png = Path(src_png)
    out_png = Path(out_png)

    # Voice validation
    vr = validate_commentary(commentary)
    if not vr.ok:
        msg = f'Voice violations in commentary for {src_png.name}:\n  - ' + '\n  - '.join(vr.violations)
        if strict:
            raise ValueError(msg)
        print(f'WARNING: {msg}', file=sys.stderr)

    # Load source chart
    chart_img = mpimg.imread(str(src_png))
    src_h, src_w = chart_img.shape[:2]
    src_ar = src_w / src_h

    # Build new figure — same width as original, but taller
    # We keep the chart's pixel-for-pixel aspect by computing a target figsize
    # that preserves the source chart proportions in the top region.
    # Default: 14x10.5 figure, chart occupies top 60% = 6.3in tall at 14in wide.
    # If the source chart's natural ratio differs, adapt.
    fig_w = 14.0
    chart_h_in = fig_w / src_ar
    # Commentary height scales with line count. 13pt Inter at 1.55 linespacing ≈ 0.30in/line.
    # Add 0.4in padding above and below text.
    wrapped = _wrap_commentary(commentary, char_width=110)
    n_lines = wrapped.count('\n') + 1
    commentary_h_in = max(1.1, 0.30 * n_lines + 0.55)
    brand_pad_in = 0.5
    fig_h = chart_h_in + commentary_h_in + brand_pad_in

    fig = plt.figure(figsize=(fig_w, fig_h), facecolor=COLORS['bg'])

    # -- Chart region (top portion) --
    # Compute axes bounds as fraction of new figure
    chart_top = 1.0 - (brand_pad_in * 0.5) / fig_h
    chart_bottom = chart_top - chart_h_in / fig_h
    ax_chart = fig.add_axes([0.0, chart_bottom, 1.0, chart_top - chart_bottom])
    ax_chart.imshow(chart_img, aspect='auto')
    ax_chart.axis('off')

    # -- Commentary region (middle-lower portion) --
    commentary_top = chart_bottom - 0.01
    commentary_bottom = (brand_pad_in * 0.5) / fig_h + 0.015
    ax_comm = fig.add_axes([0.06, commentary_bottom, 0.88, commentary_top - commentary_bottom])
    ax_comm.axis('off')
    ax_comm.set_xlim(0, 1)
    ax_comm.set_ylim(0, 1)

    # Commentary styling: subtle left rule + text
    # Ocean vertical rule on the left signals "this is commentary, read it"
    ax_comm.plot([0.0, 0.0], [0.05, 0.95], color=COLORS['ocean'], linewidth=2.5,
                 transform=ax_comm.transAxes, clip_on=False)

    ax_comm.text(
        0.015, 0.95, wrapped,
        fontsize=13, color=COLORS['fg'],
        ha='left', va='top',
        family='sans-serif',
        linespacing=1.55,
        transform=ax_comm.transAxes,
        wrap=True,
    )

    # -- Optional: thin Ocean border around the full figure --
    # The source chart already has its own border. We don't double it.
    # But we do add a subtle outer wrapper so the commentary feels inside
    # the same frame.
    fig.patches.append(plt.Rectangle(
        (0, 0), 1, 1, transform=fig.transFigure,
        fill=False, edgecolor=COLORS['ocean'], linewidth=1.5,
        zorder=100, clip_on=False,
    ))

    # Save
    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(
        str(out_png),
        dpi=200, bbox_inches='tight', pad_inches=0.1,
        facecolor=COLORS['bg'], edgecolor='none',
    )
    plt.close(fig)

    return {
        'out_path': str(out_png),
        'voice_ok': vr.ok,
        'voice_violations': vr.violations,
    }


def _wrap_commentary(text: str, char_width: int = 110) -> str:
    """Manually wrap text so matplotlib renders it consistently across platforms.

    matplotlib's wrap=True only fires at draw time and can produce inconsistent
    results across DPI settings. Pre-wrapping is reliable.
    """
    words = text.split()
    lines, current = [], []
    cur_len = 0
    for w in words:
        add_len = len(w) + (1 if current else 0)
        if cur_len + add_len > char_width and current:
            lines.append(' '.join(current))
            current, cur_len = [w], len(w)
        else:
            current.append(w)
            cur_len += add_len
    if current:
        lines.append(' '.join(current))
    return '\n'.join(lines)


# -----------------------------------------------------------------------------
# Batch runner
# -----------------------------------------------------------------------------
def batch_wrap(spec_path: str | Path, *, strict: bool = False) -> Dict[str, dict]:
    """Wrap a batch of charts from a YAML spec.

    Spec format (YAML):
        src_dir: /path/to/charts
        out_dir: /path/to/chartbook_wrapped
        charts:
          - file: ch01_quits_rate.png
            commentary: "Quits through 2.0% for the fifth time in fifteen months..."
          - file: ch02_ltu_share.png
            commentary: "..."
    """
    try:
        import yaml
    except ImportError:
        print('ERROR: batch mode requires PyYAML. Install with: brew install pyyaml', file=sys.stderr)
        sys.exit(3)

    spec_path = Path(spec_path)
    spec = yaml.safe_load(spec_path.read_text())

    src_dir = Path(spec['src_dir'])
    out_dir = Path(spec['out_dir'])
    out_dir.mkdir(parents=True, exist_ok=True)

    results = {}
    total = len(spec['charts'])
    for i, entry in enumerate(spec['charts'], 1):
        file = entry['file']
        commentary = entry['commentary']
        src = src_dir / file
        out = out_dir / file
        if not src.exists():
            print(f'  [{i}/{total}] MISSING: {src}', file=sys.stderr)
            results[file] = {'error': 'source not found'}
            continue
        try:
            r = wrap_for_chartbook(src, commentary, out, strict=strict)
            results[file] = r
            status = 'OK' if r['voice_ok'] else 'VOICE_WARN'
            print(f'  [{i}/{total}] {status} -> {out.name}', file=sys.stderr)
        except Exception as e:
            results[file] = {'error': str(e)}
            print(f'  [{i}/{total}] FAIL: {file} — {e}', file=sys.stderr)

    ok = sum(1 for r in results.values() if r.get('voice_ok'))
    warn = sum(1 for r in results.values() if r.get('voice_ok') is False)
    fail = sum(1 for r in results.values() if 'error' in r)
    print(f'\nBatch done: {ok} clean, {warn} voice warnings, {fail} failed', file=sys.stderr)
    return results


# -----------------------------------------------------------------------------
# CLI
# -----------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description='Wrap LHM charts with Chartbook commentary block.')
    sub = ap.add_subparsers(dest='cmd', required=True)

    # Single-chart mode
    sp_one = sub.add_parser('one', help='Wrap a single chart')
    sp_one.add_argument('src', help='Source PNG (already Beam-branded)')
    sp_one.add_argument('out', help='Output PNG')
    sp_one.add_argument('--commentary', required=True, help='Commentary text (2-3 sentences)')
    sp_one.add_argument('--strict', action='store_true', help='Fail on voice violations')

    # Batch mode
    sp_batch = sub.add_parser('batch', help='Wrap a batch from a YAML spec')
    sp_batch.add_argument('spec', help='YAML spec file')
    sp_batch.add_argument('--strict', action='store_true', help='Fail on voice violations')

    args = ap.parse_args()

    if args.cmd == 'one':
        r = wrap_for_chartbook(args.src, args.commentary, args.out, strict=args.strict)
        if not r['voice_ok']:
            print('Voice violations:', file=sys.stderr)
            for v in r['voice_violations']:
                print(f'  - {v}', file=sys.stderr)
            sys.exit(2)
    elif args.cmd == 'batch':
        results = batch_wrap(args.spec, strict=args.strict)
        fail = sum(1 for r in results.values() if 'error' in r)
        sys.exit(1 if fail else 0)


if __name__ == '__main__':
    main()
