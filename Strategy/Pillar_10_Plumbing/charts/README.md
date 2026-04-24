# Pillar 10 Plumbing — Chart Library

This is the **living chart library** for Pillar 10. Charts here are regenerated from `Lighthouse_Master.db` on each refresh. Target: 50+ charts total, ~80% evergreen, ~20% on-demand.

For the **frozen publication snapshot** of "Plumbing: The Invisible Infrastructure" charts, see `../article/charts/`.

## File naming convention

```
NN_series_name.png
```

## Building the chartbook PDF

```bash
python build_chartbook.py
```

Produces `../Pillar_10_Plumbing_Chartbook.pdf`.

## Chart inventory (to populate)

### Reserves and buffer
- [ ] `01_reserves.png` — Bank reserves with LCLOR threshold
- [ ] `02_rrp.png` — Overnight RRP facility balance
- [ ] `03_tga.png` — Treasury General Account daily balance
- [ ] `04_buffer_stack.png` — Reserves + RRP combined buffer

### Fed balance sheet
- [ ] `05_walcl.png` — Fed total assets (QE/QT trajectory)
- [ ] `06_soma.png` — SOMA Treasury and MBS holdings
- [ ] `07_qt_pace.png` — Monthly balance sheet runoff

### Funding markets
- [ ] `08_sofr.png` — SOFR with IORB overlay
- [ ] `09_effr_iorb.png` — EFFR minus IORB spread
- [ ] `10_sofr_iorb.png` — SOFR minus IORB spread
- [ ] `11_gcf_tpr.png` — GCF-TPR spread

### Net liquidity
- [ ] `12_net_liquidity.png` — Net Liquidity Index (WALCL - TGA - RRP)
- [ ] `13_net_liquidity_vs_spx.png` — Net Liquidity vs S&P 500
- [ ] `14_net_liquidity_vs_btc.png` — Net Liquidity vs BTC

### Crypto-liquidity nexus
- [ ] `15_btc_correlation.png` — BTC-NDX 60-day correlation
- [ ] `16_stablecoin_supply.png` — USDT + USDC aggregate market cap
- [ ] `17_stablecoin_tbills.png` — Stablecoin T-bill holdings
- [ ] `18_btc_funding_rate.png` — BTC perpetual funding rate

### Dealer balance sheets
- [ ] `19_dealer_positions.png` — Primary dealer Treasury holdings
- [ ] `20_dealer_repo.png` — Dealer repo vs reverse repo

### Composite
- [ ] `21_lci_regime.png` — LCI composite with regime bands
- [ ] `22_cli.png` — Crypto Liquidity Impulse composite

(Add charts as new research surfaces.)

## Refresh cadence

Daily for SOFR, RRP, TGA, crypto; weekly for H.4.1 (WALCL, reserves); monthly for Z.1.
