# Pillar 11 Market Structure — Chart Library

This is the **living chart library** for Pillar 11. Charts here are regenerated from `Lighthouse_Master.db` and market data providers on each refresh. Target: 50+ charts total, ~80% evergreen, ~20% on-demand.

For the **frozen publication snapshot** of "Market Structure: The Weight of Evidence" charts, see `../article/charts/`.

## File naming convention

```
NN_series_name.png
```

## Building the chartbook PDF

```bash
python build_chartbook.py
```

Produces `../Pillar_11_Market_Structure_Chartbook.pdf`.

## Chart inventory (to populate)

### Trend
- [ ] `01_spx_200d.png` — SPX vs 200d MA with distance bands
- [ ] `02_ma_stack.png` — 20d/50d/200d MA alignment
- [ ] `03_golden_death_cross.png` — Historical 50d/200d crosses

### Momentum
- [ ] `04_zroc_63d.png` — Z-RoC (63-day) with ±1σ bands
- [ ] `05_zroc_21d.png` — Z-RoC (21-day) shorter horizon
- [ ] `06_rsi.png` — RSI(14) overbought/oversold

### Breadth
- [ ] `07_breadth_20d.png` — % stocks above 20d MA (thrust detection)
- [ ] `08_breadth_50d.png` — % stocks above 50d MA (primary)
- [ ] `09_breadth_200d.png` — % stocks above 200d MA
- [ ] `10_nh_nl.png` — Net 52-week highs minus lows
- [ ] `11_ad_line.png` — Advance/decline line with slope
- [ ] `12_mcclellan.png` — McClellan Oscillator and Summation

### Relative strength
- [ ] `13_r2k_vs_spx.png` — Russell 2000 vs SPX relative strength
- [ ] `14_equal_weight.png` — Equal-weight RSP vs cap-weight SPY
- [ ] `15_sector_rotation.png` — Sector YoY vs SPX YoY

### Factor structure
- [ ] `16_value_vs_growth.png` — IVE vs IVW relative performance
- [ ] `17_quality.png` — QUAL vs SPX
- [ ] `18_low_vol.png` — SPLV vs SPX

### Volatility
- [ ] `19_vix.png` — VIX with regime bands
- [ ] `20_vix_term_structure.png` — VIX/VIX3M ratio
- [ ] `21_skew.png` — CBOE SKEW index
- [ ] `22_put_call.png` — Put/Call ratio (10d MA)

### Cross-asset structure
- [ ] `23_stock_bond_correlation.png` — 60d rolling correlation
- [ ] `24_cyclical_defensive.png` — Cyclical vs defensive spread

### Composites
- [ ] `25_msi_regime.png` — MSI composite with regime bands
- [ ] `26_sbd.png` — Structure-Breadth Divergence
- [ ] `27_ssd.png` — Sentiment-Structure Divergence

(Add charts as new research surfaces.)

## Refresh cadence

Daily for all market data and breadth; weekly for sector rotation and factor analysis.
