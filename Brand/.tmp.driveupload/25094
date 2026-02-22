---
name: lhm-brand-system
description: Branded document generation for Lighthouse Macro. Creates PDF reports, PPTX presentations, DOCX documents, and HTML artifacts with consistent brand identity including logo, colors (Ocean Blue #0089D1, Dusk Orange #FF4500), typography (Montserrat/Inter), chart styling, and professional formatting. Use when creating any Lighthouse Macro deliverable: Chartbooks, Beacon analysis, Beam insights, Horizon outlooks, framework documents, presentations, or any branded content. Triggers on requests for LHM-branded materials, macro research formatting, or professional financial document generation.
---

# Lighthouse Macro Brand System

Generate professional, branded documents for Lighthouse Macro with consistent visual identity across all formats.

## Quick Reference

| Element | Value |
|---------|-------|
| Primary Color | `#0089D1` (Ocean Blue) |
| Accent Color | `#FF4500` (Dusk Orange) |
| Header Font | Montserrat Bold |
| Body Font | Inter |
| Logo | `assets/logo.jpg` |
| Banner | `assets/banner.jpg` |
| Tagline | MACRO, ILLUMINATED. |

## Workflow

1. **Identify document type** from user request (Chartbook, Beacon, Beam, Horizon, presentation, report, one-pager, framework doc, etc.)
2. **Read references** as needed:
   - `references/brand-guide.md` — colors, fonts, contact info, watermarks
   - `references/chart-styling.md` — borders, captions, layouts, spacing
   - `references/templates.md` — structure for each document type
3. **Apply brand elements:**
   - Logo/banner placement per document type
   - Ocean Blue borders on all charts (2px solid #0089D1)
   - Captions below charts: "Figure N: Description"
   - Accent bar where appropriate (blue-orange gradient)
   - Watermarks: "LIGHTHOUSE MACRO" top-left, "MACRO, ILLUMINATED." bottom-right
4. **Include contact block** in footer:
   ```
   Bob Sheehan, CFA, CMT | Founder & Chief Investment Officer
   Lighthouse Macro | LighthouseMacro.com | @LHMacro
   ```
5. **Use standard sign-off** for written content:
   > That's our view from The Watch. Until next time, we'll be sure to keep the light on...

## Output Formats

### PDF
Use the pdf skill. Apply brand guide specifications for headers, footers, chart borders, and typography.

### PPTX
Use the pptx skill. Apply slide templates from `references/templates.md`:
- Title slide with banner
- Section dividers with Ocean Blue background
- Content slides with logo top-left
- Chart slides with bordered, captioned charts

### DOCX
Use the docx skill. Apply professional report formatting with brand typography and colors.

### HTML
Create styled HTML artifacts with embedded CSS using brand colors and Google Fonts imports for Montserrat and Inter.

## Chart Styling (Critical)

Every chart must have:
```css
border: 2px solid #0089D1;
```

Layout rules per `references/chart-styling.md`:
- **1 column:** Full content width
- **2 columns:** 48% each, 4% gutter
- **4 panels:** 48% × 48% grid
- **Caption:** Centered below, Inter 9-10pt, "Figure N: Description"
- **Spacing:** 8px chart-to-caption, 16px caption-to-next-element

## Document Types

See `references/templates.md` for detailed structure of each document type.

## Asset Paths

- Logo: `/mnt/skills/user/lhm-brand-system/assets/logo.jpg`
- Banner: `/mnt/skills/user/lhm-brand-system/assets/banner.jpg`

Copy these assets to working directory when generating documents that embed images.
