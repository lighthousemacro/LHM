#!/usr/bin/env python3
"""
build_reading_room.py — Lighthouse Macro Reading Room generator.

Renders the Substack export ON-SITE at lighthousemacro.com/research so readers
never bounce to Substack. Free posts publish full. Paid posts publish a teaser
plus a members CTA (full piece lives in Pharos). Also emits a branded RSS feed
(/feed.xml) so the Newstex syndication points at our domain, not Substack's.

Run:
    PYTHONPATH=/Users/bob/LHM python3 Scripts/website/build_reading_room.py
"""

import csv
import os
import re
import sys
import html as ihtml
from datetime import datetime, timezone
from email.utils import format_datetime
from urllib.parse import quote

from bs4 import BeautifulSoup

ROOT = "/Users/bob/LHM"
EXPORT = os.path.join(ROOT, "Pharos/content/substack_export")
POSTS_DIR = os.path.join(EXPORT, "posts")
POSTS_CSV = os.path.join(EXPORT, "posts.csv")
OUT_DIR = os.path.join(ROOT, "Website/research")
SITE = "https://lighthousemacro.com"
PHAROS = "https://pharos.lighthousemacro.com"
SUBSCRIBE = "https://research.lighthousemacro.com/subscribe"
YEAR = 2026

# --- image CDN ---------------------------------------------------------------
# Re-wrap the original S3 object through Substack's image CDN at a web-friendly
# width. Reader never touches the substack.com domain; this is just a fast image
# host. (Self-hosting is a later step; disk is tight today.)
CDN = "https://substackcdn.com/image/fetch/w_1456,c_limit,f_auto,q_auto:good,fl_progressive:steep/"


def cdn_url(s3_url: str) -> str:
    return CDN + quote(s3_url, safe="")


# --- section taxonomy --------------------------------------------------------
# Reading Room sections = Bob's all-B publication scheme (matches Substack
# modules). (key, name, short, kicker, blurb)
SECTIONS = [
    ("FRAMEWORK",    "The Blueprint",  "Blueprint",  "The Diagnostic Dozen", "Twelve pillars, three engines. The method itself."),
    ("FLAGSHIP",     "The Beacon",     "Beacon",     "Flagship analysis",    "Long-form. One thesis, taken all the way down."),
    ("LIVE",         "The Beam",       "Beam",       "The fast read",        "Fast reads on the print that just hit."),
    ("CROSSCURRENTS","The Book",       "Book",       "The live book",        "Positioning, in the open."),
    ("FOUNDATION",   "The Broadsheet", "Broadsheet", "The chartbook",        "The data, laid out to be looked at."),
    ("FORWARD",      "The Beyond",     "Beyond",     "The forward view",     "The month ahead, and where the risk sits."),
    ("FIELD_NOTES",  "The Bulletin",   "Bulletin",   "Dispatches",           "Early notes and announcements from the archive."),
]
SECTION_ORDER = [k for k, *_ in SECTIONS]

# Per-post tag shown on cards = the short section name.
PUB_TAG = {k: short for k, _n, short, _ki, _b in SECTIONS}

# Pieces removed from the Reading Room (firm announcements, not analysis).
EXCLUDE = {
    "twelve-hours",
    "welcome-to-lighthouse-macro",
    "building-the-intelligence-layer",
    "introducing-lighthouse-macro-crypto",
    "the-foundation-is-set-now-we-build",
}

# Curated order for The Blueprint (FRAMEWORK): the Two Economies primer first,
# then the twelve pillars 1->12, then the indicator-framework pieces, with the
# Liquidity Transmission Framework pinned LAST. Anything unlisted slots in by
# date between the ordered block and the pinned-last piece.
FRAMEWORK_ORDER = [
    "why-most-americans-dont-care-about",
    "labor-the-source-code",
    "prices-the-transmission-belt",
    "growth-the-second-derivative",
    "housing-the-collateral-engine",
    "consumer-the-last-domino",
    "business-the-forward-commitment",
    "trade-the-pipeline",
    "government-the-fiscal-overhang",
    "financial-the-cascade",
    "plumbing-the-invisible-infrastructure",
    "market-structure-the-weight-of-evidence",
    "sentiment-and-positioning-the-contrarian-216",
    "crypto-liquidity-impulse",
]
FRAMEWORK_LAST = "liquidity-transmission-framework"

# Fallback card image when a piece has no chart of its own: the branded card,
# never a blank panel. Every piece shows a chart or the logo.
LOGO_FALLBACK = "/og-image.png"

# Content-read classifications for the 27 posts whose section is not obvious
# from metadata (reading-room-classify workflow: 27 reader agents + reviewer,
# each read the actual article text). The other 35 are deterministic via
# det_section(). Early pre-brand deep-dives land in FLAGSHIP (the analytical
# line); firm announcements land in FIELD_NOTES.
AMBIGUOUS_SECTIONS = {
    "building-the-intelligence-layer": "FIELD_NOTES",
    "introducing-lighthouse-macro-crypto": "FIELD_NOTES",
    "the-foundation-is-set-now-we-build": "FIELD_NOTES",
    "welcome-to-lighthouse-macro": "FIELD_NOTES",
    "bullion-brilliance": "FLAGSHIP",
    "collateral-fragility": "FLAGSHIP",
    "cracks-beneath-the-surface": "FLAGSHIP",
    "cracks-in-the-foundation-the-us-treasury": "FLAGSHIP",
    "labor-woes-growth-slows": "FLAGSHIP",
    "navigating-trade-tensions": "FLAGSHIP",
    "new-year-new-paradigms": "FLAGSHIP",
    "seemingly-stable-systemically-stressed": "FLAGSHIP",
    "the-dollar-vs-gold-and-real-yields": "FLAGSHIP",
    "the-reflexive-bid": "FLAGSHIP",
    "the-us-housing-market-in-2025": "FLAGSHIP",
    "the-vanishing-job-hopper-premium": "FLAGSHIP",
    "the-widest-page-in-the-book": "FLAGSHIP",
    "two-economies": "FLAGSHIP",
    "the-splitting-cycle": "FORWARD",
    "crypto-liquidity-impulse": "FRAMEWORK",
    "liquidity-transmission-framework": "FRAMEWORK",
    "why-most-americans-dont-care-about": "FRAMEWORK",
    "chaos-in-china": "LIVE",
    "monetary-monday": "LIVE",
    "stocks-printed-a-record-bonds-and": "LIVE",
    "the-silent-capitulation-etf-exodus": "LIVE",
    "two-prints-in-one-release": "LIVE",
}


def det_section(subtitle: str, title: str):
    """Deterministic section from the series brand in the metadata, else None."""
    s = ((subtitle or "") + " " + (title or "")).lower()
    sub = (subtitle or "").lower()
    if "diagnostic dozen" in sub:
        return "FRAMEWORK"
    if "chartbook" in s:
        return "FOUNDATION"
    if "horizon" in s:
        return "FORWARD"
    if "the beacon" in s:
        return "FLAGSHIP"
    if "the beam" in s:
        return "LIVE"
    if "positioning update" in (title or "").lower() or "positioning framework" in sub:
        return "CROSSCURRENTS"
    return None


def section_for(slug: str, subtitle: str, title: str) -> str:
    return det_section(subtitle, title) or AMBIGUOUS_SECTIONS.get(slug) or "FIELD_NOTES"


# --- html cleaning -----------------------------------------------------------
KILL_SELECTORS = [
    'p.button-wrapper',
    '[data-component-name="ButtonCreateButton"]',
    '[data-component-name="SubscribeWidget"]',
    '[data-component-name="SubscribeWidgetToDOM"]',
    '.subscribe-widget',
    '.subscribe-widget-content',
    '.digest-post-embed',
    '.embedded-post',
    '.footer',
]


def clean_body(raw: str):
    """Return (dek_html, body_soup) cleaned of Substack chrome."""
    soup = BeautifulSoup(raw, "lxml")
    # lxml wraps fragments in <html><body>; operate on body contents
    body = soup.body or soup

    # remove interactive / promo chrome
    for sel in KILL_SELECTORS:
        for el in body.select(sel):
            el.decompose()
    for tag in body.find_all(["button", "svg", "form", "input"]):
        tag.decompose()
    # subscribe links / comment links
    for a in body.find_all("a"):
        href = (a.get("href") or "").lower()
        if "/subscribe" in href or "/comments" in href or "action=share" in href:
            a.decompose()

    # simplify figures -> <figure><img><figcaption>
    for fig in body.find_all("figure"):
        img = fig.find("img")
        cap = fig.find("figcaption")
        new = soup.new_tag("figure")
        if img is not None:
            src = img.get("src", "")
            m = re.search(r"(https://substack-post-media\.s3\.amazonaws\.com/[^\s\"']+)", src)
            clean_src = cdn_url(m.group(1)) if m else src
            ni = soup.new_tag("img", src=clean_src, loading="lazy")
            if img.get("alt"):
                ni["alt"] = img["alt"]
            new.append(ni)
        if cap is not None:
            nc = soup.new_tag("figcaption")
            nc.string = cap.get_text(" ", strip=True)
            if nc.string:
                new.append(nc)
        fig.replace_with(new)

    # standalone <img> not already inside a figure
    for img in body.find_all("img"):
        if img.find_parent("figure"):
            continue
        src = img.get("src", "")
        m = re.search(r"(https://substack-post-media\.s3\.amazonaws\.com/[^\s\"']+)", src)
        if m:
            img["src"] = cdn_url(m.group(1))
        img["loading"] = "lazy"
        for attr in list(img.attrs):
            if attr not in ("src", "alt", "loading"):
                del img[attr]

    # strip data-* / class noise from structural tags
    for tag in body.find_all(True):
        for attr in list(tag.attrs):
            if attr.startswith("data-") or attr in ("class", "style", "id", "target", "rel"):
                del tag[attr]

    # pull dek: leading blockquote of italic text
    dek = ""
    first = None
    for child in body.find_all(recursive=False):
        if child.name in ("p", "blockquote", "h1", "h2", "figure", "div"):
            first = child
            break
    if first is not None and first.name == "blockquote":
        dek = first.get_text(" ", strip=True)
        first.decompose()

    # collapse empty paragraphs
    for p in body.find_all("p"):
        if not p.get_text(strip=True) and not p.find("img"):
            p.decompose()

    inner = "".join(str(c) for c in body.contents).strip()
    return dek, inner


_CROSSLINK = re.compile(r'https?://research\.lighthousemacro\.com/p/([a-z0-9-]+)(?:[?#][^"\']*)?')


def rewrite_crosslinks(body_html: str, known: set, base: str = "") -> str:
    """Repoint in-body Substack cross-links to on-site Reading Room pages.
    base="" yields relative <slug>.html (article pages); pass an absolute
    base for the feed. Unknown targets fall back to the Reading Room index."""
    def repl(m):
        slug = m.group(1)
        target = f"{slug}.html" if slug in known else "index.html"
        return base + target
    return _CROSSLINK.sub(repl, body_html)


def first_image(body_html: str):
    m = re.search(r'<img[^>]+src="([^"]+)"', body_html)
    return m.group(1) if m else ""


def make_teaser(body_html: str, max_chars=900):
    """Opening of a paid piece: intro paragraphs (up to ~max_chars) plus the
    first chart as a hook, then stop. One visual, never the whole deck."""
    soup = BeautifulSoup(body_html, "lxml")
    root = soup.body or soup
    out, acc = [], 0
    for el in root.find_all(recursive=False)[:9]:
        if el.name == "p":
            txt = el.get_text(" ", strip=True)
            if not txt:
                continue
            out.append(str(el))
            acc += len(txt)
        elif el.name == "figure" and "<figure" not in "".join(out):
            out.append(str(el))
        elif el.name in ("h2", "h3"):
            if out and acc >= 250:
                break
        if acc >= max_chars and "<figure" in "".join(out):
            break
    teaser = "".join(out)
    # ensure one chart shows as the hook even when figures are nested in divs
    if "<figure" not in teaser:
        fig = soup.find("figure")
        if fig is not None:
            teaser += str(fig)
    return teaser


def plain_excerpt(body_html: str, n=300):
    txt = BeautifulSoup(body_html, "lxml").get_text(" ", strip=True)
    txt = re.sub(r"\s+", " ", txt)
    return (txt[:n].rsplit(" ", 1)[0] + "...") if len(txt) > n else txt


# --- page chrome -------------------------------------------------------------
def nav_html(prefix=""):
    return f'''<div class="accent-bar"></div>
<nav>
  <div class="nav-inner">
    <a href="{prefix}../index.html" class="nav-logo">LIGHTHOUSE <span>MACRO</span></a>
    <button class="nav-toggle" aria-label="Toggle navigation" aria-expanded="false" onclick="this.setAttribute('aria-expanded', document.querySelector('.nav-links').classList.toggle('open'))"><span></span><span></span><span></span></button>
    <ul class="nav-links">
      <li><a href="{prefix}../framework.html">The Diagnostic Dozen</a></li>
      <li><a href="{prefix}../methodology.html">Methodology</a></li>
      <li><a href="{prefix}../index.html#dashboard">Live Read</a></li>
      <li><a href="{prefix}../index.html#services">Services</a></li>
      <li><a href="{prefix}../index.html#about">About</a></li>
      <li><a href="{prefix}../index.html#contact">Contact</a></li>
      <li><a href="{prefix}../index.html#subscribe">Subscribe</a></li>
      <li><a href="{prefix}index.html" class="nav-cta alt">Reading Room</a></li>
      <li><a href="{prefix}../pharos/" class="nav-cta">Pharos</a></li>
    </ul>
  </div>
</nav>'''


def footer_html(prefix=""):
    return f'''<footer>
  <div class="wrap">
    <div class="foot-grid">
      <div>
        <div class="foot-brand">LIGHTHOUSE<span class="dot">.</span></div>
        <div class="foot-tag">MACRO, ILLUMINATED.</div>
        <p>Independent macro research and advisory built on the Diagnostic Dozen framework. Read by CIOs, central bankers, and the practitioners who watch the tape.</p>
      </div>
      <div class="foot-col">
        <h5>// Sections</h5>
        <a href="{prefix}../framework.html">Framework</a>
        <a href="{prefix}../methodology.html">Methodology</a>
        <a href="{prefix}../index.html#dashboard">Live Read</a>
        <a href="{prefix}index.html">Reading Room</a>
        <a href="{prefix}../pharos/">Pharos</a>
        <a href="{prefix}../index.html#about">About</a>
        <a href="{prefix}../index.html#contact">Contact</a>
      </div>
      <div class="foot-col">
        <h5>// Elsewhere</h5>
        <a href="{SITE}/feed.xml">RSS Feed &rarr;</a>
        <a href="https://x.com/LHMacro" target="_blank" rel="noopener">@LHMacro</a>
        <a href="mailto:advisory@lighthousemacro.com">advisory@lighthousemacro.com</a>
        <a href="mailto:bob@lighthousemacro.com">bob@lighthousemacro.com</a>
      </div>
    </div>
    <div class="foot-sig">
      <div class="lhm-sig"><a href="{SITE}">Lighthouse Macro</a> | <a href="{SITE}/research/">Research</a> | <a href="https://x.com/LHMacro">@LHMacro</a></div>
      <div class="mono" style="color:var(--doldrums);">&copy; {YEAR} Lighthouse Macro, LLC</div>
    </div>
    <div class="foot-disclaimer">
      Lighthouse Macro, LLC provides research and advisory services that are informational and educational in nature. Nothing published or communicated by Lighthouse Macro constitutes personalized investment advice, a solicitation, or a recommendation to buy, sell, or hold any security. All investment decisions are the sole responsibility of the reader or client. Past performance is not indicative of future results. Lighthouse Macro, LLC is not a registered investment advisor.
    </div>
  </div>
</footer>
<div class="foot-bar"></div>'''


NAV_SCRIPT = '''<script>
document.querySelectorAll('.nav-links a').forEach(function(a){a.addEventListener('click',function(){document.querySelector('.nav-links').classList.remove('open');});});
</script>'''


def article_page(meta, dek, content_html, is_paid):
    slug = meta["slug"]
    title = ihtml.escape(meta["title"])
    series = meta["series"]
    datestr = meta["datestr"]
    paywall = ""
    body = content_html
    robots = ""
    if is_paid:
        body = ""  # paid pieces are fully blocked on the public site, no teaser, no chart
        robots = '\n<meta name="robots" content="noindex">'
        paywall = f'''
    <div class="paywall">
      <div class="pw-mono">// Members Research</div>
      <h3>This piece is for members.</h3>
      <p>Members research lives inside Pharos, in full, alongside the live dashboards and the terminal. It is not published on the open site.</p>
      <div class="pw-ctas">
        <a class="pw-go" href="{SUBSCRIBE}">Become a member</a>
        <a class="pw-ghost" href="{PHAROS}">Open Pharos &rarr;</a>
      </div>
    </div>'''
    badge = '<span class="badge paid">Members</span>' if is_paid else '<span class="badge free">Free</span>'
    dek_html = f'<p class="art-dek">{ihtml.escape(dek)}</p>' if dek else ""
    canonical = f"{SITE}/research/{slug}.html"
    desc = ihtml.escape(meta["excerpt"])
    og_img = meta["lead_img"] or f"{SITE}/og-image.png"
    import json as _json
    headline_json = _json.dumps(meta["title"])
    free_flag = "false" if is_paid else "true"
    ld = ('{"@context":"https://schema.org","@type":"Article","headline":'
          + headline_json + ',"datePublished":"' + meta["iso"]
          + '","author":{"@type":"Person","name":"Bob Sheehan","honorificSuffix":"CFA, CMT"},'
          + '"publisher":{"@type":"Organization","name":"Lighthouse Macro"},'
          + '"isAccessibleForFree":' + free_flag + ',"url":"' + canonical + '"}')
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} | Lighthouse Macro</title>
<meta name="description" content="{desc}">{robots}
<link rel="canonical" href="{canonical}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="{og_img}">
<meta property="og:url" content="{canonical}">
<meta property="og:type" content="article">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:site" content="@LHMacro">
<script type="application/ld+json">
{ld}
</script>
<link rel="icon" type="image/x-icon" href="../favicon.ico">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700;800&family=Inter:wght@300;400;500;600&family=Source+Code+Pro:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="reader.css">
<meta name="theme-color" content="#2389BB">
</head>
<body>
{nav_html()}
<article class="art">
  <div class="wrap art-wrap">
    <div class="art-meta"><a href="index.html" class="back">&larr; Reading Room</a><span class="mono">{series} &middot; {datestr}</span>{badge}</div>
    <h1 class="art-title">{title}</h1>
    {dek_html}
    <div class="art-body">
      {body}
      {paywall}
    </div>
    <div class="art-foot">
      <div class="mono">Lighthouse Macro &middot; Research</div>
      <a class="art-sub" href="{SUBSCRIBE}">Subscribe &rarr;</a>
    </div>
  </div>
</article>
{footer_html()}
{NAV_SCRIPT}
</body>
</html>'''


def _card(m):
    badge = '<span class="badge paid">Members</span>' if m["paid"] else '<span class="badge free">Free</span>'
    img = m["lead_img"] or LOGO_FALLBACK
    thumb = f'<div class="rc-thumb"><img src="{img}" loading="lazy" alt=""></div>'
    return f'''<a class="rcard" href="{m['slug']}.html">
  {thumb}
  <div class="rc-body">
    <div class="rc-meta"><span class="mono">{m['series']} &middot; {m['datestr']}</span>{badge}</div>
    <h3 class="rc-title">{ihtml.escape(m['title'])}</h3>
    <p class="rc-ex">{ihtml.escape(m['excerpt'])}</p>
    {'<span class="rc-lock">&#128274; Read in Pharos</span>' if m['paid'] else ''}
  </div>
</a>'''


def index_page(items):
    # group into the named sections, reverse-chron within each
    by_sec = {k: [] for k in SECTION_ORDER}
    for m in items:
        by_sec.get(m["section"], by_sec["FIELD_NOTES"]).append(m)

    # The Blueprint runs in a curated order (Two Economies -> pillars 1-12 ->
    # frameworks -> Liquidity Transmission last), not reverse-chron.
    fw_idx = {s: i for i, s in enumerate(FRAMEWORK_ORDER)}
    def _fw_key(m):
        s = m["slug"]
        if s == FRAMEWORK_LAST:
            return (2, 0.0)
        if s in fw_idx:
            return (0, float(fw_idx[s]))
        return (1, -m["dt"].timestamp())  # unlisted: newest first, before the pinned-last piece
    by_sec["FRAMEWORK"].sort(key=_fw_key)

    jump, blocks = [], []
    for key, name, short, kicker, blurb in SECTIONS:
        bucket = by_sec.get(key, [])
        if not bucket:
            continue
        anchor = key.lower().replace("_", "-")
        n = len(bucket)
        jump.append(f'<a href="#{anchor}"><span>{short}</span><em>{n}</em></a>')
        cards = "\n".join(_card(m) for m in bucket)
        blocks.append(f'''<section class="rr-sec" id="{anchor}">
  <div class="rr-sec-head">
    <div class="rr-sec-mark"></div>
    <div>
      <div class="rr-sec-kicker"><span class="rr-fname">{name}</span> <span class="rr-pub">{kicker}</span></div>
      <p class="rr-sec-blurb">{blurb}</p>
    </div>
    <div class="rr-sec-count mono">{n} {'piece' if n == 1 else 'pieces'}</div>
  </div>
  <div class="rgrid">
  {cards}
  </div>
</section>''')
    jump_nav = '<nav class="rr-jump">' + "".join(jump) + '</nav>'
    sections_html = "\n".join(blocks)
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Reading Room | Lighthouse Macro</title>
<meta name="description" content="The Lighthouse Macro Reading Room. Beacons, Beams, Horizons, and Chartbooks. Read the research on framework and process, in full, on lighthousemacro.com.">
<link rel="canonical" href="{SITE}/research/">
<meta property="og:title" content="Reading Room | Lighthouse Macro">
<meta property="og:description" content="Beacons, Beams, Horizons, and Chartbooks. The research, in full, on lighthousemacro.com.">
<meta property="og:image" content="{SITE}/og-image.png">
<meta property="og:url" content="{SITE}/research/">
<meta property="og:type" content="website">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:site" content="@LHMacro">
<link rel="alternate" type="application/rss+xml" title="Lighthouse Macro" href="{SITE}/feed.xml">
<link rel="icon" type="image/x-icon" href="../favicon.ico">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700;800&family=Inter:wght@300;400;500;600&family=Source+Code+Pro:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="reader.css">
<meta name="theme-color" content="#2389BB">
</head>
<body>
{nav_html()}
<header class="rr-hero">
  <div class="wrap">
    <div class="mono" style="color:var(--ocean);">// The Reading Room</div>
    <h1>The research, in full.<br><span class="blue">On our terms</span><span class="dot">.</span></h1>
    <p>Organized the way we publish it. The Blueprint, the Beacon, the Beam, the Book, the Broadsheet, and the Beyond. Free pieces read in full here. Members research opens in full inside <a href="{PHAROS}">Pharos</a>, alongside the live dashboards and the terminal.</p>
    <div class="rr-actions"><a class="rr-rss" href="{SITE}/feed.xml">RSS Feed</a><a class="rr-join" href="{SUBSCRIBE}">Become a member &rarr;</a></div>
    {jump_nav}
  </div>
</header>
<main class="wrap rr-main">
  {sections_html}
</main>
{footer_html()}
{NAV_SCRIPT}
</body>
</html>'''


def reader_css():
    return '''/* Lighthouse Macro — Reading Room */
:root{--ocean:#2389BB;--dusk:#FF6723;--sky:#89CCFF;--sea:#00BB89;--venus:#FF2389;--doldrums:#898989;--fog:#D1D1D1;--deep:#123456;--ink:#123456;--paper:#FFFFFF;--ice:#D4E2EF;--glacier:#F4F7F9;--line:#E3E8EC;--body:#36424C;}
*{margin:0;padding:0;box-sizing:border-box;}
html{scroll-behavior:smooth;}
body{font-family:'Inter',-apple-system,BlinkMacSystemFont,sans-serif;color:var(--body);background:var(--glacier);line-height:1.6;-webkit-font-smoothing:antialiased;}
a{color:inherit;}
.wrap{max-width:1120px;margin:0 auto;padding:0 2rem;}
.mono{font-family:'Source Code Pro',monospace;letter-spacing:0.12em;text-transform:uppercase;font-size:0.72rem;color:#6b7280;}
.accent-bar{height:5px;background:linear-gradient(90deg,var(--ocean) 66%,var(--dusk) 66%);}
nav{background:rgba(255,255,255,0.92);backdrop-filter:blur(8px);border-bottom:1px solid var(--line);position:sticky;top:0;z-index:100;}
.nav-inner{max-width:1120px;margin:0 auto;padding:0 2rem;display:flex;align-items:center;justify-content:space-between;height:62px;}
.nav-logo{font-family:'Montserrat',sans-serif;font-weight:800;font-size:1.05rem;color:var(--ink);text-decoration:none;letter-spacing:0.3px;}
.nav-logo span{color:var(--ocean);}
.nav-links{display:flex;gap:1.25rem;list-style:none;align-items:center;}
.nav-links a{font-size:0.82rem;font-weight:500;color:var(--body);text-decoration:none;transition:color .2s;}
.nav-links a:hover{color:var(--ocean);}
.nav-cta{display:inline-block;white-space:nowrap;background:var(--ocean);color:#fff !important;padding:0.45rem 1.1rem;border-radius:4px;font-weight:600 !important;}
.nav-cta:hover{filter:brightness(0.85);}
.nav-cta.alt{background:transparent;color:var(--ocean) !important;border:1px solid var(--ocean);padding:calc(0.45rem - 1px) calc(1.1rem - 1px);}
.nav-cta.alt:hover{background:var(--ocean);color:#fff !important;filter:none;}
.nav-toggle{display:none;background:none;border:none;cursor:pointer;padding:0.4rem;}
.nav-toggle span{display:block;width:24px;height:2px;background:var(--ink);margin:5px 0;transition:.3s;}

/* badges */
.badge{font-family:'Source Code Pro',monospace;font-size:0.62rem;letter-spacing:0.1em;text-transform:uppercase;padding:0.18rem 0.5rem;border-radius:3px;font-weight:600;}
.badge.free{background:rgba(0,187,137,0.12);color:#0a7d5c;}
.badge.paid{background:rgba(35,137,187,0.12);color:var(--ocean);}

/* reading room hero */
.rr-hero{padding:4rem 0 2.6rem;background:radial-gradient(1100px 380px at 80% -10%,rgba(35,137,187,0.08),transparent 60%),var(--glacier);border-bottom:1px solid var(--line);}
.rr-hero h1{font-family:'Montserrat',sans-serif;font-weight:800;font-size:clamp(2.4rem,6vw,4rem);line-height:1.02;letter-spacing:-0.02em;color:var(--ink);margin:1rem 0 1.2rem;}
.rr-hero .blue{color:var(--ocean);}.rr-hero .dot{color:var(--dusk);}
.rr-hero p{font-size:1.08rem;max-width:680px;}
.rr-hero p a{color:var(--ocean);font-weight:600;text-decoration:none;}
.rr-actions{display:flex;gap:0.9rem;margin-top:1.8rem;flex-wrap:wrap;}
.rr-rss{border:1px solid var(--line);color:var(--ink);text-decoration:none;padding:0.7rem 1.3rem;border-radius:5px;font-weight:600;font-size:0.9rem;}
.rr-rss:hover{border-color:var(--ocean);color:var(--ocean);}
.rr-join{background:var(--dusk);color:#fff;text-decoration:none;padding:0.7rem 1.4rem;border-radius:5px;font-weight:600;font-size:0.9rem;}
.rr-join:hover{filter:brightness(0.92);}

/* section jump-nav */
.rr-jump{display:flex;flex-wrap:wrap;gap:0.6rem;margin-top:2rem;}
.rr-jump a{display:inline-flex;align-items:center;gap:0.5rem;border:1px solid var(--line);border-radius:999px;padding:0.4rem 0.5rem 0.4rem 0.9rem;text-decoration:none;font-size:0.82rem;font-weight:600;color:var(--ink);background:var(--paper);transition:border-color .2s,color .2s;}
.rr-jump a:hover{border-color:var(--ocean);color:var(--ocean);}
.rr-jump a em{font-style:normal;font-family:'Source Code Pro',monospace;font-size:0.7rem;background:var(--glacier);color:var(--doldrums);border-radius:999px;padding:0.1rem 0.5rem;}

/* section blocks (subtle paper / mist alternation for differentiation) */
.rr-main{padding:2.4rem 2rem 4rem;}
.rr-sec{padding:2.6rem 0;border-top:1px solid var(--line);}
.rr-sec:first-child{border-top:none;}
.rr-sec-head{display:flex;align-items:flex-start;gap:1rem;margin-bottom:1.8rem;}
.rr-sec-mark{flex:none;width:5px;align-self:stretch;border-radius:3px;background:linear-gradient(180deg,var(--ocean) 60%,var(--dusk) 60%);min-height:46px;}
.rr-sec-kicker{display:flex;align-items:baseline;gap:0.7rem;flex-wrap:wrap;}
.rr-fname{font-family:'Montserrat',sans-serif;font-weight:800;font-size:1.5rem;letter-spacing:-0.01em;color:var(--ink);}
.rr-pub{font-family:'Source Code Pro',monospace;font-size:0.74rem;letter-spacing:0.1em;text-transform:uppercase;color:var(--ocean);}
.rr-sec-blurb{font-size:0.95rem;color:#5b6770;margin-top:0.25rem;}
.rr-sec-count{margin-left:auto;color:var(--doldrums);white-space:nowrap;padding-top:0.3rem;}

/* card grid */
.rgrid{display:grid;grid-template-columns:repeat(3,1fr);gap:1.6rem;}
.rcard{display:flex;flex-direction:column;text-decoration:none;border:1px solid var(--line);border-radius:8px;overflow:hidden;background:var(--paper);transition:transform .2s,box-shadow .2s,border-color .2s;}
.rcard:hover{transform:translateY(-3px);box-shadow:0 14px 34px rgba(15,34,51,0.10);border-color:var(--ocean);}
.rc-thumb{aspect-ratio:16/9;overflow:hidden;background:var(--glacier);}
.rc-thumb img{width:100%;height:100%;object-fit:cover;display:block;}
.rc-noimg{background:linear-gradient(135deg,var(--deep),var(--ocean));}
.rc-body{padding:1.2rem 1.3rem 1.5rem;display:flex;flex-direction:column;gap:0.6rem;flex:1;}
.rc-meta{display:flex;align-items:center;justify-content:space-between;gap:0.6rem;}
.rc-title{font-family:'Montserrat',sans-serif;font-weight:700;font-size:1.12rem;line-height:1.2;color:var(--ink);}
.rc-ex{font-size:0.9rem;color:#5b6770;line-height:1.55;}
.rc-lock{display:inline-block;margin-top:0.6rem;font-family:'Source Code Pro',monospace;font-size:0.66rem;letter-spacing:0.08em;text-transform:uppercase;color:var(--dusk);font-weight:600;}

/* article */
.art{padding:3rem 0 2rem;}
.art-wrap{max-width:760px;}
.art-meta{display:flex;align-items:center;gap:1rem;flex-wrap:wrap;margin-bottom:1.4rem;}
.art-meta .back{color:var(--ocean);text-decoration:none;font-weight:600;font-size:0.85rem;margin-right:auto;}
.art-title{font-family:'Montserrat',sans-serif;font-weight:800;font-size:clamp(2rem,5vw,3rem);line-height:1.06;letter-spacing:-0.02em;color:var(--ink);margin-bottom:1.2rem;}
.art-dek{font-size:1.2rem;line-height:1.5;color:var(--ink);font-style:italic;border-left:3px solid var(--dusk);padding-left:1.2rem;margin-bottom:2rem;}
.art-body{font-size:1.08rem;line-height:1.75;color:#2b3640;}
.art-body p{margin:0 0 1.4rem;}
.art-body h2{font-family:'Montserrat',sans-serif;font-weight:700;font-size:1.6rem;color:var(--ink);margin:2.4rem 0 1rem;letter-spacing:-0.01em;}
.art-body h3{font-family:'Montserrat',sans-serif;font-weight:700;font-size:1.25rem;color:var(--ink);margin:2rem 0 0.8rem;}
.art-body strong{color:var(--ink);}
.art-body em{color:#2b3640;}
.art-body a{color:var(--ocean);text-decoration:underline;text-underline-offset:2px;}
.art-body ul,.art-body ol{margin:0 0 1.4rem 1.3rem;}
.art-body li{margin-bottom:0.5rem;}
.art-body blockquote{border-left:3px solid var(--ocean);padding-left:1.2rem;margin:0 0 1.4rem;color:#46525c;font-style:italic;}
.art-body figure{margin:2rem 0;}
.art-body img{width:100%;height:auto;border-radius:6px;border:1px solid var(--line);display:block;}
.art-body figcaption{font-family:'Source Code Pro',monospace;font-size:0.74rem;color:var(--doldrums);margin-top:0.6rem;text-align:center;}
.art-foot{display:flex;align-items:center;justify-content:space-between;gap:1rem;margin-top:2.6rem;padding-top:1.6rem;border-top:1px solid var(--line);}
.art-foot .art-sub{color:var(--ocean);font-weight:600;text-decoration:none;}

/* paywall */
.paywall{margin-top:1rem;border:1px solid var(--line);border-radius:10px;padding:2.2rem;background:var(--ice);text-align:center;position:relative;}
.paywall::before{content:"";position:absolute;top:-90px;left:0;right:0;height:90px;background:linear-gradient(to bottom,rgba(255,255,255,0),var(--glacier));pointer-events:none;}
.pw-mono{font-family:'Source Code Pro',monospace;font-size:0.68rem;letter-spacing:0.12em;text-transform:uppercase;color:var(--ocean);margin-bottom:0.6rem;}
.paywall h3{font-family:'Montserrat',sans-serif;font-weight:700;font-size:1.4rem;color:var(--ink);margin-bottom:0.8rem;}
.paywall p{font-size:0.98rem;color:#5b6770;max-width:520px;margin:0 auto 1.6rem;}
.pw-ctas{display:flex;gap:0.9rem;justify-content:center;flex-wrap:wrap;}
.pw-go{background:var(--ocean);color:#fff;text-decoration:none;padding:0.85rem 1.8rem;border-radius:5px;font-weight:600;}
.pw-go:hover{filter:brightness(0.88);}
.pw-ghost{border:1px solid var(--line);color:var(--ink);text-decoration:none;padding:0.85rem 1.6rem;border-radius:5px;font-weight:600;background:#fff;}
.pw-ghost:hover{border-color:var(--ocean);color:var(--ocean);}

/* footer */
footer{background:var(--deep);color:#9fb3c4;padding:3.4rem 0 0;margin-top:2rem;}
.foot-grid{display:grid;grid-template-columns:1.4fr 1fr 1fr;gap:2rem;}
.foot-brand{font-family:'Montserrat',sans-serif;font-weight:800;font-size:1.3rem;color:#fff;}
.foot-brand .dot{color:var(--dusk);}
.foot-tag{font-family:'Source Code Pro',monospace;font-size:0.7rem;letter-spacing:0.14em;color:var(--sky);margin:0.4rem 0 1rem;}
.foot-grid p{font-size:0.85rem;}
.foot-col h5{font-family:'Source Code Pro',monospace;font-size:0.68rem;letter-spacing:0.1em;color:var(--doldrums);margin-bottom:0.9rem;}
.foot-col a{display:block;color:#c7d4de;text-decoration:none;font-size:0.88rem;padding:0.25rem 0;}
.foot-col a:hover{color:#fff;}
.foot-sig{margin-top:2.4rem;padding:1.4rem 0;border-top:1px solid rgba(255,255,255,0.1);display:flex;justify-content:space-between;flex-wrap:wrap;gap:1rem;align-items:center;}
.foot-sig .lhm-sig a{color:var(--ocean);text-decoration:none;font-weight:600;font-size:0.85rem;}
.foot-sig .lhm-sig{font-size:0.85rem;color:var(--doldrums);}
.foot-disclaimer{font-size:0.7rem;color:#6b7d8c;line-height:1.6;padding-bottom:2rem;}
.foot-bar{height:5px;background:linear-gradient(90deg,var(--ocean) 66%,var(--dusk) 66%);}

@media (max-width:1000px){
  .rgrid{grid-template-columns:1fr 1fr;}
  .foot-grid{grid-template-columns:1fr;}
  .nav-links{display:none;position:absolute;top:62px;left:0;right:0;background:#fff;flex-direction:column;padding:1rem 2rem;border-bottom:1px solid var(--line);gap:0.9rem;}
  .nav-links.open{display:flex;}
  .nav-toggle{display:block;}
}
@media (max-width:560px){.rgrid{grid-template-columns:1fr;}}
'''


# --- feed --------------------------------------------------------------------
def build_feed(items):
    now = datetime.now(timezone.utc)
    entries = []
    for m in items:
        link = f"{SITE}/research/{m['slug']}.html"
        if m["paid"]:
            body = f'<p>{xesc(m["excerpt"])}</p><p><strong>Members research.</strong> Read it in full inside <a href="{PHAROS}">Pharos</a>, or <a href="{SUBSCRIBE}">become a member</a>.</p>'
        else:
            body = m["feed_full"]
        content = f"<![CDATA[{body}]]>"
        entries.append(f'''  <item>
    <title>{xesc(m['title'])}</title>
    <link>{link}</link>
    <guid isPermaLink="true">{link}</guid>
    <pubDate>{m['rfc822']}</pubDate>
    <dc:creator>Bob Sheehan</dc:creator>
    <category>{m['series']}</category>
    <description>{xesc(m['excerpt'])}</description>
    <content:encoded>{content}</content:encoded>
  </item>''')
    items_xml = "\n".join(entries)
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:content="http://purl.org/rss/1.0/modules/content/" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
  <title>Lighthouse Macro</title>
  <link>{SITE}/research/</link>
  <atom:link href="{SITE}/feed.xml" rel="self" type="application/rss+xml"/>
  <description>Institutional-grade macro and economic intelligence, built on framework and process. Macro, Illuminated.</description>
  <language>en-us</language>
  <copyright>Copyright {YEAR} Lighthouse Macro, LLC</copyright>
  <managingEditor>bob@lighthousemacro.com (Bob Sheehan)</managingEditor>
  <webMaster>bob@lighthousemacro.com (Bob Sheehan)</webMaster>
  <lastBuildDate>{format_datetime(now)}</lastBuildDate>
  <image><url>{SITE}/og-image.png</url><title>Lighthouse Macro</title><link>{SITE}/research/</link></image>
{items_xml}
</channel>
</rss>'''


def xesc(s):
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_sitemap(items):
    urls = [
        ("/", "daily", "1.0", None),
        ("/research/", "daily", "0.9", None),
        ("/pharos/", "monthly", "0.8", None),
        ("/framework.html", "monthly", "0.8", None),
        ("/methodology.html", "monthly", "0.6", None),
    ]
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for loc, cf, pr, _ in urls:
        out.append(f"  <url><loc>{SITE}{loc}</loc><changefreq>{cf}</changefreq><priority>{pr}</priority></url>")
    for m in items:
        if m["paid"]:
            continue  # paid stubs are noindex, keep them out of the sitemap
        lastmod = m["dt"].strftime("%Y-%m-%d")
        out.append(f'  <url><loc>{SITE}/research/{m["slug"]}.html</loc><lastmod>{lastmod}</lastmod><changefreq>monthly</changefreq><priority>0.7</priority></url>')
    out.append("</urlset>")
    return "\n".join(out)


# --- main --------------------------------------------------------------------
def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(POSTS_CSV) as f:
        rows = [r for r in csv.DictReader(f) if r["is_published"] == "true"]

    items = []
    seen_slugs = {}
    for r in rows:
        pid = r["post_id"]
        fn = os.path.join(POSTS_DIR, pid + ".html")
        if not os.path.exists(fn):
            continue
        title = (r["title"] or "Untitled").strip()
        subtitle = (r["subtitle"] or "").strip()
        paid = r["audience"] == "only_paid"
        iso = r["post_date"]
        try:
            dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        except Exception:
            dt = datetime.now(timezone.utc)
        slug = pid.split(".", 1)[1] if "." in pid else pid
        if slug in EXCLUDE:
            continue
        if slug in seen_slugs:
            slug = f"{slug}-{pid.split('.',1)[0]}"
        seen_slugs[slug] = True

        raw = open(fn, encoding="utf-8").read()
        dek, content = clean_body(raw)
        lead = first_image(content)
        if paid:
            # paid is fully blocked on-site: never derive public text from the body
            excerpt = dek[:300] if dek else "Members research. Read it in full inside Pharos."
            lead = None  # do not surface a paid lead chart on the public index
        else:
            excerpt = dek[:300] if dek else plain_excerpt(content)
        section = section_for(slug, subtitle, title)
        items.append({
            "slug": slug, "title": title,
            "section": section, "series": PUB_TAG[section],
            "paid": paid, "dt": dt, "iso": iso,
            "datestr": dt.strftime("%B %-d, %Y"),
            "rfc822": format_datetime(dt),
            "lead_img": lead, "excerpt": excerpt, "dek": dek,
            "full_html": content,
        })

    items.sort(key=lambda m: m["dt"], reverse=True)

    # repoint in-body cross-links to on-site pages (keep readers off substack)
    known = set(seen_slugs.keys())
    feedbase = f"{SITE}/research/"
    for m in items:
        # feed versions need absolute links; derive before relative rewrite.
        # paid bodies are never exposed (feed paid item = dek + members CTA only).
        if not m["paid"]:
            m["feed_full"] = rewrite_crosslinks(m["full_html"], known, base=feedbase)
            m["full_html"] = rewrite_crosslinks(m["full_html"], known)
        else:
            m["feed_full"] = ""
            m["full_html"] = ""

    # write reader.css
    with open(os.path.join(OUT_DIR, "reader.css"), "w", encoding="utf-8") as f:
        f.write(reader_css())

    # article pages
    for m in items:
        page = article_page(m, m["dek"], m["full_html"], m["paid"])
        with open(os.path.join(OUT_DIR, m["slug"] + ".html"), "w", encoding="utf-8") as f:
            f.write(page)

    # drop orphaned pages (anything excluded/removed since the last build)
    keep = {m["slug"] + ".html" for m in items} | {"index.html"}
    removed = 0
    for fn in os.listdir(OUT_DIR):
        if fn.endswith(".html") and fn not in keep:
            os.remove(os.path.join(OUT_DIR, fn))
            removed += 1
    if removed:
        print(f"  removed {removed} orphaned page(s)")

    # index
    with open(os.path.join(OUT_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(index_page(items))

    # feed
    with open(os.path.join(ROOT, "Website/feed.xml"), "w", encoding="utf-8") as f:
        f.write(build_feed(items))

    # sitemap (homepage + sections + every research page)
    with open(os.path.join(ROOT, "Website/sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(build_sitemap(items))

    free = sum(1 for m in items if not m["paid"])
    paid = sum(1 for m in items if m["paid"])
    print(f"Reading Room built: {len(items)} posts ({free} free, {paid} members)")
    print(f"  -> {OUT_DIR}/index.html + {len(items)} article pages + reader.css")
    print(f"  -> {ROOT}/Website/feed.xml")


if __name__ == "__main__":
    main()
