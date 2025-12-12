"""
ATLAS Financial Intelligence - Data Tab
=======================================
Financial data display with sub-tabs for statements, prices, ratios.
Extracted from usa_app.py lines 1691-2220 for modularity.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go

# Import format helpers
from format_helpers import (
    format_dataframe_for_display, 
    format_dataframe_for_csv, 
    prepare_table_for_display,
    format_financial_number
)

# Import excel export
from excel_export import export_financials_to_excel

# Import UI components
from ui_components import smart_dataframe
from enhanced_tables import enhanced_dataframe

# Import flip card metrics for Data tab
try:
    from data_tab_metrics import (
        render_income_metrics, render_balance_metrics, render_cashflow_metrics,
        render_price_metrics, render_ratio_metrics, render_growth_metrics,
        FLIP_CARDS_AVAILABLE as DATA_FLIP_AVAILABLE
    )
except ImportError:
    DATA_FLIP_AVAILABLE = False
    def render_income_metrics(f): pass
    def render_balance_metrics(f): pass
    def render_cashflow_metrics(f): pass
    def render_price_metrics(f): pass
    def render_ratio_metrics(f): pass
    def render_growth_metrics(f): pass


def icon(name, size="1em", color=None):
    """Render a Bootstrap Icon"""
    style = f"font-size: {size};"
    if color:
        style += f" color: {color};"
    return f'<i class="bi bi-{name}" style="{style}"></i>'


@st.fragment
def render_data_tab(ticker: str, financials: dict, extractor):
    """
    Render the Financial Data tab with sub-tabs for different statements.
    
    Uses @st.fragment to prevent full page rerun when Excel export button is clicked,
    keeping user on the Data tab instead of redirecting to Dashboard.
    
    Args:
        ticker: Stock ticker symbol
        financials: Dictionary of financial data
        extractor: USAFinancialExtractor instance for ratio calculations
    """
    st.markdown(f"## {icon('bar-chart-line', '1.5em')} Financial Data: {ticker}", unsafe_allow_html=True)
    
    # Company info
    company_name = financials.get("company_name", ticker)
    extraction_time = financials.get("extraction_time", "N/A")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Company", company_name)
    with col2:
        st.metric("Ticker", ticker)
    with col3:
        st.metric("Extraction Time", extraction_time)
    
    st.markdown("---")
    
    # Export All Data to Excel
    if st.button("Export All to Excel (Professional Format)", type="primary", use_container_width=True, key="data_excel_export"):
        try:
            excel_filename = f"{ticker}_Financial_Report_{datetime.now().strftime('%Y%m%d')}.xlsx"
            export_financials_to_excel(financials, excel_filename)
            
            # Provide download link
            with open(excel_filename, "rb") as f:
                st.download_button(
                    label="Download Excel Report",
                    data=f,
                    file_name=excel_filename,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            st.success(f"Excel report created: {excel_filename}")
        except Exception as e:
            st.error(f"Excel export failed: {str(e)}")
    
    st.markdown("---")
    
    # Sub-tabs for different statements
    sub_tab1, sub_tab2, sub_tab3, sub_tab4, sub_tab5, sub_tab6 = st.tabs([
        "Income Statement",
        "Balance Sheet",
        "Cash Flow",
        "Stock Prices",
        "Ratios",
        "Growth Metrics"
    ])
    
    # ==========================================
    # SUB-TAB 1: INCOME STATEMENT
    # ==========================================
    with sub_tab1:
        st.subheader("Income Statement (Annual)")
        
        # Flip card metrics at top
        if DATA_FLIP_AVAILABLE:
            render_income_metrics(financials)
        
        income = financials.get("income_statement", pd.DataFrame())
        
        if not income.empty:
            enhanced_dataframe(
                income,
                title="Income Statement",
                key="income_stmt",
                show_search=True,
                show_export=True,
                conditional_formatting=True,
                height=400
            )
        else:
            st.warning("No income statement data available")
    
    # ==========================================
    # SUB-TAB 2: BALANCE SHEET
    # ==========================================
    with sub_tab2:
        st.subheader("Balance Sheet (Annual)")
        
        if DATA_FLIP_AVAILABLE:
            render_balance_metrics(financials)
        
        balance = financials.get("balance_sheet", pd.DataFrame())
        
        if not balance.empty:
            enhanced_dataframe(
                balance,
                title="Balance Sheet",
                key="balance_sheet",
                show_search=True,
                show_export=True,
                conditional_formatting=True,
                height=400
            )
        else:
            st.warning("No balance sheet data available")
    
    # ==========================================
    # SUB-TAB 3: CASH FLOW
    # ==========================================
    with sub_tab3:
        st.subheader("Cash Flow Statement (Annual)")
        
        if DATA_FLIP_AVAILABLE:
            render_cashflow_metrics(financials)
        
        cashflow = financials.get("cash_flow", pd.DataFrame())
        
        if not cashflow.empty:
            cf_display, cf_csv = prepare_table_for_display(cashflow, "Cash Flow")
            smart_dataframe(cf_display, title=None, height=400, key="cashflow_table")
            
            csv = cf_csv.to_csv(index=True)
            st.download_button(
                "Download CSV",
                data=csv,
                file_name=f"{ticker}_cash_flow.csv",
                mime="text/csv"
            )
        else:
            st.warning("No cash flow data available")
    
    # ==========================================
    # SUB-TAB 4: STOCK PRICES
    # ==========================================
    with sub_tab4:
        st.subheader("Historical Stock Prices")
        
        if DATA_FLIP_AVAILABLE:
            render_price_metrics(financials)
        
        market_data = financials.get("market_data", {})
        historical_prices = market_data.get("historical_prices", pd.DataFrame())
        
        if not historical_prices.empty:
            _render_price_history(ticker, financials, historical_prices, market_data)
        else:
            st.warning("No historical price data available")
    
    # ==========================================
    # SUB-TAB 5: RATIOS
    # ==========================================
    with sub_tab5:
        st.subheader("Key Financial Ratios")
        
        if DATA_FLIP_AVAILABLE:
            render_ratio_metrics(financials)
        
        ratios = extractor.calculate_ratios(financials)
        
        if ratios and "status" not in ratios:
            all_zero = all(v == 0 for k, v in ratios.items() if isinstance(v, (int, float)))
            if all_zero:
                st.warning("Ratios returned all zeros. This may indicate data quality issues.")
                with st.expander("Show raw ratio data"):
                    st.json(ratios)
            else:
                _render_ratio_display(ratios)
        else:
            st.error("Failed to calculate ratios. Check if financial statements have required fields.")
    
    # ==========================================
    # SUB-TAB 6: GROWTH METRICS
    # ==========================================
    with sub_tab6:
        st.markdown(f"### {icon('graph-up-arrow')} Comprehensive Growth Analysis", unsafe_allow_html=True)
        
        if DATA_FLIP_AVAILABLE:
            render_growth_metrics(financials)
        
        growth = financials.get("growth_rates", {})
        
        if "status" not in growth and growth:
            _render_growth_analysis(ticker, growth)
        else:
            st.error("Growth rates calculation failed or no data available")


def _render_price_history(ticker: str, financials: dict, historical_prices: pd.DataFrame, market_data: dict):
    """Render the stock price history sub-section"""
    # Determine frequency based on IPO date
    ipo_info = ""
    if "quant_analysis" in financials:
        quant = financials["quant_analysis"]
        ipo_date = quant.get("ipo_date", "Unknown")
        freq = quant.get("data_frequency", "Daily")
        ipo_info = f"**IPO Date:** {ipo_date} | **Frequency:** {freq}"
    
    st.info(f"Historical data from January 1, 1990 to present. {ipo_info}")
    
    # Display key metrics
    current_price = market_data.get("current_price", "N/A")
    high_52w = historical_prices['Close'].rolling(252).max().iloc[-1] if len(historical_prices) > 252 else historical_prices['Close'].max()
    low_52w = historical_prices['Close'].rolling(252).min().iloc[-1] if len(historical_prices) > 252 else historical_prices['Close'].min()
    
    # Calculate 1-Year return
    if len(historical_prices) >= 252:
        price_1y_ago = historical_prices['Close'].iloc[-252]
        one_year_return = ((historical_prices['Close'].iloc[-1] / price_1y_ago) - 1) * 100
        price_change_1y = historical_prices['Close'].iloc[-1] - price_1y_ago
    else:
        price_1y_ago = historical_prices['Close'].iloc[0]
        one_year_return = ((historical_prices['Close'].iloc[-1] / price_1y_ago) - 1) * 100
        price_change_1y = historical_prices['Close'].iloc[-1] - price_1y_ago
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if isinstance(current_price, (int, float)) and price_change_1y != 0:
            change_arrow = "+" if price_change_1y > 0 else ""
            st.metric(
                "Current Price", 
                f"${current_price:.2f}",
                delta=f"{change_arrow}${abs(price_change_1y):.2f} ({change_arrow}{one_year_return:.1f}%)"
            )
        else:
            st.metric("Current Price", f"${current_price:.2f}" if isinstance(current_price, (int, float)) else current_price)
    with col2:
        st.metric("52-Week High", f"${high_52w:.2f}")
    with col3:
        st.metric("52-Week Low", f"${low_52w:.2f}")
    with col4:
        st.metric("1Y Return", f"{one_year_return:.1f}%", delta=f"vs 1 year ago", delta_color="off")
    
    st.markdown("---")
    
    # Time Period Selector
    st.markdown("### Select Time Period")
    
    total_days = len(historical_prices)
    years_available = total_days / 252
    ipo_date_val = historical_prices.index[0]
    
    # Determine available periods
    available_periods = []
    period_info = {}
    
    if total_days >= 5:
        available_periods.append("1W")
        period_info["1W"] = {"days": 5, "freq": "Daily"}
    
    if total_days >= 21:
        available_periods.append("1M")
        period_info["1M"] = {"days": 21, "freq": "Daily"}
    
    if total_days >= 252:
        available_periods.append("1Y")
        period_info["1Y"] = {"days": 252, "freq": "Daily"}
    
    if years_available >= 10:
        available_periods.append("10Y")
        period_info["10Y"] = {"days": 252 * 10, "freq": "Monthly"}
    
    available_periods.append("MAX (Since IPO)")
    period_info["MAX (Since IPO)"] = {"days": total_days, "freq": "Monthly" if years_available > 5 else "Daily"}
    
    col_select, col_freq, col_info = st.columns([1, 1, 2])
    
    with col_select:
        selected_period = st.selectbox(
            "Display Period",
            options=available_periods,
            index=2 if "1Y" in available_periods else 0,
            key="price_period_select"
        )
    
    with col_freq:
        if selected_period == "1W":
            freq_options = ["Daily"]
        elif selected_period == "1M":
            freq_options = ["Daily", "Weekly"]
        elif selected_period in ["1Y", "10Y"]:
            freq_options = ["Daily", "Weekly", "Monthly"]
        else:
            freq_options = ["Monthly", "Weekly"] if years_available > 5 else ["Daily", "Weekly"]
        
        selected_frequency = st.selectbox(
            "Data Frequency",
            options=freq_options,
            index=0,
            key="price_freq_select"
        )
    
    with col_info:
        st.info(f"Showing **{selected_period}** data | Frequency: **{selected_frequency}** | IPO: {ipo_date_val.strftime('%Y-%m-%d')}")
    
    # Filter data based on selection
    if selected_period == "1W":
        chart_data = historical_prices.tail(5)
        table_data = historical_prices.tail(5)
    elif selected_period == "1M":
        chart_data = historical_prices.tail(21)
        table_data = historical_prices.tail(21)
    elif selected_period == "1Y":
        chart_data = historical_prices.tail(252)
        table_data = historical_prices.tail(252)
    elif selected_period == "10Y":
        chart_data = historical_prices.tail(252 * 10)
        table_data = chart_data
    else:
        chart_data = historical_prices
        table_data = historical_prices
    
    # Apply frequency resampling
    if selected_frequency == "Weekly":
        chart_data = chart_data.resample('W').last()
        table_data = table_data.resample('W').last()
    elif selected_frequency == "Monthly":
        chart_data = chart_data.resample('M').last()
        table_data = table_data.resample('M').last()
    
    # Price chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=chart_data.index,
        y=chart_data['Close'],
        mode='lines',
        name='Close Price',
        line=dict(color='#1f77b4', width=2)
    ))
    fig.update_layout(
        title=f"{ticker} Stock Price History ({selected_period})",
        xaxis_title="Date",
        yaxis_title="Price (USD)",
        hovermode='x unified',
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Data table
    st.markdown(f"### Recent Price Data ({selected_frequency})")
    display_prices = table_data.copy()
    display_prices.index = display_prices.index.strftime('%Y-%m-%d')
    
    for col in ['Open', 'High', 'Low', 'Close']:
        if col in display_prices.columns:
            display_prices[col] = display_prices[col].apply(lambda x: f"${x:.2f}")
    if 'Volume' in display_prices.columns:
        display_prices['Volume'] = display_prices['Volume'].apply(lambda x: f"{x:,.0f}")
    
    smart_dataframe(display_prices.iloc[::-1], title=None, height=400, key="price_history_table")
    
    # Download button
    csv = historical_prices.to_csv()
    st.download_button(
        "Download Full Price History CSV",
        data=csv,
        file_name=f"{ticker}_price_history.csv",
        mime="text/csv"
    )


def _render_ratio_display(ratios: dict):
    """Render the financial ratios display"""
    comp = ratios.get("_components", {})
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Gross Margin", 
            f"{ratios.get('Gross_Margin', 0) * 100:.1f}%",
            help=f"Gross Profit {format_financial_number(comp.get('gross_profit', 0))} / Revenue {format_financial_number(comp.get('revenue', 0))}"
        )
        st.metric(
            "Operating Margin", 
            f"{ratios.get('Operating_Margin', 0) * 100:.1f}%",
            help=f"Operating Income {format_financial_number(comp.get('operating_income', 0))} / Revenue {format_financial_number(comp.get('revenue', 0))}"
        )
    
    with col2:
        st.metric(
            "Net Margin", 
            f"{ratios.get('Net_Margin', 0) * 100:.1f}%",
            help=f"Net Income {format_financial_number(comp.get('net_income', 0))} / Revenue {format_financial_number(comp.get('revenue', 0))}"
        )
        st.metric(
            "ROE", 
            f"{ratios.get('ROE', 0) * 100:.1f}%",
            help=f"Net Income {format_financial_number(comp.get('net_income', 0))} / Total Equity {format_financial_number(comp.get('total_equity', 0))}"
        )
    
    with col3:
        st.metric(
            "ROA", 
            f"{ratios.get('ROA', 0) * 100:.1f}%",
            help=f"Net Income {format_financial_number(comp.get('net_income', 0))} / Total Assets {format_financial_number(comp.get('total_assets', 0))}"
        )
        st.metric(
            "Debt/Equity", 
            f"{ratios.get('Debt_to_Equity', 0):.2f}",
            help=f"Total Debt {format_financial_number(comp.get('total_debt', 0))} / Total Equity {format_financial_number(comp.get('total_equity', 0))}"
        )
    
    with col4:
        fcf = ratios.get('Free_Cash_Flow', 0)
        fcf_display = format_financial_number(fcf) if fcf != 0 else "$0"
        st.metric(
            "Free Cash Flow", 
            fcf_display,
            help=f"Operating Cash Flow {format_financial_number(comp.get('op_cash_flow', 0))} - CapEx {format_financial_number(abs(comp.get('capex', 0)))}"
        )


def _render_growth_analysis(ticker: str, growth: dict):
    """Render the growth analysis sub-section"""
    is_quarterly = any("QoQ" in k or "YoY" in k for k in growth.keys())
    
    if is_quarterly:
        st.info("**Quarterly Data Detected** - Showing QoQ, YoY, and CAGR metrics")
    else:
        st.info("**Annual Data** - Showing CAGR, Dollar Change, and Percent Change")
    
    metric_groups = {
        "Total_Revenue": "Total Revenue",
        "COGS": "Cost of Goods Sold (COGS)",
        "Gross_Profit": "Gross Profit",
        "SGA_Expenses": "SG&A Expenses",
        "Total_Operating_Expenses": "Total Operating Expenses",
        "Operating_Profit": "Operating Profit",
        "NOPAT": "Net Operating Profit After Tax (NOPAT)",
        "Net_Income": "Net Income"
    }
    
    growth_data = []
    
    for metric_key, metric_label in metric_groups.items():
        row = {"Metric": metric_label}
        
        # CAGR
        cagr_key = f"{metric_key}_CAGR"
        row["CAGR (%)"] = f"{growth[cagr_key]:.2f}%" if cagr_key in growth else "N/A"
        
        # Latest Value
        latest_key = f"{metric_key}_Latest_Value"
        row["Latest Value"] = format_financial_number(growth[latest_key]) if latest_key in growth else "N/A"
        
        # Dollar Change
        dollar_key = f"{metric_key}_Dollar_Change"
        row["$ Change"] = format_financial_number(growth[dollar_key]) if dollar_key in growth else "N/A"
        
        # Percent Change
        pct_key = f"{metric_key}_Pct_Change"
        row["% Change"] = f"{growth[pct_key]:.2f}%" if pct_key in growth else "N/A"
        
        # Quarterly metrics
        if is_quarterly:
            qoq_key = f"{metric_key}_QoQ"
            row["QoQ (%)"] = f"{growth[qoq_key]:.2f}%" if qoq_key in growth else "N/A"
            
            yoy_key = f"{metric_key}_YoY"
            row["YoY (%)"] = f"{growth[yoy_key]:.2f}%" if yoy_key in growth else "N/A"
        
        if any(v != "N/A" for k, v in row.items() if k != "Metric"):
            growth_data.append(row)
    
    if growth_data:
        growth_df = pd.DataFrame(growth_data)
        smart_dataframe(growth_df, title=None, height=400, key="growth_metrics_table")
        
        csv = growth_df.to_csv(index=False)
        st.download_button(
            "Download Growth Metrics CSV",
            data=csv,
            file_name=f"{ticker}_growth_metrics.csv",
            mime="text/csv"
        )
        
        # Visual breakdown
        st.markdown("---")
        st.markdown(f"### {icon('bar-chart-line', '1.2em')} Visual Breakdown", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"**{icon('rocket-takeoff', '1em')} Top Growers (CAGR)**", unsafe_allow_html=True)
            cagr_items = [(metric_groups.get(k.replace("_CAGR", ""), k), v) 
                         for k, v in growth.items() if "_CAGR" in k and isinstance(v, (int, float))]
            cagr_items.sort(key=lambda x: x[1], reverse=True)
            for label, value in cagr_items[:5]:
                icon_html = icon('arrow-up', '1em', 'green') if value > 0 else icon('arrow-down', '1em', 'red')
                st.markdown(f"{icon_html} {label}: **{value:.1f}%**", unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"**{icon('cash-coin', '1em')} Largest $ Changes**", unsafe_allow_html=True)
            dollar_items = [(metric_groups.get(k.replace("_Dollar_Change", ""), k), v) 
                           for k, v in growth.items() if "_Dollar_Change" in k and isinstance(v, (int, float))]
            dollar_items.sort(key=lambda x: abs(x[1]), reverse=True)
            for label, value in dollar_items[:5]:
                icon_html = icon('arrow-up', '1em', 'green') if value > 0 else icon('arrow-down', '1em', 'red')
                st.markdown(f"{icon_html} {label}: **{format_financial_number(value)}**", unsafe_allow_html=True)
        
        with col3:
            if is_quarterly:
                st.markdown(f"**{icon('graph-up-arrow', '1em')} YoY Performance**", unsafe_allow_html=True)
                yoy_items = [(metric_groups.get(k.replace("_YoY", ""), k), v) 
                            for k, v in growth.items() if "_YoY" in k and isinstance(v, (int, float))]
                yoy_items.sort(key=lambda x: x[1], reverse=True)
                for label, value in yoy_items[:5]:
                    icon_html = icon('arrow-up', '1em', 'green') if value > 0 else icon('arrow-down', '1em', 'red')
                    st.markdown(f"{icon_html} {label}: **{value:.1f}%**", unsafe_allow_html=True)
            else:
                st.markdown(f"**{icon('bar-chart-line', '1em')} % Change Leaders**", unsafe_allow_html=True)
                pct_items = [(metric_groups.get(k.replace("_Pct_Change", ""), k), v) 
                            for k, v in growth.items() if "_Pct_Change" in k and isinstance(v, (int, float))]
                pct_items.sort(key=lambda x: x[1], reverse=True)
                for label, value in pct_items[:5]:
                    icon_html = icon('arrow-up', '1em', 'green') if value > 0 else icon('arrow-down', '1em', 'red')
                    st.markdown(f"{icon_html} {label}: **{value:.1f}%**", unsafe_allow_html=True)
    else:
        st.warning("No growth metrics available for the selected statement")

