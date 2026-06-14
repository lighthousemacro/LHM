"""Shared pytest fixtures and import-path setup for the LHM test suite.

The repo is not an installable package, and several modules live as loose
scripts under ``Scripts/data_pipeline``. To import them in tests we put both
the repo root and ``Scripts/data_pipeline`` on ``sys.path`` here, once, before
any test module imports the code under test.

Path layout this enables:
    import lighthouse.transforms          # Scripts/data_pipeline/lighthouse/
    import compute_indices                # Scripts/data_pipeline/
    import lighthouse_quant.config        # repo root
"""

import sys
import types
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
PIPELINE_DIR = REPO_ROOT / "Scripts" / "data_pipeline"

for p in (REPO_ROOT, PIPELINE_DIR):
    sp = str(p)
    if sp not in sys.path:
        sys.path.insert(0, sp)

# Register a lightweight stub for the ``lighthouse`` package *before* anything
# imports its submodules.
#
# The real ``Scripts/data_pipeline/lighthouse/__init__.py`` eagerly imports the
# pipeline -> fetchers chain, which pulls in heavy runtime-only deps (e.g.
# ``requests``). The modules under test (transforms, quality, config) and the
# compute_indices import chain don't need any of that. We give the package a
# ``__path__`` pointing at the real directory but an empty ``__init__`` body, so
# ``import lighthouse.transforms`` / ``from lighthouse.config import ...`` (and
# quality's relative ``from .config import ...``) resolve the individual source
# files directly without executing the eager package init.
#
# If the suite grows to cover the fetcher/pipeline stack itself, add the runtime
# deps to requirements-dev.txt and import those modules explicitly instead.
_LIGHTHOUSE_DIR = PIPELINE_DIR / "lighthouse"
if "lighthouse" not in sys.modules and _LIGHTHOUSE_DIR.is_dir():
    _pkg = types.ModuleType("lighthouse")
    _pkg.__path__ = [str(_LIGHTHOUSE_DIR)]
    _pkg.__package__ = "lighthouse"
    sys.modules["lighthouse"] = _pkg


@pytest.fixture
def monthly_index():
    """A clean 36-month month-start DatetimeIndex ending recently."""
    end = pd.Timestamp.today().normalize().replace(day=1)
    return pd.date_range(end=end, periods=36, freq="MS")


@pytest.fixture
def rising_series(monthly_index):
    """A strictly increasing monthly series (100, 101, ... )."""
    return pd.Series(
        np.arange(100.0, 100.0 + len(monthly_index)),
        index=monthly_index,
        name="value",
    )


@pytest.fixture
def clean_value_df(rising_series):
    """A DataFrame with a 'value' column on a recent monthly DatetimeIndex.

    Passes every quality check: enough obs, no missing, non-zero variance,
    no extreme outliers, no duplicate dates, and a fresh last observation.
    """
    return rising_series.to_frame(name="value")
