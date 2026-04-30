"""
Descriptive analysis: for each of the 12 pillars, build the composite using the
optimized weights and ask three concurrent questions:

1. Tracking — how well does the composite track its claimed underlying?
2. Redundancy — does the composite add information over its single best component?
3. Structural — is the composite essentially one series in disguise?

Output: markdown report with per-pillar stats + chart per pillar.
"""

import json
import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

DB = Path("/Users/bob/LHM/Data/databases/Lighthouse_Master.db")
OPT_JSON = Path("/Users/bob/LHM/Outputs/mri_optimization/pillar_multiasset_optimization.json")
OUT_DIR = Path("/Users/bob/LHM/Outputs/mri_optimization/descriptive")
OUT_DIR.mkdir(exist_ok=True)
OUT_MD = OUT_DIR / "PILLAR_DESCRIPTIVE_ANALYSIS.md"

OCEAN = "#2389BB"
DUSK = "#FF6723"
DOLDRUMS = "#898989"
FOG = "#D1D1D1"

PILLAR_FULL = {
    "LPI": "Labor Pressure Index",
    "PCI": "Price Conditions Index",
    "GCI": "Growth Conditions Index",
    "HCI": "Housing Conditions Index",
    "CCI": "Consumer Conditions Index",
    "BCI": "Business Conditions Index",
    "TCI": "Trade Conditions Index",
    "GCI_Gov": "Government Conditions Index",
    "FCI": "Financial Conditions Index",
    "LCI": "Liquidity Cushion Index",
    "MSI": "Market Structure Index",
    "SPI": "Sentiment & Positioning Index",
}

# What each pillar CLAIMS to measure — the concurrent ground-truth series.
# Format: (series_id, transform, label)
GROUND_TRUTH = {
    "LPI": ("UNRATE", "level", "Unemployment Rate (U-3)"),
    "PCI": ("PCEPILFE", "yoy", "Core PCE YoY"),
    "GCI": ("CFNAIMA3", "level", "Chicago Fed National Activity (3M MA)"),
    "HCI": ("CSUSHPINSA", "yoy", "Case-Shiller Home Prices YoY"),
    "CCI": ("PCEC96", "yoy", "Real PCE YoY"),
    "BCI": ("ANDENO", "yoy", "Nondefense Capital Goods Orders YoY"),
    "TCI": ("DTWEXBGS", "yoy", "Trade-Weighted Dollar YoY"),
    "GCI_Gov": ("THREEFYTP10", "level", "10y Term Premium (ACM)"),
    "FCI": ("ANFCI", "level", "Chicago Fed Adjusted NFCI"),
    "LCI": ("TOTRESNS", "yoy", "Bank Reserves YoY"),
    "MSI": ("SPX_vs_200d_pct", "level", "S&P 500 % vs 200d MA"),
    "SPI": ("AAII_Bull_Bear_Spread", "level", "AAII Bull-Bear Spread"),
}


def load_series(series_id: str) -> pd.Series:
    conn = sqlite3.connect(DB)
    df = pd.read_sql_query(
        "SELECT date, value FROM observations WHERE series_id = ? ORDER BY date",
        conn, params=(series_id,),
    )
    conn.close()
    if df.empty:
        return pd.Series(dtype=float)
    df["date"] = pd.to_datetime(df["date"])
    return df.set_index("date")["value"].dropna()


def transform(s: pd.Series, mode: str) -> pd.Series:
    if mode == "level":
        return s
    if mode == "yoy":
        # YoY % change. Resample to monthly first if needed.
        s_m = s.resample("ME").last() if s.index.inferred_freq != "ME" else s
        return s_m.pct_change(12) * 100
    if mode == "delta":
        return s.diff()
    raise ValueError(f"unknown mode {mode}")


def expanding_zscore(s: pd.Series, min_obs: int = 60) -> pd.Series:
    """Expanding-window z-score with min observations to avoid early-history noise."""
    s = s.dropna()
    mu = s.expanding(min_periods=min_obs).mean()
    sd = s.expanding(min_periods=min_obs).std()
    return ((s - mu) / sd).dropna()


def build_composite(weights: dict[str, float]) -> pd.DataFrame:
    """Build a weighted-z-score composite from a dict of {series_id: weight}."""
    series_data = {}
    for sid in weights:
        s = load_series(sid)
        if s.empty:
            print(f"  WARN: {sid} not in DB")
            continue
        # Resample to monthly for cross-frequency alignment
        s_m = s.resample("ME").last()
        series_data[sid] = s_m

    if not series_data:
        return pd.DataFrame()

    df = pd.DataFrame(series_data)
    z = df.apply(expanding_zscore)

    # Weighted sum of z-scores
    composite = pd.Series(0.0, index=z.index)
    weights_used = {k: v for k, v in weights.items() if k in z.columns}
    total_weight = sum(weights_used.values())
    for sid, w in weights_used.items():
        composite = composite.add(z[sid] * (w / total_weight), fill_value=0)

    # Mask rows where we have no data
    mask = z.notna().any(axis=1)
    composite = composite[mask]

    return pd.DataFrame({
        "composite": composite,
        **{f"z_{sid}": z[sid] for sid in weights_used},
    })


def compute_stats(composite: pd.Series, reference: pd.Series, components: pd.DataFrame):
    """Compute concurrent tracking + redundancy stats."""
    # Align frequencies — both monthly
    df = pd.concat([composite, reference], axis=1, join="inner").dropna()
    df.columns = ["composite", "reference"]
    if len(df) < 24:
        return None

    pearson = df["composite"].corr(df["reference"])
    spearman = df["composite"].corr(df["reference"], method="spearman")

    # Single-best-component redundancy check
    # IMPORTANT: exclude the reference itself from this check if it happens to
    # also be in the component basket (circular comparison would yield ~1.0).
    ref_name = getattr(reference, "name", None)
    best_comp_corr = -1.0
    best_comp = None
    for col in components.columns:
        if col.startswith("z_"):
            sid = col[2:]
            if sid == ref_name:
                continue  # skip the reference itself
            comp = components[col]
            aligned = pd.concat([comp, reference], axis=1, join="inner").dropna()
            if len(aligned) < 24:
                continue
            c = abs(aligned.iloc[:, 0].corr(aligned.iloc[:, 1]))
            if c > best_comp_corr:
                best_comp_corr = c
                best_comp = sid

    # R² of composite predicting reference (concurrent OLS)
    x = df["composite"].values
    y = df["reference"].values
    x_mean = x.mean()
    y_mean = y.mean()
    beta = np.sum((x - x_mean) * (y - y_mean)) / np.sum((x - x_mean) ** 2)
    alpha = y_mean - beta * x_mean
    y_pred = alpha + beta * x
    ss_res = np.sum((y - y_pred) ** 2)
    ss_tot = np.sum((y - y_mean) ** 2)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else float("nan")

    return {
        "n_obs": len(df),
        "start": df.index.min().strftime("%Y-%m"),
        "end": df.index.max().strftime("%Y-%m"),
        "pearson": pearson,
        "spearman": spearman,
        "r2": r2,
        "beta": beta,
        "best_single_component": best_comp,
        "best_single_corr": best_comp_corr,
        "incremental_corr": abs(pearson) - best_comp_corr,
    }


def plot_pillar(pillar: str, full_name: str, composite: pd.Series,
                reference: pd.Series, ref_label: str, stats: dict):
    fig, ax1 = plt.subplots(figsize=(12, 5))

    # Both series scaled — composite on its own axis
    df = pd.concat([composite, reference], axis=1, join="inner").dropna()
    df.columns = ["composite", "reference"]

    ax1.plot(df.index, df["composite"], color=OCEAN, linewidth=2, label=f"{pillar} composite (z)")
    ax1.set_ylabel(f"{pillar} composite (z-score)", color=OCEAN, fontsize=10)
    ax1.tick_params(axis="y", labelcolor=OCEAN)
    ax1.axhline(0, color=FOG, linestyle="--", linewidth=0.8)

    ax2 = ax1.twinx()
    ax2.plot(df.index, df["reference"], color=DUSK, linewidth=2,
             label=ref_label, alpha=0.85)
    ax2.set_ylabel(ref_label, color=DUSK, fontsize=10)
    ax2.tick_params(axis="y", labelcolor=DUSK)

    for spine in ax1.spines.values():
        spine.set_color(DOLDRUMS)
        spine.set_linewidth(0.5)
    for spine in ax2.spines.values():
        spine.set_color(DOLDRUMS)
        spine.set_linewidth(0.5)
    ax1.grid(False)
    ax2.grid(False)

    title = f"{full_name} ({pillar}) vs {ref_label}"
    subtitle = (f"Pearson r = {stats['pearson']:+.2f}  |  "
                f"R² = {stats['r2']:.2f}  |  "
                f"Best single component: {stats['best_single_component']} "
                f"(|r| = {stats['best_single_corr']:.2f})  |  "
                f"Incremental |r|: {stats['incremental_corr']:+.2f}")
    ax1.set_title(f"{title}\n{subtitle}", fontsize=11, loc="left")

    ax1.xaxis.set_major_locator(mdates.YearLocator(5))
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left", fontsize=9,
               framealpha=0.9, edgecolor=DOLDRUMS)

    fig.text(0.99, 0.01, "MACRO, ILLUMINATED.", ha="right", va="bottom",
             fontsize=8, color=DOLDRUMS, alpha=0.6)

    plt.tight_layout()
    out_path = OUT_DIR / f"{pillar}_descriptive.png"
    plt.savefig(out_path, dpi=150, bbox_inches="tight",
                edgecolor=OCEAN, facecolor="white")
    plt.close()
    return out_path


def main():
    with open(OPT_JSON) as f:
        opt = json.load(f)

    md = ["# Pillar Descriptive Analysis\n",
          "*Generated 2026-04-30. Concurrent tracking, redundancy, and structural-validation stats per pillar.*\n\n",
          "## Methodology\n\n",
          "For each pillar, we build the composite using the **optimized weights** from `pillar_multiasset_optimization.json` (best_target weights). Each component is z-scored on an expanding window (60-month minimum) and combined as a weight-normalized sum. The composite is then compared **concurrently** (no lead-lag) against a 'ground truth' reference series — what the pillar claims to measure.\n\n",
          "Three questions per pillar:\n\n",
          "1. **Tracking** — Pearson and Spearman correlation between the composite and the reference. High = the composite represents what it claims to.\n",
          "2. **Redundancy** — correlation of each component (z-score) with the reference. If one single component already correlates as highly as the full composite, the other components aren't adding information.\n",
          "3. **Incremental signal** — composite |r| minus best-single-component |r|. Positive = the composite adds over its best constituent. Zero or negative = the composite *is* the best constituent in disguise.\n\n",
          "## Summary table\n\n",
          "| Pillar | Reference | n | Pearson | Spearman | R² | Best single | Best |r| | Incr |r| |\n",
          "|---|---|---|---|---|---|---|---|---|\n"]

    summary_lines = []
    pillar_details = []

    for pillar_key, full_name in PILLAR_FULL.items():
        pillar_data = opt["pillars"].get(pillar_key, {})
        if not pillar_data:
            continue
        weights = pillar_data["best_target"]["optimized_weights"]
        ref_id, ref_mode, ref_label = GROUND_TRUTH[pillar_key]

        print(f"Building {pillar_key} composite from {len(weights)} components...")
        comp_df = build_composite(weights)
        if comp_df.empty:
            print(f"  SKIP {pillar_key}: no data")
            continue

        ref_raw = load_series(ref_id)
        if ref_raw.empty:
            print(f"  SKIP {pillar_key}: reference {ref_id} not in DB")
            continue
        ref = transform(ref_raw, ref_mode)
        ref_m = ref.resample("ME").last() if hasattr(ref.index, "freq") else ref
        ref_m.name = ref_id  # tag so the redundancy check can exclude it

        composite = comp_df["composite"]
        stats = compute_stats(composite, ref_m, comp_df)
        if stats is None:
            print(f"  SKIP {pillar_key}: insufficient overlap")
            continue

        chart_path = plot_pillar(pillar_key, full_name, composite, ref_m, ref_label, stats)
        print(f"  -> {chart_path.name}, pearson={stats['pearson']:+.2f}, "
              f"best_single={stats['best_single_component']} ({stats['best_single_corr']:.2f}), "
              f"incr={stats['incremental_corr']:+.2f}")

        summary_lines.append(
            f"| **{full_name} ({pillar_key})** | {ref_label} | {stats['n_obs']} | "
            f"{stats['pearson']:+.2f} | {stats['spearman']:+.2f} | {stats['r2']:.2f} | "
            f"{stats['best_single_component']} | {stats['best_single_corr']:.2f} | "
            f"{stats['incremental_corr']:+.2f} |\n"
        )

        pillar_details.append({
            "key": pillar_key,
            "name": full_name,
            "stats": stats,
            "ref_label": ref_label,
            "weights": weights,
            "chart": chart_path.name,
        })

    md.extend(summary_lines)
    md.append("\n")

    md.append("\n## Per-pillar detail\n\n")
    for d in pillar_details:
        s = d["stats"]
        md.append(f"### {d['name']} ({d['key']})\n\n")
        md.append(f"![chart]({d['chart']})\n\n")
        md.append(f"- **Reference (ground truth):** {d['ref_label']}\n")
        md.append(f"- **Window:** {s['start']} to {s['end']} ({s['n_obs']} months)\n")
        md.append(f"- **Composite Pearson r:** {s['pearson']:+.3f}\n")
        md.append(f"- **Composite Spearman ρ:** {s['spearman']:+.3f}\n")
        md.append(f"- **R² (concurrent OLS):** {s['r2']:.3f}\n")
        md.append(f"- **Best single component:** `{s['best_single_component']}` (|r| = {s['best_single_corr']:.2f})\n")
        md.append(f"- **Incremental |r| (composite over best single):** {s['incremental_corr']:+.3f}\n\n")
        md.append(f"**Components and weights (optimized):**\n\n")
        md.append("| series_id | weight |\n|---|---|\n")
        for sid, w in sorted(d["weights"].items(), key=lambda x: -x[1]):
            md.append(f"| `{sid}` | {w:.3f} |\n")
        md.append("\n")

        # Interpretation
        incr = s["incremental_corr"]
        if incr < -0.05:
            verdict = "**Verdict: REDUNDANT.** The composite tracks the reference *worse* than its best single component. The composite is destroying signal."
        elif incr < 0.05:
            verdict = "**Verdict: PROXY.** The composite is essentially its best single component in disguise. The other components aren't adding tracking power."
        elif incr < 0.15:
            verdict = "**Verdict: MARGINAL ADDITION.** The composite adds modestly over the best single component. Worth keeping but the case for the basket structure isn't strong."
        else:
            verdict = "**Verdict: REAL COMPOSITE.** The composite adds meaningfully over any single component. The basket structure earns its keep."
        md.append(f"{verdict}\n\n")

    OUT_MD.write_text("".join(md))
    print(f"\nWrote {OUT_MD}")
    print("\nDone.")


if __name__ == "__main__":
    main()
