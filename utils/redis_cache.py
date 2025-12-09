"""
REDIS CACHE - Persistent Financial Data Caching
================================================
Provides Redis-based caching for yfinance data to prevent rate limiting.
Falls back to in-memory dict if Redis is not available.

Setup:
    1. pip install redis
    2. Set environment variables:
       - REDIS_URL=redis://default:password@host:port
       OR
       - REDIS_HOST, REDIS_PORT, REDIS_PASSWORD

Usage:
    from utils.redis_cache import get_cached_ticker_info, cache_ticker_info
    
    # Get cached or fetch new
    info = get_cached_ticker_info("AAPL")
    
    # Manually cache data
    cache_ticker_info("AAPL", info_dict, ttl=3600)
"""

import os
import json
import time
import logging
from typing import Dict, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

# Try to import redis
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("Redis not installed. Using in-memory fallback cache.")

# Try to import yfinance
try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False


# =============================================================================
# REDIS CONNECTION
# =============================================================================

_redis_client: Optional[Any] = None
_memory_cache: Dict[str, Dict] = {}  # Fallback cache

def get_redis_client():
    """Get or create Redis client connection."""
    global _redis_client
    
    if _redis_client is not None:
        return _redis_client
    
    if not REDIS_AVAILABLE:
        return None
    
    try:
        # Try REDIS_URL first (Railway, Heroku, Redis Cloud format)
        redis_url = os.environ.get("REDIS_URL")
        if redis_url:
            _redis_client = redis.from_url(redis_url, decode_responses=True)
            _redis_client.ping()  # Test connection
            logger.info(f"Connected to Redis via URL")
            return _redis_client
        
        # Try individual env vars
        host = os.environ.get("REDIS_HOST", "localhost")
        port = int(os.environ.get("REDIS_PORT", 6379))
        password = os.environ.get("REDIS_PASSWORD")
        
        _redis_client = redis.Redis(
            host=host,
            port=port,
            password=password,
            decode_responses=True,
            socket_timeout=5
        )
        _redis_client.ping()  # Test connection
        logger.info(f"Connected to Redis at {host}:{port}")
        return _redis_client
        
    except Exception as e:
        logger.warning(f"Redis connection failed: {e}. Using in-memory cache.")
        return None


# =============================================================================
# CACHE OPERATIONS
# =============================================================================

def _get_cache_key(prefix: str, ticker: str) -> str:
    """Generate cache key."""
    return f"atlas:{prefix}:{ticker.upper()}"


def cache_get(key: str) -> Optional[Dict]:
    """Get value from cache (Redis or memory fallback)."""
    client = get_redis_client()
    
    if client:
        try:
            data = client.get(key)
            if data:
                return json.loads(data)
        except Exception as e:
            logger.warning(f"Redis get failed: {e}")
    
    # Fallback to memory cache
    cached = _memory_cache.get(key)
    if cached:
        # Check TTL for memory cache
        if cached.get('_expires', 0) > time.time():
            return cached.get('data')
        else:
            del _memory_cache[key]
    
    return None


def cache_set(key: str, data: Dict, ttl: int = 3600) -> bool:
    """Set value in cache with TTL (default 1 hour)."""
    client = get_redis_client()
    
    if client:
        try:
            client.setex(key, ttl, json.dumps(data, default=str))
            return True
        except Exception as e:
            logger.warning(f"Redis set failed: {e}")
    
    # Fallback to memory cache
    _memory_cache[key] = {
        'data': data,
        '_expires': time.time() + ttl
    }
    return True


def cache_delete(key: str) -> bool:
    """Delete value from cache."""
    client = get_redis_client()
    
    if client:
        try:
            client.delete(key)
        except Exception:
            pass
    
    if key in _memory_cache:
        del _memory_cache[key]
    
    return True


# =============================================================================
# TICKER-SPECIFIC CACHE FUNCTIONS
# =============================================================================

def get_cached_ticker_info(ticker: str, ttl: int = 3600) -> Dict:
    """
    Get ticker info from cache or fetch from Yahoo Finance.
    
    Args:
        ticker: Stock symbol
        ttl: Cache TTL in seconds (default 1 hour)
        
    Returns:
        Stock info dictionary
    """
    key = _get_cache_key("info", ticker)
    
    # Try cache first
    cached = cache_get(key)
    if cached:
        logger.debug(f"Cache HIT for {ticker}")
        return cached
    
    # Cache miss - fetch from Yahoo
    if not YFINANCE_AVAILABLE:
        return {}
    
    try:
        logger.debug(f"Cache MISS for {ticker} - fetching from Yahoo")
        stock = yf.Ticker(ticker.upper())
        info = stock.info or {}
        
        # Cache the result
        cache_set(key, info, ttl)
        
        return info
    except Exception as e:
        logger.warning(f"Failed to fetch {ticker}: {e}")
        return {}


def cache_ticker_info(ticker: str, info: Dict, ttl: int = 3600) -> bool:
    """Manually cache ticker info."""
    key = _get_cache_key("info", ticker)
    return cache_set(key, info, ttl)


def get_cached_financials(ticker: str, ttl: int = 3600) -> Dict:
    """
    Get full financials from cache or fetch.
    
    Returns dict with: info, financials, balance_sheet, cashflow
    """
    key = _get_cache_key("financials", ticker)
    
    # Try cache first
    cached = cache_get(key)
    if cached:
        return cached
    
    if not YFINANCE_AVAILABLE:
        return {}
    
    try:
        stock = yf.Ticker(ticker.upper())
        
        result = {
            'info': stock.info or {},
            'financials': stock.financials.to_dict() if hasattr(stock.financials, 'to_dict') else {},
            'balance_sheet': stock.balance_sheet.to_dict() if hasattr(stock.balance_sheet, 'to_dict') else {},
            'cashflow': stock.cashflow.to_dict() if hasattr(stock.cashflow, 'to_dict') else {},
            '_cached_at': datetime.now().isoformat()
        }
        
        cache_set(key, result, ttl)
        return result
        
    except Exception as e:
        logger.warning(f"Failed to fetch financials for {ticker}: {e}")
        return {}


# =============================================================================
# CACHE MANAGEMENT
# =============================================================================

def clear_ticker_cache(ticker: str = None):
    """Clear cache for a specific ticker or all tickers."""
    if ticker:
        cache_delete(_get_cache_key("info", ticker))
        cache_delete(_get_cache_key("financials", ticker))
    else:
        # Clear all - only works with Redis
        client = get_redis_client()
        if client:
            try:
                for key in client.scan_iter("atlas:*"):
                    client.delete(key)
            except Exception:
                pass
        _memory_cache.clear()


def get_cache_stats() -> Dict:
    """Get cache statistics."""
    client = get_redis_client()
    
    stats = {
        'backend': 'redis' if client else 'memory',
        'connected': client is not None,
        'memory_cache_size': len(_memory_cache)
    }
    
    if client:
        try:
            info = client.info('memory')
            stats['redis_used_memory'] = info.get('used_memory_human', 'unknown')
            stats['redis_keys'] = client.dbsize()
        except Exception:
            pass
    
    return stats


# =============================================================================
# INITIALIZATION CHECK
# =============================================================================

def init_redis_cache() -> bool:
    """
    Initialize Redis cache. Call on app startup.
    
    Returns True if Redis is connected, False if using memory fallback.
    """
    client = get_redis_client()
    if client:
        print(f"[CACHE] Redis connected: {get_cache_stats()}")
        return True
    else:
        print("[CACHE] Using in-memory fallback (Redis not available)")
        return False

