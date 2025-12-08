"""
Quick Heavy Test - Bypass USAFinancialExtractor
Test yfinance directly for 15 tickers
"""

import yfinance as yf
import time
from datetime import datetime

BATCH_A = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "BRK-B", "JPM", "V", 
           "JNJ", "UNH", "PG", "HD", "MA"]

CRITICAL_FIELDS = [
    'currentPrice', 'marketCap', 'trailingPE', 'forwardPE', 'priceToBook',
    'returnOnEquity', 'debtToEquity', 'freeCashflow', 'totalRevenue',
    'grossMargins', 'operatingMargins', 'profitMargins', 'beta',
    'dividendYield', 'trailingEps', 'forwardEps'
]

print("=" * 70)
print("HEAVY DATA TEST - BATCH A (15 tickers)")
print(f"Started: {datetime.now()}")
print("=" * 70)

results = []

for i, ticker in enumerate(BATCH_A, 1):
    print(f"\n[{i}/15] {ticker}...", end=" ")
    
    try:
        start = time.time()
        stock = yf.Ticker(ticker)
        info = stock.info
        elapsed = time.time() - start
        
        # Count fields
        present = [f for f in CRITICAL_FIELDS if info.get(f) is not None]
        missing = [f for f in CRITICAL_FIELDS if info.get(f) is None]
        
        print(f"{len(present)}/{len(CRITICAL_FIELDS)} fields | {elapsed:.2f}s")
        
        results.append({
            'ticker': ticker,
            'status': 'OK',
            'fields': len(present),
            'missing': missing,
            'time': elapsed
        })
        
    except Exception as e:
        print(f"ERROR: {str(e)[:50]}")
        results.append({
            'ticker': ticker,
            'status': 'ERROR',
            'error': str(e)
        })

# Summary
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

ok = sum(1 for r in results if r['status'] == 'OK')
print(f"Success: {ok}/{len(results)}")

# Find most missing fields
all_missing = {}
for r in results:
    for m in r.get('missing', []):
        all_missing[m] = all_missing.get(m, 0) + 1

print("\nMost Missing Fields:")
for field, count in sorted(all_missing.items(), key=lambda x: -x[1])[:5]:
    print(f"  {field}: {count}/{len(results)} ({round(count/len(results)*100)}%)")

# Save report
report = f"""# Heavy Test Results - Architect Batch A
Generated: {datetime.now()}

## Summary
- Tickers tested: {len(results)}
- Success: {ok}/{len(results)}

## Results

| Ticker | Status | Fields | Time | Missing |
|--------|--------|--------|------|---------|
"""

for r in results:
    status = r['status']
    fields = f"{r.get('fields', 0)}/16"
    time_s = f"{r.get('time', 0):.2f}s"
    missing = ', '.join(r.get('missing', [])[:3])
    if len(r.get('missing', [])) > 3:
        missing += '...'
    report += f"| {r['ticker']} | {status} | {fields} | {time_s} | {missing or 'None'} |\n"

report += f"""
## Most Missing Fields

| Field | Missing Count |
|-------|---------------|
"""

for field, count in sorted(all_missing.items(), key=lambda x: -x[1]):
    report += f"| {field} | {count} |\n"

with open('validation/heavy_test_results_architect.md', 'w') as f:
    f.write(report)

print("\nReport saved: validation/heavy_test_results_architect.md")

