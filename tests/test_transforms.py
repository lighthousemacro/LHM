"""Unit tests for Scripts/data_pipeline/lighthouse/transforms.py.

These transforms are the single source of truth that feeds every downstream
index, so a silent off-by-one in period mapping or a sign error here corrupts
the whole pipeline. They are pure functions over pandas Series — cheap to pin
down exactly.
"""

import numpy as np
import pandas as pd
import pytest

from lighthouse import transforms as T


# --------------------------------------------------------------------------
# Core arithmetic transforms
# --------------------------------------------------------------------------

def test_yoy_pct_basic():
    s = pd.Series([100.0, 110.0, 121.0])
    out = T.yoy_pct(s, periods=1)
    assert np.isnan(out.iloc[0])
    assert out.iloc[1] == pytest.approx(10.0)
    assert out.iloc[2] == pytest.approx(10.0)


def test_yoy_pct_default_period_is_12():
    s = pd.Series(range(1, 25), dtype=float)  # 24 obs
    out = T.yoy_pct(s)  # default periods=12
    # First 12 are NaN (no value 12 periods back)
    assert out.iloc[:12].isna().all()
    # value[12]=13 vs value[0]=1 -> 1200% change
    assert out.iloc[12] == pytest.approx(1200.0)


def test_yoy_diff_is_simple_difference():
    s = pd.Series([1.0, 2.0, 5.0])
    out = T.yoy_diff(s, periods=1)
    assert np.isnan(out.iloc[0])
    assert out.iloc[1] == pytest.approx(1.0)
    assert out.iloc[2] == pytest.approx(3.0)


def test_mom_pct_and_mom_diff():
    s = pd.Series([200.0, 220.0])
    assert T.mom_pct(s).iloc[1] == pytest.approx(10.0)
    assert T.mom_diff(s).iloc[1] == pytest.approx(20.0)


def test_ann_3m_annualizes_to_the_fourth_power():
    # A constant 1% step compounded over 3 months, annualized (^4).
    s = pd.Series([100.0, 100.0, 100.0, 101.0])
    out = T.ann_3m(s)
    expected = (((101.0 / 100.0) ** 4) - 1) * 100
    assert out.iloc[3] == pytest.approx(expected)


def test_ann_6m_annualizes_to_the_second_power():
    s = pd.Series([100.0] * 6 + [102.0])
    out = T.ann_6m(s)
    expected = (((102.0 / 100.0) ** 2) - 1) * 100
    assert out.iloc[6] == pytest.approx(expected)


# --------------------------------------------------------------------------
# Rolling z-score
# --------------------------------------------------------------------------

def test_z_score_min_periods_half_window():
    # window=4 -> min_periods=2, so index 0 is NaN, index 1 onward defined.
    s = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0])
    out = T.z_score(s, window=4)
    assert np.isnan(out.iloc[0])
    assert not np.isnan(out.iloc[1])


def test_z_score_constant_series_is_nan_or_inf_free_div():
    # Constant series -> std 0 -> division by zero -> NaN/inf, never a finite z.
    s = pd.Series([5.0] * 10)
    out = T.z_score(s, window=4)
    assert not np.isfinite(out.dropna()).any()


def test_z_score_known_value():
    # On a window where mean and std are analytically known.
    s = pd.Series([0.0, 0.0, 0.0, 0.0, 4.0])
    out = T.z_score(s, window=5)
    # window of all 5: mean=0.8, sample std = sqrt(variance).
    win = s.values
    expected = (4.0 - win.mean()) / win.std(ddof=1)
    assert out.iloc[4] == pytest.approx(expected)


# --------------------------------------------------------------------------
# Series-type inference (keyword precedence matters)
# --------------------------------------------------------------------------

@pytest.mark.parametrize(
    "series_id, title, expected",
    [
        ("DGS10", "10-Year Treasury Constant Maturity Rate", "rate"),
        ("BAMLH0A0HYM2", "ICE BofA US High Yield OAS", "rate"),
        ("VIXCLS", "CBOE Volatility Index", "index"),
        ("NFCI", "Chicago Fed National Financial Conditions Index", "index"),
        ("TCU", "Capacity Utilization", "ratio"),
        ("PCEPI", "Personal Consumption Expenditures Price Deflator", "price"),
        ("PAYEMS", "All Employees Total Nonfarm", "level"),
    ],
)
def test_infer_series_type(series_id, title, expected):
    assert T.infer_series_type(series_id, title) == expected


def test_infer_series_type_rate_keyword_wins_over_ratio():
    # "Unemployment Rate" contains both 'unemployment' (ratio) and 'rate'.
    # 'rate' is checked first, so the documented behavior is 'rate'.
    assert T.infer_series_type("UNRATE", "Unemployment Rate") == "rate"


def test_infer_series_type_handles_none_title():
    assert T.infer_series_type("SOMEID", None) == "level"


# --------------------------------------------------------------------------
# Frequency inference & period mapping
# --------------------------------------------------------------------------

def test_infer_frequency_monthly():
    df = pd.DataFrame({"value": range(12)},
                      index=pd.date_range("2020-01-01", periods=12, freq="MS"))
    assert T.infer_frequency(df) == "M"


def test_infer_frequency_daily_and_unknown():
    daily = pd.DataFrame({"value": range(10)},
                         index=pd.date_range("2020-01-01", periods=10, freq="D"))
    assert T.infer_frequency(daily) == "D"
    # Fewer than 3 rows -> Unknown.
    tiny = pd.DataFrame({"value": [1, 2]},
                        index=pd.date_range("2020-01-01", periods=2, freq="D"))
    assert T.infer_frequency(tiny) == "U"


def test_get_periods_for_freq_known_and_default():
    assert T.get_periods_for_freq("M") == {"yoy": 12, "mom": 1, "z_window": 24}
    assert T.get_periods_for_freq("Q") == {"yoy": 4, "mom": 1, "z_window": 8}
    # Unknown frequency falls back to monthly mapping.
    assert T.get_periods_for_freq("ZZZ") == T.get_periods_for_freq("M")


# --------------------------------------------------------------------------
# Default-transform selection
# --------------------------------------------------------------------------

def test_get_default_transforms_by_type():
    assert T.get_default_transforms("rate", "M") == ["diff", "yoy_diff", "z"]
    assert T.get_default_transforms("price", "M") == [
        "yoy_pct", "mom_pct", "3m_ann", "6m_ann",
    ]


def test_get_default_transforms_level_is_frequency_aware():
    assert T.get_default_transforms("level", "M") == ["yoy_pct", "mom_pct", "z"]
    assert T.get_default_transforms("level", "Q") == ["yoy_pct", "qoq_pct", "z"]
    assert T.get_default_transforms("level", "D") == ["yoy_pct", "wow_pct", "z"]


# --------------------------------------------------------------------------
# apply_transforms composition
# --------------------------------------------------------------------------

def test_apply_transforms_uses_frequency_aware_periods():
    s = pd.Series(range(1, 25), dtype=float,
                  index=pd.date_range("2020-01-01", periods=24, freq="MS"))
    out = T.apply_transforms(s, ["yoy_pct", "z"], freq="M")
    assert list(out.columns) == ["raw", "yoy_pct", "z"]
    # yoy_pct uses the 12-period mapping for monthly data.
    assert out["yoy_pct"].iloc[:12].isna().all()
    assert out["yoy_pct"].iloc[12] == pytest.approx(1200.0)


def test_apply_transforms_swallows_unknown_transform():
    s = pd.Series([1.0, 2.0, 3.0])
    out = T.apply_transforms(s, ["not_a_real_transform"], freq="M")
    # Unknown transforms are skipped silently; only 'raw' survives.
    assert list(out.columns) == ["raw"]


def test_apply_transforms_df_requires_value_column():
    df = pd.DataFrame({"not_value": [1, 2, 3]})
    with pytest.raises(ValueError):
        T.apply_transforms_df(df, ["yoy_pct"], freq="M")
