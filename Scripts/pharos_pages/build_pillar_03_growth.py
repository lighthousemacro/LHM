#!/usr/bin/env python3
"""Pharos — 09 Growth, Pillar 3. All values computed live from the DB."""

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
        return "ABOVE TREND", SEA
    if z < -0.5:
        return "BELOW TREND", VENUS
    return "TREND", OCEAN


def build():
    gci_b64, gci = chart_composite("GCI", "GCI")
    indpro = yoy(load_obs("INDPRO")).dropna()
    ip_b64, _ = chart_lines([(indpro, "Industrial Production YoY")], zero=True, fmt="{:+.1f}%")
    cfnai = load_obs("CFNAIMA3")
    cfnai_b64, _ = chart_lines(
        [(cfnai, "CFNAI 3mo avg")],
        thresholds=[(-0.7, "-0.7 RECESSION LINE", VENUS, "--", 1.0)],
        zero=True, fmt="{:+.2f}", legend_loc="lower left",
    )
    rsx = yoy(load_obs("RSXFS")).dropna()
    rsx_b64, _ = chart_lines([(rsx, "Retail Sales ex Autos YoY, nominal")], zero=True,
                             fmt="{:+.1f}%", legend_loc="upper right")

    gci_v = float(gci.iloc[-1])
    state, color = regime(gci_v)
    ip_v, ip_d = latest(indpro)
    cf_v, _ = latest(cfnai)
    rsx_v, _ = latest(rsx)
    tcu = load_obs("TCU")
    tcu_v, _ = latest(tcu)

    verdict_text = (
        f"GCI 21d average at {gci_v:+.2f}. Industrial production at {ip_v:+.1f}% YoY, "
        f"CFNAI 3mo average at {cf_v:+.2f} against the -0.7 recession line, "
        f"capacity utilization at {tcu_v:.1f}%."
    )

    tiles = "".join([
        tile("Activity Pulse", f"{gci_v:+.2f}", "", "GCI, 21d avg z",
             state, "st-ok" if state == "ABOVE TREND" else "st-alert" if state == "BELOW TREND" else "st-flat", SKY),
        tile("Industrial Prod", f"{ip_v:+.1f}", "%", f"YoY, {ip_d.strftime('%b %Y')}",
             "EXPANDING" if ip_v > 0 else "CONTRACTING", "st-ok" if ip_v > 0 else "st-warn", DUSK),
        tile("CFNAI 3mo", f"{cf_v:+.2f}", "", "Recession line: -0.70",
             "CLEAR" if cf_v > -0.7 else "RECESSION READ", "st-flat" if cf_v > -0.7 else "st-alert", SEA),
        tile("Retail ex Autos", f"{rsx_v:+.1f}", "%", "Nominal YoY",
             "GROWING" if rsx_v > 0 else "SHRINKING", "st-flat" if rsx_v > 0 else "st-warn", VENUS),
        tile("Capacity Util", f"{tcu_v:.1f}", "%", "Total industry",
             "SLACK" if tcu_v < 77 else "NORMAL", "st-warn" if tcu_v < 77 else "st-flat", OCEAN),
    ])

    charts = "".join([
        chart_card("Activity Pulse Index", "The composite growth read. The second derivative "
                   "matters. Daily in gray, 21d average carries the read.", gci_b64),
        chart_card("Industrial Production", "YoY growth in output. Zero is the line "
                   "between expansion and contraction.", ip_b64),
        chart_card("Chicago Fed National Activity", "85 indicators in one index. Three-month "
                   "average below -0.70 has marked every modern recession.", cfnai_b64),
        chart_card("Retail Momentum", "Retail sales ex autos, nominal YoY. The consumer side "
                   "of the growth read.", rsx_b64),
    ])

    wwcm = (
        "GCI 21d average holding above +0.5. "
        "Industrial production reaccelerating above +1% YoY. "
        "CFNAI 3mo average rising back through zero."
    )

    assemble(
        slug="growth", filename="pillar_03_growth.html", h1="GROWTH", pillar_no=3,
        subtitle="Pillar 3. The second derivative matters. Lead time 2 to 4 months.",
        verdict_label="Growth Regime", state=state, state_color=color,
        verdict_text=verdict_text, tiles_html=tiles,
        read_title="The Read",
        read_text=(
            f"Activity composite at {gci_v:+.2f} on the 21d average. CFNAI at {cf_v:+.2f} is "
            f"the cleanest single recession line in the pillar. Everything on this page "
            f"recomputes from the master database each build."),
        charts_html=charts, wwcm=wwcm,
        sources="Lighthouse Macro composites; Federal Reserve; Chicago Fed; Census; FRED",
        datathru=ip_d.strftime("%Y-%m-%d"),
    )


if __name__ == "__main__":
    build()
