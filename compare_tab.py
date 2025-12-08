"""
COMPARE TAB - PEER COMPARISON & BENCHMARKING
================================================================================
Extracted from usa_app.py for modularity.

Contains 2 sub-tabs for peer analysis:
1. Auto Peer Discovery - Automatic identification of similar companies
2. Manual Comparison - User-selected company comparisons

Features:
- Automatic peer discovery based on sector/industry/size
- Side-by-side metric comparison
- Percentile rankings
- Comparison heatmaps
- Statistical analysis
- Excel/CSV export
- DCF valuation comparison

Author: Atlas Financial Intelligence
Date: November 2025
Phase: Refactoring - Phase 3
"""

import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict

# Cached extraction to prevent rate limiting
@st.cache_data(ttl=3600, show_spinner=False)
def _cached_extract_for_compare(ticker: str) -> dict:
    """Cached extraction wrapper for compare tab"""
    from usa_backend import USAFinancialExtractor
    extractor = USAFinancialExtractor()
    return extractor.extract_financials(ticker)

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


def render_compare_tab(ticker: str, financials: Dict, extractor, visualizer) -> None:
    """
    Render Peer Comparison & Benchmarking tab with 2 sub-tabs
    
    Args:
        ticker: Stock ticker symbol
        financials: Financial data dictionary
        extractor: USAFinancialExtractor instance
        visualizer: FinancialVisualizer instance
        
    Returns:
        None (renders directly to Streamlit)
    """
    from dcf_modeling import DCFModel
    
    st.markdown(f"## {icon('search', '1.5em')} Peer Comparison & Benchmarking", unsafe_allow_html=True)
    
    st.info("Automatically discover peers, compare metrics side-by-side, and see percentile rankings")
    
    # Create sub-tabs for different comparison modes
    peer_auto_tab, peer_manual_tab = st.tabs(["Auto Peer Discovery", "Manual Comparison"])
    
    # ==========================================
    # AUTO PEER DISCOVERY TAB
    # ==========================================
    with peer_auto_tab:
        if not st.session_state.financials or not st.session_state.ticker:
            st.warning("⚠️ Please extract a company first using the sidebar")
        else:
            current_ticker = st.session_state.ticker
            
            st.markdown(f"### Automatic Peer Discovery for **{current_ticker}**")
            
            # Peer discovery settings
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.caption("Automatically identify similar companies based on sector, industry, and size")
            
            with col2:
                max_peers = st.selectbox("# of Peers", [5, 10, 15, 20], index=1, key="max_peers_select")
            
            if st.button("🔍 Discover Peers", type="primary", use_container_width=True):
                with st.spinner(f"Discovering peers for {current_ticker}..."):
                    from peer_comparison import discover_peers
                    
                    # Clear old results to ensure fresh data
                    if 'peer_comparison_data' in st.session_state:
                        del st.session_state['peer_comparison_data']
                    
                    # Discover peers
                    peer_result = discover_peers(current_ticker, max_peers=max_peers)
                    
                    if peer_result and peer_result.get('status') == 'success':
                        st.session_state['peer_discovery_result'] = peer_result
                        st.success(f"Found {len(peer_result.get('peers', []))} peers!")
                    elif peer_result:
                        st.error(peer_result.get('message', 'Peer discovery failed'))
                    else:
                        st.error("Peer discovery returned no data")
            
            # Display peer discovery results
            if 'peer_discovery_result' in st.session_state:
                peer_result = st.session_state['peer_discovery_result']
                
                # Guard: peer_result must exist and be valid
                if not peer_result:
                    del st.session_state['peer_discovery_result']
                    st.info("No peer data available. Click 'Discover Peers' to find comparable companies.")
                elif peer_result.get('ticker') != current_ticker:
                    # Clear stale data from different ticker
                    del st.session_state['peer_discovery_result']
                    if 'peer_comparison_data' in st.session_state:
                        del st.session_state['peer_comparison_data']
                    st.warning("Previous peer data was for a different company. Click 'Discover Peers' again.")
                else:
                    # Valid peer data - display it
                    st.markdown("---")
                    
                    # Company context
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Sector", peer_result.get('sector', 'N/A'))
                    
                    with col2:
                        st.metric("Industry", peer_result.get('industry', 'N/A'))
                    
                    with col3:
                        from format_helpers import format_large_number
                        market_cap = peer_result.get('market_cap')
                        if market_cap:
                            st.markdown(format_large_number(market_cap, 'currency', 2), unsafe_allow_html=True)
                            st.caption("Market Cap")
                        else:
                            st.metric("Market Cap", "N/A")
                    
                    st.markdown("---")
                    
                    # Display discovered peers
                    peers_list = peer_result.get('peers', [])
                    st.markdown(f"### Discovered Peers ({len(peers_list)} companies)")
                    
                    # Create peer DataFrame for display
                    peer_df = pd.DataFrame(peer_result['peers'])
                    
                    # Safely handle market_cap column (may not exist)
                    if 'market_cap' in peer_df.columns:
                        peer_df['market_cap'] = peer_df['market_cap'].apply(lambda x: f"${x/1e9:.2f}B" if x and x > 0 else "N/A")
                    else:
                        peer_df['market_cap'] = "N/A"
                    
                    # Ensure all required columns exist
                    for col in ['ticker', 'name', 'industry', 'similarity_score']:
                        if col not in peer_df.columns:
                            peer_df[col] = "N/A"
                    
                    peer_df = peer_df[['ticker', 'name', 'industry', 'market_cap', 'similarity_score']]
                    peer_df.columns = ['Ticker', 'Company', 'Industry', 'Market Cap', 'Match Score']
                    
                    smart_dataframe(peer_df, title=None, height=300, key="peer_discovery_table")
                    
                    st.caption(f"Discovery Method: {peer_result['discovery_method']}")
                    
                    st.markdown("---")
                    
                    # Fetch comparison data
                    if st.button("📈 Run Full Comparison Analysis", type="primary", use_container_width=True):
                        with st.spinner("Fetching data for all peers..."):
                            from peer_comparison import get_peer_comparison_data
                            
                            peer_tickers = [p['ticker'] for p in peer_result['peers']]
                            
                            comp_result = get_peer_comparison_data(current_ticker, peer_tickers)
                            
                            if comp_result['status'] == 'success':
                                st.session_state['peer_comparison_data'] = comp_result
                                st.success(f"✅ Loaded {comp_result['metrics_count']} metrics for {len(comp_result['data'])} companies!")
                                st.rerun()
                            else:
                                st.error(comp_result.get('message', 'Data fetch failed'))
            
            # Display comparison analysis
            if 'peer_comparison_data' in st.session_state:
                comp_data = st.session_state['peer_comparison_data']
                
                # Guard: ensure comp_data is valid
                if not comp_data or not isinstance(comp_data, dict) or 'data' not in comp_data:
                    del st.session_state['peer_comparison_data']
                    st.warning("Peer comparison data invalid. Please run comparison again.")
                    st.stop()  # Stop rendering this section
                
                df = comp_data['data']
                
                from peer_comparison import calculate_percentile_ranks, calculate_statistics, generate_heatmap_data, export_comparison_to_excel
                
                st.markdown("---")
                st.markdown("## Peer Comparison Analysis")
                
                # Calculate percentiles and stats
                df_with_percentiles = calculate_percentile_ranks(df, current_ticker)
                stats = calculate_statistics(df)
                
                # Analysis sub-tabs
                analysis_tab1, analysis_tab2, analysis_tab3, analysis_tab4 = st.tabs([
                    "Comparison Table", "Percentile Rankings", "Heatmap", "Statistics"
                ])
                
                # TAB 1: Comparison Table
                with analysis_tab1:
                    st.markdown("### Side-by-Side Comparison")
                    
                    # Select metrics to display
                    available_metrics = [col for col in df.columns if col not in ['Ticker', 'Company', 'Sector', 'Industry', 'Is_Primary']]
                    
                    selected_metrics = st.multiselect(
                        "Select Metrics to Display",
                        available_metrics,
                        default=available_metrics[:8] if len(available_metrics) > 8 else available_metrics,
                        key="comparison_metrics_select"
                    )
                    
                    if selected_metrics:
                        display_df = df[['Ticker', 'Company'] + selected_metrics].copy()
                        
                        # Format numbers
                        from format_helpers import format_dataframe_for_display
                        
                        # Highlight primary company
                        def highlight_primary(row):
                            if row['Ticker'] == current_ticker:
                                return ['background-color: #ffffcc'] * len(row)
                            return [''] * len(row)
                        
                        styled_df = display_df.style.apply(highlight_primary, axis=1)
                        
                        # Note: AgGrid doesn't support styled DataFrames, use native for styling
                        st.dataframe(styled_df, use_container_width=True, height=500)
                        
                        st.caption(f"Note: {current_ticker} is highlighted in yellow")
                    else:
                        st.warning("Please select at least one metric to display")
                
                # TAB 2: Percentile Rankings
                with analysis_tab2:
                    st.markdown(f"### {current_ticker} Percentile Rankings")
                    
                    st.info("Percentile rankings show where the company stands relative to peers (0th = worst, 100th = best)")
                    
                    # Get primary company's percentile data
                    primary_row = df_with_percentiles[df_with_percentiles['Ticker'] == current_ticker]
                    
                    if not primary_row.empty:
                        percentile_cols = [col for col in df_with_percentiles.columns if col.endswith('_Percentile')]
                        
                        # Create percentile summary
                        percentile_data = []
                        
                        for col in percentile_cols:
                            metric_name = col.replace('_Percentile', '')
                            percentile = primary_row[col].values[0]
                            
                            if not np.isnan(percentile):
                                # Get actual value
                                actual_value = primary_row[metric_name].values[0] if metric_name in primary_row.columns else None
                                
                                # Determine rank category
                                if percentile >= 80:
                                    rank_category = "🟢 Top 20%"
                                    color = "green"
                                elif percentile >= 60:
                                    rank_category = "🔵 Above Average"
                                    color = "blue"
                                elif percentile >= 40:
                                    rank_category = "⚪ Average"
                                    color = "gray"
                                elif percentile >= 20:
                                    rank_category = "🟠 Below Average"
                                    color = "orange"
                                else:
                                    rank_category = "🔴 Bottom 20%"
                                    color = "red"
                                
                                percentile_data.append({
                                    'Metric': metric_name,
                                    'Actual Value': f"{actual_value:.2f}" if actual_value else "N/A",
                                    'Percentile': f"{percentile:.1f}",
                                    'Rank': rank_category
                                })
                        
                        if percentile_data:
                            percentile_df = pd.DataFrame(percentile_data)
                            
                            # Sort by percentile (descending)
                            percentile_df['Percentile_Num'] = percentile_df['Percentile'].astype(float)
                            percentile_df = percentile_df.sort_values('Percentile_Num', ascending=False)
                            percentile_df = percentile_df.drop('Percentile_Num', axis=1)
                            
                            smart_dataframe(percentile_df, title=None, height=500, key="percentile_rankings_table")
                            
                            # Summary stats
                            top_20_count = len([p for p in percentile_data if float(p['Percentile']) >= 80])
                            bottom_20_count = len([p for p in percentile_data if float(p['Percentile']) <= 20])
                            
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.metric("Top 20% Rankings", top_20_count)
                            
                            with col2:
                                st.metric("Average Rankings", len(percentile_data) - top_20_count - bottom_20_count)
                            
                            with col3:
                                st.metric("Bottom 20% Rankings", bottom_20_count)
                        else:
                            st.warning("No percentile data available")
                    else:
                        st.error("Primary company not found in comparison data")
                
                # TAB 3: Heatmap
                with analysis_tab3:
                    st.markdown("### Comparison Heatmap")
                    
                    st.info("Color intensity shows relative performance: Darker = Better (green) or Worse (red) depending on metric")
                    
                    heatmap_df, color_map = generate_heatmap_data(df)
                    
                    if not heatmap_df.empty:
                        # Display heatmap using Plotly
                        import plotly.express as px
                        
                        # Prepare data for heatmap
                        heatmap_metrics = [col for col in heatmap_df.columns if col not in ['Ticker', 'Company']]
                        
                        # Create heatmap data
                        heatmap_values = heatmap_df[heatmap_metrics].values
                        
                        fig = px.imshow(
                            heatmap_values,
                            labels=dict(x="Metric", y="Company", color="Value"),
                            x=heatmap_metrics,
                            y=heatmap_df['Company'].values,
                            aspect="auto",
                            color_continuous_scale="RdYlGn"  # Red-Yellow-Green
                        )
                        
                        fig.update_layout(
                            title=f"Peer Comparison Heatmap",
                            xaxis_title="Metric",
                            yaxis_title="Company",
                            height=400 + (len(heatmap_df) * 30)
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.warning("Heatmap data not available")
                
                # TAB 4: Statistics
                with analysis_tab4:
                    st.markdown("### Peer Group Statistics")
                    
                    st.info("Statistical summary shows peer group mean, median, quartiles, and spread")
                    
                    if stats:
                        # Convert stats to DataFrame
                        stats_df = pd.DataFrame(stats).T
                        stats_df = stats_df.round(2)
                        
                        # Display statistics
                        smart_dataframe(stats_df, title=None, height=500, key="peer_statistics_table")
                        
                        # Statistical insights
                        st.markdown("---")
                        st.markdown("#### 📊 Statistical Glossary")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("""
                            - **Mean**: Average value across all peers
                            - **Median**: Middle value (50th percentile)
                            - **Std**: Standard deviation (spread of values)
                            """)
                        
                        with col2:
                            st.markdown("""
                            - **Q25**: 25th percentile (bottom quartile)
                            - **Q75**: 75th percentile (top quartile)
                            - **Count**: Number of companies with data
                            """)
                    else:
                        st.warning("No statistical data available")
                
                # Export functionality
                st.markdown("---")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    # Export to Excel
                    excel_data = export_comparison_to_excel(df_with_percentiles, current_ticker, stats)
                    
                    if excel_data:
                        st.download_button(
                            "📥 Export to Excel",
                            data=excel_data,
                            file_name=f"{current_ticker}_peer_comparison.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )
                
                with col2:
                    # Export to CSV
                    csv_data = df.to_csv(index=False)
                    
                    st.download_button(
                        "📥 Export to CSV",
                        data=csv_data,
                        file_name=f"{current_ticker}_peer_comparison.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                
                with col3:
                    # Clear comparison
                    if st.button("🗑️ Clear Analysis", use_container_width=True):
                        if 'peer_comparison_data' in st.session_state:
                            del st.session_state['peer_comparison_data']
                        if 'peer_discovery_result' in st.session_state:
                            del st.session_state['peer_discovery_result']
                        st.rerun()
    
    # ==========================================
    # MANUAL COMPARISON TAB (EXISTING FUNCTIONALITY)
    # ==========================================
    with peer_manual_tab:
        st.markdown("### Manual Company Comparison")
        
        st.info("Add multiple companies manually to compare specific metrics")
        
        # Auto-add current ticker if available and not already added
        if st.session_state.financials and st.session_state.ticker:
            current_ticker = st.session_state.ticker
            if current_ticker not in st.session_state.comparison_data:
                # Auto-add current ticker silently
                st.session_state.comparison_data[current_ticker] = st.session_state.financials
        
        # Add companies
        col1, col2 = st.columns([3, 1])
        
        with col1:
            compare_ticker = st.text_input(
                "Add Company to Comparison",
                placeholder="Enter ticker (e.g., MSFT, GOOGL)",
                key="manual_compare_ticker"
            ).upper().strip()
        
        with col2:
            st.write("")  # Spacing
            st.write("")  # Spacing
            add_button = st.button("➕ Add", use_container_width=True, key="manual_add_button")
        
        if add_button and compare_ticker:
            if compare_ticker not in st.session_state.comparison_data:
                with st.spinner(f"Adding {compare_ticker}... (cached for 1 hour)"):
                    try:
                        # Use cached extraction to prevent rate limiting
                        data = _cached_extract_for_compare(compare_ticker)
                        if "status" not in data or data["status"] != "error":
                            st.session_state.comparison_data[compare_ticker] = data
                            st.success(f"✅ Added {compare_ticker}")
                            st.rerun()
                        else:
                            st.error(f"❌ {data['message']}")
                    except Exception as e:
                        error_str = str(e).lower()
                        if 'rate limit' in error_str or 'too many requests' in error_str:
                            st.error("⏳ Rate limited - try again in 1-2 minutes")
                        else:
                            st.error(f"❌ Failed: {e}")
            else:
                st.warning(f"{compare_ticker} already in comparison")
        
        # Show current companies
        if st.session_state.comparison_data:
            st.markdown("### Companies in Comparison:")
            
            cols = st.columns(len(st.session_state.comparison_data))
            for i, ticker in enumerate(st.session_state.comparison_data.keys()):
                with cols[i]:
                    st.info(ticker)
                    if st.button("❌ Remove", key=f"remove_{ticker}"):
                        del st.session_state.comparison_data[ticker]
                        st.rerun()
            
            st.markdown("---")
            
            # Comparison metric selection
            metric_options = [
                "Total Revenue",
                "Net Income", 
                "Operating Income",
                "Total Assets",
                "Total Debt",
                "Free Cash Flow",
                "EBITDA"
            ]
            selected_metric = st.selectbox("Select Metric to Compare", metric_options)
            
            # Generate comparison chart
            companies_list = list(st.session_state.comparison_data.values())
            
            fig = visualizer.plot_peer_comparison(companies_list, selected_metric)
            st.plotly_chart(fig, use_container_width=True)
            
            # DCF Comparison (if available)
            if st.button("🚀 Run DCF for All Companies"):
                comparison_results = []
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for i, (ticker, data) in enumerate(st.session_state.comparison_data.items()):
                    status_text.text(f"Running DCF for {ticker}...")
                    
                    try:
                        model = DCFModel(data)
                        dcf_results = model.run_all_scenarios()
                        
                        comparison_results.append({
                            "Ticker": ticker,
                            "Conservative": dcf_results["conservative"]["value_per_share"],
                            "Base": dcf_results["base"]["value_per_share"],
                            "Aggressive": dcf_results["aggressive"]["value_per_share"],
                            "Weighted Avg": dcf_results["weighted_average"]
                        })
                    except Exception as e:
                        st.warning(f"DCF failed for {ticker}: {e}")
                    
                    progress_bar.progress((i + 1) / len(st.session_state.comparison_data))
                
                status_text.text("✅ Complete!")
                
                if comparison_results:
                    comparison_df = pd.DataFrame(comparison_results)
                    
                    st.markdown("### DCF Valuation Comparison")
                    st.dataframe(comparison_df.style.format({
                        "Conservative": "${:.2f}",
                        "Base": "${:.2f}",
                        "Aggressive": "${:.2f}",
                        "Weighted Avg": "${:.2f}"
                    }), use_container_width=True)
                    
                    fig = visualizer.plot_valuation_comparison(comparison_df)
                    st.plotly_chart(fig, use_container_width=True)
        
        else:
            st.info("👆 Add companies above to start comparison")
            st.markdown("""
            **How to use:**
            1. Enter a ticker symbol (e.g., AAPL, MSFT, GOOGL)
            2. Click "➕ Add" button
            3. Repeat for multiple companies
            4. View side-by-side comparison charts
            5. Run DCF for all companies at once
            
            **Tip:** Add companies in the same industry for meaningful comparisons.
            """)


# ============================================================================
# TESTING CODE
# ============================================================================

if __name__ == "__main__":
    print("="*80)
    print("TESTING COMPARE TAB MODULE")
    print("="*80)
    
    # Test import
    print("\n[TEST] Module imports successful")
    
    # Note: Actual rendering requires Streamlit context
    print("[OK] Module ready for integration")
    
    print("\n" + "="*80)




