"""Test Reverse-DCF Implementation"""
from usa_backend import quick_extract
from reverse_dcf import analyze_reverse_dcf

print("="*80)
print("TESTING REVERSE-DCF ON AAPL")
print("="*80)

# Extract AAPL data
print("\n[1/3] Extracting AAPL data...")
data = quick_extract('AAPL', fiscal_year_offset=0)

if not data:
    print("[FAIL] Extraction failed")
    exit(1)

print(f"[OK] Extraction complete")
print(f"     Current Price: ${data['market_data']['current_price']:.2f}")
print(f"     Revenue: ${data['income_statement'].loc['Total Revenue'].iloc[0]/1e9:.2f}B")

# Run Reverse-DCF
print("\n[2/3] Running Reverse-DCF analysis...")
result = analyze_reverse_dcf(data)

if result['method_1_growth_only']['status'] == 'success':
    method1 = result['method_1_growth_only']
    print("\n" + "-"*80)
    print("METHOD 1: SOLVE FOR GROWTH RATE ONLY")
    print("-"*80)
    print(f"Current Stock Price:        ${method1['current_price']:.2f}")
    print(f"Implied Growth Rate:        {method1['implied_growth_rate']*100:.2f}% annually")
    print(f"Target Enterprise Value:    ${method1['target_enterprise_value']:.2f}B")
    print(f"Calculated Enterprise Value: ${method1['calculated_enterprise_value']:.2f}B")
    print(f"Error:                      {method1['error_pct']*100:.4f}%")
    print(f"\nAnalysis: {method1['analysis']}")
    print(f"\nRecommendation:\n{method1['recommendation']}")
else:
    print(f"[FAIL] Method 1 failed: {result['method_1_growth_only']['message']}")

if result['method_2_growth_and_margin']['status'] == 'success':
    method2 = result['method_2_growth_and_margin']
    print("\n" + "-"*80)
    print("METHOD 2: SOLVE FOR GROWTH + MARGIN")
    print("-"*80)
    print(f"Implied Growth Rate:         {method2['implied_growth_rate']*100:.2f}% annually")
    print(f"Implied Operating Margin:    {method2['implied_operating_margin']*100:.2f}%")
    print(f"Current Operating Margin:    {method2['current_margin']*100:.2f}%")
    print(f"Margin Change Required:      {method2['margin_change_required']*100:+.2f} percentage points")
    print(f"\nAnalysis: {method2['analysis']}")
else:
    print(f"[FAIL] Method 2 failed: {result['method_2_growth_and_margin']['message']}")

print("\n[3/3] Reverse-DCF test complete!")
print("="*80)






