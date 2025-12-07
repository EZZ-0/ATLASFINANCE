"""
Heavy Testing Script - Executor Batch B
Tests 15 tickers for data extraction quality and performance.
"""

import yfinance as yf
import time
from datetime import datetime

BATCH_B = ["XOM", "CVX", "PFE", "KO", "PEP", "MCD", "DIS", "NFLX", "INTC", "AMD", "CRM", "ORCL", "IBM", "WMT", "COST"]

def run_heavy_test():
    print("=" * 70)
    print("HEAVY TESTING - EXECUTOR BATCH B")
    print("=" * 70)
    print(f"Start Time: {datetime.now().isoformat()}")
    print(f"Tickers: {len(BATCH_B)}")
    print("=" * 70)
    
    results = []
    
    for ticker in BATCH_B:
        print(f"\nTesting {ticker}...")
        error = None
        fields = 0
        elapsed = 0
        
        try:
            start = time.time()
            stock = yf.Ticker(ticker)
            info = stock.info
            elapsed = time.time() - start
            
            # Count non-null fields
            fields = sum(1 for v in info.values() if v is not None)
            
            # Check critical fields
            critical = ['currentPrice', 'marketCap', 'trailingPE', 'forwardPE', 'trailingEps']
            missing_critical = [f for f in critical if info.get(f) is None]
            
            if missing_critical:
                error = f"Missing: {', '.join(missing_critical)}"
            
            print(f"  {ticker}: {fields} fields, {elapsed:.2f}s" + (f" | {error}" if error else " | OK"))
            
        except Exception as e:
            error = str(e)[:50]
            print(f"  {ticker}: ERROR - {error}")
        
        results.append({
            'ticker': ticker,
            'fields': fields,
            'time': elapsed,
            'error': error
        })
    
    print("\n" + "=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)
    
    # Summary
    total_time = sum(r['time'] for r in results)
    avg_time = total_time / len(results)
    errors = sum(1 for r in results if r['error'])
    avg_fields = sum(r['fields'] for r in results) / len(results)
    
    print(f"\nSummary:")
    print(f"  Total tickers: {len(BATCH_B)}")
    print(f"  Tickers with issues: {errors}")
    print(f"  Average fields: {avg_fields:.0f}")
    print(f"  Average load time: {avg_time:.2f}s")
    print(f"  Total time: {total_time:.2f}s")
    
    # Output for markdown
    print("\n" + "=" * 70)
    print("MARKDOWN TABLE OUTPUT")
    print("=" * 70)
    print("| Ticker | Fields | Load Time | Status |")
    print("|--------|--------|-----------|--------|")
    for r in results:
        status = r['error'] if r['error'] else "✅ OK"
        print(f"| {r['ticker']} | {r['fields']} | {r['time']:.2f}s | {status} |")
    
    return results

if __name__ == "__main__":
    run_heavy_test()

