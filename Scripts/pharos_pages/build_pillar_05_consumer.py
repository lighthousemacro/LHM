#!/usr/bin/env python3
"""Pharos — 11 Consumer, Pillar 5. All values computed live from the DB."""

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
        return "SPENDING", SEA
    if z < -0.5:
        return "RETRENCHING", VENUS
    return "STEADY", OCEAN


def build():
    cci_b64, cci = chart_composite("CCI", "CCI")
    pce = yoy(load_obs("PCEC96")).dropna()
    pce_b64, _ = chart_lines([(pce, "Real PCE YoY")], zero=True, fmt="{:+.1f}%")
    save = load_obs("PSAVERT")
    save_b64, _ = chart_lines(
        [(save, "Personal saving rate")],
        thresholds=[(4.5, "4.5% THIN BUFFER", VENUS, "--", 1.0)],
        fmt="{:.1f}%", legend_loc="upper right",
    )
    umich = load_obs("UMCSENT")
    um_b64, _ = chart_lines([(umich, "UMich sentiment")], fmt="{:.1f}",
                            legend_loc="upper right")

    cci_v = float(cci.iloc[-1])
    state, color = regime(cci_v)
    pce_v, pce_d = latest(pce)
    sv_v, _ = latest(save)
    um_v, _ = latest(umich)

    verdict_text = (
        f"CCI 21d average at {cci_v:+.2f}. Real PCE at {pce_v:+.1f}% YoY, the saving rate "
        f"at {sv_v:.1f}%, UMich sentiment at {um_v:.1f}. The consumer is 68% of GDP. "
        f"The Last Domino."
    )

    tiles = "".join([
        tile("Consumer Pulse", f"{cci_v:+.2f}", "", "CCI, 21d avg z",
             state, "st-ok" if state == "SPENDING" else "st-alert" if state == "RETRENCHING" else "st-flat", SKY),
        tile("Real PCE", f"{pce_v:+.1f}", "%", f"YoY, {pce_d.strftime('%b %Y')}",
             "GROWING" if pce_v > 1.5 else "SOFT", "st-ok" if pce_v > 1.5 else "st-warn", DUSK),
        tile("Saving Rate", f"{sv_v:.1f}", "%", "Thin buffer below 4.5%",
             "THIN" if sv_v < 4.5 else "REBUILDING", "st-alert" if sv_v < 4.5 else "st-flat", VENUS),
        tile("UMich Sentiment", f"{um_v:.1f}", "", "Long-run average near 85",
             "DEPRESSED" if um_v < 70 else "NORMAL", "st-warn" if um_v < 70 else "st-flat", SEA),
    ])

    charts = "".join([
        chart_card("Consumer Pulse Index", "The composite consumer read. 68% of GDP. "
                   "Daily in gray, 21d average carries the read.", cci_b64),
        chart_card("Real Spending", "Real PCE YoY. The single number the whole cycle "
                   "eventually answers to.", pce_b64),
        chart_card("The Buffer", "The saving rate is the margin of safety. Below 4.5% "
                   "the cushion between income and spending is thin.", save_b64),
        chart_card("How It Feels", "UMich sentiment. Days-to-weeks signal, contrarian "
                   "at extremes, honest about the mood.", um_b64),
    ])

    wwcm = (
        "Saving rate rebuilding above 5%. "
        "Real PCE holding above +2% YoY. "
        "CCI 21d average rising through +0.5."
    )

    assemble(
        slug="consumer", filename="pillar_05_consumer.html", h1="CONSUMER", pillar_no=5,
        subtitle="Pillar 5. 68% of GDP. The Last Domino. Lead time 1 to 3 months.",
        verdict_label="Consumer Regime", state=state, state_color=color,
        verdict_text=verdict_text, tiles_html=tiles,
        read_title="The Read",
        read_text=(
            f"The pulse composite reads {cci_v:+.2f}. Aggregate spending holds up until "
            f"it does not, and the saving rate at {sv_v:.1f}% says how much room is left. "
            f"Everything on this page recomputes from the master database each build."),
        charts_html=charts, wwcm=wwcm,
        sources="Lighthouse Macro composites; BEA; UMich; FRED",
        datathru=pce_d.strftime("%Y-%m-%d"),
    )


if __name__ == "__main__":
    build()
