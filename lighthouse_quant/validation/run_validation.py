#!/usr/bin/env python3
"""
LIGHTHOUSE MACRO - INDICATOR VALIDATION RUNNER
===============================================
Runs comprehensive validation of all indicators and composites.

Usage:
    python -m lighthouse_quant.validation.run_validation
    python -m lighthouse_quant.validation.run_validation --quick
    python -m lighthouse_quant.validation.run_validation --output report.html
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
import argparse
import warnings
import json

# Add parent to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from lighthouse_quant.config import (
    DB_PATH, OUTPUT_DIR, INDICATOR_RELATIONSHIPS,
    NBER_RECESSIONS, ZSCORE_WINDOW_MONTHLY
)
from lighthouse_quant.data.loaders import (
    load_horizon_dataset, load_lighthouse_indices, create_nber_recession_series,
    resample_to_monthly
)
from lighthouse_quant.validation.lead_lag import (
    validate_all_relationships, validate_indicator_relationship,
    compute_cross_correlation
)
from lighthouse_quant.validation.weight_optimization import (
    analyze_component_importance, validate_composite_weights,
    optimize_weights_elastic_net, ORIGINAL_WEIGHTS
)
from lighthouse_quant.validation.regime_validation import (
    validate_against_nber, compute_regime_statistics,
    MRI_REGIMES, LFI_REGIMES, LCI_REGIMES, create_nber_series
)


def print_header(title: str):
    """Print formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_subheader(title: str):
    """Print formatted subsection header."""
    print(f"\n--- {title} ---")


def run_lead_lag_validation(df: pd.DataFrame) -> pd.DataFrame:
    """Run lead-lag validation for all configured relationships."""
    print_header("LEAD-LAG VALIDATION")

    # Resample to monthly for lead-lag analysis
    df_monthly = resample_to_monthly(df)
    print(f"Data resampled to monthly: {len(df_monthly)} observations")
    print(f"Date range: {df_monthly.index.min().date()} to {df_monthly.index.max().date()}")

    # Run validation
    results = validate_all_relationships(
        df_monthly,
        INDICATOR_RELATIONSHIPS,
        max_lag=24
    )

    # Print results
    print_subheader("Results Summary")

    valid_count = results["valid"].sum()
    total_count = len(results)
    print(f"Relationships validated: {valid_count}/{total_count} ({valid_count/total_count*100:.1f}%)")

    print_subheader("Detailed Results")
    print(f"{'Leading':<25} {'Lagging':<25} {'Exp Lag':>8} {'Opt Lag':>8} {'Corr':>8} {'Granger':>10} {'Valid':>6}")
    print("-" * 100)

    for _, row in results.iterrows():
        valid_mark = "Y" if row["valid"] else "N"
        granger_str = f"{row['granger_pvalue']:.4f}" if pd.notna(row['granger_pvalue']) else "N/A"
        corr_str = f"{row['correlation']:.3f}" if pd.notna(row['correlation']) else "N/A"

        print(f"{row['leading']:<25} {row['lagging']:<25} {row['expected_lag']:>8} "
              f"{row['optimal_lag']:>8} {corr_str:>8} {granger_str:>10} {valid_mark:>6}")

    # Highlight key findings
    print_subheader("Key Findings")

    # Best leading indicators (strongest correlations with significant Granger)
    significant = results[results["granger_pvalue"] < 0.05].copy()
    if len(significant) > 0:
        significant = significant.sort_values("correlation", key=abs, ascending=False)
        print("\nStrongest validated relationships (Granger p < 0.05):")
        for _, row in significant.head(5).iterrows():
            print(f"  {row['leading']} -> {row['lagging']}: "
                  f"r={row['correlation']:.3f} at lag {row['optimal_lag']}m")

    # Relationships that didn't validate
    invalid = results[~results["valid"]]
    if len(invalid) > 0:
        print("\nRelationships that need review:")
        for _, row in invalid.iterrows():
            reason = []
            if not row["relationship_ok"]:
                reason.append("weak correlation")
            if not row["lead_ok"]:
                reason.append(f"lag mismatch (expected {row['expected_lag']}, got {row['optimal_lag']})")
            print(f"  {row['leading']} -> {row['lagging']}: {', '.join(reason)}")

    return results


def run_weight_validation(df: pd.DataFrame, indices: pd.DataFrame) -> dict:
    """Validate composite weights for key indices."""
    print_header("COMPOSITE WEIGHT VALIDATION")

    df_monthly = resample_to_monthly(df)

    results = {}

    # LFI Weight Validation
    print_subheader("LFI (Labor Fragility Index)")

    # Prepare LFI components
    lfi_components = pd.DataFrame(index=df_monthly.index)

    # Z-score of long-term unemployed
    if "Unemployed_27wks_Plus_z" in df_monthly.columns:
        lfi_components["z_longterm"] = df_monthly["Unemployed_27wks_Plus_z"]
    elif "Unemployed_27wks_Plus" in df_monthly.columns:
        lfi_components["z_longterm"] = (
            df_monthly["Unemployed_27wks_Plus"]
            .rolling(ZSCORE_WINDOW_MONTHLY).apply(lambda x: (x.iloc[-1] - x.mean()) / x.std())
        )

    # Inverted quits rate z-score
    if "JOLTS_Quits_Rate_z" in df_monthly.columns:
        lfi_components["z_quits_inv"] = -df_monthly["JOLTS_Quits_Rate_z"]
    elif "JOLTS_Quits_Rate" in df_monthly.columns:
        quits_z = (
            df_monthly["JOLTS_Quits_Rate"]
            .rolling(ZSCORE_WINDOW_MONTHLY).apply(lambda x: (x.iloc[-1] - x.mean()) / x.std())
        )
        lfi_components["z_quits_inv"] = -quits_z

    # Hires/Quits ratio (inverted)
    if "JOLTS_Hires_Rate" in df_monthly.columns and "JOLTS_Quits_Rate" in df_monthly.columns:
        ratio = df_monthly["JOLTS_Hires_Rate"] / df_monthly["JOLTS_Quits_Rate"].replace(0, np.nan)
        ratio_z = ratio.rolling(ZSCORE_WINDOW_MONTHLY).apply(
            lambda x: (x.iloc[-1] - x.mean()) / x.std() if x.std() > 0 else 0
        )
        lfi_components["z_hires_quits_inv"] = -ratio_z

    # Target: Forward 12-month change in unemployment rate
    if "Unemployment_Rate_U3" in df_monthly.columns:
        target = df_monthly["Unemployment_Rate_U3"].diff(12).shift(-12)
    else:
        target = None

    if target is not None and len(lfi_components.dropna()) > 50:
        importance = analyze_component_importance(lfi_components, target)
        print("\nComponent importance (data-driven):")
        print(importance.to_string())

        print("\nOriginal weights:")
        for comp, weight in ORIGINAL_WEIGHTS["LFI"].items():
            print(f"  {comp}: {weight:.2f}")

        results["LFI"] = {
            "importance": importance.to_dict(),
            "original_weights": ORIGINAL_WEIGHTS["LFI"]
        }
    else:
        print("Insufficient data for LFI weight validation")

    # MRI Weight Validation
    print_subheader("MRI (Macro Risk Index)")

    if "MRI" in indices.columns:
        # MRI components are the pillar indices
        mri_components = indices[[c for c in ["LPI", "PCI", "GCI", "HCI", "CCI", "BCI",
                                               "TCI", "GCI_Gov", "FCI", "LCI"]
                                   if c in indices.columns]].copy()

        # Target: Forward 6-month equity returns (proxy with recession indicator)
        recession = create_nber_series(mri_components.index)
        recession_fwd = recession.shift(-6)  # Forward 6 months

        if len(mri_components.dropna()) > 50:
            importance = analyze_component_importance(mri_components, recession_fwd)
            print("\nComponent importance for predicting recession (data-driven):")
            print(importance.to_string())

            print("\nOriginal MRI weights:")
            for comp, weight in ORIGINAL_WEIGHTS["MRI"].items():
                print(f"  {comp}: {weight:+.2f}")

            results["MRI"] = {
                "importance": importance.to_dict(),
                "original_weights": ORIGINAL_WEIGHTS["MRI"]
            }
    else:
        print("MRI not found in indices")

    return results


def run_regime_validation(indices: pd.DataFrame) -> dict:
    """Validate regime indicators against NBER recessions."""
    print_header("REGIME VALIDATION VS NBER RECESSIONS")

    results = {}

    # Resample to monthly
    indices_monthly = resample_to_monthly(indices)

    # MRI Validation
    if "MRI" in indices_monthly.columns:
        print_subheader("MRI (Macro Risk Index)")

        mri = indices_monthly["MRI"].dropna()
        print(f"MRI data: {len(mri)} months from {mri.index.min().date()} to {mri.index.max().date()}")

        # Test different thresholds (recalibrated 2026-01-19)
        # New thresholds: Elevated > 0.10, High Risk > 0.25, Crisis > 0.50
        for threshold in [0.10, 0.25, 0.50]:
            result = validate_against_nber(
                mri,
                threshold=threshold,
                threshold_direction="above",
                min_signal_months=2,
                max_lead_months=18,
                start_date="1970-01-01"
            )

            label = {0.10: "Elevated", 0.25: "High Risk", 0.50: "Crisis"}[threshold]
            print(f"\nThreshold > {threshold} ({label}):")
            print(f"  Recessions detected: {result.n_recessions_detected}/{result.n_recessions_tested} "
                  f"({result.true_positive_rate*100:.1f}%)")
            print(f"  Average lead time: {result.average_lead_time:.1f} months")
            print(f"  False alarms: {result.n_false_alarms}")
            print(f"  Precision: {result.precision:.2f}, Recall: {result.recall:.2f}, F1: {result.f1_score:.2f}")

            if threshold == 0.25:  # Store High Risk threshold results
                results["MRI"] = {
                    "threshold": threshold,
                    "detection_rate": result.true_positive_rate,
                    "avg_lead_time": result.average_lead_time,
                    "precision": result.precision,
                    "recall": result.recall,
                    "f1": result.f1_score,
                    "details": result.recession_details
                }

        # Per-recession detail for MRI > 0.25 (High Risk)
        print("\nPer-recession detail (MRI > 0.25 High Risk):")
        result = validate_against_nber(mri, threshold=0.25, threshold_direction="above")
        for rec in result.recession_details:
            detected = "Y" if rec["detected"] else "N"
            lead = f"{rec['lead_months']:.1f}m" if pd.notna(rec['lead_months']) else "N/A"
            print(f"  {rec['recession_start'].strftime('%Y-%m')}: Detected={detected}, Lead={lead}")

    # LFI Validation
    if "LFI" in indices_monthly.columns:
        print_subheader("LFI (Labor Fragility Index)")

        lfi = indices_monthly["LFI"].dropna()
        print(f"LFI data: {len(lfi)} months")

        for threshold in [0.5, 1.0]:
            result = validate_against_nber(
                lfi,
                threshold=threshold,
                threshold_direction="above",
                min_signal_months=2,
                max_lead_months=12,
                start_date="1970-01-01"
            )

            print(f"\nThreshold > {threshold}:")
            print(f"  Detection rate: {result.true_positive_rate*100:.1f}%")
            print(f"  Average lead time: {result.average_lead_time:.1f} months")
            print(f"  F1 score: {result.f1_score:.2f}")

    # LCI Validation
    if "LCI" in indices_monthly.columns:
        print_subheader("LCI (Liquidity Cushion Index)")

        lci = indices_monthly["LCI"].dropna()
        print(f"LCI data: {len(lci)} months")

        # For LCI, low values signal stress
        for threshold in [-0.5, -1.0]:
            result = validate_against_nber(
                lci,
                threshold=threshold,
                threshold_direction="below",
                min_signal_months=2,
                max_lead_months=6,
                start_date="1990-01-01"  # LCI data limited
            )

            print(f"\nThreshold < {threshold}:")
            print(f"  Detection rate: {result.true_positive_rate*100:.1f}%")
            print(f"  Average lead time: {result.average_lead_time:.1f} months")
            print(f"  F1 score: {result.f1_score:.2f}")

    # Yield Curve Validation
    if "Curve_10Y_2Y" in indices_monthly.columns:
        print_subheader("Yield Curve (10Y-2Y)")

        curve = indices_monthly["Curve_10Y_2Y"] if "Curve_10Y_2Y" in indices_monthly.columns else None

        if curve is None and "Curve_10Y_2Y_z" in indices_monthly.columns:
            # Use raw curve from horizon_dataset
            pass

    return results


def run_regime_statistics(indices: pd.DataFrame, df: pd.DataFrame) -> dict:
    """Compute statistics for each regime."""
    print_header("REGIME STATISTICS")

    results = {}
    indices_monthly = resample_to_monthly(indices)

    # MRI Regime Statistics
    if "MRI" in indices_monthly.columns:
        print_subheader("MRI Regimes")

        # Would need equity returns for full analysis
        # For now, just show time distribution
        mri = indices_monthly["MRI"].dropna()

        print(f"\nTime in each regime (since {mri.index.min().date()}):")
        for regime_name, (lower, upper) in MRI_REGIMES.items():
            if lower == -np.inf:
                mask = mri <= upper
            elif upper == np.inf:
                mask = mri > lower
            else:
                mask = (mri > lower) & (mri <= upper)

            pct = mask.sum() / len(mri) * 100
            print(f"  {regime_name:12}: {pct:5.1f}%")

        results["MRI_distribution"] = {
            regime: float(((mri > l) & (mri <= u)).sum() / len(mri))
            if l != -np.inf else float((mri <= u).sum() / len(mri))
            for regime, (l, u) in MRI_REGIMES.items()
        }

    return results


def generate_report(
    lead_lag_results: pd.DataFrame,
    weight_results: dict,
    regime_results: dict,
    output_path: Path
):
    """Generate HTML validation report."""
    print_header("GENERATING REPORT")

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Lighthouse Macro - Indicator Validation Report</title>
        <style>
            body {{ font-family: 'Inter', sans-serif; margin: 40px; background: #f5f5f5; }}
            h1 {{ color: #2389BB; }}
            h2 {{ color: #333; border-bottom: 2px solid #2389BB; padding-bottom: 5px; }}
            table {{ border-collapse: collapse; width: 100%; margin: 20px 0; background: white; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background: #2389BB; color: white; }}
            tr:nth-child(even) {{ background: #f9f9f9; }}
            .valid {{ color: #00BB89; font-weight: bold; }}
            .invalid {{ color: #FF6723; font-weight: bold; }}
            .metric {{ font-size: 24px; font-weight: bold; color: #2389BB; }}
            .card {{ background: white; padding: 20px; margin: 10px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        </style>
    </head>
    <body>
        <h1>LIGHTHOUSE MACRO - Indicator Validation Report</h1>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>

        <h2>Executive Summary</h2>
        <div class="card">
            <p class="metric">{lead_lag_results['valid'].sum()}/{len(lead_lag_results)}</p>
            <p>Lead-lag relationships validated</p>
        </div>

        <h2>Lead-Lag Validation</h2>
        <table>
            <tr>
                <th>Leading Indicator</th>
                <th>Lagging Indicator</th>
                <th>Expected Lag</th>
                <th>Optimal Lag</th>
                <th>Correlation</th>
                <th>Granger p-value</th>
                <th>Valid</th>
            </tr>
    """

    for _, row in lead_lag_results.iterrows():
        valid_class = "valid" if row["valid"] else "invalid"
        valid_text = "Yes" if row["valid"] else "No"
        corr = f"{row['correlation']:.3f}" if pd.notna(row['correlation']) else "N/A"
        granger = f"{row['granger_pvalue']:.4f}" if pd.notna(row['granger_pvalue']) else "N/A"

        html += f"""
            <tr>
                <td>{row['leading']}</td>
                <td>{row['lagging']}</td>
                <td>{row['expected_lag']}</td>
                <td>{row['optimal_lag']}</td>
                <td>{corr}</td>
                <td>{granger}</td>
                <td class="{valid_class}">{valid_text}</td>
            </tr>
        """

    html += """
        </table>

        <h2>Regime Validation vs NBER Recessions</h2>
    """

    if "MRI" in regime_results:
        mri = regime_results["MRI"]
        html += f"""
        <div class="card">
            <h3>MRI (Threshold > 1.0)</h3>
            <p>Detection Rate: <span class="metric">{mri['detection_rate']*100:.0f}%</span></p>
            <p>Average Lead Time: <span class="metric">{mri['avg_lead_time']:.1f}</span> months</p>
            <p>F1 Score: <span class="metric">{mri['f1']:.2f}</span></p>
        </div>
        """

    html += """
    </body>
    </html>
    """

    output_path.write_text(html)
    print(f"Report saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Lighthouse Macro Indicator Validation")
    parser.add_argument("--quick", action="store_true", help="Run quick validation only")
    parser.add_argument("--output", type=str, help="Output report path")
    parser.add_argument("--start-date", type=str, default="1970-01-01", help="Start date for analysis")

    args = parser.parse_args()

    print("=" * 70)
    print("  LIGHTHOUSE MACRO - INDICATOR VALIDATION")
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    # Load data
    print("\nLoading data...")
    df = load_horizon_dataset(start_date=args.start_date)
    print(f"Horizon dataset: {len(df)} rows, {len(df.columns)} columns")

    indices = load_lighthouse_indices(start_date=args.start_date)
    print(f"Lighthouse indices: {len(indices)} rows, {len(indices.columns)} columns")

    # Run validations
    lead_lag_results = run_lead_lag_validation(df)

    if not args.quick:
        weight_results = run_weight_validation(df, indices)
        regime_results = run_regime_validation(indices)
        regime_stats = run_regime_statistics(indices, df)
    else:
        weight_results = {}
        regime_results = {}
        regime_stats = {}

    # Generate report
    output_path = Path(args.output) if args.output else OUTPUT_DIR / "validation_report.html"
    generate_report(lead_lag_results, weight_results, regime_results, output_path)

    # Save raw results
    results_path = OUTPUT_DIR / "validation_results.json"
    with open(results_path, "w") as f:
        json.dump({
            "lead_lag": lead_lag_results.to_dict(),
            "weights": weight_results,
            "regime": regime_results,
            "regime_stats": regime_stats
        }, f, indent=2, default=str)
    print(f"Raw results saved to: {results_path}")

    print("\n" + "=" * 70)
    print("  VALIDATION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
