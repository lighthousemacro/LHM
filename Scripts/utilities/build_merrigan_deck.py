#!/usr/bin/env python3
"""Rebuild the LHM Fractional-CIO deck as a clean 16:9 PDF (reportlab).
Refreshed content, consistent dark theme. Replaces the stale merged deck."""
import os
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

W, H = 960, 540  # 13.333 x 7.5 in @ 72dpi -> standard 16:9

# Dark-theme palette (current brand, May 2026): Deep canvas, Bright primary, Offwhite text.
NAVY  = HexColor("#123456")  # Deep — dark-theme canvas
CARD  = HexColor("#1C4870")  # lifted Deep for cards
OCEAN = HexColor("#89CCFF")  # Bright — promoted to primary on dark (Ocean dims on Deep)
SKY   = HexColor("#89CCFF")  # Bright
DUSK  = HexColor("#FF6723")  # Dusk — kept for the signature accent bar
SEA   = HexColor("#89CCFF")  # Bright
VENUS = HexColor("#89CCFF")  # Bright
WHITE = HexColor("#F4F7F9")  # Offwhite — dark-theme text
MUTE  = HexColor("#9FB3C8")
FOG   = HexColor("#5C7186")

# fonts (fall back to Helvetica if brand TTFs not installed)
def _reg():
    dirs = [os.path.expanduser("~/Library/Fonts"), "/Library/Fonts",
            "/System/Library/Fonts", "/System/Library/Fonts/Supplemental"]
    want = {"Mont": ["Montserrat-Bold.ttf"], "MontS": ["Montserrat-SemiBold.ttf"],
            "Body": ["Inter-Regular.ttf", "Inter.ttf"], "BodyB": ["Inter-Bold.ttf"]}
    reg = {}
    for n, fs in want.items():
        for d in dirs:
            h = next((os.path.join(d, f) for f in fs if os.path.exists(os.path.join(d, f))), None)
            if h:
                try: pdfmetrics.registerFont(TTFont(n, h)); reg[n] = 1
                except Exception: pass
                break
    return reg
R = _reg()
F_T  = "Mont"  if "Mont"  in R else "Helvetica-Bold"
F_H  = "MontS" if "MontS" in R else "Helvetica-Bold"
F_B  = "Body"  if "Body"  in R else "Helvetica"
F_BB = "BodyB" if "BodyB" in R else "Helvetica-Bold"

def track(c, x, y, s, font, size, color, gap=2.2):
    c.setFont(font, size); c.setFillColor(color); cx = x
    for ch in s:
        c.drawString(cx, y, ch); cx += c.stringWidth(ch, font, size) + gap
    return cx

def wrap(c, s, font, size, maxw):
    words, lines, cur = s.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if c.stringWidth(t, font, size) <= maxw: cur = t
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines

def para(c, x, y, s, font, size, color, maxw, lead):
    c.setFont(font, size); c.setFillColor(color)
    for ln in wrap(c, s, font, size, maxw):
        c.drawString(x, y, ln); y -= lead
    return y

def frame(c, n=None, dark=True):
    c.setFillColor(NAVY); c.rect(0, 0, W, H, fill=1, stroke=0)
    # top accent bar (Ocean 2/3 + Dusk 1/3)
    c.setFillColor(OCEAN); c.rect(0, H-6, W*0.66, 6, fill=1, stroke=0)
    c.setFillColor(DUSK);  c.rect(W*0.66, H-6, W*0.34, 6, fill=1, stroke=0)
    c.setFillColor(OCEAN); c.rect(0, 0, W*0.66, 4, fill=1, stroke=0)
    c.setFillColor(DUSK);  c.rect(W*0.66, 0, W*0.34, 4, fill=1, stroke=0)
    track(c, 48, H-34, "LIGHTHOUSE MACRO", F_H, 11, OCEAN, gap=2.6)
    if n is not None:
        c.setFont(F_B, 8.5); c.setFillColor(FOG)
        c.drawString(48, 16, "Bob Sheehan, CFA, CMT  |  Lighthouse Macro  |  @LHMacro")
        track(c, W-250, 16, "MACRO, ILLUMINATED.", F_H, 8.5, FOG, gap=1.6)

def head(c, t, sub):
    c.setFont(F_T, 30); c.setFillColor(WHITE); c.drawString(48, H-92, t)
    c.setFillColor(OCEAN); c.rect(48, H-104, 64, 3, fill=1, stroke=0)
    if sub:
        c.setFont(F_B, 13); c.setFillColor(SKY); c.drawString(48, H-128, sub)

def card(c, x, y, w, h, accent):
    c.setFillColor(CARD); c.rect(x, y, w, h, fill=1, stroke=0)
    c.setFillColor(accent); c.rect(x, y, 4, h, fill=1, stroke=0)

# ---------------------------------------------------------------- slides
c = canvas.Canvas("/Users/bob/LHM/Deliverables/Merrigan_2026-06-12/LHM_Advisory_Overview_and_Pricing.pdf",
                  pagesize=(W, H))

# 1 — TITLE
frame(c)
c.setFont(F_T, 46); c.setFillColor(WHITE)
c.drawString(48, H-230, "YOUR FRACTIONAL")
c.drawString(48, H-282, "MACRO CIO")
track(c, 50, H-318, "MACRO, ILLUMINATED.", F_H, 12, OCEAN, gap=4)
c.setFont(F_B, 14); c.setFillColor(MUTE)
c.drawString(48, H-356, "Institutional-grade macro research for advisory firms.")
c.setFont(F_BB, 11); c.setFillColor(SKY)
c.drawString(48, H-392, "Prepared for Michael Merrigan, Oppenheimer & Co.")
c.setFont(F_BB, 12); c.setFillColor(WHITE)
c.drawString(48, H-456, "Bob Sheehan, CFA, CMT")
c.setFont(F_B, 11); c.setFillColor(MUTE)
c.drawString(48, H-474, "Founder & Chief Investment Officer, Lighthouse Macro")
c.showPage()

# 2 — THE PROBLEM
frame(c, 2); head(c, "THE PROBLEM", "Your clients deserve institutional macro. You don't have time to build it.")
stats = [("9 hrs/wk", "spent trying to build a macro view", OCEAN),
         ("$300K+", "cost of a full-time in-house CIO", OCEAN),
         ("68%", "of advisors still managing in-house", OCEAN)]
x, y, w, h = 48, H-280, 280, 96
for (big, small, col) in stats:
    card(c, x, y, w, h, col)
    c.setFont(F_T, 30); c.setFillColor(WHITE); c.drawString(x+22, y+h-44, big)
    para(c, x+22, y+h-66, small, F_B, 11, MUTE, w-40, 14)
    x += w + 16
yy = y - 34
for b in ["Hundreds of economic releases a month. Without a system to weight them, it is noise.",
          "Clients expect macro context when volatility hits. Reactive answers erode confidence.",
          "Time spent building a macro view is time not spent growing the practice."]:
    c.setFillColor(OCEAN); c.circle(58, yy+4, 2.4, fill=1, stroke=0)
    yy = para(c, 72, yy, b, F_B, 12, WHITE, W-130, 17) - 10
c.showPage()

# 3 — THE SOLUTION
frame(c, 3); head(c, "THE SOLUTION", "A fractional macro CIO who becomes part of your team.")
rows = [("WEEKLY ANALYSIS", "The Beacon — a 3 to 4 thousand word synthesis. Your IC-ready briefing each week.", OCEAN),
        ("CLIENT-FACING MATERIALS", "White-labelable commentary, charts, and talking points for client meetings.", OCEAN),
        ("VISUAL DIAGNOSTICS", "The Chartbook — 50 to 75 charts. Institutional-quality visuals for your presentations.", OCEAN),
        ("REGIME SIGNAL", "One MRI reading maps to an allocation range. Systematic, not gut feel.", OCEAN),
        ("CRISIS ACCESS", "Direct strategist access during volatility events. Your clients will not wait for Monday.", OCEAN)]
y = H-176
for (lab, desc, col) in rows:
    c.setFillColor(col); c.rect(48, y-4, 4, 24, fill=1, stroke=0)
    c.setFont(F_BB, 12.5); c.setFillColor(col); c.drawString(62, y+4, lab)
    c.setFont(F_B, 12); c.setFillColor(WHITE); c.drawString(330, y+4, desc[:200])
    y -= 64
c.showPage()

# 4 — THE FRAMEWORK
frame(c, 4); head(c, "THE FRAMEWORK", "Twelve pillars across three engines, distilled into one regime signal.")
engines = [("MACRO DYNAMICS", "Labor · Prices · Growth · Housing · Consumer · Business · Trade", OCEAN),
           ("MONETARY MECHANICS", "Government · Financial · Plumbing", OCEAN),
           ("MARKET STRUCTURE", "Market Structure · Sentiment", OCEAN)]
y = H-178
for (lab, items, col) in engines:
    card(c, 48, y-30, 560, 40, col)
    c.setFont(F_BB, 11.5); c.setFillColor(col); c.drawString(64, y-2, lab)
    c.setFont(F_B, 10.5); c.setFillColor(MUTE); c.drawString(64, y-20, items)
    y -= 56
# MRI box on right
card(c, 640, H-290, 272, 152, OCEAN)
c.setFont(F_T, 17); c.setFillColor(WHITE); c.drawString(660, H-176, "MACRO RISK")
c.drawString(660, H-196, "INDEX  (MRI)")
para(c, 660, H-224, "One composite. 2,500+ series. Low Risk to Crisis, mapped to an allocation range.",
     F_B, 11, MUTE, 236, 15)
yy = H-330
c.setFont(F_BB, 11.5); c.setFillColor(OCEAN); c.drawString(48, yy, "WHAT THIS MEANS FOR YOUR PRACTICE")
yy -= 24
for b in ["A systematic regime signal that anchors your allocation conversations with clients.",
          "The confidence to explain why you are positioned the way you are with data, not gut.",
          "Explicit invalidation criteria, so clients know you have a plan if the view is wrong."]:
    c.setFillColor(OCEAN); c.circle(58, yy+4, 2.4, fill=1, stroke=0)
    yy = para(c, 72, yy, b, F_B, 12, WHITE, W-130, 16) - 8
c.showPage()

# 5 — FRAMEWORK IN ACTION
frame(c, 5); head(c, "FRAMEWORK IN ACTION", "January–February 2026: the system flagged High Risk early.")
proof = [("+7.9%", "XLU  (Utilities)", OCEAN), ("+7.6%", "XLP  (Staples)", OCEAN), ("FLAT", "SPY  (S&P 500)", FOG)]
x, y, w, h = 48, H-272, 280, 92
for (big, small, col) in proof:
    card(c, x, y, w, h, col)
    c.setFont(F_T, 30); c.setFillColor(WHITE); c.drawString(x+22, y+h-44, big)
    c.setFont(F_B, 11.5); c.setFillColor(MUTE); c.drawString(x+22, y+24, small)
    x += w + 16
yy = y - 26
yy = para(c, 48, yy, "MRI moved to High Risk in mid-January. The defensive basket outperformed a flat S&P by roughly 7 to 8 percent over five weeks.",
          F_B, 12, WHITE, W-96, 17) - 14
card(c, 48, yy-58, W-96, 56, OCEAN)
para(c, 66, yy-20, "The system picks the regime's defensive. Then it was utilities and staples. Today, in a real-rate regime, it is cash and quality. Same discipline, different trade.",
     F_B, 11.5, WHITE, W-130, 16)
c.showPage()

# 6 — ABOUT BOB
frame(c, 6); head(c, "ABOUT BOB", "Bob Sheehan, CFA, CMT — Founder & Chief Investment Officer.")
bullets = [
 "Bank of America Private Bank: Associate PM on the Strategic Growth Strategy macro-equities sleeve (~$1.2B).",
 "Tenure track record (Feb 2017–Jan 2020): 2.35 Sortino, 103% upside / 76% downside capture vs the S&P 500.",
 "EquiLend: VP, Data & Analytics — built proprietary indicators on short-sale data, published research.",
 "CFA Charterholder · CMT Charterholder · BrainStation Data Science.",
 "Code-first: 2,500+ data series, an automated daily pipeline, a Python-driven framework.",
 "Featured in FT Alphaville, Forward Guidance (Blockworks), WealthVest, and Less Noise More Signal.",
]
yy = H-168
for b in bullets:
    c.setFillColor(OCEAN); c.circle(58, yy+4, 2.4, fill=1, stroke=0)
    yy = para(c, 72, yy, b, F_B, 12, WHITE, W-130, 16) - 9
card(c, 48, yy-50, W-96, 44, OCEAN)
c.setFont(F_B, 12); c.setFillColor(SKY)
c.drawString(66, yy-30, "\"The framework does the work so the analysis stays honest. Every view comes with what would change our mind.\"")
c.showPage()

# 7 — ENGAGEMENT & PRICING
frame(c, 7); head(c, "ENGAGEMENT & PRICING", "The advisory engagement. No AUM fees. No lock-in.")
tiers = [("ADVISORY", ["The research suite, included.", "Monthly strategy calls.", "Client-facing + white-label materials.", "Direct access when volatility hits."], "$2,500/mo", OCEAN),
         ("FRACTIONAL CIO", ["Everything in Advisory, plus:", "IC participation. Model review.", "Crisis access. Quarterly outlook ghostwriting."], "Custom retainer", OCEAN)]
x, w, h, y = 48, 420, 250, H-388
for (lab, lines, price, col) in tiers:
    c.setFillColor(CARD); c.rect(x, y, w, h, fill=1, stroke=0)
    c.setFillColor(col); c.rect(x, y+h-5, w, 5, fill=1, stroke=0)
    c.setFont(F_BB, 13); c.setFillColor(col); c.drawString(x+18, y+h-30, lab)
    ly = y+h-58
    for ln in lines:
        c.setFont(F_B, 10.5); c.setFillColor(WHITE); c.drawString(x+18, ly, ln); ly -= 16
    c.setFont(F_BB, 16); c.setFillColor(WHITE); c.drawString(x+18, y+18, price)
    x += w + 24
c.setFont(F_B, 11.5); c.setFillColor(MUTE)
c.drawCentredString(W/2, y-26, "A full-time CIO runs $300K+ a year. This is institutional depth at a fraction of it.")
c.showPage()

# 8 — CLOSE
frame(c)
c.setFont(F_T, 40); c.setFillColor(WHITE); c.drawCentredString(W/2, H-250, "LIGHTHOUSE MACRO")
track(c, W/2-150, H-288, "MACRO, ILLUMINATED.", F_H, 13, OCEAN, gap=5)
c.setFont(F_BB, 13); c.setFillColor(WHITE); c.drawCentredString(W/2, H-356, "Bob Sheehan, CFA, CMT")
c.setFont(F_B, 11); c.setFillColor(MUTE); c.drawCentredString(W/2, H-374, "Founder & Chief Investment Officer")
c.setFont(F_B, 11.5); c.setFillColor(SKY)
c.drawCentredString(W/2, H-410, "bob@lighthousemacro.com    ·    @LHMacro    ·    research.lighthousemacro.com")
c.showPage()

c.save()
print("built LHM_Advisory_Overview_and_Pricing.pdf (8 slides)")
