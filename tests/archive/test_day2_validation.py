"""
DAY 2 VALIDATION SUITE
Tests both bug fixes + comprehensive end-to-end testing
"""

import sys
import time
import pandas as pd
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, '.')

from usa_backend import quick_extract
from dcf_modeling import DCFModel
from quant_engine import QuantEngine
from visualization import FinancialVisualizer
from excel_export import export_financials_to_excel
from format_helpers import format_dataframe_for_csv

def print_section(title):
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def test_bug_fix_1_quant_unicode():
    """Test that Quant Engine no longer has unicode emoji errors"""
    print_section("BUG FIX #1: QUANT UNICODE TEST")
    
    try:
        # Extract data for a company with long history
        print("[TEST] Extracting AAPL data for quant analysis...")
        financials = quick_extract("AAPL", include_quant=True)
        
        if financials.get("error"):
            print(f"[FAIL] Extraction failed: {financials['error']}")
            return False
        
        # Run Quant Analysis (this previously crashed with emoji unicode error)
        print("[TEST] Running Fama-French analysis (previously crashed on Windows)...")
        analyzer = QuantEngine()
        quant_results = analyzer.calculate_fama_french(
            ticker="AAPL",
            historical_prices=financials.get("historical_prices")
        )
        
        if quant_results.get("error"):
            print(f"[FAIL] Quant analysis failed: {quant_results['error']}")
            return False
        
        # Check for expected outputs
        if "cost_of_equity" in quant_results:
            print(f"[OK] Cost of Equity calculated: {quant_results['cost_of_equity']:.2%}")
        
        if "alpha" in quant_results:
            print(f"[OK] Alpha calculated: {quant_results['alpha']:.4f}")
        
        if "beta_market" in quant_results:
            print(f"[OK] Market Beta calculated: {quant_results['beta_market']:.4f}")
        
        print("[PASS] Bug Fix #1: Quant unicode error RESOLVED!")
        return True
        
    except UnicodeEncodeError as e:
        print(f"[FAIL] Unicode error still exists: {e}")
        return False
    except Exception as e:
        print(f"[FAIL] Unexpected error: {e}")
        return False

def test_bug_fix_2_excel_export():
    """Test that Excel export no longer has format errors"""
    print_section("BUG FIX #2: EXCEL EXPORT TEST")
    
    try:
        # Extract data
        print("[TEST] Extracting FIVE data for Excel export...")
        financials = quick_extract("FIVE")
        
        if financials.get("error"):
            print(f"[FAIL] Extraction failed: {financials['error']}")
            return False
        
        # Create Excel export (this previously crashed with format error)
        print("[TEST] Exporting to Excel (previously crashed with format error)...")
        output_file = f"test_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        export_financials_to_excel(financials, output_file)
        
        print(f"[OK] Excel file created: {output_file}")
        print("[PASS] Bug Fix #2: Excel export format error RESOLVED!")
        return True
        
    except Exception as e:
        print(f"[FAIL] Excel export failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_end_to_end_company(ticker, description):
    """Comprehensive test for a single company"""
    print_section(f"END-TO-END TEST: {ticker} ({description})")
    
    results = {
        "ticker": ticker,
        "extraction": False,
        "ratios": False,
        "cagr": False,
        "dcf": False,
        "quant": False,
        "visualization": False,
        "csv_export": False,
        "excel_export": False,
        "time": 0
    }
    
    start_time = time.time()
    
    try:
        # 1. Extraction
        print(f"[TEST] Extracting {ticker}...")
        financials = quick_extract(ticker)
        
        if financials.get("error"):
            print(f"[FAIL] Extraction failed: {financials['error']}")
            return results
        
        print(f"[OK] Extraction successful ({financials.get('data_source', 'unknown')} source)")
        results["extraction"] = True
        
        # 2. Check Ratios
        ratios = financials.get("ratios", pd.DataFrame())
        if not ratios.empty and len(ratios) > 0:
            print(f"[OK] Ratios calculated: {len(ratios)} metrics")
            results["ratios"] = True
        else:
            print("[WARN] No ratios calculated")
        
        # 3. Check CAGR
        cagr = financials.get("cagr", {})
        if cagr and len(cagr) > 0:
            print(f"[OK] CAGR calculated: {len(cagr)} metrics")
            results["cagr"] = True
        else:
            print("[WARN] No CAGR calculated")
        
        # 4. DCF Model
        print(f"[TEST] Running DCF model for {ticker}...")
        dcf_model = DCFModel()
        dcf_results = dcf_model.run_dcf(financials)
        
        if not dcf_results.get("error") and "base_case" in dcf_results:
            print(f"[OK] DCF completed - Base Case: ${dcf_results['base_case'].get('equity_value_per_share', 0):.2f}")
            results["dcf"] = True
        else:
            print(f"[WARN] DCF incomplete: {dcf_results.get('error', 'Unknown')}")
        
        # 5. Quant Analysis
        if financials.get("historical_prices") is not None:
            print(f"[TEST] Running Quant analysis for {ticker}...")
            analyzer = QuantEngine()
            quant_results = analyzer.calculate_fama_french(
                ticker=ticker,
                historical_prices=financials.get("historical_prices")
            )
            
            if not quant_results.get("error") and "cost_of_equity" in quant_results:
                print(f"[OK] Quant completed - Ke: {quant_results['cost_of_equity']:.2%}")
                results["quant"] = True
            else:
                print(f"[WARN] Quant incomplete: {quant_results.get('error', 'Unknown')}")
        
        # 6. Visualization
        print(f"[TEST] Testing visualizations for {ticker}...")
        visualizer = FinancialVisualizer()
        try:
            chart = visualizer.plot_revenue_trend(financials)
            if chart:
                print("[OK] Visualization successful")
                results["visualization"] = True
        except Exception as e:
            print(f"[WARN] Visualization failed: {e}")
        
        # 7. CSV Export
        print(f"[TEST] Testing CSV export for {ticker}...")
        try:
            income = financials.get("income_statement", pd.DataFrame())
            if not income.empty:
                csv_df = format_dataframe_for_csv(income)
                csv_file = f"test_csv_{ticker}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                csv_df.to_csv(csv_file, index=True)
                print(f"[OK] CSV export successful: {csv_file}")
                results["csv_export"] = True
        except Exception as e:
            print(f"[WARN] CSV export failed: {e}")
        
        # 8. Excel Export
        print(f"[TEST] Testing Excel export for {ticker}...")
        try:
            excel_file = f"test_excel_{ticker}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            export_financials_to_excel(financials, excel_file)
            print(f"[OK] Excel export successful: {excel_file}")
            results["excel_export"] = True
        except Exception as e:
            print(f"[WARN] Excel export failed: {e}")
        
        results["time"] = time.time() - start_time
        print(f"\n[SUMMARY] {ticker} completed in {results['time']:.2f}s")
        
    except Exception as e:
        print(f"[FAIL] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
    
    return results

def test_edge_cases():
    """Test edge cases and error handling"""
    print_section("EDGE CASE TESTING")
    
    edge_cases = [
        ("INVALID123", "Invalid ticker"),
        ("", "Empty string"),
        ("A" * 10, "Too long ticker"),
    ]
    
    passed = 0
    for ticker, description in edge_cases:
        print(f"\n[TEST] Testing {description}: '{ticker}'")
        try:
            financials = quick_extract(ticker)
            if financials.get("error"):
                print(f"[OK] Gracefully handled: {financials['error']}")
                passed += 1
            else:
                print(f"[WARN] Should have failed but didn't")
        except Exception as e:
            print(f"[FAIL] Crashed instead of graceful error: {e}")
    
    print(f"\n[SUMMARY] Edge cases: {passed}/{len(edge_cases)} handled gracefully")
    return passed == len(edge_cases)

def main():
    """Run full Day 2 validation suite"""
    print("\n" + "=" * 80)
    print("  DAY 2 VALIDATION SUITE")
    print("  Testing: Bug Fixes + End-to-End + Edge Cases")
    print("=" * 80)
    
    start_time = time.time()
    
    # Test the 2 bug fixes first
    bug1_pass = test_bug_fix_1_quant_unicode()
    bug2_pass = test_bug_fix_2_excel_export()
    
    # End-to-end testing on 5 diverse companies
    test_companies = [
        ("AAPL", "Large cap tech, 40+ years"),
        ("FIVE", "Mid cap retail, ~13 years"),
        ("PLTR", "Recent IPO, 4 years"),
        ("JPM", "Financial, different structure"),
        ("SNOW", "Very recent IPO, 3 years"),
    ]
    
    e2e_results = []
    for ticker, description in test_companies:
        result = test_end_to_end_company(ticker, description)
        e2e_results.append(result)
        time.sleep(2)  # Brief pause between tests
    
    # Edge case testing
    edge_pass = test_edge_cases()
    
    # Final Summary
    print_section("FINAL VALIDATION SUMMARY")
    
    total_time = time.time() - start_time
    
    print("\n🔧 BUG FIXES:")
    print(f"  Bug #1 (Quant Unicode): {'✅ PASS' if bug1_pass else '❌ FAIL'}")
    print(f"  Bug #2 (Excel Export): {'✅ PASS' if bug2_pass else '❌ FAIL'}")
    
    print("\n📊 END-TO-END TESTING:")
    for result in e2e_results:
        ticker = result["ticker"]
        success_count = sum([
            result["extraction"],
            result["ratios"],
            result["cagr"],
            result["dcf"],
            result["quant"],
            result["visualization"],
            result["csv_export"],
            result["excel_export"]
        ])
        print(f"  {ticker}: {success_count}/8 tests passed ({result['time']:.1f}s)")
    
    print(f"\n🔍 EDGE CASES: {'✅ PASS' if edge_pass else '❌ FAIL'}")
    
    print(f"\n⏱️  TOTAL TIME: {total_time:.2f}s")
    
    # Calculate overall success rate
    total_tests = 2 + (len(e2e_results) * 8) + 1
    passed_tests = (
        int(bug1_pass) + int(bug2_pass) + int(edge_pass) +
        sum(sum([r["extraction"], r["ratios"], r["cagr"], r["dcf"], 
                 r["quant"], r["visualization"], r["csv_export"], r["excel_export"]]) 
            for r in e2e_results)
    )
    
    success_rate = (passed_tests / total_tests) * 100
    
    print("\n" + "=" * 80)
    print(f"  SUCCESS RATE: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}%)")
    print("=" * 80)
    
    if success_rate >= 90:
        print("\n🎉 VALIDATION PASSED! Ready for next phase.")
        return True
    elif success_rate >= 70:
        print("\n⚠️  VALIDATION PARTIAL. Some issues need attention.")
        return False
    else:
        print("\n❌ VALIDATION FAILED. Critical issues detected.")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n[INTERRUPTED] Testing stopped by user")
        sys.exit(2)
    except Exception as e:
        print(f"\n\n[FATAL ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(3)

