"""
Lighthouse Macro Warning System
===============================
A threshold-based early warning system that captures discontinuity risk
and buffer exhaustion that probability models miss.

Philosophy:
    The Hollow Rally doesn't end because sentiment turns.
    It ends when the system loses capacity to absorb stress.
    This system monitors that capacity.

Architecture:
    - Individual threshold flags (binary warnings)
    - Category aggregation (Liquidity, Labor, Credit, Structure)
    - Overall warning level (GREEN/YELLOW/AMBER/RED)
    - Override logic (certain conditions force escalation)

Key Insight from Horizon Jan 2026:
    "Liquidity still exists. But it no longer absorbs risk. It transmits it."
"""

import pandas as pd
import numpy as np
import sqlite3
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum

import sys
sys.path.insert(0, "/Users/bob/LHM")
from lighthouse_quant.config import DB_PATH


class WarningLevel(Enum):
    """System-wide warning levels."""
    GREEN = 1   # Normal operations, buffers intact
    YELLOW = 2  # Elevated monitoring, some buffers depleted
    AMBER = 3   # High alert, multiple stress signals
    RED = 4     # Crisis conditions, discontinuity risk elevated


@dataclass
class ReserveManagementAssessment:
    """Assessment of Fed reserve management operations."""
    reserves_current: float          # Current reserve level ($B)
    reserves_lclor: float            # LCLOR estimate ($B)
    reserves_buffer: float           # Buffer above LCLOR ($B)
    drain_rate_monthly: float        # Monthly drain rate ($B/month)
    months_to_lclor: float           # Months until LCLOR at current pace
    fed_intervention_active: bool    # Is Fed actively managing?
    fed_balance_sheet_change: float  # Recent Fed BS change (weekly)
    rmp_estimated_pace: float        # Estimated RMP pace ($B/month)
    net_drain_rate: float            # Drain rate after RMP offset
    assessment: str                  # Summary assessment
    risk_modifier: float             # Adjustment to discontinuity premium (-0.1 to +0.1)


@dataclass
class ThresholdFlag:
    """Individual warning flag."""
    name: str
    category: str
    current_value: float
    threshold: float
    direction: str  # "above" or "below"
    triggered: bool
    severity: str   # "warning", "critical", "override"
    description: str

    def __str__(self):
        status = "🔴 TRIGGERED" if self.triggered else "🟢 OK"
        return f"{self.name}: {self.current_value:.2f} (threshold: {self.direction} {self.threshold}) - {status}"


@dataclass
class CategoryAssessment:
    """Assessment for a category of indicators."""
    name: str
    flags: List[ThresholdFlag]
    warning_count: int
    critical_count: int
    override_triggered: bool
    level: WarningLevel
    summary: str


@dataclass
class SystemWarning:
    """Complete system warning assessment."""
    date: str
    overall_level: WarningLevel
    categories: Dict[str, CategoryAssessment]
    triggered_flags: List[ThresholdFlag]
    override_active: bool
    override_reason: str
    narrative: str
    action_items: List[str]
    rmp_assessment: Optional[ReserveManagementAssessment] = None


# ==========================================
# THRESHOLD DEFINITIONS
# ==========================================

THRESHOLDS = {
    # ==========================================
    # LIQUIDITY (Buffer Exhaustion)
    # Data units: RRP in billions, Reserves in billions
    # ==========================================
    "liquidity": {
        # RRP Exhaustion - THE critical buffer (data in billions)
        "RRP_DEPLETED": {
            "series": "RRP_Usage",
            "threshold": 100,  # $100B (stored as 100)
            "direction": "below",
            "severity": "override",  # Forces AMBER minimum
            "description": "ON RRP below $100B - primary shock absorber exhausted"
        },
        "RRP_CRITICAL": {
            "series": "RRP_Usage",
            "threshold": 250,  # $250B (stored as 250)
            "direction": "below",
            "severity": "critical",
            "description": "ON RRP below $250B - buffer severely depleted"
        },

        # Bank Reserves vs LCLOR (data in billions)
        "RESERVES_AT_LCLOR": {
            "series": "Bank_Reserves",
            "threshold": 2800,  # $2.8T = 2800B
            "direction": "below",
            "severity": "override",  # Forces AMBER minimum
            "description": "Bank reserves at/below LCLOR - funding stress imminent"
        },
        "RESERVES_BUFFER_THIN": {
            "series": "Bank_Reserves",
            "threshold": 3000,  # $3.0T = 3000B
            "direction": "below",
            "severity": "critical",
            "description": "Bank reserves buffer < $200B above LCLOR"
        },

        # Funding Spreads (data in percentage points, e.g., 0.01 = 1bp)
        "SOFR_EFFR_STRESS": {
            "series": "SOFR_EFFR_Spread",
            "threshold": 0.15,  # 15 bps = 0.15 pct points
            "direction": "above",
            "severity": "critical",
            "description": "SOFR-EFFR spread > 15bps - funding stress emerging"
        },
        "SOFR_EFFR_CRISIS": {
            "series": "SOFR_EFFR_Spread",
            "threshold": 0.25,  # 25 bps = 0.25 pct points
            "direction": "above",
            "severity": "override",
            "description": "SOFR-EFFR spread > 25bps - acute funding stress"
        },

        # LCI Composite
        "LCI_SCARCE": {
            "index": "LCI",
            "threshold": -0.5,
            "direction": "below",
            "severity": "warning",
            "description": "Liquidity Cushion Index in scarce territory"
        },
        "LCI_STRESS": {
            "index": "LCI",
            "threshold": -1.0,
            "direction": "below",
            "severity": "critical",
            "description": "Liquidity Cushion Index at stress levels"
        },
    },

    # ==========================================
    # LABOR (Structural Fragility)
    # ==========================================
    "labor": {
        # Quits Rate - "truth serum"
        "QUITS_PRERECESSION": {
            "series": "JOLTS_Quits_Rate",
            "threshold": 2.0,
            "direction": "below",
            "severity": "critical",
            "description": "Quits rate at/below 2.0% - pre-recessionary territory"
        },
        "QUITS_WARNING": {
            "series": "JOLTS_Quits_Rate",
            "threshold": 2.3,
            "direction": "below",
            "severity": "warning",
            "description": "Quits rate below 2.3% - labor churn slowing"
        },
        "QUITS_NORMALIZING": {
            "series": "JOLTS_Quits_Rate",
            "threshold": 2.1,
            "direction": "below",
            "severity": "warning",
            "description": "Quits rate approaching pre-recessionary levels"
        },

        # LFI Composite
        "LFI_ELEVATED": {
            "index": "LFI",
            "threshold": 0.5,
            "direction": "above",
            "severity": "warning",
            "description": "Labor Fragility Index elevated (>0.5σ)"
        },
        "LFI_HIGH": {
            "index": "LFI",
            "threshold": 1.0,
            "direction": "above",
            "severity": "critical",
            "description": "Labor Fragility Index high (>1.0σ)"
        },
        "LFI_CRITICAL": {
            "index": "LFI",
            "threshold": 1.5,
            "direction": "above",
            "severity": "override",
            "description": "Labor Fragility Index critical (>1.5σ)"
        },

        # Initial Claims
        "CLAIMS_ELEVATED": {
            "series": "Initial_Claims",
            "threshold": 250_000,
            "direction": "above",
            "severity": "warning",
            "description": "Initial claims above 250K"
        },
        "CLAIMS_RECESSION": {
            "series": "Initial_Claims",
            "threshold": 300_000,
            "direction": "above",
            "severity": "critical",
            "description": "Initial claims above 300K - recessionary signal"
        },

        # Employment Diffusion
        "DIFFUSION_NEGATIVE": {
            "series": "Employment_Diffusion",
            "threshold": 50.0,
            "direction": "below",
            "severity": "critical",
            "description": "Employment diffusion below 50% - more industries contracting"
        },
    },

    # ==========================================
    # CREDIT (Mispricing / Complacency)
    # ==========================================
    "credit": {
        # Credit-Labor Gap
        "CLG_MISPRICED": {
            "index": "CLG",
            "threshold": -1.0,
            "direction": "below",
            "severity": "critical",
            "description": "Credit-Labor Gap < -1.0 - spreads ignoring labor fragility"
        },
        "CLG_WARNING": {
            "index": "CLG",
            "threshold": -0.5,
            "direction": "below",
            "severity": "warning",
            "description": "Credit-Labor Gap < -0.5 - spreads tight vs fundamentals"
        },

        # HY Spreads absolute (data in pct points: 2.71 = 271 bps)
        "HY_COMPLACENT": {
            "series": "HY_OAS",
            "threshold": 3.0,  # 300 bps = 3.0 pct
            "direction": "below",
            "severity": "warning",
            "description": "HY OAS below 300bps - credit complacency"
        },
        "HY_EXTREME_COMPLACENT": {
            "series": "HY_OAS",
            "threshold": 2.5,  # 250 bps = 2.5 pct
            "direction": "below",
            "severity": "critical",
            "description": "HY OAS below 250bps - extreme credit complacency"
        },

        # HY Spreads stress (opposite direction)
        "HY_STRESS": {
            "series": "HY_OAS",
            "threshold": 5.0,  # 500 bps = 5.0 pct
            "direction": "above",
            "severity": "warning",
            "description": "HY OAS above 500bps - credit stress emerging"
        },
        "HY_CRISIS": {
            "series": "HY_OAS",
            "threshold": 7.0,  # 700 bps = 7.0 pct
            "direction": "above",
            "severity": "override",
            "description": "HY OAS above 700bps - credit crisis"
        },
    },

    # ==========================================
    # MACRO (GDP-GDI, Fiscal)
    # ==========================================
    "macro": {
        # MRI Composite
        "MRI_LATE_CYCLE": {
            "index": "MRI",
            "threshold": 0.10,
            "direction": "above",
            "severity": "warning",
            "description": "MRI in late cycle territory"
        },
        "MRI_PRERECESSION": {
            "index": "MRI",
            "threshold": 0.25,
            "direction": "above",
            "severity": "critical",
            "description": "MRI in pre-recession territory"
        },
        "MRI_RECESSION": {
            "index": "MRI",
            "threshold": 0.50,
            "direction": "above",
            "severity": "override",
            "description": "MRI in recession territory"
        },

        # Yield Curve
        "CURVE_INVERTED": {
            "series": "Curve_10Y_3M",
            "threshold": 0,
            "direction": "below",
            "severity": "warning",
            "description": "Yield curve inverted (10Y-3M < 0)"
        },
        "CURVE_DEEPLY_INVERTED": {
            "series": "Curve_10Y_3M",
            "threshold": -0.5,
            "direction": "below",
            "severity": "critical",
            "description": "Yield curve deeply inverted (10Y-3M < -50bps)"
        },
    },

    # ==========================================
    # MARKET STRUCTURE (Pillar 11)
    # ==========================================
    "structure": {
        # MSI
        "MSI_WEAK": {
            "index": "MSI",
            "threshold": -0.5,
            "direction": "below",
            "severity": "warning",
            "description": "Market Structure Index weak"
        },
        "MSI_BEARISH": {
            "index": "MSI",
            "threshold": -1.0,
            "direction": "below",
            "severity": "critical",
            "description": "Market Structure Index bearish"
        },

        # SBD - Structure Breadth Divergence
        "SBD_DISTRIBUTION": {
            "index": "SBD",
            "threshold": 1.0,
            "direction": "above",
            "severity": "warning",
            "description": "Structure-Breadth Divergence showing distribution (generals without soldiers)"
        },
        "SBD_EXTREME": {
            "index": "SBD",
            "threshold": 1.5,
            "direction": "above",
            "severity": "critical",
            "description": "Extreme Structure-Breadth Divergence - major distribution"
        },
    },

    # ==========================================
    # SENTIMENT (Pillar 12) - Contrarian
    # ==========================================
    "sentiment": {
        # SPI - high = fear = bullish, low = euphoria = bearish
        "SPI_EUPHORIA": {
            "index": "SPI",
            "threshold": -1.0,
            "direction": "below",
            "severity": "warning",
            "description": "Sentiment showing euphoria - contrarian bearish"
        },
        "SPI_EXTREME_EUPHORIA": {
            "index": "SPI",
            "threshold": -1.5,
            "direction": "below",
            "severity": "critical",
            "description": "Extreme euphoria - contrarian very bearish"
        },

        # VIX
        "VIX_COMPLACENT": {
            "series": "VIX",
            "threshold": 15,
            "direction": "below",
            "severity": "warning",
            "description": "VIX below 15 - volatility complacency"
        },
        "VIX_EXTREME_COMPLACENT": {
            "series": "VIX",
            "threshold": 12,
            "direction": "below",
            "severity": "critical",
            "description": "VIX below 12 - extreme volatility complacency"
        },
    },
}


# ==========================================
# OVERRIDE RULES
# ==========================================

OVERRIDE_RULES = [
    # Any single override-severity flag forces minimum AMBER
    {
        "name": "Single Override",
        "condition": lambda flags: any(f.severity == "override" and f.triggered for f in flags),
        "min_level": WarningLevel.AMBER,
        "description": "Critical threshold breached"
    },

    # Multiple critical flags in same category forces AMBER
    {
        "name": "Category Critical Mass",
        "condition": lambda flags: max_critical_per_category(flags) >= 2,
        "min_level": WarningLevel.AMBER,
        "description": "Multiple critical warnings in same category"
    },

    # Critical flags across 3+ categories forces AMBER
    {
        "name": "Broad Critical Spread",
        "condition": lambda flags: count_categories_with_critical(flags) >= 3,
        "min_level": WarningLevel.AMBER,
        "description": "Critical warnings across multiple categories"
    },

    # Liquidity + Labor both critical forces RED
    {
        "name": "Liquidity-Labor Convergence",
        "condition": lambda flags: (
            has_critical_in_category(flags, "liquidity") and
            has_critical_in_category(flags, "labor")
        ),
        "min_level": WarningLevel.RED,
        "description": "Both liquidity and labor showing critical stress"
    },

    # RRP depleted + any other override forces RED
    {
        "name": "Buffer Gone + Stress",
        "condition": lambda flags: (
            any(f.name == "RRP_DEPLETED" and f.triggered for f in flags) and
            sum(1 for f in flags if f.severity == "override" and f.triggered) >= 2
        ),
        "min_level": WarningLevel.RED,
        "description": "RRP exhausted with additional override conditions"
    },
]


def max_critical_per_category(flags: List[ThresholdFlag]) -> int:
    """Get max critical count in any single category."""
    from collections import Counter
    critical_by_cat = Counter(f.category for f in flags if f.severity == "critical" and f.triggered)
    return max(critical_by_cat.values()) if critical_by_cat else 0


def count_categories_with_critical(flags: List[ThresholdFlag]) -> int:
    """Count categories that have at least one critical flag triggered."""
    categories = set(f.category for f in flags if f.severity == "critical" and f.triggered)
    return len(categories)


def has_critical_in_category(flags: List[ThresholdFlag], category: str) -> bool:
    """Check if category has any critical flag triggered."""
    return any(f.category == category and f.severity == "critical" and f.triggered for f in flags)


# ==========================================
# WARNING SYSTEM CLASS
# ==========================================

class WarningSystem:
    """
    Lighthouse Macro Early Warning System.

    Monitors threshold conditions across liquidity, labor, credit,
    macro, structure, and sentiment to identify discontinuity risk.
    """

    def __init__(self, conn: sqlite3.Connection = None):
        self.conn = conn or sqlite3.connect(DB_PATH)
        self._data_cache = {}

    def _get_series_value(self, series_name: str, date: str = None) -> Optional[float]:
        """Get the value for a series from horizon_dataset, as-of `date`.

        date=None -> latest available (unchanged live behavior). When a date is
        given, returns the most recent observation on or before that date.
        """
        cache_key = f"series_{series_name}_{date or 'latest'}"

        if cache_key not in self._data_cache:
            try:
                asof = f" AND date <= '{date}'" if date else ""
                query = (f"SELECT date, {series_name} FROM horizon_dataset "
                         f"WHERE {series_name} IS NOT NULL{asof} "
                         f"ORDER BY date DESC LIMIT 1")
                result = pd.read_sql(query, self.conn)
                if not result.empty:
                    self._data_cache[cache_key] = float(result.iloc[0][series_name])
                else:
                    self._data_cache[cache_key] = None
            except Exception as e:
                self._data_cache[cache_key] = None

        return self._data_cache.get(cache_key)

    def _get_index_value(self, index_name: str, date: str = None) -> Optional[float]:
        """Get latest value for an index from lighthouse_indices."""
        cache_key = f"index_{index_name}_{date or 'latest'}"

        if cache_key not in self._data_cache:
            try:
                asof = f" AND date <= '{date}'" if date else ""
                query = (f"SELECT date, value FROM lighthouse_indices "
                         f"WHERE index_id = '{index_name}'{asof} "
                         f"ORDER BY date DESC LIMIT 1")
                result = pd.read_sql(query, self.conn)
                if not result.empty:
                    self._data_cache[cache_key] = float(result.iloc[0]['value'])
                else:
                    self._data_cache[cache_key] = None
            except Exception as e:
                self._data_cache[cache_key] = None

        return self._data_cache.get(cache_key)

    def _assess_reserve_management(self, date: str = None) -> ReserveManagementAssessment:
        """
        Assess Fed reserve management operations (RMP).

        Analyzes:
        - Current reserve levels vs LCLOR
        - Rate of reserve drain
        - Fed balance sheet changes (proxy for RMP)
        - Estimated runway to stress
        """
        LCLOR = 2800  # $2.8T estimate in billions

        # Get current reserves
        asof = f" AND date <= '{date}'" if date else ""
        reserves_current = self._get_series_value("Bank_Reserves", date)
        if reserves_current is None:
            reserves_current = 2879  # Fallback to recent known value

        reserves_buffer = reserves_current - LCLOR

        # Get reserve history to calculate drain rate (last 30 days)
        try:
            reserve_history = pd.read_sql(
                "SELECT date, Bank_Reserves FROM horizon_dataset "
                f"WHERE Bank_Reserves IS NOT NULL{asof} "
                "ORDER BY date DESC LIMIT 30", self.conn)

            if len(reserve_history) >= 2:
                # Calculate monthly drain rate from recent data
                oldest = reserve_history.iloc[-1]['Bank_Reserves']
                newest = reserve_history.iloc[0]['Bank_Reserves']
                days = (pd.to_datetime(reserve_history.iloc[0]['date']) -
                       pd.to_datetime(reserve_history.iloc[-1]['date'])).days
                if days > 0:
                    daily_drain = (oldest - newest) / days
                    drain_rate_monthly = daily_drain * 30
                else:
                    drain_rate_monthly = 0
            else:
                drain_rate_monthly = 65  # Fallback estimate ~$65B/month QT pace
        except Exception:
            drain_rate_monthly = 65

        # Get Fed balance sheet changes (proxy for RMP activity)
        try:
            fed_bs = pd.read_sql(
                "SELECT date, Fed_Balance_Sheet, Fed_Balance_Sheet_wow_diff "
                "FROM horizon_dataset "
                f"WHERE Fed_Balance_Sheet IS NOT NULL{asof} "
                "ORDER BY date DESC LIMIT 8", self.conn)

            if not fed_bs.empty:
                # Average weekly change
                fed_bs_weekly_change = fed_bs['Fed_Balance_Sheet_wow_diff'].mean()
                # Convert to monthly and to billions (data might be in millions)
                fed_bs_monthly = fed_bs_weekly_change * 4 / 1000 if abs(fed_bs_weekly_change) > 100 else fed_bs_weekly_change * 4
            else:
                fed_bs_monthly = 0
        except Exception:
            fed_bs_weekly_change = 0
            fed_bs_monthly = 0

        # Expected QT runoff pace: ~$60B/month (caps: $25B Treasuries + $35B MBS)
        expected_qt_pace = 60

        # If Fed BS is shrinking slower than expected QT, implies RMP activity
        # RMP = Expected QT drain - Actual Fed BS change
        if fed_bs_monthly < 0:  # BS shrinking
            actual_shrink = abs(fed_bs_monthly)
            rmp_estimated = max(0, expected_qt_pace - actual_shrink)
        else:  # BS growing or flat
            rmp_estimated = expected_qt_pace + fed_bs_monthly

        # Net drain rate = gross drain - RMP offset
        # Gross drain includes QT + TGA fluctuations + currency demand
        net_drain_rate = max(0, drain_rate_monthly - rmp_estimated)

        # Months to LCLOR
        if net_drain_rate > 0:
            months_to_lclor = reserves_buffer / net_drain_rate
        else:
            months_to_lclor = float('inf')  # Not draining

        # Is Fed actively intervening?
        fed_intervention_active = rmp_estimated > 20  # >$20B/month suggests active RMP

        # Generate assessment
        if reserves_buffer <= 0:
            assessment = "CRITICAL: Reserves at or below LCLOR. No buffer remaining."
            risk_modifier = 0.10  # Increase risk
        elif months_to_lclor < 2:
            assessment = f"SEVERE: {months_to_lclor:.1f} months to LCLOR at current pace. Fed intervention insufficient."
            risk_modifier = 0.05
        elif months_to_lclor < 6:
            if fed_intervention_active:
                assessment = f"ELEVATED: {months_to_lclor:.1f} months to LCLOR. Fed actively managing (~${rmp_estimated:.0f}B/mo RMP) but losing ground."
                risk_modifier = 0.0  # Neutral - Fed trying but not enough
            else:
                assessment = f"ELEVATED: {months_to_lclor:.1f} months to LCLOR. No significant Fed intervention detected."
                risk_modifier = 0.05
        elif months_to_lclor < 12:
            if fed_intervention_active:
                assessment = f"MONITORED: {months_to_lclor:.1f} months to LCLOR. Fed intervention (~${rmp_estimated:.0f}B/mo) buying time."
                risk_modifier = -0.05  # Slight reduction - Fed has some control
            else:
                assessment = f"MONITORED: {months_to_lclor:.1f} months to LCLOR. Drain pace moderate."
                risk_modifier = 0.0
        else:
            assessment = f"STABLE: {months_to_lclor:.1f}+ months runway. Reserve situation manageable."
            risk_modifier = -0.10  # Reduce risk premium

        return ReserveManagementAssessment(
            reserves_current=reserves_current,
            reserves_lclor=LCLOR,
            reserves_buffer=reserves_buffer,
            drain_rate_monthly=drain_rate_monthly,
            months_to_lclor=months_to_lclor,
            fed_intervention_active=fed_intervention_active,
            fed_balance_sheet_change=fed_bs_weekly_change if 'fed_bs_weekly_change' in dir() else 0,
            rmp_estimated_pace=rmp_estimated,
            net_drain_rate=net_drain_rate,
            assessment=assessment,
            risk_modifier=risk_modifier
        )

    def _evaluate_threshold(self, flag_name: str, config: dict, category: str,
                            date: str = None) -> ThresholdFlag:
        """Evaluate a single threshold flag (as-of `date` when provided)."""
        # Get current value
        if "series" in config:
            current_value = self._get_series_value(config["series"], date)
        elif "index" in config:
            current_value = self._get_index_value(config["index"], date)
        else:
            current_value = None

        if current_value is None:
            return ThresholdFlag(
                name=flag_name,
                category=category,
                current_value=float('nan'),
                threshold=config["threshold"],
                direction=config["direction"],
                triggered=False,
                severity=config["severity"],
                description=config["description"] + " [NO DATA]"
            )

        # Check if triggered
        if config["direction"] == "above":
            triggered = current_value > config["threshold"]
        else:  # below
            triggered = current_value < config["threshold"]

        return ThresholdFlag(
            name=flag_name,
            category=category,
            current_value=current_value,
            threshold=config["threshold"],
            direction=config["direction"],
            triggered=triggered,
            severity=config["severity"],
            description=config["description"]
        )

    def evaluate(self, date: str = None) -> SystemWarning:
        """
        Evaluate all thresholds and generate system warning.

        Args:
            date: Date to evaluate (default: latest available)

        Returns:
            SystemWarning with complete assessment
        """
        self._data_cache = {}  # Clear cache for fresh evaluation

        # Evaluate all flags
        all_flags = []
        category_flags = {}

        for category, flags in THRESHOLDS.items():
            category_flags[category] = []
            for flag_name, config in flags.items():
                flag = self._evaluate_threshold(flag_name, config, category, date)
                all_flags.append(flag)
                category_flags[category].append(flag)

        # Assess each category
        categories = {}
        for category, flags in category_flags.items():
            triggered = [f for f in flags if f.triggered]
            warning_count = sum(1 for f in triggered if f.severity == "warning")
            critical_count = sum(1 for f in triggered if f.severity == "critical")
            override_count = sum(1 for f in triggered if f.severity == "override")

            # Determine category level
            if override_count > 0:
                level = WarningLevel.RED
            elif critical_count >= 2:
                level = WarningLevel.AMBER
            elif critical_count >= 1:
                level = WarningLevel.YELLOW
            elif warning_count >= 2:
                level = WarningLevel.YELLOW
            else:
                level = WarningLevel.GREEN

            categories[category] = CategoryAssessment(
                name=category,
                flags=flags,
                warning_count=warning_count,
                critical_count=critical_count,
                override_triggered=override_count > 0,
                level=level,
                summary=self._category_summary(category, flags)
            )

        # Determine overall level
        triggered_flags = [f for f in all_flags if f.triggered]

        # Start with category-based level
        max_category_level = max(categories.values(), key=lambda x: x.level.value).level
        overall_level = max_category_level

        # Apply override rules
        override_active = False
        override_reason = ""

        for rule in OVERRIDE_RULES:
            if rule["condition"](all_flags):
                if rule["min_level"].value > overall_level.value:
                    overall_level = rule["min_level"]
                    override_active = True
                    override_reason = rule["description"]

        # Assess Reserve Management Operations
        rmp_assessment = self._assess_reserve_management(date)

        # Generate narrative and action items
        narrative = self._generate_narrative(overall_level, categories, triggered_flags)
        action_items = self._generate_actions(overall_level, categories, triggered_flags)

        # Add RMP context to action items if relevant
        if rmp_assessment.fed_intervention_active:
            action_items.append(f"Note: Fed RMP active (~${rmp_assessment.rmp_estimated_pace:.0f}B/mo). {rmp_assessment.assessment}")

        return SystemWarning(
            date=date or datetime.now().strftime("%Y-%m-%d"),
            overall_level=overall_level,
            categories=categories,
            triggered_flags=triggered_flags,
            override_active=override_active,
            override_reason=override_reason,
            narrative=narrative,
            action_items=action_items,
            rmp_assessment=rmp_assessment
        )

    def _category_summary(self, category: str, flags: List[ThresholdFlag]) -> str:
        """Generate summary for a category."""
        triggered = [f for f in flags if f.triggered]
        if not triggered:
            return f"{category.title()}: All clear"

        critical = [f for f in triggered if f.severity in ("critical", "override")]
        if critical:
            return f"{category.title()}: {len(critical)} critical, {len(triggered)-len(critical)} warning"
        return f"{category.title()}: {len(triggered)} warnings"

    def _generate_narrative(self, level: WarningLevel, categories: Dict, flags: List[ThresholdFlag]) -> str:
        """Generate human-readable narrative."""
        if level == WarningLevel.GREEN:
            return "System operating normally. Buffers intact. No discontinuity risk elevated."

        if level == WarningLevel.YELLOW:
            stressed_cats = [c for c, a in categories.items() if a.level.value >= WarningLevel.YELLOW.value]
            return f"Elevated monitoring warranted. Stress signals in: {', '.join(stressed_cats)}. Buffers partially depleted but functional."

        if level == WarningLevel.AMBER:
            critical_flags = [f for f in flags if f.triggered and f.severity in ("critical", "override")]
            flag_names = [f.name for f in critical_flags[:3]]
            return f"High alert. Multiple stress signals converging. Key triggers: {', '.join(flag_names)}. System capacity to absorb stress materially diminished."

        if level == WarningLevel.RED:
            return "Crisis conditions. Discontinuity risk elevated. System operating without margin for error. The rally does not end because sentiment turns. It ends when the system loses capacity to absorb stress. That capacity is now critically impaired."

        return "Unknown state"

    def _generate_actions(self, level: WarningLevel, categories: Dict, flags: List[ThresholdFlag]) -> List[str]:
        """Generate action items based on warning level."""
        actions = []

        if level == WarningLevel.GREEN:
            actions.append("Maintain current positioning")
            actions.append("Continue regular monitoring cadence")

        elif level == WarningLevel.YELLOW:
            actions.append("Increase monitoring frequency")
            actions.append("Review tail hedges")
            actions.append("Identify rebalancing triggers")

        elif level == WarningLevel.AMBER:
            actions.append("Position defensively")
            actions.append("Maintain elevated cash/liquidity")
            actions.append("Implement tail hedges if not already in place")
            actions.append("Accept underperformance vs momentum-driven indices")
            actions.append("Prepare for rebalancing opportunities")

        elif level == WarningLevel.RED:
            actions.append("Maximum defensive positioning")
            actions.append("Prioritize capital preservation")
            actions.append("Ensure liquidity for stress scenarios")
            actions.append("Monitor for capitulation signals for tactical re-entry")

        # Add category-specific actions
        if categories.get("liquidity", CategoryAssessment("", [], 0, 0, False, WarningLevel.GREEN, "")).level.value >= WarningLevel.AMBER.value:
            actions.append("Monitor funding markets daily (SOFR-EFFR, repo rates)")

        if categories.get("labor", CategoryAssessment("", [], 0, 0, False, WarningLevel.GREEN, "")).level.value >= WarningLevel.YELLOW.value:
            actions.append("Track weekly claims releases for acceleration")

        if categories.get("credit", CategoryAssessment("", [], 0, 0, False, WarningLevel.GREEN, "")).level.value >= WarningLevel.YELLOW.value:
            actions.append("Watch for credit spread regime change")

        return actions

    def print_report(self, warning: SystemWarning = None):
        """Print formatted warning report."""
        if warning is None:
            warning = self.evaluate()

        level_colors = {
            WarningLevel.GREEN: "🟢",
            WarningLevel.YELLOW: "🟡",
            WarningLevel.AMBER: "🟠",
            WarningLevel.RED: "🔴"
        }

        print("\n" + "=" * 70)
        print("LIGHTHOUSE MACRO WARNING SYSTEM")
        print(f"Date: {warning.date}")
        print("=" * 70)

        print(f"\n{level_colors[warning.overall_level]} OVERALL STATUS: {warning.overall_level.name}")

        if warning.override_active:
            print(f"   ⚠️  OVERRIDE ACTIVE: {warning.override_reason}")

        print(f"\n{warning.narrative}")

        print("\n" + "-" * 70)
        print("CATEGORY BREAKDOWN")
        print("-" * 70)

        for cat_name, assessment in warning.categories.items():
            icon = level_colors[assessment.level]
            print(f"\n{icon} {cat_name.upper()}: {assessment.level.name}")

            triggered = [f for f in assessment.flags if f.triggered]
            if triggered:
                for flag in triggered:
                    sev_icon = "🔴" if flag.severity == "override" else ("🟠" if flag.severity == "critical" else "🟡")
                    print(f"   {sev_icon} {flag.name}: {flag.current_value:.4f} ({flag.direction} {flag.threshold})")
                    print(f"      └─ {flag.description}")
            else:
                print("   ✓ All thresholds clear")

        # RMP Assessment
        if warning.rmp_assessment:
            rmp = warning.rmp_assessment
            print("\n" + "-" * 70)
            print("RESERVE MANAGEMENT ASSESSMENT")
            print("-" * 70)
            print(f"   Reserves Current:    ${rmp.reserves_current:,.0f}B")
            print(f"   LCLOR Estimate:      ${rmp.reserves_lclor:,.0f}B")
            print(f"   Buffer Remaining:    ${rmp.reserves_buffer:,.0f}B")
            print(f"   Drain Rate (gross):  ${rmp.drain_rate_monthly:,.0f}B/month")
            print(f"   RMP Pace (est):      ${rmp.rmp_estimated_pace:,.0f}B/month")
            print(f"   Net Drain Rate:      ${rmp.net_drain_rate:,.0f}B/month")
            if rmp.months_to_lclor < 100:
                print(f"   Months to LCLOR:     {rmp.months_to_lclor:.1f}")
            else:
                print(f"   Months to LCLOR:     >100 (stable)")
            print(f"   Fed Intervention:    {'ACTIVE' if rmp.fed_intervention_active else 'MINIMAL'}")
            print(f"\n   Assessment: {rmp.assessment}")
            print(f"   Risk Modifier: {rmp.risk_modifier:+.0%}")

        print("\n" + "-" * 70)
        print("ACTION ITEMS")
        print("-" * 70)
        for i, action in enumerate(warning.action_items, 1):
            print(f"  {i}. {action}")

        print("\n" + "=" * 70)

        return warning


def compute_warning_level(conn: sqlite3.Connection = None) -> pd.Series:
    """
    Compute warning level for historical dates.

    Returns Series with warning level (1-4) indexed by date.
    """
    system = WarningSystem(conn)
    warning = system.evaluate()

    # For now, just return latest value
    # Full historical computation would require iterating through dates
    return pd.Series(
        [warning.overall_level.value],
        index=[pd.Timestamp(warning.date)],
        name="WARNING_LEVEL"
    )


# CLI interface
if __name__ == "__main__":
    conn = sqlite3.connect(DB_PATH)
    system = WarningSystem(conn)
    system.print_report()
    conn.close()
