"""
ATLAS Financial Intelligence - Market Intelligence Tab
======================================================
Technical Analysis + Quant + Options + Peer Compare
Extracted from usa_app.py lines 3449-3724
"""

import streamlit as st
import pandas as pd

# Import UI components
from ui_components import smart_dataframe

# Import tab modules
from quant_tab import render_quant_tab
from compare_tab import render_compare_tab


def icon(name, size="1em", color=None):
    """Render a Bootstrap Icon"""
    style = f"font-size: {size};"
    if color:
        style += f" color: {color};"
    return f'<i class="bi bi-{name}" style="{style}"></i>'


def render_market_tab(ticker: str, financials: dict, extractor, visualizer, has_quant: bool = True):
    """
    Render the Market Intelligence tab with sub-tabs.
    
    Args:
        ticker: Stock ticker symbol
        financials: Dictionary of financial data
        extractor: USAFinancialExtractor instance
        visualizer: FinancialVisualizer instance
        has_quant: Whether quant analysis data is available
    """
    if has_quant:
        mkt_sub1, mkt_sub2, mkt_sub3, mkt_sub4 = st.tabs(["Technical", "Quant", "Options", "Peer Compare"])
    else:
        mkt_sub1, mkt_sub3, mkt_sub4 = st.tabs(["Technical", "Options", "Peer Compare"])
        mkt_sub2 = None
    
    # ==========================================
    # SUB-TAB 1: TECHNICAL ANALYSIS
    # ==========================================
    with mkt_sub1:
        _render_technical_section(financials)
    
    # ==========================================
    # SUB-TAB 2: QUANT (if available)
    # ==========================================
    if has_quant and mkt_sub2:
        with mkt_sub2:
            render_quant_tab(ticker, financials)
    
    # ==========================================
    # SUB-TAB 3: OPTIONS FLOW
    # ==========================================
    with mkt_sub3:
        _render_options_section(ticker)
    
    # ==========================================
    # SUB-TAB 4: PEER COMPARISON
    # ==========================================
    with mkt_sub4:
        render_compare_tab(ticker, financials, extractor, visualizer)


def _render_technical_section(financials: dict):
    """Render Technical Analysis section"""
    st.markdown(f"## {icon('graph-up-arrow', '1.5em')} Technical Analysis", unsafe_allow_html=True)
    st.info("Comprehensive technical indicators and trading signals based on price action and volume.")
    
    try:
        from technical_analysis import analyze_technical
        
        market_data = financials.get("market_data", {})
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
                        'Strong Buy': '<span style="background: #28a745; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold;">STRONG BUY</span>',
                        'Buy': '<span style="background: #7cb342; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold;">BUY</span>',
                        'Hold': '<span style="background: #9e9e9e; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold;">HOLD</span>',
                        'Sell': '<span style="background: #ef5350; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold;">SELL</span>',
                        'Strong Sell': '<span style="background: #d32f2f; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold;">STRONG SELL</span>'
                    }
                    signal_html = signal_colors.get(overall['signal'], '<span style="background: #9e9e9e; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold;">NEUTRAL</span>')
                    
                    st.markdown(f"### {signal_html}", unsafe_allow_html=True)
                    st.metric("Signal Score", f"{overall['score']}/8")
                
                with col2:
                    st.markdown("**Key Factors:**")
                    for factor in overall['factors']:
                        st.write(f"- {factor}")
                
                st.markdown("---")
                
                # Moving Averages
                _render_moving_averages(tech_signals)
                
                st.markdown("---")
                
                # Momentum Indicators
                _render_momentum(tech_signals)
                
                st.markdown("---")
                
                # Volatility & Volume
                _render_volatility_volume(tech_signals)
                
                st.markdown("---")
                
                # Support & Resistance
                _render_support_resistance(tech_signals)
        
        else:
            st.warning("No historical price data available for technical analysis")
            
    except Exception as e:
        st.error(f"Error running technical analysis: {str(e)}")


def _render_moving_averages(tech_signals: dict):
    """Render Moving Averages section"""
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
    
    if ma['golden_cross']:
        st.success("Golden Cross: 50-day SMA above 200-day SMA (Bullish)")
    else:
        st.warning("Death Cross: 50-day SMA below 200-day SMA (Bearish)")


def _render_momentum(tech_signals: dict):
    """Render Momentum Indicators section"""
    st.markdown(f"### {icon('lightning-charge')} Momentum Indicators", unsafe_allow_html=True)
    mom = tech_signals['momentum']
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**RSI (Relative Strength Index)**")
        st.metric("RSI", f"{mom['rsi']:.2f}", help="14-period RSI")
        st.caption(mom['rsi_signal'])
        
        if mom['rsi'] >= 70:
            st.error("Overbought Territory")
        elif mom['rsi'] <= 30:
            st.success("Oversold Territory (Opportunity)")
        else:
            st.info("Neutral Zone")
    
    with col2:
        st.markdown("**MACD (Moving Average Convergence Divergence)**")
        st.metric("MACD Line", f"{mom['macd']:.4f}")
        st.metric("Signal Line", f"{mom['macd_signal']:.4f}")
        st.metric("Histogram", f"{mom['macd_histogram']:.4f}")
        
        if mom['macd_crossover'] == 'Bullish':
            st.success("Bullish Crossover")
        else:
            st.warning("Bearish Crossover")


def _render_volatility_volume(tech_signals: dict):
    """Render Volatility and Volume section"""
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
            st.info("Normal Volume")


def _render_support_resistance(tech_signals: dict):
    """Render Support and Resistance section"""
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


def _render_options_section(ticker: str):
    """Render Options Flow section"""
    st.markdown(f"## {icon('bar-chart-line', '1.5em')} Options Flow Analysis", unsafe_allow_html=True)
    st.info("Analyze options market sentiment through Put/Call ratio, implied volatility, and volume patterns.")
    
    try:
        from options_flow import get_options_data
        
        with st.spinner("Fetching options data..."):
            options_data = get_options_data(ticker)
            
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
                    'Bullish': '<span style="background: #28a745; color: white; padding: 6px 12px; border-radius: 4px; font-weight: bold;">BULLISH</span>',
                    'Slightly Bullish': '<span style="background: #7cb342; color: white; padding: 6px 12px; border-radius: 4px; font-weight: bold;">SLIGHTLY BULLISH</span>',
                    'Neutral': '<span style="background: #9e9e9e; color: white; padding: 6px 12px; border-radius: 4px; font-weight: bold;">NEUTRAL</span>',
                    'Slightly Bearish': '<span style="background: #ef5350; color: white; padding: 6px 12px; border-radius: 4px; font-weight: bold;">SLIGHTLY BEARISH</span>',
                    'Bearish': '<span style="background: #d32f2f; color: white; padding: 6px 12px; border-radius: 4px; font-weight: bold;">BEARISH</span>'
                }
                
                sentiment_html = sentiment_colors.get(options_data['sentiment'], '<span style="background: #9e9e9e; color: white; padding: 6px 12px; border-radius: 4px; font-weight: bold;">NEUTRAL</span>')
                st.markdown(f"## Market Sentiment: {sentiment_html}", unsafe_allow_html=True)
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
                
                st.caption("P/C < 0.7: Bullish | 0.7-1.0: Slightly Bullish | 1.0-1.3: Neutral | >1.3: Bearish")
                
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
                    smart_dataframe(options_data['most_active']['calls'], title=None, height=300, key="options_calls_mkt")
                
                with col2:
                    st.markdown(f"### {icon('fire')} Most Active Puts", unsafe_allow_html=True)
                    smart_dataframe(options_data['most_active']['puts'], title=None, height=300, key="options_puts_mkt")
            else:
                st.warning(options_data['message'])
                
    except Exception as e:
        st.error(f"Error fetching options data: {str(e)}")

