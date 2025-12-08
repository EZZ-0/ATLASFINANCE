"""
ATLAS FINANCIAL INTELLIGENCE - STREAMLIT APP
=============================================
Clean modular router - calls tab modules instead of inline code.
Target: ~400 lines (down from 3800+)

This is the NEW clean version. Test this, then replace usa_app.py.
"""

import streamlit as st
import pandas as pd
import numpy as np
import os
from datetime import datetime
import time


# ==========================================
# API KEY VALIDATION (Phase 0)
# ==========================================
def validate_api_keys():
    """Check for required API keys and warn if missing."""
    warnings = []
    
    # Critical keys (will cause feature failures)
    if not os.environ.get('FMP_API_KEY'):
        warnings.append("FMP_API_KEY not set - peer comparison and some data features may fail")
    
    # Optional keys (graceful degradation)
    if not os.environ.get('ALPHA_VANTAGE_API_KEY'):
        warnings.append("ALPHA_VANTAGE_API_KEY not set - some earnings data unavailable")
    
    if not os.environ.get('NEWSAPI_KEY'):
        warnings.append("NEWSAPI_KEY not set - news features will use fallback sources")
    
    return warnings

API_WARNINGS = validate_api_keys()

# ==========================================
# CORE IMPORTS
# ==========================================
from usa_backend import USAFinancialExtractor
from validation_engine import DataValidator
from app_css import inject_all_css, get_search_button_css
from app_landing import render_landing_page, render_ticker_display, render_no_ticker_placeholder
from app_themes import inject_theme_css, render_theme_selector, get_current_theme

# DCF and Visualization
from dcf_modeling import DCFModel
from visualization import FinancialVisualizer
from format_helpers import format_financial_number
from sp500_tickers import SP500_TICKERS, SP500_DISPLAY, extract_ticker

# Tab Modules (Existing)
from dashboard_tab import render_dashboard_tab
from analysis_tab import render_analysis_tab
from investment_summary import render_investment_summary_tab

# Tab Modules (NEW Modular)
from tabs.tab_data import render_data_tab
from tabs.tab_valuation import render_valuation_tab
from tabs.tab_risk import render_risk_tab
from tabs.tab_market import render_market_tab
from tabs.tab_news import render_news_tab

# UI Components
from ui_components import smart_dataframe, init_ui_components

# Flip cards
try:
    from flip_cards import render_flip_card
    FLIP_CARDS_ENABLED = True
except ImportError:
    FLIP_CARDS_ENABLED = False

# Mobile responsiveness
try:
    from components.mobile_responsive import inject_responsive_css, inject_viewport_meta
    MOBILE_RESPONSIVE = True
except ImportError:
    MOBILE_RESPONSIVE = False

# Authentication (disabled by default)
try:
    from auth import init_session_state as init_auth_state, is_authenticated
    from auth.config import is_monetization_active
    AUTH_ENABLED = True
except ImportError:
    AUTH_ENABLED = False
    def init_auth_state(): pass
    def is_authenticated(): return True
    def is_monetization_active(): return False

AUTH_ACTIVE = AUTH_ENABLED and is_monetization_active()

# ==========================================
# SINGLETON INSTANCES
# ==========================================
_validator = DataValidator()
extractor = USAFinancialExtractor()
visualizer = FinancialVisualizer()


def icon(name, size="1em", color=None):
    """Render a Bootstrap Icon"""
    style = f"font-size: {size};"
    if color:
        style += f" color: {color};"
    return f'<i class="bi bi-{name}" style="{style}"></i>'


# ==========================================
# CACHED EXTRACTION
# ==========================================
@st.cache_data(ttl=3600, show_spinner=False)
def cached_extract_financials(
    ticker: str,
    source: str = "auto",
    fiscal_year_offset: int = 0,
    filing_types: tuple = ("10-K", "10-Q"),
    include_quant: bool = True
) -> dict:
    """Cached wrapper for financial extraction (1 hour TTL)"""
    result = extractor.extract_financials(
        ticker,
        source=source,
        fiscal_year_offset=fiscal_year_offset,
        filing_types=list(filing_types),
        include_quant=include_quant
    )
    if result.get("status") == "error":
        raise Exception(result.get("message", "Extraction failed"))
    return result


def validate_and_enrich(ticker: str, financials: dict) -> tuple:
    """Validate extracted data"""
    if not financials or financials.get("status") == "error":
        return financials, None
    try:
        report = _validator.validate_extraction(ticker, financials)
        financials['_validation'] = {
            'status': report['overall_status'],
            'quality_score': report['quality_score'],
            'warnings': report['warnings'][:5],
            'errors': report['errors'][:3]
        }
        return financials, report
    except Exception as e:
        print(f"[WARN] Validation failed: {e}")
        return financials, None


# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="ATLAS Financial Intelligence",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================
# INJECT CSS
# ==========================================
# BACKGROUND IMAGE: Set to True and provide path when ready
# bg_image_path = os.path.join(os.path.dirname(__file__), "YOUR_BACKGROUND.png")
# inject_all_css(enable_background=True, bg_image_path=bg_image_path)
inject_all_css(enable_background=False)
inject_theme_css()
init_ui_components()

if MOBILE_RESPONSIVE:
    inject_responsive_css()
    inject_viewport_meta()

# ==========================================
# SHOW API WARNINGS (if any)
# ==========================================
if API_WARNINGS:
    for warning in API_WARNINGS:
        st.sidebar.warning(warning)

# ==========================================
# SESSION STATE INITIALIZATION
# ==========================================
if 'ticker' not in st.session_state:
    st.session_state.ticker = None
if 'financials' not in st.session_state:
    st.session_state.financials = None
if 'dcf_results' not in st.session_state:
    st.session_state.dcf_results = None
if 'current_theme' not in st.session_state:
    st.session_state.current_theme = 'atlas_dark'
# Additional session states for features
if 'live_scenario' not in st.session_state:
    st.session_state.live_scenario = None
if 'custom_assumptions' not in st.session_state:
    st.session_state.custom_assumptions = {}
if 'comparison_tickers' not in st.session_state:
    st.session_state.comparison_tickers = []
if 'monte_carlo_results' not in st.session_state:
    st.session_state.monte_carlo_results = None
if 'peer_discovery_result' not in st.session_state:
    st.session_state.peer_discovery_result = None
if 'peer_comparison_data' not in st.session_state:
    st.session_state.peer_comparison_data = None
if 'comparison_data' not in st.session_state:
    st.session_state.comparison_data = {}

if AUTH_ACTIVE:
    init_auth_state()

# ==========================================
# SIDEBAR
# ==========================================
with st.sidebar:
    # Header with close hint
    st.markdown("**ATLAS Control Panel**")
    st.caption("Click arrow at top-left of page to collapse")
    st.markdown("---")
    
    # Theme selector
    selected_theme = render_theme_selector(position='sidebar', key='main_theme_selector')
    if selected_theme != st.session_state.get('current_theme'):
        st.session_state.current_theme = selected_theme
        st.rerun()
    
    st.markdown("---")
    st.markdown("### Stock Selection")
    
    # S&P 500 dropdown
    selected_display = st.selectbox(
        "S&P 500 Quick Select",
        options=[""] + SP500_DISPLAY,
        index=0,
        key="sp500_select"
    )
    
    if selected_display:
        ticker = extract_ticker(selected_display)
        if ticker and ticker != st.session_state.ticker:
            st.session_state.ticker = ticker
            st.session_state.financials = None
            st.session_state.dcf_results = None
            st.rerun()
    
    # Manual ticker input
    st.markdown("**Or enter any ticker:**")
    manual_ticker = st.text_input("Ticker Symbol", key="manual_ticker_input").upper().strip()
    
    if st.button("Analyze", type="primary", use_container_width=True, key="analyze_btn"):
        if manual_ticker:
            st.session_state.ticker = manual_ticker
            st.session_state.financials = None
            st.session_state.dcf_results = None
            st.rerun()
        else:
            st.warning("Please enter a ticker symbol")
    
    # Show current ticker
    if st.session_state.ticker:
        st.markdown("---")
        st.markdown(f"**Currently Analyzing:** `{st.session_state.ticker}`")

# ==========================================
# MAIN CONTENT
# ==========================================
if not st.session_state.ticker:
    # Landing page
    render_landing_page(cached_extract_financials, validate_and_enrich, SP500_DISPLAY, extract_ticker)
else:
    # Extract data if needed
    if st.session_state.financials is None:
        with st.spinner(f"Extracting financial data for {st.session_state.ticker}..."):
            try:
                financials = cached_extract_financials(st.session_state.ticker)
                financials, _ = validate_and_enrich(st.session_state.ticker, financials)
                st.session_state.financials = financials
            except Exception as e:
                st.error(f"Failed to extract data: {e}")
                st.stop()
    
    # Check if we have data
    if not st.session_state.financials or st.session_state.financials.get("status") == "error":
        st.error("Failed to load financial data. Please try another ticker.")
        st.stop()
    
    # Check for quant data
    has_quant = "quant_analysis" in st.session_state.financials
    
    # ==========================================
    # APP HEADER
    # ==========================================
    st.markdown('<h1 class="main-header" style="text-align: center; color: #f0f4f8; font-size: 1.8rem; margin-bottom: 0.5rem;">ATLAS FINANCIAL INTELLIGENCE</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #94a3b8; font-size: 1rem; margin-top: -0.5rem; margin-bottom: 1rem;">Professional Financial Analysis Engine</p>', unsafe_allow_html=True)
    
    # ==========================================
    # PERSISTENT TICKER DISPLAY
    # ==========================================
    company_name = st.session_state.financials.get('company_name', 'N/A')
    current_price = st.session_state.financials.get('market_data', {}).get('current_price', 'N/A')
    render_ticker_display(st.session_state.ticker, company_name, current_price)
    
    # ==========================================
    # MAIN TABS (8-Tab Professional Structure)
    # ==========================================
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
        "Dashboard",           # 1 - Quick overview
        "Data",                # 2 - Financial statements
        "Deep Dive",           # 3 - Analysis
        "Valuation",           # 4 - DCF + Alpha Signals
        "Risk & Ownership",    # 5 - Forensic + Governance
        "Market Intelligence", # 6 - Technical + Options
        "News",                # 7 - News & Sentiment
        "IC Memo"              # 8 - Investment Summary
    ])
    
    # TAB 1: DASHBOARD
    with tab1:
        render_dashboard_tab(st.session_state.ticker, st.session_state.financials, visualizer)
    
    # TAB 2: DATA (Modular)
    with tab2:
        render_data_tab(st.session_state.ticker, st.session_state.financials, extractor)
    
    # TAB 3: DEEP DIVE
    with tab3:
        render_analysis_tab(st.session_state.ticker, st.session_state.financials)
    
    # TAB 4: VALUATION (Modular - includes Insider/Ownership/Earnings)
    with tab4:
        render_valuation_tab(st.session_state.ticker, st.session_state.financials, visualizer)
    
    # TAB 5: RISK & OWNERSHIP (Modular)
    with tab5:
        render_risk_tab(st.session_state.ticker, st.session_state.financials)
    
    # TAB 6: MARKET INTELLIGENCE (Modular)
    with tab6:
        render_market_tab(st.session_state.ticker, st.session_state.financials, extractor, visualizer, has_quant)
    
    # TAB 7: NEWS (Modular)
    with tab7:
        render_news_tab(st.session_state.ticker)
    
    # TAB 8: IC MEMO
    with tab8:
        render_investment_summary_tab(st.session_state.financials)

