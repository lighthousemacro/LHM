"""
LHM Tape Read — branded 3-panel technical chart for the Telegram bot.

Renders the LHM technical hierarchy as ONE branded PNG, in order:
  Panel 1  Price + 50d/200d SMA   (load-bearing: most height)
  Panel 2  Relative strength vs benchmark (QAI), 63d/252d SMAs, regime flag
  Panel 3  Absolute Z-RoC momentum, canonical bands (1.28/1.645/1.96), zero line

Imports the canonical template (lhm_chart_template.py) for all styling — never
re-implements brand rules. White theme. Public-voice source line.

    from lhm_tape_read import build_tape_read_chart
    png = build_tape_read_chart("NVDA", nvda_df, benchmark_df=qai_df)

ohlcv_df / benchmark_df: pandas DataFrame, DatetimeIndex, a close column
('close' or 'Close', case-insensitive). Full history in; stats computed on
full history, visible window defaults to ~1.5y.
"""
from __future__ import annotations

import os
import sys
from datetime import datetime
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # headless-safe
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lhm_chart_template as tpl  # noqa: E402

DEFAULT_OUT_DIR = Path("/Users/bob/LHM/Outputs/lhmbot")
VISIBLE_DAYS = 378  # ~1.5y trading days shown; stats use full history
CANON_BANDS = [1.28, 1.645, 1.96]


def compute_z_roc(price: pd.Series, window: int = 63, lookback: int = 252) -> pd.Series:
    """Z-scored rate of change. Mirrors structure_edu_charts.compute_z_roc."""
    roc = price.pct_change(window) * 100
    z = (roc - roc.rolling(lookback).mean()) / roc.rolling(lookback).std()
    return z.dropna()


def _close(df: pd.DataFrame) -> pd.Series:
    for col in df.columns:
        if str(col).lower() == "close":
            s = df[col].astype(float).copy()
            s.index = pd.to_datetime(df.index)
            return s.sort_index().dropna()
    raise ValueError("ohlcv_df needs a 'close'/'Close' column")


def _rs_regime(rs_last, rs63_last, rs252_last) -> tuple[str, str]:
    """(label, color_key) for the relative-strength regime vs benchmark."""
    if rs_last > rs63_last and rs_last > rs252_last:
        return "LEADING", "starboard"
    if rs_last < rs63_last and rs_last < rs252_last:
        return "LAGGING", "port"
    return "MIXED", "doldrums"


def build_tape_read_chart(symbol: str, ohlcv_df: pd.DataFrame,
                          benchmark_df: pd.DataFrame | None = None,
                          benchmark_name: str = "QAI",
                          out_path: str | Path | None = None) -> str:
    import matplotlib.pyplot as plt

    price = _close(ohlcv_df)
    if len(price) < 60:
        raise ValueError(f"{symbol}: need >=60 closes, got {len(price)}")

    sma50 = price.rolling(50).mean()
    sma200 = price.rolling(200).mean()
    z = compute_z_roc(price)

    # Relative strength (only if a real benchmark is supplied — never fabricate)
    rs = rs63 = rs252 = None
    rs_label = "n/a"
    if benchmark_df is not None:
        bench = _close(benchmark_df)
        common = price.index.intersection(bench.index)
        if len(common) >= 252:
            rs = (price.loc[common] / bench.loc[common]) * 100.0
            rs63 = rs.rolling(63).mean()
            rs252 = rs.rolling(252).mean()

    # Visible window — last ~1.5y, stats already computed on full history.
    vis = price.index[-VISIBLE_DAYS:] if len(price) > VISIBLE_DAYS else price.index
    vstart = vis[0]

    def w(s):
        return None if s is None else s[s.index >= vstart]

    p_v, s50_v, s200_v, z_v = w(price), w(sma50), w(sma200), w(z)
    rs_v, rs63_v, rs252_v = w(rs), w(rs63), w(rs252)

    # ---- one-line read for the subtitle ----
    last_p = float(price.iloc[-1])
    above200 = (not pd.isna(sma200.iloc[-1])) and last_p >= sma200.iloc[-1]
    above50 = (not pd.isna(sma50.iloc[-1])) and last_p >= sma50.iloc[-1]
    trend_txt = ("above 50d & 200d" if above200 and above50
                 else "below 200d" if not above200
                 else "below 50d, above 200d")
    z_last = float(z.iloc[-1]) if len(z) else float("nan")
    z_txt = "Z-RoC broken (<-1.0)" if z_last < -1.0 else f"Z-RoC {z_last:+.1f}"
    if rs is not None:
        rs_label, _ = _rs_regime(float(rs.iloc[-1]), float(rs63.iloc[-1]),
                                 float(rs252.iloc[-1]))
        rs_txt = f"RS {rs_label.lower()} vs {benchmark_name}"
    else:
        rs_txt = f"RS vs {benchmark_name} n/a"
    subtitle = f"{trend_txt} · {rs_txt} · {z_txt}"

    # ---- figure ----
    tpl.set_theme("white")
    C = tpl.COLORS
    bg = tpl.THEME["bg"]
    fig, axes = plt.subplots(3, 1, figsize=(14, 12), sharex=True,
                             gridspec_kw={"height_ratios": [2.5, 1, 1]})
    fig.patch.set_facecolor(bg)
    for ax in axes:
        ax.set_facecolor(bg)
    fig.subplots_adjust(top=0.84, bottom=0.10, left=0.06, right=0.94, hspace=0.16)
    ax1, ax2, ax3 = axes

    # Panel 1: price + MAs
    ax1.plot(p_v.index, p_v.values, color=C["ocean"], lw=1.8, label=symbol, zorder=5)
    ax1.plot(s200_v.index, s200_v.values, color=C["deep"], lw=1.6, label="200d", zorder=4)
    ax1.plot(s50_v.index, s50_v.values, color=C["sky"], lw=1.2, label="50d", zorder=3)
    tpl.style_single_ax(ax1, fmt="{:.0f}")
    tpl.add_last_value_label(ax1, p_v, C["ocean"], fmt="{:.0f}")
    tpl.add_smart_legend(ax1, prefer="top-left")

    # Panel 2: relative strength
    if rs_v is not None:
        _, ckey = _rs_regime(float(rs.iloc[-1]), float(rs63.iloc[-1]),
                             float(rs252.iloc[-1]))
        ax2.plot(rs_v.index, rs_v.values, color=C["ocean"], lw=1.6,
                 label=f"RS vs {benchmark_name}")
        ax2.plot(rs63_v.index, rs63_v.values, color=C["dusk"], lw=1.1, label="63d")
        ax2.plot(rs252_v.index, rs252_v.values, color=C["doldrums"], lw=1.1, label="252d")
        tpl.style_single_ax(ax2, fmt="{:.1f}")
        tpl.add_last_value_label(ax2, rs_v, C[ckey], fmt="{:.1f}")
        tpl.add_smart_legend(ax2, prefer="top-left")
    else:
        tpl.style_single_ax(ax2, fmt="{:.1f}")
        ax2.text(0.5, 0.5, f"Relative strength vs {benchmark_name} unavailable "
                 f"(no benchmark data)", transform=ax2.transAxes,
                 ha="center", va="center", color=C["doldrums"], style="italic",
                 fontsize=11)

    # Panel 3: Z-RoC with canonical bands + zero line
    ax3.axhline(0, color=C["fog"], lw=1.0, ls="--", zorder=1)
    band_colors = {1.28: C["sky"], 1.645: C["sea"], 1.96: C["venus"]}
    for b in CANON_BANDS:
        for sgn in (1, -1):
            ax3.axhline(sgn * b, color=band_colors[b], lw=0.8, ls=":", alpha=0.85,
                        zorder=1)
    z_color = C["venus"] if z_last < -1.0 else C["ocean"]
    ax3.plot(z_v.index, z_v.values, color=z_color, lw=1.6, zorder=5)
    tpl.style_single_ax(ax3, fmt="{:.1f}")
    tpl.add_last_value_label(ax3, z_v, z_color, fmt="{:+.1f}")

    tpl.set_xlim_to_data(ax3, p_v.index)

    tpl.brand_fig(fig, title=symbol, subtitle=subtitle,
                  source="Price, relative strength & momentum",
                  data_date=price.index[-1])

    out_path = Path(out_path) if out_path else (
        DEFAULT_OUT_DIR / f"tape_read_{symbol.replace(':', '_')}.png")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    return tpl.save_fig(fig, str(out_path))


if __name__ == "__main__":
    # Smoke test with REAL data (yfinance). No synthetic data.
    import yfinance as yf
    sym = sys.argv[1] if len(sys.argv) > 1 else "NVDA"
    px = yf.download(sym, period="3y", interval="1d", progress=False, auto_adjust=True)
    bx = yf.download("QAI", period="3y", interval="1d", progress=False, auto_adjust=True)
    if isinstance(px.columns, pd.MultiIndex):
        px.columns = [c[0] for c in px.columns]
    if isinstance(bx.columns, pd.MultiIndex):
        bx.columns = [c[0] for c in bx.columns]
    out = build_tape_read_chart(
        sym, px, benchmark_df=bx,
        out_path=str(DEFAULT_OUT_DIR / "tape_read_smoketest.png"))
    print("WROTE", out, os.path.getsize(out), "bytes")
