# Lighthouse Macro — Chart Styling Specification

**Version:** 4.0 (2026 Signature Palette + White Primary) **Last Updated:** February 23, 2026 **Purpose:** Canonical reference for all Lighthouse Macro chart generation. Update this file when standards change.

---

## Primary Theme: White

**White theme is the default for all publications:** Substack, PDF, social media, Chartbook. Dark theme is optional secondary (e.g., for website hero sections or special presentations).

---

## TT Deck Format (Primary Standard)

All educational, research, and deck charts follow this format unless explicitly overridden.

### Figure-Level Branding

ElementPositionStyle**Lighthouse icon**Top-left corner128px PNG, transparent bg, \~0.018 figure width**LIGHTHOUSE MACRO**Top-left, right of iconOcean `#2389BB`, bold, fontsize 13, x=0.035**Date**Top-rightMuted color, fontsize 11, `%B %d, %Y` format**Top accent bar**Below watermarksOcean 2/3, Dusk 1/3, height 0.004**Bottom accent bar**Above footerMirror of top bar**MACRO, ILLUMINATED**.Bottom-rightOcean `#2389BB`, bold italic, fontsize 13**Source line**Bottom-leftMuted, italic, fontsize 9, format: \`Lighthouse Macro

**Note:** Branding elements (watermarks, accent bars) always use Ocean/Dusk regardless of theme. They are not theme-driven.

### Title & Subtitle

ElementStyle**Title**fontsize 15, bold, centered, `y=0.945`, theme foreground color**Subtitle**fontsize 14, italic, Ocean `#2389BB` (always Ocean, not theme-driven), centered, `y=0.895`

### Subplot Margins (fig.subplots_adjust)

```python
# Standard for all charts:
fig.subplots_adjust(top=0.88, bottom=0.08, left=0.06, right=0.94)
```

### Lighthouse Icon Implementation

```python
ICON_PATH = f'{BASE_PATH}/Brand/icon_transparent_128.png'

# In brand_fig(), before the "LIGHTHOUSE MACRO" text:
if os.path.exists(ICON_PATH):
    icon_img = mpimg.imread(ICON_PATH)
    icon_w = 0.018
    icon_aspect = icon_img.shape[0] / icon_img.shape[1]
    fig_aspect = fig.get_figwidth() / fig.get_figheight()
    icon_h = icon_w * icon_aspect * fig_aspect
    icon_ax = fig.add_axes([0.012, 0.985 - icon_h, icon_w, icon_h])
    icon_ax.imshow(icon_img, aspect='equal')
    icon_ax.axis('off')
```

- Icon file: `Brand/icon_transparent_128.png` (128x290px, RGBA, transparent background)
- Sized to \~0.018 figure width, aspect-ratio preserved
- Positioned top-left, vertically centered with "LIGHTHOUSE MACRO" text
- `os.path.exists` guard so charts still render if icon is missing

### Accent Bar Implementation

```python
# Top accent bar
bar = fig.add_axes([0.03, 0.955, 0.94, 0.004])
bar.axhspan(0, 1, 0, 0.67, color='#2389BB')   # Ocean 2/3
bar.axhspan(0, 1, 0.67, 1.0, color='#FF6723')  # Dusk 1/3
bar.set_xlim(0, 1); bar.set_ylim(0, 1); bar.axis('off')

# Bottom accent bar (mirror)
bbar = fig.add_axes([0.03, 0.035, 0.94, 0.004])
bbar.axhspan(0, 1, 0, 0.67, color='#2389BB')
bbar.axhspan(0, 1, 0.67, 1.0, color='#FF6723')
bbar.set_xlim(0, 1); bbar.set_ylim(0, 1); bbar.axis('off')
```

---

## Helper Functions (Core API)

These are the standard helper functions used by all chart scripts. They encapsulate the styling rules below.

FunctionPurposeKey Parameters`new_fig(figsize=(14, 8))`Creates figure with theme background and standard margins`figsizestyle_ax(ax, right_primary=True)`Core spine/grid styling. Sets all 4 spines visible at 0.5pt, grid off, tick colors. `right_primary=True` puts ticks on RHS`right_primarystyle_dual_ax(ax1, ax2, c1, c2)`Full dual-axis styling: calls `style_ax`, colors tick labels to series, applies `%.1f` formatters, kills all tick marks`c1` (LHS color), `c2` (RHS color)`style_single_ax(ax)`Full single-axis styling: calls `style_ax(right_primary=True)`, kills tick marks, applies `%.1f` formatterNone`set_xlim_to_data(ax, idx)`Sets x-axis limits with 30-day left and 180-day right padding`idx` (DatetimeIndex)`brand_fig(fig, title, subtitle, source)`Applies all figure-level branding (watermarks, bars, title)`title`, `subtitle`, `sourceadd_last_value_label(ax, y_data, color, ...)`Adds colored pill on axis edge`fmt`, `side`, `fontsize`, `padadd_annotation_box(ax, text, x, y)`Adds takeaway box in dead space`x=0.52`, `y=0.92` defaults`add_recessions(ax, start_date)`Adds recession shading bands`start_date` (optional filter)`legend_style()`Returns legend kwargs dictNone

---

## Axes & Spines

- **All 4 spines visible**, linewidth 0.5, colored to theme spine color
- **No gridlines** (`ax.grid(False)`)
- **No tick marks** on any axis (`length=0` on all `tick_params`)
- Tick labels remain (colored to series on dual-axis charts)
- **No rotated y-axis label text** — the pills and colored tick labels tell the story

### White Theme Spine Color (Primary)

```python
'spine': '#898989'   # Doldrums
```

### Dark Theme Spine Color (Optional)

```python
'spine': '#1e3350'
```

---

## Dual-Axis Charts

### Axis Assignment

- **RHS = Primary = Ocean (the "star" series). ALWAYS.**
- **LHS = Secondary = Dusk. ALWAYS.**
- Tick labels colored to match their series (Ocean RHS, Dusk LHS)

### Styling Flow

```python
# Option A: Use the helper (handles everything)
style_dual_ax(ax1, ax2, c1=c_secondary, c2=c_primary)

# Option B: Manual (when you need custom formatters)
style_ax(ax1, right_primary=False)
ax1.grid(False); ax2.grid(False)
for spine in ax2.spines.values():
    spine.set_color(THEME['spine']); spine.set_linewidth(0.5)
ax1.tick_params(axis='both', which='both', length=0)
ax1.tick_params(axis='y', labelcolor=c_secondary, labelsize=10)
ax1.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.1f}%'))
ax2.tick_params(axis='both', which='both', length=0)
ax2.tick_params(axis='y', labelcolor=c_primary, labelsize=10)
ax2.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.1f}%'))
ax1.yaxis.set_tick_params(which='both', right=False)
ax2.yaxis.set_tick_params(which='both', left=False)
```

### Same-Scale Dual-Axis (Matched Y-Limits)

When both series are in the same units (e.g. both % YoY), match y-limits so scales are identical:

```python
all_min = min(series1.min(), series2.min())
all_max = max(series1.max(), series2.max())
pad = (all_max - all_min) * 0.08
ax1.set_ylim(all_min - pad, all_max + pad)
ax2.set_ylim(all_min - pad, all_max + pad)
```

Use same-scale when series are directly comparable (goods vs services, headline vs core, etc.).

### Independent-Scale Dual-Axis

When series have different magnitudes or units, compute padding independently per axis:

```python
pad1 = (s1.max() - s1.min()) * 0.08
pad2 = (s2.max() - s2.min()) * 0.08
ax1.set_ylim(s1.min() - pad1, s1.max() + pad1)
ax2.set_ylim(s2.min() - pad2, s2.max() + pad2)
```

Use independent scales for lead/lag comparisons, shifted series, or different unit types.

### Combined Legend (Dual-Axis)

```python
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', **legend_style())
```

---

## Single-Axis Charts

- Ticks on RHS (`right_primary=True`)
- RHS pill only
- Use `style_single_ax(ax)` which handles everything

---

## Last-Value Pills

Colored rounded pills with bold white text, positioned on the axis edge.

```python
def add_last_value_label(ax, y_data, color, fmt='{:.1f}%', side='right', fontsize=9, pad=0.3):
    last_y = float(y_data.iloc[-1])
    label = fmt.format(last_y)
    pill = dict(boxstyle=f'round,pad={pad}', facecolor=color, edgecolor=color, alpha=0.95)
    if side == 'right':
        ax.annotate(label, xy=(1.0, last_y), xycoords=('axes fraction', 'data'),
                    fontsize=fontsize, fontweight='bold', color='white',
                    ha='left', va='center',
                    xytext=(6, 0), textcoords='offset points', bbox=pill)
    else:
        ax.annotate(label, xy=(0.0, last_y), xycoords=('axes fraction', 'data'),
                    fontsize=fontsize, fontweight='bold', color='white',
                    ha='right', va='center',
                    xytext=(-6, 0), textcoords='offset points', bbox=pill)
```

### Parameters

ParamDefaultWhen to Override`fmt'{:.1f}%'`Use `'{:.2f}'` for z-scores (no %), `'{:.0f}%'` for integer-scale charts`fontsize9`Use `7` for cramped multi-pill charts (e.g. 3+ series on one axis)`pad0.3`Use `0.2` for smaller pills when space is tight`side'right'`Use `'left'` for secondary axis (LHS) on dual-axis charts

### Legend Labels

- Always include last value in legend label: `f'Core PCE ({val:.1f}%)'`
- Smoothed series should show the smoothed value (not raw) in both legend and pill

---

## X-Axis Padding

```python
padding_left = pd.Timedelta(days=30)
padding_right = pd.Timedelta(days=180)  # ~6 months for yearly charts
```

This creates breathing room between the end of the data lines and the right spine where the pills sit.

---

## Data Handling

- **Always** `dropna()` **before plotting** to prevent line breaks at NaN gaps
- FRED data frequently has sporadic NaN values that create orphaned data points
- **Quarterly data** (e.g. ECI): forward-fill to monthly frequency before plotting
- **Volatile series:** Smooth with 3-month moving average where appropriate (e.g. UMich expectations, dollar YoY)
- **Non-volatile series:** Plot raw. Do not smooth core CPI, core PCE, or other already-smoothed measures
- **Shifted series:** When showing a lead/lag relationship, shift the LAGGING series backward (not the leading series forward) to preserve right-side padding for pills. Note: shifted series need special legend labels indicating the shift (e.g. "shifted 12mo")

```python
g_plot = data['yoy'].dropna()
ax.plot(g_plot.index, g_plot, ...)
```

---

## Reference Lines

### Zero Line (Fog)

```python
ax.axhline(0, color='#D1D1D1', linewidth=0.8, alpha=0.5, linestyle='--')
```

Full-width dashed ghost line. Use `#D1D1D1` (Fog) for standard zero lines.

**Note:** Some charts use `THEME['muted']` for the zero line (e.g. composite z-score charts where the zero line should match the axis text). Either is acceptable, but prefer Ref for YoY% charts and theme muted for z-score charts.

### 2% Target Line (Venus)

```python
ax.axhline(2, color='#FF2389', linewidth=1.0, alpha=0.7, linestyle='--')
ax.text(x, 2.05, '2% Target', color='#FF2389', fontsize=8, ha='left', va='bottom')
```

Use on charts where the Fed's 2% target is relevant (inflation measures, PCE, sticky CPI, etc.).

**Label positioning:** Use `ax.get_yaxis_transform()` for x-coordinate when you want labels anchored to the y-axis data value:

```python
ax.text(0.02, 2.15, '2% Target', fontsize=8, color='#FF2389',
        alpha=0.7, style='italic', transform=ax.get_yaxis_transform())
```

### 3% Danger Zone (Sea)

```python
ax.axhline(3, color='#00BB89', linewidth=1.0, alpha=0.7, linestyle='--')
```

Use on expectations charts where 3% is the de-anchoring threshold.

---

## Annotation Box (Takeaway)

Every chart should have an annotation box with 1-2 line commentary summarizing the takeaway. Positioned in dead space where there is no data.

```python
def add_annotation_box(ax, text, x=0.52, y=0.92):
    ax.text(x, y, text, transform=ax.transAxes,
            fontsize=10, color=THEME['fg'], ha='center', va='top',
            style='italic',
            bbox=dict(boxstyle='round,pad=0.5',
                      facecolor=THEME['bg'], edgecolor='#2389BB',
                      alpha=0.9))
```

- **Border color**: Always Ocean `#2389BB` (hardcoded, not theme-driven)
- **Background**: Theme background color (opaque)
- **Text**: Theme foreground, italic, fontsize 10
- **Default position**: `x=0.52, y=0.92` (slightly right of center, near top)
- **CRITICAL: All annotation text must be dynamic** — use f-strings with live data values. Never hardcode numbers.

### Position Guidelines

Override `x` and `y` to place the box in the largest empty area:

ScenarioSuggested PositionData heavy on left, empty right-top`x=0.52, y=0.92` (default)Data heavy on top, empty bottom`x=0.52, y=0.12`Data heavy on right, empty left-top`x=0.35, y=0.92`Centered data, empty corners`x=0.45, y=0.92`

Always verify visually that the box does not overlap data, legend, recession shading, or pills.

---

## Regime Band Charts (Composite Indices)

For composite z-score indicators (PCI, LCI, MSI, etc.), use colored regime bands:

```python
# Regime bands with axhspan
ax.axhspan(1.5, 3.0, color='#892323', alpha=0.25)     # Crisis (Port)
ax.axhspan(1.0, 1.5, color='#FF6723', alpha=0.20)     # High (Dusk)
ax.axhspan(0.5, 1.0, color='#FF6723', alpha=0.12)     # Elevated (Dusk)
ax.axhspan(-0.5, 0.5, color='#00BB89', alpha=0.12)    # On target (Sea)
ax.axhspan(-3.0, -0.5, color='#23BBFF', alpha=0.12)   # Deflationary/Low (Sky)

# Regime labels — right-aligned inside chart area
ax.text(0.98, 1.75, 'CRISIS', transform=ax.get_yaxis_transform(),
        fontsize=9, color='#892323', va='center', ha='right',
        fontweight='bold', alpha=0.8)
# ... repeat for each zone with appropriate y-coordinate centered in band
```

### Regime Chart Specifics

- Use `style_single_ax(ax)` (single axis, ticks on RHS)
- Y-axis formatter: `f'{x:.1f}'` (no % sign for z-scores)
- Pill format: `fmt='{:.2f}'` (two decimal places, no %)
- Legend label: `f'PCI ({pci.iloc[-1]:.2f})'`
- Annotation should dynamically determine the current regime name

---

## Recession Shading

```python
RECESSIONS = [
    ('2001-03-01', '2001-11-01'),
    ('2007-12-01', '2009-06-01'),
    ('2020-02-01', '2020-04-01'),
]
# White theme (primary): gray, alpha 0.12
# Dark theme (optional): white, alpha 0.06
ax.axvspan(start, end, color=color, alpha=alpha, zorder=0)
```

The `add_recessions(ax, start_date)` helper handles this automatically. Pass `start_date` to skip recessions that ended before the chart's data range.

---

## Legend

```python
legend_style = dict(
    framealpha=0.95,
    facecolor=THEME['legend_bg'],
    edgecolor=THEME['spine'],
    labelcolor=THEME['legend_fg'],
)
ax.legend(loc='upper left', **legend_style())
```

---

## Color Assignments by Theme

**UPDATED (Feb 2026):** Ocean `#2389BB` is PRIMARY for BOTH themes. White theme is primary publication format.

### White Theme (Primary)

RoleColorHexPrimary seriesOcean`#2389BB`Secondary seriesDusk`#FF6723`Tertiary seriesSky`#23BBFF`Quaternary seriesSea`#00BB89`AccentVenus`#FF2389`BackgroundWhite`#ffffff`Foreground textDark`#1a1a1a`Muted textGray`#555555`SpineDoldrums`#898989`Legend bgLight`#f8f8f8`Legend fgDark`#1a1a1a`

### Dark Theme (Optional)

RoleColorHexPrimary seriesOcean`#2389BB`Secondary seriesDusk`#FF6723`Tertiary seriesSky`#23BBFF`Quaternary seriesSea`#00BB89`AccentVenus`#FF2389`BackgroundDark Navy`#0A1628`Foreground textLight`#e6edf3`Muted textGray`#8b949e`SpineDark Blue`#1e3350`Legend bgDark Blue`#0f1f38`Legend fgLight`#e6edf3`

### Full Theme Dictionary

```python
# White theme (PRIMARY — use for all publications)
THEME = {
    'bg': '#ffffff',
    'fg': '#1a1a1a',
    'muted': '#555555',
    'spine': '#898989',          # Doldrums
    'zero_line': '#D1D1D1',      # Fog — ghost reference line
    'recession': 'gray',
    'recession_alpha': 0.12,
    'brand_color': '#2389BB',    # Ocean
    'brand2_color': '#FF6723',   # Dusk
    'primary': '#2389BB',        # Ocean
    'secondary': '#FF6723',      # Dusk
    'tertiary': '#23BBFF',       # Sky
    'quaternary': '#00BB89',     # Sea
    'accent': '#FF2389',         # Venus
    'bullish': '#238923',        # Starboard
    'bearish': '#892323',        # Port
    'fill_alpha': 0.15,
    'box_bg': '#ffffff',
    'box_edge': '#2389BB',       # Ocean
    'legend_bg': '#f8f8f8',
    'legend_fg': '#1a1a1a',
    'mode': 'white',
}

# Dark theme (OPTIONAL — for website hero sections or special presentations)
THEME = {
    'bg': '#0A1628',
    'fg': '#e6edf3',
    'muted': '#8b949e',
    'spine': '#1e3350',
    'zero_line': '#e6edf3',
    'recession': '#ffffff',
    'recession_alpha': 0.06,
    'brand_color': '#2389BB',    # Ocean
    'brand2_color': '#FF6723',   # Dusk
    'primary': '#2389BB',        # Ocean
    'secondary': '#FF6723',      # Dusk
    'tertiary': '#23BBFF',       # Sky
    'quaternary': '#00BB89',     # Sea
    'accent': '#FF2389',         # Venus
    'bullish': '#238923',        # Starboard
    'bearish': '#892323',        # Port
    'fill_alpha': 0.20,
    'box_bg': '#0A1628',
    'box_edge': '#2389BB',       # Ocean
    'legend_bg': '#0f1f38',
    'legend_fg': '#e6edf3',
    'mode': 'dark',
}
```

---

## Outer Border

Every chart gets a **4.0pt Ocean border** at the absolute figure edge. Ocean regardless of theme.

```python
fig.patches.append(plt.Rectangle(
    (0, 0), 1, 1, transform=fig.transFigure,
    fill=False, edgecolor='#2389BB', linewidth=4.0,
    zorder=100, clip_on=False
))
```

---

## Save Settings

```python
fig.savefig(path, dpi=200, bbox_inches='tight', pad_inches=0.025,
            facecolor=THEME['bg'], edgecolor='none')
```

- **DPI**: 200
- **No** `tight_layout()` — conflicts with accent bar axes
- Use `bbox_inches='tight'` with `pad_inches=0.025`

---

## Publishing Workflow

**White theme is primary.** Generate white theme for all publications.

```
Output structure:
  /Outputs/.../white/chart_XX_name.png    # PRIMARY — use for Substack, PDF, social
  /Outputs/.../dark/chart_XX_name.png     # OPTIONAL — website, special presentations
```

- **Substack**: White theme charts
- **PDF**: White theme charts
- **Social media (X, LinkedIn)**: White theme (works well in both light and dark mode feeds)
- **Chartbook**: White theme
- **Website hero sections**: Dark theme optional

---

## Signature 8-Color Palette (Quick Reference)

NameHexMnemonicUsage**Ocean**`#2389BB`23+89+BBPrimary data, borders, branding**Dusk**`#FF6723`23Secondary series, accent bar, CTAs**Sky**`#23BBFF`BBTertiary data lines**Venus**`#FF2389`23+892% target lines, critical alerts**Sea**`#00BB89`BB+89Regime bands, on-target zones**Doldrums**`#898989`89+89Spines, labels, structural gray**Starboard**`#238923`23+89Bullish regime**Port**`#892323`89+23Bearish regime, crisis bands**Fog**`#D1D1D1`D1+D1Zero lines, ghost references

---

## Reference Implementation

The canonical implementation of this spec lives in:

```
/Users/bob/LHM/Scripts/utilities/lighthouse_chart_style.py
```

For the TT research deck implementation:

```
/Users/bob/LHM/Scripts/chart_generation/tt_research_charts.py
```

---

## PDF Generation

Branded PDFs follow the style established in:

```
/Users/bob/LHM/Scripts/generate_two_books_pdf.py  (canonical PDF style)
/Users/bob/LHM/Scripts/chart_generation/prices_edu_pdf.py  (educational article PDF)
```

Key elements: full-width Ocean/Dusk header bar with white text, matching thin footer bar, Ocean `#2389BB` H1/H2 headings, Ocean table headers with white text, justified body at 10pt. Open PDFs with PDF Expert.

---

## TradingView Charts

The same 23/89/BB palette and brand logic that governs matplotlib output governs our TradingView charts. Styling is not a separate system. It is the same specification, implemented in Pine Script and TradingView's native controls.

Pine Script source for all LHM indicators lives in `/Users/bob/LHM/Scripts/tradingview/`. TradingView is the deployment target. The repo is the source of truth. Update the `.pine` files here, then paste into the TradingView editor.

### Standard Layout: 3-Panel Stack

All LHM price analysis uses a three-panel stacked layout:

1. **Price** (main chart)
2. **LHM Relative Strength** (indicator pane)
3. **LHM Z-RoC Momentum** (indicator pane)

### Panel 1: Price

Hollow candle style. Black or dark gray. Up candles hollow, down candles filled.

Timeframe defaults to daily. Typical lookback is 7.5 years, long enough for cycle context without noise compression. Weekly bars only for structural views on assets with 15+ years of history (25+ preferred). Monthly is rare and only after month close.

**Moving averages**, in order of frequency:

PeriodColorHexFrequency50-dayDusk`#FF6723`Always200-dayOcean`#2389BB`Always200-weekSky`#23BBFF`Structural views, occasional50-weekVenus`#FF2389`Rare

**Support, resistance, trendlines, curves:** Sea `#00BB89`.

Line extension rule: draw just past the actual touch zones, not all the way across the chart. Think of an umbrella, not a flagpole. For 5+ year charts, extend roughly 21 bars on either side of the touch zone. Right edge may extend \~1 month into the future for active levels.

### Panel 2: LHM Relative Strength

Source: `/Users/bob/LHM/Scripts/tradingview/lhm_relative_strength.pine`

Plots `(symbol / benchmark) * 100`. Benchmark auto-detects by asset type, with manual override available.

**Benchmark auto-detect logic:**

Asset TypeDefault BenchmarkEquities (SPY / IVV / VOO)RSP (equal-weighted)Equities (QQQ / QQQM)QQEW (equal-weighted)Equities (other)RUA (Russell 3000)CryptoCRYPTOCAP:TOTALForexTVC:DXYCommodity futures (GC, SI, CL, NG, HG, PL, PA)SPGSCIRate futures (ZB, ZN, ZF, ZT, TN)TVC:US10Y

**Three-state line color:**

StateColorHexConditionBullish regimeStarboard`#238923`RS &gt; SMA(63) &gt; SMA(252)Bearish regimePort`#892323`RS &lt; SMA(63) &lt; SMA(252)Neutral / transitionalBlack—Anything else

Linewidth 3 for the RS series. SMAs rendered in muted gray at linewidth 1 so the regime color carries the visual weight.

### Panel 3: LHM Z-RoC Momentum

Source: `/Users/bob/LHM/Scripts/tradingview/lhm_z_roc.pine`

Dual-timeframe momentum composite. Tactical window is 21-day rate of change. Regime window is 63-day. Both z-scored over a 252-day lookback, robust (median / MAD) as default. Final series is a 5-period EMA of the tactical z.

**Three-state line color** (mirrors the RS panel philosophy):

| State | Color | Hex | Condition |
|---|---|---|---|
| Long bias | Sky | `#23BBFF` | Tactical z bullish (>0, >signal, rising) AND regime z > 0 |
| Short bias | Venus | `#FF2389` | Tactical z bearish (<0, <signal, falling) AND regime z < 0 |
| Neutral | Ocean | `#2389BB` | Everything else (mixed, transitional, against-regime) |

**Reference lines:**

| Line | Color | Style |
|---|---|---|
| Zero | Doldrums `#898989` | Dotted |
| ±2σ | Doldrums `#898989` | Solid, weight 2 |
| ±1σ | Doldrums 70% | Dashed, toggleable |

**Divergence dots are OFF by default.** The detection logic is built in, but the `Show Divergence Dots?` input defaults to `false`. We turn them on deliberately when we want them, not by default. When enabled:

- Bullish divergence: Sea `#00BB89` upward triangle
- Bearish divergence: Venus `#FF2389` downward triangle
- Pivot detection window: 5 bars on either side

### Alerts

Both indicators expose alerts for standard events:

- RS: SMA crosses (fast above/below slow), RS crosses of fast SMA
- Z-RoC: signal crosses (Z above/below EMA), ±2σ breaches, divergence triggers

Use sparingly. Chart noise is cheaper than alert fatigue.

### Updating Pine Script Indicators

1. Edit the `.pine` file in `/Users/bob/LHM/Scripts/tradingview/`
2. Copy the full file contents
3. In TradingView, open the Pine Editor, paste, and save with the existing indicator name
4. Commit the `.pine` file change to the LHM repo

TradingView does not auto-sync from git. The repo is where we version; TradingView is where we view.

---
