#!/usr/bin/env python3
"""
HTML → branded PDF renderer for Lighthouse Macro pieces.

Takes a publish-ready LHM HTML file (Beacon / Beam / Horizon / Chartbook /
Educational) and renders a clean, properly-paginated PDF by injecting a
print stylesheet before render. The print CSS fixes the two defects naive
Chrome print produces on Substack-style scroll HTML:

  1. Charts / figures sliced across page boundaries
     -> break-inside: avoid on every figure / chart / img / svg / table
  2. Pages 40-60% empty whitespace because a too-tall block bumped forward
     -> cap media max-height below one page so blocks always fit, and
        let breaks fall between blocks rather than inside them

Reusable. Same function works for any LHM piece HTML.

Usage:
    python html_to_branded_pdf.py INPUT.html OUTPUT.pdf
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

# Injected print stylesheet. Comes last in the cascade and uses !important
# so it overrides any piece-specific @media print rules.
PRINT_CSS = """
<style id="lhm-print-fix">
@page {
  size: Letter;
  margin: 14mm 15mm 16mm 15mm;
}
@media print {
  * {
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
  }
  html, body {
    margin: 0 !important;
    padding: 0 !important;
    background: #ffffff !important;
  }
  /* Never let a visual element split across a page break. */
  figure, .chart, .lhm-figblock, img, svg, table, .lhm-fignum,
  .lhm-figsrc, figcaption, .callout, blockquote, pre {
    break-inside: avoid !important;
    page-break-inside: avoid !important;
  }
  /* A chart taller than a page is what creates the giant orphan gaps:
     cap media height below one printable page so a block always fits in
     the space remaining or cleanly starts the next page with little waste. */
  img, svg {
    max-width: 100% !important;
    height: auto !important;
    max-height: 8.4in !important;
    display: block;
    margin-left: auto;
    margin-right: auto;
  }
  figure {
    margin: 10px auto 14px !important;
    max-height: 9in !important;
  }
  /* Headers must not strand at the bottom of a page. */
  h1, h2, h3, h4 {
    break-after: avoid !important;
    page-break-after: avoid !important;
    break-inside: avoid !important;
  }
  p { orphans: 3; widows: 3; }
  /* Kill full-viewport heroes / sticky chrome / dark page bg that waste
     a whole sheet or fight the print. */
  [style*="100vh"], [style*="min-height"] { min-height: 0 !important; height: auto !important; }
  nav, .nav, .sticky, [style*="position:fixed"], [style*="position: fixed"] {
    position: static !important;
  }
}
</style>
"""


def render(html_path: str, out_path: str) -> str:
    src = Path(html_path)
    html = src.read_text(errors="ignore")

    # Inject the print fix as the last thing before </head> so it wins the
    # cascade. Fall back to prepending into <body> or the top of the doc.
    low = html.lower()
    if "</head>" in low:
        idx = low.index("</head>")
        html = html[:idx] + PRINT_CSS + html[idx:]
    elif "<body" in low:
        idx = low.index("<body")
        end = low.index(">", idx) + 1
        html = html[:end] + PRINT_CSS + html[end:]
    else:
        html = PRINT_CSS + html

    with tempfile.NamedTemporaryFile(
        "w", suffix=".html", delete=False, dir=str(src.parent)
    ) as tf:
        tf.write(html)
        tmp_html = tf.name

    try:
        cmd = [
            CHROME, "--headless", "--disable-gpu",
            "--no-pdf-header-footer", "--print-to-pdf-no-header",
            "--run-all-compositor-stages-before-draw",
            "--virtual-time-budget=15000",
            f"--print-to-pdf={out_path}",
            f"file://{tmp_html}",
        ]
        subprocess.run(cmd, capture_output=True, timeout=180)
    finally:
        try:
            Path(tmp_html).unlink()
        except OSError:
            pass

    if not Path(out_path).exists():
        raise RuntimeError(f"Chrome did not produce {out_path}")
    return out_path


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("usage: html_to_branded_pdf.py INPUT.html OUTPUT.pdf")
        sys.exit(2)
    print(render(sys.argv[1], sys.argv[2]))
