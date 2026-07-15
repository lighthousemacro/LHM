#!/usr/bin/env python3
"""
LIGHTHOUSE MACRO - CRYPTO INDEX COMPUTATION
============================================
Computes crypto-specific indices from the observations table (live free feeds).

Indices computed (LIVE, daily):
    - CLI (Crypto Liquidity Impulse) - 4-component liquidity composite
      (ported from Scripts/backtest/cli_final.py, method PINNED 2026-07-09)
    - SLI (Stablecoin Liquidity Impulse) - rate of change in stablecoin market cap
      (rewired 2026-07-09 to STABLECOIN_TOTAL_MCAP, DefiLlama USDT+USDC)
      plus variants SLI_MCAP, SLI_ROC_30D, SLI_ROC_90D_ANN

RETIRED (paid-fundamentals lineup, crypto_scores feed dead 2026-02-02,
zombie rows purged from lighthouse_indices 2026-07-09 — functions kept for
reference, gated off by COMPUTE_RETIRED_FUNDAMENTALS):
    - CFI (Crypto Fundamentals Index) - aggregate health of DeFi protocols
    - CDI (Crypto Developer Index) - development activity across protocols
    - CVI (Crypto Valuation Index) - aggregate valuation metrics (P/F, P/S)
    - CTI (Crypto Tier Index) - count/ratio of Tier 1 vs Avoid protocols
    - CRYPTO_*_HEALTH sector composites

These indices integrate into Pillar 10 (Plumbing) and provide crypto-specific
signals for the broader macro framework.

Usage:
    python compute_crypto_indices.py              # Compute all crypto indices
    python compute_crypto_indices.py --latest     # Only compute latest date
    python compute_crypto_indices.py --verify     # Verify against thresholds
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import sys
import os

# Add paths
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, "/Users/bob/LHM")

from lighthouse.config import DB_PATH as CONFIG_DB_PATH

# Database path
DB_PATH = Path("/Users/bob/LHM/Data/databases/Lighthouse_Master.db")


# ==========================================
# CLI CONFIGURATION (PINNED — no per-run method re-selection)
# ==========================================
# Method locked 2026-07-09 from the validated cli_final.py run: rolling 3-year
# (756d) z-scores on each raw component, winsorized to +/-3, weighted sum.
# cli_final.py re-selects the z-method every run via in-sample quintile tests;
# the daily pipeline must NOT do that — one method, forever, until an explicit
# re-validation changes it here. Component weights are proprietary (in code
# only, never published).
CLI_WEIGHTS = {
    'DollarYoY': 0.20,       # -(DTWEXBGS 252d % change)
    'ResRatio_RoC': 0.50,    # 63d RoC of TOTRESNS/WALCL
    'StableBTC_RoC': 0.15,   # -(21d RoC of stablecoin mcap / BTC price)
    'ResRatio': 0.15,        # TOTRESNS/WALCL level
}
CLI_Z_WINDOW = 756           # rolling 3yr
CLI_Z_MIN_PERIODS = 126
CLI_WINSORIZE = 3.0


# ==========================================
# RETIRED PAID-FUNDAMENTALS GATE
# ==========================================
# CFI/CDI/CVI/CTI/CRYPTO_*_HEALTH read the crypto_scores table, whose paid
# feed died 2026-02-02 (Bob declined a paid replacement; CDLI is the free-data
# successor). Zombie rows purged from lighthouse_indices 2026-07-09. Leave
# this False unless a live fundamentals feed returns.
COMPUTE_RETIRED_FUNDAMENTALS = False


# ==========================================
# STATUS THRESHOLDS (Crypto-Specific)
# ==========================================

CRYPTO_STATUS_THRESHOLDS = {
    "CLI": [
        (1.0, "STRONG EXPANSION"),
        (0.3, "EXPANDING"),
        (-0.3, "NEUTRAL"),
        (-1.0, "CONTRACTING"),
        (-999, "STRONG CONTRACTION")
    ],
    "SLI": [
        (1.5, "RAPID EXPANSION"),
        (0.5, "EXPANSION"),
        (-0.5, "STABLE"),
        (-1.0, "CONTRACTION"),
        (-999, "SEVERE CONTRACTION")
    ],
    "CFI": [
        (70, "STRONG FUNDAMENTALS"),
        (55, "HEALTHY"),
        (45, "NEUTRAL"),
        (35, "WEAK"),
        (-999, "POOR FUNDAMENTALS")
    ],
    "CDI": [
        (1.0, "HIGH ACTIVITY"),
        (0.5, "ACTIVE"),
        (-0.5, "MODERATE"),
        (-1.0, "LOW ACTIVITY"),
        (-999, "DORMANT")
    ],
    "CVI": [
        (1.5, "OVERVALUED"),
        (0.5, "RICH"),
        (-0.5, "FAIR VALUE"),
        (-1.0, "CHEAP"),
        (-999, "VERY CHEAP")
    ],
    "CTI": [
        (0.6, "BULLISH SETUP"),
        (0.4, "NEUTRAL"),
        (0.2, "CAUTIOUS"),
        (-999, "BEARISH SETUP")
    ],
    # Sector-specific
    "DEFI_HEALTH": [
        (70, "HEALTHY"),
        (50, "NEUTRAL"),
        (30, "WEAK"),
        (-999, "STRESSED")
    ],
    "L1_HEALTH": [
        (70, "STRONG"),
        (50, "NEUTRAL"),
        (30, "WEAK"),
        (-999, "STRESSED")
    ],
}


def get_crypto_status(index_name: str, value: float) -> str:
    """Get status label for a crypto index value."""
    if pd.isna(value):
        return "NO DATA"
    thresholds = CRYPTO_STATUS_THRESHOLDS.get(index_name, [])
    for threshold, status in thresholds:
        if value >= threshold:
            return status
    return "UNKNOWN"


# ==========================================
# Z-SCORE HELPER
# ==========================================

def compute_zscore(series: pd.Series, window: int = 30, min_periods: int = 10) -> pd.Series:
    """Compute rolling z-score."""
    rolling_mean = series.rolling(window, min_periods=min_periods).mean()
    rolling_std = series.rolling(window, min_periods=min_periods).std()
    rolling_std = rolling_std.replace(0, np.nan)
    return (series - rolling_mean) / rolling_std


# ==========================================
# OBSERVATIONS LOADER
# ==========================================

def load_observation_series(conn: sqlite3.Connection, series_id: str) -> pd.Series:
    """Load a single series from the observations table as a date-indexed Series."""
    df = pd.read_sql(
        "SELECT date, value FROM observations WHERE series_id = ? ORDER BY date",
        conn, params=(series_id,), parse_dates=['date']
    )
    return df.set_index('date')['value'].rename(series_id)


# ==========================================
# CRYPTO INDEX COMPUTATIONS
# ==========================================

def compute_cli(conn: sqlite3.Connection) -> pd.DataFrame:
    """
    Crypto Liquidity Impulse (CLI)

    4-component empirical liquidity composite, ported from
    Scripts/backtest/cli_final.py (production 4-component v5 subset).
    Computed entirely from DB series: DTWEXBGS, TOTRESNS, WALCL,
    CRYPTO_BTC_PRICE, STABLECOIN_TOTAL_MCAP.

    Method (PINNED — see CLI_* constants above):
        raw components -> rolling 756d z (min 126) -> winsorize +/-3
        -> weighted sum (weights proprietary, CLI_WEIGHTS).

    High CLI = liquidity expanding = supportive for crypto risk
    Low CLI = liquidity contracting = headwind

    Returns:
        DataFrame with columns: date, CLI
    """
    try:
        btc = load_observation_series(conn, 'CRYPTO_BTC_PRICE')
        stable = load_observation_series(conn, 'STABLECOIN_TOTAL_MCAP')
        dtwex = load_observation_series(conn, 'DTWEXBGS')
        totres = load_observation_series(conn, 'TOTRESNS')
        walcl = load_observation_series(conn, 'WALCL')

        for name, s, min_len in [('CRYPTO_BTC_PRICE', btc, 1000),
                                 ('STABLECOIN_TOTAL_MCAP', stable, 500),
                                 ('DTWEXBGS', dtwex, 500),
                                 ('TOTRESNS', totres, 100),
                                 ('WALCL', walcl, 500)]:
            if len(s) < min_len:
                print(f"      Warning: {name} history too shallow for CLI "
                      f"({len(s)} obs) — backfill lost?")
                return pd.DataFrame(columns=["date", "CLI"])

        # Everything on the BTC (7-day crypto) calendar, forward-filled —
        # matches cli_final.py exactly.
        idx = btc.index
        dtwex_d = dtwex.reindex(idx, method='ffill')
        res = totres.reindex(idx, method='ffill')
        fed = walcl.reindex(idx, method='ffill')
        stable_d = stable.reindex(idx, method='ffill')

        comps = {}
        comps['DollarYoY'] = -(dtwex_d / dtwex_d.shift(252) - 1)
        comps['ResRatio'] = res / fed
        rr = comps['ResRatio']
        comps['ResRatio_RoC'] = rr / rr.shift(63) - 1
        ratio = stable_d / btc
        comps['StableBTC_RoC'] = -(ratio / ratio.shift(21) - 1)

        # Pinned z-method: rolling 3yr, winsorized
        z_comps = {}
        for k, v in comps.items():
            m = v.rolling(window=CLI_Z_WINDOW, min_periods=CLI_Z_MIN_PERIODS).mean()
            sd = v.rolling(window=CLI_Z_WINDOW, min_periods=CLI_Z_MIN_PERIODS).std()
            z_comps[k] = ((v - m) / sd).clip(lower=-CLI_WINSORIZE, upper=CLI_WINSORIZE)

        cli = sum(CLI_WEIGHTS[k] * z_comps[k] for k in CLI_WEIGHTS).dropna()

        result = cli.rename('CLI').reset_index()
        result.columns = ['date', 'CLI']
        return result

    except Exception as e:
        print(f"      Error computing CLI: {e}")
        return pd.DataFrame(columns=["date", "CLI"])


def compute_sli(conn: sqlite3.Connection) -> pd.DataFrame:
    """
    Stablecoin Liquidity Impulse (SLI)

    Measures rate of change in stablecoin market cap.
    Rewired 2026-07-09: feeds from STABLECOIN_TOTAL_MCAP (DefiLlama USDT+USDC,
    live daily). The original crypto_metrics TVL proxy feed died 2026-02-01;
    stablecoin mcap is what the documented formula wanted in the first place.
    (The issuance and transfer-volume components in the original doc formula
    need paid on-chain data — SLI is the mcap-RoC term alone, z-scored, same
    z-parameters as the TVL-proxy era.)

    Formula:
        SLI = z(mcap_30d_RoC), rolling 90d z (min 30)

    High SLI = Expanding liquidity = Bullish for risk assets
    Low SLI = Contracting liquidity = Bearish / Risk-off

    Variants:
        SLI_MCAP        - total stablecoin market cap, $bn
        SLI_ROC_30D     - 30-day rate of change, percent
        SLI_ROC_90D_ANN - 90-day rate of change annualized (x4), percent

    Returns:
        DataFrame with columns: date, SLI, SLI_MCAP, SLI_ROC_30D, SLI_ROC_90D_ANN
    """
    cols = ["date", "SLI", "SLI_MCAP", "SLI_ROC_30D", "SLI_ROC_90D_ANN"]
    try:
        mcap = load_observation_series(conn, 'STABLECOIN_TOTAL_MCAP')
        if mcap.empty:
            print("      Warning: No STABLECOIN_TOTAL_MCAP data for SLI computation")
            return pd.DataFrame(columns=cols)

        # Guarantee calendar-day shifts (DefiLlama is daily-continuous, but
        # forward-fill any gap so shift(30) is always 30 calendar days)
        mcap = mcap.reindex(
            pd.date_range(mcap.index.min(), mcap.index.max(), freq='D'),
            method='ffill')

        df = pd.DataFrame({'mcap': mcap})
        df['roc_30d'] = df['mcap'] / df['mcap'].shift(30) - 1
        df['roc_90d'] = df['mcap'] / df['mcap'].shift(90) - 1

        # Z-score the rate of change (same parameters as the TVL-proxy era)
        df['SLI'] = compute_zscore(df['roc_30d'], window=90, min_periods=30)

        df['SLI_MCAP'] = df['mcap'] / 1e9                 # $bn
        df['SLI_ROC_30D'] = df['roc_30d'] * 100           # percent
        df['SLI_ROC_90D_ANN'] = df['roc_90d'] * 4 * 100   # percent, simple x4 ann.

        result = df.reset_index().rename(columns={'index': 'date'})
        return result[cols].dropna(subset=['SLI'])

    except Exception as e:
        print(f"      Error computing SLI: {e}")
        return pd.DataFrame(columns=cols)


def compute_cfi(conn: sqlite3.Connection) -> pd.DataFrame:
    """
    Crypto Fundamentals Index (CFI)

    Aggregate fundamental health score across tracked protocols.
    Uses the overall_score from crypto_scores table.

    Formula:
        CFI = mean(overall_score) across all protocols

    Returns:
        DataFrame with columns: date, CFI, protocols_count
    """
    query = """
        SELECT date, AVG(overall_score) as cfi, COUNT(*) as protocols_count
        FROM crypto_scores
        GROUP BY date
        ORDER BY date
    """

    try:
        df = pd.read_sql(query, conn, parse_dates=['date'])
        if df.empty:
            return pd.DataFrame(columns=["date", "CFI", "protocols_count"])

        df.columns = ['date', 'CFI', 'protocols_count']
        return df

    except Exception as e:
        print(f"      Error computing CFI: {e}")
        return pd.DataFrame(columns=["date", "CFI", "protocols_count"])


def compute_cdi(conn: sqlite3.Connection) -> pd.DataFrame:
    """
    Crypto Developer Index (CDI)

    Aggregate developer activity across protocols.
    Uses active_developers from crypto_scores.

    Formula:
        CDI = z(mean(active_developers))

    High CDI = Strong development activity across ecosystem
    Low CDI = Declining development activity

    Returns:
        DataFrame with columns: date, CDI, avg_developers, total_developers
    """
    query = """
        SELECT date,
               AVG(active_developers) as avg_devs,
               SUM(active_developers) as total_devs
        FROM crypto_scores
        GROUP BY date
        ORDER BY date
    """

    try:
        df = pd.read_sql(query, conn, parse_dates=['date'])
        if df.empty:
            return pd.DataFrame(columns=["date", "CDI", "avg_developers", "total_developers"])

        df = df.set_index('date')
        df['CDI'] = compute_zscore(df['avg_devs'], window=30, min_periods=10)

        result = df.reset_index()[['date', 'CDI', 'avg_devs', 'total_devs']]
        result.columns = ['date', 'CDI', 'avg_developers', 'total_developers']

        return result.dropna(subset=['CDI'])

    except Exception as e:
        print(f"      Error computing CDI: {e}")
        return pd.DataFrame(columns=["date", "CDI", "avg_developers", "total_developers"])


def compute_cvi(conn: sqlite3.Connection) -> pd.DataFrame:
    """
    Crypto Valuation Index (CVI)

    Aggregate valuation metrics across protocols.
    Uses P/E and P/F ratios from crypto_scores.

    Formula:
        CVI = z(mean(pe_ratio)) where pe_ratio is capped at 500

    High CVI = Expensive valuations (overvalued)
    Low CVI = Cheap valuations (potentially undervalued)

    Returns:
        DataFrame with columns: date, CVI, avg_pe, avg_pf
    """
    query = """
        SELECT date,
               AVG(CASE WHEN pe_ratio < 500 THEN pe_ratio ELSE NULL END) as avg_pe,
               AVG(CASE WHEN pf_ratio < 1000 THEN pf_ratio ELSE NULL END) as avg_pf
        FROM crypto_scores
        GROUP BY date
        ORDER BY date
    """

    try:
        df = pd.read_sql(query, conn, parse_dates=['date'])
        if df.empty:
            return pd.DataFrame(columns=["date", "CVI", "avg_pe", "avg_pf"])

        df = df.set_index('date')
        df['CVI'] = compute_zscore(df['avg_pe'], window=30, min_periods=10)

        result = df.reset_index()[['date', 'CVI', 'avg_pe', 'avg_pf']]
        result.columns = ['date', 'CVI', 'avg_pe', 'avg_pf']

        return result.dropna(subset=['CVI'])

    except Exception as e:
        print(f"      Error computing CVI: {e}")
        return pd.DataFrame(columns=["date", "CVI", "avg_pe", "avg_pf"])


def compute_cti(conn: sqlite3.Connection) -> pd.DataFrame:
    """
    Crypto Tier Index (CTI)

    Ratio of Tier 1/Tier 2 protocols vs Avoid/Caution.
    Indicates overall health of the crypto ecosystem from fundamental perspective.

    Formula:
        CTI = (Tier1_count + Tier2_count) / total_count

    High CTI (>0.6) = Most protocols are fundamentally sound = Bullish
    Low CTI (<0.3) = Most protocols are problematic = Bearish

    Returns:
        DataFrame with columns: date, CTI, tier1_count, tier2_count, avoid_count
    """
    query = """
        SELECT date,
               SUM(CASE WHEN verdict LIKE '%TIER 1%' THEN 1 ELSE 0 END) as tier1_count,
               SUM(CASE WHEN verdict LIKE '%TIER 2%' THEN 1 ELSE 0 END) as tier2_count,
               SUM(CASE WHEN verdict LIKE '%AVOID%' THEN 1 ELSE 0 END) as avoid_count,
               COUNT(*) as total_count
        FROM crypto_scores
        GROUP BY date
        ORDER BY date
    """

    try:
        df = pd.read_sql(query, conn, parse_dates=['date'])
        if df.empty:
            return pd.DataFrame(columns=["date", "CTI", "tier1_count", "tier2_count", "avoid_count"])

        df['CTI'] = (df['tier1_count'] + df['tier2_count']) / df['total_count']

        return df[['date', 'CTI', 'tier1_count', 'tier2_count', 'avoid_count']]

    except Exception as e:
        print(f"      Error computing CTI: {e}")
        return pd.DataFrame(columns=["date", "CTI", "tier1_count", "tier2_count", "avoid_count"])


def compute_sector_health(conn: sqlite3.Connection) -> pd.DataFrame:
    """
    Sector-specific health indices.

    Computes average overall_score for each sector.

    Returns:
        DataFrame with columns: date, sector, health_score, protocol_count
    """
    query = """
        SELECT date, sector, AVG(overall_score) as health_score, COUNT(*) as protocol_count
        FROM crypto_scores
        GROUP BY date, sector
        ORDER BY date, sector
    """

    try:
        df = pd.read_sql(query, conn, parse_dates=['date'])
        return df

    except Exception as e:
        print(f"      Error computing sector health: {e}")
        return pd.DataFrame(columns=["date", "sector", "health_score", "protocol_count"])


# ==========================================
# MAIN COMPUTATION ENGINE
# ==========================================

def compute_all_crypto_indices(conn: sqlite3.Connection, latest_only: bool = False) -> pd.DataFrame:
    """
    Compute all crypto indices.

    Args:
        conn: Database connection
        latest_only: If True, filter to latest date only

    Returns:
        DataFrame with columns: date, index_id, value, status
    """
    print("\n--- Computing Crypto Indices ---")

    # Compute each index
    print("   Computing CLI (Crypto Liquidity Impulse)...")
    cli_df = compute_cli(conn)

    print("   Computing SLI (Stablecoin Liquidity Impulse)...")
    sli_df = compute_sli(conn)

    if COMPUTE_RETIRED_FUNDAMENTALS:
        print("   Computing CFI (Crypto Fundamentals Index)...")
        cfi_df = compute_cfi(conn)

        print("   Computing CDI (Crypto Developer Index)...")
        cdi_df = compute_cdi(conn)

        print("   Computing CVI (Crypto Valuation Index)...")
        cvi_df = compute_cvi(conn)

        print("   Computing CTI (Crypto Tier Index)...")
        cti_df = compute_cti(conn)

        print("   Computing Sector Health Indices...")
        sector_df = compute_sector_health(conn)
    else:
        print("   Skipping retired paid-fundamentals indices (CFI/CDI/CVI/CTI/sector health)")
        cfi_df = cdi_df = cvi_df = cti_df = sector_df = pd.DataFrame()

    # Build output rows
    rows = []

    # Add CLI
    for _, row in cli_df.iterrows():
        rows.append({
            "date": row['date'].strftime("%Y-%m-%d") if hasattr(row['date'], 'strftime') else str(row['date']),
            "index_id": "CLI",
            "value": round(row['CLI'], 4),
            "status": get_crypto_status("CLI", row['CLI'])
        })

    # Add SLI + variants
    for _, row in sli_df.iterrows():
        date_str = row['date'].strftime("%Y-%m-%d") if hasattr(row['date'], 'strftime') else str(row['date'])
        rows.append({
            "date": date_str,
            "index_id": "SLI",
            "value": round(row['SLI'], 4),
            "status": get_crypto_status("SLI", row['SLI'])
        })
        for variant in ("SLI_MCAP", "SLI_ROC_30D", "SLI_ROC_90D_ANN"):
            if pd.notna(row[variant]):
                rows.append({
                    "date": date_str,
                    "index_id": variant,
                    "value": round(row[variant], 4),
                    "status": None
                })

    # Add CFI
    for _, row in cfi_df.iterrows():
        rows.append({
            "date": row['date'].strftime("%Y-%m-%d") if hasattr(row['date'], 'strftime') else str(row['date']),
            "index_id": "CFI",
            "value": round(row['CFI'], 2),
            "status": get_crypto_status("CFI", row['CFI'])
        })

    # Add CDI
    for _, row in cdi_df.iterrows():
        rows.append({
            "date": row['date'].strftime("%Y-%m-%d") if hasattr(row['date'], 'strftime') else str(row['date']),
            "index_id": "CDI",
            "value": round(row['CDI'], 4),
            "status": get_crypto_status("CDI", row['CDI'])
        })

    # Add CVI
    for _, row in cvi_df.iterrows():
        rows.append({
            "date": row['date'].strftime("%Y-%m-%d") if hasattr(row['date'], 'strftime') else str(row['date']),
            "index_id": "CVI",
            "value": round(row['CVI'], 4),
            "status": get_crypto_status("CVI", row['CVI'])
        })

    # Add CTI
    for _, row in cti_df.iterrows():
        rows.append({
            "date": row['date'].strftime("%Y-%m-%d") if hasattr(row['date'], 'strftime') else str(row['date']),
            "index_id": "CTI",
            "value": round(row['CTI'], 4),
            "status": get_crypto_status("CTI", row['CTI'])
        })

    # Add Sector Health
    for _, row in sector_df.iterrows():
        sector_name = row['sector'].upper().replace(' ', '_').replace('-', '_')[:20]
        index_id = f"CRYPTO_{sector_name}_HEALTH"
        rows.append({
            "date": row['date'].strftime("%Y-%m-%d") if hasattr(row['date'], 'strftime') else str(row['date']),
            "index_id": index_id,
            "value": round(row['health_score'], 2),
            "status": get_crypto_status("DEFI_HEALTH", row['health_score'])
        })

    result_df = pd.DataFrame(rows)

    if latest_only and not result_df.empty:
        latest_date = result_df['date'].max()
        result_df = result_df[result_df['date'] == latest_date]

    print(f"   Generated {len(result_df)} crypto index observations")

    return result_df


def write_crypto_indices_to_db(conn: sqlite3.Connection, indices_df: pd.DataFrame):
    """Write computed crypto indices to lighthouse_indices table."""
    c = conn.cursor()

    # Create table if not exists (same schema as macro indices)
    c.execute('''CREATE TABLE IF NOT EXISTS lighthouse_indices (
        date TEXT,
        index_id TEXT,
        value REAL,
        status TEXT,
        PRIMARY KEY (date, index_id)
    )''')

    # Insert/replace data
    for _, row in indices_df.iterrows():
        c.execute("""
            INSERT OR REPLACE INTO lighthouse_indices (date, index_id, value, status)
            VALUES (?, ?, ?, ?)
        """, (row["date"], row["index_id"], row["value"], row["status"]))

    conn.commit()
    print(f"   Wrote {len(indices_df)} crypto index rows to lighthouse_indices")


def verify_crypto_indices(conn: sqlite3.Connection):
    """Verify latest crypto index values."""
    print("\n--- Verification: Latest Crypto Index Values ---")

    query = """
        SELECT li.index_id, li.value, li.status, li.date
        FROM lighthouse_indices li
        JOIN (
            SELECT index_id, MAX(date) AS max_date
            FROM lighthouse_indices
            WHERE index_id IN ('CLI', 'SLI', 'SLI_MCAP', 'SLI_ROC_30D',
                               'SLI_ROC_90D_ANN', 'CRYPTO_DEFI_LIQUIDITY')
            GROUP BY index_id
        ) latest ON li.index_id = latest.index_id AND li.date = latest.max_date
        ORDER BY li.index_id
    """

    try:
        latest = pd.read_sql(query, conn)

        if latest.empty:
            print("   No crypto indices found in database")
            return

        print(f"\nLatest crypto values ({latest['date'].iloc[0] if len(latest) > 0 else 'N/A'}):")
        print("-" * 60)

        for _, row in latest.iterrows():
            status_str = row['status'] if row['status'] else "N/A"
            print(f"   {row['index_id']:25} {row['value']:>10.3f}  [{status_str}]")

        print("-" * 60)

    except Exception as e:
        print(f"   Error verifying indices: {e}")


# ==========================================
# CLI
# ==========================================

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Compute Lighthouse Macro Crypto Indices")
    parser.add_argument("--latest", action="store_true", help="Only compute latest date")
    parser.add_argument("--verify", action="store_true", help="Verify against expected values")
    parser.add_argument("--dry-run", action="store_true", help="Compute but don't write to database")

    args = parser.parse_args()

    print("=" * 70)
    print("LIGHTHOUSE MACRO - CRYPTO INDEX COMPUTATION")
    print(f"Database: {DB_PATH}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    conn = sqlite3.connect(DB_PATH, timeout=60)
    conn.execute("PRAGMA busy_timeout=60000")

    # Check the live feed exists (CLI/SLI read observations, not crypto_scores)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM observations WHERE series_id = 'STABLECOIN_TOTAL_MCAP'")
    if c.fetchone()[0] == 0:
        print("\nWARNING: STABLECOIN_TOTAL_MCAP has no observations.")
        print("Run the pipeline with --sources CRYPTO first to populate crypto data.")
        conn.close()
        return

    # Compute indices
    indices_df = compute_all_crypto_indices(conn, latest_only=args.latest)

    if indices_df.empty:
        print("\nNo crypto indices computed - ensure crypto data is populated first.")
        conn.close()
        return

    # Write to database
    if not args.dry_run:
        print("\n--- Writing to Database ---")
        write_crypto_indices_to_db(conn, indices_df)
    else:
        print("\n--- Dry Run: Skipping database write ---")

    # Verify
    if args.verify or not args.dry_run:
        verify_crypto_indices(conn)

    conn.close()

    print("\n" + "=" * 70)
    print("CRYPTO INDEX COMPUTATION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
