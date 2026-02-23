#!/usr/bin/env python3
"""
Generate Branded PDF for On-Chain Analytics Framework
=====================================================
Converts the markdown framework document to a branded PDF
with Lighthouse Macro styling.

Usage:
    python generate_crypto_framework_pdf.py
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
FRAMEWORK_PATH = f'{BASE_PATH}/Strategy/ONCHAIN_ANALYTICS_FRAMEWORK.md'
OUTPUT_PATH = f'{BASE_PATH}/Outputs/LHM_Crypto_Fundamentals_Framework.pdf'

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
        fontSize=9,
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

    return styles


def parse_markdown_section(content, section_name):
    """Extract a section from markdown content."""
    pattern = rf'## {re.escape(section_name)}\n(.*?)(?=\n## |\Z)'
    match = re.search(pattern, content, re.DOTALL)
    if match:
        return match.group(1).strip()
    return ""


def create_table_from_markdown(md_table, styles):
    """Convert a markdown table to a ReportLab Table."""
    lines = [l.strip() for l in md_table.strip().split('\n') if l.strip() and not l.strip().startswith('|---')]
    if not lines:
        return None

    data = []
    for i, line in enumerate(lines):
        cells = [c.strip() for c in line.split('|')[1:-1]]
        if i == 0:
            # Header row
            data.append([Paragraph(f"<b>{c}</b>", styles['LHMTableCell']) for c in cells])
        else:
            data.append([Paragraph(c, styles['LHMTableCell']) for c in cells])

    if not data:
        return None

    # Create table with styling
    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), OCEAN_BLUE),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, DOLDRUMS_GRAY),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, LIGHT_GRAY]),
    ]))

    return table


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
    canvas.drawRightString(letter[0] - 72, letter[1] - 40, "On-Chain Analytics Framework")

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


def build_pdf():
    """Build the branded PDF document."""
    styles = create_styles()

    # Read the markdown file
    with open(FRAMEWORK_PATH, 'r') as f:
        content = f.read()

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
    story.append(Spacer(1, 100))
    story.append(Paragraph("ON-CHAIN ANALYTICS", styles['LHMTitle']))
    story.append(Paragraph("& TOKEN FUNDAMENTAL ANALYSIS", styles['LHMTitle']))
    story.append(Spacer(1, 12))
    story.append(Paragraph("FRAMEWORK", styles['LHMTitle']))
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
        '"Flows > Stocks applies to crypto too. We track protocol revenue flows, '
        'user acquisition dynamics, and valuation fundamentals systematically."',
        styles['LHMQuote']
    ))

    story.append(Spacer(1, 48))
    story.append(Paragraph("Lighthouse Macro Digital Asset Research", styles['LHMSubtitle']))
    story.append(Paragraph(f"Version 2.0 | {datetime.now().strftime('%B %Y')}", styles['LHMSubtitle']))

    story.append(Spacer(1, 100))
    story.append(Paragraph("Bob Sheehan, CFA, CMT", styles['LHMBody']))
    story.append(Paragraph("Founder & Chief Investment Officer", styles['LHMBody']))
    story.append(Paragraph("bob@lighthousemacro.com", styles['LHMBody']))

    story.append(PageBreak())

    # ============================================
    # TABLE OF CONTENTS
    # ============================================
    story.append(Paragraph("TABLE OF CONTENTS", styles['LHMSection']))
    story.append(Spacer(1, 12))

    toc_items = [
        "1. Framework Overview",
        "2. LHM Sector Taxonomy",
        "3. The Three Pillars of Token Analysis",
        "4. Metric Categories & Definitions",
        "5. LHM Proprietary Ratios",
        "6. The 19-Point Scoring System",
        "7. Microstructure Analysis",
        "8. The Perfect Setup",
        "9. Verdict Logic & Screening",
        "10. Position Sizing & Risk Management",
        "11. Trading Rules Framework",
        "12. Red Flags & Warning Signs",
        "13. Data Sources & Vendor Infrastructure",
        "14. Python Implementation",
    ]

    for item in toc_items:
        story.append(Paragraph(item, styles['LHMBody']))

    story.append(PageBreak())

    # ============================================
    # FRAMEWORK OVERVIEW
    # ============================================
    story.append(Paragraph("1. FRAMEWORK OVERVIEW", styles['LHMSection']))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Philosophy", styles['LHMSubsection']))
    philosophy_points = [
        "<b>Revenue quality matters:</b> Fees from organic usage > fees from incentivized activity",
        "<b>Dilution is the enemy:</b> Token incentives are stock-based compensation, treat them as expenses",
        "<b>Users are customers:</b> DAU/MAU trends reveal product-market fit",
        "<b>Cash flow beats narrative:</b> Earnings > hype",
    ]
    for point in philosophy_points:
        story.append(Paragraph(f"• {point}", styles['LHMBody']))

    story.append(PageBreak())

    # ============================================
    # LHM SECTOR TAXONOMY
    # ============================================
    story.append(Paragraph("2. LHM SECTOR TAXONOMY", styles['LHMSection']))
    story.append(Spacer(1, 12))

    story.append(Paragraph(
        "We strip away marketing terms ('GameFi,' 'SocialFi') and categorize by economic function.",
        styles['LHMBody']
    ))
    story.append(Spacer(1, 12))

    sector_data = [
        ['LHM Sector', 'Economic Function', 'Key Metric', 'Examples'],
        ['Layer 1 (Settlement)', 'The economy itself', 'Blockspace Demand', 'ETH, SOL, AVAX'],
        ['Layer 2 (Scaling)', 'Execution bandwidth', 'L2 Fee - L1 Rent', 'ARB, OP, BASE'],
        ['DeFi - DEX', 'Trading services', 'Volume / TVL', 'UNI, CRV, RAY'],
        ['DeFi - Lending', 'Banking services', 'Revenue / TVL', 'AAVE, COMP, MKR'],
        ['DeFi - Derivatives', 'Leverage and hedging', 'Notional / OI', 'GMX, DYDX, HLP'],
        ['Liquid Staking', 'Staking derivatives', 'Take Rate', 'LDO, RPL, JTO'],
        ['Infrastructure', 'Oracles, indexers', 'Integrations', 'LINK, GRT, PYTH'],
        ['Stablecoins', 'USD-pegged issuers', 'Outstanding Supply', 'USDC, USDT, SKY'],
        ['RWA', 'Off-chain collateral', 'AUM / Yield', 'ONDO, CFG'],
    ]

    sector_table = Table(sector_data, colWidths=[100, 120, 90, 100])
    sector_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), OCEAN_BLUE),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 0.5, DOLDRUMS_GRAY),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, LIGHT_GRAY]),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(sector_table)

    story.append(Spacer(1, 12))
    story.append(Paragraph(
        "<b>Key Insight:</b> L1 chains are infrastructure, not businesses. Their 'token incentives' "
        "are security budget (paying validators), not marketing spend. Judge L1s by fees and usage, not revenue.",
        styles['LHMBody']
    ))

    story.append(PageBreak())

    # ============================================
    # 24-POINT SCORING SYSTEM
    # ============================================
    story.append(Paragraph("6. THE 24-POINT SCORING SYSTEM", styles['LHMSection']))
    story.append(Spacer(1, 12))

    story.append(Paragraph(
        "Every crypto position receives a composite score from 0-24 points across three equally-weighted "
        "dimensions. The 24-point system mirrors the 12 Macro Pillars (Diagnostic Dozen x 2 = 24).",
        styles['LHMBody']
    ))
    story.append(Spacer(1, 12))

    scoring_data = [
        ['Dimension', 'Points', 'Components'],
        ['Technical', '0-8', 'Price vs 200d, Price vs 50d, 50d vs 200d, Relative Strength'],
        ['Fundamental', '0-8', 'Subsidy Score, Float/Unlock, Revenue Trend, Valuation'],
        ['Microstructure', '0-8', 'Funding Rate, Liquidations, Exchange Flows, OI/Leverage'],
    ]

    scoring_table = Table(scoring_data, colWidths=[100, 60, 250])
    scoring_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), OCEAN_BLUE),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, DOLDRUMS_GRAY),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, LIGHT_GRAY]),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(scoring_table)

    story.append(Spacer(1, 12))
    story.append(Paragraph(
        "<b>Design Rationale:</b> Technical tells you <i>when</i> to enter. Fundamental tells you "
        "<i>what</i> to own. Microstructure tells you <i>who else</i> is positioned. All three matter equally.",
        styles['LHMBody']
    ))

    story.append(Spacer(1, 18))
    story.append(Paragraph("Conviction Tier Assignment", styles['LHMSubsection']))

    tier_data = [
        ['Total Score', 'Conviction Tier', 'Position Weight'],
        ['20-24', 'Tier 1 (High Conviction)', '15-20%'],
        ['15-19', 'Tier 2 (Standard)', '8-12%'],
        ['10-14', 'Tier 3 (Reduced)', '4-7%'],
        ['<10', 'Tier 4 (Avoid)', '0%'],
    ]

    tier_table = Table(tier_data, colWidths=[100, 150, 100])
    tier_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), OCEAN_BLUE),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, DOLDRUMS_GRAY),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, LIGHT_GRAY]),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(tier_table)

    story.append(Spacer(1, 12))
    story.append(Paragraph("Section Minimums (Disqualifiers)", styles['LHMSubsection']))
    min_data = [
        ['Section', 'Minimum', 'Rationale'],
        ['Technical', '4/8', 'Below this, trend is broken'],
        ['Fundamental', '3/8', 'Below this, thesis is weak'],
        ['Microstructure', '2/8', 'Below this, positioning dangerous'],
    ]
    min_table = Table(min_data, colWidths=[100, 60, 200])
    min_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), OCEAN_BLUE),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, DOLDRUMS_GRAY),
    ]))
    story.append(min_table)

    story.append(PageBreak())

    # ============================================
    # LHM PROPRIETARY RATIOS
    # ============================================
    story.append(Paragraph("5. LHM PROPRIETARY RATIOS", styles['LHMSection']))
    story.append(Spacer(1, 12))

    # Subsidy Score
    story.append(Paragraph("Subsidy Score", styles['LHMSubsection']))
    story.append(Paragraph(
        "Is the protocol organic or paying users to stay?",
        styles['LHMBody']
    ))
    story.append(Paragraph(
        "Subsidy Score = Token Incentives / Revenue",
        styles['LHMCode']
    ))

    subsidy_data = [
        ['Range', 'Signal', 'Action'],
        ['< 0.5', 'ORGANIC', 'Tier 1 candidate'],
        ['0.5 - 2.0', 'SUBSIDIZED', 'Monitor trend'],
        ['> 2.0', 'UNSUSTAINABLE', 'Avoid'],
    ]

    subsidy_table = Table(subsidy_data, colWidths=[80, 120, 150])
    subsidy_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), OCEAN_BLUE),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, DOLDRUMS_GRAY),
        ('BACKGROUND', (0, 1), (-1, 1), SEA_TEAL),
        ('TEXTCOLOR', (0, 1), (-1, 1), colors.white),
        ('BACKGROUND', (0, 3), (-1, 3), VENUS_MAGENTA),
        ('TEXTCOLOR', (0, 3), (-1, 3), colors.white),
    ]))
    story.append(subsidy_table)
    story.append(Paragraph("<i>Note: L1 chains are exempt. Their 'incentives' are security budget.</i>", styles['LHMBody']))

    story.append(Spacer(1, 12))

    # Float Ratio
    story.append(Paragraph("Float Ratio", styles['LHMSubsection']))
    story.append(Paragraph(
        "Is there a VC unlock overhang?",
        styles['LHMBody']
    ))
    story.append(Paragraph(
        "Float Ratio = Circulating Supply / Total Supply",
        styles['LHMCode']
    ))

    float_data = [
        ['Range', 'Signal', 'Action'],
        ['> 70%', 'Healthy', 'Most supply trading'],
        ['50-70%', 'Acceptable', 'Monitor unlocks'],
        ['20-50%', 'Caution', 'Significant unlocks coming'],
        ['< 20%', 'PREDATORY', 'Massive dilution ahead'],
    ]

    float_table = Table(float_data, colWidths=[80, 120, 150])
    float_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), OCEAN_BLUE),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, DOLDRUMS_GRAY),
        ('BACKGROUND', (0, 4), (-1, 4), VENUS_MAGENTA),
        ('TEXTCOLOR', (0, 4), (-1, 4), colors.white),
    ]))
    story.append(float_table)

    story.append(PageBreak())

    # ============================================
    # THE PERFECT SETUP
    # ============================================
    story.append(Paragraph("8. THE PERFECT SETUP", styles['LHMSection']))
    story.append(Spacer(1, 12))

    story.append(Paragraph(
        "A 'Perfect Setup' represents maximum conviction and justifies maximum position sizing. "
        "All six elements must align:",
        styles['LHMBody']
    ))
    story.append(Spacer(1, 12))

    setup_elements = [
        ("<b>1. PRIMARY TREND ALIGNED:</b> Price > 50d MA > 200d MA, both MAs rising"),
        ("<b>2. RELATIVE STRENGTH CONFIRMED:</b> Outperforming BTC on 30d and 90d timeframes"),
        ("<b>3. CONSOLIDATION PRESENT:</b> 10-30 days of sideways price action, volatility compressing"),
        ("<b>4. MOMENTUM COOLED BUT NOT BROKEN:</b> Z-RoC pulled back but never hit -1.0"),
        ("<b>5. BREAKOUT TRIGGER:</b> Price breaks consolidation range, volume spike >1.5x average"),
        ("<b>6. MACRO REGIME SUPPORTIVE:</b> MRI < +1.5, LCI > -1.0, BTC not in death cross"),
    ]

    for element in setup_elements:
        story.append(Paragraph(f"• {element}", styles['LHMBody']))

    story.append(Spacer(1, 12))
    story.append(Paragraph(
        "<b>This is the only setup that justifies maximum position sizing.</b>",
        styles['LHMQuote']
    ))

    story.append(PageBreak())

    # ============================================
    # VERDICT CATEGORIES
    # ============================================
    story.append(Paragraph("9. VERDICT LOGIC & SCREENING", styles['LHMSection']))
    story.append(Spacer(1, 12))

    story.append(Paragraph("LHM Verdict Categories", styles['LHMSubsection']))

    verdict_data = [
        ['Verdict', 'Meaning', 'Action'],
        ['TIER 1 (Accumulate)', 'Strong fundamentals, organic traction', 'Build position'],
        ['TIER 2 (Hold)', 'Decent fundamentals, reasonable value', 'Maintain exposure'],
        ['NEUTRAL (Watch)', 'Mixed signals', 'Watchlist only'],
        ['CAUTION (Low Float)', 'Good metrics but unlock overhang', 'Avoid until unlocks'],
        ['AVOID (Vaporware)', 'High FDV, minimal revenue', 'Do not touch'],
        ['AVOID (Unsustainable)', 'Subsidy Score > 2.0', 'Ponzi dynamics'],
        ['AVOID (Dead)', 'No developers, no users', 'Abandoned'],
    ]

    verdict_table = Table(verdict_data, colWidths=[120, 180, 100])
    verdict_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), OCEAN_BLUE),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, DOLDRUMS_GRAY),
        ('BACKGROUND', (0, 1), (-1, 1), SEA_TEAL),
        ('TEXTCOLOR', (0, 1), (-1, 1), colors.white),
        ('BACKGROUND', (0, 5), (-1, -1), VENUS_MAGENTA),
        ('TEXTCOLOR', (0, 5), (-1, -1), colors.white),
    ]))
    story.append(verdict_table)

    story.append(PageBreak())

    # ============================================
    # REGIME MULTIPLIERS
    # ============================================
    story.append(Paragraph("10. POSITION SIZING & RISK MANAGEMENT", styles['LHMSection']))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Macro Regime Multipliers", styles['LHMSubsection']))
    story.append(Paragraph(
        "Position sizing is adjusted based on the broader macro environment. "
        "Even great setups deserve smaller positions in hostile regimes.",
        styles['LHMBody']
    ))
    story.append(Spacer(1, 12))

    regime_data = [
        ['Regime', 'Multiplier', 'Conditions'],
        ['SUPPORTIVE', '1.0x', 'MRI < +0.5, LCI > 0, BTC golden cross'],
        ['NEUTRAL', '0.6x', 'MRI +0.5 to +1.0, mixed signals'],
        ['RESTRICTIVE', '0.3x', 'MRI > +1.0, LCI < -0.5, BTC death cross'],
    ]

    regime_table = Table(regime_data, colWidths=[100, 80, 230])
    regime_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), OCEAN_BLUE),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, DOLDRUMS_GRAY),
        ('BACKGROUND', (0, 1), (-1, 1), SEA_TEAL),
        ('TEXTCOLOR', (0, 1), (-1, 1), colors.white),
        ('BACKGROUND', (0, 3), (-1, 3), VENUS_MAGENTA),
        ('TEXTCOLOR', (0, 3), (-1, 3), colors.white),
    ]))
    story.append(regime_table)

    story.append(Spacer(1, 12))
    story.append(Paragraph("Position Sizing Formula", styles['LHMSubsection']))
    story.append(Paragraph(
        "Final Position Size = Base Weight x Conviction Multiplier x Regime Multiplier x Liquidity Adjustment",
        styles['LHMCode']
    ))

    story.append(PageBreak())

    # ============================================
    # TRADING RULES
    # ============================================
    story.append(Paragraph("11. TRADING RULES FRAMEWORK", styles['LHMSection']))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Unconditional Rules (Never Override)", styles['LHMSubsection']))
    story.append(Paragraph(
        "<b>RULE #3:</b> Never buy when underperforming BTC on 30d AND 90d. NO EXCEPTIONS.",
        styles['LHMBody']
    ))
    story.append(Paragraph(
        "<b>RULE #5:</b> Never chase when price > 15% above 50d MA. NO EXCEPTIONS.",
        styles['LHMBody']
    ))

    story.append(Spacer(1, 12))
    story.append(Paragraph("Conditional Rules (Context-Dependent)", styles['LHMSubsection']))
    story.append(Paragraph(
        "<b>RULE #1 (Below 200d MA):</b> Default no new longs. Override allowed in mature downtrend "
        "(>60 days) with 50% sizing and tight stops.",
        styles['LHMBody']
    ))
    story.append(Paragraph(
        "<b>RULE #2 (Death Cross):</b> Default no new longs. Override allowed >60 days into death cross "
        "with 50% sizing and positive relative strength.",
        styles['LHMBody']
    ))
    story.append(Paragraph(
        "<b>RULE #4 (Z-RoC < -1.0):</b> Reduce 50% minimum. Full exit if combined with other violations.",
        styles['LHMBody']
    ))

    story.append(PageBreak())

    # ============================================
    # TECHNICAL OVERLAY BOOK
    # ============================================
    story.append(Paragraph("11. TECHNICAL OVERLAY BOOK", styles['LHMSection']))
    story.append(Spacer(1, 12))

    story.append(Paragraph(
        "The Core Book is macro-driven. When MRI is elevated and the regime multiplier compresses "
        "position sizes, the Technical Overlay Book provides a structured way to participate in "
        "pure technical setups. This is not an override of macro. It's a separate, smaller allocation.",
        styles['LHMBody']
    ))
    story.append(Spacer(1, 12))

    # Portfolio structure table
    story.append(Paragraph("Portfolio Structure", styles['LHMSubsection']))
    port_data = [
        ['Book', 'Allocation', 'Approach', 'Direction'],
        ['Core Book', '70-100%', 'Macro + Fundamental + Technical', 'Long only'],
        ['Technical Overlay', '0-30%', 'Pure technical (trend + momentum)', 'Long or Short'],
    ]
    port_table = Table(port_data, colWidths=[100, 70, 160, 80])
    port_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), OCEAN_BLUE),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, DOLDRUMS_GRAY),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, LIGHT_GRAY]),
    ]))
    story.append(port_table)
    story.append(Spacer(1, 12))

    story.append(Paragraph("Activation Criteria", styles['LHMSubsection']))
    activation_points = [
        "Core Book is in defensive mode (MRI > +1.0)",
        "At least 3 clear technical setups exist (long OR short)",
        "BTC or SPX showing directional trend (not chop)",
        "You explicitly decide to activate (not automatic)",
    ]
    for point in activation_points:
        story.append(Paragraph(f"• {point}", styles['LHMBody']))

    story.append(Spacer(1, 12))
    story.append(Paragraph("Technical Book Scoring (9-Point System)", styles['LHMSubsection']))
    tech_score_data = [
        ['Component', 'Points', 'What It Measures'],
        ['Trend Structure', '0-3', 'Price vs 50d vs 200d alignment'],
        ['Momentum (Z-RoC)', '0-3', 'Direction and magnitude'],
        ['Relative Strength', '0-3', 'vs BTC (63d and 252d)'],
    ]
    tech_score_table = Table(tech_score_data, colWidths=[120, 60, 200])
    tech_score_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), OCEAN_BLUE),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, DOLDRUMS_GRAY),
    ]))
    story.append(tech_score_table)
    story.append(Paragraph("<b>Minimum score to enter: 7/9</b>", styles['LHMBody']))

    story.append(Spacer(1, 12))
    story.append(Paragraph("Position Limits & Stops", styles['LHMSubsection']))
    limits_data = [
        ['Parameter', 'Longs', 'Shorts'],
        ['Max per position', '5%', '3%'],
        ['Hard stop', '10%', '8%'],
        ['Technical stop', 'Close below 50d MA', 'Close above 50d MA'],
        ['Momentum stop', 'Z-RoC crosses below 0', 'Z-RoC crosses above 0'],
        ['Time stop', '20 trading days', '20 trading days'],
    ]
    limits_table = Table(limits_data, colWidths=[140, 120, 120])
    limits_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), OCEAN_BLUE),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, DOLDRUMS_GRAY),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, LIGHT_GRAY]),
    ]))
    story.append(limits_table)

    story.append(Spacer(1, 12))
    story.append(Paragraph("Short-Specific Requirements", styles['LHMSubsection']))
    short_points = [
        "Price < 50d < 200d (both MAs falling)",
        "Z-RoC < -1.0 (strongly negative, not just below zero)",
        "Relative strength RED on both 63d and 252d",
        "Clear breakdown, not just weakness",
        "NOT extended (price not >10% below 50d MA)",
    ]
    for point in short_points:
        story.append(Paragraph(f"• {point}", styles['LHMBody']))

    story.append(Spacer(1, 12))
    story.append(Paragraph(
        "<b>The Technical Book is NOT:</b> A way to override macro when impatient, a license to "
        "trade every setup, or a replacement for the Core Book. It's optional.",
        styles['LHMBody']
    ))

    story.append(PageBreak())

    # ============================================
    # Z-ROC INDICATOR SETTINGS
    # ============================================
    story.append(Paragraph("APPENDIX: Z-RoC Indicator Settings", styles['LHMSection']))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Recommended Parameters", styles['LHMSubsection']))
    zroc_data = [
        ['Parameter', 'Value', 'Rationale'],
        ['ROC Length', '21 days', '1 month of trading days'],
        ['Z Lookback', '252 days', '1 year for normalization'],
        ['Smoothing', '5-day EMA', '1 week, filters noise'],
        ['Robust Z', 'Yes (median/MAD)', 'Handles fat tails'],
        ['Winsorize', '±3.0', 'Caps extreme readings'],
    ]
    zroc_table = Table(zroc_data, colWidths=[100, 100, 180])
    zroc_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), OCEAN_BLUE),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, DOLDRUMS_GRAY),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, LIGHT_GRAY]),
    ]))
    story.append(zroc_table)

    story.append(Spacer(1, 12))
    story.append(Paragraph("Interpretation", styles['LHMSubsection']))
    interp_points = [
        "<b>Z-RoC > +2.0:</b> Strong momentum, overbought in context",
        "<b>Z-RoC > 0:</b> Positive momentum",
        "<b>Z-RoC < 0:</b> Negative momentum",
        "<b>Z-RoC < -1.0:</b> Momentum breakdown (exit signal for longs)",
        "<b>Z-RoC < -2.0:</b> Oversold, potential capitulation",
    ]
    for point in interp_points:
        story.append(Paragraph(f"• {point}", styles['LHMBody']))

    story.append(Spacer(1, 12))
    story.append(Paragraph("Benchmark", styles['LHMSubsection']))
    story.append(Paragraph(
        "For crypto relative strength: <b>CRYPTO30 Index</b> (Pepperstone) or CRYPTOCAP:TOTAL. "
        "BTC-weighted but provides defensible benchmark for crypto-native conversations.",
        styles['LHMBody']
    ))

    story.append(PageBreak())

    # ============================================
    # DATA VENDORS
    # ============================================
    story.append(Paragraph("14. DATA SOURCES & VENDOR INFRASTRUCTURE", styles['LHMSection']))
    story.append(Spacer(1, 12))

    vendor_data = [
        ['Vendor', 'Strength', 'Use Case', 'Priority'],
        ['Token Terminal', 'Standardized financials', 'Fundamental analysis', 'P0 - Essential'],
        ['Glassnode', 'Deep on-chain', 'Holder distribution, flows', 'P0 - Essential'],
        ['Coinglass', 'Derivatives aggregation', 'Microstructure scoring', 'P0 - Essential'],
        ['CryptoQuant', 'Exchange flows', 'Verification, alerts', 'P1 - Important'],
        ['DefiLlama', 'Free TVL data', 'TVL cross-reference', 'P1 - Important'],
        ['Messari', 'Governance', 'Token unlocks', 'P2 - Nice to Have'],
    ]

    vendor_table = Table(vendor_data, colWidths=[90, 120, 130, 80])
    vendor_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), OCEAN_BLUE),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, DOLDRUMS_GRAY),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, LIGHT_GRAY]),
    ]))
    story.append(vendor_table)

    story.append(PageBreak())

    # ============================================
    # CLOSING
    # ============================================
    story.append(Spacer(1, 100))
    story.append(Paragraph("MACRO, ILLUMINATED.", styles['LHMTitle']))
    story.append(Spacer(1, 48))

    # Accent bar
    story.append(accent_table)

    story.append(Spacer(1, 48))
    story.append(Paragraph(
        "That's our view from the Watch. Until next time, we'll be sure to keep the light on....",
        styles['LHMQuote']
    ))

    story.append(Spacer(1, 48))
    story.append(Paragraph("Bob Sheehan, CFA, CMT", styles['LHMBody']))
    story.append(Paragraph("Founder & Chief Investment Officer", styles['LHMBody']))
    story.append(Paragraph("Lighthouse Macro", styles['LHMBody']))
    story.append(Paragraph("bob@lighthousemacro.com | @LHMacro", styles['LHMBody']))

    # Build PDF
    doc.build(story, onFirstPage=add_header_footer, onLaterPages=add_header_footer)

    print(f"\n{'='*60}")
    print("PDF GENERATED SUCCESSFULLY")
    print(f"{'='*60}")
    print(f"Output: {OUTPUT_PATH}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    build_pdf()
