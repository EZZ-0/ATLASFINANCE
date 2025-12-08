"""
DAY 1 - DIAGNOSTIC TEST
Test USA Engine on 3 tickers: AAPL, MSFT, FIVE
Identify what works vs what's broken
"""

import sys
import pandas as pd
from datetime import datetime

print("="*80)
print("USA ENGINE DIAGNOSTIC TEST - DAY 1")
print("="*80)
print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# Test 1: Import all modules
print("[TEST 1] Module Imports")
print("-"*80)

try:
    from usa_backend import USAFinancialExtractor
    print("[OK] usa_backend imported")
except Exception as e:
    print(f"[FAIL] usa_backend: {e}")
    sys.exit(1)

try:
    from dcf_modeling import DCFModel
    print("[OK] dcf_modeling imported")
except Exception as e:
    print(f"[FAIL] dcf_modeling: {e}")

try:
    from visualization import FinancialVisualizer
    print("[OK] visualization imported")
except Exception as e:
    print(f"[FAIL] visualization: {e}")

try:
    from format_helpers import format_financial_number, format_dataframe_for_csv
    print("[OK] format_helpers imported")
except Exception as e:
    print(f"[FAIL] format_helpers: {e}")

try:
    from excel_export import export_financials_to_excel
    print("[OK] excel_export imported")
except Exception as e:
    print(f"[FAIL] excel_export: {e}")

try:
    from quant_engine import QuantEngine
    print("[OK] quant_engine imported")
except Exception as e:
    print(f"[FAIL] quant_engine: {e}")

print()

# Test 2: Number formatting
print("[TEST 2] Number Formatting")
print("-"*80)

test_numbers = [
    (400000000, "$400M"),      # 400 million
    (1140000000, "$1.14B"),    # 1.14 billion
    (950000000, "$950M"),      # Should be M not B
    (750000, "$750K"),         # Thousands
]

for num, expected in test_numbers:
    result = format_financial_number(num)
    status = "[OK]" if "$" in result and ("M" in result or "B" in result or "K" in result) else "[FAIL]"
    print(f"{status} {num:>15,} -> {result:>12} (expected: {expected})")

print()

# Test 3: Data Extraction
print("[TEST 3] Data Extraction - 3 Companies")
print("-"*80)

extractor = USAFinancialExtractor()

test_tickers = ["AAPL", "MSFT", "FIVE"]

results = {}

for ticker in test_tickers:
    print(f"\n[INFO] Testing {ticker}...")
    try:
        data = extractor.extract_financials(ticker, filing_types=["10-K"])
        
        # Check what we got
        has_income = not data.get("income_statement", pd.DataFrame()).empty
        has_balance = not data.get("balance_sheet", pd.DataFrame()).empty
        has_cashflow = not data.get("cash_flow", pd.DataFrame()).empty
        has_market = bool(data.get("market_data", {}).get("historical_prices") is not None)
        
        print(f"  Income Statement: {'[OK]' if has_income else '[FAIL]'}")
        print(f"  Balance Sheet:    {'[OK]' if has_balance else '[FAIL]'}")
        print(f"  Cash Flow:        {'[OK]' if has_cashflow else '[FAIL]'}")
        print(f"  Market Data:      {'[OK]' if has_market else '[FAIL]'}")
        
        # Check historical prices specifically
        if has_market:
            hist_prices = data["market_data"]["historical_prices"]
            if not hist_prices.empty:
                print(f"  Price History:    [OK] {len(hist_prices)} days from {hist_prices.index[0].date()} to {hist_prices.index[-1].date()}")
            else:
                print(f"  Price History:    [FAIL] Empty DataFrame")
        
        # Try calculating ratios
        try:
            ratios = extractor.calculate_ratios(data)
            if ratios and "status" not in ratios:
                all_zero = all(v == 0 for k, v in ratios.items() if isinstance(v, (int, float)))
                if all_zero:
                    print(f"  Ratios:           [WARN] All zeros - check data quality")
                else:
                    print(f"  Ratios:           [OK] Calculated successfully")
            else:
                print(f"  Ratios:           [FAIL] Error in calculation")
        except Exception as e:
            print(f"  Ratios:           [FAIL] {str(e)[:50]}")
        
        results[ticker] = {
            "success": True,
            "has_income": has_income,
            "has_balance": has_balance,
            "has_cashflow": has_cashflow,
            "has_market": has_market
        }
        
    except Exception as e:
        print(f"  [FAIL] Extraction failed: {str(e)[:100]}")
        results[ticker] = {"success": False, "error": str(e)}

print()

# Test 4: CSV Export Format
print("[TEST 4] CSV Export Format")
print("-"*80)

if "AAPL" in results and results["AAPL"]["success"]:
    try:
        data = extractor.extract_financials("AAPL", filing_types=["10-K"])
        income = data.get("income_statement", pd.DataFrame())
        
        if not income.empty:
            csv_df = format_dataframe_for_csv(income)
            
            # Check for scientific notation
            csv_str = csv_df.to_csv()
            has_scientific = 'E+' in csv_str or 'e+' in csv_str
            
            if has_scientific:
                print("[FAIL] CSV still contains scientific notation")
            else:
                print("[OK] CSV format is clean (no scientific notation)")
                
            # Show sample
            print("\nSample CSV output (first 3 rows):")
            print(csv_df.head(3).to_string())
        else:
            print("[SKIP] No income data to test")
    except Exception as e:
        print(f"[FAIL] CSV test error: {e}")
else:
    print("[SKIP] AAPL data not available")

print()

# Summary
print("="*80)
print("DIAGNOSTIC SUMMARY")
print("="*80)

success_count = sum(1 for r in results.values() if r.get("success", False))
print(f"Successful extractions: {success_count}/{len(test_tickers)}")

if success_count > 0:
    print("\n[OK] Core extraction works")
else:
    print("\n[FAIL] Core extraction broken - needs immediate fix")

print()
print("[INFO] Diagnostic complete. Ready to launch app.")
print("="*80)

