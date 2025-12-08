"""
INVESTMENT SUMMARY - AUTOMATED LOGIC TESTS
==========================================
Tests the intelligence and logic of Investment Summary generation
WITHOUT requiring Streamlit UI or real financial data.

This validates:
- Bull/Bear case generation logic
- Risk assessment logic
- Valuation range calculations
- Red flags detection
- Edge case handling

Run: python test_investment_summary_logic.py
"""

import pandas as pd
import sys
from investment_summary import InvestmentSummaryGenerator

# Test counter
tests_run = 0
tests_passed = 0
tests_failed = 0

def test(name):
    """Decorator to track tests"""
    def decorator(func):
        def wrapper():
            global tests_run, tests_passed, tests_failed
            tests_run += 1
            try:
                func()
                tests_passed += 1
                print(f"✅ {name}")
                return True
            except AssertionError as e:
                tests_failed += 1
                print(f"❌ {name}")
                print(f"   Error: {str(e)}")
                return False
            except Exception as e:
                tests_failed += 1
                print(f"❌ {name} (Exception)")
                print(f"   Error: {str(e)}")
                return False
        return wrapper
    return decorator

# ==========================================
# TEST SUITE 1: BULL CASE LOGIC
# ==========================================

@test("Bull Case: High ROE triggers profitability mention")
def test_bull_high_roe():
    """High ROE (25%) should trigger "Strong profitability" in bull case"""
    mock = {
        'ticker': 'TEST',
        'company_name': 'Test Corp',
        'ratios': pd.DataFrame({
            'ROE': [0.25],
            'Gross_Margin': [0.20],
            'Operating_Margin': [0.10],
            'Current_Ratio': [1.0],
            'Debt_to_Equity': [1.0],
            'PE_Ratio': [20.0],
            'Net_Income': [100000000],
            'Operating_Cash_Flow': [80000000]
        }).T,
        'growth_rates': {},
        'income_statement': pd.DataFrame(),
        'balance_sheet': pd.DataFrame(),
        'market_data': {}
    }
    
    gen = InvestmentSummaryGenerator(mock)
    bull_case = gen.generate_bull_case()
    
    assert len(bull_case) == 3, f"Expected 3 bull points, got {len(bull_case)}"
    
    # Should mention profitability or ROE
    has_profitability = any(
        'profitability' in point.lower() or 'roe' in point.lower() 
        for point in bull_case
    )
    assert has_profitability, f"Bull case should mention profitability for ROE 25%. Got: {bull_case}"

@test("Bull Case: High margins trigger pricing power mention")
def test_bull_high_margins():
    """Gross margin > 40% should trigger margin strength mention"""
    mock = {
        'ticker': 'TEST',
        'company_name': 'Test Corp',
        'ratios': pd.DataFrame({
            'ROE': [0.10],
            'Gross_Margin': [0.45],  # 45%
            'Operating_Margin': [0.20],
            'Current_Ratio': [1.0],
            'Debt_to_Equity': [1.0]
        }).T,
        'growth_rates': {},
        'income_statement': pd.DataFrame(),
        'balance_sheet': pd.DataFrame(),
        'market_data': {}
    }
    
    gen = InvestmentSummaryGenerator(mock)
    bull_case = gen.generate_bull_case()
    
    has_margin = any('margin' in point.lower() for point in bull_case)
    assert has_margin, f"Bull case should mention margins for 45% gross margin. Got: {bull_case}"

@test("Bull Case: Strong liquidity triggers mention")
def test_bull_strong_liquidity():
    """Current Ratio > 2.0 should trigger liquidity strength"""
    mock = {
        'ticker': 'TEST',
        'company_name': 'Test Corp',
        'ratios': pd.DataFrame({
            'ROE': [0.10],
            'Gross_Margin': [0.20],
            'Current_Ratio': [2.5],  # Strong liquidity
            'Debt_to_Equity': [0.3]
        }).T,
        'growth_rates': {},
        'income_statement': pd.DataFrame(),
        'balance_sheet': pd.DataFrame(),
        'market_data': {}
    }
    
    gen = InvestmentSummaryGenerator(mock)
    bull_case = gen.generate_bull_case()
    
    has_liquidity = any('liquidity' in point.lower() or 'current ratio' in point.lower() for point in bull_case)
    assert has_liquidity, f"Bull case should mention liquidity for CR 2.5. Got: {bull_case}"

# ==========================================
# TEST SUITE 2: BEAR CASE LOGIC
# ==========================================

@test("Bear Case: High P/E triggers valuation concern")
def test_bear_high_pe():
    """P/E > 40 should trigger "Premium valuation" warning"""
    mock = {
        'ticker': 'TEST',
        'company_name': 'Test Corp',
        'ratios': pd.DataFrame({
            'ROE': [0.15],
            'PE_Ratio': [45.0],  # High valuation
            'Debt_to_Equity': [0.5],
            'Current_Ratio': [1.5],
            'Operating_Margin': [0.15]
        }).T,
        'growth_rates': {'Total_Revenue_CAGR': 0.05},
        'income_statement': pd.DataFrame(),
        'balance_sheet': pd.DataFrame(),
        'market_data': {}
    }
    
    gen = InvestmentSummaryGenerator(mock)
    bear_case = gen.generate_bear_case()
    
    has_valuation_concern = any(
        'valuation' in point.lower() or 'p/e' in point.lower() 
        for point in bear_case
    )
    assert has_valuation_concern, f"Bear case should mention valuation for P/E 45. Got: {bear_case}"

@test("Bear Case: High leverage triggers debt concern")
def test_bear_high_leverage():
    """Debt/Equity > 2.0 should trigger leverage warning"""
    mock = {
        'ticker': 'TEST',
        'company_name': 'Test Corp',
        'ratios': pd.DataFrame({
            'ROE': [0.10],
            'PE_Ratio': [15.0],
            'Debt_to_Equity': [2.5],  # High debt
            'Current_Ratio': [1.0],
            'Operating_Margin': [0.10]
        }).T,
        'growth_rates': {},
        'income_statement': pd.DataFrame(),
        'balance_sheet': pd.DataFrame(),
        'market_data': {}
    }
    
    gen = InvestmentSummaryGenerator(mock)
    bear_case = gen.generate_bear_case()
    
    has_leverage_concern = any(
        'leverage' in point.lower() or 'debt' in point.lower() 
        for point in bear_case
    )
    assert has_leverage_concern, f"Bear case should mention leverage for D/E 2.5. Got: {bear_case}"

@test("Bear Case: Slow growth triggers concern")
def test_bear_slow_growth():
    """Revenue CAGR < 2% should trigger growth concern"""
    mock = {
        'ticker': 'TEST',
        'company_name': 'Test Corp',
        'ratios': pd.DataFrame({
            'ROE': [0.10],
            'PE_Ratio': [20.0],
            'Debt_to_Equity': [0.5],
            'Current_Ratio': [1.5]
        }).T,
        'growth_rates': {'Total_Revenue_CAGR': 0.01},  # 1% growth
        'income_statement': pd.DataFrame(),
        'balance_sheet': pd.DataFrame(),
        'market_data': {}
    }
    
    gen = InvestmentSummaryGenerator(mock)
    bear_case = gen.generate_bear_case()
    
    has_growth_concern = any('growth' in point.lower() for point in bear_case)
    assert has_growth_concern, f"Bear case should mention slow growth for 1% CAGR. Got: {bear_case}"

# ==========================================
# TEST SUITE 3: RISK ASSESSMENT LOGIC
# ==========================================

@test("Risk Assessment: Strong financials = LOW risk")
def test_risk_low():
    """Strong metrics should result in LOW financial health risk"""
    mock = {
        'ticker': 'TEST',
        'company_name': 'Test Corp',
        'ratios': pd.DataFrame({
            'Current_Ratio': [2.0],  # Strong
            'Debt_to_Equity': [0.3],  # Low debt
            'PE_Ratio': [15.0],
            'ROE': [0.20],
            'Operating_Margin': [0.20]
        }).T,
        'growth_rates': {'Total_Revenue_CAGR': 0.12},
        'income_statement': pd.DataFrame(),
        'balance_sheet': pd.DataFrame(),
        'market_data': {}
    }
    
    gen = InvestmentSummaryGenerator(mock)
    risks = gen.assess_risks()
    
    assert risks['Financial Health'] == 'LOW', f"Expected LOW financial risk, got {risks['Financial Health']}"
    assert risks['Valuation'] == 'LOW', f"Expected LOW valuation risk for P/E 15, got {risks['Valuation']}"
    assert risks['Growth'] == 'LOW', f"Expected LOW growth risk for 12% CAGR, got {risks['Growth']}"

@test("Risk Assessment: High debt = HIGH risk")
def test_risk_high():
    """High debt and low liquidity should result in HIGH risk"""
    mock = {
        'ticker': 'TEST',
        'company_name': 'Test Corp',
        'ratios': pd.DataFrame({
            'Current_Ratio': [0.8],  # Low liquidity
            'Debt_to_Equity': [3.0],  # High debt
            'PE_Ratio': [50.0],  # High valuation
            'ROE': [-0.05],  # Negative
            'Operating_Margin': [0.02]  # Thin
        }).T,
        'growth_rates': {'Total_Revenue_CAGR': -0.02},  # Declining
        'income_statement': pd.DataFrame(),
        'balance_sheet': pd.DataFrame(),
        'market_data': {}
    }
    
    gen = InvestmentSummaryGenerator(mock)
    risks = gen.assess_risks()
    
    assert risks['Financial Health'] == 'HIGH', f"Expected HIGH financial risk, got {risks['Financial Health']}"
    assert risks['Valuation'] == 'HIGH', f"Expected HIGH valuation risk for P/E 50, got {risks['Valuation']}"
    assert risks['Liquidity'] == 'HIGH', f"Expected HIGH liquidity risk for CR 0.8, got {risks['Liquidity']}"

@test("Risk Assessment: MODERATE case")
def test_risk_moderate():
    """Average metrics should result in MODERATE risks"""
    mock = {
        'ticker': 'TEST',
        'company_name': 'Test Corp',
        'ratios': pd.DataFrame({
            'Current_Ratio': [1.2],
            'Debt_to_Equity': [0.8],
            'PE_Ratio': [25.0],
            'ROE': [0.08],
            'Operating_Margin': [0.08]
        }).T,
        'growth_rates': {'Total_Revenue_CAGR': 0.05},
        'income_statement': pd.DataFrame(),
        'balance_sheet': pd.DataFrame(),
        'market_data': {}
    }
    
    gen = InvestmentSummaryGenerator(mock)
    risks = gen.assess_risks()
    
    assert risks['Financial Health'] == 'MODERATE', f"Expected MODERATE financial risk, got {risks['Financial Health']}"
    assert risks['Valuation'] == 'MODERATE', f"Expected MODERATE valuation risk, got {risks['Valuation']}"

# ==========================================
# TEST SUITE 4: RED FLAGS DETECTION
# ==========================================

@test("Red Flags: Healthy company shows no flags")
def test_red_flags_none():
    """Healthy company should show 'No major red flags'"""
    mock = {
        'ticker': 'TEST',
        'company_name': 'Test Corp',
        'ratios': pd.DataFrame({
            'ROE': [0.20],
            'Debt_to_Equity': [0.5],
            'Current_Ratio': [1.8],
            'PE_Ratio': [22.0]
        }).T,
        'growth_rates': {'Total_Revenue_CAGR': 0.08},
        'income_statement': pd.DataFrame(),
        'balance_sheet': pd.DataFrame(),
        'market_data': {}
    }
    
    gen = InvestmentSummaryGenerator(mock)
    red_flags = gen.detect_red_flags()
    
    assert len(red_flags) == 1, f"Expected 1 flag (no issues), got {len(red_flags)}"
    assert '✅' in red_flags[0], f"Expected green checkmark for healthy company, got: {red_flags[0]}"

@test("Red Flags: Negative ROE triggers warning")
def test_red_flags_negative_roe():
    """Negative ROE should trigger red flag"""
    mock = {
        'ticker': 'TEST',
        'company_name': 'Test Corp',
        'ratios': pd.DataFrame({
            'ROE': [-0.10],  # Negative!
            'Debt_to_Equity': [0.5],
            'Current_Ratio': [1.5],
            'PE_Ratio': [20.0]
        }).T,
        'growth_rates': {},
        'income_statement': pd.DataFrame(),
        'balance_sheet': pd.DataFrame(),
        'market_data': {}
    }
    
    gen = InvestmentSummaryGenerator(mock)
    red_flags = gen.detect_red_flags()
    
    has_roe_warning = any('negative' in flag.lower() and 'equity' in flag.lower() for flag in red_flags)
    assert has_roe_warning, f"Expected negative ROE warning. Got: {red_flags}"

@test("Red Flags: High debt triggers warning")
def test_red_flags_high_debt():
    """Debt/Equity > 2.0 should trigger red flag"""
    mock = {
        'ticker': 'TEST',
        'company_name': 'Test Corp',
        'ratios': pd.DataFrame({
            'ROE': [0.10],
            'Debt_to_Equity': [2.5],  # High!
            'Current_Ratio': [1.5],
            'PE_Ratio': [20.0]
        }).T,
        'growth_rates': {},
        'income_statement': pd.DataFrame(),
        'balance_sheet': pd.DataFrame(),
        'market_data': {}
    }
    
    gen = InvestmentSummaryGenerator(mock)
    red_flags = gen.detect_red_flags()
    
    has_debt_warning = any('leverage' in flag.lower() or 'debt' in flag.lower() for flag in red_flags)
    assert has_debt_warning, f"Expected high debt warning. Got: {red_flags}"

@test("Red Flags: Liquidity crisis triggers warning")
def test_red_flags_liquidity():
    """Current Ratio < 0.8 should trigger red flag"""
    mock = {
        'ticker': 'TEST',
        'company_name': 'Test Corp',
        'ratios': pd.DataFrame({
            'ROE': [0.10],
            'Debt_to_Equity': [0.5],
            'Current_Ratio': [0.6],  # Severe liquidity issue!
            'PE_Ratio': [20.0]
        }).T,
        'growth_rates': {},
        'income_statement': pd.DataFrame(),
        'balance_sheet': pd.DataFrame(),
        'market_data': {}
    }
    
    gen = InvestmentSummaryGenerator(mock)
    red_flags = gen.detect_red_flags()
    
    has_liquidity_warning = any('liquidity' in flag.lower() for flag in red_flags)
    assert has_liquidity_warning, f"Expected liquidity warning. Got: {red_flags}"

# ==========================================
# TEST SUITE 5: VALUATION RANGE
# ==========================================

@test("Valuation: Bear case is lower than base")
def test_valuation_bear_lower():
    """Bear case should be < base case"""
    mock = {
        'ticker': 'TEST',
        'company_name': 'Test Corp',
        'ratios': pd.DataFrame({
            'Current_Price': [100.0]
        }).T,
        'growth_rates': {},
        'income_statement': pd.DataFrame(),
        'balance_sheet': pd.DataFrame(),
        'market_data': {}
    }
    
    gen = InvestmentSummaryGenerator(mock)
    valuation = gen.calculate_valuation_range()
    
    assert valuation['bear_case'] < valuation['base_case'], \
        f"Bear case ({valuation['bear_case']}) should be < base ({valuation['base_case']})"

@test("Valuation: Bull case is higher than base")
def test_valuation_bull_higher():
    """Bull case should be > base case"""
    mock = {
        'ticker': 'TEST',
        'company_name': 'Test Corp',
        'ratios': pd.DataFrame({
            'Current_Price': [100.0]
        }).T,
        'growth_rates': {},
        'income_statement': pd.DataFrame(),
        'balance_sheet': pd.DataFrame(),
        'market_data': {}
    }
    
    gen = InvestmentSummaryGenerator(mock)
    valuation = gen.calculate_valuation_range()
    
    assert valuation['bull_case'] > valuation['base_case'], \
        f"Bull case ({valuation['bull_case']}) should be > base ({valuation['base_case']})"

@test("Valuation: Percentages are correct")
def test_valuation_percentages():
    """Valuation percentages should match actual ranges"""
    mock = {
        'ticker': 'TEST',
        'company_name': 'Test Corp',
        'ratios': pd.DataFrame({
            'Current_Price': [100.0]
        }).T,
        'growth_rates': {},
        'income_statement': pd.DataFrame(),
        'balance_sheet': pd.DataFrame(),
        'market_data': {}
    }
    
    gen = InvestmentSummaryGenerator(mock)
    valuation = gen.calculate_valuation_range()
    
    # Bear should be -20%
    expected_bear = 100.0 * 0.80
    assert abs(valuation['bear_case'] - expected_bear) < 0.01, \
        f"Bear case should be $80, got {valuation['bear_case']}"
    
    # Bull should be +25%
    expected_bull = 100.0 * 1.25
    assert abs(valuation['bull_case'] - expected_bull) < 0.01, \
        f"Bull case should be $125, got {valuation['bull_case']}"

# ==========================================
# TEST SUITE 6: EDGE CASES
# ==========================================

@test("Edge Case: Missing ROE doesn't crash")
def test_edge_missing_roe():
    """Missing ROE should be handled gracefully"""
    mock = {
        'ticker': 'TEST',
        'company_name': 'Test Corp',
        'ratios': pd.DataFrame({
            'PE_Ratio': [20.0],
            'Current_Ratio': [1.5]
            # No ROE!
        }).T,
        'growth_rates': {},
        'income_statement': pd.DataFrame(),
        'balance_sheet': pd.DataFrame(),
        'market_data': {}
    }
    
    gen = InvestmentSummaryGenerator(mock)
    
    # Should not crash
    bull_case = gen.generate_bull_case()
    bear_case = gen.generate_bear_case()
    risks = gen.assess_risks()
    
    assert len(bull_case) == 3, "Should still generate 3 bull points"
    assert len(bear_case) == 3, "Should still generate 3 bear points"

@test("Edge Case: All missing data doesn't crash")
def test_edge_all_missing():
    """Empty ratios should be handled gracefully"""
    mock = {
        'ticker': 'TEST',
        'company_name': 'Test Corp',
        'ratios': pd.DataFrame(),  # Empty!
        'growth_rates': {},
        'income_statement': pd.DataFrame(),
        'balance_sheet': pd.DataFrame(),
        'market_data': {}
    }
    
    gen = InvestmentSummaryGenerator(mock)
    
    # Should not crash
    bull_case = gen.generate_bull_case()
    bear_case = gen.generate_bear_case()
    risks = gen.assess_risks()
    red_flags = gen.detect_red_flags()
    valuation = gen.calculate_valuation_range()
    
    # Should have fallback values
    assert len(bull_case) == 3, "Should generate fallback bull points"
    assert len(bear_case) == 3, "Should generate fallback bear points"

@test("Edge Case: Negative price doesn't crash")
def test_edge_negative_price():
    """Negative or zero price should be handled"""
    mock = {
        'ticker': 'TEST',
        'company_name': 'Test Corp',
        'ratios': pd.DataFrame({
            'Current_Price': [-10.0]  # Invalid!
        }).T,
        'growth_rates': {},
        'income_statement': pd.DataFrame(),
        'balance_sheet': pd.DataFrame(),
        'market_data': {}
    }
    
    gen = InvestmentSummaryGenerator(mock)
    valuation = gen.calculate_valuation_range()
    
    # Should return zeros, not crash
    assert valuation['bear_case'] == 0
    assert valuation['base_case'] == 0
    assert valuation['bull_case'] == 0

# ==========================================
# RUN ALL TESTS
# ==========================================

def run_all_tests():
    print("="*60)
    print("INVESTMENT SUMMARY - AUTOMATED LOGIC TESTS")
    print("="*60)
    print()
    
    # Bull Case Tests
    print("📊 Testing Bull Case Logic...")
    test_bull_high_roe()
    test_bull_high_margins()
    test_bull_strong_liquidity()
    print()
    
    # Bear Case Tests
    print("📉 Testing Bear Case Logic...")
    test_bear_high_pe()
    test_bear_high_leverage()
    test_bear_slow_growth()
    print()
    
    # Risk Assessment Tests
    print("⚠️  Testing Risk Assessment...")
    test_risk_low()
    test_risk_high()
    test_risk_moderate()
    print()
    
    # Red Flags Tests
    print("🚩 Testing Red Flags Detection...")
    test_red_flags_none()
    test_red_flags_negative_roe()
    test_red_flags_high_debt()
    test_red_flags_liquidity()
    print()
    
    # Valuation Tests
    print("💰 Testing Valuation Range...")
    test_valuation_bear_lower()
    test_valuation_bull_higher()
    test_valuation_percentages()
    print()
    
    # Edge Case Tests
    print("🔬 Testing Edge Cases...")
    test_edge_missing_roe()
    test_edge_all_missing()
    test_edge_negative_price()
    print()
    
    # Summary
    print("="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Tests Run:    {tests_run}")
    print(f"Tests Passed: {tests_passed} ✅")
    print(f"Tests Failed: {tests_failed} ❌")
    print()
    
    if tests_failed == 0:
        print("🎉 ALL TESTS PASSED - Logic is 100% correct!")
        print()
        print("Next step: Manual testing for:")
        print("  1. Visual quality (UI appearance)")
        print("  2. Real data accuracy (compare with Yahoo Finance)")
        print("  3. Subjective quality (do insights sound smart?)")
        return 0
    else:
        print("❌ SOME TESTS FAILED - Review errors above")
        print()
        print("Fix issues before proceeding to manual tests")
        return 1

if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)


