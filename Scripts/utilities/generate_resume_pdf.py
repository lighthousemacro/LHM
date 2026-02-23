#!/usr/bin/env python3
"""Generate Bob Sheehan's resume as PDF using reportlab."""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

# Colors
OCEAN = HexColor('#2389BB')
DARK = HexColor('#1a1a1a')
GRAY = HexColor('#444444')

def create_resume():
    doc = SimpleDocTemplate(
        "/Users/bob/Bob_Sheehan_Resume.pdf",
        pagesize=letter,
        rightMargin=0.5*inch,
        leftMargin=0.5*inch,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch
    )

    # Styles
    styles = {
        'name': ParagraphStyle(
            'name',
            fontName='Helvetica-Bold',
            fontSize=16,
            textColor=DARK,
            alignment=TA_CENTER,
            spaceAfter=2
        ),
        'contact': ParagraphStyle(
            'contact',
            fontName='Helvetica',
            fontSize=9,
            textColor=GRAY,
            alignment=TA_CENTER,
            spaceAfter=10
        ),
        'section': ParagraphStyle(
            'section',
            fontName='Helvetica-Bold',
            fontSize=11,
            textColor=OCEAN,
            spaceBefore=12,
            spaceAfter=6,
            borderPadding=(0, 0, 2, 0)
        ),
        'job_title': ParagraphStyle(
            'job_title',
            fontName='Helvetica-Bold',
            fontSize=10,
            textColor=DARK,
            spaceBefore=6,
            spaceAfter=1
        ),
        'job_company': ParagraphStyle(
            'job_company',
            fontName='Helvetica-Oblique',
            fontSize=9,
            textColor=GRAY,
            spaceAfter=4
        ),
        'body': ParagraphStyle(
            'body',
            fontName='Helvetica',
            fontSize=9,
            textColor=DARK,
            alignment=TA_JUSTIFY,
            spaceAfter=4,
            leading=12
        ),
        'bullet': ParagraphStyle(
            'bullet',
            fontName='Helvetica',
            fontSize=9,
            textColor=DARK,
            leftIndent=12,
            spaceAfter=2,
            leading=11
        ),
        'skills': ParagraphStyle(
            'skills',
            fontName='Helvetica',
            fontSize=9,
            textColor=DARK,
            spaceAfter=3,
            leading=11
        )
    }

    story = []

    # Header
    story.append(Paragraph("Bob Sheehan, CFA, CMT", styles['name']))
    story.append(Paragraph("Macro Strategist | Investment Analyst | Data Scientist", styles['contact']))
    story.append(Paragraph(
        "240-672-7418 | bob@lighthousemacro.com | linkedin.com/in/bob-sheehan-cfa-cmt | LighthouseMacro.com | @LHMacro",
        styles['contact']
    ))

    # Profile
    story.append(Paragraph("PROFILE", styles['section']))
    story.append(Paragraph(
        "Macro Strategist & Investment Analyst with track record managing multi-asset portfolios ($4.5B AUM) and co-managing "
        "a $1B large cap equity strategy that outperformed the S&P 500 by 719 bps annualized (2.35 Sortino, 103% upside capture, "
        "76% downside). Built institutional-grade research infrastructure combining systematic macro analysis with quantitative "
        "frameworks. Known for:",
        styles['body']
    ))

    bullets = [
        "Building proprietary macro indicators and risk models that translate economic data into actionable investment signals",
        "Developing systematic frameworks for position sizing, regime detection, and recession probability estimation",
        "Delivering research to institutional clients including hedge funds, asset managers, and family offices",
        "Chartered Financial Analyst (CFA) & Chartered Market Technician (CMT)"
    ]
    for b in bullets:
        story.append(Paragraph(f"<bullet>&bull;</bullet> {b}", styles['bullet']))

    # Core Competencies
    story.append(Paragraph("CORE COMPETENCIES & TECHNICAL SKILLS", styles['section']))
    story.append(Paragraph(
        "<b>Investment:</b> Global Macro, Portfolio Management, Asset Allocation, Risk Management, Technical Analysis, "
        "Equity Research, Cross-Asset Trading",
        styles['skills']
    ))
    story.append(Paragraph(
        "<b>Quantitative:</b> Python, SQL, Statistical Analysis, Machine Learning, Time Series Forecasting, Factor Models, "
        "Regime Detection",
        styles['skills']
    ))
    story.append(Paragraph(
        "<b>Platforms:</b> Bloomberg, FactSet, TradingView, Refinitiv, CoinGlass, DefiLlama, Token Terminal",
        styles['skills']
    ))

    # Experience
    story.append(Paragraph("PROFESSIONAL EXPERIENCE", styles['section']))

    jobs = [
        {
            'title': 'Founder & Chief Investment Officer',
            'dates': 'Apr 2024 - Present',
            'company': 'Lighthouse Macro | New York, NY (Remote)',
            'bullets': [
                "Built institutional macro research platform serving hedge funds, family offices, and allocators with systematic, data-driven analysis",
                "Developed 12-pillar diagnostic framework (The Diagnostic Dozen) covering labor, prices, growth, housing, consumer, business, trade, fiscal, credit, liquidity, market structure, and sentiment",
                "Created 41 proprietary composite indicators including Macro Risk Index (MRI), Labor Fragility Index (LFI), Liquidity Cushion Index (LCI), and Credit-Labor Gap (CLG)",
                "Built recession probability model and early warning system synthesizing leading indicators across macro, credit, and liquidity domains",
                "Engineered analytical database with 1.78M observations across 1,094 series from 5+ institutional data sources",
                "Designed conviction-weighted position sizing framework with regime-based allocation (3-10 concentrated positions, 7-20% sizing)",
                "Extended framework to crypto with 24-point scoring system for protocol fundamentals, technicals, and microstructure"
            ]
        },
        {
            'title': 'Vice President, Market Strategy & Research',
            'dates': 'Apr 2025 - Sep 2025',
            'company': 'EquiLend | New York, NY',
            'bullets': [
                "Led market strategy and research for Data & Analytics team at leading securities finance technology provider",
                "Produced market analysis on securities lending dynamics, including lockup expiration impact studies (CRWV, CRCL)",
                "Identified critical warning signals in borrowing metrics ahead of volatility events (CRWV peak: 44,324 bps)"
            ]
        },
        {
            'title': 'Senior Domain Expert | Economics & Finance',
            'dates': 'Nov 2025 - Present',
            'company': 'Mercor Intelligence | New York, NY (Contract)',
            'bullets': [
                "Providing domain expertise in economics, finance, investments, and portfolio management to improve AI models for leading AI research lab"
            ]
        },
        {
            'title': 'Senior Research Analyst',
            'dates': 'Jul 2024 - Feb 2025',
            'company': 'Strom Capital Management LLC | New York, NY',
            'bullets': [
                "Conducted macro research and technical analysis in direct collaboration with Founder & CIO for discretionary global macro fund",
                "Developed data science solutions to identify trading opportunities; authored investor communications"
            ]
        },
        {
            'title': 'Institutional Research Sales',
            'dates': 'Nov 2021 - Jul 2022',
            'company': 'Trahan Macro Research | New York, NY',
            'bullets': [
                "Delivered macro and quantitative research to leading hedge funds, pension funds, and asset managers"
            ]
        },
        {
            'title': 'AVP, Associate Portfolio Manager',
            'dates': 'Jul 2015 - Jun 2021',
            'company': 'Bank of America Private Bank | New York, NY',
            'bullets': [
                "Dual mandate: global multi-asset portfolios ($4.5B AUM) and Strategic Growth Strategy ($1B AUM large cap equity)",
                "SGS outperformed S&P 500 by 719 bps annualized (21.7% vs 14.5%) with 2.35 Sortino, 103% upside capture, 76% downside",
                "Led team's macro research and technical analysis efforts informing portfolio strategy and trading decisions",
                "Presented investment commentary and portfolio updates to technical and non-technical stakeholders"
            ]
        }
    ]

    for job in jobs:
        # Title and dates on same line
        title_table = Table(
            [[Paragraph(job['title'], styles['job_title']),
              Paragraph(job['dates'], ParagraphStyle('dates', fontName='Helvetica', fontSize=9, textColor=GRAY, alignment=2))]],
            colWidths=[4.5*inch, 2.5*inch]
        )
        title_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ]))
        story.append(title_table)
        story.append(Paragraph(job['company'], styles['job_company']))

        for b in job['bullets']:
            story.append(Paragraph(f"<bullet>&bull;</bullet> {b}", styles['bullet']))

    # Education
    story.append(Paragraph("EDUCATION", styles['section']))

    edu = [
        ('BrainStation | Diploma, Data Science', 'Apr 2024 - Jul 2024'),
        ('Providence College | B.S. Finance, Minor in Economics', 'Sep 2011 - May 2015')
    ]

    for school, dates in edu:
        edu_table = Table(
            [[Paragraph(f"<b>{school}</b>", styles['skills']),
              Paragraph(dates, ParagraphStyle('dates', fontName='Helvetica', fontSize=9, textColor=GRAY, alignment=2))]],
            colWidths=[5*inch, 2*inch]
        )
        edu_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ]))
        story.append(edu_table)

    story.append(Paragraph("Division 1 Men's Lacrosse, 4x Big East All-Academic, Chi Alpha Sigma National Honor Society", styles['bullet']))

    doc.build(story)
    print("Resume saved to: /Users/bob/Bob_Sheehan_Resume.pdf")

if __name__ == "__main__":
    create_resume()
