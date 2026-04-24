# Pillar 3 Growth — Chart Library

This is the **living chart library** for Pillar 3. Charts here are regenerated from `Lighthouse_Master.db` on each refresh. Target: 50+ charts total, ~80% evergreen, ~20% on-demand.

For the **frozen publication snapshot** of "Growth: The Second Derivative" charts, see `../article/charts/`.

## File naming convention

```
NN_series_name.png
```

Two-digit numeric prefix drives PDF page order.

## Building the chartbook PDF

```bash
python build_chartbook.py
```

Produces `../Pillar_03_Growth_Chartbook.pdf`.

## Chart inventory (to populate)

### Headline GDP and components
- [ ] `01_gdp_yoy.png` — Real GDP YoY with recession shading
- [ ] `02_gdi_gdp_gap.png` — GDP vs GDI divergence
- [ ] `03_gdp_components.png` — PCE, investment, government, net exports contributions

### Leading indicators
- [ ] `04_industrial_production.png` — IP YoY with ISM Manufacturing overlay
- [ ] `05_ism_manufacturing.png` — ISM Mfg composite with 50-line
- [ ] `06_ism_services.png` — ISM Services composite
- [ ] `07_services_mfg_spread.png` — Services-Manufacturing PMI spread

### Real-time trackers
- [ ] `08_atlanta_gdpnow.png` — Atlanta Fed GDPNow nowcast
- [ ] `09_ny_fed_nowcast.png` — NY Fed GDP nowcast
- [ ] `10_wei.png` — NY Fed Weekly Economic Index

### Activity indicators
- [ ] `11_retail_sales.png` — Real retail sales YoY
- [ ] `12_capex_orders.png` — Core capital goods orders YoY
- [ ] `13_housing_starts.png` — Housing starts and permits
- [ ] `14_capacity_utilization.png` — Capacity utilization vs long-run average

### Composite
- [ ] `15_gci_regime.png` — GCI composite with regime bands

(Add charts as new research surfaces.)

## Refresh cadence

Quarterly with BEA GDP releases, monthly with ISM/IP releases.
