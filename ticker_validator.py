"""
TICKER VALIDATION MODULE
========================
Security layer to validate and sanitize ticker inputs before extraction.

Features:
- Ticker format validation (alphanumeric, 1-5 chars)
- Known ticker database (S&P 500 + common stocks)
- Suspicious pattern detection (SQL injection, XSS)
- Company name extraction and verification
"""

import re
from typing import Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

try:
    from sp500_tickers import SP500_TICKERS, SP500_COMPANIES
    SP500_AVAILABLE = True
except ImportError:
    SP500_AVAILABLE = False
    SP500_TICKERS = []
    SP500_COMPANIES = {}

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False


class TickerValidator:
    """
    Validates and sanitizes ticker symbols to prevent:
    - Invalid formats
    - SQL injection attempts
    - XSS attacks
    - Non-existent tickers
    """
    
    # ==========================================
    # VALIDATION PATTERNS
    # ==========================================
    
    # Valid ticker format: 1-5 alphanumeric characters + optional hyphen/dot
    VALID_TICKER_PATTERN = re.compile(r'^[A-Z]{1,5}(-[A-Z])?(\.[A-Z])?$', re.IGNORECASE)
    
    # Suspicious patterns (security)
    SUSPICIOUS_PATTERNS = [
        re.compile(r'[;\'"<>()]'),  # SQL/XSS characters
        re.compile(r'(DROP|DELETE|INSERT|UPDATE|SELECT|UNION|EXEC)', re.IGNORECASE),  # SQL keywords
        re.compile(r'(<script|javascript:|onerror=)', re.IGNORECASE),  # XSS patterns
        re.compile(r'(\.\.|//|\\\\)'),  # Path traversal
    ]
    
    # Common exchange suffixes (international support)
    KNOWN_SUFFIXES = ['.TO', '.L', '.HK', '.T', '.AX', '.SA', '-UN', '-A', '-B']
    
    def __init__(self):
        """Initialize Ticker Validator"""
        self.sp500_tickers = set(ticker.upper() for ticker in SP500_TICKERS) if SP500_AVAILABLE else set()
        self.validation_cache = {}  # Cache validation results
    
    # ==========================================
    # 1. FORMAT VALIDATION
    # ==========================================
    
    def validate_format(self, ticker: str) -> Tuple[bool, str]:
        """
        Validate ticker format.
        
        Rules:
        - 1-5 alphabetic characters
        - Optional hyphen or dot for class shares
        - No special characters, numbers, or SQL/XSS patterns
        
        Args:
            ticker: Ticker symbol to validate
            
        Returns:
            (is_valid, error_message)
        """
        if not ticker or not isinstance(ticker, str):
            return False, "Ticker cannot be empty"
        
        # Clean and uppercase
        ticker_clean = ticker.strip().upper()
        
        # Length check
        if len(ticker_clean) < 1 or len(ticker_clean) > 8:
            return False, f"Ticker length must be 1-8 characters (got {len(ticker_clean)})"
        
        # Security: Check for suspicious patterns
        for pattern in self.SUSPICIOUS_PATTERNS:
            if pattern.search(ticker):
                return False, f"Ticker contains invalid/suspicious characters: {ticker}"
        
        # Format validation
        if not self.VALID_TICKER_PATTERN.match(ticker_clean):
            return False, f"Invalid ticker format: {ticker}. Must be 1-5 letters with optional suffix (-A, .B, etc.)"
        
        return True, ""
    
    # ==========================================
    # 2. EXISTENCE VALIDATION
    # ==========================================
    
    def validate_existence(self, ticker: str, quick_check: bool = True) -> Tuple[bool, Optional[str]]:
        """
        Verify ticker exists and is tradable.
        
        Args:
            ticker: Ticker symbol
            quick_check: If True, only check S&P 500 list (fast). If False, query yfinance (slow but comprehensive)
            
        Returns:
            (exists, company_name or None)
        """
        ticker_clean = ticker.strip().upper()
        
        # Check cache first
        if ticker_clean in self.validation_cache:
            return self.validation_cache[ticker_clean]
        
        # Quick check: Is it in S&P 500?
        if quick_check and SP500_AVAILABLE:
            if ticker_clean in self.sp500_tickers:
                company_name = SP500_COMPANIES.get(ticker_clean, ticker_clean)
                self.validation_cache[ticker_clean] = (True, company_name)
                return True, company_name
            else:
                # Not in S&P 500, but might still exist
                return self._check_yfinance(ticker_clean)
        
        # Comprehensive check: Query yfinance
        return self._check_yfinance(ticker_clean)
    
    def _check_yfinance(self, ticker: str) -> Tuple[bool, Optional[str]]:
        """
        Check if ticker exists using yfinance.
        
        Args:
            ticker: Ticker symbol
            
        Returns:
            (exists, company_name or None)
        """
        if not YFINANCE_AVAILABLE:
            # Cannot verify, assume valid if format is correct
            return True, None
        
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Check if we got real data back
            if not info or 'symbol' not in info:
                return False, None
            
            # Extract company name
            company_name = info.get('longName') or info.get('shortName') or ticker
            
            # Cache result
            self.validation_cache[ticker] = (True, company_name)
            return True, company_name
            
        except Exception:
            # Ticker doesn't exist or API error
            self.validation_cache[ticker] = (False, None)
            return False, None
    
    # ==========================================
    # 3. COMPREHENSIVE VALIDATION
    # ==========================================
    
    def validate(self, ticker: str, check_existence: bool = False) -> Tuple[bool, str, Optional[str]]:
        """
        Comprehensive ticker validation.
        
        Args:
            ticker: Ticker symbol to validate
            check_existence: If True, verify ticker exists (slower)
            
        Returns:
            (is_valid, message, company_name or None)
        """
        # Step 1: Format validation (fast, security)
        format_valid, format_error = self.validate_format(ticker)
        if not format_valid:
            return False, format_error, None
        
        ticker_clean = ticker.strip().upper()
        
        # Step 2: Existence validation (optional, slower)
        if check_existence:
            exists, company_name = self.validate_existence(ticker_clean, quick_check=True)
            if not exists:
                return False, f"Ticker '{ticker_clean}' not found or not tradable", None
            return True, f"Valid ticker: {company_name}", company_name
        
        # Format valid, existence not checked
        return True, f"Format valid: {ticker_clean}", None
    
    # ==========================================
    # 4. BATCH VALIDATION
    # ==========================================
    
    def validate_batch(self, tickers: list, check_existence: bool = False) -> dict:
        """
        Validate multiple tickers at once.
        
        Args:
            tickers: List of ticker symbols
            check_existence: If True, verify tickers exist
            
        Returns:
            Dictionary with validation results for each ticker
        """
        results = {}
        for ticker in tickers:
            is_valid, message, company_name = self.validate(ticker, check_existence)
            results[ticker] = {
                'valid': is_valid,
                'message': message,
                'company_name': company_name,
                'ticker_clean': ticker.strip().upper() if is_valid else None
            }
        return results
    
    # ==========================================
    # 5. SANITIZATION
    # ==========================================
    
    def sanitize(self, ticker: str) -> str:
        """
        Sanitize ticker input (remove whitespace, convert to uppercase).
        
        Args:
            ticker: Raw ticker input
            
        Returns:
            Sanitized ticker
        """
        if not ticker:
            return ""
        return ticker.strip().upper()


# ==========================================
# HELPER FUNCTIONS
# ==========================================

def quick_validate(ticker: str) -> bool:
    """
    Quick validation helper (format only, no existence check).
    
    Args:
        ticker: Ticker symbol
        
    Returns:
        True if format is valid
    """
    validator = TickerValidator()
    is_valid, _, _ = validator.validate(ticker, check_existence=False)
    return is_valid


def full_validate(ticker: str) -> Tuple[bool, str, Optional[str]]:
    """
    Full validation helper (format + existence check).
    
    Args:
        ticker: Ticker symbol
        
    Returns:
        (is_valid, message, company_name)
    """
    validator = TickerValidator()
    return validator.validate(ticker, check_existence=True)


if __name__ == "__main__":
    # Test cases
    validator = TickerValidator()
    
    test_cases = [
        ("AAPL", True, "Valid S&P 500 ticker"),
        ("GOOGL", True, "Valid S&P 500 ticker"),
        ("BRK-B", True, "Valid with hyphen"),
        ("BRK.B", True, "Valid with dot"),
        ("", False, "Empty ticker"),
        ("TOOLONGTICKER", False, "Too long"),
        ("123", False, "Numbers only"),
        ("AAPL; DROP TABLE", False, "SQL injection attempt"),
        ("<script>alert('xss')</script>", False, "XSS attempt"),
        ("../etc/passwd", False, "Path traversal attempt"),
    ]
    
    print("=" * 80)
    print("TICKER VALIDATOR - TEST SUITE")
    print("=" * 80)
    
    for ticker, should_pass, description in test_cases:
        is_valid, message, _ = validator.validate(ticker, check_existence=False)
        status = "✅ PASS" if (is_valid == should_pass) else "❌ FAIL"
        print(f"{status} | {description:30} | Ticker: {ticker:20} | {message}")
    
    print("\n" + "=" * 80)
    print("All tests completed!")
    print("=" * 80)




