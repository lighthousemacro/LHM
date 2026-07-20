#!/usr/bin/env python3
"""Pharos — 18 Sentiment, Pillar 12. All values computed live from the DB."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pillar_common import (  # noqa: E402
    DUSK, OCEAN, SEA, SKY, VENUS,
    assemble, chart_card, chart_composite, chart_lines, latest, load_obs, tile,
)


def regime(z: float) -> tuple[str, str]:
    if z > 1.5:
        return "EUPHORIC, FADE", VENUS
    if z < -1.0:
        return "CAPITULATION, FADE", SEA
    return "UNREMARKABLE", OCEAN


def build():
    spi_b64, spi = chart_composite(
        "SPI", "SPI",
        thresholds=[
            (1.5, "+1.5 FADE", VENUS, "--", 1.0),
            (-1.0, "-1.0 FADE", SEA, "--", 1.0, "top", -0.06),
        ],
    )
    spread = load_obs("AAII_Bull_Bear_Spread")
    spread_b64, _ = chart_lines(
        [(spread, "AAII bull-bear spread")],
        thresholds=[(30, "+30 EUPHORIA", VENUS, "--", 1.0), (-20, "-20 CAPITULATION", SEA, "--", 1.0, "top", -1.5)],
        zero=True, fmt="{:+.0f}", legend_loc="lower left",
    )
    bulls = load_obs("AAII_Bullish")
    bears = load_obs("AAII_Bearish")
    bb_b64, _ = chart_lines(
        [(bulls, "Bulls %"), (bears, "Bears %")],
        fmt="{:.0f}", legend_loc="upper left",
    )

    spi_v = float(spi.iloc[-1])
    state, color = regime(spi_v)
    sp_v, sp_d = latest(spread)
    bu_v, _ = latest(bulls)
    be_v, _ = latest(bears)

    verdict_text = (
        f"SPI 21d average at {spi_v:+.2f} against the +1.5 and -1.0 fade lines. "
        f"AAII spread at {sp_v:+.0f} against the +30 and -20 extremes. Sentiment is "
        f"contrarian at extremes only. Between the lines it is weather, not signal."
    )

    tiles = "".join([
        tile("Sentiment Tide", f"{spi_v:+.2f}", "", "SPI, 21d avg z. Fade past +1.5 / -1.0",
             state, "st-warn" if "FADE" in state else "st-flat", SKY),
        tile("AAII Spread", f"{sp_v:+.0f}", "", f"{sp_d.strftime('%b %d')}. Extremes: +30 / -20",
             "EXTREME" if sp_v > 30 or sp_v < -20 else "MID-RANGE",
             "st-warn" if sp_v > 30 or sp_v < -20 else "st-flat", DUSK),
        tile("AAII Bulls", f"{bu_v:.0f}", "%", "Weekly survey",
             "LEVEL", "st-flat", SEA),
        tile("AAII Bears", f"{be_v:.0f}", "%", "Weekly survey",
             "LEVEL", "st-flat", VENUS),
    ])

    charts = "".join([
        chart_card("Sentiment Tide Index", "The composite positioning read. Contrarian at "
                   "extremes only. Daily in gray, 21d average carries the read.", spi_b64),
        chart_card("The Crowd", "AAII bull-bear spread with the +30 euphoria and -20 "
                   "capitulation extremes marked.", spread_b64),
        chart_card("Bulls and Bears", "The raw survey lines. The spread carries the "
                   "signal, the components carry the texture.", bb_b64),
    ])

    wwcm = (
        "SPI 21d average breaching +1.5 or -1.0, which flips this pillar from weather "
        "to signal. An AAII print past the +30 or -20 extreme in the same week would "
        "confirm it."
    )

    assemble(
        slug="sentiment", filename="pillar_12_sentiment.html", h1="SENTIMENT", pillar_no=12,
        subtitle="Pillar 12. Contrarian at extremes only. Days-to-weeks signal.",
        verdict_label="Sentiment Regime", state=state, state_color=color,
        verdict_text=verdict_text, tiles_html=tiles,
        read_title="The Read",
        read_text=(
            f"The tide composite reads {spi_v:+.2f}. Between the fade lines this pillar is "
            f"context. Past them it is one of the few signals that works in days rather "
            f"than months. Everything on this page recomputes from the master database each build."),
        charts_html=charts, wwcm=wwcm,
        sources="Lighthouse Macro composites; AAII",
        datathru=sp_d.strftime("%Y-%m-%d"),
    )


if __name__ == "__main__":
    build()
