"""
WORKING COMPREHENSIVE TEST - FIXED VERSION
===========================================
Tests all companies with visible output and progress tracking.
"""

import sys
import time
from datetime import datetime
from test_config import TEST_COMPANIES

# Import backend
from usa_backend import USAFinancialExtractor

def test_all_companies():
    """Test data extraction for all 17 companies"""
    
    print("="*80, flush=True)
    print("COMPREHENSIVE ENGINE TEST - ALL 17 COMPANIES", flush=True)
    print("="*80, flush=True)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", flush=True)
    print(f"Companies to test: {len(TEST_COMPANIES)}", flush=True)
    print(flush=True)
    
    extractor = USAFinancialExtractor()
    results = []
    
    for i, ticker in enumerate(TEST_COMPANIES, 1):
        print(f"\n[{i}/{len(TEST_COMPANIES)}] Testing {ticker}...", flush=True)
        print("-" * 60, flush=True)
        
        try:
            start = time.time()
            data = extractor.extract_financials(ticker)
            duration = time.time() - start
            
            if data and isinstance(data, dict):
                data_size = len(str(data))
                keys = len(data)
                
                result = {
                    'ticker': ticker,
                    'status': 'PASS',
                    'duration': duration,
                    'data_size': data_size,
                    'keys': keys
                }
                
                print(f"✅ {ticker}: SUCCESS", flush=True)
                print(f"   Time: {duration:.2f}s", flush=True)
                print(f"   Data: {data_size:,} bytes, {keys} keys", flush=True)
                
            else:
                result = {
                    'ticker': ticker,
                    'status': 'FAIL',
                    'duration': duration,
                    'error': 'No data returned'
                }
                print(f"❌ {ticker}: FAILED - No data")
                
        except Exception as e:
            result = {
                'ticker': ticker,
                'status': 'ERROR',
                'error': str(e)
            }
            print(f"❌ {ticker}: ERROR - {e}")
        
        results.append(result)
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for r in results if r['status'] == 'PASS')
    failed = sum(1 for r in results if r['status'] in ['FAIL', 'ERROR'])
    
    print(f"\nTotal Companies: {len(results)}")
    print(f"✅ Passed: {passed} ({passed/len(results)*100:.1f}%)")
    print(f"❌ Failed: {failed} ({failed/len(results)*100:.1f}%)")
    
    if passed > 0:
        avg_time = sum(r.get('duration', 0) for r in results if r['status'] == 'PASS') / passed
        print(f"\nAverage extraction time: {avg_time:.2f}s")
    
    # Detailed results
    print("\n" + "-"*80)
    print("DETAILED RESULTS:")
    print("-"*80)
    
    for r in results:
        status_icon = "✅" if r['status'] == 'PASS' else "❌"
        ticker = r['ticker'].ljust(6)
        status = r['status'].ljust(6)
        
        if r['status'] == 'PASS':
            print(f"{status_icon} {ticker} {status} {r['duration']:.2f}s  {r['data_size']:>8,} bytes")
        else:
            print(f"{status_icon} {ticker} {status} {r.get('error', 'Unknown error')}")
    
    print("\n" + "="*80)
    print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    return passed == len(results)

if __name__ == "__main__":
    try:
        success = test_all_companies()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n❌ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

