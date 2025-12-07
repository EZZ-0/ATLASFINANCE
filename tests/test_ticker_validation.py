"""
Ticker Validation Tests - TASK-E003, E004, E005
================================================
Validates AAPL, MSFT, JNJ metrics against reference data.

Run with: pytest tests/test_ticker_validation.py -v
Or: python tests/test_ticker_validation.py (standalone mode)

Author: ATLAS Financial Intelligence
Created: 2025-12-07
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import pandas as pd
from typing import Dict, Any, Optional

# Reference values (Yahoo Finance Dec 2024)
REFERENCE_DATA = {
    'AAPL': {
        'name': 'Apple Inc.',
        'pe_range': (35.0, 45.0),
        'revenue_min': 380e9,
        'revenue_max': 400e9,
        'roe_range': (100.0, 200.0),  # Very high due to buybacks
        'beta_range': (1.1, 1.4),
        'notes': 'ROE extremely high due to share buybacks reducing equity'
    },
    'MSFT': {
        'name': 'Microsoft Corporation',
        'pe_range': (32.0, 40.0),
        'revenue_min': 240e9,
        'revenue_max': 255e9,
        'roe_range': (30.0, 45.0),
        'beta_range': (0.8, 1.1),
        'notes': 'Very stable metrics, good baseline'
    },
    'JNJ': {
        'name': 'Johnson & Johnson',
        'pe_range': (14.0, 20.0),
        'revenue_min': 80e9,
        'revenue_max': 90e9,
        'roe_range': (15.0, 25.0),
        'beta_range': (0.4, 0.7),
        'notes': 'Kenvue spinoff in 2023 may affect historical data'
    }
}

TOLERANCE_PCT = 0.05  # 5% tolerance


def get_metric_from_df(df: pd.DataFrame, keys: list, column_idx: int = 0) -> Optional[float]:
    """
    Safely extract a metric from a DataFrame.
    Handles both row-indexed and column-indexed formats.
    """
    if df is None or df.empty:
        return None
    
    for key in keys:
        try:
            # Try row index lookup (yfinance format)
            if key in df.index:
                value = df.loc[key].iloc[column_idx] if len(df.loc[key]) > column_idx else df.loc[key]
                if pd.notna(value):
                    return float(value)
            
            # Try column lookup (SEC format)
            if key in df.columns:
                value = df[key].iloc[0] if len(df[key]) > 0 else None
                if pd.notna(value):
                    return float(value)
        except (KeyError, IndexError, TypeError, ValueError):
            continue
    
    return None


class TestTickerExtraction:
    """Test that extraction works for key tickers."""
    
    @pytest.fixture(scope='class')
    def extractor(self):
        """Create extractor instance (shared across tests)."""
        from usa_backend import USAFinancialExtractor
        return USAFinancialExtractor()
    
    @pytest.mark.parametrize("ticker", ['AAPL', 'MSFT', 'JNJ'])
    def test_extraction_succeeds(self, extractor, ticker):
        """Test that extraction completes without error."""
        result = extractor.extract_financials(ticker)
        
        assert result is not None, f"{ticker}: No result returned"
        assert result.get('status') != 'error', f"{ticker}: Extraction failed: {result.get('message')}"
        assert 'income_statement' in result, f"{ticker}: Missing income_statement"
        assert 'balance_sheet' in result, f"{ticker}: Missing balance_sheet"
        assert 'cash_flow' in result, f"{ticker}: Missing cash_flow"
    
    @pytest.mark.parametrize("ticker", ['AAPL', 'MSFT', 'JNJ'])
    def test_has_company_info(self, extractor, ticker):
        """Test that company info is extracted."""
        result = extractor.extract_financials(ticker)
        
        assert result.get('ticker') == ticker
        assert result.get('company_name') is not None


class TestRevenueValidation:
    """Test revenue extraction accuracy."""
    
    @pytest.fixture(scope='class')
    def extractor(self):
        from usa_backend import USAFinancialExtractor
        return USAFinancialExtractor()
    
    @pytest.mark.parametrize("ticker", ['AAPL', 'MSFT', 'JNJ'])
    def test_revenue_in_expected_range(self, extractor, ticker):
        """Test that extracted revenue is within expected range."""
        result = extractor.extract_financials(ticker)
        income = result.get('income_statement')
        
        revenue_keys = ['Total Revenue', 'TotalRevenue', 'Revenue', 'Revenues']
        revenue = get_metric_from_df(income, revenue_keys)
        
        if revenue is None:
            pytest.skip(f"{ticker}: Could not find revenue in income statement")
        
        ref = REFERENCE_DATA[ticker]
        
        # Check range
        assert ref['revenue_min'] <= revenue <= ref['revenue_max'], \
            f"{ticker}: Revenue ${revenue/1e9:.1f}B outside expected range " \
            f"${ref['revenue_min']/1e9:.0f}B - ${ref['revenue_max']/1e9:.0f}B"


class TestRatioValidation:
    """Test ratio calculation accuracy."""
    
    @pytest.fixture(scope='class')
    def extractor(self):
        from usa_backend import USAFinancialExtractor
        return USAFinancialExtractor()
    
    @pytest.mark.parametrize("ticker", ['AAPL', 'MSFT', 'JNJ'])
    def test_ratios_calculated(self, extractor, ticker):
        """Test that ratios are calculated and present."""
        result = extractor.extract_financials(ticker)
        ratios = result.get('ratios')
        
        assert ratios is not None, f"{ticker}: No ratios calculated"
        assert not ratios.empty, f"{ticker}: Ratios DataFrame is empty"
        
        # Check at least some expected ratios exist
        expected = ['ROE', 'Current_Ratio', 'Debt_to_Equity']
        found = [r for r in expected if r in ratios.index]
        
        assert len(found) > 0, f"{ticker}: None of expected ratios found: {expected}"
    
    @pytest.mark.parametrize("ticker", ['AAPL', 'MSFT', 'JNJ'])
    def test_roe_in_expected_range(self, extractor, ticker):
        """Test that ROE is within expected range for each ticker."""
        result = extractor.extract_financials(ticker)
        ratios = result.get('ratios')
        
        if ratios is None or 'ROE' not in ratios.index:
            pytest.skip(f"{ticker}: ROE not available")
        
        roe = get_metric_from_df(ratios, ['ROE'])
        
        if roe is None:
            pytest.skip(f"{ticker}: ROE is None")
        
        # Convert to percentage if in decimal form
        if abs(roe) < 5:  # Likely in decimal form
            roe = roe * 100
        
        ref = REFERENCE_DATA[ticker]
        
        assert ref['roe_range'][0] <= roe <= ref['roe_range'][1], \
            f"{ticker}: ROE {roe:.1f}% outside expected range " \
            f"{ref['roe_range'][0]:.0f}% - {ref['roe_range'][1]:.0f}%"


class TestQuantEngineValidation:
    """Test quant engine beta calculations."""
    
    @pytest.fixture(scope='class')
    def extractor(self):
        from usa_backend import USAFinancialExtractor
        return USAFinancialExtractor()
    
    @pytest.mark.parametrize("ticker", ['AAPL', 'MSFT', 'JNJ'])
    def test_quant_data_available(self, extractor, ticker):
        """Test that quant analysis data is extracted."""
        result = extractor.extract_financials(ticker, include_quant=True)
        quant = result.get('quant_analysis')
        
        # Quant may not always be available (depends on data availability)
        if quant is None:
            pytest.skip(f"{ticker}: Quant analysis not available")
        
        # Check for key quant fields
        assert 'beta_market' in quant or 'cost_of_equity' in quant, \
            f"{ticker}: Missing key quant metrics"


class TestDataConsistency:
    """Test data consistency across statements."""
    
    @pytest.fixture(scope='class')
    def extractor(self):
        from usa_backend import USAFinancialExtractor
        return USAFinancialExtractor()
    
    @pytest.mark.parametrize("ticker", ['AAPL', 'MSFT', 'JNJ'])
    def test_net_income_consistency(self, extractor, ticker):
        """
        Test that net income appears consistently across statements.
        Net income should appear in both income statement and cash flow.
        """
        result = extractor.extract_financials(ticker)
        
        income = result.get('income_statement')
        cashflow = result.get('cash_flow')
        
        # Get net income from income statement
        ni_income = get_metric_from_df(income, ['Net Income', 'NetIncome', 'Net Income Common Stockholders'])
        
        # Get net income from cash flow
        ni_cf = get_metric_from_df(cashflow, ['Net Income', 'NetIncome', 'Net Income From Continuing Operations'])
        
        if ni_income is None or ni_cf is None:
            pytest.skip(f"{ticker}: Could not find net income in both statements")
        
        # They should be within 10% of each other (accounting for timing differences)
        diff_pct = abs(ni_income - ni_cf) / max(abs(ni_income), abs(ni_cf), 1)
        
        assert diff_pct < 0.10, \
            f"{ticker}: Net income mismatch - IS: ${ni_income/1e9:.1f}B, CF: ${ni_cf/1e9:.1f}B ({diff_pct:.1%} diff)"


# ==========================================
# STANDALONE RUNNER
# ==========================================

def run_validation_standalone():
    """Run validation tests in standalone mode (without pytest)."""
    print("=" * 60)
    print("TICKER VALIDATION - Standalone Mode")
    print("=" * 60)
    
    try:
        from usa_backend import USAFinancialExtractor
    except ImportError as e:
        print(f"[FAIL] Cannot import usa_backend: {e}")
        return False
    
    extractor = USAFinancialExtractor()
    all_passed = True
    
    for ticker, ref in REFERENCE_DATA.items():
        print(f"\n[TEST] {ticker} ({ref['name']})")
        print("-" * 40)
        
        try:
            result = extractor.extract_financials(ticker)
            
            if result.get('status') == 'error':
                print(f"  [FAIL] Extraction error: {result.get('message')}")
                all_passed = False
                continue
            
            print(f"  [OK] Extraction successful")
            
            # Check revenue
            income = result.get('income_statement')
            revenue = get_metric_from_df(income, ['Total Revenue', 'TotalRevenue', 'Revenue'])
            
            if revenue:
                in_range = ref['revenue_min'] <= revenue <= ref['revenue_max']
                status = "[OK]" if in_range else "[WARN]"
                print(f"  {status} Revenue: ${revenue/1e9:.1f}B (expected ${ref['revenue_min']/1e9:.0f}B - ${ref['revenue_max']/1e9:.0f}B)")
                if not in_range:
                    all_passed = False
            else:
                print(f"  [SKIP] Revenue not found")
            
            # Check ratios
            ratios = result.get('ratios')
            if ratios is not None and 'ROE' in ratios.index:
                roe = get_metric_from_df(ratios, ['ROE'])
                if roe:
                    if abs(roe) < 5:
                        roe *= 100
                    in_range = ref['roe_range'][0] <= roe <= ref['roe_range'][1]
                    status = "[OK]" if in_range else "[WARN]"
                    print(f"  {status} ROE: {roe:.1f}% (expected {ref['roe_range'][0]:.0f}% - {ref['roe_range'][1]:.0f}%)")
            else:
                print(f"  [SKIP] ROE not available")
            
            # Notes
            print(f"  [NOTE] {ref['notes']}")
            
        except Exception as e:
            print(f"  [FAIL] Exception: {e}")
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("[PASS] All validation tests passed")
    else:
        print("[WARN] Some tests failed or had warnings")
    print("=" * 60)
    
    return all_passed


if __name__ == "__main__":
    # Run standalone if executed directly
    success = run_validation_standalone()
    sys.exit(0 if success else 1)

