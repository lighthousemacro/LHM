#!/usr/bin/env python3
"""Build the CoinRabbit partnership proposal deck as a 7-page 16:9 PDF (reportlab).
Light theme per the June 2026 palette lock: Glacier base, Deep ink, Ocean primary."""
import os
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

W, H = 960, 540  # 16:9 landscape

OCEAN    = HexColor("#2389BB")
DUSK     = HexColor("#FF6723")
SKY      = HexColor("#89CCFF")
DEEP     = HexColor("#123456")
SEA      = HexColor("#00BB89")
GLACIER  = HexColor("#F4F7F9")
ICE      = HexColor("#D1E1F1")
DOLDRUMS = HexColor("#898989")
FOAM     = HexColor("#FFFFFF")

FONT_DIR = os.environ.get(
    "LHM_FONT_DIR",
    "/private/tmp/claude-502/-Users-bob-LHM/7a4c4a74-3333-4c23-849e-f702eb24571d/scratchpad/fonts")

def _reg():
    want = {"Mont": "Montserrat-Bold.ttf", "MontS": "Montserrat-SemiBold.ttf",
            "Body": "Inter-Regular.ttf", "BodyS": "Inter-SemiBold.ttf",
            "BodyB": "Inter-Bold.ttf", "Code": "SourceCodePro-Semibold.ttf"}
    reg = {}
    dirs = [FONT_DIR, os.path.expanduser("~/Library/Fonts"), "/Library/Fonts"]
    for n, f in want.items():
        for d in dirs:
            p = os.path.join(d, f)
            if os.path.exists(p):
                try:
                    pdfmetrics.registerFont(TTFont(n, p)); reg[n] = 1
                except Exception:
                    pass
                break
    return reg

R = _reg()
F_T  = "Mont"  if "Mont"  in R else "Helvetica-Bold"   # titles
F_H  = "MontS" if "MontS" in R else "Helvetica-Bold"   # subheads / kickers
F_B  = "Body"  if "Body"  in R else "Helvetica"        # body
F_BS = "BodyS" if "BodyS" in R else "Helvetica-Bold"   # body semibold
F_BB = "BodyB" if "BodyB" in R else "Helvetica-Bold"   # body bold
F_C  = "Code"  if "Code"  in R else "Courier-Bold"     # prices / data

def track(c, x, y, s, font, size, color, gap=2.2):
    c.setFont(font, size); c.setFillColor(color); cx = x
    for ch in s:
        c.drawString(cx, y, ch); cx += c.stringWidth(ch, font, size) + gap
    return cx

def track_w(c, s, font, size, gap=2.2):
    return sum(c.stringWidth(ch, font, size) + gap for ch in s) - gap

def wrap(c, s, font, size, maxw):
    words, lines, cur = s.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if c.stringWidth(t, font, size) <= maxw:
            cur = t
        else:
            lines.append(cur); cur = w
    if cur:
        lines.append(cur)
    return lines

def para(c, x, y, s, font, size, color, maxw, lead):
    c.setFont(font, size); c.setFillColor(color)
    for ln in wrap(c, s, font, size, maxw):
        c.drawString(x, y, ln); y -= lead
    return y

def footer(c, page=None):
    """One-line hyperlinked footer, Ocean links, on every page."""
    y = 18
    segs = [("Lighthouse Macro", "https://lighthousemacro.com"),
            ("Research", "https://research.lighthousemacro.com"),
            ("@LHMacro", "https://x.com/LHMacro")]
    size = 8.5
    x = 48
    for i, (label, url) in enumerate(segs):
        c.setFont(F_BS, size); c.setFillColor(OCEAN)
        w = c.stringWidth(label, F_BS, size)
        c.drawString(x, y, label)
        c.linkURL(url, (x - 1, y - 3, x + w + 1, y + size), relative=0)
        x += w
        if i < len(segs) - 1:
            c.setFillColor(DOLDRUMS); c.setFont(F_B, size)
            c.drawString(x + 6, y, "|")
            x += 6 + c.stringWidth("|", F_B, size) + 6
    if page is not None:
        c.setFont(F_B, 8.5); c.setFillColor(DOLDRUMS)
        c.drawRightString(W - 48, y, f"{page} / 7")
        tw = track_w(c, "MACRO, ILLUMINATED.", F_H, 8.5, gap=1.6)
        track(c, (W - tw) / 2, y, "MACRO, ILLUMINATED.", F_H, 8.5, DOLDRUMS, gap=1.6)

def frame(c, page=None):
    c.setFillColor(GLACIER); c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setFillColor(OCEAN); c.rect(0, H - 6, W * 0.66, 6, fill=1, stroke=0)
    c.setFillColor(DUSK);  c.rect(W * 0.66, H - 6, W * 0.34, 6, fill=1, stroke=0)
    if page is not None:
        track(c, 48, H - 34, "LIGHTHOUSE MACRO", F_H, 10.5, OCEAN, gap=2.6)
    footer(c, page)

def head(c, t, sub=None):
    c.setFont(F_T, 27); c.setFillColor(DEEP); c.drawString(48, H - 88, t)
    c.setFillColor(DUSK); c.rect(48, H - 100, 64, 3, fill=1, stroke=0)
    if sub:
        c.setFont(F_B, 12.5); c.setFillColor(DOLDRUMS); c.drawString(48, H - 124, sub)

def card(c, x, y, w, h, accent=None, fill=FOAM):
    c.setFillColor(fill); c.setStrokeColor(ICE); c.setLineWidth(1)
    c.roundRect(x, y, w, h, 6, fill=1, stroke=1)
    if accent is not None:
        c.setFillColor(accent); c.rect(x, y + 8, 3.5, h - 16, fill=1, stroke=0)

OUT_DIR = "/Users/bob/LHM/Deliverables/CoinRabbit_2026-07-09"
os.makedirs(OUT_DIR, exist_ok=True)
OUT = os.path.join(OUT_DIR, "LHM_CoinRabbit_Partnership_Proposal_2026-07-09.pdf")

c = canvas.Canvas(OUT, pagesize=(W, H))
c.setTitle("Lighthouse Macro | Research Partnership Proposal | CoinRabbit")
c.setAuthor("Bob Sheehan, CFA, CMT")
c.setSubject("Research Partnership Proposal, prepared for CoinRabbit, July 2026")

# ------------------------------------------------------------- 1 COVER
frame(c)
track(c, 48, H - 150, "LIGHTHOUSE MACRO", F_T, 21, DEEP, gap=4.5)
track(c, 50, H - 176, "MACRO, ILLUMINATED.", F_H, 10.5, OCEAN, gap=3.2)
c.setFont(F_T, 44); c.setFillColor(DEEP)
c.drawString(48, H - 270, "RESEARCH PARTNERSHIP")
c.drawString(48, H - 318, "PROPOSAL")
c.setFillColor(DUSK); c.rect(48, H - 340, 88, 4, fill=1, stroke=0)
c.setFont(F_BS, 15); c.setFillColor(OCEAN)
c.drawString(48, H - 374, "Prepared for CoinRabbit  ·  July 2026")
c.setFont(F_BB, 12.5); c.setFillColor(DEEP)
c.drawString(48, H - 448, "Bob Sheehan, CFA, CMT")
c.setFont(F_B, 11); c.setFillColor(DOLDRUMS)
c.drawString(48, H - 466, "Head of Macro Strategy & Chief Investment Officer")
c.showPage()

# ------------------------------------------- 2 LIGHTHOUSE MACRO AT A GLANCE
frame(c, 2)
head(c, "LIGHTHOUSE MACRO AT A GLANCE")
intro = ("Lighthouse Macro is an independent macro research firm. We cover the full landscape, "
         "the real economy, the monetary system, and market internals, and we publish the view "
         "with the data that would prove it wrong. Led by Bob Sheehan, CFA, CMT, formerly "
         "portfolio management for HNW and UHNW clients at Bank of America Private Bank.")
para(c, 48, H - 128, intro, F_B, 12, DEEP, W - 96, 17)

points = [
    ("TWELVE PILLARS, THREE ENGINES",
     "Macro Dynamics, Monetary Mechanics, and Market Technicals, synthesized into one regime "
     "signal, the Macro Risk Index."),
    ("SIX ASSET CLASSES",
     "Equities, fixed income, crypto, currencies, commodities, and cash. Crypto is read as one "
     "flow among many."),
    ("EXPLICIT THRESHOLDS",
     "Every call is published with the levels that would make us wrong, before the market "
     "decides it for us."),
    ("2,500+ SERIES, REFRESHED DAILY",
     "A proprietary database spanning labor, prices, credit, liquidity, positioning, and "
     "on-chain flows."),
    ("CRYPTO FLUENT",
     "Creator of the Crypto Liquidity Index. We treat digital assets as a liquidity read, "
     "written in plain macro language."),
]
gw, gh, gx0, gy0 = 275, 108, 48, H - 300
for i, (t, d) in enumerate(points[:3]):
    x = gx0 + i * (gw + 20)
    card(c, x, gy0, gw, gh, OCEAN)
    c.setFont(F_H, 10.5); c.setFillColor(OCEAN)
    yy = gy0 + gh - 24
    for ln in wrap(c, t, F_H, 10.5, gw - 34):
        c.drawString(x + 18, yy, ln); yy -= 13
    para(c, x + 18, yy - 6, d, F_B, 10, DEEP, gw - 34, 13.5)
gy1 = gy0 - gh - 18
for i, (t, d) in enumerate(points[3:]):
    x = gx0 + i * (gw + 20)
    card(c, x, gy1, gw, gh, OCEAN)
    c.setFont(F_H, 10.5); c.setFillColor(OCEAN)
    yy = gy1 + gh - 24
    for ln in wrap(c, t, F_H, 10.5, gw - 34):
        c.drawString(x + 18, yy, ln); yy -= 13
    para(c, x + 18, yy - 6, d, F_B, 10, DEEP, gw - 34, 13.5)
# third slot on second row: quiet framing statement
x = gx0 + 2 * (gw + 20)
card(c, x, gy1, gw, gh, fill=ICE)
para(c, x + 18, gy1 + gh - 30,
     "Institutional rigor, written for humans. Educational, data-driven, and calm when the "
     "tape is not.", F_BS, 10.5, DEEP, gw - 34, 14.5)
c.showPage()

# --------------------------------------------------- 3 PARTNERSHIP PRINCIPLES
frame(c, 3)
head(c, "PARTNERSHIP PRINCIPLES", "The ground rules that make this work for both audiences.")
principles = [
    ("EDUCATIONAL, NEVER PROMOTIONAL",
     "Data-driven analysis with explicit thresholds and invalidation criteria. No hype, no "
     "sensationalism, nothing your clients would read as a shill."),
    ("HOLISTIC MACRO, CRYPTO FLUENT",
     "World economics first, exactly as your managers asked. Crypto gets covered with real "
     "fluency, grounded in the Crypto Liquidity Index."),
    ("FULL ATTRIBUTION, ALWAYS",
     "Name, photo, and links on every piece. Short versions for your socials, long versions "
     "for your blog and private client chats."),
    ("START SMALL, SCALE WHAT WORKS",
     "A three-month baseline proves the fit. Expansion follows evidence, on your side and "
     "ours."),
    ("INDEPENDENT BY DESIGN",
     "Our research is never a product endorsement. That protects your credibility with your "
     "clients as much as it protects ours."),
]
y = H - 158
for i, (t, d) in enumerate(principles):
    card(c, 48, y - 52, W - 96, 62, OCEAN if i != 4 else DUSK)
    c.setFont(F_C, 15); c.setFillColor(SKY if i != 4 else DUSK)
    c.drawString(66, y - 22, f"0{i+1}")
    c.setFont(F_H, 12); c.setFillColor(DEEP); c.drawString(104, y - 14, t)
    para(c, 104, y - 32, d, F_B, 10.5, DOLDRUMS, W - 200, 13.5)
    y -= 72
c.showPage()

# ------------------------------------------------------ 4 PROGRAM STRUCTURE
frame(c, 4)
head(c, "PROGRAM STRUCTURE", "Two ways in. Same research, different cadence.")
pw, ph, py = 412, 264, H - 410
# Core panel
x = 48
card(c, x, py, pw, ph, fill=FOAM)
c.setFillColor(OCEAN); c.rect(x, py + ph - 5, pw, 5, fill=1, stroke=0)
c.setFont(F_H, 13.5); c.setFillColor(OCEAN); c.drawString(x + 24, py + ph - 36, "CORE SPONSORSHIP")
c.setFont(F_C, 26); c.setFillColor(DEEP); c.drawString(x + 24, py + ph - 72, "$7,500 / month")
c.setFont(F_B, 10); c.setFillColor(DOLDRUMS)
c.drawString(x + 24, py + ph - 90, "The syndication license.")
core = ["3 to 4 LHM research pieces per month, selected by us",
        "Verbatim syndication with full attribution, every time",
        "Short-form for your socials, long-form for your blog",
        "Long-form delivery into your private client chats",
        "One quarterly Chartbook edition for private channels"]
ly = py + ph - 118
for ln in core:
    c.setFillColor(OCEAN); c.circle(x + 28, ly + 3, 2.0, fill=1, stroke=0)
    c.setFont(F_B, 10.5); c.setFillColor(DEEP); c.drawString(x + 38, ly, ln); ly -= 21
# Full panel
x = 48 + pw + 28
card(c, x, py, pw, ph, fill=FOAM)
c.setFillColor(DUSK); c.rect(x, py + ph - 5, pw, 5, fill=1, stroke=0)
c.setFont(F_H, 13.5); c.setFillColor(DUSK); c.drawString(x + 24, py + ph - 36, "FULL PROGRAM")
c.setFont(F_C, 26); c.setFillColor(DEEP); c.drawString(x + 24, py + ph - 72, "$12,500 / month")
c.setFont(F_B, 10); c.setFillColor(DOLDRUMS)
c.drawString(x + 24, py + ph - 90, "Core, plus the commissioned cadence from your recap.")
full = ["Everything in Core Sponsorship",
        "Up to four commissioned pieces per month",
        "Built around the narratives your team is seeing",
        "Priority turnaround on every commissioned draft",
        "One revision round per piece, delivered for your channels"]
ly = py + ph - 118
for ln in full:
    c.setFillColor(DUSK); c.circle(x + 28, ly + 3, 2.0, fill=1, stroke=0)
    c.setFont(F_B, 10.5); c.setFillColor(DEEP); c.drawString(x + 38, ly, ln); ly -= 21
# equivalence math
card(c, 48, py - 68, W - 96, 54, fill=ICE)
c.setFont(F_BS, 11); c.setFillColor(DEEP)
c.drawCentredString(W / 2, py - 34,
    "Assembled piece by piece, Core plus four commissioned pieces runs $15,500 a month.")
c.drawCentredString(W / 2, py - 52,
    "The Full Program packages the same work at $12,500, roughly 19% below the à la carte build.")
c.showPage()

# ------------------------------------------------ 5 COMMISSIONED COMMENTARY
frame(c, 5)
head(c, "COMMISSIONED COMMENTARY", "Your narratives, our research. Written by us, published to your channels.")
steps = [
    ("YOU SHARE THE NARRATIVE",
     "A theme your clients are talking about. Input from your Chief Strategy Officer is "
     "welcome here."),
    ("WE SCOPE THE ANGLE",
     "One email to lock the framing, the data we will use, and the delivery date."),
    ("DRAFT IN FIVE BUSINESS DAYS",
     "Research-grade work on your clock. Priority turnaround inside the Full Program."),
    ("ONE REVISION, THEN DELIVERY",
     "Ships for your channels with full attribution and co-branding where it helps."),
]
sw, sh, sy = 204, 178, H - 366
for i, (t, d) in enumerate(steps):
    x = 48 + i * (sw + 16)
    card(c, x, sy, sw, sh, fill=FOAM)
    c.setFillColor(OCEAN); c.rect(x, sy + sh - 5, sw, 5, fill=1, stroke=0)
    c.setFont(F_C, 20); c.setFillColor(SKY); c.drawString(x + 18, sy + sh - 40, f"0{i+1}")
    c.setFont(F_H, 10.5); c.setFillColor(DEEP)
    yy = sy + sh - 64
    for ln in wrap(c, t, F_H, 10.5, sw - 34):
        c.drawString(x + 18, yy, ln); yy -= 13.5
    para(c, x + 18, yy - 8, d, F_B, 9.5, DOLDRUMS, sw - 34, 13)
    if i < 3:
        c.setFont(F_T, 14); c.setFillColor(DOLDRUMS)
        c.drawString(x + sw + 3.5, sy + sh / 2 - 5, "›")
card(c, 48, sy - 66, W - 96, 50, fill=ICE)
c.setFont(F_C, 15); c.setFillColor(DEEP)
c.drawString(66, sy - 40, "$2,000 per piece à la carte")
c.setFont(F_B, 10.5); c.setFillColor(DEEP)
c.drawString(66, sy - 56, "30-day exclusivity on your channels, then the piece reverts to the LHM archive.")
c.showPage()

# --------------------------------------- 6 PREMIUM RESEARCH LICENSING (OPTIONAL)
frame(c, 6)
head(c, "PREMIUM RESEARCH LICENSING", "Optional add-on. Full LHM paid-tier access for your Private Program clients.")
# left: what a seat includes
lw, lh, ly0 = 430, 280, H - 424
card(c, 48, ly0, lw, lh, fill=FOAM)
c.setFillColor(OCEAN); c.rect(48, ly0 + lh - 5, lw, 5, fill=1, stroke=0)
c.setFont(F_H, 12.5); c.setFillColor(OCEAN); c.drawString(72, ly0 + lh - 34, "WHAT A SEAT INCLUDES")
inc = [("The Beacon", "Weekly long-form analysis, the flagship."),
       ("The Beam", "Twice-weekly data-driven insight, five charts each."),
       ("The Horizon", "The monthly forward outlook."),
       ("Chartbooks", "The full visual read of the macro landscape."),
       ("Indicator readings", "Real-time levels on the proprietary composites.")]
yy = ly0 + lh - 64
for t, d in inc:
    c.setFillColor(OCEAN); c.circle(76, yy + 3, 2.0, fill=1, stroke=0)
    c.setFont(F_BS, 11); c.setFillColor(DEEP); c.drawString(88, yy, t)
    c.setFont(F_B, 10); c.setFillColor(DOLDRUMS)
    c.drawString(88 + c.stringWidth(t, F_BS, 11) + 8, yy, d)
    yy -= 42
# right: seat table
rx = 48 + lw + 28
rw = W - 96 - lw - 28
card(c, rx, ly0, rw, lh, fill=FOAM)
c.setFillColor(OCEAN); c.rect(rx, ly0 + lh - 5, rw, 5, fill=1, stroke=0)
c.setFont(F_H, 12.5); c.setFillColor(OCEAN); c.drawString(rx + 24, ly0 + lh - 34, "SEAT PRICING")
rows = [("10-24 seats", "$400 / seat / yr"),
        ("25-49 seats", "$350 / seat / yr"),
        ("50+ seats",   "$300 / seat / yr")]
yy = ly0 + lh - 66
for i, (a, b) in enumerate(rows):
    if i % 2 == 0:
        c.setFillColor(GLACIER); c.rect(rx + 16, yy - 12, rw - 32, 34, fill=1, stroke=0)
    c.setFont(F_B, 11.5); c.setFillColor(DEEP); c.drawString(rx + 28, yy, a)
    c.setFont(F_C, 12.5); c.setFillColor(DEEP); c.drawRightString(rx + rw - 28, yy, b)
    yy -= 40
para(c, rx + 24, yy + 4,
     "Annual prepay. Named users, non-transferable, no redistribution. 10-seat minimum.",
     F_B, 9.5, DOLDRUMS, rw - 48, 13)
card(c, 48, ly0 - 54, W - 96, 42, fill=ICE)
c.setFont(F_BS, 11.5); c.setFillColor(DEEP)
c.drawCentredString(W / 2, ly0 - 30,
    "This is how your Private Program clients get everything we publish, in full, the moment it ships.")
c.showPage()

# --------------------------------------------------------- 7 TERMS & TIMELINE
frame(c, 7)
head(c, "TERMS & TIMELINE", "Simple structure, clean start.")
terms = [
    ("TERM", "Three-month initial program. Month-to-month after, with 30 days' notice either way."),
    ("BILLING", "Month one invoiced at signing. The first deliverable ships once payment clears."),
    ("EDITORIAL", "We select the syndication pieces and they run verbatim. Commissioned drafts include one revision round."),
    ("ANNOUNCEMENTS", "Partnership announcement language requires mutual approval from both teams."),
    ("START", "Proposed start: week of July 20, 2026."),
]
y = H - 150
for t, d in terms:
    card(c, 48, y - 30, W - 96, 44, OCEAN)
    c.setFont(F_H, 11); c.setFillColor(OCEAN); c.drawString(70, y - 12, t)
    c.setFont(F_B, 11.5); c.setFillColor(DEEP); c.drawString(240, y - 12, d)
    y -= 56
c.setFont(F_BS, 12); c.setFillColor(DEEP)
c.drawString(48, y - 12, "Bob Sheehan, CFA, CMT   ·   Head of Macro Strategy & Chief Investment Officer")
c.setFont(F_BS, 12); c.setFillColor(OCEAN)
em = "bob@lighthousemacro.com"
c.drawString(48, y - 32, em)
c.linkURL("mailto:bob@lighthousemacro.com", (47, y - 36, 48 + c.stringWidth(em, F_BS, 12), y - 20), relative=0)
c.showPage()

c.save()
print(f"built {OUT}")
print(f"fonts registered: {sorted(R.keys())}")
