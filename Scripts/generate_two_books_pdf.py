#!/usr/bin/env python3
"""
Generate branded PDF for Two Books Framework
Lighthouse Macro - MACRO, ILLUMINATED.
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from datetime import datetime

# Brand Colors
OCEAN_BLUE = colors.HexColor('#2389BB')
DUSK_ORANGE = colors.HexColor('#FF6723')
SKY_BLUE = colors.HexColor('#00D4FF')
DARK_GRAY = colors.HexColor('#333333')
LIGHT_GRAY = colors.HexColor('#F5F5F5')
WHITE = colors.white

def create_header_footer(canvas, doc):
    """Add header and footer to each page"""
    canvas.saveState()

    # Header bar (Ocean Blue + Dusk Orange accent)
    canvas.setFillColor(OCEAN_BLUE)
    canvas.rect(0, letter[1] - 0.4*inch, letter[0] * 0.7, 0.4*inch, fill=1, stroke=0)
    canvas.setFillColor(DUSK_ORANGE)
    canvas.rect(letter[0] * 0.7, letter[1] - 0.4*inch, letter[0] * 0.3, 0.4*inch, fill=1, stroke=0)

    # Header text
    canvas.setFillColor(WHITE)
    canvas.setFont('Helvetica-Bold', 10)
    canvas.drawString(0.5*inch, letter[1] - 0.28*inch, "LIGHTHOUSE MACRO")
    canvas.drawRightString(letter[0] - 0.5*inch, letter[1] - 0.28*inch, "Two Books Framework")

    # Footer
    canvas.setFillColor(DARK_GRAY)
    canvas.setFont('Helvetica', 8)
    canvas.drawString(0.5*inch, 0.4*inch, f"Generated: {datetime.now().strftime('%Y-%m-%d')}")
    canvas.drawCentredString(letter[0]/2, 0.4*inch, "MACRO, ILLUMINATED.")
    canvas.drawRightString(letter[0] - 0.5*inch, 0.4*inch, f"Page {doc.page}")

    # Footer accent bar
    canvas.setFillColor(OCEAN_BLUE)
    canvas.rect(0, 0.25*inch, letter[0] * 0.7, 0.05*inch, fill=1, stroke=0)
    canvas.setFillColor(DUSK_ORANGE)
    canvas.rect(letter[0] * 0.7, 0.25*inch, letter[0] * 0.3, 0.05*inch, fill=1, stroke=0)

    canvas.restoreState()

def build_pdf():
    """Build the Two Books Framework PDF"""

    output_path = '/Users/bob/LHM/Outputs/LHM_Two_Books_Framework.pdf'
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=0.6*inch,
        leftMargin=0.6*inch,
        topMargin=0.8*inch,
        bottomMargin=0.7*inch
    )

    # Styles
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=28,
        textColor=OCEAN_BLUE,
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )

    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=14,
        textColor=DARK_GRAY,
        spaceAfter=20,
        alignment=TA_CENTER,
        fontName='Helvetica'
    )

    h1_style = ParagraphStyle(
        'H1',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=OCEAN_BLUE,
        spaceBefore=20,
        spaceAfter=12,
        fontName='Helvetica-Bold'
    )

    h2_style = ParagraphStyle(
        'H2',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=OCEAN_BLUE,
        spaceBefore=16,
        spaceAfter=8,
        fontName='Helvetica-Bold'
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontSize=10,
        textColor=DARK_GRAY,
        spaceAfter=8,
        alignment=TA_JUSTIFY,
        fontName='Helvetica',
        leading=14
    )

    italic_style = ParagraphStyle(
        'Italic',
        parent=body_style,
        fontName='Helvetica-Oblique',
        textColor=OCEAN_BLUE
    )

    bullet_style = ParagraphStyle(
        'Bullet',
        parent=body_style,
        leftIndent=20,
        bulletIndent=10,
        spaceAfter=4
    )

    # Build content
    story = []

    # Title Page
    story.append(Spacer(1, 1.5*inch))
    story.append(Paragraph("THE TWO BOOKS", title_style))
    story.append(Paragraph("FRAMEWORK", title_style))
    story.append(Spacer(1, 0.3*inch))

    # Accent bar
    accent_table = Table([['']], colWidths=[4*inch])
    accent_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), OCEAN_BLUE),
        ('LINEBELOW', (0, 0), (0, 0), 4, DUSK_ORANGE),
    ]))
    story.append(accent_table)

    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("Core Book & Technical Overlay Book", subtitle_style))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph(
        '"Entry logic determines how you get in.<br/>Price and drivers determine how long you stay."',
        italic_style
    ))
    story.append(Spacer(1, 1*inch))
    story.append(Paragraph("Lighthouse Macro", subtitle_style))
    story.append(Paragraph("Version 1.0 | January 2026", subtitle_style))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("Bob Sheehan, CFA, CMT<br/>Founder & Chief Investment Officer", body_style))

    story.append(PageBreak())

    # Philosophy
    story.append(Paragraph("PHILOSOPHY", h1_style))
    story.append(Paragraph(
        "True global macro is directional, not directionally constrained. Soros didn't break the Bank of England "
        "by being too bullish on the UK's currency. He shorted the shit out of the pound. We are directional macro, "
        "not relative value. We have views. In a world where prices go up most of the time, our bias will be towards "
        "owning as opposed to shorting. The framework accommodates wherever the thesis takes us: long or short.",
        body_style
    ))
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph(
        "The distinction between the two books isn't about direction or duration. It's about what drives the position:",
        body_style
    ))
    story.append(Paragraph("• <b>Core Book:</b> Position follows a macro/fundamental thesis", bullet_style))
    story.append(Paragraph("• <b>Technical Overlay:</b> Position follows price structure alone", bullet_style))
    story.append(Spacer(1, 0.15*inch))
    story.append(Paragraph(
        "<b>Critical Insight:</b> The books are entry frameworks, not holding period constraints. "
        "The moment you own something, you're managing a position. Entry logic determines how you get in. "
        "Price and drivers determine how long you stay.",
        body_style
    ))

    # Portfolio Structure
    story.append(Paragraph("PORTFOLIO STRUCTURE", h1_style))

    structure_data = [
        ['', 'CORE BOOK', 'TECHNICAL OVERLAY'],
        ['Allocation', '50-100%', '0-50%'],
        ['Driver', 'Macro/Fundamental thesis', 'Price structure'],
        ['Direction', 'Long or short', 'Long or short'],
        ['Max Position', '20%', '10% (longs), 5% (shorts)'],
        ['Scoring', '24-point system', '12-point system'],
        ['Stops', 'Dual (Thesis + Price)', 'Price only (tighter)'],
        ['When Active', 'Always available', 'When Core is defensive'],
    ]

    structure_table = Table(structure_data, colWidths=[1.5*inch, 2.5*inch, 2.5*inch])
    structure_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), OCEAN_BLUE),
        ('TEXTCOLOR', (0, 0), (-1, 0), WHITE),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, OCEAN_BLUE),
        ('BACKGROUND', (0, 1), (0, -1), LIGHT_GRAY),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('ROWBACKGROUNDS', (1, 1), (-1, -1), [WHITE, LIGHT_GRAY]),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(structure_table)

    story.append(PageBreak())

    # Core Book
    story.append(Paragraph("CORE BOOK", h1_style))
    story.append(Paragraph(
        "The Core Book requires convergence across the three-engine framework. Single-engine signals "
        "are insufficient; we require convergence for high-conviction positioning.",
        body_style
    ))

    story.append(Paragraph("Three-Engine Framework", h2_style))

    engine_data = [
        ['Engine', 'Focus', 'Key Question'],
        ['Macro Dynamics', 'Pillars 1-7', 'What is the fundamental thesis?'],
        ['Monetary Mechanics', 'Pillars 8-10', 'Is liquidity supportive or restrictive?'],
        ['Market Structure', 'Pillars 11-12', 'Is price confirming the thesis?'],
    ]

    engine_table = Table(engine_data, colWidths=[1.8*inch, 1.8*inch, 2.9*inch])
    engine_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), OCEAN_BLUE),
        ('TEXTCOLOR', (0, 0), (-1, 0), WHITE),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, OCEAN_BLUE),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(engine_table)

    story.append(Paragraph("Position Sizing", h2_style))
    story.append(Paragraph(
        "<b>Formula:</b> Position Size = Base Weight × Conviction Multiplier × Regime Multiplier",
        body_style
    ))

    tier_data = [
        ['Conviction Tier', 'Score', 'Base Weight'],
        ['Tier 1 (High Conviction)', '16-19 pts', '20%'],
        ['Tier 2 (Standard)', '12-15 pts', '12%'],
        ['Tier 3 (Reduced)', '8-11 pts', '7%'],
        ['Tier 4 (Avoid)', '<8 pts', '0%'],
    ]

    tier_table = Table(tier_data, colWidths=[2.2*inch, 1.5*inch, 1.5*inch])
    tier_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), OCEAN_BLUE),
        ('TEXTCOLOR', (0, 0), (-1, 0), WHITE),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, OCEAN_BLUE),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(tier_table)
    story.append(Spacer(1, 0.15*inch))

    regime_data = [
        ['MRI Regime', 'Multiplier'],
        ['Supportive (< +0.5)', '1.0x'],
        ['Neutral (+0.5 to +1.0)', '0.6x'],
        ['Restrictive (> +1.0)', '0.3x'],
    ]

    regime_table = Table(regime_data, colWidths=[2.5*inch, 1.5*inch])
    regime_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), OCEAN_BLUE),
        ('TEXTCOLOR', (0, 0), (-1, 0), WHITE),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, OCEAN_BLUE),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(regime_table)

    story.append(Paragraph("Dual Stop System", h2_style))
    story.append(Paragraph("Every Core Book position has TWO stops. Use whichever triggers first.", body_style))
    story.append(Paragraph("• <b>Thesis Stop:</b> Fundamental invalidation (regime shift, indicator breach, catalyst failure)", bullet_style))
    story.append(Paragraph("• <b>Price Stop:</b> Technical invalidation (200d break, Z-RoC < -1.0, 15% drawdown)", bullet_style))

    story.append(PageBreak())

    # Technical Overlay Book
    story.append(Paragraph("TECHNICAL OVERLAY BOOK", h1_style))
    story.append(Paragraph(
        "When the Core Book is defensive (MRI > +1.0) and regime multipliers compress position sizes, "
        "clear technical trends can still exist. The Technical Overlay Book provides a structured way to "
        "follow price when macro is uncertain but trends are evident.",
        body_style
    ))
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph(
        "<b>This is not shorter-term trading.</b> Price trends can last years to decades. "
        "The distinction is about drivers, not duration.",
        body_style
    ))

    story.append(Paragraph("Activation Criteria", h2_style))
    story.append(Paragraph("All conditions must be met:", body_style))
    story.append(Paragraph("• Core Book is in defensive mode (MRI > +1.0)", bullet_style))
    story.append(Paragraph("• At least 3 clear technical setups exist (long OR short)", bullet_style))
    story.append(Paragraph("• BTC or SPX showing directional trend (not chop)", bullet_style))
    story.append(Paragraph("• You explicitly decide to activate (not automatic)", bullet_style))

    story.append(Paragraph("12-Point Scoring System", h2_style))
    story.append(Paragraph("Three components, 4 points each. Clean 2:1 ratio to Core Book's 24 points.", body_style))

    scoring_data = [
        ['Component', 'Points', 'What It Measures'],
        ['Trend Structure', '0-4', 'Price vs 50d vs 200d alignment + slope'],
        ['Momentum (Z-RoC)', '0-4', 'Direction, magnitude, and trajectory'],
        ['Relative Strength', '0-4', 'vs BTC/SPX (multiple timeframes + slope)'],
    ]

    scoring_table = Table(scoring_data, colWidths=[1.8*inch, 1*inch, 3.5*inch])
    scoring_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), OCEAN_BLUE),
        ('TEXTCOLOR', (0, 0), (-1, 0), WHITE),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, OCEAN_BLUE),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(scoring_table)
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph("<b>Minimum score to enter: 8/12</b>", body_style))

    story.append(Paragraph("Position Limits & Stops", h2_style))

    limits_data = [
        ['Parameter', 'Longs', 'Shorts'],
        ['Max per position', '10%', '5%'],
        ['Hard stop', '10%', '8%'],
        ['Technical stop', 'Close below 50d MA', 'Close above 50d MA'],
        ['Momentum stop', 'Z-RoC crosses below 0', 'Z-RoC crosses above 0'],
        ['Time stop', '20 trading days', '20 trading days'],
    ]

    limits_table = Table(limits_data, colWidths=[2*inch, 2.2*inch, 2.2*inch])
    limits_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), OCEAN_BLUE),
        ('TEXTCOLOR', (0, 0), (-1, 0), WHITE),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, OCEAN_BLUE),
        ('BACKGROUND', (0, 1), (0, -1), LIGHT_GRAY),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(limits_table)

    story.append(Paragraph("Short-Specific Requirements", h2_style))
    story.append(Paragraph("Shorts have additional hurdles (all must be true):", body_style))
    story.append(Paragraph("• Price < 50d < 200d (both MAs falling)", bullet_style))
    story.append(Paragraph("• Z-RoC < -1.0 (strongly negative, not just below zero)", bullet_style))
    story.append(Paragraph("• Relative strength RED on both 63d and 252d", bullet_style))
    story.append(Paragraph("• Clear breakdown (not just weakness)", bullet_style))
    story.append(Paragraph("• NOT extended (price not >10% below 50d MA)", bullet_style))

    story.append(PageBreak())

    # Position Graduation
    story.append(Paragraph("POSITION GRADUATION", h1_style))
    story.append(Paragraph(
        "A Technical Book position can graduate to Core Book treatment when fundamental drivers emerge. "
        "This is the key insight: the books are entry frameworks, not permanent classifications.",
        body_style
    ))

    story.append(Paragraph("Technical Entry → Fundamental Confirmation", h2_style))
    story.append(Paragraph("1. Enter position in Technical Book (pure price-driven)", bullet_style))
    story.append(Paragraph("2. Hold for 3 months following trend", bullet_style))
    story.append(Paragraph("3. Macro regime shifts, MRI improves", bullet_style))
    story.append(Paragraph("4. Fundamental catalyst emerges for the position", bullet_style))
    story.append(Paragraph("5. The position now has both engines firing", bullet_style))
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph(
        "<b>Action:</b> The position graduates. Size up to Core Book weights if conviction supports. "
        "Shift to Core Book stop framework. Extend holding period expectation.",
        body_style
    ))

    story.append(Paragraph("Core Entry → Macro Uncertainty", h2_style))
    story.append(Paragraph("1. Enter position in Core Book (thesis-driven)", bullet_style))
    story.append(Paragraph("2. Thesis plays out partially", bullet_style))
    story.append(Paragraph("3. MRI deteriorates, Core Book goes defensive", bullet_style))
    story.append(Paragraph("4. Position still has strong technical structure", bullet_style))
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph(
        "<b>Action:</b> The position can remain, but sizing governed by Technical Book limits. "
        "Stops tighten to Technical Book framework. Monitor for thesis repair or technical breakdown.",
        body_style
    ))

    # Absolute Rules
    story.append(Paragraph("ABSOLUTE RULES (BOTH BOOKS)", h1_style))

    rules_data = [
        ['Rule', 'Condition', 'Override'],
        ['#1: Below 200d', 'Price < 200d MA', 'Conditional (>60d allows tactical)'],
        ['#2: Death Cross', '50d < 200d', 'Conditional (>60d allows tactical)'],
        ['#3: Red Relative', 'Underperforming benchmark', 'UNCONDITIONAL - NEVER'],
        ['#4: Z-RoC Broken', 'Z-RoC < -1.0 (longs)', 'Reduce 50% min, full exit if combined'],
        ['#5: Extended', '>15% above 50d MA', 'UNCONDITIONAL - NEVER CHASE'],
    ]

    rules_table = Table(rules_data, colWidths=[1.5*inch, 2*inch, 2.8*inch])
    rules_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), OCEAN_BLUE),
        ('TEXTCOLOR', (0, 0), (-1, 0), WHITE),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, OCEAN_BLUE),
        ('BACKGROUND', (0, 3), (-1, 3), colors.HexColor('#FFE0E0')),
        ('BACKGROUND', (0, 5), (-1, 5), colors.HexColor('#FFE0E0')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(rules_table)

    story.append(PageBreak())

    # What the Books Are NOT
    story.append(Paragraph("WHAT THE BOOKS ARE NOT", h1_style))

    story.append(Paragraph("The Technical Overlay Book is NOT:", h2_style))
    story.append(Paragraph("• A way to override macro when impatient", bullet_style))
    story.append(Paragraph("• A license to trade every setup", bullet_style))
    story.append(Paragraph("• A replacement for the Core Book", bullet_style))
    story.append(Paragraph("• Active all the time", bullet_style))
    story.append(Paragraph("• An excuse to ignore MRI signals", bullet_style))

    story.append(Paragraph("The Core Book is NOT:", h2_style))
    story.append(Paragraph("• Long only (true global macro is directional)", bullet_style))
    story.append(Paragraph("• Restricted to 3-6 month holds (that's catalyst horizon, not exit requirement)", bullet_style))
    story.append(Paragraph("• Blind to price (technicals confirm the thesis)", bullet_style))

    # Closing
    story.append(Spacer(1, 0.5*inch))
    story.append(HRFlowable(width="80%", thickness=2, color=OCEAN_BLUE, spaceBefore=10, spaceAfter=20))

    closing_style = ParagraphStyle(
        'Closing',
        parent=body_style,
        alignment=TA_CENTER,
        fontSize=12,
        textColor=OCEAN_BLUE,
        fontName='Helvetica-Oblique'
    )

    story.append(Paragraph(
        "The books are entry taxonomies, not duration boxes.<br/>"
        "Entry logic determines how you get in.<br/>"
        "Price and drivers determine how long you stay.",
        closing_style
    ))

    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("MACRO, ILLUMINATED.", title_style))

    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph(
        "That's our view from the Watch. Until next time, we'll be sure to keep the light on....",
        italic_style
    ))

    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph(
        "Bob Sheehan, CFA, CMT<br/>"
        "Founder & Chief Investment Officer<br/>"
        "Lighthouse Macro<br/>"
        "bob@lighthousemacro.com | @LHMacro",
        body_style
    ))

    # Build PDF
    doc.build(story, onFirstPage=create_header_footer, onLaterPages=create_header_footer)
    print(f"PDF generated: {output_path}")
    return output_path

if __name__ == "__main__":
    build_pdf()
