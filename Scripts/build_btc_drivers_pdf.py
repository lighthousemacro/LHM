"""
Build "What Is REALLY Driving Bitcoin's Price?" PDF
with updated charts (February 25, 2026)
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Image,
                                 HRFlowable, KeepTogether)
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

# =============================================================================
# CONFIG
# =============================================================================
CHART_DIR = '/Users/bob/LHM/Outputs/BTC_Drivers/white'
OUT_PDF = '/Users/bob/LHM/Outputs/BTC_Drivers/What_Is_REALLY_Driving_Bitcoins_Price.pdf'

OCEAN = HexColor('#2389BB')
DUSK = HexColor('#FF6723')
GRAY = HexColor('#898989')
BLACK = HexColor('#1a1a1a')
WHITE = HexColor('#ffffff')

# Try to register fonts
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
    styles = getSampleStyleSheet()

    s = {}
    s['brand'] = ParagraphStyle('brand', fontName=TITLE_FONT, fontSize=11,
                                 textColor=OCEAN, leading=14)
    s['date'] = ParagraphStyle('date', fontName=BODY_FONT, fontSize=10,
                                textColor=GRAY, alignment=TA_LEFT, leading=14)
    s['title'] = ParagraphStyle('title', fontName=TITLE_FONT, fontSize=24,
                                 textColor=BLACK, leading=30, spaceAfter=4)
    s['contributor'] = ParagraphStyle('contributor', fontName=BODY_FONT, fontSize=11,
                                      textColor=OCEAN, leading=14, spaceAfter=16)
    s['h1'] = ParagraphStyle('h1', fontName=TITLE_FONT, fontSize=18,
                              textColor=BLACK, leading=24, spaceBefore=20, spaceAfter=10)
    s['h2'] = ParagraphStyle('h2', fontName=TITLE_FONT, fontSize=14,
                              textColor=OCEAN, leading=18, spaceBefore=14, spaceAfter=8)
    s['body'] = ParagraphStyle('body', fontName=BODY_FONT, fontSize=10.5,
                                textColor=BLACK, leading=15, alignment=TA_JUSTIFY,
                                spaceAfter=8)
    s['caption'] = ParagraphStyle('caption', fontName=BODY_FONT, fontSize=9,
                                   textColor=GRAY, alignment=TA_CENTER,
                                   leading=12, spaceAfter=12, spaceBefore=4)
    s['footer'] = ParagraphStyle('footer', fontName=BODY_FONT, fontSize=8,
                                  textColor=GRAY, leading=10)
    s['tagline'] = ParagraphStyle('tagline', fontName=TITLE_FONT, fontSize=9,
                                   textColor=OCEAN, leading=12, alignment=TA_LEFT)
    s['disclosure'] = ParagraphStyle('disclosure', fontName=BODY_FONT, fontSize=9.5,
                                      textColor=GRAY, leading=13, alignment=TA_JUSTIFY,
                                      fontName2=BODY_FONT, spaceAfter=6)
    s['bio'] = ParagraphStyle('bio', fontName=BODY_FONT, fontSize=9,
                               textColor=GRAY, leading=12, spaceAfter=4)
    return s


# =============================================================================
# CONTENT
# =============================================================================
def build_pdf():
    s = make_styles()

    def draw_page(canvas, doc):
        """Draw accent bar + header/footer on every page."""
        w, h = letter
        margin = 0.85 * inch
        bar_h = 4

        # Top accent bar: Ocean 2/3, Dusk 1/3
        bar_y = h - 0.45 * inch
        bar_w = w - 2 * margin
        canvas.setFillColor(OCEAN)
        canvas.rect(margin, bar_y, bar_w * 0.67, bar_h, fill=1, stroke=0)
        canvas.setFillColor(DUSK)
        canvas.rect(margin + bar_w * 0.67, bar_y, bar_w * 0.33, bar_h, fill=1, stroke=0)

        # "LIGHTHOUSE MACRO" top-left
        canvas.setFillColor(OCEAN)
        canvas.setFont(TITLE_FONT, 11)
        canvas.drawString(margin, bar_y + 10, 'LIGHTHOUSE MACRO')

        # Date top-right
        canvas.setFillColor(GRAY)
        canvas.setFont(BODY_FONT, 10)
        canvas.drawRightString(w - margin, bar_y + 10, 'February 2026')

        # Bottom accent bar
        bot_y = 0.45 * inch
        canvas.setFillColor(OCEAN)
        canvas.rect(margin, bot_y, bar_w * 0.67, bar_h, fill=1, stroke=0)
        canvas.setFillColor(DUSK)
        canvas.rect(margin + bar_w * 0.67, bot_y, bar_w * 0.33, bar_h, fill=1, stroke=0)

        # Footer left
        canvas.setFillColor(GRAY)
        canvas.setFont(BODY_FONT, 8)
        canvas.drawString(margin, bot_y - 12,
                          'Bob Sheehan, CFA, CMT | Lighthouse Macro | LighthouseMacro.com | @LHMacro')

        # Footer right
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

    # --- HEADER (handled by page template, just add spacing) ---
    story.append(Spacer(1, 8))

    # Title
    story.append(Paragraph("What Is REALLY Driving Bitcoin's Price?", s['title']))
    story.append(Paragraph('Contributor: Bob Sheehan, CFA, CMT, Lighthouse Macro', s['contributor']))

    # --- INTRO ---
    body = s['body']

    story.append(Paragraph(
        'Gun to my head, two indicators: the Crypto Liquidity Impulse (CLI) and our Technical Structure scoring system.',
        body))
    story.append(Paragraph(
        'One maps the macro tide as it flows through specific pipes into crypto. The other tells you whether price action is confirming or diverging from that tide. They occupy fundamentally different information domains: liquidity conditions versus market structure. That\'s the point.',
        body))
    story.append(Paragraph(
        'No single indicator achieves strong out-of-sample predictive power for Bitcoin in isolation. The academic evidence (MDPI, 2024) shows blended signals consistently outperform any lone metric. But the blend has to make sense. You need a macro signal that tells you whether conditions favor risk assets, and a technical signal that tells you whether the market agrees. When both align, you have conviction. When they diverge, you have information.',
        body))

    # --- INDICATOR 1: CLI ---
    story.append(Paragraph('Indicator #1: The Crypto Liquidity Impulse (CLI)', s['h1']))

    story.append(Paragraph(
        'Most people who talk about "liquidity driving Bitcoin" are pointing at the right ocean but tracking the wrong waves. The standard net liquidity formula (Fed balance sheet minus TGA minus RRP) is a blunt instrument. It\'s US-only. It uses levels instead of rate of change. It ignores the channels through which liquidity actually reaches crypto markets. And post-RRP depletion (the facility effectively hit zero in 2025), it\'s structurally compromised: one of its three components is now a flatline.',
        body))
    story.append(Paragraph(
        'The CLI is our attempt to fix this. It\'s a weighted composite of eight components organized across three tiers, each capturing a different layer of the liquidity transmission mechanism with a different lead time.',
        body))

    # Tier 1
    story.append(Paragraph(
        'Tier 1 (40% weight, 11 to 13 week lead) captures the macro tide: Global M2 momentum and dollar direction. Michael Howell\'s work at CrossBorder Capital provides the empirical anchor. His variance decomposition attributes roughly 40% of Bitcoin\'s systematic price variance to global liquidity, with Granger causality kicking in at week 5 and peaking at weeks 11 to 13. Bitcoin\'s liquidity beta runs approximately 4.5x (gold\'s is 1.8x). The honest measure (12-month rolling correlation) averages 0.51. Still the highest of any asset class. Lyn Alden and Sam Callahan found BTC moves directionally with global M2 in 83% of 12-month periods.',
        body))

    # FIGURE 1
    fig1_path = os.path.join(CHART_DIR, 'fig_01_dxy_vs_btc.png')
    if os.path.exists(fig1_path):
        story.append(Spacer(1, 6))
        story.append(Image(fig1_path, width=W, height=W*0.55))
        story.append(Paragraph(
            'Figure 1: DXY (inverted) vs BTC/USD. Dollar peaks align with BTC cycle bottoms. Tier 1 captures this with DXY 63-Day RoC (25% of CLI weight).',
            s['caption']))

    # Tier 2
    story.append(Paragraph(
        'Tier 2 (35% weight, 1 to 6 week lead) maps the plumbing: the net liquidity impulse from WALCL, TGA, and RRP, plus wholesale funding stress via SOFR-IORB spreads and credit conditions via HY OAS. Post-RRP depletion, TGA rebuilds hit bank reserves directly. That\'s a regime change most net-liquidity trackers haven\'t internalized.',
        body))

    # Tier 3
    story.append(Paragraph(
        'Tier 3 (25% weight, 0 to 2 week lead) captures crypto-native transmission. Stablecoin supply momentum shows a 95% contemporaneous correlation with BTC (Bitcoin Magazine Pro). FalconX Research ran formal Granger causality tests on ETF flows: F-statistic of 8.48, p = 0.004. With US spot Bitcoin ETFs holding roughly 1.3 million BTC (about 7% of total supply), this channel is no longer marginal.',
        body))

    story.append(Paragraph(
        'A leverage regime filter (perpetual futures funding rates) is applied multiplicatively after the composite calculation. It captures the ~17% of time when crypto positioning dynamics override macro liquidity trends.',
        body))

    # FIGURE 2
    fig2_path = os.path.join(CHART_DIR, 'fig_02_cli_vs_fwd42d.png')
    if os.path.exists(fig2_path):
        story.append(Spacer(1, 6))
        story.append(Image(fig2_path, width=W, height=W*0.55))
        story.append(Paragraph(
            'Figure 2: CLI vs 42-Day Forward BTC Returns (2018-2026). Quintile bands shaded. Current reading: +0.18 (Q4, strength).',
            s['caption']))

    # FIGURE 3
    fig3_path = os.path.join(CHART_DIR, 'fig_03_cli_regime_bars.png')
    if os.path.exists(fig3_path):
        story.append(Spacer(1, 6))
        story.append(Image(fig3_path, width=W, height=W*0.55))
        story.append(Paragraph(
            'Figure 3: Average BTC Forward Returns by CLI Quintile (2018-2025). Monotonic at all horizons. Q5-Q1 spread: +22.1% (42D), t-stat 15.6. n=2,886.',
            s['caption']))

    # Disclosure
    story.append(Paragraph(
        '<i>Disclosure: Architecture, components, and empirical results are public. Exact weights, z-score methodology, and regime filter calibration are proprietary.</i>',
        s['disclosure']))

    # --- INDICATOR 2: TECHNICAL STRUCTURE ---
    story.append(Paragraph('Indicator #2: Technical Structure Scoring', s['h1']))

    story.append(Paragraph(
        'If the CLI tells you about the tide, the technical structure tells you whether the boat is moving with it or against it. Most technical analysis for Bitcoin is either too simple (just the 200-day moving average) or too cluttered (20 indicators saying different things). Our system distills it into three components scored 0 to 4 each, for a maximum of 12 points.',
        body))

    # Component 1: Trend
    story.append(Paragraph('Component 1: Trend Structure (0 to 4 points)', s['h2']))
    story.append(Paragraph(
        'Price position relative to the 50-day and 200-day moving averages, plus the slope of those averages. A clean uptrend has price above both, with both sloping up. Degradation happens in stages: price dips below the 50-day first, then the slope rolls over, then the 200-day gives way. Each stage costs points. The 200-week moving average serves as structural support, the level where long-term holders have historically accumulated.',
        body))

    # FIGURE 4
    fig4_path = os.path.join(CHART_DIR, 'fig_04_trend_structure.png')
    if os.path.exists(fig4_path):
        story.append(Spacer(1, 6))
        story.append(Image(fig4_path, width=W, height=W*0.55))
        story.append(Paragraph(
            'Figure 4: BTC Trend Structure. Price (gray) vs 50d MA (orange) and 200d MA (blue). Green shading = bullish structure. Pink = bearish.',
            s['caption']))

    # Component 2: Momentum
    story.append(Paragraph('Component 2: Momentum via Z-RoC (0 to 4 points)', s['h2']))
    story.append(Paragraph(
        'Z-score of the rate of change. Not just "is BTC going up" but "how unusual is the current move relative to its own history?" This is a dual-timeframe system: the 21-day Z-RoC captures tactical momentum (good for timing), while the 63-day Z-RoC captures regime-level momentum (good for positioning). The color logic is regime-aware: when both timeframes agree bullish, you\'re in a confirmed environment. When they diverge, you\'re in transition. When momentum is screaming, you listen. When it\'s whispering, you weigh it.',
        body))

    # FIGURE 5
    fig5_path = os.path.join(CHART_DIR, 'fig_05_zroc.png')
    if os.path.exists(fig5_path):
        story.append(Spacer(1, 6))
        story.append(Image(fig5_path, width=W, height=W*0.55))
        story.append(Paragraph(
            'Figure 5: Z-RoC with dual-timeframe color logic. Blue = both bullish. Orange = both bearish. Gray = timeframes diverge.',
            s['caption']))

    # Component 3: Relative Strength
    story.append(Paragraph('Component 3: Relative Strength (0 to 4 points)', s['h2']))
    story.append(Paragraph(
        'BTC\'s performance versus the total crypto market cap and versus SPX, across multiple timeframes, with slope analysis. This tells you whether Bitcoin is leading the move or getting dragged along. Persistent relative strength outperformance on rising slope is the strongest confirmation that a move has institutional backing, not just speculative froth.',
        body))

    # FIGURE 6
    fig6_path = os.path.join(CHART_DIR, 'fig_06_relative_strength.png')
    if os.path.exists(fig6_path):
        story.append(Spacer(1, 6))
        story.append(Image(fig6_path, width=W, height=W*0.55))
        story.append(Paragraph(
            'Figure 6: BTC/SPY Relative Strength Ratio (light blue) with 50-Day MA (blue). Rising ratio = BTC outperforming equities.',
            s['caption']))

    # --- SCORING DISCIPLINE ---
    story.append(Paragraph('Scoring Discipline and Risk Management', s['h2']))
    story.append(Paragraph(
        'Below 8 out of 12, you don\'t enter. Period. This alone filters out most of the "it looks like it\'s going up" trades that destroy capital in crypto. Above 8, the score determines position size: 16 to 19 points gets maximum conviction (20% allocation), 12 to 15 gets standard (12%), 8 to 11 gets reduced (7%).',
        body))
    story.append(Paragraph(
        'Every position has two stops: a thesis stop (what fundamental condition would invalidate the trade) and a price stop (15% drawdown, break of 200-day, or Z-RoC collapse below -1.0). Whichever triggers first. This means you can never hold a position where the thesis has broken but the price hasn\'t confirmed it, or vice versa.',
        body))

    # Why they pair
    story.append(Paragraph('<b>Why technicals pair with the CLI.</b>', body))
    story.append(Paragraph(
        'CLI expanding while the technical score is above 8 has been the highest-conviction entry setup. CLI expanding while technicals are deteriorating (score degrading from 10 to 6 over two weeks) is a warning: liquidity is supportive but something in price action is broken. Maybe it\'s an idiosyncratic event the macro can\'t see. Maybe it\'s early distribution. Either way, the divergence itself is information.',
        body))
    story.append(Paragraph(
        'CLI contracting while technicals remain strong (score above 12) is the classic "running on fumes" pattern. Price is still moving but the fuel is drying up. These are the environments where stops matter most, because the reversal, when it comes, tends to be fast.',
        body))

    # --- WHAT DOESN'T WORK ---
    from reportlab.platypus import PageBreak
    story.append(PageBreak())
    story.append(Paragraph("What Doesn't Work (And Why People Still Use It)", s['h1']))

    story.append(Paragraph(
        'Stock-to-Flow. A regression of price on a derivative of price is not a model. It\'s a mirror. Nico Cordeiro (Strix Leviathan) called it a "chameleon model," tautological by construction. Dr. Sebastian Kripfganz showed the results are "not statistically significantly different from zero" once autocorrelation is addressed. It predicted >$100K for 2022. Bitcoin was at $20K.',
        body))
    story.append(Paragraph(
        'Global M2 with a 70 to 80 Day Lag. Originated with Joe Consorti at Theya Bitcoin in late 2024. The "optimal" lag varies wildly (56 to 108 days). Sample: 14 months. Consorti himself conceded by mid-2025 that the relationship had broken down. Log returns correlation: 0.02 same-day.',
        body))
    story.append(Paragraph(
        'The 4-Year Halving Cycle. N = 3 completed cycles. Miners went from 68% to 3.9% of transaction value. Post-2024, BTC delivered its worst halving-epoch performance to date. Howell finds no evidence for a traditional 4-year cycle, attributing the apparent pattern to a 65-month global liquidity cycle. Which brings us back to indicator #1.',
        body))

    # --- HONEST CAVEAT ---
    story.append(Paragraph('The Honest Caveat', s['h1']))
    story.append(Paragraph(
        'No Bitcoin forecasting framework has survived rigorous out-of-sample testing across more than 3 to 4 cycles. Every relationship documented above is conditional and time-varying. The Bundesbank\'s Karau (2023) identified a regime shift: before 2020, Fed tightening actually increased Bitcoin prices (emerging-market demand for "digital cash"). After 2020, tightening decreased prices (risk-asset behavior). The sign flipped. If it flipped once, it can flip again.',
        body))
    story.append(Paragraph(
        'The analyst who combines directional liquidity conditions with disciplined technical structure and maintains epistemic humility about regime change will outperform the one chasing precise M2 overlays or halving countdowns. The CLI maps the pipes. The technical score tells you whether the market believes it. Neither claims to know where the storm goes next. But together, they give you the best available read on conditions.',
        body))

    # --- FOOTER ---
    # --- BIO ---
    story.append(Spacer(1, 20))
    story.append(HRFlowable(width='100%', thickness=1, color=OCEAN, spaceAfter=8))
    story.append(Paragraph(
        '<i>Bob Sheehan, CFA, CMT is the Founder and Chief Investment Officer of Lighthouse Macro, an institutional macro research firm. His work on Fed plumbing, liquidity transmission, and cross-asset strategy has been featured on Pascal Hugli\'s "Less Noise More Signal" podcast and Substack. Former Associate PM at Bank of America Private Bank ($4.5B AUM, 2.35 Sortino, 103% upside capture, 76% downside capture vs S&amp;P 500). Former VP, Data & Analytics at EquiLend.</i>',
        s['bio']))
    story.append(Paragraph(
        'Lighthouse Macro | LighthouseMacro.com | @LHMacro | bob@lighthousemacro.com',
        s['bio']))

    # Build with page template
    doc.build(story, onFirstPage=draw_page, onLaterPages=draw_page)
    print(f'  PDF saved: {OUT_PDF}')


if __name__ == '__main__':
    build_pdf()
