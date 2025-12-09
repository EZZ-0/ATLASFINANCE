"""
TICKER CACHE - Centralized yfinance Ticker Caching with Redis
===============================================================
Uses Redis for persistent caching, falls back to Streamlit cache if unavailable.

Usage:
    from utils.ticker_cache import get_ticker_info, prefetch_ticker_data
    
    # Get cached stock info
    info = get_ticker_info("AAPL")
"""

import os
import json
import logging
from typing import Dict, Optional, Any
from datetime import datetime

import yfinance as yf

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

logger = logging.getLogger(__name__)

# =============================================================================
# REDIS CONNECTION
# =============================================================================

_redis_client = None
_redis_available = False

def _init_redis():
    """Initialize Redis connection if available."""
    global _redis_client, _redis_available
    
    if _redis_client is not None:
        return _redis_available
    
    try:
        import redis
        redis_url = os.environ.get("REDIS_URL")
        
        if redis_url:
            _redis_client = redis.from_url(redis_url, decode_responses=True)
            _redis_client.ping()
            _redis_available = True
            print(f"[CACHE] ✅ Redis connected successfully")
            return True
    except Exception as e:
        print(f"[CACHE] ⚠️ Redis not available: {e}")
        _redis_available = False
    
    return False

# Try to connect on module load
_init_redis()


# =============================================================================
# CACHE OPERATIONS
# =============================================================================

def _cache_get(key: str) -> Optional[Dict]:
    """Get from Redis cache."""
    if not _redis_available or not _redis_client:
        return None
    try:
        data = _redis_client.get(key)
        if data:
            return json.loads(data)
    except Exception as e:
        logger.debug(f"Redis get failed: {e}")
    return None


def _cache_set(key: str, data: Dict, ttl: int = 3600) -> bool:
    """Set in Redis cache with TTL."""
    if not _redis_available or not _redis_client:
        return False
    try:
        _redis_client.setex(key, ttl, json.dumps(data, default=str))
        return True
    except Exception as e:
        logger.debug(f"Redis set failed: {e}")
        return False


# =============================================================================
# TICKER INFO (Main function used by app)
# =============================================================================

def get_ticker_info(ticker: str, ttl: int = 3600) -> Dict:
    """
    Get stock info with Redis caching.
    
    Args:
        ticker: Stock symbol
        ttl: Cache TTL in seconds (default 1 hour)
        
    Returns:
        Stock info dictionary
    """
    ticker = ticker.upper()
    cache_key = f"atlas:info:{ticker}"
    
    # Try Redis first
    cached = _cache_get(cache_key)
    if cached:
        logger.debug(f"[CACHE] Redis HIT for {ticker}")
        return cached
    
    # Cache miss - fetch from Yahoo
    try:
        logger.debug(f"[CACHE] MISS for {ticker} - fetching from Yahoo")
        stock = yf.Ticker(ticker)
        info = stock.info or {}
        
        # Cache in Redis
        _cache_set(cache_key, info, ttl)
        
        return info
    except Exception as e:
        logger.warning(f"Failed to get info for {ticker}: {e}")
        return {}


def get_ticker(ticker: str) -> yf.Ticker:
    """
    Get yfinance Ticker object.
    Note: The Ticker object itself isn't cached, but info calls are.
    """
    return yf.Ticker(ticker.upper())


# =============================================================================
# ADDITIONAL CACHED ACCESSORS
# =============================================================================

def get_ticker_financials(ticker: str, ttl: int = 3600) -> Dict[str, Any]:
    """Get all financial statements with Redis caching."""
    ticker = ticker.upper()
    cache_key = f"atlas:financials:{ticker}"
    
    cached = _cache_get(cache_key)
    if cached:
        return cached
    
    stock = yf.Ticker(ticker)
    
    result = {
        'info': {},
        'financials': None,
        'balance_sheet': None,
        'cashflow': None,
        'timestamp': datetime.now().isoformat()
    }
    
    try:
        result['info'] = stock.info or {}
    except Exception:
        pass
    
    try:
        # Convert DataFrames to dicts for JSON serialization
        financials = stock.financials
        result['financials'] = financials.to_dict() if hasattr(financials, 'to_dict') else None
    except Exception:
        pass
    
    try:
        balance = stock.balance_sheet
        result['balance_sheet'] = balance.to_dict() if hasattr(balance, 'to_dict') else None
    except Exception:
        pass
    
    try:
        cashflow = stock.cashflow
        result['cashflow'] = cashflow.to_dict() if hasattr(cashflow, 'to_dict') else None
    except Exception:
        pass
    
    _cache_set(cache_key, result, ttl)
    return result


def get_ticker_holders(ticker: str, ttl: int = 3600) -> Dict[str, Any]:
    """Get holder data with Redis caching."""
    ticker = ticker.upper()
    cache_key = f"atlas:holders:{ticker}"
    
    cached = _cache_get(cache_key)
    if cached:
        return cached
    
    stock = yf.Ticker(ticker)
    
    result = {
        'major_holders': None,
        'institutional_holders': None,
        'insider_transactions': None,
        'timestamp': datetime.now().isoformat()
    }
    
    try:
        mh = stock.major_holders
        result['major_holders'] = mh.to_dict() if hasattr(mh, 'to_dict') else None
    except Exception:
        pass
    
    try:
        ih = stock.institutional_holders
        result['institutional_holders'] = ih.to_dict() if hasattr(ih, 'to_dict') else None
    except Exception:
        pass
    
    try:
        it = stock.insider_transactions
        result['insider_transactions'] = it.to_dict() if hasattr(it, 'to_dict') else None
    except Exception:
        pass
    
    _cache_set(cache_key, result, ttl)
    return result


def get_ticker_earnings(ticker: str, ttl: int = 3600) -> Dict[str, Any]:
    """Get earnings data with Redis caching."""
    ticker = ticker.upper()
    cache_key = f"atlas:earnings:{ticker}"
    
    cached = _cache_get(cache_key)
    if cached:
        return cached
    
    stock = yf.Ticker(ticker)
    
    result = {
        'earnings_dates': None,
        'recommendations': None,
        'timestamp': datetime.now().isoformat()
    }
    
    try:
        ed = stock.earnings_dates
        result['earnings_dates'] = ed.to_dict() if hasattr(ed, 'to_dict') else None
    except Exception:
        pass
    
    try:
        rec = stock.recommendations
        result['recommendations'] = rec.to_dict() if hasattr(rec, 'to_dict') else None
    except Exception:
        pass
    
    _cache_set(cache_key, result, ttl)
    return result


# =============================================================================
# PREFETCH UTILITY
# =============================================================================

def prefetch_ticker_data(ticker: str) -> bool:
    """Prefetch all common data for a ticker to warm cache."""
    try:
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
    """Clear cached data for a ticker or all tickers."""
    if not _redis_available or not _redis_client:
        return
    
    try:
        if ticker:
            ticker = ticker.upper()
            _redis_client.delete(f"atlas:info:{ticker}")
            _redis_client.delete(f"atlas:financials:{ticker}")
            _redis_client.delete(f"atlas:holders:{ticker}")
            _redis_client.delete(f"atlas:earnings:{ticker}")
        else:
            # Clear all atlas keys
            for key in _redis_client.scan_iter("atlas:*"):
                _redis_client.delete(key)
    except Exception as e:
        logger.warning(f"Failed to clear cache: {e}")


def get_cache_stats() -> Dict:
    """Get cache statistics."""
    stats = {
        'backend': 'redis' if _redis_available else 'none',
        'connected': _redis_available,
        'ttl': '3600s'
    }
    
    if _redis_available and _redis_client:
        try:
            info = _redis_client.info('memory')
            stats['used_memory'] = info.get('used_memory_human', 'unknown')
            stats['keys'] = _redis_client.dbsize()
        except Exception:
            pass
    
    return stats


def is_redis_connected() -> bool:
    """Check if Redis is connected."""
    return _redis_available
