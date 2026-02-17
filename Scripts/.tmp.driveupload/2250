"""
LIGHTHOUSE MACRO - Chart Style Library
Official 8-Color System + Institutional Formatting Standards
Target: January 7, 2026 Publication
"""

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.patches import FancyBboxPatch
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter
import numpy as np

# =============================================================================
# OFFICIAL 8-COLOR PALETTE
# =============================================================================

LIGHTHOUSE_COLORS = {
    'ocean_blue': '#0089D1',      # Primary data series, bullish signals
    'dusk_orange': '#FF6723',     # Warning thresholds, secondary emphasis
    'electric_cyan': '#33CCFF',   # Volatility indicators, highlights (bright cerulean)
    'hot_magenta': '#FF2389',     # Critical alerts, extreme stress
    'teal_green': '#00BB99',      # Secondary series, stable metrics
    'neutral_gray': '#D3D6D9',    # Backgrounds, grids, reference
    'lime_green': '#00FF00',      # Extreme bullish/overbought
    'pure_red': '#FF0000'         # Crisis zones, recession signals
}

# Fill variants (30% opacity)
LIGHTHOUSE_FILLS = {
    'ocean_blue_fill': 'rgba(0, 137, 209, 0.3)',
    'dusk_orange_fill': 'rgba(255, 103, 35, 0.3)',
    'stress_zone': 'rgba(255, 0, 0, 0.2)',
    'expansion_zone': 'rgba(0, 255, 0, 0.2)',
    'neutral_zone': 'rgba(211, 214, 217, 0.3)'
}

# Hex fills for matplotlib
LIGHTHOUSE_FILLS_HEX = {
    'ocean_blue_fill': '#0089D14D',
    'dusk_orange_fill': '#FF67234D',
    'stress_zone': '#FF000033',
    'expansion_zone': '#00FF0033',
    'neutral_zone': '#D3D6D94D',
    'light_blue_bg': '#E6F4FB',
    'light_red_bg': '#FFEBEE',
    'light_green_bg': '#E8F5E9'
}


def hex_to_rgba(hex_color, alpha=0.3):
    """Convert hex color to rgba with specified alpha"""
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16) / 255
    g = int(hex_color[2:4], 16) / 255
    b = int(hex_color[4:6], 16) / 255
    return (r, g, b, alpha)


# =============================================================================
# CHART STYLING FUNCTIONS
# =============================================================================

def apply_lighthouse_style(ax, title, subtitle=None, show_branding=True,
                          four_spine=True, primary_side='right'):
    """
    Apply standard Lighthouse Macro styling to axes

    INSTITUTIONAL STANDARD: 4 visible spines, RHS is primary axis

    Parameters:
    -----------
    ax : matplotlib axes
    title : str - Chart title
    subtitle : str - Optional subtitle/tagline
    show_branding : bool - Whether to show LHM branding
    four_spine : bool - If True, show all 4 spines (institutional standard)
    primary_side : str - 'right' (institutional default) or 'left'
    """
    # Remove gridlines (clean institutional look)
    ax.grid(False)

    # INSTITUTIONAL STANDARD: All 4 spines visible
    if four_spine:
        ax.spines['top'].set_visible(True)
        ax.spines['right'].set_visible(True)
        ax.spines['left'].set_visible(True)
        ax.spines['bottom'].set_visible(True)

        # Spine styling - subtle but present
        for spine in ['top', 'right', 'left', 'bottom']:
            ax.spines[spine].set_linewidth(0.5)
            ax.spines[spine].set_color('#666666')

        # Primary axis on RHS (institutional convention)
        if primary_side == 'right':
            ax.yaxis.set_label_position('right')
            ax.yaxis.tick_right()
    else:
        # Legacy 2-spine mode (deprecated)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_linewidth(0.5)
        ax.spines['left'].set_color('#666666')
        ax.spines['bottom'].set_linewidth(0.5)
        ax.spines['bottom'].set_color('#666666')

    # Title styling
    ax.set_title(title, fontsize=14, fontweight='bold', loc='center', pad=20)

    if subtitle:
        ax.text(0.5, 1.02, subtitle, transform=ax.transAxes,
                fontsize=10, ha='center', style='italic',
                color='#666666')

    if show_branding:
        # Top-left branding
        ax.text(0.01, 1.06, 'LIGHTHOUSE MACRO',
                transform=ax.transAxes, fontsize=8,
                color=LIGHTHOUSE_COLORS['ocean_blue'],
                fontweight='bold')

        # Bottom-right tagline
        ax.text(0.99, -0.08, 'MACRO, ILLUMINATED.',
                transform=ax.transAxes, fontsize=7,
                color=LIGHTHOUSE_COLORS['hot_magenta'],
                ha='right', style='italic')

    return ax


def apply_lighthouse_style_fig(fig, title, subtitle=None):
    """
    Apply Lighthouse styling at figure level for multi-panel charts
    """
    # Main title
    fig.suptitle(title, fontsize=16, fontweight='bold', y=0.98)

    if subtitle:
        fig.text(0.5, 0.94, subtitle, ha='center', fontsize=10,
                 style='italic', color='#666666')

    # Branding
    fig.text(0.01, 0.99, 'LIGHTHOUSE MACRO', fontsize=8,
             color=LIGHTHOUSE_COLORS['ocean_blue'], fontweight='bold',
             va='top')

    fig.text(0.99, 0.01, 'MACRO, ILLUMINATED.', fontsize=7,
             color=LIGHTHOUSE_COLORS['hot_magenta'], ha='right',
             style='italic')

    return fig


def add_threshold_line(ax, y_value, label, color='red', linestyle='--',
                       linewidth=1, alpha=0.8, label_side='right'):
    """
    Add horizontal threshold line with label

    Parameters:
    -----------
    ax : matplotlib axes
    y_value : float - Y position of threshold
    label : str - Label text
    color : str - Line color
    linestyle : str - Line style
    label_side : str - 'right' or 'left' for label position
    """
    ax.axhline(y=y_value, color=color, linestyle=linestyle,
               linewidth=linewidth, alpha=alpha, zorder=1)

    xlim = ax.get_xlim()
    if label_side == 'right':
        x_pos = xlim[1]
        ha = 'left'
        label_text = f' {label}'
    else:
        x_pos = xlim[0]
        ha = 'right'
        label_text = f'{label} '

    ax.text(x_pos, y_value, label_text, va='center', ha=ha,
            fontsize=8, color=color, fontweight='bold')


def add_callout_box(ax, text, position, boxstyle='round',
                    facecolor='white', edgecolor=None, fontsize=8):
    """
    Add annotation box with key insights

    Parameters:
    -----------
    ax : matplotlib axes
    text : str - Box content
    position : tuple - (x, y) in axes coordinates
    boxstyle : str - Box style
    """
    if edgecolor is None:
        edgecolor = LIGHTHOUSE_COLORS['dusk_orange']

    props = dict(boxstyle=boxstyle, facecolor=facecolor,
                 edgecolor=edgecolor, alpha=0.95, linewidth=1.5)

    ax.text(position[0], position[1], text,
            transform=ax.transAxes, fontsize=fontsize,
            verticalalignment='top', bbox=props,
            family='monospace')


def add_last_value_label(ax, y_value, color, label_format='{:.2f}', side='right',
                         fontsize=9, padding=0.02):
    """
    Add TradingView-style last value label anchored to axis.

    Solid color box matching data line with bold white text.

    Parameters:
    -----------
    ax : matplotlib axes
    y_value : float - The last value to display
    color : str - Color matching the data series (box fill color)
    label_format : str - Format string for the value
    side : str - 'right' or 'left' axis
    fontsize : int - Font size for label
    padding : float - Padding from axis edge in axes coordinates
    """
    # Format the value
    label_text = label_format.format(y_value)

    # Position on the axis edge
    if side == 'right':
        x_pos = 1.0 + padding
        ha = 'left'
    else:
        x_pos = -padding
        ha = 'right'

    # Transform y_value to axes coordinates
    ylim = ax.get_ylim()
    y_norm = (y_value - ylim[0]) / (ylim[1] - ylim[0])

    # Clamp to visible range
    y_norm = max(0.02, min(0.98, y_norm))

    # Create solid box with white bold text
    bbox_props = dict(
        boxstyle='round,pad=0.3',
        facecolor=color,
        edgecolor=color,
        alpha=1.0,
        linewidth=0
    )

    ax.text(x_pos, y_norm, label_text,
            transform=ax.transAxes,
            fontsize=fontsize,
            fontweight='bold',
            color='white',
            ha=ha,
            va='center',
            bbox=bbox_props,
            zorder=100,
            clip_on=False)


def add_series_with_label(ax, x, y, label, color, linewidth=2, linestyle='-',
                          show_last_value=True, value_format='{:.2f}',
                          value_side='right', fill=False, fill_alpha=0.15):
    """
    Plot a data series with proper label and optional last-value axis label.

    TradingView style: every series labeled, last value shown on axis.

    Parameters:
    -----------
    ax : matplotlib axes
    x : array-like - X values (dates)
    y : array-like - Y values
    label : str - Series label for legend
    color : str - Line color
    linewidth : float - Line width
    linestyle : str - Line style
    show_last_value : bool - Show last value label on axis
    value_format : str - Format string for last value
    value_side : str - 'right' or 'left' for value label
    fill : bool - Fill area under line
    fill_alpha : float - Fill transparency

    Returns:
    --------
    line : matplotlib line object
    """
    # Plot the line
    line, = ax.plot(x, y, color=color, linewidth=linewidth, linestyle=linestyle,
                    label=label, zorder=3)

    # Optional fill
    if fill:
        ax.fill_between(x, y, alpha=fill_alpha, color=color, zorder=1)

    # Add last value label on axis
    if show_last_value and len(y) > 0:
        # Get last non-NaN value
        y_arr = np.array(y)
        valid_mask = ~np.isnan(y_arr)
        if valid_mask.any():
            last_val = y_arr[valid_mask][-1]
            add_last_value_label(ax, last_val, color, value_format, value_side)

    return line


def create_tradingview_dual_axis(dates, series_left, series_right, title,
                                  labels_left, labels_right,
                                  colors_left=None, colors_right=None,
                                  ylabel_left='', ylabel_right='',
                                  value_formats_left=None, value_formats_right=None):
    """
    Create TradingView-style chart with dual axes, all series labeled,
    and last values shown on respective axes.

    Parameters:
    -----------
    dates : array-like - Date values
    series_left : list of arrays - Data series for left axis
    series_right : list of arrays - Data series for right axis
    title : str - Chart title
    labels_left : list of str - Labels for left axis series
    labels_right : list of str - Labels for right axis series
    colors_left : list of str - Colors for left series (optional)
    colors_right : list of str - Colors for right series (optional)
    ylabel_left, ylabel_right : str - Axis labels
    value_formats_left, value_formats_right : list of str - Format strings

    Returns:
    --------
    fig, (ax_left, ax_right)
    """
    fig, ax_left = create_figure()
    ax_right = ax_left.twinx()

    # Default colors
    default_colors_left = [LIGHTHOUSE_COLORS['dusk_orange'], LIGHTHOUSE_COLORS['teal_green'],
                           LIGHTHOUSE_COLORS['neutral_gray']]
    default_colors_right = [LIGHTHOUSE_COLORS['ocean_blue'], LIGHTHOUSE_COLORS['hot_magenta'],
                            LIGHTHOUSE_COLORS['electric_cyan']]

    if colors_left is None:
        colors_left = default_colors_left
    if colors_right is None:
        colors_right = default_colors_right

    # Default formats
    if value_formats_left is None:
        value_formats_left = ['{:.2f}'] * len(series_left)
    if value_formats_right is None:
        value_formats_right = ['{:.2f}'] * len(series_right)

    # Plot left axis series
    for i, (y, label) in enumerate(zip(series_left, labels_left)):
        color = colors_left[i % len(colors_left)]
        fmt = value_formats_left[i] if i < len(value_formats_left) else '{:.2f}'
        add_series_with_label(ax_left, dates, y, label, color,
                              linewidth=1.5, show_last_value=True,
                              value_format=fmt, value_side='left')

    # Plot right axis series (primary)
    for i, (y, label) in enumerate(zip(series_right, labels_right)):
        color = colors_right[i % len(colors_right)]
        fmt = value_formats_right[i] if i < len(value_formats_right) else '{:.2f}'
        add_series_with_label(ax_right, dates, y, label, color,
                              linewidth=2.5, show_last_value=True,
                              value_format=fmt, value_side='right',
                              fill=(i == 0))  # Fill primary series

    # Style both axes - 4 spines visible
    for spine in ['top', 'bottom', 'left', 'right']:
        ax_left.spines[spine].set_visible(True)
        ax_left.spines[spine].set_linewidth(0.5)
        ax_left.spines[spine].set_color('#666666')

    ax_left.grid(False)
    ax_right.grid(False)

    # Axis labels
    ax_left.set_ylabel(ylabel_left, fontsize=10)
    ax_right.set_ylabel(ylabel_right, fontsize=10, fontweight='bold')

    # Color axis labels to match primary series
    if colors_left:
        ax_left.tick_params(axis='y', labelcolor=colors_left[0])
    if colors_right:
        ax_right.tick_params(axis='y', labelcolor=colors_right[0])

    # Title and branding
    ax_left.set_title(title, fontsize=14, fontweight='bold', loc='center', pad=20)
    ax_left.text(0.01, 1.06, 'LIGHTHOUSE MACRO',
                 transform=ax_left.transAxes, fontsize=8,
                 color=LIGHTHOUSE_COLORS['ocean_blue'], fontweight='bold')
    ax_left.text(0.99, -0.08, 'MACRO, ILLUMINATED.',
                 transform=ax_left.transAxes, fontsize=7,
                 color=LIGHTHOUSE_COLORS['hot_magenta'],
                 ha='right', style='italic')

    # Combined legend
    lines_l, labels_l = ax_left.get_legend_handles_labels()
    lines_r, labels_r = ax_right.get_legend_handles_labels()
    ax_left.legend(lines_l + lines_r, labels_l + labels_r,
                   loc='upper left', framealpha=0.95, edgecolor='#666666')

    return fig, (ax_left, ax_right)


def add_zone_shading(ax, y_min, y_max, color, alpha=0.2, label=None):
    """
    Add background zone shading

    Parameters:
    -----------
    ax : matplotlib axes
    y_min, y_max : float - Y range for shading
    color : str - Fill color
    alpha : float - Transparency
    label : str - Optional zone label
    """
    ax.axhspan(y_min, y_max, color=color, alpha=alpha, zorder=0)

    if label:
        xlim = ax.get_xlim()
        ax.text(xlim[0], (y_min + y_max) / 2, f' {label}',
                fontsize=7, color=color, alpha=0.8, va='center')


def add_vertical_zone(ax, x_min, x_max, color, alpha=0.15, label=None):
    """
    Add vertical zone shading (for recession bars, events, etc.)
    """
    ax.axvspan(x_min, x_max, color=color, alpha=alpha, zorder=0)

    if label:
        ylim = ax.get_ylim()
        mid_x = x_min + (x_max - x_min) / 2
        ax.text(mid_x, ylim[1], label, fontsize=7, color=color,
                ha='center', va='bottom', rotation=90)


def add_current_marker(ax, x, y, label, color=None, marker='o', size=80):
    """
    Add highlighted marker for current/latest data point
    """
    if color is None:
        color = LIGHTHOUSE_COLORS['hot_magenta']

    ax.scatter([x], [y], c=color, s=size, zorder=5, marker=marker)
    ax.annotate(label, (x, y), xytext=(10, 10),
                textcoords='offset points', fontsize=8,
                color=color, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                         edgecolor=color, alpha=0.9))


def format_axis_percent(ax, axis='y', decimals=1):
    """Format axis as percentage"""
    formatter = FuncFormatter(lambda x, p: f'{x:.{decimals}f}%')
    if axis == 'y':
        ax.yaxis.set_major_formatter(formatter)
    else:
        ax.xaxis.set_major_formatter(formatter)


def format_axis_billions(ax, axis='y', already_in_billions=True):
    """Format axis in billions with $

    Args:
        ax: matplotlib axes
        axis: 'x' or 'y'
        already_in_billions: if True, values are already in billions (e.g., 2800 = $2,800B)
                           if False, values are raw (e.g., 2800000000000)
    """
    if already_in_billions:
        # Data is already in billions, just add formatting
        formatter = FuncFormatter(lambda x, p: f'${x:,.0f}B' if x >= 1 else f'${x*1000:.0f}M')
    else:
        # Data is raw, divide by 1e9
        formatter = FuncFormatter(lambda x, p: f'${x/1e9:.1f}B' if x >= 1e9 else f'${x/1e6:.0f}M')
    if axis == 'y':
        ax.yaxis.set_major_formatter(formatter)
    else:
        ax.xaxis.set_major_formatter(formatter)


def format_axis_trillions(ax, axis='y'):
    """Format axis in trillions with $"""
    formatter = FuncFormatter(lambda x, p: f'${x:.1f}T')
    if axis == 'y':
        ax.yaxis.set_major_formatter(formatter)
    else:
        ax.xaxis.set_major_formatter(formatter)


def setup_date_axis(ax, date_format='%Y-%m', rotation=45):
    """Configure date axis formatting"""
    ax.xaxis.set_major_formatter(mdates.DateFormatter(date_format))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=rotation, ha='right')


def create_figure(figsize=(12, 7), dpi=150):
    """Create figure with standard Lighthouse settings"""
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')
    return fig, ax


def create_dual_panel(figsize=(12, 10), height_ratios=[2, 1], dpi=150):
    """Create dual-panel figure (common for impulse charts)"""
    fig, axes = plt.subplots(2, 1, figsize=figsize, dpi=dpi,
                             gridspec_kw={'height_ratios': height_ratios,
                                         'hspace': 0.15})
    fig.patch.set_facecolor('white')
    for ax in axes:
        ax.set_facecolor('white')
    return fig, axes


def create_multi_panel(rows, cols, figsize=None, dpi=150):
    """Create multi-panel figure"""
    if figsize is None:
        figsize = (5 * cols, 4 * rows)

    fig, axes = plt.subplots(rows, cols, figsize=figsize, dpi=dpi)
    fig.patch.set_facecolor('white')

    if rows == 1 and cols == 1:
        axes = np.array([[axes]])
    elif rows == 1:
        axes = axes.reshape(1, -1)
    elif cols == 1:
        axes = axes.reshape(-1, 1)

    for ax_row in axes:
        for ax in ax_row:
            ax.set_facecolor('white')

    return fig, axes


def save_chart(fig, filename, output_dir=None, tight=True):
    """Save chart with standard settings"""
    import os

    if output_dir:
        filepath = os.path.join(output_dir, filename)
    else:
        filepath = filename

    if tight:
        fig.tight_layout()

    fig.savefig(filepath, dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close(fig)

    return filepath


# =============================================================================
# SPECIALIZED CHART TEMPLATES
# =============================================================================

def create_time_series_chart(dates, values, title, ylabel,
                             color=None, fill=True, ma_period=None,
                             primary_side='right'):
    """
    Create standard time series chart

    INSTITUTIONAL STANDARD: 4 spines, RHS is primary axis

    Parameters:
    -----------
    dates : array-like - Date values
    values : array-like - Data values
    title : str - Chart title
    ylabel : str - Y-axis label
    color : str - Line color (default: ocean_blue)
    fill : bool - Whether to fill area under line
    ma_period : int - Moving average period (optional)
    primary_side : str - 'right' (institutional default) or 'left'

    Returns:
    --------
    fig, ax
    """
    if color is None:
        color = LIGHTHOUSE_COLORS['ocean_blue']

    fig, ax = create_figure()

    # Main line
    ax.plot(dates, values, color=color, linewidth=2, label='Value')

    if fill:
        ax.fill_between(dates, values, alpha=0.2, color=color)

    if ma_period:
        ma = np.convolve(values, np.ones(ma_period)/ma_period, mode='valid')
        ma_dates = dates[ma_period-1:]
        ax.plot(ma_dates, ma, color=LIGHTHOUSE_COLORS['hot_magenta'],
                linewidth=1.5, linestyle='-', label=f'{ma_period}-Day MA')

    ax.set_ylabel(ylabel)
    ax.set_xlabel('Date')
    apply_lighthouse_style(ax, title, primary_side=primary_side)

    return fig, ax


def create_dual_axis_chart(dates, values1, values2, title,
                           label1, label2, ylabel1, ylabel2,
                           color1=None, color2=None,
                           primary_on_right=True):
    """
    Create dual-axis time series chart

    INSTITUTIONAL STANDARD:
    - RHS is PRIMARY axis (main data series)
    - LHS is OVERLAY axis (secondary/comparison series)
    - All 4 spines visible

    Parameters:
    -----------
    dates : array-like - Date values
    values1 : array-like - PRIMARY data (plotted on RHS by default)
    values2 : array-like - OVERLAY data (plotted on LHS by default)
    title : str - Chart title
    label1, label2 : str - Legend labels
    ylabel1, ylabel2 : str - Y-axis labels
    color1, color2 : str - Line colors
    primary_on_right : bool - If True (default), values1 on RHS; if False, values1 on LHS
    """
    if color1 is None:
        color1 = LIGHTHOUSE_COLORS['ocean_blue']
    if color2 is None:
        color2 = LIGHTHOUSE_COLORS['dusk_orange']

    fig, ax_left = create_figure()

    # All 4 spines visible (institutional standard)
    for spine in ['top', 'right', 'left', 'bottom']:
        ax_left.spines[spine].set_visible(True)
        ax_left.spines[spine].set_linewidth(0.5)
        ax_left.spines[spine].set_color('#666666')

    ax_left.grid(False)

    # Create right axis
    ax_right = ax_left.twinx()

    if primary_on_right:
        # PRIMARY on RHS, OVERLAY on LHS (institutional default)
        ax_primary, ax_overlay = ax_right, ax_left
        primary_color, overlay_color = color1, color2
        primary_values, overlay_values = values1, values2
        primary_label, overlay_label = label1, label2
        primary_ylabel, overlay_ylabel = ylabel1, ylabel2
    else:
        # Reversed: PRIMARY on LHS, OVERLAY on RHS
        ax_primary, ax_overlay = ax_left, ax_right
        primary_color, overlay_color = color1, color2
        primary_values, overlay_values = values1, values2
        primary_label, overlay_label = label1, label2
        primary_ylabel, overlay_ylabel = ylabel1, ylabel2

    # PRIMARY axis (RHS by default) - main data with fill
    ax_primary.plot(dates, primary_values, color=primary_color, linewidth=2.5, label=primary_label, zorder=3)
    ax_primary.fill_between(dates, primary_values, alpha=0.2, color=primary_color, zorder=2)
    ax_primary.set_ylabel(primary_ylabel, color=primary_color, fontweight='bold')
    ax_primary.tick_params(axis='y', labelcolor=primary_color)

    # OVERLAY axis (LHS by default) - comparison line only
    ax_overlay.plot(dates, overlay_values, color=overlay_color, linewidth=1.5, label=overlay_label, linestyle='-', alpha=0.8, zorder=1)
    ax_overlay.set_ylabel(overlay_ylabel, color=overlay_color)
    ax_overlay.tick_params(axis='y', labelcolor=overlay_color)

    ax_left.set_xlabel('Date')

    # Title and branding (no spine manipulation - already set)
    ax_left.set_title(title, fontsize=14, fontweight='bold', loc='center', pad=20)

    # Branding
    ax_left.text(0.01, 1.06, 'LIGHTHOUSE MACRO',
                transform=ax_left.transAxes, fontsize=8,
                color=LIGHTHOUSE_COLORS['ocean_blue'],
                fontweight='bold')
    ax_left.text(0.99, -0.08, 'MACRO, ILLUMINATED.',
                transform=ax_left.transAxes, fontsize=7,
                color=LIGHTHOUSE_COLORS['hot_magenta'],
                ha='right', style='italic')

    # Combined legend (upper left, out of the way of data)
    lines1, labels1 = ax_primary.get_legend_handles_labels()
    lines2, labels2 = ax_overlay.get_legend_handles_labels()
    ax_left.legend(lines1 + lines2, labels1 + labels2, loc='upper left',
                   framealpha=0.9, edgecolor='#666666')

    return fig, (ax_left, ax_right)


def create_spread_chart(dates, spread, title, threshold=None,
                        threshold_label=None, ma_period=20):
    """
    Create spread chart with threshold and MA overlay
    """
    fig, ax = create_figure()

    # Bar chart for spread
    colors = [LIGHTHOUSE_COLORS['ocean_blue'] if s >= 0
              else LIGHTHOUSE_COLORS['pure_red'] for s in spread]
    ax.bar(dates, spread, color=colors, alpha=0.6, width=1)

    # Moving average
    if ma_period and len(spread) >= ma_period:
        ma = np.convolve(spread, np.ones(ma_period)/ma_period, mode='valid')
        ma_dates = dates[ma_period-1:]
        ax.plot(ma_dates, ma, color=LIGHTHOUSE_COLORS['hot_magenta'],
                linewidth=2, label=f'{ma_period}-Day MA')

    # Threshold line
    if threshold is not None:
        add_threshold_line(ax, threshold, threshold_label or f'{threshold}',
                          color=LIGHTHOUSE_COLORS['pure_red'])

    # Zero line
    ax.axhline(y=0, color='black', linewidth=0.5)

    ax.set_ylabel('Spread (bps)')
    ax.set_xlabel('Date')
    apply_lighthouse_style(ax, title)

    if ma_period:
        ax.legend(loc='upper left')

    return fig, ax


def create_histogram_with_current(data, current_value, title, xlabel,
                                  bins=50, percentile_label=True):
    """
    Create histogram with current value marker
    """
    fig, ax = create_figure(figsize=(10, 6))

    # Calculate percentile
    percentile = (data < current_value).sum() / len(data) * 100

    # Histogram
    n, bins_edges, patches = ax.hist(data, bins=bins,
                                      color=LIGHTHOUSE_COLORS['ocean_blue'],
                                      alpha=0.7, edgecolor='white')

    # Color bins below current differently
    for i, patch in enumerate(patches):
        if bins_edges[i] < current_value:
            patch.set_facecolor(LIGHTHOUSE_COLORS['teal_green'])
        else:
            patch.set_facecolor(LIGHTHOUSE_COLORS['pure_red'])
            patch.set_alpha(0.5)

    # Current value line
    ax.axvline(x=current_value, color=LIGHTHOUSE_COLORS['hot_magenta'],
               linewidth=2, linestyle='-', label=f'Current: {current_value:.0f}')

    # Mean line
    mean_val = np.mean(data)
    ax.axvline(x=mean_val, color='black', linewidth=1, linestyle='--',
               label=f'Mean: {mean_val:.0f}')

    if percentile_label:
        ax.text(0.95, 0.95, f'Current: {percentile:.0f}th Percentile',
                transform=ax.transAxes, fontsize=10, fontweight='bold',
                ha='right', va='top', color=LIGHTHOUSE_COLORS['hot_magenta'])

    ax.set_xlabel(xlabel)
    ax.set_ylabel('Frequency')
    ax.legend(loc='upper right')
    apply_lighthouse_style(ax, title)

    return fig, ax


# =============================================================================
# DATA SOURCE HELPERS
# =============================================================================

def get_fred_series_info():
    """
    Return dictionary of FRED series used in Lighthouse charts
    """
    return {
        # Funding rates
        'SOFR': 'Secured Overnight Financing Rate',
        'EFFR': 'Effective Federal Funds Rate',
        'IORB': 'Interest Rate on Reserve Balances',

        # Fed balance sheet
        'RRPONTSYD': 'Overnight Reverse Repurchase Agreements',
        'WRESBAL': 'Reserve Balances with Federal Reserve Banks',
        'WTREGEN': 'Treasury General Account',
        'WALCL': 'Fed Total Assets',
        'TREAST': 'Fed Treasury Holdings',
        'WSHOMCB': 'Fed MBS Holdings',

        # Treasury yields
        'DGS3MO': '3-Month Treasury',
        'DGS6MO': '6-Month Treasury',
        'DGS1': '1-Year Treasury',
        'DGS2': '2-Year Treasury',
        'DGS5': '5-Year Treasury',
        'DGS10': '10-Year Treasury',
        'DGS30': '30-Year Treasury',

        # Credit spreads
        'BAMLC0A1CAAAEY': 'AAA OAS',
        'BAMLC0A4CBBBEY': 'BBB OAS',
        'BAMLH0A0HYM2EY': 'HY OAS',

        # Labor
        'ICSA': 'Initial Claims',
        'CCSA': 'Continuing Claims',
        'JTSQUR': 'Quits Rate',
        'JTSHIR': 'Hires Rate',
        'LNS13025703': 'Long-term Unemployment',
        'PAYEMS': 'Total Nonfarm Payrolls',

        # Consumer
        'TOTALSL': 'Consumer Credit Outstanding',
        'PSAVERT': 'Personal Savings Rate',
        'DRCCLACBS': 'Credit Card Delinquency Rate',

        # GDP
        'GDPC1': 'Real GDP',
        'GDPDEF': 'GDP Deflator',
        'GDP': 'Nominal GDP',

        # Debt
        'GFDEBTN': 'Federal Debt Outstanding',
        'GFDEGDQ188S': 'Federal Debt to GDP'
    }


# =============================================================================
# CHART METADATA
# =============================================================================

# =============================================================================
# CHART QA VALIDATION SYSTEM
# =============================================================================

class ChartQAValidator:
    """
    Validates charts against Lighthouse Macro institutional standards.

    Standards:
    - 4 visible spines (top, bottom, left, right)
    - RHS is primary y-axis
    - No overlapping annotations
    - All data series have labels
    - Title and branding present
    """

    def __init__(self, ax, fig=None):
        self.ax = ax
        self.fig = fig or ax.get_figure()
        self.issues = []
        self.warnings = []

    def validate_all(self):
        """Run all validation checks"""
        self.check_spines()
        self.check_axis_labels()
        self.check_title()
        self.check_data_presence()
        self.check_annotation_overlap()
        self.check_branding()
        return self.get_report()

    def check_spines(self):
        """Verify all 4 spines are visible"""
        for spine_name in ['top', 'bottom', 'left', 'right']:
            spine = self.ax.spines[spine_name]
            if not spine.get_visible():
                self.issues.append(f"SPINE_HIDDEN: {spine_name} spine not visible (institutional standard: all 4 visible)")

    def check_axis_labels(self):
        """Verify y-axis label exists"""
        ylabel = self.ax.get_ylabel()
        if not ylabel or ylabel.strip() == '':
            self.issues.append("MISSING_YLABEL: No y-axis label present")

        xlabel = self.ax.get_xlabel()
        if not xlabel or xlabel.strip() == '':
            self.warnings.append("MISSING_XLABEL: No x-axis label (may be intentional for date axes)")

    def check_title(self):
        """Verify chart has title"""
        title = self.ax.get_title()
        if not title or title.strip() == '':
            self.issues.append("MISSING_TITLE: Chart has no title")

    def check_data_presence(self):
        """Verify chart has data plotted"""
        has_lines = len(self.ax.get_lines()) > 0
        has_collections = len(self.ax.collections) > 0
        has_patches = len(self.ax.patches) > 0

        if not (has_lines or has_collections or has_patches):
            self.issues.append("NO_DATA: Chart appears to have no data plotted")

    def check_annotation_overlap(self):
        """Check for potentially overlapping text annotations"""
        texts = self.ax.texts
        if len(texts) > 1:
            # Get bounding boxes in display coordinates
            renderer = self.fig.canvas.get_renderer() if hasattr(self.fig.canvas, 'get_renderer') else None
            if renderer:
                bboxes = []
                for text in texts:
                    try:
                        bbox = text.get_window_extent(renderer=renderer)
                        bboxes.append((text.get_text()[:20], bbox))
                    except:
                        pass

                # Check for overlaps
                for i, (text1, bbox1) in enumerate(bboxes):
                    for j, (text2, bbox2) in enumerate(bboxes[i+1:], i+1):
                        if bbox1.overlaps(bbox2):
                            self.warnings.append(f"ANNOTATION_OVERLAP: '{text1}...' may overlap with '{text2}...'")

    def check_branding(self):
        """Check for Lighthouse branding elements"""
        texts = [t.get_text() for t in self.ax.texts]
        has_lhm = any('LIGHTHOUSE' in t.upper() for t in texts)
        has_tagline = any('ILLUMINATED' in t.upper() for t in texts)

        if not has_lhm:
            self.warnings.append("MISSING_BRANDING: 'LIGHTHOUSE MACRO' watermark not found")
        if not has_tagline:
            self.warnings.append("MISSING_TAGLINE: 'MACRO, ILLUMINATED.' not found")

    def get_report(self):
        """Generate validation report"""
        return {
            'passed': len(self.issues) == 0,
            'issues': self.issues,
            'warnings': self.warnings,
            'issue_count': len(self.issues),
            'warning_count': len(self.warnings)
        }

    def print_report(self):
        """Print formatted validation report"""
        report = self.get_report()
        status = "PASS" if report['passed'] else "FAIL"
        print(f"\n{'='*60}")
        print(f"CHART QA VALIDATION: {status}")
        print(f"{'='*60}")

        if report['issues']:
            print("\nISSUES (must fix):")
            for issue in report['issues']:
                print(f"  [X] {issue}")

        if report['warnings']:
            print("\nWARNINGS (review):")
            for warning in report['warnings']:
                print(f"  [!] {warning}")

        if report['passed'] and not report['warnings']:
            print("\n  All checks passed. Chart meets institutional standards.")

        print(f"\nSummary: {report['issue_count']} issues, {report['warning_count']} warnings")
        return report


def validate_chart(ax, fig=None, print_report=True):
    """
    Convenience function to validate a chart against institutional standards.

    Usage:
        fig, ax = create_figure()
        # ... build chart ...
        report = validate_chart(ax)
    """
    validator = ChartQAValidator(ax, fig)
    if print_report:
        return validator.print_report()
    return validator.validate_all()


def batch_validate_charts(axes_list, names=None):
    """
    Validate multiple charts and return summary.

    Parameters:
    -----------
    axes_list : list of matplotlib axes
    names : list of str - Optional chart names/IDs

    Returns:
    --------
    dict with summary stats and per-chart results
    """
    results = []
    total_issues = 0
    total_warnings = 0

    for i, ax in enumerate(axes_list):
        name = names[i] if names else f"Chart_{i+1}"
        validator = ChartQAValidator(ax)
        report = validator.validate_all()
        report['name'] = name
        results.append(report)
        total_issues += report['issue_count']
        total_warnings += report['warning_count']

    passed = sum(1 for r in results if r['passed'])

    return {
        'total_charts': len(axes_list),
        'passed': passed,
        'failed': len(axes_list) - passed,
        'total_issues': total_issues,
        'total_warnings': total_warnings,
        'results': results
    }


CHART_REGISTRY = {
    # Part I - Macro Dynamics
    'S1_01': {'title': 'Foreign Official Treasury Holdings', 'tier': 3, 'freq': 'monthly'},
    'S1_02': {'title': 'Federal Interest Expense', 'tier': 3, 'freq': 'quarterly'},
    'S1_03': {'title': 'Wealth Share Distribution', 'tier': 3, 'freq': 'quarterly'},
    'S1_06': {'title': 'Primary Dealer Balance Sheet', 'tier': 2, 'freq': 'weekly'},
    'S1_08': {'title': 'Credit Impulse', 'tier': 2, 'freq': 'monthly'},
    'S1_09': {'title': 'Real vs Nominal GDP', 'tier': 3, 'freq': 'quarterly'},
    'S1_15': {'title': 'Cross-Asset Correlations', 'tier': 1, 'freq': 'daily'},
    'S1_16': {'title': 'Treasury Yield Curve Shape', 'tier': 1, 'freq': 'daily'},

    # Part II - Monetary Mechanics
    'S2_01': {'title': 'Excess Savings Depletion', 'tier': 2, 'freq': 'quarterly'},
    'S2_02': {'title': 'Yield Curve Evolution Heatmap', 'tier': 2, 'freq': 'daily'},
    'S2_03': {'title': 'Primary Dealer Balance Sheet', 'tier': 2, 'freq': 'weekly'},
    'S2_04': {'title': 'Bank Reserves vs GDP', 'tier': 1, 'freq': 'weekly'},
    'S2_05': {'title': 'Employment Diffusion Index', 'tier': 2, 'freq': 'monthly'},
    'S2_06': {'title': 'Auction Tails Scatter', 'tier': 1, 'freq': 'per_auction'},
    'S2_07': {'title': 'Credit Spread Percentiles', 'tier': 1, 'freq': 'daily'},
    'S2_08': {'title': 'Two-Speed Consumer', 'tier': 2, 'freq': 'quarterly'},
    'S2_10': {'title': 'Standing Repo Facility Usage', 'tier': 1, 'freq': 'daily'},
    'S2_11': {'title': 'Foreign Treasury Holdings', 'tier': 3, 'freq': 'monthly'},
    'S2_13': {'title': 'Fiscal Dominance Cascade', 'tier': 4, 'freq': 'static'},
    'S2_14': {'title': 'Critical Event Calendar', 'tier': 4, 'freq': 'static'},
    'S2_15': {'title': 'Repo Rate Dispersion', 'tier': 1, 'freq': 'daily'},
    'S2_16': {'title': 'SOFR-EFFR Spread', 'tier': 1, 'freq': 'daily'},
    'S2_17': {'title': '10-Year Yield Scenario', 'tier': 4, 'freq': 'projection'},
    'S2_18': {'title': 'Auction Tails Time Series', 'tier': 1, 'freq': 'per_auction'},
    'S2_19': {'title': 'Treasury Basis Dynamics', 'tier': 1, 'freq': 'daily'},
    'S2_20': {'title': 'Federal Debt Trajectory', 'tier': 3, 'freq': 'quarterly'},
    'S2_21': {'title': 'Federal Interest Expense', 'tier': 3, 'freq': 'quarterly'},
    'S2_23': {'title': 'Subprime Auto Delinquencies', 'tier': 2, 'freq': 'quarterly'},
    'S2_24': {'title': 'CRE Office Delinquencies', 'tier': 2, 'freq': 'monthly'},
    'S2_27': {'title': 'Auction Tails Deviation', 'tier': 1, 'freq': 'per_auction'},
    'S2_28': {'title': 'Treasury Yield Curve Repricing', 'tier': 1, 'freq': 'daily'},
    'S2_31': {'title': 'Treasury Issuance by Tenor', 'tier': 3, 'freq': 'quarterly'},
    'S2_32': {'title': 'Treasury Maturity Wall', 'tier': 4, 'freq': 'projection'},
    'S2_33': {'title': 'CRE Delinquencies Multi', 'tier': 2, 'freq': 'monthly'},
    'S2_36': {'title': 'Labor Fragility Index', 'tier': 2, 'freq': 'monthly'},
}


if __name__ == '__main__':
    # Test the style system
    import numpy as np

    # Generate test data
    dates = np.arange('2024-01', '2026-02', dtype='datetime64[M]')
    values = np.cumsum(np.random.randn(len(dates))) + 100

    # Test time series chart
    fig, ax = create_time_series_chart(
        dates, values,
        title='Test Chart: Lighthouse Style',
        ylabel='Value',
        ma_period=3
    )

    add_threshold_line(ax, 102, 'Warning Level',
                       color=LIGHTHOUSE_COLORS['dusk_orange'])
    add_zone_shading(ax, 95, 98, LIGHTHOUSE_COLORS['pure_red'],
                     alpha=0.1, label='Stress Zone')

    plt.tight_layout()
    plt.show()
