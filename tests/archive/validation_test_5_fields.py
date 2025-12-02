"""
VALIDATION TEST 5: FIELD MAPPING AUDIT
========================================
Validates that we're extracting the correct fields from financial statements.

Checks:
1. Field names are not suspicious (no "Unknown", "Unnamed", etc.)
2. All expected fields are present
3. No duplicate fields
4. Field values are reasonable (not all zeros)
"""

import sys
import pandas as pd
from typing import Dict, List, Set
from usa_backend import quick_extract

def test_field_mapping(ticker: str = "AAPL"):
    """
    Main test: Audit field name mapping.
    """
    print("="*70)
    print(f"VALIDATION TEST 5: FIELD MAPPING AUDIT - {ticker}")
    print("="*70)
    
    # Extract data
    # Read fiscal_year_offset from validation template (defaults to 1 for backward compatibility)
    from validation_test_1_extraction import load_ground_truth
    truth = load_ground_truth(ticker)
    fiscal_year_offset = truth.get("_FISCAL_YEAR_OFFSET", 1) if truth else 1
    fy_end = truth.get("_FISCAL_YEAR_END", "Unknown") if truth else "Unknown"
    print(f"\n[INFO] Validation target: FY ending {fy_end}, using offset={fiscal_year_offset}")
    print(f"\n[INFO] Extracting {ticker} data...")
    data = quick_extract(ticker, fiscal_year_offset=fiscal_year_offset)
    
    if data.get("error"):
        print(f"[FAIL] Extraction failed")
        return {"status": "FAILED", "reason": "extraction_error"}
    
    income = data.get('income_statement', pd.DataFrame())
    balance = data.get('balance_sheet', pd.DataFrame())
    cashflow = data.get('cash_flow', pd.DataFrame())
    
    results = []
    issues = []
    
    # Test 1: Check for suspicious field names
    print("\n" + "-"*70)
    print("TEST 1: SUSPICIOUS FIELD NAME CHECK")
    print("-"*70)
    
    suspicious_keywords = ['Unnamed', 'Unknown', 'Other', 'Misc', 'Level_', 'index']
    
    def check_suspicious(df: pd.DataFrame, statement_name: str):
        """Check DataFrame for suspicious field names"""
        if df.empty:
            print(f"\n[WARN] {statement_name}: Empty DataFrame")
            return []
        
        found_issues = []
        print(f"\n{statement_name} Fields: {len(df.index)}")
        
        for field in df.index:
            field_str = str(field)
            for keyword in suspicious_keywords:
                if keyword.lower() in field_str.lower():
                    found_issues.append(f"{statement_name}: '{field}' contains '{keyword}'")
                    print(f"  [WARN] Suspicious field: {field}")
        
        if not found_issues:
            print(f"  [PASS] No suspicious fields")
        
        return found_issues
    
    issues.extend(check_suspicious(income, "Income Statement"))
    issues.extend(check_suspicious(balance, "Balance Sheet"))
    issues.extend(check_suspicious(cashflow, "Cash Flow"))
    
    if not issues:
        print(f"\n[PASS] No suspicious field names found")
        results.append(True)
    else:
        print(f"\n[FAIL] Found {len(issues)} suspicious fields")
        results.append(False)
    
    # Test 2: Expected Fields Present
    print("\n" + "-"*70)
    print("TEST 2: EXPECTED FIELDS CHECK")
    print("-"*70)
    
    expected_income = [
        ['Total Revenue', 'Revenue', 'Net Sales'],
        ['Gross Profit', 'GrossProfit'],
        ['Operating Income', 'EBIT', 'Operating Revenue'],
        ['Net Income', 'Net Income Common Stockholders'],
    ]
    
    expected_balance = [
        ['Total Assets', 'TotalAssets'],
        ['Total Liabilities', 'TotalLiabilitiesNetMinorityInterest'],
        ['Total Equity', 'Stockholders Equity', 'Total Stockholders Equity'],
        ['Cash And Cash Equivalents', 'Cash'],
    ]
    
    expected_cashflow = [
        ['Operating Cash Flow', 'Total Cash From Operating Activities'],
        ['Capital Expenditure', 'Capital Expenditures'],
        ['Free Cash Flow', 'FreeCashFlow'],
    ]
    
    def check_expected_fields(df: pd.DataFrame, expected_list: List[List[str]], 
                             statement_name: str) -> int:
        """Check if expected fields are present"""
        if df.empty:
            print(f"\n[SKIP] {statement_name}: No data")
            return 0
        
        found_count = 0
        print(f"\n{statement_name}:")
        
        for field_options in expected_list:
            found = False
            for option in field_options:
                if option in df.index:
                    print(f"  [PASS] Found: {option}")
                    found = True
                    found_count += 1
                    break
            
            if not found:
                print(f"  [WARN] Missing: {' OR '.join(field_options)}")
        
        return found_count
    
    income_found = check_expected_fields(income, expected_income, "Income Statement")
    balance_found = check_expected_fields(balance, expected_balance, "Balance Sheet")
    cashflow_found = check_expected_fields(cashflow, expected_cashflow, "Cash Flow")
    
    total_expected = len(expected_income) + len(expected_balance) + len(expected_cashflow)
    total_found = income_found + balance_found + cashflow_found
    
    coverage = (total_found / total_expected * 100) if total_expected > 0 else 0
    
    print(f"\nField Coverage: {total_found}/{total_expected} ({coverage:.1f}%)")
    
    if coverage >= 80:
        print(f"[PASS] Good field coverage")
        results.append(True)
    elif coverage >= 60:
        print(f"[WARN] Acceptable field coverage")
        results.append(True)
    else:
        print(f"[FAIL] Poor field coverage")
        results.append(False)
    
    # Test 3: Check for duplicate fields
    print("\n" + "-"*70)
    print("TEST 3: DUPLICATE FIELD CHECK")
    print("-"*70)
    
    def check_duplicates(df: pd.DataFrame, statement_name: str) -> int:
        """Check for duplicate field names"""
        if df.empty:
            return 0
        
        duplicates = df.index[df.index.duplicated()].tolist()
        
        if duplicates:
            print(f"\n{statement_name}:")
            print(f"  [WARN] Found {len(duplicates)} duplicate fields:")
            for dup in duplicates[:5]:  # Show first 5
                print(f"    - {dup}")
            return len(duplicates)
        else:
            print(f"\n{statement_name}:")
            print(f"  [PASS] No duplicates")
            return 0
    
    dup_count = 0
    dup_count += check_duplicates(income, "Income Statement")
    dup_count += check_duplicates(balance, "Balance Sheet")
    dup_count += check_duplicates(cashflow, "Cash Flow")
    
    if dup_count == 0:
        print(f"\n[PASS] No duplicate fields")
        results.append(True)
    else:
        print(f"\n[FAIL] Found {dup_count} duplicate fields")
        results.append(False)
    
    # Test 4: Value sanity check (not all zeros)
    print("\n" + "-"*70)
    print("TEST 4: VALUE SANITY CHECK")
    print("-"*70)
    
    def check_values(df: pd.DataFrame, statement_name: str) -> bool:
        """Check if values are reasonable (not all zeros)"""
        if df.empty:
            print(f"\n{statement_name}: [SKIP] No data")
            return None
        
        # Count non-zero values
        non_zero_count = 0
        total_values = 0
        
        for col in df.columns:
            for idx in df.index:
                val = df.loc[idx, col]
                if pd.notna(val):
                    total_values += 1
                    if abs(float(val)) > 0.01:
                        non_zero_count += 1
        
        if total_values == 0:
            print(f"\n{statement_name}: [FAIL] No valid values")
            return False
        
        non_zero_pct = (non_zero_count / total_values * 100)
        
        print(f"\n{statement_name}:")
        print(f"  Non-zero values: {non_zero_count}/{total_values} ({non_zero_pct:.1f}%)")
        
        if non_zero_pct >= 50:
            print(f"  [PASS] Sufficient non-zero values")
            return True
        elif non_zero_pct >= 25:
            print(f"  [WARN] Low non-zero values")
            return True
        else:
            print(f"  [FAIL] Too many zeros")
            return False
    
    income_ok = check_values(income, "Income Statement")
    balance_ok = check_values(balance, "Balance Sheet")
    cashflow_ok = check_values(cashflow, "Cash Flow")
    
    value_checks = [c for c in [income_ok, balance_ok, cashflow_ok] if c is not None]
    if value_checks and all(value_checks):
        results.append(True)
    else:
        results.append(False)
    
    # Summary
    print("\n" + "="*70)
    print("FIELD MAPPING SUMMARY")
    print("="*70)
    
    passed = sum(results)
    total = len(results)
    pass_rate = (passed / total * 100) if total > 0 else 0
    
    print(f"Tests Passed: {passed}/{total} ({pass_rate:.1f}%)")
    print(f"Issues Found: {len(issues)}")
    
    if pass_rate >= 75:
        grade = "PASS"
    else:
        grade = "FAIL"
    
    print(f"Grade: {grade}")
    
    return {
        "test": "field_mapping",
        "ticker": ticker,
        "passed": passed,
        "total": total,
        "pass_rate": pass_rate,
        "issues": issues,
        "field_coverage": coverage,
        "grade": grade,
        "status": "PASS" if pass_rate >= 75 else "FAIL"
    }

if __name__ == "__main__":
    ticker = sys.argv[1] if len(sys.argv) > 1 else "AAPL"
    result = test_field_mapping(ticker)
    sys.exit(0 if result["status"] == "PASS" else 1)

