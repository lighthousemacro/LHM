import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from datetime import datetime
from matplotlib.backends.backend_pdf import PdfPages

# --------------------------------------------------
# User-defined constants
# --------------------------------------------------
OCEAN_BLUE         = '2389BB'      # darker blue for lines
DEEP_ORANGE        = '#FF6B35'     # highlight orange
NEON_CAROLINA_BLUE = '#00C5FF'     # light blue accent
NEON_MAGENTA       = '#FF00FF'     # magenta accent
MED_LIGHT_GRAY     = '#999999'     # gray for baselines / gridlines
FRED_API_KEY       = '6dcc7a0d790cdcc28c1f751420ee9d27'

# --------------------------------------------------
# Utility functions
# --------------------------------------------------
def fred_api(series_id, api_key):
    """Fetch data from FRED API (JSON) and return a Pandas Series."""
    url = (
        f"https://api.stlouisfed.org/fred/series/observations"
        f"?series_id={series_id}&api_key={api_key}&file_type=json&observation_start=1990-01-01"
    )
    resp = requests.get(url)
    data = resp.json()['observations']
    dates = pd.to_datetime([obs['date'] for obs in data])
    values = [float(obs['value']) if obs['value'] not in ('', '.') else float('nan') for obs in data]
    series = pd.Series(values, index=dates, name=series_id).astype(float).resample('ME').mean()
    return series

def zscore(series):
    return (series - series.mean()) / series.std()

def percentile(series):
    return series.rank(pct=True)

def style_axes(ax, title):
    """Apply Lighthouse-style formatting and watermarks."""
    ax.set_title(title, loc='left', fontsize=14, fontweight='bold', color=f"#{OCEAN_BLUE}")
    fig = ax.get_figure()
    fig.text(0.01, 0.98, "LIGHTHOUSE MACRO", fontsize=10, color=f"#{OCEAN_BLUE}", alpha=0.7)
    fig.text(0.99, 0.02, "MACRO, ILLUMINATED.", fontsize=8, color=MED_LIGHT_GRAY, alpha=0.7, ha='right')
    ax.spines['top'].set_visible(True)
    ax.spines['right'].set_visible(True)
    for spine in ax.spines.values():
        spine.set_linewidth(1)
        spine.set_color(f"#{OCEAN_BLUE}")
    ax.grid(False)

def save_chart(fig, filename):
    fig.tight_layout()
    charts_dir = Path('charts')
    charts_dir.mkdir(exist_ok=True)
    fig.savefig(charts_dir / filename, dpi=200)
    plt.close(fig)

def plot_dual(data, labels, ylabels, title, fname):
    fig, ax = plt.subplots(figsize=(12, 6.75))
    ax.plot(data.index, data.iloc[:,0], color=f'#{OCEAN_BLUE}', lw=2.5, label=labels[0])
    ax.set_ylabel(ylabels[0], color=f'#{OCEAN_BLUE}')
    ax.tick_params(axis='y', labelcolor=f'#{OCEAN_BLUE}')
    ax2 = ax.twinx()
    ax2.plot(data.index, data.iloc[:,1], color=DEEP_ORANGE, lw=2.5, label=labels[1])
    ax2.set_ylabel(ylabels[1], color=DEEP_ORANGE)
    ax2.tick_params(axis='y', labelcolor=DEEP_ORANGE)
    lines, labs = ax.get_legend_handles_labels()
    lines2, labs2 = ax2.get_legend_handles_labels()
    ax2.legend(lines + lines2, labs + labs2, loc='upper left', fontsize=8)
    style_axes(ax, title)
    save_chart(fig, fname)

def plot_single(df, labels, ylabel, title, fname):
    fig, ax = plt.subplots(figsize=(12, 6.75))
    for idx, col in enumerate(df.columns):
        color = [f'#{OCEAN_BLUE}', DEEP_ORANGE, NEON_CAROLINA_BLUE, NEON_MAGENTA][idx % 4]
        ax.plot(df.index, df[col], color=color, lw=2.5, label=labels[idx])
    ax.set_ylabel(ylabel)
    ax.legend(loc='upper left')
    style_axes(ax, title)
    save_chart(fig, fname)

# --------------------------------------------------
# Download data from FRED (these calls require internet)
# --------------------------------------------------
print("Fetching data from FRED API...")
payems  = fred_api('PAYEMS', FRED_API_KEY)
jtsqur  = fred_api('JTSQUR', FRED_API_KEY)
jtshir  = fred_api('JTSHIR', FRED_API_KEY)
jtsldl  = fred_api('JTSLDL', FRED_API_KEY)
awhman  = fred_api('AWHMAN', FRED_API_KEY)
uemp27  = fred_api('UEMP27OV', FRED_API_KEY)
unrate  = fred_api('UNRATE', FRED_API_KEY)
hy_oas  = fred_api('BAMLH0A0HYM2', FRED_API_KEY)
bbb_oas = fred_api('BAMLC0A0CM', FRED_API_KEY)
dgs10   = fred_api('DGS10', FRED_API_KEY)
dgs2    = fred_api('DGS2', FRED_API_KEY)
sofr    = fred_api('SOFR', FRED_API_KEY)
effr    = fred_api('EFFR', FRED_API_KEY)
rrp     = fred_api('RRPONTSYD', FRED_API_KEY)
res     = fred_api('RESBALNS', FRED_API_KEY)
gdp     = fred_api('GDP', FRED_API_KEY)
sp500   = fred_api('SP500', FRED_API_KEY)
sp500_daily = sp500  # monthly resampled

print("Data fetched successfully. Computing metrics...")

# --------------------------------------------------
# Compute composites and metrics
# --------------------------------------------------
# Payroll YoY vs Quits Z
payroll_yoy = payems.pct_change(12) * 100
quits_z = zscore(jtsqur)
series1 = pd.concat([payroll_yoy, quits_z], axis=1).dropna()

# Hours vs headcount (2019=100)
payroll_norm = payems / payems.loc['2019-01-31'] * 100
hours_norm   = awhman / awhman.loc['2019-01-31'] * 100

# Hires/Quits & Quits/Layoffs
hires_to_quits   = (jtshir / jtsqur).dropna()
quits_to_layoffs = (jtsqur / jtsldl).dropna()

# Labor Fragility Index
frag_index = pd.concat([
    -zscore(jtsqur),
    zscore(uemp27),
    -zscore(awhman),
    -zscore(jtshir)
], axis=1).mean(axis=1)

# Labor Dynamism Index
dyn_index = pd.concat([
    zscore(jtsqur),
    zscore(jtshir),
    -zscore(uemp27)
], axis=1).mean(axis=1)

# Credit–Labor Lag (HY vs lagged fragility)
lagged_frag = frag_index.shift(6)
series7 = pd.concat([hy_oas, lagged_frag], axis=1).dropna()

# Heatmap percentiles
heat_df = pd.concat([
    percentile(frag_index),
    percentile(hy_oas),
    percentile(sofr - effr),
    percentile(dgs10 - dgs2),
    percentile(jtsqur),
    percentile(rrp / (rrp + res))
], axis=1).dropna()
heat_df.columns = ['LaborFrag','HY_OAS','Funding','YieldCurve','Quits','RRPShare']

# HY vs Unrate (dual)
series9 = pd.concat([hy_oas, unrate], axis=1).dropna()

# Spread differential (BBB - HY)
spread_diff = bbb_oas - hy_oas

# HY vol (6m standard deviation of spreads)
hy_vol = hy_oas.pct_change().rolling(126).std()

# RRP & Reserves / GDP
gdp_monthly = gdp.resample('ME').ffill()
rrp_gdp = (rrp / gdp_monthly) * 100
res_gdp = (res / gdp_monthly) * 100

# Yield curve vs funding
yc = dgs10 - dgs2
funding = sofr - effr
series13 = pd.concat([yc, funding], axis=1).dropna()

# Funding stress
funding_stress = zscore((sofr - effr).dropna()) + zscore((rrp / (rrp + res)).dropna())

# Transition tracker composite
credit_labor_gap = zscore(hy_oas - lagged_frag.dropna())
transition_tracker = (0.4*frag_index + 0.35*credit_labor_gap + 0.25*zscore(funding_stress)).dropna()

# SPX technicals
spx = sp500_daily.dropna()
ma50  = spx.rolling(50).mean()
ma200 = spx.rolling(200).mean()
series17 = pd.concat([spx, dgs10], axis=1).dropna()
series18 = pd.concat([spx, hy_oas], axis=1).dropna()

print("Metrics computed. Generating charts...")

# --------------------------------------------------
# Plot and save each chart
# --------------------------------------------------
# Chart 1
plot_dual(series1, ['Payrolls YoY','Quits (z)'], ['Percent','z-score'], 'Headline vs Flow: Payrolls vs Quits', 'chart1_dual_payrolls_quits.png')

# Chart 2
df2 = pd.DataFrame({'Hours': hours_norm, 'Headcount': payroll_norm}).dropna()
plot_single(df2, ['Hours (AWHMAN)','Headcount (PAYEMS)'], 'Index (2019=100)', 'Under the Hood: Hours vs Headcount', 'chart2_hours_employment.png')

# Chart 3
plot_single(pd.DataFrame({'Hires/Quits': hires_to_quits}).dropna(), ['Hires/Quits'], 'Ratio', 'Hires vs Quits Ratio', 'chart3_hires_quits_ratio.png')

# Chart 4
plot_single(pd.DataFrame({'Quits/Layoffs': quits_to_layoffs}).dropna(), ['Quits/Layoffs'], 'Ratio', 'Quits vs Layoffs Ratio', 'chart4_quits_layoffs_ratio.png')

# Chart 5
plot_single(pd.DataFrame({'Labor Fragility': frag_index}).dropna(), ['Labor Fragility'], 'z-score', 'Labor Fragility Index', 'chart5_labor_fragility.png')

# Chart 6
plot_single(pd.DataFrame({'Labor Dynamism': dyn_index}).dropna(), ['Labor Dynamism'], 'z-score', 'Labor Dynamism Index (High=Dynamic)', 'chart6_labor_dynamism.png')

# Chart 7
plot_dual(series7, ['HY OAS','Lagged Labor Fragility'], ['Percent','z-score'], 'When Credit Notices Labor', 'chart7_dual_credit_labor.png')

# Chart 8 – heatmap as image
fig, ax = plt.subplots(figsize=(12, 6.75))
sns.heatmap(heat_df.T, cmap='coolwarm', linewidths=.5, ax=ax, cbar_kws={'label': 'Percentile'})
ax.set_title('Transition Heatmap (Percentile Rank)', loc='left', fontsize=14, fontweight='bold')
ax.set_ylabel('')
ax.set_xlabel('')
fig.text(0.01, 0.98, "LIGHTHOUSE MACRO", fontsize=10, color=f"#{OCEAN_BLUE}", alpha=0.7)
fig.text(0.99, 0.02, "MACRO, ILLUMINATED.", fontsize=8, color=MED_LIGHT_GRAY, alpha=0.7, ha='right')
save_chart(fig, 'chart8_transition_heatmap.png')

# Chart 9
plot_dual(series9, ['HY OAS','Unemployment Rate'], ['Percent','Percent'], 'HY Spread vs Unemployment', 'chart9_dual_hy_unrate.png')

# Chart 10
plot_single(pd.DataFrame({'Spread Differential': spread_diff}).dropna(), ['Spread Differential (BBB-HY)'], 'Percent', 'The BBB Cliff', 'chart10_spread_differential.png')

# Chart 11
plot_single(pd.DataFrame({'HY Volatility': hy_vol}).dropna(), ['HY Spread Volatility (6m)'], 'Volatility', 'Credit Spread Volatility (6m)', 'chart11_hy_volatility.png')

# Chart 12
plot_single(pd.DataFrame({'RRP % GDP': rrp_gdp, 'Reserves % GDP': res_gdp}).dropna(), ['RRP % GDP','Reserves % GDP'], 'Percent', 'RRP and Reserves vs GDP', 'chart12_rrp_reserves_gdp.png')

# Chart 13
plot_dual(series13, ['Yield Curve (10Y-2Y)','SOFR - EFFR'], ['bp','bp'], 'Yield Curve vs Funding Spread', 'chart13_dual_yieldcurve_funding.png')

# Chart 14
plot_single(pd.DataFrame({'Funding Stress': funding_stress}).dropna(), ['Funding Stress'], 'z-score', 'Funding Stress Index', 'chart14_funding_stress.png')

# Chart 15
plot_single(pd.DataFrame({'Transition Tracker': transition_tracker}).dropna(), ['Transition Tracker'], 'Composite Index', 'Transition Tracker Composite', 'chart15_transition_tracker.png')

# Chart 16
plot_single(pd.DataFrame({'SPX': spx, 'MA50': ma50, 'MA200': ma200}).dropna(), ['S&P 500','50-day MA','200-day MA'], 'Index Level', 'S&P 500: 50 & 200-Day MAs', 'chart16_sp500_ma.png')

# Chart 17
plot_dual(series17, ['SPX','10Y Yield'], ['Index','Percent'], 'S&P 500 vs 10Y Yield', 'chart17_sp500_vs_10y.png')

# Chart 18
plot_dual(series18, ['SPX','HY OAS'], ['Index','Percent'], 'S&P 500 vs HY OAS', 'chart18_sp500_vs_hy.png')

print("All charts generated to ./charts/")

# --------------------------------------------------
# Export data to CSV
# --------------------------------------------------
print("Exporting data to CSV...")
exports_dir = Path('exports')
exports_dir.mkdir(exist_ok=True)

# Combine all key metrics into one dataframe
export_data = {
    "payroll_yoy": payroll_yoy,
    "quits_z": quits_z,
    "payroll_norm": payroll_norm,
    "hours_norm": hours_norm,
    "hires_to_quits": hires_to_quits,
    "quits_to_layoffs": quits_to_layoffs,
    "labor_fragility": frag_index,
    "labor_dynamism": dyn_index,
    "lagged_fragility": lagged_frag,
    "credit_labor_gap": credit_labor_gap,
    "funding_stress": funding_stress,
    "transition_tracker": transition_tracker,
    "spx": spx,
    "spx_ma50": ma50,
    "spx_ma200": ma200,
    "hy_oas": hy_oas,
    "bbb_oas": bbb_oas,
    "unrate": unrate,
    "spread_diff": spread_diff,
    "hy_vol": hy_vol,
    "rrp_gdp": rrp_gdp,
    "res_gdp": res_gdp,
    "yield_curve": yc,
    "funding_spread": funding,
    "dgs10": dgs10,
    "dgs2": dgs2,
    "sofr": sofr,
    "effr": effr
}

combined_df = pd.concat(export_data, axis=1)
csv_path = exports_dir / "macro_dashboard_data.csv"
combined_df.to_csv(csv_path)
print(f"Data exported to {csv_path}")

# Also export the heatmap data separately
heatmap_path = exports_dir / "transition_heatmap_data.csv"
heat_df.to_csv(heatmap_path)
print(f"Heatmap data exported to {heatmap_path}")

# --------------------------------------------------
# Generate PDF report with all charts
# --------------------------------------------------
print("Generating PDF report...")
charts_dir = Path('charts')
pdf_path = exports_dir / "macro_dashboard_charts.pdf"

with PdfPages(pdf_path) as pdf:
    # Add a cover page
    fig = plt.figure(figsize=(11, 8.5))
    fig.text(0.5, 0.6, 'LIGHTHOUSE MACRO',
             ha='center', va='center', fontsize=32, fontweight='bold', color=f"#{OCEAN_BLUE}")
    fig.text(0.5, 0.5, 'Macro Dashboard Report',
             ha='center', va='center', fontsize=20, color=f"#{OCEAN_BLUE}")
    fig.text(0.5, 0.4, f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}',
             ha='center', va='center', fontsize=12, color=MED_LIGHT_GRAY)
    fig.text(0.5, 0.1, 'MACRO, ILLUMINATED.',
             ha='center', va='center', fontsize=10, color=MED_LIGHT_GRAY, alpha=0.7)
    plt.axis('off')
    pdf.savefig(fig, bbox_inches='tight')
    plt.close()

    # Add all chart images
    for chart_file in sorted(charts_dir.glob("chart*.png")):
        fig = plt.figure(figsize=(11, 8.5))
        img = plt.imread(chart_file)
        plt.imshow(img)
        plt.axis('off')
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()

print(f"PDF report generated at {pdf_path}")

# --------------------------------------------------
# Summary statistics
# --------------------------------------------------
print("\n" + "="*60)
print("DASHBOARD SUMMARY")
print("="*60)
print(f"Latest SPX close: {spx.iloc[-1]:,.2f}")
print(f"SPX 50-day MA: {ma50.iloc[-1]:,.2f}")
print(f"SPX 200-day MA: {ma200.iloc[-1]:,.2f}")
print(f"\nLabor Fragility (latest): {frag_index.dropna().iloc[-1]:.2f}")
print(f"Labor Dynamism (latest): {dyn_index.dropna().iloc[-1]:.2f}")
print(f"Transition Tracker (latest): {transition_tracker.iloc[-1]:.2f}")
print(f"\nHY OAS: {hy_oas.dropna().iloc[-1]:.2f}%")
print(f"BBB OAS: {bbb_oas.dropna().iloc[-1]:.2f}%")
print(f"Spread Differential (BBB-HY): {spread_diff.dropna().iloc[-1]:.2f}%")
print(f"\nFunding Stress: {funding_stress.dropna().iloc[-1]:.2f}")
print(f"Yield Curve (10Y-2Y): {yc.dropna().iloc[-1]:.2f} bp")
print(f"Funding Spread (SOFR-EFFR): {funding.dropna().iloc[-1]:.2f} bp")
print(f"\nUnemployment Rate: {unrate.dropna().iloc[-1]:.2f}%")
print(f"Payroll YoY: {payroll_yoy.dropna().iloc[-1]:.2f}%")
print("="*60)
print(f"\nAll outputs saved to:")
print(f"  Charts: ./charts/ (18 PNG files)")
print(f"  Data: ./exports/macro_dashboard_data.csv")
print(f"  Heatmap: ./exports/transition_heatmap_data.csv")
print(f"  Report: ./exports/macro_dashboard_charts.pdf")
print("="*60)
