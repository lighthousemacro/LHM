"""
LHM Canonical Chart Template
============================

Shared styling module for all Lighthouse Macro chart generation.
Extracted from the Educational Series (Pillar 11 / Pillar 12 scripts) which
produced the canonical pillar chart look that all other LHM charts must match.

Usage:
    from lhm_chart_template import (
        COLORS, RECESSIONS, set_theme, new_fig, new_fig_multi,
        style_ax, style_dual_ax, style_single_ax,
        add_annotation_box, add_last_value_label, add_recessions,
        set_xlim_to_data, legend_style, save_fig, brand_fig,
        align_yaxis_zero
    )

This is the SINGLE source of truth for LHM chart styling. If the brand spec
changes, update THIS file and every downstream chart generator inherits it.
"""

import os
from datetime import datetime

import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import FuncFormatter


# ============================================
# PALETTE (23/89/BB mnemonic)
# ============================================
COLORS = {
    'ocean':     '#2389BB',  # primary brand
    'dusk':      '#FF6723',  # secondary / accent (top tier)
    'sky':       '#23BBFF',  # secondary / lighter blue (top tier)
    'bright':    '#89ccff',  # secondary / soft sky (top tier) — pops on dark
    'deep':      '#123456',  # secondary / deep navy (top tier) — dark-theme bg
    'venus':     '#FF2389',  # critical alerts / 2% target
    'sea':       '#00BB89',  # tertiary / on-target bands
    'doldrums':  '#898989',  # spines, muted text
    'starboard': '#238923',  # bullish regime
    'port':      '#892323',  # bearish regime / crisis bands
    'fog':       '#D1D1D1',  # zero lines, ghost refs
    'offwhite':  '#f4f7f9',  # secondary surface / card bg
    'glacier':   '#e8f1f7',  # pale icy blue — light-theme page bg
}

# Multi-series cycling order. Use this when plotting >2 lines so the
# series colors stay on-brand. Top tier (Ocean/Dusk/Sky/Bright/Deep) leads;
# Sea/Venus/Doldrums fill in below.
LHM_PALETTE = [
    COLORS['ocean'], COLORS['dusk'], COLORS['sky'],
    COLORS['bright'], COLORS['deep'],
    COLORS['sea'], COLORS['venus'], COLORS['doldrums'],
]

RECESSIONS = [
    ('1953-07-01', '1954-05-01'),
    ('1957-08-01', '1958-04-01'),
    ('1960-04-01', '1961-02-01'),
    ('1969-12-01', '1970-11-01'),
    ('1973-11-01', '1975-03-01'),
    ('1980-01-01', '1980-07-01'),
    ('1981-07-01', '1982-11-01'),
    ('1990-07-01', '1991-03-01'),
    ('2001-03-01', '2001-11-01'),
    ('2007-12-01', '2009-06-01'),
    ('2020-02-01', '2020-04-01'),
]

ICON_PATH = '/Users/bob/LHM/Brand/icon_transparent_128.png'

# ============================================
# THEME CONFIG
# ============================================
THEME = {}

def set_theme(mode='white'):
    """Set global theme: 'white' (primary) or 'dark'.

    White: pure white paper bg, ink text, Doldrums spines.
    Dark: Deep (#123456) bg, offwhite text, slightly lifted spine for contrast.
    """
    if mode == 'dark':
        # Two-surface rule on dark: page canvas (Deep #123456) and chart canvas
        # must differ so charts don't visually merge into the page. The chart
        # PNG renders on Deep-lift (#1a3a5a), so when it's placed on a Deep
        # page (via the HTML scaffold) the chart reads as a lifted card.
        THEME.update({
            'bg': '#1a3a5a',               # chart canvas (Deep-lift); page sits on Deep behind it
            'page_bg': COLORS['deep'],     # page/document bg consumers should set themselves
            'fg': COLORS['offwhite'],      # Offwhite text/labels
            'muted': '#9bb1c5',
            'spine': '#3b5a7a',            # legible spine against Deep-lift
            'zero_line': COLORS['offwhite'],
            'recession': '#ffffff', 'recession_alpha': 0.06,
            'ocean': COLORS['ocean'], 'dusk': COLORS['dusk'],
            'sky': COLORS['sky'], 'bright': COLORS['bright'],
            'sea': COLORS['sea'], 'venus': COLORS['venus'],
            # On Deep-lift, Bright still leads — it's the highest-contrast
            # primary line color on a dark canvas.
            'primary': COLORS['bright'], 'secondary': COLORS['dusk'],
            'tertiary': COLORS['sky'], 'quaternary': COLORS['sea'],
            'accent': COLORS['venus'], 'fill_alpha': 0.22,
            'box_bg': '#1a3a5a', 'box_edge': COLORS['bright'],
            'legend_bg': '#22466e', 'legend_fg': COLORS['offwhite'],
            'mode': 'dark',
        })
    else:
        THEME.update({
            'bg': '#ffffff', 'fg': '#1a1a1a', 'muted': '#555555',
            'spine': COLORS['doldrums'], 'zero_line': COLORS['fog'],
            'recession': 'gray', 'recession_alpha': 0.12,
            'ocean': COLORS['ocean'], 'dusk': COLORS['dusk'],
            'sky': COLORS['sky'], 'bright': COLORS['bright'],
            'sea': COLORS['sea'], 'venus': COLORS['venus'],
            # On white bg, Ocean and Deep are the workhorse high-contrast pair.
            'primary': COLORS['ocean'], 'secondary': COLORS['dusk'],
            'tertiary': COLORS['sky'], 'quaternary': COLORS['sea'],
            'accent': COLORS['venus'], 'fill_alpha': 0.15,
            'box_bg': '#ffffff', 'box_edge': COLORS['ocean'],
            'legend_bg': COLORS['offwhite'], 'legend_fg': '#1a1a1a',
            'mode': 'white',
        })

# ============================================
# FIGURE CONSTRUCTORS
# ============================================
def new_fig(figsize=(14, 8)):
    """Create single-axis figure with LHM theme and reserved margins for
    the header band (top) and the brand footer (bottom).

    Top margin reserved at 0.84 to leave room for: header watermarks at 0.98,
    accent bar at 0.955, title at 0.93, subtitle at 0.87. Plot area begins
    at 0.84 so subtitle and plot are not scrunched."""
    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_facecolor(THEME['bg'])
    ax.set_facecolor(THEME['bg'])
    fig.subplots_adjust(top=0.84, bottom=0.10, left=0.06, right=0.94)
    return fig, ax

def new_fig_multi(rows, cols, figsize=(14, 10)):
    """Create multi-panel figure with LHM theme."""
    fig, axes = plt.subplots(rows, cols, figsize=figsize)
    fig.patch.set_facecolor(THEME['bg'])
    for ax in axes.flat:
        ax.set_facecolor(THEME['bg'])
    fig.subplots_adjust(top=0.84, bottom=0.10, left=0.06, right=0.94,
                        hspace=0.35, wspace=0.25)
    return fig, axes

# ============================================
# AXIS STYLING
# ============================================
def style_ax(ax, right_primary=True):
    """All 4 spines at 0.5pt. No gridlines. Right axis primary by default."""
    ax.grid(False)
    for spine in ['top', 'right', 'left', 'bottom']:
        ax.spines[spine].set_visible(True)
        ax.spines[spine].set_linewidth(0.5)
        ax.spines[spine].set_color(THEME['spine'])
    ax.tick_params(colors=THEME['fg'], labelsize=10)
    ax.xaxis.label.set_color(THEME['fg'])
    ax.yaxis.label.set_color(THEME['fg'])
    ax.title.set_color(THEME['fg'])
    if right_primary:
        ax.yaxis.tick_right()
        ax.yaxis.set_label_position('right')

def style_dual_ax(ax1, ax2, c1, c2):
    """Full styling for dual-axis chart. c1=left color, c2=right color."""
    style_ax(ax1, right_primary=False)
    ax1.grid(False); ax2.grid(False)
    for spine in ax2.spines.values():
        spine.set_color(THEME['spine'])
        spine.set_linewidth(0.5)
    ax1.tick_params(axis='both', which='both', length=0)
    ax1.tick_params(axis='y', labelcolor=c1, labelsize=10)
    ax2.tick_params(axis='both', which='both', length=0)
    ax2.tick_params(axis='y', labelcolor=c2, labelsize=10)
    ax1.yaxis.set_tick_params(which='both', right=False)
    ax2.yaxis.set_tick_params(which='both', left=False)

def style_single_ax(ax, fmt='{:.1f}'):
    """Full styling for single-axis chart with y-axis number formatting."""
    style_ax(ax, right_primary=True)
    ax.tick_params(axis='both', which='both', length=0)
    ax.tick_params(axis='y', labelcolor=THEME['fg'], labelsize=10)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: fmt.format(x)))

# ============================================
# ANNOTATIONS
# ============================================
def add_annotation_box(ax, text, x=0.50, y=0.95, ha='center'):
    """White callout box with Ocean border and Ocean text.
    Clean, neutral, reads on any background. Larger font.
    High zorder so bars/lines never bleed through."""
    ax.text(x, y, text, transform=ax.transAxes,
            fontsize=14, fontweight='bold', color=COLORS['ocean'],
            ha=ha, va='top', style='italic', zorder=20,
            bbox=dict(boxstyle='round,pad=0.5',
                      facecolor='#ffffff', edgecolor=COLORS['ocean'],
                      linewidth=1.5, alpha=1.0))

def add_last_value_label(ax, y_data, color, fmt='{:.1f}', side='right', fontsize=9, pad=0.3):
    """Colored pill label on axis edge. y_data is a Series or list."""
    if len(y_data) == 0:
        return
    last_y = float(y_data.iloc[-1]) if hasattr(y_data, 'iloc') else float(y_data[-1])
    label = fmt.format(last_y)
    pill = dict(boxstyle=f'round,pad={pad}', facecolor=color, edgecolor=color, alpha=0.95)
    if side == 'right':
        ax.annotate(label, xy=(1.0, last_y), xycoords=('axes fraction', 'data'),
                    fontsize=fontsize, fontweight='bold', color='white',
                    ha='left', va='center', xytext=(6, 0),
                    textcoords='offset points', bbox=pill)
    else:
        ax.annotate(label, xy=(0.0, last_y), xycoords=('axes fraction', 'data'),
                    fontsize=fontsize, fontweight='bold', color='white',
                    ha='right', va='center', xytext=(-6, 0),
                    textcoords='offset points', bbox=pill)

def add_recessions(ax, start_date=None):
    """NBER recession shading."""
    for s, e in RECESSIONS:
        ts, te = pd.Timestamp(s), pd.Timestamp(e)
        if start_date and te < pd.Timestamp(start_date):
            continue
        ax.axvspan(ts, te, color=THEME['recession'],
                   alpha=THEME['recession_alpha'], zorder=0)

def set_xlim_to_data(ax, *indices, right_frac=0.06):
    """X-axis range — data hugs the left spine, configurable right pad.

    LHM rule (locked): 0 left padding, gap on the right for the value pill.
    Default right pad is 6% of the plotted span — enough breathing room so
    the pill never collides with the last data point, while keeping recent
    data visually dominant. Lower values (2-3%) cause the pill to kiss the
    line; higher values (>8%) waste chart real estate.

    Uses LATEST start across all indices for series that begin at different
    dates.
    """
    start = max(idx.min() for idx in indices)
    end = max(idx.max() for idx in indices)
    span = end - start
    right_pad = pd.Timedelta(seconds=span.total_seconds() * (right_frac / (1 - right_frac)))
    ax.set_xlim(start, end + right_pad)

def legend_style():
    """Legend styling dict for ax.legend(**legend_style())."""
    return dict(
        framealpha=0.95,
        facecolor=THEME['legend_bg'],
        edgecolor='#23BBFF' if THEME['mode'] == 'dark' else THEME['spine'],
        labelcolor=THEME['legend_fg'],
    )

def align_yaxis_zero(a1, a2):
    """Align both y-axes at zero for dual-axis charts.

    Use when at least one series crosses zero or is naturally centered at
    zero (z-scores, deviations, spreads vs. baseline). Both axes share a
    horizontal zero line, so overlays line up visually."""
    y1_min, y1_max = a1.get_ylim()
    y2_min, y2_max = a2.get_ylim()
    r1 = abs(y1_min) / max(abs(y1_max), 1e-6)
    r2 = abs(y2_min) / max(abs(y2_max), 1e-6)
    r = max(r1, r2)
    a1.set_ylim(bottom=-r * abs(y1_max), top=y1_max)
    a2.set_ylim(bottom=-r * abs(y2_max), top=y2_max)


def align_yaxis_midpoint(a1, a2, s1=None, s2=None):
    """Align both y-axes at their data midpoints when neither crosses zero.

    Use for positive-only pairs (spread levels, prices, indices). Computes
    each series' median as the alignment anchor and rescales both axes so
    the medians sit at the same y-pixel. Without this, two positive series
    on a dual axis look like they trend the same when they don't, or vice
    versa — overlays mislead.

    If `s1` and `s2` are passed, midpoints come from the actual data. If
    omitted, midpoints come from the current axis limits."""
    import numpy as np

    if s1 is not None and len(s1) > 0:
        mid1 = float(np.nanmedian(np.asarray(s1, dtype=float)))
    else:
        y1_min, y1_max = a1.get_ylim()
        mid1 = (y1_min + y1_max) / 2.0

    if s2 is not None and len(s2) > 0:
        mid2 = float(np.nanmedian(np.asarray(s2, dtype=float)))
    else:
        y2_min, y2_max = a2.get_ylim()
        mid2 = (y2_min + y2_max) / 2.0

    y1_min, y1_max = a1.get_ylim()
    y2_min, y2_max = a2.get_ylim()
    half1 = max(mid1 - y1_min, y1_max - mid1)
    half2 = max(mid2 - y2_min, y2_max - mid2)
    a1.set_ylim(bottom=mid1 - half1, top=mid1 + half1)
    a2.set_ylim(bottom=mid2 - half2, top=mid2 + half2)


def align_yaxis_smart(a1, a2, s1=None, s2=None):
    """Pick the right alignment automatically.

    If either provided series spans zero (or the axis already does), use
    zero alignment. Otherwise use midpoint alignment so positive-only
    overlays still register as comparable.
    """
    import numpy as np

    def _spans_zero(series, axis):
        if series is not None and len(series) > 0:
            arr = np.asarray(series, dtype=float)
            arr = arr[~np.isnan(arr)]
            if arr.size:
                return arr.min() < 0 < arr.max()
        lo, hi = axis.get_ylim()
        return lo < 0 < hi

    if _spans_zero(s1, a1) or _spans_zero(s2, a2):
        align_yaxis_zero(a1, a2)
    else:
        align_yaxis_midpoint(a1, a2, s1, s2)

# ============================================
# BRAND (header band + footer + watermarks)
# ============================================
def brand_fig(fig, title, subtitle=None, source=None, data_date=None):
    """
    Apply full LHM brand treatment at the figure level:
      - Top: lighthouse icon + LIGHTHOUSE MACRO text + current date + Ocean/Dusk bar
      - Title in header band (y=0.945)
      - Subtitle italic Ocean below title (y=0.895)
      - Bottom: source footer + MACRO, ILLUMINATED + Ocean/Dusk bar
    Call AFTER plotting all data but BEFORE save_fig.
    """
    fig.patch.set_facecolor(THEME['bg'])

    OCEAN = COLORS['ocean']
    DUSK = COLORS['dusk']

    # Top watermark text
    fig.text(0.035, 0.98, 'LIGHTHOUSE MACRO', fontsize=13,
             color=OCEAN, fontweight='bold', va='top')
    fig.text(0.97, 0.98, datetime.now().strftime('%B %d, %Y'),
             fontsize=11, color=THEME['muted'], ha='right', va='top')

    # Top accent bar (Ocean 2/3 + Dusk 1/3)
    bar = fig.add_axes([0.03, 0.955, 0.94, 0.004])
    bar.axhspan(0, 1, 0, 0.67, color=OCEAN)
    bar.axhspan(0, 1, 0.67, 1.0, color=DUSK)
    bar.set_xlim(0, 1); bar.set_ylim(0, 1); bar.axis('off')

    # Lighthouse icon top-left (overlays the brand text area)
    if os.path.exists(ICON_PATH):
        icon_img = mpimg.imread(ICON_PATH)
        icon_w = 0.018
        icon_aspect = icon_img.shape[0] / icon_img.shape[1]
        fig_aspect = fig.get_figwidth() / fig.get_figheight()
        icon_h = icon_w * icon_aspect * fig_aspect
        icon_ax = fig.add_axes([0.012, 0.985 - icon_h, icon_w, icon_h])
        icon_ax.imshow(icon_img, aspect='equal')
        icon_ax.axis('off')

    # Bottom accent bar
    bbar = fig.add_axes([0.03, 0.035, 0.94, 0.004])
    bbar.axhspan(0, 1, 0, 0.67, color=OCEAN)
    bbar.axhspan(0, 1, 0.67, 1.0, color=DUSK)
    bbar.set_xlim(0, 1); bbar.set_ylim(0, 1); bbar.axis('off')

    # MACRO, ILLUMINATED. bottom-right
    fig.text(0.97, 0.025, 'MACRO, ILLUMINATED.', fontsize=13,
             color=OCEAN, ha='right', va='top', style='italic', fontweight='bold')

    # Source footer bottom-left
    if source:
        pull_str = datetime.now().strftime('%m.%d.%Y')
        if data_date is not None:
            if isinstance(data_date, str):
                data_date = pd.Timestamp(data_date)
            data_str = data_date.strftime('%m.%d.%Y')
            fig.text(0.03, 0.022,
                     f'Lighthouse Macro | {source} | Data thru {data_str} | Pulled {pull_str}',
                     fontsize=9, color=THEME['muted'],
                     ha='left', va='top', style='italic')
        else:
            fig.text(0.03, 0.022,
                     f'Lighthouse Macro | {source}; {pull_str}',
                     fontsize=9, color=THEME['muted'],
                     ha='left', va='top', style='italic')

    # Title under the accent bar. Subtitle below with breathing room above
    # the plot area (which starts at y=0.84 via new_fig).
    fig.suptitle(title, fontsize=15, fontweight='bold', y=0.93,
                 color=THEME['fg'])
    if subtitle:
        fig.text(0.5, 0.87, subtitle, fontsize=12, ha='center',
                 color=OCEAN, style='italic')

# ============================================
# SAVE
# ============================================
def _add_border(fig, border_color=None, border_width=4.0):
    """Attach the signature Ocean (or Bright on dark) border to the figure."""
    if border_color is None:
        border_color = COLORS['bright'] if THEME.get('mode') == 'dark' else COLORS['ocean']
    fig.patches.append(plt.Rectangle(
        (0, 0), 1, 1, transform=fig.transFigure,
        fill=False, edgecolor=border_color, linewidth=border_width,
        zorder=100, clip_on=False,
    ))


def save_fig(fig, filepath):
    """Save figure to disk with 4pt brand border. Returns the filepath."""
    _add_border(fig)
    fig.savefig(filepath, dpi=200, bbox_inches='tight', pad_inches=0.025,
                facecolor=THEME['bg'], edgecolor='none')
    plt.close(fig)
    return filepath


def save_fig_buffer(fig, dpi=150):
    """Render figure to an in-memory PNG buffer (BytesIO) so it can be
    base64-embedded in HTML. Same brand border and theme bg as save_fig.

    Returns:
        bytes: raw PNG bytes.
    """
    import io
    _add_border(fig)
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=dpi, bbox_inches='tight',
                pad_inches=0.025, facecolor=THEME['bg'], edgecolor='none')
    plt.close(fig)
    return buf.getvalue()
