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

    subs = data.get("subscribers")
    if subs is not None and len(subs):
        last = subs.iloc[-1]
        d7 = subs[subs["date"] >= subs["date"].max() - pd.Timedelta(days=7)]
        d30 = subs[subs["date"] >= subs["date"].max() - pd.Timedelta(days=30)]
        kpi["total_subs"] = safe_int(last.get("total_subscribers"))
        kpi["paid_subs"] = safe_int(last.get("paid"))
        kpi["free_trials"] = safe_int(last.get("free_trials"))
        kpi["comps"] = safe_int(last.get("comps"))
        kpi["gifts"] = safe_int(last.get("gifts"))
        if len(d7) >= 2:
            kpi["total_subs_7d"] = safe_int(last.get("total_subscribers")) - safe_int(d7.iloc[0].get("total_subscribers"))
            kpi["paid_subs_7d"]  = safe_int(last.get("paid")) - safe_int(d7.iloc[0].get("paid"))
        if len(d30) >= 2:
            kpi["total_subs_30d"] = safe_int(last.get("total_subscribers")) - safe_int(d30.iloc[0].get("total_subscribers"))
            kpi["paid_subs_30d"]  = safe_int(last.get("paid")) - safe_int(d30.iloc[0].get("paid"))

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


def chart_subscribers(subs: pd.DataFrame) -> str:
    df = subs[subs["date"] >= subs["date"].max() - pd.Timedelta(days=180)].copy()
    fig, ax = plt.subplots(figsize=(9, 3.6), facecolor="white")
    ax.fill_between(df["date"], 0, df["total_subscribers"], color=OCEAN, alpha=0.10)
    ax.plot(df["date"], df["total_subscribers"], color=OCEAN, linewidth=2.8, label="Total")
    if "paid" in df.columns:
        ax.plot(df["date"], df["paid"], color=DUSK, linewidth=2.4, label="Paid")
    _style_axes(ax)
    ax.set_title("Subscribers — last 180d", color=OCEAN, fontsize=11, fontweight="bold", loc="left")
    ax.legend(loc="upper left", frameon=False, fontsize=9)
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
    ax.set_xlim(df["date"].min(), df["date"].max() + pd.Timedelta(days=2))
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


def render_html(kpi: dict, charts: dict, tables: dict, stamp_human: str,
                missing: list[str]) -> str:
    icon_b64 = _icon_b64()
    icon_img = f'<img class="icon" src="data:image/png;base64,{icon_b64}" alt="LHM" />' if icon_b64 else ""

    # KPI tiles
    tiles: list[str] = []
    tiles.append(kpi_card(
        "Total subscribers", _fmt_int(kpi.get("total_subs")),
        delta=_fmt_signed(kpi.get("total_subs_30d")) + " /30d" if kpi.get("total_subs_30d") is not None else None,
        delta_dir="up" if (kpi.get("total_subs_30d") or 0) > 0 else "down" if (kpi.get("total_subs_30d") or 0) < 0 else "neutral",
        sub=f"{_fmt_signed(kpi.get('total_subs_7d'))} last 7d" if kpi.get("total_subs_7d") is not None else None,
    ))
    tiles.append(kpi_card(
        "Paid subscribers", _fmt_int(kpi.get("paid_subs")),
        delta=_fmt_signed(kpi.get("paid_subs_30d")) + " /30d" if kpi.get("paid_subs_30d") is not None else None,
        delta_dir="up" if (kpi.get("paid_subs_30d") or 0) > 0 else "down" if (kpi.get("paid_subs_30d") or 0) < 0 else "neutral",
        sub=f"{_fmt_signed(kpi.get('paid_subs_7d'))} last 7d" if kpi.get("paid_subs_7d") is not None else None,
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
    tiles.append(kpi_card(
        "New paid (30d)", _fmt_int(kpi.get("new_paid_30d")),
        sub=f"Upgrades {_fmt_int(kpi.get('upgrades_30d'))} · Trials {_fmt_int(kpi.get('trials_started_30d'))}",
    ))
    tiles.append(kpi_card(
        "Cancels (30d)", _fmt_int(kpi.get("cancels_finalized_30d")),
        delta_dir="down" if (kpi.get("cancels_finalized_30d") or 0) > 0 else "neutral",
    ))

    def chart_block(title: str, b64: str) -> str:
        if not b64:
            return ""
        return f'<section class="chart-block"><h3>{title}</h3><img src="data:image/png;base64,{b64}" /></section>'

    chart_html = "\n".join([
        chart_block("Subscribers", charts.get("subscribers", "")),
        chart_block("Annual recurring revenue", charts.get("arr", "")),
        chart_block("Daily traffic", charts.get("traffic", "")),
        chart_block("Paid subscriber flow", charts.get("paid_growth", "")),
        chart_block("Email engagement", charts.get("email_engagement", "")),
        chart_block("Traffic sources", charts.get("traffic_sources", "")),
        chart_block("Growth sources", charts.get("growth_sources", "")),
        chart_block("Audience location", charts.get("audience_location", "")),
    ])

    top_posts_html = tables.get("top_posts", "")
    recent_posts_html = tables.get("recent_posts", "")
    unsubs_html = tables.get("unsubs", "")

    missing_html = ""
    if missing:
        missing_html = f"""
        <div class="warning">
          Missing CSV inputs: {", ".join(missing)} — sections that depend on these will be blank.
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
      padding: 28px 32px 60px 32px;
    }}
    .kpi-grid {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 14px;
      margin-bottom: 28px;
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
    }}
    footer span {{ color: var(--ocean); font-weight: 700; }}
    @media (max-width: 900px) {{
      .kpi-grid {{ grid-template-columns: repeat(2, 1fr); }}
      .grid-2 {{ grid-template-columns: 1fr; }}
    }}
    """

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Lighthouse Macro — Substack Dashboard</title>
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
  <main>
    {missing_html}
    <div class="kpi-grid">
      {''.join(tiles)}
    </div>

    {chart_block("Subscribers", charts.get("subscribers", ""))}

    <div class="grid-2">
      {chart_block("Annual recurring revenue", charts.get("arr", ""))}
      {chart_block("Paid subscriber flow", charts.get("paid_growth", ""))}
    </div>

    {chart_block("Daily traffic", charts.get("traffic", ""))}

    {chart_block("Email engagement — last 20 posts", charts.get("email_engagement", ""))}

    <div class="chart-block">
      <h3>Top posts (30d) — by views</h3>
      {top_posts_html}
    </div>

    <div class="chart-block">
      <h3>Recent posts</h3>
      {recent_posts_html}
    </div>

    <div class="grid-2">
      {chart_block("Traffic sources", charts.get("traffic_sources", ""))}
      {chart_block("Audience location", charts.get("audience_location", ""))}
    </div>

    {chart_block("Growth sources", charts.get("growth_sources", ""))}

    <div class="chart-block">
      <h3>Recent unsubscribes</h3>
      {unsubs_html}
    </div>
  </main>
  <footer>
    <span>LIGHTHOUSE MACRO</span> · INTERNAL · DO NOT DISTRIBUTE
  </footer>
</body>
</html>
"""
    return html


# ---------------------------------------------------------------------------
# Tables
# ---------------------------------------------------------------------------

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
        title = (r.get("title") or "").replace("<", "&lt;").replace(">", "&gt;")
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
        title = (r.get("title") or "").replace("<", "&lt;").replace(">", "&gt;")
        date = r["post_date"].strftime("%Y-%m-%d") if pd.notna(r["post_date"]) else "—"
        section = r.get("section_name") or r.get("audience") or ""
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


def table_unsubs(unsubs: pd.DataFrame) -> str:
    if unsubs is None or unsubs.empty:
        return "<p style='color:#898989;font-size:12px'>No unsubscribes recorded.</p>"
    df = unsubs.copy()
    if "unsubscribed_at" in df.columns:
        df = df.sort_values("unsubscribed_at", ascending=False)
    df = df.head(15)
    rows = []
    for _, r in df.iterrows():
        when = r["unsubscribed_at"].strftime("%Y-%m-%d") if "unsubscribed_at" in df.columns and pd.notna(r["unsubscribed_at"]) else "—"
        email = (r.get("email") or "").replace("<", "&lt;")
        bucket = r.get("cancel_reason_bucket") or ""
        feedback = (r.get("feedback") or "").replace("<", "&lt;").replace(">", "&gt;")
        rows.append(f"<tr><td>{when}</td><td>{email}</td><td>{bucket}</td><td>{feedback}</td></tr>")
    return ("<table><thead><tr>"
            "<th>When</th><th>Email</th><th>Reason</th><th>Feedback</th>"
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

    charts: dict = {}
    if "subscribers" in data:        charts["subscribers"] = chart_subscribers(data["subscribers"])
    if "arr" in data:                charts["arr"] = chart_arr(data["arr"])
    if "traffic" in data:            charts["traffic"] = chart_traffic(data["traffic"])
    if "traffic_sources" in data:    charts["traffic_sources"] = chart_traffic_sources(data["traffic_sources"])
    if "growth_sources" in data:     charts["growth_sources"] = chart_growth_sources(data["growth_sources"])
    if "audience_location" in data:  charts["audience_location"] = chart_audience_location(data["audience_location"])
    if "paid_subscriber_growth" in data: charts["paid_growth"] = chart_paid_growth(data["paid_subscriber_growth"])
    if "email_stats" in data:        charts["email_engagement"] = chart_email_engagement(data["email_stats"])

    tables = {
        "top_posts": table_top_posts(data.get("email_stats")),
        "recent_posts": table_recent_posts(data.get("email_stats")),
        "unsubs": table_unsubs(data.get("unsubscribes")),
    }

    missing = [t for t in CSV_TYPES if t not in picks and t != "free_subscriber_growth"]
    html = render_html(kpi, charts, tables, stamp_human, missing)

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
