# LIGHTHOUSE MACRO - MODELING & BACKTESTING ARCHITECTURE

**Purpose:** Systematic framework for validating, improving, and operationalizing the Diagnostic Dozen

---

## EXECUTIVE SUMMARY

The goal is a multi-layer diagnostic system:

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           REGIME IDENTIFICATION                                  │
│                                                                                 │
│   ECONOMIC REGIME (MRI-based)              MARKET REGIME (MSI/SPI-based)        │
│   ┌───────────────────────────┐            ┌───────────────────────────┐        │
│   │ Expansion │ Late-Cycle    │            │ Risk-On  │ Transition    │        │
│   │ Slowdown  │ Recession     │            │ Risk-Off │ Capitulation  │        │
│   │ Recovery  │               │            │          │               │        │
│   └───────────────────────────┘            └───────────────────────────┘        │
│                         ↓                              ↓                        │
│                    ┌─────────────────────────────────────┐                      │
│                    │      COMBINED REGIME MATRIX         │                      │
│                    │   (Economic × Market = 12-20 states)│                      │
│                    └─────────────────────────────────────┘                      │
│                                      ↓                                          │
│   ┌──────────────────────────────────────────────────────────────────────┐      │
│   │                    ALLOCATION DECISION TREE                          │      │
│   │                                                                      │      │
│   │  ASSET CLASS → SUB-ASSET → SECTOR → (Geography later)               │      │
│   │  ┌─────────┐   ┌─────────┐   ┌─────────┐                            │      │
│   │  │Equities │   │Large/Mid│   │Cyclicals│                            │      │
│   │  │Fixed Inc│   │Growth/  │   │Defensive│                            │      │
│   │  │Commodit │   │Value    │   │Rates-   │                            │      │
│   │  │Cash     │   │Duration │   │Sensitive│                            │      │
│   │  │Alts     │   │Credit   │   │         │                            │      │
│   │  └─────────┘   └─────────┘   └─────────┘                            │      │
│   └──────────────────────────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## PART 1: WHAT WE'RE ACTUALLY MODELING

### 1.1 The Two Regime Types

**Economic Regime** (from Pillars 1-10):
- What phase of the business/credit cycle are we in?
- Leading indicators: LFI, LCI, CLG, GCI, etc.
- Changes slowly (months to quarters)

**Market Regime** (from Pillars 11-12):
- What is the market's current risk appetite and structure?
- Leading indicators: MSI, SPI, SBD, SSD
- Changes quickly (days to weeks)

**Key Insight:** These can diverge significantly. Economy can be weakening while markets remain euphoric (late 2007, early 2020). The gap between them IS the alpha opportunity.

### 1.2 The Diagnostic Questions at Each Level

| Level | Question | Index/Signal | Decision |
|-------|----------|--------------|----------|
| **Regime** | "What environment are we in?" | MRI + MSI combination | Sets baseline allocation bands |
| **Asset Class** | "Where should capital flow?" | Regime-specific return/risk profiles | Equity/Bond/Commodity/Cash mix |
| **Sub-Asset** | "Which flavor within the class?" | Relative value + momentum signals | Growth/Value, Duration, Credit quality |
| **Sector** | "Which segments have tailwinds?" | Pillar-specific signals (HCI→Homebuilders) | Sector over/underweights |
| **Vehicle** | "How to express it?" | Liquidity, cost, tracking | (Tiered by client: ETF vs options vs swaps) |

---

## PART 2: BACKTESTING ARCHITECTURE

### 2.1 What Needs Validation

| Component | Validation Question | Method |
|-----------|---------------------|--------|
| **Individual Indicators** | "Does Quits Rate actually lead unemployment?" | Lead-lag analysis, Granger causality |
| **Composite Weights** | "Are the 0.35/0.35/0.30 weights for LFI optimal?" | Optimization, PCA, random forest importance |
| **Regime Thresholds** | "Is MRI > 1.5 really 'Crisis'?" | Historical regime labeling, state identification |
| **Allocation Rules** | "Does 25-35% equity in Crisis outperform?" | Walk-forward backtesting |
| **Signal Timing** | "How early do signals fire before events?" | Event study methodology |

### 2.2 Backtesting Framework Structure

```
/Users/bob/LHM/
├── Backtesting/
│   ├── __init__.py
│   ├── core/
│   │   ├── engine.py              # Walk-forward backtester
│   │   ├── metrics.py             # Sharpe, Sortino, max DD, etc.
│   │   ├── regime_labeler.py      # Historical regime identification
│   │   └── universe.py            # Asset/ETF definitions
│   │
│   ├── validation/
│   │   ├── indicator_validation.py    # Lead-lag, Granger tests
│   │   ├── weight_optimization.py     # PCA, ML-based weight tuning
│   │   ├── threshold_calibration.py   # Regime threshold validation
│   │   └── signal_persistence.py      # Autocorrelation, half-life
│   │
│   ├── strategies/
│   │   ├── regime_allocation.py       # MRI-based allocation
│   │   ├── tactical_overlay.py        # MSI/SPI timing signals
│   │   ├── sector_rotation.py         # Pillar-driven sector tilts
│   │   └── risk_parity_regime.py      # Risk-parity with regime adjustment
│   │
│   ├── analysis/
│   │   ├── event_studies.py           # Recession, correction analysis
│   │   ├── drawdown_analysis.py       # When did signals protect?
│   │   └── attribution.py             # What drove returns?
│   │
│   └── reports/
│       ├── validation_report.py       # Generate indicator validation report
│       └── backtest_report.py         # Strategy performance report
```

### 2.3 Walk-Forward Protocol

```python
# Pseudo-code for walk-forward validation

class WalkForwardBacktest:
    """
    Walk-forward with expanding or rolling window.

    Key principle: NEVER use future data.
    - Z-scores computed with data available at time t only
    - Regime thresholds calibrated on training window only
    - Rebalance decisions made with lagged data (account for publication delays)
    """

    def __init__(self,
                 train_years: int = 5,        # Initial training window
                 test_months: int = 6,        # Out-of-sample test period
                 expanding: bool = True,      # Expanding vs rolling
                 rebalance_freq: str = "M"):  # Monthly rebalance
        pass

    def run(self, data: pd.DataFrame, strategy: Strategy) -> BacktestResult:
        """
        1. For each test period:
           a. Train regime model on historical data only
           b. Identify current regime using trained model
           c. Execute allocation based on regime
           d. Record returns and exposures
        2. Aggregate results across all test periods
        3. Compute performance metrics
        """
        pass
```

### 2.4 Publication Lag Handling

**Critical:** Many series have publication delays. The backtest must respect these.

| Series | Publication Lag | Backtest Treatment |
|--------|-----------------|-------------------|
| JOLTS (Quits, Hires) | ~5 weeks | Use t-35 days |
| Initial Claims | 5 days | Use t-5 days |
| CPI | 2 weeks | Use t-14 days |
| GDP | 4 weeks | Use t-28 days |
| Market data | Real-time | Use t-1 (close) |
| Fed balance sheet | 1 day | Use t-1 |

```python
# Publication lag registry
PUBLICATION_LAGS = {
    "JOLTS_Quits_Rate": 35,
    "JOLTS_Hires_Rate": 35,
    "Initial_Claims": 5,
    "CPI_Core_yoy": 14,
    "PCE_Core_yoy": 28,
    "RRP_Usage": 1,
    "Bank_Reserves": 1,
    "HY_OAS": 1,
    # ... etc
}

def get_available_data(df: pd.DataFrame, as_of_date: pd.Timestamp) -> pd.DataFrame:
    """Return only data that would have been available on as_of_date."""
    result = df.copy()
    for col, lag_days in PUBLICATION_LAGS.items():
        if col in result.columns:
            mask = result.index > (as_of_date - pd.Timedelta(days=lag_days))
            result.loc[mask, col] = np.nan
    return result
```

---

## PART 3: ML/STATISTICAL METHODS TO APPLY

### 3.1 For Indicator Validation

| Method | Purpose | Application |
|--------|---------|-------------|
| **Granger Causality** | Test if X leads Y | Does LFI Granger-cause unemployment rate? |
| **Cross-correlation** | Optimal lead/lag | What's the peak correlation lag for Quits → Claims? |
| **Impulse Response** | Dynamic response | How do equities respond to LCI shocks? |
| **Rolling Regression** | Stability testing | Are relationships stable or time-varying? |

```python
from statsmodels.tsa.stattools import grangercausalitytests, ccf
from statsmodels.tsa.vector_ar.var_model import VAR

def validate_lead_lag(leading: pd.Series, lagging: pd.Series, max_lag: int = 12):
    """
    Test if 'leading' indicator actually leads 'lagging' indicator.

    Returns:
        - Optimal lag (in periods)
        - Cross-correlation at optimal lag
        - Granger causality p-value
        - Confidence assessment
    """
    # Cross-correlation function
    ccf_values = ccf(leading.dropna(), lagging.dropna(), adjusted=False)
    optimal_lag = np.argmax(np.abs(ccf_values[:max_lag]))

    # Granger causality
    data = pd.concat([lagging, leading], axis=1).dropna()
    gc_result = grangercausalitytests(data, maxlag=max_lag, verbose=False)

    return {
        "optimal_lag": optimal_lag,
        "correlation_at_lag": ccf_values[optimal_lag],
        "granger_pvalues": [gc_result[i+1][0]['ssr_ftest'][1] for i in range(max_lag)]
    }
```

### 3.2 For Weight Optimization

| Method | Purpose | When to Use |
|--------|---------|-------------|
| **PCA** | Identify orthogonal factors | Reduce redundancy in pillar components |
| **Lasso/Elastic Net** | Sparse weight selection | Which components actually matter? |
| **Random Forest Importance** | Non-linear importance | Capture interaction effects |
| **Bayesian Optimization** | Hyperparameter tuning | Optimize thresholds/weights jointly |

```python
from sklearn.decomposition import PCA
from sklearn.linear_model import LassoCV, ElasticNetCV
from sklearn.ensemble import RandomForestRegressor

def optimize_composite_weights(components: pd.DataFrame,
                               target: pd.Series,
                               method: str = "elastic_net") -> dict:
    """
    Find optimal weights for composite index components.

    Args:
        components: DataFrame of z-scored component series
        target: What we're trying to predict (e.g., forward returns, recession)
        method: "pca", "lasso", "elastic_net", "random_forest"

    Returns:
        Optimized weights and diagnostics
    """
    X = components.dropna()
    y = target.loc[X.index]

    if method == "elastic_net":
        model = ElasticNetCV(l1_ratio=[.1, .5, .7, .9, .95, 1], cv=5)
        model.fit(X, y)
        weights = dict(zip(X.columns, model.coef_))

    elif method == "random_forest":
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X, y)
        weights = dict(zip(X.columns, model.feature_importances_))

    # Normalize to sum to 1
    total = sum(abs(v) for v in weights.values())
    weights = {k: v/total for k, v in weights.items()}

    return weights
```

### 3.3 For Regime Identification

| Method | Purpose | Application |
|--------|---------|-------------|
| **Hidden Markov Models (HMM)** | Unsupervised regime detection | Let data reveal natural regimes |
| **Gaussian Mixture Models** | Cluster-based regimes | Group similar market conditions |
| **Change Point Detection** | Identify transitions | When did regime actually change? |
| **Supervised Classification** | Labeled regime prediction | Predict NBER recession/expansion |

```python
from hmmlearn import hmm
from sklearn.mixture import GaussianMixture

class RegimeDetector:
    """
    Detect economic/market regimes using statistical methods.
    """

    def fit_hmm(self, features: pd.DataFrame, n_regimes: int = 4):
        """
        Fit Hidden Markov Model to identify latent regimes.

        Regimes emerge from:
        - Emission distributions (what values are typical in each regime)
        - Transition matrix (how likely to move between regimes)
        """
        model = hmm.GaussianHMM(
            n_components=n_regimes,
            covariance_type="full",
            n_iter=100,
            random_state=42
        )
        model.fit(features.values)

        # Decode most likely regime sequence
        regimes = model.predict(features.values)

        return {
            "regimes": pd.Series(regimes, index=features.index),
            "transition_matrix": model.transmat_,
            "regime_means": model.means_,
            "regime_covars": model.covars_
        }

    def validate_against_nber(self, detected_regimes: pd.Series,
                               nber_recessions: pd.Series) -> dict:
        """
        Compare detected regimes against NBER recession dates.

        Key metrics:
        - True positive rate (how many recessions did we catch?)
        - Lead time (how early did we detect?)
        - False positive rate (how many false alarms?)
        """
        pass
```

### 3.4 For Time Series Forecasting

| Method | Purpose | Application |
|--------|---------|-------------|
| **VAR/VECM** | Multivariate forecasting | Joint dynamics of macro variables |
| **ARIMA-X** | Univariate with exogenous | Forecast GDP with leading indicators |
| **Prophet** | Trend + seasonality | Handle irregular macro data |
| **LSTM/GRU** | Deep learning sequences | Capture complex non-linear patterns |
| **Gradient Boosting** | Feature-rich prediction | XGBoost/LightGBM for regime prediction |

```python
# Example: Gradient boosting for regime prediction

import lightgbm as lgb
from sklearn.model_selection import TimeSeriesSplit

def train_regime_classifier(features: pd.DataFrame,
                            regime_labels: pd.Series,
                            n_splits: int = 5):
    """
    Train gradient boosting classifier for regime prediction.

    Uses time-series cross-validation to prevent look-ahead bias.
    """
    tscv = TimeSeriesSplit(n_splits=n_splits)

    models = []
    scores = []

    for train_idx, val_idx in tscv.split(features):
        X_train = features.iloc[train_idx]
        y_train = regime_labels.iloc[train_idx]
        X_val = features.iloc[val_idx]
        y_val = regime_labels.iloc[val_idx]

        model = lgb.LGBMClassifier(
            n_estimators=100,
            learning_rate=0.05,
            max_depth=5,
            random_state=42
        )
        model.fit(X_train, y_train)

        score = model.score(X_val, y_val)
        models.append(model)
        scores.append(score)

    return {
        "models": models,
        "cv_scores": scores,
        "feature_importance": pd.Series(
            models[-1].feature_importances_,
            index=features.columns
        ).sort_values(ascending=False)
    }
```

---

## PART 4: ALLOCATION FRAMEWORK

### 4.1 Regime-Based Allocation Matrix

```python
# Base allocation by regime (equity allocation shown, rest to bonds/cash)

REGIME_ALLOCATIONS = {
    # Economic Regime (MRI-based)
    "expansion": {
        "equities": 0.70,
        "fixed_income": 0.25,
        "commodities": 0.05,
        "cash": 0.00
    },
    "late_cycle": {
        "equities": 0.50,
        "fixed_income": 0.35,
        "commodities": 0.05,
        "cash": 0.10
    },
    "slowdown": {
        "equities": 0.40,
        "fixed_income": 0.40,
        "commodities": 0.05,
        "cash": 0.15
    },
    "recession": {
        "equities": 0.30,
        "fixed_income": 0.45,
        "commodities": 0.00,
        "cash": 0.25
    },
    "recovery": {
        "equities": 0.65,
        "fixed_income": 0.25,
        "commodities": 0.10,
        "cash": 0.00
    }
}

# Market regime overlay (adjusts base allocation)
MARKET_OVERLAY = {
    "risk_on": {"equities": +0.05, "cash": -0.05},
    "neutral": {"equities": 0.00, "cash": 0.00},
    "risk_off": {"equities": -0.10, "cash": +0.10},
    "capitulation": {"equities": +0.10, "cash": -0.10}  # Contrarian
}
```

### 4.2 Sub-Asset Allocation Rules

```python
# Within equities: style/size tilts based on regime

EQUITY_TILTS = {
    "expansion": {
        "growth_vs_value": 0.60,      # Tilt growth
        "large_vs_small": 0.50,       # Neutral
        "us_vs_intl": 0.65            # US bias
    },
    "late_cycle": {
        "growth_vs_value": 0.40,      # Tilt value (quality)
        "large_vs_small": 0.60,       # Tilt large
        "us_vs_intl": 0.70            # Stronger US bias
    },
    "recession": {
        "growth_vs_value": 0.35,      # Deep value
        "large_vs_small": 0.70,       # Defensive large
        "us_vs_intl": 0.75            # Home bias
    },
    "recovery": {
        "growth_vs_value": 0.55,      # Slight growth
        "large_vs_small": 0.35,       # Small cap outperformance
        "us_vs_intl": 0.55            # Broaden international
    }
}

# Within fixed income: duration/credit based on regime
FIXED_INCOME_TILTS = {
    "expansion": {
        "duration": "short",          # Rising rate risk
        "credit": "high_yield"        # Spread compression
    },
    "late_cycle": {
        "duration": "intermediate",
        "credit": "investment_grade"  # Quality up
    },
    "recession": {
        "duration": "long",           # Flight to quality
        "credit": "treasuries"        # No credit risk
    },
    "recovery": {
        "duration": "short",
        "credit": "high_yield"        # Spread tightening
    }
}
```

### 4.3 Sector Allocation (Pillar-Driven)

```python
# Map pillars to sector tilts

PILLAR_SECTOR_MAP = {
    # Pillar → (overweight sectors, underweight sectors)
    "LPI_strong": {
        "overweight": ["XLY", "XLI"],      # Consumer disc, industrials
        "underweight": ["XLU", "XLP"]       # Utilities, staples
    },
    "LPI_weak": {
        "overweight": ["XLU", "XLP", "XLV"],  # Defensive
        "underweight": ["XLY", "XLI"]
    },
    "HCI_strong": {
        "overweight": ["XHB", "ITB", "XLF"],  # Homebuilders, financials
        "underweight": []
    },
    "HCI_weak": {
        "overweight": [],
        "underweight": ["XHB", "ITB"]
    },
    "LCI_abundant": {
        "overweight": ["XLF", "IWM"],        # Financials, small caps
        "underweight": []
    },
    "LCI_scarce": {
        "overweight": ["XLU", "XLP"],        # Defensive + quality
        "underweight": ["XLF", "IWM"]        # Funding-sensitive
    },
    "PCI_elevated": {
        "overweight": ["XLE", "XLB", "GLD"], # Commodities, materials
        "underweight": ["XLU", "TLT"]        # Rate-sensitive
    }
}
```

---

## PART 5: IMPLEMENTATION ROADMAP

### Phase 1: Indicator Validation (Weeks 1-3)

**Goal:** Confirm existing indicators have predictive power

1. **Lead-Lag Analysis**
   - Run Granger causality tests for all pillar components
   - Identify optimal lags for each leading indicator
   - Document which relationships are robust

2. **Composite Weight Validation**
   - Use PCA to check for redundancy in components
   - Run elastic net to find sparse optimal weights
   - Compare current weights vs. data-driven weights

3. **Threshold Calibration**
   - Use HMM to identify natural regime clusters
   - Compare to current threshold levels
   - Adjust thresholds based on historical regime performance

**Deliverable:** Indicator Validation Report with recommendations

### Phase 2: Regime Model Development (Weeks 4-6)

**Goal:** Build robust regime identification system

1. **Economic Regime Model**
   - Train HMM on MRI and pillar composites
   - Label regimes (expansion, late-cycle, recession, recovery)
   - Validate against NBER dates + market events

2. **Market Regime Model**
   - Build MSI/SPI-based state machine
   - Define transition rules (e.g., SSD thresholds)
   - Validate with drawdown/rally analysis

3. **Combined Regime Matrix**
   - Map Economic × Market regime combinations
   - Identify historical occurrences of each combination
   - Calculate return profiles for each state

**Deliverable:** Regime Model with backtested transition detection

### Phase 3: Allocation Strategy Backtesting (Weeks 7-10)

**Goal:** Validate allocation rules produce alpha

1. **Strategic Allocation**
   - Backtest regime-based asset allocation
   - Walk-forward validation with publication lags
   - Compare to 60/40, risk parity benchmarks

2. **Tactical Overlay**
   - Test MSI/SPI timing signals
   - Measure value-add of market structure overlay
   - Quantify protection during drawdowns

3. **Sector Rotation**
   - Backtest pillar-driven sector tilts
   - Measure relative performance in each regime
   - Identify which pillar-sector links are profitable

**Deliverable:** Strategy Performance Report with risk metrics

### Phase 4: Production System (Weeks 11-12)

**Goal:** Operationalize the validated system

1. **Signal Generation Pipeline**
   - Daily regime classification
   - Allocation recommendations
   - Risk alerts

2. **Monitoring Dashboard**
   - Current regime status
   - Allocation drift tracking
   - Signal strength indicators

3. **Tiered Output System**
   - Basic tier: Regime + broad allocation
   - Active tier: Specific trade ideas
   - Institutional tier: Full model access + customization

**Deliverable:** Production-ready system with documentation

---

## PART 6: DATA REQUIREMENTS

### Currently Available
- FRED macro series (labor, prices, credit, housing, etc.)
- Market prices (SPY, IWM, QQQ, TLT, GLD, etc.)
- Volatility indices (VIX, VVIX, MOVE proxy)
- Fed balance sheet data

### Needed for Full Implementation

| Data | Source | Purpose | Priority |
|------|--------|---------|----------|
| **Sector ETF prices** | Yahoo Finance | Sector allocation backtest | High |
| **Factor returns** | Kenneth French / AQR | Style tilt validation | High |
| **NBER recession dates** | FRED | Regime validation | High |
| **International ETFs** | Yahoo Finance | Geographic allocation | Medium |
| **Breadth data** | Yahoo Finance / custom | MSI components | High |
| **Sentiment data** | AAII, II, NAAIM | SPI components | High |
| **Options data** | CBOE | Put/call ratios | Medium |

---

## PART 7: KEY METRICS TO TRACK

### Strategy Performance
- **CAGR**: Compound annual growth rate
- **Sharpe Ratio**: Risk-adjusted return (target > 0.8)
- **Sortino Ratio**: Downside-adjusted return (target > 1.0)
- **Max Drawdown**: Largest peak-to-trough (target < 20%)
- **Calmar Ratio**: CAGR / Max DD (target > 0.5)

### Regime Detection
- **True Positive Rate**: % of recessions detected
- **Average Lead Time**: How early signal fires
- **False Positive Rate**: False recession calls
- **Regime Persistence**: Average regime duration

### Indicator Quality
- **Information Coefficient**: Correlation of signal with forward returns
- **Hit Rate**: % of correct directional calls
- **Signal Decay**: How quickly signal loses predictive power

---

## APPENDIX A: ASSET UNIVERSE

### Core ETFs for Backtesting

**Equities:**
- SPY (S&P 500)
- IWM (Russell 2000)
- QQQ (Nasdaq 100)
- IWF (Russell 1000 Growth)
- IWD (Russell 1000 Value)
- EFA (EAFE)
- EEM (Emerging Markets)

**Fixed Income:**
- TLT (20+ Year Treasury)
- IEF (7-10 Year Treasury)
- SHY (1-3 Year Treasury)
- LQD (Investment Grade Corp)
- HYG (High Yield Corp)
- EMLC (EM Local Currency)

**Commodities:**
- GLD (Gold)
- DBC (Broad Commodities)
- USO (Oil)

**Sectors:**
- XLF (Financials)
- XLE (Energy)
- XLK (Technology)
- XLV (Healthcare)
- XLI (Industrials)
- XLY (Consumer Discretionary)
- XLP (Consumer Staples)
- XLU (Utilities)
- XLB (Materials)
- XLRE (Real Estate)
- XHB (Homebuilders)

---

## APPENDIX B: CODE STRUCTURE RECOMMENDATION

```
/Users/bob/LHM/
├── lighthouse_quant/                    # New package for modeling
│   ├── __init__.py
│   ├── config.py                        # Paths, parameters
│   │
│   ├── data/
│   │   ├── loaders.py                   # Load from DB/parquet
│   │   ├── publication_lags.py          # Lag registry
│   │   └── universe.py                  # ETF definitions
│   │
│   ├── indicators/
│   │   ├── composites.py                # LFI, LCI, MRI, etc.
│   │   ├── market_structure.py          # MSI, SBD
│   │   ├── sentiment.py                 # SPI, SSD
│   │   └── validation.py                # Lead-lag tests
│   │
│   ├── regimes/
│   │   ├── economic.py                  # MRI-based regimes
│   │   ├── market.py                    # MSI/SPI-based regimes
│   │   ├── hmm.py                       # Hidden Markov models
│   │   └── combined.py                  # Regime matrix
│   │
│   ├── allocation/
│   │   ├── strategic.py                 # Regime-based allocation
│   │   ├── tactical.py                  # Timing overlay
│   │   ├── sector.py                    # Sector rotation
│   │   └── optimization.py              # Mean-variance, risk parity
│   │
│   ├── backtesting/
│   │   ├── engine.py                    # Walk-forward framework
│   │   ├── metrics.py                   # Performance metrics
│   │   ├── attribution.py               # Return attribution
│   │   └── reports.py                   # Generate reports
│   │
│   └── ml/
│       ├── weight_optimization.py       # Lasso, RF importance
│       ├── regime_classification.py     # LightGBM, XGBoost
│       └── forecasting.py               # VAR, Prophet, etc.
│
├── notebooks/
│   ├── 01_indicator_validation.ipynb
│   ├── 02_regime_analysis.ipynb
│   ├── 03_backtest_results.ipynb
│   └── 04_production_dashboard.ipynb
│
└── tests/
    ├── test_indicators.py
    ├── test_regimes.py
    └── test_backtesting.py
```

---

**Version:** 1.0
**Author:** Bob Sheehan, CFA, CMT
**Date:** 2026-01-19

*"MACRO, ILLUMINATED."*
