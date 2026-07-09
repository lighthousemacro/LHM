"""
LIGHTHOUSE MACRO - FREE CRYPTO DATA FETCHERS
=============================================
Replaces Token Terminal with free APIs:
- DefiLlama: TVL, fees, revenue (unlimited, free)
- CoinGecko: Price data (30 calls/min free)

No API keys required!
"""

import requests
import pandas as pd
import numpy as np
import sqlite3
import time
import logging
from datetime import datetime, timedelta
from typing import Tuple, List, Dict, Optional

logger = logging.getLogger(__name__)

# ==========================================
# CONFIGURATION
# ==========================================

# DefiLlama endpoints (no auth required)
DEFILLAMA_BASE = "https://api.llama.fi"
DEFILLAMA_COINS = "https://coins.llama.fi"
DEFILLAMA_STABLECOINS = "https://stablecoins.llama.fi"

# DefiLlama stablecoin asset IDs for the CLI/SLI aggregate (USDT=1, USDC=2).
# Full history per asset comes from /stablecoin/{id}; summed into
# STABLECOIN_TOTAL_MCAP each run (idempotent upsert keeps it current).
STABLECOIN_TOTAL_IDS = {1: 'USDT', 2: 'USDC'}

# CoinGecko endpoints (no auth for basic, 30/min limit)
COINGECKO_BASE = "https://api.coingecko.com/api/v3"

# Protocols to track (DefiLlama IDs)
DEFI_PROTOCOLS = {
    # Layer 1
    'ethereum': 'Ethereum',
    'solana': 'Solana',
    'avalanche': 'Avalanche',
    'near': 'NEAR',
    'sui': 'Sui',
    'aptos': 'Aptos',

    # Layer 2
    'arbitrum': 'Arbitrum',
    'optimism': 'Optimism',
    'base': 'Base',
    'polygon': 'Polygon',

    # DeFi - DEX
    'uniswap': 'Uniswap',
    'curve-dex': 'Curve',
    'pancakeswap': 'PancakeSwap',
    'raydium': 'Raydium',
    'aerodrome': 'Aerodrome',

    # DeFi - Lending
    'aave': 'Aave',
    'compound': 'Compound',
    'morpho': 'Morpho',
    'spark': 'Spark',

    # DeFi - Derivatives
    'gmx': 'GMX',
    'dydx': 'dYdX',
    'hyperliquid': 'Hyperliquid',
    'synthetix': 'Synthetix',

    # Liquid Staking
    'lido': 'Lido',
    'rocket-pool': 'Rocket Pool',
    'jito': 'Jito',
    'marinade-finance': 'Marinade',

    # Infrastructure
    'chainlink': 'Chainlink',
    'the-graph': 'The Graph',

    # Stablecoins
    'makerdao': 'MakerDAO',
}

# CoinGecko IDs for price data
COINGECKO_IDS = {
    'bitcoin': 'BTC',
    'ethereum': 'ETH',
    'solana': 'SOL',
    'avalanche-2': 'AVAX',
    'near': 'NEAR',
    'sui': 'SUI',
    'aptos': 'APT',
    'arbitrum': 'ARB',
    'optimism': 'OP',
    'matic-network': 'MATIC',
    'uniswap': 'UNI',
    'curve-dao-token': 'CRV',
    'aave': 'AAVE',
    'gmx': 'GMX',
    'lido-dao': 'LDO',
    'rocket-pool': 'RPL',
    'chainlink': 'LINK',
    'the-graph': 'GRT',
    'maker': 'MKR',
}


# ==========================================
# DEFILLAMA FETCHER
# ==========================================

class DefiLlamaFetcher:
    """Fetch DeFi data from DefiLlama (free, no auth)."""

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/json',
            'User-Agent': 'LighthouseMacro/1.0'
        })

    def fetch_all_tvl(self) -> Tuple[int, int]:
        """Fetch TVL for all tracked protocols."""
        c = self.conn.cursor()
        total_obs = 0
        protocols_updated = 0

        logger.info("Fetching TVL data from DefiLlama...")

        for protocol_id, name in DEFI_PROTOCOLS.items():
            try:
                url = f"{DEFILLAMA_BASE}/protocol/{protocol_id}"
                r = self.session.get(url, timeout=30)

                if r.status_code != 200:
                    logger.warning(f"   {name}: HTTP {r.status_code}")
                    continue

                data = r.json()

                # Get TVL history
                tvl_history = data.get('tvl', [])
                if not tvl_history:
                    tvl_history = data.get('chainTvls', {}).get('combined', {}).get('tvl', [])

                obs_count = 0
                for point in tvl_history:
                    if isinstance(point, dict):
                        ts = point.get('date')
                        value = point.get('totalLiquidityUSD')
                    elif isinstance(point, list) and len(point) >= 2:
                        ts, value = point[0], point[1]
                    else:
                        continue

                    if ts and value:
                        date_str = datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                        series_id = f"DEFI_{protocol_id.upper().replace('-', '_')}_TVL"
                        c.execute(
                            "INSERT OR REPLACE INTO observations VALUES (?,?,?)",
                            (series_id, date_str, float(value))
                        )
                        obs_count += 1

                if obs_count > 0:
                    # Update metadata
                    c.execute("""INSERT OR REPLACE INTO series_meta
                                (series_id, title, source, category, frequency, units, last_updated, last_fetched)
                                VALUES (?,?,?,?,?,?,?,?)""",
                             (f"DEFI_{protocol_id.upper().replace('-', '_')}_TVL",
                              f"{name} TVL", "DefiLlama", "Crypto_TVL", "Daily", "USD",
                              datetime.now().isoformat(), datetime.now().isoformat()))

                    protocols_updated += 1
                    total_obs += obs_count
                    logger.info(f"   {name}: {obs_count:,} observations")

                time.sleep(0.2)  # Rate limiting

            except Exception as e:
                logger.error(f"   {name}: Error - {e}")
                continue

        self.conn.commit()
        return protocols_updated, total_obs

    def fetch_all_fees(self) -> Tuple[int, int]:
        """Fetch fees/revenue for all protocols."""
        c = self.conn.cursor()
        total_obs = 0
        protocols_updated = 0

        logger.info("Fetching fees/revenue from DefiLlama...")

        try:
            # Get overview of all protocol fees
            url = f"{DEFILLAMA_BASE}/overview/fees"
            r = self.session.get(url, timeout=30)

            if r.status_code != 200:
                logger.error(f"Fees API error: {r.status_code}")
                return 0, 0

            data = r.json()
            protocols = data.get('protocols', [])

            for protocol in protocols:
                name = protocol.get('name', '')
                protocol_id = protocol.get('defillamaId') or protocol.get('slug', '').lower()

                # Check if it's in our watchlist
                if protocol_id not in DEFI_PROTOCOLS:
                    continue

                # Get daily fees/revenue
                daily_fees = protocol.get('total24h')
                daily_revenue = protocol.get('totalRevenue24h') or protocol.get('revenue24h')

                date_str = datetime.now().strftime('%Y-%m-%d')

                if daily_fees:
                    series_id = f"DEFI_{protocol_id.upper().replace('-', '_')}_FEES"
                    c.execute(
                        "INSERT OR REPLACE INTO observations VALUES (?,?,?)",
                        (series_id, date_str, float(daily_fees))
                    )
                    c.execute("""INSERT OR REPLACE INTO series_meta
                                (series_id, title, source, category, frequency, units, last_updated, last_fetched)
                                VALUES (?,?,?,?,?,?,?,?)""",
                             (series_id, f"{name} Daily Fees", "DefiLlama", "Crypto_Fees",
                              "Daily", "USD", datetime.now().isoformat(), datetime.now().isoformat()))
                    total_obs += 1

                if daily_revenue:
                    series_id = f"DEFI_{protocol_id.upper().replace('-', '_')}_REVENUE"
                    c.execute(
                        "INSERT OR REPLACE INTO observations VALUES (?,?,?)",
                        (series_id, date_str, float(daily_revenue))
                    )
                    c.execute("""INSERT OR REPLACE INTO series_meta
                                (series_id, title, source, category, frequency, units, last_updated, last_fetched)
                                VALUES (?,?,?,?,?,?,?,?)""",
                             (series_id, f"{name} Daily Revenue", "DefiLlama", "Crypto_Revenue",
                              "Daily", "USD", datetime.now().isoformat(), datetime.now().isoformat()))
                    total_obs += 1

                protocols_updated += 1

            self.conn.commit()
            logger.info(f"   Fees/revenue: {protocols_updated} protocols, {total_obs} observations")

        except Exception as e:
            logger.error(f"Fees fetch error: {e}")

        return protocols_updated, total_obs

    def fetch_chain_tvl(self) -> Tuple[int, int]:
        """Fetch aggregate TVL by chain."""
        c = self.conn.cursor()
        total_obs = 0
        chains_updated = 0

        logger.info("Fetching chain TVL from DefiLlama...")

        try:
            url = f"{DEFILLAMA_BASE}/v2/chains"
            r = self.session.get(url, timeout=30)

            if r.status_code != 200:
                return 0, 0

            chains = r.json()
            date_str = datetime.now().strftime('%Y-%m-%d')

            for chain in chains:
                name = chain.get('name', '')
                tvl = chain.get('tvl')

                if name and tvl:
                    series_id = f"CHAIN_{name.upper().replace(' ', '_')}_TVL"
                    c.execute(
                        "INSERT OR REPLACE INTO observations VALUES (?,?,?)",
                        (series_id, date_str, float(tvl))
                    )
                    c.execute("""INSERT OR REPLACE INTO series_meta
                                (series_id, title, source, category, frequency, units, last_updated, last_fetched)
                                VALUES (?,?,?,?,?,?,?,?)""",
                             (series_id, f"{name} Chain TVL", "DefiLlama", "Crypto_Chain_TVL",
                              "Daily", "USD", datetime.now().isoformat(), datetime.now().isoformat()))
                    total_obs += 1
                    chains_updated += 1

            self.conn.commit()
            logger.info(f"   Chain TVL: {chains_updated} chains")

        except Exception as e:
            logger.error(f"Chain TVL error: {e}")

        return chains_updated, total_obs

    def fetch_stablecoin_tvl(self) -> Tuple[int, int]:
        """Fetch stablecoin market cap data."""
        c = self.conn.cursor()
        total_obs = 0

        logger.info("Fetching stablecoin data from DefiLlama...")

        try:
            url = f"{DEFILLAMA_BASE}/stablecoins"
            r = self.session.get(url, timeout=30)

            if r.status_code != 200:
                return 0, 0

            data = r.json()
            stables = data.get('peggedAssets', [])
            date_str = datetime.now().strftime('%Y-%m-%d')

            # Top stablecoins
            top_stables = ['USDT', 'USDC', 'DAI', 'FRAX', 'TUSD', 'BUSD']

            for stable in stables:
                symbol = stable.get('symbol', '')
                if symbol not in top_stables:
                    continue

                circulating = stable.get('circulating', {}).get('peggedUSD')
                if circulating:
                    series_id = f"STABLE_{symbol}_MCAP"
                    c.execute(
                        "INSERT OR REPLACE INTO observations VALUES (?,?,?)",
                        (series_id, date_str, float(circulating))
                    )
                    c.execute("""INSERT OR REPLACE INTO series_meta
                                (series_id, title, source, category, frequency, units, last_updated, last_fetched)
                                VALUES (?,?,?,?,?,?,?,?)""",
                             (series_id, f"{symbol} Market Cap", "DefiLlama", "Crypto_Stablecoins",
                              "Daily", "USD", datetime.now().isoformat(), datetime.now().isoformat()))
                    total_obs += 1

            self.conn.commit()
            logger.info(f"   Stablecoins: {total_obs} series")

        except Exception as e:
            logger.error(f"Stablecoin error: {e}")

        return len(top_stables), total_obs

    def fetch_stablecoin_total_mcap(self) -> Tuple[int, int]:
        """
        Fetch FULL daily history of USDT+USDC total market cap and store as
        STABLECOIN_TOTAL_MCAP. This is the live feed for CLI (StableBTC_RoC
        component) and SLI. Unlike fetch_stablecoin_tvl (latest snapshot only),
        this pulls the complete per-asset history each run, so any gap
        self-heals on the next pipeline run.
        """
        c = self.conn.cursor()
        total = None

        logger.info("Fetching stablecoin total mcap history (USDT+USDC) from DefiLlama...")

        try:
            for sid, symbol in STABLECOIN_TOTAL_IDS.items():
                url = f"{DEFILLAMA_STABLECOINS}/stablecoin/{sid}"
                r = self.session.get(url, timeout=60)

                if r.status_code != 200:
                    logger.warning(f"   {symbol}: HTTP {r.status_code}")
                    continue

                data = r.json()
                rows = []
                for pt in data.get('tokens', []):
                    # Timestamps are 00:00 UTC daily — parse as UTC-naive so the
                    # calendar date is right (datetime.fromtimestamp would shift
                    # to local time and land on the previous day).
                    dt = pd.to_datetime(pt['date'], unit='s')
                    circ = pt.get('circulating', {})
                    mc = circ.get('peggedUSD', 0) if isinstance(circ, dict) else 0
                    if mc > 0:
                        rows.append({'date': dt, 'mcap': mc})

                if not rows:
                    logger.warning(f"   {symbol}: no history returned")
                    continue

                s = pd.DataFrame(rows).set_index('date').sort_index()
                s = s[~s.index.duplicated(keep='last')]

                if total is None:
                    total = s.rename(columns={'mcap': 'stable_mcap'})
                else:
                    total['stable_mcap'] = total['stable_mcap'].add(
                        s['mcap'].reindex(total.index, method='ffill'), fill_value=0)

                time.sleep(0.2)  # Rate limiting

            if total is None or total.empty:
                logger.error("Stablecoin total mcap: no data from any asset")
                return 0, 0

            obs_count = 0
            for dt, row in total.iterrows():
                c.execute(
                    "INSERT OR REPLACE INTO observations VALUES (?,?,?)",
                    ("STABLECOIN_TOTAL_MCAP", dt.strftime('%Y-%m-%d'), float(row['stable_mcap']))
                )
                obs_count += 1

            c.execute("""INSERT OR REPLACE INTO series_meta
                        (series_id, title, source, category, frequency, units, last_updated, last_fetched)
                        VALUES (?,?,?,?,?,?,?,?)""",
                     ("STABLECOIN_TOTAL_MCAP",
                      "Stablecoin Total Market Cap (USDT+USDC)", "DefiLlama", "Crypto",
                      "Daily", "USD", datetime.now().isoformat(), datetime.now().isoformat()))

            self.conn.commit()
            logger.info(f"   Stablecoin total mcap: {obs_count:,} observations")
            return 1, obs_count

        except Exception as e:
            logger.error(f"Stablecoin total mcap error: {e}")
            return 0, 0


# ==========================================
# COINGECKO FETCHER
# ==========================================

class CoinGeckoFetcher:
    """Fetch crypto price data from CoinGecko (free tier: 30 calls/min)."""

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/json',
            'User-Agent': 'LighthouseMacro/1.0'
        })
        self.last_call = 0
        self.min_interval = 2.1  # ~30 calls/min = 2 sec between calls

    def _rate_limit(self):
        """Enforce rate limit."""
        elapsed = time.time() - self.last_call
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        self.last_call = time.time()

    def fetch_prices(self, days: int = 30) -> Tuple[int, int]:
        """Fetch historical prices for tracked tokens."""
        c = self.conn.cursor()
        total_obs = 0
        tokens_updated = 0

        logger.info(f"Fetching {days}d price history from CoinGecko...")

        for coin_id, symbol in COINGECKO_IDS.items():
            try:
                self._rate_limit()

                url = f"{COINGECKO_BASE}/coins/{coin_id}/market_chart"
                params = {
                    'vs_currency': 'usd',
                    'days': days,
                    'interval': 'daily'
                }

                r = self.session.get(url, params=params, timeout=30)

                if r.status_code == 429:
                    logger.warning("Rate limited, waiting 60s...")
                    time.sleep(60)
                    continue

                if r.status_code != 200:
                    logger.warning(f"   {symbol}: HTTP {r.status_code}")
                    continue

                data = r.json()
                prices = data.get('prices', [])
                market_caps = data.get('market_caps', [])
                volumes = data.get('total_volumes', [])

                obs_count = 0

                # Store price
                for ts, price in prices:
                    date_str = datetime.fromtimestamp(ts/1000).strftime('%Y-%m-%d')
                    series_id = f"CRYPTO_{symbol}_PRICE"
                    c.execute(
                        "INSERT OR REPLACE INTO observations VALUES (?,?,?)",
                        (series_id, date_str, float(price))
                    )
                    obs_count += 1

                # Store market cap
                for ts, mcap in market_caps:
                    date_str = datetime.fromtimestamp(ts/1000).strftime('%Y-%m-%d')
                    series_id = f"CRYPTO_{symbol}_MCAP"
                    c.execute(
                        "INSERT OR REPLACE INTO observations VALUES (?,?,?)",
                        (series_id, date_str, float(mcap))
                    )
                    obs_count += 1

                # Store volume
                for ts, vol in volumes:
                    date_str = datetime.fromtimestamp(ts/1000).strftime('%Y-%m-%d')
                    series_id = f"CRYPTO_{symbol}_VOLUME"
                    c.execute(
                        "INSERT OR REPLACE INTO observations VALUES (?,?,?)",
                        (series_id, date_str, float(vol))
                    )
                    obs_count += 1

                # Update metadata
                for suffix, title_suffix, units in [
                    ('PRICE', 'Price', 'USD'),
                    ('MCAP', 'Market Cap', 'USD'),
                    ('VOLUME', 'Volume', 'USD')
                ]:
                    series_id = f"CRYPTO_{symbol}_{suffix}"
                    c.execute("""INSERT OR REPLACE INTO series_meta
                                (series_id, title, source, category, frequency, units, last_updated, last_fetched)
                                VALUES (?,?,?,?,?,?,?,?)""",
                             (series_id, f"{symbol} {title_suffix}", "CoinGecko", "Crypto_Prices",
                              "Daily", units, datetime.now().isoformat(), datetime.now().isoformat()))

                tokens_updated += 1
                total_obs += obs_count
                logger.info(f"   {symbol}: {obs_count:,} observations")

            except Exception as e:
                logger.error(f"   {symbol}: Error - {e}")
                continue

        self.conn.commit()
        return tokens_updated, total_obs

    def fetch_global_metrics(self) -> Tuple[int, int]:
        """Fetch global crypto market metrics."""
        c = self.conn.cursor()
        total_obs = 0

        logger.info("Fetching global crypto metrics...")

        try:
            self._rate_limit()

            url = f"{COINGECKO_BASE}/global"
            r = self.session.get(url, timeout=30)

            if r.status_code != 200:
                return 0, 0

            data = r.json().get('data', {})
            date_str = datetime.now().strftime('%Y-%m-%d')

            metrics = {
                'CRYPTO_TOTAL_MCAP': data.get('total_market_cap', {}).get('usd'),
                'CRYPTO_TOTAL_VOLUME': data.get('total_volume', {}).get('usd'),
                'CRYPTO_BTC_DOMINANCE': data.get('market_cap_percentage', {}).get('btc'),
                'CRYPTO_ETH_DOMINANCE': data.get('market_cap_percentage', {}).get('eth'),
                'CRYPTO_DEFI_MCAP': data.get('defi_market_cap'),
                'CRYPTO_ACTIVE_COINS': data.get('active_cryptocurrencies'),
            }

            for series_id, value in metrics.items():
                if value is not None:
                    c.execute(
                        "INSERT OR REPLACE INTO observations VALUES (?,?,?)",
                        (series_id, date_str, float(value))
                    )
                    c.execute("""INSERT OR REPLACE INTO series_meta
                                (series_id, title, source, category, frequency, units, last_updated, last_fetched)
                                VALUES (?,?,?,?,?,?,?,?)""",
                             (series_id, series_id.replace('_', ' ').title(), "CoinGecko",
                              "Crypto_Global", "Daily", "USD" if 'MCAP' in series_id or 'VOLUME' in series_id else "Percent",
                              datetime.now().isoformat(), datetime.now().isoformat()))
                    total_obs += 1

            self.conn.commit()
            logger.info(f"   Global metrics: {total_obs} series")

        except Exception as e:
            logger.error(f"Global metrics error: {e}")

        return 1, total_obs


# ==========================================
# UNIFIED CRYPTO FETCHER
# ==========================================

class FreeCryptoFetcher:
    """
    Unified fetcher combining DefiLlama + CoinGecko.
    Replaces TokenTerminal with free alternatives.
    """

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        self.defillama = DefiLlamaFetcher(conn)
        self.coingecko = CoinGeckoFetcher(conn)

    def fetch_all(self, price_days: int = 30) -> Tuple[int, int]:
        """Fetch all crypto data from free sources."""
        total_series = 0
        total_obs = 0

        logger.info("\n--- FREE CRYPTO DATA (DefiLlama + CoinGecko) ---")

        # DefiLlama: TVL
        series, obs = self.defillama.fetch_all_tvl()
        total_series += series
        total_obs += obs

        # DefiLlama: Fees/Revenue
        series, obs = self.defillama.fetch_all_fees()
        total_series += series
        total_obs += obs

        # DefiLlama: Chain TVL
        series, obs = self.defillama.fetch_chain_tvl()
        total_series += series
        total_obs += obs

        # DefiLlama: Stablecoins
        series, obs = self.defillama.fetch_stablecoin_tvl()
        total_series += series
        total_obs += obs

        # DefiLlama: Stablecoin total mcap full history (CLI/SLI feed)
        series, obs = self.defillama.fetch_stablecoin_total_mcap()
        total_series += series
        total_obs += obs

        # CoinGecko: Prices
        series, obs = self.coingecko.fetch_prices(days=price_days)
        total_series += series * 3  # price, mcap, volume per token
        total_obs += obs

        # CoinGecko: Global metrics
        series, obs = self.coingecko.fetch_global_metrics()
        total_series += series
        total_obs += obs

        logger.info(f"\nCrypto total: {total_series} series, {total_obs:,} observations")

        return total_series, total_obs


# ==========================================
# MAIN
# ==========================================

if __name__ == "__main__":
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )

    db_path = "/Users/bob/LHM/Data/databases/Lighthouse_Master.db"
    conn = sqlite3.connect(db_path)

    fetcher = FreeCryptoFetcher(conn)
    series, obs = fetcher.fetch_all(price_days=30)

    print(f"\nComplete: {series} series, {obs:,} observations")
    conn.close()
