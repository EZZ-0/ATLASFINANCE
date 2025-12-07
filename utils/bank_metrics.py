"""
BANK-SPECIFIC METRICS - MILESTONE-012
=====================================
Banks have different financial structures:
- No traditional FCF (operating cash flow different)
- No meaningful D/E ratio (leverage is the business)
- Use: Tier 1 Capital, NIM, Efficiency Ratio, NPL Ratio

This module provides bank-specific metric handling.

Author: ATLAS Architect
Date: 2025-12-08
"""

from typing import Dict, Any, Optional, List
import yfinance as yf

# Bank/Financial sector tickers (major US banks)
BANK_TICKERS = {
    # Major Banks
    'JPM', 'BAC', 'WFC', 'C', 'GS', 'MS', 'USB', 'PNC', 'TFC', 'COF',
    # Regional Banks
    'FITB', 'KEY', 'RF', 'HBAN', 'CFG', 'MTB', 'ZION', 'CMA', 'ALLY',
    # Investment Banks / Brokers
    'SCHW', 'IBKR', 'RJF', 'LPLA', 'SF',
}

# Alternative metrics for banks (instead of FCF/D/E)
BANK_METRICS = {
    'tier1_capital_ratio': {
        'name': 'Tier 1 Capital Ratio',
        'formula': 'Tier 1 Capital / Risk-Weighted Assets',
        'benchmark': (10, 14),  # 10% minimum, 14%+ is strong
        'higher_is': 'better',
        'unit': '%',
        'insight': 'Capital strength. >12% is well-capitalized.'
    },
    'net_interest_margin': {
        'name': 'Net Interest Margin',
        'formula': '(Interest Income - Interest Expense) / Avg Assets',
        'benchmark': (2.5, 4.0),
        'higher_is': 'better',
        'unit': '%',
        'insight': 'Core profitability. >3% is healthy.'
    },
    'efficiency_ratio': {
        'name': 'Efficiency Ratio',
        'formula': 'Non-Interest Expense / Revenue',
        'benchmark': (50, 65),
        'higher_is': 'worse',  # Lower is better
        'unit': '%',
        'insight': 'Cost control. <55% is excellent.'
    },
    'npl_ratio': {
        'name': 'NPL Ratio',
        'formula': 'Non-Performing Loans / Total Loans',
        'benchmark': (0.5, 2.0),
        'higher_is': 'worse',
        'unit': '%',
        'insight': 'Asset quality. <1% is strong.'
    },
    'loan_to_deposit': {
        'name': 'Loan-to-Deposit Ratio',
        'formula': 'Total Loans / Total Deposits',
        'benchmark': (70, 90),
        'higher_is': 'neutral',
        'unit': '%',
        'insight': 'Liquidity. 80-90% is optimal.'
    },
    'rote': {
        'name': 'Return on Tangible Equity',
        'formula': 'Net Income / Tangible Common Equity',
        'benchmark': (10, 15),
        'higher_is': 'better',
        'unit': '%',
        'insight': 'True profitability. >12% is good.'
    },
}


def is_bank(ticker: str, info: Dict = None) -> bool:
    """
    Check if ticker is a bank/financial institution.
    
    Args:
        ticker: Stock ticker
        info: Optional yfinance info dict
    
    Returns:
        True if bank/financial
    """
    # Check known banks first
    if ticker.upper() in BANK_TICKERS:
        return True
    
    # Check sector from info
    if info:
        sector = info.get('sector', '').lower()
        industry = info.get('industry', '').lower()
        
        bank_keywords = ['bank', 'financial', 'credit', 'lending', 'savings']
        if any(kw in sector for kw in bank_keywords):
            return True
        if any(kw in industry for kw in bank_keywords):
            return True
    
    return False


def get_bank_metrics(ticker: str) -> Dict[str, Any]:
    """
    Get bank-specific metrics for a financial institution.
    
    Note: yfinance doesn't provide all bank-specific metrics directly.
    This extracts what's available and marks unavailable ones.
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        if not is_bank(ticker, info):
            return {'status': 'not_bank', 'ticker': ticker}
        
        # Extract available metrics
        metrics = {
            'ticker': ticker,
            'status': 'success',
            'is_bank': True,
            'company_name': info.get('longName', ticker),
        }
        
        # ROE is available
        roe = info.get('returnOnEquity')
        if roe is not None:
            metrics['roe'] = round(roe * 100, 2)
        
        # ROTE approximation (use ROE if tangible not available)
        metrics['rote'] = metrics.get('roe')  # Approximation
        
        # Book Value Per Share
        bvps = info.get('bookValue')
        if bvps:
            metrics['book_value_per_share'] = round(bvps, 2)
        
        # Price to Book (important for banks)
        ptb = info.get('priceToBook')
        if ptb:
            metrics['price_to_book'] = round(ptb, 2)
        
        # Price to Tangible Book (approximation)
        metrics['price_to_tangible_book'] = metrics.get('price_to_book')
        
        # Dividend Yield (banks often pay dividends)
        div_yield = info.get('dividendYield')
        if div_yield:
            metrics['dividend_yield'] = round(div_yield * 100, 2)
        
        # Note which metrics are NOT available via yfinance
        metrics['unavailable_metrics'] = [
            'tier1_capital_ratio',  # Requires regulatory filings
            'net_interest_margin',  # Requires bank-specific data
            'efficiency_ratio',     # Requires bank-specific breakdown
            'npl_ratio',           # Requires loan quality data
            'loan_to_deposit',     # Requires deposit data
        ]
        
        # Provide guidance
        metrics['note'] = (
            "Bank-specific metrics (Tier 1, NIM, NPL) require regulatory filings. "
            "Use FDIC or Federal Reserve data for detailed bank analysis."
        )
        
        return metrics
        
    except Exception as e:
        return {
            'status': 'error',
            'ticker': ticker,
            'error': str(e)
        }


def get_bank_display_metrics(ticker: str, info: Dict = None) -> List[Dict]:
    """
    Get display-ready bank metrics for UI.
    Returns list of metrics suitable for flip cards.
    """
    if not is_bank(ticker, info):
        return []
    
    # If info provided, extract from it; otherwise fetch
    if info is None:
        stock = yf.Ticker(ticker)
        info = stock.info
    
    metrics = []
    
    # Price to Book (key bank metric)
    ptb = info.get('priceToBook')
    if ptb:
        metrics.append({
            'key': 'PB_Ratio',
            'value': ptb,
            'label': 'Price/Book',
            'insight': 'Bank valuation. <1 may be undervalued, >2 premium.'
        })
    
    # ROE
    roe = info.get('returnOnEquity')
    if roe:
        metrics.append({
            'key': 'ROE',
            'value': roe * 100,
            'label': 'ROE',
            'insight': 'Bank profitability. >10% is good for banks.'
        })
    
    # Dividend Yield
    div = info.get('dividendYield')
    if div:
        metrics.append({
            'key': 'Dividend_Yield',
            'value': div * 100,
            'label': 'Dividend Yield',
            'insight': 'Bank income. Most large banks pay 2-4%.'
        })
    
    # Beta
    beta = info.get('beta')
    if beta:
        metrics.append({
            'key': 'Beta',
            'value': beta,
            'label': 'Beta',
            'insight': 'Bank volatility. Banks typically 1.0-1.5.'
        })
    
    return metrics


# Export
__all__ = [
    'is_bank',
    'get_bank_metrics',
    'get_bank_display_metrics',
    'BANK_TICKERS',
    'BANK_METRICS'
]

