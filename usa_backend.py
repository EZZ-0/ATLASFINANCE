"""
USA EARNINGS ENGINE - BACKEND EXTRACTOR
========================================
Multi-source financial data extractor for USA public companies.
Uses SEC EDGAR API + yfinance for comprehensive data coverage.

Data Sources:
1. SEC EDGAR API (XBRL structured data) - PRIMARY
2. yfinance (Yahoo Finance) - FALLBACK
3. Financial Modeling Prep API - OPTIONAL (paid)

Speed: < 5 seconds for full 10-year history
"""

import os
import json
import time
import requests
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Callable, Any
from functools import wraps
import usa_dictionary as usa_dict

# Import centralized logging
from utils.logging_config import EngineLogger, log_error, log_warning, log_info
# Import ticker mapper for alias handling (M011)
from utils.ticker_mapper import normalize_ticker, PROBLEMATIC_TICKERS

# Initialize logger for this module
_logger = EngineLogger.get_logger("USABackend")


# ==========================================
# RETRY DECORATOR WITH EXPONENTIAL BACKOFF
# ==========================================

def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 30.0,
    exponential_base: float = 2.0,
    retryable_exceptions: Tuple = (requests.exceptions.RequestException, requests.exceptions.Timeout)
):
    """
    Decorator for retrying API calls with exponential backoff.
    
    Handles rate limiting (HTTP 429) and temporary failures gracefully.
    
    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay in seconds
        max_delay: Maximum delay between retries
        exponential_base: Multiplier for exponential backoff
        retryable_exceptions: Tuple of exception types to retry on
    
    Usage:
        @retry_with_backoff(max_retries=3)
        def fetch_data(url):
            return requests.get(url)
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    result = func(*args, **kwargs)
                    
                    # Check for rate limiting in response (if it's a requests Response)
                    if hasattr(result, 'status_code') and result.status_code == 429:
                        raise requests.exceptions.RequestException("Rate limited (HTTP 429)")
                    
                    return result
                    
                except retryable_exceptions as e:
                    last_exception = e
                    
                    if attempt < max_retries:
                        # Calculate delay with exponential backoff + jitter
                        delay = min(base_delay * (exponential_base ** attempt), max_delay)
                        # Add jitter (±25%) to prevent thundering herd
                        import random
                        jitter = delay * 0.25 * (2 * random.random() - 1)
                        delay = delay + jitter
                        
                        _logger.warning(
                            f"Retry {attempt + 1}/{max_retries} for {func.__name__} "
                            f"after {delay:.1f}s delay. Error: {e}"
                        )
                        time.sleep(delay)
                    else:
                        _logger.error(
                            f"All {max_retries} retries failed for {func.__name__}. "
                            f"Last error: {e}"
                        )
                        
                except Exception as e:
                    # Non-retryable exception, raise immediately
                    _logger.error(f"Non-retryable error in {func.__name__}: {e}")
                    raise
            
            # All retries exhausted
            if last_exception:
                raise last_exception
            
        return wrapper
    return decorator


def retry_yfinance_call(func: Callable, *args, max_retries: int = 3, **kwargs):
    """
    Wrapper for yfinance calls with retry logic.
    
    yfinance doesn't use requests directly, so we handle its errors separately.
    
    Args:
        func: The yfinance function to call
        *args: Arguments for the function
        max_retries: Maximum retry attempts
        **kwargs: Keyword arguments for the function
    
    Returns:
        Result from the yfinance call
    """
    last_exception = None
    
    for attempt in range(max_retries + 1):
        try:
            result = func(*args, **kwargs)
            return result
            
        except Exception as e:
            error_str = str(e).lower()
            
            # Check if it's a rate limiting error
            if 'rate limit' in error_str or 'too many requests' in error_str or '429' in error_str:
                last_exception = e
                
                if attempt < max_retries:
                    delay = min(2.0 * (2 ** attempt), 30.0)  # Exponential backoff
                    _logger.warning(
                        f"yfinance rate limited, retry {attempt + 1}/{max_retries} "
                        f"after {delay:.1f}s. Error: {e}"
                    )
                    time.sleep(delay)
                else:
                    _logger.error(f"yfinance rate limit persists after {max_retries} retries")
            else:
                # Non-rate-limit error, raise immediately
                raise
    
    if last_exception:
        raise last_exception

# Import quant engine for advanced analysis
try:
    from quant_engine import QuantEngine
    QUANT_ENGINE_AVAILABLE = True
except ImportError:
    QUANT_ENGINE_AVAILABLE = False

# === OPTIONAL DEPENDENCIES ===
try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False
    print("⚠️ yfinance not installed. Install with: pip install yfinance")

# FMP (Financial Modeling Prep) - Third data source
try:
    from fmp_extractor import get_fmp_extractor, FMPExtractor
    FMP_AVAILABLE = True
except ImportError:
    FMP_AVAILABLE = False

# Alpha Vantage - Alternative third data source (500 calls/day free)
try:
    from alphavantage_extractor import get_alphavantage_extractor, AlphaVantageExtractor
    ALPHAVANTAGE_AVAILABLE = True
except ImportError:
    ALPHAVANTAGE_AVAILABLE = False

class USAFinancialExtractor:
    """
    Extracts financial data from USA public companies using multiple sources.
    Prioritizes SEC API for accuracy, falls back to yfinance for speed.
    Now with FIELD-LEVEL FALLBACK for gap filling.
    """
    
    # Field priority map: which source to try first for each field type
    FIELD_SOURCE_PRIORITY = {
        # Financial statements - SEC most accurate
        'revenue': ['sec', 'yfinance'],
        'net_income': ['sec', 'yfinance'],
        'total_assets': ['sec', 'yfinance'],
        'total_liabilities': ['sec', 'yfinance'],
        'total_equity': ['sec', 'yfinance'],
        'operating_income': ['sec', 'yfinance'],
        'gross_profit': ['sec', 'yfinance'],
        'total_debt': ['sec', 'yfinance'],
        'cash_and_equivalents': ['sec', 'yfinance'],
        'free_cash_flow': ['sec', 'yfinance'],
        
        # Market data - yfinance better for real-time
        'current_price': ['yfinance', 'sec'],
        'market_cap': ['yfinance', 'sec'],
        'volume': ['yfinance'],
        'shares_outstanding': ['yfinance', 'sec'],
        'beta': ['yfinance'],
        'fifty_two_week_high': ['yfinance'],
        'fifty_two_week_low': ['yfinance'],
        
        # Ratios - calculated from source data
        'pe_ratio': ['yfinance', 'sec'],
        'forward_pe': ['yfinance'],
        'peg_ratio': ['yfinance'],
        'price_to_book': ['yfinance', 'sec'],
        'price_to_sales': ['yfinance', 'sec'],
        'debt_to_equity': ['yfinance', 'sec'],
        'current_ratio': ['yfinance', 'sec'],
        'quick_ratio': ['yfinance', 'sec'],
        'roe': ['yfinance', 'sec'],
        'roa': ['yfinance', 'sec'],
        
        # Company info
        'sector': ['yfinance', 'sec'],
        'industry': ['yfinance', 'sec'],
        'employees': ['yfinance', 'sec'],
        'description': ['yfinance', 'sec'],
        'company_name': ['yfinance', 'sec'],
        
        # Analyst/sentiment
        'analyst_rating': ['yfinance'],
        'target_price': ['yfinance'],
        'recommendation': ['yfinance'],
    }
    
    def __init__(self, user_agent: str = "AtlasFinancialIntelligence/2.0 (Educational Research; Python 3.13; Contact: research@atlas-fi.com)"):
        """
        Initialize extractor with SEC API headers.
        
        Args:
            user_agent: Required by SEC (must include contact info in production)
                       SEC requires: Company Name, Version, Purpose, Contact
        """
        self.headers = {
            'User-Agent': user_agent,
            'Accept-Encoding': 'gzip, deflate',
            'Host': 'data.sec.gov',
            'Connection': 'keep-alive',
            'Accept': 'application/json'
        }
        self.sec_base_url = "https://data.sec.gov/api/xbrl"
        
        # TTL-based cache for market data
        # Format: {key: {"data": value, "timestamp": datetime, "ttl_seconds": int}}
        self._cache = {}
        self._cache_ttl = {
            "market_data": 3600,      # 1 hour for real-time market data
            "financials": 86400,       # 24 hours for financial statements
            "company_info": 604800,    # 7 days for company info
            "default": 3600            # 1 hour default
        }
        
        # Track extraction sources for transparency
        self._extraction_sources = {}
    
    # ==========================================
    # API REQUEST HELPERS WITH RETRY
    # ==========================================
    
    def _make_sec_request(self, url: str, timeout: int = 15) -> requests.Response:
        """
        Make a request to SEC API with retry logic.
        
        Args:
            url: The SEC API URL
            timeout: Request timeout in seconds
        
        Returns:
            Response object
        
        Raises:
            requests.exceptions.RequestException: After all retries exhausted
        """
        max_retries = 3
        last_exception = None
        
        for attempt in range(max_retries + 1):
            try:
                resp = requests.get(url, headers=self.headers, timeout=timeout)
                
                # Check for rate limiting
                if resp.status_code == 429:
                    raise requests.exceptions.RequestException(
                        f"SEC API rate limited (HTTP 429). Retry-After: {resp.headers.get('Retry-After', 'unknown')}"
                    )
                
                return resp
                
            except (requests.exceptions.RequestException, requests.exceptions.Timeout) as e:
                last_exception = e
                
                if attempt < max_retries:
                    # Exponential backoff: 1s, 2s, 4s
                    delay = min(1.0 * (2 ** attempt), 10.0)
                    _logger.warning(f"SEC API retry {attempt + 1}/{max_retries} after {delay:.1f}s. Error: {e}")
                    time.sleep(delay)
                else:
                    _logger.error(f"SEC API failed after {max_retries} retries: {e}")
        
        if last_exception:
            raise last_exception
    
    def _make_yfinance_call(self, func: Callable, *args, **kwargs):
        """
        Make a yfinance API call with retry logic for rate limiting.
        
        Args:
            func: The yfinance function/method to call
            *args: Positional arguments
            **kwargs: Keyword arguments
        
        Returns:
            Result from yfinance call
        """
        return retry_yfinance_call(func, *args, max_retries=3, **kwargs)
    
    # ==========================================
    # TTL-BASED CACHING
    # ==========================================
    
    def _cache_get(self, key: str) -> Optional[Any]:
        """
        Get a value from cache if it exists and hasn't expired.
        
        Args:
            key: Cache key
        
        Returns:
            Cached data or None if expired/not found
        """
        if key not in self._cache:
            return None
        
        entry = self._cache[key]
        timestamp = entry.get("timestamp")
        ttl = entry.get("ttl_seconds", self._cache_ttl["default"])
        
        # Check if expired
        if timestamp:
            age = (datetime.now() - timestamp).total_seconds()
            if age > ttl:
                _logger.debug(f"Cache expired for key: {key} (age: {age:.0f}s, ttl: {ttl}s)")
                del self._cache[key]
                return None
        
        _logger.debug(f"Cache hit for key: {key}")
        return entry.get("data")
    
    def _cache_set(self, key: str, data: Any, cache_type: str = "default"):
        """
        Store a value in cache with TTL.
        
        Args:
            key: Cache key
            data: Data to cache
            cache_type: Type of cache ("market_data", "financials", "company_info", "default")
        """
        ttl = self._cache_ttl.get(cache_type, self._cache_ttl["default"])
        
        self._cache[key] = {
            "data": data,
            "timestamp": datetime.now(),
            "ttl_seconds": ttl,
            "cache_type": cache_type
        }
        _logger.debug(f"Cache set for key: {key} (ttl: {ttl}s)")
    
    def _cache_clear(self, key: Optional[str] = None):
        """
        Clear cache entries.
        
        Args:
            key: Specific key to clear, or None to clear all
        """
        if key:
            if key in self._cache:
                del self._cache[key]
                _logger.info(f"Cache cleared for key: {key}")
        else:
            self._cache.clear()
            _logger.info("Cache cleared (all entries)")
    
    def _cache_stats(self) -> Dict:
        """
        Get cache statistics.
        
        Returns:
            Dict with cache stats
        """
        now = datetime.now()
        stats = {
            "total_entries": len(self._cache),
            "entries_by_type": {},
            "expired_count": 0
        }
        
        for key, entry in self._cache.items():
            cache_type = entry.get("cache_type", "default")
            stats["entries_by_type"][cache_type] = stats["entries_by_type"].get(cache_type, 0) + 1
            
            # Check if expired
            timestamp = entry.get("timestamp")
            ttl = entry.get("ttl_seconds", 3600)
            if timestamp and (now - timestamp).total_seconds() > ttl:
                stats["expired_count"] += 1
        
        return stats
    
    # ==========================================
    # 0. FISCAL YEAR INTELLIGENCE
    # ==========================================
    
    def detect_fiscal_year_info(self, df: pd.DataFrame, ticker: str = "") -> Dict:
        """
        Intelligently detect fiscal year information from financial statement dates.
        
        Identifies the most recent COMPLETE fiscal year (12 full months) and
        determines the correct fiscal year offset to use for extraction.
        
        Args:
            df: Financial statement DataFrame with date columns
            ticker: Company ticker for logging
            
        Returns:
            Dict with fiscal year info:
                - latest_fy_end: Date of most recent complete fiscal year
                - latest_fy_label: How the company labels it (e.g., "Fiscal 2024")
                - recommended_offset: Offset to use for current complete FY
                - is_recent: Whether data is from current calendar year
        """
        from datetime import datetime, timedelta
        
        if df.empty:
            return {
                "latest_fy_end": None,
                "latest_fy_label": "Unknown",
                "recommended_offset": 0,
                "is_recent": False,
                "note": "Empty DataFrame"
            }
        
        # Get date columns (yfinance format: dates as columns)
        if isinstance(df.index[0], str):
            # Dates are columns
            date_cols = [col for col in df.columns if isinstance(col, (str, pd.Timestamp))]
            if not date_cols:
                return {"latest_fy_end": None, "recommended_offset": 0}
            
            # Convert to datetime
            dates = []
            for col in date_cols:
                try:
                    if isinstance(col, pd.Timestamp):
                        dates.append(col)
                    else:
                        dates.append(pd.to_datetime(col))
                except (ValueError, TypeError, pd.errors.ParserError):
                    # Skip columns that can't be parsed as dates
                    continue
            
            if not dates:
                return {"latest_fy_end": None, "recommended_offset": 0}
            
            # Sort dates (most recent first)
            dates.sort(reverse=True)
            latest_date = dates[0]
            
            # Determine if this is a complete fiscal year
            today = datetime.now()
            months_since = (today.year - latest_date.year) * 12 + (today.month - latest_date.month)
            
            # If fiscal year ended more than 3 months ago, it's likely complete and filed
            if months_since >= 3:
                recommended_offset = 0  # This is the most recent complete FY
                is_recent = months_since <= 6  # Filed within last 6 months
            else:
                # FY just ended, might not be filed yet
                recommended_offset = 1  # Use previous FY
                is_recent = False
            
            # Determine fiscal year label (usually by calendar year of FY end)
            fy_year = latest_date.year
            fy_label = f"Fiscal {fy_year}"
            
            return {
                "latest_fy_end": latest_date.strftime("%Y-%m-%d"),
                "latest_fy_label": fy_label,
                "recommended_offset": recommended_offset,
                "is_recent": is_recent,
                "months_since_fy_end": months_since,
                "note": f"FY ended {latest_date.strftime('%b %Y')}, {months_since} months ago"
            }
        
        return {
            "latest_fy_end": None,
            "latest_fy_label": "Unknown",
            "recommended_offset": 0,
            "is_recent": False,
            "note": "Could not parse date format"
        }
    
    # ==========================================
    # 1. TICKER LOOKUP & VALIDATION
    # ==========================================
    
    def get_cik_from_ticker(self, ticker: str) -> Optional[str]:
        """
        Convert stock ticker to SEC CIK number.
        
        Args:
            ticker: Stock symbol (e.g., "AAPL", "MSFT")
            
        Returns:
            10-digit CIK string or None if not found
        """
        try:
            # SEC maintains a ticker-to-CIK mapping
            url = "https://www.sec.gov/files/company_tickers.json"
            resp = self._make_sec_request(url, timeout=10)
            resp.raise_for_status()
            
            data = resp.json()
            ticker_upper = ticker.upper().strip()
            
            # Search through mapping
            for item in data.values():
                if item.get("ticker") == ticker_upper:
                    cik = str(item["cik_str"]).zfill(10)  # Pad to 10 digits
                    return cik
            
            return None
        except Exception as e:
            print(f"[ERROR] CIK Lookup Failed: {e}")
            return None
    
    def validate_ticker(self, ticker: str) -> Tuple[bool, str]:
        """
        Check if ticker exists and is valid.
        
        Returns:
            (is_valid, company_name or error_message)
        """
        try:
            if YFINANCE_AVAILABLE:
                stock = yf.Ticker(ticker)
                info = stock.info
                if "shortName" in info or "longName" in info:
                    name = info.get("longName", info.get("shortName", ticker))
                    return True, name
            
            # Fallback to CIK lookup
            cik = self.get_cik_from_ticker(ticker)
            if cik:
                return True, f"{ticker.upper()} (CIK: {cik})"
            
            return False, "Ticker not found in SEC database"
        except Exception as e:
            return False, str(e)
    
    # ==========================================
    # 2. SEC EDGAR API EXTRACTION
    # ==========================================
    
    def extract_from_sec(self, ticker: str, years: int = 5, filing_types: List[str] = ["10-K"]) -> Dict:
        """
        Extract financial data from SEC EDGAR API using XBRL format.
        This is the most accurate source for USA companies.
        
        Args:
            ticker: Stock symbol
            years: Number of years of historical data
            
        Returns:
            Dictionary with financial statements (income, balance, cashflow)
        """
        _logger.info(f"Extracting from SEC EDGAR: {ticker.upper()}")
        print(f"\n[INFO] Extracting from SEC EDGAR: {ticker.upper()}")
        t0 = time.time()
        
        # 1. Get CIK
        cik = self.get_cik_from_ticker(ticker)
        if not cik:
            _logger.warning(f"CIK not found for ticker: {ticker}")
            return {"status": "error", "message": "CIK not found"}
        
        # 2. Fetch Company Facts (XBRL data) with retry logic
        try:
            url = f"{self.sec_base_url}/companyfacts/CIK{cik}.json"
            resp = self._make_sec_request(url, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            
            # 3. Extract Facts
            facts = data.get("facts", {})
            us_gaap = facts.get("us-gaap", {})
            
            # 4. Build Financial Statements
            filing_label = " + ".join(filing_types)
            _logger.debug(f"Extracting {filing_label} filings for {ticker}")
            print(f"   Extracting {filing_label} filings...")
            
            financials = {
                "ticker": ticker.upper(),
                "company_name": data.get("entityName", ticker),
                "cik": cik,
                "filing_types": filing_types,
                "extraction_time": f"{time.time() - t0:.2f}s",
                "income_statement": self._extract_income_statement(us_gaap, filing_types),
                "balance_sheet": self._extract_balance_sheet(us_gaap, filing_types),
                "cash_flow": self._extract_cash_flow(us_gaap, filing_types),
                "per_share_data": self._extract_per_share_data(us_gaap, filing_types)
            }
            
            _logger.info(f"SEC Extraction Complete for {ticker}: {financials['extraction_time']}")
            EngineLogger.log_data_extraction(ticker, success=True)
            print(f"[OK] SEC Extraction Complete: {financials['extraction_time']}")
            return financials
            
        except requests.exceptions.HTTPError as e:
            _logger.error(f"SEC HTTP error for {ticker}: {e}")
            if e.response.status_code == 404:
                return {"status": "error", "message": "Company not found in SEC database"}
            EngineLogger.log_data_extraction(ticker, success=False, error=str(e))
            return {"status": "error", "message": f"SEC API Error: {e}"}
        except Exception as e:
            _logger.error(f"SEC extraction failed for {ticker}: {e}", exc_info=True)
            EngineLogger.log_data_extraction(ticker, success=False, error=str(e))
            return {"status": "error", "message": f"Extraction failed: {e}"}
    
    def _extract_income_statement(self, us_gaap: Dict, filing_types: List[str] = ["10-K"]) -> pd.DataFrame:
        """
        Extract income statement line items from XBRL data
        
        Args:
            us_gaap: XBRL data dictionary
            filing_types: List of SEC filing types to extract
                         ["10-K"] = Annual only
                         ["10-Q"] = Quarterly only
                         ["10-K", "10-Q"] = Both annual and quarterly
                         ["S-1"] = IPO filings
        """
        metrics = {}
        
        # Define what we're looking for (using XBRL tags)
        search_map = {
            "Revenue": ["Revenues", "SalesRevenueNet", "RevenueFromContractWithCustomerExcludingAssessedTax"],
            "Cost_of_Revenue": ["CostOfRevenue", "CostOfGoodsAndServicesSold"],
            "Gross_Profit": ["GrossProfit"],
            "Operating_Expenses": ["OperatingExpenses"],
            "Operating_Income": ["OperatingIncomeLoss"],
            "Interest_Expense": ["InterestExpense"],
            "Pretax_Income": ["IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest"],
            "Tax_Expense": ["IncomeTaxExpenseBenefit"],
            "Net_Income": ["NetIncomeLoss", "ProfitLoss"]
        }
        
        # Search for each metric
        for metric_name, xbrl_tags in search_map.items():
            for tag in xbrl_tags:
                if tag in us_gaap:
                    # Extract values for specified filing types
                    values = us_gaap[tag].get("units", {})
                    if "USD" in values:
                        # Filter by filing type
                        filtered_data = [
                            item for item in values["USD"]
                            if item.get("form") in filing_types and "val" in item
                        ]
                        if filtered_data:
                            metrics[metric_name] = filtered_data
                            break
        
        # Convert to DataFrame
        return self._format_time_series(metrics)
    
    def _extract_balance_sheet(self, us_gaap: Dict, filing_types: List[str] = ["10-K"]) -> pd.DataFrame:
        """Extract balance sheet items from XBRL data"""
        metrics = {}
        
        search_map = {
            "Total_Assets": ["Assets"],
            "Total_Liabilities": ["Liabilities"],
            "Total_Equity": ["StockholdersEquity", "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest"],
            "Cash": ["CashAndCashEquivalentsAtCarryingValue"],
            "Total_Debt": ["LongTermDebtAndCapitalLeaseObligations", "DebtCurrent"],
            "Current_Assets": ["AssetsCurrent"],
            "Current_Liabilities": ["LiabilitiesCurrent"]
        }
        
        for metric_name, xbrl_tags in search_map.items():
            for tag in xbrl_tags:
                if tag in us_gaap:
                    values = us_gaap[tag].get("units", {})
                    if "USD" in values:
                        filtered_data = [
                            item for item in values["USD"]
                            if item.get("form") in filing_types and "val" in item
                        ]
                        if filtered_data:
                            metrics[metric_name] = filtered_data
                            break
        
        return self._format_time_series(metrics)
    
    def _extract_cash_flow(self, us_gaap: Dict, filing_types: List[str] = ["10-K"]) -> pd.DataFrame:
        """Extract cash flow statement from XBRL data"""
        metrics = {}
        
        search_map = {
            "Operating_Cash_Flow": ["NetCashProvidedByUsedInOperatingActivities"],
            "Investing_Cash_Flow": ["NetCashProvidedByUsedInInvestingActivities"],
            "Financing_Cash_Flow": ["NetCashProvidedByUsedInFinancingActivities"],
            "Capex": ["PaymentsToAcquirePropertyPlantAndEquipment"]
        }
        
        for metric_name, xbrl_tags in search_map.items():
            for tag in xbrl_tags:
                if tag in us_gaap:
                    values = us_gaap[tag].get("units", {})
                    if "USD" in values:
                        filtered_data = [
                            item for item in values["USD"]
                            if item.get("form") in filing_types and "val" in item
                        ]
                        if filtered_data:
                            metrics[metric_name] = filtered_data
                            break
        
        return self._format_time_series(metrics)
    
    def _extract_per_share_data(self, us_gaap: Dict, filing_types: List[str] = ["10-K"]) -> pd.DataFrame:
        """Extract EPS and other per-share metrics"""
        metrics = {}
        
        search_map = {
            "Basic_EPS": ["EarningsPerShareBasic"],
            "Diluted_EPS": ["EarningsPerShareDiluted"],
            "Shares_Outstanding": ["WeightedAverageNumberOfSharesOutstandingBasic"]
        }
        
        for metric_name, xbrl_tags in search_map.items():
            for tag in xbrl_tags:
                if tag in us_gaap:
                    # EPS might be in USD/shares or just shares
                    for unit_type in ["USD/shares", "shares", "pure"]:
                        values = us_gaap[tag].get("units", {})
                        if unit_type in values:
                            filtered_data = [
                                item for item in values[unit_type]
                                if item.get("form") in filing_types and "val" in item
                            ]
                            if filtered_data:
                                metrics[metric_name] = filtered_data
                                break
        
        return self._format_time_series(metrics)
    
    def _format_time_series(self, metrics: Dict) -> pd.DataFrame:
        """Convert raw XBRL data to clean time-series DataFrame"""
        if not metrics:
            return pd.DataFrame()
        
        # Build rows for each year
        rows = {}
        for metric_name, data_points in metrics.items():
            for point in data_points:
                year = point.get("fy")  # Fiscal year
                value = point.get("val")
                
                if year and value:
                    if year not in rows:
                        rows[year] = {}
                    rows[year][metric_name] = value
        
        # Convert to DataFrame
        df = pd.DataFrame.from_dict(rows, orient="index")
        df.index.name = "Year"
        df = df.sort_index(ascending=False)  # Most recent first
        
        return df
    
    # ==========================================
    # 3. YFINANCE FALLBACK EXTRACTION
    # ==========================================
    
    def extract_from_yfinance(self, ticker: str, fiscal_year_offset: int = 0) -> Dict:
        """
        Fallback extractor using yfinance (Yahoo Finance).
        Faster but less comprehensive than SEC API.
        
        Args:
            ticker: Stock symbol
            fiscal_year_offset: Which fiscal year to extract (0=latest, 1=previous year, etc.)
        """
        if not YFINANCE_AVAILABLE:
            _logger.warning("yfinance not available for extraction")
            return {"status": "error", "message": "yfinance not installed"}
        
        _logger.info(f"Extracting from Yahoo Finance: {ticker.upper()}")
        print(f"\n[INFO] Extracting from Yahoo Finance: {ticker.upper()}")
        t0 = time.time()
        
        try:
            stock = yf.Ticker(ticker)
            
            # Get financial statements with retry logic for rate limiting
            def get_financials_with_retry():
                """Fetch financials with retry on rate limit"""
                max_retries = 3
                for attempt in range(max_retries + 1):
                    try:
                        income = stock.financials
                        bal = stock.balance_sheet
                        cf = stock.cashflow
                        return income, bal, cf
                    except Exception as e:
                        error_str = str(e).lower()
                        if 'rate limit' in error_str or 'too many requests' in error_str or '429' in error_str:
                            if attempt < max_retries:
                                delay = 2.0 * (2 ** attempt)
                                _logger.warning(f"yfinance rate limited, retry {attempt + 1}/{max_retries} after {delay:.1f}s")
                                print(f"   [RETRY] Rate limited, waiting {delay:.1f}s...")
                                time.sleep(delay)
                            else:
                                raise
                        else:
                            raise
                return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
            
            income_stmt, balance, cashflow = get_financials_with_retry()
            
            # Get historical prices (back to 1990 or IPO) with retry
            print(f"   Fetching historical prices...")
            historical_prices = pd.DataFrame()
            for attempt in range(3):
                try:
                    historical_prices = stock.history(period="max", start="1990-01-01")
                    break
                except Exception as e:
                    if 'rate limit' in str(e).lower() or '429' in str(e):
                        if attempt < 2:
                            delay = 2.0 * (2 ** attempt)
                            _logger.warning(f"yfinance history rate limited, retry after {delay:.1f}s")
                            time.sleep(delay)
                        else:
                            _logger.error(f"Failed to fetch history after retries: {e}")
                    else:
                        raise
            
            # Get current market data with explicit error handling and retry
            info = {}
            for attempt in range(3):
                try:
                    info = stock.info
                    break
                except Exception as e:
                    if 'rate limit' in str(e).lower() or '429' in str(e):
                        if attempt < 2:
                            delay = 2.0 * (2 ** attempt)
                            _logger.warning(f"yfinance info rate limited, retry after {delay:.1f}s")
                            time.sleep(delay)
                        else:
                            _logger.error(f"Failed to fetch info after retries: {e}")
                            info = {}
                    else:
                        raise
            
            current_price = info.get("currentPrice", info.get("regularMarketPrice", 0))
            shares = info.get("sharesOutstanding", 0)
            
            # Market Cap - try multiple sources with error tracking
            market_cap = None
            market_cap_error = None
            
            try:
                # Source 1: Direct from yfinance
                market_cap = info.get("marketCap")
                
                if not market_cap or market_cap == 0:
                    # Source 2: Calculate from price × shares
                    if current_price > 0 and shares > 0:
                        market_cap = current_price * shares
                        print(f"   [INFO] Market cap calculated: ${market_cap/1e9:.2f}B (price × shares)")
                    else:
                        raise ValueError(f"Cannot calculate: price={current_price}, shares={shares}")
                        
            except Exception as e:
                market_cap_error = str(e)
                market_cap = 0
                print(f"   [WARNING] Market cap unavailable: {market_cap_error}")
            
            financials = {
                "ticker": ticker.upper(),
                "company_name": info.get("longName", ticker),
                "extraction_time": f"{time.time() - t0:.2f}s",
                "income_statement": income_stmt,
                "balance_sheet": balance,
                "cash_flow": cashflow,
                "market_data": {
                    "historical_prices": historical_prices,
                    "current_price": current_price,
                    "market_cap": market_cap,
                    "shares_outstanding": shares
                },
                "info": info  # Full info dict for other uses
            }
            
            if not historical_prices.empty:
                print(f"   Historical prices: {len(historical_prices)} days from {historical_prices.index[0].date()} to {historical_prices.index[-1].date()}")
            
            # Calculate ratios and growth rates
            print(f"   Calculating financial ratios...")
            ratios_dict = self.calculate_ratios(financials, fiscal_year_offset=fiscal_year_offset)
            if "status" not in ratios_dict or ratios_dict["status"] != "error":
                # Convert ratios dict to DataFrame for consistency
                ratios_df = pd.DataFrame([ratios_dict])
                financials["ratios"] = ratios_df.T  # Transpose so ratios are rows
            
            print(f"   Calculating growth rates (CAGR)...")
            growth_dict = self.calculate_growth_rates(financials, fiscal_year_offset=fiscal_year_offset)
            if growth_dict:
                financials["growth_rates"] = growth_dict
            
            _logger.info(f"Yahoo Finance Extraction Complete for {ticker}: {financials['extraction_time']}")
            EngineLogger.log_data_extraction(ticker, success=True)
            print(f"[OK] Yahoo Finance Extraction Complete: {financials['extraction_time']}")
            return financials
            
        except Exception as e:
            _logger.error(f"yfinance extraction failed for {ticker}: {e}", exc_info=True)
            EngineLogger.log_data_extraction(ticker, success=False, error=str(e))
            return {"status": "error", "message": f"yfinance extraction failed: {e}"}
    
    # ==========================================
    # 4. SMART EXTRACTION (Multi-Source)
    # ==========================================
    
    def extract_financials(self, ticker: str, source: str = "auto", filing_types: List[str] = ["10-K"], 
                          include_quant: bool = False, fiscal_year_offset: int = 0,
                          use_cache: bool = True) -> Dict:
        """
        Smart extractor that chooses best source automatically.
        
        Args:
            ticker: Stock symbol
            source: "sec", "yfinance", or "auto" (tries SEC first)
            filing_types: List of SEC filing types ["10-K"], ["10-Q"], ["10-K", "10-Q"], ["S-1"]
            include_quant: If True, run Fama-French quant analysis
            use_cache: If True, use cached data if available and not expired
            
        Returns:
            Comprehensive financial data dictionary
        """
        # Normalize ticker (handles aliases like ZOOM->ZM, FACEBOOK->META)
        original_ticker = ticker
        ticker = normalize_ticker(ticker)
        if original_ticker.upper() != ticker:
            _logger.info(f"Ticker mapped: {original_ticker} → {ticker}")
        
        # Warn about problematic tickers
        if ticker in PROBLEMATIC_TICKERS:
            _logger.warning(f"Ticker {ticker}: {PROBLEMATIC_TICKERS[ticker]}")
        
        # Generate cache key based on parameters
        cache_key = f"{ticker}_{source}_{','.join(filing_types)}_{include_quant}_{fiscal_year_offset}"
        
        # Check cache first (if enabled)
        if use_cache:
            cached_data = self._cache_get(cache_key)
            if cached_data:
                _logger.info(f"Returning cached data for {ticker}")
                print(f"[CACHE] Using cached data for {ticker}")
                return cached_data
        
        # Capture overall start time for accurate extraction time
        self._overall_start_time = time.time()
        
        # Validate ticker first
        is_valid, result = self.validate_ticker(ticker)
        if not is_valid:
            return {"status": "error", "message": result}
        
        # AUTO mode: Try SEC first, fallback to yfinance, then FILL GAPS
        if source == "auto":
            print(f"\n[INFO] AUTO MODE: Extracting {ticker} ({result})")
            
            # Try SEC API first (most accurate)
            sec_data = self.extract_from_sec(ticker, filing_types=filing_types)
            if "status" not in sec_data or sec_data["status"] != "error":
                financials = sec_data
                primary_source = "sec"
            else:
                print("[WARN] SEC extraction failed, trying Yahoo Finance...")
                # Fallback to yfinance
                financials = self.extract_from_yfinance(ticker, fiscal_year_offset=fiscal_year_offset)
                primary_source = "yfinance"
            
            # PHASE 1: Field-level gap filling
            financials = self._fill_data_gaps(ticker, financials, primary_source)
        
        # Manual source selection
        elif source == "sec":
            financials = self.extract_from_sec(ticker, filing_types=filing_types)
        elif source == "yfinance":
            financials = self.extract_from_yfinance(ticker, fiscal_year_offset=fiscal_year_offset)
        else:
            return {"status": "error", "message": f"Unknown source: {source}"}
        
        # Add quant analysis if requested
        if include_quant and QUANT_ENGINE_AVAILABLE:
            try:
                print(f"\n[QUANT] Running Quantitative Analysis (Fama-French)...")
                quant = QuantEngine()
                quant_results = quant.analyze_stock(ticker)
                financials["quant_analysis"] = quant_results
            except Exception as e:
                print(f"[WARN] Quant analysis failed: {e}")
                financials["quant_analysis"] = {"status": "error", "message": str(e)}
        
        # Update extraction time to include quant analysis
        if "extraction_time" in financials and hasattr(self, '_overall_start_time'):
            financials["extraction_time"] = f"{time.time() - self._overall_start_time:.2f}s"
        
        # Cache the results (only if successful)
        if "status" not in financials or financials.get("status") != "error":
            self._cache_set(cache_key, financials, cache_type="financials")
            _logger.info(f"Cached financial data for {ticker}")
        
        return financials
    
    # ==========================================
    # 4B. FIELD-LEVEL GAP FILLING (PHASE 1)
    # ==========================================
    
    def _fill_data_gaps(self, ticker: str, financials: Dict, primary_source: str) -> Dict:
        """
        Fill missing fields by trying alternate sources (PHASE 1 + PHASE 2).
        
        Multi-source fusion:
        - Identifies gaps (missing/null values)
        - Tries yfinance first, then FMP for remaining gaps
        - Tracks which source provided each field
        
        Args:
            ticker: Stock symbol
            financials: Primary extraction results
            primary_source: Which source was used ('sec' or 'yfinance')
        
        Returns:
            financials dict with gaps filled
        """
        # Track sources for transparency
        if '_sources' not in financials:
            financials['_sources'] = {}
        
        # Fields to check for gaps (expanded list)
        critical_fields = [
            # Market data
            'current_price', 'market_cap', 'beta', 'average_volume',
            'fifty_two_week_high', 'fifty_two_week_low', 'shares_outstanding',
            # Valuation ratios
            'pe_ratio', 'forward_pe', 'peg_ratio', 'price_to_book', 'price_to_sales',
            'ev_to_ebitda', 'ev_to_sales', 'enterprise_value',
            # Profitability
            'roe', 'roa', 'roic', 'gross_margin', 'operating_margin', 'profit_margin',
            # Liquidity/Solvency
            'debt_to_equity', 'current_ratio', 'quick_ratio', 'interest_coverage',
            # Growth
            'revenue_growth', 'earnings_growth',
            # Dividends
            'dividend_yield', 'payout_ratio',
            # Company info
            'sector', 'industry', 'employees',
            # Analyst data
            'target_price', 'target_price_avg', 'recommendation', 'eps_estimate_avg',
            # FMP special
            'fmp_rating', 'fmp_rating_score', 'graham_number',
        ]
        
        # Identify gaps
        gaps = []
        for field in critical_fields:
            value = financials.get(field)
            if value is None or value == 'N/A' or value == '' or value == 0:
                gaps.append(field)
        
        if not gaps:
            print(f"   [GAP FILL] No gaps detected")
            return financials
        
        print(f"   [GAP FILL] Found {len(gaps)} gaps: {', '.join(gaps[:5])}{'...' if len(gaps) > 5 else ''}")
        
        gaps_filled_yf = 0
        gaps_filled_fmp = 0
        remaining_gaps = gaps.copy()
        
        # ========== STEP 1: Try yfinance for gaps ==========
        if YFINANCE_AVAILABLE and primary_source != 'yfinance':
            try:
                stock = yf.Ticker(ticker)
                info = stock.info
                
                yf_field_map = {
                    'current_price': ['currentPrice', 'regularMarketPrice'],
                    'market_cap': ['marketCap'],
                    'pe_ratio': ['trailingPE'],
                    'forward_pe': ['forwardPE'],
                    'peg_ratio': ['pegRatio'],
                    'price_to_book': ['priceToBook'],
                    'price_to_sales': ['priceToSalesTrailing12Months'],
                    'roe': ['returnOnEquity'],
                    'roa': ['returnOnAssets'],
                    'debt_to_equity': ['debtToEquity'],
                    'current_ratio': ['currentRatio'],
                    'quick_ratio': ['quickRatio'],
                    'revenue_growth': ['revenueGrowth'],
                    'earnings_growth': ['earningsGrowth'],
                    'dividend_yield': ['dividendYield'],
                    'beta': ['beta'],
                    'sector': ['sector'],
                    'industry': ['industry'],
                    'employees': ['fullTimeEmployees'],
                    'fifty_two_week_high': ['fiftyTwoWeekHigh'],
                    'fifty_two_week_low': ['fiftyTwoWeekLow'],
                    'shares_outstanding': ['sharesOutstanding'],
                    'target_price': ['targetMeanPrice'],
                    'recommendation': ['recommendationKey'],
                    'enterprise_value': ['enterpriseValue'],
                    'average_volume': ['averageVolume'],
                    'gross_margin': ['grossMargins'],
                    'operating_margin': ['operatingMargins'],
                    'profit_margin': ['profitMargins'],
                    'payout_ratio': ['payoutRatio'],
                }
                
                for field in gaps:
                    yf_keys = yf_field_map.get(field, [field])
                    for yf_key in yf_keys:
                        value = info.get(yf_key)
                        if value is not None and value != '' and value != 0:
                            financials[field] = value
                            financials['_sources'][field] = 'yfinance'
                            gaps_filled_yf += 1
                            if field in remaining_gaps:
                                remaining_gaps.remove(field)
                            break
                
                if gaps_filled_yf > 0:
                    print(f"   [GAP FILL] Filled {gaps_filled_yf} gaps from yfinance")
                
            except Exception as e:
                print(f"   [GAP FILL] yfinance fallback failed: {e}")
        
        # ========== STEP 2: Try FMP for remaining gaps (if available) ==========
        if FMP_AVAILABLE and remaining_gaps:
            try:
                fmp = get_fmp_extractor()
                if fmp.available:
                    fmp_data = fmp.extract_all(ticker)
                    
                    if fmp_data and len(fmp_data) > 0:
                        for field in list(remaining_gaps):
                            value = fmp_data.get(field)
                            if value is not None and value != '' and value != 0:
                                financials[field] = value
                                financials['_sources'][field] = 'fmp'
                                gaps_filled_fmp += 1
                                remaining_gaps.remove(field)
                        
                        if gaps_filled_fmp > 0:
                            print(f"   [GAP FILL] Filled {gaps_filled_fmp} gaps from FMP")
            except Exception:
                pass  # FMP failed silently
        
        # ========== STEP 3: Try Alpha Vantage for remaining gaps ==========
        gaps_filled_av = 0
        if ALPHAVANTAGE_AVAILABLE and remaining_gaps:
            try:
                av = get_alphavantage_extractor()
                if av.available:
                    av_data = av.extract_all(ticker)
                    
                    if av_data and len(av_data) > 0:
                        for field in list(remaining_gaps):
                            value = av_data.get(field)
                            if value is not None and value != '' and value != 0:
                                financials[field] = value
                                financials['_sources'][field] = 'alphavantage'
                                gaps_filled_av += 1
                                remaining_gaps.remove(field)
                        
                        if gaps_filled_av > 0:
                            print(f"   [GAP FILL] Filled {gaps_filled_av} gaps from Alpha Vantage")
            except Exception:
                pass  # Alpha Vantage failed silently
        
        total_filled = gaps_filled_yf + gaps_filled_fmp + gaps_filled_av
        if total_filled > 0:
            print(f"   [GAP FILL] Total: {total_filled}/{len(gaps)} gaps filled")
        
        return financials
    
    # ==========================================
    # 5. DATA ENRICHMENT & CALCULATIONS
    # ==========================================
    
    def calculate_ratios(self, financials: Dict, fiscal_year_offset: int = 0) -> Dict:
        """
        Calculate financial ratios from extracted data.
        
        Args:
            financials: Financial data dictionary
            fiscal_year_offset: Which fiscal year to use (0=latest, 1=previous year, etc.)
        
        Returns dictionary of key metrics.
        """
        ratios = {}
        
        try:
            # Get latest year data
            income = financials.get("income_statement", pd.DataFrame())
            balance = financials.get("balance_sheet", pd.DataFrame())
            cashflow = financials.get("cash_flow", pd.DataFrame())
            info = financials.get("info", {})  # Needed for market P/E and D/E
            
            if income.empty:
                return {"status": "error", "message": "No income statement data"}
            
            # Helper function to get metric value (handles both SEC and yfinance formats)
            def get_metric(df, possible_names, default=0):
                if df.empty:
                    return default
                
                # yfinance format: metrics as index, dates as columns
                if isinstance(df.index[0], str):
                    for name in possible_names:
                        if name in df.index:
                            # Use fiscal_year_offset to select column
                            col_idx = min(fiscal_year_offset, len(df.columns) - 1)
                            val = df.loc[name].iloc[col_idx]
                            return val if pd.notnull(val) else default
                # SEC format: dates as index, metrics as columns
                else:
                    for name in possible_names:
                        if name in df.columns:
                            # Use fiscal_year_offset to select row
                            row_idx = min(fiscal_year_offset, len(df) - 1)
                            val = df.iloc[row_idx][name]
                            return val if pd.notnull(val) else default
                return default
            
            # Extract metrics with multiple possible field names
            revenue = get_metric(income, ["Total Revenue", "Revenue", "Sales Revenue Net"])
            gross_profit = get_metric(income, ["Gross Profit", "GrossProfit"])
            operating_income = get_metric(income, ["Operating Income", "EBIT", "Operating Income Or Loss"])
            net_income = get_metric(income, ["Net Income", "Normalized Income", "Net Income From Continuing Operation Net Minority Interest"])
            
            total_assets = get_metric(balance, ["Total Assets", "TotalAssets"])
            total_equity = get_metric(balance, ["Stockholders Equity", "Total Equity", "Total Stockholders Equity"])
            total_liabilities = get_metric(balance, ["Total Liabilities", "TotalLiabilitiesNetMinorityInterest", "Total Liabilities Net Minority Interest"])
            total_debt = get_metric(balance, ["Total Debt", "TotalDebt", "Long Term Debt And Capital Lease Obligation"])
            current_assets = get_metric(balance, ["Current Assets", "TotalCurrentAssets", "Total Current Assets"])
            current_liabilities = get_metric(balance, ["Current Liabilities", "TotalCurrentLiabilities", "Total Current Liabilities"])
            
            op_cash_flow = get_metric(cashflow, ["Operating Cash Flow", "Cash Flow From Operating Activities"])
            capex = get_metric(cashflow, ["Capital Expenditure", "Capex"])
            free_cash_flow_direct = get_metric(cashflow, ["Free Cash Flow", "FreeCashFlow"])  # Try to get FCF directly
            
            # Calculate ratios (as decimals, not percentages)
            if revenue > 0:
                if gross_profit > 0:
                    ratios["Gross_Margin"] = (gross_profit / revenue)
                if operating_income > 0:
                    ratios["Operating_Margin"] = (operating_income / revenue)
                if net_income > 0:
                    ratios["Net_Margin"] = (net_income / revenue)
            
            if total_equity > 0 and net_income > 0:
                ratios["ROE"] = (net_income / total_equity)
            
            if total_assets > 0 and net_income > 0:
                ratios["ROA"] = (net_income / total_assets)
            
            # Debt to Equity - prefer market data, flag discrepancies
            market_de = info.get('debtToEquity')  # Yahoo Finance value (as percentage)
            calculated_de = None
            
            if total_equity > 0 and total_liabilities > 0:
                calculated_de = total_liabilities / total_equity
            
            if market_de is not None and market_de > 0:
                ratios["Debt_to_Equity"] = market_de / 100  # Convert from percentage
                ratios["Debt_to_Equity_Source"] = "market"
                ratios["Debt_to_Equity_Calculated"] = calculated_de
                
                # Flag significant discrepancies
                if calculated_de and abs(market_de/100 - calculated_de) / (market_de/100) > 0.15:
                    ratios["Debt_to_Equity_Warning"] = f"Market D/E ({market_de/100:.2f}) differs from statement-based ({calculated_de:.2f})"
            elif calculated_de is not None:
                ratios["Debt_to_Equity"] = calculated_de
                ratios["Debt_to_Equity_Source"] = "calculated"
            
            ratios["Debt_to_Equity_Timestamp"] = datetime.now().isoformat()
            
            if current_liabilities > 0 and current_assets > 0:
                ratios["Current_Ratio"] = current_assets / current_liabilities
            
            # Free Cash Flow: Try direct value first, then calculate
            if free_cash_flow_direct != 0:
                ratios["Free_Cash_Flow"] = free_cash_flow_direct
            elif op_cash_flow != 0:  # Changed from > 0 to != 0 to handle banks with negative OCF
                ratios["Free_Cash_Flow"] = op_cash_flow - abs(capex) if capex else op_cash_flow
            
            # Get market data for valuation ratios (from yfinance)
            market_data = financials.get('market_data', {})
            current_price = market_data.get('current_price', 0)
            market_cap = market_data.get('market_cap', 0)
            shares_outstanding = market_data.get('shares_outstanding', 0)
            
            # Calculate valuation multiples if market data available
            if current_price > 0:
                ratios["Current_Price"] = current_price
                
                # PE Ratio - prefer trailing P/E from market
                market_pe = info.get('trailingPE')  # Yahoo's calculated TTM P/E
                calculated_pe = None
                
                if net_income > 0 and shares_outstanding > 0:
                    eps = net_income / shares_outstanding
                    if eps > 0:
                        calculated_pe = current_price / eps
                
                # Prefer market P/E (uses TTM data)
                if market_pe is not None and market_pe > 0:
                    ratios["PE_Ratio"] = market_pe
                    ratios["PE_Ratio_Source"] = "market_ttm"
                    ratios["PE_Ratio_Calculated"] = calculated_pe
                    
                    # Flag significant discrepancies (>10%)
                    if calculated_pe and abs(market_pe - calculated_pe) / market_pe > 0.10:
                        ratios["PE_Ratio_Warning"] = f"Market P/E ({market_pe:.1f}x) differs from annual-based ({calculated_pe:.1f}x)"
                elif calculated_pe:
                    ratios["PE_Ratio"] = calculated_pe
                    ratios["PE_Ratio_Source"] = "calculated_annual"
                
                ratios["PE_Ratio_Timestamp"] = datetime.now().isoformat()
                
                # Price to Book
                if total_equity > 0 and shares_outstanding > 0:
                    book_value_per_share = total_equity / shares_outstanding
                    if book_value_per_share > 0:
                        ratios["Price_to_Book"] = current_price / book_value_per_share
                
                # Price to Sales
                if revenue > 0 and shares_outstanding > 0:
                    sales_per_share = revenue / shares_outstanding
                    if sales_per_share > 0:
                        ratios["Price_to_Sales"] = current_price / sales_per_share
            
            # EV-based multiples (if we have debt and cash)
            if market_cap > 0:
                cash = get_metric(balance, ["Cash And Cash Equivalents", "Cash", "CashAndCashEquivalentsAtCarryingValue"])
                enterprise_value = market_cap + total_debt - cash
                
                if enterprise_value > 0:
                    # EV/Revenue
                    if revenue > 0:
                        ratios["EV_to_Sales"] = enterprise_value / revenue
                    
                    # EV/EBITDA (approximate EBITDA as Operating Income)
                    if operating_income > 0:
                        ratios["EV_to_EBITDA"] = enterprise_value / operating_income
                    
                    # EV/EBIT (same as EV/Operating Income)
                    if operating_income > 0:
                        ratios["EV_to_EBIT"] = enterprise_value / operating_income
            
            # PEG Ratio (P/E / Growth Rate)
            pe_ratio = ratios.get("PE_Ratio")
            # Try to get earnings growth from info
            earnings_growth = info.get('earningsGrowth')  # As decimal
            if pe_ratio and earnings_growth and earnings_growth > 0:
                # Convert growth to percentage for PEG calculation
                earnings_growth_pct = earnings_growth * 100
                if earnings_growth_pct > 0:
                    ratios["PEG_Ratio"] = pe_ratio / earnings_growth_pct
            elif pe_ratio:
                # Fallback: use revenue growth if available
                revenue_growth = info.get('revenueGrowth')
                if revenue_growth and revenue_growth > 0:
                    revenue_growth_pct = revenue_growth * 100
                    if revenue_growth_pct > 0:
                        ratios["PEG_Ratio"] = pe_ratio / revenue_growth_pct
            
            # Store raw values for reference
            ratios["Revenue"] = revenue
            ratios["Net_Income"] = net_income
            ratios["Total_Assets"] = total_assets
            ratios["Total_Equity"] = total_equity
            
            # Set defaults for any missing ratios
            for key in ["Gross_Margin", "Operating_Margin", "Net_Margin", "ROE", "ROA", "Debt_to_Equity", "Current_Ratio", "Free_Cash_Flow"]:
                if key not in ratios:
                    ratios[key] = 0
            
            # Store component values for tooltip breakdowns
            ratios["_components"] = {
                "revenue": revenue,
                "gross_profit": gross_profit,
                "operating_income": operating_income,
                "net_income": net_income,
                "total_assets": total_assets,
                "total_equity": total_equity,
                "total_liabilities": total_liabilities,
                "total_debt": total_debt,
                "current_assets": current_assets,
                "current_liabilities": current_liabilities,
                "op_cash_flow": op_cash_flow,
                "capex": capex
            }
            
            return ratios
            
        except Exception as e:
            return {"status": "error", "message": f"Ratio calculation failed: {e}"}
    
    # ==========================================
    # 6. MULTI-YEAR TREND ANALYSIS
    # ==========================================
    
    def calculate_growth_rates(self, financials: Dict, years: int = 5, fiscal_year_offset: int = 0, 
                              period_type: str = "annual") -> Dict:
        """
        Calculate growth rates for key metrics over specified period.
        Handles both SEC (columns) and yfinance (index) formats.
        Handles both annual (10-K) and quarterly (10-Q) data.
        
        Args:
            financials: Financial data dict
            years: Number of years to calculate CAGR
            fiscal_year_offset: Which fiscal year to use
            period_type: "annual" (10-K) or "quarterly" (10-Q)
        
        Returns:
            Dict with CAGR, YoY change, QoQ change (if quarterly)
        """
        growth = {}
        is_quarterly = (period_type == "quarterly")
        
        try:
            income = financials.get("income_statement", pd.DataFrame())
            if income.empty:
                return {"status": "error", "message": "No income statement data"}
            
            # Helper to get time series for a metric
            def get_time_series(df, possible_names):
                if df.empty:
                    return None
                
                # yfinance format: metrics as index, dates as columns
                if isinstance(df.index[0], str):
                    for name in possible_names:
                        if name in df.index:
                            # Get all columns (time series) for this metric
                            series = df.loc[name]
                            return series.dropna().sort_index()  # Sort by date
                # SEC format: dates as index, metrics as columns
                else:
                    for name in possible_names:
                        if name in df.columns:
                            series = df[name]
                            return series.dropna().sort_index(ascending=False)  # Most recent first
                return None
            
            # Calculate CAGR for key metrics (comprehensive list)
            metrics_map = {
                "Total_Revenue": ["Total Revenue", "Revenue", "Sales Revenue Net"],
                "COGS": ["Cost Of Revenue", "Cost Of Goods Sold", "Reconciled Cost Of Revenue"],
                "Gross_Profit": ["Gross Profit", "GrossProfit"],
                "SGA_Expenses": ["Selling General And Administration", "SG&A", "Selling General Administrative"],
                "Total_Operating_Expenses": ["Operating Expense", "Total Operating Expenses", "Operating Expenses"],
                "Operating_Profit": ["Operating Income", "EBIT", "Operating Profit"],
                "Net_Income": ["Net Income", "Normalized Income", "Net Income From Continuing Operation Net Minority Interest"]
            }
            
            # Store operating profit series for NOPAT calculation later
            operating_profit_series = None
            tax_expense_series = None
            
            for metric_name, possible_names in metrics_map.items():
                series = get_time_series(income, possible_names)
                
                # Store operating profit for NOPAT calculation
                if metric_name == "Operating_Profit" and series is not None:
                    operating_profit_series = series
                
                if series is not None and len(series) >= 2:
                    # Most recent vs oldest
                    latest = series.iloc[-1] if isinstance(income.index[0], str) else series.iloc[0]
                    oldest = series.iloc[0] if isinstance(income.index[0], str) else series.iloc[-1]
                    n_years = len(series) - 1
                    
                    if oldest > 0 and latest > 0 and n_years > 0:
                        # Calculate CAGR (always useful)
                        cagr = ((latest / oldest) ** (1 / n_years) - 1) * 100
                        
                        # Cap extreme values (likely data errors)
                        if abs(cagr) > 1000:  # More than 1000% is likely an error
                            cagr = None
                        
                        if cagr is not None:
                            growth[f"{metric_name}_CAGR"] = round(cagr, 2)
                        
                        # Calculate dollar change and percent change
                        dollar_change = latest - oldest
                        pct_change = ((latest / oldest) - 1) * 100
                        
                        # Cap percent change too
                        if abs(pct_change) > 1000:
                            pct_change = None
                        
                        growth[f"{metric_name}_Dollar_Change"] = dollar_change
                        if pct_change is not None:
                            growth[f"{metric_name}_Pct_Change"] = round(pct_change, 2)
                        growth[f"{metric_name}_Latest_Value"] = latest
                        growth[f"{metric_name}_Oldest_Value"] = oldest
                        
                        # For quarterly data, also calculate QoQ and YoY
                        if is_quarterly and len(series) >= 2:
                            # Quarter-over-Quarter (most recent vs previous quarter)
                            if len(series) >= 2:
                                current_q = series.iloc[-1] if isinstance(income.index[0], str) else series.iloc[0]
                                prev_q = series.iloc[-2] if isinstance(income.index[0], str) else series.iloc[1]
                                
                                if prev_q > 0:
                                    qoq_growth = ((current_q / prev_q) - 1) * 100
                                    growth[f"{metric_name}_QoQ"] = round(qoq_growth, 2)
                            
                            # Year-over-Year (same quarter, previous year)
                            if len(series) >= 5:  # Need at least 5 quarters (1 year + 1 quarter)
                                current_q = series.iloc[-1] if isinstance(income.index[0], str) else series.iloc[0]
                                yoy_q = series.iloc[-5] if isinstance(income.index[0], str) else series.iloc[4]
                                
                                if yoy_q > 0:
                                    yoy_growth = ((current_q / yoy_q) - 1) * 100
                                    growth[f"{metric_name}_YoY"] = round(yoy_growth, 2)
            
            # ==========================================
            # CALCULATE NOPAT (Net Operating Profit After Tax)
            # NOPAT = Operating Income × (1 - Tax Rate)
            # ==========================================
            if operating_profit_series is not None and len(operating_profit_series) >= 2:
                # Get tax expense to calculate effective tax rate
                tax_expense_series = get_time_series(income, ["Tax Provision", "Income Tax Expense", "Tax Expense"])
                pretax_income_series = get_time_series(income, ["Pretax Income", "Income Before Tax", "EBT"])
                
                # Calculate effective tax rate (use 21% default if not available)
                effective_tax_rate = 0.21  # Default US corporate rate
                if tax_expense_series is not None and pretax_income_series is not None:
                    try:
                        latest_tax = tax_expense_series.iloc[-1] if isinstance(income.index[0], str) else tax_expense_series.iloc[0]
                        latest_pretax = pretax_income_series.iloc[-1] if isinstance(income.index[0], str) else pretax_income_series.iloc[0]
                        if latest_pretax > 0 and latest_tax > 0:
                            effective_tax_rate = latest_tax / latest_pretax
                            effective_tax_rate = min(max(effective_tax_rate, 0.10), 0.40)  # Cap between 10-40%
                    except (KeyError, IndexError, TypeError, ZeroDivisionError):
                        # Use default US corporate tax rate if calculation fails
                        effective_tax_rate = 0.21
                
                # Calculate NOPAT series
                nopat_series = operating_profit_series * (1 - effective_tax_rate)
                
                if len(nopat_series) >= 2:
                    latest_nopat = nopat_series.iloc[-1] if isinstance(income.index[0], str) else nopat_series.iloc[0]
                    oldest_nopat = nopat_series.iloc[0] if isinstance(income.index[0], str) else nopat_series.iloc[-1]
                    n_years = len(nopat_series) - 1
                    
                    if oldest_nopat > 0 and latest_nopat > 0 and n_years > 0:
                        # CAGR
                        nopat_cagr = ((latest_nopat / oldest_nopat) ** (1 / n_years) - 1) * 100
                        if abs(nopat_cagr) <= 1000:
                            growth["NOPAT_CAGR"] = round(nopat_cagr, 2)
                        
                        # Dollar and percent change
                        growth["NOPAT_Dollar_Change"] = latest_nopat - oldest_nopat
                        pct_change = ((latest_nopat / oldest_nopat) - 1) * 100
                        if abs(pct_change) <= 1000:
                            growth["NOPAT_Pct_Change"] = round(pct_change, 2)
                        growth["NOPAT_Latest_Value"] = latest_nopat
                        growth["NOPAT_Oldest_Value"] = oldest_nopat
                        growth["NOPAT_Effective_Tax_Rate"] = round(effective_tax_rate * 100, 1)
            
            return growth if growth else {"status": "error", "message": "Could not calculate growth rates"}
            
        except Exception as e:
            return {"status": "error", "message": f"Growth calculation failed: {e}"}


# === CONVENIENCE FUNCTIONS ===
def quick_extract(ticker: str, filing_types: List[str] = ["10-K"], include_quant: bool = False, 
                  fiscal_year_offset: int = 0) -> Dict:
    """
    One-line function to extract all financial data.
    
    Args:
        ticker: Stock symbol
        filing_types: ["10-K"] for annual, ["10-Q"] for quarterly, ["10-K", "10-Q"] for both
        include_quant: If True, includes Fama-French quantitative analysis
        fiscal_year_offset: Which fiscal year to extract (0=latest, 1=previous year, etc.)
    
    Usage:
        # Annual only (latest fiscal year)
        data = quick_extract("AAPL")
        
        # Previous fiscal year (for validation against historical 10-K)
        data = quick_extract("AAPL", fiscal_year_offset=1)
        
        # Annual + Quarterly
        data = quick_extract("MSFT", filing_types=["10-K", "10-Q"])
        
        # With quant analysis
        data = quick_extract("GOOGL", include_quant=True)
        print(f"Cost of Equity: {data['quant_analysis']['fama_french']['cost_of_equity_annual']*100:.2f}%")
    """
    extractor = USAFinancialExtractor()
    return extractor.extract_financials(ticker, filing_types=filing_types, include_quant=include_quant, 
                                       fiscal_year_offset=fiscal_year_offset)

