# LIGHTHOUSE MACRO — WEBSITE BUILDOUT PLAN

**Created:** 2026-03-14
**Status:** Planning
**Author:** Bob Sheehan + Claude

---

## THE VISION

Transform lighthousemacro.com from a 3-page brochure site into the one-stop hub for LHM research, frameworks, offerings, and (eventually) live data. Reduce dependency on Substack as the reading destination. Substack becomes the email delivery layer, not the home base.

**Guiding principle:** Bob's time should be spent thinking and analyzing, not managing platform friction. The site should make everything findable, browsable, and compelling without requiring readers to hop between Twitter, the website, Substack, and back.

**Inspiration model:** Michael Nadeau / The DeFi Report. The research is the product. The podcast amplifies. Consulting happens when organic and aligned, not as primary revenue.

---

## CURRENT STATE

### Existing Pages (GitHub Pages, hand-crafted HTML)
- `index.html` — Landing page (hero, framework overview, services/pricing, about, research cards, subscribe embed, contact, footer)
- `framework.html` — Diagnostic Dozen framework page (architecture diagram, MRI section, all 12 pillar cards by engine)
- `methodology.html` — Philosophy, process, principles
- `og-image.png` — Social sharing image
- `CNAME` — Custom domain (lighthousemacro.com)

### Brand Assets Available
- `Brand/icon_transparent_128.png` — Chart icon
- `Brand/Logo2389bb.png` — Primary logo
- `Brand/ReversLogo2389bb.png` — Reverse logo
- `Brand/Banner2389bb.png` — Banner lockup
- Full brand system documented in `Brand/brand-guide.md`, `Brand/chart-styling.md`, `Brand/templates.md`

### Content Available
- 12 Pillar Strategy docs in `Strategy/PILLAR [1-12] *.md` (internal reference, detailed)
- Pillar post template in `Strategy/PILLAR_TEMPLATE.md`
- 9 of 12 Diagnostic Dozen educational posts published on Substack (as of March 2026)
- 3 remaining: Market Structure, Sentiment, and one more TBD
- Various Beacon, Beam, and Chartbook content published on Substack

### Tech Stack
- GitHub Pages (static HTML/CSS/JS, no build tools)
- Custom domain via Network Solutions (expires Sep 9, 2026)
- Substack at research.lighthousemacro.com (custom domain)

---

## PHASE 1: PILLAR FRAMEWORK PAGES (DEFINITE — DOING THIS)

**Goal:** All 12 Diagnostic Dozen educational articles hosted as HTML pages on lighthousemacro.com, with optional PDF download for each.

### Content Strategy
- **Source material:** The published Substack versions (educational series), NOT the raw Strategy docs
- **Treatment:** "Timeless framework" versions — strip any "where we are now" current analysis so they don't go stale. The pillar pages explain: what this pillar is, why it matters, what indicators to watch, how to interpret them, the consensus trap, invalidation criteria
- **Current analysis** stays in paid research (Substack for now, eventually on-site)

### Technical Requirements

#### Shared Infrastructure (build first)
- [ ] Extract shared CSS into `styles.css` (currently every page duplicates ~700 lines of CSS)
- [ ] Create shared nav/footer as HTML includes or JS-injected components
- [ ] Establish consistent page template structure

#### Pillar Page Template
- [ ] Page header with pillar number, name, engine designation
- [ ] Accent bar + branding consistent with existing pages
- [ ] Full article content with proper typography (Montserrat headers, Inter body)
- [ ] Embedded charts (static images AND interactive HTML where applicable)
- [ ] "Download PDF" button for each pillar
- [ ] Navigation between pillars (prev/next + back to framework hub)
- [ ] Social sharing meta tags (og:image per pillar if possible)
- [ ] Mobile responsive

#### Framework Page Update
- [ ] Update `framework.html` pillar cards to link to individual pillar pages
- [ ] Add status indicators (published vs. coming soon) for the 3 remaining pillars

#### Nav Update
- [ ] Add "Pillars" or "Research" dropdown to site navigation
- [ ] Link to pillar index page or directly to framework.html as hub

#### PDF Generation
- [ ] Generate branded PDF for each pillar article
- [ ] Use LHM brand system (accent bar, watermarks, typography)
- [ ] Host PDFs in a `/pdfs/` or `/downloads/` directory

### File Structure (Proposed)
```
Website/
  index.html
  framework.html          (updated: pillar cards link to individual pages)
  methodology.html
  styles.css              (NEW: shared stylesheet)
  components/
    nav.js                (NEW: shared nav injection)
    footer.js             (NEW: shared footer injection)
  pillars/
    labor.html            (NEW)
    prices.html           (NEW)
    growth.html           (NEW)
    housing.html          (NEW)
    consumer.html         (NEW)
    business.html         (NEW)
    trade.html            (NEW)
    government.html       (NEW)
    financial.html        (NEW)
    plumbing.html         (NEW)
    market-structure.html (NEW)
    sentiment.html        (NEW)
  pdfs/
    pillar-01-labor.pdf   (NEW)
    pillar-02-prices.pdf  (NEW)
    ... etc
  assets/
    charts/               (NEW: chart images for pillar pages)
  og-image.png
  CNAME
```

### Workflow for Each Pillar
1. Pull final published version from Substack (verify it's the latest)
2. Strip "current state" / "where we are now" analysis (make timeless)
3. Convert to HTML using pillar page template
4. Embed charts as images (and interactive HTML where Substack couldn't)
5. Generate branded PDF version
6. Test on mobile
7. Deploy via git push

---

## PHASE 2: RESEARCH ARCHIVE (HIGHLY LIKELY)

**Goal:** Published research (Beacons, Beams, Chartbooks) lives on lighthousemacro.com. Substack becomes email delivery, not reading destination.

### Considerations
- Headless CMS vs. static markdown vs. hand-crafted HTML
- Bob mentioned seeing an API-based CMS — worth evaluating options
- Could use Jekyll (native GitHub Pages support) for blog-style content
- Need to decide: does paid content live here (with auth) or stay on Substack?
- RSS feed for research posts

### CMS Options to Evaluate
- **Jekyll** (GitHub Pages native, markdown-based, free)
- **Headless CMS** (Contentful, Strapi, Sanity — API-based, Bob mentioned seeing one)
- **Keep it manual** (hand-crafted HTML per post, simple but doesn't scale)

---

## PHASE 3: DASHBOARDS & INTERACTIVE CONTENT (PROBABLE)

**Goal:** Dashboard page with current pillar readings, interactive charts, and framework visualizations that Substack can't render.

### Possibilities
- MRI gauge / regime indicator
- Pillar heatmap (12-pillar status at a glance)
- Interactive charts powered by Chart.js, Plotly, or D3
- Could pull from a JSON data file updated by the data pipeline

### Note on Terminals
Bob is evaluating OpenBB, Fincept Terminal, and World Monitor as open source terminal options. The website dashboard is NOT a terminal replacement. It's a branded, public-facing visualization of LHM's framework outputs. Terminal tools are for Bob's personal analysis workflow.

---

## PHASE 4: PAID CONTENT ON-SITE (EVENTUAL)

**Goal:** Full independence from Substack. Paid content lives on lighthousemacro.com with Stripe-powered subscriptions.

### Requirements (future)
- Authentication / paywall
- Stripe integration (Bob already has Stripe connected)
- Email delivery (replace Substack's email with something like Buttondown, ConvertKit, or Resend)
- Subscriber management

### Timeline
- Not until the research product is fully mature and subscriber base justifies the migration cost
- Substack's distribution/discovery value still matters during growth phase
- This is a "when it makes sense" move, not a "rush to do it" move

---

## BRAND & DESIGN CONSTRAINTS

All pages must follow the existing brand system:

### Colors (23/89/BB Mnemonic)
| Name | Hex | Usage |
|------|-----|-------|
| Ocean | `#2389BB` | Primary brand, headers, borders |
| Dusk | `#FF6723` | Secondary, accent bar, CTAs |
| Sky | `#23BBFF` | Lighter blue, secondary lines |
| Venus | `#FF2389` | Critical alerts, target lines |
| Sea | `#00BB89` | Tertiary, on-target |
| Doldrums | `#898989` | Spines, labels, secondary text |
| Starboard | `#238923` | Bullish, green |
| Port | `#892323` | Bearish, crisis |
| Fog | `#D1D1D1` | Zero lines, ghost references |

### Typography
- Titles: Montserrat Bold
- Headers: Montserrat Bold/SemiBold
- Body: Inter Regular
- Data/Code: Source Code Pro

### Accent Bar
- Ocean for 2/3 width (left), Dusk for 1/3 (right)
- Height: 4px on web

### General
- White theme primary
- No emdashes (commas, periods, colons, parentheses, ellipses)
- No semicolons
- Voice: 80% institutional rigor, 20% personality, 0% forced flair

---

## SUBSTACK FRUSTRATIONS (CONTEXT)

Bob's issues with Substack (informing the migration timeline):
- Shift toward algorithmic social media / Notes feature
- Can't render interactive HTML charts or custom formatting
- Forces multi-platform friction (Twitter → LHM → Substack → subscribe)
- Doesn't support the visual/interactive quality of LHM's best work
- Still valuable for: email delivery, subscriber discovery, existing audience

**Current stance:** Stay on Substack for now, but build the website to reduce dependency. The site should be the destination; Substack should be the notification system.

---

## OPEN QUESTIONS

1. **CMS choice:** Jekyll vs headless CMS vs manual HTML for research archive (Phase 2)
2. **Chart hosting:** Static images vs. interactive HTML embeds vs. iframe approach for pillar pages
3. **PDF generation:** Automated pipeline or manual per-pillar?
4. **Analytics:** Add basic analytics to the site? (Plausible, Umami, or similar privacy-respecting option)
5. **Search:** Site search when content grows beyond ~20 pages?
6. **Domain:** Network Solutions expires Sep 9, 2026 — consider moving to Cloudflare or similar

---

## SESSION PROMPT TEMPLATE

When starting a website buildout session, use this prompt context:

```
I'm building out lighthousemacro.com (GitHub Pages, static HTML/CSS/JS).
Reference: /Users/bob/LHM/Strategy/WEBSITE_BUILDOUT_PLAN.md

Current task: [specific task from the phase checklist]

Key files:
- Website source: /Users/bob/LHM/Website/
- Brand guide: /Users/bob/LHM/Brand/brand-guide.md
- Chart styling: /Users/bob/LHM/Brand/chart-styling.md
- Pillar strategy docs: /Users/bob/LHM/Strategy/PILLAR [N] *.md
- Brand assets: /Users/bob/LHM/Brand/

Requirements:
- Match existing site brand (23/89/BB palette, Montserrat/Inter typography)
- Shared CSS in styles.css
- Mobile responsive
- No build tools (pure HTML/CSS/JS, GitHub Pages compatible)
```

---

**END OF PLAN**
