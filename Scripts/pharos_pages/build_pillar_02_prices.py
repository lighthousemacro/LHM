#!/usr/bin/env python3
"""Pharos — 08 Prices, Pillar 2. All values computed live from the DB."""

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
        return "HOT", VENUS
    if z < -0.5:
        return "COOL", SKY
    return "CONTAINED", OCEAN


def build():
    pci_b64, pci = chart_composite("PCI", "PCI")
    cpi = yoy(load_obs("CPIAUCSL")).dropna()
    core = yoy(load_obs("CPILFESL")).dropna()
    pce_core = yoy(load_obs("PCEPILFE")).dropna()
    infl_b64, _ = chart_lines(
        [(cpi, "CPI YoY"), (core, "Core CPI YoY"), (pce_core, "Core PCE YoY")],
        thresholds=[(2.0, "2% TARGET", VENUS, "-", 1.0)],
        zero=False, fmt="{:+.1f}%",
    )
    ppi = yoy(load_obs("PPIACO")).dropna()
    ppi_b64, _ = chart_lines([(ppi, "PPI All Commodities YoY")], zero=True, fmt="{:+.1f}%",
                             legend_loc="upper right")

    sticky = load_obs("CORESTICKM159SFRBATL").dropna()
    flex = load_obs("FLEXCPIM159SFRBATL").dropna()
    sf_b64, _ = chart_lines(
        [(sticky, "Sticky Core CPI YoY"), (flex, "Flexible CPI YoY")],
        thresholds=[(2.0, "2% TARGET", VENUS, "--", 1.0)],
        zero=True, fmt="{:+.1f}%",
    )

    be5 = load_obs("T5YIE").dropna()
    be10 = load_obs("T10YIE").dropna()
    be5y5 = load_obs("T5YIFR").dropna()
    be_b64, _ = chart_lines(
        [(be5, "5Y breakeven"), (be10, "10Y breakeven"), (be5y5, "5Y5Y forward")],
        thresholds=[(2.0, "2% TARGET", VENUS, "--", 1.0)],
        zero=False, fmt="{:.2f}%", legend_loc="upper right",
    )

    shelter = yoy(load_obs("CPIHOSSL")).dropna()
    svc = yoy(load_obs("CUSR0000SASLE")).dropna()
    shel_b64, _ = chart_lines(
        [(shelter, "Shelter CPI YoY"), (svc, "Services less energy YoY")],
        thresholds=[(2.0, "2% TARGET", VENUS, "--", 1.0)],
        zero=False, fmt="{:+.1f}%",
    )

    pci_v = float(pci.iloc[-1])
    state, color = regime(pci_v)
    cpi_v, cpi_d = latest(cpi)
    core_v, _ = latest(core)
    pcec_v, _ = latest(pce_core)
    ppi_v, _ = latest(ppi)

    verdict_text = (
        f"PCI 21d average at {pci_v:+.2f}. Headline CPI at {cpi_v:+.1f}% YoY, "
        f"core at {core_v:+.1f}%, core PCE at {pcec_v:+.1f}%, all against the 2% target. "
        f"Pipeline PPI at {ppi_v:+.1f}% YoY."
    )

    tiles = "".join([
        tile("Inflation Heat", f"{pci_v:+.2f}", "", "PCI, 21d avg z. Hot above +0.5",
             state, "st-alert" if state == "HOT" else "st-ok" if state == "COOL" else "st-flat", SKY),
        tile("CPI", f"{cpi_v:+.1f}", "%", f"Headline YoY, {cpi_d.strftime('%b %Y')}",
             "ABOVE 2%" if cpi_v > 2.0 else "AT TARGET", "st-warn" if cpi_v > 3.0 else "st-flat", VENUS),
        tile("Core CPI", f"{core_v:+.1f}", "%", "Ex food and energy YoY",
             "STICKY" if core_v > 3.0 else "EASING", "st-warn" if core_v > 3.0 else "st-flat", DUSK),
        tile("Core PCE", f"{pcec_v:+.1f}", "%", "The Fed's preferred gauge YoY",
             "ABOVE 2%" if pcec_v > 2.0 else "AT TARGET", "st-warn" if pcec_v > 2.5 else "st-flat", SEA),
        tile("PPI", f"{ppi_v:+.1f}", "%", "Pipeline pressure YoY",
             "BUILDING" if ppi_v > 2.0 else "QUIET", "st-warn" if ppi_v > 4.0 else "st-flat", OCEAN),
    ])

    charts = "".join([
        chart_card("Inflation Heat Index", "The composite inflation read. Daily in gray, "
                   "21d average carries the read.", pci_b64),
        chart_card("The Last Mile", "Headline, core, and core PCE against the 2% target. "
                   "Shelter makes the last mile sticky, with a 12 to 18 month lead.", infl_b64),
        chart_card("Pipeline Pressure", "PPI all commodities YoY. What producers pay "
                   "shows up in what consumers pay later.", ppi_b64),
        chart_card("Sticky vs Flexible", "Sticky core prices reset slowly and carry the "
                   "trend. Flexible prices swing with demand. The gap is where the last mile lives.", sf_b64),
        chart_card("What the Market Expects", "Market-based inflation expectations. Five and "
                   "ten year breakevens with the 5Y5Y forward. Where the bond market prices the 2% target.", be_b64),
        chart_card("The Shelter Anchor", "Shelter YoY against services less energy. Shelter is "
                   "the largest and slowest core component, and it leads the services read by quarters.", shel_b64),
    ])

    wwcm = (
        "Core CPI printing below 3% for three consecutive months. "
        "Core PCE converging to the 2% target. "
        "PCI 21d average falling through zero."
    )

    assemble(
        slug="prices", filename="pillar_02_prices.html", h1="PRICES", pillar_no=2,
        subtitle="Pillar 2. The last mile is sticky. Shelter leads by 12 to 18 months.",
        verdict_label="Inflation Regime", state=state, state_color=color,
        verdict_text=verdict_text, tiles_html=tiles,
        read_title="The Read",
        read_text=(
            f"The composite reads {pci_v:+.2f} on the 21d average. Core measures carry "
            f"more signal than headline, and pipeline PPI at {ppi_v:+.1f}% shows what is "
            f"still working through. Everything on this page recomputes from the master "
            f"database each build."),
        charts_html=charts, wwcm=wwcm,
        sources="Lighthouse Macro composites; BLS; BEA; FRED",
        datathru=cpi_d.strftime("%Y-%m-%d"),
    )


if __name__ == "__main__":
    build()
