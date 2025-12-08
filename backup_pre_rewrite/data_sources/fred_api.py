"""
FRED API Integration Module
============================
Fetches risk-free rates and economic indicators from FRED.

FRED = Federal Reserve Economic Data (St. Louis Fed)
API Docs: https://fred.stlouisfed.org/docs/api/fred/

Key Series:
- DGS10: 10-Year Treasury Constant Maturity Rate (risk-free for DCF)
- DGS5: 5-Year Treasury Rate
- DGS30: 30-Year Treasury Rate
- DTB3: 3-Month T-Bill Rate
- DFF: Federal Funds Rate

Author: ATLAS Financial Intelligence
Created: 2025-12-07 (TASK-E007)
"""

import os
import requests
from datetime import datetime, timedelta
from typing import Optional, Dict, Tuple
import json

# Import centralized logging
try:
    from utils.logging_config import EngineLogger
    _logger = EngineLogger.get_logger("FRED_API")
except ImportError:
    import logging
    _logger = logging.getLogger("FRED_API")


# ==========================================
# CONFIGURATION
# ==========================================

FRED_BASE_URL = "https://api.stlouisfed.org/fred"

# Treasury rate series
TREASURY_SERIES = {
    '10Y': 'DGS10',       # 10-Year Treasury (primary for WACC)
    '5Y': 'DGS5',         # 5-Year Treasury
    '30Y': 'DGS30',       # 30-Year Treasury
    '20Y': 'DGS20',       # 20-Year Treasury
    '1Y': 'DGS1',         # 1-Year Treasury
    '3M': 'DTB3',         # 3-Month T-Bill
    '6M': 'DTB6',         # 6-Month T-Bill
    'fed_funds': 'DFF',   # Federal Funds Rate
}

# Additional economic indicators
ECONOMIC_INDICATORS = {
    'inflation_expectations': 'T5YIE',    # 5-Year Breakeven Inflation
    'gdp_growth': 'A191RL1Q225SBEA',      # Real GDP Growth
    'unemployment': 'UNRATE',              # Unemployment Rate
    'cpi': 'CPIAUCSL',                     # Consumer Price Index
}

# Default risk-free rates (fallback when API unavailable)
DEFAULT_RATES = {
    '10Y': 0.042,  # 4.2%
    '5Y': 0.040,   # 4.0%
    '30Y': 0.044,  # 4.4%
    '3M': 0.045,   # 4.5%
    'fed_funds': 0.0455,  # 4.55%
}

# Cache settings
CACHE_TTL_SECONDS = 3600  # 1 hour (rates don't change during market hours)


class FREDClient:
    """
    Client for FRED API.
    
    Fetches treasury rates for DCF/WACC calculations.
    Includes caching to minimize API calls.
    
    Usage:
        # With API key
        client = FREDClient(api_key="your_key")
        rate = client.get_risk_free_rate()  # 10Y Treasury
        
        # Without API key (uses fallback values)
        client = FREDClient()
        rate = client.get_risk_free_rate()  # Returns default
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize FRED client.
        
        Args:
            api_key: FRED API key. If None, tries FRED_API_KEY env var.
                    If still None, uses fallback values.
        """
        self.api_key = api_key or os.getenv('FRED_API_KEY')
        self._cache: Dict[str, Tuple[datetime, float]] = {}
        self._fallback_mode = self.api_key is None
        
        if self._fallback_mode:
            _logger.warning(
                "FRED API key not configured. Using fallback rates. "
                "Set FRED_API_KEY environment variable for live data."
            )
    
    # ==========================================
    # PUBLIC API
    # ==========================================
    
    def get_risk_free_rate(self, maturity: str = '10Y') -> float:
        """
        Get current risk-free rate for DCF/WACC calculations.
        
        Args:
            maturity: Treasury maturity ('10Y', '5Y', '30Y', '3M', etc.)
            
        Returns:
            Rate as decimal (e.g., 0.042 for 4.2%)
        """
        if self._fallback_mode:
            return DEFAULT_RATES.get(maturity, DEFAULT_RATES['10Y'])
        
        series_id = TREASURY_SERIES.get(maturity, 'DGS10')
        return self._get_latest_observation(series_id)
    
    def get_treasury_curve(self) -> Dict[str, float]:
        """
        Get full treasury yield curve.
        
        Returns:
            Dict mapping maturity to rate: {'3M': 0.045, '10Y': 0.042, ...}
        """
        curve = {}
        for maturity, series_id in TREASURY_SERIES.items():
            if maturity == 'fed_funds':
                continue  # Not part of yield curve
            
            try:
                rate = self._get_latest_observation(series_id) if not self._fallback_mode else DEFAULT_RATES.get(maturity)
                if rate:
                    curve[maturity] = rate
            except Exception as e:
                _logger.warning(f"Failed to get {maturity} rate: {e}")
        
        return curve
    
    def get_fed_funds_rate(self) -> float:
        """Get current Federal Funds rate."""
        if self._fallback_mode:
            return DEFAULT_RATES['fed_funds']
        return self._get_latest_observation('DFF')
    
    def get_inflation_expectation(self) -> float:
        """Get 5-year breakeven inflation rate."""
        if self._fallback_mode:
            return 0.023  # 2.3% default
        return self._get_latest_observation('T5YIE')
    
    def get_rate_info(self, maturity: str = '10Y') -> Dict:
        """
        Get rate with metadata.
        
        Returns:
            {
                'rate': 0.042,
                'maturity': '10Y',
                'series_id': 'DGS10',
                'date': '2024-12-06',
                'source': 'FRED' or 'Fallback'
            }
        """
        rate = self.get_risk_free_rate(maturity)
        series_id = TREASURY_SERIES.get(maturity, 'DGS10')
        
        return {
            'rate': rate,
            'maturity': maturity,
            'series_id': series_id,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'source': 'Fallback (no API key)' if self._fallback_mode else 'FRED API',
            'is_fallback': self._fallback_mode
        }
    
    # ==========================================
    # INTERNAL METHODS
    # ==========================================
    
    def _get_latest_observation(self, series_id: str) -> float:
        """
        Get latest observation for a FRED series.
        Uses caching to minimize API calls.
        """
        # Check cache
        cache_key = series_id
        if cache_key in self._cache:
            cached_time, cached_value = self._cache[cache_key]
            if datetime.now() - cached_time < timedelta(seconds=CACHE_TTL_SECONDS):
                _logger.debug(f"Cache hit for {series_id}: {cached_value}")
                return cached_value
        
        # Fetch from API
        try:
            rate = self._fetch_series_latest(series_id)
            self._cache[cache_key] = (datetime.now(), rate)
            return rate
        except Exception as e:
            _logger.error(f"FRED API error for {series_id}: {e}")
            # Return fallback if API fails
            return DEFAULT_RATES.get('10Y', 0.042)
    
    def _fetch_series_latest(self, series_id: str) -> float:
        """
        Fetch latest value from FRED API.
        """
        params = {
            'series_id': series_id,
            'api_key': self.api_key,
            'file_type': 'json',
            'sort_order': 'desc',
            'limit': 10,  # Get recent values (in case latest is missing)
        }
        
        url = f"{FRED_BASE_URL}/series/observations"
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        observations = data.get('observations', [])
        
        if not observations:
            raise ValueError(f"No observations found for {series_id}")
        
        # Find first valid observation (some days have '.' for missing data)
        for obs in observations:
            value = obs.get('value')
            if value and value != '.':
                rate = float(value) / 100  # Convert percentage to decimal
                _logger.info(f"FRED {series_id}: {rate:.4f} ({obs.get('date')})")
                return rate
        
        raise ValueError(f"No valid data found for {series_id}")
    
    def clear_cache(self):
        """Clear the rate cache."""
        self._cache.clear()
    
    def is_api_configured(self) -> bool:
        """Check if API key is configured."""
        return not self._fallback_mode


# ==========================================
# SINGLETON INSTANCE
# ==========================================

_fred_client: Optional[FREDClient] = None


def get_fred_client() -> FREDClient:
    """Get or create singleton FRED client."""
    global _fred_client
    if _fred_client is None:
        _fred_client = FREDClient()
    return _fred_client


# ==========================================
# CONVENIENCE FUNCTIONS
# ==========================================

def get_risk_free_rate(maturity: str = '10Y') -> float:
    """
    Get current risk-free rate.
    
    Args:
        maturity: Treasury maturity ('10Y', '5Y', '30Y', '3M')
        
    Returns:
        Rate as decimal (e.g., 0.042 for 4.2%)
    """
    return get_fred_client().get_risk_free_rate(maturity)


def get_treasury_rate_for_dcf() -> Dict:
    """
    Get treasury rate with metadata for DCF calculations.
    
    Returns:
        {
            'rate': 0.042,
            'source': 'FRED API' or 'Fallback',
            'date': '2024-12-06',
            ...
        }
    """
    return get_fred_client().get_rate_info('10Y')


# ==========================================
# INTEGRATION WITH DCF MODEL
# ==========================================

def calculate_wacc_with_live_rate(
    cost_of_equity: float,
    cost_of_debt: float,
    equity_weight: float,
    debt_weight: float,
    tax_rate: float = 0.21,
    use_live_rf: bool = True
) -> Dict:
    """
    Calculate WACC using live risk-free rate.
    
    This is a helper for integrating with dcf_modeling.py.
    
    Args:
        cost_of_equity: Cost of equity (can be recalculated with live Rf)
        cost_of_debt: Pre-tax cost of debt
        equity_weight: E / (E + D)
        debt_weight: D / (E + D)
        tax_rate: Corporate tax rate (default 21%)
        use_live_rf: If True, uses live FRED rate; else uses provided values
        
    Returns:
        {
            'wacc': calculated WACC,
            'cost_of_equity': Ke,
            'cost_of_debt_after_tax': Kd * (1 - t),
            'risk_free_rate': Rf used,
            'rf_source': 'FRED API' or 'Fallback'
        }
    """
    rf_info = get_treasury_rate_for_dcf()
    
    # After-tax cost of debt
    cost_of_debt_after_tax = cost_of_debt * (1 - tax_rate)
    
    # WACC calculation
    wacc = (equity_weight * cost_of_equity) + (debt_weight * cost_of_debt_after_tax)
    
    return {
        'wacc': wacc,
        'cost_of_equity': cost_of_equity,
        'cost_of_debt_after_tax': cost_of_debt_after_tax,
        'risk_free_rate': rf_info['rate'],
        'rf_source': rf_info['source'],
        'rf_date': rf_info['date'],
        'tax_rate': tax_rate,
        'equity_weight': equity_weight,
        'debt_weight': debt_weight
    }


# ==========================================
# TEST / EXAMPLE
# ==========================================

if __name__ == "__main__":
    print("=" * 60)
    print("FRED API MODULE TEST")
    print("=" * 60)
    
    client = FREDClient()
    
    print(f"\nAPI Configured: {client.is_api_configured()}")
    
    # Get 10Y rate
    info = client.get_rate_info('10Y')
    print(f"\n10-Year Treasury Rate:")
    print(f"  Rate: {info['rate']:.2%}")
    print(f"  Source: {info['source']}")
    print(f"  Date: {info['date']}")
    
    # Get yield curve (if API available)
    if client.is_api_configured():
        print(f"\nTreasury Yield Curve:")
        curve = client.get_treasury_curve()
        for maturity, rate in sorted(curve.items(), key=lambda x: x[0]):
            print(f"  {maturity}: {rate:.2%}")
    
    # Test DCF helper
    print("\nWACC Calculation Example:")
    wacc_result = calculate_wacc_with_live_rate(
        cost_of_equity=0.10,  # 10%
        cost_of_debt=0.05,    # 5%
        equity_weight=0.70,
        debt_weight=0.30
    )
    print(f"  WACC: {wacc_result['wacc']:.2%}")
    print(f"  Risk-Free Rate: {wacc_result['risk_free_rate']:.2%}")
    print(f"  Source: {wacc_result['rf_source']}")
    
    print("\n[OK] Module ready for integration")

