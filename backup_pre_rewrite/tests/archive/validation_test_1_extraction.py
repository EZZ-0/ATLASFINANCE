"""
VALIDATION TEST 1: RAW DATA EXTRACTION ACCURACY
================================================
Validates that we extract the EXACT numbers from financial statements.

Compares our extraction against manually verified ground truth data.
"""

import json
import pandas as pd
import sys
from typing import Dict, Tuple
from usa_backend import quick_extract

def load_ground_truth(ticker: str) -> Dict:
    """Load manually verified ground truth data"""
    try:
        with open(f'validation_truth_{ticker}.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"[ERROR] Ground truth file not found: validation_truth_{ticker}.json")
        print("Please create this file with manually verified data from SEC filings")
        sys.exit(1)

def validate_metric(name: str, extracted: float, expected: float, 
                   tolerance: float = 0.01) -> Tuple[bool, float]:
    """
    Validate a single metric against expected value.
    
    Args:
        name: Metric name
        extracted: Value extracted by our system
        expected: Ground truth value
        tolerance: Acceptable error percentage (default 1%)
    
    Returns:
        (is_valid, difference_percentage)
    """
    if expected is None:
        print(f"[SKIP] {name}: No ground truth available")
        return None, 0.0
    
    if expected == 0:
        # For zero values, check absolute match
        if abs(extracted) < 0.01:
            print(f"[PASS] {name}: Both zero")
            return True, 0.0
        else:
            print(f"[FAIL] {name}: Expected 0, got ${extracted:,.0f}")
            return False, float('inf')
    
    diff_pct = abs(extracted - expected) / abs(expected)
    
    if diff_pct > tolerance:
        print(f"[FAIL] {name}")
        print(f"       Expected:  ${expected:,.0f}")
        print(f"       Extracted: ${extracted:,.0f}")
        print(f"       Diff:      {diff_pct*100:.4f}%")
        return False, diff_pct
    else:
        print(f"[PASS] {name} (diff: {diff_pct*100:.4f}%)")
        return True, diff_pct

def find_value_in_dataframe(df: pd.DataFrame, possible_names: list, year_idx: int = 0) -> float:
    """
    Find a value in DataFrame by trying multiple possible field names.
    
    Args:
        df: Financial statement DataFrame
        possible_names: List of possible field name variations
        year_idx: Which year/column to extract (0 = most recent)
    
    Returns:
        Extracted value or 0 if not found
    """
    if df is None or df.empty:
        return 0.0
    
    for name in possible_names:
        if name in df.index:
            try:
                value = df.loc[name].iloc[year_idx]
                if pd.notna(value):
                    return float(value)
            except:
                continue
    
    return 0.0

def test_extraction_accuracy(ticker: str = "AAPL"):
    """
    Main test: Compare extracted data against ground truth.
    """
    print("="*70)
    print(f"VALIDATION TEST 1: EXTRACTION ACCURACY - {ticker}")
    print("="*70)
    
    # Load ground truth
    truth = load_ground_truth(ticker)
    
    # Extract using our engine
    # Read fiscal_year_offset from validation template (defaults to 1 for backward compatibility)
    fiscal_year_offset = truth.get("_FISCAL_YEAR_OFFSET", 1)
    fy_end = truth.get("_FISCAL_YEAR_END", "Unknown")
    print(f"\n[INFO] Validation target: FY ending {fy_end}, using offset={fiscal_year_offset}")
    print(f"[INFO] Extracting {ticker} data using our engine...")
    data = quick_extract(ticker, fiscal_year_offset=fiscal_year_offset)
    
    if data.get("error"):
        print(f"[FAIL] Extraction failed: {data['error']}")
        return {"status": "FAILED", "reason": "extraction_error"}
    
    print(f"[OK] Extraction complete. Source: {data.get('data_source', 'unknown')}")
    
    # Extract statements
    income = data.get('income_statement', pd.DataFrame())
    balance = data.get('balance_sheet', pd.DataFrame())
    cashflow = data.get('cash_flow', pd.DataFrame())
    
    results = []
    max_diff = 0.0
    
    # Validate Income Statement
    print("\n" + "-"*70)
    print("INCOME STATEMENT VALIDATION")
    print("-"*70)
    
    income_tests = [
        ("Total Revenue", ["Total Revenue", "Revenue", "Net Sales"], 
         truth['income_statement']['total_revenue']),
        ("Gross Profit", ["Gross Profit", "GrossProfit"], 
         truth['income_statement']['gross_profit']),
        ("Operating Income", ["Operating Income", "Operating Revenue", "EBIT"], 
         truth['income_statement']['operating_income']),
        ("Net Income", ["Net Income", "Net Income Common Stockholders"], 
         truth['income_statement']['net_income']),
    ]
    
    for name, possible_fields, expected in income_tests:
        # Use fiscal_year_offset to select the correct column from the DataFrame
        # (offset=0 reads most recent, offset=1 reads previous year, etc.)
        extracted = find_value_in_dataframe(income, possible_fields, year_idx=fiscal_year_offset)
        result, diff = validate_metric(name, extracted, expected)
        if result is not None:
            results.append(result)
            if diff > max_diff:
                max_diff = diff
    
    # Validate Balance Sheet
    print("\n" + "-"*70)
    print("BALANCE SHEET VALIDATION")
    print("-"*70)
    
    balance_tests = [
        ("Total Assets", ["Total Assets", "TotalAssets"], 
         truth['balance_sheet']['total_assets']),
        ("Total Liabilities", [
            "Total Liabilities Net Minority Interest",
            "Total Liabilities",
            "TotalLiabilitiesNetMinorityInterest",
            "TotalLiabilities"
        ], truth['balance_sheet']['total_liabilities']),
        ("Total Equity", ["Total Equity", "Stockholders Equity", "Total Stockholders Equity"], 
         truth['balance_sheet']['total_equity']),
        ("Cash and Equivalents", ["Cash And Cash Equivalents", "Cash"], 
         truth['balance_sheet']['cash_and_equivalents']),
    ]
    
    for name, possible_fields, expected in balance_tests:
        # Use fiscal_year_offset to select the correct column from the DataFrame
        # (offset=0 reads most recent, offset=1 reads previous year, etc.)
        extracted = find_value_in_dataframe(balance, possible_fields, year_idx=fiscal_year_offset)
        result, diff = validate_metric(name, extracted, expected)
        if result is not None:
            results.append(result)
            if diff > max_diff:
                max_diff = diff
    
    # Validate Cash Flow
    print("\n" + "-"*70)
    print("CASH FLOW VALIDATION")
    print("-"*70)
    
    cashflow_tests = [
        ("Operating Cash Flow", ["Operating Cash Flow", "Total Cash From Operating Activities"], 
         truth['cash_flow'].get('operating_cash_flow')),
        ("Capital Expenditures", ["Capital Expenditure", "Capital Expenditures", "CapEx"], 
         truth['cash_flow'].get('capital_expenditures')),
        ("Free Cash Flow", ["Free Cash Flow", "FreeCashFlow"], 
         truth['cash_flow'].get('free_cash_flow_manual', truth['cash_flow'].get('free_cash_flow'))),
    ]
    
    for name, possible_fields, expected in cashflow_tests:
        # Use fiscal_year_offset to select the correct column from the DataFrame
        # (offset=0 reads most recent, offset=1 reads previous year, etc.)
        extracted = find_value_in_dataframe(cashflow, possible_fields, year_idx=fiscal_year_offset)
        result, diff = validate_metric(name, extracted, expected)
        if result is not None:
            results.append(result)
            if diff > max_diff:
                max_diff = diff
    
    # Summary
    print("\n" + "="*70)
    print("EXTRACTION VALIDATION SUMMARY")
    print("="*70)
    
    passed = sum(results)
    total = len(results)
    pass_rate = (passed / total * 100) if total > 0 else 0
    
    print(f"Tests Passed: {passed}/{total} ({pass_rate:.1f}%)")
    print(f"Max Difference: {max_diff*100:.4f}%")
    
    if pass_rate == 100:
        grade = "A+ PERFECT"
    elif pass_rate >= 90:
        grade = "A EXCELLENT"
    elif pass_rate >= 80:
        grade = "B GOOD"
    elif pass_rate >= 70:
        grade = "C ACCEPTABLE"
    else:
        grade = "F FAIL"
    
    print(f"Grade: {grade}")
    
    return {
        "test": "extraction_accuracy",
        "ticker": ticker,
        "passed": passed,
        "total": total,
        "pass_rate": pass_rate,
        "max_diff": max_diff,
        "grade": grade,
        "status": "PASS" if pass_rate >= 90 else "FAIL"
    }

if __name__ == "__main__":
    ticker = sys.argv[1] if len(sys.argv) > 1 else "AAPL"
    result = test_extraction_accuracy(ticker)
    sys.exit(0 if result["status"] == "PASS" else 1)

