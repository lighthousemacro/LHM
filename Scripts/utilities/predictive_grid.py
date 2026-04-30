"""
Predictive grid: each pillar's optimized composite tested against a
standardized menu of asset-class targets at short, medium, and long horizons.

Same composite, same z-score methodology, same asset universe — so the resulting
matrix is comparable across pillars and tells us "which pillar predicts what."

Output: markdown matrix + per-pillar / per-asset detail.
"""

import json
import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

DB = Path("/Users/bob/LHM/Data/databases/Lighthouse_Master.db")
OPT_JSON = Path("/Users/bob/LHM/Outputs/mri_optimization/pillar_multiasset_optimization.json")
OUT_DIR = Path("/Users/bob/LHM/Outputs/mri_optimization/predictive")
OUT_DIR.mkdir(exist_ok=True)
OUT_MD = OUT_DIR / "PILLAR_PREDICTIVE_GRID.md"

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

# Standardized asset menu. Each entry: (label, series_id_a, series_id_b_or_None, mode, horizons_list)
# mode: "log_return" (single asset), "delta" (single asset), "max_widening" (single asset),
#       "spread_log_return" (a/b), "spread_delta" (a-b)
ASSET_MENU = [
    ("SPX 21d",    "SPX_Close",      None, "log_return",   21),
    ("SPX 63d",    "SPX_Close",      None, "log_return",   63),
    ("SPX 252d",   "SPX_Close",      None, "log_return",   252),
    ("VIX 21d",    "VIXCLS",         None, "log_return",   21),
    ("VIX 63d",    "VIXCLS",         None, "log_return",   63),
    ("DGS2 63d",   "DGS2",           None, "delta",        63),
    ("DGS2 252d",  "DGS2",           None, "delta",        252),
    ("DGS10 63d",  "DGS10",          None, "delta",        63),
    ("DGS10 252d", "DGS10",          None, "delta",        252),
    ("T10Y2Y 63d", "T10Y2Y",         None, "delta",        63),
    ("T10Y2Y 252d","T10Y2Y",         None, "delta",        252),
    ("HY OAS 63d", "BAMLH0A0HYM2",   None, "max_widening", 63),
    ("HY OAS 126d","BAMLH0A0HYM2",   None, "max_widening", 126),
    ("IG OAS 63d", "BAMLC0A0CM",     None, "max_widening", 63),
    ("IG OAS 126d","BAMLC0A0CM",     None, "max_widening", 126),
    ("DXY 63d",    "DTWEXBGS",       None, "log_return",   63),
    ("DXY 252d",   "DTWEXBGS",       None, "log_return",   252),
    ("USDJPY 252d","DEXJPUS",        None, "log_return",   252),
    ("HY-IG 63d",  "BAMLH0A0HYM2",   "BAMLC0A0CM", "spread_max_widening", 63),
    ("HYG/LQD 63d","HYG_Close",      "LQD_Close",  "spread_log_return",   63),
    ("SPY/TLT 63d","SPY_Close",      "TLT_Close",  "spread_log_return",   63),
]


def load_series(series_id: str) -> pd.Series:
    conn = sqlite3.connect(DB)
    df = pd.read_sql_query(
        "SELECT date, value FROM observations WHERE series_id = ? ORDER BY date",
        conn, params=(series_id,),
    )
    conn.close()
    if df.empty:
        return pd.Series(dtype=float, name=series_id)
    df["date"] = pd.to_datetime(df["date"])
    s = df.set_index("date")["value"].dropna()
    s.name = series_id
    return s


def expanding_zscore(s: pd.Series, min_obs: int = 60) -> pd.Series:
    s = s.dropna()
    mu = s.expanding(min_periods=min_obs).mean()
    sd = s.expanding(min_periods=min_obs).std()
    return ((s - mu) / sd).dropna()


def build_composite_daily(weights: dict[str, float]) -> pd.Series:
    """Build composite at daily frequency by ffill-ing lower-frequency components."""
    series_data = {}
    for sid in weights:
        s = load_series(sid)
        if s.empty:
            continue
        # Resample to daily and forward-fill (lower-freq carries forward)
        s_d = s.resample("D").ffill()
        series_data[sid] = s_d

    if not series_data:
        return pd.Series(dtype=float)

    df = pd.DataFrame(series_data)
    z = df.apply(expanding_zscore)

    weights_used = {k: v for k, v in weights.items() if k in z.columns}
    total_weight = sum(weights_used.values())
    composite = pd.Series(0.0, index=z.index)
    for sid, w in weights_used.items():
        composite = composite.add(z[sid] * (w / total_weight), fill_value=0)

    composite = composite.where(z.notna().any(axis=1)).dropna()
    return composite


def build_target(label: str, sid_a: str, sid_b: str | None,
                 mode: str, horizon: int) -> pd.Series:
    """Build a forward-looking target series at daily frequency."""
    a = load_series(sid_a)
    if a.empty:
        return pd.Series(dtype=float, name=label)
    a = a.resample("D").ffill()

    if sid_b is not None:
        b = load_series(sid_b)
        if b.empty:
            return pd.Series(dtype=float, name=label)
        b = b.resample("D").ffill()

    if mode == "log_return":
        target = (np.log(a.shift(-horizon)) - np.log(a)).rename(label)
    elif mode == "delta":
        target = (a.shift(-horizon) - a).rename(label)
    elif mode == "max_widening":
        # Max increase in spread over the next `horizon` days
        future_max = a.shift(-1).rolling(horizon, min_periods=1).max().shift(-(horizon - 1))
        target = (future_max - a).rename(label)
    elif mode == "spread_log_return":
        log_a = np.log(a.shift(-horizon)) - np.log(a)
        log_b = np.log(b.shift(-horizon)) - np.log(b)
        target = (log_a - log_b).rename(label)
    elif mode == "spread_max_widening":
        spread = a - b
        future_max = spread.shift(-1).rolling(horizon, min_periods=1).max().shift(-(horizon - 1))
        target = (future_max - spread).rename(label)
    else:
        raise ValueError(f"unknown mode {mode}")

    return target.dropna()


def rank_ic(composite: pd.Series, target: pd.Series) -> tuple[float, int]:
    df = pd.concat([composite, target], axis=1, join="inner").dropna()
    if len(df) < 252:
        return float("nan"), len(df)
    rho, _ = spearmanr(df.iloc[:, 0].values, df.iloc[:, 1].values)
    return rho, len(df)


def cell_color_marker(ic: float) -> str:
    """Return a marker for the IC magnitude — used in markdown rendering."""
    if pd.isna(ic):
        return "-"
    abs_ic = abs(ic)
    sign = "+" if ic >= 0 else "-"
    if abs_ic >= 0.50:
        return f"**{sign}{abs_ic:.2f}**"
    if abs_ic >= 0.30:
        return f"`{sign}{abs_ic:.2f}`"
    if abs_ic >= 0.15:
        return f"{sign}{abs_ic:.2f}"
    return f"<sub>{sign}{abs_ic:.2f}</sub>"


def main():
    with open(OPT_JSON) as f:
        opt = json.load(f)

    # Build all target series upfront
    print("Building target series...")
    targets = {}
    for label, sid_a, sid_b, mode, horizon in ASSET_MENU:
        try:
            t = build_target(label, sid_a, sid_b, mode, horizon)
            if not t.empty:
                targets[label] = t
                print(f"  {label}: {len(t)} obs")
            else:
                print(f"  {label}: SKIP (empty)")
        except Exception as e:
            print(f"  {label}: ERROR {e}")

    # Build all composites
    print("\nBuilding pillar composites...")
    composites = {}
    for pillar_key in PILLAR_FULL:
        weights = opt["pillars"][pillar_key]["best_target"]["optimized_weights"]
        c = build_composite_daily(weights)
        if not c.empty:
            composites[pillar_key] = c
            print(f"  {pillar_key}: {len(c)} obs")

    # Compute IC matrix
    print("\nComputing IC matrix...")
    ic_matrix = {}
    n_matrix = {}
    for pillar_key, comp in composites.items():
        ic_matrix[pillar_key] = {}
        n_matrix[pillar_key] = {}
        for label, target in targets.items():
            ic, n = rank_ic(comp, target)
            ic_matrix[pillar_key][label] = ic
            n_matrix[pillar_key][label] = n

    # Build markdown output
    md = ["# Pillar Predictive Grid\n",
          "*Generated 2026-04-30. Forward rank IC of each pillar's composite (current optimized weights) against a standardized asset-class menu across horizons.*\n\n",
          "## How to read\n\n",
          "Each cell is the **forward rank information coefficient** (Spearman ρ) between the pillar composite (z-score sum, expanding-window) and a forward-looking asset-class target. Same composite weights for every column — what changes is the target.\n\n",
          "**Magnitude reading:**\n",
          "- **bold** = |IC| ≥ 0.50 (very strong, often publishable on its own)\n",
          "- `code` = 0.30 ≤ |IC| < 0.50 (strong)\n",
          "- plain = 0.15 ≤ |IC| < 0.30 (modest)\n",
          "- <sub>subscript</sub> = |IC| < 0.15 (weak/noise)\n\n",
          "Sign reading: positive IC means the pillar composite leads the target in the same direction (composite up → target up). Whether that's bullish or bearish depends on the asset.\n\n",
          "**Caveat:** these are IC values from the composite tuned for *one specific best_target* per pillar (in `pillar_multiasset_optimization.json`). They are a 'how does this pillar's already-optimized composite predict OTHER assets' read, not 'what is the maximum predictive power of this pillar against each target' (the latter would require per-target re-optimization).\n\n",
          "## IC matrix\n\n"]

    # Header row
    asset_labels = [m[0] for m in ASSET_MENU if m[0] in targets]
    header = "| Pillar | " + " | ".join(asset_labels) + " |\n"
    sep = "|---|" + "|".join(["---"] * len(asset_labels)) + "|\n"
    md.append(header)
    md.append(sep)

    for pillar_key, full_name in PILLAR_FULL.items():
        if pillar_key not in ic_matrix:
            continue
        row_cells = [f"**{full_name} ({pillar_key})**"]
        for label in asset_labels:
            ic = ic_matrix[pillar_key].get(label, float("nan"))
            row_cells.append(cell_color_marker(ic))
        md.append("| " + " | ".join(row_cells) + " |\n")
    md.append("\n")

    # Top-IC list per pillar
    md.append("## Strongest signal per pillar\n\n")
    md.append("| Pillar | Best target | IC | Direction | n |\n|---|---|---|---|---|\n")
    for pillar_key, full_name in PILLAR_FULL.items():
        if pillar_key not in ic_matrix:
            continue
        ranked = sorted(
            [(lbl, ic) for lbl, ic in ic_matrix[pillar_key].items() if not pd.isna(ic)],
            key=lambda x: -abs(x[1]),
        )
        if not ranked:
            continue
        best_lbl, best_ic = ranked[0]
        direction = "↑↑" if best_ic > 0 else "↓↑"
        md.append(
            f"| **{full_name} ({pillar_key})** | {best_lbl} | "
            f"{best_ic:+.3f} | {direction} | {n_matrix[pillar_key][best_lbl]} |\n"
        )
    md.append("\n")

    # Per-pillar full IC sorted
    md.append("## Per-pillar IC, sorted by magnitude\n\n")
    for pillar_key, full_name in PILLAR_FULL.items():
        if pillar_key not in ic_matrix:
            continue
        md.append(f"### {full_name} ({pillar_key})\n\n")
        ranked = sorted(
            [(lbl, ic) for lbl, ic in ic_matrix[pillar_key].items() if not pd.isna(ic)],
            key=lambda x: -abs(x[1]),
        )
        md.append("| Target | IC | n |\n|---|---|---|\n")
        for lbl, ic in ranked:
            md.append(f"| {lbl} | {cell_color_marker(ic)} | {n_matrix[pillar_key][lbl]} |\n")
        md.append("\n")

    OUT_MD.write_text("".join(md))
    print(f"\nWrote {OUT_MD}")

    # Print quick summary
    print("\nTop signal per pillar:")
    for pillar_key in PILLAR_FULL:
        if pillar_key not in ic_matrix:
            continue
        ranked = sorted(
            [(lbl, ic) for lbl, ic in ic_matrix[pillar_key].items() if not pd.isna(ic)],
            key=lambda x: -abs(x[1]),
        )
        if ranked:
            best_lbl, best_ic = ranked[0]
            print(f"  {pillar_key:>8}: {best_lbl:>15} {best_ic:+.3f}")


if __name__ == "__main__":
    main()
