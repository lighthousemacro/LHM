#!/usr/bin/env python3
"""
Generate Branded PDF for Pillar 1: Labor Framework
===================================================
Converts the PILLAR 1 LABOR.md document to a branded PDF
with Lighthouse Macro styling.

Usage:
    python generate_labor_framework_pdf.py
"""

import os
import re
from datetime import datetime

# Try to import PDF libraries
try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        PageBreak, ListFlowable, ListItem, Preformatted
    )
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False
    print("ReportLab not installed. Installing...")
    os.system("pip install reportlab")
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        PageBreak, ListFlowable, ListItem, Preformatted
    )
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

# ============================================
# LIGHTHOUSE MACRO BRAND COLORS
# ============================================
OCEAN_BLUE = colors.HexColor('#2389BB')
DUSK_ORANGE = colors.HexColor('#FF6723')
SKY_CYAN = colors.HexColor('#00D4FF')
VENUS_MAGENTA = colors.HexColor('#FF2389')
SEA_TEAL = colors.HexColor('#00BB89')
DOLDRUMS_GRAY = colors.HexColor('#898989')
DARK_GRAY = colors.HexColor('#333333')
LIGHT_GRAY = colors.HexColor('#F5F5F5')

# ============================================
# PATHS
# ============================================
BASE_PATH = '/Users/bob/LHM'
FRAMEWORK_PATH = f'{BASE_PATH}/Strategy/PILLAR 1 LABOR.md'
OUTPUT_PATH = f'{BASE_PATH}/Outputs/LHM_Pillar_1_Labor_Framework.pdf'

def create_styles():
    """Create branded paragraph styles."""
    styles = getSampleStyleSheet()

    # Title style
    styles.add(ParagraphStyle(
        name='LHMTitle',
        fontName='Helvetica-Bold',
        fontSize=24,
        textColor=OCEAN_BLUE,
        alignment=TA_CENTER,
        spaceAfter=6
    ))

    # Subtitle style
    styles.add(ParagraphStyle(
        name='LHMSubtitle',
        fontName='Helvetica',
        fontSize=14,
        textColor=DARK_GRAY,
        alignment=TA_CENTER,
        spaceAfter=24
    ))

    # Section header (H2)
    styles.add(ParagraphStyle(
        name='LHMSection',
        fontName='Helvetica-Bold',
        fontSize=16,
        textColor=OCEAN_BLUE,
        spaceBefore=18,
        spaceAfter=12,
        borderColor=OCEAN_BLUE,
        borderWidth=0,
        borderPadding=0
    ))

    # Subsection header (H3)
    styles.add(ParagraphStyle(
        name='LHMSubsection',
        fontName='Helvetica-Bold',
        fontSize=12,
        textColor=DARK_GRAY,
        spaceBefore=12,
        spaceAfter=8
    ))

    # Sub-subsection (H4)
    styles.add(ParagraphStyle(
        name='LHMSubSubsection',
        fontName='Helvetica-Bold',
        fontSize=10,
        textColor=OCEAN_BLUE,
        spaceBefore=8,
        spaceAfter=6
    ))

    # Body text
    styles.add(ParagraphStyle(
        name='LHMBody',
        fontName='Helvetica',
        fontSize=10,
        textColor=DARK_GRAY,
        alignment=TA_JUSTIFY,
        spaceBefore=4,
        spaceAfter=8,
        leading=14
    ))

    # Quote/emphasis
    styles.add(ParagraphStyle(
        name='LHMQuote',
        fontName='Helvetica-Oblique',
        fontSize=10,
        textColor=OCEAN_BLUE,
        alignment=TA_CENTER,
        spaceBefore=12,
        spaceAfter=12,
        leftIndent=36,
        rightIndent=36
    ))

    # Code/preformatted
    styles.add(ParagraphStyle(
        name='LHMCode',
        fontName='Courier',
        fontSize=8,
        textColor=DARK_GRAY,
        backColor=LIGHT_GRAY,
        spaceBefore=6,
        spaceAfter=6,
        leftIndent=12,
        rightIndent=12
    ))

    # Table header
    styles.add(ParagraphStyle(
        name='LHMTableHeader',
        fontName='Helvetica-Bold',
        fontSize=9,
        textColor=colors.white,
        alignment=TA_CENTER
    ))

    # Table cell
    styles.add(ParagraphStyle(
        name='LHMTableCell',
        fontName='Helvetica',
        fontSize=8,
        textColor=DARK_GRAY,
        alignment=TA_LEFT
    ))

    # Footer
    styles.add(ParagraphStyle(
        name='LHMFooter',
        fontName='Helvetica',
        fontSize=8,
        textColor=DOLDRUMS_GRAY,
        alignment=TA_CENTER
    ))

    # Bullet point
    styles.add(ParagraphStyle(
        name='LHMBullet',
        fontName='Helvetica',
        fontSize=10,
        textColor=DARK_GRAY,
        leftIndent=20,
        spaceBefore=2,
        spaceAfter=2,
        leading=14
    ))

    return styles


def add_header_footer(canvas, doc):
    """Add branded header and footer to each page."""
    canvas.saveState()

    # Header: accent bar
    canvas.setFillColor(OCEAN_BLUE)
    canvas.rect(0, letter[1] - 20, letter[0] * 0.67, 4, fill=1, stroke=0)
    canvas.setFillColor(DUSK_ORANGE)
    canvas.rect(letter[0] * 0.67, letter[1] - 20, letter[0] * 0.33, 4, fill=1, stroke=0)

    # Header text
    canvas.setFillColor(OCEAN_BLUE)
    canvas.setFont('Helvetica-Bold', 8)
    canvas.drawString(72, letter[1] - 40, "LIGHTHOUSE MACRO")

    canvas.setFillColor(DARK_GRAY)
    canvas.setFont('Helvetica', 8)
    canvas.drawRightString(letter[0] - 72, letter[1] - 40, "Pillar 1: Labor Framework")

    # Footer
    canvas.setFillColor(DOLDRUMS_GRAY)
    canvas.setFont('Helvetica', 8)
    canvas.drawString(72, 36, f"Generated: {datetime.now().strftime('%Y-%m-%d')}")
    canvas.drawCentredString(letter[0] / 2, 36, "MACRO, ILLUMINATED.")
    canvas.drawRightString(letter[0] - 72, 36, f"Page {doc.page}")

    # Footer accent bar
    canvas.setFillColor(OCEAN_BLUE)
    canvas.rect(0, 24, letter[0] * 0.67, 2, fill=1, stroke=0)
    canvas.setFillColor(DUSK_ORANGE)
    canvas.rect(letter[0] * 0.67, 24, letter[0] * 0.33, 2, fill=1, stroke=0)

    canvas.restoreState()


def create_table(data, col_widths=None, highlight_rows=None):
    """Create a styled table."""
    if col_widths is None:
        col_widths = [100] * len(data[0])

    table = Table(data, colWidths=col_widths, repeatRows=1)

    style_commands = [
        ('BACKGROUND', (0, 0), (-1, 0), OCEAN_BLUE),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 0.5, DOLDRUMS_GRAY),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, LIGHT_GRAY]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ]

    # Add highlight rows (for breach/warning indicators)
    if highlight_rows:
        for row_idx, color in highlight_rows:
            style_commands.append(('BACKGROUND', (0, row_idx), (-1, row_idx), color))
            style_commands.append(('TEXTCOLOR', (0, row_idx), (-1, row_idx), colors.white))

    table.setStyle(TableStyle(style_commands))
    return table


def build_pdf():
    """Build the branded PDF document."""
    styles = create_styles()

    # Create output directory if needed
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    # Create PDF document
    doc = SimpleDocTemplate(
        OUTPUT_PATH,
        pagesize=letter,
        leftMargin=72,
        rightMargin=72,
        topMargin=72,
        bottomMargin=72
    )

    story = []

    # ============================================
    # TITLE PAGE
    # ============================================
    story.append(Spacer(1, 80))
    story.append(Paragraph("PILLAR 1: LABOR", styles['LHMTitle']))
    story.append(Spacer(1, 12))
    story.append(Paragraph("THE ECONOMIC GENOME", styles['LHMTitle']))
    story.append(Spacer(1, 24))

    # Accent bar
    accent_data = [['', '']]
    accent_table = Table(accent_data, colWidths=[300, 150])
    accent_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), OCEAN_BLUE),
        ('BACKGROUND', (1, 0), (1, 0), DUSK_ORANGE),
        ('LINEABOVE', (0, 0), (-1, 0), 4, OCEAN_BLUE),
    ]))
    story.append(accent_table)

    story.append(Spacer(1, 24))
    story.append(Paragraph(
        '"The unemployment rate is at 4.2%. By every historical standard, that\'s a healthy labor market. '
        'So why are workers acting like it\'s 2008?"',
        styles['LHMQuote']
    ))

    story.append(Spacer(1, 12))
    story.append(Paragraph(
        '"The quits rate is the economy\'s truth serum. Workers vote with their feet, '
        'and the ballots are already counted."',
        styles['LHMQuote']
    ))

    story.append(Spacer(1, 48))
    story.append(Paragraph("The Diagnostic Dozen: A Framework for Reading the Macro Cycle", styles['LHMSubtitle']))
    story.append(Paragraph(f"Version 3.0 | {datetime.now().strftime('%B %Y')}", styles['LHMSubtitle']))

    story.append(Spacer(1, 80))
    story.append(Paragraph("Bob Sheehan, CFA, CMT", styles['LHMBody']))
    story.append(Paragraph("Founder & Chief Investment Officer", styles['LHMBody']))
    story.append(Paragraph("Lighthouse Macro", styles['LHMBody']))
    story.append(Paragraph("bob@lighthousemacro.com", styles['LHMBody']))

    story.append(PageBreak())

    # ============================================
    # TABLE OF CONTENTS
    # ============================================
    story.append(Paragraph("TABLE OF CONTENTS", styles['LHMSection']))
    story.append(Spacer(1, 12))

    toc_items = [
        "1. The Labor Transmission Chain",
        "2. Why Labor Leads Everything",
        "3. Primary Indicators",
        "   A. Employment Flows (The Core Signal)",
        "   B. Wage Dynamics (The Inflation Transmission Belt)",
        "   C. Labor Supply (The Structural Foundation)",
        "   D. Job Quality & Composition",
        "   E. Unemployment Decomposition",
        "   F. Hours Worked & Productivity",
        "   G. Labor Fragility Index (LFI)",
        "   H. Sectoral Employment Dynamics",
        "4. Demographic Segmentation",
        "   I. Unemployment by Age (The Youth Canary)",
        "   J. Unemployment by Education (The Skills Buffer)",
        "   K. Unemployment by Race/Ethnicity (The Leading Edge)",
        "   L. Unemployment by Gender (The Sectoral Proxy)",
        "5. Labor Force Participation by Segment",
        "6. Geographic Segmentation",
        "7. Income Distribution & Wage Bifurcation",
        "8. Industry Deep Dive",
        "9. Firm Size Dynamics",
        "10. High-Frequency Leading Indicators",
        "11. Segmented Labor Fragility Index",
        "12. Labor Pillar Composite Index (LPI)",
        "13. Lead/Lag Relationships",
        "14. Cross-Pillar Integration",
        "15. Current State Assessment",
        "16. Invalidation Criteria",
    ]

    for item in toc_items:
        story.append(Paragraph(item, styles['LHMBody']))

    story.append(PageBreak())

    # ============================================
    # SECTION 1: THE LABOR TRANSMISSION CHAIN
    # ============================================
    story.append(Paragraph("1. THE LABOR TRANSMISSION CHAIN", styles['LHMSection']))
    story.append(Spacer(1, 8))

    story.append(Paragraph(
        "Labor isn't just employment data. It's the economic genome, the code that determines whether "
        "the expansion continues or the system resets. The transmission mechanism operates through cascading flows:",
        styles['LHMBody']
    ))

    story.append(Spacer(1, 8))
    story.append(Paragraph(
        "Worker Confidence → Job-Switching Behavior → Wage Pressure → "
        "Income Growth → Spending Capacity → Corporate Pricing Power → "
        "Profit Margins → Hiring Decisions → Worker Confidence",
        styles['LHMCode']
    ))

    story.append(Spacer(1, 8))
    story.append(Paragraph(
        "<b>The Insight:</b> This isn't a linear chain. It's a feedback loop. And the loop is breaking.",
        styles['LHMBody']
    ))

    story.append(Paragraph(
        "When workers stop quitting, they're not being prudent. They're seeing something management hasn't "
        "admitted yet. The quits rate is the economy's truth serum, it strips away the narrative and exposes "
        "the underlying fragility. Six to nine months before the unemployment rate rises, quits collapse. "
        "Every. Single. Time.",
        styles['LHMBody']
    ))

    story.append(PageBreak())

    # ============================================
    # SECTION 2: WHY LABOR LEADS EVERYTHING
    # ============================================
    story.append(Paragraph("2. WHY LABOR LEADS EVERYTHING", styles['LHMSection']))
    story.append(Spacer(1, 8))

    story.append(Paragraph(
        "Labor is the <b>alpha generator</b> in the three-pillar framework for a simple reason: "
        "it sits upstream of every other economic flow.",
        styles['LHMBody']
    ))

    story.append(Spacer(1, 8))
    story.append(Paragraph("The Cascade:", styles['LHMSubsection']))

    cascade_data = [
        ['Link', 'Mechanism', 'Lag'],
        ['Labor → Consumer', 'Income determines spending capacity', '1-3 months'],
        ['Labor → Credit', 'Employment stress precedes default risk', '3-6 months'],
        ['Labor → Housing', 'Job stability drives home-buying decisions', '6-9 months'],
        ['Labor → Growth', 'Hours worked contracts before output falls', '2-4 months'],
        ['Labor → Prices', 'Wage pressure drives services inflation', 'Persistent'],
    ]
    story.append(create_table(cascade_data, col_widths=[100, 220, 80]))

    story.append(Spacer(1, 12))
    story.append(Paragraph(
        "<b>Get the labor call right, and you've triangulated 70% of the macro outlook. "
        "Miss it, and you're trading narratives instead of reality.</b>",
        styles['LHMQuote']
    ))

    story.append(PageBreak())

    # ============================================
    # SECTION 3A: EMPLOYMENT FLOWS
    # ============================================
    story.append(Paragraph("3A. EMPLOYMENT FLOWS (The Core Signal)", styles['LHMSection']))
    story.append(Spacer(1, 8))

    story.append(Paragraph(
        "The stock of employment (payrolls, unemployment rate) is a lagging indicator. "
        "The <b>flows</b> tell you where we're going.",
        styles['LHMBody']
    ))

    story.append(Spacer(1, 8))
    story.append(Paragraph("Primary JOLTS & Claims Indicators", styles['LHMSubsection']))

    flows_data = [
        ['Indicator', 'FRED Code', 'Freq', 'Lead/Lag', 'Interpretation'],
        ['JOLTS Job Openings', 'JTSJOL', 'M', 'Leads 3-6 mo', 'Demand signal (noisy)'],
        ['JOLTS Hires', 'JTSHIL', 'M', 'Leads 2-4 mo', 'Actual hiring execution'],
        ['JOLTS Quits', 'JTSQUL', 'M', 'Leads 6-9 mo', 'Worker confidence'],
        ['JOLTS Quits Rate', 'JTSQUR', 'M', 'PRIMARY', 'Normalized quits'],
        ['JOLTS Layoffs', 'JTSLDL', 'M', 'Lags 1-3 mo', 'Stress confirmation'],
        ['Initial Claims', 'ICSA', 'W', 'Leads 4-8 wks', 'Highest-freq stress'],
        ['Continued Claims', 'CCSA', 'W', 'Coincident', 'Slack measure'],
    ]
    story.append(create_table(flows_data, col_widths=[90, 60, 30, 70, 140]))

    story.append(Spacer(1, 12))
    story.append(Paragraph("Derived Flow Metrics", styles['LHMSubsection']))

    derived_flows = [
        ['Metric', 'Formula', 'Threshold', 'Signal'],
        ['Hires/Quits Ratio', 'JTSHIL / JTSQUL', '<2.0', 'Demand weakening'],
        ['Quits/Layoffs Ratio', 'JTSQUL / JTSLDL', '<2.0', 'Confidence collapsing'],
        ['Openings/Unemployed', 'JTSJOL / Unemployed', '<1.2', 'Slack developing'],
        ['Claims Momentum', 'YoY% 4-wk MA ICSA', '>+15%', 'Early deterioration'],
    ]
    story.append(create_table(derived_flows, col_widths=[100, 120, 60, 120]))

    story.append(Spacer(1, 12))
    story.append(Paragraph("Regime Thresholds: Employment Flows", styles['LHMSubsection']))

    regime_flows = [
        ['Indicator', 'Expansion', 'Neutral', 'Softening', 'Contraction'],
        ['Quits Rate', '>2.5%', '2.2-2.5%', '2.0-2.2%', '<2.0%'],
        ['Hires/Quits', '>2.5', '2.0-2.5', '1.7-2.0', '<1.7'],
        ['Openings/Unemployed', '>1.8', '1.2-1.8', '1.0-1.2', '<1.0'],
        ['Initial Claims 4-wk MA', '<220k', '220-250k', '250-300k', '>300k'],
    ]
    story.append(create_table(regime_flows, col_widths=[100, 70, 70, 70, 70]))

    story.append(Spacer(1, 12))
    story.append(Paragraph(
        "<b>The Quits Rate Kill Line:</b> Below 2.0%, the labor market has crossed into pre-recessionary "
        "territory in every cycle since 1990. No exceptions. Current reading: <b>1.9%</b> (Dec 2025).",
        styles['LHMBody']
    ))

    story.append(PageBreak())

    # ============================================
    # SECTION 3B: WAGE DYNAMICS
    # ============================================
    story.append(Paragraph("3B. WAGE DYNAMICS (The Inflation Transmission Belt)", styles['LHMSection']))
    story.append(Spacer(1, 8))

    story.append(Paragraph(
        "Wages are sticky. They accelerate during expansions and decelerate slowly during downturns. "
        "This stickiness creates the 'last mile' inflation problem.",
        styles['LHMBody']
    ))

    wage_data = [
        ['Indicator', 'FRED/Source', 'Freq', 'Lead/Lag', 'Interpretation'],
        ['Avg Hourly Earnings', 'CES0500000003', 'M', 'Coincident', 'Headline wage growth'],
        ['AHE: Prod Workers', 'CES0500000008', 'M', 'Coincident', '80% of workforce'],
        ['ECI Total', 'ECIALLCIV', 'Q', 'Lagging', 'Wages + benefits'],
        ['Atlanta Fed Tracker', 'Web', 'M', 'Coincident', 'Median wage (CPS)'],
        ['Job Switchers', 'Atlanta Fed', 'M', 'LEADING', 'Job-hopper premium'],
        ['Job Stayers', 'Atlanta Fed', 'M', 'Lagging', 'Inertia component'],
    ]
    story.append(create_table(wage_data, col_widths=[90, 80, 30, 60, 130]))

    story.append(Spacer(1, 12))
    story.append(Paragraph("Key Wage Metrics", styles['LHMSubsection']))

    wage_metrics = [
        ['Metric', 'Formula', 'Threshold', 'Signal'],
        ['Job-Hopper Premium', 'Switchers - Stayers', '<0.5 ppts', 'Late-cycle warning'],
        ['Real Wage Growth', 'AHE YoY - Core CPI', '<0%', 'Purchasing power eroding'],
        ['Wage-Productivity Gap', 'AHE YoY - Productivity', '>2 ppts', 'Margin squeeze'],
    ]
    story.append(create_table(wage_metrics, col_widths=[100, 140, 70, 100]))

    story.append(Spacer(1, 12))
    story.append(Paragraph(
        "<b>The Job-Hopper Premium Collapse:</b> From 2021-2022, job switchers earned 5-6 ppts more than stayers. "
        "By Jan 2026, the premium narrowed to <b>0.2 ppts</b>. The grass is no longer greener. Workers know it.",
        styles['LHMBody']
    ))

    story.append(PageBreak())

    # ============================================
    # SECTION 3G: LABOR FRAGILITY INDEX
    # ============================================
    story.append(Paragraph("3G. LABOR FRAGILITY INDEX (LFI)", styles['LHMSection']))
    story.append(Spacer(1, 8))

    story.append(Paragraph(
        "The Labor Fragility Index synthesizes leading indicators of labor market stress into a single composite.",
        styles['LHMBody']
    ))

    story.append(Spacer(1, 8))
    story.append(Paragraph("Formula:", styles['LHMSubsection']))
    story.append(Paragraph(
        "LFI = 0.30 x z(Long_Term_Unemployed_Share)\n"
        "    + 0.25 x z(-Quits_Rate)           [Inverted]\n"
        "    + 0.20 x z(-Hires_Quits_Ratio)    [Inverted]\n"
        "    + 0.15 x z(-Temp_Help_YoY)        [Inverted]\n"
        "    + 0.10 x z(-Job_Hopper_Premium)   [Inverted]",
        styles['LHMCode']
    ))

    story.append(Spacer(1, 8))
    story.append(Paragraph("Component Weights:", styles['LHMSubsection']))

    lfi_weights = [
        ['Component', 'Weight', 'Rationale'],
        ['Long-Term Unemployed Share', '30%', 'Structural fragility, highest persistence'],
        ['Quits Rate', '25%', 'Primary leading indicator, cleanest signal'],
        ['Hires/Quits Ratio', '20%', 'Demand confirmation'],
        ['Temp Help Employment', '15%', 'Canary, first to be cut'],
        ['Job-Hopper Premium', '10%', 'Worker confidence microstructure'],
    ]
    story.append(create_table(lfi_weights, col_widths=[130, 50, 220]))

    story.append(Spacer(1, 12))
    story.append(Paragraph("LFI Interpretation:", styles['LHMSubsection']))

    lfi_interp = [
        ['LFI Range', 'Regime', 'Interpretation'],
        ['< 0.0', 'Healthy', 'Labor market robust, flows positive'],
        ['0.0 to +0.5', 'Neutral', 'Balanced conditions, normal churn'],
        ['+0.5 to +1.0', 'Elevated', 'Fragility developing, early stress'],
        ['+1.0 to +1.5', 'High', 'Pre-recessionary, flows deteriorating'],
        ['> +1.5', 'Critical', 'Recession imminent, structural damage'],
    ]
    story.append(create_table(lfi_interp, col_widths=[80, 80, 240],
                              highlight_rows=[(3, DUSK_ORANGE), (4, VENUS_MAGENTA), (5, VENUS_MAGENTA)]))

    story.append(Spacer(1, 12))
    story.append(Paragraph(
        "<b>Current LFI: +0.93</b> (Elevated Fragility). Labor market in pre-recessionary zone.",
        styles['LHMQuote']
    ))

    story.append(PageBreak())

    # ============================================
    # DEMOGRAPHIC SEGMENTATION
    # ============================================
    story.append(Paragraph("4. DEMOGRAPHIC SEGMENTATION", styles['LHMSection']))
    story.append(Spacer(1, 8))

    story.append(Paragraph(
        "Headlines lie. The unemployment rate is an average that obscures critical distributional dynamics. "
        "True labor market analysis requires decomposing the aggregate into demographic cohorts.",
        styles['LHMBody']
    ))

    story.append(Spacer(1, 8))
    story.append(Paragraph("The Segmentation Hierarchy:", styles['LHMSubsection']))
    story.append(Paragraph(
        "LEADING (First to show stress)          LAGGING (Last to show stress)\n"
        "────────────────────────────────────────────────────────────────────\n"
        "Youth (16-24)                           Prime-Age (25-54)\n"
        "Less than HS Education                  Bachelor's Degree+\n"
        "Black/Hispanic Unemployment             White Unemployment\n"
        "Men (Goods-producing)                   Women (Services)\n"
        "Part-time for Economic Reasons          Full-time Employment",
        styles['LHMCode']
    ))

    story.append(Spacer(1, 12))
    story.append(Paragraph("Unemployment by Age", styles['LHMSubsection']))

    age_data = [
        ['Age Cohort', 'FRED Code', 'Typical Ratio', 'Cycle Behavior'],
        ['16-19 years', 'LNS14000012', '3.0-4.0x', 'Most volatile, first to rise'],
        ['20-24 years', 'LNS14000036', '1.8-2.5x', 'Entry-level sensitivity'],
        ['25-54 (Prime)', 'LNS14000060', '0.8-0.9x', 'Core workforce, most stable'],
        ['55+ years', 'LNS14024230', '0.7-0.9x', 'Lower rate, longer duration'],
    ]
    story.append(create_table(age_data, col_widths=[80, 90, 80, 150]))

    story.append(Spacer(1, 12))
    story.append(Paragraph("Unemployment by Education", styles['LHMSubsection']))

    edu_data = [
        ['Education Level', 'FRED Code', 'Typical Rate', 'Cycle Sensitivity'],
        ['Less Than High School', 'LNS14027659', '6-8%', 'Highest, most cyclical'],
        ['High School Only', 'LNS14027660', '4-5%', 'High cyclicality'],
        ['Some College/Associate', 'LNS14027689', '3-4%', 'Moderate cyclicality'],
        ['Bachelor\'s Degree+', 'LNS14027662', '2-3%', 'Lowest, most insulated'],
    ]
    story.append(create_table(edu_data, col_widths=[110, 90, 70, 130]))

    story.append(PageBreak())

    # ============================================
    # GEOGRAPHIC SEGMENTATION
    # ============================================
    story.append(Paragraph("6. GEOGRAPHIC SEGMENTATION", styles['LHMSection']))
    story.append(Spacer(1, 8))

    story.append(Paragraph(
        "National data obscures regional variation. Labor market conditions vary substantially across states, "
        "and regional divergence often precedes national turns.",
        styles['LHMBody']
    ))

    story.append(Spacer(1, 8))
    story.append(Paragraph("Regional Economic Dynamics:", styles['LHMSubsection']))

    geo_data = [
        ['Region', 'Key States', 'Cycle Sensitivity', 'Leading Industries'],
        ['Rust Belt', 'OH, MI, PA, IN', 'High (Mfg)', 'Auto, steel, machinery'],
        ['Sun Belt', 'TX, FL, AZ, GA', 'Moderate (Growth)', 'Construction, services'],
        ['Energy Belt', 'TX, ND, OK, WV', 'Commodity-linked', 'Oil & gas'],
        ['Tech Corridor', 'CA, WA, MA, CO', 'Tech cycle', 'Software, hardware'],
        ['Northeast', 'NY, NJ, CT', 'Finance-sensitive', 'Financial services'],
    ]
    story.append(create_table(geo_data, col_widths=[70, 90, 100, 140]))

    story.append(Spacer(1, 12))
    story.append(Paragraph("State Diffusion Index:", styles['LHMSubsection']))

    diffusion_data = [
        ['% States Rising', 'Interpretation'],
        ['<30%', 'Localized (idiosyncratic state issues)'],
        ['30-50%', 'Spreading (weakness gaining traction)'],
        ['50-70%', 'Broad-Based (national downturn underway)'],
        ['>70%', 'Pervasive (deep recession)'],
    ]
    story.append(create_table(diffusion_data, col_widths=[100, 300],
                              highlight_rows=[(3, DUSK_ORANGE), (4, VENUS_MAGENTA)]))

    story.append(Spacer(1, 12))
    story.append(Paragraph(
        "<b>Current State:</b> 58% of states showing rising unemployment. "
        "Weakness is spreading, not isolated.",
        styles['LHMBody']
    ))

    story.append(PageBreak())

    # ============================================
    # LABOR PILLAR COMPOSITE INDEX
    # ============================================
    story.append(Paragraph("12. LABOR PILLAR COMPOSITE INDEX (LPI)", styles['LHMSection']))
    story.append(Spacer(1, 8))

    story.append(Paragraph(
        "The Labor Pillar Composite synthesizes flows, stocks, and quality metrics into a single regime indicator.",
        styles['LHMBody']
    ))

    story.append(Spacer(1, 8))
    story.append(Paragraph("Formula:", styles['LHMSubsection']))
    story.append(Paragraph(
        "LPI = 0.20 x z(Quits_Rate)\n"
        "    + 0.15 x z(Hires_Quits_Ratio)\n"
        "    + 0.15 x z(-Long_Term_Unemployed_Share)   [Inverted]\n"
        "    + 0.15 x z(-Initial_Claims_4wk_MA)        [Inverted]\n"
        "    + 0.10 x z(Prime_Age_LFPR)\n"
        "    + 0.10 x z(Avg_Weekly_Hours_Mfg)\n"
        "    + 0.10 x z(-Temp_Help_YoY)                [Inverted]\n"
        "    + 0.05 x z(Job_Hopper_Premium)",
        styles['LHMCode']
    ))

    story.append(Spacer(1, 12))
    story.append(Paragraph("LPI Interpretation:", styles['LHMSubsection']))

    lpi_interp = [
        ['LPI Range', 'Regime', 'Equity Allocation', 'Signal'],
        ['> +1.0', 'Labor Boom', '65-70%', 'Tight labor, wage pressure'],
        ['+0.5 to +1.0', 'Expansion', '60-65%', 'Healthy growth, lean cyclical'],
        ['-0.5 to +0.5', 'Neutral', '55-60%', 'Balanced conditions'],
        ['-1.0 to -0.5', 'Softening', '45-50%', 'Fragility developing'],
        ['< -1.0', 'Contraction', '30-40%', 'Recession imminent'],
    ]
    story.append(create_table(lpi_interp, col_widths=[80, 80, 90, 150],
                              highlight_rows=[(4, DUSK_ORANGE), (5, VENUS_MAGENTA)]))

    story.append(Spacer(1, 12))
    story.append(Paragraph("Historical Calibration:", styles['LHMSubsection']))

    lpi_history = [
        ['Period', 'LPI', 'Regime', 'Outcome (12M Forward)'],
        ['Dec 2006', '-0.4', 'Softening', 'Recession (Dec 2007 start)'],
        ['Dec 2007', '-1.2', 'Contraction', 'Deep recession confirmed'],
        ['Dec 2018', '+0.1', 'Neutral', 'Mfg recession, no broad downturn'],
        ['Feb 2020', '+0.8', 'Expansion', 'COVID shock (exogenous)'],
        ['Dec 2021', '+1.6', 'Boom', 'Tightest labor in 50 years'],
        ['Dec 2025', '-0.6', 'Softening', 'Fragility signal active'],
    ]
    story.append(create_table(lpi_history, col_widths=[70, 50, 80, 200],
                              highlight_rows=[(6, DUSK_ORANGE)]))

    story.append(PageBreak())

    # ============================================
    # CURRENT STATE ASSESSMENT
    # ============================================
    story.append(Paragraph("15. CURRENT STATE ASSESSMENT (January 2026)", styles['LHMSection']))
    story.append(Spacer(1, 8))

    current_data = [
        ['Indicator', 'Current', 'Threshold', 'Assessment'],
        ['Quits Rate', '1.9%', '<2.0% = Pre-recessionary', 'BREACH'],
        ['Hires/Quits Ratio', '1.8', '<2.0 = Weakening', 'Caution'],
        ['Long-Term Unemployed Share', '25.7%', '>22% = Fragility', 'BREACH'],
        ['Initial Claims 4-wk MA', '235k', '<250k = Stable', 'OK'],
        ['Temp Help YoY%', '-7.1%', '<-3% = Recession signal', 'BREACH'],
        ['Mfg Weekly Hours', '40.6 hrs', '<40.5 = Contraction', 'Caution'],
        ['Job-Hopper Premium', '0.2 ppts', '<0.5 ppts = Late-cycle', 'BREACH'],
        ['Unemployment Rate', '4.2%', '<4.5% = Stable', 'OK'],
        ['Prime-Age LFPR', '83.7%', '>83.0% = Healthy', 'OK'],
        ['LPI Estimate', '-0.6', '<-0.5 = Softening', 'SOFTENING'],
        ['LFI Estimate', '+0.93', '>+0.5 = Fragility', 'ELEVATED'],
    ]
    story.append(create_table(current_data, col_widths=[120, 60, 130, 80],
                              highlight_rows=[(1, VENUS_MAGENTA), (3, VENUS_MAGENTA),
                                             (5, VENUS_MAGENTA), (7, VENUS_MAGENTA),
                                             (10, DUSK_ORANGE), (11, DUSK_ORANGE)]))

    story.append(Spacer(1, 12))
    story.append(Paragraph("Demographic Assessment:", styles['LHMSubsection']))

    demo_current = [
        ['Segment', 'Current', '6M Prior', 'Change', 'Assessment'],
        ['Youth Unemployment (16-24)', '9.8%', '8.5%', '+1.3 ppts', 'Rising'],
        ['Prime-Age Unemployment', '3.8%', '3.6%', '+0.2 ppts', 'Stable'],
        ['Less Than HS Unemployment', '7.2%', '6.1%', '+1.1 ppts', 'Rising'],
        ['Bachelor\'s+ Unemployment', '2.4%', '2.3%', '+0.1 ppts', 'Stable'],
        ['Black Unemployment', '6.8%', '6.0%', '+0.8 ppts', 'Rising'],
        ['Job-Hopper Premium', '0.2 ppts', '1.2 ppts', '-1.0 ppts', 'COLLAPSED'],
        ['State Diffusion (% Rising)', '58%', '42%', '+16 ppts', 'Spreading'],
    ]
    story.append(create_table(demo_current, col_widths=[130, 55, 55, 60, 80],
                              highlight_rows=[(6, VENUS_MAGENTA)]))

    story.append(PageBreak())

    # ============================================
    # NARRATIVE SYNTHESIS
    # ============================================
    story.append(Paragraph("Narrative Synthesis", styles['LHMSection']))
    story.append(Spacer(1, 8))

    story.append(Paragraph(
        "The labor market is exhibiting <b>classic late-cycle bifurcation</b>: stocks look fine, flows are deteriorating. "
        "The unemployment rate (4.2%) and prime-age participation (83.7%) signal health. But underneath:",
        styles['LHMBody']
    ))

    synthesis_points = [
        "Workers have stopped quitting (1.9%, below 2.0% threshold for first time since 2020)",
        "Long-term unemployment is spiking (25.7%, highest since 2021)",
        "Temp help is collapsing (-7.1% YoY, leading indicator of broader layoffs)",
        "Manufacturing hours are contracting (40.6 hrs, production cutbacks underway)",
        "The job-hopper premium is gone (0.2 ppts, no wage premium for switching)",
    ]
    for point in synthesis_points:
        story.append(Paragraph(f"• {point}", styles['LHMBullet']))

    story.append(Spacer(1, 12))
    story.append(Paragraph(
        "<b>Translation:</b> Workers see something employers haven't said yet. "
        "The quits rate is the truth serum. It doesn't lie.",
        styles['LHMQuote']
    ))

    story.append(PageBreak())

    # ============================================
    # INVALIDATION CRITERIA
    # ============================================
    story.append(Paragraph("16. INVALIDATION CRITERIA", styles['LHMSection']))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Bull Case Invalidation Thresholds", styles['LHMSubsection']))
    story.append(Paragraph(
        "If the following conditions are met <b>simultaneously for 3+ months</b>, the bearish labor thesis is invalidated:",
        styles['LHMBody']
    ))

    bull_invalidation = [
        "Quits Rate rises above 2.1% (confidence returning)",
        "Job Openings rise above 8.5M (demand accelerating)",
        "Long-Term Unemployed Share drops below 20% (structural healing)",
        "Temp Help Employment YoY% turns positive (hiring resuming)",
        "Initial Claims 4-wk MA drops below 220k (stress fading)",
        "Hours Worked (Mfg) rises above 41.0 hrs (production accelerating)",
        "LFI drops below +0.5 (fragility diminishing)",
    ]
    for point in bull_invalidation:
        story.append(Paragraph(f"✓ {point}", styles['LHMBullet']))

    story.append(Spacer(1, 12))
    story.append(Paragraph("Bear Case Confirmation Thresholds", styles['LHMSubsection']))
    story.append(Paragraph(
        "If the following conditions are met, labor deterioration is accelerating into contraction:",
        styles['LHMBody']
    ))

    bear_confirmation = [
        "Unemployment Rate crosses 4.5% and rising (recession historically begins)",
        "Initial Claims 4-wk MA exceeds 300k for 4+ consecutive weeks (acute stress)",
        "Temp Help YoY% exceeds -10% (cascading layoffs)",
        "Quits Rate drops below 1.7% (workers paralyzed, extreme risk aversion)",
        "Payrolls 3M Average turns negative (job losses confirmed)",
        "LFI exceeds +1.5 (severe fragility, recession imminent)",
        "LPI drops below -1.0 (contraction regime confirmed)",
    ]
    for point in bear_confirmation:
        story.append(Paragraph(f"✗ {point}", styles['LHMBullet']))

    story.append(PageBreak())

    # ============================================
    # CLOSING
    # ============================================
    story.append(Spacer(1, 60))
    story.append(Paragraph("CONCLUSION", styles['LHMSection']))
    story.append(Spacer(1, 12))

    story.append(Paragraph(
        "Labor isn't a sector. It's the <b>code that writes the economy</b>.",
        styles['LHMQuote']
    ))

    story.append(Spacer(1, 12))
    story.append(Paragraph(
        "When the quits rate collapses, it's not workers being prudent. It's workers reading the signal before "
        "management admits it. When long-term unemployment spikes while headline unemployment stays low, it's not "
        "a statistical quirk. It's the market fragmenting in real time. When temp help gets cut, it's not cost "
        "optimization. It's the canary singing its last note.",
        styles['LHMBody']
    ))

    story.append(Paragraph(
        "The labor market doesn't forecast the recession. <b>It is the recession</b>, "
        "six to nine months before the NBER makes it official.",
        styles['LHMBody']
    ))

    story.append(Spacer(1, 24))
    story.append(Paragraph("Current State:", styles['LHMSubsection']))
    story.append(Paragraph("• LPI at -0.6 (Softening Regime)", styles['LHMBullet']))
    story.append(Paragraph("• LFI at +0.93 (Elevated Fragility)", styles['LHMBullet']))
    story.append(Paragraph("• Quits Rate at 1.9% (Pre-Recessionary)", styles['LHMBullet']))

    story.append(Spacer(1, 24))
    story.append(Paragraph(
        "The flows are screaming. The stocks are sleeping. One of them is wrong.",
        styles['LHMQuote']
    ))

    story.append(Spacer(1, 48))

    # Accent bar
    story.append(accent_table)

    story.append(Spacer(1, 24))
    story.append(Paragraph(
        "That's our view from the Watch. Until next time, we'll be sure to keep the light on....",
        styles['LHMQuote']
    ))

    story.append(Spacer(1, 36))
    story.append(Paragraph("Bob Sheehan, CFA, CMT", styles['LHMBody']))
    story.append(Paragraph("Founder & Chief Investment Officer", styles['LHMBody']))
    story.append(Paragraph("Lighthouse Macro", styles['LHMBody']))
    story.append(Paragraph("bob@lighthousemacro.com | @LHMacro", styles['LHMBody']))
    story.append(Paragraph(f"January {datetime.now().year}", styles['LHMBody']))

    # Build PDF
    doc.build(story, onFirstPage=add_header_footer, onLaterPages=add_header_footer)

    print(f"\n{'='*60}")
    print("PDF GENERATED SUCCESSFULLY")
    print(f"{'='*60}")
    print(f"Output: {OUTPUT_PATH}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    build_pdf()
