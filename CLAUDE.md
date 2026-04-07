# CLAUDE.md — LHM (Lighthouse Macro Monorepo)

> Single source of truth for Lighthouse Macro's codebase. This file helps AI assistants be immediately productive.

## Project Overview

**LHM** is the internal monorepo for **Lighthouse Macro**, an institutional-grade macro research firm founded by Bob Sheehan, CFA, CMT. It houses:

- A daily data pipeline fetching from 10+ government/financial data sources
- Proprietary composite indices (MRI, LFI, LCI, CLG, and pillar composites)
- A quantitative modeling/backtesting framework (`lighthouse_quant`)
- Chart generation scripts following strict brand standards
- Automation for morning briefs, threshold alerts, and content publishing
- A 12-pillar analytical framework covering the full macro landscape

**Tagline:** MACRO, ILLUMINATED.

---

## Repository Structure

```
LHM/
├── Scripts/                    # Operational scripts (primary working code)
│   ├── data_pipeline/          # Core data pipeline
│   │   ├── lighthouse/         # Pipeline package (fetchers, transforms, quality)
│   │   │   ├── config.py       # API keys, FRED/BLS/BEA series catalogs, thresholds
│   │   │   ├── pipeline.py     # Master daily update (run_daily_update)
│   │   │   ├── fetchers.py     # FRED, BLS, BEA, NYFed, OFR fetchers
│   │   │   ├── market_fetchers.py  # Market data (MSI/SPI)
│   │   │   ├── crypto_free_fetchers.py  # DefiLlama + CoinGecko
│   │   │   ├── breadth_fetcher.py   # S&P 500 market breadth
│   │   │   ├── zillow_fetcher.py    # Zillow ZHVI + ZORI
│   │   │   ├── tradingview_fetcher.py  # TradingView ECONOMICS series
│   │   │   ├── transforms.py   # Statistical transforms (z-scores, YoY, etc.)
│   │   │   ├── quality.py      # Data quality flagging
│   │   │   └── query.py        # Query/export helpers
│   │   ├── run_pipeline.py     # Daily runner (entry point)
│   │   ├── compute_indices.py  # Proprietary index computation
│   │   ├── compute_crypto_indices.py  # Crypto index computation
│   │   ├── horizon_dataset_builder.py # Raw → z-scores for indices
│   │   ├── sync_all.py         # Sync DB to GitHub/iCloud/GDrive/Dropbox
│   │   ├── threshold_alerts.py # Alert rules engine
│   │   └── morning_brief.py    # HTML morning brief generator
│   ├── automation/             # CRM, tasks, email briefs
│   │   ├── lhm_tasks.py        # Task & content calendar CLI
│   │   ├── lhm_crm.py          # Contact/CRM management
│   │   ├── email_brief.py      # Email brief generation
│   │   └── briefing_helpers.py  # Shared briefing utilities
│   ├── backtest/               # Backtesting CLI tools (v1-v5, OOS, asymmetry)
│   ├── chart_generation/       # Chart scripts (horizon, edu series, premium, BTC ETF)
│   ├── utilities/              # One-off helpers (chart style, data fetcher, deep dives)
│   └── validation/             # Data validation scripts
│
├── lighthouse_quant/           # Quantitative modeling package (v0.1.0)
│   ├── __init__.py
│   ├── config.py               # Paths, publication lags, NBER recessions, indicator relationships
│   ├── crypto/                 # Crypto analytics (Token Terminal, fundamentals, systematic, ML)
│   ├── data/                   # Data loaders (horizon_dataset, lighthouse_indices)
│   ├── models/                 # Recession probability, risk ensemble, warning system
│   ├── validation/             # Lead-lag analysis, weight optimization, regime validation
│   └── utils/
│
├── Data/                       # Data directory (large files NOT committed)
│   ├── databases/              # SQLite databases (gitignored)
│   │   └── Lighthouse_Master.db    # Master database (~700+ series)
│   └── lighthouse_data/        # Secondary data library
│       ├── collect/            # FRED, crypto, market, labor collectors
│       ├── curate/             # Panel builders (macro, crypto, chartbook)
│       ├── charts/             # Chart generation modules
│       ├── dashboards/         # Consumer, labor, liquidity, treasury dashboards
│       ├── features/           # Transform functions
│       ├── indicators/         # Core indicator computation
│       ├── orchestration/      # Daily flow orchestration
│       ├── catalog/            # YAML dataset/indicator catalogs
│       └── config.py           # DataConfig dataclass (paths, API keys from env)
│
├── Strategy/                   # Strategy documents & pillar definitions
│   ├── PILLAR 1 LABOR.md       # through PILLAR 12 SENTIMENT.md
│   ├── LIGHTHOUSE MACRO TRADING STRATEGY - MASTER.md
│   ├── LIGHTHOUSE MACRO - PROPRIETARY INDICATORS REFERENCE.md
│   ├── MODELING_ARCHITECTURE_PLAN.md
│   ├── ONCHAIN_ANALYTICS_FRAMEWORK.md
│   └── TWO_BOOKS_FRAMEWORK.md
│
├── Brand/                      # Brand assets and styling specs
│   ├── brand-guide.md          # Colors, typography, logo usage
│   ├── chart-styling.md        # Canonical chart styling spec (v3.0)
│   ├── templates.md            # Document templates
│   ├── Logo.JPG, Banner.JPG    # Brand imagery
│   └── voice-and-tone-for-gemini.md
│
├── Charts/                     # Generated chart outputs (PNGs gitignored)
├── Content/                    # Written content and educational series
├── Deliverables/               # Client deliverables, decks, podcast packages
├── Analysis/                   # LCI forward analysis, version comparisons
├── Outputs/                    # Pipeline outputs (gitignored)
├── Archive/                    # Historical code and archived projects (gitignored)
├── Working/                    # Scratch/working files (gitignored)
├── External/                   # External data sources (gitignored)
├── logs/                       # Pipeline, alerts, brief, sync logs
│
├── .github/
│   └── copilot-instructions.md # GitHub Copilot instructions
├── .gitignore
└── .vscode/
    └── settings.json           # Theme: Cobalt2
```

---

## Key Concepts

### The 12-Pillar Framework

Lighthouse Macro organizes macro analysis into 12 pillars, each with dedicated data series, transforms, and composite indices:

1. **Labor** — JOLTS, BLS employment, unemployment duration, demographics
2. **Prices** — CPI/PCE components, PPI pipeline, inflation expectations
3. **Growth** — GDP, industrial production, retail sales, business surveys
4. **Housing** — Starts, permits, prices (Case-Shiller, FHFA), affordability
5. **Consumer** — Credit, savings, debt service, consumption
6. **Business** — Durable goods, inventories, freight, auto sales
7. **Trade** — Trade balance, import/export prices, dollar indices, current account
8. **Government** — Fiscal balance, federal spending, debt metrics
9. **Financial** — Yield curve, credit spreads, financial conditions indices
10. **Plumbing** — Fed balance sheet, RRP, reserves, money markets
11. **Market Structure** — Breadth, volatility, market internals
12. **Sentiment** — Consumer sentiment, surveys

### Proprietary Indices

Computed in `Scripts/data_pipeline/compute_indices.py`:

| Index | Full Name | Description |
|-------|-----------|-------------|
| **MRI** | Macro Risk Index | Master composite — cycle-phase classification |
| **LFI** | Labor Fragility Index | Labor market stress composite |
| **LCI** | Liquidity Cushion Index | Liquidity conditions composite |
| **CLG** | Credit-Labor Gap | Credit vs. labor divergence |
| **LPI** | Labor Pillar Index | Pillar 1 composite |
| **PCI** | Prices Composite Index | Pillar 2 composite |
| **GCI** | Growth Composite Index | Pillar 3 composite |
| **HCI** | Housing Composite Index | Pillar 4 composite |
| **CCI** | Consumer Composite Index | Pillar 5 composite |
| **BCI** | Business Composite Index | Pillar 6 composite |
| **TCI** | Trade Composite Index | Pillar 7 composite |
| **FCI** | Financial Conditions Index | Pillar 9 composite |
| **REC_PROB** | Recession Probability | 3/6/12-month forward probability |

### Database Schema

The master SQLite database (`Lighthouse_Master.db`) has three core tables:

- **`observations`** — `(series_id TEXT, date TEXT, value REAL)` primary key on (series_id, date)
- **`series_meta`** — Series metadata (source, category, frequency, quality flags)
- **`update_log`** — Pipeline run history

Plus computed tables:
- **`horizon_dataset`** — Z-scored indicators for index computation
- **`lighthouse_indices`** — Proprietary index values by date
- **`crypto_scores`** — Crypto analytics scores

---

## Data Pipeline

### Daily Pipeline Flow

The pipeline runs daily (originally 06:00 ET via launchd). Entry point: `Scripts/data_pipeline/run_pipeline.py`

```
1. Fetch raw data from sources (FRED, BLS, BEA, NYFed, OFR, Market, Crypto, Breadth, Zillow, TradingView)
2. Write to observations table with upsert
3. Run quality checks (staleness, outliers, missing data)
4. Rebuild horizon_dataset (raw → z-scores)
5. Compute proprietary indices (MRI, LFI, LCI, CLG, pillar composites)
6. Compute crypto indices
7. Backup database (keep 7 days)
8. Sync to external destinations
9. Run threshold alerts
10. Generate morning brief (HTML)
```

### Running the Pipeline

```bash
# Full update
python Scripts/data_pipeline/run_pipeline.py

# Stats only
python Scripts/data_pipeline/run_pipeline.py --stats

# Quick (skip quality checks)
python Scripts/data_pipeline/run_pipeline.py --quick

# FRED only
python Scripts/data_pipeline/run_pipeline.py --fred-only

# Specific sources
python Scripts/data_pipeline/run_pipeline.py --sources FRED BLS MARKET

# Skip index computation
python Scripts/data_pipeline/run_pipeline.py --skip-indices
```

### Data Sources

| Source | API Key Required | Series Count | Key Data |
|--------|-----------------|-------------|----------|
| FRED | Yes (`FRED_API_KEY`) | ~400+ | Macro series, yields, spreads |
| BLS | Yes (`BLS_API_KEY`) | ~30 | Employment, wages, prices |
| BEA | Yes (`BEA_API_KEY`) | ~9 tables | GDP, PCE, corporate profits |
| NY Fed | No | ~5 rates | SOFR, EFFR, OBFR |
| OFR | No | ~15 | FSI, money market funds, repo |
| Market | Via FRED | ~20 | Market stress/positioning indices |
| Crypto | No (free APIs) | Variable | DeFi TVL, prices, on-chain |
| Breadth | Via yfinance | ~10 | S&P 500 breadth metrics |
| Zillow | No (public CSVs) | ~5 | ZHVI, ZORI housing data |
| TradingView | No | ~5 | NAHB, MBA, pending home sales |

---

## Environment & Configuration

### Required Environment Variables

```bash
FRED_API_KEY=...           # Required — Federal Reserve Economic Data
BLS_API_KEY=...            # Required — Bureau of Labor Statistics
BEA_API_KEY=...            # Required — Bureau of Economic Analysis
LIGHTHOUSE_DB_PATH=...     # Optional — override default DB path

# For crypto analytics (optional)
SANTIMENT_API_KEY=...
DUNE_API_KEY=...
COINGLASS_API_KEY=...
```

API keys can be set in a `.env` file at `Scripts/data_pipeline/.env` (python-dotenv is used if available).

### Python Environment

- **Python 3.8+** (3.10+ preferred for union type syntax in Data/lighthouse_data/config.py)
- Key dependencies: `pandas`, `numpy`, `matplotlib`, `sqlite3` (stdlib), `requests`
- Optional: `statsmodels`, `pyarrow`, `python-dotenv`, `yfinance`, `scipy`
- No `requirements.txt` currently committed — install dependencies as needed

### Hardcoded Paths

Several scripts reference `/Users/bob/LHM/` as the root path. When working in a different environment, these paths need to be adjusted:

- `lighthouse_quant/config.py` → `LHM_ROOT = Path("/Users/bob/LHM")`
- `Scripts/data_pipeline/lighthouse/config.py` → `DB_PATH` default
- `Scripts/data_pipeline/compute_indices.py` → `DB_PATH`
- `Scripts/data_pipeline/run_pipeline.py` → `LHM_BACKUP_DIR`

Use `LIGHTHOUSE_DB_PATH` env var where supported to override.

---

## Charting Standards

All charts must follow the brand specification in `Brand/chart-styling.md` (v3.0):

### Required Elements
- **Background:** Dark navy `#0A1628`
- **Spines:** All 4 visible, 0.5pt linewidth, no gridlines
- **Right axis primary** (ticks on RHS by default)
- **Top accent bar:** Ocean `#0089D1` (2/3) + Dusk `#FF6723` (1/3)
- **Bottom accent bar:** Mirror of top
- **Top-left watermark:** "LIGHTHOUSE MACRO" in Ocean blue
- **Bottom-right watermark:** "MACRO, ILLUMINATED." in Ocean blue
- **Source line:** Bottom-left, format `Lighthouse Macro | {Source}; mm.dd.yyyy`

### Color Palette

| Name | Hex | Usage |
|------|-----|-------|
| Ocean | `#0089D1` | Primary brand, headers, accents |
| Dusk | `#FF6723` | Warnings, accent bar |
| Sky | `#33CCFF` | Volatility, momentum |
| Venus | `#FF2389` | Critical alerts |
| Sea | `#00BB99` | Secondary series |
| Doldrums | `#D3D6D9` | Backgrounds, grids |
| Starboard | `#00FF00` | Extreme bullish |
| Port | `#FF0000` | Crisis zones |

### Typography
- **Titles:** Montserrat Bold
- **Body:** Inter Regular
- **Data/Tables:** Inter or Source Code Pro

### Helper Functions (from chart-styling.md)
- `new_fig(figsize)` — Create themed figure
- `style_ax(ax)` — Core spine/grid styling
- `style_dual_ax(ax1, ax2, c1, c2)` — Dual-axis coloring
- `brand_fig(fig, title, subtitle, source)` — Apply all branding
- `add_last_value_label(ax, y_data, color)` — Colored pill labels
- `add_recessions(ax, start_date)` — NBER recession shading

---

## Conventions & Rules

### Code Conventions
- Python by default (pandas, numpy, matplotlib; statsmodels/scipy optional)
- Type hints and docstrings required for reusable modules in packages
- PEP 8 style
- Use relative paths for data I/O in notebooks
- Set random seeds for reproducibility

### Data Rules
- **Never fabricate or approximate data.** If inputs are missing, stop and request the exact source.
- **Never commit raw data or secrets** to `Data/` or `configs/`
- Credentials via environment variables and `.env` only
- Publication lags are defined in `lighthouse_quant/config.py` — critical for avoiding look-ahead bias in backtesting
- Z-score windows: 24 months (monthly), 252 days (daily)

### Hard Constraints
- Do not add or commit raw data or secrets to `Data/` or `configs/`
- Keep function signatures stable; prefer adding helpers rather than changing public APIs
- Charts must follow the charting standards — no gridlines, all four spines, correct color palette
- Watermark "MACRO, ILLUMINATED." bottom-right on all charts (never overlap data)

---

## Key Files Reference

| Purpose | File |
|---------|------|
| Pipeline entry point | `Scripts/data_pipeline/run_pipeline.py` |
| Pipeline core | `Scripts/data_pipeline/lighthouse/pipeline.py` |
| Series catalog (FRED/BLS/BEA) | `Scripts/data_pipeline/lighthouse/config.py` |
| Index computation | `Scripts/data_pipeline/compute_indices.py` |
| Quant package init | `lighthouse_quant/__init__.py` |
| Quant config (lags, recessions) | `lighthouse_quant/config.py` |
| Data loaders | `lighthouse_quant/data/loaders.py` |
| Recession model | `lighthouse_quant/models/recession_probability.py` |
| Risk ensemble | `lighthouse_quant/models/risk_ensemble.py` |
| Warning system | `lighthouse_quant/models/warning_system.py` |
| Chart styling spec | `Brand/chart-styling.md` |
| Brand guide | `Brand/brand-guide.md` |
| Trading strategy | `Strategy/LIGHTHOUSE MACRO TRADING STRATEGY - MASTER.md` |
| Pillar docs | `Strategy/PILLAR 1 LABOR.md` through `PILLAR 12 SENTIMENT.md` |
| Indicator reference | `Strategy/LIGHTHOUSE MACRO - PROPRIETARY INDICATORS REFERENCE.md` |

---

## Git & Workflow

- **Default branch:** `main`
- **Automated commits:** "Daily pipeline sync" commits happen every 15 minutes during pipeline runs
- **Gitignored:** `Data/databases/`, `Data/raw/`, `Data/curated/`, `*.parquet`, `Archive/`, `Working/`, `External/`, `Outputs/`, `Charts/*.png`, `.env`, credentials, `.claude/`
- **No CI/CD workflows** currently configured (`.github/workflows/` does not exist)
- Large files and generated outputs are excluded from git

### Logs

Pipeline logs are stored in `logs/`:
- `pipeline.log` / `pipeline_error.log`
- `alerts.log`
- `morning_brief.log` / `morning_brief_error.log`
- `email_brief.log` / `email_brief_error.log`
- `sync.log` / `sync_error.log`

---

## Common Tasks

### Adding a New FRED Series
1. Add the series ID and label to `FRED_CURATED` dict in `Scripts/data_pipeline/lighthouse/config.py`
2. Run the pipeline with `--sources FRED`
3. If needed for index computation, update `horizon_dataset_builder.py` and `compute_indices.py`

### Adding a New Indicator/Index
1. Define the formula in `Scripts/data_pipeline/compute_indices.py`
2. Add status thresholds in the `STATUS_THRESHOLDS` dict
3. Add publication lag to `lighthouse_quant/config.py` `PUBLICATION_LAGS`
4. Add to threshold alerts if monitoring is needed

### Creating a New Chart
1. Follow `Brand/chart-styling.md` v3.0 specification
2. Use the helper functions (`new_fig`, `style_ax`, `brand_fig`, etc.)
3. Export to `Charts/` directory
4. Include source attribution in bottom-left

### Running Backtests
```bash
python Scripts/backtest/cli_backtest_v5.py    # Latest backtesting CLI
python Scripts/backtest/cli_oos_90_10.py      # Out-of-sample 90/10 split
python Scripts/backtest/cli_asymmetry.py      # Asymmetry analysis
```

---

## Asking Questions Before Editing

If anything is ambiguous, clarify:
1. Which environment (Python version) should be targeted? (default: 3.8+)
2. Are external API keys available for the data source?
3. Should the change touch index computation or just raw data?
4. Is this for a published deliverable (strict brand compliance) or internal use?
