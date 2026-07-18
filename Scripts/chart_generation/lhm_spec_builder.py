"""LHM Spec-Driven Chart Builder
================================
One engine that turns a JSON spec into a branded LHM chart pulled live from Lighthouse_Master.db.

Use it for:
  - Rebuilding a third-party research chart from OUR primary data (find the series, write a spec).
  - Standing up specialty analytics on request (z-scores, spreads, ratios, lead/lag, rolling corr,
    forward-return studies, price+MA security charts).

Run:   python3 lhm_spec_builder.py <specs.json> [--out DIR]
Spec file = a JSON list of chart specs. See Working/chart_intake/README.md for the full field guide
and Working/chart_intake/example_specs.json for worked examples.

Every chart is rendered on the canonical lhm_chart_template, QC-ready, images only.
"""
import sys, os, json, sqlite3, argparse
sys.path.insert(0, '/Users/bob/LHM/Scripts/chart_generation')
import pandas as pd, numpy as np
from lhm_chart_template import (COLORS, set_theme, new_fig, style_single_ax, style_dual_ax,
    add_last_value_label, add_recessions, set_xlim_to_data, add_annotation_box, brand_fig,
    save_fig, align_yaxis_zero, add_smart_legend)
import matplotlib.pyplot as plt

DB = '/Users/bob/LHM/Data/databases/Lighthouse_Master.db'
DEEP = '#123456'
_c = sqlite3.connect(DB)

def series(sid, start=None, end=None):
    df = pd.read_sql_query("SELECT date,value FROM observations WHERE series_id=? ORDER BY date", _c, params=(sid,))
    if df.empty: raise KeyError(f"series {sid} not in DB")
    df['date'] = pd.to_datetime(df['date']); x = df.set_index('date')['value'].dropna()
    if start: x = x[x.index >= start]
    if end:   x = x[x.index <= end]
    return x

def yoy(x):  return ((x / x.shift(12) - 1) * 100).dropna()
def mom(x):  return (x.diff()).dropna()
def ma(x,n): return x.rolling(n).mean().dropna()

def _transform(sid, tf, scale=1.0, start='1990-01-01'):
    x = series(sid, start) * scale
    if tf in (None, 'level'): return x
    if tf == 'yoy':  return yoy(series(sid, '1988-01-01')) * (scale if scale != 1 else 1)
    if tf == 'mom':  return mom(x)
    if tf.startswith('ma'):  return ma(series(sid, '1988-01-01'), int(tf[2:]))
    if tf == 'zscore':
        z = (x - x.rolling(252, min_periods=60).mean()) / x.rolling(252, min_periods=60).std()
        return z.dropna()
    raise ValueError(f"unknown transform {tf}")

def build_one(spec, outdir):
    post = spec.get('post', 'misc'); fn = spec['fname']
    d = os.path.join(outdir, post); os.makedirs(d, exist_ok=True)
    kind = spec['kind']; start = spec.get('start', '2000-01-01')
    title, sub, src = spec['title'], spec.get('subtitle', ''), spec.get('source', 'FRED')
    fmt = spec.get('fmt', '{:.1f}')
    fig, ax = new_fig(figsize=tuple(spec.get('figsize', [14, 8])))
    dd = None
    try:
        if kind in ('level', 'yoy', 'mom', 'zscore', 'transform'):
            tf = spec.get('transform', 'level' if kind == 'transform' else kind)
            x = _transform(spec['series'], tf, spec.get('scale', 1.0), start='1988-01-01')
            x = x[x.index >= start]
            ax.plot(x.index, x.values, color=COLORS['ocean'], linewidth=2.6)
            if spec.get('zero_line', kind in ('yoy', 'zscore')):
                ax.axhline(0, color=COLORS['fog'], linestyle='--', linewidth=1.0, zorder=0)
            if kind == 'zscore':
                for lv in (2, -2): ax.axhline(lv, color=COLORS['venus'], linewidth=0.9, alpha=0.7)
            style_single_ax(ax, fmt=fmt); add_last_value_label(ax, x, COLORS['ocean'], fmt=fmt, side='right'); dd = x.index[-1]
        elif kind == 'spread':  # a - b (optionally b transformed)
            a = _transform(spec['a'], spec.get('a_tf', 'level'), start='1988-01-01')
            b = _transform(spec['b'], spec.get('b_tf', 'level'), start='1988-01-01')
            x = (a - b).dropna(); x = x[x.index >= start]
            ax.plot(x.index, x.values, color=COLORS['ocean'], linewidth=2.6)
            ax.axhline(0, color=spec.get('zero_color', COLORS['fog']), linestyle='--', linewidth=1.0, zorder=0)
            style_single_ax(ax, fmt=fmt); add_last_value_label(ax, x, COLORS['ocean'], fmt=fmt, side='right'); dd = x.index[-1]
        elif kind == 'ratio':  # (a/b)*mult
            a = series(spec['a']); b = series(spec['b']); x = ((a / b) * spec.get('mult', 1.0)).dropna(); x = x[x.index >= start]
            ax.plot(x.index, x.values, color=COLORS['ocean'], linewidth=2.6)
            style_single_ax(ax, fmt=fmt); add_last_value_label(ax, x, COLORS['ocean'], fmt=fmt, side='right'); dd = x.index[-1]
        elif kind == 'dual':  # a = Ocean primary (right axis, ax2); b = Dusk secondary (left axis, ax)
            import matplotlib.ticker as mticker
            a = _transform(spec['a'], spec.get('a_tf', 'level'), start='1988-01-01'); a = a[a.index >= start]
            b = _transform(spec['b'], spec.get('b_tf', 'level'), start='1988-01-01'); b = b[b.index >= start]
            ax2 = ax.twinx()
            ax.plot(b.index, b.values, color=COLORS['dusk'], linewidth=2.4, label=spec.get('b_label', spec['b']))
            ax2.plot(a.index, a.values, color=COLORS['ocean'], linewidth=2.4, label=spec.get('a_label', spec['a']))
            style_dual_ax(ax, ax2, COLORS['dusk'], COLORS['ocean'])  # c1=left(dusk), c2=right(ocean)
            fa = spec.get('fmt_a', fmt); fb = spec.get('fmt_b', fmt)
            ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, p: fa.format(v)))
            ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, p: fb.format(v)))
            add_last_value_label(ax2, a, COLORS['ocean'], fmt=fa, side='right')
            add_last_value_label(ax, b, COLORS['dusk'], fmt=fb, side='left')
            if spec.get('align_zero'): align_yaxis_zero(ax, ax2)
            add_smart_legend(ax); dd = a.index[-1]
        elif kind == 'price':  # security convention: Deep px + Dusk 50d + Ocean 200d, log
            px = series(spec['series'] + '_Close', start)
            full = series(spec['series'] + '_Close')
            ax.plot(px.index, px.values, color=DEEP, linewidth=2.0, label=spec['series'])
            ax.plot(full.rolling(50).mean()[px.index].index, full.rolling(50).mean()[px.index].values, color=COLORS['dusk'], linewidth=1.6, label='50-day')
            ax.plot(full.rolling(200).mean()[px.index].index, full.rolling(200).mean()[px.index].values, color=COLORS['ocean'], linewidth=1.6, label='200-day')
            if spec.get('log', True): ax.set_yscale('log')
            style_single_ax(ax, fmt=fmt); add_last_value_label(ax, px, DEEP, fmt=fmt, side='right'); add_smart_legend(ax); dd = px.index[-1]
        elif kind == 'rs':  # relative strength (a/bench)*100
            a = series(spec['series'] + '_Close'); b = series(spec.get('bench', 'SPY') + '_Close')
            x = ((a / b) * 100).dropna(); x = x[x.index >= start]
            ax.plot(x.index, x.values, color=COLORS['ocean'], linewidth=2.4)
            style_single_ax(ax, fmt=fmt); add_last_value_label(ax, x, COLORS['ocean'], fmt=fmt, side='right'); dd = x.index[-1]
        else:
            raise ValueError(f"unknown kind {kind}")
        if spec.get('recessions', True) and kind not in ('price', 'rs'):
            add_recessions(ax)
        set_xlim_to_data(ax, (x.index if 'x' in dir() else a.index))
        if spec.get('annotation'):
            add_annotation_box(ax, spec['annotation'])
        brand_fig(fig, title=title, subtitle=sub, source=src, data_date=dd)
        path = os.path.join(d, fn + '.png'); save_fig(fig, path)
        return ('ok', f"{post}/{fn}")
    except Exception as e:
        plt.close('all'); return ('fail', f"{post}/{fn}: {type(e).__name__} {e}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('specs'); ap.add_argument('--out', default='/Users/bob/LHM/Working/chart_regen/spec_output')
    a = ap.parse_args()
    set_theme('white')
    specs = json.load(open(a.specs))
    ok, fail = [], []
    for sp in specs:
        st, msg = build_one(sp, a.out)
        (ok if st == 'ok' else fail).append(msg)
    print(f"BUILT {len(ok)} / {len(specs)} -> {a.out}")
    for m in ok: print("  +", m)
    for m in fail: print("  x", m)

if __name__ == '__main__':
    main()
