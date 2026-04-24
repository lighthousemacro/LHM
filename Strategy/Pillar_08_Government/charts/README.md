# Pillar 8 Government — Chart Library

This is the **living chart library** for Pillar 8. Charts here are regenerated from `Lighthouse_Master.db` on each refresh. Target: 50+ charts total, ~80% evergreen, ~20% on-demand.

For the **frozen publication snapshot** of "Government: The Fiscal Overhang" charts, see `../article/charts/`.

## File naming convention

```
NN_series_name.png
```

## Building the chartbook PDF

```bash
python build_chartbook.py
```

Produces `../Pillar_08_Government_Chartbook.pdf`.

## Chart inventory (to populate)

### Deficit flow
- [ ] `01_deficit_gdp.png` — Deficit / GDP with recession shading
- [ ] `02_primary_deficit.png` — Primary deficit (ex-interest) / GDP
- [ ] `03_receipts_outlays.png` — Federal receipts and outlays YoY

### Debt stock
- [ ] `04_debt_gdp.png` — Debt held by public / GDP (long history)
- [ ] `05_debt_maturity.png` — WAM (Weighted Average Maturity)
- [ ] `06_foreign_holdings.png` — Foreign % of public debt

### Interest expense
- [ ] `07_interest_outlays.png` — Interest / Outlays (vs defense spending)
- [ ] `08_interest_gdp.png` — Interest / GDP trajectory
- [ ] `09_wai_vs_10y.png` — Weighted Avg Interest Rate vs 10Y yield

### Issuance
- [ ] `10_quarterly_issuance.png` — Net marketable borrowing by quarter
- [ ] `11_bills_share.png` — Bills as % of marketable debt
- [ ] `12_auction_tails.png` — 10Y auction tail (3M avg)
- [ ] `13_dealer_takedown.png` — Primary dealer take-down share

### Term premium
- [ ] `14_term_premium.png` — ACM 10Y term premium
- [ ] `15_real_10y.png` — Real 10Y (TIPS) yield with recession shading
- [ ] `16_5y5y_inflation.png` — 5Y5Y forward inflation

### Political
- [ ] `17_us_cds.png` — 1Y US sovereign CDS spread
- [ ] `18_tga_balance.png` — Treasury General Account daily balance

### Composite
- [ ] `19_gci_gov_regime.png` — GCI-Gov composite with regime bands

(Add charts as new research surfaces.)

## Refresh cadence

Monthly with MTS release; daily for TGA and term premium; quarterly for TIC and refunding.
