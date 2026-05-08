"""
LHM Universe Scan Visualizer
============================

Reads the output of lhm_universe_scan.py and produces:
  - Top setups table (PNG) split by stocks vs ETFs
  - Category breakdown chart (count of GREEN regime by score tier)
  - HTML summary with the top-50 names embedded

Use after lhm_universe_scan.py completes.
"""
import os
import sys
import base64
from datetime import datetime
from io import BytesIO

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

sys.path.insert(0, '/Users/bob/LHM/Scripts/chart_generation')
from lhm_chart_template import (COLORS, set_theme, new_fig, style_ax,
                                 brand_fig, save_fig)

SCAN_DIR = '/Users/bob/LHM/Outputs/scan'


def regime_color(r):
    return COLORS['ocean'] if r == 'GREEN' else (COLORS['port'] if r == 'RED' else COLORS['doldrums'])


def render_top_table(df, kind, n=25, save_path=None):
    """Render top N as a clean table chart (matplotlib)."""
    set_theme('white')
    sub = df[df.kind == kind].head(n).copy()
    if sub.empty:
        return None

    fig, ax = new_fig(figsize=(15, max(8, n * 0.32 + 2)))
    ax.set_axis_off()

    headers = ['Rank', 'Ticker', 'Last', 'Score', 'Z-21', 'Z-63', 'd21Z', 'd50Z', 'd200Z', 'RS']
    col_widths = [0.05, 0.10, 0.10, 0.07, 0.09, 0.09, 0.09, 0.09, 0.09, 0.10]
    col_x = np.cumsum([0.04] + col_widths[:-1])

    # Header row
    y_top = 0.94
    for x, w, h in zip(col_x, col_widths, headers):
        ax.text(x + w/2, y_top, h, ha='center', va='center',
                fontsize=11, fontweight='bold', color=COLORS['ocean'],
                transform=ax.transAxes)
    ax.plot([0.04, 0.96], [y_top - 0.02, y_top - 0.02],
            color=COLORS['ocean'], linewidth=1.2, transform=ax.transAxes)

    row_h = 0.85 / n
    for i, r in enumerate(sub.itertuples(), 1):
        y = y_top - 0.04 - (i - 1) * row_h
        # Alternating row shading
        if i % 2 == 0:
            from matplotlib.patches import Rectangle
            rect = Rectangle((0.02, y - row_h*0.45), 0.96, row_h*0.9,
                             color='#f5f8fa', zorder=0,
                             transform=ax.transAxes)
            ax.add_patch(rect)

        cells = [
            (str(i), COLORS['doldrums']),
            (r.ticker, COLORS['ocean']),
            (f'${r.last:,.2f}', COLORS['fg'] if False else '#1a1a1a'),
            (str(r.score), COLORS['ocean'] if r.score >= 6 else COLORS['doldrums']),
            (f'{r.z21:+.2f}', COLORS['port'] if r.z21 < -0.5 else ('#1a1a1a' if r.z21 < 0 else COLORS['ocean'])),
            (f'{r.z63:+.2f}', COLORS['port'] if r.z63 < -0.5 else ('#1a1a1a' if r.z63 < 0 else COLORS['ocean'])),
            (f'{r.d21z:+.2f}', '#1a1a1a'),
            (f'{r.d50z:+.2f}', '#1a1a1a'),
            (f'{r.d200z:+.2f}', COLORS['port'] if r.d200z > 1.5 else '#1a1a1a'),
            (r.regime, regime_color(r.regime)),
        ]
        for (val, color), x, w in zip(cells, col_x, col_widths):
            weight = 'bold' if x == col_x[1] or x == col_x[-1] else 'normal'
            ax.text(x + w/2, y, val, ha='center', va='center',
                    fontsize=10, fontweight=weight, color=color,
                    transform=ax.transAxes)

    title_kind = 'Stocks' if kind == 'stock' else 'ETFs'
    n_total = (df.kind == kind).sum()
    brand_fig(fig,
        title=f'Top {n} {title_kind} by LHM Setup Score',
        subtitle=f'Universe: {n_total:,} {title_kind.lower()} | Score weights GREEN regime + Z constructive + not stretched',
        source='Lighthouse Macro Universe Scan',
        data_date=datetime.now())
    if save_path:
        save_fig(fig, save_path)
        return save_path
    return fig


def render_category_summary(df, save_path=None):
    """Score-tier breakdown chart."""
    set_theme('white')
    fig, ax = new_fig(figsize=(13, 7))

    bins = [(-100, 0, '<0 Broken'),
            (0, 3, '0-2 Weak'),
            (3, 5, '3-4 Decent'),
            (5, 7, '5-6 Strong'),
            (7, 100, '7+ Cleanest')]

    stock_counts = []
    etf_counts = []
    labels = []
    for lo, hi, lab in bins:
        s = ((df.score >= lo) & (df.score < hi) & (df.kind == 'stock')).sum()
        e = ((df.score >= lo) & (df.score < hi) & (df.kind == 'etf')).sum()
        stock_counts.append(s)
        etf_counts.append(e)
        labels.append(lab)

    x = np.arange(len(labels))
    w = 0.4
    ax.bar(x - w/2, stock_counts, w, color=COLORS['ocean'], label='Stocks', zorder=3)
    ax.bar(x + w/2, etf_counts, w, color=COLORS['dusk'], label='ETFs', zorder=3)

    for xi, s, e in zip(x, stock_counts, etf_counts):
        ax.text(xi - w/2, s, str(s), ha='center', va='bottom', fontsize=10,
                fontweight='bold', color=COLORS['ocean'])
        ax.text(xi + w/2, e, str(e), ha='center', va='bottom', fontsize=10,
                fontweight='bold', color=COLORS['dusk'])

    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    style_ax(ax)
    ax.set_ylabel('Count')
    ax.legend(loc='upper left', fontsize=10, framealpha=0.95)

    brand_fig(fig,
        title='Universe scan: distribution of LHM setup scores',
        subtitle='Stocks vs ETFs across score tiers',
        source='Lighthouse Macro Universe Scan',
        data_date=datetime.now())
    if save_path:
        save_fig(fig, save_path)
        return save_path
    return fig


def img_to_b64(path):
    with open(path, 'rb') as f:
        return 'data:image/png;base64,' + base64.b64encode(f.read()).decode('ascii')


def render_html(df, charts):
    """One-page HTML summary with embedded base64 images."""
    top_stocks = df[df.kind == 'stock'].head(50)
    top_etfs = df[df.kind == 'etf'].head(30)

    def row_html(r, i):
        score_class = 'green' if r.score >= 6 else ('yellow' if r.score >= 4 else 'gray')
        return (f'<tr><td>{i}</td><td><b>{r.ticker}</b></td>'
                f'<td>${r.last:.2f}</td>'
                f'<td class="{score_class}">{r.score}</td>'
                f'<td>{r.z21:+.2f}</td><td>{r.z63:+.2f}</td>'
                f'<td>{r.d50z:+.2f}</td><td>{r.d200z:+.2f}</td>'
                f'<td class="{r.regime.lower() if r.regime != "mixed" else "gray"}">{r.regime}</td></tr>')

    stock_rows = '\n'.join(row_html(r, i) for i, r in enumerate(top_stocks.itertuples(), 1))
    etf_rows = '\n'.join(row_html(r, i) for i, r in enumerate(top_etfs.itertuples(), 1))

    summary_b64 = img_to_b64(charts['summary'])

    html = f'''<!doctype html>
<html><head><meta charset="utf-8">
<title>LHM Universe Scan - {datetime.now().strftime("%Y-%m-%d")}</title>
<style>
body {{ font-family: -apple-system, sans-serif; max-width: 1200px; margin: 2rem auto;
       padding: 0 2rem; color: #1a1a1a; }}
h1 {{ color: #2389BB; border-bottom: 3px solid #FF6723; padding-bottom: 0.3em; }}
h2 {{ color: #2389BB; margin-top: 2em; }}
table {{ border-collapse: collapse; width: 100%; font-size: 13px; margin: 1em 0; }}
th {{ background: #2389BB; color: white; padding: 8px; text-align: center; }}
td {{ padding: 6px 8px; text-align: center; border-bottom: 1px solid #eee; }}
tr:nth-child(even) td {{ background: #f5f8fa; }}
.green {{ color: #00BB89; font-weight: bold; }}
.red {{ color: #892323; font-weight: bold; }}
.yellow {{ color: #FF6723; font-weight: bold; }}
.gray {{ color: #898989; }}
img {{ width: 100%; max-width: 1100px; }}
.meta {{ color: #898989; font-size: 12px; }}
</style></head><body>
<h1>LHM Universe Scan</h1>
<p class="meta">{datetime.now().strftime("%B %d, %Y - %H:%M ET")} | {len(df):,} tickers screened</p>
<img src="{summary_b64}">
<h2>Top 50 Stocks</h2>
<table><thead><tr><th>#</th><th>Ticker</th><th>Last</th><th>Score</th>
<th>Z-21</th><th>Z-63</th><th>d50Z</th><th>d200Z</th><th>RS</th></tr></thead>
<tbody>{stock_rows}</tbody></table>
<h2>Top 30 ETFs</h2>
<table><thead><tr><th>#</th><th>Ticker</th><th>Last</th><th>Score</th>
<th>Z-21</th><th>Z-63</th><th>d50Z</th><th>d200Z</th><th>RS</th></tr></thead>
<tbody>{etf_rows}</tbody></table>
<p class="meta">Lighthouse Macro | MACRO, ILLUMINATED.</p>
</body></html>'''

    out_html = f'{SCAN_DIR}/lhm_universe_scan_report.html'
    with open(out_html, 'w') as f:
        f.write(html)
    print(f'HTML -> {out_html}')


def main():
    csv = f'{SCAN_DIR}/lhm_universe_scan_full.csv'
    if not os.path.exists(csv):
        print(f'No scan output at {csv}')
        return
    df = pd.read_csv(csv)
    print(f'Loaded {len(df)} rows')

    charts = {}
    charts['top_stocks'] = render_top_table(df, 'stock', n=30,
        save_path=f'{SCAN_DIR}/top_stocks.png')
    charts['top_etfs'] = render_top_table(df, 'etf', n=20,
        save_path=f'{SCAN_DIR}/top_etfs.png')
    charts['summary'] = render_category_summary(df,
        save_path=f'{SCAN_DIR}/score_distribution.png')
    render_html(df, charts)

    print(f'\nSummary:')
    print(f'  Total scored: {len(df)}')
    print(f'  Stocks: {(df.kind == "stock").sum()}')
    print(f'  ETFs: {(df.kind == "etf").sum()}')
    print(f'  GREEN regime: {(df.regime == "GREEN").sum()}')
    print(f'  Score >= 7: {(df.score >= 7).sum()}')
    print(f'  Score >= 6: {(df.score >= 6).sum()}')


if __name__ == '__main__':
    main()
