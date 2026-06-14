"""Unit tests for Scripts/data_pipeline/lighthouse/quality.py.

These are the guardrails that are supposed to stop bad/stale data reaching
clients. A regression that silently turns a check into a no-op is exactly the
failure mode worth pinning down. All check functions are pure: they take a
DataFrame/args and return an issue string or None.
"""

from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import pytest

from lighthouse import quality as Q
from lighthouse.config import QUALITY_CONFIG


# --------------------------------------------------------------------------
# check_missing_values
# --------------------------------------------------------------------------

def test_missing_values_empty_dataframe():
    msg = Q.check_missing_values(pd.DataFrame({"value": []}), "SID")
    assert msg is not None and "Empty" in msg


def test_missing_values_above_threshold_flags():
    # 3 of 4 missing = 75% > default 50% threshold.
    df = pd.DataFrame({"value": [1.0, np.nan, np.nan, np.nan]})
    msg = Q.check_missing_values(df, "SID")
    assert msg is not None and "missing" in msg


def test_missing_values_below_threshold_passes():
    df = pd.DataFrame({"value": [1.0, 2.0, 3.0, np.nan]})  # 25% missing
    assert Q.check_missing_values(df, "SID") is None


# --------------------------------------------------------------------------
# check_zero_variance
# --------------------------------------------------------------------------

def test_zero_variance_constant_series_flags():
    df = pd.DataFrame({"value": [7.0, 7.0, 7.0]})
    assert Q.check_zero_variance(df, "SID") is not None


def test_zero_variance_varying_series_passes():
    df = pd.DataFrame({"value": [1.0, 2.0, 3.0]})
    assert Q.check_zero_variance(df, "SID") is None


# --------------------------------------------------------------------------
# check_outliers
# --------------------------------------------------------------------------

def test_outliers_too_few_points_returns_none():
    df = pd.DataFrame({"value": [1.0, 100.0]})
    assert Q.check_outliers(df, "SID", z_threshold=2) is None


def test_outliers_flagged_when_above_explicit_threshold():
    df = pd.DataFrame({"value": [1.0, 1.0, 1.0, 1.0, 50.0]})
    msg = Q.check_outliers(df, "SID", z_threshold=1.5)
    assert msg is not None and "outlier" in msg.lower()


def test_outliers_constant_series_returns_none():
    # Zero std must not raise / must not flag.
    df = pd.DataFrame({"value": [5.0, 5.0, 5.0, 5.0]})
    assert Q.check_outliers(df, "SID", z_threshold=2) is None


def test_outliers_default_threshold_is_lenient():
    # Default threshold (10) should not flag a mild 3-sigma spike.
    base = [1.0, 2.0, 3.0, 2.0, 1.0, 2.0, 3.0, 2.0]
    df = pd.DataFrame({"value": base + [6.0]})
    assert Q.check_outliers(df, "SID") is None


# --------------------------------------------------------------------------
# check_staleness
# --------------------------------------------------------------------------

def test_staleness_no_date():
    assert "No data" in Q.check_staleness("", "M", "SID")


def test_staleness_invalid_date():
    assert "Invalid date" in Q.check_staleness("not-a-date", "M", "SID")


def test_staleness_fresh_monthly_passes():
    recent = (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d")
    assert Q.check_staleness(recent, "M", "SID") is None


def test_staleness_old_monthly_flags():
    old = (datetime.now() - timedelta(days=200)).strftime("%Y-%m-%d")
    msg = Q.check_staleness(old, "M", "SID")
    assert msg is not None and "Stale" in msg


def test_staleness_thresholds_differ_by_frequency():
    # 30 days old: stale for daily (7d) but fresh for monthly (75d).
    d = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    assert Q.check_staleness(d, "D", "SID") is not None
    assert Q.check_staleness(d, "M", "SID") is None


# --------------------------------------------------------------------------
# check_negative_values / check_duplicates
# --------------------------------------------------------------------------

def test_negative_values_allowed_by_default():
    df = pd.DataFrame({"value": [-1.0, 2.0]})
    assert Q.check_negative_values(df, "SID") is None


def test_negative_values_flagged_when_disallowed():
    df = pd.DataFrame({"value": [-1.0, 2.0, -3.0]})
    msg = Q.check_negative_values(df, "SID", allow_negative=False)
    assert msg is not None and "negative" in msg


def test_duplicates_on_date_column():
    df = pd.DataFrame({"date": ["2020-01-01", "2020-01-01", "2020-02-01"],
                       "value": [1.0, 2.0, 3.0]})
    msg = Q.check_duplicates(df, "SID")
    assert msg is not None and "duplicate" in msg


def test_duplicates_none_when_unique():
    df = pd.DataFrame({"date": ["2020-01-01", "2020-02-01"], "value": [1.0, 2.0]})
    assert Q.check_duplicates(df, "SID") is None


# --------------------------------------------------------------------------
# validate_series (composition)
# --------------------------------------------------------------------------

def test_validate_series_insufficient_data_short_circuits():
    df = pd.DataFrame({"value": [1.0, 2.0]})  # below min_observations
    issues = Q.validate_series(df, "SID", frequency="M")
    assert len(issues) == 1 and "Insufficient" in issues[0]


def test_validate_series_clean_series_has_no_issues(clean_value_df):
    issues = Q.validate_series(clean_value_df, "SID", frequency="M")
    assert issues == []


def test_validate_series_collects_multiple_issues():
    # Constant series: triggers zero-variance; long enough to pass min obs.
    n = QUALITY_CONFIG["min_observations"] + 5
    idx = pd.date_range(end=pd.Timestamp.today(), periods=n, freq="MS")
    df = pd.DataFrame({"value": [5.0] * n}, index=idx)
    issues = Q.validate_series(df, "SID", frequency="M")
    assert any("Zero variance" in i for i in issues)
