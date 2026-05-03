# Lighthouse Macro — OpenBB Workspace Backend

FastAPI backend that exposes Lighthouse_Master.db and the Diagnostic Dozen framework as a set of OpenBB Workspace widgets and apps.

## Architecture

The framework is **the Diagnostic Dozen**: 12 pillars across 3 engines.

- **Macro Dynamics** (Pillars 1–7): Labor, Prices, Growth, Housing, Consumer, Business, Trade
- **Monetary Mechanics** (Pillars 8–10): Government, Financial, Plumbing
- **Market Structure** (Pillars 11–12): Structure, Sentiment

Composite indices surfaced as first-class widgets: MRI (master), LFI, LCI, FCI, CLG, MSI, SPI, SBD, SSD, CCI, PCI, GCI, HCI, BCI, TCI, GCI_Gov.

## Files

| Path | Purpose |
|---|---|
| `lhm_backend.py` | FastAPI app. Endpoints for catalog, observations, composites, synthesis. |
| `widgets.json` | Widget manifest consumed by OpenBB Workspace. 20 widgets. |
| `apps.json` | Five-screen app layout: Pulse / Asset Flow / Chain / Real Check / Divergence. |
| `scripts/discover_schema.py` | Phase 1 — interrogates the DB and emits `schema_manifest.md`. |
| `scripts/schema_manifest.md` | Generated. Tables, columns, dtypes, sample rows, date ranges. |

## Launch

```bash
/Users/bob/LHM/OpenBB/conda/envs/lhm-obb/bin/openbb-api \
    --app /Users/bob/LHM/Scripts/openbb_backend/lhm_backend.py \
    --name app \
    --host 127.0.0.1 \
    --port 6900
```

Then in OpenBB Workspace: **Settings → Backend → Add Custom Backend → `http://127.0.0.1:6900`**.

To regenerate the schema manifest after a pipeline run:

```bash
python3 /Users/bob/LHM/Scripts/openbb_backend/scripts/discover_schema.py
```

## Endpoint catalog

### Catalog / browse

| Endpoint | Purpose |
|---|---|
| `GET /health` | DB connectivity + global counts |
| `GET /categories` | All categories in `series_meta` with counts |
| `GET /sources` | All sources with counts |
| `GET /series` | List/search series. Filter: `category`, `source`, `search`, `limit` |

### Series and composites

| Endpoint | Purpose |
|---|---|
| `GET /observations?series_id=...` | Time series for one series |
| `GET /latest?series_ids=A,B,C` | Latest reading for many series |
| `GET /composites` | Latest reading per composite (one row per `index_id`) |
| `GET /composite_history?index_id=MRI` | Time series for a single composite |

### Panels (multi-series payloads)

| Endpoint | Series |
|---|---|
| `GET /breadth_panel` | `SPX_PCT_ABOVE_20D` / `_50D` / `_200D` |
| `GET /sentiment_panel` | `AAII_Bullish` / `AAII_Bearish` / `AAII_Bull_Bear_Spread` |
| `GET /rates_panel` | `DGS2` / `DGS5` / `DGS10` / `DGS30` / `MORTGAGE30US` |
| `GET /credit_panel` | `BAMLH0A0HYM2` (HY OAS) / `BAMLC0A0CM` (IG OAS) |
| `GET /plumbing_panel` | `RRPONTSYD` / `WALCL` / `WTREGEN` / `IORB` |

### Synthesis

| Endpoint | Purpose |
|---|---|
| `GET /pillar_heatmap` | Current z-score for every pillar composite |
| `GET /engine_summary` | Mean / mean abs / max abs z per engine |
| `GET /transmission_chain?chain_id=...` | Z-scores along a chain. Available: `plumbing_credit_labor`, `rates_housing_consumer`, `sentiment_structure_risk` |
| `GET /transmission_chain_table?chain_id=...` | Same payload, flat table shape |
| `GET /divergence?market_node=MSI&real_node=LFI` | Single market vs real-economy z-gap |
| `GET /divergence_grid` | All canonical pairs |

## Apps

Each app is a pre-configured Workspace screen. Open via the dashboard picker.

| App | Purpose | Key widgets |
|---|---|---|
| **01 The Pulse** | Where the framework stands right now | Health, engine summary, pillar heatmap, MRI history, pulse tiles |
| **02 Asset Flow** | Cross-asset surveillance | Rates / Credit / Plumbing / Breadth / Sentiment panels |
| **03 The Chain** | Transmission visualization | Lead/lag chain, pillar heatmap, composite drill-down |
| **04 Real Check** | Market vs real-economy reads | Pillar heatmap, composite history, divergence grid |
| **05 Divergence** | Risk surface | Pair view, divergence grid, supporting context |

## Brand and voice (markdown widgets)

When the backend emits text:

- "We" frame, not third-person
- No emdashes, no semicolons
- Threshold-aware language ("LFI at +0.7 — fragility elevated, not yet acute")
- Cite the actual reading and its threshold

Chart palette: Ocean `#2389BB`, Dusk `#FF6723`, Sea `#00BB89`, Sky `#23BBFF`, Venus `#FF2389`, Doldrums `#898989`, Starboard `#238923`, Port `#892323`. Border on every chart: 4pt solid Ocean.

## Open items

- Co-branded vs LHM-on-OpenBB visual treatment (alignment with Didier pending)
- Transmission chain lag estimates: precomputed table vs on-the-fly. Currently on-the-fly with full-history z-scores per node.
- IG OAS mnemonic in credit panel — verify `BAMLC0A0CM` matches DB; swap if a different `BAMLC0A0CMTRIV` style ID is used in `series_meta`.
