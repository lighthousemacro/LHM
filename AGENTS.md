# AGENTS.md

## Cursor Cloud specific instructions

### Environment overview

LHM is a Python 3.12 monorepo with no `requirements.txt` or `pyproject.toml`. Dependencies are installed ad-hoc via `pip install`. The core product is a **data pipeline** that fetches macroeconomic data from 10+ APIs, stores it in a SQLite database, and computes proprietary composite indices.

### Critical path setup

- **Hardcoded paths**: Multiple files reference `/Users/bob/LHM/` as root. A symlink `sudo mkdir -p /Users/bob && sudo ln -sf /workspace /Users/bob/LHM` resolves this without code changes. The update script handles this automatically.
- **Database path**: Set `export LIGHTHOUSE_DB_PATH=/workspace/Data/databases/Lighthouse_Master.db` (already in `~/.bashrc`). The pipeline's `config.py` reads this env var.
- **PYTHONPATH**: Must include `/workspace` so `lighthouse_quant` is importable: `export PYTHONPATH=/workspace`.
- **Database directory**: `mkdir -p /workspace/Data/databases/backups` is needed before first run.

### Running the pipeline

See `CLAUDE.md` for full pipeline CLI flags. Quick reference:

```bash
cd /workspace
PYTHONPATH=/workspace python3 Scripts/data_pipeline/run_pipeline.py --quick --fred-only --skip-indices
```

The pipeline's working directory changes to `Scripts/data_pipeline/` at runtime (via `os.chdir` in `run_pipeline.py`), so relative imports within that subtree work regardless of where you invoke from.

### Index computation bootstrap

After a fresh DB, run index computation twice:
1. First run creates the `lighthouse_indices` table.
2. Second run (with `latest_only=False`) lets `REC_PROB`, `WARNING_LEVEL`, and `ENSEMBLE_RISK` read back their own table for self-referential calculations.

### Chart generation

Charts use `matplotlib` with `Agg` backend (no display server). Follow `Brand/chart-styling.md` v3.0 for styling. Key: dark navy `#0A1628` background, all four spines visible, no gridlines, `MACRO, ILLUMINATED.` watermark.

### No automated test suite

There is no `tests/` directory or pytest suite. Validation is done by running the pipeline and checking database stats (`--stats` flag) or by importing `lighthouse_quant` modules.

### API keys

Hardcoded fallback API keys exist in `Scripts/data_pipeline/lighthouse/config.py` for FRED, BLS, and BEA. These work without setting env vars or `.env`. For production use, set keys in `Scripts/data_pipeline/.env` (see `.env.example`).
