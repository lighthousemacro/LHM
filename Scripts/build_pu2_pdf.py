#!/usr/bin/env python3
"""
Build branded PDF for Positioning Update #2 - Lighthouse Macro
February 23, 2026
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, Color
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak,
    Table, TableStyle, KeepTogether, Flowable, Frame, PageTemplate,
    BaseDocTemplate, NextPageTemplate
)
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from PIL import Image as PILImage

# =============================================================================
# BRAND COLORS
# =============================================================================
OCEAN = HexColor('#2389BB')
DUSK = HexColor('#FF6723')
SKY = HexColor('#00BBFF')
VENUS = HexColor('#FF2389')
SEA = HexColor('#00BB89')
DOLDRUMS = HexColor('#898989')
STARBOARD = HexColor('#238923')
PORT = HexColor('#892323')
FOG = HexColor('#D1D1D1')
WHITE = HexColor('#FFFFFF')
BLACK = HexColor('#000000')
NEAR_BLACK = HexColor('#1a1a1a')

# Watermark color: very faint gray
WATERMARK_COLOR = Color(0.6, 0.6, 0.6, 0.15)

# =============================================================================
# PATHS
# =============================================================================
IMG_DIR = '/Users/bob/LHM/Outputs/positioning_update_2/white/'
OUTPUT_PATH = '/Users/bob/LHM/Outputs/positioning_update_2/PU2_Feb23_2026.pdf'

# =============================================================================
# PAGE SETTINGS
# =============================================================================
PAGE_WIDTH, PAGE_HEIGHT = letter  # 612 x 792 points
MARGIN = 0.75 * inch
CONTENT_WIDTH = PAGE_WIDTH - 2 * MARGIN  # ~468 points


# =============================================================================
# CUSTOM FLOWABLES
# =============================================================================
class AccentBar(Flowable):
    """Thin accent bar: 2/3 Ocean, 1/3 Dusk."""
    def __init__(self, width, height=4):
        Flowable.__init__(self)
        self.width = width
        self.height = height

    def draw(self):
        ocean_w = self.width * (2.0 / 3.0)
        dusk_w = self.width * (1.0 / 3.0)
        self.canv.setFillColor(OCEAN)
        self.canv.rect(0, 0, ocean_w, self.height, fill=1, stroke=0)
        self.canv.setFillColor(DUSK)
        self.canv.rect(ocean_w, 0, dusk_w, self.height, fill=1, stroke=0)


class HorizontalRule(Flowable):
    """A thin horizontal rule."""
    def __init__(self, width, color=FOG, thickness=0.75):
        Flowable.__init__(self)
        self.width = width
        self.color = color
        self.thickness = thickness

    def draw(self):
        self.canv.setStrokeColor(self.color)
        self.canv.setLineWidth(self.thickness)
        self.canv.line(0, 0, self.width, 0)


class TitlePageContent(Flowable):
    """Full title page content as a single flowable."""
    def __init__(self, width, height):
        Flowable.__init__(self)
        self.width = width
        self.height = height

    def wrap(self, availWidth, availHeight):
        """Return actual needed dimensions within available space."""
        self.width = min(self.width, availWidth)
        self.height = min(self.height, availHeight)
        return self.width, self.height

    def draw(self):
        c = self.canv
        w = self.width

        # Accent bar at top
        bar_y = self.height - 30
        ocean_w = w * (2.0 / 3.0)
        dusk_w = w * (1.0 / 3.0)
        c.setFillColor(OCEAN)
        c.rect(0, bar_y, ocean_w, 5, fill=1, stroke=0)
        c.setFillColor(DUSK)
        c.rect(ocean_w, bar_y, dusk_w, 5, fill=1, stroke=0)

        # "POSITIONING UPDATE" label
        c.setFont('Helvetica', 12)
        c.setFillColor(DOLDRUMS)
        label_y = bar_y - 80
        c.drawCentredString(w / 2, label_y, 'POSITIONING UPDATE')

        # Thin accent line under label
        line_y = label_y - 10
        line_w = 80
        c.setStrokeColor(OCEAN)
        c.setLineWidth(1.5)
        c.line(w/2 - line_w/2, line_y, w/2 + line_w/2, line_y)

        # Date
        c.setFont('Helvetica-Bold', 22)
        c.setFillColor(OCEAN)
        date_y = line_y - 45
        c.drawCentredString(w / 2, date_y, 'FEBRUARY 23, 2026')

        # Title
        c.setFont('Helvetica-Bold', 16)
        c.setFillColor(NEAR_BLACK)
        title_y = date_y - 60
        c.drawCentredString(w / 2, title_y, 'The Tariff Regime Breaks.')
        c.drawCentredString(w / 2, title_y - 22, 'The Defensive Thesis Doesn\'t.')

        # Horizontal rule
        rule_y = title_y - 55
        c.setStrokeColor(FOG)
        c.setLineWidth(0.75)
        c.line(w * 0.2, rule_y, w * 0.8, rule_y)

        # Framework line
        c.setFont('Helvetica', 10)
        c.setFillColor(DOLDRUMS)
        fw_y = rule_y - 25
        c.drawCentredString(w / 2, fw_y, 'Two Books Framework: Core Book + Technical Overlay')

        # Author
        c.setFont('Helvetica-Bold', 12)
        c.setFillColor(NEAR_BLACK)
        author_y = fw_y - 50
        c.drawCentredString(w / 2, author_y, 'Bob Sheehan, CFA, CMT')

        c.setFont('Helvetica', 10)
        c.setFillColor(DOLDRUMS)
        c.drawCentredString(w / 2, author_y - 18, 'Founder & Chief Investment Officer')
        c.drawCentredString(w / 2, author_y - 34, 'Lighthouse Macro')

        # Bottom accent bar
        c.setFillColor(OCEAN)
        c.rect(0, 30, ocean_w, 5, fill=1, stroke=0)
        c.setFillColor(DUSK)
        c.rect(ocean_w, 30, dusk_w, 5, fill=1, stroke=0)

        # Bottom tagline
        c.setFont('Helvetica', 9)
        c.setFillColor(DOLDRUMS)
        c.drawCentredString(w / 2, 12, 'LighthouseMacro.com | @LHMacro | MACRO, ILLUMINATED.')


# =============================================================================
# PAGE DECORATIONS (header accent bar, watermarks, page numbers, footer)
# =============================================================================
def draw_page_decorations(canvas_obj, doc):
    """Called on every non-title page."""
    canvas_obj.saveState()
    w, h = PAGE_WIDTH, PAGE_HEIGHT

    # --- Accent bar at top ---
    bar_y = h - 0.35 * inch
    bar_height = 4
    ocean_w = (w - 2 * 0.5 * inch) * (2.0 / 3.0)
    dusk_w = (w - 2 * 0.5 * inch) * (1.0 / 3.0)
    bar_x = 0.5 * inch
    canvas_obj.setFillColor(OCEAN)
    canvas_obj.rect(bar_x, bar_y, ocean_w, bar_height, fill=1, stroke=0)
    canvas_obj.setFillColor(DUSK)
    canvas_obj.rect(bar_x + ocean_w, bar_y, dusk_w, bar_height, fill=1, stroke=0)

    # --- Watermarks ---
    canvas_obj.setFillColor(WATERMARK_COLOR)
    canvas_obj.setFont('Helvetica-Bold', 10)
    canvas_obj.drawString(MARGIN, h - 0.55 * inch, 'LIGHTHOUSE MACRO')
    canvas_obj.drawRightString(w - MARGIN, 0.55 * inch, 'MACRO, ILLUMINATED.')

    # --- Page number bottom center ---
    canvas_obj.setFillColor(DOLDRUMS)
    canvas_obj.setFont('Helvetica', 9)
    page_num = canvas_obj.getPageNumber()
    canvas_obj.drawCentredString(w / 2, 0.4 * inch, str(page_num))

    # --- Footer ---
    canvas_obj.setFont('Helvetica', 7)
    canvas_obj.setFillColor(DOLDRUMS)
    footer = 'Bob Sheehan, CFA, CMT | Founder & Chief Investment Officer | Lighthouse Macro | LighthouseMacro.com | @LHMacro'
    canvas_obj.drawCentredString(w / 2, 0.28 * inch, footer)

    canvas_obj.restoreState()


def draw_title_page(canvas_obj, doc):
    """Title page has no decorations (handled by TitlePageContent)."""
    pass


# =============================================================================
# STYLES
# =============================================================================
def get_styles():
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        'LHM_Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=15,
        textColor=NEAR_BLACK,
        alignment=TA_JUSTIFY,
        spaceAfter=8,
        spaceBefore=2,
    ))

    styles.add(ParagraphStyle(
        'LHM_SectionHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        textColor=OCEAN,
        spaceBefore=20,
        spaceAfter=10,
    ))

    styles.add(ParagraphStyle(
        'LHM_SubHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=NEAR_BLACK,
        spaceBefore=14,
        spaceAfter=8,
    ))

    styles.add(ParagraphStyle(
        'LHM_SubHeader2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11.5,
        leading=15,
        textColor=NEAR_BLACK,
        spaceBefore=10,
        spaceAfter=6,
    ))

    styles.add(ParagraphStyle(
        'LHM_Caption',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=9,
        leading=12,
        textColor=DOLDRUMS,
        alignment=TA_CENTER,
        spaceBefore=4,
        spaceAfter=12,
    ))

    styles.add(ParagraphStyle(
        'LHM_Emphasis',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=NEAR_BLACK,
        alignment=TA_JUSTIFY,
        spaceAfter=8,
        spaceBefore=2,
    ))

    styles.add(ParagraphStyle(
        'LHM_Callout',
        parent=styles['Normal'],
        fontName='Helvetica-BoldOblique',
        fontSize=12,
        leading=16,
        textColor=OCEAN,
        alignment=TA_CENTER,
        spaceBefore=12,
        spaceAfter=12,
        leftIndent=30,
        rightIndent=30,
    ))

    styles.add(ParagraphStyle(
        'LHM_Bullet',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=15,
        textColor=NEAR_BLACK,
        leftIndent=20,
        spaceAfter=4,
        spaceBefore=2,
        bulletIndent=8,
    ))

    styles.add(ParagraphStyle(
        'LHM_SignOff',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=11,
        leading=15,
        textColor=DOLDRUMS,
        alignment=TA_CENTER,
        spaceBefore=8,
        spaceAfter=4,
    ))

    styles.add(ParagraphStyle(
        'LHM_Tagline',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=OCEAN,
        alignment=TA_CENTER,
        spaceBefore=12,
        spaceAfter=8,
    ))

    styles.add(ParagraphStyle(
        'LHM_Footer_Author',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=NEAR_BLACK,
        alignment=TA_CENTER,
        spaceBefore=4,
        spaceAfter=2,
    ))

    styles.add(ParagraphStyle(
        'LHM_Footer_Org',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=DOLDRUMS,
        alignment=TA_CENTER,
        spaceBefore=2,
        spaceAfter=4,
    ))

    styles.add(ParagraphStyle(
        'LHM_Tracking_Note',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=9.5,
        leading=13,
        textColor=DOLDRUMS,
        alignment=TA_JUSTIFY,
        spaceBefore=8,
        spaceAfter=8,
        leftIndent=15,
        rightIndent=15,
    ))

    return styles


# =============================================================================
# IMAGE HELPER
# =============================================================================
def make_image(filename, max_width=None):
    """Create a reportlab Image flowable from a PNG, scaled to fit content width."""
    path = os.path.join(IMG_DIR, filename)
    if not os.path.exists(path):
        print(f"WARNING: Image not found: {path}")
        return Spacer(1, 12)

    if max_width is None:
        max_width = CONTENT_WIDTH

    pil_img = PILImage.open(path)
    w_px, h_px = pil_img.size
    aspect = h_px / w_px
    display_w = max_width
    display_h = display_w * aspect

    # Cap height at 80% of content area to avoid overflow
    max_h = (PAGE_HEIGHT - 2 * MARGIN - 1.0 * inch) * 0.80
    if display_h > max_h:
        display_h = max_h
        display_w = display_h / aspect

    return Image(path, width=display_w, height=display_h)


# =============================================================================
# BUILD THE DOCUMENT
# =============================================================================
def build_pdf():
    styles = get_styles()

    # Create document with page templates
    doc = BaseDocTemplate(
        OUTPUT_PATH,
        pagesize=letter,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
        title='Positioning Update #2 - Lighthouse Macro',
        author='Bob Sheehan, CFA, CMT',
        subject='Macro Positioning Update - February 23, 2026',
    )

    # Frame for title page (full page, wide margins for centered content)
    title_frame = Frame(
        MARGIN, MARGIN,
        CONTENT_WIDTH, PAGE_HEIGHT - 2 * MARGIN,
        id='title_frame',
        leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0,
    )

    # Frame for content pages (with room for header bar and footer)
    content_frame = Frame(
        MARGIN, 0.75 * inch,
        CONTENT_WIDTH, PAGE_HEIGHT - 1.5 * inch - 0.15 * inch,
        id='content_frame'
    )

    title_template = PageTemplate(
        id='TitlePage',
        frames=[title_frame],
        onPage=draw_title_page,
    )

    content_template = PageTemplate(
        id='ContentPage',
        frames=[content_frame],
        onPage=draw_page_decorations,
    )

    doc.addPageTemplates([title_template, content_template])

    # =========================================================================
    # BUILD STORY
    # =========================================================================
    story = []

    # --- TITLE PAGE ---
    story.append(TitlePageContent(CONTENT_WIDTH, PAGE_HEIGHT - 2 * MARGIN))
    story.append(NextPageTemplate('ContentPage'))
    story.append(PageBreak())

    # Helper shortcuts
    body = lambda text: Paragraph(text, styles['LHM_Body'])
    section = lambda text: Paragraph(text, styles['LHM_SectionHeader'])
    subsec = lambda text: Paragraph(text, styles['LHM_SubHeader'])
    subsec2 = lambda text: Paragraph(text, styles['LHM_SubHeader2'])
    caption = lambda text: Paragraph(text, styles['LHM_Caption'])
    callout = lambda text: Paragraph(text, styles['LHM_Callout'])
    emphasis = lambda text: Paragraph(text, styles['LHM_Emphasis'])
    bullet = lambda text: Paragraph(text, styles['LHM_Bullet'])
    note = lambda text: Paragraph(text, styles['LHM_Tracking_Note'])
    sp = lambda h=8: Spacer(1, h)
    hr = lambda: HorizontalRule(CONTENT_WIDTH)

    # --- HOW WE'RE DOING ---
    story.append(section("HOW WE'RE DOING: JANUARY 15 TO FEBRUARY 22"))
    story.append(sp(4))

    story.append(body(
        'On January 15, we published "Playing Defense in a Hollow Rally." Our macro risk '
        'assessment was elevated. We called for underweighting equities, overweighting '
        'defensives, avoiding the long bond, and said VIX in the mid-teens was complacent.'
    ))

    story.append(sp(4))
    story.append(emphasis('Here is what happened:'))
    story.append(sp(6))

    # Scorecard table image
    story.append(make_image('table_scorecard.png'))
    story.append(sp(6))

    # Defensive basket chart
    story.append(make_image('fig01_defensive_basket.png'))
    story.append(caption('Figure 1: Defensive Basket vs. SPY'))

    story.append(body(
        'Defensive basket vs. SPY: XLU +7.9% and XLP +7.6% relative in five weeks. '
        'IWM and XLV flat. The calls that worked, worked big.'
    ))

    story.append(body(
        'The outperformance is not flashy. It is structural. SPY lost 0.6% while XLU '
        'returned +7.3% and XLP gained +7.0% absolute. In a flat-to-down tape, that is '
        'the entire game.'
    ))

    story.append(body(
        'The vol call is worth highlighting separately. We said VIX in the mid-teens was '
        'mispricing risk. VIX moved from 15.44 to 19.09, a 23.6% increase in the index '
        'level. The specific P&amp;L depends on expression (VIX calls, put spreads on SPY, '
        'long VXX), but the directional read was correct and well-timed.'
    ))

    story.append(body(
        'Four of six legs clearly working (SPY underweight, XLP, XLU, vol). IWM and XLV '
        'essentially flat. Credit underweight structurally intact but early. The SCOTUS '
        'relief rally does not break any of these calls.'
    ))

    story.append(sp(8))
    story.append(note(
        'A note on tracking: these are research calls published with timestamps, not a '
        'managed portfolio. The piece went out after the close on Jan 15. Prices are '
        'sourced from Jan 16 open and Feb 20 market closes. We are building a formal '
        'model portfolio with verifiable execution timestamps for future updates. For now, '
        'the published calls with dates serve as the audit trail. We would rather show you '
        'exactly what we said and when than fabricate a backtest.'
    ))

    story.append(sp(6))
    story.append(hr())
    story.append(sp(6))

    # --- WHAT'S IN THIS UPDATE ---
    story.append(section("WHAT'S IN THIS UPDATE"))
    story.append(sp(4))

    story.append(body(
        '<b>Labor:</b> The quits rate is sitting on the exact threshold that preceded the '
        'last three recessions. The question is not whether the labor market is weakening. '
        'It is whether the headline data catches up before or after credit does.'
    ))

    story.append(body(
        '<b>Credit:</b> The gap between what spreads are pricing and what labor is saying '
        'has not been this wide since 2007. The SCOTUS ruling may have made it worse.'
    ))

    story.append(body(
        '<b>Plumbing:</b> The shock absorber is gone. RRP is effectively zero. SOFR-EFFR '
        'is quiet, but the margin for error just got thinner.'
    ))

    story.append(body(
        '<b>Rates:</b> The steepener is building. Term premium is repricing for a post-QT, '
        'deficit-heavy world. The SCOTUS ruling does not change that.'
    ))

    story.append(body(
        'Full analysis: updated macro assessment across labor, credit, plumbing, and market '
        'structure. Two Books positioning with entry/exit levels, Technical Overlay watchlist, '
        'and explicit invalidation criteria for both directions.'
    ))

    story.append(sp(6))
    story.append(hr())
    story.append(sp(6))

    # --- EXECUTIVE SUMMARY ---
    story.append(section('EXECUTIVE SUMMARY'))
    story.append(sp(4))

    story.append(callout('Yesterday changed the game. Not the thesis.'))
    story.append(sp(4))

    story.append(body(
        'The Supreme Court struck down IEEPA tariffs 6-3, invalidating the legal foundation '
        'for roughly $130-175 billion in tariff revenue collected since early 2025. Within '
        'hours, Trump signed a proclamation imposing a 10% global tariff under Section 122 '
        'of the Trade Act of 1974. By the following morning, he announced via Truth Social '
        'that the rate would increase to 15%, the statutory maximum.'
    ))

    story.append(body(
        'Here is what matters: the SCOTUS ruling alone dropped the effective tariff rate '
        'from roughly 17% to 9%, per the Yale Budget Lab. But Section 122 at 15% pushes it '
        'back to approximately 14%. The net relief is real but narrower than the headline '
        'suggests. Section 122 is structurally capped at 15% and expires in 150 days unless '
        'Congress acts. That is a fundamentally different animal than the open-ended, '
        'uncapped IEEPA regime. The tariff wild card just got materially smaller.'
    ))

    story.append(body(
        'What did not change: the labor market is still freezing. The quits rate sits at the '
        'pre-recessionary threshold. December JOLTS printed the lowest openings rate since 2020 '
        '(3.9% per BLS, or 4.1% as a share of nonfarm employment), continuing a slide that '
        'professional services, retail, and finance led lower. BLS revised 2025 payrolls from '
        '584,000 down to 181,000. Long-term unemployment is building, quits are decelerating, '
        'and the hires-to-quits ratio is compressing. Credit spreads are still pricing a '
        'different economy than labor is reporting. HY OAS at 288 bps, below 300, while labor '
        'deteriorates underneath.'
    ))

    story.append(sp(4))
    story.append(callout(
        'The SCOTUS ruling lowers the ceiling on how bad things can get. '
        'It does not raise the floor on how fragile labor already is.'
    ))
    story.append(sp(4))

    story.append(emphasis(
        'Net assessment: The tariff pressure valve released. We remain in an elevated risk '
        'environment. The defensive posture holds. But the composition of risk has shifted, '
        'and that changes which expressions we favor.'
    ))

    story.append(sp(6))
    story.append(hr())
    story.append(sp(6))

    # --- WHAT CHANGED ---
    story.append(section('WHAT CHANGED SINCE JANUARY 15'))
    story.append(sp(4))

    # Section 1: Tariff Regime
    story.append(subsec('1. The Tariff Regime: Broken and Rebuilt in 24 Hours'))
    story.append(sp(4))

    story.append(body(
        'The Supreme Court ruled that IEEPA does not authorize the President to impose tariffs. '
        'Chief Justice Roberts, joined by Gorsuch, Barrett, and the three liberal justices, held '
        'that two words buried in a 1977 statute cannot bear the weight of unilateral trade policy. '
        'The immediate market response was a relief rally: SPX +0.65%, VIX from ~20 to 19.09, '
        'dollar index weakening.'
    ))

    story.append(body(
        'Trump moved fast. A proclamation signed the same day revoked IEEPA tariffs and imposed '
        'Section 122 tariffs at 10%. The following day (Feb 21), he announced the rate would '
        'increase to 15% via Truth Social. The formal executive order for the 15% rate had not '
        'been signed as of this writing. The differences from IEEPA matter:'
    ))

    story.append(bullet(
        '<b>Rate cap:</b> 15% maximum under Section 122 vs. uncapped under IEEPA '
        '(rates had reached 145% on some Chinese goods).'
    ))
    story.append(bullet(
        '<b>Duration:</b> 150 days unless Congress extends. IEEPA had no expiration.'
    ))
    story.append(bullet(
        '<b>Refund overhang:</b> $100-175 billion in IEEPA tariff revenue may need to be refunded '
        'to importers (Yale Budget Lab estimates up to $175B, RSM estimates $100-130B, Penn Wharton '
        'estimates $165B). Timing is highly uncertain: the Court did not order refunds or specify a '
        'process, and CIT litigation will determine the mechanics. But directionally, this is a '
        'fiscal impulse in reverse, eventually injecting liquidity back to the private sector.'
    ))
    story.append(bullet(
        '<b>Effective rate:</b> Yale Budget Lab calculates the average effective tariff rate fell '
        'from ~17% to 9.1% with the SCOTUS ruling alone. Section 122 at 15% pushes it back to '
        'approximately 14%. The consumer price impact falls from 1.2% to 0.6% (pre-substitution, '
        'per Yale).'
    ))

    story.append(sp(4))
    story.append(body(
        'For our framework: the tariff pass-through into CPI that we flagged as a Q2 risk now has '
        'a lower ceiling. The deficit-financed stimulus offset for tariff drag is less necessary if '
        'the drag itself shrinks.'
    ))

    story.append(sp(8))

    # Section 2: Labor
    story.append(subsec('2. Labor: Still at the Threshold'))
    story.append(sp(4))

    story.append(body(
        'Nothing improved. The JOLTS report confirmed the deceleration pattern: the openings rate '
        'fell to 3.9% (BLS official rate), lowest since 2020. Professional services, retail, and '
        'finance led the decline. The quits rate continues pressing the pre-recessionary threshold.'
    ))

    story.append(sp(4))
    story.append(callout(
        '2.0% quits is the line. We have been saying this for months. A print below 2.0% is '
        'not a data point. It is a regime confirmation.'
    ))
    story.append(sp(4))

    story.append(body(
        'BLS benchmark revisions wiped 403,000 jobs from the 2025 total. The labor market was '
        'running colder than headline payrolls suggested all year. This is not a revision that '
        'changes the narrative. It is a revision that confirms the narrative we already had.'
    ))

    story.append(body(
        'The structural story is building underneath the headline. Long-term unemployment is rising, '
        'quits are decelerating, and the hires-to-quits ratio is compressing. This is not noise. '
        'This is late-cycle labor market architecture.'
    ))

    story.append(body(
        'The next JOLTS release (early March) is the most important data point in our framework '
        'right now. A quits print below 2.0% moves the diagnosis from "concerning" to '
        '"pre-recessionary confirmed."'
    ))

    story.append(sp(6))

    # Charts: JOLTS quits + openings
    story.append(make_image('fig02_quits_rate.png'))
    story.append(caption('Figure 2: JOLTS Quits Rate: Sitting on the Line'))

    story.append(sp(4))
    story.append(make_image('fig03_openings_rate.png'))
    story.append(caption('Figure 3: JOLTS Job Openings Rate: Collapse to 2020 Lows'))

    story.append(sp(8))

    # Section 3: Credit
    story.append(subsec('3. Credit: Complacency Deepens'))
    story.append(sp(4))

    story.append(body(
        'HY OAS at 288 bps. Still below the 300 bps complacent threshold. Credit and labor '
        'continue pricing two different economies.'
    ))

    story.append(body(
        'The divergence between where credit spreads are and where labor flows say they should be '
        'has widened since our January update, not narrowed. Spreads are too tight for the labor '
        'reality underneath. The gap between what credit is pricing and what the quits rate, '
        'openings data, and payroll revisions are saying has not been this wide in over two years.'
    ))

    story.append(body(
        'The SCOTUS ruling could paradoxically reinforce credit complacency in the short term. '
        'Lower tariff drag means less recession risk from trade, which gives credit markets another '
        'reason to stay tight. But the labor deterioration is domestic, not trade-driven. Credit is '
        'looking at the wrong risk.'
    ))

    story.append(sp(6))
    story.append(make_image('fig04_hy_oas.png'))
    story.append(caption('Figure 4: HY OAS: Credit Still in Denial'))

    story.append(sp(4))
    story.append(make_image('fig05_credit_labor_divergence.png'))
    story.append(caption('Figure 5: The Divergence: Credit Spreads vs Labor Flows'))

    story.append(sp(8))

    # Section 4: Market Structure
    story.append(subsec('4. Market Structure: The Relief Rally Test'))
    story.append(sp(4))

    story.append(body(
        'SPX rallied on the SCOTUS news, recovering above the 50-day MA. But context matters: '
        'Nasdaq breadth remains fractured at ~44% above the 200-day MA vs. SPX at ~64%. Price is '
        'moving higher. The soldiers are not following the generals.'
    ))

    story.append(body(
        'The question is whether this rally has legs. If breadth does not confirm within 2-3 weeks '
        '(Nasdaq % above 200d needs to recover toward 55%+), this is distribution masquerading as '
        'relief. Watch it, don\'t chase it.'
    ))

    story.append(sp(8))

    # Section 5: Volatility
    story.append(subsec('5. Volatility: The VIX Gave Back'))
    story.append(sp(4))

    story.append(body(
        'VIX dropped from ~21 to ~19 on the SCOTUS ruling. In January, we called VIX in the '
        'mid-teens "complacent" and said to own convexity. That worked. VIX ran from ~15 to the '
        'low 20s. For context, a typical 30-day at-the-money VIX call purchased in mid-January '
        'would have returned roughly 30-40% at peak.'
    ))

    story.append(body(
        'Now: VIX at ~20 is not cheap, but it is no longer pricing the full tariff uncertainty '
        'that existed 48 hours ago. With Section 122 capped and time-limited, the tail risk '
        'distribution has compressed. The vol call has played out. We would not add new convexity '
        'at these levels.'
    ))

    story.append(sp(6))
    story.append(make_image('fig06_vix.png'))
    story.append(caption('Figure 6: VIX: From Complacency to Recalibration'))

    story.append(sp(8))

    # Section 6: Plumbing
    story.append(subsec('6. Plumbing: Quiet but Not Comfortable'))
    story.append(sp(4))

    story.append(body(
        'SOFR at 367 bps, EFFR at 364 bps. The SOFR-EFFR spread sits at roughly 3 bps, well below '
        'our 15-20 bps distress threshold. Regime stays Defensive, not Disorderly. No change to '
        'The One Switch.'
    ))

    story.append(body(
        'RRP usage continues declining (sub-$1B), confirming the buffer exhaustion we flagged in '
        'January. Reserve levels are adequate but shrinking. The system is operating without a '
        'shock absorber, but funding markets are not yet stressed. The margin for error is thin '
        'and getting thinner.'
    ))

    story.append(sp(6))
    story.append(make_image('fig07_sofr_effr.png'))
    story.append(caption('Figure 7: SOFR vs EFFR: The One Switch'))

    story.append(sp(8))

    # Section 7: Gold and the Dollar
    story.append(subsec('7. Gold and the Dollar: The Call That Keeps Paying'))
    story.append(sp(4))

    story.append(body(
        'We have been bullish gold since May 2024, when we published "The Dollar vs. Gold &amp; '
        'Real Yields" and argued that gold was pricing something beyond real yields: central bank '
        'buying, de-dollarization, and fiscal dominance. GLD was around $214 then. We reinforced '
        'the call in March 2025 with "Bullion Brilliance," writing explicitly that new all-time '
        'highs should not trigger profit-taking. We formalized it in the January positioning update.'
    ))

    story.append(body(
        'Gold surged above $5,000 on SCOTUS day, with spot trading around $5,025-5,050 and futures '
        'touching higher. The structural thesis is intact and accelerating. The SCOTUS ruling and '
        'dollar weakness reinforce the bid: the refund overhang ($100-175 billion eventually flowing '
        'back to importers) is a fiscal impulse that gold may be front-running, and institutional '
        'rebalancing out of dollar assets as DXY weakens adds a second tailwind.'
    ))

    story.append(body(
        'BTC traded to ~$67,684, modestly positive but lagging gold. In a Defensive (not Disorderly) '
        'plumbing regime with a falling dollar, gold leads. Crypto follows only when plumbing stress '
        'resolves and liquidity expands. We are not there yet.'
    ))

    story.append(body(
        'Dollar weakness, if sustained, has implications beyond gold. EM equities and commodities '
        'tend to outperform in DXY downcycles. We are monitoring but not yet expressing this. Our '
        'framework is US-centric by design, and the credibility of the diagnostic system depends on '
        'staying within what it measures. Adding a global transmission layer is on the roadmap, not '
        'in the current stack. When it is ready, we will say so.'
    ))

    story.append(sp(8))

    # Section 8: Rates
    story.append(subsec('8. Rates: The Steepener Building'))
    story.append(sp(4))

    story.append(body(
        'The 10Y sits at 4.08% with the 10Y-2Y curve at +60 bps. Term premium continues to build. '
        'The steepener thesis we introduced in the February update is gaining traction: tariff '
        'pass-through is inflationary at the long end, deficit dynamics keep supply heavy, and the '
        'front end stays anchored by a Fed that cannot cut into sticky core inflation.'
    ))

    story.append(sp(6))
    story.append(make_image('fig08_yield_curve.png'))
    story.append(caption('Figure 8: 10Y-2Y Curve: Steepener Building'))

    story.append(sp(6))
    story.append(hr())
    story.append(sp(6))

    # --- POSITIONS ---
    story.append(section('POSITIONS: TWO BOOKS FRAMEWORK'))
    story.append(sp(4))

    story.append(subsec('Core Book: Defensive Posture Maintained'))
    story.append(sp(4))

    story.append(body(
        'The relief rally does not change the labor-credit divergence underneath. We maintain the '
        'defensive tilt with one adjustment: the tariff-driven inflation hedge is de-emphasized '
        'given SCOTUS, and gold, a structural position since May 2024, is formalized in the Core Book.'
    ))

    story.append(sp(6))
    story.append(subsec2('Equities'))
    story.append(sp(4))
    story.append(make_image('table_positions_equities.png'))
    story.append(sp(4))

    story.append(body(
        'Not adding risk despite VIX elevation. The VIX move reflects tariff/Fed uncertainty, '
        'not capitulation washout.'
    ))

    story.append(sp(6))
    story.append(subsec2('Rates'))
    story.append(sp(4))
    story.append(make_image('table_positions_rates.png'))
    story.append(sp(4))

    story.append(body(
        'If 10yr breaks above 4.60-4.70%, steepener thesis accelerates.'
    ))

    story.append(sp(6))
    story.append(subsec2('Credit'))
    story.append(sp(4))
    story.append(make_image('table_positions_credit.png'))
    story.append(sp(8))

    story.append(subsec2('Real Assets and Cash'))
    story.append(sp(4))
    story.append(make_image('table_positions_real_assets.png'))

    story.append(sp(8))

    # Technical Overlay Book
    story.append(subsec('Technical Overlay Book'))
    story.append(sp(4))

    story.append(body(
        'The Overlay runs in parallel with the Core Book. It is not gated by macro conditions. '
        'It scores instruments on a 12-point system across Trend Structure (0-4), Momentum via '
        'Z-RoC (0-4), and Relative Strength (0-4). Minimum 8/12 to enter. The Overlay is pure '
        'technical: trend, momentum, relative strength. No macro input, no narrative. If the score '
        'is there, the position is there.'
    ))

    story.append(sp(4))
    story.append(body(
        'Two instruments currently scoring well:'
    ))

    story.append(sp(4))
    story.append(body(
        '<b>GLD:</b> Trend structure strong (price > 50d > 200d, slopes positive). Momentum strong '
        '(Z-RoC positive across both timeframes). Relative strength vs SPY persistent across '
        'multiple timeframes with rising slope. Scoring 10-11/12. This is the rare case where Core '
        'Book conviction and Overlay scoring converge on the same instrument.'
    ))

    story.append(body(
        '<b>XLU:</b> Trend intact, relative strength vs SPY has been persistent since mid-January. '
        'Scoring 9-10/12. Defensive beta that the Overlay confirms independently of the macro thesis.'
    ))

    story.append(sp(6))
    story.append(hr())
    story.append(sp(6))

    # --- KEY MONITORING SIGNALS ---
    story.append(section('KEY MONITORING SIGNALS'))
    story.append(sp(4))

    # Invalidation table
    story.append(make_image('table_invalidation.png'))
    story.append(sp(8))

    story.append(subsec2('The Labor Floor'))
    story.append(sp(4))
    story.append(body(
        'Quits at the pre-recessionary threshold is the line. The next JOLTS release (early March) '
        'will either confirm or deny. A print below 2.0% moves the labor deceleration from '
        '"concerning" to "pre-recessionary confirmed." The structural deterioration underneath the '
        'headline (long-term unemployment rising, hires-to-quits compressing) is already screaming. '
        'The headline just has not caught up.'
    ))

    story.append(sp(6))
    story.append(subsec2('The Tariff Transition'))
    story.append(sp(4))
    story.append(body(
        'Section 122 at 15% is the new baseline. Congress has 150 days. Watch for: (a) attempts to '
        'legislate replacement tariffs under Section 301/232, which would be more durable, (b) the '
        'refund process for IEEPA tariffs, which injects liquidity back to importers, (c) trade deal '
        'renegotiations, since deals struck under IEEPA threat may need to be reworked.'
    ))

    story.append(sp(6))
    story.append(subsec2('The One Switch'))
    story.append(sp(4))
    story.append(body(
        'SOFR-EFFR spread. Still quiet at ~3 bps. The Defensive-to-Disorderly threshold remains '
        '15-20 bps. No change. This is the plumbing signal that would force us from caution to action.'
    ))

    story.append(sp(6))
    story.append(subsec2('Breadth Confirmation Window'))
    story.append(sp(4))
    story.append(body(
        'Nasdaq % above 200-day MA needs to recover from ~44% toward 55%+ within 3 weeks to '
        'validate the SCOTUS relief rally. Failure means the divergence between index-level price '
        'and underlying participation widens, and the distribution pattern we flagged accelerates.'
    ))

    story.append(sp(6))
    story.append(subsec2('Gold and Dollar Momentum'))
    story.append(sp(4))
    story.append(body(
        'Gold above $5,000 with DXY weakening. If gold sustains above $5,000 with dollar weakness '
        'persisting, the real asset rotation thesis strengthens. This has been a structural call since '
        'May 2024, now formalized in the Core Book. Sustained dollar weakness would also begin to '
        'create conditions for EM outperformance, which we will address when we have the framework '
        'to back it.'
    ))

    story.append(sp(6))
    story.append(subsec2('Liquidity Watch'))
    story.append(sp(4))
    story.append(body(
        'RRP effectively exhausted. Reserve levels adequate but shrinking. SOFR-EFFR spread the '
        'canary. If funding spreads widen toward 15 bps, the plumbing risk profile changes from '
        '"uncomfortable" to "fragile." That would be the signal to further increase cash.'
    ))

    story.append(sp(6))
    story.append(hr())
    story.append(sp(6))

    # --- THE BOTTOM LINE ---
    story.append(section('THE BOTTOM LINE'))
    story.append(sp(4))

    story.append(body(
        'The Supreme Court just removed the biggest unpredictable variable in the macro landscape. '
        'IEEPA tariffs were uncapped, open-ended, and subject to presidential whim. Section 122 '
        'tariffs are capped at 15%, expire in 150 days, and face immediate Congressional scrutiny. '
        'That is a fundamentally different risk profile.'
    ))

    story.append(body(
        'But the tariff regime was never the core of our defensive thesis. Labor is. And labor has '
        'not improved. Quits pressing the pre-recessionary threshold, job openings collapsing to '
        '2020 lows, payrolls revised down by 400,000. The economy we are tracking underneath the '
        'headlines has been decelerating for months, and that deceleration is domestic, not '
        'trade-driven.'
    ))

    story.append(body(
        'The SCOTUS ruling lowers the amplitude of the downside scenario. It does not change the '
        'direction. We stay defensive, hold gold as a structural position that has been working for '
        '21 months, and watch the labor data like a hawk.'
    ))

    story.append(sp(12))

    story.append(callout('The penalty for being early to defense is still low.'))
    story.append(callout('The penalty for being wrong-sized on risk is still asymmetric.'))

    story.append(sp(16))
    story.append(hr())
    story.append(sp(12))

    # Sign off
    story.append(Paragraph(
        "Don't navigate in the dark. Join us.",
        styles['LHM_Callout']
    ))
    story.append(sp(8))
    story.append(Paragraph(
        "That's our view from the Watch. Until next time, we'll be sure to keep the light on....",
        styles['LHM_SignOff']
    ))
    story.append(sp(12))
    story.append(Paragraph('MACRO, ILLUMINATED.', styles['LHM_Tagline']))
    story.append(sp(8))
    story.append(Paragraph(
        'Bob Sheehan, CFA, CMT | Founder &amp; Chief Investment Officer',
        styles['LHM_Footer_Author']
    ))
    story.append(Paragraph(
        'Lighthouse Macro | @LHMacro',
        styles['LHM_Footer_Org']
    ))

    # =========================================================================
    # BUILD
    # =========================================================================
    doc.build(story)
    print(f"PDF built successfully: {OUTPUT_PATH}")
    print(f"File size: {os.path.getsize(OUTPUT_PATH) / 1024 / 1024:.1f} MB")


if __name__ == '__main__':
    build_pdf()
