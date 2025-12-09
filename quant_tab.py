"""
QUANT TAB - QUANTITATIVE ANALYSIS (FAMA-FRENCH 3-FACTOR)
================================================================================
Extracted from usa_app.py for modularity.

Displays Fama-French 3-Factor model results:
- Cost of Equity calculation
- Alpha (excess returns)
- Beta exposures (Market, Size, Value)
- Risk premiums
- Model fit statistics
- Export functionality

Author: Atlas Financial Intelligence
Date: November 2025
Phase: Refactoring - Phase 4 (Final)
"""

import streamlit as st
import pandas as pd
from typing import Dict

# Import smart_dataframe with fallback for graceful degradation
try:
    from ui_components import smart_dataframe
    UI_COMPONENTS_AVAILABLE = True
except ImportError:
    UI_COMPONENTS_AVAILABLE = False
    def smart_dataframe(df, title=None, height=400, key=None, **kwargs):
        if title:
            st.markdown(f"**{title}**")
        st.dataframe(df, use_container_width=True, height=height, key=key)


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


def render_quant_tab(ticker: str, financials: Dict) -> None:
    """
    Render Quantitative Analysis tab with Fama-French 3-Factor model
    
    Args:
        ticker: Stock ticker symbol
        financials: Financial data dictionary
        
    Returns:
        None (renders directly to Streamlit)
    """
    
    st.markdown(f"## {icon('calculator', '1.5em')} Quantitative Analysis (Fama-French 3-Factor Model)", unsafe_allow_html=True)
    
    quant_data = financials.get("quant_analysis", {}) if financials else {}
    
    # If no quant data, try to fetch it on-demand
    if not quant_data and ticker:
        st.info("Loading Fama-French analysis...")
        
        try:
            from quant_engine import QuantEngine
            
            with st.spinner("Running Fama-French 3-Factor Analysis..."):
                quant = QuantEngine()
                quant_data = quant.analyze_stock(ticker)
                
                # Store in financials for future use (won't persist to cache but helps this session)
                if financials is not None:
                    financials["quant_analysis"] = quant_data
                    
        except ImportError as ie:
            st.warning("Quant engine not available. Install required dependencies.")
            st.markdown("""
            **What is Fama-French 3-Factor Analysis?**
            
            The Fama-French 3-Factor model extends CAPM by adding:
            - **Market Risk Premium (Mkt-RF)**: Excess return of market over risk-free rate
            - **Size Factor (SMB)**: Small vs Big - premium for smaller companies
            - **Value Factor (HML)**: High vs Low book-to-market - premium for value stocks
            
            This helps explain stock returns beyond just market beta.
            """)
            return
        except Exception as e:
            st.error(f"Error running quant analysis: {e}")
            return
    
    if not quant_data:
        st.warning("Unable to load quant analysis data.")
        return
    
    if "status" in quant_data and quant_data["status"] == "error":
        st.error(f"❌ Quant analysis failed: {quant_data.get('message')}")
    elif quant_data:
        # Summary metrics
        st.markdown(f"### {icon('bar-chart-line')} Summary", unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        ipo_date = quant_data.get("ipo_date", "N/A")
        freq = quant_data.get("data_frequency", "N/A")
        years = quant_data.get("date_range", {}).get("years", 0)
        
        with col1:
            st.metric("IPO Date", ipo_date)
        with col2:
            st.metric("Data Frequency", freq)
        with col3:
            st.metric("History (Years)", f"{years:.1f}")
        with col4:
            total_obs = quant_data.get("total_observations", 0)
            st.metric("Total Observations", f"{total_obs:,}")
        
        st.markdown("---")
        
        # Fama-French Results
        ff_results = quant_data.get("fama_french", {})
        
        if ff_results:
            st.markdown(f"### {icon('bullseye')} Fama-French 3-Factor Regression Results", unsafe_allow_html=True)
            
            # Cost of Equity (main result)
            col1, col2 = st.columns(2)
            
            with col1:
                coe_annual = ff_results.get("cost_of_equity_annual", 0) * 100
                st.metric(
                    "Cost of Equity (Annual)",
                    f"{coe_annual:.2f}%",
                    help="Required return calculated using Fama-French 3-Factor Model"
                )
            
            with col2:
                alpha_annual = ff_results.get("alpha_annualized", 0) * 100
                st.metric(
                    "Alpha (Annualized)",
                    f"{alpha_annual:.2f}%",
                    delta="Excess return vs factors",
                    help="Return not explained by market, size, or value factors"
                )
            
            st.markdown("### Factor Loadings (Betas)")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                beta_mkt = ff_results.get("beta_market", 0)
                p_mkt = ff_results.get("p_values", {}).get("market", 1)
                sig = "***" if p_mkt < 0.01 else "**" if p_mkt < 0.05 else "*" if p_mkt < 0.10 else ""
                st.metric(
                    f"β Market {sig}",
                    f"{beta_mkt:.4f}",
                    help=f"Market risk (p={p_mkt:.4f})"
                )
            
            with col2:
                beta_smb = ff_results.get("beta_smb", 0)
                p_smb = ff_results.get("p_values", {}).get("smb", 1)
                sig = "***" if p_smb < 0.01 else "**" if p_smb < 0.05 else "*" if p_smb < 0.10 else ""
                st.metric(
                    f"β SMB (Size) {sig}",
                    f"{beta_smb:.4f}",
                    help=f"Small vs Big exposure (p={p_smb:.4f})"
                )
            
            with col3:
                beta_hml = ff_results.get("beta_hml", 0)
                p_hml = ff_results.get("p_values", {}).get("hml", 1)
                sig = "***" if p_hml < 0.01 else "**" if p_hml < 0.05 else "*" if p_hml < 0.10 else ""
                st.metric(
                    f"β HML (Value) {sig}",
                    f"{beta_hml:.4f}",
                    help=f"Value vs Growth exposure (p={p_hml:.4f})"
                )
            
            # Model fit
            st.markdown("### Model Quality")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                r2 = ff_results.get("r_squared", 0)
                st.metric("R-Squared", f"{r2:.4f}")
            
            with col2:
                adj_r2 = ff_results.get("adj_r_squared", 0)
                st.metric("Adjusted R²", f"{adj_r2:.4f}")
            
            with col3:
                obs = ff_results.get("observations", 0)
                st.metric("Regression Obs", f"{obs}")
            
            st.markdown("---")
            
            # Risk Premiums
            st.markdown(f"### {icon('graph-up-arrow')} Risk Premiums & Returns", unsafe_allow_html=True)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                rf = ff_results.get("risk_free_rate", 0) * 12 * 100
                st.metric("Risk-Free Rate", f"{rf:.2f}%")
            
            with col2:
                mkt_prem = ff_results.get("market_premium", 0) * 12 * 100
                st.metric("Market Premium", f"{mkt_prem:.2f}%")
            
            with col3:
                smb_prem = ff_results.get("smb_premium", 0) * 12 * 100
                st.metric("SMB Premium", f"{smb_prem:.2f}%")
            
            with col4:
                hml_prem = ff_results.get("hml_premium", 0) * 12 * 100
                st.metric("HML Premium", f"{hml_prem:.2f}%")
            
            # Returns comparison
            st.markdown("### Return Comparison")
            
            returns_data = quant_data.get("returns", {})
            stock_return = returns_data.get("annualized_return", 0) * 100
            required_return = ff_results.get("required_return_annual", 0) * 100
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric(
                    "Stock Annual Return",
                    f"{stock_return:.2f}%",
                    help="Realized historical return"
                )
            
            with col2:
                delta = stock_return - required_return
                st.metric(
                    "Required Return (FF)",
                    f"{required_return:.2f}%",
                    delta=f"{delta:+.2f}% vs realized",
                    help="Return required by Fama-French model"
                )
            
            # Interpretation
            st.markdown("---")
            st.markdown(f"### {icon('file-text')} Interpretation", unsafe_allow_html=True)
            
            if abs(beta_mkt - 1) < 0.2:
                mkt_interp = "**Market Risk:** Moves in line with market (neutral)"
            elif beta_mkt > 1.2:
                mkt_interp = "**Market Risk:** High volatility, amplifies market moves"
            elif beta_mkt < 0.8:
                mkt_interp = "**Market Risk:** Defensive, less volatile than market"
            else:
                mkt_interp = "**Market Risk:** Moderate volatility"
            
            if abs(beta_smb) < 0.3:
                size_interp = "**Size:** Neutral to size factor"
            elif beta_smb > 0:
                size_interp = "**Size:** Behaves like small-cap stock"
            else:
                size_interp = "**Size:** Behaves like large-cap stock"
            
            if abs(beta_hml) < 0.3:
                value_interp = "**Style:** Neutral (blend of growth/value)"
            elif beta_hml > 0:
                value_interp = "**Style:** Value stock characteristics"
            else:
                value_interp = "**Style:** Growth stock characteristics"
            
            # Display interpretations in professional themed boxes
            st.markdown(f"""
            <div style='padding: 0.8rem 1rem; margin: 0.5rem 0;
                        background: rgba(59, 130, 246, 0.08); backdrop-filter: blur(10px);
                        border-left: 3px solid #1e88e5; border-radius: 4px;'>
                <p style='color: #e3f2fd; margin: 0; line-height: 1.6;'>{mkt_interp}</p>
            </div>
            <div style='padding: 0.8rem 1rem; margin: 0.5rem 0;
                        background: rgba(59, 130, 246, 0.08); backdrop-filter: blur(10px);
                        border-left: 3px solid #1e88e5; border-radius: 4px;'>
                <p style='color: #e3f2fd; margin: 0; line-height: 1.6;'>{size_interp}</p>
            </div>
            <div style='padding: 0.8rem 1rem; margin: 0.5rem 0;
                        background: rgba(59, 130, 246, 0.08); backdrop-filter: blur(10px);
                        border-left: 3px solid #1e88e5; border-radius: 4px;'>
                <p style='color: #e3f2fd; margin: 0; line-height: 1.6;'>{value_interp}</p>
            </div>
            """, unsafe_allow_html=True)
            
            if alpha_annual > 2:
                alpha_interp = f"**Alpha:** Positive ({alpha_annual:.2f}% annualized) - Outperforms risk-adjusted expectations"
                alpha_color = "#4caf50"
            elif alpha_annual < -2:
                alpha_interp = f"**Alpha:** Negative ({alpha_annual:.2f}% annualized) - Underperforms risk-adjusted expectations"
                alpha_color = "#f44336"
            else:
                alpha_interp = f"**Alpha:** Neutral ({alpha_annual:.2f}% annualized) - Performs as expected"
                alpha_color = "#ff9800"
            
            st.markdown(f"""
            <div style='padding: 0.8rem 1rem; margin: 0.5rem 0;
                        background: rgba(59, 130, 246, 0.08); backdrop-filter: blur(10px);
                        border-left: 3px solid {alpha_color}; border-radius: 4px;'>
                <p style='color: #e3f2fd; margin: 0; line-height: 1.6;'>{alpha_interp}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Download data
            st.markdown("---")
            st.markdown(f"### {icon('download')} Export Data", unsafe_allow_html=True)
            
            # Prepare export
            export_data = {
                "Metric": [
                    "Cost of Equity (Annual)",
                    "Alpha (Annualized)",
                    "Beta Market",
                    "Beta SMB",
                    "Beta HML",
                    "R-Squared",
                    "Risk-Free Rate",
                    "Market Premium",
                    "Stock Return",
                    "Required Return"
                ],
                "Value": [
                    f"{coe_annual:.2f}%",
                    f"{alpha_annual:.2f}%",
                    f"{beta_mkt:.4f}",
                    f"{beta_smb:.4f}",
                    f"{beta_hml:.4f}",
                    f"{r2:.4f}",
                    f"{rf:.2f}%",
                    f"{mkt_prem:.2f}%",
                    f"{stock_return:.2f}%",
                    f"{required_return:.2f}%"
                ]
            }
            
            export_df = pd.DataFrame(export_data)
            smart_dataframe(export_df, title=None, height=300, key="quant_export_table")
            
            csv = export_df.to_csv(index=False)
            st.download_button(
                "📥 Download Quant Results CSV",
                data=csv,
                file_name=f"{ticker}_quant_analysis.csv",
                mime="text/csv"
            )
    else:
        st.warning("No quant analysis data available")


# ============================================================================
# TESTING CODE
# ============================================================================

if __name__ == "__main__":
    print("="*80)
    print("TESTING QUANT TAB MODULE")
    print("="*80)
    
    # Test import
    print("\n[TEST] Module imports successful")
    
    # Note: Actual rendering requires Streamlit context
    print("[OK] Module ready for integration")
    
    print("\n" + "="*80)




