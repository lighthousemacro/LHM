# Pillar 6 Business — Chart Library

This is the **living chart library** for Pillar 6. Charts here are regenerated from `Lighthouse_Master.db` on each refresh. Target: 50+ charts total, ~80% evergreen, ~20% on-demand.

For the **frozen publication snapshot** of "Business: The Forward Commitment" charts, see `../article/charts/`.

## File naming convention

```
NN_series_name.png
```

## Building the chartbook PDF

```bash
python build_chartbook.py
```

Produces `../Pillar_06_Business_Chartbook.pdf`.

## Chart inventory (to populate)

### Small business sentiment
- [ ] `01_nfib_optimism.png` — NFIB Optimism Index with recession shading
- [ ] `02_nfib_hiring_plans.png` — NFIB Hiring Plans net %
- [ ] `03_nfib_capex_plans.png` — NFIB Capex Plans net %

### Capex and orders
- [ ] `04_core_capex_orders.png` — Core capital goods orders YoY
- [ ] `05_bookings_billings.png` — Orders/Shipments ratio
- [ ] `06_durable_goods.png` — Durable goods orders YoY

### Inventories
- [ ] `07_is_ratio.png` — Inventory/Sales ratio vs trend
- [ ] `08_ism_new_orders_inventories.png` — ISM New Orders minus Inventories

### Surveys
- [ ] `09_ism_manufacturing.png` — ISM Mfg composite + sub-components
- [ ] `10_ism_services.png` — ISM Services composite + sub-components
- [ ] `11_regional_fed_composite.png` — Average of Philly/Empire/Dallas/Richmond/KC

### Profits and margins
- [ ] `12_sp500_earnings.png` — S&P 500 earnings YoY
- [ ] `13_sp500_margins.png` — S&P 500 net margin
- [ ] `14_earnings_revisions.png` — Earnings revision ratio

### Credit
- [ ] `15_sloos_ci.png` — SLOOS net tightening (large vs small firm)
- [ ] `16_ci_loan_growth.png` — C&I loan growth YoY

### Composite
- [ ] `17_bci_regime.png` — BCI composite with regime bands

(Add charts as new research surfaces.)

## Refresh cadence

Monthly with NFIB, ISM releases; quarterly with SLOOS and earnings.
