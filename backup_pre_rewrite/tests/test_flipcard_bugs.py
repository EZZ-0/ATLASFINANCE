"""
FLIP CARD BUG TESTING
=====================
Tests flip_card_component.py and flip_card_v2.py for bugs.
Part of MILESTONE-007 testing phase.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("="*60)
print("FLIP CARD BUG TESTING")
print("="*60)

# Test flip_card_component.py
print("\n" + "="*60)
print("TESTING: flip_card_component.py")
print("="*60)

try:
    from flip_card_component import FlipCardMetric, create_metrics_from_financials
    
    # Test 1: Basic initialization
    print("\n[TEST 1] Basic FlipCardMetric creation...")
    try:
        metric = FlipCardMetric(
            name='P/E Ratio',
            value=22.5,
            formula='Price / EPS',
            components={'Price': 175.50, 'EPS': 7.80},
            category='Valuation'
        )
        print(f"  Name: {metric.name} ✓")
        print(f"  Value: {metric.format_value()} ✓")
        print(f"  Color: {metric.get_color()} ✓")
        print(f"  Calculation: {metric.get_calculation_string()} ✓")
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
    
    # Test 2: Edge cases - None value
    print("\n[TEST 2] None value handling...")
    try:
        metric_none = FlipCardMetric(name='Test', value=None)
        result = metric_none.format_value()
        color = metric_none.get_color()
        print(f"  format_value() = {result} ✓")
        print(f"  get_color() = {color} ✓")
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
    
    # Test 3: Edge cases - N/A string
    print("\n[TEST 3] N/A string handling...")
    try:
        metric_na = FlipCardMetric(name='Test', value='N/A')
        result = metric_na.format_value()
        color = metric_na.get_color()
        print(f"  format_value() = {result} ✓")
        print(f"  get_color() = {color} ✓")
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
    
    # Test 4: Negative values
    print("\n[TEST 4] Negative value handling...")
    try:
        metric_neg = FlipCardMetric(name='Net Margin', value=-0.15)
        result = metric_neg.format_value()
        print(f"  Net Margin -0.15 -> {result} ✓")
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
    
    # Test 5: Very large numbers
    print("\n[TEST 5] Large number formatting...")
    try:
        metric_big = FlipCardMetric(name='Market Cap', value=2.5e12)
        print(f"  2.5T = {metric_big.format_value()} ✓")
        metric_bil = FlipCardMetric(name='Revenue', value=350e9)
        print(f"  350B = {metric_bil.format_value()} ✓")
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
    
    # Test 6: Percentage formatting
    print("\n[TEST 6] Percentage metrics...")
    try:
        metric_pct = FlipCardMetric(name='ROE', value=0.185)
        result = metric_pct.format_value()
        status = "✓" if "%" in result else "⚠️ BUG: Missing %"
        print(f"  ROE 0.185 -> {result} {status}")
        
        metric_margin = FlipCardMetric(name='Gross Margin', value=0.42)
        result2 = metric_margin.format_value()
        status2 = "✓" if "%" in result2 else "⚠️ BUG: Missing %"
        print(f"  Gross Margin 0.42 -> {result2} {status2}")
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
    
    # Test 7: Benchmark color logic
    print("\n[TEST 7] Benchmark color logic...")
    try:
        # P/E Ratio: lower is better
        low_pe = FlipCardMetric(name='P/E Ratio', value=12, benchmark={'low': 15, 'high': 25})
        high_pe = FlipCardMetric(name='P/E Ratio', value=35, benchmark={'low': 15, 'high': 25})
        print(f"  P/E 12 (low) -> {low_pe.get_color()} (should be green)")
        print(f"  P/E 35 (high) -> {high_pe.get_color()} (should be red)")
        
        # ROE: higher is better
        low_roe = FlipCardMetric(name='ROE', value=0.05, benchmark={'low': 0.10, 'high': 0.20})
        high_roe = FlipCardMetric(name='ROE', value=0.25, benchmark={'low': 0.10, 'high': 0.20})
        print(f"  ROE 5% (low) -> {low_roe.get_color()} (should be red)")
        print(f"  ROE 25% (high) -> {high_roe.get_color()} (should be green)")
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
    
    # Test 8: Zero division protection
    print("\n[TEST 8] Zero/division edge cases...")
    try:
        metric_zero = FlipCardMetric(name='Test', value=0)
        result = metric_zero.format_value()
        print(f"  value=0 -> {result} ✓")
        
        metric_zero_comp = FlipCardMetric(name='Test', value=10, components={'A': 0, 'B': 100})
        calc = metric_zero_comp.get_calculation_string()
        print(f"  Components with 0 -> {calc} ✓")
    except Exception as e:
        print(f"  ❌ ERROR: {e}")

except ImportError as e:
    print(f"❌ Import error: {e}")

# Test flip_card_v2.py
print("\n" + "="*60)
print("TESTING: flip_card_v2.py")
print("="*60)

try:
    from flip_card_v2 import (
        METRIC_CONFIG, fmt_short, get_color, format_display, build_equation
    )
    
    # Test 9: METRIC_CONFIG completeness
    print("\n[TEST 9] METRIC_CONFIG validation...")
    required_keys = ['name', 'formula_template', 'components', 'insight', 'benchmark', 'higher_is_better', 'unit']
    missing = []
    for metric_key, config in METRIC_CONFIG.items():
        for req in required_keys:
            if req not in config:
                missing.append(f"{metric_key}.{req}")
    
    if missing:
        print(f"  ⚠️ Missing config keys: {missing}")
    else:
        print(f"  All {len(METRIC_CONFIG)} metrics have required keys ✓")
    
    # Test 10: fmt_short edge cases
    print("\n[TEST 10] fmt_short formatting...")
    test_cases = [
        (None, "N/A"),
        (2.5e12, "T"),
        (350e9, "B"),
        (50e6, "M"),
        (5000, "K"),
        (123.45, "$"),
    ]
    for val, expected_contains in test_cases:
        result = fmt_short(val)
        status = "✓" if expected_contains in result else f"⚠️ Expected '{expected_contains}'"
        print(f"  fmt_short({val}) = {result} {status}")
    
    # Test 11: get_color edge cases
    print("\n[TEST 11] get_color validation...")
    print(f"  None value -> {get_color(None, 'PE_Ratio')} ✓")
    print(f"  PE high (bad) -> {get_color(50, 'PE_Ratio')}")
    print(f"  PE low (good) -> {get_color(10, 'PE_Ratio')}")
    print(f"  ROE high (good) -> {get_color(25, 'ROE')}")
    print(f"  ROE low (bad) -> {get_color(5, 'ROE')}")
    
    # Test 12: format_display edge cases
    print("\n[TEST 12] format_display validation...")
    test_displays = [
        ("PE_Ratio", 22.5, "x"),
        ("ROE", 0.185, "%"),
        ("current_price", 175.50, "$"),
        ("market_cap", 2.5e12, "$"),
    ]
    for metric_key, val, unit in test_displays:
        formatted, num = format_display(val, unit, metric_key)
        print(f"  {metric_key}: {val} -> {formatted} ✓")
    
    # Test 13: build_equation
    print("\n[TEST 13] build_equation...")
    comp = {'price': 175.50, 'eps': 7.80, 'net_income': 100e9, 'equity': 500e9}
    eq = build_equation('PE_Ratio', comp)
    print(f"  PE equation: {eq}")
    eq2 = build_equation('ROE', comp)
    print(f"  ROE equation: {eq2}")
    
except ImportError as e:
    print(f"❌ Import error: {e}")

print("\n" + "="*60)
print("BUG TEST COMPLETE")
print("="*60)

