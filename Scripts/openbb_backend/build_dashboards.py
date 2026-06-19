"""
Builder for the Lighthouse Macro OpenBB Workspace dashboard set.

Idempotent merge: loads the existing widgets.json / apps.json, ADDS the
asset-class dashboards, the mainpage ("The Watch"), and the sixth primary
("The Risk Desk"), renumbers the twelve pillar apps to slot after the six
primaries, and writes both manifests back. Re-running overwrites only the
keys it owns; existing primary/pillar layouts are preserved.

Target lineup (25 dashboards):
    00 The Watch          mainpage / cover
    01 The Pulse  ... 05 Divergence      five existing primaries
    06 The Risk Desk      new sixth primary (recession prob / ensemble risk)
    07 Labor      ... 18 Sentiment       twelve pillars (renumbered 06->07 ..)
    19 Equities   ... 24 Crypto          six asset classes (new)

Run:
    python Scripts/openbb_backend/build_dashboards.py
"""

from __future__ import annotations

import json
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent
WIDGETS_PATH = BACKEND_DIR / "widgets.json"
APPS_PATH = BACKEND_DIR / "apps.json"

CATEGORY = "Lighthouse Macro"

# Shared table column layout for "latest reading" tiles (mirrors the pillar
# key-series widgets so every table looks the same across the workspace).
LATEST_COLUMNS = {
    "table": {
        "showAll": True,
        "columnsDefs": [
            {"field": "series_id", "headerName": "ID", "pinned": "left", "width": 150},
            {"field": "title", "headerName": "Title", "width": 280},
            {"field": "date", "headerName": "Date", "cellDataType": "date", "width": 110},
            {"field": "value", "headerName": "Value", "cellDataType": "number", "width": 120},
            {"field": "units", "headerName": "Units", "width": 110},
        ],
    }
}


# --------------------------------------------------------------------------- #
# Widget factories
# --------------------------------------------------------------------------- #
def _date_params() -> list[dict]:
    return [
        {"type": "date", "paramName": "start_date", "label": "Start", "show": True},
        {"type": "date", "paramName": "end_date", "label": "End", "show": True},
    ]


def panel_widget(name, desc, sub, series_ids, rebase=False, w=20, h=16) -> dict:
    """Multi-series overlay chart off /series_panel."""
    return {
        "name": name,
        "description": desc,
        "category": CATEGORY,
        "subCategory": sub,
        "type": "chart",
        "endpoint": "series_panel",
        "gridData": {"w": w, "h": h},
        "params": [
            {"type": "text", "paramName": "series_ids", "value": series_ids, "show": False},
            {"type": "text", "paramName": "rebase", "value": "true" if rebase else "false", "show": False},
            *_date_params(),
        ],
    }


def latest_widget(name, desc, sub, series_ids, w=20, h=14) -> dict:
    """Latest-reading table off /latest."""
    return {
        "name": name,
        "description": desc,
        "category": CATEGORY,
        "subCategory": sub,
        "type": "table",
        "endpoint": "latest",
        "gridData": {"w": w, "h": h},
        "params": [
            {"type": "text", "paramName": "series_ids", "value": series_ids,
             "label": "Series IDs", "show": True},
        ],
        "data": LATEST_COLUMNS,
    }


def composite_widget(name, desc, sub, index_id, w=20, h=16) -> dict:
    """Single-composite history chart off /composite_history."""
    return {
        "name": name,
        "description": desc,
        "category": CATEGORY,
        "subCategory": sub,
        "type": "chart",
        "endpoint": "composite_history",
        "gridData": {"w": w, "h": h},
        "params": [
            {"type": "text", "paramName": "index_id", "value": index_id, "show": False},
            *_date_params(),
        ],
    }


def endpoint_widget(name, desc, sub, endpoint, wtype="table", w=20, h=16, params=None) -> dict:
    return {
        "name": name,
        "description": desc,
        "category": CATEGORY,
        "subCategory": sub,
        "type": wtype,
        "endpoint": endpoint,
        "gridData": {"w": w, "h": h},
        "params": params or [],
    }


def layout(items) -> list[dict]:
    """items: list of (widget_id, x, y, w, h)."""
    return [{"i": i, "x": x, "y": y, "w": w, "h": h} for (i, x, y, w, h) in items]


def app(name, desc, tab_id, tab_name, items, groups=None) -> dict:
    a = {
        "name": name,
        "description": desc,
        "img": "", "img_dark": "", "img_light": "",
    }
    if groups:
        a["groups"] = groups
    a["tabs"] = {"tabs": {tab_name: {"id": tab_id, "name": tab_name, "layout": layout(items)}}}
    return a


# --------------------------------------------------------------------------- #
# NEW WIDGETS
# --------------------------------------------------------------------------- #
NEW_WIDGETS: dict[str, dict] = {
    # ---- Equities ----
    "lhm_eq_indices": panel_widget(
        "Equities — Index Map (rebased)",
        "SPY / QQQ / IWM / EFA / EEM rebased to 100. Large vs tech vs small vs intl vs EM.",
        "Equities", "SPY_Close,QQQ_Close,IWM_Close,EFA_Close,EEM_Close", rebase=True),
    "lhm_eq_sectors": panel_widget(
        "Equities — Sector Rotation (rebased)",
        "GICS sector ETFs rebased to 100. Relative leadership across the eleven sectors.",
        "Equities",
        "XLK_Close,XLF_Close,XLE_Close,XLV_Close,XLI_Close,XLY_Close,XLP_Close,XLU_Close,XLB_Close",
        rebase=True),
    "lhm_eq_tiles": latest_widget(
        "Equities — Tape & Internals",
        "S&P level, VIX, % above 200d, RSI, Z-RoC, AAII spread. Pillar 11/12 read.",
        "Equities",
        "SPX_Close,VIXCLS,SPX_PCT_ABOVE_200D,SPX_RSI_14d,SPX_Z_RoC_63d,AAII_Bull_Bear_Spread"),
    "lhm_eq_sector_tiles": latest_widget(
        "Equities — Sector Levels",
        "Latest close for each GICS sector ETF.",
        "Equities",
        "XLK_Close,XLF_Close,XLE_Close,XLV_Close,XLI_Close,XLY_Close,XLP_Close,XLU_Close,XLB_Close"),

    # ---- Rates ----
    "lhm_rates_curve": panel_widget(
        "Rates — Curve Slope",
        "10Y-2Y and 10Y-3M spreads. Inversion and re-steepening.",
        "Rates", "T10Y2Y,T10Y3M", rebase=False, h=14),
    "lhm_rates_real": panel_widget(
        "Rates — Real Yield & Breakeven",
        "10Y TIPS real yield and 10Y breakeven inflation.",
        "Rates", "DFII10,T10YIE", rebase=False, h=14),
    "lhm_rates_tiles": latest_widget(
        "Rates — Curve & Policy",
        "Curve anchors, spreads, real yield, breakeven, mortgage, SOFR, EFFR.",
        "Rates",
        "DGS2,DGS5,DGS10,DGS30,T10Y2Y,T10Y3M,DFII10,T10YIE,MORTGAGE30US,SOFR,EFFR", h=15),
    "lhm_treasury_auctions": endpoint_widget(
        "Rates — Treasury Auction Quality",
        "10Y tail, bid-to-cover, indirect share, bills share, weighted-avg maturity.",
        "Rates", "treasury_auctions", wtype="chart", h=15, params=_date_params()),

    # ---- Credit ----
    "lhm_credit_etfs": panel_widget(
        "Credit — HY vs IG ETFs (rebased)",
        "HYG and LQD rebased to 100. Price-return proxy for high-yield vs investment-grade.",
        "Credit", "HYG_Close,LQD_Close", rebase=True),
    "lhm_clg_history": composite_widget(
        "Credit — Credit-Labor Gap (CLG)",
        "CLG composite over history. Spreads vs labor fragility. <-1.0 = spreads ignoring labor.",
        "Credit", "CLG"),
    "lhm_credit_tiles": latest_widget(
        "Credit — Spreads & ETFs",
        "HY OAS, IG OAS, and the HYG / LQD closes.",
        "Credit", "BAMLH0A0HYM2,BAMLC0A0CM,HYG_Close,LQD_Close", h=15),

    # ---- Currencies ----
    "lhm_fx_dollar": panel_widget(
        "Currencies — Dollar Indices",
        "Trade-weighted broad dollar and advanced-foreign-economies dollar.",
        "Currencies", "DTWEXBGS,DTWEXAFEGS", rebase=False),
    "lhm_fx_majors": panel_widget(
        "Currencies — Majors (rebased)",
        "EUR, GBP, JPY, CAD, CNY vs USD rebased to 100. Quote conventions vary; read moves, not levels.",
        "Currencies", "DEXUSEU,DEXUSUK,DEXJPUS,DEXCAUS,DEXCHUS", rebase=True),
    "lhm_fx_tiles": latest_widget(
        "Currencies — Spot Board",
        "Broad dollar plus the major USD pairs.",
        "Currencies", "DTWEXBGS,DEXUSEU,DEXUSUK,DEXJPUS,DEXCAUS,DEXMXUS,DEXCHUS", w=40, h=13),

    # ---- Commodities ----
    "lhm_cmdty_energy": panel_widget(
        "Commodities — Energy",
        "WTI and Brent crude, dollars per barrel.",
        "Commodities", "DCOILWTICO,DCOILBRENTEU", rebase=False),
    "lhm_cmdty_metals": panel_widget(
        "Commodities — Metals (rebased)",
        "Gold, silver, and gold miners rebased to 100.",
        "Commodities", "GLD_Close,SLV_Close,GDX_Close", rebase=True),
    "lhm_cmdty_vol": panel_widget(
        "Commodities — Implied Vol",
        "CBOE gold (GVZ) and crude oil (OVX) volatility indices.",
        "Commodities", "GVZCLS,OVXCLS", rebase=False, h=14),
    "lhm_cmdty_tiles": latest_widget(
        "Commodities — Board",
        "WTI, Brent, gold, silver, copper, retail gasoline.",
        "Commodities", "DCOILWTICO,DCOILBRENTEU,GLD_Close,SLV_Close,PCOPPUSDM,GASREGW", h=14),

    # ---- Crypto ----
    "lhm_crypto_majors": panel_widget(
        "Crypto — Majors (rebased)",
        "BTC, ETH, SOL rebased to 100. Relative performance across the majors.",
        "Crypto", "CRYPTO_BTC_PRICE,CRYPTO_ETH_PRICE,CRYPTO_SOL_PRICE", rebase=True, w=40, h=16),
    "lhm_crypto_cdli": composite_widget(
        "Crypto — DeFi Liquidity (CDLI)",
        "Crypto DeFi Liquidity composite. Free-data on-chain liquidity read.",
        "Crypto", "CRYPTO_DEFI_LIQUIDITY", h=14),
    "lhm_crypto_sli": composite_widget(
        "Crypto — Stablecoin Liquidity (SLI)",
        "Stablecoin Liquidity Impulse. Dollar liquidity entering / leaving the chain.",
        "Crypto", "SLI", h=14),
    "lhm_crypto_tiles": latest_widget(
        "Crypto — Majors Board",
        "BTC / ETH / SOL price and BTC / ETH market cap.",
        "Crypto", "CRYPTO_BTC_PRICE,CRYPTO_ETH_PRICE,CRYPTO_SOL_PRICE,CRYPTO_BTC_MCAP,CRYPTO_ETH_MCAP",
        w=40, h=12),

    # ---- Risk Desk (sixth primary) ----
    "lhm_risk_model": endpoint_widget(
        "Risk — Ensemble Output",
        "Recession probability, ensemble risk, warning level, allocation multiplier, liquidity stage.",
        "Risk", "risk_model", wtype="table", w=20, h=16,
        params=[]),
    "lhm_recprob_history": composite_widget(
        "Risk — Recession Probability",
        "REC_PROB over history. 6-12 month forward recession odds from the ensemble.",
        "Risk", "REC_PROB"),
}

# Attach table columns to the risk-model table widget.
NEW_WIDGETS["lhm_risk_model"]["data"] = {
    "table": {
        "showAll": True,
        "columnsDefs": [
            {"field": "index_id", "headerName": "Model", "pinned": "left", "width": 200},
            {"field": "as_of", "headerName": "As Of", "cellDataType": "date", "width": 120},
            {"field": "value", "headerName": "Value", "cellDataType": "number", "width": 120},
            {"field": "status", "headerName": "Status", "width": 160},
        ],
    }
}


# --------------------------------------------------------------------------- #
# NEW APPS
# --------------------------------------------------------------------------- #
NEW_APPS: dict[str, dict] = {
    "lhm_home": app(
        "00 The Watch",
        "The cover. Where the whole framework stands right now — health, engine regime, the "
        "Diagnostic Dozen heatmap, the risk-model output, MRI history, and every composite's latest read.",
        "watch", "The Watch",
        [
            ("lhm_health", 0, 0, 40, 5),
            ("lhm_engine_summary", 0, 5, 20, 12),
            ("lhm_pillar_heatmap", 20, 5, 20, 20),
            ("lhm_risk_model", 0, 17, 20, 12),
            ("lhm_mri_history", 0, 29, 20, 15),
            ("lhm_composites_latest", 20, 25, 20, 19),
        ],
    ),
    "lhm_risk": app(
        "06 The Risk Desk",
        "The risk screen. Recession probability and the ensemble risk model on one side, MRI and "
        "the pillar heatmap on the other, every composite's latest reading underneath.",
        "risk", "Risk Desk",
        [
            ("lhm_risk_model", 0, 0, 20, 16),
            ("lhm_recprob_history", 20, 0, 20, 16),
            ("lhm_mri_history", 0, 16, 20, 15),
            ("lhm_pillar_heatmap", 20, 16, 20, 15),
            ("lhm_composites_latest", 0, 31, 40, 15),
        ],
    ),
    "lhm_equities": app(
        "19 Equities",
        "Equity asset class. Index map and sector rotation rebased to 100, market breadth and AAII "
        "sentiment underneath, tape internals and sector levels as boards.",
        "equities", "Equities",
        [
            ("lhm_eq_indices", 0, 0, 20, 16),
            ("lhm_eq_sectors", 20, 0, 20, 16),
            ("lhm_breadth_panel", 0, 16, 20, 15),
            ("lhm_sentiment_panel", 20, 16, 20, 15),
            ("lhm_eq_tiles", 0, 31, 20, 12),
            ("lhm_eq_sector_tiles", 20, 31, 20, 12),
        ],
    ),
    "lhm_rates": app(
        "20 Rates",
        "Rates asset class. Treasury curve plus mortgage, curve slope, real yield and breakeven, the "
        "curve/policy board, and Treasury auction quality.",
        "rates", "Rates",
        [
            ("lhm_rates_panel", 0, 0, 40, 16),
            ("lhm_rates_curve", 0, 16, 20, 14),
            ("lhm_rates_real", 20, 16, 20, 14),
            ("lhm_rates_tiles", 0, 30, 20, 15),
            ("lhm_treasury_auctions", 20, 30, 20, 15),
        ],
    ),
    "lhm_credit": app(
        "21 Credit",
        "Credit asset class. HY and IG option-adjusted spreads, HY vs IG ETFs rebased, the "
        "Credit-Labor Gap composite, and the spread/ETF board.",
        "credit", "Credit",
        [
            ("lhm_credit_panel", 0, 0, 20, 16),
            ("lhm_credit_etfs", 20, 0, 20, 16),
            ("lhm_clg_history", 0, 16, 20, 15),
            ("lhm_credit_tiles", 20, 16, 20, 15),
        ],
    ),
    "lhm_currencies": app(
        "22 Currencies",
        "Currency asset class. Trade-weighted dollar indices, the majors rebased to 100, and the spot board.",
        "currencies", "Currencies",
        [
            ("lhm_fx_dollar", 0, 0, 20, 16),
            ("lhm_fx_majors", 20, 0, 20, 16),
            ("lhm_fx_tiles", 0, 16, 40, 13),
        ],
    ),
    "lhm_commodities": app(
        "23 Commodities",
        "Commodity asset class. Energy (WTI/Brent), metals rebased (gold/silver/miners), gold and oil "
        "implied vol, and the commodity board.",
        "commodities", "Commodities",
        [
            ("lhm_cmdty_energy", 0, 0, 20, 16),
            ("lhm_cmdty_metals", 20, 0, 20, 16),
            ("lhm_cmdty_vol", 0, 16, 20, 14),
            ("lhm_cmdty_tiles", 20, 16, 20, 14),
        ],
    ),
    "lhm_crypto": app(
        "24 Crypto",
        "Crypto asset class. BTC/ETH/SOL rebased, the DeFi Liquidity and Stablecoin Liquidity "
        "composites, and the majors board.",
        "crypto", "Crypto",
        [
            ("lhm_crypto_majors", 0, 0, 40, 16),
            ("lhm_crypto_cdli", 0, 16, 20, 14),
            ("lhm_crypto_sli", 20, 16, 20, 14),
            ("lhm_crypto_tiles", 0, 30, 40, 12),
        ],
    ),
}

# Renumber the twelve pillar apps from "06 .." to "07 .." so they slot after
# the six primaries (00 Watch is the cover, 01-06 are primaries).
PILLAR_RENUMBER = {
    "p01_labor": "07 Labor — Pillar 1",
    "p02_prices": "08 Prices — Pillar 2",
    "p03_growth": "09 Growth — Pillar 3",
    "p04_housing": "10 Housing — Pillar 4",
    "p05_consumer": "11 Consumer — Pillar 5",
    "p06_business": "12 Business — Pillar 6",
    "p07_trade": "13 Trade — Pillar 7",
    "p08_government": "14 Government — Pillar 8",
    "p09_financial": "15 Financial — Pillar 9",
    "p10_plumbing": "16 Plumbing — Pillar 10",
    "p11_structure": "17 Structure — Pillar 11",
    "p12_sentiment": "18 Sentiment — Pillar 12",
}

# Desired display order of all 25 apps.
ORDER = [
    "lhm_home",
    "lhm_pulse", "lhm_asset_flow", "lhm_chain", "lhm_real_check", "lhm_divergence",
    "lhm_risk",
    "p01_labor", "p02_prices", "p03_growth", "p04_housing", "p05_consumer", "p06_business",
    "p07_trade", "p08_government", "p09_financial", "p10_plumbing", "p11_structure", "p12_sentiment",
    "lhm_equities", "lhm_rates", "lhm_credit", "lhm_currencies", "lhm_commodities", "lhm_crypto",
]


def main() -> None:
    widgets = json.loads(WIDGETS_PATH.read_text())
    apps = json.loads(APPS_PATH.read_text())

    # Merge widgets (new keys + overwrite our own).
    widgets.update(NEW_WIDGETS)

    # Merge apps + renumber pillars.
    apps.update(NEW_APPS)
    for k, new_name in PILLAR_RENUMBER.items():
        if k in apps:
            apps[k]["name"] = new_name

    # Reorder apps to ORDER, appending any stragglers at the end.
    ordered = {k: apps[k] for k in ORDER if k in apps}
    for k, v in apps.items():
        if k not in ordered:
            ordered[k] = v

    WIDGETS_PATH.write_text(json.dumps(widgets, indent=2, ensure_ascii=False) + "\n")
    APPS_PATH.write_text(json.dumps(ordered, indent=2, ensure_ascii=False) + "\n")

    print(f"widgets.json: {len(widgets)} widgets")
    print(f"apps.json:    {len(ordered)} apps")
    missing = [k for k in ORDER if k not in ordered]
    if missing:
        print("MISSING from apps:", missing)
    # Sanity: every widget referenced by every app must exist.
    refs = set()
    for a in ordered.values():
        for tab in a.get("tabs", {}).get("tabs", {}).values():
            for item in tab.get("layout", []):
                refs.add(item["i"])
    dangling = sorted(r for r in refs if r not in widgets)
    print("dangling widget refs:", dangling or "none")


if __name__ == "__main__":
    main()
