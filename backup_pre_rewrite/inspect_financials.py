"""
Quick diagnostic to see what's actually in the financials dictionary for APA
"""
import streamlit as st
from usa_backend import USAFinancialExtractor

st.title("🔍 Financials Dictionary Inspector")

ticker = st.text_input("Ticker", value="APA")

if st.button("Inspect"):
    extractor = USAFinancialExtractor()
    financials = extractor.extract_financials(ticker)
    
    st.subheader("📊 Top-level Keys:")
    st.write(list(financials.keys()))
    
    st.subheader("📈 Sample Top-level Values:")
    for key in ['current_price', 'pe_ratio', 'market_cap', 'revenue', 'net_income', 'roe', 'ticker']:
        st.write(f"**{key}:** {financials.get(key, 'NOT FOUND')}")
    
    st.subheader("📋 Income Statement Info:")
    income = financials.get('income_statement', None)
    if income is not None:
        st.write(f"Type: {type(income)}")
        if hasattr(income, 'columns'):
            st.write(f"Columns: {list(income.columns)}")
        if hasattr(income, 'index'):
            st.write(f"Index (first 10): {list(income.index[:10])}")
    
    st.subheader("🔢 Ratios Info:")
    ratios = financials.get('ratios', None)
    if ratios is not None:
        st.write(f"Type: {type(ratios)}")
        if isinstance(ratios, dict):
            st.write(f"Keys: {list(ratios.keys())}")
    
    st.subheader("📦 Full Dictionary (first level):")
    st.json({k: str(type(v)) for k, v in financials.items()})


