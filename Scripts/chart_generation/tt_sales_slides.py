#!/usr/bin/env python3
"""
TOKEN TERMINAL x LIGHTHOUSE MACRO — Sales Deck Slides
======================================================
PNG slides for sending to Token Terminal sales team.
Dark theme, institutional quality.

Output: /Users/bob/LHM/Outputs/token_terminal_deck/slides/
"""

import sys
sys.path.insert(0, '/Users/bob/LHM/Scripts/utilities')

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Rectangle
from pathlib import Path
from datetime import datetime

from lighthouse_chart_style import LIGHTHOUSE_COLORS as C

OUT = Path('/Users/bob/LHM/Outputs/token_terminal_deck/slides')
OUT.mkdir(parents=True, exist_ok=True)

# Brand colors
BG = '#0A1628'
OCEAN = '#2389BB'
DUSK = '#FF6723'
SEA = '#00BB89'
SKY = '#00BBFF'
WHITE = '#e6edf3'
MUTED = '#7a8a9e'
SPINE = '#2a4060'


def add_accent_bars(fig):
    """Add top and bottom accent bars."""
    bar = fig.add_axes([0.03, 0.955, 0.94, 0.005])
    bar.axhspan(0, 1, 0, 0.67, color=OCEAN)
    bar.axhspan(0, 1, 0.67, 1.0, color=DUSK)
    bar.set_xlim(0, 1); bar.set_ylim(0, 1); bar.axis('off')

    bbar = fig.add_axes([0.03, 0.035, 0.94, 0.005])
    bbar.axhspan(0, 1, 0, 0.67, color=OCEAN)
    bbar.axhspan(0, 1, 0.67, 1.0, color=DUSK)
    bbar.set_xlim(0, 1); bbar.set_ylim(0, 1); bbar.axis('off')


def add_footer(fig, source=None):
    """Add standard footer."""
    fig.text(0.97, 0.015, 'MACRO, ILLUMINATED.', fontsize=11,
             color=OCEAN, ha='right', va='top', style='italic', fontweight='bold')
    if source:
        date_str = datetime.now().strftime('%m.%d.%Y')
        fig.text(0.03, 0.015, f'Lighthouse Macro | {source}; {date_str}',
                 fontsize=7, color=MUTED, ha='left', va='top', style='italic')


def save(fig, name):
    fig.savefig(OUT / name, dpi=200, bbox_inches='tight', pad_inches=0.15,
                facecolor=BG, edgecolor='none')
    plt.close(fig)
    print(f'  Saved: {name}')


# =========================================================================
# SLIDE 1: TITLE
# =========================================================================

def slide_01_title():
    fig = plt.figure(figsize=(16, 9), facecolor=BG)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor(BG)
    ax.axis('off')

    # Lighthouse Macro branding top-left
    ax.text(0.05, 0.92, 'LIGHTHOUSE MACRO', fontsize=14,
            color=OCEAN, fontweight='bold', transform=ax.transAxes)

    # Main title
    ax.text(0.5, 0.58, 'Crypto Protocol\nFundamentals Deck', fontsize=42,
            color=WHITE, fontweight='bold', ha='center', va='center',
            transform=ax.transAxes, linespacing=1.3)

    # Subtitle
    ax.text(0.5, 0.40, '34 Protocols Scored on Financials, Usage & Valuation',
            fontsize=16, color=SKY, ha='center', va='center',
            transform=ax.transAxes, style='italic')

    # Collab line
    ax.text(0.5, 0.30, 'Token Terminal  ×  Lighthouse Macro',
            fontsize=14, color=MUTED, ha='center', va='center',
            transform=ax.transAxes)

    # Date
    ax.text(0.5, 0.22, datetime.now().strftime('January %d, %Y'),
            fontsize=12, color=MUTED, ha='center', va='center',
            transform=ax.transAxes)

    # Author
    ax.text(0.5, 0.12, 'Bob Sheehan, CFA, CMT  |  Founder & CIO',
            fontsize=11, color=MUTED, ha='center', va='center',
            transform=ax.transAxes)

    add_accent_bars(fig)
    add_footer(fig)
    save(fig, 'slide_01_title.png')


# =========================================================================
# SLIDE 2: METHODOLOGY
# =========================================================================

def slide_02_methodology():
    fig = plt.figure(figsize=(16, 9), facecolor=BG)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor(BG)
    ax.axis('off')

    ax.text(0.05, 0.92, 'LIGHTHOUSE MACRO', fontsize=12,
            color=OCEAN, fontweight='bold', transform=ax.transAxes)

    ax.text(0.5, 0.88, 'Scoring Methodology', fontsize=28,
            color=WHITE, fontweight='bold', ha='center', transform=ax.transAxes)

    ax.text(0.5, 0.82, '24-Point System  |  Three Pillars of Fundamental Quality',
            fontsize=13, color=SKY, ha='center', transform=ax.transAxes, style='italic')

    # Three pillars
    pillars = [
        {
            'title': 'FINANCIAL',
            'color': SEA,
            'x': 0.18,
            'items': [
                'Annualized Revenue',
                'Revenue Growth (90d)',
                'Fee Generation',
                'Net Earnings (Rev − Incentives)',
            ],
            'weight': '8 points'
        },
        {
            'title': 'USAGE',
            'color': SKY,
            'x': 0.50,
            'items': [
                'Daily Active Users (DAU)',
                'DAU Growth (90d)',
                'Total Value Locked (TVL)',
                'Developer Activity',
            ],
            'weight': '8 points'
        },
        {
            'title': 'VALUATION',
            'color': DUSK,
            'x': 0.82,
            'items': [
                'P/F Ratio (FDV / Fees)',
                'Float Ratio (Circ / Total)',
                'Subsidy Score',
                'Market Cap vs Revenue',
            ],
            'weight': '8 points'
        }
    ]

    for p in pillars:
        # Pillar header
        ax.text(p['x'], 0.70, p['title'], fontsize=18, color=p['color'],
                fontweight='bold', ha='center', transform=ax.transAxes)

        # Weight
        ax.text(p['x'], 0.64, p['weight'], fontsize=11, color=MUTED,
                ha='center', transform=ax.transAxes)

        # Underline
        ax.plot([p['x'] - 0.10, p['x'] + 0.10], [0.62, 0.62],
                color=p['color'], linewidth=2, alpha=0.5, transform=ax.transAxes)

        # Items
        for i, item in enumerate(p['items']):
            ax.text(p['x'], 0.55 - i * 0.065, f'•  {item}',
                    fontsize=11, color=WHITE, ha='center', transform=ax.transAxes)

    # Bottom summary
    ax.text(0.5, 0.18, 'VERDICT TIERS', fontsize=14, color=WHITE,
            fontweight='bold', ha='center', transform=ax.transAxes)

    tiers = [
        ('Tier 1: Accumulate', '≥ 75', SEA),
        ('Tier 2: Hold', '60–74', SKY),
        ('Neutral: Watch', '45–59', MUTED),
        ('Avoid', '< 45', '#FF4455'),
    ]

    for i, (label, score, color) in enumerate(tiers):
        x = 0.18 + i * 0.22
        ax.text(x, 0.12, label, fontsize=11, color=color,
                fontweight='bold', ha='center', transform=ax.transAxes)
        ax.text(x, 0.07, f'Score: {score}', fontsize=9, color=MUTED,
                ha='center', transform=ax.transAxes)

    add_accent_bars(fig)
    add_footer(fig, source='LHM Scoring Engine')
    save(fig, 'slide_02_methodology.png')


# =========================================================================
# SLIDE 3: KEY FINDINGS
# =========================================================================

def slide_03_key_findings():
    fig = plt.figure(figsize=(16, 9), facecolor=BG)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor(BG)
    ax.axis('off')

    ax.text(0.05, 0.92, 'LIGHTHOUSE MACRO', fontsize=12,
            color=OCEAN, fontweight='bold', transform=ax.transAxes)

    ax.text(0.5, 0.88, 'Key Findings', fontsize=28,
            color=WHITE, fontweight='bold', ha='center', transform=ax.transAxes)

    ax.text(0.5, 0.82, '34 Protocols Analyzed  |  January 2026',
            fontsize=13, color=SKY, ha='center', transform=ax.transAxes, style='italic')

    findings = [
        {
            'stat': '18%',
            'label': 'Made Tier 1',
            'detail': 'Only 6 of 34 protocols pass the fundamental filter.',
            'color': SEA,
        },
        {
            'stat': '35%',
            'label': 'Scored Avoid',
            'detail': 'Over a third of protocols fail on financials, usage, or valuation.',
            'color': '#FF4455',
        },
        {
            'stat': '$940M',
            'label': 'Top Net Earnings',
            'detail': 'Hyperliquid leads with the highest revenue minus incentives.',
            'color': SKY,
        },
        {
            'stat': '$6.2B',
            'label': 'Largest Subsidy Burn',
            'detail': 'Solana: $104 in token incentives per $1 of protocol revenue.',
            'color': DUSK,
        },
    ]

    for i, f in enumerate(findings):
        y_base = 0.68 - i * 0.155

        # Stat number
        ax.text(0.12, y_base, f['stat'], fontsize=32, color=f['color'],
                fontweight='bold', ha='center', va='center', transform=ax.transAxes)

        # Label
        ax.text(0.25, y_base + 0.02, f['label'], fontsize=15, color=WHITE,
                fontweight='bold', va='center', transform=ax.transAxes)

        # Detail
        ax.text(0.25, y_base - 0.035, f['detail'], fontsize=11, color=MUTED,
                va='center', transform=ax.transAxes)

        # Divider
        if i < len(findings) - 1:
            ax.plot([0.05, 0.95], [y_base - 0.07, y_base - 0.07],
                    color=SPINE, linewidth=0.5, transform=ax.transAxes)

    add_accent_bars(fig)
    add_footer(fig, source='Token Terminal, LHM Scoring Engine')
    save(fig, 'slide_03_key_findings.png')


# =========================================================================
# SLIDE 4: TOP PROTOCOLS
# =========================================================================

def slide_04_top_protocols():
    fig = plt.figure(figsize=(16, 9), facecolor=BG)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor(BG)
    ax.axis('off')

    ax.text(0.05, 0.92, 'LIGHTHOUSE MACRO', fontsize=12,
            color=OCEAN, fontweight='bold', transform=ax.transAxes)

    ax.text(0.5, 0.88, 'Tier 1: Accumulate', fontsize=28,
            color=SEA, fontweight='bold', ha='center', transform=ax.transAxes)

    ax.text(0.5, 0.82, 'Protocols That Pass the Fundamental Filter',
            fontsize=13, color=SKY, ha='center', transform=ax.transAxes, style='italic')

    # Table header
    headers = ['Protocol', 'Score', 'Financial', 'Usage', 'Valuation', 'Sector']
    header_x = [0.10, 0.30, 0.42, 0.54, 0.66, 0.82]

    for x, h in zip(header_x, headers):
        ax.text(x, 0.73, h, fontsize=11, color=OCEAN,
                fontweight='bold', transform=ax.transAxes)

    ax.plot([0.05, 0.95], [0.71, 0.71], color=OCEAN, linewidth=1.5,
            transform=ax.transAxes)

    # Top protocols data
    protocols = [
        ('PancakeSwap', '86', '95', '72', '90', 'DeFi – DEX'),
        ('Uniswap', '85', '96', '66', '92', 'DeFi – DEX'),
        ('Aave', '85', '94', '65', '96', 'DeFi – Lending'),
        ('GMX', '85', '88', '67', '100', 'DeFi – Derivatives'),
        ('Arbitrum One', '83', '92', '63', '95', 'Layer 2'),
        ('Lido Finance', '81', '100', '54', '88', 'Liquid Staking'),
    ]

    for i, (name, score, fin, use, val, sector) in enumerate(protocols):
        y = 0.64 - i * 0.07
        ax.text(header_x[0], y, name, fontsize=12, color=WHITE,
                fontweight='bold', transform=ax.transAxes)
        ax.text(header_x[1], y, score, fontsize=12, color=SEA,
                fontweight='bold', transform=ax.transAxes)
        ax.text(header_x[2], y, fin, fontsize=11, color=WHITE,
                transform=ax.transAxes)
        ax.text(header_x[3], y, use, fontsize=11, color=WHITE,
                transform=ax.transAxes)
        ax.text(header_x[4], y, val, fontsize=11, color=WHITE,
                transform=ax.transAxes)
        ax.text(header_x[5], y, sector, fontsize=10, color=MUTED,
                transform=ax.transAxes)

        if i < len(protocols) - 1:
            ax.plot([0.05, 0.95], [y - 0.03, y - 0.03],
                    color=SPINE, linewidth=0.3, transform=ax.transAxes)

    # Bottom note
    ax.text(0.5, 0.15, 'DeFi dominates Tier 1. Layer 1 chains struggle on valuation.',
            fontsize=12, color=MUTED, ha='center', transform=ax.transAxes, style='italic')

    add_accent_bars(fig)
    add_footer(fig, source='Token Terminal, LHM Scoring Engine')
    save(fig, 'slide_04_top_protocols.png')


# =========================================================================
# SLIDE 5: MACRO OVERLAY
# =========================================================================

def slide_05_macro_overlay():
    fig = plt.figure(figsize=(16, 9), facecolor=BG)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor(BG)
    ax.axis('off')

    ax.text(0.05, 0.92, 'LIGHTHOUSE MACRO', fontsize=12,
            color=OCEAN, fontweight='bold', transform=ax.transAxes)

    ax.text(0.5, 0.88, 'Macro Overlay: What Drives Crypto Fundamentals?',
            fontsize=24, color=WHITE, fontweight='bold', ha='center',
            transform=ax.transAxes)

    ax.text(0.5, 0.82, 'Token Terminal Metrics × Lighthouse Macro Indicators',
            fontsize=13, color=SKY, ha='center', transform=ax.transAxes, style='italic')

    # Overlay pairs
    pairs = [
        {
            'crypto': 'Protocol Revenue',
            'macro': 'Fed RRP (Liquidity)',
            'finding': 'Revenue tracks Fed liquidity drainage. As RRP nears zero, the buffer is gone.',
            'chart': 'Chart 21',
            'color': DUSK,
        },
        {
            'crypto': 'Aggregate DAU',
            'macro': 'Financial Conditions (NFCI)',
            'finding': 'Crypto adoption expands when financial conditions loosen. NFCI leads DAU by 4-8 weeks.',
            'chart': 'Chart 22',
            'color': SKY,
        },
        {
            'crypto': 'Protocol Fees',
            'macro': 'HY Credit Spreads',
            'finding': 'Tight spreads + rising fees = risk-on regime. Widening spreads compress fee generation.',
            'chart': 'Chart 23',
            'color': SEA,
        },
        {
            'crypto': 'DeFi TVL',
            'macro': 'VIX (Volatility)',
            'finding': 'TVL recovers when vol compresses. Structure improving, but fundamentals lag.',
            'chart': 'Chart 24',
            'color': OCEAN,
        },
    ]

    for i, p in enumerate(pairs):
        y_base = 0.68 - i * 0.15

        # Chart ref
        ax.text(0.06, y_base, p['chart'], fontsize=9, color=p['color'],
                fontweight='bold', va='center', transform=ax.transAxes)

        # Crypto metric → Macro indicator
        ax.text(0.15, y_base + 0.02, f"{p['crypto']}  →  {p['macro']}",
                fontsize=13, color=WHITE, fontweight='bold', va='center',
                transform=ax.transAxes)

        # Finding
        ax.text(0.15, y_base - 0.035, p['finding'],
                fontsize=10, color=MUTED, va='center', transform=ax.transAxes)

        if i < len(pairs) - 1:
            ax.plot([0.05, 0.95], [y_base - 0.07, y_base - 0.07],
                    color=SPINE, linewidth=0.5, transform=ax.transAxes)

    # Bottom CTA
    ax.text(0.5, 0.12, 'Crypto doesn\'t trade in a vacuum. Macro liquidity is the tide.',
            fontsize=13, color=DUSK, ha='center', transform=ax.transAxes,
            fontweight='bold', style='italic')

    add_accent_bars(fig)
    add_footer(fig, source='Token Terminal, FRED, Lighthouse Macro')
    save(fig, 'slide_05_macro_overlay.png')


# =========================================================================
# SLIDE 6: PARTNERSHIP / CTA
# =========================================================================

def slide_06_partnership():
    fig = plt.figure(figsize=(16, 9), facecolor=BG)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor(BG)
    ax.axis('off')

    ax.text(0.05, 0.92, 'LIGHTHOUSE MACRO', fontsize=12,
            color=OCEAN, fontweight='bold', transform=ax.transAxes)

    ax.text(0.5, 0.82, 'What We Built With Token Terminal Data',
            fontsize=28, color=WHITE, fontweight='bold', ha='center',
            transform=ax.transAxes)

    # Deliverables
    items = [
        ('25-Chart Research Deck', 'Institutional-quality charts covering scoring, trends, sector analysis, and macro overlays.'),
        ('24-Point Scoring Engine', 'Automated fundamental scoring across financial, usage, and valuation dimensions.'),
        ('Macro × Crypto Overlay', '5 charts mapping crypto metrics to Fed liquidity, credit spreads, volatility, and yield curve.'),
        ('Twitter Thread (4 Posts)', 'Research-driven thread tagging @tokenterminal, designed for engagement and credibility.'),
        ('Repeatable Pipeline', 'Fully automated. New data in, new charts out. Weekly or on-demand refresh.'),
    ]

    for i, (title, desc) in enumerate(items):
        y = 0.68 - i * 0.105
        ax.text(0.08, y, '→', fontsize=16, color=DUSK,
                fontweight='bold', va='center', transform=ax.transAxes)
        ax.text(0.12, y + 0.01, title, fontsize=14, color=WHITE,
                fontweight='bold', va='center', transform=ax.transAxes)
        ax.text(0.12, y - 0.03, desc, fontsize=10, color=MUTED,
                va='center', transform=ax.transAxes)

    # Contact
    ax.text(0.5, 0.14, 'Bob Sheehan, CFA, CMT  |  bob@lighthousemacro.com  |  @LHMacro',
            fontsize=12, color=MUTED, ha='center', transform=ax.transAxes)

    ax.text(0.5, 0.08, 'LighthouseMacro.com  |  Join The Watch.',
            fontsize=13, color=OCEAN, ha='center', fontweight='bold',
            transform=ax.transAxes)

    add_accent_bars(fig)
    add_footer(fig)
    save(fig, 'slide_06_partnership.png')


# =========================================================================
# RUN ALL
# =========================================================================

def run_all():
    print('GENERATING SALES SLIDES (dark theme):')
    slide_01_title()
    slide_02_methodology()
    slide_03_key_findings()
    slide_04_top_protocols()
    slide_05_macro_overlay()
    slide_06_partnership()
    print(f'\nDone. 6 slides saved to {OUT}/')


if __name__ == '__main__':
    run_all()
