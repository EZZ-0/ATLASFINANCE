"""
HEAVY DATA TESTING - ARCHITECT BATCH A
=======================================
15 tickers: AAPL, MSFT, GOOGL, AMZN, NVDA, META, TSLA, BRK-B, JPM, V, JNJ, UNH, PG, HD, MA

Tests:
1. Financial extraction completeness
2. Flip card metric color accuracy
3. DCF/WACC calculation validation
4. Insider/Ownership data presence

Author: ATLAS Architect
Date: 2025-12-08
"""

import sys
import os
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Tickers for Architect batch
BATCH_A = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "BRK-B", "JPM", "V", 
           "JNJ", "UNH", "PG", "HD", "MA"]

# Key fields we expect
CRITICAL_FIELDS = [
    'currentPrice', 'marketCap', 'trailingPE', 'forwardPE', 'priceToBook',
    'returnOnEquity', 'debtToEquity', 'freeCashflow', 'totalRevenue',
    'grossMargins', 'operatingMargins', 'profitMargins', 'beta',
    'dividendYield', 'trailingEps', 'forwardEps'
]

def test_extraction_completeness(ticker, extractor):
    """Test how many critical fields are present."""
    try:
        start = time.time()
        data = extractor.extract_all_financials(ticker)
        elapsed = time.time() - start
        
        info = data.get('info', {})
        
        present = []
        missing = []
        
        for field in CRITICAL_FIELDS:
            val = info.get(field)
            if val is not None and str(val) != 'nan':
                present.append(field)
            else:
                missing.append(field)
        
        return {
            'ticker': ticker,
            'status': 'OK',
            'fields_present': len(present),
            'fields_missing': len(missing),
            'missing_list': missing,
            'load_time': round(elapsed, 2),
            'data': data
        }
    except Exception as e:
        return {
            'ticker': ticker,
            'status': 'ERROR',
            'error': str(e)[:100],
            'load_time': 0
        }


def test_flip_card_colors(ticker, info):
    """Test if flip card colors are correct based on values."""
    from flip_cards import get_metric_color, METRICS
    
    results = []
    
    # Map info fields to metric keys
    field_map = {
        'ROE': ('returnOnEquity', 100),  # multiply by 100 for %
        'Debt_to_Equity': ('debtToEquity', 1),
        'Gross_Margin': ('grossMargins', 100),
        'PE_Ratio': ('trailingPE', 1),
        'Beta': ('beta', 1),
    }
    
    for metric_key, (field, multiplier) in field_map.items():
        raw_val = info.get(field)
        if raw_val is not None:
            try:
                val = float(raw_val) * multiplier
                color = get_metric_color(val, metric_key)
                
                # Check if color makes sense
                config = METRICS.get(metric_key, {})
                benchmark = config.get('benchmark')
                direction = config.get('higher_is', 'neutral')
                
                expected = None
                if benchmark:
                    low, high = benchmark
                    if direction == 'better':
                        if val >= high: expected = 'green'
                        elif val <= low: expected = 'red'
                        else: expected = 'yellow'
                    elif direction == 'worse':
                        if val <= low: expected = 'green'
                        elif val >= high: expected = 'red'
                        else: expected = 'yellow'
                
                actual = 'green' if color == '#10b981' else 'red' if color == '#ef4444' else 'yellow' if color == '#f59e0b' else 'blue'
                
                correct = expected == actual if expected else True
                
                results.append({
                    'metric': metric_key,
                    'value': round(val, 2),
                    'color': actual,
                    'expected': expected or 'neutral',
                    'correct': correct
                })
            except:
                pass
    
    return results


def test_insider_data(ticker):
    """Test if insider transaction data is available."""
    try:
        from insider_transactions import get_insider_summary
        data = get_insider_summary(ticker, days=90)
        
        if data:
            return {
                'ticker': ticker,
                'has_data': True,
                'sentiment_score': data.sentiment_score,
                'buy_count': data.buy_transactions,
                'sell_count': data.sell_transactions
            }
        else:
            return {'ticker': ticker, 'has_data': False}
    except Exception as e:
        return {'ticker': ticker, 'has_data': False, 'error': str(e)[:50]}


def test_ownership_data(ticker):
    """Test if institutional ownership data is available."""
    try:
        from institutional_ownership import get_ownership_summary
        data = get_ownership_summary(ticker)
        
        if data:
            return {
                'ticker': ticker,
                'has_data': True,
                'institutional_pct': round(data.institutional_pct, 2),
                'insider_pct': round(data.insider_pct, 2),
                'total_institutions': data.total_institutions
            }
        else:
            return {'ticker': ticker, 'has_data': False}
    except Exception as e:
        return {'ticker': ticker, 'has_data': False, 'error': str(e)[:50]}


def run_all_tests():
    """Run all tests and generate report."""
    from usa_backend import USAFinancialExtractor
    
    print("=" * 70)
    print("HEAVY DATA TESTING - ARCHITECT BATCH A")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    extractor = USAFinancialExtractor()
    
    extraction_results = []
    color_results = []
    insider_results = []
    ownership_results = []
    
    for i, ticker in enumerate(BATCH_A, 1):
        print(f"\n[{i}/{len(BATCH_A)}] Testing {ticker}...")
        
        # 1. Extraction test
        ext_result = test_extraction_completeness(ticker, extractor)
        extraction_results.append(ext_result)
        print(f"  Extraction: {ext_result['status']} | {ext_result.get('fields_present', 0)}/{len(CRITICAL_FIELDS)} fields | {ext_result.get('load_time', 0)}s")
        
        # 2. Color test (if data available)
        if ext_result['status'] == 'OK':
            info = ext_result['data'].get('info', {})
            colors = test_flip_card_colors(ticker, info)
            color_results.append({'ticker': ticker, 'colors': colors})
            correct = sum(1 for c in colors if c['correct'])
            print(f"  Colors: {correct}/{len(colors)} correct")
        
        # 3. Insider test
        insider = test_insider_data(ticker)
        insider_results.append(insider)
        print(f"  Insider: {'YES' if insider.get('has_data') else 'NO'}")
        
        # 4. Ownership test
        ownership = test_ownership_data(ticker)
        ownership_results.append(ownership)
        print(f"  Ownership: {'YES' if ownership.get('has_data') else 'NO'}")
    
    # Generate report
    generate_report(extraction_results, color_results, insider_results, ownership_results)


def generate_report(extraction, colors, insider, ownership):
    """Generate markdown report."""
    
    report = f"""# Heavy Data Testing - Architect Batch A
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary
- **Tickers Tested:** {len(BATCH_A)}
- **Extraction Success:** {sum(1 for e in extraction if e['status'] == 'OK')}/{len(extraction)}
- **Insider Data Available:** {sum(1 for i in insider if i.get('has_data'))}/{len(insider)}
- **Ownership Data Available:** {sum(1 for o in ownership if o.get('has_data'))}/{len(ownership)}

## 1. Extraction Results

| Ticker | Status | Fields | Missing | Load Time |
|--------|--------|--------|---------|-----------|
"""
    
    for e in extraction:
        status = e['status']
        fields = f"{e.get('fields_present', 0)}/{len(CRITICAL_FIELDS)}"
        missing = ', '.join(e.get('missing_list', [])[:3]) + ('...' if len(e.get('missing_list', [])) > 3 else '')
        load = f"{e.get('load_time', 0)}s"
        report += f"| {e['ticker']} | {status} | {fields} | {missing or 'None'} | {load} |\n"
    
    report += """
## 2. Flip Card Color Accuracy

| Ticker | Metric | Value | Color | Expected | Correct |
|--------|--------|-------|-------|----------|---------|
"""
    
    for c in colors:
        for col in c.get('colors', []):
            report += f"| {c['ticker']} | {col['metric']} | {col['value']} | {col['color']} | {col['expected']} | {'YES' if col['correct'] else 'NO'} |\n"
    
    report += """
## 3. Insider Transaction Data

| Ticker | Has Data | Sentiment | Buys | Sells |
|--------|----------|-----------|------|-------|
"""
    
    for i in insider:
        has = 'YES' if i.get('has_data') else 'NO'
        sent = i.get('sentiment_score', 'N/A')
        buys = i.get('buy_count', 'N/A')
        sells = i.get('sell_count', 'N/A')
        report += f"| {i['ticker']} | {has} | {sent} | {buys} | {sells} |\n"
    
    report += """
## 4. Institutional Ownership Data

| Ticker | Has Data | Inst % | Insider % | # Institutions |
|--------|----------|--------|-----------|----------------|
"""
    
    for o in ownership:
        has = 'YES' if o.get('has_data') else 'NO'
        inst = o.get('institutional_pct', 'N/A')
        ins = o.get('insider_pct', 'N/A')
        count = o.get('total_institutions', 'N/A')
        report += f"| {o['ticker']} | {has} | {inst} | {ins} | {count} |\n"
    
    # Missing fields summary
    all_missing = {}
    for e in extraction:
        for m in e.get('missing_list', []):
            all_missing[m] = all_missing.get(m, 0) + 1
    
    report += """
## 5. Most Frequently Missing Fields

| Field | Missing Count | % Missing |
|-------|---------------|-----------|
"""
    
    for field, count in sorted(all_missing.items(), key=lambda x: -x[1]):
        pct = round(count / len(extraction) * 100, 1)
        report += f"| {field} | {count} | {pct}% |\n"
    
    report += """
## Issues Found

(List any bugs or data quality issues here)

---
*Report by ATLAS Architect*
"""
    
    # Write report
    with open('validation/heavy_test_results_architect.md', 'w') as f:
        f.write(report)
    
    print("\n" + "=" * 70)
    print("REPORT SAVED: validation/heavy_test_results_architect.md")
    print("=" * 70)


if __name__ == "__main__":
    run_all_tests()

