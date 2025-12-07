"""
Utils package for Saudi Earnings Engine
Contains security, logging, validation, and caching utilities
"""

from .security import SecurityValidator, quick_validate, sanitize
from .logging_config import EngineLogger, get_logger, log_error, log_warning, log_info
from .ticker_cache import (
    get_ticker, get_ticker_info, get_ticker_financials,
    get_ticker_holders, get_ticker_earnings, prefetch_ticker_data,
    clear_ticker_cache, get_cache_stats
)
from .bank_metrics import is_bank, get_bank_metrics, get_bank_display_metrics, BANK_TICKERS
from .ticker_mapper import (
    normalize_ticker, validate_ticker, quick_normalize,
    TICKER_ALIASES, PROBLEMATIC_TICKERS, TickerValidation
)

__all__ = [
    # Security
    'SecurityValidator', 'quick_validate', 'sanitize',
    # Logging
    'EngineLogger', 'get_logger', 'log_error', 'log_warning', 'log_info',
    # Ticker Cache
    'get_ticker', 'get_ticker_info', 'get_ticker_financials',
    'get_ticker_holders', 'get_ticker_earnings', 'prefetch_ticker_data',
    'clear_ticker_cache', 'get_cache_stats',
    # Bank Metrics (M012)
    'is_bank', 'get_bank_metrics', 'get_bank_display_metrics', 'BANK_TICKERS'
]

