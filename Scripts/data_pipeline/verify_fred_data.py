"""
FRED Data Verification Script — Diagnostic Dozen #6 (Business Pillar)
=====================================================================
Pulls latest values from FRED API for key series and computes YoY%,
capacity utilization levels, and bookings/billings ratios.

Run: python3 Scripts/data_pipeline/verify_fred_data.py

Series verified:
  INDPRO   — Total Industrial Production (YoY%)
  IPMAN    — Manufacturing IP (YoY%)
  TCU      — Total Capacity Utilization (level)
  MCUMFN   — Manufacturing Capacity Utilization (level)
  NEWORDER — Core Capital Goods Orders, nondefense ex-aircraft (YoY%)
  ANXAVS   — Core Capital Goods Shipments, nondefense ex-aircraft (YoY%)
  Bookings/Billings ratio = NEWORDER / ANXAVS (3-month average)
"""

import urllib.request
import json
from datetime import datetime


FRED_API_KEY = "11893c506c07b3b8647bf16cf60586e8"
BASE_URL = "https://api.stlouisfed.org/fred"


def fetch_observations(series_id: str, start_date: str = "2023-01-01") -> dict:
    """Fetch FRED observations as {date_str: value} dict."""
    url = (
        f"{BASE_URL}/series/observations?"
        f"series_id={series_id}&api_key={FRED_API_KEY}"
        f"&file_type=json&observation_start={start_date}"
        f"&sort_order=desc&limit=50"
    )
    req = urllib.request.Request(url, headers={"User-Agent": "LHM/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())
    return {
        o["date"]: float(o["value"])
        for o in data["observations"]
        if o["value"] != "."
    }


def fetch_metadata(series_id: str) -> dict:
    """Fetch FRED series metadata."""
    url = (
        f"{BASE_URL}/series?"
        f"series_id={series_id}&api_key={FRED_API_KEY}"
        f"&file_type=json"
    )
    req = urllib.request.Request(url, headers={"User-Agent": "LHM/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())
    return data["seriess"][0]


def yoy_pct(current: float, year_ago: float) -> float:
    """Year-over-year percent change."""
    return ((current / year_ago) - 1.0) * 100.0


def main():
    series_ids = ["INDPRO", "IPMAN", "TCU", "MCUMFN", "NEWORDER", "ANXAVS"]

    # Draft values for comparison
    draft = {
        "INDPRO": {"value": 2.0, "metric": "YoY%"},
        "IPMAN": {"value": None, "metric": "YoY%"},
        "TCU": {"value": 76.2, "metric": "Level"},
        "MCUMFN": {"value": 75.6, "metric": "Level"},
        "NEWORDER": {"value": 5.9, "metric": "YoY%"},
        "ANXAVS": {"value": 5.6, "metric": "YoY%"},
    }

    print("=" * 95)
    print("FRED DATA VERIFICATION — Diagnostic Dozen #6 (Business Pillar)")
    print(f"Run date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 95)

    all_data = {}
    for sid in series_ids:
        meta = fetch_metadata(sid)
        obs = fetch_observations(sid)
        all_data[sid] = obs

        dates = sorted(obs.keys(), reverse=True)
        latest_date = dates[0]
        latest_val = obs[latest_date]
        latest_dt = datetime.strptime(latest_date, "%Y-%m-%d")
        year_ago_str = latest_dt.replace(year=latest_dt.year - 1).strftime("%Y-%m-%d")
        year_ago_val = obs.get(year_ago_str)

        print(f"\n{'─' * 95}")
        print(f"  {sid}: {meta['title']}")
        print(f"  Last updated: {meta['last_updated']}")
        print(f"  Latest: {latest_date} = {latest_val:,.4f}")

        if sid in ("TCU", "MCUMFN"):
            # Report as level
            computed = round(latest_val, 1)
            draft_val = draft[sid]["value"]
            changed = "YES" if draft_val and abs(computed - draft_val) >= 0.1 else "No"
            print(f"  Level: {computed}%")
            print(f"  Draft: {draft_val}%  |  Changed: {changed}")
        else:
            # Compute YoY%
            if year_ago_val:
                computed = round(yoy_pct(latest_val, year_ago_val), 2)
                print(f"  Year-ago: {year_ago_str} = {year_ago_val:,.4f}")
                print(f"  YoY%: {computed:+.2f}%")
                draft_val = draft[sid]["value"]
                if draft_val is not None:
                    diff = computed - draft_val
                    changed = "YES" if abs(diff) >= 0.1 else "No"
                    print(f"  Draft: {draft_val:+.1f}%  |  Changed: {changed}  |  Diff: {diff:+.2f} pp")
                else:
                    print(f"  Draft: N/A (context only)")
            else:
                print(f"  Year-ago {year_ago_str}: NOT AVAILABLE")

    # Bookings / Billings ratio
    print(f"\n{'═' * 95}")
    print("BOOKINGS / BILLINGS RATIO  (NEWORDER / ANXAVS)")
    print(f"{'═' * 95}")

    orders = all_data["NEWORDER"]
    ships = all_data["ANXAVS"]
    common = sorted(set(orders.keys()) & set(ships.keys()), reverse=True)

    print(f"\n  Monthly ratios:")
    for d in common[:6]:
        r = orders[d] / ships[d]
        print(f"    {d}: {orders[d]:>10,.0f} / {ships[d]:>10,.0f} = {r:.4f}x")

    if len(common) >= 3:
        dates_3m = common[:3]
        avg_o = sum(orders[d] for d in dates_3m) / 3
        avg_s = sum(ships[d] for d in dates_3m) / 3
        ratio_3m = avg_o / avg_s
        print(f"\n  3-month avg ending {dates_3m[0]}:")
        print(f"    Orders avg:    {avg_o:>10,.0f}")
        print(f"    Shipments avg: {avg_s:>10,.0f}")
        print(f"    Ratio:         {ratio_3m:.4f}x")
        print(f"    Draft:         1.28x  |  MAJOR DISCREPANCY — see notes")

    print(f"\n{'═' * 95}")
    print("NOTES")
    print(f"{'═' * 95}")
    print("""
  1. MCU does not exist in FRED. The correct series is TCU (Total Capacity Utilization).
  2. ACDGNO is 'Consumer Durable Goods Orders', NOT core capex shipments.
     The correct shipments series is ANXAVS (Nondefense Capital Goods Ex-Aircraft Shipments).
  3. The draft's 1.28x bookings/billings cannot be reproduced from NEWORDER/ANXAVS.
     Actual ratio runs ~1.00x. Investigate the source of the 1.28x figure.
  4. LEI (Conference Board) is not on FRED. Dec 2025 = 97.6, MoM = -0.2%.
     YoY% ≈ -3.94% (vs Dec 2024 = 101.6). Jan 2026 data delayed by shutdown.
""")


if __name__ == "__main__":
    main()
