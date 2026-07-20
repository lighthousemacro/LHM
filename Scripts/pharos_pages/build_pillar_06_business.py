#!/usr/bin/env python3
"""Pharos — 12 Business, Pillar 6. All values computed live from the DB."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pillar_common import (  # noqa: E402
    DUSK, OCEAN, SEA, SKY, VENUS,
    assemble, chart_card, chart_composite, chart_lines, chart_nowcast,
    latest, load_obs, nowcast_tile, tile, yoy,
)


def regime(z: float) -> tuple[str, str]:
    if z > 0.5:
        return "COMMITTING", SEA
    if z < -0.5:
        return "PULLING BACK", VENUS
    return "HOLDING", OCEAN


def build():
    bci_b64, bci = chart_composite("BCI", "BCI")
    orders = yoy(load_obs("DGORDER")).dropna()
    ord_b64, _ = chart_lines([(orders, "Durable goods orders YoY")], zero=True, fmt="{:+.1f}%")
    tcu = load_obs("TCU")
    tcu_b64, _ = chart_lines([(tcu, "Capacity utilization")], fmt="{:.1f}%",
                             legend_loc="lower left")
    nc_b64, nc_v, nc_d = chart_nowcast("INDPRO")

    bci_v = float(bci.iloc[-1])
    state, color = regime(bci_v)
    or_v, or_d = latest(orders)
    tc_v, _ = latest(tcu)
    ip = yoy(load_obs("INDPRO")).dropna()
    ip_v, _ = latest(ip)

    verdict_text = (
        f"BCI 21d average at {bci_v:+.2f}. Durable goods orders at {or_v:+.1f}% YoY, "
        f"industrial production at {ip_v:+.1f}%, capacity utilization at {tc_v:.1f}%. "
        f"Capex is a forward commitment. Lead time 4 to 8 months."
    )

    tiles = "".join([
        tile("Capex Thrust", f"{bci_v:+.2f}", "", "BCI, 21d avg z",
             state, "st-ok" if state == "COMMITTING" else "st-alert" if state == "PULLING BACK" else "st-flat", SKY),
        tile("Durable Orders", f"{or_v:+.1f}", "%", f"YoY, {or_d.strftime('%b %Y')}",
             "EXPANDING" if or_v > 0 else "CONTRACTING", "st-ok" if or_v > 0 else "st-warn", DUSK),
        tile("Industrial Prod", f"{ip_v:+.1f}", "%", "YoY",
             "EXPANDING" if ip_v > 0 else "CONTRACTING", "st-flat" if ip_v > 0 else "st-warn", SEA),
        tile("Capacity Util", f"{tc_v:.1f}", "%", "Total industry",
             "SLACK" if tc_v < 77 else "NORMAL", "st-warn" if tc_v < 77 else "st-flat", OCEAN),
        nowcast_tile("INDPRO", "IP Nowcast"),
    ])

    charts = "".join([
        chart_card("Capex Thrust Index", "The composite business investment read. Capex is "
                   "a forward commitment. Daily in gray, 21d average carries the read.", bci_b64),
        chart_card("Orders Momentum", "Durable goods orders YoY. Businesses order equipment "
                   "when they believe in the next two years.", ord_b64),
        chart_card("Capacity", "Utilization says whether the capital stock is working. "
                   "Slack below 77% removes the reason to build more.", tcu_b64),
        chart_card("The IP Nowcast", "Elastic net over market and macro proxies, updated "
                   "daily between releases. Solid is the realized print, dashed is the "
                   "model. OOS R² 0.61.", nc_b64),
    ])

    if state == "COMMITTING":
        wwcm = (
            "Durable orders rolling over below zero YoY. "
            "Capacity utilization falling through 77%. "
            "BCI 21d average breaking back below +0.5."
        )
    elif state == "PULLING BACK":
        wwcm = (
            "Durable orders reaccelerating above +3% YoY. "
            "Capacity utilization rising back through 78%. "
            "BCI 21d average recovering through -0.5."
        )
    else:
        wwcm = (
            "BCI 21d average breaking out of the -0.5 to +0.5 band in either direction, "
            "with durable orders and utilization confirming the move."
        )

    assemble(
        slug="business", filename="pillar_06_business.html", h1="BUSINESS", pillar_no=6,
        subtitle="Pillar 6. Capex is a forward commitment. Lead time 4 to 8 months.",
        verdict_label="Business Regime", state=state, state_color=color,
        verdict_text=verdict_text, tiles_html=tiles,
        read_title="The Read",
        read_text=(
            f"The thrust composite reads {bci_v:+.2f}. Orders at {or_v:+.1f}% YoY are the "
            f"commitment signal, utilization at {tc_v:.1f}% is the constraint. Everything "
            f"on this page recomputes from the master database each build."),
        charts_html=charts, wwcm=wwcm,
        sources="Lighthouse Macro composites; Census; Federal Reserve; FRED",
        datathru=or_d.strftime("%Y-%m-%d"),
    )


if __name__ == "__main__":
    build()
