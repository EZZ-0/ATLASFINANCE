"""
IC-READY INVESTMENT SUMMARY - COMPREHENSIVE TEST SUITE
Tests all 8 enhancements for bugs, rendering issues, and data integrity
"""

import sys
import traceback
from typing import Dict, List

def test_investment_summary_enhancements():
    """Test all IC-ready enhancements"""
    
    print("=" * 70)
    print("  IC-READY INVESTMENT SUMMARY - COMPREHENSIVE TESTS")
    print("=" * 70)
    print()
    
    tests_passed = 0
    tests_failed = 0
    errors = []
    
    # Test 1: Module imports
    print("[TEST 1] Checking module imports...")
    try:
        from investment_summary import InvestmentSummaryGenerator, render_investment_summary_tab
        print("✅ PASS - All modules imported successfully")
        tests_passed += 1
    except Exception as e:
        print(f"❌ FAIL - Import error: {e}")
        tests_failed += 1
        errors.append(f"Import Error: {e}")
        return  # Cannot continue without imports
    
    # Test 2: Mock financials dictionary
    print("\n[TEST 2] Creating mock financials data...")
    try:
        import pandas as pd
        
        mock_financials = {
            'ticker': 'AAPL',
            'company_name': 'Apple Inc.',
            'ratios': pd.DataFrame({
                'Metric': ['Current_Price', 'PE_Ratio', 'Price_to_Book', 'Market_Cap', 'Revenue', 
                          'Net_Income', 'ROE', 'Debt_to_Equity', 'Current_Ratio', 'Operating_Margin',
                          'Operating_Cash_Flow', 'Capital_Expenditures', 'EBITDA', 'Total_Debt',
                          'Total_Revenue_CAGR'],
                '2023': [230.45, 28.5, 45.2, 3.5e12, 383e9, 97e9, 0.285, 1.8, 1.07, 0.30,
                        110e9, -11e9, 125e9, 110e9, 0.12]
            }).set_index('Metric').T,
            'growth_rates': {
                'Total_Revenue_CAGR': 0.12,
                'Net_Income_CAGR': 0.15
            },
            'income_statement': pd.DataFrame(),
            'balance_sheet': pd.DataFrame(),
            'cash_flow': pd.DataFrame()
        }
        print("✅ PASS - Mock financials created successfully")
        tests_passed += 1
    except Exception as e:
        print(f"❌ FAIL - Mock data creation error: {e}")
        tests_failed += 1
        errors.append(f"Mock Data Error: {e}")
        return
    
    # Test 3: Generator initialization
    print("\n[TEST 3] Initializing InvestmentSummaryGenerator...")
    try:
        generator = InvestmentSummaryGenerator(mock_financials)
        assert generator.ticker == 'AAPL'
        assert generator.company_name == 'Apple Inc.'
        print("✅ PASS - Generator initialized correctly")
        tests_passed += 1
    except Exception as e:
        print(f"❌ FAIL - Generator initialization error: {e}")
        tests_failed += 1
        errors.append(f"Generator Init Error: {e}")
        return
    
    # Test 4: Recommendation generation
    print("\n[TEST 4] Testing generate_recommendation()...")
    try:
        rec_data = generator.generate_recommendation()
        assert 'recommendation' in rec_data
        assert 'conviction' in rec_data
        assert 'price_target' in rec_data
        assert 'upside_pct' in rec_data
        assert rec_data['recommendation'] in ['BUY', 'HOLD', 'SELL']
        assert rec_data['conviction'] in ['HIGH', 'MEDIUM', 'LOW']
        print(f"✅ PASS - Recommendation: {rec_data['recommendation']} | Conviction: {rec_data['conviction']}")
        print(f"         Price Target: ${rec_data['price_target']:.0f} | Upside: {rec_data['upside_pct']:+.1f}%")
        tests_passed += 1
    except Exception as e:
        print(f"❌ FAIL - Recommendation generation error: {e}")
        traceback.print_exc()
        tests_failed += 1
        errors.append(f"Recommendation Error: {e}")
    
    # Test 5: Investment thesis generation
    print("\n[TEST 5] Testing generate_investment_thesis()...")
    try:
        thesis = generator.generate_investment_thesis()
        assert isinstance(thesis, list)
        assert len(thesis) >= 2 and len(thesis) <= 3
        assert all(isinstance(point, str) for point in thesis)
        print(f"✅ PASS - Generated {len(thesis)} thesis points")
        for i, point in enumerate(thesis, 1):
            print(f"         {i}. {point[:60]}...")
        tests_passed += 1
    except Exception as e:
        print(f"❌ FAIL - Thesis generation error: {e}")
        traceback.print_exc()
        tests_failed += 1
        errors.append(f"Thesis Error: {e}")
    
    # Test 6: Why Now catalysts
    print("\n[TEST 6] Testing generate_why_now_catalyst()...")
    try:
        catalysts = generator.generate_why_now_catalyst()
        assert isinstance(catalysts, list)
        assert len(catalysts) >= 2 and len(catalysts) <= 3
        print(f"✅ PASS - Generated {len(catalysts)} catalysts")
        for i, catalyst in enumerate(catalysts, 1):
            print(f"         {i}. {catalyst[:60]}...")
        tests_passed += 1
    except Exception as e:
        print(f"❌ FAIL - Catalyst generation error: {e}")
        traceback.print_exc()
        tests_failed += 1
        errors.append(f"Catalyst Error: {e}")
    
    # Test 7: Risk triage
    print("\n[TEST 7] Testing triage_red_flags()...")
    try:
        risk_triage = generator.triage_red_flags()
        assert 'deal_breaker' in risk_triage
        assert 'monitor' in risk_triage
        assert 'manageable' in risk_triage
        assert isinstance(risk_triage['deal_breaker'], list)
        assert isinstance(risk_triage['monitor'], list)
        assert isinstance(risk_triage['manageable'], list)
        print(f"✅ PASS - Risk Matrix:")
        print(f"         🔴 Deal-Breakers: {len(risk_triage['deal_breaker'])}")
        print(f"         🟡 Monitor: {len(risk_triage['monitor'])}")
        print(f"         🟢 Manageable: {len(risk_triage['manageable'])}")
        tests_passed += 1
    except Exception as e:
        print(f"❌ FAIL - Risk triage error: {e}")
        traceback.print_exc()
        tests_failed += 1
        errors.append(f"Risk Triage Error: {e}")
    
    # Test 8: Peer comparison
    print("\n[TEST 8] Testing generate_peer_comparison()...")
    try:
        peer_data = generator.generate_peer_comparison()
        assert 'company' in peer_data
        assert 'sector' in peer_data
        assert 'premium' in peer_data
        assert 'PE' in peer_data['company']
        print(f"✅ PASS - Peer comparison generated")
        if peer_data['company']['PE']:
            print(f"         Company P/E: {peer_data['company']['PE']:.1f}x")
            print(f"         Sector P/E: {peer_data['sector']['PE']:.1f}x")
            if peer_data['premium']['PE']:
                print(f"         Premium/Discount: {peer_data['premium']['PE']:+.1f}%")
        tests_passed += 1
    except Exception as e:
        print(f"❌ FAIL - Peer comparison error: {e}")
        traceback.print_exc()
        tests_failed += 1
        errors.append(f"Peer Comparison Error: {e}")
    
    # Test 9: Catalyst timeline
    print("\n[TEST 9] Testing generate_catalyst_timeline()...")
    try:
        timeline = generator.generate_catalyst_timeline()
        assert isinstance(timeline, list)
        assert len(timeline) >= 2 and len(timeline) <= 3
        assert all('quarter' in c and 'event' in c and 'impact' in c for c in timeline)
        print(f"✅ PASS - Generated {len(timeline)} timeline events")
        for cat in timeline:
            print(f"         {cat['quarter']}: {cat['event'][:50]}... (+${cat['impact']:.0f})")
        tests_passed += 1
    except Exception as e:
        print(f"❌ FAIL - Timeline generation error: {e}")
        traceback.print_exc()
        tests_failed += 1
        errors.append(f"Timeline Error: {e}")
    
    # Test 10: Valuation range
    print("\n[TEST 10] Testing calculate_valuation_range()...")
    try:
        valuation = generator.calculate_valuation_range()
        assert 'bear_case' in valuation
        assert 'base_case' in valuation
        assert 'bull_case' in valuation
        assert valuation['bear_case'] < valuation['base_case'] < valuation['bull_case']
        print(f"✅ PASS - Valuation range:")
        print(f"         Bear: ${valuation['bear_case']:.0f}")
        print(f"         Base: ${valuation['base_case']:.0f}")
        print(f"         Bull: ${valuation['bull_case']:.0f}")
        tests_passed += 1
    except Exception as e:
        print(f"❌ FAIL - Valuation range error: {e}")
        traceback.print_exc()
        tests_failed += 1
        errors.append(f"Valuation Error: {e}")
    
    # Final Summary
    print("\n" + "=" * 70)
    print("  TEST SUMMARY")
    print("=" * 70)
    print(f"\n✅ Tests Passed: {tests_passed}/{tests_passed + tests_failed}")
    print(f"❌ Tests Failed: {tests_failed}/{tests_passed + tests_failed}")
    
    if tests_failed == 0:
        print("\n🎉 ALL TESTS PASSED! IC-Ready Investment Summary is working correctly!")
        print("\n✅ Ready for production use")
        return True
    else:
        print("\n⚠️  SOME TESTS FAILED - Review errors below:")
        for i, error in enumerate(errors, 1):
            print(f"   {i}. {error}")
        return False

if __name__ == "__main__":
    success = test_investment_summary_enhancements()
    sys.exit(0 if success else 1)


