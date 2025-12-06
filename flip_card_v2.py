"""
FLIP CARD V2.3 - Proper Streamlit Layout
========================================
Each card rendered in its own Streamlit column.
Same size as st.metric() boxes.
"""

import streamlit as st
import streamlit.components.v1 as components
from typing import Dict, Any, List
import pandas as pd
import hashlib

# ============================================================================
# METRIC CONFIGURATIONS
# ============================================================================

METRIC_CONFIG = {
    "PE_Ratio": {
        "name": "P/E Ratio",
        "formula_template": "{price} ÷ {eps}",
        "components": ["price", "eps"],
        "insight": "Investor sentiment per $1 earnings",
        "benchmark": (15, 25),
        "higher_is_better": False,
        "unit": "x"
    },
    "ROE": {
        "name": "ROE",
        "formula_template": "{net_income} ÷ {equity}",
        "components": ["net_income", "equity"],
        "insight": "Profit per shareholder dollar",
        "benchmark": (10, 20),
        "higher_is_better": True,
        "unit": "%"
    },
    "Debt_to_Equity": {
        "name": "D/E Ratio",
        "formula_template": "{total_debt} ÷ {equity}",
        "components": ["total_debt", "equity"],
        "insight": "Leverage risk. <1 is conservative",
        "benchmark": (0.5, 1.5),
        "higher_is_better": False,
        "unit": "x"
    },
    "Gross_Margin": {
        "name": "Gross Margin",
        "formula_template": "({revenue} - {cogs}) ÷ {revenue}",
        "components": ["revenue", "cogs"],
        "insight": "Pricing power. >40% is strong",
        "benchmark": (30, 50),
        "higher_is_better": True,
        "unit": "%"
    },
    "FCF_Yield": {
        "name": "FCF Yield",
        "formula_template": "{fcf} ÷ {market_cap}",
        "components": ["fcf", "market_cap"],
        "insight": "Cash generation vs price",
        "benchmark": (3, 8),
        "higher_is_better": True,
        "unit": "%"
    },
    "Dividend_Yield": {
        "name": "Div Yield",
        "formula_template": "{annual_div} ÷ {price}",
        "components": ["annual_div", "price"],
        "insight": "Income return. >4% high yield",
        "benchmark": (2, 5),
        "higher_is_better": True,
        "unit": "%"
    },
    "Beta": {
        "name": "Beta",
        "formula_template": "Cov(Stock,Mkt) ÷ Var(Mkt)",
        "components": [],
        "insight": "Volatility vs market",
        "benchmark": (0.8, 1.2),
        "higher_is_better": None,
        "unit": ""
    },
    "EPS": {
        "name": "EPS",
        "formula_template": "{net_income} ÷ {shares}",
        "components": ["net_income", "shares"],
        "insight": "Earnings per share",
        "benchmark": None,
        "higher_is_better": True,
        "unit": "$"
    },
    "current_price": {
        "name": "Price",
        "formula_template": "Market Price",
        "components": [],
        "insight": "Compare to intrinsic value",
        "benchmark": None,
        "higher_is_better": None,
        "unit": "$"
    },
    "market_cap": {
        "name": "Market Cap",
        "formula_template": "{price} × {shares}",
        "components": ["price", "shares"],
        "insight": "Company size. >$10B = large cap",
        "benchmark": None,
        "higher_is_better": None,
        "unit": "$"
    }
}


def fmt_short(val: Any) -> str:
    """Format number short for equations."""
    if val is None:
        return "N/A"
    try:
        num = float(val)
        if pd.isna(num):
            return "N/A"
        if abs(num) >= 1e12:
            return f"${num/1e12:.1f}T"
        elif abs(num) >= 1e9:
            return f"${num/1e9:.1f}B"
        elif abs(num) >= 1e6:
            return f"${num/1e6:.0f}M"
        elif abs(num) >= 1000:
            return f"${num/1000:.0f}K"
        else:
            return f"${num:.2f}"
    except:
        return "N/A"


def get_color(value: float, metric_key: str) -> str:
    """Get color based on benchmark."""
    if value is None:
        return "#6b7280"
    
    config = METRIC_CONFIG.get(metric_key, {})
    benchmark = config.get("benchmark")
    higher_is_better = config.get("higher_is_better")
    
    if benchmark is None or higher_is_better is None:
        return "#60a5fa"
    
    low, high = benchmark
    
    if higher_is_better:
        if value >= high:
            return "#10b981"
        elif value <= low:
            return "#ef4444"
        else:
            return "#f59e0b"
    else:
        if value <= low:
            return "#10b981"
        elif value >= high:
            return "#ef4444"
        else:
            return "#f59e0b"


def format_display(value: Any, unit: str, metric_key: str) -> tuple:
    """Format value and return (formatted_string, numeric_for_color)."""
    if value is None:
        return "N/A", None
    
    try:
        num = float(value)
        if pd.isna(num):
            return "N/A", None
    except:
        return "N/A", None
    
    # Handle conversions
    display_num = num
    if unit == "%" and metric_key in ["ROE", "Gross_Margin", "FCF_Yield", "Dividend_Yield"]:
        if abs(num) < 1:
            display_num = num * 100
    
    if metric_key == "Debt_to_Equity" and num > 10:
        display_num = num / 100
    
    # Format string
    if unit == "$":
        if abs(display_num) >= 1e12:
            formatted = f"${display_num/1e12:.2f}T"
        elif abs(display_num) >= 1e9:
            formatted = f"${display_num/1e9:.2f}B"
        elif abs(display_num) >= 1e6:
            formatted = f"${display_num/1e6:.2f}M"
        else:
            formatted = f"${display_num:.2f}"
    elif unit == "%":
        formatted = f"{display_num:.2f}%"
    elif unit == "x":
        formatted = f"{display_num:.2f}x"
    else:
        formatted = f"{display_num:.2f}"
    
    return formatted, display_num


def build_equation(metric_key: str, comp: Dict) -> str:
    """Build equation with real numbers."""
    config = METRIC_CONFIG.get(metric_key, {})
    template = config.get("formula_template", "")
    
    if not template:
        return ""
    
    result = template
    for c in config.get("components", []):
        val = comp.get(c)
        result = result.replace("{" + c + "}", fmt_short(val))
    
    return result


def render_single_flip_card(
    metric_key: str,
    value: Any,
    label: str,
    comp: Dict,
    card_id: str
) -> None:
    """Render one flip card using st.components.v1.html in current column."""
    
    config = METRIC_CONFIG.get(metric_key, {})
    unit = config.get("unit", "")
    insight = config.get("insight", "")
    benchmark = config.get("benchmark")
    
    formatted, num_val = format_display(value, unit, metric_key)
    color = get_color(num_val, metric_key)
    equation = build_equation(metric_key, comp)
    
    bench_text = ""
    if benchmark:
        low, high = benchmark
        bench_text = f"{low}-{high}{unit}"
    
    # HTML for single card - fits in st.column
    html = f"""
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        .flip-wrap {{
            perspective: 1000px;
            width: 100%;
            height: 100px;
            cursor: pointer;
        }}
        .flip-inner {{
            position: relative;
            width: 100%;
            height: 100%;
            transition: transform 0.5s ease;
            transform-style: preserve-3d;
        }}
        .flip-wrap:hover .flip-inner {{
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
            border-radius: 8px;
        }}
        .flip-wrap.flipped .flip-inner {{
            transform: rotateY(180deg);
        }}
        .flip-front, .flip-back {{
            position: absolute;
            width: 100%;
            height: 100%;
            backface-visibility: hidden;
            -webkit-backface-visibility: hidden;
            border-radius: 8px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            padding: 12px;
            background: linear-gradient(180deg, #262c36 0%, #1a1f27 100%);
            border: 1px solid #363d47;
        }}
        .flip-back {{
            transform: rotateY(180deg);
        }}
        .label {{
            color: #8b949e;
            font-size: 0.75rem;
            font-weight: 500;
            margin-bottom: 6px;
        }}
        .value {{
            color: {color};
            font-size: 1.5rem;
            font-weight: 700;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }}
        .equation {{
            color: #58a6ff;
            font-size: 0.7rem;
            font-family: 'SF Mono', 'Consolas', monospace;
            margin-bottom: 6px;
            word-break: break-all;
        }}
        .insight {{
            color: #c9d1d9;
            font-size: 0.7rem;
            line-height: 1.3;
        }}
        .bench {{
            color: #6e7681;
            font-size: 0.6rem;
            margin-top: 4px;
        }}
    </style>
    <div class="flip-wrap" onclick="this.classList.toggle('flipped')">
        <div class="flip-inner">
            <div class="flip-front">
                <div class="label">{label}</div>
                <div class="value">{formatted}</div>
            </div>
            <div class="flip-back">
                <div class="equation">{equation}</div>
                <div class="insight">{insight}</div>
                <div class="bench">{bench_text}</div>
            </div>
        </div>
    </div>
    """
    
    components.html(html, height=110)


def render_dashboard_flip_cards(financials: Dict) -> None:
    """Render dashboard flip cards using Streamlit columns."""
    
    info = financials.get('info', {})
    market_data = financials.get('market_data', {})
    ratios_df = financials.get('ratios', pd.DataFrame())
    
    def get_val(keys, default=None):
        sources = [info, market_data, financials]
        for src in sources:
            if not isinstance(src, dict):
                continue
            for k in (keys if isinstance(keys, list) else [keys]):
                if k in src and src[k] is not None:
                    v = src[k]
                    if not (isinstance(v, float) and pd.isna(v)):
                        return v
        
        if isinstance(ratios_df, pd.DataFrame) and not ratios_df.empty:
            for k in (keys if isinstance(keys, list) else [keys]):
                if k in ratios_df.index:
                    v = ratios_df.loc[k].iloc[0]
                    if pd.notna(v):
                        return v
        return default
    
    # Extract components for equations
    price = get_val(['currentPrice', 'current_price'])
    eps = get_val(['trailingEps', 'eps'])
    net_income = get_val(['netIncome', 'net_income'])
    revenue = get_val(['totalRevenue', 'revenue'])
    gross_profit = get_val(['grossProfit', 'gross_profit'])
    cogs = (revenue - gross_profit) if revenue and gross_profit else None
    total_debt = get_val(['totalDebt', 'total_debt'])
    equity = get_val(['totalStockholderEquity', 'stockholdersEquity', 'total_equity'])
    shares = get_val(['sharesOutstanding', 'shares_outstanding'])
    market_cap = get_val(['marketCap', 'market_cap'])
    fcf = get_val(['freeCashflow', 'free_cash_flow'])
    annual_div = get_val(['dividendRate', 'annual_dividend'])
    
    comp = {
        "price": price, "eps": eps, "net_income": net_income, "revenue": revenue,
        "cogs": cogs, "total_debt": total_debt, "equity": equity, "shares": shares,
        "market_cap": market_cap, "fcf": fcf, "annual_div": annual_div
    }
    
    # Get metric values
    pe_ratio = get_val(['trailingPE', 'PE_Ratio', 'pe_ratio'])
    roe = get_val(['ROE', 'roe', 'returnOnEquity'])
    de_ratio = get_val(['Debt_to_Equity', 'debt_to_equity', 'debtToEquity'])
    gross_margin = get_val(['Gross_Margin', 'gross_margin', 'grossMargins'])
    fcf_yield = (fcf / market_cap * 100) if fcf and market_cap and market_cap > 0 else None
    div_yield = get_val(['dividendYield'])
    if div_yield and div_yield < 1:
        div_yield = div_yield * 100
    beta = get_val(['beta'])
    
    st.markdown("### Key Metrics")
    st.caption("Click any card to see equation & insight")
    
    # Row 1 - 5 columns (same as st.metric layout)
    c1, c2, c3, c4, c5 = st.columns(5)
    
    with c1:
        render_single_flip_card("PE_Ratio", pe_ratio, "P/E Ratio", comp, "pe")
    with c2:
        render_single_flip_card("current_price", price, "Price", comp, "price")
    with c3:
        render_single_flip_card("ROE", roe, "ROE", comp, "roe")
    with c4:
        render_single_flip_card("Debt_to_Equity", de_ratio, "D/E Ratio", comp, "de")
    with c5:
        render_single_flip_card("Gross_Margin", gross_margin, "Gross Margin", comp, "gm")
    
    # Row 2 - 5 columns
    c6, c7, c8, c9, c10 = st.columns(5)
    
    with c6:
        render_single_flip_card("EPS", eps, "EPS", comp, "eps")
    with c7:
        render_single_flip_card("market_cap", market_cap, "Market Cap", comp, "mc")
    with c8:
        render_single_flip_card("FCF_Yield", fcf_yield, "FCF Yield", comp, "fcf")
    with c9:
        render_single_flip_card("Beta", beta, "Beta", comp, "beta")
    with c10:
        render_single_flip_card("Dividend_Yield", div_yield, "Div Yield", comp, "div")


# Exports
METRIC_INSIGHTS = METRIC_CONFIG
__all__ = ['render_dashboard_flip_cards', 'METRIC_INSIGHTS', 'METRIC_CONFIG']
