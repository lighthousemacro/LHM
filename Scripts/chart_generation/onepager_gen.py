"""LHM Indicator One-Pagers (Prometheus-style) — full build
==========================================================
Every indicator gets a card + branded chart. DESCRIPTIVE/composite = annotated history (recession bands
+ major-turn era labels). The 5 nowcasts = OURS vs the realized series we predict (skill overlay).
Assembles a browsable HTML gallery. Run: python3 onepager_gen.py
"""
import sys, sqlite3, os, json, html
sys.path.insert(0, '/Users/bob/LHM/Scripts/chart_generation')
import pandas as pd, numpy as np
import matplotlib; matplotlib.use("Agg")
from lhm_chart_template import (COLORS, set_theme, new_fig, style_single_ax, add_last_value_label,
    add_recessions, set_xlim_to_data, brand_fig, save_fig, add_smart_legend)
import matplotlib.pyplot as plt
DB='/Users/bob/LHM/Data/databases/Lighthouse_Master.db'
D='/Users/bob/LHM/Working/db_overview'; OUT=f'{D}/onepagers'; os.makedirs(OUT,exist_ok=True)
c=sqlite3.connect(DB); set_theme('white'); DEEP='#123456'
META={x['id']:x for x in json.load(open(f'{D}/batch_a.json'))+json.load(open(f'{D}/batch_b.json'))}
NCS={x['id']:x for x in json.load(open(f'{D}/nowcast_summary.json'))}

def s(sid, ind=False):
    tbl,col=('lighthouse_indices','index_id') if ind else ('observations','series_id')
    df=pd.read_sql_query(f"SELECT date,value FROM {tbl} WHERE {col}=? ORDER BY date",c,params=(sid,))
    if df.empty: return None
    df['date']=pd.to_datetime(df['date']); return df.set_index('date')['value'].dropna()

ERAS=[("2008-09-15","GFC / Lehman"),("2011-08-01","EU debt · US downgrade"),
      ("2015-12-01","Industrial recession"),("2018-12-01","Vol-mageddon / QT"),
      ("2020-03-01","COVID shock"),("2022-06-01","Fastest hikes in 40y"),("2025-04-01","Tariff shock")]

ORDINAL={'LIQ_STAGE','WARNING_LEVEL'}  # regime stages — never smooth
def descriptive_card(iid):
    x=s(iid,ind=True)
    if x is None or len(x)<50: return None
    x=x[x.index>='2000-01-01']
    m=META.get(iid,{})
    # noisy z-score composites get a 3-month MA (standing rule); ordinal stages stay raw
    chop=float(np.std(np.diff(x.values[-2500:]))/(np.std(x.values[-2500:])+1e-9))
    smoothed = chop>0.13 and iid not in ORDINAL
    fig,ax=new_fig(figsize=(14,8))
    if smoothed:
        xs=x.rolling(63,min_periods=20).mean().dropna()
        ax.plot(x.index,x.values,color=COLORS['sky'],linewidth=0.8,alpha=0.35,label='raw')
        ax.plot(xs.index,xs.values,color=COLORS['ocean'],linewidth=2.4,label='3-month average')
        x=xs
    else:
        ax.plot(x.index,x.values,color=COLORS['ocean'],linewidth=2.1)
    ax.axhline(0,color=COLORS['fog'],linestyle='--',linewidth=1.0,zorder=0)
    style_single_ax(ax,fmt='{:.2f}'); add_last_value_label(ax,x,COLORS['ocean'],fmt='{:.2f}',side='right')
    set_xlim_to_data(ax,x.index); add_recessions(ax)
    med=x.median()
    for dt,lbl in ERAS:
        d=pd.Timestamp(dt)
        if d<x.index.min() or d>x.index.max(): continue
        yv=x.reindex([d],method='nearest').iloc[0]
        ax.annotate(lbl,xy=(d,yv),xytext=(0,26 if yv<med else -26),textcoords='offset points',
                    fontsize=8,color=DEEP,ha='center',fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.28',fc='white',ec=COLORS['ocean'],lw=1,alpha=0.92),
                    arrowprops=dict(arrowstyle='-',color=COLORS['dusk'],lw=1.1))
    if smoothed: add_smart_legend(ax)
    sub=(m.get('describes','') or '')[:104] + (" · 3-month average" if smoothed else "")
    brand_fig(fig,title=m.get('full_name',iid),subtitle=sub,source="Lighthouse Macro",data_date=x.index[-1])
    p=f"{OUT}/{iid}.png"; save_fig(fig,p); plt.close('all'); return p

def predictive_card(ncid):
    nc=NCS[ncid]; ours=s(ncid)
    tmap={'LHM_GDP_NOWCAST':('GDPC1',4),'LHM_LABOR_NOWCAST':('PAYEMS',12),'LHM_INDPRO_NOWCAST':('INDPRO',12),
          'LHM_HOUSING_NOWCAST':('CSUSHPINSA',12),'LHM_INFLATION_NOWCAST':('CPILFESL',12)}
    tgt_id,ppy=tmap[ncid]; tgt=s(tgt_id); realized=(tgt.pct_change(ppy)*100).dropna()
    fitted=s(ncid.replace('_NOWCAST','_FITTED'))  # full fitted history (ours across all time)
    realized=realized[realized.index>='2010-01-01']
    ours_full = fitted[fitted.index>='2010-01-01'] if fitted is not None else ours[ours.index>='2010-01-01']
    fig,ax=new_fig(figsize=(14,8))
    ax.plot(realized.index,realized.values,color=DEEP,linewidth=2.3,label='Realized print')
    ax.plot(ours_full.index,ours_full.values,color=COLORS['ocean'],linewidth=2.0,label='LHM Nowcast (ours)')
    ours=ours_full
    ax.axhline(0,color=COLORS['fog'],linestyle='--',linewidth=1.0,zorder=0)
    style_single_ax(ax,fmt='{:.1f}%'); add_last_value_label(ax,ours,COLORS['ocean'],fmt='{:.1f}%',side='right')
    set_xlim_to_data(ax,realized.index); add_recessions(ax); add_smart_legend(ax)
    brand_fig(fig,title=nc['label']+" — LHM Nowcast",subtitle=f"Ours vs realized  ·  {nc['tier']}  ·  OOS R²={nc.get("oos_r2")} · correlation {nc["oos_r"]} · dir {int(nc['dir_hit']*100)}%",
              source="LHM Nowcast Model",data_date=ours.index[-1])
    p=f"{OUT}/{ncid}.png"; save_fig(fig,p); plt.close('all'); return p

# build all
built=[]
for iid in META:
    try:
        p=descriptive_card(iid)
        if p: built.append(('desc',iid,p))
    except Exception as e: print("desc fail",iid,e)
for ncid in NCS:
    try:
        p=predictive_card(ncid); built.append(('pred',ncid,p))
    except Exception as e: print("pred fail",ncid,e)
print(f"built {len(built)} one-pager charts")

# assemble gallery HTML
def esc(x): return html.escape(str(x)) if x is not None else ''
cards=""
# nowcasts first (the flashy predictive ones), then composites
order=[b for b in built if b[0]=='pred']+[b for b in built if b[0]=='desc']
for kind,iid,p in order:
    fn=os.path.basename(p)
    if kind=='pred':
        nc=NCS[iid]; badge=nc['tier']; bc={'STRONG':'#00BB89','USABLE':'#2389BB','NOT READY':'#FF2389'}.get(badge,'#898989')
        meta=f"<span class='b' style='background:{bc}'>{badge} · R² {nc.get('oos_r2')}</span> <span class='k'>Predictive nowcast (ours vs realized)</span>"
        title=nc['label']+" Nowcast"; body=f"Proxy basket: {esc(nc['basket'])}"
    else:
        m=META.get(iid,{}); cls=m.get('classification','')
        bc='#FF2389' if 'predict' in cls else '#898989'
        meta=f"<span class='b' style='background:{bc}'>{esc(cls)}</span> <span class='k'>{esc(m.get('relationship_type',''))}</span>"
        title=m.get('full_name',iid); body=f"<b>Formula:</b> {esc(m.get('formula',''))[:220]}<br><b>Reads:</b> {esc(m.get('describes',''))}"
    cards+=f"""<div class="card"><div class="ct"><span class="id">{esc(iid)}</span><span class="tt">{esc(title)}</span></div>
      <div class="mt">{meta}</div><img src="onepagers/{esc(fn)}" loading="lazy">
      <div class="bd">{body}</div></div>"""

HTML=f"""<!doctype html><html><head><meta charset="utf-8"><title>LHM Indicator One-Pagers</title><style>
body{{font-family:-apple-system,Inter,sans-serif;background:#F4F7F9;color:#123456;margin:0;padding:0 0 60px}}
header{{background:#123456;color:#fff;padding:22px 30px;border-bottom:5px solid #2389BB}}
header .bar{{height:5px;background:linear-gradient(90deg,#2389BB 0 66%,#FF6723 66%);margin:-18px -30px 16px}}
h1{{margin:0;font-size:24px}} .sub{{color:#89CCFF;font-style:italic;font-size:14px}}
.wrap{{max-width:1500px;margin:0 auto;padding:20px 22px}}
.grid{{display:grid;grid-template-columns:1fr 1fr;gap:22px}}
.card{{background:#fff;border:1px solid #dce6ee;border-radius:12px;padding:14px;box-shadow:0 1px 4px rgba(18,52,86,.05)}}
.ct{{display:flex;align-items:baseline;gap:10px}} .ct .id{{font-family:'Source Code Pro',monospace;font-weight:800;color:#2389BB;font-size:12px}}
.ct .tt{{font-weight:700;font-size:15px}} .mt{{margin:5px 0 8px}}
.b{{color:#fff;font-size:10px;font-weight:800;padding:2px 8px;border-radius:5px;text-transform:uppercase}}
.k{{color:#898989;font-size:11px;text-transform:uppercase;letter-spacing:.4px}}
.card img{{width:100%;border-radius:8px;border:1px solid #eef3f7}} .bd{{font-size:12px;color:#33475a;margin-top:8px;line-height:1.5}}
.bd b{{color:#123456}}
</style></head><body><header><div class="bar"></div>
<h1>Lighthouse Macro — Indicator One-Pagers</h1><div class="sub">{len(order)} cards · nowcasts (ours vs realized) + composites (annotated history) · MACRO, ILLUMINATED.</div></header>
<div class="wrap"><div class="grid">{cards}</div></div></body></html>"""
open(f"{D}/LHM_INDICATOR_ONEPAGERS.html","w").write(HTML)
print("wrote LHM_INDICATOR_ONEPAGERS.html")
