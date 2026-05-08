"""
LHM Universe Scan
=================

Run the full LHM systematic screen across:
  - Russell 3000 stocks (from iShares IWV holdings)
  - Cross-asset ETF universe (~500 tickers)

For each ticker compute:
  - Z-RoC tactical (21d ROC, robust z over 252d, 5d EMA smooth)
  - Z-RoC regime (63d ROC, robust z over 252d, 5d EMA smooth)
  - Distance-from-MA z-scores (21d, 50d, 200d MAs, expanding-window z)
  - Relative strength regime vs RUA (price ratio × 100, 63d/252d SMA, regime label)

Rank by an LHM score that prefers:
  - RS GREEN regime
  - Both Z-RoCs constructive (>= 0)
  - Not overstretched (no d-z > +2)
  - Not broken (no Z-RoC < -1.0, price > 200d MA)

Save:
  - /Users/bob/LHM/Outputs/scan/lhm_universe_scan_full.csv (every ticker)
  - /Users/bob/LHM/Outputs/scan/lhm_universe_scan_top.csv (top 100)
"""
import os
import sys
import time
import urllib.request
from io import StringIO

import numpy as np
import pandas as pd
import yfinance as yf

OUT_DIR = '/Users/bob/LHM/Outputs/scan'
os.makedirs(OUT_DIR, exist_ok=True)

BENCH = '^RUA'
HISTORY_PERIOD = '5y'  # 5y is enough for Z-RoC (252d) and rough d-z; full max would be cleaner but slower
CHUNK = 200


# ============================================================
# UNIVERSE BUILDERS
# ============================================================

def fetch_iwv_holdings():
    """Pull Russell 3000 holdings from iShares IWV daily CSV."""
    url = ('https://www.ishares.com/us/products/239714/'
           'ishares-russell-3000-etf/1467271812596.ajax?'
           'fileType=csv&fileName=IWV_holdings&dataType=fund')
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=30) as resp:
            text = resp.read().decode('utf-8', errors='replace')
        # iShares CSV has header rows before the actual table — find the data start
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if line.startswith('Ticker,Name'):
                csv_text = '\n'.join(lines[i:])
                break
        else:
            raise ValueError('IWV CSV format unexpected')
        df = pd.read_csv(StringIO(csv_text))
        df = df[df['Asset Class'].fillna('').str.strip() == 'Equity']
        tickers = df['Ticker'].dropna().astype(str).str.strip().tolist()
        # Clean: drop tickers with dots, dashes, or weird chars (keep simple ones for yfinance)
        tickers = [t for t in tickers if t and t.replace('.', '').isalnum()]
        # yfinance uses '-' for class shares; iShares uses '.' (e.g., BRK.B)
        tickers = [t.replace('.', '-') for t in tickers]
        return tickers
    except Exception as e:
        print(f'IWV fetch failed: {e}')
        return None


def cross_asset_etf_universe():
    """A pragmatic ~500-ETF cross-asset universe. Hand-curated for breadth."""
    return [
        # Broad equity
        'SPY','VOO','IVV','QQQ','QQQM','DIA','IWM','IWV','RSP','EWZ','VTI','VEA','VWO','VT',
        # Sector SPDRs + Vanguard
        'XLE','XLU','XLP','XLY','XLK','XLI','XLV','XLF','XLB','XLRE','XLC',
        'VGT','VDE','VFH','VHT','VIS','VAW','VOX','VPU','VCR','VDC','VNQ',
        # Style/factor
        'MTUM','QUAL','USMV','VLUE','SIZE','SCHD','VYM','HDV','DVY','VIG','DGRO',
        'COWZ','MOAT','EWGS','PRF','SPLV','SPHB','SPLG','SPYV','SPYG',
        # Equal weight
        'RSP','EQAL','EWMC','EWSC',
        # Innovation/thematic
        'ARKK','ARKW','ARKG','ARKQ','ARKF','BOTZ','ROBO','SKYY','HACK','CIBR','ICLN',
        'TAN','LIT','URA','URNM','REMX','XME','GDX','GDXJ','SIL','SILJ','COPX',
        # International
        'EFA','VEA','EEM','VWO','EWJ','EWG','EWU','EWQ','EWP','EWI','EWZ','EWY',
        'EWT','EWH','EWS','EWA','EWC','INDA','MCHI','FXI','KWEB','CQQQ','ASHR',
        'EPI','EPHE','VNM','THD','FLBR','EWW','ILF','GREK','TUR','EZA',
        # Region/style intl
        'IEFA','IEMG','VEU','VXUS','ACWI','ACWX','SCHF','SCHE',
        # Small/mid cap
        'IWM','IWN','IWO','IJR','IJH','IJJ','IJS','IJT','VB','VBR','VBK','VTWO','VIOO',
        # Bonds — Treasuries
        'TLT','IEF','SHY','SHV','BIL','TBT','TMF','EDV','GOVT','SGOV','PLW','VGIT','VGSH','VGLT','VTIP','SCHO','SCHR',
        # Bonds — credit
        'LQD','IGLB','HYG','JNK','EMB','PCY','BKLN','SRLN','SHYG','HYS','VCSH','VCIT','VCLT','BSV','BIV','BLV','BND','AGG',
        # Bonds — TIPS / inflation
        'TIP','SCHP','VTIP','STIP','LTPZ',
        # Bonds — preferred / hybrid
        'PFF','PGX','PFFD','SPFF',
        # Currency
        'UUP','UDN','FXE','FXY','FXB','FXC','FXA','FXF','CYB','UUP','EUO','YCS',
        # Commodities — broad
        'DBC','GSG','PDBC','BCI','COMT','DJP','CCRV',
        # Commodities — gold/silver/PM
        'GLD','IAU','GLDM','SGOL','SLV','PSLV','PALL','PPLT',
        # Commodities — energy
        'USO','BNO','UCO','SCO','UNG','BOIL','KOLD','UGA','BNO',
        # Commodities — agri/livestock
        'WEAT','CORN','SOYB','CANE','COW','MOO',
        # Volatility
        'VIXY','VIXM','VXX','UVXY','SVXY','SVIX',
        # Crypto-related
        'IBIT','FBTC','BITO','BITX','BTCO','BRRR','HODL','GBTC','ETHA','ETHE','ETHV','ETHU','ETHD',
        'BLOK','BITQ','DAPP','LEGR','BITS','SATO','BTF','XBTF',
        # Real estate
        'VNQ','IYR','SCHH','REET','REZ','RWR','XLRE','SRET','MORT','REM',
        # Leveraged / inverse (sample)
        'TQQQ','SQQQ','SPXL','SPXS','UPRO','SPXU','SOXL','SOXS','TNA','TZA','LABU','LABD','FAS','FAZ','TMF','TMV',
        # Defense / aerospace / industry themes
        'ITA','XAR','PPA','ITB','XHB','XME','XOP','OIH','IYT','XTN','IBB','XBI','ARKG',
        # Clean energy
        'ICLN','TAN','PBW','FAN','LIT','URA','BATT',
        # Cyber / cloud / software
        'HACK','CIBR','BUG','WCLD','SKYY','IGV','VGT',
        # Semiconductors
        'SOXX','SMH','XSD','PSI','SOXL','SOXS','FTXL',
        # AI / robotics
        'BOTZ','ROBO','IRBO','THNQ','AIQ','CHAT','AIRR',
        # Healthcare segments
        'IBB','XBI','ARKG','IHI','IHF','IYC','PPH','PJP',
        # Mortgage / fixed-income special
        'CMBS','MBB','GNMA','REM','MORT',
        # Biotech / pharma
        'XBI','IBB','PJP','PPH','XPH','CURE','LABU','LABD',
        # Defense / sin / themes
        'KOMP','PSCT','ESPO','GAMR','BJK','PEJ','XRT','RTH','PMR','FXR',
        # Munis
        'MUB','TFI','VTEB','HYD','SUB','SHM',
        # Dividends/income
        'SDOG','DEF','DVY','VYM','HDV','DGRO','DLN','SPHD','REGL','VIG','PEY','RDIV','SDY',
        # Quality + low vol
        'QUAL','SPHQ','OEF','MGV','DEF','USMV','SPLV','XSLV','EFAV','EEMV',
        # Dividend growth, multifactor
        'DTD','DON','VYMI','HDLB','SCHV','RPV','RPG','RFV','RFG',
        # Closed-end / managed
        'KMLM','RYLD','QYLD','XYLD','JEPI','JEPQ','SVOL','BTAL','BIL','SGOV',
    ]


# ============================================================
# LHM COMPUTE
# ============================================================

def robust_z(s, lookback=252, smooth=5, cap=10.0):
    med = s.rolling(lookback).median()
    mad = (s - med).abs().rolling(lookback).median()
    z = ((s - med) / (1.4826 * mad)).replace([np.inf, -np.inf], np.nan).clip(-cap, cap)
    return z.ewm(span=smooth, adjust=False).mean()


def lhm_stack(close, bench):
    """Compute the LHM full stack for one ticker. Returns dict or None."""
    s = close.dropna()
    if len(s) < 600:
        return None
    last = float(s.iloc[-1])
    z21 = robust_z(s.pct_change(21) * 100).iloc[-1]
    z63 = robust_z(s.pct_change(63) * 100).iloc[-1]

    def _dz(ma_len):
        ma = s.rolling(ma_len).mean()
        d = (s / ma - 1) * 100
        m = d.expanding(min_periods=200).mean()
        sd = d.expanding(min_periods=200).std()
        z = ((d - m) / sd).iloc[-1]
        return z, d.iloc[-1]

    d21z, d21pct = _dz(21)
    d50z, d50pct = _dz(50)
    d200z, d200pct = _dz(200)

    rs = (s / bench).dropna()
    if len(rs) < 252:
        return None
    rs_last = rs.iloc[-1]
    sma63 = rs.rolling(63).mean().iloc[-1]
    sma252 = rs.rolling(252).mean().iloc[-1]
    if rs_last > sma63 and sma63 > sma252:
        regime = 'GREEN'
    elif rs_last < sma63 and sma63 < sma252:
        regime = 'RED'
    else:
        regime = 'mixed'

    score = 0
    if regime == 'GREEN': score += 3
    elif regime == 'mixed': score += 1
    if z21 > 0: score += 2
    elif z21 > -0.5: score += 1
    if z63 > 0: score += 2
    elif z63 > -0.5: score += 1
    if pd.notna(d200z) and d200z > 2: score -= 3
    elif pd.notna(d200z) and d200z > 1.5: score -= 1
    if pd.notna(d50z) and d50z > 2: score -= 1
    if z21 < -1.0: score -= 3
    if z63 < -1.0: score -= 3
    if last < s.tail(200).mean(): score -= 2

    return {
        'last': last, 'z21': float(z21), 'z63': float(z63),
        'd21z': float(d21z) if pd.notna(d21z) else np.nan,
        'd50z': float(d50z) if pd.notna(d50z) else np.nan,
        'd200z': float(d200z) if pd.notna(d200z) else np.nan,
        'd21pct': float(d21pct), 'd50pct': float(d50pct), 'd200pct': float(d200pct),
        'regime': regime, 'score': score,
    }


# ============================================================
# RUNNER
# ============================================================

def chunked_download(tickers, period=HISTORY_PERIOD, chunk_size=CHUNK):
    """Download in chunks to avoid yfinance overload."""
    all_data = {}
    n_chunks = (len(tickers) + chunk_size - 1) // chunk_size
    for i in range(n_chunks):
        batch = tickers[i*chunk_size:(i+1)*chunk_size]
        print(f'  chunk {i+1}/{n_chunks} ({len(batch)} tickers)...', flush=True)
        try:
            data = yf.download(batch, period=period, interval='1d',
                               auto_adjust=True, progress=False, threads=True)['Close']
            if isinstance(data, pd.Series):
                data = data.to_frame(batch[0])
            for t in data.columns:
                all_data[t] = data[t]
        except Exception as e:
            print(f'    chunk failed: {e}')
        time.sleep(0.5)
    return all_data


def main():
    print('Building universe...')
    stocks = fetch_iwv_holdings()
    if stocks is None:
        print('Falling back to S&P 500 + extensions')
        sp500 = pd.read_html(
            'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]
        stocks = sp500['Symbol'].tolist()
    etfs = cross_asset_etf_universe()
    etfs = list(dict.fromkeys(etfs))  # dedupe

    print(f'Stocks: {len(stocks)}, ETFs: {len(etfs)}, Total: {len(stocks)+len(etfs)}')

    # Pull benchmark first
    print('Pulling benchmark RUA...')
    bench = yf.download(BENCH, period=HISTORY_PERIOD, interval='1d',
                        auto_adjust=True, progress=False)['Close']
    if isinstance(bench, pd.DataFrame):
        bench = bench.iloc[:, 0]
    bench.index = pd.DatetimeIndex(bench.index).tz_localize(None)

    print('Pulling universe price history...')
    print('  Stocks...')
    stock_data = chunked_download(stocks)
    print('  ETFs...')
    etf_data = chunked_download(etfs)

    print(f'Got data for {len(stock_data)} stocks + {len(etf_data)} ETFs')

    rows = []
    for label, datadict in [('stock', stock_data), ('etf', etf_data)]:
        for t, s in datadict.items():
            if s.dropna().empty:
                continue
            try:
                s.index = pd.DatetimeIndex(s.index).tz_localize(None)
                aligned = s.reindex(bench.index, method='ffill')
                bench_aligned = bench.reindex(s.index, method='ffill')
                if len(aligned.dropna()) < 600:
                    continue
                result = lhm_stack(aligned, bench_aligned.reindex(aligned.index))
                if result is None:
                    continue
                result['ticker'] = t
                result['kind'] = label
                rows.append(result)
            except Exception:
                continue

    df = pd.DataFrame(rows)
    if df.empty:
        print('No results — universe scan failed')
        return

    df = df.sort_values('score', ascending=False)
    df.to_csv(f'{OUT_DIR}/lhm_universe_scan_full.csv', index=False)
    df.head(100).to_csv(f'{OUT_DIR}/lhm_universe_scan_top.csv', index=False)

    print(f'\nTotal scored: {len(df)}')
    print(f'GREEN regime: {(df.regime=="GREEN").sum()}')
    print(f'Score >= 7 (cleanest): {(df.score>=7).sum()}')
    print(f'Score >= 6: {(df.score>=6).sum()}')
    print(f'Saved -> {OUT_DIR}/lhm_universe_scan_full.csv')
    print(f'Top 100 -> {OUT_DIR}/lhm_universe_scan_top.csv')

    print('\n=== TOP 30 BY SCORE ===')
    cols = ['ticker','kind','score','regime','z21','z63','d50z','d200z','last']
    print(df[cols].head(30).to_string(index=False))


if __name__ == '__main__':
    main()
