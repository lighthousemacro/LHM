#!/usr/bin/env python3
"""Shared chart constructors for the pillar pages. Mirrors build_pillar_labor.py patterns."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from terminal_theme import (  # noqa: E402
    DUSK, OCEAN, SEA, SKY, VENUS, DARK_MUTED, DOLDRUMS, FOG,
    add_recessions, chart_card, dark_fig, latest, legend, load_index, load_obs,
    pill, render_page, section, set_xlim, sigma_refs, style_ax, threshold_callout,
    tile, to_b64, verdict_block, write_page, yoy, zero_line,
)

SERIES_COLORS = [SKY, DUSK, SEA, VENUS]


def band_state(z: float, hi_label: str = "ABOVE TREND", lo_label: str = "BELOW TREND",
               mid_label: str = "NEUTRAL") -> tuple[str, str]:
    if z > 0.5:
        return hi_label, DUSK
    if z < -0.5:
        return lo_label, SKY
    return mid_label, OCEAN


def hline(ax, y: float, label: str, color=VENUS, ls="--", lw=1.0, va="bottom", dy=0.0):
    """Threshold line. Label renders as a banded box-and-arrow callout, never on
    the line itself (Bob 7/20). va/dy kept for signature compatibility, unused."""
    ax.axhline(y, color=color, linewidth=lw, alpha=0.75, linestyle=ls)
    if label:
        threshold_callout(ax, label, y, color)


def chart_composite(index_id: str, display: str, thresholds: list[tuple] | None = None,
                    window: int = 21):
    """Composite: one clean smoothed line, no raw daily artifact. We smooth the
    already-computed z-score for display (21d = house standard); we never recompute
    the z-score on smoothed data. Pass a larger window for noisier composites.
    Returns (b64, smooth)."""
    s = load_index(index_id)
    smooth = s.rolling(window).mean().dropna()
    start = smooth.index.min()
    fig, ax = dark_fig()
    add_recessions(ax, start)
    zero_line(ax)
    sigma_refs(ax)
    ax.plot(smooth.index, smooth.values, color=SKY, linewidth=2.0,
            label=f"{display} ({smooth.iloc[-1]:+.2f})")
    for th in (thresholds or []):
        hline(ax, *th)
    style_ax(ax)
    set_xlim(ax, start, smooth.index.max())
    v, d = latest(smooth)
    pill(ax, d, v, f"{v:+.2f}", SKY)
    legend(ax, loc="upper left")
    return to_b64(fig), smooth


def chart_composite_monthly(index_id: str, display: str, thresholds: list[tuple] | None = None):
    """Composite stored as a monthly step forward-filled to daily rows.

    Collapses to the true monthly prints and plots one honest line: no gray
    daily artifact, no 21d average (which would equal the raw forward-fill).
    Returns (b64, monthly series).
    """
    s = load_index(index_id).resample("MS").first().dropna()
    start = s.index.min()
    fig, ax = dark_fig()
    add_recessions(ax, start)
    zero_line(ax)
    sigma_refs(ax)
    ax.plot(s.index, s.values, color=SKY, linewidth=2.0,
            label=f"{display} monthly ({s.iloc[-1]:+.2f})")
    for th in (thresholds or []):
        hline(ax, *th)
    style_ax(ax)
    set_xlim(ax, start, s.index.max())
    v, d = latest(s)
    pill(ax, d, v, f"{v:+.2f}", SKY)
    legend(ax, loc="upper left")
    return to_b64(fig), s


def chart_lines(series: list[tuple[pd.Series, str]], thresholds: list[tuple] | None = None,
                zero: bool = False, start: pd.Timestamp | None = None,
                fmt: str = "{:+.1f}", pill_series: int = 0, legend_loc: str = "upper left"):
    """Overlay 1-3 lines. series = [(pd.Series, label), ...]. Returns (b64, first series)."""
    s0 = series[0][0]
    data_start = min(s.index.min() for s, _ in series)
    start = max(start, data_start) if start is not None else data_start
    fig, ax = dark_fig()
    add_recessions(ax, start)
    if zero:
        zero_line(ax)
    for i, (s, label) in enumerate(series):
        sw = s[s.index >= start]
        ax.plot(sw.index, sw.values, color=SERIES_COLORS[i % len(SERIES_COLORS)],
                linewidth=2.0 if i == 0 else 1.6,
                label=f"{label} ({fmt.format(sw.iloc[-1])})")
    for th in (thresholds or []):
        hline(ax, *th)
    style_ax(ax)
    end = max(s.index.max() for s, _ in series)
    set_xlim(ax, start, end)
    ps = series[pill_series][0]
    v, d = latest(ps)
    pill(ax, d, v, fmt.format(v), SERIES_COLORS[pill_series % len(SERIES_COLORS)])
    legend(ax, loc=legend_loc)
    return to_b64(fig), s0


# Nowcast wiring. Units confirmed in Scripts/data_pipeline/nowcast_model.py TARGETS
# (lines 26-37): every LHM_*_NOWCAST is the TRANSFORMED read and every transform is
# "yoy", so all four values below are YoY percents. LHM_*_FITTED is the full fitted
# history at target frequency (write block, lines 106-123). R-squared figures are the
# canon out-of-sample numbers and the only ones citable. LHM_INFLATION_NOWCAST is a
# dead model and is banned from every page.
NOWCASTS = {
    "GDP": dict(nowcast="LHM_GDP_NOWCAST", fitted="LHM_GDP_FITTED", target="GDPC1",
                label="Real GDP YoY", r2="0.71"),
    "LABOR": dict(nowcast="LHM_LABOR_NOWCAST", fitted="LHM_LABOR_FITTED", target="PAYEMS",
                  label="Payrolls YoY", r2="0.71"),
    "HOUSING": dict(nowcast="LHM_HOUSING_NOWCAST", fitted="LHM_HOUSING_FITTED", target="CSUSHPINSA",
                    label="Case-Shiller YoY", r2="0.89"),
    "INDPRO": dict(nowcast="LHM_INDPRO_NOWCAST", fitted="LHM_INDPRO_FITTED", target="INDPRO",
                   label="Industrial Production YoY", r2="0.61"),
}


def chart_nowcast(key: str, legend_loc: str = "upper left"):
    """Nowcast vs realized chart. Returns (b64, live_value, live_date).

    Solid Dusk = the realized target print. Dashed Sky = the model: full fitted
    history plus the live daily nowcast tail. Window starts where the model
    history starts, which is the span where the relationship exists.
    """
    cfg = NOWCASTS[key]
    realized = yoy(load_obs(cfg["target"])).dropna()
    fitted = load_obs(cfg["fitted"]).dropna()
    live = load_obs(cfg["nowcast"]).dropna()
    model = pd.concat([fitted, live]).sort_index()
    model = model[~model.index.duplicated(keep="last")]
    start = fitted.index.min()
    fig, ax = dark_fig()
    add_recessions(ax, start)
    zero_line(ax)
    rw = realized[realized.index >= start]
    ax.plot(rw.index, rw.values, color=DUSK, linewidth=2.0,
            label=f"{cfg['label']} realized ({rw.iloc[-1]:+.1f}%)")
    ax.plot(model.index, model.values, color=SKY, linewidth=1.8, linestyle="--",
            label=f"LHM nowcast ({model.iloc[-1]:+.1f}%)")
    style_ax(ax)
    set_xlim(ax, start, max(model.index.max(), rw.index.max()))
    v, d = latest(model)
    pill(ax, d, v, f"{v:+.1f}%", SKY)
    legend(ax, loc=legend_loc)
    return to_b64(fig), float(live.iloc[-1]), live.index.max()


def nowcast_tile(key: str, tile_label: str, extra_sub: str = "") -> str:
    """Standard nowcast tile. R-squared cited first per house rule."""
    cfg = NOWCASTS[key]
    live = load_obs(cfg["nowcast"]).dropna()
    v = float(live.iloc[-1])
    sub = f"OOS R² {cfg['r2']}. {cfg['label']}, live daily read{extra_sub}"
    return tile(tile_label, f"{v:+.1f}", "%", sub, "MODEL", "st-flat", SKY)


def assemble(*, slug: str, filename: str, h1: str, subtitle: str, pillar_no: int,
             verdict_label: str, state: str, state_color: str, verdict_text: str,
             tiles_html: str, read_title: str, read_text: str, charts_html: str,
             wwcm: str, sources: str, datathru: str):
    body = (
        verdict_block(verdict_label, state, verdict_text, state_color)
        + f'<div class="tiles">{tiles_html}</div>'
        + section(read_title, read_text)
        + f'<div class="charts">{charts_html}</div>'
        + section("What Would Change Our Mind", wwcm)
    )
    html = render_page(
        title=f"{h1.title()} | Pillar {pillar_no}", h1=h1, subtitle=subtitle,
        active=slug, body=body, sources=sources, datathru=datathru,
    )
    out = write_page(filename, html)
    print(f"Wrote {out} ({out.stat().st_size:,} bytes)")
