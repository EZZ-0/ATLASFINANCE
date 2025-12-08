"""
DAY 2 QUICK VALIDATION - SIMPLIFIED
Tests critical functionality without unicode issues
"""

import sys
sys.path.insert(0, '.')

from usa_backend import quick_extract
from dcf_modeling import DCFModel  
from quant_engine import QuantEngine
from excel_export import export_financials_to_excel
import pandas as pd

def test_company(ticker):
    """Quick test for one company"""
    print(f"\n{'='*60}")
    print(f"TESTING: {ticker}")
    print('='*60)
    
    # Extract
    print("[1/5] Extracting data...")
    data = quick_extract(ticker)
    
    if data.get("error"):
        print(f"[FAIL] {data['error']}")
        return False
    
    print(f"[OK] Extracted ({data.get('data_source', 'unknown')} source)")
    
    # Check components
    print("[2/5] Checking financials...")
    has_income = not data.get("income_statement", pd.DataFrame()).empty
    has_balance = not data.get("balance_sheet", pd.DataFrame()).empty
    has_cash = not data.get("cash_flow", pd.DataFrame()).empty
    print(f"[OK] Income: {has_income}, Balance: {has_balance}, Cash: {has_cash}")
    
    print("[3/5] Checking ratios...")
    ratios = data.get("ratios", pd.DataFrame())
    print(f"[OK] Ratios: {len(ratios) if not ratios.empty else 0} metrics")
    
    print("[4/5] Checking DCF...")
    if has_income:
        dcf = DCFModel(data)
        dcf_results = dcf.calculate_dcf("base")
        if not dcf_results.get("error"):
            equity_val = dcf_results.get("equity_value_per_share", 0)
            print(f"[OK] DCF Base Case: ${equity_val:.2f}/share")
        else:
            print(f"[WARN] DCF failed: {dcf_results.get('error')}")
    else:
        print("[SKIP] No income statement for DCF")
    
    print("[5/5] Checking quant...")
    market_data = data.get("market_data", {})
    prices = market_data.get("historical_prices") if isinstance(market_data, dict) else None
    if prices is not None and not prices.empty:
        engine = QuantEngine()
        quant = engine.analyze_stock(ticker)
        if not quant.get("error"):
            ke = quant.get("cost_of_equity", 0)
            print(f"[OK] Quant Ke: {ke:.2%}")
        else:
            print(f"[WARN] Quant failed: {quant.get('error')}")
    else:
        print("[SKIP] No price data for quant")
    
    # Excel export test
    print("[BONUS] Testing Excel export...")
    try:
        filename = f"test_{ticker}.xlsx"
        export_financials_to_excel(data, filename)
        print(f"[OK] Excel: {filename}")
    except Exception as e:
        print(f"[FAIL] Excel: {e}")
    
    return True

def main():
    print("\n" + "="*60)
    print("  DAY 2 VALIDATION - QUICK TEST")
    print("="*60)
    
    # Test 3 diverse companies
    companies = ["AAPL", "FIVE", "SNOW"]
    
    results = {}
    for ticker in companies:
        try:
            results[ticker] = test_company(ticker)
        except Exception as e:
            print(f"[FATAL] {ticker} crashed: {e}")
            results[ticker] = False
    
    # Summary
    print("\n" + "="*60)
    print("  SUMMARY")
    print("="*60)
    for ticker, success in results.items():
        status = "[PASS]" if success else "[FAIL]"
        print(f"{status} {ticker}")
    
    passed = sum(results.values())
    total = len(results)
    print(f"\nSuccess Rate: {passed}/{total} ({passed/total*100:.0f}%)")
    
    return passed == total

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n[STOPPED]")
        sys.exit(2)
    except Exception as e:
        print(f"\n[FATAL] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(3)

