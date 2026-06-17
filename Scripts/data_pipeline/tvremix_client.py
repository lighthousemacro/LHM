"""
tvremix_client.py — LHM Bot's MCP client to the tvremix TradingView server.

This is the "tape" half of the fused brief. LHM Bot connects to tvremix.xyz/mcp
as an MCP client and pulls live cross-asset quotes, technicals, news, the
economic calendar, and (if connected) TV portfolio holdings. The proprietary
framework stays local; this just adds real market context so the brief stops
guessing the tape. No Claude session required — runs standalone on cron.

Config (Scripts/data_pipeline/.env):
  TVREMIX_MCP_URL        default https://tvremix.xyz/mcp
  TVREMIX_MCP_AUTH       bearer token / key for the bot's own connection.
                         ASK TVREMIX what it needs; drop it here. Empty = try anon.
  TVREMIX_MCP_TRANSPORT  'http' (streamable-http, default) or 'sse'

Tools are discovered at runtime and matched by name SUFFIX, so this works whether
the server exposes get_quotes_batch or tg_get_quotes_batch.

Symbols are TradingView EXCHANGE:TICKER — bare tickers do NOT resolve.
"""
from __future__ import annotations

import asyncio
import json
import os
from contextlib import asynccontextmanager

# Cross-asset universe, EXCHANGE:TICKER (validated live against tvremix).
CROSS_ASSET = [
    "AMEX:SPY", "NASDAQ:QQQ", "AMEX:IWM", "AMEX:RSP", "NASDAQ:TLT", "NASDAQ:SHY",
    "AMEX:HYG", "AMEX:LQD", "AMEX:GLD", "AMEX:USO", "AMEX:UUP", "AMEX:XLP",
    "AMEX:XLV", "AMEX:QAI", "TVC:DXY", "TVC:VIX", "COINBASE:BTCUSD",
]
# Thesis vehicles to pull technicals + news on (the book + the benchmark).
THESIS_VEHICLES = ["AMEX:XLP", "AMEX:GLD", "AMEX:SPY"]
NEWS_SYMBOLS = ["AMEX:SPY", "AMEX:XLP"]


def _cfg():
    return (
        os.environ.get("TVREMIX_MCP_URL", "https://tvremix.xyz/mcp"),
        os.environ.get("TVREMIX_MCP_AUTH", "").strip(),
        os.environ.get("TVREMIX_MCP_TRANSPORT", "http").strip().lower(),
    )


@asynccontextmanager
async def _session():
    from mcp import ClientSession
    url, auth, transport = _cfg()
    headers = {"Authorization": f"Bearer {auth}"} if auth else None
    if transport == "sse":
        from mcp.client.sse import sse_client
        async with sse_client(url, headers=headers) as (r, w):
            async with ClientSession(r, w) as s:
                await s.initialize()
                yield s
    else:
        from mcp.client.streamable_http import streamablehttp_client
        async with streamablehttp_client(url, headers=headers) as (r, w, _):
            async with ClientSession(r, w) as s:
                await s.initialize()
                yield s


async def _find(session, *suffixes) -> str | None:
    tools = (await session.list_tools()).tools
    names = [t.name for t in tools]
    for suf in suffixes:
        for n in names:
            if n.endswith(suf):
                return n
    return None


def _unwrap(result):
    """MCP call_tool result -> python object (parses the JSON text block)."""
    for block in getattr(result, "content", []) or []:
        if getattr(block, "type", None) == "text":
            try:
                return json.loads(block.text)
            except Exception:
                return {"text": block.text}
    sc = getattr(result, "structuredContent", None)
    return sc if sc is not None else None


async def _safe(session, tool, args, errors, label):
    if not tool:
        errors.append(f"{label}: tool not found on server")
        return None
    try:
        return _unwrap(await session.call_tool(tool, args))
    except Exception as e:  # noqa: BLE001
        errors.append(f"{label}: {e}")
        return None


async def _gather(symbols, thesis, news_syms, calendar_days):
    out = {"quotes": None, "calendar": None, "news": {}, "technicals": {},
           "portfolios": None, "errors": [], "tools": {}}
    async with _session() as s:
        t_quotes = await _find(s, "get_quotes_batch", "quotes_batch")
        t_cal = await _find(s, "get_economic_calendar", "economic_calendar")
        t_news = await _find(s, "get_news")
        t_tech = await _find(s, "get_technicals")
        t_wl = await _find(s, "get_portfolio_holdings", "my_portfolios",
                           "my_watchlist_symbols", "my_watchlists")
        out["tools"] = {"quotes": t_quotes, "calendar": t_cal, "news": t_news,
                        "technicals": t_tech, "portfolio": t_wl}

        out["quotes"] = await _safe(s, t_quotes, {"symbols": symbols},
                                    out["errors"], "quotes")
        # calendar: some servers reject extra kwargs; keep args minimal.
        from datetime import date, timedelta
        d0 = date.today().isoformat()
        d1 = (date.today() + timedelta(days=calendar_days)).isoformat()
        out["calendar"] = await _safe(s, t_cal,
                                      {"countries": ["US"], "date_from": d0, "date_to": d1},
                                      out["errors"], "calendar")
        for sym in news_syms:
            r = await _safe(s, t_news, {"symbol": sym, "limit": 5}, out["errors"], f"news:{sym}")
            if r is not None:
                out["news"][sym] = r
        for sym in thesis:
            d = {}
            for iv in ("1D", "1W"):
                r = await _safe(s, t_tech, {"symbol": sym, "interval": iv},
                                out["errors"], f"tech:{sym}:{iv}")
                if r is not None:
                    d[iv] = r
            if d:
                out["technicals"][sym] = d
        if t_wl:
            out["portfolios"] = await _safe(s, t_wl, {}, out["errors"], "portfolio")
    return out


def gather_tape(symbols=None, thesis=None, news_syms=None, calendar_days=2,
                timeout=60) -> dict:
    """Sync entry point. Returns a structured tape dict; on connection failure
    returns {'connected': False, 'error': ...} so the brief can degrade to
    framework-only instead of crashing the morning push."""
    symbols = symbols or CROSS_ASSET
    thesis = thesis or THESIS_VEHICLES
    news_syms = news_syms or NEWS_SYMBOLS

    async def _run():
        return await asyncio.wait_for(_gather(symbols, thesis, news_syms, calendar_days), timeout)

    try:
        data = asyncio.run(_run())
        data["connected"] = True
        return data
    except Exception as e:  # noqa: BLE001
        return {"connected": False, "error": str(e),
                "hint": "Set TVREMIX_MCP_AUTH (ask tvremix) and TVREMIX_MCP_URL in .env."}


if __name__ == "__main__":
    import pprint
    pprint.pprint(gather_tape())
