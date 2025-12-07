"""
HEAVY DATA TESTING - PRE-BUILT BATCHES
======================================
30 tickers split into batches for parallel agent testing.

Usage:
    python validation/test_batches.py --batch A1  # Architect Batch 1
    python validation/test_batches.py --batch B1  # Executor Batch 1
    python validation/test_batches.py --batch A2  # Architect Batch 2
    ...etc

Author: ATLAS Architect
Date: 2025-12-08
"""

import yfinance as yf
import time
import sys
from datetime import datetime

# ============================================================================
# BATCH DEFINITIONS - 60 TOTAL TICKERS
# ============================================================================

BATCHES = {
    # ARCHITECT BATCHES (A1-A4)
    "A1": {
        "name": "Architect Batch 1 - Mega Caps",
        "tickers": ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "BRK-B", "JPM", "V", "JNJ", "UNH", "PG", "HD", "MA"],
        "focus": "extraction_completeness"
    },
    "A2": {
        "name": "Architect Batch 2 - Mid Caps",
        "tickers": ["SQ", "SHOP", "ZOOM", "ROKU", "SNOW", "PLTR", "NET", "DDOG", "ZS", "CRWD", "OKTA", "BILL", "MELI", "SE", "PINS"],
        "focus": "growth_metrics"
    },
    "A3": {
        "name": "Architect Batch 3 - Dividends",
        "tickers": ["T", "VZ", "MO", "PM", "XOM", "CVX", "O", "ABBV", "PFE", "BMY", "MMM", "IBM", "KHC", "WBA", "LMT"],
        "focus": "dividend_metrics"
    },
    "A4": {
        "name": "Architect Batch 4 - Banks & Finance",
        "tickers": ["BAC", "WFC", "C", "GS", "MS", "SCHW", "BLK", "AXP", "COF", "USB", "PNC", "TFC", "SPGI", "ICE", "CME"],
        "focus": "financial_sector"
    },
    
    # EXECUTOR BATCHES (B1-B4)
    "B1": {
        "name": "Executor Batch 1 - Consumer",
        "tickers": ["XOM", "CVX", "PFE", "KO", "PEP", "MCD", "DIS", "NFLX", "INTC", "AMD", "CRM", "ORCL", "IBM", "WMT", "COST"],
        "focus": "consumer_staples"
    },
    "B2": {
        "name": "Executor Batch 2 - Healthcare",
        "tickers": ["LLY", "MRK", "TMO", "ABT", "DHR", "AMGN", "GILD", "VRTX", "REGN", "ISRG", "ZTS", "SYK", "BDX", "EW", "IQV"],
        "focus": "healthcare_sector"
    },
    "B3": {
        "name": "Executor Batch 3 - Industrials",
        "tickers": ["CAT", "DE", "HON", "UPS", "UNP", "RTX", "BA", "LMT", "GE", "MMM", "EMR", "ETN", "ITW", "PH", "ROK"],
        "focus": "industrial_sector"
    },
    "B4": {
        "name": "Executor Batch 4 - Real Estate & Utilities",
        "tickers": ["AMT", "PLD", "CCI", "EQIX", "PSA", "SPG", "O", "DLR", "AVB", "EQR", "NEE", "DUK", "SO", "D", "AEP"],
        "focus": "reits_utilities"
    },
}

CRITICAL_FIELDS = [
    'currentPrice', 'marketCap', 'trailingPE', 'forwardPE', 'priceToBook',
    'returnOnEquity', 'debtToEquity', 'freeCashflow', 'totalRevenue',
    'grossMargins', 'operatingMargins', 'profitMargins', 'beta',
    'dividendYield', 'trailingEps', 'forwardEps'
]

DIVIDEND_FIELDS = ['dividendRate', 'dividendYield', 'payoutRatio', 'fiveYearAvgDividendYield', 'exDividendDate']
GROWTH_FIELDS = ['revenueGrowth', 'earningsGrowth', 'earningsQuarterlyGrowth', 'revenueQuarterlyGrowth']


def run_batch(batch_id: str):
    """Run a specific test batch."""
    
    if batch_id not in BATCHES:
        print(f"ERROR: Unknown batch '{batch_id}'")
        print(f"Available: {', '.join(BATCHES.keys())}")
        return
    
    batch = BATCHES[batch_id]
    tickers = batch["tickers"]
    focus = batch["focus"]
    
    print("=" * 70)
    print(f"BATCH {batch_id}: {batch['name']}")
    print(f"Focus: {focus}")
    print(f"Started: {datetime.now()}")
    print("=" * 70)
    
    results = []
    
    for i, ticker in enumerate(tickers, 1):
        print(f"\n[{i}/{len(tickers)}] {ticker}...", end=" ")
        
        try:
            start = time.time()
            stock = yf.Ticker(ticker)
            info = stock.info
            elapsed = time.time() - start
            
            # Count critical fields
            present = [f for f in CRITICAL_FIELDS if info.get(f) is not None]
            missing = [f for f in CRITICAL_FIELDS if info.get(f) is None]
            
            # Focus-specific checks
            extra_checks = {}
            if focus == "dividend_metrics":
                div_present = [f for f in DIVIDEND_FIELDS if info.get(f) is not None]
                extra_checks['dividend_fields'] = len(div_present)
            elif focus == "growth_metrics":
                growth_present = [f for f in GROWTH_FIELDS if info.get(f) is not None]
                extra_checks['growth_fields'] = len(growth_present)
            
            print(f"{len(present)}/{len(CRITICAL_FIELDS)} | {elapsed:.2f}s")
            
            results.append({
                'ticker': ticker,
                'status': 'OK',
                'fields': len(present),
                'missing': missing,
                'time': elapsed,
                **extra_checks
            })
            
        except Exception as e:
            print(f"ERROR: {str(e)[:40]}")
            results.append({
                'ticker': ticker,
                'status': 'ERROR',
                'error': str(e)[:100]
            })
    
    # Generate report
    generate_report(batch_id, batch, results)
    
    return results


def generate_report(batch_id: str, batch: dict, results: list):
    """Generate markdown report for batch."""
    
    ok_count = sum(1 for r in results if r['status'] == 'OK')
    
    # Count missing fields
    all_missing = {}
    for r in results:
        for m in r.get('missing', []):
            all_missing[m] = all_missing.get(m, 0) + 1
    
    report = f"""# Test Results - Batch {batch_id}
**{batch['name']}**

Generated: {datetime.now()}

## Summary
- Tickers: {len(results)}
- Success: {ok_count}/{len(results)}
- Focus: {batch['focus']}

## Results

| Ticker | Status | Fields | Time | Missing |
|--------|--------|--------|------|---------|
"""
    
    for r in results:
        status = r['status']
        fields = f"{r.get('fields', 0)}/16"
        time_s = f"{r.get('time', 0):.2f}s"
        missing = ', '.join(r.get('missing', [])[:2])
        if len(r.get('missing', [])) > 2:
            missing += '...'
        report += f"| {r['ticker']} | {status} | {fields} | {time_s} | {missing or 'None'} |\n"
    
    report += f"""
## Missing Fields Summary

| Field | Count | % |
|-------|-------|---|
"""
    
    for field, count in sorted(all_missing.items(), key=lambda x: -x[1]):
        pct = round(count / len(results) * 100)
        report += f"| {field} | {count} | {pct}% |\n"
    
    # Save report
    filename = f"validation/batch_{batch_id}_results.md"
    with open(filename, 'w') as f:
        f.write(report)
    
    print(f"\n{'=' * 70}")
    print(f"SUCCESS: {ok_count}/{len(results)} tickers")
    print(f"Report: {filename}")
    print("=" * 70)


def list_batches():
    """List all available batches."""
    print("\n" + "=" * 70)
    print("AVAILABLE TEST BATCHES")
    print("=" * 70)
    
    print("\nARCHITECT BATCHES:")
    for bid in ["A1", "A2", "A3", "A4"]:
        b = BATCHES[bid]
        print(f"  {bid}: {b['name']} ({len(b['tickers'])} tickers)")
    
    print("\nEXECUTOR BATCHES:")
    for bid in ["B1", "B2", "B3", "B4"]:
        b = BATCHES[bid]
        print(f"  {bid}: {b['name']} ({len(b['tickers'])} tickers)")
    
    print("\nUsage: python validation/test_batches.py --batch <ID>")
    print("=" * 70)


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] == "--list":
        list_batches()
    elif sys.argv[1] == "--batch" and len(sys.argv) >= 3:
        run_batch(sys.argv[2].upper())
    else:
        print("Usage:")
        print("  python validation/test_batches.py --list")
        print("  python validation/test_batches.py --batch A1")

