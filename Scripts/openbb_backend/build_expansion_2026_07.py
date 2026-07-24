"""
Expansion builder — closes the gap to the published copy (locked 2026-07-19):
"30 dashboards: 12 Pillars + 6 asset classes + 6 Main Street Monitors + 6
Transmission Chain Trackers."

Adds, idempotently (re-run safe, only touches keys it owns):
  1. widgets.json — updates lhm_transmission_chain dropdown to SIX chains
     (backend CHAINS in lhm_backend.py already defines all six).
  2. widgets.json — 12 new sector-monitor widgets (series_panel / latest based,
     all series verified live in Lighthouse_Master.db 2026-07-23).
  3. apps.json — three new tabs on "Pharos — Markets & Main Street":
     Restaurants & Food, Retail, Services & Trades.

Run:
    python Scripts/openbb_backend/build_expansion_2026_07.py
"""

from __future__ import annotations

import json
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent
WIDGETS_PATH = BACKEND_DIR / "widgets.json"
APPS_PATH = BACKEND_DIR / "apps.json"
CATEGORY = "Lighthouse Macro"

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


def _date_params():
    return [
        {"type": "date", "paramName": "start_date", "label": "Start", "show": True},
        {"type": "date", "paramName": "end_date", "label": "End", "show": True},
    ]


def panel(name, desc, series_ids, rebase=False, transform="none", periods=12, w=20, h=15):
    params = [
        {"type": "text", "paramName": "series_ids", "value": series_ids, "show": False},
        {"type": "text", "paramName": "rebase", "value": "true" if rebase else "false", "show": False},
    ]
    if transform != "none":
        params.append({"type": "text", "paramName": "transform", "value": transform, "show": False})
        params.append({"type": "number", "paramName": "periods", "value": periods, "show": False})
    params.extend(_date_params())
    return {
        "name": name, "description": desc, "category": CATEGORY,
        "subCategory": "Operators", "type": "chart", "endpoint": "series_panel",
        "gridData": {"w": w, "h": h}, "params": params,
    }


def tiles(name, desc, series_ids, w=40, h=12):
    return {
        "name": name, "description": desc, "category": CATEGORY,
        "subCategory": "Operators", "type": "table", "endpoint": "latest",
        "gridData": {"w": w, "h": h},
        "params": [{"type": "text", "paramName": "series_ids", "value": series_ids,
                    "label": "Series IDs", "show": True}],
        "data": LATEST_COLUMNS,
    }


# --------------------------------------------------------------------------- #
# Sector monitor widgets (all series verified in Lighthouse_Master.db)
# --------------------------------------------------------------------------- #

SECTOR_WIDGETS = {
    # -- Restaurants & Food Service -----------------------------------------
    "lhm_rest_sales": panel(
        "Restaurants — Sales Pulse",
        "Food services & drinking places vs restaurants & eating places, YoY. Is the table still full?",
        "RSFSDP,MRTSSM7225USN", transform="yoy", periods=12),
    "lhm_rest_jobs": panel(
        "Restaurants — Staffing",
        "Leisure & hospitality employment, YoY. The staffing side of the dining room.",
        "USLAH", transform="yoy", periods=12),
    "lhm_rest_quits": panel(
        "Restaurants — Quit Signal",
        "JOLTS quits rate, leisure & hospitality. The sector's truth serum: nobody quits into a bad market.",
        "JTS7000QUR"),
    "lhm_rest_tiles": tiles(
        "Restaurants — Latest Board",
        "Latest reads across the restaurant complex.",
        "RSFSDP,MRTSSM7225USN,USLAH,JTS7000QUR"),

    # -- Retail --------------------------------------------------------------
    "lhm_retail_sales": panel(
        "Retail — Sales Mix",
        "Headline retail vs ex-food-services vs nonstore (e-commerce proxy), YoY. Where the wallet actually goes.",
        "RSAFS,RSXFS,RSNSR", transform="yoy", periods=12),
    "lhm_retail_staples": panel(
        "Retail — Staples vs Fuel",
        "Grocery vs gasoline station sales, YoY. The non-discretionary floor under the print.",
        "RSGCS,RSGASS", transform="yoy", periods=12),
    "lhm_retail_jobs": panel(
        "Retail — Jobs & Quits",
        "Retail trade employment YoY against the JOLTS retail quits rate.",
        "USTRADE", transform="yoy", periods=12),
    "lhm_retail_tiles": tiles(
        "Retail — Latest Board",
        "Latest reads across the retail complex.",
        "RSAFS,RSXFS,RSNSR,RSGCS,RSGASS,USTRADE,JTS4400QUR"),

    # -- Services & Trades ---------------------------------------------------
    "lhm_svc_ism": panel(
        "Services — ISM Complex",
        "ISM Services: business activity, new orders, employment. The service economy's forward gauges.",
        "TV_USNMBA,TV_USNMNO,TV_USNMEMP"),
    "lhm_svc_construction": panel(
        "Trades — Construction Pulse",
        "Construction employment YoY. The trades' hiring cycle.",
        "USCONS", transform="yoy", periods=12),
    "lhm_svc_spend": panel(
        "Trades — Construction Spending",
        "Total construction spending, YoY. The pipeline behind the hiring.",
        "TV_USCONSTS", transform="yoy", periods=12),
    "lhm_svc_tiles": tiles(
        "Services & Trades — Latest Board",
        "Latest reads across services and the trades.",
        "TV_USNMBA,TV_USNMNO,TV_USNMEMP,TV_USNMPR,USCONS,TV_USCONSTS"),
}

CHAIN_OPTIONS = [
    {"value": "plumbing_credit_labor", "label": "Plumbing → Credit → Labor"},
    {"value": "rates_housing_consumer", "label": "Rates → Housing → Consumer"},
    {"value": "sentiment_structure_risk", "label": "Sentiment → Structure → Risk"},
    {"value": "dollar_trade_growth", "label": "Dollar → Trade → Growth"},
    {"value": "fiscal_term_premium_housing", "label": "Fiscal → Term Premium → Housing"},
    {"value": "labor_consumer_business", "label": "Labor → Consumer → Business"},
]

NEW_TABS = {
    "restaurants": {
        "id": "restaurants", "name": "Restaurants & Food",
        "layout": [
            {"i": "lhm_rest_sales", "x": 0, "y": 0, "w": 20, "h": 15},
            {"i": "lhm_rest_jobs", "x": 20, "y": 0, "w": 20, "h": 15},
            {"i": "lhm_rest_quits", "x": 0, "y": 15, "w": 20, "h": 15},
            {"i": "lhm_rest_tiles", "x": 20, "y": 15, "w": 20, "h": 15},
        ],
    },
    "retail": {
        "id": "retail", "name": "Retail",
        "layout": [
            {"i": "lhm_retail_sales", "x": 0, "y": 0, "w": 20, "h": 15},
            {"i": "lhm_retail_staples", "x": 20, "y": 0, "w": 20, "h": 15},
            {"i": "lhm_retail_jobs", "x": 0, "y": 15, "w": 20, "h": 15},
            {"i": "lhm_retail_tiles", "x": 20, "y": 15, "w": 20, "h": 15},
        ],
    },
    "services_trades": {
        "id": "services_trades", "name": "Services & Trades",
        "layout": [
            {"i": "lhm_svc_ism", "x": 0, "y": 0, "w": 20, "h": 15},
            {"i": "lhm_svc_construction", "x": 20, "y": 0, "w": 20, "h": 15},
            {"i": "lhm_svc_spend", "x": 0, "y": 15, "w": 20, "h": 15},
            {"i": "lhm_svc_tiles", "x": 20, "y": 15, "w": 20, "h": 15},
        ],
    },
}


def main() -> None:
    widgets = json.loads(WIDGETS_PATH.read_text())
    apps = json.loads(APPS_PATH.read_text())

    # 1. Chain dropdown → six chains
    tc = widgets.get("lhm_transmission_chain")
    if tc:
        for p in tc.get("params", []):
            if p.get("paramName") == "chain_id":
                p["options"] = CHAIN_OPTIONS
                p["description"] = " / ".join(o["value"] for o in CHAIN_OPTIONS)

    # 2. Sector widgets (own-key overwrite)
    widgets.update(SECTOR_WIDGETS)

    # 3. Tabs on Markets & Main Street
    for a in apps:
        if a.get("name", "").endswith("Markets & Main Street"):
            a["tabs"].update(NEW_TABS)
            a["description"] = (
                "The board. Six asset classes from equities to crypto, and the "
                "six-monitor Main Street suite built for operators."
            )

    WIDGETS_PATH.write_text(json.dumps(widgets, indent=1))
    APPS_PATH.write_text(json.dumps(apps, indent=1))
    print(f"widgets: {len(widgets)} total ({len(SECTOR_WIDGETS)} sector widgets ensured)")
    print(f"chains in dropdown: {len(CHAIN_OPTIONS)}")
    for a in apps:
        print(f"app: {a['name']} — {len(a['tabs'])} tabs")


if __name__ == "__main__":
    main()
