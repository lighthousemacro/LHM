"""
PiTrade Client API wrapper for the Crosscurrents book.

Auth is a two-step JWT flow (documented at
https://support.pitrade.com/client-apis/native/authentication):

  1. Sign a JWT with {clientId, iat, exp} using the API key (HS256).
  2. POST it to /public/auth/token to receive IdToken + RefreshToken.
  3. Send `Authorization: Bearer <IdToken>` on every /client request.

Credentials come from the pipeline .env:

    PITRADE_CLIENT_ID=...
    PITRADE_API_KEY=...
    PITRADE_ROAR_API_KEY=...      # separate x-api-key credential
    PITRADE_ENV=prod              # or 'devo' for the sandbox

The portfolio and trade endpoint schemas are not published yet, so
`discover()` probes the documented and likely paths and reports which ones
answer. Once PiTrade publishes the spec, pin the winners in PORTFOLIO_PATHS.
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

import jwt

LHM_ROOT = Path("/Users/bob/LHM")
ENV_PATH = LHM_ROOT / "Scripts" / "data_pipeline" / ".env"

BASES = {
    "prod": ("https://api.pitrade.com/public", "https://api.pitrade.com/client"),
    "devo": ("https://devo.api.pitrade.com/public", "https://devo.api.pitrade.com/client"),
}
ROAR_BASE = "https://api.pitrade.com/external"

# Only /api/portfolios is confirmed (it appears in PiTrade's own auth example).
# The rest are probes for discover().
PORTFOLIO_PATHS = [
    "/api/portfolios",
    "/api/portfolio",
    "/api/portfolios/holdings",
    "/api/holdings",
    "/api/positions",
    "/api/transactions",
    "/api/orders",
]


def _load_env() -> None:
    """Load the pipeline .env without requiring python-dotenv."""
    if not ENV_PATH.exists():
        return
    for line in ENV_PATH.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        os.environ.setdefault(key.strip(), val.strip().strip("'\""))


class PiTradeError(RuntimeError):
    pass


class PiTradeClient:
    def __init__(
        self,
        client_id: str | None = None,
        api_key: str | None = None,
        env: str | None = None,
    ) -> None:
        _load_env()
        self.client_id = client_id or os.environ.get("PITRADE_CLIENT_ID", "")
        self.api_key = api_key or os.environ.get("PITRADE_API_KEY", "")
        self.env = env or os.environ.get("PITRADE_ENV", "prod")
        if self.env not in BASES:
            raise PiTradeError(f"PITRADE_ENV must be one of {list(BASES)}, got {self.env!r}")
        self.public_base, self.client_base = BASES[self.env]
        self._id_token: str | None = None
        self._refresh_token: str | None = None
        self._expires_at: float = 0.0

    # ---- plumbing -------------------------------------------------------

    @staticmethod
    def _request(
        url: str,
        method: str = "GET",
        headers: dict[str, str] | None = None,
        body: dict[str, Any] | None = None,
        timeout: int = 30,
    ) -> tuple[int, Any]:
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(url, data=data, method=method)
        req.add_header("Content-Type", "application/json")
        for k, v in (headers or {}).items():
            req.add_header(k, v)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                raw = resp.read().decode()
                try:
                    return resp.status, json.loads(raw)
                except json.JSONDecodeError:
                    return resp.status, raw
        except urllib.error.HTTPError as exc:
            raw = exc.read().decode(errors="replace")
            try:
                return exc.code, json.loads(raw)
            except json.JSONDecodeError:
                return exc.code, raw
        except urllib.error.URLError as exc:
            raise PiTradeError(f"network error calling {url}: {exc.reason}") from exc

    # ---- auth -----------------------------------------------------------

    def _signed_jwt(self) -> str:
        if not self.client_id or not self.api_key:
            raise PiTradeError(
                "PITRADE_CLIENT_ID and PITRADE_API_KEY are not set. "
                f"Add them to {ENV_PATH} (request them from PiTrade support)."
            )
        now = int(time.time())
        payload = {"clientId": self.client_id, "iat": now, "exp": now + 3600}
        return jwt.encode(payload, self.api_key, algorithm="HS256")

    def authenticate(self) -> str:
        status, data = self._request(
            f"{self.public_base}/auth/token",
            method="POST",
            body={"token": self._signed_jwt()},
        )
        if status != 200 or not isinstance(data, dict):
            raise PiTradeError(f"auth/token failed ({status}): {data}")
        self._id_token = data["IdToken"]
        self._refresh_token = data.get("RefreshToken")
        # Renew a minute early so a long call never straddles expiry.
        self._expires_at = time.time() + int(data.get("ExpiresIn", 3600)) - 60
        return self._id_token

    def _refresh(self) -> str:
        if not self._refresh_token:
            return self.authenticate()
        status, data = self._request(
            f"{self.public_base}/auth/refresh",
            method="POST",
            body={"refresh_token": self._refresh_token},
        )
        if status != 200 or not isinstance(data, dict):
            # Refresh tokens expire too. Fall back to a full handshake.
            return self.authenticate()
        self._id_token = data["IdToken"]
        self._expires_at = time.time() + int(data.get("ExpiresIn", 3600)) - 60
        return self._id_token

    def token(self) -> str:
        if not self._id_token:
            return self.authenticate()
        if time.time() >= self._expires_at:
            return self._refresh()
        return self._id_token

    # ---- client API -----------------------------------------------------

    def get(self, path: str, raise_on_error: bool = True) -> Any:
        status, data = self._request(
            f"{self.client_base}{path}",
            headers={"Authorization": f"Bearer {self.token()}"},
        )
        if status != 200 and raise_on_error:
            raise PiTradeError(f"GET {path} failed ({status}): {data}")
        return data if status == 200 else None

    def portfolios(self) -> Any:
        return self.get("/api/portfolios")

    def discover(self) -> dict[str, str]:
        """Probe candidate paths and report which ones respond.

        The portfolio and trade specs are not published yet, so this is how we
        find the real surface without guessing in production code.
        """
        found: dict[str, str] = {}
        for path in PORTFOLIO_PATHS:
            status, data = self._request(
                f"{self.client_base}{path}",
                headers={"Authorization": f"Bearer {self.token()}"},
            )
            preview = json.dumps(data)[:220] if not isinstance(data, str) else data[:220]
            found[path] = f"{status} {preview}"
        return found

    # ---- ROAR risk scores ----------------------------------------------

    @staticmethod
    def roar_snapshot(tickers: list[str] | None = None) -> dict[str, float]:
        """Current ROAR momentum-risk scores, 0-100, lower means lower risk.

        Uses the separate x-api-key credential, not the JWT flow.
        """
        _load_env()
        key = os.environ.get("PITRADE_ROAR_API_KEY", "")
        if not key:
            raise PiTradeError("PITRADE_ROAR_API_KEY is not set.")
        status, data = PiTradeClient._request(
            f"{ROAR_BASE}/roar/v1/snapshot/tickers",
            headers={"x-api-key": key},
        )
        if status != 200 or not isinstance(data, dict):
            raise PiTradeError(f"ROAR snapshot failed ({status}): {data}")
        if tickers:
            return {t: data[t] for t in tickers if t in data}
        return data

    @staticmethod
    def roar_history(ticker: str, start: str, end: str) -> list[dict[str, Any]]:
        """ROAR score history. Dates are YYYY-MM-DD, US/Eastern."""
        _load_env()
        key = os.environ.get("PITRADE_ROAR_API_KEY", "")
        if not key:
            raise PiTradeError("PITRADE_ROAR_API_KEY is not set.")
        status, data = PiTradeClient._request(
            f"{ROAR_BASE}/roar/v1/ticker/{ticker}/range/{start}/{end}?sort=asc",
            headers={"x-api-key": key},
        )
        if status != 200:
            raise PiTradeError(f"ROAR history for {ticker} failed ({status}): {data}")
        return data


if __name__ == "__main__":
    import sys

    client = PiTradeClient()
    if not client.client_id or not client.api_key:
        print("Credentials missing. Add to", ENV_PATH)
        print("  PITRADE_CLIENT_ID=...")
        print("  PITRADE_API_KEY=...")
        print("  PITRADE_ROAR_API_KEY=...")
        sys.exit(1)

    client.authenticate()
    print("Authenticated against", client.client_base)
    print()
    print("Endpoint probe:")
    for path, result in client.discover().items():
        print(f"  {path:32s} {result}")
