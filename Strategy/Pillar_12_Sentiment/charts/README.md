# Pillar 12 Sentiment — Chart Library

This is the **living chart library** for Pillar 12. Charts here are regenerated from `Lighthouse_Master.db` and sentiment data providers on each refresh. Target: 50+ charts total, ~80% evergreen, ~20% on-demand.

For the **frozen publication snapshot** of "Sentiment & Positioning: The Contrarian Edge" charts, see `../article/charts/`.

## File naming convention

```
NN_series_name.png
```

## Building the chartbook PDF

```bash
python build_chartbook.py
```

Produces `../Pillar_12_Sentiment_Chartbook.pdf`.

## Chart inventory (to populate)

### Retail sentiment
- [ ] `01_aaii_bull_bear.png` — AAII Bull-Bear spread with extreme bands
- [ ] `02_aaii_4wk.png` — AAII 4-week smoothed spread
- [ ] `03_ii_bull_bear.png` — Investors Intelligence Bull-Bear
- [ ] `04_cnn_fear_greed.png` — CNN Fear & Greed composite (with 7 components)
- [ ] `05_umich_sentiment.png` — UMich consumer sentiment

### Professional positioning
- [ ] `06_naaim_exposure.png` — NAAIM Exposure Index with regime bands
- [ ] `07_cot_asset_managers.png` — COT Asset Manager net position (SPX)
- [ ] `08_cot_leveraged.png` — COT Leveraged Funds net position
- [ ] `09_gfms_cash.png` — BofA GFMS cash level % (institutional)

### Options
- [ ] `10_put_call_10d.png` — Put/Call ratio (10-day MA) with extremes
- [ ] `11_equity_pc.png` — Equity-only put/call
- [ ] `12_vix.png` — VIX with regime bands and recession shading
- [ ] `13_vix_term_structure.png` — VIX / VIX3M ratio (contango/backwardation)
- [ ] `14_skew.png` — CBOE SKEW (tail risk pricing)

### Flows
- [ ] `15_equity_etf_flows.png` — ETF equity flows (4-wk sum)
- [ ] `16_mmf_assets.png` — Money market fund assets (dry powder)
- [ ] `17_margin_debt.png` — FINRA margin debt YoY growth

### Behavioral
- [ ] `18_google_trends.png` — "recession" and "crash" search intensity
- [ ] `19_wsb_mentions.png` — WSB ticker mention volume
- [ ] `20_btc_as_sentiment.png` — BTC as retail risk-on/off proxy
- [ ] `21_0dte_volume.png` — 0DTE options share of SPX volume

### Composite
- [ ] `22_spi_regime.png` — SPI composite with regime bands
- [ ] `23_ssd.png` — Sentiment-Structure Divergence (bridge to Pillar 11)

### Historical extremes
- [ ] `24_capitulation_events.png` — Historical SPI > +1.5 events
- [ ] `25_blow_off_events.png` — Historical SPI < -1.0 events

(Add charts as new research surfaces.)

## Refresh cadence

Weekly for AAII/II/NAAIM; daily for VIX family, put/call, BTC; monthly for GFMS and margin debt.
