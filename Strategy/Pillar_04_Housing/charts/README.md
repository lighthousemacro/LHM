# Pillar 4 Housing — Chart Library

This is the **living chart library** for Pillar 4. Charts here are regenerated from `Lighthouse_Master.db` on each refresh. Target: 50+ charts total, ~80% evergreen, ~20% on-demand.

For the **frozen publication snapshot** of "Housing: The Collateral Engine" charts, see `../article/charts/`.

## File naming convention

```
NN_series_name.png
```

## Building the chartbook PDF

```bash
python build_chartbook.py
```

Produces `../Pillar_04_Housing_Chartbook.pdf`.

## Chart inventory (to populate)

### Construction
- [ ] `01_housing_starts.png` — Starts YoY with recession shading
- [ ] `02_permits.png` — Building permits YoY
- [ ] `03_completions.png` — Completions and months of supply

### Sales
- [ ] `04_existing_home_sales.png` — Existing home sales monthly SAAR
- [ ] `05_new_home_sales.png` — New home sales SAAR
- [ ] `06_pending_sales.png` — NAR pending home sales (leads existing by 1-2 months)

### Prices
- [ ] `07_case_shiller.png` — Case-Shiller National and 20-city
- [ ] `08_fhfa_hpi.png` — FHFA HPI (conforming mortgages)
- [ ] `09_zillow_zhvi.png` — Zillow ZHVI (broader coverage)

### Affordability and mortgage
- [ ] `10_mortgage_rates.png` — 30Y fixed mortgage (Freddie PMMS)
- [ ] `11_mortgage_spread.png` — Primary-secondary spread + MBS OAS
- [ ] `12_affordability.png` — NAR affordability index
- [ ] `13_mortgage_apps.png` — MBA purchase and refi indexes

### Supply / inventory
- [ ] `14_months_supply.png` — Existing + new home months of supply
- [ ] `15_rental_market.png` — Apartment List + Zillow ZORI vs CPI shelter

### Builder sentiment
- [ ] `16_nahb_hmi.png` — NAHB Housing Market Index composite

### Composite
- [ ] `17_hci_regime.png` — HCI composite with regime bands

(Add charts as new research surfaces.)

## Refresh cadence

Monthly with Census/NAR/NAHB/Freddie releases; weekly for Zillow and Redfin alternative data.
