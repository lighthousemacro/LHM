#!/usr/bin/env python3
"""Pharos — 15 Financial, Pillar 9. All values computed live from the DB."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pillar_common import (  # noqa: E402
    DUSK, OCEAN, SEA, SKY, VENUS,
    assemble, chart_card, chart_composite, chart_lines, latest, load_index, load_obs, tile,
)


def regime(z: float) -> tuple[str, str]:
    if z > 0.5:
        return "TIGHTENING", VENUS
    if z < -0.5:
        return "EASY", SEA
    return "NEUTRAL", OCEAN


def build():
    fci_b64, fci = chart_composite("FCI", "FCI")
    hy = load_obs("BAMLH0A0HYM2") * 100.0
    ig = load_obs("BAMLC0A0CM") * 100.0
    oas_b64, _ = chart_lines(
        [(hy, "HY OAS, bps"), (ig, "IG OAS, bps")],
        thresholds=[(300, "300 bps COMPLACENT", VENUS, "--", 1.0)],
        fmt="{:,.0f}", legend_loc="upper right",
    )
    clg = load_index("CLG")
    clg_smooth = clg.rolling(21).mean().dropna()
    clg_b64, _ = chart_lines(
        [(clg_smooth, "CLG 21d avg")],
        thresholds=[(-1.0, "-1.0 SPREADS IGNORING LABOR", VENUS, "--", 1.0)],
        zero=True, fmt="{:+.2f}", legend_loc="lower left",
    )

    fci_v = float(fci.iloc[-1])
    state, color = regime(fci_v)
    hy_v, hy_d = latest(hy)
    ig_v, _ = latest(ig)
    clg_v, _ = latest(clg_smooth)

    verdict_text = (
        f"FCI 21d average at {fci_v:+.2f}. HY OAS at {hy_v:.0f} bps against the 300 bps "
        f"complacency line, IG at {ig_v:.0f} bps. The Credit-Labor Gap at {clg_v:+.2f} "
        f"against the -1.0 threshold. Spreads lead defaults by 6 to 9 months."
    )

    tiles = "".join([
        tile("Credit Tide", f"{fci_v:+.2f}", "", "FCI, 21d avg z",
             state, "st-alert" if state == "TIGHTENING" else "st-ok" if state == "EASY" else "st-flat", SKY),
        tile("HY OAS", f"{hy_v:.0f}", "bps", f"{hy_d.strftime('%b %d')}. Complacent below 300",
             "COMPLACENT" if hy_v < 300 else "NORMAL", "st-warn" if hy_v < 300 else "st-flat", DUSK),
        tile("IG OAS", f"{ig_v:.0f}", "bps", "Investment grade",
             "TIGHT" if ig_v < 100 else "NORMAL", "st-warn" if ig_v < 100 else "st-flat", SEA),
        tile("Credit-Labor Gap", f"{clg_v:+.2f}", "", "21d avg. Alert below -1.0",
             "DIVERGING" if clg_v < -1.0 else "ALIGNED", "st-alert" if clg_v < -1.0 else "st-flat", VENUS),
    ])

    charts = "".join([
        chart_card("Credit Tide Index", "The composite credit read. Spreads lead defaults. "
                   "Daily in gray, 21d average carries the read.", fci_b64),
        chart_card("The Spread Complex", "HY and IG option-adjusted spreads. Below 300 bps "
                   "high yield is pricing a world without accidents.", oas_b64),
        chart_card("Credit-Labor Gap", "When spreads price one story and labor tells "
                   "another, the gap goes negative. Below -1.0 is the alert.", clg_b64),
    ])

    wwcm = (
        "HY OAS repricing above 350 bps without a labor deterioration. "
        "The Credit-Labor Gap closing back above -0.5. "
        "FCI 21d average falling through zero."
    )

    assemble(
        slug="financial", filename="pillar_09_financial.html", h1="FINANCIAL", pillar_no=9,
        subtitle="Pillar 9. Spreads lead defaults. Lead time 6 to 9 months.",
        verdict_label="Credit Regime", state=state, state_color=color,
        verdict_text=verdict_text, tiles_html=tiles,
        read_title="The Read",
        read_text=(
            f"The tide composite reads {fci_v:+.2f}. The gap between what credit prices "
            f"and what labor shows is the pillar's sharpest signal, at {clg_v:+.2f} now. "
            f"Everything on this page recomputes from the master database each build."),
        charts_html=charts, wwcm=wwcm,
        sources="Lighthouse Macro composites; ICE BofA; FRED",
        datathru=hy_d.strftime("%Y-%m-%d"),
    )


if __name__ == "__main__":
    build()
