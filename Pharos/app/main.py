"""Pharos terminal — FastAPI app.

Magic-link sign-in, gated by an active Substack subscription (Stripe) or the allowlist,
serving the Lighthouse Macro data backend behind the paywall.

Run (from the Pharos/ directory):
    uvicorn app.main:app --host 127.0.0.1 --port 8800 --reload
"""
from __future__ import annotations

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from . import auth, config, data, entitlements

app = FastAPI(title="Pharos", docs_url=None, redoc_url=None, openapi_url=None)
app.mount("/static", StaticFiles(directory=str(config.PHAROS_DIR / "static")), name="static")

WEB = config.PHAROS_DIR / "web"
SESSION_COOKIE = "pharos_session"

SUBSCRIBE_URL = config.JOIN_URL
_NOT_SUBSCRIBER_HTML = f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Pharos · Lighthouse Macro</title>
<style>body{{font-family:-apple-system,BlinkMacSystemFont,'Inter',sans-serif;background:#123456;color:#cdd9e3;
display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0;padding:2rem;text-align:center;}}
.card{{max-width:440px;}}h1{{font-family:'Montserrat',sans-serif;color:#fff;font-size:1.5rem;margin:0 0 0.8rem;}}
a.btn{{display:inline-block;margin-top:1.4rem;background:#FF6723;color:#fff;text-decoration:none;font-weight:700;
padding:0.9rem 1.6rem;border-radius:7px;}}a.alt{{display:block;margin-top:1rem;color:#89CCFF;}}</style></head>
<body><div class="card"><h1>We could not find an active subscription for that email.</h1>
<p>Pharos is included with any paid Lighthouse Macro subscription. Use the email on your subscription, or join below.</p>
<a class="btn" href="{SUBSCRIBE_URL}">Become a member &rarr;</a>
<a class="alt" href="/">Try a different email</a></div></body></html>"""


def _page(name: str) -> str:
    return (WEB / name).read_text(encoding="utf-8")


def _current_email(request: Request) -> str | None:
    return auth.verify_session(request.cookies.get(SESSION_COOKIE))


@app.on_event("startup")
def _check_config() -> None:
    if not config.secret_ok():
        raise RuntimeError(
            "PHAROS_SECRET_KEY is missing or too short. Put a 32+ char secret in Pharos/.env "
            '(generate one: python3 -c "import secrets; print(secrets.token_urlsafe(48))").'
        )


@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    if _current_email(request):
        return RedirectResponse("/terminal", status_code=302)
    return HTMLResponse(_page("login.html"))


@app.post("/auth/request", response_class=HTMLResponse)
def auth_request(email: str = Form(...)):
    """Instant entry: confirm the email is an active subscriber and let them straight in.

    No magic link, no inbox round-trip. We check the allowlist / live Stripe / paid-subscriber
    list, and if it is an active subscription we set the session and drop them in the terminal.
    """
    email = email.strip().lower()
    entitled, _reason = entitlements.check(email)
    if not entitled:
        return HTMLResponse(_NOT_SUBSCRIBER_HTML, status_code=403)
    resp = RedirectResponse("/terminal", status_code=303)
    resp.set_cookie(
        SESSION_COOKIE,
        auth.issue_session(email),
        max_age=config.SESSION_TTL,
        httponly=True,
        secure=config.COOKIE_SECURE,
        samesite="lax",
    )
    return resp


@app.get("/terminal", response_class=HTMLResponse)
def terminal(request: Request):
    if not _current_email(request):
        return RedirectResponse("/", status_code=302)
    return HTMLResponse(_page("terminal.html"))


@app.get("/api/dashboard")
def api_dashboard(request: Request):
    if not _current_email(request):
        return JSONResponse({"error": "unauthorized"}, status_code=401)
    return JSONResponse({"health": data.backend_health(), "composites": data.get_composites()})


@app.get("/auth/logout")
def logout():
    resp = RedirectResponse("/", status_code=302)
    resp.delete_cookie(SESSION_COOKIE)
    return resp


@app.get("/healthz")
def healthz():
    return {"status": "ok", "service": "pharos", "version": "0.1"}
