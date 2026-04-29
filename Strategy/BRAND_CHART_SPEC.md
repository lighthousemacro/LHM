# Brand Chart Spec — Canonical

**Author:** Bob Sheehan, CFA, CMT | Lighthouse Macro
**Created:** 2026-04-24
**Status:** Active. Supersedes any earlier ad-hoc chart styling. All LHM chart code must conform.
**Single source of truth:** `/Users/bob/LHM/Scripts/chart_generation/lhm_chart_template.py`

---

## TL;DR

Every LHM chart reads as one system. Any new chart script must import from `lhm_chart_template.py` rather than redefining styling inline. If something looks off, the template is law — the chart is wrong.

This doc codifies the spec reverse-engineered from:
- Pillar 11 (Market Structure) educational charts
- Pillar 12 (Sentiment & Positioning) educational charts
- Beam "Rally Reconcentrated" (Apr 23, 2026)
- Beam "The Broadening Broke" (Apr 23, 2026)
- Beam "Retail Sales March 2026" (Apr 21, 2026)

All five use the canonical spec. They are the reference.

---

## 1. Figure

| Element | Value | Source |
|---|---|---|
| Figsize (standard) | `(14, 8)` inches | `new_fig()` |
| Figsize (multi-panel) | `(14, 10)` inches | `new_fig_multi()` |
| Subplot margins | top=0.88, bottom=0.08, left=0.06, right=0.94 | `new_fig()` |
| DPI | 200 | `save_fig()` |
| bbox_inches | `'tight'` | `save_fig()` |
| pad_inches | **0.025** | `save_fig()` |
| Background (white theme) | `#ffffff` | `set_theme('white')` |
| Background (dark theme) | `#0A1628` | `set_theme('dark')` |

### Border frame

| Element | Value |
|---|---|
| Color | Ocean `#2389BB` |
| Line width | **4.0 pt** |
| Fill | none |
| zorder | 100 |
| clip_on | False |

Drawn via `fig.patches.append(plt.Rectangle(...))` in `save_fig()`. Four-point stroke — thicker than the spines — so it reads as a true frame, not just a bounding box.

---

## 2. Top Brand Band

The region above the chart data (roughly y=0.89 to y=1.0 in figure coordinates) contains four elements.

### 2a. Lighthouse icon (top-left)

| Parameter | Value |
|---|---|
| Source file | `/Users/bob/LHM/Brand/icon_transparent_128.png` |
| Figure position x | 0.012 |
| Figure position width | 0.018 |
| Top anchor y | 0.985 |
| Aspect | preserved, scaled to fig aspect |

### 2b. "LIGHTHOUSE MACRO" text (top-left, next to icon)

| Parameter | Value |
|---|---|
| Font | Default sans (matplotlib default) |
| Size | 13 pt |
| Weight | bold |
| Color | Ocean `#2389BB` |
| Figure position x | 0.035 |
| Figure position y | 0.98 |
| Vertical align | top |

### 2c. Current date (top-right)

| Parameter | Value |
|---|---|
| Format | `%B %d, %Y` (e.g., "April 24, 2026") |
| Size | 11 pt |
| Color | Doldrums `#898989` (muted) |
| Figure position x | 0.97 |
| Figure position y | 0.98 |
| Horizontal align | right |
| Vertical align | top |

### 2d. Top accent bar

| Parameter | Value |
|---|---|
| Figure position | x=0.03, y=0.955, width=0.94, height=0.004 |
| Ocean portion | 0 to 67% of width |
| Dusk portion | 67% to 100% of width |
| Ocean hex | `#2389BB` |
| Dusk hex | `#FF6723` |

---

## 3. Title Block (inside header band)

### 3a. Title

| Parameter | Value |
|---|---|
| Font size | 15 pt |
| Weight | bold |
| Color | fg (black `#1a1a1a` white theme / light `#e6edf3` dark theme) |
| Figure y | 0.945 |
| Position | `suptitle`, horizontally centered |

### 3b. Subtitle (italic, Ocean)

| Parameter | Value |
|---|---|
| Font size | **14 pt** |
| Style | italic |
| Color | Ocean `#2389BB` |
| Figure x | 0.5 (centered) |
| Figure y | 0.895 |
| Horizontal align | center |

---

## 4. Axes

### Spines

| Parameter | Value |
|---|---|
| Top, right, left, bottom | all visible |
| Line width | 0.5 pt |
| Color | Doldrums `#898989` |

### Gridlines

| Parameter | Value |
|---|---|
| Major / minor | **none** — no gridlines, ever |

### Ticks

| Parameter | Value |
|---|---|
| Tick length | 0 (no tick marks) |
| Label size | 10 pt |
| Label color | fg (matches text color) |
| Primary axis | right (unless dual) |

### Dual-axis

| Side | Color matches |
|---|---|
| Left (secondary) | line color c1 |
| Right (primary) | line color c2 |

---

## 5. Reference Lines

| Type | Color | Style |
|---|---|---|
| Zero line | Fog `#D1D1D1` | dashed, 0.8 pt |
| 2% inflation target | Venus `#FF2389` | solid |
| 3% danger level | Sea `#00BB89` | solid |
| Regime threshold | Starboard / Port | solid, 0.5-0.6 pt |

---

## 6. Annotations

### Pills (last-value labels)

| Parameter | Value |
|---|---|
| Shape | rounded rectangle (boxstyle `round,pad=0.3`) |
| Fill | matches series color |
| Edge | matches series color |
| Alpha | 0.95 |
| Text color | white |
| Font size | 9 pt |
| Weight | bold |
| Position | flush with axis spine, offset 6 px outward |
| **Right-edge pad** | **6% of plotted span** (via `set_xlim_to_data(..., right_frac=0.06)`) — prevents pill colliding with last data point |

### Callout boxes

| Parameter | Value |
|---|---|
| Background | white (box_bg) |
| Border color | Ocean |
| Border width | 1.5 pt |
| Pad | 0.5 |
| Text size | 14 pt |
| Text color | Ocean |
| Text weight | bold |
| Text style | italic |
| zorder | 20 (above data) |

### Legend

| Parameter | Value |
|---|---|
| Background | `#f8f8f8` white theme / `#0f1f38` dark |
| Edge color | Doldrums white / Sky dark |
| Alpha | 0.95 |
| Location | upper left default |

---

## 7. Bottom Brand Band

### 7a. Source footer (bottom-left)

| Parameter | Value |
|---|---|
| Format | `Lighthouse Macro \| {source} \| Data thru {data_date} \| Pulled {pull_date}` |
| Date format | `%m.%d.%Y` |
| Size | 9 pt |
| Color | Doldrums (muted) |
| Style | italic |
| Figure x | 0.03 |
| Figure y | 0.022 |
| Horizontal align | left |
| Vertical align | top |

### 7b. "MACRO, ILLUMINATED." (bottom-right)

| Parameter | Value |
|---|---|
| Size | 13 pt |
| Weight | bold |
| Style | italic |
| Color | Ocean |
| Figure x | 0.97 |
| Figure y | 0.025 |
| Horizontal align | right |
| Vertical align | top |

### 7c. Bottom accent bar

Identical to top accent bar, positioned at y=0.035.

---

## 8. Palette

| Name | Hex | Canonical usage |
|---|---|---|
| Ocean | `#2389BB` | Primary brand, headers, borders, chart primary |
| Dusk | `#FF6723` | Secondary series, accent bar, CTA |
| Sky | `#23BBFF` | Lighter blue for tertiary series |
| Venus | `#FF2389` | 2% target lines, critical alerts |
| Sea | `#00BB89` | Tertiary, on-target regime bands |
| Doldrums | `#898989` | Axis spines, labels, muted text |
| Starboard | `#238923` | Bullish regime |
| Port | `#892323` | Bearish regime, crisis bands |
| Fog | `#D1D1D1` | Zero lines, ghost reference |

---

## 9. Common Drift Sources

These are what to check first when a chart "looks off":

| Mistake | Symptom | Fix |
|---|---|---|
| Border width 1.5pt instead of 4.0pt | Frame looks thin, underbranded | Import `save_fig` from template |
| pad_inches 0.15 instead of 0.025 | Too much outside padding, tight-bbox unnecessary | Import `save_fig` from template |
| Subtitle 12pt instead of 14pt | Subtitle looks small, unbalanced with title | Import `brand_fig` from template |
| Title 13pt instead of 15pt | Title underweight | Import `brand_fig` from template |
| Accent bars positioned at y=0.92 / y=0.04 | Accent bars don't line up with other charts | Use exact values: top 0.955, bottom 0.035 |
| "LIGHTHOUSE MACRO" inside plot area | Old pillar-article layout | Re-render with current `brand_fig()` |
| Tick marks visible | Plot looks busy | `tick_params(length=0)` via `style_*_ax()` |
| Gridlines visible | Plot looks like default matplotlib | `ax.grid(False)` via `style_*_ax()` |
| Data drawn in non-palette colors | Visual incoherence | Cycle the 5 canonical colors: Ocean, Dusk, Sky, Sea, Venus |
| Data starts mid-history on the LHS, gap before earliest visible point | Pre-windowed data load instead of full history | Always load full available history; `set_xlim()` controls the visible window, never the data |
| z-scores or rolling stats look wrong / regime classifications drift | Statistics computed on a windowed subset instead of full series | Recompute on the full-history series. Display window doesn't change baseline. |
| Multi-series chart shows a solo line for years before the second series begins | Display window defaulted to overall-earliest start date instead of overlap start | Default visible window to LHS = MAX(per-series start dates) — the chart is communicating a *relationship*, default to where the relationship exists. Override only if Bob explicitly asks for solo pre-overlap history. |

---

## 10. Required Workflow

Every new chart script MUST:

1. Import from the template:
```python
from lhm_chart_template import (
    COLORS, set_theme, new_fig, style_single_ax, style_dual_ax,
    add_annotation_box, add_last_value_label, add_recessions,
    set_xlim_to_data, legend_style, save_fig, brand_fig, align_yaxis_zero
)
```
2. Call `set_theme('white')` at start of render.
3. Use `new_fig()` or `new_fig_multi()` to construct figure.
4. Use `style_single_ax` / `style_dual_ax` for axis styling.
5. Plot data using `COLORS[name]` — never inline hex codes.
6. Call `brand_fig(fig, title, subtitle, source, data_date)` after plotting.
7. Call `save_fig(fig, path)` to save with border.

Never redefine brand elements inline. If the template lacks something you need, extend the template, not the caller.

---

## 11. Chartbook-Only Addition

Chartbooks use `/Users/bob/LHM/Scripts/chart_generation/chartbook_layout.py` to add a commentary block below the chart. The commentary block is Chartbook-only. Beams, Beacons, Horizons use the base Beam-style chart with no modification.

See `/Users/bob/LHM/Strategy/BEAM_CHARTBOOK_CADENCE.md` for the Chartbook workflow.

---

## 12. Voice Rules (Chart Titles, Subtitles, Annotations)

All text inside chart frames inherits the house voice rules:

- **No emdashes.** Commas, periods, colons, parentheses, ellipses instead.
- **No "Not X, it's Y" construction.** Zero instances. Never as a closer.
- **No portfolio-framework language in public copy** until PiTrade is live. Internal terminology ("framework-driven sizing," "technical sleeve," "humility patch," and any legacy "Core Book" / "Technical Overlay Book" framings) stays internal.
- **No AI-tell phrases** ("cautiously optimistic," "geopolitical uncertainty," "it is important to note," "at the end of the day").
- **"We" frame** when referring to our own analysis.

The `chartbook_layout.py` commentary block has an automated voice validator. Apply the same rules by hand to titles, subtitles, and in-chart annotations in the base chart code.

---

## 13. Versioning

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-04-24 | Initial spec reverse-engineered from Pillars 11+12 + last 3 Beams |

When a new brand element gets introduced, update `lhm_chart_template.py` first, then append to this spec with a new version row.

---

**End of spec.**

*Bob Sheehan, CFA, CMT | Founder & Chief Investment Officer*
*Lighthouse Macro | LighthouseMacro.com | @LHMacro*
