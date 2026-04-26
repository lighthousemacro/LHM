# LIGHTHOUSE MACRO — DESIGN SYSTEM & BRAND KIT (DESIGN.md)

## 1. BRAND IDENTITY
- **Company Name:** Lighthouse Macro
- **Official Acronym:** LHM (Do not use "LM")
- **Taglines / Sign-offs:** "Macro, Illuminated." | "Join The Watch." | "Don't navigate in the dark." | "We'll keep the light on."
- **Brand Ethos:** Institutional rigor, Bloomberg-terminal precision, dry, data-backed. Clean, structured, anchored in reality. Zero clutter, no drop-shadows, no 3D effects, no generic "cartoon" clip-art.

## 2. GLOBAL COLOR PALETTE
**Core Brand Assets (Logos, Headers, Footers, UI, Backgrounds):**
Use ONLY these colors for structural brand design.
- **Ocean:** `#2389BB` (Primary brand color, borders, primary text, base of lighthouse)
- **Dusk:** `#FF6723` (Action color, highlights, "Illuminated" text, light beam, last-value pills)
- **Sky:** `#23BBFF` (Secondary accent, secondary light beams, UI highlights)
- **White:** `#FFFFFF` (Primary background, text inside Dusk pills)
- **Fog:** `#D1D1D1` (Muted UI elements, inactive states)
- **Doldrums:** `#898989` (Secondary text, metadata, subtle borders)
- **Glacier/Off-White:** `#F4F7F9` (Subtle institutional background for slide decks, asset sheets, and large panels)

**Data Visualization / Charting ONLY (Do NOT use in logos/headers):**
- **Sea:** `#00BB89` (Positive flows, structural support)
- **Venus:** `#FF2389` (Extreme divergences, risk flags)
- **Starboard:** `#238923` (Standard positive technicals)
- **Port:** `#892323` (Standard negative technicals)

## 3. TYPOGRAPHY ("The Quant Terminal" Aesthetic)
- **Primary Font (Headers, Titles, Logos):** `IBM Plex Sans` (Bold/Semi-Bold). Industrial, slightly squared, technical.
- **Secondary Font (Body Text, Long-form Analysis):** `IBM Plex Serif` (Regular). Highly legible for institutional white papers. 
- **Tertiary Font (Data Labels, MRI Outputs, Charts):** `IBM Plex Mono`. Monospace font to elevate the database/code-first credibility.
- **Styling Rules:** Short sentences. Sharp alignment (Left or Center depending on component). Never use cursive or highly decorative fonts.

## 4. COMPONENT STYLING & BORDERS
- **Borders:** Containers, charts, and header blocks must have a **4.0pt solid Ocean (`#2389BB`) border**. 
- **Spines:** All four spines (top, bottom, left, right) must be visible on framed elements.
- **Data Pills ("Last-Value Pills"):** Used to highlight critical current data (e.g., MRI readings). Must be a bold White (`#FFFFFF`) text centered inside a solid Dusk (`#FF6723`) pill/rectangle.
- **Backgrounds:** Default to Pure White (`#FFFFFF`) for content cards. Main canvas/slide backgrounds can use Glacier (`#F4F7F9`). No gradients unless strictly necessary for a subtle Sky-to-White transition.

## 5. LOGO & ICONOGRAPHY
- **Lighthouse Icon:** Clean, geometric vector. Base is Ocean (`#2389BB`). Single sharp beam of light is Sky (`#23BBFF`) or Dusk (`#FF6723`).
- **Acronym Mark:** The letters "LHM" in heavy `IBM Plex Sans` bold, Ocean (`#2389BB`), often paired with the minimalist lighthouse icon to the left.
- **Methodology Icons (The 3 Engines):** 1. Macro Dynamics (Factory/Globe)
  2. Monetary Mechanics (Bank/Liquidity/Pipes)
  3. Market Structure (Charts/Dials)
  *Rule:* Icons must be line-art or flat vector (Ocean/Sky). NO 3D, NO drop shadows.

## 6. CHARTING & DATA VISUALIZATION RULES (STRICT)
If generating code for charts (Python/Matplotlib/Plotly) or SVG chart mocks:
- **Gridlines:** NONE. (No vertical, no horizontal).
- **Ticks:** NONE.
- **Spines:** All 4 spines visible, colored Ocean (`#2389BB`), thickness 4.0pt.
- **Background:** White.
- **Labels:** Crisp, readable (`IBM Plex Mono` for axis, `IBM Plex Sans` for titles). Last value must be highlighted using the Dusk "Last-Value Pill" design.

## 7. STANDARD TEMPLATE LAYOUTS
**Email / Substack Header (1100x200 px):**
- 4.0pt Ocean border.
- Left: Lighthouse icon + "LIGHTHOUSE MACRO" (Ocean) + "Macro, Illuminated." (Dusk) + "Join The Watch." (Doldrums).
- Right: Systematic engine diagram OR a clean data box displaying "MRI v2.0" and the current regime.

**Slide Decks (16:9):**
- **Title Slide:** Ocean banner at top/bottom, large `IBM Plex Sans` Bold title, centered.
- **Content Slide:** LHM Logo top left, Title top, chart/bullets taking 70-80% of slide area, page number bottom right.
- **Divider:** Solid Ocean background, white text.

**Social Media (X/Twitter & LinkedIn):**
- Maintain Glacier background (`#F4F7F9`). Center LHM logo or full Lighthouse Macro text. Keep it sparse. Let the brand colors breathe.