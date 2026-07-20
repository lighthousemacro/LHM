"""
Lighthouse Macro brand layer for OpenBB Workspace chart widgets.

Chart endpoints return Plotly figure dicts built here, so every widget renders
in the 23/89/BB palette with house chart rules instead of OpenBB defaults.

House rules (Brand/chart-styling.md, adapted to the Workspace dark theme):
- No gridlines. All four spines visible, Doldrums, thin.
- Right axis primary.
- Zero line = Fog dashed. Z-score references at +/-2 sigma only.
- Trace cycle on dark canvas: Sky, Dusk, Sea, Venus, Ocean (Sky is the
  dark-theme primary per the brand guide).
- Fonts: Inter body, Montserrat titles.
"""

from __future__ import annotations

from typing import Any

# 23/89/BB palette
OCEAN = "#2389BB"
DUSK = "#FF6723"
SKY = "#89CCFF"
DEEP = "#123456"
SEA = "#00BB89"
VENUS = "#FF2389"
STARBOARD = "#238923"
PORT = "#892323"
DOLDRUMS = "#898989"
GLACIER = "#F4F7F9"
ICE = "#D4E2EF"
FOG = "#D1D1D1"
FOAM = "#FFFFFF"

# Dark-theme trace cycle: Sky leads on dark canvas
CYCLE_DARK = [SKY, DUSK, SEA, VENUS, OCEAN]

FONT_BODY = "Inter, sans-serif"
FONT_TITLE = "Montserrat, Inter, sans-serif"


def lhm_layout(
    title: str | None = None,
    y_title: str | None = None,
    show_legend: bool = False,
) -> dict[str, Any]:
    """Base Plotly layout implementing house style on the Workspace dark theme."""
    axis_common: dict[str, Any] = {
        "showgrid": False,
        "zeroline": False,
        "showline": True,
        "linecolor": DOLDRUMS,
        "linewidth": 1,
        "mirror": True,  # all four spines
        "ticks": "outside",
        "tickcolor": DOLDRUMS,
        "tickfont": {"family": FONT_BODY, "size": 11, "color": DOLDRUMS},
    }
    layout: dict[str, Any] = {
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "font": {"family": FONT_BODY, "size": 12, "color": ICE},
        "margin": {"l": 8, "r": 56, "t": 42 if title else 16, "b": 32},
        "xaxis": dict(axis_common),
        "yaxis": dict(axis_common, side="right", title=(
            {"text": y_title, "font": {"family": FONT_BODY, "size": 11, "color": DOLDRUMS}}
            if y_title else None
        )),
        "showlegend": show_legend,
        "hovermode": "x unified",
        "hoverlabel": {
            "bgcolor": DEEP,
            "bordercolor": OCEAN,
            "font": {"family": FONT_BODY, "size": 11, "color": FOAM},
        },
    }
    if title:
        layout["title"] = {
            "text": title,
            "font": {"family": FONT_TITLE, "size": 14, "color": ICE},
            "x": 0.01,
            "xanchor": "left",
        }
    if show_legend:
        layout["legend"] = {
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "left",
            "x": 0,
            "font": {"family": FONT_BODY, "size": 11, "color": ICE},
        }
    return layout


def _zero_line() -> dict[str, Any]:
    return {
        "type": "line",
        "xref": "paper",
        "x0": 0,
        "x1": 1,
        "yref": "y",
        "y0": 0,
        "y1": 0,
        "line": {"color": FOG, "width": 1, "dash": "dash"},
        "layer": "below",
    }


def _sigma_lines(sigma: float = 2.0) -> list[dict[str, Any]]:
    """+/- 2 sigma references only (house rule: never +/-1)."""
    out = []
    for y in (sigma, -sigma):
        out.append({
            "type": "line",
            "xref": "paper",
            "x0": 0,
            "x1": 1,
            "yref": "y",
            "y0": y,
            "y1": y,
            "line": {"color": DOLDRUMS, "width": 1, "dash": "dot"},
            "layer": "below",
        })
    return out


def _last_value_annotation(dates: list[str], values: list[float]) -> dict[str, Any]:
    """Latest-value pill, top-left, Dusk. The RHS pill equivalent for Workspace."""
    latest = values[-1]
    return {
        "xref": "paper",
        "yref": "paper",
        "x": 0.01,
        "y": 1.0,
        "xanchor": "left",
        "yanchor": "top",
        "text": f"<b>{latest:+.2f}</b>  ·  {dates[-1]}",
        "showarrow": False,
        "font": {"family": FONT_BODY, "size": 12, "color": DUSK},
        "bgcolor": "rgba(18,52,86,0.75)",  # Deep at 75%
        "bordercolor": DUSK,
        "borderwidth": 1,
        "borderpad": 4,
    }


def long_to_chart(
    rows: list[dict[str, Any]],
    y_title: str | None = None,
    order: list[str] | None = None,
    labels: dict[str, str] | None = None,
    zscore: bool = False,
) -> dict[str, Any]:
    """Brand a long-format payload [{date, series_id, value}] as a multi-line chart.

    order: optional series_id ordering for the color cycle (first = Sky).
    labels: optional series_id -> display-name mapping for the legend.
    Adds the Fog zero line automatically when values span zero.
    """
    seqs: dict[str, tuple[list[str], list[float]]] = {}
    for r in rows:
        if r.get("value") is None:
            continue
        sid = r["series_id"]
        if sid not in seqs:
            seqs[sid] = ([], [])
        seqs[sid][0].append(r["date"])
        seqs[sid][1].append(r["value"])
    sids = [s for s in (order or []) if s in seqs] + [s for s in seqs if s not in (order or [])]
    series = [
        {
            "name": (labels or {}).get(sid, sid),
            "dates": seqs[sid][0],
            "values": seqs[sid][1],
        }
        for sid in sids
    ]
    all_vals = [v for _, (_, vs) in seqs.items() for v in vs]
    spans_zero = bool(all_vals) and min(all_vals) < 0 < max(all_vals)
    fig = line_chart(
        dates=series[0]["dates"] if series else [],
        series=series,
        y_title=y_title,
        zscore=zscore,
        last_value_pill=len(series) == 1,
    )
    if spans_zero and not zscore:
        fig["layout"].setdefault("shapes", []).append(_zero_line())
    return fig


def line_chart(
    dates: list[str],
    series: list[dict[str, Any]],
    title: str | None = None,
    y_title: str | None = None,
    zscore: bool = False,
    last_value_pill: bool = True,
) -> dict[str, Any]:
    """Branded multi-line chart.

    series: [{"name": str, "values": [...], "color": optional hex}]
    zscore=True adds the 0 line (Fog dashed) and +/-2 sigma dotted references.
    """
    traces = []
    for i, s in enumerate(series):
        traces.append({
            "type": "scatter",
            "mode": "lines",
            "name": s["name"],
            "x": dates if "dates" not in s else s["dates"],
            "y": s["values"],
            "line": {"color": s.get("color") or CYCLE_DARK[i % len(CYCLE_DARK)], "width": 2},
            "hovertemplate": "%{y:.2f}<extra>" + s["name"] + "</extra>",
        })
    layout = lhm_layout(title=title, y_title=y_title, show_legend=len(series) > 1)
    shapes: list[dict[str, Any]] = []
    if zscore:
        shapes.append(_zero_line())
        shapes.extend(_sigma_lines())
    if shapes:
        layout["shapes"] = shapes
    if last_value_pill and series and series[0]["values"]:
        s0 = series[0]
        d0 = s0.get("dates", dates)
        layout["annotations"] = [_last_value_annotation(list(d0), list(s0["values"]))]
    return {"data": traces, "layout": layout}
