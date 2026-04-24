# Pillar 9 Financial — Chart Library

This is the **living chart library** for Pillar 9. Charts here are regenerated from `Lighthouse_Master.db` on each refresh. Target: 50+ charts total, ~80% evergreen, ~20% on-demand.

For the **frozen publication snapshot** of "Financial: The Cascade" charts, see `../article/charts/`.

## File naming convention

```
NN_series_name.png
```

## Building the chartbook PDF

```bash
python build_chartbook.py
```

Produces `../Pillar_09_Financial_Chartbook.pdf`.

## Chart inventory (to populate)

### Credit spreads
- [ ] `01_hy_oas.png` — HY OAS (with percentile bands)
- [ ] `02_ig_oas.png` — IG OAS
- [ ] `03_bbb_a_ratio.png` — BBB/A ratio (quality migration gauge)
- [ ] `04_ccc_b_spread.png` — CCC-B spread (distressed mispricing)
- [ ] `05_em_vs_us_hy.png` — EM sovereign vs US HY

### Yield curve
- [ ] `06_10y_2y.png` — 10Y-2Y spread with recession shading
- [ ] `07_10y_3m.png` — 10Y-3M (Fed's preferred)
- [ ] `08_curve_segments.png` — 2s, 5s, 10s, 30s snapshot
- [ ] `09_real_yield_curve.png` — TIPS curve

### Financial conditions composites
- [ ] `10_nfci.png` — Chicago Fed NFCI
- [ ] `11_nfci_components.png` — NFCI Credit/Leverage/Risk decomposition
- [ ] `12_stl_fsi.png` — St. Louis FSI vs NFCI

### Bank lending
- [ ] `13_ci_loan_growth.png` — C&I loan growth YoY
- [ ] `14_sloos_tightening.png` — SLOOS net tightening (large + small)
- [ ] `15_real_estate_loans.png` — Real estate loan growth (CRE + mortgage)

### Equity markets
- [ ] `16_equity_risk_premium.png` — Earnings yield minus real 10Y
- [ ] `17_spx_forward_pe.png` — S&P 500 forward P/E
- [ ] `18_breadth_200dma.png` — % stocks above 200d MA

### Volatility
- [ ] `19_vix.png` — VIX with regime bands
- [ ] `20_vix_term_structure.png` — VIX / VIX3M (contango/backwardation)
- [ ] `21_move_vix_ratio.png` — MOVE/VIX ratio

### Real rates
- [ ] `22_real_fed_funds.png` — Real Fed Funds vs r* estimates
- [ ] `23_real_10y.png` — Real 10Y (TIPS)

### Plumbing (cross-linked with Pillar 10)
- [ ] `24_reserves.png` — Bank reserves with LCLOR threshold
- [ ] `25_rrp_tga.png` — RRP and TGA trajectories

### Composite
- [ ] `26_fci_regime.png` — FCI composite with regime bands
- [ ] `27_clg.png` — Credit-Labor Gap (HY OAS - LFI z-scores)

(Add charts as new research surfaces.)

## Refresh cadence

Daily for spreads, yields, volatility; weekly for bank lending, NFCI; quarterly for SLOOS.
