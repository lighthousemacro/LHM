"""Build self-contained HTML for the Two Economies Twitter Article.
Embeds charts as base64, inline CSS, LHM brand system.
"""
import base64
from pathlib import Path
import re

CHART_DIR = Path('/Users/bob/LHM/Outputs/Charts/two_economies')
MD_FILE = Path('/Users/bob/LHM/Outputs/Content/two_economies_twitter_article.md')
OUT_FILE = Path('/Users/bob/LHM/Outputs/Content/two_economies_twitter_article.html')


def embed_chart(fig_name: str, alt: str) -> str:
    path = CHART_DIR / fig_name
    b64 = base64.b64encode(path.read_bytes()).decode('ascii')
    return (
        '<figure class="chart">'
        f'<img src="data:image/png;base64,{b64}" alt="{alt}">'
        '</figure>'
    )


CHART_MAP = {
    'Figure 1: Who Owns America': ('fig1_wealth_concentration.png', 'Figure 1: Who Owns America'),
    'Figure 3: Personal Savings Rate by Income Group': ('fig3_savings_rate_quintile.png', 'Figure 3: Personal Savings Rate by Income Group'),
    'Figure 5: Vehicle Repossessions': ('fig5_vehicle_repossessions.png', 'Figure 5: Vehicle Repossessions'),
    'Figure 6: Delinquency by Loan Type': ('fig6_delinquency_by_loan_type.png', 'Figure 6: Delinquency by Loan Type, Q4 2025 vs Q4 2019'),
    'Figure 7: Employment by Firm Size': ('fig7_employment_by_firm_size.png', 'Figure 7: Employment by Firm Size (ADP)'),
    'Figure 11: Great Wealth Transfer': ('fig11_wealth_transfer.png', 'Figure 11: The Great Wealth Transfer'),
    'Figure 12: First-Time Buyer Down Payment Sources': ('fig12_downpayment_sources.png', 'Figure 12: First-Time Buyer Down Payment Sources'),
}

md = MD_FILE.read_text()

# Strip the first H1 — we render the title in the header ourselves
md = re.sub(r'^# .*\n', '', md, count=1).lstrip()

# Convert markdown to HTML (minimal parser — just what this doc uses)
html_body = []
in_list = False
for block in re.split(r'\n\n+', md.strip()):
    block = block.strip()
    if not block:
        continue
    # Horizontal rules
    if block == '---':
        html_body.append('<hr>')
        continue
    # Chart placeholder
    m = re.match(r'^\*\*\[(Figure \d+[^\]]+)\]\*\*$', block)
    if m:
        key = m.group(1)
        if key in CHART_MAP:
            fname, alt = CHART_MAP[key]
            html_body.append(embed_chart(fname, alt))
        continue
    # H2
    if block.startswith('## '):
        html_body.append(f'<h2>{block[3:].strip()}</h2>')
        continue
    # Blockquote / italic lead
    if block.startswith('*') and block.endswith('*') and '\n' not in block and not block.startswith('**'):
        html_body.append(f'<p class="lede"><em>{block[1:-1]}</em></p>')
        continue
    # Sign-off line
    if block.startswith('**— ') or block.startswith('**—'):
        inner = block.strip('*').strip()
        html_body.append(f'<p class="signoff"><strong>{inner}</strong></p>')
        continue
    # Teaser line for Beacon
    if block.startswith('**Full chart pack'):
        inner = block.strip('*').strip()
        html_body.append(f'<p class="beacon-teaser"><strong>{inner}</strong></p>')
        continue
    if block == "*Don't navigate in the dark. Join The Watch.*":
        html_body.append('<p class="cta"><em>Don\'t navigate in the dark. Join The Watch.</em></p>')
        continue
    # Default: paragraph with inline bold/italic/quotes
    para = block
    # Convert **bold**
    para = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', para)
    # Convert *italic* (but not already-consumed)
    para = re.sub(r'(?<!\*)\*([^*\n]+)\*(?!\*)', r'<em>\1</em>', para)
    # Line breaks inside a paragraph block
    para = para.replace('\n', '<br>')
    html_body.append(f'<p>{para}</p>')

body_html = '\n'.join(html_body)

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Two Economies: Why the Consumer Can't Quit | Lighthouse Macro</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Montserrat:wght@600;700;800&display=swap');

  :root {{
    --ocean: #2389BB;
    --dusk: #FF6723;
    --sky: #23BBFF;
    --venus: #FF2389;
    --sea: #00BB89;
    --doldrums: #898989;
    --starboard: #238923;
    --port: #892323;
    --fog: #D1D1D1;
    --ink: #1a1a1a;
  }}

  * {{ margin: 0; padding: 0; box-sizing: border-box; }}

  body {{
    font-family: 'Inter', -apple-system, sans-serif;
    background: #f4f6f8;
    color: var(--ink);
    line-height: 1.65;
    font-size: 17px;
  }}

  .header {{
    background: white;
    padding: 34px 24px 20px;
    text-align: center;
    border-bottom: 1px solid #e0e0e0;
  }}
  .header-bar {{
    height: 5px;
    background: linear-gradient(to right, var(--ocean) 67%, var(--dusk) 67%);
    margin: -34px -24px 22px;
  }}
  .header .kicker {{
    font-family: 'Montserrat', sans-serif;
    font-size: 12px;
    font-weight: 700;
    color: var(--ocean);
    letter-spacing: 2px;
    margin-bottom: 14px;
  }}
  .header h1 {{
    font-family: 'Montserrat', sans-serif;
    font-size: 34px;
    font-weight: 800;
    color: var(--ink);
    line-height: 1.15;
    max-width: 820px;
    margin: 0 auto 10px;
  }}
  .header .subhead {{
    font-size: 17px;
    color: var(--doldrums);
    font-style: italic;
    max-width: 680px;
    margin: 0 auto;
  }}
  .header .byline {{
    font-size: 13px;
    color: var(--doldrums);
    margin-top: 18px;
    letter-spacing: 0.5px;
  }}

  article {{
    max-width: 720px;
    margin: 0 auto;
    padding: 40px 24px 20px;
    background: white;
    border-left: 1px solid #e0e0e0;
    border-right: 1px solid #e0e0e0;
  }}

  article p {{
    margin-bottom: 18px;
    color: #2a2a2a;
  }}

  article p.lede {{
    font-size: 19px;
    color: var(--doldrums);
    border-left: 3px solid var(--ocean);
    padding-left: 18px;
    margin-bottom: 32px;
    line-height: 1.55;
  }}

  article h2 {{
    font-family: 'Montserrat', sans-serif;
    font-size: 24px;
    font-weight: 700;
    color: var(--ocean);
    margin: 38px 0 18px;
    padding-bottom: 8px;
    border-bottom: 2px solid var(--fog);
  }}

  article strong {{
    color: var(--ink);
    font-weight: 700;
  }}

  article em {{
    color: #2a2a2a;
  }}

  figure.chart {{
    margin: 28px -24px;
    background: #fafbfc;
    padding: 16px;
    border-top: 1px solid #eee;
    border-bottom: 1px solid #eee;
  }}
  figure.chart img {{
    width: 100%;
    height: auto;
    display: block;
    border: 4px solid var(--ocean);
  }}

  hr {{
    border: none;
    height: 1px;
    background: var(--fog);
    margin: 32px 0;
  }}

  p.beacon-teaser {{
    background: #fafbfc;
    border-left: 3px solid var(--dusk);
    padding: 14px 18px;
    margin: 28px 0;
    font-size: 16px;
    color: var(--ink);
  }}

  p.cta {{
    text-align: center;
    font-size: 18px;
    color: var(--ocean);
    margin: 12px 0;
  }}

  p.signoff {{
    text-align: center;
    font-family: 'Montserrat', sans-serif;
    font-size: 14px;
    color: var(--ocean);
    letter-spacing: 1.5px;
    margin-top: 8px;
  }}

  .footer {{
    max-width: 720px;
    margin: 0 auto;
    padding: 28px 24px 48px;
    background: white;
    border-left: 1px solid #e0e0e0;
    border-right: 1px solid #e0e0e0;
    border-bottom: 4px solid var(--ocean);
    text-align: center;
    color: var(--doldrums);
    font-size: 13px;
  }}
  .footer .accent-bar {{
    height: 4px;
    background: linear-gradient(to right, var(--ocean) 67%, var(--dusk) 67%);
    margin-bottom: 20px;
  }}
  .footer a {{ color: var(--ocean); text-decoration: none; }}
  .footer .tagline {{
    font-family: 'Montserrat', sans-serif;
    font-weight: 700;
    color: var(--ocean);
    letter-spacing: 1.5px;
    margin-top: 10px;
    font-size: 12px;
  }}

  @media (max-width: 640px) {{
    body {{ font-size: 16px; }}
    .header h1 {{ font-size: 26px; }}
    .header .subhead {{ font-size: 15px; }}
    article {{ padding: 28px 18px; }}
    article h2 {{ font-size: 20px; }}
    figure.chart {{ margin: 22px -18px; }}
  }}
</style>
</head>
<body>

<header class="header">
  <div class="header-bar"></div>
  <div class="kicker">LIGHTHOUSE MACRO</div>
  <h1>Two Economies: Why the Consumer Can't Quit</h1>
  <div class="subhead">We laid out the framework in January. The conversation has caught up. Here is where the threads connect, with the full chart pack underneath.</div>
  <div class="byline">Bob Sheehan, CFA, CMT &nbsp;·&nbsp; Apr 17, 2026</div>
</header>

<article>
{body_html}
</article>

<div class="footer">
  <div class="accent-bar"></div>
  <p><strong>Bob Sheehan, CFA, CMT</strong> &nbsp;|&nbsp; Founder &amp; Chief Investment Officer</p>
  <p>Lighthouse Macro &nbsp;|&nbsp; <a href="https://lighthousemacro.com">LighthouseMacro.com</a> &nbsp;|&nbsp; @LHMacro</p>
  <p class="tagline">MACRO, ILLUMINATED.</p>
</div>

</body>
</html>
"""

OUT_FILE.write_text(html)
size_mb = OUT_FILE.stat().st_size / 1024 / 1024
print(f"Wrote: {OUT_FILE}")
print(f"Size: {size_mb:.2f} MB")
print(f"Charts embedded: {len(CHART_MAP)}")
