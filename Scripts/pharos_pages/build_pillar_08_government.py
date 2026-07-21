#!/usr/bin/env python3
"""Pharos — 14 Government, Pillar 8. All values computed live from the DB."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pillar_common import (  # noqa: E402
    DUSK, OCEAN, SEA, SKY, VENUS,
    assemble, chart_card, chart_composite, chart_lines, latest, load_obs, tile,
)


def regime(z: float) -> tuple[str, str]:
    if z > 0.5:
        return "PRESSURE BUILDING", VENUS
    if z < -0.5:
        return "PRESSURE EASING", SEA
    return "STRUCTURAL", OCEAN


def build():
    fpi_b64, fpi = chart_composite("FPI", "FPI")
    y10 = load_obs("DGS10")
    y30 = load_obs("DGS30")
    yields_b64, _ = chart_lines(
        [(y10, "10Y Treasury"), (y30, "30Y Treasury")],
        fmt="{:.2f}%", legend_loc="upper right",
    )
    deficit_m = load_obs("MTSDS133FMS")
    deficit_12m = (deficit_m.rolling(12).sum() / 1000.0).dropna()  # $M -> $B
    def_b64, _ = chart_lines(
        [(deficit_12m, "Federal balance, 12m rolling, $B")],
        zero=True, fmt="{:,.0f}", legend_loc="lower left",
    )

    tp = load_obs("THREEFYTP10")
    tp_b64, _ = chart_lines(
        [(tp, "ACM 10Y term premium")],
        zero=True, fmt="{:+.2f}%", legend_loc="upper right",
    )

    debt_gdp = load_obs("GFDEGDQ188S")
    debtgdp_b64, _ = chart_lines(
        [(debt_gdp, "Federal debt held by public, % of GDP")],
        fmt="{:.0f}%", legend_loc="lower right",
    )

    net_int = load_obs("A091RC1Q027SBEA")
    netint_b64, _ = chart_lines(
        [(net_int, "Net federal interest outlays, $B annualized")],
        fmt="{:,.0f}", legend_loc="upper left",
    )

    fpi_v = float(fpi.iloc[-1])
    state, color = regime(fpi_v)
    y10_v, y10_d = latest(y10)
    y30_v, _ = latest(y30)
    df_v, _ = latest(deficit_12m)

    verdict_text = (
        f"FPI 21d average at {fpi_v:+.2f}. The 10Y at {y10_v:.2f}% and the 30Y at "
        f"{y30_v:.2f}%. The 12-month federal balance runs at {df_v:,.0f}B dollars. "
        f"Fiscal dominance is a structural read. It sets the level of term premium "
        f"rather than the timing of the next move."
    )

    tiles = "".join([
        tile("Fiscal Pressure", f"{fpi_v:+.2f}", "", "FPI, 21d avg z",
             state, "st-alert" if state == "PRESSURE BUILDING" else "st-ok" if state == "PRESSURE EASING" else "st-flat", SKY),
        tile("10Y Treasury", f"{y10_v:.2f}", "%", f"{y10_d.strftime('%b %d')}",
             "LEVEL", "st-flat", DUSK),
        tile("30Y Treasury", f"{y30_v:.2f}", "%", "The long end carries term premium",
             "LEVEL", "st-flat", SEA),
        tile("12m Fed Balance", f"{df_v:,.0f}", "B", "Rolling 12-month, negative = deficit",
             "DEFICIT" if df_v < 0 else "SURPLUS", "st-warn" if df_v < 0 else "st-ok", VENUS),
    ])

    charts = "".join([
        chart_card("Fiscal Pressure Index", "The composite fiscal read, structural by "
                   "nature. Daily in gray, 21d average carries the read.", fpi_b64),
        chart_card("The Long End", "10Y and 30Y Treasury yields. Where fiscal supply "
                   "meets duration demand, term premium lives here.", yields_b64),
        chart_card("The Deficit Run-Rate", "Federal surplus or deficit, 12-month rolling "
                   "sum in billions. The supply side of the Treasury market.", def_b64),
        chart_card("Term Premium", "The ACM 10-year term premium. The extra yield "
                   "investors demand to hold duration. This is where fiscal dominance shows up "
                   "in the price of the long end.", tp_b64),
        chart_card("Debt to GDP", "Federal debt held by the public as a share of GDP. "
                   "The structural backdrop that sets the level of every fiscal read on this page.", debtgdp_b64),
        chart_card("The Interest Burden", "Net federal interest outlays, annualized in "
                   "billions. As the debt stock rolls into higher coupons, this line becomes the "
                   "fastest-growing line in the budget.", netint_b64),
    ])

    wwcm = (
        "The 12-month deficit narrowing for two consecutive quarters. "
        "The 30Y rallying through its one-year average while supply holds. "
        "FPI 21d average falling through zero."
    )

    assemble(
        slug="government", filename="pillar_08_government.html", h1="GOVERNMENT", pillar_no=8,
        subtitle="Pillar 8. Fiscal dominance and term premium. A structural read.",
        verdict_label="Fiscal Regime", state=state, state_color=color,
        verdict_text=verdict_text, tiles_html=tiles,
        read_title="The Read",
        read_text=(
            f"The pressure composite reads {fpi_v:+.2f}. The deficit run-rate at "
            f"{df_v:,.0f}B dollars sets Treasury supply, and the long end prices it. "
            f"Everything on this page recomputes from the master database each build."),
        charts_html=charts, wwcm=wwcm,
        sources="Lighthouse Macro composites; Treasury; FRED",
        datathru=y10_d.strftime("%Y-%m-%d"),
    )


if __name__ == "__main__":
    build()
