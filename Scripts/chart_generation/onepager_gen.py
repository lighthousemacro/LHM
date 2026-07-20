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
from lhm_chart_template import (COLORS, set_theme, new_fig, style_single_ax, style_dual_ax,
    add_last_value_label, add_recessions, set_xlim_to_data, brand_fig, save_fig, add_smart_legend)
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

def _cadence_win(x):
    """3-month smoothing window in native cadence: 63 obs for daily, 3 for monthly."""
    gap=x.index.to_series().diff().dt.days.median()
    return 3 if (gap or 1)>20 else 63

def _three_mo(x):
    w=_cadence_win(x)
    return x.rolling(w,min_periods=max(2,w//3)).mean().dropna()

def _monthly_map(t):
    return {(d.year,d.month):v for d,v in t.items()}

def _date_aware_12m(t, mode):
    """12-calendar-month YoY %% ('yoy') or 12-month difference in pp ('chg12'). Gap months -> dropped."""
    mm=_monthly_map(t); out={}
    for d,v in t.items():
        base=mm.get((d.year-1,d.month))
        if base is None: continue
        if mode=='yoy':
            if base==0: continue
            out[d]=(v/base-1.0)*100.0
        else:
            out[d]=v-base
    r=pd.Series(out); r.index=pd.to_datetime(r.index); return r.sort_index()

# CLI-style predictive overlays: indicator (3m avg) vs the thing it predicts, shifted
# by the documented lead. One target, one horizon (middle of the documented range).
# kind: 'yoy' 12m %% change | 'chg12' 12m diff (pp) | 'fwd' forward n-trading-day return
OVERLAYS={
  'LPI':('UNRATE','chg12',6,'Unemployment rate, 12m change (pp), led 6m'),
  'LFI':('UNRATE','chg12',6,'Unemployment rate, 12m change (pp), led 6m'),
  'PCI':('CPIAUCSL','yoy',15,'CPI YoY %, led 15m'),
  'GCI':('INDPRO','yoy',3,'Industrial production YoY %, led 3m'),
  'HCI':('HOUST','yoy',7,'Housing starts YoY %, led 7m'),
  'CCI':('PCEC96','yoy',2,'Real PCE YoY %, led 2m'),
  'BCI':('NEWORDER','yoy',6,'Core capex orders YoY %, led 6m'),
  'TCI':('EEM_Close','yoy',4,'EM equities YoY %, led 4m'),
  'FCI':('UNRATE','chg12',7,'Unemployment rate, 12m change (pp), led 7m'),
  'CLG':('UNRATE','chg12',7,'Unemployment rate, 12m change (pp), led 7m'),
  'LCI':('SPY_Close','fwd',21,'SPY forward 21d return %'),
  'MSI':('SPY_Close','fwd',63,'SPY forward 63d return %'),
  'SBD':('SPY_Close','fwd',63,'SPY forward 63d return %'),
  'SPI':('SPY_Close','fwd',21,'SPY forward 21d return %'),
  'SSD':('SPY_Close','fwd',21,'SPY forward 21d return %'),
  'MRI':('INDPRO','yoy',9,'Industrial production YoY %, led 9m'),
  'CLI':('CRYPTO_BTC_PRICE','fwd',21,'BTC forward 21d return %'),
  # ALLOC family (Bob 7/20): rolling H-period target return/change, led H, per validated spec
  'ALLOC_CONS_ROTATION':('XLY_Close/XLP_Close','rollret',3,'XLY/XLP rolling 3m return %, led 3m'),
  'ALLOC_CYCLICAL_DEFENSIVE':('XLI_Close/XLP_Close','rollret',3,'XLI/XLP rolling 3m return %, led 3m'),
  'ALLOC_ENERGY_MOMENTUM':('XLE_Close/SPY_Close','rollret',3,'XLE/SPY rolling 3m return %, led 3m'),
  'ALLOC_INCOME_DEPLETION':('XLY_Close/XLP_Close','rollret',6,'XLY/XLP rolling 6m return %, led 6m'),
  'ALLOC_INVENTORY_DESTOCK':('XLB_Close/SPY_Close','rollret',6,'XLB/SPY rolling 6m return %, led 6m'),
  'ALLOC_DOLLAR_EM':('EEM_Close','rollret',6,'EEM rolling 6m return %, led 6m (inverse signal)'),
  'ALLOC_REALYIELD_GOLD':('GLD_Close','rollret',6,'GLD rolling 6m return %, led 6m'),
  'ALLOC_CREDIT_LABOR_GAP':('BAMLH0A0HYM2','rollchg',6,'HY OAS rolling 6m change (pp), led 6m'),
  'ALLOC_CURVE_STEEPENER':('T10Y2Y','rollchg',6,'2s10s rolling 6m change (pp), led 6m'),
  'SLI':('CRYPTO_BTC_PRICE','fwd',21,'BTC forward 21d return %'),
}

def overlay_card(iid):
    """Indicator (3m avg, RHS Ocean) vs its led target (LHS Dusk), CLI convention."""
    x=s(iid,ind=True)
    if x is None or len(x)<50: return None
    tgt_id,kind,lead,tlabel=OVERLAYS[iid]
    if '/' in tgt_id:
        num,den=tgt_id.split('/'); a=s(num); b=s(den)
        if a is None or b is None: return None
        t=(a/b.reindex(a.index).ffill()).dropna()
    else:
        t=s(tgt_id)
    if t is None: return None
    xs=_three_mo(x[x.index>='2000-01-01'])
    if kind=='fwd':
        led=((t.shift(-lead)/t-1.0)*100.0).dropna()
    elif kind in ('rollret','rollchg'):
        hd={3:63,6:126}[lead]
        roll=((t/t.shift(hd)-1.0)*100.0) if kind=='rollret' else (t-t.shift(hd))
        led=roll.dropna()
        led.index=led.index-pd.DateOffset(months=lead)
    else:
        led=_date_aware_12m(t,kind)
        led.index=led.index-pd.DateOffset(months=lead)
    # clip only the START to the common window; the indicator runs to its latest print
    # (the led target ends ~lead ago by construction, CLI convention)
    lo=max(xs.index.min(),led.index.min())
    xs=xs[xs.index>=lo]; led=led[led.index>=lo]
    if len(xs)<30 or len(led)<30: return None
    m=META.get(iid,{})
    fig,ax=new_fig(figsize=(14,8))
    ax2=ax.twinx()
    l1,=ax.plot(led.index,led.values,color=COLORS['dusk'],linewidth=1.7,label=tlabel)
    l2,=ax2.plot(xs.index,xs.values,color=COLORS['ocean'],linewidth=2.4,label=f'{iid} 3m avg, z')
    style_dual_ax(ax,ax2,COLORS['dusk'],COLORS['ocean'])
    ax2.axhline(0,color=COLORS['fog'],linestyle='--',linewidth=1.0,zorder=0)
    add_last_value_label(ax2,xs,COLORS['ocean'],fmt='{:.2f}',side='right')
    span=xs.index if xs.index.max()>=led.index.max() else led.index
    set_xlim_to_data(ax,span); add_recessions(ax)
    ax.legend(handles=[l2,l1],loc='upper left',fontsize=9,framealpha=0.9)
    brand_fig(fig,title=f"{m.get('full_name',iid)} vs What It Predicts",
              subtitle=f"{iid} 3m avg (RHS) vs {tlabel} (LHS)",
              source="LHM calculations; FRED + market data",data_date=xs.index[-1])
    p=f"{OUT}/{iid}.png"; save_fig(fig,p); plt.close('all'); return p

def descriptive_card(iid):
    x=s(iid,ind=True)
    if x is None or len(x)<50: return None
    x=x[x.index>='2000-01-01']
    m=META.get(iid,{})
    # every composite reads off the 3-month average (Bob 7/20: z off the 3m, for all of them);
    # ordinal regime stages stay raw
    smoothed = iid not in ORDINAL
    fig,ax=new_fig(figsize=(14,8))
    if smoothed:
        xs=_three_mo(x)
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
        if iid in OVERLAYS:
            p=overlay_card(iid)
            if p: built.append(('ovl',iid,p)); continue
            print("overlay fell back to plain:",iid)
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

# four canonical types (Bob, 2026-07-20): actionable first.
# Nowcast cards predict real-economy releases, so they sit in RealBC.
TYPE_ORDER = ["TAA", "RealBC", "Market Structure", "Descriptive"]
TYPE_DISPLAY = {"TAA": "Alloc"}  # Bob 7/20: display label
TYPE_SUB = {
    "TAA": "Alloc. Tactical asset allocation, validated or provisional signals on asset targets.",
    "RealBC": "Real business cycle. Macro impact, regime, and the nowcasts.",
    "Market Structure": "The state of the market itself. Structure and sentiment reads.",
    "Descriptive": "Honest state reads. Combined-metric measurements, no forward claim.",
}
def card_type(kind, iid):
    if kind == 'pred':
        return "RealBC"
    return META.get(iid, {}).get('type', 'Descriptive')

cards=""
# within each type: nowcasts first, then predictive overlays, then plain composites
order=[]
for _t in TYPE_ORDER:
    for _kind_pass in ('pred', 'ovl', 'desc'):
        order += [b for b in built if b[0] == _kind_pass and card_type(b[0], b[1]) == _t]

_open_section = None
for kind,iid,p in order:
    _t = card_type(kind, iid)
    if _t != _open_section:
        if _open_section is not None:
            cards += "</div></div>"  # close grid + sect
        n_sec = sum(1 for b in order if card_type(b[0], b[1]) == _t)
        cards += (f"<div class='sect'><div class='sh'><span class='shn'>{esc(TYPE_DISPLAY.get(_t, _t))}</span>"
                  f"<span class='shc'>{n_sec} cards</span>"
                  f"<span class='shs'>{esc(TYPE_SUB[_t])}</span></div>")
        cards += "<div class='grid'>"
        _open_section = _t
    fn=os.path.basename(p)
    if kind=='pred':
        nc=NCS[iid]; badge=nc['tier']; bc={'STRONG':'#00BB89','USABLE':'#2389BB','NOT READY':'#FF2389'}.get(badge,'#898989')
        meta=f"<span class='b' style='background:{bc}'>{badge} · R² {nc.get('oos_r2')}</span> <span class='k'>Predictive nowcast (ours vs realized)</span>"
        title=nc['label']+" Nowcast"; body=f"Proxy basket: {esc(nc['basket'])}"
    elif kind=='ovl':
        m=META.get(iid,{}); _,_,lead,tlabel=OVERLAYS[iid]
        import re as _re
        _ic=_re.search(r'OOS IC ([+\-]?[0-9.]+), n=(\d+)', m.get('lead_lag','') or '')
        _cred=f" <span class='b' style='background:#00BB89'>OOS IC {_ic.group(1)} · n={_ic.group(2)}</span>" if _ic else ''
        meta=f"<span class='b' style='background:#FF6723'>PREDICTIVE OVERLAY</span>{_cred} <span class='k'>{esc(tlabel)}</span>"
        title=m.get('full_name',iid)
        body=f"<b>Overlay:</b> {esc(iid)} 3m avg vs {esc(tlabel)}<br><b>Reads:</b> {esc(m.get('describes',''))}"
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
.sect{{margin:26px 0 6px}}
.sh{{display:flex;align-items:baseline;gap:14px;border-bottom:3px solid #2389BB;padding:6px 2px;margin-bottom:16px}}
.shn{{font-weight:800;font-size:18px;color:#123456;text-transform:uppercase;letter-spacing:1.2px}}
.shc{{font-family:'Source Code Pro',monospace;font-size:11px;color:#2389BB;font-weight:700}}
.shs{{font-size:12px;color:#898989;font-style:italic}}
</style></head><body><header><div class="bar"></div>
<h1>Lighthouse Macro — Indicator One-Pagers</h1><div class="sub">{len(order)} cards · nowcasts (ours vs realized) + composites (annotated history) · MACRO, ILLUMINATED.</div></header>
<div class="wrap">{cards}{"</div></div>" if cards else ""}</div></body></html>"""
open(f"{D}/LHM_INDICATOR_ONEPAGERS.html","w").write(HTML)
print("wrote LHM_INDICATOR_ONEPAGERS.html")
