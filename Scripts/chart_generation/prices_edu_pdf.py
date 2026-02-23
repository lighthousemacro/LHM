#!/usr/bin/env python3
"""
Generate Lighthouse Macro branded PDF for Prices Educational Article.
Style matches generate_two_books_pdf.py (the canonical LHM PDF style).
"""

import os
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle,
    PageBreak, HRFlowable, KeepTogether, CondPageBreak
)
from PIL import Image as PILImage

# ============================================
# BRAND COLORS (matches Two Books PDF)
# ============================================
OCEAN_BLUE = colors.HexColor('#2389BB')
DUSK_ORANGE = colors.HexColor('#FF6723')
DARK_GRAY = colors.HexColor('#333333')
LIGHT_GRAY = colors.HexColor('#F5F5F5')
MUTED_GRAY = colors.HexColor('#555555')
WHITE = colors.white

# ============================================
# PATHS
# ============================================
BASE_PATH = '/Users/bob/LHM'
ARTICLE_DIR = f'{BASE_PATH}/Outputs/Educational_Charts/Prices_Post_2'
CHART_DIR = f'{ARTICLE_DIR}/white'
DARK_CHART_DIR = f'{ARTICLE_DIR}/dark'
OUTPUT_PDF = f'{ARTICLE_DIR}/Prices The Transmission Belt.pdf'

PAGE_W, PAGE_H = letter
CONTENT_W = PAGE_W - 0.6 * inch  # 0.3" margins each side


def create_header_footer(canvas, doc):
    """Exact match of Two Books PDF header/footer."""
    canvas.saveState()

    # Header bar — full width, Ocean 70% + Dusk 30%
    canvas.setFillColor(OCEAN_BLUE)
    canvas.rect(0, PAGE_H - 0.4 * inch, PAGE_W * 0.7, 0.4 * inch, fill=1, stroke=0)
    canvas.setFillColor(DUSK_ORANGE)
    canvas.rect(PAGE_W * 0.7, PAGE_H - 0.4 * inch, PAGE_W * 0.3, 0.4 * inch, fill=1, stroke=0)

    # Header text — white on colored bar
    canvas.setFillColor(WHITE)
    canvas.setFont('Helvetica-Bold', 10)
    canvas.drawString(0.3 * inch, PAGE_H - 0.28 * inch, "LIGHTHOUSE MACRO")
    canvas.drawRightString(PAGE_W - 0.3 * inch, PAGE_H - 0.28 * inch, "Prices: The Transmission Belt")

    # Footer text
    canvas.setFillColor(DARK_GRAY)
    canvas.setFont('Helvetica', 8)
    canvas.drawString(0.3 * inch, 0.35 * inch, f"Generated: {datetime.now().strftime('%Y-%m-%d')}")
    canvas.drawCentredString(PAGE_W / 2, 0.35 * inch, "MACRO, ILLUMINATED.")
    canvas.drawRightString(PAGE_W - 0.3 * inch, 0.35 * inch, f"Page {doc.page}")

    # Footer accent bar
    canvas.setFillColor(OCEAN_BLUE)
    canvas.rect(0, 0.25 * inch, PAGE_W * 0.7, 0.05 * inch, fill=1, stroke=0)
    canvas.setFillColor(DUSK_ORANGE)
    canvas.rect(PAGE_W * 0.7, 0.25 * inch, PAGE_W * 0.3, 0.05 * inch, fill=1, stroke=0)

    canvas.restoreState()


# ============================================
# STYLES (matches Two Books PDF)
# ============================================
_base = getSampleStyleSheet()

title_style = ParagraphStyle(
    'LHMTitle',
    parent=_base['Heading1'],
    fontSize=28,
    textColor=OCEAN_BLUE,
    spaceAfter=6,
    alignment=TA_CENTER,
    fontName='Helvetica-Bold',
)

subtitle_style = ParagraphStyle(
    'LHMSubtitle',
    parent=_base['Normal'],
    fontSize=14,
    textColor=DARK_GRAY,
    spaceAfter=20,
    alignment=TA_CENTER,
    fontName='Helvetica',
)

h1_style = ParagraphStyle(
    'LHMH1',
    parent=_base['Heading1'],
    fontSize=18,
    textColor=OCEAN_BLUE,
    spaceBefore=20,
    spaceAfter=12,
    fontName='Helvetica-Bold',
)

h2_style = ParagraphStyle(
    'LHMH2',
    parent=_base['Heading2'],
    fontSize=14,
    textColor=OCEAN_BLUE,
    spaceBefore=16,
    spaceAfter=8,
    fontName='Helvetica-Bold',
)

body_style = ParagraphStyle(
    'LHMBody',
    parent=_base['Normal'],
    fontSize=10,
    textColor=DARK_GRAY,
    spaceAfter=8,
    alignment=TA_JUSTIFY,
    fontName='Helvetica',
    leading=14,
)

italic_style = ParagraphStyle(
    'LHMItalic',
    parent=body_style,
    fontName='Helvetica-Oblique',
    textColor=OCEAN_BLUE,
)

bullet_style = ParagraphStyle(
    'LHMBullet',
    parent=body_style,
    leftIndent=20,
    bulletIndent=10,
    spaceAfter=4,
)

caption_style = ParagraphStyle(
    'LHMCaption',
    parent=_base['Normal'],
    fontName='Helvetica-Oblique',
    fontSize=9,
    leading=12,
    textColor=MUTED_GRAY,
    alignment=TA_CENTER,
    spaceAfter=12,
)

footer_style = ParagraphStyle(
    'LHMFooter',
    parent=_base['Normal'],
    fontName='Helvetica',
    fontSize=8,
    leading=11,
    textColor=MUTED_GRAY,
    alignment=TA_CENTER,
)

section_label_style = ParagraphStyle(
    'LHMSectionLabel',
    parent=_base['Normal'],
    fontName='Helvetica-Bold',
    fontSize=10,
    leading=13,
    textColor=OCEAN_BLUE,
    spaceAfter=4,
)


def lhm_table(data, col_widths):
    """Create a table with the standard LHM style (Ocean header, Ocean grid)."""
    t = Table(data, colWidths=col_widths)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), OCEAN_BLUE),
        ('TEXTCOLOR', (0, 0), (-1, 0), WHITE),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, OCEAN_BLUE),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
    ]))
    return t


def get_chart_path(filename):
    """Get chart path, preferring white theme."""
    white_path = os.path.join(CHART_DIR, filename)
    dark_path = os.path.join(DARK_CHART_DIR, filename)
    if os.path.exists(white_path):
        return white_path
    elif os.path.exists(dark_path):
        return dark_path
    return None


def add_chart(story, filename, caption_text):
    """Add a chart image with caption."""
    path = get_chart_path(filename)
    if path is None:
        story.append(Paragraph(f'[Chart missing: {filename}]', italic_style))
        return

    img = PILImage.open(path)
    aspect = img.height / img.width
    img_w = CONTENT_W
    img_h = img_w * aspect

    max_h = 4.2 * inch
    if img_h > max_h:
        img_h = max_h
        img_w = img_h / aspect

    chart_img = Image(path, width=img_w, height=img_h)
    chart_img.hAlign = 'CENTER'

    story.append(Spacer(1, 6))
    story.append(chart_img)
    story.append(Spacer(1, 4))
    story.append(Paragraph(caption_text, caption_style))


def build_pdf():
    """Build the full branded PDF matching Two Books style."""

    doc = SimpleDocTemplate(
        OUTPUT_PDF,
        pagesize=letter,
        rightMargin=0.3 * inch,
        leftMargin=0.3 * inch,
        topMargin=0.55 * inch,
        bottomMargin=0.5 * inch,
    )

    story = []

    # ==========================================
    # TITLE PAGE
    # ==========================================
    story.append(Spacer(1, 1.5 * inch))
    story.append(Paragraph("PRICES: THE TRANSMISSION BELT", title_style))
    story.append(Spacer(1, 0.3 * inch))

    # Accent bar
    accent = Table([['']], colWidths=[4 * inch])
    accent.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), OCEAN_BLUE),
        ('LINEBELOW', (0, 0), (0, 0), 4, DUSK_ORANGE),
    ]))
    story.append(accent)

    story.append(Spacer(1, 0.3 * inch))
    story.append(Paragraph("The Diagnostic Dozen: A Framework for Reading the Macro Cycle (2 of 12)", subtitle_style))
    story.append(Spacer(1, 0.3 * inch))
    story.append(Paragraph(
        '<i>"The headline is improving. The details are stuck.<br/>'
        'This is the last mile problem."</i>',
        italic_style
    ))
    story.append(Spacer(1, 0.8 * inch))
    story.append(Paragraph("Lighthouse Macro", subtitle_style))
    story.append(Paragraph("Pillar 2 of 12 | The Diagnostic Dozen", subtitle_style))
    story.append(Spacer(1, 0.5 * inch))
    story.append(Paragraph(
        "Bob Sheehan, CFA, CMT<br/>Founder &amp; Chief Investment Officer",
        body_style
    ))

    story.append(PageBreak())

    # ==========================================
    # OPENING HOOK
    # ==========================================
    hook_style = ParagraphStyle(
        'Hook', parent=body_style, fontSize=12,
        fontName='Helvetica-Oblique', spaceAfter=10, leading=17
    )
    story.append(Paragraph("Inflation doesn't negotiate.", hook_style))
    story.append(Paragraph(
        "GDP can disappoint and the Fed shrugs. Employment can soften and they wait for confirmation. "
        "But if inflation stays elevated, the Fed stays restrictive. There is no discretion here. "
        "Inflation is the only macro variable that directly controls the policy rate, and the policy rate "
        "controls everything else.",
        body_style
    ))
    story.append(Paragraph(
        "This asymmetry makes prices different from every other pillar in our framework. Labor drives "
        "consumer dynamics. Growth dictates corporate earnings. But inflation dictates policy, and policy "
        "dictates everything else.",
        body_style
    ))
    story.append(Paragraph(
        "Right now, headline CPI sits at 2.7%. Mission accomplished, right?",
        body_style
    ))
    story.append(Paragraph(
        "Not so fast. That number isn't even what the Fed targets. The Fed watches Core PCE, which sits "
        "at 2.8%. And underneath the surface:",
        body_style
    ))

    for b in [
        "Core services inflation is running at 3.0%, more than double the rate of core goods at 1.4%",
        "Sticky CPI is at 3.0%, 1.5x the target, and barely budging",
        "Shelter, 34% of the CPI basket, is still mechanically unwinding from its 2023 peak",
        "The Dallas Fed Trimmed Mean, which strips outlier noise, confirms the stickiness is broad-based",
    ]:
        story.append(Paragraph(f'\u2022 {b}', bullet_style))

    story.append(Spacer(1, 6))
    story.append(Paragraph(
        'The headline is improving. The details are stuck. This is the "last mile" problem, '
        "and it's why the Fed remains boxed in.",
        body_style
    ))

    story.append(CondPageBreak(3.5 * inch))

    # ==========================================
    # THE CORE INSIGHT: COMPOSITION OVER LEVEL
    # ==========================================
    story.append(Paragraph('THE CORE INSIGHT: COMPOSITION OVER LEVEL', h1_style))
    story.append(Paragraph(
        "When CPI prints at 2.7%, the market sees a number. The Fed sees 300 components, each with "
        "different speeds, different drivers, and different implications for policy.",
        body_style
    ))
    story.append(Paragraph(
        "Headline inflation is a weighted average of three fundamentally different economies:",
        body_style
    ))
    story.append(Paragraph(
        "<b>Goods</b> are globally traded, supply-chain responsive, and deflationary post-pandemic. "
        "When goods deflate, it's fast. Excess inventory gets cleared. Supply chains normalize. "
        "Import prices compress. The transmission is mechanical and predictable.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Services</b> are locally produced, wage-driven, and structurally sticky. You can't offshore "
        "a haircut. You can't import a doctor. Labor costs are 60-70% of service sector expenses, and "
        "wages don't deflate without unemployment rising substantially. The only way to break services "
        "inflation is to break the labor market.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Shelter</b> is the lagging anchor. Measured via lease renewals and owners' equivalent rent, "
        "it represents 34% of the CPI basket but operates on a 12-18 month lag. Market rents peaked at "
        "+16% in February 2022. CPI shelter didn't peak until March 2023, thirteen months later.",
        body_style
    ))
    story.append(Paragraph(
        "A uniform 2.7% inflation environment is structurally different from +1.4% goods + 3.0% services "
        "= 2.7% average. The first is symmetric disinflation. The second is bifurcation with a structural "
        "wage floor preventing the last mile. Fed policy responds to composition, not averages.",
        body_style
    ))
    story.append(Paragraph(
        "We validated this against every inflation cycle since 1980. The pattern repeats: goods are the "
        "shock absorber, services are the structural floor, shelter is the lagging confirmation. In 1990, "
        "goods fell first. Services persisted for 18 months longer. In 2008, goods deflated violently "
        "while services stayed positive until unemployment hit 10%. In 2021-2023, goods peaked 13 months "
        "before services. The sequence is consistent. Composition tells you where you're going. The "
        "headline tells you where you've been.",
        body_style
    ))

    story.append(CondPageBreak(3.5 * inch))

    # ==========================================
    # SECTION 1: The Great Divergence
    # ==========================================
    story.append(Paragraph('THE GREAT DIVERGENCE', h1_style))
    story.append(Paragraph(
        'The single most important chart in inflation right now is the split between goods and services.',
        body_style
    ))

    add_chart(story, 'chart_01_goods_vs_services.png',
              'Figure 1: Core goods CPI vs. core services CPI. The divergence is the defining feature of the current inflation regime.')

    story.append(Paragraph(
        "Core goods peaked at +12.3% in February 2022 and have fallen to +1.4%. That's a 10.9 percentage "
        "point decline. Goods disinflation is largely complete. Supply chains healed. Inventories rebuilt. "
        "China exported deflation. The strong dollar made imports cheaper. Goods are barely positive and "
        "no longer contributing to headline pressure.",
        body_style
    ))
    story.append(Paragraph(
        "Core services peaked at +7.2% in March 2023 and sit at +3.0%. That's a 4.2 percentage point "
        "decline, but most of the improvement came from shelter unwinding. Services ex-shelter remains elevated.",
        body_style
    ))
    story.append(Paragraph(
        "The current goods-services spread is approximately 1.6 percentage points. At its peak in early "
        "2023, the spread exceeded 10 points, the widest divergence on record. It has narrowed substantially "
        "as goods normalized and services decelerated. But the spread is still positive, meaning services "
        "continue to run hotter than goods. Historical normalization happens either through goods re-inflating "
        "(tariffs, dollar weakness) or services decelerating (recession, labor market cracking). The direction "
        "of convergence is the macro call.",
        body_style
    ))

    story.append(CondPageBreak(3.5 * inch))

    # ==========================================
    # SECTION 2: The Gap That Matters
    # ==========================================
    story.append(Paragraph('THE GAP THAT MATTERS', h1_style))
    story.append(Paragraph(
        "Here's the distinction that separates informed analysis from headlines: "
        "the Fed doesn't target CPI. It targets Core PCE.",
        body_style
    ))

    add_chart(story, 'chart_02_headline_vs_core.png',
              "Figure 2: Headline CPI vs. Core PCE. The Fed watches Core PCE, and it's still meaningfully above target.")

    story.append(Paragraph(
        "CPI and PCE measure different things, and the difference matters mechanically. CPI uses fixed "
        "weights based on what people bought last year. PCE uses chain-weighted spending based on what "
        "people are buying now. PCE also captures a broader set of expenditures, including employer-provided "
        "healthcare (17% of PCE vs. 7% of CPI for out-of-pocket only).",
        body_style
    ))
    story.append(Paragraph(
        "The practical result: PCE tends to run 0.3-0.5 percentage points below CPI because it accounts "
        "for substitution effects. When beef gets expensive, people buy chicken. CPI misses that. PCE "
        "captures it.",
        body_style
    ))
    story.append(Paragraph(
        "Shelter is 34% of CPI but only 18% of PCE. This means CPI overstates the shelter problem relative "
        "to what the Fed actually watches. When shelter normalizes, CPI will drop faster than PCE, and the "
        'gap between "headline victory" and "Fed reality" will temporarily widen.',
        body_style
    ))
    story.append(Paragraph(
        'Core PCE at 2.8% is still 40% above the 2% goal. That\'s not "close to target." That\'s '
        "meaningfully elevated for a central bank that spent the last 30 months above 2.5% and hasn't "
        "seen a sustained return to target since early 2021.",
        body_style
    ))

    story.append(CondPageBreak(3.5 * inch))

    # ==========================================
    # SECTION 3: The Shelter Lag Trap
    # ==========================================
    story.append(Paragraph('THE SHELTER LAG TRAP', h1_style))
    story.append(Paragraph(
        "Shelter is 34% of the CPI basket. It's the single largest component. "
        "And it operates on a mechanical lag that distorts the headline number in both directions.",
        body_style
    ))

    add_chart(story, 'chart_03_shelter_lag.png',
              "Figure 3: Shelter CPI, Rent of Primary Residence, and Owners' Equivalent Rent. All three are declining but remain above target.")

    story.append(Paragraph(
        "Here's how the lag works. The BLS measures shelter through surveys of existing leases. "
        "When market rents spike (as they did in 2021-2022), it takes 12-18 months for those increases "
        "to flow through the lease renewal cycle into CPI. The same works in reverse.",
        body_style
    ))

    # Shelter lag table
    shelter_data = [
        ['Market Rent Peak/Trough', 'CPI Shelter Peak/Trough', 'Lag'],
        ['Feb 2022 (+16.0% peak)', 'Mar 2023 (+8.2% peak)', '13 months'],
        ['Jun 2020 (-1.2% trough)', 'Jun 2021 (+1.9% trough)', '12 months'],
        ['Jan 2019 (+3.2% local peak)', 'Feb 2020 (+3.8% local peak)', '13 months'],
    ]
    story.append(KeepTogether([
        lhm_table(shelter_data, [2.4 * inch, 2.4 * inch, 1.4 * inch]),
        Spacer(1, 6),
        Paragraph(
            "Average lag: 12.7 months. Range: 10-14 months.",
            body_style
        ),
    ]))
    story.append(Paragraph(
        "Market rents have decelerated to approximately +2.4% year-over-year. Applying the 12-month lag, "
        "CPI shelter should approach 3.0% by mid-2026. This is arithmetic, not a forecast. The decline is baked in.",
        body_style
    ))
    story.append(KeepTogether([
        Paragraph(
            "The contribution math: shelter at 3.2% with 34% CPI weight contributes 1.09 percentage points "
            "to headline. As it continues declining toward 3.0%, the remaining mechanical disinflation is "
            "modest, perhaps 0.07 points. The big shelter unwind is mostly behind us. That's actually the "
            "problem: the easy shelter-driven disinflation is fading, and what's left is the hard part.",
            body_style
        ),
        Paragraph(
            "The bad news: even after shelter normalizes, services ex-shelter remains sticky. "
            "Shelter was masking the problem, not causing it. The goal post moves. When shelter finally "
            "cooperates in Q2-Q3 2026, the Fed will be watching supercore (services ex-shelter), and "
            "supercore is still elevated.",
            body_style
        ),
    ]))

    story.append(CondPageBreak(3.5 * inch))

    # ==========================================
    # SECTION 4: The Persistence Problem
    # ==========================================
    story.append(Paragraph('THE PERSISTENCE PROBLEM', h1_style))
    story.append(Paragraph(
        "The Atlanta Fed decomposes CPI into two categories that reveal the structural nature of current inflation.",
        body_style
    ))

    add_chart(story, 'chart_04_sticky_vs_flexible.png',
              'Figure 4: Sticky CPI vs. Flexible CPI (shifted 12 months). Flexible inflation leads Sticky by roughly 12 months.')

    story.append(Paragraph(
        '<b>Flexible CPI</b> includes items with prices that change frequently: gasoline, food, airfares. '
        "These respond quickly to supply and demand. Flexible CPI has normalized. Mission accomplished on "
        "the transitory components.",
        body_style
    ))
    story.append(Paragraph(
        '<b>Sticky CPI</b> includes items where prices change infrequently: rent, insurance, medical care, '
        "education. These embed expectations and wage costs. They're slow to rise and slow to fall.",
        body_style
    ))
    story.append(Paragraph(
        "We tested sticky CPI as a predictor of core CPI six months forward. The results are clear:",
        body_style
    ))
    for b in [
        "Sticky CPI predicts future core with an R-squared of 0.82 (1980-2025)",
        "Flexible CPI predicts future core with an R-squared of 0.37",
        "Sticky CPI has 2.3x the predictive power of flexible CPI",
    ]:
        story.append(Paragraph(f'\u2022 {b}', bullet_style))

    story.append(Spacer(1, 4))
    story.append(Paragraph(
        "Sticky CPI at 3.0% is 1.5x the 2% target. The chart shows flexible inflation shifted forward "
        "12 months to reveal the lead relationship. What happens in flexible prices today flows into "
        "sticky prices roughly a year later. The correlation is striking when the lag is accounted for.",
        body_style
    ))
    story.append(Paragraph(
        "This is why we track persistence. Headline disinflation is mostly a flexible-price story. "
        "The structural floor, set by sticky prices, hasn't broken. Historically, sticky CPI has never "
        "broken below 3.0% without a recession. Until it moves decisively toward 2%, the last mile "
        "remains incomplete.",
        body_style
    ))

    story.append(CondPageBreak(3.5 * inch))

    # ==========================================
    # SECTION 5: The Pipeline
    # ==========================================
    story.append(Paragraph('THE PIPELINE: PPI LEADS CPI', h1_style))
    story.append(Paragraph(
        "Producer prices are the upstream signal. What manufacturers and service providers pay "
        "eventually passes through to consumers.",
        body_style
    ))

    add_chart(story, 'chart_05_ppi_leads_cpi.png',
              'Figure 5: PPI Final Demand vs. CPI. Producer prices lead consumer prices by 3-6 months.')

    story.append(Paragraph(
        "We tested the lead-lag relationship formally. PPI Granger-causes CPI with high statistical "
        "significance across multiple lags (p&lt;0.001 at lag 3-4 months). The reverse relationship also "
        "shows statistical significance, consistent with the feedback loop between producer and consumer "
        "prices, but the economic mechanism flows primarily upstream to downstream.",
        body_style
    ))
    story.append(Paragraph(
        "When PPI runs below CPI, producers are absorbing cost declines that haven't yet reached consumers. "
        "That's disinflationary pressure building in the pipeline. When PPI runs above CPI, inflationary "
        "pressure is coming.",
        body_style
    ))
    story.append(Paragraph(
        "Current PPI at 3.0% sits modestly above CPI at 2.7%. The spread suggests modest inflationary "
        "pressure still in the pipeline over the next 3-6 months, reinforcing the sticky services floor.",
        body_style
    ))

    story.append(CondPageBreak(3.5 * inch))

    # ==========================================
    # SECTION 6: Expectations
    # ==========================================
    story.append(Paragraph('INFLATION EXPECTATIONS: ARE THEY ANCHORED?', h1_style))
    story.append(Paragraph(
        "Inflation expectations are arguably more important than inflation itself. If businesses and "
        "consumers expect inflation to remain elevated, they price accordingly. Wages get negotiated higher. "
        "Prices get set higher. Expectations become self-fulfilling.",
        body_style
    ))

    add_chart(story, 'chart_06_expectations.png',
              'Figure 6: The 5-Year, 5-Year Forward Inflation Rate vs. University of Michigan 1-Year Consumer Expectations.')

    story.append(Paragraph("Two measures tell very different stories:", body_style))
    story.append(Paragraph(
        "<b>5Y5Y Forward</b> (bond market expectations) sits at 2.19%. This is the market's view of where "
        "inflation will be 5-10 years from now. It's drifting slightly above the 2% anchor. Professional "
        "investors aren't panicking, but they're repricing.",
        body_style
    ))
    story.append(Paragraph(
        '<b>UMich 1Y Expectations</b> (consumer expectations) are elevated. Consumers still <i>feel</i> '
        "inflation. Grocery bills, insurance premiums, rent: these are the prices people interact with daily. "
        "They don't care that goods are barely inflating if their rent is up 5%.",
        body_style
    ))
    story.append(Paragraph(
        "The risk: if 5Y5Y breaks above 2.5%, the Fed gets nervous. If it breaks 3.0%, the Fed loses the "
        "expectations anchor entirely. That would force aggressive tightening regardless of growth conditions. "
        "For now, it's drifting, not de-anchored. But it bears watching closely.",
        body_style
    ))

    story.append(CondPageBreak(3.5 * inch))

    # ==========================================
    # SECTION 7: Trimmed Mean
    # ==========================================
    story.append(Paragraph('THE SIGNAL BENEATH THE NOISE', h1_style))
    story.append(Paragraph(
        "The Dallas Fed Trimmed Mean PCE strips the most extreme price changes each month, "
        "both high and low, to reveal the underlying trend.",
        body_style
    ))

    add_chart(story, 'chart_07_trimmed_mean.png',
              'Figure 7: Dallas Fed Trimmed Mean PCE vs. Core PCE. The trimmed mean strips outlier noise and confirms the underlying trend.')

    story.append(Paragraph(
        "Why does this matter? Because headline measures get distorted by outliers, and those distortions "
        "mislead. We tested forecast accuracy across the full 2005-2024 sample: the trimmed mean produced "
        "38% lower RMSE than headline CPI at predicting core PCE twelve months forward. Even over the "
        "volatile 2021-2023 subperiod, the trimmed mean outperformed headline CPI by 16%.",
        body_style
    ))
    story.append(Paragraph(
        "The trimmed mean avoids distortions from outliers like motor vehicle insurance, which surged "
        "14%+ as insurers repriced for higher replacement costs. Because auto insurance is roughly 3% of "
        "CPI, it alone contributes about 0.4 percentage points to headline. When it normalizes, that's "
        "free disinflation that says nothing about underlying pressure.",
        body_style
    ))
    story.append(Paragraph(
        "At 2.8%, the trimmed mean confirms the same story as sticky CPI: the underlying inflation trend "
        "is above target, and the stickiness is broad-based, not driven by one or two categories.",
        body_style
    ))

    story.append(CondPageBreak(3.5 * inch))

    # ==========================================
    # SECTION 8: Wages vs Prices
    # ==========================================
    story.append(Paragraph('THE SPIRAL CHECK', h1_style))
    story.append(Paragraph(
        "The wage-price spiral is the inflation scenario that keeps central bankers awake. Workers demand "
        "higher wages because prices are rising. Businesses raise prices to cover higher labor costs. Repeat.",
        body_style
    ))

    add_chart(story, 'chart_08_wages_vs_prices.png',
              'Figure 8: ECI Total Compensation vs. Core PCE. Wages above inflation means positive real wages but sticky services.')

    story.append(Paragraph(
        "The Employment Cost Index is the gold standard for measuring labor cost pressure because it "
        "controls for compositional shifts. Average Hourly Earnings can fall just because the economy is "
        "adding more low-wage jobs. That looks like wage disinflation but it's actually just mix shift. "
        "ECI holds the job mix constant. If ECI is elevated, wage pressure is real.",
        body_style
    ))
    story.append(Paragraph(
        "ECI Total Compensation is running at 3.5%, above Core PCE at 2.8%. That's positive real wages, "
        "which is good for workers and consumers. But it's also the reason services inflation won't come down "
        "easily. Labor costs are the largest input for most service businesses.",
        body_style
    ))
    story.append(Paragraph(
        "The math: unit labor costs equal compensation growth minus productivity growth. At 3.5% "
        "compensation and 1.5% productivity, ULC runs at roughly 2.0%. That's consistent with services "
        "inflation in the 2.5-3.0% range. Not crisis. Not target. Stuck.",
        body_style
    ))
    story.append(Paragraph(
        "The good news: there's no spiral. Wages aren't accelerating. They're decelerating from their "
        "2022 peak. The bad news: wages above inflation is an equilibrium that sustains services inflation "
        "above target. It's stable, but it's stable at the wrong level.",
        body_style
    ))
    story.append(Paragraph(
        "From our labor framework (Pillar 1): the Labor Fragility Index is elevated and quits have fallen "
        "to the 2.0% threshold. If labor continues to soften, wage growth will decelerate further, and "
        "that deceleration will flow into services inflation with a 6-9 month lag. The labor pillar and "
        "the prices pillar are connected through this wage channel.",
        body_style
    ))

    story.append(CondPageBreak(3.5 * inch))

    # ==========================================
    # SECTION 9: Dollar Channel
    # ==========================================
    story.append(Paragraph('THE DOLLAR CHANNEL', h1_style))
    story.append(Paragraph(
        "The trade-weighted dollar is the mechanism behind goods price suppression.",
        body_style
    ))

    add_chart(story, 'chart_09_dollar_goods.png',
              'Figure 9: Trade-weighted dollar (inverted) vs. Core Goods CPI, shifted 18 months to show the lead relationship.')

    story.append(Paragraph(
        "A strong dollar makes imports cheaper. Since the US imports a massive share of its goods consumption, "
        "dollar strength flows directly into goods prices with a 9-18 month lag. A 10% dollar appreciation "
        "typically results in 1.0-1.5 percentage points of reduction in goods CPI over 12-18 months. The "
        "near-zero goods inflation isn't a mystery. It's the mechanical result of prior dollar strength.",
        body_style
    ))
    story.append(Paragraph(
        "The implication cuts both ways. If the dollar weakens (which it would in a rate-cutting cycle), "
        "goods inflation reaccelerates. That removes the one force currently keeping goods from contributing "
        "to headline pressure. The Fed's own easing could reignite goods inflation, creating a feedback loop "
        "that constrains how aggressively they can cut.",
        body_style
    ))
    story.append(Paragraph(
        "There's also a tariff channel. Tariffs are a direct tax on imports that transmits to consumer "
        "prices with a 3-9 month lag. A broad 10% tariff on Chinese imports could add 0.3-0.5 percentage "
        "points to headline CPI over 6-12 months. Tariff inflation is supply-side, so the Fed faces an "
        "impossible choice: hike to fight it (causing unnecessary demand destruction) or ignore it (risking "
        "expectations de-anchoring).",
        body_style
    ))

    story.append(CondPageBreak(3.5 * inch))

    # ==========================================
    # SECTION 10: PCI Composite
    # ==========================================
    story.append(Paragraph('PUTTING IT ALL TOGETHER: THE PRICES COMPOSITE', h1_style))
    story.append(Paragraph(
        "We synthesize the key inflation signals into a composite we call the Prices Composite Index (PCI):",
        body_style
    ))

    add_chart(story, 'chart_10_pci_composite.png',
              'Figure 10: The Prices Composite Index (PCI). Regime bands show the inflation environment.')

    story.append(Paragraph(
        'The PCI combines six components, each z-scored over a rolling 60-month window:',
        body_style
    ))
    for c in [
        "<b>Core PCE momentum</b> (3-month annualized): The Fed's primary target, highest weight",
        "<b>Services inflation trend</b>: Wage-driven persistence, the supercore signal",
        "<b>Shelter trajectory</b>: Largest single CPI component, lagging but mechanical",
        "<b>Sticky price persistence</b>: Atlanta Fed decomposition, predicts future core",
        "<b>Expectations anchoring</b> (5Y5Y forward): The credibility gauge",
        "<b>Goods price level</b> (inverted): Disinflationary force when negative, fading",
    ]:
        story.append(Paragraph(f'\u2022 {c}', bullet_style))

    story.append(Spacer(1, 8))
    regime_data = [
        ['PCI Range', 'Regime', 'Interpretation'],
        ['> +1.5', 'Crisis', 'Inflation emergency, Fed forced to act'],
        ['+1.0 to +1.5', 'High', 'Aggressive restraint, no cuts possible'],
        ['+0.5 to +1.0', 'Elevated', "Fed can't ease aggressively"],
        ['-0.5 to +0.5', 'On Target', 'Policy flexibility restored'],
        ['< -0.5', 'Deflationary', 'Easing urgently needed'],
    ]
    story.append(KeepTogether([
        Paragraph('Regime Bands', h2_style),
        lhm_table(regime_data, [1.5 * inch, 1.5 * inch, 3.2 * inch]),
    ]))

    story.append(Spacer(1, 8))
    story.append(Paragraph(
        "We calibrated the PCI against every inflation regime since 2004. At -0.2 in December 2019 "
        "(on target, stable 2% PCE). At +2.4 in June 2022 (peak crisis, CPI 9.1%). At +0.9 in "
        "December 2023 (elevated, disinflation underway). The composite tracked regime shifts in "
        "real-time and correctly identified the \"still elevated\" condition that kept the Fed on hold "
        "through late 2024.",
        body_style
    ))
    story.append(Paragraph(
        "The specific weights are proprietary, but the signal is clear: when multiple inflation "
        "indicators remain elevated simultaneously, the composite stays in restrictive territory, "
        "and the Fed stays boxed in.",
        body_style
    ))

    story.append(CondPageBreak(3.5 * inch))

    # ==========================================
    # WHERE WE ARE NOW
    # ==========================================
    story.append(Paragraph("WHERE WE ARE NOW", h1_style))

    story.append(Paragraph('<b>The headline is improving:</b>', body_style))
    for b in [
        "CPI at 2.7%, down from 9.1% peak",
        "Core goods at +1.4%, near flat",
        "Shelter mechanically declining",
        "Core PCE 3M annualized at 2.3%, trending in the right direction",
    ]:
        story.append(Paragraph(f'\u2022 {b}', bullet_style))

    story.append(Spacer(1, 6))
    story.append(Paragraph('<b>The details are stuck:</b>', body_style))
    for b in [
        "Core PCE at 2.8%, still 40% above target",
        "Core services at 3.0%, barely budging",
        "Sticky CPI at 3.0%, 1.5x the target",
        "Trimmed Mean at 2.8%, confirming breadth",
        "ECI at 3.5%, wages above inflation sustaining services stickiness",
        "PPI at 3.0%, above CPI, suggesting pipeline pressure ahead",
    ]:
        story.append(Paragraph(f'\u2022 {b}', bullet_style))

    story.append(Spacer(1, 6))
    story.append(Paragraph('<b>The cross-pillar picture:</b>', body_style))
    for b in [
        "Labor fragility is elevated (Pillar 1), suggesting wage pressure will eventually fade, but with a 6-9 month lag into services",
        "Liquidity cushion is thin (Pillar 10), limiting the Fed's ability to ease even if inflation cooperates",
        "Growth is softening (Pillar 3), creating disinflationary pressure, but the lag chain from growth weakness to services disinflation runs 9-12 months",
    ]:
        story.append(Paragraph(f'\u2022 {b}', bullet_style))

    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "This is the bifurcated reality. Goods are solved. Services are stuck. The last mile isn't a distance "
        "problem. It's a composition problem. And composition problems don't respond to time alone.",
        body_style
    ))

    story.append(CondPageBreak(3.5 * inch))

    # ==========================================
    # THE CONSENSUS TRAP
    # ==========================================
    story.append(Paragraph('THE CONSENSUS TRAP', h1_style))
    story.append(Paragraph(
        "Here's the pattern that repeats every cycle.",
        body_style
    ))
    story.append(Paragraph(
        '<b>Surface narrative:</b> "Inflation is beaten. Headline CPI is at 2.7%, down from 9.1%. '
        'The Fed can start cutting aggressively. Soft landing achieved."',
        body_style
    ))
    story.append(Paragraph(
        "<b>What's actually happening:</b> Goods barely positive at +1.4% (no longer pulling headline "
        "lower). Services still at +3.0% (wage floor intact). Sticky CPI at +3.0% (1.5x the target). "
        "Shelter declining but still above target. The easy disinflation is done.",
        body_style
    ))
    story.append(Paragraph("Consensus gets trapped by three biases:", body_style))
    story.append(Paragraph(
        "<b>Recency bias.</b> Inflation fell from 9.1% to 2.7% in roughly two years. Extrapolating that "
        "pace suggests sub-2% soon. But the easy part is done. Goods disinflation is complete and can't "
        "contribute further. The last mile is services, and services don't deflate without labor market "
        "deterioration.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Headline focus.</b> Media covers headline CPI. Markets trade headline CPI. The Fed watches "
        "core PCE. When headline and core diverge, consensus misses the Fed's constraint.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Lag misunderstanding.</b> As shelter continues to normalize, headline will look better. But "
        "the market will be watching services ex-shelter, which remains elevated. The goal post moves.",
        body_style
    ))
    story.append(Paragraph(
        "This happened in 2018-2019. Headline CPI fell from 2.9% to 1.8%. Consensus expected aggressive "
        "cuts. The Fed cut only 75 bps. Core PCE stayed at 1.6-1.8% (on target). The current setup is "
        "structurally different: core PCE at 2.8% (vs 1.8% then), sticky CPI at 3.0% (vs 2.8%). The Fed "
        "has less room to cut now than in 2019 despite similar headline prints.",
        body_style
    ))
    story.append(Paragraph(
        "The market is pricing 100-125 basis points of cuts in 2026. The inflation data, read through "
        "composition rather than headline, says 0-50 basis points unless something breaks. When the market "
        "figures this out, real yields stay elevated, growth assets reprice, and the \"soft landing\" narrative "
        "gets tested.",
        body_style
    ))

    story.append(CondPageBreak(3.5 * inch))

    # ==========================================
    # WHAT TO WATCH
    # ==========================================
    story.append(Paragraph('WHAT TO WATCH', h1_style))
    story.append(Paragraph(
        "If you want to track the inflation picture yourself, here's a practical watchlist "
        "organized by what it tells you:",
        body_style
    ))

    # Core Trend
    story.append(KeepTogether([
        Paragraph('Core Trend (Fed Reaction Function)', h2_style),
        lhm_table(
            [
                ['Indicator', 'Source', 'Frequency', 'Watch For'],
                ['Core PCE YoY', 'FRED: PCEPILFE', 'Monthly', 'Sustained move below 2.5%'],
                ['Core PCE 3M Ann.', 'Derived', 'Monthly', 'Direction more than level'],
                ['Trimmed Mean PCE', 'FRED: PCETRIM12M...', 'Monthly', 'Convergence toward 2%'],
                ['Sticky CPI', 'Atlanta Fed', 'Monthly', 'Break below 3.0%'],
            ],
            [1.5 * inch, 1.6 * inch, 0.9 * inch, 2.2 * inch]
        ),
    ]))
    story.append(Spacer(1, 10))

    # Components
    story.append(KeepTogether([
        Paragraph('Components (Where the Pressure Lives)', h2_style),
        lhm_table(
            [
                ['Indicator', 'Source', 'Frequency', 'Watch For'],
                ['Shelter CPI', 'FRED: CUSR0000SAH1', 'Monthly', 'Decline toward 3%'],
                ['Services ex-Shelter', 'BLS', 'Monthly', 'Below 3.0% = victory'],
                ['Core Goods CPI', 'FRED: CUSR...SACL1E', 'Monthly', 'Above 2% (tariffs, dollar)'],
            ],
            [1.5 * inch, 1.6 * inch, 0.9 * inch, 2.2 * inch]
        ),
    ]))
    story.append(Spacer(1, 10))

    # Expectations
    story.append(KeepTogether([
        Paragraph('Expectations (The Credibility Anchor)', h2_style),
        lhm_table(
            [
                ['Indicator', 'Source', 'Frequency', 'Watch For'],
                ['5Y5Y Forward', 'FRED: T5YIFR', 'Daily', '>2.5% caution, >3.0% alarm'],
                ['UMich 1Y', 'Univ. of Michigan', 'Monthly', 'Extreme readings (>4% or <2%)'],
            ],
            [1.5 * inch, 1.6 * inch, 0.9 * inch, 2.2 * inch]
        ),
    ]))
    story.append(Spacer(1, 10))

    # Pipeline
    story.append(KeepTogether([
        Paragraph('Pipeline (What\'s Coming)', h2_style),
        lhm_table(
            [
                ['Indicator', 'Source', 'Frequency', 'Watch For'],
                ['PPI Final Demand', 'FRED: PPIFIS', 'Monthly', 'PPI above CPI = inflationary'],
                ['ECI Total Comp', 'FRED: ECIALLCIV', 'Quarterly', 'Below 3.0% = services relief'],
            ],
            [1.5 * inch, 1.6 * inch, 0.9 * inch, 2.2 * inch]
        ),
    ]))

    story.append(Spacer(1, 8))
    story.append(Paragraph(
        "The signal isn't any single indicator. It's the composition. When services moderate, sticky prices "
        "break lower, and expectations re-anchor simultaneously, that's when the last mile is complete.",
        body_style
    ))

    story.append(CondPageBreak(3.5 * inch))

    # ==========================================
    # INVALIDATION CRITERIA
    # ==========================================
    story.append(Paragraph('INVALIDATION CRITERIA', h1_style))
    story.append(Paragraph(
        "Strong views, weakly held. Here's what would change the thesis.",
        body_style
    ))

    story.append(Paragraph(
        '<b>Bull Case: What Would Prove "Sticky Inflation" Wrong?</b>',
        body_style
    ))
    story.append(Paragraph(
        "If any three of the following trigger simultaneously for three consecutive months, the elevated "
        "inflation regime ends and Fed flexibility opens:",
        body_style
    ))
    for b in [
        "Core PCE 3M annualized drops below 2.5% (on-target path confirmed)",
        "Services ex-shelter drops below 3.0% (wage pressure breaking)",
        "Sticky CPI drops below 3.0% (persistence breaking)",
        "5Y5Y forward drops below 2.3% (expectations re-anchoring)",
        "PCI drops below +0.5 (regime shift to on-target)",
    ]:
        story.append(Paragraph(f'\u2022 {b}', bullet_style))

    story.append(Spacer(1, 8))
    story.append(Paragraph(
        "<b>Bear Case: What Would Confirm It's Getting Worse?</b>",
        body_style
    ))
    story.append(Paragraph(
        "If any two of the following trigger, inflation is reaccelerating beyond sticky into crisis territory:",
        body_style
    ))
    for b in [
        "Core PCE 3M annualized exceeds 4.0% (momentum reversing)",
        "Goods CPI accelerates above 3.0% (tariff pass-through or dollar weakness)",
        "5Y5Y forward exceeds 2.75% (expectations de-anchoring)",
        "Services ex-shelter exceeds 4.5% (wage-price spiral resuming)",
    ]:
        story.append(Paragraph(f'\u2022 {b}', bullet_style))

    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "Framework drives positioning, but the framework can be wrong. Data determines outcome. "
        "We publish our thresholds so you can hold us accountable.",
        body_style
    ))

    story.append(CondPageBreak(3.5 * inch))

    # ==========================================
    # THE BOTTOM LINE
    # ==========================================
    story.append(Paragraph('THE BOTTOM LINE', h1_style))
    story.append(Paragraph(
        "The last mile of disinflation is a services problem, not an inflation problem in the traditional "
        "sense. Goods are barely positive and no longer a source of relief. The shelter lag has mostly "
        "unwound. But services ex-shelter remain stuck, held up by wage growth that's positive in real "
        "terms but inconsistent with 2% inflation.",
        body_style
    ))
    story.append(Paragraph(
        "The Fed is boxed in. Cut too aggressively and you risk reigniting inflation through a weaker "
        "dollar and easier financial conditions. Stay too tight and you risk breaking the labor market "
        "(see Pillar 1) while waiting for services to moderate.",
        body_style
    ))
    story.append(Paragraph(
        "Five structural forces keep the floor elevated: deglobalization raising goods costs as supply "
        "chains shift to higher-cost alternatives, the energy transition creating resource-intensive "
        "commodity demand before the long-run deflationary payoff arrives, demographics constraining "
        "labor supply as Baby Boomer retirements depress participation, chronic housing underbuilding "
        "since the GFC keeping vacancy rates historically low, and fiscal deficits above 5% of GDP "
        "injecting demand that monetary policy is simultaneously trying to restrict.",
        body_style
    ))
    story.append(Paragraph(
        "Together, they suggest a structural inflation floor of 2.5-3.0%. The 2010s regime of sub-2% "
        "inflation required globalization tailwinds, subdued wages, and fiscal austerity. All three "
        "have reversed.",
        body_style
    ))
    story.append(Paragraph(
        "The framework says: watch the composition, not the headline. The headline may approach 2% "
        "eventually. The question is whether it gets there through genuine services moderation or through "
        "a recession that crushes demand. The flows that lead in labor, not the stocks that lag, will "
        "tell us which path we're on.",
        body_style
    ))

    # ==========================================
    # CLOSING
    # ==========================================
    story.append(Spacer(1, 0.3 * inch))
    story.append(Paragraph(
        "That's our view from the Watch. Until next time, we'll be sure to keep the light on....",
        ParagraphStyle('SignOff', parent=body_style, fontName='Helvetica-Oblique',
                       alignment=TA_CENTER, fontSize=11, textColor=OCEAN_BLUE)
    ))

    story.append(Spacer(1, 0.4 * inch))
    story.append(HRFlowable(width="80%", thickness=2, color=OCEAN_BLUE, spaceBefore=10, spaceAfter=20))

    closing_style = ParagraphStyle(
        'Closing',
        parent=body_style,
        alignment=TA_CENTER,
        fontSize=12,
        textColor=OCEAN_BLUE,
        fontName='Helvetica-Oblique',
    )

    story.append(Paragraph(
        "<i>Next in the series: Pillar 3 (Growth) and the Second Derivative.<br/>"
        "Why the rate of change matters more than the level, and what leading<br/>"
        "indicators are saying about the growth trajectory.</i>",
        closing_style
    ))

    story.append(Spacer(1, 0.3 * inch))
    story.append(Paragraph(
        '<b>Join The Watch</b> for the full 12-Pillar Educational Series.',
        ParagraphStyle('CTA', parent=body_style, alignment=TA_CENTER, fontSize=11)
    ))

    story.append(Spacer(1, 0.5 * inch))
    story.append(Paragraph("MACRO, ILLUMINATED.", title_style))

    story.append(Spacer(1, 0.3 * inch))
    story.append(Paragraph(
        "Bob Sheehan, CFA, CMT<br/>"
        "Founder &amp; Chief Investment Officer<br/>"
        "Lighthouse Macro<br/>"
        "bob@lighthousemacro.com | @LHMacro",
        body_style
    ))

    # Data sources / disclosure
    story.append(Spacer(1, 0.5 * inch))
    story.append(HRFlowable(width="100%", thickness=0.5, color=OCEAN_BLUE, spaceAfter=8))

    disc_style = ParagraphStyle('Disc', parent=body_style, fontSize=8, leading=11, textColor=MUTED_GRAY)
    story.append(Paragraph(
        '<b>Data Sources:</b> Bureau of Labor Statistics (CPI, PPI) \u00b7 Bureau of Economic Analysis (PCE) \u00b7 '
        'Atlanta Fed (Sticky/Flexible CPI) \u00b7 Dallas Fed (Trimmed Mean PCE) \u00b7 '
        'University of Michigan (Consumer Expectations) \u00b7 FRED',
        disc_style
    ))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        '<b>Disclosure:</b> This is educational content. Not investment advice. Past patterns don\'t guarantee '
        'future results. The inflation framework is empirically grounded and uses publicly available data. '
        'Composite weightings are proprietary.',
        disc_style
    ))

    # Build
    doc.build(story, onFirstPage=create_header_footer, onLaterPages=create_header_footer)
    print(f'\nPDF generated: {OUTPUT_PDF}')
    return OUTPUT_PDF


if __name__ == '__main__':
    build_pdf()
