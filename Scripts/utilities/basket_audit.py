"""
Basket audit: compare the components used in pillar_multiasset_optimization.json
against the full universe of series in each pillar sub-DB.

Output: structured markdown per pillar listing in-basket, in-DB-not-in-basket,
and a noise filter for clearly-irrelevant series (discontinued regional CPIs,
FOMC SEP projections, etc.).
"""

import json
import sqlite3
from pathlib import Path

PILLAR_DBS = Path("/Users/bob/LHM/Data/databases/pillars")
OPT_JSON = Path("/Users/bob/LHM/Outputs/mri_optimization/pillar_multiasset_optimization.json")
OUT_PATH = Path("/Users/bob/LHM/Outputs/mri_optimization/PILLAR_BASKET_AUDIT.md")

PILLAR_DB_MAP = {
    "LPI": "Pillar_01_Labor.db",
    "PCI": "Pillar_02_Prices.db",
    "GCI": "Pillar_03_Growth.db",
    "HCI": "Pillar_04_Housing.db",
    "CCI": "Pillar_05_Consumer.db",
    "BCI": "Pillar_06_Business.db",
    "TCI": "Pillar_07_Trade.db",
    "GCI_Gov": "Pillar_08_Government.db",
    "FCI": "Pillar_09_Financial.db",
    "LCI": "Pillar_10_Plumbing.db",
    "MSI": "Pillar_11_Structure.db",
    "SPI": "Pillar_12_Sentiment.db",
}

PILLAR_FULL_NAME = {
    "LPI": "Labor Pressure Index",
    "PCI": "Price Conditions Index",
    "GCI": "Growth Conditions Index",
    "HCI": "Housing Conditions Index",
    "CCI": "Consumer Conditions Index",
    "BCI": "Business Conditions Index",
    "TCI": "Trade Conditions Index",
    "GCI_Gov": "Government Conditions Index",
    "FCI": "Financial Conditions Index",
    "LCI": "Liquidity Cushion Index",
    "MSI": "Market Structure Index",
    "SPI": "Sentiment & Positioning Index",
}

NOISE_PATTERNS = [
    # FOMC SEP projections (forecasts, not data)
    "CTH", "CTL", "CTM", "CTLLR", "CTMLR",
    "MD", "MDLR",
    "RH", "RM", "RHLR", "RMLR", "RLLR",
    # Discontinued regional series
    "CUURA",
    # Vintage / research variants
    "CPIE",
    # Single-city CPIs (we want national, not local)
    # Frequency junk
]

NOISE_TITLE_KEYWORDS = [
    "FOMC Summary",
    "Longer Run",
    "DISCONTINUED",
    "(MSA)",
    "(CMSA)",
    "Research Consumer Price Index:",
]


def is_noise(series_id: str, title: str) -> bool:
    if title:
        for kw in NOISE_TITLE_KEYWORDS:
            if kw in title:
                return True
    return False


def get_pillar_series(db_path: Path) -> list[dict]:
    conn = sqlite3.connect(db_path)
    cur = conn.execute(
        "SELECT series_id, title, source, frequency, units, obs_count, "
        "last_value_date FROM series_meta ORDER BY series_id"
    )
    cols = [d[0] for d in cur.description]
    rows = [dict(zip(cols, r)) for r in cur.fetchall()]
    conn.close()
    return rows


def main():
    with open(OPT_JSON) as f:
        opt = json.load(f)

    out = []
    out.append("# Pillar Basket Audit\n")
    out.append(f"*Generated: 2026-04-30 from `{OPT_JSON.name}` against pillar sub-DBs*\n")
    out.append("Compares components used in the latest optimization run against the full ")
    out.append("universe of series in each pillar sub-DB. 'Noise' series ")
    out.append("(FOMC SEP projections, discontinued regional CPIs, vintage research variants) ")
    out.append("are filtered out of the candidate pool.\n\n")

    summary_rows = []

    for pillar_key, db_name in PILLAR_DB_MAP.items():
        db_path = PILLAR_DBS / db_name
        pillar_data = opt["pillars"].get(pillar_key, {})
        in_basket = set()
        if "best_target" in pillar_data:
            in_basket = set(pillar_data["best_target"]["optimized_weights"].keys())
        else:
            # Aggregate all targets tested
            for t in pillar_data.get("targets_tested", []):
                in_basket.update(t.get("optimized_weights", {}).keys())

        all_series = get_pillar_series(db_path)
        signal_series = [
            s for s in all_series
            if not is_noise(s["series_id"], s["title"] or "")
        ]
        noise_series = [
            s for s in all_series
            if is_noise(s["series_id"], s["title"] or "")
        ]

        in_basket_rows = [s for s in signal_series if s["series_id"] in in_basket]
        not_in_basket = [s for s in signal_series if s["series_id"] not in in_basket]

        full_name = PILLAR_FULL_NAME[pillar_key]
        out.append(f"\n## {full_name} ({pillar_key})\n")
        out.append(f"- DB: `{db_name}`\n")
        out.append(f"- Total series in DB: **{len(all_series)}**\n")
        out.append(f"- Signal candidates (after noise filter): **{len(signal_series)}**\n")
        out.append(f"- In current optimization basket: **{len(in_basket_rows)}**\n")
        out.append(f"- In DB but NOT in basket: **{len(not_in_basket)}**\n\n")

        out.append("### Currently in basket\n\n")
        out.append("| series_id | title | freq | units | obs |\n")
        out.append("|---|---|---|---|---|\n")
        for s in in_basket_rows:
            t = (s["title"] or "")[:70]
            out.append(
                f"| `{s['series_id']}` | {t} | {s['frequency'] or ''} | "
                f"{s['units'] or ''} | {s['obs_count'] or ''} |\n"
            )
        out.append("\n")

        out.append("### In DB but NOT in basket — candidate additions\n\n")
        out.append(f"({len(not_in_basket)} series after noise filter)\n\n")
        out.append("| series_id | title | freq | obs | last |\n")
        out.append("|---|---|---|---|---|\n")
        for s in not_in_basket:
            t = (s["title"] or "")[:80]
            out.append(
                f"| `{s['series_id']}` | {t} | {s['frequency'] or ''} | "
                f"{s['obs_count'] or ''} | {s['last_value_date'] or ''} |\n"
            )
        out.append("\n")

        out.append(f"### Filtered out as noise ({len(noise_series)} series)\n\n")
        out.append("<details><summary>show noise list</summary>\n\n")
        for s in noise_series[:50]:
            t = (s["title"] or "")[:70]
            out.append(f"- `{s['series_id']}` — {t}\n")
        if len(noise_series) > 50:
            out.append(f"- ...and {len(noise_series) - 50} more\n")
        out.append("\n</details>\n\n")

        summary_rows.append({
            "pillar": pillar_key,
            "name": full_name,
            "total": len(all_series),
            "signal": len(signal_series),
            "in_basket": len(in_basket_rows),
            "not_in_basket": len(not_in_basket),
        })

    # Insert summary at top after the intro
    summary_md = ["\n## Summary\n\n"]
    summary_md.append(
        "| Pillar | Total in DB | Signal candidates | Currently used | Not in basket |\n"
    )
    summary_md.append("|---|---|---|---|---|\n")
    for r in summary_rows:
        summary_md.append(
            f"| **{r['name']} ({r['pillar']})** | {r['total']} | {r['signal']} | "
            f"{r['in_basket']} | {r['not_in_basket']} |\n"
        )
    summary_md.append("\n")

    final = "".join(out[:5]) + "".join(summary_md) + "".join(out[5:])

    OUT_PATH.write_text(final)
    print(f"Wrote {OUT_PATH}")
    print(f"\nSummary:")
    for r in summary_rows:
        print(
            f"  {r['pillar']:>8} ({r['name'][:40]:>40}): "
            f"in-basket={r['in_basket']}, gap={r['not_in_basket']}"
        )


if __name__ == "__main__":
    main()
