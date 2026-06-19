"""Pharos configuration. Everything comes from the environment / Pharos/.env.
No secret is ever hard-coded here."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent      # .../Pharos/app
PHAROS_DIR = BASE_DIR.parent                     # .../Pharos


def _load_dotenv() -> None:
    """Minimal .env loader (no dependency). Existing env vars win."""
    envf = PHAROS_DIR / ".env"
    if not envf.exists():
        return
    for line in envf.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


_load_dotenv()

# --- signing / sessions ---
SECRET_KEY = os.environ.get("PHAROS_SECRET_KEY", "")
MAGIC_TTL = int(os.environ.get("PHAROS_MAGIC_TTL", "900"))                  # 15 min
SESSION_TTL = int(os.environ.get("PHAROS_SESSION_TTL", str(60 * 60 * 24 * 30)))  # 30 days
COOKIE_SECURE = os.environ.get("PHAROS_COOKIE_SECURE", "0") == "1"

# --- access verification ---
# Two Stripe accounts, joined by the subscriber's email (Stripe will not merge accounts):
#   PHAROS_STRIPE_API_KEY         -> account behind the Substack publication
#   PHAROS_STRIPE_API_KEY_DIRECT  -> main account for direct Pharos signups
# An active subscription in EITHER account (matched by email) grants access.
STRIPE_API_KEY = os.environ.get("PHAROS_STRIPE_API_KEY", "")               # restricted read-only (Substack account)
STRIPE_API_KEY_DIRECT = os.environ.get("PHAROS_STRIPE_API_KEY_DIRECT", "") # restricted read-only (direct/main account)
STRIPE_API_KEYS = [k for k in (STRIPE_API_KEY, STRIPE_API_KEY_DIRECT) if k]

# Where "Become a member" sends a non-subscriber. Set to the direct Pharos Stripe
# Payment Link once it exists; defaults to the Substack subscribe page meanwhile.
JOIN_URL = os.environ.get("PHAROS_JOIN_URL", "https://research.lighthousemacro.com/subscribe")

ALLOWLIST_PATH = BASE_DIR / "allowlist.txt"
PAID_SEED_PATH = BASE_DIR / "paid_seed.csv"

# --- data backend (the running OpenBB FastAPI service) ---
OPENBB_BACKEND = os.environ.get("PHAROS_OPENBB_BACKEND", "http://127.0.0.1:6900")

# --- urls / email ---
BASE_URL = os.environ.get("PHAROS_BASE_URL", "http://127.0.0.1:8800")
SMTP_HOST = os.environ.get("PHAROS_SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("PHAROS_SMTP_PORT", "465"))
SMTP_USER = os.environ.get("PHAROS_SMTP_USER", os.environ.get("GMAIL_FROM", ""))
SMTP_PASS = os.environ.get("PHAROS_SMTP_PASS", os.environ.get("GMAIL_APP_PASSWORD", ""))
MAIL_FROM = os.environ.get("PHAROS_MAIL_FROM", SMTP_USER or "research@lighthousemacro.com")

# --- modes ---
DEV_MODE = os.environ.get("PHAROS_DEV", "0") == "1"   # print magic links instead of emailing


def secret_ok() -> bool:
    return len(SECRET_KEY) >= 32
