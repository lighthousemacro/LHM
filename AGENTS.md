# AGENTS.md

See `CLAUDE.md` for full project context, repository structure, and conventions.

## Cursor Cloud specific instructions

### Environment

- **Python 3.12** (system Python at `/usr/bin/python3`).
- The hardcoded path `/Users/bob/LHM` in several scripts is resolved by a symlink: `/Users/bob/LHM -> /workspace`. The update script recreates this on every boot.
- `LIGHTHOUSE_DB_PATH` must be set to `/workspace/Data/databases/Lighthouse_Master.db` (persisted in `~/.bashrc`).
- `PYTHONPATH` must include `/workspace` so `lighthouse_quant` is importable from any working directory (persisted in `~/.bashrc`).

### Running the pipeline

- Entry point: `python Scripts/data_pipeline/run_pipeline.py` (see `CLAUDE.md` for flags).
- The pipeline creates the SQLite DB on first run if it doesn't exist.
- FRED API rate limits (429s) are common with the built-in fallback API key. To avoid, set a personal `FRED_API_KEY` in `Scripts/data_pipeline/.env` or as an environment secret.
- The `--skip-indices` and `--skip-pillars` flags are useful for quick data-only runs.

### Key gotchas

- `compute_indices.py` hardcodes `sys.path.insert(0, "/Users/bob/LHM")` — the symlink resolves this. Do not rely on `PYTHONPATH` alone for that file.
- `lighthouse_quant/config.py` runs `OUTPUT_DIR.mkdir(parents=True, exist_ok=True)` at import time — the symlink must exist before importing this module.
- The `Data/databases/` directory is gitignored. It must be created before the pipeline runs.
- There is no `requirements.txt` in the repo. Dependencies are: `pandas`, `numpy`, `matplotlib`, `scipy`, `statsmodels`, `yfinance`, `python-dotenv`, `scikit-learn`, `pyarrow`, `requests`.
- No test suite (`tests/` directory) exists. Validation is done by running the pipeline and checking `--stats` output.
- Sync destinations (iCloud, Dropbox, GDrive) are specific to the original developer's machine and will be skipped in cloud environments.
