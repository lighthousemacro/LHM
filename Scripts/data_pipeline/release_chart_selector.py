#!/usr/bin/env python3
"""
LIGHTHOUSE MACRO - RELEASE-AWARE CHART SELECTOR
=================================================
Maps FRED economic releases to relevant chart functions.
Picks charts for the morning brief based on:
  1. What released yesterday (data just dropped)
  2. What releases today (what's coming)
  3. What releases tomorrow (preview)
  4. Day-of-week rotation for quiet days

Usage:
    from release_chart_selector import select_charts, fetch_calendar_context
"""

import sys
import os
from datetime import datetime, timedelta

import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lighthouse.config import API_KEYS

# ============================================================
# FRED RELEASE -> CHART MAPPING
# ============================================================
# Maps FRED release names (from fred/releases/dates API) to
# chart function names and pillar context.

RELEASE_CHART_MAP = {
    # ----- PILLAR 1: LABOR -----
    "Employment Situation": {
        "pillar": 1,
        "charts": ["chart_unemployment_rate", "chart_nfp_momentum", "chart_wages", "chart_lfpr"],
        "headline": "Jobs Day",
    },
    "Job Openings and Labor Turnover Survey": {
        "pillar": 1,
        "charts": ["chart_jolts_quits", "chart_jolts_hires_separations"],
        "headline": "JOLTS",
    },
    "Unemployment Insurance Weekly Claims Report": {
        "pillar": 1,
        "charts": ["chart_claims"],
        "headline": "Jobless Claims",
    },

    # ----- PILLAR 2: PRICES -----
    "Consumer Price Index": {
        "pillar": 2,
        "charts": ["chart_cpi_headline_core", "chart_cpi_shelter", "chart_breakevens"],
        "headline": "CPI",
    },
    "Producer Price Index": {
        "pillar": 2,
        "charts": ["chart_cpi_headline_core", "chart_breakevens"],
        "headline": "PPI",
    },
    "Personal Income and Outlays": {
        "pillar": [2, 5],
        "charts": ["chart_pce_core", "chart_income_spending", "chart_saving_rate"],
        "headline": "PCE / Income",
    },

    # ----- PILLAR 3: GROWTH -----
    "Gross Domestic Product": {
        "pillar": 3,
        "charts": ["chart_gdp_growth", "chart_industrial_production"],
        "headline": "GDP",
    },
    "Industrial Production and Capacity Utilization": {
        "pillar": 3,
        "charts": ["chart_industrial_production"],
        "headline": "Industrial Production",
    },
    "Durable Goods Manufacturers' Shipments, Inventories, and Orders": {
        "pillar": [3, 6],
        "charts": ["chart_industrial_production", "chart_ism_pmi"],
        "headline": "Durable Goods",
    },

    # ----- PILLAR 4: HOUSING -----
    "New Residential Construction": {
        "pillar": 4,
        "charts": ["chart_housing_starts", "chart_mortgage_vs_starts"],
        "headline": "Housing Starts",
    },
    "Existing Home Sales": {
        "pillar": 4,
        "charts": ["chart_housing_starts", "chart_mortgage_vs_starts"],
        "headline": "Existing Home Sales",
    },
    "New Residential Sales": {
        "pillar": 4,
        "charts": ["chart_housing_starts", "chart_mortgage_vs_starts"],
        "headline": "New Home Sales",
    },
    "S&P/Case-Shiller Home Price Indices": {
        "pillar": 4,
        "charts": ["chart_case_shiller", "chart_housing_starts"],
        "headline": "Case-Shiller",
    },

    # ----- PILLAR 5: CONSUMER -----
    "Advance Monthly Sales for Retail and Food Services": {
        "pillar": 5,
        "charts": ["chart_retail_sales", "chart_saving_rate"],
        "headline": "Retail Sales",
    },
    "Consumer Credit": {
        "pillar": 5,
        "charts": ["chart_consumer_credit", "chart_saving_rate"],
        "headline": "Consumer Credit",
    },
    "University of Michigan: Surveys of Consumers": {
        "pillar": 5,
        "charts": ["chart_consumer_sentiment"],
        "headline": "UMich Sentiment",
    },

    # ----- PILLAR 6: BUSINESS -----
    "ISM Manufacturing: PMI Composite Index": {
        "pillar": 6,
        "charts": ["chart_ism_pmi", "chart_industrial_production"],
        "headline": "ISM Manufacturing",
    },

    # ----- PILLAR 8: GOVERNMENT / RATES -----
    "Treasury Statement": {
        "pillar": 8,
        "charts": ["chart_yield_curve", "chart_term_premium"],
        "headline": "Treasury Statement",
    },
    "Federal Open Market Committee": {
        "pillar": 8,
        "charts": ["chart_yield_curve", "chart_fed_balance_sheet", "chart_term_premium"],
        "headline": "FOMC",
    },
    "Senior Loan Officer Opinion Survey on Bank Lending Practices": {
        "pillar": 9,
        "charts": ["chart_hy_oas", "chart_credit_labor_gap"],
        "headline": "SLOOS",
    },

    # ----- PILLAR 9: FINANCIAL -----
    "H.15 Selected Interest Rates": {
        "pillar": 9,
        "charts": ["chart_yield_curve", "chart_hy_oas"],
        "headline": "Interest Rates",
    },

    # ----- PILLAR 7: TRADE -----
    "U.S. International Trade in Goods and Services": {
        "pillar": 7,
        "charts": ["chart_trade_balance", "chart_dollar"],
        "headline": "Trade Balance",
    },
    "U.S. Import and Export Price Indexes": {
        "pillar": 7,
        "charts": ["chart_dollar", "chart_trade_balance"],
        "headline": "Import/Export Prices",
    },
}

# Always-on charts (slots 1-2)
ALWAYS_ON = ["chart_mri", "chart_spx"]

# Day-of-week rotation for quiet days (no major release)
# Cycles through different pillars so the brief never feels stale
DOW_ROTATION = {
    0: {  # Monday: Structure + Sentiment (weekend positioning shifts)
        "label": "Weekly Check: Structure & Sentiment",
        "charts": ["chart_breadth", "chart_vix", "chart_aaii"],
    },
    1: {  # Tuesday: Plumbing + Credit
        "label": "Rotation: Plumbing & Credit",
        "charts": ["chart_fed_balance_sheet", "chart_hy_oas", "chart_sofr_iorb"],
    },
    2: {  # Wednesday: Rates + Government
        "label": "Rotation: Rates & Fiscal",
        "charts": ["chart_yield_curve", "chart_term_premium", "chart_real_rates"],
    },
    3: {  # Thursday: Labor context (claims always weekly)
        "label": "Weekly Check: Labor & Claims",
        "charts": ["chart_claims", "chart_unemployment_rate", "chart_jolts_quits"],
    },
    4: {  # Friday: Dollar + Trade + Broad view
        "label": "Rotation: Trade & Dollar",
        "charts": ["chart_dollar", "chart_trade_balance", "chart_breakevens"],
    },
    5: {  # Saturday (unlikely but handle)
        "label": "Weekly Review",
        "charts": ["chart_yield_curve", "chart_hy_oas", "chart_vix"],
    },
    6: {  # Sunday
        "label": "Weekly Review",
        "charts": ["chart_breadth", "chart_saving_rate", "chart_dollar"],
    },
}

# Maximum charts in the brief
MAX_CHARTS = 12


# ============================================================
# FRED CALENDAR FETCH
# ============================================================

def fetch_calendar_context() -> dict:
    """
    Fetch FRED releases for yesterday, today, and next 3 days.

    Returns:
        {"yesterday": [...], "today": [...], "upcoming": [...]}
        Each item: {"name": str, "date": str}
    """
    try:
        api_key = API_KEYS.get("FRED", "")
        if not api_key:
            return {"yesterday": [], "today": [], "upcoming": []}

        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        end = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")
        today_str = datetime.now().strftime("%Y-%m-%d")

        url = "https://api.stlouisfed.org/fred/releases/dates"
        params = {
            "api_key": api_key,
            "file_type": "json",
            "realtime_start": yesterday,
            "realtime_end": end,
            "include_release_dates_with_no_data": "true",
            "sort_order": "asc",
        }

        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()

        yesterday_releases = []
        today_releases = []
        upcoming_releases = []
        seen = set()

        for item in data.get("release_dates", []):
            name = item.get("release_name", "")
            date = item.get("date", "")
            key = f"{name}_{date}"
            if key in seen:
                continue
            seen.add(key)

            entry = {"name": name, "date": date}
            if date == yesterday:
                yesterday_releases.append(entry)
            elif date == today_str:
                today_releases.append(entry)
            else:
                upcoming_releases.append(entry)

        return {
            "yesterday": yesterday_releases,
            "today": today_releases,
            "upcoming": upcoming_releases,
        }
    except Exception as e:
        print(f"  FRED calendar fetch failed: {e}")
        return {"yesterday": [], "today": [], "upcoming": []}


# ============================================================
# CHART SELECTION LOGIC
# ============================================================

def select_charts(calendar_ctx: dict) -> list:
    """
    Select charts based on release calendar context.

    Returns ordered list of:
        {"func_name": str, "context": str, "priority": int}
    """
    selected = []
    seen_funcs = set()

    # Slot 1-2: Always-on
    for func_name in ALWAYS_ON:
        selected.append({
            "func_name": func_name,
            "context": "Always On",
            "priority": 0,
        })
        seen_funcs.add(func_name)

    # Process releases: yesterday first (highest priority), then today, then upcoming
    release_groups = [
        ("yesterday", calendar_ctx.get("yesterday", []), 1),
        ("today", calendar_ctx.get("today", []), 2),
        ("upcoming", calendar_ctx.get("upcoming", []), 3),
    ]

    release_headlines = []

    for time_label, releases, priority in release_groups:
        for release in releases:
            name = release["name"]
            date = release["date"]

            # Check if this release maps to charts
            for release_key, mapping in RELEASE_CHART_MAP.items():
                if release_key.lower() in name.lower() or name.lower() in release_key.lower():
                    headline = mapping["headline"]
                    if time_label == "yesterday":
                        context = f"Released Yesterday: {headline}"
                    elif time_label == "today":
                        context = f"Today: {headline}"
                    else:
                        context = f"Upcoming: {headline} ({date})"

                    release_headlines.append(context)

                    for func_name in mapping["charts"]:
                        if func_name not in seen_funcs and len(selected) < MAX_CHARTS:
                            selected.append({
                                "func_name": func_name,
                                "context": context,
                                "priority": priority,
                            })
                            seen_funcs.add(func_name)
                    break

    # Fill remaining slots from day-of-week rotation
    dow = datetime.now().weekday()
    rotation = DOW_ROTATION.get(dow, DOW_ROTATION[0])

    if len(selected) < 6:
        for func_name in rotation["charts"]:
            if func_name not in seen_funcs and len(selected) < MAX_CHARTS:
                selected.append({
                    "func_name": func_name,
                    "context": rotation["label"],
                    "priority": 5,
                })
                seen_funcs.add(func_name)

    return selected, release_headlines


# ============================================================
# CLI TEST
# ============================================================

if __name__ == "__main__":
    print("Fetching FRED calendar context...")
    ctx = fetch_calendar_context()

    print(f"\n  Yesterday: {len(ctx['yesterday'])} releases")
    for r in ctx["yesterday"]:
        mapped = "***" if any(k.lower() in r["name"].lower() or r["name"].lower() in k.lower()
                              for k in RELEASE_CHART_MAP) else ""
        print(f"    {r['date']} | {r['name']} {mapped}")

    print(f"\n  Today: {len(ctx['today'])} releases")
    for r in ctx["today"]:
        mapped = "***" if any(k.lower() in r["name"].lower() or r["name"].lower() in k.lower()
                              for k in RELEASE_CHART_MAP) else ""
        print(f"    {r['date']} | {r['name']} {mapped}")

    print(f"\n  Upcoming: {len(ctx['upcoming'])} releases")
    for r in ctx["upcoming"][:10]:
        mapped = "***" if any(k.lower() in r["name"].lower() or r["name"].lower() in k.lower()
                              for k in RELEASE_CHART_MAP) else ""
        print(f"    {r['date']} | {r['name']} {mapped}")

    print("\n--- Chart Selection ---")
    charts, headlines = select_charts(ctx)
    for h in headlines:
        print(f"  HEADLINE: {h}")
    for c in charts:
        print(f"  [{c['priority']}] {c['func_name']:35s} | {c['context']}")
