"""
Ticker Mapper - MILESTONE-011
=============================
Maps common ticker aliases and handles renamed/delisted symbols.

Created: 2025-12-08
Author: ATLAS Financial Intelligence (Executor)
"""

import yfinance as yf
import logging
from typing import Optional, Tuple, Dict
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# Common ticker aliases and corrections
TICKER_ALIASES: Dict[str, str] = {
    # Common mistakes
    "ZOOM": "ZM",           # Zoom Video Communications (not ZOOM Technologies)
    "GOOGLE": "GOOGL",      # Alphabet Inc Class A
    "GOOG": "GOOGL",        # Prefer Class A
    "FACEBOOK": "META",     # Meta Platforms (renamed 2021)
    "FB": "META",           # Old Facebook ticker
    
    # Renamed companies
    "TWTR": "X",            # Twitter → X (now private, but for reference)
    
    # Class share preferences (use most liquid)
    "BRK.A": "BRK-B",       # Berkshire Class B more accessible
    "BRK.B": "BRK-B",       # Normalize format
    
    # Common typos
    "APPL": "AAPL",         # Apple typo
    "MSFT.": "MSFT",        # Trailing dot
    "AMZN.": "AMZN",        # Trailing dot
}

# Tickers known to be problematic (delisted, renamed, or require special handling)
PROBLEMATIC_TICKERS: Dict[str, str] = {
    "SQ": "Block Inc - Ticker changed to XYZ. May still work as SQ for some data.",
    "WBA": "Walgreens Boots Alliance - Check if still trading. May have data issues.",
    "ZOOM": "Wrong ticker - use ZM for Zoom Video Communications.",
}

# Known delisted or invalid tickers
DELISTED_TICKERS: Dict[str, str] = {
    "WBA": "Walgreens Boots Alliance - Returns 404 from yfinance (as of Dec 2025). May be delisted or data unavailable.",
}


@dataclass
class TickerValidation:
    """Result of ticker validation."""
    original: str
    normalized: str
    is_valid: bool
    warning: Optional[str] = None
    suggestion: Optional[str] = None


def normalize_ticker(ticker: str) -> str:
    """
    Map common aliases to correct tickers.
    
    Args:
        ticker: Raw ticker input from user
        
    Returns:
        Normalized ticker symbol
    """
    if not ticker:
        return ticker
    
    # Clean up input
    cleaned = ticker.strip().upper()
    
    # Remove common suffixes
    for suffix in ['.', ',', ' ']:
        cleaned = cleaned.rstrip(suffix)
    
    # Check aliases
    if cleaned in TICKER_ALIASES:
        mapped = TICKER_ALIASES[cleaned]
        logger.info(f"Ticker mapped: {cleaned} → {mapped}")
        return mapped
    
    return cleaned


def validate_ticker(ticker: str) -> TickerValidation:
    """
    Validate a ticker symbol and provide suggestions if invalid.
    
    Args:
        ticker: Ticker symbol to validate
        
    Returns:
        TickerValidation with status and suggestions
    """
    original = ticker
    normalized = normalize_ticker(ticker)
    
    # Check if it's a known problematic ticker
    if normalized in PROBLEMATIC_TICKERS:
        return TickerValidation(
            original=original,
            normalized=normalized,
            is_valid=True,  # May still work
            warning=PROBLEMATIC_TICKERS[normalized]
        )
    
    # Check if delisted
    if normalized in DELISTED_TICKERS:
        return TickerValidation(
            original=original,
            normalized=normalized,
            is_valid=False,
            warning=f"Ticker {normalized} appears to be delisted.",
            suggestion=DELISTED_TICKERS[normalized]
        )
    
    # Try to validate with yfinance (quick check)
    try:
        stock = yf.Ticker(normalized)
        info = stock.info
        
        # Check if we got valid data
        if info and info.get('regularMarketPrice') is not None:
            return TickerValidation(
                original=original,
                normalized=normalized,
                is_valid=True
            )
        elif info and info.get('shortName'):
            # Has name but no price - might be valid but after hours
            return TickerValidation(
                original=original,
                normalized=normalized,
                is_valid=True,
                warning="Ticker found but no current price data."
            )
        else:
            # No valid data - likely invalid
            return TickerValidation(
                original=original,
                normalized=normalized,
                is_valid=False,
                warning=f"Could not find data for ticker {normalized}.",
                suggestion=_suggest_similar_ticker(normalized)
            )
            
    except Exception as e:
        logger.error(f"Error validating ticker {normalized}: {e}")
        return TickerValidation(
            original=original,
            normalized=normalized,
            is_valid=False,
            warning=f"Error validating ticker: {str(e)}"
        )


def _suggest_similar_ticker(ticker: str) -> Optional[str]:
    """
    Suggest a similar valid ticker based on common patterns.
    """
    suggestions = {
        "ZOOM": "Did you mean ZM (Zoom Video)?",
        "GOOGLE": "Did you mean GOOGL (Alphabet)?",
        "FACEBOOK": "Did you mean META (Meta Platforms)?",
        "TWITTER": "Twitter is now private (acquired by X Corp).",
        "APPL": "Did you mean AAPL (Apple)?",
    }
    
    return suggestions.get(ticker.upper())


def get_ticker_info(ticker: str) -> Tuple[str, Optional[str]]:
    """
    Get normalized ticker and any warning message.
    
    Args:
        ticker: Raw ticker input
        
    Returns:
        Tuple of (normalized_ticker, warning_message_or_none)
    """
    normalized = normalize_ticker(ticker)
    
    warning = None
    if ticker.upper() != normalized:
        warning = f"Ticker '{ticker}' mapped to '{normalized}'"
    
    if normalized in PROBLEMATIC_TICKERS:
        if warning:
            warning += f". Note: {PROBLEMATIC_TICKERS[normalized]}"
        else:
            warning = PROBLEMATIC_TICKERS[normalized]
    
    return normalized, warning


# Quick validation without yfinance call (for UI performance)
def quick_normalize(ticker: str) -> str:
    """
    Quick normalization without API validation.
    Use for performance-critical paths.
    """
    return normalize_ticker(ticker)


# Export commonly used function names
__all__ = [
    'normalize_ticker',
    'validate_ticker', 
    'get_ticker_info',
    'quick_normalize',
    'TICKER_ALIASES',
    'PROBLEMATIC_TICKERS',
    'TickerValidation'
]


# Test script
if __name__ == "__main__":
    print("=" * 60)
    print("TICKER MAPPER TEST")
    print("=" * 60)
    
    test_cases = [
        "AAPL",      # Normal - no change
        "ZOOM",      # Should map to ZM
        "GOOGLE",    # Should map to GOOGL
        "FACEBOOK",  # Should map to META
        "FB",        # Should map to META
        "APPL",      # Typo - should map to AAPL
        "SQ",        # Problematic - should warn
        "WBA",       # Problematic - should warn
        "msft",      # Lowercase - should normalize
        "  NVDA  ",  # Whitespace - should clean
    ]
    
    print("\nNormalization Tests:")
    for ticker in test_cases:
        normalized = normalize_ticker(ticker)
        status = "→" if ticker.upper().strip() != normalized else "="
        print(f"  {ticker:12} {status} {normalized}")
    
    print("\n" + "=" * 60)
    print("Validation Tests (with yfinance):")
    print("=" * 60)
    
    for ticker in ["AAPL", "ZOOM", "SQ", "INVALIDXYZ"]:
        result = validate_ticker(ticker)
        status = "✅" if result.is_valid else "❌"
        print(f"\n  {ticker}:")
        print(f"    Normalized: {result.normalized}")
        print(f"    Valid: {status}")
        if result.warning:
            print(f"    Warning: {result.warning}")
        if result.suggestion:
            print(f"    Suggestion: {result.suggestion}")

