"""
ATLAS Financial Intelligence - Risk Tab
========================================
Forensic Shield + Corporate Governance analysis
Extracted from usa_app.py lines 3287-3444
"""

import streamlit as st
import pandas as pd

# Import UI components
from ui_components import smart_dataframe

# Import governance tab
from governance_tab import render_governance_tab


def icon(name, size="1em", color=None):
    """Render a Bootstrap Icon"""
    style = f"font-size: {size};"
    if color:
        style += f" color: {color};"
    return f'<i class="bi bi-{name}" style="{style}"></i>'


def render_risk_tab(ticker: str, financials: dict):
    """
    Render the Risk & Ownership tab with sub-tabs for Forensic and Governance.
    
    Args:
        ticker: Stock ticker symbol
        financials: Dictionary of financial data
    """
    risk_sub1, risk_sub2 = st.tabs(["Forensic Shield", "Corporate Governance"])
    
    # ==========================================
    # SUB-TAB 1: FORENSIC ANALYSIS
    # ==========================================
    with risk_sub1:
        st.markdown(f"## {icon('shield-check', '1.5em')} Forensic Shield: Risk Assessment", unsafe_allow_html=True)
        st.info("Advanced forensic accounting models to detect fraud, bankruptcy risk, and financial quality issues.")
        
        try:
            from forensic_shield import analyze_forensic_shield
            
            with st.spinner("Running forensic analysis..."):
                forensic_results = analyze_forensic_shield(financials)
                
                # Overall Assessment
                overall = forensic_results['overall_assessment']
                
                risk_colors = {
                    'LOW': '<span style="background: #28a745; color: white; padding: 6px 12px; border-radius: 4px; font-weight: bold;">LOW</span>',
                    'MODERATE': '<span style="background: #ff9800; color: white; padding: 6px 12px; border-radius: 4px; font-weight: bold;">MODERATE</span>',
                    'HIGH': '<span style="background: #d32f2f; color: white; padding: 6px 12px; border-radius: 4px; font-weight: bold;">HIGH</span>'
                }
                
                risk_html = risk_colors.get(overall['risk_level'], '<span style="background: #9e9e9e; color: white; padding: 6px 12px; border-radius: 4px; font-weight: bold;">UNKNOWN</span>')
                st.markdown(f"## Overall Risk: {risk_html}", unsafe_allow_html=True)
                st.markdown(f"**Summary:** {overall['summary']}")
                
                if overall.get('risk_factors'):
                    st.warning("**Risk Factors Identified:**")
                    for factor in overall['risk_factors']:
                        st.write(f"- {factor}")
                
                st.markdown("---")
                
                # Altman Z-Score
                _render_altman_zscore(forensic_results)
                
                st.markdown("---")
                
                # Beneish M-Score
                _render_beneish_mscore(forensic_results)
                
                st.markdown("---")
                
                # Piotroski F-Score
                _render_piotroski_fscore(forensic_results)
                    
        except Exception as e:
            st.error(f"Error running forensic analysis: {str(e)}")
    
    # ==========================================
    # SUB-TAB 2: CORPORATE GOVERNANCE
    # ==========================================
    with risk_sub2:
        render_governance_tab(ticker, financials)


def _render_altman_zscore(forensic_results: dict):
    """Render Altman Z-Score section"""
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
            smart_dataframe(comp_df.T, title=None, height=200, key="zscore_components_risk")
    else:
        st.warning(f"Altman Z-Score: {altman.get('message', 'Unavailable')}")


def _render_beneish_mscore(forensic_results: dict):
    """Render Beneish M-Score section"""
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
                    Red Flags Detected
                </p>
            </div>
            """, unsafe_allow_html=True)
            for flag in beneish['red_flags']:
                st.markdown(f"""
                <div style='padding: 0.6rem 1rem; margin: 0.4rem 0 0.4rem 1.5rem; 
                            background: rgba(244, 67, 54, 0.04); 
                            border-left: 3px solid rgba(244, 67, 54, 0.5); 
                            border-radius: 4px;'>
                    <p style='color: #ffcdd2; margin: 0; font-size: 0.95rem;'>- {flag}</p>
                </div>
                """, unsafe_allow_html=True)
        
        with st.expander("View M-Score Components"):
            comp_df = pd.DataFrame([beneish['components']])
            smart_dataframe(comp_df.T, title=None, height=200, key="mscore_components_risk")
    else:
        st.warning(f"Beneish M-Score: {beneish.get('message', 'Unavailable')}")


def _render_piotroski_fscore(forensic_results: dict):
    """Render Piotroski F-Score section"""
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
                    <p style='color: #81c784; margin: 0;'><strong>[PASS]</strong> {test}</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style='padding: 0.5rem 1rem; margin: 0.3rem 0; 
                            background: rgba(244, 67, 54, 0.08); 
                            border-left: 3px solid #F44336; border-radius: 4px;'>
                    <p style='color: #e57373; margin: 0;'><strong>[FAIL]</strong> {test}</p>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.warning(f"Piotroski F-Score: {piotroski.get('message', 'Unavailable')}")

