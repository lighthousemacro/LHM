#!/usr/bin/env python3
"""Pharos — 16 Plumbing, Pillar 10. All values computed live from the DB.

Captions on this page stay purely descriptive by editorial rule.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pillar_common import (  # noqa: E402
    DUSK, OCEAN, SEA, SKY, VENUS,
    assemble, chart_card, chart_composite, chart_lines, latest, load_obs, tile,
)


def regime(z: float) -> tuple[str, str]:
    if z < -0.5:
        return "SCARCE", VENUS
    if z > 0.5:
        return "AMPLE", SEA
    return "ADEQUATE", OCEAN


def build():
    lci_b64, lci = chart_composite(
        "LCI", "LCI",
        thresholds=[(-0.5, "-0.5 SCARCE", VENUS, "--", 1.0, "top", -0.06)],
    )
    rrp = load_obs("RRPONTSYD")
    rrp_b64, _ = chart_lines(
        [(rrp, "RRP balance, $B")],
        thresholds=[(200, "$200B", DUSK, "--", 1.0)],
        fmt="{:,.0f}", legend_loc="upper left",
    )
    effr = load_obs("EFFR")
    iorb = load_obs("IORB")
    spread = ((effr - iorb) * 100.0).dropna()
    sp_b64, _ = chart_lines(
        [(spread, "EFFR minus IORB, bps")],
        thresholds=[(8, "+8 bps", VENUS, "--", 1.0)],
        zero=True, fmt="{:+.0f}", legend_loc="upper left",
    )
    walcl = load_obs("WALCL") / 1_000_000.0  # $M -> $T
    tga = load_obs("WTREGEN") / 1_000.0     # $B -> ... check units at runtime
    bs_b64, _ = chart_lines(
        [(walcl, "Fed balance sheet, $T")],
        fmt="{:.2f}", legend_loc="upper left",
    )

    lci_v = float(lci.iloc[-1])
    state, color = regime(lci_v)
    rrp_v, rrp_d = latest(rrp)
    sp_v, _ = latest(spread)
    bs_v, _ = latest(walcl)

    verdict_text = (
        f"LCI 21d average at {lci_v:+.2f}. RRP balance at {rrp_v:,.0f}B dollars against "
        f"the 200B reference. EFFR minus IORB at {sp_v:+.0f} bps against the +8 bps line. "
        f"Fed balance sheet at {bs_v:.2f}T dollars."
    )

    tiles = "".join([
        tile("Liquidity Cushion", f"{lci_v:+.2f}", "", "LCI, 21d avg z. Scarce below -0.5",
             state, "st-alert" if state == "SCARCE" else "st-ok" if state == "AMPLE" else "st-flat", SKY),
        tile("RRP Balance", f"{rrp_v:,.0f}", "B", f"{rrp_d.strftime('%b %d')}. Reference: 200B",
             "BELOW 200B" if rrp_v < 200 else "ABOVE 200B",
             "st-warn" if rrp_v < 200 else "st-flat", DUSK),
        tile("EFFR - IORB", f"{sp_v:+.0f}", "bps", "Reference: +8 bps",
             "ABOVE +8" if sp_v > 8 else "CONTAINED", "st-alert" if sp_v > 8 else "st-flat", VENUS),
        tile("Fed Balance Sheet", f"{bs_v:.2f}", "T", "Total assets",
             "LEVEL", "st-flat", SEA),
    ])

    charts = "".join([
        chart_card("Liquidity Cushion Index", "The composite plumbing read. Daily in gray, "
                   "21d average carries the read. Lead time 1 to 4 weeks.", lci_b64),
        chart_card("Reverse Repo", "The RRP facility balance in billions, with the 200B "
                   "reference line marked.", rrp_b64),
        chart_card("The Corridor", "Effective fed funds minus interest on reserve balances, "
                   "in basis points, with the +8 bps reference marked.", sp_b64),
        chart_card("The Balance Sheet", "Total Federal Reserve assets in trillions.", bs_b64),
    ])

    wwcm = (
        "LCI 21d average recovering above zero. "
        "EFFR minus IORB holding below +5 bps through a quarter-end. "
        "Both would mark funding conditions loosening."
    )

    assemble(
        slug="plumbing", filename="pillar_10_plumbing.html", h1="PLUMBING", pillar_no=10,
        subtitle="Pillar 10. The pipes under the market. Lead time 1 to 4 weeks.",
        verdict_label="Plumbing Regime", state=state, state_color=color,
        verdict_text=verdict_text, tiles_html=tiles,
        read_title="The Read",
        read_text=(
            f"The cushion composite reads {lci_v:+.2f}. The corridor spread at {sp_v:+.0f} bps "
            f"and the RRP balance at {rrp_v:,.0f}B are the fastest-moving reads in the "
            f"framework. Everything on this page recomputes from the master database each build."),
        charts_html=charts, wwcm=wwcm,
        sources="Lighthouse Macro composites; NY Fed; Federal Reserve; FRED",
        datathru=rrp_d.strftime("%Y-%m-%d"),
    )


if __name__ == "__main__":
    build()
