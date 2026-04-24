# Pillar 5 Consumer — Chart Library

This is the **living chart library** for Pillar 5. Charts here are regenerated from `Lighthouse_Master.db` on each refresh. Target: 50+ charts total, ~80% evergreen, ~20% on-demand.

For the **frozen publication snapshot** of "Consumer: The Last Domino" charts, see `../article/charts/`.

## File naming convention

```
NN_series_name.png
```

## Building the chartbook PDF

```bash
python build_chartbook.py
```

Produces `../Pillar_05_Consumer_Chartbook.pdf`.

## Chart inventory (to populate)

### Spending flows
- [ ] `01_real_pce.png` — Real PCE YoY with recession shading
- [ ] `02_pce_goods_services.png` — Goods vs Services PCE
- [ ] `03_durables_vs_nondurables.png` — Durables, nondurables, services decomposition
- [ ] `04_retail_sales_control.png` — Retail Sales Control Group (GDP proxy)

### Income and savings
- [ ] `05_real_dpi.png` — Real Disposable Personal Income YoY
- [ ] `06_saving_rate.png` — Personal saving rate with pre-pandemic trend
- [ ] `07_excess_savings.png` — SF Fed excess savings stock

### Credit
- [ ] `08_cc_balances.png` — Credit card balances (NY Fed)
- [ ] `09_cc_delinquency.png` — Credit card delinquency rate
- [ ] `10_auto_delinquency.png` — Auto loan delinquency
- [ ] `11_dsr.png` — Debt service ratio

### Confidence
- [ ] `12_cb_confidence.png` — Conference Board Present + Expectations spread
- [ ] `13_umich_sentiment.png` — UMich consumer sentiment
- [ ] `14_cnn_fear_greed.png` — CNN Fear & Greed composite

### High-frequency
- [ ] `15_card_spending.png` — BofA/JPM Chase card spending YoY
- [ ] `16_trade_down.png` — Walmart/Target same-store sales spread

### Composite
- [ ] `17_cci_regime.png` — CCI composite with regime bands
- [ ] `18_stress_stages.png` — 4-stage stress sequence visualization

(Add charts as new research surfaces.)

## Refresh cadence

Monthly with BEA, Census, Conference Board, UMich releases; weekly for card spending.
