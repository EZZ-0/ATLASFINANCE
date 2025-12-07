"""
APP LANDING PAGE - Centered Search Experience
==============================================
Extracted from usa_app.py for maintainability.

Usage:
    from app_landing import render_landing_page
    
    if not st.session_state.get('data_extracted', False):
        render_landing_page(cached_extract_financials, validate_and_enrich, SP500_DISPLAY, extract_ticker)
        st.stop()
"""

import streamlit as st
from typing import Callable, List


def render_landing_page(
    cached_extract_financials: Callable,
    validate_and_enrich: Callable,
    sp500_display: List[str],
    extract_ticker: Callable
) -> bool:
    """
    Render the centered landing page with ticker search.
    
    Args:
        cached_extract_financials: Function to extract financial data (cached)
        validate_and_enrich: Function to validate extracted data
        sp500_display: List of S&P 500 ticker options for dropdown
        extract_ticker: Function to extract ticker from dropdown selection
    
    Returns:
        bool: True if extraction was successful, False otherwise
    """
    
    # Centered container for search
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Ticker input
        landing_ticker = st.text_input(
            "Ticker Symbol",
            placeholder="Type ticker (e.g., AAPL, MSFT, TSLA)",
            label_visibility="visible",
            key="landing_ticker_input"
        ).upper().strip()
        
        st.markdown("<p style='text-align: center; color: #64748b; margin: 1.2rem 0; font-size: 1.1rem;'>OR</p>", unsafe_allow_html=True)
        
        # S&P 500 dropdown
        landing_sp500 = st.selectbox(
            "S&P 500 Companies",
            options=sp500_display,
            label_visibility="visible",
            key="landing_sp500_select"
        )
        
        if landing_sp500 != "--":
            landing_ticker = extract_ticker(landing_sp500)
        
        st.write("")  # Spacing
        
        # EXTRACT button (actually runs extraction)
        if landing_ticker:
            if st.button("EXTRACT DATA", type="primary", use_container_width=True, key="landing_extract"):
                with st.spinner(f"Extracting financial data for {landing_ticker}... (cached for 1 hour)"):
                    try:
                        # Use default settings
                        selected_source = "auto"
                        filing_types_list = ["10-K"]
                        include_quant_analysis = False
                        
                        # Use cached extraction to prevent rate limiting
                        financials = cached_extract_financials(
                            ticker=landing_ticker,
                            source=selected_source,
                            filing_types=tuple(filing_types_list),  # Tuple for caching
                            include_quant=include_quant_analysis
                        )
                        
                        # Check if we got financial data (status field may not exist)
                        if financials and 'ticker' in financials and 'income_statement' in financials:
                            # Validate extracted data
                            validated_financials, validation_report = validate_and_enrich(landing_ticker, financials)
                            # Successful extraction
                            st.session_state.ticker = landing_ticker
                            st.session_state.financials = validated_financials
                            st.session_state.validation_report = validation_report
                            st.session_state.data_extracted = True
                            st.success(f"✓ Successfully extracted data for {landing_ticker}")
                            st.rerun()
                        else:
                            st.error(f"Extraction failed: {financials.get('message', 'No data returned')}")
                    
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
                            st.error(f"Error during extraction: {str(e)}")
        else:
            st.button("EXTRACT DATA", type="primary", use_container_width=True, disabled=True)
    
    return False  # Extraction not complete (or failed)


def render_ticker_display(ticker: str, company_name: str, current_price):
    """
    Render the persistent ticker display header.
    
    Args:
        ticker: Company ticker symbol
        company_name: Company name
        current_price: Current stock price
    """
    # Main ticker display
    st.markdown(f"""
    <div style='text-align: center; padding: 0.8rem 1.5rem; margin: -1rem auto 0.5rem auto;
                max-width: 800px;
                background: linear-gradient(135deg, rgba(59, 130, 246, 0.12) 0%, rgba(59, 130, 246, 0.06) 100%);
                border: 1px solid rgba(59, 130, 246, 0.25);
                border-radius: 10px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);'>
        <div style='display: flex; justify-content: center; align-items: center; gap: 2rem;'>
            <div style='text-align: center;'>
                <p style='color: #3b82f6; font-size: 0.8rem; margin: 0; font-weight: 600; letter-spacing: 0.5px;'>TICKER</p>
                <p style='color: #f0f4f8; font-size: 1.5rem; margin: 0; font-weight: 700;'>{ticker}</p>
            </div>
            <div style='width: 2px; height: 40px; background: rgba(59, 130, 246, 0.3);'></div>
            <div style='text-align: center;'>
                <p style='color: #3b82f6; font-size: 0.8rem; margin: 0; font-weight: 600; letter-spacing: 0.5px;'>COMPANY</p>
                <p style='color: #f0f4f8; font-size: 1.2rem; margin: 0; font-weight: 600;'>{company_name}</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Centralized Stock Price Display
    price_display = current_price if isinstance(current_price, str) else f'{current_price:.2f}'
    st.markdown(f"""
    <div style='padding: 0.8rem 1.5rem; margin: 0.5rem auto 1rem auto;
                max-width: 400px;
                background: #1e2530;
                border: 1px solid rgba(59, 130, 246, 0.2); border-radius: 8px;
                text-align: center;'>
        <p style='color: #3b82f6; font-size: 0.75rem; margin: 0; font-weight: 600; letter-spacing: 0.5px;'>STOCK PRICE (AT EXTRACTION)</p>
        <p style='color: #10b981; font-size: 1.8rem; margin: 0.3rem 0 0 0; font-weight: 700;'>${price_display}</p>
    </div>
    """, unsafe_allow_html=True)


def render_no_ticker_placeholder():
    """Render placeholder when no ticker is loaded."""
    st.markdown("""
    <div style='text-align: center; padding: 0.6rem 1.5rem; margin: -1rem auto 1.5rem auto;
                max-width: 800px;
                background: rgba(59, 130, 246, 0.05);
                border: 1px dashed rgba(59, 130, 246, 0.2);
                border-radius: 10px;'>
        <p style='color: #64748b; font-size: 0.9rem; margin: 0; font-style: italic;'>
            <i class="bi bi-info-circle" style="margin-right: 0.5rem;"></i>
            No ticker loaded - Enter a ticker in the sidebar to begin
        </p>
    </div>
    """, unsafe_allow_html=True)


# Export all functions
__all__ = [
    'render_landing_page',
    'render_ticker_display',
    'render_no_ticker_placeholder'
]

