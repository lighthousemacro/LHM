"""
Expanded Pillar Component Specs v2
====================================
Tier 1 must-adds from the Apr 30 2026 basket audit, applied to the 10 unblocked
pillars (LPI, PCI, GCI, HCI, CCI, BCI, TCI, GCI_Gov→FPI, FCI, LCI).

MSI and SPI are NOT expanded here:
  - MSI breadth components (% above MAs, AD line, McClellan) only have ~812 obs
    from Feb 2023, when breadth_fetcher.py first ran. Need backfill.
  - SPI documented components (NAAIM, II, Put/Call, ETF flows, VIX backwardation)
    are not ingested — separate ingestion sprint required.

Each pillar's spec follows the same shape as `pillar_weight_optimization.PILLAR_SPECS`:
  components: list of (series_id, sign, transform, prior_weight)
    sign = ±1 (theoretical direction)
    transform = 'level' / 'yoy_pct' / 'delta' / 'log_yoy'
  target: (series_id, horizon_days, mode, event_threshold)
  risk_side: 'low' / 'high' / 'extreme'
"""

EXPANDED_PILLAR_SPECS = {
    # =========================================================================
    # LABOR PRESSURE (LPI) — adds ICSA, CCSA, AHETPI, U6RATE, AWHAETP
    # =========================================================================
    'LPI': {
        'components': [
            # Original 6
            ('UNRATE',    +1, 'level',   None),
            ('UEMP27OV',  +1, 'level',   0.35),
            ('JTSQUR',    -1, 'level',   0.35),  # high quits = healthy
            ('JTSHIR',    -1, 'level',   None),
            ('JTSJOL',    -1, 'level',   None),
            ('TEMPHELPS', -1, 'yoy_pct', None),
            # Tier 1 additions
            ('ICSA',      +1, 'yoy_pct', None),  # Initial claims YoY
            ('CCSA',      +1, 'yoy_pct', None),  # Continuing claims YoY
            ('AHETPI',    -1, 'yoy_pct', None),  # Wage growth (high = labor tight = low LPI)
            ('U6RATE',    +1, 'level',   None),  # Broader unemployment (U-6)
            ('AWHAETP',   -1, 'yoy_pct', None),  # Avg weekly hours (falling = recession)
        ],
        'target': ('UNRATE', 252, 'delta', 0.5),
        'risk_side': 'high',
    },

    # =========================================================================
    # INFLATION HEAT (PCI) — adds PCEPI, sticky/median/trimmed, breakevens, expectations
    # =========================================================================
    'PCI': {
        'components': [
            # Original 5
            ('CPIAUCSL',              +1, 'yoy_pct', None),
            ('CPILFESL',              +1, 'yoy_pct', None),
            ('PCEPILFE',              +1, 'yoy_pct', None),
            ('CPIHOSSL',              +1, 'yoy_pct', None),
            ('TRMMEANCPIM158SFRBCLE', +1, 'level',   None),  # already annualized
            # Tier 1 additions
            ('PCEPI',                 +1, 'yoy_pct', None),  # Headline PCE
            ('MEDCPIM158SFRBCLE',     +1, 'level',   None),  # Cleveland median CPI annualized
            ('PCETRIM12M159SFRBDAL',  +1, 'level',   None),  # Dallas trimmed PCE 12mo
            ('STICKCPIM158SFRBATL',   +1, 'level',   None),  # Atlanta sticky CPI
            ('CORESTICKM158SFRBATL',  +1, 'level',   None),  # Atlanta sticky core
            ('T5YIE',                 +1, 'level',   None),  # 5y breakeven
            ('T10YIE',                +1, 'level',   None),  # 10y breakeven
            ('MICH',                  +1, 'level',   None),  # UMich 1y expectations
            ('PPIFIS',                +1, 'yoy_pct', None),  # PPI final demand
        ],
        'target': ('PCEPILFE', 365, 'yoy_pct_level', None),
        'risk_side': 'high',
    },

    # =========================================================================
    # ACTIVITY PULSE (GCI) — adds CFNAI, BBK, RPI, PCEC96, HOANBS
    # =========================================================================
    'GCI': {
        'components': [
            # Original
            ('INDPRO',     +1, 'yoy_pct', None),
            ('PAYEMS',     +1, 'yoy_pct', None),
            ('RSXFS',      +1, 'yoy_pct', None),
            ('TCU',        +1, 'level',   None),
            ('MANEMP',     +1, 'yoy_pct', None),
            # Tier 1 additions
            ('CFNAIMA3',   +1, 'level',   None),  # Chicago Fed coincident
            ('BBKMLEIX',   +1, 'level',   None),  # Brave-Butters-Kelley leading
            ('RPI',        +1, 'yoy_pct', None),  # Real personal income
            ('PCEC96',     +1, 'yoy_pct', None),  # Real PCE monthly
            ('HOANBS',     +1, 'yoy_pct', None),  # Hours worked
        ],
        'target': ('INDPRO', 252, 'yoy_pct_level', None),
        'risk_side': 'low',
    },

    # =========================================================================
    # HOUSING TIDE (HCI) — adds HOUST1F, Case-Shiller, MORTGAGE15US, delinquency
    # =========================================================================
    'HCI': {
        'components': [
            # Original
            ('HOUST',         +1, 'yoy_pct', None),
            ('PERMIT',        +1, 'yoy_pct', None),
            ('HSN1F',         +1, 'yoy_pct', None),
            ('MORTGAGE30US',  -1, 'level',   None),
            ('MSACSR',        -1, 'level',   None),
            # Tier 1 additions
            ('HOUST1F',       +1, 'yoy_pct', None),  # Single-family starts
            ('CSUSHPINSA',    +1, 'yoy_pct', None),  # Case-Shiller
            ('MORTGAGE15US',  -1, 'level',   None),  # 15y mortgage
            ('DRSFRMACBS',    -1, 'level',   None),  # Mortgage delinquency (high = stress)
            ('MSPUS',         +1, 'yoy_pct', None),  # Median home price
        ],
        'target': ('HOUST', 365, 'yoy_pct_level', -10.0),
        'risk_side': 'low',
    },

    # =========================================================================
    # CONSUMER PULSE (CCI) — GROUND-UP REBUILD per documented Feb 2026 formula
    # Replaces the broken composite (-0.05 vs Real PCE)
    # =========================================================================
    'CCI': {
        'components': [
            # Documented Feb 2026 + Tier 1 adds
            ('PCEC96',     +1, 'yoy_pct', 0.25),  # Real PCE — was MISSING from old basket
            ('RSXFS',      +1, 'yoy_pct', 0.15),
            ('PSAVERT',    +1, 'level',   0.10),  # documented as 0.20, but tier1 adds dilute
            ('UMCSENT',    +1, 'level',   0.05),
            ('RPI',        +1, 'yoy_pct', 0.10),  # Real personal income (Tier 1)
            ('DSPIC96',    +1, 'yoy_pct', 0.05),
            ('TOTALSL',    -1, 'yoy_pct', 0.05),  # Total consumer credit growth (rising = stress under high rates)
            ('REVOLSL',    -1, 'yoy_pct', 0.05),  # Revolving credit
            ('DRCCLACBS',  -1, 'level',   0.10),  # CC delinquency — was MISSING
            ('TDSP',       -1, 'level',   0.10),  # Debt service ratio — was MISSING
        ],
        'target': ('PCEC96', 252, 'yoy_pct_level', None),  # Target Real PCE not SPX
        'risk_side': 'low',
    },

    # =========================================================================
    # CAPEX THRUST (BCI) — GROUND-UP: drop BUSINV, add ANDENO + capex chain
    # =========================================================================
    'BCI': {
        'components': [
            # Cleaned + Tier 1
            ('NEWORDER',    +1, 'yoy_pct', None),  # Total mfg orders (kept)
            ('ANDENO',      +1, 'yoy_pct', None),  # Standard capex proxy (Tier 1, was missing)
            ('ANXAVS',      +1, 'yoy_pct', None),  # Capex shipments
            ('ACDGNO',      +1, 'yoy_pct', None),  # Durable orders ex-defense
            ('AMTMNO',      +1, 'yoy_pct', None),  # Total mfg new orders
            ('CAPB50001S',  +1, 'yoy_pct', None),  # Industrial capacity
            ('BUSLOANS',    +1, 'yoy_pct', None),  # Business loans (kept)
            ('GPDIC1',      +1, 'yoy_pct', None),  # Real private investment (kept)
            # Dropped: BUSINV (low signal)
        ],
        'target': ('ANDENO', 252, 'yoy_pct_level', None),  # Target capex not arbitrary
        'risk_side': 'low',
    },

    # =========================================================================
    # GLOBAL TIDE (TCI) — adds JPY, CNY, MXN crosses, gross flows, terms-of-trade
    # =========================================================================
    'TCI': {
        'components': [
            # Original
            ('DTWEXBGS',  +1, 'level',   None),
            ('BOPGSTB',   +1, 'level',   None),
            ('NETEXP',    +1, 'level',   None),
            # Tier 1
            ('DEXJPUS',   +1, 'level',   None),  # USD/JPY
            ('DEXCHUS',   +1, 'level',   None),  # USD/CNY
            ('DEXMXUS',   +1, 'level',   None),  # USD/MXN
            ('BOPTEXP',   +1, 'yoy_pct', None),  # Gross exports
            ('BOPTIMP',   -1, 'yoy_pct', None),  # Gross imports (rising = TCI down?)
            ('IQ',        +1, 'yoy_pct', None),  # Export price index
            ('IR',        -1, 'yoy_pct', None),  # Import price index (rising = trade weakening)
        ],
        'target': ('DTWEXBGS', 252, 'log_fwd_return', None),
        'risk_side': 'high',
    },

    # =========================================================================
    # FISCAL PRESSURE (GCI_Gov / FPI) — adds long+short tsy, 10y-3m, debt level
    # =========================================================================
    'GCI_Gov': {
        'components': [
            # Original
            ('DGS10',       +1, 'level',   None),
            ('T10Y2Y',      -1, 'level',   None),  # Inverted curve = stress (negative)
            ('THREEFYTP10', +1, 'level',   None),  # Term premium
            ('BAA10Y',      +1, 'level',   None),  # IG spread (kept)
            # Tier 1
            ('DGS30',       +1, 'level',   None),  # Long end
            ('DGS3MO',      +1, 'level',   None),  # Front end
            ('T10Y3M',      -1, 'level',   None),  # 10y-3m (NBER recession spread)
            ('FEDDT',       +1, 'yoy_pct', None),  # Federal debt growth
            ('FDHBFIN',     -1, 'yoy_pct', None),  # Foreign debt holdings (falling = stress)
        ],
        'target': ('THREEFYTP10', 252, 'delta', None),
        'risk_side': 'high',
    },

    # =========================================================================
    # CREDIT TIDE (FCI) — adds ANFCI, AAA, delinquency, charge-offs, SLOOS
    # =========================================================================
    'FCI': {
        'components': [
            # Original
            ('BAMLH0A0HYM2', +1, 'level',   None),
            ('BAMLC0A0CM',   +1, 'level',   None),
            ('VIXCLS',       +1, 'level',   None),
            ('BAA10YM',      +1, 'level',   None),
            # Tier 1
            ('ANFCI',        +1, 'level',   None),  # Adjusted NFCI (Chicago Fed)
            ('AAA10Y',       +1, 'level',   None),  # AAA spread
            ('DRALACBS',     +1, 'level',   None),  # All-loans delinquency
            ('CORCCACBS',    +1, 'level',   None),  # CC charge-offs
            ('DRTSCILM',     +1, 'level',   None),  # SLOOS C&I tightening
        ],
        'target': ('BAMLH0A0HYM2', 126, 'fwd_max_change', None),
        'risk_side': 'high',
    },

    # =========================================================================
    # LIQUIDITY CUSHION (LCI) — adds IORB, EFFR, TGCR, MMF series
    # =========================================================================
    'LCI': {
        'components': [
            # Original
            ('TOTRESNS',                  +1, 'yoy_pct', None),
            ('RRPONTSYD',                 +1, 'yoy_pct', None),
            ('WALCL',                     +1, 'yoy_pct', None),
            ('WTREGEN',                   -1, 'yoy_pct', None),  # Rising TGA = liquidity drain
            ('SOFR',                      -1, 'level',   None),  # High SOFR = scarce
            # Tier 1
            ('IORB',                      -1, 'level',   None),  # Interest on reserves
            ('EFFR',                      -1, 'level',   None),  # Effective fed funds
            ('NYFED_TGCR',                -1, 'level',   None),  # Tri-party GC rate
            ('OFR_MMF-MMF_RP_TOT-M',      +1, 'yoy_pct', None),  # MMF Repo (more = abundant)
            ('OFR_MMF-MMF_TOT-M',         +1, 'yoy_pct', None),  # MMF Total Assets
        ],
        'target': ('BAMLH0A0HYM2', 63, 'fwd_max_change', None),
        'risk_side': 'low',
    },
}

# Display names per the 2026-05-08 naming lock
DISPLAY_NAMES = {
    'LPI':     'Labor Pressure',
    'PCI':     'Inflation Heat',
    'GCI':     'Activity Pulse',
    'HCI':     'Housing Tide',
    'CCI':     'Consumer Pulse',
    'BCI':     'Capex Thrust',
    'TCI':     'Global Risk Tide',
    'GCI_Gov': 'Fiscal Pressure',
    'FCI':     'Credit Tide',
    'LCI':     'Liquidity Cushion',
    'MSI':     'Market Breadth Pulse',
    'SPI':     'Sentiment Tide',
    'LFI':     'Labor Fragility',
    'CLG':     'Credit-Labor Gap',
    'SBD':     'Structure-Breadth Divergence',
    'SSD':     'Sentiment-Structure Divergence',
    'CLI':     'Crypto Liquidity Impulse',
    'SLI':     'Stablecoin Liquidity Impulse',
    'MRI':     'Macro Risk Index',
}
