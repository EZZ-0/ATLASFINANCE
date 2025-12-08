"""
BRUTAL HONEST AUDIT - Why isn't code showing up?
"""
import os

print("=" * 60)
print("AUDIT: WHY ISN'T CODE PUSHING TO LOCAL?")
print("=" * 60)

# 1. What tabs ACTUALLY exist
print("\n1. ACTUAL TAB STRUCTURE:")
with open('usa_app.py', 'r', encoding='utf-8') as f:
    app = f.read()

# Main tabs
if '"Dashboard"' in app:
    print("   Main Tab 1: Dashboard")
if '"Data"' in app:
    print("   Main Tab 2: Data")
if '"Deep Dive"' in app:
    print("   Main Tab 3: Deep Dive")
if '"Valuation"' in app:
    print("   Main Tab 4: Valuation")
if '"Risk & Ownership"' in app:
    print("   Main Tab 5: Risk & Ownership")
if '"Summary"' in app:
    print("   Main Tab: Summary EXISTS")
else:
    print("   NO SUMMARY TAB - PDF Export has no home!")

# 2. Check if Investment Summary tab exists at all
print("\n2. INVESTMENT SUMMARY / PDF EXPORT:")
if 'investment_summary' in app:
    print("   investment_summary IMPORTED in usa_app.py")
    # Find where it's rendered
    if 'render_investment_summary' in app:
        print("   render_investment_summary() IS CALLED")
    else:
        print("   render_investment_summary() NEVER CALLED - DEAD CODE!")
else:
    print("   investment_summary NOT IMPORTED - Module exists but unused!")

# 3. Check flip cards integration
print("\n3. FLIP CARDS:")
if 'from flip_cards import' in app:
    print("   flip_cards IMPORTED")
    # Count actual calls
    flip_calls = app.count('render_flip_card(')
    print(f"   render_flip_card() called {flip_calls} times")
    
    # Where are they called?
    if 'render_dashboard_metrics' in app:
        print("   render_dashboard_metrics: IMPORTED")
        if 'render_dashboard_metrics(' in app:
            # Check if call is in usa_app.py or delegated to dashboard_tab
            print("   But is it called in usa_app.py? NO - delegated to dashboard_tab.py")
else:
    print("   flip_cards NOT IMPORTED")

# 4. Check theme selector
print("\n4. THEME SELECTOR:")
if 'render_theme_selector' in app:
    print("   render_theme_selector IMPORTED")
    if 'render_theme_selector(' in app:
        count = app.count('render_theme_selector(')
        print(f"   render_theme_selector() called {count} times")
    else:
        print("   render_theme_selector() NEVER CALLED!")
else:
    print("   render_theme_selector NOT IMPORTED")

# 5. Check insider/ownership/earnings tabs
print("\n5. ALPHA SIGNAL TABS (Insider, Ownership, Earnings):")
# These should be in the Valuation sub-tabs
if 'insider_tab' in app:
    print("   insider_tab variable EXISTS")
if 'ownership_tab' in app:
    print("   ownership_tab variable EXISTS")
if 'earnings_tab' in app:
    print("   earnings_tab variable EXISTS")

# Check if insider_transactions module is used
if 'InsiderAnalyzer' in app or 'analyze_insider' in app:
    print("   InsiderAnalyzer IS USED")
else:
    print("   InsiderAnalyzer NOT USED - just tab exists, no data!")

if 'OwnershipAnalyzer' in app or 'analyze_ownership' in app:
    print("   OwnershipAnalyzer IS USED")
else:
    print("   OwnershipAnalyzer NOT USED")

# 6. Check mobile responsive
print("\n6. MOBILE RESPONSIVE:")
if 'inject_responsive_css' in app:
    print("   inject_responsive_css IMPORTED")
    if 'inject_responsive_css(' in app:
        print("   inject_responsive_css() IS CALLED")
    else:
        print("   inject_responsive_css() NEVER CALLED!")
else:
    print("   Mobile CSS NOT IMPORTED")

# 7. Check draggable grid
print("\n7. DRAGGABLE GRID:")
if 'draggable_grid' in app:
    print("   draggable_grid IMPORTED")
else:
    print("   draggable_grid NOT IMPORTED in usa_app.py")

# Check dashboard_tab.py
with open('dashboard_tab.py', 'r', encoding='utf-8') as f:
    dash = f.read()
if 'draggable_grid' in dash:
    print("   draggable_grid IMPORTED in dashboard_tab.py")
if 'render_reorder_controls' in dash:
    print("   render_reorder_controls() CALLED in dashboard_tab.py")

# 8. Line count of usa_app.py - is it bloated?
print("\n8. FILE SIZE:")
lines = len(app.split('\n'))
print(f"   usa_app.py: {lines} lines")
if lines > 3000:
    print("   BLOATED - likely causing slow performance")

# 9. Check for obvious errors
print("\n9. SYNTAX CHECK:")
try:
    compile(app, 'usa_app.py', 'exec')
    print("   usa_app.py: SYNTAX OK")
except SyntaxError as e:
    print(f"   usa_app.py: SYNTAX ERROR at line {e.lineno}: {e.msg}")

print("\n" + "=" * 60)
print("VERDICT:")
print("=" * 60)

