"""
Build "Lighthouse Macro's Crypto Liquidity Impulse (CLI)" PDF
Public-safe version for external distribution (February 2026)
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Image,
                                 HRFlowable, Table, TableStyle, PageBreak)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

# =============================================================================
# CONFIG
# =============================================================================
CHART_DIR = '/Users/bob/LHM/Outputs/BTC_Drivers/white'
OUT_PDF = '/Users/bob/LHM/Outputs/BTC_Drivers/CLI_Crypto_Liquidity_Impulse.pdf'

OCEAN = HexColor('#2389BB')
DUSK = HexColor('#FF6723')
GRAY = HexColor('#898989')
BLACK = HexColor('#1a1a1a')
WHITE = HexColor('#ffffff')
FOG = HexColor('#D1D1D1')

try:
    pdfmetrics.registerFont(TTFont('Montserrat-Bold', '/System/Library/Fonts/Supplemental/Arial Bold.ttf'))
    pdfmetrics.registerFont(TTFont('Inter', '/System/Library/Fonts/Supplemental/Arial.ttf'))
    TITLE_FONT = 'Montserrat-Bold'
    BODY_FONT = 'Inter'
except:
    TITLE_FONT = 'Helvetica-Bold'
    BODY_FONT = 'Helvetica'

# =============================================================================
# STYLES
# =============================================================================
def make_styles():
    s = {}
    s['title'] = ParagraphStyle('title', fontName=TITLE_FONT, fontSize=22,
                                 textColor=BLACK, leading=28, spaceAfter=4,
                                 alignment=TA_CENTER)
    s['subtitle'] = ParagraphStyle('subtitle', fontName=BODY_FONT, fontSize=11,
                                    textColor=OCEAN, leading=14, spaceAfter=16,
                                    alignment=TA_CENTER)
    s['h1'] = ParagraphStyle('h1', fontName=TITLE_FONT, fontSize=16,
                              textColor=BLACK, leading=22, spaceBefore=18, spaceAfter=10)
    s['h2'] = ParagraphStyle('h2', fontName=TITLE_FONT, fontSize=13,
                              textColor=OCEAN, leading=17, spaceBefore=12, spaceAfter=6)
    s['body'] = ParagraphStyle('body', fontName=BODY_FONT, fontSize=10.5,
                                textColor=BLACK, leading=15, alignment=TA_JUSTIFY,
                                spaceAfter=8)
    s['bullet'] = ParagraphStyle('bullet', fontName=BODY_FONT, fontSize=10.5,
                                  textColor=BLACK, leading=15, alignment=TA_JUSTIFY,
                                  spaceAfter=4, leftIndent=18, bulletIndent=6)
    s['caption'] = ParagraphStyle('caption', fontName=BODY_FONT, fontSize=9,
                                   textColor=GRAY, alignment=TA_CENTER,
                                   leading=12, spaceAfter=12, spaceBefore=4)
    s['disclosure'] = ParagraphStyle('disclosure', fontName=BODY_FONT, fontSize=9.5,
                                      textColor=GRAY, leading=13, alignment=TA_JUSTIFY,
                                      spaceAfter=6)
    s['bio'] = ParagraphStyle('bio', fontName=BODY_FONT, fontSize=9,
                               textColor=GRAY, leading=12, spaceAfter=4)
    s['table_header'] = ParagraphStyle('th', fontName=TITLE_FONT, fontSize=9.5,
                                        textColor=WHITE, leading=13, alignment=TA_CENTER)
    s['table_cell'] = ParagraphStyle('tc', fontName=BODY_FONT, fontSize=9,
                                      textColor=BLACK, leading=12, alignment=TA_CENTER)
    s['table_cell_left'] = ParagraphStyle('tcl', fontName=BODY_FONT, fontSize=9,
                                           textColor=BLACK, leading=12, alignment=TA_LEFT)
    s['table_cell_bold'] = ParagraphStyle('tcb', fontName=TITLE_FONT, fontSize=9,
                                           textColor=BLACK, leading=12, alignment=TA_CENTER)
    return s


def build_pdf():
    s = make_styles()

    def draw_page(canvas, doc):
        w, h = letter
        margin = 0.85 * inch
        bar_h = 4
        bar_w = w - 2 * margin

        # Top accent bar
        bar_y = h - 0.45 * inch
        canvas.setFillColor(OCEAN)
        canvas.rect(margin, bar_y, bar_w * 0.67, bar_h, fill=1, stroke=0)
        canvas.setFillColor(DUSK)
        canvas.rect(margin + bar_w * 0.67, bar_y, bar_w * 0.33, bar_h, fill=1, stroke=0)

        # Header
        canvas.setFillColor(OCEAN)
        canvas.setFont(TITLE_FONT, 11)
        canvas.drawString(margin, bar_y + 10, 'LIGHTHOUSE MACRO')
        canvas.setFillColor(GRAY)
        canvas.setFont(BODY_FONT, 10)
        canvas.drawRightString(w - margin, bar_y + 10, 'February 2026')

        # Bottom accent bar
        bot_y = 0.45 * inch
        canvas.setFillColor(OCEAN)
        canvas.rect(margin, bot_y, bar_w * 0.67, bar_h, fill=1, stroke=0)
        canvas.setFillColor(DUSK)
        canvas.rect(margin + bar_w * 0.67, bot_y, bar_w * 0.33, bar_h, fill=1, stroke=0)

        # Footer
        canvas.setFillColor(GRAY)
        canvas.setFont(BODY_FONT, 8)
        canvas.drawString(margin, bot_y - 12,
                          'Bob Sheehan, CFA, CMT | Lighthouse Macro | LighthouseMacro.com | @LHMacro')
        canvas.setFillColor(OCEAN)
        canvas.setFont(TITLE_FONT, 9)
        canvas.drawRightString(w - margin, bot_y - 12, 'MACRO, ILLUMINATED.')

    doc = SimpleDocTemplate(
        OUT_PDF, pagesize=letter,
        leftMargin=0.85*inch, rightMargin=0.85*inch,
        topMargin=0.9*inch, bottomMargin=0.8*inch
    )

    story = []
    W = doc.width
    body = s['body']
    bullet = s['bullet']

    story.append(Spacer(1, 8))

    # Title
    story.append(Paragraph("Lighthouse Macro's<br/>Crypto Liquidity Impulse (CLI)", s['title']))
    story.append(Paragraph('Bob Sheehan, CFA, CMT | Lighthouse Macro', s['subtitle']))

    # --- WHAT IT IS ---
    story.append(Paragraph('What It Is', s['h1']))
    story.append(Paragraph(
        'A weighted z-score composite measuring how fast global liquidity transmits into crypto. '
        'Positive CLI = expanding liquidity impulse. Negative = contracting. '
        '"Impulse" (not "Flow") because the indicator measures rate of change (second derivative), not cumulative direction.',
        body))

    # --- ARCHITECTURE ---
    story.append(Paragraph('Architecture: Three Tiers, Eight Components', s['h1']))

    # Tier 1
    story.append(Paragraph('Tier 1: Macro Liquidity Tide (40% conceptual weight, 11-13 week lead)', s['h2']))
    story.append(Paragraph(
        'Captures the global liquidity backdrop that sets the direction for all risk assets.',
        body))
    story.append(Paragraph(
        '<bullet>&bull;</bullet><b>Global M2 Momentum:</b> Year-over-year change in broad global money supply. '
        'Empirical research on global liquidity transmission shows ~40% of Bitcoin\'s systematic price variance '
        'traces to global liquidity conditions, with Granger causality peaking at weeks 11-13.',
        bullet))
    story.append(Paragraph(
        '<bullet>&bull;</bullet><b>Dollar Direction:</b> Rate of change in the trade-weighted dollar. '
        'Dollar peaks align with BTC cycle bottoms. Captures global risk appetite and capital flow dynamics.',
        bullet))

    # Tier 2
    story.append(Paragraph('Tier 2: US Plumbing Mechanics (35% conceptual weight, 1-6 week lead)', s['h2']))
    story.append(Paragraph(
        'Maps the internal plumbing of the US financial system, where most crypto liquidity originates.',
        body))
    story.append(Paragraph(
        '<bullet>&bull;</bullet><b>Fed Balance Sheet (WALCL):</b> Weekly changes in the Fed\'s balance sheet as a proxy for aggregate liquidity supply.',
        bullet))
    story.append(Paragraph(
        '<bullet>&bull;</bullet><b>TGA Drawdown/Buildup Rate:</b> Treasury General Account movements directly affect bank reserves and available liquidity.',
        bullet))
    story.append(Paragraph(
        '<bullet>&bull;</bullet><b>RRP Facility Balance:</b> Reverse repo as a liquidity buffer. Post-depletion (effectively zero in 2025), '
        'TGA rebuilds hit bank reserves directly. A regime change most net-liquidity trackers haven\'t internalized.',
        bullet))
    story.append(Paragraph(
        '<bullet>&bull;</bullet><b>SOFR-IORB Spread:</b> Wholesale funding stress indicator. Widening signals plumbing strain.',
        bullet))
    story.append(Paragraph(
        '<bullet>&bull;</bullet><b>HY OAS (Inverted):</b> Credit conditions as a transmission channel. Tight spreads = risk-on = supportive for crypto.',
        bullet))

    # Tier 3
    story.append(Paragraph('Tier 3: Crypto-Native Transmission (25% conceptual weight, 0-2 week lead)', s['h2']))
    story.append(Paragraph(
        'Captures the channels through which macro liquidity actually reaches crypto markets.',
        body))
    story.append(Paragraph(
        '<bullet>&bull;</bullet><b>Stablecoin Supply Momentum:</b> Rate of change in aggregate stablecoin market cap (USDT + USDC). '
        '95% contemporaneous correlation with BTC (Bitcoin Magazine Pro).',
        bullet))
    story.append(Paragraph(
        '<bullet>&bull;</bullet><b>BTC ETF Net Flows (20d):</b> FalconX Research: F-statistic 8.48, p = 0.004 for Granger causality. '
        'With US spot Bitcoin ETFs holding ~1.3M BTC (~7% of total supply), this channel is no longer marginal.',
        bullet))
    story.append(Paragraph(
        '<bullet>&bull;</bullet><b>Exchange Stablecoin Reserves:</b> On-chain capital sitting on exchange, ready to deploy.',
        bullet))

    # Leverage filter
    story.append(Paragraph('Leverage Regime Filter', s['h2']))
    story.append(Paragraph(
        'Perpetual futures funding rates applied as a multiplicative overlay after composite calculation. '
        'Captures the ~17% of time when crypto positioning dynamics override macro liquidity trends.',
        body))

    # --- METHODOLOGY ---
    story.append(Paragraph('Methodology', s['h1']))
    story.append(Paragraph(
        '<bullet>&bull;</bullet>Z-score normalization across all components', bullet))
    story.append(Paragraph(
        '<bullet>&bull;</bullet>Expanding window with outlier management', bullet))
    story.append(Paragraph(
        '<bullet>&bull;</bullet>Composite = weighted sum of component z-scores', bullet))
    story.append(Paragraph(
        '<bullet>&bull;</bullet>Positive CLI = expanding liquidity impulse; Negative = contracting', bullet))

    # --- BACKTEST RESULTS ---
    story.append(Paragraph('Backtest Results', s['h1']))
    story.append(Paragraph('Sample: 2018-2025 (~2,850-2,900 daily observations)', body))

    # Quintile table
    story.append(Paragraph('Quintile Sort: CLI Quintile to Forward BTC Returns', s['h2']))

    th = s['table_header']
    tc = s['table_cell']
    tcb = s['table_cell_bold']

    quintile_data = [
        [Paragraph('Horizon', th), Paragraph('Q1<br/>(Weakest)', th), Paragraph('Q2', th),
         Paragraph('Q3', th), Paragraph('Q4', th), Paragraph('Q5<br/>(Strongest)', th),
         Paragraph('Q5-Q1<br/>Spread', th), Paragraph('t-stat', th), Paragraph('p-value', th)],
        [Paragraph('21D', tc), Paragraph('-4.8%', tc), Paragraph('+0.5%', tc),
         Paragraph('+1.0%', tc), Paragraph('+2.0%', tc), Paragraph('+8.6%', tc),
         Paragraph('<b>+13.4%</b>', tc), Paragraph('14.2', tc), Paragraph('&lt;0.0001', tc)],
        [Paragraph('42D', tc), Paragraph('-7.8%', tc), Paragraph('-0.2%', tc),
         Paragraph('+3.9%', tc), Paragraph('+6.0%', tc), Paragraph('+14.3%', tc),
         Paragraph('<b>+22.1%</b>', tc), Paragraph('15.6', tc), Paragraph('&lt;0.0001', tc)],
        [Paragraph('63D', tc), Paragraph('-9.8%', tc), Paragraph('-2.1%', tc),
         Paragraph('+9.0%', tc), Paragraph('+11.1%', tc), Paragraph('+17.2%', tc),
         Paragraph('<b>+27.0%</b>', tc), Paragraph('15.0', tc), Paragraph('&lt;0.0001', tc)],
    ]

    col_w = [W*0.09, W*0.10, W*0.08, W*0.08, W*0.08, W*0.11, W*0.11, W*0.09, W*0.10]
    # Make sure widths don't exceed W
    t = Table(quintile_data, colWidths=col_w)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), OCEAN),
        ('TEXTCOLOR', (0, 0), (-1, 0), WHITE),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, FOG),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [WHITE, HexColor('#f5f9fc')]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t)
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        '<b>Monotonic at all horizons.</b> Every step up in CLI corresponds to higher forward returns. All p &lt; 0.0001.',
        body))

    # Slugging table
    story.append(Paragraph('Slugging Percentage (Win Size Ratio)', s['h2']))

    slug_data = [
        [Paragraph('Horizon', th), Paragraph('Q1 Slugging', th), Paragraph('Q5 Slugging', th)],
        [Paragraph('21D', tc), Paragraph('0.45x', tc), Paragraph('4.81x', tc)],
        [Paragraph('42D', tc), Paragraph('0.43x', tc), Paragraph('4.50x', tc)],
        [Paragraph('63D', tc), Paragraph('0.39x', tc), Paragraph('3.70x', tc)],
    ]
    t2 = Table(slug_data, colWidths=[W*0.25, W*0.25, W*0.25])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), OCEAN),
        ('TEXTCOLOR', (0, 0), (-1, 0), WHITE),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, FOG),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [WHITE, HexColor('#f5f9fc')]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t2)
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        'In expanding environments, wins are nearly 4x the size of losses. In contracting environments, losses dominate by more than 2:1.',
        body))

    # Tercile regime table
    story.append(Paragraph('Tercile Regime Stats (63D Forward)', s['h2']))

    regime_data = [
        [Paragraph('CLI Regime', th), Paragraph('Avg 63D Return', th),
         Paragraph('Win Rate', th), Paragraph('Slugging', th)],
        [Paragraph('Contracting', tc), Paragraph('-8.5%', tc), Paragraph('33%', tc), Paragraph('0.43x', tc)],
        [Paragraph('Neutral', tc), Paragraph('+6.9%', tc), Paragraph('55%', tc), Paragraph('2.06x', tc)],
        [Paragraph('Expanding', tc), Paragraph('+16.8%', tc), Paragraph('73%', tc), Paragraph('3.92x', tc)],
    ]
    t3 = Table(regime_data, colWidths=[W*0.22, W*0.22, W*0.18, W*0.18])
    t3.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), OCEAN),
        ('TEXTCOLOR', (0, 0), (-1, 0), WHITE),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, FOG),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [WHITE, HexColor('#f5f9fc')]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t3)

    # --- DIFFERENTIATION ---
    story.append(Paragraph('Differentiation', s['h1']))

    tcl = s['table_cell_left']
    diff_data = [
        [Paragraph('vs Who', th), Paragraph('CLI Advantage', th)],
        [Paragraph('<b>Traditional Global<br/>Liquidity Indices</b>', tcl),
         Paragraph('Institutional-grade but don\'t include crypto-native transmission channels. CLI captures both macro liquidity AND how it actually reaches crypto markets.', tcl)],
        [Paragraph('<b>Lyn Alden</b>', tcl),
         Paragraph('Broader measurement (wholesale via reserves ratio, not just M2) plus crypto-native integration.', tcl)],
        [Paragraph('<b>Arthur Hayes</b>', tcl),
         Paragraph('Systematic construction with statistical grounding rather than narrative-driven tactical calls.', tcl)],
        [Paragraph('<b>Standard Net Liquidity<br/>(BS - TGA - RRP)</b>', tcl),
         Paragraph('CLI uses rate of change (not levels), includes crypto-native channels, captures reserve adequacy (not just reserves), and isn\'t broken by RRP depletion.', tcl)],
    ]
    t4 = Table(diff_data, colWidths=[W*0.28, W*0.62])
    t4.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), OCEAN),
        ('TEXTCOLOR', (0, 0), (-1, 0), WHITE),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, FOG),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [WHITE, HexColor('#f5f9fc')]),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t4)

    # --- CURRENT READING ---
    story.append(Paragraph('Current Reading', s['h1']))
    story.append(Paragraph(
        'As of Feb 25, 2026: <b>+0.18 (Q4, Strength)</b>',
        body))
    story.append(Paragraph(
        'Liquidity impulse firming. Crossed Q3/Q4 boundary in recent weeks. '
        'Dollar weakening and reserve dynamics improving. '
        'Technicals diverging (Z-RoC at -1.25, price below both MAs).',
        body))

    # --- INVALIDATION ---
    story.append(Paragraph('Invalidation', s['h1']))
    story.append(Paragraph('The CLI framework breaks if:', body))
    story.append(Paragraph(
        '<bullet>&bull;</bullet>The correlation between dollar direction and BTC reverses persistently '
        '(it has before: pre-2020, Fed tightening <i>increased</i> BTC prices)',
        bullet))
    story.append(Paragraph(
        '<bullet>&bull;</bullet>Stablecoin market structure changes fundamentally '
        '(e.g., regulatory crackdown eliminates the on-ramp channel)',
        bullet))
    story.append(Paragraph(
        '<bullet>&bull;</bullet>Reserve dynamics decouple from risk asset transmission '
        '(structural regime shift in Fed operations)',
        bullet))
    story.append(Paragraph(
        '<bullet>&bull;</bullet>Bitcoin\'s correlation to macro liquidity collapses as it '
        'transitions to a different asset class identity',
        bullet))

    # --- DISCLOSURE ---
    story.append(Spacer(1, 16))
    story.append(HRFlowable(width='100%', thickness=1, color=OCEAN, spaceAfter=8))
    story.append(Paragraph(
        '<i>Architecture, components, and empirical results are public. '
        'Exact component weights, z-score methodology, and regime filter calibration are proprietary.</i>',
        s['disclosure']))
    story.append(Paragraph(
        '<i>Lighthouse Macro | LighthouseMacro.com | @LHMacro | bob@lighthousemacro.com</i>',
        s['bio']))

    doc.build(story, onFirstPage=draw_page, onLaterPages=draw_page)
    print(f'  PDF saved: {OUT_PDF}')


if __name__ == '__main__':
    build_pdf()
