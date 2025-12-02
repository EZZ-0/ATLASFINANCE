"""Quick test to verify Reverse-DCF works end-to-end"""
from usa_backend import quick_extract
from reverse_dcf import analyze_reverse_dcf

print("="*80)
print("TESTING REVERSE-DCF END-TO-END")
print("="*80)

# Extract AAPL data
print("\n[1/3] Extracting AAPL data...")
financials = quick_extract('AAPL', fiscal_year_offset=0)

if not financials:
    print("[FAIL] Extraction failed")
    exit(1)

print("[OK] Extraction complete")

# Check if market price is available
market_data = financials.get('market_data', {})
current_price = market_data.get('current_price')

print(f"\n[2/3] Checking market data...")
print(f"  Current Price: ${current_price}")
print(f"  Market Data Keys: {list(market_data.keys())}")

if not current_price:
    print("[FAIL] No current price found")
    exit(1)

print("[OK] Market price available")

# Run Reverse-DCF
print(f"\n[3/3] Running Reverse-DCF analysis...")
results = analyze_reverse_dcf(financials)

print("\n" + "="*80)
print("REVERSE-DCF RESULTS")
print("="*80)

# Method 1
method1 = results.get('method_1_growth_only', {})
if method1.get('status') == 'success':
    print(f"\nMethod 1 (Growth Only):")
    print(f"  Implied Growth Rate:  {method1['implied_growth_rate']*100:.2f}%")
    print(f"  Current Price:        ${method1['current_price']:.2f}")
    print(f"  Calculation Error:    {method1['error_pct']*100:.4f}%")
    print(f"  [OK] Method 1 SUCCESS")
else:
    print(f"\n[FAIL] Method 1: {method1.get('message', 'Unknown error')}")

# Method 2
method2 = results.get('method_2_growth_and_margin', {})
if method2.get('status') == 'success':
    print(f"\nMethod 2 (Growth + Margin):")
    print(f"  Implied Growth Rate:      {method2['implied_growth_rate']*100:.2f}%")
    print(f"  Implied Operating Margin: {method2['implied_operating_margin']*100:.2f}%")
    print(f"  Calculation Error:        {method2['error_pct']*100:.4f}%")
    print(f"  [OK] Method 2 SUCCESS")
else:
    print(f"\n[WARN] Method 2: {method2.get('message', 'Unknown error')}")

# Summary
summary = results.get('summary', {})
print(f"\nSummary:")
print(f"  Current Price:         ${summary['current_price']:.2f}")
print(f"  Revenue (Latest):      ${summary['revenue_latest']:.2f}B")
print(f"  Operating Margin:      {summary['operating_margin_current']:.2f}%")

print("\n" + "="*80)
print("[SUCCESS] REVERSE-DCF TEST COMPLETE")
print("="*80)





