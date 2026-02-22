# LHM — Lighthouse Macro Research Infrastructure

**MACRO, ILLUMINATED.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

## Overview

LHM (Lighthouse Macro) is the internal source-of-truth monorepo powering institutional-grade macroeconomic research, systematic analysis, and market intelligence for Lighthouse Macro. This repository contains:

- **Python-based analytical frameworks** for macro regime classification, liquidity transmission, and risk assessment
- **Quantitative modeling infrastructure** (`lighthouse_quant`) for backtesting and systematic trading
- **Data pipeline automation** integrating FRED, Treasury, BLS, JOLTS, and proprietary sources
- **Chart generation systems** adhering to institutional publication standards
- **Research notebooks** for reproducible macro analysis
- **Content production workflows** for The Beacon, The Beam, The Chartbook, and Horizon reports

This repository is designed for hedge funds, CIOs, central banks, and sophisticated allocators seeking institutional-grade macro intelligence.

---

## Repository Structure

```
LHM/
├── lighthouse_quant/        # Quantitative modeling & backtesting framework
│   ├── crypto/             # Crypto fundamentals & systematic models
│   ├── data/               # Data loaders and transformations
│   ├── models/             # Risk models, warning systems, ensemble methods
│   ├── utils/              # Utilities and helpers
│   └── validation/         # Model validation and testing
│
├── Scripts/                # Production scripts & automation
│   ├── data_pipeline/      # ETL and data refresh workflows
│   ├── chart_generation/   # Chart automation systems
│   ├── backtest/           # Backtesting utilities
│   └── utilities/          # General-purpose tools
│
├── Data/                   # Data storage (gitignored, regenerated daily)
│   ├── lighthouse_data/    # Core datasets and frameworks
│   ├── databases/          # SQLite databases (Lighthouse_Master.db)
│   └── logs/               # Data pipeline logs
│
├── Charts/                 # Generated visualizations (gitignored)
├── Analysis/               # Ad-hoc analysis and research
├── Content/                # Publication drafts and educational content
├── Deliverables/           # Client-ready packages and reports
├── Brand/                  # Visual assets and brand guidelines
└── Strategy/               # Strategic frameworks and planning
```

---

## Core Frameworks

### Three Pillars Architecture

1. **Macro Dynamics**: Structural forces driving growth, inflation, employment, housing, fiscal flows
2. **Monetary Mechanics**: Central bank plumbing, liquidity transmission, repo markets, collateral flows
3. **Market Technicals**: Positioning, microstructure, correlation shifts, cross-border flows

### Analytical Systems

- **Macro Regime Classification**: Growth × Inflation quadrants (Goldilocks, Overheating, Recession, Stagflation)
- **Labor Dynamics Flow Model**: JOLTS → hiring → employment → wages → consumption
- **Liquidity Transmission Framework (LTF)**: RRP → SOFR-EFFR → repo → dealer balance sheets
- **Systemic Risk Early Warning System**: Credit spreads, yield curve, financial conditions
- **Crypto-Liquidity Vector Integration**: On-chain metrics tied to traditional liquidity proxies

For detailed framework documentation, see [`Data/lighthouse_data/LHM_markdowns/`](Data/lighthouse_data/LHM_markdowns/).

---

## Installation & Setup

### Prerequisites

- Python 3.8+
- SQLite 3
- Git

### Quick Start

```bash
# Clone the repository
git clone https://github.com/lighthousemacro/LHM.git
cd LHM

# Install Python dependencies (if requirements.txt exists)
pip install -r requirements.txt

# Set up environment variables for API keys
cp .env.example .env  # Create .env file (never commit this)
# Add FRED_API_KEY, BLS_API_KEY, etc. to .env

# Verify installation
python -c "import lighthouse_quant; print(lighthouse_quant.__version__)"
```

### Configuration

**Critical**: All API keys and credentials must be stored in `.env` and never committed.

Edit `lighthouse_quant/config.py` to set paths:

```python
LHM_ROOT = Path("/path/to/your/LHM")
DATA_DIR = LHM_ROOT / "Data"
DB_PATH = DATA_DIR / "databases" / "Lighthouse_Master.db"
```

---

## Usage

### Data Pipeline

Refresh all macro data sources:

```bash
python Scripts/refresh_all_horizon_data.py
```

### Chart Generation

Generate institutional-grade charts adhering to LHM standards:

```bash
# Generate all charts
python Scripts/generate_all_charts.py

# Generate labor framework charts
python Scripts/generate_labor_educational_charts.py

# Generate crypto framework charts
python Scripts/generate_crypto_framework_pdf.py
```

### Backtesting & Quantitative Analysis

```python
from lighthouse_quant.models import RiskEnsemble
from lighthouse_quant.data.loaders import load_macro_data

# Load data
df = load_macro_data("Lighthouse_Master.db")

# Run risk ensemble
risk = RiskEnsemble(df)
signals = risk.generate_signals()
```

### Dashboard & Monitoring

```bash
# Launch macro dashboard
python Scripts/macro_dashboard_complete.py

# Launch NY Fed liquidity dashboard
python Scripts/ny_fed_dashboard_live.py
```

---

## Charting Standards

All charts adhere to institutional publication standards defined in `Data/lighthouse_data/LHM_markdowns/LHM_Operations.md`:

### Visual Guidelines

- **No gridlines** (clean, minimal aesthetic)
- **All four spines visible** (complete framing)
- **Right axis is primary** (standard convention)
- **Color palette**:
  - Ocean Blue: `#0077BE`
  - Deep Sunset Orange: `#FF6F20`
  - Neon Carolina Blue: `#4B9CD3`
  - Neon Magenta: `#D946EF`
  - Medium-Light Gray: `#9CA3AF`
- **Line thickness**: ~3pt
- **Longest history available** (maximize context)
- **Axes matched at zero** when comparing series
- **Watermark**: "MACRO, ILLUMINATED." (bottom-right, never overlapping data)

Example implementation:

```python
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(12, 7))
ax.plot(dates, values, color='#0077BE', linewidth=3, label='Series')
ax.spines['top'].set_visible(True)
ax.spines['right'].set_visible(True)
ax.grid(False)
ax.text(0.98, 0.02, "MACRO, ILLUMINATED.", 
        transform=ax.transAxes, ha='right', va='bottom',
        fontsize=8, color='gray', alpha=0.6)
plt.tight_layout()
```

---

## Data Sources

LHM integrates data from:

### Primary Sources
- **FRED (Federal Reserve Economic Data)**: ~200+ series
- **BLS (Bureau of Labor Statistics)**: Employment, CPI, wages
- **Treasury Direct**: Treasury yields, auction results
- **SIFMA**: Repo market statistics
- **NY Fed**: SOFR, RRP, EFFR, balance sheet

### Proprietary Sources
- **Senior Loan Officer Opinion Survey (SLOOS)**: Credit tightening
- **Token Terminal**: On-chain crypto fundamentals
- **MacroMicro**: Global macro aggregates

### Data Refresh

- **Daily**: Market data (yields, spreads, VIX, crypto)
- **Weekly**: JOLTS, initial claims, Fed balance sheet
- **Monthly**: CPI, PCE, GDP, ISM, housing

Data is stored in SQLite (`Data/databases/Lighthouse_Master.db`) with publication lag tracking to prevent look-ahead bias in backtests.

---

## Publication Cadence

- **The Beacon** (Daily): Market commentary and quick takes
- **The Beam** (Weekly): Focused thematic analysis
- **The Chartbook** (Weekly Friday): 50-75 institutional-grade charts
- **The Horizon** (Quarterly): Comprehensive macro outlook

All content drafts are stored in `Content/` and final deliverables in `Deliverables/`.

---

## Testing

Run the test suite (if available):

```bash
pytest tests/ -v
```

Tests include:
- Data loader validation
- Model performance benchmarks
- Chart generation verification
- Publication lag enforcement

---

## Contributing

This repository is internal to Lighthouse Macro. External contributions are not accepted at this time.

### Internal Development Workflow

1. Work in feature branches
2. Run all tests before committing
3. Ensure data is excluded via `.gitignore`
4. Update documentation when adding frameworks
5. Follow PEP 8 style guidelines
6. Add type hints and docstrings to all functions

---

## Key Documentation

- **[LHM Master Index](Data/lighthouse_data/LHM_markdowns/LHM_Master_Index.md)**: Complete documentation index
- **[Core Frameworks](Data/lighthouse_data/LHM_markdowns/LHM_Core_Frameworks.md)**: Analytical methodologies
- **[Business Strategy](Data/lighthouse_data/LHM_markdowns/LHM_Business_Strategy.md)**: Revenue and positioning
- **[Content Strategy](Data/lighthouse_data/LHM_markdowns/LHM_Content_Strategy.md)**: Publication workflows
- **[Operations](Data/lighthouse_data/LHM_markdowns/LHM_Operations.md)**: Technical infrastructure
- **[Partnerships](Data/lighthouse_data/LHM_markdowns/LHM_Partnerships.md)**: Strategic alliances

---

## Security & Compliance

**Never commit**:
- API keys or credentials
- Raw client data
- Proprietary datasets
- `.env` files

All sensitive data is referenced via environment variables and excluded in `.gitignore`.

---

## Performance Metrics

### Research Output
- **Weekly**: 50-75 institutional-grade charts
- **Monthly**: 4 long-form research pieces
- **Quarterly**: Comprehensive macro outlook
- **Annual**: 200+ analytical artifacts

### System Capabilities
- **Data sources**: 300+ economic series
- **Publication lag tracking**: 60+ series
- **Backtesting**: 1948-present (NBER recessions validated)
- **Model suite**: VAR, VECM, State-Space, Bayesian, ML ensembles

---

## License

Copyright © 2024-2026 Lighthouse Macro. All rights reserved.

This repository is proprietary and confidential. Unauthorized use, distribution, or reproduction is prohibited.

---

## Contact

**Lighthouse Macro**  
Institutional Macro Research & Intelligence

- Website: [lighthousemacro.com](https://lighthousemacro.com)
- Email: contact@lighthousemacro.com
- Substack: [lighthousemacro.substack.com](https://lighthousemacro.substack.com)

---

## Acknowledgments

Built with:
- Python (pandas, numpy, matplotlib, statsmodels)
- SQLite
- Jupyter
- FRED API, BLS API, Treasury API

**MACRO, ILLUMINATED.**
