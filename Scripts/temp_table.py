import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OCEAN = '#0089D1'
DUSK = '#FF6723'
VENUS = '#FF2389'
SEA = '#00BB99'

data = [
    ("ISM Manufacturing PMI", "55.9", "Expansion (breakout from 26-month contraction)"),
    ("ISM Services PMI", "53.8", "Modest expansion"),
    ("ISM Mfg New Orders", "57.1", "Strong demand"),
    ("ISM Mfg Employment", "48.1", "Still contracting (output without hiring)"),
    ("ISM Mfg Prices Paid", "59.0", "Input costs rising"),
    ("Core Capex Orders YoY", "+20.1%", "Very strong (front-loading risk)"),
    ("Bookings/Billings Ratio", "1.28x", "Backlog building"),
    ("Durable Goods ex-Transport YoY", "+5.1%", "Positive trend"),
    ("Inventory/Sales Ratio", "1.37", "Balanced"),
    ("Regional Fed 5-Survey Avg", "2.2", "Barely positive (lagging ISM)"),
    ("Industrial Production YoY", "+2.3%", "Modest growth"),
    ("Mfg Capacity Utilization", "75.5%", "Slack (below 78% threshold)"),
    ("Corporate Profits YoY", "-2.4%", "Contracting (margin pressure)"),
    ("Unit Labor Costs YoY", "+1.3%", "Moderate"),
    ("Productivity YoY", "+1.9%", "Solid"),
    ("C&I Loan Growth YoY", "+3.0%", "Modest"),
    ("Business Delinquency Rate", "1.3%", "Normalizing"),
    ("LEI YoY", "-3.7%", "Near recession threshold"),
]

def get_signal_color(signal, theme='dark'):
    s = signal.lower()
    if any(w in s for w in ['contracting', 'recession', 'still contracting']):
        return VENUS
    elif any(w in s for w in ['barely', 'slack', 'front-loading', 'margin', 'decelerating']):
        return DUSK
    elif any(w in s for w in ['strong', 'expansion', 'breakout', 'building', 'solid']):
        return SEA
    else:
        return '#e8edf3' if theme == 'dark' else '#1a1a1a'

def make_table(theme='dark'):
    if theme == 'dark':
        bg, fg, spine = '#0a1628', '#e8edf3', '#1e3350'
        row_alt, row_norm = '#0f1f38', '#0a1628'
        muted = '#6b7d99'
    else:
        bg, fg, spine = '#ffffff', '#1a1a1a', '#cccccc'
        row_alt, row_norm = '#f5f8fc', '#ffffff'
        muted = '#888888'

    n_rows = len(data)
    row_h = 0.042
    header_h = 0.05
    # Calculate tight figure: branding top ~12%, table, branding bottom ~6%
    top_brand = 0.115
    bot_brand = 0.055
    table_frac = header_h + n_rows * row_h  # ~0.806
    # total content fraction
    total = top_brand + table_frac + bot_brand  # should be ~0.976

    fig = plt.figure(figsize=(14, 11.5), facecolor=bg)

    # === BRANDING ===
    fig.text(0.04, 0.98, 'LIGHTHOUSE MACRO', fontsize=14, fontweight='bold',
             color=OCEAN, va='top', ha='left', family='sans-serif')
    fig.text(0.96, 0.98, 'February 19, 2026', fontsize=12,
             color=muted, va='top', ha='right', family='sans-serif')

    bar = fig.add_axes([0.03, 0.962, 0.94, 0.005])
    bar.axhspan(0, 1, 0, 0.67, color=OCEAN)
    bar.axhspan(0, 1, 0.67, 1.0, color=DUSK)
    bar.set_xlim(0, 1); bar.set_ylim(0, 1); bar.axis('off')

    fig.text(0.50, 0.945, 'Business Pillar: Where We Are Now', fontsize=20,
             fontweight='bold', color=fg, va='top', ha='center', family='sans-serif')
    fig.text(0.50, 0.915, 'The Diagnostic Dozen: Pillar 6 Summary',
             fontsize=16, fontstyle='italic', color=OCEAN, va='top', ha='center',
             family='sans-serif')

    # === TABLE ===
    col_x = [0.04, 0.38, 0.52]
    col_w = [0.34, 0.14, 0.48]
    y = 0.89

    # Header
    for cx, cw in zip(col_x, col_w):
        fig.patches.append(plt.Rectangle((cx, y - header_h), cw, header_h,
                           transform=fig.transFigure, facecolor=OCEAN, edgecolor='none', clip_on=False))
    for hx, h in zip([0.06, 0.45, 0.54], ['Indicator', 'Latest', 'Signal']):
        fig.text(hx, y - header_h/2, h, fontsize=13, fontweight='bold',
                 color='#ffffff', va='center', ha='left' if h != 'Latest' else 'center',
                 family='sans-serif')
    y -= header_h

    # Rows
    for idx, (indicator, latest, signal) in enumerate(data):
        rc = row_alt if idx % 2 == 0 else row_norm
        for cx, cw in zip(col_x, col_w):
            fig.patches.append(plt.Rectangle((cx, y - row_h), cw, row_h,
                               transform=fig.transFigure, facecolor=rc, edgecolor='none', clip_on=False))
        fig.text(0.06, y - row_h/2, indicator, fontsize=12,
                 color=fg, va='center', ha='left', family='sans-serif')
        fig.text(0.45, y - row_h/2, latest, fontsize=12, fontweight='bold',
                 color=fg, va='center', ha='center', family='monospace')
        fig.text(0.54, y - row_h/2, signal, fontsize=12,
                 color=get_signal_color(signal, theme), va='center', ha='left', family='sans-serif')
        y -= row_h

    # Border
    fig.patches.append(plt.Rectangle((col_x[0], y), sum(col_w), 0.89 - y,
                       transform=fig.transFigure, facecolor='none', edgecolor=spine,
                       linewidth=0.5, clip_on=False))

    # === FOOTER ===
    bbar = fig.add_axes([0.03, 0.025, 0.94, 0.005])
    bbar.axhspan(0, 1, 0, 0.67, color=OCEAN)
    bbar.axhspan(0, 1, 0.67, 1.0, color=DUSK)
    bbar.set_xlim(0, 1); bbar.set_ylim(0, 1); bbar.axis('off')

    fig.text(0.04, 0.012, 'Lighthouse Macro | BLS, ISM, Census, BEA, Conference Board; 02.19.2026',
             fontsize=10, fontstyle='italic', color=muted, va='bottom', ha='left', family='sans-serif')
    fig.text(0.96, 0.012, 'MACRO, ILLUMINATED.', fontsize=14, fontweight='bold',
             fontstyle='italic', color=OCEAN, va='bottom', ha='right', family='sans-serif')

    suffix = 'dark' if theme == 'dark' else 'white'
    path = f'/Users/bob/LHM/Outputs/business_pillar_table_{suffix}.png'
    fig.savefig(path, dpi=200, facecolor=bg, bbox_inches='tight', pad_inches=0.10)
    plt.close(fig)
    print(f"Saved: {path}")

make_table('dark')
make_table('white')
