"""
ANALYSIS TAB - FINANCIAL DEEP DIVE
================================================================================
Extracted from usa_app.py for modularity.

Contains 7 sub-tabs for comprehensive financial analysis:
1. Earnings Analysis
2. Dividend Analysis  
3. Valuation Multiples
4. Cash Flow Deep Dive
5. Balance Sheet Health
6. Management Effectiveness
7. Growth Quality

Author: Atlas Financial Intelligence
Date: November 2025
Phase: Refactoring - Phase 1
"""

import streamlit as st
from typing import Dict

# Import analysis modules
from earnings_analysis import analyze_earnings_history
from dividend_analysis import analyze_dividends
from valuation_multiples import analyze_valuation_multiples
from cashflow_analysis import analyze_cashflow
from balance_sheet_health import analyze_balance_sheet_health
from management_effectiveness import analyze_management_effectiveness
from growth_quality import analyze_growth_quality

# Import flip card metrics with fallback
try:
    from analysis_tab_metrics import (
        render_earnings_flip_metrics, render_dividend_flip_metrics,
        render_valuation_flip_metrics, render_cashflow_flip_metrics,
        render_balance_flip_metrics, render_management_flip_metrics,
        render_growth_flip_metrics, FLIP_CARDS_AVAILABLE
    )
except ImportError:
    FLIP_CARDS_AVAILABLE = False


def icon(name: str, size: str = '1em') -> str:
    """
    Helper function to render Bootstrap icons
    
    Args:
        name: Bootstrap icon name
        size: Icon size (default '1em')
        
    Returns:
        HTML string for icon
    """
    return f'<i class="bi bi-{name}" style="font-size: {size};"></i>'


def render_analysis_tab(ticker: str, financials: Dict) -> None:
    """
    Render Financial Deep Dive Analysis tab with 7 sub-tabs
    
    Args:
        ticker: Stock ticker symbol
        financials: Financial data dictionary
        
    Returns:
        None (renders directly to Streamlit)
    """
    
    st.markdown(f"## {icon('graph-up-arrow', '1.5em')} Financial Deep Dive", unsafe_allow_html=True)
    st.markdown("Advanced financial analysis: earnings, dividends, valuation, cash flow, balance sheet, management, and growth quality.")
    
    # Create sub-tabs for each analysis type
    analysis_sub1, analysis_sub2, analysis_sub3, analysis_sub4, analysis_sub5, analysis_sub6, analysis_sub7 = st.tabs([
        "Earnings",
        "Dividends",
        "Valuation",
        "Cash Flow",
        "Balance Sheet",
        "Management",
        "Growth Quality"
    ])
    
    # ====================================
    # SUB-TAB 1: EARNINGS ANALYSIS
    # ====================================
    with analysis_sub1:
        st.markdown(f"### {icon('bar-chart-line', '1.2em')} Earnings Performance Analysis", unsafe_allow_html=True)
        
        with st.spinner("Analyzing earnings history..."):
            earnings_data = analyze_earnings_history(ticker)
        
        if earnings_data['status'] == 'success':
            metrics = earnings_data['metrics']
            
            # Flip card metrics at top (if available)
            if FLIP_CARDS_AVAILABLE:
                render_earnings_flip_metrics(earnings_data)
            else:
                # Fallback to standard metrics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Earnings Score", f"{metrics.get('earnings_score', 0)}/100",
                             help="Overall earnings quality: Beat rate + Surprise + Growth + Consistency")
                with col2:
                    st.metric("Beat Rate", f"{metrics.get('beat_rate', 0)}%")
                with col3:
                    st.metric("Avg Surprise", f"{metrics.get('average_surprise_pct', 0)}%")
                with col4:
                    st.metric("Quality Ratio", f"{metrics.get('quality_ratio', 0):.2f}")
            
            st.markdown("---")
            
            # Performance breakdown
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"#### {icon('trophy', '1.1em')} Historical Performance", unsafe_allow_html=True)
                st.metric("Total Earnings Reports", metrics.get('total_reports', 0))
                st.metric("Consecutive Beats", metrics.get('consecutive_beats', 0))
                st.metric("Consecutive Misses", metrics.get('consecutive_misses', 0))
                st.metric("Rating", metrics.get('earnings_rating', 'N/A'))
            
            with col2:
                st.markdown(f"#### {icon('graph-up', '1.1em')} Growth Metrics", unsafe_allow_html=True)
                st.metric("EPS Momentum", f"{metrics.get('eps_momentum', 0)}%")
                st.metric("Revenue Surprise", f"{metrics.get('avg_revenue_surprise_pct', 0)}%")
                st.metric("Growth Forecast", f"{metrics.get('growth_forecast', 0)}%")
            
            # Calendar
            if 'next_earnings_date' in metrics:
                st.markdown("---")
                st.markdown(f"#### {icon('calendar', '1.1em')} Earnings Calendar", unsafe_allow_html=True)
                col1, col2 = st.columns(2)
                with col1:
                    st.info(f"**Next Earnings:** {metrics['next_earnings_date']}")
                with col2:
                    st.info(f"**Last Earnings:** {metrics.get('last_earnings_date', 'N/A')}")
        
        elif earnings_data['status'] == 'no_data':
            st.info(earnings_data['message'])
        else:
            st.error(earnings_data['message'])
    
    # ====================================
    # SUB-TAB 2: DIVIDEND ANALYSIS
    # ====================================
    with analysis_sub2:
        st.markdown(f"### {icon('cash-coin', '1.2em')} Dividend Analysis", unsafe_allow_html=True)
        
        with st.spinner("Analyzing dividend history..."):
            dividend_data = analyze_dividends(ticker)
        
        if dividend_data['status'] == 'success':
            metrics = dividend_data['metrics']
            
            # Flip card metrics at top (if available)
            if FLIP_CARDS_AVAILABLE:
                render_dividend_flip_metrics(dividend_data)
            else:
                # Fallback to standard metrics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Dividend Score", f"{metrics.get('dividend_score', 0)}/100",
                             help="Overall dividend quality: Yield + Growth + Sustainability + Consistency")
                with col2:
                    st.metric("Annual Dividend", f"${metrics.get('annual_dividend', 0):.2f}")
                with col3:
                    st.metric("Yield", f"{metrics.get('dividend_yield', 0)}%")
                with col4:
                    st.metric("Payout Ratio", f"{metrics.get('payout_ratio', 0)}%")
            
            st.markdown("---")
            
            # Status and consistency
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"#### {icon('award', '1.1em')} Dividend Status", unsafe_allow_html=True)
                st.metric("Status", metrics.get('dividend_status', 'N/A'))
                st.metric("Tier", metrics.get('status_tier', 'N/A'))
                st.metric("Consecutive Years", metrics.get('consecutive_years', 0))
                st.metric("Total Payments", metrics.get('total_payments', 0))
            
            with col2:
                st.markdown(f"#### {icon('graph-up-arrow', '1.1em')} Growth Rates", unsafe_allow_html=True)
                if 'dividend_growth_1y' in metrics:
                    st.metric("1-Year Growth", f"{metrics['dividend_growth_1y']}%")
                if 'dividend_cagr_3y' in metrics:
                    st.metric("3-Year CAGR", f"{metrics['dividend_cagr_3y']}%")
                if 'dividend_cagr_5y' in metrics:
                    st.metric("5-Year CAGR", f"{metrics['dividend_cagr_5y']}%")
                if 'dividend_cagr_10y' in metrics:
                    st.metric("10-Year CAGR", f"{metrics['dividend_cagr_10y']}%")
            
            # Sustainability
            st.markdown("---")
            st.markdown(f"#### {icon('shield-check', '1.1em')} Sustainability", unsafe_allow_html=True)
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Assessment", metrics.get('sustainability', 'N/A'))
            with col2:
                st.metric("Sustainability Score", f"{metrics.get('sustainability_score', 0)}/100")
            with col3:
                if 'fcf_coverage_ratio' in metrics:
                    st.metric("FCF Coverage", f"{metrics['fcf_coverage_ratio']}x")
            
            if 'coverage_health' in metrics:
                st.info(f"**Coverage Health:** {metrics['coverage_health']}")
            
            # Overall rating
            st.markdown("---")
            st.info(f"**Overall Rating:** {metrics.get('dividend_rating', 'N/A')}")
        
        elif dividend_data['status'] == 'no_dividend':
            st.info(dividend_data['message'])
        else:
            st.error(dividend_data['message'])
    
    # ====================================
    # SUB-TAB 3: VALUATION MULTIPLES
    # ====================================
    with analysis_sub3:
        st.markdown(f"### {icon('currency-dollar', '1.2em')} Valuation Multiples", unsafe_allow_html=True)
        
        with st.spinner("Analyzing valuation..."):
            valuation_data = analyze_valuation_multiples(ticker)
        
        if valuation_data['status'] == 'success':
            metrics = valuation_data['metrics']
            
            # Flip card metrics at top (if available)
            if FLIP_CARDS_AVAILABLE:
                render_valuation_flip_metrics(valuation_data)
                st.markdown("---")
            
            # P/E Ratios
            st.markdown(f"#### {icon('percent', '1.1em')} P/E Ratios", unsafe_allow_html=True)
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Trailing P/E", metrics.get('pe_trailing', 'N/A'))
            with col2:
                st.metric("Forward P/E", metrics.get('pe_forward', 'N/A'))
            with col3:
                peg = metrics.get('peg_ratio', 'N/A')
                st.metric("PEG Ratio", peg)
            
            if 'peg_interpretation' in metrics:
                st.info(f"**PEG Assessment:** {metrics['peg_interpretation']}")
            
            st.markdown("---")
            
            # Enterprise Value Ratios
            st.markdown(f"#### {icon('building', '1.1em')} Enterprise Value Ratios", unsafe_allow_html=True)
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                if 'enterprise_value' in metrics:
                    ev = metrics['enterprise_value'] / 1e9
                    st.metric("EV", f"${ev:.2f}B")
            with col2:
                st.metric("EV/EBITDA", metrics.get('ev_to_ebitda', 'N/A'))
            with col3:
                st.metric("EV/Revenue", metrics.get('ev_to_revenue', 'N/A'))
            with col4:
                st.metric("EV/EBIT", metrics.get('ev_to_ebit', 'N/A'))
            
            st.markdown("---")
            
            # Price Ratios
            st.markdown(f"#### {icon('tag', '1.1em')} Price Ratios", unsafe_allow_html=True)
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Price/Book", metrics.get('price_to_book', 'N/A'))
            with col2:
                st.metric("Price/Sales", metrics.get('price_to_sales', 'N/A'))
            with col3:
                st.metric("Price/FCF", metrics.get('price_to_fcf', 'N/A'))
            
            # Valuation Assessment
            st.markdown("---")
            st.markdown(f"#### {icon('clipboard-check', '1.1em')} Assessment", unsafe_allow_html=True)
            
            if metrics.get('valuation_signals'):
                st.markdown("**Signals:**")
                for signal in metrics['valuation_signals']:
                    st.write(f"• {signal}")
            
            overall = metrics.get('overall_valuation', 'N/A')
            if overall == 'Expensive':
                st.warning(f"**Overall Valuation:** {overall}")
            elif overall == 'Cheap':
                st.success(f"**Overall Valuation:** {overall}")
            else:
                st.info(f"**Overall Valuation:** {overall}")
        
        else:
            st.error(valuation_data['message'])
    
    # ====================================
    # SUB-TAB 4: CASH FLOW DEEP DIVE
    # ====================================
    with analysis_sub4:
        st.markdown(f"### {icon('cash-stack', '1.2em')} Cash Flow Deep Dive", unsafe_allow_html=True)
        
        with st.spinner("Analyzing cash flow..."):
            cashflow_data = analyze_cashflow(ticker)
        
        if cashflow_data['status'] == 'success':
            metrics = cashflow_data['metrics']
            
            # Flip card metrics at top (if available)
            if FLIP_CARDS_AVAILABLE:
                render_cashflow_flip_metrics(cashflow_data)
            else:
                # Fallback to standard metrics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("CF Score", f"{metrics.get('cashflow_score', 0)}/100",
                             help="Cash flow quality: FCF Consistency + Conversion + Earnings Quality + Margins")
                with col2:
                    if 'free_cash_flow' in metrics:
                        fcf = metrics['free_cash_flow'] / 1e9
                        st.metric("FCF", f"${fcf:.2f}B")
                with col3:
                    st.metric("FCF Margin", f"{metrics.get('fcf_margin', 0)}%")
                with col4:
                    st.metric("OCF Margin", f"{metrics.get('ocf_margin', 0)}%")
            
            st.markdown("---")
            
            # Quality metrics
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"#### {icon('check-circle', '1.1em')} Quality & Conversion", unsafe_allow_html=True)
                st.metric("FCF Conversion Rate", f"{metrics.get('fcf_conversion_rate', 0)}%")
                st.metric("Conversion Quality", metrics.get('conversion_quality', 'N/A'))
                st.metric("CF/NI Ratio", metrics.get('cf_to_ni_ratio', 'N/A'))
                st.metric("Earnings Quality", metrics.get('earnings_quality', 'N/A'))
            
            with col2:
                st.markdown(f"#### {icon('tools', '1.1em')} CapEx & Efficiency", unsafe_allow_html=True)
                if 'capital_expenditure' in metrics:
                    capex = abs(metrics['capital_expenditure']) / 1e9
                    st.metric("CapEx", f"${capex:.2f}B")
                st.metric("CapEx Intensity", f"{metrics.get('capex_intensity', 0)}%")
                st.metric("CapEx Profile", metrics.get('capex_profile', 'N/A'))
                st.metric("CapEx/OCF", f"{metrics.get('capex_to_ocf_ratio', 0)}%")
            
            # Stability
            st.markdown("---")
            st.markdown(f"#### {icon('graph-down', '1.1em')} Stability & Trends", unsafe_allow_html=True)
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("FCF Consistency", metrics.get('fcf_consistency', 'N/A'))
            with col2:
                st.metric("FCF Stability", f"{metrics.get('fcf_stability', 0)}%")
            with col3:
                st.metric("Avg FCF Growth", f"{metrics.get('fcf_growth_avg', 0)}%")
            
            # Overall rating
            st.markdown("---")
            st.info(f"**Cash Flow Rating:** {metrics.get('cashflow_rating', 'N/A')}")
        
        else:
            st.error(cashflow_data['message'])
    
    # ====================================
    # SUB-TAB 5: BALANCE SHEET HEALTH
    # ====================================
    with analysis_sub5:
        st.markdown(f"### {icon('shield-fill-check', '1.2em')} Balance Sheet Health", unsafe_allow_html=True)
        
        with st.spinner("Analyzing balance sheet..."):
            bs_data = analyze_balance_sheet_health(ticker)
        
        if bs_data['status'] == 'success':
            metrics = bs_data['metrics']
            
            # Flip card metrics at top (if available)
            if FLIP_CARDS_AVAILABLE:
                render_balance_flip_metrics(bs_data)
            else:
                # Fallback to standard metrics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("BS Score", f"{metrics.get('balance_sheet_score', 0)}/100",
                             help="Balance sheet strength: Liquidity + Leverage + Asset Quality + Debt Coverage")
                with col2:
                    st.metric("Current Ratio", metrics.get('current_ratio', 'N/A'))
                with col3:
                    st.metric("D/E Ratio", metrics.get('debt_to_equity', 'N/A'))
                with col4:
                    if 'working_capital' in metrics:
                        wc = metrics['working_capital'] / 1e9
                        st.metric("Working Capital", f"${wc:.2f}B")
            
            st.markdown("---")
            
            # Liquidity and Leverage
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"#### {icon('droplet', '1.1em')} Liquidity", unsafe_allow_html=True)
                st.metric("Current Ratio", f"{metrics.get('current_ratio', 'N/A')} - {metrics.get('current_ratio_health', 'N/A')}")
                st.metric("Quick Ratio", f"{metrics.get('quick_ratio', 'N/A')} - {metrics.get('quick_ratio_health', 'N/A')}")
                st.metric("Cash Ratio", f"{metrics.get('cash_ratio', 'N/A')} - {metrics.get('cash_ratio_health', 'N/A')}")
            
            with col2:
                st.markdown(f"#### {icon('graph-down', '1.1em')} Leverage", unsafe_allow_html=True)
                st.metric("Debt/Equity", f"{metrics.get('debt_to_equity', 'N/A')} - {metrics.get('debt_to_equity_health', 'N/A')}")
                st.metric("Debt/Assets", f"{metrics.get('debt_to_assets', 'N/A')} - {metrics.get('debt_to_assets_health', 'N/A')}")
                st.metric("Equity Ratio", f"{metrics.get('equity_ratio', 'N/A')} - {metrics.get('equity_ratio_health', 'N/A')}")
            
            # Asset Quality & Coverage
            st.markdown("---")
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"#### {icon('gem', '1.1em')} Asset Quality", unsafe_allow_html=True)
                st.metric("Tangible Asset Ratio", metrics.get('tangible_asset_ratio', 'N/A'))
                st.metric("Quality Assessment", metrics.get('asset_quality', 'N/A'))
                if 'working_capital_ratio' in metrics:
                    st.metric("WC/Assets", f"{metrics['working_capital_ratio']}%")
            
            with col2:
                st.markdown(f"#### {icon('cash', '1.1em')} Debt Servicing", unsafe_allow_html=True)
                st.metric("Interest Coverage", f"{metrics.get('interest_coverage', 'N/A')}x")
                st.metric("Coverage Health", metrics.get('interest_coverage_health', 'N/A'))
            
            # Overall rating
            st.markdown("---")
            rating = metrics.get('balance_sheet_rating', 'N/A')
            if 'Fortress' in rating or 'Excellent' in rating:
                st.success(f"**Balance Sheet Rating:** {rating}")
            elif 'Strong' in rating:
                st.info(f"**Balance Sheet Rating:** {rating}")
            else:
                st.warning(f"**Balance Sheet Rating:** {rating}")
        
        else:
            st.error(bs_data['message'])
    
    # ====================================
    # SUB-TAB 6: MANAGEMENT EFFECTIVENESS
    # ====================================
    with analysis_sub6:
        st.markdown(f"### {icon('person-badge', '1.2em')} Management Effectiveness", unsafe_allow_html=True)
        
        with st.spinner("Analyzing management performance..."):
            mgmt_data = analyze_management_effectiveness(ticker)
        
        if mgmt_data['status'] == 'success':
            metrics = mgmt_data['metrics']
            
            # Flip card metrics at top (if available)
            if FLIP_CARDS_AVAILABLE:
                render_management_flip_metrics(mgmt_data)
            else:
                # Fallback to standard metrics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Mgmt Score", f"{metrics.get('management_score', 0)}/100",
                             help="Management effectiveness: ROE + ROA + Asset Efficiency + Profitability + Productivity")
                with col2:
                    st.metric("ROE", f"{metrics.get('return_on_equity', 'N/A')}%")
                with col3:
                    st.metric("ROA", f"{metrics.get('return_on_assets', 'N/A')}%")
                with col4:
                    st.metric("Asset Turnover", metrics.get('asset_turnover', 'N/A'))
            
            st.markdown("---")
            
            # Returns and Efficiency
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"#### {icon('trophy', '1.1em')} Returns", unsafe_allow_html=True)
                st.metric("Return on Equity", f"{metrics.get('return_on_equity', 'N/A')}%")
                st.metric("ROE Quality", metrics.get('roe_quality', 'N/A'))
                st.metric("Return on Assets", f"{metrics.get('return_on_assets', 'N/A')}%")
                st.metric("ROA Quality", metrics.get('roa_quality', 'N/A'))
            
            with col2:
                st.markdown(f"#### {icon('gear', '1.1em')} Efficiency", unsafe_allow_html=True)
                st.metric("Asset Turnover", f"{metrics.get('asset_turnover', 'N/A')} - {metrics.get('asset_efficiency', 'N/A')}")
                if 'receivables_turnover' in metrics:
                    st.metric("Receivables Turnover", f"{metrics['receivables_turnover']}x")
                    st.metric("DSO", f"{metrics.get('days_sales_outstanding', 'N/A')} days")
                if 'inventory_turnover' in metrics:
                    st.metric("Inventory Turnover", f"{metrics['inventory_turnover']}x")
            
            # Productivity and Capital Allocation
            st.markdown("---")
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"#### {icon('people', '1.1em')} Productivity", unsafe_allow_html=True)
                if 'total_employees' in metrics:
                    st.metric("Employees", f"{metrics['total_employees']:,}")
                if 'revenue_per_employee' in metrics:
                    st.metric("Revenue/Employee", f"${metrics['revenue_per_employee']:,.0f}")
                if 'profit_per_employee' in metrics:
                    st.metric("Profit/Employee", f"${metrics['profit_per_employee']:,.0f}")
                st.metric("Productivity Level", metrics.get('productivity_level', 'N/A'))
            
            with col2:
                st.markdown(f"#### {icon('wallet2', '1.1em')} Capital Allocation", unsafe_allow_html=True)
                if 'shares_outstanding_change' in metrics:
                    st.metric("Share Count Change", f"{metrics['shares_outstanding_change']}%")
                    st.metric("Activity", metrics.get('buyback_activity', 'N/A'))
                if 'dividend_payout_ratio' in metrics:
                    st.metric("Payout Ratio", f"{metrics['dividend_payout_ratio']}%")
                    st.metric("Policy", metrics.get('dividend_policy', 'N/A'))
            
            # Profitability Management
            st.markdown("---")
            st.markdown(f"#### {icon('graph-up', '1.1em')} Profitability Management", unsafe_allow_html=True)
            col1, col2, col3 = st.columns(3)
            with col1:
                if 'gross_margin' in metrics:
                    st.metric("Gross Margin", f"{metrics['gross_margin']}%")
            with col2:
                if 'operating_margin' in metrics:
                    st.metric("Operating Margin", f"{metrics['operating_margin']}%")
            with col3:
                if 'profit_margin' in metrics:
                    st.metric("Profit Margin", f"{metrics['profit_margin']}%")
            
            st.info(f"**Quality:** {metrics.get('profitability_management', 'N/A')}")
            
            # Overall rating
            st.markdown("---")
            rating = metrics.get('management_rating', 'N/A')
            if rating == 'Elite':
                st.success(f"**Management Rating:** {rating}")
            elif rating == 'Strong':
                st.info(f"**Management Rating:** {rating}")
            else:
                st.warning(f"**Management Rating:** {rating}")
        
        else:
            st.error(mgmt_data['message'])
    
    # ====================================
    # SUB-TAB 7: GROWTH QUALITY
    # ====================================
    with analysis_sub7:
        st.markdown(f"### {icon('rocket-takeoff', '1.2em')} Growth Quality", unsafe_allow_html=True)
        
        with st.spinner("Analyzing growth quality..."):
            growth_data = analyze_growth_quality(ticker)
        
        if growth_data['status'] == 'success':
            metrics = growth_data['metrics']
            
            # Flip card metrics at top (if available)
            if FLIP_CARDS_AVAILABLE:
                render_growth_flip_metrics(growth_data)
            else:
                # Fallback to standard metrics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Growth Score", f"{metrics.get('growth_quality_score', 0)}/100",
                             help="Growth quality: Revenue Growth + Consistency + Profitability Trend + Self-Funding Ability")
                with col2:
                    st.metric("Revenue Growth", f"{metrics.get('revenue_growth_rate', 'N/A')}%")
                with col3:
                    st.metric("Earnings Growth", f"{metrics.get('earnings_growth_rate', 'N/A')}%")
                with col4:
                    st.metric("Momentum", metrics.get('growth_momentum', 'N/A'))
            
            st.markdown("---")
            
            # Growth Rates and Consistency
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"#### {icon('graph-up-arrow', '1.1em')} Growth Rates", unsafe_allow_html=True)
                st.metric("Revenue Growth", f"{metrics.get('revenue_growth_rate', 'N/A')}%")
                st.metric("Quality", metrics.get('revenue_growth_quality', 'N/A'))
                st.metric("Earnings Growth", f"{metrics.get('earnings_growth_rate', 'N/A')}%")
                st.metric("Quality", metrics.get('earnings_growth_quality', 'N/A'))
                st.metric("Profitability Trend", metrics.get('profitability_trend', 'N/A'))
            
            with col2:
                st.markdown(f"#### {icon('activity', '1.1em')} Consistency", unsafe_allow_html=True)
                st.metric("Revenue Consistency", metrics.get('revenue_consistency', 'N/A'))
                if 'revenue_growth_volatility' in metrics:
                    st.metric("Growth Volatility", f"{metrics['revenue_growth_volatility']}%")
                if 'quarterly_revenue_growth' in metrics:
                    st.metric("Q/Q Revenue Growth", f"{metrics['quarterly_revenue_growth']}%")
                if 'quarterly_earnings_growth' in metrics:
                    st.metric("Q/Q Earnings Growth", f"{metrics['quarterly_earnings_growth']}%")
                st.metric("Growth Momentum", metrics.get('growth_momentum', 'N/A'))
            
            # Efficiency and Funding
            st.markdown("---")
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"#### {icon('speedometer', '1.1em')} Efficiency", unsafe_allow_html=True)
                if 'revenue_per_employee_current' in metrics:
                    st.metric("Revenue/Employee", f"${metrics['revenue_per_employee_current']:,.0f}")
                st.metric("Productivity", metrics.get('employee_productivity', 'N/A'))
                if 'operating_efficiency_ratio' in metrics:
                    st.metric("Operating Efficiency", f"{metrics['operating_efficiency_ratio']}")
                st.metric("Cost Control", metrics.get('cost_control', 'N/A'))
            
            with col2:
                st.markdown(f"#### {icon('bank', '1.1em')} Growth Funding", unsafe_allow_html=True)
                if 'total_cash' in metrics:
                    st.metric("Cash", f"${metrics['total_cash']/1e9:.2f}B")
                if 'cash_to_market_cap' in metrics:
                    st.metric("Cash/Market Cap", f"{metrics['cash_to_market_cap']}%")
                st.metric("Financial Flexibility", metrics.get('financial_flexibility', 'N/A'))
                if 'fcf_margin' in metrics:
                    st.metric("FCF Margin", f"{metrics['fcf_margin']}%")
                st.metric("Funding Quality", metrics.get('growth_funding_quality', 'N/A'))
            
            # Market Expectations
            if 'analyst_upside' in metrics:
                st.markdown("---")
                st.markdown(f"#### {icon('binoculars', '1.1em')} Market Expectations", unsafe_allow_html=True)
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Analyst Upside", f"{metrics['analyst_upside']}%")
                with col2:
                    st.metric("Growth Expectations", metrics.get('growth_expectations', 'N/A'))
            
            # Overall rating
            st.markdown("---")
            rating = metrics.get('growth_quality_rating', 'N/A')
            if 'Excellent' in rating:
                st.success(f"**Growth Quality Rating:** {rating}")
            elif 'Good' in rating:
                st.info(f"**Growth Quality Rating:** {rating}")
            else:
                st.warning(f"**Growth Quality Rating:** {rating}")
        
        else:
            st.error(growth_data['message'])


# ============================================================================
# TESTING CODE
# ============================================================================

if __name__ == "__main__":
    print("="*80)
    print("TESTING ANALYSIS TAB MODULE")
    print("="*80)
    
    # Test import
    print("\n[TEST] Module imports successful")
    
    # Note: Actual rendering requires Streamlit context
    print("[OK] Module ready for integration")
    
    print("\n" + "="*80)




