# LHM Test Suite

First automated tests for the monorepo. This is an initial, high-ROI slice
covering the **pure numeric logic** that the whole pipeline depends on.

## Running

```bash
pip install -r requirements-dev.txt   # pandas, numpy, pytest
pytest                                # from the repo root
```

`tests/conftest.py` puts the repo root and `Scripts/data_pipeline/` on
`sys.path`, so no install/packaging step is required.

## What's covered

| File | Module under test | Focus |
|------|-------------------|-------|
| `test_transforms.py` | `lighthouse/transforms.py` | YoY/MoM/annualized transforms, rolling z-score, series-type & frequency inference, `apply_transforms` composition |
| `test_quality.py` | `lighthouse/quality.py` | Missing-value / variance / outlier / staleness / duplicate gates and `validate_series` composition |
| `test_index_status.py` | `compute_indices.py` | `get_status` threshold bands (MRI/LFI + monotonicity invariant) and the strict NaN-propagating composite math (`weighted_sum_strict`, `all_present_mean`, `compute_zscore`) |

## Not yet covered (suggested next slices)

- `lighthouse_quant/config.py` invariants (publication lags, NBER recession
  ordering, indicator relationships)
- Fetcher response parsing (FRED/BLS/BEA/OFR) via saved JSON/CSV fixtures
- Pipeline DB writes / `query.py` reads against in-memory SQLite
- `lighthouse_quant/models/` (recession probability, warning-system override rules)
