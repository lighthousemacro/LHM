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
    # SPI is fear-up as computed: +1.5 = capitulation washout (contrarian
    # buy), -1.0 = euphoric crowd (contrarian sell).
    if z > 1.5:
        return "CAPITULATION, FADE", SEA
    if z < -1.0:
        return "EUPHORIC, FADE", VENUS
    return "UNREMARKABLE", OCEAN


def build():
    spi_b64, spi = chart_composite(
        "SPI", "SPI",
        thresholds=[
            (1.5, "+1.5 CAPITULATION, FADE", SEA, "--", 1.0),
            (-1.0, "-1.0 EUPHORIA, FADE", VENUS, "--", 1.0, "top", -0.06),
        ],
    )
    # AAII stored as decimal fractions in the DB; display in percent
    spread = load_obs("AAII_Bull_Bear_Spread") * 100.0
    spread_b64, _ = chart_lines(
        [(spread, "AAII bull-bear spread")],
        thresholds=[(30, "+30 EUPHORIA", VENUS, "--", 1.0), (-20, "-20 CAPITULATION", SEA, "--", 1.0, "top", -1.5)],
        zero=True, fmt="{:+.0f}", legend_loc="lower left",
    )
    bulls = load_obs("AAII_Bullish") * 100.0
    bears = load_obs("AAII_Bearish") * 100.0
    bb_b64, _ = chart_lines(
        [(bulls, "Bulls %"), (bears, "Bears %")],
        fmt="{:.0f}", legend_loc="upper left",
    )
    vix = load_obs("VIXCLS").dropna()
    vix_b64, _ = chart_lines(
        [(vix, "VIX")],
        thresholds=[(30, "30 FEAR", VENUS, "--", 1.0), (15, "15 COMPLACENCY", SEA, "--", 1.0, "top", -0.8)],
        fmt="{:.1f}", legend_loc="upper left",
    )
    umcsent = load_obs("UMCSENT").dropna()
    umc_b64, _ = chart_lines(
        [(umcsent, "U-Mich sentiment")],
        fmt="{:.0f}", legend_loc="lower left",
    )
    neutral = load_obs("AAII_Neutral") * 100.0
    neu_b64, _ = chart_lines(
        [(neutral, "Neutral %")],
        fmt="{:.0f}", legend_loc="upper left",
    )

    spi_v = float(spi.iloc[-1])
    state, color = regime(spi_v)
    sp_v, sp_d = latest(spread)
    bu_v, _ = latest(bulls)
    be_v, _ = latest(bears)

    verdict_text = (
        f"SPI 21d average at {spi_v:+.2f} against the +1.5 capitulation and -1.0 "
        f"euphoria fade lines. AAII spread at {sp_v:+.0f} against the +30 and -20 "
        f"extremes. Sentiment is contrarian at extremes only. Between the fade lines "
        f"we treat it as background weather."
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
        chart_card("The Fear Gauge", "VIX, the options market's price of protection. Below "
                   "15 is complacency, above 30 is fear. Extremes fade, the middle is noise.", vix_b64),
        chart_card("Household Mood", "University of Michigan consumer sentiment. The retail "
                   "read on how households feel, monthly.", umc_b64),
        chart_card("On the Fence", "The AAII neutral share. When indecision runs high the "
                   "crowd has no conviction to fade.", neu_b64),
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
