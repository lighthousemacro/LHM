#!/usr/bin/env python3
"""Re-render the Main Street Monitor's 4 charts to article production quality
(canonical LHM template) and rewrite the dashboard to embed them as branded
PNGs. Drops Chart.js, the inline JS, the timeframe toggle, and redundant card
titles (the PNG carries title/subtitle)."""
import re, json, base64, io, sys
import pandas as pd
sys.path.insert(0,"/Users/bob/LHM/Scripts/chart_generation")
from lhm_chart_template import (
    COLORS, set_theme, new_fig, style_single_ax, style_dual_ax,
    add_last_value_label, set_xlim_to_data, legend_style, brand_fig,
    _add_border, align_yaxis_smart,
)
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

HTML="/Users/bob/LHM/Data/databases/pillars/main_street_monitor.html"
set_theme("white")
FIG=(9.4,5.5); DPI=145; WIN_MONTHS=24

html=open(HTML).read()

# ---- extract CHART_DATA ----
data=None
for line in html.splitlines():
    if line.strip().startswith("const CHART_DATA"):
        s=line.index("{"); e=line.rindex("}"); data=json.loads(line[s:e+1]); break
assert data, "CHART_DATA not found"

def ser(key):
    d=data[key]; s=pd.Series(d["values"],index=pd.to_datetime(d["dates"])).dropna()
    return s[~s.index.duplicated(keep="last")].sort_index()
def win(s):
    end=s.index.max(); return s[s.index>=end-pd.DateOffset(months=WIN_MONTHS)]
def refline(ax,y,label,color,ls="--"):
    ax.axhline(y,color=color,lw=1.3,ls=ls,zorder=1)
    ax.text(0.012,y,label,transform=ax.get_yaxis_transform(),fontsize=8.5,
            color=color,va="bottom",ha="left",style="italic",
            bbox=dict(boxstyle="round,pad=0.15",fc="white",ec="none",alpha=0.7))

def buf(fig):
    _add_border(fig); b=io.BytesIO()
    fig.savefig(b,format="png",dpi=DPI,bbox_inches="tight",pad_inches=0.025,
                facecolor="white",edgecolor="none"); plt.close(fig)
    return base64.b64encode(b.getvalue()).decode()

imgs={}

# CHART 1 — Savings Buffer
sr=win(ser("saving_rate")); pce=win(ser("real_pce_yoy"))
fig,ax=new_fig(FIG); ax2=ax.twinx(); style_dual_ax(ax,ax2,COLORS["ocean"],COLORS["dusk"])
ax.plot(sr.index,sr.values,color=COLORS["ocean"],lw=2.6,zorder=3)
ax.fill_between(sr.index,sr.values,sr.min()*0,color=COLORS["ocean"],alpha=0.10,zorder=2)
ax2.plot(pce.index,pce.values,color=COLORS["dusk"],lw=2.2,ls=(0,(5,2)),zorder=3)
ax.set_ylabel("Saving rate %",color=COLORS["ocean"]); ax2.set_ylabel("Real PCE YoY %",color=COLORS["dusk"])
refline(ax,7.4,"Pre-COVID avg 7.4%",COLORS["doldrums"])
align_yaxis_smart(ax,ax2,sr.values,pce.values)
add_last_value_label(ax,sr,COLORS["ocean"],fmt="{:.1f}",side="left")
add_last_value_label(ax2,pce,COLORS["dusk"],fmt="{:.1f}",side="right")
set_xlim_to_data(ax,sr.index,pce.index)
brand_fig(fig,"Savings Buffer: Depleted",
          subtitle="Saving rate vs real PCE growth — spending on drawn-down savings, not rising income",
          source="BEA",data_date=sr.index.max())
imgs["chart1"]=buf(fig)

# CHART 2 — Credit Substitution
ccd=win(ser("cc_delinquency")); ccr=win(ser("cc_rate"))
fig,ax=new_fig(FIG); ax2=ax.twinx(); style_dual_ax(ax,ax2,COLORS["ocean"],COLORS["dusk"])
ax.plot(ccd.index,ccd.values,color=COLORS["ocean"],lw=2.6,zorder=3)
ax.fill_between(ccd.index,ccd.values,ccd.min(),color=COLORS["ocean"],alpha=0.10,zorder=2)
ax2.plot(ccr.index,ccr.values,color=COLORS["dusk"],lw=2.2,zorder=3)
ax.set_ylabel("CC delinquency %",color=COLORS["ocean"]); ax2.set_ylabel("CC APR %",color=COLORS["dusk"])
refline(ax,2.97,"GFC peak 2.97%",COLORS["venus"])
align_yaxis_smart(ax,ax2,ccd.values,ccr.values)
add_last_value_label(ax,ccd,COLORS["ocean"],fmt="{:.2f}",side="left")
add_last_value_label(ax2,ccr,COLORS["dusk"],fmt="{:.1f}",side="right")
set_xlim_to_data(ax,ccd.index,ccr.index)
brand_fig(fig,"Credit Substitution: Stage 2",
          subtitle="Delinquency vs APR — borrowing at record cost to fund essentials",
          source="Federal Reserve",data_date=ccd.index.max())
imgs["chart2"]=buf(fig)

# CHART 3 — Wage-Price Squeeze (single axis, 4 lines)
ahe=win(ser("ahe_yoy")); cpia=win(ser("cpi_all_yoy")); cpis=win(ser("cpi_shelter_yoy")); cpif=win(ser("cpi_food_yoy"))
fig,ax=new_fig(FIG); style_single_ax(ax,fmt="{:.1f}")
ax.plot(ahe.index,ahe.values,color=COLORS["ocean"],lw=2.6,label="Avg hourly earnings",zorder=4)
ax.plot(cpia.index,cpia.values,color=COLORS["dusk"],lw=2.2,label="CPI all items",zorder=3)
ax.plot(cpis.index,cpis.values,color=COLORS["sky"],lw=1.8,label="CPI shelter",zorder=3)
ax.plot(cpif.index,cpif.values,color=COLORS["sea"],lw=1.8,label="CPI food at home",zorder=3)
ax.set_ylabel("% YoY")
add_last_value_label(ax,ahe,COLORS["ocean"],fmt="{:.1f}")
leg=ax.legend(loc="upper right",fontsize=9,**legend_style())
set_xlim_to_data(ax,ahe.index)
brand_fig(fig,"The Wage-Price Squeeze",
          subtitle="Hourly earnings vs the CPI lines that hit Main Street hardest",
          source="BLS",data_date=ahe.index.max())
imgs["chart3"]=buf(fig)

# CHART 4 — Labor Surface vs Depth
qr=win(ser("quits_rate")); th=win(ser("temp_help_yoy"))
fig,ax=new_fig(FIG); ax2=ax.twinx(); style_dual_ax(ax,ax2,COLORS["ocean"],COLORS["dusk"])
ax.plot(qr.index,qr.values,color=COLORS["ocean"],lw=2.6,zorder=3)
ax2.plot(th.index,th.values,color=COLORS["dusk"],lw=2.2,zorder=3)
ax.set_ylabel("Quits rate %",color=COLORS["ocean"]); ax2.set_ylabel("Temp help YoY %",color=COLORS["dusk"])
refline(ax,2.0,"Danger <2.0%",COLORS["venus"])
align_yaxis_smart(ax,ax2,qr.values,th.values)
add_last_value_label(ax,qr,COLORS["ocean"],fmt="{:.1f}",side="left")
add_last_value_label(ax2,th,COLORS["dusk"],fmt="{:.1f}",side="right")
set_xlim_to_data(ax,qr.index,th.index)
brand_fig(fig,"Labor Market: Surface vs Depth",
          subtitle="Quits and temp help — the labor quality the headline hides",
          source="BLS JOLTS",data_date=qr.index.max())
imgs["chart4"]=buf(fig)

# ---------------- HTML surgery ----------------
# 1. drop Chart.js CDN scripts
html=re.sub(r'\s*<script src="https://cdnjs\.cloudflare\.com/ajax/libs/Chart\.js[^>]*></script>','',html)
html=re.sub(r'\s*<script src="https://cdnjs\.cloudflare\.com/ajax/libs/chartjs-plugin-annotation[^>]*></script>','',html)
# 2. remove the timeframe toggle UI
html=re.sub(r'<div class="tf-toggle">.*?</div>\s*','',html,flags=re.S)
# 3. remove redundant card titles/subs (PNG carries them)
html=re.sub(r'\s*<div class="chart-title">.*?</div>','',html,flags=re.S)
html=re.sub(r'\s*<div class="chart-sub">.*?</div>','',html,flags=re.S)
# 4. swap canvases for branded PNGs
for cid,b64 in imgs.items():
    html=re.sub(r'<div class="chart-canvas-wrap"><canvas id="%s"[^>]*></canvas></div>'%cid,
                f'<img class="chart-img" src="data:image/png;base64,{b64}" alt="{cid}"/>',html)
# 5. remove the inline data/build script block
html=re.sub(r'<script>\s*const CHART_DATA.*?</script>','',html,flags=re.S)
# 6. css: add chart-img rule, neutralize old canvas-wrap height
html=html.replace(".chart-canvas-wrap{position:relative;width:100%;height:220px;}\n.chart-canvas{display:block;}",
                  ".chart-img{width:100%;display:block;border-radius:6px;}")

open(HTML,"w").write(html)
print("REWROTE",HTML)
print("charts embedded:",list(imgs.keys()),"| html KB:",round(len(html)/1024))
