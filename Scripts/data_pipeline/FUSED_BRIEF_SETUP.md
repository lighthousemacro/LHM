# Fused Brief — activation

The LHM bot's `fused` command produces the daily brief by fusing the **real
framework** (MRI / risk / allocation / 12 pillars, local) with the **real tape**
(quotes / technicals / news / calendar / TV positions, via the tvremix MCP),
synthesized by an LLM in Bob's voice. One Telegram surface, no fake regime labels.

```
Scripts/.venv/bin/python Scripts/data_pipeline/lhmbot_push.py fused          # send
Scripts/.venv/bin/python Scripts/data_pipeline/lhmbot_push.py fused --dry-run # print
```

Run it under **`Scripts/.venv`** — that venv has the `mcp` client. It falls back
to the framework-only brief if anything below is missing, so it never fails the push.

## What you provide (in `Scripts/data_pipeline/.env`)

```
# 1. LLM synthesis (required for the fused prose)
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-sonnet-4-6     # optional; claude-opus-4-8 for max quality

# 2. tvremix MCP — ask the tvremix bot what its server needs, then fill in
TVREMIX_MCP_URL=https://tvremix.xyz/mcp
TVREMIX_MCP_AUTH=...                   # bearer token / key for the bot's own connection
TVREMIX_MCP_TRANSPORT=http             # 'http' (streamable-http) or 'sse'
```

Until `TVREMIX_MCP_AUTH` + the correct URL/transport are set, the tape comes back
offline and the brief says so. Until `ANTHROPIC_API_KEY` is set, it falls back to
the old framework-only morning.

## Files

- `tvremix_client.py` — MCP client. Discovers tools by name **suffix** (works with
  `get_quotes_batch` or `tg_get_quotes_batch`). Cross-asset universe is in
  `CROSS_ASSET` (EXCHANGE:TICKER — bare tickers do not resolve). Sync `gather_tape()`.
- `fused_brief.py` — framework + tape -> LLM -> brief. `gather_framework()` reuses
  the bot's authoritative morning read as ground truth. `SYSTEM` holds the voice +
  fusion rules (framework numbers never overridden). `generate()` returns
  `(brief_text, statuses)`.
- `lhmbot_push.py` — `cmd_fused` (the `fused` subcommand), with fallback.

## Switch the morning schedule

Point the existing morning launchd/cron job at `fused` instead of `morning`, and
use the venv python:

```
Scripts/.venv/bin/python Scripts/data_pipeline/lhmbot_push.py fused
```

## Asks for the tvremix bot (it gave you the architecture)

1. Auth: does `tvremix.xyz/mcp` need a bearer token / API key for a non-claude.ai
   MCP client, and what header? (Maybe the existing `TRADINGVIEW_API_KEY` works.)
2. Transport: streamable-http or SSE?
3. The tool names it exposes (we match by suffix, but confirm `quotes_batch`,
   `economic_calendar`, `news`, `technicals`, `portfolio holdings` exist) and the
   economic-calendar argument shape (the claude.ai copy rejects an `importance` kwarg).
