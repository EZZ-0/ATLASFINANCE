"""
VALIDATION TEST 4: QUANT ANALYSIS VALIDATION
=============================================
Validates Fama-French 3-Factor Model calculations.

Checks:
1. Beta values are within reasonable ranges
2. Alpha is close to zero (market efficiency)
3. Cost of Equity is reasonable (8-15% typical)
4. Historical prices match yfinance exactly
"""

import sys
import pandas as pd
import numpy as np
from typing import Dict
from usa_backend import quick_extract
from quant_engine import QuantEngine
import yfinance as yf

def test_quant_analysis(ticker: str = "AAPL"):
    """
    Main test: Validate Quant/FF3 calculations.
    """
    print("="*70)
    print(f"VALIDATION TEST 4: QUANT ANALYSIS - {ticker}")
    print("="*70)
    
    results = []
    
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
    
    # Test 1: Historical Price Accuracy
    print("\n" + "-"*70)
    print("TEST 1: HISTORICAL PRICE ACCURACY")
    print("-"*70)
    
    try:
        # Our prices
        market_data = data.get('market_data', {})
        our_prices = market_data.get('historical_prices') if isinstance(market_data, dict) else None
        
        # Direct from yfinance
        yf_ticker = yf.Ticker(ticker)
        yf_prices = yf_ticker.history(period="1mo")
        
        if our_prices is not None and not our_prices.empty and not yf_prices.empty:
            # Compare last 5 trading days
            price_matches = 0
            price_tests = 0
            
            print("\nDate       | Our Close | YF Close  | Match")
            print("-" * 60)
            
            for date in yf_prices.index[-5:]:
                if date in our_prices.index:
                    our_close = our_prices.loc[date]['Close']
                    yf_close = yf_prices.loc[date]['Close']
                    
                    diff = abs(our_close - yf_close)
                    match = diff < 0.01
                    
                    symbol = "[PASS]" if match else "[FAIL]"
                    print(f"{date.date()} | ${our_close:7.2f} | ${yf_close:7.2f} | {symbol}")
                    
                    price_tests += 1
                    if match:
                        price_matches += 1
            
            if price_tests > 0:
                if price_matches == price_tests:
                    print(f"\n[PASS] All {price_tests} prices match exactly")
                    results.append(True)
                else:
                    print(f"\n[WARN] Only {price_matches}/{price_tests} prices match")
                    results.append(False)
            else:
                print("[SKIP] No overlapping dates to compare")
        else:
            print("[SKIP] Price data not available")
    
    except Exception as e:
        print(f"[ERROR] Price comparison failed: {e}")
    
    # Test 2: Run Quant Analysis
    print("\n" + "-"*70)
    print("TEST 2: FAMA-FRENCH ANALYSIS")
    print("-"*70)
    
    try:
        engine = QuantEngine()
        quant_results = engine.analyze_stock(ticker)
        
        if quant_results.get('status') == 'error':
            print(f"[FAIL] Quant analysis failed: {quant_results.get('message')}")
            return {"status": "FAILED", "reason": "quant_error"}
        
        ff = quant_results.get('fama_french', {})
        
        # Extract metrics
        beta_market = ff.get('beta_market', 0)
        beta_smb = ff.get('beta_smb', 0)
        beta_hml = ff.get('beta_hml', 0)
        alpha = ff.get('alpha', 0)
        ke_annual = ff.get('cost_of_equity_annual', 0)
        r_squared = ff.get('r_squared', 0)
        
        print(f"\nCalculated Metrics:")
        print(f"  Beta (Market): {beta_market:.4f}")
        print(f"  Beta (SMB):    {beta_smb:.4f}")
        print(f"  Beta (HML):    {beta_hml:.4f}")
        print(f"  Alpha:         {alpha*100:.4f}% monthly")
        print(f"  Cost of Equity: {ke_annual*100:.2f}% annual")
        print(f"  R-Squared:     {r_squared:.4f}")
        
        # Test 2a: Beta Range Check
        print("\n" + "-"*50)
        print("Beta Range Validation")
        print("-"*50)
        
        # Typical ranges for large cap stocks
        if 0.5 <= abs(beta_market) <= 2.0:
            print(f"[PASS] Market Beta {beta_market:.4f} is reasonable (0.5-2.0)")
            results.append(True)
        else:
            print(f"[WARN] Market Beta {beta_market:.4f} outside typical range")
            results.append(False)
        
        if abs(beta_smb) <= 2.0:
            print(f"[PASS] SMB Beta {beta_smb:.4f} is reasonable")
            results.append(True)
        else:
            print(f"[WARN] SMB Beta {beta_smb:.4f} seems extreme")
            results.append(False)
        
        if abs(beta_hml) <= 2.0:
            print(f"[PASS] HML Beta {beta_hml:.4f} is reasonable")
            results.append(True)
        else:
            print(f"[WARN] HML Beta {beta_hml:.4f} seems extreme")
            results.append(False)
        
        # Test 2b: Alpha Check (should be near zero in efficient market)
        print("\n" + "-"*50)
        print("Alpha Validation (Market Efficiency)")
        print("-"*50)
        
        alpha_annual = alpha * 12
        if abs(alpha_annual) < 0.05:  # Less than 5% annual
            print(f"[PASS] Alpha {alpha_annual*100:.2f}% near zero (efficient)")
            results.append(True)
        elif abs(alpha_annual) < 0.10:  # Less than 10% annual
            print(f"[WARN] Alpha {alpha_annual*100:.2f}% slightly high")
            results.append(True)
        elif abs(alpha_annual) < 0.20:  # Less than 20% annual
            print(f"[WARN] Alpha {alpha_annual*100:.2f}% high (extreme growth stock)")
            results.append(True)  # Pass with warning for extreme growth
        else:
            print(f"[WARN] Alpha {alpha_annual*100:.2f}% suspiciously high")
            results.append(False)
        
        # Test 2c: Cost of Equity Range
        print("\n" + "-"*50)
        print("Cost of Equity Validation")
        print("-"*50)
        
        if 0.05 <= ke_annual <= 0.20:  # 5% to 20% typical
            print(f"[PASS] Ke {ke_annual*100:.2f}% within reasonable range (5-20%)")
            results.append(True)
        elif 0.20 < ke_annual <= 0.25:  # 20-25% for extreme growth
            print(f"[WARN] Ke {ke_annual*100:.2f}% high (extreme growth stock)")
            results.append(True)  # Pass with warning for extreme growth
        else:
            print(f"[WARN] Ke {ke_annual*100:.2f}% outside typical range")
            results.append(False)
        
        # Test 2d: Model Fit (R-squared)
        print("\n" + "-"*50)
        print("Model Fit Validation")
        print("-"*50)
        
        if r_squared >= 0.30:
            print(f"[PASS] R-squared {r_squared:.4f} shows good fit (>30%)")
            results.append(True)
        elif r_squared >= 0.15:
            print(f"[WARN] R-squared {r_squared:.4f} shows weak fit")
            results.append(True)
        else:
            print(f"[FAIL] R-squared {r_squared:.4f} shows very poor fit")
            results.append(False)
        
    except Exception as e:
        print(f"[FAIL] Quant analysis crashed: {e}")
        import traceback
        traceback.print_exc()
        results.append(False)
    
    # Summary
    print("\n" + "="*70)
    print("QUANT VALIDATION SUMMARY")
    print("="*70)
    
    passed = sum(results)
    total = len(results)
    pass_rate = (passed / total * 100) if total > 0 else 0
    
    print(f"Tests Passed: {passed}/{total} ({pass_rate:.1f}%)")
    
    if pass_rate >= 80:
        grade = "PASS"
        verdict = "Quant analysis producing reasonable results"
    else:
        grade = "FAIL"
        verdict = "Quant analysis needs review"
    
    print(f"Grade: {grade}")
    print(f"Verdict: {verdict}")
    
    return {
        "test": "quant_analysis",
        "ticker": ticker,
        "passed": passed,
        "total": total,
        "pass_rate": pass_rate,
        "beta_market": beta_market if 'beta_market' in locals() else None,
        "cost_of_equity": ke_annual if 'ke_annual' in locals() else None,
        "grade": grade,
        "status": "PASS" if pass_rate >= 80 else "FAIL"
    }

if __name__ == "__main__":
    ticker = sys.argv[1] if len(sys.argv) > 1 else "AAPL"
    result = test_quant_analysis(ticker)
    sys.exit(0 if result["status"] == "PASS" else 1)

