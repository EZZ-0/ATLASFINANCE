"""
FCF Calculator Tests - TASK-E009 Validation
=============================================
Tests for calculations/fcf_calculator.py

Run with: pytest tests/test_fcf_calculator.py -v
Or: python tests/test_fcf_calculator.py (standalone mode)

Author: ATLAS Financial Intelligence
Date: 2025-12-07
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from calculations.fcf_calculator import (
    FCFCalculator, FCFMethod, FCFResult,
    calculate_fcf, calculate_all_fcf
)


# ==========================================
# TEST DATA
# ==========================================

SAMPLE_AAPL_FINANCIALS = {
    'operating_cash_flow': 110_000_000_000,
    'capital_expenditures': 11_000_000_000,
    'interest_expense': 3_000_000_000,
    'net_income': 97_000_000_000,
    'depreciation': 11_000_000_000,
    'amortization': 500_000_000,
    'change_in_working_capital': -2_000_000_000,  # Decrease = positive for FCF
    'ebit': 120_000_000_000,
    'tax_rate': 0.16
}

MINIMAL_FINANCIALS = {
    'operating_cash_flow': 50_000_000_000,
    'capital_expenditures': 5_000_000_000,
}

NEGATIVE_OCF_FINANCIALS = {
    'operating_cash_flow': -10_000_000_000,
    'capital_expenditures': 5_000_000_000,
}


# ==========================================
# SIMPLE FCF TESTS
# ==========================================

class TestSimpleFCF:
    """Test Simple FCF: OCF - CapEx"""
    
    def test_simple_fcf_calculation(self):
        """Test basic Simple FCF calculation."""
        calc = FCFCalculator(SAMPLE_AAPL_FINANCIALS)
        result = calc.calculate_simple_fcf()
        
        assert result is not None
        assert result.method == FCFMethod.SIMPLE
        # Expected: 110B - 11B = 99B
        assert result.value == pytest.approx(99_000_000_000, rel=0.01)
    
    def test_simple_fcf_formula(self):
        """Test formula string is correct."""
        calc = FCFCalculator(SAMPLE_AAPL_FINANCIALS)
        result = calc.calculate_simple_fcf()
        
        assert "OCF - CapEx" in result.formula
    
    def test_simple_fcf_components(self):
        """Test components are returned correctly."""
        calc = FCFCalculator(SAMPLE_AAPL_FINANCIALS)
        result = calc.calculate_simple_fcf()
        
        assert 'operating_cash_flow' in result.components
        assert 'capital_expenditures' in result.components
        assert result.components['operating_cash_flow'] == 110_000_000_000
    
    def test_simple_fcf_missing_ocf(self):
        """Test returns None when OCF missing."""
        calc = FCFCalculator({'capital_expenditures': 5_000_000_000})
        result = calc.calculate_simple_fcf()
        
        assert result is None
    
    def test_simple_fcf_negative_ocf(self):
        """Test handles negative OCF correctly."""
        calc = FCFCalculator(NEGATIVE_OCF_FINANCIALS)
        result = calc.calculate_simple_fcf()
        
        assert result is not None
        # Expected: -10B - 5B = -15B
        assert result.value == pytest.approx(-15_000_000_000, rel=0.01)


# ==========================================
# LEVERED FCF TESTS
# ==========================================

class TestLeveredFCF:
    """Test Levered FCF: OCF - CapEx - Interest"""
    
    def test_levered_fcf_calculation(self):
        """Test basic Levered FCF calculation."""
        calc = FCFCalculator(SAMPLE_AAPL_FINANCIALS)
        result = calc.calculate_levered_fcf()
        
        assert result is not None
        assert result.method == FCFMethod.LEVERED
        # Expected: 110B - 11B - 3B = 96B
        assert result.value == pytest.approx(96_000_000_000, rel=0.01)
    
    def test_levered_fcf_no_interest(self):
        """Test with no interest expense."""
        calc = FCFCalculator(MINIMAL_FINANCIALS)
        result = calc.calculate_levered_fcf()
        
        assert result is not None
        # Expected: 50B - 5B - 0 = 45B
        assert result.value == pytest.approx(45_000_000_000, rel=0.01)


# ==========================================
# OWNER EARNINGS TESTS
# ==========================================

class TestOwnerEarnings:
    """Test Owner Earnings: NI + D&A - CapEx - ΔWC"""
    
    def test_owner_earnings_calculation(self):
        """Test basic Owner Earnings calculation."""
        calc = FCFCalculator(SAMPLE_AAPL_FINANCIALS)
        result = calc.calculate_owner_earnings()
        
        assert result is not None
        assert result.method == FCFMethod.OWNER_EARNINGS
        # Expected: 97B + 11.5B - 11B - (-2B) = 99.5B
        expected = 97_000_000_000 + 11_500_000_000 - 11_000_000_000 + 2_000_000_000
        assert result.value == pytest.approx(expected, rel=0.01)
    
    def test_owner_earnings_formula(self):
        """Test formula includes Buffett reference."""
        calc = FCFCalculator(SAMPLE_AAPL_FINANCIALS)
        result = calc.calculate_owner_earnings()
        
        assert "NI" in result.formula
        assert "D&A" in result.formula
        assert "ΔWC" in result.formula
    
    def test_owner_earnings_missing_net_income(self):
        """Test returns None when Net Income missing."""
        calc = FCFCalculator({
            'depreciation': 11_000_000_000,
            'capital_expenditures': 5_000_000_000,
        })
        result = calc.calculate_owner_earnings()
        
        assert result is None


# ==========================================
# FCFF TESTS
# ==========================================

class TestFCFF:
    """Test FCFF: EBIT(1-T) + D&A - CapEx - ΔWC"""
    
    def test_fcff_calculation(self):
        """Test basic FCFF calculation."""
        calc = FCFCalculator(SAMPLE_AAPL_FINANCIALS)
        result = calc.calculate_fcff()
        
        assert result is not None
        assert result.method == FCFMethod.FCFF
        # Expected: 120B * 0.84 + 11.5B - 11B + 2B = 103.3B
        nopat = 120_000_000_000 * (1 - 0.16)
        d_and_a = 11_000_000_000 + 500_000_000
        expected = nopat + d_and_a - 11_000_000_000 + 2_000_000_000
        assert result.value == pytest.approx(expected, rel=0.01)
    
    def test_fcff_nopat_component(self):
        """Test NOPAT is calculated correctly."""
        calc = FCFCalculator(SAMPLE_AAPL_FINANCIALS)
        result = calc.calculate_fcff()
        
        assert 'nopat' in result.components
        expected_nopat = 120_000_000_000 * 0.84
        assert result.components['nopat'] == pytest.approx(expected_nopat, rel=0.01)
    
    def test_fcff_default_tax_rate(self):
        """Test uses 21% default when tax rate not provided."""
        financials = {
            'ebit': 100_000_000_000,
            'depreciation': 10_000_000_000,
            'capital_expenditures': 5_000_000_000,
        }
        calc = FCFCalculator(financials)
        result = calc.calculate_fcff()
        
        # Should use 21% default
        expected_nopat = 100_000_000_000 * 0.79
        assert result.components['nopat'] == pytest.approx(expected_nopat, rel=0.01)
    
    def test_fcff_missing_ebit(self):
        """Test returns None when EBIT missing."""
        calc = FCFCalculator({
            'net_income': 97_000_000_000,
            'depreciation': 11_000_000_000,
        })
        result = calc.calculate_fcff()
        
        assert result is None


# ==========================================
# CALCULATE ALL TESTS
# ==========================================

class TestCalculateAll:
    """Test calculate_all() method."""
    
    def test_returns_all_methods(self):
        """Test all 4 methods are returned."""
        calc = FCFCalculator(SAMPLE_AAPL_FINANCIALS)
        results = calc.calculate_all()
        
        assert 'simple' in results
        assert 'levered' in results
        assert 'owner_earnings' in results
        assert 'fcff' in results
    
    def test_all_methods_have_values(self):
        """Test all methods calculate successfully with full data."""
        calc = FCFCalculator(SAMPLE_AAPL_FINANCIALS)
        results = calc.calculate_all()
        
        for name, result in results.items():
            assert result is not None, f"{name} should not be None"
            assert isinstance(result.value, (int, float)), f"{name} value should be numeric"


# ==========================================
# RECOMMENDATION ENGINE TESTS
# ==========================================

class TestRecommendation:
    """Test get_recommended_method()."""
    
    def test_recommends_fcff_with_full_data(self):
        """Test recommends FCFF when EBIT and D&A available."""
        calc = FCFCalculator(SAMPLE_AAPL_FINANCIALS)
        method, reason = calc.get_recommended_method()
        
        assert method == FCFMethod.FCFF
        assert "valuation" in reason.lower() or "ebit" in reason.lower()
    
    def test_recommends_simple_with_minimal_data(self):
        """Test recommends Simple FCF when only OCF available."""
        calc = FCFCalculator(MINIMAL_FINANCIALS)
        method, reason = calc.get_recommended_method()
        
        assert method == FCFMethod.SIMPLE


# ==========================================
# CONVENIENCE FUNCTIONS TESTS
# ==========================================

class TestConvenienceFunctions:
    """Test module-level convenience functions."""
    
    def test_calculate_fcf_function(self):
        """Test calculate_fcf() convenience function."""
        result = calculate_fcf(SAMPLE_AAPL_FINANCIALS, FCFMethod.SIMPLE)
        
        assert result is not None
        assert result.method == FCFMethod.SIMPLE
    
    def test_calculate_all_fcf_function(self):
        """Test calculate_all_fcf() convenience function."""
        results = calculate_all_fcf(SAMPLE_AAPL_FINANCIALS)
        
        assert len(results) == 4
        assert all(r is not None for r in results.values())


# ==========================================
# FIELD NORMALIZATION TESTS
# ==========================================

class TestFieldNormalization:
    """Test that various field name formats are handled."""
    
    def test_yfinance_format(self):
        """Test yfinance-style field names."""
        financials = {
            'operatingCashflow': 100_000_000_000,
            'capitalExpenditures': 10_000_000_000,
        }
        calc = FCFCalculator(financials)
        result = calc.calculate_simple_fcf()
        
        assert result is not None
        assert result.value == 90_000_000_000
    
    def test_sec_format(self):
        """Test SEC-style field names."""
        financials = {
            'operating_cash_flow': 100_000_000_000,
            'capital_expenditures': 10_000_000_000,
        }
        calc = FCFCalculator(financials)
        result = calc.calculate_simple_fcf()
        
        assert result is not None
        assert result.value == 90_000_000_000


# ==========================================
# FCF RESULT TESTS
# ==========================================

class TestFCFResult:
    """Test FCFResult dataclass."""
    
    def test_to_dict(self):
        """Test to_dict() serialization."""
        calc = FCFCalculator(SAMPLE_AAPL_FINANCIALS)
        result = calc.calculate_simple_fcf()
        
        d = result.to_dict()
        
        assert d['method'] == 'simple'
        assert 'value' in d
        assert 'components' in d
        assert 'formula' in d
        assert 'description' in d


# ==========================================
# STANDALONE RUNNER
# ==========================================

def run_standalone_tests():
    """Run tests in standalone mode."""
    print("=" * 60)
    print("FCF CALCULATOR VALIDATION - Standalone Mode")
    print("=" * 60)
    
    calc = FCFCalculator(SAMPLE_AAPL_FINANCIALS)
    results = calc.calculate_all()
    
    # Expected values
    expected = {
        'simple': 99_000_000_000,
        'levered': 96_000_000_000,
        'owner_earnings': 99_500_000_000,
        'fcff': 103_300_000_000
    }
    
    all_passed = True
    
    for name, result in results.items():
        if result is None:
            print(f"[FAIL] {name}: Result is None")
            all_passed = False
            continue
        
        exp = expected[name]
        diff = abs(result.value - exp) / exp
        
        if diff < 0.01:
            print(f"[PASS] {name}: ${result.value/1e9:.1f}B (expected ${exp/1e9:.1f}B)")
        else:
            print(f"[FAIL] {name}: ${result.value/1e9:.1f}B (expected ${exp/1e9:.1f}B, diff {diff:.1%})")
            all_passed = False
    
    # Test recommendation
    method, reason = calc.get_recommended_method()
    print(f"\n[INFO] Recommended: {method.value}")
    print(f"[INFO] Reason: {reason}")
    
    print("\n" + "=" * 60)
    if all_passed:
        print("[PASS] All FCF calculator tests passed!")
    else:
        print("[FAIL] Some tests failed")
    print("=" * 60)
    
    return all_passed


if __name__ == "__main__":
    success = run_standalone_tests()
    sys.exit(0 if success else 1)

