#!/usr/bin/env python3
"""Internal 12-pillar read: clean charts (no on-chart annotations) + live readings dump.
White theme, 23/89/BB palette. Captions live in the HTML, not on the plot.
"""
import sqlite3, json, os
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

DB = "/Users/bob/LHM/Data/databases/Lighthouse_Master.db"
OUT = "/Users/bob/LHM/Outputs/pillar_charts"
os.makedirs(OUT, exist_ok=True)

# 23/89/BB palette
OCEAN="#2389BB"; DUSK="#FF6723"; SKY="#23BBFF"; SEA="#00BB89"; VENUS="#FF2389"
DOLDRUMS="#898989"; STARBOARD="#238923"; PORT="#892323"; FOG="#D1D1D1"
NBER=[("2007-12-01","2009-06-30"),("2020-02-01","2020-04-30")]

plt.rcParams.update({
    "font.family":"sans-serif",
    "font.sans-serif":["Montserrat","Inter","Helvetica Neue","Arial","DejaVu Sans"],
    "axes.edgecolor":DOLDRUMS,"axes.linewidth":0.5,"figure.dpi":150,
})

con=sqlite3.connect(DB)
def load(sid):
    df=pd.read_sql("select date,value from observations where series_id=? order by date",con,params=(sid,))
    if df.empty: return pd.Series(dtype=float)
    s=pd.Series(df.value.values,index=pd.to_datetime(df.date)).dropna()
    return s[~s.index.duplicated(keep="last")]

def idx(iid):
    df=pd.read_sql("select date,value from lighthouse_indices where index_id=? order by date",con,params=(iid,))
    if df.empty: return pd.Series(dtype=float)
    s=pd.Series(df.value.values,index=pd.to_datetime(df.date)).dropna()
    return s[~s.index.duplicated(keep="last")]

def yoy(s, freq_periods=12):
    m=s.resample("ME").last()
    return (m/m.shift(freq_periods)-1.0)*100.0

readings={}
def rec(name,s,unit="",dp=2):
    if s is None or len(s)==0:
        readings[name]={"last":None}; return
    last=float(s.iloc[-1]); dt=s.index[-1].strftime("%Y-%m-%d")
    prev=None
    try:
        yr=s[s.index<=s.index[-1]-pd.Timedelta(days=365)]
        prev=float(yr.iloc[-1]) if len(yr) else None
    except Exception: pass
    readings[name]={"last":round(last,dp),"date":dt,"yr_ago":(round(prev,dp) if prev is not None else None),
                    "chg_1y":(round(last-prev,dp) if prev is not None else None),"unit":unit}

def base(figsize=(7.6,3.5)):
    fig,ax=plt.subplots(figsize=figsize)
    fig.patch.set_facecolor("white"); ax.set_facecolor("white")
    for sp in ax.spines.values(): sp.set_visible(True); sp.set_color(DOLDRUMS); sp.set_linewidth(0.5)
    ax.grid(False)
    ax.yaxis.set_label_position("right"); ax.yaxis.tick_right()
    ax.tick_params(colors=DOLDRUMS,labelsize=8)
    return fig,ax

def finish(fig,ax,title,source,fname,window_start=None):
    if window_start is not None:
        ax.set_xlim(left=pd.to_datetime(window_start))
    # accent bar
    fig.subplots_adjust(top=0.86,bottom=0.16,left=0.04,right=0.90)
    tb=fig.add_axes([0.04,0.945,0.86,0.022]); tb.axis("off")
    tb.add_patch(plt.Rectangle((0,0),0.666,1,color=OCEAN,transform=tb.transAxes))
    tb.add_patch(plt.Rectangle((0.666,0),0.334,1,color=DUSK,transform=tb.transAxes))
    fig.text(0.04,0.90,title,fontsize=11,fontweight="bold",color="#111",ha="left")
    fig.text(0.04,0.035,f"Lighthouse Macro | {source}",fontsize=6.5,color=DOLDRUMS,ha="left")
    fig.text(0.90,0.035,"INTERNAL",fontsize=6.5,color=DOLDRUMS,ha="right",style="italic")
    fig.savefig(os.path.join(OUT,fname),dpi=150,facecolor="white",
                bbox_inches="tight",pad_inches=0.04)
    plt.close(fig)

def add_recessions(ax,start):
    s=pd.to_datetime(start)
    for a,b in NBER:
        a=pd.to_datetime(a); b=pd.to_datetime(b)
        if b>=s: ax.axvspan(max(a,s),b,color=DOLDRUMS,alpha=0.12,lw=0)

def zchart(series,title,source,fname,smooth_days=90,window_start=None,recess=True):
    """z-score composite: smoothed line, zero + canonical 2sigma bands. No annotations."""
    if series is None or len(series)==0: return
    s=series.sort_index()
    sm=s.rolling(f"{smooth_days}D").mean()
    fig,ax=base()
    ws=window_start or s.index.min()
    if recess: add_recessions(ax,ws)
    ax.axhline(0,color=FOG,lw=0.8,ls="--")
    ax.axhline(1.96,color=DOLDRUMS,lw=0.6,ls=":"); ax.axhline(-1.96,color=DOLDRUMS,lw=0.6,ls=":")
    ax.plot(sm.index,sm.values,color=OCEAN,lw=1.6)
    ax.set_ylabel("z-score",color=DOLDRUMS,fontsize=8)
    finish(fig,ax,title,source,fname,window_start=ws)

def linechart(series,title,source,fname,color=OCEAN,window_start="2005-01-01",
              recess=True,ylabel="",pct_band=None):
    if series is None or len(series)==0: return
    s=series.sort_index()
    fig,ax=base()
    if recess: add_recessions(ax,window_start)
    if pct_band:
        for lvl in pct_band: ax.axhline(lvl,color=DOLDRUMS,lw=0.6,ls=":")
    ax.plot(s.index,s.values,color=color,lw=1.5)
    if ylabel: ax.set_ylabel(ylabel,color=DOLDRUMS,fontsize=8)
    finish(fig,ax,title,source,fname,window_start=window_start)

def dualchart(s1,s2,title,source,fname,l1,l2,c1=OCEAN,c2=DUSK,window_start="2005-01-01",recess=True):
    if s1 is None or len(s1)==0: return
    s1=s1.sort_index();
    fig,ax=base()
    if recess: add_recessions(ax,window_start)
    ax.plot(s1.index,s1.values,color=c1,lw=1.5,label=l1)
    ax.set_ylabel(l1,color=c1,fontsize=8)
    ax.tick_params(axis="y",colors=c1)
    if s2 is not None and len(s2)>0:
        s2=s2.sort_index()
        ax2=ax.twinx(); ax2.set_facecolor("none")
        for sp in ax2.spines.values(): sp.set_color(DOLDRUMS); sp.set_linewidth(0.5)
        ax2.yaxis.set_label_position("left"); ax2.yaxis.tick_left()
        ax2.plot(s2.index,s2.values,color=c2,lw=1.5,label=l2)
        ax2.set_ylabel(l2,color=c2,fontsize=8); ax2.tick_params(axis="y",colors=c2,labelsize=8)
    finish(fig,ax,title,source,fname,window_start=window_start)

def twolines(s1,s2,title,source,fname,l1,l2,c1=OCEAN,c2=DUSK,window_start="2005-01-01",
             recess=True,ylabel="",zero=False):
    fig,ax=base()
    if recess: add_recessions(ax,window_start)
    if zero: ax.axhline(0,color=FOG,lw=0.8,ls="--")
    if s1 is not None and len(s1): ax.plot(s1.sort_index().index,s1.sort_index().values,color=c1,lw=1.5,label=l1)
    if s2 is not None and len(s2): ax.plot(s2.sort_index().index,s2.sort_index().values,color=c2,lw=1.5,label=l2)
    if ylabel: ax.set_ylabel(ylabel,color=DOLDRUMS,fontsize=8)
    leg=ax.legend(loc="best",fontsize=7,frameon=False)
    for t in leg.get_texts(): t.set_color("#333")
    finish(fig,ax,title,source,fname,window_start=window_start)

CW="2010-01-01"  # composite display window default

# ---------- MASTER ----------
mri=idx("MRI"); rec("MRI",mri,dp=3)
for k in ["ENSEMBLE_RISK","ALLOC_MULTIPLIER","WARNING_LEVEL","REC_PROB","DISCONTINUITY_PREMIUM","BASE_REC_PROB","LIQ_STAGE"]:
    rec(k,idx(k),dp=3)
zchart(mri,"Macro Risk Index (MRI) — master composite","Lighthouse Macro composite","00_mri.png",window_start=mri.index.min() if len(mri) else None,recess=True)

# ---------- 1 LABOR ----------
lfi=idx("LFI"); rec("LFI",lfi,dp=3)
zchart(lfi,"Labor Fragility Index (LFI)","Lighthouse Macro composite","p1_lfi.png",window_start=CW)
quits=load("JTSQUR"); rec("JTSQUR",quits,"%")
linechart(quits,"JOLTS Quits Rate","BLS JOLTS","p1_quits.png",window_start="2005-01-01",ylabel="%",pct_band=[2.0])
claims=load("ICSA").rolling("28D").mean(); rec("ICSA",load("ICSA"))
linechart(claims,"Initial Jobless Claims (4-week avg)","DOL","p1_claims.png",window_start="2015-01-01",ylabel="claims")

# ---------- 2 PRICES ----------
pci=idx("PCI"); rec("PCI",pci,dp=3)
zchart(pci,"Inflation Heat (PCI)","Lighthouse Macro composite","p2_pci.png",window_start=CW)
corepce=yoy(load("PCEPILFE")); rec("CorePCE_YoY",corepce,"%")
linechart(corepce,"Core PCE — year over year","BEA","p2_corepce.png",window_start="2005-01-01",ylabel="% YoY",pct_band=[2.0])
be5=load("T5YIE"); fwd=load("T5YIFR"); rec("T5YIE",be5,"%"); rec("T5YIFR",fwd,"%")
twolines(be5,fwd,"5Y breakeven vs 5Y5Y forward inflation","Treasury / FRBNY","p2_breakeven.png",
         "5Y breakeven","5Y5Y forward",window_start="2010-01-01",ylabel="%")

# ---------- 3 GROWTH ----------
gci=idx("GCI"); rec("GCI",gci,dp=3)
zchart(gci,"Activity Pulse (GCI)","Lighthouse Macro composite","p3_gci.png",window_start=gci.index.min() if len(gci) else None,recess=True)
ip=yoy(load("INDPRO")); rec("INDPRO_YoY",ip,"%")
linechart(ip,"Industrial Production — year over year","Federal Reserve","p3_indpro.png",window_start="2005-01-01",ylabel="% YoY",pct_band=[0.0])
rr=yoy(load("RRSFS")); rec("RealRetail_YoY",rr,"%")
linechart(rr,"Real Retail & Food Sales — year over year","Census","p3_retail.png",window_start="2005-01-01",ylabel="% YoY",pct_band=[0.0])

# ---------- 4 HOUSING ----------
hci=idx("HCI"); rec("HCI",hci,dp=3)
zchart(hci,"Housing Tide (HCI)","Lighthouse Macro composite","p4_hci.png",window_start=hci.index.min() if len(hci) else None)
st=load("HOUST"); pm=load("PERMIT"); rec("HOUST",st); rec("PERMIT",pm)
twolines(st,pm,"Housing Starts vs Building Permits","Census","p4_starts.png","Starts","Permits",window_start="2005-01-01",ylabel="thous, SAAR")
nahb=load("TV_USHMI"); mort=load("MORTGAGE30US"); rec("NAHB",nahb); rec("MORTGAGE30US",mort,"%")
dualchart(nahb,mort,"NAHB builder sentiment vs 30Y mortgage rate","NAHB / Freddie Mac","p4_nahb.png",
          "NAHB index","30Y mortgage %",window_start="2010-01-01")

# ---------- 5 CONSUMER ----------
cci=idx("CCI"); rec("CCI",cci,dp=3)
zchart(cci,"Consumer Pulse (CCI)","Lighthouse Macro composite","p5_cci.png",window_start=CW)
um=load("UMCSENT"); rec("UMCSENT",um)
linechart(um,"UMich Consumer Sentiment","University of Michigan","p5_umich.png",window_start="2005-01-01",ylabel="index")
rsx=yoy(load("RSXFS")); rec("RSXFS_YoY",rsx,"%")
linechart(rsx,"Retail Sales ex Food Services — year over year","Census","p5_rsxfs.png",window_start="2005-01-01",ylabel="% YoY",pct_band=[0.0])

# ---------- 6 BUSINESS ----------
bci=idx("BCI"); rec("BCI",bci,dp=3)
zchart(bci,"Capex Thrust (BCI)","Lighthouse Macro composite","p6_bci.png",window_start=CW)
no=yoy(load("NEWORDER")); rec("NEWORDER_YoY",no,"%")
linechart(no,"Core Capital Goods New Orders — year over year","Census","p6_neworder.png",window_start="2005-01-01",ylabel="% YoY",pct_band=[0.0],color=SEA)
tcu=load("TCU"); rec("TCU",tcu,"%")
linechart(tcu,"Total Capacity Utilization","Federal Reserve","p6_tcu.png",window_start="2005-01-01",ylabel="%")

# ---------- 7 TRADE ----------
tci=idx("TCI"); rec("TCI",tci,dp=3)
zchart(tci,"Global Risk Tide (TCI)","Lighthouse Macro composite","p7_tci.png",window_start=CW)
dxy=load("DTWEXBGS"); rec("DTWEXBGS",dxy)
linechart(dxy,"Nominal Broad U.S. Dollar Index","Federal Reserve","p7_dollar.png",window_start="2010-01-01",ylabel="index",color=DUSK)
tb=load("BOPGSTB"); rec("BOPGSTB",tb)
linechart(tb,"Trade Balance, Goods & Services","BEA","p7_tradebal.png",window_start="2005-01-01",ylabel="$ mil",pct_band=[0.0])

# ---------- 8 GOVERNMENT ----------
fpi=idx("FPI"); rec("FPI",fpi,dp=3)
zchart(fpi,"Fiscal Pressure (FPI)","Lighthouse Macro composite","p8_fpi.png",window_start=CW)
tp=load("THREEFYTP10"); rec("TermPrem10",tp,"%")
linechart(tp,"10Y Term Premium (ACM)","FRBNY","p8_termprem.png",window_start="2005-01-01",ylabel="%",pct_band=[0.0],color=DUSK)
bb=load("MTSDS133FMS"); rec("BudgetBal",bb)
linechart(bb,"Monthly Federal Budget Balance","U.S. Treasury","p8_budget.png",window_start="2010-01-01",ylabel="$ mil",pct_band=[0.0])

# ---------- 9 FINANCIAL ----------
fci=idx("FCI"); clg=idx("CLG"); rec("FCI",fci,dp=3); rec("CLG",clg,dp=3)
zchart(fci,"Credit Tide (FCI)","Lighthouse Macro composite","p9_fci.png",window_start=CW)
hy=load("BAMLH0A0HYM2"); ig=load("BAMLC0A0CM"); rec("HY_OAS",hy,"%"); rec("IG_OAS",ig,"%")
twolines(hy,ig,"High Yield vs Investment Grade OAS","ICE BofA","p9_spreads.png","HY OAS","IG OAS",
         window_start="2007-01-01",ylabel="%")
c1=load("T10Y2Y"); c2=load("T10Y3M"); rec("T10Y2Y",c1,"%"); rec("T10Y3M",c2,"%")
twolines(c1,c2,"Yield Curve: 10Y-2Y and 10Y-3M","Federal Reserve","p9_curve.png","10Y-2Y","10Y-3M",
         window_start="2005-01-01",ylabel="%",zero=True)

# ---------- 10 PLUMBING ----------
lci=idx("LCI"); rec("LCI",lci,dp=3)
zchart(lci,"Liquidity Cushion (LCI)","Lighthouse Macro composite","p10_lci.png",window_start=CW)
res=load("WRESBAL")/1000.0; rrp=load("RRPONTSYD"); rec("WRESBAL",res*1000); rec("RRP",rrp)
dualchart(res,rrp,"Bank Reserves vs Overnight RRP","Federal Reserve","p10_reserves.png",
          "Reserves $bn","RRP $bn",window_start="2015-01-01",recess=False)
effr=load("EFFR"); iorb=load("IORB")
spread=(effr-iorb.reindex(effr.index).ffill())*100  # to bps
rec("EFFR_IORB_bps",spread,"bps")
linechart(spread.dropna(),"EFFR minus IORB (bps)","FRBNY / Federal Reserve","p10_effr.png",
          window_start="2018-01-01",ylabel="bps",pct_band=[8.0,0.0],color=VENUS,recess=False)

# ---------- 11 STRUCTURE ----------
msi=idx("MSI"); rec("MSI",msi,dp=3)
zchart(msi,"Market Breadth Pulse (MSI)","Lighthouse Macro composite","p11_msi.png",window_start="2018-01-01",recess=False)
a50=load("SPX_PCT_ABOVE_50D"); rec("PCT_ABOVE_50D",a50,"%")
linechart(a50,"S&P 500 % Above 50-Day MA","Lighthouse Macro","p11_breadth.png",window_start="2023-01-01",
          ylabel="%",pct_band=[30.0,70.0],recess=False,color=OCEAN)
mcc=load("SPX_MCCLELLAN_SUM"); rec("MCCLELLAN_SUM",mcc)
linechart(mcc,"S&P 500 McClellan Summation Index","Lighthouse Macro","p11_mcclellan.png",window_start="2023-01-01",
          ylabel="index",pct_band=[0.0],recess=False,color=SEA)

# ---------- 12 SENTIMENT ----------
spi=idx("SPI"); rec("SPI",spi,dp=3)
zchart(spi,"Sentiment Tide (SPI)","Lighthouse Macro composite","p12_spi.png",window_start="2018-01-01",recess=False)
aa=load("AAII_Bull_Bear_Spread")*100.0; rec("AAII_BULL_BEAR",aa,"pp")
linechart(aa,"AAII Bull-Bear Spread","AAII","p12_aaii.png",window_start="2015-01-01",ylabel="pct points",
          pct_band=[30.0,-20.0,0.0],recess=False,color=DUSK)
vix=load("VIXCLS"); rec("VIX",vix)
linechart(vix,"CBOE Volatility Index (VIX)","CBOE","p12_vix.png",window_start="2015-01-01",ylabel="index",color=PORT,recess=False)

con.close()
with open("/tmp/pillar_readings.json","w") as f: json.dump(readings,f,indent=2)
print("CHARTS WRITTEN to",OUT)
print(json.dumps(readings,indent=2))
