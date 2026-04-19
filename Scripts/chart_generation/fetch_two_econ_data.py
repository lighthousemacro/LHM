"""
Re-fetch source data for two_economies_charts.py
Targets: /tmp/two_econ_data/

Auto-fetches what's freely scriptable (Yahoo, Zillow, ADP CSV, NY Fed).
Cox is paywalled — falls back to hardcoded values from the original chart.
"""
import os
import sys
import io
import urllib.request
import pandas as pd

OUT = '/tmp/two_econ_data'
os.makedirs(OUT, exist_ok=True)

UA = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}


def fetch(url, dest, binary=False):
    print(f'  -> {os.path.basename(dest)}')
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        data = r.read()
    mode = 'wb' if binary else 'wb'
    with open(dest, mode) as f:
        f.write(data)
    print(f'     [{len(data):,} bytes]')


def fetch_yahoo(ticker, dest):
    """Monthly close from Yahoo via yfinance if available, else CSV chart endpoint."""
    try:
        import yfinance as yf
        df = yf.download(ticker, start='2021-12-01', interval='1mo', progress=False, auto_adjust=False)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df = df[['Close']].dropna()
        df.to_csv(dest)
        print(f'  -> {os.path.basename(dest)} via yfinance ({len(df)} rows)')
        return
    except Exception as e:
        print(f'  yfinance failed for {ticker}: {e}; trying CSV endpoint')
    # Fallback: Yahoo CSV chart endpoint
    import time
    p2 = int(time.time())
    url = f'https://query1.finance.yahoo.com/v7/finance/download/{ticker}?period1=1640995200&period2={p2}&interval=1mo&events=history'
    fetch(url, dest)


def fetch_zillow():
    """Zillow ZHVI tier CSVs (public)."""
    base = 'https://files.zillowstatic.com/research/public_csvs/zhvi'
    fetch(f'{base}/Metro_zhvi_uc_sfrcondo_tier_0.0_0.33_sm_sa_month.csv',
          f'{OUT}/zillow_bottom.csv')
    fetch(f'{base}/Metro_zhvi_uc_sfrcondo_tier_0.67_1.0_sm_sa_month.csv',
          f'{OUT}/zillow_top.csv')


def fetch_adp():
    """ADP National Employment Report — public XLSX from adpemploymentreport.com."""
    # Public NER history file
    candidates = [
        'https://adpemploymentreport.com/common/docs/ADP_NER_history.csv',
        'https://www.adpemploymentreport.com/common/docs/ADP_NER_history.csv',
    ]
    for url in candidates:
        try:
            fetch(url, f'{OUT}/ADP_NER_history.csv')
            return
        except Exception as e:
            print(f'    {url} -> {e}')
    raise RuntimeError('Could not fetch ADP NER history. Manual download required from adpemploymentreport.com (Historical Data link).')


def fetch_nyfed():
    """NY Fed Household Debt and Credit Report Q4 2025."""
    # The NY Fed posts their HHDC supplement XLSX
    candidates = [
        'https://www.newyorkfed.org/medialibrary/interactives/householdcredit/data/xls/HHD_C_Report_2025Q4.xlsx',
        'https://www.newyorkfed.org/medialibrary/interactives/householdcredit/data/xls/hhd_c_report_2025Q4.xlsx',
    ]
    for url in candidates:
        try:
            fetch(url, f'{OUT}/nyfed_q4_2025.xlsx', binary=True)
            return
        except Exception as e:
            print(f'    {url} -> {e}')
    raise RuntimeError('NY Fed HHDC URL changed. Visit https://www.newyorkfed.org/microeconomics/hhdc and download the Q4 2025 XLSX manually.')


def main():
    print('Fetching Yahoo monthly closes...')
    for ticker, dest in [
        ('DG', f'{OUT}/dg_yf.csv'),
        ('DLTR', f'{OUT}/dltr_yf.csv'),
        ('TPR', f'{OUT}/tpr_yf.csv'),
        ('LVMUY', f'{OUT}/lvmuy_yf.csv'),
    ]:
        try:
            fetch_yahoo(ticker, dest)
        except Exception as e:
            print(f'  FAIL {ticker}: {e}')

    print('\nFetching Zillow ZHVI tiers...')
    try:
        fetch_zillow()
    except Exception as e:
        print(f'  FAIL Zillow: {e}')

    print('\nFetching ADP NER history...')
    try:
        fetch_adp()
    except Exception as e:
        print(f'  FAIL ADP: {e}')

    print('\nFetching NY Fed HHDC Q4 2025...')
    try:
        fetch_nyfed()
    except Exception as e:
        print(f'  FAIL NY Fed: {e}')

    print('\nCox repossessions: paywalled, not fetched. Skipping fig5 (existing PNG remains).')

    print('\nFiles in', OUT)
    for f in sorted(os.listdir(OUT)):
        sz = os.path.getsize(f'{OUT}/{f}')
        print(f'  {f}  ({sz:,} bytes)')


if __name__ == '__main__':
    main()
