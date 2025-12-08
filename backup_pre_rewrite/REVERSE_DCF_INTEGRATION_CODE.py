"""
ADD THIS TO usa_app.py AFTER LINE 860 (inside the Model tab, after DCF scenarios)
================================================================================
"""

# Add at the top of usa_app.py with other imports:
# from reverse_dcf import analyze_reverse_dcf

# Add this section after the DCF scenarios (around line 860):

"""
            st.markdown("---")
            st.markdown("---")
            
            # REVERSE-DCF SECTION
            st.subheader("🔄 Reverse-DCF: What is the Market Pricing In?")
            
            with st.expander("ℹ️ What is Reverse-DCF?", expanded=False):
                st.markdown('''
                **Reverse-DCF** (also called "Expectations Investing") answers a different question:
                
                Instead of asking "*What should this stock be worth?*"  
                We ask: "*What assumptions must be TRUE for the current price to be justified?*"
                
                **How it works:**
                1. Takes the current stock price as a given
                2. Solves backwards to find the implied growth rate
                3. Shows you what the MARKET is expecting
                
                **Why it's powerful:**
                - Removes your bias (price is fact, not opinion)
                - Forces you to evaluate if market expectations are realistic
                - Reveals consensus assumptions you can agree or disagree with
                
                **Example:**  
                Stock trading at $180. Reverse-DCF reveals: "Market expects 14% growth for 10 years."  
                You decide: "*Industry growing at 5%... this seems too optimistic!*" → Overvalued signal.
                ''')
            
            if st.button("🔄 Run Reverse-DCF Analysis", type="secondary", use_container_width=True):
                with st.spinner("Solving for market-implied assumptions..."):
                    try:
                        from reverse_dcf import analyze_reverse_dcf
                        rdcf_results = analyze_reverse_dcf(st.session_state.financials)
                        st.session_state.rdcf_results = rdcf_results
                        st.success("✅ Reverse-DCF Complete!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Reverse-DCF failed: {e}")
            
            if 'rdcf_results' in st.session_state and st.session_state.rdcf_results:
                rdcf = st.session_state.rdcf_results
                
                # Method 1: Growth Rate Only
                if rdcf['method_1_growth_only']['status'] == 'success':
                    method1 = rdcf['method_1_growth_only']
                    
                    st.markdown("### 📈 Method 1: Solve for Growth Rate")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric(
                            "Current Stock Price",
                            f"${method1['current_price']:.2f}",
                            help="Current trading price"
                        )
                    
                    with col2:
                        st.metric(
                            "Implied Growth Rate",
                            f"{method1['implied_growth_rate']*100:.2f}%",
                            help="Annual revenue growth rate market is pricing in for next 10 years"
                        )
                    
                    with col3:
                        st.metric(
                            "Calculation Error",
                            f"{method1['error_pct']*100:.4f}%",
                            help="How close our reverse calculation matches the actual price"
                        )
                    
                    # Interpretation
                    st.info(f"**Market Expectations:** {method1['analysis']}")
                    
                    # Recommendation box
                    st.markdown("---")
                    st.markdown("#### 🤔 Your Decision:")
                    st.markdown(method1['recommendation'])
                    
                    # Assumptions used
                    st.markdown("---")
                    with st.expander("📊 Assumptions Used", expanded=False):
                        assump = method1['assumptions']
                        st.write(f"- **WACC (Discount Rate):** {assump['wacc']*100:.1f}%")
                        st.write(f"- **Terminal Growth Rate:** {assump['terminal_growth']*100:.1f}%")
                        st.write(f"- **Projection Period:** {assump['projection_years']} years")
                        st.write(f"- **Operating Margin:** {assump['operating_margin']*100:.2f}%")
                
                # Method 2: Growth + Margin
                if rdcf['method_2_growth_and_margin']['status'] == 'success':
                    method2 = rdcf['method_2_growth_and_margin']
                    
                    st.markdown("---")
                    st.markdown("### 📊 Method 2: Solve for Growth + Margin")
                    st.caption("This method allows BOTH growth and margin to adjust")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric(
                            "Implied Growth",
                            f"{method2['implied_growth_rate']*100:.2f}%",
                            help="Annual revenue growth"
                        )
                    
                    with col2:
                        st.metric(
                            "Implied Operating Margin",
                            f"{method2['implied_operating_margin']*100:.2f}%",
                            delta=f"{method2['margin_change_required']*100:+.2f} pts",
                            help="Operating margin market is pricing in"
                        )
                    
                    with col3:
                        st.metric(
                            "Current Margin",
                            f"{method2['current_margin']*100:.2f}%",
                            help="Historical operating margin"
                        )
                    
                    st.info(f"**Market Expectations:** {method2['analysis']}")
                    
                    # Comparison
                    st.markdown("---")
                    st.markdown("#### 💡 Comparison of Both Methods:")
                    comparison_data = {
                        "Method": ["Method 1 (Growth Only)", "Method 2 (Growth + Margin)"],
                        "Implied Growth": [
                            f"{method1['implied_growth_rate']*100:.2f}%",
                            f"{method2['implied_growth_rate']*100:.2f}%"
                        ],
                        "Implied Margin": [
                            f"{method1['assumptions']['operating_margin']*100:.2f}% (fixed)",
                            f"{method2['implied_operating_margin']*100:.2f}%"
                        ]
                    }
                    st.table(comparison_data)
                    
                    st.markdown('''
                    **Interpretation:**
                    - **Method 1** assumes margin stays constant → All valuation from growth
                    - **Method 2** allows margin expansion/contraction → More flexible
                    
                    **Use Method 2** if you believe margins can change (e.g., economies of scale, pricing power).  
                    **Use Method 1** for mature companies with stable margins.
                    ''')
"""






