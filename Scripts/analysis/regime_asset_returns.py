#!/usr/bin/env python3
"""
Regime-conditioned cross-asset returns
======================================
Engine behind the LHM regime/asset-class exhibits. Three regime lenses,
one return panel.

Lenses
------
1. GROWTH x INFLATION quadrant  — Activity Pulse (GCI) vs Inflation Heat (PCI),
   both 21-day smoothed (daily composites smooth at 21d per house rule),
   split at zero. Four states: Goldilocks, Overheat, Stagflation, Contraction.
2. MRI band                     — the canonical five Macro Risk Index bands.
3. Recession-risk band          — Model B REC_PROB (12m), adopted 2026-07-25.

Returns
-------
All prices are yfinance auto_adjust closes stored in Lighthouse_Master.db,
i.e. total return (dividends reinvested). Cash leg is BIL where available.
Regimes are lagged one day before being matched to returns, so a given day's
return is attributed to the regime that was observable the prior close.

Author: Lighthouse Macro
Date: 2026-07-26
"""

from __future__ import annotations

import sqlite3

import numpy as np
import pandas as pd

DB_PATH = "/Users/bob/LHM/Data/databases/Lighthouse_Master.db"
TRADING_DAYS = 252

# ---------------------------------------------------------------- universes

MAJORS = {
    'US Equities':   'SPY',
    'US Treasuries': 'IEF',
    'US Credit':     'LQD',
    'Commodities':   'DBC',
    'Gold':          'GLD',
    'US Dollar':     'UUP',
}

MAJORS_PLUS = {**MAJORS, 'Bitcoin': 'BTC', 'REITs': 'VNQ'}

SECTORS = {
    'Technology': 'XLK', 'Financials': 'XLF', 'Health Care': 'XLV',
    'Cons. Disc.': 'XLY', 'Cons. Staples': 'XLP', 'Industrials': 'XLI',
    'Energy': 'XLE', 'Materials': 'XLB', 'Utilities': 'XLU',
    'Real Estate': 'XLRE', 'Comm. Services': 'XLC',
}

SUB_ASSETS = {
    # rates and credit
    'T-Bills (0-3m)':    'BIL',
    'Short Tsy (1-3y)':  'SHY',
    'Interm Tsy (7-10y)':'IEF',
    'Long Tsy (20y+)':   'TLT',
    'TIPS':              'TIP',
    'Agency MBS':        'MBB',
    'US Agg':            'AGG',
    'IG Credit':         'LQD',
    'High Yield':        'HYG',
    'EM Sovereign':      'EMB',
    # equity regions
    'US Large Cap':      'SPY',
    'US Small Cap':      'IWM',
    'Nasdaq 100':        'QQQ',
    'EAFE ex-US':        'EFA',
    'Europe':            'VGK',
    'Japan':             'EWJ',
    'EM Equity':         'EEM',
    'China':             'FXI',
    # style
    'Large Growth':      'IWF',
    'Large Value':       'IWD',
    'Equal Weight':      'RSP',
    # real assets
    'Broad Commodities': 'DBC',
    'Energy Commod.':    'DBE',
    'Agriculture':       'DBA',
    'Gold':              'GLD',
    'Silver':            'SLV',
    'Gold Miners':       'GDX',
    'Metals & Mining':   'XME',
    'REITs':             'VNQ',
    'Homebuilders':      'ITB',
    # fx / crypto
    'US Dollar':         'UUP',
    'Bitcoin':           'BTC',
}

FACTORS = {
    'Momentum': 'MTUM', 'Quality': 'QUAL', 'Min Vol': 'USMV',
    'Value': 'VLUE', 'Large Growth': 'IWF', 'Large Value': 'IWD',
    'Equal Weight': 'RSP', 'Small Cap': 'IWM',
}

QUADRANTS = ['Goldilocks', 'Overheat', 'Stagflation', 'Contraction']
QUAD_DESC = {
    'Goldilocks':  'Growth up, inflation down',
    'Overheat':    'Growth up, inflation up',
    'Stagflation': 'Growth down, inflation up',
    'Contraction': 'Growth down, inflation down',
}
MRI_BANDS = ['Low Risk', 'Neutral', 'Elevated', 'High Risk', 'Crisis']


# ------------------------------------------------------------------- loaders

def _conn():
    return sqlite3.connect(DB_PATH)


def load_prices(tickers=None) -> pd.DataFrame:
    """Daily total-return-adjusted closes, wide frame indexed by date."""
    with _conn() as c:
        df = pd.read_sql(
            "SELECT series_id, date, value FROM observations "
            "WHERE series_id LIKE '%\\_Close' ESCAPE '\\'",
            c, parse_dates=['date'])
    df['ticker'] = df.series_id.str.replace('_Close', '', regex=False)
    wide = df.pivot_table(index='date', columns='ticker', values='value')
    wide = wide.sort_index()
    if tickers is not None:
        keep = [t for t in tickers if t in wide.columns]
        wide = wide[keep]
    return wide


def load_index(index_id: str) -> pd.Series:
    with _conn() as c:
        d = pd.read_sql(
            "SELECT date, value FROM lighthouse_indices WHERE index_id=? ORDER BY date",
            c, params=(index_id,), parse_dates=['date'])
    return d.set_index('date').value


def growth_inflation_regime(smooth: int = 21) -> pd.DataFrame:
    """Daily growth/inflation quadrant from Activity Pulse and Inflation Heat."""
    gci = load_index('GCI').resample('D').ffill()
    pci = load_index('PCI').resample('D').ffill()
    g = gci.rolling(smooth, min_periods=smooth).mean()
    i = pci.rolling(smooth, min_periods=smooth).mean()
    df = pd.concat([g.rename('growth'), i.rename('inflation')], axis=1).dropna()
    up_g = df.growth > 0
    up_i = df.inflation > 0
    df['quadrant'] = np.select(
        [up_g & ~up_i, up_g & up_i, ~up_g & up_i, ~up_g & ~up_i],
        QUADRANTS, default=None)
    return df


def mri_regime(smooth: int = 21) -> pd.DataFrame:
    mri = load_index('MRI').resample('D').ffill().rolling(smooth, min_periods=smooth).mean()
    band = pd.cut(mri, [-np.inf, -0.5, 0.5, 1.0, 1.5, np.inf], labels=MRI_BANDS)
    return pd.DataFrame({'mri': mri, 'band': band}).dropna()


def recprob_regime() -> pd.DataFrame:
    p = load_index('REC_PROB').resample('D').ffill()
    band = pd.cut(p, [-np.inf, 0.10, 0.25, 0.40, np.inf],
                  labels=['<10%', '10-25%', '25-40%', '>40%'])
    return pd.DataFrame({'rec_prob': p, 'band': band}).dropna()


# ------------------------------------------------------------------- returns

def daily_returns(tickers: dict) -> pd.DataFrame:
    """Log-safe simple daily returns keyed by display name."""
    px = load_prices(list(tickers.values()))
    out = {}
    for name, tkr in tickers.items():
        if tkr not in px.columns:
            continue
        s = px[tkr].dropna()
        out[name] = s.pct_change()
    return pd.DataFrame(out)


def regime_stats(rets: pd.DataFrame, regime: pd.Series,
                 states=None, min_days: int = 60) -> dict:
    """Annualized return / vol / Sharpe / hit rate / max drawdown by regime state.

    `regime` is shifted one day so returns are attributed to the regime that was
    observable at the prior close (no same-day look-ahead).
    """
    reg = regime.shift(1).reindex(rets.index).ffill(limit=5)
    states = states if states is not None else [s for s in pd.unique(reg.dropna())]
    frames = {k: pd.DataFrame(index=rets.columns, columns=states, dtype=float)
              for k in ('ann_return', 'ann_vol', 'sharpe', 'hit_rate', 'max_dd', 'n_days')}

    for st in states:
        mask = reg == st
        sub = rets[mask]
        for col in rets.columns:
            s = sub[col].dropna()
            n = len(s)
            frames['n_days'].loc[col, st] = n
            if n < min_days:
                continue
            ann = (1 + s).prod() ** (TRADING_DAYS / n) - 1
            vol = s.std() * np.sqrt(TRADING_DAYS)
            frames['ann_return'].loc[col, st] = ann * 100
            frames['ann_vol'].loc[col, st] = vol * 100
            frames['sharpe'].loc[col, st] = ann / vol if vol else np.nan
            frames['hit_rate'].loc[col, st] = (s > 0).mean() * 100
            curve = (1 + s).cumprod()
            frames['max_dd'].loc[col, st] = ((curve / curve.cummax()) - 1).min() * 100
    return frames


def full_sample_stats(rets: pd.DataFrame) -> pd.DataFrame:
    rows = {}
    for col in rets.columns:
        s = rets[col].dropna()
        if len(s) < 60:
            continue
        n = len(s)
        ann = (1 + s).prod() ** (TRADING_DAYS / n) - 1
        vol = s.std() * np.sqrt(TRADING_DAYS)
        curve = (1 + s).cumprod()
        rows[col] = dict(ann_return=ann * 100, ann_vol=vol * 100,
                         sharpe=ann / vol if vol else np.nan,
                         start=s.index[0], end=s.index[-1], n_days=n,
                         max_dd=((curve / curve.cummax()) - 1).min() * 100)
    return pd.DataFrame(rows).T


def trend_signal(px: pd.Series, fast: int = 50, slow: int = 200) -> pd.Series:
    """Two-speed binary trend: +1 both trends up, -1 both down, 0 mixed."""
    f = np.sign(px - px.rolling(fast).mean())
    s = np.sign(px - px.rolling(slow).mean())
    sig = pd.Series(0.0, index=px.index)
    sig[(f > 0) & (s > 0)] = 1.0
    sig[(f < 0) & (s < 0)] = -1.0
    return sig


def rolling_returns(tickers: dict, months: int = 3) -> pd.DataFrame:
    px = load_prices(list(tickers.values()))
    px = px.rename(columns={v: k for k, v in tickers.items()})
    wk = px.resample('W-FRI').last()
    return wk.pct_change(months * 4 + 1) * 100


if __name__ == '__main__':
    gi = growth_inflation_regime()
    print('Growth/Inflation regime:', gi.index[0].date(), '->', gi.index[-1].date())
    print(gi.quadrant.value_counts())
    print('\nCurrent:', gi.iloc[-1].to_dict())
    r = daily_returns(MAJORS_PLUS)
    st = regime_stats(r, gi.quadrant, QUADRANTS)
    pd.set_option('display.width', 200)
    print('\nAnnualized return by quadrant (%):')
    print(st['ann_return'].round(1))
    print('\nDays per quadrant:')
    print(st['n_days'].astype('Int64'))
