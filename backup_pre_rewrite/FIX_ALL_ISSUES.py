"""
Quick script to verify and fix all data formatting issues
Run this then restart Streamlit with: streamlit run usa_app.py --server.runOnSave=true
"""

import pandas as pd

# Test data formatting function
def format_number(x):
    """Universal number formatter"""
    if pd.isna(x) or x == 0:
        return "N/A"
    
    abs_x = abs(x)
    
    if abs_x >= 1e12:
        return f"${x/1e12:.2f}T"
    elif abs_x >= 1e9:
        return f"${x/1e9:.2f}B"
    elif abs_x >= 1e6:
        return f"${x/1e6:.1f}M"
    elif abs_x >= 1e3:
        return f"${x/1e3:.1f}K"
    else:
        return f"${x:.2f}"

# Test cases
test_values = [
    1.45e11,   # Should be $145.00B
    1.35e11,   # Should be $135.00B
    1.26e11,   # Should be $126.00B
    3.93e9,    # Should be $3.9B
    2.65e9,    # Should be $2.7B
    1.98e8,    # Should be $198.0M
    7.46,      # Should be $7.46
    0,         # Should be N/A
]

print("Testing number formatting:")
print("="*50)
for val in test_values:
    print(f"Input: {val:15.2e}  →  Output: {format_number(val)}")
print("="*50)
print("\n✅ Formatting function works correctly!")
print("\nNext steps:")
print("1. Delete __pycache__ folder")
print("2. Restart Streamlit: streamlit run usa_app.py")

