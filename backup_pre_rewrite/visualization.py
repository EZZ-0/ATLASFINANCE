"""
INTERACTIVE VISUALIZATION MODULE
=================================
Plotly-based charts and dashboards for financial analysis.

Features:
- Revenue/Profit trends
- Margin waterfall charts
- DCF scenario comparisons
- Sensitivity heatmaps
- Multi-company comparisons
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, List, Optional

class FinancialVisualizer:
    """
    Create interactive financial visualizations using Plotly.
    """
    
    def __init__(self, theme: str = "plotly_dark"):
        """
        Initialize visualizer.
        
        Args:
            theme: Plotly template ("plotly_dark", "plotly_white", "seaborn", etc.)
        """
        self.theme = theme
        self.colors = {
            "revenue": "#1f77b4",
            "profit": "#2ca02c",
            "expense": "#d62728",
            "cash": "#9467bd",
            "conservative": "#ff7f0e",
            "base": "#2ca02c",
            "aggressive": "#1f77b4"
        }
    
    # ==========================================
    # 1. INCOME STATEMENT VISUALIZATIONS
    # ==========================================
    
    def plot_revenue_trend(self, financials: Dict) -> go.Figure:
        """
        Plot multi-year revenue trend with growth rates.
        Handles both SEC and yfinance data formats.
        """
        income = financials.get("income_statement", pd.DataFrame())
        
        if income.empty:
            return self._empty_chart("No Income Data Available")
        
        try:
            # Check if data is from yfinance (rows are metrics)
            if "Total Revenue" in income.index or any('revenue' in str(idx).lower() for idx in income.index):
                # yfinance format: find revenue row
                revenue_row = None
                for idx in income.index:
                    if 'revenue' in str(idx).lower() or 'sales' in str(idx).lower():
                        revenue_row = idx
                        break
                
                if revenue_row is None:
                    return self._empty_chart("No Revenue Data Found")
                
                # Extract revenue series and transpose
                df = pd.DataFrame({"Revenue": income.loc[revenue_row]})
            else:
                # SEC format
                if "Revenue" not in income.columns:
                    return self._empty_chart("No Revenue Column Found")
                df = income[["Revenue"]].copy()
            
            df = df.iloc[::-1]  # Oldest to newest
            
            # Calculate YoY growth
            df["Growth_%"] = df["Revenue"].pct_change() * 100
            
        except Exception as e:
            return self._empty_chart(f"Data format error: {str(e)}")
        
        # Create figure with secondary y-axis
        fig = make_subplots(
            rows=1, cols=1,
            specs=[[{"secondary_y": True}]]
        )
        
        # Revenue bars
        fig.add_trace(
            go.Bar(
                x=df.index,
                y=df["Revenue"],
                name="Revenue",
                marker_color=self.colors["revenue"],
                text=[f"${v/1e9:.2f}B" if v > 1e9 else f"${v/1e6:.0f}M" for v in df["Revenue"]],
                textposition="outside"
            ),
            secondary_y=False
        )
        
        # Growth rate line
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df["Growth_%"],
                name="YoY Growth",
                mode="lines+markers",
                line=dict(color=self.colors["profit"], width=3),
                marker=dict(size=10),
                yaxis="y2"
            ),
            secondary_y=True
        )
        
        # Update layout
        fig.update_layout(
            title=f"Revenue Trend | {financials.get('ticker', '')}",
            template=self.theme,
            hovermode="x unified",
            height=500
        )
        
        fig.update_yaxes(title_text="Revenue (USD)", secondary_y=False)
        fig.update_yaxes(title_text="Growth Rate (%)", secondary_y=True)
        
        return fig
    
    def plot_margin_analysis(self, financials: Dict) -> go.Figure:
        """
        Waterfall chart showing margin breakdown.
        Handles both SEC and yfinance data formats.
        """
        income = financials.get("income_statement", pd.DataFrame())
        
        if income.empty:
            return self._empty_chart("No Income Statement Data")
        
        try:
            # Check if data is from yfinance (rows are metrics)
            if len(income.index) > 0 and (isinstance(income.index[0], str) or 
                                           any('revenue' in str(idx).lower() for idx in income.index[:5])):
                # yfinance format: rows are metrics, columns are dates
                # Get the most recent column (first column after transpose)
                latest_col = income.columns[0]
                
                # Extract metrics with flexible matching
                def find_metric(keywords):
                    for idx in income.index:
                        idx_lower = str(idx).lower()
                        if any(kw.lower() in idx_lower for kw in keywords):
                            return income.loc[idx, latest_col] if idx in income.index else 0
                    return 0
                
                revenue = find_metric(['Total Revenue', 'Revenue', 'Sales'])
                cogs = -find_metric(['Cost of Revenue', 'Cost Of Goods Sold', 'COGS'])
                gross_profit = find_metric(['Gross Profit'])
                operating_income = find_metric(['Operating Income', 'Operating Profit', 'EBIT'])
                tax = -find_metric(['Tax Provision', 'Income Tax', 'Tax Expense'])
                net_income = find_metric(['Net Income'])
                
                # Calculate opex if not directly available
                if gross_profit and operating_income:
                    opex = -(gross_profit - operating_income)
                else:
                    opex = 0
                    
            else:
                # SEC format: columns are metrics, rows are dates
                latest = income.iloc[0]
                
                revenue = latest.get("Revenue", 0)
                cogs = -latest.get("Cost_of_Revenue", 0)
                gross_profit = latest.get("Gross_Profit", revenue + cogs)
                opex = -(gross_profit - latest.get("Operating_Income", 0))
                operating_income = latest.get("Operating_Income", 0)
                tax = -latest.get("Tax_Expense", 0)
                net_income = latest.get("Net_Income", 0)
        
        except Exception as e:
            return self._empty_chart(f"Data format error: {str(e)}")
        
        # Create waterfall
        fig = go.Figure(go.Waterfall(
            name="Income Statement",
            orientation="v",
            measure=["absolute", "relative", "total", "relative", "total", "relative", "total"],
            x=["Revenue", "COGS", "Gross Profit", "OpEx", "Operating Income", "Tax", "Net Income"],
            y=[revenue, cogs, 0, opex, 0, tax, 0],
            text=[f"${v/1e9:.2f}B" if abs(v) > 1e9 else f"${v/1e6:.0f}M" for v in [revenue, cogs, gross_profit, opex, operating_income, tax, net_income]],
            textposition="outside",
            connector={"line": {"color": "rgb(63, 63, 63)"}},
            decreasing={"marker": {"color": self.colors["expense"]}},
            increasing={"marker": {"color": self.colors["profit"]}},
            totals={"marker": {"color": self.colors["cash"]}}
        ))
        
        fig.update_layout(
            title=f"Margin Waterfall | {financials.get('ticker', '')} - Latest Year",
            template=self.theme,
            height=500,
            showlegend=False
        )
        
        return fig
    
    def plot_profitability_trends(self, financials: Dict) -> go.Figure:
        """
        Multi-line chart showing Revenue, Operating Income, and Net Income trends.
        Handles both SEC (columns as metrics) and yfinance (rows as metrics) formats.
        """
        income = financials.get("income_statement", pd.DataFrame())
        
        if income.empty:
            return self._empty_chart("No Income Data")
        
        # Check if data is from yfinance (rows are metrics, columns are dates)
        # or SEC (columns are metrics, index are dates)
        try:
            # More robust format detection: check if index contains strings (metrics) or Timestamps (dates)
            is_yfinance_format = False
            
            if len(income.index) > 0:
                first_idx = income.index[0]
                # If index is string type (metric names), it's yfinance format
                if isinstance(first_idx, str):
                    is_yfinance_format = True
                # Also check if common metric names are in index
                elif any(metric in income.index for metric in ["Total Revenue", "Net Income", "Operating Income"]):
                    is_yfinance_format = True
            
            if is_yfinance_format:
                # yfinance format: rows are metrics, columns are dates
                # We need to extract specific metrics and create a proper DataFrame
                
                # Find the metric rows we need
                revenue_vals = None
                op_income_vals = None
                net_income_vals = None
                
                for idx in income.index:
                    idx_lower = str(idx).lower()
                    if revenue_vals is None and ('total revenue' in idx_lower or ('revenue' in idx_lower and 'total' in idx_lower)):
                        revenue_vals = income.loc[idx]
                    elif op_income_vals is None and ('operating income' in idx_lower or 'ebit' in idx_lower):
                        op_income_vals = income.loc[idx]
                    elif net_income_vals is None and ('net income' in idx_lower and 'common' not in idx_lower):
                        net_income_vals = income.loc[idx]
                
                # Build DataFrame with unique columns
                data_dict = {}
                if revenue_vals is not None:
                    data_dict['Revenue'] = revenue_vals
                if op_income_vals is not None:
                    data_dict['Operating_Income'] = op_income_vals
                if net_income_vals is not None:
                    data_dict['Net_Income'] = net_income_vals
                
                if not data_dict:
                    return self._empty_chart("Required metrics not found in data")
                
                df = pd.DataFrame(data_dict)
            else:
                # SEC format or already correct
                df = income.copy()
                
                # Select only the metrics we want (if they exist)
                available_metrics = []
                for metric in ["Revenue", "Operating_Income", "Net_Income"]:
                    if metric in df.columns:
                        available_metrics.append(metric)
                
                if not available_metrics:
                    return self._empty_chart("Required metrics not found in data")
                
                df = df[available_metrics]
            
            df = df.iloc[::-1]  # Chronological order (oldest to newest)
            available_metrics = df.columns.tolist()
            
        except Exception as e:
            return self._empty_chart(f"Data format error: {str(e)}")
        
        # Create figure
        fig = go.Figure()
        
        metric_colors = {
            "Revenue": self.colors["revenue"],
            "Operating_Income": self.colors["cash"],
            "Net_Income": self.colors["profit"]
        }
        
        for metric in available_metrics:
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df[metric],
                name=metric.replace("_", " "),
                mode="lines+markers",
                line=dict(width=3, color=metric_colors[metric]),
                marker=dict(size=8)
            ))
        
        fig.update_layout(
            title=f"Profitability Trends | {financials.get('ticker', '')}",
            template=self.theme,
            hovermode="x unified",
            yaxis_title="USD",
            height=500
        )
        
        return fig
    
    # ==========================================
    # 2. DCF VISUALIZATION
    # ==========================================
    
    def plot_dcf_comparison(self, dcf_results: Dict) -> go.Figure:
        """
        Bar chart comparing valuations across 3 scenarios.
        """
        scenarios = ["conservative", "base", "aggressive"]
        values = [dcf_results[s]["value_per_share"] for s in scenarios]
        colors_list = [self.colors[s] for s in scenarios]
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=[s.capitalize() for s in scenarios],
            y=values,
            text=[f"${v:.2f}" for v in values],
            textposition="outside",
            marker_color=colors_list,
            showlegend=False
        ))
        
        # Add weighted average line
        weighted = dcf_results.get("weighted_average", 0)
        fig.add_hline(
            y=weighted,
            line_dash="dash",
            line_color="yellow",
            annotation_text=f"Weighted Avg: ${weighted:.2f}",
            annotation_position="right"
        )
        
        fig.update_layout(
            title="DCF Valuation Comparison (Per Share)",
            template=self.theme,
            yaxis_title="Value per Share (USD)",
            height=500
        )
        
        return fig
    
    def plot_dcf_breakdown(self, dcf_result: Dict, scenario: str = "base") -> go.Figure:
        """
        Pie chart showing Enterprise Value breakdown (PV Cash Flows vs Terminal Value).
        """
        pv_cf = dcf_result["pv_cash_flows"]
        pv_tv = dcf_result["pv_terminal_value"]
        
        fig = go.Figure(data=[go.Pie(
            labels=["PV of Cash Flows", "PV of Terminal Value"],
            values=[pv_cf, pv_tv],
            hole=0.4,
            marker_colors=[self.colors["base"], self.colors["conservative"]],
            textinfo="label+percent",
            textfont_size=14
        )])
        
        fig.update_layout(
            title=f"Enterprise Value Breakdown | {scenario.capitalize()} Scenario",
            template=self.theme,
            height=400,
            annotations=[dict(
                text=f"EV:<br>${dcf_result['enterprise_value']/1e9:.2f}B",
                x=0.5, y=0.5,
                font_size=16,
                showarrow=False
            )]
        )
        
        return fig
    
    def plot_dcf_projections(self, dcf_result: Dict, scenario: str = "base") -> go.Figure:
        """
        Bar chart showing projected Free Cash Flows over forecast period.
        """
        projections = dcf_result["projections"]
        
        fig = go.Figure()
        
        # FCF bars
        fig.add_trace(go.Bar(
            x=projections["Year"],
            y=projections["Free_Cash_Flow"],
            name="Free Cash Flow",
            marker_color=self.colors["profit"],
            text=[f"${v/1e9:.2f}B" if v > 1e9 else f"${v/1e6:.0f}M" for v in projections["Free_Cash_Flow"]],
            textposition="outside"
        ))
        
        # Revenue line (secondary axis)
        fig.add_trace(go.Scatter(
            x=projections["Year"],
            y=projections["Revenue"],
            name="Revenue",
            mode="lines+markers",
            line=dict(color=self.colors["revenue"], width=3),
            marker=dict(size=10),
            yaxis="y2"
        ))
        
        # Create secondary y-axis
        fig.update_layout(
            title=f"Cash Flow Projections | {scenario.capitalize()} Scenario",
            template=self.theme,
            yaxis=dict(title="Free Cash Flow (USD)"),
            yaxis2=dict(title="Revenue (USD)", overlaying="y", side="right"),
            hovermode="x unified",
            height=500
        )
        
        return fig
    
    def plot_sensitivity_heatmap(self, sensitivity_df: pd.DataFrame, ticker: str = "") -> go.Figure:
        """
        Heatmap for DCF sensitivity analysis (WACC vs Terminal Growth).
        """
        fig = go.Figure(data=go.Heatmap(
            z=sensitivity_df.values,
            x=sensitivity_df.columns,
            y=sensitivity_df.index,
            colorscale="RdYlGn",
            text=sensitivity_df.values,
            texttemplate="$%{text:.2f}",
            textfont={"size": 10},
            colorbar=dict(title="Value/Share")
        ))
        
        fig.update_layout(
            title=f"DCF Sensitivity Analysis | {ticker}",
            xaxis_title="Terminal Growth Rate",
            yaxis_title="Discount Rate (WACC)",
            template=self.theme,
            height=500
        )
        
        return fig
    
    # ==========================================
    # 3. BALANCE SHEET & CASH FLOW
    # ==========================================
    
    def plot_balance_sheet_structure(self, financials: Dict) -> go.Figure:
        """
        Stacked bar chart showing Assets vs Liabilities + Equity.
        Handles both SEC and yfinance data formats.
        """
        balance = financials.get("balance_sheet", pd.DataFrame())
        
        if balance.empty:
            return self._empty_chart("No Balance Sheet Data")
        
        try:
            # Check if data is from yfinance (rows are metrics)
            if len(balance.index) > 0 and isinstance(balance.index[0], str):
                # yfinance format
                latest_col = balance.columns[0]
                
                def find_metric(keywords):
                    for idx in balance.index:
                        idx_lower = str(idx).lower()
                        if any(kw.lower() in idx_lower for kw in keywords):
                            return balance.loc[idx, latest_col] if idx in balance.index else 0
                    return 0
                
                total_assets = find_metric(['Total Assets'])
                current_assets = find_metric(['Current Assets', 'Total Current Assets'])
                total_liabilities = find_metric(['Total Liabilities'])
                total_equity = find_metric(['Total Stockholder Equity', 'Total Equity', 'Stockholders Equity'])
                
            else:
                # SEC format
                latest = balance.iloc[0]
                total_assets = latest.get("Total_Assets", 0)
                current_assets = latest.get("Current_Assets", 0)
                total_liabilities = latest.get("Total_Liabilities", 0)
                total_equity = latest.get("Total_Equity", 0)
            
            non_current_assets = total_assets - current_assets
            
        except Exception as e:
            return self._empty_chart(f"Data format error: {str(e)}")
        
        fig = go.Figure()
        
        # Assets bar
        fig.add_trace(go.Bar(
            name="Current Assets",
            x=["Assets"],
            y=[current_assets],
            marker_color="#66c2a5"
        ))
        fig.add_trace(go.Bar(
            name="Non-Current Assets",
            x=["Assets"],
            y=[non_current_assets],
            marker_color="#fc8d62"
        ))
        
        # Liabilities + Equity bars
        fig.add_trace(go.Bar(
            name="Liabilities",
            x=["Liabilities + Equity"],
            y=[total_liabilities],
            marker_color="#e78ac3"
        ))
        fig.add_trace(go.Bar(
            name="Equity",
            x=["Liabilities + Equity"],
            y=[total_equity],
            marker_color="#8da0cb"
        ))
        
        fig.update_layout(
            title=f"Balance Sheet Structure | {financials.get('ticker', '')}",
            barmode="stack",
            template=self.theme,
            yaxis_title="USD",
            height=500
        )
        
        return fig
    
    def plot_cash_flow_trends(self, financials: Dict) -> go.Figure:
        """
        Line chart showing Operating, Investing, and Financing cash flows.
        Handles both SEC and yfinance data formats.
        """
        cashflow = financials.get("cash_flow", pd.DataFrame())
        
        if cashflow.empty:
            return self._empty_chart("No Cash Flow Data")
        
        try:
            # Check if data is from yfinance (rows are metrics)
            if len(cashflow.index) > 0 and isinstance(cashflow.index[0], str):
                # yfinance format: rows are metrics, columns are dates
                # Look for the three main cash flow categories
                
                operating_cf = None
                investing_cf = None
                financing_cf = None
                
                for idx in cashflow.index:
                    idx_lower = str(idx).lower()
                    if operating_cf is None and any(term in idx_lower for term in ['operating cash flow', 'cash from operating', 'operating activities']):
                        operating_cf = idx
                    elif investing_cf is None and any(term in idx_lower for term in ['investing cash flow', 'cash from investing', 'investing activities']):
                        investing_cf = idx
                    elif financing_cf is None and any(term in idx_lower for term in ['financing cash flow', 'cash from financing', 'financing activities']):
                        financing_cf = idx
                
                # If we found the rows, extract them and create DataFrame
                data = {}
                if operating_cf:
                    data['Operating'] = cashflow.loc[operating_cf]
                if investing_cf:
                    data['Investing'] = cashflow.loc[investing_cf]
                if financing_cf:
                    data['Financing'] = cashflow.loc[financing_cf]
                
                if not data:
                    return self._empty_chart("No standard cash flow categories found")
                
                df = pd.DataFrame(data)
                
            else:
                # SEC format: dates as index, metrics as columns
                df = cashflow.copy()
                
                # Map SEC column names
                column_mapping = {}
                for col in df.columns:
                    col_lower = str(col).lower()
                    if 'operating' in col_lower:
                        column_mapping[col] = 'Operating'
                    elif 'investing' in col_lower:
                        column_mapping[col] = 'Investing'
                    elif 'financing' in col_lower:
                        column_mapping[col] = 'Financing'
                
                df = df.rename(columns=column_mapping)
            
            df = df.iloc[::-1]  # Chronological (oldest to newest)
            
            fig = go.Figure()
            
            cf_types = [
                ("Operating", "Operating", self.colors["profit"]),
                ("Investing", "Investing", self.colors["expense"]),
                ("Financing", "Financing", self.colors["cash"])
            ]
            
            for col, label, color in cf_types:
                if col in df.columns:
                    fig.add_trace(go.Scatter(
                        x=df.index,
                        y=df[col],
                        name=label,
                        mode="lines+markers",
                        line=dict(width=3, color=color),
                        marker=dict(size=8)
                    ))
                    
        except Exception as e:
            return self._empty_chart(f"Data format error: {str(e)}")
        
        # Add zero line
        fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
        
        fig.update_layout(
            title=f"Cash Flow Trends | {financials.get('ticker', '')}",
            template=self.theme,
            yaxis_title="Cash Flow (USD)",
            hovermode="x unified",
            height=500
        )
        
        return fig
    
    # ==========================================
    # 4. MULTI-COMPANY COMPARISONS
    # ==========================================
    
    def plot_peer_comparison(self, companies_data: List[Dict], metric: str = "Revenue") -> go.Figure:
        """
        Grouped bar chart comparing a metric across multiple companies.
        
        Args:
            companies_data: List of financial dictionaries from usa_backend
            metric: Which metric to compare (Revenue, Net_Income, etc.)
        """
        data = []
        
        for company in companies_data:
            ticker = company.get("ticker", "Unknown")
            income = company.get("income_statement", pd.DataFrame())
            
            if not income.empty and metric in income.columns:
                latest_value = income[metric].iloc[0]
                data.append({"Company": ticker, "Value": latest_value})
        
        if not data:
            return self._empty_chart(f"No {metric} Data for Comparison")
        
        df = pd.DataFrame(data)
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=df["Company"],
            y=df["Value"],
            marker_color=self.colors["revenue"],
            text=[f"${v/1e9:.1f}B" if v > 1e9 else f"${v/1e6:.0f}M" for v in df["Value"]],
            textposition="outside"
        ))
        
        fig.update_layout(
            title=f"Peer Comparison: {metric}",
            template=self.theme,
            yaxis_title=f"{metric} (USD)",
            height=500
        )
        
        return fig
    
    def plot_valuation_comparison(self, comparison_df: pd.DataFrame) -> go.Figure:
        """
        Grouped bar chart showing DCF valuations for multiple companies.
        
        Args:
            comparison_df: Output from dcf_modeling.compare_valuations()
        """
        fig = go.Figure()
        
        scenarios = ["Conservative", "Base", "Aggressive"]
        colors_list = [self.colors["conservative"], self.colors["base"], self.colors["aggressive"]]
        
        for scenario, color in zip(scenarios, colors_list):
            if scenario in comparison_df.columns:
                fig.add_trace(go.Bar(
                    name=scenario,
                    x=comparison_df["Ticker"],
                    y=comparison_df[scenario],
                    marker_color=color
                ))
        
        fig.update_layout(
            title="Multi-Company DCF Valuation Comparison",
            template=self.theme,
            yaxis_title="Value per Share (USD)",
            barmode="group",
            height=500
        )
        
        return fig
    
    # ==========================================
    # 5. UTILITIES
    # ==========================================
    
    def _empty_chart(self, message: str) -> go.Figure:
        """Return empty chart with error message"""
        fig = go.Figure()
        fig.add_annotation(
            text=message,
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=20, color="gray")
        )
        fig.update_layout(
            template=self.theme,
            height=400,
            xaxis=dict(visible=False),
            yaxis=dict(visible=False)
        )
        return fig
    
    def create_dashboard(self, financials: Dict, dcf_results: Optional[Dict] = None) -> List[go.Figure]:
        """
        Generate complete set of charts for a company.
        
        Returns:
            List of Plotly figures ready for display
        """
        charts = []
        
        # Financial Statement Charts
        charts.append(self.plot_revenue_trend(financials))
        charts.append(self.plot_margin_analysis(financials))
        charts.append(self.plot_profitability_trends(financials))
        charts.append(self.plot_balance_sheet_structure(financials))
        charts.append(self.plot_cash_flow_trends(financials))
        
        # DCF Charts (if provided)
        if dcf_results:
            charts.append(self.plot_dcf_comparison(dcf_results))
            charts.append(self.plot_dcf_breakdown(dcf_results["base"]))
            charts.append(self.plot_dcf_projections(dcf_results["base"]))
        
        return charts


# === CONVENIENCE FUNCTIONS ===

def quick_viz(ticker: str, financials: Optional[Dict] = None) -> FinancialVisualizer:
    """
    Quick access to visualizer for a ticker.
    
    Usage:
        viz = quick_viz("AAPL")
        fig = viz.plot_revenue_trend(financials)
        fig.show()
    """
    if financials is None:
        from usa_backend import quick_extract
        financials = quick_extract(ticker)
    
    return FinancialVisualizer()

