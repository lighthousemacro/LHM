#!/usr/bin/env python3
"""Assemble the internal 12-pillar read into branded HTML with base64-inlined charts."""
import base64, json, os, datetime

CH="/Users/bob/LHM/Outputs/pillar_charts"
OUT="/Users/bob/LHM/Outputs/12pillar_internal_read.html"
R=json.load(open("/tmp/pillar_readings.json"))
def g(k,f="last",d="n/a"):
    v=R.get(k,{}).get(f); return d if v is None else v

def img(fn):
    p=os.path.join(CH,fn)
    if not os.path.exists(p): return "<div class='missing'>[chart missing: %s]</div>"%fn
    b=base64.b64encode(open(p,"rb").read()).decode()
    return f"<img src='data:image/png;base64,{b}' alt='{fn}'/>"

def fig(fn,cap):
    return f"<figure>{img(fn)}<figcaption>{cap}</figcaption></figure>"

OCEAN="#2389BB"; DUSK="#FF6723"; PORT="#892323"; STARBOARD="#238923"; DOLDRUMS="#898989"

# pillar blocks: (num, name, code, status_word, status_color, read_html, [(file,caption),...])
def chip(txt,color): return f"<span class='chip' style='background:{color}'>{txt}</span>"

pillars=[]

pillars.append((1,"Labor","LFI / LPI","NEUTRAL, fraying at the edge",OCEAN,
 f"""LFI sits at <b>{g('LFI')}</b>, essentially neutral and nowhere near the +0.5 fragile line. The composite is not the story yet. The flow underneath it is. Quits have rolled to <b>{g('JTSQUR')}%</b>, below the 2.0% line we treat as the pre-recession tell, which is the cleanest soft signal on the board. Claims stay tame, so there is no acute break, just a labor market that has stopped tightening and started leaking at the margin. Watch the quits-to-claims gap. The headline unemployment rate will be the last to know.""",
 [("p1_lfi.png","Labor Fragility composite, 3mo-smoothed z-score. Neutral, no fragility signal firing."),
  ("p1_quits.png","JOLTS quits rate. Below the 2.0% pre-recession threshold (dotted) for the first time this cycle."),
  ("p1_claims.png","Initial claims, 4-week average. Still historically low, no acute stress.")]))

pillars.append((2,"Prices","PCI","STICKY, last-mile stalled",DUSK,
 f"""PCI is near zero at <b>{g('PCI')}</b>, which understates the problem. Core PCE printed <b>{g('CorePCE_YoY')}%</b> YoY on the April release, the in-line-but-elevated number the Fed writes from, and the disinflation has flattened rather than continued. Market-implied inflation has stopped helping: 5Y5Y forward sits at <b>{g('T5YIFR')}%</b>, anchored above target, while the household survey channel is screaming a different number. The gap between the two is the live tension. Either the curve moves or the household does.""",
 [("p2_pci.png","Inflation Heat composite, smoothed z-score. Cooled off the 2022 peak, now drifting sideways near mean."),
  ("p2_corepce.png","Core PCE YoY. Re-acceleration off the lows, holding above the 2% target line."),
  ("p2_breakeven.png","5Y breakeven vs 5Y5Y forward. Long-run expectations sticky above target, not rolling over.")]))

pillars.append((3,"Growth","GCI","FIRM, above trend",STARBOARD,
 f"""GCI reads <b>{g('GCI')}</b>, firmly above its mean, which is the part of the picture that keeps recession probability contained. Industrial production is positive at <b>{g('INDPRO_YoY')}%</b> YoY and real retail at <b>{g('RealRetail_YoY')}%</b>, decelerating from last year but not contracting. This is the wealth-cohort economy still printing transactions. Growth is the reason the regime is late-cycle and not recession. It is also the thing that turns last when it turns.""",
 [("p3_gci.png","Activity Pulse composite, smoothed z-score. Running above trend, no growth scare in the diffusion."),
  ("p3_indpro.png","Industrial production YoY. Positive but flat, mid-cycle pace."),
  ("p3_retail.png","Real retail and food sales YoY. Decelerating off 2024 highs, still above zero.")]))

pillars.append((4,"Housing","HCI","FROZEN, rate-locked",DOLDRUMS,
 f"""HCI at <b>{g('HCI')}</b> is mildly positive, which masks a frozen market rather than a healthy one. Builder sentiment (NAHB) sits at <b>{g('NAHB')}</b>, deep in contraction territory, with the 30Y mortgage at <b>{g('MORTGAGE30US')}%</b> keeping both demand and existing-home turnover locked. Starts and permits are grinding sideways at low levels. This is the frozen equilibrium: nothing clears, nobody moves, and it stays that way until the long end gives or rates come down. Rate-sensitive and stuck.""",
 [("p4_hci.png","Housing Tide composite, smoothed z-score. Off the lows but no real thaw."),
  ("p4_starts.png","Starts vs permits. Range-bound at depressed levels, no breakout either way."),
  ("p4_nahb.png","NAHB builder sentiment (left) vs 30Y mortgage (right). Sentiment pinned in contraction while financing stays expensive.")]))

pillars.append((5,"Consumer","CCI","WEAK, cohort-split",PORT,
 f"""CCI is the second-weakest pillar on the board at <b>{g('CCI')}</b>. Caveat up front: this is one of the optimized composites we flagged as descriptively noisy, so read it alongside the proxy. UMich sits at <b>49.8</b> on the April final in the DB, and the May print landed at <b>44.8</b>, a record low. Yet retail ex-food is running <b>+{g('RSXFS_YoY')}%</b> YoY. That is the two-economies signature in one pillar: the squeezed cohort answers the survey, the wealth cohort prints the transaction. The composite weakness is real, the spending strength is real, and they belong to different households.""",
 [("p5_cci.png","Consumer Pulse composite, smoothed z-score. Among the weakest readings on the panel (optimized composite, read with proxy)."),
  ("p5_umich.png","UMich consumer sentiment. Near historic lows, the squeezed-cohort read."),
  ("p5_rsxfs.png","Retail sales ex food YoY (the proxy). Still firmly positive, the wealth-cohort read.")]))

pillars.append((6,"Business","BCI","STABLE, capex holding",OCEAN,
 f"""BCI reads <b>{g('BCI')}</b>, modestly positive. Same caveat as the consumer pillar: BCI is an optimized composite we lean on the new-orders proxy for. Core capital goods orders are running <b>+{g('NEWORDER_YoY')}%</b> YoY, a genuine acceleration that is mostly the AI-capex thread doing the heavy lifting. Capacity utilization at <b>{g('TCU')}%</b> is middling, neither tight nor slack. Capex is forward commitment, and right now the commitment is concentrated, not broad. The breadth of the orders matters more than the headline.""",
 [("p6_bci.png","Capex Thrust composite, smoothed z-score. Stable and positive (optimized composite, read with proxy)."),
  ("p6_neworder.png","Core capital goods new orders YoY (the proxy). Sharp acceleration, AI-capex concentrated."),
  ("p6_tcu.png","Total capacity utilization. Mid-range, no demand-pull pressure on prices.")]))

pillars.append((7,"Trade","TCI","RISK-OFF tilt",PORT,
 f"""TCI is the weakest pillar on the panel at <b>{g('TCI')}</b>, and it has deteriorated sharply over the year. The broad dollar at <b>{g('DTWEXBGS')}</b> has softened off its highs, which historically loosens global conditions, but the composite is reading the risk-tide as defensive. Trade balance remains structurally negative. This pillar is the rotation engine via dollar dynamics, and right now it is pulling toward caution, consistent with the capital-preservation regime.""",
 [("p7_tci.png","Global Risk Tide composite, smoothed z-score. Weakest pillar reading, defensive tilt."),
  ("p7_dollar.png","Broad dollar index. Off the highs, easing global financial conditions at the margin."),
  ("p7_tradebal.png","Trade balance, goods and services. Structurally negative, no inflection.")]))

pillars.append((8,"Government","FPI","ELEVATED, fiscal dominance",DUSK,
 f"""FPI sits in the elevated band at <b>{g('FPI')}</b>. This is the pillar carrying the macro story right now. The 10Y term premium has climbed to <b>{g('TermPrem10')}%</b>, roughly double its level two years ago, and that repricing, not the Fed path, is what is driving the long end. The monthly budget balance keeps the supply story heavy. Heavy issuance plus a thinner buyer base plus a new chair who wants the balance sheet smaller is the fiscal-dominance signature. The long end answers to this, not to the dot plot.""",
 [("p8_fpi.png","Fiscal Pressure composite, smoothed z-score. Elevated band, the load-bearing pillar this cycle."),
  ("p8_termprem.png","10Y term premium (ACM). Doubled in two years, carrying the long-end move."),
  ("p8_budget.png","Monthly federal budget balance. Persistent deficits keeping coupon supply heavy.")]))

pillars.append((9,"Financial","FCI / CLG","COMPLACENT, spreads asleep",STARBOARD,
 f"""FCI reads <b>{g('FCI')}</b> and CLG <b>{g('CLG')}</b>, both benign. The credit market is asleep. HY OAS sits at <b>{int(round(g('HY_OAS')*100))}bps</b> and IG at <b>{int(round(g('IG_OAS')*100))}bps</b>, both near the tights, complacent against the long-end stress and the labor leak. The curve has un-inverted: 10Y-2Y at <b>+{int(round(g('T10Y2Y')*100))}bps</b>, 10Y-3M at <b>+{int(round(g('T10Y3M')*100))}bps</b>, a bear steepener. Spreads lead defaults but lag everything the framework watches first. Credit confirming late is the whole reason the book is already defensive.""",
 [("p9_fci.png","Credit Tide composite, smoothed z-score. Benign, no credit stress in the read."),
  ("p9_spreads.png","HY vs IG OAS. Both near cycle tights, credit pricing no risk while the long end reprices."),
  ("p9_curve.png","Yield curve, 10Y-2Y and 10Y-3M. Re-steepening out of inversion, the bear-steepener pattern.")]))

pillars.append((10,"Plumbing","LCI","CUSHION GONE, funding still calm",DUSK,
 f"""LCI is neutral at <b>{g('LCI')}</b>, which buries the real signal. The RRP cushion that absorbed two years of QT is effectively exhausted at <b>${g('RRP')}bn</b>, down from triple digits a year ago. The next dollar of drain now lands on bank reserves directly, and reserves have fallen to roughly <b>${g('WRESBAL')/1e6:.2f}T</b>. The instrument that moves first when reserves get scarce, EFFR minus IORB, is still benign at <b>{g('EFFR_IORB_bps')}bps</b>, well under the +8bps acute line. So: the buffer is gone, the funding market has not signed off yet, and the gap between those two is the runway. It is shorter than it was.""",
 [("p10_lci.png","Liquidity Cushion composite, smoothed z-score. Reads neutral, masking an exhausted buffer."),
  ("p10_reserves.png","Reserves (left) vs RRP (right). The RRP cushion is gone, drain now hits reserves directly."),
  ("p10_effr.png","EFFR minus IORB (bps). Still benign, below the +8bps acute line. The trigger to watch.")]))

pillars.append((11,"Market Structure","MSI / SBD","THINNING under a calm tape",PORT,
 f"""MSI reads <b>{g('MSI')}</b>, mildly positive, but the internals are decaying under a record tape. Percent above the 50-day sits at <b>{g('PCT_ABOVE_50D')}%</b>, neutral, with no breadth thrust having fired. The McClellan Summation has collapsed to <b>{g('MCCLELLAN_SUM')}</b> from the high 300s a year ago, rolling over while the index makes highs. That is the non-confirmation in two independently-built instruments. Breadth divergence is distribution. The leaders are still leading, so this is not a sell signal, it is a do-not-chase signal.""",
 [("p11_msi.png","Market Breadth Pulse composite, smoothed z-score. Positive but fading."),
  ("p11_breadth.png","% of S&P above the 50-day. Neutral, no thrust (30/70 bands dotted), participation not broadening."),
  ("p11_mcclellan.png","McClellan Summation Index. Rolled over hard while the index printed records, the breadth-momentum decay.")]))

pillars.append((12,"Sentiment","SPI / SSD","NEUTRAL, no extreme to fade",OCEAN,
 f"""SPI is dead neutral at <b>{g('SPI')}</b>, up sharply off last year's washout but nowhere near a fade-able extreme. AAII bull-bear sits at <b>{g('AAII_BULL_BEAR')}pp</b>, mildly net-bearish, not the euphoria (>+30) or capitulation (<-20) that gives the contrarian read teeth. VIX at <b>{g('VIX')}</b> is calm. Sentiment is the fastest-moving pillar and right now it offers no edge in either direction. The signal this week is the structure underneath the calm, not the calm itself.""",
 [("p12_spi.png","Sentiment Tide composite, smoothed z-score. Neutral, no contrarian extreme."),
  ("p12_aaii.png","AAII bull-bear spread (pct points). Mildly bearish, inside the neutral band (+30/-20 dotted)."),
  ("p12_vix.png","VIX. Calm, complacent against the structural backdrop.")]))

# build pillar HTML
def block(p):
    num,name,code,status,color,read,figs=p
    figs_html="".join(fig(f,c) for f,c in figs)
    return f"""
    <section class='pillar'>
      <div class='phead'>
        <div class='pnum'>{num:02d}</div>
        <div class='ptitle'><h2>{name} <span class='code'>{code}</span></h2>
          <div class='pstatus'>{chip(status,color)}</div></div>
      </div>
      <p class='read'>{read}</p>
      <div class='figs'>{figs_html}</div>
    </section>"""

today=datetime.date.today().strftime("%B %d, %Y")
master_read=f"""The framework is in <b>capital preservation</b>. Ensemble Risk reads <b>{g('ENSEMBLE_RISK')}</b> (pre-crisis band), Warning Level is <b>RED ({int(g('WARNING_LEVEL'))})</b>, and the allocation multiplier has dropped to <b>{g('ALLOC_MULTIPLIER')}</b>. The regime composite (MRI) is more measured at <b>{g('MRI')}</b>, neutral, and base recession probability is contained at <b>{g('REC_PROB','last',0)*100:.0f}%</b>. That split is the whole read: the slow-moving regime engine still says late-cycle-not-recession, while the fast risk ensemble says stand closer to the door. The Discontinuity Premium sits in the EXTREME band at <b>{g('DISCONTINUITY_PREMIUM')}</b>, meaning the tape and the fundamentals have stopped telling the same story. Where the stress actually sits: the long end (Fiscal Pressure elevated, term premium doubling) and the plumbing (RRP cushion gone). Where it is conspicuously absent: credit (spreads at the tights) and volatility (VIX calm). The pillars that lead are nervous. The pillars that lag are asleep. That is the configuration the book is positioned for."""

pillar_html="".join(block(p) for p in pillars)

html=f"""<!DOCTYPE html><html lang='en'><head><meta charset='utf-8'>
<meta name='viewport' content='width=device-width,initial-scale=1'>
<title>Lighthouse Macro — 12-Pillar Internal Read</title>
<style>
 :root{{--ocean:#2389BB;--dusk:#FF6723;--dol:#898989;--ink:#15202b;}}
 *{{box-sizing:border-box}}
 body{{font-family:'Inter',-apple-system,'Segoe UI',sans-serif;color:var(--ink);
   max-width:920px;margin:0 auto;padding:0 28px 96px;line-height:1.55;font-size:15.5px;background:#fff}}
 .accent{{height:6px;background:linear-gradient(to right,var(--ocean) 0 66.6%,var(--dusk) 66.6% 100%);
   border-radius:3px;margin:34px 0 26px}}
 header h1{{font-family:'Montserrat',sans-serif;font-weight:800;font-size:30px;margin:0 0 6px;letter-spacing:-.3px}}
 header .sub{{color:var(--dol);font-size:14px;margin:0 0 4px}}
 .stamp{{font-family:'Source Code Pro',monospace;font-size:11px;color:var(--dol)}}
 .master{{background:#f6fafc;border:1px solid #e4eef3;border-left:4px solid var(--ocean);
   border-radius:8px;padding:20px 22px;margin:22px 0 14px}}
 .master h3{{font-family:'Montserrat',sans-serif;margin:0 0 10px;font-size:17px}}
 .dash{{display:flex;flex-wrap:wrap;gap:10px;margin:0 0 14px}}
 .metric{{background:#fff;border:1px solid #e4eef3;border-radius:7px;padding:8px 12px;min-width:120px}}
 .metric .k{{font-size:10.5px;color:var(--dol);text-transform:uppercase;letter-spacing:.4px}}
 .metric .v{{font-family:'Source Code Pro',monospace;font-size:18px;font-weight:600;color:var(--ink)}}
 .metric .v.red{{color:#892323}} .metric .v.amber{{color:#FF6723}}
 .pillar{{border-top:1px solid #eee;padding:26px 0 8px}}
 .phead{{display:flex;align-items:center;gap:14px;margin:0 0 8px}}
 .pnum{{font-family:'Montserrat',sans-serif;font-weight:800;font-size:30px;color:#dce7ec;line-height:1}}
 .ptitle h2{{font-family:'Montserrat',sans-serif;font-size:20px;margin:0;font-weight:700}}
 .ptitle .code{{font-size:12px;color:var(--dol);font-weight:500;font-family:'Source Code Pro',monospace}}
 .chip{{display:inline-block;color:#fff;font-size:11px;font-weight:600;padding:2px 10px;border-radius:20px;
   margin-top:5px;letter-spacing:.2px}}
 .read{{margin:6px 0 16px}}
 .figs{{display:grid;grid-template-columns:repeat(auto-fit,minmax(430px,1fr));gap:18px}}
 @media(max-width:760px){{.figs{{grid-template-columns:1fr}}}}
 .scorecard{{margin:4px 0 18px}} .scorecard img{{width:100%;max-width:780px;display:block;margin:0 auto;border:1px solid #e9eef1;border-radius:6px}}
 figure{{margin:0}}
 figure img{{width:100%;border:1px solid #e9eef1;border-radius:6px;display:block}}
 figcaption{{font-size:11.5px;color:#5a6b76;margin-top:6px;line-height:1.4}}
 .missing{{font-size:12px;color:#b00;padding:20px;border:1px dashed #b00}}
 footer{{margin-top:40px;padding-top:16px;border-top:1px solid #eee;font-size:11px;color:var(--dol);
   font-family:'Source Code Pro',monospace}}
</style></head><body>
<div class='accent'></div>
<header>
 <h1>The Twelve Pillars — Internal Read</h1>
 <p class='sub'>Pillar-by-pillar state of the framework. Internal working document, not for distribution.</p>
 <p class='stamp'>Generated {today} &nbsp;·&nbsp; readings as of latest available DB print &nbsp;·&nbsp; Lighthouse_Master.db</p>
</header>

<div class='master'>
 <h3>Master Composite — where the book stands</h3>
 <div class='scorecard'>{img('00_scorecard.png')}</div>
 <p class='read'>{master_read}</p>
 <div class='figs' style='grid-template-columns:1fr;max-width:680px;margin:14px auto 0'>
   {fig('00_mri.png','Macro Risk Index, full-history smoothed z-score with ±2σ bands. The master regime composite, currently neutral.')}
 </div>
</div>

{pillar_html}

<footer>Lighthouse Macro · Internal · The Twelve Pillars across three engines (Macro Dynamics 1-7 · Monetary Mechanics 8-10 · Market Structure 11-12) · MACRO, ILLUMINATED.</footer>
</body></html>"""

open(OUT,"w").write(html)
print("WROTE",OUT, "size KB", round(os.path.getsize(OUT)/1024))
