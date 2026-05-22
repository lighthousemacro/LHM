#!/usr/bin/env python3
import ast
import glob
import json
import os
import sys
from pathlib import Path

try:
    import dash
except ImportError:
    print(
        "ny_fed_dashboard_live needs dash, plotly, and pandas.\n\n"
        "On Homebrew Python, use a venv (PEP 668 blocks global pip), e.g.:\n"
        "  python3 -m venv .venv && .venv/bin/pip install dash plotly pandas\n"
        "  .venv/bin/python Scripts/ny_fed_dashboard_live.py\n",
        file=sys.stderr,
    )
    sys.exit(1)
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Input, Output, dash_table, dcc, html

app = dash.Dash(__name__)
app.title = 'NY Fed Market Data Dashboard'

# Resolve CSVs relative to repo root (parent of Scripts/), not the shell cwd.
_REPO_ROOT = Path(__file__).resolve().parent.parent
base_dir = str(_REPO_ROOT / "ny_fed_data")

def latest(pattern):
    files = glob.glob(pattern)
    files.sort()
    return files[-1] if len(files) > 0 else None

# Generic loaders

def load_reference_rates():
    path = latest(os.path.join(base_dir, 'reference_rates_*.csv'))
    if path is None:
        return pd.DataFrame()
    df = pd.read_csv(path)
    if 'effectiveDate' in df.columns:
        df['effectiveDate'] = pd.to_datetime(df['effectiveDate'], errors='coerce')
    for c in ['percentRate','volumeInBillions','average30day','average90day','average180day']:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors='coerce')
    return df


def parse_nested_column(csv_path, preferred_cols=None):
    if csv_path is None:
        return pd.DataFrame()
    df_raw = pd.read_csv(csv_path)
    cand_cols = []
    if preferred_cols is not None:
        for c in preferred_cols:
            if c in df_raw.columns:
                cand_cols.append(c)
    for c in df_raw.columns:
        if c not in cand_cols and df_raw[c].dtype == object:
            cand_cols.append(c)
    chosen = None
    for c in cand_cols:
        vals = df_raw[c].dropna()
        if len(vals) == 0:
            continue
        ok = 0
        for v in vals.head(5):
            parsed = None
            if isinstance(v, dict):
                parsed = v
            else:
                s = str(v).strip()
                try:
                    parsed = ast.literal_eval(s)
                except Exception:
                    try:
                        parsed = json.loads(s)
                    except Exception:
                        parsed = None
            if isinstance(parsed, dict):
                ok += 1
        if ok >= 1:
            chosen = c
            break
    if chosen is None:
        return pd.DataFrame()
    rows = []
    for _, r in df_raw.iterrows():
        v = r[chosen]
        if isinstance(v, dict):
            rows.append(v)
        else:
            s = str(v).strip()
            try:
                parsed = ast.literal_eval(s)
            except Exception:
                try:
                    parsed = json.loads(s)
                except Exception:
                    parsed = {}
            if isinstance(parsed, dict):
                rows.append(parsed)
            else:
                rows.append({})
    return pd.DataFrame(rows)


def _read_csv_flat_or_nested(path, nested_keys, flat_key):
    if path is None:
        return pd.DataFrame()
    raw = pd.read_csv(path)
    if flat_key in raw.columns:
        return raw
    return parse_nested_column(path, nested_keys)


def load_soma():
    path = latest(os.path.join(base_dir, 'soma_holdings_*.csv'))
    df = _read_csv_flat_or_nested(path, ['summary'], 'asOfDate')
    if 'asOfDate' in df.columns:
        df['asOfDate'] = pd.to_datetime(df['asOfDate'], errors='coerce')
    for c in ['mbs','cmbs','tips','tipsInflationCompensation','notesbonds','bills','agencies','total']:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors='coerce')
    return df


def load_repo():
    path = latest(os.path.join(base_dir, 'repo_operations_*.csv'))
    df = _read_csv_flat_or_nested(path, ['operations'], 'operationDate')
    for dc in ['operationDate','settlementDate','maturityDate','lastUpdated']:
        if dc in df.columns:
            df[dc] = pd.to_datetime(df[dc], errors='coerce')
    for nc in ['totalAmtSubmitted','totalAmtAccepted','operationLimit','participatingCpty']:
        if nc in df.columns:
            df[nc] = pd.to_numeric(df[nc], errors='coerce')
    return df


def load_rrp():
    path = latest(os.path.join(base_dir, 'reverse_repo_detailed_*.csv'))
    df = _read_csv_flat_or_nested(path, ['operations'], 'operationDate')
    for dc in ['operationDate','settlementDate','maturityDate','lastUpdated']:
        if dc in df.columns:
            df[dc] = pd.to_datetime(df[dc], errors='coerce')
    for nc in ['totalAmtSubmitted','totalAmtAccepted','operationLimit','participatingCpty']:
        if nc in df.columns:
            df[nc] = pd.to_numeric(df[nc], errors='coerce')
    return df

# Load once at app start; add Refresh button for manual reload
ref = load_reference_rates()
soma = load_soma()
repo = load_repo()
rrp = load_rrp()

# Layout
app.layout = html.Div([
    html.Div([
        html.H1('New York Fed Market Data Dashboard'),
        html.P('Reference rates, SOMA holdings, repo and reverse repo operations')
    ], className='header'),

    html.Div([
        dcc.Tabs(id='tabs', value='rates', children=[
            dcc.Tab(label='Reference Rates', value='rates'),
            dcc.Tab(label='SOMA Holdings', value='soma'),
            dcc.Tab(label='Repo Operations', value='repo'),
            dcc.Tab(label='Reverse Repo', value='rrp'),
        ])
    ], className='tab-container'),

    html.Div(id='controls'),
    html.Div(id='content'),

    html.Div('Source: Federal Reserve Bank of New York Market Data', className='footer')
])

# Dynamic controls per tab
@app.callback(Output('controls','children'), Input('tabs','value'))
def render_controls(tab):
    if tab == 'rates':
        rate_types = sorted([t for t in ref['type'].dropna().unique()]) if not ref.empty else []
        return html.Div([
            html.Div([
                html.Label('Rate Types'),
                dcc.Dropdown(options=[{'label': t, 'value': t} for t in rate_types],
                             value=rate_types,
                             multi=True,
                             id='rates-types')
            ], className='control-item'),
            html.Div([
                html.Label('Date Range'),
                dcc.DatePickerRange(id='rates-dates',
                                    min_date_allowed=ref['effectiveDate'].min() if not ref.empty else None,
                                    max_date_allowed=ref['effectiveDate'].max() if not ref.empty else None,
                                    start_date=ref['effectiveDate'].max() - pd.Timedelta(days=60) if not ref.empty else None,
                                    end_date=ref['effectiveDate'].max() if not ref.empty else None)
            ], className='control-item')
        ], className='control-bar')
    if tab == 'soma':
        components = [c for c in ['notesbonds','mbs','bills','tips','agencies'] if c in soma.columns]
        return html.Div([
            html.Div([
                html.Label('Components'),
                dcc.Dropdown(options=[{'label': c.capitalize(), 'value': c} for c in components],
                             value=components,
                             multi=True,
                             id='soma-components')
            ], className='control-item')
        ], className='control-bar')
    if tab == 'repo':
        terms = sorted([t for t in repo.get('term', pd.Series(dtype='object')).dropna().unique()]) if not repo.empty and 'term' in repo.columns else []
        return html.Div([
            html.Div([
                html.Label('Terms'),
                dcc.Dropdown(options=[{'label': t, 'value': t} for t in terms],
                             value=terms,
                             multi=True,
                             id='repo-terms')
            ], className='control-item')
        ], className='control-bar')
    if tab == 'rrp':
        return html.Div([
            html.Div([
                html.Label('Show Participants Overlay'),
                dcc.Checklist(options=[{'label': 'Participants', 'value': 'show'}],
                              value=['show'], id='rrp-show-part')
            ], className='control-item')
        ], className='control-bar')
    return html.Div()

# Content per tab with interactivity
@app.callback(Output('content','children'),
              Input('tabs','value'))
def render_content(tab):
    if tab == 'rates':
        if ref.empty:
            return html.Div('No reference rate data available')
        df = ref.copy()
        # Show all data by default
        fig = px.line(df.sort_values('effectiveDate'), x='effectiveDate', y='percentRate', color='type', title='Reference Rates Over Time')
        latest = df.sort_values('effectiveDate').dropna(subset=['percentRate']).groupby('type').tail(1)
        table_cols = ['type', 'effectiveDate', 'percentRate', 'volumeInBillions', 'average30day', 'average90day', 'average180day']
        return html.Div([
            dcc.Graph(figure=fig),
            html.H4('Most Recent Observations'),
            dash_table.DataTable(columns=[{'name': c, 'id': c} for c in table_cols],
                                 data=latest[table_cols].to_dict('records'),
                                 page_size=10,
                                 style_table={'overflowX': 'auto'})
        ])
    if tab == 'soma':
        if soma.empty:
            return html.Div('No SOMA data available')
        show_cols = [c for c in ['notesbonds', 'mbs', 'bills', 'tips', 'agencies'] if c in soma.columns]
        srt = soma.sort_values('asOfDate')
        fig = go.Figure()
        for c in show_cols:
            if c in srt.columns:
                fig.add_trace(go.Scatter(x=srt['asOfDate'], y=srt[c]/1e12, name=c))
        fig.update_layout(title='SOMA Holdings by Component (Trillions USD)')
        latest_row = srt.dropna(subset=['asOfDate']).iloc[-1] if not srt.empty else None
        summary_cols = ['total'] + show_cols
        if latest_row is not None:
            summary = [{ 'Component': col, 'Level (T)': (latest_row[col]/1e12 if pd.notna(latest_row.get(col)) else None) } for col in summary_cols if col in srt.columns]
        else:
            summary = []
        return html.Div([
            dcc.Graph(figure=fig),
            html.H4('Latest SOMA Snapshot'),
            dash_table.DataTable(columns=[{'name': k, 'id': k} for k in ['Component', 'Level (T)']],
                                 data=summary, page_size=10)
        ])
    if tab == 'repo':
        if repo.empty:
            return html.Div('No repo data available')
        df = repo.copy().sort_values('operationDate')
        fig = px.bar(df.tail(40), x='operationDate', y='totalAmtAccepted', color=df.get('term', 'operationType'), title='Repo Accepted Amounts (Recent)')
        return html.Div([
            dcc.Graph(figure=fig),
            html.H4('Recent Operations'),
            dash_table.DataTable(columns=[{'name': c, 'id': c} for c in ['operationDate', 'operationType', 'term', 'totalAmtAccepted', 'operationLimit'] if c in df.columns],
                                 data=df[['operationDate', 'operationType', 'term', 'totalAmtAccepted', 'operationLimit']].tail(20).to_dict('records'),
                                 page_size=10)
        ])
    if tab == 'rrp':
        if rrp.empty:
            return html.Div('No reverse repo data available')
        df = rrp.copy().sort_values('operationDate')
        traces = [go.Scatter(x=df['operationDate'], y=df['totalAmtAccepted']/1e9, name='Accepted ($B)', line=dict(color='#0066cc'))]
        if 'participatingCpty' in df.columns:
            traces.append(go.Scatter(x=df['operationDate'], y=df['participatingCpty'], name='Participants', yaxis='y2', line=dict(color='#999999')))
        fig = go.Figure(traces)
        fig.update_layout(title='Reverse Repo: Volume and Participants',
                          yaxis=dict(title='Volume ($ Billions)'),
                          yaxis2=dict(title='Participants', overlaying='y', side='right'))
        return html.Div([
            dcc.Graph(figure=fig),
            html.H4('Recent Operations'),
            dash_table.DataTable(columns=[{'name': c, 'id': c} for c in ['operationDate', 'totalAmtAccepted', 'participatingCpty'] if c in df.columns],
                                 data=df[['operationDate', 'totalAmtAccepted', 'participatingCpty']].tail(20).to_dict('records'),
                                 page_size=10)
        ])
    return html.Div()

def ensure_data():
    data_path = Path(base_dir)
    data_path.mkdir(parents=True, exist_ok=True)
    if list(data_path.glob("*.csv")):
        return
    fetch_script = _REPO_ROOT / "Scripts" / "fetch_ny_fed_data.py"
    print("No ny_fed_data CSVs found — pulling fresh from NY Fed API...")
    import subprocess
    subprocess.run([sys.executable, str(fetch_script)], check=True, cwd=str(_REPO_ROOT))
    global ref, soma, repo, rrp
    ref = load_reference_rates()
    soma = load_soma()
    repo = load_repo()
    rrp = load_rrp()


if __name__ == '__main__':
    data_path = Path(base_dir)
    ensure_data()
    n = len(list(data_path.glob("*.csv")))
    print(f"NY Fed dashboard — {n} CSV(s) in {data_path}")
    print("Open http://127.0.0.1:8050/ in a browser (Ctrl+C to stop)")
    app.run(debug=True, host="127.0.0.1", port=8050)
