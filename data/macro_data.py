"""
macro_data.py
--------------
Centralized data-access layer for US macroeconomic indicators.

Design goals:
- Single responsibility: fetch + transform macro data
- UI-agnostic (Tkinter, PyQt, web, etc.)
- Graceful failure (returns None or NaN, not crashes)
- Easy to extend with new series

Primary source: FRED (St. Louis Fed)
Secondary sources (future): BEA, BLS
"""

from datetime import datetime
from typing import Optional, Dict

import pandas as pd

try:
    from fredapi import Fred
except ImportError:
    Fred = None

import os

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

FRED_API_KEY = os.getenv("FRED_API_KEY")

if Fred and FRED_API_KEY:
    fred = Fred(api_key=FRED_API_KEY)
else:
    fred = None
    if Fred:
        print("Warning: FRED_API_KEY not set. API calls will not work.")

# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------


def _safe_latest(series_id: str) -> Optional[float]:
    """Safely fetch the latest value of a FRED series."""
    if fred is None:
        return None
    try:
        s = fred.get_series(series_id)
        return float(s.dropna().iloc[-1])
    except Exception:
        return None


def _safe_yoy(series_id: str) -> Optional[float]:
    """Year-over-year percent change for a monthly series."""
    if fred is None:
        return None
    try:
        s = fred.get_series(series_id).dropna()
        if len(s) < 13:
            return None
        return float((s.iloc[-1] / s.iloc[-13] - 1) * 100)
    except Exception:
        return None


def _safe_qoq_annualized(series_id: str) -> Optional[float]:
    """Quarter-over-quarter annualized growth rate."""
    if fred is None:
        return None
    try:
        s = fred.get_series(series_id).dropna()
        if len(s) < 2:
            return None
        qoq = (s.iloc[-1] / s.iloc[-2] - 1)
        return float((1 + qoq) ** 4 - 1) * 100
    except Exception:
        return None

# ---------------------------------------------------------------------------
# Core macro indicators
# ---------------------------------------------------------------------------


def real_gdp_growth() -> Optional[float]:
    """Real GDP QoQ annualized (%)."""
    return _safe_qoq_annualized("GDPC1")


def nominal_gdp_growth() -> Optional[float]:
    """Nominal GDP QoQ annualized (%)."""
    return _safe_qoq_annualized("GDP")


def unemployment_rate() -> Optional[float]:
    """Unemployment rate (%)."""
    return _safe_latest("UNRATE")


def prime_age_employment_ratio() -> Optional[float]:
    """Prime-age (25–54) employment-population ratio (%)."""
    return _safe_latest("LNS12300060")


def payroll_employment_change() -> Optional[float]:
    """Monthly change in nonfarm payrolls (thousands)."""
    if fred is None:
        return None
    try:
        s = fred.get_series("PAYEMS").dropna()
        return float((s.iloc[-1] - s.iloc[-2]) / 1000)
    except Exception:
        return None


def core_pce_yoy() -> Optional[float]:
    """Core PCE inflation YoY (%)."""
    return _safe_yoy("PCEPILFE")


def wage_growth_yoy() -> Optional[float]:
    """Average hourly earnings YoY (%)."""
    return _safe_yoy("CES0500000003")


def yield_curve_3m_10y() -> Optional[float]:
    """3-month minus 10-year Treasury yield (percentage points)."""
    if fred is None:
        return None
    try:
        t10y = fred.get_series("DGS10").dropna().iloc[-1]
        t3m = fred.get_series("DTB3").dropna().iloc[-1]
        return float(t10y - t3m)
    except Exception:
        return None


def credit_spread_high_yield() -> Optional[float]:
    """High-yield corporate bond spread (percentage points)."""
    return _safe_latest("BAMLH0A0HYM2")


def financial_conditions_index() -> Optional[float]:
    """Chicago Fed National Financial Conditions Index."""
    return _safe_latest("NFCI")

# ---------------------------------------------------------------------------
# Aggregated interface (for GUI consumption)
# ---------------------------------------------------------------------------


def get_macro_snapshot() -> Dict[str, Optional[float]]:
    """Return a snapshot dictionary of all core macro indicators."""
    return {
        "Real GDP Growth (%)": real_gdp_growth(),
        "Nominal GDP Growth (%)": nominal_gdp_growth(),
        "Unemployment Rate (%)": unemployment_rate(),
        "Prime-Age E/P Ratio (%)": prime_age_employment_ratio(),
        "Payroll Change (k)": payroll_employment_change(),
        "Core PCE YoY (%)": core_pce_yoy(),
        "Wage Growth YoY (%)": wage_growth_yoy(),
        "Yield Curve 3m–10y": yield_curve_3m_10y(),
        "High-Yield Spread": credit_spread_high_yield(),
        "Financial Conditions Index": financial_conditions_index(),
    }


if __name__ == "__main__":
    snapshot = get_macro_snapshot()
    for k, v in snapshot.items():
        print(f"{k}: {v}")
