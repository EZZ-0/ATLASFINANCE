"""
QUICK TEST SCRIPT FOR USA EARNINGS ENGINE
==========================================
Run this to verify all modules are working correctly.
"""

import sys
from usa_backend import USAFinancialExtractor
from dcf_modeling import DCFModel
from visualization import FinancialVisualizer

def test_extraction():
    """Test data extraction from SEC/yfinance"""
    print("\n" + "="*60)
    print("TEST 1: DATA EXTRACTION")
    print("="*60)
    
    try:
        extractor = USAFinancialExtractor()
        print("[OK] Extractor initialized")
        
        # Test ticker validation
        is_valid, name = extractor.validate_ticker("AAPL")
        if is_valid:
            print(f"[OK] Ticker validation: AAPL -> {name}")
        else:
            print(f"[FAIL] Ticker validation failed: {name}")
            return False
        
        # Test extraction
        print("\n[INFO] Extracting Apple (AAPL) financials...")
        data = extractor.extract_financials("AAPL", source="auto")
        
        if "status" in data and data["status"] == "error":
            print(f"[FAIL] Extraction failed: {data['message']}")
            return False
        
        print(f"[OK] Extraction successful in {data.get('extraction_time', 'N/A')}")
        print(f"   Company: {data.get('company_name', 'N/A')}")
        print(f"   Ticker: {data.get('ticker', 'N/A')}")
        
        # Check statements
        income = data.get("income_statement")
        if income is not None and not income.empty:
            print(f"[OK] Income Statement: {len(income)} years")
            # Convert columns to strings (they might be Timestamps from yfinance)
            cols_str = [str(col) for col in income.columns[:5]]
            print(f"   Columns: {', '.join(cols_str)}...")
        else:
            print("[WARN] No income statement data")
        
        balance = data.get("balance_sheet")
        if balance is not None and not balance.empty:
            print(f"[OK] Balance Sheet: {len(balance)} years")
        else:
            print("[WARN] No balance sheet data")
        
        cashflow = data.get("cash_flow")
        if cashflow is not None and not cashflow.empty:
            print(f"[OK] Cash Flow: {len(cashflow)} years")
        else:
            print("[WARN] No cash flow data")
        
        return data
        
    except Exception as e:
        print(f"[FAIL] TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_dcf(financials):
    """Test DCF modeling"""
    print("\n" + "="*60)
    print("TEST 2: DCF MODELING")
    print("="*60)
    
    try:
        print("[INFO] Building DCF model...")
        model = DCFModel(financials)
        print("[OK] DCF Model initialized")
        
        print(f"   Base Revenue: ${model.base_revenue/1e9:.2f}B")
        print(f"   Operating Margin: {model.operating_margin:.1%}")
        print(f"   Historical Growth: {model.historical_growth:.1%}")
        
        print("\n[INFO] Running 3-scenario analysis...")
        results = model.run_all_scenarios()
        
        print(f"\n[OK] DCF Complete!")
        print(f"   Conservative: ${results['conservative']['value_per_share']:.2f}")
        print(f"   Base Case:    ${results['base']['value_per_share']:.2f}")
        print(f"   Aggressive:   ${results['aggressive']['value_per_share']:.2f}")
        print(f"   Weighted Avg: ${results['weighted_average']:.2f}")
        
        return results
        
    except Exception as e:
        print(f"[FAIL] TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_visualization(financials, dcf_results):
    """Test chart generation"""
    print("\n" + "="*60)
    print("TEST 3: VISUALIZATION")
    print("="*60)
    
    try:
        viz = FinancialVisualizer()
        print("[OK] Visualizer initialized")
        
        # Test revenue chart
        print("[INFO] Generating revenue trend chart...")
        fig = viz.plot_revenue_trend(financials)
        if fig:
            print("[OK] Revenue chart created")
        else:
            print("[WARN] Revenue chart failed")
        
        # Test DCF chart
        print("[INFO] Generating DCF comparison chart...")
        fig = viz.plot_dcf_comparison(dcf_results)
        if fig:
            print("[OK] DCF chart created")
        else:
            print("[WARN] DCF chart failed")
        
        print("\n[OK] Visualization tests passed")
        return True
        
    except Exception as e:
        print(f"[FAIL] TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ratios(extractor, financials):
    """Test ratio calculations"""
    print("\n" + "="*60)
    print("TEST 4: FINANCIAL RATIOS")
    print("="*60)
    
    try:
        print("[INFO] Calculating ratios...")
        ratios = extractor.calculate_ratios(financials)
        
        if "status" in ratios and ratios["status"] == "error":
            print(f"[WARN] Ratio calculation failed: {ratios['message']}")
            return False
        
        print("[OK] Ratios calculated:")
        for key, value in ratios.items():
            if isinstance(value, (int, float)):
                if "Margin" in key or "RO" in key:
                    print(f"   {key}: {value:.1f}%")
                elif "Debt" in key or "Ratio" in key:
                    print(f"   {key}: {value:.2f}x")
                else:
                    print(f"   {key}: ${value/1e9:.2f}B" if abs(value) > 1e9 else f"${value/1e6:.0f}M")
        
        # Test growth rates
        print("\n[INFO] Calculating growth rates...")
        growth = extractor.calculate_growth_rates(financials)
        
        if "status" not in growth:
            print("[OK] Growth rates calculated:")
            for key, value in growth.items():
                print(f"   {key}: {value:.1f}%")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("\n")
    print("*" * 60)
    print("  USA EARNINGS ENGINE - SYSTEM TEST")
    print("*" * 60)
    
    # Test 1: Extraction
    financials = test_extraction()
    if not financials:
        print("\n[FAIL] EXTRACTION FAILED - Cannot continue tests")
        sys.exit(1)
    
    # Test 2: DCF
    dcf_results = test_dcf(financials)
    if not dcf_results:
        print("\n[WARN] DCF FAILED - Continuing with remaining tests")
    
    # Test 3: Ratios
    extractor = USAFinancialExtractor()
    ratios_ok = test_ratios(extractor, financials)
    
    # Test 4: Visualization
    if dcf_results:
        viz_ok = test_visualization(financials, dcf_results)
    else:
        print("\n[WARN] SKIPPING VISUALIZATION TEST (no DCF results)")
        viz_ok = False
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"[OK] Data Extraction:  PASS")
    print(f"{'[OK]' if dcf_results else '[FAIL]'} DCF Modeling:      {'PASS' if dcf_results else 'FAIL'}")
    print(f"{'[OK]' if ratios_ok else '[FAIL]'} Ratio Calculation: {'PASS' if ratios_ok else 'FAIL'}")
    print(f"{'[OK]' if viz_ok else '[FAIL]'} Visualization:     {'PASS' if viz_ok else 'FAIL/SKIP'}")
    print("="*60)
    
    if financials and dcf_results:
        print("\n[SUCCESS] ALL CRITICAL TESTS PASSED!")
        print("\nNext steps:")
        print("  1. Run the Streamlit app: streamlit run usa_app.py")
        print("  2. Try different tickers: MSFT, GOOGL, TSLA, etc.")
        print("  3. Explore all 5 tabs: Extract, Model, Visualize, Compare, Quant")
    else:
        print("\n[WARN] SOME TESTS FAILED - Check error messages above")
        sys.exit(1)

if __name__ == "__main__":
    main()
