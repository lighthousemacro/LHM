#!/usr/bin/env python3
"""
Print-authored branded PDF for any Lighthouse Macro piece.

Re-flows a published LHM HTML (Beacon / Beam / Horizon / Educational)
through reportlab so pagination is controlled — no sliced charts, no
orphan-whitespace pages — matching the Horizon / Labor pristine bar.
Single source of truth is the published HTML: text and charts already
interleaved in document order with their own captions.

Handles the structural variants seen across LHM HTML:
  - root container: .lhm-beacon / article / main / densest div / body
  - figure caption: internal <figcaption>, OR a following
    <p class="caption"> sibling (no figcaption), OR an .lhm-figsrc span
  - page chrome to skip: header.masthead, footer.branding, .lhm-footer,
    nav / .lhm-toc, .lhm-header-rule

Usage:
    build_branded_pdf.py INPUT.html OUTPUT.pdf \\
        --label "The Beacon" --date "May 3, 2026" \\
        [--title "Override Title"] [--subtitle "Override deck"]
"""

from __future__ import annotations

import io
import os
import re
import sys
import base64
import argparse
from pathlib import Path

from bs4 import BeautifulSoup, NavigableString, Tag
from PIL import Image as PILImage
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Flowable, KeepTogether,
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

OCEAN   = HexColor("#2389BB")
DUSK    = HexColor("#FF6723")
INK     = HexColor("#1a1a1a")
BODYINK = HexColor("#222222")
MUTED   = HexColor("#6b7280")
RULE    = HexColor("#d8dee4")
EXECBG  = HexColor("#f4f7f9")

PAGE_W, PAGE_H = letter
M_LR, M_TOP, M_BOT = 0.62 * inch, 0.62 * inch, 0.66 * inch
CONTENT_W = PAGE_W - 2 * M_LR

# Set from CLI in build(); used by the page furniture.
RUN = {"label": "Lighthouse Macro", "date": ""}


def _register_fonts() -> dict:
    dirs = [os.path.expanduser("~/Library/Fonts"), "/Library/Fonts",
            "/System/Library/Fonts", "/System/Library/Fonts/Supplemental"]
    want = {
        "Montserrat-Bold": ["Montserrat-Bold.ttf"],
        "Montserrat-SemiBold": ["Montserrat-SemiBold.ttf"],
        "Inter": ["Inter-Regular.ttf", "Inter.ttf", "Inter-Regular.otf"],
        "Inter-Bold": ["Inter-Bold.ttf", "Inter-Bold.otf"],
        "Inter-Italic": ["Inter-Italic.ttf", "Inter-Italic.otf"],
    }
    reg = {}
    for name, files in want.items():
        for d in dirs:
            hit = next((os.path.join(d, f) for f in files
                        if os.path.exists(os.path.join(d, f))), None)
            if hit:
                try:
                    pdfmetrics.registerFont(TTFont(name, hit)); reg[name] = True
                except Exception:
                    pass
                break
    return reg


REG = _register_fonts()
F_TITLE = "Montserrat-Bold" if "Montserrat-Bold" in REG else "Helvetica-Bold"
F_H = "Montserrat-Bold" if "Montserrat-Bold" in REG else "Helvetica-Bold"
F_H3 = "Montserrat-SemiBold" if "Montserrat-SemiBold" in REG else "Helvetica-Bold"
F_BODY = "Inter" if "Inter" in REG else "Helvetica"
F_BODY_B = "Inter-Bold" if "Inter-Bold" in REG else "Helvetica-Bold"
F_BODY_I = "Inter-Italic" if "Inter-Italic" in REG else "Helvetica-Oblique"

ST = {
    "title": ParagraphStyle("title", fontName=F_TITLE, fontSize=27, leading=31,
                             textColor=OCEAN, spaceAfter=4),
    "kicker": ParagraphStyle("kicker", fontName=F_BODY_B, fontSize=8.5,
                             leading=11, textColor=DUSK, spaceAfter=4),
    "deck": ParagraphStyle("deck", fontName=F_BODY_I, fontSize=11.5,
                            leading=15, textColor=MUTED, spaceAfter=6),
    "byline": ParagraphStyle("byline", fontName=F_BODY, fontSize=9.5,
                             leading=12, textColor=MUTED, spaceAfter=12),
    "h2": ParagraphStyle("h2", fontName=F_H, fontSize=15.5, leading=19,
                          textColor=OCEAN, spaceBefore=15, spaceAfter=6,
                          keepWithNext=True),
    "h3": ParagraphStyle("h3", fontName=F_H3, fontSize=12, leading=15.5,
                          textColor=INK, spaceBefore=10, spaceAfter=4,
                          keepWithNext=True),
    "body": ParagraphStyle("body", fontName=F_BODY, fontSize=10.3, leading=15,
                            textColor=BODYINK, alignment=TA_JUSTIFY,
                            spaceAfter=8),
    "exec": ParagraphStyle("exec", fontName=F_BODY, fontSize=10.3, leading=15,
                            textColor=BODYINK, alignment=TA_JUSTIFY,
                            spaceAfter=7, leftIndent=10, rightIndent=10),
    "mono": ParagraphStyle("mono", fontName="Courier", fontSize=9.5,
                            leading=13, textColor=INK, spaceAfter=8,
                            leftIndent=10, rightIndent=10),
    "cap": ParagraphStyle("cap", fontName=F_BODY_B, fontSize=8.6, leading=11,
                          textColor=INK, alignment=TA_LEFT, spaceBefore=5,
                          spaceAfter=1),
    "src": ParagraphStyle("src", fontName=F_BODY_I, fontSize=7.6, leading=10,
                          textColor=MUTED, spaceAfter=10),
    "signoff": ParagraphStyle("signoff", fontName=F_BODY_I, fontSize=10.5,
                              leading=15, textColor=OCEAN, spaceBefore=8,
                              spaceAfter=8),
    "cta": ParagraphStyle("cta", fontName=F_BODY_B, fontSize=10.5, leading=15,
                          textColor=OCEAN, alignment=TA_CENTER,
                          spaceBefore=8, spaceAfter=8),
}


class AccentBar(Flowable):
    def __init__(self, width, height=5, sp_before=0, sp_after=0):
        super().__init__()
        self.width, self.height = width, height
        self.sp_before, self.sp_after = sp_before, sp_after

    def wrap(self, *a):
        return (self.width, self.height + self.sp_before + self.sp_after)

    def draw(self):
        c = self.canv
        c.translate(0, self.sp_after)
        bw = self.width * 2 / 3
        c.setFillColor(OCEAN); c.rect(0, 0, bw, self.height, fill=1, stroke=0)
        c.setFillColor(DUSK)
        c.rect(bw, 0, self.width - bw, self.height, fill=1, stroke=0)


class Rule(Flowable):
    def __init__(self, width, color=RULE, t=0.6):
        super().__init__()
        self.width, self.color, self.t = width, color, t

    def draw(self):
        self.canv.setStrokeColor(self.color)
        self.canv.setLineWidth(self.t)
        self.canv.line(0, 0, self.width, 0)


class TintBox(Flowable):
    """Light-tinted rounded panel behind a set of flowables (exec summary)."""
    def __init__(self, flowables, width, pad=10, bg=EXECBG, bar=OCEAN):
        super().__init__()
        self.flowables = flowables
        self.width = width
        self.pad = pad
        self.bg = bg
        self.bar = bar
        self._h = 0

    def wrap(self, aw, ah):
        h = self.pad * 2
        for f in self.flowables:
            _, fh = f.wrap(self.width - 2 * self.pad - 6, ah)
            h += fh
        self._h = h
        return (self.width, h)

    def draw(self):
        c = self.canv
        c.setFillColor(self.bg)
        c.roundRect(0, 0, self.width, self._h, 5, fill=1, stroke=0)
        c.setFillColor(self.bar)
        c.rect(0, 0, 3, self._h, fill=1, stroke=0)
        y = self._h - self.pad
        for f in self.flowables:
            fw, fh = f.wrap(self.width - 2 * self.pad - 6, self._h)
            f.drawOn(c, self.pad + 6, y - fh)
            y -= fh


def _page(canvas, doc):
    canvas.saveState()
    bw = CONTENT_W * 2 / 3
    ty = PAGE_H - 0.42 * inch
    canvas.setFillColor(OCEAN); canvas.rect(M_LR, ty, bw, 3, fill=1, stroke=0)
    canvas.setFillColor(DUSK)
    canvas.rect(M_LR + bw, ty, CONTENT_W - bw, 3, fill=1, stroke=0)
    canvas.setFont(F_H, 7.5); canvas.setFillColor(OCEAN)
    canvas.drawString(M_LR, ty + 7, "LIGHTHOUSE MACRO")
    canvas.setFont(F_BODY, 7.5); canvas.setFillColor(MUTED)
    canvas.drawRightString(PAGE_W - M_LR, ty + 7,
                           f"{RUN['label']}  ·  {RUN['date']}".strip(" ·"))
    by = M_BOT - 0.30 * inch
    canvas.setFillColor(OCEAN); canvas.rect(M_LR, by, bw, 3, fill=1, stroke=0)
    canvas.setFillColor(DUSK)
    canvas.rect(M_LR + bw, by, CONTENT_W - bw, 3, fill=1, stroke=0)
    canvas.setFont(F_BODY, 7); canvas.setFillColor(MUTED)
    canvas.drawString(M_LR, by - 12,
                      "Lighthouse Macro  |  LighthouseMacro.com  |  @LHMacro")
    canvas.drawCentredString(PAGE_W / 2, by - 12, f"Page {doc.page}")
    canvas.setFont(F_H, 7); canvas.setFillColor(OCEAN)
    canvas.drawRightString(PAGE_W - M_LR, by - 12, "MACRO, ILLUMINATED.")
    canvas.restoreState()


def inline(el) -> str:
    """Serialize an element's inline content to reportlab mini-markup."""
    out = []
    for n in el.children:
        if isinstance(n, NavigableString):
            out.append(str(n).replace("&", "&amp;")
                       .replace("<", "&lt;").replace(">", "&gt;"))
        elif isinstance(n, Tag):
            inner = inline(n)
            name = n.name.lower()
            if name in ("strong", "b"):
                out.append(f"<b>{inner}</b>")
            elif name in ("em", "i"):
                out.append(f"<i>{inner}</i>")
            elif name == "a":
                href = n.get("href", "")
                out.append(f'<link href="{href}" color="#2389BB">{inner}</link>')
            elif name == "br":
                out.append("<br/>")
            elif name in ("code", "kbd"):
                out.append(f'<font face="Courier">{inner}</font>')
            else:
                out.append(inner)
    return "".join(out).strip()


def image_block(fig: Tag, ext_caption: Tag = None):
    """Build a KeepTogether(image + caption + source) from a <figure>.

    Caption resolution order:
      1. internal <figcaption> (Two Economies, Term Premium)
      2. ext_caption — a following <p class="caption"> sibling (AI Beam)
    A nested .lhm-figsrc inside the caption is split out as the source line.
    """
    img = fig.find("img")
    if not img:
        return None
    src = img.get("src", "")
    if "base64," not in src:
        return None
    png = base64.b64decode(src.split("base64,", 1)[1])
    pil = PILImage.open(io.BytesIO(png))
    w, h = pil.size
    aspect = h / w
    disp_w = CONTENT_W
    disp_h = disp_w * aspect
    max_h = 4.9 * inch
    if disp_h > max_h:
        disp_h = max_h
        disp_w = disp_h / aspect
    im = Image(io.BytesIO(png), width=disp_w, height=disp_h)
    im.hAlign = "CENTER"
    block = [im]
    cap_node = fig.find("figcaption") or ext_caption
    if cap_node is not None:
        srcspan = cap_node.find(class_="lhm-figsrc") if hasattr(cap_node, "find") else None
        src_txt = srcspan.get_text(" ", strip=True) if srcspan else ""
        if srcspan:
            srcspan.extract()
        cap_txt = cap_node.get_text(" ", strip=True)
        if cap_txt:
            block.append(Paragraph(cap_txt, ST["cap"]))
        if src_txt:
            block.append(Paragraph(src_txt, ST["src"]))
    return KeepTogether(block)


SKIP = {"lhm-footer", "lhm-toc", "lhm-header-rule", "masthead", "branding"}
SKIP_TAGS = {"header", "footer", "nav", "script", "style"}


def el_to_flowables(el: Tag) -> list:
    cls = el.get("class") or []
    cls = set(cls) if isinstance(cls, list) else {cls}
    name = el.name.lower()

    if cls & SKIP or name in SKIP_TAGS:
        return []
    if name == "figure":
        b = image_block(el)
        return [b] if b else []
    if name == "hr":
        return [Spacer(1, 5), Rule(CONTENT_W, RULE, 0.5), Spacer(1, 7)]
    if "signoff" in cls:
        return [Paragraph(inline(el), ST["signoff"])]
    if "caption" in cls:
        # An orphan caption (not consumed by a preceding figure). Render
        # in caption style rather than as body text.
        txt = inline(el)
        return [Paragraph(txt, ST["cap"])] if txt else []
    if name in ("h1",) or "lhm-title" in cls:
        return [Paragraph(inline(el), ST["title"])]
    if "lhm-kicker" in cls:
        return [Paragraph(inline(el), ST["kicker"])]
    if "lhm-deck" in cls:
        return [Paragraph(inline(el), ST["deck"]),
                Spacer(1, 3), Rule(CONTENT_W), Spacer(1, 4)]
    if "lhm-byline" in cls:
        return [Paragraph(inline(el), ST["byline"])]
    if name == "h2":
        return [Paragraph(inline(el), ST["h2"])]
    if name in ("h3", "h4"):
        return [Paragraph(inline(el), ST["h3"])]
    if "lhm-signoff" in cls:
        return [Paragraph(inline(el), ST["signoff"])]
    if "lhm-accent" in cls:
        return [Spacer(1, 6), AccentBar(CONTENT_W, 5), Spacer(1, 6)]
    if cls & {"lhm-arithmetic", "lhm-formula", "lhm-mathfun"}:
        return [Paragraph(inline(el), ST["mono"])]
    if cls & {"lhm-exec", "lhm-breach-board"}:
        inner = []
        for ch in el.children:
            if isinstance(ch, Tag):
                for f in el_to_flowables(ch):
                    inner.append(f)
            elif isinstance(ch, NavigableString) and ch.strip():
                inner.append(Paragraph(str(ch).strip(), ST["exec"]))
        if not inner:
            inner = [Paragraph(inline(el), ST["exec"])]
        return [Spacer(1, 4), TintBox(inner, CONTENT_W), Spacer(1, 8)]
    if "lhm-cta" in cls:
        return [Spacer(1, 6), Rule(CONTENT_W, OCEAN, 1.0), Spacer(1, 5),
                Paragraph(inline(el), ST["cta"]),
                Spacer(1, 5), Rule(CONTENT_W, OCEAN, 1.0), Spacer(1, 6)]
    if name in ("ul", "ol"):
        out = []
        for li in el.find_all("li", recursive=False):
            out.append(Paragraph("•&nbsp;&nbsp;" + inline(li), ST["body"]))
        return out
    if name == "p":
        txt = inline(el)
        return [Paragraph(txt, ST["body"])] if txt else []
    # Fallback: recurse containers
    out = []
    for ch in el.children:
        if isinstance(ch, Tag):
            out += el_to_flowables(ch)
    if not out:
        t = inline(el)
        if t:
            out = [Paragraph(t, ST["body"])]
    return out


def _detect_root(soup):
    """Pick the densest content container (.lhm-beacon, article, main, or
    the densest div) so the walker covers the real body, not page chrome."""
    pref = soup.find(class_="lhm-beacon")
    if pref:
        return pref
    body = soup.body or soup

    def density(el):
        return len(el.find_all(["p", "figure", "h2"], recursive=True))

    cands = [body] + body.find_all(["article", "main", "div"], recursive=True)
    return max(cands, key=density)


def build(html_path: str, out_path: str, title: str = None,
          subtitle: str = None, label: str = None, date: str = None):
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    soup = BeautifulSoup(Path(html_path).read_text(errors="ignore"),
                         "html.parser")
    root = _detect_root(soup)

    # Title block: prefer explicit args, else detected h1 / first h2.
    if title is None:
        h1 = soup.find(["h1"]) or soup.find(class_="lhm-title")
        title = h1.get_text(" ", strip=True) if h1 else "Lighthouse Macro"
    RUN["label"] = label or "Lighthouse Macro"
    RUN["date"] = date or ""

    story = [Spacer(1, 0.05 * inch), AccentBar(CONTENT_W, 5),
             Spacer(1, 0.16 * inch), Paragraph(title, ST["title"])]
    if subtitle:
        story += [Paragraph(subtitle, ST["deck"])]
    sub_line = " · ".join(x for x in (RUN["label"], RUN["date"]) if x)
    story += [Rule(CONTENT_W), Spacer(1, 0.05 * inch),
              Paragraph("Lighthouse Macro, LLC  |  Bob Sheehan, CFA, CMT"
                        + (f"  |  {sub_line}" if sub_line else ""),
                        ST["byline"])]

    kids = [c for c in root.children if isinstance(c, Tag)]
    fig_count = 0
    skip_next = False
    seen_title = False
    for i, el in enumerate(kids):
        if skip_next:
            skip_next = False
            continue
        ecls = set(el.get("class") or [])
        ename = el.name.lower()
        # Drop the doc's own title/deck/byline/h1 — we built our own block.
        if not seen_title and (ename == "h1" or "lhm-title" in ecls
                               or "lhm-kicker" in ecls or "lhm-deck" in ecls
                               or "lhm-byline" in ecls):
            if ename in ("h2",):
                seen_title = True
            else:
                continue
        if ename in ("h2", "figure", "p") and not ("caption" in ecls):
            seen_title = True
        # figure with caption as a FOLLOWING sibling (AI Beam pattern)
        if ename == "figure" and not el.find("figcaption"):
            nxt = kids[i + 1] if i + 1 < len(kids) else None
            if (nxt is not None and nxt.name == "p"
                    and "caption" in set(nxt.get("class") or [])):
                b = image_block(el, ext_caption=nxt)
                if b:
                    story.append(b)
                    fig_count += 1
                skip_next = True
                continue
        flows = el_to_flowables(el)
        for f in flows:
            if isinstance(f, KeepTogether):
                fig_count += 1
        story += flows

    # Keep the final closing section intact. The last h2 (e.g. the closing
    # section) plus its paragraphs, signoff, and byline must not orphan a
    # trailing clause onto a near-empty last page. Wrap from the last h2
    # through the end of the story in a single KeepTogether so reportlab
    # moves the whole block to a fresh page rather than splitting it.
    last_h2 = None
    for idx, f in enumerate(story):
        if (isinstance(f, Paragraph)
                and getattr(f, "style", None) is not None
                and f.style.name == "h2"):
            last_h2 = idx
    if last_h2 is not None and last_h2 < len(story):
        story[last_h2:] = [KeepTogether(story[last_h2:])]

    doc = SimpleDocTemplate(
        str(out), pagesize=letter,
        leftMargin=M_LR, rightMargin=M_LR,
        topMargin=M_TOP, bottomMargin=M_BOT,
        title=title, author="Bob Sheehan, CFA, CMT",
        subject="Lighthouse Macro Research", creator="Lighthouse Macro",
    )
    doc.build(story, onFirstPage=_page, onLaterPages=_page)
    print(f"figure blocks: {fig_count}  pages-built  -> {out}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("html")
    ap.add_argument("out")
    ap.add_argument("--title", default=None)
    ap.add_argument("--subtitle", default=None)
    ap.add_argument("--label", default=None)
    ap.add_argument("--date", default=None)
    a = ap.parse_args()
    build(a.html, a.out, a.title, a.subtitle, a.label, a.date)
