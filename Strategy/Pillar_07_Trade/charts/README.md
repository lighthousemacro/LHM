# Pillar 7 Trade — Chart Library

This is the **living chart library** for Pillar 7. Charts here are regenerated from `Lighthouse_Master.db` on each refresh. Target: 50+ charts total, ~80% evergreen, ~20% on-demand.

For the **frozen publication snapshot** of "Trade: The Pipeline" charts, see `../article/charts/`.

## File naming convention

```
NN_series_name.png
```

## Building the chartbook PDF

```bash
python build_chartbook.py
```

Produces `../Pillar_07_Trade_Chartbook.pdf`.

## Chart inventory (to populate)

### Trade balance
- [ ] `01_trade_balance.png` — Monthly trade balance with GDP ratio
- [ ] `02_exports_imports.png` — Total exports and imports YoY
- [ ] `03_current_account.png` — Current account / GDP

### Prices
- [ ] `04_import_prices.png` — Import price index YoY (with and without petroleum)
- [ ] `05_export_prices.png` — Export price index YoY
- [ ] `06_terms_of_trade.png` — Terms of trade YoY

### Dollar
- [ ] `07_dxy_broad.png` — Broad Trade-Weighted Dollar Index
- [ ] `08_dollar_yoy.png` — Dollar YoY with recession overlay
- [ ] `09_bis_reer.png` — BIS Real Effective Exchange Rate vs 10Y average

### Bilateral
- [ ] `10_china_trade.png` — China imports/exports share over time
- [ ] `11_mexico_vietnam.png` — China substitution patterns

### Supply chain
- [ ] `12_gscpi.png` — NY Fed Global Supply Chain Pressure Index
- [ ] `13_container_volume.png` — Port of LA container throughput
- [ ] `14_baltic_dry.png` — Baltic Dry Index

### Policy
- [ ] `15_effective_tariff.png` — Effective US tariff rate (historical)
- [ ] `16_eputrade.png` — Trade policy uncertainty index

### Capital flows
- [ ] `17_tic_flows.png` — TIC net long-term foreign flows
- [ ] `18_foreign_holdings.png` — Foreign official Treasury holdings

### Composite
- [ ] `19_tci_regime.png` — TCI composite with regime bands

(Add charts as new research surfaces.)

## Refresh cadence

Monthly with Census/BEA/BLS releases; weekly for container volume and Baltic Dry.
