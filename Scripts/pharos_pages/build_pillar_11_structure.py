#!/usr/bin/env python3
"""Pharos — 17 Structure, Pillar 11. All values computed live from the DB."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pillar_common import (  # noqa: E402
    DUSK, OCEAN, SEA, SKY, VENUS,
    assemble, chart_card, chart_composite, chart_lines, hline, latest, load_obs, tile,
)


def regime(z: float) -> tuple[str, str]:
    if z < -1.0:
        return "BROKEN", VENUS
    if z < -0.5:
        return "WEAKENING", DUSK
    if z > 0.5:
        return "HEALTHY", SEA
    return "MIXED", OCEAN


def build():
    msi_b64, msi = chart_composite(
        "MSI", "MSI",
        thresholds=[(-1.0, "-1.0 BROKEN", VENUS, "--", 1.0, "top", -0.06)],
    )
    p50 = load_obs("SPX_PCT_ABOVE_50D")
    b50_b64, _ = chart_lines(
        [(p50, "% of S&P 500 above 50d MA")],
        thresholds=[(80, "80 CROWDED", DUSK, "--", 1.0), (25, "25 WASHED OUT", SEA, "--", 1.0)],
        fmt="{:.0f}%", legend_loc="lower left",
    )
    p200 = load_obs("SPX_PCT_ABOVE_200D")
    b200_b64, _ = chart_lines(
        [(p200, "% of S&P 500 above 200d MA")],
        fmt="{:.0f}%", legend_loc="lower left",
    )

    msi_v = float(msi.iloc[-1])
    state, color = regime(msi_v)
    p20 = load_obs("SPX_PCT_ABOVE_20D")
    p20_v, _ = latest(p20)
    p50_v, p50_d = latest(p50)
    p200_v, _ = latest(p200)

    verdict_text = (
        f"MSI 21d average at {msi_v:+.2f}. Breadth reads {p20_v:.0f}% above the 20d, "
        f"{p50_v:.0f}% above the 50d, {p200_v:.0f}% above the 200d. Breadth divergence "
        f"is distribution. Broken below -1.0 on the composite."
    )

    tiles = "".join([
        tile("Breadth Pulse", f"{msi_v:+.2f}", "", "MSI, 21d avg z. Broken below -1.0",
             state, "st-alert" if state == "BROKEN" else "st-warn" if state == "WEAKENING" else "st-ok" if state == "HEALTHY" else "st-flat", SKY),
        tile("% Above 20d", f"{p20_v:.0f}", "%", "Tactical breadth",
             "CROWDED" if p20_v > 80 else "WASHED OUT" if p20_v < 25 else "MID-RANGE",
             "st-warn" if p20_v > 80 or p20_v < 25 else "st-flat", DUSK),
        tile("% Above 50d", f"{p50_v:.0f}", "%", "Swing breadth. Bands: 25 / 80",
             "CROWDED" if p50_v > 80 else "WASHED OUT" if p50_v < 25 else "MID-RANGE",
             "st-warn" if p50_v > 80 or p50_v < 25 else "st-flat", SEA),
        tile("% Above 200d", f"{p200_v:.0f}", "%", "Primary trend participation",
             "NARROW" if p200_v < 50 else "BROAD", "st-warn" if p200_v < 50 else "st-flat", VENUS),
    ])

    charts = "".join([
        chart_card("Market Breadth Pulse", "The composite structure read. Divergence between "
                   "price and participation is distribution. Daily in gray, 21d average "
                   "carries the read.", msi_b64),
        chart_card("Swing Breadth", "Percent of S&P 500 members above their 50d average, "
                   "with the 25 washed-out and 80 crowded bands.", b50_b64),
        chart_card("Primary Trend Participation", "Percent above the 200d average. How much "
                   "of the tape is actually in an uptrend.", b200_b64),
    ])

    if state in ("BROKEN", "WEAKENING"):
        wwcm = (
            "A breadth thrust, 30 to 70 on the 20d measure inside ten sessions. "
            "MSI 21d average reclaiming zero. "
            "The 50d measure clearing the 80 crowded band on expanding participation."
        )
    elif state == "HEALTHY":
        wwcm = (
            "MSI 21d average breaking below -1.0. "
            "The 20d measure washing out below 25. "
            "Participation above the 200d narrowing below 50% while the index holds near highs."
        )
    else:
        wwcm = (
            "MSI 21d average breaking below -1.0, or clearing +0.5 with breadth confirming. "
            "The 20d measure tagging either the 25 washout or the 80 crowded band."
        )

    assemble(
        slug="structure", filename="pillar_11_structure.html", h1="STRUCTURE", pillar_no=11,
        subtitle="Pillar 11. Breadth divergence is distribution. Lead 2 to 4 months.",
        verdict_label="Structure Regime", state=state, state_color=color,
        verdict_text=verdict_text, tiles_html=tiles,
        read_title="The Read",
        read_text=(
            f"The pulse composite reads {msi_v:+.2f}. The 20d, 50d, and 200d breadth reads "
            f"are separate indicators at {p20_v:.0f}, {p50_v:.0f}, and {p200_v:.0f}. "
            f"Everything on this page recomputes from the master database each build."),
        charts_html=charts, wwcm=wwcm,
        sources="Lighthouse Macro composites and breadth engine",
        datathru=p50_d.strftime("%Y-%m-%d"),
    )


if __name__ == "__main__":
    build()
