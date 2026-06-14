"""Unit tests for the pure index logic in Scripts/data_pipeline/compute_indices.py.

This is the firm's IP: the status-label thresholds that drive client-facing
regime classifications (RECESSION / LATE CYCLE / CRITICAL ...), and the
canonical composite math (strict NaN-propagating weighted sums + z-scores).
Boundary tests here protect the published formulas from accidental edits.
"""

import numpy as np
import pandas as pd
import pytest

import compute_indices as CI


# --------------------------------------------------------------------------
# get_status — threshold classification
# --------------------------------------------------------------------------

def test_get_status_nan_is_no_data():
    assert CI.get_status("MRI", np.nan) == "NO DATA"


def test_get_status_unknown_index_returns_unknown():
    assert CI.get_status("NOT_AN_INDEX", 0.5) == "UNKNOWN"


@pytest.mark.parametrize(
    "value, expected",
    [
        (0.60, "RECESSION"),
        (0.50, "RECESSION"),      # boundary is inclusive (>=)
        (0.30, "PRE-RECESSION"),
        (0.15, "LATE CYCLE"),
        (0.00, "MID-CYCLE"),
        (-0.50, "EARLY EXPANSION"),
    ],
)
def test_get_status_mri_bands(value, expected):
    assert CI.get_status("MRI", value) == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        (1.6, "CRITICAL"),
        (1.5, "CRITICAL"),        # boundary inclusive
        (1.0, "HIGH"),
        (0.5, "ELEVATED"),
        (0.0, "NEUTRAL"),
        (-2.0, "HEALTHY"),
    ],
)
def test_get_status_lfi_bands(value, expected):
    assert CI.get_status("LFI", value) == expected


def test_status_thresholds_are_monotonic_with_catchall():
    """Every threshold table must be sorted descending and end in a -999 catch-all.

    This invariant is what makes get_status's first-match-wins loop correct;
    if an edit breaks ordering, some bands become unreachable.
    """
    for index_name, bands in CI.STATUS_THRESHOLDS.items():
        cutoffs = [c for c, _ in bands]
        assert cutoffs == sorted(cutoffs, reverse=True), (
            f"{index_name} thresholds not descending: {cutoffs}"
        )
        assert cutoffs[-1] == -999, f"{index_name} missing -999 catch-all"


# --------------------------------------------------------------------------
# weighted_sum_strict — canonical composite formula
# --------------------------------------------------------------------------

def test_weighted_sum_strict_basic():
    idx = pd.date_range("2020-01-01", periods=3, freq="MS")
    a = pd.Series([1.0, 2.0, 3.0], index=idx)
    b = pd.Series([10.0, 20.0, 30.0], index=idx)
    out = CI.weighted_sum_strict([(a, 0.5), (b, 0.5)])
    expected = 0.5 * a + 0.5 * b
    pd.testing.assert_series_equal(out, expected, check_names=False)


def test_weighted_sum_strict_nan_propagates():
    idx = pd.date_range("2020-01-01", periods=3, freq="MS")
    a = pd.Series([1.0, np.nan, 3.0], index=idx)
    b = pd.Series([10.0, 20.0, 30.0], index=idx)
    out = CI.weighted_sum_strict([(a, 0.5), (b, 0.5)])
    # Missing input at position 1 nulls the composite there — no silent reweight.
    assert np.isnan(out.iloc[1])
    assert out.iloc[0] == pytest.approx(5.5)
    assert out.iloc[2] == pytest.approx(16.5)


def test_weighted_sum_strict_empty_is_empty_series():
    out = CI.weighted_sum_strict([])
    assert isinstance(out, pd.Series) and out.empty


# --------------------------------------------------------------------------
# all_present_mean — equal-weight composite
# --------------------------------------------------------------------------

def test_all_present_mean_basic_and_nan_propagation():
    idx = pd.date_range("2020-01-01", periods=3, freq="MS")
    a = pd.Series([1.0, 2.0, np.nan], index=idx)
    b = pd.Series([3.0, 4.0, 5.0], index=idx)
    out = CI.all_present_mean(a, b)
    assert out.iloc[0] == pytest.approx(2.0)
    assert out.iloc[1] == pytest.approx(3.0)
    assert np.isnan(out.iloc[2])  # strict: any NaN -> NaN


def test_all_present_mean_empty_is_empty_series():
    out = CI.all_present_mean()
    assert isinstance(out, pd.Series) and out.empty


# --------------------------------------------------------------------------
# compute_zscore — division-by-zero protection
# --------------------------------------------------------------------------

def test_compute_zscore_constant_window_is_nan_not_inf():
    s = pd.Series([3.0] * 30)
    out = CI.compute_zscore(s, window=24)
    # std is 0 across the window -> replaced with NaN -> no inf leaks through.
    assert not np.isinf(out.to_numpy()).any()
    assert out.dropna().empty


def test_compute_zscore_known_value():
    s = pd.Series([0.0, 0.0, 0.0, 0.0, 4.0])
    out = CI.compute_zscore(s, window=5, min_periods=5)
    win = s.to_numpy()
    expected = (4.0 - win.mean()) / win.std(ddof=1)
    assert out.iloc[4] == pytest.approx(expected)
