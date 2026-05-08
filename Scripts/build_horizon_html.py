"""
Build the publish-ready HTML for Horizon May 2026 v2.

Process:
  1. Read the v2 markdown
  2. Convert markdown to HTML
  3. Replace [Figure N: ...] placeholders with embedded base64 images
  4. Wrap in LHM-branded HTML template
  5. Save final HTML + a copy to Desktop
"""
import os
import re
import base64
import shutil
from datetime import datetime

import markdown

SLUG_DIR = '/Users/bob/LHM/Outputs/horizon_may_2026'
MD_PATH = f'{SLUG_DIR}/horizon_may_2026_v2.md'
HTML_OUT = f'{SLUG_DIR}/horizon_may_2026_v2.html'
DESKTOP_COPY = '/Users/bob/Desktop/Horizon_May_2026_PUBLISH.html'

CHART_DIR = '/Users/bob/LHM/Outputs/charts/horizon_may_2026'

CHART_FILES = {
    1:  'chart_01_mri.png',
    2:  'chart_02_fomc_dissents.png',
    3:  'chart_03_treasury_borrowing.png',
    4:  'chart_04_spy_breadth.png',
    5:  'chart_05_yields.png',
    6:  'chart_06_term_premium.png',
    7:  'chart_07_sbd.png',
    8:  'chart_08_clg.png',
    9:  'chart_09_hire_quit_combined.png',
    10: 'chart_11_hyperscaler.png',
    11: 'chart_12_semi_ip.png',
    12: 'chart_13_eps_decomp.png',
    13: 'chart_14_book_composition.png',
}

# All tables now render as native HTML for the May 2026 Horizon — the
# Book table restructured into 8 positions with a different schema, and
# the Chart Specifications table was replaced with prose. Risk Matrix
# stays native too for consistency with the rest of the doc.
TABLE_PNGS = {}
TABLE_FIRST_HEADER = {}


def img_to_b64(path):
    with open(path, 'rb') as f:
        return 'data:image/png;base64,' + base64.b64encode(f.read()).decode('ascii')


def replace_figures(md_text):
    """Replace [Figure N: ...] placeholders with markdown image refs that we'll
    later inline as base64."""
    pattern = re.compile(r'\[Figure (\d+):([^\]]+)\]')

    def repl(m):
        n = int(m.group(1))
        caption = m.group(2).strip().rstrip('.')
        path = CHART_FILES.get(n)
        if not path:
            return f'<div class="figure-missing"><b>Figure {n}.</b> <i>{caption}</i> &nbsp;<span class="missing-tag">[manual data — chart pending]</span></div>'
        full = os.path.join(CHART_DIR, path)
        if not os.path.exists(full):
            return f'<div class="figure-missing"><b>Figure {n}.</b> <i>{caption}</i> &nbsp;<span class="missing-tag">[chart not found]</span></div>'
        b64 = img_to_b64(full)
        # Truncate the caption to a reasonable length for visual cleanliness
        short = caption.split('.')[0].strip()
        if len(short) > 200:
            short = short[:200] + '...'
        return (f'<figure class="lhm-figure">'
                f'<img src="{b64}" alt="Figure {n}">'
                f'<figcaption><strong>Figure {n}.</strong> {short}.</figcaption>'
                f'</figure>')

    return pattern.sub(repl, md_text)


def replace_tables_with_pngs(md_text):
    """Find each known markdown table and replace it with a base64-embedded PNG.
    Detection: each table starts with a unique header line; the table block
    runs until the first non-table line (line not starting with '|')."""
    lines = md_text.split('\n')
    out = []
    i = 0
    while i < len(lines):
        line = lines[i]
        matched_key = None
        for key, hdr in TABLE_FIRST_HEADER.items():
            if line.startswith(hdr):
                matched_key = key
                break
        if matched_key is None:
            out.append(line)
            i += 1
            continue

        # Skip the table block: collect all consecutive lines starting with '|'
        # plus the separator row (---|---|...)
        while i < len(lines) and (lines[i].startswith('|') or lines[i].strip() == ''):
            if lines[i].strip() == '':
                # Blank line ends the table
                break
            i += 1

        # Insert the PNG reference
        png_name = TABLE_PNGS[matched_key]
        png_path = os.path.join(CHART_DIR, png_name)
        if os.path.exists(png_path):
            b64 = img_to_b64(png_path)
            out.append(f'<figure class="lhm-table"><img src="{b64}" alt="LHM table"></figure>')
        else:
            out.append(f'<div class="figure-missing">[Table PNG missing: {png_name}]</div>')

    return '\n'.join(out)


def build():
    with open(MD_PATH) as f:
        md = f.read()

    # Replace tables FIRST with embedded PNGs
    md = replace_tables_with_pngs(md)

    # Replace figures BEFORE markdown conversion so the HTML lands inline
    md = replace_figures(md)

    # Convert markdown to HTML
    body_html = markdown.markdown(md, extensions=['tables', 'extra', 'sane_lists'])

    # Wrap in LHM-branded template
    template = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Horizon May 2026 — The Test Came Back. The Tape Did Not Listen.</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Montserrat:wght@600;700;800&display=swap');
body {{
    font-family: 'Inter', -apple-system, sans-serif;
    color: #1a1a1a;
    max-width: 780px;
    margin: 0 auto;
    padding: 2.5rem 2rem 4rem;
    line-height: 1.65;
    font-size: 17px;
    background: #ffffff;
}}
h1, h2, h3 {{
    font-family: 'Montserrat', sans-serif;
    color: #2389BB;
    line-height: 1.25;
    margin-top: 2.2em;
    margin-bottom: 0.4em;
}}
h1 {{
    font-size: 2.4em;
    border-bottom: 4px solid #FF6723;
    padding-bottom: 0.4em;
    margin-top: 0;
}}
h1 + h2 {{
    margin-top: 0.4em;
    color: #FF6723;
    font-style: italic;
    font-weight: 600;
    font-size: 1.4em;
    border: none;
}}
h2 {{
    font-size: 1.6em;
    border-bottom: 1px solid #e0e7ec;
    padding-bottom: 0.25em;
}}
h3 {{
    font-size: 1.25em;
    color: #2389BB;
}}
hr {{
    border: 0;
    height: 1px;
    background: #d1d1d1;
    margin: 2.5em 0;
}}
p {{ margin: 0.85em 0; }}
strong {{ color: #1a1a1a; font-weight: 700; }}
em {{ color: #555555; }}
table {{
    border-collapse: collapse;
    width: 100%;
    margin: 1.5em 0;
    font-size: 14px;
    line-height: 1.45;
}}
th {{
    background: #2389BB;
    color: white;
    padding: 10px 12px;
    text-align: left;
    font-weight: 600;
    font-size: 13px;
    letter-spacing: 0.02em;
}}
td {{
    padding: 9px 12px;
    border-bottom: 1px solid #e8eef2;
}}
tr:nth-child(even) td {{ background: #f5f8fa; }}
ul, ol {{ padding-left: 1.5em; }}
li {{ margin: 0.35em 0; }}
.lhm-figure, .lhm-table {{
    margin: 2em 0;
    text-align: center;
}}
.lhm-table img {{
    width: 100%;
    max-width: 760px;
    height: auto;
    border: 1px solid #e0e7ec;
    border-radius: 2px;
}}
.lhm-figure img {{
    width: 100%;
    max-width: 760px;
    height: auto;
    border: 1px solid #e0e7ec;
    border-radius: 2px;
}}
.lhm-figure figcaption {{
    font-size: 13px;
    color: #555555;
    margin-top: 0.6em;
    font-style: italic;
    text-align: center;
}}
.figure-missing {{
    background: #fff8ed;
    border: 1px dashed #FF6723;
    padding: 12px 16px;
    margin: 1.5em 0;
    font-size: 13px;
    color: #555555;
    border-radius: 3px;
}}
.missing-tag {{
    color: #FF6723;
    font-weight: 600;
    font-size: 12px;
}}
blockquote {{
    border-left: 3px solid #2389BB;
    margin: 1.5em 0;
    padding: 0.4em 1.2em;
    color: #555555;
    background: #f8fafb;
}}
code, pre {{
    font-family: 'Source Code Pro', ui-monospace, monospace;
    font-size: 14px;
}}
.lhm-header {{
    border-top: 4px solid #2389BB;
    border-bottom: 1px solid #FF6723;
    padding: 8px 0;
    font-size: 12px;
    letter-spacing: 0.18em;
    color: #2389BB;
    font-weight: 700;
    text-transform: uppercase;
    text-align: center;
    margin-bottom: 2em;
}}
.lhm-footer {{
    border-top: 4px solid #2389BB;
    border-bottom: 1px solid #FF6723;
    padding: 1em 0;
    margin-top: 4em;
    color: #2389BB;
    text-align: center;
    font-size: 13px;
    letter-spacing: 0.05em;
}}
.lhm-footer a {{
    color: #2389BB;
    text-decoration: none;
    margin: 0 0.5em;
    font-weight: 600;
}}
.lhm-footer a:hover {{ text-decoration: underline; }}
</style>
</head>
<body>
<div class="lhm-header">Lighthouse Macro &nbsp;|&nbsp; The Horizon &nbsp;|&nbsp; {datetime.now().strftime("%B %Y")}</div>
{body_html}
<div class="lhm-footer">
<a href="https://lighthousemacro.com">Lighthouse Macro</a> |
<a href="https://research.lighthousemacro.com">Research</a> |
<a href="https://x.com/LHMacro">@LHMacro</a>
<br><br>
<em>Bob Sheehan, CFA, CMT &nbsp;|&nbsp; Founder & Chief Investment Officer</em><br>
<strong style="letter-spacing: 0.1em;">MACRO, ILLUMINATED.</strong>
</div>
</body>
</html>
'''

    with open(HTML_OUT, 'w') as f:
        f.write(template)
    size_mb = os.path.getsize(HTML_OUT) / 1024 / 1024
    print(f'Wrote {HTML_OUT} ({size_mb:.1f} MB)')

    # Copy to Desktop
    shutil.copy(HTML_OUT, DESKTOP_COPY)
    print(f'Copied to {DESKTOP_COPY}')


if __name__ == '__main__':
    build()
