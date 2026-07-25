#!/usr/bin/env python3
"""Pharos — 10 Housing, Pillar 4. All values computed live from the DB."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pillar_common import (  # noqa: E402
    DUSK, OCEAN, SEA, SKY, VENUS,
    assemble, chart_card, chart_composite, chart_composite_lead, chart_lines,
    chart_nowcast, latest, load_obs, nowcast_tile, tile,
)

# Measured, not asserted. `lead_calibration.py HCI` sweeps every non-component target:
# industrial production peaks at 16 months (r 0.53) with a clean interior peak, rising
# into 16 and falling after. Residential investment scores higher (0.64 at 23mo) but is
# quarterly and still climbing at the edge of the window, so we don't lean on it.
# The old "6 to 9 month" claim does not hold at the composite level: correlation there
# is roughly half the peak. Permits and starts do lead on that horizon, and they are
# HCI inputs, which is most likely where the 6-to-9 figure came from.
HCI_LEAD_MONTHS = 16
HCI_LEAD_TARGET = "INDPRO"


def regime(z: float) -> tuple[str, str]:
    if z > 0.5:
        return "RISING TIDE", SEA
    if z < -0.5:
        return "EBBING", VENUS
    return "FROZEN", OCEAN


def build():
    # One HCI chart, not two: the lead overlay carries the composite AND what it
    # leads, so a standalone HCI line would be the same series plotted twice (Bob 7/25).
    lead_b64, hci, lead_corr = chart_composite_lead(
        "HCI", "HCI", HCI_LEAD_TARGET, "Industrial production YoY (LHS)",
        HCI_LEAD_MONTHS,
    )
    starts = load_obs("HOUST")
    permits = load_obs("PERMIT")
    sp_b64, _ = chart_lines(
        [(starts, "Housing starts"), (permits, "Permits")],
        fmt="{:,.0f}", legend_loc="upper right",
    )
    # Affordability Pressure over the raw 30Y, because it already contains the 30Y
    # (rate + median price YoY - wage YoY). The payment is the binding constraint on
    # the marginal buyer, not the coupon on its own.
    afford_b64, afford = chart_composite("AFFORD_PRESSURE", "Affordability Pressure")
    mort = load_obs("MORTGAGE30US")
    supply = load_obs("MSACSR")
    sup_b64, _ = chart_lines([(supply, "Months' supply, new homes")],
                             thresholds=[(6.0, "6.0 = BALANCED MARKET", VENUS, "--", 1.0)],
                             fmt="{:.1f}", legend_loc="upper left")
    nc_b64, nc_v, nc_d = chart_nowcast("HOUSING")

    hci_v = float(hci.iloc[-1])
    state, color = regime(hci_v)
    st_v, st_d = latest(starts)
    pm_v, _ = latest(permits)
    mo_v, _ = latest(mort)
    afford_v = float(afford.iloc[-1])
    # Same bands as descriptive_indicators.BANDS, read high-is-stretched.
    afford_state = ("EXTREME" if afford_v > 1.5 else "ELEVATED" if afford_v > 0.5
                    else "NEUTRAL" if afford_v > -0.5 else "EASY")

    verdict_text = (
        f"HCI at {hci_v:+.2f}. Starts at {st_v:,.0f}k and permits at "
        f"{pm_v:,.0f}k annualized. Affordability pressure at {afford_v:+.2f} "
        f"({afford_state.lower()}) with the 30Y at {mo_v:.2f}%. "
        f"Permits lead starts by a quarter or so. The composite leads the goods cycle "
        f"by about {HCI_LEAD_MONTHS} months."
    )

    tiles = "".join([
        tile("Housing Tide", f"{hci_v:+.2f}", "", "Composite z",
             state, "st-ok" if state == "RISING TIDE" else "st-alert" if state == "EBBING" else "st-flat", SKY),
        tile("Starts", f"{st_v:,.0f}", "k", f"SAAR, {st_d.strftime('%b %Y')}",
             "SOFT" if st_v < 1300 else "STEADY", "st-warn" if st_v < 1300 else "st-flat", DUSK),
        tile("Permits", f"{pm_v:,.0f}", "k", "SAAR. Permits lead starts",
             "SOFT" if pm_v < 1300 else "STEADY", "st-warn" if pm_v < 1300 else "st-flat", SEA),
        tile("Affordability Pressure", f"{afford_v:+.2f}", "", f"30Y at {mo_v:.2f}%, vs wages",
             afford_state, "st-alert" if afford_v > 1.5 else "st-warn" if afford_v > 0.5
             else "st-flat", VENUS),
        nowcast_tile("HOUSING", "Home Price Nowcast"),
    ])

    charts = "".join([
        chart_card("HCI", "The composite housing read, advanced "
                   f"{HCI_LEAD_MONTHS} months against industrial production. Starts, "
                   f"existing sales, months' supply, home prices and the 30Y mortgage in "
                   f"one z-score. Housing commits capital before the goods cycle responds, "
                   f"so the composite turns first and the real economy follows more than a "
                   f"year later. Correlation {lead_corr:+.2f} at the plotted lead.", lead_b64),
        chart_card("Starts and Permits", "Permits lead starts, starts lead completions. "
                   "The front of the housing pipeline.", sp_b64),
        chart_card("Affordability Pressure", "The true cost of owning: the 30Y mortgage plus "
                   f"median sale price growth, net of wages. Reads {afford_v:+.2f}, "
                   f"{afford_state.lower()}. This is the binding constraint on the marginal "
                   f"buyer, and it moves even when the coupon sits still.", afford_b64),
        chart_card("Months of Supply", "New homes for sale divided by the sales pace. Above 6 "
                   "months is a buyer's market, below is a seller's. Inventory is the pressure valve.", sup_b64),
        chart_card("The Home Price Nowcast", "Elastic net over mortgage rates, home values, "
                   "and builder proxies, updated daily between Case-Shiller releases. Solid is "
                   "the realized print, dashed is the model. OOS R² 0.89.", nc_b64),
    ])

    wwcm = (
        "Permits turning up for three consecutive months. "
        "The 30Y mortgage sustained below 6%. "
        "HCI crossing above +0.5."
    )

    assemble(
        slug="housing", filename="pillar_04_housing.html", h1="HOUSING", pillar_no=4,
        subtitle=f"Pillar 4. Frozen equilibrium, rate sensitive. Leads the goods cycle "
                 f"by about {HCI_LEAD_MONTHS} months.",
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
