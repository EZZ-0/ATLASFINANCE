"""
Quick test script to verify extraction improvements
Tests N/A reduction across multiple tickers
"""

import sys
import time

# Test tickers - diverse set
TEST_TICKERS = ["AAPL", "MSFT", "JPM", "XOM", "TSLA"]

def test_extraction():
    print("=" * 60)
    print("EXTRACTION IMPROVEMENT TEST")
    print("=" * 60)
    
    from usa_backend import USAFinancialExtractor
    
    extractor = USAFinancialExtractor()
    
    # Key fields to check
    key_fields = [
        'current_price', 'market_cap', 'pe_ratio', 'price_to_book',
        'roe', 'roa', 'debt_to_equity', 'current_ratio',
        'gross_margin', 'operating_margin', 'profit_margin',
        'revenue_growth', 'dividend_yield', 'beta',
        'sector', 'industry', 'employees'
    ]
    
    results = {}
    
    for ticker in TEST_TICKERS:
        print(f"\n{'='*60}")
        print(f"Testing: {ticker}")
        print("="*60)
        
        t0 = time.time()
        try:
            # Extract with new defaults (10-K + 10-Q)
            financials = extractor.extract_financials(ticker, source="auto")
            extraction_time = time.time() - t0
            
            # Count filled vs N/A
            filled = 0
            na_fields = []
            sources_used = set()
            
            for field in key_fields:
                value = financials.get(field)
                source = financials.get('_sources', {}).get(field, 'unknown')
                
                if value is not None and value != 'N/A' and value != '' and value != 0:
                    filled += 1
                    sources_used.add(source)
                else:
                    na_fields.append(field)
            
            fill_rate = (filled / len(key_fields)) * 100
            
            results[ticker] = {
                'fill_rate': fill_rate,
                'filled': filled,
                'total': len(key_fields),
                'na_fields': na_fields,
                'sources': list(sources_used),
                'time': extraction_time
            }
            
            print(f"\n[RESULT] {ticker}:")
            print(f"   Fill Rate: {fill_rate:.1f}% ({filled}/{len(key_fields)})")
            print(f"   Sources Used: {', '.join(sources_used)}")
            print(f"   Extraction Time: {extraction_time:.2f}s")
            if na_fields:
                print(f"   N/A Fields: {', '.join(na_fields[:5])}{'...' if len(na_fields) > 5 else ''}")
            
            # Show validation result
            validation = financials.get('_validation', {})
            if validation:
                print(f"   Validation: {'PASS' if validation.get('valid') else 'WARNINGS'}")
                if validation.get('warnings'):
                    print(f"   Warnings: {len(validation['warnings'])}")
            
        except Exception as e:
            print(f"[ERROR] {ticker}: {str(e)}")
            results[ticker] = {'error': str(e)}
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    total_fill = 0
    successful = 0
    
    for ticker, data in results.items():
        if 'error' not in data:
            print(f"{ticker}: {data['fill_rate']:.1f}% filled ({data['time']:.1f}s)")
            total_fill += data['fill_rate']
            successful += 1
        else:
            print(f"{ticker}: ERROR - {data['error']}")
    
    if successful > 0:
        avg_fill = total_fill / successful
        print(f"\nAVERAGE FILL RATE: {avg_fill:.1f}%")
        print(f"TARGET: 80%+")
        print(f"STATUS: {'PASS' if avg_fill >= 80 else 'NEEDS IMPROVEMENT'}")
    
    return results

if __name__ == "__main__":
    test_extraction()

