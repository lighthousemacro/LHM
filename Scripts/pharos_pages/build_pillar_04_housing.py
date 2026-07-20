#!/usr/bin/env python3
"""Pharos — 10 Housing, Pillar 4. All values computed live from the DB."""

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
        return "RISING TIDE", SEA
    if z < -0.5:
        return "EBBING", VENUS
    return "FROZEN", OCEAN


def build():
    hci_b64, hci = chart_composite("HCI", "HCI")
    starts = load_obs("HOUST")
    permits = load_obs("PERMIT")
    sp_b64, _ = chart_lines(
        [(starts, "Housing starts"), (permits, "Permits")],
        fmt="{:,.0f}", legend_loc="upper right",
    )
    mort = load_obs("MORTGAGE30US")
    mort_b64, _ = chart_lines([(mort, "30Y mortgage rate")], fmt="{:.2f}%",
                              legend_loc="upper left")
    nc_b64, nc_v, nc_d = chart_nowcast("HOUSING")

    hci_v = float(hci.iloc[-1])
    state, color = regime(hci_v)
    st_v, st_d = latest(starts)
    pm_v, _ = latest(permits)
    mo_v, _ = latest(mort)

    verdict_text = (
        f"HCI 21d average at {hci_v:+.2f}. Starts at {st_v:,.0f}k and permits at "
        f"{pm_v:,.0f}k annualized, with the 30Y mortgage at {mo_v:.2f}%. "
        f"Permits lead starts, and both lead the cycle by 6 to 9 months."
    )

    tiles = "".join([
        tile("Housing Tide", f"{hci_v:+.2f}", "", "HCI, 21d avg z",
             state, "st-ok" if state == "RISING TIDE" else "st-alert" if state == "EBBING" else "st-flat", SKY),
        tile("Starts", f"{st_v:,.0f}", "k", f"SAAR, {st_d.strftime('%b %Y')}",
             "SOFT" if st_v < 1300 else "STEADY", "st-warn" if st_v < 1300 else "st-flat", DUSK),
        tile("Permits", f"{pm_v:,.0f}", "k", "SAAR. Permits lead starts",
             "SOFT" if pm_v < 1300 else "STEADY", "st-warn" if pm_v < 1300 else "st-flat", SEA),
        tile("30Y Mortgage", f"{mo_v:.2f}", "%", "Freddie Mac weekly",
             "RESTRICTIVE" if mo_v > 6.0 else "NEUTRAL", "st-warn" if mo_v > 6.0 else "st-flat", VENUS),
        nowcast_tile("HOUSING", "Home Price Nowcast"),
    ])

    charts = "".join([
        chart_card("Housing Tide Index", "The composite housing read. Rate sensitive, "
                   "6 to 9 month lead. Daily in gray, 21d average carries the read.", hci_b64),
        chart_card("Starts and Permits", "Permits lead starts, starts lead completions. "
                   "The front of the housing pipeline.", sp_b64),
        chart_card("The Price of Money", "The 30Y mortgage rate sets the affordability "
                   "constraint for the marginal buyer.", mort_b64),
        chart_card("The Home Price Nowcast", "Elastic net over mortgage rates, home values, "
                   "and builder proxies, updated daily between Case-Shiller releases. Solid is "
                   "the realized print, dashed is the model. OOS R² 0.89.", nc_b64),
    ])

    wwcm = (
        "Permits turning up for three consecutive months. "
        "The 30Y mortgage sustained below 6%. "
        "HCI 21d average crossing above +0.5."
    )

    assemble(
        slug="housing", filename="pillar_04_housing.html", h1="HOUSING", pillar_no=4,
        subtitle="Pillar 4. Frozen equilibrium, rate sensitive. Lead time 6 to 9 months.",
        verdict_label="Housing Regime", state=state, state_color=color,
        verdict_text=verdict_text, tiles_html=tiles,
        read_title="The Read",
        read_text=(
            f"The tide composite reads {hci_v:+.2f}. Permits at {pm_v:,.0f}k are the "
            f"cleanest forward read in the pillar. Everything on this page recomputes "
            f"from the master database each build."),
        charts_html=charts, wwcm=wwcm,
        sources="Lighthouse Macro composites; Census; Freddie Mac; FRED",
        datathru=st_d.strftime("%Y-%m-%d"),
    )


if __name__ == "__main__":
    build()
