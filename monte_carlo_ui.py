"""
Monte Carlo UI Integration for ATLAS Financial Intelligence
=============================================================

Provides Streamlit UI components for Monte Carlo simulation results.
Designed to integrate with the DCF section of usa_app.py.

Author: ATLAS Financial Intelligence
Created: 2025-12-08 (TASK-A006)
"""

import streamlit as st
import numpy as np
from typing import Dict, Optional
import plotly.graph_objects as go
import plotly.express as px

from monte_carlo_engine import MonteCarloEngine, SimulationParams


def render_monte_carlo_button(
    financials: Dict,
    current_price: float,
    key_prefix: str = "mc"
) -> Optional[Dict]:
    """
    Render Monte Carlo simulation button and return results.
    
    Args:
        financials: ATLAS extracted financials
        current_price: Current stock price
        key_prefix: Unique key prefix for Streamlit widgets
        
    Returns:
        Simulation results dict if run, None otherwise
    """
    col1, col2 = st.columns([3, 1])
    
    with col1:
        run_mc = st.button(
            "Run Monte Carlo Simulation",
            type="primary",
            use_container_width=True,
            key=f"{key_prefix}_run_button"
        )
    
    with col2:
        n_sims = st.selectbox(
            "Simulations",
            options=[1000, 5000, 10000, 50000],
            index=2,  # Default 10,000
            key=f"{key_prefix}_n_sims"
        )
    
    if run_mc:
        return run_monte_carlo_simulation(financials, current_price, n_sims, key_prefix)
    
    return None


def run_monte_carlo_simulation(
    financials: Dict,
    current_price: float,
    n_simulations: int = 10000,
    key_prefix: str = "mc"
) -> Dict:
    """
    Run Monte Carlo DCF simulation and store in session state.
    
    Args:
        financials: ATLAS extracted financials
        current_price: Current stock price
        n_simulations: Number of simulations
        key_prefix: Unique key prefix
        
    Returns:
        Simulation results dict
    """
    with st.spinner(f"Running {n_simulations:,} simulations..."):
        try:
            # Extract required inputs from financials
            market_data = financials.get('market_data', {})
            income_stmt = financials.get('income_statement', {})
            cashflow = financials.get('cashflow_statement', {})
            balance = financials.get('balance_sheet', {})
            
            # Get base values
            base_revenue = _extract_value(income_stmt, ['Total Revenue', 'totalRevenue', 'Revenue']) or 1e9
            
            # Calculate FCF margin
            ocf = _extract_value(cashflow, ['Operating Cash Flow', 'operatingCashFlow']) or 0
            capex = abs(_extract_value(cashflow, ['Capital Expenditure', 'capitalExpenditure']) or 0)
            fcf = ocf - capex
            base_fcf_margin = fcf / base_revenue if base_revenue > 0 else 0.15
            
            shares = market_data.get('shares_outstanding') or _extract_value(balance, ['Ordinary Shares Number']) or 1e9
            
            # Net debt
            total_debt = _extract_value(balance, ['Total Debt', 'totalDebt']) or 0
            cash = _extract_value(balance, ['Cash And Cash Equivalents', 'cash']) or 0
            net_debt = total_debt - cash
            
            # Create engine and run simulation
            engine = MonteCarloEngine(SimulationParams(n_simulations=n_simulations))
            
            results = engine.dcf_simulation(
                base_revenue=base_revenue,
                base_fcf_margin=base_fcf_margin,
                shares_outstanding=shares,
                net_debt=net_debt
            )
            
            # Add probability calculation
            results['prob_above_current'] = engine.probability_above_price(results, current_price)
            results['current_price'] = current_price
            results['n_simulations'] = n_simulations
            
            # Store in session state
            st.session_state[f'{key_prefix}_results'] = results
            
            st.success(f"Monte Carlo simulation complete!")
            return results
            
        except Exception as e:
            st.error(f"Simulation failed: {e}")
            return None


def render_monte_carlo_results(
    results: Dict,
    current_price: float,
    key_prefix: str = "mc"
):
    """
    Render Monte Carlo simulation results with visualizations.
    
    Args:
        results: Monte Carlo simulation results
        current_price: Current stock price
        key_prefix: Unique key prefix
    """
    if not results:
        return
    
    st.markdown("### Monte Carlo Valuation Distribution")
    
    # Key metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    percentiles = results.get('percentiles', {})
    
    with col1:
        p10 = percentiles.get(10, 0)
        st.metric(
            "10th Percentile",
            f"${p10:.2f}",
            help="10% of simulations resulted in a value below this"
        )
    
    with col2:
        median = percentiles.get(50, 0)
        delta = ((median / current_price) - 1) * 100 if current_price > 0 else 0
        st.metric(
            "Median (50th)",
            f"${median:.2f}",
            f"{delta:+.1f}% vs current",
            delta_color="normal"
        )
    
    with col3:
        p90 = percentiles.get(90, 0)
        st.metric(
            "90th Percentile",
            f"${p90:.2f}",
            help="90% of simulations resulted in a value below this"
        )
    
    with col4:
        prob = results.get('prob_above_current', 0) * 100
        st.metric(
            "Upside Probability",
            f"{prob:.1f}%",
            help="Probability that fair value exceeds current price"
        )
    
    # Distribution chart
    st.markdown("---")
    
    fig = create_distribution_chart(results, current_price)
    st.plotly_chart(fig, use_container_width=True)
    
    # Detailed statistics expander
    with st.expander("Detailed Statistics"):
        render_detailed_statistics(results, current_price)


def create_distribution_chart(
    results: Dict,
    current_price: float
) -> go.Figure:
    """
    Create histogram of simulation results.
    
    Args:
        results: Monte Carlo results
        current_price: Current stock price
        
    Returns:
        Plotly figure
    """
    values = results.get('intrinsic_values', np.array([100]))
    
    # Create histogram
    fig = go.Figure()
    
    fig.add_trace(go.Histogram(
        x=values,
        nbinsx=50,
        name="Simulation Results",
        marker_color='rgba(59, 130, 246, 0.6)',
        marker_line_color='rgba(59, 130, 246, 1)',
        marker_line_width=1
    ))
    
    # Add current price line
    fig.add_vline(
        x=current_price,
        line_dash="dash",
        line_color="red",
        line_width=2,
        annotation_text=f"Current: ${current_price:.2f}",
        annotation_position="top"
    )
    
    # Add median line
    median = np.median(values)
    fig.add_vline(
        x=median,
        line_dash="solid",
        line_color="green",
        line_width=2,
        annotation_text=f"Median: ${median:.2f}",
        annotation_position="bottom"
    )
    
    fig.update_layout(
        title="Monte Carlo DCF Valuation Distribution",
        xaxis_title="Intrinsic Value per Share ($)",
        yaxis_title="Frequency",
        showlegend=False,
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig


def render_detailed_statistics(
    results: Dict,
    current_price: float
):
    """
    Render detailed statistics table.
    
    Args:
        results: Monte Carlo results
        current_price: Current stock price
    """
    values = results.get('intrinsic_values', np.array([100]))
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Distribution Statistics**")
        stats_data = {
            "Mean": f"${np.mean(values):.2f}",
            "Median": f"${np.median(values):.2f}",
            "Std Dev": f"${np.std(values):.2f}",
            "Min": f"${np.min(values):.2f}",
            "Max": f"${np.max(values):.2f}",
        }
        for label, value in stats_data.items():
            st.text(f"{label}: {value}")
    
    with col2:
        st.markdown("**Percentiles**")
        percentiles = [5, 10, 25, 50, 75, 90, 95]
        for p in percentiles:
            pval = np.percentile(values, p)
            st.text(f"{p}th: ${pval:.2f}")
    
    # Upside/Downside analysis
    st.markdown("---")
    st.markdown("**Risk/Reward Analysis**")
    
    median = np.median(values)
    p10 = np.percentile(values, 10)
    p90 = np.percentile(values, 90)
    
    upside = ((p90 / current_price) - 1) * 100 if current_price > 0 else 0
    downside = ((p10 / current_price) - 1) * 100 if current_price > 0 else 0
    expected = ((median / current_price) - 1) * 100 if current_price > 0 else 0
    
    risk_reward = abs(upside / downside) if downside != 0 else float('inf')
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Upside (90th)", f"{upside:+.1f}%")
    with col2:
        st.metric("Downside (10th)", f"{downside:+.1f}%")
    with col3:
        st.metric("Risk/Reward Ratio", f"{risk_reward:.2f}x")


def render_input_distributions(key_prefix: str = "mc"):
    """
    Render input distribution configuration for Monte Carlo.
    
    Args:
        key_prefix: Unique key prefix
    """
    st.markdown("#### Input Assumptions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Growth Rate**")
        growth_mean = st.slider(
            "Expected Growth",
            min_value=0.0,
            max_value=0.30,
            value=0.08,
            format="%.1f%%",
            key=f"{key_prefix}_growth_mean"
        )
        growth_std = st.slider(
            "Growth Uncertainty (Std Dev)",
            min_value=0.01,
            max_value=0.15,
            value=0.03,
            format="%.1f%%",
            key=f"{key_prefix}_growth_std"
        )
    
    with col2:
        st.markdown("**Discount Rate (WACC)**")
        wacc_mean = st.slider(
            "Expected WACC",
            min_value=0.05,
            max_value=0.20,
            value=0.09,
            format="%.1f%%",
            key=f"{key_prefix}_wacc_mean"
        )
        wacc_std = st.slider(
            "WACC Uncertainty (Std Dev)",
            min_value=0.005,
            max_value=0.05,
            value=0.015,
            format="%.2f%%",
            key=f"{key_prefix}_wacc_std"
        )
    
    return {
        'growth': {'mean': growth_mean, 'std': growth_std},
        'wacc': {'mean': wacc_mean, 'std': wacc_std}
    }


def _extract_value(data: Dict, keys: list) -> Optional[float]:
    """Extract value from dict trying multiple keys."""
    if isinstance(data, dict):
        for key in keys:
            if key in data:
                val = data[key]
                if isinstance(val, (int, float)) and not np.isnan(val):
                    return float(val)
    return None


# ==========================================
# INTEGRATION FUNCTION FOR usa_app.py
# ==========================================

def integrate_monte_carlo_section(
    financials: Dict,
    current_price: float,
    key_prefix: str = "dcf_mc"
):
    """
    Full Monte Carlo section to add to DCF tab.
    
    Usage in usa_app.py:
        from monte_carlo_ui import integrate_monte_carlo_section
        
        # Inside DCF section:
        integrate_monte_carlo_section(
            st.session_state.financials,
            current_price,
            key_prefix="valuation_mc"
        )
    
    Args:
        financials: ATLAS extracted financials
        current_price: Current stock price
        key_prefix: Unique key prefix
    """
    st.markdown("---")
    st.markdown("### Monte Carlo Simulation")
    st.info(
        "Monte Carlo simulation runs thousands of DCF valuations with randomized inputs "
        "to estimate the probability distribution of fair value."
    )
    
    # Show input configuration in expander
    with st.expander("Configure Assumptions", expanded=False):
        assumptions = render_input_distributions(key_prefix)
    
    # Run simulation
    results_key = f'{key_prefix}_results'
    
    # Button and run
    mc_results = render_monte_carlo_button(financials, current_price, key_prefix)
    
    # Check session state for results
    if mc_results is None and results_key in st.session_state:
        mc_results = st.session_state[results_key]
    
    # Render results if available
    if mc_results:
        render_monte_carlo_results(mc_results, current_price, key_prefix)


# ==========================================
# STANDALONE TEST
# ==========================================

if __name__ == "__main__":
    # For testing, run: streamlit run monte_carlo_ui.py
    st.set_page_config(page_title="Monte Carlo Test", layout="wide")
    
    st.title("Monte Carlo Simulation Test")
    
    # Mock data
    mock_financials = {
        'market_data': {
            'shares_outstanding': 15e9,
            'current_price': 175.0
        },
        'income_statement': {
            'Total Revenue': 400e9
        },
        'cashflow_statement': {
            'Operating Cash Flow': 110e9,
            'Capital Expenditure': -11e9
        },
        'balance_sheet': {
            'Total Debt': 100e9,
            'Cash And Cash Equivalents': 60e9
        }
    }
    
    integrate_monte_carlo_section(
        mock_financials,
        current_price=175.0,
        key_prefix="test_mc"
    )

