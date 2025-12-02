"""
MASTER VALIDATION RUNNER
=========================
Runs all validation tests and generates comprehensive report.

Usage:
    python validation_master_runner.py AAPL FIVE MSFT
"""

import sys
import json
import time
from datetime import datetime
from typing import List, Dict

# Import all test modules
import validation_test_1_extraction as test1
import validation_test_2_ratios as test2
import validation_test_3_dcf as test3
import validation_test_4_quant as test4
import validation_test_5_fields as test5
import validation_test_6_growth as test6

def run_full_validation(tickers: List[str]) -> Dict:
    """
    Run complete validation suite on multiple tickers.
    
    Args:
        tickers: List of ticker symbols to test
    
    Returns:
        Comprehensive results dictionary
    """
    print("\n" + "="*80)
    print("  ATLAS FINANCIAL INTELLIGENCE - COMPREHENSIVE VALIDATION SUITE")
    print("="*80)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Tickers to test: {', '.join(tickers)}")
    print("="*80)
    
    all_results = {
        "timestamp": datetime.now().isoformat(),
        "tickers_tested": tickers,
        "test_results": {},
        "summary": {}
    }
    
    for ticker in tickers:
        print(f"\n\n{'#'*80}")
        print(f"# TESTING: {ticker}")
        print(f"{'#'*80}\n")
        
        ticker_results = {
            "ticker": ticker,
            "tests": {},
            "start_time": time.time()
        }
        
        # Test 1: Extraction Accuracy
        print(f"\n{'='*80}")
        print(f"Running Test 1/6: Extraction Accuracy")
        print(f"{'='*80}")
        try:
            result1 = test1.test_extraction_accuracy(ticker)
            ticker_results["tests"]["extraction"] = result1
        except Exception as e:
            print(f"[ERROR] Test 1 crashed: {e}")
            ticker_results["tests"]["extraction"] = {"status": "CRASHED", "error": str(e)}
        
        # Test 2: Ratio Accuracy
        print(f"\n{'='*80}")
        print(f"Running Test 2/6: Ratio Calculation")
        print(f"{'='*80}")
        try:
            result2 = test2.test_ratio_accuracy(ticker)
            ticker_results["tests"]["ratios"] = result2
        except Exception as e:
            print(f"[ERROR] Test 2 crashed: {e}")
            ticker_results["tests"]["ratios"] = {"status": "CRASHED", "error": str(e)}
        
        # Test 3: DCF Reasonableness
        print(f"\n{'='*80}")
        print(f"Running Test 3/6: DCF Reasonableness")
        print(f"{'='*80}")
        try:
            result3 = test3.test_dcf_reasonableness(ticker)
            ticker_results["tests"]["dcf"] = result3
        except Exception as e:
            print(f"[ERROR] Test 3 crashed: {e}")
            ticker_results["tests"]["dcf"] = {"status": "CRASHED", "error": str(e)}
        
        # Test 4: Quant Analysis
        print(f"\n{'='*80}")
        print(f"Running Test 4/6: Quant Analysis")
        print(f"{'='*80}")
        try:
            result4 = test4.test_quant_analysis(ticker)
            ticker_results["tests"]["quant"] = result4
        except Exception as e:
            print(f"[ERROR] Test 4 crashed: {e}")
            ticker_results["tests"]["quant"] = {"status": "CRASHED", "error": str(e)}
        
        # Test 5: Field Mapping
        print(f"\n{'='*80}")
        print(f"Running Test 5/6: Field Mapping")
        print(f"{'='*80}")
        try:
            result5 = test5.test_field_mapping(ticker)
            ticker_results["tests"]["fields"] = result5
        except Exception as e:
            print(f"[ERROR] Test 5 crashed: {e}")
            ticker_results["tests"]["fields"] = {"status": "CRASHED", "error": str(e)}
        
        # Test 6: Growth Calculations
        print(f"\n{'='*80}")
        print(f"Running Test 6/6: Growth Calculations")
        print(f"{'='*80}")
        try:
            result6 = test6.validate_growth_calculations(ticker)
            ticker_results["tests"]["growth"] = result6
        except Exception as e:
            print(f"[ERROR] Test 6 crashed: {e}")
            ticker_results["tests"]["growth"] = {"status": "CRASHED", "error": str(e)}
        
        ticker_results["end_time"] = time.time()
        ticker_results["duration"] = ticker_results["end_time"] - ticker_results["start_time"]
        
        all_results["test_results"][ticker] = ticker_results
    
    # Generate summary
    all_results["summary"] = generate_summary(all_results["test_results"])
    
    return all_results

def generate_summary(test_results: Dict) -> Dict:
    """Generate summary statistics"""
    summary = {
        "total_tickers": len(test_results),
        "total_tests": 0,
        "tests_passed": 0,
        "tests_failed": 0,
        "tests_crashed": 0,
        "by_test_type": {},
        "overall_pass_rate": 0,
        "overall_grade": "F"
    }
    
    test_types = ["extraction", "ratios", "dcf", "quant", "fields", "growth"]
    
    for test_type in test_types:
        summary["by_test_type"][test_type] = {
            "passed": 0,
            "failed": 0,
            "crashed": 0
        }
    
    for ticker, ticker_data in test_results.items():
        for test_type in test_types:
            test_result = ticker_data["tests"].get(test_type, {})
            status = test_result.get("status", "UNKNOWN")
            
            summary["total_tests"] += 1
            
            if status == "PASS":
                summary["tests_passed"] += 1
                summary["by_test_type"][test_type]["passed"] += 1
            elif status == "FAIL":
                summary["tests_failed"] += 1
                summary["by_test_type"][test_type]["failed"] += 1
            elif status == "CRASHED":
                summary["tests_crashed"] += 1
                summary["by_test_type"][test_type]["crashed"] += 1
    
    if summary["total_tests"] > 0:
        summary["overall_pass_rate"] = (summary["tests_passed"] / summary["total_tests"] * 100)
        
        if summary["overall_pass_rate"] >= 90:
            summary["overall_grade"] = "A"
        elif summary["overall_pass_rate"] >= 80:
            summary["overall_grade"] = "B"
        elif summary["overall_pass_rate"] >= 70:
            summary["overall_grade"] = "C"
        elif summary["overall_pass_rate"] >= 60:
            summary["overall_grade"] = "D"
        else:
            summary["overall_grade"] = "F"
    
    return summary

def print_final_report(results: Dict):
    """Print comprehensive final report"""
    print("\n\n" + "="*80)
    print("  FINAL VALIDATION REPORT")
    print("="*80)
    
    summary = results["summary"]
    
    print(f"\nOverall Statistics:")
    print(f"  Tickers Tested: {summary['total_tickers']}")
    print(f"  Total Tests:    {summary['total_tests']}")
    print(f"  Passed:         {summary['tests_passed']} ({summary['overall_pass_rate']:.1f}%)")
    print(f"  Failed:         {summary['tests_failed']}")
    print(f"  Crashed:        {summary['tests_crashed']}")
    print(f"  Overall Grade:  {summary['overall_grade']}")
    
    print(f"\nResults by Test Type:")
    print(f"{'Test Type':<20} {'Passed':<10} {'Failed':<10} {'Crashed':<10}")
    print("-" * 60)
    for test_type, stats in summary["by_test_type"].items():
        print(f"{test_type.capitalize():<20} {stats['passed']:<10} {stats['failed']:<10} {stats['crashed']:<10}")
    
    print(f"\nResults by Ticker:")
    print(f"{'Ticker':<10} {'Extraction':<12} {'Ratios':<12} {'DCF':<12} {'Quant':<12} {'Fields':<12}")
    print("-" * 80)
    for ticker, ticker_data in results["test_results"].items():
        tests = ticker_data["tests"]
        row = f"{ticker:<10}"
        for test_type in ["extraction", "ratios", "dcf", "quant", "fields"]:
            status = tests.get(test_type, {}).get("status", "SKIP")
            symbol = "OK" if status == "PASS" else "X" if status == "FAIL" else "!" if status == "CRASHED" else "-"
            row += f" {symbol:<11}"
        print(row)
    
    print("\n" + "="*80)
    
    if summary["overall_pass_rate"] >= 90:
        print("  [OK] VALIDATION PASSED - System is accurate and reliable")
    elif summary["overall_pass_rate"] >= 70:
        print("  [WARN] VALIDATION WARNING - Some issues detected, review recommended")
    else:
        print("  [FAIL] VALIDATION FAILED - Critical issues detected, fix required")
    
    print("="*80)

def save_report(results: Dict, filename: str = "validation_report.json"):
    """Save detailed report to JSON"""
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n[OK] Detailed report saved: {filename}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validation_master_runner.py TICKER1 TICKER2 ...")
        print("Example: python validation_master_runner.py AAPL FIVE MSFT")
        sys.exit(1)
    
    tickers = sys.argv[1:]
    
    # Run validation
    results = run_full_validation(tickers)
    
    # Print report
    print_final_report(results)
    
    # Save detailed report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    save_report(results, f"validation_report_{timestamp}.json")
    
    # Exit with appropriate code
    overall_pass_rate = results["summary"]["overall_pass_rate"]
    sys.exit(0 if overall_pass_rate >= 70 else 1)

