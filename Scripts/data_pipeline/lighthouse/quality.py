"""
LIGHTHOUSE MACRO - DATA QUALITY
===============================
Validation, sanity checks, and quality flags.
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import logging

from .config import QUALITY_CONFIG, DB_PATH

logger = logging.getLogger(__name__)


# ==========================================
# QUALITY CHECK FUNCTIONS
# ==========================================

def check_missing_values(df: pd.DataFrame, series_id: str, threshold: float = None) -> Optional[str]:
    """Check for excessive missing values."""
    threshold = threshold or QUALITY_CONFIG["max_missing_pct"]

    if df.empty:
        return f"{series_id}: Empty dataframe"

    missing_pct = df["value"].isna().sum() / len(df)
    if missing_pct > threshold:
        return f"{series_id}: {missing_pct:.1%} missing values (threshold: {threshold:.1%})"

    return None


def check_zero_variance(df: pd.DataFrame, series_id: str) -> Optional[str]:
    """Check for constant series (zero variance)."""
    if df["value"].std() == 0:
        return f"{series_id}: Zero variance (constant value)"
    return None


def check_outliers(df: pd.DataFrame, series_id: str, z_threshold: float = None) -> Optional[str]:
    """Check for extreme outliers."""
    z_threshold = z_threshold or QUALITY_CONFIG["outlier_z_threshold"]

    values = df["value"].dropna()
    if len(values) < 3:
        return None

    mean = values.mean()
    std = values.std()

    if std == 0:
        return None

    z_scores = np.abs((values - mean) / std)
    outlier_count = (z_scores > z_threshold).sum()

    if outlier_count > 0:
        max_z = z_scores.max()
        return f"{series_id}: {outlier_count} extreme outliers (max z-score: {max_z:.1f})"

    return None


def check_staleness(
    last_value_date: str,
    frequency: str,
    series_id: str
) -> Optional[str]:
    """Check if series is stale (hasn't updated when it should have)."""
    if not last_value_date:
        return f"{series_id}: No data"

    try:
        last_date = pd.to_datetime(last_value_date)
    except Exception:
        return f"{series_id}: Invalid date format"

    today = datetime.now()
    days_since = (today - last_date).days

    # Determine expected update frequency based on series cadence
    freq_upper = (frequency or "").upper()
    if freq_upper in ["D", "DAILY"]:
        stale_threshold = QUALITY_CONFIG["stale_days_daily"]
    elif freq_upper in ["W", "WEEKLY"]:
        stale_threshold = QUALITY_CONFIG["stale_days_weekly"]
    elif freq_upper in ["M", "MONTHLY"]:
        stale_threshold = QUALITY_CONFIG["stale_days_monthly"]
    elif freq_upper in ["Q", "QUARTERLY"]:
        stale_threshold = QUALITY_CONFIG["stale_days_quarterly"]
    elif freq_upper in ["A", "ANNUAL", "ANNUALLY", "Y", "YEARLY"]:
        stale_threshold = QUALITY_CONFIG["stale_days_annual"]
    else:
        # Default to monthly threshold for unknown frequencies
        stale_threshold = QUALITY_CONFIG["stale_days_monthly"]

    if days_since > stale_threshold:
        return f"{series_id}: Stale ({days_since} days since last update, threshold: {stale_threshold})"

    return None


def check_negative_values(df: pd.DataFrame, series_id: str, allow_negative: bool = True) -> Optional[str]:
    """Check for unexpected negative values."""
    if allow_negative:
        return None

    negative_count = (df["value"] < 0).sum()
    if negative_count > 0:
        return f"{series_id}: {negative_count} unexpected negative values"

    return None


# Series where a value <= 0 is physically impossible and always means feed
# corruption, never data. The July 2023-May 2024 breadth incident (285 literal
# 0.0 placeholder rows that reached a published chart) is the reason this
# exists. Match by prefix so spliced siblings (_TV/_HIST) are covered too.
STRICTLY_POSITIVE_PREFIXES = (
    "SPX_PCT_ABOVE_",   # percent of index members above an MA: 0 only if the feed died
)


def check_impossible_zeros(df: pd.DataFrame, series_id: str) -> Optional[str]:
    """Flag value <= 0 for series classes where zero cannot occur in reality."""
    if not series_id.startswith(STRICTLY_POSITIVE_PREFIXES):
        return None

    bad = (df["value"] <= 0).sum()
    if bad > 0:
        return f"{series_id}: {bad} impossible zero/negative values (feed corruption class)"

    return None


def check_duplicates(df: pd.DataFrame, series_id: str) -> Optional[str]:
    """Check for duplicate dates."""
    if "date" in df.columns:
        dupe_count = df["date"].duplicated().sum()
    else:
        dupe_count = df.index.duplicated().sum()

    if dupe_count > 0:
        return f"{series_id}: {dupe_count} duplicate dates"

    return None


# ==========================================
# SERIES VALIDATION
# ==========================================

def validate_series(df: pd.DataFrame, series_id: str, frequency: str = None) -> List[str]:
    """
    Run all quality checks on a series.

    Returns list of issue strings (empty if all checks pass).
    """
    issues = []

    # Basic checks
    if len(df) < QUALITY_CONFIG["min_observations"]:
        issues.append(f"{series_id}: Insufficient data ({len(df)} obs, min: {QUALITY_CONFIG['min_observations']})")
        return issues  # Skip other checks

    # Run checks
    check = check_missing_values(df, series_id)
    if check:
        issues.append(check)

    check = check_zero_variance(df, series_id)
    if check:
        issues.append(check)

    check = check_outliers(df, series_id)
    if check:
        issues.append(check)

    check = check_duplicates(df, series_id)
    if check:
        issues.append(check)

    check = check_impossible_zeros(df, series_id)
    if check:
        issues.append(check)

    # Staleness check if we have date info
    if not df.empty:
        if isinstance(df.index, pd.DatetimeIndex):
            last_date = df.index.max().strftime("%Y-%m-%d")
        elif "date" in df.columns:
            last_date = df["date"].max()
        else:
            last_date = None

        if last_date and frequency:
            check = check_staleness(last_date, frequency, series_id)
            if check:
                issues.append(check)

    return issues


# ==========================================
# DATABASE QUALITY REPORT
# ==========================================

def run_quality_report(conn: sqlite3.Connection = None) -> pd.DataFrame:
    """
    Run quality checks on all series in the database.

    Returns DataFrame with quality status for each series.
    """
    if conn is None:
        conn = sqlite3.connect(DB_PATH)
        close_conn = True
    else:
        close_conn = False

    # Get all series metadata
    series_meta = pd.read_sql("""
        SELECT series_id, title, source, category, frequency, last_updated
        FROM series_meta
    """, conn)

    results = []

    logger.info(f"Running quality checks on {len(series_meta)} series...")

    for idx, row in series_meta.iterrows():
        series_id = row["series_id"]
        frequency = row["frequency"] or "M"

        # Fetch data
        df = pd.read_sql("""
            SELECT date, value FROM observations
            WHERE series_id = ?
            ORDER BY date
        """, conn, params=[series_id])

        if not df.empty:
            df["date"] = pd.to_datetime(df["date"], errors="coerce")
            df = df.dropna(subset=["date"])
            df = df.set_index("date")

        # Run validation
        issues = validate_series(df, series_id, frequency)

        # Determine quality status
        if not issues:
            status = "good"
        elif any("Stale" in i for i in issues):
            status = "stale"
        elif any("Insufficient" in i or "Empty" in i for i in issues):
            status = "insufficient"
        elif any("outlier" in i.lower() for i in issues):
            status = "suspect"
        else:
            status = "warning"

        results.append({
            "series_id": series_id,
            "title": row["title"],
            "source": row["source"],
            "category": row["category"],
            "frequency": frequency,
            "obs_count": len(df),
            "first_date": df.index.min().strftime("%Y-%m-%d") if len(df) > 0 else None,
            "last_date": df.index.max().strftime("%Y-%m-%d") if len(df) > 0 else None,
            "quality_status": status,
            "issues": "; ".join(issues) if issues else None,
        })

        if (idx + 1) % 100 == 0:
            logger.info(f"   Checked {idx + 1} series...")

    if close_conn:
        conn.close()

    df_results = pd.DataFrame(results)

    # Summary
    status_counts = df_results["quality_status"].value_counts()
    logger.info("\n--- Quality Summary ---")
    for status, count in status_counts.items():
        logger.info(f"   {status}: {count}")

    return df_results


def update_quality_flags(conn: sqlite3.Connection = None):
    """
    Update quality flags in series_meta table.
    """
    if conn is None:
        conn = sqlite3.connect(DB_PATH)
        close_conn = True
    else:
        close_conn = False

    c = conn.cursor()

    # Ensure quality columns exist
    try:
        c.execute("ALTER TABLE series_meta ADD COLUMN data_quality TEXT")
    except sqlite3.OperationalError:
        pass  # Column already exists

    try:
        c.execute("ALTER TABLE series_meta ADD COLUMN last_value_date TEXT")
    except sqlite3.OperationalError:
        pass

    try:
        c.execute("ALTER TABLE series_meta ADD COLUMN obs_count INTEGER")
    except sqlite3.OperationalError:
        pass

    # Run quality report
    df_quality = run_quality_report(conn)

    # Update each series
    for _, row in df_quality.iterrows():
        c.execute("""
            UPDATE series_meta
            SET data_quality = ?,
                last_value_date = ?,
                obs_count = ?
            WHERE series_id = ?
        """, (row["quality_status"], row["last_date"], row["obs_count"], row["series_id"]))

    conn.commit()

    if close_conn:
        conn.close()

    logger.info("Quality flags updated in database.")

    return df_quality


def get_problem_series(conn: sqlite3.Connection = None) -> pd.DataFrame:
    """Get series with quality issues."""
    if conn is None:
        conn = sqlite3.connect(DB_PATH)
        close_conn = True
    else:
        close_conn = False

    df = pd.read_sql("""
        SELECT series_id, title, source, data_quality, last_value_date, obs_count
        FROM series_meta
        WHERE data_quality IS NOT NULL AND data_quality != 'good'
        ORDER BY data_quality, source
    """, conn)

    if close_conn:
        conn.close()

    return df


def get_stale_series(conn: sqlite3.Connection = None, days: int = 30) -> pd.DataFrame:
    """Get series that haven't updated in specified days."""
    if conn is None:
        conn = sqlite3.connect(DB_PATH)
        close_conn = True
    else:
        close_conn = False

    cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

    df = pd.read_sql(f"""
        SELECT series_id, title, source, frequency, last_value_date
        FROM series_meta
        WHERE last_value_date < '{cutoff}'
        ORDER BY last_value_date
    """, conn)

    if close_conn:
        conn.close()

    return df
