"""
Dashboard Tab - Combined Charts View
=====================================
Single comprehensive view of all key financial charts for a company

Layout: 2x3 grid + summary metrics
- Revenue Trend | Margin Analysis
- Profitability  | Cash Flow
- Valuation      | Growth Metrics
- Summary Cards (full width)
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any

def render_dashboard_tab(ticker: str, financials: Dict[str, Any], visualizer):
    """
    Render the Dashboard tab with all key charts in a single view
    
    Args:
        ticker: Company ticker symbol
        financials: Financial data dictionary
        visualizer: FinancialVisualizer instance
    """
    
    st.markdown("## Financial Dashboard", unsafe_allow_html=True)
    st.markdown(f"### {ticker} - Complete Financial Overview", unsafe_allow_html=True)
    
    if not financials:
        st.warning("Load company data first to view dashboard")
        return
    
    # Summary metrics at top
    st.markdown("### Key Metrics")
    display_key_metrics(financials)
    
    st.markdown("---")
    st.markdown("### Charts Overview")
    
    # Top row - Revenue & Margins
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Revenue Trend")
        try:
            chart = visualizer.plot_revenue_trend(financials)
            st.plotly_chart(chart, use_container_width=True, key="dash_revenue")
        except Exception as e:
            st.error(f"Revenue chart error: {str(e)}")
    
    with col2:
        st.markdown("#### Margin Analysis")
        try:
            chart = visualizer.plot_margin_analysis(financials)
            st.plotly_chart(chart, use_container_width=True, key="dash_margin")
        except Exception as e:
            st.error(f"Margin chart error: {str(e)}")
    
    # Middle row - Profitability & Cash Flow
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown("#### Profitability Trends")
        try:
            chart = visualizer.plot_profitability_trends(financials)
            st.plotly_chart(chart, use_container_width=True, key="dash_profit")
        except Exception as e:
            st.error(f"Profitability chart error: {str(e)}")
    
    with col4:
        st.markdown("#### Cash Flow Analysis")
        try:
            chart = visualizer.plot_cash_flow_trends(financials)  # Fixed method name
            st.plotly_chart(chart, use_container_width=True, key="dash_cashflow")
        except Exception as e:
            st.error(f"Cash flow chart error: {str(e)}")
    
    # Bottom row - Valuation & Growth
    col5, col6 = st.columns(2)
    
    with col5:
        st.markdown("#### Valuation Multiples")
        try:
            chart = create_valuation_chart(financials, visualizer)  # Use helper function
            st.plotly_chart(chart, use_container_width=True, key="dash_valuation")
        except Exception as e:
            st.error(f"Valuation chart error: {str(e)}")
    
    with col6:
        st.markdown("#### Growth Metrics")
        try:
            chart = create_growth_chart(financials, visualizer)  # Use helper function
            st.plotly_chart(chart, use_container_width=True, key="dash_growth")
        except Exception as e:
            st.error(f"Growth chart error: {str(e)}")
    
    # Quick insights at bottom
    st.markdown("---")
    st.markdown("### Quick Insights")
    display_quick_insights(financials)


def display_key_metrics(financials: Dict[str, Any]):
    """Display key metrics in a card format"""
    
    # First row - 5 metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    # Helper function to extract from nested structure or top-level
    def get_metric(key, default='N/A'):
        # Try top-level first
        value = financials.get(key, None)
        if value is not None and value != 'N/A':
            return value
        
        # Try in ratios (transposed DataFrame from usa_backend)
        ratios = financials.get('ratios', None)
        if ratios is not None and isinstance(ratios, pd.DataFrame) and not ratios.empty:
            # Ratios are stored as transposed: index = ratio names, column = values
            # Common mappings
            ratio_mapping = {
                'current_price': 'Current_Price',
                'pe_ratio': 'PE_Ratio',
                'roe': 'ROE',
                'revenue': 'Revenue',
                'net_income': 'Net_Income',
                'debt_to_equity': 'Debt_to_Equity'
            }
            
            # Try direct key
            if key in ratios.index:
                return ratios.loc[key].iloc[0] if len(ratios.columns) > 0 else default
            
            # Try mapped key
            mapped_key = ratio_mapping.get(key)
            if mapped_key and mapped_key in ratios.index:
                return ratios.loc[mapped_key].iloc[0] if len(ratios.columns) > 0 else default
        
        # Try in market_data dict (yfinance)
        market_data = financials.get('market_data', {})
        if isinstance(market_data, dict) and key in market_data:
            return market_data[key]
        
        # Try in income statement (latest row)
        income = financials.get('income_statement', pd.DataFrame())
        if not income.empty:
            if isinstance(income.index[0], str):  # yfinance format
                # Search for the metric
                search_terms = {
                    'revenue': ['Total Revenue', 'Revenue'],
                    'net_income': ['Net Income'],
                }
                search_list = search_terms.get(key, [key])
                for search_term in search_list:
                    for idx in income.index:
                        if search_term.lower() in str(idx).lower():
                            return income.loc[idx, income.columns[0]]
            elif key in income.columns:
                return income[key].iloc[0]
        
        # Try balance sheet
        balance = financials.get('balance_sheet', pd.DataFrame())
        if not balance.empty and key in balance.columns:
            return balance[key].iloc[0]
        
        return default
    
    with col1:
        price = get_metric('current_price')
        if price != 'N/A' and price is not None:
            st.metric("Current Price", f"${float(price):.2f}")
        else:
            st.metric("Current Price", 'N/A')
    
    with col2:
        pe = get_metric('pe_ratio')
        if pe != 'N/A' and pe is not None:
            try:
                st.metric("P/E Ratio", f"{float(pe):.2f}")
            except (ValueError, TypeError):
                st.metric("P/E Ratio", 'N/A')
        else:
            st.metric("P/E Ratio", 'N/A')
    
    with col3:
        revenue = get_metric('revenue')
        if revenue == 'N/A' or revenue is None:
            # Try to get from income statement
            income = financials.get('income_statement', pd.DataFrame())
            if not income.empty:
                if isinstance(income.index[0], str):  # yfinance format
                    for idx in income.index:
                        if 'revenue' in str(idx).lower():
                            revenue = income.loc[idx, income.columns[0]]
                            break
        
        if revenue != 'N/A' and revenue is not None:
            try:
                revenue_val = float(revenue)
                if revenue_val > 1e9:
                    st.metric("Revenue", f"${revenue_val/1e9:.2f}B")
                elif revenue_val > 1e6:
                    st.metric("Revenue", f"${revenue_val/1e6:.2f}M")
                else:
                    st.metric("Revenue", f"${revenue_val:,.0f}")
            except (ValueError, TypeError):
                st.metric("Revenue", 'N/A')
        else:
            st.metric("Revenue", 'N/A')
    
    with col4:
        net_income = get_metric('net_income')
        if net_income == 'N/A' or net_income is None:
            # Try to get from income statement
            income = financials.get('income_statement', pd.DataFrame())
            if not income.empty:
                if isinstance(income.index[0], str):  # yfinance format
                    for idx in income.index:
                        if 'net income' in str(idx).lower() and 'common' not in str(idx).lower():
                            net_income = income.loc[idx, income.columns[0]]
                            break
        
        if net_income != 'N/A' and net_income is not None:
            try:
                income_val = float(net_income)
                if abs(income_val) > 1e9:
                    st.metric("Net Income", f"${income_val/1e9:.2f}B")
                elif abs(income_val) > 1e6:
                    st.metric("Net Income", f"${income_val/1e6:.2f}M")
                else:
                    st.metric("Net Income", f"${income_val:,.0f}")
            except (ValueError, TypeError):
                st.metric("Net Income", 'N/A')
        else:
            st.metric("Net Income", 'N/A')
    
    with col5:
        roe = get_metric('roe')
        if roe != 'N/A' and roe is not None:
            try:
                st.metric("ROE", f"{float(roe):.1f}%")
            except (ValueError, TypeError):
                st.metric("ROE", 'N/A')
        else:
            st.metric("ROE", 'N/A')
    
    # Second row - EPS, Market Cap, Debt/Equity, etc.
    col6, col7, col8, col9, col10 = st.columns(5)
    
    # Get info dict for EPS and other metrics
    info = financials.get('info', {})
    
    with col6:
        # Current EPS (Trailing)
        trailing_eps = info.get('trailingEps')
        if trailing_eps and trailing_eps != 'N/A':
            try:
                st.metric("EPS (TTM)", f"${float(trailing_eps):.2f}")
            except (ValueError, TypeError):
                st.metric("EPS (TTM)", 'N/A')
        else:
            st.metric("EPS (TTM)", 'N/A')
    
    with col7:
        # Forward EPS
        forward_eps = info.get('forwardEps')
        if forward_eps and forward_eps != 'N/A':
            try:
                st.metric("Forward EPS", f"${float(forward_eps):.2f}")
            except (ValueError, TypeError):
                st.metric("Forward EPS", 'N/A')
        else:
            st.metric("Forward EPS", 'N/A')
    
    with col8:
        # Market Cap
        market_cap = info.get('marketCap') or get_metric('market_cap')
        if market_cap and market_cap != 'N/A':
            try:
                mc_val = float(market_cap)
                if mc_val > 1e12:
                    st.metric("Market Cap", f"${mc_val/1e12:.2f}T")
                elif mc_val > 1e9:
                    st.metric("Market Cap", f"${mc_val/1e9:.2f}B")
                else:
                    st.metric("Market Cap", f"${mc_val/1e6:.2f}M")
            except (ValueError, TypeError):
                st.metric("Market Cap", 'N/A')
        else:
            st.metric("Market Cap", 'N/A')
    
    with col9:
        # Debt/Equity
        debt_equity = get_metric('debt_to_equity')
        if debt_equity and debt_equity != 'N/A':
            try:
                de_val = float(debt_equity)
                # yfinance sometimes returns as percentage (155 = 1.55)
                if de_val > 10:
                    de_val = de_val / 100
                st.metric("Debt/Equity", f"{de_val:.2f}x")
            except (ValueError, TypeError):
                st.metric("Debt/Equity", 'N/A')
        else:
            st.metric("Debt/Equity", 'N/A')
    
    with col10:
        # Free Cash Flow
        fcf = info.get('freeCashflow')
        if fcf and fcf != 'N/A':
            try:
                fcf_val = float(fcf)
                if abs(fcf_val) > 1e9:
                    st.metric("Free Cash Flow", f"${fcf_val/1e9:.2f}B")
                elif abs(fcf_val) > 1e6:
                    st.metric("Free Cash Flow", f"${fcf_val/1e6:.2f}M")
                else:
                    st.metric("Free Cash Flow", f"${fcf_val:,.0f}")
            except (ValueError, TypeError):
                st.metric("Free Cash Flow", 'N/A')
        else:
            st.metric("Free Cash Flow", 'N/A')


def display_quick_insights(financials: Dict[str, Any]):
    """Display quick analysis insights"""
    
    # Helper to extract from ratios DataFrame
    def get_ratio(key):
        ratios = financials.get('ratios', None)
        if ratios is not None and isinstance(ratios, pd.DataFrame) and not ratios.empty:
            if key in ratios.index:
                val = ratios.loc[key].iloc[0]
                return val if pd.notnull(val) else None
        return None
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### Valuation")
        pe = get_ratio('PE_Ratio')
        if pe and isinstance(pe, (int, float)) and pe > 0:
            if pe < 15:
                st.success(f"Undervalued (P/E: {pe:.1f})")
            elif pe > 30:
                st.warning(f"Potentially Overvalued (P/E: {pe:.1f})")
            else:
                st.info(f"Fairly Valued (P/E: {pe:.1f})")
        else:
            st.caption("P/E ratio not available")
    
    with col2:
        st.markdown("#### Profitability")
        roe = get_ratio('ROE')
        if roe and isinstance(roe, (int, float)):
            # ROE is stored as decimal (0.15), convert to percentage
            roe_pct = roe * 100 if roe < 1 else roe
            if roe_pct > 15:
                st.success(f"Strong ROE: {roe_pct:.1f}%")
            elif roe_pct > 10:
                st.info(f"Moderate ROE: {roe_pct:.1f}%")
            else:
                st.warning(f"Low ROE: {roe_pct:.1f}%")
        else:
            st.caption("ROE not available")
    
    with col3:
        st.markdown("#### Debt")
        debt_equity = get_ratio('Debt_to_Equity')
        if debt_equity and isinstance(debt_equity, (int, float)) and debt_equity >= 0:
            if debt_equity < 0.5:
                st.success(f"Low Debt: {debt_equity:.2f}")
            elif debt_equity < 1.0:
                st.info(f"Moderate Debt: {debt_equity:.2f}")
            else:
                st.warning(f"High Debt: {debt_equity:.2f}")
        else:
            st.caption("Debt/Equity not available")


def create_valuation_chart(financials: Dict[str, Any], visualizer):
    """Create a bar chart showing key valuation multiples"""
    import plotly.graph_objects as go
    
    # Helper to extract from ratios DataFrame
    def get_ratio(key):
        ratios = financials.get('ratios', None)
        if ratios is not None and isinstance(ratios, pd.DataFrame) and not ratios.empty:
            if key in ratios.index:
                val = ratios.loc[key].iloc[0]
                return val if pd.notnull(val) else None
        return None
    
    # Extract valuation metrics from ratios DataFrame
    metrics = {
        'P/E Ratio': get_ratio('PE_Ratio'),
        'P/B Ratio': get_ratio('Price_to_Book'),
        'P/S Ratio': get_ratio('Price_to_Sales'),
        'EV/EBITDA': get_ratio('EV_to_EBITDA'),
        'EV/Sales': get_ratio('EV_to_Sales')
    }
    
    # Filter out None values
    metrics = {k: v for k, v in metrics.items() if v is not None and isinstance(v, (int, float)) and not pd.isna(v)}
    
    if not metrics:
        return visualizer._empty_chart("No valuation metrics available")
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=list(metrics.keys()),
        y=list(metrics.values()),
        marker_color='#FFD700',
        text=[f"{v:.2f}" for v in metrics.values()],
        textposition='outside'
    ))
    
    fig.update_layout(
        title=f"Valuation Multiples | {financials.get('ticker', '')}",
        template=visualizer.theme,
        yaxis_title="Multiple Value",
        height=500
    )
    
    return fig


def create_growth_chart(financials: Dict[str, Any], visualizer):
    """Create a bar chart showing growth metrics"""
    import plotly.graph_objects as go
    
    # Helper to extract from growth_rates dict or ratios DataFrame
    def get_growth(keys_list):
        """Try multiple key variations"""
        # Try growth_rates dict first
        growth_rates = financials.get('growth_rates', {})
        if isinstance(growth_rates, dict):
            for key in keys_list:
                if key in growth_rates:
                    val = growth_rates[key]
                    if pd.notnull(val):
                        return val
        
        # Try ratios DataFrame
        ratios = financials.get('ratios', None)
        if ratios is not None and isinstance(ratios, pd.DataFrame) and not ratios.empty:
            for key in keys_list:
                if key in ratios.index:
                    val = ratios.loc[key].iloc[0]
                    if pd.notnull(val):
                        return val
        
        return None
    
    # Extract growth metrics with multiple possible key names
    metrics = {
        'Revenue Growth': get_growth(['Revenue_CAGR_3Y', 'Total_Revenue_CAGR', 'Revenue_CAGR']),
        'Earnings Growth': get_growth(['Net_Income_CAGR_3Y', 'Net_Income_CAGR', 'Earnings_CAGR']),
        'Operating Income': get_growth(['Operating_Profit_CAGR', 'Operating_Income_CAGR', 'EBIT_CAGR']),
        'Asset Growth': get_growth(['Total_Assets_CAGR_3Y', 'Total_Assets_CAGR', 'Assets_CAGR'])
    }
    
    # Filter out None values
    metrics = {k: v for k, v in metrics.items() if v is not None and isinstance(v, (int, float)) and not pd.isna(v)}
    
    if not metrics:
        return visualizer._empty_chart("No growth metrics available")
    
    fig = go.Figure()
    
    # Color positive values green, negative red
    colors = ['#4CAF50' if v > 0 else '#F44336' for v in metrics.values()]
    
    fig.add_trace(go.Bar(
        x=list(metrics.keys()),
        y=list(metrics.values()),
        marker_color=colors,
        text=[f"{v:.1f}%" for v in metrics.values()],
        textposition='outside'
    ))
    
    # Add zero line
    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
    
    fig.update_layout(
        title=f"Growth Metrics (CAGR) | {financials.get('ticker', '')}",
        template=visualizer.theme,
        yaxis_title="Growth Rate (%)",
        height=500
    )
    
    return fig

