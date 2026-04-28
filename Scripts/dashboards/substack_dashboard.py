"""Lighthouse Macro — Substack Internal Dashboard

Ingests the eleven Substack CSV exports that Bob drops into ~/Downloads/, archives
them under Data/substack_snapshots/, computes KPIs, renders LHM-branded charts,
and emits a self-contained HTML dashboard at Outputs/Substack_Dashboard/.

Run twice a day (04:30 ET / 16:30 ET) via launchd. Each run picks the newest
CSV of each type by mtime and the date stamp in the filename.

Outputs:
    Outputs/Substack_Dashboard/dashboard_latest.html   (stable path, overwritten)
    Outputs/Substack_Dashboard/dashboard_<stamp>.html  (versioned archive)
    Data/substack_snapshots/<stamp>/*.csv              (raw CSV archive)
    Data/substack_snapshots/kpi_history.csv            (append-only KPI log)
"""
from __future__ import annotations

import base64
import io
import json
import logging
import re
import shutil
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import FancyBboxPatch

# ---------------------------------------------------------------------------
# Paths & config
# ---------------------------------------------------------------------------

REPO = Path("/Users/bob/LHM")
DOWNLOADS = Path.home() / "Downloads"
OUT_DIR = REPO / "Outputs" / "Substack_Dashboard"
SNAP_ROOT = REPO / "Data" / "substack_snapshots"
KPI_HISTORY = SNAP_ROOT / "kpi_history.csv"
RESUBBED_FILE = SNAP_ROOT / "resubbed_emails.txt"  # one email per line, '#' for comments
LOG_DIR = REPO / "logs"
ICON = REPO / "Brand" / "icon_transparent_128.png"

OUT_DIR.mkdir(parents=True, exist_ok=True)
SNAP_ROOT.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

# LHM 23/89/BB palette
OCEAN     = "#2389BB"
DUSK      = "#FF6723"
SKY       = "#23BBFF"
VENUS     = "#FF2389"
SEA       = "#00BB89"
DOLDRUMS  = "#898989"
STARBOARD = "#238923"
PORT      = "#892323"
FOG       = "#D1D1D1"

CSV_TYPES = [
    "arr",
    "audience_location",
    "email_stats",
    "emails",
    "followers",
    "growth_sources",
    "paid_subscriber_growth",
    "free_subscriber_growth",
    "subscribers",
    "traffic",
    "traffic_sources",
    "unsubscribes",
]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "substack_dashboard.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("dashboard")


# ---------------------------------------------------------------------------
# CSV discovery
# ---------------------------------------------------------------------------

CSV_RE = re.compile(r"lighthousemacro_(?P<type>[a-z_]+)_(?P<date>\d{4}-\d{2}-\d{2})(?:\s*\(\d+\))?\.csv$")


@dataclass
class CSVPick:
    csv_type: str
    path: Path
    date: str  # YYYY-MM-DD from filename


def discover_csvs() -> dict[str, CSVPick]:
    """Pick the newest CSV for each type from ~/Downloads/, by date stamp then mtime."""
    candidates: dict[str, list[tuple[str, float, Path]]] = {t: [] for t in CSV_TYPES}
    for p in DOWNLOADS.glob("lighthousemacro_*.csv"):
        m = CSV_RE.match(p.name)
        if not m:
            continue
        t = m.group("type")
        if t not in candidates:
            continue
        candidates[t].append((m.group("date"), p.stat().st_mtime, p))

    picks: dict[str, CSVPick] = {}
    for t, items in candidates.items():
        if not items:
            continue
        items.sort(key=lambda x: (x[0], x[1]), reverse=True)
        date, _mtime, path = items[0]
        picks[t] = CSVPick(t, path, date)
        log.info("picked %s: %s", t, path.name)
    missing = [t for t in CSV_TYPES if t not in picks]
    if missing:
        log.warning("missing CSV types: %s", ", ".join(missing))
    return picks


def archive_snapshot(picks: dict[str, CSVPick], stamp: str) -> Path:
    snap_dir = SNAP_ROOT / stamp
    snap_dir.mkdir(parents=True, exist_ok=True)
    for t, pick in picks.items():
        target = snap_dir / f"{t}.csv"
        shutil.copy2(pick.path, target)
    log.info("archived %d CSVs to %s", len(picks), snap_dir)
    return snap_dir


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------

def _read_two_col_series(path: Path, value_name: str) -> pd.DataFrame:
    df = pd.read_csv(path, header=None, names=["date", value_name])
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    if df[value_name].dtype == object:
        df[value_name] = (
            df[value_name].astype(str).str.replace(r"[\$,]", "", regex=True).str.strip()
        )
        df[value_name] = pd.to_numeric(df[value_name], errors="coerce")
    df = df.dropna(subset=["date"]).sort_values("date").reset_index(drop=True)
    return df


def load_arr(path: Path) -> pd.DataFrame:
    return _read_two_col_series(path, "arr")


def load_followers(path: Path) -> pd.DataFrame:
    return _read_two_col_series(path, "followers")


def load_emails(path: Path) -> pd.DataFrame:
    return _read_two_col_series(path, "emails")


def load_subscribers(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    for col in ["paid", "comps", "gifts", "free_trials", "total_subscribers"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["date"]).sort_values("date").reset_index(drop=True)
    if "total_subscribers" in df.columns and df["total_subscribers"].isna().all():
        df["total_subscribers"] = df[["paid", "comps", "gifts", "free_trials"]].sum(axis=1, min_count=1)
    return df


def load_traffic(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df.columns = [c.strip().lower() for c in df.columns]
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["views"] = pd.to_numeric(df["views"], errors="coerce")
    return df.dropna(subset=["date"]).sort_values("date").reset_index(drop=True)


def load_traffic_sources(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    return df


def load_audience_location(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    return df


def load_growth_sources(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    for col in ["unique_visitors", "new_subscribers", "new_revenue"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df.dropna(subset=["date"]).reset_index(drop=True)


def load_email_stats(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["post_date"] = pd.to_datetime(df["post_date"], errors="coerce", utc=True)
    for col in ["views", "open_rate", "click_through_rate", "engagement_rate",
                "likes", "comments", "shares", "restacks", "subscribes",
                "free_trials", "estimated_value", "sent", "opens", "clicks"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df.sort_values("post_date", ascending=False).reset_index(drop=True)


def load_paid_growth(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df.columns = [c.strip().lower() for c in df.columns]
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    return df.dropna(subset=["date"]).sort_values("date").reset_index(drop=True)


def load_unsubscribes(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df.columns = [c.strip().lower() for c in df.columns]
    if "unsubscribed_at" in df.columns:
        df["unsubscribed_at"] = pd.to_datetime(df["unsubscribed_at"], errors="coerce", utc=True)
    return df


# ---------------------------------------------------------------------------
# KPIs
# ---------------------------------------------------------------------------

def safe_int(x) -> Optional[int]:
    try:
        if pd.isna(x):
            return None
        return int(round(float(x)))
    except Exception:
        return None


def safe_float(x) -> Optional[float]:
    try:
        if pd.isna(x):
            return None
        return float(x)
    except Exception:
        return None


def pct(a: Optional[float], b: Optional[float]) -> Optional[float]:
    if a is None or b is None or b == 0:
        return None
    return (a - b) / b * 100.0


def compute_kpis(data: dict) -> dict:
    today = datetime.now(timezone.utc).date()
    kpi: dict = {"as_of": today.isoformat()}

    # Subscribers CSV tracks PAID-tier rows (paid, comps, gifts, free trials).
    # Free subscribers come from the emails list (one row per day with list size).
    subs = data.get("subscribers")
    emails_df = data.get("emails")
    if subs is not None and len(subs):
        last = subs.iloc[-1]
        d7 = subs[subs["date"] >= subs["date"].max() - pd.Timedelta(days=7)]
        d30 = subs[subs["date"] >= subs["date"].max() - pd.Timedelta(days=30)]
        kpi["paid_subs"] = safe_int(last.get("paid"))
        kpi["free_trials"] = safe_int(last.get("free_trials"))
        kpi["comps"] = safe_int(last.get("comps"))
        kpi["gifts"] = safe_int(last.get("gifts"))
        if len(d7) >= 2:
            kpi["paid_subs_7d"]  = safe_int(last.get("paid")) - safe_int(d7.iloc[0].get("paid"))
        if len(d30) >= 2:
            kpi["paid_subs_30d"] = safe_int(last.get("paid")) - safe_int(d30.iloc[0].get("paid"))

    if emails_df is not None and len(emails_df):
        last_emails = safe_int(emails_df.iloc[-1]["emails"])
        kpi["total_subs"] = last_emails  # email list = free + paid
        d7 = emails_df[emails_df["date"] >= emails_df["date"].max() - pd.Timedelta(days=7)]
        d30 = emails_df[emails_df["date"] >= emails_df["date"].max() - pd.Timedelta(days=30)]
        if len(d7) >= 2:
            kpi["total_subs_7d"] = last_emails - safe_int(d7.iloc[0]["emails"])
        if len(d30) >= 2:
            kpi["total_subs_30d"] = last_emails - safe_int(d30.iloc[0]["emails"])
        if kpi.get("paid_subs") is not None:
            kpi["free_subs"] = last_emails - kpi["paid_subs"]

    arr = data.get("arr")
    if arr is not None and len(arr):
        last_arr = safe_float(arr.iloc[-1]["arr"])
        kpi["arr"] = last_arr
        d30 = arr[arr["date"] >= arr["date"].max() - pd.Timedelta(days=30)]
        d90 = arr[arr["date"] >= arr["date"].max() - pd.Timedelta(days=90)]
        if len(d30) >= 2:
            kpi["arr_30d_change"] = last_arr - safe_float(d30.iloc[0]["arr"])
        if len(d90) >= 2:
            kpi["arr_90d_change"] = last_arr - safe_float(d90.iloc[0]["arr"])

    fol = data.get("followers")
    if fol is not None and len(fol):
        kpi["followers"] = safe_int(fol.iloc[-1]["followers"])
        d30 = fol[fol["date"] >= fol["date"].max() - pd.Timedelta(days=30)]
        if len(d30) >= 2:
            kpi["followers_30d"] = safe_int(fol.iloc[-1]["followers"]) - safe_int(d30.iloc[0]["followers"])

    emails = data.get("emails")
    if emails is not None and len(emails):
        kpi["emails_total"] = safe_int(emails.iloc[-1]["emails"])

    traffic = data.get("traffic")
    if traffic is not None and len(traffic):
        recent = traffic.tail(30)
        kpi["views_30d"] = safe_int(recent["views"].sum())
        kpi["views_avg_30d"] = safe_float(recent["views"].mean())
        prev = traffic.iloc[-60:-30] if len(traffic) >= 60 else None
        if prev is not None and len(prev):
            kpi["views_30d_chg_pct"] = pct(kpi["views_30d"], safe_float(prev["views"].sum()))

    es = data.get("email_stats")
    if es is not None and len(es):
        last30 = es[es["post_date"] >= pd.Timestamp.utcnow() - pd.Timedelta(days=30)]
        if len(last30):
            kpi["avg_open_rate_30d"] = safe_float(last30["open_rate"].mean())
            kpi["avg_ctr_30d"] = safe_float(last30["click_through_rate"].mean())
            kpi["avg_engagement_30d"] = safe_float(last30["engagement_rate"].mean())
            kpi["posts_30d"] = int(len(last30))

    paid_g = data.get("paid_subscriber_growth")
    if paid_g is not None and len(paid_g):
        recent = paid_g.tail(30)
        kpi["new_paid_30d"] = safe_int(recent["new_paid"].sum()) if "new_paid" in recent else None
        kpi["upgrades_30d"] = safe_int(recent["upgrades"].sum()) if "upgrades" in recent else None
        kpi["trials_started_30d"] = safe_int(recent["trials_started"].sum()) if "trials_started" in recent else None
        kpi["cancels_finalized_30d"] = safe_int(recent["cancellations_finalized"].sum()) if "cancellations_finalized" in recent else None

    return kpi


def append_kpi_history(kpi: dict, stamp: str) -> None:
    row = {"run_stamp": stamp, **kpi}
    df_row = pd.DataFrame([row])
    if KPI_HISTORY.exists():
        prev = pd.read_csv(KPI_HISTORY)
        df_row = pd.concat([prev, df_row], ignore_index=True, sort=False)
    df_row.to_csv(KPI_HISTORY, index=False)


# ---------------------------------------------------------------------------
# Derived analysis — the inputs for written takeaways
# ---------------------------------------------------------------------------

def classify_post(row) -> str:
    """Classify a post as Beam / Beacon / Note / Horizon / Chartbook / Other."""
    tags = _s(row.get("tags")) if hasattr(row, "get") else ""
    title = _s(row.get("title")) if hasattr(row, "get") else ""
    blob = (tags + " " + title).lower()
    for kind in ["beam", "beacon", "horizon", "chartbook"]:
        if kind in blob:
            return kind.title()
    if "note" in tags.lower():
        return "Note"
    return "Other"


def analyze(data: dict, kpi: dict) -> dict:
    """Compute derived metrics that drive panel charts and written takeaways."""
    A: dict = {}

    # ---- Growth sources: who's actually converting ----
    gs = data.get("growth_sources")
    if gs is not None and len(gs):
        cat = (gs.groupby("category", as_index=False)
                 [["unique_visitors", "new_subscribers", "new_revenue"]].sum()
                 .sort_values("new_subscribers", ascending=False))
        cat["conv_visitor_to_sub"] = (cat["new_subscribers"] / cat["unique_visitors"]).replace([np.inf, -np.inf], 0).fillna(0)
        cat["revenue_per_visitor"] = (cat["new_revenue"] / cat["unique_visitors"]).replace([np.inf, -np.inf], 0).fillna(0)
        A["growth_by_category"] = cat
        # Top sources
        src_all = (gs.groupby("source", as_index=False)
                     [["unique_visitors", "new_subscribers", "new_revenue"]].sum()
                     .sort_values("new_subscribers", ascending=False))
        A["growth_top_sources"] = src_all.head(12)
        # Notes-specific aggregation across all the named-Notes rows
        notes_rows = src_all[src_all["source"].str.contains("Notes", na=False, regex=False)]
        if len(notes_rows):
            A["notes_subs"] = int(notes_rows["new_subscribers"].sum())
            A["notes_revenue"] = int(notes_rows["new_revenue"].sum())
            A["notes_post_count"] = int(len(notes_rows))
        # Headline numbers
        A["total_visitors"] = int(cat["unique_visitors"].sum())
        A["total_new_subs_period"] = int(cat["new_subscribers"].sum())
        A["total_new_revenue_period"] = float(cat["new_revenue"].sum())
        if A["total_visitors"]:
            A["overall_visitor_to_sub"] = A["total_new_subs_period"] / A["total_visitors"]
        # Best converting category (min 50 visitors so 1 sub on tiny base doesn't win)
        big = cat[cat["unique_visitors"] >= 50]
        if len(big):
            A["best_conv_category"] = big.sort_values("conv_visitor_to_sub", ascending=False).iloc[0].to_dict()
            A["worst_conv_category"] = big.sort_values("conv_visitor_to_sub", ascending=True).iloc[0].to_dict()
        # Revenue concentration
        A["revenue_share_substack"] = (
            float(cat[cat["category"] == "Substack"]["new_revenue"].sum())
            / max(A["total_new_revenue_period"], 1)
        ) if A.get("total_new_revenue_period") else 0.0

    # ---- Traffic sources: where reads come from ----
    ts = data.get("traffic_sources")
    if ts is not None and len(ts):
        df = ts.copy()
        df["free_signup"] = pd.to_numeric(df["free_signup"], errors="coerce")
        df["subscribed"] = pd.to_numeric(df["subscribed"], errors="coerce")
        df["views"] = pd.to_numeric(df["views"], errors="coerce")
        df["users"] = pd.to_numeric(df["users"], errors="coerce")
        df["sub_per_visitor"] = (df["free_signup"].fillna(0) / df["users"].replace(0, np.nan))
        A["traffic_sources"] = df
        cat = df.groupby("source_category", as_index=False)[["views", "users", "free_signup", "subscribed"]].sum()
        A["traffic_by_category"] = cat.sort_values("views", ascending=False)

    # ---- Email post performance: by type and audience ----
    es = data.get("email_stats")
    if es is not None and len(es):
        df = es.copy()
        df["type"] = df.apply(classify_post, axis=1)
        df["section"] = df["section_name"].fillna("untagged")
        # By post type
        by_type = (df.groupby("type")
                     .agg(posts=("title", "count"),
                          avg_views=("views", "mean"),
                          avg_open=("open_rate", "mean"),
                          avg_ctr=("click_through_rate", "mean"),
                          avg_eng=("engagement_rate", "mean"),
                          total_signups=("signups", "sum"),
                          total_subs=("subscribes", "sum"),
                          total_value=("estimated_value", "sum"))
                     .reset_index())
        A["posts_by_type"] = by_type
        # By audience
        by_aud = (df.groupby("audience")
                    .agg(posts=("title", "count"),
                         avg_views=("views", "mean"),
                         avg_open=("open_rate", "mean"),
                         total_signups=("signups", "sum"),
                         total_value=("estimated_value", "sum"))
                    .reset_index())
        A["posts_by_audience"] = by_aud
        # Top performers
        A["top_posts_signups"] = df.sort_values("signups", ascending=False).head(8)
        A["top_posts_value"] = df.sort_values("estimated_value", ascending=False).head(8)
        # Free → paid attribution: posts where subscribes > 0
        A["paid_converting_posts"] = df[df["subscribes"] > 0].sort_values("subscribes", ascending=False)
        # Open / CTR aggregates
        A["all_open_mean"] = float(df["open_rate"].mean())
        A["paid_open_mean"] = float(df[df["audience"] == "only_paid"]["open_rate"].mean()) if (df["audience"] == "only_paid").any() else None
        A["everyone_open_mean"] = float(df[df["audience"] == "everyone"]["open_rate"].mean()) if (df["audience"] == "everyone").any() else None

    # ---- Funnel: visitor → free → paid ----
    pg = data.get("paid_subscriber_growth")
    if pg is not None and len(pg):
        last30 = pg.tail(30)
        A["pg_new_paid"] = int(last30.get("new_paid", pd.Series([0])).sum())
        A["pg_upgrades"] = int(last30.get("upgrades", pd.Series([0])).sum())
        A["pg_trials"] = int(last30.get("trials_started", pd.Series([0])).sum())
        A["pg_cancels_init"] = int(last30.get("cancellations_initiated", pd.Series([0])).sum())
        A["pg_cancels_final"] = int(last30.get("cancellations_finalized", pd.Series([0])).sum())
        A["pg_total_in"] = A["pg_new_paid"] + A["pg_upgrades"]
        A["pg_net"] = A["pg_total_in"] - A["pg_cancels_final"]
        # Upgrade dominance: fraction of new paid coming from upgrades vs direct
        denom = A["pg_total_in"]
        A["upgrade_share"] = (A["pg_upgrades"] / denom) if denom else None

    # ---- Audience composition ----
    loc = data.get("audience_location")
    if loc is not None and len(loc):
        df = loc.copy()
        total = df["free_signups"].sum()
        df["pct"] = df["free_signups"] / total * 100 if total else 0
        A["audience_total"] = int(total)
        A["audience_top"] = df.sort_values("free_signups", ascending=False).head(10)
        # US share
        us = df[df["location"].str.upper() == "US"]
        A["us_share"] = float(us["pct"].sum()) if len(us) else None
        # Geographic concentration: HHI on shares
        shares = (df["free_signups"] / total).fillna(0) if total else pd.Series([0])
        A["geo_hhi"] = float((shares ** 2).sum() * 10000)  # 0-10000 scale
        A["country_count"] = int((df["free_signups"] > 0).sum())

    # ---- Engagement: 30d vs 60d trend ----
    if es is not None and len(es):
        d = es.copy()
        cutoff_30 = pd.Timestamp.utcnow() - pd.Timedelta(days=30)
        cutoff_60 = pd.Timestamp.utcnow() - pd.Timedelta(days=60)
        last30 = d[d["post_date"] >= cutoff_30]
        prev30 = d[(d["post_date"] >= cutoff_60) & (d["post_date"] < cutoff_30)]
        A["open_rate_30d"] = float(last30["open_rate"].mean()) if len(last30) else None
        A["open_rate_prev30"] = float(prev30["open_rate"].mean()) if len(prev30) else None
        A["ctr_30d"] = float(last30["click_through_rate"].mean()) if len(last30) else None
        A["ctr_prev30"] = float(prev30["click_through_rate"].mean()) if len(prev30) else None
        A["posts_30d"] = int(len(last30))
        A["posts_prev30"] = int(len(prev30))

    # ---- Followers vs email list relationship ----
    fol = data.get("followers")
    em = data.get("emails")
    if fol is not None and em is not None and len(fol) and len(em):
        latest_fol = int(fol.iloc[-1]["followers"])
        latest_em = int(em.iloc[-1]["emails"])
        A["follower_email_ratio"] = latest_fol / latest_em if latest_em else None
        # 30d growth comparison
        fol_30 = fol[fol["date"] >= fol["date"].max() - pd.Timedelta(days=30)]
        em_30 = em[em["date"] >= em["date"].max() - pd.Timedelta(days=30)]
        if len(fol_30) >= 2 and len(em_30) >= 2:
            A["fol_growth_30d"] = int(latest_fol - int(fol_30.iloc[0]["followers"]))
            A["em_growth_30d"] = int(latest_em - int(em_30.iloc[0]["emails"]))

    # ---- ARR per paid sub (implied annualized rate) ----
    if kpi.get("arr") and kpi.get("paid_subs"):
        A["arr_per_paid"] = kpi["arr"] / kpi["paid_subs"]

    return A


# ---------------------------------------------------------------------------
# Written takeaways — data-driven, LHM voice
# ---------------------------------------------------------------------------

def _arrow(x: Optional[float]) -> str:
    if x is None:
        return ""
    if x > 0:
        return "↑"
    if x < 0:
        return "↓"
    return "→"


def takeaways_overview(kpi: dict, A: dict) -> list[str]:
    out = []
    total = kpi.get("total_subs")
    paid = kpi.get("paid_subs")
    free = kpi.get("free_subs")
    arr = kpi.get("arr")
    if total and paid is not None:
        paid_pct = paid / total * 100
        out.append(
            f"List sits at {total:,} subscribers, {paid:,} paid ({paid_pct:.1f}%). "
            f"The free base is doing the heavy lifting on reach. The paid book is what gets monetized."
        )
    if kpi.get("paid_subs_30d") is not None and kpi.get("paid_subs_30d") > 0:
        prev = paid - kpi["paid_subs_30d"]
        lift = (kpi["paid_subs_30d"] / max(prev, 1)) * 100
        out.append(
            f"Paid subs added {kpi['paid_subs_30d']} in 30 days, a {lift:.0f}% lift off a base of {prev}. "
            f"Small absolute numbers, large percentage moves. Don't overweight a single week."
        )
    if arr and kpi.get("arr_30d_change"):
        per_paid = A.get('arr_per_paid', 0)
        out.append(
            f"ARR ${arr:,.0f}, up ${kpi['arr_30d_change']:,.0f} in 30 days. "
            f"Implied per-paid run-rate is ${per_paid:,.0f}/year, below the $500/yr list price because founding-member "
            f"rates ($300-$400/yr locked for life) and Substack's per-month pricing on monthly subs dilute the average."
        )
    if kpi.get("views_30d") and kpi.get("views_30d_chg_pct") is not None:
        chg = kpi["views_30d_chg_pct"]
        verb = "doubled" if chg > 90 else "jumped" if chg > 25 else "drifted" if abs(chg) < 5 else "softened"
        out.append(
            f"30-day views {verb} ({chg:+.0f}% vs prior 30d), {kpi['views_30d']:,} total. "
            f"Reach is expanding faster than paid. The funnel has volume; conversion is the constraint."
        )
    op = kpi.get("avg_open_rate_30d")
    if op:
        bench = "well above" if op > 0.40 else "above" if op > 0.30 else "in line with" if op > 0.20 else "below"
        out.append(
            f"30-day open rate {op*100:.1f}% is {bench} typical macro newsletter benchmarks (~25-35%). "
            f"Engagement signal is healthy. The acquisition signal is the part to watch."
        )
    return out


def takeaways_growth(A: dict) -> list[str]:
    out = []
    cat = A.get("growth_by_category")
    if cat is not None and len(cat):
        top = cat.iloc[0]
        out.append(
            f"{top['category']} is the dominant acquisition channel: "
            f"{int(top['unique_visitors']):,} visitors, {int(top['new_subscribers'])} new subs, "
            f"${int(top['new_revenue']):,} new revenue. "
            f"Substack-internal flow (Notes, recommendations, cross-promo) is doing what off-platform usually doesn't."
        )
        rev_share = A.get("revenue_share_substack")
        if rev_share and rev_share > 0.5:
            out.append(
                f"{rev_share*100:.0f}% of new revenue comes through Substack-native sources. "
                f"That's a concentration risk and a leverage point. If Notes recommendations dry up, paid acquisition dries up with it."
            )
    if A.get("best_conv_category") and A.get("worst_conv_category"):
        b = A["best_conv_category"]
        w = A["worst_conv_category"]
        out.append(
            f"Best converting category: {b['category']} at "
            f"{b['conv_visitor_to_sub']*100:.1f}% visitor→sub. "
            f"Weakest: {w['category']} at {w['conv_visitor_to_sub']*100:.1f}%. "
            f"The gap between channels is wider than the gap between posts."
        )
    if A.get("overall_visitor_to_sub"):
        out.append(
            f"Overall visitor-to-sub conversion runs {A['overall_visitor_to_sub']*100:.1f}%. "
            f"Industry rule of thumb for paid newsletters is 1-3% on cold traffic. "
            f"Anything in or above that range means top-of-funnel is fine and the bottleneck is further down."
        )
    if A.get("notes_subs"):
        n_subs = A["notes_subs"]
        n_rev = A.get("notes_revenue", 0)
        n_count = A.get("notes_post_count", 0)
        out.append(
            f"Notes drives {n_subs} new subs across {n_count} attributed Notes posts, ${n_rev:,} in revenue. "
            f"Substack records 0 visitors for Notes because attribution is in-app, not web-traffic. "
            f"Notes is a top-of-funnel engine, not a monetization engine. That's not a bug. It's the design."
        )
    return out


def takeaways_engagement(kpi: dict, A: dict) -> list[str]:
    out = []
    op30 = A.get("open_rate_30d")
    op60 = A.get("open_rate_prev30")
    if op30 is not None and op60 is not None and op60 > 0:
        delta = (op30 - op60) * 100
        if abs(delta) < 1:
            out.append(
                f"Open rate held flat at {op30*100:.1f}% across the last two 30-day windows. "
                f"Stability at this level is the floor, not the ceiling."
            )
        elif delta > 0:
            out.append(
                f"Open rate improved {delta:.1f}pp ({op60*100:.1f}% to {op30*100:.1f}%) "
                f"between the prior 30 days and the most recent 30. List quality is moving the right way."
            )
        else:
            out.append(
                f"Open rate softened {abs(delta):.1f}pp ({op60*100:.1f}% to {op30*100:.1f}%) "
                f"between the prior 30 days and the most recent 30. "
                f"Common when the list grows faster than engagement; new free subs need time to warm up."
            )
    paid_o = A.get("paid_open_mean")
    every_o = A.get("everyone_open_mean")
    if paid_o and every_o:
        gap = (paid_o - every_o) * 100
        out.append(
            f"Paid-only posts open at {paid_o*100:.1f}% vs {every_o*100:.1f}% on everyone-posts ({gap:+.1f}pp). "
            f"Paid subs are more engaged than the broader list, which is what you'd want. "
            f"It also means paid-only posts reach a smaller absolute audience: that's the price of segmentation."
        )
    by_type = A.get("posts_by_type")
    if by_type is not None and len(by_type):
        # Find the type with most posts (excluding 'Other' if dominant)
        non_other = by_type[by_type["type"] != "Other"]
        if len(non_other):
            best_eng = non_other.sort_values("avg_eng", ascending=False).iloc[0]
            out.append(
                f"By post type, {best_eng['type']} leads on engagement at "
                f"{best_eng['avg_eng']*100:.1f}% (n={int(best_eng['posts'])}). "
                f"Sample sizes are still small. Treat as directional, not definitive."
            )
    ctr30 = A.get("ctr_30d")
    if ctr30:
        verdict = "strong" if ctr30 > 0.04 else "fine" if ctr30 > 0.02 else "soft"
        out.append(
            f"30-day CTR sits at {ctr30*100:.2f}%, which is {verdict} for a research newsletter. "
            f"CTR is the truer engagement signal. Opens can be inflated by image pixels and prefetching."
        )
    return out


def takeaways_funnel(kpi: dict, A: dict) -> list[str]:
    out = []
    total_in = A.get("pg_total_in")
    upgrades = A.get("pg_upgrades")
    new_paid = A.get("pg_new_paid")
    cancels = A.get("pg_cancels_final")
    if total_in is not None:
        out.append(
            f"Last 30 days: {total_in} paid additions ({new_paid} new direct + {upgrades} upgrades), "
            f"{cancels} cancellations finalized. Net {A.get('pg_net', 0):+d}. "
            f"The book is growing through conversion, not new acquisition."
        )
    if A.get("upgrade_share") is not None:
        share = A["upgrade_share"] * 100
        out.append(
            f"Upgrades account for {share:.0f}% of paid additions. "
            f"Free→paid is the dominant path. Direct paid sign-ups are rare. "
            f"The implication: keep growing the free list and the paid conversion will follow on its own clock."
        )
    if A.get("pg_trials") is not None:
        trials = A["pg_trials"]
        if trials > 0:
            out.append(
                f"{trials} free trial{'s' if trials != 1 else ''} started in the last 30 days. "
                f"Small but real. Trials are a different beast than direct paid sign-ups: they signal interest with optionality."
            )
    if cancels and total_in:
        churn_rate = cancels / max(kpi.get("paid_subs", 1) - total_in + cancels, 1) * 100
        out.append(
            f"Implied 30-day churn on the prior paid base: {churn_rate:.1f}%. "
            f"On a sub-20 paid book, every cancel is 5%+ of the base. "
            f"Don't read trend into single events; do read the reason buckets."
        )
    if kpi.get("total_subs") and kpi.get("paid_subs"):
        free_to_paid_ratio = kpi["paid_subs"] / kpi["total_subs"] * 100
        out.append(
            f"Free→paid penetration is {free_to_paid_ratio:.1f}%. "
            f"Industry benchmark for macro/finance newsletters is 2-5% over time. "
            f"At {free_to_paid_ratio:.1f}%, there's headroom in both directions: bigger free list and higher conversion."
        )
    return out


def takeaways_content(A: dict) -> list[str]:
    out = []
    by_aud = A.get("posts_by_audience")
    if by_aud is not None and len(by_aud):
        every = by_aud[by_aud["audience"] == "everyone"]
        paid = by_aud[by_aud["audience"] == "only_paid"]
        if len(every) and len(paid):
            ev = every.iloc[0]
            pa = paid.iloc[0]
            out.append(
                f"Everyone-posts ({int(ev['posts'])}) average {int(ev['avg_views'])} views; "
                f"paid-only ({int(pa['posts'])}) average {int(pa['avg_views'])}. "
                f"Reach gap is roughly {ev['avg_views']/max(pa['avg_views'],1):.1f}x. "
                f"Paid-only posts can't reach the cold list by design. That gap isn't a problem; it's the paywall working."
            )
    by_type = A.get("posts_by_type")
    if by_type is not None and len(by_type):
        # Most signups by type
        by_type_v = by_type[by_type["total_signups"] > 0].sort_values("total_signups", ascending=False)
        if len(by_type_v):
            t = by_type_v.iloc[0]
            out.append(
                f"{t['type']} posts drove {int(t['total_signups'])} signups across {int(t['posts'])} posts "
                f"(${int(t['total_value']):,} attributed value). "
                f"That's the format pulling the most acquisition weight right now."
            )
    paid_conv = A.get("paid_converting_posts")
    if paid_conv is not None and len(paid_conv):
        out.append(
            f"{len(paid_conv)} posts in the email-stats window directly drove paid conversions. "
            f"The rest are reach plays, brand plays, or audience-warming. Both functions matter. "
            f"Don't let conversion attribution dictate every editorial choice."
        )
        top_conv = paid_conv.head(3)
        titles = [_s(t)[:50] for t in top_conv["title"].tolist()]
        out.append(
            f"Top converting titles: {' · '.join(titles)}. "
            f"Pattern in the survivor set: definitive claims, specific numbers, named regimes."
        )
    return out


def takeaways_audience(kpi: dict, A: dict) -> list[str]:
    out = []
    if A.get("us_share") is not None:
        out.append(
            f"US share of free signups: {A['us_share']:.1f}%. "
            f"International tail is real ({A.get('country_count', 0)} countries represented in the signup mix). "
            f"For an institutional macro audience, that international weight is a feature."
        )
    if A.get("geo_hhi") is not None:
        hhi = A["geo_hhi"]
        verdict = "highly concentrated" if hhi > 4000 else "moderately concentrated" if hhi > 2500 else "diversified"
        out.append(
            f"Geographic HHI on signup share: {hhi:,.0f} ({verdict}). "
            f"Reference points: HHI under 1500 is competitive, 2500+ is concentrated. "
            f"A US-heavy macro newsletter scoring 'concentrated' is the expected outcome, not a flag."
        )
    if A.get("follower_email_ratio") is not None:
        ratio = A["follower_email_ratio"]
        out.append(
            f"Follower-to-email ratio is {ratio:.2f}x. "
            f"Followers are a Substack profile metric, broader than the email list. "
            f"A ratio above 1.0 means there's a discoverable surface area not yet captured as email."
        )
    if A.get("fol_growth_30d") is not None and A.get("em_growth_30d") is not None:
        fg = A["fol_growth_30d"]
        eg = A["em_growth_30d"]
        if eg > 0:
            faster = "Followers" if fg > eg else "Email subs"
            slower = "Email subs" if fg > eg else "Followers"
            out.append(
                f"30-day growth: {fg:+d} followers, {eg:+d} emails. "
                f"{faster} growing faster than {slower.lower()}. "
                f"Healthy sign that profile-level brand recognition is pacing or outpacing email capture."
            )
    return out


# ---------------------------------------------------------------------------
# Chart helpers — LHM brand
# ---------------------------------------------------------------------------

def _style_axes(ax):
    ax.grid(False)
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_linewidth(0.5)
        spine.set_color(DOLDRUMS)
    ax.tick_params(axis="both", which="both", length=0, colors=DOLDRUMS, labelsize=9)
    ax.yaxis.tick_right()
    ax.yaxis.set_label_position("right")


def _save_to_b64(fig) -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=160, bbox_inches="tight",
                pad_inches=0.05, facecolor="white")
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode("ascii")


def chart_subscribers(subs: pd.DataFrame, emails: Optional[pd.DataFrame] = None) -> str:
    df = subs[subs["date"] >= subs["date"].max() - pd.Timedelta(days=180)].copy()
    fig, ax = plt.subplots(figsize=(9, 3.6), facecolor="white")
    if emails is not None and len(emails):
        em = emails[emails["date"] >= emails["date"].max() - pd.Timedelta(days=180)].copy()
        ax.fill_between(em["date"], 0, em["emails"], color=OCEAN, alpha=0.10)
        ax.plot(em["date"], em["emails"], color=OCEAN, linewidth=2.8, label="Total list (free + paid)")
    if "paid" in df.columns:
        ax.plot(df["date"], df["paid"], color=DUSK, linewidth=2.4, label="Paid")
    _style_axes(ax)
    ax.set_title("Subscribers — last 180d", color=OCEAN, fontsize=11, fontweight="bold", loc="left")
    ax.legend(loc="upper left", frameon=False, fontsize=9)
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
    xmin = df["date"].min() if emails is None else min(df["date"].min(), em["date"].min())
    xmax = df["date"].max() if emails is None else max(df["date"].max(), em["date"].max())
    ax.set_xlim(xmin, xmax + pd.Timedelta(days=2))
    return _save_to_b64(fig)


def chart_arr(arr: pd.DataFrame) -> str:
    df = arr.copy()
    fig, ax = plt.subplots(figsize=(9, 3.2), facecolor="white")
    ax.fill_between(df["date"], 0, df["arr"], color=SEA, alpha=0.15)
    ax.plot(df["date"], df["arr"], color=SEA, linewidth=2.8)
    _style_axes(ax)
    ax.set_title("ARR ($)", color=OCEAN, fontsize=11, fontweight="bold", loc="left")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    ax.set_xlim(df["date"].min(), df["date"].max() + pd.Timedelta(days=2))
    return _save_to_b64(fig)


def chart_traffic(traffic: pd.DataFrame) -> str:
    df = traffic.copy()
    df["ma7"] = df["views"].rolling(7, min_periods=1).mean()
    fig, ax = plt.subplots(figsize=(9, 3.2), facecolor="white")
    ax.bar(df["date"], df["views"], color=SKY, alpha=0.55, width=0.9, label="Daily")
    ax.plot(df["date"], df["ma7"], color=OCEAN, linewidth=2.6, label="7d MA")
    _style_axes(ax)
    ax.set_title("Daily traffic — views", color=OCEAN, fontsize=11, fontweight="bold", loc="left")
    ax.legend(loc="upper left", frameon=False, fontsize=9)
    ax.set_xlim(df["date"].min(), df["date"].max() + pd.Timedelta(days=1))
    return _save_to_b64(fig)


def chart_traffic_sources(ts: pd.DataFrame) -> str:
    df = ts.copy().sort_values("views", ascending=True)
    fig, ax = plt.subplots(figsize=(9, max(3.0, 0.32 * len(df))), facecolor="white")
    colors = [OCEAN if i % 2 == 0 else DUSK for i in range(len(df))]
    ax.barh(df["source"], df["views"], color=colors)
    _style_axes(ax)
    ax.yaxis.tick_left()
    ax.yaxis.set_label_position("left")
    ax.set_title("Traffic sources — views", color=OCEAN, fontsize=11, fontweight="bold", loc="left")
    return _save_to_b64(fig)


def chart_growth_sources(gs: pd.DataFrame) -> str:
    df = gs.groupby("category", as_index=False)[["unique_visitors", "new_subscribers"]].sum()
    df = df.sort_values("new_subscribers", ascending=True).tail(10)
    fig, ax = plt.subplots(figsize=(9, max(3.0, 0.4 * len(df))), facecolor="white")
    ax.barh(df["category"], df["new_subscribers"], color=OCEAN, label="New subs")
    ax2 = ax.twiny()
    ax2.plot(df["unique_visitors"], df["category"], "o", color=DUSK, markersize=6, label="Unique visitors")
    _style_axes(ax)
    ax.yaxis.tick_left()
    ax.yaxis.set_label_position("left")
    ax2.tick_params(axis="x", colors=DUSK, labelsize=9, length=0)
    for s in ax2.spines.values():
        s.set_visible(False)
    ax.set_title("Growth sources — new subs (Ocean) vs unique visitors (Dusk)",
                 color=OCEAN, fontsize=11, fontweight="bold", loc="left")
    return _save_to_b64(fig)


def chart_audience_location(loc: pd.DataFrame) -> str:
    df = loc.sort_values("free_signups", ascending=True).tail(12)
    fig, ax = plt.subplots(figsize=(9, max(3.0, 0.36 * len(df))), facecolor="white")
    ax.barh(df["location"], df["free_signups"], color=OCEAN)
    _style_axes(ax)
    ax.yaxis.tick_left()
    ax.yaxis.set_label_position("left")
    ax.set_title("Audience location — free signups (top 12)",
                 color=OCEAN, fontsize=11, fontweight="bold", loc="left")
    return _save_to_b64(fig)


def chart_paid_growth(pg: pd.DataFrame) -> str:
    df = pg.tail(30).copy()
    fig, ax = plt.subplots(figsize=(9, 3.2), facecolor="white")
    width = 0.7
    ax.bar(df["date"], df.get("new_paid", 0), color=STARBOARD, label="New paid", width=width)
    if "upgrades" in df.columns:
        ax.bar(df["date"], df["upgrades"], color=SEA, bottom=df.get("new_paid", 0),
               label="Upgrades", width=width)
    if "cancellations_finalized" in df.columns:
        ax.bar(df["date"], -df["cancellations_finalized"], color=PORT,
               label="Cancels", width=width)
    ax.axhline(0, color=FOG, linewidth=0.6, linestyle="--")
    _style_axes(ax)
    ax.set_title("Paid subscriber flow — last 30d", color=OCEAN,
                 fontsize=11, fontweight="bold", loc="left")
    ax.legend(loc="upper left", frameon=False, fontsize=9, ncol=3)
    return _save_to_b64(fig)


def chart_email_engagement(es: pd.DataFrame) -> str:
    df = es.dropna(subset=["post_date", "open_rate"]).head(20).iloc[::-1].copy()
    if df.empty:
        return ""
    fig, ax = plt.subplots(figsize=(9, 3.6), facecolor="white")
    x = df["post_date"]
    ax.plot(x, df["open_rate"] * 100, color=OCEAN, marker="o", linewidth=2.4, label="Open rate %")
    if "click_through_rate" in df.columns:
        ax.plot(x, df["click_through_rate"] * 100, color=DUSK, marker="o",
                linewidth=2.4, label="CTR %")
    _style_axes(ax)
    ax.set_title("Email engagement — last 20 posts", color=OCEAN,
                 fontsize=11, fontweight="bold", loc="left")
    ax.legend(loc="upper left", frameon=False, fontsize=9)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.0f}%"))
    return _save_to_b64(fig)


# ---------------------------------------------------------------------------
# Analysis-panel charts
# ---------------------------------------------------------------------------

def chart_source_funnel(A: dict) -> str:
    """Visitor → free signup → paid sub conversion by category, dual-axis."""
    cat = A.get("growth_by_category")
    if cat is None or cat.empty:
        return ""
    df = cat.sort_values("unique_visitors", ascending=True).copy()
    fig, ax = plt.subplots(figsize=(9, max(3.0, 0.5 * len(df) + 1.0)), facecolor="white")
    y = np.arange(len(df))
    ax.barh(y, df["unique_visitors"], color=OCEAN, alpha=0.55, label="Unique visitors")
    ax.barh(y, df["new_subscribers"] * 20, color=DUSK, alpha=0.85,
            label="New subs (×20 for visibility)")
    ax.set_yticks(y)
    ax.set_yticklabels(df["category"])
    _style_axes(ax)
    ax.yaxis.tick_left()
    ax.yaxis.set_label_position("left")
    ax.set_title("Acquisition funnel by category — visitors vs new subs",
                 color=OCEAN, fontsize=11, fontweight="bold", loc="left")
    ax.legend(loc="lower right", frameon=False, fontsize=9)
    # Annotate conversion rate
    for i, row in enumerate(df.itertuples()):
        rate = row.conv_visitor_to_sub * 100
        ax.text(row.unique_visitors * 1.02, i, f"  {rate:.1f}% conv",
                va="center", fontsize=9, color=DOLDRUMS)
    return _save_to_b64(fig)


def chart_revenue_by_source(A: dict) -> str:
    """Where the money is coming from."""
    cat = A.get("growth_by_category")
    if cat is None or cat.empty:
        return ""
    df = cat[cat["new_revenue"] > 0].sort_values("new_revenue", ascending=True)
    if df.empty:
        return ""
    fig, ax = plt.subplots(figsize=(9, max(2.6, 0.55 * len(df) + 0.6)), facecolor="white")
    colors = [OCEAN, DUSK, SEA, SKY, VENUS][:len(df)]
    ax.barh(df["category"], df["new_revenue"], color=colors)
    _style_axes(ax)
    ax.yaxis.tick_left()
    ax.yaxis.set_label_position("left")
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    ax.set_title("New revenue by acquisition category",
                 color=OCEAN, fontsize=11, fontweight="bold", loc="left")
    for i, (_, row) in enumerate(df.iterrows()):
        share = row["new_revenue"] / df["new_revenue"].sum() * 100
        ax.text(row["new_revenue"] * 1.02, i, f"  {share:.0f}%",
                va="center", fontsize=9, color=DOLDRUMS)
    return _save_to_b64(fig)


def chart_post_type_performance(A: dict) -> str:
    """Avg views (x) vs avg engagement (y), bubble sized by post count."""
    by_type = A.get("posts_by_type")
    if by_type is None or by_type.empty:
        return ""
    df = by_type.copy()
    fig, ax = plt.subplots(figsize=(9, 4.0), facecolor="white")
    color_map = {"Beam": DUSK, "Beacon": OCEAN, "Note": SKY, "Horizon": VENUS,
                 "Chartbook": SEA, "Other": DOLDRUMS}
    for _, row in df.iterrows():
        c = color_map.get(row["type"], DOLDRUMS)
        size = max(80, min(800, row["posts"] * 60))
        ax.scatter(row["avg_views"], row["avg_eng"] * 100, s=size, color=c,
                   alpha=0.7, edgecolors="white", linewidth=2)
        ax.annotate(f"{row['type']} (n={int(row['posts'])})",
                    (row["avg_views"], row["avg_eng"] * 100),
                    xytext=(8, 6), textcoords="offset points",
                    fontsize=10, color=c, fontweight="bold")
    _style_axes(ax)
    ax.set_xlabel("Avg views", color=DOLDRUMS, fontsize=10)
    ax.set_ylabel("Avg engagement %", color=DOLDRUMS, fontsize=10)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.1f}%"))
    ax.set_title("Post type performance — reach vs engagement",
                 color=OCEAN, fontsize=11, fontweight="bold", loc="left")
    return _save_to_b64(fig)


def chart_audience_split(A: dict, kpi: dict) -> str:
    """Stacked horizontal bars: views and signups by audience segment."""
    by_aud = A.get("posts_by_audience")
    if by_aud is None or by_aud.empty:
        return ""
    df = by_aud.copy()
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.0), facecolor="white")
    ax1, ax2 = axes
    df_sorted = df.sort_values("avg_views", ascending=True)
    ax1.barh(df_sorted["audience"], df_sorted["avg_views"], color=OCEAN)
    _style_axes(ax1)
    ax1.yaxis.tick_left()
    ax1.yaxis.set_label_position("left")
    ax1.set_title("Avg views per post", color=OCEAN, fontsize=10,
                  fontweight="bold", loc="left")
    df_sorted2 = df.sort_values("total_signups", ascending=True)
    ax2.barh(df_sorted2["audience"], df_sorted2["total_signups"], color=DUSK)
    _style_axes(ax2)
    ax2.yaxis.tick_left()
    ax2.yaxis.set_label_position("left")
    ax2.set_title("Total signups", color=OCEAN, fontsize=10,
                  fontweight="bold", loc="left")
    fig.tight_layout()
    return _save_to_b64(fig)


def chart_funnel_waterfall(A: dict, kpi: dict) -> str:
    """Last-30d paid subscriber waterfall: starting → +new → +upgrades → -cancels → ending."""
    if A.get("pg_total_in") is None:
        return ""
    starting = (kpi.get("paid_subs", 0) or 0) - (A.get("pg_total_in", 0) - A.get("pg_cancels_final", 0))
    new = A.get("pg_new_paid", 0)
    up = A.get("pg_upgrades", 0)
    cancels = -A.get("pg_cancels_final", 0)
    ending = kpi.get("paid_subs", 0) or 0
    labels = ["Starting", "New paid", "Upgrades", "Cancels", "Ending"]
    values = [starting, new, up, cancels, ending]
    colors = [DOLDRUMS, STARBOARD, SEA, PORT, OCEAN]
    fig, ax = plt.subplots(figsize=(9, 3.4), facecolor="white")
    cumulative = [starting]
    for v in [new, up, cancels]:
        cumulative.append(cumulative[-1] + v)
    cumulative.append(ending)
    # Draw bars
    for i, (label, value, color) in enumerate(zip(labels, values, colors)):
        if i == 0 or i == len(labels) - 1:
            ax.bar(i, value, color=color, width=0.6)
            ax.text(i, value + 0.3, str(int(value)), ha="center", fontsize=10,
                    color=color, fontweight="bold")
        else:
            base = cumulative[i - 1]
            top = base + value
            ax.bar(i, value, bottom=base, color=color, width=0.6)
            sign = "+" if value >= 0 else ""
            ax.text(i, max(base, top) + 0.3, f"{sign}{int(value)}", ha="center",
                    fontsize=10, color=color, fontweight="bold")
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, fontsize=10)
    _style_axes(ax)
    ax.set_title("Paid subscriber waterfall — last 30d",
                 color=OCEAN, fontsize=11, fontweight="bold", loc="left")
    return _save_to_b64(fig)


def chart_free_paid_composition(subs: pd.DataFrame, emails: pd.DataFrame) -> str:
    """Stacked area: free vs paid over time."""
    if subs is None or emails is None or len(subs) == 0 or len(emails) == 0:
        return ""
    em = emails[emails["date"] >= emails["date"].max() - pd.Timedelta(days=180)].copy()
    sb = subs[subs["date"] >= subs["date"].max() - pd.Timedelta(days=180)].copy()
    merged = pd.merge(em, sb[["date", "paid", "comps"]], on="date", how="left").ffill().fillna(0)
    merged["paid_total"] = merged["paid"] + merged["comps"]
    merged["free"] = (merged["emails"] - merged["paid_total"]).clip(lower=0)
    fig, ax = plt.subplots(figsize=(9, 3.4), facecolor="white")
    ax.fill_between(merged["date"], 0, merged["free"], color=OCEAN, alpha=0.3, label="Free")
    ax.fill_between(merged["date"], merged["free"], merged["free"] + merged["paid_total"],
                    color=DUSK, alpha=0.8, label="Paid + Comps")
    ax.plot(merged["date"], merged["free"] + merged["paid_total"], color=OCEAN, linewidth=2)
    _style_axes(ax)
    ax.set_title("Subscriber composition — free vs paid (last 180d)",
                 color=OCEAN, fontsize=11, fontweight="bold", loc="left")
    ax.legend(loc="upper left", frameon=False, fontsize=9)
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
    return _save_to_b64(fig)


def chart_engagement_trend(es: pd.DataFrame) -> str:
    """Open rate and CTR rolling means over time."""
    if es is None or es.empty:
        return ""
    df = es.dropna(subset=["post_date"]).sort_values("post_date").copy()
    if len(df) < 3:
        return ""
    df["open_pct"] = df["open_rate"] * 100
    df["ctr_pct"] = df["click_through_rate"] * 100
    df["open_ma"] = df["open_pct"].rolling(5, min_periods=2).mean()
    df["ctr_ma"] = df["ctr_pct"].rolling(5, min_periods=2).mean()
    fig, ax = plt.subplots(figsize=(9, 3.4), facecolor="white")
    ax.scatter(df["post_date"], df["open_pct"], color=OCEAN, alpha=0.35, s=30, label="Open rate (per post)")
    ax.plot(df["post_date"], df["open_ma"], color=OCEAN, linewidth=2.6, label="Open 5-post MA")
    ax2 = ax.twinx()
    ax2.scatter(df["post_date"], df["ctr_pct"], color=DUSK, alpha=0.35, s=30)
    ax2.plot(df["post_date"], df["ctr_ma"], color=DUSK, linewidth=2.6, label="CTR 5-post MA")
    _style_axes(ax)
    ax2.tick_params(axis="y", colors=DUSK, labelsize=9, length=0)
    ax2.yaxis.tick_left()
    ax2.yaxis.set_label_position("left")
    for s in ax2.spines.values():
        s.set_visible(False)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.0f}%"))
    ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.1f}%"))
    ax.set_title("Engagement trend — open rate (Ocean, RHS) and CTR (Dusk, LHS)",
                 color=OCEAN, fontsize=11, fontweight="bold", loc="left")
    return _save_to_b64(fig)


# ---------------------------------------------------------------------------
# HTML rendering
# ---------------------------------------------------------------------------

def _icon_b64() -> str:
    if not ICON.exists():
        return ""
    return base64.b64encode(ICON.read_bytes()).decode("ascii")


def _fmt_int(x):
    return "—" if x is None else f"{int(x):,}"


def _fmt_money(x):
    return "—" if x is None else f"${float(x):,.0f}"


def _fmt_pct(x, digits=2):
    return "—" if x is None else f"{x*100:.{digits}f}%"


def _fmt_signed(x):
    if x is None:
        return "—"
    if x == 0:
        return "0"
    return f"+{int(x):,}" if x > 0 else f"{int(x):,}"


def _fmt_signed_pct(x, digits=1):
    if x is None:
        return "—"
    sign = "+" if x >= 0 else ""
    return f"{sign}{x:.{digits}f}%"


def kpi_card(label: str, value: str, delta: Optional[str] = None,
             delta_dir: str = "neutral", sub: Optional[str] = None) -> str:
    delta_html = ""
    if delta is not None:
        color = {"up": STARBOARD, "down": PORT, "neutral": DOLDRUMS}.get(delta_dir, DOLDRUMS)
        delta_html = f'<div class="delta" style="color:{color}">{delta}</div>'
    sub_html = f'<div class="sub">{sub}</div>' if sub else ""
    return f"""
        <div class="kpi">
          <div class="label">{label}</div>
          <div class="value">{value}</div>
          {delta_html}
          {sub_html}
        </div>
    """


def _build_kpi_tiles(kpi: dict) -> list[str]:
    tiles: list[str] = []
    tiles.append(kpi_card(
        "Total list", _fmt_int(kpi.get("total_subs")),
        delta=_fmt_signed(kpi.get("total_subs_30d")) + " /30d" if kpi.get("total_subs_30d") is not None else None,
        delta_dir="up" if (kpi.get("total_subs_30d") or 0) > 0 else "down" if (kpi.get("total_subs_30d") or 0) < 0 else "neutral",
        sub=f"{_fmt_signed(kpi.get('total_subs_7d'))} last 7d" if kpi.get("total_subs_7d") is not None else None,
    ))
    tiles.append(kpi_card(
        "Paid subscribers", _fmt_int(kpi.get("paid_subs")),
        delta=_fmt_signed(kpi.get("paid_subs_30d")) + " /30d" if kpi.get("paid_subs_30d") is not None else None,
        delta_dir="up" if (kpi.get("paid_subs_30d") or 0) > 0 else "down" if (kpi.get("paid_subs_30d") or 0) < 0 else "neutral",
        sub=f"{_fmt_signed(kpi.get('paid_subs_7d'))} last 7d · Comps {_fmt_int(kpi.get('comps'))}" if kpi.get("paid_subs_7d") is not None else None,
    ))
    tiles.append(kpi_card(
        "Free subscribers", _fmt_int(kpi.get("free_subs")),
        sub="Email list minus paid",
    ))
    tiles.append(kpi_card(
        "ARR", _fmt_money(kpi.get("arr")),
        delta=("+" if (kpi.get("arr_30d_change") or 0) >= 0 else "") + _fmt_money(kpi.get("arr_30d_change")) + " /30d" if kpi.get("arr_30d_change") is not None else None,
        delta_dir="up" if (kpi.get("arr_30d_change") or 0) > 0 else "down" if (kpi.get("arr_30d_change") or 0) < 0 else "neutral",
        sub=("+" if (kpi.get("arr_90d_change") or 0) >= 0 else "") + _fmt_money(kpi.get("arr_90d_change")) + " /90d" if kpi.get("arr_90d_change") is not None else None,
    ))
    tiles.append(kpi_card(
        "Followers", _fmt_int(kpi.get("followers")),
        delta=_fmt_signed(kpi.get("followers_30d")) + " /30d" if kpi.get("followers_30d") is not None else None,
        delta_dir="up" if (kpi.get("followers_30d") or 0) > 0 else "down" if (kpi.get("followers_30d") or 0) < 0 else "neutral",
    ))
    tiles.append(kpi_card(
        "Views (30d)", _fmt_int(kpi.get("views_30d")),
        delta=_fmt_signed_pct(kpi.get("views_30d_chg_pct")) + " vs prior 30d" if kpi.get("views_30d_chg_pct") is not None else None,
        delta_dir="up" if (kpi.get("views_30d_chg_pct") or 0) > 0 else "down" if (kpi.get("views_30d_chg_pct") or 0) < 0 else "neutral",
        sub=f"{_fmt_int(round(kpi.get('views_avg_30d') or 0))}/day avg",
    ))
    tiles.append(kpi_card(
        "Open rate (30d)", _fmt_pct(kpi.get("avg_open_rate_30d")),
        sub=f"CTR {_fmt_pct(kpi.get('avg_ctr_30d'))}",
    ))
    net_paid_30d = None
    if kpi.get("new_paid_30d") is not None and kpi.get("cancels_finalized_30d") is not None:
        net_paid_30d = kpi["new_paid_30d"] + (kpi.get("upgrades_30d") or 0) - kpi["cancels_finalized_30d"]
    tiles.append(kpi_card(
        "Paid flow (30d)", _fmt_signed(net_paid_30d) if net_paid_30d is not None else _fmt_int(kpi.get("new_paid_30d")),
        delta_dir="up" if (net_paid_30d or 0) > 0 else "down" if (net_paid_30d or 0) < 0 else "neutral",
        sub=f"+{_fmt_int(kpi.get('new_paid_30d'))} new · +{_fmt_int(kpi.get('upgrades_30d'))} upgrades · -{_fmt_int(kpi.get('cancels_finalized_30d'))} cancels",
    ))
    return tiles


def _chart_block(title: str, b64: str) -> str:
    if not b64:
        return ""
    return f'<section class="chart-block"><h3>{title}</h3><img src="data:image/png;base64,{b64}" /></section>'


def _takeaways_block(title: str, bullets: list[str]) -> str:
    if not bullets:
        return ""
    items = "".join(f"<li>{b}</li>" for b in bullets)
    return f"""
    <section class="takeaways">
      <h3>{title}</h3>
      <ul>{items}</ul>
    </section>
    """


def render_html(kpi: dict, charts: dict, tables: dict, stamp_human: str,
                missing: list[str], analysis: dict, takeaways: dict) -> str:
    icon_b64 = _icon_b64()
    icon_img = f'<img class="icon" src="data:image/png;base64,{icon_b64}" alt="LHM" />' if icon_b64 else ""

    tiles = _build_kpi_tiles(kpi)
    chart_block = _chart_block

    top_posts_html = tables.get("top_posts", "")
    recent_posts_html = tables.get("recent_posts", "")
    unsubs_html = tables.get("unsubs", "")
    growth_sources_table = tables.get("growth_sources", "")
    traffic_sources_table = tables.get("traffic_sources", "")

    missing_html = ""
    if missing:
        missing_html = f"""
        <div class="warning">
          Missing CSV inputs: {", ".join(missing)}. Sections that depend on these will be blank.
        </div>
        """

    css = f"""
    :root {{
      --ocean: {OCEAN};
      --dusk: {DUSK};
      --sky: {SKY};
      --venus: {VENUS};
      --sea: {SEA};
      --doldrums: {DOLDRUMS};
      --starboard: {STARBOARD};
      --port: {PORT};
      --fog: {FOG};
    }}
    * {{ box-sizing: border-box; }}
    body {{
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, sans-serif;
      margin: 0;
      background: #f7f9fb;
      color: #1a2332;
    }}
    header {{
      background: linear-gradient(135deg, var(--ocean) 0%, #1a6e96 100%);
      color: white;
      padding: 32px 40px 24px 40px;
      border-bottom: 4px solid var(--dusk);
      display: flex;
      align-items: center;
      gap: 18px;
      box-shadow: 0 2px 12px rgba(35,137,187,0.15);
    }}
    header .icon {{ height: 64px; width: auto; filter: brightness(0) invert(1); }}
    header h1 {{
      margin: 0;
      font-family: 'Montserrat', 'Inter', sans-serif;
      font-weight: 800;
      font-size: 28px;
      letter-spacing: 0.5px;
    }}
    header .tag {{
      font-size: 12px;
      letter-spacing: 3px;
      text-transform: uppercase;
      opacity: 0.85;
      margin-top: 2px;
    }}
    header .stamp {{
      margin-left: auto;
      font-size: 13px;
      opacity: 0.85;
      text-align: right;
    }}
    main {{
      max-width: 1280px;
      margin: 0 auto;
      padding: 0 32px 60px 32px;
    }}
    nav.tabs {{
      display: flex;
      gap: 4px;
      background: white;
      border-bottom: 1px solid #e5ecf2;
      padding: 0 32px;
      position: sticky;
      top: 0;
      z-index: 10;
      overflow-x: auto;
      box-shadow: 0 1px 4px rgba(0,0,0,0.04);
    }}
    nav.tabs button {{
      background: transparent;
      border: none;
      padding: 16px 20px 14px 20px;
      font-family: 'Montserrat', 'Inter', sans-serif;
      font-size: 12px;
      font-weight: 700;
      letter-spacing: 1.5px;
      text-transform: uppercase;
      color: var(--doldrums);
      cursor: pointer;
      border-bottom: 3px solid transparent;
      transition: color 0.15s, border-color 0.15s;
      white-space: nowrap;
    }}
    nav.tabs button:hover {{ color: var(--ocean); }}
    nav.tabs button.active {{
      color: var(--ocean);
      border-bottom-color: var(--dusk);
    }}
    .panel {{ display: none; padding-top: 28px; }}
    .panel.active {{ display: block; }}
    .panel-intro {{
      font-size: 13px;
      color: var(--doldrums);
      margin-bottom: 18px;
      max-width: 800px;
      line-height: 1.5;
    }}
    .kpi-grid {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 14px;
      margin-bottom: 24px;
    }}
    .kpi {{
      background: white;
      border: 1px solid #e5ecf2;
      border-left: 4px solid var(--ocean);
      border-radius: 8px;
      padding: 16px 18px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }}
    .kpi .label {{
      color: var(--doldrums);
      font-size: 11px;
      font-weight: 600;
      letter-spacing: 1.2px;
      text-transform: uppercase;
    }}
    .kpi .value {{
      color: var(--ocean);
      font-size: 28px;
      font-weight: 700;
      font-family: 'Montserrat', 'Inter', sans-serif;
      margin-top: 4px;
      letter-spacing: -0.5px;
    }}
    .kpi .delta {{ font-size: 12px; font-weight: 600; margin-top: 4px; }}
    .kpi .sub {{ font-size: 11px; color: var(--doldrums); margin-top: 2px; }}
    .chart-block {{
      background: white;
      border: 1px solid #e5ecf2;
      border-radius: 8px;
      padding: 16px 18px;
      margin-bottom: 16px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }}
    .chart-block h3 {{
      color: var(--ocean);
      font-family: 'Montserrat', 'Inter', sans-serif;
      font-size: 14px;
      letter-spacing: 1.5px;
      text-transform: uppercase;
      margin: 0 0 12px 0;
      padding-bottom: 8px;
      border-bottom: 2px solid #f0f4f7;
    }}
    .chart-block img {{ width: 100%; height: auto; display: block; }}
    .grid-2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 16px; }}
    .grid-2 .chart-block {{ margin-bottom: 0; }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 12px;
    }}
    th {{
      text-align: left;
      color: var(--doldrums);
      font-size: 10px;
      letter-spacing: 1px;
      text-transform: uppercase;
      padding: 8px 10px;
      border-bottom: 2px solid #e5ecf2;
    }}
    td {{
      padding: 8px 10px;
      border-bottom: 1px solid #f0f4f7;
      vertical-align: top;
    }}
    td.num {{ text-align: right; font-variant-numeric: tabular-nums; font-family: 'Source Code Pro', monospace; }}
    .chart-block table {{ margin-top: 4px; }}
    .takeaways {{
      background: linear-gradient(135deg, #f8fbfd 0%, #eef5fa 100%);
      border: 1px solid #d4e3ed;
      border-left: 4px solid var(--dusk);
      border-radius: 8px;
      padding: 18px 22px;
      margin-bottom: 18px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.03);
    }}
    .takeaways h3 {{
      color: var(--ocean);
      font-family: 'Montserrat', 'Inter', sans-serif;
      font-size: 13px;
      letter-spacing: 1.5px;
      text-transform: uppercase;
      margin: 0 0 10px 0;
    }}
    .takeaways ul {{
      margin: 0;
      padding-left: 20px;
    }}
    .takeaways li {{
      font-size: 13.5px;
      line-height: 1.55;
      margin-bottom: 10px;
      color: #1a2332;
    }}
    .takeaways li:last-child {{ margin-bottom: 0; }}
    .takeaways li::marker {{ color: var(--dusk); }}
    .warning {{
      background: #fff7ed;
      border: 1px solid #fed7aa;
      border-left: 4px solid var(--dusk);
      padding: 10px 14px;
      border-radius: 6px;
      font-size: 12px;
      color: #7c2d12;
      margin-bottom: 18px;
    }}
    footer {{
      text-align: center;
      color: var(--doldrums);
      font-size: 11px;
      letter-spacing: 2px;
      text-transform: uppercase;
      padding: 24px;
      border-top: 1px solid #e5ecf2;
      margin-top: 24px;
      background: white;
    }}
    footer span {{ color: var(--ocean); font-weight: 700; }}
    @media (max-width: 900px) {{
      .kpi-grid {{ grid-template-columns: repeat(2, 1fr); }}
      .grid-2 {{ grid-template-columns: 1fr; }}
      nav.tabs {{ padding: 0 16px; }}
      main {{ padding: 0 16px 40px 16px; }}
    }}
    """

    js = """
    function showPanel(id, btn) {
      document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
      document.querySelectorAll('nav.tabs button').forEach(b => b.classList.remove('active'));
      document.getElementById(id).classList.add('active');
      btn.classList.add('active');
      window.scrollTo({top: 0, behavior: 'smooth'});
    }
    """

    # ---- Build each panel ----
    overview = f"""
      <div class="panel-intro">
        High-level state of the publication. Subscriber base, revenue, reach, engagement, paid flow.
        Use this view as the daily check. The other tabs go deeper.
      </div>
      <div class="kpi-grid">{''.join(tiles)}</div>
      {_takeaways_block("Bottom Line", takeaways.get('overview', []))}
      {_chart_block("Subscribers — total list and paid", charts.get("subscribers", ""))}
      <div class="grid-2">
        {_chart_block("Annual recurring revenue", charts.get("arr", ""))}
        {_chart_block("Daily traffic", charts.get("traffic", ""))}
      </div>
    """

    growth = f"""
      <div class="panel-intro">
        Where new visitors and subscribers come from, and which channels actually convert.
        Substack-internal, social, search, direct, email referrals each behave differently.
      </div>
      {_takeaways_block("What's Working, What's Not", takeaways.get('growth', []))}
      {_chart_block("Acquisition funnel by category", charts.get("source_funnel", ""))}
      <div class="grid-2">
        {_chart_block("New revenue by category", charts.get("revenue_by_source", ""))}
        {_chart_block("Top growth sources (top 10)", charts.get("growth_sources", ""))}
      </div>
      <div class="chart-block">
        <h3>Growth sources detail</h3>
        {growth_sources_table}
      </div>
    """

    engagement = f"""
      <div class="panel-intro">
        Open rates, click-through, engagement by post type and audience segment.
        How the list responds to the work, both quantitatively and over time.
      </div>
      {_takeaways_block("Engagement Read", takeaways.get('engagement', []))}
      {_chart_block("Engagement trend — open and click rates over time", charts.get("engagement_trend", ""))}
      {_chart_block("Email engagement — last 20 posts", charts.get("email_engagement", ""))}
      {_chart_block("Post type performance — reach vs engagement", charts.get("post_type_performance", ""))}
    """

    funnel = f"""
      <div class="panel-intro">
        How subscribers move from free to paid. Direct conversions, upgrades from the free list,
        trials, cancellations. The conversion physics of the publication.
      </div>
      {_takeaways_block("Funnel Mechanics", takeaways.get('funnel', []))}
      {_chart_block("Paid subscriber waterfall — last 30d", charts.get("funnel_waterfall", ""))}
      <div class="grid-2">
        {_chart_block("Free vs paid composition (180d)", charts.get("free_paid_composition", ""))}
        {_chart_block("Paid subscriber daily flow", charts.get("paid_growth", ""))}
      </div>
      <div class="chart-block">
        <h3>Recent unsubscribes</h3>
        {unsubs_html}
      </div>
    """

    content_panel = f"""
      <div class="panel-intro">
        Post-level performance. Which titles drove signups, which converted to paid,
        which audiences and formats are pulling weight.
      </div>
      {_takeaways_block("Editorial Read", takeaways.get('content', []))}
      {_chart_block("Audience segment split — views and signups", charts.get("audience_split", ""))}
      <div class="chart-block">
        <h3>Top posts (30d) by views</h3>
        {top_posts_html}
      </div>
      <div class="chart-block">
        <h3>Recent posts</h3>
        {recent_posts_html}
      </div>
    """

    audience = f"""
      <div class="panel-intro">
        Who the readers are. Geographic distribution, the follower-to-email ratio,
        traffic source mix. Where the audience lives, literally and structurally.
      </div>
      {_takeaways_block("Audience Composition", takeaways.get('audience', []))}
      <div class="grid-2">
        {_chart_block("Audience location — top free signup sources", charts.get("audience_location", ""))}
        {_chart_block("Traffic sources by views", charts.get("traffic_sources", ""))}
      </div>
      <div class="chart-block">
        <h3>Traffic source detail</h3>
        {traffic_sources_table}
      </div>
    """

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Lighthouse Macro - Substack Dashboard</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Montserrat:wght@600;700;800&family=Source+Code+Pro:wght@400;600&display=swap" rel="stylesheet" />
  <style>{css}</style>
</head>
<body>
  <header>
    {icon_img}
    <div>
      <h1>SUBSTACK DASHBOARD</h1>
      <div class="tag">MACRO, ILLUMINATED.</div>
    </div>
    <div class="stamp">
      <div>Generated {stamp_human}</div>
      <div>research.lighthousemacro.com</div>
    </div>
  </header>
  <nav class="tabs">
    <button class="active" onclick="showPanel('panel-overview', this)">Overview</button>
    <button onclick="showPanel('panel-growth', this)">Growth Engine</button>
    <button onclick="showPanel('panel-engagement', this)">Engagement</button>
    <button onclick="showPanel('panel-funnel', this)">Funnel</button>
    <button onclick="showPanel('panel-content', this)">Content</button>
    <button onclick="showPanel('panel-audience', this)">Audience</button>
  </nav>
  <main>
    {missing_html}
    <section id="panel-overview" class="panel active">{overview}</section>
    <section id="panel-growth" class="panel">{growth}</section>
    <section id="panel-engagement" class="panel">{engagement}</section>
    <section id="panel-funnel" class="panel">{funnel}</section>
    <section id="panel-content" class="panel">{content_panel}</section>
    <section id="panel-audience" class="panel">{audience}</section>
  </main>
  <footer>
    <span>LIGHTHOUSE MACRO</span> · INTERNAL · DO NOT DISTRIBUTE
  </footer>
  <script>{js}</script>
</body>
</html>
"""
    return html


# ---------------------------------------------------------------------------
# Tables
# ---------------------------------------------------------------------------

def _s(v) -> str:
    """Stringify any cell, returning '' for NaN/None."""
    if v is None:
        return ""
    try:
        if pd.isna(v):
            return ""
    except (TypeError, ValueError):
        pass
    return str(v)


def table_top_posts(es: pd.DataFrame) -> str:
    if es is None or es.empty:
        return "<p style='color:#898989;font-size:12px'>No email stats available.</p>"
    cutoff = pd.Timestamp.utcnow() - pd.Timedelta(days=30)
    df = es[es["post_date"] >= cutoff].copy()
    if df.empty:
        df = es.head(10).copy()
    df = df.sort_values("views", ascending=False).head(10)
    rows = []
    for _, r in df.iterrows():
        title = _s(r.get("title")).replace("<", "&lt;").replace(">", "&gt;")
        date = r["post_date"].strftime("%Y-%m-%d") if pd.notna(r["post_date"]) else "—"
        views = _fmt_int(r.get("views"))
        opens = _fmt_pct(r.get("open_rate"))
        ctr = _fmt_pct(r.get("click_through_rate"))
        eng = _fmt_pct(r.get("engagement_rate"))
        rows.append(f"<tr><td>{date}</td><td>{title}</td>"
                    f"<td class='num'>{views}</td>"
                    f"<td class='num'>{opens}</td>"
                    f"<td class='num'>{ctr}</td>"
                    f"<td class='num'>{eng}</td></tr>")
    return ("<table><thead><tr>"
            "<th>Date</th><th>Title</th>"
            "<th style='text-align:right'>Views</th>"
            "<th style='text-align:right'>Open</th>"
            "<th style='text-align:right'>CTR</th>"
            "<th style='text-align:right'>Engagement</th>"
            "</tr></thead><tbody>" + "".join(rows) + "</tbody></table>")


def table_recent_posts(es: pd.DataFrame) -> str:
    if es is None or es.empty:
        return "<p style='color:#898989;font-size:12px'>No email stats available.</p>"
    df = es.head(10).copy()
    rows = []
    for _, r in df.iterrows():
        title = _s(r.get("title")).replace("<", "&lt;").replace(">", "&gt;")
        date = r["post_date"].strftime("%Y-%m-%d") if pd.notna(r["post_date"]) else "—"
        section = _s(r.get("section_name")) or _s(r.get("audience")) or ""
        views = _fmt_int(r.get("views"))
        opens = _fmt_pct(r.get("open_rate"))
        signups = _fmt_int(r.get("signups"))
        subs = _fmt_int(r.get("subscribes"))
        rows.append(f"<tr><td>{date}</td><td>{title}</td><td>{section}</td>"
                    f"<td class='num'>{views}</td>"
                    f"<td class='num'>{opens}</td>"
                    f"<td class='num'>{signups}</td>"
                    f"<td class='num'>{subs}</td></tr>")
    return ("<table><thead><tr>"
            "<th>Date</th><th>Title</th><th>Audience</th>"
            "<th style='text-align:right'>Views</th>"
            "<th style='text-align:right'>Open</th>"
            "<th style='text-align:right'>Signups</th>"
            "<th style='text-align:right'>Subs</th>"
            "</tr></thead><tbody>" + "".join(rows) + "</tbody></table>")


def _load_resubbed_emails() -> set[str]:
    """Read RESUBBED_FILE and return a normalized set of email addresses
    that have re-subscribed since their unsubscribe event."""
    if not RESUBBED_FILE.exists():
        return set()
    out = set()
    for line in RESUBBED_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        out.add(line.lower())
    return out


def table_unsubs(unsubs: pd.DataFrame) -> str:
    if unsubs is None or unsubs.empty:
        return "<p style='color:#898989;font-size:12px'>No unsubscribes recorded.</p>"
    resubbed = _load_resubbed_emails()
    df = unsubs.copy()
    if "unsubscribed_at" in df.columns:
        df = df.sort_values("unsubscribed_at", ascending=False)
    df = df.head(20)
    rows = []
    active_count = 0
    resubbed_count = 0
    for _, r in df.iterrows():
        when = r["unsubscribed_at"].strftime("%Y-%m-%d") if "unsubscribed_at" in df.columns and pd.notna(r["unsubscribed_at"]) else "—"
        email_raw = _s(r.get("email")).strip()
        email = email_raw.replace("<", "&lt;")
        bucket = _s(r.get("cancel_reason_bucket"))
        feedback = _s(r.get("feedback")).replace("<", "&lt;").replace(">", "&gt;")
        is_resub = email_raw.lower() in resubbed
        if is_resub:
            resubbed_count += 1
            row_style = " style='opacity:0.55;background:#f4faf6'"
            badge = (f"<span style='display:inline-block;background:{STARBOARD};color:white;"
                     f"padding:1px 7px;border-radius:10px;font-size:9px;font-weight:700;"
                     f"letter-spacing:1px;text-transform:uppercase;margin-left:6px'>Resubbed</span>")
            email_cell = f"{email}{badge}"
        else:
            active_count += 1
            row_style = ""
            email_cell = email
        rows.append(f"<tr{row_style}><td>{when}</td><td>{email_cell}</td><td>{bucket}</td><td>{feedback}</td></tr>")
    summary = (f"<div style='font-size:11px;color:{DOLDRUMS};margin-bottom:10px'>"
               f"Showing {len(rows)} unsubscribe events. "
               f"<strong style='color:{PORT}'>{active_count} still off the list.</strong> "
               f"<strong style='color:{STARBOARD}'>{resubbed_count} re-subscribed</strong> "
               f"(tracked in <code>{RESUBBED_FILE.name}</code>).</div>") if rows else ""
    return (summary + "<table><thead><tr>"
            "<th>When</th><th>Email</th><th>Reason</th><th>Feedback</th>"
            "</tr></thead><tbody>" + "".join(rows) + "</tbody></table>")


def table_growth_sources(A: dict) -> str:
    src = A.get("growth_top_sources")
    if src is None or src.empty:
        return "<p style='color:#898989;font-size:12px'>No growth source data.</p>"
    rows = []
    for _, r in src.iterrows():
        name = _s(r.get("source")).replace("<", "&lt;")
        if len(name) > 60:
            name = name[:60] + "..."
        rows.append(
            f"<tr><td>{name}</td>"
            f"<td class='num'>{int(r['unique_visitors']):,}</td>"
            f"<td class='num'>{int(r['new_subscribers'])}</td>"
            f"<td class='num'>${int(r['new_revenue']):,}</td></tr>"
        )
    return ("<table><thead><tr>"
            "<th>Source</th>"
            "<th style='text-align:right'>Visitors</th>"
            "<th style='text-align:right'>New subs</th>"
            "<th style='text-align:right'>Revenue</th>"
            "</tr></thead><tbody>" + "".join(rows) + "</tbody></table>")


def table_traffic_sources(A: dict) -> str:
    df = A.get("traffic_sources")
    if df is None or df.empty:
        return "<p style='color:#898989;font-size:12px'>No traffic source data.</p>"
    df = df.sort_values("views", ascending=False).head(15)
    rows = []
    for _, r in df.iterrows():
        src = _s(r.get("source"))
        cat = _s(r.get("source_category"))
        views = _fmt_int(r.get("views"))
        users = _fmt_int(r.get("users"))
        signups = _fmt_int(r.get("free_signup")) if pd.notna(r.get("free_signup")) else "—"
        subs = _fmt_int(r.get("subscribed")) if pd.notna(r.get("subscribed")) else "—"
        rows.append(
            f"<tr><td>{src}</td><td>{cat}</td>"
            f"<td class='num'>{views}</td>"
            f"<td class='num'>{users}</td>"
            f"<td class='num'>{signups}</td>"
            f"<td class='num'>{subs}</td></tr>"
        )
    return ("<table><thead><tr>"
            "<th>Source</th><th>Category</th>"
            "<th style='text-align:right'>Views</th>"
            "<th style='text-align:right'>Users</th>"
            "<th style='text-align:right'>Signups</th>"
            "<th style='text-align:right'>Subs</th>"
            "</tr></thead><tbody>" + "".join(rows) + "</tbody></table>")


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------

def run() -> Path:
    now = datetime.now()
    stamp = now.strftime("%Y-%m-%d_%H%M")
    stamp_human = now.strftime("%Y-%m-%d %H:%M %Z").strip() or now.strftime("%Y-%m-%d %H:%M")

    picks = discover_csvs()
    if not picks:
        raise SystemExit("No Substack CSVs found in ~/Downloads. Drop today's exports there and re-run.")
    archive_snapshot(picks, stamp)

    loaders = {
        "arr": load_arr,
        "audience_location": load_audience_location,
        "email_stats": load_email_stats,
        "emails": load_emails,
        "followers": load_followers,
        "growth_sources": load_growth_sources,
        "paid_subscriber_growth": load_paid_growth,
        "free_subscriber_growth": load_paid_growth,  # same schema if present
        "subscribers": load_subscribers,
        "traffic": load_traffic,
        "traffic_sources": load_traffic_sources,
        "unsubscribes": load_unsubscribes,
    }

    data: dict = {}
    for t, pick in picks.items():
        try:
            data[t] = loaders[t](pick.path)
            log.info("loaded %s: %d rows", t, len(data[t]))
        except Exception as exc:
            log.exception("failed to load %s: %s", t, exc)

    kpi = compute_kpis(data)
    append_kpi_history(kpi, stamp)

    analysis = analyze(data, kpi)

    takeaways = {
        "overview":   takeaways_overview(kpi, analysis),
        "growth":     takeaways_growth(analysis),
        "engagement": takeaways_engagement(kpi, analysis),
        "funnel":     takeaways_funnel(kpi, analysis),
        "content":    takeaways_content(analysis),
        "audience":   takeaways_audience(kpi, analysis),
    }

    charts: dict = {}
    if "subscribers" in data:        charts["subscribers"] = chart_subscribers(data["subscribers"], data.get("emails"))
    if "arr" in data:                charts["arr"] = chart_arr(data["arr"])
    if "traffic" in data:            charts["traffic"] = chart_traffic(data["traffic"])
    if "traffic_sources" in data:    charts["traffic_sources"] = chart_traffic_sources(data["traffic_sources"])
    if "growth_sources" in data:     charts["growth_sources"] = chart_growth_sources(data["growth_sources"])
    if "audience_location" in data:  charts["audience_location"] = chart_audience_location(data["audience_location"])
    if "paid_subscriber_growth" in data: charts["paid_growth"] = chart_paid_growth(data["paid_subscriber_growth"])
    if "email_stats" in data:        charts["email_engagement"] = chart_email_engagement(data["email_stats"])

    # Analysis-panel charts
    charts["source_funnel"] = chart_source_funnel(analysis)
    charts["revenue_by_source"] = chart_revenue_by_source(analysis)
    charts["post_type_performance"] = chart_post_type_performance(analysis)
    charts["audience_split"] = chart_audience_split(analysis, kpi)
    charts["funnel_waterfall"] = chart_funnel_waterfall(analysis, kpi)
    if "subscribers" in data and "emails" in data:
        charts["free_paid_composition"] = chart_free_paid_composition(data["subscribers"], data["emails"])
    if "email_stats" in data:
        charts["engagement_trend"] = chart_engagement_trend(data["email_stats"])

    tables = {
        "top_posts": table_top_posts(data.get("email_stats")),
        "recent_posts": table_recent_posts(data.get("email_stats")),
        "unsubs": table_unsubs(data.get("unsubscribes")),
        "growth_sources": table_growth_sources(analysis),
        "traffic_sources": table_traffic_sources(analysis),
    }

    missing = [t for t in CSV_TYPES if t not in picks and t != "free_subscriber_growth"]
    html = render_html(kpi, charts, tables, stamp_human, missing, analysis, takeaways)

    versioned = OUT_DIR / f"dashboard_{stamp}.html"
    latest = OUT_DIR / "dashboard_latest.html"
    versioned.write_text(html, encoding="utf-8")
    latest.write_text(html, encoding="utf-8")
    (OUT_DIR / "kpi_latest.json").write_text(json.dumps(kpi, indent=2, default=str), encoding="utf-8")
    log.info("wrote %s (%d KB)", latest, len(html) // 1024)
    return latest


if __name__ == "__main__":
    out = run()
    print(out)
