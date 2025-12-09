"""
Dashboard Tab - Combined Charts View
=====================================
Single comprehensive view of all key financial charts for a company

Layout: 2x3 grid + summary metrics
- Revenue Trend | Margin Analysis
- Profitability  | Cash Flow
- Valuation      | Growth Metrics
- Summary Cards (full width)

Phase 1: Flip Card Integration
- Key metrics now use FlipCardMetric for educational breakdown
- Click any metric to see formula, components, and 3-depth explanation
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any

# Import unified flip cards (MILESTONE-008)
try:
    from flip_cards import render_dashboard_metrics, METRICS
    FLIP_CARDS_AVAILABLE = True
except ImportError:
    try:
        from flip_card_v2 import render_dashboard_flip_cards as render_dashboard_metrics, METRIC_CONFIG as METRICS
        FLIP_CARDS_AVAILABLE = True
    except ImportError:
        FLIP_CARDS_AVAILABLE = False
        METRICS = {}
        def render_dashboard_metrics(f): pass

# Import draggable grid for layout customization (MILESTONE-014)
try:
    from components.draggable_grid import (
        render_reorder_controls, 
        inject_drag_styles,
        GridConfig
    )
    DRAGGABLE_AVAILABLE = True
except ImportError:
    DRAGGABLE_AVAILABLE = False

# NO LEGACY FLIP CARDS - removed the old button-based implementation

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
    
    # Inject drag styles for visual feedback (M014)
    if DRAGGABLE_AVAILABLE:
        inject_drag_styles()
        # Layout customization controls
        render_reorder_controls(GridConfig(columns=5))
    
    # V2 Quizlet-style flip cards (pure CSS animation, no server round-trip)
    if FLIP_CARDS_AVAILABLE:
        render_dashboard_metrics(financials)
    else:
        # Simple metrics fallback (NO old button-based flip - too slow)
        st.markdown("### Key Metrics")
        display_key_metrics(financials)
    
    st.markdown("---")
    
    # Price Chart - Full Width at top
    st.markdown("### Stock Price")
    try:
        price_chart = create_price_chart(ticker, financials)
        if price_chart:
            st.plotly_chart(price_chart, use_container_width=True, key="dash_price")
    except Exception as e:
        st.info(f"Price chart unavailable: {str(e)}")
    
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


def display_key_metrics_flip(financials: Dict[str, Any], depth: str = "beginner"):
    """
    Display key metrics as flip cards with educational breakdown
    
    Args:
        financials: Financial data dictionary
        depth: Explanation level (beginner, intermediate, professional)
    """
    
    # Helper function to extract metrics (same as original)
    def get_metric(key, default=None):
        # Try top-level first
        value = financials.get(key, None)
        if value is not None and value != 'N/A':
            return value
        
        # Try in ratios (transposed DataFrame)
        ratios = financials.get('ratios', None)
        if ratios is not None and isinstance(ratios, pd.DataFrame) and not ratios.empty:
            ratio_mapping = {
                'current_price': 'Current_Price',
                'pe_ratio': 'PE_Ratio',
                'roe': 'ROE',
                'revenue': 'Revenue',
                'net_income': 'Net_Income',
                'debt_to_equity': 'Debt_to_Equity'
            }
            if key in ratios.index:
                val = ratios.loc[key].iloc[0] if len(ratios.columns) > 0 else default
                if pd.notna(val):
                    return val
            mapped_key = ratio_mapping.get(key)
            if mapped_key and mapped_key in ratios.index:
                val = ratios.loc[mapped_key].iloc[0] if len(ratios.columns) > 0 else default
                if pd.notna(val):
                    return val
        
        # Try in market_data dict
        market_data = financials.get('market_data', {})
        if isinstance(market_data, dict) and key in market_data:
            return market_data[key]
        
        # Try in info dict
        info = financials.get('info', {})
        if isinstance(info, dict) and key in info:
            return info[key]
        
        # Try income statement
        income = financials.get('income_statement', pd.DataFrame())
        if not income.empty and isinstance(income.index[0], str):
            search_terms = {'revenue': ['Total Revenue', 'Revenue'], 'net_income': ['Net Income']}
            for search_term in search_terms.get(key, [key]):
                for idx in income.index:
                    if search_term.lower() in str(idx).lower():
                        val = income.loc[idx, income.columns[0]]
                        if pd.notna(val):
                            return val
        
        return default
    
    # Get info dict for additional metrics
    info = financials.get('info', {})
    
    # Define all 10 metrics with their configurations
    metrics_config = [
        # Row 1
        {"key": "PE_Ratio", "value": get_metric('pe_ratio'), "label": "P/E Ratio", 
         "unit": "x", "higher_is_better": False, "benchmark_low": 15, "benchmark_high": 25},
        {"key": "current_price", "value": get_metric('current_price'), "label": "Current Price", 
         "unit": "$", "higher_is_better": True},
        {"key": "revenue", "value": get_metric('revenue'), "label": "Revenue (TTM)", 
         "unit": "$", "format_large": True, "higher_is_better": True},
        {"key": "net_income", "value": get_metric('net_income'), "label": "Net Income", 
         "unit": "$", "format_large": True, "higher_is_better": True},
        {"key": "ROE", "value": get_metric('roe'), "label": "ROE", 
         "unit": "%", "is_pct": True, "higher_is_better": True, "benchmark_low": 10, "benchmark_high": 20},
        # Row 2
        {"key": "EPS", "value": info.get('trailingEps'), "label": "EPS (TTM)", 
         "unit": "$", "higher_is_better": True},
        {"key": "forward_eps", "value": info.get('forwardEps'), "label": "Forward EPS", 
         "unit": "$", "higher_is_better": True},
        {"key": "market_cap", "value": info.get('marketCap') or get_metric('market_cap'), "label": "Market Cap", 
         "unit": "$", "format_large": True, "higher_is_better": True},
        {"key": "Debt_to_Equity", "value": get_metric('debt_to_equity'), "label": "Debt/Equity", 
         "unit": "x", "higher_is_better": False, "benchmark_low": 0.5, "benchmark_high": 1.5},
        {"key": "FCF", "value": info.get('freeCashflow'), "label": "Free Cash Flow", 
         "unit": "$", "format_large": True, "higher_is_better": True},
    ]
    
    # Render Row 1 (5 metrics)
    cols1 = st.columns(5)
    for i, config in enumerate(metrics_config[:5]):
        with cols1[i]:
            _render_flip_metric(config, financials, depth)
    
    # Render Row 2 (5 metrics)
    cols2 = st.columns(5)
    for i, config in enumerate(metrics_config[5:]):
        with cols2[i]:
            _render_flip_metric(config, financials, depth)


def _render_flip_metric(config: Dict, financials: Dict, depth: str):
    """Render a single flip card metric"""
    
    key = config["key"]
    value = config["value"]
    label = config["label"]
    unit = config.get("unit", "")
    format_large = config.get("format_large", False)
    is_pct = config.get("is_pct", False)
    higher_is_better = config.get("higher_is_better", True)
    benchmark_low = config.get("benchmark_low")
    benchmark_high = config.get("benchmark_high")
    
    # Format the value
    if value is None or (isinstance(value, float) and pd.isna(value)):
        formatted_value = "N/A"
        color = "#6b7280"  # Gray
    else:
        try:
            num_val = float(value)
            
            if format_large:
                if abs(num_val) >= 1e12:
                    formatted_value = f"${num_val/1e12:.2f}T"
                elif abs(num_val) >= 1e9:
                    formatted_value = f"${num_val/1e9:.2f}B"
                elif abs(num_val) >= 1e6:
                    formatted_value = f"${num_val/1e6:.2f}M"
                else:
                    formatted_value = f"${num_val:,.0f}"
            elif is_pct:
                # Handle percentage: if < 1, assume decimal form
                pct_val = num_val * 100 if abs(num_val) < 1 else num_val
                formatted_value = f"{pct_val:.1f}%"
                num_val = pct_val  # Use percentage for benchmarking
            elif unit == "$":
                formatted_value = f"${num_val:.2f}"
            elif unit == "x":
                # Normalize D/E if it looks like percentage
                if key == "Debt_to_Equity" and num_val > 10:
                    num_val = num_val / 100
                formatted_value = f"{num_val:.2f}x"
            else:
                formatted_value = f"{num_val:.2f}"
            
            # Determine color based on benchmarks
            if benchmark_low is not None and benchmark_high is not None:
                if higher_is_better:
                    if num_val >= benchmark_high:
                        color = "#22c55e"  # Green
                    elif num_val <= benchmark_low:
                        color = "#ef4444"  # Red
                    else:
                        color = "#f59e0b"  # Yellow
                else:
                    if num_val <= benchmark_low:
                        color = "#22c55e"  # Green (low is good)
                    elif num_val >= benchmark_high:
                        color = "#ef4444"  # Red (high is bad)
                    else:
                        color = "#f59e0b"  # Yellow
            else:
                color = "#60a5fa"  # Blue (neutral)
                
        except (ValueError, TypeError):
            formatted_value = str(value) if value else "N/A"
            color = "#6b7280"
    
    # Get definition from RATIO_DEFINITIONS
    definition = RATIO_DEFINITIONS.get(key, {})
    
    # Build back content
    if definition:
        formula = definition.get("formula", "")
        explanation = definition.get("explanations", {}).get(depth, "")
        components = definition.get("components", [])
    else:
        formula = ""
        explanation = f"No detailed definition available for {label}."
        components = []
    
    # Create unique key for this card (for CSS styling uniqueness)
    card_key = f"flip_{key}_{id(financials)}"
    
    # Build component values string
    comp_str = ""
    if components:
        comp_vals = []
        for comp in components[:3]:  # Max 3 components
            comp_val = _get_component_value(comp, financials)
            if comp_val:
                comp_vals.append(f"{comp.replace('_', ' ').title()}: {comp_val}")
        if comp_vals:
            comp_str = " | ".join(comp_vals)
    
    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
        
        .flip-container-{card_key} {{
            perspective: 1000px;
            height: 140px;
            margin-bottom: 8px;
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        }}
        .flip-card-{card_key} {{
            position: relative;
            width: 100%;
            height: 100%;
            text-align: center;
            transition: transform 0.45s cubic-bezier(0.4, 0, 0.2, 1);
            transform-style: preserve-3d;
            cursor: pointer;
            border-radius: 12px;
        }}
        .flip-container-{card_key}:hover .flip-card-{card_key} {{
            transform: rotateY(180deg);
        }}
        .flip-front-{card_key}, .flip-back-{card_key} {{
            position: absolute;
            width: 100%;
            height: 100%;
            backface-visibility: hidden;
            -webkit-backface-visibility: hidden;
            border-radius: 12px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            padding: 16px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.15);
            background: linear-gradient(145deg, #1e2530 0%, #161b22 100%);
            border: 1px solid rgba(59, 130, 246, 0.2);
        }}
        .flip-front-{card_key}:hover, .flip-back-{card_key}:hover {{
            border-color: rgba(59, 130, 246, 0.5);
            box-shadow: 0 6px 20px rgba(59, 130, 246, 0.25);
        }}
        .flip-front-{card_key} {{
            border-left: 4px solid {color};
        }}
        .flip-back-{card_key} {{
            border-left: 4px solid {color};
            transform: rotateY(180deg);
            text-align: left;
            align-items: flex-start;
            justify-content: flex-start;
            padding-top: 14px;
        }}
        .metric-label-{card_key} {{
            color: #a0aec0;
            font-size: 0.85rem;
            font-weight: 600;
            margin-bottom: 6px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .metric-value-{card_key} {{
            color: {color};
            font-size: 1.75rem;
            font-weight: 700;
            letter-spacing: -0.5px;
        }}
        .formula-text-{card_key} {{
            color: #60a5fa;
            font-family: 'SF Mono', 'Fira Code', Consolas, monospace;
            font-size: 0.9rem;
            font-weight: 500;
            margin-bottom: 8px;
        }}
        .explanation-text-{card_key} {{
            color: #e2e8f0;
            font-size: 0.85rem;
            line-height: 1.5;
            overflow: hidden;
            display: -webkit-box;
            -webkit-line-clamp: 3;
            -webkit-box-orient: vertical;
        }}
        .components-text-{card_key} {{
            color: #94a3b8;
            font-size: 0.75rem;
            margin-top: 8px;
            font-weight: 500;
        }}
        .flip-hint-{card_key} {{
            position: absolute;
            bottom: 6px;
            right: 10px;
            color: #64748b;
            font-size: 0.7rem;
            opacity: 0.8;
            font-style: italic;
        }}
    </style>
    <div class="flip-container-{card_key}">
        <div class="flip-card-{card_key}">
            <div class="flip-front-{card_key}">
                <div class="metric-label-{card_key}">{label}</div>
                <div class="metric-value-{card_key}">{formatted_value}</div>
                <div class="flip-hint-{card_key}">Hover for details</div>
            </div>
            <div class="flip-back-{card_key}">
                <div style="font-weight: 600; color: #e2e8f0; margin-bottom: 6px; font-size: 0.9rem;">{label}</div>
                <div class="formula-text-{card_key}">{formula if formula else ''}</div>
                <div class="explanation-text-{card_key}">{explanation[:180]}{'...' if len(explanation) > 180 else ''}</div>
                <div class="components-text-{card_key}">{comp_str if comp_str else ''}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def _get_component_value(component: str, financials: Dict) -> str:
    """Extract and format a component value from financials"""
    
    # Try various sources
    info = financials.get('info', {})
    market_data = financials.get('market_data', {})
    
    # Map component names to data keys
    mappings = {
        'current_price': ('current_price', market_data, '$'),
        'eps': ('trailingEps', info, '$'),
        'shares_outstanding': ('sharesOutstanding', info, 'shares'),
        'net_income': ('netIncome', info, '$'),
        'total_equity': ('totalEquity', info, '$'),
        'total_debt': ('totalDebt', info, '$'),
    }
    
    if component in mappings:
        key, source, fmt = mappings[component]
        val = source.get(key)
        if val:
            try:
                num = float(val)
                if fmt == '$':
                    if abs(num) >= 1e9:
                        return f"${num/1e9:.1f}B"
                    elif abs(num) >= 1e6:
                        return f"${num/1e6:.1f}M"
                    return f"${num:.2f}"
                return f"{num:,.0f}"
            except:
                pass
    
    return ""


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


def create_price_chart(ticker: str, financials: Dict[str, Any]):
    """Create a stock price chart with volume"""
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    import yfinance as yf
    from datetime import datetime, timedelta
    
    try:
        # Fetch 1 year of daily data
        stock = yf.Ticker(ticker)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        history = stock.history(start=start_date, end=end_date)
        
        if history.empty:
            return None
        
        # Create figure with secondary y-axis for volume
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            row_heights=[0.75, 0.25]
        )
        
        # Price line
        fig.add_trace(
            go.Scatter(
                x=history.index,
                y=history['Close'],
                mode='lines',
                name='Price',
                line=dict(color='#3b82f6', width=2),
                fill='tozeroy',
                fillcolor='rgba(59, 130, 246, 0.1)'
            ),
            row=1, col=1
        )
        
        # Volume bars
        colors = ['#22c55e' if c >= o else '#ef4444' 
                  for c, o in zip(history['Close'], history['Open'])]
        fig.add_trace(
            go.Bar(
                x=history.index,
                y=history['Volume'],
                name='Volume',
                marker_color=colors,
                opacity=0.7
            ),
            row=2, col=1
        )
        
        # Current price annotation
        current_price = history['Close'].iloc[-1]
        price_change = ((current_price - history['Close'].iloc[0]) / history['Close'].iloc[0]) * 100
        
        fig.update_layout(
            title=dict(
                text=f"{ticker} | ${current_price:.2f} ({'+' if price_change >= 0 else ''}{price_change:.1f}% YTD)",
                font=dict(size=16)
            ),
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=350,
            showlegend=False,
            margin=dict(l=40, r=40, t=60, b=40),
            xaxis2_rangeslider_visible=False
        )
        
        fig.update_yaxes(title_text="Price ($)", row=1, col=1, gridcolor='rgba(255,255,255,0.1)')
        fig.update_yaxes(title_text="Volume", row=2, col=1, gridcolor='rgba(255,255,255,0.1)')
        fig.update_xaxes(gridcolor='rgba(255,255,255,0.05)')
        
        return fig
        
    except Exception:
        return None


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

