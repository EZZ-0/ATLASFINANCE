"""
UNIT TESTS - INDIVIDUAL MODULES
================================
Tests each module's functions in isolation.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import pandas as pd
import numpy as np
from datetime import datetime

# Import modules to test
from ticker_validator import TickerValidator, quick_validate, full_validate
from format_helpers import format_large_number, format_change, external_link


class TestTickerValidator:
    """Test Ticker Validation Module"""
    
    def test_valid_tickers(self):
        """Test valid ticker formats"""
        validator = TickerValidator()
        
        valid_tickers = ["AAPL", "MSFT", "GOOGL", "BRK-B", "BRK.B"]
        for ticker in valid_tickers:
            is_valid, message, _ = validator.validate(ticker)
            assert is_valid, f"Failed for {ticker}: {message}"
    
    def test_invalid_tickers(self):
        """Test invalid ticker formats"""
        validator = TickerValidator()
        
        invalid_tickers = [
            "",
            "TOOLONGTICKER",
            "123",
            "AAPL; DROP TABLE",
            "<script>alert('xss')</script>",
            "../etc/passwd"
        ]
        
        for ticker in invalid_tickers:
            is_valid, _, _ = validator.validate(ticker)
            assert not is_valid, f"Should have rejected: {ticker}"
    
    def test_sanitization(self):
        """Test ticker sanitization"""
        validator = TickerValidator()
        
        assert validator.sanitize("  aapl  ") == "AAPL"
        assert validator.sanitize("msft") == "MSFT"
        assert validator.sanitize("") == ""
    
    def test_batch_validation(self):
        """Test batch validation"""
        validator = TickerValidator()
        
        tickers = ["AAPL", "INVALID123", "MSFT"]
        results = validator.validate_batch(tickers)
        
        assert results["AAPL"]["valid"] == True
        assert results["INVALID123"]["valid"] == False
        assert results["MSFT"]["valid"] == True


class TestFormatHelpers:
    """Test Format Helper Functions"""
    
    def test_format_large_number(self):
        """Test number formatting"""
        # Billions
        assert "B" in format_large_number(1_500_000_000, format_type='currency')
        
        # Millions
        assert "M" in format_large_number(50_000_000, format_type='currency')
        
        # Thousands
        assert "K" in format_large_number(5_000, format_type='currency')
        
        # Small numbers
        result = format_large_number(100, format_type='currency')
        assert "$" in result
    
    def test_format_change(self):
        """Test change formatting with colors"""
        # Positive change
        positive = format_change(5.5)
        assert "🟢" in positive or "+" in positive
        
        # Negative change
        negative = format_change(-3.2)
        assert "🔴" in negative or "-" in negative
        
        # Zero change
        zero = format_change(0.0)
        assert "⚪" in zero or "0.0" in zero
    
    def test_external_link(self):
        """Test external link generation"""
        link = external_link("https://example.com", "Test Link")
        
        assert "href" in link
        assert "target=\"_blank\"" in link
        assert "rel=\"noopener noreferrer\"" in link
        assert "Test Link" in link


class TestFinancialCalculations:
    """Test Financial Calculation Functions"""
    
    def test_ratio_calculations(self):
        """Test basic ratio calculations"""
        # Mock financial data
        net_income = 100_000_000
        revenue = 500_000_000
        equity = 400_000_000
        
        # Calculate ratios
        net_margin = net_income / revenue
        roe = net_income / equity
        
        assert 0 < net_margin < 1
        assert 0 < roe < 1
        assert net_margin == 0.2  # 20%
        assert roe == 0.25  # 25%
    
    def test_growth_rate_calculation(self):
        """Test CAGR calculation"""
        initial_value = 100
        final_value = 200
        years = 5
        
        # CAGR formula: (FV/PV)^(1/n) - 1
        cagr = (final_value / initial_value) ** (1/years) - 1
        
        assert 0.1 < cagr < 0.2  # ~14.87%
        assert abs(cagr - 0.1487) < 0.001


class TestDataExtraction:
    """Test Data Extraction Functions"""
    
    def test_backend_import(self):
        """Test that usa_backend imports successfully"""
        try:
            import usa_backend
            assert hasattr(usa_backend, 'extract_financials')
        except Exception as e:
            pytest.fail(f"Failed to import usa_backend: {e}")
    
    def test_dcf_modeling_import(self):
        """Test that dcf_modeling imports successfully"""
        try:
            import dcf_modeling
            assert hasattr(dcf_modeling, 'run_dcf_valuation')
        except Exception as e:
            pytest.fail(f"Failed to import dcf_modeling: {e}")


class TestAnalysisModules:
    """Test Analysis Modules"""
    
    def test_earnings_analysis_import(self):
        """Test earnings analysis module"""
        try:
            from earnings_analysis import analyze_earnings_history
            assert callable(analyze_earnings_history)
        except Exception as e:
            pytest.fail(f"Failed to import earnings_analysis: {e}")
    
    def test_dividend_analysis_import(self):
        """Test dividend analysis module"""
        try:
            from dividend_analysis import analyze_dividends
            assert callable(analyze_dividends)
        except Exception as e:
            pytest.fail(f"Failed to import dividend_analysis: {e}")
    
    def test_governance_analysis_import(self):
        """Test governance analysis module"""
        try:
            from governance_analysis import analyze_governance
            assert callable(analyze_governance)
        except Exception as e:
            pytest.fail(f"Failed to import governance_analysis: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])




