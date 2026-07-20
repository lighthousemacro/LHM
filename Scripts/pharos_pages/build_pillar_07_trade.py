#!/usr/bin/env python3
"""Pharos — 13 Trade, Pillar 7. All values computed live from the DB."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pillar_common import (  # noqa: E402
    DUSK, OCEAN, SEA, SKY, VENUS,
    assemble, chart_card, chart_composite, chart_lines, latest, load_obs, tile, yoy,
)


def regime(z: float) -> tuple[str, str]:
    if z > 0.5:
        return "RISK TIDE IN", SEA
    if z < -0.5:
        return "RISK TIDE OUT", VENUS
    return "SLACK TIDE", OCEAN


def build():
    tci_b64, tci = chart_composite("TCI", "TCI")
    dxy = load_obs("DTWEXBGS")
    dxy_b64, _ = chart_lines([(dxy, "Trade-weighted dollar")], fmt="{:.1f}",
                             legend_loc="upper left")
    dxy_yoy = yoy(dxy, periods=252).dropna()
    dyoy_b64, _ = chart_lines([(dxy_yoy, "Dollar YoY")], zero=True, fmt="{:+.1f}%",
                              legend_loc="lower left")
    jpy = load_obs("DEXJPUS")
    jpy_b64, _ = chart_lines([(jpy, "USDJPY")], fmt="{:.0f}", legend_loc="upper left")

    tci_v = float(tci.iloc[-1])
    state, color = regime(tci_v)
    dx_v, dx_d = latest(dxy)
    dy_v, _ = latest(dxy_yoy)
    jp_v, _ = latest(jpy)
    cny = load_obs("DEXCHUS")
    cn_v, _ = latest(cny)

    verdict_text = (
        f"TCI 21d average at {tci_v:+.2f}. The trade-weighted dollar at {dx_v:.1f}, "
        f"{dy_v:+.1f}% YoY. Dollar direction is the rotation engine for global risk."
    )

    tiles = "".join([
        tile("Global Risk Tide", f"{tci_v:+.2f}", "", "TCI, 21d avg z",
             state, "st-ok" if state == "RISK TIDE IN" else "st-alert" if state == "RISK TIDE OUT" else "st-flat", SKY),
        tile("TW Dollar", f"{dx_v:.1f}", "", f"Broad index, {dx_d.strftime('%b %d')}",
             "STRONG" if dy_v > 0 else "WEAKENING", "st-warn" if dy_v > 5 else "st-flat", DUSK),
        tile("Dollar YoY", f"{dy_v:+.1f}", "%", "252-day change",
             "TIGHTENING" if dy_v > 0 else "EASING", "st-warn" if dy_v > 0 else "st-ok", SEA),
        tile("USDJPY", f"{jp_v:.0f}", "", "Yen per dollar",
             "LEVEL", "st-flat", VENUS),
        tile("USDCNY", f"{cn_v:.2f}", "", "Yuan per dollar",
             "LEVEL", "st-flat", OCEAN),
    ])

    charts = "".join([
        chart_card("Global Risk Tide Index", "The composite external read. Dollar dynamics "
                   "drive the rotation. Daily in gray, 21d average carries the read.", tci_b64),
        chart_card("The Dollar", "Trade-weighted broad dollar. A strong dollar tightens "
                   "global conditions with a 3 to 6 month lead.", dxy_b64),
        chart_card("Dollar Momentum", "YoY change in the broad dollar. The rate of change "
                   "carries more signal than the level.", dyoy_b64),
        chart_card("The Yen Cross", "USDJPY. The funding currency the world watches when "
                   "carry unwinds.", jpy_b64),
    ])

    wwcm = (
        "Dollar YoY turning negative and holding for a month. "
        "TCI 21d average crossing above +0.5. "
        "Both would mark the external tide turning supportive."
    )

    assemble(
        slug="trade", filename="pillar_07_trade.html", h1="TRADE", pillar_no=7,
        subtitle="Pillar 7. The rotation engine runs on dollar dynamics. Lead 3 to 6 months.",
        verdict_label="External Regime", state=state, state_color=color,
        verdict_text=verdict_text, tiles_html=tiles,
        read_title="The Read",
        read_text=(
            f"The tide composite reads {tci_v:+.2f}. The dollar at {dy_v:+.1f}% YoY is the "
            f"cleanest lever on global liquidity in the pillar. Everything on this page "
            f"recomputes from the master database each build."),
        charts_html=charts, wwcm=wwcm,
        sources="Lighthouse Macro composites; Federal Reserve; FRED",
        datathru=dx_d.strftime("%Y-%m-%d"),
    )


if __name__ == "__main__":
    build()
