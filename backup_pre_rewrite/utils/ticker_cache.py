"""
TICKER CACHE - Centralized yfinance Ticker Caching
====================================================
Part of MILESTONE-007: Performance Optimization

Provides a singleton cached Ticker object to avoid redundant API calls.
All modules should use get_ticker() instead of yf.Ticker() directly.

Author: EXECUTOR
Created: 2025-12-08

Usage:
    from utils.ticker_cache import get_ticker, get_ticker_info, prefetch_ticker_data
    
    # Instead of: stock = yf.Ticker(ticker)
    stock = get_ticker(ticker)
    
    # Pre-fetch all common data for a ticker
    prefetch_ticker_data(ticker)
"""

import streamlit as st
import yfinance as yf
from typing import Dict, Optional, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


# =============================================================================
# CACHED TICKER OBJECT
# =============================================================================

@st.cache_resource(ttl=3600)  # Cache Ticker objects for 1 hour
def get_ticker(ticker: str) -> yf.Ticker:
    """
    Get a cached yfinance Ticker object.
    
    This is the ONLY way modules should access Ticker objects.
    Reusing the same object avoids redundant API initialization.
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        yfinance Ticker object (cached)
    """
    return yf.Ticker(ticker.upper())


# =============================================================================
# CACHED DATA ACCESSORS
# =============================================================================

@st.cache_data(ttl=3600)
def get_ticker_info(ticker: str) -> Dict:
    """
    Get cached stock info dict.
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        Stock info dictionary
    """
    stock = get_ticker(ticker)
    try:
        return stock.info or {}
    except Exception as e:
        logger.warning(f"Failed to get info for {ticker}: {e}")
        return {}


@st.cache_data(ttl=3600)
def get_ticker_financials(ticker: str) -> Dict[str, Any]:
    """
    Get all financial statements in one call (cached).
    
    This prefetches all common financial data to avoid multiple calls.
    
    Returns:
        Dict with keys: financials, balance_sheet, cashflow, info
    """
    stock = get_ticker(ticker)
    
    result = {
        'info': {},
        'financials': None,
        'balance_sheet': None,
        'cashflow': None,
        'timestamp': datetime.now().isoformat()
    }
    
    try:
        result['info'] = stock.info or {}
    except Exception as e:
        logger.warning(f"Failed to get info: {e}")
    
    try:
        result['financials'] = stock.financials
    except Exception as e:
        logger.warning(f"Failed to get financials: {e}")
    
    try:
        result['balance_sheet'] = stock.balance_sheet
    except Exception as e:
        logger.warning(f"Failed to get balance_sheet: {e}")
    
    try:
        result['cashflow'] = stock.cashflow
    except Exception as e:
        logger.warning(f"Failed to get cashflow: {e}")
    
    return result


@st.cache_data(ttl=3600)
def get_ticker_holders(ticker: str) -> Dict[str, Any]:
    """
    Get holder data in one call (cached).
    
    Returns:
        Dict with keys: major_holders, institutional_holders, insider_transactions
    """
    stock = get_ticker(ticker)
    
    result = {
        'major_holders': None,
        'institutional_holders': None,
        'insider_transactions': None,
        'timestamp': datetime.now().isoformat()
    }
    
    try:
        result['major_holders'] = stock.major_holders
    except Exception as e:
        logger.warning(f"Failed to get major_holders: {e}")
    
    try:
        result['institutional_holders'] = stock.institutional_holders
    except Exception as e:
        logger.warning(f"Failed to get institutional_holders: {e}")
    
    try:
        result['insider_transactions'] = stock.insider_transactions
    except Exception as e:
        logger.warning(f"Failed to get insider_transactions: {e}")
    
    return result


@st.cache_data(ttl=3600)
def get_ticker_earnings(ticker: str) -> Dict[str, Any]:
    """
    Get earnings-related data in one call (cached).
    
    Returns:
        Dict with keys: earnings_dates, recommendations
    """
    stock = get_ticker(ticker)
    
    result = {
        'earnings_dates': None,
        'recommendations': None,
        'timestamp': datetime.now().isoformat()
    }
    
    try:
        result['earnings_dates'] = stock.earnings_dates
    except Exception as e:
        logger.warning(f"Failed to get earnings_dates: {e}")
    
    try:
        result['recommendations'] = stock.recommendations
    except Exception as e:
        logger.warning(f"Failed to get recommendations: {e}")
    
    return result


# =============================================================================
# PREFETCH UTILITY
# =============================================================================

def prefetch_ticker_data(ticker: str) -> bool:
    """
    Prefetch all common data for a ticker.
    
    Call this once when a ticker is selected to warm the cache.
    Subsequent calls will be instant.
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        True if prefetch succeeded
    """
    try:
        # Warm the cache by calling all accessors
        get_ticker_info(ticker)
        get_ticker_financials(ticker)
        get_ticker_holders(ticker)
        get_ticker_earnings(ticker)
        return True
    except Exception as e:
        logger.error(f"Prefetch failed for {ticker}: {e}")
        return False


# =============================================================================
# CACHE MANAGEMENT
# =============================================================================

def clear_ticker_cache(ticker: str = None):
    """
    Clear cached data.
    
    Args:
        ticker: If provided, only clear for this ticker. If None, clear all.
    """
    # Streamlit doesn't support per-key clearing, so we clear all
    get_ticker_info.clear()
    get_ticker_financials.clear()
    get_ticker_holders.clear()
    get_ticker_earnings.clear()
    
    # Also clear the Ticker resource cache
    get_ticker.clear()


def get_cache_stats() -> Dict:
    """Get cache statistics (for debugging)."""
    return {
        'ticker_cache': 'active',
        'ttl': '3600s',
        'note': 'Use clear_ticker_cache() to invalidate'
    }

