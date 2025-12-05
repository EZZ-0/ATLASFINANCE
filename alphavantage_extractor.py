"""
ALPHA VANTAGE DATA EXTRACTOR
============================
Alternative third data source for multi-source fusion.

Alpha Vantage Free Tier: 500 API calls/day, 5 calls/minute
Best for: Historical prices, fundamentals, earnings, balance sheets

API Docs: https://www.alphavantage.co/documentation/
Get free key: https://www.alphavantage.co/support/#api-key
"""

import os
import requests
import time
from datetime import datetime
from typing import Dict, Optional, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import logging
try:
    from utils.logging_config import EngineLogger
    _logger = EngineLogger.get_logger("AlphaVantage")
except ImportError:
    import logging
    _logger = logging.getLogger("AlphaVantage")


class AlphaVantageExtractor:
    """
    Alpha Vantage API extractor.
    
    Free tier: 500 calls/day, 5 calls/minute
    Endpoints used:
    - OVERVIEW: Company fundamentals
    - INCOME_STATEMENT: Income statement
    - BALANCE_SHEET: Balance sheet
    - CASH_FLOW: Cash flow statement
    - EARNINGS: Quarterly/annual earnings
    - GLOBAL_QUOTE: Real-time price
    """
    
    BASE_URL = "https://www.alphavantage.co/query"
    
    # Field mapping: Alpha Vantage field -> our standard field name
    FIELD_MAP = {
        # Overview/Profile
        'Symbol': 'ticker',
        'Name': 'company_name',
        'Description': 'description',
        'Exchange': 'exchange',
        'Currency': 'currency',
        'Country': 'country',
        'Sector': 'sector',
        'Industry': 'industry',
        'FullTimeEmployees': 'employees',
        'FiscalYearEnd': 'fiscal_year_end',
        
        # Market Data
        'MarketCapitalization': 'market_cap',
        'EBITDA': 'ebitda',
        'PERatio': 'pe_ratio',
        'PEGRatio': 'peg_ratio',
        'BookValue': 'book_value',
        'DividendPerShare': 'dividend_per_share',
        'DividendYield': 'dividend_yield',
        'EPS': 'eps',
        'RevenuePerShareTTM': 'revenue_per_share',
        'ProfitMargin': 'profit_margin',
        'OperatingMarginTTM': 'operating_margin',
        'ReturnOnAssetsTTM': 'roa',
        'ReturnOnEquityTTM': 'roe',
        'RevenueTTM': 'revenue_ttm',
        'GrossProfitTTM': 'gross_profit_ttm',
        'DilutedEPSTTM': 'diluted_eps',
        'QuarterlyEarningsGrowthYOY': 'earnings_growth',
        'QuarterlyRevenueGrowthYOY': 'revenue_growth',
        'AnalystTargetPrice': 'target_price',
        'TrailingPE': 'trailing_pe',
        'ForwardPE': 'forward_pe',
        'PriceToSalesRatioTTM': 'price_to_sales',
        'PriceToBookRatio': 'price_to_book',
        'EVToRevenue': 'ev_to_revenue',
        'EVToEBITDA': 'ev_to_ebitda',
        'Beta': 'beta',
        '52WeekHigh': 'fifty_two_week_high',
        '52WeekLow': 'fifty_two_week_low',
        '50DayMovingAverage': 'sma_50',
        '200DayMovingAverage': 'sma_200',
        'SharesOutstanding': 'shares_outstanding',
        'DividendDate': 'dividend_date',
        'ExDividendDate': 'ex_dividend_date',
        
        # Global Quote (real-time)
        '05. price': 'current_price',
        '08. previous close': 'previous_close',
        '09. change': 'price_change',
        '10. change percent': 'price_change_pct',
        '06. volume': 'volume',
    }
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Alpha Vantage extractor.
        
        Args:
            api_key: API key. If not provided, reads from ALPHAVANTAGE_API_KEY env var.
        """
        self.api_key = api_key or os.getenv('ALPHAVANTAGE_API_KEY') or os.getenv('ALPHA_VANTAGE_API_KEY')
        self.available = bool(self.api_key)
        
        if not self.available:
            pass  # Silent - don't spam console
        else:
            print(f"[AV] Alpha Vantage initialized: {self.api_key[:8]}...")
        
        # Rate limiting: 5 calls/minute
        self._last_request_time = 0
        self._min_request_interval = 12.0  # 12 seconds = 5 calls/minute max
        self._daily_calls = 0
        self._daily_limit = 500
        self._last_reset_date = datetime.now().date()
    
    def _check_rate_limit(self) -> bool:
        """Check if we're within rate limits."""
        if datetime.now().date() != self._last_reset_date:
            self._daily_calls = 0
            self._last_reset_date = datetime.now().date()
        
        return self._daily_calls < self._daily_limit
    
    def _make_request(self, function: str, symbol: str, extra_params: Optional[Dict] = None) -> Optional[Dict]:
        """
        Make API request with rate limiting.
        
        Args:
            function: API function (e.g., 'OVERVIEW', 'GLOBAL_QUOTE')
            symbol: Stock symbol
            extra_params: Additional parameters
        
        Returns:
            JSON response or None
        """
        if not self.available:
            return None
        
        if not self._check_rate_limit():
            print(f"[AV] Daily limit reached ({self._daily_limit} calls)")
            return None
        
        # Rate limiting - 12 seconds between calls
        elapsed = time.time() - self._last_request_time
        if elapsed < self._min_request_interval:
            time.sleep(self._min_request_interval - elapsed)
        
        params = {
            'function': function,
            'symbol': symbol.upper(),
            'apikey': self.api_key,
        }
        if extra_params:
            params.update(extra_params)
        
        try:
            response = requests.get(self.BASE_URL, params=params, timeout=15)
            self._last_request_time = time.time()
            self._daily_calls += 1
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for API errors
                if 'Error Message' in data:
                    print(f"[AV] API error: {data['Error Message'][:50]}")
                    return None
                if 'Note' in data:  # Rate limit message
                    print(f"[AV] Rate limited: {data['Note'][:50]}")
                    return None
                if 'Information' in data:  # API limit message
                    print(f"[AV] {data['Information'][:50]}")
                    return None
                
                return data
            else:
                print(f"[AV] HTTP error: {response.status_code}")
                return None
                
        except requests.exceptions.Timeout:
            print("[AV] Request timeout")
            return None
        except requests.exceptions.RequestException as e:
            print(f"[AV] Request failed: {e}")
            return None
    
    def get_overview(self, ticker: str) -> Dict:
        """Get company overview/fundamentals - most useful endpoint."""
        data = self._make_request('OVERVIEW', ticker)
        if data:
            return self._map_fields(data)
        return {}
    
    def get_quote(self, ticker: str) -> Dict:
        """Get real-time quote."""
        data = self._make_request('GLOBAL_QUOTE', ticker)
        if data and 'Global Quote' in data:
            return self._map_fields(data['Global Quote'])
        return {}
    
    def get_earnings(self, ticker: str) -> Dict:
        """Get earnings data."""
        data = self._make_request('EARNINGS', ticker)
        if data and 'annualEarnings' in data:
            # Get most recent annual earnings
            annual = data['annualEarnings']
            if annual and len(annual) > 0:
                latest = annual[0]
                return {
                    'reported_eps': float(latest.get('reportedEPS', 0)),
                    'fiscal_date': latest.get('fiscalDateEnding'),
                }
        return {}
    
    def _map_fields(self, data: Dict) -> Dict:
        """Map Alpha Vantage fields to our standard names."""
        mapped = {}
        for av_key, value in data.items():
            if av_key in self.FIELD_MAP:
                our_key = self.FIELD_MAP[av_key]
                if value is not None and value != '' and value != 'None':
                    # Try to convert numeric strings
                    try:
                        if isinstance(value, str) and value.replace('.', '').replace('-', '').isdigit():
                            value = float(value)
                    except:
                        pass
                    mapped[our_key] = value
        return mapped
    
    def extract_all(self, ticker: str) -> Dict:
        """
        Extract all available data for a ticker.
        
        Makes 2 API calls: OVERVIEW + GLOBAL_QUOTE
        (Keeping it minimal due to rate limits)
        
        Args:
            ticker: Stock symbol
        
        Returns:
            Combined dict of extracted data
        """
        if not self.available:
            return {}
        
        print(f"[AV] Extracting data for {ticker.upper()}...")
        result = {}
        
        # Overview - has most fundamentals
        overview = self.get_overview(ticker)
        result.update(overview)
        
        # Quote - real-time price
        quote = self.get_quote(ticker)
        result.update(quote)
        
        if result:
            print(f"[AV] Extracted {len(result)} fields for {ticker.upper()}")
        
        return result
    
    def get_field(self, ticker: str, field: str) -> Optional[Any]:
        """Get a specific field value."""
        if not self.available:
            return None
        
        # Most fields come from overview
        data = self.get_overview(ticker)
        value = data.get(field)
        
        if value is None and field == 'current_price':
            # Price needs quote endpoint
            quote = self.get_quote(ticker)
            value = quote.get('current_price')
        
        return value


# Singleton instance
_av_instance = None

def get_alphavantage_extractor() -> AlphaVantageExtractor:
    """Get or create Alpha Vantage extractor singleton."""
    global _av_instance
    if _av_instance is None:
        _av_instance = AlphaVantageExtractor()
    return _av_instance


# Quick test
if __name__ == "__main__":
    av = AlphaVantageExtractor()
    if av.available:
        data = av.extract_all("AAPL")
        print(f"\nExtracted {len(data)} fields:")
        for key, value in list(data.items())[:15]:
            print(f"  {key}: {value}")
    else:
        print("Set ALPHAVANTAGE_API_KEY environment variable to test")
        print("Get free key: https://www.alphavantage.co/support/#api-key")


