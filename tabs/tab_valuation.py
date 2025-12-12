"""
ATLAS Financial Intelligence - Valuation Tab
=============================================
DCF Modeling + Alpha Signals (Insider, Ownership, Earnings)
Extracted from usa_app.py lines 2231-2614 + dead code 668-954
"""

import streamlit as st
import pandas as pd

# Import format helpers
from format_helpers import format_financial_number

# Import UI components
from ui_components import smart_dataframe

# Import DCF and visualization
from dcf_modeling import DCFModel

# Import flip cards if available
try:
    from flip_cards import render_flip_card
    FLIP_CARDS_ENABLED = True
except ImportError:
    FLIP_CARDS_ENABLED = False


def icon(name, size="1em", color=None):
    """Render a Bootstrap Icon"""
    style = f"font-size: {size};"
    if color:
        style += f" color: {color};"
    return f'<i class="bi bi-{name}" style="{style}"></i>'


@st.fragment
def render_valuation_tab(ticker: str, financials: dict, visualizer):
    """
    Render the Valuation tab with sub-tabs for DCF and Alpha Signals.
    
    Uses @st.fragment to prevent full page rerun when DCF button is clicked,
    keeping user on the Valuation tab instead of redirecting to Dashboard.
    
    Args:
        ticker: Stock ticker symbol
        financials: Dictionary of financial data
        visualizer: FinancialVisualizer instance
    """
    st.markdown(f"## {icon('cash-coin', '1.5em')} Valuation & Alpha Signals", unsafe_allow_html=True)
    
    # Main sub-tabs for this section
    dcf_tab, insider_tab, ownership_tab, earnings_tab = st.tabs([
        "DCF Model",
        "Insider Activity",
        "Inst. Ownership",
        "Earnings Revisions"
    ])
    
    # ==========================================
    # SUB-TAB 1: DCF MODEL
    # ==========================================
    with dcf_tab:
        _render_dcf_section(ticker, financials, visualizer)
    
    # ==========================================
    # SUB-TAB 2: INSIDER ACTIVITY (from dead code)
    # ==========================================
    with insider_tab:
        _render_insider_section(ticker)
    
    # ==========================================
    # SUB-TAB 3: INSTITUTIONAL OWNERSHIP (from dead code)
    # ==========================================
    with ownership_tab:
        _render_ownership_section(ticker)
    
    # ==========================================
    # SUB-TAB 4: EARNINGS REVISIONS (from dead code)
    # ==========================================
    with earnings_tab:
        _render_earnings_section(ticker)


def _render_dcf_section(ticker: str, financials: dict, visualizer):
    """Render the DCF Model sub-section"""
    # Create DCF mode sub-tabs
    quick_tab, live_tab = st.tabs([
        "Quick 3-Scenario DCF",
        "Live Scenario Builder"
    ])
    
    with quick_tab:
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            if st.button("RUN 3-SCENARIO DCF ANALYSIS", type="primary", use_container_width=True, key="dcf_button_quick"):
                with st.spinner("Building DCF model..."):
                    try:
                        model = DCFModel(financials)
                        results = model.run_all_scenarios()
                        st.session_state.dcf_results = results
                        st.success("DCF Analysis Complete!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"DCF failed: {e}")
        
        with col2:
            st.number_input("Projection Years", min_value=3, max_value=10, value=5, key="proj_years_quick")
        
        with col3:
            show_sensitivity = st.checkbox("Show Sensitivity", value=False, key="show_sens_quick")
        
        st.markdown("---")
        
        # Display results if available
        if st.session_state.get('dcf_results'):
            results = st.session_state.dcf_results
            
            st.markdown(f"### {icon('bar-chart-line')} Valuation Summary", unsafe_allow_html=True)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                conservative = results["conservative"]["value_per_share"]
                st.metric("Conservative", f"${conservative:.2f}", help="Bear case scenario")
            
            with col2:
                base = results["base"]["value_per_share"]
                st.metric("Base Case", f"${base:.2f}", help="Most likely scenario")
            
            with col3:
                aggressive = results["aggressive"]["value_per_share"]
                st.metric("Aggressive", f"${aggressive:.2f}", help="Bull case scenario")
            
            with col4:
                weighted = results["weighted_average"]
                st.metric("Weighted Avg", f"${weighted:.2f}", help="40% Base + 30% Conservative + 30% Aggressive")
            
            # Scenario comparison chart
            st.plotly_chart(
                visualizer.plot_dcf_comparison(results),
                use_container_width=True
            )
            
            # Detailed breakdown tabs
            scenario_tab1, scenario_tab2, scenario_tab3 = st.tabs([
                "Conservative Details",
                "Base Case Details",
                "Aggressive Details"
            ])
            
            for tab, scenario_name in zip(
                [scenario_tab1, scenario_tab2, scenario_tab3],
                ["conservative", "base", "aggressive"]
            ):
                with tab:
                    scenario_result = results[scenario_name]
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Enterprise Value", format_financial_number(scenario_result['enterprise_value']))
                        st.metric("Equity Value", format_financial_number(scenario_result['equity_value']))
                    
                    with col2:
                        st.metric("PV of Cash Flows", format_financial_number(scenario_result['pv_cash_flows']))
                        st.metric("PV of Terminal Value", format_financial_number(scenario_result['pv_terminal_value']))
                    
                    with col3:
                        assumptions = scenario_result['assumptions']
                        st.metric("Discount Rate (WACC)", f"{assumptions.discount_rate*100:.1f}%")
                        st.metric("Terminal Growth", f"{assumptions.terminal_growth_rate*100:.1f}%")
                    
                    # Charts
                    chart_col1, chart_col2 = st.columns(2)
                    
                    with chart_col1:
                        st.plotly_chart(
                            visualizer.plot_dcf_breakdown(scenario_result, scenario_name),
                            use_container_width=True
                        )
                    
                    with chart_col2:
                        st.plotly_chart(
                            visualizer.plot_dcf_projections(scenario_result, scenario_name),
                            use_container_width=True
                        )
                    
                    # Projections table
                    st.subheader("Cash Flow Projections")
                    projections = scenario_result['projections'].copy()
                    
                    numeric_cols = ["Revenue", "EBIT", "Tax", "NOPAT", "Depreciation", "Capex", "NWC_Change", "Free_Cash_Flow"]
                    for col in numeric_cols:
                        if col in projections.columns:
                            projections[col] = projections[col].apply(format_financial_number)
                    
                    smart_dataframe(projections, title=None, height=300, key=f"dcf_projections_{scenario_name}")
            
            # Sensitivity Analysis
            if show_sensitivity:
                st.markdown("---")
                st.markdown(f"### {icon('clipboard-data')} Sensitivity Analysis", unsafe_allow_html=True)
                
                with st.spinner("Running sensitivity analysis..."):
                    model = DCFModel(financials)
                    sensitivity_df = model.sensitivity_analysis(scenario="base")
                    
                    st.plotly_chart(
                        visualizer.plot_sensitivity_heatmap(sensitivity_df, ticker),
                        use_container_width=True
                    )
            
            # Reverse-DCF Section
            _render_reverse_dcf(ticker, financials)
            
            # Analyst Ratings Section
            _render_analyst_ratings(ticker)
        
        else:
            st.info("Click 'RUN 3-SCENARIO DCF ANALYSIS' to generate valuation")
    
    with live_tab:
        try:
            from live_dcf_modeling import render_live_dcf_modeling
            model = DCFModel(financials)
            render_live_dcf_modeling(financials, model)
        except Exception as e:
            st.error(f"Live modeling error: {e}")
            st.info("Make sure live_dcf_modeling.py is available")


def _render_reverse_dcf(ticker: str, financials: dict):
    """Render Reverse-DCF section"""
    st.markdown("---")
    st.markdown(f"### {icon('arrow-repeat')} Reverse-DCF: What the Market is Pricing In", unsafe_allow_html=True)
    st.info("This analysis reverse-engineers the DCF model to determine what growth rate the current market price implies.")
    
    try:
        from reverse_dcf import analyze_reverse_dcf
        
        market_data = financials.get('market_data', {})
        current_price = market_data.get('current_price')
        
        if current_price:
            with st.spinner("Running Reverse-DCF analysis..."):
                reverse_results = analyze_reverse_dcf(financials)
                
                method1 = reverse_results.get('method_1_growth_only', {})
                
                if method1.get('status') == 'success':
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric(
                            "Implied Growth Rate",
                            f"{method1['implied_growth_rate']*100:.2f}%",
                            help="Growth rate the market is currently pricing in"
                        )
                    
                    with col2:
                        st.metric(
                            "Calculation Error",
                            f"{method1['error_pct']*100:.4f}%",
                            help="How close the reverse calculation matches actual price"
                        )
                    
                    with col3:
                        historical_growth = financials.get('historical_growth_rate', 0.05)
                        growth_diff = (method1['implied_growth_rate'] - historical_growth) * 100
                        st.metric(
                            "vs Historical Growth",
                            f"{growth_diff:+.1f}%",
                            help="Difference from historical growth rate"
                        )
                    
                    implied_growth = method1['implied_growth_rate'] * 100
                    if implied_growth > 15:
                        interpretation = f"**High Growth Expected:** Market is pricing in {implied_growth:.1f}% annual growth."
                    elif implied_growth > 8:
                        interpretation = f"**Moderate Growth Expected:** Market expects {implied_growth:.1f}% annual growth."
                    elif implied_growth > 3:
                        interpretation = f"**Steady Growth Expected:** Market pricing in {implied_growth:.1f}% growth."
                    else:
                        interpretation = f"**Low Growth Expected:** Market expects only {implied_growth:.1f}% growth."
                    
                    st.markdown(interpretation)
                else:
                    st.warning(f"Reverse-DCF analysis unavailable: {method1.get('message', 'Insufficient data')}")
        else:
            st.warning("Current market price not available for Reverse-DCF analysis")
            
    except Exception as e:
        st.error(f"Error running Reverse-DCF: {str(e)}")


def _render_analyst_ratings(ticker: str):
    """Render Analyst Ratings section"""
    st.markdown("---")
    st.markdown(f"### {icon('person-badge')} Wall Street Analyst Ratings", unsafe_allow_html=True)
    
    try:
        from analyst_ratings import get_analyst_ratings
        
        with st.spinner("Fetching analyst ratings..."):
            ratings_data = get_analyst_ratings(ticker)
            
            if ratings_data['status'] == 'success':
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Consensus Rating", ratings_data['consensus_rating'])
                
                with col2:
                    if ratings_data['total_analysts']:
                        st.metric("Number of Analysts", ratings_data['total_analysts'])
                
                with col3:
                    if ratings_data['price_target']['mean']:
                        st.metric("Price Target", f"${ratings_data['price_target']['mean']:.2f}")
                
                with col4:
                    if ratings_data['price_target']['upside_pct'] is not None:
                        upside = ratings_data['price_target']['upside_pct']
                        st.metric("Implied Upside", f"{upside:+.1f}%")
                
                # Rating distribution
                st.markdown(f"### {icon('bar-chart-line', '1.2em')} Rating Distribution", unsafe_allow_html=True)
                
                dist = ratings_data['rating_distribution']
                col1, col2, col3, col4, col5 = st.columns(5)
                
                with col1:
                    st.metric("Strong Buy", dist['strongBuy'])
                with col2:
                    st.metric("Buy", dist['buy'])
                with col3:
                    st.metric("Hold", dist['hold'])
                with col4:
                    st.metric("Sell", dist['sell'])
                with col5:
                    st.metric("Strong Sell", dist['strongSell'])
            else:
                st.warning(f"Analyst ratings unavailable: {ratings_data.get('message', 'Unknown error')}")
                
    except Exception as e:
        st.error(f"Error fetching analyst ratings: {str(e)}")


def _render_insider_section(ticker: str):
    """Render Insider Transactions section (from dead code lines 668-749)"""
    st.markdown(f"### {icon('person-check', '1.2em')} Insider Transactions", unsafe_allow_html=True)
    st.info("Track insider buying and selling activity - a key signal for stock analysis.")
    
    try:
        from insider_transactions import get_insider_summary, create_insider_gauge, create_insider_activity_chart, create_transaction_table
        
        with st.spinner("Analyzing insider activity..."):
            insider_data = get_insider_summary(ticker, days=90)
            
            if insider_data:
                # Summary metrics row
                st.caption("Click any metric for insight")
                icol1, icol2, icol3, icol4 = st.columns(4)
                
                if FLIP_CARDS_ENABLED:
                    with icol1:
                        render_flip_card("Insider_Sentiment", insider_data.sentiment_score, "Sentiment Score")
                    with icol2:
                        net_val = insider_data.net_value / 1_000_000 if abs(insider_data.net_value) >= 1_000_000 else insider_data.net_value
                        render_flip_card("market_cap", net_val, "Net Value ($M)" if abs(insider_data.net_value) >= 1_000_000 else "Net Value")
                    with icol3:
                        render_flip_card("Insider_Sentiment", 50 if insider_data.sentiment_label == "Bullish" else -50 if insider_data.sentiment_label == "Bearish" else 0, insider_data.sentiment_label)
                    with icol4:
                        cluster_val = insider_data.cluster_buyers_count if insider_data.is_cluster_buying else 0
                        render_flip_card("Insider_Sentiment", cluster_val * 20, "Cluster Buying" if insider_data.is_cluster_buying else "No Cluster")
                else:
                    with icol1:
                        st.metric("Insider Sentiment", f"{insider_data.sentiment_score:+.0f}")
                    with icol2:
                        net_str = f"${insider_data.net_value/1_000_000:.1f}M" if abs(insider_data.net_value) >= 1_000_000 else f"${insider_data.net_value:,.0f}"
                        st.metric("Net Value", net_str)
                    with icol3:
                        st.metric("Sentiment", insider_data.sentiment_label)
                    with icol4:
                        if insider_data.is_cluster_buying:
                            st.metric("Cluster Buying", f"{insider_data.cluster_buyers_count} insiders")
                        else:
                            st.metric("Cluster Status", "Not Detected")
                
                st.markdown("---")
                
                # Activity breakdown
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Buy Activity:**")
                    st.write(f"Transactions: {insider_data.buy_transactions}")
                    st.write(f"Total Value: ${insider_data.total_buy_value:,.0f}")
                    st.write(f"Shares Bought: {insider_data.total_shares_bought:,}")
                    if insider_data.notable_buyers:
                        st.success(f"Notable: {', '.join(insider_data.notable_buyers[:3])}")
                
                with col2:
                    st.markdown("**Sell Activity:**")
                    st.write(f"Transactions: {insider_data.sell_transactions}")
                    st.write(f"Total Value: ${insider_data.total_sell_value:,.0f}")
                    st.write(f"Shares Sold: {insider_data.total_shares_sold:,}")
                    if insider_data.notable_sellers:
                        st.warning(f"Notable: {', '.join(insider_data.notable_sellers[:3])}")
                
                # Charts in expander
                with st.expander("View Insider Charts", expanded=False):
                    chart_col1, chart_col2 = st.columns(2)
                    
                    with chart_col1:
                        st.plotly_chart(create_insider_gauge(insider_data.sentiment_score), use_container_width=True)
                    
                    with chart_col2:
                        st.plotly_chart(create_insider_activity_chart(insider_data), use_container_width=True)
                
                # Transaction table
                if insider_data.recent_transactions:
                    with st.expander("Recent Transactions", expanded=False):
                        df = create_transaction_table(insider_data.recent_transactions)
                        st.dataframe(df, hide_index=True, use_container_width=True)
            else:
                st.info("No insider transaction data available for this ticker.")
    except ImportError:
        st.warning("Insider tracking module not available. Check insider_transactions.py exists.")
    except Exception as e:
        st.error(f"Error loading insider data: {str(e)}")


def _render_ownership_section(ticker: str):
    """Render Institutional Ownership section (from dead code lines 751-830)"""
    st.markdown(f"### {icon('building', '1.2em')} Institutional Ownership", unsafe_allow_html=True)
    st.info("Track institutional and insider ownership - smart money signals.")
    
    try:
        from institutional_ownership import get_ownership_summary, create_ownership_pie, create_accumulation_gauge
        
        with st.spinner("Analyzing institutional ownership..."):
            ownership_data = get_ownership_summary(ticker)
            
            if ownership_data:
                # Summary metrics row
                ocol1, ocol2, ocol3, ocol4 = st.columns(4)
                
                if FLIP_CARDS_ENABLED:
                    with ocol1:
                        render_flip_card("ROE", ownership_data.institutional_pct, "Institutional %")
                    with ocol2:
                        render_flip_card("ROE", ownership_data.insider_pct, "Insider %")
                    with ocol3:
                        render_flip_card("ROE", ownership_data.top10_concentration, "Top 10 Conc.")
                    with ocol4:
                        render_flip_card("Institutional_Flow", ownership_data.accumulation_score, ownership_data.sentiment_label)
                else:
                    with ocol1:
                        st.metric("Institutional", f"{ownership_data.institutional_pct:.1f}%")
                    with ocol2:
                        st.metric("Insider", f"{ownership_data.insider_pct:.1f}%")
                    with ocol3:
                        st.metric("Top 10 Concentration", f"{ownership_data.top10_concentration:.1f}%")
                    with ocol4:
                        st.metric("Signal", ownership_data.sentiment_label)
                
                st.markdown("---")
                
                # Ownership breakdown
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Ownership Breakdown:**")
                    st.write(f"Institutional: {ownership_data.institutional_pct:.1f}%")
                    st.write(f"Insider: {ownership_data.insider_pct:.1f}%")
                    st.write(f"Retail/Other: {ownership_data.retail_pct:.1f}%")
                    st.write(f"Total Institutions: {ownership_data.total_institutions}")
                
                with col2:
                    st.markdown("**Concentration Analysis:**")
                    st.write(f"Top 10 Hold: {ownership_data.top10_concentration:.1f}%")
                    concentrated = "Yes - Concentrated" if ownership_data.is_concentrated else "No - Distributed"
                    st.write(f"Highly Concentrated: {concentrated}")
                    st.write(f"Accumulation Score: {ownership_data.accumulation_score:+.0f}")
                
                # Charts in expander
                with st.expander("View Ownership Charts", expanded=False):
                    chart_col1, chart_col2 = st.columns(2)
                    
                    with chart_col1:
                        st.plotly_chart(create_ownership_pie(ownership_data), use_container_width=True)
                    
                    with chart_col2:
                        st.plotly_chart(create_accumulation_gauge(ownership_data.accumulation_score), use_container_width=True)
                
                # Top holders table
                if ownership_data.top_holders:
                    with st.expander("Top Institutional Holders", expanded=False):
                        holders_data = [{
                            'Holder': h.name[:40] + '...' if len(h.name) > 40 else h.name,
                            'Shares': f"{h.shares:,}",
                            'Value': f"${h.value/1_000_000:.1f}M" if h.value >= 1_000_000 else f"${h.value:,.0f}",
                            '% Owned': f"{h.percent_held:.2f}%",
                            'Type': h.holder_type.value
                        } for h in ownership_data.top_holders[:10]]
                        st.dataframe(pd.DataFrame(holders_data), hide_index=True, use_container_width=True)
            else:
                st.info("No institutional ownership data available for this ticker.")
    except ImportError:
        st.warning("Ownership tracking module not available. Check institutional_ownership.py exists.")
    except Exception as e:
        st.error(f"Error loading ownership data: {str(e)}")


def _render_earnings_section(ticker: str):
    """Render Earnings Revisions section (from dead code lines 832-954)"""
    st.markdown(f"### {icon('graph-up-arrow', '1.2em')} Earnings Quality & Revisions", unsafe_allow_html=True)
    
    try:
        from earnings_analysis import analyze_earnings_history
        
        with st.spinner("Analyzing earnings history..."):
            earnings_data = analyze_earnings_history(ticker, periods=8)
            
            if earnings_data['status'] == 'success':
                metrics = earnings_data['metrics']
                
                # Summary metrics
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Beat Rate", f"{metrics.get('beat_rate', 0):.1f}%", help="Percentage of earnings beats")
                
                with col2:
                    st.metric("Avg Surprise", f"{metrics.get('avg_surprise_pct', 0):.2f}%", help="Average earnings surprise magnitude")
                
                with col3:
                    st.metric("EPS Momentum", f"{metrics.get('eps_momentum', 0):.1f}%", help="EPS acceleration/deceleration")
                
                with col4:
                    score = metrics.get('earnings_score', 0)
                    rating = metrics.get('earnings_rating', 'N/A')
                    st.metric("Quality Score", f"{score:.0f}/100", help=f"Rating: {rating}")
                
                st.markdown("---")
                
                # Detailed breakdown
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Performance:**")
                    st.write(f"Total Reports: {metrics.get('total_earnings_reports', 0)}")
                    st.write(f"Beats: {metrics.get('earnings_beats', 0)}")
                    st.write(f"Misses: {metrics.get('earnings_misses', 0)}")
                    st.write(f"Consistency: {metrics.get('surprise_consistency', 'N/A')}")
                
                with col2:
                    st.markdown("**EPS & Trends:**")
                    trailing_eps = metrics.get('trailing_eps', 0)
                    forward_eps = metrics.get('forward_eps', 0)
                    st.write(f"Current EPS (TTM): ${trailing_eps:.2f}" if trailing_eps else "Current EPS: N/A")
                    st.write(f"Forward EPS: ${forward_eps:.2f}" if forward_eps else "Forward EPS: N/A")
                    st.write(f"EPS Growth Forecast: {metrics.get('eps_growth_forecast', 0):.1f}%")
                    st.write(f"EPS Trend: {metrics.get('eps_trend', 'N/A')}")
                
                # EARNINGS REVISIONS SECTION
                st.markdown("---")
                st.markdown(f"### {icon('arrow-repeat', '1.1em')} Analyst Estimate Revisions", unsafe_allow_html=True)
                st.caption("Tracks changes in analyst EPS estimates - a key predictor of stock performance")
                
                try:
                    from earnings_revisions import get_earnings_revisions, create_revision_gauge, create_revision_trend_chart
                    
                    revision_data = get_earnings_revisions(ticker)
                    
                    if revision_data:
                        rev_dict = revision_data.to_dict()
                        
                        rcol1, rcol2, rcol3, rcol4 = st.columns(4)
                        
                        with rcol1:
                            score = rev_dict['momentum_score']
                            st.metric("Revision Momentum", f"{score:+.0f}", help="Score from -100 to +100")
                        
                        with rcol2:
                            st.metric("Trend", rev_dict['trend'], help="Overall direction of estimate changes")
                        
                        with rcol3:
                            st.metric("Analyst Agreement", rev_dict['analyst_agreement'], help="How closely analysts agree")
                        
                        with rcol4:
                            if rev_dict['current_year']['growth']:
                                growth = rev_dict['current_year']['growth'] * 100
                                st.metric("EPS Growth Est", f"{growth:+.1f}%")
                            else:
                                st.metric("EPS Growth Est", "N/A")
                        
                        # Revision gauge chart
                        with st.expander("View Revision Charts", expanded=False):
                            chart_col1, chart_col2 = st.columns(2)
                            
                            with chart_col1:
                                st.plotly_chart(create_revision_gauge(score), use_container_width=True)
                            
                            with chart_col2:
                                st.plotly_chart(
                                    create_revision_trend_chart(rev_dict['revisions']),
                                    use_container_width=True
                                )
                    else:
                        st.info("Revision data not available for this ticker")
                except ImportError:
                    st.caption("Revision tracking module loading...")
                except Exception as rev_e:
                    st.caption(f"Revisions: {str(rev_e)}")
                
            else:
                st.warning(earnings_data.get('message', 'No earnings data available'))
    except Exception as e:
        st.error(f"Error analyzing earnings: {str(e)}")

