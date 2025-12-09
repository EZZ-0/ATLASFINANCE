"""
LIVE DCF SCENARIO MODELING MODULE
==================================
Interactive DCF modeling with real-time adjustments and scenario management

Features:
- Live sliders for all DCF inputs
- Quick preview calculations
- Save/Load custom scenarios
- Compare custom vs. presets
- Scenario library management
- PDF export with custom assumptions
"""

import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
from typing import Dict, Optional, List
from dcf_modeling import DCFModel, DCFAssumptions
from dcf_validation import validate_dcf_assumptions, validate_scenario_name, DCFValidationError


class ScenarioManager:
    """Manage custom DCF scenarios with save/load functionality"""
    
    def __init__(self, scenarios_dir: str = "saved_scenarios"):
        self.scenarios_dir = scenarios_dir
        os.makedirs(scenarios_dir, exist_ok=True)
    
    def save_scenario(self, name: str, ticker: str, assumptions: DCFAssumptions, 
                     result: Dict = None) -> bool:
        """
        Save a custom scenario to JSON
        
        Args:
            name: Scenario name
            ticker: Stock ticker
            assumptions: DCFAssumptions object
            result: Optional DCF result dict
        
        Returns:
            True if saved successfully
        """
        try:
            scenario_data = {
                'name': name,
                'ticker': ticker,
                'saved_at': datetime.now().isoformat(),
                'assumptions': {
                    'revenue_growth_rates': assumptions.revenue_growth_rates,
                    'terminal_growth_rate': assumptions.terminal_growth_rate,
                    'discount_rate': assumptions.discount_rate,
                    'tax_rate': assumptions.tax_rate,
                    'capex_pct_revenue': assumptions.capex_pct_revenue,
                    'nwc_pct_revenue': assumptions.nwc_pct_revenue,
                    'depreciation_pct_revenue': assumptions.depreciation_pct_revenue,
                    'projection_years': assumptions.projection_years
                }
            }
            
            if result:
                scenario_data['result'] = {
                    'enterprise_value': result.get('enterprise_value'),
                    'equity_value': result.get('equity_value'),
                    'value_per_share': result.get('value_per_share')
                }
            
            filename = f"{ticker}_{name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = os.path.join(self.scenarios_dir, filename)
            
            with open(filepath, 'w') as f:
                json.dump(scenario_data, f, indent=2)
            
            return True
        except Exception as e:
            st.error(f"Failed to save scenario: {e}")
            return False
    
    def load_scenarios(self, ticker: Optional[str] = None) -> List[Dict]:
        """
        Load saved scenarios
        
        Args:
            ticker: Optional filter by ticker
        
        Returns:
            List of scenario dicts
        """
        scenarios = []
        
        try:
            for filename in os.listdir(self.scenarios_dir):
                if filename.endswith('.json'):
                    if ticker and not filename.startswith(ticker):
                        continue
                    
                    filepath = os.path.join(self.scenarios_dir, filename)
                    with open(filepath, 'r') as f:
                        scenario = json.load(f)
                        scenario['filename'] = filename
                        scenarios.append(scenario)
            
            # Sort by date (newest first)
            scenarios.sort(key=lambda x: x.get('saved_at', ''), reverse=True)
        except Exception as e:
            st.error(f"Failed to load scenarios: {e}")
        
        return scenarios
    
    def delete_scenario(self, filename: str) -> bool:
        """Delete a saved scenario"""
        try:
            filepath = os.path.join(self.scenarios_dir, filename)
            if os.path.exists(filepath):
                os.remove(filepath)
                return True
        except Exception as e:
            st.error(f"Failed to delete scenario: {e}")
        return False


def render_live_dcf_modeling(financials: Dict, model: DCFModel):
    """
    Render interactive live DCF modeling interface
    
    Args:
        financials: Financial data dict
        model: DCFModel instance
    """
    
    st.markdown("""
    <div style='padding: 1rem; background: rgba(59, 130, 246, 0.1); 
                border-left: 4px solid #1e88e5; border-radius: 6px; margin-bottom: 1.5rem;'>
        <h3 style='color: #42a5f5; margin: 0 0 0.5rem 0;'>
            <i class="bi bi-sliders" style="margin-right: 0.5rem;"></i>Live DCF Scenario Builder
        </h3>
        <p style='color: #94a3b8; margin: 0; font-size: 0.9rem;'>
            Adjust assumptions with sliders below to see instant preview. Click "Run Full DCF" for complete valuation.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize scenario manager
    scenario_mgr = ScenarioManager()
    
    # Scenario preset selector
    col_preset, col_save, col_load = st.columns([2, 1, 1])
    
    with col_preset:
        preset = st.selectbox(
            "📋 Start with Preset:",
            ["Base Case", "Conservative", "Aggressive", "Custom"],
            help="Choose a starting point, then adjust sliders below"
        )
    
    with col_save:
        save_scenario_btn = st.button("💾 Save", use_container_width=True, help="Save current scenario")
    
    with col_load:
        load_scenario_btn = st.button("📂 Load", use_container_width=True, help="Load saved scenario")
    
    # Get base assumptions from preset
    if preset == "Conservative":
        base_assumptions = model.scenarios['conservative']
    elif preset == "Aggressive":
        base_assumptions = model.scenarios['aggressive']
    else:
        base_assumptions = model.scenarios['base']
    
    # Handle load scenario
    if load_scenario_btn:
        st.session_state.show_load_dialog = True
    
    if st.session_state.get('show_load_dialog', False):
        with st.expander("📂 Load Saved Scenario", expanded=True):
            saved_scenarios = scenario_mgr.load_scenarios(model.ticker)
            
            if saved_scenarios:
                for scenario in saved_scenarios:
                    col1, col2, col3 = st.columns([3, 1, 1])
                    with col1:
                        st.markdown(f"**{scenario['name']}**")
                        st.caption(f"Saved: {scenario['saved_at'][:19]}")
                    with col2:
                        if st.button("Load", key=f"load_{scenario['filename']}"):
                            # Load assumptions into session state
                            st.session_state.loaded_assumptions = scenario['assumptions']
                            st.success(f"Loaded: {scenario['name']}")
                            st.session_state.show_load_dialog = False
                            # NOTE: Removed st.rerun() - causes redirect
                    with col3:
                        if st.button("🗑️", key=f"delete_{scenario['filename']}"):
                            if scenario_mgr.delete_scenario(scenario['filename']):
                                st.success("Deleted!")
            else:
                st.info("No saved scenarios found for this ticker")
            
            if st.button("Close"):
                st.session_state.show_load_dialog = False
    
    # Load assumptions if available
    if 'loaded_assumptions' in st.session_state:
        loaded = st.session_state.loaded_assumptions
        growth_defaults = [g * 100 for g in loaded['revenue_growth_rates'][:5]]
        discount_default = loaded['discount_rate'] * 100
        terminal_default = loaded['terminal_growth_rate'] * 100
        tax_default = loaded['tax_rate'] * 100
        capex_default = loaded['capex_pct_revenue'] * 100
        nwc_default = loaded['nwc_pct_revenue'] * 100
        depreciation_default = loaded.get('depreciation_pct_revenue', 0.04) * 100
        del st.session_state.loaded_assumptions
    else:
        growth_defaults = [g * 100 for g in base_assumptions.revenue_growth_rates[:5]]
        discount_default = base_assumptions.discount_rate * 100
        terminal_default = base_assumptions.terminal_growth_rate * 100
        tax_default = base_assumptions.tax_rate * 100
        capex_default = base_assumptions.capex_pct_revenue * 100
        nwc_default = base_assumptions.nwc_pct_revenue * 100
        depreciation_default = base_assumptions.depreciation_pct_revenue * 100
    
    st.markdown("---")
    
    # Create 3 columns for slider inputs
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**📈 Growth Assumptions**")
        
        growth_y1 = st.slider(
            "Year 1 Growth", -10.0, 50.0, growth_defaults[0], 0.5, format="%.1f%%"
        )
        growth_y2 = st.slider(
            "Year 2 Growth", -10.0, 50.0, growth_defaults[1], 0.5, format="%.1f%%"
        )
        growth_y3 = st.slider(
            "Year 3 Growth", -10.0, 50.0, growth_defaults[2], 0.5, format="%.1f%%"
        )
        growth_y4 = st.slider(
            "Year 4 Growth", -10.0, 40.0, growth_defaults[3], 0.5, format="%.1f%%"
        )
        growth_y5 = st.slider(
            "Year 5 Growth", -10.0, 30.0, growth_defaults[4], 0.5, format="%.1f%%"
        )
    
    with col2:
        st.markdown("**💰 Valuation Assumptions**")
        
        discount_rate = st.slider(
            "Discount Rate (WACC)",
            5.0, 20.0, discount_default, 0.1, format="%.1f%%",
            help="Weighted Average Cost of Capital"
        )
        
        terminal_growth = st.slider(
            "Terminal Growth",
            0.0, 5.0, terminal_default, 0.1, format="%.1f%%",
            help="Perpetual growth rate (typically 2-3%)"
        )
        
        tax_rate = st.slider(
            "Tax Rate",
            0.0, 40.0, tax_default, 1.0, format="%.0f%%"
        )
    
    with col3:
        st.markdown("**🔧 Operating Assumptions**")
        
        capex_pct = st.slider(
            "CapEx (% Revenue)",
            0.0, 20.0, capex_default, 0.5, format="%.1f%%",
            help="Capital Expenditures as % of Revenue"
        )
        
        nwc_pct = st.slider(
            "NWC Change (% Revenue)",
            -5.0, 10.0, nwc_default, 0.5, format="%.1f%%",
            help="Net Working Capital change as % of Revenue"
        )
        
        depreciation_pct = st.slider(
            "Depreciation (% Revenue)",
            0.0, 15.0, depreciation_default, 0.5, format="%.1f%%",
            help="Depreciation & Amortization as % of Revenue"
        )
        
        projection_years = st.selectbox(
            "Projection Years",
            [5, 7, 10],
            index=0,
            help="Number of years to project"
        )
    
    # Quick preview calculations
    st.markdown("---")
    st.markdown("### 📊 Quick Preview (Instant Estimate)")
    
    preview_col1, preview_col2, preview_col3, preview_col4 = st.columns(4)
    
    # Simple estimates (fast, not full DCF)
    avg_growth = (growth_y1 + growth_y2 + growth_y3 + growth_y4 + growth_y5) / 5
    implied_multiple = (100 / discount_rate) * (1 + avg_growth/100)
    estimated_ev = model.base_revenue * implied_multiple / 10  # Rough estimate
    
    with preview_col1:
        st.metric(
            "Est. Enterprise Value",
            f"${estimated_ev/1e9:.2f}B",
            help="Quick estimate (not full DCF)"
        )
    
    with preview_col2:
        st.metric(
            "Avg Growth (5Y)",
            f"{avg_growth:.1f}%",
            delta=f"{avg_growth - base_assumptions.revenue_growth_rates[0]*100:+.1f}% vs preset"
        )
    
    with preview_col3:
        st.metric(
            "WACC",
            f"{discount_rate:.1f}%",
            delta=f"{discount_rate - base_assumptions.discount_rate*100:+.1f}% vs preset"
        )
    
    with preview_col4:
        wacc_sensitivity = (discount_rate - base_assumptions.discount_rate * 100) * -3
        st.metric(
            "Value Sensitivity",
            f"{wacc_sensitivity:+.1f}%",
            help="Est. value change from WACC adjustment"
        )
    
    # Full DCF Calculation
    st.markdown("---")
    
    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    
    with col_btn2:
        run_dcf_btn = st.button(
            "🚀 Run Full DCF with Custom Inputs",
            type="primary",
            use_container_width=True
        )
    
    if run_dcf_btn:
        with st.spinner("Calculating full DCF valuation..."):
            # Build custom assumptions from sliders
            custom_assumptions = DCFAssumptions(
                revenue_growth_rates=[
                    growth_y1/100, growth_y2/100, growth_y3/100,
                    growth_y4/100, growth_y5/100
                ],
                terminal_growth_rate=terminal_growth/100,
                discount_rate=discount_rate/100,
                tax_rate=tax_rate/100,
                capex_pct_revenue=capex_pct/100,
                nwc_pct_revenue=nwc_pct/100,
                depreciation_pct_revenue=depreciation_pct/100,
                projection_years=projection_years
            )
            
            # Run full DCF
            custom_result = model.calculate_dcf(
                scenario="custom",
                custom_assumptions=custom_assumptions
            )
            
            # Store in session state
            st.session_state.custom_dcf_result = custom_result
            st.session_state.custom_dcf_assumptions = custom_assumptions
            
            # #region agent log
            import json as _json_dcf; open(r'c:\Users\cidma\OneDrive\Desktop\backup\ATLAS v1.5 - public\Saudi_Earnings_Engine\.cursor\debug.log', 'a').write(_json_dcf.dumps({"hypothesisId":"E","location":"live_dcf_modeling.py:DCF_COMPLETE","message":"Custom DCF completed WITHOUT st.rerun()","data":{"has_result":bool(custom_result)},"timestamp":__import__('time').time()*1000,"sessionId":"debug-p0"})+'\n')
            # #endregion
            st.success("✅ Custom DCF Complete!")
            # NOTE: Removed st.rerun() - causes redirect to Dashboard tab
            # Results display naturally without rerun
    
    # Display results if available
    if 'custom_dcf_result' in st.session_state:
        custom_result = st.session_state.custom_dcf_result
        custom_assumptions = st.session_state.custom_dcf_assumptions
        
        st.markdown("---")
        st.markdown("### ✅ Custom Scenario Results")
        
        # Main metrics
        res_col1, res_col2, res_col3, res_col4 = st.columns(4)
        
        with res_col1:
            st.metric("Enterprise Value", f"${custom_result['enterprise_value']/1e9:.2f}B")
        with res_col2:
            st.metric("Equity Value", f"${custom_result['equity_value']/1e9:.2f}B")
        with res_col3:
            st.metric("Value Per Share", f"${custom_result['value_per_share']:.2f}")
        with res_col4:
            current_price = model.current_price or 0
            if current_price > 0:
                upside = ((custom_result['value_per_share'] - current_price) / current_price * 100)
                st.metric("Upside/Downside", f"{upside:+.1f}%", delta=f"vs ${current_price:.2f}")
            else:
                st.metric("Upside/Downside", "N/A")
        
        # Compare to presets
        st.markdown("---")
        st.markdown("### 📊 Compare to Presets")
        
        # Run preset scenarios for comparison
        base_result = model.calculate_dcf("base")
        cons_result = model.calculate_dcf("conservative")
        aggr_result = model.calculate_dcf("aggressive")
        
        comparison_data = {
            'Scenario': ['Conservative', 'Base', 'Aggressive', 'Your Custom'],
            'Value/Share': [
                cons_result['value_per_share'],
                base_result['value_per_share'],
                aggr_result['value_per_share'],
                custom_result['value_per_share']
            ],
            'Enterprise Value': [
                cons_result['enterprise_value']/1e9,
                base_result['enterprise_value']/1e9,
                aggr_result['enterprise_value']/1e9,
                custom_result['enterprise_value']/1e9
            ],
            'Implied Growth': [
                f"{cons_result.get('assumptions', {}).get('revenue_growth_rates', [0])[0]*100:.1f}%",
                f"{base_result.get('assumptions', {}).get('revenue_growth_rates', [0])[0]*100:.1f}%",
                f"{aggr_result.get('assumptions', {}).get('revenue_growth_rates', [0])[0]*100:.1f}%",
                f"{avg_growth:.1f}%"
            ]
        }
        
        comparison_df = pd.DataFrame(comparison_data)
        st.dataframe(comparison_df, use_container_width=True, hide_index=True)
        
        # Action buttons
        st.markdown("---")
        action_col1, action_col2, action_col3 = st.columns(3)
        
        with action_col1:
            if save_scenario_btn or st.button("💾 Save This Scenario", use_container_width=True):
                scenario_name = st.text_input("Scenario Name:", "My Custom Scenario")
                if st.button("Confirm Save"):
                    if scenario_mgr.save_scenario(
                        scenario_name,
                        model.ticker,
                        custom_assumptions,
                        custom_result
                    ):
                        st.success(f"✅ Saved: {scenario_name}")
        
        with action_col2:
            csv = comparison_df.to_csv(index=False)
            st.download_button(
                "📥 Export Comparison (CSV)",
                data=csv,
                file_name=f"{model.ticker}_DCF_Comparison_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with action_col3:
            if st.button("📄 Generate PDF Report", use_container_width=True):
                try:
                    from pdf_export import generate_custom_dcf_pdf
                    
                    # Get company name from financials
                    company_name = financials.get('company_name', model.ticker)
                    
                    # Run preset scenarios for comparison
                    preset_results = {
                        'conservative': model.calculate_dcf('conservative'),
                        'base': model.calculate_dcf('base'),
                        'aggressive': model.calculate_dcf('aggressive')
                    }
                    
                    # Generate PDF
                    pdf_buffer = generate_custom_dcf_pdf(
                        model.ticker,
                        company_name,
                        st.session_state.custom_dcf_assumptions,
                        custom_result,
                        preset_results
                    )
                    
                    # Download button
                    st.download_button(
                        label="💾 Save Custom DCF PDF",
                        data=pdf_buffer,
                        file_name=f"Custom_DCF_{model.ticker}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                    
                    st.success("✅ PDF generated! Click 'Save' button above to download.")
                    
                except ImportError:
                    st.error("⚠️ PDF export requires 'reportlab' library. Install with: pip install reportlab")
                except Exception as e:
                    st.error(f"❌ PDF generation error: {e}")

