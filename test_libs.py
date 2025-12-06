"""
Quick test to verify UI library installation
"""
print("Testing UI Libraries...")
print("=" * 50)

# Test streamlit-aggrid
try:
    from st_aggrid import AgGrid
    print("✅ streamlit-aggrid: INSTALLED")
except ImportError as e:
    print(f"❌ streamlit-aggrid: NOT INSTALLED ({e})")

# Test streamlit-echarts
try:
    from streamlit_echarts import st_echarts
    print("✅ streamlit-echarts: INSTALLED")
except ImportError as e:
    print(f"❌ streamlit-echarts: NOT INSTALLED ({e})")

# Test streamlit-extras
try:
    from streamlit_extras.metric_cards import style_metric_cards
    print("✅ streamlit-extras: INSTALLED")
except ImportError as e:
    print(f"❌ streamlit-extras: NOT INSTALLED ({e})")

# Test pygwalker
try:
    import pygwalker
    print("✅ pygwalker: INSTALLED")
except ImportError as e:
    print(f"❌ pygwalker: NOT INSTALLED ({e})")

# Test streamlit-lottie
try:
    from streamlit_lottie import st_lottie
    print("✅ streamlit-lottie: INSTALLED")
except ImportError as e:
    print(f"❌ streamlit-lottie: NOT INSTALLED ({e})")

# Test lightweight-charts
try:
    from lightweight_charts import Chart
    print("✅ lightweight-charts: INSTALLED")
except ImportError as e:
    print(f"❌ lightweight-charts: NOT INSTALLED ({e})")

print("=" * 50)
print("Test complete!")






