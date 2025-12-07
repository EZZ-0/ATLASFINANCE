"""
ATLAS FINANCIAL INTELLIGENCE - STREAMLIT APP
=============================================
Multi-tab interactive financial analysis tool.

Tabs:
1. Extract - Pull financial data from SEC/Yahoo
2. Model - 3-Scenario DCF Valuation
3. Visualize - Interactive charts and dashboards
4. Compare - Multi-company peer analysis
"""

import streamlit as st
import pandas as pd
import numpy as np
import os
import base64
from datetime import datetime
import time
import hashlib

# ==========================================
# BACKGROUND IMAGE TOGGLE (Easy to undo)
# ==========================================
# Set to False to disable the custom background image
ENABLE_BACKGROUND_IMAGE = True

# Import our modules
from usa_backend import USAFinancialExtractor
from validation_engine import DataValidator
from app_css import inject_all_css, get_search_button_css
from app_landing import render_landing_page, render_ticker_display, render_no_ticker_placeholder
from app_themes import inject_theme_css, render_theme_selector, get_current_theme

# Import flip cards (MILESTONE-008)
try:
    from flip_cards import render_flip_card, render_valuation_metrics, render_alpha_metrics
    FLIP_CARDS_ENABLED = True
except ImportError:
    FLIP_CARDS_ENABLED = False

# Initialize validator (singleton pattern)
_validator = DataValidator()

def validate_and_enrich(ticker: str, financials: dict) -> tuple:
    """
    Validate extracted data and return (financials, validation_report).
    Adds validation metadata to financials dict.
    """
    if not financials or financials.get("status") == "error":
        return financials, None
    
    try:
        report = _validator.validate_extraction(ticker, financials)
        # Attach validation metadata
        financials['_validation'] = {
            'status': report['overall_status'],
            'quality_score': report['quality_score'],
            'warnings': report['warnings'][:5],  # Top 5 warnings
            'errors': report['errors'][:3]  # Top 3 errors
        }
        return financials, report
    except Exception as e:
        # Don't block extraction if validation fails
        print(f"[WARN] Validation failed: {e}")
        return financials, None

# ==========================================
# CACHING - Prevent Rate Limiting
# ==========================================
# Cache financial data for 1 hour to avoid hitting Yahoo Finance repeatedly
@st.cache_data(ttl=3600, show_spinner=False)
def cached_extract_financials(
    ticker: str, 
    source: str = "auto",
    fiscal_year_offset: int = 0,
    filing_types: tuple = ("10-K", "10-Q"),  # Must be tuple for caching (hashable)
    include_quant: bool = True
) -> dict:
    """
    Cached wrapper for financial extraction.
    TTL=3600 seconds (1 hour) - data is refreshed hourly.
    This prevents rate limiting on Streamlit Cloud.
    
    Note: filing_types must be tuple (not list) for Streamlit caching.
    IMPORTANT: Error results raise exceptions (not cached).
    """
    extractor = USAFinancialExtractor()
    result = extractor.extract_financials(
        ticker, 
        source=source,
        fiscal_year_offset=fiscal_year_offset,
        filing_types=list(filing_types),  # Convert back to list for the backend
        include_quant=include_quant
    )
    
    # DON'T cache error results - raise exception instead
    # This ensures rate limit errors aren't cached for 1 hour
    if result.get("status") == "error":
        error_msg = result.get("message", "Extraction failed")
        raise Exception(error_msg)
    
    return result

def get_cache_key(ticker: str) -> str:
    """Generate a cache key for tracking"""
    return hashlib.md5(f"{ticker}_{datetime.now().strftime('%Y%m%d%H')}".encode()).hexdigest()[:8]

def clear_ticker_cache(ticker: str):
    """Clear cache for a specific ticker (for force refresh)"""
    cached_extract_financials.clear()
from dcf_modeling import DCFModel
from visualization import FinancialVisualizer
from format_helpers import format_dataframe_for_display, format_dataframe_for_csv, prepare_table_for_display, external_link, format_large_number, format_change, format_financial_number
from excel_export import export_financials_to_excel
from sp500_tickers import SP500_TICKERS, SP500_DISPLAY, extract_ticker

# Phase 3 Modules - Financial Deep Dive
from earnings_analysis import analyze_earnings_history
from dividend_analysis import analyze_dividends
from valuation_multiples import analyze_valuation_multiples
from cashflow_analysis import analyze_cashflow

# Phase 4 Modules - Advanced Analysis
from balance_sheet_health import analyze_balance_sheet_health
from management_effectiveness import analyze_management_effectiveness
from growth_quality import analyze_growth_quality

# Refactored Tab Modules (Phase 6C Refactoring)
from analysis_tab import render_analysis_tab
from governance_tab import render_governance_tab
from compare_tab import render_compare_tab
from quant_tab import render_quant_tab

# Enhanced UI Components (Phase 2B)
from enhanced_tables import enhanced_dataframe, create_sortable_table
from investment_summary import render_investment_summary_tab
from dashboard_tab import render_dashboard_tab
from data_tab_metrics import (
    render_income_metrics, render_balance_metrics, render_cashflow_metrics,
    render_price_metrics, render_ratio_metrics, render_growth_metrics,
    FLIP_CARDS_AVAILABLE as DATA_FLIP_AVAILABLE
)

# Advanced UI Components (Phase 7 - UI/UX Enhancement)
from ui_components import (
    smart_dataframe, render_gauge, render_radar_chart, 
    render_styled_header, render_data_explorer, init_ui_components,
    show_library_status, DARK_THEME
)

# ==========================================
# BOOTSTRAP ICON HELPER
# ==========================================

def icon(name, size="1em", color=None):
    """Render a Bootstrap Icon"""
    style = f"font-size: {size};"
    if color:
        style += f" color: {color};"
    return f'<i class="bi bi-{name}" style="{style}"></i>'

def inline_ai_explain(metric_name, metric_value, context_data=None):
    """
    Create an inline AI explanation button for a metric
    Returns a small clickable icon that shows AI explanation in a popover
    """
    explanation_key = f"explain_{metric_name}_{metric_value}".replace(" ", "_").replace("$", "").replace(".", "")
    
    # Create a unique key for this explanation
    if f"show_{explanation_key}" not in st.session_state:
        st.session_state[f"show_{explanation_key}"] = False
    
    # Small info icon button
    if st.button("ℹ️", key=f"btn_{explanation_key}", help=f"AI explanation for {metric_name}"):
        st.session_state[f"show_{explanation_key}"] = not st.session_state[f"show_{explanation_key}"]
    
    # Show explanation if toggled
    if st.session_state[f"show_{explanation_key}"]:
        with st.spinner("Getting AI explanation..."):
            try:
                from financial_ai import FinancialAI
                ai_advisor = FinancialAI(tier="free")
                
                # Build context
                if context_data is None:
                    context_data = {}
                
                # Ask AI to explain this specific metric
                question = f"Explain what '{metric_name}' means and why the value of {metric_value} is significant for this company."
                result = ai_advisor.ask(question, context_data, context_type='explanation')
                
                st.info(f"**AI Insight:** {result['response'][:300]}...")  # Show first 300 chars
                st.caption(f"Model: {result['model_used']} | Confidence: {result['confidence']}%")
            except Exception as e:
                st.error(f"Could not get AI explanation: {str(e)}")

# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="Atlas Financial Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"  # Auto-expand on load (better UX)
)

# Performance optimization: Disable initial query params check
if 'initialized' not in st.session_state:
    st.session_state.initialized = True

# ==========================================
# INJECT ALL CSS (from app_css.py)
# ==========================================
bg_image_path = os.path.join(os.path.dirname(__file__), "Background_1.png")
inject_all_css(enable_background=ENABLE_BACKGROUND_IMAGE, bg_image_path=bg_image_path)

# NOTE: Main CSS moved to app_css.py (~500 lines saved)
# To modify styling, edit app_css.py

# ==========================================
# INJECT THEME CSS (from app_themes.py)
# ==========================================
# Theme selection handled in sidebar, CSS applied here
# This overrides default colors with selected theme
if 'current_theme' not in st.session_state:
    st.session_state.current_theme = 'atlas_dark'
inject_theme_css(st.session_state.current_theme)

# ==========================================
# [REMOVED] Legacy CSS block was here (lines 213-770)
# All CSS now loaded from app_css.py via inject_all_css()
# ==========================================

# [LEGACY CSS REMOVED - Now loaded from app_css.py via inject_all_css()]

# ==========================================
# SESSION STATE INITIALIZATION
# ==========================================

# Initialize session state variables if they don't exist
if "financials" not in st.session_state:
    st.session_state.financials = None
if "ticker" not in st.session_state:
    st.session_state.ticker = ""
if "dcf_results" not in st.session_state:
    st.session_state.dcf_results = None
if "use_new_model_tab" not in st.session_state:
    st.session_state.use_new_model_tab = False
if "comparison_data" not in st.session_state:
    st.session_state.comparison_data = {}
if "validation_report" not in st.session_state:
    st.session_state.validation_report = None

# ==========================================
# INITIALIZE BACKEND
# ==========================================

# Initialize the financial data extractor and visualizer (cached for performance)
@st.cache_resource
def get_extractor():
    """Cached extractor instance - expensive to create"""
    return USAFinancialExtractor()

@st.cache_resource  
def get_visualizer():
    """Cached visualizer instance - reused across reruns"""
    return FinancialVisualizer()

extractor = get_extractor()
visualizer = get_visualizer()

# ==========================================
# SIDEBAR - REDESIGNED FOR PROFESSIONAL UX
# ==========================================


with st.sidebar:
    # Header
    st.markdown(f"""
    <div style='text-align: center; padding: 1rem 0; border-bottom: 2px solid rgba(59, 130, 246, 0.25); margin-bottom: 1.5rem;'>
        <h2 style='color: #3b82f6; margin: 0;'>
            <i class="bi bi-sliders" style="margin-right: 0.5rem;"></i>Control Panel
        </h2>
        <p style='color: #94a3b8; font-size: 0.85rem; margin: 0.3rem 0 0 0;'>Configure & Extract Financial Data</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Theme Selector (MILESTONE-006)
    selected_theme = render_theme_selector(position='sidebar', key='main_theme_selector')
    if selected_theme != st.session_state.get('current_theme'):
        st.session_state.current_theme = selected_theme
        st.rerun()  # Apply theme immediately
    
    st.write("")  # Spacing
    
    # Ticker input (FULL WIDTH - NO COLUMNS)
    # Sync with landing page if user entered ticker there
    default_ticker = st.session_state.get('sidebar_landing_sync', '')
    
    ticker_input = st.text_input(
        "Enter Ticker Symbol",
        value=default_ticker,
        placeholder="Type ticker (e.g., AAPL, MSFT, TSLA)",
        help="Enter any USA publicly traded company ticker symbol",
        label_visibility="visible"
    ).upper().strip()
    
    st.caption("**Or select from S&P 500:**")
    
    # S&P 500 Dropdown (FULL WIDTH)
    sp500_pick = st.selectbox(
        "S&P 500 Companies",
        options=SP500_DISPLAY,
        label_visibility="collapsed",
        help="503 S&P 500 companies (alphabetical by company name)"
    )
    if sp500_pick != "--":
        ticker_input = extract_ticker(sp500_pick)
    
    # Data Configuration (minimal divider)
    st.write("")  # Just spacing
    
    # Data source selection
    data_source = st.radio(
        "Data Source",
        options=["Auto (SEC → Yahoo)", "SEC API Only", "Yahoo Finance Only"],
        help="Auto mode tries SEC first, falls back to Yahoo if needed",
        horizontal=False
    )
    
    source_map = {
        "Auto (SEC → Yahoo)": "auto",
        "SEC API Only": "sec",
        "Yahoo Finance Only": "yfinance"
    }
    
    # Filing type selection
    filing_option = st.selectbox(
        "Filing Type",
        options=[
            "10-K (Annual Reports)",
            "10-Q (Quarterly Reports)",
            "10-K + 10-Q (Both)",
            "S-1 (IPO Filings)"
        ],
        help="10-K = Audited annual reports\n10-Q = Unaudited quarterly reports\nS-1 = Pre-IPO registration"
    )
    
    filing_map = {
        "10-K (Annual Reports)": ["10-K"],
        "10-Q (Quarterly Reports)": ["10-Q"],
        "10-K + 10-Q (Both)": ["10-K", "10-Q"],
        "S-1 (IPO Filings)": ["S-1"]
    }
    filing_types = filing_map[filing_option]
    
    # Advanced Options
    st.write("")  # Just spacing
    with st.expander("⚙️ Advanced Options", expanded=False):
        # Quant analysis toggle
        include_quant = st.checkbox(
            "Include Quant Analysis (Fama-French)",
            value=True,
            help="Run advanced quantitative analysis with historical pricing and Fama-French 3-Factor regression"
        )
        
        # Force refresh toggle (bypass cache)
        force_refresh = st.checkbox(
            "Force Refresh (bypass cache)",
            value=False,
            help="Clear cached data and fetch fresh from source. Use sparingly to avoid rate limits."
        )
    
    # Extract button with theme-aware gradient
    st.write("")  # Just spacing
    
    # Dynamic button styling based on selected theme (using new theme system)
    from config.themes import get_theme
    theme = get_theme(st.session_state.get('current_theme', 'atlas_dark'))
    
    st.markdown(f"""
    <style>
    div.stButton > button[kind="primary"] {{
        background: {theme['gradient']} !important;
        color: white !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
        letter-spacing: 1px !important;
        padding: 0.75rem 2rem !important;
        border: none !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3) !important;
        transition: all 0.3s ease !important;
        text-transform: uppercase !important;
    }}
    div.stButton > button[kind="primary"]:hover {{
        box-shadow: 0 6px 25px rgba(0, 0, 0, 0.5) !important;
        transform: translateY(-3px) scale(1.02) !important;
    }}
    </style>
    """, unsafe_allow_html=True)
    
    if st.button("🔍 SEARCH", type="primary", use_container_width=True):
        if ticker_input:
            # Clear cache if force refresh is enabled
            if force_refresh:
                clear_ticker_cache(ticker_input)
                st.toast("Cache cleared - fetching fresh data")
            
            cache_status = "fetching fresh data" if force_refresh else "cached for 1 hour"
            with st.spinner(f"Extracting {ticker_input}... ({cache_status})"):
                try:
                    # Use cached extraction to prevent rate limiting
                    result = cached_extract_financials(
                        ticker_input, 
                        source=source_map[data_source],
                        filing_types=tuple(filing_types),  # Convert to tuple for caching
                        include_quant=include_quant
                    )
                    
                    if "status" in result and result["status"] == "error":
                        st.error(f"{result['message']}")
                    else:
                        # Validate extracted data
                        validated_result, validation_report = validate_and_enrich(ticker_input, result)
                        st.session_state.financials = validated_result
                        st.session_state.ticker = ticker_input
                        st.session_state.validation_report = validation_report
                        st.session_state.dcf_results = None  # Reset DCF when new data loaded
                        st.session_state.data_extracted = True  # Enable tabs view
                        
                        # Auto-collapse sidebar - DIRECT APPROACH
                        st.markdown("""
                        <script>
                            setTimeout(function() {
                                // Find ALL buttons and click the one with SVG arrow (collapse button)
                                const allButtons = window.parent.document.querySelectorAll('button');
                                for (let btn of allButtons) {
                                    // The collapse button has specific SVG or is in sidebar header
                                    const svg = btn.querySelector('svg');
                                    if (svg || btn.getAttribute('kind') === 'header') {
                                        // Check if it's the sidebar toggle by looking at parent
                                        const rect = btn.getBoundingClientRect();
                                        if (rect.left < 500) {  // Left side of screen = sidebar area
                                            btn.click();
                                            console.log('Sidebar collapsed');
                                            break;
                                        }
                                    }
                                }
                            }, 500);
                        </script>
                        """, unsafe_allow_html=True)
                        
                        success_msg = f"Data extracted in {result.get('extraction_time', 'N/A')}"
                        if include_quant and "quant_analysis" in result:
                            success_msg += " (with quant analysis)"
                        st.success(success_msg)
                        st.rerun()
                except Exception as e:
                    error_str = str(e).lower()
                    if 'rate limit' in error_str or 'too many requests' in error_str or '429' in error_str:
                        st.error("⏳ Rate Limited by Yahoo Finance")
                        st.info("""
                        **What happened:** Too many requests were made to Yahoo Finance.
                        
                        **Solutions:**
                        1. **Wait 1-2 minutes** and try again
                        2. **Try a different ticker** - it might be cached
                        3. **Check back later** - data is cached for 1 hour once loaded
                        
                        *This happens on Streamlit Cloud due to shared IP addresses.*
                        """)
                    else:
                        st.error(f"Extraction failed: {e}")
        else:
            st.warning("Please enter a ticker symbol")
    
    # Current status section (clean, no boxes)
    st.write("")  # Just spacing
    st.write("")  # Extra spacing
    
    if st.session_state.financials:
        company_name = st.session_state.financials.get('company_name', 'N/A')
        st.success(f"✓ Loaded: **{st.session_state.ticker}**")
        st.caption(f"Company: {company_name}")
        
        # Data Quality Indicator
        validation = st.session_state.financials.get('_validation', {})
        if validation:
            status = validation.get('status', 'UNKNOWN')
            score = validation.get('quality_score', 0)
            if status == 'PASS':
                st.caption(f"Data Quality: ✓ {score}/100")
            elif status == 'WARN':
                st.caption(f"Data Quality: ⚠️ {score}/100")
                warnings = validation.get('warnings', [])
                if warnings:
                    with st.expander("View warnings", expanded=False):
                        for w in warnings[:3]:
                            st.caption(f"• {w}")
            elif status == 'FAIL':
                st.caption(f"Data Quality: ⛔ {score}/100")
                st.warning("Some data may be inaccurate")
        
        if st.button("🗑️ Clear Data", use_container_width=True):
            st.session_state.financials = None
            st.session_state.dcf_results = None
            st.session_state.ticker = ""
            st.session_state.data_extracted = False  # Return to landing page
            st.rerun()
        
    else:
        st.info("No data loaded yet")
        st.caption("Enter a ticker above and click SEARCH")
    
    # About section
    st.write("")  # Just spacing
    st.write("")  # Extra spacing
    st.caption("**Atlas Financial Intelligence v2.2**")
    st.caption("Built with Streamlit, yfinance, SEC EDGAR API")
    st.caption("© 2025 | Professional-Grade Analysis")


# ==========================================
# TAB RENDER FUNCTIONS (Future-Proof Architecture)
# ==========================================
# Each tab is now a function that can internally have sub-tabs
# This allows for 2-layer structure: Main Tabs → Sub-Tabs
# Without breaking existing code structure

def render_model_tab_EXAMPLE():
    """
    Model tab with 7 sub-tabs for comprehensive valuation analysis
    2-Layer Structure: Model → [DCF | Reverse-DCF | Analyst | Earnings | Dividends | Valuation | Cash Flow]
    """
    st.markdown(f"## {icon('cash-coin', '1.5em')} Valuation & Analysis", unsafe_allow_html=True)
    
    # Sub-tabs for different analysis types (2nd layer)
    dcf_tab, reverse_tab, analyst_tab, insider_tab, ownership_tab, earnings_tab, dividend_tab, valuation_tab, cashflow_tab = st.tabs([
        "DCF",
        "Reverse-DCF", 
        "Analyst",
        "Insider",
        "Ownership",
        "Earnings",
        "Dividends",
        "Valuation",
        "Cash Flow"
    ])
    
    with dcf_tab:
        st.markdown("### 💰 3-Scenario DCF", unsafe_allow_html=True)
        
        if st.button("▶️ Run 3-Scenario DCF Analysis", type="primary", use_container_width=True, key="dcf_button_new"):
            with st.spinner("Running DCF valuation..."):
                try:
                    model = DCFModel(st.session_state.financials)
                    results = model.run_all_scenarios()
                    st.session_state.dcf_results = results
                    st.success("DCF analysis complete!")
                except Exception as e:
                    st.error(f"DCF Error: {e}")
        
        # Display results if available
        if st.session_state.dcf_results:
            results = st.session_state.dcf_results
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                conservative = results["conservative"]["value_per_share"]
                st.metric(
                    "Conservative",
                    f"${conservative:.2f}",
                    help="Bear case scenario with lower growth and higher discount rate"
                )
            
            with col2:
                base = results["base"]["value_per_share"]
                st.metric(
                    "Base Case",
                    f"${base:.2f}",
                    help="Most likely scenario using historical averages"
                )
            
            with col3:
                aggressive = results["aggressive"]["value_per_share"]
                st.metric(
                    "Aggressive",
                    f"${aggressive:.2f}",
                    help="Bull case with higher growth and lower discount rate"
                )
            
            with col4:
                weighted = results["weighted_average"]
                st.metric(
                    "Weighted Avg",
                    f"${weighted:.2f}",
                    help="40% Base + 30% Conservative + 30% Aggressive"
                )
    
    with reverse_tab:
        st.markdown(f"### {icon('arrow-repeat', '1.2em')} Market-Implied Expectations", unsafe_allow_html=True)
        st.info("ℹ This analysis reverse-engineers the DCF model to determine what growth rate and margins the current market price implies.")
        
        # Reverse-DCF content would go here
        st.caption("Full implementation in main Model tab")
    
    with analyst_tab:
        st.markdown(f"### {icon('person-badge', '1.2em')} Wall Street Consensus", unsafe_allow_html=True)
        st.info("ℹ Consensus recommendations and price targets from Wall Street analysts.")
        
        # Analyst ratings content would go here
        st.caption("Full implementation in main Model tab")
    
    with insider_tab:
        st.markdown(f"### {icon('person-check', '1.2em')} Insider Transactions", unsafe_allow_html=True)
        st.info("ℹ Track insider buying and selling activity - a key signal for stock analysis.")
        
        try:
            from insider_transactions import get_insider_summary, create_insider_gauge, create_insider_activity_chart, create_transaction_table
            
            with st.spinner("Analyzing insider activity..."):
                insider_data = get_insider_summary(st.session_state.ticker, days=90)
                
                if insider_data:
                    # Summary metrics row - use flip cards if available
                    st.caption("Click any metric for insight")
                    icol1, icol2, icol3, icol4 = st.columns(4)
                    
                    if FLIP_CARDS_ENABLED:
                        with icol1:
                            render_flip_card("Insider_Sentiment", insider_data.sentiment_score, "Sentiment Score")
                        with icol2:
                            net_val = insider_data.net_value / 1_000_000 if abs(insider_data.net_value) >= 1_000_000 else insider_data.net_value
                            render_flip_card("market_cap", net_val, "Net Value ($M)" if abs(insider_data.net_value) >= 1_000_000 else "Net Value")
                        with icol3:
                            render_flip_card("Insider_Sentiment", 50 if insider_data.sentiment_label == "Bullish" else -50 if insider_data.sentiment_label == "Bearish" else 0, insider_data.sentiment_label)
                        with icol4:
                            cluster_val = insider_data.cluster_buyers_count if insider_data.is_cluster_buying else 0
                            render_flip_card("Insider_Sentiment", cluster_val * 20, "Cluster Buying" if insider_data.is_cluster_buying else "No Cluster")
                    else:
                        with icol1:
                            st.metric("Insider Sentiment", f"{insider_data.sentiment_score:+.0f}")
                        with icol2:
                            net_str = f"${insider_data.net_value/1_000_000:.1f}M" if abs(insider_data.net_value) >= 1_000_000 else f"${insider_data.net_value:,.0f}"
                            st.metric("Net Value", net_str)
                        with icol3:
                            st.metric("Sentiment", insider_data.sentiment_label)
                        with icol4:
                            if insider_data.is_cluster_buying:
                                st.metric("Cluster Buying", f"{insider_data.cluster_buyers_count} insiders")
                            else:
                                st.metric("Cluster Status", "Not Detected")
                    
                    st.markdown("---")
                    
                    # Activity breakdown
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Buy Activity:**")
                        st.write(f"• Transactions: {insider_data.buy_transactions}")
                        st.write(f"• Total Value: ${insider_data.total_buy_value:,.0f}")
                        st.write(f"• Shares Bought: {insider_data.total_shares_bought:,}")
                        if insider_data.notable_buyers:
                            st.success(f"Notable: {', '.join(insider_data.notable_buyers[:3])}")
                    
                    with col2:
                        st.markdown("**Sell Activity:**")
                        st.write(f"• Transactions: {insider_data.sell_transactions}")
                        st.write(f"• Total Value: ${insider_data.total_sell_value:,.0f}")
                        st.write(f"• Shares Sold: {insider_data.total_shares_sold:,}")
                        if insider_data.notable_sellers:
                            st.warning(f"Notable: {', '.join(insider_data.notable_sellers[:3])}")
                    
                    # Charts in expander
                    with st.expander("View Insider Charts", expanded=False):
                        chart_col1, chart_col2 = st.columns(2)
                        
                        with chart_col1:
                            st.plotly_chart(create_insider_gauge(insider_data.sentiment_score), use_container_width=True)
                        
                        with chart_col2:
                            st.plotly_chart(create_insider_activity_chart(insider_data), use_container_width=True)
                    
                    # Transaction table
                    if insider_data.recent_transactions:
                        with st.expander("Recent Transactions", expanded=False):
                            df = create_transaction_table(insider_data.recent_transactions)
                            st.dataframe(df, hide_index=True, use_container_width=True)
                else:
                    st.info("No insider transaction data available for this ticker.")
        except ImportError:
            st.caption("Insider tracking module loading...")
        except Exception as ins_e:
            st.error(f"Error loading insider data: {str(ins_e)}")
    
    with ownership_tab:
        st.markdown(f"### {icon('building', '1.2em')} Institutional Ownership", unsafe_allow_html=True)
        st.info("ℹ Track institutional and insider ownership - smart money signals.")
        
        try:
            from institutional_ownership import get_ownership_summary, create_ownership_pie, create_accumulation_gauge
            
            with st.spinner("Analyzing institutional ownership..."):
                ownership_data = get_ownership_summary(st.session_state.ticker)
                
                if ownership_data:
                    # Summary metrics row
                    ocol1, ocol2, ocol3, ocol4 = st.columns(4)
                    
                    if FLIP_CARDS_ENABLED:
                        with ocol1:
                            render_flip_card("ROE", ownership_data.institutional_pct, "Institutional %")
                        with ocol2:
                            render_flip_card("ROE", ownership_data.insider_pct, "Insider %")
                        with ocol3:
                            render_flip_card("ROE", ownership_data.top10_concentration, "Top 10 Conc.")
                        with ocol4:
                            render_flip_card("Institutional_Flow", ownership_data.accumulation_score, ownership_data.sentiment_label)
                    else:
                        with ocol1:
                            st.metric("Institutional", f"{ownership_data.institutional_pct:.1f}%")
                        with ocol2:
                            st.metric("Insider", f"{ownership_data.insider_pct:.1f}%")
                        with ocol3:
                            st.metric("Top 10 Concentration", f"{ownership_data.top10_concentration:.1f}%")
                        with ocol4:
                            st.metric("Signal", ownership_data.sentiment_label)
                    
                    st.markdown("---")
                    
                    # Ownership breakdown
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Ownership Breakdown:**")
                        st.write(f"• Institutional: {ownership_data.institutional_pct:.1f}%")
                        st.write(f"• Insider: {ownership_data.insider_pct:.1f}%")
                        st.write(f"• Retail/Other: {ownership_data.retail_pct:.1f}%")
                        st.write(f"• Total Institutions: {ownership_data.total_institutions}")
                    
                    with col2:
                        st.markdown("**Concentration Analysis:**")
                        st.write(f"• Top 10 Hold: {ownership_data.top10_concentration:.1f}%")
                        concentrated = "Yes - Concentrated" if ownership_data.is_concentrated else "No - Distributed"
                        st.write(f"• Highly Concentrated: {concentrated}")
                        st.write(f"• Accumulation Score: {ownership_data.accumulation_score:+.0f}")
                    
                    # Charts in expander
                    with st.expander("View Ownership Charts", expanded=False):
                        chart_col1, chart_col2 = st.columns(2)
                        
                        with chart_col1:
                            st.plotly_chart(create_ownership_pie(ownership_data), use_container_width=True)
                        
                        with chart_col2:
                            st.plotly_chart(create_accumulation_gauge(ownership_data.accumulation_score), use_container_width=True)
                    
                    # Top holders table
                    if ownership_data.top_holders:
                        with st.expander("Top Institutional Holders", expanded=False):
                            import pandas as pd
                            holders_data = [{
                                'Holder': h.name[:40] + '...' if len(h.name) > 40 else h.name,
                                'Shares': f"{h.shares:,}",
                                'Value': f"${h.value/1_000_000:.1f}M" if h.value >= 1_000_000 else f"${h.value:,.0f}",
                                '% Owned': f"{h.percent_held:.2f}%",
                                'Type': h.holder_type.value
                            } for h in ownership_data.top_holders[:10]]
                            st.dataframe(pd.DataFrame(holders_data), hide_index=True, use_container_width=True)
                else:
                    st.info("No institutional ownership data available for this ticker.")
        except ImportError:
            st.caption("Ownership tracking module loading...")
        except Exception as own_e:
            st.error(f"Error loading ownership data: {str(own_e)}")
    
    with earnings_tab:
        st.markdown(f"### {icon('graph-up-arrow', '1.2em')} Earnings Quality & Trends", unsafe_allow_html=True)
        
        try:
            from earnings_analysis import analyze_earnings_history
            
            with st.spinner("Analyzing earnings history..."):
                earnings_data = analyze_earnings_history(st.session_state.ticker, periods=8)
                
                if earnings_data['status'] == 'success':
                    metrics = earnings_data['metrics']
                    
                    # Summary metrics
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Beat Rate", f"{metrics.get('beat_rate', 0):.1f}%",
                                 help="Percentage of earnings beats")
                    
                    with col2:
                        st.metric("Avg Surprise", f"{metrics.get('avg_surprise_pct', 0):.2f}%",
                                 help="Average earnings surprise magnitude")
                    
                    with col3:
                        st.metric("EPS Momentum", f"{metrics.get('eps_momentum', 0):.1f}%",
                                 help="EPS acceleration/deceleration")
                    
                    with col4:
                        score = metrics.get('earnings_score', 0)
                        rating = metrics.get('earnings_rating', 'N/A')
                        st.metric("Quality Score", f"{score:.0f}/100",
                                 help=f"Rating: {rating}")
                    
                    st.markdown("---")
                    
                    # Detailed breakdown
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Performance:**")
                        st.write(f"• Total Reports: {metrics.get('total_earnings_reports', 0)}")
                        st.write(f"• Beats: {metrics.get('earnings_beats', 0)}")
                        st.write(f"• Misses: {metrics.get('earnings_misses', 0)}")
                        st.write(f"• Consistency: {metrics.get('surprise_consistency', 'N/A')}")
                    
                    with col2:
                        st.markdown("**EPS & Trends:**")
                        trailing_eps = metrics.get('trailing_eps', 0)
                        forward_eps = metrics.get('forward_eps', 0)
                        st.write(f"• **Current EPS (TTM):** ${trailing_eps:.2f}" if trailing_eps else "• Current EPS: N/A")
                        st.write(f"• Forward EPS: ${forward_eps:.2f}" if forward_eps else "• Forward EPS: N/A")
                        st.write(f"• EPS Growth Forecast: {metrics.get('eps_growth_forecast', 0):.1f}%")
                        st.write(f"• EPS Trend: {metrics.get('eps_trend', 'N/A')}")
                        st.write(f"• Quality: {metrics.get('earnings_quality', 'N/A')}")
                    
                    # EARNINGS REVISIONS SECTION (MILESTONE-002)
                    st.markdown("---")
                    st.markdown(f"### {icon('arrow-repeat', '1.1em')} Analyst Estimate Revisions", unsafe_allow_html=True)
                    st.caption("Tracks changes in analyst EPS estimates - a key predictor of stock performance")
                    
                    try:
                        from earnings_revisions import get_earnings_revisions, create_revision_gauge, create_revision_trend_chart
                        
                        revision_data = get_earnings_revisions(st.session_state.ticker)
                        
                        if revision_data:
                            rev_dict = revision_data.to_dict()
                            
                            # Revision metrics row
                            rcol1, rcol2, rcol3, rcol4 = st.columns(4)
                            
                            with rcol1:
                                score = rev_dict['momentum_score']
                                st.metric(
                                    "Revision Momentum",
                                    f"{score:+.0f}",
                                    help="Score from -100 (negative revisions) to +100 (positive revisions)"
                                )
                            
                            with rcol2:
                                st.metric(
                                    "Trend",
                                    rev_dict['trend'],
                                    help="Overall direction of estimate changes"
                                )
                            
                            with rcol3:
                                st.metric(
                                    "Analyst Agreement",
                                    rev_dict['analyst_agreement'],
                                    help="How closely analysts agree on estimates"
                                )
                            
                            with rcol4:
                                if rev_dict['current_year']['growth']:
                                    growth = rev_dict['current_year']['growth'] * 100
                                    st.metric("EPS Growth Est", f"{growth:+.1f}%")
                                else:
                                    st.metric("EPS Growth Est", "N/A")
                            
                            # Revision gauge chart
                            with st.expander("View Revision Charts", expanded=False):
                                chart_col1, chart_col2 = st.columns(2)
                                
                                with chart_col1:
                                    st.plotly_chart(create_revision_gauge(score), use_container_width=True)
                                
                                with chart_col2:
                                    st.plotly_chart(
                                        create_revision_trend_chart(rev_dict['revisions']),
                                        use_container_width=True
                                    )
                        else:
                            st.info("Revision data not available for this ticker")
                    except ImportError:
                        st.caption("Revision tracking module loading...")
                    except Exception as rev_e:
                        st.caption(f"Revisions: {str(rev_e)}")
                    
                else:
                    st.warning(earnings_data.get('message', 'No earnings data available'))
        except Exception as e:
            st.error(f"Error analyzing earnings: {str(e)}")
    
    with dividend_tab:
        st.markdown(f"### {icon('cash-coin', '1.2em')} Dividend Analysis", unsafe_allow_html=True)
        
        try:
            from dividend_analysis import analyze_dividends
            
            with st.spinner("Analyzing dividends..."):
                div_data = analyze_dividends(st.session_state.ticker)
                
                if div_data['status'] == 'success':
                    metrics = div_data['metrics']
                    
                    # Current metrics
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Annual Dividend", f"${metrics.get('annual_dividend', 0):.2f}")
                    
                    with col2:
                        st.metric("Dividend Yield", f"{metrics.get('dividend_yield', 0):.2f}%")
                    
                    with col3:
                        st.metric("Payout Ratio", f"{metrics.get('payout_ratio', 0):.1f}%")
                    
                    with col4:
                        score = metrics.get('dividend_score', 0)
                        st.metric("Score", f"{score:.0f}/100")
                    
                    st.markdown("---")
                    
                    # History & Status
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**History & Status:**")
                        st.write(f"• Consecutive Years: {metrics.get('consecutive_years', 0)}")
                        st.write(f"• Status: {metrics.get('dividend_status', 'N/A')}")
                        st.write(f"• Tier: {metrics.get('status_tier', 'N/A')}")
                        st.write(f"• Sustainability: {metrics.get('sustainability', 'N/A')}")
                    
                    with col2:
                        st.markdown("**Growth Rates:**")
                        st.write(f"• 1-Year: {metrics.get('dividend_growth_1y', 'N/A')}%")
                        st.write(f"• 3-Year CAGR: {metrics.get('dividend_cagr_3y', 'N/A')}%")
                        st.write(f"• 5-Year CAGR: {metrics.get('dividend_cagr_5y', 'N/A')}%")
                        st.write(f"• 10-Year CAGR: {metrics.get('dividend_cagr_10y', 'N/A')}%")
                
                elif div_data['status'] == 'no_dividend':
                    st.info("ℹ This company does not currently pay dividends")
                else:
                    st.warning(div_data.get('message', 'No dividend data available'))
        except Exception as e:
            st.error(f"Error analyzing dividends: {str(e)}")
    
    with valuation_tab:
        st.markdown(f"### {icon('bar-chart-line', '1.2em')} Valuation Multiples", unsafe_allow_html=True)
        
        try:
            from valuation_multiples import analyze_valuation_multiples
            
            with st.spinner("Calculating valuation multiples..."):
                val_data = analyze_valuation_multiples(st.session_state.ticker)
                
                if val_data['status'] == 'success':
                    metrics = val_data['metrics']
                    
                    st.caption("Click any metric to see formula & insight")
                    
                    # P/E Ratios - Use flip cards if available
                    st.markdown("**P/E Ratios:**")
                    col1, col2, col3 = st.columns(3)
                    
                    if FLIP_CARDS_ENABLED:
                        with col1:
                            render_flip_card("PE_Ratio", metrics.get('pe_trailing'), "Trailing P/E")
                        with col2:
                            render_flip_card("PE_Ratio", metrics.get('pe_forward'), "Forward P/E")
                        with col3:
                            render_flip_card("PE_Ratio", metrics.get('peg_ratio'), "PEG Ratio")
                    else:
                        with col1:
                            st.metric("Trailing P/E", f"{metrics.get('pe_trailing', 'N/A')}")
                        with col2:
                            st.metric("Forward P/E", f"{metrics.get('pe_forward', 'N/A')}")
                        with col3:
                            st.metric("PEG Ratio", f"{metrics.get('peg_ratio', 'N/A')}")
                    
                    st.markdown("---")
                    
                    # Enterprise Value Ratios
                    st.markdown("**Enterprise Value Ratios:**")
                    col1, col2, col3 = st.columns(3)
                    
                    if FLIP_CARDS_ENABLED:
                        with col1:
                            render_flip_card("EV_EBITDA", metrics.get('ev_to_ebitda'), "EV/EBITDA")
                        with col2:
                            render_flip_card("PS_Ratio", metrics.get('ev_to_revenue'), "EV/Revenue")
                        with col3:
                            render_flip_card("EV_EBITDA", metrics.get('ev_to_ebit'), "EV/EBIT")
                    else:
                        with col1:
                            st.metric("EV/EBITDA", f"{metrics.get('ev_to_ebitda', 'N/A')}")
                        with col2:
                            st.metric("EV/Revenue", f"{metrics.get('ev_to_revenue', 'N/A'):.2f}" if metrics.get('ev_to_revenue') else 'N/A')
                        with col3:
                            st.metric("EV/EBIT", f"{metrics.get('ev_to_ebit', 'N/A'):.2f}" if metrics.get('ev_to_ebit') else 'N/A')
                    
                    st.markdown("---")
                    
                    # Price Ratios
                    st.markdown("**Price Ratios:**")
                    col1, col2, col3 = st.columns(3)
                    
                    if FLIP_CARDS_ENABLED:
                        with col1:
                            render_flip_card("PB_Ratio", metrics.get('price_to_book'), "Price/Book")
                        with col2:
                            render_flip_card("PS_Ratio", metrics.get('price_to_sales'), "Price/Sales")
                        with col3:
                            render_flip_card("FCF_Yield", metrics.get('price_to_fcf'), "Price/FCF")
                    else:
                        with col1:
                            st.metric("Price/Book", f"{metrics.get('price_to_book', 'N/A')}")
                        with col2:
                            st.metric("Price/Sales", f"{metrics.get('price_to_sales', 'N/A'):.2f}" if metrics.get('price_to_sales') else 'N/A')
                        with col3:
                            st.metric("Price/FCF", f"{metrics.get('price_to_fcf', 'N/A'):.2f}" if metrics.get('price_to_fcf') else 'N/A')
                    
                    st.markdown("---")
                    
                    # Overall Assessment
                    st.markdown(f"**Overall Valuation:** {metrics.get('overall_valuation', 'N/A')}")
                    
                    if metrics.get('valuation_signals'):
                        st.markdown("**Signals:**")
                        for signal in metrics['valuation_signals']:
                            st.write(f"• {signal}")
                else:
                    st.warning(val_data.get('message', 'No valuation data available'))
        except Exception as e:
            st.error(f"Error analyzing valuation: {str(e)}")
    
    with cashflow_tab:
        st.markdown(f"### {icon('cash', '1.2em')} Cash Flow Deep Dive", unsafe_allow_html=True)
        
        try:
            from cashflow_analysis import analyze_cashflow
            
            with st.spinner("Analyzing cash flows..."):
                cf_data = analyze_cashflow(st.session_state.ticker)
                
                if cf_data['status'] == 'success':
                    metrics = cf_data['metrics']
                    
                    # Key Metrics - Use flip cards if available
                    st.caption("Click any metric for insight")
                    col1, col2, col3, col4 = st.columns(4)
                    
                    if FLIP_CARDS_ENABLED:
                        fcf = metrics.get('free_cash_flow', 0)
                        with col1:
                            render_flip_card("FCF_Yield", fcf / 1e9 if abs(fcf) > 1e9 else fcf / 1e6, "FCF ($B)" if abs(fcf) > 1e9 else "FCF ($M)")
                        with col2:
                            render_flip_card("Gross_Margin", metrics.get('fcf_conversion_rate'), "FCF Conversion")
                        with col3:
                            render_flip_card("Net_Margin", metrics.get('fcf_margin'), "FCF Margin")
                        with col4:
                            render_flip_card("ROE", metrics.get('cashflow_score'), "CF Score")
                    else:
                        with col1:
                            fcf = metrics.get('free_cash_flow', 0)
                            st.metric("Free Cash Flow", f"${fcf/1e9:.2f}B" if abs(fcf) > 1e9 else f"${fcf/1e6:.2f}M")
                        with col2:
                            st.metric("FCF Conversion", f"{metrics.get('fcf_conversion_rate', 0):.1f}%")
                        with col3:
                            st.metric("FCF Margin", f"{metrics.get('fcf_margin', 0):.2f}%")
                        with col4:
                            st.metric("Score", f"{metrics.get('cashflow_score', 0):.0f}/100")
                    
                    st.markdown("---")
                    
                    # Quality & Efficiency
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Quality:**")
                        st.write(f"• CF to NI Ratio: {metrics.get('cf_to_ni_ratio', 'N/A')}")
                        st.write(f"• Earnings Quality: {metrics.get('earnings_quality', 'N/A')}")
                        st.write(f"• FCF Consistency: {metrics.get('fcf_consistency', 'N/A')}")
                        st.write(f"• OCF Margin: {metrics.get('ocf_margin', 'N/A')}%")
                    
                    with col2:
                        st.markdown("**Efficiency:**")
                        st.write(f"• CapEx Intensity: {metrics.get('capex_intensity', 'N/A')}%")
                        st.write(f"• CapEx Profile: {metrics.get('capex_profile', 'N/A')}")
                        st.write(f"• CapEx to OCF: {metrics.get('capex_to_ocf_ratio', 'N/A')}%")
                        st.write(f"• WC to Sales: {metrics.get('working_capital_to_sales', 'N/A')}%")
                else:
                    st.warning(cf_data.get('message', 'No cash flow data available'))
        except Exception as e:
            st.error(f"Error analyzing cash flow: {str(e)}")



# NOTE: Other tab functions will be created as we migrate
# For now, existing tabs use the old inline structure
# This EXAMPLE function shows the pattern without breaking anything

# ==========================================
# MAIN CONTENT TABS (Current Structure - UNCHANGED)
# ==========================================

# App Title/Header
st.markdown('<h1 class="main-header"><i class="bi bi-lightning-fill" style="margin-right: 0.8rem;"></i>ATLAS FINANCIAL INTELLIGENCE</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #94a3b8; font-size: 1.1rem; margin-top: -1rem; margin-bottom: 2rem;"> Financial Analysis & Valuation Engine</p>', unsafe_allow_html=True)

# ==========================================
# CENTERED SEARCH BAR (Landing Page Only)
# ==========================================
# NOTE: Landing page logic moved to app_landing.py

if not st.session_state.get('data_extracted', False):
    render_landing_page(cached_extract_financials, validate_and_enrich, SP500_DISPLAY, extract_ticker)
    st.stop()  # Don't render tabs until data is extracted

# ==========================================
# PERSISTENT TICKER DISPLAY (Across All Tabs)
# ==========================================
# NOTE: Display functions moved to app_landing.py

if st.session_state.financials and st.session_state.ticker:
    company_name = st.session_state.financials.get('company_name', 'N/A')
    current_price = st.session_state.financials.get('market_data', {}).get('current_price', 'N/A')
    render_ticker_display(st.session_state.ticker, company_name, current_price)
else:
    render_no_ticker_placeholder()

# ==========================================
# CUSTOM CONTROL PANEL BUTTON (When Sidebar Collapsed)
# ==========================================

st.markdown("""
<style>
/* Hide default >> button */
button[kind="header"][data-testid="baseButton-header"] {
    display: none !important;
}

/* Custom Control Panel button */
.control-panel-btn {
    position: fixed;
    left: 20px;
    top: 80px;
    z-index: 999999;
    background: linear-gradient(135deg, #1e88e5 0%, #ffd700 100%);
    color: white;
    padding: 0.7rem 1.5rem;
    border-radius: 12px;
    font-weight: 700;
    font-size: 0.95rem;
    letter-spacing: 0.5px;
    cursor: pointer;
    border: none;
    box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
    transition: all 0.3s ease;
    font-family: 'Plus Jakarta Sans', sans-serif;
}

.control-panel-btn:hover {
    box-shadow: 0 6px 25px rgba(59, 130, 246, 0.5);
    transform: translateY(-2px) scale(1.02);
}

.control-panel-btn i {
    margin-right: 0.5rem;
}
</style>

<script>
// Create custom control panel button
setTimeout(function() {
    // Check if button already exists
    if (document.querySelector('.control-panel-btn')) return;
    
    // Create button
    const btn = document.createElement('button');
    btn.className = 'control-panel-btn';
    btn.innerHTML = '<i class="bi bi-sliders"></i> Control Panel';
    btn.onclick = function() {
        // Click the collapsed control to expand sidebar
        const collapsedControl = window.parent.document.querySelector('[data-testid="collapsedControl"]');
        if (collapsedControl) {
            collapsedControl.click();
        }
    };
    
    // Add to body
    document.body.appendChild(btn);
    
    // Show/hide based on sidebar state
    function updateButtonVisibility() {
        const sidebar = window.parent.document.querySelector('[data-testid="stSidebar"]');
        if (sidebar) {
            const isExpanded = sidebar.getAttribute('aria-expanded') === 'true';
            btn.style.display = isExpanded ? 'none' : 'block';
        }
    }
    
    // Check periodically (optimized interval)
    setInterval(updateButtonVisibility, 500);
    updateButtonVisibility();
}, 1000);
</script>
""", unsafe_allow_html=True)

# ==========================================
# SMOOTH TAB SCROLL BUTTONS
# ==========================================

st.markdown("""
<style>
/* Tab scroll container enhancement - FIXED */
.stTabs [data-baseweb="tab-list"] {
    gap: 0.5rem;
    position: relative;
    overflow-x: auto;
    scroll-behavior: smooth;
    scrollbar-width: thin;
    scrollbar-color: rgba(100, 181, 246, 0.3) transparent;
    justify-content: center !important; /* Center tabs to fill space */
}

/* Make tabs fill space evenly (8 tabs) */
.stTabs [data-baseweb="tab-list"] button {
    flex: 1 1 auto !important;
    min-width: 130px !important;
    max-width: 180px !important;
}

.stTabs [data-baseweb="tab-list"]::-webkit-scrollbar {
    height: 6px;
}

.stTabs [data-baseweb="tab-list"]::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.02);
    border-radius: 10px;
}

.stTabs [data-baseweb="tab-list"]::-webkit-scrollbar-thumb {
    background: rgba(100, 181, 246, 0.3);
    border-radius: 10px;
}

.stTabs [data-baseweb="tab-list"]::-webkit-scrollbar-thumb:hover {
    background: rgba(100, 181, 246, 0.5);
}

/* Clean scroll buttons - FIXED POSITIONING */
.tab-scroll-btn {
    position: absolute;
    top: 50%;
    transform: translateY(-50%);
    width: 40px;
    height: 40px;
    background: #1e2530;
    border: 1px solid rgba(59, 130, 246, 0.3);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    z-index: 1000;
    transition: all 0.3s ease;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.tab-scroll-btn:hover {
    background: #252d3a;
    border-color: rgba(59, 130, 246, 0.5);
    box-shadow: 0 6px 20px rgba(59, 130, 246, 0.3);
    transform: translateY(-50%) scale(1.1);
}

.tab-scroll-btn-left {
    left: 5px;
}

.tab-scroll-btn-right {
    right: 5px;
}

.tab-scroll-btn i {
    color: #3b82f6;
    font-size: 1.2rem;
}

.tab-scroll-btn.hidden {
    display: none !important;
}
</style>

<script>
// Wait for tabs to render then add scroll buttons (deferred for performance)
function initTabScrollButtons() {
    const tabList = document.querySelector('.stTabs [data-baseweb="tab-list"]');
    
    if (tabList && !document.querySelector('.tab-scroll-btn-left')) {
        // Create scroll buttons
        const leftBtn = document.createElement('div');
        leftBtn.className = 'tab-scroll-btn tab-scroll-btn-left';
        leftBtn.innerHTML = '<i class="bi bi-chevron-left"></i>';
        leftBtn.onclick = () => {
            tabList.scrollBy({ left: -300, behavior: 'smooth' });
        };
        
        const rightBtn = document.createElement('div');
        rightBtn.className = 'tab-scroll-btn tab-scroll-btn-right';
        rightBtn.innerHTML = '<i class="bi bi-chevron-right"></i>';
        rightBtn.onclick = () => {
            tabList.scrollBy({ left: 300, behavior: 'smooth' });
        };
        
        // Insert buttons relative to tab container
        const tabsContainer = tabList.parentElement;
        tabsContainer.style.position = 'relative';
        tabsContainer.appendChild(leftBtn);
        tabsContainer.appendChild(rightBtn);
        
        // Auto-hide and opacity logic
        function updateButtons() {
            const hasScroll = tabList.scrollWidth > tabList.clientWidth;
            leftBtn.classList.toggle('hidden', !hasScroll);
            rightBtn.classList.toggle('hidden', !hasScroll);
            
            if (hasScroll) {
                const isAtStart = tabList.scrollLeft <= 5;
                const isAtEnd = tabList.scrollLeft + tabList.clientWidth >= tabList.scrollWidth - 5;
                
                leftBtn.style.opacity = isAtStart ? '0.3' : '1';
                leftBtn.style.pointerEvents = isAtStart ? 'none' : 'auto';
                
                rightBtn.style.opacity = isAtEnd ? '0.3' : '1';
                rightBtn.style.pointerEvents = isAtEnd ? 'none' : 'auto';
            }
        }
        
        // Check on scroll and resize
        tabList.addEventListener('scroll', updateButtons);
        window.addEventListener('resize', updateButtons);
        updateButtons();
    }
}

// Defer execution until page is fully loaded for better performance
if (document.readyState === 'complete') {
    setTimeout(initTabScrollButtons, 500);
} else {
    window.addEventListener('load', () => setTimeout(initTabScrollButtons, 500));
}
</script>
""", unsafe_allow_html=True)

# ==========================================
# FLOATING AI CHAT PANEL (Bloomberg Style)
# ==========================================

# Initialize AI chat state
if "show_ai_chat" not in st.session_state:
    st.session_state.show_ai_chat = False
if "ai_chat_history" not in st.session_state:
    st.session_state.ai_chat_history = []
if "ai_disclaimer_shown" not in st.session_state:
    st.session_state.ai_disclaimer_shown = False

# Toggle buttons (top-right corner) - New Search and AI
# CSS for matching button styles
    st.markdown("""
    <style>
/* Match header button styles */
[data-testid="stHorizontalBlock"] > div:nth-last-child(-n+2) button[kind="secondary"] {
    font-size: 0.75rem !important;
    font-weight: 600 !important;
    padding: 0.35rem 0.6rem !important;
    border-radius: 6px !important;
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
    border: none !important;
    color: white !important;
    white-space: nowrap !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
col1, col2, col3 = st.columns([7, 1, 1])
with col2:
    if st.session_state.get('data_extracted', False):
        if st.button("New Search", key="home_btn", use_container_width=True):
            st.session_state.financials = None
            st.session_state.dcf_results = None
            st.session_state.ticker = ""
            st.session_state.data_extracted = False
            st.rerun()
with col3:
    if st.button("AI Chat", key="ai_toggle", help="AI Financial Advisor", use_container_width=True):
        st.session_state.show_ai_chat = not st.session_state.show_ai_chat
        st.rerun()

# AI Chat Panel - Using Dialog/Modal
if st.session_state.show_ai_chat:
    # Initialize AI advisor (reinit if failed before)
    if "ai_advisor" not in st.session_state or st.session_state.ai_advisor is None:
        try:
            print("[AI] Initializing FinancialAI...")
            from financial_ai import FinancialAI
            st.session_state.ai_advisor = FinancialAI(tier="free")
            if st.session_state.ai_advisor.primary_model:
                print("[AI] FinancialAI initialized with Gemini")
            else:
                print("[AI] FinancialAI initialized but no model available")
                st.session_state.ai_error = "Gemini model not initialized"
        except Exception as e:
            st.session_state.ai_advisor = None
            st.session_state.ai_error = str(e)
            print(f"[AI ERROR] Failed to initialize: {e}")
            import traceback
            traceback.print_exc()
    
    # Build COMPREHENSIVE company data for AI - pass ALL extracted metrics
    company_data = {}
    if st.session_state.financials:
        fin = st.session_state.financials
        
        # Basic info
        company_data = {
            'ticker': st.session_state.get('ticker', 'N/A'),
            'company_name': fin.get('company_name', st.session_state.get('ticker', 'N/A')),
            'sector': fin.get('sector', 'N/A'),
            'industry': fin.get('industry', 'N/A'),
            'current_price': fin.get('current_price', 'N/A'),
            'market_cap': fin.get('market_cap', 'N/A'),
        }
        
        # Add ALL ratios if available
        if 'ratios' in fin:
            try:
                ratios_df = fin['ratios']
                if hasattr(ratios_df, 'empty') and not ratios_df.empty:
                    latest_col = ratios_df.columns[0]
                    for idx in ratios_df.index:
                        val = ratios_df.loc[idx, latest_col]
                        if pd.notna(val) and val not in [None, 'N/A', '']:
                            company_data[str(idx)] = val
            except Exception:
                pass
        
        # Add key metrics directly from fin dict
        key_metrics = ['pe_ratio', 'forward_pe', 'peg_ratio', 'price_to_book', 'price_to_sales',
                       'revenue', 'net_income', 'gross_margin', 'operating_margin', 'profit_margin',
                       'roe', 'roa', 'roic', 'current_ratio', 'quick_ratio', 'debt_to_equity',
                       'revenue_growth', 'earnings_growth', 'free_cash_flow', 'dividend_yield',
                       'eps', 'book_value', 'total_debt', 'total_cash', 'shares_outstanding',
                       'beta', 'fifty_two_week_high', 'fifty_two_week_low', 'average_volume']
        for key in key_metrics:
            if key in fin and fin[key] not in [None, 'N/A', '', 0]:
                company_data[key] = fin[key]
    
    # AI Chat Container - Visible at top of page
    st.markdown("---")
    st.markdown("### 🤖 AI Financial Advisor")
    
    # Show disclaimer
    if not st.session_state.ai_disclaimer_shown:
        st.info("⚠️ AI responses are for informational purposes only. Not investment advice.")
        st.session_state.ai_disclaimer_shown = True
    
    # Check AI availability
    if st.session_state.ai_advisor is None:
        st.error(f"❌ AI unavailable: {st.session_state.get('ai_error', 'Unknown error')}")
        st.code("Troubleshooting:\n1. Set GEMINI_API_KEY in environment\n2. pip install google-generativeai")
    else:
        st.success("✅ AI Ready - Gemini connected")
        
        # Chat history display
        if st.session_state.ai_chat_history:
            chat_container = st.container()
            with chat_container:
                for msg in st.session_state.ai_chat_history[-4:]:
                    if msg['role'] == 'user':
                        st.markdown(f"**🧑 You:** {msg['content']}")
                    else:
                        st.markdown(f"**🤖 AI:** {msg['content']}")
                st.markdown("---")
        
        # Input area
        user_q = st.text_input("Ask a question:", key="ai_input", placeholder="e.g., Is this stock overvalued?")
        
        c1, c2, c3 = st.columns([2, 1, 1])
        with c1:
            if st.button("Send", key="send_ai", use_container_width=True):
                if user_q.strip():
                    st.session_state.ai_chat_history.append({'role': 'user', 'content': user_q})
                    with st.spinner("🤔 Thinking..."):
                        try:
                            result = st.session_state.ai_advisor.ask(user_q, company_data, 'general')
                            response = result.get('response', 'No response') if result else 'No response'
                            st.session_state.ai_chat_history.append({'role': 'assistant', 'content': response})
                        except Exception as e:
                            st.session_state.ai_chat_history.append({'role': 'assistant', 'content': f"Error: {e}"})
                    st.rerun()
        with c2:
            if st.button("Clear", key="clear_ai", use_container_width=True):
                st.session_state.ai_chat_history = []
                st.rerun()
        with c3:
            if st.button("Close", key="close_ai", use_container_width=True):
                st.session_state.show_ai_chat = False
                st.rerun()
        
        # Quick questions
        st.caption("Quick questions:")
        q1, q2, q3 = st.columns(3)
        with q1:
            if st.button("📊 Overvalued?", key="q1"):
                st.session_state.ai_chat_history.append({'role': 'user', 'content': "Is this stock overvalued?"})
                with st.spinner("Analyzing..."):
                    try:
                        r = st.session_state.ai_advisor.ask("Is this stock overvalued?", company_data, 'general')
                        st.session_state.ai_chat_history.append({'role': 'assistant', 'content': r.get('response', 'No response')})
                    except Exception as e:
                        st.session_state.ai_chat_history.append({'role': 'assistant', 'content': str(e)})
                st.rerun()
        with q2:
            if st.button("⚠️ Risks?", key="q2"):
                st.session_state.ai_chat_history.append({'role': 'user', 'content': "What are the key risks?"})
                with st.spinner("Analyzing..."):
                    try:
                        r = st.session_state.ai_advisor.ask("What are the key risks?", company_data, 'general')
                        st.session_state.ai_chat_history.append({'role': 'assistant', 'content': r.get('response', 'No response')})
                    except Exception as e:
                        st.session_state.ai_chat_history.append({'role': 'assistant', 'content': str(e)})
                st.rerun()
        with q3:
            if st.button("📝 Summary", key="q3"):
                st.session_state.ai_chat_history.append({'role': 'user', 'content': "Give me a brief financial summary"})
                with st.spinner("Analyzing..."):
                    try:
                        r = st.session_state.ai_advisor.ask("Give me a brief financial summary", company_data, 'general')
                        st.session_state.ai_chat_history.append({'role': 'assistant', 'content': r.get('response', 'No response')})
                    except Exception as e:
                        st.session_state.ai_chat_history.append({'role': 'assistant', 'content': str(e)})
                st.rerun()
    
    st.markdown("---")

# ==========================================
# MAIN CONTENT
# ==========================================

if st.session_state.financials is None:
    # Simple prompt - no clutter
    st.info("**Get Started:** Enter a ticker in the sidebar and click 'Extract Data'")

else:
    # ==========================================
    # QUICK SEARCH BAR (Prominent, Always Visible)
    # ==========================================
    from search_utils import search_financials, get_search_suggestions
    
    # Search bar container with styling
    search_col1, search_col2, search_col3 = st.columns([1, 3, 1])
    
    with search_col2:
        # Styled search input
        search_query = st.text_input(
            "🔍 Quick Search",
            placeholder="Search any metric: Revenue, PE Ratio, ROE, Margin, Debt...",
            key="main_metric_search",
            label_visibility="collapsed"
        )
        
        # Show results in an expandable section
        if search_query and len(search_query) >= 2:
            results = search_financials(st.session_state.financials, search_query, limit=12)
            
            if results:
                with st.expander(f"📊 **{len(results)} results for '{search_query}'**", expanded=True):
                    # Display results in a clean grid
                    result_cols = st.columns(3)
                    for idx, r in enumerate(results):
                        with result_cols[idx % 3]:
                            st.markdown(f"""
                            <div style='padding: 0.6rem; margin: 0.3rem 0; 
                                        background: rgba(59, 130, 246, 0.08); 
                                        border-radius: 8px; border-left: 3px solid #3b82f6;'>
                                <div style='font-size: 0.75rem; color: #94a3b8;'>{r['icon']} {r['category']}</div>
                                <div style='font-weight: 600; color: #f0f4f8;'>{r['metric']}</div>
                                <div style='font-size: 1.1rem; color: #3b82f6; font-weight: 700;'>{r['value']}</div>
                                <div style='font-size: 0.7rem; color: #64748b;'>📍 {r['location']}</div>
                            </div>
                            """, unsafe_allow_html=True)
            else:
                st.info(f"No results for '{search_query}'")
                suggestions = get_search_suggestions(st.session_state.financials)
                if suggestions:
                    st.caption(f"💡 Try: {', '.join(suggestions[:6])}")
    
    st.markdown("")  # Spacing before tabs
    
    # Main tabs (dynamically show based on available data)
    has_quant = st.session_state.financials and "quant_analysis" in st.session_state.financials
    
    # Always show these tabs now (backends are ready)
    # 8-Tab Professional Structure
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
        "Dashboard",           # 1 - Quick overview
        "Data",                # 2 - Extract
        "Deep Dive",           # 3 - Analysis (with sub-tabs)
        "Valuation",           # 4 - Model (DCF)
        "Risk & Ownership",    # 5 - Forensic + Governance
        "Market Intelligence", # 6 - Technical + Quant + Options + Compare
        "News",                # 7 - News & Events
        "IC Memo"              # 8 - Investment Summary
    ])
    
    # ==========================================
    # TAB 1: DASHBOARD - Quick Overview
    # ==========================================
    
    with tab1:
        render_dashboard_tab(st.session_state.ticker, st.session_state.financials, visualizer)
    
    # ==========================================
    # TAB 2: DATA - Financial Extraction
    # ==========================================
    
    with tab2:
        st.markdown(f"## {icon('bar-chart-line', '1.5em')} Financial Data: {st.session_state.ticker}", unsafe_allow_html=True)
        
        # Company info
        company_name = st.session_state.financials.get("company_name", st.session_state.ticker)
        extraction_time = st.session_state.financials.get("extraction_time", "N/A")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Company", company_name)
        with col2:
            st.metric("Ticker", st.session_state.ticker)
        with col3:
            st.metric("Extraction Time", extraction_time)
        
        st.markdown("---")
        
        # Export All Data to Excel
        if st.button("📥 Export All to Excel (Professional Format)", type="primary", use_container_width=True):
            try:
                excel_filename = f"{st.session_state.ticker}_Financial_Report_{datetime.now().strftime('%Y%m%d')}.xlsx"
                export_financials_to_excel(st.session_state.financials, excel_filename)
                
                # Provide download link
                with open(excel_filename, "rb") as f:
                    st.download_button(
                        label="Download Excel Report",
                        data=f,
                        file_name=excel_filename,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
                st.success(f"Excel report created: {excel_filename}")
            except Exception as e:
                st.error(f"Excel export failed: {str(e)}")
        
        st.markdown("---")
        
        # Sub-tabs for different statements
        sub_tab1, sub_tab2, sub_tab3, sub_tab4, sub_tab5, sub_tab6 = st.tabs([
            "Income Statement",
            "Balance Sheet",
            "Cash Flow",
            "Stock Prices",
            "Ratios",
            "Growth Metrics"
        ])
        
        with sub_tab1:
            st.subheader("Income Statement (Annual)")
            
            # Flip card metrics at top
            if DATA_FLIP_AVAILABLE:
                render_income_metrics(st.session_state.financials)
            
            income = st.session_state.financials.get("income_statement", pd.DataFrame())
            
            if not income.empty:
                # Use enhanced dataframe with sorting, filtering, export
                enhanced_dataframe(
                    income,
                    title="Income Statement",
                    key="income_stmt",
                    show_search=True,
                    show_export=True,
                    conditional_formatting=True,
                    height=400
                )
            else:
                st.warning("No income statement data available")
        
        with sub_tab2:
            st.subheader("Balance Sheet (Annual)")
            
            # Flip card metrics at top
            if DATA_FLIP_AVAILABLE:
                render_balance_metrics(st.session_state.financials)
            
            balance = st.session_state.financials.get("balance_sheet", pd.DataFrame())
            
            if not balance.empty:
                # Use enhanced dataframe with sorting, filtering, export
                enhanced_dataframe(
                    balance,
                    title="Balance Sheet",
                    key="balance_sheet",
                    show_search=True,
                    show_export=True,
                    conditional_formatting=True,
                    height=400
                )
            else:
                st.warning("No balance sheet data available")
        
        with sub_tab3:
            st.subheader("Cash Flow Statement (Annual)")
            
            # Flip card metrics at top
            if DATA_FLIP_AVAILABLE:
                render_cashflow_metrics(st.session_state.financials)
            
            cashflow = st.session_state.financials.get("cash_flow", pd.DataFrame())
            
            if not cashflow.empty:
                # Use helper function for proper formatting
                cf_display, cf_csv = prepare_table_for_display(cashflow, "Cash Flow")
                
                smart_dataframe(cf_display, title=None, height=400, key="cashflow_table")
                
                # Download button with properly formatted CSV
                csv = cf_csv.to_csv(index=True)
                st.download_button(
                    "Download CSV",
                    data=csv,
                    file_name=f"{st.session_state.ticker}_cash_flow.csv",
                    mime="text/csv"
                )
            else:
                st.warning("No cash flow data available")
        
        with sub_tab4:
            st.subheader("Historical Stock Prices")
            
            # Flip card metrics at top
            if DATA_FLIP_AVAILABLE:
                render_price_metrics(st.session_state.financials)
            
            market_data = st.session_state.financials.get("market_data", {})
            historical_prices = market_data.get("historical_prices", pd.DataFrame())
            
            if not historical_prices.empty:
                # Determine frequency based on IPO date
                ipo_info = ""
                if "quant_analysis" in st.session_state.financials:
                    quant = st.session_state.financials["quant_analysis"]
                    ipo_date = quant.get("ipo_date", "Unknown")
                    freq = quant.get("data_frequency", "Daily")
                    ipo_info = f"**IPO Date:** {ipo_date} | **Frequency:** {freq}"
                
                st.info(f"Historical data from January 1, 1990 to present. {ipo_info}")
                
                # Display key metrics with price change indicators
                current_price = market_data.get("current_price", "N/A")
                high_52w = historical_prices['Close'].rolling(252).max().iloc[-1] if len(historical_prices) > 252 else historical_prices['Close'].max()
                low_52w = historical_prices['Close'].rolling(252).min().iloc[-1] if len(historical_prices) > 252 else historical_prices['Close'].min()
                
                # Calculate 1-Year return (more meaningful than all-time)
                if len(historical_prices) >= 252:
                    price_1y_ago = historical_prices['Close'].iloc[-252]
                    one_year_return = ((historical_prices['Close'].iloc[-1] / price_1y_ago) - 1) * 100
                    price_change_1y = historical_prices['Close'].iloc[-1] - price_1y_ago
                else:
                    # Use available data if less than 1 year
                    price_1y_ago = historical_prices['Close'].iloc[0]
                    one_year_return = ((historical_prices['Close'].iloc[-1] / price_1y_ago) - 1) * 100
                    price_change_1y = historical_prices['Close'].iloc[-1] - price_1y_ago
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    # Current price with change indicator
                    if isinstance(current_price, (int, float)) and price_change_1y != 0:
                        change_color = "#10b981" if price_change_1y > 0 else "#ef4444"
                        change_arrow = "+" if price_change_1y > 0 else ""
                        st.metric(
                            "Current Price", 
                            f"${current_price:.2f}",
                            delta=f"{change_arrow}${abs(price_change_1y):.2f} ({change_arrow}{one_year_return:.1f}%)"
                        )
                    else:
                        st.metric("Current Price", f"${current_price:.2f}" if isinstance(current_price, (int, float)) else current_price)
                with col2:
                    st.metric("52-Week High", f"${high_52w:.2f}")
                with col3:
                    st.metric("52-Week Low", f"${low_52w:.2f}")
                with col4:
                    # Show 1Y Return instead of all-time return
                    delta_color = "normal" if one_year_return > 0 else "inverse"
                    st.metric("1Y Return", f"{one_year_return:.1f}%", delta=f"vs 1 year ago", delta_color="off")
                
                st.markdown("---")
                
                # Time Period Selector (Bulletproof)
                st.markdown("### 📅 Select Time Period")
                
                # Calculate how many years of data we have
                total_days = len(historical_prices)
                years_available = total_days / 252  # Approx trading days per year
                ipo_date = historical_prices.index[0]
                
                # Determine available periods (bulletproof)
                available_periods = []
                period_info = {}
                
                if total_days >= 5:  # At least 1 week
                    available_periods.append("1W")
                    period_info["1W"] = {"days": 5, "freq": "Daily"}
                
                if total_days >= 21:  # At least 1 month
                    available_periods.append("1M")
                    period_info["1M"] = {"days": 21, "freq": "Daily"}
                
                if total_days >= 252:  # At least 1 year
                    available_periods.append("1Y")
                    period_info["1Y"] = {"days": 252, "freq": "Daily"}
                
                if years_available >= 10:
                    available_periods.append("10Y")
                    period_info["10Y"] = {"days": 252 * 10, "freq": "Monthly"}
                
                # Always available (show max history)
                available_periods.append("MAX (Since IPO)")
                period_info["MAX (Since IPO)"] = {"days": total_days, "freq": "Monthly" if years_available > 5 else "Daily"}
                
                col_select, col_freq, col_info = st.columns([1, 1, 2])
                
                with col_select:
                    selected_period = st.selectbox(
                        "Display Period",
                        options=available_periods,
                        index=2 if "1Y" in available_periods else 0
                    )
                
                with col_freq:
                    # Determine available frequencies based on period
                    if selected_period == "1W":
                        freq_options = ["Daily"]  # Only daily for 1 week
                    elif selected_period == "1M":
                        freq_options = ["Daily", "Weekly"]
                    elif selected_period in ["1Y", "10Y"]:
                        freq_options = ["Daily", "Weekly", "Monthly"]
                    else:  # MAX
                        freq_options = ["Monthly", "Weekly"] if years_available > 5 else ["Daily", "Weekly"]
                    
                    selected_frequency = st.selectbox(
                        "Data Frequency",
                        options=freq_options,
                        index=0
                    )
                
                with col_info:
                    period_config = period_info.get(selected_period, {})
                    st.info(f"ℹ Showing **{selected_period}** data | Frequency: **{selected_frequency}** | IPO: {ipo_date.strftime('%Y-%m-%d')}")
                
                # Filter data based on selection
                if selected_period == "1W":
                    chart_data = historical_prices.tail(5)
                    table_data = historical_prices.tail(5)
                elif selected_period == "1M":
                    chart_data = historical_prices.tail(21)
                    table_data = historical_prices.tail(21)
                elif selected_period == "1Y":
                    chart_data = historical_prices.tail(252)
                    table_data = historical_prices.tail(252)
                elif selected_period == "10Y":
                    chart_data = historical_prices.tail(252 * 10)
                    table_data = chart_data
                else:  # MAX
                    chart_data = historical_prices
                    table_data = historical_prices
                
                # Apply frequency resampling based on user selection
                if selected_frequency == "Weekly":
                    chart_data = chart_data.resample('W').last()
                    table_data = table_data.resample('W').last()
                elif selected_frequency == "Monthly":
                    chart_data = chart_data.resample('M').last()
                    table_data = table_data.resample('M').last()
                # Daily = no resampling needed
                
                # Price chart
                import plotly.graph_objects as go
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=chart_data.index,
                    y=chart_data['Close'],
                    mode='lines',
                    name='Close Price',
                    line=dict(color='#1f77b4', width=2)
                ))
                fig.update_layout(
                    title=f"{st.session_state.ticker} Stock Price History ({selected_period})",
                    xaxis_title="Date",
                    yaxis_title="Price (USD)",
                    hovermode='x unified',
                    height=500
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Data table
                freq_label = period_config.get('freq', 'Daily')
                st.markdown(f"### Recent Price Data ({freq_label})")
                display_prices = table_data.copy()
                display_prices.index = display_prices.index.strftime('%Y-%m-%d')
                
                # Format columns
                for col in ['Open', 'High', 'Low', 'Close']:
                    if col in display_prices.columns:
                        display_prices[col] = display_prices[col].apply(lambda x: f"${x:.2f}")
                if 'Volume' in display_prices.columns:
                    display_prices['Volume'] = display_prices['Volume'].apply(lambda x: f"{x:,.0f}")
                
                smart_dataframe(display_prices.iloc[::-1], title=None, height=400, key="price_history_table")
                
                # Download button
                csv = historical_prices.to_csv()
                st.download_button(
                    "Download Full Price History CSV",
                    data=csv,
                    file_name=f"{st.session_state.ticker}_price_history.csv",
                    mime="text/csv"
                )
            else:
                st.warning("No historical price data available")
        
        with sub_tab5:
            st.subheader("Key Financial Ratios")
            
            # Flip card metrics at top
            if DATA_FLIP_AVAILABLE:
                render_ratio_metrics(st.session_state.financials)
            
            ratios = extractor.calculate_ratios(st.session_state.financials)
            growth = extractor.calculate_growth_rates(st.session_state.financials)
            
            # Debug: Check if ratios are actually calculated
            if ratios and "status" not in ratios:
                # Check if all values are zero
                all_zero = all(v == 0 for k, v in ratios.items() if isinstance(v, (int, float)))
                if all_zero:
                    st.warning("Ratios returned all zeros. This may indicate data quality issues or missing financial statement items.")
                    with st.expander("Show raw ratio data"):
                        st.json(ratios)
                else:
                    # Get component values for tooltips
                    from format_helpers import format_financial_number
                    comp = ratios.get("_components", {})
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric(
                            "Gross Margin", 
                            f"{ratios.get('Gross_Margin', 0) * 100:.1f}%",
                            help=f"Gross Profit {format_financial_number(comp.get('gross_profit', 0))} ÷ Revenue {format_financial_number(comp.get('revenue', 0))} = {ratios.get('Gross_Margin', 0) * 100:.1f}%"
                        )
                        st.metric(
                            "Operating Margin", 
                            f"{ratios.get('Operating_Margin', 0) * 100:.1f}%",
                            help=f"Operating Income {format_financial_number(comp.get('operating_income', 0))} ÷ Revenue {format_financial_number(comp.get('revenue', 0))} = {ratios.get('Operating_Margin', 0) * 100:.1f}%"
                        )
                    
                    with col2:
                        st.metric(
                            "Net Margin", 
                            f"{ratios.get('Net_Margin', 0) * 100:.1f}%",
                            help=f"Net Income {format_financial_number(comp.get('net_income', 0))} ÷ Revenue {format_financial_number(comp.get('revenue', 0))} = {ratios.get('Net_Margin', 0) * 100:.1f}%"
                        )
                        st.metric(
                            "ROE", 
                            f"{ratios.get('ROE', 0) * 100:.1f}%",
                            help=f"Net Income {format_financial_number(comp.get('net_income', 0))} ÷ Total Equity {format_financial_number(comp.get('total_equity', 0))} = {ratios.get('ROE', 0) * 100:.1f}%"
                        )
                    
                    with col3:
                        st.metric(
                            "ROA", 
                            f"{ratios.get('ROA', 0) * 100:.1f}%",
                            help=f"Net Income {format_financial_number(comp.get('net_income', 0))} ÷ Total Assets {format_financial_number(comp.get('total_assets', 0))} = {ratios.get('ROA', 0) * 100:.1f}%"
                        )
                        st.metric(
                            "Debt/Equity", 
                            f"{ratios.get('Debt_to_Equity', 0):.2f}",
                            help=f"Total Debt {format_financial_number(comp.get('total_debt', 0))} ÷ Total Equity {format_financial_number(comp.get('total_equity', 0))} = {ratios.get('Debt_to_Equity', 0):.2f}"
                        )
                    
                    with col4:
                        fcf = ratios.get('Free_Cash_Flow', 0)
                        fcf_display = format_financial_number(fcf) if fcf != 0 else "$0"
                        st.metric(
                            "Free Cash Flow", 
                            fcf_display,
                            help=f"Operating Cash Flow {format_financial_number(comp.get('op_cash_flow', 0))} - Capital Expenditure {format_financial_number(abs(comp.get('capex', 0)))} = {fcf_display}"
                        )
            else:
                st.error("Failed to calculate ratios. Check if financial statements have required fields.")
        
        with sub_tab6:
            st.markdown(f"### {icon('graph-up-arrow')} Comprehensive Growth Analysis", unsafe_allow_html=True)
            
            # Flip card metrics at top
            if DATA_FLIP_AVAILABLE:
                render_growth_metrics(st.session_state.financials)
            
            growth = st.session_state.financials.get("growth_rates", {})
            
            if "status" not in growth and growth:
                # Detect if quarterly data (has QoQ or YoY fields)
                is_quarterly = any("QoQ" in k or "YoY" in k for k in growth.keys())
                
                if is_quarterly:
                    st.info("ℹ **Quarterly Data Detected** - Showing QoQ, YoY, and CAGR metrics")
                else:
                    st.info("ℹ **Annual Data** - Showing CAGR, Dollar Change, and Percent Change")
                
                # Define metric groups
                metric_groups = {
                    "Total_Revenue": "Total Revenue",
                    "COGS": "Cost of Goods Sold (COGS)",
                    "Gross_Profit": "Gross Profit",
                    "SGA_Expenses": "SG&A Expenses",
                    "Total_Operating_Expenses": "Total Operating Expenses",
                    "Operating_Profit": "Operating Profit",
                    "NOPAT": "Net Operating Profit After Tax (NOPAT)",
                    "Net_Income": "Net Income"
                }
                
                # Create comprehensive growth table
                growth_data = []
                
                for metric_key, metric_label in metric_groups.items():
                    row = {"Metric": metric_label}
                    
                    # CAGR (always present)
                    cagr_key = f"{metric_key}_CAGR"
                    if cagr_key in growth:
                        row["CAGR (%)"] = f"{growth[cagr_key]:.2f}%"
                    else:
                        row["CAGR (%)"] = "N/A"
                    
                    # Latest Value
                    latest_key = f"{metric_key}_Latest_Value"
                    if latest_key in growth:
                        row["Latest Value"] = format_financial_number(growth[latest_key])
                    else:
                        row["Latest Value"] = "N/A"
                    
                    # Dollar Change
                    dollar_key = f"{metric_key}_Dollar_Change"
                    if dollar_key in growth:
                        row["$ Change"] = format_financial_number(growth[dollar_key])
                    else:
                        row["$ Change"] = "N/A"
                    
                    # Percent Change
                    pct_key = f"{metric_key}_Pct_Change"
                    if pct_key in growth:
                        row["% Change"] = f"{growth[pct_key]:.2f}%"
                    else:
                        row["% Change"] = "N/A"
                    
                    # Quarterly metrics (if available)
                    if is_quarterly:
                        qoq_key = f"{metric_key}_QoQ"
                        if qoq_key in growth:
                            row["QoQ (%)"] = f"{growth[qoq_key]:.2f}%"
                        else:
                            row["QoQ (%)"] = "N/A"
                        
                        yoy_key = f"{metric_key}_YoY"
                        if yoy_key in growth:
                            row["YoY (%)"] = f"{growth[yoy_key]:.2f}%"
                        else:
                            row["YoY (%)"] = "N/A"
                    
                    # Only add row if we have at least one metric
                    if any(v != "N/A" for k, v in row.items() if k != "Metric"):
                        growth_data.append(row)
                
                if growth_data:
                    growth_df = pd.DataFrame(growth_data)
                    
                    # Display table with clean formatting (uses AgGrid if available)
                    smart_dataframe(growth_df, title=None, height=400, key="growth_metrics_table")
                    
                    # Download button
                    csv = growth_df.to_csv(index=False)
                    st.download_button(
                        "Download Growth Metrics CSV",
                        data=csv,
                        file_name=f"{st.session_state.ticker}_growth_metrics.csv",
                        mime="text/csv"
                    )
                    
                    # Visual breakdown
                    st.markdown("---")
                    st.markdown(f"### {icon('bar-chart-line', '1.2em')} Visual Breakdown", unsafe_allow_html=True)
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.markdown(f"**{icon('rocket-takeoff', '1em')} Top Growers (CAGR)**", unsafe_allow_html=True)
                        cagr_items = [(metric_groups.get(k.replace("_CAGR", ""), k), v) 
                                     for k, v in growth.items() if "_CAGR" in k and isinstance(v, (int, float))]
                        cagr_items.sort(key=lambda x: x[1], reverse=True)
                        for label, value in cagr_items[:5]:
                            icon_html = icon('arrow-up', '1em', 'green') if value > 0 else icon('arrow-down', '1em', 'red')
                            st.markdown(f"{icon_html} {label}: **{value:.1f}%**", unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown(f"**{icon('cash-coin', '1em')} Largest $ Changes**", unsafe_allow_html=True)
                        dollar_items = [(metric_groups.get(k.replace("_Dollar_Change", ""), k), v) 
                                       for k, v in growth.items() if "_Dollar_Change" in k and isinstance(v, (int, float))]
                        dollar_items.sort(key=lambda x: abs(x[1]), reverse=True)
                        for label, value in dollar_items[:5]:
                            icon_html = icon('arrow-up', '1em', 'green') if value > 0 else icon('arrow-down', '1em', 'red')
                            st.markdown(f"{icon_html} {label}: **{format_financial_number(value)}**", unsafe_allow_html=True)
                    
                    with col3:
                        if is_quarterly:
                            st.markdown(f"**{icon('graph-up-arrow', '1em')} YoY Performance**", unsafe_allow_html=True)
                            yoy_items = [(metric_groups.get(k.replace("_YoY", ""), k), v) 
                                        for k, v in growth.items() if "_YoY" in k and isinstance(v, (int, float))]
                            yoy_items.sort(key=lambda x: x[1], reverse=True)
                            for label, value in yoy_items[:5]:
                                icon_html = icon('arrow-up', '1em', 'green') if value > 0 else icon('arrow-down', '1em', 'red')
                                st.markdown(f"{icon_html} {label}: **{value:.1f}%**", unsafe_allow_html=True)
                        else:
                            st.markdown(f"**{icon('bar-chart-line', '1em')} % Change Leaders**", unsafe_allow_html=True)
                            pct_items = [(metric_groups.get(k.replace("_Pct_Change", ""), k), v) 
                                        for k, v in growth.items() if "_Pct_Change" in k and isinstance(v, (int, float))]
                            pct_items.sort(key=lambda x: x[1], reverse=True)
                            for label, value in pct_items[:5]:
                                icon_html = icon('arrow-up', '1em', 'green') if value > 0 else icon('arrow-down', '1em', 'red')
                                st.markdown(f"{icon_html} {label}: **{value:.1f}%**", unsafe_allow_html=True)
                else:
                    st.warning("No growth metrics available for the selected statement")
            else:
                st.error("Growth rates calculation failed or no data available")
    
    # ==========================================
    # TAB 3: DEEP DIVE - Financial Analysis
    # ==========================================
    
    with tab3:
        render_analysis_tab(st.session_state.ticker, st.session_state.financials)
    
    # ==========================================
    # TAB 4: VALUATION - DCF Modeling
    # ==========================================
    
    with tab4:
        st.markdown(f"## {icon('cash-coin', '1.5em')} DCF Valuation Model", unsafe_allow_html=True)
        
        # Create sub-tabs for different DCF modes
        dcf_tab1, dcf_tab2 = st.tabs([
            "📊 Quick 3-Scenario DCF",
            "🎛️ Live Scenario Builder"
        ])
        
        # ==========================================
        # SUB-TAB 1: QUICK 3-SCENARIO DCF (Original)
        # ==========================================
        with dcf_tab1:
            # Run DCF button
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                if st.button("▶️ RUN 3-SCENARIO DCF ANALYSIS", type="primary", use_container_width=True, key="dcf_button_quick"):
                    with st.spinner("Building DCF model..."):
                        try:
                            model = DCFModel(st.session_state.financials)
                            results = model.run_all_scenarios()
                            st.session_state.dcf_results = results
                            st.success("DCF Analysis Complete!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"DCF failed: {e}")
            
            with col2:
                projection_years = st.number_input("Projection Years", min_value=3, max_value=10, value=5, key="proj_years_quick")
            
            with col3:
                show_sensitivity = st.checkbox("Show Sensitivity", value=False, key="show_sens_quick")
            
            st.markdown("---")
        
        if st.session_state.dcf_results:
            results = st.session_state.dcf_results
            
            # Summary metrics
            st.markdown(f"### {icon('bar-chart-line')} Valuation Summary", unsafe_allow_html=True)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                conservative = results["conservative"]["value_per_share"]
                st.metric(
                    "Conservative",
                    f"${conservative:.2f}",
                    help="Bear case scenario with lower growth and higher discount rate"
                )
            
            with col2:
                base = results["base"]["value_per_share"]
                st.metric(
                    "Base Case",
                    f"${base:.2f}",
                    help="Most likely scenario using historical averages"
                )
            
            with col3:
                aggressive = results["aggressive"]["value_per_share"]
                st.metric(
                    "Aggressive",
                    f"${aggressive:.2f}",
                    help="Bull case with higher growth and lower discount rate"
                )
            
            with col4:
                weighted = results["weighted_average"]
                st.metric(
                    "Weighted Avg",
                    f"${weighted:.2f}",
                    help="40% Base + 30% Conservative + 30% Aggressive"
                )
            
            # Scenario comparison chart
            st.plotly_chart(
                visualizer.plot_dcf_comparison(results),
                use_container_width=True
            )
            
            # Detailed breakdown tabs
            scenario_tab1, scenario_tab2, scenario_tab3 = st.tabs([
                "Conservative Details",
                "Base Case Details",
                "Aggressive Details"
            ])
            
            for tab, scenario_name in zip(
                [scenario_tab1, scenario_tab2, scenario_tab3],
                ["conservative", "base", "aggressive"]
            ):
                with tab:
                    scenario_result = results[scenario_name]
                    
                    # Metrics
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Enterprise Value", format_financial_number(scenario_result['enterprise_value']))
                        st.metric("Equity Value", format_financial_number(scenario_result['equity_value']))
                    
                    with col2:
                        st.metric("PV of Cash Flows", format_financial_number(scenario_result['pv_cash_flows']))
                        st.metric("PV of Terminal Value", format_financial_number(scenario_result['pv_terminal_value']))
                    
                    with col3:
                        assumptions = scenario_result['assumptions']
                        st.metric("Discount Rate (WACC)", f"{assumptions.discount_rate*100:.1f}%")
                        st.metric("Terminal Growth", f"{assumptions.terminal_growth_rate*100:.1f}%")
                    
                    # Charts
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.plotly_chart(
                            visualizer.plot_dcf_breakdown(scenario_result, scenario_name),
                            use_container_width=True
                        )
                    
                    with col2:
                        st.plotly_chart(
                            visualizer.plot_dcf_projections(scenario_result, scenario_name),
                            use_container_width=True
                        )
                    
                    # Projections table
                    st.subheader("Cash Flow Projections")
                    projections = scenario_result['projections'].copy()
                    
                    # Format ALL numeric columns with adaptive scaling (not hardcoded to billions)
                    from format_helpers import format_financial_number
                    numeric_cols = ["Revenue", "EBIT", "Tax", "NOPAT", "Depreciation", "Capex", "NWC_Change", "Free_Cash_Flow"]
                    for col in numeric_cols:
                        if col in projections.columns:
                            projections[col] = projections[col].apply(format_financial_number)
                    
                    smart_dataframe(projections, title=None, height=300, key=f"dcf_projections_{scenario_name}")
            
            # Sensitivity Analysis
            if show_sensitivity:
                st.markdown("---")
                st.markdown(f"### {icon('clipboard-data')} Sensitivity Analysis", unsafe_allow_html=True)
                
                with st.spinner("Running sensitivity analysis..."):
                    model = DCFModel(st.session_state.financials)
                    sensitivity_df = model.sensitivity_analysis(scenario="base")
                    
                    st.plotly_chart(
                        visualizer.plot_sensitivity_heatmap(sensitivity_df, st.session_state.ticker),
                        use_container_width=True
                    )
            
            # ==========================================
            # REVERSE-DCF (EXPECTATIONS INVESTING)
            # ==========================================
            st.markdown("---")
            st.markdown(f"### {icon('arrow-repeat')} Reverse-DCF: What the Market is Pricing In", unsafe_allow_html=True)
            st.info("ℹ This analysis reverse-engineers the DCF model to determine what growth rate and margins the current market price implies.")
            
            try:
                from reverse_dcf import analyze_reverse_dcf
                
                # Get current market price (check if available)
                market_data = st.session_state.financials.get('market_data', {})
                current_price = market_data.get('current_price')
                
                if current_price:
                    with st.spinner("Running Reverse-DCF analysis..."):
                        reverse_results = analyze_reverse_dcf(st.session_state.financials)
                        
                        method1 = reverse_results.get('method_1_growth_only', {})
                        method2 = reverse_results.get('method_2_growth_and_margin', {})
                        
                        # Check if Method 1 succeeded
                        if method1.get('status') == 'success':
                            # Display implied growth rate
                            st.markdown(f"### {icon('graph-up-arrow', '1.2em')} Implied Growth Rate (Method 1)", unsafe_allow_html=True)
                            
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.metric(
                                    "Implied Growth Rate",
                                    f"{method1['implied_growth_rate']*100:.2f}%",
                                    help="Growth rate the market is currently pricing in"
                                )
                            
                            with col2:
                                st.metric(
                                    "Calculation Error",
                                    f"{method1['error_pct']*100:.4f}%",
                                    help="How close the reverse calculation matches actual price"
                                )
                            
                            with col3:
                                historical_growth = st.session_state.financials.get('historical_growth_rate', 0.05)
                                growth_diff = (method1['implied_growth_rate'] - historical_growth) * 100
                                st.metric(
                                    "vs Historical Growth",
                                    f"{growth_diff:+.1f}%",
                                    help="Difference from historical growth rate"
                                )
                            
                            # Interpretation
                            implied_growth = method1['implied_growth_rate'] * 100
                            if implied_growth > 15:
                                interpretation = f"**High Growth Expected:** Market is pricing in {implied_growth:.1f}% annual growth - expecting significant expansion."
                            elif implied_growth > 8:
                                interpretation = f"**Moderate Growth Expected:** Market expects {implied_growth:.1f}% annual growth - solid growth trajectory."
                            elif implied_growth > 3:
                                interpretation = f"**Steady Growth Expected:** Market pricing in {implied_growth:.1f}% growth - stable performance anticipated."
                            else:
                                interpretation = f"**Low Growth Expected:** Market expects only {implied_growth:.1f}% growth - limited expansion priced in."
                            
                            st.markdown(interpretation)
                            
                            # Method 2: Growth + Margin
                            if method2.get('status') == 'success':
                                st.markdown(f"### {icon('bullseye', '1.2em')} Implied Growth + Operating Margin (Method 2)", unsafe_allow_html=True)
                                
                                col1, col2, col3 = st.columns(3)
                                
                                with col1:
                                    st.metric(
                                        "Implied Growth Rate",
                                        f"{method2['implied_growth_rate']*100:.2f}%"
                                    )
                                
                                with col2:
                                    st.metric(
                                        "Implied Operating Margin",
                                        f"{method2['implied_operating_margin']*100:.2f}%"
                                    )
                                
                                with col3:
                                    current_margin = method2.get('current_margin', 0) * 100
                                    st.metric(
                                        "Current Margin",
                                        f"{current_margin:.2f}%",
                                        help="Company's current operating margin"
                                    )
                        
                        else:
                            st.warning(f"Reverse-DCF analysis unavailable: {method1.get('message', 'Insufficient data for analysis')}")
                else:
                    st.warning("Current market price not available for Reverse-DCF analysis")
                    
            except Exception as e:
                st.error(f"Error running Reverse-DCF: {str(e)}")
            
            # ==========================================
            # ANALYST RATINGS & PRICE TARGETS
            # ==========================================
            st.markdown("---")
            st.markdown(f"### {icon('person-badge')} Wall Street Analyst Ratings", unsafe_allow_html=True)
            st.info("ℹ Consensus recommendations and price targets from Wall Street analysts.")
            
            try:
                from analyst_ratings import get_analyst_ratings
                
                with st.spinner("Fetching analyst ratings..."):
                    ratings_data = get_analyst_ratings(st.session_state.ticker)
                    
                    if ratings_data['status'] == 'success':
                        # Top-level metrics
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric(
                                "Consensus Rating",
                                ratings_data['consensus_rating'],
                                help="Overall analyst consensus"
                            )
                        
                        with col2:
                            if ratings_data['total_analysts']:
                                st.metric(
                                    "Number of Analysts",
                                    ratings_data['total_analysts'],
                                    help="Total analyst coverage"
                                )
                        
                        with col3:
                            if ratings_data['price_target']['mean']:
                                st.metric(
                                    "Price Target",
                                    f"${ratings_data['price_target']['mean']:.2f}",
                                    help="Mean analyst price target"
                                )
                        
                        with col4:
                            if ratings_data['price_target']['upside_pct'] is not None:
                                upside = ratings_data['price_target']['upside_pct']
                                st.metric(
                                    "Implied Upside",
                                    f"{upside:+.1f}%",
                                    delta=f"{upside:.1f}%",
                                    help="Upside to mean price target"
                                )
                        
                        # Price target range
                        if ratings_data['price_target']['high'] and ratings_data['price_target']['low']:
                            st.markdown(f"### {icon('bullseye', '1.2em')} Price Target Range", unsafe_allow_html=True)
                            
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.metric("Low Target", f"${ratings_data['price_target']['low']:.2f}")
                            
                            with col2:
                                if ratings_data['price_target']['median']:
                                    st.metric("Median Target", f"${ratings_data['price_target']['median']:.2f}")
                            
                            with col3:
                                st.metric("High Target", f"${ratings_data['price_target']['high']:.2f}")
                        
                        # Rating distribution
                        st.markdown(f"### {icon('bar-chart-line', '1.2em')} Rating Distribution", unsafe_allow_html=True)
                        
                        dist = ratings_data['rating_distribution']
                        col1, col2, col3, col4, col5 = st.columns(5)
                        
                        with col1:
                            st.metric("Strong Buy", dist['strongBuy'], help="Strong Buy recommendations")
                        
                        with col2:
                            st.metric("Buy", dist['buy'], help="Buy recommendations")
                        
                        with col3:
                            st.metric("Hold", dist['hold'], help="Hold recommendations")
                        
                        with col4:
                            st.metric("Sell", dist['sell'], help="Sell recommendations")
                        
                        with col5:
                            st.metric("Strong Sell", dist['strongSell'], help="Strong Sell recommendations")
                        
                        # Interpretation
                        total_positive = dist['strongBuy'] + dist['buy']
                        total_negative = dist['sell'] + dist['strongSell']
                        total_all = sum(dist.values())
                        
                        if total_all > 0:
                            positive_pct = (total_positive / total_all) * 100
                            
                            if positive_pct >= 70:
                                sentiment = f"**Bullish Sentiment:** {positive_pct:.0f}% of analysts recommend buying - strong positive consensus."
                            elif positive_pct >= 50:
                                sentiment = f"**Moderately Bullish:** {positive_pct:.0f}% positive recommendations - cautiously optimistic."
                            elif positive_pct >= 30:
                                sentiment = f"**Mixed Sentiment:** {positive_pct:.0f}% positive vs {(total_negative/total_all)*100:.0f}% negative - divided opinion."
                            else:
                                sentiment = f"**Bearish Sentiment:** Only {positive_pct:.0f}% positive recommendations - analysts are cautious."
                            
                            st.markdown(sentiment)
                    
                    else:
                        st.warning(f"Analyst ratings unavailable: {ratings_data.get('message', 'Unknown error')}")
                        
            except Exception as e:
                st.error(f"Error fetching analyst ratings: {str(e)}")
        
        else:
            st.info("Click 'Run 3-Scenario DCF Analysis' to generate valuation")
        
        # ==========================================
        # SUB-TAB 2: LIVE SCENARIO BUILDER (New!)
        # ==========================================
        with dcf_tab2:
            try:
                from live_dcf_modeling import render_live_dcf_modeling
                
                # Initialize DCF model
                model = DCFModel(st.session_state.financials)
                
                # Render live modeling interface
                render_live_dcf_modeling(st.session_state.financials, model)
                
            except Exception as e:
                st.error(f"Live modeling error: {e}")
                st.info("Make sure dcf_modeling.py and live_dcf_modeling.py are available")
    
    # ==========================================
    # OLD TAB 7: TECHNICAL ANALYSIS - MOVED TO TAB 6 SUB-TAB
    # ==========================================
    
    # technical_tab = tab7 if has_quant else tab6
    
    if False:  # Disabled - moved to tab6
        st.markdown(f"## {icon('graph-up-arrow', '1.5em')} Technical Analysis", unsafe_allow_html=True)
        
        st.info("ℹ Comprehensive technical indicators and trading signals based on price action and volume.")
        
        try:
            from technical_analysis import analyze_technical
            
            # Get historical price data
            market_data = st.session_state.financials.get("market_data", {})
            historical_prices = market_data.get("historical_prices", pd.DataFrame())
            
            if not historical_prices.empty:
                with st.spinner("Running technical analysis..."):
                    tech_signals = analyze_technical(historical_prices)
                    
                    # Current Price
                    st.metric("Current Price", f"${tech_signals['price']:.2f}")
                    
                    st.markdown("---")
                    
                    # Overall Signal
                    overall = tech_signals['overall_signal']
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        signal_colors = {
                            'Strong Buy': '<span style="background: #28a745; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold;">●</span>',
                            'Buy': '<span style="background: #7cb342; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold;">●</span>',
                            'Hold': '<span style="background: #9e9e9e; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold;">●</span>',
                            'Sell': '<span style="background: #ef5350; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold;">●</span>',
                            'Strong Sell': '<span style="background: #d32f2f; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold;">●</span>'
                        }
                        signal_icon = signal_colors.get(overall['signal'], '<span style="background: #9e9e9e; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold;">●</span>')
                        
                        st.markdown(f"### {signal_icon} {overall['signal']}", unsafe_allow_html=True)
                        st.metric("Signal Score", f"{overall['score']}/8")
                    
                    with col2:
                        st.markdown("**Key Factors:**")
                        for factor in overall['factors']:
                            st.write(f"• {factor}")
                    
                    st.markdown("---")
                    
                    # Moving Averages
                    st.markdown(f"### {icon('bar-chart-line')} Moving Averages", unsafe_allow_html=True)
                    ma = tech_signals['moving_averages']
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("SMA 20", f"${ma['sma_20']:.2f}", 
                                 help=f"Price is {ma['price_vs_sma20']} 20-day SMA")
                    
                    with col2:
                        st.metric("SMA 50", f"${ma['sma_50']:.2f}",
                                 help=f"Price is {ma['price_vs_sma50']} 50-day SMA")
                    
                    with col3:
                        st.metric("SMA 200", f"${ma['sma_200']:.2f}",
                                 help=f"Price is {ma['price_vs_sma200']} 200-day SMA")
                    
                    # Golden/Death Cross
                    if ma['golden_cross']:
                        st.success("Golden Cross: 50-day SMA above 200-day SMA (Bullish)")
                    else:
                        st.warning("Death Cross: 50-day SMA below 200-day SMA (Bearish)")
                    
                    st.markdown("---")
                    
                    # Momentum Indicators
                    st.markdown(f"### {icon('lightning-charge')} Momentum Indicators", unsafe_allow_html=True)
                    mom = tech_signals['momentum']
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**RSI (Relative Strength Index)**")
                        st.metric("RSI", f"{mom['rsi']:.2f}", help="14-period RSI")
                        st.caption(mom['rsi_signal'])
                        
                        # RSI gauge
                        if mom['rsi'] >= 70:
                            st.error("Overbought Territory")
                        elif mom['rsi'] <= 30:
                            st.success("Oversold Territory (Opportunity)")
                        else:
                            st.info("ℹ Neutral Zone")
                    
                    with col2:
                        st.markdown("**MACD (Moving Average Convergence Divergence)**")
                        st.metric("MACD Line", f"{mom['macd']:.4f}")
                        st.metric("Signal Line", f"{mom['macd_signal']:.4f}")
                        st.metric("Histogram", f"{mom['macd_histogram']:.4f}")
                        
                        if mom['macd_crossover'] == 'Bullish':
                            st.success("Bullish Crossover")
                        else:
                            st.warning("Bearish Crossover")
                    
                    st.markdown("---")
                    
                    # Volatility & Volume
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"### {icon('bar-chart-line')} Volatility", unsafe_allow_html=True)
                        vol = tech_signals['volatility']
                        st.metric("ATR (Average True Range)", f"${vol['atr']:.2f}")
                        st.metric("ATR %", f"{vol['atr_pct']:.2f}%", 
                                 help="ATR as percentage of price")
                        st.caption(f"Bollinger Position: {vol['bb_position']}")
                    
                    with col2:
                        st.markdown(f"### {icon('graph-up')} Volume Analysis", unsafe_allow_html=True)
                        v = tech_signals['volume']
                        st.metric("Current Volume", f"{v['current']:,.0f}")
                        st.metric("20-day Avg Volume", f"{v['sma_20']:,.0f}")
                        
                        if v['relative'] == 'High':
                            st.success("High Volume (Strong interest)")
                        elif v['relative'] == 'Low':
                            st.warning("Low Volume (Weak interest)")
                        else:
                            st.info("ℹ Normal Volume")
                    
                    st.markdown("---")
                    
                    # Support & Resistance
                    st.markdown(f"### {icon('bullseye')} Support & Resistance Levels", unsafe_allow_html=True)
                    levels = tech_signals['levels']
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Resistance Levels:**")
                        for r in levels['resistance']:
                            st.markdown(f"{icon('geo-alt', '1em')} ${r:.2f}", unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown("**Support Levels:**")
                        for s in levels['support']:
                            st.markdown(f"{icon('geo-alt', '1em')} ${s:.2f}", unsafe_allow_html=True)
            
            else:
                st.warning("No historical price data available for technical analysis")
                
        except Exception as e:
            st.error(f"Error running technical analysis: {str(e)}")
    
    # ==========================================
    # OLD TAB 9: FORENSIC SHIELD - MOVED TO TAB 5 SUB-TAB
    # ==========================================
    
    # forensic_tab = tab9 if has_quant else tab8
    
    if False:  # Disabled - moved to tab5
        st.markdown(f"## {icon('shield-check', '1.5em')} Forensic Shield: Risk Assessment", unsafe_allow_html=True)
        
        st.info("ℹ Advanced forensic accounting models to detect fraud, bankruptcy risk, and financial quality issues.")
        
        try:
            from forensic_shield import analyze_forensic_shield
            
            with st.spinner("Running forensic analysis..."):
                forensic_results = analyze_forensic_shield(st.session_state.financials)
                
                # Overall Assessment
                overall = forensic_results['overall_assessment']
                
                risk_colors = {
                    'LOW': '<span style="background: #28a745; color: white; padding: 6px 12px; border-radius: 4px; font-weight: bold;">●</span>',
                    'MODERATE': '<span style="background: #ff9800; color: white; padding: 6px 12px; border-radius: 4px; font-weight: bold;">●</span>',
                    'HIGH': '<span style="background: #d32f2f; color: white; padding: 6px 12px; border-radius: 4px; font-weight: bold;">●</span>'
                }
                
                st.markdown(f"## {risk_colors.get(overall['risk_level'], '<span style=\"background: #9e9e9e; color: white; padding: 6px 12px; border-radius: 4px; font-weight: bold;\">●</span>')} Overall Risk: {overall['risk_level']}", unsafe_allow_html=True)
                st.markdown(f"**Summary:** {overall['summary']}")
                
                if overall.get('risk_factors'):
                    st.warning("**Risk Factors Identified:**")
                    for factor in overall['risk_factors']:
                        st.write(f"• {factor}")
                
                st.markdown("---")
                
                # Altman Z-Score
                st.markdown(f"### {icon('bar-chart-line')} Altman Z-Score (Bankruptcy Risk)", unsafe_allow_html=True)
                altman = forensic_results['altman_z_score']
                
                if altman['status'] == 'success':
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Z-Score", f"{altman['z_score']:.2f}")
                    
                    with col2:
                        st.metric("Zone", altman['zone'])
                    
                    with col3:
                        st.metric("Risk Level", altman['risk_level'])
                    
                    st.info(f"**Interpretation:** {altman['interpretation']}")
                    
                    with st.expander("View Z-Score Components"):
                        comp_df = pd.DataFrame([altman['components']])
                        smart_dataframe(comp_df.T, title=None, height=200, key="zscore_components")
                else:
                    st.warning(f"Altman Z-Score: {altman.get('message', 'Unavailable')}")
                
                st.markdown("---")
                
                # Beneish M-Score
                st.markdown(f"### {icon('search')} Beneish M-Score (Earnings Manipulation)", unsafe_allow_html=True)
                beneish = forensic_results['beneish_m_score']
                
                if beneish['status'] == 'success':
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.metric("M-Score", f"{beneish['m_score']:.4f}")
                    
                    with col2:
                        st.metric("Risk Level", beneish['risk_level'])
                    
                    st.info(f"**Interpretation:** {beneish['interpretation']}")
                    
                    if beneish.get('warning'):
                        st.warning(f"{beneish['warning']}")
                    
                    if beneish.get('red_flags'):
                        st.markdown("""
                        <div style='padding: 1rem; background: rgba(244, 67, 54, 0.08); 
                                    border: 1px solid rgba(244, 67, 54, 0.3); border-left: 4px solid #F44336;
                                    border-radius: 8px; margin: 1rem 0;'>
                            <p style='color: #ff5252; font-weight: 700; margin: 0 0 0.5rem 0; font-size: 1.1rem;'>
                                ⚠️ Red Flags Detected
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                        for flag in beneish['red_flags']:
                            st.markdown(f"""
                            <div style='padding: 0.6rem 1rem; margin: 0.4rem 0 0.4rem 1.5rem; 
                                        background: rgba(244, 67, 54, 0.04); 
                                        border-left: 3px solid rgba(244, 67, 54, 0.5); 
                                        border-radius: 4px;'>
                                <p style='color: #ffcdd2; margin: 0; font-size: 0.95rem;'>• {flag}</p>
                            </div>
                            """, unsafe_allow_html=True)
                    
                    with st.expander("View M-Score Components"):
                        comp_df = pd.DataFrame([beneish['components']])
                        smart_dataframe(comp_df.T, title=None, height=200, key="mscore_components")
                else:
                    st.warning(f"Beneish M-Score: {beneish.get('message', 'Unavailable')}")
                
                st.markdown("---")
                
                # Piotroski F-Score
                st.markdown(f"### {icon('star-fill')} Piotroski F-Score (Financial Quality)", unsafe_allow_html=True)
                piotroski = forensic_results['piotroski_f_score']
                
                if piotroski['status'] == 'success':
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.metric("F-Score", f"{piotroski['f_score']}/{piotroski['max_score']}")
                    
                    with col2:
                        st.metric("Quality", piotroski['quality'])
                    
                    st.info(f"**Interpretation:** {piotroski['interpretation']}")
                    
                    st.markdown("""
                    <div style='padding: 0.8rem 1rem; margin: 1rem 0; 
                                background: #1e2530;
                                border: 1px solid rgba(59, 130, 246, 0.2); border-radius: 8px;'>
                        <p style='color: #3b82f6; font-weight: 700; margin: 0 0 0.8rem 0; font-size: 1rem;'>
                            Breakdown
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    for test, passed in piotroski['breakdown'].items():
                        if passed:
                            st.markdown(f"""
                            <div style='padding: 0.5rem 1rem; margin: 0.3rem 0; 
                                        background: rgba(76, 175, 80, 0.08); 
                                        border-left: 3px solid #4CAF50; border-radius: 4px;'>
                                <p style='color: #81c784; margin: 0;'><strong>✓</strong> {test}</p>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown(f"""
                            <div style='padding: 0.5rem 1rem; margin: 0.3rem 0; 
                                        background: rgba(244, 67, 54, 0.08); 
                                        border-left: 3px solid #F44336; border-radius: 4px;'>
                                <p style='color: #e57373; margin: 0;'><strong>✗</strong> {test}</p>
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.warning(f"Piotroski F-Score: {piotroski.get('message', 'Unavailable')}")
                    
        except Exception as e:
            st.error(f"Error running forensic analysis: {str(e)}")
    
    # ==========================================
    # OLD TAB 10: OWNERSHIP & GOVERNANCE - MOVED TO TAB 5 SUB-TAB
    # ==========================================
    
    # ownership_tab = tab10 if has_quant else tab9
    
    if False:  # Disabled - moved to tab5
        render_governance_tab(st.session_state.ticker, st.session_state.financials)
    
    # ==========================================
    # OLD TAB 11: OPTIONS FLOW - WILL BE MOVED TO TAB 6 SUB-TAB
    # ==========================================
    
    # options_tab = tab11 if has_quant else tab10
    
    if False:  # Disabled - will be moved to tab6
        st.markdown(f"## {icon('bar-chart-line', '1.5em')} Options Flow Analysis", unsafe_allow_html=True)
        
        st.info("ℹ Analyze options market sentiment through Put/Call ratio, implied volatility, and volume patterns.")
        
        try:
            from options_flow import get_options_data
            
            with st.spinner("Fetching options data..."):
                options_data = get_options_data(st.session_state.ticker)
                
                if options_data['status'] == 'success':
                    # Current Price & Expiration
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.metric("Current Price", f"${options_data['current_price']:.2f}")
                    
                    with col2:
                        st.metric("Next Expiration", options_data['expiration_date'])
                    
                    st.markdown("---")
                    
                    # Sentiment
                    sentiment_colors = {
                        'Bullish': '<span style="background: #28a745; color: white; padding: 6px 12px; border-radius: 4px; font-weight: bold;">●</span>',
                        'Slightly Bullish': '<span style="background: #7cb342; color: white; padding: 6px 12px; border-radius: 4px; font-weight: bold;">●</span>',
                        'Neutral': '<span style="background: #9e9e9e; color: white; padding: 6px 12px; border-radius: 4px; font-weight: bold;">●</span>',
                        'Slightly Bearish': '<span style="background: #ef5350; color: white; padding: 6px 12px; border-radius: 4px; font-weight: bold;">●</span>',
                        'Bearish': '<span style="background: #d32f2f; color: white; padding: 6px 12px; border-radius: 4px; font-weight: bold;">●</span>'
                    }
                    
                    st.markdown(f"## {sentiment_colors.get(options_data['sentiment'], '<span style=\"background: #9e9e9e; color: white; padding: 6px 12px; border-radius: 4px; font-weight: bold;\">●</span>')} Market Sentiment: {options_data['sentiment']}", unsafe_allow_html=True)
                    st.caption(options_data['sentiment_description'])
                    
                    st.markdown("---")
                    
                    # Put/Call Ratio
                    st.markdown(f"### {icon('bar-chart-line', '1.2em')} Put/Call Ratio", unsafe_allow_html=True)
                    pcr = options_data['put_call_ratio']
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.metric("Volume-Based P/C", f"{pcr['volume_based']:.2f}",
                                 help="Ratio of put volume to call volume")
                    
                    with col2:
                        st.metric("Open Interest P/C", f"{pcr['oi_based']:.2f}",
                                 help="Ratio of put OI to call OI")
                    
                    st.markdown(f'<small style="color: gray;">📌 P/C < 0.7: Bullish | 0.7-1.0: Slightly Bullish | 1.0-1.3: Neutral | >1.3: Bearish</small>', unsafe_allow_html=True)
                    
                    st.markdown("---")
                    
                    # Implied Volatility
                    st.markdown(f"### {icon('graph-up-arrow')} Implied Volatility", unsafe_allow_html=True)
                    iv = options_data['implied_volatility']
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Overall IV", f"{iv['overall']*100:.2f}%")
                    
                    with col2:
                        st.metric("Call IV", f"{iv['calls']*100:.2f}%")
                    
                    with col3:
                        st.metric("Put IV", f"{iv['puts']*100:.2f}%")
                    
                    st.markdown("---")
                    
                    # Volume Analysis
                    st.markdown(f"### {icon('bar-chart-line')} Volume & Open Interest", unsafe_allow_html=True)
                    
                    vol = options_data['volume']
                    oi = options_data['open_interest']
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Total Volume:**")
                        st.metric("Calls", f"{vol['total_calls']:,.0f}")
                        st.metric("Puts", f"{vol['total_puts']:,.0f}")
                    
                    with col2:
                        st.markdown("**Open Interest:**")
                        st.metric("Calls", f"{oi['total_calls']:,.0f}")
                        st.metric("Puts", f"{oi['total_puts']:,.0f}")
                    
                    st.markdown("---")
                    
                    # Most Active Options
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"### {icon('fire')} Most Active Calls", unsafe_allow_html=True)
                        smart_dataframe(options_data['most_active']['calls'], title=None, height=300, key="options_calls_1")
                    
                    with col2:
                        st.markdown(f"### {icon('fire')} Most Active Puts", unsafe_allow_html=True)
                        smart_dataframe(options_data['most_active']['puts'], title=None, height=300, key="options_puts_1")
                else:
                    st.warning(options_data['message'])
                    
        except Exception as e:
            st.error(f"Error fetching options data: {str(e)}")
    
    # ==========================================
    # OLD TAB 12: NEWS & SENTIMENT - WILL BE TAB 7
    # ==========================================
    
    # news_tab = tab12 if has_quant else tab11
    
    if False:  # Disabled - will be tab7
        st.markdown(f"## {icon('newspaper', '1.5em')} Recent News & Market Sentiment", unsafe_allow_html=True)
        
        st.info("Multi-source news aggregation with sentiment analysis")
        
        # Toggle for NewsAPI (paid)
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown("### News Sources")
        
        with col2:
            use_newsapi = st.checkbox(
                "Use NewsAPI",
                value=False,
                help="Enable NewsAPI for 30,000+ premium sources (requires API key). Leave unchecked for free RSS feeds."
            )
        
        if use_newsapi:
            st.caption("NewsAPI enabled (paid/limited free tier - 100 requests/day)")
        else:
            st.caption("🆓 Using free RSS feeds (Yahoo Finance + Google News)")
        
        st.markdown("---")
        
        try:
            from news_analysis import get_ticker_news
            
            with st.spinner("Fetching latest news..."):
                news_data = get_ticker_news(st.session_state.ticker, use_newsapi=use_newsapi)
                
                if news_data['status'] == 'success':
                    summary = news_data['summary']
                    
                    # Display API warning if present
                    if 'api_warning' in news_data:
                        st.warning(f"{news_data['api_warning']}")
                    
                    # Summary metrics
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Total Articles", summary['total_articles'])
                    
                    with col2:
                        st.metric("News Sources", summary['sources'])
                    
                    with col3:
                        sentiment = news_data.get('overall_sentiment', 'Neutral')
                        sentiment_color = news_data.get('sentiment_color', 'gray')
                        st.metric("Sentiment", sentiment)
                    
                    with col4:
                        st.metric("Positive Articles", f"{summary['positive_articles']}/{summary['total_articles']}")
                    
                    st.markdown("---")
                    
                    # Sentiment breakdown
                    st.markdown(f"### {icon('bar-chart-line', '1.2em')} Sentiment Breakdown", unsafe_allow_html=True)
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.markdown(f"<div style='text-align: center;'><h3 style='color: green;'>{summary['positive_articles']}</h3><p>Positive</p></div>", unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown(f"<div style='text-align: center;'><h3 style='color: gray;'>{summary['neutral_articles']}</h3><p>Neutral</p></div>", unsafe_allow_html=True)
                    
                    with col3:
                        st.markdown(f"<div style='text-align: center;'><h3 style='color: red;'>{summary['negative_articles']}</h3><p>Negative</p></div>", unsafe_allow_html=True)
                    
                    st.markdown("---")
                    
                    # Sources used
                    st.markdown(f"### {icon('database', '1.2em')} Sources Used", unsafe_allow_html=True)
                    
                    for source in news_data['sources_used']:
                        if 'Paid' in source:
                            st.markdown(f"• [Premium] {source}")
                        else:
                            st.markdown(f"• 🆓 {source}")
                    
                    st.markdown("---")
                    
                    # Display articles with sentiment tags
                    st.markdown(f"### {icon('list', '1.2em')} Recent Headlines (Latest {min(20, summary['total_articles'])})", unsafe_allow_html=True)
                    
                    for i, article in enumerate(news_data['articles'][:20], 1):
                        with st.container():
                            # Sentiment indicator
                            sentiment_icons = {
                                'Positive': '<span style="background: #28a745; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.8em;">BULLISH</span>',
                                'Negative': '<span style="background: #d32f2f; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.8em;">BEARISH</span>',
                                'Neutral': '<span style="background: #9e9e9e; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.8em;">NEUTRAL</span>'
                            }
                            
                            sentiment_tag = sentiment_icons.get(article.get('sentiment', 'Neutral'), '')
                            
                            col1, col2 = st.columns([5, 2])
                            
                            with col1:
                                st.markdown(f"{sentiment_tag} **{article['title']}**", unsafe_allow_html=True)
                                if article.get('summary'):
                                    st.markdown(f"_{article['summary'][:200]}..._")
                            
                            with col2:
                                st.caption(f"{article['source']}")
                                st.caption(f"{article['published'][:10]}")
                                
                                # Add author if available
                                if article.get('author'):
                                    st.caption(f"✍️ {article['author']}")
                                
                                # Add sentiment confidence if available
                                if article.get('sentiment_score'):
                                    confidence = article['sentiment_score']
                                    st.caption(f"Confidence: {confidence:.0%}")
                                
                                # Add estimated read time based on summary length
                                if article.get('summary'):
                                    word_count = len(article['summary'].split())
                                    read_time = max(1, word_count // 200)
                                    st.caption(f"{read_time} min read")
                            
                            st.markdown(f'<a href="{article["link"]}" target="_blank" rel="noopener noreferrer">Read Full Article →</a>', unsafe_allow_html=True)
                            
                            if i < len(news_data['articles'][:20]):
                                st.markdown("---")
                    
                    # API key setup instructions (if NewsAPI not enabled)
                    if not use_newsapi:
                        with st.expander("How to enable NewsAPI (optional)"):
                            st.markdown("""
                            **To unlock 30,000+ premium news sources:**
                            
                            1. Sign up at <a href="https://newsapi.org/" target="_blank" rel="noopener noreferrer">newsapi.org</a> (free tier: 100 requests/day)
                            2. Get your API key
                            3. Set environment variable: `NEWSAPI_KEY=your_key_here`
                            4. Check the "Use NewsAPI" box above
                            
                            **Note:** Free tier is limited. For production use, consider the paid plan ($449/month for developer tier).
                            """)
                
                else:
                    st.error(f"{news_data.get('message', 'Failed to fetch news')}")
        
        except Exception as e:
            st.error(f"Error fetching news: {str(e)}")
            st.caption("Tip: Make sure you have internet connection and RSS feeds are accessible.")
    
    
    # ==========================================
    # OLD TAB 6: VISUALIZE - KEEPING AS STANDALONE OR MERGE LATER
    # ==========================================
    
    # visualize_tab = tab6 if has_quant else tab5
    
    if False:  # Disabled temporarily
        st.markdown(f"## {icon('graph-up', '1.5em')} Interactive Visualizations", unsafe_allow_html=True)
        
        # Chart selection
        chart_options = [
            "Revenue Trend",
            "Margin Waterfall",
            "Profitability Trends",
            "Balance Sheet Structure",
            "Cash Flow Trends"
        ]
        
        selected_charts = st.multiselect(
            "Select Charts to Display",
            options=chart_options,
            default=["Revenue Trend", "Margin Waterfall", "Profitability Trends"]
        )
        
        st.markdown("---")
        
        # Generate selected charts
        for chart_name in selected_charts:
            if chart_name == "Revenue Trend":
                st.plotly_chart(
                    visualizer.plot_revenue_trend(st.session_state.financials),
                    use_container_width=True
                )
            
            elif chart_name == "Margin Waterfall":
                st.plotly_chart(
                    visualizer.plot_margin_analysis(st.session_state.financials),
                    use_container_width=True
                )
            
            elif chart_name == "Profitability Trends":
                st.plotly_chart(
                    visualizer.plot_profitability_trends(st.session_state.financials),
                    use_container_width=True
                )
            
            elif chart_name == "Balance Sheet Structure":
                st.plotly_chart(
                    visualizer.plot_balance_sheet_structure(st.session_state.financials),
                    use_container_width=True
                )
            
            elif chart_name == "Cash Flow Trends":
                st.plotly_chart(
                    visualizer.plot_cash_flow_trends(st.session_state.financials),
                    use_container_width=True
                )
    
    # ==========================================
    # OLD TAB 8: COMPARE - WILL BE MOVED TO TAB 6 SUB-TAB
    # ==========================================
    
    # compare_tab = tab8 if has_quant else tab7
    
    if False:  # Disabled - will be moved to tab6
        render_compare_tab(st.session_state.ticker, st.session_state.financials, extractor, visualizer)
    
    # ==========================================
    # OLD TAB 5: QUANT ANALYSIS - WILL BE MOVED TO TAB 6 SUB-TAB
    # ==========================================
    
    # if has_quant:
    #     with tab5:
    #         render_quant_tab(st.session_state.ticker, st.session_state.financials)

    # ==========================================
    # TAB 5: RISK & OWNERSHIP - Forensic + Governance
    # ==========================================
    
    with tab5:
        risk_sub1, risk_sub2 = st.tabs(["Forensic Shield", "Corporate Governance"])
        
        # Sub-tab 1: Forensic Analysis
        with risk_sub1:
            st.markdown(f"## {icon('shield-check', '1.5em')} Forensic Shield: Risk Assessment", unsafe_allow_html=True)
            
            st.info("Advanced forensic accounting models to detect fraud, bankruptcy risk, and financial quality issues.")
            
            try:
                from forensic_shield import analyze_forensic_shield
                
                with st.spinner("Running forensic analysis..."):
                    forensic_results = analyze_forensic_shield(st.session_state.financials)
                    
                    # Overall Assessment
                    overall = forensic_results['overall_assessment']
                    
                    risk_colors = {
                        'LOW': '<span style="background: #28a745; color: white; padding: 6px 12px; border-radius: 4px; font-weight: bold;">●</span>',
                        'MODERATE': '<span style="background: #ff9800; color: white; padding: 6px 12px; border-radius: 4px; font-weight: bold;">●</span>',
                        'HIGH': '<span style="background: #d32f2f; color: white; padding: 6px 12px; border-radius: 4px; font-weight: bold;">●</span>'
                    }
                    
                    st.markdown(f"## {risk_colors.get(overall['risk_level'], '<span style=\"background: #9e9e9e; color: white; padding: 6px 12px; border-radius: 4px; font-weight: bold;\">●</span>')} Overall Risk: {overall['risk_level']}", unsafe_allow_html=True)
                    st.markdown(f"**Summary:** {overall['summary']}")
                    
                    if overall.get('risk_factors'):
                        st.warning("**Risk Factors Identified:**")
                        for factor in overall['risk_factors']:
                            st.write(f"• {factor}")
                    
                    st.markdown("---")
                    
                    # Altman Z-Score
                    st.markdown(f"### {icon('bar-chart-line')} Altman Z-Score (Bankruptcy Risk)", unsafe_allow_html=True)
                    altman = forensic_results['altman_z_score']
                    
                    if altman['status'] == 'success':
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Z-Score", f"{altman['z_score']:.2f}")
                        
                        with col2:
                            st.metric("Zone", altman['zone'])
                        
                        with col3:
                            st.metric("Risk Level", altman['risk_level'])
                        
                        st.info(f"**Interpretation:** {altman['interpretation']}")
                        
                        with st.expander("View Z-Score Components"):
                            comp_df = pd.DataFrame([altman['components']])
                            smart_dataframe(comp_df.T, title=None, height=200, key="zscore_components_2")
                    else:
                        st.warning(f"Altman Z-Score: {altman.get('message', 'Unavailable')}")
                    
                    st.markdown("---")
                    
                    # Beneish M-Score
                    st.markdown(f"### {icon('search')} Beneish M-Score (Earnings Manipulation)", unsafe_allow_html=True)
                    beneish = forensic_results['beneish_m_score']
                    
                    if beneish['status'] == 'success':
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.metric("M-Score", f"{beneish['m_score']:.4f}")
                        
                        with col2:
                            st.metric("Risk Level", beneish['risk_level'])
                        
                        st.info(f"**Interpretation:** {beneish['interpretation']}")
                        
                        if beneish.get('warning'):
                            st.warning(f"{beneish['warning']}")
                        
                        if beneish.get('red_flags'):
                            st.markdown("""
                            <div style='padding: 1rem; background: rgba(244, 67, 54, 0.08); 
                                        border: 1px solid rgba(244, 67, 54, 0.3); border-left: 4px solid #F44336;
                                        border-radius: 8px; margin: 1rem 0;'>
                                <p style='color: #ff5252; font-weight: 700; margin: 0 0 0.5rem 0; font-size: 1.1rem;'>
                                    ⚠️ Red Flags Detected
                                </p>
                            </div>
                            """, unsafe_allow_html=True)
                            for flag in beneish['red_flags']:
                                st.markdown(f"""
                                <div style='padding: 0.6rem 1rem; margin: 0.4rem 0 0.4rem 1.5rem; 
                                            background: rgba(244, 67, 54, 0.04); 
                                            border-left: 3px solid rgba(244, 67, 54, 0.5); 
                                            border-radius: 4px;'>
                                    <p style='color: #ffcdd2; margin: 0; font-size: 0.95rem;'>• {flag}</p>
                                </div>
                                """, unsafe_allow_html=True)
                        
                        with st.expander("View M-Score Components"):
                            comp_df = pd.DataFrame([beneish['components']])
                            smart_dataframe(comp_df.T, title=None, height=200, key="mscore_components_2")
                    else:
                        st.warning(f"Beneish M-Score: {beneish.get('message', 'Unavailable')}")
                    
                    st.markdown("---")
                    
                    # Piotroski F-Score
                    st.markdown(f"### {icon('star-fill')} Piotroski F-Score (Financial Quality)", unsafe_allow_html=True)
                    piotroski = forensic_results['piotroski_f_score']
                    
                    if piotroski['status'] == 'success':
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.metric("F-Score", f"{piotroski['f_score']}/{piotroski['max_score']}")
                        
                        with col2:
                            st.metric("Quality", piotroski['quality'])
                        
                        st.info(f"**Interpretation:** {piotroski['interpretation']}")
                        
                        st.markdown("""
                        <div style='padding: 0.8rem 1rem; margin: 1rem 0; 
                                    background: #1e2530;
                                    border: 1px solid rgba(59, 130, 246, 0.2); border-radius: 8px;'>
                            <p style='color: #3b82f6; font-weight: 700; margin: 0 0 0.8rem 0; font-size: 1rem;'>
                                Breakdown
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        for test, passed in piotroski['breakdown'].items():
                            if passed:
                                st.markdown(f"""
                                <div style='padding: 0.5rem 1rem; margin: 0.3rem 0; 
                                            background: rgba(76, 175, 80, 0.08); 
                                            border-left: 3px solid #4CAF50; border-radius: 4px;'>
                                    <p style='color: #81c784; margin: 0;'><strong>✓</strong> {test}</p>
                                </div>
                                """, unsafe_allow_html=True)
                            else:
                                st.markdown(f"""
                                <div style='padding: 0.5rem 1rem; margin: 0.3rem 0; 
                                            background: rgba(244, 67, 54, 0.08); 
                                            border-left: 3px solid #F44336; border-radius: 4px;'>
                                    <p style='color: #e57373; margin: 0;'><strong>✗</strong> {test}</p>
                                </div>
                                """, unsafe_allow_html=True)
                    else:
                        st.warning(f"Piotroski F-Score: {piotroski.get('message', 'Unavailable')}")
                        
            except Exception as e:
                st.error(f"Error running forensic analysis: {str(e)}")
        
        # Sub-tab 2: Corporate Governance
        with risk_sub2:
            render_governance_tab(st.session_state.ticker, st.session_state.financials)
    
    # ==========================================
    # TAB 6: MARKET INTELLIGENCE - Technical + Quant + Options + Compare
    # ==========================================
    
    with tab6:
        if has_quant:
            mkt_sub1, mkt_sub2, mkt_sub3, mkt_sub4 = st.tabs(["Technical", "Quant", "Options", "Peer Compare"])
        else:
            mkt_sub1, mkt_sub3, mkt_sub4 = st.tabs(["Technical", "Options", "Peer Compare"])
        
        # Sub-tab 1: Technical Analysis
        with mkt_sub1:
            st.markdown(f"## {icon('graph-up-arrow', '1.5em')} Technical Analysis", unsafe_allow_html=True)
            
            st.info("ℹ Comprehensive technical indicators and trading signals based on price action and volume.")
            
            try:
                from technical_analysis import analyze_technical
                
                # Get historical price data
                market_data = st.session_state.financials.get("market_data", {})
                historical_prices = market_data.get("historical_prices", pd.DataFrame())
                
                if not historical_prices.empty:
                    with st.spinner("Running technical analysis..."):
                        tech_signals = analyze_technical(historical_prices)
                        
                        # Current Price
                        st.metric("Current Price", f"${tech_signals['price']:.2f}")
                        
                        st.markdown("---")
                        
                        # Overall Signal
                        overall = tech_signals['overall_signal']
                        col1, col2 = st.columns([1, 2])
                        
                        with col1:
                            signal_colors = {
                                'Strong Buy': '<span style="background: #28a745; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold;">●</span>',
                                'Buy': '<span style="background: #7cb342; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold;">●</span>',
                                'Hold': '<span style="background: #9e9e9e; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold;">●</span>',
                                'Sell': '<span style="background: #ef5350; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold;">●</span>',
                                'Strong Sell': '<span style="background: #d32f2f; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold;">●</span>'
                            }
                            signal_icon = signal_colors.get(overall['signal'], '<span style="background: #9e9e9e; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold;">●</span>')
                            
                            st.markdown(f"### {signal_icon} {overall['signal']}", unsafe_allow_html=True)
                            st.metric("Signal Score", f"{overall['score']}/8")
                        
                        with col2:
                            st.markdown("**Key Factors:**")
                            for factor in overall['factors']:
                                st.write(f"• {factor}")
                        
                        st.markdown("---")
                        
                        # Moving Averages
                        st.markdown(f"### {icon('bar-chart-line')} Moving Averages", unsafe_allow_html=True)
                        ma = tech_signals['moving_averages']
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("SMA 20", f"${ma['sma_20']:.2f}", 
                                     help=f"Price is {ma['price_vs_sma20']} 20-day SMA")
                        
                        with col2:
                            st.metric("SMA 50", f"${ma['sma_50']:.2f}",
                                     help=f"Price is {ma['price_vs_sma50']} 50-day SMA")
                        
                        with col3:
                            st.metric("SMA 200", f"${ma['sma_200']:.2f}",
                                     help=f"Price is {ma['price_vs_sma200']} 200-day SMA")
                        
                        # Golden/Death Cross
                        if ma['golden_cross']:
                            st.success("Golden Cross: 50-day SMA above 200-day SMA (Bullish)")
                        else:
                            st.warning("Death Cross: 50-day SMA below 200-day SMA (Bearish)")
                        
                        st.markdown("---")
                        
                        # Momentum Indicators
                        st.markdown(f"### {icon('lightning-charge')} Momentum Indicators", unsafe_allow_html=True)
                        mom = tech_signals['momentum']
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("**RSI (Relative Strength Index)**")
                            st.metric("RSI", f"{mom['rsi']:.2f}", help="14-period RSI")
                            st.caption(mom['rsi_signal'])
                            
                            # RSI gauge
                            if mom['rsi'] >= 70:
                                st.error("Overbought Territory")
                            elif mom['rsi'] <= 30:
                                st.success("Oversold Territory (Opportunity)")
                            else:
                                st.info("ℹ Neutral Zone")
                        
                        with col2:
                            st.markdown("**MACD (Moving Average Convergence Divergence)**")
                            st.metric("MACD Line", f"{mom['macd']:.4f}")
                            st.metric("Signal Line", f"{mom['macd_signal']:.4f}")
                            st.metric("Histogram", f"{mom['macd_histogram']:.4f}")
                            
                            if mom['macd_crossover'] == 'Bullish':
                                st.success("Bullish Crossover")
                            else:
                                st.warning("Bearish Crossover")
                        
                        st.markdown("---")
                        
                        # Volatility & Volume
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown(f"### {icon('bar-chart-line')} Volatility", unsafe_allow_html=True)
                            vol = tech_signals['volatility']
                            st.metric("ATR (Average True Range)", f"${vol['atr']:.2f}")
                            st.metric("ATR %", f"{vol['atr_pct']:.2f}%", 
                                     help="ATR as percentage of price")
                            st.caption(f"Bollinger Position: {vol['bb_position']}")
                        
                        with col2:
                            st.markdown(f"### {icon('graph-up')} Volume Analysis", unsafe_allow_html=True)
                            v = tech_signals['volume']
                            st.metric("Current Volume", f"{v['current']:,.0f}")
                            st.metric("20-day Avg Volume", f"{v['sma_20']:,.0f}")
                            
                            if v['relative'] == 'High':
                                st.success("High Volume (Strong interest)")
                            elif v['relative'] == 'Low':
                                st.warning("Low Volume (Weak interest)")
                            else:
                                st.info("ℹ Normal Volume")
                        
                        st.markdown("---")
                        
                        # Support & Resistance
                        st.markdown(f"### {icon('bullseye')} Support & Resistance Levels", unsafe_allow_html=True)
                        levels = tech_signals['levels']
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("**Resistance Levels:**")
                            for r in levels['resistance']:
                                st.markdown(f"{icon('geo-alt', '1em')} ${r:.2f}", unsafe_allow_html=True)
                        
                        with col2:
                            st.markdown("**Support Levels:**")
                            for s in levels['support']:
                                st.markdown(f"{icon('geo-alt', '1em')} ${s:.2f}", unsafe_allow_html=True)
                
                else:
                    st.warning("No historical price data available for technical analysis")
                    
            except Exception as e:
                st.error(f"Error running technical analysis: {str(e)}")
        
        # Sub-tab 2: Quant (if available)
        if has_quant:
            with mkt_sub2:
                render_quant_tab(st.session_state.ticker, st.session_state.financials)
        
        # Sub-tab 3: Options
        with mkt_sub3:
            st.markdown(f"## {icon('bar-chart-line', '1.5em')} Options Flow Analysis", unsafe_allow_html=True)
            
            st.info("ℹ Analyze options market sentiment through Put/Call ratio, implied volatility, and volume patterns.")
            
            try:
                from options_flow import get_options_data
                
                with st.spinner("Fetching options data..."):
                    options_data = get_options_data(st.session_state.ticker)
                    
                    if options_data['status'] == 'success':
                        # Current Price & Expiration
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.metric("Current Price", f"${options_data['current_price']:.2f}")
                        
                        with col2:
                            st.metric("Next Expiration", options_data['expiration_date'])
                        
                        st.markdown("---")
                        
                        # Sentiment
                        sentiment_colors = {
                            'Bullish': '<span style="background: #28a745; color: white; padding: 6px 12px; border-radius: 4px; font-weight: bold;">●</span>',
                            'Slightly Bullish': '<span style="background: #7cb342; color: white; padding: 6px 12px; border-radius: 4px; font-weight: bold;">●</span>',
                            'Neutral': '<span style="background: #9e9e9e; color: white; padding: 6px 12px; border-radius: 4px; font-weight: bold;">●</span>',
                            'Slightly Bearish': '<span style="background: #ef5350; color: white; padding: 6px 12px; border-radius: 4px; font-weight: bold;">●</span>',
                            'Bearish': '<span style="background: #d32f2f; color: white; padding: 6px 12px; border-radius: 4px; font-weight: bold;">●</span>'
                        }
                        
                        st.markdown(f"## {sentiment_colors.get(options_data['sentiment'], '<span style=\"background: #9e9e9e; color: white; padding: 6px 12px; border-radius: 4px; font-weight: bold;\">●</span>')} Market Sentiment: {options_data['sentiment']}", unsafe_allow_html=True)
                        st.caption(options_data['sentiment_description'])
                        
                        st.markdown("---")
                        
                        # Put/Call Ratio
                        st.markdown(f"### {icon('bar-chart-line', '1.2em')} Put/Call Ratio", unsafe_allow_html=True)
                        pcr = options_data['put_call_ratio']
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.metric("Volume-Based P/C", f"{pcr['volume_based']:.2f}",
                                     help="Ratio of put volume to call volume")
                        
                        with col2:
                            st.metric("Open Interest P/C", f"{pcr['oi_based']:.2f}",
                                     help="Ratio of put OI to call OI")
                        
                        st.markdown(f'<small style="color: gray;">📌 P/C < 0.7: Bullish | 0.7-1.0: Slightly Bullish | 1.0-1.3: Neutral | >1.3: Bearish</small>', unsafe_allow_html=True)
                        
                        st.markdown("---")
                        
                        # Implied Volatility
                        st.markdown(f"### {icon('graph-up-arrow')} Implied Volatility", unsafe_allow_html=True)
                        iv = options_data['implied_volatility']
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Overall IV", f"{iv['overall']*100:.2f}%")
                        
                        with col2:
                            st.metric("Call IV", f"{iv['calls']*100:.2f}%")
                        
                        with col3:
                            st.metric("Put IV", f"{iv['puts']*100:.2f}%")
                        
                        st.markdown("---")
                        
                        # Volume Analysis
                        st.markdown(f"### {icon('bar-chart-line')} Volume & Open Interest", unsafe_allow_html=True)
                        
                        vol = options_data['volume']
                        oi = options_data['open_interest']
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("**Total Volume:**")
                            st.metric("Calls", f"{vol['total_calls']:,.0f}")
                            st.metric("Puts", f"{vol['total_puts']:,.0f}")
                        
                        with col2:
                            st.markdown("**Open Interest:**")
                            st.metric("Calls", f"{oi['total_calls']:,.0f}")
                            st.metric("Puts", f"{oi['total_puts']:,.0f}")
                        
                        st.markdown("---")
                        
                        # Most Active Options
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown(f"### {icon('fire')} Most Active Calls", unsafe_allow_html=True)
                            smart_dataframe(options_data['most_active']['calls'], title=None, height=300, key="options_calls_2")
                        
                        with col2:
                            st.markdown(f"### {icon('fire')} Most Active Puts", unsafe_allow_html=True)
                            smart_dataframe(options_data['most_active']['puts'], title=None, height=300, key="options_puts_2")
                    else:
                        st.warning(options_data['message'])
                        
            except Exception as e:
                st.error(f"Error fetching options data: {str(e)}")
        
        # Sub-tab 4: Peer Comparison
        with mkt_sub4:
            render_compare_tab(st.session_state.ticker, st.session_state.financials, extractor, visualizer)
    
    # ==========================================
    # TAB 7: NEWS & SENTIMENT
    # ==========================================
    
    with tab7:
        st.markdown(f"## {icon('newspaper', '1.5em')} Recent News & Market Sentiment", unsafe_allow_html=True)
        
        st.info("Multi-source news aggregation with sentiment analysis")
        
        # Toggle for NewsAPI (paid)
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown("### News Sources")
        
        with col2:
            use_newsapi = st.checkbox(
                "Use NewsAPI",
                value=False,
                help="Enable NewsAPI for 30,000+ premium sources (requires API key). Leave unchecked for free RSS feeds."
            )
        
        if use_newsapi:
            st.caption("NewsAPI enabled (paid/limited free tier - 100 requests/day)")
        else:
            st.caption("🆓 Using free RSS feeds (Yahoo Finance + Google News)")
        
        st.markdown("---")
        
        try:
            from news_analysis import get_ticker_news
            
            with st.spinner("Fetching latest news..."):
                news_data = get_ticker_news(st.session_state.ticker, use_newsapi=use_newsapi)
                
                if news_data['status'] == 'success':
                    summary = news_data['summary']
                    
                    # Display API warning if present
                    if 'api_warning' in news_data:
                        st.warning(f"{news_data['api_warning']}")
                    
                    # Summary metrics
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Total Articles", summary['total_articles'])
                    
                    with col2:
                        st.metric("News Sources", summary['sources'])
                    
                    with col3:
                        sentiment = news_data.get('overall_sentiment', 'Neutral')
                        sentiment_color = news_data.get('sentiment_color', 'gray')
                        st.metric("Sentiment", sentiment)
                    
                    with col4:
                        st.metric("Positive Articles", f"{summary['positive_articles']}/{summary['total_articles']}")
                    
                    st.markdown("---")
                    
                    # Sentiment breakdown
                    st.markdown(f"### {icon('bar-chart-line', '1.2em')} Sentiment Breakdown", unsafe_allow_html=True)
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.markdown(f"<div style='text-align: center;'><h3 style='color: green;'>{summary['positive_articles']}</h3><p>Positive</p></div>", unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown(f"<div style='text-align: center;'><h3 style='color: gray;'>{summary['neutral_articles']}</h3><p>Neutral</p></div>", unsafe_allow_html=True)
                    
                    with col3:
                        st.markdown(f"<div style='text-align: center;'><h3 style='color: red;'>{summary['negative_articles']}</h3><p>Negative</p></div>", unsafe_allow_html=True)
                    
                    st.markdown("---")
                    
                    # Sources used
                    st.markdown(f"### {icon('database', '1.2em')} Sources Used", unsafe_allow_html=True)
                    
                    for source in news_data['sources_used']:
                        if 'Paid' in source:
                            st.markdown(f"• [Premium] {source}")
                        else:
                            st.markdown(f"• 🆓 {source}")
                    
                    st.markdown("---")
                    
                    # Display articles with sentiment tags
                    st.markdown(f"### {icon('list', '1.2em')} Recent Headlines (Latest {min(20, summary['total_articles'])})", unsafe_allow_html=True)
                    
                    for i, article in enumerate(news_data['articles'][:20], 1):
                        with st.container():
                            # Sentiment indicator
                            sentiment_icons = {
                                'Positive': '<span style="background: #28a745; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.8em;">BULLISH</span>',
                                'Negative': '<span style="background: #d32f2f; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.8em;">BEARISH</span>',
                                'Neutral': '<span style="background: #9e9e9e; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.8em;">NEUTRAL</span>'
                            }
                            
                            sentiment_tag = sentiment_icons.get(article.get('sentiment', 'Neutral'), '')
                            
                            col1, col2 = st.columns([5, 2])
                            
                            with col1:
                                st.markdown(f"{sentiment_tag} **{article['title']}**", unsafe_allow_html=True)
                                if article.get('summary'):
                                    st.markdown(f"_{article['summary'][:200]}..._")
                            
                            with col2:
                                st.caption(f"{article['source']}")
                                st.caption(f"{article['published'][:10]}")
                                
                                # Add author if available
                                if article.get('author'):
                                    st.caption(f"✍️ {article['author']}")
                                
                                # Add sentiment confidence if available
                                if article.get('sentiment_score'):
                                    confidence = article['sentiment_score']
                                    st.caption(f"Confidence: {confidence:.0%}")
                                
                                # Add estimated read time based on summary length
                                if article.get('summary'):
                                    word_count = len(article['summary'].split())
                                    read_time = max(1, word_count // 200)
                                    st.caption(f"{read_time} min read")
                            
                            st.markdown(f'<a href="{article["link"]}" target="_blank" rel="noopener noreferrer">Read Full Article →</a>', unsafe_allow_html=True)
                            
                            if i < len(news_data['articles'][:20]):
                                st.markdown("---")
                    
                    # API key setup instructions (if NewsAPI not enabled)
                    if not use_newsapi:
                        with st.expander("How to enable NewsAPI (optional)"):
                            st.markdown("""
                            **To unlock 30,000+ premium news sources:**
                            
                            1. Sign up at <a href="https://newsapi.org/" target="_blank" rel="noopener noreferrer">newsapi.org</a> (free tier: 100 requests/day)
                            2. Get your API key
                            3. Set environment variable: `NEWSAPI_KEY=your_key_here`
                            4. Check the "Use NewsAPI" box above
                            
                            **Note:** Free tier is limited. For production use, consider the paid plan ($449/month for developer tier).
                            """, unsafe_allow_html=True)
                
                else:
                    st.error(f"{news_data.get('message', 'Failed to fetch news')}")
        
        except Exception as e:
            st.error(f"Error fetching news: {str(e)}")
            st.caption("Tip: Make sure you have internet connection and RSS feeds are accessible.")
    
    # ==========================================
    # TAB 8: IC MEMO - Investment Summary
    # ==========================================
    
    with tab8:
        render_investment_summary_tab(st.session_state.financials)