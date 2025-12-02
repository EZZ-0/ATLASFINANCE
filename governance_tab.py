"""
GOVERNANCE TAB - CORPORATE GOVERNANCE ANALYSIS
================================================================================
Extracted from usa_app.py for modularity.

Contains 6 sub-tabs for comprehensive governance analysis:
1. Overview - Governance score and assessment
2. Board & Score - Board composition and AGS scoring
3. Ownership Structure - Equity, capital structure, shareholder rights
4. Insider Trading - Recent insider transactions
5. Institutional Holdings - Top institutional owners
6. SEC Filings - Direct links to Edgar filings

Author: Atlas Financial Intelligence
Date: November 2025
Phase: Refactoring - Phase 2
"""

import streamlit as st
import pandas as pd
from typing import Dict


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


def render_governance_tab(ticker: str, financials: Dict) -> None:
    """
    Render Corporate Governance tab with 6 sub-tabs
    
    Args:
        ticker: Stock ticker symbol
        financials: Financial data dictionary
        
    Returns:
        None (renders directly to Streamlit)
    """
    
    st.markdown(f"## {icon('shield-check', '1.5em')} Corporate Governance", unsafe_allow_html=True)
    
    st.info("ℹ️ Comprehensive governance analysis including board composition, ownership structure, and shareholder rights.")
    
    # Sub-tabs for governance sections
    gov_overview_tab, board_tab, ownership_tab, insider_tab, institutional_tab, sec_tab = st.tabs([
        "Overview", "Board & Score", "Ownership Structure", "Insider Trading", "Institutional Holdings", "SEC Filings"
    ])
    
    # ==========================================
    # GOV TAB 1: OVERVIEW
    # ==========================================
    with gov_overview_tab:
        try:
            from governance_analysis import analyze_governance
            from format_helpers import format_large_number, external_link
            
            with st.spinner("Analyzing governance..."):
                gov_data = analyze_governance(ticker)
                
                if gov_data['status'] == 'success':
                    st.subheader(f"Governance Overview: {gov_data['company_name']}")
                    
                    # Top-level metrics
                    col1, col2, col3, col4 = st.columns(4)
                    
                    score = gov_data.get('governance_score', {})
                    assessment = gov_data.get('overall_assessment', {})
                    
                    with col1:
                        if score.get('overall_grade'):
                            st.metric("Governance Grade", score['overall_grade'],
                                     help="Atlas Governance Score (AGS) - Similar to ISS methodology")
                    
                    with col2:
                        if score.get('overall_score'):
                            st.metric("AGS Score", f"{score['overall_score']}/10",
                                     help="Lower scores are better (1=Best, 10=Worst)")
                    
                    with col3:
                        if score.get('risk_level'):
                            st.metric("Risk Level", score['risk_level'])
                    
                    with col4:
                        st.metric("Overall Grade", assessment.get('overall_grade', 'N/A'))
                    
                    st.markdown("---")
                    
                    # Strengths & Concerns
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"### {icon('check-circle', '1.2em')} Strengths", unsafe_allow_html=True)
                        strengths = assessment.get('strengths', [])
                        if strengths:
                            for strength in strengths:
                                st.markdown(f"✅ {strength}")
                        else:
                            st.caption("No major strengths identified")
                    
                    with col2:
                        st.markdown(f"### {icon('exclamation-triangle', '1.2em')} Concerns", unsafe_allow_html=True)
                        concerns = assessment.get('concerns', [])
                        if concerns:
                            for concern in concerns:
                                st.markdown(f"⚠️ {concern}")
                        else:
                            st.caption("No major concerns identified")
                    
                    st.markdown("---")
                    
                    # Recommendations
                    st.markdown(f"### {icon('lightbulb', '1.2em')} Recommendations", unsafe_allow_html=True)
                    recommendations = assessment.get('recommendations', [])
                    if recommendations:
                        for rec in recommendations:
                            st.info(f"💡 {rec}")
                else:
                    st.warning(gov_data.get('message', 'Unable to fetch governance data'))
        
        except Exception as e:
            st.error(f"Error analyzing governance: {str(e)}")
    
    # ==========================================
    # GOV TAB 2: BOARD & SCORE
    # ==========================================
    with board_tab:
        try:
            from governance_analysis import analyze_governance
            
            with st.spinner("Analyzing board composition..."):
                gov_data = analyze_governance(ticker)
                
                if gov_data['status'] == 'success':
                    st.subheader("Board of Directors")
                    
                    board = gov_data.get('board', {})
                    score = gov_data.get('governance_score', {})
                    
                    # Board composition
                    if board.get('total_directors'):
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric("Total Directors", board['total_directors'])
                        
                        with col2:
                            st.metric("Independent", f"~{board['independent_directors']}")
                        
                        with col3:
                            st.metric("Insider", f"~{board['insider_directors']}")
                        
                        with col4:
                            st.metric("Independence", f"{board['independence_ratio']*100:.0f}%")
                        
                        st.progress(board['independence_ratio'])
                        
                        # Assessment
                        st.markdown("---")
                        st.markdown(f"**Board Size Assessment:** {board['board_size_assessment']}")
                        st.caption(board.get('board_risk', ''))
                        
                        if board.get('estimated'):
                            st.warning("⚠️ Note: Independence figures are estimated based on industry averages. See Proxy Statement (DEF 14A) for exact data.")
                    
                    st.markdown("---")
                    
                    # Governance Score Breakdown
                    st.subheader("Atlas Governance Score (AGS)")
                    
                    st.info(f"ℹ️ {score.get('methodology_note', '')}")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Overall Score", f"{score.get('overall_score', 'N/A')}/10",
                                 help="Lower is better (ISS-style)")
                    
                    with col2:
                        st.metric("Grade", score.get('overall_grade', 'N/A'),
                                 help=score.get('grade_interpretation', ''))
                    
                    with col3:
                        st.metric("Risk Level", score.get('risk_level', 'N/A'))
                    
                    st.markdown("---")
                    
                    # Score components
                    st.markdown("### Score Components")
                    
                    components_col1, components_col2 = st.columns(2)
                    
                    with components_col1:
                        st.metric("Board Structure (40%)", f"{score.get('board_score', 'N/A')}/10")
                        st.metric("Shareholder Rights (20%)", f"{score.get('shareholder_rights_score', 'N/A')}/10")
                    
                    with components_col2:
                        st.metric("Compensation (25%)", f"{score.get('compensation_score', 'N/A')}/10")
                        st.metric("Audit & Risk (15%)", f"{score.get('audit_score', 'N/A')}/10")
                    
                    st.caption(score.get('interpretation', ''))
                else:
                    st.warning(gov_data.get('message', 'Unable to fetch board data'))
        
        except Exception as e:
            st.error(f"Error analyzing board: {str(e)}")
    
    # ==========================================
    # GOV TAB 3: OWNERSHIP STRUCTURE
    # ==========================================
    with ownership_tab:
        try:
            from governance_analysis import analyze_governance
            from format_helpers import format_large_number
            
            with st.spinner("Analyzing ownership structure..."):
                gov_data = analyze_governance(ticker)
                
                if gov_data['status'] == 'success':
                    equity = gov_data.get('equity_structure', {})
                    capital = gov_data.get('capital_structure', {})
                    rights = gov_data.get('shareholder_rights', {})
                    
                    # Equity Structure
                    st.subheader("Equity Structure")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        shares_out = equity.get('shares_outstanding', 'N/A')
                        if shares_out and shares_out != 'N/A':
                            st.metric("Shares Outstanding", format_large_number(shares_out, 'number', 2))
                        else:
                            st.metric("Shares Outstanding", "N/A")
                    
                    with col2:
                        float_shares = equity.get('float_shares', 'N/A')
                        if float_shares and float_shares != 'N/A':
                            st.metric("Float Shares", format_large_number(float_shares, 'number', 2))
                        else:
                            st.metric("Float Shares", "N/A")
                    
                    with col3:
                        if equity.get('free_float_ratio'):
                            st.metric("Free Float", f"{equity['free_float_ratio']*100:.1f}%")
                        else:
                            st.metric("Free Float", "N/A")
                    
                    if equity.get('liquidity_assessment'):
                        st.info(f"**Liquidity:** {equity['liquidity_assessment']}")
                    
                    st.markdown("---")
                    
                    # Ownership Breakdown
                    st.subheader("Ownership Breakdown")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if equity.get('insider_ownership_pct'):
                            st.metric("Insider Ownership", f"{equity['insider_ownership_pct']*100:.2f}%")
                            st.progress(equity['insider_ownership_pct'])
                    
                    with col2:
                        if equity.get('institutional_ownership_pct'):
                            st.metric("Institutional Ownership", f"{equity['institutional_ownership_pct']*100:.2f}%")
                            st.progress(equity['institutional_ownership_pct'])
                    
                    st.markdown("---")
                    
                    # Short Interest
                    if equity.get('shares_short'):
                        st.subheader("Short Interest")
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.markdown(format_large_number(equity['shares_short'], 'number', 2), 
                                       unsafe_allow_html=True)
                            st.caption("Shares Short")
                        
                        with col2:
                            if equity.get('short_percent_of_float'):
                                st.metric("% of Float", f"{equity['short_percent_of_float']*100:.2f}%")
                        
                        with col3:
                            if equity.get('short_ratio'):
                                st.metric("Days to Cover", f"{equity['short_ratio']:.1f}")
                    
                    st.markdown("---")
                    
                    # Capital Structure
                    st.subheader("Capital Structure")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if capital.get('total_debt'):
                            st.markdown(format_large_number(capital['total_debt'], 'currency', 2), 
                                       unsafe_allow_html=True)
                            st.caption("Total Debt")
                    
                    with col2:
                        if capital.get('total_cash'):
                            st.markdown(format_large_number(capital['total_cash'], 'currency', 2), 
                                       unsafe_allow_html=True)
                            st.caption("Total Cash")
                    
                    with col3:
                        if capital.get('net_debt'):
                            st.markdown(format_large_number(capital['net_debt'], 'currency', 2), 
                                       unsafe_allow_html=True)
                            st.caption("Net Debt")
                    
                    # Leverage ratios
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if capital.get('debt_to_equity'):
                            st.metric("Debt/Equity", f"{capital['debt_to_equity']:.2f}x")
                    
                    with col2:
                        if capital.get('debt_to_capital'):
                            st.metric("Debt/Capital", f"{capital['debt_to_capital']*100:.1f}%")
                    
                    with col3:
                        if capital.get('interest_coverage'):
                            st.metric("Interest Coverage", f"{capital['interest_coverage']:.1f}x")
                    
                    if capital.get('leverage_assessment'):
                        assessment_color = {
                            'Conservative': 'green',
                            'Moderate': 'blue',
                            'High': 'orange',
                            'Very High': 'red'
                        }.get(capital['leverage_assessment'], 'gray')
                        
                        st.markdown(f"<div style='background: {assessment_color}; color: white; padding: 10px; border-radius: 5px; text-align: center;'><strong>{capital['leverage_assessment']} Leverage</strong><br>{capital.get('leverage_note', '')}</div>", unsafe_allow_html=True)
                    
                    st.markdown("---")
                    
                    # Shareholder Rights
                    st.subheader("Shareholder Rights")
                    
                    if rights.get('dual_class_shares'):
                        st.warning(f"⚠️ {rights.get('dual_class_note', 'Dual-class share structure detected')}")
                    else:
                        st.success("✅ No dual-class share structure detected")
                    
                    # Top Shareholders
                    if gov_data.get('top_shareholders'):
                        st.markdown("---")
                        st.subheader("Top 10 Shareholders")
                        
                        holders_df = pd.DataFrame(gov_data['top_shareholders'])
                        
                        # Format display
                        if not holders_df.empty:
                            display_df = holders_df[['holder', 'shares', 'percent_out', 'date_reported']].copy()
                            display_df.columns = ['Holder', 'Shares', '% Outstanding', 'Date Reported']
                            
                            # Format shares
                            if 'Shares' in display_df.columns:
                                display_df['Shares'] = display_df['Shares'].apply(lambda x: f"{x:,.0f}")
                            
                            # Format percentage
                            if '% Outstanding' in display_df.columns:
                                display_df['% Outstanding'] = display_df['% Outstanding'].apply(lambda x: f"{x:.2f}%" if isinstance(x, (int, float)) else x)
                            
                            st.dataframe(display_df, use_container_width=True, height=400)
                else:
                    st.warning(gov_data.get('message', 'Unable to fetch ownership data'))
        
        except Exception as e:
            st.error(f"Error analyzing ownership: {str(e)}")
    
    # ==========================================
    # GOV TAB 4: INSIDER TRADING (EXISTING)
    # ==========================================
    with insider_tab:
        try:
            from insider_institutional import get_insider_transactions
            
            st.subheader("Recent Insider Transactions")
            
            with st.spinner("Fetching insider data..."):
                insider_data = get_insider_transactions(ticker, limit=20)
                
                if insider_data['status'] == 'success':
                    summary = insider_data['summary']
                    
                    # Summary metrics
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Total Transactions", summary['total_transactions'])
                    
                    with col2:
                        st.metric("Buys", summary['num_buys'])
                    
                    with col3:
                        st.metric("Sells", summary['num_sells'])
                    
                    with col4:
                        st.metric("Sentiment", insider_data['sentiment'])
                    
                    # Buy/Sell Ratio
                    if summary['num_buys'] + summary['num_sells'] > 0:
                        st.progress(summary['buy_ratio'])
                        st.caption(f"Buy Ratio: {summary['buy_ratio']*100:.1f}%")
                    
                    st.markdown("---")
                    
                    # Transactions table
                    if not insider_data['transactions'].empty:
                        st.markdown("### Recent Transactions")
                        st.dataframe(insider_data['transactions'], use_container_width=True, height=400)
                else:
                    st.warning(insider_data['message'])
                    
        except Exception as e:
            st.error(f"Error fetching insider data: {str(e)}")
    
    with institutional_tab:
        try:
            from insider_institutional import get_institutional_holders
            
            st.subheader("Institutional Ownership")
            
            with st.spinner("Fetching institutional data..."):
                inst_data = get_institutional_holders(ticker)
                
                if inst_data['status'] == 'success':
                    summary = inst_data['summary']
                    
                    # Summary metrics
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Total Holders", summary['total_holders'])
                    
                    with col2:
                        st.metric("Institutional Ownership", f"{summary['institutional_ownership_pct']:.2f}%")
                    
                    with col3:
                        st.metric("Top 5 Concentration", f"{summary['top_5_concentration']:.2f}%")
                    
                    st.markdown("---")
                    
                    # Holders table
                    if not inst_data['holders'].empty:
                        st.markdown("### Top Institutional Holders")
                        st.dataframe(inst_data['holders'], use_container_width=True, height=400)
                else:
                    st.warning(inst_data['message'])
                    
        except Exception as e:
            st.error(f"Error fetching institutional data: {str(e)}")
    
    # ==========================================
    # GOV TAB 6: SEC FILINGS
    # ==========================================
    with sec_tab:
        try:
            from governance_analysis import analyze_governance
            from format_helpers import external_link
            
            with st.spinner("Fetching SEC filing links..."):
                gov_data = analyze_governance(ticker)
                
                if gov_data['status'] == 'success':
                    sec = gov_data.get('sec_links', {})
                    
                    st.subheader("SEC Edgar Filings")
                    
                    st.info("""
                    ℹ️ **SEC Edgar Filing Links:**
                    - ✅ Instant access for 140+ most-traded stocks (S&P 500 + popular names)
                    - ⚠️ Other US stocks require SEC API registration (in progress)
                    - 📋 **To enable full coverage:** Update contact email and register with SEC
                    - 🔗 If unavailable, visit [sec.gov](https://www.sec.gov/edgar/searchedgar/companysearch) and search manually
                    """)
                    
                    if sec.get('cik'):
                        st.info(f"**CIK (Central Index Key):** {sec['cik']}")
                        
                        st.markdown("---")
                        
                        # Key filings
                        st.markdown("### Key Governance Filings")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown(f"#### {icon('file-text', '1.1em')} Proxy Statement (DEF 14A)", unsafe_allow_html=True)
                            st.caption("Board composition, executive compensation, shareholder proposals")
                            if sec.get('proxy_statement'):
                                st.markdown(external_link(sec['proxy_statement'], "View Proxy Statements →"), unsafe_allow_html=True)
                            else:
                                st.caption("Link not available")
                        
                        with col2:
                            st.markdown(f"#### {icon('file-text', '1.1em')} Annual Report (10-K)", unsafe_allow_html=True)
                            st.caption("Complete financial statements, risk factors, MD&A")
                            if sec.get('annual_report'):
                                st.markdown(external_link(sec['annual_report'], "View 10-K Filings →"), unsafe_allow_html=True)
                            else:
                                st.caption("Link not available")
                        
                        st.markdown("---")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown(f"#### {icon('file-text', '1.1em')} Current Reports (8-K)", unsafe_allow_html=True)
                            st.caption("Material events, earnings releases, major announcements")
                            if sec.get('current_reports'):
                                st.markdown(external_link(sec['current_reports'], "View 8-K Filings →"), unsafe_allow_html=True)
                            else:
                                st.caption("Link not available")
                        
                        with col2:
                            st.markdown(f"#### {icon('folder', '1.1em')} All Filings", unsafe_allow_html=True)
                            st.caption("Complete filing history")
                            if sec.get('all_filings'):
                                st.markdown(external_link(sec['all_filings'], "View All Filings →"), unsafe_allow_html=True)
                            else:
                                st.caption("Link not available")
                        
                        st.markdown("---")
                        
                        # Investor Relations
                        st.markdown("### Investor Relations")
                        
                        if sec.get('investor_relations'):
                            st.markdown(external_link(sec['investor_relations'], "Visit Investor Relations Page →"), unsafe_allow_html=True)
                            
                            # Show note if available
                            if sec.get('investor_relations_note'):
                                st.caption(f"ℹ️ {sec['investor_relations_note']}")
                        else:
                            st.caption("Investor Relations link not available")
                        
                        st.markdown("---")
                        
                        # Usage guide
                        st.markdown("### 📘 Filing Guide")
                        
                        st.markdown("""
                        **What to look for in each filing:**
                        
                        **Proxy Statement (DEF 14A):**
                        - Board of Directors composition & independence
                        - Executive compensation details (CEO pay ratio)
                        - Shareholder proposals & voting results
                        - Related party transactions
                        
                        **Annual Report (10-K):**
                        - Complete audited financial statements
                        - Management Discussion & Analysis (MD&A)
                        - Risk factors specific to the company
                        - Legal proceedings
                        - Segment reporting
                        
                        **Current Reports (8-K):**
                        - Quarterly earnings releases
                        - Major acquisitions or divestitures
                        - Changes in management or board
                        - Material agreements
                        - Bankruptcy or receivership
                        """)
                        
                        st.info("💡 **Tip:** All links open in a new tab so you can review filings without losing your analysis.")
                    else:
                        st.warning("Unable to retrieve CIK for SEC Edgar links")
                else:
                    st.warning(gov_data.get('message', 'Unable to fetch SEC filing data'))
        
        except Exception as e:
            st.error(f"Error fetching SEC filing links: {str(e)}")


# ============================================================================
# TESTING CODE
# ============================================================================

if __name__ == "__main__":
    print("="*80)
    print("TESTING GOVERNANCE TAB MODULE")
    print("="*80)
    
    # Test import
    print("\n[TEST] Module imports successful")
    
    # Note: Actual rendering requires Streamlit context
    print("[OK] Module ready for integration")
    
    print("\n" + "="*80)

