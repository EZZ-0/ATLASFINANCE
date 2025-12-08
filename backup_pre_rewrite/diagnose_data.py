"""
Diagnostic tool to inspect what keys/values are actually available
"""
import streamlit as st
import pandas as pd
from usa_backend import USAFinancialExtractor

st.title("🔍 Financial Data Inspector")

ticker = st.text_input("Ticker", value="APA")

if st.button("Inspect", type="primary"):
    with st.spinner(f"Extracting {ticker}..."):
        extractor = USAFinancialExtractor()
        financials = extractor.extract_financials(ticker)
    
    st.success(f"✅ Extracted {ticker}")
    
    # Top-level keys
    st.subheader("📦 Top-level Keys")
    st.write(list(financials.keys()))
    
    # Ratios inspection
    st.subheader("📊 Ratios Structure")
    ratios = financials.get('ratios', None)
    if ratios is not None:
        st.write(f"**Type:** {type(ratios)}")
        if isinstance(ratios, pd.DataFrame):
            st.write(f"**Shape:** {ratios.shape}")
            st.write(f"**Index (ratio names):**")
            st.write(list(ratios.index))
            st.write(f"**Sample values:**")
            st.dataframe(ratios.head(20))
        elif isinstance(ratios, dict):
            st.write(f"**Keys:** {list(ratios.keys())}")
            st.json(ratios)
    else:
        st.error("❌ No ratios found!")
    
    # Growth rates inspection
    st.subheader("📈 Growth Rates")
    growth = financials.get('growth_rates', None)
    if growth:
        st.write(f"**Type:** {type(growth)}")
        if isinstance(growth, dict):
            st.json(growth)
        else:
            st.dataframe(growth)
    else:
        st.warning("⚠️ No growth_rates found")
    
    # Market data inspection
    st.subheader("💰 Market Data")
    market = financials.get('market_data', None)
    if market:
        st.json(market)
    else:
        st.warning("⚠️ No market_data found")
    
    # Income statement sample
    st.subheader("📋 Income Statement (first 10 rows)")
    income = financials.get('income_statement', None)
    if income is not None and not income.empty:
        st.write(f"**Type:** {type(income)}")
        st.write(f"**Shape:** {income.shape}")
        st.write(f"**Index type:** {type(income.index[0])}")
        if isinstance(income.index[0], str):
            st.write("✅ yfinance format (metrics as index)")
        st.dataframe(income.head(10))
    else:
        st.warning("⚠️ No income_statement")
    
    # Cash flow sample
    st.subheader("💰 Cash Flow Statement (first 10 rows)")
    cashflow = financials.get('cash_flow', None)
    if cashflow is not None and not cashflow.empty:
        st.write(f"**Type:** {type(cashflow)}")
        st.write(f"**Shape:** {cashflow.shape}")
        st.write(f"**Index (first 10 rows):**")
        st.write(list(cashflow.index[:10]))
        st.dataframe(cashflow.head(10))
    else:
        st.warning("⚠️ No cash_flow statement")
    
    # Test extraction for specific metrics
    st.subheader("🧪 Test Metric Extraction")
    
    def get_ratio_safe(key):
        if ratios is not None and isinstance(ratios, pd.DataFrame) and not ratios.empty:
            if key in ratios.index:
                val = ratios.loc[key].iloc[0]
                return val if pd.notnull(val) else "NULL"
        return "NOT FOUND"
    
    test_keys = [
        'Current_Price', 'PE_Ratio', 'ROE', 'Revenue', 'Net_Income',
        'Price_to_Book', 'Price_to_Sales', 'EV_to_EBITDA',
        'Revenue_CAGR_3Y', 'Net_Income_CAGR_3Y'
    ]
    
    results = {}
    for key in test_keys:
        results[key] = get_ratio_safe(key)
    
    st.json(results)
    
    # Full ratios export
    with st.expander("📄 Export Full Ratios Table"):
        if ratios is not None and isinstance(ratios, pd.DataFrame):
            st.dataframe(ratios, use_container_width=True)

