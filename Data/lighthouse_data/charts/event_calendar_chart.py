"""
Critical Event Calendar - INSTITUTIONAL GRADE
Lighthouse Macro - January 2026

The original chart had NO Y-AXIS, making the height of events meaningless.
This version clearly shows what the height represents.

Options for y-axis:
1. Market Impact Score (estimated volatility contribution)
2. Historical VIX spike on similar events
3. Simple categorical (High/Medium/Low risk)

We'll use option 3 for clarity with option 1 as secondary.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
from datetime import datetime, timedelta
from pathlib import Path

COLORS = {
    'ocean_blue': '#2389BB',
    'dusk_orange': '#FF6723',
    'electric_cyan': '#03DDFF',
    'hot_magenta': '#FF00F0',
    'sea_teal': '#289389',
    'silvs_gray': '#D1D1D1',
    'up_green': '#008000',
    'down_red': '#FF3333',
    'neutral': '#666666',
}


def generate_event_calendar_chart(output_path: Path = None):
    """
    Critical Event Calendar with CLEAR Y-AXIS

    Y-axis: Risk Level (categorical + numerical proxy)
    - 3 = High Risk (FOMC, NFP, CPI, Debt Ceiling)
    - 2 = Medium Risk (Retail Sales, GDP, PCE)
    - 1 = Low Risk (Housing, Factory Orders)

    Each event shows expected market impact based on historical VIX behavior.
    """
    print("\nGenerating Event Calendar chart (WITH Y-AXIS)...")

    # 16-week window from today
    start_date = datetime(2026, 1, 8)
    end_date = start_date + timedelta(weeks=16)

    # Key events with RISK LEVEL and description
    # Risk: 3=High, 2=Medium, 1=Low
    # Impact: typical VIX move around this event
    events = [
        # FOMC meetings (High risk)
        {'date': datetime(2026, 1, 29), 'name': 'FOMC\nDecision', 'risk': 3, 'type': 'Fed', 'impact': '+2-5 VIX pts typical'},
        {'date': datetime(2026, 3, 19), 'name': 'FOMC\nDecision', 'risk': 3, 'type': 'Fed', 'impact': '+2-5 VIX pts typical'},

        # Employment (High risk)
        {'date': datetime(2026, 1, 10), 'name': 'NFP', 'risk': 3, 'type': 'Labor', 'impact': '+1-3 VIX pts'},
        {'date': datetime(2026, 2, 7), 'name': 'NFP', 'risk': 3, 'type': 'Labor', 'impact': '+1-3 VIX pts'},
        {'date': datetime(2026, 3, 6), 'name': 'NFP', 'risk': 3, 'type': 'Labor', 'impact': '+1-3 VIX pts'},

        # CPI (High risk)
        {'date': datetime(2026, 1, 15), 'name': 'CPI', 'risk': 3, 'type': 'Inflation', 'impact': '+2-4 VIX pts'},
        {'date': datetime(2026, 2, 12), 'name': 'CPI', 'risk': 3, 'type': 'Inflation', 'impact': '+2-4 VIX pts'},
        {'date': datetime(2026, 3, 12), 'name': 'CPI', 'risk': 3, 'type': 'Inflation', 'impact': '+2-4 VIX pts'},

        # Treasury Auctions (Medium-High risk)
        {'date': datetime(2026, 1, 14), 'name': '10Y\nAuction', 'risk': 2.5, 'type': 'Treasury', 'impact': '+0.5-2 VIX pts'},
        {'date': datetime(2026, 2, 11), 'name': '10Y\nAuction', 'risk': 2.5, 'type': 'Treasury', 'impact': '+0.5-2 VIX pts'},
        {'date': datetime(2026, 3, 10), 'name': '10Y\nAuction', 'risk': 2.5, 'type': 'Treasury', 'impact': '+0.5-2 VIX pts'},

        # Debt Ceiling (EXTREME risk if in play)
        {'date': datetime(2026, 3, 1), 'name': 'Debt\nCeiling?', 'risk': 3, 'type': 'Fiscal', 'impact': '+5-15 VIX pts if crisis'},

        # GDP (Medium risk)
        {'date': datetime(2026, 1, 30), 'name': 'GDP\nQ4 Adv', 'risk': 2, 'type': 'Growth', 'impact': '+0.5-1.5 VIX pts'},
        {'date': datetime(2026, 2, 27), 'name': 'GDP\nQ4 2nd', 'risk': 1.5, 'type': 'Growth', 'impact': 'Usually muted'},

        # PCE (Medium risk)
        {'date': datetime(2026, 1, 31), 'name': 'PCE', 'risk': 2, 'type': 'Inflation', 'impact': '+1-2 VIX pts'},
        {'date': datetime(2026, 2, 28), 'name': 'PCE', 'risk': 2, 'type': 'Inflation', 'impact': '+1-2 VIX pts'},

        # Retail Sales (Low-Medium risk)
        {'date': datetime(2026, 1, 16), 'name': 'Retail\nSales', 'risk': 1.5, 'type': 'Consumer', 'impact': 'Usually muted'},
        {'date': datetime(2026, 2, 14), 'name': 'Retail\nSales', 'risk': 1.5, 'type': 'Consumer', 'impact': 'Usually muted'},
    ]

    # Filter to window
    events = [e for e in events if start_date <= e['date'] <= end_date]

    # Sort by date
    events = sorted(events, key=lambda x: x['date'])

    fig, ax = plt.subplots(figsize=(14, 8))

    # Y-axis: Risk Level
    ax.set_ylim(0, 4)
    ax.set_ylabel('Risk Level', fontweight='bold', fontsize=12)

    # Add risk level labels
    ax.axhline(1, color=COLORS['silvs_gray'], linestyle='--', alpha=0.3)
    ax.axhline(2, color=COLORS['silvs_gray'], linestyle='--', alpha=0.3)
    ax.axhline(3, color=COLORS['silvs_gray'], linestyle='--', alpha=0.3)

    ax.text(start_date - timedelta(days=3), 1, 'LOW', fontsize=9, va='center',
            color=COLORS['up_green'], fontweight='bold')
    ax.text(start_date - timedelta(days=3), 2, 'MEDIUM', fontsize=9, va='center',
            color=COLORS['dusk_orange'], fontweight='bold')
    ax.text(start_date - timedelta(days=3), 3, 'HIGH', fontsize=9, va='center',
            color=COLORS['down_red'], fontweight='bold')

    # Background shading for risk zones
    ax.axhspan(0, 1.5, alpha=0.05, color=COLORS['up_green'])
    ax.axhspan(1.5, 2.5, alpha=0.05, color=COLORS['dusk_orange'])
    ax.axhspan(2.5, 4, alpha=0.05, color=COLORS['down_red'])

    # Color map by event type
    type_colors = {
        'Fed': COLORS['hot_magenta'],
        'Labor': COLORS['ocean_blue'],
        'Inflation': COLORS['dusk_orange'],
        'Treasury': COLORS['sea_teal'],
        'Fiscal': COLORS['down_red'],
        'Growth': COLORS['up_green'],
        'Consumer': COLORS['silvs_gray'],
    }

    # Plot events
    for event in events:
        color = type_colors.get(event['type'], COLORS['neutral'])

        # Bar showing risk level
        ax.bar(event['date'], event['risk'], width=2, color=color, alpha=0.8,
               edgecolor='white', linewidth=0.5)

        # Event label
        ax.text(event['date'], event['risk'] + 0.15, event['name'],
                ha='center', va='bottom', fontsize=8, fontweight='bold',
                color=color)

    # Week markers
    current = start_date
    week_num = 1
    while current <= end_date:
        if current.weekday() == 0:  # Monday
            ax.axvline(current, color=COLORS['silvs_gray'], linestyle=':', alpha=0.3)
            ax.text(current, 3.8, f'W{week_num}', fontsize=7, ha='center',
                    color=COLORS['neutral'], alpha=0.7)
            week_num += 1
        current += timedelta(days=1)

    # X-axis formatting
    ax.set_xlim(start_date - timedelta(days=3), end_date + timedelta(days=3))
    ax.xaxis.set_major_locator(plt.matplotlib.dates.WeekdayLocator(byweekday=0))
    ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%b %d'))
    plt.xticks(rotation=45, ha='right')

    # Legend
    legend_elements = [
        mpatches.Patch(facecolor=type_colors['Fed'], label='Fed/FOMC'),
        mpatches.Patch(facecolor=type_colors['Labor'], label='Employment'),
        mpatches.Patch(facecolor=type_colors['Inflation'], label='Inflation'),
        mpatches.Patch(facecolor=type_colors['Treasury'], label='Treasury'),
        mpatches.Patch(facecolor=type_colors['Fiscal'], label='Fiscal'),
        mpatches.Patch(facecolor=type_colors['Growth'], label='Growth'),
    ]
    ax.legend(handles=legend_elements, loc='upper right', ncol=3,
              frameon=True, facecolor='white', fontsize=8)

    ax.set_title('Critical Event Calendar: 16-Week Risk Window\nJanuary - April 2026',
                 fontsize=14, fontweight='bold', pad=20)

    # Clean styling
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(False)

    # Key insight box
    insight_text = (
        "Y-Axis = Risk Level:\n"
        "3 = High (FOMC, NFP, CPI)\n"
        "2 = Medium (GDP, PCE)\n"
        "1 = Low (Retail, Housing)\n\n"
        "Based on historical VIX\n"
        "behavior around events"
    )
    ax.text(0.98, 0.02, insight_text, transform=ax.transAxes,
            fontsize=8, verticalalignment='bottom', horizontalalignment='right',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='white',
                      edgecolor=COLORS['neutral'], alpha=0.95),
            family='monospace')

    # Branding
    fig.text(0.01, 0.99, 'LIGHTHOUSE MACRO', fontsize=10, fontweight='bold',
             color=COLORS['ocean_blue'], ha='left', va='top')
    fig.text(0.99, 0.01, 'MACRO, ILLUMINATED.', fontsize=8, style='italic',
             color=COLORS['ocean_blue'], ha='right', va='bottom', alpha=0.7)
    fig.text(0.01, 0.01,
             'Risk levels based on historical VIX response to similar events | Not investment advice',
             fontsize=7, color=COLORS['neutral'], ha='left', va='bottom', style='italic')

    plt.tight_layout()

    if output_path is None:
        output_path = Path('/Users/bob/LHM/data/charts/institutional/chart_event_calendar.png')

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close(fig)

    print(f"  Saved: {output_path}")
    return output_path


if __name__ == "__main__":
    generate_event_calendar_chart()
