"""
FINANCIAL MODELING PREP (FMP) DATA EXTRACTOR
=============================================
Third data source for multi-source fusion architecture.

FMP Free Tier: 250 API calls/day
Best for: Fundamentals, ratios, historical data, analyst estimates

API Docs: https://site.financialmodelingprep.com/developer/docs
"""

import os
import requests
import time
from datetime import datetime
from typing import Dict, Optional, List, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import logging
try:
    from utils.logging_config import EngineLogger
    _logger = EngineLogger.get_logger("FMPExtractor")
except ImportError:
    import logging
    _logger = logging.getLogger("FMPExtractor")


class FMPExtractor:
    """
    Financial Modeling Prep API extractor.
    
    Free tier: 250 calls/day
    Endpoints used:
    - /profile: Company info
    - /ratios: Financial ratios
    - /key-metrics: Key metrics
    - /income-statement: Income statement
    - /balance-sheet-statement: Balance sheet
    - /cash-flow-statement: Cash flow
    - /analyst-estimates: Analyst estimates
    """
    
    BASE_URL = "https://financialmodelingprep.com/api/v3"
    
    # Field mapping: FMP field name -> our standard field name
    FIELD_MAP = {
        # Profile
        'symbol': 'ticker',
        'companyName': 'company_name',
        'sector': 'sector',
        'industry': 'industry',
        'fullTimeEmployees': 'employees',
        'description': 'description',
        'ceo': 'ceo',
        'country': 'country',
        'exchange': 'exchange',
        'currency': 'currency',
        'mktCap': 'market_cap',
        'price': 'current_price',
        'beta': 'beta',
        'volAvg': 'average_volume',
        'lastDiv': 'last_dividend',
        'range': 'fifty_two_week_range',
        'ipoDate': 'ipo_date',
        
        # Ratios
        'peRatioTTM': 'pe_ratio',
        'pegRatioTTM': 'peg_ratio',
        'priceToBookRatioTTM': 'price_to_book',
        'priceToSalesRatioTTM': 'price_to_sales',
        'dividendYielTTM': 'dividend_yield',
        'dividendYieldTTM': 'dividend_yield',
        'returnOnEquityTTM': 'roe',
        'returnOnAssetsTTM': 'roa',
        'debtEquityRatioTTM': 'debt_to_equity',
        'currentRatioTTM': 'current_ratio',
        'quickRatioTTM': 'quick_ratio',
        'grossProfitMarginTTM': 'gross_margin',
        'operatingProfitMarginTTM': 'operating_margin',
        'netProfitMarginTTM': 'profit_margin',
        'freeCashFlowPerShareTTM': 'fcf_per_share',
        'cashPerShareTTM': 'cash_per_share',
        'revenuePerShareTTM': 'revenue_per_share',
        'interestCoverageTTM': 'interest_coverage',
        
        # Key Metrics
        'revenuePerShare': 'revenue_per_share',
        'netIncomePerShare': 'eps',
        'operatingCashFlowPerShare': 'ocf_per_share',
        'freeCashFlowPerShare': 'fcf_per_share',
        'cashPerShare': 'cash_per_share',
        'bookValuePerShare': 'book_value',
        'tangibleBookValuePerShare': 'tangible_book_value',
        'shareholdersEquityPerShare': 'equity_per_share',
        'interestDebtPerShare': 'debt_per_share',
        'marketCap': 'market_cap',
        'enterpriseValue': 'enterprise_value',
        'peRatio': 'pe_ratio',
        'priceToSalesRatio': 'price_to_sales',
        'pocfratio': 'price_to_ocf',
        'pfcfRatio': 'price_to_fcf',
        'pbRatio': 'price_to_book',
        'ptbRatio': 'price_to_tangible_book',
        'evToSales': 'ev_to_sales',
        'enterpriseValueOverEBITDA': 'ev_to_ebitda',
        'evToOperatingCashFlow': 'ev_to_ocf',
        'evToFreeCashFlow': 'ev_to_fcf',
        'earningsYield': 'earnings_yield',
        'freeCashFlowYield': 'fcf_yield',
        'debtToEquity': 'debt_to_equity',
        'debtToAssets': 'debt_to_assets',
        'netDebtToEBITDA': 'net_debt_to_ebitda',
        'currentRatio': 'current_ratio',
        'interestCoverage': 'interest_coverage',
        'incomeQuality': 'income_quality',
        'dividendYield': 'dividend_yield',
        'payoutRatio': 'payout_ratio',
        'salesGeneralAndAdministrativeToRevenue': 'sga_to_revenue',
        'researchAndDevelopementToRevenue': 'rd_to_revenue',
        'intangiblesToTotalAssets': 'intangibles_ratio',
        'capexToOperatingCashFlow': 'capex_to_ocf',
        'capexToRevenue': 'capex_to_revenue',
        'capexToDepreciation': 'capex_to_depreciation',
        'stockBasedCompensationToRevenue': 'sbc_to_revenue',
        'grahamNumber': 'graham_number',
        'roic': 'roic',
        'returnOnTangibleAssets': 'rota',
        'grahamNetNet': 'graham_net_net',
        'workingCapital': 'working_capital',
        'tangibleAssetValue': 'tangible_assets',
        'netCurrentAssetValue': 'ncav',
        'investedCapital': 'invested_capital',
        'averageReceivables': 'avg_receivables',
        'averagePayables': 'avg_payables',
        'averageInventory': 'avg_inventory',
        'daysSalesOutstanding': 'dso',
        'daysPayablesOutstanding': 'dpo',
        'daysOfInventoryOnHand': 'dio',
        'receivablesTurnover': 'receivables_turnover',
        'payablesTurnover': 'payables_turnover',
        'inventoryTurnover': 'inventory_turnover',
        'roe': 'roe',
        'capexPerShare': 'capex_per_share',
        
        # Analyst Estimates
        'estimatedRevenueLow': 'revenue_estimate_low',
        'estimatedRevenueHigh': 'revenue_estimate_high',
        'estimatedRevenueAvg': 'revenue_estimate_avg',
        'estimatedEbitdaLow': 'ebitda_estimate_low',
        'estimatedEbitdaHigh': 'ebitda_estimate_high',
        'estimatedEbitdaAvg': 'ebitda_estimate_avg',
        'estimatedEpsLow': 'eps_estimate_low',
        'estimatedEpsHigh': 'eps_estimate_high',
        'estimatedEpsAvg': 'eps_estimate_avg',
        'estimatedNetIncomeLow': 'net_income_estimate_low',
        'estimatedNetIncomeHigh': 'net_income_estimate_high',
        'estimatedNetIncomeAvg': 'net_income_estimate_avg',
        'estimatedSgaExpenseLow': 'sga_estimate_low',
        'estimatedSgaExpenseHigh': 'sga_estimate_high',
        'estimatedSgaExpenseAvg': 'sga_estimate_avg',
        'numberAnalystEstimatedRevenue': 'num_analysts_revenue',
        'numberAnalystsEstimatedEps': 'num_analysts_eps',
    }
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize FMP extractor.
        
        Args:
            api_key: FMP API key. If not provided, reads from FMP_API_KEY env var.
        """
        self.api_key = api_key or os.getenv('FMP_API_KEY')
        self.available = bool(self.api_key)
        
        if not self.available:
            print("[FMP] No API key found. Set FMP_API_KEY in .env to enable.")
        else:
            print(f"[FMP] Initialized with API key: {self.api_key[:8]}...")
        
        # Rate limiting
        self._last_request_time = 0
        self._min_request_interval = 0.5  # 500ms between requests
        self._daily_calls = 0
        self._daily_limit = 250
        self._last_reset_date = datetime.now().date()
    
    def _check_rate_limit(self) -> bool:
        """Check if we're within rate limits."""
        # Reset daily counter if new day
        if datetime.now().date() != self._last_reset_date:
            self._daily_calls = 0
            self._last_reset_date = datetime.now().date()
        
        return self._daily_calls < self._daily_limit
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """
        Make API request with rate limiting.
        
        Args:
            endpoint: API endpoint (e.g., '/profile/AAPL')
            params: Additional query parameters
        
        Returns:
            JSON response or None if failed
        """
        if not self.available:
            return None
        
        if not self._check_rate_limit():
            print(f"[FMP] Daily limit reached ({self._daily_limit} calls)")
            return None
        
        # Rate limiting - wait if needed
        elapsed = time.time() - self._last_request_time
        if elapsed < self._min_request_interval:
            time.sleep(self._min_request_interval - elapsed)
        
        # Build URL
        url = f"{self.BASE_URL}{endpoint}"
        
        # Add API key
        if params is None:
            params = {}
        params['apikey'] = self.api_key
        
        try:
            response = requests.get(url, params=params, timeout=10)
            self._last_request_time = time.time()
            self._daily_calls += 1
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                print("[FMP] Invalid API key")
                self.available = False
                return None
            elif response.status_code == 403:
                # FMP changed their API - v3 is now legacy/paid only
                if not hasattr(self, '_403_warned'):
                    print("[FMP] API requires paid subscription (v3 endpoints deprecated)")
                    self._403_warned = True
                self.available = False
                return None
            elif response.status_code == 429:
                print("[FMP] Rate limited")
                return None
            else:
                print(f"[FMP] API error: {response.status_code}")
                return None
                
        except requests.exceptions.Timeout:
            print("[FMP] Request timeout")
            return None
        except requests.exceptions.RequestException as e:
            print(f"[FMP] Request failed: {e}")
            return None
    
    def get_profile(self, ticker: str) -> Dict:
        """Get company profile."""
        data = self._make_request(f"/profile/{ticker.upper()}")
        if data and isinstance(data, list) and len(data) > 0:
            return self._map_fields(data[0])
        return {}
    
    def get_ratios_ttm(self, ticker: str) -> Dict:
        """Get trailing twelve months ratios."""
        data = self._make_request(f"/ratios-ttm/{ticker.upper()}")
        if data and isinstance(data, list) and len(data) > 0:
            return self._map_fields(data[0])
        return {}
    
    def get_key_metrics_ttm(self, ticker: str) -> Dict:
        """Get trailing twelve months key metrics."""
        data = self._make_request(f"/key-metrics-ttm/{ticker.upper()}")
        if data and isinstance(data, list) and len(data) > 0:
            return self._map_fields(data[0])
        return {}
    
    def get_analyst_estimates(self, ticker: str) -> Dict:
        """Get analyst estimates for next year."""
        data = self._make_request(f"/analyst-estimates/{ticker.upper()}", {'limit': 1})
        if data and isinstance(data, list) and len(data) > 0:
            return self._map_fields(data[0])
        return {}
    
    def get_price_target(self, ticker: str) -> Dict:
        """Get analyst price targets."""
        data = self._make_request(f"/price-target-consensus/{ticker.upper()}")
        if data and isinstance(data, list) and len(data) > 0:
            return {
                'target_price_low': data[0].get('targetLow'),
                'target_price_high': data[0].get('targetHigh'),
                'target_price_avg': data[0].get('targetConsensus'),
                'target_price_median': data[0].get('targetMedian'),
            }
        return {}
    
    def get_rating(self, ticker: str) -> Dict:
        """Get company rating/score."""
        data = self._make_request(f"/rating/{ticker.upper()}")
        if data and isinstance(data, list) and len(data) > 0:
            return {
                'fmp_rating': data[0].get('rating'),
                'fmp_rating_score': data[0].get('ratingScore'),
                'fmp_rating_recommendation': data[0].get('ratingRecommendation'),
                'dcf_score': data[0].get('ratingDetailsDCFScore'),
                'roe_score': data[0].get('ratingDetailsROEScore'),
                'roa_score': data[0].get('ratingDetailsROAScore'),
                'de_score': data[0].get('ratingDetailsDEScore'),
                'pe_score': data[0].get('ratingDetailsPEScore'),
                'pb_score': data[0].get('ratingDetailsPBScore'),
            }
        return {}
    
    def _map_fields(self, data: Dict) -> Dict:
        """Map FMP field names to our standard field names."""
        mapped = {}
        for fmp_key, value in data.items():
            if fmp_key in self.FIELD_MAP:
                our_key = self.FIELD_MAP[fmp_key]
                if value is not None and value != '':
                    mapped[our_key] = value
            else:
                # Keep unmapped fields with fmp_ prefix
                if value is not None and value != '':
                    mapped[f'fmp_{fmp_key}'] = value
        return mapped
    
    def extract_all(self, ticker: str) -> Dict:
        """
        Extract all available data for a ticker.
        
        Makes 5-6 API calls (profile, ratios, metrics, estimates, targets, rating).
        
        Args:
            ticker: Stock symbol
        
        Returns:
            Combined dict of all extracted data
        """
        if not self.available:
            return {'status': 'error', 'message': 'FMP API key not configured'}
        
        print(f"[FMP] Extracting data for {ticker.upper()}...")
        result = {}
        
        # Profile (company info, price, market cap)
        profile = self.get_profile(ticker)
        result.update(profile)
        
        # TTM Ratios
        ratios = self.get_ratios_ttm(ticker)
        result.update(ratios)
        
        # Key Metrics
        metrics = self.get_key_metrics_ttm(ticker)
        result.update(metrics)
        
        # Analyst Estimates
        estimates = self.get_analyst_estimates(ticker)
        result.update(estimates)
        
        # Price Targets
        targets = self.get_price_target(ticker)
        result.update(targets)
        
        # Rating
        rating = self.get_rating(ticker)
        result.update(rating)
        
        print(f"[FMP] Extracted {len(result)} fields for {ticker.upper()}")
        
        return result
    
    def get_field(self, ticker: str, field: str) -> Optional[Any]:
        """
        Get a specific field value.
        
        Used for gap filling - only fetches what's needed.
        
        Args:
            ticker: Stock symbol
            field: Our standard field name
        
        Returns:
            Field value or None
        """
        if not self.available:
            return None
        
        # Determine which endpoint has this field
        profile_fields = {'ticker', 'company_name', 'sector', 'industry', 'employees', 
                         'description', 'ceo', 'country', 'exchange', 'currency',
                         'market_cap', 'current_price', 'beta', 'average_volume',
                         'last_dividend', 'ipo_date'}
        
        ratio_fields = {'pe_ratio', 'peg_ratio', 'price_to_book', 'price_to_sales',
                       'dividend_yield', 'roe', 'roa', 'debt_to_equity', 'current_ratio',
                       'quick_ratio', 'gross_margin', 'operating_margin', 'profit_margin',
                       'interest_coverage'}
        
        metric_fields = {'eps', 'book_value', 'enterprise_value', 'ev_to_ebitda',
                        'ev_to_sales', 'roic', 'working_capital', 'graham_number'}
        
        estimate_fields = {'revenue_estimate_avg', 'eps_estimate_avg', 'ebitda_estimate_avg',
                          'num_analysts_eps', 'num_analysts_revenue'}
        
        target_fields = {'target_price_low', 'target_price_high', 'target_price_avg'}
        
        rating_fields = {'fmp_rating', 'fmp_rating_score', 'fmp_rating_recommendation'}
        
        # Fetch from appropriate endpoint
        if field in profile_fields:
            data = self.get_profile(ticker)
        elif field in ratio_fields:
            data = self.get_ratios_ttm(ticker)
        elif field in metric_fields:
            data = self.get_key_metrics_ttm(ticker)
        elif field in estimate_fields:
            data = self.get_analyst_estimates(ticker)
        elif field in target_fields:
            data = self.get_price_target(ticker)
        elif field in rating_fields:
            data = self.get_rating(ticker)
        else:
            # Unknown field - try profile as default
            data = self.get_profile(ticker)
        
        return data.get(field)


# Singleton instance
_fmp_instance = None

def get_fmp_extractor() -> FMPExtractor:
    """Get or create FMP extractor singleton."""
    global _fmp_instance
    if _fmp_instance is None:
        _fmp_instance = FMPExtractor()
    return _fmp_instance


# Quick test
if __name__ == "__main__":
    fmp = FMPExtractor()
    if fmp.available:
        data = fmp.extract_all("AAPL")
        print(f"\nExtracted {len(data)} fields:")
        for key, value in list(data.items())[:20]:
            print(f"  {key}: {value}")
    else:
        print("Set FMP_API_KEY environment variable to test")

