"""
VALIDATION TEST 2: RATIO CALCULATION ACCURACY
==============================================
Validates that our ratio formulas are mathematically correct.

Compares our calculated ratios against manually calculated ground truth.
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
        print(f"[ERROR] Ground truth file not found")
        sys.exit(1)

def calculate_ratio_manually(data: Dict, ratio_name: str, fiscal_year_offset: int = 0) -> float:
    """
    Calculate ratios manually from raw financial data.
    This serves as the control group for our automated calculations.
    
    Args:
        data: Financial data dictionary
        ratio_name: Name of ratio to calculate
        fiscal_year_offset: Which fiscal year column to use (same as extraction)
    """
    income = data.get('income_statement', pd.DataFrame())
    balance = data.get('balance_sheet', pd.DataFrame())
    cashflow = data.get('cash_flow', pd.DataFrame())
    
    def safe_get(df, names, idx=0):
        """Safely get value from DataFrame"""
        if df is None or df.empty:
            return 0
        for name in names if isinstance(names, list) else [names]:
            if name in df.index:
                try:
                    val = df.loc[name].iloc[idx]
                    return float(val) if pd.notna(val) else 0
                except:
                    continue
        return 0
    
    # Manual calculations (use fiscal_year_offset to match engine's calculation)
    idx = fiscal_year_offset
    if ratio_name == "gross_margin":
        revenue = safe_get(income, ["Total Revenue", "Revenue"], idx=idx)
        gross_profit = safe_get(income, ["Gross Profit"], idx=idx)
        return (gross_profit / revenue) if revenue != 0 else 0
    
    elif ratio_name == "operating_margin":
        revenue = safe_get(income, ["Total Revenue", "Revenue"], idx=idx)
        operating_income = safe_get(income, ["Operating Income", "EBIT"], idx=idx)
        return (operating_income / revenue) if revenue != 0 else 0
    
    elif ratio_name == "net_margin":
        revenue = safe_get(income, ["Total Revenue", "Revenue"], idx=idx)
        net_income = safe_get(income, ["Net Income"], idx=idx)
        return (net_income / revenue) if revenue != 0 else 0
    
    elif ratio_name == "roe":
        net_income = safe_get(income, ["Net Income"], idx=idx)
        equity = safe_get(balance, ["Total Equity", "Stockholders Equity"], idx=idx)
        return (net_income / equity) if equity != 0 else 0
    
    elif ratio_name == "roa":
        net_income = safe_get(income, ["Net Income"], idx=idx)
        assets = safe_get(balance, ["Total Assets"], idx=idx)
        return (net_income / assets) if assets != 0 else 0
    
    elif ratio_name == "debt_to_equity":
        liabilities = safe_get(balance, [
            "Total Liabilities Net Minority Interest",
            "Total Liabilities",
            "TotalLiabilitiesNetMinorityInterest",
            "TotalLiabilities"
        ], idx=idx)
        equity = safe_get(balance, ["Total Equity", "Stockholders Equity"], idx=idx)
        return (liabilities / equity) if equity != 0 else 0
    
    elif ratio_name == "current_ratio":
        current_assets = safe_get(balance, ["Total Current Assets", "Current Assets"], idx=idx)
        current_liab = safe_get(balance, ["Total Current Liabilities", "Current Liabilities"], idx=idx)
        return (current_assets / current_liab) if current_liab != 0 else 0
    
    elif ratio_name == "free_cash_flow":
        ocf = safe_get(cashflow, ["Operating Cash Flow", "Total Cash From Operating Activities"], idx=idx)
        capex = safe_get(cashflow, ["Capital Expenditure", "Capital Expenditures"], idx=idx)
        return ocf + capex  # capex is usually negative
    
    return 0

def validate_ratio(name: str, our_value: float, manual_value: float, 
                  expected_value: float = None, tolerance: float = 0.001) -> Tuple[bool, str]:
    """
    Validate a ratio calculation.
    
    Checks:
    1. Our automated calculation vs manual calculation from same data
    2. Both against ground truth (if available)
    """
    # Check 1: Our calculation vs Manual calculation
    if manual_value == 0:
        if abs(our_value) < 0.0001:
            check1 = True
            check1_msg = "Both zero"
        else:
            check1 = False
            check1_msg = f"Manual=0, Ours={our_value:.4f}"
    else:
        diff = abs(our_value - manual_value) / abs(manual_value)
        if diff < tolerance:
            check1 = True
            check1_msg = f"Match (diff: {diff*100:.4f}%)"
        else:
            check1 = False
            check1_msg = f"MISMATCH (diff: {diff*100:.2f}%)"
    
    # Check 2: Against ground truth (if available)
    check2 = None
    check2_msg = "No ground truth"
    
    if expected_value is not None:
        if expected_value == 0:
            check2 = abs(manual_value) < 0.0001
            check2_msg = "Match truth" if check2 else "Truth mismatch"
        else:
            diff_truth = abs(manual_value - expected_value) / abs(expected_value)
            if diff_truth < tolerance * 10:  # More lenient for ground truth
                check2 = True
                check2_msg = f"Match truth (diff: {diff_truth*100:.4f}%)"
            else:
                check2 = False
                check2_msg = f"Truth mismatch (diff: {diff_truth*100:.2f}%)"
    
    # Verdict
    passed = check1 and (check2 is None or check2)
    
    if passed:
        print(f"[PASS] {name}")
        print(f"       Our Value:    {our_value:.4f}")
        print(f"       Manual Calc:  {manual_value:.4f}")
        if expected_value is not None:
            print(f"       Ground Truth: {expected_value:.4f}")
        print(f"       Status: {check1_msg} | {check2_msg}")
    else:
        print(f"[FAIL] {name}")
        print(f"       Our Value:    {our_value:.4f}")
        print(f"       Manual Calc:  {manual_value:.4f}")
        if expected_value is not None:
            print(f"       Ground Truth: {expected_value:.4f}")
        print(f"       Status: {check1_msg} | {check2_msg}")
    
    return passed, check1_msg

def test_ratio_accuracy(ticker: str = "AAPL"):
    """
    Main test: Validate ratio calculation formulas.
    """
    print("="*70)
    print(f"VALIDATION TEST 2: RATIO CALCULATION - {ticker}")
    print("="*70)
    
    # Load ground truth
    truth = load_ground_truth(ticker)
    
    # Extract data
    # Read fiscal_year_offset from validation template (defaults to 1 for backward compatibility)
    fiscal_year_offset = truth.get("_FISCAL_YEAR_OFFSET", 1)
    fy_end = truth.get("_FISCAL_YEAR_END", "Unknown")
    print(f"\n[INFO] Validation target: FY ending {fy_end}, using offset={fiscal_year_offset}")
    print(f"[INFO] Extracting {ticker} data...")
    data = quick_extract(ticker, fiscal_year_offset=fiscal_year_offset)
    
    if data.get("error"):
        print(f"[FAIL] Extraction failed")
        return {"status": "FAILED", "reason": "extraction_error"}
    
    # Get our calculated ratios
    our_ratios = data.get('ratios', pd.DataFrame())
    
    print(f"[OK] Data extracted. Testing ratio calculations...\n")
    
    # Test each ratio
    ratios_to_test = [
        ("Gross Margin", "Gross_Margin", "gross_margin"),
        ("Operating Margin", "Operating_Margin", "operating_margin"),
        ("Net Margin", "Net_Margin", "net_margin"),
        ("ROE", "ROE", "roe"),
        ("ROA", "ROA", "roa"),
        ("Debt to Equity", "Debt_to_Equity", "debt_to_equity"),
        ("Current Ratio", "Current_Ratio", "current_ratio"),
        ("Free Cash Flow", "Free_Cash_Flow", "free_cash_flow"),
    ]
    
    results = []
    
    for display_name, our_field, manual_field in ratios_to_test:
        print("-" * 70)
        
        # Get our value
        our_value = 0
        if not our_ratios.empty and our_field in our_ratios.index:
            try:
                our_value = float(our_ratios.loc[our_field].iloc[0])
            except:
                our_value = 0
        
        # Calculate manually (using same fiscal_year_offset as engine)
        manual_value = calculate_ratio_manually(data, manual_field, fiscal_year_offset)
        
        # Get ground truth
        expected = truth['calculated_ratios'].get(manual_field)
        
        # Validate
        passed, msg = validate_ratio(display_name, our_value, manual_value, expected)
        results.append(passed)
    
    # Summary
    print("\n" + "="*70)
    print("RATIO VALIDATION SUMMARY")
    print("="*70)
    
    passed = sum(results)
    total = len(results)
    pass_rate = (passed / total * 100) if total > 0 else 0
    
    print(f"Tests Passed: {passed}/{total} ({pass_rate:.1f}%)")
    
    if pass_rate == 100:
        grade = "A+ PERFECT"
    elif pass_rate >= 90:
        grade = "A EXCELLENT"
    elif pass_rate >= 80:
        grade = "B GOOD"
    else:
        grade = "F FAIL"
    
    print(f"Grade: {grade}")
    
    return {
        "test": "ratio_accuracy",
        "ticker": ticker,
        "passed": passed,
        "total": total,
        "pass_rate": pass_rate,
        "grade": grade,
        "status": "PASS" if pass_rate >= 90 else "FAIL"
    }

if __name__ == "__main__":
    ticker = sys.argv[1] if len(sys.argv) > 1 else "AAPL"
    result = test_ratio_accuracy(ticker)
    sys.exit(0 if result["status"] == "PASS" else 1)

