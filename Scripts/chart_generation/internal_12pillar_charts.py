#!/usr/bin/env python3
"""Internal 12-pillar read: ARTICLE-GRADE charts via the canonical LHM template,
plus a branded scorecard PNG for the master section. No on-chart callout boxes;
descriptive captions live in the HTML. Last-value pills are standard chart chrome.
"""
import sqlite3, json, os, sys
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

sys.path.insert(0,"/Users/bob/LHM/Scripts/chart_generation")
from lhm_chart_template import (
    COLORS, set_theme, new_fig, style_ax, style_single_ax, style_dual_ax,
    add_last_value_label, add_recessions, set_xlim_to_data, legend_style,
    brand_fig, save_fig, _add_border, align_yaxis_smart,
)

DB="/Users/bob/LHM/Data/databases/Lighthouse_Master.db"
OUT="/Users/bob/LHM/Outputs/pillar_charts"
os.makedirs(OUT,exist_ok=True)
set_theme("white")
FIGSIZE=(10.6,6.1)
DPI=150
con=sqlite3.connect(DB)

def _save(fig,fname):
    _add_border(fig)
    fig.savefig(os.path.join(OUT,fname),dpi=DPI,bbox_inches="tight",
                pad_inches=0.025,facecolor="white",edgecolor="none")
    plt.close(fig)

def load(sid):
    df=pd.read_sql("select date,value from observations where series_id=? order by date",con,params=(sid,))
    if df.empty: return pd.Series(dtype=float)
    s=pd.Series(df.value.values,index=pd.to_datetime(df.date)).dropna()
    return s[~s.index.duplicated(keep="last")].sort_index()

def idx(iid):
    df=pd.read_sql("select date,value from lighthouse_indices where index_id=? order by date",con,params=(iid,))
    if df.empty: return pd.Series(dtype=float)
    s=pd.Series(df.value.values,index=pd.to_datetime(df.date)).dropna()
    return s[~s.index.duplicated(keep="last")].sort_index()

def yoy(s,p=12):
    m=s.resample("ME").last(); return (m/m.shift(p)-1.0)*100.0

def disp(s,start):
    return s if start is None else s[s.index>=pd.to_datetime(start)]

readings={}
def rec(name,s,unit="",dp=2):
    if s is None or len(s)==0: readings[name]={"last":None}; return
    last=float(s.iloc[-1]); dt=s.index[-1].strftime("%Y-%m-%d"); prev=None
    try:
        yr=s[s.index<=s.index[-1]-pd.Timedelta(days=365)]; prev=float(yr.iloc[-1]) if len(yr) else None
    except Exception: pass
    readings[name]={"last":round(last,dp),"date":dt,"yr_ago":(round(prev,dp) if prev is not None else None),
                    "chg_1y":(round(last-prev,dp) if prev is not None else None),"unit":unit}

def hbands(ax,levels,c=None):
    c=c or COLORS["doldrums"]
    for lv in levels: ax.axhline(lv,color=c,lw=0.8,ls=":",zorder=1)

# ---------- chart builders ----------
def zchart(series,title,subtitle,source,fname,smooth=90,start="2010-01-01",recess=True,fmt="{:.2f}"):
    if series is None or len(series)==0: return
    sm=series.rolling(f"{smooth}D").mean()
    d=disp(sm,start)
    if len(d)==0: d=sm
    fig,ax=new_fig(FIGSIZE); style_single_ax(ax,fmt=fmt)
    if recess: add_recessions(ax,start_date=d.index.min())
    ax.axhline(0,color=COLORS["fog"],lw=1.0,ls="--",zorder=1)
    hbands(ax,[1.96,-1.96])
    ax.plot(d.index,d.values,color=COLORS["ocean"],lw=2.0,zorder=3)
    ax.set_ylabel("z-score")
    add_last_value_label(ax,d,COLORS["ocean"],fmt=fmt)
    set_xlim_to_data(ax,d.index)
    brand_fig(fig,title,subtitle=subtitle,source=source,data_date=series.index.max())
    _save(fig,fname)

def linechart(series,title,subtitle,source,fname,color=None,start="2005-01-01",recess=True,
              ylabel="",bands=None,fmt="{:.1f}"):
    if series is None or len(series)==0: return
    color=color or COLORS["ocean"]; d=disp(series,start)
    fig,ax=new_fig(FIGSIZE); style_single_ax(ax,fmt=fmt)
    if recess: add_recessions(ax,start_date=d.index.min())
    if bands: hbands(ax,bands)
    ax.plot(d.index,d.values,color=color,lw=2.0,zorder=3)
    if ylabel: ax.set_ylabel(ylabel)
    add_last_value_label(ax,d,color,fmt=fmt)
    set_xlim_to_data(ax,d.index)
    brand_fig(fig,title,subtitle=subtitle,source=source,data_date=series.index.max())
    _save(fig,fname)

def twolines(s1,s2,title,subtitle,source,fname,l1,l2,c1=None,c2=None,start="2005-01-01",
             recess=True,ylabel="",bands=None,zero=False,fmt="{:.1f}"):
    c1=c1 or COLORS["ocean"]; c2=c2 or COLORS["dusk"]
    d1=disp(s1,start) if s1 is not None else None
    d2=disp(s2,start) if s2 is not None else None
    fig,ax=new_fig(FIGSIZE); style_single_ax(ax,fmt=fmt)
    if recess: add_recessions(ax,start_date=(d1.index.min() if d1 is not None and len(d1) else start))
    if zero: ax.axhline(0,color=COLORS["fog"],lw=1.0,ls="--",zorder=1)
    if bands: hbands(ax,bands)
    if d1 is not None and len(d1): ax.plot(d1.index,d1.values,color=c1,lw=2.0,label=l1,zorder=3)
    if d2 is not None and len(d2): ax.plot(d2.index,d2.values,color=c2,lw=2.0,label=l2,zorder=3)
    if ylabel: ax.set_ylabel(ylabel)
    if d1 is not None and len(d1): add_last_value_label(ax,d1,c1,fmt=fmt)
    if d2 is not None and len(d2): add_last_value_label(ax,d2,c2,fmt=fmt)
    leg=ax.legend(loc="upper left",fontsize=10,**legend_style());
    idxs=[x.index for x in (d1,d2) if x is not None and len(x)]
    set_xlim_to_data(ax,*idxs)
    dd=max([s.index.max() for s in (s1,s2) if s is not None and len(s)])
    brand_fig(fig,title,subtitle=subtitle,source=source,data_date=dd)
    _save(fig,fname)

def dualchart(s1,s2,title,subtitle,source,fname,l1,l2,c1=None,c2=None,start="2005-01-01",
              recess=True,fmt1="{:.0f}",fmt2="{:.1f}"):
    c1=c1 or COLORS["ocean"]; c2=c2 or COLORS["dusk"]
    d1=disp(s1,start); d2=disp(s2,start)
    fig,ax=new_fig(FIGSIZE); ax2=ax.twinx()
    style_dual_ax(ax,ax2,c1,c2)
    if recess: add_recessions(ax,start_date=d1.index.min())
    ax.plot(d1.index,d1.values,color=c1,lw=2.0,zorder=3)
    ax2.plot(d2.index,d2.values,color=c2,lw=2.0,zorder=3)
    ax.set_ylabel(l1,color=c1); ax2.set_ylabel(l2,color=c2)
    align_yaxis_smart(ax,ax2,d1.values,d2.values)
    add_last_value_label(ax,d1,c1,fmt=fmt1,side="left")
    add_last_value_label(ax2,d2,c2,fmt=fmt2,side="right")
    set_xlim_to_data(ax,d1.index,d2.index)
    brand_fig(fig,title,subtitle=subtitle,source=source,data_date=max(s1.index.max(),s2.index.max()))
    _save(fig,fname)

# ================= MASTER =================
mri=idx("MRI"); rec("MRI",mri,dp=3)
for k in ["ENSEMBLE_RISK","ALLOC_MULTIPLIER","WARNING_LEVEL","REC_PROB","DISCONTINUITY_PREMIUM","BASE_REC_PROB","LIQ_STAGE"]:
    rec(k,idx(k),dp=3)
zchart(mri,"Macro Risk Index (MRI)","Master regime composite — currently neutral","Lighthouse Macro composite",
       "00_mri.png",start=mri.index.min(),recess=True)

# ================= 1 LABOR =================
lfi=idx("LFI"); rec("LFI",lfi,dp=3)
zchart(lfi,"Labor Fragility Index (LFI)","Composite of labor-market stress; +0.5 = fragile","Lighthouse Macro composite","p1_lfi.png")
quits=load("JTSQUR"); rec("JTSQUR",quits,"%")
linechart(quits,"JOLTS Quits Rate","Quits below 2.0% is the pre-recession tell","BLS JOLTS","p1_quits.png",ylabel="%",bands=[2.0],fmt="{:.1f}")
claims_raw=load("ICSA"); claims=claims_raw.rolling("28D").mean(); rec("ICSA",claims_raw)
linechart(claims,"Initial Jobless Claims (4-week avg)","Still historically low; no acute break","DOL","p1_claims.png",ylabel="claims",color=COLORS["sky"],fmt="{:,.0f}")

# ================= 2 PRICES =================
pci=idx("PCI"); rec("PCI",pci,dp=3)
zchart(pci,"Inflation Heat (PCI)","Composite inflation pressure; cooled, now sideways","Lighthouse Macro composite","p2_pci.png")
corepce=yoy(load("PCEPILFE")); rec("CorePCE_YoY",corepce,"%")
linechart(corepce,"Core PCE — Year over Year","The gauge the Fed writes from","BEA","p2_corepce.png",ylabel="% YoY",bands=[2.0],fmt="{:.1f}")
be5=load("T5YIE"); fwd=load("T5YIFR"); rec("T5YIE",be5,"%"); rec("T5YIFR",fwd,"%")
twolines(be5,fwd,"5Y Breakeven vs 5Y5Y Forward","Long-run expectations sticky above target","Treasury / FRBNY","p2_breakeven.png",
         "5Y breakeven","5Y5Y forward",start="2010-01-01",ylabel="%",fmt="{:.2f}")

# ================= 3 GROWTH =================
gci=idx("GCI"); rec("GCI",gci,dp=3)
zchart(gci,"Activity Pulse (GCI)","Real-activity diffusion — running above trend","Lighthouse Macro composite","p3_gci.png",start=gci.index.min())
ip=yoy(load("INDPRO")); rec("INDPRO_YoY",ip,"%")
linechart(ip,"Industrial Production — Year over Year","Positive but flat, mid-cycle pace","Federal Reserve","p3_indpro.png",ylabel="% YoY",bands=[0.0],fmt="{:.1f}",color=COLORS["sea"])
rr=yoy(load("RRSFS")); rec("RealRetail_YoY",rr,"%")
linechart(rr,"Real Retail & Food Sales — Year over Year","Decelerating off 2024 highs, still positive","Census","p3_retail.png",ylabel="% YoY",bands=[0.0],fmt="{:.1f}")

# ================= 4 HOUSING =================
hci=idx("HCI"); rec("HCI",hci,dp=3)
zchart(hci,"Housing Tide (HCI)","Composite housing conditions — off lows, no thaw","Lighthouse Macro composite","p4_hci.png",start=hci.index.min())
st=load("HOUST"); pm=load("PERMIT"); rec("HOUST",st); rec("PERMIT",pm)
twolines(st,pm,"Housing Starts vs Building Permits","Range-bound at depressed levels","Census","p4_starts.png",
         "Starts","Permits",start="2005-01-01",ylabel="thous, SAAR",fmt="{:,.0f}")
nahb=load("TV_USHMI"); mort=load("MORTGAGE30US"); rec("NAHB",nahb); rec("MORTGAGE30US",mort,"%")
dualchart(nahb,mort,"NAHB Builder Sentiment vs 30Y Mortgage","Sentiment pinned in contraction; financing costly","NAHB / Freddie Mac","p4_nahb.png",
          "NAHB index","30Y mortgage %",start="2010-01-01",fmt1="{:.0f}",fmt2="{:.1f}")

# ================= 5 CONSUMER =================
cci=idx("CCI"); rec("CCI",cci,dp=3)
zchart(cci,"Consumer Pulse (CCI)","Among weakest pillars (optimized composite, read with proxy)","Lighthouse Macro composite","p5_cci.png")
um=load("UMCSENT"); rec("UMCSENT",um)
linechart(um,"UMich Consumer Sentiment","Near historic lows — the squeezed-cohort read","University of Michigan","p5_umich.png",ylabel="index",fmt="{:.0f}",color=COLORS["port"])
rsx=yoy(load("RSXFS")); rec("RSXFS_YoY",rsx,"%")
linechart(rsx,"Retail Sales ex Food — Year over Year","The proxy: wealth-cohort spending still firm","Census","p5_rsxfs.png",ylabel="% YoY",bands=[0.0],fmt="{:.1f}")

# ================= 6 BUSINESS =================
bci=idx("BCI"); rec("BCI",bci,dp=3)
zchart(bci,"Capex Thrust (BCI)","Stable & positive (optimized composite, read with proxy)","Lighthouse Macro composite","p6_bci.png")
no=yoy(load("NEWORDER")); rec("NEWORDER_YoY",no,"%")
linechart(no,"Core Capital Goods Orders — Year over Year","The proxy: sharp, AI-capex concentrated","Census","p6_neworder.png",ylabel="% YoY",bands=[0.0],fmt="{:.1f}",color=COLORS["sea"])
tcu=load("TCU"); rec("TCU",tcu,"%")
linechart(tcu,"Total Capacity Utilization","Mid-range, no demand-pull on prices","Federal Reserve","p6_tcu.png",ylabel="%",fmt="{:.1f}",color=COLORS["sky"])

# ================= 7 TRADE =================
tci=idx("TCI"); rec("TCI",tci,dp=3)
zchart(tci,"Global Risk Tide (TCI)","Weakest pillar — defensive risk tilt","Lighthouse Macro composite","p7_tci.png")
dxy=load("DTWEXBGS"); rec("DTWEXBGS",dxy)
linechart(dxy,"Nominal Broad U.S. Dollar Index","Off highs — easing global conditions at the margin","Federal Reserve","p7_dollar.png",ylabel="index",fmt="{:.0f}",color=COLORS["dusk"],start="2010-01-01")
tb=load("BOPGSTB"); rec("BOPGSTB",tb)
linechart(tb,"Trade Balance, Goods & Services","Structurally negative, no inflection","BEA","p7_tradebal.png",ylabel="$ mil",bands=[0.0],fmt="{:,.0f}")

# ================= 8 GOVERNMENT =================
fpi=idx("FPI"); rec("FPI",fpi,dp=3)
zchart(fpi,"Fiscal Pressure (FPI)","Elevated band — the load-bearing pillar this cycle","Lighthouse Macro composite","p8_fpi.png")
tp=load("THREEFYTP10"); rec("TermPrem10",tp,"%")
linechart(tp,"10Y Term Premium (ACM)","Doubled in two years — carrying the long end","FRBNY","p8_termprem.png",ylabel="%",bands=[0.0],fmt="{:.2f}",color=COLORS["dusk"])
bb=load("MTSDS133FMS"); rec("BudgetBal",bb)
linechart(bb,"Monthly Federal Budget Balance","Persistent deficits keep coupon supply heavy","U.S. Treasury","p8_budget.png",ylabel="$ mil",bands=[0.0],fmt="{:,.0f}",start="2010-01-01")

# ================= 9 FINANCIAL =================
fci=idx("FCI"); clg=idx("CLG"); rec("FCI",fci,dp=3); rec("CLG",clg,dp=3)
zchart(fci,"Credit Tide (FCI)","Benign — no credit stress in the read","Lighthouse Macro composite","p9_fci.png")
hy=load("BAMLH0A0HYM2"); ig=load("BAMLC0A0CM"); rec("HY_OAS",hy,"%"); rec("IG_OAS",ig,"%")
twolines(hy,ig,"High Yield vs Investment Grade OAS","Both near tights — credit asleep","ICE BofA","p9_spreads.png",
         "HY OAS","IG OAS",start="2007-01-01",ylabel="%",fmt="{:.2f}")
cc1=load("T10Y2Y"); cc2=load("T10Y3M"); rec("T10Y2Y",cc1,"%"); rec("T10Y3M",cc2,"%")
twolines(cc1,cc2,"Yield Curve: 10Y-2Y and 10Y-3M","Re-steepening out of inversion (bear steepener)","Federal Reserve","p9_curve.png",
         "10Y-2Y","10Y-3M",start="2005-01-01",ylabel="%",zero=True,fmt="{:.2f}")

# ================= 10 PLUMBING =================
lci=idx("LCI"); rec("LCI",lci,dp=3)
zchart(lci,"Liquidity Cushion (LCI)","Reads neutral — masks an exhausted buffer","Lighthouse Macro composite","p10_lci.png")
res=load("WRESBAL")/1000.0; rrp=load("RRPONTSYD"); rec("WRESBAL",res*1000); rec("RRP",rrp)
dualchart(res,rrp,"Bank Reserves vs Overnight RRP","RRP cushion gone — drain now hits reserves","Federal Reserve","p10_reserves.png",
          "Reserves $bn","RRP $bn",start="2015-01-01",recess=False,fmt1="{:,.0f}",fmt2="{:,.0f}")
effr=load("EFFR"); iorb=load("IORB")
spread=((effr-iorb.reindex(effr.index).ffill())*100).dropna(); rec("EFFR_IORB_bps",spread,"bps")
linechart(spread,"EFFR minus IORB (bps)","The trigger to watch — benign below +8bps","FRBNY / Federal Reserve","p10_effr.png",
          ylabel="bps",bands=[8.0,0.0],fmt="{:.0f}",color=COLORS["venus"],start="2018-01-01",recess=False)

# ================= 11 STRUCTURE =================
msi=idx("MSI"); rec("MSI",msi,dp=3)
zchart(msi,"Market Breadth Pulse (MSI)","Positive but fading under a record tape","Lighthouse Macro composite","p11_msi.png",start="2018-01-01",recess=False)
a50=load("SPX_PCT_ABOVE_50D"); rec("PCT_ABOVE_50D",a50,"%")
linechart(a50,"S&P 500 % Above 50-Day MA","Neutral — no breadth thrust (30/70 bands)","Lighthouse Macro","p11_breadth.png",
          ylabel="%",bands=[30.0,70.0],fmt="{:.0f}",start="2023-01-01",recess=False)
mcc=load("SPX_MCCLELLAN_SUM"); rec("MCCLELLAN_SUM",mcc)
linechart(mcc,"S&P 500 McClellan Summation Index","Rolled over hard while index made highs","Lighthouse Macro","p11_mcclellan.png",
          ylabel="index",bands=[0.0],fmt="{:.0f}",color=COLORS["sea"],start="2023-01-01",recess=False)

# ================= 12 SENTIMENT =================
spi=idx("SPI"); rec("SPI",spi,dp=3)
zchart(spi,"Sentiment Tide (SPI)","Neutral — no contrarian extreme to fade","Lighthouse Macro composite","p12_spi.png",start="2018-01-01",recess=False)
aa=load("AAII_Bull_Bear_Spread")*100.0; rec("AAII_BULL_BEAR",aa,"pp")
linechart(aa,"AAII Bull-Bear Spread","Mildly bearish, inside neutral band (+30/-20)","AAII","p12_aaii.png",
          ylabel="pct points",bands=[30.0,-20.0,0.0],fmt="{:.0f}",color=COLORS["dusk"],start="2015-01-01",recess=False)
vix=load("VIXCLS"); rec("VIX",vix)
linechart(vix,"CBOE Volatility Index (VIX)","Calm — complacent against the backdrop","CBOE","p12_vix.png",ylabel="index",fmt="{:.0f}",color=COLORS["port"],start="2015-01-01",recess=False)

# ================= SCORECARD PNG =================
def g(k,f="last"): return readings.get(k,{}).get(f)
def fmtv(v,suf="",dp=2):
    return "n/a" if v is None else (f"{v:.{dp}f}{suf}")

SC=[ # num, name, code, reading_str, status, color
 (1,"Labor","LFI",f"LFI {fmtv(g('LFI'),'',2)} · quits {fmtv(g('JTSQUR'),'%',1)}","NEUTRAL, fraying",COLORS["ocean"]),
 (2,"Prices","PCI",f"PCI {fmtv(g('PCI'),'',2)} · core PCE {fmtv(g('CorePCE_YoY'),'%',1)}","STICKY",COLORS["dusk"]),
 (3,"Growth","GCI",f"GCI {fmtv(g('GCI'),'',2)} · IP {fmtv(g('INDPRO_YoY'),'%',1)} YoY","FIRM",COLORS["starboard"]),
 (4,"Housing","HCI",f"HCI {fmtv(g('HCI'),'',2)} · NAHB {fmtv(g('NAHB'),'',0)}","FROZEN",COLORS["doldrums"]),
 (5,"Consumer","CCI",f"CCI {fmtv(g('CCI'),'',2)} · UMich {fmtv(g('UMCSENT'),'',0)}","WEAK, split",COLORS["port"]),
 (6,"Business","BCI",f"BCI {fmtv(g('BCI'),'',2)} · orders {fmtv(g('NEWORDER_YoY'),'%',1)} YoY","STABLE",COLORS["ocean"]),
 (7,"Trade","TCI",f"TCI {fmtv(g('TCI'),'',2)} · USD {fmtv(g('DTWEXBGS'),'',0)}","RISK-OFF",COLORS["port"]),
 (8,"Government","FPI",f"FPI {fmtv(g('FPI'),'',2)} · term prem {fmtv(g('TermPrem10'),'%',2)}","ELEVATED",COLORS["dusk"]),
 (9,"Financial","FCI",f"FCI {fmtv(g('FCI'),'',2)} · HY {int(round(g('HY_OAS')*100))}bps","COMPLACENT",COLORS["starboard"]),
 (10,"Plumbing","LCI",f"LCI {fmtv(g('LCI'),'',2)} · RRP ${fmtv(g('RRP'),'bn',0)}","CUSHION GONE",COLORS["dusk"]),
 (11,"Structure","MSI",f"MSI {fmtv(g('MSI'),'',2)} · >50d {fmtv(g('PCT_ABOVE_50D'),'%',0)}","THINNING",COLORS["port"]),
 (12,"Sentiment","SPI",f"SPI {fmtv(g('SPI'),'',2)} · VIX {fmtv(g('VIX'),'',0)}","NEUTRAL",COLORS["ocean"]),
]
METRICS=[("MRI (regime)",fmtv(g("MRI"),'',2),COLORS["ocean"]),
 ("Ensemble Risk",fmtv(g("ENSEMBLE_RISK"),'',2),COLORS["dusk"]),
 ("Warning",f"RED · {int(g('WARNING_LEVEL'))}",COLORS["port"]),
 ("Alloc Mult",fmtv(g("ALLOC_MULTIPLIER"),'',2),COLORS["port"]),
 ("Rec Prob",f"{g('REC_PROB')*100:.0f}%",COLORS["ocean"]),
 ("Discont. Prem",fmtv(g("DISCONTINUITY_PREMIUM"),'',2),COLORS["dusk"]),
 ("Liq Stage",f"{int(g('LIQ_STAGE'))}",COLORS["ocean"]),
]

fig=plt.figure(figsize=(11.5,9.2)); fig.patch.set_facecolor("white")
ax=fig.add_axes([0.04,0.055,0.92,0.74]); ax.axis("off"); ax.set_xlim(0,1); ax.set_ylim(0,1)
# metrics band
n=len(METRICS); cw=1.0/n
for i,(k,v,c) in enumerate(METRICS):
    x=i*cw+cw/2
    ax.text(x,0.99,k.upper(),ha="center",va="top",fontsize=8.5,color=COLORS["doldrums"])
    ax.text(x,0.945,v,ha="center",va="top",fontsize=15,fontweight="bold",color=c)
ax.axhline(0.90,xmin=0.0,xmax=1.0,color=COLORS["doldrums"],lw=0.6)
# pillar rows
top=0.855; bot=0.01; rh=(top-bot)/12.0
for i,(num,name,code,rd,status,color) in enumerate(SC):
    y=top-(i+0.5)*rh
    if i%2==0:
        ax.add_patch(plt.Rectangle((0,top-(i+1)*rh),1,rh,color=COLORS["offwhite"],zorder=0))
    ax.text(0.018,y,f"{num:02d}",ha="left",va="center",fontsize=15,fontweight="bold",color="#cdd9e0")
    ax.text(0.075,y,name,ha="left",va="center",fontsize=13,fontweight="bold",color="#1a1a1a")
    ax.text(0.075,y-rh*0.30,code,ha="left",va="center",fontsize=8.5,color=COLORS["doldrums"],family="monospace")
    ax.text(0.30,y,rd,ha="left",va="center",fontsize=11,color="#33485a",family="monospace")
    # status chip
    chip=FancyBboxPatch((0.80,y-rh*0.22),0.185,rh*0.44,
                        boxstyle="round,pad=0.004,rounding_size=0.02",
                        mutation_aspect=0.5,facecolor=color,edgecolor="none",zorder=2)
    ax.add_patch(chip)
    ax.text(0.8925,y,status,ha="center",va="center",fontsize=9.5,fontweight="bold",color="white",zorder=3)
brand_fig(fig,"The Twelve Pillars — Internal Scorecard",
          subtitle="Live composite readings across three engines",
          source="Lighthouse_Master.db",data_date=pd.Timestamp(g("ENSEMBLE_RISK","date") or "2026-06-04"))
_save(fig,"00_scorecard.png")

con.close()
with open("/tmp/pillar_readings.json","w") as f: json.dump(readings,f,indent=2)
print("DONE — charts + scorecard in",OUT)
