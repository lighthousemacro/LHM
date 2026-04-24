# Pillar 2 Prices — Chart Library

This is the **living chart library** for Pillar 2. Charts here are regenerated from `Lighthouse_Master.db` on each refresh. Target: 50+ charts total, ~80% evergreen (same series, same layout, refreshed data), ~20% created on demand for specific research.

For the **frozen publication snapshot** of "Prices: The Transmission Belt" charts, see `../article/charts/`.

## File naming convention

```
NN_series_name.png
```

Where `NN` is a two-digit number that drives PDF page order. Zero-pad to stay under 99. Examples: `01_headline_cpi.png`, `02_core_cpi_vs_target.png`, `03_supercore.png`.

## Building the chartbook PDF

```bash
python build_chartbook.py
```

Produces `../Pillar_02_Prices_Chartbook.pdf` (one level up) with a branded cover page plus every PNG in this folder, sorted by filename. Cover uses the 23/89/BB palette (Ocean `#2389BB` primary, Dusk `#FF6723` accent).

## Chart inventory (to populate)

Chart slots live here. Fill them with production PNGs generated from the Master DB via the `chart-god` and `lhm-data-analyst` skills.

### Core inflation measures
- [ ] `01_headline_cpi.png` — CPI YoY vs 2% target, recession shading
- [ ] `02_core_cpi.png` — Core CPI YoY vs 2% target
- [ ] `03_core_pce.png` — Core PCE YoY (Fed's preferred gauge)
- [ ] `04_supercore.png` — Services ex-Shelter YoY
- [ ] `05_trimmed_mean_pce.png` — Trimmed-mean PCE, sticky CPI, median CPI

### Composition
- [ ] `06_goods_vs_services.png` — Goods CPI vs Services CPI YoY spread
- [ ] `07_shelter_cpi.png` — Shelter CPI vs market rent indices (Apartment List, Zillow ZORI)
- [ ] `08_energy_cpi.png` — Energy CPI contribution to headline

### Expectations
- [ ] `09_5y5y_inflation.png` — 5Y5Y forward inflation (Fed anchor gauge)
- [ ] `10_breakevens.png` — 5Y vs 10Y breakevens
- [ ] `11_umich_expectations.png` — UMich 1yr and 5-10yr inflation expectations

### Composite
- [ ] `12_pci_regime.png` — PCI composite with regime bands

(Add charts as new research surfaces. Update inventory here.)

## Refresh cadence

Target: automated daily refresh via pipeline. Manual refresh: whenever a major CPI, PCE, or ECI release drops.
