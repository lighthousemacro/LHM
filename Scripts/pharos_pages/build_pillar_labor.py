#!/usr/bin/env python3
"""Pharos — 07 Labor, Pillar 1. All values computed live from the DB."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from terminal_theme import (  # noqa: E402
    DUSK, OCEAN, SEA, SKY, VENUS, DARK_MUTED,
    add_recessions, chart_card, dark_fig, latest, legend, load_index, load_obs,
    pill, render_page, section, set_xlim, sigma_refs, style_ax, tile, to_b64,
    verdict_block, write_page, yoy, zero_line,
)


def labor_regime(z: float) -> tuple[str, str]:
    if z > 0.5:
        return "FRAGILE", VENUS
    if z < -0.5:
        return "TIGHT", SEA
    return "BALANCED", OCEAN


def chart_lfi():
    lfi = load_index("LFI")
    smooth = lfi.rolling(63).mean().dropna()
    start = lfi.index.min()
    fig, ax = dark_fig()
    add_recessions(ax, start)
    zero_line(ax)
    sigma_refs(ax)
    ax.plot(lfi.index, lfi.values, color=DARK_MUTED, linewidth=0.7, alpha=0.45,
            label=f"LFI daily ({lfi.iloc[-1]:+.2f})")
    ax.plot(smooth.index, smooth.values, color=SKY, linewidth=2.2,
            label=f"LFI 3mo avg ({smooth.iloc[-1]:+.2f})")
    ax.axhline(0.5, color=VENUS, linewidth=1.0, alpha=0.7, linestyle="--")
    ax.text(0.985, 0.56, "+0.5 FRAGILE", transform=ax.get_yaxis_transform(),
            fontsize=8, color=VENUS, ha="right", va="bottom", fontweight="bold", alpha=0.85)
    style_ax(ax)
    set_xlim(ax, start, lfi.index.max())
    v, d = latest(smooth)
    pill(ax, d, v, f"{v:+.2f}", SKY)
    legend(ax, loc="upper left")
    return to_b64(fig), smooth


def chart_quits():
    quits = load_obs("JTSQUR")
    start = quits.index.min()
    fig, ax = dark_fig()
    add_recessions(ax, start)
    ax.plot(quits.index, quits.values, color=SKY, linewidth=2.0,
            label=f"Quits rate ({quits.iloc[-1]:.1f}%)")
    ax.axhline(2.0, color=VENUS, linewidth=1.2, alpha=0.75, linestyle="--")
    ax.text(0.985, 2.03, "2.0% PRE-RECESSION FLOOR", transform=ax.get_yaxis_transform(),
            fontsize=8, color=VENUS, ha="right", va="bottom", fontweight="bold", alpha=0.85)
    style_ax(ax)
    set_xlim(ax, start, quits.index.max())
    v, d = latest(quits)
    pill(ax, d, v, f"{v:.1f}%", SKY if v >= 2.0 else VENUS)
    legend(ax, loc="upper left")
    return to_b64(fig), quits


def chart_payrolls():
    pay = load_obs("PAYEMS")
    pay_yoy = yoy(pay).dropna()
    window_start = pd.Timestamp("2000-01-01")
    start = max(pay_yoy.index.min(), window_start)
    fig, ax = dark_fig()
    add_recessions(ax, start)
    zero_line(ax)
    ax.plot(pay_yoy.index, pay_yoy.values, color=DUSK, linewidth=2.0,
            label=f"Payrolls YoY ({pay_yoy.iloc[-1]:+.1f}%)")
    style_ax(ax)
    set_xlim(ax, start, pay_yoy.index.max())
    v, d = latest(pay_yoy)
    pill(ax, d, v, f"{v:+.1f}%", DUSK)
    legend(ax, loc="lower left")
    return to_b64(fig), pay_yoy


def build():
    lfi_b64, lfi_smooth = chart_lfi()
    quits_b64, quits = chart_quits()
    pay_b64, pay_yoy_s = chart_payrolls()

    lfi_v = float(lfi_smooth.iloc[-1])
    regime, regime_color = labor_regime(lfi_v)
    quits_v = float(quits.iloc[-1])
    quits_d = quits.index.max().strftime("%b %Y")
    ahe = yoy(load_obs("CES0500000003")).dropna()
    ahe_v = float(ahe.iloc[-1])
    unrate = load_obs("UNRATE")
    un_v = float(unrate.iloc[-1])
    pay_v = float(pay_yoy_s.iloc[-1])

    verdict_text = (
        f"LFI 3mo average at {lfi_v:+.2f}. "
        f"Quits at {quits_v:.1f}% as of {quits_d}, "
        f"{'below' if quits_v < 2.0 else 'above'} the 2.0% pre-recession floor. "
        f"Payroll growth at {pay_v:+.1f}% YoY, wages at {ahe_v:+.1f}% YoY."
    )

    tiles = "".join([
        tile("Labor Fragility", f"{lfi_v:+.2f}", "", "LFI, 3mo avg z. Fragile above +0.5",
             regime, "st-alert" if regime == "FRAGILE" else "st-ok" if regime == "TIGHT" else "st-flat", SKY),
        tile("Quits Rate", f"{quits_v:.1f}", "%", f"JOLTS, {quits_d}. Floor: 2.0%",
             "BELOW FLOOR" if quits_v < 2.0 else "ABOVE FLOOR",
             "st-alert" if quits_v < 2.0 else "st-ok", VENUS),
        tile("Payroll Growth", f"{pay_v:+.1f}", "%", "Nonfarm payrolls YoY",
             "COOLING" if pay_v < 1.0 else "STEADY", "st-warn" if pay_v < 1.0 else "st-flat", DUSK),
        tile("Wage Growth", f"{ahe_v:+.1f}", "%", "Avg hourly earnings YoY",
             "REAL TEST", "st-flat", SEA),
        tile("Unemployment", f"{un_v:.1f}", "%", "U-3 headline rate",
             "LAGGING READ", "st-flat", OCEAN),
    ])

    charts = "".join([
        chart_card("Labor Fragility Index", "The pressure underneath the labor market. "
                   "The stuff that moves before the headline. Daily in gray, 3mo average carries the read.", lfi_b64),
        chart_card("The Quit Signal", "Quits are truth serum. Workers only walk when they "
                   "are confident. The 2.0% floor has preceded every modern recession.", quits_b64),
        chart_card("Payrolls Momentum", "Headline payroll growth YoY. By the time this "
                   "breaks, the story is usually already over.", pay_b64),
    ])

    wwcm = (
        f"Quits recovering above 2.0% and holding for two prints. "
        f"LFI 3mo average turning down through +0.25. "
        f"Payroll growth reaccelerating above +1.5% YoY with wages outrunning CPI."
    )

    body = (
        verdict_block("Labor Regime", regime, verdict_text, regime_color)
        + f'<div class="tiles">{tiles}</div>'
        + section("The Read",
                  f"Flows lead, stocks lag. The quits rate at {quits_v:.1f}% is the cleanest "
                  f"forward read in the pillar, and the unemployment rate at {un_v:.1f}% is the "
                  f"most lagging. Everything on this page recomputes from the master database each build.")
        + f'<div class="charts">{charts}</div>'
        + section("What Would Change Our Mind", wwcm)
    )

    datathru = max(lfi_smooth.index.max(), quits.index.max()).strftime("%Y-%m-%d")
    html = render_page(
        title="Labor — Pillar 1", h1="LABOR", subtitle="Pillar 1. Quits are truth serum. Flows lead, stocks lag.",
        active="labor", body=body,
        sources="Lighthouse Macro composites; BLS; JOLTS; FRED",
        datathru=datathru,
    )
    out = write_page("pillar_01_labor.html", html)
    print(f"Wrote {out} ({out.stat().st_size:,} bytes)")


if __name__ == "__main__":
    build()
