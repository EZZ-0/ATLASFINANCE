"""
Data Tab Flip Card Metrics
==========================
Provides flip card metric displays for each sub-tab in the Data tab.

Sub-tabs:
1. Income Statement - Revenue, Gross Profit, Operating Income, Net Income
2. Balance Sheet - Assets, Liabilities, Equity, Current Ratio
3. Cash Flow - Operating CF, Investing CF, FCF
4. Stock Prices - Price, Returns, Volatility
5. Ratios - Valuation and profitability ratios
6. Growth - CAGR metrics
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any, Optional

# Import flip card components with fallback
try:
    from flip_cards import RATIO_DEFINITIONS
    FLIP_CARDS_AVAILABLE = True
except ImportError:
    FLIP_CARDS_AVAILABLE = False
    RATIO_DEFINITIONS = {}
    RATIO_DEFINITIONS = {}


def render_income_metrics(financials: Dict, depth: str = "beginner"):
    """Render key income statement metrics as flip cards"""
    
    if not FLIP_CARDS_AVAILABLE:
        return
    
    income = financials.get('income_statement', pd.DataFrame())
    if income.empty:
        return
    
    st.markdown("#### Key Income Metrics")
    st.caption("Click any metric to see breakdown")
    
    # Extract values from income statement
    def get_income_value(search_terms):
        if isinstance(income.index[0], str):
            for term in search_terms:
                for idx in income.index:
                    if term.lower() in str(idx).lower():
                        val = income.loc[idx].iloc[0] if len(income.columns) > 0 else None
                        if pd.notna(val):
                            return val
        return None
    
    revenue = get_income_value(['Total Revenue', 'Revenue'])
    gross_profit = get_income_value(['Gross Profit'])
    operating_income = get_income_value(['Operating Income', 'Operating Profit'])
    net_income = get_income_value(['Net Income'])
    
    # Calculate margins
    gross_margin = (gross_profit / revenue * 100) if revenue and gross_profit else None
    operating_margin = (operating_income / revenue * 100) if revenue and operating_income else None
    net_margin = (net_income / revenue * 100) if revenue and net_income else None
    
    # Render 4 key metrics
    cols = st.columns(4)
    
    metrics = [
        {"label": "Revenue", "value": revenue, "format": "currency"},
        {"label": "Gross Margin", "value": gross_margin, "format": "pct", "benchmark": (30, 50)},
        {"label": "Operating Margin", "value": operating_margin, "format": "pct", "benchmark": (10, 20)},
        {"label": "Net Margin", "value": net_margin, "format": "pct", "benchmark": (5, 15)},
    ]
    
    for i, m in enumerate(metrics):
        with cols[i]:
            _render_simple_flip(m, depth)
    
    st.markdown("---")


def render_balance_metrics(financials: Dict, depth: str = "beginner"):
    """Render key balance sheet metrics as flip cards"""
    
    if not FLIP_CARDS_AVAILABLE:
        return
    
    balance = financials.get('balance_sheet', pd.DataFrame())
    if balance.empty:
        return
    
    st.markdown("#### Key Balance Sheet Metrics")
    st.caption("Click any metric to see breakdown")
    
    def get_balance_value(search_terms):
        if isinstance(balance.index[0], str):
            for term in search_terms:
                for idx in balance.index:
                    if term.lower() in str(idx).lower():
                        val = balance.loc[idx].iloc[0] if len(balance.columns) > 0 else None
                        if pd.notna(val):
                            return val
        return None
    
    total_assets = get_balance_value(['Total Assets'])
    total_liab = get_balance_value(['Total Liabilities', 'Total Liab'])
    total_equity = get_balance_value(['Stockholders Equity', 'Total Equity', 'Shareholders Equity'])
    current_assets = get_balance_value(['Current Assets', 'Total Current Assets'])
    current_liab = get_balance_value(['Current Liabilities', 'Total Current Liabilities'])
    
    # Calculate ratios
    current_ratio = (current_assets / current_liab) if current_assets and current_liab and current_liab != 0 else None
    debt_to_equity = (total_liab / total_equity) if total_liab and total_equity and total_equity != 0 else None
    
    cols = st.columns(4)
    
    metrics = [
        {"label": "Total Assets", "value": total_assets, "format": "currency"},
        {"label": "Total Equity", "value": total_equity, "format": "currency"},
        {"label": "Current Ratio", "value": current_ratio, "format": "ratio", "benchmark": (1.0, 2.0), "higher_better": True},
        {"label": "Debt/Equity", "value": debt_to_equity, "format": "ratio", "benchmark": (0.5, 1.5), "higher_better": False},
    ]
    
    for i, m in enumerate(metrics):
        with cols[i]:
            _render_simple_flip(m, depth)
    
    st.markdown("---")


def render_cashflow_metrics(financials: Dict, depth: str = "beginner"):
    """Render key cash flow metrics as flip cards"""
    
    if not FLIP_CARDS_AVAILABLE:
        return
    
    cf = financials.get('cash_flow', pd.DataFrame())
    info = financials.get('info', {})
    
    st.markdown("#### Key Cash Flow Metrics")
    st.caption("Click any metric to see breakdown")
    
    def get_cf_value(search_terms):
        if not cf.empty and isinstance(cf.index[0], str):
            for term in search_terms:
                for idx in cf.index:
                    if term.lower() in str(idx).lower():
                        val = cf.loc[idx].iloc[0] if len(cf.columns) > 0 else None
                        if pd.notna(val):
                            return val
        return None
    
    operating_cf = get_cf_value(['Operating Cash Flow', 'Cash From Operating', 'Net Cash Operating'])
    investing_cf = get_cf_value(['Investing Cash Flow', 'Cash From Investing', 'Net Cash Investing'])
    financing_cf = get_cf_value(['Financing Cash Flow', 'Cash From Financing', 'Net Cash Financing'])
    fcf = info.get('freeCashflow') or get_cf_value(['Free Cash Flow'])
    
    cols = st.columns(4)
    
    metrics = [
        {"label": "Operating CF", "value": operating_cf, "format": "currency"},
        {"label": "Investing CF", "value": investing_cf, "format": "currency"},
        {"label": "Financing CF", "value": financing_cf, "format": "currency"},
        {"label": "Free Cash Flow", "value": fcf, "format": "currency"},
    ]
    
    for i, m in enumerate(metrics):
        with cols[i]:
            _render_simple_flip(m, depth)
    
    st.markdown("---")


def render_price_metrics(financials: Dict, depth: str = "beginner"):
    """Render stock price metrics as flip cards"""
    
    if not FLIP_CARDS_AVAILABLE:
        return
    
    market_data = financials.get('market_data', {})
    info = financials.get('info', {})
    
    st.markdown("#### Key Price Metrics")
    st.caption("Click any metric to see breakdown")
    
    current_price = market_data.get('current_price') or info.get('currentPrice')
    week_52_high = info.get('fiftyTwoWeekHigh')
    week_52_low = info.get('fiftyTwoWeekLow')
    beta = info.get('beta')
    
    # Calculate % from 52-week high
    pct_from_high = None
    if current_price and week_52_high:
        pct_from_high = ((current_price - week_52_high) / week_52_high) * 100
    
    cols = st.columns(4)
    
    metrics = [
        {"label": "Current Price", "value": current_price, "format": "price"},
        {"label": "52-Week High", "value": week_52_high, "format": "price"},
        {"label": "% From High", "value": pct_from_high, "format": "pct"},
        {"label": "Beta", "value": beta, "format": "ratio", "benchmark": (0.8, 1.2)},
    ]
    
    for i, m in enumerate(metrics):
        with cols[i]:
            _render_simple_flip(m, depth)
    
    st.markdown("---")


def render_ratio_metrics(financials: Dict, depth: str = "beginner"):
    """Render key ratio metrics as flip cards"""
    
    if not FLIP_CARDS_AVAILABLE:
        return
    
    ratios = financials.get('ratios', pd.DataFrame())
    if ratios.empty:
        return
    
    st.markdown("#### Key Valuation Ratios")
    st.caption("Click any metric to see breakdown")
    
    def get_ratio(key):
        if key in ratios.index:
            val = ratios.loc[key].iloc[0] if len(ratios.columns) > 0 else None
            if pd.notna(val):
                return val
        return None
    
    cols = st.columns(5)
    
    metrics = [
        {"label": "P/E Ratio", "value": get_ratio('PE_Ratio'), "format": "ratio", "benchmark": (15, 25), "higher_better": False},
        {"label": "P/B Ratio", "value": get_ratio('Price_to_Book'), "format": "ratio", "benchmark": (1, 3), "higher_better": False},
        {"label": "P/S Ratio", "value": get_ratio('Price_to_Sales'), "format": "ratio", "benchmark": (1, 5), "higher_better": False},
        {"label": "EV/EBITDA", "value": get_ratio('EV_to_EBITDA'), "format": "ratio", "benchmark": (8, 15), "higher_better": False},
        {"label": "ROE", "value": get_ratio('ROE'), "format": "pct", "benchmark": (10, 20), "higher_better": True},
    ]
    
    for i, m in enumerate(metrics):
        with cols[i]:
            _render_simple_flip(m, depth)
    
    st.markdown("---")


def render_growth_metrics(financials: Dict, depth: str = "beginner"):
    """Render growth metrics as flip cards"""
    
    if not FLIP_CARDS_AVAILABLE:
        return
    
    ratios = financials.get('ratios', pd.DataFrame())
    growth_rates = financials.get('growth_rates', {})
    
    st.markdown("#### Growth Rates (CAGR)")
    st.caption("Click any metric to see breakdown")
    
    def get_growth(keys):
        # Try growth_rates dict first
        if isinstance(growth_rates, dict):
            for key in keys:
                if key in growth_rates and pd.notna(growth_rates[key]):
                    return growth_rates[key]
        # Try ratios DataFrame
        if not ratios.empty:
            for key in keys:
                if key in ratios.index:
                    val = ratios.loc[key].iloc[0]
                    if pd.notna(val):
                        return val
        return None
    
    cols = st.columns(4)
    
    metrics = [
        {"label": "Revenue CAGR", "value": get_growth(['Revenue_CAGR_3Y', 'Total_Revenue_CAGR']), "format": "pct", "benchmark": (5, 15)},
        {"label": "Earnings CAGR", "value": get_growth(['Net_Income_CAGR_3Y', 'Net_Income_CAGR']), "format": "pct", "benchmark": (5, 20)},
        {"label": "Asset CAGR", "value": get_growth(['Total_Assets_CAGR_3Y', 'Total_Assets_CAGR']), "format": "pct", "benchmark": (3, 10)},
        {"label": "EPS CAGR", "value": get_growth(['EPS_CAGR_3Y', 'EPS_CAGR']), "format": "pct", "benchmark": (5, 20)},
    ]
    
    for i, m in enumerate(metrics):
        with cols[i]:
            _render_simple_flip(m, depth)
    
    st.markdown("---")


def _render_simple_flip(config: Dict, depth: str):
    """Render a simple flip card metric"""
    
    label = config["label"]
    value = config["value"]
    fmt = config.get("format", "number")
    benchmark = config.get("benchmark")
    higher_better = config.get("higher_better", True)
    
    # Format value
    if value is None or (isinstance(value, float) and pd.isna(value)):
        formatted = "N/A"
        color = "#6b7280"
    else:
        try:
            num = float(value)
            
            if fmt == "currency":
                if abs(num) >= 1e12:
                    formatted = f"${num/1e12:.2f}T"
                elif abs(num) >= 1e9:
                    formatted = f"${num/1e9:.2f}B"
                elif abs(num) >= 1e6:
                    formatted = f"${num/1e6:.2f}M"
                else:
                    formatted = f"${num:,.0f}"
            elif fmt == "price":
                formatted = f"${num:.2f}"
            elif fmt == "pct":
                formatted = f"{num:.1f}%"
            elif fmt == "ratio":
                formatted = f"{num:.2f}x"
            else:
                formatted = f"{num:.2f}"
            
            # Determine color
            if benchmark:
                low, high = benchmark
                if higher_better:
                    if num >= high:
                        color = "#22c55e"
                    elif num <= low:
                        color = "#ef4444"
                    else:
                        color = "#f59e0b"
                else:
                    if num <= low:
                        color = "#22c55e"
                    elif num >= high:
                        color = "#ef4444"
                    else:
                        color = "#f59e0b"
            else:
                # Default color based on sign for currency
                if fmt == "currency" and num < 0:
                    color = "#ef4444"
                else:
                    color = "#60a5fa"
                    
        except (ValueError, TypeError):
            formatted = str(value) if value else "N/A"
            color = "#6b7280"
    
    # Get explanation from definitions
    key_mapping = {
        "P/E Ratio": "PE_Ratio",
        "P/B Ratio": "PB_Ratio",
        "P/S Ratio": "PS_Ratio",
        "EV/EBITDA": "EV_EBITDA",
        "ROE": "ROE",
        "Current Ratio": "Current_Ratio",
        "Debt/Equity": "Debt_to_Equity",
        "Gross Margin": "Gross_Margin",
        "Operating Margin": "Operating_Margin",
        "Net Margin": "Net_Margin",
        "Beta": "Beta",
    }
    
    def_key = key_mapping.get(label, label.replace(" ", "_"))
    definition = RATIO_DEFINITIONS.get(def_key, {})
    formula = definition.get("formula", "")
    explanation = definition.get("explanations", {}).get(depth, f"Measures {label.lower()}")
    
    # Create unique key
    card_key = f"data_flip_{label.replace(' ', '_').replace('/', '_')}"
    
    if card_key not in st.session_state:
        st.session_state[card_key] = False
    
    is_flipped = st.session_state[card_key]
    
    # Render card
    st.markdown(f"""
    <style>
        .data-flip-{card_key} {{
            perspective: 1000px;
            height: 110px;
            margin-bottom: 8px;
        }}
        .data-card-{card_key} {{
            position: relative;
            width: 100%;
            height: 100%;
            text-align: center;
            transition: transform 0.5s;
            transform-style: preserve-3d;
            cursor: pointer;
            border-radius: 10px;
        }}
        .data-card-{card_key}.flipped {{
            transform: rotateY(180deg);
        }}
        .data-front-{card_key}, .data-back-{card_key} {{
            position: absolute;
            width: 100%;
            height: 100%;
            backface-visibility: hidden;
            border-radius: 10px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            padding: 10px;
            box-shadow: 0 3px 10px rgba(0,0,0,0.25);
        }}
        .data-front-{card_key} {{
            background: linear-gradient(145deg, #1e293b, #0f172a);
            border-left: 3px solid {color};
        }}
        .data-back-{card_key} {{
            background: linear-gradient(145deg, #0f172a, #1e293b);
            border-left: 3px solid {color};
            transform: rotateY(180deg);
            text-align: left;
            font-size: 0.7rem;
            overflow-y: auto;
        }}
    </style>
    <div class="data-flip-{card_key}">
        <div class="data-card-{card_key} {'flipped' if is_flipped else ''}">
            <div class="data-front-{card_key}">
                <div style="color: #94a3b8; font-size: 0.75rem;">{label}</div>
                <div style="color: {color}; font-size: 1.5rem; font-weight: 700;">{formatted}</div>
            </div>
            <div class="data-back-{card_key}">
                <div style="font-weight: 600; color: #e2e8f0; font-size: 0.8rem;">{label}</div>
                <div style="color: #60a5fa; font-family: monospace; font-size: 0.65rem; margin: 3px 0;">{formula if formula else ''}</div>
                <div style="color: #cbd5e1; font-size: 0.65rem; line-height: 1.2;">{explanation[:120]}{'...' if len(explanation) > 120 else ''}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Toggle button
    if st.button("↻", key=f"btn_{card_key}", help="Flip"):
        st.session_state[card_key] = not st.session_state[card_key]
        st.rerun()

