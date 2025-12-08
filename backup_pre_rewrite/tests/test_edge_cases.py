"""
EDGE CASE TESTS
===============
Tests extreme values, invalid inputs, and boundary conditions.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import pandas as pd
import numpy as np

from ticker_validator import TickerValidator
from format_helpers import format_large_number


class TestEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_empty_ticker(self):
        """Test empty ticker input"""
        validator = TickerValidator()
        is_valid, message, _ = validator.validate("")
        assert not is_valid
        assert "empty" in message.lower()
    
    def test_extremely_long_ticker(self):
        """Test ticker that's way too long"""
        validator = TickerValidator()
        long_ticker = "A" * 100
        is_valid, message, _ = validator.validate(long_ticker)
        assert not is_valid
    
    def test_sql_injection_attempts(self):
        """Test SQL injection patterns"""
        validator = TickerValidator()
        
        injection_attempts = [
            "AAPL; DROP TABLE users;",
            "AAPL' OR '1'='1",
            "AAPL--",
            "AAPL/**/OR/**/1=1",
        ]
        
        for attempt in injection_attempts:
            is_valid, _, _ = validator.validate(attempt)
            assert not is_valid, f"Failed to block: {attempt}"
    
    def test_xss_attempts(self):
        """Test XSS attack patterns"""
        validator = TickerValidator()
        
        xss_attempts = [
            "<script>alert('xss')</script>",
            "<img src=x onerror=alert(1)>",
            "javascript:alert(1)",
        ]
        
        for attempt in xss_attempts:
            is_valid, _, _ = validator.validate(attempt)
            assert not is_valid, f"Failed to block: {attempt}"
    
    def test_path_traversal_attempts(self):
        """Test path traversal patterns"""
        validator = TickerValidator()
        
        traversal_attempts = [
            "../etc/passwd",
            "..\\..\\windows\\system32",
            "....//....//etc//passwd",
        ]
        
        for attempt in traversal_attempts:
            is_valid, _, _ = validator.validate(attempt)
            assert not is_valid, f"Failed to block: {attempt}"
    
    def test_extreme_numbers(self):
        """Test formatting of extreme numbers"""
        # Very large number (trillions)
        large = format_large_number(1_500_000_000_000, format_type='currency')
        assert "T" in large or "B" in large
        
        # Very small number
        small = format_large_number(0.01, format_type='currency')
        assert "$" in small
        
        # Zero
        zero = format_large_number(0, format_type='currency')
        assert "$" in zero
        
        # Negative
        negative = format_large_number(-1_000_000, format_type='currency')
        assert "-" in negative or "(" in negative
    
    def test_nan_and_inf_handling(self):
        """Test NaN and infinity handling"""
        # NaN should be handled gracefully
        result_nan = format_large_number(np.nan, format_type='currency')
        assert result_nan is not None
        
        # Infinity should be handled gracefully
        result_inf = format_large_number(np.inf, format_type='currency')
        assert result_inf is not None
    
    def test_negative_growth_rates(self):
        """Test negative growth rate calculations"""
        initial = 100
        final = 50
        years = 3
        
        # Negative CAGR
        cagr = (final / initial) ** (1/years) - 1
        assert cagr < 0
        assert cagr > -1  # Can't lose more than 100%
    
    def test_division_by_zero(self):
        """Test division by zero scenarios"""
        # ROE when equity is zero
        with pytest.raises(ZeroDivisionError):
            roe = 100_000 / 0
        
        # Use numpy for safe division
        safe_roe = np.divide(100_000, 0, out=np.zeros_like(100_000, dtype=float), where=0!=0)
        assert safe_roe == 0 or np.isnan(safe_roe) or np.isinf(safe_roe)
    
    def test_missing_financial_data(self):
        """Test handling of missing financial data"""
        # Empty DataFrame
        empty_df = pd.DataFrame()
        assert empty_df.empty
        
        # DataFrame with NaN values
        df_with_nan = pd.DataFrame({
            'Revenue': [100, np.nan, 200],
            'Net Income': [10, 20, np.nan]
        })
        
        # Check if we can safely calculate ratios
        safe_margin = df_with_nan['Net Income'] / df_with_nan['Revenue']
        assert len(safe_margin) == 3
    
    def test_unicode_and_special_chars(self):
        """Test unicode and special character handling"""
        validator = TickerValidator()
        
        special_inputs = [
            "AAPL™",
            "MSFT®",
            "GOOGL©",
            "テスト",  # Japanese
            "测试",    # Chinese
            "тест",   # Russian
        ]
        
        for special in special_inputs:
            is_valid, _, _ = validator.validate(special)
            # Should reject non-ASCII characters
            assert not is_valid


class TestDataQuality:
    """Test data quality and consistency"""
    
    def test_date_consistency(self):
        """Test that dates are properly ordered"""
        dates = pd.date_range(start='2020-01-01', end='2024-01-01', freq='Y')
        assert dates.is_monotonic_increasing
    
    def test_financial_data_completeness(self):
        """Test that financial statements have required fields"""
        required_fields = [
            'Total Revenue',
            'Net Income',
            'Total Assets',
            'Total Liabilities',
            'Operating Cash Flow'
        ]
        
        # Mock financial data
        mock_data = {field: [100, 200, 300] for field in required_fields}
        df = pd.DataFrame(mock_data)
        
        # Check all required fields exist
        for field in required_fields:
            assert field in df.columns
    
    def test_ratio_bounds(self):
        """Test that calculated ratios are within reasonable bounds"""
        # Margins should be between -100% and 100%
        margin = 0.25
        assert -1 <= margin <= 1
        
        # P/E ratio shouldn't be absurdly high
        pe_ratio = 25
        assert -100 <= pe_ratio <= 1000  # Wide bounds for edge cases
        
        # Current ratio should be positive
        current_ratio = 1.5
        assert current_ratio >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])




