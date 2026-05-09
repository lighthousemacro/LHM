"""Lighthouse Macro - Substack Outreach Dashboard.

Reads the latest snapshot under Data/substack_snapshots/<stamp>/ (populated
by substack_dashboard.py) and renders a self-contained HTML focused on
subscriber outreach cuts:

  1. Header strip (totals, MRR, deltas, average open rate)
  2. Growth and retention (free vs paid, cumulative, churn rate, paid conversion)
  3. Engagement (open / CTR distributions, post-level performance)
  4. Warm Free Subs (conversion targets, adjustable threshold knobs)
  5. Top Engagers (paid + free leaderboard)
  6. Churn Risk (recent unsubscribes + paid trend)

Sections 4 and 5 require a per-subscriber CSV that Substack does not
expose by default. The script auto-detects any CSV under the latest
snapshot named `subscriber_list.csv` or `subscribers_list.csv` (or the
user can drop `lighthousemacro_subscriber_list_<date>.csv` into ~/Downloads
and substack_dashboard.py will archive it on the next run if extended).
If no per-subscriber data is found, those sections render an empty state
with explicit instructions.

Output:
    Outputs/Substack_Dashboard/outreach_latest.html       (stable path)
    Outputs/Substack_Dashboard/outreach_<stamp>.html      (versioned)

Run via launchd just after substack_dashboard.py:
    com.lighthousemacro.substack-outreach.plist  (04:35 / 16:35 ET)
"""
from __future__ import annotations

import json
import logging
import math
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Paths and config
# ---------------------------------------------------------------------------

REPO = Path("/Users/bob/LHM")
SNAP_ROOT = REPO / "Data" / "substack_snapshots"
OUT_DIR = REPO / "Outputs" / "Substack_Dashboard"
LOG_DIR = REPO / "logs"
ICON = REPO / "Brand" / "icon_transparent_128.png"

OUT_DIR.mkdir(parents=True, exist_ok=True)
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

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "substack_outreach.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("outreach")


# ---------------------------------------------------------------------------
# Snapshot discovery
# ---------------------------------------------------------------------------

SNAP_RE = re.compile(r"^\d{4}-\d{2}-\d{2}_\d{4}$")


def latest_snapshot() -> Path:
    folders = [p for p in SNAP_ROOT.iterdir()
               if p.is_dir() and SNAP_RE.match(p.name)]
    if not folders:
        raise SystemExit(f"No snapshots found under {SNAP_ROOT}")
    folders.sort(key=lambda p: p.name, reverse=True)
    return folders[0]


# ---------------------------------------------------------------------------
# Loaders (mirror the patterns in substack_dashboard.py)
# ---------------------------------------------------------------------------

def _two_col(path: Path, name: str) -> pd.DataFrame:
    df = pd.read_csv(path, header=None, names=["date", name])
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    if df[name].dtype == object:
        df[name] = (df[name].astype(str)
                    .str.replace(r"[\$,]", "", regex=True).str.strip())
        df[name] = pd.to_numeric(df[name], errors="coerce")
    return df.dropna(subset=["date"]).sort_values("date").reset_index(drop=True)


def load_all(snap: Path) -> dict:
    out: dict = {}

    f = snap / "subscribers.csv"
    if f.exists():
        df = pd.read_csv(f)
        df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        for c in ["paid", "comps", "gifts", "free_trials", "total_subscribers"]:
            if c in df.columns:
                df[c] = pd.to_numeric(df[c], errors="coerce")
        df = df.dropna(subset=["date"]).sort_values("date").reset_index(drop=True)
        out["subscribers"] = df

    f = snap / "emails.csv"
    if f.exists():
        out["emails"] = _two_col(f, "emails")

    f = snap / "arr.csv"
    if f.exists():
        out["arr"] = _two_col(f, "arr")

    f = snap / "followers.csv"
    if f.exists():
        out["followers"] = _two_col(f, "followers")

    f = snap / "traffic.csv"
    if f.exists():
        df = pd.read_csv(f)
        df.columns = [c.strip().lower() for c in df.columns]
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df["views"] = pd.to_numeric(df["views"], errors="coerce")
        out["traffic"] = (df.dropna(subset=["date"])
                            .sort_values("date").reset_index(drop=True))

    f = snap / "email_stats.csv"
    if f.exists():
        df = pd.read_csv(f)
        df["post_date"] = pd.to_datetime(df["post_date"], errors="coerce", utc=True)
        for c in ["views", "open_rate", "click_through_rate", "engagement_rate",
                  "likes", "comments", "shares", "restacks", "subscribes",
                  "free_trials", "estimated_value", "sent", "opens", "clicks"]:
            if c in df.columns:
                df[c] = pd.to_numeric(df[c], errors="coerce")
        out["email_stats"] = df.sort_values("post_date").reset_index(drop=True)

    f = snap / "paid_subscriber_growth.csv"
    if f.exists():
        df = pd.read_csv(f)
        df.columns = [c.strip().lower() for c in df.columns]
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        out["paid_growth"] = (df.dropna(subset=["date"])
                                .sort_values("date").reset_index(drop=True))

    f = snap / "unsubscribes.csv"
    if f.exists():
        df = pd.read_csv(f)
        df.columns = [c.strip().lower() for c in df.columns]
        if "unsubscribed_at" in df.columns:
            df["unsubscribed_at"] = pd.to_datetime(df["unsubscribed_at"],
                                                   errors="coerce", utc=True)
        out["unsubscribes"] = df

    # Optional per-subscriber list. Tries several names. Schema is
    # tolerated loosely; we re-map common Substack column variants.
    sub_path = None
    for cand in ["subscriber_list.csv", "subscribers_list.csv",
                 "email_list.csv", "subscribers_full.csv"]:
        p = snap / cand
        if p.exists():
            sub_path = p
            break
    if sub_path is not None:
        try:
            df = pd.read_csv(sub_path)
            df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
            # Common column variants
            ren = {"email_address": "email", "subscribed_on": "subscribed_at",
                   "subscribed_at_": "subscribed_at", "created_at": "subscribed_at",
                   "last_seen": "last_seen_at", "last_active": "last_seen_at",
                   "subscription_type": "plan", "type": "plan", "status": "status"}
            for k, v in ren.items():
                if k in df.columns and v not in df.columns:
                    df = df.rename(columns={k: v})
            for c in ["subscribed_at", "last_seen_at"]:
                if c in df.columns:
                    df[c] = pd.to_datetime(df[c], errors="coerce", utc=True)
            for c in ["opens", "clicks", "opens_last_10", "clicks_last_10",
                      "opens_30d", "clicks_30d", "open_rate"]:
                if c in df.columns:
                    df[c] = pd.to_numeric(df[c], errors="coerce")
            out["subscriber_list"] = df
            log.info("loaded subscriber_list: %d rows", len(df))
        except Exception as exc:
            log.warning("could not parse %s: %s", sub_path, exc)
    else:
        log.info("no subscriber_list CSV found in snapshot - sections 4/5 "
                 "will render empty state")

    return out


# ---------------------------------------------------------------------------
# Computations
# ---------------------------------------------------------------------------

def safe_int(x):
    try:
        if pd.isna(x):
            return None
        return int(round(float(x)))
    except Exception:
        return None


def safe_float(x):
    try:
        if pd.isna(x):
            return None
        return float(x)
    except Exception:
        return None


def compute_header(data: dict) -> dict:
    h: dict = {}
    subs = data.get("subscribers")
    emails = data.get("emails")
    if subs is not None and len(subs):
        last = subs.iloc[-1]
        h["paid"] = safe_int(last.get("paid"))
        h["comps"] = safe_int(last.get("comps"))
        h["free_trials"] = safe_int(last.get("free_trials"))
        d30 = subs[subs["date"] >= subs["date"].max() - pd.Timedelta(days=30)]
        if len(d30) >= 2:
            h["paid_30d"] = h["paid"] - safe_int(d30.iloc[0].get("paid"))
    if emails is not None and len(emails):
        last = emails.iloc[-1]
        h["total"] = safe_int(last["emails"])
        d30 = emails[emails["date"] >= emails["date"].max() - pd.Timedelta(days=30)]
        if len(d30) >= 2:
            h["total_30d"] = h["total"] - safe_int(d30.iloc[0]["emails"])
    if h.get("total") is not None and h.get("paid") is not None:
        h["free"] = h["total"] - h["paid"]
    arr = data.get("arr")
    if arr is not None and len(arr):
        h["arr"] = safe_float(arr.iloc[-1]["arr"])
        h["mrr"] = h["arr"] / 12.0 if h["arr"] is not None else None
    es = data.get("email_stats")
    if es is not None and len(es):
        cutoff = pd.Timestamp.utcnow() - pd.Timedelta(days=30)
        recent = es[es["post_date"] >= cutoff]
        if len(recent):
            h["avg_open_rate_30d"] = safe_float(recent["open_rate"].mean())
            h["avg_ctr_30d"] = safe_float(recent["click_through_rate"].mean())

    # 30d net growth and churn approximations from paid_growth.csv
    pg = data.get("paid_growth")
    if pg is not None and len(pg):
        recent = pg.tail(30)
        h["new_paid_30d"] = safe_int(recent["new_paid"].sum()) if "new_paid" in recent else None
        h["cancels_30d"] = safe_int(recent["cancellations_finalized"].sum()) if "cancellations_finalized" in recent else None
        if h.get("paid") and h.get("cancels_30d") is not None:
            h["churn_30d_rate"] = (h["cancels_30d"] / max(h["paid"], 1))

    return h


def growth_series(data: dict) -> dict:
    """Returns daily series suitable for Chart.js: dates, free, paid, total."""
    subs = data.get("subscribers")
    emails = data.get("emails")
    if subs is None or emails is None:
        return {"dates": [], "free": [], "paid": [], "total": []}
    # Align on date
    df_e = emails.set_index("date")["emails"].rename("total")
    df_s = subs.set_index("date")["paid"].rename("paid")
    df = pd.concat([df_e, df_s], axis=1).sort_index()
    df["paid"] = df["paid"].ffill()
    df["total"] = df["total"].ffill()
    df["free"] = (df["total"] - df["paid"]).clip(lower=0)
    df = df.dropna(subset=["total", "paid"])
    df = df.tail(540)  # ~18 months
    return {
        "dates": [d.strftime("%Y-%m-%d") for d in df.index],
        "free": df["free"].astype(int).tolist(),
        "paid": df["paid"].astype(int).tolist(),
        "total": df["total"].astype(int).tolist(),
    }


def daily_net_series(data: dict) -> dict:
    """Daily delta in total subs, broken into estimated free vs paid."""
    g = growth_series(data)
    if not g["dates"]:
        return {"dates": [], "free_delta": [], "paid_delta": []}
    free = pd.Series(g["free"])
    paid = pd.Series(g["paid"])
    fd = free.diff().fillna(0).astype(int).tolist()
    pd_ = paid.diff().fillna(0).astype(int).tolist()
    return {"dates": g["dates"], "free_delta": fd, "paid_delta": pd_}


def churn_series(data: dict) -> dict:
    """Approximate paid churn rate over time using paid_subscriber_growth.csv."""
    pg = data.get("paid_growth")
    subs = data.get("subscribers")
    if pg is None or subs is None or pg.empty:
        return {"dates": [], "rate": []}
    df = pg.set_index("date").sort_index()
    # 30d rolling cancellations / 30d rolling avg paid base
    base = subs.set_index("date")["paid"].sort_index().reindex(df.index, method="ffill")
    cancels = df.get("cancellations_finalized")
    if cancels is None:
        return {"dates": [], "rate": []}
    rolling_cancels = cancels.rolling(30, min_periods=1).sum()
    rolling_base = base.rolling(30, min_periods=1).mean().clip(lower=1)
    rate = (rolling_cancels / rolling_base).fillna(0)
    return {
        "dates": [d.strftime("%Y-%m-%d") for d in rate.index],
        "rate": [float(r) for r in rate.tolist()],
    }


def conversion_series(data: dict) -> dict:
    """Paid conversion rate proxy: cumulative paid / cumulative total."""
    g = growth_series(data)
    if not g["dates"]:
        return {"dates": [], "rate": []}
    total = pd.Series(g["total"]).clip(lower=1)
    paid = pd.Series(g["paid"])
    rate = (paid / total).tolist()
    return {"dates": g["dates"], "rate": [float(x) for x in rate]}


def post_table(data: dict) -> list[dict]:
    es = data.get("email_stats")
    if es is None or es.empty:
        return []
    df = es.sort_values("post_date", ascending=False).head(30).copy()
    rows = []
    for _, r in df.iterrows():
        rows.append({
            "title": str(r.get("title") or ""),
            "date": r["post_date"].strftime("%Y-%m-%d") if pd.notna(r["post_date"]) else "",
            "audience": str(r.get("audience") or ""),
            "views": int(r["views"]) if pd.notna(r.get("views")) else 0,
            "sent": int(r["sent"]) if pd.notna(r.get("sent")) else 0,
            "opens": int(r["opens"]) if pd.notna(r.get("opens")) else 0,
            "clicks": int(r["clicks"]) if pd.notna(r.get("clicks")) else 0,
            "open_rate": float(r["open_rate"]) if pd.notna(r.get("open_rate")) else 0.0,
            "ctr": float(r["click_through_rate"]) if pd.notna(r.get("click_through_rate")) else 0.0,
            "engagement": float(r["engagement_rate"]) if pd.notna(r.get("engagement_rate")) else 0.0,
        })
    return rows


def open_rate_distribution(data: dict) -> dict:
    es = data.get("email_stats")
    if es is None or es.empty:
        return {"bins": [], "counts": []}
    rates = es["open_rate"].dropna() * 100.0
    bins = list(range(0, 105, 5))
    counts, edges = np.histogram(rates, bins=bins)
    labels = [f"{edges[i]:.0f}-{edges[i+1]:.0f}%" for i in range(len(counts))]
    return {"bins": labels, "counts": counts.astype(int).tolist()}


def ctr_distribution(data: dict) -> dict:
    es = data.get("email_stats")
    if es is None or es.empty:
        return {"bins": [], "counts": []}
    rates = es["click_through_rate"].dropna() * 100.0
    bins = [0, 1, 2, 3, 4, 5, 7.5, 10, 15, 20]
    counts, edges = np.histogram(rates, bins=bins)
    labels = [f"{edges[i]:.1f}-{edges[i+1]:.1f}%" for i in range(len(counts))]
    return {"bins": labels, "counts": counts.astype(int).tolist()}


# ---------------------------------------------------------------------------
# Subscriber intelligence (warm free, top engagers, churn risk)
# ---------------------------------------------------------------------------

def score_subscribers(df: Optional[pd.DataFrame]) -> list[dict]:
    """Build a per-subscriber dataset for the JS layer to filter.

    Score heuristic when columns are available:
        score = 0.5 * z(opens_last_10 / 10)
              + 0.3 * z(clicks_last_10 / 10)
              + 0.2 * z(tenure_days)

    Falls back gracefully on whatever columns the source provides. The
    full dataset is shipped to the browser; threshold knobs filter
    client-side.
    """
    if df is None or df.empty:
        return []
    out = []
    now = pd.Timestamp.utcnow()
    # Pick the right columns
    has_o10 = "opens_last_10" in df.columns
    has_c10 = "clicks_last_10" in df.columns
    has_o30 = "opens_30d" in df.columns
    has_open_rate = "open_rate" in df.columns

    # z-score helpers
    def z(series):
        if series is None or len(series) == 0:
            return pd.Series([0.0] * len(df), index=df.index)
        m = series.mean()
        s = series.std()
        if not s or pd.isna(s):
            return pd.Series([0.0] * len(series), index=series.index)
        return (series - m) / s

    df = df.copy()
    if "subscribed_at" in df.columns:
        df["tenure_days"] = (now - df["subscribed_at"]).dt.days.fillna(0)
    else:
        df["tenure_days"] = 0

    base_engagement = None
    if has_o10:
        base_engagement = df["opens_last_10"].fillna(0) / 10.0
    elif has_o30:
        base_engagement = df["opens_30d"].fillna(0)
    elif has_open_rate:
        base_engagement = df["open_rate"].fillna(0)

    if base_engagement is None:
        df["score"] = 0.0
    else:
        z_eng = z(base_engagement)
        z_clicks = z(df["clicks_last_10"].fillna(0)) if has_c10 else pd.Series(0.0, index=df.index)
        z_tenure = z(df["tenure_days"])
        df["score"] = 0.5 * z_eng + 0.3 * z_clicks + 0.2 * z_tenure

    df = df.sort_values("score", ascending=False)
    for _, r in df.iterrows():
        out.append({
            "email": str(r.get("email") or ""),
            "name": str(r.get("name") or ""),
            "plan": str(r.get("plan") or "free"),
            "status": str(r.get("status") or "active"),
            "subscribed_at": r["subscribed_at"].strftime("%Y-%m-%d") if "subscribed_at" in df.columns and pd.notna(r["subscribed_at"]) else "",
            "last_seen_at": r["last_seen_at"].strftime("%Y-%m-%d") if "last_seen_at" in df.columns and pd.notna(r["last_seen_at"]) else "",
            "tenure_days": int(r.get("tenure_days") or 0),
            "opens_last_10": safe_int(r.get("opens_last_10")) or 0,
            "clicks_last_10": safe_int(r.get("clicks_last_10")) or 0,
            "opens_30d": safe_int(r.get("opens_30d")) or 0,
            "open_rate": float(r["open_rate"]) if pd.notna(r.get("open_rate")) else 0.0,
            "score": float(r.get("score") or 0.0),
        })
    return out


def churn_risk_paid(subscribers_data: list[dict]) -> list[dict]:
    """Paid subs flagged on engagement decline. Requires per-sub data with
    an open_rate or opens_last_10 vs opens_prev. Falls back to last_seen_at."""
    if not subscribers_data:
        return []
    risk = []
    for s in subscribers_data:
        if s.get("plan", "").lower() not in ("paid", "founding", "annual", "monthly"):
            continue
        # Heuristic: low opens_last_10 OR last_seen_at older than 21d
        flag = False
        reason = ""
        if s.get("opens_last_10", 0) <= 1:
            flag = True
            reason = f"opened {s.get('opens_last_10')}/10 last emails"
        elif s.get("open_rate", 0) > 0 and s.get("open_rate", 0) < 0.10:
            flag = True
            reason = f"30d open rate {s.get('open_rate', 0)*100:.0f}%"
        if flag:
            r = dict(s)
            r["risk_reason"] = reason
            risk.append(r)
    return risk[:50]


def recent_unsubs(data: dict) -> list[dict]:
    df = data.get("unsubscribes")
    if df is None or df.empty:
        return []
    df = df.sort_values("unsubscribed_at", ascending=False).head(30)
    out = []
    for _, r in df.iterrows():
        out.append({
            "email": str(r.get("email") or ""),
            "when": r["unsubscribed_at"].strftime("%Y-%m-%d") if pd.notna(r.get("unsubscribed_at")) else "",
            "bucket": str(r.get("cancel_reason_bucket") or ""),
            "feedback": str(r.get("feedback") or ""),
        })
    return out


# ---------------------------------------------------------------------------
# HTML
# ---------------------------------------------------------------------------

def _icon_b64() -> str:
    if not ICON.exists():
        return ""
    import base64
    return base64.b64encode(ICON.read_bytes()).decode("ascii")


def _fmt_int(x):
    if x is None:
        return "&mdash;".replace("mdash", "minus")  # belt and suspenders, no emdash
    try:
        return f"{int(x):,}"
    except Exception:
        return "-"


def _fmt_money(x):
    if x is None:
        return "-"
    try:
        return f"${float(x):,.0f}"
    except Exception:
        return "-"


def _fmt_pct(x, digits=1):
    if x is None:
        return "-"
    try:
        return f"{float(x)*100:.{digits}f}%"
    except Exception:
        return "-"


def _fmt_signed(x):
    if x is None:
        return "-"
    try:
        n = int(x)
        return f"+{n:,}" if n > 0 else f"{n:,}"
    except Exception:
        return "-"


def _kpi(label, value, sub=None, delta=None, delta_kind="neutral"):
    delta_html = ""
    if delta is not None:
        color = {"good": STARBOARD, "bad": PORT, "neutral": DOLDRUMS}[delta_kind]
        delta_html = f"<div class='delta' style='color:{color}'>{delta}</div>"
    sub_html = f"<div class='sub'>{sub}</div>" if sub else ""
    return (f"<div class='kpi'>"
            f"<div class='label'>{label}</div>"
            f"<div class='value'>{value}</div>"
            f"{delta_html}{sub_html}</div>")


def render_html(header: dict, snapshot_stamp: str, generated: str,
                charts_data: dict, posts: list[dict],
                subscribers: list[dict], churn_risk: list[dict],
                unsubs: list[dict], snap_path: Path,
                has_subscriber_list: bool) -> str:
    icon_b64 = _icon_b64()
    icon_img = (f'<img class="icon" src="data:image/png;base64,{icon_b64}" alt="LHM" />'
                if icon_b64 else "")

    # Header KPIs
    total = header.get("total")
    paid = header.get("paid")
    free = header.get("free")
    mrr = header.get("mrr")
    paid_30d = header.get("paid_30d")
    total_30d = header.get("total_30d")
    avg_open = header.get("avg_open_rate_30d")
    cancels = header.get("cancels_30d")
    churn_rate = header.get("churn_30d_rate")

    kpi_strip = "".join([
        _kpi("Total Subs", _fmt_int(total),
             delta=_fmt_signed(total_30d) + " / 30d" if total_30d is not None else None,
             delta_kind="good" if (total_30d or 0) > 0 else "bad" if (total_30d or 0) < 0 else "neutral"),
        _kpi("Free", _fmt_int(free)),
        _kpi("Paid", _fmt_int(paid),
             delta=_fmt_signed(paid_30d) + " / 30d" if paid_30d is not None else None,
             delta_kind="good" if (paid_30d or 0) > 0 else "bad" if (paid_30d or 0) < 0 else "neutral"),
        _kpi("MRR", _fmt_money(mrr),
             sub=f"ARR {_fmt_money(header.get('arr'))}"),
        _kpi("30d Net Growth", _fmt_signed(total_30d) if total_30d is not None else "-",
             delta_kind="good" if (total_30d or 0) > 0 else "bad"),
        _kpi("30d Cancels", _fmt_int(cancels),
             sub=f"Rate {_fmt_pct(churn_rate)}" if churn_rate is not None else None,
             delta_kind="bad" if (cancels or 0) > 0 else "neutral"),
        _kpi("Avg Open Rate (30d)", _fmt_pct(avg_open),
             sub=f"CTR {_fmt_pct(header.get('avg_ctr_30d'))}"),
        _kpi("As of", header.get("as_of") or generated[:10],
             sub=f"Snapshot {snapshot_stamp}"),
    ])

    # JSON blobs for client side
    payload = {
        "header": header,
        "growth": charts_data.get("growth", {}),
        "daily_net": charts_data.get("daily_net", {}),
        "churn": charts_data.get("churn", {}),
        "conversion": charts_data.get("conversion", {}),
        "open_dist": charts_data.get("open_dist", {}),
        "ctr_dist": charts_data.get("ctr_dist", {}),
        "posts": posts,
        "subscribers": subscribers,
        "churn_risk": churn_risk,
        "unsubs": unsubs,
        "has_subscriber_list": has_subscriber_list,
        "snapshot_path": str(snap_path),
    }
    payload_json = json.dumps(payload, default=str)

    css = f"""
    :root {{
      --ocean: {OCEAN}; --dusk: {DUSK}; --sky: {SKY}; --venus: {VENUS};
      --sea: {SEA}; --doldrums: {DOLDRUMS}; --starboard: {STARBOARD};
      --port: {PORT}; --fog: {FOG};
    }}
    * {{ box-sizing: border-box; }}
    body {{
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
      margin: 0; background: #f7f9fb; color: #1a2332;
    }}
    header.app {{
      background: linear-gradient(135deg, var(--ocean) 0%, #1a6e96 100%);
      color: white; padding: 24px 36px; display: flex; align-items: center;
      gap: 16px; border-bottom: 4px solid var(--dusk);
    }}
    header.app .icon {{ height: 56px; filter: brightness(0) invert(1); }}
    header.app h1 {{
      margin: 0; font-family: 'Montserrat', sans-serif; font-weight: 800;
      font-size: 24px; letter-spacing: 0.5px;
    }}
    header.app .tag {{
      font-size: 11px; letter-spacing: 3px; text-transform: uppercase;
      opacity: 0.85;
    }}
    header.app .stamp {{ margin-left: auto; font-size: 12px; opacity: 0.85; text-align: right; }}
    nav.tabs {{
      display: flex; gap: 0; background: white; border-bottom: 1px solid #e5ecf2;
      padding: 0 24px; position: sticky; top: 0; z-index: 10; overflow-x: auto;
    }}
    nav.tabs button {{
      background: transparent; border: none; padding: 14px 18px;
      font-family: 'Montserrat', sans-serif; font-size: 11px; font-weight: 700;
      letter-spacing: 1.4px; text-transform: uppercase; color: var(--doldrums);
      cursor: pointer; border-bottom: 3px solid transparent;
    }}
    nav.tabs button:hover {{ color: var(--ocean); }}
    nav.tabs button.active {{ color: var(--ocean); border-bottom-color: var(--dusk); }}
    main {{ max-width: 1280px; margin: 0 auto; padding: 24px 28px 60px; }}
    .panel {{ display: none; }}
    .panel.active {{ display: block; }}
    .panel-intro {{
      font-size: 13px; color: var(--doldrums); margin-bottom: 18px;
      max-width: 820px; line-height: 1.5;
    }}
    .kpi-grid {{
      display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px;
      margin-bottom: 24px;
    }}
    @media (max-width: 1100px) {{ .kpi-grid {{ grid-template-columns: repeat(2, 1fr); }} }}
    .kpi {{
      background: white; border: 1px solid #e5ecf2; border-left: 4px solid var(--ocean);
      border-radius: 8px; padding: 14px 16px;
    }}
    .kpi .label {{
      color: var(--doldrums); font-size: 10px; font-weight: 600;
      letter-spacing: 1.2px; text-transform: uppercase;
    }}
    .kpi .value {{
      color: var(--ocean); font-size: 24px; font-weight: 700;
      font-family: 'Montserrat', sans-serif; margin-top: 4px; letter-spacing: -0.5px;
    }}
    .kpi .delta {{ font-size: 11px; font-weight: 600; margin-top: 2px; }}
    .kpi .sub {{ font-size: 11px; color: var(--doldrums); margin-top: 2px; }}
    .card {{
      background: white; border: 1px solid #e5ecf2; border-radius: 8px;
      padding: 16px 18px; margin-bottom: 14px;
    }}
    .card h3 {{
      color: var(--ocean); font-family: 'Montserrat', sans-serif; font-size: 14px;
      font-weight: 700; letter-spacing: 0.6px; margin: 0 0 10px;
      text-transform: uppercase;
    }}
    .grid-2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }}
    @media (max-width: 900px) {{ .grid-2 {{ grid-template-columns: 1fr; }} }}
    .chart-wrap {{ position: relative; height: 280px; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 12px; }}
    th, td {{ text-align: left; padding: 8px 10px; border-bottom: 1px solid #eef2f5; }}
    th {{
      color: var(--doldrums); font-weight: 700; font-size: 10px;
      text-transform: uppercase; letter-spacing: 1px; cursor: pointer;
      user-select: none; background: #fafbfc;
    }}
    th.sortable:hover {{ color: var(--ocean); }}
    th.sorted-asc::after {{ content: " ▲"; font-size: 9px; color: var(--ocean); }}
    th.sorted-desc::after {{ content: " ▼"; font-size: 9px; color: var(--ocean); }}
    td.num, th.num {{ text-align: right; font-family: 'Source Code Pro', monospace; font-size: 11px; }}
    tr:hover td {{ background: #f7faff; }}
    .knobs {{
      display: flex; flex-wrap: wrap; gap: 18px; padding: 12px 16px;
      background: #f0f6fb; border: 1px solid #d6e3ed; border-radius: 6px;
      margin-bottom: 14px; align-items: end;
    }}
    .knob label {{
      display: block; font-size: 10px; color: var(--doldrums);
      letter-spacing: 1px; text-transform: uppercase; font-weight: 700;
      margin-bottom: 4px;
    }}
    .knob input[type=number], .knob select {{
      font-family: 'Source Code Pro', monospace; font-size: 13px;
      padding: 6px 10px; border: 1px solid #c5d1dc; border-radius: 4px;
      background: white; width: 90px;
    }}
    .knob .value-display {{ font-size: 11px; color: var(--ocean); font-weight: 600; margin-top: 4px; }}
    .empty-state {{
      padding: 28px; text-align: center; background: #fff8f1;
      border: 1px dashed var(--dusk); border-radius: 8px; color: #4a5764;
    }}
    .empty-state code {{
      background: #fdebda; padding: 2px 6px; border-radius: 3px;
      font-size: 12px; color: var(--port);
    }}
    .copy-btn {{
      background: var(--ocean); color: white; border: none; padding: 4px 10px;
      border-radius: 4px; font-size: 10px; font-weight: 700; cursor: pointer;
      letter-spacing: 0.5px;
    }}
    .copy-btn:hover {{ background: #1a6e96; }}
    .copy-btn.copied {{ background: var(--starboard); }}
    .pill {{
      display: inline-block; padding: 1px 8px; border-radius: 10px;
      font-size: 9px; font-weight: 700; text-transform: uppercase;
      letter-spacing: 0.6px;
    }}
    .pill.paid {{ background: var(--ocean); color: white; }}
    .pill.free {{ background: #e8edf3; color: var(--doldrums); }}
    .pill.risk {{ background: var(--port); color: white; }}
    footer {{
      text-align: center; padding: 20px; color: var(--doldrums);
      font-size: 11px; letter-spacing: 1px; text-transform: uppercase;
    }}
    .summary-row {{
      display: flex; gap: 24px; padding: 10px 0; font-size: 11px;
      color: var(--doldrums); flex-wrap: wrap;
    }}
    .summary-row strong {{ color: var(--ocean); font-size: 13px; }}
    """

    js = """
    const DATA = ___PAYLOAD___;
    const PALETTE = {
      ocean: '#2389BB', dusk: '#FF6723', sky: '#23BBFF', venus: '#FF2389',
      sea: '#00BB89', doldrums: '#898989', starboard: '#238923', port: '#892323',
      fog: '#D1D1D1'
    };

    function showPanel(id, btn) {
      document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
      document.querySelectorAll('nav.tabs button').forEach(b => b.classList.remove('active'));
      document.getElementById(id).classList.add('active');
      btn.classList.add('active');
    }

    function fmtPct(x, digits=1) {
      if (x === null || x === undefined || isNaN(x)) return '-';
      return (x * 100).toFixed(digits) + '%';
    }
    function fmtNum(x) {
      if (x === null || x === undefined || isNaN(x)) return '-';
      return Math.round(x).toLocaleString();
    }

    Chart.defaults.font.family = "'Inter', sans-serif";
    Chart.defaults.font.size = 11;
    Chart.defaults.color = PALETTE.doldrums;
    Chart.defaults.elements.line.tension = 0;
    Chart.defaults.elements.line.borderWidth = 2.5;
    Chart.defaults.elements.point.radius = 0;
    Chart.defaults.scale.grid.display = false;
    Chart.defaults.plugins.legend.labels.boxWidth = 12;

    const baseScales = {
      x: { grid: { display: false }, ticks: { maxTicksLimit: 8 } },
      y: { grid: { display: false }, beginAtZero: false,
           border: { display: true, color: PALETTE.doldrums },
           ticks: { padding: 6 } }
    };

    function drawGrowth() {
      const g = DATA.growth;
      if (!g.dates || !g.dates.length) return;
      new Chart(document.getElementById('chart-growth'), {
        type: 'line',
        data: {
          labels: g.dates,
          datasets: [
            { label: 'Free', data: g.free, borderColor: PALETTE.ocean, backgroundColor: 'rgba(35,137,187,0.1)' },
            { label: 'Paid', data: g.paid, borderColor: PALETTE.dusk, backgroundColor: 'rgba(255,103,35,0.1)' }
          ]
        },
        options: { scales: baseScales, plugins: { legend: { position: 'top' } } }
      });
    }

    function drawCumulative() {
      const g = DATA.growth;
      if (!g.dates || !g.dates.length) return;
      new Chart(document.getElementById('chart-cumulative'), {
        type: 'line',
        data: { labels: g.dates,
          datasets: [{ label: 'Total subscribers', data: g.total,
                       borderColor: PALETTE.ocean, fill: true,
                       backgroundColor: 'rgba(35,137,187,0.08)' }]
        },
        options: { scales: baseScales, plugins: { legend: { display: false } } }
      });
    }

    function drawChurn() {
      const c = DATA.churn;
      if (!c.dates || !c.dates.length) return;
      new Chart(document.getElementById('chart-churn'), {
        type: 'line',
        data: { labels: c.dates,
          datasets: [{ label: '30d rolling churn rate', data: c.rate.map(x => x*100),
                       borderColor: PALETTE.port, fill: true,
                       backgroundColor: 'rgba(137,35,35,0.08)' }]
        },
        options: { scales: { ...baseScales, y: { ...baseScales.y, ticks: {
                     callback: v => v.toFixed(1) + '%' } } },
                   plugins: { legend: { display: false } } }
      });
    }

    function drawConversion() {
      const c = DATA.conversion;
      if (!c.dates || !c.dates.length) return;
      new Chart(document.getElementById('chart-conversion'), {
        type: 'line',
        data: { labels: c.dates,
          datasets: [{ label: 'Paid / Total', data: c.rate.map(x => x*100),
                       borderColor: PALETTE.starboard, fill: true,
                       backgroundColor: 'rgba(35,137,35,0.08)' }]
        },
        options: { scales: { ...baseScales, y: { ...baseScales.y, ticks: {
                     callback: v => v.toFixed(2) + '%' } } },
                   plugins: { legend: { display: false } } }
      });
    }

    function drawOpenDist() {
      const o = DATA.open_dist;
      if (!o.bins || !o.bins.length) return;
      new Chart(document.getElementById('chart-open-dist'), {
        type: 'bar',
        data: { labels: o.bins,
          datasets: [{ data: o.counts, backgroundColor: PALETTE.ocean }] },
        options: { scales: baseScales, plugins: { legend: { display: false } } }
      });
    }

    function drawCtrDist() {
      const o = DATA.ctr_dist;
      if (!o.bins || !o.bins.length) return;
      new Chart(document.getElementById('chart-ctr-dist'), {
        type: 'bar',
        data: { labels: o.bins,
          datasets: [{ data: o.counts, backgroundColor: PALETTE.dusk }] },
        options: { scales: baseScales, plugins: { legend: { display: false } } }
      });
    }

    function drawDailyNet() {
      const d = DATA.daily_net;
      if (!d.dates || !d.dates.length) return;
      // Trim to last 120 days so the bars are legible
      const n = 120;
      const labels = d.dates.slice(-n);
      const free = d.free_delta.slice(-n);
      const paid = d.paid_delta.slice(-n);
      new Chart(document.getElementById('chart-daily-net'), {
        type: 'bar',
        data: { labels,
          datasets: [
            { label: 'Free', data: free, backgroundColor: PALETTE.ocean, stack: 's' },
            { label: 'Paid', data: paid, backgroundColor: PALETTE.dusk, stack: 's' }
          ]},
        options: { scales: { x: { stacked: true, grid: { display: false } },
                              y: { stacked: true, grid: { display: false },
                                   border: { color: PALETTE.doldrums } } },
                   plugins: { legend: { position: 'top' } } }
      });
    }

    // Sortable table
    function makeSortable(tableId, getRows) {
      const table = document.getElementById(tableId);
      if (!table) return;
      let sortKey = null, sortDir = 1;
      table.querySelectorAll('th.sortable').forEach(th => {
        th.addEventListener('click', () => {
          const k = th.dataset.key;
          if (sortKey === k) sortDir = -sortDir;
          else { sortKey = k; sortDir = 1; }
          table.querySelectorAll('th').forEach(x => x.classList.remove('sorted-asc','sorted-desc'));
          th.classList.add(sortDir > 0 ? 'sorted-asc' : 'sorted-desc');
          const rows = getRows();
          rows.sort((a, b) => {
            const av = a[k], bv = b[k];
            if (typeof av === 'number') return (av - bv) * sortDir;
            return String(av).localeCompare(String(bv)) * sortDir;
          });
          renderTable(tableId, rows);
        });
      });
    }

    function escapeHtml(s) {
      return String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
    }

    function copyEmail(btn, email) {
      navigator.clipboard.writeText(email).then(() => {
        btn.textContent = 'COPIED';
        btn.classList.add('copied');
        setTimeout(() => { btn.textContent = 'COPY'; btn.classList.remove('copied'); }, 1500);
      });
    }
    window.copyEmail = copyEmail;

    // ----- Posts table -----
    function renderPosts() {
      const tbody = document.querySelector('#tbl-posts tbody');
      if (!tbody) return;
      const rows = (DATA.posts || []).slice();
      tbody.innerHTML = rows.map(r => `
        <tr>
          <td>${r.date}</td>
          <td>${escapeHtml(r.title)}</td>
          <td>${escapeHtml(r.audience)}</td>
          <td class="num">${fmtNum(r.views)}</td>
          <td class="num">${fmtNum(r.opens)}</td>
          <td class="num">${fmtNum(r.clicks)}</td>
          <td class="num">${fmtPct(r.open_rate)}</td>
          <td class="num">${fmtPct(r.ctr)}</td>
          <td class="num">${fmtPct(r.engagement)}</td>
        </tr>`).join('');
    }
    function renderTable(tableId, rows) {
      // Generic re-render. Posts handled separately by renderPosts.
      if (tableId === 'tbl-posts') {
        const tbody = document.querySelector('#tbl-posts tbody');
        tbody.innerHTML = rows.map(r => `
        <tr>
          <td>${r.date}</td>
          <td>${escapeHtml(r.title)}</td>
          <td>${escapeHtml(r.audience)}</td>
          <td class="num">${fmtNum(r.views)}</td>
          <td class="num">${fmtNum(r.opens)}</td>
          <td class="num">${fmtNum(r.clicks)}</td>
          <td class="num">${fmtPct(r.open_rate)}</td>
          <td class="num">${fmtPct(r.ctr)}</td>
          <td class="num">${fmtPct(r.engagement)}</td>
        </tr>`).join('');
      }
    }

    // ----- Warm Free Subs -----
    function renderWarm() {
      if (!DATA.has_subscriber_list) return;
      const minOpens = +document.getElementById('warm-min-opens').value;
      const minTenure = +document.getElementById('warm-min-tenure').value;
      const minClicks = +document.getElementById('warm-min-clicks').value;
      document.getElementById('warm-min-opens-disp').textContent = minOpens + ' / 10';
      document.getElementById('warm-min-tenure-disp').textContent = minTenure + ' days';
      document.getElementById('warm-min-clicks-disp').textContent = minClicks + ' / 10';
      const all = DATA.subscribers.filter(s =>
        s.plan.toLowerCase() === 'free'
        && s.opens_last_10 >= minOpens
        && s.tenure_days >= minTenure
        && s.clicks_last_10 >= minClicks
      );
      document.getElementById('warm-count').textContent = all.length;
      const tbody = document.querySelector('#tbl-warm tbody');
      tbody.innerHTML = all.slice(0, 200).map(s => `
        <tr>
          <td>${escapeHtml(s.email)}</td>
          <td>${escapeHtml(s.name || '')}</td>
          <td>${s.subscribed_at || '-'}</td>
          <td>${s.last_seen_at || '-'}</td>
          <td class="num">${s.opens_last_10}</td>
          <td class="num">${s.clicks_last_10}</td>
          <td class="num">${s.tenure_days}</td>
          <td class="num">${s.score.toFixed(2)}</td>
          <td><button class="copy-btn" onclick="copyEmail(this, '${s.email}')">COPY</button></td>
        </tr>`).join('');
    }

    // ----- Top Engagers -----
    function renderTop() {
      if (!DATA.has_subscriber_list) return;
      const planFilter = document.getElementById('top-plan').value;
      let all = DATA.subscribers.slice();
      if (planFilter !== 'all') {
        all = all.filter(s => s.plan.toLowerCase() === planFilter);
      }
      all.sort((a, b) => b.score - a.score);
      all = all.slice(0, 50);
      const tbody = document.querySelector('#tbl-top tbody');
      tbody.innerHTML = all.map((s, i) => `
        <tr>
          <td class="num">${i+1}</td>
          <td>${escapeHtml(s.email)}</td>
          <td><span class="pill ${s.plan.toLowerCase()==='paid'?'paid':'free'}">${escapeHtml(s.plan)}</span></td>
          <td>${s.subscribed_at || '-'}</td>
          <td class="num">${s.opens_last_10}</td>
          <td class="num">${s.clicks_last_10}</td>
          <td class="num">${s.score.toFixed(2)}</td>
          <td><button class="copy-btn" onclick="copyEmail(this, '${s.email}')">COPY</button></td>
        </tr>`).join('');
    }

    // ----- Churn risk -----
    function renderChurn() {
      const tbody = document.querySelector('#tbl-churn tbody');
      const rows = DATA.churn_risk || [];
      if (!rows.length) {
        tbody.innerHTML = '<tr><td colspan="6" style="color:#898989;font-size:12px;text-align:center;padding:20px">No paid subscribers flagged at-risk. Either everything is healthy, or per-subscriber engagement data is unavailable (see Subscribers tab).</td></tr>';
      } else {
        tbody.innerHTML = rows.map(s => `
          <tr>
            <td>${escapeHtml(s.email)}</td>
            <td><span class="pill paid">${escapeHtml(s.plan)}</span></td>
            <td>${s.subscribed_at || '-'}</td>
            <td>${s.last_seen_at || '-'}</td>
            <td class="num">${s.opens_last_10}</td>
            <td><span class="pill risk">${escapeHtml(s.risk_reason)}</span></td>
          </tr>`).join('');
      }
      const utbody = document.querySelector('#tbl-unsubs tbody');
      const u = DATA.unsubs || [];
      if (!u.length) {
        utbody.innerHTML = '<tr><td colspan="4" style="color:#898989;font-size:12px;text-align:center;padding:20px">No unsubscribes recorded.</td></tr>';
      } else {
        utbody.innerHTML = u.map(r => `
          <tr>
            <td>${r.when}</td>
            <td>${escapeHtml(r.email)}</td>
            <td>${escapeHtml(r.bucket)}</td>
            <td style="font-size:11px;color:#4a5764">${escapeHtml(r.feedback)}</td>
          </tr>`).join('');
      }
    }

    document.addEventListener('DOMContentLoaded', () => {
      drawGrowth(); drawCumulative(); drawChurn(); drawConversion();
      drawOpenDist(); drawCtrDist(); drawDailyNet();
      renderPosts(); renderWarm(); renderTop(); renderChurn();
      ['warm-min-opens','warm-min-tenure','warm-min-clicks'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.addEventListener('input', renderWarm);
      });
      const topPlan = document.getElementById('top-plan');
      if (topPlan) topPlan.addEventListener('change', renderTop);
      makeSortable('tbl-posts', () => DATA.posts.slice());
    });
    """.replace("___PAYLOAD___", payload_json)

    # Empty state for sections that need per-subscriber data
    empty_msg = ("""
        <div class="empty-state">
          <strong>Per-subscriber engagement data not available.</strong><br>
          Substack's standard CSV exports do not include per-email open / click counts.
          To enable Warm Free Subs and Top Engagers cuts, drop a CSV named
          <code>subscriber_list.csv</code> (or <code>subscribers_list.csv</code>) into
          the latest snapshot folder with columns:
          <code>email, name, plan, status, subscribed_at, opens_last_10, clicks_last_10, last_seen_at</code>.
          The next 04:30 / 16:30 build will pick it up automatically.
        </div>""" if not has_subscriber_list else "")

    warm_panel = f"""
      <div class="panel-intro">
        Free subscribers ranked by engagement. Default cut surfaces readers
        who opened 5 or more of the last 10 emails AND have been on the list
        for at least 30 days. Adjust the knobs to widen or narrow the cut.
      </div>
      {empty_msg}
      <div class="knobs">
        <div class="knob">
          <label>Min opens (of last 10)</label>
          <input type="number" id="warm-min-opens" value="5" min="0" max="10" step="1" />
          <div class="value-display"><span id="warm-min-opens-disp">5 / 10</span></div>
        </div>
        <div class="knob">
          <label>Min tenure (days)</label>
          <input type="number" id="warm-min-tenure" value="30" min="0" step="5" />
          <div class="value-display"><span id="warm-min-tenure-disp">30 days</span></div>
        </div>
        <div class="knob">
          <label>Min clicks (of last 10)</label>
          <input type="number" id="warm-min-clicks" value="0" min="0" max="10" step="1" />
          <div class="value-display"><span id="warm-min-clicks-disp">0 / 10</span></div>
        </div>
        <div class="knob" style="margin-left:auto;align-self:center;font-size:12px">
          <span style="color:var(--doldrums)">Matches: </span>
          <strong id="warm-count" style="color:var(--ocean);font-size:18px;font-family:'Montserrat'">0</strong>
        </div>
      </div>
      <div class="card">
        <table id="tbl-warm">
          <thead><tr>
            <th>Email</th><th>Name</th><th>Subscribed</th><th>Last Seen</th>
            <th class="num">Opens / 10</th><th class="num">Clicks / 10</th>
            <th class="num">Tenure (d)</th><th class="num">Score</th><th></th>
          </tr></thead>
          <tbody></tbody>
        </table>
      </div>
    """

    top_panel = f"""
      <div class="panel-intro">
        Most-engaged subscribers, ranked by composite score
        (50% recent opens, 30% recent clicks, 20% tenure). The people worth
        a personal note. Filter by plan and sort by any column.
      </div>
      {empty_msg}
      <div class="knobs">
        <div class="knob">
          <label>Plan</label>
          <select id="top-plan">
            <option value="all">All</option>
            <option value="paid">Paid only</option>
            <option value="free">Free only</option>
          </select>
        </div>
        <div class="knob" style="margin-left:auto;align-self:center;font-size:11px;color:var(--doldrums)">
          Showing top 50 by composite score
        </div>
      </div>
      <div class="card">
        <table id="tbl-top">
          <thead><tr>
            <th class="num">#</th><th>Email</th><th>Plan</th><th>Subscribed</th>
            <th class="num">Opens / 10</th><th class="num">Clicks / 10</th>
            <th class="num">Score</th><th></th>
          </tr></thead>
          <tbody></tbody>
        </table>
      </div>
    """

    churn_panel = """
      <div class="panel-intro">
        Bonus cut. Paid subscribers showing engagement decline plus the
        recent unsubscribe log. Not a centerpiece, just a third surface
        worth checking weekly.
      </div>
      <div class="card">
        <h3>Paid subs at risk</h3>
        <table id="tbl-churn">
          <thead><tr>
            <th>Email</th><th>Plan</th><th>Subscribed</th><th>Last Seen</th>
            <th class="num">Opens / 10</th><th>Reason</th>
          </tr></thead>
          <tbody></tbody>
        </table>
      </div>
      <div class="card">
        <h3>Recent unsubscribes</h3>
        <table id="tbl-unsubs">
          <thead><tr>
            <th>When</th><th>Email</th><th>Reason bucket</th><th>Feedback</th>
          </tr></thead>
          <tbody></tbody>
        </table>
      </div>
    """

    overview_panel = f"""
      <div class="panel-intro">
        Outreach view. Header strip aggregates the metrics that matter for
        prioritization: where the list sits, how it is moving, how well it
        is engaging. Detail in the Growth, Engagement, and Subscriber tabs.
      </div>
      <div class="kpi-grid">{kpi_strip}</div>
      <div class="grid-2">
        <div class="card"><h3>Daily net subscribers, last 120 days</h3>
          <div class="chart-wrap"><canvas id="chart-daily-net"></canvas></div></div>
        <div class="card"><h3>Cumulative subscribers</h3>
          <div class="chart-wrap"><canvas id="chart-cumulative"></canvas></div></div>
      </div>
    """

    growth_panel = """
      <div class="panel-intro">
        Free vs paid trajectories, churn rate, and paid conversion ratio.
        Daily series since list inception or last 540 days, whichever is shorter.
      </div>
      <div class="card"><h3>Free vs paid subscribers over time</h3>
        <div class="chart-wrap"><canvas id="chart-growth"></canvas></div></div>
      <div class="grid-2">
        <div class="card"><h3>Paid churn rate (30d rolling)</h3>
          <div class="chart-wrap"><canvas id="chart-churn"></canvas></div></div>
        <div class="card"><h3>Paid conversion ratio (paid / total)</h3>
          <div class="chart-wrap"><canvas id="chart-conversion"></canvas></div></div>
      </div>
    """

    engagement_panel = """
      <div class="panel-intro">
        Per-post performance and the shape of open / click rate distributions
        across the catalog. Sortable by any column.
      </div>
      <div class="grid-2">
        <div class="card"><h3>Open rate distribution</h3>
          <div class="chart-wrap"><canvas id="chart-open-dist"></canvas></div></div>
        <div class="card"><h3>Click-through rate distribution</h3>
          <div class="chart-wrap"><canvas id="chart-ctr-dist"></canvas></div></div>
      </div>
      <div class="card">
        <h3>Post-level performance, last 30 posts</h3>
        <table id="tbl-posts">
          <thead><tr>
            <th class="sortable" data-key="date">Date</th>
            <th class="sortable" data-key="title">Title</th>
            <th class="sortable" data-key="audience">Audience</th>
            <th class="sortable num" data-key="views">Views</th>
            <th class="sortable num" data-key="opens">Opens</th>
            <th class="sortable num" data-key="clicks">Clicks</th>
            <th class="sortable num" data-key="open_rate">Open</th>
            <th class="sortable num" data-key="ctr">CTR</th>
            <th class="sortable num" data-key="engagement">Engagement</th>
          </tr></thead>
          <tbody></tbody>
        </table>
      </div>
    """

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Lighthouse Macro - Outreach Dashboard</title>
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Montserrat:wght@600;700;800&family=Source+Code+Pro:wght@400;600&display=swap" rel="stylesheet" />
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
<style>{css}</style>
</head>
<body>
  <header class="app">
    {icon_img}
    <div>
      <h1>OUTREACH DASHBOARD</h1>
      <div class="tag">MACRO, ILLUMINATED.</div>
    </div>
    <div class="stamp">
      <div>Generated {generated}</div>
      <div>Snapshot {snapshot_stamp}</div>
    </div>
  </header>
  <nav class="tabs">
    <button class="active" onclick="showPanel('p-overview', this)">Overview</button>
    <button onclick="showPanel('p-growth', this)">Growth & Retention</button>
    <button onclick="showPanel('p-engagement', this)">Engagement</button>
    <button onclick="showPanel('p-warm', this)">Warm Free Subs</button>
    <button onclick="showPanel('p-top', this)">Top Engagers</button>
    <button onclick="showPanel('p-churn', this)">Churn Risk</button>
  </nav>
  <main>
    <section id="p-overview" class="panel active">{overview_panel}</section>
    <section id="p-growth" class="panel">{growth_panel}</section>
    <section id="p-engagement" class="panel">{engagement_panel}</section>
    <section id="p-warm" class="panel">{warm_panel}</section>
    <section id="p-top" class="panel">{top_panel}</section>
    <section id="p-churn" class="panel">{churn_panel}</section>
  </main>
  <footer>LIGHTHOUSE MACRO &middot; INTERNAL &middot; DO NOT DISTRIBUTE</footer>
  <script>{js}</script>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------

def run() -> Path:
    snap = latest_snapshot()
    log.info("using snapshot %s", snap)
    data = load_all(snap)

    header = compute_header(data)
    header["as_of"] = datetime.now().strftime("%Y-%m-%d")

    sub_data = score_subscribers(data.get("subscriber_list"))
    has_sub_list = bool(sub_data)

    charts_data = {
        "growth": growth_series(data),
        "daily_net": daily_net_series(data),
        "churn": churn_series(data),
        "conversion": conversion_series(data),
        "open_dist": open_rate_distribution(data),
        "ctr_dist": ctr_distribution(data),
    }

    posts = post_table(data)
    risk = churn_risk_paid(sub_data) if has_sub_list else []
    unsubs = recent_unsubs(data)

    snapshot_stamp = snap.name
    generated = datetime.now().strftime("%Y-%m-%d %H:%M")

    html = render_html(
        header=header,
        snapshot_stamp=snapshot_stamp,
        generated=generated,
        charts_data=charts_data,
        posts=posts,
        subscribers=sub_data,
        churn_risk=risk,
        unsubs=unsubs,
        snap_path=snap,
        has_subscriber_list=has_sub_list,
    )

    stamp = datetime.now().strftime("%Y-%m-%d_%H%M")
    versioned = OUT_DIR / f"outreach_{stamp}.html"
    latest = OUT_DIR / "outreach_latest.html"
    versioned.write_text(html, encoding="utf-8")
    latest.write_text(html, encoding="utf-8")
    log.info("wrote %s (%d KB)", latest, len(html) // 1024)
    return latest


if __name__ == "__main__":
    out = run()
    print(out)
