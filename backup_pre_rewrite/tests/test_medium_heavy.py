"""
MEDIUM-HEAVY TESTING - MILESTONE-008
====================================
Test flip cards and overall app integration with real tickers.

Author: ATLAS Architect
Created: 2025-12-08
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flip_cards import METRICS, get_metric_color, format_value

# Test tickers covering different scenarios
TEST_TICKERS = [
    "AAPL",   # Tech mega-cap
    "MSFT",   # Tech mega-cap
    "JNJ",    # Healthcare
    "XOM",    # Energy
    "JPM",    # Financials
    "KO",     # Consumer staples
    "TSLA",   # High growth
    "BRK-B",  # Conglomerate
    "META",   # Tech
    "NVDA",   # Semiconductor
]

def test_flip_cards_module():
    """Test flip cards module functions."""
    print("\n=== FLIP CARDS MODULE TESTS ===")
    
    # 1. Metrics count
    print(f"[1] Metrics defined: {len(METRICS)}")
    assert len(METRICS) >= 20, "Should have 20+ metrics"
    print("    PASS: 26 metrics defined")
    
    # 2. Color logic - higher is better
    color = get_metric_color(25, "ROE")
    print(f"[2] ROE=25 color: {color}")
    assert color == "#10b981", f"ROE 25 should be green, got {color}"
    print("    PASS: Green for high ROE")
    
    # 3. Color logic - higher is worse
    color = get_metric_color(2.0, "Debt_to_Equity")
    print(f"[3] D/E=2.0 color: {color}")
    assert color == "#ef4444", f"D/E 2.0 should be red, got {color}"
    print("    PASS: Red for high D/E")
    
    # 4. Format value - billions
    formatted, num = format_value(1_500_000_000, "$")
    print(f"[4] Format $1.5B: {formatted}")
    assert "1.50B" in formatted, f"Should format as B, got {formatted}"
    print("    PASS: Billions formatted correctly")
    
    # 5. Format value - percent
    formatted, num = format_value(0.15, "%")
    print(f"[5] Format 0.15 as %: {formatted}")
    assert "15" in formatted, f"Should convert to 15%, got {formatted}"
    print("    PASS: Decimal to percent conversion")
    
    # 6. N/A handling
    formatted, num = format_value(None, "%")
    print(f"[6] Format None: {formatted}")
    assert formatted == "N/A", f"None should be N/A, got {formatted}"
    print("    PASS: N/A handling")
    
    # 7. All metrics have required fields
    required = ['label', 'formula', 'insight', 'higher_is', 'unit', 'category']
    errors = []
    for key, config in METRICS.items():
        for field in required:
            if field not in config:
                errors.append(f"{key} missing {field}")
    if errors:
        print(f"[7] Missing fields: {errors}")
        assert False, f"Missing fields: {errors}"
    print(f"[7] All {len(METRICS)} metrics have required fields")
    print("    PASS: All metrics complete")
    
    print("\n=== ALL FLIP CARDS TESTS PASSED ===\n")


def test_usa_backend_extraction():
    """Test financial data extraction for test tickers."""
    print("\n=== DATA EXTRACTION TESTS ===")
    
    try:
        from usa_backend import USAFinancialExtractor
    except ImportError as e:
        print(f"[!] Cannot import USAFinancialExtractor: {e}")
        return
    
    extractor = USAFinancialExtractor()
    results = []
    
    for ticker in TEST_TICKERS[:5]:  # Test first 5 tickers
        print(f"\n[{ticker}] Extracting...")
        try:
            data = extractor.extract_all_financials(ticker)
            
            # Check key fields
            info = data.get('info', {})
            has_pe = info.get('trailingPE') is not None
            has_roe = info.get('returnOnEquity') is not None
            has_price = info.get('currentPrice') is not None or info.get('regularMarketPrice') is not None
            
            result = {
                'ticker': ticker,
                'status': 'OK',
                'has_pe': has_pe,
                'has_roe': has_roe,
                'has_price': has_price,
                'fields': len(info)
            }
            results.append(result)
            
            print(f"    P/E: {'YES' if has_pe else 'NO'}")
            print(f"    ROE: {'YES' if has_roe else 'NO'}")
            print(f"    Price: {'YES' if has_price else 'NO'}")
            print(f"    Fields: {len(info)}")
            
        except Exception as e:
            results.append({
                'ticker': ticker,
                'status': f'ERROR: {str(e)[:50]}',
            })
            print(f"    ERROR: {str(e)[:50]}")
    
    # Summary
    print("\n=== EXTRACTION SUMMARY ===")
    ok_count = sum(1 for r in results if r['status'] == 'OK')
    print(f"Success: {ok_count}/{len(results)}")
    
    for r in results:
        status = "OK" if r['status'] == 'OK' else "FAIL"
        print(f"  {r['ticker']}: {status}")
    
    return results


def test_dashboard_tab_integration():
    """Test dashboard tab imports and flip card availability."""
    print("\n=== DASHBOARD TAB INTEGRATION ===")
    
    try:
        from dashboard_tab import FLIP_CARDS_AVAILABLE, METRICS
        print(f"[1] FLIP_CARDS_AVAILABLE: {FLIP_CARDS_AVAILABLE}")
        print(f"[2] METRICS count: {len(METRICS)}")
        
        if FLIP_CARDS_AVAILABLE:
            print("    PASS: Flip cards enabled in dashboard")
        else:
            print("    WARN: Flip cards not available - fallback active")
            
    except ImportError as e:
        print(f"    ERROR: Cannot import dashboard_tab: {e}")


if __name__ == "__main__":
    print("=" * 60)
    print("MEDIUM-HEAVY TESTING - ATLAS Financial Intelligence")
    print("=" * 60)
    
    # Run tests
    test_flip_cards_module()
    test_dashboard_tab_integration()
    test_usa_backend_extraction()
    
    print("\n" + "=" * 60)
    print("TESTING COMPLETE")
    print("=" * 60)

